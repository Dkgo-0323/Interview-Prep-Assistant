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
✅ 基础层 (100%)
├── config.py (v0.3.0 - 全局配置)
├── models/schemas.py (v0.4.4 - 7个数据模型)
└── services/llm_service.py (v0.3.0 - LLM服务)

✅ 工具层 (100%)
├── utils/logger.py (日志系统)
├── utils/text_cleaner.py (文本清洗)
├── utils/token_counter.py (Token计数)
├── utils/validators.py (验证器)
└── utils/__init__.py

✅ 解析器层 (100%)
├── core/parsers/pdf_parser.py (PDF解析)
├── core/parsers/docx_parser.py (DOCX解析)
├── core/parsers/txt_parser.py (TXT解析)
├── core/parsers/parser_factory.py (解析器工厂)
├── core/parsers/exceptions.py (解析异常)
└── core/parsers/__init__.py

✅ 提示词层 (100%)
├── prompts/jd_extraction.py (JD提取提示词)
├── prompts/resume_extraction.py (简历提取提示词)
├── prompts/gap_analysis.py (差距分析提示词)
├── prompts/question_generation.py (v0.5.0 - 题目生成提示词)
└── prompts/__init__.py

✅ 分析器层 (100%) 🎉 完成 v0.4.6
├── core/analyzers/jd_analyzer.py (JD分析器)
├── core/analyzers/resume_analyzer.py (简历分析器)
├── core/analyzers/gap_analyzer.py (差距分析器)
├── core/analyzers/exceptions.py (v0.5.0 - 新增QuestionGenerationError)
└── core/analyzers/__init__.py

✅ 生成器层 (100%) 🎉 完成 v0.5.0
├── core/generators/question_generator.py (题目生成器)
└── core/generators/__init__.py

✅ 前端层 (100%) 🎉 完成 v0.6.0 Phase 1
├── app/main.py (主入口 - 欢迎页)
├── app/pages/01_upload.py (上传页面)
├── app/pages/02_analysis.py (分析页面)
├── app/pages/03_questions.py (题目页面)
└── app/utils/ui_components.py (UI组件库)
    ├── apply_apple_style() - 全局CSS样式
    ├── render_progress_indicator() - 进度指示器
    ├── render_document_preview() - 文档预览
    ├── render_match_score_card() - 匹配度卡片
    ├── render_radar_chart() - 雷达图
    ├── render_skill_comparison() - 技能对比
    ├── render_flashcard() - 闪卡组件
    └── render_loading_spinner() - 加载动画

