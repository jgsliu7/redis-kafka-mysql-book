# 第四轮复核条目（20 项，供独立复核 Agent 使用）

版本基线：Redis 7.x、MySQL 8.0.x、Kafka 3.9（Tiered Storage 以 3.9+ 为准）。
章节文件根目录：/Users/liu/dev/demos/redis-kafka-books/chapters/

## Redis 项

**R1 · SipHash 版本**（02-data-structures-protocols/chapter.md:48）
现文："用 SipHash 做哈希函数（Redis 4.0 起为防哈希洪泛攻击，从 MurmurHash2 改用带随机种子的 SipHash）"。
指控：SipHash 是 5.0 才引入，"4.0 起"错误。

**R3 · channel 权限版本**（06-security/chapter.md:100）
现文："6.2 起，通道（channel）权限也独立出来，Pub/Sub 的订阅权限和键空间的读写权限分离"。
指控：channel 权限 6.0 引入 ACL 时就有，"6.2 起"错误。

**R4 · replication backlog 与 7.0 实现**（09-data-sync/chapter.md:70-76、07-cluster/chapter.md:59）
现文（ch9:72）："暂存进这条复制连接专属的输出缓冲区（不是 replication backlog——那是常驻的环形缓冲，职责是服务断线重连后的部分重同步）"。
指控：Redis 7.0 起部分重同步实现重构（PSYNC7），backlog 分配/共享方式有变，书的"环形缓冲"描述需补 7.0 实现细节（共享缓冲/repl-backlog-ttl）才准确。

**R11 · 命令表生成文件名**（05-layered-architecture/chapter.md:52）
现文："Redis 7.0 重构后，命令表改由 `commands/` 目录下的 JSON 描述文件自动生成到 `commands.c`"。
指控：生成的文件实际叫 `commands.def.h`，不是 `commands.c`。

**C4 · default 用户内置规则**（06-security/chapter.md:102）
现文："`7.x` 里 `default` 用户的内置规则仍是 `user default on nopass ~* &* +@all`"。
指控：与 `ACL LIST` 实际输出有出入（标志位表述瑕疵）。

**N2 · LFU 打满次数（图）**（04-memory-disk/diagrams/fig-4-2.svg 第 90 行）
现文："8 位可表达 0~255，默认参数下约 31 万次访问打满"。
指控：官方文档说约一百万次（around one million requests），31 万错误。

**N3 · LFU 数量级（正文）**（04-memory-disk/chapter.md:79）
现文："计数值随真实访问次数对数增长，所以 8 位能近似记到数十万级"。
指控：应为"百万级"。

**N5 · fork 延迟与 THP**（04-memory-disk/chapter.md:34 关键数字框、03-lifecycle/chapter.md:175）
现文（ch4:34）："fork 要拷贝页表，阻塞时间随实例内存线性上升，小实例几十毫秒，大实例（几十 GB 以上）可达数百毫秒，还受页表大小和是否开启透明大页（THP）影响"。
指控：数字区间应补 THP 开/关的具体影响（如 10–20ms/GB）。

**N6 · RESP 字节数**（02-data-structures-protocols/chapter.md:130）
现文："`SET key value` 变成 `*3\r\n$3\r\nSET\r\n$3\r\nkey\r\n$5\r\nvalue\r\n` 有三十多个字节"。
指控：精确 33 字节，"三十多个"不准确。

## MySQL 项

**M9 · 启动第二步主从语序**（03-lifecycle/chapter.md:87）
现文："加载系统表空间（ibdata 文件），拿到数据字典（MySQL 8.0 起数据字典已迁移到独立的 `mysql.ibd` 文件，undo log 也固定存放在独立的 undo 表空间，`ibdata1` 里剩下的主要是修改缓冲（change buffer）；5.7 及更早版本数据字典与默认存放的 undo log 都还在 `ibdata1` 中）"。
指控：主句"加载系统表空间，拿到数据字典"按 5.7 旧模型叙述、靠括注纠正，主从语序颠倒，应改为以 8.0 口径为主句。

