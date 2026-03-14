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
│   ├── 📄 main.py                   # Application entry point
│   └── 📂 pages/                    # Streamlit multi-page app
│       ├── 📄 01_upload.py          # Page: Upload JD + Resume
│       ├── 📄 02_analysis.py        # Page: Gap analysis results
│       └── 📄 03_questions.py       # Page: Generated interview questions
│
├── 📂 core/                         # ========== BUSINESS LOGIC ==========
│   ├── 📂 parsers/                  # File parsing module
│   │   ├── 📄 pdf_parser.py         # Parse PDF to text
│   │   ├── 📄 docx_parser.py        # Parse DOCX to text
│   │   ├── 📄 txt_parser.py         # Parse TXT with encoding detection
│   │   └── 📄 parser_factory.py     # Auto-select parser by file extension
│   │
│   ├── 📂 analyzers/                # AI analysis module
│   │   ├── 📄 jd_analyzer.py        # Extract structured info from JD
│   │   ├── 📄 resume_analyzer.py    # Extract structured info from Resume
│   │   └── 📄 gap_analyzer.py       # Match JD vs Resume
│   │
│   └── 📂 generators/               # Question generation module
│       └── 📄 question_generator.py # Generate personalized questions
│
├── 📂 prompts/                      # ========== LLM PROMPT TEMPLATES ==========
│   ├── 📄 jd_extraction.py          # Prompt for JD analysis
│   ├── 📄 resume_extraction.py      # Prompt for Resume analysis
│   ├── 📄 gap_analysis.py           # Prompt for gap analysis
│   └── 📄 question_generation.py    # Prompt for question generation
│
├── 📂 models/                       # ========== DATA MODELS ==========
│   ├── 📄 __init__.py               # ✅ Package exports
│   └── 📄 schemas.py                # ✅ Pydantic models (all enums and models)
│
├── 📂 services/                     # ========== SERVICES LAYER ==========
│   ├── 📄 __init__.py
│   └── 📄 llm_service.py            # LLM API wrapper
│
├── 📂 utils/                        # ========== UTILITIES ==========
│   ├── 📄 __init__.py
│   ├── 📄 logger.py                 # ✅ Logging configuration
│   ├── 📄 text_cleaner.py           # ✅ Text preprocessing
│   ├── 📄 token_counter.py          # Token counting & truncation
│   └── 📄 validators.py             # Input validation
│
├── 📂 data/uploads/                 # ✅ Temporary uploaded files (auto-created)
├── 📂 logs/                         # ✅ Log files (auto-created)
└── 📂 tests/                        # ========== TESTS ==========
    └── 📂 fixtures/                 # Test sample files
```

---

## 🔌 Core API Definitions

### **Module: utils/text_cleaner** ✅

```python
# text_cleaner.py

def clean_text(
    text: str,
    remove_extra_whitespace: bool = True,
    normalize_line_breaks: bool = True,
    remove_special_chars: bool = False,
    lowercase: bool = False
) -> str:
    """
    清洗和标准化文本内容
    
    Features:
        - 统一换行符（\r\n, \r → \n）
        - 去除多余空白（多空格、制表符、过多空行）
        - 可选：去除特殊字符（保留字母数字和基本标点）
        - 可选：转小写
        
    Returns:
        清洗后的文本字符串
    """

def remove_html_tags(text: str) -> str:
    """去除HTML标签和实体（&nbsp;等）"""

def normalize_unicode(text: str) -> str:
    """统一Unicode编码（NFC规范化）"""
```

**Usage:**
```python
from utils.text_cleaner import clean_text

# 基础清洗
text = clean_text(raw_text)

# 完全清洗
text = clean_text(raw_text, 
                  remove_special_chars=True, 
                  lowercase=True)
```

---

### **Module: utils/logger** ✅

```python
# logger.py

def get_logger(name: str) -> Logger:
    """
    获取配置好的logger实例
    
    Features:
        - 彩色控制台输出（DEBUG=青, INFO=绿, WARNING=黄, ERROR=红）
        - 文件轮转（5MB/文件，保留3个备份）
        - 自动创建logs/目录
        - Logger缓存避免重复handlers
    """

default_logger: Logger  # 模块级默认logger
```

---

### **Module: models/schemas** ✅

```python
# schemas.py - 核心数据模型

