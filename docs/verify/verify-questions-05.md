# 第05章《安全》事实核查问题清单

---

### Q1: Redis ACL 引入版本
**章节位置**: 5.2.1
**原文陈述**: "6.0 之前的 Redis 只有一个 `requirepass` 全局密码" / "6.0 引入 ACL"
**待确认点**: Redis ACL 功能是否确在 6.0 版本首次引入
**建议验证来源**: Redis 官方 changelog / release notes for 6.0; Redis.io 文档

### Q2: Redis 密码存储使用 SHA-256 哈希
**章节位置**: 5.2.1
**原文陈述**: "密码用 SHA-256 哈希存（通过 `ACL FILE` 持久化到 `users.acl`），不存明文"
**待确认点**: Redis ACL 密码是否使用 SHA-256 哈希存储；确认具体算法细节（是否为 SHA-256 迭代哈希，还是直接 SHA-256）
**建议验证来源**: Redis 源码 src/acl.c; Redis 文档 on ACL passwords

### Q3: Redis 密码哈希无加盐
**章节位置**: 5.2.1
**原文陈述**: "SHA-256 是哈希不是加密，且无加盐"
**待确认点**: Redis ACL 的密码哈希是否确实不加盐
**建议验证来源**: Redis 源码 src/acl.c; Redis 安全文档

### Q4: Redis 命令类别分组
**章节位置**: 5.2.2
**原文陈述**: "Redis 把上百条命令折叠成几个语义组：`@read`、`@write`、`@admin`、`@dangerous`、`@fast`、`@slow`"
**待确认点**: Redis AUC 命令类别是否包含这些确切分组，是否有遗漏
**建议验证来源**: Redis 官方 ACL 文档; `ACL CAT` 命令输出; Redis 源码 src/server.h 中命令分组定义

### Q5: Redis 通道权限引入版本
**章节位置**: 5.2.2
**原文陈述**: "6.2 之后，通道（channel）权限也独立出来"
**待确认点**: Pub/Sub channel 权限是否确在 Redis 6.2 引入
**建议验证来源**: Redis 6.2 release notes; Redis 文档

### Q6: Redis 7.x default 用户内置规则
**章节位置**: 5.2.2
**原文陈述**: "7.x 里 `default` 用户的内置规则仍是 `user default on nopass ~* &* +@all`"
**待确认点**: Redis 7.x 中 default 用户的默认 ACL 规则是否确为此值
**建议验证来源**: 在 Redis 7.x 实例上运行 `ACL LIST`; Redis 7.0 release notes

### Q7: Redis protected-mode 引入版本和默认值
**章节位置**: 5.2.2
**原文陈述**: "protected-mode（保护模式，3.2.0 起，默认开启）"
**待确认点**: protected-mode 是否确在 Redis 3.2.0 引入，默认是否开启
**建议验证来源**: Redis 3.2 release notes; redis.conf default config

### Q8: Redis 原生 TLS 支持版本
**章节位置**: 5.2.3
**原文陈述**: "Redis 到 6.0 才原生支持 TLS"
**待确认点**: Redis 是否确在 6.0 首次原生支持 TLS
**建议验证来源**: Redis 6.0 release notes / GA announcement

### Q9: Redis TLS 协议建议
**章节位置**: 5.2.3
**原文陈述**: "建议限定 `tls-protocols TLSv1.2 TLSv1.3`"
**待确认点**: Redis 配置项名称和默认建议是否确切为 `tls-protocols`
**建议验证来源**: Redis TLS 配置文档; redis.conf template

### Q10: Redis TLS 性能衰减比例
**章节位置**: 5.2.3
**原文陈述**: "开启 TLS 后单线程吞吐相比无加密约降至六成左右"
**待确认点**: Redis 开启 TLS 后的吞吐降幅是否约为 40%（降至六成）
**建议验证来源**: Redis 官方 benchmark 数据; 第三方性能对比测试

### Q11: MySQL 认证缓存的密码哈希算法
**章节位置**: 5.3.1
**原文陈述**: "新插件用 SHA-256 哈希，首次连接走完整的挑战—响应握手，之后服务端把哈希结果缓存在内存里"
**待确认点**: caching_sha2_password 是否使用 SHA-256；缓存机制描述是否准确
**建议验证来源**: MySQL 8.0 官方文档关于 caching_sha2_password 的实现细节

