# 第8章 数据同步机制

在分布式系统中，数据同步是永恒的主题。无论是为了扩展读性能、保证高可用，还是实现地理分布，数据都需要在多个节点间保持一致。然而，一致性与可用性、性能往往难以兼得。本章将深入分析 Redis、MySQL 和 Kafka 的数据同步机制，探索不同场景下的同步策略选择。

## 8.1 数据同步的核心挑战

数据同步面临三大核心挑战：一致性、延迟和容错。

一致性描述的是多个副本之间的数据状态关系。强一致性要求任何读取都能返回最新的写入；顺序一致性要求所有进程看到的操作顺序一致；因果一致性要求因果相关的操作顺序一致；最终一致性则保证若无新写入，最终所有副本一致。从强到弱，一致性要求递减，但系统可用性和性能通常递增。

同步延迟来源于多个环节：网络传输（数据包在网络中的传播时间）、磁盘写入（副本持久化到磁盘的时间）和处理开销（序列化、压缩、验证等 CPU 操作）。降低延迟往往意味着接受更弱的一致性保证。

容错能力决定系统在故障时的行为，需要应对节点故障（主节点宕机、从节点失联）、网络分区（脑裂、分区导致的隔离）和数据损坏（磁盘错误、内存损坏）。优秀的同步机制需要在各种故障场景下都能保证数据安全。

## 8.2 Redis：主从复制与 Sentinel 高可用

Redis 的复制机制设计简洁高效，优先考虑低延迟和高吞吐，接受最终一致性。

### 复制架构演进

Redis 的复制经历了从旧版到 PSYNC 的重大改进。旧版 SYNC 的问题是每次断线重连都需要全量同步，即使只丢失了几条命令。主节点收到 SYNC 请求后生成 RDB 快照并传输给从节点，这个过程会阻塞主节点。

PSYNC 引入了复制偏移量（Replication Offset）和复制积压缓冲区（Replication Backlog）。主节点内存中维护固定大小（默认 1MB）的 Backlog，从节点记录自己的 offset，断线后重连时上报 PSYNC 命令携带 replid 和 slave_offset。若 slave_offset 在 backlog 范围内则进行部分重同步，否则触发全量重同步。

Redis 2.8.18 引入无盘复制，避免全量同步时的磁盘 I/O。传统复制流程是内存到 RDB 文件到磁盘再到网络最后到从节点，无盘复制则跳过磁盘直接从内存到网络再到从节点。

### 复制流程详解

全量同步流程分为四个阶段。首先是握手建立，从节点向主节点发送 REPLICAOF 命令，主节点返回 PONG。然后是 PSYNC 协商，从节点发送 PSYNC ? -1（首次同步，无 offset），主节点返回 +FULLRESYNC replid offset。接着是 RDB 生成与传输，主节点将 RDB 文件流发送给从节点。最后是命令传播，主节点持续向从节点发送增量命令流进行实时同步。

从节点每秒向主节点发送 REPLCONF ACK offset，主节点据此判断从节点的同步状态。主节点 info 中的复制状态显示 master_repl_offset（主节点当前偏移量）和各个从节点的信息（ip、port、state、offset、lag）。

### 主从拓扑与读写分离

Redis 支持多种复制拓扑。链式复制（Master -> Slave1 -> Slave2 -> Slave3）减轻主节点压力，但会增加延迟。树形复制在大量从节点时能有效分散复制负载。

### Sentinel 高可用架构

Redis Sentinel 提供了自动故障转移能力。架构包含 Client、多个 Sentinel、Master 和 Slave 组件。Sentinel 之间通过互相通信来协调故障检测和转移。

故障检测机制包含主观下线和客观下线两个阶段。主观下线（SDOWN）是单个 Sentinel 认为节点不可用，当超过 down-after-milliseconds 未响应时标记。客观下线（ODOWN）是多数 Sentinel 同意，当收到足够数量的其他 Sentinel 的 SDOWN 报告时确认。

故障转移流程是：Sentinel 发现 Master ODOWN 后向其他 Sentinel 申请成为 Leader，获得多数票后成为 Leader。Leader 从 Slave 中选出新的 Master（按优先级、偏移量、RunID 排序），向新 Master 发送 SLAVEOF NO ONE，向其他 Slave 发送 SLAVEOF 新 Master，最后更新配置纪元并广播新配置。