✅ 测试层 (92%)
├── test_jd_analyzer.py ✅
├── test_resume_analyzer.py ✅
├── test_gap_analyzer.py ✅
├── test_llm_service.py ✅
├── test_parser_factory.py ✅
├── test_question_generator.py ✅
├── test_docx_parser.py ✅
├── test_pdf_parser.py ✅
├── test_resume_extraction.py ✅
├── test_gap_analysis.py ✅
├── test_api_connection.py ✅
└── test_raw_openai.py ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
总计: 33/33 模块 (100%) ✅
Phase 1 MVP 已完成 🎉
```

---

## 完整项目目录
```text
interview-prep-assistant/
│
├── 📄 配置文件
│   ├── .env.example                    # 环境变量模板
│   ├── .gitignore                      # Git忽略配置
│   ├── requirements.txt                # Python依赖包
│   ├── config.py                       # 全局配置 (v0.3.0)
│   ├── generate_fixtures.py            # 测试数据生成器
│   └── README.md                       # 项目说明文档
│
├── 📊 数据模型层 (models/)
│   ├── __init__.py
│   └── schemas.py                      # Pydantic数据模型 (v0.4.4)
│       ├── QuestionType (Enum)         # 题目类型: 技术深度/项目经验/情景模拟/行为面试
│       ├── DifficultyLevel (Enum)      # 难度级别: 基础/进阶/高级
│       ├── WorkExperience              # 工作经历模型
│       ├── Project                     # 项目经历模型
│       ├── Education                   # 教育背景模型
│       ├── JDInfo                      # JD信息模型
│       ├── ResumeInfo                  # 简历信息模型
│       ├── GapAnalysis                 # 差距分析模型
│       ├── Question                    # 面试题模型
│       └── QuestionList                # 面试题列表模型
│
├── 🔧 工具层 (utils/)
│   ├── __init__.py
│   ├── logger.py                       # 日志系统
│   ├── text_cleaner.py                 # 文本清洗工具
│   ├── token_counter.py                # Token计数工具
│   └── validators.py                   # 验证器工具
│
├── 📄 解析器层 (core/parsers/)
│   ├── __init__.py
│   ├── pdf_parser.py                   # PDF文件解析器
│   ├── docx_parser.py                  # DOCX文件解析器
│   ├── txt_parser.py                   # TXT文件解析器
│   ├── parser_factory.py               # 解析器工厂模式
│   └── exceptions.py                   # 解析器异常类
│
├── 💬 提示词层 (prompts/)
│   ├── __init__.py
│   ├── jd_extraction.py                # JD提取提示词模板
│   ├── resume_extraction.py            # 简历提取提示词模板
│   ├── gap_analysis.py                 # 差距分析提示词模板
│   └── question_generation.py          # 题目生成提示词模板 (v0.5.0)
│
├── 🔍 分析器层 (core/analyzers/)
│   ├── __init__.py
│   ├── jd_analyzer.py                  # JD分析器
│   ├── resume_analyzer.py              # 简历分析器
│   ├── gap_analyzer.py                 # 差距分析器 (v0.4.6)
│   └── exceptions.py                   # 分析器异常类 (v0.5.0)
│       ├── AnalyzerError               # 基础异常
│       ├── JDAnalysisError             # JD分析异常
│       ├── ResumeAnalysisError         # 简历分析异常
│       ├── GapAnalysisError            # 差距分析异常
│       └── QuestionGenerationError     # 题目生成异常 (新增)
│
├── 🎯 生成器层 (core/generators/)
│   ├── __init__.py
│   └── question_generator.py           # 题目生成器 (v0.5.0)
│       ├── 前置输入验证 (5个必填字段检查)
│       ├── Resume上下文智能截断 (防幻觉)
│       ├── 题目去重检查
│       ├── 结果完整性验证
│       └── 异常统一包装 (中文用户友好消息)
│
├── 🎨 前端层 (app/)
│   ├── main.py                         # Streamlit主入口
│   ├── pages/
│   │   ├── 01_upload.py               # 文件上传页面
│   │   ├── 02_analysis.py             # 分析结果页面
│   │   └── 03_questions.py            # 题目展示页面
│   └── utils/                         # UI组件 (待创建)
│       ├── __init__.py
│       └── ui_components.py           # 共享UI组件
│           ├── render_radar_chart()   # 雷达图组件
│           ├── render_skill_comparison() # 技能对比组件
│           └── render_flashcard()     # 闪卡组件 (HTML/CSS翻转)
│
├── ⚙️ 服务层 (services/)
│   ├── __init__.py
│   └── llm_service.py                 # LLM服务 (v0.3.0)
│       ├── 重试机制 (3次重试)
│       ├── 超时处理 (30秒)
│       ├── Token计数
│       └── 错误处理
│
├── 🧪 测试层 (tests/)
│   ├── fixtures/                      # 测试数据
│   │   ├── sample_resume.docx
│   │   ├── corrupted.docx
│   │   ├── encrypted.docx
│   │   └── large.docx
│   ├── test_jd_analyzer.py
│   ├── test_resume_analyzer.py
│   ├── test_gap_analyzer.py
│   ├── test_llm_service.py
│   ├── test_parser_factory.py
│   ├── test_question_generator.py
│   ├── test_docx_parser.py
│   ├── test_pdf_parser.py
│   ├── test_resume_extraction.py
│   ├── test_gap_analysis.py
│   ├── test_api_connection.py
│   └── test_raw_openai.py
│
├── 📁 数据目录 (data/)
│   └── uploads/
│       └── .gitkeep                   # 保持目录存在
│
├── 📝 日志目录 (logs/)
│   └── app.log                        # 应用日志文件
│
├── 📋 文档文件
│   ├── Architecture.md                # 架构文档 (本文档)
│   ├── Front-End-Plan.md              # 前端设计文档
│   └── .pytest_cache/                 # pytest缓存目录
│
└── 🐙 Git目录 (.git/)
    ├── HEAD
    ├── config
    ├── description
    ├── hooks/
    ├── info/
    ├── objects/
    └── refs/
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
| **0.6.0** | 2025-01-XX | ✅ **完成 Frontend Layer (100%) - Phase 1 MVP**<br>- 实现 `app/main.py` 欢迎页<br>- 实现 `01_upload.py` 文件上传页面<br>- 实现 `02_analysis.py` 分析报告页面<br>- 实现 `03_questions.py` 面试题库页面<br>- 实现 `ui_components.py` 完整组件库<br>- Apple 风格设计 + 闪卡翻转动画<br>- 添加 plotly 依赖 |
| 0.5.0 | 2025-01-XX | ✅ **完成 Generator Layer (100%)**<br>- 实现 `question_generator.py` + 完整测试<br>- 修复 `prompts/question_generation.py` 字段引用<br>- 新增 `QuestionGenerationError` 异常<br>- 实现 Resume 截断和防幻觉策略 |
| 0.4.6 | 2025-01-XX | ✅ **完成 Analyzer Layer (100%)**<br>- 实现 `gap_analyzer.py` + 完整测试<br>- 确认总分计算权重和舍入规则<br>- 统一中文异常消息体系 |
| 0.4.5 | 2025-01-XX | ✅ `jd_analyzer.py` + `resume_analyzer.py` + `exceptions.py` |
| 0.4.4 | 2025-01-XX | ✅ `prompts/question_generation.py` + Question Schema |
| 0.4.3 | 2025-01-XX | ✅ `prompts/gap_analysis.py` + GapAnalysis Schema (12 fields) |
| 0.4.0-0.4.2 | 2025-01-XX | ✅ JD/Resume Prompts + Schema 迭代 |
| 0.3.0 | 2025-01-XX | ✅ `llm_service.py` (重试机制) |

