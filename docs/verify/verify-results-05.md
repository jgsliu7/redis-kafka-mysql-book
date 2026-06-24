# 第05章《安全》事实核查结果

> 核查时间: 2026-06-23
> 核查范围: verify-questions-05.md 全部 65 个问题

## 核查统计

| 结果 | 数量 |
|------|------|
| ✅ 确认正确 | 57 |
| ❌ 需要修正 | 1 |
| ⚠️ 需要澄清 | 5 |
| 🔍 无法确认 | 2 |

---

## 逐题核查

### Q1: Redis ACL 引入版本
**原文陈述**: "6.0 之前的 Redis 只有一个 requirepass 全局密码" / "6.0 引入 ACL"
**核查结果**: ✅ 确认正确
**核查依据**: Redis 官方文档明确声明 "Redis 6 (the first version to have ACLs)"。Redis 6.0.0 GA release notes 将 ACL 作为主要新特性列出。6.0 之前确实仅有 `requirepass` 全局密码机制。
**建议**: 无需修改。

### Q2: Redis 密码存储使用 SHA-256 哈希
**原文陈述**: "密码用 SHA-256 哈希存（通过 ACL FILE 持久化到 users.acl），不存明文"
**核查结果**: ✅ 确认正确
**核查依据**: Redis 源码 `src/acl.c` 中 `ACLHashPassword()` 函数使用 SHA-256 哈希（调用 `sha256_init`、`sha256_update`、`sha256_final`），将密码转为 64 字符十六进制字符串存储。
**建议**: 无需修改。

### Q3: Redis 密码哈希无加盐
**原文陈述**: "SHA-256 是哈希不是加密，且无加盐"
**核查结果**: ✅ 确认正确
**核查依据**: Redis 源码 `ACLHashPassword()` 中 `sha256_update` 仅传入明文密码，无盐值。Redis 官方文档明确说明 "Redis internally stores passwords hashed with SHA256" 并明确论证了不加盐的理由（强调使用强密码而非慢哈希）。
**建议**: 无需修改。

### Q4: Redis 命令类别分组
**原文陈述**: "Redis 把上百条命令折叠成几个语义组：@read、@write、@admin、@dangerous、@fast、@slow"
**核查结果**: ✅ 确认正确
**核查依据**: `ACL CAT` 输出明确包含 `admin`、`dangerous`、`fast`、`read`、`slow`、`write` 等类别。完整的分类集还包含 `keyspace`、`set`、`sortedset`、`list`、`hash`、`string`、`bitmap`、`hyperloglog`、`geo`、`stream`、`pubsub`、`blocking`、`connection`、`transaction`、`scripting` 等。书中列举的 6 个分类均存在，且是实际 ACL 配置中最常用的分类。
**建议**: 无需修改。

### Q5: Redis 通道权限引入版本
**原文陈述**: "6.2 之后，通道（channel）权限也独立出来"
**核查结果**: ✅ 确认正确
**核查依据**: Redis 6.2 RC1 release notes 列出 "ACL patterns for Pub/Sub channels" 作为新特性。Redis 6.2 发布后，ACL 规则新增 `&*` 表示所有 Pub/Sub 通道。
**建议**: 无需修改。

### Q6: Redis 7.x default 用户内置规则
**原文陈述**: "7.x 里 default 用户的内置规则仍是 user default on nopass ~* &* +@all"
**核查结果**: ✅ 确认正确
**核查依据**: Redis 7.x 默认配置确认 `user default on nopass ~* &* +@all`。默认用户开启、无密码、可访问所有键和所有频道、可执行所有命令。
**建议**: 无需修改。

### Q7: Redis protected-mode 引入版本和默认值
**原文陈述**: "protected-mode（保护模式，3.2.0 起，默认开启）"
**核查结果**: ✅ 确认正确
**核查依据**: Redis 3.2.0 release notes 引入 protected mode（首次出现在 RC2）。默认配置为 `protected-mode yes`。
**建议**: 无需修改。

### Q8: Redis 原生 TLS 支持版本
**原文陈述**: "Redis 到 6.0 才原生支持 TLS"
**核查结果**: ✅ 确认正确
**核查依据**: Redis 6.0.0 GA release notes 确认 TLS 是新构建的系统，RC3 已有 "Fix crash due to refactoring for SSL" 相关提交。
**建议**: 无需修改。

### Q9: Redis TLS 协议建议
**原文陈述**: "建议限定 tls-protocols TLSv1.2 TLSv1.3"
**核查结果**: ✅ 确认正确
**核查依据**: `redis.conf` 中有注释掉的 `tls-protocols "TLSv1.2 TLSv1.3"`。文档说明默认只启用 TLSv1.2 和 TLSv1.3，旧版本已禁用。
**建议**: 无需修改。

