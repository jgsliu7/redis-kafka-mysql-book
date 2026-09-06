# A 组已阅读来源及支持范围

- Redis数据类型：https://redis.io/docs/latest/develop/data-types/ 。仅支持数据结构服务器与基线已有类型，不把页面中新增数组/向量等类型带入Redis7.x。
- MySQL8.0多版本：https://dev.mysql.com/doc/refman/8.0/en/innodb-multi-versioning.html 。undo与旧版本；不推出所有读都无锁。
- MySQL8.0一致性非锁定读：https://dev.mysql.com/doc/refman/8.0/en/innodb-consistent-read.html 。普通一致性读范围、RR/RC快照区别。
- 先前报告A独立核查：Kafka3.9 ACL；Kubernetes probes与lifecycle hooks；MySQL8.0 option-files；Kafka3.9.0 TierStateMachine与ReplicaFetcherThread；MySQL8.0 semisync、semisync-interface、next-key-locking。来源详情见原报告§8；新稿使用时在对应章节直接放精确链接。

本记录表示资料阅读，不表示命令已运行或全部技术事实已作源码核验。

## 第2章新增核查

- https://github.com/redis/redis/blob/7.2.5/src/sds.c ：_sdsMakeRoomFor greedy/non-greedy、sdsResize，避免所有路径必倍增或永不缩容。
- https://github.com/redis/redis/blob/7.2.5/src/dict.c ：dictRehash空桶访问上限与整桶迁移；不提供不卡顿保证。
- https://github.com/redis/redis/blob/7.2.5/src/t_set.c ：setTypeAddAux中intset转listpack须数量、元素长、安全大小等条件；否则hashtable。
- https://dev.mysql.com/doc/refman/8.0/en/innodb-row-format.html ：DYNAMIC长列页外引用20字节、依赖页大小与整行。
- https://dev.mysql.com/doc/refman/8.0/en/innodb-adaptive-hash.html ：键前缀、热点页、额外维护与争用成本。
- https://redis.io/docs/latest/develop/reference/protocol-spec/ ：RESP二进制安全/请求响应/Pipeline/版本协商。
- https://dev.mysql.com/doc/dev/mysql-server/latest/page_protocol_com_query_response_text_resultset.html 与 https://dev.mysql.com/doc/dev/mysql-server/latest/page_protocol_binary_resultset.html ：经典协议文本与二进制结果集分开；非整套MySQL8.0源码核验。
- https://kafka.apache.org/39/implementation/message-format/ ：RecordBatch格式、固定字段与CRC范围。
- https://kafka.apache.org/39/design/protocol/ ：请求头v0/v1/v2、每API版本、ApiVersions共同支持范围；不将全体头写死四字段。

## 第3章新增核查

- https://redis.io/docs/latest/commands/shutdown/ ：7.0起shutdown-timeout副本追赶与NOW/FORCE/ABORT；SAVE/NOSAVE；首次AOF等拒绝关闭条件。
- https://github.com/redis/redis/blob/7.2.5/src/server.c ：基础设施/加载/服务状态相关入口；未逐行全源码认证。
- https://dev.mysql.com/doc/refman/8.0/en/innodb-recovery.html ：必要redo恢复后可接受连接，后台回滚可能与新事务锁冲突，XA PREPARE例外。
- https://dev.mysql.com/doc/refman/8.0/en/innodb-parameters.html#sysvar_innodb_fast_shutdown ：0/1/2；2刷新日志后进入需恢复的关闭，不等于SIGKILL。
- https://dev.mysql.com/doc/refman/8.0/en/option-files.html ：后读优先、--user首次例外、mysqld-auto.cnf区别。
- https://github.com/apache/kafka/blob/3.9.0/core/src/main/scala/kafka/server/BrokerLifecycleManager.scala ：RUNNING→PENDING_CONTROLLED_SHUTDOWN；心跳WantShutDown；shouldShutDown；STARTING/RECOVERY与unfence。
- https://kubernetes.io/docs/concepts/workloads/pods/probes/ ：startup/liveness/readiness不同后果。
- https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/ ：preStop之前开始宽限倒计时，钩子结束后发送TERM。

## 第4章新增核查

- https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/ ：RDB/AOF，7.x多部分AOF、base/incr/manifest、重写目的；正文没有抄其若干过强宣传概括。
- https://redis.io/docs/latest/develop/reference/eviction/ ：近似LRU采样+candidate pool、LFU、策略范围；不推导noeviction即不丢。
- https://redis.io/docs/latest/commands/waitaof/ ：7.2新增，本连接此前写的本地/副本AOF同步等待。
- https://dev.mysql.com/doc/refman/8.0/en/innodb-buffer-pool.html ：缓冲池与页替换背景。
- https://dev.mysql.com/doc/refman/8.0/en/innodb-performance-midpoint_insertion.html ：中点插入、old块时间与比例。
- https://dev.mysql.com/doc/refman/8.0/en/innodb-parameters.html#sysvar_innodb_flush_log_at_trx_commit ：0/1/2，同步周期不是严格1秒，相关文件/设备假设。
- https://dev.mysql.com/doc/refman/8.0/en/replication-options-binary-log.html#sysvar_sync_binlog ：binlog同步，与redo分别处理。
- https://dev.mysql.com/doc/refman/8.0/en/innodb-doublewrite-buffer.html ：完整页恢复来源，8.0.20起独立文件。
- https://dev.mysql.com/doc/refman/8.0/en/innodb-change-buffer.html ：二级索引修改适用范围、内存与system tablespace持久组织、后台合并。
- https://docs.kernel.org/admin-guide/sysctl/vm.html ：dirty比例分母为total available memory非总物理内存，字节/比例配置区别。
- https://kafka.apache.org/39/configuration/producer-configs/ ：acks=0/1/all及3.9默认；不等价本地fsync。

第4章命中率算例为明示的编辑假设（5μs/500μs），只演示加权均值，非设备测试；无新增真实项目性能数据。
