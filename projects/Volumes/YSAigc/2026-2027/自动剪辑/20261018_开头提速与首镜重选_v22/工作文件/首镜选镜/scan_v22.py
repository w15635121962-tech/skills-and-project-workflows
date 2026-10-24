import av,json,re,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parent
D=json.load(open('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_学校粗剪/工作文件/footage.json'))
F=ImageFont.load_default(size=15)
def no(x):
 m=re.search('C(\\d+)',x['name']);return int(m[1]) if m else -1
A=[x for x in D if x['group']=='001' or (x['group']=='004' and no(x)>=280) or (x['group']=='006' and 170<no(x)<320 and no(x)%6==0)]
def thumb(x):
 q=ROOT/'thumbs'/f"{x['group']}_{x['name']}.jpg";q.parent.mkdir(exist_ok=True)
 if not q.exists():
  with av.open(x['path']) as c:
   st=c.streams.video[0];ts=min(x['duration']*.4,x['duration']-0.1);c.seek(int(ts/st.time_base),stream=st)
   for f in c.decode(st):
    if float(f.time)>=ts:
     im=f.to_image();im.thumbnail((320,180));im.save(q);break
 return x,q
for idx in range(0,len(A),24):
 batch=A[idx:idx+24];ims=ThreadPoolExecutor(4).map(thumb,batch);out=Image.new('RGB',(1280,6*214),(12,16,20));dr=ImageDraw.Draw(out)
 for j,(x,p) in enumerate(ims):
  xx=(j%4)*320;yy=(j//4)*214
  if p.exists():out.paste(Image.open(p),(xx,yy))
  dr.text((xx+4,yy+181),x['group']+'_'+x['name'].replace('_Proxy.mov','').replace('_Proxy.mp4',''),font=F,fill='white');dr.text((xx+4,yy+198),str(round(x['duration'],1))+f" {x['fps']}fps",font=F,fill='yellow')
 q=ROOT/f'overview_{idx//24+1:02}.jpg';out.save(q);print(q,flush=True)
json.dump(A,open(ROOT/'scan_manifest_v22.json','w'),ensure_ascii=False,indent=2)
