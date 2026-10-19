# 当前状态

更新：2026-10-19（Asia/Shanghai）；详情见 [当天记录](daily/2026-10-19.md)。状态：用户已确认 S1 回归基线与 CI，B-001–B-003 开发进行中。

## 仓库快照

- 分支 `codex/qwen-provider-migration`；HEAD `4d5a0edf8b937e60ff8e2ed94e6b9e992837a5d6`。
- origin：`git@github.com:Dkgo-0323/Interview-Prep-Assistant.git`；本地上游引用为 `origin/codex/qwen-provider-migration`，本次未 fetch/验证远程连通性，不能保证远端实时一致。
- 开始时已有：`logs/app.log` 修改；未跟踪 `docs/interview_mock_exam_2027_project_reverse_engineering.md`、`docs/resume_project_analysis1.md`、`test-results/api-workflow.xml`。均保留，不纳入本次提交。
- 本次只新增 `docs/development/`，配置应用正式自动化；未修改功能代码、未提交、未推送。
- 本地 worktree 清单只有当前 checkout；应用有限聊天快照未发现另一个明确正在开发本仓库的聊天，但列表不完整，不能证明没有并行工作。新一轮仍须核对。

## 代码证据支持的能力

| 能力 | 证据与边界 |
| --- | --- |
| 上传/解析 | `api/routes/upload.py`、`core/parsers/`；PDF/DOCX/TXT、10 MB 校验和临时文件清理。本次未浏览器验收各格式。 |
| 结构化分析/SSE | `api/routes/analyze.py`、`core/analyzers/`、`models/schemas.py`；分阶段事件与 Pydantic 契约。本次尚未取得 API 回归完成结果。 |
| 题目生成/缓存 | `core/generators/question_generator.py`、`api/routes/questions.py`；分批、去重、补足，缓存为进程内状态。 |
| LLM 适配 | `services/llm_service.py`、`config.py`；OpenAI SDK 兼容协议调用 Qwen，默认配置 `qwen3.7-plus`。未验证供应商当前模型可用性、真实质量与成本。 |
| 前端 | Next.js 16.2.9 / React 19.2.4 / TypeScript / Tailwind；上传、报告、题库、画像页面。画像后端占位，前端雷达包含随机值，题库失败会降级示例题。 |

## 验证情况

- 本次环境：Windows PowerShell；项目 venv Python 3.12.7，Node v22.15.0，npm 10.9.2。
- `frontend` 下 `npm.cmd run lint`：退出 0，通过；不代表构建、类型或浏览器链路通过。
- 解析器工厂：首次执行受默认 pytest 临时目录权限影响产生 13 个 setup error；换本次专用可写 `--basetemp` 后，`tests/test_parser_factory.py` 为 **8 passed / 5 failed**。失败表现为测试 mock 未拦截、真实解析器访问不存在的 PDF/DOCX；见 daily 中根因假设，尚未修复。
- API 离线回归两次均在 TestClient 初始化阶段等待，已中断，无通过结论。禁用第三方 pytest 插件并指定可写临时目录仍复现；faulthandler 显示 Windows asyncio 创建 socketpair 时停在 socket.accept，属于本机运行环境阻碍线索，尚未证明根因或业务通过。完整复查命令见 daily。
- 历史记录：`docs/api-workflow-test-record.md` 记载 2026-10-18 API 回归 26 passed / 1 warning，仅属历史。
- 未运行：真实 Qwen、全测试集、生产构建、浏览器 SSE 时序/代理、多人并发、线上可用性；本次不使用付费资源。

## 工程缺口与阻碍

1. P0：解析器工厂测试不绿；离线回归可重复性需确认，CI 尚无可复现基线。
2. P0（公开演示前）：`api/main.py::_session_store` 为全局字典，缺少会话隔离、持久化、并发版本保护；不得当成多用户服务。
3. P1：未发现跟踪的 CI、Docker/Compose 或云部署配置；CORS 仅允许本地前端；缺少线上 SSE、超时和重启恢复验收。
4. P1：示例降级与画像占位需清晰呈现；真实模型效果、耗时、token/cost 尚无本次可复核评估。
5. 后续按需求判断认证、限流、存储、任务队列；无依据加入 RAG、Agent、向量库或微服务。

`alembic/`、`evals/`、`scripts/` 目录只发现忽略的历史 `.pyc`，不能计为当前迁移、评估或部署能力。

## 接续入口

- 自动化：每日 12:00，北京时间，ACTIVE，本地项目独立新聊天；配置已回查，首次实际执行待验证。
- Q-001 已于本聊天 2026-10-19 用户“确认使用该首阶段线路”明确确认，范围为 S1（B-001–B-003），包括必要检查、提交和向现有授权远程分支推送。当前聊天负责 tests、质量门禁、CI 和相关文档。
- 待决：Q-002 演示会话/持久化边界；Q-003 何时做效果评估及付费用量审批。它们不阻碍 S1，仍不在本次开发范围。
