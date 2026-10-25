"""Real registered HTTP/auth handlers; synthetic provider and storage adapter.

PostgreSQL concurrency and persistence are verified separately, never emulated
by this suite's in-memory adapter.
"""
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlsplit
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
import httpx
import pytest

from api.auth import AUTH_COOKIE, AuthConfig, AuthService
from api.history_errors import HistoryFull, HistoryMissing
from api.main import app


class SyntheticStore:
    def __init__(self):
        self.rows, self.calls = {}, []

    def list(self, owner):
        self.calls.append(('list', owner))
        return [row for row in self.rows.values() if row['owner_id'] == owner]

    def create(self, owner, title):
        if len(self.list(owner)) >= 20:
            raise HistoryFull()
        now = datetime.now(timezone.utc)
        row = dict(id=uuid4(), owner_id=owner, title=title, revision=0,
                   created_at=now, updated_at=now, inputs={}, results={})
        self.rows[row['id']] = row
        return row

    def get(self, owner, record):
        row = self.rows.get(record)
        if row is None or row['owner_id'] != owner:
            raise HistoryMissing()
        return row

    def rename(self, owner, record, title):
        row = self.get(owner, record)
        row['title'] = title
        return row

    def delete(self, owner, record):
        self.get(owner, record)
        del self.rows[record]


@pytest.fixture
def setup(monkeypatch):
    clock = [0.0]
    def provider(request):
        return httpx.Response(200, json={'access_token': 'synthetic'} if
                              request.url.path.endswith('access_token') else {'id': 101})
    service = AuthService(AuthConfig('synthetic', 'synthetic',
        'https://api.example.test/api/auth/github/callback', 'https://app.example.test'),
        lambda github_id: UUID(int=github_id), transport=httpx.MockTransport(provider), clock=lambda: clock[0])
    repository = SyntheticStore()
    monkeypatch.setattr(app.state, 'auth_service', service, raising=False)
    monkeypatch.setattr(app.state, 'history_store', repository, raising=False)
    # No lifespan/configuration/real provider or database is started.
    client = TestClient(app, base_url='https://api.example.test', follow_redirects=False)
    login = client.get('/api/auth/github/login')
    state = parse_qs(urlsplit(login.headers['location']).query)['state'][0]
    assert client.get('/api/auth/github/callback', params={'state': state, 'code': 'synthetic'}).status_code == 303
    client.headers['origin'] = 'https://app.example.test'
    yield client, repository, service, clock
    client.close()


def create(client, title=' Python 后端 '):
    response = client.post('/api/records', json={'title': title})
    assert response.status_code == 201, response.text
    return response.json()


def test_management_roundtrip_and_metadata_projection(setup):
    client, repository, _, _ = setup
    record = create(client)
    assert record['title'] == 'Python 后端' and record['revision'] == 0
    assert record['inputs'] == record['results'] == {}
    assert 'owner_id' not in record
    # Lists must not leak text/results even if an adapter returns extra fields.
    row = repository.rows[UUID(record['id'])]
    row.update(inputs={'jd_text': '合成岗位'}, results={'gap': {'score': 80}})
    listing = client.get('/api/records')
    assert set(listing.json()[0]) == {'id', 'title', 'revision', 'created_at', 'updated_at'}
    path = '/api/records/' + record['id']
    detail = client.get(path)
    assert detail.json()['inputs'] == {'jd_text': '合成岗位'}
    renamed = client.patch(path, json={'title': ' AI 应用 '})
    assert renamed.json()['title'] == 'AI 应用'
    assert renamed.json()['results'] == detail.json()['results']
    assert renamed.json()['revision'] == 0
    for response in (listing, detail, renamed):
        assert response.headers['cache-control'] == 'no-store'
        assert 'owner_id' not in response.text
    removed = client.delete(path)
    assert removed.status_code == 204 and removed.content == b''
    assert removed.headers['cache-control'] == 'no-store'
    assert client.get(path).status_code == 404
    assert client.get('/api/records').json() == []


@pytest.mark.parametrize('method', ['get', 'patch', 'delete'])
def test_foreign_and_missing_indistinguishable(setup, method):
    client, repository, service, _ = setup
    record = create(client)
    # Separate account with its own cookie; repository authorization still uses
    # the resolved identity rather than an ID in request headers/body/query.
    from api.auth import Identity
    service.sessions[service.digest('second-account')] = Identity(UUID(int=202), 1800)
    # TestClient is deliberately not a context manager (no production lifespan).
    other = TestClient(app, base_url='https://api.example.test')
    other.cookies.set(AUTH_COOKIE, 'second-account')
    other.headers['origin'] = 'https://app.example.test'
    kwargs = {'json': {'title': 'stolen'}} if method == 'patch' else {}
    foreign = other.request(method, '/api/records/' + record['id'], **kwargs)
    missing = other.request(method, '/api/records/' + str(uuid4()), **kwargs)
    assert foreign.status_code == missing.status_code == 404
    assert foreign.json() == missing.json() == {'detail': '记录不存在'}
    assert other.get('/api/records').json() == []
    other.close()
    assert repository.get(UUID(int=101), UUID(record['id']))['title'] == 'Python 后端'


