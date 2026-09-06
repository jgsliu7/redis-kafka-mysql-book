from html.parser import HTMLParser
from pathlib import Path
import sys

class Node:
    def __init__(self, tag, attrs=None):
        self.tag, self.attrs, self.children = tag, dict(attrs or []), []
    def text(self):
        return ''.join(c if isinstance(c,str) else c.text() for c in self.children)

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(); self.root=Node('root'); self.stack=[self.root]
    def handle_starttag(self,tag,attrs):
        n=Node(tag,attrs); self.stack[-1].children.append(n)
        if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}: self.stack.append(n)
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,0,-1):
            if self.stack[i].tag==tag: self.stack=self.stack[:i]; break
    def handle_data(self,data): self.stack[-1].children.append(data)

def walk(n):
    if isinstance(n,str): return
    yield n
    for c in n.children: yield from walk(c)

root=Path(__file__).resolve().parents[1]
p=Parser(); p.feed((root/'20260905gpt5.6版本.html').read_text())
sections=[n for n in walk(p.root) if n.tag=='section' and 'chapter' in n.attrs.get('class','').split()]
def blocks(n):
    for c in n.children:
        if isinstance(c,str): continue
        anchor=c.attrs.get('id','')
        if c.tag in {'h1','h2','h3','h4','p','pre','li','figcaption'}:
            yield f'[{c.tag} #{anchor}] '+c.text().strip()
        elif c.tag=='table':
            for row in walk(c):
                if row.tag=='tr': yield '[table] '+' | '.join(x.text().strip() for x in row.children if not isinstance(x,str) and x.tag in {'td','th'})
        elif c.tag=='svg':
            yield '[图中文字] '+' / '.join(x.text().strip() for x in walk(c) if x.tag=='text')
        else: yield from blocks(c)
if len(sys.argv)==1:
    for i,s in enumerate(sections):print(i,s.attrs.get('id'),len(list(blocks(s))))
else:
    s=sections[int(sys.argv[1])]; b=list(blocks(s)); a=int(sys.argv[2]) if len(sys.argv)>2 else 1; z=int(sys.argv[3]) if len(sys.argv)>3 else len(b)
    print('UNIT',s.attrs.get('id'),'BLOCKS',len(b))
    for i in range(a-1,min(z,len(b))):print(f'B{i+1:03} {b[i]}\n')
