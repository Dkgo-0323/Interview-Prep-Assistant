"""Offline identity, lifecycle and deterministic interleavings; no provider calls."""
import asyncio
import json
from pathlib import Path
import threading
from types import SimpleNamespace
from unittest.mock import Mock

from fastapi import HTTPException
from fastapi.testclient import TestClient
import pytest

from api import main
from api.routes import analyze, questions, upload
from api.schemas import QuestionRequest
from api.session import COOKIE_NAME, SessionExpired, SessionStore, Superseded
from models.schemas import GapAnalysis, JDInfo, QuestionList, ResumeInfo

FIXTURES = Path(__file__).parent / "fixtures" / "workflow"


@pytest.fixture
def store(monkeypatch):
    clock = [0.0]
    store = SessionStore(ttl=30, capacity=2, clock=lambda: clock[0])
    monkeypatch.setattr(main, "session_store", store)
    return store, clock


@pytest.fixture
def service(monkeypatch):
    data = json.loads((FIXTURES / "llm_responses.json").read_text(encoding="utf-8"))
    service = Mock()
    service.call.side_effect = lambda *, response_model, **kwargs: response_model.model_validate(data[response_model.__name__])
    monkeypatch.setattr(analyze, "LLMService", lambda: service)
    monkeypatch.setattr(questions, "LLMService", lambda: service)
    return data


def seed(store, data=None):
    session = store.create()
    session.replace_input("jd_text", (FIXTURES / "jd.txt").read_text(encoding="utf-8"))
    session.replace_input("resume_text", (FIXTURES / "resume.txt").read_text(encoding="utf-8"))
    if data:
        for name, model in (("jd", JDInfo), ("resume", ResumeInfo), ("gap", GapAnalysis)):
            session.data[name] = model.model_validate(data[model.__name__])
    return session


def test_two_clients_entire_chain_is_isolated(store, service):
    with TestClient(main.app) as a, TestClient(main.app) as b:
        for client in (a, b):
            assert client.post("/api/session").status_code == 200
        assert a.cookies.get(COOKIE_NAME) != b.cookies.get(COOKIE_NAME)
        for kind in ("jd", "resume"):
            response = a.post(f"/api/upload/{kind}", files={"file": (f"{kind}.txt", (FIXTURES / f"{kind}.txt").read_bytes())})
            assert response.status_code == 200
        assert b.get("/api/upload/status").json()["ready_to_analyze"] is False
        events = a.get("/api/analyze/stream").text
        assert '"complete"' in events
        assert a.post("/api/questions/generate", json={"num_questions": 10}).status_code == 200
        assert a.get("/api/questions/cached").status_code == 200
        assert a.get("/api/analyze/result").status_code == 200
        assert a.get("/api/analyze/result").headers["cache-control"] == "no-store"
        for path in ("/api/analyze/result", "/api/questions/cached"):
            assert b.get(path).status_code == 404
        assert b.post("/api/questions/generate", json={"num_questions": 10}).status_code == 400
        b.delete("/api/upload/clear")
        assert a.get("/api/questions/cached").status_code == 200
        a.delete("/api/upload/clear")
        assert a.get("/api/questions/cached").status_code == 404


def test_cookie_bootstrap_health_and_unknown_identity(store):
    with TestClient(main.app) as client:
        assert client.get("/api/health").json() == {"status": "ok"}
        assert not client.cookies
        assert not store[0].sessions
        assert client.get("/api/upload/status").status_code == 410
        response = client.post("/api/session")
        cookie = response.headers["set-cookie"]
        assert "HttpOnly" in cookie and "SameSite=lax" in cookie
        token = client.cookies.get(COOKIE_NAME)
        assert len(token) >= 32
        assert token not in response.text
        assert client.post("/api/session").status_code == 200
        assert client.cookies.get(COOKIE_NAME) == token
        assert len(store[0].sessions) == 1
        client.cookies.set(COOKIE_NAME, "attacker-chosen-token")
        assert client.post("/api/session").status_code == 410
        assert "attacker-chosen-token" not in store[0].sessions


def test_expiry_capacity_and_restart_do_not_restore_data(store, monkeypatch):
    sessions, clock = store
    with TestClient(main.app) as a, TestClient(main.app) as b, TestClient(main.app) as c:
        assert a.post("/api/session").status_code == 200
        token = a.cookies.get(COOKIE_NAME)
        sessions.resolve(token).replace_input("jd_text", "private synthetic data")
        assert b.post("/api/session").status_code == 200
        full = c.post("/api/session")
        assert full.status_code == 503 and "容量已满" in full.json()["detail"]
        assert a.get("/api/upload/status").json()["jd_uploaded"] is True
        clock[0] = 29
        a.get("/api/upload/status")  # Sliding idle timeout.
        clock[0] = 31
        assert c.post("/api/session").status_code == 200  # B expired, A retained.
        assert a.get("/api/upload/status").json()["jd_uploaded"] is True
        clock[0] = 61
        assert a.get("/api/upload/status").status_code == 410
        assert not a.cookies.get(COOKIE_NAME)
        assert token not in sessions.sessions
        assert a.post("/api/session").status_code == 200
        assert a.get("/api/upload/status").json()["jd_uploaded"] is False
        monkeypatch.setattr(main, "session_store", SessionStore())
        assert a.get("/api/upload/status").status_code == 410


