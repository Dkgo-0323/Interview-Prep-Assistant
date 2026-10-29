"""Explicit PostgreSQL backup, without dotenv or credentials in command arguments.

The destination must be new. A bundle is published only after pg_restore can
read its archive and its SHA256 receipt is written. No restore/delete/scheduler.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def run_tool(args, env):
    # Tool errors may contain connection details. Never print captured stderr.
    try:
        subprocess.run(args, env=env, check=True, capture_output=True, timeout=1800)
    except (OSError, subprocess.SubprocessError):
        raise RuntimeError('PostgreSQL tool failed; no backup was published') from None


def verify(bundle, pg_restore='pg_restore'):
    archive = bundle / 'history.dump'
    receipt = json.loads((bundle / 'receipt.json').read_text(encoding='utf-8'))
    if receipt['format'] != 1 or archive.stat().st_size != receipt['bytes'] or digest(archive) != receipt['sha256']:
        raise ValueError('Backup receipt mismatch')
    run_tool([pg_restore, '--list', str(archive)], os.environ.copy())
    return receipt


def backup(destination, dsn, pg_dump='pg_dump', pg_restore='pg_restore', schema=None):
    destination = Path(destination).absolute()
    if destination.exists():
        raise ValueError('Destination already exists; choose a new bundle directory')
    # Parent must already be provisioned on a protected backup volume.
    staging = Path(tempfile.mkdtemp(prefix='.history-backup-', dir=destination.parent))
    try:
        archive = staging / 'history.dump'
        env = os.environ.copy()
        env['PGDATABASE'] = dsn
        args = [pg_dump, '--format=custom', '--no-password', '--file', str(archive)]
        if schema:
            args.extend(['--schema', schema])
        run_tool(args, env)
        archive.chmod(0o600)
        receipt = dict(format=1, created_at=datetime.now(timezone.utc).isoformat(),
                       bytes=archive.stat().st_size, sha256=digest(archive))
        (staging / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
        verify(staging, pg_restore)
        # Rename on the same filesystem; reject an existing destination again.
        # os.rename on POSIX may replace an EMPTY directory, so reserve the name
        # using mkdir, then move files and publish READY only as the final step.
        destination.mkdir(mode=0o700)
        for name in ('history.dump', 'receipt.json'):
            shutil.move(str(staging / name), str(destination / name))
        (destination / 'READY').touch(mode=0o600)
        return receipt
    finally:
        shutil.rmtree(staging)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['create', 'verify'])
    parser.add_argument('bundle', type=Path)
    parser.add_argument('--pg-dump', default='pg_dump')
    parser.add_argument('--pg-restore', default='pg_restore')
    args = parser.parse_args()
    try:
        if args.action == 'create':
            dsn = os.environ.get('HISTORY_DATABASE_URL')
            if not dsn:
                raise ValueError('HISTORY_DATABASE_URL is required; dotenv is never loaded')
            backup(args.bundle, dsn, args.pg_dump, args.pg_restore)
        else:
            if not (args.bundle / 'READY').is_file():
                raise ValueError('Backup is incomplete: READY is missing')
            verify(args.bundle, args.pg_restore)
    except (ValueError, KeyError, OSError, RuntimeError):
        parser.exit(1, 'Backup failed validation or export; no credentials are printed.\n')
    print('Backup bundle verified; restore rehearsal and off-host copy remain separate checks.')


if __name__ == '__main__':
    main()
