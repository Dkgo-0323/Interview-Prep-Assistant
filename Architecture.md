# 📐 ARCHITECTURE.md

> **Project Map & Technical Documentation**
> Last Updated: 2025-01-XX | Version: 0.4.2

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
├── 📂 prompts/                      # 🔄 75%
│   ├── 📄 __init__.py               # ✅ v0.4.2
│   ├── 📄 jd_extraction.py          # ✅ v0.4.1
│   ├── 📄 resume_extraction.py      # ✅ v0.4.2 ⭐ NEW
│   ├── 📄 gap_analysis.py           # ⬜
│   └── 📄 question_generation.py    # ⬜
├── 📂 models/
│   ├── 📄 __init__.py               # ✅
│   └── 📄 schemas.py                # ✅ v0.4.2
├── 📂 services/
│   └── 📄 llm_service.py            # ✅ v0.3.0
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
    ├── 📄 test_llm_service.py       # ✅ v0.3.0
    └── 📄 test_resume_extraction.py # ✅ v0.4.2 ⭐ NEW
```

---

## 📊 Module Status

```
✅ Foundation Layer (100%)
├── [✅] config.py
├── [✅] models/schemas.py (v0.4.2)
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

✅ Services (100%) 🎊
└── [✅] services/llm_service.py

🔄 Prompts (75%)
├── [✅] prompts/__init__.py
├── [✅] prompts/jd_extraction.py (v0.4.1)
├── [✅] prompts/resume_extraction.py (v0.4.2) ⭐ NEW
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

🔄 Tests (75%)
├── [ ] tests/fixtures/  (sample files needed)
├── [✅] tests/test_pdf_parser.py
├── [✅] tests/test_docx_parser.py
├── [✅] tests/test_parser_factory.py
├── [✅] tests/test_llm_service.py
├── [✅] tests/test_resume_extraction.py (v0.4.2) ⭐ NEW
└── [ ] tests/test_*.py (other modules)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Progress: 19/29 modules (65%)
Next Target: prompts/gap_analysis.py 🚀
```

---

## 🔌 Core API Definitions

### ✅ File Parsing Layer

```python
from core.parsers import parse_file, FileParseError, UnsupportedFileError

text = parse_file("file.pdf")  # 支持 .pdf, .docx, .txt
```

**异常:** `UnsupportedFileError` | `FileParseError`

---

### ✅ LLM Service (v0.3.0)

```python
from services.llm_service import LLMService, LLMServiceError
from models.schemas import JDInfo

llm = LLMService()

# 结构化输出
jd = llm.call(
    prompt="Extract job info:\n{text}",
    response_model=JDInfo,
    system_prompt="You are an HR analyst.",
    temperature=0.3,
)

# 纯文本输出
advice = llm.call_simple(prompt="Give interview tips", temperature=0.7)
```

**异常:** `LLMServiceError`

**自动重试:** SDK内置（网络/429/500） + 手动（解析失败一次）

---

### ✅ Prompts Layer (v0.4.2)

```python
# JD Extraction
from prompts.jd_extraction import JD_SYSTEM_PROMPT, get_jd_extraction_prompt

prompt = get_jd_extraction_prompt(jd_text)
llm.call(prompt=prompt, response_model=JDInfo, system_prompt=JD_SYSTEM_PROMPT)

# Resume Extraction ⭐ NEW
from prompts.resume_extraction import RESUME_SYSTEM_PROMPT, get_resume_extraction_prompt

