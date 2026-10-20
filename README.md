# Interview Prep Assistant

面向求职者的 AI 面试准备工具。用户上传职位描述（JD）和简历后，系统提取结构化信息、分析岗位匹配度，并生成可筛选的个性化面试题与参考回答。

本项目以一条完整的产品链路展示如何把大模型能力接入可交互的 Web 应用：**文件解析 → 结构化抽取 → 能力差距分析 → 流式反馈 → 面试题生成**。

## 项目亮点

- **端到端真实链路**：Next.js 前端直接调用 FastAPI，上传、分析和题目生成均接入真实后端，而非仅展示静态页面。
- **结构化 LLM 输出**：以 Pydantic 模型约束 JD、简历、差距分析和面试题的数据契约，降低自由文本输出进入业务层的风险。
- **流式用户体验**：分析过程通过 Server-Sent Events（SSE）分阶段返回 JD、简历与差距分析进度，避免长时间请求无反馈。
- **面试题质量控制**：按题量分批生成，对空答案与高相似题去重；当题量不足时会补充生成。
- **工程化边界清晰**：文件类型与大小校验、临时文件清理、错误映射、LLM 重试、日志和 token/cost 统计均位于明确的基础设施边界内。

## 已实现功能

| 能力 | 状态 | 说明 |
| --- | --- | --- |
| JD / 简历上传 | 已实现 | 支持 PDF、DOCX、TXT，单文件最大 10 MB。 |
| 文本解析 | 已实现 | 根据文件类型分派 PDF、DOCX、TXT 解析器。 |
| 岗位与简历结构化抽取 | 已实现 | 提取岗位技能、职责、经历、项目、教育背景等信息。 |
| 匹配度与差距分析 | 已实现 | 输出技能、经验、教育、项目维度的分数、优势、短板与建议。 |
| 流式分析进度 | 已实现 | 通过 SSE 依次推送 JD、简历与差距分析阶段。 |
| 个性化面试题 | 已实现 | 支持生成 10–50 题，包含类型、难度、考察点与参考回答。 |
| 题库交互 | 已实现 | 支持筛选、搜索、翻转卡片、收藏（收藏仅保留在当前前端会话）。 |
| 求职画像页面 | 尚未开放 | 页面明确说明当前状态，并引导至岗位匹配分析和题库；不调用占位生成接口，不展示虚构评分或薪资。 |

## 技术栈

| 层次 | 技术 |
| --- | --- |
| 前端 | Next.js 16、React 19、TypeScript、Tailwind CSS、Recharts |
| 后端 | FastAPI、Pydantic v2、Uvicorn |
| 大模型 | Qwen（DashScope OpenAI-compatible API），通过 OpenAI Python SDK 调用 |
| 文档解析 | pdfplumber、PyPDF2、python-docx、chardet |
| 测试 | pytest、FastAPI TestClient、前端 ESLint |

## 本地运行

### 1. 准备后端

需要 Python 3.10+。在项目根目录执行：

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

在 `.env` 中填写 DashScope 兼容接口配置，至少包括：

```dotenv
DASHSCOPE_API_KEY=your-api-key
LLM_BASE_URL=https://your-workspace-id.cn-beijing.maas.aliyuncs.com/compatible-mode/v1
LLM_DEFAULT_MODEL=qwen3.7-plus
```

启动 API：

```powershell
uvicorn api.main:app --reload --port 8000
```

服务启动后可访问 [Swagger UI](http://localhost:8000/docs)，健康检查地址为 `http://localhost:8000/api/health`。

### 2. 准备前端

需要 Node.js 20+。新开一个终端：

```powershell
Set-Location frontend
npm install
npm run dev
```

打开 `http://localhost:3000`。默认前端会连接 `http://localhost:8000`；如需覆盖，可设置 `NEXT_PUBLIC_API_URL`。

## 使用流程

1. 在首页分别上传 JD 与简历。
2. 进入分析页，查看 SSE 推送的解析进度及最终匹配报告。
3. 进入题库页，生成或读取缓存的个性化面试题。
4. 使用题型、难度、关键词与收藏筛选进行练习。

## API 概览

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| `POST` | `/api/upload/jd` | 上传并解析 JD。 |
| `POST` | `/api/upload/resume` | 上传并解析简历。 |
| `GET` | `/api/analyze/stream` | 以 SSE 执行三阶段分析。 |
| `GET` | `/api/analyze/result` | 读取当前内存会话中的分析结果。 |
| `POST` | `/api/questions/generate` | 根据分析结果生成 10–50 道题。 |
| `GET` | `/api/questions/cached` | 读取当前内存会话中的题目缓存。 |
| `DELETE` | `/api/upload/clear` | 清空当前服务进程的演示会话。 |

完整接口契约以运行中的 Swagger 文档为准。

## 验证

日常质量门禁使用固定依赖与经过审阅的离线测试集合（无需模型密钥）：

```powershell
python -m pip install -r requirements-ci.txt
python scripts/check_backend.py

Set-Location frontend
npm ci
npm run check
```

`check` 包含 lint、显式类型检查和生产构建。后端入口遇到本地回环权限受限时快速报环境错误；请使用允许本机回环的终端。覆盖范围、跳过项及 CI 说明见 [质量门禁](docs/development/quality-gates.md)。长期开发交接见 [协作入口](docs/development/README.md)。

仅复查 API 链路时，也可在已安装依赖的项目 venv 中执行：

```powershell
.\venv\Scripts\python.exe -m pytest tests/test_api_workflow.py tests/test_api_smoke.py -v -p no:cacheprovider

Set-Location frontend
npm run lint
```

测试目录覆盖文件解析、LLM 服务、结构化抽取、差距分析、题目生成及 API 冒烟场景。

上述命令是无需 API Key、不会产生模型费用的 API 链路回归：使用固定虚构 JD / 简历和 Mock LLM 返回值，真实执行上传解析、分析业务逻辑、SSE 序列、题目生成与缓存恢复。它不验证外部模型质量、网络连通性或浏览器逐帧接收 SSE 的时序。请勿将整个 `pytest` 测试目录视为离线测试，其中包含外部 API 测试。

2026-10-18 验证：26 项通过。复现问题、最小修复和完整契约见 [API 链路测试记录](docs/api-workflow-test-record.md)。真实 Qwen 验证可另行按 `tests/test_qwen_integration.py` 中的说明显式启用，会产生 API 用量。

## 面试展示建议

可以围绕以下设计决策展开：

1. 为什么用 Pydantic 约束大模型输出，而不是直接消费自然语言？
2. 为什么把同步 LLM 调用放入线程，并用 SSE 把阶段性结果反馈给浏览器？
3. 为什么题目生成需要分批、补足与相似度去重？
4. 如何将当前内存会话替换为 Redis/数据库，使其支持多用户、持久化和横向扩展？

## 当前边界

- 后端使用进程内全局字典保存演示会话，重启服务、多人同时使用或多实例部署都会丢失/混用状态；不适用于生产环境。
- 未实现登录、持久化历史、报告导出和模拟面试。
- 题库页在接口失败时会显示前端示例题，仅用于演示 UI；不能将该降级内容视为模型生成结果。
- 求职画像页面当前明确标注尚未开放；后端画像接口仍为历史占位实现，需补充真实分析服务和验收后再开放。

更多设计与运行时边界见 [Architecture.md](Architecture.md)。
