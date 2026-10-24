"""Optional GitHub identity boundary. No dotenv, credentials or network at import."""
from dataclasses import dataclass, field
import base64
import hashlib
import secrets
import threading
import time
from urllib.parse import urlencode, urlsplit

from fastapi import HTTPException, Request
import httpx


AUTH_COOKIE = 'ipa_account'
FLOW_COOKIE = 'ipa_login'


@dataclass(frozen=True)
class AuthConfig:
    client_id: str
    client_secret: str = field(repr=False)
    callback_url: str
    frontend_origin: str

    def __post_init__(self):
        if not self.client_id or not self.client_secret:
            raise ValueError('GitHub client configuration required')
        for value in (self.callback_url, self.frontend_origin):
            url = urlsplit(value)
            local = url.hostname in {'localhost', '127.0.0.1', '::1'}
            if (not url.netloc or url.username or url.password or url.query or url.fragment
                    or not (url.scheme == 'https' or (local and url.scheme == 'http'))):
                raise ValueError('Auth URLs require HTTPS, except loopback development')
        if urlsplit(self.frontend_origin).path not in ('', '/'):
            raise ValueError('Frontend origin cannot contain a path')
        if urlsplit(self.callback_url).path != '/api/auth/github/callback':
            raise ValueError('Unexpected callback path')
        if urlsplit(self.callback_url).scheme != urlsplit(self.frontend_origin).scheme:
            raise ValueError('Auth URLs must use the same scheme')

    @property
    def secure(self):
        return urlsplit(self.callback_url).scheme == 'https'


@dataclass(frozen=True)
class Identity:
    owner: object
    expires_at: float


class AuthService:
    """Bounded single-worker sessions; DB account identity survives a new login."""
    def __init__(self, config, account_for_github, *, transport=None,
                 clock=time.monotonic, capacity=100, ttl=1800):
        if capacity <= 0 or ttl <= 0:
            raise ValueError('Positive auth capacity/TTL required')
        self.config = config
        self.account_for_github = account_for_github
        self.transport = transport
        self.clock, self.capacity, self.ttl = clock, capacity, ttl
        self.flows, self.sessions, self.inflight = {}, {}, {}
        self.lock = threading.RLock()

    @staticmethod
    def digest(token):
        return hashlib.sha256(token.encode()).hexdigest()

    def prune(self):
        now = self.clock()
        self.flows = {key: value for key, value in self.flows.items() if value[2] > now}
        self.sessions = {key: value for key, value in self.sessions.items() if value.expires_at > now}
        self.inflight = {key: expiry for key, expiry in self.inflight.items() if expiry > now}

    def start(self, previous=None):
        with self.lock:
            self.prune()
            if previous:
                self.flows.pop(self.digest(previous), None)
                self.inflight.pop(self.digest(previous), None)
            if len(self.flows) + len(self.inflight) >= self.capacity:
                raise HTTPException(503, '登录请求容量已满，请稍后重试')
            binding, state, verifier = (secrets.token_urlsafe(32) for _ in range(3))
            self.flows[self.digest(binding)] = (state, verifier, self.clock() + 600)
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b'=').decode()
        query = urlencode(dict(client_id=self.config.client_id, redirect_uri=self.config.callback_url,
                               state=state, scope='', code_challenge=challenge, code_challenge_method='S256'))
        return binding, 'https://github.com/login/oauth/authorize?' + query

    def finish(self, binding, state, code, previous=None):
        with self.lock:
            self.prune()
            flow = self.flows.pop(self.digest(binding), None) if binding else None
            if not flow or not state or not secrets.compare_digest(flow[0].encode(), state.encode()) or not code:
                raise HTTPException(400, '登录请求无效或已过期，请重新登录')
            key = self.digest(binding)
            self.inflight[key] = flow[2]
        try:
            return self._finish(code, flow[1], key, previous)
        finally:
            with self.lock:
                self.inflight.pop(key, None)

    def _finish(self, code, verifier, flow_key, previous):
        # Consume before IO: retries/concurrent callbacks cannot reuse the code.
        try:
            with httpx.Client(transport=self.transport, timeout=10, follow_redirects=False, trust_env=False) as client:
                response = client.post('https://github.com/login/oauth/access_token',
                    headers={'Accept': 'application/json'}, data=dict(
                        client_id=self.config.client_id, client_secret=self.config.client_secret,
                        code=code, redirect_uri=self.config.callback_url, code_verifier=verifier))
                response.raise_for_status()
                token = response.json().get('access_token')
                if not isinstance(token, str) or not token:
                    raise ValueError('Missing provider token')
                response = client.get('https://api.github.com/user',
                    headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json'})
                response.raise_for_status()
                github_id = response.json().get('id')
                if type(github_id) is not int or not 0 < github_id <= 9223372036854775807:
                    raise ValueError('Invalid provider identity')
        except (httpx.HTTPError, ValueError, TypeError, AttributeError):
            raise HTTPException(502, 'GitHub身份验证失败，请重新登录') from None
        # No token is returned to the browser, logged or persisted.
        try:
            owner = self.account_for_github(github_id)
        except Exception:
            raise HTTPException(503, '账号存储暂不可用，请重新登录') from None
        with self.lock:
            self.prune()
            if flow_key not in self.inflight:
                raise HTTPException(400, '登录已取消或过期，请重新登录')
            if previous:
                self.sessions.pop(self.digest(previous), None)
            if len(self.sessions) >= self.capacity:
                raise HTTPException(503, '账号会话容量已满，请稍后重试')
            session = secrets.token_urlsafe(32)
            self.sessions[self.digest(session)] = Identity(owner, self.clock() + self.ttl)
            return session

    def resolve(self, token):
        with self.lock:
            self.prune()
            identity = self.sessions.get(self.digest(token)) if token else None
            if identity is None:
                raise HTTPException(401, '请先登录GitHub账号')
            return identity

    def logout(self, token, binding):
        with self.lock:
            if token:
                self.sessions.pop(self.digest(token), None)
            if binding:
                self.flows.pop(self.digest(binding), None)
                self.inflight.pop(self.digest(binding), None)


def get_auth(request: Request) -> AuthService:
    service = getattr(request.app.state, 'auth_service', None)
    if service is None:
        raise HTTPException(503, '账号登录尚未配置')
    return service


def get_identity(request: Request) -> Identity:
    """Shared REST/SSE dependency; ownership never comes from URL/body headers."""
    return get_auth(request).resolve(request.cookies.get(AUTH_COOKIE))
