"""Gap analysis prompt templates.

This module provides prompts for analyzing the gap between
job description requirements and resume qualifications.
"""

from models.schemas import JDInfo, ResumeInfo

GAP_SYSTEM_PROMPT = """You are an expert career advisor and HR analyst.
Your task is to analyze the gap between a job description's requirements and a candidate's resume qualifications. Provide an objective, detailed assessment to help the candidate understand their fit for the position.

Key Guidelines:
1. **Language Requirement (CRITICAL)**: All analysis text, including descriptions, strengths, weaknesses, and recommendations MUST be generated and output in Simplified Chinese (简体中文). Technical skills and proper nouns (e.g., "Python", "AWS") should remain in English.
2. **Objective Assessment**: Be objective and constructive in your assessment.
3. **Skill Matching**: Normalize synonyms and abbreviations (e.g., "Python programming" = "Python", "AWS" = "Amazon Web Services", "JS" = "JavaScript").
4. **Actionable Feedback**: Provide specific, actionable recommendations focused on helping the candidate improve their candidacy.
5. **Scoring**: Score each dimension from 0-100 based on how well the resume meets the requirements.
6. **Special Cases Handling**: Handle edge cases gracefully (e.g., fresh graduates with no work experience, candidates with no formal education, etc.). Provide constructive feedback and alternative assessment criteria."""


def get_gap_analysis_prompt(jd: JDInfo, resume: ResumeInfo) -> str:
    """
    Generate prompt for gap analysis between JD and resume.

    Args:
        jd: Parsed job description information
        resume: Parsed resume information

    Returns:
        Formatted prompt string for LLM
    """
    jd_json = jd.model_dump_json(indent=2)
    resume_json = resume.model_dump_json(indent=2)

    return f"""Analyze the gap between the following job description and resume.

⚠️ CRITICAL INSTRUCTION: The content of your response MUST be in Simplified Chinese (简体中文). The JSON keys must remain exactly as requested in English, but all descriptive text values MUST be written in professional Chinese. 

## Job Description
```json
{jd_json}
```

## Resume
```json
{resume_json}
```

## Scoring Guidelines
Evaluate each dimension on a 0-100 scale:

**Skill Score (Weight: 40%)**
100: All required skills present, most preferred skills present
70-90: Most required skills present, some preferred skills
40-69: Some required skills present, gaps in key areas
0-39: Major skill gaps, few required skills present
IMPORTANT: Normalize skill names before matching (e.g., "React.js" = "React", "Amazon Web Services" = "AWS")

**Experience Score (Weight: 30%)**
100: Meets or exceeds experience requirements with highly relevant roles
70-90: Meets experience requirements, relevant industry/role
40-69: Slightly below requirements or partially relevant experience
10-39: Significantly below requirements or unrelated experience
0-9: No work experience provided (fresh graduate/freelancer)
SPECIAL CASE: If resume.experiences is empty, score based on project complexity, internship experience, and learning potential. Provide specific recommendations for entry-level positions.

**Education Score (Weight: 20%)**
100: Exceeds education requirements
70-90: Meets education requirements exactly
40-69: Partially meets requirements (related field, lower degree)
0-39: Does not meet education requirements
SPECIAL CASE: If resume.education is empty, score based on certifications, relevant coursework, or self-learning evidence.

**Project Score (Weight: 10%)**
100: Projects directly demonstrate required skills and relevant domain experience
70-90: Projects show most required technologies/skills
40-69: Projects partially relevant
0-39: Projects not relevant to the position
SPECIAL CASE: If resume.projects is empty, focus assessment on work experience and skills demonstration.

## Special Cases Handling
**For Fresh Graduates (empty experiences list)**:
- Assess potential based on educational background, projects, and internships
- In experience_match field, state: "应届毕业生，无正式工作经验。基于项目经历和实习经验进行评估。"
- In recommendations, suggest: "积累实习经验", "参与开源项目", "构建个人作品集" etc.
- Adjust experience_score based on project relevance (can reach 20-40 if projects are highly relevant)

**For Career Changers (unrelated experiences)**:
- Highlight transferable skills and relevant projects
- Provide recommendations for bridging the gap (e.g., "获取相关认证", "参与相关项目")

**For Candidates without Formal Education**:
- Focus on skills, projects, and certifications
- In education_match field, state: "无正式教育背景，但通过其他方式展示了相关能力"
- Score based on alternative qualifications

## Required Output Fields
Extract the following information:
- matched_skills: List of skills from JD that the candidate possesses (after normalizing synonyms/abbreviations)
- missing_skills: List of required/preferred skills from JD that the candidate lacks (translated to Chinese if it's a concept, keep English if it's a specific technology)
- skill_score: Integer 0-100
- experience_match: Description of how candidate's experience aligns with requirements (MUST BE IN CHINESE, e.g., "JD要求5年经验，候选人有3年相关经验，部分符合要求" or "应届毕业生，无正式工作经验")
- experience_score: Integer 0-100
- education_match: Description of education alignment (MUST BE IN CHINESE, e.g., "候选人拥有计算机科学硕士学位，超出了JD要求的本科学历")
- education_score: Integer 0-100
- project_relevance: Description of how candidate's projects relate to the job requirements (MUST BE IN CHINESE)
- project_score: Integer 0-100
- strengths: List of 3-5 candidate strengths relative to this position (MUST BE IN CHINESE)
- weaknesses: List of 3-5 gaps or areas for improvement (MUST BE IN CHINESE)
- recommendations: List of 3-5 specific, actionable suggestions to improve candidacy (MUST BE IN CHINESE)

NOTE: Do NOT include "overall_match_score" in your response - it will be calculated separately."""