# 终审主修复清单(投稿前最后一轮)

> 基于 15 个只读审查 agent(ai-writing-detector×4 / typo-grammar / term-consistency / crossref-validity / svg-semantics×2 / fact-consistency / command-runnable / number-provenance / structure-pedagogy / tech-editor / compliance)+ svg_audit.py + playwright 视觉核验。本文件是审计留痕与分区依据。

## 一、🔴 必改硬伤(技术正确性,低风险高收益)

| # | 位置 | 问题 | 改法 |
|---|------|------|------|
| H1 | `chapters/04-memory-disk/diagrams/fig-4-1.svg:104` | 结论框"约 1,000 万倍(10⁷)"算错,与正文 ch4:39"十万倍"矛盾(视觉已确认醒目) | →"约十万倍(10⁵)" |
| H2 | `fig-4-1.svg:11` 副标题 | "6～7 个数量级"(内存DRAM100ns→机械盘10ms=5个数量级) | →"5 个数量级" |
| H3 | `chapters/02-.../diagrams/fig-2-1.svg:22` | 图写"MurmurHash2",但 Redis 4.0 起用 SipHash(正文 ch2:35) | →"SipHash(防 hash 洪泛)" |
| H4 | `ch7` 5 处 | CAP 归类同章自相矛盾:导读:7、7.2.3开头:84、acks段:164、启示段:195/206/222/224 写"Redis 偏 AP / MySQL 默认偏 CP"无 nuance,与同章 nuance 段(86/190/232)及 ch9:143/ch10:100 打架 | 全部对齐"Redis 归类有争议不作一刀切;MySQL 默认复制形态偏 AP、产品定位偏 CP"。详见 ch7 agent |
| H5 | `ch5:184` | Kafka 刷盘参数名错 `flush.messages`/`flush.ms`(不存在,与 ch4 矛盾) | →`log.flush.interval.messages`/`log.flush.interval.ms` |
| H6 | `ch10:98` | "MySQL 5.7.7+ 默认 sync_binlog=1"误述(5.7/8.0 默认都是 0;双1是手动配置) | 改为"默认偏向持久性(innodb_flush_log_at_trx_commit=1),再开 sync_binlog=1 即双1" |
| H7 | `ch10:129` | 中文句夹裸英文动词 "trade" | →"取舍"(或"权衡") |
| H8 | `ch6:167` | 无编号游离子标题"### 各产品安全设计取舍" | →"### 6.4.4 三款软件的加密取舍"(或就地并入各家) |
| H9 | `ch6/outline.md:81` | `ldap_simple` 残留(正文已改) | →`authentication_ldap_simple` |
| H10 | `references:57` | KIP-101/320 缺年份+混编两条+URL单一 | 拆两条、补(2015)、补 KIP-320 URL |
| H11 | `references:76` | NetDB [C] 缺会议地点 | 补"Stockholm," |

## 二、🟡 术语统一(全书 find-replace,已定标)

| 术语 | 现状 | 统一为 |
|------|------|--------|
| PageCache/页缓存/page cache(51) | 三写法,基线声称统一实回退 | **PageCache**;ch1:97 首现注"页缓存(PageCache)" |
| 双写缓冲/双写区/双写(32) | 三叫法 | **双写缓冲**;首现"双写缓冲(doublewrite buffer)" |
| leader/Leader | 协议字段名(leader epoch/unclean.leader.election)保留小写;角色名词→**Leader** | ch4:214、ch9:213、ch10:31/152 |
| partition/Partition | "分区"中文为主(134次),保留 | 仅修首现注大小写"分区(Partition)"、标题 Partition |
| Topic/topic(9) | 大小写混 | →**Topic**(专名,匹配 Broker/Leader) |
| relay log(14)/中继日志(3) | 英文过多 | 首现后 →**中继日志** |
| group commit | ch10:59 英文 | →**组提交** |
| Change Buffer/change buffer/修改缓冲 | 混 | 首现"修改缓冲(Change Buffer)",后用**修改缓冲** |
| I/O vs IO(56) | 不统一 | **I/O**(Phase4 全局脚本统一,agent 不碰) |
| 数字+拉丁单位空格 | 16KB vs 16 KB 混 | **无空格**(16KB/10ms/100ns);Phase4 全局脚本,agent 不碰 |

