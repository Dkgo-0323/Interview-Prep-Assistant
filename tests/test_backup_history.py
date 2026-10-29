"""Offline failure-boundary checks; actual tool/restore coverage lives in PG CI."""
import json
from pathlib import Path
import subprocess
import pytest
from scripts import backup_history as module


@pytest.fixture
def tools(monkeypatch):
    import sys
    from types import ModuleType
    conninfo = ModuleType('psycopg.conninfo')
    conninfo.conninfo_to_dict = lambda dsn: {'dbname': 'synthetic', 'password': dsn}
    monkeypatch.setitem(sys.modules, 'psycopg.conninfo', conninfo)
    calls = []
    def run(args, **kwargs):
        calls.append((args, kwargs))
        if '--file' in args:
            Path(args[args.index('--file') + 1]).write_bytes(b'synthetic archive')
    monkeypatch.setattr(subprocess, 'run', run)
    return calls


def test_bundle_and_secret_boundary(tmp_path, tools):
    target = tmp_path/'bundle'
    receipt = module.backup(target, 'secret-dsn')
    assert (target/'READY').exists()
    assert receipt == module.verify(target)
    assert 'secret-dsn' not in json.dumps(receipt)
    assert all('secret-dsn' not in str(args) for args, _ in tools)
    assert tools[0][1]['env']['PGSERVICE'] == 'history_backup'
    assert not Path(tools[0][1]['env']['PGSERVICEFILE']).exists()
    assert tools[0][1]['timeout'] == 1800
    with pytest.raises(ValueError):
        module.backup(target, 'secret-dsn')


@pytest.mark.parametrize('failure', ['dump', 'list'])
def test_failure_never_publishes(tmp_path, monkeypatch, tools, failure):
    def run(args, **kwargs):
        if '--file' in args:
            Path(args[args.index('--file') + 1]).write_bytes(b'partial')
        if ('--file' in args) == (failure == 'dump'):
            raise subprocess.CalledProcessError(1, args, stderr=b'secret-dsn')
    monkeypatch.setattr(subprocess, 'run', run)
    with pytest.raises(RuntimeError, match='no backup was published') as error:
        module.backup(tmp_path/'bundle', 'secret-dsn')
    assert 'secret-dsn' not in str(error.value)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize('change', ['truncate', 'same-size', 'receipt'])
def test_corruption_rejected_before_tool(tmp_path, tools, change):
    target = tmp_path/'bundle'
    module.backup(target, 'synthetic')
    calls = len(tools)
    if change == 'receipt':
        (target/'receipt.json').write_text('{}')
    else:
        (target/'history.dump').write_bytes(b'x' if change == 'truncate' else b'x'*17)
    with pytest.raises((ValueError, KeyError)):
        module.verify(target)
    assert len(tools) == calls
