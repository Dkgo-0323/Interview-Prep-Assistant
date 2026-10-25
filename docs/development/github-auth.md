# GitHub account boundary — partial S3 delivery

Opt-in backend OAuth authorization-code flow with S256 PKCE, browser-bound
one-use state and opaque HttpOnly account cookies. No login UI or account-bound
upload/analysis/questions yet; the anonymous application remains active.

## Configuration

Install normal backend plus `requirements-history.txt`; explicitly provision and
migrate PostgreSQL using the [storage manual](history-storage.md). Supply only
through the backend process environment/secret manager, never frontend variables:

| Setting | Meaning |
| --- | --- |
| `GITHUB_AUTH_ENABLED=true` | Explicit opt-in; default false |
| `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET` | Registered OAuth app credentials |
| `GITHUB_CALLBACK_URL` | Fixed URL ending `/api/auth/github/callback` |
| `AUTH_FRONTEND_ORIGIN` | Exact frontend origin; no path/query/fragment |
| `HISTORY_DATABASE_URL` | Explicit PostgreSQL connection; no default |

HTTPS required except loopback HTTP development; both URLs use the same scheme.
Use the same hostname, preferably a single HTTPS proxy origin for API/frontend;
local ports may differ. Registered callback must match configuration. No automatic
migrations. Incomplete enabled configuration fails startup. Disabled mode needs
neither database driver nor credentials. Configure exact CORS origins before
separate-origin UI integration; current anonymous CORS remains local-only.

| Method/path | Behavior |
| --- | --- |
| GET `/api/auth/github/login` | GitHub redirect; no repository/email scope requested |
| GET `/api/auth/github/callback` | Consume state, exchange code, verify `/user`, map numeric ID to DB account |
| GET `/api/auth/me` | Own internal UUID or 401; disabled returns 503 |
| POST `/api/auth/logout` | Exact configured `Origin` required; revoke this device and pending login |

Callback redirects to fixed frontend root. No client-supplied owner, token or
redirect establishes identity. GitHub token stays in callback memory, never in
DB/browser/logs. Fixed HTTPS provider endpoints, 10-second HTTP timeout, no
redirect following; errors are generic. Numeric GitHub ID maps to stable UUID,
independent of changeable login names. Cookie stores a random credential; server
stores its hash. Private responses carry no-store and no-referrer headers.

Sessions are process-local, absolute 30-minute lifetime (not sliding), capacity
100. Pending logins expire after 10 minutes; capacity 100 includes in-flight
callbacks. Full capacity rejects new sessions without eviction. Reauthentication
rotates this device's token; logout preserves other devices and cancels pending
callbacks, including one waiting on provider/DB IO. Restart requires login again,
but the verified GitHub ID maps to the existing database account. These are
single-worker implementation defaults, not persistent login/multi-instance support.

`api.auth.get_identity` now protects the [record REST API](history-storage.md)
and remains the shared dependency for future analysis SSE. Existing
anonymous routes are not retrofitted. Long-running record jobs must capture
owner/record/revision and recheck session/record validity before publication;
retaining a previously returned Identity alone is insufficient. No automatic
anonymous data migration is introduced.

## Verification and release boundaries

`python scripts/check_backend.py` includes reviewed `tests/test_auth.py`: actual
FastAPI handlers with synthetic GitHub HTTP transport and account mapper, under
the external-network guard. Covers PKCE/state/browser binding/replay, expiration,
rotation/capacity/two-device logout, in-flight cancellation, provider/DB failures
and forged identity. Not real OAuth, PostgreSQL callback integration, browser
cookie behavior, UI or public deployment. No live credentials were used.

Before publication, proxy/server access logs must omit callback query strings
(authorization codes/state). Disable Uvicorn access logs or use a query-redacting
formatter; no HTTP body/header debug logging. Complete record business wiring/UI and job
revocation, verify HTTPS cookies/Origin/SSE and actual GitHub reachability, then
perform separately approved release acceptance. No resources are provisioned.

Implementation reference, accessed 2026-10-24 Asia/Shanghai:
[GitHub official OAuth web flow](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps)
(state, S256 PKCE, code exchange and identity revalidation).