prompt = get_resume_extraction_prompt(resume_text)
llm.call(prompt=prompt, response_model=ResumeInfo, system_prompt=RESUME_SYSTEM_PROMPT)
```

**设计原则:**
- 纯函数 + 常量，零依赖，零副作用
- system prompt 命名规范：`{MODULE}_SYSTEM_PROMPT`
- 缺失值策略：核心字段必填，次要字段使用 `"Not specified"` 或 `[]`

---

### ✅ Data Models (models/schemas.py v0.4.2)

**Enums:** `QuestionType` | `DifficultyLevel`

**Models:**

| Model | 核心字段 | 新增/修正 (v0.4.2) |
|-------|---------|-------------------|
| `JDInfo` | `job_title`, `required_skills`, `responsibilities` | (v0.4.1) +`company`, +`experience_required`, +`education_required` |
| `WorkExperience` | `company`, `title`, `responsibilities` | ⭐ **新增嵌套模型**<br>`start_date`, `end_date`, `achievements` |
| `Project` | `name`, `description`, `technologies` | ⭐ **新增嵌套模型**<br>`role`, `link` |
| `Education` | `institution`, `degree` | ⭐ **新增嵌套模型**<br>`field_of_study`, `graduation_date`, `gpa` |
| `ResumeInfo` | `skills`, `experiences`, `projects`, `education` | ⭐ **扩展至8字段**<br>+`summary`, +`certifications`, +`languages`, `years_of_experience` |
| `GapAnalysis` | `overall_match_score`, `matched_skills`, `missing_skills` | — |
| `Question` | `question_text`, `question_type`, `difficulty` | (v0.4.1) 拼写修正 |

---

#### 📋 ResumeInfo 完整字段列表 (8个)

```python
# === 核心字段 (4个) ===
skills: List[str]                              # 必填，可带熟练度标记
experiences: List[WorkExperience]              # 必填（应届生可为空列表）
projects: List[Project] = Field(default_factory=list)
education: List[Education]                     # 必填（至少最高学历）

# === 扩展字段 (4个) ===
summary: Optional[str] = None                  # ⭐ v0.4.2 新增（职业总结）
certifications: List[str] = Field(default_factory=list)  # ⭐ 新增（证书）
languages: List[str] = Field(default_factory=list)       # ⭐ 新增（语言能力）
years_of_experience: Optional[int] = None      # 推荐计算
```

---

#### 📋 WorkExperience Schema

```python
class WorkExperience(BaseModel):
    company: str                               # 必填
    title: str                                 # 必填
    start_date: Optional[str] = None           # 原样保留（如 "2020-01"）
    end_date: Optional[str] = None             # 原样保留（如 "Present"）
    responsibilities: List[str] = Field(default_factory=list)  # 未区分的职责
    achievements: List[str] = Field(default_factory=list)      # 量化成果
```

---

#### 📋 Project Schema

```python
class Project(BaseModel):
    name: str                                  # 必填
    description: str                           # 必填
    technologies: List[str] = Field(default_factory=list)
    role: Optional[str] = None                 # 如 "Tech Lead"
    link: Optional[str] = None                 # GitHub/Demo 链接
```

---

#### 📋 Education Schema

```python
class Education(BaseModel):
    institution: str                           # 必填
    degree: str                                # 必填（如 "Bachelor of Science"）
    field_of_study: Optional[str] = None       # 允许与 degree 冗余
    graduation_date: Optional[str] = None      # 原样保留
    gpa: Optional[str] = None                  # 如 "3.8/4.0"
```

---

### ⬜ Pending APIs

```python
# prompts/gap_analysis.py
GAP_SYSTEM_PROMPT: str
def get_gap_analysis_prompt(jd: JDInfo, resume: ResumeInfo) -> str: ...

# prompts/question_generation.py
QUESTION_SYSTEM_PROMPT: str
def get_question_generation_prompt(gap: GapAnalysis, num: int) -> str: ...

# core/analyzers/
def analyze_jd(text: str) -> JDInfo: ...
def analyze_resume(text: str) -> ResumeInfo: ...
def analyze_gap(jd: JDInfo, resume: ResumeInfo) -> GapAnalysis: ...

# core/generators/
def generate_questions(gap: GapAnalysis, num_questions: int = 10) -> List[Question]: ...
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

## 🎯 Permanent Design Decisions

### Prompts Layer (v0.4.2)
- system prompt 命名：`{MODULE}_SYSTEM_PROMPT`（如 `JD_SYSTEM_PROMPT`, `RESUME_SYSTEM_PROMPT`）
- 缺失值策略：
  - **JD:** 核心字段（`job_title`, `required_skills`, `responsibilities`）可推断，不可为空
  - **Resume:** 核心字段（`skills`, `education`）必填，`experiences` 应届生可为空列表
  - 次要字段使用 `"Not specified"` 或 `[]`
