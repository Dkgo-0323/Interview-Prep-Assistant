"""CI-only real browser/HTTP/PostgreSQL acceptance; identity/provider synthetic."""
import json
import os
from pathlib import Path
import socket
import threading
import time
from unittest.mock import patch

import pytest
from test_history_postgres import database  # isolated migrated schema + cleanup


def test_two_devices_browser_postgres(database, monkeypatch):
    from playwright.sync_api import sync_playwright, expect
    import uvicorn
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from api.auth import AUTH_COOKIE, AuthConfig, AuthService, Identity
    from api.routes import auth, history

    origin = 'http://127.0.0.1:3000'
    monkeypatch.setenv('DEBUG', 'true')
    monkeypatch.setenv('DASHSCOPE_API_KEY', 'offline-test-key')
    monkeypatch.setenv('LLM_BASE_URL', 'https://offline.invalid/v1')
    with patch('dotenv.load_dotenv', return_value=False):
        from api.routes import record_workflow as workflow
    fixtures = Path(__file__).parent / 'fixtures/workflow'
    responses = json.loads((fixtures / 'llm_responses.json').read_text(encoding='utf-8'))
    calls = []

    class SyntheticLLM:
        def call(self, *, response_model, **kwargs):
            calls.append(response_model.__name__)
            return response_model.model_validate(responses[response_model.__name__])

    monkeypatch.setattr(workflow, 'LLMService', SyntheticLLM)
    # No application .env import, no OAuth exchange, no model network access.
    original_connect = socket.socket.connect
    def local_connect(sock, address):
        if sock.family in (socket.AF_INET, socket.AF_INET6) and address[0] not in ('127.0.0.1', '::1'):
            raise RuntimeError('Browser acceptance blocks external sockets')
        return original_connect(sock, address)
    monkeypatch.setattr(socket.socket, 'connect', local_connect)
    store, _, _ = database
    owner = store.account_for_github(101)
    other = store.account_for_github(202)
    service = AuthService(AuthConfig('synthetic', 'synthetic',
        'http://127.0.0.1:8000/api/auth/github/callback', origin), store.account_for_github)
    for token, account in [('device-a', owner), ('device-b', owner), ('other', other)]:
        service.sessions[service.digest(token)] = Identity(account, service.clock() + 1800)
    app = FastAPI()
    app.state.auth_service, app.state.history_store = service, store
    app.add_middleware(CORSMiddleware, allow_origins=[origin], allow_credentials=True,
        allow_methods=['*'], allow_headers=['*'])
    app.include_router(auth.router, prefix='/api/auth')
    app.include_router(history.router, prefix='/api/records')
    app.include_router(workflow.router, prefix='/api/records')
    server = uvicorn.Server(uvicorn.Config(app, host='127.0.0.1', port=8000, access_log=False))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    try:
        deadline = time.monotonic() + 15
        while not server.started and thread.is_alive() and time.monotonic() < deadline:
            time.sleep(.05)
        assert server.started, 'API failed to start'
        with sync_playwright() as p:
            browser = p.chromium.launch()
            errors = []
            def device(token):
                context = browser.new_context(service_workers='block')
                context.add_cookies([dict(name=AUTH_COOKIE, value=token,
                    domain='127.0.0.1', path='/api', httpOnly=True, sameSite='Lax')])
                # Only allow real local requests; never fulfill or replace API responses.
                context.route('**/*', lambda route: route.continue_() if
                    route.request.url.startswith((origin + '/', 'http://127.0.0.1:8000/')) else route.abort())
                page = context.new_page()
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.set_default_timeout(15000)
                return page
            a, b, foreign = device('device-a'), device('device-b'), device('other')
            a.goto(origin + '/history')
            a.get_by_label('新记录名称').fill('合成双设备验收')
            a.get_by_role('button', name='创建记录', exact=True).click()
            expect(a.get_by_label('上传记录JD')).to_be_visible()
            a.get_by_label('上传记录JD').set_input_files(fixtures / 'jd.txt')
            expect(a.get_by_text('资料版本 1 · 刷新只读取已保存内容')).to_be_visible()
            a.get_by_label('上传记录简历').set_input_files(fixtures / 'resume.txt')
            expect(a.get_by_text('资料版本 2 · 刷新只读取已保存内容')).to_be_visible()
            a.get_by_role('button', name='开始分析当前资料', exact=True).click()
            expect(a.get_by_role('heading', name='已保存的匹配报告')).to_be_visible()
            a.get_by_role('button', name='生成本记录题目', exact=True).click()
            expect(a.get_by_role('heading', name='已保存的个性化题库（10题）')).to_be_visible()
            url = a.url
            count = len(calls)
            assert count >= 4
            b.goto(url)
            expect(b.get_by_role('heading', name='已保存的匹配报告')).to_be_visible()
            expect(b.locator('details')).to_have_count(10)
            b.reload()
            expect(b.locator('details')).to_have_count(10)
            b.locator('summary').first.click()
            expect(b.locator('details[open] p').first).not_to_be_empty()
            assert len(calls) == count, 'Reading/reload must not generate'
            rows = store.list(owner)
            assert len(rows) == 1
            saved = store.get(owner, rows[0]['id'])
            assert saved['revision'] == 2 and saved['results']['gap']['overall_match_score'] == 77
            assert len(saved['results']['questions']['questions']) == 10
            foreign.goto(url)
            expect(foreign.get_by_text('尚未读取记录，或记录已不可用。请刷新确认。')).to_be_visible()
            expect(foreign.get_by_role('heading', name='已保存的匹配报告')).to_have_count(0)
            a.get_by_role('button', name='退出本设备', exact=True).click()
            expect(a.get_by_role('link', name='使用 GitHub 登录')).to_be_visible()
            b.reload()
            expect(b.locator('details')).to_have_count(10)
            assert len(calls) == count
            assert not errors
            browser.close()
    finally:
        server.should_exit = True
        thread.join(timeout=15)
        assert not thread.is_alive(), 'API worker did not stop'
