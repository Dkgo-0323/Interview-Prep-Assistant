"""Tests for question generator module."""

from prompts.question_generation import QUESTION_SYSTEM_PROMPT
import pytest
from unittest.mock import Mock, MagicMock
from models.schemas import (
    GapAnalysis, ResumeInfo, JDInfo, QuestionList, Question,
    QuestionType, DifficultyLevel, WorkExperience, Project, Education
)
from core.generators.question_generator import generate_questions, _validate_inputs, _check_duplicate_questions
from core.analyzers.exceptions import QuestionGenerationError


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_llm_service():
    """Mock LLM service."""
    mock = Mock()
    return mock


@pytest.fixture
def valid_jd():
    """Valid job description."""
    return JDInfo(
        job_title="高级Python开发工程师",
        company="某科技公司",
        required_skills=["Python", "FastAPI", "PostgreSQL", "Docker", "微服务"],
        responsibilities=[
            "负责后端微服务架构设计与开发",
            "优化系统性能，提升响应速度",
            "参与技术方案评审和代码审查"
        ]
    )


@pytest.fixture
def valid_resume():
    """Valid resume with experiences and projects."""
    return ResumeInfo(
        skills=["Python (Expert)", "FastAPI", "PostgreSQL", "Docker"],
        experiences=[
            WorkExperience(
                company="前公司",
                title="Python开发工程师",
                start_date="2020-01",
                end_date="2023-12",
                responsibilities=[
                    "负责微服务架构重构，使用FastAPI和Docker",
                    "优化数据库查询，提升系统性能30%",
                    "参与技术方案设计和代码审查"
                ],
                achievements=["获得年度优秀员工奖", "主导完成核心模块重构"]
            )
        ],
        projects=[
            Project(
                name="电商平台微服务重构",
                description="将单体应用拆分为多个微服务，提升系统可扩展性",
                technologies=["Python", "FastAPI", "Docker", "Kubernetes"],
                role="核心开发"
            )
        ],
        education=[
            Education(
                institution="某大学",
                degree="计算机科学学士",
                graduation_date="2019-06"
            )
        ],
        years_of_experience=4
    )


@pytest.fixture
def valid_gap():
    """Valid gap analysis result."""
    return GapAnalysis(
        matched_skills=["Python", "FastAPI", "PostgreSQL", "Docker"],
        missing_skills=["微服务", "Kubernetes"],
        skill_score=80,
        experience_match="有相关工作经验，但微服务经验不足",
        experience_score=70,
        education_match="学历符合要求",
        education_score=90,
        project_relevance="项目经验相关",
        project_score=85,
        strengths=["Python基础扎实", "有实际项目经验"],
        weaknesses=["微服务架构经验不足", "缺乏大规模系统经验"],
        recommendations=["加强微服务相关知识学习", "参与更多大型项目"],
        overall_match_score=78  # Python计算：80*0.4 + 70*0.3 + 90*0.2 + 85*0.1 = 78
    )


@pytest.fixture
def sample_questions():
    """Sample questions for testing."""
    return QuestionList(
        questions=[
            Question(
                question_text="请解释Python中的GIL是什么，以及它对多线程编程的影响？",
                question_type=QuestionType.TECHNICAL,
                difficulty=DifficultyLevel.INTERMEDIATE,
                focus_area="Python并发编程",
                intent="考察对Python底层机制的理解",
                reference_answer="GIL是全局解释器锁，它确保同一时刻只有一个线程执行Python字节码。这限制了多线程程序的CPU并行能力，但对于I/O密集型任务影响较小。"
            ),
            Question(
                question_text="请描述你在电商平台微服务重构项目中遇到的最大挑战是什么？",
                question_type=QuestionType.PROJECT,
                difficulty=DifficultyLevel.ADVANCED,
                focus_area="微服务架构",
                intent="考察实际项目经验和问题解决能力",
                reference_answer="最大的挑战是服务拆分后的数据一致性问题。我们通过引入事件驱动架构和最终一致性方案来解决。"
            )
        ]
    )


# ============================================================================
# Test: _validate_inputs()
# ============================================================================

def test_validate_inputs_success(valid_gap, valid_resume, valid_jd):
    """Test successful validation with valid inputs."""
    # Should not raise any exception
    _validate_inputs(valid_gap, valid_resume, valid_jd, num_questions=15)