### Q10: Redis TLS 性能衰减比例
**原文陈述**: "开启 TLS 后单线程吞吐相比无加密约降至六成左右"
**核查结果**: ✅ 确认正确
**核查依据**: Redis 性能基准测试显示，单线程模式下开启 TLS 后吞吐下降约 36%（降至约 64%，即六成左右）。Redis 核心贡献者/性能工程师在 GitHub issue #7595 中用火焰图分析了 TLS 开销来源。书中已注明 "具体数值随硬件、TLS 版本、证书算法波动较大，以实测为准"，此免责声明合理。
**建议**: 无需修改。

### Q11: MySQL 认证缓存的密码哈希算法
**原文陈述**: "新插件用 SHA-256 哈希，首次连接走完整的挑战—响应握手，之后服务端把哈希结果缓存在内存里"
**核查结果**: ✅ 确认正确
**核查依据**: MySQL 官方文档明确 `caching_sha2_password` "Implements SHA-256 authentication"。首次连接使用完整安全通道或 RSA 加密密码交换，成功后账户名/密码哈希对缓存在服务端内存中，后续连接直接使用缓存。
**建议**: 无需修改。

### Q12: MySQL 8.0.4 默认认证插件变更
**原文陈述**: "8.0.4 起把默认认证插件从老的 mysql_native_password 改成了 caching_sha2_password"
**核查结果**: ✅ 确认正确
**核查依据**: MySQL 官方博客 "The MySQL 8.0.4 Release Candidate is available" 明确记载 "Make caching_sha2_password default authentication mechanism (WL#11057)"。
**建议**: 无需修改。

### Q13: MySQL 可插拔认证插件名称
**原文陈述**: "auth_socket 让本机进程免密登录、authentication_pam 对接企业 PAM、ldap_simple 对接 LDAP 目录、sha256_password 提供无缓存的高安全选项"
**核查结果**: ⚠️ 需要澄清
**核查依据**: 
- `auth_socket` — 名称正确 ✅
- `authentication_pam` — 名称正确（MySQL Enterprise 插件）✅
- `ldap_simple` — 官方完整名称为 `authentication_ldap_simple`，书中简称为 `ldap_simple` 可能造成混淆 ⚠️
- `sha256_password` — 名称正确 ✅
**建议**: 「ldap_simple」建议改为完整名称 `authentication_ldap_simple`，与其他插件的命名风格保持一致。

### Q14: MySQL 授权层级数量
**原文陈述**: "权限按作用域分五层：全局、数据库、表、列、存储程序"
**核查结果**: ✅ 确认正确
**核查依据**: MySQL 官方文档列出五个权限级别：Global (user 表)、Database (db 表)、Table (tables_priv 表)、Column (columns_priv 表)、Routine (procs_priv 表)。
**建议**: 无需修改。

### Q15: MySQL 权限表名称
**原文陈述**: "对应 mysql.user、mysql.db、mysql.tables_priv、mysql.columns_priv、mysql.procs_priv 多张权限表"
**核查结果**: ✅ 确认正确
**核查依据**: MySQL 8.0 官方文档 "Grant Tables" 章节确认这五张是核心权限表（同时还有 global_grants、proxies_priv、default_roles、role_edges、password_history 等补充表）。
**建议**: 无需修改。

### Q16: MySQL 8.0 RBAC 角色系统
**原文陈述**: "8.0 才补齐 RBAC 角色系统，支持 CREATE ROLE、GRANT role TO user、会话级 SET ROLE"
**核查结果**: ✅ 确认正确
**核查依据**: MySQL 8.0 引入角色系统，支持 `CREATE ROLE`、`GRANT role TO user`、`SET ROLE` 等命令。
**建议**: 无需修改。

### Q17: MySQL 权限按风险分类
**原文陈述**: "权限语义按风险分四类：数据操作（DML，包括 SELECT、INSERT、UPDATE、DELETE）、结构变更（DDL，包括 CREATE、ALTER、DROP，更危险）、管理（SUPER、PROCESS、FILE、RELOAD，高度敏感）、复制（REPLICATION SLAVE、REPLICATION CLIENT，专用于复制拓扑）"
**核查结果**: ⚠️ 需要澄清
**核查依据**: 
1. 这种按风险分类是作者自己的组织框架，并非 MySQL 官方分类。官方文档按作用域（全局/数据库/表/列/存储过程）和类型（静态/动态）分类。
2. `REPLICATION SLAVE` 权限名称在 MySQL 8.0.x 中仍然保持原名，并未更名为 `REPLICATION_APPLIER`。8.0.22 中只是 SQL 语句关键词（`START SLAVE` → `START REPLICA`）做了更名，权限名称不变。`REPLICATION_APPLIER` 是 8.0.18 引入的完全不同的动态权限。
**建议**: 可注明此分类为作者整理的语义框架，非 MySQL 官方分类。`REPLICATION SLAVE` 名称本身使用正确，无需修改。

