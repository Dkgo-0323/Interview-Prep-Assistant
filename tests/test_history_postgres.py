"""Real PostgreSQL only. Explicit synthetic loopback DSN; never load dotenv."""
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import shutil
import subprocess
from uuid import uuid4

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict
from psycopg.rows import dict_row
import pytest

from api.history import HistoryConflict, HistoryFull, HistoryMissing, HistoryStore


def test_coordinator_interruption_is_exact_attempt_only(database):
    store, _, _ = database
    owner, record = task_record(store)
    old = store.claim_task(owner, record, 0, 'analysis')
    store.interrupt_task(owner, record, 0, 'analysis', old['attempt'])
    assert store.tasks(owner, record)[0]['status'] == 'interrupted'
    current = store.claim_task(owner, record, 0, 'analysis')
    with pytest.raises(HistoryConflict):
        store.interrupt_task(owner, record, 0, 'analysis', old['attempt'])
    with pytest.raises(HistoryMissing):
        store.interrupt_task(uuid4(), record, 0, 'analysis', current['attempt'])
    assert store.tasks(owner, record)[0]['status'] == 'running'


@pytest.mark.parametrize('change', ['none', 'logout', 'replace', 'delete'])
def test_record_business_chain_with_real_postgres(database, monkeypatch, change):
    """Real parsers/domain/HTTP/SQL; only identity and provider are synthetic."""
    import json
    from unittest.mock import Mock, patch
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from api.auth import AUTH_COOKIE, AuthConfig, AuthService, Identity
    # This independent DB job must also never read local dotenv/credentials.
    for key, value in dict(DEBUG='true', DASHSCOPE_API_KEY='offline-test-key',
        LLM_BASE_URL='https://offline.invalid/v1', LLM_DEFAULT_MODEL='qwen3.7-plus',
        GITHUB_AUTH_ENABLED='false').items():
        monkeypatch.setenv(key, value)
    with patch('dotenv.load_dotenv', return_value=False):
        from api.routes import record_workflow as workflow
    store, _, _ = database
    owner = store.account_for_github(101)
    record = store.create(owner, '真实数据库业务闭环')['id']
    service = AuthService(AuthConfig('synthetic', 'synthetic',
        'https://api.example.test/api/auth/github/callback', 'https://app.example.test'),
        store.account_for_github, clock=lambda: 0)
    for token in ('device-a', 'device-b'):
        service.sessions[service.digest(token)] = Identity(owner, 1800)
    app = FastAPI()
    app.state.auth_service, app.state.history_store = service, store
    app.include_router(workflow.router, prefix='/api/records')
    fixtures = Path(__file__).parent / 'fixtures/workflow'
    data = json.loads((fixtures / 'llm_responses.json').read_text(encoding='utf-8'))
    llm = Mock()
    llm.call.side_effect = lambda *, response_model, **kwargs: response_model.model_validate(data[response_model.__name__])
    monkeypatch.setattr(workflow, 'LLMService', lambda: llm)
    path = f'/api/records/{record}'
    with TestClient(app, base_url='https://api.example.test') as a, TestClient(app, base_url='https://api.example.test') as b:
        for client, token in ((a, 'device-a'), (b, 'device-b')):
            client.cookies.set(AUTH_COOKIE, token)
            client.headers['origin'] = 'https://app.example.test'
        for revision, kind in enumerate(('jd', 'resume')):
            response = a.post(path + '/upload/' + kind, params={'revision': revision},
                files={'file': (kind + '.txt', (fixtures / (kind + '.txt')).read_bytes())})
            assert response.status_code == 200, response.text
        response = a.post(path + '/analysis/stream', json={'revision': 2})
        assert '"complete"' in response.text and '"overall_match_score": 77' in response.text
        assert b.get(path + '/analysis/result').json()['data']['overall_match_score'] == 77
        assert b.post(path + '/questions/generate', json={'revision': 2}).json()['total'] == 10
        assert a.get(path + '/questions/cached').json()['total'] == 10
        assert HistoryStore(store.connect).get(owner, record)['results']['questions']['questions']
        assert all(task['status'] == 'completed' for task in b.get(path + '/tasks').json())
        calls = llm.call.call_count
        if change == 'none':
            # New repository/another device read saved snapshots without generation.
            assert a.get(path + '/questions/cached').status_code == 200
            assert llm.call.call_count == calls
            assert '"complete"' in a.post(path + '/analysis/stream', json={'revision': 2}).text
            assert b.get(path + '/questions/cached').status_code == 404
            assert len(store.tasks(owner, record)) == 1
        else:
            def change_during_provider(*, response_model, **kwargs):
                if change == 'logout':
                    service.logout('device-a', None)
                elif change == 'replace':
                    assert b.request('DELETE', path + '/inputs', json={'revision': 2}).status_code == 200
                else:
                    store.delete(owner, record)
                return response_model.model_validate(data[response_model.__name__])
            llm.call.side_effect = change_during_provider
            response = a.post(path + '/analysis/stream', json={'revision': 2})
            assert '"error"' in response.text and '"complete"' not in response.text
            assert llm.call.call_count == calls + 1  # Stops before resume/gap.
            if change != 'delete':
                task = next(t for t in store.tasks(owner, record) if t['kind'] == 'analysis')
                assert task['status'] == 'interrupted'
                # Revocation does not revoke the other device or leave a busy slot.
                assert b.get(path + '/tasks').status_code == 200
                if change == 'logout':
                    assert store.get(owner, record)['results']['gap']['overall_match_score'] == 77
                else:
                    assert store.get(owner, record)['results'] == {}
            else:
                with pytest.raises(HistoryMissing):
                    HistoryStore(store.connect).get(owner, record)


