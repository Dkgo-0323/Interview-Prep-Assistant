# core/analyzers/resume_analyzer.py

import logging
from models.schemas import ResumeInfo
from services.llm_service import LLMService
from prompts.resume_extraction import RESUME_SYSTEM_PROMPT, get_resume_extraction_prompt
from core.analyzers.exceptions import ResumeAnalysisError

logger = logging.getLogger(__name__)

# 简历长度的安全限制 (约合20页密集文本)
MAX_RESUME_LENGTH = 30000 

def analyze_resume(text: str, llm: LLMService) -> ResumeInfo:
    """
    分析简历文本并提取高度结构化的信息（支持多层嵌套）。

    Args:
        text (str): 纯文本格式的简历内容
        llm (LLMService): LLM服务实例 (依赖注入)

    Returns:
        ResumeInfo: 结构化的简历信息模型

    Raises:
        ResumeAnalysisError: 当输入无效、超长或LLM提取失败时抛出友好异常
    """
    # 1. 基础校验：非空与过短检查
    if not text or not text.strip():
        raise ResumeAnalysisError("输入的简历文本为空，请重新上传或提供有效内容。")
        
    if len(text.strip()) < 50:
        raise ResumeAnalysisError("输入的简历内容过短，无法提取有效的个人经历。")

    # 2. 上限拦截：防止恶意超长文本（对应20页上限决策）
    if len(text) > MAX_RESUME_LENGTH:
        logger.warning(f"简历文本超长，当前字符数: {len(text)}，上限: {MAX_RESUME_LENGTH}")
        raise ResumeAnalysisError("简历内容过长（超过约20页限制）。请精简后重试。")

    # 3. 调用 LLM 进行嵌套结构的提取
    try:
        prompt = get_resume_extraction_prompt(text)
        
        logger.info("开始请求 LLM 解析简历（含嵌套结构）...")
        result = llm.call(
            prompt=prompt,
            response_model=ResumeInfo,
            system_prompt=RESUME_SYSTEM_PROMPT
        )
        logger.info(f"简历解析成功！提取到 {len(result.experiences)} 段经历, {len(result.projects)} 个项目。")
        return result

    except Exception as e:
        # 内部打印完整报错堆栈，便于排查 Pydantic ValidationError 或 网络异常
        logger.error(f"简历分析过程中发生底层错误: {str(e)}", exc_info=True)
        # 向上层（前端）抛出统一的对用户友好的业务异常（决策3）
        raise ResumeAnalysisError("简历解析失败，请检查文件内容格式是否过于混乱，或稍后重试。")