### Q12: MySQL 8.0.4 默认认证插件变更
**章节位置**: 5.3.1
**原文陈述**: "8.0.4 起把默认认证插件从老的 `mysql_native_password` 改成了 `caching_sha2_password`"
**待确认点**: MySQL 8.0.4 是否确实将默认认证插件从 mysql_native_password 改为 caching_sha2_password
**建议验证来源**: MySQL 8.0.4 release notes; MySQL 文档

### Q13: MySQL 可插拔认证插件名称
**章节位置**: 5.3.1
**原文陈述**: "`auth_socket` 让本机进程免密登录、`authentication_pam` 对接企业 PAM、`ldap_simple` 对接 LDAP 目录、`sha256_password` 提供无缓存的高安全选项"
**待确认点**: 这些认证插件的名称和作用是否准确
**建议验证来源**: MySQL 8.0 文档 "Authentication Plugins" 章节

### Q14: MySQL 授权层级数量
**章节位置**: 5.3.2
**原文陈述**: "权限按作用域分五层：全局、数据库、表、列、存储程序"
**待确认点**: MySQL 的权限层级是否为五层（全局/数据库/表/列/存储程序）
**建议验证来源**: MySQL 8.0 官方权限文档

### Q15: MySQL 权限表名称
**章节位置**: 5.3.2
**原文陈述**: "对应 `mysql.user`、`mysql.db`、`mysql.tables_priv`、`mysql.columns_priv`、`mysql.procs_priv` 多张权限表"
**待确认点**: MySQL 8.0 的系统权限表是否仍为这些名称
**建议验证来源**: MySQL 8.0 文档 "Grant Tables" 章节

### Q16: MySQL 8.0 RBAC 角色系统
**章节位置**: 5.3.2
**原文陈述**: "8.0 才补齐 RBAC 角色系统，支持 `CREATE ROLE`、`GRANT role TO user`、会话级 `SET ROLE`"
**待确认点**: MySQL 8.0 是否首次引入 RBAC；`CREATE ROLE`、`GRANT ... TO user`、`SET ROLE` 命令是否确为 8.0 特性
**建议验证来源**: MySQL 8.0 release notes / 文档关于角色

### Q17: MySQL 权限按风险分类
**章节位置**: 5.3.2
**原文陈述**: "权限语义按风险分四类：数据操作（DML，包括 SELECT、INSERT、UPDATE、DELETE）、结构变更（DDL，包括 CREATE、ALTER、DROP，更危险）、管理（SUPER、PROCESS、FILE、RELOAD，高度敏感）、复制（REPLICATION SLAVE、REPLICATION CLIENT，专用于复制拓扑）"
**待确认点**: 这种按风险分类是否为 MySQL 官方分类；`REPLICATION SLAVE` 在 8.x 中是否已改名为 `REPLICATION SLAVE`（事实上 8.0.22 中已更名为 `REPLICATION APPLIER`）
**建议验证来源**: MySQL 8.0 文档 "Privileges Provided by MySQL"

### Q18: MySQL FILE 权限风险描述
**章节位置**: 5.3.2
**原文陈述**: "FILE 权限能读写服务器文件系统，配合 SQL 注入可读任意文件"
**待确认点**: FILE 权限的确切权限范围
**建议验证来源**: MySQL 官方文档关于 FILE 权限的描述

### Q19: MySQL TDE 在 InnoDB 表空间级别加密
**章节位置**: 5.3.3
**原文陈述**: "TDE（Transparent Data Encryption，透明数据加密）在 InnoDB 表空间级别加密数据"
**待确认点**: MySQL TDE 是否在 InnoDB 表空间级别加密，密钥管理是否对接 HashiCorp Vault / 云 KMS
**建议验证来源**: MySQL 8.0 文档 "InnoDB Data-at-Rest Encryption"

### Q20: MySQL binlog/relay log 加密版本
**章节位置**: 5.3.3
**原文陈述**: "8.0.14 起二进制日志（binlog）与 relay log 支持加密"
**待确认点**: 二进制日志和 relay log 加密是否确在 MySQL 8.0.14 引入
**建议验证来源**: MySQL 8.0.14 release notes

