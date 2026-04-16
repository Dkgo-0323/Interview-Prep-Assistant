# -*- coding: utf-8 -*-
"""Tests for gap analyzer module.

Tests the gap analysis functionality including input validation,
score calculation, and error handling.
"""

import pytest
from unittest.mock import Mock
from pydantic import ValidationError

from models.schemas import JDInfo, ResumeInfo, GapAnalysis, WorkExperience, Education, Project
from services.llm_service import LLMService
from prompts.gap_analysis import GAP_SYSTEM_PROMPT  # ← 添加这个 import
from core.analyzers.gap_analyzer import (
    analyze_gap,
    _validate_inputs,
    _validate_scores,
    _calculate_overall_score
)
from core.analyzers.exceptions import GapAnalysisError


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def valid_jd():
    """Valid job description for testing."""
    return JDInfo(
        job_title="Senior Python Developer",
        company="Tech Corp",
        required_skills=["Python", "Django", "PostgreSQL"],
        nice_to_have_skills=["AWS", "Docker"],
        responsibilities=[
            "Develop backend services",
            "Design database schemas",
            "Lead technical discussions"
        ],
        experience_required="5+ years",
        education_required="Bachelor's in Computer Science",
        industry="Technology",
        seniority_level="Senior"
    )


@pytest.fixture
def valid_resume():
    """Valid resume for testing."""
    return ResumeInfo(
        skills=["Python", "Django", "PostgreSQL", "Redis"],
        experiences=[
            WorkExperience(
                company="Previous Tech",
                title="Python Developer",
                start_date="2019-01",
                end_date="2024-01",
                responsibilities=["Backend development", "API design"],
                achievements=["Improved performance by 40%"]
            )
        ],
        projects=[],  # Empty projects allowed
        education=[
            Education(
                institution="Tech University",
                degree="Bachelor of Science",
                field_of_study="Computer Science",
                graduation_date="2018-06"
            )
        ],
        years_of_experience=5
    )


@pytest.fixture
def mock_llm_service():
    """Mock LLM service that returns valid gap analysis."""
    mock = Mock(spec=LLMService)
    
    # Default return value - valid GapAnalysis without overall_match_score
    mock.call.return_value = GapAnalysis(
        matched_skills=["Python", "Django", "PostgreSQL"],
        missing_skills=["AWS", "Docker"],
        skill_score=85,
        experience_match="Candidate has 5 years, meets requirement exactly",
        experience_score=90,
        education_match="Bachelor's in CS matches requirement",
        education_score=100,
        project_relevance="No projects provided",
        project_score=0,
        strengths=["Strong Python skills", "Relevant experience"],
        weaknesses=["Missing cloud skills"],
        recommendations=["Learn AWS basics"],
        overall_match_score=0  # Will be calculated by analyzer
    )
    
    return mock


@pytest.fixture
def jd_missing_skills():
    """JD with empty required_skills."""
    return JDInfo(
        job_title="Developer",
        required_skills=[],  # Invalid: empty
        responsibilities=["Develop software"]
    )


@pytest.fixture
def jd_missing_responsibilities():
    """JD with empty responsibilities."""
    return JDInfo(
        job_title="Developer",
        required_skills=["Python"],
        responsibilities=[]  # Invalid: empty
    )


@pytest.fixture
def resume_missing_skills():
    """Resume with empty skills."""
    return ResumeInfo(
        skills=[],  # Invalid: empty
        experiences=[
            WorkExperience(
                company="Company",
                title="Developer",
                responsibilities=["Coding"]
            )
        ],
        education=[
            Education(institution="University", degree="BS")
        ]
    )


@pytest.fixture
def resume_missing_experiences():
    """Resume with empty experiences."""
    return ResumeInfo(
        skills=["Python"],
        experiences=[],  # Invalid: empty
        education=[
            Education(institution="University", degree="BS")
        ]
    )


# ============================================================================
# Test: analyze_gap() - Happy Path
# ============================================================================

