# 可复现质量门禁

适用主链路：FastAPI + Next.js。日期：2026-10-19。对应 S1 / B-001–B-003，用户确认出处见当天 daily。

## 后端离线入口

使用 Python 3.12，在独立虚拟环境安装固定的回归依赖（包括其传递依赖），避免依赖现有 venv 中历史数据库/部署包：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-ci.txt
.\.venv\Scripts\python.exe scripts/check_backend.py
```

Linux/CI 使用 `python -m pip install -r requirements-ci.txt` 和 `python scripts/check_backend.py`。此依赖集合用于回归，不替代包含旧 Streamlit 原型的完整 `requirements.txt`，也不是部署依赖清单；应用依赖变化后需要同步核对。

入口只运行审阅过的 6 个测试文件：

| 文件 | 验证内容 |
| --- | --- |
| `tests/test_parser_factory.py` | 扩展名路由、路径规范化、异常传播；PDF/DOCX 使用路由表替身 |
| `tests/test_pdf_parser.py` | 路径/损坏等边界，真实 PDF 样本不存在时明确跳过 |
| `tests/test_docx_parser.py` | 基本错误、表格/截断等；保留 2 项历史显式 skip |
| `tests/test_qwen_provider.py` | 构造配置、结构化请求参数、usage/费用边界；SDK 用 mock 替换 |
| `tests/test_api_workflow.py` | 真上传/解析与业务流程、SSE 事件序列、旧结果失效；仅 LLM 返回固定合成数据 |
| `tests/test_api_smoke.py` | 健康、接口校验、空会话等冒烟 |

入口不加载 `.env`，使用虚假模型配置；禁用第三方 pytest 自动插件和额外命令行环境参数，DEBUG 日志输出到控制台，不追加原有 `logs/app.log`。外部 IPv4/IPv6 socket 连接会被阻止，只允许本机 `127.0.0.1`/`::1`；这样误加真实 HTTP 模型调用会失败，而不是消费模型额度。新增测试必须先审阅，再加入显式清单。

入口先做有 3 秒超时的本地 socketpair 收发探测。Windows asyncio/TestClient 需要这个本地回环能力；如果当前沙箱拦截，入口报 `ENVIRONMENT BLOCKED` 并返回非零，不进入业务测试。用具有本地回环权限的终端重新执行，不要修改产品代码或 mock 事件循环以伪造通过。

pytest 使用本次进程独有临时目录，结束后清理自己创建的目录；不会清理用户的 test-results 或共享临时目录。CI job 还有总时限，卡住时输出 faulthandler 栈便于定位。

不要把 `python -m pytest tests` 当作纯离线入口，其他文件可能调用外部模型。当前门禁没有覆盖真实 Qwen 质量、浏览器实时 SSE、多人隔离、所有 PDF/DOCX 格式和完整测试目录。

## 前端入口

Node.js 22，在 `frontend/` 执行：

```powershell
npm ci
npm run check
```

`check` 顺序执行 `lint`、`typecheck`（`next typegen` + `tsc --noEmit --incremental false`）、`build`。删除了 `ignoreBuildErrors: true`，生产构建也恢复类型检查。不得用跳过错误、虚构字体响应或删除失败步骤换取绿色结果。

原 `next/font/google` 在生产构建时需要下载字体，当前环境请求 Google Fonts 失败；改用固定版本 `geist@1.8.1` 的 `GeistSans`/`GeistMono`，字体由 npm 依赖本地打包，CSS 变量继续使用 `--font-geist-sans` / `--font-geist-mono`。依赖安装需要 npm 网络访问，安装完后构建不再依赖 Google Fonts。

## CI

[quality.yml](../../.github/workflows/quality.yml) 对 push、pull_request 和手动运行触发：

- Backend offline：Ubuntu、Windows，Python 3.12，安装 requirements-ci.txt 后执行同一个离线入口。
- Frontend lint, types and production build：Ubuntu、Node 22、npm ci 后执行 npm run check。

工作流权限为 `contents: read`，不配置模型密钥，不部署、不发布。push/PR 的并发新运行会取消同一引用的旧运行。工作流本身不强制分支保护，是否设为合并必需检查另行确认；不把“已写 YAML”当作“远程 CI 已通过”。本次实际运行结果、SHA 与远程 run 链接见 daily。

实现参考（访问：2026-10-19）：[GitHub Python CI](https://docs.github.com/en/actions/tutorials/build-and-test-code/python)、[GitHub Node.js CI](https://docs.github.com/en/actions/tutorials/build-and-test-code/nodejs)、[官方 Geist 字体包](https://github.com/vercel/geist-font)。Next.js 配置另核对安装版本 `node_modules/next/dist/docs/` 的 TypeScript、CLI 和字体指南。
