# api/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, Any


class HealthResponse(BaseModel):
    status: str = "ok"


class UploadResponse(BaseModel):
    success: bool = True
    filename: str
    char_count: int
    preview: str  # 前200字符


class QuestionRequest(BaseModel):
    num_questions: int = Field(default=10, ge=10, le=50)


class QuestionResponse(BaseModel):
    success: bool = True
    total: int
    questions: list[Any]


class UserProfile(BaseModel):
    core_strengths: list[str]
    suitable_company_size: str
    career_stage: str
    search_keywords: list[str]
    positioning_summary: str
    salary_range_estimate: str


class ProfileResponse(BaseModel):
    success: bool = True
    profile: UserProfile