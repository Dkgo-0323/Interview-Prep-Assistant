from typing import Dict, Any
from models.schemas import GapAnalysis, ResumeInfo, JDInfo

# ==========================================
# 1. System Prompt
# ==========================================
QUESTION_SYSTEM_PROMPT = """你是一个资深且极其严谨的技术面试官。你的任务是根据候选人的【能力差距分析】、【简历精简履历】以及【职位核心要求】，为候选人量身定制一套个性化的模拟面试题。

【核心原则 - 必读】
1. 绝对避免重复：禁止在同一领域内生成高度相似或概念重叠的问题（例如：不要同时问"请解释Python基础语法"和"Python有哪些基础数据类型"）。每个问题必须具有独立且唯一的考察价值。
2. 结合真实履历：在生成"项目经验"类问题时，必须紧扣提供的简历项目细节进行追问，不要凭空捏造候选人没做过的项目。
3. 针对性弥补短板：技术类问题应重点考察 Gap 分析中提到的 missing_skills 和 weaknesses。
4. 参考答案要求：reference_answer 必须简明扼要（1-3句话），直接指出核心得分点或思考框架，不要长篇大论。
5. 严格遵循输出格式：输出必须是符合给定 JSON Schema 的对象。
"""

# ==========================================
# 2. Resume 上下文截断函数
# ==========================================
def _truncate_resume_context(resume: ResumeInfo) -> str:
    """
    截断简历上下文，防止幻觉并控制 token 数量。
    
    截断规则：
    - 保留最近 3 个 WorkExperience
    - 每个 experience 的 responsibilities 只取前 3 条
    - 每条 responsibility 截断到 150 字符
    - 保留所有 Projects，但 description 截断到 200 字符
    - 保留所有 skills（核心匹配依据）
    """
    resume_summary = []
    
    # 1. 技能列表（核心）
    if resume.skills:
        resume_summary.append("【技能列表】:")
        for skill in resume.skills[:20]:  # 最多显示 20 个技能
            resume_summary.append(f"- {skill}")
    
    # 2. 工作经历（截断）
    if resume.experiences:
        resume_summary.append("【工作经历摘要】:")
        # 取最近 3 个经历
        for exp in resume.experiences[-3:]:
            # 构建日期信息
            date_info = ""
            if exp.start_date or exp.end_date:
                start = exp.start_date or "未知"
                end = exp.end_date or "至今"
                date_info = f" ({start} - {end})"
            
            resume_summary.append(f"- {exp.company} | {exp.title}{date_info}")
            
            # 取前 3 条 responsibilities，每条截断到 150 字符
            for i, resp in enumerate(exp.responsibilities[:3]):
                truncated = resp[:150] + "..." if len(resp) > 150 else resp
                resume_summary.append(f"  {i+1}. {truncated}")
            
            # 如果有 achievements，也显示一些
            if exp.achievements:
                for i, ach in enumerate(exp.achievements[:2]):
                    truncated = ach[:100] + "..." if len(ach) > 100 else ach
                    resume_summary.append(f"  * 成就: {truncated}")
    
    # 3. 项目经历（保留所有，但截断描述）
    if resume.projects:
        resume_summary.append("【核心项目摘要】:")
        for proj in resume.projects:
            tech_str = ", ".join(proj.technologies) if proj.technologies else "未指定"
            role_str = f" | 角色: {proj.role}" if proj.role else ""
            resume_summary.append(f"- 项目: {proj.name}{role_str}")
            resume_summary.append(f"  技术栈: {tech_str}")
            
            # 描述截断到 200 字符
            if proj.description:
                truncated_desc = proj.description[:200] + "..." if len(proj.description) > 200 else proj.description
                resume_summary.append(f"  描述: {truncated_desc}")
    
    # 4. 教育背景（简要）
    if resume.education:
        resume_summary.append("【教育背景】:")
        for edu in resume.education[:3]:  # 最多显示 3 个学历
            gpa_str = f" | GPA: {edu.gpa}" if edu.gpa else ""
            grad_str = f" | 毕业: {edu.graduation_date}" if edu.graduation_date else ""
            resume_summary.append(f"- {edu.institution}: {edu.degree}{gpa_str}{grad_str}")
    
    return "\n".join(resume_summary) if resume_summary else "无可用简历信息"