缩写首现补全称:RTT(ch2:89)、RTO(ch10:152)、RPO(ch10:67)、ZK(ch3:140)、PSYNC/PSYNC2(ch10:169)。

## 三、🎯 AI 味去味(用户核心目标)——按章分区见各 agent

优先级 P0 单点:ch5:305(拔高+三连+价值收口三件套)、ch8:254/266(机械三连,验收点名)、ch10:10.3.1(五维度模板)、各章收口"不是A而是B+升华"金句群(epilogue L45/L9/L21、ch9:343、references:80)。

6 类新病理(全 agent 识别并修):①PPT横比收口句 ②节首悬空判断前置 ③价值标签括注 ④三栏镜像排比 ⑤金句对仗尾+TED升华 ⑥反向否定三连。

## 四、📐 SVG 视觉核验结论

- fig-4-1:**必改**(H1/H2,视觉确认)
- fig-2-1:**必改**(H3)
- fig-6-2:**不改**(svg_audit [high] 误报,视觉确认清晰)
- fig-1-3:**可选**(仅"低延迟"顶点雷达线轻压,可接受)
- fig-7-2:迁移示例槽号不严谨(中,可选)
- 其余 47 张:语义+数值全对(svg-semantics 双 agent 交叉确认)

## 五、✅ 已达标(不再动)

交叉引用 0 硬伤(crossref);文字三校仅 1 硬错(H7);命令/参数可运行性 0 硬伤(command-runnable,约50项核验正确);三家/broker/checkpoint/分区vs分片/脏页刷盘 术语达标;致谢/版权/勘误/商标声明段齐备(compliance)。

## 六、分区(8 agent,每 agent 独占文件,零冲突)

| Agent | 文件(独占) | 重点 |
|-------|-----------|------|
| 1 | 00-preface + 01-introduction | 序言AI味+五骨架释义;ch1完全不同×3/横比套句/三家对仗/表后复述/小结;商标首现®;ch1:41裸数字;page cache→PageCache |
| 2 | 02 + 03 | ch2:126映射/启示比喻/压动词/RTT首现/fig-2-1/小结;ch3履约守数据清责/三栏镜像/undo-redo首现铺垫/ZK首现/句号断句/outline ldap |
| 3 | 04 + 06 | ch4三栏镜像/数据以X为家/fig-4-1/双写缓冲/小结/N.6首句;ch6无编号子标题/小结/数字软化/TLS降幅/Topic/修改缓冲 |
| 4 | 05 | ch5:305 P0/看三件事×6/不是而是/换来的解耦/三栏镜像;flush参数名;副本同步铺垫;N.6首句 |
| 5 | 07 | **CAP 5处nuance对齐(H4)**;三栏+完全不同/7.5同构/看似其实;relay→中继日志;N.6首句 |
| 6 | 08 | ch8:254/266 P0机械三连/范式模板+密度/反向否定三连/小结自复述;RDB前提;双写缓冲;N.6首句 |
| 7 | 09 + 10-epilogue | ch9不是而是/段末收口;leader/Leader;epilogue致谢套话/不是而是/三家排比/双1 |
| 8 | 10-summary + 11-references | ch10 10.3.1五维度模板/判据×2/规律核心思想×3/拿到你×4/sync_binlog(H6)/trade(H7);references:80/著录(H10/H11) |

## 七、⚠️ 故意不做(最后一轮,避免引入新风险)

- 章节重排/打破八段式/加中场休息(tech-editor 宏观建议——结构性大改风险>收益,且与"终审抛光"相悖)
- 图序重编号(历史已暂缓,破坏风险高)
- 跨章移动内容 ch4↔ch8(仅 ch4 加"详见8.2.4"指针,不搬)
- 小结整段重写(仅"补一句新判断",不推倒重来)
- AI 披露(preface:31)——**留待用户决策**(见终审报告)

## 八、AI 披露决策(待用户)

preface:31 现明确披露"多数章节初稿由 AI 辅助生成(Claude/GPT)"。用户目标是"不被发现是 AI"。这是核心分叉,不自动改,终审报告单独提交。
