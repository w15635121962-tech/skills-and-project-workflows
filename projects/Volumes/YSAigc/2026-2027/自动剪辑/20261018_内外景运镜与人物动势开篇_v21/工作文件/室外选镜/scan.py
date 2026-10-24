import av,json,re,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parent
D=json.load(open('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_学校粗剪/工作文件/footage.json'))
S=json.load(open('/Volumes/YSAigc/2026-2027/自动剪辑/20261018_开篇三素材与强配乐_v20/工作文件/final_native_snapshot_v20.json'))
used={i['path'] for t in S['video'] for i in t['items'] if i.get('enabled',True)}
def no(x):
 m=re.search('C(\d+)',x['name']);return int(m[1]) if m else -1
A=[x for x in D if x['group']=='002' or (x['group']=='004' and no(x)<=85) or (x['group']=='006' and (150<=no(x)<=170 or no(x)>=320)) or (x['group']=='007' and (no(x)<=22 or 115<=no(x)<=140))]
F=ImageFont.load_default(size=15)
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
  dr.text((xx+4,yy+181),x['group']+'_'+x['name'].replace('_Proxy.mov',''),font=F,fill='white');dr.text((xx+4,yy+198),str(round(x['duration'],1))+(' USED' if x['path'] in used else ' NEW'),font=F,fill='yellow')
 q=ROOT/f'overview_{idx//24+1:02}.jpg';out.save(q);print(q,flush=True)
json.dump(A,open(ROOT/'scan_manifest.json','w'),ensure_ascii=False,indent=2)