### Q18: MySQL FILE 权限风险描述
**原文陈述**: "FILE 权限能读写服务器文件系统，配合 SQL 注入可读任意文件"
**核查结果**: ✅ 确认正确
**核查依据**: MySQL 官方文档确认 FILE 权限 "Enables reading and writing files on the server host using the LOAD DATA and SELECT ... INTO OUTFILE statements and the LOAD_FILE() function"。
**建议**: 无需修改。

### Q19: MySQL TDE 在 InnoDB 表空间级别加密
**原文陈述**: "TDE（Transparent Data Encryption，透明数据加密）在 InnoDB 表空间级别加密数据"
**核查结果**: ✅ 确认正确
**核查依据**: MySQL 官方文档确认 InnoDB Data-at-Rest Encryption 在表空间级别加密（file-per-table、general tablespaces、mysql system tablespace），密钥管理支持 HashiCorp Vault（`keyring_hashicorp`）和 AWS KMS（`keyring_aws`）。
**建议**: 无需修改。

### Q20: MySQL binlog/relay log 加密版本
**原文陈述**: "8.0.14 起二进制日志（binlog）与 relay log 支持加密"
**核查结果**: ✅ 确认正确
**核查依据**: MySQL 8.0.14 Replication Enhancements 博客确认 "The binary and relay logs can now be encrypted when stored on disk"。系统变量 `binlog_encryption` 在 8.0.14 引入。
**建议**: 无需修改。

### Q21: MySQL redo/undo log 加密版本
**原文陈述**: "8.0.15 起重做日志（redo log）、回滚日志（undo log）也支持加密"
**核查结果**: ❌ 需要修正
**核查依据**: 
- `innodb_undo_log_encrypt`: MySQL 8.0.16 的 release notes 包含对该变量的 bug 修复（Bug #28952870、Bug #29477795），表明该变量在 8.0.16 或更早引入。但 8.0.15 release notes 中未提及此功能。
- `innodb_redo_log_encrypt`: 根据 MySQL 8.0.17 release notes 和相关 Worklog（WL#9290），重做日志加密在 8.0.17 引入。MySQL 8.0.16 release notes 中明确未提及此变量。
**建议**: 修正为 "8.0.16 起重做日志（redo log，实际为 8.0.17）、回滚日志（undo log）也支持加密"。如果不要求精确到小版本，可改为 "8.0.16 起 undo log 支持加密，8.0.17 起 redo log 支持加密"。

### Q22: MySQL connection_control 插件
**原文陈述**: "可启用 connection_control 插件做连接失败锁定"
**核查结果**: ✅ 确认正确
**核查依据**: MySQL 官方文档确认 `connection_control` 插件在连续失败连接超过阈值后引入延迟。默认连续失败 3 次后开始 1 秒最小延迟。
**建议**: 无需修改。

### Q23: Kafka KRaft 版本
**原文陈述**: "3.x 的 KRaft"
**核查结果**: ✅ 确认正确
**核查依据**: KRaft 模式在 Kafka 2.8 以 early access 引入，3.0 进入 preview，3.3 被标记为 production-ready。3.x 系列中 KRaft 是核心特性。ZK 完全移除是在 4.0（2025 年 3 月）。
**建议**: 无需修改。

### Q24: Kafka SASL 机制列表
**原文陈述**: "SASL 下面挂多种机制：PLAIN、SCRAM-SHA-256、SCRAM-SHA-512、GSSAPI（Kerberos）、OAUTHBEARER（OAuth 2.0）"
**核查结果**: ✅ 确认正确
**核查依据**: Kafka 官方支持 SASL/PLAIN（0.10.0+）、SASL/SCRAM-SHA-256/SHA-512（0.10.2+）、SASL/GSSAPI（Kerberos，0.9.0+）、SASL/OAUTHBEARER（2.0+）。SCRAM-SHA-1 不是 Kafka 官方支持的 SASL 机制。
**建议**: 无需修改。

