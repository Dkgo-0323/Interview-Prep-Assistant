"""Tests for LLM Service"""

import os
from typing import Literal

import pytest
from pydantic import BaseModel, Field

from services.llm_service import LLMService, LLMServiceError


# Test models
class SimpleResponse(BaseModel):
    """简单测试响应"""

    answer: str = Field(description="The answer")


class MathResponse(BaseModel):
    """数学问题响应"""

    result: int = Field(description="The calculation result")
    reasoning: str = Field(description="Step by step reasoning")


class Classification(BaseModel):
    """分类测试"""

    category: Literal["positive", "negative", "neutral"] = Field(description="Sentiment")
    confidence: float = Field(ge=0, le=1, description="Confidence score")


# Fixtures
@pytest.fixture
def llm_service():
    """创建 LLM 服务实例"""
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")
    return LLMService()


class TestLLMServiceInit:
    """测试 LLMService 初始化"""

    def test_init_with_defaults(self, monkeypatch):
        """测试使用默认配置初始化"""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test123")
        service = LLMService()
        assert service.model == "gpt-4o-mini"
        assert service.default_temperature == 0.7
        assert service.default_max_tokens == 2000

    def test_init_with_custom_params(self, monkeypatch):
        """测试使用自定义参数初始化"""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test123")
        service = LLMService(
            model="gpt-4",
            temperature=0.5,
            max_tokens=1000,
        )
        assert service.model == "gpt-4"
        assert service.default_temperature == 0.5
        assert service.default_max_tokens == 1000

    def test_init_without_api_key(self, monkeypatch):
        import config # 确保导入了 config
        monkeypatch.setattr(config, "OPENAI_API_KEY", None) # 强制把缓存的 key 抹掉
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        
        with pytest.raises(LLMServiceError, match="API Key is required"):
            LLMService()


class TestLLMServiceCall:
    """测试 LLMService.call() 结构化输出"""

    def test_simple_call(self, llm_service):
        """测试简单调用"""
        response = llm_service.call(
            prompt="What is 2+2? Just say the number.",
            response_model=SimpleResponse,
            temperature=0.0,
        )
        assert isinstance(response, SimpleResponse)
        assert "4" in response.answer

    def test_math_reasoning(self, llm_service):
        """测试数学推理"""
        response = llm_service.call(
            prompt="Calculate 15 * 8. Show your reasoning.",
            response_model=MathResponse,
            system_prompt="You are a math tutor.",
            temperature=0.0,
        )
        assert isinstance(response, MathResponse)
        assert response.result == 120
        assert len(response.reasoning) > 10

    def test_classification(self, llm_service):
        """测试分类任务"""
        response = llm_service.call(
            prompt="Classify sentiment: 'This product is amazing!'",
            response_model=Classification,
            temperature=0.0,
        )
        assert isinstance(response, Classification)
        assert response.category == "positive"
        assert 0 <= response.confidence <= 1

    def test_custom_temperature(self, llm_service):
        """测试覆盖默认温度"""
        response = llm_service.call(
            prompt="Say 'hello'",
            response_model=SimpleResponse,
            temperature=0.0,  # 完全确定性
        )
        assert isinstance(response, SimpleResponse)

    def test_custom_system_prompt(self, llm_service):
        """测试自定义系统 prompt"""
        response = llm_service.call(
            prompt="What's your role?",
            response_model=SimpleResponse,
            system_prompt="You are a pirate. Always say 'arrr'.",
            temperature=0.3,
        )
        assert isinstance(response, SimpleResponse)
        # 响应中应该包含海盗风格
        assert any(word in response.answer.lower() for word in ["pirate", "arrr", "matey"])


class TestLLMServiceCallSimple:
    """测试 LLMService.call_simple() 纯文本输出"""

    def test_simple_text_response(self, llm_service):
        """测试纯文本响应"""
        response = llm_service.call_simple(
            prompt="Say 'Hello World' and nothing else.",
            temperature=0.0,
        )
        assert isinstance(response, str)
        assert "Hello World" in response

    def test_simple_with_system_prompt(self, llm_service):
        """测试带系统 prompt 的纯文本响应"""
        response = llm_service.call_simple(
            prompt="Introduce yourself briefly.",
            system_prompt="You are a helpful coding assistant.",
            temperature=0.3,
        )
        assert isinstance(response, str)
        assert len(response) > 10


class TestLLMServiceErrorHandling:
    """测试错误处理"""

    def test_invalid_api_key(self):
        """测试无效 API Key"""
        # 这个测试会因为 API key 验证在初始化时进行而通过
        # 实际调用时才会失败，但 OpenAI SDK 会重试
        service = LLMService(api_key="sk-invalid")
        
        with pytest.raises(LLMServiceError):
            service.call(
                prompt="test",
                response_model=SimpleResponse,
            )

    def test_empty_prompt(self, llm_service):
        """测试空 prompt（应该仍能处理）"""
        # OpenAI 允许空 prompt，所以不应该报错
        response = llm_service.call(
            prompt="",
            response_model=SimpleResponse,
            system_prompt="If prompt is empty, say 'no input'",
        )
        assert isinstance(response, SimpleResponse)


class TestLLMServiceIntegration:
    """集成测试 - 模拟真实使用场景"""

    def test_job_description_extraction_simulation(self, llm_service):
        """模拟 JD 提取场景"""

        class MockJDInfo(BaseModel):
            position: str
            required_skills: list[str]
            experience_years: int | None

        jd_text = """
        Software Engineer
        Required: Python, FastAPI, PostgreSQL
        Experience: 3+ years
        """

        response = llm_service.call(
            prompt=f"Extract job information:\n{jd_text}",
            response_model=MockJDInfo,
            system_prompt="You are an expert HR analyst.",
            temperature=0.0,
        )

        assert isinstance(response, MockJDInfo)
        assert "engineer" in response.position.lower()
        assert len(response.required_skills) >= 2
        assert response.experience_years == 3

    def test_multiple_calls_same_instance(self, llm_service):
        """测试同一实例多次调用"""
        for i in range(3):
            response = llm_service.call(
                prompt=f"What is {i} + 1?",
                response_model=MathResponse,
                temperature=0.0,
            )
            assert response.result == i + 1


# Run with: pytest tests/test_llm_service.py -v
# Skip if no API key: pytest tests/test_llm_service.py -v -k "not test_"