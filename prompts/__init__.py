"""
Prompts 模块。

提供各种 LLM 调用所需的 prompt 模板。
所有 prompt 模块均为纯函数 + 常量，零依赖，零副作用。
"""

from prompts.jd_extraction import (
    SYSTEM_PROMPT as JD_SYSTEM_PROMPT,
    get_jd_extraction_prompt,
)

from prompts.resume_extraction import (
    RESUME_SYSTEM_PROMPT,
    get_resume_extraction_prompt,
)

__all__ = [
    # JD 提取
    "JD_SYSTEM_PROMPT",
    "get_jd_extraction_prompt",
    # Resume 提取
    "RESUME_SYSTEM_PROMPT",
    "get_resume_extraction_prompt",
]