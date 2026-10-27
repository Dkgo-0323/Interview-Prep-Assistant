# S3 PostgreSQL history foundation

This repository now backs **account-owned record management HTTP**, with optional
GitHub login mapping verified numeric identity through the same repository.
Separate account-record upload/analysis/question APIs are now connected to this
repository. History/login pages are not connected yet; the current website
continues to use anonymous process memory. HTTP/storage recovery evidence is
distinct from complete cross-device browser login or public deployment.

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
restart interruption. The record coordinator now captures the original account
session and revalidates it before result/failure transitions. Record management
and business HTTP map safe errors and use the live account identity dependency.

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

Selection reads a record URL; no global current-record field. The default website
still uses anonymous routes; no history UI or anonymous import is introduced.

## Account preparation workflow HTTP

All paths below are relative to `/api/records/{uuid}`. Identity comes only from
the account cookie; writes require the exact configured Origin. No endpoint
accepts an owner, result snapshot or token in its body/query.

| Method/path | Input and behavior |
| --- | --- |
| POST `/upload/jd` or `/upload/resume` | Multipart `file`, query `revision=N`; same PDF/DOCX/TXT/10MB parser and tempfile cleanup as anonymous uploads; returns record detail with incremented revision |
| DELETE `/inputs` | JSON `{ "revision": N }`; clears text/results, increments revision, interrupts running work |
| POST `/analysis/stream` | Strict JSON `{ "revision": N }`; explicit generation, SSE jd/resume/gap stages; publishes complete snapshot atomically |
| GET `/analysis/result` | Last successfully stored GapAnalysis, or 404; no generation |
| POST `/questions/generate` | Strict JSON `{ "revision": N, "num_questions": 10 }`; 10–50 questions, requires stored jd/resume/gap |
| GET `/questions/cached` | Stored question response, or 404; no generation |
| GET `/tasks` | Latest kind/revision/attempt/status/time per record; no inputs, owner or provider errors |

Each successful upload returns the next revision; use that value for the next
upload/generation. Concurrent devices using the same old revision cannot merge or
silently overwrite: a stale request gets 409 and must refresh the record. Upload
captures existing inputs before parsing, then rechecks the original login and
updates against the expected revision. Only parsed text is retained, no filename
or original file. Replacing inputs clears all derived results in one transaction.

Analysis uses **POST**, so native EventSource cannot initiate it; the future UI
must read the POST fetch response stream and close on complete/error. Read/status
GETs never start a model. Identity/Origin/body/record preflight errors use HTTP
401/403/422/404/503; after SSE starts, failures (including busy/stale 409 or missing
inputs 400) are terminal `error` events with `data.status`, not HTTP status changes.
Do not automatically reconnect or retry the POST. Question errors use normal HTTP.
These routes introduce no automatic job retry; existing LLMService provider-level
retries remain unchanged. Normal deployment still uses the configured real
provider: synthetic model behavior exists only in acceptance tests at present.

The coordinator holds no DB transaction during provider work, checks task/session
validity between stages, and revalidates Pydantic domain values before publishing.
A short auth lock spans original-cookie revalidation and result/failure DB writes,
serializing those transitions with logout. A revoked/expired login cannot publish
or mark a task failed; trusted lifecycle cleanup may only mark its captured exact
attempt interrupted. It cannot change newer attempts or write results. Disconnect
cancels publication, not a running synchronous thread: the running slot remains
until that thread actually exits, then exact-attempt interruption releases it.
If storage is unavailable during cleanup, no retry occurs; exclusive startup is
the recovery boundary. Reupload/delete can invalidate old work while it runs;
any later callback cannot restore its snapshot or interrupt a newer attempt.

While reanalysis runs or fails without changing inputs, read APIs retain the last
successful snapshot. Clients must read task status and label it as previous output;
it is not proof the latest attempt succeeded. Successful reanalysis clears previous
questions. Missing results return 404; malformed stored result models return a safe
503 without generating or exposing the stored body.

## Durable task repository and exclusive startup

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
Do not call from a request, a connection constructor or a parallel worker. Enabled
account startup now calls this before accepting traffic; missing migration/storage
fails startup. Stop the old worker first; do not run overlapping workers or rolling
restarts. Account cookies are still process-local and require login after restart;
saved records/results survive separately. The anonymous website still loses its data.
No queue, lease, automatic retry or multi-worker support is introduced.

Business HTTP revalidates the original account session before publishing
or failing a task; DB ownership/attempt checks alone do not prove session validity.
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
Record-business cases additionally exercise actual upload parsing, domain analyzers,
SSE/report/questions across two HTTP clients and another repository connection,
reanalysis invalidation, logout/reupload/deletion during provider return, and exact
interruption cleanup. Provider responses and identity issuance remain synthetic.
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
