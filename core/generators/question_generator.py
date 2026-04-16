"""Question generator module.

Generates personalized interview questions based on gap analysis,
resume information, and job description requirements.
"""

from typing import List, Dict, Optional, Tuple
from models.schemas import GapAnalysis, ResumeInfo, JDInfo, QuestionList, Question
from services.llm_service import LLMService
from prompts.question_generation import QUESTION_SYSTEM_PROMPT, get_question_generation_prompt
from core.analyzers.exceptions import QuestionGenerationError
from utils.logger import get_logger

logger = get_logger(__name__)

# 分批生成的阈值
BATCH_THRESHOLD = 15
# 每批次的最大题目数
BATCH_SIZE = 15


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
    
    logger.info(f"开始生成 {num_questions} 道面试题")
    
    # 2. 根据题目数量选择生成策略
    if num_questions <= BATCH_THRESHOLD:
        # 直接生成（单批次）
        logger.info(f"题目数量 {num_questions} <= {BATCH_THRESHOLD}，采用单批次生成策略")
        return _generate_single_batch(gap, resume, jd, llm, num_questions)
    else:
        # 分批生成
        logger.info(f"题目数量 {num_questions} > {BATCH_THRESHOLD}，采用分批生成策略")
        return _generate_in_batches(gap, resume, jd, llm, num_questions)


def _generate_single_batch(
    gap: GapAnalysis,
    resume: ResumeInfo,
    jd: JDInfo,
    llm: LLMService,
    num_questions: int,
    batch_info: Optional[Dict] = None
) -> QuestionList:
    """
    单批次生成题目（核心生成逻辑）。
    
    Args:
        gap: 能力差距分析结果
        resume: 候选人简历信息
        jd: 职位描述信息
        llm: LLM 服务实例
        num_questions: 本次批次需要生成的题目数量
        batch_info: 分批信息（可选）
            - batch_number: 当前批次号
            - total_batches: 总批次数
            - existing_questions: 已生成的题目列表
        
    Returns:
        QuestionList 对象
    """
    try:
        # 1. 动态计算 max_tokens
        base_tokens = 1500  # prompt + system prompt 的基础消耗
        tokens_per_question = 240  # 每题约 200 tokens + 20% 缓冲
        required_max_tokens = base_tokens + (num_questions * tokens_per_question)
        max_tokens = min(required_max_tokens, 14000)  # GPT-4o-mini 输出上限为 16384，留余量
        
        logger.debug(f"动态计算 max_tokens: {max_tokens} (base={base_tokens}, questions={num_questions})")
        
        # 2. 生成 Prompt
        prompt = get_question_generation_prompt(gap, resume, jd, num_questions, batch_info)
        
        # 3. 调用 LLM
        result: QuestionList = llm.call(
            prompt=prompt,
            response_model=QuestionList,
            system_prompt=QUESTION_SYSTEM_PROMPT,
            max_tokens=max_tokens
        )
        
        # 4. 验证返回结果
        if len(result.questions) != num_questions:
            error_msg = f"生成的题目数量不正确：期望 {num_questions}，实际 {len(result.questions)}"
            logger.error(error_msg)
            raise QuestionGenerationError(error_msg)
        
        # 5. 检查重复题目
        _check_duplicate_questions(result.questions)
        
        # 6. 验证每个题目的必填字段
        _validate_reference_answers(result.questions)
        
        logger.info(f"单批次生成成功，共 {len(result.questions)} 道题目")
        return result
        
    except QuestionGenerationError:
        # 重新抛出我们自己的异常
        raise
    except Exception as e:
        # 包装其他异常
        logger.error(f"题目生成异常: {str(e)}", exc_info=True)
        raise QuestionGenerationError(
            "面试题生成失败，请稍后重试或联系技术支持"
        ) from e