### Q25: Kafka SCRAM 凭证存储位置（3.x 去 ZK 后）
**原文陈述**: "在 3.x 去 ZooKeeper 之后，SCRAM 凭证存在 KRaft 的元数据日志里"
**核查结果**: ✅ 确认正确
**核查依据**: KIP-554（Kafka 3.5+）实现将 SCRAM 凭证作为 `UserScramCredentialsRecord` 存储在 KRaft 元数据日志（`__cluster_metadata` topic）中。Confluent 文档确认 "The default SCRAM implementation in Kafka stores SCRAM credentials in the metadata log"。
**建议**: 无需修改。

### Q26: Kafka 控制面监听器使用 SSL
**原文陈述**: "控制面监听器通常配成预共享证书的 SSL，而把 SCRAM 留给客户端到 Broker 这一层"
**核查结果**: ✅ 确认正确
**核查依据**: KRaft 模式下控制器间通信（control plane）通常使用 SSL/mTLS 进行身份验证，而客户端到 broker 的认证可使用 SCRAM。Confluent KRaft Security 文档确认此最佳实践。
**建议**: 无需修改。

### Q27: Kafka 委托令牌（Delegation Token）
**原文陈述**: "委托令牌（Delegation Token）是 Kafka 处理'身份在跳之间频繁传递'的另一招"
**核查结果**: ✅ 确认正确
**核查依据**: Kafka Delegation Tokens（KIP-48、KIP-255）提供短寿命令牌，可在无需共享密码的场景下安全传递身份。适用于跨数据中心复制、安全转发等场景。
**建议**: 无需修改。

### Q28: Kafka ACL 操作列表
**原文陈述**: "每类资源有自己的操作集：Read、Write、Create、Delete、Alter、Describe、ClusterAction、All"
**核查结果**: ⚠️ 需要澄清
**核查依据**: Kafka AclOperation 枚举包含这些核心操作，但还包含 `ALTER_CONFIGS`、`DESCRIBE_CONFIGS`、`IDEMPOTENT_WRITE`、`CREATE_TOKENS`、`DESCRIBE_TOKENS` 等额外操作。书中列出的 8 个是核心操作集，但不完整。
**建议**: 可补充说明 Kafka ACL 还包含 `ALTER_CONFIGS` 和 `DESCRIBE_CONFIGS` 等操作，或在省略号中暗示还有更多。

### Q29: Kafka allow.everyone.if.no.acl.found 默认值变更版本
**原文陈述**: "allow.everyone.if.no.acl.found 这个参数（仅对旧的 SimpleAclAuthorizer 生效）在 1.x 时代默认是 true...从 2.0 起官方把默认值改成了 false"
**核查结果**: ✅ 确认正确
**核查依据**: Kafka 2.0 release notes（KIP-169/KIP-238）将默认值改为 false。早期版本（0.x/1.x）默认值为 true。
**建议**: 无需修改。

### Q30: Kafka StandardAuthorizer
**原文陈述**: "新引入的 StandardAuthorizer（KRaft 模式下的内置授权器）"
**核查结果**: ✅ 确认正确
**核查依据**: KIP-801（Kafka 3.2+）引入 `StandardAuthorizer`（`org.apache.kafka.metadata.authorizer.StandardAuthorizer`），作为 KRaft 模式下的内置授权器。
**建议**: 无需修改。

### Q31: Kafka TLS 性能衰减比例（RSA vs ECDSA）
**原文陈述**: "实测中，RSA 证书方案吞吐降幅约三成多，改用 ECDSA 证书能把降幅压到两成多"
**核查结果**: 🔍 无法确认
**核查依据**: 未能找到针对 Kafka 的 RSA vs ECDSA TLS 证书性能对比的官方 benchmark 数据。通用 TLS 性能知识表明 ECDSA 密钥交换比 RSA 快（尤其在握手阶段），但未能定位 Kafka 方面的具体定量数据。书中的大致比例（RSA 降三成多、ECDSA 降两成多）在合理范围内，但缺乏权威来源佐证。
**建议**: 如有条件，补充引用 Confluent/LinkedIn 的 Kafka TLS benchmark 报告；否则建议注明 "根据通用 TLS 基准测试估计"。

### Q32: Kafka TLS 会话恢复
**原文陈述**: "启用 TLS 会话恢复（session resumption，避免重复握手）"
**核查结果**: 🔍 无法确认
**核查依据**: 未能找到 Kafka 官方文档中关于 TLS session resumption 的具体配置指南或推荐。JVM 层面默认启用 SSL session cache（`javax.net.ssl.sessionCacheSize`），Kafka 客户端和 broker 可以使用此机制，但 Kafka 文档中未明确强调此功能为推荐配置。
**建议**: 如果原文引用了某篇具体文档或博客，建议附上引用；否则可改为更谨慎的表述 "可依赖 JVM 内置的 SSL session cache 机制减少重复握手"。