# 枚举类型
class QuestionType(str, Enum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SCENARIO = "scenario"
    PROJECT = "project"

class DifficultyLevel(str, Enum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"

# 主要模型
class JDInfo(BaseModel):
    job_title: str
    required_skills: List[str]
    nice_to_have_skills: List[str]
    responsibilities: List[str]
    industry: Optional[str]
    seniority_level: Optional[str]

class ResumeInfo(BaseModel):
    skills: List[str]
    experiences: List[WorkExperience]
    projects: List[Project]
    education: List[Education]
    years_of_experience: Optional[int]

class GapAnalysis(BaseModel):
    overall_match_score: float  # 0-100
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
```

---

### **Module: core/parsers**

```python
# parser_factory.py
def parse_file(file_path: str) -> str:
    """自动检测文件类型并提取文本"""
```

---

### **Module: core/analyzers**

```python
# jd_analyzer.py
def analyze_jd(text: str) -> JDInfo:
    """从职位描述中提取结构化信息"""

# resume_analyzer.py
def analyze_resume(text: str) -> ResumeInfo:
    """从简历中提取结构化信息"""

# gap_analyzer.py
def analyze_gap(jd: JDInfo, resume: ResumeInfo) -> GapAnalysis:
    """分析职位要求与简历的匹配度"""
```

---

### **Module: core/generators**

```python
# question_generator.py
def generate_questions(gap: GapAnalysis, num_questions: int = 10) -> List[Question]:
    """生成个性化面试问题"""
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
    """调用LLM API并返回结构化输出"""

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """计算文本的token数量"""
```

---

## 📦 Installed Dependencies

| Package | Version | Purpose | Status |
|---------|---------|---------|--------|
| `streamlit` | 1.40.0 | Web UI framework | ✅ |
| `python-dotenv` | 1.0.1 | Environment variables | ✅ |
| `pdfplumber` | 0.11.4 | PDF extraction | ✅ |
| `python-docx` | 1.1.2 | DOCX extraction | ✅ |
| `chardet` | 5.2.0 | Encoding detection | ✅ |
| `openai` | 1.55.0 | OpenAI API | ✅ |
| `tiktoken` | 0.8.0 | Token counting | ✅ |
| `pydantic` | 2.10.2 | Data validation | ✅ |

---

## 📊 Module Status

### **Phase 1 Progress Tracker**

```
✅ Configuration Layer (100%)
├── [✅] config.py
└── [✅] .env setup

✅ Data Models (100%)
├── [✅] models/schemas.py
└── [✅] models/__init__.py

🚧 Utilities (25%)
├── [✅] utils/logger.py              - Logging system
├── [✅] utils/text_cleaner.py        - Text preprocessing
├── [ ] utils/token_counter.py       - Token management
└── [ ] utils/validators.py          - Input validation

⬜ File Parsing (0%)
├── [ ] core/parsers/pdf_parser.py
├── [ ] core/parsers/docx_parser.py
├── [ ] core/parsers/txt_parser.py
└── [ ] core/parsers/parser_factory.py

⬜ Services (0%)
└── [ ] services/llm_service.py

⬜ Prompts (0%)
├── [ ] prompts/jd_extraction.py
├── [ ] prompts/resume_extraction.py
├── [ ] prompts/gap_analysis.py
└── [ ] prompts/question_generation.py

⬜ Analyzers (0%)
├── [ ] core/analyzers/jd_analyzer.py
├── [ ] core/analyzers/resume_analyzer.py
└── [ ] core/analyzers/gap_analyzer.py

⬜ Generators (0%)
└── [ ] core/generators/question_generator.py

⬜ Frontend (0%)
├── [ ] app/main.py
├── [ ] app/pages/01_upload.py
├── [ ] app/pages/02_analysis.py
└── [ ] app/pages/03_questions.py

Overall Phase 1 Progress: 5/25 modules (20%)
```

---

## 🎯 Current Working Module

**Status**: 🟢 `utils/text_cleaner.py` completed  
**Next Target**: `utils/token_counter.py`

**What to implement in utils/token_counter.py**:
```python
# Token计数和文本截断工具
# 依赖：tiktoken, config.py

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """使用tiktoken计算文本的token数量"""

def truncate_text(text: str, max_tokens: int, model: str = "gpt-4o-mini") -> str:
    """截断文本到指定token数量"""

def estimate_cost(num_tokens: int, model: str = "gpt-4o-mini") -> float:
    """估算API调用成本（美元）"""
```

**Why this order?**  
- Token管理是调用LLM API的前置依赖
- 需要在文本发送前检查长度限制
- 后续所有analyzer和generator都需要使用
- 依赖项已就绪：✅ config.py, ✅ tiktoken

**Blockers**: None  
**Dependencies Ready**: ✅ config.py, ✅ utils/logger.py, ✅ utils/text_cleaner.py

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
│ parser_factory  │ ──→ Raw Text
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  text_cleaner   │ ──→ Cleaned Text ✅
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│jd_     │ │resume_ │ ──→ JDInfo + ResumeInfo ✅
│analyzer│ │analyzer│
└────┬───┘ └───┬────┘
     │         │
     └────┬────┘
          ▼
    ┌───────────┐
    │gap_       │ ──→ GapAnalysis ✅
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
    │ Streamlit UI  │
    └───────────────┘
```

---

## ⚙️ Configuration

### **Environment Variables (.env)**

```env
# LLM Configuration
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1  # Optional
MODEL_NAME=gpt-4o-mini

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
```

### **Global Config (config.py)** ✅

```python
# Key constants:
PROJECT_ROOT: Path
UPLOAD_DIR: Path
OPENAI_API_KEY: str
MODEL_NAME: str
TEMPERATURE: float = 0.7
MAX_TOKENS: int = 2000
UPLOAD_MAX_SIZE_MB: int = 10
ALLOWED_EXTENSIONS: set = {'.pdf', '.docx', '.txt'}
LOG_LEVEL: str
DEBUG: bool
```

---

## 📝 Update Log

| Date | Version | Changes |
|------|---------|---------|
| 2025-01-XX | 0.1.0 | Initial architecture documentation |
| 2025-01-XX | 0.1.1 | ✅ Completed `config.py` |
| 2025-01-XX | 0.1.2 | ✅ Completed `models/schemas.py` |
| 2025-01-XX | 0.1.3 | ✅ Completed `utils/logger.py` |
| 2025-01-XX | 0.1.4 | ✅ Completed `utils/text_cleaner.py` |
| - | - | **Text preprocessing layer ready** ✅ |

---

## 🔜 Next Steps

1. ✅ Complete environment setup
2. ✅ Implement `config.py`
3. ✅ Implement `models/schemas.py`
4. ✅ Implement `utils/logger.py`
5. ✅ Implement `utils/text_cleaner.py`
6. ⬜ **[NEXT]** Implement `utils/token_counter.py`
7. ⬜ Implement `utils/validators.py`
8. ⬜ Implement file parsers (pdf/docx/txt)
9. ⬜ Implement `services/llm_service.py`
10. ⬜ Implement prompts and analyzers

---

## 📊 Completed Modules Detail

### ✅ utils/text_cleaner.py (100%)

**Implementation Details:**
- **Core Functions**:
  - `clean_text()`: 主清洗函数，支持4个可选参数
  - `remove_html_tags()`: 去除HTML标签和实体
  - `normalize_unicode()`: Unicode NFC规范化

- **Features**:
  - ✅ 换行符统一（\r\n, \r → \n）
  - ✅ 去除多余空白（多空格、制表符、过多空行）
  - ✅ 可选去除特殊字符（保留中英文、数字、基本标点）
  - ✅ 可选转小写
  - ✅ 每行首尾空白裁剪
  - ✅ 完整的输入验证和日志记录

**Export Interface:**
```python
from utils.text_cleaner import clean_text, remove_html_tags, normalize_unicode

# 基础清洗（默认参数）
clean_text = clean_text(raw_text)

# 完全清洗
clean_text = clean_text(raw_text, remove_special_chars=True, lowercase=True)

# HTML清洗
clean_text = remove_html_tags(html_text)
```

**Testing:**
```bash
python -m utils.text_cleaner
```

---

### ✅ utils/logger.py (100%)

**Features:**
- ✅ 彩色控制台输出（DEBUG=青色, INFO=绿色, WARNING=黄色, ERROR=红色）
- ✅ 文件轮转（5MB/文件，保留3个备份）
- ✅ Logger缓存防止重复handlers
- ✅ 自动创建logs/目录
- ✅ 环境变量配置（DEBUG模式仅控制台）

**Export Interface:**
```python
from utils.logger import get_logger, default_logger

logger = get_logger(__name__)
logger.info("Module started")
```

---

### ✅ models/schemas.py (100%)

**Includes:**
- ✅ 2个枚举类（QuestionType, DifficultyLevel）
- ✅ 3个子模型（WorkExperience, Project, Education）
- ✅ 4个主模型（JDInfo, ResumeInfo, GapAnalysis, Question）
- ✅ Pydantic v2类型验证和约束

**Export Interface:**
```python
from models.schemas import (
    QuestionType, DifficultyLevel,
    JDInfo, ResumeInfo, GapAnalysis, Question
)
```

---

**Note**: This document is the **single source of truth** for project structure. Update whenever:
- ✅ A new module is completed
- 🔄 API signatures change
- 📦 New dependencies are added
- 🏗️ Architecture decisions are made