### Q21: MySQL redo/undo log 加密版本
**章节位置**: 5.3.3
**原文陈述**: "8.0.15 起重做日志（redo log）、回滚日志（undo log）也支持加密"
**待确认点**: redo log 和 undo log 加密是否确在 MySQL 8.0.15 引入
**建议验证来源**: MySQL 8.0.15 release notes

### Q22: MySQL connection_control 插件
**章节位置**: 5.3.5
**原文陈述**: "可启用 `connection_control` 插件做连接失败锁定"
**待确认点**: connection_control 插件的功能和默认行为
**建议验证来源**: MySQL 8.0 文档 "Connection-Control Plugins"

### Q23: Kafka KRaft 版本
**章节位置**: 5.4
**原文陈述**: "3.x 的 KRaft"
**待确认点**: KRaft 模式是否在 Kafka 3.x 中引入/可用
**建议验证来源**: Kafka 3.0 / 3.x release notes; KIP-500

### Q24: Kafka SASL 机制列表
**章节位置**: 5.4.1
**原文陈述**: "SASL 下面挂多种机制：PLAIN、SCRAM-SHA-256、SCRAM-SHA-512、GSSAPI（Kerberos）、OAUTHBEARER（OAuth 2.0）"
**待确认点**: Kafka 支持的 SASL 机制是否包含这些，是否有遗漏（如 SCRAM-SHA-1）
**建议验证来源**: Kafka 官方安全文档

### Q25: Kafka SCRAM 凭证存储位置（3.x 去 ZK 后）
**章节位置**: 5.4.1
**原文陈述**: "在 3.x 去 ZooKeeper 之后，SCRAM 凭证存在 KRaft 的元数据日志里"
**待确认点**: 3.x 去 ZK 后（KRaft 模式下）SCRAM 凭证是否存储在 KRaft 元数据日志中
**建议验证来源**: Kafka 3.x 文档; KIP-516 / KIP-相关信息

### Q26: Kafka 控制面监听器使用 SSL
**章节位置**: 5.4.1
**原文陈述**: "控制面监听器通常配成预共享证书的 SSL，而把 SCRAM 留给客户端到 Broker 这一层"
**待确认点**: KRaft 控制面（quorum）通信是否通常使用 SSL 而非 SCRAM
**建议验证来源**: Kafka 3.x KRaft 配置文档; KIP-853 / 相关 KIP

### Q27: Kafka 委托令牌（Delegation Token）
**章节位置**: 5.4.1
**原文陈述**: "委托令牌（Delegation Token）是 Kafka 处理'身份在跳之间频繁传递'的另一招"
**待确认点**: Kafka Delegation Token 的功能和使用场景描述是否准确
**建议验证来源**: Kafka 文档 "Delegation Tokens"; KIP-255

### Q28: Kafka ACL 操作列表
**章节位置**: 5.4.2
**原文陈述**: "每类资源有自己的操作集：Read、Write、Create、Delete、Alter、Describe、ClusterAction、All"
**待确认点**: Kafka ACL 操作集合是否包含这些且完整
**建议验证来源**: Kafka 官方文档 "Authorization and ACLs"

### Q29: Kafka allow.everyone.if.no.acl.found 默认值变更版本
**章节位置**: 5.4.2
**原文陈述**: "`allow.everyone.if.no.acl.found` 这个参数（仅对旧的 `SimpleAclAuthorizer` 生效）在 1.x 时代默认是 true...从 2.0 起官方把默认值改成了 false"
**待确认点**: Kafka 是否在 2.0 版本将 `allow.everyone.if.no.acl.found` 默认值从 true 改为 false
**建议验证来源**: Kafka 2.0 release notes; KIP-169 / KIP-238

### Q30: Kafka StandardAuthorizer
**章节位置**: 5.4.2
**原文陈述**: "新引入的 `StandardAuthorizer`（KRaft 模式下的内置授权器）"
**待确认点**: StandardAuthorizer 是否在 KRaft 模式下作为内置授权器
**建议验证来源**: Kafka 3.x 文档; KIP-800 / KIP-相关信息

### Q31: Kafka TLS 性能衰减比例
**章节位置**: 5.4.3
**原文陈述**: "实测中，RSA 证书方案吞吐降幅约三成多，改用 ECDSA 证书能把降幅压到两成多"
**待确认点**: Kafka TLS 使用 RSA 与 ECDSA 证书时的具体性能降幅是否大致相符
**建议验证来源**: Kafka 官方性能测试; 第三方 benchmark 报告; LinkedIn / Confluent 工程博客

