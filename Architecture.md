# 📐 ARCHITECTURE.md

> **Project Map & Technical Documentation**  
> **Version**: 0.4.6 | **Last Updated**: 2025-01-XX

---

## 🎯 Project Overview

**Name**: Interview Prep Assistant  
**Purpose**: AI-powered personalized interview preparation tool  
**Tech Stack**: Python 3.9+, Streamlit, OpenAI GPT-4o-mini

---

## 📊 Module Status Dashboard

```text
✅ Foundation (100%)
├── config.py
├── models/schemas.py (v0.4.4 - 7 models defined)
└── services/llm_service.py (v0.3.0)

✅ Utilities (100%)
└── utils/ (file validation, token counting, etc.)

✅ Parsers (100%)
└── core/parsers/ (PDF, DOCX, TXT support)

✅ Prompts (100%)
├── prompts/jd_extraction.py
├── prompts/resume_extraction.py
├── prompts/gap_analysis.py
└── prompts/question_generation.py

✅ Analyzers (100%) 🎉 COMPLETED v0.4.6
├── core/analyzers/exceptions.py
├── core/analyzers/jd_analyzer.py
├── core/analyzers/resume_analyzer.py
└── core/analyzers/gap_analyzer.py ✅ NEW

⬜ Generators (0%)
└── core/generators/question_generator.py

⬜ Frontend (0%)
└── app/ (Streamlit pages)

✅ Tests (85%)
├── test_jd_analyzer.py ✅
├── test_resume_analyzer.py ✅
├── test_gap_analyzer.py ✅ NEW
├── test_llm_service.py ✅
├── test_parser_factory.py ✅
└── [ ] test_question_generator.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall: 27/32 modules (84%)
Next: core/generators/question_generator.py 🚀
```

---

## 🔌 Core API Signatures

### Analyzers (v0.4.6)

```python
from core.analyzers import analyze_jd, analyze_resume, analyze_gap
from services.llm_service import LLMService

def analyze_jd(text: str, llm: LLMService) -> JDInfo
def analyze_resume(text: str, llm: LLMService) -> ResumeInfo
def analyze_gap(jd: JDInfo, resume: ResumeInfo, llm: LLMService) -> GapAnalysis
```

### Exceptions (v0.4.5)

```python
from core.analyzers.exceptions import (
    AnalyzerError,           # Base exception
    JDAnalysisError,         # JD parsing/analysis failures
    ResumeAnalysisError,     # Resume parsing/analysis failures
    GapAnalysisError         # Gap calculation failures
)
```

### Pending APIs

```python
# Question Generator (v0.5.0 - TO BE IMPLEMENTED)
def generate_questions(
    gap: GapAnalysis,
    resume: ResumeInfo,
    jd: JDInfo,
    num_questions: int = 20
) -> QuestionList
```

---

## 🧱 Schema Quick Reference

### Core Models (models/schemas.py v0.4.4)

```python
# Input Models
JDInfo:
    - required_skills: List[str]
    - responsibilities: List[str]
    - job_title, company, experience_required, education_required, etc.

ResumeInfo:
    - skills: List[str]
    - experiences: List[WorkExperience]
    - projects: List[Project]  # Can be empty
    - education: List[Education]
    - years_of_experience: Optional[int]  # LLM-extracted

# Analysis Output
GapAnalysis:
    - matched_skills, missing_skills: List[str]
    - skill_score, experience_score, education_score, project_score: int (0-100)
    - overall_match_score: int (0-100)  # Python-calculated, NOT from LLM
    - strengths, weaknesses, recommendations: List[str]

# Question Generation
Question:
    - question_text: str
    - question_type: QuestionType (Enum: 技术深度/项目经验/情景模拟/行为面试)
    - difficulty: DifficultyLevel (Enum: 基础/进阶/高级)
    - focus_area, intent, reference_answer: str

QuestionList:
    - questions: List[Question]
```

---

## 🧭 Critical Design Rules

### 1. Analyzer Layer (v0.4.6)

| Rule | Description |
|------|-------------|
| **输入解耦** | Analyzers 只接收 `str`，不处理文件 I/O |
| **依赖注入** | `LLMService` 由调用方传入，不在内部实例化 |
| **异常包装** | 底层错误包装为用户友好的业务异常 |
| **单一职责** | 仅负责"文本 → 结构化数据"，不做 UI/存储 |

### 2. Gap Analysis Score Calculation (v0.4.6)

```python
# overall_match_score 由 Python 计算，权重：
- 技能匹配 (skill_score):       40%
- 经验匹配 (experience_score):  30%
- 学历匹配 (education_score):   20%
- 项目相关 (project_score):     10%

# 计算公式：round(skill*0.4 + exp*0.3 + edu*0.2 + proj*0.1)
```