**M12 · 权限检查内存缓存**（06-security/chapter.md:113）
现文："MySQL 的应对是把检查结果按'账号加库表'做内存缓存，权限用位图（bitmap）表示"。
指控：缓存机制实为"启动时把授权表载入内存的副本"（in-memory copies of the grant tables），"按账号加库表缓存检查结果"表述不准。

**M5 · TDE keyring 版本边界【已批准待补执行】**（06-security/chapter.md:143）
现文："TDE（Transparent Data Encryption，透明数据加密）在 InnoDB 表空间级别加密数据，密钥由密钥管理插件托管，常见的是对接 HashiCorp Vault 或云厂商 KMS。……"
待核实事实（用于拟一句边界说明）：表空间加密哪些版本/版次起社区版可用（5.7 是否企业版独占、8.0.16 起社区版是否可用）；社区版自带哪些 keyring 插件（keyring_file / keyring_okv / keyring_aws…）、企业版增加哪些（keyring_encrypted_file / 云厂商…）；binlog/redo log 加密的版本与版次归属。核实后给出一句话措辞建议（不超过 60 字，不改原段意思）。

## Kafka 项

**K2 · Tiered Storage GA 版本**（01-introduction/chapter.md:198、05-layered-architecture/chapter.md:186、08-storage-format/chapter.md:223、09-data-sync/chapter.md:214 四处）
现文口径："3.9 正式 GA"（ch5 另有"3.6 起以早期版本引入"）。
指控：GA 是 4.0，3.9 仍为 EA。

**K4 · KIP-106 引证**（09-data-sync/chapter.md:244）
现文："这个默认值自 0.11 起就由 true 改为 false，KIP-106，3.x 沿用并强化了这一取向"。
指控：unclean.leader.election.enable 默认值改 false 的提案编号/版本引证有误。

**K8 · TLS 与零拷贝**（06-security/chapter.md 6.5 节 131–149 行区间）
现文：Redis TLS 小节讲握手与吞吐代价（"单线程吞吐相比无加密约降至六到八成"）；Kafka 加密段讲多段 TLS。全书未出现"TLS 下零拷贝仍成立"类断言（可自行 grep 核实）。
指控：TLS 节应补"启用 TLS 后 sendfile 零拷贝失效（加解密回用户态）"一句，否则读者会误以为零拷贝在 TLS 下仍然成立。

**K13 · 日志段文件数**（05-layered-architecture/chapter.md:167、08-storage-format/chapter.md:166、图 8-6）
现文："每个 LogSegment 在磁盘上是三个文件：`.log`、`.index`、`.timeindex`"。
指控：事务型分区日志段还有 `.txnindex`（另有分区级 `.leader-epoch-checkpoint`），"三个文件"应改"主要三个文件"。

**C5 · kafka-acls 参数大小写**（06-security/chapter.md:125）
现文："`--resource-pattern-type prefixed --topic app-a.`"。
指控：官方文档示例用首字母大写 `Prefixed`，书中小写不对。

## 数字/量级项

**N8 · NVMe 延迟区间**（04-memory-disk/chapter.md:25 表格）
现文："SSD（随机读）~100μs（基准值；生产负载下 NVMe 典型在 100–500μs，受 I/O 深度与队列效应影响）"。
指控：设备级单笔 20–100μs 与生产端到端 100–500μs 两个口径混在同一格，应分注设备级区间。

**N9 · 单核十万级 QPS**（06-security/chapter.md:26、135）
现文："Redis 的内核追求极简和单核十万级 QPS（小包 GET/SET 场景）"（26 行）；"Redis 的设计目标是单核十万级 QPS"（135 行）。
指控：该数字无官方出处，应删或补来源口径。

**N10 · 进程内 vs 网络调用数量级**（05-layered-architecture/chapter.md:232）
现文："进程内调用的延迟是纳秒级，网络调用的延迟是毫秒级，差了六个数量级"。
指控：同机房网络往返典型 100μs–1ms（亚毫秒级），"毫秒级/六个数量级"夸大，应为"四到六个数量级"。
