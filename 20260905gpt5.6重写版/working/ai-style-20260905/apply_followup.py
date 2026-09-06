from pathlib import Path
import json,datetime
W=Path(__file__).resolve().parent;R=W.parents[1]
items=[
('S01',1,'仍被读取视图需要的旧版本','读取视图仍然需要的旧版本',['A','C']),
('S02',2,'这样的设计交换十分具体','这里的设计取舍十分具体',['A','C']),
('S03',3,'不能说明目标系统是否足够','不能说明这段时间对目标系统是否足够',['A','C']),
('S04',4,'恢复依据不能缺席','不能缺少恢复依据',['A','C']),
('S05',4,'重建协议不能缺席','不能缺少重建协议',['A','C']),
('S06',5,'容易误导实现理解','容易使人误解实现',['A','C']),
('R069',7,'自动化的意义是按既定条件重复执行转移，并不能直接证明哪个副本具有所有刚刚确认的写入。','自动化可以按既定条件重复执行转移，但不能据此证明哪个副本具有所有刚刚确认的写入。',['B','C']),
]
records=[]
for ident,ch,old,new,votes in items:
 p=next((R/'chapters').glob(f'{ch:02d}-*/chapter.md'));s=p.read_text();assert s.count(old)==1,(ident,s.count(old));line=s[:s.index(old)].count('\n')+1
 records.append({'id':ident,'file':str(p.relative_to(R)),'line':line,'old':old,'new':new,'votes':votes,'old_paragraph':s.splitlines()[line-1]})
for r in records:
 p=R/r['file'];s=p.read_text();assert s.count(r['old'])==1;r['new_paragraph']=s.replace(r['old'],r['new'],1).splitlines()[r['line']-1];p.write_text(s.replace(r['old'],r['new'],1))
p=W/'followup-changes.json';existing=json.loads(p.read_text()) if p.exists() else []
existing.append({'at':datetime.datetime.now().astimezone().isoformat(),'stage':'postreview-1','changes':records})
p.write_text(json.dumps(existing,ensure_ascii=False,indent=2)+'\n')
with (W/'FIX-SKIP.md').open('a') as f:
 f.write('\n# 改后复审追加（初轮记录不覆盖）\n\n本批追加 7 次精确替换：6 处原存量语句修正，1 处为 FIX069 的改后衔接复修。累计 125 次操作，涉及 124 个不同位置。\n\n')
 for r in records:f.write(f"- {r['id']} · {r['file']}:{r['line']} · {'+'.join(r['votes'])} 两票：{r['old']} → {r['new']}\n")
print('Applied 7 followup replacements; initial log retained.')
