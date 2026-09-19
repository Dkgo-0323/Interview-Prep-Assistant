r"""Real Qwen integration and API workflow acceptance tests.

These tests use only synthetic fixtures. They are opt-in because they make real
provider calls and incur API usage:

    $env:RUN_QWEN_INTEGRATION = "1"
    venv\Scripts\python.exe -m pytest -m qwen_integration -v -s
"""

import json
import os

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel

import config
from api.main import app, get_session
from models.schemas import GapAnalysis, JDInfo, Question, ResumeInfo
from services.llm_service import LLMService


pytestmark = pytest.mark.qwen_integration

if os.getenv("RUN_QWEN_INTEGRATION") != "1":
    pytest.skip(
        "Set RUN_QWEN_INTEGRATION=1 to run real Qwen integration tests",
        allow_module_level=True,
    )


SYNTHETIC_JD = """
Senior Backend Engineer
Company: Example Technology
Required skills: Python, FastAPI, PostgreSQL, Docker, REST API design
Nice to have: Kubernetes, Redis
Responsibilities:
- Design and maintain reliable backend APIs
- Review code and improve service performance
- Collaborate with product and frontend teams
Experience: 3+ years of backend development
Education: Bachelor's degree in computer science or equivalent experience
""".strip()

SYNTHETIC_RESUME = """
Candidate: Zhang San
Summary: Backend engineer with four years of experience building web services.
Skills: Python, FastAPI, PostgreSQL, Docker, Redis, Git
Experience:
- Backend Engineer, Example Software, 2022-01 to Present
  - Built REST APIs with Python and FastAPI.
  - Optimized PostgreSQL queries and reduced average latency by 30%.
  - Containerized services with Docker and participated in code reviews.
Projects:
- Interview Preparation Platform
  - Developed a FastAPI backend and PostgreSQL data layer.
  - Used Docker for local development and deployment.
Education:
- Bachelor of Computer Science, Example University, 2021
""".strip()


class ProviderProbe(BaseModel):
    provider: str
    structured_output_ok: bool


def _assert_real_qwen_configuration() -> None:
    assert config.DASHSCOPE_API_KEY, "DASHSCOPE_API_KEY is required"
    assert config.LLM_BASE_URL, "LLM_BASE_URL or DASHSCOPE_BASE_URL is required"
    assert config.LLM_DEFAULT_MODEL == "qwen3.7-plus"
    for variable_name in (
        "LLM_MODEL_JD_EXTRACTION",
        "LLM_MODEL_RESUME_EXTRACTION",
        "LLM_MODEL_GAP_ANALYSIS",
        "LLM_MODEL_QUESTION_GENERATION",
    ):
        configured_model = os.getenv(variable_name)
        if configured_model:
            assert configured_model == "qwen3.7-plus", variable_name


def _parse_sse_events(response) -> list[dict]:
    events = []
    for line in response.iter_lines():
        if line.startswith("data: "):
            events.append(json.loads(line.removeprefix("data: ")))
    return events


@pytest.fixture(scope="module")
def analyzed_application():
    _assert_real_qwen_configuration()
    client = TestClient(app)
    client.delete("/api/upload/clear")

    jd_upload = client.post(
        "/api/upload/jd",
        files={"file": ("synthetic-jd.txt", SYNTHETIC_JD.encode(), "text/plain")},
    )
    resume_upload = client.post(
        "/api/upload/resume",
        files={
            "file": (
                "synthetic-resume.txt",
                SYNTHETIC_RESUME.encode(),
                "text/plain",
            )
        },
    )
    assert jd_upload.status_code == 200
    assert resume_upload.status_code == 200

    with client.stream("GET", "/api/analyze/stream") as response:
        assert response.status_code == 200
        events = _parse_sse_events(response)

    error_events = [event for event in events if event.get("step") == "error"]
    assert not error_events, error_events
    assert events[-1]["step"] == "complete"

    yield client, events, get_session()

    client.delete("/api/upload/clear")


def test_qwen_pydantic_structured_output_three_times():
    """Prove that the real endpoint supports SDK-generated JSON Schema."""
    _assert_real_qwen_configuration()
    llm = LLMService()

    for _ in range(3):
        result = llm.call(
            prompt=(
                "Return provider='qwen' and structured_output_ok=true. "
                "Do not add facts or commentary."
            ),
            response_model=ProviderProbe,
            temperature=0.0,
        )
        assert result.provider.lower() == "qwen"
        assert result.structured_output_ok is True


def test_real_qwen_analysis_chain_preserves_business_contract(analyzed_application):
    _, events, session = analyzed_application

    assert [event["step"] for event in events] == [
        "jd_start",
        "jd_done",
        "resume_start",
        "resume_done",
        "gap_start",
        "complete",
    ]
    assert isinstance(session["jd"], JDInfo)
    assert isinstance(session["resume"], ResumeInfo)
    assert isinstance(session["gap"], GapAnalysis)
    assert session["jd"].required_skills
    assert session["jd"].responsibilities
    assert session["resume"].skills

    gap = session["gap"]
    expected_score = round(
        gap.skill_score * 0.40
        + gap.experience_score * 0.30
        + gap.education_score * 0.20
        + gap.project_score * 0.10
    )
    assert gap.overall_match_score == expected_score


@pytest.mark.parametrize("num_questions", [10, 15])
def test_real_qwen_question_generation_preserves_contract(
    analyzed_application,
    num_questions,
):
    client, _, _ = analyzed_application

    response = client.post(
        "/api/questions/generate",
        json={"num_questions": num_questions},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["total"] == num_questions
    assert len(payload["questions"]) == num_questions

    questions = [Question.model_validate(item) for item in payload["questions"]]
    assert all(question.reference_answer.strip() for question in questions)
    normalized = [question.question_text.strip().casefold() for question in questions]
    assert len(normalized) == len(set(normalized))
