from pathlib import Path
import json,av
from PIL import Image,ImageDraw,ImageFont
R=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_大气开篇与书法角标_v15/工作文件/开篇候选');meta=json.loads((R/'校园源片_已抽帧.json').read_text());pick=[('004','A001C240',8.0),('006','C0327',6.0),('002','A002C018',5.0)];rows=[]
for group,prefix,t0 in pick:
 x=next(x.copy() for x in meta if x['group']==group and x['name'].startswith(prefix));x['suggested_source_in_seconds']=t0;x['suggested_source_out_exclusive_seconds']=t0+2.4;x['source_in_frame']=round(t0*x['fps']);x['source_out_exclusive_frame']=x['source_in_frame']+60;x['samples']=[]
 with av.open(x['path']) as c:
  st=c.streams.video[0]
  for i,delta in enumerate([0,10,20,30,40,50,59]):
   t=t0+delta/25;c.seek(int(t/st.time_base),stream=st,backward=True,any_frame=False)
   for f in c.decode(st):
    if f.time is not None and f.time>=t-.015:
     p=R/'精确区间'/prefix/f'{delta:02d}_{f.time:.2f}s.jpg';p.parent.mkdir(parents=True,exist_ok=True);f.to_image().save(p,quality=97,subsampling=0);x['samples'].append({'record_local_frame':delta,'source_time':f.time,'path':str(p)});break
 x['source_overlap']=[]
 for u in x['used_intervals']:
  if max(t0,u['in_seconds'])<min(t0+2.4,u['out_seconds']):x['source_overlap'].append(u)
 rows.append(x)
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',24);can=Image.new('RGB',(1920,len(rows)*420),(14,24,26));dr=ImageDraw.Draw(can)
for r,x in enumerate(rows):
 y=r*420;dr.text((10,y+4),f"候选{r+1} {x['group']}/{x['name']} | {x['suggested_source_in_seconds']:.2f}–{x['suggested_source_out_exclusive_seconds']:.2f}s | 25fps / 60帧 / 无重叠",font=font,fill=(230,235,225))
 for j,k in enumerate([0,3,6]):
  f=x['samples'][k];im=Image.open(f['path']).convert('RGB').resize((640,360),Image.Resampling.LANCZOS);can.paste(im,(j*640,y+36));dr.text((j*640+8,y+392),f"{['首','中','尾'][j]} 源{f['source_time']:.2f}s",font=font,fill=(225,235,225))
can.save(R/'三组开篇_精确首中尾.jpg',quality=97,subsampling=0);(R/'三组开篇_精确抽帧.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print(str(R/'三组开篇_精确首中尾.jpg'))