def test_analyze_gap_success(valid_jd, valid_resume, mock_llm_service):
    """Test successful gap analysis with valid inputs."""
    result = analyze_gap(valid_jd, valid_resume, mock_llm_service)
    
    # Verify LLM was called
    mock_llm_service.call.assert_called_once()
    
    # Verify result structure
    assert isinstance(result, GapAnalysis)
    assert result.matched_skills == ["Python", "Django", "PostgreSQL"]
    assert result.missing_skills == ["AWS", "Docker"]
    
    # Verify individual scores
    assert result.skill_score == 85
    assert result.experience_score == 90
    assert result.education_score == 100
    assert result.project_score == 0
    
    # Verify overall score was calculated (not from LLM)
    # Expected: 85*0.4 + 90*0.3 + 100*0.2 + 0*0.1 = 81
    assert result.overall_match_score == 81


def test_analyze_gap_with_projects(valid_jd, valid_resume, mock_llm_service):
    """Test gap analysis when resume has projects."""
    # Add projects to resume
    valid_resume.projects = [
        Project(
            name="E-commerce Platform",
            description="Built with Django",
            technologies=["Python", "Django", "PostgreSQL"]
        )
    ]
    
    # Update mock to return higher project score
    mock_llm_service.call.return_value.project_score = 80
    
    result = analyze_gap(valid_jd, valid_resume, mock_llm_service)
    
    # Verify project score is included
    assert result.project_score == 80
    
    # Expected: 85*0.4 + 90*0.3 + 100*0.2 + 80*0.1 = 89
    assert result.overall_match_score == 89


def test_analyze_gap_empty_projects_allowed(valid_jd, valid_resume, mock_llm_service):
    """Test that empty projects list is allowed and doesn't cause errors."""
    valid_resume.projects = []  # Explicitly empty
    
    result = analyze_gap(valid_jd, valid_resume, mock_llm_service)
    
    # Should succeed without raising exception
    assert isinstance(result, GapAnalysis)
    assert result.project_score == 0


# ============================================================================
# Test: Input Validation
# ============================================================================

def test_validate_inputs_jd_missing_skills(jd_missing_skills, valid_resume):
    """Test validation fails when JD has no required skills."""
    with pytest.raises(GapAnalysisError) as exc_info:
        _validate_inputs(jd_missing_skills, valid_resume)
    
    assert "职位描述缺少必要的技能要求信息" in str(exc_info.value)


def test_validate_inputs_jd_missing_responsibilities(jd_missing_responsibilities, valid_resume):
    """Test validation fails when JD has no responsibilities."""
    with pytest.raises(GapAnalysisError) as exc_info:
        _validate_inputs(jd_missing_responsibilities, valid_resume)
    
    assert "职位描述缺少岗位职责信息" in str(exc_info.value)


def test_validate_inputs_resume_missing_skills(valid_jd, resume_missing_skills):
    """Test validation fails when resume has no skills."""
    with pytest.raises(GapAnalysisError) as exc_info:
        _validate_inputs(valid_jd, resume_missing_skills)
    
    # 修改后（使用部分匹配避免乱码）：
    assert "简历中未找到" in str(exc_info.value)
    assert "技能信息" in str(exc_info.value)


def test_analyze_gap_input_validation_integration(jd_missing_skills, valid_resume, mock_llm_service):
    """Test that analyze_gap properly validates inputs and raises user-friendly errors."""
    with pytest.raises(GapAnalysisError) as exc_info:
        analyze_gap(jd_missing_skills, valid_resume, mock_llm_service)
    
    # Should raise validation error with user-friendly message
    assert "职位描述缺少必要的技能要求信息" in str(exc_info.value)
    
    # LLM should NOT have been called
    mock_llm_service.call.assert_not_called()


# ============================================================================
# Test: Score Validation
# ============================================================================

def test_validate_scores_success():
    """Test score validation passes with valid scores."""
    valid_result = GapAnalysis(
        matched_skills=["Python"],
        missing_skills=["AWS"],
        skill_score=80,
        experience_match="Good match",
        experience_score=75,
        education_match="Meets requirements",
        education_score=90,
        project_relevance="Relevant",
        project_score=70,
        strengths=["Strong skills"],
        weaknesses=["Some gaps"],
        recommendations=["Learn AWS"],
        overall_match_score=0  # Not validated here
    )
    
    # Should not raise any exception
    _validate_scores(valid_result)


