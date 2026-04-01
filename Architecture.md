# 📐 ARCHITECTURE.md

> **Project Map & Technical Documentation**
> Last Updated: 2025-01-XX | Version: 0.3.0

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
│   │   ├── 📄 __init__.py           # ✅ v0.2.0
│   │   ├── 📄 exceptions.py         # ✅
│   │   ├── 📄 txt_parser.py         # ✅
│   │   ├── 📄 pdf_parser.py         # ✅
│   │   ├── 📄 docx_parser.py        # ✅
│   │   └── 📄 parser_factory.py     # ✅ v0.2.0
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
│   └── 📄 llm_service.py            # ✅ NEW v0.3.0
├── 📂 utils/
│   ├── 📄 logger.py                 # ✅
│   ├── 📄 text_cleaner.py           # ✅
│   ├── 📄 token_counter.py          # ✅
│   └── 📄 validators.py             # ✅
└── 📂 tests/
    ├── 📂 fixtures/                 # ⬜ Test files
    │   └── 📄 .gitkeep
    ├── 📄 test_pdf_parser.py        # ✅
    ├── 📄 test_docx_parser.py       # ✅
    ├── 📄 test_parser_factory.py    # ✅
    └── 📄 test_llm_service.py       # ✅ NEW v0.3.0
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

✅ File Parsing (100%) 🎊
├── [✅] core/parsers/__init__.py
├── [✅] core/parsers/exceptions.py
├── [✅] core/parsers/txt_parser.py
├── [✅] core/parsers/pdf_parser.py
├── [✅] core/parsers/docx_parser.py
└── [✅] core/parsers/parser_factory.py

✅ Services (100%) 🎊 NEW!
└── [✅] services/llm_service.py  ⭐ NEW

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

🔄 Tests (70%)
├── [ ] tests/fixtures/  (sample files needed)
├── [✅] tests/test_pdf_parser.py
├── [✅] tests/test_docx_parser.py
├── [✅] tests/test_parser_factory.py
├── [✅] tests/test_llm_service.py  ⭐ NEW
└── [ ] tests/test_*.py (other modules)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Progress: 16/29 modules (55%)
Next Target: prompts/jd_extraction.py 🚀
```

---

## 🔌 Core API Definitions

### 🎯 Parsing Layer Universal Contract

**核心原则：** 所有解析器 100% 可互换
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

### ✅ core/parsers/parser_factory.py

```python
def parse_file(file_path: str | Path) -> str:
```

**处理流程:**
```
file_path → Path化 → suffix.lower() → 查PARSER_MAP
    → 找不到 → UnsupportedFileError
    → 找到   → 调用对应解析器 → 返回str
```

**异常:** 
- `UnsupportedFileError`: 不支持的文件格式
- `FileParseError`: 解析失败（从底层解析器传递）

---

### ✅ core/parsers/__init__.py (v0.2.0)

```python
from core.parsers.exceptions import FileParseError, UnsupportedFileError
from core.parsers.txt_parser import parse_txt
from core.parsers.pdf_parser import parse_pdf
from core.parsers.docx_parser import parse_docx
from core.parsers.parser_factory import parse_file

__all__ = [
    "FileParseError",
    "UnsupportedFileError",
    "parse_txt",
    "parse_pdf",
    "parse_docx",
    "parse_file",  # ⭐ 推荐使用的统一入口
]
```

---

### ✅ services/llm_service.py ⭐ NEW (v0.3.0)

```python
class LLMServiceError(Exception):
    """LLM 服务调用失败（网络/认证/解析等）"""