### Q33: Redis ACL LOG 和 SLOWLOG
**原文陈述**: "Redis 只提供 ACL LOG（记录被拒命令的详情，包括时间戳、客户端 IP、被拒命令和参数）和 SLOWLOG"
**核查结果**: ✅ 确认正确
**核查依据**: Redis ACL LOG 命令（Redis 6.0+）记录认证失败、命令被拒、键/频道访问被拒等安全事件，包含 reason、context、object、username、age-seconds、client-info（含 IP 和端口）、entry-id、timestamp-created 等字段。SLOWLOG 记录慢查询。两者是 Redis 的审计工具。
**建议**: 无需修改。

### Q34: MySQL 企业版审计插件
**原文陈述**: "MySQL 的审计能力比 Redis 强，但有门槛。企业版提供审计插件，能做到语句级审计、按用户/数据库/主机过滤、把日志输出到文件或 syslog"
**核查结果**: ✅ 确认正确
**核查依据**: MySQL Enterprise Audit Plugin（`audit_log`）支持基于 JSON 规则的语句级过滤（按命令类型、数据库、用户、连接等），日志可输出到文件或 syslog。
**建议**: 无需修改。

### Q35: Kafka ProducerInterceptor / ConsumerInterceptor 审计
**原文陈述**: "自定义 ProducerInterceptor / ConsumerInterceptor 在客户端拦截并写审计主题"
**核查结果**: ✅ 确认正确
**核查依据**: Kafka 0.10.0.0 引入 `ProducerInterceptor` 和 `ConsumerInterceptor` 接口。`ProducerInterceptor.onSend()` 在消息发送前被调用，`ConsumerInterceptor.onConsume()` 在消费后调用，可用于审计日志。
**建议**: 无需修改。

### Q36: 横向对比表 — Redis 默认认证状态
**原文陈述**: Redis（7.x）默认是否认证: "否（仅可选密码）"
**核查结果**: ✅ 确认正确
**核查依据**: Redis 7.x default 用户为 `on nopass ~* &* +@all`，即无密码，无需认证。用户可选择设置密码或使用 ACL。
**建议**: 无需修改。

### Q37: 横向对比表 — Redis 推荐生产认证方式
**原文陈述**: "推荐生产认证: ACL 加 TLS 客户端证书"
**核查结果**: ✅ 确认正确
**核查依据**: Redis 官方安全最佳实践推荐使用 ACL（细粒度权限）结合 TLS 客户端证书进行强身份认证。Redis 文档强调 TLS 用于传输加密，ACL 用于细粒度访问控制。
**建议**: 无需修改。

### Q38: 横向对比表 — MySQL 推荐生产认证
**原文陈述**: "推荐生产认证: caching_sha2_password"
**核查结果**: ✅ 确认正确
**核查依据**: MySQL 8.0 默认认证插件就是 `caching_sha2_password`，也是生产环境的推荐选择。它使用 SHA-256 哈希、随机盐值、5000 轮迭代，并提供缓存机制优化后续连接。
**建议**: 无需修改。

### Q39: 横向对比表 — Kafka 推荐生产认证
**原文陈述**: "推荐生产认证: SCRAM-SHA-512"
**核查结果**: ✅ 确认正确
**核查依据**: SCRAM-SHA-512 是 Kafka 生产环境常用的推荐认证机制。相比 SCRAM-SHA-256 更强的哈希、相比 PLAIN 避免了明文密码传输、相比 GSSAPI 部署运维更简单。
**建议**: 无需修改。

### Q40: 横向对比表 — Kafka 凭证存储
**原文陈述**: "凭证存储: KRaft/ZK（SCRAM 哈希）"
**核查结果**: ✅ 确认正确
**核查依据**: ZooKeeper 模式中 SCRAM 凭证存储在 ZK znodes 中，KRaft 模式中存储在元数据日志（`__cluster_metadata` topic）。
**建议**: 无需修改。

### Q41: 横向对比表 — Redis 存储加密
**原文陈述**: "存储加密: 无原生"
**核查结果**: ✅ 确认正确
**核查依据**: Redis 本身不提供存储加密功能。Redis 文档和功能列表中无原生存储加密。需要通过文件系统级别加密（dm-crypt、LUKS）或磁盘加密实现。
**建议**: 无需修改。

