# core/analyzers/jd_analyzer.py

import logging
from models.schemas import JDInfo
from services.llm_service import LLMService
from prompts.jd_extraction import JD_SYSTEM_PROMPT, get_jd_extraction_prompt
from core.analyzers.exceptions import JDAnalysisError

logger = logging.getLogger(__name__)

def analyze_jd(text: str, llm: LLMService) -> JDInfo:
    """
    分析工作描述(JD)文本并提取结构化信息。

    Args:
        text (str): 纯文本格式的职位描述(JD)
        llm (LLMService): LLM服务实例 (依赖注入)

    Returns:
        JDInfo: 结构化的JD信息模型

    Raises:
        JDAnalysisError: 当输入无效或LLM提取失败时抛出友好异常
    """
    # 1. 基础校验：非空与长度检查
    if not text or not text.strip():
        raise JDAnalysisError("输入的工作描述(JD)文本为空，请重新提供。")
        
    if len(text.strip()) < 20:
        raise JDAnalysisError("输入的工作描述(JD)文本过短，无法提取有效信息。")

    # 2. 调用LLM进行结构化提取
    try:
        prompt = get_jd_extraction_prompt(text)
        
        logger.info("开始请求 LLM 解析 JD...")
        result = llm.call(
            prompt=prompt,
            response_model=JDInfo,
            system_prompt=JD_SYSTEM_PROMPT
        )
        logger.info("JD 信息解析成功！")
        return result

    except Exception as e:
        # 内部打印完整报错堆栈，便于开发者排查
        logger.error(f"JD 分析过程中发生底层错误: {str(e)}", exc_info=True)
        # 向上层抛出对用户友好的业务异常
        raise JDAnalysisError("职位描述(JD)分析失败，请稍后重试或检查文本内容。")