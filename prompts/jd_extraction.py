# prompts/jd_extraction.py
"""
JD 提取的 prompt 模板模块。

负责构建用于提取 JD 结构化信息的 prompts。
纯函数 + 常量，零依赖，零副作用。
"""

# ============================================================
# System Prompt - 定义 LLM 角色和规则
# ============================================================

JD_SYSTEM_PROMPT = """你是一位专业的 HR 分析师，专门分析招聘职位描述。

请仔细阅读职位描述，准确提取以下信息：

关键规则：
1. 仅提取明确提到的信息，不要推断或编造
2. 仔细区分"必需技能"和"优先技能"：
   - "要求"、"必需"、"必备"、"必须" → 必需技能
   - "优先"、"加分"、"更好"、"有...者优先" → 优先技能
3. 经验要求提取为字符串格式：
   - "3-5 years"、"5+ years"、"Not specified"等
   - 如果提到"经验不限"或未提及，使用"Not specified"
4. 教育要求提取为字符串格式：
   - "Bachelor's degree in Computer Science"、"本科及以上"、"Not specified"等
5. 资历级别（seniority_level）提取：
   - 从职位名称或描述中推断："Junior"、"Mid-level"、"Senior"、"Lead"、"Staff"等
   - 如果无法判断，使用"Not specified"
6. 公司名称如果未明确提及，使用"Not specified"
7. 行业如果未明确提及，可以基于职位描述合理推断
8. 职位名称必须提取，如果描述中未明确提及，基于内容推断一个合理的
9. 所有列表字段（技能、职责）请确保是明确的列表，不要合并或拆分
10. 如果某个字段完全没有信息，使用适当默认值：
    - 字符串字段："Not specified"
    - 列表字段：[]
"""


# ============================================================
# User Prompt 构建函数
# ============================================================

def get_jd_extraction_prompt(text: str) -> str:
    """构建 JD 提取的 user prompt。
    
    Args:
        text: JD 的原始文本
        
    Returns:
        格式化的 prompt 字符串
        
    Notes:
        - 纯函数，无副作用
        - 不负责文本验证或截断（由调用者处理）
        - 返回的 prompt 应与 models.schemas.JDInfo 字段完全对应
    """
    return f"""请分析以下职位描述，提取结构化信息：

职位描述：
---
{text}
---

请准确提取以下字段：
- job_title: 职位名称
- company: 公司名称
- required_skills: 必需技能列表
- nice_to_have_skills: 优先技能列表
- responsibilities: 主要职责列表
- experience_required: 经验要求
- education_required: 教育要求
- industry: 行业信息
- seniority_level: 资历级别

确保严格按照规则处理缺失信息和技能分类。"""