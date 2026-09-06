from pathlib import Path
import json, re, hashlib

BASE = Path('/Users/liu/dev/demos/redis-kafka-books/20260905gpt5.6重写版')
WORK = BASE / 'working/report-revision-20260905'
SOURCE = WORK / 'baseline'
drafts = []

def read_source(p):
    return (SOURCE / p.relative_to(BASE)).read_text()

def path(prefix):
    return next((BASE/'chapters').glob(prefix+'*/chapter.md'))

def section(prefix, number):
    p = path(prefix)
    t = read_source(p)
    depth = 2 if number.count('.') == 1 else 3
    m = re.search(r'^#{'+str(depth)+r'} '+re.escape(number)+r'\s.*?(?=^#{1,'+str(depth)+r'} |\Z)', t, re.M|re.S)
    assert m, (prefix, number)
    return p, m.group(0).rstrip()

def add(key, cards, p, old, new, note=''):
    t = read_source(p)
    assert old and t.count(old) == 1, (key, t.count(old))
    drafts.append(dict(id=key, cards=cards, path=str(p), old=old, new=new,
                       note=note, approval='C proposal; await A/B second vote'))

def para(prefix, number, starts):
    p, s = section(prefix, number)
    hits = [x for x in s.split('\n\n') if x.startswith(starts)]
    assert len(hits)==1, (prefix,number,starts)
    return p,hits[0]

p,o=para('01','1.4.1','起初按软件')
add('C-D01',['C01','语02'],p,o+'\n\n','')

# Move unique MVCC explanation, rather than deleting it as an alleged repetition.
p,o=section('01','1.2.2')
parts=o.split('\n\n')
mvcc='\n\n'.join(parts[3:7]).replace('第9章讨论副本旧值之前，会保留这项区别。','第9章讨论副本旧值时，还会用到这项区别。')
new='''### 1.2.2 MySQL：关系接口之下还有页、版本和提交过程

应用通过SQL描述查询和修改，通过事务规定哪些修改应一起生效。MySQL服务层负责连接、语句处理和执行计划，存储引擎承担具体的数据访问。本书讨论MySQL时，未特别说明的存储机制以默认引擎InnoDB为对象。binlog（二进制日志）属于服务层，redo log（重做日志）属于InnoDB，它们承担不同的记录职责。

InnoDB用页和B+树组织行记录，缓冲池（Buffer Pool）保存正在使用的页。查询可能涉及多次索引访问、行过滤或排序，SQL接口并不消除这些内部工作。第2章解释访问结构，第4章说明工作集、页写回与持久化条件。

MVCC（多版本并发控制，Multi-Version Concurrency Control）让普通一致性读依据读取视图选择可见版本，但不取消数据库中的锁。undo log（回滚日志）支持事务回滚与旧版本重建。同一次业务读到旧值，可能来自事务快照，也可能来自落后副本，不能仅凭外观判定原因。读取视图、undo维护成本和两种隔离级别的具体区别，见第4章4.3.7。

事务提供数据库内部的修改边界，持久化和副本切换仍需各自的条件。向另一个服务发送通知也未必属于同一个提交过程。第4章拆开这些恢复职责，第10章再把数据库之外的状态纳入完整设计。'''
add('C-D02',['C02','语03'],p,o,new,'Only execute with C-D03 migration; first definitions redo/undo retained at new main section; retain original citation metadata.')
p4,o4=section('04','4.3.6')
new4=o4+'\n\n### 4.3.7 读取视图与旧版本也会占用资源\n\n'+mvcc
add('C-D03',['C02','语03'],p4,o4,new4,'Exact source paragraphs from former1.2.2, including references. Must re-read moved existing prose, not just seams. Check first-definition redo/undo after migration.')

p,o=para('02','2.5','如果通过补一个索引')
new='''这里再作一组设定：现有业务数据已经在MySQL中，适用索引在目标负载下满足前一百名查询，分数修改还需要与业务状态一起提交。在这组条件下，先保留现库的索引访问；新增一份Redis排名会增加同步与重建责任，而现有索引已经满足这里设定的查询要求。

如果后续测量表明排名读取挤占了事务资源，并且业务允许明确的刷新延迟，派生排名才重新成为候选。此时要同时验证读取收益、增量更新成本和重建过程。开篇那次测试告诉我的首先是要检查实际访问过程；派生排名是否值得引入，还要由这些负载与一致性条件判断。'''
add('C-D04',['C04'],p,o,new)

