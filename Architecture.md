# 📐 ARCHITECTURE.md

> **Project Map & Technical Documentation**
> Last Updated: 2025-01-XX | Version: 0.4.4

-----

## 🎯 Project Overview

**Name**: Interview Prep Assistant
**Purpose**: AI-powered personalized interview preparation tool
**Tech Stack**: Python 3.9+, Streamlit, OpenAI GPT-4o-mini

-----

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
│   ├── 📂 parsers/                  # ✅ Parsing Layer (100%)
│   ├── 📂 analyzers/                # 🎯 NEXT TARGET
│   │   ├── 📄 jd_analyzer.py        # ⬜
│   │   ├── 📄 resume_analyzer.py    # ⬜
│   │   └── 📄 gap_analyzer.py       # ⬜
│   └── 📂 generators/
│       └── 📄 question_generator.py # ⬜
├── 📂 prompts/                      # ✅ Prompts Layer (100%)
│   ├── 📄 __init__.py               # ✅ v0.4.3
│   ├── 📄 jd_extraction.py          # ✅ v0.4.1
│   ├── 📄 resume_extraction.py      # ✅ v0.4.2
│   ├── 📄 gap_analysis.py           # ✅ v0.4.3
│   └── 📄 question_generation.py    # ✅ v0.4.4 ⭐ NEW
├── 📂 models/
│   ├── 📄 __init__.py               # ✅
│   └── 📄 schemas.py                # ✅ v0.4.4 ⭐ NEW (Question Schema 扩充)
├── 📂 services/
│   └── 📄 llm_service.py            # ✅ v0.3.0
├── 📂 utils/                        # ✅ Utils Layer (100%)
└── 📂 tests/
    ├── 📄 test_question_generation.py# ⬜ 待补充测试
    ├── 📄 test_gap_analysis.py      # ✅ v0.4.3
    ├── 📄 test_resume_extraction.py # ✅ v0.4.2
    ├── 📄 test_parser_factory.py    # ✅
    ├── 📄 test_llm_service.py       # ✅
    └── 📄 test_*.py                 # ⬜ (other modules)
```

-----

## 📊 Module Status

```
✅ Foundation Layer (100%)
✅ Utilities (100%)
✅ File Parsing (100%)
✅ Services (100%)
✅ Prompts (100%) ⭐ COMPLETE
├── [✅] prompts/__init__.py
├── [✅] prompts/jd_extraction.py
├── [✅] prompts/resume_extraction.py
├── [✅] prompts/gap_analysis.py
└── [✅] prompts/question_generation.py (v0.4.4) ⭐ NEW

⬜ Analyzers (0%) 🎯 NEXT
├── [ ] core/analyzers/jd_analyzer.py
├── [ ] core/analyzers/resume_analyzer.py
└── [ ] core/analyzers/gap_analyzer.py

⬜ Generators (0%)
└── [ ] core/generators/question_generator.py

⬜ Frontend (0%)
└── [ ] app/ & pages/

🔄 Tests (72%)
├── [ ] tests/test_question_generation.py
└── [ ] 待补全其余业务逻辑测试

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Progress: 21/29 modules (72%)
Next Target: core/analyzers/jd_analyzer.py 🚀
```

-----

## 🔌 Core API Definitions

### ✅ Prompts Layer (v0.4.4)

```python
# Question Generation ⭐ NEW
from prompts.question_generation import QUESTION_SYSTEM_PROMPT, get_question_generation_prompt

# 将在 Python 层内部动态计算题目和难度分配，防止 LLM 算数幻觉
prompt = get_question_generation_prompt(gap_obj, resume_obj, jd_obj, num_questions=20)
llm.call(prompt=prompt, response_model=QuestionList, system_prompt=QUESTION_SYSTEM_PROMPT)
```

### ✅ Data Models (models/schemas.py v0.4.4)

| Model | 核心说明 | 状态/变更记录 |
|-------|---------|-------------|
| `JDInfo` | JD结构化提取 (9字段) | ✅ v0.4.1 |
| `ResumeInfo` | 简历结构化提取 (8字段+嵌套模型) | ✅ v0.4.2 |
| `GapAnalysis` | JD与简历的匹配度差异分析 | ✅ v0.4.3 |
| `QuestionList` | 包含 `List[Question]` 的最外层容器 | ✅ **v0.4.4 ⭐ NEW** |
| `Question` | 动态生成的面试题 (结合Enum强约束) | ✅ **v0.4.4 ⭐ NEW** |

-----

#### 📋 Question 完整字段列表 (6个) ⭐ NEW

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
    question_text: str          # 具体的面试问题内容
    question_type: QuestionType # Enum强约束：技术/项目/情景/行为
    difficulty: DifficultyLevel # Enum强约束：基础/进阶/高级
    focus_area: str             # 关联的具体技能点或项目名
    intent: str                 # 考察意图（一句话让用户明白意义）
    reference_answer: str       # 简短的参考答案/核心得分点（限1-3句话）
```

