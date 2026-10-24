from pathlib import Path
import json,concurrent.futures
import av
from PIL import Image,ImageDraw,ImageFont
R=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_片尾第三轨大方选镜_v17/工作文件/片尾选镜');rows=json.loads((R/'unused_candidates_metadata_v17.json').read_text());rows=[x for x in rows if x['duration']>=2.4]
def process(x):
 p=Path(x['path']);dest=R/'抽帧'/x['group']/p.stem;dest.mkdir(parents=True,exist_ok=True);samples=[]
 times=[round((.12+.19*i)*x['duration']*25)/25 for i in range(5)]
 with av.open(str(p)) as c:
  s=c.streams.video[0];s.thread_type='AUTO'
  for i,t in enumerate(times):
   c.seek(int(t/s.time_base),stream=s,backward=True,any_frame=False)
   for f in c.decode(s):
    if f.time is not None and f.time>=t-.02:
     path=dest/f'{i}_{t:.2f}s.jpg';f.to_image().convert('RGB').resize((640,360),Image.Resampling.LANCZOS).save(path,quality=94);samples.append({'time':f.time,'path':str(path)});break
 x['samples']=samples;return x
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as e: rows=list(e.map(process,rows))
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',22)
for page,k in enumerate(range(0,len(rows),5),1):
 batch=rows[k:k+5];im=Image.new('RGB',(1920,len(batch)*266),(15,24,27));d=ImageDraw.Draw(im)
 for row,x in enumerate(batch):
  y=row*266;used='未使用' if not x['used_intervals'] else '已用 '+str([(a['record_start'],a['in_seconds'],a['out_seconds']) for a in x['used_intervals']]);d.text((8,y),f"{x['group']}/{x['name']} | {x['duration']:.2f}s | {used}",font=font,fill=(235,240,230))
  for j,sm in enumerate(x['samples']):
   pic=Image.open(sm['path']).resize((384,216),Image.Resampling.LANCZOS);im.paste(pic,(j*384,y+28));d.text((j*384+8,y+241),f"源{sm['time']:.2f}s",font=font,fill=(225,230,225))
 im.save(R/f'片尾舒展_初筛{page:02d}.jpg',quality=95,subsampling=0)
(R/'unused_candidates_sampled_v17.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print(json.dumps({'clips':len(rows),'samples':sum(len(x['samples']) for x in rows),'contact_sheets':[str(p) for p in sorted(R.glob('片尾舒展_初筛*.jpg'))]},ensure_ascii=False))
