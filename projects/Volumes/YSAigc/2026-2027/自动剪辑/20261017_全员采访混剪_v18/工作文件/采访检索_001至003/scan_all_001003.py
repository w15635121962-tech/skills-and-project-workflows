import json,concurrent.futures,shutil
from pathlib import Path
import av
from PIL import Image,ImageDraw
OUT=Path(__file__).parent;T=OUT/'全量缩略图';T.mkdir(exist_ok=True)
rows=[r for r in json.loads(Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_学校粗剪/工作文件/footage.json').read_text()) if r['group'] in ['001','002','003']]
def job(r):
 p=T/(r['key']+'.jpg')
 if p.exists():return str(p)
 old=Path(r.get('thumb',''))
 if old.is_file():shutil.copy2(old,p);return str(p)
 try:
  with av.open(r['path']) as c:
   s=c.streams.video[0];ts=min(r['duration']*.45,max(0,r['duration']-1));c.seek(int(ts/float(s.time_base)),stream=s,backward=True)
   for f in c.decode(s):
    if f.time>=ts:
     im=f.to_image();im.thumbnail((480,270));im.save(p,quality=86);return str(p)
 except Exception as e:return repr(e)
 return None
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for r,res in zip(rows,ex.map(job,rows)):
  r['scan_thumb']=res
(OUT/'full_scan_manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
for g in ['001','002','003']:
 rr=[r for r in rows if r['group']==g]
 for offset in range(0,len(rr),36):
  subset=rr[offset:offset+36];sheet=Image.new('RGB',(1500,1056),'#111111');d=ImageDraw.Draw(sheet)
  for i,r in enumerate(subset):
   x=(i%6)*250;y=(i//6)*176
   p=Path(r['scan_thumb'] or '')
   if p.is_file():
    im=Image.open(p).convert('RGB');im.thumbnail((248,140));sheet.paste(im,(x,y))
   d.text((x+2,y+141),r['name'][:32],fill='white');d.text((x+2,y+157),f"{r['duration']:.1f}s",fill='#cccccc')
  sheet.save(OUT/f'全量_{g}_{offset//36+1:02d}.jpg',quality=92)
print('DONE',len(rows),flush=True)