def _generate_in_batches(
    gap: GapAnalysis,
    resume: ResumeInfo,
    jd: JDInfo,
    llm: LLMService,
    total_questions: int
) -> QuestionList:
    """
    分批生成题目并合并结果。
    
    Args:
        gap: 能力差距分析结果
        resume: 候选人简历信息
        jd: 职位描述信息
        llm: LLM 服务实例
        total_questions: 总题目数量
        
    Returns:
        QuestionList 对象，包含所有批次的题目
    """
    # 1. 计算分批策略
    batches = _calculate_batches(total_questions, BATCH_SIZE)
    logger.info(f"分批策略: {len(batches)} 批次，每批最多 {BATCH_SIZE} 题")
    
    all_questions: List[Question] = []
    
    # 2. 逐批生成
    for batch_idx, (batch_number, batch_count) in enumerate(batches):
        logger.info(f"正在生成第 {batch_number}/{len(batches)} 批，本批 {batch_count} 题")
        
        # 构建批次信息（传递已生成的题目，避免重复）
        batch_info = {
            "batch_number": batch_number,
            "total_batches": len(batches),
            "existing_questions": all_questions
        }
        
        try:
            # 生成当前批次
            batch_result = _generate_single_batch(
                gap, resume, jd, llm, batch_count, batch_info
            )
            
            # 检查跨批次重复（双重保险）
            duplicates_found = 0
            for question in batch_result.questions:
                if _is_duplicate_question(question, all_questions):
                    logger.warning(
                        f"发现跨批次重复题目，跳过: {question.question_text[:50]}..."
                    )
                    duplicates_found += 1
                    continue
                all_questions.append(question)
            
            if duplicates_found > 0:
                logger.warning(f"第 {batch_number} 批发现 {duplicates_found} 个重复题目")
            
            logger.info(
                f"第 {batch_number} 批完成，累计 {len(all_questions)}/{total_questions} 题"
            )
            
        except QuestionGenerationError as e:
            logger.error(f"第 {batch_number} 批生成失败: {str(e)}")
            
            # 如果是最后一批且失败，尝试降低要求继续
            if batch_number == len(batches):
                logger.warning("最后一批生成失败，尝试补充生成")
                # 可以在这里添加补救逻辑
                # 但为了简单，我们直接抛出异常
            raise
    
    # 3. 最终验证
    if len(all_questions) < total_questions:
        error_msg = (
            f"分批生成后题目数量不足：期望 {total_questions}，"
            f"实际 {len(all_questions)}"
        )
        logger.error(error_msg)
        raise QuestionGenerationError(error_msg)
    
    # 4. 返回结果（截断到精确数量，以防万一）
    final_questions = all_questions[:total_questions]
    logger.info(f"✅ 分批生成完成，共 {len(final_questions)} 道题目")
    
    return QuestionList(questions=final_questions)


def _calculate_batches(total: int, batch_size: int) -> List[Tuple[int, int]]:
    """
    计算分批策略。
    
    Args:
        total: 总题目数
        batch_size: 每批次最大题目数
        
    Returns:
        List of (batch_number, batch_count) tuples
    """
    batches = []
    remaining = total
    batch_number = 1
    
    while remaining > 0:
        current_batch_size = min(batch_size, remaining)
        batches.append((batch_number, current_batch_size))
        remaining -= current_batch_size
        batch_number += 1
    
    return batches


def _is_duplicate_question(question: Question, existing: List[Question]) -> bool:
    """
    检查题目是否与已有题目重复。
    
    Args:
        question: 待检查的题目
        existing: 已有题目列表
        
    Returns:
        True 如果重复，False 如果不重复
    """
    # 完全相同的文本
    for existing_q in existing:
        if question.question_text == existing_q.question_text:
            return True
        
        # 高度相似检查（可选，防止换个问法）
        # 简单实现：如果前 50 个字符相同，视为重复
        if (len(question.question_text) > 50 and 
            question.question_text[:50] == existing_q.question_text[:50]):
            return True
    
    return False


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


def _validate_reference_answers(questions: List[Question]) -> None:
    """
    验证每个题目的参考答案。
    
    Args:
        questions: 题目列表
        
    Raises:
        QuestionGenerationError: 如果发现缺少参考答案
    """
    for i, question in enumerate(questions):
        if not question.reference_answer or not question.reference_answer.strip():
            raise QuestionGenerationError(
                f"第 {i+1} 题缺少参考答案"
            )


# 导出函数
__all__ = ["generate_questions"]