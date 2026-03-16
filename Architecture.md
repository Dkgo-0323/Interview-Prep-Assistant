# 📐 ARCHITECTURE.md

> **Project Map & Technical Documentation**  
> Last Updated: 2025-01-XX | Version: 0.1.6

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
│   └── 📄 validators.py             # ✅ Input validation
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

✅ Utilities (100%) 🎊
├── [✅] utils/logger.py              - Logging system
├── [✅] utils/text_cleaner.py        - Text preprocessing
├── [✅] utils/token_counter.py       - Token management
└── [✅] utils/validators.py          - Input validation ⭐ NEW

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
Overall Progress: 7/25 modules (28%)
Next Target: core/parsers/ (4 files)
```

---

## 🔌 Core API Definitions

### **✅ utils/validators.py** (NEW - v0.1.6)

```python
def validate_file_extension(filename: str) -> Tuple[bool, str]:
    """验证文件扩展名是否在允许列表中"""

def validate_file_size(file_size: int) -> Tuple[bool, str]:
    """验证文件大小是否在限制内（输入单位: bytes）"""

def validate_text_content(
    text: str, 
    content_type: str = "general"  # "jd" | "resume" | "general"
) -> Tuple[bool, str]:
    """验证文本内容有效性（最小长度: JD=100, resume=50）"""

def validate_upload(
    filename: str, 
    file_size: int
) -> Tuple[bool, List[str]]:
    """聚合验证：一次性验证文件名+大小"""
```

**Usage:**
```python
from utils.validators import validate_upload, validate_text_content

# 文件上传验证
is_valid, errors = validate_upload("resume.pdf", 2_000_000)
if not is_valid:
    for error in errors:
        print(f"❌ {error}")

# 文本内容验证
is_valid, msg = validate_text_content(extracted_text, content_type="resume")
if not is_valid:
    raise ValueError(msg)
```

**Features:**
- ✅ 统一返回格式 `Tuple[bool, str]`
- ✅ 扩展名大小写不敏感（`.PDF` → `.pdf`）
- ✅ 文件大小单位: bytes（与 Streamlit 一致）
- ✅ 内容类型区分（JD=100字符，resume=50字符）
- ✅ 聚合验证函数（收集所有错误）
- ✅ 完整日志记录

**Testing:**
```bash
python -m utils.validators
```

---

### **✅ utils/token_counter.py**

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
validators (文件验证) ✅
    ↓
parser_factory → Raw Text
    ↓
text_cleaner → Cleaned Text ✅
    ↓
validators (内容验证) ✅
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

### ✅ utils/validators.py (NEW - v0.1.6)

**4 Core Functions:**
1. `validate_file_extension()` - 扩展名白名单验证
2. `validate_file_size()` - 文件大小限制检查
3. `validate_text_content()` - 文本有效性验证（区分JD/resume）
4. `validate_upload()` - 聚合验证（文件名+大小）

**Implementation Highlights:**
- 统一返回 `Tuple[bool, str]`（前三个函数）
- 聚合函数返回 `Tuple[bool, List[str]]`（收集所有错误）
- 扩展名大小写不敏感
- 内容类型区分（JD=100, resume=50, general=50）
- 完整边界情况处理

**Validation Rules:**
```python
# 文件扩展名
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}

# 文件大小
MAX_SIZE = 10MB (10 * 1024 * 1024 bytes)
MIN_SIZE = 1 byte (拒绝空文件)

# 文本长度
MIN_LENGTH = {
    "jd": 100,       # 职位描述
    "resume": 50,    # 简历
    "general": 50    # 通用
}
```

**Testing:**
```bash
python -m utils.validators

# 测试覆盖:
# - 8 种文件扩展名场景
# - 7 种文件大小场景
# - 8 种文本内容场景
# - 6 种聚合验证场景
```

---

### ✅ utils/token_counter.py

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

**🎊 MILESTONE: Utilities Layer 100% Complete!**

**Current**: ✅ utils/validators.py completed  
**Next**: ⬜ core/parsers/ (进入核心业务逻辑层)

**Parsers 模块优先级（按依赖关系）：**
1. `txt_parser.py` - 最简单，无外部依赖
2. `pdf_parser.py` - 依赖 pdfplumber
3. `docx_parser.py` - 依赖 python-docx
4. `parser_factory.py` - 依赖前三个解析器（工厂模式）

**After parsers/:**
1. services/llm_service.py
2. prompts/ (4个文件)
3. core/analyzers/ (3个文件)
4. core/generators/
5. app/ (Frontend)

---

## 📋 Update Log

| Version | Changes |
|---------|---------|
| 0.1.6 | ✅ Completed `utils/validators.py` - **Utilities 100%** 🎊 |
| 0.1.5 | ✅ Completed `utils/token_counter.py` |
| 0.1.4 | ✅ Completed `utils/text_cleaner.py` |
| 0.1.3 | ✅ Completed `utils/logger.py` |
| 0.1.2 | ✅ Completed `models/schemas.py` |
| 0.1.1 | ✅ Completed `config.py` |
| 0.1.0 | Initial documentation |

---

## 🏆 Phase Completion Status

```
Phase 1 - Foundation & Utilities
├── [100%] Foundation Layer
│   ├── ✅ config.py
│   ├── ✅ models/schemas.py
│   └── ✅ models/__init__.py
│
└── [100%] Utilities Layer  🎊🎊🎊
    ├── ✅ utils/logger.py
    ├── ✅ utils/text_cleaner.py
    ├── ✅ utils/token_counter.py
    └── ✅ utils/validators.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Phase 2 - File Parsing [0%]
└── [ ] core/parsers/ (4 files) ← NEXT
```

---

**Note**: This is the **single source of truth** for project structure.  
Update on every module completion or architecture change.

---

## 📌 Quick Reference

### Completed Utilities APIs

```python
# 日志
from utils.logger import get_logger
logger = get_logger(__name__)

# 文本清洗
from utils.text_cleaner import clean_text
text = clean_text(raw_text)

# Token计数
from utils.token_counter import count_tokens, truncate_text
tokens = count_tokens(text)
text = truncate_text(text, max_tokens=4000)

# 验证
from utils.validators import validate_upload, validate_text_content
is_valid, errors = validate_upload(filename, file_size)
is_valid, msg = validate_text_content(text, content_type="jd")
```

### Module Import Pattern

```python
# ✅ Recommended
from utils.logger import get_logger
from utils.validators import validate_upload
from models.schemas import JDInfo, ResumeInfo

# ❌ Avoid
from utils import *
import utils.logger as logger
```

---

**Ready for Phase 2: File Parsing Layer** 🚀