# tests/test_jd_analyzer.py

import pytest
from unittest.mock import Mock
from models.schemas import JDInfo
from core.analyzers.jd_analyzer import analyze_jd
from core.analyzers.exceptions import JDAnalysisError

@pytest.fixture
def mock_llm():
    """创建一个 Mock 的 LLMService 实例"""
    return Mock()

@pytest.fixture
def sample_jd_text():
    return "我们需要一名高级Python开发工程师，熟练掌握FastAPI和PostgreSQL，5年以上后端开发经验..."

def test_analyze_jd_success(mock_llm, sample_jd_text):
    # 模拟 LLM 成功返回真实的 JDInfo 实例 (严格对齐你的 Schema)
    expected_result = JDInfo(
        job_title="高级Python开发工程师",
        company="某科技公司",
        required_skills=["Python", "FastAPI", "PostgreSQL"],
        nice_to_have_skills=["Docker", "Kubernetes"],
        responsibilities=["负责后端核心业务逻辑开发", "优化系统性能"],
        experience_required="5年以上",
        education_required="本科及以上",
        industry="互联网",
        seniority_level="高级"
    )
    # mock_llm.call 返回这个实例
    mock_llm.call.return_value = expected_result

    # 执行测试
    result = analyze_jd(sample_jd_text, mock_llm)

    # 验证断言
    assert result == expected_result
    mock_llm.call.assert_called_once()
    assert mock_llm.call.call_args[1]["response_model"] == JDInfo

def test_analyze_jd_empty_text(mock_llm):
    # 测试空文本情况
    with pytest.raises(JDAnalysisError, match="文本为空"):
        analyze_jd("   ", mock_llm)
        
    # 测试过短文本情况
    with pytest.raises(JDAnalysisError, match="文本过短"):
        analyze_jd("太短了", mock_llm)
        
    # 确保没有调用 LLM
    mock_llm.call.assert_not_called()

def test_analyze_jd_llm_failure(mock_llm, sample_jd_text):
    # 模拟 LLM 抛出底层异常（如网络超时）
    mock_llm.call.side_effect = Exception("OpenAI API Connection Timeout")

    # 验证是否被成功包装为友好的 JDAnalysisError
    with pytest.raises(JDAnalysisError, match="职位描述\\(JD\\)分析失败"):
        analyze_jd(sample_jd_text, mock_llm)