def test_validate_scores_skill_score_too_high():
    """
    Test that Pydantic prevents creating GapAnalysis with invalid scores.
    
    This demonstrates our "double insurance" design - Pydantic is the first line of defense,
    and _validate_scores() provides redundant safety.
    """
    with pytest.raises(ValidationError) as exc_info:
        GapAnalysis(
            matched_skills=["Python"],
            missing_skills=[],
            skill_score=120,  # Invalid: > 100, Pydantic will catch this
            experience_match="Good",
            experience_score=80,
            education_match="Good",
            education_score=90,
            project_relevance="Good",
            project_score=75,
            strengths=["Strong"],
            weaknesses=["None"],
            recommendations=["Keep it up"],
            overall_match_score=0
        )
    
    # Verify Pydantic caught the invalid score
    assert "skill_score" in str(exc_info.value)


def test_validate_scores_experience_score_negative():
    """
    Test that Pydantic prevents negative scores at model creation.
    """
    with pytest.raises(ValidationError) as exc_info:
        GapAnalysis(
            matched_skills=["Python"],
            missing_skills=[],
            skill_score=80,
            experience_match="Poor",
            experience_score=-10,  # Invalid: < 0, Pydantic will catch this
            education_match="Good",
            education_score=90,
            project_relevance="Good",
            project_score=75,
            strengths=["Some"],
            weaknesses=["Experience"],
            recommendations=["Gain experience"],
            overall_match_score=0
        )
    
    # Verify Pydantic caught the invalid score
    assert "experience_score" in str(exc_info.value)


def test_validate_scores_redundant_check():
    """
    Test our redundant _validate_scores() function with manually created invalid object.
    
    This simulates a scenario where somehow an invalid score bypasses Pydantic
    (e.g., through direct attribute assignment after creation).
    """
    # Create valid object first
    result = GapAnalysis(
        matched_skills=["Python"],
        missing_skills=[],
        skill_score=80,
        experience_match="Good",
        experience_score=75,
        education_match="Good",
        education_score=90,
        project_relevance="Good",
        project_score=70,
        strengths=["Strong"],
        weaknesses=["None"],
        recommendations=["Keep going"],
        overall_match_score=0
    )
    
    # Bypass Pydantic validation by direct assignment (for testing only)
    result.skill_score = 150
    
    # Our redundant validation should catch it
    with pytest.raises(GapAnalysisError) as exc_info:
        _validate_scores(result)
    
    assert "技能匹配度评分超出有效范围" in str(exc_info.value)


def test_analyze_gap_invalid_score_from_llm(valid_jd, valid_resume, mock_llm_service):
    """
    Test that if LLM returns invalid data, it's caught and wrapped properly.
    
    We simulate this by making the mock raise a generic Exception,
    since Pydantic ValidationError construction in tests is complex.
    """
    # Mock LLM to raise a generic exception (simulating LLM returning invalid data)
    mock_llm_service.call.side_effect = Exception("LLM returned invalid score format")
    
    with pytest.raises(GapAnalysisError) as exc_info:
        analyze_gap(valid_jd, valid_resume, mock_llm_service)
    
    # Should be wrapped in user-friendly message
    assert "无法完成岗位匹配度分析" in str(exc_info.value)
    
    # Original error should be preserved
    assert "LLM returned invalid score format" in str(exc_info.value.__cause__)


# ============================================================================
# Test: Overall Score Calculation
# ============================================================================

def test_calculate_overall_score_balanced():
    """Test overall score calculation with balanced scores."""
    # All scores = 80
    # Expected: 80*0.4 + 80*0.3 + 80*0.2 + 80*0.1 = 80
    score = _calculate_overall_score(
        skill_score=80,
        experience_score=80,
        education_score=80,
        project_score=80
    )
    assert score == 80


