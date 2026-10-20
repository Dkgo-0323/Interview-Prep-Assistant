# 当前状态

更新：2026-10-20 22:52（Asia/Shanghai）；详情见 [当天记录](daily/2026-10-20.md)。状态：S1 已交付；用户确认的 B-006a 方案 A 已完成，本地/浏览器与功能提交远程 CI 均通过，已推送。Q-002/Q-003 及其他 S2 范围仍待决。

## 2026-10-20 最新核对

- **22:51 当前交付**：B-006a 采用 A（用户原文“采用A”）；画像页明确尚未开放，移除占位生成入口与虚构评分/薪资展示，保留首页、岗位匹配分析和题库入口。底层占位 API、共用组件和会话设计未改。功能提交 `faa2458b4b02adc4ce626bd976f00e129bcc7db9` 已推送当前授权分支。
- 本次新增验证：允许进程通信环境的 `frontend/npm.cmd run check` 全部通过；headless Edge 在本机生产服务验证直接访问、刷新、无画像 API/图表/生成按钮、移动布局和导航通过，桌面/移动截图已复查。导航到其他页面时 API 全拦截为 503，无真实后端/模型调用；未声称验证真实画像或其他页面的模型效果。临时服务已停止。
- [本次功能提交 CI](https://github.com/Dkgo-0323/Interview-Prep-Assistant/actions/runs/39442836760) 已核验 success，SHA 为 `faa2458`，两个后端与前端三个 job 均通过。本轮仅一个小功能，不按原 4–5+ 提交期望拆碎实现；之后仅文档交接提交的 SHA/推送状态以本聊天最终报告与 Git 为准。

以下保留本日早期核验/候选历史，后续时间记录优先；原有 dirty 文件保持不变。

- **22:26 最新规划修正**：用户反馈 10–18h 单次范围过大；该数值改按 S2 阶段估算理解。以后每天只推荐一个约 1–3h 的独立可验收主任务（包含验证/回填），过大再拆。本日先推荐 B-006a 画像占位诚实呈现（1–2h），可独立讨论；具体功能尚未确认。Q-002 不再作为要求一次批准整个 S2 的问题，仍保留会话/持久化技术选择待决。详见 daily 22:26 追加记录；无功能开发/提交/推送。

- 当前分支 `codex/qwen-provider-migration`，HEAD `054940b80f8e8b58143378f7692c2ed89292fa1b`；GitHub API 读取远程 ref 与本地一致。原有日志、两份未跟踪文档及 test-results 保留；暂存区空。
- 本次在允许本机回环的环境运行 `.\venv\Scripts\python.exe scripts/check_backend.py`，Python 3.12.7，退出 0：**62 passed / 5 skipped / 1 warning（5.96s）**。沙箱内同命令被 socketpair 超时挡住，业务测试未执行；保留执行器 exit 1 与源码 return 2 的差异。未盲跑全测试目录，未产生真实模型用量。
- [当前 HEAD 的远程 CI](https://github.com/Dkgo-0323/Interview-Prep-Assistant/actions/runs/39227494548) 为 completed / success，三个 job 成功。这是 10-19 运行、10-20 只读核验；今天未本地重跑前端或触发新 CI。
- 重新核查代码：共享全局字典、长操作晚到写回、占位画像及随机雷达仍存在；题库错误区**已有**示例题提示，B-006 应保留并完善，不误报为完全无标识。尚无跟踪的部署配置或本次验证过的线上 URL。
- 本聊天负责本轮四份规划文档。有限聊天列表中其他相关聊天为 notLoaded，已读 S1/API 交付 turn completed；worktree 仅当前 checkout。外部编辑器、更早聊天/其他机器情况未知，不能推断无人开发。开发前须再次核对范围。
- Q-001 / B-001–B-003 已完成；没有已确认未完成的跨天功能。Q-002 推荐匿名 Cookie、进程内 TTL/容量、输入版本/操作标识保护和占位来源标识（B-004–B-006，10–18h），明确单进程、重启需重传；持久化为备选，**未决策**。Q-003 真实模型评估/用量继续待决。
- 调研：百度两个校招岗位列表职责可读，完整任职要求未取得；Apple 详情失效、腾讯详情空，均未宣称在招。已读两个开源项目固定提交文件，成本/替代与限制见当天 daily。
- 已观察到本次自动化在新的独立项目聊天启动；没有据此宣称精确在 12:00:00 执行或以后运行必然成功。未改调度配置。

以下保留 2026-10-19 交付快照与历史验证；其中“本次”均指 10-19，最新事实以上述 10-20 记录为准。

## 仓库快照

- 分支 `codex/qwen-provider-migration`；HEAD `4d5a0edf8b937e60ff8e2ed94e6b9e992837a5d6`。
- 上述 HEAD 为初始化基线；S1 代码/CI 验收提交为 `1e212983b8fc6b1737465ff2dcc11529a5d97336`，已推送。后续仅文档回填的 HEAD 请用 git 核对。
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
- [远程 CI 首轮](https://github.com/Dkgo-0323/Interview-Prep-Assistant/actions/runs/39227131294) 整体 completed / success，Windows/Ubuntu 后端离线与前端 lint/typecheck/build 三个 job 均成功，验证代码提交 `1e21298`；后续文档回填提交状态见 daily 和本聊天最终报告。
- 未运行：真实 Qwen、全测试集、浏览器 SSE 时序/代理、多人并发、线上可用性；本次不使用付费模型资源。

## 工程缺口与阻碍

1. S1 已解决初始回归与构建阻碍，相关 CI job 通过；剩余跳过项、弃用警告及浏览器/真实模型覆盖不应被算作完成。
2. P0（公开演示前）：`api/main.py::_session_store` 为全局字典，缺少会话隔离、持久化、并发版本保护；不得当成多用户服务。
3. P1：CI 已配置；Docker/Compose 或云部署配置仍未实现，CORS 仅允许本地前端；缺少线上 SSE、超时和重启恢复验收。
4. P1：示例降级与画像占位需清晰呈现；真实模型效果、耗时、token/cost 尚无本次可复核评估。
5. 后续按需求判断认证、限流、存储、任务队列；无依据加入 RAG、Agent、向量库或微服务。

`alembic/`、`evals/`、`scripts/` 目录只发现忽略的历史 `.pyc`，不能计为当前迁移、评估或部署能力。

## 接续入口

- 自动化：每日 12:00，北京时间，ACTIVE，本地项目独立新聊天；配置已回查，首次实际执行待验证。
- Q-001 已于本聊天 2026-10-19 用户“确认使用该首阶段线路”明确确认，范围为 S1（B-001–B-003），包括必要检查、提交和向现有授权远程分支推送。该范围已交付，完成文档回填后释放 tests、质量门禁、CI 的修改范围；下一阶段尚未开始。
- 待决：Q-002 演示会话/持久化边界；Q-003 何时做效果评估及付费用量审批。它们不阻碍 S1，仍不在本次开发范围。

## 2026-10-20 22:43 B-006a 方案 A 已确认、验证中

本聊天用户最新回复“采用A”（turn 01a159bf-08bb-7351-b677-a9d9ce1fa5c4），批准的是画像尚未开放说明页及原讨论范围。页面修正已实现，前端 check/浏览器验证进行中，尚未提交/推送。B-006a 当前为进行中，不能继续按早期“候选/待确认”摘要理解。对应 ADR 0002；Q-002/Q-003、其他 B-006 剩余项未确认，S2 未整体完成。
