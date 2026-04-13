# 📐 ARCHITECTURE.md

> **Project Map & Technical Documentation**  
> **Version**: 0.5.0 | **Last Updated**: 2025-01-XX

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
└── prompts/question_generation.py (v0.5.0 - 修复字段引用+截断逻辑)

✅ Analyzers (100%) 🎉 COMPLETED v0.4.6
├── core/analyzers/exceptions.py (v0.5.0 - 新增 QuestionGenerationError)
├── core/analyzers/jd_analyzer.py
├── core/analyzers/resume_analyzer.py
└── core/analyzers/gap_analyzer.py

✅ Generators (100%) 🎉 COMPLETED v0.5.0
└── core/generators/question_generator.py ✅ NEW

⬜ Frontend (0%)
└── app/ (Streamlit pages)

✅ Tests (92%)
├── test_jd_analyzer.py ✅
├── test_resume_analyzer.py ✅
├── test_gap_analyzer.py ✅
├── test_llm_service.py ✅
├── test_parser_factory.py ✅
└── test_question_generator.py ✅ NEW

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall: 30/32 modules (94%)
Next: app/ (Streamlit Frontend) 🚀
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

### Generators (v0.5.0)

```python
from core.generators import generate_questions
from services.llm_service import LLMService

def generate_questions(
    gap: GapAnalysis,
    resume: ResumeInfo,
    jd: JDInfo,
    llm: LLMService,
    num_questions: int = 10
) -> QuestionList
```

### Exceptions (v0.5.0)

```python
from core.analyzers.exceptions import (
    AnalyzerError,           # Base exception
    JDAnalysisError,         # JD parsing/analysis failures
    ResumeAnalysisError,     # Resume parsing/analysis failures
    GapAnalysisError,        # Gap calculation failures
    QuestionGenerationError  # Question generation failures (v0.5.0)
)
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

### 2. Generator Layer (v0.5.0)

| Rule | Description |
|------|-------------|
| **输入验证** | 前置验证 gap/resume/jd 的必填字段 |
| **题目数量限制** | 10-50 题，默认 10 题 |
| **防幻觉策略** | Resume 上下文截断（最近3经历，每经历前3职责） |
| **去重检查** | Python 层检查完全相同的题目文本 |
| **结果验证** | 验证题目数量、参考答案完整性 |

### 3. Gap Analysis Score Calculation (v0.4.6)

```python
# overall_match_score 由 Python 计算，权重：
- 技能匹配 (skill_score):       40%
- 经验匹配 (experience_score):  30%
- 学历匹配 (education_score):   20%
- 项目相关 (project_score):     10%

# 计算公式：round(skill*0.4 + exp*0.3 + edu*0.2 + proj*0.1)
```

### 4. Question Generation Anti-Hallucination (v0.5.0)

```python
# Resume 截断规则：
- 保留最近 3 个 WorkExperience
- 每个 experience 的 responsibilities 只取前 3 条
- 每条 responsibility 截断到 150 字符
- 保留所有 Projects，但 description 截断到 200 字符
- 保留所有 skills（核心匹配依据）

