from pathlib import Path
import json,hashlib,datetime,difflib
W=Path(__file__).resolve().parent; R=W.parents[1]; BASE=W/'baseline'
plan=json.loads((W/'fix-plan.json').read_text()); groups={}
for x in plan['fixes']:groups.setdefault(x['file'],[]).append(x)
outputs={}; log=[]
# Validate every file and replacement before making the first edit.
for name, fixes in groups.items():
 p=R/name; before=p.read_text(); assert before==(BASE/name).read_text(),f'Source changed before apply: {name}'
 after=before
 for x in sorted(fixes,key=lambda q:q['start'],reverse=True):
  assert after[x['start']:x['end']]==x['old'],x['fix_id']
  after=after[:x['start']]+x['new']+after[x['end']:]
 outputs[name]=(before,after)
 for x in fixes:
  y=dict(x);y['new_paragraph']=after.splitlines()[x['line']-1];log.append(y)
for name,(before,after) in outputs.items():(R/name).write_text(after)
(W/'applied-changes.json').write_text(json.dumps({'at':datetime.datetime.now().astimezone().isoformat(),'distinct_replacements':len(log),'changed_files':len(outputs),'changes':log},ensure_ascii=False,indent=2)+'\n')
(W/'source-changes.diff').write_text(''.join(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='baseline/'+name,tofile='current/'+name,n=3)) for name,(before,after) in outputs.items()))
print(f'Applied {len(log)} exact replacements to {len(outputs)} files. No source outside approved spans changed.')
