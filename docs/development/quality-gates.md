# 可复现质量门禁

现行计划见 [plan](plan.md)，新的实际执行结果记 [journal](journal.md)。本文件是技术手册，按检查实现变化更新，不承担另一份每日状态；下文涉及旧daily的语句/链接是历史验收来源，不是继续生成逐日文件的要求。

## 2026-10-22 可信会话验收

后端入口新增审阅过的`tests/test_api_sessions.py`，仍不读.env、不允许外部连接。会话集合使用两个独立TestClient、合成样例、可控时钟与线程阻塞点；覆盖Cookie身份/匿名隔离、滑动闲置过期、容量拒绝/释放、重启失效、重传/清除/过期与分析三个阶段或题目生成交错、重分析使旧题目失效、重复任务、取消等待后的忙槽、上传晚到。无需真实模型和新服务。健康接口现在仅返回status，不返回session_keys。

前端API契约集合现12项，新增共享初始化/credentials、410不重放工作且可显式重试、容量失败不发后续请求、清除失败保留错误、报告恢复不启动SSE、SSE凭证及卸载取消。实际运行结果只记journal，下面保留旧日期基线。

生产浏览器可复现：先确认测试端口空闲，给前端构建进程明确设置`NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`后执行`npm run check`，再启动生产前端`npm run start -- --hostname 127.0.0.1 --port 3168`。另开终端在根目录用`python scripts/serve_offline_demo.py --port 8000 --capacity 2 --frontend-origin http://127.0.0.1:3168`启动全新合成模型后端。该脚本只绑定回环、阻止外部socket、替换dotenv加载与模型工厂，真实执行路由/解析/业务逻辑；它不是生产启动命令。如果已有构建覆盖了API端口，先从浏览器请求确认实际本机地址，让测试服务匹配，不读取或改写用户环境文件。

在可用Playwright/Edge环境运行`node scripts/check_sessions_ui.cjs http://127.0.0.1:3168 <独立产物目录>`（外部包目录通过NODE_PATH指定），每次用新合成服务避免残留会话占用2个槽。验证并行初次上传共用初始化、HttpOnly/REST/SSE、首页/报告/题库刷新、访客隔离、第三访客满额不生成、清除仅影响自己；过期UI使用拦截410，真实TTL/重启由后端测试覆盖。JSON与桌面/390px截图保留在指定产物目录，用完停止本次服务器。`scripts/check_questions_ui.cjs`仍全API拦截，补充初始化响应，原10场景继续回归。两种浏览器检查不调用真实供应商，也不等于公网部署/SSE代理验收。

## 2026-10-21 B-006b 验证增量

前端 `npm run check` 现按 lint → typecheck → **test:api** → build 执行；CI 原调用同一入口，因此无需改 workflow。`npm run test:api` 等同根目录的 `node --test scripts/test_frontend_api.cjs`，使用已安装 TypeScript 编译器和 VM/fetch 替身，验证 404/502/503/422/网络错误与成功载荷，不联网、不读取本地环境配置。完整类型正确性由 typecheck 负责。

生产页面另有 `scripts/check_questions_ui.cjs`，需要已可用的 Playwright 与浏览器，不在此脚本内安装依赖。先在 frontend 启动 `npm run start -- --hostname 127.0.0.1 --port 3168`，再在项目根目录执行 `node scripts/check_questions_ui.cjs http://127.0.0.1:3168 <本次独立产物目录>`。若 Playwright 位于外部依赖目录，给该终端设置对应 NODE_PATH；浏览器默认已安装的 Edge，可通过 PLAYWRIGHT_CHANNEL 指定。脚本只接受本机页面，全部 /api/ 请求使用固定合成响应并计数，阻止其他外部资源；产出 JSON 与桌面/移动截图。无后端或真实模型调用，不能替代真实供应商/多人/部署验收。用完停止自己启动的服务器。

覆盖缓存成功、404、非 JSON 404、500、断网、非 JSON 502、200 空/畸形响应、显式重试失败后成功、首次生成失败共十场景；检查来源、生成请求次数、刷新/筛选/翻卡/收藏、换题集清空收藏与移动溢出。实际运行结果见当天 daily。以下保留 S1 的原始环境与机制说明。

适用主链路：FastAPI + Next.js。日期：2026-10-19。对应 S1 / B-001–B-003，用户确认出处见当天 daily。

## 后端离线入口