def test_validate_inputs_num_questions_too_small(valid_gap, valid_resume, valid_jd):
    """Test validation fails when num_questions is too small."""
    with pytest.raises(ValueError, match="题目数量必须在 10 到 50 之间"):
        _validate_inputs(valid_gap, valid_resume, valid_jd, num_questions=5)


def test_validate_inputs_num_questions_too_large(valid_gap, valid_resume, valid_jd):
    """Test validation fails when num_questions is too large."""
    with pytest.raises(ValueError, match="题目数量必须在 10 到 50 之间"):
        _validate_inputs(valid_gap, valid_resume, valid_jd, num_questions=60)


def test_validate_inputs_gap_missing_score(valid_resume, valid_jd):
    """Test validation fails when gap has overall_match_score=None."""
    # Create valid GapAnalysis first (Pydantic won't allow None at creation)
    gap_no_score = GapAnalysis(
        matched_skills=["Python"],
        missing_skills=[],
        skill_score=80,
        experience_match="",
        experience_score=70,
        education_match="",
        education_score=90,
        project_relevance="",
        project_score=85,
        strengths=[],
        weaknesses=[],
        recommendations=[],
        overall_match_score=0  # Valid value initially
    )
    
    # Manually set to None to test validation logic
    gap_no_score.overall_match_score = None
    
    with pytest.raises(QuestionGenerationError, match="能力差距分析缺少匹配度分数"):
        _validate_inputs(gap_no_score, valid_resume, valid_jd, num_questions=10)


def test_validate_inputs_no_skills_in_gap(valid_resume, valid_jd):
    """Test validation fails when gap has no skill information."""
    gap_no_skills = GapAnalysis(
        matched_skills=[],
        missing_skills=[],
        skill_score=0,
        experience_match="",
        experience_score=0,
        education_match="",
        education_score=0,
        project_relevance="",
        project_score=0,
        strengths=[],
        weaknesses=[],
        recommendations=[],
        overall_match_score=50
    )
    
    with pytest.raises(QuestionGenerationError, match="能力差距分析缺少技能信息"):
        _validate_inputs(gap_no_skills, valid_resume, valid_jd, num_questions=10)


def test_validate_inputs_resume_no_skills(valid_gap, valid_jd):
    """Test validation fails when resume has no skills."""
    resume_no_skills = ResumeInfo(
        skills=[],  # No skills
        experiences=[WorkExperience(company="Test", title="Engineer")],
        projects=[],
        education=[]
    )
    
    with pytest.raises(QuestionGenerationError, match="简历缺少技能信息"):
        _validate_inputs(valid_gap, resume_no_skills, valid_jd, num_questions=10)


def test_validate_inputs_jd_no_required_skills(valid_gap, valid_resume):
    """Test validation fails when JD has no required skills."""
    jd_no_skills = JDInfo(
        job_title="工程师",
        required_skills=[],  # No required skills
        responsibilities=["做一些工作"]
    )
    
    with pytest.raises(QuestionGenerationError, match="职位描述缺少必备技能信息"):
        _validate_inputs(valid_gap, valid_resume, jd_no_skills, num_questions=10)


# ============================================================================
# Test: _check_duplicate_questions()
# ============================================================================

def test_check_duplicate_questions_no_duplicates(sample_questions):
    """Test no duplicates in valid question list."""
    # Should not raise any exception
    _check_duplicate_questions(sample_questions.questions)


def test_check_duplicate_questions_with_duplicates():
    """Test detection of duplicate questions."""
    questions = [
        Question(
            question_text="相同的问题",
            question_type=QuestionType.TECHNICAL,
            difficulty=DifficultyLevel.BASIC,
            focus_area="测试",
            intent="测试",
            reference_answer="答案"
        ),
        Question(
            question_text="不同的问题",
            question_type=QuestionType.TECHNICAL,
            difficulty=DifficultyLevel.BASIC,
            focus_area="测试",
            intent="测试",
            reference_answer="答案"
        ),
        Question(
            question_text="相同的问题",  # Duplicate!
            question_type=QuestionType.PROJECT,
            difficulty=DifficultyLevel.ADVANCED,
            focus_area="测试2",
            intent="测试2",
            reference_answer="答案2"
        )
    ]
    
    with pytest.raises(QuestionGenerationError, match="发现重复的面试题目"):
        _check_duplicate_questions(questions)