# 题目分配策略：
- 让 LLM 根据匹配度和候选人特点动态分配类型和难度
- 提供分配指导而非硬编码比例
- 匹配度 < 60: 侧重基础题（60%）和进阶题（40%）
- 匹配度 >= 60: 侧重进阶题（40%）和高级题（60%）
```

---

## 📋 Implementation Notes

### `core/generators/question_generator.py` ✅ v0.5.0

**Key Features**:
- 前置输入校验（5个必填字段检查 + 题目数量范围）
- Resume 上下文智能截断（防幻觉关键）
- 题目去重检查（完全相同的文本）
- 结果完整性验证（题目数量、参考答案）
- 异常统一包装为中文用户友好消息

**Error Messages** (用户可见):
```python
"能力差距分析缺少匹配度分数"
"能力差距分析缺少技能信息"
"简历缺少技能信息"
"职位描述缺少必备技能信息"
"简历缺少工作经历信息"
"生成的题目数量不正确：期望 X，实际 Y"
"第 X 题缺少参考答案"
"发现重复的面试题目"
"面试题生成失败，请稍后重试或联系技术支持"
```

### `core/analyzers/gap_analyzer.py` ✅ v0.4.6

**Key Features**:
- 前置输入校验（4 个必填字段检查）
- 冗余分数校验（0-100 范围，虽然 Pydantic 已限制）
- Python 层计算 `overall_match_score`（权重加权）
- 异常统一包装为中文用户友好消息

### `prompts/question_generation.py` ✅ v0.5.0

**Key Features**:
- 修复字段引用错误（work_experience → experiences 等）
- 实现 Resume 截断函数 `_truncate_resume_context()`
- 动态分配指导（非硬编码比例）
- 提供智能分配建议给 LLM

---

## 📦 Version History

| Version | Date | Key Changes |
|---------|------|-------------|
| **0.5.0** | 2025-01-XX | ✅ **完成 Generator Layer (100%)**<br>- 实现 `question_generator.py` + 完整测试<br>- 修复 `prompts/question_generation.py` 字段引用<br>- 新增 `QuestionGenerationError` 异常<br>- 实现 Resume 截断和防幻觉策略 |
| 0.4.6 | 2025-01-XX | ✅ **完成 Analyzer Layer (100%)**<br>- 实现 `gap_analyzer.py` + 完整测试<br>- 确认总分计算权重和舍入规则<br>- 统一中文异常消息体系 |
| 0.4.5 | 2025-01-XX | ✅ `jd_analyzer.py` + `resume_analyzer.py` + `exceptions.py` |
| 0.4.4 | 2025-01-XX | ✅ `prompts/question_generation.py` + Question Schema |
| 0.4.3 | 2025-01-XX | ✅ `prompts/gap_analysis.py` + GapAnalysis Schema (12 fields) |
| 0.4.0-0.4.2 | 2025-01-XX | ✅ JD/Resume Prompts + Schema 迭代 |
| 0.3.0 | 2025-01-XX | ✅ `llm_service.py` (重试机制) |

---

## 🚀 Next Milestone: v0.6.0 - Streamlit Frontend

### Implementation Checklist

```python
# app/ (Streamlit Frontend)
[ ] 页面布局设计 (3页：上传 → 分析 → 题目)
[ ] 文件上传组件 (JD/Resume PDF/DOCX/TXT)
[ ] 分析结果可视化 (匹配度雷达图/技能对比)
[ ] 面试题展示界面 (分类/难度筛选)
[ ] 状态管理和进度指示

# 集成测试
[ ] 端到端流程测试
[ ] 错误处理UI反馈
[ ] 响应式设计适配
```

### Design Questions to Resolve

1. 分析结果可视化：雷达图 vs 柱状图 vs 进度条？
2. 题目展示：分页 vs 滚动 vs 折叠面板？
3. 状态持久化：Session State vs 临时文件？

---

## 📖 Developer Quick Start

```python
# 典型调用流程
from services.llm_service import LLMService
from core.analyzers import analyze_jd, analyze_resume, analyze_gap
from core.generators import generate_questions

llm = LLMService()

# 1. 解析 JD 和简历
jd = analyze_jd(jd_text, llm)
resume = analyze_resume(resume_text, llm)

# 2. 分析匹配度
gap = analyze_gap(jd, resume, llm)
print(f"总分: {gap.overall_match_score}")  # Python 计算的加权分

# 3. 生成面试题 (v0.5.0)
questions = generate_questions(gap, resume, jd, llm, num_questions=15)
print(f"生成 {len(questions.questions)} 道面试题")
for q in questions.questions[:3]:
    print(f"- {q.question_text} ({q.question_type}, {q.difficulty})")
```

---

> **Single Source of Truth** — 每次重大更新必须同步此文档  
> **Next Target**: `app/` (Streamlit Frontend) 🎯  
> **Status**: Generator Layer 已完成，进入 Frontend 阶段