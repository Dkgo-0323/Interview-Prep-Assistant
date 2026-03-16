# 📐 ARCHITECTURE.md

> **Project Map & Technical Documentation**
> Last Updated: 2025-01-XX | Version: 0.1.7

---

## 🎯 Project Overview

**Name**: Interview Prep Assistant
**Purpose**: AI-powered personalized interview preparation tool
**Tech Stack**: Python 3.9+, Streamlit, OpenAI GPT-4o-mini

---

## 📂 Directory Structure

```
interview-prep-assistant/
├── 📄 config.py                     # ✅
├── 📂 app/                          # ⬜ Frontend (Streamlit)
│   ├── 📄 main.py
│   └── 📂 pages/
│       ├── 📄 01_upload.py
│       ├── 📄 02_analysis.py
│       └── 📄 03_questions.py
├── 📂 core/
│   ├── 📂 parsers/
│   │   ├── 📄 exceptions.py         # ✅ NEW
│   │   ├── 📄 txt_parser.py         # ✅ NEW
│   │   ├── 📄 pdf_parser.py         # ⬜
│   │   ├── 📄 docx_parser.py        # ⬜
│   │   └── 📄 parser_factory.py     # ⬜
│   ├── 📂 analyzers/
│   │   ├── 📄 jd_analyzer.py        # ⬜
│   │   ├── 📄 resume_analyzer.py    # ⬜
│   │   └── 📄 gap_analyzer.py       # ⬜
│   └── 📂 generators/
│       └── 📄 question_generator.py # ⬜
├── 📂 prompts/                      # ⬜
│   ├── 📄 jd_extraction.py
│   ├── 📄 resume_extraction.py
│   ├── 📄 gap_analysis.py
│   └── 📄 question_generation.py
├── 📂 models/
│   ├── 📄 __init__.py               # ✅
│   └── 📄 schemas.py                # ✅
├── 📂 services/
│   └── 📄 llm_service.py            # ⬜
└── 📂 utils/
    ├── 📄 logger.py                 # ✅
    ├── 📄 text_cleaner.py           # ✅
    ├── 📄 token_counter.py          # ✅
    └── 📄 validators.py             # ✅
```

---

## 📊 Module Status

```
✅ Foundation Layer (100%)
├── [✅] config.py
├── [✅] models/schemas.py
└── [✅] models/__init__.py

✅ Utilities (100%) 🎊
├── [✅] utils/logger.py
├── [✅] utils/text_cleaner.py
├── [✅] utils/token_counter.py
└── [✅] utils/validators.py

🔄 File Parsing (50%)
├── [✅] core/parsers/exceptions.py  ⭐ NEW
├── [✅] core/parsers/txt_parser.py  ⭐ NEW
├── [ ] core/parsers/pdf_parser.py
├── [ ] core/parsers/docx_parser.py
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
Overall Progress: 9/27 modules (33%)
Next Target: pdf_parser.py → docx_parser.py → parser_factory.py
```

---

## 🔌 Core API Definitions

### ✅ core/parsers/exceptions.py

```python
class FileParseError(Exception):
    """文件解析失败（损坏/加密/空文件等）"""

class UnsupportedFileError(FileParseError):
    """不支持的文件格式"""
```

---

### ✅ core/parsers/txt_parser.py

```python
def parse_txt(file_path: str | Path) -> str:
    """解析 TXT 文件，自动检测编码，返回清洗后文本"""
```

**处理流程:**
```
file_path → Path对象 → 存在性检查 → 读取raw_bytes
→ 空文件检查 → chardet编码检测 → decode(fallback: utf-8 errors=ignore)
→ clean_text() → 空文本检查 → 返回 cleaned_text
```

**异常:** `FileParseError` (文件不存在 / 空文件 / 清理后为空)

**依赖:** `chardet`, `utils.text_cleaner.clean_text`, `utils.logger`

---

### ✅ utils/validators.py

```python
def validate_file_extension(filename: str) -> Tuple[bool, str]: ...
def validate_file_size(file_size: int) -> Tuple[bool, str]: ...
def validate_text_content(text: str, content_type: str = "general") -> Tuple[bool, str]: ...
def validate_upload(filename: str, file_size: int) -> Tuple[bool, List[str]]: ...
```