p,o=para('02','2.2.6','表2-1保留')
add('C-D05',['C05','语04'],p,o,'表2-1与图2-7给出V2批头的关键字段和字节边界。第8章在这份布局基础上讨论批头依赖、校验与恢复。')
p,o=section('08','8.4.2'); ps=o.split('\n\n')
ps[1]='Kafka的V2记录批头与61字节固定部分见第2章表2-1和图2-7。进入文件读取与恢复时，重要的是哪些信息必须一起有效。每条记录除了批头的分摊成本，还包含自身长度、键值和头部等内容，不能把61除以消息数就当成全部存储成本。精确格式定义见[R8-12：Kafka 记录格式](https://kafka.apache.org/39/implementation/message-format/)。'
ps.pop(2)  # shared-header benefit is already explained in main chapter2
ps[2]='压缩可以在批范围内进行。相近结构的数据可能有更多可压缩的重复内容，已压缩或高随机性内容则可能收益很小。读取时需要处理相应解压范围，内存峰值也可能变化；选择压缩与批大小仍须结合第2章的凑批等待成本，在同一负载下比较压缩率、吞吐和尾延迟。'
add('C-D06',['C05','语04'],p,o,'\n\n'.join(ps),'Retain dependency, checksum scope, producer state, fig8-6 and official link.')

p,o=section('02','2.6.3')
new='''### 2.6.3 协议简单，应体现为责任明确

我自己设计新协议，会提前写出第二个版本要怎样出现。本章的Kafka版本协商提供一个具体例子：客户端确认某项API存在共同支持的版本后，按该版本编码请求；没有共同版本，就应识别为不兼容，而不是把一种新布局直接交给旧解析器。版本字段只有与这些行为相连，才形成兼容约定。

改变返回类型、增加可选字段和连接中断是不同问题。第8章会用新旧文件说明无法识别字段时的读取选择；连接中断后能否重试，则还取决于操作是否可能已经完成，不能由版本号决定。

协议易读有帮助，能够直接看见控制字段可以降低部分排障成本；二进制字段也能借助工具检查。客户端实现是否可靠，还取决于分包、错误、认证、超时和资源限制。'''
add('C-D07',['C06','语06'],p,o,new,'Use only existing2.3.3 negotiation semantics; no new protocol invented.')

p,o=para('03','3.3.2','一个重要边界是')
add('C-D08',['C07','语08'],p,o,o.replace('MySQL可以在部分回滚尚未完成时开放网络。',''))
p,o=section('03','3.4.2')
new='''### 3.4.2 网络资源准备与请求放行是不同状态

Kafka的接入、网络I/O和请求处理具有不同职责；第5章5.4.1完整说明Acceptor、Processor与RequestChannel的交接。生命周期管理关注这些职责何时能够接受工作，以及退出时尚未完成的工作如何处理。

监听资源已经建立，不表示认证和相关管理器已经满足请求的放行条件。先准备监听资源、暂缓处理依赖尚未就绪的请求，可以是合法顺序。图3-5表示这些条件关系，不规定所有版本和部署都具有同一套初始化调用次序。

![图 3-5 Kafka请求处理的放行与退出条件](diagrams/fig-3-5.svg)
图 3-5　资源准备、依赖就绪与请求放行是不同状态；退出还需要处理已经进入执行路径的请求。

停止接受新请求后，已有请求和响应仍可能占用队列、内存与连接。处理跟不上会形成请求积压，网络发送慢则会延长响应处理。正常退出需要协调这些工作与管理器、日志的停止；期限耗尽或进程异常终止时，未完成结果还要按恢复与重试协议处理。第5章解释运行期间的背压，第3.4.3节继续讨论Broker离开集群时的协调。'''
add('C-D09',['C08','语10'],p,o,new,'Requires fig3-5 redraw matching condition graph; not unverified fixed Kafka shutdown order.')

