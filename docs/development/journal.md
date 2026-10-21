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
