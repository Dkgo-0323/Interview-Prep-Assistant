# S3 PostgreSQL history foundation

This is an implemented repository, **not yet connected to record HTTP or pages; optional GitHub login now maps verified numeric identity through this repository**.
The current anonymous application continues to use process memory. Do not claim
cross-device login, server restart recovery or public deployment is delivered.

## Setup and migration

Install `python -m pip install -r requirements-history.txt` in the backend environment.
Provision PostgreSQL 16 with a dedicated database and runtime role. Supply
`HISTORY_DATABASE_URL` through the process environment/secret manager; do not place
credentials in commands, tracked files or logs. Then run:

```text
python scripts/migrate_history.py
```

Migration 001 is additive and idempotent, serialized using a transaction advisory
lock. It creates accounts/preparations and an owner index in the selected schema.
The caller must explicitly choose the database; there is no default production
DSN, automatic application-start migration or dotenv loading. Future changes need
new migration versions, not destructive edits to migration 001. For deployment,
use a migration role and a runtime role without schema administration permissions.

## Storage contract

`HistoryStore.account_for_github` accepts the numeric identity obtained from an
**authenticated GitHub user lookup**, not a login name or client-supplied ID. It
is a persistence method, not authentication. No public route accepts a caller-supplied GitHub ID. The optional [GitHub callback](github-auth.md) invokes it only after the authenticated provider user lookup.

Each preparation belongs to one account and has a title, input revision, parsed
JD/resume text and JSON results. Titles contain 1–100 trimmed characters. Accounts
can own 20 records; create locks the account row before counting, so concurrent
connections cannot both take the final slot. Lists return metadata only. Foreign
and missing records deliberately share an error outcome. UUIDs are identifiers,
not access control. No original uploaded binary is stored by this module.

Input replacement uses expected revision and clears all derived results. Model
work must capture record ID/owner/revision and publish only against those values.
Deleting a row or replacing its inputs prevents late writes. Calls use short
transactions and close connections; never retain a database transaction during a
model call. This foundation does not yet handle same-revision duplicate tasks,
restart-interrupted task state, HTTP error mapping or account session revocation;
these remain required before wiring it to analysis routes.

## Real database acceptance and recovery

The separate `History PostgreSQL and backup restore` CI job uses PostgreSQL 16,
a disposable database and synthetic data. It runs only
`tests/test_history_postgres.py`; it never imports application model configuration.
Every test creates a unique `history_test_<uuid>` schema and drops only that schema.
It covers ownership, actual concurrent connections at the capacity boundary,
independent repository objects, stale writes/deletion, record separation, names
and idempotent migration. The recovery case dumps an owned schema using pg_dump,
drops that synthetic schema, restores with pg_restore and checks identity, text
and report content. Missing database/tools is a failure, never a fake pass.

For an already provisioned disposable local PostgreSQL, supply `HISTORY_TEST_DSN`
with a loopback host and run `python -m pytest tests/test_history_postgres.py -q`.
Install pytest separately if this environment does not have it. This entry does
not belong to the default offline suite, which needs neither PostgreSQL nor its
driver. pg_dump/pg_restore 16 are required; CI selects the explicit versioned path.

A CI dump/restore is not a production backup system. Before publication we still
need a backup schedule, off-host protected destination, retention, disk monitoring,
and a documented restore exercise on the chosen host. Same-disk backups alone do
not protect against loss of the server. No recovery time or loss guarantee exists
yet. Revert this additive foundation by leaving it disconnected; never drop real
user records to roll back application code.
