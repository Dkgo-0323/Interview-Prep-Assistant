# models/schemas.py

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class QuestionType(str, Enum):
    TECHNICAL = "技术深度"      # 对应 missing_skills / matched_skills
    PROJECT = "项目经验"        # 对应 resume projects / work_experience
    SCENARIO = "情景模拟"       # 对应 实际工作场景问题
    BEHAVIORAL = "行为面试"     # 对应 软技能/团队协作

class DifficultyLevel(str, Enum):
    BASIC = "基础"
    INTERMEDIATE = "进阶"
    ADVANCED = "高级"

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
    projects: list[Project] = Field(default_factory=list) # 让它默认变为空列表
    education: List[Education]
    
    # === 扩展字段 ===
    summary: Optional[str] = None         # 职业摘要（2-3 句话）
    certifications: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)  # "English (Native)"
    years_of_experience: Optional[int] = None

class GapAnalysis(BaseModel):
    """Gap analysis between JD requirements and resume qualifications."""
    
    # === 技能匹配 (权重 40%) ===
    matched_skills: List[str]                   # JD要求 ∩ 简历拥有（同义词已合并）
    missing_skills: List[str]                   # JD要求 - 简历拥有
    skill_score: int = Field(ge=0, le=100)      # 0-100
    
    # === 经验匹配 (权重 30%) ===
    experience_match: str                       # 自由文本描述
    experience_score: int = Field(ge=0, le=100) # 0-100
    
    # === 教育匹配 (权重 20%) ===
    education_match: str                        # 自由文本描述
    education_score: int = Field(ge=0, le=100)  # 0-100
    
    # === 项目相关性 (权重 10%) ===
    project_relevance: str                      # 自由文本描述
    project_score: int = Field(ge=0, le=100)    # 0-100
    
    # === 综合评估 ===
    strengths: List[str]                        # 优势（3-5条）
    weaknesses: List[str]                       # 劣势（3-5条）
    recommendations: List[str]                  # 针对性建议（3-5条）
    
    # === 计算字段 ===
    overall_match_score: int = Field(ge=0, le=100)  # Python 计算，非 LLM 输出

class Question(BaseModel):
    question_text: str = Field(..., description="具体的面试问题内容")
    question_type: QuestionType = Field(..., description="问题所属类型")
    difficulty: DifficultyLevel = Field(..., description="问题难度级别")
    focus_area: str = Field(..., description="关联的具体技能点或项目名（如：Vue3, 微服务重构项目）")
    intent: str = Field(..., description="一句话说明考察意图，让用户明白该问题的意义")
    reference_answer: str = Field(..., description="简短的参考答案或核心得分点（限1-3句话，直击要害）")

class QuestionList(BaseModel):
    questions: List[Question] = Field(..., description="生成的面试题列表")

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
    "QuestionList"
]