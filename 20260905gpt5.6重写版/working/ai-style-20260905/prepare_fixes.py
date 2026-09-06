from pathlib import Path
import json
W=Path(__file__).resolve().parent; R=W.parents[1]; BASE=W/'baseline'
accepted=[]; skipped=[]
for source in ['cross-C.json','cross-A.json']:
 for r in json.loads((W/source).read_text()):
  x={'id':r['id'],'file':r['file'],'line':r['line'],'old':r['old'],'new':r.get('final',r.get('new')),'reason':r['reason'],'source':source}
  if r['vote']=='SKIP': skipped.append(x);continue
  x['votes']= ['A','C'] if r['id'].startswith('C') else (['A','B'] if r['id'].startswith('B') else (['A','C'] if r['vote']=='FIX' else ['B','C']))
  if x['id']=='A105':
   x['new']='数据库维护本例容易放在一个事务里的不变量，可延后传递的事件通过Kafka发送，Redis保存可以重新加载的展示数据。'; x['votes']=['A','B','C']
  s=(BASE/x['file']).read_text(); assert s.count(x['old'])==1,x
  x['start']=s.index(x['old']); x['end']=x['start']+len(x['old']); accepted.append(x)
groups=[]
for x in sorted(accepted,key=lambda v:(v['file'],v['start'],v['end'])):
 if groups and groups[-1][0]['file']==x['file'] and x['start']<max(y['end'] for y in groups[-1]):groups[-1].append(x)
 else:groups.append([x])
plan=[]
for group in groups:
 winner=max(group,key=lambda x:(len(x['old']),x['id'].startswith('C'),x['id'].startswith('B')))
 assert all(winner['start']<=r['start'] and winner['end']>=r['end'] for r in group),group
 x={k:v for k,v in winner.items() if k not in ['id','source']}; x['fix_id']=f'FIX{len(plan)+1:03}';x['candidate_ids']=[r['id'] for r in group];x['selected_candidate']=winner['id'];x['alternatives']=group
 x['old_paragraph']=(BASE/x['file']).read_text().splitlines()[x['line']-1]
 plan.append(x)
(W/'fix-plan.json').write_text(json.dumps({'fixes':plan,'skips':skipped,'candidate_count':len(accepted)+len(skipped),'accepted_candidate_count':len(accepted),'distinct_fix_count':len(plan)},ensure_ascii=False,indent=2)+'\n')
md=['# 本轮精确 FIX / SKIP 共识表','',f'原始候选 {len(accepted)+len(skipped)} 项；{len(accepted)} 项经交叉采纳，重叠合并为 {len(plan)} 个精确替换；{len(skipped)} 项保留原文。候选重叠只执行最终句一次，不重复计数。ADJUST 的精确终稿另经消息交叉确认；不能把初稿赞成票自动计为改写后赞成票。','']
for x in plan:
 md += [f"## {x['fix_id']} · {', '.join(x['candidate_ids'])}",f"位置：{x['file']}:{x['line']}；最终句票源：{' + '.join(x['votes'])}；选用候选：{x['selected_candidate']}。",f"- 原：{x['old']}",f"- 新：{x['new']}",f"- 理由：{x['reason']}",'']
md += ['# 保留原文','']
for x in skipped:md += [f"- {x['id']} · {x['file']}:{x['line']}：{x['reason']}"]
(W/'FIX-SKIP.md').write_text('\n'.join(md)+'\n')
print(json.dumps({'candidates':len(accepted)+len(skipped),'accepted':len(accepted),'distinct_fixes':len(plan),'skips':len(skipped)},ensure_ascii=False))
for x in plan:
 if len(x['candidate_ids'])>1:print(x['fix_id'],','.join(x['candidate_ids']),'SELECT',x['selected_candidate'],x['new'])
