"""Opt-in Qwen connectivity diagnostic.

The comprehensive real-provider acceptance suite lives in
``tests/test_qwen_integration.py``. This small check remains for developers who
want a quick text-only connection probe.
"""

import os

import pytest

import config
from services.llm_service import LLMService


pytestmark = pytest.mark.qwen_integration


def test_connection():
    if os.getenv("RUN_QWEN_INTEGRATION") != "1":
        pytest.skip("Set RUN_QWEN_INTEGRATION=1 to call the real Qwen provider")

    assert config.DASHSCOPE_API_KEY, "DASHSCOPE_API_KEY is required"
    assert config.LLM_BASE_URL, "LLM_BASE_URL or DASHSCOPE_BASE_URL is required"
    assert config.LLM_DEFAULT_MODEL == "qwen3.7-plus"

    result = LLMService(max_tokens=32).call_simple(
        prompt="Reply with exactly: Connection Successful",
        temperature=0.0,
    )
    assert "Connection Successful" in result
