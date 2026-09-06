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
book=(root/'20260905gpt5.6版本.html').read_text()
source_figures=[];figure_errors=[];svg_without_internal_number=[]
for rel,_ in CHAPTERS:
    md=(root/rel).read_text()
    numbers=[]
    for alt,url in re.findall(r'!\[([^\]]*)\]\(([^)]+)\)',md):
        asset=(root/rel).parent/url
        number=re.search(r'图\s*(\d+-\d+)',alt)
        if not number or asset.stem!='fig-'+number[1]:
            figure_errors.append({'file':rel,'alt':alt,'asset':url});continue
        source_figures.append(asset.stem);numbers.append(int(number[1].split('-')[1]))
        svg=asset.read_text()
        internal_numbers=re.findall(r'图\s*(\d+-\d+)',svg)
        if not internal_numbers:svg_without_internal_number.append(str(asset.relative_to(root)))
        elif number[1] not in internal_numbers:figure_errors.append({'asset':url,'error':'SVG title number mismatch'})
    if numbers and numbers!=list(range(1,len(numbers)+1)):figure_errors.append({'file':rel,'error':'non-contiguous figure numbering','numbers':numbers})
html_figures=re.findall(r'<figure class="fig" id="([^"]+)"',book)
figure_match=Counter(source_figures)==Counter(html_figures)
active_svg_files={q.stem for q in (root/'chapters').glob('*/diagrams/*.svg')}
unused_svg_files=sorted(active_svg_files-set(source_figures))
reference_ids=set(re.findall(r'\*\*(R\d+-\d+)\*\*',refs))
citation_errors=[]
for rel,_ in CHAPTERS[1:11]:
    for label,dest in re.findall(r'\[([^\]]+)\]\(#ref-([^)]+)\)',(root/rel).read_text()):
        rid=re.match(r'R\d+-\d+',label)
        if not rid or rid[0] not in reference_ids or dest!=rid[0].lower():citation_errors.append({'file':rel,'label':label,'target':dest})
report={'unit_count':len(p.units),'units':results,'body_citations_absent_from_references':missing,'source_code_blocks':len(source_codes),'html_code_blocks':len(codes.blocks),'code_text_multiset_equal':code_match,'source_figure_count':len(source_figures),'html_figure_count':len(html_figures),'figure_set_equal':figure_match,'figure_number_errors':figure_errors,'unreferenced_active_svg_files':unused_svg_files,'citation_id_errors':citation_errors}
report['svg_without_internal_number']=svg_without_internal_number
(root/'qa/content-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False))
if len(p.units)!=len(CHAPTERS) or any(not r['exact_han_sequence'] for r in results) or missing or not code_match or not figure_match or figure_errors or unused_svg_files or citation_errors:raise SystemExit(1)
