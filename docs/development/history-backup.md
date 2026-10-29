# History backup bundles

This is an explicit operator tool, not an installed production backup service.
It never reads dotenv, provisions resources, schedules jobs or restores/deletes
databases. Use PostgreSQL 16 client tools with the currently selected PG16 server.

## Export and check

Provision a private backup parent directory outside the checkout (Linux mode 0700,
or equivalent Windows ACL). Supply HISTORY_DATABASE_URL through the process
environment or secret manager; do not paste credentials into commands or logs.
Use a least-privilege database role that can read all application tables. Then:

```sh
python scripts/backup_history.py create /protected-backups/history-20261029T060000Z
python scripts/backup_history.py verify /protected-backups/history-20261029T060000Z
```

Both commands exit nonzero on failure and suppress PostgreSQL error text that
could contain connection details. `--pg-dump` and `--pg-restore` select explicit
client binary paths. The create command refuses an existing destination. It dumps
the complete selected database (not roles), checks `pg_restore --list`, and writes
a receipt containing UTC time, byte count and SHA256, without the connection URL.
Staging directories are private and cleaned on handled errors. No model is called.

Only directories containing READY are complete. A failure while moving files or
an abrupt process/host crash may leave an incomplete directory: do not reuse it
or restore from it. Investigate and choose a new name. `verify` requires READY,
compares the archive to its receipt and checks its table of contents. The receipt
detects accidental corruption, not malicious replacement of both files; it is
not a signature, encryption, SQL restore proof or a freshness/service guarantee.

## Off-host copy and restore rehearsal

The archive contains parsed resumes, reports and account identifiers: treat the
entire bundle as private user data. Copy a completed bundle and its receipt to
an independently protected, encrypted destination, then run verify on that copy.
Do not put bundles in Git, public artifacts or web directories. Same-server
copies alone cannot survive server loss. No destination, credentials, scheduler,
retention period, recovery objective or paid service is configured by this change.
Agree actual operational settings before publication; monitor failures and space,
and never delete the last known-good off-host backup to make room for a new one.

For a rehearsal, provision a separate EMPTY disposable PG16 database and matching
role. Verify the copied bundle first, set PGDATABASE/PGUSER/PGHOST/PGPORT and a
protected password file for that disposable target, then run:

```sh
pg_restore --no-password --exit-on-error --single-transaction /protected-copy/history-20261029T060000Z/history.dump
```

Do not use `--clean`, target the live database, or overwrite an existing database.
This is a data archive: provision server roles/grants separately; failure to match
roles is an error to investigate. Verify account IDs, record titles, inputs,
reports, questions and task attempts with the repository against the restored DB.
Keep the old worker stopped before starting the sole replacement worker: startup
marks restored running tasks interrupted, without model retry. Log in again;
process-local account sessions are not backed up. Do not send test traffic to a
real provider. No production restoration or rollback is performed by this tool.

## Evidence

The reviewed offline suite checks no credential command arguments/receipt,
non-overwrite, dump/list failures and cleanup, and receipt/archive corruption.
The real PostgreSQL CI recovery case now uses this export tool, then actually
restores its synthetic schema and reads account, input, report and running task
back before startup interruption. Its schema filter is internal test isolation;
the operator CLI deliberately exposes no schema filter. CI does not prove an
off-host transfer, production permissions, a scheduler, or recovery duration.