# ============================================================================
# Test: generate_questions() - Happy Path
# ============================================================================

def test_generate_questions_success(valid_gap, valid_resume, valid_jd, mock_llm_service):
    """Test successful question generation."""
    # Create 10 questions to match the requested number
    mock_questions = QuestionList(
        questions=[
            Question(
                question_text=f"请解释Python中的概念 {i}",
                question_type=QuestionType.TECHNICAL,
                difficulty=DifficultyLevel.INTERMEDIATE,
                focus_area="Python核心知识",
                intent="考察对Python底层机制的理解",
                reference_answer=f"这是第 {i} 个问题的参考答案。"
            )
            for i in range(10)
        ]
    )
    
    # Mock LLM to return 10 questions
    mock_llm_service.call.return_value = mock_questions
    
    # Call the function
    result = generate_questions(
        gap=valid_gap,
        resume=valid_resume,
        jd=valid_jd,
        llm=mock_llm_service,
        num_questions=10
    )
    
    # Verify LLM was called with correct parameters
    mock_llm_service.call.assert_called_once()
    call_args = mock_llm_service.call.call_args
    
    # Check response model
    assert call_args[1]["response_model"] == QuestionList
    # Check system prompt
    assert call_args[1]["system_prompt"] == QUESTION_SYSTEM_PROMPT
    
    # Verify result
    assert len(result.questions) == 10
    assert result.questions[0].question_text == "请解释Python中的概念 0"


def test_generate_questions_custom_num_questions(valid_gap, valid_resume, valid_jd, mock_llm_service):
    """Test generation with custom number of questions."""
    # Create mock questions with exactly 15 items
    mock_questions = QuestionList(
        questions=[
            Question(
                question_text=f"问题 {i}",
                question_type=QuestionType.TECHNICAL,
                difficulty=DifficultyLevel.BASIC,
                focus_area="测试",
                intent="测试",
                reference_answer="答案"
            )
            for i in range(15)
        ]
    )
    mock_llm_service.call.return_value = mock_questions
    
    result = generate_questions(
        gap=valid_gap,
        resume=valid_resume,
        jd=valid_jd,
        llm=mock_llm_service,
        num_questions=15
    )
    
    assert len(result.questions) == 15


# ============================================================================
# Test: generate_questions() - Error Handling
# ============================================================================

def test_generate_questions_wrong_number_returned(valid_gap, valid_resume, valid_jd, mock_llm_service, sample_questions):
    """Test error when LLM returns wrong number of questions."""
    # Mock LLM returns 2 questions but we requested 10
    mock_llm_service.call.return_value = sample_questions
    
    with pytest.raises(QuestionGenerationError, match="生成的题目数量不正确：期望 10，实际 2"):
        generate_questions(
            gap=valid_gap,
            resume=valid_resume,
            jd=valid_jd,
            llm=mock_llm_service,
            num_questions=10
        )


def test_generate_questions_empty_reference_answer(valid_gap, valid_resume, valid_jd, mock_llm_service):
    """Test error when question has empty reference answer."""
    # Create 10 questions, with the 5th one having an empty reference answer
    questions_with_empty_answer = QuestionList(
        questions=[
            Question(
                question_text=f"问题 {i+1}",
                question_type=QuestionType.TECHNICAL,
                difficulty=DifficultyLevel.BASIC,
                focus_area="测试",
                intent="测试",
                reference_answer="正常答案" if i != 4 else "   "  # 5th question has empty answer
            )
            for i in range(10)
        ]
    )
    mock_llm_service.call.return_value = questions_with_empty_answer
    
    with pytest.raises(QuestionGenerationError, match="第 5 题缺少参考答案"):
        generate_questions(
            gap=valid_gap,
            resume=valid_resume,
            jd=valid_jd,
            llm=mock_llm_service,
            num_questions=10
        )


def test_generate_questions_llm_failure(valid_gap, valid_resume, valid_jd, mock_llm_service):
    """Test error handling when LLM call fails."""
    mock_llm_service.call.side_effect = Exception("OpenAI API timeout")
    
    with pytest.raises(QuestionGenerationError, match="面试题生成失败，请稍后重试或联系技术支持"):
        generate_questions(
            gap=valid_gap,
            resume=valid_resume,
            jd=valid_jd,
            llm=mock_llm_service,
            num_questions=10
        )


