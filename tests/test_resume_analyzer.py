# tests/test_resume_analyzer.py

import pytest
from unittest.mock import Mock
from models.schemas import ResumeInfo, WorkExperience, Project, Education
from core.analyzers.resume_analyzer import analyze_resume, MAX_RESUME_LENGTH
from core.analyzers.exceptions import ResumeAnalysisError

@pytest.fixture
def mock_llm():
    """创建一个 Mock 的 LLMService 实例"""
    return Mock()

@pytest.fixture
def sample_resume_text():
    return "张三\nPython开发工程师\n在某大厂工作了3年，负责微服务架构重构，使用FastAPI和Docker..."

def test_analyze_resume_success(mock_llm, sample_resume_text):
    # 模拟 LLM 成功返回真实的嵌套 ResumeInfo 实例 (严格对齐 Schema)
    expected_result = ResumeInfo(
        skills=["Python (Expert)", "FastAPI (Advanced)", "Docker"],
        experiences=[
            WorkExperience(
                company="某大厂",
                title="Python开发工程师",
                start_date="2021-01",
                end_date="2024-01",
                responsibilities=["负责微服务架构重构", "核心业务逻辑开发"],
                achievements=["系统性能提升30%"]
            )
        ],
        projects=[
            Project(
                name="高并发订单系统",
                description="基于FastAPI构建的高并发订单处理系统",
                technologies=["FastAPI", "Redis", "PostgreSQL"],
                role="核心开发者",
                link="https://github.com/example/order-system"
            )
        ],
        education=[
            Education(
                institution="某某大学",
                degree="本科",
                field_of_study="计算机科学与技术",
                graduation_date="2021-07",
                gpa="3.8/4.0"
            )
        ],
        summary="拥有3年Python后端开发经验，精通微服务架构。",
        certifications=["AWS Certified Developer"],
        languages=["English (Fluent)"],
        years_of_experience=3
    )
    mock_llm.call.return_value = expected_result

    # 执行测试
    result = analyze_resume(sample_resume_text, mock_llm)

    # 验证断言
    assert result == expected_result
    mock_llm.call.assert_called_once()
    assert mock_llm.call.call_args[1]["response_model"] == ResumeInfo

def test_analyze_resume_empty_or_short(mock_llm):
    # 测试空文本情况
    with pytest.raises(ResumeAnalysisError, match="简历文本为空"):
        analyze_resume("   \n  ", mock_llm)
        
    # 测试过短文本情况 (少于50字符)
    with pytest.raises(ResumeAnalysisError, match="简历内容过短"):
        analyze_resume("姓名：张三，电话：123456789。完。", mock_llm)
        
    # 确保没有调用 LLM
    mock_llm.call.assert_not_called()

def test_analyze_resume_too_long(mock_llm):
    # 测试超长文本拦截机制 (超过 MAX_RESUME_LENGTH)
    long_text = "A" * (MAX_RESUME_LENGTH + 10)
    
    with pytest.raises(ResumeAnalysisError, match="简历内容过长（超过约20页限制）"):
        analyze_resume(long_text, mock_llm)
        
    mock_llm.call.assert_not_called()

def test_analyze_resume_llm_failure(mock_llm, sample_resume_text):
    # 模拟 LLM 抛出底层异常（如 ValidationError 或 API 超时）
    mock_llm.call.side_effect = Exception("Pydantic ValidationError: missing field experiences")

    # 验证是否被成功包装为对用户友好的 ResumeAnalysisError
    with pytest.raises(ResumeAnalysisError, match="简历解析失败"):
        analyze_resume(sample_resume_text, mock_llm)