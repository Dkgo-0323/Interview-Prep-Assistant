"""Question generator module.

Generates personalized interview questions based on gap analysis,
resume information, and job description requirements.
"""

import time
import difflib
from typing import List, Dict, Optional, Tuple
from models.schemas import GapAnalysis, ResumeInfo, JDInfo, QuestionList, Question
from services.llm_service import LLMService
from prompts.question_generation import QUESTION_SYSTEM_PROMPT, get_question_generation_prompt
from core.analyzers.exceptions import QuestionGenerationError
from utils.logger import get_logger

logger = get_logger(__name__)

# [优化] 降低单批次数量，提升大模型输出稳定性和计数准确性
BATCH_THRESHOLD = 10
BATCH_SIZE = 8


def generate_questions(
    gap: GapAnalysis,
    resume: ResumeInfo,
    jd: JDInfo,
    llm: LLMService,
    num_questions: int = 10
) -> QuestionList:
    """
    根据能力差距分析、简历和职位要求生成个性化面试题。
    """
    _validate_inputs(gap, resume, jd, num_questions)
    
    logger.info(f"开始生成 {num_questions} 道面试题")
    
    if num_questions <= BATCH_THRESHOLD:
        logger.info(f"题目数量 {num_questions} <= {BATCH_THRESHOLD}，采用单批次生成策略")
        return _generate_single_batch(gap, resume, jd, llm, num_questions)
    else:
        logger.info(f"题目数量 {num_questions} > {BATCH_THRESHOLD}，采用分批生成策略")
        return _generate_in_batches(gap, resume, jd, llm, num_questions)


def _generate_single_batch(
    gap: GapAnalysis,
    resume: ResumeInfo,
    jd: JDInfo,
    llm: LLMService,
    num_questions: int,
    batch_info: Optional[Dict] = None,
    max_retries: int = 3
) -> QuestionList:
    """
    单批次生成题目（核心生成逻辑 - 支持自适应查漏补缺）。
    """
    all_valid_questions: List[Question] = []
    current_retry = 0
    
    # [核心优化] 使用 While 循环进行动态补位
    while len(all_valid_questions) < num_questions and current_retry < max_retries:
        # 计算当前缺口的数量
        remaining_needed = num_questions - len(all_valid_questions)
        
        prompt = get_question_generation_prompt(gap, resume, jd, remaining_needed, batch_info)
        
        try:
            # 动态计算 max_tokens (基于当前还需要的题目数量)
            base_tokens = 1500 
            tokens_per_question = 240
            required_max_tokens = base_tokens + (remaining_needed * tokens_per_question)
            max_tokens = min(required_max_tokens, 14000)
            
            logger.debug(f"[第{current_retry+1}次尝试] 目标生成: {remaining_needed} 题, max_tokens: {max_tokens}")
            
            result: QuestionList = llm.call(
                prompt=prompt,
                response_model=QuestionList,
                system_prompt=QUESTION_SYSTEM_PROMPT,
                max_tokens=max_tokens
            )
            
            # 验证并合并本轮生成的题目
            for q in result.questions:
                # 1. 过滤空答案
                if not q.reference_answer or not q.reference_answer.strip():
                    continue
                    
                # 2. 检查本轮内部去重
                if _is_duplicate_question(q, all_valid_questions):
                    continue
                    
                # 3. 检查全局跨批次去重
                if batch_info and _is_duplicate_question(q, batch_info.get("existing_questions", [])):
                    continue
                    
                # 校验通过，加入集合
                all_valid_questions.append(q)
                
                # 如果数量已经达标，提前退出循环
                if len(all_valid_questions) == num_questions:
                    break
                    
        except Exception as e:
            logger.warning(f"批次生成遇到异常 (重试 {current_retry + 1}/{max_retries}): {str(e)}")
            
        current_retry += 1
        
        # 如果还没凑齐，等待一下继续发请求补齐差额
        if len(all_valid_questions) < num_questions and current_retry < max_retries:
            missing_count = num_questions - len(all_valid_questions)
            logger.info(f"本轮生成存在损耗或缺失，仍差 {missing_count} 题，触发自适应补全...")
            time.sleep(1)  # 短暂休眠，防止并发频率被限制

    # 最终防御性校验
    if len(all_valid_questions) < num_questions:
        error_msg = f"经过 {max_retries} 次自适应重试，仍未能生成足够数量的题目。期望: {num_questions}, 实际: {len(all_valid_questions)}"
        logger.error(error_msg)
        raise QuestionGenerationError(error_msg)

    logger.info(f"单批次生成成功，共获取 {len(all_valid_questions)} 道有效题目")
    return QuestionList(questions=all_valid_questions)


def _generate_in_batches(
    gap: GapAnalysis,
    resume: ResumeInfo,
    jd: JDInfo,
    llm: LLMService,
    total_questions: int
) -> QuestionList:
    """
    分批生成题目并合并结果。
    """
    batches = _calculate_batches(total_questions, BATCH_SIZE)
    logger.info(f"分批策略: {len(batches)} 批次，每批最多 {BATCH_SIZE} 题")
    
    all_questions: List[Question] = []
    
    for batch_idx, (batch_number, batch_count) in enumerate(batches):
        logger.info(f"正在生成第 {batch_number}/{len(batches)} 批，本批需 {batch_count} 题")
        
        batch_info = {
            "batch_number": batch_number,
            "total_batches": len(batches),
            "existing_questions": all_questions
        }
        
        try:
            batch_result = _generate_single_batch(
                gap, resume, jd, llm, batch_count, batch_info
            )
            all_questions.extend(batch_result.questions)
            
            logger.info(f"第 {batch_number} 批完成，累计 {len(all_questions)}/{total_questions} 题")
            
        except QuestionGenerationError as e:
            logger.error(f"第 {batch_number} 批生成失败: {str(e)}")
            raise
            
    # 截断以防万一
    final_questions = all_questions[:total_questions]
    logger.info(f"✅ 分批生成完成，共 {len(final_questions)} 道题目")
    
    return QuestionList(questions=final_questions)


def _calculate_batches(total: int, batch_size: int) -> List[Tuple[int, int]]:
    """
    计算分批策略。
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
    [优化] 使用 difflib 检查题目是否与已有题目高度相似。
    """
    for existing_q in existing:
        # 1. 完全相同
        if question.question_text == existing_q.question_text:
            return True
            
        # 2. 相似度检测：高于 85% 视为换壳重复题
        # SequenceMatcher 对于中英文混合的长文本相似度判断比较稳定
        similarity = difflib.SequenceMatcher(
            None, 
            question.question_text, 
            existing_q.question_text
        ).ratio()
        
        if similarity > 0.85:
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
    """
    if not (10 <= num_questions <= 50):
        raise ValueError("题目数量必须在 10 到 50 之间")
        
    if gap.overall_match_score is None:
        raise QuestionGenerationError("能力差距分析缺少匹配度分数")
        
    if not gap.missing_skills and not gap.matched_skills:
        raise QuestionGenerationError("能力差距分析缺少技能信息")
        
    if not resume.skills:
        raise QuestionGenerationError("简历缺少技能信息")
        
    if not jd.required_skills:
        raise QuestionGenerationError("职位描述缺少必备技能信息")


__all__ = ["generate_questions"]