# 第6章 集群架构

> "单点是一切故障的根源，分布式是解决问题的手段，也是引入问题的来源。"
> —— 分布式系统第一定律

任何一个成功的软件系统，都不可避免地会面临一个抉择：**何时从单体走向集群？**

单机系统面临扩展性、高可用性和负载能力三座大山。CPU/内存/磁盘有物理上限限制了扩展性，单点故障意味着服务中断，单节点吞吐量有限难以应对高负载。集群方案通过水平扩展（加机器）、多副本冗余和请求分散解决了这些问题。

然而，分布式系统并非银弹。正如 Leslie Lamport 所说："分布式系统是指一台你甚至不知道存在的计算机，却能让你的计算机无法正常工作的系统。"

本章将深入剖析 Redis、MySQL 和 Kafka 三款系统的集群方案，看它们如何在**一致性、可用性、分区容错性（CAP）** 的三角关系中做出取舍。

---

## 6.1 Redis 集群：从主从到分布式

Redis 的集群演进经历了三个阶段：**主从复制 → Sentinel 哨兵 → Redis Cluster**。每个阶段都是为了解决特定的问题。

主从复制是 Redis 高可用的基础，也是最简单的集群形式。主节点负责处理读写请求，从节点通过复制保持数据同步，仅提供读服务。从节点可以配置为级联复制，减轻主节点的复制压力。复制配置通过`replicaof`指令指定主节点地址，设置从节点只读，并配置心跳检测间隔和复制超时时间。复制过程分为两个阶段：全量同步发生在初次连接或部分同步失败时，主节点fork子进程生成RDB文件发送给从节点，然后发送积压缓冲区的命令；部分重同步则在断线重连且offset在缓冲区内时触发，主节点仅发送断线期间的命令。Redis维护一个固定大小的循环缓冲区（默认1MB）支持部分重同步，当从节点的offset在缓冲区范围内时，可以避免昂贵的全量同步。主从复制解决了数据冗余问题，但故障转移仍需人工介入，且存在明显局限：无法水平扩展写（只有单个Master接受写操作）、内存受限（所有数据必须在单节点内存中）、客户端复杂性（需要支持Sentinel协议自动切换Master地址）。

Sentinel的出现实现了自动化故障转移。Sentinel集群由多个Sentinel节点组成，它们通过共识决策监控Redis主从集群，实现监控、通知和自动故障转移。Sentinel配置包括监控主节点、设置判定故障所需的哨兵同意数、配置无响应视为下线的时间、故障转移时的并行同步数以及故障转移超时时间，还可配置通知脚本和客户端重配置脚本。故障转移流程始于单个Sentinel检测到Master在指定时间内无响应，标记为主观下线（SDOWN），然后询问其他Sentinel，如果达到quorum数同意，则标记为客观下线（ODOWN）。随后使用Raft算法选举Leader Sentinel，每个epoch每个Sentinel只能投一票。从健康的从节点中选择新Master时，Sentinel会过滤已下线、断开连接、优先级为0的节点，按优先级最高、复制offset最大、运行ID最小的顺序选择。之后向选中的从节点发送SLAVEOF NO ONE提升为新Master，向其他从节点发送SLAVEOF指令指向新Master，最后更新Sentinel内部的master地址并执行客户端重配置脚本通知客户端。Raft选举的核心逻辑是每个Sentinel维护当前epoch（类似任期号），发现客观下线的Sentinel增加epoch成为Candidate，向其他Sentinel发送请求投票，其他Sentinel在epoch更新时投票，每个epoch只能投一次票，获得超过半数投票的Sentinel成为Leader执行故障转移。

