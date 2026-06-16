# 📐 ARCHITECTURE.md

> **Project Map & Technical Documentation** > **Version**: 0.9.0 (Day 1 架构迁移与全栈流式联调完成版)  
> **Architecture Style**: 前后端分离架构 (Next.js 14 + FastAPI)

---

## 🎯 Project Overview

**Name**: Interview Prep Assistant (AI 面试准备助手)  
**Purpose**: 基于大模型驱动的个性化面试辅导与漏斗分析工具，通过精准匹配求职意向（JD）与候选人简历，动态生成无幻觉的定制化面试题库。  
**Tech Stack**: Next.js 14, Tailwind CSS, FastAPI, Pydantic v2, OpenAI GPT-4o-mini。

---

## 🏗️ 全栈分层架构 (Full-Stack Layered Architecture)

本系统采用工业级**前后端分离架构**，核心业务逻辑与网络传输层完全解耦，确保了高内聚低耦合的技术表现。

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. 前端表现层 (Frontend UI Layer) - Next.js 14 & Tailwind CSS         │
│    - 页面路由管理 (/upload, /analysis, /questions)                     │
│    - 共享组件库 (进度指示器、动画闪卡、匹配度雷达图)                    │
│    - 事件流监听 (SSE EventSource Client)                               │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ HTTP REST / SSE (流式推送)
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. API 路由与适配层 (API Adapter Layer) - FastAPI                      │
│    - 网络协议握手、跨域处理 (CORS)、临时会话网关 (_session_store)      │
│    - 统一多部分表单 (Multipart) 解析与异常过滤器映射                   │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ Pydantic 强类型依赖注入
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 3. 核心业务处理层 (Core Business Logic Layer)                          │
│    - 解析器子层 (core/parsers): 多格式文档 (PDF/Docx/Txt) 文本提取     │
│    - 分析器子层 (core/analyzers): JD/简历语义抽取、可解释性差异分析    │
│    - 生成器子层 (core/generators): 智能上下文截断与面试题去重生成      │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ 结构化 Prompt 契约
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 4. 基础设施与服务层 (Infrastructure & LLM Service Layer)              │
│    - LLM 基础通信 (支持 3次指数退避重试、30秒硬超时控制、Token 计数)    │
│    - 日志审计系统 (utils/logger.py)、全局配置中心 (config.py)         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 完整项目目录结构 (Complete Directory Structure)

以下为升级后系统的全量文件快照，展示了 Streamlit 废弃后，新全栈框架的工程形态：