### Q32: Kafka TLS 会话恢复
**章节位置**: 5.4.3
**原文陈述**: "启用 TLS 会话恢复（session resumption，避免重复握手）"
**待确认点**: Kafka 是否支持并推荐 TLS session resumption
**建议验证来源**: Kafka TLS 配置文档; JVM TLS session cache 机制

### Q33: Redis ACL LOG 和 SLOWLOG
**章节位置**: 5.4.6
**原文陈述**: "Redis 只提供 ACL LOG（记录被拒命令的详情，包括时间戳、客户端 IP、被拒命令和参数）和 SLOWLOG"
**待确认点**: ACL LOG 和 SLOWLOG 的功能描述是否准确
**建议验证来源**: Redis 文档 on ACL LOG and SLOWLOG

### Q34: MySQL 企业版审计插件
**章节位置**: 5.4.6
**原文陈述**: "MySQL 的审计能力比 Redis 强，但有门槛。企业版提供审计插件，能做到语句级审计、按用户/数据库/主机过滤、把日志输出到文件或 syslog"
**待确认点**: MySQL 企业版审计插件是否支持这些功能
**建议验证来源**: MySQL 企业版文档 "Audit Log Plugin"

### Q35: Kafka ProducerInterceptor / ConsumerInterceptor 审计
**章节位置**: 5.4.6
**原文陈述**: "自定义 ProducerInterceptor / ConsumerInterceptor 在客户端拦截并写审计主题"
**待确认点**: Kafka 的 ProducerInterceptor 和 ConsumerInterceptor 接口是否存在且可自定义用于审计
**建议验证来源**: Kafka 文档 "Kafka Client Interceptors"

### Q36: 横向对比表 — Redis 默认认证状态
**章节位置**: 5.5 (表 5-1)
**原文陈述**: Redis（7.x）默认是否认证: "否（仅可选密码）"
**待确认点**: 7.x 中 Redis 默认是否认证（default 用户默认 nopass）的描述是否准确
**建议验证来源**: Redis 7.x 默认配置

### Q37: 横向对比表 — Redis 推荐生产认证方式
**章节位置**: 5.5 (表 5-1)
**原文陈述**: "推荐生产认证: ACL 加 TLS 客户端证书"
**待确认点**: 官方推荐的生产环境 Redis 认证方式是否确为 ACL + TLS 客户端证书
**建议验证来源**: Redis 官方安全文档 / 最佳实践

### Q38: 横向对比表 — MySQL 推荐生产认证
**章节位置**: 5.5 (表 5-1)
**原文陈述**: "推荐生产认证: caching_sha2_password"
**待确认点**: MySQL 8.0 推荐的生产环境默认认证插件是否为 caching_sha2_password
**建议验证来源**: MySQL 8.0 认证文档

### Q39: 横向对比表 — Kafka 推荐生产认证
**章节位置**: 5.5 (表 5-1)
**原文陈述**: "推荐生产认证: SCRAM-SHA-512"
**待确认点**: Kafka 官方推荐的生产环境认证机制是否为 SCRAM-SHA-512
**建议验证来源**: Kafka 安全最佳实践文档

### Q40: 横向对比表 — Kafka 凭证存储
**章节位置**: 5.5 (表 5-1)
**原文陈述**: "凭证存储: KRaft/ZK（SCRAM 哈希）"
**待确认点**: Kafka SCRAM 凭证是否存储在 KRaft 或 ZooKeeper 中
**建议验证来源**: Kafka 安全文档

### Q41: 横向对比表 — Redis 存储加密
**章节位置**: 5.5 (表 5-1)
**原文陈述**: "存储加密: 无原生"
**待确认点**: Redis 是否确实没有原生存储加密功能
**建议验证来源**: Redis 文档; Redis 功能列表

### Q42: 横向对比表 — Kafka 存储加密
**章节位置**: 5.5 (表 5-1)
**原文陈述**: "存储加密: 无原生（靠磁盘加密）"
**待确认点**: Kafka 是否确实没有原生存储加密
**建议验证来源**: Kafka 文档; Kafka 安全特性