### 3. Input Validation Requirements

```python
# JD 必填字段
- required_skills: 至少 1 个
- responsibilities: 至少 1 个

# Resume 必填字段
- skills: 至少 1 个
- experiences: 至少 1 个
- projects: 允许为空 []

# 简历长度限制
- 最大 20 页（前端需明确提示）
- 超限抛 ResumeAnalysisError
```

### 4. Anti-Hallucination Strategy

```python
# Question Generation 防幻觉设计：
1. 传入完整 GapAnalysis 结果
2. 传入精简的 Resume (核心项目+经历，避免超长上下文)
3. 题目数量/难度分配由 Python 层计算
4. 强制使用 Enum 约束题型和难度
```

---

## 📋 Implementation Notes

### `core/analyzers/gap_analyzer.py` ✅ v0.4.6

**Key Features**:
- 前置输入校验（4 个必填字段检查）
- 冗余分数校验（0-100 范围，虽然 Pydantic 已限制）
- Python 层计算 `overall_match_score`（权重加权）
- 异常统一包装为中文用户友好消息

**Error Messages** (用户可见):
```python
"职位描述缺少必要的技能要求信息，无法进行匹配度分析"
"简历中未找到技能信息，无法进行匹配度分析"
"无法完成岗位匹配度分析，请稍后重试或联系技术支持"
"分析结果异常：技能匹配度评分超出有效范围，请重试"
```

### `core/analyzers/jd_analyzer.py` ✅ v0.4.5

**Responsibilities**:
- 调用 `prompts.jd_extraction.get_jd_extraction_prompt()`
- LLM 调用失败 → 抛 `JDAnalysisError`

### `core/analyzers/resume_analyzer.py` ✅ v0.4.5

**Responsibilities**:
- 基础校验：空文本、过短内容
- 防御性校验：超长文本（配合 utils 的 token/page 限制）
- LLM 提取 `years_of_experience`（暂不做 Python 兜底计算）

---

## 📦 Version History

| Version | Date | Key Changes |
|---------|------|-------------|
| **0.4.6** | 2025-01-XX | ✅ **完成 Analyzer Layer (100%)**<br>- 实现 `gap_analyzer.py` + 完整测试<br>- 确认总分计算权重和舍入规则<br>- 统一中文异常消息体系 |
| 0.4.5 | 2025-01-XX | ✅ `jd_analyzer.py` + `resume_analyzer.py` + `exceptions.py` |
| 0.4.4 | 2025-01-XX | ✅ `prompts/question_generation.py` + Question Schema |
| 0.4.3 | 2025-01-XX | ✅ `prompts/gap_analysis.py` + GapAnalysis Schema (12 fields) |
| 0.4.0-0.4.2 | 2025-01-XX | ✅ JD/Resume Prompts + Schema 迭代 |
| 0.3.0 | 2025-01-XX | ✅ `llm_service.py` (重试机制) |

---

## 🚀 Next Milestone: v0.5.0 - Question Generator

### Implementation Checklist

```python
# core/generators/question_generator.py
[ ] 实现 generate_questions() 函数
[ ] 题目数量按难度分配逻辑 (基础:进阶:高级 = 4:4:2)
[ ] 题目类型按 Gap 自适应分配
[ ] Resume 上下文精简（截断至关键项目/经历）
[ ] 集成 prompts.question_generation

# tests/test_question_generator.py
[ ] 正常流程测试
[ ] 数量/难度/类型分布验证
[ ] 空 projects 场景测试
[ ] 异常处理测试
```

### Design Questions to Resolve

1. Resume 截断策略：保留最近 N 个项目？Token 限制？
2. 题目去重逻辑：需要 Python 层检查重复吗？
3. 异常类型：新建 `QuestionGenerationError` 还是复用现有？

---

## 📖 Developer Quick Start

```python
# 典型调用流程
from services.llm_service import LLMService
from core.analyzers import analyze_jd, analyze_resume, analyze_gap

llm = LLMService()

# 1. 解析 JD 和简历
jd = analyze_jd(jd_text, llm)
resume = analyze_resume(resume_text, llm)

# 2. 分析匹配度
gap = analyze_gap(jd, resume, llm)
print(f"总分: {gap.overall_match_score}")  # Python 计算的加权分

# 3. 生成面试题（待实现）
# questions = generate_questions(gap, resume, jd, num_questions=20)
```

---

> **Single Source of Truth** — 每次重大更新必须同步此文档  
> **Next Target**: `core/generators/question_generator.py` 🎯  
> **Status**: Analyzer Layer 已完成，进入 Generator 阶段