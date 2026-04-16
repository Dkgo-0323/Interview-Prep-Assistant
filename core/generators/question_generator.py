"""Question generator module.

Generates personalized interview questions based on gap analysis,
resume information, and job description requirements.
"""

from typing import List
from models.schemas import GapAnalysis, ResumeInfo, JDInfo, QuestionList, Question
from services.llm_service import LLMService
from prompts.question_generation import QUESTION_SYSTEM_PROMPT, get_question_generation_prompt
from core.analyzers.exceptions import QuestionGenerationError


def generate_questions(
    gap: GapAnalysis,
    resume: ResumeInfo,
    jd: JDInfo,
    llm: LLMService,
    num_questions: int = 10
) -> QuestionList:
    """
    根据能力差距分析、简历和职位要求生成个性化面试题。
    
    Args:
        gap: 能力差距分析结果
        resume: 候选人简历信息
        jd: 职位描述信息
        llm: LLM 服务实例
        num_questions: 生成的题目数量 (10-50，默认10)
        
    Returns:
        QuestionList 对象，包含指定数量的面试题
        
    Raises:
        QuestionGenerationError: 题目生成失败
        ValueError: num_questions 超出有效范围
        
    Example:
        >>> gap = analyze_gap(jd, resume, llm)
        >>> questions = generate_questions(gap, resume, jd, llm, num_questions=15)
        >>> print(len(questions.questions))  # 15
        >>> print(questions.questions[0].question_text)
    """
    # 1. 输入验证
    _validate_inputs(gap, resume, jd, num_questions)
    
    try:
        # 2. 生成 Prompt
        prompt = get_question_generation_prompt(gap, resume, jd, num_questions)
        
        # 3. 调用 LLM
        result: QuestionList = llm.call(
            prompt=prompt,
            response_model=QuestionList,
            system_prompt=QUESTION_SYSTEM_PROMPT
        )
        
        # 4. 验证返回结果
        if len(result.questions) != num_questions:
            raise QuestionGenerationError(
                f"生成的题目数量不正确：期望 {num_questions}，实际 {len(result.questions)}"
            )
        
        # 5. 检查重复题目
        _check_duplicate_questions(result.questions)
        
        # 6. 验证每个题目的必填字段
        for i, question in enumerate(result.questions):
            if not question.reference_answer.strip():
                raise QuestionGenerationError(
                    f"第 {i+1} 题缺少参考答案"
                )
        
        return result
        
    except QuestionGenerationError:
        # 重新抛出我们自己的异常
        raise
    except Exception as e:
        # 包装其他异常
        raise QuestionGenerationError(
            "面试题生成失败，请稍后重试或联系技术支持"
        ) from e


def _validate_inputs(
    gap: GapAnalysis,
    resume: ResumeInfo,
    jd: JDInfo,
    num_questions: int
) -> None:
    """
    验证输入参数的有效性。
    
    Raises:
        QuestionGenerationError: 如果输入不满足生成条件
        ValueError: 如果 num_questions 超出范围
    """
    # 1. 题目数量范围检查
    if not (10 <= num_questions <= 50):
        raise ValueError("题目数量必须在 10 到 50 之间")
    
    # 2. GapAnalysis 必须包含 overall_match_score
    if gap.overall_match_score is None:
        raise QuestionGenerationError("能力差距分析缺少匹配度分数")
    
    # 3. 必须有缺失技能或匹配技能（至少一个）
    if not gap.missing_skills and not gap.matched_skills:
        raise QuestionGenerationError("能力差距分析缺少技能信息")
    
    # 4. 简历必须有技能信息
    if not resume.skills:
        raise QuestionGenerationError("简历缺少技能信息")
    
    # 5. JD 必须有必备技能
    if not jd.required_skills:
        raise QuestionGenerationError("职位描述缺少必备技能信息")


def _check_duplicate_questions(questions: List[Question]) -> None:
    """
    检查是否有完全相同的题目文本。
    
    Args:
        questions: 题目列表
        
    Raises:
        QuestionGenerationError: 如果发现完全相同的题目
    """
    seen_texts = set()
    for question in questions:
        if question.question_text in seen_texts:
            raise QuestionGenerationError("发现重复的面试题目")
        seen_texts.add(question.question_text)


# 导出函数
__all__ = ["generate_questions"]