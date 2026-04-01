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

class WorkExperience(BaseModel):
    company: str
    role: str
    duration: str
    achievements: List[str]

class Project(BaseModel):
    name: str
    description: str
    technologies: List[str]
    role: str

class Education(BaseModel):
    degree: str
    institution: str
    graduation_year: Optional[int] = None

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

class ResumeInfo(BaseModel):
    skills: List[str]
    experiences: List[WorkExperience]
    projects: List[Project]
    education: List[Education]
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