# 研究与开发记录（按周）

现行计划/工作约定见 [plan](plan.md)，使用/运行见根 [README](../../README.md)。在此按周记录研究、每日有意义交付及必要实施决定，不复制完整计划或生成逐日文件。时间统一Asia/Shanghai；当前最终交接提交自身SHA/push/CI先记聊天与memory，下轮归档，避免自引用提交循环。

## 2026-10-19 — 2026-10-25（迁移首周）

### 周报基线：复用10-20/10-21研究，不是本次新调研

来自 [10-20历史记录](daily/2026-10-20.md)、[10-21历史记录](daily/2026-10-21.md) 的当时访问。迁移为周三，不重复例行研究，下次周一2026-10-26集中更新；以下不推为现在仍在招或最新版本。

| 直接来源 / 原访问日 | 原证据及可信边界 | 本项目关系 |
| --- | --- | --- |
| [Amazon10583340](https://amazon.jobs/en/jobs/10583340/software-development-engineer-early-career-2027-us)，10-21 | Software Development Engineer, Early Career - 2027 (US)，Jobs for grads；发布日期未知；当时完整官方详情，有Apply now/持续接收描述，未验证投递/名额，非中国校招资格 | 通用语言含Python/TypeScript、算法/数据结构、验证AI代码、CI/CD/排障，支持可验收工程成果，不推出必须AWS |
| [百度J100737/J101055官方列表](https://talent.baidu.com/jobs/list?recruitType=GRADUATE)，10-20/21 | 北京后端开发、AI测试开发；2027届校招；列表日期2026-07-21；只取得列表职责，未取得完整任职要求/投递状态 | 模型集成/稳定性、接口与AI评测资产；不造未读语言/数据库条款，不算两个完整JD |
| Apple失败核验，10-21：[200654019](https://jobs.apple.com/en-us/details/200654019-3278/software-engineer-apple-online-store-early-careers?team=CORSV)、[200669087](https://jobs.apple.com/en-sg/details/200669087-1052/early-careers-software-development-engineer?team=CORSV) | 前者导航壳、后者不存在/不可用；搜索索引不等于已读正文 | 不作在招/技能依据，保留失败，不为数量补造 |
| [fastapi/full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template)，10-21 | SHA `b1125d8839482cb7bbae603ddc6d0081bf87532e`；实读 [items.tsx](https://github.com/fastapi/full-stack-fastapi-template/blob/b1125d8839482cb7bbae603ddc6d0081bf87532e/frontend/src/routes/_layout/items.tsx)、[__root.tsx](https://github.com/fastapi/full-stack-fastapi-template/blob/b1125d8839482cb7bbae603ddc6d0081bf87532e/frontend/src/routes/__root.tsx) | 采用加载/空结果/错误分离思路，B-006b已应用；不移植TanStack路由或整套账号/数据库，避免替换Next架构维护成本 |
| [sysid/sse-starlette](https://github.com/sysid/sse-starlette)，10-21 | SHA `463210322ccfc208572c1703c27939d68fe9f21f`；实读 [sse_starlette/sse.py](https://github.com/sysid/sse-starlette/blob/463210322ccfc208572c1703c27939d68fe9f21f/sse_starlette/sse.py) 发送超时/ping/断连/关闭协调 | 后续SSE运行验收参考，未决定引库；不能自动取消同步线程或实现隔离 |

**采纳及理由**：围绕实际接口/页面状态验证，分清来源与错误，优先可靠性/隔离；现有离线门禁、画像边界和题库来源能支持可信展示。

**已有/缺口**：上传→解析→结构化分析/SSE→报告→题库练习存在，S1/B-006a/b交付；全局会话、晚到写回/重启语义仍有缺口，未验收公网部署/真实语义质量，具体状态只维护plan。

**路线调整**：没有新证据要求更换业务主线，继续Next/FastAPI/Qwen。调整工作方式为周一研究、阶段内自主推进，不堆框架。

**本周交付/依赖/验收**：S1/B-006a/b完成；本轮交付工作流迁移和真实交接；下一业务阶段Q-002确认目标/资料生命周期后再做隔离/旧结果保护，验收独立客户端和长操作交错。不预填本周会完成隔离或上线。

**暂不采纳**：整套模板/TanStack会增加重复路由、账号/存储维护；Redis/PostgreSQL未有持久化确认；sse-starlette未有真实代理/取消验收；岗位提及Agent/AWS不构成本项目需求。旧逐日估时不是新工作流的开发上限。

### 2026-10-19 回归与CI基线（历史归档）

用户Q-001确认“确认使用该首阶段线路”，详 [历史daily](daily/2026-10-19.md)、[ADR0001](decisions/0001-offline-quality-baseline.md)。目标是无付费模型也能回归上传/分析/题库。

| 完整SHA（均已推送当前授权分支） | 增量 |
| --- | --- |
| `da657ef0ee7d9debaee6ca7ee19b953980656d3d` | 解析器工厂测试替身，13项通过，生产解析器未改 |
| `69d8646832cf9721eac5365b2edc514c854a74f9` | 六文件离线allowlist与固定回归依赖 |
| `4a1c8ed97ae4b614f69fd737700122680b869beb` | 前端类型/构建门禁与本地字体 |
| `1e212983b8fc6b1737465ff2dcc11529a5d97336` | Windows/Ubuntu后端及前端CI |
| `054940b80f8e8b58143378f7692c2ed89292fa1b` | S1验证/CI交接 |

历史环境Windows/Python3.12.7、Node22.15.0/npm10.9.2；`python scripts/check_backend.py`在现有和独立venv均62 passed/5 skipped/1 warning，前端`npm.cmd run check`和远端三job通过。保留失败：沙箱socketpair阻碍TestClient；原工厂8通过/5失败为mock未替换缓存映射，修复后13通过；字体下载失败改为本地包。5项skip/弃用警告仍在，真实模型/多人/线上SSE未验证。本次迁移没有重跑这些业务检查。

### 2026-10-20 画像入口如实呈现（历史归档）

用户“采用A”，聊天`01a1577b-fbcc-7842-ba33-70495c9bcb9b`/turn`01a159bf-08bb-7351-b677-a9d9ce1fa5c4`，确认明确未开放页面，不是批准真实画像模型，覆盖更早歧义。

- 改动：移除占位生成/虚构评分薪资，保留分析/题库导航；底层API占位未改。[ADR0002](decisions/0002-profile-unavailable.md)、[历史daily](daily/2026-10-20.md)。
- 历史验收：允许本机进程通信环境`npm.cmd run check`通过；生产页headless Edge桌面/390px、刷新/导航通过，API全Mock；沙箱Turbopack通信失败单列。非公网/真实模型能力。
- 已推送功能`faa2458b4b02adc4ce626bd976f00e129bcc7db9`、交接`ebbb3d568097ae0a98c57b425a04a0b31ee52c6e`；[最终CI](https://github.com/Dkgo-0323/Interview-Prep-Assistant/actions/runs/39443361333)三job成功，Q-002/Q-003未确认。

### 2026-10-21 B-006b题库来源与缓存分流（已交付）

用户本聊天`01a15e7d-3173-7d73-b704-4b0427c49b8d`明确“确认 B-006b，继续开发”，目标是缓存错误不悄悄生成、用户知道题目来源。

- 链路：APIError保留HTTP status → 仅404或显式操作生成 → 页面独立显示缓存/本次生成/固定示例，题集切换清收藏。6项客户端测试接npm check，10场景Mock脚本保留；[ADR0003](decisions/0003-question-provenance-and-cache-errors.md)保留当时确认，同类普通实施细节以后记journal。
- 最终本地Windows/Node22.15.0/npm10.9.2/Next16.2.9，`frontend/npm.cmd run check` exit0（lint/typecheck/6项测试/七页build）；`node scripts/check_questions_ui.cjs http://127.0.0.1:3168 <独立产物目录>` headless Edge十场景exit0，无意外请求/pageerror，桌面/移动截图复查；API全合成、外部阻止，临时服务停止。
- 保留失败/修复：沙箱CSS worker通信失败；首轮8场景后自查修复200 null真假值分支，再完整check+10场景通过。网络/5xx/空或畸形200不自动POST；404才自动POST；显式失败→成功、筛选/翻卡/收藏/刷新、390px溢出验收通过。
- 已推送功能`61572df95393520fccfb3f9c38339c5b62c9835f`、交接`caeedbe1cd43aba718c00a873049461d48290609`；[功能CI](https://github.com/Dkgo-0323/Interview-Prep-Assistant/actions/runs/39608553120)、[最终HEAD CI](https://github.com/Dkgo-0323/Interview-Prep-Assistant/actions/runs/39609067202)三job均成功。较早规划阶段后端62/5/1、8.04s为同日历史；开发未本地重复后端，远程后端另行通过。
- 演示仅本机题库状态行为；真实模型质量、公网/多人未验收，下一阶段Q-002待决。本次文档迁移不把以上历史成功当新业务测试。

### 2026-10-21 工作流迁移（本聊天确认）

**目标/授权**：用户要求先确认理解，再回复“确认”；批准仅本项目原任务、文档/memory、检查和提交/普通推送，不开始新业务、不改VOC项目/任务。新规则取代每日例行研究、独立daily/prompt、多表同步、逐日A/B、每日1–3h小任务及提交数目标；已有交付/授权和Q-002/Q-003边界保留。

**实际配置**：23:06使用管理工具`automation_update mode=update id=interview-prep-assistant`成功，随后view；持久化`updated_at=1792595197309`。保留原ID/名称/创建时间、ACTIVE、北京时间每日12:00、本地独立新聊天、项目`30b254df-d398-43b1-bc43-ff9ac69d0764`/`D:\codefield\interview-prep-assistant`、`gpt-6.1-sol`/high；通知原无显式字段、未新增覆盖。系统China Standard Time（UTC+08:00）与Asia/Shanghai一致。未新建重复任务，不是只改说明声称更新。

**文档**：新增plan/journal承接真实状态/授权/风险与历史收据；根README直接导航；development README静态化、原文同目录完整归档。status/roadmap/backlog、三份daily及旧模板只加停止维护提示，原正文保留；daily加静态索引。ADR索引只要求长期架构决定单列，手册不再承担日常状态。

**核验/边界**：本地与实时远程基线`caeedbe1cd43aba718c00a873049461d48290609`一致；仅本聊天active，旧daily idle，历史聊天notLoaded，worktree仅当前，外部并行未知。四类用户文件只核对路径/哈希，不输出正文。配置逐字段、文档链接/规则、历史payload与用户文件哈希检查在本节追加；业务代码/依赖/CI未改，不重跑无关业务测试/模型/浏览器/部署。

**提交/下一步**：检查后只暂存本次具体文档并普通推送既有分支；本轮最终交接提交自身完整SHA/push/最终CI先记聊天和memory，下轮归档。配置/memory为本机任务状态，不伪称存在GitHub。未来定时触发/无人值守权限未实际运行验证；不自动开新业务，下一阶段S2目标需Q-002 interview。

#### 23:20 迁移交付核验（提交前收据）

- 已用任务管理工具更新原ID并view；Python3.12.7/tomllib读取持久化配置，ASCII转义JSON返回后与预期提示词逐字相同（2690字符）；ID/名称/创建时间/ACTIVE/每日12:00/local/项目路径绑定/模型high及未显式通知策略均保持。首轮非ASCII终端输出显示乱码造成比较误判，采用ASCII转义证明配置正文无误，没有绕过工具修写TOML。
- memory顶部已写当前授权规则与取代清单，原历史字节保留。明确取消旧每日JD/开源例行调研、daily/prompt、多表同步、逐日小任务审批/1–3h上限/提交数量目标；保留Q-001、B-006a/b真实交付和Q-002/Q-003未决边界。
- 实际检查命令：项目venv Python运行本聊天独立产物目录workflow-migration/validate.py（Windows/Python3.12.7），exit0；18份Markdown本地链接有效，8份历史payload逐字节哈希一致，4个原有用户文件哈希不变，配置字段保留且无通知覆盖，memory现行规则在首部，无业务实现文件变更。git diff --check -- README.md docs/development通过，仅既有LF/CRLF转换提示。首轮校验的关键词断言过窄，修正为文档实际“不设置提交数量”后通过，不是补造规则或业务测试。
- 验证产物在本聊天visualization/workflow-migration下，含preservation-baseline.json、validate.py、validation.json；不纳入仓库。没有新JD调研、业务测试、真实模型调用、浏览器或部署验证；旧测试数字仅作为有日期的历史归档，未来12:00新流程触发尚未验证。
- 文档/memory/配置本地工作已完成，仅待本次文档Git提交/普通推送及最终收据；提交前没有自己的新SHA，绝不提前写已推送。最终交接自身完整SHA/push/CI见本聊天和memory，下轮再归档journal，不再为此单独拆碎提交。没有启动下一业务阶段，交接后释放本轮文档编辑范围。

### 2026-10-22 可信会话：确认、实现与本地验收

**上轮收据归档**：迁移提交`63c32203035d847953e6819ee43209e8acf3d996`已普通推送`origin/codex/qwen-provider-migration`；[CI39624896935](https://github.com/Dkgo-0323/Interview-Prep-Assistant/actions/runs/39624896935)三job成功。本轮实时ls-remote仍为同一SHA，工具复核该CI三job；它是10-21历史CI，不是本次功能的新CI。GitHub deployments返回空数组，只能说明未取得平台记录/线上验收地址。迁移后已观察到本次新聊天执行，不能由11:54首次读取时间证明12:00准点触发。

**范围/并行核对**：启动时仅日志、两份未跟踪分析材料及test-results为原有改动，plan/journal干净、暂存为空；分支/HEAD/上游/origin及单checkout已核对。上轮相关聊天idle，其他可见历史聊天notLoaded，外部编辑器/其他机器活动未知；只读核查相关聊天，没有向其发消息。本轮负责`api/session.py`及API路由、前端API/上传/分析/题库状态、相关离线和浏览器验收脚本、README/Architecture/plan/journal/质量手册/ADR0004。用户四类原有文件仅核对路径和SHA256，不读正文；未读取环境文件或真实简历。

**必要确认**：本聊天`01a161bc-9751-7071-9f00-b1a1ea1ceae4`三题均明确选A：完整可信会话；HttpOnly匿名Cookie、单进程短期内存、闲置30分钟/最多100会话且可配置、重启丢失/满额拒绝新访客；旧结果作废、同类任务忙时提示，不自动排队。确认前只做核查/验收设计，确认后开始业务实现。长期取舍见[ADR0004](decisions/0004-anonymous-memory-sessions.md)。真实用量/Q-003和正式发布未获授权。

**为何现在做/实际链路**：公开演示前，A上传的资料必须不能被B读取；A重传或清除后，旧分析/题目不能回到新资料。前端共享初始化Promise → POST会话取得随机Cookie → REST/EventSource带同一身份 → FastAPI依赖解析独立Session → Operation捕获输入快照/revision → 线程返回与发布时再次检查存活/版本 → 本访客报告/题目。输入变更和重分析使旧结果失效；分文件上传序号阻止较早上传晚到覆盖，清除保留身份但作废旧任务。关闭等待不会停止供应商线程，忙槽等待线程实际完成再释放。健康检查不创建/暴露会话，API响应no-store。首页刷新恢复上传状态，分析页刷新优先恢复报告，只有404才启动分析；过期/容量失败不自动重放模型工作，提供恢复提示和清除入口。画像占位仍未开放，只接入身份依赖。

**针对实现的资料核验，非例行JD研究**：北京时间10-22实读[FastAPI Cookie](https://fastapi.tiangolo.com/advanced/response-cookies/)、[CORS](https://fastapi.tiangolo.com/tutorial/cors/)、[MDN Fetch credentials](https://developer.mozilla.org/en-US/docs/Web/API/Request/credentials)、[EventSource credentials](https://developer.mozilla.org/en-US/docs/Web/API/EventSource/withCredentials)。明确默认跨源请求不自动携带凭证、直接返回Response需在实际响应设置Cookie；REST/SSE均处理。按frontend/AGENTS读取已安装Next16.2.9的use-client和Server/Client Components指南。没有新库、Redis/数据库或VOC成果迁移。

**已运行验证/失败修复**：Windows、Python3.12.7、Node22.15.0/npm10.9.2、Next16.2.9。

- `.\venv\Scripts\python.exe scripts/check_backend.py`：沙箱socketpair失败，未跑业务测试；允许回环环境首轮82通过/8失败/5跳过/1警告。8失败是新交错用例的合成JD太短，被已有分析器校验提前拒绝、没有到达阻塞点；换用现有合成fixture后同一审阅入口**90通过/5跳过/1既有弃用警告，4.98s，exit0**。新增28项，七个文件仍阻止外部连接且禁dotenv；保留原缺少PDF/DOCX样例skip，不盲跑全tests。
- `frontend/npm.cmd run check`：允许本机worker通信环境通过lint、typegen/tsc、**12项客户端测试**、七页production build；首页恢复/视觉修复后再次运行，实际结果在下面最终核验补记。未跳过错误或修改用户环境文件。真实Qwen验收fixture仅适配新Cookie接口，未运行也不宣称通过。
- `scripts/check_questions_ui.cjs`：生产页headless Edge，API全部合成拦截，**原十场景exit0**，无意外请求/pageerror；补充bootstrap响应，来源/404/非404/示例/收藏等行为保留。
- `scripts/check_sessions_ui.cjs`：生产前端+真实本机FastAPI/解析/业务逻辑，LLM仅合成替身；首轮上传按钮等待失败，诊断为构建实际请求`127.0.0.1:8001`而测试服务在8000，且起初页面使用localhost。未读/改环境文件，从浏览器只观察本机host/port后，把合成服务对齐8001、两端统一127.0.0.1并允许确切3168 origin，五组场景exit0。包括首次双上传共用初始化、HttpOnly不可被JS读取、真实REST/SSE、首页/报告/题库刷新、独立访客、第三访客满额不生成、清除仅影响自己。过期UI单独拦截410；真实TTL/重启由后端可控时钟/替换store测试，非浏览器等待30分钟。初次服务启动GBK输出emoji报日志编码错误，合成脚本在导入应用前切UTF-8后消失；原服务已停。
- 初次截图复查发现过期错误页标题仍“正在分析中”，已改为“暂时无法完成分析”，并新增返回首页重新上传链接，正在最终生产页复验。失败JSON/截图保留于本聊天独立产物目录，不入仓库。

**演示/剩余边界**：可用两个独立浏览器上下文分别走上传→SSE报告→题库，刷新保留各自内容，A清除不影响B；全部模型效果为替身，不能证明真实Qwen质量/耗时/费用。闲置在访问时惰性清理，单worker、重启丢失符合已选方案；跨站/HTTPS/public代理、持久化、多实例和正式上线未验收。下一阶段建议先讨论可审阅部署目标/平台/费用及真实用量边界，再准备或发布；不默认扩展授权。

**交付状态**：代码和本轮本地验收已产生；待最后UI复验/文档与保留性检查后，只暂存本轮具体路径，核验当时分支/远程并普通推送。新交接提交自身完整SHA/push/最终CI收据按规则写本聊天和memory，下轮再归档，不提前虚填已推送，也不创建补自身SHA的空价值提交。

#### 12:24 最终实现核验

- 最后`npm.cmd run check` exit0：lint/typecheck、12项API客户端测试、七页build全部通过。最终合成服务`python scripts/serve_offline_demo.py --port 8001 --capacity 2 --frontend-origin http://127.0.0.1:3168`配合生产前端3168及`node scripts/check_sessions_ui.cjs http://127.0.0.1:3168 <本聊天独立目录>/sessions-ui-final`，五组场景exit0、无pageerror/外部请求。最终移动截图已目视确认错误标题与重新上传链接正确、390px无横溢出；题库桌面截图来源与排版正确。
- 验收产物在本聊天visualization下`sessions-ui-final`（最终真实本机HTTP/替身模型）、`sessions-ui`（早期失败/修复）、`questions-ui`（十场景全拦截）；不会纳入Git。所有本轮启动的前端/合成API进程已用各自session停止，端口8000/8001/3168查询无监听；Ctrl+C会使工具进程返回1，不是业务检查失败。
- S2完整已确认范围的实现和本地验收完成。后端90/5/1为本次真实离线结果，不沿用旧62；Qwen真实质量/预算、正式发布、跨站域名/代理/多实例仍未验证。下面Git/文档交付按最终收据规则处理，不再增加无关功能或例行调研。
- 交付检查：独立`validate_delivery.py` exit0，7份当前文档的35个本地链接有效、12份改动Python源码AST语法通过，4个用户原有文件SHA256与启动基线一致；三个相关CJS脚本`node --check`通过。`git diff --check`通过（只有LF/CRLF提示），旧status/roadmap/backlog/daily/templates无改动；提交前实时远端仍为`63c32203035d847953e6819ee43209e8acf3d996`，当前分支/既有origin未变，关联开放PR列表为空。准备一次连贯功能提交和普通推送，最终自身SHA/推送/CI见本聊天和memory，下轮归档。

#### 18:35 定时时间与每日解释要求调整

- 用户本聊天明确要求改为每日北京时间14:00、GPT-6.1 sol中等推理，并进一步要求每日复盘详细、明确解释当天实际推进的任务。先读当前memory/持久化任务和plan/journal/git状态；本地HEAD仍为下面已交付功能提交，文档干净，只有原有四类用户文件，未发现可见文档冲突，外部编辑活动未知。
- 通过`automation_update mode=update`更新既有任务；18:31:59持久化核验时间14:00/模型gpt-6.1-sol/medium，提示词开头由旧12:00对齐14:00。随后将每日交付要求改为具体任务与前后场景、核心调用链/状态/防错理由、真实验证与证据边界、阶段剩余及下一步的充分解释；完整读回3037字符，后一轮仅prompt/updated_at变化，其余字段逐项保留。没有新建任务、修改通知或其他项目，不将保存当作未来准点触发验收。
- plan同步当前设置和说明深度，不新建每日模板/prompt；本次仅必要规则文档/本机任务与memory，未新增业务代码，不重复运行无关业务测试或真实模型。文档检查/普通提交推送收据按本轮交接规则记录，当前提交自身SHA不预填。
- 归档今天S2真实交付：`6d561419588ef2d04b9769dc01eea389dbd9a6e4`已普通推送`origin/codex/qwen-provider-migration`；[CI39722459728](https://github.com/Dkgo-0323/Interview-Prep-Assistant/actions/runs/39722459728)对应精确SHA，12:28:02北京时间completed/success，Ubuntu后端、Windows后端、前端三job全部成功。本节是已有交付收据，不是18:35重新开发或重跑的成绩。

### 2026-10-23 阶段交接核对与S3集中决策（待回复）

- 今天主任务是关闭计划中S2仅“本地验收”的过时状态、接收另一聊天的main合并交接并提出下一阶段集中决策；没有新增业务功能，不把重复核对算成功能交付。周五未重复JD/同类项目研究。
- 负责范围仅plan/journal与本任务memory。启动时两份规划文档干净，暂存为空；单checkout、当前开发分支、origin/上游与近期提交已核对。README聊天`01a166c3-6279-71a1-a1e2-06fd595905b2`为idle，用户明确批准合并全部既有实现与截图；未向其他聊天发消息，外部编辑/其他机器未知。原日志、两份未跟踪材料和test-results保留，未读取隐私正文或环境文件。
- 收据归档：S2功能`6d561419588ef2d04b9769dc01eea389dbd9a6e4`已推送且CI39722459728成功；规则文档`ebcf5b925fabe21e1125cb788c997acbf26abf47`已推送且CI39764403624成功（上轮memory）。本日较早另一聊天交付README/三张合成链路截图`e44da22da39093f8a6e69edb33f12406a8db0fe7`，已推开发分支并经用户授权快进main。本轮实时`git ls-remote`核验两远端分支均等于该SHA，[main CI39895693460](https://github.com/Dkgo-0323/Interview-Prep-Assistant/actions/runs/39895693460)及开发分支CI39895471927均completed/success。它们不是本轮新增功能的成绩。
- 失败与恢复：沙箱gh网络连接失败、SSH进程权限失败；连接工具核验main和CI成功，但编码分支路径/deployments端点不支持。随后经允许的沙箱外只读命令成功读取两ref/CI/deployments（空数组）；不据此宣称线上已部署。
- S3 interview一次三题：部署包或同时公开演示；保留短期匿名单进程或增加长期存储；合成验收或另议真实模型评估。各题提供推荐和成本边界；尚未收到明确选择，推荐不能视作确认。未实施部署包、购买资源、调用真实模型或发布。现有README部署说明不等于可复现部署包或公网验收。
- 本轮验证仅Git状态/远端收据/文档diff及本地链接；不重复运行业务回归，无本轮新浏览器、构建、真实模型或部署成绩。历史90通过/5跳过和合成HTTP验收仍是各自日期证据。下一步收到三题选择后细化S3验收并连续开发；新平台/费用/凭据/发布必要时另行确认。

#### S3第一组决策已收到：B / B / A

- 用户本聊天明确选择：本阶段同时推进公开演示；需要长期保存与多设备恢复，先设计存储与身份；部署验收继续合成模型，真实Qwen范围/预算另议Q-003。覆盖上文“待回复”，不再把原推荐A/A/A当作选定方向。
- 第二组集中interview已发出，解释电脑上传后手机恢复的身份问题、最新数据与多份历史的范围差别、托管资源/费用/发布边界。分别提供账号/恢复码、最新一组/多份历史、先方案审批/既有资源选项及代价；仍待回复，未选择具体供应商或实施依赖设计。
- 本次仅记录目标与待决，未新增业务代码、付费资源或真实调用。plan/journal限定diff检查；原有用户文件不动。本次决策记录暂为本地未提交，待明确设计后随有意义增量交付；不冒称已推送。

#### S3第二组决策与具体托管提案

- 用户明确A/B/A：账号登录且首次一种方式，多份历史记录并主动删除，先调研具体托管/费用再确认资源，最终发布前再确认。覆盖上节第二组待回复；无供应商、费用或发布批准。负责仍为plan/journal/memory，延续本聊天未提交决策记录；当前开发分支/远端为`6a213fd2c041d17a316795a018c87dd35619c3b0`，暂存空，其他用户路径不动，外部并行未知。
- 本轮实读现有Architecture、session.py、frontend/lib/api.ts和依赖：数据仍为匿名进程内存；现有REST和原生EventSource共用Cookie，不能直接假设跨域Bearer头可用于原生EventSource。候选方案需同一鉴权边界、服务端身份验证、数据库owner/record/revision条件写入，保留S2防串数据语义；尚未更改代码。
- 北京时间2026-10-23针对性官方资料（非例行JD/同类项目研究）：[Supabase价格](https://supabase.com/pricing)正文明确Free 0美元、500MB数据库、5万MAU、闲置一周暂停；Pro起价25美元/月、首项目含在内及7天每日备份，额度/超额另计。[Render免费限制](https://render.com/docs/free)明确闲置15分钟休眠，不用免费层宣称稳定常驻。[Render Web Services](https://render.com/docs/web-services)支持FastAPI/Node及平台子域名；未实测本项目SSE或中国大陆访问。[Supabase GitHub登录](https://supabase.com/docs/guides/auth/social-sign-in/auth-github)及[SSR身份验证](https://supabase.com/docs/guides/auth/server-side/creating-a-client)支持托管OAuth与验证claims，不能只信未经验证的cookie/session字段。
- 提案（未选定）：Render两个应用+Supabase身份/PostgreSQL，先单worker。常驻预算约39美元/月=应用约14+Supabase Pro起价25；14来自[Render官方示例仓库QUICKSTART](https://github.com/render-examples/web-research-agent-template/blob/main/QUICKSTART.md)的两服务估算，不是本项目报价/实测容量。Render动态[价格页](https://render.com/pricing)本次正文未取得计算费表，不能将示例金额当实时精确价格；开通前必须核价，税/流量超额/域名不含，Qwen未计也未批准。[Vercel Hobby条款](https://vercel.com/docs/limits/fair-use-guidelines)限个人非商业，作为备选未采用；没有为了部署替换Next/FastAPI业务主线。
- 第三组集中确认已发：GitHub或邮箱验证码入口；20份可命名/重命名/选择/删除、保留文本与结果但不保留原文件或扩展原文件存储；托管组合本地/免费准备、常驻预算研究或改查大陆方案。推荐不当作批准。计划给出身份所有权→记录CRUD→条件写回→合成/数据库/浏览器→部署验收切片与明确证据边界，不先实现依赖供应商的代码。
- 上次交接`6a213fd2c041d17a316795a018c87dd35619c3b0`普通推送已核验；本轮`gh run view 39909440644`显示精确SHA completed/success，覆盖此前排队状态。此为前次文档提交的CI。当前仅文档检查，无新业务回归/构建/OAuth/数据库/浏览器或公网结果，无资源开通、真实调用、发布。

#### S3第三组已确认A/A/C：产品规则确定，拒绝原托管组合

- 用户明确GitHub登录和20份历史方案（命名/重命名/选择/主动删除、不保留原文件、满额先删不淘汰）；不采用Render/Supabase组合，要求先比较大陆访问更合适的托管方案，身份/存储供应商暂不锁定。前节原组合和约39美元只是已拒绝提案，不是实施依据。
- 北京时间10-23官方定向核验：[腾讯云Lighthouse产品页](https://cloud.tencent.com/product/lighthouse)正文取得内地2核2GB 45元/月、2核4GB 100元/月套餐，后者含100GB盘/7Mbps/1000GB月流量；页面另有新客109元年广告，未将其当常规价。香港tab未取得可靠报价；[阿里云轻量产品页](https://www.alibabacloud.com/en/product/simple-application-server)工具访问失败，不补造价格。地区本身不证明GitHub或本项目可达性，全部无实测。
- [阿里云备案流程](https://help.aliyun.com/en/icp-filing/basic-icp-service/user-guide/icp-filing-application-overview)官方正文说明内地服务器需接入商备案、香港/境外无需该备案；部署选内地时作为发布依赖，不替用户处理身份材料，不宣称已备案。[GitHub OAuth官方流程](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps)支持浏览器授权码流程，可由应用直接接入；不意味着已批准自行运维身份/数据库。
- 比较：内地单机候选Next+FastAPI+PostgreSQL+同源反向代理，费用可读、需要备案和数据库备份维护；香港单机同样可自管但报价/大陆可达性待实测；国内托管身份/数据库可减运维但GitHub兼容/价格待核验，暂不选服务。推荐内地2核4GB作初始预算而非容量保证，不在最小机器上宣称生产性能。
- 已发第四组两题：地区/备案路线；直接GitHub+自管PostgreSQL或托管身份/数据库。仅这些架构/维护选择待确认，不重问GitHub登录、20份历史和合成模型。没有新增代码或资源；本次修订先本地保留，等待选择后随下一实质增量交付。
- 前次提案文档提交`adfacc6d4b8fe770ea33c0b9842c2503f0d35f17`已普通推送原开发分支；其自身CI未核验，不能用较早39909440644成功替代。

#### S3第四组A/A确认，开始历史存储基础实现

- 用户确认腾讯云内地单机本地部署准备（100元月候选预算，购买/备案材料/发布另行确认），应用直接GitHub登录+同机PostgreSQL，承担维护和备份恢复。四组决策完毕，不再日常重问。ADR0005记录长期取舍；前节第四组待决已被覆盖。负责范围新增api/history.py、db迁移、requirements-history、显式迁移脚本、数据库测试/CI和相关手册，未编辑前端或用户原有路径。
- 实现：accounts以GitHub稳定数字ID关联内部UUID；preparations含owner/title/revision/输入文本/JSON结果和时间。全部访问按owner过滤；创建锁账号行后计数，20份上限覆盖不同连接并发；列表只返回元信息。输入替换按期望版本更新并清结果，发布按账号/记录/版本条件写入，重传/删除后旧任务不能恢复结果。无公开身份注入接口，登录尚未实现，调用方必须提供已验证身份。每次短事务独立连接，不持锁等待模型。
- 显式幂等迁移001与脚本不读dotenv、不自动运行于应用启动；可选psycopg依赖独立，不让默认匿名演示依赖数据库。新CI PostgreSQL16服务只用合成数据，九项真实数据库用例含并发20份/隔离/不同连接恢复/改名/分记录/版本与删除写回/名称/迁移，另有真实pg_dump→删除自建schema→pg_restore内容恢复。测试仅删除自己唯一命名schema，非用户数据库；不是生产备份计划。
- 本地Windows/Python3.12.7：AST解析通过；`.\venv\Scripts\python.exe scripts/check_backend.py`在允许回环环境exit0，90 passed/5 skipped/1既有Starlette warning，6.45s。缺PDF/DOCX样本skip保留。Docker CLI存在但Linux engine管道不存在，真实本地PostgreSQL与备份恢复未执行，不用替身冒充通过；交由新增远端临时数据库job验证。没有本轮前端改动，不重复前端门禁/浏览器；没有真实模型/资源/发布。
- 下一步：取得真实数据库CI收据并修复失败；再实现GitHub回调/安全会话、记录API与现有SSE/分析/题库绑定、重启中断/同版本重复任务保护和历史UI。数据库基础不等于用户已可登录或跨设备使用。备份异机目的地、调度/保留/恢复演练仍待部署落实，不宣称数据持久化已上线。

#### 用户启动Docker后补充本机真实数据库验收

- 用户告知已启动本机Docker。本轮沙箱访问Docker命名管道被拒绝，允许的沙箱外检查成功（Engine29.1.3）；发现已有interview-prep-postgres，未操作该容器。另建本任务标记的ipa-history-check-20261023临时容器，PostgreSQL数据仅tmpfs，不挂载用户目录/数据库。
- 仅复制api/__init__.py、api/history.py、迁移001和已审阅的test_history_postgres.py，容器内安装独立测试依赖；使用合成loopback DSN运行同一组测试：`python -m pytest tests/test_history_postgres.py -q -p no:cacheprovider`，9 passed，0.58s，exit0。实际容器Python3.14.8、PostgreSQL/pg_dump16.15、psycopg3.3.5/pytest8.3.4；不是Windows主机Python3.12，也不是此前远端CI成绩。真实dump/删除自建schema/restore及内容核对包含在9项中。
- 核验本轮容器ID与任务label后删除，仅本轮容器被清理，原interview-prep-postgres仍运行。无真实OAuth、业务HTTP/页面、模型调用或公网验收，不把容器测试当生产备份计划。没有产品源码变化；此验证记录本地保留，随下一实质开发提交，不为补收据单独创建提交。

### 2026-10-24 S3第二切片：GitHub后端身份边界

- 主任务/范围：延续已确认GitHub直接登录+自管PostgreSQL，交付可选后端OAuth与账号会话，不新增阶段/供应商/费用决定。周六无例行JD/同类研究。负责api/auth.py、api/routes/auth.py、main注册/显式启动、审阅测试入口与相关手册/README/plan/journal；前端与用户日志/材料/test-results未编辑。启动journal已有10-23 Docker收据，本轮保留随功能归档。单worktree，分支/上游/origin仍既有开发分支；相关10-23聊天notLoaded，本任务active，可见无同项目其他active聊天，外部/其他机器并行未知，未向聊天发消息。
- 启动实时远端：开发分支67d8f5f6cd521557f5c7786c7f2d87c1fd3909e6，main e44da22da39093f8a6e69edb33f12406a8db0fe7；前次历史基础提交已推送，[CI39927468141](https://github.com/Dkgo-0323/Interview-Prep-Assistant/actions/runs/39927468141)精确SHA completed/success。部署列表为空，不据此声称已有公网URL。沙箱SSH/gh失败，经允许的只读命令恢复核验。前次本机PostgreSQL9项/实际dump恢复见上节，不算今天新跑。
- 实际实现：GET登录/回调、GET me、POST logout及共用REST/SSE身份依赖；随机state绑定HttpOnly浏览器Cookie，S256 PKCE、10分钟/100项待登录（含在途）；回调一次消费、固定GitHub HTTPS端点换token并每次查/user稳定数字ID，再交既有仓库映射内部UUID。随机账号Cookie只存服务端哈希，30分钟绝对过期/100会话/单worker；满额拒绝不驱逐、重登录轮换本设备、退出保留其他设备。退出/新登录取消旧在途回调，避免退出后回调复活。令牌不返前端/不入库；错误不泄露供应商正文或DSN；退出要求精确Origin，回跳固定前端根路径。普通配置详情见登录手册，不新写ADR。
- 显式GITHUB_AUTH_ENABLED开关默认关闭；启用时从后端进程环境取得完整配置，可选导入历史驱动，不自动迁移、不读取dotenv。未使用真实OAuth凭据。现有匿名上传→解析→SSE结构化报告→题库仍在内存，未接账号历史。数据库已有accounts/preparations，账号会话仅本进程；重启后需重新登录，历史不因此删除。默认实现不代表永久登录/多实例批准。
- 具体资料只查[GitHub官方OAuth](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps)，北京时间10-24正文取得，确认state/S256/code_verifier及每次验证身份。采用官方流程，无新框架/服务。发布前日志必须屏蔽回调query，真实HTTPS/域名/GitHub可达性仍待验收。
- 验证：首次沙箱`venv/Scripts/python.exe scripts/check_backend.py`socketpair超时、exit2，业务未运行；允许本机回环后，Windows/Python3.12.7最终同命令exit0，117 passed/5 skipped/1既有Starlette警告，4.48s。新增27项合成GitHub transport+账号mapper测试，实际执行FastAPI路由；覆盖PKCE、Cookie/state/跨浏览器/Unicode伪造/重放/过期/拒绝、身份注入拒绝、错误关闭、旋转、两设备、容量及在途退出取消。审阅发现Unicode state直接字符串compare_digest会异常，改字节比较并新增回归；最终复验通过，未伪称观察到失败测试。跳过项为既有缺失PDF/DOCX样本。外网socket拦截+dotenv禁用保持，无真实模型/OAuth/DB回调集成。
- 文档修正：plan顶表和切片标题已对齐四组既有确认，不再写供应商待决；README准确标记仅后端基础；存储/质量/登录手册说明运行、会话边界及未来长任务必须重新核验会话/record/revision。没有前端改动，未本机重复npm check或浏览器，不把后端TestClient当浏览器Cookie验收。实际PostgreSQL用例交远端独立job重新执行。
- 可演示：离线测试展示完整授权回调与me/退出防错；界面没有新增登录按钮或历史列表。S3仍实施中。下一步可自主继续账号记录CRUD及所有权、绑定上传/分析SSE/题库与record/revision、重复/重启任务状态，再历史UI和两设备合成链路。真实凭据/GitHub连通、部署包/异机备份/备案资源/精确购买费用/正式发布仍未验收；Q003真实模型预算另行interview。当前提交自身SHA/普通推送/最终CI在本聊天及memory，下一轮归档，避免自引用提交。

### 2026-10-25 S3第三切片：账号历史记录管理API

- 主任务：接通已确认账号身份与PostgreSQL历史仓库，交付创建/列表/读取/改名/删除REST，不扩大到新阶段。周日不重复JD/同类项目研究。负责api/history_errors.py、api/routes/history.py、main启动/注册、history异常兼容、离线入口、新HTTP测试与数据库组合测试/CI，以及README/Architecture/plan/本journal和登录/存储/质量手册；前端、原日志/两份分析材料/test-results未编辑。源码确认主链仍Next.js+FastAPI+Qwen，Streamlit历史原型。
- 并行与基线：单worktree，原分支codex/qwen-provider-migration、上游与origin不变；本地/实时远端起始HEAD均f1cb07a15967b11bdcbcbe67e29287dc2485fa8e，main仍e44da22da39093f8a6e69edb33f12406a8db0fe7。前次功能已普通推送，[CI40069415715](https://github.com/Dkgo-0323/Interview-Prep-Assistant/actions/runs/40069415715)精确SHA completed/success，本轮只读核验，不当今天新成绩；部署列表为空。沙箱SSH/gh受限，获允许的只读命令恢复。今天较早聊天01a171a3-0b46-7fa3-b4ad-5b842f92b7c4为idle，读到workspace routing discovery failed，未交付代码；本聊天active，未见其他同项目active，外部活动未知。没有跨聊天消息。文档修改前git差异为空，无可见规划并发冲突。
- 实际实现：/api/records五种操作统一get_identity，owner始终取服务端账号Cookie；所有写操作要求与配置前端完全一致的Origin。标题严格字符串、trim后1–100字，拒绝owner/inputs/results/revision等额外字段与非法UUID。列表通过响应模型仅暴露元信息，详情按id取自己的文本/结果；没有全局current记录，改名不改变输入版本/结果，删除不自动选别的记录。缺失/他人记录统一404，20份满额409不淘汰，数据库异常安全503且不自动重试，防止响应丢失时重复创建；所有应用API沿用no-store。数据库异常类型拆到无驱动模块并保留旧导入兼容，使默认关闭账号时仍无需psycopg。显式启用时共享同一HistoryStore，关闭应用生命周期清理适配器；不自动迁移/导入匿名资料，不存原始文件。
- 场景与边界：后端现在可为同一账号建立多个命名准备记录；独立设备会话读取同一记录，改名互相可见，退出只撤销本设备。现有网页没有登录/历史入口，上传→内存文本→SSE结构化抽取/匹配报告→题库仍为匿名链；新记录输入/结果默认空，未接业务写入，因此不宣称用户已能跨设备恢复完整准备流程。没有真实OAuth/模型或正式发布。
- 本地验证：Windows/Python3.12.7，最终`venv/Scripts/python.exe scripts/check_backend.py`允许回环环境exit0，186 passed/5 skipped/1既有Starlette warning，23.24s；新增69项HTTP验收，使用真实注册路由/合成GitHub transport与账号映射/内存存储替身，覆盖增删读改、元信息过滤、越权同404、所有端点无身份/伪造/过期/退出、写Origin、严格输入与伪造字段、容量删除释放、存储失败不泄露且不重试、默认关闭与双客户端同账号改名/单设备退出。禁dotenv与外网guard保持。第一次沙箱socketpair超时，业务未运行；第一次允许环境186通过。增强真实双客户端场景后出现1 failed/185 passed：测试客户端默认跟随OAuth跳转而无location；设置follow_redirects=False后上述最终门禁通过。保留该失败，不将初次结果当最终结果。
- 独立真实数据库验收：在既有9项PostgreSQL/并发/dump恢复之外新增HTTP→实际HistoryStore组合用例，验证真实SQL创建、存储快照读取、改名、摘要过滤、他账号拒绝、删除及另一个仓库实例确认已删除；账号Cookie合成，不引入真实GitHub/模型。CI数据库job改装固定requirements-ci+history依赖，仍只跑审阅过的test_history_postgres.py。本机Docker engine管道不存在，未跑本机真实数据库或dump恢复；新组合测试交远端CI，结果待本聊天与memory最终收据，不能先标成功。
- 其他验证：7个Python AST、7份文档45个本地链接通过；限定路径diff检查通过。没有前端源码/页面变化，本机未重复npm check或浏览器，不将TestClient当浏览器验收；远端工作流仍覆盖前端门禁。可演示成果为合成测试/接口契约，不是新增网页。
- 下一步（已确认可自主继续）：上传/分析SSE/题库绑定账号record+revision，持久同版本任务占用与重启可重试状态、退出后晚到结果再次鉴权，再历史UI/双设备完整链路、部署包与异机备份恢复。真实凭据/GitHub可达性、实际HTTPSCookie/SSE、备案/购买/精确费用/正式发布仍需独立验收或决定，Q003真实模型预算待interview。本次提交自身SHA、推送与最终CI留本聊天/memory，下次实质增量归档，不另做自引用收据提交。

## 2026-10-26 — 2026-11-01

### 周一集中研究（访问日期：北京时间2026-10-26）

本周重新取得下列证据，不将上周研究冒充更新。当前主链源码仍Next.js+FastAPI+Qwen，Streamlit为历史原型；已确认S3继续，不增新阶段或框架。

| 官方岗位直接链接 | 届别/类别/日期与取得程度 | 一手要求及适用边界 |
| --- | --- | --- |
| [百度北京后端J100737官方列表](https://talent.baidu.com/jobs/list) | 官方列表标2027届（毕业2026-09-01至2027-08-31）、校招技术；列表日期2026-07-21。取得职责摘要与届别，未取得完整详情/任职要求；带推荐码URL先超时，基础URL成功 | 摘要明确模型接入、稳定性/排障/调优及AI辅助编程。页面列出不证明剩余名额或可投递；不从人数推出实际在招人数，不虚构Python/PostgreSQL要求 |
| [Amazon10583340](https://amazon.jobs/en/jobs/10583340/software-development-engineer-early-career-2027-us) | Early Career 2027 US / Jobs for grads；发布日期未知；取得官方详情职责及资格，Apply now/持续接收描述可见 | 通用语言含Python/TypeScript、数据结构/设计、验证AI代码、CI/CD与排障。用于工程能力对照，非中国校招资格判断；未实际投递，不保证名额 |
| [Atlassian25813](https://www.atlassian.com/company/careers/details/25813) | Software Engineer 2027 Graduate U.S.；2027-08前毕业，发布日期未知；官方详情职责/最低资格正文取得，Apply入口可见 | 端到端实现/测试/监测、API/云/AI应用项目、Python/Java等。Seattle hybrid且明确不提供工作签证、F1/J1不适用，不能当作用户可直接申请建议；未验证投递/剩余名额 |

| 开源仓库/锁定版本 | 实际模块与取得程度 | 采纳及成本/备选 |
| --- | --- | --- |
| [fastapi/full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template/tree/b1125d8839482cb7bbae603ddc6d0081bf87532e)（本次实时API取master SHA） | [backend/app/api/routes/items.py](https://github.com/fastapi/full-stack-fastapi-template/blob/b1125d8839482cb7bbae603ddc6d0081bf87532e/backend/app/api/routes/items.py)锁定正文取得，CurrentUser、owner过滤、public响应投影 | 延续服务端身份决定所有权、响应模型约束。已有类似能力，不重复实现。其superuser/403暴露方式不照搬，本项目他人/不存在统一404；不迁移SQLModel/前端栈。备选维持现有psycopg短事务，无新依赖成本 |
| [sysid/sse-starlette](https://github.com/sysid/sse-starlette/tree/431ad1a6b238322fc5498a253814b7459eaafe10)（本次实时API取main SHA） | [sse_starlette/sse.py](https://github.com/sysid/sse-starlette/blob/431ad1a6b238322fc5498a253814b7459eaafe10/sse_starlette/sse.py)：web锁定raw返回cache miss，随后gh contents固定ref取得源码，核对_listen_for_disconnect/_stream_response/_ping/send_timeout/client_close_handler_callable | 采纳断连/超时/进程退出边界应分开处理的思路；本轮不安装/换SSE库，库不能停止已发起的同步供应商线程，也不能代替数据库attempt校验。备选保持现有StreamingResponse，后续业务接线时补验收；不宣称有性能提升 |

**本周取舍**：岗位证据共同支持把已有AI产品链路交付完整、证明权限/并发/故障恢复；不是要求引入多Agent、RAG、队列或微服务。已有上传解析、Pydantic、匿名SSE、题库、CI，以及可选账号与历史CRUD；缺口是业务绑定记录、持久任务一致性、历史UI、双设备合成闭环和部署/异机恢复。路线优先级不变：本轮先持久任务仓库作为安全接线前置，随后账号record+revision上传/SSE/题库、发布前重验会话、历史UI/双设备；部署包继续在确认S3内。周目标按验收而非承诺截止：并发只领取一次、旧attempt不写回、重启只标中断不自动调用；后续完整链需合成HTTP/浏览器与实际数据库配合。依赖：本机Docker不可用时由真实PostgreSQL CI；真实OAuth/目标域名/资源与正式发布仍独立审批。Q003模型预算未批，评测资产/真实质量留后续，不为JD堆框架。未采纳签证不适用岗位作为投递建议，未采用模板superuser、自动模型重试或新基础服务。

### 2026-10-26 S3第四切片：持久任务占用与精确尝试写回

- 范围/原因：继续已确认S3，今天负责api/history.py、迁移002、迁移脚本、真实数据库测试及plan/journal/存储与质量手册。账号CRUD虽可用，尚无跨连接任务状态，不能安全连接多设备生成；本轮交付可独立验收的仓库层一致性，业务HTTP/页面接线保留下一步。文档修改前无差异。未碰前端、原日志/两份私人分析材料/test-results，未读.env或凭据；默认匿名链不变。
- 基线/并行：单worktree，codex/qwen-provider-migration，起始本地及实时远端d30b091d2258c8e12c805d47ae94f5418e52854d；main仍e44da22da39093f8a6e69edb33f12406a8db0fe7，上游origin原分支，部署列表0。前次[CI40178916950](https://github.com/Dkgo-0323/Interview-Prep-Assistant/actions/runs/40178916950)精确SHA completed/success，10项真实数据库含HTTP与备份恢复成功，归档上次收据而非今日成绩。本任务active，上轮聊天notLoaded且最后交付完成；可见无同项目其他active，外部/其他机器活动未知，无跨聊天消息。初次沙箱SSH/gh失败，允许读取后核验成功。
- 实现：迁移002新增preparation_tasks，record+kind主键每份最多保留analysis/questions最新两项；owner仍从已有仓库边界传入，记录行锁后核对revision并拒绝任何running，发新attempt UUID；短事务提交后再由未来协调层调用模型。同版本再次明确生成使用新attempt，旧attempt即使输入版本相同也不能结束/失败新任务。running→completed与完整快照一起提交，写入失败一起回滚；失败仅记failed，不存供应商错误/隐私。重分析原子清除旧questions及任务；重传同事务清结果/中断running；删除级联任务。原001不改，迁移脚本显式运行001–002，支持重复/旧数据升级。
- 重启边界：独立interrupt_tasks_on_startup只供旧单worker停止后、新worker接流量前显式调用，将running改interrupted、不自动重试/模型调用。普通连接/仓库重建不触发中断，其他记录互不占用。应用启动目前尚未调用，不能宣称网页重启恢复已生效；不支持并行worker/租约/任务队列。旧publish保留兼容测试，无attempt保护，后续任务HTTP必须用finish_task；完成前还须重新核验原账号会话，库层所有权不等于退出后授权仍有效。
- 本机验证：Windows/Python3.12.7，初次沙箱check_backend在socketpair超时、exit1，未运行业务；允许回环后`venv/Scripts/python.exe scripts/check_backend.py` exit0：186 passed/5既有样本缺失skip/1既有Starlette警告，8.67s。这个九文件离线集合证明匿名/账号既有HTTP不回归，不包含本次真实SQL新行为。3 Python AST解析通过。全仓diff检查碰到用户已有logs/app.log空白，未修改，改限定本轮路径检查通过。Docker Linux engine管道不存在，未运行本机数据库/dump恢复。没有前端改动，不本机重复npm/browser；未进行真实模型/OAuth/部署或购买。
- 新数据库验收范围：审阅test_history_postgres新增并发四连接只一成功、跨种类互斥、完成/重试/旧attempt、失败、显式重启、重传版本、所有权/跨记录/删除级联、重分析失效题库、JSON失败事务回滚、非法快照和001升级；既有dump/restore现在核对任务状态与attempt，恢复后显式中断。交独立PostgreSQL16 CI，实际结果待取得，不先标通过。
- 可演示/剩余：本轮可通过数据库验收展示并发与故障状态；网页无新按钮/业务功能。现有上传→匿名内存文本→SSE结构化提取/报告→题库仍未落到账号记录。下一步已授权：接record+revision业务协调、原会话撤销检查与启动中断，再历史UI/完整双设备合成链、部署包/异机备份。真实凭据/资源购买/精确费用/正式发布、Q003模型预算仍按既有interview边界。本次提交SHA/push/最终CI在当轮聊天和memory，下轮实质增量归档，避免自引用补收据提交。

### 2026-10-27 S3第五切片：账号记录上传、报告与题库后端闭环

- 目标/范围：周二不重复例行JD研究，继续已确认S3。负责记录业务路由/协调器、公共文件解析与SSE消息工具、历史精确中断和应用启动、相关离线/真实数据库验收及README/Architecture/plan/journal/技术手册。改前确认规划文档无并行差异。网页本轮无新按钮：登录/历史UI与POST SSE客户端仍待接，默认匿名页面继续工作，不宣称S3全部完成。
- 基线/并行/上轮归档：单checkout、`codex/qwen-provider-migration`，起始本地/实时远端`c06c7d51b0e6d010fd09c257a2a8da9f59dc493f`；上游origin同名分支/main仍`e44da22da39093f8a6e69edb33f12406a8db0fe7`，部署列表0。上轮完整SHA已普通推送，[CI40278176507](https://github.com/Dkgo-0323/Interview-Prep-Assistant/actions/runs/40278176507)精确SHA completed/success、四job成功，真实PostgreSQL22通过/1既有警告含实际dump/restore（3.01s）；这是10-26成绩，不是今日新测试。本任务active，上轮同项目聊天notLoaded且已交付；可见无其他同项目active，外部/其他机器活动未知，无跨聊天消息。沙箱SSH/gh网络失败，允许只读网络后核对成功。
- 实现/数据链：新增`/api/records/{uuid}`下JD/简历上传与输入清空、POST分析SSE、报告读取、题目生成/读取、任务状态；服务端账号Cookie提供owner，不接受客户端owner/结果。上传复用PDF/DOCX/TXT/10MB与临时文件清理，持久化仅解析文本，成功返回新revision；跨设备旧版本409、结果清空与任务中断同事务。文件解析与SSE格式从匿名路由提为公共工具，避免账号接口反向导入匿名路由造成循环；匿名调用仍复用原逻辑。记录选择仅URL，不加全局current_record，不自动导入匿名资料。
- 任务/权限：分析领取record+revision+attempt，短事务后调用原JD/简历/差距分析器，Pydantic完整快照校验后`finish_task`原子提交；包括重新校验已被修改的模型实例，避免model_validate(instance)默认信任绕过约束。题库从该记录持久jd/resume/gap构建，同样领取/完成attempt。每阶段检查存活/版本/任务，写回与failed前短暂持有账号锁重验原token，与退出串行；模型工作不持有账号/数据库锁。退出/过期不发布结果也不写failed，仅可信生命周期清理精确attempt为interrupted，释放另一设备可重试的占用；旧版本/删除/新attempt不能被清理误伤。断连不能终止同步供应商线程，shield后保留running至线程实际结束，再只中断本attempt。存储清理失败不重试，启动恢复兜底。
- API/启动边界：生成采用明确POST，GET读取/任务状态不生成，禁止自动重连/任务重试；未来UI用fetch读取POST SSE，不能直接用原EventSource启动账号分析。鉴权/来源/体/记录预检用HTTP错误；流开始后的busy/缺输入/旧版本/业务异常用末尾error事件及data.status（不是改变HTTP200），完整提交后才complete。常规LLMService已有供应商内部重试未改。重分析中或失败保留同输入的上次成功快照，客户端须结合任务状态标明旧结果，成功重分析才清旧题。启用账号时在接受流量前调用真实仓库启动中断；失败则启动失败，不自动迁移/调用模型。必须停旧单worker后启动新worker，不支持滚动重启/多worker。账号登录重启需重登，数据库资料可恢复；默认匿名网页仍重启丢失。
- 本机验证：Windows/Python3.12.7，`venv/Scripts/python.exe scripts/check_backend.py`十文件审阅集合，外部连接阻断、dotenv屏蔽。首次沙箱socketpair超时exit1，业务未执行；允许回环后首轮213通过/1失败/5跳过，取消用例用过短JD被已有20字符校验提前挡住，修正为仓库合成JD/简历，非放宽业务校验；随后216通过。增加坏数据/上传/存储等验收并提公共工具后最终223 passed/5既有缺文件skip/1既有Starlette警告，8.57s，exit0。新增37个用例覆盖真实已注册HTTP+解析/领域分析器、双设备读取/生成、权限/Origin/严格输入、busy与旧版本、退出/过期/重传/删除交错、取消忙槽、失败显式重试、坏领域实例/存储安全错误、启动成功与失败关闭。身份/模型/存储边界为替身，不能证明SQL或真实模型质量。
- 真实数据库验收安排：独立PostgreSQL16门禁新增六项：四组合实际解析→分析SSE→报告→题库、同账号双HTTP客户端/独立仓库连接恢复、重分析清题库，以及模型返回时退出/重传/删除拒绝发布；精确中断只改原attempt；真实应用启动中断数据库running后才接请求。身份签发/模型仍合成，无真实OAuth或Qwen。沿用原实际pg_dump/pg_restore。Docker引擎管道不存在，未运行本机数据库/恢复；本次真实SQL结果待远端取得，不预标通过。前端无改动，不本机重复npm/浏览器；远端完整前端门禁照常执行。
- 交付/风险/下一步：当前可通过HTTP验收演示账号资料持久链路，页面仍匿名。下一步已授权：登录/历史列表/命名切换删除、账号POST SSE与题库UI、完整双设备合成浏览器验收，再单机部署包/异机备份恢复。真实OAuth凭据与目标HTTPS/GitHub可达性、Q003模型预算、资源购买/精确价格/正式发布仍保留既有决策边界；无需重复阶段interview。未读.env或私人资料正文，原日志/两份私人分析材料/test-results内容哈希不变。本次提交自身完整SHA、普通推送与最终CI先记本聊天/memory，下轮实质增量归档。

### 2026-10-28 S3第六切片：账号历史网页与明确生成流程

- 主任务/范围：周三沿已确认S3完成“我的记录”网页，非新阶段、不重复JD研究。负责frontend/lib/history-api.ts、components/history-workspace.tsx、app/history/page.tsx、导航、离线契约与生产浏览器脚本、package脚本及README/Architecture/plan/journal/相关三技术手册。修改前规划文件无差异；不读.env/真实简历正文，不改原日志/两份私人材料/test-results。本次无后端实现变化，无新依赖/资源/模型调用。
- 基线与并行：单worktree、codex/qwen-provider-migration、上游origin同名分支；本地/实时远端起始9cbf3df3a1eaaa5bb3ddaa41a469ea312d529ad4，main仍e44da22da39093f8a6e69edb33f12406a8db0fe7。上轮已普通推送，[CI40460075448](https://github.com/Dkgo-0323/Interview-Prep-Assistant/actions/runs/40460075448)精确SHA completed/success四job，真实PG28通过含实际dump/restore（5.60s），本轮只读归档，不算今日新成绩。部署列表0。初次沙箱SSH/gh网络失败，允许只读网络后恢复。可见本任务active、前次同项目idle且最后turn completed；无可见其他同项目active，外部/其他机器并行未知，无跨聊天消息。
- 用户可见成果：导航新增“我的记录”；未登录可跳转GitHub并重新检查身份，默认未配置显示503、首页匿名仍可用。账号内最多20份、命名创建/列表/改名/选择/二次确认删除，满额不淘汰。记录内依次上传JD/简历、明确分析、生成10–50题并展开参考回答；刷新恢复保存报告/题库，任务状态与上次成功快照分开标注。现有OAuth回调固定回首页，再进入记录页；不自动导入匿名资料、不存浏览器token或私密localStorage。
- 请求/一致性：独立账号客户端携带HttpOnly Cookie与no-store，不初始化匿名会话，不提交owner/结果。上传绑定record+revision并应用服务器新版本，改名不改版本；分析是POST fetch流式读取（非EventSource），解码UTF8/跨包CRLF/心跳，以complete或error终止；HTTP200流内错误保留data.status，提前EOF/坏JSON报错，不自动重连或重发生成。刷新/选择仅GET；已有后端负责短事务claim→原分析器→快照/任务原子完成、原会话重验、退出/重传/删除防旧写回。页面key包含account+record，卸载取消流、忽略旧响应。401清账号视图，409/不确定请求失败撤下旧记录展示、要求明确刷新；不把前端取消说成停止供应商线程。当前选择仅URL记录id，服务端仍验证所有权。
- 本机验证：Windows Node22.15.0/npm10.9.2/Next16.2.9，最终允许进程通信环境`npm.cmd run check` exit0：lint、next typegen/tsc、18项离线契约（原12+新6）、生产build全部通过，新增/history静态入口；未改后端，不在本机重复后端离线或PG，远端CI照常覆盖。新增契约包括不初始化匿名/凭据/no-store、严格参数、204、401/404/409/503无重试，中文逐字节SSE/CRLF跨包、终端错误、坏JSON/提前断流、取消信号。初次check因effect直接调用包含状态更新的refresh被React lint拒绝；拆成异步读取回调后通过，无关闭规则。一次误从根目录运行npm报无package.json，改回frontend后正常。
- 浏览器真实页面、合成API：`NODE_PATH=<bundled runtime node_modules> node scripts/check_history_ui.cjs http://127.0.0.1:3168 <本轮独立产物目录>/history-ui`，本机生产Next+headless Edge，八组全部通过：完整命名/上传/明确分析/题库回答；独立浏览器同账号恢复/刷新不生成；改名与跨设备旧revision409；HTTP200内busy/失败及中断上次结果；晚到GET后切换不串；删除取消/确认及20份；另一账号404/过期清屏/本设备退出；503恢复与390px/桌面无溢出。完整正常链analysis1/questions1，后续两次明确错误尝试合计analysis3/questions1；匿名请求0/pageErrors空。API全部拦截合成，共享合成记录，不执行真实OAuth/Cookie鉴权/解析器/SQL/模型，不冒充浏览器直连完整后端。另`check_questions_ui.cjs`原十场景全部通过，unexpected0/pageErrors空。两张记录桌面/手机截图已目视检查，合成总分0来自原fixture，不是UI计算失败。产物仅放C:/Users/dukai/.codex/visualizations/2026/10/28/01a18116-c155-77b3-be90-bd330dd05be7，不入Git。
- 失败与修复：首轮浏览器在旧GET挂起时router.replace切换未及时完成；改为安装版本Next官方本地指南支持的native history.replaceState与useSearchParams同步，不必为同页选择等待服务端导航。重测切换通过后发现401清屏增加epoch导致finally不清loading，补401同步结束loading，重建后八组最终通过。初次Playwright模块不可解析，使用已配置bundled NODE_PATH，无安装新包。失败未计成功；未绕过权限或弱化断言。
- 边界/下一步：S3网页功能已接入且拦截API浏览器验收通过，但浏览器→真实FastAPI→PostgreSQL双设备组合证据仍待补，真实GitHub/数据库回调、实际HTTPSCookie/Origin/SSE代理、单机部署包/异机备份恢复及公网发布仍未完成。可在现有授权内继续组合验收与部署包；真实用量Q003、凭据/购买/精确费用/正式发布按原interview边界，不重复询问常规UI选择。当前提交自身SHA/push/最终CI留本聊天与memory，下轮实质增量归档；不为补自身收据另做提交。

### 2026-10-29 S3第七切片：可校验备份包与实际恢复门禁

- 主任务/范围：周四不重复例行研究，继续已确认S3备份恢复工程；负责scripts/backup_history.py、离线allowlist/备份测试、真实PG恢复测试及plan/journal/存储和备份手册。未增加业务页面。原计划优先浏览器直连数据库组合；本机Docker引擎此前不可用，本轮先交付同阶段不依赖该环境的备份工具及远端真实恢复证据，组合浏览器验收仍未完成。
- 基线/并行/上轮归档：单worktree、codex/qwen-provider-migration，本地及实时origin同名分支99557143755f5687ca34748f00e18d2b7d355e23；main仍e44da22da39093f8a6e69edb33f12406a8db0fe7。上轮CI40642952113 completed/success、四job成功，部署列表0；这是旧收据，非今日新测试。可见仅本聊天同项目active，前次notLoaded，外部并行未知，无跨聊天消息。根和上层AGENTS不存在，前端AGENTS已读；本轮未改前端。文档修改前无差异，原日志/两份私人材料/test-results未触碰，未读.env/隐私正文。
- 实现/防错：显式create/verify工具不导入应用或dotenv；DSN仅传子进程环境，不进入命令参数、收据或输出错误。私密同盘临时目录内pg_dump custom→pg_restore list→分块SHA256/字节数/UTC收据；拒绝覆盖现有目的目录，READY最后写入。导出/检查失败不发布备份，移动/崩溃可留无READY目录，CLI拒绝验证为完成；不自动删除用户备份/恢复DB/启动定时器。校验防意外损坏，不防同时篡改收据和归档、不等于加密或完整恢复。手册提供异机复制后再verify、隔离空库事务恢复、角色/权限与单worker启动中断要求；不选择未批准资源/费用/保留周期。
- 验证：本机Windows/Python3.12.7，首次沙箱socketpair超时exit1、业务未执行；允许本机回环后venv/Scripts/python.exe scripts/check_backend.py exit0，十一文件229 passed/5既有缺fixture skips/1既有Starlette警告，32.28s。新增六例覆盖凭据边界/非覆盖、dump/list失败清理、截断/等长损坏/坏收据拒绝；工具为替身，非真实备份证明。真实PG16既有恢复测试改为调用新导出工具及verify，再实际drop合成schema/pg_restore/读回账号文本报告task及启动中断；远端结果尚待取得，不预标通过。无前端改动，本机不重复npm或浏览器；远端仍跑完整门禁。未调用真实模型/OAuth、未部署/购买。
- 可演示/剩余：现在可对已配置数据库显式生成完整可校验包，另处复制后检查，再在隔离库演练。尚无线上备份服务、异机实际传输/恢复/定时/磁盘告警/恢复时长承诺；浏览器→FastAPI→PG组合、单机代理启动迁移健康检查/回滚包继续已授权推进。真实凭据/资源/正式发布/Q003保留既有interview边界。当前提交自身完整SHA/普通push/最终CI记聊天与memory，下轮归档避免自引用提交。