### Q43: 横向对比表 — Redis 审计能力
**章节位置**: 5.5 (表 5-1)
**原文陈述**: "审计能力: ACL LOG 加 SLOWLOG（弱）"
**待确认点**: Redis 7.x 是否只有 ACL LOG 和 SLOWLOG 作为审计手段
**建议验证来源**: Redis 7.x 审计相关功能文档

### Q44: 横向对比表 — MySQL 授权粒度
**章节位置**: 5.5 (表 5-1)
**原文陈述**: "最细粒度: 列级"
**待确认点**: MySQL 8.0 是否仍支持列级权限
**建议验证来源**: MySQL 8.0 权限文档

### Q45: 横向对比表 — Kafka 默认策略
**章节位置**: 5.5 (表 5-1)
**原文陈述**: "默认策略: 无 ACL 默认拒绝（2.0 起）"
**待确认点**: `allow.everyone.if.no.acl.found` 默认 false 是否自 2.0 起生效
**建议验证来源**: Kafka 2.0 release notes

### Q46: Redis 2.0 验证 — mysql_native_password 插件名称拼写
**章节位置**: 5.3.1
**原文陈述**: "mysql_native_password"
**待确认点**: MySQL 旧认证插件名称拼写是否正确（应为 `mysql_native_password`）
**建议验证来源**: MySQL 8.0 文档关于认证插件

### Q47: MySQL 复制权限名称变更
**章节位置**: 5.3.2
**原文陈述**: "REPLICATION SLAVE"
**待确认点**: MySQL 8.0.22 是否已将 REPLICATION SLAVE 更名为 REPLICATION_APPLIER（检查章节使用的名称是否过时）
**建议验证来源**: MySQL 8.0.22 release notes; 权限命名变更

### Q48: Redis requirepass 和 AUTH 命令
**章节位置**: 5.2.1
**原文陈述**: "历史上未授权 Redis 写 SSH 公钥、写定时任务导致远程代码执行（RCE）的案例多到成梗"
**待确认点**: 历史 Redis 未授权访问是否涉及写 SSH 公钥和 crontab 导致 RCE
**建议验证来源**: Redis 未授权漏洞历史 (CVE); 安全公告

### Q49: Redis 连接时序 — AUTH 命令
**章节位置**: 5.2.2 (图 5-2 说明)
**原文陈述**: "连接建立时客户端先用 `AUTH alice <密码>` 走一次完整认证，服务端校验 SHA-256 通过后"
**待确认点**: Redis ACL 认证流程中，密码校验是否使用 SHA-256（两次确认）
**建议验证来源**: Redis 源码 src/acl.c; Redis 官方文档

### Q50: Redis TLS 性能 "六成左右"
**章节位置**: 5.2.3
**原文陈述**: "开启 TLS 后单线程吞吐相比无加密约降至六成左右（具体数值随硬件、TLS 版本、证书算法波动较大，以实测为准）"
**待确认点**: "六成左右" 是否对应当代常见硬件（Intel Xeon / AMD EPYC）和现代 TLS 1.3 下的典型衰减
**建议验证来源**: Redis 6.0/7.x 官方或第三方 benchmark

### Q51: Kafka 1.x 中 allow.everyone.if.no.acl.found 默认值
**章节位置**: 5.4.2
**原文陈述**: "在 1.x 时代默认是 true"
**待确认点**: Kafka 0.x / 1.x 中 SimpleAclAuthorizer 的 `allow.everyone.if.no.acl.found` 默认值是否为 true
**建议验证来源**: Kafka 早期版本源码; Kafka 1.x 文档

### Q52: 横向对比表 — Redis 授权模型
**章节位置**: 5.5 (表 5-1)
**原文陈述**: "授权模型: ACL（用户直绑）"
**待确认点**: Redis ACL 是否直接将权限绑定到用户（无角色继承）
**建议验证来源**: Redis ACL 文档

### Q53: Kafka 前缀授权功能
**章节位置**: 5.4.2
**原文陈述**: "前缀授权（prefixed resource pattern）"
**待确认点**: Kafka ACL 是否支持 prefixed resource pattern
**建议验证来源**: Kafka ACL 文档; KIP-290

### Q54: MySQL 授权检查 "逐层收窄、命中即停"
**章节位置**: 5.3.2
**原文陈述**: "授权检查时，从全局到列逐层收窄，命中即停"
**待确认点**: MySQL 授权检查的流程描述是否准确（是否有 "命中即停" 或 "最精确优先" 的正确语义）
**建议验证来源**: MySQL 官方文档 "Privilege Check" / "Privilege System"

