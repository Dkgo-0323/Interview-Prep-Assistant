# 📐 ARCHITECTURE.md

> **Project Map & Technical Documentation**
> Last Updated: 2025-01-XX | Version: 0.4.3

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
│   ├── 📂 analyzers/
│   │   ├── 📄 jd_analyzer.py        # ⬜
│   │   ├── 📄 resume_analyzer.py    # ⬜
│   │   └── 📄 gap_analyzer.py       # ⬜
│   └── 📂 generators/
│       └── 📄 question_generator.py # ⬜
├── 📂 prompts/                      # 🔄 80%
│   ├── 📄 __init__.py               # ✅ v0.4.3
│   ├── 📄 jd_extraction.py          # ✅ v0.4.1
│   ├── 📄 resume_extraction.py      # ✅ v0.4.2
│   ├── 📄 gap_analysis.py           # ✅ v0.4.3 ⭐ NEW
│   └── 📄 question_generation.py    # ⬜
├── 📂 models/
│   ├── 📄 __init__.py               # ✅
│   └── 📄 schemas.py                # ✅ v0.4.3 ⭐ NEW (GapAnalysis 扩充)
├── 📂 services/
│   └── 📄 llm_service.py            # ✅ v0.3.0
├── 📂 utils/                        # ✅ Utils Layer (100%)
└── 📂 tests/
    ├── 📄 test_gap_analysis.py      # ✅ v0.4.3 ⭐ NEW
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

🔄 Prompts (80%)
├── [✅] prompts/__init__.py
├── [✅] prompts/jd_extraction.py
├── [✅] prompts/resume_extraction.py
├── [✅] prompts/gap_analysis.py (v0.4.3) ⭐ NEW
└── [ ] prompts/question_generation.py

⬜ Analyzers (0%)
├── [ ] core/analyzers/jd_analyzer.py
├── [ ] core/analyzers/resume_analyzer.py
└── [ ] core/analyzers/gap_analyzer.py

⬜ Generators (0%)
└── [ ] core/generators/question_generator.py

⬜ Frontend (0%)
└── [ ] app/ & pages/

🔄 Tests (69%)
├── [✅] tests/test_gap_analysis.py (v0.4.3) ⭐ NEW
└── [ ] 待补全其余业务逻辑测试

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Progress: 20/29 modules (69%)
Next Target: prompts/question_generation.py 🚀
```

-----

## 🔌 Core API Definitions

### ✅ Prompts Layer (v0.4.3)

```python
# Gap Analysis ⭐ NEW
from prompts.gap_analysis import GAP_SYSTEM_PROMPT, get_gap_analysis_prompt

prompt = get_gap_analysis_prompt(jd_json, resume_json)
llm.call(prompt=prompt, response_model=GapAnalysis, system_prompt=GAP_SYSTEM_PROMPT)
```

### ✅ Data Models (models/schemas.py v0.4.3)

| Model | 核心说明 | 状态/变更记录 |
|-------|---------|-------------|
| `JDInfo` | JD结构化提取 (9字段) | ✅ v0.4.1 (完整) |
| `ResumeInfo` | 简历结构化提取 (8字段+嵌套模型) | ✅ v0.4.2 (完整) |
| `GapAnalysis` | JD与简历的匹配度差异分析 | ✅ **v0.4.3 (扩展至12字段)** |
| `Question` | 动态生成的面试题 | ⬜ 待集成验证 |

-----

#### 📋 GapAnalysis 完整字段列表 (12个) ⭐ NEW

```python
class GapAnalysis(BaseModel):
    # 技能匹配 (权重 40%) - LLM需处理同义词/缩写
    matched_skills: List[str]          
    missing_skills: List[str]          
    skill_score: int                   # 0-100
    
    # 经验匹配 (权重 30%)
    experience_match: str              
    experience_score: int              # 0-100
    
    # 教育匹配 (权重 20%)
    education_match: str               
    education_score: int               # 0-100
    
    # 项目相关性 (权重 10%)
    project_relevance: str             
    project_score: int                 # 0-100
    
    # 综合评估 (3-5条)
    strengths: List[str]               
    weaknesses: List[str]              
    recommendations: List[str]         
    
    # 计算字段 (⭐ 由Python后处理计算，非LLM输出)
    overall_match_score: int = Field(default=0, ge=0, le=100)
```

-----

### ⬜ Pending APIs

```python
# prompts/question_generation.py
QUESTION_SYSTEM_PROMPT: str
def get_question_generation_prompt(gap: GapAnalysis, num: int) -> str: ...

# core/analyzers/
def analyze_jd(text: str) -> JDInfo: ...
def analyze_resume(text: str) -> ResumeInfo: ...
def analyze_gap(jd: JDInfo, resume: ResumeInfo) -> GapAnalysis: ... # 将在此计算 overall_match_score

# core/generators/
def generate_questions(gap: GapAnalysis, num_questions: int = 10) -> List[Question]: ...
```

-----

## 🎯 Permanent Design Decisions

### Model & Prompts Logic (v0.4.3)

  - **输入序列化**：Prompt 接收的 JD 和 Resume 对象统一使用 `.model_dump_json(indent=2)` 序列化，确保信息无损传入。
  - **职责分离 (Separation of Concerns)**：`overall_match_score` 从 LLM Prompt 的要求中被明确剔除。Prompt 仅负责各维度的独立评分与自由文本评估，最终的总分由 `gap_analyzer.py` 中的 Python 代码基于 40/30/20/10 的权重（技能/经验/教育/项目）精确计算。
  - **智能化规范**：在技能匹配时，强制 LLM 进行同义词和缩写的合并规范化（如 JS = JavaScript），以减少后续硬编码规则的需求。

-----

## 📋 Update Log

| Version | Date | Changes |
|---------|------|---------|
| **0.4.3** | **2025-01-XX** | **✅ `prompts/gap_analysis.py` + Schema 扩展**<br>- `GapAnalysis` 模型扩展至 12 字段<br>- 确立 40/30/20/10 评分权重分布<br>- 新增 `test_gap_analysis.py` (22 个用例)<br>- 确立 `overall_match_score` 的计算代码后置策略 |
| 0.4.2 | 2025-01-XX | ✅ `prompts/resume_extraction.py` + 简历Schema嵌套模型扩展 |
| 0.4.1 | 2025-01-XX | 🐛 Schema 修正 + `JDInfo` 字段扩展 |
| 0.4.0 | 2025-01-XX | ✅ `prompts/jd_extraction.py` |
| 0.3.0 | 2025-01-XX | ✅ `services/llm_service.py` (包含异常重试机制) |

-----

## 🚀 Next Steps

### Immediate (Next 3 Tasks)

1.  ⬜ `prompts/question_generation.py` 🎯 **NEXT**
2.  ⬜ `core/analyzers/jd_analyzer.py`
3.  ⬜ `core/analyzers/resume_analyzer.py`

### Medium Term

4.  `core/analyzers/gap_analyzer.py` (实现 `calculate_overall_score()` 逻辑)
5.  `core/generators/question_generator.py`

-----

> **Single source of truth** — 每次模块完成时更新。
> **Last Updated**: v0.4.3 — `prompts/gap_analysis.py` + 匹配度分析 Prompt
> **Next**: `prompts/question_generation.py` 🚀