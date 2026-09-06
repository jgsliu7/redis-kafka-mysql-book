# B 负责章节来源账本

本文件供合并参考文献与复核，不进入电子书正文。核查日期 2026-09-05。Redis 7.x、MySQL 8.0.x 的小版本差异需与具体叙述配套；Kafka 精确实现为 3.9.0。官方在线页中最新说明不自动外推全部基线版本。以下链接标识已在正文使用。

## 第 5 章

| 标识 | 官方来源 | 支撑范围 |
|---|---|---|
| R5-01 | https://redis.io/docs/latest/develop/reference/clients/ | 客户端输出缓冲、硬软限制、普通客户端该限制默认0；另核7.2分支redis.conf |
| R5-02 | https://redis.io/docs/latest/commands/unlink/ | 键移除与异步内存释放的区分，不声称所有删除路径总异步 |
| R5-03 | https://dev.mysql.com/doc/refman/8.0/en/pluggable-storage-overview.html | MySQL引擎接口、引擎能力差异 |
| R5-04 | https://dev.mysql.com/doc/refman/5.7/en/query-cache-operation.html | 历史Query Cache的查询结果和表更新失效；明确历史5.7 |
| R5-05 | https://dev.mysql.com/doc/refman/8.0/en/mysql-nutshell.html | Query Cache在8.0移除 |
| R5-06 | https://kafka.apache.org/39/design/protocol/ | API键/版本及请求响应，不等同全部领域逻辑 |
| R5-07 | https://kafka.apache.org/39/design/design/ | 文件传输优化及SSL不使用所述sendfile路径；不引用过时硬件吞吐 |
| R5-08 | https://kafka.apache.org/39/operations/tiered-storage/ | 远程存储接口/部署条件；与T5源码事实相配套 |

补充基线：Redis https://github.com/redis/redis/blob/7.2/redis.conf；Kafka 3.9.0 TierStateMachine https://github.com/apache/kafka/blob/3.9.0/core/src/main/java/kafka/server/TierStateMachine.java ，副本辅助状态恢复后续传的路径不推广为任意故障保证。

## 第 6 章

| 标识 | 官方来源 | 支撑范围 |
|---|---|---|
| R6-01 | https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/ | 用户/密码/ACL持久化，off不直接终止已有会话 |
| R6-02 | https://redis.io/docs/latest/commands/acl-dryrun/ | Redis7.0起DRYRUN；不执行真实命令 |
| R6-03 | https://dev.mysql.com/doc/refman/8.0/en/caching-sha2-pluggable-authentication.html | 完整/缓存认证；RSA密码交换不加密后续业务流量 |
| R6-04 | https://kafka.apache.org/39/security/authentication-using-sasl/ | SASL与传输协议区别、机制与委托令牌；不作控制器永不支持SCRAM断言 |
| R6-05 | https://redis.io/docs/latest/operate/oss_and_stack/management/security/ | protected mode与网络/认证配置的边界 |
| R6-06 | https://dev.mysql.com/doc/refman/8.0/en/request-access.html | 不同适用作用域授权组合；程序权限为独立对象分支 |
| R6-07 | https://dev.mysql.com/doc/refman/8.0/en/partial-revokes.html | 8.0.16起partial_revokes、数据库级限制范围 |
| R6-08 | https://kafka.apache.org/39/security/authorization-and-acls/ | 授权器无匹配ACL默认拒绝（superusers例外）、可显式改变 |
| R6-09 | https://redis.io/docs/latest/operate/oss_and_stack/management/security/encryption/ | TLS各通道与客户端证书；不把证书等同任意ACL用户 |
| R6-10 | https://dev.mysql.com/doc/refman/8.0/en/innodb-data-encryption.html | 表空间/日志加密范围、keyring组件/插件、密钥恢复依赖 |

本轮对软件运行命令未连接真实Redis/MySQL/Kafka服务；示例为基线文档支持的隔离演示，最终核验说明应保留该限制。

## 第 7 章

| 标识 | 官方或原始来源 | 支撑范围 |
|---|---|---|
| R7-01 | https://doi.org/10.1145/564585.564601 | Gilbert/Lynch CAP原始论文；不是产品分类体系 |
| R7-02 | https://redis.io/docs/latest/commands/wait/ | WAIT复制确认不能等同强一致系统 |
| R7-03 | https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/ | SDOWN/ODOWN quorum与故障转移授权多数派、候选选择 |
| R7-04 | https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/ | 槽/重定向/投票资格/分区写损失窗口；不扩展新版本特性 |
| R7-05 | https://dev.mysql.com/doc/refman/8.0/en/replication-semisync.html | ACK包含relay log写入刷盘，不等同已应用 |
| R7-06 | https://dev.mysql.com/doc/refman/8.0/en/group-replication.html | 组通信、认证、单主/多主与完整组副本 |
| R7-07 | https://dev.mysql.com/doc/refman/8.0/en/group-replication-consistency-guarantees.html | group_replication_consistency可见性/等待边界 |
| R7-08 | https://kafka.apache.org/39/configuration/producer-configs/ | acks、分区器、键映射前提，3.9配置 |
| R7-09 | https://kafka.apache.org/39/configuration/topic-level-configs/ | min.insync.replicas、unclean.leader.election.enable |
| R7-10 | https://kafka.apache.org/39/operations/kraft/ | Controller/Broker角色与元数据日志，不等同业务分区Raft |

正文是机制与论证重写，不宣称已经执行实际Redis/MySQL/Kafka集群故障演练；未采用原文无同口径依据的吞吐、跨AZ延迟或百万分区保证。
