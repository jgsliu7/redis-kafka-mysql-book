# 读者053 · 最小权
身份：DBA(权限方向)，11年，爱好：养多肉
主读：第 6 章

## 五个问题

1. 【6.3|技术事实】正文和图 6-4 底注都说 MySQL「启动时把授权表整表载入内存，按'账号加库表'组织成位图化的权限结构」。按我做权限审计的了解，8.0 里常驻内存的是全局权限（mysql.user），表级/列级权限是首次使用时按需读入并缓存、靠 GRANT/FLUSH PRIVILEGES 触发重载——「整表载入」的说法疑似 5.x 时代口径，位图化这个内部结构也没给来源，请核实。

2. 【6.3|逻辑论证】表 6-1 的「最细粒度」写的是「键模式加命令」，但正文同小节明确说「6.2 起通道权限独立出来」，且引用的 default 规则 `~* &* +@all` 里就有通道模式 `&*`。书的权限矩阵行和它自己引用的规则互相矛盾——对我这种拿对比表当工作底稿的读者，矩阵行漏一个维度就会照抄出错。

3. 【6.3|技术事实】Kafka 资源类型清单列了 Topic、Group、Cluster、TransactionalId、DelegationToken，漏了 USER——配额管理（AlterUserQuotas/DescribeUserQuotas）和用户 SCRAM 凭证变更（AlterUserScramCredentials）都挂在 USER 资源上；操作集也少列了 AlterConfigs/DescribeConfigs/IdempotentWrite 等。给几十个服务建 ACL 矩阵时这份清单是不全的。

4. 【6.3|读不懂】「保护模式开启且 default 用户带 nopass 时，会拒绝非本地连接」——「本地」的判定标准是什么？只认 loopback（127.0.0.1/::1/Unix socket），还是同宿主机的非环回地址（Docker 网桥、容器 IP）也算本地？容器化部署里这直接决定 default 用户要不要显式处理，书里没说清我落不了地。

5. 【6.1|逻辑论证】6.1 给认证开的职责清单是「凭证的存储、传输、校验和防暴力破解」四件事，但 6.2 三家认证小节没有一处回收「防暴力破解」：Redis 有没有失败锁定机制（据我所知没有）、Kafka 对 SASL/PLAIN 猜密码有没有限速（也没有）、MySQL 的 connection_control 又拖到 6.6 才露面。开头列了清单、正文不收口，读者会以为三家都有解。

## 五个建议

1. 【6.3|版本时效】权限语义四分类（DML/DDL/管理/复制）是 5.x 的旧地图：8.0 已转向动态权限体系（CONNECTION_ADMIN、BINLOG_ADMIN、REPLICATION_APPLIER 等），SUPER 自 8.0.34 起弃用，且 SYSTEM_USER 把账号分成「系统/普通用户」两层、改变了「谁能改谁的账号」。做 8.0 权限收敛的 DBA 拿书对不上实机，建议至少补一段动态权限与 SYSTEM_USER。

2. 【6.3|深度广度】建议加一段 WITH GRANT OPTION：转授出去的权限在撤销时不级联（回收 A 不影响 A 转授给 B 的权限），这是权限审查里最常见的失控路径，也是「最小权限」最难守住的一角。正好对照 Redis ACL 和 Kafka ACL 都没有转授语义，引出「转授权要不要进内核」的取舍——非常贴本书主题。

3. 【6.3|案例示例】授权维度只有概念没有可复制的最小写法。建议给一个「同一个多租户需求在三家的最小授权」并排示例：Redis 一行 ACL SETUSER（键模式+命令类别）、MySQL 一句 GRANT SELECT(phone) ON db.users、Kafka 三条 prefixed ACL。三段并排，最小权限原则从口号变成能直接抄的作业。

4. 【6.4|深度广度】社区版 TDE 的安全边界建议点破：keyring_file 的密钥就在本机明文文件里，防不了能登录主机或拿到磁盘镜像的攻击者，官方文档自己都定位为测试用途。现在「社区版可用 keyring_file」的写法容易让读者误以为开了就满足加密合规，加一句「生产合规=企业版密钥管理或磁盘加密」能救不少人。

5. 【6.5|案例示例】MySQL 社区审计除 General Log 外还有更现实的选项：Percona Server 的 audit_log 插件（开源、输出格式兼容企业版）、MariaDB 的 server_audit，以及 binlog+init_connect 的低成本组合，建议至少点名；Kafka 外挂审计也建议给一个最小方案（拦截器写审计主题，并注明审计主题自身的 ACL 与保留期约束），现在只说「外挂补全」太抽象。