Redis 3.0引入的Cluster模式实现了**数据分片（Sharding）** 和**自动故障转移**。Redis Cluster将键空间划分为16384个槽（0-16383），通过`slot = CRC16(key) % 16384`计算键所属的槽。例如key "user:10001"计算后可能得到slot 12345，key "order:500"可能得到slot 8901。最小配置为3主3从（每个主节点至少一个从节点），每个主节点负责一部分槽，从节点复制主节点数据并在主节点故障时接管。集群配置包括启用集群模式、指定集群配置文件路径、设置节点超时时间、配置部分槽不可用时是否停止服务以及从节点迁移阈值。Redis Cluster没有集中式的元数据服务，节点之间通过Gossip协议交换信息。Gossip消息类型包括PING（定期发送给随机节点，包含自己和已知的部分节点信息）、PONG（回复PING并携带节点信息）、MEET（邀请新节点加入集群）、FAIL（广播某节点已故障）和UPDATE（更新节点槽位信息）。传播机制是每个节点每秒向随机几个节点发送PING，收到的节点更新本地视图并继续传播，实现最终一致性。客户端路由通过MOVED和ASK重定向实现。当键在正确的节点上时直接返回结果；当槽已迁移时返回MOVED错误并携带新节点地址，客户端需要更新槽映射并向新节点重试；当槽正在迁移时返回ASK错误，客户端发送ASKING命令后重试。Java Jedis客户端配置只需指定部分节点，客户端会自动发现集群拓扑并处理槽路由。Redis Cluster存在一些限制：涉及多键的命令（MGET、事务、Lua脚本）要求所有键在同一个槽，可通过哈希标签解决（如`{user}:10001:profile`和`{user}:10001:orders`只有{}内的内容参与计算slot，确保在同一节点）；不支持多数据库（SELECT命令被禁用）；故障转移期间部分槽位可能暂时不可用。

---

## 6.2 MySQL 集群：复制的艺术

MySQL 的集群方案同样经历了从简单到复杂的演进：**异步复制 → 半同步复制 → Group Replication → InnoDB Cluster**。

MySQL的复制基于 **Binlog（二进制日志）** ，它记录了所有数据变更操作。Binlog格式包括STATEMENT（记录SQL语句如UPDATE users SET age=age+1）、ROW（记录行级变更如记录ID=5的行age从20变为21）和MIXED（混合模式，默认用STATEMENT必要时用ROW）。MySQL 8.0推荐使用ROW格式配合FULL行图像，最安全且支持GTID。主节点配置包括设置全局唯一server-id、启用Binlog、指定Binlog格式、启用GTID并强制一致性、设置Binlog保留天数和单个文件大小。从节点配置包括设置不同的server-id、启用中继日志、设置为只读模式、启用GTID。复制工作流程中，主节点执行事务并写入Binlog，Dump Thread读取Binlog发送给从节点，从节点的I/O Thread接收并写入Relay Log，SQL Thread应用Relay Log到数据库。MySQL 5.6引入的GTID（全局事务标识）让复制管理更简单，GTID格式为source_id:transaction_id，从节点可使用GTID自动定位，无需指定file/position。复制延迟是常见问题，可通过`SHOW SLAVE STATUS`查看Seconds_Behind_Master。延迟原因包括主库写入过快从库单线程SQL线程跟不上、从库有慢查询阻塞、网络延迟。MySQL 8.0的多线程复制通过设置`slave_parallel_type = LOGICAL_CLOCK`和`slave_parallel_workers`实现SQL线程并行应用。

MySQL 5.7.17引入的Group Replication（GR）实现了**多主复制**和**自动故障转移**，使用Paxos变种（XCom实现）达成共识。与传统复制的单向流、主从角色固定不同，Group Replication在单主模式下所有成员通过Paxos达成共识，Primary处理读写，Secondary只读；多主模式下所有成员都可读写，但需处理冲突。配置Group Replication需要设置server-id、启用GTID、加载group_replication插件、配置组名称、本地地址、组成员种子地址、单主模式等。第一个节点需要引导组，其他节点加入组。通过`performance_schema.replication_group_members`可查看组成员状态。Group Replication的特性包括：最多容忍(N-1)/2个节点故障的容错性；主节点故障自动选举新主的自动故障转移；事务在多数节点确认后才提交的数据一致性；以及多主模式下检测并发修改冲突的冲突检测。

