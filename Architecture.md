✅ 已完整更新 ARCHITECTURE.md 到版本 0.1.9。所有设计决策、模块状态和契约都已经正式记录为单一可信源。所有本次讨论达成的决定现在都已经永久写入架构文档，未来任何开发者或者LLM都可以从这个文档获得完整准确的项目状态。


---

# 📐 ARCHITECTURE.md

> **Project Map & Technical Documentation**
> Last Updated: 2025-01-XX | Version: 0.1.9


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
│   │   ├── 📄 __init__.py           # ✅ UPDATED
│   │   ├── 📄 exceptions.py         # ✅
│   │   ├── 📄 txt_parser.py         # ✅
│   │   ├── 📄 pdf_parser.py         # ✅
│   │   ├── 📄 docx_parser.py        # ✅ NEW
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
├── 📂 utils/
│   ├── 📄 logger.py                 # ✅
│   ├── 📄 text_cleaner.py           # ✅
│   ├── 📄 token_counter.py          # ✅
│   └── 📄 validators.py             # ✅
└── 📂 tests/
    ├── 📂 fixtures/                 # ⬜ Test files
    │   └── 📄 .gitkeep
    ├── 📄 test_pdf_parser.py        # ✅
    └── 📄 test_docx_parser.py       # ✅ NEW
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

🔄 File Parsing (80%)
├── [✅] core/parsers/__init__.py
├── [✅] core/parsers/exceptions.py
├── [✅] core/parsers/txt_parser.py
├── [✅] core/parsers/pdf_parser.py
├── [✅] core/parsers/docx_parser.py   ⭐ NEW
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

🔄 Tests (50%)
├── [ ] tests/fixtures/  (sample files needed)
├── [✅] tests/test_pdf_parser.py
├── [✅] tests/test_docx_parser.py     ⭐ NEW
└── [ ] tests/test_*.py (other modules)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Progress: 13/29 modules (45%)
Next Target: parser_factory.py 🚀
```


---

## 🔌 Core API Definitions

### 🎯 Parsing Layer Universal Contract
所有三个解析器100%可互换，这是整个解析层的核心设计原则：
* 完全相同的函数签名
* 完全相同的输出格式
* 完全相同的异常类型
* 对于调用者完全透明，永远不需要知道文本来自什么格式


---

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
```

**处理流程:**
```
file_path → 存在性检查 → 编码检测 → decode → clean_text → 空文本检查 → 返回
```

**异常:** `FileParseError`


---

### ✅ core/parsers/pdf_parser.py

```python
def parse_pdf(file_path: str | Path) -> str:
```

**处理流程:**
```
file_path → 存在性检查 → 打开PDF → 最多20页 → 扫描件检测 → clean_text → 返回
```

**异常:** `FileParseError`

**常量:**
```python
MAX_PAGES = 20
SCANNED_PAGE_TEXT_THRESHOLD = 50
```


---

### ✅ core/parsers/docx_parser.py

```python
def parse_docx(file_path: str | Path) -> str:
```

**处理流程:**
```
file_path → 存在性检查 → 打开DOCX → 遍历XML保持原始顺序 → 提取段落和表格 → 制表符分隔表格 → 字符数限制 → clean_text → 返回
```

**异常:** `FileParseError`

**常量:**
```python
MAX_CHARACTERS = 50000
```


---

### ✅ core/parsers/__init__.py

```python
from core.parsers.exceptions import FileParseError, UnsupportedFileError
from core.parsers.txt_parser import parse_txt
from core.parsers.pdf_parser import parse_pdf
from core.parsers.docx_parser import parse_docx

__all__ = [
    "FileParseError",
    "UnsupportedFileError",
    "parse_txt",
    "parse_pdf",
    "parse_docx",
]
```


---

### ✅ All Utility Modules
所有工具模块100%完成并稳定，API不会变更。

```python
# utils/validators.py
validate_file_extension()
validate_file_size()
validate_text_content()
validate_upload()

# utils/token_counter.py
count_tokens()
truncate_text()
estimate_cost()

# utils/text_cleaner.py
clean_text()

# utils/logger.py
get_logger()
```


---

### ✅ models/schemas.py

**Enums:** `QuestionType` | `DifficultyLevel`
**Models:** `JDInfo` | `ResumeInfo` | `GapAnalysis` | `Question`


---

### ⬜ Pending APIs

```python
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
┌─────────────────────────────────┐
│ parse_txt() ✅ / parse_pdf() ✅ │
│ / parse_docx() ✅               │
└─────────────────────────────────┘
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

| Package | Version | Purpose | Status |
|---------|---------|---------|--------|
| `streamlit` | 1.40.0 | Web UI | ⬜ |
| `python-dotenv` | 1.0.1 | Env vars | ✅ |
| `pdfplumber` | 0.11.4 | PDF parsing | ✅ |
| `python-docx` | 1.1.2 | DOCX parsing | ✅ |
| `chardet` | 5.2.0 | Encoding detection | ✅ |
| `openai` | 1.55.0 | OpenAI API | ⬜ |
| `tiktoken` | 0.8.0 | Token counting | ✅ |
| `pydantic` | 2.10.2 | Data validation | ✅ |


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


---

## 📌 Quick Reference

```python
# File Parsing ✅
from core.parsers import FileParseError, parse_txt, parse_pdf, parse_docx

# File Parsing ⬜
from core.parsers import parse_file
```


---

## 🎯 Permanent Design Decisions

这些是已经最终确定的架构决策，不需要重新讨论：

### PDF Parser (v0.1.8)
1. 仅当所有页均为扫描页时才报错，允许混合内容PDF
2. 默认不保留布局，避免多栏文档混乱
3. 最多处理20页

### DOCX Parser (v0.1.9)
1. 遍历底层XML保持段落和表格的原始顺序
2. 表格单元格用制表符分隔
3. 忽略页眉、页脚、文本框和嵌套表格
4. 最大字符数限制50000，约等于20页
5. 超过限制时截断并记录warning，不抛出异常
6. 正确检测加密DOCX并返回有意义的错误消息


---

## 🧪 Testing

### Test Coverage
```
✅ tests/test_pdf_parser.py
✅ tests/test_docx_parser.py
```

### Test Fixtures Needed
```
tests/fixtures/
├── sample_resume.pdf
├── sample_resume.docx
├── encrypted.pdf
├── encrypted.docx
└── scanned.pdf
```


---

## 📋 Update Log

| Version | Date | Changes |
|---------|------|---------|
| 0.1.9 | 2025-01-XX | ✅ `core/parsers/docx_parser.py` + `test_docx_parser.py` + 更新解析层统一契约 |
| 0.1.8 | 2025-01-XX | ✅ `core/parsers/pdf_parser.py` + `test_pdf_parser.py` |
| 0.1.7 | 2025-01-XX | ✅ `core/parsers/exceptions.py` + `txt_parser.py` |
| 0.1.6 | 2025-01-XX | ✅ `utils/validators.py` — Utilities 100% 🎊 |
| 0.1.5 | 2025-01-XX | ✅ `utils/token_counter.py` |
| 0.1.4 | 2025-01-XX | ✅ `utils/text_cleaner.py` |
| 0.1.3 | 2025-01-XX | ✅ `utils/logger.py` |
| 0.1.2 | 2025-01-XX | ✅ `models/schemas.py` |
| 0.1.1 | 2025-01-XX | ✅ `config.py` |


---

> **Single source of truth** — update on every module completion.
> **Next**: `parser_factory.py` 🚀