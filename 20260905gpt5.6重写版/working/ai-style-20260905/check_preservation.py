#!/usr/bin/env python3
"""Compare this expression-only edit with its immutable snapshot; no semantic claim."""
from pathlib import Path
import hashlib,json,re,subprocess
W=Path(__file__).resolve().parent
ROOT=W.parents[1]
BASE=W/'baseline'
sha=lambda data:hashlib.sha256(data).hexdigest()
jhash=lambda value:sha(json.dumps(value,ensure_ascii=False,separators=(',',':')).encode())
manifest=json.loads((BASE/'manifest.json').read_text())
rows=[]
for name, before in manifest['files'].items():
 p=ROOT/name
 if p.suffix!='.md':continue
 s=p.read_text(); old=(BASE/name).read_text()
 current={
 'code_sha256':jhash(re.findall(r'^```[^\n]*\n.*?^```[^\n]*$',s,re.M|re.S)),
 'numbers_sha256':jhash(re.findall(r'\d+(?:\.\d+)*',s)),
 'urls_sha256':jhash(re.findall(r'\]\(([^)]+)\)',s)),
 'inline_code_sha256':jhash(re.findall(r'`([^`\n]+)`',s)),
 }
 rows.append({'file':name,'source_changed':sha(p.read_bytes())!=before['sha256'], 'checks':{k:current[k]==before[k] for k in current}, 'before_han':len(re.findall(r'[\u4e00-\u9fff]',old)), 'after_han':len(re.findall(r'[\u4e00-\u9fff]',s))})
svg={n:sha((ROOT/n).read_bytes())==v for n,v in manifest['svg'].items()}
scripts={n:sha((ROOT/n).read_bytes())==v for n,v in manifest['scripts'].items()}
tracked=hashlib.sha256()
repo=ROOT.parent
for raw in sorted(subprocess.check_output(['git','ls-files','-z'],cwd=repo).split(b'\0')):
 if not raw:continue
 p=repo/raw.decode()
 if p.is_file():tracked.update(raw+b'\0'+p.read_bytes()+b'\0')
html=next(ROOT.glob('20260905gpt5.6版本.html')).read_text(); oldhtml=(BASE/'20260905gpt5.6版本.html').read_text()
style_equal=re.findall(r'<style[^>]*>(.*?)</style>',html,re.S)==re.findall(r'<style[^>]*>(.*?)</style>',oldhtml,re.S)
report={'scope':'Expression-edit preservation only; hashes do not prove semantic equivalence','units':len(rows),'files':rows,'svg_count':len(svg),'svg_unchanged':all(svg.values()),'changed_svg':[k for k,v in svg.items() if not v],'existing_scripts_unchanged':all(scripts.values()),'styles_unchanged':style_equal,'original_tracked_unchanged':tracked.hexdigest()==manifest['tracked_files_aggregate_sha256'],'original_tracked_current':tracked.hexdigest()}
report['passed']=all(all(r['checks'].values()) for r in rows) and all(svg.values()) and all(scripts.values()) and style_equal and report['original_tracked_unchanged']
(W/'preservation-current.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='files'},ensure_ascii=False,indent=2))
for r in rows:
 if not all(r['checks'].values()): print('CHANGED SENTINEL',r['file'],r['checks'])
raise SystemExit(0 if report['passed'] else 1)
