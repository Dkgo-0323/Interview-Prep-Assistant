# 📐 ARCHITECTURE.md

> **Project Map & Technical Documentation**  
> Last Updated: 2025-01-XX | Version: 0.1.5

---

## 📑 Table of Contents

1. [Project Overview](#project-overview)
2. [Directory Structure](#directory-structure)
3. [Module Status](#module-status)
4. [Core API Definitions](#core-api-definitions)
5. [Data Flow](#data-flow)
6. [Dependencies](#dependencies)
7. [Configuration](#configuration)

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
├── 📄 .env                          # Environment variables - NOT IN GIT
├── 📄 .env.example                  # Environment template
├── 📄 .gitignore
├── 📄 requirements.txt
├── 📄 README.md
├── 📄 ARCHITECTURE.md              # This file
│
├── 📄 config.py                     # ✅ Global configuration
│
├── 📂 app/                          # Frontend (Streamlit)
│   ├── 📄 main.py
│   └── 📂 pages/
│       ├── 📄 01_upload.py
│       ├── 📄 02_analysis.py
│       └── 📄 03_questions.py
│
├── 📂 core/                         # Business Logic
│   ├── 📂 parsers/
│   │   ├── 📄 pdf_parser.py
│   │   ├── 📄 docx_parser.py
│   │   ├── 📄 txt_parser.py
│   │   └── 📄 parser_factory.py
│   ├── 📂 analyzers/
│   │   ├── 📄 jd_analyzer.py
│   │   ├── 📄 resume_analyzer.py
│   │   └── 📄 gap_analyzer.py
│   └── 📂 generators/
│       └── 📄 question_generator.py
│
├── 📂 prompts/                      # LLM Prompt Templates
│   ├── 📄 jd_extraction.py
│   ├── 📄 resume_extraction.py
│   ├── 📄 gap_analysis.py
│   └── 📄 question_generation.py
│
├── 📂 models/                       # Data Models
│   ├── 📄 __init__.py               # ✅
│   └── 📄 schemas.py                # ✅ Pydantic models
│
├── 📂 services/                     # Services Layer
│   ├── 📄 __init__.py
│   └── 📄 llm_service.py
│
├── 📂 utils/                        # Utilities
│   ├── 📄 __init__.py
│   ├── 📄 logger.py                 # ✅ Logging system
│   ├── 📄 text_cleaner.py           # ✅ Text preprocessing
│   ├── 📄 token_counter.py          # ✅ Token management
│   └── 📄 validators.py             # Input validation
│
├── 📂 data/uploads/                 # ✅ Auto-created
├── 📂 logs/                         # ✅ Auto-created
└── 📂 tests/
    └── 📂 fixtures/
```

---

## 📊 Module Status

### **Phase 1 Progress Tracker**

```
✅ Foundation Layer (100%)
├── [✅] config.py                    - Global configuration
├── [✅] models/schemas.py            - Pydantic data models
└── [✅] models/__init__.py           - Package exports

✅ Utilities (75%)
├── [✅] utils/logger.py              - Logging system
├── [✅] utils/text_cleaner.py        - Text preprocessing
├── [✅] utils/token_counter.py       - Token management ⭐ NEW
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

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Progress: 6/25 modules (24%)
Next Target: utils/validators.py
```

---

## 🔌 Core API Definitions

### **✅ utils/token_counter.py** (NEW)

```python
def count_tokens(text: str, model: str = MODEL_NAME) -> int:
    """计算文本token数量"""

def truncate_text(
    text: str, 
    max_tokens: int, 
    model: str = MODEL_NAME,
    suffix: str = "..."
) -> str:
    """截断文本到指定token限制"""

def estimate_cost(
    num_tokens: int, 
    model: str = MODEL_NAME,
    cost_type: str = "input"
) -> float:
    """估算API调用成本（USD）"""

def get_token_info(text: str, model: str = MODEL_NAME) -> Dict:
    """获取完整token信息（便捷函数）"""
```

**Usage:**
```python
from utils.token_counter import count_tokens, truncate_text, estimate_cost

tokens = count_tokens(text)
if tokens > 4000:
    text = truncate_text(text, max_tokens=4000)
cost = estimate_cost(tokens)
```

**Features:**
- ✅ 编码器缓存（@lru_cache）
- ✅ 模型fallback机制（未知模型→cl100k_base）
- ✅ 4个模型定价表（gpt-4o-mini/gpt-4o/gpt-4/gpt-3.5-turbo）
- ✅ 截断日志记录（记录减少百分比）

---

### **✅ utils/text_cleaner.py**

```python
def clean_text(
    text: str,
    remove_extra_whitespace: bool = True,
    normalize_line_breaks: bool = True,
    remove_special_chars: bool = False,
    lowercase: bool = False
) -> str:
    """清洗和标准化文本"""

def remove_html_tags(text: str) -> str:
    """去除HTML标签和实体"""

def normalize_unicode(text: str) -> str:
    """Unicode NFC规范化"""
```

---

### **✅ utils/logger.py**

```python
def get_logger(name: str) -> Logger:
    """获取配置好的logger实例"""

default_logger: Logger  # 模块级默认logger
```

**Features:**
- 彩色控制台输出
- 文件轮转（5MB/文件，3个备份）
- Logger缓存

---

### **✅ models/schemas.py**

**Enums:**
- `QuestionType`: TECHNICAL | BEHAVIORAL | SCENARIO | PROJECT
- `DifficultyLevel`: JUNIOR | MID | SENIOR

**Models:**
- `JDInfo`: 职位描述信息
- `ResumeInfo`: 简历信息
- `GapAnalysis`: 匹配度分析
- `Question`: 生成的问题

---

### **⬜ utils/validators.py** (NEXT TARGET)

```python
def validate_file_extension(filename: str) -> bool:
    """验证文件扩展名是否允许"""

def validate_file_size(file_size: int) -> bool:
    """验证文件大小是否在限制内"""

def validate_text_content(text: str) -> Tuple[bool, str]:
    """验证文本内容（非空、最小长度）"""
```

---

### **⬜ Core Modules** (To Be Implemented)

```python
# parser_factory.py
def parse_file(file_path: str) -> str:
    """自动检测文件类型并提取文本"""

# jd_analyzer.py
def analyze_jd(text: str) -> JDInfo:
    """从JD提取结构化信息"""

# resume_analyzer.py
def analyze_resume(text: str) -> ResumeInfo:
    """从简历提取结构化信息"""

# gap_analyzer.py
def analyze_gap(jd: JDInfo, resume: ResumeInfo) -> GapAnalysis:
    """分析匹配度"""

# question_generator.py
def generate_questions(gap: GapAnalysis, num_questions: int = 10) -> List[Question]:
    """生成面试问题"""

# llm_service.py
def call_llm(prompt: str, response_model: Type[T], **kwargs) -> T:
    """调用LLM API"""
```

---

## 🔄 Data Flow

```
User Upload (JD + Resume)
    ↓
parser_factory → Raw Text
    ↓
text_cleaner → Cleaned Text ✅
    ↓
token_counter (检查长度) ✅
    ↓
┌─────────────┴─────────────┐
│                           │
jd_analyzer          resume_analyzer
    ↓                       ↓
JDInfo ✅              ResumeInfo ✅
    └──────────┬────────────┘
               ↓
         gap_analyzer
               ↓
         GapAnalysis ✅
               ↓
      question_generator
               ↓
       List[Question] ✅
               ↓
         Streamlit UI
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `streamlit` | 1.40.0 | Web UI |
| `python-dotenv` | 1.0.1 | Env vars |
| `pdfplumber` | 0.11.4 | PDF parsing |
| `python-docx` | 1.1.2 | DOCX parsing |
| `chardet` | 5.2.0 | Encoding detection |
| `openai` | 1.55.0 | OpenAI API |
| `tiktoken` | 0.8.0 | Token counting |
| `pydantic` | 2.10.2 | Data validation |

---

## ⚙️ Configuration

### **Environment Variables (.env)**

```env
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1  # Optional
MODEL_NAME=gpt-4o-mini
DEBUG=False
LOG_LEVEL=INFO
```

### **config.py Constants**

```python
PROJECT_ROOT: Path
UPLOAD_DIR: Path
OPENAI_API_KEY: str
MODEL_NAME: str
TEMPERATURE: float = 0.7
MAX_TOKENS: int = 2000
UPLOAD_MAX_SIZE_MB: int = 10
ALLOWED_EXTENSIONS: set = {'.pdf', '.docx', '.txt'}
```

---

## 📝 Completed Modules Detail

### ✅ utils/token_counter.py (NEW)

**4 Core Functions:**
1. `count_tokens()` - 使用tiktoken计算token数
2. `truncate_text()` - 截断文本到指定限制
3. `estimate_cost()` - API成本估算
4. `get_token_info()` - 获取完整信息（便捷函数）

**Implementation Highlights:**
- 编码器缓存（避免重复加载）
- 模型fallback（未知模型→cl100k_base）
- 价格表维护（4个主流模型）
- 截断日志（记录减少百分比）

**Testing:**
```bash
python -m utils.token_counter
```

---

### ✅ utils/text_cleaner.py

**3 Core Functions:**
- `clean_text()` - 主清洗（4个可选参数）
- `remove_html_tags()` - HTML清理
- `normalize_unicode()` - Unicode规范化

---

### ✅ utils/logger.py

**Features:**
- 彩色控制台输出
- 文件轮转（5MB × 3）
- Logger缓存

---

### ✅ models/schemas.py

**Includes:**
- 2个枚举类
- 3个子模型（WorkExperience, Project, Education）
- 4个主模型（JDInfo, ResumeInfo, GapAnalysis, Question）

---

## 🎯 Next Steps

**Current**: ✅ utils/token_counter.py completed  
**Next**: ⬜ utils/validators.py (Utilities层最后一个模块)

**After validators.py:**
1. core/parsers/ (4个文件)
2. services/llm_service.py
3. prompts/ (4个文件)
4. core/analyzers/ (3个文件)
5. core/generators/
6. app/ (Frontend)

---

## 📋 Update Log

| Version | Changes |
|---------|---------|
| 0.1.5 | ✅ Completed `utils/token_counter.py` |
| 0.1.4 | ✅ Completed `utils/text_cleaner.py` |
| 0.1.3 | ✅ Completed `utils/logger.py` |
| 0.1.2 | ✅ Completed `models/schemas.py` |
| 0.1.1 | ✅ Completed `config.py` |
| 0.1.0 | Initial documentation |

---

**Note**: This is the **single source of truth** for project structure.  
Update on every module completion or architecture change.