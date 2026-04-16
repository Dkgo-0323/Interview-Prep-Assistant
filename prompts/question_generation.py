"""Question generation prompt templates.

Provides structured prompts for LLM to generate personalized interview questions.
"""

from typing import Dict, Optional, List
from models.schemas import GapAnalysis, ResumeInfo, JDInfo, Question


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
6. 数量精确性：必须严格按照要求的数量生成题目，不能多也不能少。
7. 题目自增编号验证：在你的内部思考过程中，请为每道题打上序号（如 1/N, 2/N），以确保你严格生成到了指定的数量，不会中途截断。
"""


# ==========================================
# 2. Resume 上下文截断函数
# ==========================================
def _truncate_resume_context(resume: ResumeInfo) -> str:
    """
    截断简历上下文，防止幻觉并控制 token 数量。
    """
    resume_summary = []
    
    if resume.skills:
        resume_summary.append("【技能列表】:")
        for skill in resume.skills[:20]:
            resume_summary.append(f"- {skill}")
            
    if resume.experiences:
        resume_summary.append("\n【工作经历摘要】:")
        for exp in resume.experiences[-3:]:
            start = exp.start_date or "未知"
            end = exp.end_date or "至今"
            date_info = f" ({start} - {end})"
            
            resume_summary.append(f"- {exp.company} | {exp.title}{date_info}")
            
            for i, resp in enumerate(exp.responsibilities[:3]):
                truncated = resp[:150] + "..." if len(resp) > 150 else resp
                resume_summary.append(f"  {i+1}. {truncated}")
                
            if exp.achievements:
                for i, ach in enumerate(exp.achievements[:2]):
                    truncated = ach[:100] + "..." if len(ach) > 100 else ach
                    resume_summary.append(f"  * 成就: {truncated}")
                    
    if resume.projects:
        resume_summary.append("\n【核心项目摘要】:")
        for proj in resume.projects:
            tech_str = ", ".join(proj.technologies) if proj.technologies else "未指定"
            role_str = f" | 角色: {proj.role}" if proj.role else ""
            resume_summary.append(f"- 项目: {proj.name}{role_str}")
            resume_summary.append(f"  技术栈: {tech_str}")
            
            if proj.description:
                truncated_desc = proj.description[:200] + "..." if len(proj.description) > 200 else proj.description
                resume_summary.append(f"  描述: {truncated_desc}")
                
    if resume.education:
        resume_summary.append("\n【教育背景】:")
        for edu in resume.education[:3]:
            gpa_str = f" | GPA: {edu.gpa}" if edu.gpa else ""
            grad_str = f" | 毕业: {edu.graduation_date}" if edu.graduation_date else ""
            resume_summary.append(f"- {edu.institution}: {edu.degree}{gpa_str}{grad_str}")
            
    return "\n".join(resume_summary) if resume_summary else "无可用简历信息"


# ==========================================
# 3. 格式化已有题目（用于分批生成）
# ==========================================
def _format_existing_questions(questions: List[Question], max_display: int = 5) -> str:
    """
    格式化已生成的题目，用于提示 LLM 避免重复。
    """
    if not questions:
        return "（暂无已生成题目）"
        
    formatted = []
    display_count = min(len(questions), max_display)
    
    for i, q in enumerate(questions[:display_count]):
        text_preview = q.question_text[:60] + "..." if len(q.question_text) > 60 else q.question_text
        formatted.append(f"{i+1}. [{q.question_type}] {text_preview}")
        
    if len(questions) > max_display:
        formatted.append(f"... 还有 {len(questions) - max_display} 道已生成题目")
        
    return "\n".join(formatted)


# ==========================================
# 4. Prompt Generator
# ==========================================
def get_question_generation_prompt(
    gap: GapAnalysis, 
    resume: ResumeInfo, 
    jd: JDInfo, 
    num_questions: int = 10,
    batch_info: Optional[Dict] = None
) -> str:
    """
    构建面试题生成 Prompt，包含精简上下文和智能分配指导。
    """
    jd_summary = []
    jd_summary.append(f"职位: {jd.job_title}")
    if jd.company:
        jd_summary.append(f"公司: {jd.company}")
        
    if jd.required_skills:
        jd_summary.append("\n【必备技能】:")
        for skill in jd.required_skills:
            jd_summary.append(f"- {skill}")
            
    if jd.responsibilities:
        jd_summary.append("\n【岗位职责】:")
        for i, resp in enumerate(jd.responsibilities[:5]):
            jd_summary.append(f"{i+1}. {resp}")
            
    jd_context = "\n".join(jd_summary)
    resume_context = _truncate_resume_context(resume)
    
    gap_summary = []
    gap_summary.append(f"匹配度总分: {gap.overall_match_score}/100")
    
    if gap.matched_skills:
        matched_display = ', '.join(gap.matched_skills[:10])
        if len(gap.matched_skills) > 10:
            matched_display += f"... (共{len(gap.matched_skills)}项)"
        gap_summary.append(f"匹配技能: {matched_display}")
        
    if gap.missing_skills:
        missing_display = ', '.join(gap.missing_skills[:10])
        if len(gap.missing_skills) > 10:
            missing_display += f"... (共{len(gap.missing_skills)}项)"
        gap_summary.append(f"缺失技能: {missing_display}")
        
    if gap.strengths:
        strengths_display = ', '.join(gap.strengths[:3])
        if len(gap.strengths) > 3:
            strengths_display += "..."
        gap_summary.append(f"优势: {strengths_display}")
        
    if gap.weaknesses:
        weaknesses_display = ', '.join(gap.weaknesses[:3])
        if len(gap.weaknesses) > 3:
            weaknesses_display += "..."
        gap_summary.append(f"劣势: {weaknesses_display}")
        
    gap_context = "\n".join(gap_summary)
    
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
3. 分配建议：
   - 技术深度类：重点考察 missing_skills 和 matched_skills
   - 项目经验类：基于候选人的实际项目追问细节
   - 情景模拟类：结合岗位职责设计实际工作场景
   - 行为面试类：考察软技能和团队协作能力
"""
    
    quantity_constraint = f"""
【数量约束 - 必须严格遵守】
✅ 请在返回的 JSON 列表中，严格确保数组元素的个数精确为 {num_questions} 个！
✅ 不允许生成少于或多于 {num_questions} 道题目。
✅ 每道题目必须包含完整的 6 个字段（question_text, question_type, difficulty, focus_area, intent, reference_answer）。
✅ reference_answer 不能为空或过于简短（至少 10 个字符）。

⚠️  重要提示：宁可多生成几道再删除，也绝对不要生成不足。如果数组长度不等于 {num_questions}，整个系统将崩溃。
"""
    
    batch_constraint = ""
    if batch_info:
        batch_number = batch_info.get("batch_number", 1)
        total_batches = batch_info.get("total_batches", 1)
        existing_questions = batch_info.get("existing_questions", [])
        
        batch_constraint = f"""
【分批生成说明】
当前批次: 第 {batch_number} 批，共 {total_batches} 批
本批次需生成: {num_questions} 道题目

已生成题目摘要（请避免重复）:
{_format_existing_questions(existing_questions, max_display=5)}

⚠️  分批生成注意事项：
- 请确保本批次的 {num_questions} 道题目与已有题目不重复
- 题目的考察角度和侧重点应与已有题目有所区分
"""
    
    prompt = f"""
请为候选人生成精确数量为 {num_questions} 道面试题。

{'='*60}

### 1. 职位核心要求 (JD)
{jd_context}

{'='*60}

### 2. 候选人能力差距分析 (Gap Analysis)
{gap_context}

{'='*60}

### 3. 候选人履历摘要 (Resume Highlight)
{resume_context}

{'='*60}

### 4. 生成要求
{distribution_guidance}

{'='*60}

### 5. 数量约束
{quantity_constraint}

{batch_constraint}

{'='*60}

【开始生成】
请严格按照上述要求生成 {num_questions} 道面试题，输出为 JSON 格式。
确保每道题目都完整、独立、无重复，且参考答案简明扼要。
"""
    return prompt


__all__ = [
    "QUESTION_SYSTEM_PROMPT",
    "get_question_generation_prompt"
]