使用 Python 3.12，在独立虚拟环境安装固定的回归依赖（包括其传递依赖），避免依赖现有 venv 中历史数据库/部署包：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-ci.txt
.\.venv\Scripts\python.exe scripts/check_backend.py
```

Linux/CI 使用 `python -m pip install -r requirements-ci.txt` 和 `python scripts/check_backend.py`。此依赖集合用于回归，不替代包含旧 Streamlit 原型的完整 `requirements.txt`，也不是部署依赖清单；应用依赖变化后需要同步核对。

入口只运行审阅过的7个测试文件（2026-10-22加入会话集合）：

| 文件 | 验证内容 |
| --- | --- |
| `tests/test_parser_factory.py` | 扩展名路由、路径规范化、异常传播；PDF/DOCX 使用路由表替身 |
| `tests/test_pdf_parser.py` | 路径/损坏等边界，真实 PDF 样本不存在时明确跳过 |
| `tests/test_docx_parser.py` | 基本错误、表格/截断等；保留 2 项历史显式 skip |
| `tests/test_qwen_provider.py` | 构造配置、结构化请求参数、usage/费用边界；SDK 用 mock 替换 |
| `tests/test_api_workflow.py` | 真上传/解析与业务流程、SSE 事件序列、旧结果失效；仅 LLM 返回固定合成数据 |
| `tests/test_api_smoke.py` | 健康、接口校验、空会话等冒烟 |
| `tests/test_api_sessions.py` | Cookie/独立访客、TTL/容量/重启、三个分析阶段和题目生成的重传/清除/过期交错、取消后忙槽与上传晚到保护；全部替身模型 |

入口不加载 `.env`，使用虚假模型配置；禁用第三方 pytest 自动插件和额外命令行环境参数，DEBUG 日志输出到控制台，不追加原有 `logs/app.log`。外部 IPv4/IPv6 socket 连接会被阻止，只允许本机 `127.0.0.1`/`::1`；这样误加真实 HTTP 模型调用会失败，而不是消费模型额度。新增测试必须先审阅，再加入显式清单。

入口先做有 3 秒超时的本地 socketpair 收发探测。Windows asyncio/TestClient 需要这个本地回环能力；如果当前沙箱拦截，入口报 `ENVIRONMENT BLOCKED` 并返回非零，不进入业务测试。用具有本地回环权限的终端重新执行，不要修改产品代码或 mock 事件循环以伪造通过。

pytest 使用本次进程独有临时目录，结束后清理自己创建的目录；不会清理用户的 test-results 或共享临时目录。CI job 还有总时限，卡住时输出 faulthandler 栈便于定位。

不要把`python -m pytest tests`当作纯离线入口，其他文件可能调用外部模型。后端门禁覆盖匿名隔离，但不覆盖真实Qwen质量、浏览器实时SSE、所有PDF/DOCX格式和完整tests；本机浏览器验收另行执行，仍不覆盖公网代理/真实供应商。

## 前端入口

Node.js 22，在 `frontend/` 执行：

```powershell
npm ci
npm run check
```

`check`顺序执行`lint`、`typecheck`（`next typegen` + `tsc --noEmit --incremental false`）、`test:api`、`build`。删除了`ignoreBuildErrors: true`，生产构建也恢复类型检查。不得用跳过错误、虚构字体响应或删除失败步骤换取绿色结果。

原 `next/font/google` 在生产构建时需要下载字体，当前环境请求 Google Fonts 失败；改用固定版本 `geist@1.8.1` 的 `GeistSans`/`GeistMono`，字体由 npm 依赖本地打包，CSS 变量继续使用 `--font-geist-sans` / `--font-geist-mono`。依赖安装需要 npm 网络访问，安装完后构建不再依赖 Google Fonts。

## CI

[quality.yml](../../.github/workflows/quality.yml) 对 push、pull_request 和手动运行触发：

- Backend offline：Ubuntu、Windows，Python 3.12，安装 requirements-ci.txt 后执行同一个离线入口。
- Frontend lint, types and production build：Ubuntu、Node 22、npm ci 后执行 npm run check。

工作流权限为 `contents: read`，不配置模型密钥，不部署、不发布。push/PR 的并发新运行会取消同一引用的旧运行。工作流本身不强制分支保护，是否设为合并必需检查另行确认；不把“已写 YAML”当作“远程 CI 已通过”。本次实际运行结果、SHA 与远程 run 链接见 daily。

实现参考（访问：2026-10-19）：[GitHub Python CI](https://docs.github.com/en/actions/tutorials/build-and-test-code/python)、[GitHub Node.js CI](https://docs.github.com/en/actions/tutorials/build-and-test-code/nodejs)、[官方 Geist 字体包](https://github.com/vercel/geist-font)。Next.js 配置另核对安装版本 `node_modules/next/dist/docs/` 的 TypeScript、CLI 和字体指南。

## S3独立数据库门禁

新增`History PostgreSQL and backup restore` job：Ubuntu临时PostgreSQL16、合成身份/文本/报告，运行`tests/test_history_postgres.py`，真实并发连接及pg_dump/pg_restore。它独立于无数据库的七文件离线集合，不把模型调用加入默认tests。安装`requirements-history.txt`；CI缺数据库或客户端工具必须失败。范围/本地命令/恢复边界见[history-storage](history-storage.md)。当前历史模块未接入HTTP和页面，数据库测试不等于OAuth/端到端/生产恢复验收。