def test_calculate_overall_score_skill_weighted():
    """Test that skill score has highest weight (40%)."""
    # Skills: 100, others: 0
    # Expected: 100*0.4 + 0*0.3 + 0*0.2 + 0*0.1 = 40
    score = _calculate_overall_score(
        skill_score=100,
        experience_score=0,
        education_score=0,
        project_score=0
    )
    assert score == 40


def test_calculate_overall_score_rounding():
    """Test that overall score is properly rounded."""
    # 85*0.4 + 72*0.3 + 91*0.2 + 63*0.1 = 80.1
    # Should round to 80
    score = _calculate_overall_score(
        skill_score=85,
        experience_score=72,
        education_score=91,
        project_score=63
    )
    assert score == 80


def test_calculate_overall_score_rounding_up():
    """
    Test rounding behavior with a score that clearly rounds up.
    
    90*0.4 + 85*0.3 + 75*0.2 + 80*0.1 = 84.5
    Python's round(84.5) = 84 (banker's rounding)
    
    To get a clear round-up case: 85*0.4 + 86*0.3 + 90*0.2 + 81*0.1 = 85.9 → 86
    """
    score = _calculate_overall_score(
        skill_score=85,
        experience_score=86,
        education_score=90,
        project_score=81
    )
    assert score == 86  # 85.9 rounds to 86


def test_calculate_overall_score_edge_case_all_zero():
    """Test calculation when all scores are zero."""
    score = _calculate_overall_score(
        skill_score=0,
        experience_score=0,
        education_score=0,
        project_score=0
    )
    assert score == 0


def test_calculate_overall_score_edge_case_all_perfect():
    """Test calculation when all scores are perfect."""
    score = _calculate_overall_score(
        skill_score=100,
        experience_score=100,
        education_score=100,
        project_score=100
    )
    assert score == 100


# ============================================================================
# Test: Error Handling
# ============================================================================

def test_analyze_gap_llm_call_fails(valid_jd, valid_resume, mock_llm_service):
    """Test that LLM failures are wrapped in user-friendly errors."""
    # Mock LLM raises exception
    mock_llm_service.call.side_effect = Exception("OpenAI API timeout")
    
    with pytest.raises(GapAnalysisError) as exc_info:
        analyze_gap(valid_jd, valid_resume, mock_llm_service)
    
    # User-friendly message
    assert "无法完成岗位匹配度分析" in str(exc_info.value)
    assert "请稍后重试或联系技术支持" in str(exc_info.value)
    
    # Original error is preserved in __cause__
    assert exc_info.value.__cause__ is not None
    assert "OpenAI API timeout" in str(exc_info.value.__cause__)


def test_analyze_gap_pydantic_validation_fails(valid_jd, valid_resume, mock_llm_service):
    """Test that Pydantic validation errors are wrapped properly."""
    # Mock LLM raises a generic exception (simulating validation failure)
    mock_llm_service.call.side_effect = Exception("Validation failed")
    
    with pytest.raises(GapAnalysisError) as exc_info:
        analyze_gap(valid_jd, valid_resume, mock_llm_service)
    
    # Should show user-friendly message
    assert "无法完成岗位匹配度分析" in str(exc_info.value)


def test_analyze_gap_preserves_own_exceptions(valid_jd, valid_resume, mock_llm_service):
    """Test that GapAnalysisError from validation is not double-wrapped."""
    # This should raise GapAnalysisError from _validate_inputs
    jd_invalid = JDInfo(
        job_title="Dev",
        required_skills=[],  # Invalid
        responsibilities=["Work"]
    )
    
    with pytest.raises(GapAnalysisError) as exc_info:
        analyze_gap(jd_invalid, valid_resume, mock_llm_service)
    
    # Should be the original validation error, not wrapped
    assert "职位描述缺少必要的技能要求信息" in str(exc_info.value)
    
    # Should NOT have the generic "无法完成岗位匹配度分析" wrapper
    assert "请稍后重试" not in str(exc_info.value)


# ============================================================================
# Test: Integration Scenarios
# ============================================================================