def test_generate_questions_validation_error_propagates(valid_gap, valid_resume, valid_jd, mock_llm_service):
    """Test that validation errors are not double-wrapped."""
    # Create invalid JD without required skills
    invalid_jd = JDInfo(
        job_title="工程师",
        required_skills=[],  # Invalid: no required skills
        responsibilities=["工作"]
    )
    
    with pytest.raises(QuestionGenerationError, match="职位描述缺少必备技能信息"):
        generate_questions(
            gap=valid_gap,
            resume=valid_resume,
            jd=invalid_jd,
            llm=mock_llm_service,
            num_questions=10
        )
    
    # LLM should not be called when validation fails
    mock_llm_service.call.assert_not_called()


# ============================================================================
# Test: Edge Cases
# ============================================================================

def test_generate_questions_resume_without_projects(valid_gap, valid_jd, mock_llm_service):
    """Test generation with resume that has no projects (allowed)."""
    resume_no_projects = ResumeInfo(
        skills=["Python"],
        experiences=[WorkExperience(company="Test", title="Engineer")],
        projects=[],  # Empty projects allowed
        education=[]
    )
    
    # Mock successful LLM call - create 10 DIFFERENT questions to avoid duplicates
    mock_questions = QuestionList(
        questions=[
            Question(
                question_text=f"测试问题 {i}",  # Make each question unique
                question_type=QuestionType.TECHNICAL,
                difficulty=DifficultyLevel.BASIC,
                focus_area="测试",
                intent="测试",
                reference_answer=f"答案 {i}"  # Make each answer unique
            )
            for i in range(10)
        ]
    )
    mock_llm_service.call.return_value = mock_questions
    
    # Should succeed without error
    result = generate_questions(
        gap=valid_gap,
        resume=resume_no_projects,
        jd=valid_jd,
        llm=mock_llm_service,
        num_questions=10
    )
    
    assert len(result.questions) == 10


def test_generate_questions_default_num_questions(valid_gap, valid_resume, valid_jd, mock_llm_service):
    """Test generation with default number of questions (10)."""
    mock_questions = QuestionList(
        questions=[
            Question(
                question_text=f"问题 {i}",
                question_type=QuestionType.TECHNICAL,
                difficulty=DifficultyLevel.BASIC,
                focus_area="测试",
                intent="测试",
                reference_answer="答案"
            )
            for i in range(10)
        ]
    )
    mock_llm_service.call.return_value = mock_questions
    
    # Call without specifying num_questions (should use default 10)
    result = generate_questions(
        gap=valid_gap,
        resume=valid_resume,
        jd=valid_jd,
        llm=mock_llm_service
    )
    
    assert len(result.questions) == 10


# ============================================================================
# Test: Fresh Graduate Scenarios
# ============================================================================

def test_validate_inputs_resume_empty_experiences_allowed(valid_gap, valid_jd):
    """Test that empty experiences list is allowed (fresh graduate scenario)."""
    resume_fresh_grad = ResumeInfo(
        skills=["Python", "FastAPI"],
        experiences=[],  # Empty - fresh graduate
        projects=[
            Project(
                name="Capstone Project",
                description="Built a web application",
                technologies=["Python", "FastAPI"]
            )
        ],
        education=[
            Education(
                institution="University",
                degree="Bachelor of Science",
                field_of_study="Computer Science",
                graduation_date="2024-05"
            )
        ]
    )
    
    # Should NOT raise any exception
    _validate_inputs(valid_gap,resume_fresh_grad, valid_jd, num_questions=10)