# ==========================================
# 3. Prompt Generator
# ==========================================
def get_question_generation_prompt(
    gap: GapAnalysis, 
    resume: ResumeInfo, 
    jd: JDInfo, 
    num_questions: int = 10
) -> str:
    """
    构建面试题生成 Prompt，包含精简上下文和智能分配指导。
    
    Args:
        gap: Gap analysis result
        resume: Candidate's resume information
        jd: Job description information
        num_questions: Number of questions to generate (10-50, default 10)
        
    Returns:
        Formatted prompt string
    """
    
    # 1. 提取 JD 核心要求
    jd_summary = []
    jd_summary.append(f"职位: {jd.job_title}")
    if jd.company:
        jd_summary.append(f"公司: {jd.company}")
    
    if jd.required_skills:
        jd_summary.append("【必备技能】:")
        for skill in jd.required_skills:
            jd_summary.append(f"- {skill}")
    
    if jd.responsibilities:
        jd_summary.append("【岗位职责】:")
        for i, resp in enumerate(jd.responsibilities[:5]):  # 最多显示 5 条
            jd_summary.append(f"{i+1}. {resp}")
    
    jd_context = "\n".join(jd_summary)
    
    # 2. 提取简历摘要（截断后）
    resume_context = _truncate_resume_context(resume)
    
    # 3. 构建动态分配指导（让 LLM 根据具体情况决定）
    distribution_guidance = f"""
【题目生成指导】
请生成总计 {num_questions} 道面试题。

请根据以下信息智能分配题目类型和难度：

1. 职位类型分析：
   - 职位: {jd.job_title}
   - 必备技能: {len(jd.required_skills)} 项
   - 匹配度: {gap.overall_match_score}/100

2. 候选人特点：
   - 技能匹配: {len(gap.matched_skills)}/{len(jd.required_skills)} 项
   - 缺失技能: {len(gap.missing_skills)} 项
   - 工作经历: {len(resume.experiences)} 段
   - 项目经验: {len(resume.projects)} 个

3. 分配建议（请根据实际情况调整）：
   - 技术深度类：重点考察 missing_skills 和 matched_skills
   - 项目经验类：基于候选人的实际项目追问细节
   - 情景模拟类：结合岗位职责设计实际工作场景
   - 行为面试类：考察软技能和团队协作能力

4. 难度分配建议：
   - 匹配度 < 60: 侧重基础题（60%）和进阶题（40%）
   - 匹配度 >= 60: 侧重进阶题（40%）和高级题（60%）

请确保题目分布合理，避免重复，且所有题目都紧密结合候选人的实际情况。
"""

    # 4. 组装最终 Prompt
    prompt = f"""
请为候选人生成精确数量为 {num_questions} 道面试题。

### 1. 职位核心要求 (JD)
{jd_context}

### 2. 候选人能力差距分析 (Gap Analysis)
匹配度总分: {gap.overall_match_score}/100
匹配技能: {', '.join(gap.matched_skills[:10])}{'...' if len(gap.matched_skills) > 10 else ''}
缺失技能: {', '.join(gap.missing_skills[:10])}{'...' if len(gap.missing_skills) > 10 else ''}
优势: {', '.join(gap.strengths[:3])}{'...' if len(gap.strengths) > 3 else ''}
劣势: {', '.join(gap.weaknesses[:3])}{'...' if len(gap.weaknesses) > 3 else ''}

### 3. 候选人履历摘要 (Resume Highlight)
{resume_context}

### 4. 生成要求
{distribution_guidance}

开始生成 JSON，确保：
1. 题目数量精确为 {num_questions} 道
2. 所有 `question_type` 和 `difficulty` 均符合 Enum 枚举值定义
3. `reference_answer` 简短精炼（1-3句话）
4. 避免任何形式的题目重复
"""

    return prompt