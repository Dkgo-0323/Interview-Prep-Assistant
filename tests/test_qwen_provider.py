"""Offline contract tests for the Qwen provider adapter."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel

import config
from services.llm_service import LLMService, LLMServiceError
from utils.token_counter import estimate_cost


class StructuredResult(BaseModel):
    value: str


@pytest.fixture
def qwen_config(monkeypatch):
    monkeypatch.setattr(config, "DASHSCOPE_API_KEY", "test-key")
    monkeypatch.setattr(
        config,
        "LLM_BASE_URL",
        "https://workspace.example.com/compatible-mode/v1",
    )
    monkeypatch.setattr(config, "LLM_DEFAULT_MODEL", "qwen3.7-plus")
    monkeypatch.setattr(config, "MODEL_NAME", "qwen3.7-plus")
    monkeypatch.setattr(config, "LLM_PROVIDER", "qwen")
    monkeypatch.setattr(config, "LLM_ENABLE_THINKING", False)


def _usage(prompt_tokens=10, completion_tokens=5):
    return SimpleNamespace(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
    )


def test_initializes_openai_compatible_client(monkeypatch, qwen_config):
    client = MagicMock()
    constructor = MagicMock(return_value=client)
    monkeypatch.setattr("services.llm_service.OpenAI", constructor)

    service = LLMService()

    assert service.model == "qwen3.7-plus"
    constructor.assert_called_once_with(
        api_key="test-key",
        base_url="https://workspace.example.com/compatible-mode/v1",
        max_retries=3,
        timeout=config.LLM_TIMEOUT_SECONDS,
    )


def test_structured_call_uses_parse_without_token_limit(monkeypatch, qwen_config):
    parsed = StructuredResult(value="ok")
    client = MagicMock()
    client.chat.completions.parse.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(parsed=parsed))],
        usage=_usage(),
    )
    monkeypatch.setattr("services.llm_service.OpenAI", MagicMock(return_value=client))

    result = LLMService().call(
        prompt="Return a structured result",
        response_model=StructuredResult,
        max_tokens=14_000,
    )

    assert result == parsed
    kwargs = client.chat.completions.parse.call_args.kwargs
    assert kwargs["model"] == "qwen3.7-plus"
    assert kwargs["response_format"] is StructuredResult
    assert kwargs["extra_body"] == {"enable_thinking": False}
    assert "max_tokens" not in kwargs
    assert "max_completion_tokens" not in kwargs


def test_simple_call_uses_completion_token_limit(monkeypatch, qwen_config):
    client = MagicMock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))],
        usage=_usage(),
    )
    monkeypatch.setattr("services.llm_service.OpenAI", MagicMock(return_value=client))

    result = LLMService(max_tokens=321).call_simple(prompt="hello")

    assert result == "ok"
    assert client.chat.completions.create.call_args.kwargs["max_completion_tokens"] == 321
    assert client.chat.completions.create.call_args.kwargs["extra_body"] == {
        "enable_thinking": False
    }


def test_missing_qwen_configuration_fails_before_request(monkeypatch, qwen_config):
    monkeypatch.setattr(config, "DASHSCOPE_API_KEY", None)
    with pytest.raises(LLMServiceError, match="DASHSCOPE_API_KEY"):
        LLMService()

    monkeypatch.setattr(config, "DASHSCOPE_API_KEY", "test-key")
    monkeypatch.setattr(config, "LLM_BASE_URL", None)
    with pytest.raises(LLMServiceError, match="LLM_BASE_URL"):
        LLMService()


def test_unknown_model_cost_is_not_faked():
    assert estimate_cost(1_000, "unknown-provider-model", "input") is None
