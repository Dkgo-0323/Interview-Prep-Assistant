下面是我建议更新后的 **ARCHITECTURE.md** 内容，已纳入你们刚刚完成/明确的两项 Analyzer 设计、异常层、以及关键 Schema 蓝图，目的是让它真正成为后续开发的 **single source of truth**，减少字段名漂移和“模型幻觉”。

你可以直接替换原文对应部分，或整体覆盖。

---

# 📐 ARCHITECTURE.md

> **Project Map & Technical Documentation**  
> Last Updated: 2025-01-XX | Version: 0.4.5

-----

## 🎯 Project Overview

**Name**: Interview Prep Assistant  
**Purpose**: AI-powered personalized interview preparation tool  
**Tech Stack**: Python 3.9+, Streamlit, OpenAI GPT-4o-mini

-----

## 📂 Directory Structure

```text
interview-prep-assistant/
├── 📄 config.py                          # ✅
├── 📂 app/                               # ⬜ Frontend (Streamlit)
│   ├── 📄 main.py
│   └── 📂 pages/
│       ├── 📄 01_upload.py
│       ├── 📄 02_analysis.py
│       └── 📄 03_questions.py
├── 📂 core/
│   ├── 📂 parsers/                       # ✅ Parsing Layer (100%)
│   ├── 📂 analyzers/                     # 🔄 In Progress
│   │   ├── 📄 exceptions.py             # ✅ NEW v0.4.5
│   │   ├── 📄 jd_analyzer.py            # ✅ v0.4.5
│   │   ├── 📄 resume_analyzer.py        # ✅ v0.4.5
│   │   └── 📄 gap_analyzer.py           # ⬜ NEXT
│   └── 📂 generators/
│       └── 📄 question_generator.py     # ⬜
├── 📂 prompts/                           # ✅ Prompts Layer (100%)
│   ├── 📄 __init__.py                    # ✅ v0.4.3
│   ├── 📄 jd_extraction.py               # ✅ v0.4.1
│   ├── 📄 resume_extraction.py           # ✅ v0.4.2
│   ├── 📄 gap_analysis.py                # ✅ v0.4.3
│   └── 📄 question_generation.py         # ✅ v0.4.4
├── 📂 models/
│   ├── 📄 __init__.py                    # ✅
│   └── 📄 schemas.py                     # ✅ v0.4.4
├── 📂 services/
│   └── 📄 llm_service.py                 # ✅ v0.3.0
├── 📂 utils/                             # ✅ Utils Layer (100%)
└── 📂 tests/
    ├── 📄 test_jd_analyzer.py            # ✅ NEW v0.4.5
    ├── 📄 test_resume_analyzer.py        # ✅ NEW v0.4.5
    ├── 📄 test_question_generation.py    # ⬜ 待补充测试
    ├── 📄 test_gap_analysis.py           # ✅ v0.4.3
    ├── 📄 test_resume_extraction.py      # ✅ v0.4.2
    ├── 📄 test_parser_factory.py         # ✅
    ├── 📄 test_llm_service.py            # ✅
    └── 📄 test_*.py                      # ⬜ (other modules)
```

-----

## 📊 Module Status

```text
✅ Foundation Layer (100%)
✅ Utilities (100%)
✅ File Parsing (100%)
✅ Services (100%)
✅ Prompts (100%)
├── [✅] prompts/__init__.py
├── [✅] prompts/jd_extraction.py
├── [✅] prompts/resume_extraction.py
├── [✅] prompts/gap_analysis.py
└── [✅] prompts/question_generation.py

🔄 Analyzers (67%) 🎯 IN PROGRESS
├── [✅] core/analyzers/exceptions.py
├── [✅] core/analyzers/jd_analyzer.py
├── [✅] core/analyzers/resume_analyzer.py
└── [ ] core/analyzers/gap_analyzer.py   # NEXT

⬜ Generators (0%)
└── [ ] core/generators/question_generator.py

⬜ Frontend (0%)
└── [ ] app/ & pages/

🔄 Tests (79%)
├── [✅] tests/test_jd_analyzer.py
├── [✅] tests/test_resume_analyzer.py
├── [ ] tests/test_question_generation.py
└── [ ] 待补全其余业务逻辑测试

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Progress: 25/31 modules (81%)
Next Target: core/analyzers/gap_analyzer.py 🚀
```

> 注：总模块数因新增 `core/analyzers/exceptions.py`、`tests/test_jd_analyzer.py`、`tests/test_resume_analyzer.py` 而上升。

-----

## 🔌 Core API Definitions

### ✅ Analyzer Layer (v0.4.5)

```python
from models.schemas import JDInfo, ResumeInfo, GapAnalysis
from services.llm_service import LLMService

def analyze_jd(text: str, llm: LLMService) -> JDInfo: ...
def analyze_resume(text: str, llm: LLMService) -> ResumeInfo: ...
def analyze_gap(jd: JDInfo, resume: ResumeInfo, llm: LLMService) -> GapAnalysis: ...
```

