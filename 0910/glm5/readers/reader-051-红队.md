# 读者051 · 红队
身份：渗透测试工程师，9年，爱好：打 CTF
主读：第 6 章

## 五个问题
1. 【6.3 | 版本时效】书里说「在 Redis 7.0 的实现中……是否绑定全部网卡不是这一判断的条件」。我拉源码核了：7.0 的 networking.c（clientAcceptHandler）确实只判 protected_mode + default 用户 nopass + 非本地，但 6.2 及更早版本的条件里还有 `server.bindaddr_count == 0`——只要显式 bind 过任意地址，保护就整体失效。书只钉死 7.0、不提 6.x 差异，而线上还跑着大量 6.x；这些读者显式配了 `bind 0.0.0.0` 就会按书的说法误以为自己仍受保护。
2. 【6.6 | 技术事实】表 6-1「推荐生产认证」的 Redis 列写「ACL 用户与必要的 TLS 证书校验」，并排放置容易让人以为证书能和 ACL 用户关联。事实上 Redis 的 `tls-auth-clients` 只是全局开关，客户端证书校验通过后不映射到任何 ACL 用户（身份仍靠密码或 default）；对比 MySQL 有账号级 REQUIRE X509/SUBJECT、Kafka 能用 ssl.principal.mapping.rules 把证书 DN 映射成 Principal 参与 ACL——三家在「证书即身份」上差异巨大，这一行并排写法把这层差异抹掉了。
3. 【6.2 | 读不懂】KRaft 段这句：「这与 Controller 之间的共识连接不是同一条路径。后者在 3.5.1、3.6.0 曾出现用 SCRAM 启动集群失败的问题」。我读了三遍仍无法还原「后者」具体指哪条连接，也不知道失败根因是什么（SCRAM 凭证本身存在元数据日志里、启动期先有鸡还是先有蛋？）。没有 JIRA 编号没有根因，读者无法判断自己用的版本是否踩同一个坑。
4. 【6.7 | 逻辑论证】「默认值错配的洞，比权限配粗的洞出得快，也更难被发现」——后半句我不认同。公网 default nopass 恰恰是最容易被暴露面测绘（Shodan/FOFA）发现的一类，攻击者和防守方的扫描当天都能找到（本章开头自己就说「当天就会被扫到」）；真正难被发现的是内网可横向到达的 default nopass（无外部暴露特征、又没有审计）。这句断言需要收窄限定条件，否则与开篇案例自相矛盾。
5. 【6.2 | 术语使用】「`auth_socket` 让本机进程免密登录」不准确：auth_socket 依赖 Unix socket 的 SO_PEERCRED，把操作系统用户名与 MySQL 用户名匹配，两者一致才免密成功（这正是 `sudo mysql` 能直进的原因——OS 的 root 对应 root@localhost）。「本机进程免密」的说法会被人理解成任意本机进程都能无密码连入，我在提权评估报告里见过因这个误解引发的风险判定争议。

## 五个建议
1. 【6.2 | 案例示例】「历史上未授权 Redis 写 SSH 公钥、写定时任务导致 RCE 的案例非常多见」这句应补上链条原语和前提：该链依赖 `CONFIG SET dir/dbfilename` 任意文件写、且进程用户对 `~/.ssh` 或 crontab 有写权限，另有 rogue master + `MODULE LOAD` 加载 .so 的路线。尤其值得点出 Redis 7.0 已默认封锁这两条路（enable-protected-configs 让 dir/dbfilename 不可改、enable-module-command 默认禁 MODULE，我在 7.0 的 redis.conf 里核对过）——只说「案例非常多见」而不给前提和官方对策，读者没法映射到自己的防御检查单。
2. 【6.2 | 案例示例】MySQL 可插拔认证的动机处建议补 CVE-2012-2122（认证令牌 memcmp 比较缺陷，错密码重试约千次内即有约 1/256 概率通过，MySQL 与 MariaDB 都中招）。这是「自研认证协议」最经典的历史教训，一个案例就能让读者掂出「认证逻辑与协议解耦、做成可插拔」的分量，也正好呼应第 5 章可插拔存储引擎的类比。
3. 【6.5 | 深度广度】社区版 MySQL 审计一节别只给「企业版插件 / General Log 凑合」两个极端，提一句甲方真实在用的替代：McAfee mysql-audit、Percona/MariaDB 的 audit 插件、或 performance_schema 的 digest 表做近似追溯。Redis 侧同样可加一句 MONITOR 的双刃性（全量命令参数明文、性能重挫——既是调试后门也是攻击者拿到连接后最爱敲的命令），这节会立刻更接地气。
4. 【6.6 | 深度广度】建议横向对比表 6-1 增加「典型失陷路径」一行：Redis default nopass 暴露公网=当天被测绘接管；Kafka SASL/PLAIN 不套 TLS=链路嗅探直接见密码；MySQL 应用账号授 FILE+SQL 注入=任意文件读。安全评审的人扫一眼这一行就知道先查什么，四维对比表也能从「配置清单」升级成「威胁对照表」，与 6.7 启示一形成闭环。
5. 【6.2 | 版本时效】mysql_native_password 在 MySQL 8.4 已默认禁用、9.0 彻底移除，书里「老客户端常因不支持而需要显式回退」是个正在关闭的窗口。建议正文或表格标注版本边界（8.0 可用 / 8.4 默认禁用 / 9.0 移除），避免读者在新版本上照书回退失败；顺手可用一句话处理我问题 1 里的 protected-mode 6.x/7.0 条件差异。