```text
interview-prep-assistant/
│
├── 📄 配置文件
│   ├── .env.example                    # 环境变量模板（含 OpenAI API 配置）
│   ├── .gitignore                      # Git 忽略配置
│   ├── requirements.txt                # Python 后端核心依赖包
│   ├── config.py                       # 全局配置中心 (v0.3.0)
│   ├── generate_fixtures.py            # 测试数据生成脚本
│   └── README.md                       # 项目主说明文档
│
├── 🌐 api/                             # ✨ 新增：FastAPI 后端适配层
│   ├── __init__.py
│   ├── main.py                         # 后端主入口，CORS 策略与全局路由挂载中心
│   ├── schemas.py                      # 针对 HTTP 请求/响应定制的 Pydantic 模型
│   └── routes/                         # 路由终结点解耦目录
│       ├── __init__.py
│       ├── upload.py                   # 文件上传路由，驱动 core/parsers 解析文本
│       ├── analyze.py                  # 核心：实现 Server-Sent Events (SSE) 流式分析
│       └── questions.py                # 触发定制化面试题目生成
│
├── 💻 frontend/                        # ✨ 新增：Next.js 14 前端工程
│   ├── package.json                    # 前端依赖配置文件 (Tailwind, Axios, Recharts)
│   ├── tailwind.config.js              # Tailwind CSS 样式原子化配置文件
│   ├── app/                            # Next.js App Router 路由目录
│   │   ├── layout.tsx                  # 全局 HTML 骨架、Apple 风格 CSS 注入与全局状态上下文
│   │   ├── page.tsx                    # 系统欢迎门户首页
│   │   ├── upload/                     # 模块一：双文件拖拽上传
│   │   │   └── page.tsx                # 文件上传与字符数预览页面
│   │   ├── analysis/                   # 模块二：能力差距分析
│   │   │   └── page.tsx                # SSE 进度实时点亮与雷达图、技能对比渲染页
│   │   └── questions/                  # 模块三：个性化智能题库
│   │       └── page.tsx                # 题库多维过滤筛选与 HTML/CSS 翻转闪卡交互页
│   ├── components/                     # 共享原子 UI 组件库
│   │   ├── LoadingSpinner.tsx          # 统一加载动画组件
│   │   ├── ErrorMessage.tsx            # 统一异常拦截友好提示边界
│   │   └── ProgressIndicator.tsx       # SSE 专用进度条高亮核心组件
│   └── lib/
│       └── api.ts                      # 基于 Axios 与原生 EventSource 的 API 客户端封装
│
├── 📊 models/                          # 核心数据模型层（单真理源 Single Source of Truth）
│   ├── __init__.py
│   └── schemas.py                      # Pydantic 数据实体契约 (QuestionType, JDInfo, ResumeInfo, GapAnalysis等)
│
├── 📄 core/                            # 核心业务底座 (对 API 层完全透明)
│   ├── parsers/                        # 解析器子层：解耦文件 I/O，仅处理二进制流转文本
│   │   ├── pdf_parser.py               # PDF 结构文本提取器
│   │   ├── docx_parser.py              # DOCX 结构文本提取器
│   │   ├── txt_parser.py               # 纯文本解析器
│   │   └── parser_factory.py           # 工厂模式：根据后缀名动态指派解析器
│   ├── analyzers/                      # 分析器子层：执行语义级抽取与分析
│   │   ├── jd_analyzer.py              # 职位描述语义抽取器
│   │   ├── resume_analyzer.py          # 简历特征语义抽取器
│   │   └── gap_analyzer.py             # 核心：可解释性差距比对分析器
│   └── generators/                     # 生成器子层
│       └── question_generator.py       # 核心：防幻觉面试题智能生成器
│
├── 💬 prompts/                         # 独立提示词资产库
│   ├── jd_extraction.py                # JD 抽取 Prompt 模板
│   ├── resume_extraction.py            # 简历抽取 Prompt 模板
│   ├── gap_analysis.py                 # 匹配度漏斗比对 Prompt 模板
│   └── question_generation.py          # 定制化题库生成 Prompt 模板
│
├── ⚙️ services/                        # 韧性基础设施层
│   └── llm_service.py                  # 大模型底层通信封装（含 3 次退避重试、30s 硬超时控制）
│
├── 🔧 utils/                           # 工具箱目录
│   ├── logger.py                       # 滚动系统日志系统
│   └── token_counter.py                # 严密计算 Token 消耗工具
│
├── 🧪 tests/                           # 自动化测试层
│   └── test_api_e2e.py                 # ✨ 新增：针对 FastAPI 全套路由的端到端集成测试
│
├── 📁 data/uploads/                    # 运行时本地临时缓存目录
├── 📝 logs/app.log                     # 后端全局运行审计日志
└── 📦 app/                             # ⚠️ 归档：原旧版 Streamlit 前端（已完全废弃，仅做参考）
```

---

## 🔄 数据流动机制 (Data Flow Mechanism)

系统的整体数据流动依托三大核心管道，在前后端之间通过强类型的 JSON 载荷与底层的 Pydantic 实体进行刚性约束。

### 1. 文件流与文本解析阶段 (Stateless Parsing)
```text
[用户选择文件] -> Frontend (FormData) -> POST /api/upload/ -> Backend Memory
                                                                 │
[返回解析预览] <- Frontend (JSON) <- 文本解析工厂 (ParserFactory) ◄┘
```
* **流动细节**：前端通过 HTML5 拖拽组件捕获物理文件，组装成 `multipart/form-data` 结构通过 Axios 投递至后端 `/api/upload/jd` 或 `/api/upload/resume` 接口。后端路由截获二进制流后，通过 `ParserFactory` 分发至对应的解析器进行纯文本提取，将无损文本写入临时内存 Session Store，并立刻向前端返回前 200 字的解析预览及总字符数以进行视觉确认。

### 2. 流式语义分析阶段 (SSE Pipeline)
```text
Frontend (EventSource) ──► GET /api/analyze/stream ──► Backend 异步线程开始调度
                                                            │
进度条点亮 (1/3) ◄─────────── event: jd_done ───────────────┤ 1. 执行 analyze_jd()
进度条点亮 (2/3) ◄─────────── event: resume_done ───────────┤ 2. 执行 analyze_resume()
雷达图渲染展现    ◄─────────── event: complete (携带JSON) ───┘ 3. 执行 analyze_gap() 计算总分
```
* **流动细节**：前端实例化原生 `EventSource` 向后端发起持久的长连接请求。FastAPI 后端通过异步生成器（`async generator`）接管该连接，依次驱动核心层的 `analyze_jd`、`analyze_resume`。大模型解析出来的中间结构化 JSON 会在第一时间封装成 SSE 协议的特定格式事件（`event: jd_done` 等）高频推送至前端，实时点亮前端的步骤指示器。最后一步由后端 Python 层动态执行加权总分运算，生成完整的 `GapAnalysis` 大 JSON 载荷，随 `complete` 事件下发后安全挂断长连接。