p,o=para('03','3.5.2','MySQL的清理与Kafka')
new=o+'''

可以用一个只说明预算计算的设定检查这件事：终止从时刻0开始，总宽限期为T，preStop在t1完成，在途请求处理到t2结束，且0≤t1≤t2≤T。下面把这几项工作假定为串行，便于看清已经消耗的时间；实际若有重叠，应按时间轴记录，不能把各阶段耗时直接相加。

| 检查时点 | 已消耗时间 | 距离总截止时间的余量 | 此时需要判定的事 |
|---|---|---|---|
| preStop开始 | 0 | T | 放行条件和停止新请求的动作是什么 |
| preStop结束 | t1 | T−t1 | 后续处理与持久化能否在剩余时间内完成 |
| 在途处理结束 | t2 | T−t2 | 清理和状态保存是否仍有足够时间 |
| 总期限到达 | T | 0 | 未完成结果走哪条恢复、查询或重试路径 |

这个设定没有给出适用于所有系统的退出时长，也不保证所有清理都会执行。它只排除一种预算错误：钩子已经使用的时间，不能在之后重新计算为可用时间。'''
add('C-D10',['C09'],p,o,new)

p,o=para('04','4.3.3','日志记录怎样')
add('C-D11',['C11'],p,o,o.replace('日志记录怎样表达页修改，第8章会说明。','页的布局和完整性保护见第8章。'))
p,o=para('05','5.3.4','Query Cache 被移除')
add('C-D12',['C13'],p,o,'Query Cache退出以后，数据依赖与失效问题仍然存在。应用缓存、代理缓存和物化结果也需要处理这些关系，只是把责任放到了其他地方。评价缓存位置时，仍需比较它能够取得的失效信息、维护成本与省下的执行工作。')

p,o=section('05','5.6.1')
new='''### 5.6.1 先判断要隔离的变化，再选择交接方式

Redis 的类型与编码说明，表示变化可以被限制在一组相关操作里；MySQL 的引擎接口说明，统一入口仍要表达能力差异；Kafka 的队列说明，执行速度不同可以通过有限积压协调。三个机制解决的问题不同，不能都缩成“增加一层”。

从查询与导出共用SQL拼接这一现象出发，可以区分两种情况。下面是假设分析，并非对当年具体实现的还原。

| 假定需要处理的变化 | 可先采用的安排 | 减少的风险 | 仍要承担的成本 |
|---|---|---|---|
| 查询与导出遵循同一套筛选规则，但导出会修改调用中共享的条件状态 | 保留共同筛选规则，导出使用独立构造的条件；不共享可变调用状态 | 导出修改条件时影响另一条查询路径 | 条件构造和公共规则仍须保持一致，不能靠复制整套查询代码长期分叉 |
| 查询与导出的字段、排序或资源要求已经不同 | 分开访问接口，明确各自输入与执行约束；仅复用确实相同的底层操作 | 一条路径改变SQL拼接或结果范围时牵动另一条路径 | 增加接口与部分重复代码，需要分别维护与验证 |

如果只是第一种情况，先隔离调用状态，比增加一个只转发参数的Service更直接；如果已经是第二种情况，强行维持同一访问入口反而会累积条件分支。两项选择都需要用实际调用关系验证。'''
add('C-D13',['C12'],p,o,new)

p,o=para('06','6.4.4','Kafka 客户端')
add('C-D14',['C15'],p,o,'第6.2.4—6.2.5节已经区分应用、节点间与控制面入口。传输保护须落实到实际使用的连接：一个入口配置TLS，不会自动保护其余连接；流量被称为“内部”，也不改变其中数据的敏感性。')
p,o=para('06','6.5.4','我更愿意')
new='''我更愿意从一次具体事件倒推审计需求。假设调查发现共享应用账号访问了一个不属于日常业务的表，下面只列三种证据状态，不把它们当成所有产品默认具备的日志能力。

| 实际留下的记录 | 可以进一步确认什么 | 仍不能由此确定什么 |
|---|---|---|
| 数据库侧记录了账号、访问对象、操作与时间 | 哪个应用账号在相应时间访问了哪些资源 | 共享该账号的哪个最终用户发起了请求 |
| 应用侧还记录了请求标识、认证用户及对应数据访问，且能可靠关联到这次操作 | 请求从哪个业务身份进入，并经过哪条访问路径 | 没有记录的中间步骤，不能仅凭时间接近补成事实 |
| 只剩应用总错误计数，相关访问记录未保留 | 记录周期内的错误总数 | 是否与本次访问有关，以及具体对象、请求和用户，均无法由总数确认 |

这会改变记录选择：为调查补上必要的账号、对象和关联信息，比无差别复制所有查询内容更直接。记录缺失时应保留未知范围；增加采集也要继续满足前面的字段遮蔽、权限与留存约定。'''
add('C-D15',['C16'],p,o,new)

