# models/schemas.py

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class QuestionType(str, Enum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SCENARIO = "scenario"
    PROJECT = "project"

class DifficultyLevel(str, Enum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"

# ========== Resume Related Models ==========

class WorkExperience(BaseModel):
    """工作经历"""
    company: str
    title: str
    start_date: Optional[str] = None      # 原样保留："Jan 2020", "2020-01"
    end_date: Optional[str] = None        # "Present", "Dec 2023"
    responsibilities: List[str] = Field(default_factory=list)  # 含未区分的成就
    achievements: List[str] = Field(default_factory=list)      # 明确的量化成果


class Project(BaseModel):
    """项目经历"""
    name: str
    description: str
    technologies: List[str] = Field(default_factory=list)
    role: Optional[str] = None
    link: Optional[str] = None


class Education(BaseModel):
    """教育背景"""
    institution: str
    degree: str                           # "Bachelor of Science in Computer Science"
    field_of_study: Optional[str] = None  # 允许与 degree 冗余
    graduation_date: Optional[str] = None
    gpa: Optional[str] = None

class JDInfo(BaseModel):
    job_title: str
    company: Optional[str] = None
    required_skills: List[str]
    nice_to_have_skills: List[str] = Field(default_factory=list)
    responsibilities: List[str]
    experience_required: Optional[str] = None
    education_required: Optional[str] = None
    industry: Optional[str] = None
    seniority_level: Optional[str] = None

# ========== 修改 ResumeInfo ==========

class ResumeInfo(BaseModel):
    """简历信息（增强版本 - v0.4.1）"""
    # === 核心字段 ===
    skills: List[str]                     # 带熟练度标记："Python (Expert)", "React"
    experiences: List[WorkExperience]
    projects: List[Project]
    education: List[Education]
    
    # === 扩展字段 ===
    summary: Optional[str] = None         # 职业摘要（2-3 句话）
    certifications: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)  # "English (Native)"
    years_of_experience: Optional[int] = None

class GapAnalysis(BaseModel):
    overall_match_score: float = Field(..., ge=0, le=100)
    matched_skills: List[str]
    missing_skills: List[str]
    strengths: List[str]
    weaknesses: List[str]
    focus_areas: List[str]

class Question(BaseModel):
    question_text: str
    question_type: QuestionType
    difficulty: DifficultyLevel
    focus_area: str
    reference_answer: str
    evaluation_criteria: List[str]

__all__ = [
    "QuestionType",
    "DifficultyLevel",
    "WorkExperience",
    "Project",
    "Education",
    "JDInfo",
    "ResumeInfo",
    "GapAnalysis",
    "Question",
]