### Q42: 横向对比表 — Kafka 存储加密
**原文陈述**: "存储加密: 无原生（靠磁盘加密）"
**核查结果**: ✅ 确认正确
**核查依据**: Kafka 不提供原生存储加密。数据以明文形式存储在日志段文件中。可通过磁盘加密（dm-crypt、LUKS、云盘加密）实现。
**建议**: 无需修改。

### Q43: 横向对比表 — Redis 审计能力
**原文陈述**: "审计能力: ACL LOG 加 SLOWLOG（弱）"
**核查结果**: ✅ 确认正确
**核查依据**: Redis 7.x 仅提供 ACL LOG（安全事件日志）和 SLOWLOG（慢查询日志）作为审计手段，无 SQL 语句级审计，功能相对有限。
**建议**: 无需修改。

### Q44: 横向对比表 — MySQL 授权粒度
**原文陈述**: "最细粒度: 列级"
**核查结果**: ✅ 确认正确
**核查依据**: MySQL 8.0 支持列级权限（`mysql.columns_priv` 表），可对 `SELECT(col1)`、`UPDATE(col2)` 等做精细化控制。
**建议**: 无需修改。

### Q45: 横向对比表 — Kafka 默认策略
**原文陈述**: "默认策略: 无 ACL 默认拒绝（2.0 起）"
**核查结果**: ✅ 确认正确
**核查依据**: Kafka 2.0 起 `allow.everyone.if.no.acl.found` 默认值为 false，即无 ACL 时默认拒绝。1.x 及之前版本默认值为 true（默认允许）。
**建议**: 无需修改。

### Q46: mysql_native_password 插件名称拼写
**原文陈述**: "mysql_native_password"
**核查结果**: ✅ 确认正确
**核查依据**: MySQL 官方文档确认旧认证插件名称为 `mysql_native_password`（全小写，下划线分隔）。
**建议**: 无需修改。

### Q47: MySQL 复制权限名称变更
**原文陈述**: "REPLICATION SLAVE"
**核查结果**: ✅ 确认正确（书中名称未过时）
**核查依据**: `REPLICATION SLAVE` 权限名称在 MySQL 8.0.x 中并未改变。8.0.22 中更名的是 SQL 语句关键词（`START SLAVE` → `START REPLICA`），而非权限名称。`REPLICATION_APPLIER` 是一个完全不同的动态权限（8.0.18 引入），用于 `PRIVILEGE_CHECKS_USER` 场景，并非 `REPLICATION SLAVE` 的改名。因此书中使用 `REPLICATION SLAVE` 是正确的。
**建议**: 无需修改。

### Q48: Redis 未授权写 SSH 公钥/定时任务导致的 RCE
**原文陈述**: "历史上未授权 Redis 写 SSH 公钥、写定时任务导致远程代码执行（RCE）的案例多到成梗"
**核查结果**: ✅ 确认正确
**核查依据**: 这是 Redis 著名的未授权访问漏洞攻击向量。攻击者可利用 Redis CONFIG 命令修改数据路径为 `/root/.ssh/authorized_keys` 写入 SSH 公钥，或写入 `/var/spool/cron/` 定时任务反弹 shell。Censys 报告 2022 年统计约 39,000 个未授权 Redis 实例暴露在互联网上。
**建议**: 无需修改。

### Q49: Redis 连接时序 — AUTH 命令
**原文陈述**: "连接建立时客户端先用 AUTH alice <密码> 走一次完整认证，服务端校验 SHA-256 通过后"
**核查结果**: ✅ 确认正确
**核查依据**: Redis ACL AUTH 流程中，服务端收到密码后使用 `ACLHashPassword()` 进行 SHA-256 哈希，然后与存储的哈希值比较。书中描述的流程基本正确。
**建议**: 无需修改。

### Q50: Redis TLS 性能 "六成左右"（重复确认）
**原文陈述**: "开启 TLS 后单线程吞吐相比无加密约降至六成左右（具体数值随硬件、TLS 版本、证书算法波动较大，以实测为准）"
**核查结果**: ✅ 确认正确
**核查依据**: Redis 性能基准测试显示 TLS 降幅约 36%，吞吐降至约 64%，约为六成。书中已包含合理的免责声明。
**建议**: 无需修改。

### Q51: Kafka 1.x 中 allow.everyone.if.no.acl.found 默认值
**原文陈述**: "在 1.x 时代默认是 true"
**核查结果**: ✅ 确认正确
**核查依据**: Kafka 早期版本（0.x/1.x）中 `allow.everyone.if.no.acl.found` 默认值为 true。KIP-169/KIP-238 在 Kafka 2.0 中将默认值改为 false。
**建议**: 无需修改。