@pytest.mark.parametrize('mode', ['absent', 'forged', 'expired', 'logout'])
@pytest.mark.parametrize('method,path', [('get', ''), ('post', ''), ('get', '/item'), ('patch', '/item'), ('delete', '/item')])
def test_every_endpoint_requires_live_account(setup, mode, method, path):
    client, repository, service, clock = setup
    record = create(client)
    if mode == 'absent':
        client.cookies.clear()
    elif mode == 'forged':
        client.cookies.clear()
        client.cookies.set(AUTH_COOKIE, 'forged')
    elif mode == 'expired':
        clock[0] = 1800
    else:
        assert client.post('/api/auth/logout').status_code == 200
    repository.calls.clear()
    kwargs = {'json': {'title': '无权写入'}} if method in ('post', 'patch') else {}
    response = client.request(method, '/api/records' + path.replace('item', record['id']), **kwargs)
    assert response.status_code == 401
    assert response.headers['cache-control'] == 'no-store'
    assert not repository.calls
    assert len(repository.rows) == 1


@pytest.mark.parametrize('origin', [None, 'null', 'https://evil.example.test', 'https://app.example.test.evil', 'http://app.example.test'])
@pytest.mark.parametrize('method', ['post', 'patch', 'delete'])
def test_mutations_require_exact_origin(setup, origin, method):
    client, repository, _, _ = setup
    record = create(client)
    client.headers.pop('origin')
    kwargs = {'headers': {'origin': origin}} if origin is not None else {}
    if method != 'delete':
        kwargs['json'] = {'title': '不应写入'}
    path = '/api/records' + ('' if method == 'post' else '/' + record['id'])
    assert client.request(method, path, **kwargs).status_code == 403
    assert len(repository.rows) == 1
    assert repository.rows[UUID(record['id'])]['title'] == 'Python 后端'


@pytest.mark.parametrize('body', [{'title': ''}, {'title': ' \t\n'}, {'title': 'a'*101}, {'title': None}, {'title': 5}, {'title': 'ok', 'owner_id': str(UUID(int=202))}, {'title': 'ok', 'inputs': {'jd_text': 'injected'}}, {'title': 'ok', 'results': {}}, {'title': 'ok', 'revision': 2}])
@pytest.mark.parametrize('method', ['post', 'patch'])
def test_invalid_titles_and_identity_or_data_injection_rejected(setup, body, method):
    client, repository, _, _ = setup
    record = create(client)
    path = '/api/records' + ('' if method == 'post' else '/' + record['id'])
    assert client.request(method, path, json=body).status_code == 422
    assert len(repository.rows) == 1
    assert repository.rows[UUID(record['id'])]['title'] == 'Python 后端'


def test_capacity_is_explicit_and_delete_releases_slot(setup):
    client, _, _, _ = setup
    records = [create(client, '岗位' + str(i)) for i in range(20)]
    response = client.post('/api/records', json={'title': '第21份'})
    assert response.status_code == 409 and '20' in response.json()['detail']
    assert len(client.get('/api/records').json()) == 20
    assert client.delete('/api/records/' + records[0]['id']).status_code == 204
    create(client, '删除后新建')


@pytest.mark.parametrize('method', ['get', 'patch', 'delete'])
def test_invalid_record_uuid_rejected(setup, method):
    client, _, _, _ = setup
    kwargs = {'json': {'title': 'ok'}} if method == 'patch' else {}
    assert client.request(method, '/api/records/not-a-uuid', **kwargs).status_code == 422


@pytest.mark.parametrize('method', ['list', 'create', 'get', 'rename', 'delete'])
def test_storage_failure_is_safe_and_not_retried(setup, monkeypatch, method):
    client, repository, _, _ = setup
    record = create(client)
    calls = []
    def broken(*args):
        calls.append(args)
        raise RuntimeError('private DSN and synthetic resume text')
    monkeypatch.setattr(repository, method, broken)
    verb = {'list': 'get', 'create': 'post', 'get': 'get', 'rename': 'patch', 'delete': 'delete'}[method]
    path = '/api/records' + ('' if method in ('list', 'create') else '/' + record['id'])
    kwargs = {'json': {'title': 'ok'}} if verb in ('post', 'patch') else {}
    response = client.request(verb, path, **kwargs)
    assert response.status_code == 503 and len(calls) == 1
    assert 'private' not in response.text and 'DSN' not in response.text
    assert response.headers['cache-control'] == 'no-store'


def test_unconfigured_history_and_auth_fail_closed(setup, monkeypatch):
    client, _, _, _ = setup
    monkeypatch.delattr(app.state, 'history_store')
    assert client.get('/api/records').status_code == 503
    monkeypatch.delattr(app.state, 'auth_service')
    assert client.get('/api/records').status_code == 503


def test_same_account_two_cookie_sessions_read_same_record(setup):
    client, _, service, _ = setup
    record = create(client)
    second = TestClient(app, base_url='https://api.example.test', follow_redirects=False)
    second.headers['origin'] = 'https://app.example.test'
    login = second.get('/api/auth/github/login')
    state = parse_qs(urlsplit(login.headers['location']).query)['state'][0]
    assert second.get('/api/auth/github/callback', params={'state': state, 'code': 'second'}).status_code == 303
    assert len(service.sessions) == 2
    assert second.get('/api/records/' + record['id']).json()['title'] == record['title']
    assert second.patch('/api/records/' + record['id'], json={'title': '设备二改名'}).status_code == 200
    assert client.get('/api/records/' + record['id']).json()['title'] == '设备二改名'
    assert second.post('/api/auth/logout').status_code == 200
    assert second.get('/api/records').status_code == 401
    assert len(service.sessions) == 1
    record['title'] = '设备二改名'
    assert client.get('/api/records/' + record['id']).json()['title'] == record['title']
    second.close()


def test_default_app_lifespan_leaves_history_disabled():
    with TestClient(app) as client:
        assert client.get('/api/records').status_code == 503
        assert client.get('/api/health').json() == {'status': 'ok'}
    assert not hasattr(app.state, 'history_store')