---

## ✅ Phase 1 MVP Completed!

### Implementation Checklist

```python
# app/ (Streamlit Frontend)
[✅] 页面布局设计 (3页：上传 → 分析 → 题目)
[✅] 文件上传组件 (JD/Resume PDF/DOCX/TXT)
[✅] 分析结果可视化 (匹配度雷达图/技能对比)
[✅] 面试题展示界面 (分类/难度筛选)
[✅] 状态管理和进度指示
[✅] Apple 风格 CSS 设计
[✅] 闪卡翻转动画
[✅] UI 组件库封装

# 待完成 (Phase 2)
[ ] 端到端流程测试
[ ] 错误处理UI反馈优化
[ ] 响应式设计适配
[ ] PDF 报告导出
[ ] 题库批量导出
```

## 🚀 Next Milestone: v0.7.0 - Phase 2 Enhancements

### Planned Features

1. **PDF 报告导出**：使用 ReportLab/WeasyPrint 生成分析报告
2. **题库导出**：支持导出所有题目为 PDF/Markdown
3. **键盘快捷键**：← → 切换题目，Space 翻转卡片
4. **响应式优化**：移动端适配
5. **错误处理增强**：更友好的错误提示和恢复机制

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
> **Current Version**: v0.6.0 - Phase 1 MVP ✅  
> **Status**: 前端核心功能已完成，可运行完整流程  
> **Next Target**: Phase 2 增强功能 (PDF导出/键盘快捷键/响应式优化)