def test_analyze_gap_full_workflow(valid_jd, valid_resume, mock_llm_service):
    """Test complete gap analysis workflow end-to-end."""
    # Setup mock to return realistic data
    mock_llm_service.call.return_value = GapAnalysis(
        matched_skills=["Python", "Django", "PostgreSQL"],
        missing_skills=["AWS", "Docker"],
        skill_score=75,
        experience_match="5 years matches requirement",
        experience_score=85,
        education_match="Bachelor's meets requirement",
        education_score=100,
        project_relevance="No projects to evaluate",
        project_score=50,
        strengths=[
            "Strong backend development skills",
            "Relevant database experience",
            "Meets education requirements"
        ],
        weaknesses=[
            "Missing cloud platform experience",
            "No containerization skills"
        ],
        recommendations=[
            "Complete AWS certification",
            "Build Docker-based projects",
            "Gain cloud deployment experience"
        ],
        overall_match_score=0  # Will be calculated
    )
    
    result = analyze_gap(valid_jd, valid_resume, mock_llm_service)
    
    # Verify all components
    assert len(result.matched_skills) == 3
    assert len(result.missing_skills) == 2
    assert len(result.strengths) == 3
    assert len(result.weaknesses) == 2
    assert len(result.recommendations) == 3
    
    # Verify score calculation
    # 75*0.4 + 85*0.3 + 100*0.2 + 50*0.1 = 80.5 → rounds to 80
    assert result.overall_match_score == 80
    
    # Verify LLM was called with correct parameters
    call_args = mock_llm_service.call.call_args
    assert call_args.kwargs["response_model"] == GapAnalysis
    assert call_args.kwargs["system_prompt"] == GAP_SYSTEM_PROMPT


# ============================================================================
# Test: Fresh Graduate Scenarios (Empty Experiences)
# ============================================================================

def test_validate_inputs_resume_empty_experiences_allowed(valid_jd):
    """Test that empty experiences list is allowed (fresh graduate scenario)."""
    resume_fresh_grad = ResumeInfo(
        skills=["Python", "Django"],
        experiences=[],  # Empty - fresh graduate
        projects=[
            Project(
                name="E-commerce Platform",
                description="Built with Django",
                technologies=["Python", "Django"]
            )
        ],
        education=[
            Education(
                institution="University",
                degree="Bachelor of Science",
                field_of_study="Computer Science",
                graduation_date="2024-06"
            )
        ]
    )
    
    # Should NOT raise any exception
    _validate_inputs(valid_jd, resume_fresh_grad)


def test_analyze_gap_fresh_graduate(valid_jd, mock_llm_service):
    """
    Test gap analysis for fresh graduate with no work experience.
    
    This is an integration test validating the complete workflow
    for a fresh graduate candidate.
    """
    # Fresh graduate resume
    fresh_grad_resume = ResumeInfo(
        skills=["Python", "Django", "PostgreSQL"],
        experiences=[],  # No work experience
        projects=[
            Project(
                name="Student Management System",
                description="Full-stack web application for managing student records",
                technologies=["Python", "Django", "PostgreSQL", "React"]
            ),
            Project(
                name="ML Image Classifier",
                description="Built CNN model for image classification",
                technologies=["Python", "TensorFlow", "Keras"]
            )
        ],
        education=[
            Education(
                institution="UC Berkeley",
                degree="Bachelor of Science",
                field_of_study="Computer Science",
                graduation_date="2024-05",
                gpa="3.9/4.0"
            )
        ],
        certifications=["AWS Cloud Practitioner"],
        years_of_experience=0
    )
    
    # Mock LLM to return appropriate analysis for fresh graduate
    mock_llm_service.call.return_value = GapAnalysis(
        matched_skills=["Python", "Django", "PostgreSQL"],
        missing_skills=["AWS", "Docker"],
        skill_score=75,
        experience_match="应届毕业生，无正式工作经验。基于项目经历评估，候选人有2个相关项目，展示了较强的技术能力。",
        experience_score=25,  # Low but not zero - projects show potential
        education_match="计算机科学本科学历符合要求，GPA优秀(3.9/4.0)",
        education_score=90,
        project_relevance="学生管理系统项目使用了JD要求的核心技术栈(Python, Django, PostgreSQL)，展示了全栈开发能力",
        project_score=80,
        strengths=[
            "扎实的计算机科学理论基础",
            "项目经验展示了良好的技术能力",
            "优秀的学术成绩(GPA 3.9)",
            "已有AWS认证，展现了学习能力"
        ],
        weaknesses=[
            "缺乏正式工作经验",
            "缺少微服务架构实践",
            "未参与过大规模系统开发"
        ],
        recommendations=[
            "积累实习经验，了解企业级开发流程",
            "深入学习微服务架构和容器化技术",
            "参与开源项目，积累团队协作经验",
            "构建更多个人项目展示技术深度"
        ],
        overall_match_score=0  # Will be calculated
    )
    
    # Execute gap analysis
    result = analyze_gap(valid_jd, fresh_grad_resume, mock_llm_service)
    
    # Verify result structure
    assert isinstance(result, GapAnalysis)
    assert len(result.matched_skills) == 3
    assert len(result.missing_skills) == 2
    
    # Verify scores for fresh graduate scenario
    assert result.skill_score == 75
    assert result.experience_score == 25  # Low but evaluated
    assert result.education_score == 90
    assert result.project_score == 80
    
    # Verify overall score calculation
    # 75*0.4 + 25*0.3 + 90*0.2 + 80*0.1 = 63.5 → 64
    assert result.overall_match_score == 64
    
    # Verify strengths and weaknesses are appropriate
    assert any("工作经验" in w for w in result.weaknesses)
    assert any("实习" in r for r in result.recommendations)


