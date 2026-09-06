#!/usr/bin/env python3
"""校验Markdown→HTML汉字序列及源引用对应；不代替技术或语言通读。"""
from pathlib import Path
from html.parser import HTMLParser
import re,json,sys
from collections import Counter
sys.dont_write_bytecode=True
from build_book import CHAPTERS
root=Path(__file__).resolve().parents[1]
class Extract(HTMLParser):
    def __init__(self):super().__init__();self.units=[];self.active=False;self.svg=0
    def handle_starttag(self,tag,attrs):
        if tag=='section' and dict(attrs).get('class')=='chapter':self.units.append('');self.active=True
        if tag=='svg':self.svg+=1
    def handle_endtag(self,tag):
        if tag=='svg':self.svg-=1
        if tag=='section':self.active=False
    def handle_data(self,data):
        if self.active and not self.svg:self.units[-1]+=data
def han(s):return ''.join(re.findall('[\u4e00-\u9fff]',s))
p=Extract();p.feed((root/'20260905gpt5.6版本.html').read_text())
results=[]
for (rel,_),actual in zip(CHAPTERS,p.units):
    md=(root/rel).read_text()
    md=re.sub(r'^!\[[^\]]*\]\([^)]+\)\s*$', '',md,flags=re.M)
    md=re.sub(r'\[([^\]]+)\]\([^)]+\)',r'\1',md)
    expected=han(md);actual=han(actual)
    match=expected==actual
    item={'file':rel,'han_expected':len(expected),'han_html':len(actual),'exact_han_sequence':match}
    if not match:
        at=next((i for i,(a,b) in enumerate(zip(expected,actual)) if a!=b),min(len(expected),len(actual)))
        item['first_difference']={'at':at,'expected':expected[max(0,at-30):at+80],'actual':actual[max(0,at-30):at+80]}
    results.append(item)
refs=(root/'chapters/11-references.md').read_text()
reference_urls=set(re.findall(r'\]\((https?://[^)]+)\)',refs));missing=[]
for rel,_ in CHAPTERS[1:11]:
    for label,url in re.findall(r'\[([^\]]+)\]\((https?://[^)]+)\)',(root/rel).read_text()):
        if url not in reference_urls:missing.append({'file':rel,'label':label,'url':url})
class CodeExtract(HTMLParser):
    def __init__(self):super().__init__();self.blocks=[];self.active=False
    def handle_starttag(self,tag,attrs):
        if tag=='pre':self.blocks.append('');self.active=True
    def handle_endtag(self,tag):
        if tag=='pre':self.active=False
    def handle_data(self,data):
        if self.active:self.blocks[-1]+=data
codes=CodeExtract();codes.feed((root/'20260905gpt5.6版本.html').read_text())
source_codes=[]
for rel,_ in CHAPTERS:
    source_codes+=re.findall(r'^```[^\n]*\n(.*?)^```\s*$',(root/rel).read_text(),flags=re.M|re.S)
code_match=Counter(s.rstrip('\n') for s in source_codes)==Counter(s.rstrip('\n') for s in codes.blocks)
report={'unit_count':len(p.units),'units':results,'body_citations_absent_from_references':missing,'source_code_blocks':len(source_codes),'html_code_blocks':len(codes.blocks),'code_text_multiset_equal':code_match}
(root/'qa/content-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False))
if len(p.units)!=13 or any(not r['exact_han_sequence'] for r in results) or missing or not code_match:raise SystemExit(1)