class LLMService:
    """LLM 服务封装类"""
    
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        max_retries: int = 3,
        timeout: float = 60.0,
    ) -> None:
        """初始化 LLM 服务"""
    
    def call(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: str = "You are a helpful assistant.",
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> T:
        """调用 LLM 并返回结构化数据（Pydantic 模型）"""
    
    def call_simple(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """调用 LLM 并返回纯文本响应"""
```

**处理流程（call）:**
```
prompt + response_model → 构建messages → beta.chat.completions.parse()
    → 解析失败 → 重试一次 → 仍失败 → LLMServiceError
    → 成功     → 记录token使用/成本 → 返回Pydantic对象
```

**处理流程（call_simple）:**
```
prompt → 构建messages → chat.completions.create()
    → 失败 → LLMServiceError
    → 成功 → 记录token使用/成本 → 返回str
```

**异常:** `LLMServiceError`

**自动重试:**
- SDK内置：网络错误、429限流、500/503服务错误（指数退避）
- 手动：解析失败重试一次（仅针对结构化输出）

**日志记录:**
- ✅ 模型名称、token数、成本、耗时
- ❌ 完整prompt/响应内容、API Key

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
# prompts/jd_extraction.py
def get_jd_extraction_prompt(text: str) -> str: ...
SYSTEM_PROMPT: str

# prompts/resume_extraction.py
def get_resume_extraction_prompt(text: str) -> str: ...
SYSTEM_PROMPT: str

# prompts/gap_analysis.py
def get_gap_analysis_prompt(jd: JDInfo, resume: ResumeInfo) -> str: ...
SYSTEM_PROMPT: str

# prompts/question_generation.py
def get_question_generation_prompt(gap: GapAnalysis, num: int) -> str: ...
SYSTEM_PROMPT: str

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
validators ✅ → parse_file() ✅
    ↓
┌─────────────────────────────────┐
│ parse_txt() ✅ / parse_pdf() ✅ │
│ / parse_docx() ✅               │
└─────────────────────────────────┘
    ↓
clean_text() ✅ → validators(内容) ✅ → token_counter ✅
    ↓                           ↓
jd_analyzer ⬜              resume_analyzer ⬜
    ↓                           ↓
    ├→ jd_extraction_prompt ⬜  ├→ resume_extraction_prompt ⬜
    ↓                           ↓
    └→ LLMService.call() ✅     └→ LLMService.call() ✅
    ↓                           ↓
JDInfo ✅                   ResumeInfo ✅
    └──────────┬────────────────┘
           gap_analyzer ⬜
               ↓
           gap_analysis_prompt ⬜
               ↓
           LLMService.call() ✅
               ↓
          GapAnalysis ✅
               ↓
       question_generator ⬜
               ↓
       question_generation_prompt ⬜
               ↓
       LLMService.call() ✅
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
| `openai` | 1.55.0 | OpenAI API | ✅ |
| `tiktoken` | 0.8.0 | Token counting | ✅ |
| `pydantic` | 2.10.2 | Data validation | ✅ |

---

## ⚙️ Configuration

```python
# config.py
PROJECT_ROOT: Path
UPLOAD_DIR: Path
OPENAI_API_KEY: str
MODEL_NAME: str = "gpt-4o-mini"
TEMPERATURE: float = 0.7
MAX_TOKENS: int = 2000
UPLOAD_MAX_SIZE_MB: int = 10
ALLOWED_EXTENSIONS: set = {'.pdf', '.docx', '.txt'}
```

---

## 📌 Quick Reference

### File Parsing

```python
from core.parsers import parse_file, FileParseError, UnsupportedFileError

try:
    text = parse_file("resume.pdf")  # 自动识别格式
except UnsupportedFileError:
    # 不支持的格式
except FileParseError:
    # 解析失败
```

### LLM Service ⭐ NEW

```python
from services.llm_service import LLMService, LLMServiceError
from models.schemas import JDInfo

# 初始化（应用启动时创建单例）
llm = LLMService()

# 结构化调用
try:
    jd = llm.call(
        prompt=f"Extract job info:\n{text}",
        response_model=JDInfo,
        system_prompt="You are an HR analyst.",
        temperature=0.3,
    )
except LLMServiceError as e:
    # 处理LLM调用失败
    pass

# 纯文本调用
advice = llm.call_simple(
    prompt="Give interview tips",
    temperature=0.7,
)
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

### Parser Factory (v0.2.0)
1. **纯函数设计**：不使用类，没有插件机制需求
2. **纯路由职责**：只负责分发，验证由调用者决定
3. **自检后缀**：对不支持格式自己抛 `UnsupportedFileError`
4. **大小写兼容**：统一转小写匹配 `.PDF` `.Docx` `.TxT`
5. **PARSER_MAP 私有**：实现细节不暴露

### LLM Service (v0.3.0) ⭐ NEW
1. **类封装**：可复用实例，应用启动时创建单例
2. **结构化输出**：使用 `beta.chat.completions.parse()` 直接返回 Pydantic 对象
3. **统一异常**：所有错误统一为 `LLMServiceError`，内部处理重试
4. **SDK内置重试**：`OpenAI(max_retries=3)` 自动处理网络/限流/服务错误
5. **解析失败重试**：结构化输出解析失败时手动重试一次
6. **日志策略**：记录元数据（token/成本/耗时），不记录敏感内容
7. **两种调用模式**：
   - `call()`: 结构化输出（返回 Pydantic 模型）
   - `call_simple()`: 纯文本输出（返回 str）
8. **参数可覆盖**：temperature/max_tokens 可在调用时覆盖默认值
9. **线程安全**：OpenAI client 本身线程安全，可在多线程环境使用

---

## 🧪 Testing

### Test Coverage
```
✅ tests/test_pdf_parser.py
✅ tests/test_docx_parser.py
✅ tests/test_parser_factory.py
✅ tests/test_llm_service.py  ⭐ NEW
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
| 0.3.0 | 2025-01-XX | ✅ `services/llm_service.py` + `test_llm_service.py` — **Services 100%** 🎊 |
| 0.2.0 | 2025-01-XX | ✅ `parser_factory.py` + `test_parser_factory.py` — **File Parsing 100%** 🎊 |
| 0.1.9 | 2025-01-XX | ✅ `core/parsers/docx_parser.py` + `test_docx_parser.py` |
| 0.1.8 | 2025-01-XX | ✅ `core/parsers/pdf_parser.py` + `test_pdf_parser.py` |
| 0.1.7 | 2025-01-XX | ✅ `core/parsers/exceptions.py` + `txt_parser.py` |
| 0.1.6 | 2025-01-XX | ✅ `utils/validators.py` — **Utilities 100%** 🎊 |
| 0.1.5 | 2025-01-XX | ✅ `utils/token_counter.py` |
| 0.1.4 | 2025-01-XX | ✅ `utils/text_cleaner.py` |
| 0.1.3 | 2025-01-XX | ✅ `utils/logger.py` |
| 0.1.2 | 2025-01-XX | ✅ `models/schemas.py` |
| 0.1.1 | 2025-01-XX | ✅ `config.py` |

---

## 🎉 Milestones

```
✅ v0.1.x: Foundation + Utilities (100%)
✅ v0.2.0: File Parsing Layer (100%)
✅ v0.3.0: LLM Service (100%)  ⭐ NEW!
⬜ v0.4.x: Prompts + Analyzers
⬜ v0.5.x: Question Generator
⬜ v1.0.0: Full Application
```

---

## 🚀 Next Steps

### Immediate (v0.4.0)
1. `prompts/jd_extraction.py` — JD提取的prompt模板
2. `prompts/resume_extraction.py` — 简历提取的prompt模板
3. `core/analyzers/jd_analyzer.py` — 调用LLMService分析JD
4. `core/analyzers/resume_analyzer.py` — 调用LLMService分析简历

### After That (v0.4.1)
5. `prompts/gap_analysis.py` — 差距分析的prompt模板
6. `core/analyzers/gap_analyzer.py` — 调用LLMService进行差距分析

### Then (v0.5.0)
7. `prompts/question_generation.py` — 问题生成的prompt模板
8. `core/generators/question_generator.py` — 调用LLMService生成面试问题

### Finally (v1.0.0)
9. `app/` — Streamlit UI
10. 集成测试 + 文档完善

---

> **Single source of truth** — update on every module completion.
> **Next**: `prompts/jd_extraction.py` 🚀