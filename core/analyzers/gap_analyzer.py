"""Gap analyzer module.

Analyzes the gap between job description requirements 
and resume qualifications.
"""

from models.schemas import JDInfo, ResumeInfo, GapAnalysis
from services.llm_service import LLMService
from prompts.gap_analysis import GAP_SYSTEM_PROMPT, get_gap_analysis_prompt
from core.analyzers.exceptions import GapAnalysisError


def analyze_gap(jd: JDInfo, resume: ResumeInfo, llm: LLMService) -> GapAnalysis:
    """
    Analyze the gap between job requirements and candidate qualifications.
    
    Args:
        jd: Parsed job description information
        resume: Parsed resume information
        llm: LLM service instance for API calls
        
    Returns:
        GapAnalysis object with detailed gap assessment and calculated overall score
        
    Raises:
        GapAnalysisError: If input validation fails or analysis processing fails
        
    Example:
        >>> jd = analyze_jd(jd_text, llm)
        >>> resume = analyze_resume(resume_text, llm)
        >>> gap = analyze_gap(jd, resume, llm)
        >>> print(gap.overall_match_score)  # Calculated weighted score
    """
    # 1. Input validation
    _validate_inputs(jd, resume)
    
    try:
        # 2. Generate prompt
        prompt = get_gap_analysis_prompt(jd, resume)
        
        # 3. Call LLM (returns GapAnalysis without overall_match_score)
        raw_result: GapAnalysis = llm.call(
            prompt=prompt,
            response_model=GapAnalysis,
            system_prompt=GAP_SYSTEM_PROMPT
        )
        
        # 4. Validate individual dimension scores (redundant safety check)
        _validate_scores(raw_result)
        
        # 5. Calculate overall score in Python layer
        overall_score = _calculate_overall_score(
            skill_score=raw_result.skill_score,
            experience_score=raw_result.experience_score,
            education_score=raw_result.education_score,
            project_score=raw_result.project_score
        )
        
        # 6. Update overall score and return
        raw_result.overall_match_score = overall_score
        return raw_result
        
    except GapAnalysisError:
        # Re-raise our own exceptions without wrapping
        raise
    except Exception as e:
        # Wrap all other exceptions with user-friendly message
        raise GapAnalysisError(
            "无法完成岗位匹配度分析，请稍后重试或联系技术支持"
        ) from e


def _validate_inputs(jd: JDInfo, resume: ResumeInfo) -> None:
    """
    Validate input data before gap analysis.
    
    Args:
        jd: Job description info
        resume: Resume info
        
    Raises:
        GapAnalysisError: If validation fails with user-friendly message
    """
    # JD required fields validation
    if not jd.required_skills:
        raise GapAnalysisError(
            "职位描述缺少必要的技能要求信息，无法进行匹配度分析"
        )
    
    if not jd.responsibilities:
        raise GapAnalysisError(
            "职位描述缺少岗位职责信息，无法进行匹配度分析"
        )
    
    # Resume required fields validation
    if not resume.skills:
        raise GapAnalysisError(
            "简历中未找到技能信息，无法进行匹配度分析"
        )
    
    # Note: resume.projects is allowed to be empty
    # Not all candidates have project experience

def _validate_scores(result: GapAnalysis) -> None:
    """
    Validate that all dimension scores are within valid range (0-100).
    
    This is a redundant safety check on top of Pydantic's Field constraints.
    
    Args:
        result: Gap analysis result from LLM
        
    Raises:
        GapAnalysisError: If any score is out of valid range
    """
    scores = {
        "技能匹配度": result.skill_score,
        "经验匹配度": result.experience_score,
        "学历匹配度": result.education_score,
        "项目相关度": result.project_score
    }
    
    for score_name, score_value in scores.items():
        if not (0 <= score_value <= 100):
            raise GapAnalysisError(
                f"分析结果异常：{score_name}评分超出有效范围，请重试"
            )


def _calculate_overall_score(
    skill_score: int,
    experience_score: int,
    education_score: int,
    project_score: int
) -> int:
    """
    Calculate weighted overall match score.
    
    Scoring weights (aligned with prompt guidelines):
        - Skills: 40%
        - Experience: 30%
        - Education: 20%
        - Projects: 10%
    
    Args:
        skill_score: Score for skills match (0-100)
        experience_score: Score for experience match (0-100)
        education_score: Score for education match (0-100)
        project_score: Score for project relevance (0-100)
        
    Returns:
        Weighted overall score (0-100), rounded to nearest integer
        
    Example:
        >>> _calculate_overall_score(80, 70, 90, 60)
        77  # 80*0.4 + 70*0.3 + 90*0.2 + 60*0.1 = 77.0
    """
    weighted_score = (
        skill_score * 0.40 +
        experience_score * 0.30 +
        education_score * 0.20 +
        project_score * 0.10
    )
    
    return round(weighted_score)