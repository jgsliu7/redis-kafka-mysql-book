#!/usr/bin/env python3
from pathlib import Path
from collections import Counter
import re,json,sys
work=Path(__file__).resolve().parent
root=work.parents[1]
blacklist=json.loads((work/'blacklist-original.json').read_text())
source=root if len(sys.argv)<2 or sys.argv[1]=='current' else work/'baseline'
mode='current' if source==root else 'baseline'
files=sorted((source/'chapters').glob('*/chapter.md'))+sorted((source/'chapters').glob('0*.md'))
extra=[source/'chapters/10-epilogue.md',source/'chapters/11-references.md']
reports={}
for name,paths in [('original_11_units',files),('complete_13_units',files+extra)]:
 counter=Counter();hits=[]
 for p in paths:
  for i,line in enumerate(p.read_text().splitlines(),1):
   for word in blacklist:
    for m in re.finditer(word,line):
     counter[word]+=1;hits.append({'file':str(p.relative_to(source)),'line':i,'column':m.start()+1,'pattern':word,'match':m.group(),'text':line})
 reports[name]={'units':len(paths),'total_hits':sum(counter.values()),'word_kinds':len(counter),'counts':dict(counter.most_common()),'hits':hits}
(work/('lexical-'+mode+'.json')).write_text(json.dumps(reports,ensure_ascii=False,indent=2))
print(json.dumps({k:{a:b for a,b in v.items() if a!='hits'} for k,v in reports.items()},ensure_ascii=False))