-----

### ⬜ Pending APIs

```python
# core/analyzers/ (Business Logic Layer) 🎯 NEXT
def analyze_jd(text: str) -> JDInfo: ...
def analyze_resume(text: str) -> ResumeInfo: ...
def analyze_gap(jd: JDInfo, resume: ResumeInfo) -> GapAnalysis: ... # 将计算 overall_match_score

# core/generators/
def generate_questions(gap: GapAnalysis, resume: ResumeInfo, jd: JDInfo, num_questions: int = 20) -> QuestionList: ...
```

-----

## 🎯 Permanent Design Decisions

### Model & Prompts Logic (v0.4.4)

  - **防幻觉设计 (Anti-Hallucination)**：生成面试题时，不仅传入 Gap 结果，还传入截断精简后的 `Resume` 核心项目与工作经历，确保 LLM 提问（尤其是 30% 的项目题）紧扣候选人真实履历，不凭空捏造。
  - **数学计算前置 (Python-Layer Math)**：LLM 算数能力较弱。关于自适应难度（ `<60分` 偏基础，`>=60分` 偏高级）以及题目类型配比（技术60%、项目30%等）的具体生成数量，**全部由 Python 层算好具体的整数**后，作为强指令注入 Prompt，大幅提升 LLM 结构化输出的服从度。
  - **枚举强约束 (Enum Strictness)**：在 `Question` Schema 中全面使用 `Enum` (`QuestionType`, `DifficultyLevel`)，利用 OpenAI Structured Outputs 的强 Schema 支持，确保前端渲染和按类型过滤时不会遇到脏数据。
  - **职责分离 (Separation of Concerns)**：`overall_match_score` 从 LLM Prompt 的要求中被明确剔除。Prompt 仅负责各维度的独立评分与自由文本评估，最终的总分由 `gap_analyzer.py` 基于权重计算。

-----

## 📋 Update Log

| Version | Date | Changes |
|---------|------|---------|
| **0.4.4** | **2025-01-XX** | **✅ `prompts/question_generation.py` + Schema 扩展**<br>- 引入 `Question` 和 `QuestionList` 模型及 Enum 类型约束<br>- 确定自适应难度和按比例分布的 Python 层计算逻辑<br>- 确立针对项目题防幻觉的上下文精简截断策略 |
| 0.4.3 | 2025-01-XX | ✅ `prompts/gap_analysis.py` + `GapAnalysis` 扩充至12字段 (确立权重与总分后置计算) |
| 0.4.2 | 2025-01-XX | ✅ `prompts/resume_extraction.py` + 简历Schema嵌套模型扩展 |
| 0.4.1 | 2025-01-XX | 🐛 Schema 修正 + `JDInfo` 字段扩展 |
| 0.4.0 | 2025-01-XX | ✅ `prompts/jd_extraction.py` |
| 0.3.0 | 2025-01-XX | ✅ `services/llm_service.py` (包含异常重试机制) |

-----

## 🚀 Next Steps

### Immediate (Next 3 Tasks)

1.  ⬜ `core/analyzers/jd_analyzer.py` 🎯 **NEXT**
2.  ⬜ `core/analyzers/resume_analyzer.py`
3.  ⬜ `core/analyzers/gap_analyzer.py` (实现 `calculate_overall_score()` 逻辑)

### Medium Term

4.  `core/generators/question_generator.py` (串联 LLM 与 Python 动态分发逻辑)
5.  构建 Streamlit Frontend (`app/pages/`)

-----

> **Single source of truth** — 每次模块完成时更新。
> **Last Updated**: v0.4.4 — 提示词工程全面竣工 (Prompts Layer 100%)
> **Next**: `core/analyzers/jd_analyzer.py` 🚀 (正式进入业务逻辑整合层)