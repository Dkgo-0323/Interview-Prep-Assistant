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