### Q55: MySQL 授权检查缓存机制
**章节位置**: 5.3.2
**原文陈述**: "把检查结果按'账号加库表'做内存缓存，把权限压成位图（bitmap）"
**待确认点**: MySQL 权限检查结果是否通过位图缓存在内存中
**建议验证来源**: MySQL 8.0 源码 sql/auth/ 相关代码; MySQL 文档

### Q56: Kafka 3.x 去 ZooKeeper
**章节位置**: 5.4.1
**原文陈述**: "在 3.x 去 ZooKeeper 之后"
**待确认点**: Kafka 3.x 是否完全去掉了 ZooKeeper（或者只是 KRaft 模式可选，ZooKeeper 模式仍在）
**建议验证来源**: Kafka 3.x release notes; KIP-500 进度

### Q57: 横向对比表 — Kafka 认证抽象
**章节位置**: 5.5 (表 5-1)
**原文陈述**: "认证抽象: SASL 框架加 JAAS"
**待确认点**: Kafka 认证是否通过 SASL 框架配合 JAAS 配置实现
**建议验证来源**: Kafka 安全文档

### Q58: Redis command categories 确认
**章节位置**: 5.2.2
**原文陈述**: Redis 命令类别包括 `@fast` 和 `@slow`
**待确认点**: Redis ACL 是否确实有 `@fast` 和 `@slow` 命令类别
**建议验证来源**: `ACL CAT` 命令输出; Redis 文档

### Q59: Redis password storage in users.acl
**章节位置**: 5.2.1
**原文陈述**: "通过 ACL FILE 持久化到 users.acl"
**待确认点**: `aclfile` 配置项默认值是否指向 `users.acl`，持久化格式是否包含 SHA-256 哈希密码
**建议验证来源**: Redis 配置文档; redis.conf

### Q60: MySQL 审计 General Log 功能
**章节位置**: 5.4.6
**原文陈述**: "社区版用户通常只能用 General Log 做近似替代——记录所有客户端发来的 SQL，短时间调试可以，生产环境长时间开启会让磁盘和性能都吃不消"
**待确认点**: MySQL General Log 的功能和性能影响描述是否准确
**建议验证来源**: MySQL 文档 "General Query Log"

### Q61: Redis TLS 配置项名称
**章节位置**: 5.2.3
**原文陈述**: "tls-protocols"
**待确认点**: Redis TLS 配置项是否确实为 `tls-protocols`
**建议验证来源**: Redis 6.0+ TLS 配置文档; redis.conf

### Q62: MySQL 企业版审计插件名称
**章节位置**: 5.4.6
**原文陈述**: "MySQL 企业版提供审计插件"
**待确认点**: MySQL 企业版审计插件的确切名称和功能特性
**建议验证来源**: MySQL Enterprise Audit Plugin 文档

### Q63: MySQL 8.0.4 "8.0 系列中后段默认即此" 的表述
**章节位置**: 5.3.1
**原文陈述**: "8.0.4 起把默认认证插件从老的 mysql_native_password 改成了 caching_sha2_password（8.0 系列中后段默认即此，老客户端常因不支持而需要显式回退）"
**待确认点**: 括号内 "8.0 系列中后段默认即此" 是否与 "8.0.4 起" 有矛盾；8.0.4 究竟是 8.0 系列的前段还是中段
**建议验证来源**: MySQL 8.0 版本的按时间顺序排列

### Q64: Redis protected-mode 绑定全部网卡时的行为
**章节位置**: 5.2.2
**原文陈述**: "当 Redis 绑定全部网卡且没有配置任何密码、AUTH 等认证手段时，它只接受本地回环连接，对外网连接直接拒绝"
**待确认点**: protected-mode 触发条件是否与原文一致
**建议验证来源**: Redis 3.2+ 配置文档关于 protected-mode 的触发条件

### Q65: 横向对比表 — MySQL 默认策略
**章节位置**: 5.5 (表 5-1)
**原文陈述**: "默认策略: 默认安全（强密码、可删匿名）"
**待确认点**: MySQL 安装后默认是否强制设置强 root 密码；是否存在匿名用户
**建议验证来源**: MySQL 8.0 安装和安全部署指南; mysql_secure_installation 脚本行为
