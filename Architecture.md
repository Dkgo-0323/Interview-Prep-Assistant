# 📐 ARCHITECTURE.md

> **Project Map & Technical Documentation**  
> Last Updated: 2025-01-XX

---

## 📑 Table of Contents

1. [Project Overview](#project-overview)
2. [Directory Structure](#directory-structure)
3. [Core API Definitions](#core-api-definitions)
4. [Installed Dependencies](#installed-dependencies)
5. [Module Status](#module-status)
6. [Current Working Module](#current-working-module)
7. [Data Flow](#data-flow)
8. [Configuration](#configuration)

---

## 🎯 Project Overview

**Name**: Interview Prep Assistant  
**Purpose**: AI-powered personalized interview preparation tool  
**Current Phase**: Phase 1 - MVP (Question Generator)  
**Tech Stack**: Python 3.9+, Streamlit, OpenAI GPT-4o-mini

---

## 📂 Directory Structure

```
interview-prep-assistant/
│
├── 📄 .env                          # Environment variables (API keys) - NOT IN GIT
├── 📄 .env.example                  # Template for environment variables
├── 📄 .gitignore                    # Git ignore rules
├── 📄 requirements.txt              # Python dependencies
├── 📄 README.md                     # Project introduction & quick start
├── 📄 ARCHITECTURE.md              # This file - technical documentation
│
├── 📄 config.py                     # ✅ Global configuration (model, params, constants)
│   └── Status: [✅] Completed
│   └── Exports: All global constants and paths
│
├── 📂 app/                          # ========== FRONTEND (Streamlit) ==========
│   │
│   ├── 📄 main.py                   # Application entry point
│   │   └── Status: [ ] Not started
│   │   └── Purpose: Streamlit app config, routing, session state
│   │
│   ├── 📂 pages/                    # Streamlit multi-page app
│   │   ├── 📄 01_upload.py          # Page: Upload JD + Resume
│   │   │   └── Status: [ ] Not started
│   │   │   └── Purpose: File uploader UI, validation, trigger parsing
│   │   │
│   │   ├── 📄 02_analysis.py        # Page: Gap analysis results
│   │   │   └── Status: [ ] Not started
│   │   │   └── Purpose: Display JD vs Resume matching score & insights
│   │   │
│   │   ├── 📄 03_questions.py       # Page: Generated interview questions
│   │   │   └── Status: [ ] Not started
│   │   │   └── Purpose: Display questions with difficulty, type, answer
│   │   │
│   │   ├── 📄 04_mock_interview.py  # [Phase 2] Mock interview chat UI
│   │   ├── 📄 05_report.py          # [Phase 2] Evaluation report
│   │   └── 📄 06_history.py         # [Phase 3] History & wrong answer book
│   │
│   └── 📂 components/               # Reusable UI components
│       └── (Empty for Phase 1)
│
├── 📂 core/                         # ========== BUSINESS LOGIC ==========
│   │
│   ├── 📂 parsers/                  # File parsing module
│   │   ├── 📄 __init__.py
│   │   │
│   │   ├── 📄 pdf_parser.py         # Parse PDF to text
│   │   │   └── Status: [ ] Not started
│   │   │   └── Function: extract_text_from_pdf(file_path) -> str
│   │   │
│   │   ├── 📄 docx_parser.py        # Parse DOCX to text
│   │   │   └── Status: [ ] Not started
│   │   │   └── Function: extract_text_from_docx(file_path) -> str
│   │   │
│   │   ├── 📄 txt_parser.py         # Parse TXT with encoding detection
│   │   │   └── Status: [ ] Not started
│   │   │   └── Function: extract_text_from_txt(file_path) -> str
│   │   │
│   │   └── 📄 parser_factory.py     # Auto-select parser by file extension
│   │       └── Status: [ ] Not started
│   │       └── Function: parse_file(file_path) -> str
│   │
│   ├── 📂 analyzers/                # AI analysis module
│   │   ├── 📄 __init__.py
│   │   │
│   │   ├── 📄 jd_analyzer.py        # Extract structured info from JD
│   │   │   └── Status: [ ] Not started
│   │   │   └── Function: analyze_jd(text: str) -> JDInfo
│   │   │   └── Returns: job title, required skills, nice-to-have, responsibilities
│   │   │
│   │   ├── 📄 resume_analyzer.py    # Extract structured info from Resume
│   │   │   └── Status: [ ] Not started
│   │   │   └── Function: analyze_resume(text: str) -> ResumeInfo
│   │   │   └── Returns: skills, experiences, projects, education
│   │   │
│   │   └── 📄 gap_analyzer.py       # Match JD vs Resume
│   │       └── Status: [ ] Not started
│   │       └── Function: analyze_gap(jd: JDInfo, resume: ResumeInfo) -> GapAnalysis
│   │       └── Returns: match score, strengths, weaknesses, focus areas
│   │
│   ├── 📂 generators/               # Question generation module
│   │   ├── 📄 __init__.py
│   │   │
│   │   └── 📄 question_generator.py # Generate personalized questions
│   │       └── Status: [ ] Not started
│   │       └── Function: generate_questions(gap: GapAnalysis) -> List[Question]
│   │       └── Returns: 10 questions with type, difficulty, answer
│   │
│   └── 📂 interview/                # [Phase 2] Mock interview module
│       └── (Not yet created)
│
├── 📂 prompts/                      # ========== LLM PROMPT TEMPLATES ==========
│   │
│   ├── 📄 jd_extraction.py          # Prompt for JD analysis
│   │   └── Status: [ ] Not started
│   │   └── Exports: JD_EXTRACTION_PROMPT (string template)
│   │
│   ├── 📄 resume_extraction.py      # Prompt for Resume analysis
│   │   └── Status: [ ] Not started
│   │   └── Exports: RESUME_EXTRACTION_PROMPT
│   │
│   ├── 📄 gap_analysis.py           # Prompt for gap analysis
│   │   └── Status: [ ] Not started
│   │   └── Exports: GAP_ANALYSIS_PROMPT
│   │
│   └── 📄 question_generation.py    # Prompt for question generation
│       └── Status: [ ] Not started
│       └── Exports: QUESTION_GENERATION_PROMPT
│
├── 📂 models/                       # ========== DATA MODELS ==========
│   ├── 📄 __init__.py               # ✅ Package exports
│   │   └── Status: [✅] Completed
│   │   └── Exports: All schemas for external import
│   │
│   └── 📄 schemas.py                # ✅ Pydantic models
│       └── Status: [✅] Completed
│       └── Defines:
│           ✅ QuestionType (Enum: TECHNICAL/BEHAVIORAL/SCENARIO/PROJECT)
│           ✅ DifficultyLevel (Enum: JUNIOR/MID/SENIOR)
│           ✅ WorkExperience (company, role, duration, achievements)
│           ✅ Project (name, description, technologies, role)
│           ✅ Education (degree, institution, graduation_year)
│           ✅ JDInfo (job_title, required_skills, nice_to_have_skills, etc.)
│           ✅ ResumeInfo (skills, experiences, projects, education, years_of_experience)
│           ✅ GapAnalysis (match_score, matched_skills, missing_skills, etc.)
│           ✅ Question (question_text, type, difficulty, answer, criteria)
│
├── 📂 services/                     # ========== SERVICES LAYER ==========
│   ├── 📄 __init__.py
│   │
│   ├── 📄 llm_service.py            # LLM API wrapper
│   │   └── Status: [ ] Not started
│   │   └── Functions:
│   │       - call_llm(prompt: str, response_model: Type[BaseModel]) -> BaseModel
│   │       - count_tokens(text: str) -> int
│   │   └── Features: retry, error handling, token management
│   │
│   ├── 📄 db_service.py             # [Phase 3] Database operations
│   └── 📄 export_service.py         # [Phase 3] PDF export
│
├── 📂 utils/                        # ========== UTILITIES ==========
│   ├── 📄 __init__.py
│   │
│   ├── 📄 logger.py                 # Logging configuration
│   │   └── Status: [ ] Not started
│   │   └── Exports: get_logger(name: str) -> Logger
│   │
│   ├── 📄 text_cleaner.py           # Text preprocessing
│   │   └── Status: [ ] Not started
│   │   └── Function: clean_text(text: str) -> str
│   │
│   ├── 📄 token_counter.py          # Token counting & truncation
│   │   └── Status: [ ] Not started
│   │   └── Function: count_tokens(text: str, model: str) -> int
│   │
│   └── 📄 validators.py             # Input validation
│       └── Status: [ ] Not started
│       └── Functions:
│           - validate_file_size(file, max_mb: int) -> bool
│           - validate_file_extension(filename: str) -> bool
│
├── 📂 data/                         # ========== DATA STORAGE ==========
│   └── 📂 uploads/                  # ✅ Temporary uploaded files (auto-created)
│       └── .gitkeep
│
└── 📂 tests/                        # ========== TESTS ==========
    ├── 📂 fixtures/                 # Test sample files
    │   └── (Will add sample JD & Resume)
    │
    └── test_*.py                    # Unit tests (to be added)
```

---

## 🔌 Core API Definitions

### **Module: core/parsers**

```python
# parser_factory.py
def parse_file(file_path: str) -> str:
    """
    Auto-detect file type and extract text.
    
    Args:
        file_path: Path to uploaded file
        
    Returns:
        Extracted text content
        
    Raises:
        ValueError: Unsupported file format
    """
```

---

### **Module: core/analyzers**

```python
# jd_analyzer.py
from models.schemas import JDInfo

def analyze_jd(text: str) -> JDInfo:
    """
    Extract structured information from job description.
    
    Args:
        text: Raw JD text
        
    Returns:
        JDInfo model containing:
        - job_title: str
        - required_skills: List[str]
        - nice_to_have_skills: List[str]
        - responsibilities: List[str]
        - industry: str
        - seniority_level: str
    """
```

```python
# resume_analyzer.py
from models.schemas import ResumeInfo

def analyze_resume(text: str) -> ResumeInfo:
    """
    Extract structured information from resume.
    
    Args:
        text: Raw resume text
        
    Returns:
        ResumeInfo model containing:
        - skills: List[str]
        - experiences: List[WorkExperience]
        - projects: List[Project]
        - education: List[Education]
        - years_of_experience: int
    """
```

```python
# gap_analyzer.py
from models.schemas import JDInfo, ResumeInfo, GapAnalysis

def analyze_gap(jd: JDInfo, resume: ResumeInfo) -> GapAnalysis:
    """
    Analyze the gap between JD requirements and resume.
    
    Args:
        jd: Analyzed JD information
        resume: Analyzed resume information
        
    Returns:
        GapAnalysis model containing:
        - overall_match_score: float (0-100)
        - matched_skills: List[str]
        - missing_skills: List[str]
        - strengths: List[str]
        - weaknesses: List[str]
        - focus_areas: List[str]
    """
```

---

### **Module: core/generators**

```python
# question_generator.py
from models.schemas import GapAnalysis, Question

def generate_questions(
    gap: GapAnalysis,
    num_questions: int = 10
) -> List[Question]:
    """
    Generate personalized interview questions.
    
    Args:
        gap: Gap analysis results
        num_questions: Number of questions to generate
        
    Returns:
        List of Question models containing:
        - question_text: str
        - question_type: QuestionType (TECHNICAL/BEHAVIORAL/SCENARIO/PROJECT)
        - difficulty: DifficultyLevel (JUNIOR/MID/SENIOR)
        - focus_area: str
        - reference_answer: str
        - evaluation_criteria: List[str]
    """
```

---

### **Module: services/llm_service**

```python
# llm_service.py
from typing import Type, TypeVar
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

def call_llm(
    prompt: str,
    response_model: Type[T],
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> T:
    """
    Call LLM API with structured output.
    
    Args:
        prompt: Input prompt
        response_model: Pydantic model for response validation
        temperature: Sampling temperature
        max_tokens: Max response length
        
    Returns:
        Validated response as Pydantic model
        
    Raises:
        APIError: If LLM call fails
        ValidationError: If response doesn't match schema
    """

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """Count tokens in text for specific model."""
```

---

### **Module: models/schemas** ✅

```python
# schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class QuestionType(str, Enum):
    """面试问题类型枚举"""
    TECHNICAL = "technical"      # 技术问题
    BEHAVIORAL = "behavioral"    # 行为问题
    SCENARIO = "scenario"        # 情景问题
    PROJECT = "project"          # 项目问题

class DifficultyLevel(str, Enum):
    """问题难度等级枚举"""
    JUNIOR = "junior"   # 初级 (0-2年)
    MID = "mid"         # 中级 (3-5年)
    SENIOR = "senior"   # 高级 (5年+)

class WorkExperience(BaseModel):
    """工作经历模型"""
    company: str                 # 公司名称
    role: str                    # 职位
    duration: str                # 工作时长
    achievements: List[str]      # 工作成就

class Project(BaseModel):
    """项目经历模型"""
    name: str                    # 项目名称
    description: str             # 项目描述
    technologies: List[str]      # 技术栈
    role: str                    # 项目角色

class Education(BaseModel):
    """教育背景模型"""
    degree: str                  # 学位
    institution: str             # 学校
    graduation_year: Optional[int] = None  # 毕业年份

class JDInfo(BaseModel):
    """职位描述结构化信息"""
    job_title: str
    required_skills: List[str]
    nice_to_have_skills: List[str] = []
    responsibilities: List[str]
    industry: Optional[str] = None
    seniority_level: Optional[str] = None

class ResumeInfo(BaseModel):
    """简历结构化信息"""
    skills: List[str]
    experiences: List[WorkExperience]
    projects: List[Project]
    education: List[Education]
    years_of_experience: Optional[int] = None

class GapAnalysis(BaseModel):
    """差距分析结果"""
    overall_match_score: float = Field(ge=0, le=100)
    matched_skills: List[str]
    missing_skills: List[str]
    strengths: List[str]
    weaknesses: List[str]
    focus_areas: List[str]

class Question(BaseModel):
    """面试问题模型"""
    question_text: str
    question_type: QuestionType
    difficulty: DifficultyLevel
    focus_area: str
    reference_answer: str
    evaluation_criteria: List[str]
```

---

## 📦 Installed Dependencies

### **Current (requirements.txt)**

| Package | Version | Purpose | Status |
|---------|---------|---------|--------|
| `streamlit` | 1.40.0 | Web UI framework | ✅ Installed |
| `python-dotenv` | 1.0.1 | Environment variable management | ✅ Installed |
| `pdfplumber` | 0.11.4 | PDF text extraction | ✅ Installed |
| `python-docx` | 1.1.2 | DOCX text extraction | ✅ Installed |
| `chardet` | 5.2.0 | Text encoding detection | ✅ Installed |
| `openai` | 1.55.0 | OpenAI API client | ✅ Installed |
| `tiktoken` | 0.8.0 | Token counting | ✅ Installed |
| `pydantic` | 2.10.2 | Data validation | ✅ Installed |

### **To Add in Future Phases**

| Package | Purpose | Phase |
|---------|---------|-------|
| `sqlalchemy` | Database ORM | Phase 3 |
| `fpdf2` | PDF export | Phase 3 |
| `streamlit-chat` | Chat UI components | Phase 2 |
| `pytest` | Unit testing | Phase 2/3 |

---

## 📊 Module Status

### **Phase 1 Progress Tracker**

```
Configuration Layer:
├── [✅] config.py                    (100% - Completed)
│   ├── ✅ Environment variables loading
│   ├── ✅ Project paths configuration
│   ├── ✅ LLM settings (API key, model, temperature)
│   ├── ✅ File upload constraints
│   ├── ✅ Logging configuration
│   └── ✅ Auto-create upload directory
└── [✅] .env setup                   (100% - Completed)

Data Models:
├── [✅] models/schemas.py            (100% - Completed)
│   ├── ✅ QuestionType enum
│   ├── ✅ DifficultyLevel enum
│   ├── ✅ WorkExperience model
│   ├── ✅ Project model
│   ├── ✅ Education model
│   ├── ✅ JDInfo model
│   ├── ✅ ResumeInfo model
│   ├── ✅ GapAnalysis model
│   └── ✅ Question model
└── [✅] models/__init__.py           (100% - Completed)

Utilities:
├── [ ] utils/logger.py              (0% - Not started)
├── [ ] utils/text_cleaner.py        (0% - Not started)
├── [ ] utils/token_counter.py       (0% - Not started)
└── [ ] utils/validators.py          (0% - Not started)

File Parsing:
├── [ ] core/parsers/pdf_parser.py   (0% - Not started)
├── [ ] core/parsers/docx_parser.py  (0% - Not started)
├── [ ] core/parsers/txt_parser.py   (0% - Not started)
└── [ ] core/parsers/parser_factory.py (0% - Not started)

Services:
└── [ ] services/llm_service.py      (0% - Not started)

Prompts:
├── [ ] prompts/jd_extraction.py     (0% - Not started)
├── [ ] prompts/resume_extraction.py (0% - Not started)
├── [ ] prompts/gap_analysis.py      (0% - Not started)
└── [ ] prompts/question_generation.py (0% - Not started)

Analyzers:
├── [ ] core/analyzers/jd_analyzer.py (0% - Not started)
├── [ ] core/analyzers/resume_analyzer.py (0% - Not started)
└── [ ] core/analyzers/gap_analyzer.py (0% - Not started)

Generators:
└── [ ] core/generators/question_generator.py (0% - Not started)

Frontend:
├── [ ] app/main.py                  (0% - Not started)
├── [ ] app/pages/01_upload.py       (0% - Not started)
├── [ ] app/pages/02_analysis.py     (0% - Not started)
└── [ ] app/pages/03_questions.py    (0% - Not started)

Overall Phase 1 Progress: 3/25 modules (12%)
```

---

## 🎯 Current Working Module

**Status**: 🟢 models/schemas.py completed - Ready for next module  
**Next Target**: `utils/logger.py`  

**What to implement in utils/logger.py**:
```python
# Logging utility with:
1. Colored console output (development)
2. File logging with rotation (production)
3. Different log levels per environment
4. Structured logging format
5. get_logger(name: str) -> Logger factory function

Features:
- Read LOG_LEVEL from config.py
- Auto-create logs/ directory
- Format: [TIMESTAMP] [LEVEL] [MODULE] MESSAGE
- Console: colored output with rich/colorlog
- File: daily rotation with size limit
```

**Why this order?**  
- Logger is used by EVERY subsequent module for debugging
- No external dependencies on other business logic
- Once logger is ready, all future modules can import and use it

**Blockers**: None  
**Dependencies Ready**: ✅ config.py completed, models/schemas.py completed

---

## 🔄 Data Flow

```
┌─────────────┐
│ User Upload │
│  JD + Resume│
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ parser_factory  │ ──→ Raw Text (str)
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│jd_     │ │resume_ │ ──→ JDInfo + ResumeInfo (Pydantic) ✅
│analyzer│ │analyzer│
└────┬───┘ └───┬────┘
     │         │
     └────┬────┘
          ▼
    ┌───────────┐
    │gap_       │ ──→ GapAnalysis (Pydantic) ✅
    │analyzer   │
    └─────┬─────┘
          │
          ▼
    ┌───────────────┐
    │question_      │ ──→ List[Question] ✅
    │generator      │
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │ Streamlit UI  │ ──→ Display to user
    └───────────────┘
```

---

## ⚙️ Configuration

### **Environment Variables (.env)**

```env
# LLM Configuration
OPENAI_API_KEY=sk-...                    # Required
OPENAI_BASE_URL=https://api.openai.com/v1  # Optional (for proxy)
MODEL_NAME=gpt-4o-mini                   # Model to use

# Application Settings
DEBUG=False                              # Debug mode
LOG_LEVEL=INFO                          # Logging level
```

### **Global Config (config.py)** ✅

```python
# ✅ Implemented constants:
- PROJECT_ROOT: Path          # Project root directory
- UPLOAD_DIR: Path            # Upload files directory
- OPENAI_API_KEY: str         # API key from environment
- OPENAI_BASE_URL: str        # API base URL
- MODEL_NAME: str             # LLM model name
- TEMPERATURE: float          # LLM temperature (0.7)
- MAX_TOKENS: int             # Max response tokens (2000)
- UPLOAD_MAX_SIZE_MB: int     # Max file size (10MB)
- ALLOWED_EXTENSIONS: set     # Allowed file types {.pdf, .docx, .txt}
- LOG_LEVEL: str              # Logging level (INFO)
- DEBUG: bool                 # Debug mode flag
- DEFAULT_NUM_QUESTIONS: int  # Default question count (10)
```

---

## 📝 Update Log

| Date | Version | Changes |
|------|---------|---------|
| 2025-01-XX | 0.1.0 | Initial architecture documentation |
| 2025-01-XX | 0.1.1 | ✅ Completed `config.py` implementation |
| 2025-01-XX | 0.1.2 | ✅ Completed `models/schemas.py` - All Pydantic models defined |
| - | - | Project setup completed |
| - | - | Dependencies installed |
| - | - | Directory structure created |
| - | - | Global configuration system established |
| - | - | **Data contract layer completed** ✅ |

---

## 🔜 Next Steps

1. ✅ Complete environment setup
2. ✅ Implement `config.py`
3. ✅ Implement `models/schemas.py`
4. ⬜ **[NEXT]** Implement `utils/logger.py`
5. ⬜ Implement `utils/text_cleaner.py`
6. ⬜ Implement `utils/token_counter.py`
7. ⬜ Implement `utils/validators.py`
8. ⬜ Implement file parsers

---

## 📊 Completed Modules Detail

### ✅ models/schemas.py (100%)

**Implementation Details:**
- **Enums**: 
  - `QuestionType`: 4 types (TECHNICAL/BEHAVIORAL/SCENARIO/PROJECT)
  - `DifficultyLevel`: 3 levels (JUNIOR/MID/SENIOR)
  
- **Sub-models**:
  - `WorkExperience`: company, role, duration, achievements
  - `Project`: name, description, technologies, role
  - `Education`: degree, institution, graduation_year
  
- **Main Models**:
  - `JDInfo`: 6 fields with optional industry & seniority
  - `ResumeInfo`: 5 fields with nested models
  - `GapAnalysis`: 6 fields with score validation (0-100)
  - `Question`: 6 fields with enum types

**Export Interface:**
```python
from models.schemas import (
    QuestionType,
    DifficultyLevel,
    WorkExperience,
    Project,
    Education,
    JDInfo,
    ResumeInfo,
    GapAnalysis,
    Question
)
```

**Validation Features:**
- ✅ Type safety with Pydantic v2
- ✅ Field validation (e.g., score range 0-100)
- ✅ Optional fields with defaults
- ✅ Enum constraints for categorical fields
- ✅ Nested model support

**Usage Examples:**
```python
# Example 1: Create a JD info
jd = JDInfo(
    job_title="Senior Python Developer",
    required_skills=["Python", "Django", "PostgreSQL"],
    nice_to_have_skills=["Docker", "AWS"],
    responsibilities=["Design APIs", "Code review"],
    industry="FinTech",
    seniority_level="Senior"
)

# Example 2: Create a question
question = Question(
    question_text="How do you handle database migrations?",
    question_type=QuestionType.TECHNICAL,
    difficulty=DifficultyLevel.MID,
    focus_area="Database Management",
    reference_answer="Use migration tools like Alembic...",
    evaluation_criteria=["Knowledge of tools", "Best practices"]
)
```

---

**Note**: Update this file whenever:
- A new module is completed ✅
- API signatures change
- New dependencies are added
- Major architectural decisions are made