# API 链路测试记录（2026-10-18）

## 范围与固定输入

- `tests/fixtures/workflow/jd.txt`：虚构示例智能公司的 AI 工程师 JD。
- `tests/fixtures/workflow/resume.txt`：虚构候选人甲的脱敏简历。
- `tests/fixtures/workflow/llm_responses.json`：固定结构化模型返回值，综合分故意为 0，以验证业务层真实计算得到 77。
- 仅 Mock 两个路由引用的 `LLMService` 构造器及 `call`；真实执行 FastAPI TestClient、multipart 上传、TXT 文件解析、Pydantic 校验、三个分析器、题目生成器、SSE 编码、缓存读取和失效逻辑。
- 每个测试前后清理演示 session，避免顺序依赖；不调用付费模型，不需要 API Key。

## 接口契约和断言

| 场景 | 预期 |
| --- | --- |
| 只上传 JD，缺少简历 | SSE HTTP 200，仅 `error`，不调用 LLM |
| 两份文件上传但未分析 | 生成题目 HTTP 400，结果与题目缓存 HTTP 404 |
| 成功分析 | `jd_start → jd_done → resume_start → resume_done → gap_start → complete` |
| 结果恢复 | `/api/analyze/result` 返回与 complete.data 相同的报告 |
| 题目生成与恢复 | 生成 10 道有效题目，`/api/questions/cached` 与生成响应完全一致 |
| LLM 初始化失败 | SSE 仅 `error`，无报告 |
| 成功后重新分析，在任一阶段失败 | 最后事件为 `error`，无 `complete`；旧报告与旧题目不可读，生成题目 HTTP 400 |
| 成功后重新上传 JD 或简历 | 报告与题目缓存失效，生成题目 HTTP 400 |

## 失败复现与最小修复

首次运行新增测试：**3 failed, 6 passed**。三个失败均为重新分析失败后依然读到旧成功报告，关键断言输出如下（保留失败证据）：

```text
FAILED test_failed_reanalysis_cannot_recover_old_success[JDInfo-expected_steps0]
FAILED test_failed_reanalysis_cannot_recover_old_success[ResumeInfo-expected_steps1]
FAILED test_failed_reanalysis_cannot_recover_old_success[GapAnalysis-expected_steps2]
assert client.get("/api/analyze/result").status_code == 404
E AssertionError: assert 200 == 404
```

原因：分析只逐步写入成功结果，开始重试时不清除既有 `gap` 和 `questions`，失败后仍能读取或使用旧结果。

修复：`api/routes/analyze.py` 在新一轮流式分析开始、前置检查及初始化之前清除 `jd`、`resume`、`gap`、`questions`。保留原始上传文本，重试重新计算；此次没有重构会话系统。

## 验证命令与结果

```powershell
.\venv\Scripts\python.exe -m pytest tests/test_api_workflow.py tests/test_api_smoke.py -v -p no:cacheprovider --junitxml=test-results/api-workflow.xml
```

结果：**26 passed, 1 warning**（新增链路测试 9 项、原有冒烟测试 17 项）。警告为已安装 Starlette TestClient 对 httpx 的弃用提示，不影响断言。使用 `-p no:cacheprovider` 避开本地 `.pytest_cache` 权限问题。JUnit 输出位于 `test-results/api-workflow.xml`。

## 保留风险与后续验证

`api/main.py` 的 `_session_store` 是进程级全局字典，仅适用于单用户演示；没有多用户隔离、持久化或跨进程一致性。此次失效修复也不提供并发上传与分析之间的隔离或事务保证。后续需独立设计用户会话标识、版本控制及存储层，不能将当前实现作为具备隔离能力的 SaaS。

TestClient 验证 SSE 内容及事件顺序，不证明浏览器、代理中的实时传输或断线重连。真实 LLM、供应商连接和输出质量留待显式启用 `tests/test_qwen_integration.py` 单独验收；本次未执行。
