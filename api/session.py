"""Bounded, process-local anonymous sessions and guarded asynchronous work.

No input text is kept in the cookie. Restarting the process loses all sessions.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
import math
import secrets
import threading
import time
from typing import Callable

from fastapi import HTTPException

COOKIE_NAME = "interview_session"
RESULT_KEYS = ("jd", "resume", "gap", "questions", "profile")


class SessionExpired(HTTPException):
    def __init__(self):
        super().__init__(410, "会话已过期或服务已重启，请返回首页重新上传资料")


class Superseded(HTTPException):
    def __init__(self):
        super().__init__(409, "资料已更新或清除，本次旧结果已作废，请重新分析")


@dataclass(eq=False)
class Operation:
    session: Session
    kind: str
    revision: int
    inputs: dict
    pending: int = 0
    finished: bool = False

    def check(self):
        with self.session.store.lock:
            self.session._check()
            if self.finished or self.revision != self.session.revision:
                raise Superseded()

    def publish(self, key, value):
        with self.session.store.lock:
            self.check()
            self.session.data[key] = value

    def _release(self):
        if self.finished and not self.pending:
            if self.session.operations.get(self.kind) is self:
                self.session.operations.pop(self.kind)

    def finish(self):
        with self.session.store.lock:
            self.finished = True
            self._release()

    async def run(self, function, *args):
        """Cancellation stops publication, not the synchronous supplier thread.

        Keep the busy slot until the shielded thread task actually completes.
        """
        with self.session.store.lock:
            self.check()
            self.pending += 1
        task = asyncio.create_task(asyncio.to_thread(function, *args))

        def done(completed):
            # Retrieve failures even if the HTTP consumer disconnected.
            if not completed.cancelled():
                completed.exception()
            with self.session.store.lock:
                self.pending -= 1
                self._release()

        task.add_done_callback(done)
        result = await asyncio.shield(task)
        self.check()
        return result


@dataclass(eq=False)
class Session:
    store: SessionStore
    token: str
    last_seen: float
    data: dict = field(default_factory=dict)
    revision: int = 0
    operations: dict[str, Operation] = field(default_factory=dict)
    uploads: dict[str, int] = field(default_factory=dict)

    def _check(self):
        if (self.store.sessions.get(self.token) is not self
                or self.store.clock() - self.last_seen >= self.store.ttl):
            self.store.sessions.pop(self.token, None)
            self.data.clear()
            raise SessionExpired()

    def snapshot(self):
        with self.store.lock:
            self._check()
            return dict(self.data)

    def upload_ticket(self, key):
        with self.store.lock:
            self._check()
            ticket = self.uploads.get(key, 0) + 1
            self.uploads[key] = ticket
            return ticket

    def replace_input(self, key, text, ticket=None):
        with self.store.lock:
            self._check()
            if ticket is not None and self.uploads.get(key) != ticket:
                raise Superseded()
            self.revision += 1
            self.data[key] = text
            for name in RESULT_KEYS:
                self.data.pop(name, None)

    def clear(self):
        with self.store.lock:
            self._check()
            self.revision += 1
            self.data.clear()
            for key in ("jd_text", "resume_text"):
                self.uploads[key] = self.uploads.get(key, 0) + 1
            # Do not release running work: a supplier thread may still be alive.

    def begin(self, kind):
        with self.store.lock:
            self._check()
            if kind in self.operations:
                raise HTTPException(409, "同类任务仍在处理中，请等待结束后重试")
            keys = ("jd_text", "resume_text") if kind == "analysis" else ("jd", "resume", "gap")
            if any(key not in self.data for key in keys):
                detail = "请先上传职位描述 (JD) 文件和简历" if kind == "analysis" else "请先完成智能分析"
                raise HTTPException(400, detail)
            inputs = {key: self.data[key] for key in keys}
            if kind == "analysis":
                self.revision += 1
                for key in RESULT_KEYS:
                    self.data.pop(key, None)
            operation = Operation(self, kind, self.revision, inputs)
            self.operations[kind] = operation
            return operation


class SessionStore:
    def __init__(self, ttl=1800, capacity=100, clock: Callable[[], float] = time.monotonic):
        if not math.isfinite(ttl) or ttl <= 0 or capacity <= 0:
            raise ValueError("Session TTL and capacity must be positive")
        self.ttl = ttl
        self.capacity = capacity
        self.clock = clock
        self.sessions: dict[str, Session] = {}
        self.lock = threading.RLock()

    def _prune(self):
        now = self.clock()
        for token, session in list(self.sessions.items()):
            if now - session.last_seen >= self.ttl:
                self.sessions.pop(token)
                session.data.clear()

    def create(self):
        with self.lock:
            self._prune()
            if len(self.sessions) >= self.capacity:
                raise HTTPException(503, "演示会话容量已满，请稍后重试")
            token = secrets.token_urlsafe(32)
            session = Session(self, token, self.clock())
            self.sessions[token] = session
            return session

    def resolve(self, token):
        with self.lock:
            self._prune()
            session = self.sessions.get(token)
            if session is None:
                raise SessionExpired()
            session.last_seen = self.clock()
            return session