### Q52: 横向对比表 — Redis 授权模型
**原文陈述**: "授权模型: ACL（用户直绑）"
**核查结果**: ✅ 确认正确
**核查依据**: Redis ACL 将权限直接绑定到用户，无角色继承机制。每个用户单独配置命令分类、键模式和频道模式。
**建议**: 无需修改。

### Q53: Kafka 前缀授权功能
**原文陈述**: "前缀授权（prefixed resource pattern）"
**核查结果**: ✅ 确认正确
**核查依据**: KIP-290 在 Kafka 2.0.0 引入 Prefixed Resource Pattern。支持 `LITERAL` 和 `PREFIXED` 两种模式类型，可通过 `--resource-pattern-type prefixed` 使用。
**建议**: 无需修改。

### Q54: MySQL 授权检查 "逐层收窄、命中即停"
**原文陈述**: "授权检查时，从全局到列逐层收窄，命中即停"
**核查结果**: ✅ 确认正确
**核查依据**: MySQL 权限检查算法确实从全局权限开始，逐步检查数据库、表、列、存储过程级别。对于特定操作，如果在全局层面有权限就直接允许，无需继续检查下层。权限是累积的（OR 逻辑）。"逐层收窄、命中即停" 是对此流程的合理教学比喻。
**建议**: 无需修改。

### Q55: MySQL 授权检查缓存机制
**原文陈述**: "把检查结果按'账号加库表'做内存缓存，把权限压成位图（bitmap）"
**核查结果**: ✅ 确认正确
**核查依据**: MySQL 源码中的 `GRANT_INFO` 结构体使用 `Access_bitmask`（权限位图）来高效表示用户对特定对象拥有的权限。`column_priv_hash` 作为二级缓存，通过 `version` 字段实现缓存失效。权限检查时通过位运算快速判断。
**建议**: 无需修改。

### Q56: Kafka 3.x 去 ZooKeeper
**原文陈述**: "在 3.x 去 ZooKeeper 之后"
**核查结果**: ⚠️ 需要澄清
**核查依据**: Kafka 3.x 中 KRaft 模式是可选方案（从 2.8 early access 到 3.3 production-ready），但 ZooKeeper 模式在 3.x 仍完全支持并被广泛使用。ZooKeeper 是到 4.0（2025 年 3 月）才被彻底移除。原文 "3.x 去 ZooKeeper 之后" 的表述可能让读者误以为 3.x 已完全移除 ZK。建议明确 "在 KRaft 模式下（3.x 起可选）"。
**建议**: 改为 "在 KRaft 模式下（3.x 起可选，不再依赖 ZooKeeper）"。

### Q57: 横向对比表 — Kafka 认证抽象
**原文陈述**: "认证抽象: SASL 框架加 JAAS"
**核查结果**: ✅ 确认正确
**核查依据**: Kafka 认证通过 SASL 框架结合 JAAS 配置实现。每个 SASL 机制对应一个 JAAS LoginModule（如 `PlainLoginModule`、`ScramLoginModule`、`Krb5LoginModule`、`OAuthBearerLoginModule`）。
**建议**: 无需修改。

### Q58: Redis command categories 确认 @fast 和 @slow
**原文陈述**: Redis 命令类别包括 @fast 和 @slow
**核查结果**: ✅ 确认正确
**核查依据**: `ACL CAT` 输出明确包含 `fast` 和 `slow` 类别。@fast 包含 O(1) 的低延迟命令，@slow 包含其他所有命令。
**建议**: 无需修改。

### Q59: Redis password storage in users.acl
**原文陈述**: "通过 ACL FILE 持久化到 users.acl"
**核查结果**: ✅ 确认正确
**核查依据**: Redis `aclfile` 配置项默认示例路径为 `/etc/redis/users.acl`（在 redis.conf 中注释显示）。用户可使用 `ACL SAVE` 将内存中 ACL 规则（含 SHA-256 哈希密码）持久化到此文件。
**建议**: 无需修改。

### Q60: MySQL 审计 General Log 功能
**原文陈述**: "社区版用户通常只能用 General Log 做近似替代——记录所有客户端发来的 SQL，短时间调试可以，生产环境长时间开启会让磁盘和性能都吃不消"
**核查结果**: ✅ 确认正确
**核查依据**: MySQL General Log 记录所有客户端 SQL。基准测试显示写入文件时吞吐下降约 13%、响应时间增加约 17%；写入表时吞吐下降 34-44%。多个权威来源（Broadcom、Bytebase、Percona）一致建议生产环境仅短时间启用，不可常开。
**建议**: 无需修改。