def test_record_http_with_real_postgres(database):
    """Compose real account-cookie HTTP handlers with the real SQL repository.

    Identity issuance is synthetic; this does not contact GitHub or the model.
    """
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from api.auth import AUTH_COOKIE, AuthConfig, AuthService, Identity
    from api.routes.history import router

    store, _, _ = database
    owner = store.account_for_github(101)
    other = store.account_for_github(202)
    service = AuthService(AuthConfig('synthetic', 'synthetic',
        'https://api.example.test/api/auth/github/callback', 'https://app.example.test'),
        store.account_for_github, clock=lambda: 0)
    service.sessions[service.digest('owner')] = Identity(owner, 1800)
    service.sessions[service.digest('other')] = Identity(other, 1800)
    app = FastAPI()
    app.state.auth_service, app.state.history_store = service, store
    app.include_router(router, prefix='/api/records')
    with TestClient(app, base_url='https://api.example.test') as client:
        client.cookies.set(AUTH_COOKIE, 'owner')
        client.headers['origin'] = 'https://app.example.test'
        response = client.post('/api/records', json={'title': ' 真实数据库合成记录 '})
        assert response.status_code == 201
        record = response.json()['id']
        from uuid import UUID
        assert store.get(owner, UUID(record))['title'] == '真实数据库合成记录'
        store.replace_inputs(owner, UUID(record), 0, {'jd_text': '合成岗位'})
        store.publish(owner, UUID(record), 1, 'gap', {'score': 80})
        path = '/api/records/' + record
        assert client.get(path).json()['results'] == {'gap': {'score': 80}}
        assert client.patch(path, json={'title': '另一设备改名'}).json()['revision'] == 1
        assert 'inputs' not in client.get('/api/records').json()[0]
        client.cookies.set(AUTH_COOKIE, 'other')
        for method in ('get', 'patch', 'delete'):
            kwargs = {'json': {'title': '越权'}} if method == 'patch' else {}
            assert client.request(method, path, **kwargs).status_code == 404
        assert client.get('/api/records').json() == []
        client.cookies.set(AUTH_COOKIE, 'owner')
        assert client.delete(path).status_code == 204
        assert client.get(path).status_code == 404
        with pytest.raises(HistoryMissing):
            HistoryStore(store.connect).get(owner, UUID(record))


