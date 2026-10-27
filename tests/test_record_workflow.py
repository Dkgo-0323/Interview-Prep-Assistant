"""Account business HTTP, actual parsers/analyzers, synthetic identity/LLM/DB.

This adapter only tests coordination; real SQL is tested by the PostgreSQL job.
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import threading
from unittest.mock import Mock
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
import pytest

from api.auth import AUTH_COOKIE, AuthConfig, AuthService, Identity
from api.history_errors import HistoryConflict, HistoryMissing
from api.main import app
from api.record_workflow import RecordAccess, RecordOperation
from api.routes import record_workflow as workflow

FIXTURES = Path(__file__).parent / 'fixtures/workflow'


class MemoryWorkflowStore:
    """Deterministic storage boundary, not PostgreSQL transaction evidence."""
    def __init__(self, owner):
        self.owner, self.record = owner, uuid4()
        self.row = dict(id=self.record, title='合成准备记录', revision=0, owner_id=owner,
                        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
                        inputs={}, results={})
        self.jobs, self.finishes = {}, 0
        self.lock = threading.RLock()

    def get(self, owner, record):
        with self.lock:
            if self.row is None or owner != self.owner or record != self.record:
                raise HistoryMissing()
            return deepcopy(self.row)

    def tasks(self, owner, record):
        self.get(owner, record)
        return deepcopy(list(self.jobs.values()))

    def replace_inputs(self, owner, record, revision, inputs):
        with self.lock:
            if self.get(owner, record)['revision'] != revision:
                raise HistoryConflict()
            self.row.update(inputs=deepcopy(inputs), results={}, revision=revision + 1)
            for task in self.jobs.values():
                if task['status'] == 'running':
                    task['status'] = 'interrupted'
            return self.get(owner, record)

    def claim_task(self, owner, record, revision, kind):
        with self.lock:
            if self.get(owner, record)['revision'] != revision or any(t['status'] == 'running' for t in self.jobs.values()):
                raise HistoryConflict()
            task = dict(kind=kind, revision=revision, attempt=uuid4(), status='running',
                        updated_at=datetime.now(timezone.utc))
            self.jobs[kind] = task
            return deepcopy(task)

    def transition(self, owner, record, revision, kind, attempt, status):
        with self.lock:
            task = self.jobs.get(kind)
            if (self.get(owner, record)['revision'] != revision or not task
                    or task['attempt'] != attempt or task['status'] != 'running'):
                raise HistoryConflict()
            task['status'] = status

    def finish_task(self, owner, record, revision, kind, attempt, results):
        with self.lock:
            self.transition(owner, record, revision, kind, attempt, 'completed')
            if kind == 'analysis':
                self.row['results'].pop('questions', None)
                self.jobs.pop('questions', None)
            self.row['results'].update(deepcopy(results))
            self.finishes += 1

    def fail_task(self, *args):
        self.transition(*args, 'failed')

    def interrupt_task(self, *args):
        self.transition(*args, 'interrupted')


@pytest.fixture
def setup(monkeypatch):
    owner = uuid4()
    clock = [0.0]
    service = AuthService(AuthConfig('synthetic', 'synthetic',
        'https://api.example.test/api/auth/github/callback', 'https://app.example.test'),
        lambda _: owner, clock=lambda: clock[0])
    for token, account in (('device-a', owner), ('device-b', owner), ('other', uuid4())):
        service.sessions[service.digest(token)] = Identity(account, 1800)
    repository = MemoryWorkflowStore(owner)
    monkeypatch.setattr(app.state, 'auth_service', service, raising=False)
    monkeypatch.setattr(app.state, 'history_store', repository, raising=False)
    data = json.loads((FIXTURES / 'llm_responses.json').read_text(encoding='utf-8'))
    llm = Mock()
    llm.call.side_effect = lambda *, response_model, **kwargs: response_model.model_validate(data[response_model.__name__])
    monkeypatch.setattr(workflow, 'LLMService', Mock(return_value=llm))
    clients = []
    for token in ('device-a', 'device-b', 'other'):
        client = TestClient(app, base_url='https://api.example.test')
        client.cookies.set(AUTH_COOKIE, token)
        client.headers['origin'] = 'https://app.example.test'
        clients.append(client)
    yield *clients, repository, service, clock, llm
    for client in clients:
        client.close()


def path(repository, suffix):
    return f'/api/records/{repository.record}/{suffix}'


def upload_pair(client, repository):
    for revision, kind in enumerate(('jd', 'resume')):
        response = client.post(path(repository, f'upload/{kind}'), params={'revision': revision},
            files={'file': (kind + '.txt', (FIXTURES / (kind + '.txt')).read_bytes())})
        assert response.status_code == 200, response.text
        assert response.json()['revision'] == revision + 1


def analyze(client, repository, revision=2):
    response = client.post(path(repository, 'analysis/stream'), json={'revision': revision})
    assert response.status_code == 200
    return [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith('data: ')]


def test_two_devices_complete_chain_and_reanalysis(setup):
    a, b, other, repo, _, _, llm = setup
    upload_pair(a, repo)
    events = analyze(a, repo)
    assert [event['step'] for event in events] == ['jd_start', 'jd_done', 'resume_start', 'resume_done', 'gap_start', 'complete']
    assert events[-1]['data']['overall_match_score'] == 77
    report = b.get(path(repo, 'analysis/result'))
    assert report.json()['data'] == events[-1]['data']
    generated = b.post(path(repo, 'questions/generate'), json={'revision': 2, 'num_questions': 10})
    assert generated.status_code == 200 and generated.json()['total'] == 10
    calls = llm.call.call_count
    assert a.get(path(repo, 'questions/cached')).json() == generated.json()
    assert a.get(path(repo, 'tasks')).json()[0]['status'] == 'completed'
    assert llm.call.call_count == calls  # Reading/status/other device never generate.
    assert other.get(path(repo, 'analysis/result')).status_code == 404
    assert analyze(a, repo)[-1]['step'] == 'complete'
    assert b.get(path(repo, 'questions/cached')).status_code == 404
    assert len(repo.jobs) == 1 and repo.finishes == 3


@pytest.mark.parametrize('suffix,method', [('tasks', 'get'), ('analysis/result', 'get'),
    ('questions/cached', 'get'), ('analysis/stream', 'post'), ('questions/generate', 'post'),
    ('upload/jd', 'post'), ('inputs', 'delete')])
def test_identity_owner_and_origin_boundaries(setup, suffix, method):
    a, _, other, repo, service, _, llm = setup
    kwargs = {'json': {'revision': 0}} if method != 'get' else {}
    if suffix == 'upload/jd':
        kwargs = {'params': {'revision': 0}, 'files': {'file': ('jd.txt', b'synthetic JD content')}}
    assert other.request(method, path(repo, suffix), **kwargs).status_code == 404
    if method != 'get':
        assert a.request(method, path(repo, suffix), headers={'origin': 'https://evil.test'}, **kwargs).status_code == 403
    service.logout('device-a', None)
    response = a.request(method, path(repo, suffix), **kwargs)
    assert response.status_code == 401 and response.headers['cache-control'] == 'no-store'
    assert repo.row['revision'] == 0 and not repo.jobs
    llm.call.assert_not_called()


@pytest.mark.parametrize('body', [{'revision': -1}, {'revision': True}, {'revision': '0'},
    {'revision': 0, 'owner': 'fake'}, {}, {'revision': 0, 'num_questions': 9}])
def test_strict_generation_contract(setup, body):
    a, _, _, repo, _, _, llm = setup
    assert a.post(path(repo, 'questions/generate'), json=body).status_code == 422
    llm.call.assert_not_called()


def test_missing_prerequisites_and_stale_revision_do_not_call_model(setup):
    a, _, _, repo, _, _, llm = setup
    assert analyze(a, repo, 0)[-1]['data']['status'] == 400
    assert repo.jobs['analysis']['status'] == 'failed'
    assert a.post(path(repo, 'questions/generate'), json={'revision': 0}).status_code == 400
    upload_pair(a, repo)
    assert analyze(a, repo, 1)[-1]['data']['status'] == 409
    assert a.post(path(repo, 'questions/generate'), json={'revision': 1}).status_code == 409
    assert a.post(path(repo, 'upload/jd'), params={'revision': 1},
        files={'file': ('jd.txt', b'synthetic stale text')}).status_code == 409
    llm.call.assert_not_called()


@pytest.mark.parametrize('change', ['logout', 'expire', 'replace', 'delete'])
@pytest.mark.parametrize('kind', ['analysis', 'questions'])
def test_late_provider_return_cannot_publish(setup, change, kind):
    a, b, _, repo, service, clock, llm = setup
    upload_pair(a, repo)
    if kind == 'questions':
        assert analyze(a, repo)[-1]['step'] == 'complete'
    finishes = repo.finishes
    def changed(*, response_model, **kwargs):
        if change == 'logout':
            assert a.post('/api/auth/logout').status_code == 200
        elif change == 'expire':
            clock[0] = 1800
        elif change == 'replace':
            assert b.request('DELETE', path(repo, 'inputs'), json={'revision': 2}).status_code == 200
        else:
            repo.row = None  # SQL deletion/cascade is tested in real PostgreSQL.
        return response_model.model_validate(data[response_model.__name__])
    data = json.loads((FIXTURES / 'llm_responses.json').read_text(encoding='utf-8'))
    llm.call.side_effect = changed
    if kind == 'analysis':
        events = analyze(a, repo)
        assert events[-1]['step'] == 'error' and events[-1]['data']['status'] in (401, 404, 409)
        assert not any(event['step'] == 'complete' for event in events)
    else:
        assert a.post(path(repo, 'questions/generate'), json={'revision': 2}).status_code in (401, 404, 409)
    assert repo.finishes == finishes
    if change != 'delete':
        assert repo.jobs[kind]['status'] == 'interrupted'
    if change == 'logout':
        assert b.get(path(repo, 'tasks')).status_code == 200
        # Trusted cleanup releases the record, not another device's login.
        assert service.resolve('device-b').owner == repo.owner


def test_failed_model_is_safe_and_explicit_retry_gets_new_attempt(setup):
    a, _, _, repo, _, _, llm = setup
    upload_pair(a, repo)
    original = llm.call.side_effect
    llm.call.side_effect = RuntimeError('PRIVATE_PROVIDER_BODY')
    events = analyze(a, repo)
    assert events[-1]['step'] == 'error' and 'PRIVATE_PROVIDER_BODY' not in str(events)
    assert repo.jobs['analysis']['status'] == 'failed' and not repo.row['results']
    attempt = repo.jobs['analysis']['attempt']
    llm.call.side_effect = original
    assert analyze(a, repo)[-1]['step'] == 'complete'
    assert repo.jobs['analysis']['attempt'] != attempt


def test_questions_failure_never_stores_partial_snapshot(setup):
    a, _, _, repo, _, _, llm = setup
    upload_pair(a, repo)
    assert analyze(a, repo)[-1]['step'] == 'complete'
    original = llm.call.side_effect
    llm.call.side_effect = RuntimeError('PRIVATE_QUESTION_PROVIDER_BODY')
    response = a.post(path(repo, 'questions/generate'), json={'revision': 2})
    assert response.status_code == 500 and 'PRIVATE' not in response.text
    assert repo.jobs['questions']['status'] == 'failed'
    assert 'questions' not in repo.row['results'] and repo.finishes == 1
    attempt = repo.jobs['questions']['attempt']
    llm.call.side_effect = original
    assert a.post(path(repo, 'questions/generate'), json={'revision': 2}).status_code == 200
    assert repo.jobs['questions']['attempt'] != attempt


@pytest.mark.parametrize('name,content,status', [('jd.exe', b'bad type', 400),
    ('jd.txt', b'', 400), ('jd.txt', b'tiny', 422)])
def test_upload_rejection_keeps_existing_record(setup, name, content, status):
    a, _, _, repo, _, _, llm = setup
    response = a.post(path(repo, 'upload/jd'), params={'revision': 0}, files={'file': (name, content)})
    assert response.status_code == status
    assert repo.row['revision'] == 0 and repo.row['inputs'] == {}
    llm.call.assert_not_called()


def test_saved_corrupt_results_fail_safely_without_generation(setup):
    a, _, _, repo, _, _, llm = setup
    repo.row['results'] = {'gap': {'private': 'INVALID_STORED_DATA'}, 'questions': {'wrong': True}}
    for suffix in ('analysis/result', 'questions/cached'):
        response = a.get(path(repo, suffix))
        assert response.status_code == 503 and 'INVALID' not in response.text
    llm.call.assert_not_called()


def test_storage_finish_failure_is_not_retried(setup, monkeypatch):
    a, _, _, repo, _, _, _ = setup
    upload_pair(a, repo)
    finish = Mock(side_effect=RuntimeError('PRIVATE_DSN'))
    monkeypatch.setattr(repo, 'finish_task', finish)
    events = analyze(a, repo)
    assert events[-1]['data']['status'] == 503 and 'PRIVATE' not in str(events)
    finish.assert_called_once()
    assert not repo.row['results'] and repo.jobs['analysis']['status'] == 'failed'


def test_busy_record_rejects_second_device_without_extra_calls(setup):
    a, b, _, repo, _, _, llm = setup
    upload_pair(a, repo)
    entered, release = threading.Event(), threading.Event()
    original = llm.call.side_effect
    def block(**kwargs):
        entered.set()
        assert release.wait(10)
        return original(**kwargs)
    llm.call.side_effect = block
    with ThreadPoolExecutor(1) as pool:
        first = pool.submit(analyze, a, repo)
        try:
            assert entered.wait(10)
            assert analyze(b, repo)[-1]['data']['status'] == 409
            assert b.post(path(repo, 'questions/generate'), json={'revision': 2}).status_code == 409
            assert llm.call.call_count == 1
        finally:
            release.set()
        assert first.result(10)[-1]['step'] == 'complete'


def test_cancelled_stream_keeps_busy_until_thread_exits(setup):
    _, _, _, repo, service, _, llm = setup
    repo.replace_inputs(repo.owner, repo.record, 0, {
        key + '_text': (FIXTURES / (key + '.txt')).read_text(encoding='utf-8') for key in ('jd', 'resume')})
    entered, release = threading.Event(), threading.Event()
    original = llm.call.side_effect
    def block(**kwargs):
        entered.set()
        assert release.wait(10)
        return original(**kwargs)
    llm.call.side_effect = block
    operation = RecordOperation(RecordAccess(service, 'device-a', service.resolve('device-a'), repo, repo.record), 1, 'analysis')
    async def scenario():
        async def consume():
            async for _ in workflow.stream(operation):
                pass
        task = asyncio.create_task(consume())
        assert await asyncio.to_thread(entered.wait, 10)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert repo.jobs['analysis']['status'] == 'running'
        with pytest.raises(HistoryConflict):
            repo.claim_task(repo.owner, repo.record, 1, 'questions')
        release.set()
        await operation.pending
        await asyncio.sleep(0)  # Delivery of exact-attempt cleanup callback.
        assert repo.jobs['analysis']['status'] == 'interrupted'
        assert not repo.row['results'] and repo.finishes == 0
    try:
        asyncio.run(scenario())
    finally:
        release.set()


def test_upload_rechecks_revocation_after_parse(setup, monkeypatch):
    a, _, _, repo, service, _, llm = setup
    async def parse(_):
        service.logout('device-a', None)
        return 'synthetic parsed text'
    monkeypatch.setattr(workflow, '_read_and_parse', parse)
    assert a.post(path(repo, 'upload/jd'), params={'revision': 0}, files={'file': ('jd.txt', b'synthetic')}).status_code == 401
    assert repo.row['inputs'] == {} and repo.row['revision'] == 0
    llm.call.assert_not_called()


def test_bad_domain_and_storage_fail_closed(setup, monkeypatch):
    a, _, _, repo, _, _, llm = setup
    upload_pair(a, repo)
    monkeypatch.setattr(workflow, 'analyze_jd', lambda *args: {'private': 'invalid'})
    assert analyze(a, repo)[-1]['data']['status'] == 500
    assert not repo.row['results'] and repo.finishes == 0
    assert repo.jobs['analysis']['status'] == 'failed'
    def unavailable(*args):
        raise RuntimeError('SECRET_DSN_AND_SQL')
    monkeypatch.setattr(repo, 'get', unavailable)
    response = a.get(path(repo, 'analysis/result'))
    assert response.status_code == 503 and 'SECRET' not in response.text
    # No automatic retry of a storage mutation.
    llm.call.assert_not_called()


def test_mutated_domain_instance_is_revalidated_before_storage(setup, monkeypatch):
    from models.schemas import GapAnalysis
    a, _, _, repo, _, _, _ = setup
    upload_pair(a, repo)
    data = json.loads((FIXTURES / 'llm_responses.json').read_text(encoding='utf-8'))
    invalid = GapAnalysis.model_validate(data['GapAnalysis'])
    invalid.overall_match_score = 200  # Pydantic instances do not validate assignment by default.
    monkeypatch.setattr(workflow, 'analyze_gap', lambda *args: invalid)
    assert analyze(a, repo)[-1]['data']['status'] == 500
    assert repo.row['results'] == {} and repo.finishes == 0


@pytest.mark.parametrize('fails', [False, True])
def test_exclusive_startup_interrupts_before_traffic(monkeypatch, fails):
    import sys
    from types import SimpleNamespace
    repository = Mock()
    if fails:
        repository.interrupt_tasks_on_startup.side_effect = RuntimeError('synthetic unavailable')
    factory = Mock(return_value=repository)
    monkeypatch.setitem(sys.modules, 'api.history', SimpleNamespace(HistoryStore=SimpleNamespace(from_dsn=factory)))
    for key, value in dict(GITHUB_AUTH_ENABLED='true', GITHUB_CLIENT_ID='synthetic',
        GITHUB_CLIENT_SECRET='synthetic', GITHUB_CALLBACK_URL='https://api.example.test/api/auth/github/callback',
        AUTH_FRONTEND_ORIGIN='https://app.example.test', HISTORY_DATABASE_URL='synthetic-not-a-dsn').items():
        monkeypatch.setenv(key, value)
    if fails:
        with pytest.raises(RuntimeError, match='synthetic unavailable'):
            with TestClient(app):
                pytest.fail('must not accept traffic')
    else:
        with TestClient(app) as client:
            repository.interrupt_tasks_on_startup.assert_called_once_with()
            assert client.get('/api/health').status_code == 200
            assert app.state.history_store is repository
    assert not hasattr(app.state, 'history_store') and not hasattr(app.state, 'auth_service')
    repository.interrupt_tasks_on_startup.assert_called_once_with()