### 3. 精准题库生成阶段 (Anti-Hallucination Generation)
```text
Frontend (POST Payload) ──► POST /api/questions/generate (num_questions: 10)
                                    │
    ┌───────────────────────────────┴────────────────────────────────┐
    ▼                                                                ▼
[Resume 智能上下文截断]                                     [LLM 生成题目列表 JSON]
(保留最近3项经验/每项前3条职责/限长)                                   │
    │                                                                ▼
    ▼                                                       [Python 层完全去重核验]
[组装终极精准 Prompt] ─────────────────────────────────────► 验证数量与参考答案完整性
                                                                     │
    ◄─────────────────── 返回无幻觉题库 QuestionList JSON ───────────┘
```

---

## 🔌 API 接口与数据格式明细 (API Endpoints & Data Formats)

### 1. 基础健康检查
* **Endpoint**: `GET /api/health`
* **Response Body**:
```json
{
  "status": "ok"
}
```

### 2. 简历/JD 文件上传适配接口
* **Endpoint**: `POST /api/upload/jd` 和 `POST /api/upload/resume`
* **Payload**: `file: UploadFile` (Binary Form)
* **Response Body**:
```json
{
  "success": true,
  "filename": "john_doe_resume.pdf",
  "char_count": 1420,
  "preview": "工作经历：2023-至今 担任高级后端开发工程师..."
}
```

### 3. 核心流式分析事件流 (SSE)
* **Endpoint**: `GET /api/analyze/stream`
* **Output Format**: `text/event-stream`
* **事件载荷序列流实例**：
```text
event: jd_start
data: {"message": "正在深度透视职位描述(JD)核心需求..."}

event: jd_done
data: {"job_title": "高级后端工程师", "required_skills": ["Python", "FastAPI", "Redis"]}

event: complete
data: {
  "matched_skills": ["Python", "Redis"],
  "missing_skills": ["FastAPI"],
  "skill_score": 80,
  "experience_score": 75,
  "education_score": 90,
  "project_score": 70,
  "overall_match_score": 78,
  "strengths": ["具有大规模分布式系统调优经验"],
  "weaknesses": ["缺乏 FastAPI 生产环境实战支撑"],
  "recommendations": ["建议在面试前重点复习异步IO模型与FastAPI中间件机制"]
}
```

### 4. 智能定制题目生成接口
* **Endpoint**: `POST /api/questions/generate`
* **Request Body**:
```json
{
  "num_questions": 10
}
```
* **Response Body (`QuestionList` 模型)**:
```json
{
  "success": true,
  "questions": [
    {
      "question_text": "在您过往的 Redis 项目中，是如何处理缓存雪崩效应的？请结合实际生产案例说明。",
      "question_type": "项目经验",
      "difficulty": "进阶",
      "focus_area": "高并发稳定性控制",
      "intent": "考察候选人是否具备真实生产环境的问题排查与架构防御能力，而非纸上谈兵。",
      "reference_answer": "1. 引入随机过期时间扰动因子（TTL + Random）；2. 配置多级缓存架构；3. 落地熔断降级隔离机制..."
    }
  ]
}
```

---

## ✨ 项目核心技术亮点 (Core Project Highlights)

### 1. 工业级 Server-Sent Events (SSE) 极速流式反馈
传统的大模型全链路分析（解析、特征提取、比对）通常需要长达 15-30 秒的推理耗时。单体架构下的阻塞请求会导致页面长时间假死。本系统采用 FastAPI 异步上下文生成器与 HTTP 长连接，将复杂长任务重构为 6 个高频状态节点，建立起实时“跳动”的步骤指示条，将用户交互体验从传统的无感等待提升为工业级实时追踪。

### 2. 严苛的“防幻觉”简历上下文智能截断策略
直接将长篇大论的完整简历灌入大语言模型会引发两大死穴：Token 消耗指数级膨胀，以及长上下文导致模型注意力失焦而产生“凭空捏造（幻觉）”。
本系统在生成器层 (`core/generators/question_generator.py`) 创新性地引入了工业截断策略：
* **工作经验收敛**：强制仅提取候选人最近 3 个周期的 `WorkExperience` 数据实体。
* **职责颗粒度裁剪**：每个工作周期仅截取前 3 条核心 `responsibilities`，且单条字符数通过代码刚性截断至 150 字以内。
* **项目精简化表达**：保留所有项目的完整骨架，但核心 `description` 强制截断至 200 字符以内。
通过极限降噪，保证了生成的每一道面试题都严密紧扣候选人的真实履历，完全锁死了模型的幻觉空间。