### ✅ Exceptions (v0.4.5)

```python
class AnalyzerError(Exception): ...
class JDAnalysisError(AnalyzerError): ...
class ResumeAnalysisError(AnalyzerError): ...
class GapAnalysisError(AnalyzerError): ...
```

### ✅ Prompts Layer (v0.4.4)

```python
# Question Generation
from prompts.question_generation import QUESTION_SYSTEM_PROMPT, get_question_generation_prompt

prompt = get_question_generation_prompt(gap_obj, resume_obj, jd_obj, num_questions=20)
llm.call(
    prompt=prompt,
    response_model=QuestionList,
    system_prompt=QUESTION_SYSTEM_PROMPT
)
```

### ⬜ Pending APIs

```python
from models.schemas import QuestionList, GapAnalysis, ResumeInfo, JDInfo

def generate_questions(
    gap: GapAnalysis,
    resume: ResumeInfo,
    jd: JDInfo,
    num_questions: int = 20
) -> QuestionList: ...
```

-----

## 🧭 Confirmed Top-Level Design Decisions

### Analyzer Layer Rules (v0.4.5)

- **输入解耦**：`jd_analyzer` / `resume_analyzer` 只接收纯文本 `str`，不接收文件对象。文件解析由 `core/parsers/` 负责。
- **依赖注入**：Analyzer 不在内部实例化 `LLMService`，统一由调用方注入：`analyze_xxx(text, llm) -> Model`。
- **异常包装**：Analyzer 捕获底层异常（OpenAI 调用失败、Pydantic 校验失败等），向上抛出统一业务异常，避免将底层实现细节直接暴露给前端用户。
- **单一职责**：Analyzer 负责“文本 → 结构化模型”的业务整合，不承担文件解析、页面提示、复杂状态管理等职责。

### Resume Input Guardrail (v0.4.5)

- **20页上限策略已确认**：系统对简历长度设置上限，避免极端超长文本带来的成本、延迟和稳定性问题。
- **前端需展示该限制**：上传页需明确提示用户简历存在长度/页数上限。
- **实现层建议**：
  - 优先复用 `utils` 中现有 `token_counter` / 页数限制逻辑；
  - `resume_analyzer.py` 仅作为最后一道防线做防御性校验；
  - 若超限，抛出 `ResumeAnalysisError`，由前端友好提示。

### Experience Field Strategy

- `ResumeInfo.years_of_experience` **暂由 LLM 提取**；
- Python 层 **暂不做兜底重算**，保持实现简单；
- 若后续出现明显误差，再考虑引入日期解析和兜底逻辑。

### Gap Score Ownership

- `GapAnalysis.overall_match_score` **不由 LLM 输出**；
- `gap_analyzer.py` 将基于权重在 Python 层统一计算：
  - 技能匹配：40%
  - 经验匹配：30%
  - 教育匹配：20%
  - 项目相关性：10%

-----

## 🧱 Schema Blueprint Snapshot
> 这是业务层开发必须对齐的“最小蓝图摘录”。  
> 目的：避免后续实现时再出现字段名猜测、测试与模型不一致、Prompt 与 Schema 漂移。

### JDInfo

```python
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
```

### ResumeInfo

```python
class ResumeInfo(BaseModel):
    skills: List[str]
    experiences: List[WorkExperience]
    projects: List[Project] = Field(default_factory=list)
    education: List[Education]

    summary: Optional[str] = None
    certifications: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    years_of_experience: Optional[int] = None
```

### WorkExperience

```python
class WorkExperience(BaseModel):
    company: str
    title: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
```

### Project

```python
class Project(BaseModel):
    name: str
    description: str
    technologies: List[str] = Field(default_factory=list)
    role: Optional[str] = None
    link: Optional[str] = None
```

### Education

```python
class Education(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    graduation_date: Optional[str] = None
    gpa: Optional[str] = None
```

### GapAnalysis

```python
class GapAnalysis(BaseModel):
    matched_skills: List[str]
    missing_skills: List[str]
    skill_score: int = Field(ge=0, le=100)

    experience_match: str
    experience_score: int = Field(ge=0, le=100)

    education_match: str
    education_score: int = Field(ge=0, le=100)

    project_relevance: str
    project_score: int = Field(ge=0, le=100)

    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]

    overall_match_score: int = Field(ge=0, le=100)
```

### Question / QuestionList

```python
class QuestionType(str, Enum):
    TECHNICAL = "技术深度"
    PROJECT = "项目经验"
    SCENARIO = "情景模拟"
    BEHAVIORAL = "行为面试"

class DifficultyLevel(str, Enum):
    BASIC = "基础"
    INTERMEDIATE = "进阶"
    ADVANCED = "高级"

class Question(BaseModel):
    question_text: str
    question_type: QuestionType
    difficulty: DifficultyLevel
    focus_area: str
    intent: str
    reference_answer: str

class QuestionList(BaseModel):
    questions: List[Question]
```