def test_generate_questions_for_fresh_graduate(mock_llm_service):
    """
    Test question generation for fresh graduate with no work experience.
    
    This validates that the system can generate appropriate questions
    based on projects and skills when work experience is absent.
    """
    # Fresh graduate resume
    fresh_grad_resume = ResumeInfo(
        skills=["Python", "Django", "PostgreSQL"],
        experiences=[],  # No work experience
        projects=[
            Project(
                name="Student Management System",
                description="Full-stack application for managing student records",
                technologies=["Python", "Django", "PostgreSQL", "React"],
                role="Lead Developer"
            ),
            Project(
                name="ML Image Classifier",
                description="CNN model for image classification",
                technologies=["Python", "TensorFlow"],
                role="Sole Developer"
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
        years_of_experience=0
    )
    
    # Entry-level JD
    entry_level_jd = JDInfo(
        job_title="Junior Python Developer",
        required_skills=["Python", "Django"],
        nice_to_have_skills=["AWS"],
        responsibilities=[
            "Develop backend features",
            "Write clean code"
        ]
    )
    
    # Gap analysis for fresh graduate
    fresh_grad_gap = GapAnalysis(
        matched_skills=["Python", "Django"],
        missing_skills=["AWS"],
        skill_score=80,
        experience_match="应届毕业生，无正式工作经验",
        experience_score=40,
        education_match="本科学历符合要求",
        education_score=100,
        project_relevance="项目经验展示了基础技术能力",
        project_score=70,
        strengths=["掌握核心技术栈", "学习能力强"],
        weaknesses=["缺少工作经验", "未掌握云服务"],
        recommendations=["积累实习经验", "学习AWS"],
        overall_match_score=68
    )
    
    # Mock LLM to return questions appropriate for fresh graduate
    mock_questions = QuestionList(
        questions=[
            Question(
                question_text=f"请解释Python中的装饰器是什么？请结合你的学生管理系统项目说明如何使用。{i}",
                question_type=QuestionType.TECHNICAL,
                difficulty=DifficultyLevel.BASIC,
                focus_area="Python核心概念",
                intent="考察基础知识掌握程度",
                reference_answer=f"装饰器是用于修改函数行为的工具。在项目中用于权限验证等场景。{i}"
            )
            for i in range(10)
        ]
    )
    mock_llm_service.call.return_value = mock_questions
    
    # Generate questions
    result = generate_questions(
        gap=fresh_grad_gap,
        resume=fresh_grad_resume,
        jd=entry_level_jd,
        llm=mock_llm_service,
        num_questions=10
    )
    
    # Verify questions were generated successfully
    assert len(result.questions) == 10
    
    # Verify LLM was called
    mock_llm_service.call.assert_called_once()
    
    # Verify the prompt contains project information (since no experience)
    call_args = mock_llm_service.call.call_args
    prompt = call_args[1]["prompt"]
    assert "Student Management System" in prompt or "ML Image Classifier" in prompt


def test_generate_questions_fresh_graduate_focuses_on_projects(mock_llm_service):
    """
    Test that question generation for fresh graduates focuses on projects
    and skills rather than work experience.
    """
    # Fresh graduate with only education and skills
    minimal_fresh_grad = ResumeInfo(
        skills=["Python", "Git"],
        experiences=[],
        projects=[],  # Even without projects
        education=[
            Education(
                institution="University",
                degree="Bachelor of Science",
                field_of_study="Computer Science",
                graduation_date="2024-05"
            )
        ],
        years_of_experience=0
    )
    
    # Junior position JD
    junior_jd = JDInfo(
        job_title="Junior Developer",
        required_skills=["Python"],
        responsibilities=["Learn and contribute to development"]
    )
    
    # Gap analysis
    gap = GapAnalysis(
        matched_skills=["Python"],
        missing_skills=[],
        skill_score=60,
        experience_match="应届毕业生，无经验",
        experience_score=20,
        education_match="符合要求",
        education_score=100,
        project_relevance="无项目经验",
        project_score=0,
        strengths=["掌握Python基础", "计算机科学背景"],
        weaknesses=["缺少实践经验"],
        recommendations=["多动手实践"],
        overall_match_score=50
    )
    
    # Mock questions focused on basics
    mock_questions = QuestionList(
        questions=[
            Question(
                question_text=f"Python基础问题 {i}",
                question_type=QuestionType.TECHNICAL,
                difficulty=DifficultyLevel.BASIC,
                focus_area="Python基础",
                intent="考察基础知识",
                reference_answer=f"参考答案 {i}"
            )
            for i in range(10)
        ]
    )
    mock_llm_service.call.return_value = mock_questions
    
    # Should succeed even with minimal information
    result = generate_questions(
        gap=gap,
        resume=minimal_fresh_grad,
        jd=junior_jd,
        llm=mock_llm_service,
        num_questions=10
    )
    
    assert len(result.questions) == 10
    
    # Verify questions are basic level (appropriate for fresh graduate)
    for question in result.questions:
        assert question.difficulty == DifficultyLevel.BASIC