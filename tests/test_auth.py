"""Real HTTP handlers with synthetic GitHub transport; no external calls/DB."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import base64
import threading
from urllib.parse import parse_qs, urlsplit
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient
import httpx
import pytest

from api.auth import AUTH_COOKIE, FLOW_COOKIE, AuthConfig, AuthService, get_identity
from api.routes.auth import router


@pytest.fixture
def setup():
    clock, calls, identities = [0.0], [], []
    def provider(request):
        calls.append(request)
        if request.url.path.endswith('access_token'):
            return httpx.Response(200, json={'access_token': 'synthetic-provider-token'})
        return httpx.Response(200, json={'id': 101, 'login': 'mutable-name'})
    def account(github_id):
        identities.append(github_id)
        return UUID(int=github_id)
    config = AuthConfig('synthetic-id', 'synthetic-secret',
                        'https://api.example.test/api/auth/github/callback', 'https://app.example.test')
    service = AuthService(config, account, transport=httpx.MockTransport(provider), clock=lambda: clock[0], capacity=2)
    app = FastAPI()
    app.include_router(router, prefix='/api/auth')
    app.state.auth_service = service
    @app.get('/api/protected-stream')
    def protected(identity=Depends(get_identity)):
        return {'owner': str(identity.owner)}
    client = TestClient(app, base_url='https://api.example.test', follow_redirects=False)
    return client, service, clock, calls, identities


def begin(client):
    response = client.get('/api/auth/github/login')
    assert response.status_code == 303
    query = parse_qs(urlsplit(response.headers['location']).query, keep_blank_values=True)
    assert query['scope'] == ['']
    assert query['code_challenge_method'] == ['S256']
    return query


def finish(client, query):
    return client.get('/api/auth/github/callback', params={'state': query['state'][0], 'code': 'synthetic-code'})


def test_complete_identity_pkce_and_private_cookies(setup):
    client, service, _, calls, identities = setup
    query = begin(client)
    response = finish(client, query)
    assert response.status_code == 303
    assert response.headers['location'] == 'https://app.example.test/'
    cookie = response.headers['set-cookie']
    assert 'HttpOnly' in cookie and 'Secure' in cookie and 'SameSite=lax' in cookie
    assert 'synthetic-provider-token' not in str(response.headers)
    assert response.headers['cache-control'] == 'no-store'
    assert response.headers['referrer-policy'] == 'no-referrer'
    assert identities == [101]
    form = parse_qs(calls[0].content.decode())
    challenge = base64.urlsafe_b64encode(hashlib.sha256(form['code_verifier'][0].encode()).digest()).rstrip(b'=').decode()
    assert challenge == query['code_challenge'][0]
    assert calls[1].headers['authorization'] == 'Bearer synthetic-provider-token'
    assert client.get('/api/auth/me').json() == {'account_id': str(UUID(int=101))}
    assert client.get('/api/protected-stream').json()['owner'] == str(UUID(int=101))
    assert client.cookies.get(AUTH_COOKIE) not in service.sessions
    assert finish(client, query).status_code == 400
    assert len(calls) == 2


@pytest.mark.parametrize('failure', ['state', 'unicode-state', 'cookie', 'expired', 'denied'])
def test_invalid_callback_never_contacts_provider(setup, failure):
    client, _, clock, calls, identities = setup
    query = begin(client)
    if failure == 'state':
        query['state'] = ['forged']
    elif failure == 'unicode-state':
        query['state'] = ['伪造state']
    elif failure == 'cookie':
        client.cookies.clear()
    elif failure == 'expired':
        clock[0] = 600
    if failure == 'denied':
        response = client.get('/api/auth/github/callback', params={'state': query['state'][0], 'error': 'access_denied'})
    else:
        response = finish(client, query)
    assert response.status_code == 400
    assert not calls and not identities


@pytest.mark.parametrize('mode', ['timeout', 'http', 'missing-token', 'invalid-json', 'bool-id', 'string-id', 'huge-id', 'db'])
def test_provider_and_database_fail_closed(setup, mode):
    client, service, _, _, identities = setup
    def failing(request):
        if mode == 'timeout':
            raise httpx.ReadTimeout('private failure', request=request)
        if mode == 'http':
            return httpx.Response(401, text='private failure')
        if mode == 'invalid-json':
            return httpx.Response(200, text='private failure')
        if request.url.path.endswith('access_token'):
            return httpx.Response(200, json={} if mode == 'missing-token' else {'access_token': 'synthetic'})
        return httpx.Response(200, json={'id': {'bool-id': True, 'string-id': '101', 'huge-id': 2**63}.get(mode, 101)})
    service.transport = httpx.MockTransport(failing)
    if mode == 'db':
        def unavailable(_):
            raise RuntimeError('private DSN failure')
        service.account_for_github = unavailable
    query = begin(client)
    response = finish(client, query)
    assert response.status_code == (503 if mode == 'db' else 502)
    assert 'private' not in response.text
    assert not client.cookies.get(AUTH_COOKIE)
    assert not service.sessions and not service.inflight and not identities
    assert finish(client, query).status_code == 400


def test_logout_origin_revocation_expiry_and_restart(setup):
    client, service, clock, _, _ = setup
    assert client.get('/api/auth/me', headers={'Authorization': 'Bearer forged', 'X-Owner': str(UUID(int=101))}).status_code == 401
    assert finish(client, begin(client)).status_code == 303
    token = client.cookies.get(AUTH_COOKIE)
    for origin in (None, 'https://evil.test', 'https://app.example.test.evil.test'):
        assert client.post('/api/auth/logout', headers={'Origin': origin} if origin else {}).status_code == 403
    assert client.get('/api/auth/me').status_code == 200
    assert client.post('/api/auth/logout', headers={'Origin': service.config.frontend_origin}).status_code == 200
    client.cookies.set(AUTH_COOKIE, token)
    assert client.get('/api/auth/me').status_code == 401
    client.cookies.clear()
    assert finish(client, begin(client)).status_code == 303
    clock[0] = 1800
    assert client.get('/api/auth/me').status_code == 401
    clock[0] = 0
    assert finish(client, begin(client)).status_code == 303
    service.sessions.clear()  # process restart loses login, not persisted history
    assert client.get('/api/auth/me').status_code == 401


def test_rotation_and_two_device_logout_scope(setup):
    client, service, _, _, _ = setup
    assert finish(client, begin(client)).status_code == 303
    first = client.cookies.get(AUTH_COOKIE)
    other = TestClient(client.app, base_url='https://api.example.test', follow_redirects=False)
    assert finish(other, begin(other)).status_code == 303
    assert other.get('/api/auth/me').json() == client.get('/api/auth/me').json()
    assert finish(client, begin(client)).status_code == 303
    assert service.digest(first) not in service.sessions
    assert other.post('/api/auth/logout', headers={'Origin': service.config.frontend_origin}).status_code == 200
    assert client.get('/api/auth/me').status_code == 200


def test_logout_cancels_inflight_callback(setup):
    client, service, _, _, _ = setup
    query = begin(client)
    binding = client.cookies.get(FLOW_COOKIE)
    entered, release = threading.Event(), threading.Event()
    def delayed(_):
        entered.set()
        assert release.wait(5)
        return UUID(int=101)
    service.account_for_github = delayed
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(service.finish, binding, query['state'][0], 'synthetic-code')
        assert entered.wait(5)
        service.logout(None, binding)
        release.set()
        with pytest.raises(HTTPException) as result:
            future.result(timeout=5)
        assert result.value.status_code == 400
    assert not service.sessions and not service.inflight


def test_capacity_and_flow_replacement(setup):
    client, service, clock, _, _ = setup
    first = begin(client)
    second = begin(client)
    assert finish(client, first).status_code == 400
    assert finish(client, second).status_code == 400  # invalid callback consumes binding
    service.start()
    service.start()
    assert client.get('/api/auth/github/login').status_code == 503
    clock[0] = 600
    assert client.get('/api/auth/github/login').status_code == 303


def test_callback_requires_same_browser_binding(setup):
    client, service, _, calls, _ = setup
    query = begin(client)
    other = TestClient(client.app, base_url='https://api.example.test', follow_redirects=False)
    assert finish(other, query).status_code == 400
    assert calls == []
    assert finish(client, query).status_code == 303
    assert len(service.sessions) == 1


def test_full_sessions_reject_new_device_without_eviction(setup):
    client, service, _, _, _ = setup
    service.capacity = 1
    assert finish(client, begin(client)).status_code == 303
    other = TestClient(client.app, base_url='https://api.example.test', follow_redirects=False)
    assert finish(other, begin(other)).status_code == 503
    assert client.get('/api/auth/me').status_code == 200
    assert other.get('/api/auth/me').status_code == 401
    assert not service.inflight


def test_starting_new_login_cancels_previous_pending_login(setup):
    client, service, _, calls, _ = setup
    query = begin(client)
    binding = client.cookies.get(FLOW_COOKIE)
    begin(client)
    with pytest.raises(HTTPException) as result:
        service.finish(binding, query['state'][0], 'synthetic-code')
    assert result.value.status_code == 400 and not calls


@pytest.mark.parametrize('url', ['http://public.test', 'https://evil.test/?q=1', 'https://user:pass@host.test', '//host.test', 'https://host.test/subpath'])
def test_invalid_configuration(url):
    with pytest.raises(ValueError):
        AuthConfig('id', 'secret', 'https://api.test/api/auth/github/callback', url)


def test_disabled_login_does_not_invent_identity():
    app = FastAPI()
    app.include_router(router, prefix='/api/auth')
    client = TestClient(app)
    assert client.get('/api/auth/github/login').status_code == 503
    assert client.get('/api/auth/me').status_code == 503