-----

## 📋 Current Business Logic Notes

### `core/analyzers/jd_analyzer.py` ✅

**职责**
- 接收 JD 纯文本；
- 组合 `prompts.jd_extraction`；
- 调用 `LLMService.call(...)`；
- 返回 `JDInfo`；
- 包装底层异常为 `JDAnalysisError`。

**函数签名**
```python
def analyze_jd(text: str, llm: LLMService) -> JDInfo: ...
```

### `core/analyzers/resume_analyzer.py` ✅

**职责**
- 接收简历纯文本；
- 做基础输入校验；
- 执行超长内容防御性校验；
- 组合 `prompts.resume_extraction`；
- 调用 `LLMService.call(...)`；
- 返回 `ResumeInfo`；
- 包装底层异常为 `ResumeAnalysisError`。

**函数签名**
```python
def analyze_resume(text: str, llm: LLMService) -> ResumeInfo: ...
```

**已确认行为**
- 输入为空：抛业务异常；
- 输入过短：抛业务异常；
- 输入超长：抛业务异常；
- LLM/Pydantic 失败：统一包装后抛出业务异常。

> 备注：长度限制的最终实现应优先参考 `utils` 中现有 token/page 限制逻辑，Analyzer 仅作为兜底层。

-----

## 🎯 Permanent Design Decisions

### Model & Prompts Logic

- **防幻觉设计 (Anti-Hallucination)**：生成面试题时，不仅传入 Gap 结果，还传入截断精简后的 `Resume` 核心项目与工作经历，确保 LLM 提问紧扣候选人真实履历。
- **数学计算前置 (Python-Layer Math)**：题目数量分配、难度比例、总分计算等数值逻辑由 Python 层完成，避免 LLM 算数幻觉。
- **枚举强约束 (Enum Strictness)**：`Question.question_type` 与 `Question.difficulty` 全面采用 Enum，保障前端过滤和渲染稳定。
- **职责分离 (Separation of Concerns)**：Prompt 负责抽取和文本分析，Python 负责分数汇总、配比计算、边界控制。
- **Schema First**：后续任何模块实现、测试、Prompt 适配，必须以 `models/schemas.py` 为唯一字段依据，禁止凭命名习惯自行推测字段名。

-----

## 📋 Update Log

| Version | Date | Changes |
|---------|------|---------|
| **0.4.5** | **2025-01-XX** | **✅ Analyzer Layer 启动**<br>- 新增 `core/analyzers/exceptions.py` 统一业务异常<br>- 完成 `core/analyzers/jd_analyzer.py` 顶层 API 设计<br>- 完成 `core/analyzers/resume_analyzer.py` 顶层 API 设计<br>- 确认 Analyzer 依赖注入与输入解耦原则<br>- 确认 Resume 20页限制策略（前端需明确展示）<br>- 将关键 Schema 摘录纳入 Architecture，避免字段幻觉 |
| **0.4.4** | **2025-01-XX** | **✅ `prompts/question_generation.py` + Schema 扩展**<br>- 引入 `Question` 和 `QuestionList` 模型及 Enum 类型约束<br>- 确定自适应难度和按比例分布的 Python 层计算逻辑<br>- 确立针对项目题防幻觉的上下文精简截断策略 |
| 0.4.3 | 2025-01-XX | ✅ `prompts/gap_analysis.py` + `GapAnalysis` 扩充至12字段 |
| 0.4.2 | 2025-01-XX | ✅ `prompts/resume_extraction.py` + 简历Schema嵌套模型扩展 |
| 0.4.1 | 2025-01-XX | 🐛 Schema 修正 + `JDInfo` 字段扩展 |
| 0.4.0 | 2025-01-XX | ✅ `prompts/jd_extraction.py` |
| 0.3.0 | 2025-01-XX | ✅ `services/llm_service.py` (包含异常重试机制) |

-----

## 🚀 Next Steps

### Immediate (Next 3 Tasks)

1. ⬜ `core/analyzers/gap_analyzer.py` 🎯 **NEXT**
2. ⬜ `core/generators/question_generator.py`
3. ⬜ 同步前端上传页展示 Resume 长度/页数限制

### Medium Term

4. 构建 Streamlit Frontend (`app/pages/`)
5. 补充 `question_generator` 及业务层测试覆盖

-----

> **Single source of truth** — 每次模块完成时更新。  
> **Last Updated**: v0.4.5 — Analyzer Layer 已启动，Schema Blueprint 已入档  
> **Next**: `core/analyzers/gap_analyzer.py` 🚀

---

如果你愿意，我下一步可以继续帮你做两件事中的任意一个：

1. **把这份更新版 ARCHITECTURE 再压缩成更适合团队阅读的精简版**  
2. **继续进入 `gap_analyzer.py` 的顶层 API 决策讨论**