- User prompt 明确列出所有目标字段，防止 LLM 遗漏

### Data Models (v0.4.2)
- **JDInfo** (v0.4.1): 扩展支持公司、经验、教育要求
- **ResumeInfo** (v0.4.2): 新增3个嵌套模型 + 扩展至8字段
  - 嵌套模型：`WorkExperience`, `Project`, `Education`
  - 时间格式：原样保留（避免转换错误）
  - 隐私考虑：不保留 `name`/`location` 字段
  - 技能熟练度：保留原样（如 "Python (Expert)"）
  - 职责/成就区分：量化成果→`achievements`，未区分→`responsibilities`
- 所有 Optional 字段默认值为 `None`，列表字段使用 `Field(default_factory=list)`
- 字段拼写和语法严格遵守 Python/Pydantic 规范

### LLM Service (v0.3.0)
- 结构化输出使用 `beta.chat.completions.parse()`
- 统一异常 `LLMServiceError`，内部处理重试
- 日志记录元数据（token/成本/耗时），不记录敏感内容

### File Parsing (v0.2.0)
- PDF：允许混合内容，最多20页
- DOCX：保持原始顺序（段落+表格），最大50000字符
- 纯函数设计，大小写兼容

---

## 📋 Update Log

| Version | Date | Changes |
|---------|------|---------|
| **0.4.2** | **2025-01-XX** | **✅ `prompts/resume_extraction.py` + Schema 嵌套模型**<br>- 新增 `WorkExperience`, `Project`, `Education` 嵌套模型<br>- `ResumeInfo` 扩展至 8 字段（+`summary`, +`certifications`, +`languages`）<br>- 新增 `tests/test_resume_extraction.py`（17 个测试用例）<br>- 更新 `prompts/__init__.py` 导出<br>— **Prompts 75%** 🎊 |
| 0.4.1 | 2025-01-XX | 🐛 Schema 修正 + JDInfo 扩展<br>- 修复 `JDInfo` 语法错误（冒号）<br>- 新增 `company`, `experience_required`, `education_required`<br>- 修正 `QuestionType.TECHNICAL` 和 `WorkExperience.achievements` 拼写<br>- 更新 `jd_extraction.py` prompt 对齐9个字段 |
| 0.4.0 | 2025-01-XX | ✅ `prompts/jd_extraction.py` + `prompts/__init__.py` — **Prompts 50%** 🎊 |
| 0.3.0 | 2025-01-XX | ✅ `services/llm_service.py` + `test_llm_service.py` — **Services 100%** 🎊 |
| 0.2.0 | 2025-01-XX | ✅ `parser_factory.py` + `test_parser_factory.py` — **File Parsing 100%** 🎊 |
| 0.1.x | 2025-01-XX | ✅ Foundation + Utilities + Parsers |

---

## 🎉 Milestones

```
✅ v0.1.x: Foundation + Utilities (100%)
✅ v0.2.0: File Parsing Layer (100%)
✅ v0.3.0: LLM Service (100%)
🔄 v0.4.x: Prompts + Data Models Refinement (75%)  ⭐ IN PROGRESS
⬜ v0.5.x: Analyzers + Question Generator
⬜ v1.0.0: Full Application
```

---

## 🚀 Next Steps

### Immediate (Next 3 Tasks)
1. ⬜ `prompts/gap_analysis.py` 🎯 **NEXT**
2. ⬜ `core/analyzers/jd_analyzer.py`
3. ⬜ `core/analyzers/resume_analyzer.py`

### Medium Term
4. `core/analyzers/gap_analyzer.py`
5. `prompts/question_generation.py`
6. `core/generators/question_generator.py`

### Final Push
7. Streamlit UI (3 pages)
8. Integration Tests
9. Documentation + Deployment

---

> **Single source of truth** — 每次模块完成时更新。
> **Last Updated**: v0.4.2 — `prompts/resume_extraction.py` + Schema 嵌套模型扩展
> **Next**: `prompts/gap_analysis.py` 🚀