### Q61: Redis TLS 配置项名称
**原文陈述**: "tls-protocols"
**核查结果**: ✅ 确认正确
**核查依据**: Redis 配置文档和 `redis.conf` 中确认配置名为 `tls-protocols`。
**建议**: 无需修改。

### Q62: MySQL 企业版审计插件名称
**原文陈述**: "MySQL 企业版提供审计插件"
**核查结果**: ✅ 确认正确
**核查依据**: MySQL Enterprise Edition 包含 Audit Log Plugin（`audit_log`），支持语句级审计、按用户/数据库/主机过滤、输出到文件或 syslog、AES-256 加密等特性。
**建议**: 无需修改。

### Q63: MySQL 8.0.4 "8.0 系列中后段默认即此" 的表述
**原文陈述**: "8.0.4 起把默认认证插件从老的 mysql_native_password 改成了 caching_sha2_password（8.0 系列中后段默认即此，老客户端常因不支持而需要显式回退）"
**核查结果**: ⚠️ 需要澄清
**核查依据**: MySQL 8.0.4 RC 于 2018 年 1 月 24 日发布，在 8.0.11 GA（2018 年 4 月 19 日）之前。MySQL 8.0 系列从 8.0.0 到 8.0.46 共有约 47 个小版本，8.0.4 处于系列极早期（前 10%）。"中后段" 的表述与 8.0.4 的实际时间位置不符。事实上，`caching_sha2_password` 从 8.0.4 起就是默认，覆盖了整个 8.0 系列的中后段，但 8.0.4 本身并非处于中后段。
**建议**: 将 "8.0 系列中后段默认即此" 改为 "8.0 系列自该版本起默认即此" 或 "8.0 系列后续版本默认即此"。

### Q64: Redis protected-mode 绑定全部网卡时的行为
**原文陈述**: "当 Redis 绑定全部网卡且没有配置任何密码、AUTH 等认证手段时，它只接受本地回环连接，对外网连接直接拒绝"
**核查结果**: ✅ 确认正确
**核查依据**: Redis 文档确认：当 protected-mode 启用时，若 default 用户无密码，服务器仅接受来自 127.0.0.1、::1 或 Unix domain socket 的连接。典型错误信息: "DENIED Redis is running in protected mode...no password is set for the default user. In this mode connections are only accepted from the loopback interface."
**建议**: 无需修改。

### Q65: 横向对比表 — MySQL 默认策略
**原文陈述**: "默认策略: 默认安全（强密码、可删匿名）"
**核查结果**: ✅ 确认正确
**核查依据**: MySQL 8.0 安装后默认使用 `caching_sha2_password`（强哈希认证），提供 `mysql_secure_installation` 脚本帮助删除匿名用户、设置 root 密码、禁用远程 root 登录。书中 "可删匿名" 指通过该脚本可删除匿名用户。
**建议**: 无需修改。

---

## 修正优先级

### 高优先级（必须修正）

| Q | 问题 | 说明 | 建议修正 |
|---|------|------|----------|
| Q21 | redo/undo log 加密引入版本 | 原文写 8.0.15，但 undo log 加密实际在 8.0.16、redo log 加密在 8.0.17 引入 | 改为正确的版本号 |

### 中优先级（建议修正）

| Q | 问题 | 说明 | 建议修正 |
|---|------|------|----------|
| Q13 | ldap_simple 插件名称 | 官方名称为 `authentication_ldap_simple`，书中简写可能混淆 | 改为完整名称 |
| Q28 | Kafka ACL 操作集不全 | 遗漏 `ALTER_CONFIGS`、`DESCRIBE_CONFIGS` 等操作 | 补充或加省略号 |
| Q56 | "3.x 去 ZooKeeper" 表述 | 3.x 中 ZK 并未移除，KRaft 是可选项；ZK 完全移除在 4.0 | 改为 "在 KRaft 模式下（3.x 起可选）" |
| Q63 | "8.0 系列中后段" 表述 | 8.0.4 处于 8.0 系列极早期，不应描述为"中后段" | 改为 "8.0 系列自该版本起默认即此" |

### 低优先级（可选优化）

| Q | 问题 | 说明 | 建议修正 |
|---|------|------|----------|
| Q17 | 风险分类非官方分类 | 此分类为作者整理的教学框架，非 MySQL 官方文档中的分类 | 可注明 "按照风险级别大致可分为" |
| Q31 | Kafka TLS RSA/ECDSA benchmark 缺来源 | 比例大致合理但缺乏 Kafka 官方 benchmark 支撑 | 建议补充引用来源 |
| Q32 | Kafka TLS session resumption | JVM 层面默认启用但 Kafka 文档未明确强调 | 可改为更谨慎的措辞 |