## 8.3 MySQL：成熟的复制生态

MySQL 的复制机制经过多年演进，从简单的异步复制发展到支持多种同步模式和高可用方案。

### Binlog 复制基础

MySQL 支持三种 Binlog 格式。STATEMENT 记录原始 SQL，简单省空间，但有副作用问题。ROW 记录行级变化，精确安全，但日志量大。MIXED 自动选择，默认平衡安全和性能。MySQL 8.0 默认使用 ROW 格式，支持更精确的数据同步。

Binlog 文件以 Magic（4 字节）开头，后跟一系列 Event。Event Header 共 19 字节，包含 Timestamp、Type、Server ID、Event Size 和 End Pos。

复制线程模型中，从节点包含 IO Thread 和 SQL Thread。IO Thread 向主节点请求 Binlog 并写入 Relay Log，SQL Thread 从 Relay Log 读取并应用到数据。MySQL 5.6+ 支持并行复制，可以基于 Schema（slave-parallel-type=DATABASE）或基于事务（slave-parallel-type=LOGICAL_CLOCK）进行并行处理。

### 复制模式详解

异步复制是默认模式，主节点提交事务后立即返回，不等待从节点确认。这种模式下客户端发送 SQL 后主节点写入 Binlog 并提交事务，立即返回 OK，从节点稍后拉取 Binlog 并应用。异步复制延迟低，但在主节点故障时可能丢失数据。

半同步复制通过安装 rpl_semi_sync_master 和 rpl_semi_sync_slave 插件并启用。主节点写入 Binlog 后发送到从节点并等待 ACK，收到 ACK 后才向客户端返回 OK。半同步复制保证至少一个从节点收到数据后才提交，平衡了性能和可靠性。

组复制（Group Replication）在 MySQL 5.7.17 引入，提供强一致性。所有写入需要多数节点确认，支持自动故障检测和自动恢复，支持单主和多主模式。单主模式只有一个 Primary 接受写入，其他都是 Secondary；多主模式所有节点都可以接受写入，自动处理冲突。

### GTID：全局事务标识

GTID（Global Transaction Identifier）是 MySQL 5.6 引入的全局事务标识符，格式为 source_uuid:transaction_id。传统复制切换时需要处理文件和位置（CHANGE MASTER TO MASTER_LOG_FILE 和 MASTER_LOG_POS），GTID 复制只需指定主节点（CHANGE MASTER TO MASTER_AUTO_POSITION=1），从节点自动找到正确的位置开始同步。

GTID 自动定位流程是：Slave 发送 GTID 集合（已执行的事务），Master 比较自己的 GTID 集合，找到第一个未执行的 GTID，从该位置开始传输 Binlog。

### 高可用方案对比

MySQL 的高可用方案包括 MHA（外部脚本检测加 SSH 切换，手动或自动，传统方案）、MGR（组复制加内置选举，自动，强一致需求）和 InnoDB Cluster（MySQL Shell 加 Router，自动，官方推荐）。

## 8.4 Kafka：分布式日志的同步艺术

Kafka 的复制机制围绕分布式日志设计，实现了高吞吐和强一致性的平衡。

### 副本模型

每个分区有一个 Leader 和多个 Follower，Leader 负责所有读写，Follower 被动复制。ISR（In-Sync Replicas）是与 Leader 保持同步的副本集合。AR（Assigned Replicas）是所有分配副本，ISR 仅包含同步中的副本，OSR 是滞后副本。若副本在 replica.lag.time.max.ms（默认 10 秒）内未同步即踢出 ISR。

### 副本同步机制

Kafka 3.x 的副本同步逻辑通过 ReplicaFetcherThread 实现。Fetcher 线程构建 Fetch 请求，向 Leader 发送请求，处理响应并写入本地日志，更新本地 HW（High Watermark）。

Leader 和 Follower 都维护 HW。Leader 端的 HW 等于 Leader LEO 和所有 ISR 成员 LEO 的最小值；Follower 端的 HW 等于 Fetch 响应中的 HW 和自己的 LEO 的最小值。消费者只能消费 HW 之前的消息（已确认复制的消息）。

### Leader 选举

Controller 处理 Leader 失效时，优先从 ISR 中选择新 Leader。若 unclean.leader.election.enable=true，可从非 ISR 中选择。默认配置为 false，保证不丢消息；设为 true 则优先可用性，可能丢消息。