MySQL 5.7+和MySQL Shell提供了**InnoDB Cluster**，将Group Replication、MySQL Router和Shell管理工具整合成完整的集群解决方案。架构组成包括：应用程序连接MySQL Router代理层；MySQL Router自动发现InnoDB Cluster拓扑，将写请求路由到Primary节点，读请求负载均衡到Secondary节点，并实现故障自动切换；底层是三个MySQL节点组成GR组，Primary可读写，Secondary只读；MySQL Shell作为管理工具用于部署集群、监控状态和故障诊断。使用MySQL Shell部署集群包括连接到第一个节点、创建集群、添加其他节点、查看集群状态等步骤。MySQL Router配置读写分离，Primary路由使用read-write模式指向Primary角色，Secondary路由使用read-only模式指向Secondary角色。

---

## 6.3 Kafka 集群：分区与复制的协奏曲

Kafka 的集群设计与其产品定位密切相关：**高吞吐、持久化、流处理**。其架构天然就是分布式的。

Kafka的Topic被划分为多个 **Partition**，每个Partition是一个有序的、不可变的消息序列。生产者根据key的hash分配到Partition，消费者组中每个Partition只能被一个消费者消费。生产者分区策略包括：指定分区号直接写入；指定key使用DefaultPartitioner（murmur2(key) % numPartitions），相同key进入同一分区保证顺序；都不指定时使用轮询或粘性分区。可自定义分区器实现特定分区逻辑，如按用户ID分区。分区数选择需要考量吞吐量（更多分区=更高并行度=更高吞吐）、顺序性（分区是顺序保证的最小单位）、消费者数（分区数≥消费者数，消费者不能超过分区数）、文件句柄（每个分区对应磁盘上的多个文件）和延迟（分区过多增加选举和恢复时间）。经验法则是单分区吞吐约10 MB/s写入或10k消息/秒，根据目标吞吐计算分区数并预留20-30%余量。

Kafka的分区可以配置多个副本（Replication）保证数据可靠性。Topic创建时指定分区数和副本因子。Leader分散在不同Broker实现负载均衡，Leader处理读写，Follower同步Leader数据。生产者确认配置`acks=all`表示等待所有ISR确认，`retries`设置发送失败重试，`enable.idempotence`启用幂等性避免重试导致重复。Controller（控制器）负责Leader选举：第一个启动的Broker成为Controller，监听ZK/KRaft的节点变化，当检测到Leader故障时从ISR列表中选择新的Leader（优先选择ISR中的副本，选择offset最新的副本），通知所有Broker更新元数据，通知生产者/消费者Leader变更。

**ISR（In-Sync Replicas）** 是Kafka实现高可用的核心概念。只有ISR中的副本才有资格成为Leader。HW（High Watermark）是消费者可见的最大offset，LEO（Log End Offset）是副本的最后一个offset。Follower复制过程包括：Follower向Leader发送Fetch请求（Fetch(offset=当前LEO)）；Leader返回数据或保持连接（长轮询）；Follower写入本地日志更新LEO；如果Follower的LEO在指定时间内同步则保持在ISR中，否则被移除。配置参数`replica.lag.time.max.ms`默认30秒，Follower超过此时间未同步即被踢出ISR。生产者acks=all时的HW和commit语义：Leader收到消息写入本地log，Follower拉取并写入本地log，当ISR中所有副本都确认后Leader更新HW，Leader向生产者确认写入成功，消费者只能读到HW之前的消息。这种设计保证即使Leader崩溃，新Leader一定有已确认的消息。

Kafka 2.8引入KRaft（Kafka Raft）模式，彻底摆脱对ZooKeeper的依赖。ZooKeeper模式存在元数据分离（配置在ZK实际状态在Kafka一致性复杂）、脑裂风险（ZK和Kafka Controller可能产生不一致视图）、扩展性限制（ZK不适合存储大量元数据分区数受限）、运维复杂（需要维护两套系统）和故障排查难（问题可能出在ZK或Kafka任何一侧）等问题。KRaft模式下，三个Broker同时作为Controller，使用Raft协议管理元数据，包括Topic分区信息、ISR列表、配置信息等。所有元数据变更都通过Raft共识。优势包括简化架构（单进程管理）、更强一致性（Raft保证元数据一致性）、更高性能（分区数支持到百万级别）和更快恢复（无需从ZK加载元数据）。KRaft配置包括设置process.roles为broker,controller、指定node.id、配置controller.quorum.voters、设置listeners和controller.listener.names、指定log.dirs。启动流程包括生成集群UUID、格式化存储目录、启动Kafka（无需ZooKeeper）。

