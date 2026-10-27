# GitHub account boundary — partial S3 delivery

Opt-in backend OAuth authorization-code flow with S256 PKCE, browser-bound
one-use state and opaque HttpOnly account cookies. Account-bound upload, analysis
and questions now have separate record APIs; login/history UI is still pending.
The existing anonymous website remains active.

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
migrations. Stop the previous worker before starting the sole new worker: enabled
startup marks leftover running tasks interrupted before attaching adapters or
accepting traffic, without retrying models. Database failure aborts startup.
Incomplete enabled configuration fails startup. Disabled mode needs
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

`api.auth.get_identity` protects record management and the new
[record business API](history-storage.md). Both SSE and REST use the same cookie;
all generation requires an explicit POST with the exact frontend Origin.
The coordinator captures the originating token/identity and owner/record/revision/
attempt. Before publication or failure it resolves that original session again,
holding the auth lock only across the short DB transition so logout cannot slip
between validation and publication. Provider calls hold neither auth nor DB locks.
Revocation/expiry or disconnect only allow trusted exact-attempt interruption
(no results or provider payload); another device's session is unaffected. If a
synchronous provider thread is still active, cleanup waits for its actual return.
Existing anonymous routes are not retrofitted; no anonymous import is introduced.

## Verification and release boundaries

`python scripts/check_backend.py` includes reviewed `tests/test_auth.py`: actual
FastAPI handlers with synthetic GitHub HTTP transport and account mapper, under
the external-network guard. Covers PKCE/state/browser binding/replay, expiration,
rotation/capacity/two-device logout, in-flight cancellation, provider/DB failures
and forged identity. Not real OAuth, PostgreSQL callback integration, browser
cookie behavior, UI or public deployment. No live credentials were used.

Before publication, proxy/server access logs must omit callback query strings
(authorization codes/state). Disable Uvicorn access logs or use a query-redacting
formatter; no HTTP body/header debug logging. Complete login/history UI and
two-device browser acceptance, verify HTTPS cookies/Origin/SSE and actual GitHub reachability, then
perform separately approved release acceptance. No resources are provisioned.

Implementation reference, accessed 2026-10-24 Asia/Shanghai:
[GitHub official OAuth web flow](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps)
(state, S256 PKCE, code exchange and identity revalidation).
