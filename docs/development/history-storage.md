# S3 PostgreSQL history foundation

This repository now backs **account-owned record management HTTP**, with optional
GitHub login mapping verified numeric identity through the same repository.
Upload/analysis/question routes and history pages are not connected yet.
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

Migrations 001–002 are additive and idempotent, serialized using a transaction advisory
lock. They create accounts/preparations, an owner index and preparation_tasks.
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
model call. The task repository below handles duplicate attempts and explicit
restart interruption; business HTTP binding and late-job account session revocation
remain required before wiring it to analysis routes. Record management
already maps HTTP errors and uses the live account identity dependency.

## Account record HTTP

Enable explicit GitHub configuration in the [login manual](github-auth.md).
Startup attaches one HistoryStore; no automatic migration or anonymous import
occurs. Disabled operation needs no database driver.

| Method | Path | Contract |
| --- | --- | --- |
| GET | `/api/records` | Own metadata: id, title, revision, timestamps |
| POST | `/api/records` | `{ "title": "Python backend" }`, returns 201 detail |
| GET | `/api/records/{uuid}` | Own parsed text/result snapshot and metadata |
| PATCH | `/api/records/{uuid}` | Same title body; preserves revision/text/results |
| DELETE | `/api/records/{uuid}` | Deletes owned row; 204 with no body |

Titles must be strings, trimmed to 1–100 characters. Extra body fields (including
owner/inputs/results/revision) and malformed UUIDs are rejected (422). Ownership
always comes from the live HttpOnly account cookie. Writes require exact `Origin`
matching `AUTH_FRONTEND_ORIGIN` without a trailing slash, including local clients.
Missing/expired accounts return 401 (disabled configuration returns 503).
Missing and foreign records share 404. Capacity is 409 with no automatic eviction.
Storage failures return safe 503s without SQL/DSN details. All application API
responses have `Cache-Control: no-store`, including errors. Writes are never
automatically retried: a lost response could follow a committed mutation, so
refresh the list before deciding to repeat it.

Selection reads a record URL; no global current-record field. This slice has no
input/result write endpoint: anonymous uploads, reports and questions remain in
memory. No history UI or HTTP task coordination is claimed.

## Durable task repository (not yet wired to business HTTP)

Migration 002 stores at most the latest analysis and questions attempt per record.
`claim_task(owner, record, revision, kind)` locks the owned preparation row, checks
its revision, rejects any running task on that record, then assigns a fresh UUID
attempt. Other records remain independent. The transaction ends before model work.
An explicit retry replaces the previous finished/failed/interrupted attempt; opening
another connection never interrupts work or starts a model.

`finish_task` requires the matching running attempt, owner and input revision. A
complete analysis snapshot has jd/resume/gap keys; a questions snapshot has only
questions. Completion and JSON publication commit together or both roll back.
Analysis regeneration removes prior questions and their task state, because even
unchanged input can produce a different report. Domain Pydantic validation remains
the coordinator's responsibility; the repository checks snapshot keys, not model
semantics. `fail_task` changes only the matching running attempt to failed, without
storing provider error text. Input replacement interrupts running work and clears
results in the same transaction; deletion cascades task rows.

`interrupt_tasks_on_startup()` is an explicit **exclusive single-worker startup**
operation: stop the previous worker first, call before accepting traffic, then
allow users to retry. It changes running to interrupted and invokes no model.
Do not call from a request, a connection constructor or a parallel worker. Application
startup wiring is pending; restart recovery is not active in the current website.
No queue, lease, automatic retry or multi-worker support is introduced.

Future business HTTP MUST revalidate the original account session before publishing
or failing a task; DB ownership/attempt checks do not prove a session is still valid.
The old `publish` method remains for existing repository callers/tests only and has
no attempt guard; new task-backed HTTP must use `finish_task`, never that shortcut.

## Real database acceptance and recovery

The separate `History PostgreSQL and backup restore` CI job uses PostgreSQL 16,
a disposable database and synthetic data. It runs only
`tests/test_history_postgres.py`; it never imports application model configuration.
Every test creates a unique `history_test_<uuid>` schema and drops only that schema.
It covers ownership, actual concurrent connections at the capacity boundary,
independent repository objects, stale writes/deletion, record separation, names
and idempotent migration/001 upgrade. Task cases exercise concurrent claims,
cross-kind exclusion, exact-attempt fencing, failure/retry, explicit restart,
input replacement/deletion, ownership, analysis invalidation and atomic rollback.
A composed HTTP case exercises real routes against
PostgreSQL (synthetic issued cookies): create, stored snapshot reads, metadata,
rename, foreign-account rejection and deletion verified via another repository.
This does not run real OAuth. The recovery case dumps an owned schema using pg_dump,
drops that synthetic schema, restores with pg_restore and checks identity, text
and report/task content, then explicitly interrupts restored running tasks. Missing database/tools is a failure, never a fake pass.

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