@pytest.fixture
def database():
    dsn = os.environ.get('HISTORY_TEST_DSN')
    if not dsn:
        pytest.fail('HISTORY_TEST_DSN required: use a disposable loopback PostgreSQL')
    config = conninfo_to_dict(dsn)
    if config.get('host') not in {'localhost', '127.0.0.1', '::1'}:
        pytest.fail('history test database must be loopback')
    name = 'history_test_' + uuid4().hex
    with psycopg.connect(dsn, autocommit=True) as conn:
        conn.execute(sql.SQL('CREATE SCHEMA {}').format(sql.Identifier(name)))
    def connect():
        return psycopg.connect(dsn, row_factory=dict_row, options=f'-csearch_path={name}', connect_timeout=5)
    store = HistoryStore(connect)
    try:
        store.migrate()
        yield store, dsn, name
    finally:
        assert name.startswith('history_test_') and len(name) == 45
        with psycopg.connect(dsn, autocommit=True) as conn:
            conn.execute(sql.SQL('DROP SCHEMA IF EXISTS {} CASCADE').format(sql.Identifier(name)))


def test_accounts_and_idempotent_migration(database):
    store, _, _ = database
    store.migrate()
    assert store.account_for_github(101) == store.account_for_github(101)
    assert store.account_for_github(101) != store.account_for_github(102)
    with pytest.raises(ValueError):
        store.account_for_github(True)


def task_record(store):
    owner = store.account_for_github(301)
    item = store.create(owner, '任务合成记录')
    return owner, item['id']


def analysis_snapshot(label='synthetic'):
    return {'jd': {'title': label}, 'resume': {'name': label}, 'gap': {'score': 42}}


def test_task_claim_atomic_across_connections(database):
    store, _, _ = database
    owner, record = task_record(store)
    def claim(_):
        try:
            return HistoryStore(store.connect).claim_task(owner, record, 0, 'analysis')
        except HistoryConflict:
            return None
    with ThreadPoolExecutor(max_workers=4) as pool:
        claims = list(pool.map(claim, range(4)))
    assert sum(item is not None for item in claims) == 1
    assert store.tasks(owner, record)[0]['status'] == 'running'
    # Analysis and questions share the record lock: no cross-kind race.
    with pytest.raises(HistoryConflict):
        store.claim_task(owner, record, 0, 'questions')
    assert store.get(owner, record)['results'] == {}


def test_task_complete_retry_and_attempt_fencing(database):
    store, _, _ = database
    owner, record = task_record(store)
    first = store.claim_task(owner, record, 0, 'analysis')
    store.finish_task(owner, record, 0, 'analysis', first['attempt'], analysis_snapshot())
    assert store.tasks(owner, record)[0]['status'] == 'completed'
    assert store.get(owner, record)['results'] == analysis_snapshot()
    with pytest.raises(HistoryConflict):
        store.finish_task(owner, record, 0, 'analysis', first['attempt'], analysis_snapshot('old'))
    second = store.claim_task(owner, record, 0, 'analysis')
    assert second['attempt'] != first['attempt']
    with pytest.raises(HistoryConflict):
        store.fail_task(owner, record, 0, 'analysis', first['attempt'])
    assert store.tasks(owner, record)[0]['status'] == 'running'
    store.finish_task(owner, record, 0, 'analysis', second['attempt'], analysis_snapshot('new'))
    assert store.get(owner, record)['results']['jd']['title'] == 'new'


def test_failed_task_is_explicitly_retryable(database):
    store, _, _ = database
    owner, record = task_record(store)
    task = store.claim_task(owner, record, 0, 'analysis')
    store.fail_task(owner, record, 0, 'analysis', task['attempt'])
    assert store.tasks(owner, record)[0]['status'] == 'failed'
    assert store.get(owner, record)['results'] == {}
    assert store.claim_task(owner, record, 0, 'analysis')['attempt'] != task['attempt']