### 3. 可解释性 Python 加权算法替代大模型盲盒得分
本系统杜绝了大模型直接输出不透明“综合匹配度得分”的做法。系统的综合匹配分（`overall_match_score`）完全依托确定性的可解释算法，在 Python 内存层进行精确计算：

$$overall\_match\_score = \text{round}(skill \times 0.4 + exp \times 0.3 + edu \times 0.2 + proj \times 0.1)$$

这确保了评估体系具有可追溯性与数据严谨度，让系统输出具有坚实的工程学支撑。

### 4. 零改动的算法核心无缝迁移
由于在核心层 (`core/`) 坚持执行依赖注入（`LLMService` 作为入参传入）与输入解耦（仅接收原生 `str` 文本，不处理任何文件 I/O 与 HTTP 报文），整个系统的核心算法层在从 Streamlit 单体架构迁移至 Next.js + FastAPI 的现代化全栈架构时，**代码改动率为 0%**。这种高超的工程解耦设计，使得核心资产具备了极高的可移植性。

---

## 🔌 后续项目对接与联调必备信息 (Integration & Handoff Specs)

为了方便后续团队承接项目或进行二次深度开发，以下列出联调与对接所需的底层工程细节：

### 1. 运行环境依赖 (Runtime Environment)
* **后端硬件与系统环境**：Python 3.9+ 运行环境。
* **前端硬件与系统环境**：Node.js 18.x 或 Node.js 20+ 环境，使用 npm 或 yarn 包管理器。

### 2. 环境变量契约 (Environment Variables)
在项目根目录下必须建立 `.env` 文件，且必须包含以下键值对：
```bash
# OpenAI 大模型服务密钥配置
OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
# 全局超时时间控制（秒）
LLM_TIMEOUT=30
# 允许的前端跨域源地址配置
ALLOWED_CORS_ORIGINS="http://localhost:3000"
```

### 3. 本地开发快速拉起命令 (Dev Launch Commands)
```bash
# 终端管道 1: 启动 FastAPI 后端服务
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000

# 终端管道 2: 启动 Next.js 前端服务
cd frontend
npm install
npm run dev
```
* **联调访问网关**：前端访问地址为 `http://localhost:3000`；后端接口文档 (Swagger UI) 访问地址为 `http://localhost:8000/docs`。

### 4. 临时会话存储数据模型 (Session Store Schema)
当前系统的多页面状态流转基于 `api/main.py` 中的全局内存字典 `_session_store`。二次开发人员如需升级为分布式多用户 SaaS 版本，需使用 Redis 或关系型数据库重构以下结构：

```python
# 核心对接 Session 内存结构契约
_session_store: dict = {
    "jd_text": str,             # 由 /api/upload/jd 写入的原始解析纯文本
    "resume_text": str,         # 由 /api/upload/resume 写入的原始解析纯文本
    "jd": JDInfo,               # 经由 analyze_jd() 解析后的 Pydantic 模型实体
    "resume": ResumeInfo,       # 经由 analyze_resume() 解析后的 Pydantic 模型实体
    "gap": GapAnalysis,         # 经由 analyze_gap() 推导出的核心匹配度大 JSON 对象
    "questions": QuestionList   # 经由 /api/questions/generate 生成并存储的题库实体
}
```
* **生命周期约束**：调用 `/api/upload/` 时会覆写对应的 `_text` 字段，调用 `/api/analyze/stream` 流程前必须确保 `jd_text` 和 `resume_text` 已经成功写入，否则后端会立即抛出 `400 Bad Request` 业务异常。

### 5. 跨域策略 (CORS Contract)
后端 `api/main.py` 已默认挂载 `CORSMiddleware`。在与新域名联调时，必须确保 `allow_origins` 列表中包含前端的精准域名与端口，且必须允许 `allow_credentials=True`，以便 SSE 长连接顺利握手。

---

> **Single Source of Truth** — 每次重大更新必须同步此文档  
> **Current Version**: v0.9.0 - Day 1 完美合流稳定版 ✅  
> **Status**: 全栈联调成功，全量文件结构稳固，后续项目对接接口及参数全公开，具备极佳的工程可承接性。
```