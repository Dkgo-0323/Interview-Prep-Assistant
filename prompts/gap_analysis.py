"""Gap analysis prompt templates.

This module provides prompts for analyzing the gap between
job description requirements and resume qualifications.
"""

from models.schemas import JDInfo, ResumeInfo

GAP_SYSTEM_PROMPT = """You are an expert career advisor and HR analyst.
Your task is to analyze the gap between a job description's requirements and a candidate's resume qualifications. Provide an objective, detailed assessment to help the candidate understand their fit for the position.

Guidelines:
- Be objective and constructive in your assessment
- When matching skills, normalize synonyms and abbreviations (e.g., "Python programming" = "Python", "AWS" = "Amazon Web Services", "JS" = "JavaScript")
- Provide specific, actionable recommendations
- Focus on helping the candidate improve their candidacy
- Score each dimension from 0-100 based on how well the resume meets the requirements"""


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
0-39: Significantly below requirements or unrelated experience

**Education Score (Weight: 20%)**
100: Exceeds education requirements
70-90: Meets education requirements exactly
40-69: Partially meets requirements (related field, lower degree)
0-39: Does not meet education requirements

**Project Score (Weight: 10%)**
100: Projects directly demonstrate required skills and relevant domain experience
70-90: Projects show most required technologies/skills
40-69: Projects partially relevant
0-39: Projects not relevant to the position

## Required Output Fields
Extract the following information:
- matched_skills: List of skills from JD that the candidate possesses (after normalizing synonyms/abbreviations)
- missing_skills: List of required/preferred skills from JD that the candidate lacks
- skill_score: Integer 0-100
- experience_match: Description of how candidate's experience aligns with requirements (e.g., "JD requires 5 years, candidate has 3 years in relevant roles")
- experience_score: Integer 0-100
- education_match: Description of education alignment (e.g., "JD requires BS in CS, candidate has MS in Computer Science - exceeds requirement")
- education_score: Integer 0-100
- project_relevance: Description of how candidate's projects relate to the job requirements
- project_score: Integer 0-100
- strengths: List of 3-5 candidate strengths relative to this position
- weaknesses: List of 3-5 gaps or areas for improvement
- recommendations: List of 3-5 specific, actionable suggestions to improve candidacy

NOTE: Do NOT include "overall_match_score" in your response - it will be calculated separately."""