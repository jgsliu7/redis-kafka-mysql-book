const fs=require('fs'),path=require('path');
const base='/Users/liu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/';
const {createCanvas}=require(base+'@napi-rs/canvas');
async function main(){
const pdfjs=await import(base+'pdfjs-dist/legacy/build/pdf.mjs');
const qa=path.resolve(__dirname,'../qa'),pdf=await pdfjs.getDocument({data:new Uint8Array(fs.readFileSync(path.join(qa,'print-proof.pdf'))),useSystemFonts:true}).promise;
const outside=[],sparse=[],samples=[];
for(let n=1;n<=pdf.numPages;n++){
 const p=await pdf.getPage(n),text=await p.getTextContent(),v=p.getViewport({scale:1});
 const words=text.items.filter(i=>i.str?.trim());
 for(const i of words){const x=i.transform[4],right=x+i.width;if(x<45||right>v.width-45)outside.push({page:n,text:i.str,x,right})}
 const all=words.map(i=>i.str).join('');if(all.length<60)sparse.push(n);
 if(n===1||all.includes('会话身份')&&all.includes('AUTH')||all.includes('UPDATEinventory')||n===pdf.numPages-1||n===31){
  const vp=p.getViewport({scale:1.5}),c=createCanvas(vp.width,vp.height);await p.render({canvasContext:c.getContext('2d'),viewport:vp}).promise;
  const filename='print-final-'+n+'.png';fs.writeFileSync(path.join(qa,filename),c.toBuffer('image/png'));samples.push(filename);
 }
}
const report={renderer:'PDF.js + @napi-rs/canvas',pages:pdf.numPages,textOutsideHorizontalMargins:outside,pagesWithUnder60TextCharacters:sparse,sampleImages:samples};fs.writeFileSync(path.join(qa,'print-audit.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}
main().catch(e=>{console.error(e);process.exit(1)});
