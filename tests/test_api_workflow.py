"""Offline API integration: real routes/parsers/business logic, mocked LLM only."""
import json
from pathlib import Path
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from api.main import app, get_session
from api.routes import analyze, questions
from models.schemas import GapAnalysis, JDInfo, QuestionList, ResumeInfo

FIXTURES = Path(__file__).parent / "fixtures" / "workflow"
STEPS = ["jd_start", "jd_done", "resume_start", "resume_done", "gap_start", "complete"]


@pytest.fixture
def client():
    get_session().clear()
    with TestClient(app) as test_client:
        yield test_client
    get_session().clear()


@pytest.fixture
def llm(monkeypatch):
    responses = json.loads((FIXTURES / "llm_responses.json").read_text(encoding="utf-8"))
    service = Mock()
    service.call.side_effect = lambda *, response_model, **kwargs: response_model.model_validate(
        responses[response_model.__name__]
    )
    factory = Mock(return_value=service)
    monkeypatch.setattr(analyze, "LLMService", factory)
    monkeypatch.setattr(questions, "LLMService", factory)
    return service


def upload(client, kind):
    content = (FIXTURES / f"{kind}.txt").read_bytes()
    response = client.post(f"/api/upload/{kind}", files={"file": (f"{kind}.txt", content, "text/plain")})
    assert response.status_code == 200
    assert response.json()["char_count"] == len(content.decode("utf-8").strip())


def events(client):
    with client.stream("GET", "/api/analyze/stream") as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        return [json.loads(line[6:]) for line in response.iter_lines() if line.startswith("data: ")]


def complete(client):
    upload(client, "jd")
    upload(client, "resume")
    result = events(client)
    assert [event["step"] for event in result] == STEPS
    return result[-1]["data"]


def test_missing_resume_is_terminal_error(client, llm):
    upload(client, "jd")
    result = events(client)
    assert [event["step"] for event in result] == ["error"]
    assert "简历" in result[0]["message"]
    llm.call.assert_not_called()


def test_full_workflow_and_cached_recovery(client, llm):
    report = complete(client)
    assert report["overall_match_score"] == 77  # Real weighted calculation, mock returns 0.
    assert client.get("/api/analyze/result").json() == {"success": True, "data": report}
    response = client.post("/api/questions/generate", json={"num_questions": 10})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["total"] == len(body["questions"]) == 10
    assert all(question["reference_answer"] for question in body["questions"])
    assert client.get("/api/questions/cached").json() == body
    assert [call.kwargs["response_model"] for call in llm.call.call_args_list] == [
        JDInfo, ResumeInfo, GapAnalysis, QuestionList,
    ]
    assert "示例智能" in llm.call.call_args_list[0].kwargs["prompt"]
    assert "候选人甲" in llm.call.call_args_list[1].kwargs["prompt"]


def test_uploaded_but_not_analyzed_rejects_questions(client, llm):
    upload(client, "jd")
    upload(client, "resume")
    response = client.post("/api/questions/generate", json={"num_questions": 10})
    assert response.status_code == 400
    assert "请先完成智能分析" in response.json()["detail"]
    assert client.get("/api/analyze/result").status_code == 404
    assert client.get("/api/questions/cached").status_code == 404
    llm.call.assert_not_called()


@pytest.mark.parametrize("failure_model,expected_steps", [
    (JDInfo, ["jd_start", "error"]),
    (ResumeInfo, STEPS[:3] + ["error"]),
    (GapAnalysis, STEPS[:5] + ["error"]),
])
def test_failed_reanalysis_cannot_recover_old_success(client, llm, failure_model, expected_steps):
    complete(client)
    assert client.post("/api/questions/generate", json={"num_questions": 10}).status_code == 200
    original = llm.call.side_effect

    def fail(**kwargs):
        if kwargs["response_model"] is failure_model:
            raise RuntimeError("synthetic provider failure")
        return original(**kwargs)

    llm.call.side_effect = fail
    result = events(client)
    assert [event["step"] for event in result] == expected_steps
    assert client.get("/api/analyze/result").status_code == 404
    assert client.get("/api/questions/cached").status_code == 404
    assert client.post("/api/questions/generate", json={"num_questions": 10}).status_code == 400


@pytest.mark.parametrize("kind", ["jd", "resume"])
def test_reupload_invalidates_results(client, llm, kind):
    complete(client)
    assert client.post("/api/questions/generate", json={"num_questions": 10}).status_code == 200
    upload(client, kind)
    assert client.get("/api/analyze/result").status_code == 404
    assert client.get("/api/questions/cached").status_code == 404
    assert client.post("/api/questions/generate", json={"num_questions": 10}).status_code == 400


def test_initialization_failure_is_terminal_error(client, llm, monkeypatch):
    upload(client, "jd")
    upload(client, "resume")
    monkeypatch.setattr(analyze, "LLMService", Mock(side_effect=RuntimeError("synthetic init failure")))
    assert [event["step"] for event in events(client)] == ["error"]
    assert client.get("/api/analyze/result").status_code == 404
    llm.call.assert_not_called()
