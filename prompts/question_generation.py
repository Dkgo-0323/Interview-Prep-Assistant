from typing import Dict, Any
from models.schemas import GapAnalysis, ResumeInfo, JDInfo

# ==========================================
# 1. System Prompt
# ==========================================
QUESTION_SYSTEM_PROMPT = """你是一个资深且极其严谨的技术面试官。你的任务是根据候选人的【能力差距分析】、【简历精简履历】以及【职位核心要求】，为候选人量身定制一套个性化的模拟面试题。

【核心原则 - 必读】
1. 绝对避免重复：禁止在同一领域内生成高度相似或概念重叠的问题（例如：不要同时问“请解释Python基础语法”和“Python有哪些基础数据类型”）。每个问题必须具有独立且唯一的考察价值。
2. 结合真实履历：在生成“项目经验”类问题时，必须紧扣提供的简历项目细节进行追问，不要凭空捏造候选人没做过的项目。
3. 针对性弥补短板：技术类问题应重点考察 Gap 分析中提到的 missing_skills 和 weaknesses。
4. 参考答案要求：reference_answer 必须简明扼要（1-3句话），直接指出核心得分点或思考框架，不要长篇大论。
5. 严格遵循输出格式：输出必须是符合给定 JSON Schema 的对象。
"""

# ==========================================
# 2. 动态分配计算逻辑 (Python 层处理)
# ==========================================
def _calculate_distribution(score: int, total_questions: int = 20) -> str:
    """
    根据 overall_match_score 动态计算题目分布
    score < 60: 60%基础 + 40%进阶
    score >= 60: 40%基础 + 60%高级
    类型占比: 技术60% (12), 项目30% (6), 情景5% (1), 行为5% (1)
    """
    # 基础类型数量
    tech_total = int(total_questions * 0.6)       # 12
    proj_total = int(total_questions * 0.3)       # 6
    scene_total = int(total_questions * 0.05)     # 1
    behav_total = int(total_questions * 0.05)     # 1
    
    # 防止因小数取整导致的数量丢失（兜底补齐到技术题）
    actual_total = tech_total + proj_total + scene_total + behav_total
    if actual_total < total_questions:
        tech_total += (total_questions - actual_total)

    if score < 60:
        dist = f"""
        【动态难度分配】 (匹配度 < 60，偏向基础构建与进阶提升)
        - 技术深度 ({tech_total}题): {int(tech_total*0.6)}题 [基础], {tech_total - int(tech_total*0.6)}题 [进阶]
        - 项目经验 ({proj_total}题): {int(proj_total*0.6)}题 [基础], {proj_total - int(proj_total*0.6)}题 [进阶]
        - 情景模拟 ({scene_total}题): 1题 [基础]
        - 行为面试 ({behav_total}题): 1题 [进阶]
        """
    else:
        dist = f"""
        【动态难度分配】 (匹配度 >= 60，偏向深度挖掘与高级挑战)
        - 技术深度 ({tech_total}题): {int(tech_total*0.4)}题 [基础], {tech_total - int(tech_total*0.4)}题 [高级]
        - 项目经验 ({proj_total}题): {int(proj_total*0.4)}题 [基础], {proj_total - int(proj_total*0.4)}题 [高级]
        - 情景模拟 ({scene_total}题): 1题 [高级]
        - 行为面试 ({behav_total}题): 1题 [基础]
        """
    return dist

# ==========================================
# 3. Prompt Generator
# ==========================================
def get_question_generation_prompt(
    gap: GapAnalysis, 
    resume: ResumeInfo, 
    jd: JDInfo, 
    num_questions: int = 20
) -> str:
    """
    构建包含精简上下文和动态数量分配的 Prompt
    """
    
    # 1. 提取 JD 核心要求 (精简)
    jd_reqs = "\n".join([f"- {req}" for req in jd.requirements]) if jd.requirements else "未提供明确要求"
    
    # 2. 提取简历项目与工作经验摘要 (防幻觉的关键)
    resume_summary = []
    if resume.work_experience:
        resume_summary.append("【工作经历摘要】:")
        for exp in resume.work_experience:
            resume_summary.append(f"- {exp.company} | {exp.role} ({exp.duration}): {exp.description[:100]}...")
            
    if resume.projects:
        resume_summary.append("【核心项目摘要】:")
        for proj in resume.projects:
            tech_stack = ", ".join(proj.tech_stack) if proj.tech_stack else "未知"
            resume_summary.append(f"- 项目名: {proj.project_name} | 栈: {tech_stack}")
            if proj.description:
                resume_summary.append(f"  描述: {proj.description[:150]}...")
    
    resume_context = "\n".join(resume_summary) if resume_summary else "无可用项目/工作经验记录"

    # 3. 计算精准的题目分布指令
    distribution_instructions = _calculate_distribution(gap.overall_match_score, num_questions)

    # 4. 组装最终 Prompt
    prompt = f"""
请为候选人生成精确数量为 {num_questions} 道面试题。

### 1. 职位核心要求 (JD)
{jd_reqs}

### 2. 候选人能力差距分析 (Gap Analysis)
{gap.model_dump_json(indent=2, exclude={'overall_match_score'})}
(注：该候选人的综合匹配度为 {gap.overall_match_score}/100)

### 3. 候选人履历摘要 (Resume Highlight)
{resume_context}

### 4. 生成要求与分布
请严格按照以下分布生成 {num_questions} 道题目，数量必须分毫不差：
{distribution_instructions}

开始生成 JSON，确保所有的 `question_type` 和 `difficulty` 均符合 Enum 枚举值定义，并且 `reference_answer` 简短精炼。
"""
    return prompt