def test_exclusive_restart_interrupts_without_automatic_retry(database):
    store, _, _ = database
    owner, record = task_record(store)
    task = store.claim_task(owner, record, 0, 'analysis')
    restarted = HistoryStore(store.connect)
    # Recreating a repository/connection must never interrupt live work.
    assert restarted.tasks(owner, record)[0]['status'] == 'running'
    assert restarted.interrupt_tasks_on_startup() == 1
    assert restarted.interrupt_tasks_on_startup() == 0
    assert restarted.tasks(owner, record)[0]['status'] == 'interrupted'
    with pytest.raises(HistoryConflict):
        store.finish_task(owner, record, 0, 'analysis', task['attempt'], analysis_snapshot('late'))
    retry = restarted.claim_task(owner, record, 0, 'analysis')
    assert retry['attempt'] != task['attempt']
    restarted.finish_task(owner, record, 0, 'analysis', retry['attempt'], analysis_snapshot())


def test_replace_inputs_interrupts_and_rejects_old_attempt(database):
    store, _, _ = database
    owner, record = task_record(store)
    task = store.claim_task(owner, record, 0, 'analysis')
    store.replace_inputs(owner, record, 0, {'jd_text': '新岗位'})
    assert store.tasks(owner, record)[0]['status'] == 'interrupted'
    with pytest.raises(HistoryConflict):
        store.finish_task(owner, record, 0, 'analysis', task['attempt'], analysis_snapshot())
    with pytest.raises(HistoryConflict):
        store.claim_task(owner, record, 0, 'analysis')
    assert store.get(owner, record)['results'] == {}
    assert store.claim_task(owner, record, 1, 'analysis')['revision'] == 1


def test_task_owner_record_and_deletion_boundaries(database):
    store, _, _ = database
    owner, record = task_record(store)
    other = store.account_for_github(302)
    task = store.claim_task(owner, record, 0, 'analysis')
    for action in (
        lambda: store.tasks(other, record),
        lambda: store.claim_task(other, record, 0, 'analysis'),
        lambda: store.finish_task(other, record, 0, 'analysis', task['attempt'], analysis_snapshot()),
        lambda: store.fail_task(other, record, 0, 'analysis', task['attempt']),
    ):
        with pytest.raises(HistoryMissing):
            action()
    second = store.create(owner, '另一记录')['id']
    store.claim_task(owner, second, 0, 'analysis')
    with pytest.raises(HistoryConflict):
        store.finish_task(owner, second, 0, 'analysis', task['attempt'], analysis_snapshot())
    store.delete(owner, record)
    with pytest.raises(HistoryMissing):
        store.finish_task(owner, record, 0, 'analysis', task['attempt'], analysis_snapshot())
    with store.connect() as conn:
        assert conn.execute('SELECT count(*) AS n FROM preparation_tasks WHERE record_id=%s', (record,)).fetchone()['n'] == 0


def test_analysis_regeneration_invalidates_questions_atomically(database):
    store, _, _ = database
    owner, record = task_record(store)
    task = store.claim_task(owner, record, 0, 'questions')
    store.finish_task(owner, record, 0, 'questions', task['attempt'], {'questions': {'items': ['old']}})
    task = store.claim_task(owner, record, 0, 'analysis')
    store.finish_task(owner, record, 0, 'analysis', task['attempt'], analysis_snapshot())
    assert 'questions' not in store.get(owner, record)['results']
    assert [row['kind'] for row in store.tasks(owner, record)] == ['analysis']


def test_task_snapshot_failure_rolls_back_state_and_results(database):
    store, _, _ = database
    owner, record = task_record(store)
    task = store.claim_task(owner, record, 0, 'analysis')
    invalid = analysis_snapshot()
    invalid['gap'] = {'not_json_serializable': object()}
    with pytest.raises(TypeError):
        store.finish_task(owner, record, 0, 'analysis', task['attempt'], invalid)
    assert store.tasks(owner, record)[0]['status'] == 'running'
    assert store.get(owner, record)['results'] == {}
    store.finish_task(owner, record, 0, 'analysis', task['attempt'], analysis_snapshot())


@pytest.mark.parametrize('kind,results', [('other', {}), ('analysis', {'gap': {}}), ('questions', {'gap': {}})])
def test_invalid_task_contract_does_not_mutate(database, kind, results):
    store, _, _ = database
    owner, record = task_record(store)
    with pytest.raises(ValueError):
        store.finish_task(owner, record, 0, kind, uuid4(), results)
    assert store.tasks(owner, record) == []


