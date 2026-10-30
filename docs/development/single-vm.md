# 单机运行与回滚包（S3，尚未部署）

仓库提供 [systemd API](../../deploy/single-vm/ipa-api.service)、
[Next 服务](../../deploy/single-vm/ipa-web.service) 与
[同源 HTTPS 代理](../../deploy/single-vm/nginx.conf)。这是供审阅/演练的 Linux
配置，不是安装器，不会申请资源、迁移数据库或发布。尚缺目标主机实际验收。

## 发布目录与准备

目标布局：`/srv/interview-prep/releases/<完整SHA>` 保存独立版本及各自的
`venv`、`frontend/node_modules`、`frontend/.next`；`current` 是指向当前版本的
符号链接。不要在运行中的目录 git pull、覆盖构建或复用旧虚拟环境。
专用非 root 用户/组为 `ipa`；系统级 Node22 路径为 `/usr/bin/node`。
部署者应先核实目标 Linux/systemd/nginx/PostgreSQL16/Node22/Python3.12
版本与可用磁盘，不适用时先调整并验收模板，不直接套用。

1. 在新 release 安装后端依赖 `requirements.txt` 和 `requirements-history.txt`，
   前端执行 `npm ci`；以 `NEXT_PUBLIC_API_URL='' npm run check` 构建同源请求。
   该变量是构建期值，不能在启动时修正旧 build；不能把 localhost:8000 编入公网包。
2. `/etc/interview-prep/api.env` 仅 root 可读写（0600，由 systemd 读取），
   配置项见 [账号手册](github-auth.md)；callback 和 frontend origin 必须是同一
   实际 HTTPS 域名。匿名 Cookie 强制 secure。不要在 release 留 `.env`，
   服务设置 `PYTHON_DOTENV_DISABLED=1` 避免意外读取历史配置。
   无真实用量授权不配置真实模型密钥；当前没有合成运行开关，不能把这些模板
   当作可公开生成的合成演示。真实凭据接入仍需原批准边界。
3. PostgreSQL只监听本机，防火墙仅开放获批HTTPS/管理入口，8000/3000/5432
   不开放公网。数据库角色与备份权限见 [存储](history-storage.md) 和
   [恢复](history-backup.md)。不把密码放 shell 参数或文档。
4. 配置实际证书/域名，复制 unit 至 systemd、nginx片段至 http 上下文。
   `nginx -t` 和 `systemd-analyze verify` 必须通过才应用。本包没有80端口
   或证书签发配置；域名/备案/证书和资源仍是发布依赖。

## 明确的停机升级顺序

先通过维护入口阻断新流量（由部署者准备并验证），停止 web 和 API：
`systemctl stop ipa-web ipa-api`，确认两者 inactive 且旧8000进程退出。
禁止并行启动第二worker、滚动替换或在启动步骤自动迁移。
API等待最多300秒后由systemd终止进程组；这不证明已发出的供应商调用停止或免费。

按恢复手册导出旧库、verify并复制到受保护异机位置，再检查待应用迁移的兼容性。
在新 release 中，由受控进程环境注入 `HISTORY_DATABASE_URL`，显式运行
`venv/bin/python scripts/migrate_history.py`，禁止把 env 文件当 shell 脚本 source。
迁移失败保持维护状态，不启动旧代码假装成功。切换current后daemon-reload、
启动API，再做下列检查，最后启动web、检查页面并恢复入口。
当前单worker启动会把残留running任务标interrupted，不自动重新生成；
账号Cookie会失效，需要重新登录，数据库记录保留。

## 健康与真实验收

`curl --fail http://127.0.0.1:8000/api/health` 应返回 `{"status":"ok"}`；
经实际HTTPS域名访问同一路径，验证代理与证书；GET `/history` 验证前端。
health仅证明应用响应，不是数据库持续可用、OAuth、模型或完整链路就绪证明。
账号功能启用时启动必须成功连接库并中断旧任务；还须用独立设备会话实测
创建记录→上传合成JD/简历→明确分析→题库→另一设备读取→刷新不生成、
旧版本409、删除后不可恢复；合成模型需独立测试注入，不擅自使用真实密钥。

发布前另测实际GitHub回调、HTTPS HttpOnly/Secure Cookie、精确Origin拒绝、
长SSE分阶段及时到达、断连/超时/重启后的interrupted，以及异机实际恢复。
代理关闭响应缓冲/缓存/自动上游重试；300秒是相邻读取间隔超时而非整个任务
预算，不能保证长线程完成。11MiB请求上限为10MiB文件留multipart开销，
业务仍检查文件大小。关闭访问日志、Uvicorn access log和本虚拟主机错误日志，
避免OAuth code/state进入请求URI日志；代价是代理诊断证据减少，发布前需落实
不含查询字符串/正文/凭据的监控与告警。不得临时打开完整请求日志排障。

## 回滚与恢复

保持维护→停止两服务并确认退出→核对数据库兼容性→current指向已验收旧release→
启动API/健康检查→启动web/HTTPS与记录只读检查→恢复流量。
不能仅凭代码回滚就逆转schema或恢复丢失资料；不兼容迁移需要隔离恢复验证、
获准的数据恢复方案与停机窗口，禁止自动down migration或覆盖现库。
备份定时/异机目的地/保留周期/磁盘监控与实际恢复记录仍待落实，不承诺RPO/RTO。
默认 `Restart=no`，崩溃后需检查并显式重启，避免失败循环掩盖故障；目标主机
服务/磁盘/备份告警仍为发布前置。

参考（2026-10-30北京时间）：[nginx proxy官方文档](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)
关于buffering/read timeout/retry；[systemd.service官方文档](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html)
关于Type=exec及进程启动不等于业务就绪。CI只验证模板语法，不证明主机部署成功。