p,o=para('07','7.4.4','生产者重试又')
add('C-D16',['C17'],p,o,'生产者重试与外部业务结果另有状态条件。第9章9.4.5区分消费位置与业务输出，第10章10.5把重复发布、目标库提交和消费进度放进同一次失败分析；`acks`不能代替这些协议。')

p=path('10-summary');t=read_source(p);o=t.split('\n\n')[2]
assert o.startswith('我曾在活动库存')
new='第7章的库存事故最终出现了超卖。后来改成以MySQL记录库存结果，Redis放在前面承担预处理。这是当时作出的调整；本章从它暴露的确认与恢复问题出发，继续检查事务之外的请求与状态。'
add('C-D17',['C18'],p,o,new,'Keep original factual later MySQL+Redis adjustment and oversell result; ch7 keeps complete fault narrative.')

p,o=para('08','8.6.2','一个可检查的方案')
new='''下面采用一个静态文件发布的设定：A是已经发布且可恢复的旧文件集合，B是正在生成的新集合，生成期间被发布的内容不再变化。这个限制只为了单独观察发布过程；存在并发增量时，还必须说明增量如何进入A或B以及在哪个时点切换，不能由此表直接推导增量安全。

| 阶段 | 已发布入口 | 额外文件 | 此时停止后的处理 | 尚不能做的事 |
|---|---|---|---|---|
| 生成前 | A | 无 | 按A恢复 | 删除A |
| 生成中 | A | 未完成的B | 仍按A恢复；识别未发布残留 | 让正式入口引用未完成的B |
| B完成但未发布 | A | 完整B | A仍是当前入口，B能否利用由恢复协议决定 | 因B存在就删除A |
| 发布B后 | B | 旧A | 校验入口与所需文件，再按规则清理旧集合 | 未满足发布持久化条件就认定A可清理 |
| 清理后 | B | 可能有清理残留 | 重复清理不改变B的有效性 | 把清理失败当成B失效 |

表中“发布B后”以入口及所需文件满足约定的持久化条件为前提。它列出的是一个设定方案的检查结果，不是Redis全部发布实现，也不证明任意文件系统上的崩溃安全。'''
add('C-D18',['C20'],p,o,new,'Keep following original paragraph on atomic rename versus data+directory durability.')

p,o=section('08','8.6.3');ps=o.split('\n\n')
old='\n\n'.join(ps[1:3])
new='''导读里的事故中，文件已经有版本号，仍然缺少新旧读写组合的约定。下面另设一个最小例子：旧程序A只认识格式v1；新程序B认识v1和v2；v2增加了一个理解记录所必需的字段。A能够识别格式版本并拒绝不支持的版本，B读取v1时按旧格式含义处理，不凭空推导新增字段的值。

| 写入者及格式 | 读取者 | 本例确定的行为 |
|---|---|---|
| A写v1 | A | 按已有v1规则读取 |
| A写v1 | B | 按v1规则读取，保留旧记录含义 |
| B写v2 | B | 校验并读取新增必需字段 |
| B写v2 | A | 识别为不支持的版本并拒绝，不跳过必需字段继续解释 |

如果部署要求随时回退到A，就不能在仍需回退期间无条件启用v2写入；若B保留写v1的能力，可以暂时继续写v1，或另外完成可验证的格式转换与回退方案。这里选择拒绝而不是忽略，是因为新增字段被设定为解释记录所必需。'''
add('C-D19',['C21'],p,old,new,'Keep all subsequent unknown-optional-field conditions and existing staged-upgrade/rollback/sample verification paragraphs.')

