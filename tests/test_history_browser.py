"""CI-only real browser/HTTP/PostgreSQL acceptance; identity/provider synthetic."""
import json
from urllib.parse import parse_qs, urlencode, urlsplit

import httpx
import os
from pathlib import Path
import socket
import subprocess
import ssl
from urllib.request import urlopen
import threading
import time
from unittest.mock import patch

import pytest
from test_history_postgres import database  # isolated migrated schema + cleanup


@pytest.fixture
def https_origin(tmp_path):
    """Real shipped proxy, isolated certificate; no system service changes."""
    cert, key = tmp_path / 'cert.pem', tmp_path / 'key.pem'
    subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes',
        '-days', '1', '-subj', '/CN=localhost', '-addext', 'subjectAltName=IP:127.0.0.1',
        '-keyout', str(key), '-out', str(cert)], check=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0))
        port = probe.getsockname()[1]
    origin = f'https://127.0.0.1:{port}'
    template = (Path(__file__).resolve().parents[1] / 'deploy/single-vm/nginx.conf').read_text()
    for old, new in {
        'listen 443 ssl;': f'listen 127.0.0.1:{port} ssl;',
        '/etc/interview-prep/tls/fullchain.pem': str(cert),
        '/etc/interview-prep/tls/privkey.pem': str(key),
    }.items():
        assert old in template
        template = template.replace(old, new)
    config = tmp_path / 'nginx.conf'
    config.write_text(f'pid {tmp_path}/nginx.pid;\nerror_log stderr;\nevents {{}}\nhttp {{\n{template}\n}}\n')
    process = subprocess.Popen(['nginx', '-p', f'{tmp_path}/', '-c', str(config),
        '-g', 'daemon off;'], stdout=subprocess.DEVNULL)
    try:
        context = ssl.create_default_context(cafile=str(cert))
        for attempt in range(100):
            try:
                with urlopen(origin + '/history', context=context, timeout=2) as response:
                    assert response.status == 200
                break
            except OSError:
                if process.poll() is not None or attempt == 99:
                    raise
                time.sleep(.1)
        yield origin
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def test_two_devices_browser_postgres(database, monkeypatch, https_origin):
    from playwright.sync_api import sync_playwright, expect
    import uvicorn
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from api.auth import AUTH_COOKIE, AuthConfig, AuthService, FLOW_COOKIE
    from api.routes import auth, history

    origin = https_origin
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
    # No application .env import; provider transport and model are offline replacements.
    original_connect = socket.socket.connect
    def local_connect(sock, address):
        if sock.family in (socket.AF_INET, socket.AF_INET6) and address[0] not in ('127.0.0.1', '::1'):
            raise RuntimeError('Browser acceptance blocks external sockets')
        return original_connect(sock, address)
    monkeypatch.setattr(socket.socket, 'connect', local_connect)
    store, _, _ = database
    owner = store.account_for_github(101)
    other = store.account_for_github(202)
    provider_calls = []
    challenges = {}
    def provider(request):
        provider_calls.append(request.url.path)
        if request.url.path == '/login/oauth/access_token':
            import base64
            import hashlib
            form = parse_qs(request.content.decode())
            code = form['code'][0]
            challenge = base64.urlsafe_b64encode(hashlib.sha256(
                form['code_verifier'][0].encode()).digest()).rstrip(b'=').decode()
            assert challenge == challenges[code]
            assert form['redirect_uri'] == [origin + '/api/auth/github/callback']
            return httpx.Response(200, json={'access_token': code})
        assert request.url.host == 'api.github.com' and request.url.path == '/user'
        code = request.headers['authorization'].removeprefix('Bearer ')
        return httpx.Response(200, json={'id': 202 if code == 'other' else 101})
    service = AuthService(AuthConfig('synthetic', 'synthetic',
        origin + '/api/auth/github/callback', origin), store.account_for_github,
        transport=httpx.MockTransport(provider))
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
            def device(code):
                context = browser.new_context(service_workers='block', ignore_https_errors=True)
                # Obtain the real login redirect without following it to GitHub.
                # Playwright routing does not re-route every redirect hop.
                context.route('**/*', lambda route: route.continue_() if
                    route.request.url.startswith(origin + '/') else route.abort())
                start = context.request.get(origin + '/api/auth/github/login', max_redirects=0)
                assert start.status == 303
                parsed = urlsplit(start.headers['location'])
                assert parsed.scheme == 'https' and parsed.netloc == 'github.com'
                assert parsed.path == '/login/oauth/authorize'
                query = parse_qs(parsed.query, keep_blank_values=True)
                assert query['scope'] == ['']
                assert query['code_challenge_method'] == ['S256']
                assert query['redirect_uri'] == [origin + '/api/auth/github/callback']
                flow = context.cookies(origin + '/api/auth/github/callback')
                assert any(c['name'] == FLOW_COOKIE and c['secure'] and c['httpOnly']
                    and c['sameSite'] == 'Lax' for c in flow)
                challenges[code] = query['code_challenge'][0]
                callback = origin + '/api/auth/github/callback?' + urlencode(
                    {'state': query['state'][0], 'code': code})
                page = context.new_page()
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.set_default_timeout(15000)
                page.goto(callback)
                page.wait_for_url(origin + '/')
                cookies = context.cookies(origin + '/api/auth/github/callback')
                assert not any(c['name'] == FLOW_COOKIE for c in cookies)
                account_cookie = next(c for c in cookies if c['name'] == AUTH_COOKIE)
                assert account_cookie['secure'] and account_cookie['httpOnly']
                assert account_cookie['sameSite'] == 'Lax' and account_cookie['path'] == '/api'
                assert context.request.get(origin + '/api/auth/me').status == 200
                count_before = len(provider_calls)
                replay = context.request.get(callback, max_redirects=0)
                assert replay.status == 400
                assert len(provider_calls) == count_before, 'Replay must not exchange again'
                return page
            a, b, foreign = device('device-a'), device('device-b'), device('other')
            assert len(provider_calls) == 6
            a.goto(origin + '/history')
            # Browser sends the secure cookie through HTTPS; real API checks Origin.
            assert a.context.request.get(origin + '/api/auth/me').status == 200
            before = len(store.list(owner))
            denied = a.context.request.post(origin + '/api/records',
                headers={'Origin': 'https://foreign.invalid'}, data={'title': 'rejected'})
            assert denied.status == 403
            assert len(store.list(owner)) == before
            cookies = a.context.cookies(origin + '/api/auth/me')
            assert any(c['name'] == AUTH_COOKIE and c['secure'] and c['httpOnly'] for c in cookies)
            a.get_by_label('新记录名称').fill('合成双设备验收')
            a.get_by_role('button', name='创建记录', exact=True).click()
            expect(a.get_by_label('上传记录JD')).to_be_visible()
            expect(a.get_by_label('上传记录JD')).to_be_enabled()
            a.get_by_label('上传记录JD').set_input_files(fixtures / 'jd.txt')
            expect(a.get_by_text('资料版本 1 · 刷新只读取已保存内容')).to_be_visible()
            # Revision renders before apply() finishes reading task status.
            # set_input_files does not wait for enabled like a user click does.
            expect(a.get_by_label('上传记录简历')).to_be_enabled()
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
