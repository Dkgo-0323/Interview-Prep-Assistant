# 当前状态

更新：2026-10-19（Asia/Shanghai）；详情见 [当天记录](daily/2026-10-19.md)。状态：用户已确认 S1 回归基线与 CI，B-001–B-003 开发进行中。

## 仓库快照

- 分支 `codex/qwen-provider-migration`；HEAD `4d5a0edf8b937e60ff8e2ed94e6b9e992837a5d6`。
- origin：`git@github.com:Dkgo-0323/Interview-Prep-Assistant.git`；本地上游引用为 `origin/codex/qwen-provider-migration`，本次未 fetch/验证远程连通性，不能保证远端实时一致。
- 开始时已有：`logs/app.log` 修改；未跟踪 `docs/interview_mock_exam_2027_project_reverse_engineering.md`、`docs/resume_project_analysis1.md`、`test-results/api-workflow.xml`。均保留，不纳入本次提交。
- 初始化后用户确认 S1；已修复测试替身，增加离线门禁和固定依赖、前端类型/构建门禁及本地字体，配置 CI。提交与推送进展见当天 daily；未改解析业务或开展 S2 功能。
- 本地 worktree 清单只有当前 checkout；应用有限聊天快照未发现另一个明确正在开发本仓库的聊天，但列表不完整，不能证明没有并行工作。新一轮仍须核对。

## 代码证据支持的能力

| 能力 | 证据与边界 |
| --- | --- |
| 上传/解析 | `api/routes/upload.py`、`core/parsers/`；PDF/DOCX/TXT、10 MB 校验和临时文件清理。本次未浏览器验收各格式。 |
| 结构化分析/SSE | `api/routes/analyze.py`、`core/analyzers/`、`models/schemas.py`；分阶段事件与 Pydantic 契约。本次 API 离线回归 26 项通过，真实模型/浏览器时序未验证。 |
| 题目生成/缓存 | `core/generators/question_generator.py`、`api/routes/questions.py`；分批、去重、补足，缓存为进程内状态。 |
| LLM 适配 | `services/llm_service.py`、`config.py`；OpenAI SDK 兼容协议调用 Qwen，默认配置 `qwen3.7-plus`。未验证供应商当前模型可用性、真实质量与成本。 |
| 前端 | Next.js 16.2.9 / React 19.2.4 / TypeScript / Tailwind；上传、报告、题库、画像页面。画像后端占位，前端雷达包含随机值，题库失败会降级示例题。 |

## 验证情况

- 本次环境：Windows PowerShell；项目 venv Python 3.12.7，Node v22.15.0，npm 10.9.2。
- `frontend` 下 `npm.cmd run check`：在沙箱外退出 0，lint、显式类型检查、生产 build 全部通过；恢复 build 的类型校验，Geist 字体从固定 npm 包本地打包。沙箱内 Turbopack 工作进程连接受限，不能作为业务编译失败结论；未做浏览器验收。
- 解析器工厂初始 8 passed / 5 failed 已修复：测试替身原先只 patch 模块名，未替换分派映射保存的函数引用；现在改为临时替换映射条目，精确验证路径/异常传播。工厂 13 项全部通过，生产解析器代码未改。
- API 初始化等待已通过受限/非受限环境对照定位为沙箱回环连接阻碍；沙箱外实际重跑 **26 passed / 1 warning**。
- 新入口 `python scripts/check_backend.py` 在现有 venv 与独立空 venv（只安装 requirements-ci.txt）中均为 **62 passed / 5 skipped / 1 warning**；空环境 `pip check` 通过。3 项 skip 缺 PDF fixture、2 项 DOCX 是旧测试显式 skip。警告为 Starlette/httpx 弃用提示，未忽略或当作错误修复。
- 离线入口不加载 .env、使用虚假配置、阻止外部 socket，仅允许回环；沙箱内预检约 3 秒返回环境错误，不再挂在 TestClient 初始化。
- 历史记录：`docs/api-workflow-test-record.md` 记载 2026-10-18 API 回归 26 passed / 1 warning，仅属历史。
- 未运行：真实 Qwen、全测试集、浏览器 SSE 时序/代理、多人并发、线上可用性；本次不使用付费模型资源。远程 CI 状态在 daily 更新，不将本地通过等同远程通过。

## 工程缺口与阻碍

1. S1：本地回归基线已建立；CI 配置含 Ubuntu/Windows 后端、Ubuntu 前端，远程运行状态见 daily。
2. P0（公开演示前）：`api/main.py::_session_store` 为全局字典，缺少会话隔离、持久化、并发版本保护；不得当成多用户服务。
3. P1：CI 已配置；Docker/Compose 或云部署配置仍未实现，CORS 仅允许本地前端；缺少线上 SSE、超时和重启恢复验收。
4. P1：示例降级与画像占位需清晰呈现；真实模型效果、耗时、token/cost 尚无本次可复核评估。
5. 后续按需求判断认证、限流、存储、任务队列；无依据加入 RAG、Agent、向量库或微服务。

`alembic/`、`evals/`、`scripts/` 目录只发现忽略的历史 `.pyc`，不能计为当前迁移、评估或部署能力。

## 接续入口

- 自动化：每日 12:00，北京时间，ACTIVE，本地项目独立新聊天；配置已回查，首次实际执行待验证。
- Q-001 已于本聊天 2026-10-19 用户“确认使用该首阶段线路”明确确认，范围为 S1（B-001–B-003），包括必要检查、提交和向现有授权远程分支推送。当前聊天负责 tests、质量门禁、CI 和相关文档。
- 待决：Q-002 演示会话/持久化边界；Q-003 何时做效果评估及付费用量审批。它们不阻碍 S1，仍不在本次开发范围。