@pytest.mark.parametrize("stage", ["jd", "resume", "gap"])
@pytest.mark.parametrize("change", ["jd", "resume", "clear", "expire"])
def test_analysis_late_completion_cannot_write_back(store, service, monkeypatch, stage, change):
    sessions, clock = store
    session = seed(sessions)
    entered, release = threading.Event(), threading.Event()
    model = {"jd": JDInfo, "resume": ResumeInfo, "gap": GapAnalysis}[stage]

    def blocked(*args):
        entered.set()
        if not release.wait(5):
            raise TimeoutError("synthetic test barrier")
        return model.model_validate(service[model.__name__])

    monkeypatch.setattr(analyze, f"analyze_{stage}", blocked)

    async def scenario():
        async def consume():
            return [json.loads(item[6:]) async for item in analyze._stream_analysis(session)]
        task = asyncio.create_task(consume())
        try:
            assert await asyncio.to_thread(entered.wait, 3)
            with pytest.raises(HTTPException) as busy:
                session.begin("analysis")
            assert busy.value.status_code == 409
            if change == "clear":
                session.clear()
            elif change == "expire":
                clock[0] = 30
            else:
                session.replace_input(f"{change}_text", "new synthetic input")
        finally:
            release.set()
        events = await asyncio.wait_for(task, 3)
        assert events[-1]["step"] == "error"
        assert events[-1]["data"]["status"] == (410 if change == "expire" else 409)
        assert not any(event["step"] == "complete" for event in events)
        assert not any(key in session.data for key in ("jd", "resume", "gap", "questions"))
        assert not session.operations

    asyncio.run(scenario())


@pytest.mark.parametrize("change", ["jd", "resume", "clear", "reanalyze", "expire"])
def test_questions_late_completion_and_duplicate_request(store, service, monkeypatch, change):
    sessions, clock = store
    session = seed(sessions, service)
    entered, release = threading.Event(), threading.Event()

    def blocked(*args):
        entered.set()
        if not release.wait(5):
            raise TimeoutError("synthetic test barrier")
        return QuestionList.model_validate(service["QuestionList"])

    monkeypatch.setattr(questions, "generate_questions", blocked)

    async def scenario():
        task = asyncio.create_task(questions.generate(QuestionRequest(), session))
        try:
            assert await asyncio.to_thread(entered.wait, 3)
            with pytest.raises(HTTPException) as busy:
                await questions.generate(QuestionRequest(), session)
            assert busy.value.status_code == 409
            if change == "clear":
                session.clear()
            elif change == "expire":
                clock[0] = 30
            elif change == "reanalyze":
                session.begin("analysis").finish()
            else:
                session.replace_input(f"{change}_text", "new input")
        finally:
            release.set()
        with pytest.raises(HTTPException) as stale:
            await asyncio.wait_for(task, 3)
        assert stale.value.status_code == (410 if change == "expire" else 409)
        assert "questions" not in session.data
        assert not session.operations

    asyncio.run(scenario())


def test_cancelled_consumer_keeps_busy_until_thread_completes(store):
    session = seed(store[0])
    entered, release = threading.Event(), threading.Event()

    def blocked():
        entered.set()
        assert release.wait(5)
        return "old result"

    async def scenario():
        operation = session.begin("analysis")
        task = asyncio.create_task(operation.run(blocked))
        try:
            assert await asyncio.to_thread(entered.wait, 3)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
            operation.finish()
            with pytest.raises(HTTPException) as busy:
                session.begin("analysis")
            assert busy.value.status_code == 409
        finally:
            release.set()
        for _ in range(100):
            if not session.operations:
                break
            await asyncio.sleep(0.01)
        assert not session.operations
        with pytest.raises(Superseded):
            operation.publish("gap", "cancelled old result")
        session.begin("analysis").finish()

    asyncio.run(scenario())


@pytest.mark.parametrize("clear", [False, True])
def test_upload_started_before_newer_upload_or_clear_is_discarded(store, monkeypatch, clear):
    session = seed(store[0])

    async def scenario():
        entered, release = asyncio.Event(), asyncio.Event()

        async def parse(file):
            entered.set()
            await release.wait()
            return "old upload text"

        monkeypatch.setattr(upload, "_read_and_parse", parse)
        task = asyncio.create_task(upload.upload_jd(SimpleNamespace(filename="old.txt"), session))
        await entered.wait()
        if clear:
            session.clear()
        else:
            ticket = session.upload_ticket("jd_text")
            session.replace_input("jd_text", "newest upload", ticket)
        release.set()
        with pytest.raises(Superseded):
            await task
        assert session.snapshot().get("jd_text") == (None if clear else "newest upload")

    asyncio.run(scenario())


def test_independent_upload_tickets_and_failure_release(store, service):
    session = seed(store[0])
    jd_ticket = session.upload_ticket("jd_text")
    resume_ticket = session.upload_ticket("resume_text")
    session.replace_input("jd_text", "JD", jd_ticket)
    session.replace_input("resume_text", "resume", resume_ticket)
    assert session.snapshot()["jd_text"] == "JD"

    async def scenario():
        operation = session.begin("analysis")
        try:
            def fail():
                raise RuntimeError("synthetic failure")
            with pytest.raises(RuntimeError):
                await operation.run(fail)
        finally:
            operation.finish()
        assert not session.operations
        session.begin("analysis").finish()
    asyncio.run(scenario())


@pytest.mark.parametrize("ttl,capacity", [(0, 1), (-1, 1), (float("nan"), 1), (1, 0)])
def test_invalid_limits_fail_fast(ttl, capacity):
    with pytest.raises(ValueError):
        SessionStore(ttl=ttl, capacity=capacity)