def test_owner_isolation_and_no_text_in_listing(database):
    store, _, _ = database
    a, b = store.account_for_github(101), store.account_for_github(102)
    item = store.create(a, '岗位 A')
    assert store.list(b) == []
    assert 'inputs' not in store.list(a)[0]
    for action in [lambda: store.get(b,item['id']), lambda: store.rename(b,item['id'],'stolen'), lambda: store.delete(b,item['id'])]:
        with pytest.raises(HistoryMissing):
            action()
    with pytest.raises(HistoryConflict):
        store.publish(b, item['id'], 0, 'gap', {'score': 100})
    assert store.get(a,item['id'])['title'] == '岗位 A'


def test_capacity_is_atomic_across_connections(database):
    store, _, _ = database
    owner = store.account_for_github(101)
    for i in range(19):
        store.create(owner, f'岗位{i}')
    def create(i):
        try:
            store.create(owner,f'并发{i}')
            return True
        except HistoryFull:
            return False
    with ThreadPoolExecutor(max_workers=4) as pool:
        assert sum(pool.map(create, range(4))) == 1
    assert len(store.list(owner)) == 20
    store.delete(owner,store.list(owner)[0]['id'])
    store.create(owner,'删除后新建')
    assert len(store.list(owner)) == 20


def test_two_devices_and_repository_recreation(database):
    store, dsn, name = database
    owner = store.account_for_github(101)
    item = store.create(owner,'后端岗位')
    store.replace_inputs(owner,item['id'],0,{'jd_text':'合成岗位','resume_text':'合成简历'})
    second_device = HistoryStore(store.connect)
    assert second_device.account_for_github(101) == owner
    assert second_device.get(owner,item['id'])['inputs']['jd_text'] == '合成岗位'
    store.rename(owner,item['id'],'重新命名')
    assert second_device.list(owner)[0]['title'] == '重新命名'


def test_stale_inputs_and_deleted_record_cannot_publish(database):
    store, _, _ = database
    owner = store.account_for_github(101)
    item = store.create(owner,'A')
    store.replace_inputs(owner,item['id'],0,{'jd_text':'v1'})
    store.publish(owner,item['id'],1,'gap',{'score': 50})
    store.replace_inputs(owner,item['id'],1,{'jd_text':'v2'})
    assert store.get(owner,item['id'])['results'] == {}
    with pytest.raises(HistoryConflict):
        store.publish(owner,item['id'],1,'questions',{'old': True})
    with pytest.raises(HistoryConflict):
        store.replace_inputs(owner,item['id'],1,{'jd_text':'stale device'})
    store.delete(owner,item['id'])
    with pytest.raises(HistoryConflict):
        store.publish(owner,item['id'],2,'gap',{'old': True})
    assert store.list(owner) == []


def test_records_do_not_mix_results(database):
    store, _, _ = database
    owner = store.account_for_github(101)
    a,b = store.create(owner,'A'),store.create(owner,'B')
    store.publish(owner,a['id'],0,'questions',{'items':['synthetic A']})
    assert store.get(owner,b['id'])['results'] == {}
    assert store.get(owner,a['id'])['results']['questions']['items'] == ['synthetic A']


@pytest.mark.parametrize('title',[' ', 'x'*101])
def test_invalid_names_do_not_insert(database,title):
    store, _, _ = database
    owner = store.account_for_github(101)
    with pytest.raises(ValueError):
        store.create(owner,title)
    assert store.list(owner) == []