---

## 6.4 对比分析：三种集群哲学

三款系统的集群方案在多个维度上存在差异。Redis Cluster采用16384个槽的数据分片，客户端路由；使用Gossip协议去中心化元数据管理；最终一致性协议；分片扩展写入；自动故障转移（秒级）；需要多数派处理脑裂；不支持跨分区事务。MySQL Group Replication无数据分片（单主）；使用集中式元数据管理（通过Group）；Paxos多数确认一致性协议；单主写入；自动故障转移（秒级）；多数派机制处理脑裂；支持跨分区事务。Kafka Cluster采用Partition分区，生产者路由；使用KRaft/ZK集中式元数据管理；ISR加Leader确认一致性协议；Partition并行写入；自动故障转移（亚秒级）；Controller仲裁处理脑裂；不支持跨分区事务。

在元数据管理方面，Redis Cluster的Gossip协议优点是无单点、自动发现，缺点是收敛慢、可能出现不一致视图。MySQL Group Replication的集中式优点是强一致性、Paxos保证，缺点是写入需要多数确认延迟增加。Kafka的Controller模式优点是元数据操作高效、恢复快速，缺点是Controller切换时有短暂影响。

故障转移机制方面，Redis Cluster是从节点检测主节点超时，发起选举请求，其他主节点投票（基于epoch），获得多数票后升级为主节点，广播新拓扑。MySQL Group Replication是组成员检测到主节点无响应，触发View Change，新主节点选举（权重或UUID），新主节点执行GTID对齐，对外提供服务。Kafka是Controller检测到Leader无响应，从ISR中选择新Leader（优先顺序），更新Partition元数据，通知所有Broker更新缓存，生产者/消费者自动切换（metadata刷新）。

---

## 6.5 架构启示：没有完美的集群方案

通过对 Redis、MySQL 和 Kafka 集群方案的深入分析，我们可以得出以下架构启示。

CAP定理指出在网络分区发生时，必须在一致性（C）和可用性（A）之间选择，分区容错性（P）是必须保证的。各系统的CAP选择不同：Redis Cluster选择AP，分区时可能丢失写或脑裂，优先可用性；MySQL GR选择CP，分区时minority分区停止服务，优先一致性；Kafka选择AP（可配置），ISR可配置，acks=all时偏向CP。

集群设计的核心原则包括：理解你的SLA——不同的业务需求适合不同的方案，电商订单系统要求强一致性适合CP类方案，实时监控系统要求持续可用适合AP类方案，缓存系统要求极致性能可接受全量丢失适合Redis Cluster；失败是常态，设计要容错——集群设计应假设网络不可靠、节点会故障、时钟不同步、操作会重试，采用防御性编程包括超时设置避免无限等待、重试退避指数退避避免雪崩、熔断降级失败时保护系统、限流防止过载；监控和可观测性——通过INFO命令、性能模式、JMX等监控集群状态。

没有完美的集群方案，只有适合特定场景的权衡选择。理解各方案的一致性模型、故障处理机制和运维复杂度，才能在实际应用中做出正确的架构决策。

---

## 本章小结

集群架构是分布式系统的核心命题。通过对Redis、MySQL和Kafka三款软件的集群方案分析，我们看到了不同设计理念在实践中的体现：

Redis从简单的主从复制演进为分布式Cluster，在保持高性能的同时实现了水平扩展，AP的设计哲学使其成为缓存场景的首选。MySQL的复制技术从异步发展到Group Replication，InnoDB Cluster提供了完整的高可用解决方案，CP特性满足了数据强一致性的业务需求。Kafka的Partition+Replication设计天然适合分布式环境，ISR机制在保证可用性的同时提供了可配置的一致性级别。

三款软件虽然集群方案各异，但都体现了分布式系统设计的核心思想：**数据分片实现扩展、副本冗余保证可用、共识算法解决协调**。理解这些原理，将帮助我们在面对分布式系统设计的挑战时做出正确的选择。

在本书的后续章节，我们将继续探讨这些成熟软件的其他架构维度，从错误处理到可观测性，从配置管理到扩展机制，全面解析优秀软件的设计智慧。
