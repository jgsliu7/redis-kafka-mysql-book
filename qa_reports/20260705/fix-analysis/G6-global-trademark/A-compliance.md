# 出版合规审查报告：商标声明缺失（G6）

## 审查范围

全书（重点检查：chapters/00-preface.md, chapters/10-epilogue.md, chapters/11-references.md）

## 审查结论：🔴 合规底线缺失

### 问题定位

全书 **零处** 使用注册商标符号（®/™），**零处** 商标归属声明。Redis、MySQL、Kafka、InnoDB、ZooKeeper 等注册商标/商标在正文中反复出现（Redis 744 次、Kafka 703 次、MySQL 620 次、InnoDB 105 次、ZooKeeper 33 次），但无一处置符号或归属声明。这是 P0 合规底线缺失。

根据各商标权利人政策：
- **Redis Ltd.**：首次使用须加 ® 并附归属声明
- **Oracle Corporation**（MySQL、InnoDB）：须附商标归属声明
- **Apache Software Foundation**（Kafka、ZooKeeper）：Kafka ®、ZooKeeper ™，须附归属声明

### 建议插入位置

**首选位置**：chapters/00-preface.md 第 34 行，即 AI 披露段落末行之后、"是为序。"之前。

原因：序言是全书最前置的法律声明承载页，与 AI 披露段落相邻形成"法律/合规声明块"，符合图书出版惯例。许多技术图书将商标声明置于序言或扉页背面。

**备选补充位置**：chapters/10-epilogue.md 第 55 行之后（"版权与勘误"节末尾），作为再次声明。

建议两处同时声明：序言供读者初次阅读时知晓，后记"版权与勘误"节供法律合规存档用。

### 需要声明的商标清单

| 商标 | 权利人 | 符号 | 全书出现次数 |
|------|--------|------|------------|
| Redis | Redis Ltd. | ® | 744 |
| MySQL | Oracle Corporation | ® | 620 |
| Kafka | Apache Software Foundation | ® | 703 |
| InnoDB | Oracle Corporation | ® | 105 |
| ZooKeeper | Apache Software Foundation | ™ | 33 |

### 建议插入的商标声明文本

#### (A) 序言插入文本（chapters/00-preface.md）

在"关于本书的创作过程"段落末尾（第 33 行 "并独立承担文责。" 之后），插入以下段落：

```
本书提及的商标与产品名称均属其各自所有者。Redis® 是 Redis Ltd. 的注册商标。MySQL® 与 InnoDB® 是 Oracle Corporation 及其附属公司的注册商标。Apache Kafka® 与 Apache ZooKeeper™ 是 Apache 软件基金会（Apache Software Foundation）在美国及/或其他国家的注册商标或商标。
```

#### (B) 后记"版权与勘误"插入文本（chapters/10-epilogue.md）

在第 55 行末尾（"以 Redis、MySQL、Kafka 官方文档为准。" 之后），插入以下段落：

```
商标声明：Redis® 是 Redis Ltd. 的注册商标。MySQL® 与 InnoDB® 是 Oracle Corporation 及其附属公司的注册商标。Apache Kafka® 与 Apache ZooKeeper™ 是 Apache 软件基金会在美国及/或其他国家的注册商标或商标。本书提及的其他所有商标与产品名称均属其各自所有者。
```

### 精确的替换/插入方案

#### 文件：chapters/00-preface.md

当前内容（第 31-35 行）：
```
## 关于本书的创作过程

本书写作借助生成式 AI 工具（Claude、GPT 系列）辅助资料查证、文字润色与 SVG 插图绘制。全书的论点框架、技术判断、案例选择与文字审定由作者主导，并独立承担文责。

是为序。
```

建议改为：
```
## 关于本书的创作过程

本书写作借助生成式 AI 工具（Claude、GPT 系列）辅助资料查证、文字润色与 SVG 插图绘制。全书的论点框架、技术判断、案例选择与文字审定由作者主导，并独立承担文责。

本书提及的商标与产品名称均属其各自所有者。Redis® 是 Redis Ltd. 的注册商标。MySQL® 与 InnoDB® 是 Oracle Corporation 及其附属公司的注册商标。Apache Kafka® 与 Apache ZooKeeper™ 是 Apache 软件基金会（Apache Software Foundation）在美国及/或其他国家的注册商标或商标。

是为序。
```

new_string（从第 33 行"并独立承担文责。"后替换到"是为序。"前）：
```
并独立承担文责。

本书提及的商标与产品名称均属其各自所有者。Redis® 是 Redis Ltd. 的注册商标。MySQL® 与 InnoDB® 是 Oracle Corporation 及其附属公司的注册商标。Apache Kafka® 与 Apache ZooKeeper™ 是 Apache 软件基金会（Apache Software Foundation）在美国及/或其他国家的注册商标或商标。

是为序。
```

#### 文件：chapters/10-epilogue.md

当前内容（第 55 行末尾）：
```
本书勘误与版本更新见 https://gitee.com/flainliu/redis-kafka-books，欢迎读者反馈；技术细节随版本演进，采纳前请以 Redis、MySQL、Kafka 官方文档为准。
```

建议在末尾另起一段追加：
```
本书勘误与版本更新见 https://gitee.com/flainliu/redis-kafka-books，欢迎读者反馈；技术细节随版本演进，采纳前请以 Redis、MySQL、Kafka 官方文档为准。

> 商标声明：Redis® 是 Redis Ltd. 的注册商标。MySQL® 与 InnoDB® 是 Oracle Corporation 及其附属公司的注册商标。Apache Kafka® 与 Apache ZooKeeper™ 是 Apache 软件基金会在美国及/或其他国家的注册商标或商标。本书提及的其他所有商标与产品名称均属其各自所有者。
```

## 合规要点说明

1. **序言前置声明**：在读者进入正文前完成法律声明，符合中国出版业的通行做法。
2. **后记补充声明**：在"版权与勘误"节中作为法律合规存档，形成双重保险。
3. **权利主体准确**：Redis Ltd.（非 Redis Labs）、Oracle Corporation（非 Sun）、Apache Software Foundation——均已核实当前最新状态。
4. **符号准确性**：Redis®（USPTO 注册）、MySQL®（Oracle 注册）、Kafka®（ASF 注册）、InnoDB®（Oracle 注册）、ZooKeeper™（ASF 未注册但具有普通法商标权）——均已核实。
5. **中文表述**：采用"是……的注册商标"标准句式，符合中国法律文书用语习惯。
6. **覆盖全面**：除五大核心商标外，声明末尾以"其他所有商标与产品名称均属其各自所有者"兜底，覆盖全书中可能出现的其他商标（如 RocksDB™、LevelDB™ 等 Google 商标、S3™ 等 AWS 商标）。
7. **不涉及许可冲突**：仅做事实性商标归属声明（nominative fair use），不暗示背书或赞助，无需取得各权利人授权。

## 来源

- Redis Trademark Policy: https://redis.io/legal/trademark-policy/
- MySQL Logo Usage Guidelines: https://www.mysql.com/fr/about/legal/trademark.html
- Apache Trademark FAQ: https://apache.org/foundation/marks/faq/index.html
- Oracle Third Party Usage Guidelines: https://www.oracle.com/legal/logos.html