def test_analyze_gap_fresh_graduate_entry_level_jd(mock_llm_service):
    """
    Test gap analysis for fresh graduate applying to entry-level position.
    
    Expected: Higher experience score since JD expectations are lower.
    """
    # Entry-level JD
    entry_level_jd = JDInfo(
        job_title="Junior Python Developer",
        company="Startup Inc",
        required_skills=["Python", "Django"],
        nice_to_have_skills=["AWS"],
        responsibilities=[
            "Develop backend features",
            "Write clean code",
            "Learn and grow with the team"
        ],
        experience_required="0-1 years",
        education_required="Bachelor's in CS or related",
        seniority_level="Junior"
    )
    
    # Fresh graduate resume
    fresh_grad_resume = ResumeInfo(
        skills=["Python", "Django", "PostgreSQL"],
        experiences=[],
        projects=[
            Project(
                name="Portfolio Website",
                description="Personal website built with Django",
                technologies=["Python", "Django"]
            )
        ],
        education=[
            Education(
                institution="State University",
                degree="Bachelor of Science",
                field_of_study="Computer Science",
                graduation_date="2024-05"
            )
        ],
        years_of_experience=0
    )
    
    # Mock LLM response for entry-level position
    mock_llm_service.call.return_value = GapAnalysis(
        matched_skills=["Python", "Django"],
        missing_skills=["AWS"],
        skill_score=80,
        experience_match="应届毕业生，符合初级岗位要求(0-1年)。项目经验展示了基础技术能力。",
        experience_score=50,  # Higher score for entry-level
        education_match="计算机科学本科学历完全符合要求",
        education_score=100,
        project_relevance="个人网站项目展示了基本的Django开发能力",
        project_score=70,
        strengths=[
            "掌握岗位要求的核心技能",
            "教育背景完全符合",
            "适合初级岗位的成长潜力"
        ],
        weaknesses=[
            "缺少云平台经验",
            "项目复杂度较低"
        ],
        recommendations=[
            "学习AWS基础服务",
            "参与更多复杂项目开发"
        ],
        overall_match_score=0
    )
    
    result = analyze_gap(entry_level_jd, fresh_grad_resume, mock_llm_service)
    
    # Verify appropriate scoring for entry-level position
    assert result.experience_score == 50  # Higher than senior position
    assert "应届毕业生" in result.experience_match
    
    # Overall score should be higher
    # 80*0.4 + 50*0.3 + 100*0.2 + 70*0.1 = 74
    assert result.overall_match_score == 74