def test_backup_restore(database,tmp_path):
    store, dsn, name = database
    owner = store.account_for_github(101)
    item = store.create(owner,'备份恢复合成记录')
    store.replace_inputs(owner,item['id'],0,{'jd_text':'backup synthetic'})
    store.publish(owner,item['id'],1,'gap',{'score':42})
    task = store.claim_task(owner, item['id'], 1, 'questions')
    def binary(tool):
        pinned = Path('/usr/lib/postgresql/16/bin') / tool
        value = str(pinned) if pinned.exists() else shutil.which(tool)
        assert value, f'{tool} required for actual backup/restore acceptance'
        return value
    backup = tmp_path/'synthetic.dump'
    subprocess.run([binary('pg_dump'),'--dbname',dsn,'--schema',name,'--format=custom','--file',str(backup)], check=True, capture_output=True)
    with psycopg.connect(dsn,autocommit=True) as conn:
        conn.execute(sql.SQL('DROP SCHEMA {} CASCADE').format(sql.Identifier(name)))
    subprocess.run([binary('pg_restore'),'--dbname',dsn,'--exit-on-error',str(backup)],check=True,capture_output=True)
    restored = HistoryStore(store.connect)
    assert restored.account_for_github(101) == owner
    assert restored.get(owner,item['id'])['results']['gap']['score'] == 42
    assert restored.get(owner,item['id'])['inputs']['jd_text'] == 'backup synthetic'
    assert restored.tasks(owner, item['id'])[0]['attempt'] == task['attempt']
    assert restored.tasks(owner, item['id'])[0]['status'] == 'running'
    # Restoration never starts a model; the exclusive new worker must explicitly
    # mark restored in-flight attempts interrupted before serving requests.
    assert restored.interrupt_tasks_on_startup() == 1


def test_upgrade_from_001_preserves_existing_record(database):
    store, _, _ = database
    # Simulate a deployed 001 schema without touching any other test schema.
    with store.connect() as conn:
        conn.execute('DROP TABLE preparation_tasks')
    owner, record = task_record(store)
    # Existing 001 application wrote this snapshot before the additive migration.
    with store.connect() as conn:
        from psycopg.types.json import Jsonb
        conn.execute('UPDATE preparations SET inputs=%s WHERE id=%s',
                     (Jsonb({'jd_text': 'migration synthetic'}), record))
    store.migrate()
    store.migrate()
    assert store.get(owner, record)['inputs'] == {'jd_text': 'migration synthetic'}
    assert store.tasks(owner, record) == []
    assert store.claim_task(owner, record, 0, 'analysis')['status'] == 'running'


def test_enabled_startup_interrupts_real_database_before_traffic(database, monkeypatch):
    from unittest.mock import patch
    from fastapi.testclient import TestClient
    from api.auth import AUTH_COOKIE, Identity
    store, _, _ = database
    owner, record = task_record(store)
    task = store.claim_task(owner, record, 0, 'analysis')
    for key, value in dict(GITHUB_AUTH_ENABLED='true', GITHUB_CLIENT_ID='synthetic',
        GITHUB_CLIENT_SECRET='synthetic', GITHUB_CALLBACK_URL='https://api.example.test/api/auth/github/callback',
        AUTH_FRONTEND_ORIGIN='https://app.example.test', HISTORY_DATABASE_URL='synthetic-scoped-test-store',
        DEBUG='true', DASHSCOPE_API_KEY='offline-test-key', LLM_BASE_URL='https://offline.invalid/v1',
        LLM_DEFAULT_MODEL='qwen3.7-plus').items():
        monkeypatch.setenv(key, value)
    with patch('dotenv.load_dotenv', return_value=False):
        from api.main import app
    # Inject only the schema-scoped connection factory, not the startup method.
    monkeypatch.setattr(HistoryStore, 'from_dsn', classmethod(lambda cls, _: store))
    with TestClient(app, base_url='https://api.example.test') as client:
        auth = app.state.auth_service
        auth.sessions[auth.digest('synthetic')] = Identity(owner, auth.clock() + 1800)
        client.cookies.set(AUTH_COOKIE, 'synthetic')
        response = client.get(f'/api/records/{record}/tasks')
        assert response.status_code == 200
        assert response.json()[0]['status'] == 'interrupted'
        assert response.json()[0]['attempt'] == str(task['attempt'])
        assert store.get(owner, record)['results'] == {}
    assert not hasattr(app.state, 'history_store') and not hasattr(app.state, 'auth_service')