p,o=para('09','9.5.3','考察一条客户端')
new='''设定一条写入W已经向客户端返回成功，原写端P随后失联，候选Q仍可连接。业务要求重新开放后保留W，同时不能让两个写端继续产生不受协调的历史。这个共同问题需要同时检查历史与写端隔离，而不是只测试Q能否连接。

| 已有证据 | 仍缺少什么 | 本次判断 |
|---|---|---|
| 只知道Q可连接 | Q是否包含W，P是否仍可接收有效业务写入 | 不足以开放写入 |
| Q的有效历史可验证地包含W，但P的写入能力尚未隔离 | 旧写端隔离与本部署接替协议要求 | 不能仅凭历史完整就开放 |
| 已隔离P，但Q的历史不能证明包含W | 满足业务要求的历史来源或受控恢复结果 | 保持暂停并查找恢复依据 |
| 已隔离P，Q具有所需历史，并满足本部署的恢复与接替条件 | 应用重新放行所需的其他明确条件 | 可以据这些条件继续执行受控开放流程 |

表中的历史证据由具体协议提供。异步复制中的成功可能早于副本接收；带等待的复制还要检查是否超时降级，以及Q是否属于取得所需确认的范围。上一表列出的确认机制因此不是强弱标签，而是判断W保留在哪里的依据。'''
add('C-D20',['C23'],p,o,new,'Historical completeness alone never authorizes write reopening; retain following unknown response/idempotence paragraphs.')

p,o=para('09','9.3.4','`AFTER_SYNC`')
new='''`AFTER_SYNC`与`AFTER_COMMIT`改变源端等待的位置。下表只列正常半同步提交路径的相对顺序，所需副本确认沿用前段的relay log接收与刷盘条件。[R9-12：半同步等待点与可见性](https://dev.mysql.com/doc/refman/8.0/en/replication-semisync-interface.html)

| 等待点 | 正常提交路径中的相对顺序 | 与故障分析有关的区别 |
|---|---|---|
| AFTER_SYNC | 源端binlog同步 → 等待所需副本确认 → 存储引擎提交 | 引擎提交与其他会话可见发生在该等待之后 |
| AFTER_COMMIT | 源端binlog同步 → 存储引擎提交 → 等待所需副本确认 | 等待期间其他会话可能已看到结果，但副本尚未确认接收；特定故障切换路径下可能失去这些已见事务 |'''
add('C-D21',['C24'],p,o,new,'Replace original timing paragraph only; retain full preceding ACK and following phantom/selection/fallback/mode paragraphs plus fig9-5. Verify against R9-12.')

p,o=para('10-summary','10.8.1','同样，数据库')
new='数据库维护本例容易放在一个事务里的不变量，可延后传递的事件通过Kafka发送，Redis保存可以重新加载的展示数据。改变业务对象后，这些职责的分工也可能改变。'
add('C-D22',['C27'],p,o,new)

# Simple removals of duplicate illustrations; files remain as archived sources.
for key, prefix, fig, cards in [('C-D23','05','5-7',['C14']),('C-D24','08','8-1',['C19']),('C-D25','09','9-1',['C22','语19']),('C-D26','10-summary','10-1',['C25'])]:
    p=path(prefix);t=read_source(p)
    m=re.search(r'^!\[.*?\]\(diagrams/fig-'+re.escape(fig)+r'\.svg\)\n图 '+re.escape(fig)+r'.*?(?=\n\n|\Z)',t,re.M)
    assert m,fig
    add(key,cards,p,m.group(0)+'\n\n','','Merge any unique SVG semantics before removing embed; clear related prose xrefs; do not delete SVG file.')

cards=[]
for line in (WORK/'plan-C.md').read_text().splitlines():
    if re.match(r'\| C\d+ \|',line):
        fields=[x.strip() for x in line.strip('|').split('|')]
        cards.append(dict(id=fields[0],decision=fields[1],action=fields[2],teacher_overlap=fields[3]))
assert len(cards)==30
previous=json.loads((WORK/'plan-C.json').read_text()) if (WORK/'plan-C.json').exists() else None
if previous:
    pending={'C-D04','C-D05','C-D13','C-D15','C-D19','C-D21'}
    revisions={d['id']:d for d in drafts}
    drafts=[revisions[d['id']] if d['id'] in pending else d for d in previous['drafts']]
obj=dict(source_sha256=hashlib.sha256((SOURCE/'20260905gpt5.6版本.html').read_bytes()).hexdigest(),
         approval='independent C proposal; not executable until second vote',cards=cards,drafts=drafts,
         non_text_actions=['fig4-4 relational redraw','fig3-5 lifecycle condition redraw','citation+reference/edition layout decided jointly','epilogue/preface consolidation with A draft','remaining teacher exact corrections via A plan'])
(WORK/'plan-C.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'cards':len(cards),'drafts':len(drafts),'exact_old_unique':True,'path':str(WORK/'plan-C.json')},ensure_ascii=False))