**Rules:** 扩展名 `{.pdf/.docx/.txt}` | 大小 `1B ~ 10MB` | 最小长度 `JD=100 / resume=50`

---

### ✅ utils/token_counter.py

```python
def count_tokens(text: str, model: str = MODEL_NAME) -> int: ...
def truncate_text(text: str, max_tokens: int, ...) -> str: ...
def estimate_cost(num_tokens: int, model: str, cost_type: str) -> float: ...
def get_token_info(text: str, model: str) -> Dict: ...
```

---

### ✅ utils/text_cleaner.py

```python
def clean_text(text: str, remove_extra_whitespace=True,
               normalize_line_breaks=True, remove_special_chars=False,
               lowercase=False) -> str: ...
def remove_html_tags(text: str) -> str: ...
def normalize_unicode(text: str) -> str: ...
```

---

### ✅ utils/logger.py

```python
def get_logger(name: str) -> Logger: ...
```

---

### ✅ models/schemas.py

**Enums:** `QuestionType` | `DifficultyLevel`
**Models:** `JDInfo` | `ResumeInfo` | `GapAnalysis` | `Question`
**Sub-models:** `WorkExperience` | `Project` | `Education`

---

### ⬜ Pending APIs

```python
# pdf_parser.py
def parse_pdf(file_path: str | Path) -> str: ...

# docx_parser.py
def parse_docx(file_path: str | Path) -> str: ...

# parser_factory.py
def parse_file(file_path: str | Path) -> str: ...

# llm_service.py
def call_llm(prompt: str, response_model: Type[T], **kwargs) -> T: ...

# analyzers
def analyze_jd(text: str) -> JDInfo: ...
def analyze_resume(text: str) -> ResumeInfo: ...
def analyze_gap(jd: JDInfo, resume: ResumeInfo) -> GapAnalysis: ...

# generator
def generate_questions(gap: GapAnalysis, num_questions: int = 10) -> List[Question]: ...
```

---

## 🔄 Data Flow

```
User Upload (JD + Resume)
    ↓
validators ✅ → parse_file() ⬜
    ↓
clean_text() ✅ → validators(内容) ✅ → token_counter ✅
    ↓                    ↓
jd_analyzer ⬜    resume_analyzer ⬜
    ↓                    ↓
JDInfo ✅          ResumeInfo ✅
    └────────┬───────────┘
         gap_analyzer ⬜
             ↓
        GapAnalysis ✅
             ↓
     question_generator ⬜
             ↓
      List[Question] ✅
             ↓
       Streamlit UI ⬜
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

```python
# config.py
PROJECT_ROOT: Path
UPLOAD_DIR: Path
OPENAI_API_KEY: str
MODEL_NAME: str
TEMPERATURE: float = 0.7
MAX_TOKENS: int = 2000
UPLOAD_MAX_SIZE_MB: int = 10
ALLOWED_EXTENSIONS: set = {'.pdf', '.docx', '.txt'}
```

```env
# .env
OPENAI_API_KEY=sk-...
MODEL_NAME=gpt-4o-mini
DEBUG=False
LOG_LEVEL=INFO
```

---

## 📌 Quick Reference

```python
# Logger
from utils.logger import get_logger
logger = get_logger(__name__)

# Text
from utils.text_cleaner import clean_text
from utils.token_counter import count_tokens, truncate_text

# Validation
from utils.validators import validate_upload, validate_text_content

# Parsing ✅
from core.parsers.txt_parser import parse_txt
from core.parsers.exceptions import FileParseError, UnsupportedFileError

# Parsing ⬜ (coming soon)
from core.parsers.parser_factory import parse_file
```

---

## 📋 Update Log

| Version | Changes |
|---------|---------|
| 0.1.7 | ✅ `core/parsers/exceptions.py` + `txt_parser.py` |
| 0.1.6 | ✅ `utils/validators.py` — Utilities 100% 🎊 |
| 0.1.5 | ✅ `utils/token_counter.py` |
| 0.1.4 | ✅ `utils/text_cleaner.py` |
| 0.1.3 | ✅ `utils/logger.py` |
| 0.1.2 | ✅ `models/schemas.py` |
| 0.1.1 | ✅ `config.py` |

---

> **Single source of truth** — update on every module completion.
> **Next**: `pdf_parser.py` 🚀