### 幂等性与事务

生产者幂等性通过设置 enable.idempotence=true、acks=all 和 retries=Integer.MAX_VALUE 启用。幂等性实现使用 PID（Producer ID，每个生产者唯一标识）和 Sequence Number（每个分区单调递增的序号）。Broker 端去重逻辑是若 sequence_number 小于等于 last_committed_seq 则认为是重复消息，直接返回成功而不写入。

事务生产者通过 initTransactions、beginTransaction、send、sendOffsetsToTransaction 和 commitTransaction 实现。事务协调器（Transaction Coordinator）为每个事务性生产者分配一个 Coordinator，维护事务日志（__transaction_state），采用两阶段提交（Prepare -> Commit/Abort）。

## 8.5 对比分析：CAP 权衡与同步策略

CAP 定理指出，分布式系统无法同时满足一致性（Consistency）、可用性（Availability）和分区容错性（Partition Tolerance）。在发生网络分区时，必须在 C 和 A 之间选择。

三款软件的 CAP 选择各有特点。Redis 默认异步复制，选择 AP（最终一致），但可配置为同步（CP）。MySQL 默认异步复制，也是 AP（最终一致），但可通过半同步或组复制实现 CP。Kafka 默认 ISR 复制，AP 和 CP 可调，通过 acks 和 min.insync.replicas 配置。

Redis 的优势在于实现简单易于理解，复制延迟极低（内存操作），支持树形拓扑扩展；劣势是异步复制可能丢数据，手动故障转移复杂（需 Sentinel），无内置的一致性保证。

MySQL 的优势在于多种复制模式适应不同场景，GTID 简化拓扑管理，组复制提供强一致性；劣势是强一致性模式性能下降明显，故障转移需要外部工具，配置复杂度高。

Kafka 的优势在于 ISR 机制平衡可用性和一致性，内置 Leader 选举和自动恢复，幂等性和事务支持精确一次；劣势是强一致配置影响吞吐，消费者偏移量管理复杂，分区数受限于 ISR 同步。

## 8.6 架构启示：不同一致性需求下的设计选择

缓存系统的需求是极致性能，可接受部分数据丢失，应选择 Redis 异步复制，配置建议为关闭持久化（纯缓存场景）、异步复制和 Sentinel 自动故障转移。

金融交易系统的需求是数据零丢失，强一致性，应选择 MySQL 组复制或 Kafka acks=all。MySQL 配置建议为 group_replication_single_primary_mode=ON 和 group_replication_enforce_update_everywhere_checks=ON。Kafka 配置建议为 acks=all、enable.idempotence=true 和 min.insync.replicas=2。

日志收集系统的需求是高吞吐，可容忍少量丢失，应选择 Kafka 默认配置，建议 acks=1 或 acks=0，replication.factor=3，容忍 Unclean Leader Election。

从三款软件的同步设计中，我们可以总结出以下原则：明确一致性需求，不要为不需要强一致的场景付出性能代价，Redis 选择最终一致正是基于缓存场景的特点；将选择权交给用户，MySQL 和 Kafka 都提供多种同步模式，让用户根据场景权衡，好的设计提供选项而非强制；故障处理优于故障避免，分布式系统中故障不可避免，Sentinel、Controller、MGR 都提供了自动故障检测和恢复机制；简单优于复杂，Redis 的复制机制相对简单但满足其场景需求，不必要的复杂性会增加故障概率。

在设计数据同步方案时，可以按以下流程决策：首先进行数据重要性评估，若可丢失则选择异步复制追求性能，若不可丢失则进入下一步；然后进行一致性要求评估，若最终一致可接受则选择异步加故障恢复，若需要强一致则进入下一步；接着进行性能敏感度评估，若可容忍延迟则选择同步复制（多数确认），若需要低延迟则选择半同步或优化后的同步；最后进行可用性要求评估，若允许短暂不可用则选择 CP 方案，若必须持续可用则选择 AP 方案加补偿机制。

数据同步没有银弹。Redis、MySQL 和 Kafka 给出了不同场景下的优秀答案，但更重要的是理解这些设计背后的权衡逻辑。架构师的职责不是选择"最好"的方案，而是选择"最适合"的方案。
