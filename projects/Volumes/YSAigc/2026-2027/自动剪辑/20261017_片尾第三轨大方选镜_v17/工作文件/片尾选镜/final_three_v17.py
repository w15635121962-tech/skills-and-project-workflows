from pathlib import Path
import json,av,hashlib
from PIL import Image,ImageDraw,ImageFont
R=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_片尾第三轨大方选镜_v17/工作文件/片尾选镜');meta=json.loads((R/'unused_candidates_sampled_v17.json').read_text());specs=[('003','A003C067',100,11150,11242),('006','C0258',390,11242,11318),('004','A001C349',450,11318,11407)];rows=[]
for group,prefix,source_in,rec_in,rec_out in specs:
 x=next(x.copy() for x in meta if x['group']==group and x['name'].startswith(prefix));n=rec_out-rec_in;x.update({'track':3,'start':rec_in,'end':rec_out,'record_end_exclusive':rec_out,'duration_frames':n,'source_in_frame':source_in,'source_out_exclusive_frame':source_in+n,'source_out_inclusive_frame':source_in+n-1,'source_in_seconds':source_in/25,'source_out_exclusive_seconds':(source_in+n)/25,'duration_seconds':n/25,'samples':[]})
 with av.open(x['path']) as c:
  st=c.streams.video[0]
  for label,delta in [('首',0),('中',n//2),('尾',n-1)]:
   t=(source_in+delta)/25;c.seek(int(t/st.time_base),stream=st,backward=True,any_frame=False)
   for f in c.decode(st):
    if f.time is not None and f.time>=t-.015:
     p=R/'最终三镜_真实源尺寸'/prefix/f'{label}_F{round(f.time*25)}_{f.time:.2f}s.jpg';p.parent.mkdir(parents=True,exist_ok=True);f.to_image().save(p,quality=98,subsampling=0);x['samples'].append({'label':label,'record_frame':rec_in+delta,'source_frame':round(f.time*25),'source_seconds':f.time,'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()});break
 rows.append(x)
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',23);can=Image.new('RGB',(1920,len(rows)*420),(15,24,27));draw=ImageDraw.Draw(can)
for i,x in enumerate(rows):
 y=i*420;draw.text((8,y+3),f"V3 {x['start']}–{x['end']} | {x['duration_frames']}帧 {x['duration_seconds']:.2f}s | {x['name']} 源{x['source_in_seconds']:.2f}–{x['source_out_exclusive_seconds']:.2f}s",font=font,fill=(230,235,225))
 for j,f in enumerate(x['samples']):
  im=Image.open(f['path']).resize((640,360),Image.Resampling.LANCZOS);can.paste(im,(j*640,y+32));draw.text((j*640+8,y+392),f"{f['label']} 源{f['source_seconds']:.2f}s / F{f['source_frame']}",font=font,fill=(225,235,230))
can.save(R/'片尾V3_最终三镜_真实首中尾.jpg',quality=98,subsampling=0);(R/'three_exact_source_samples_v17.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print(str(R/'片尾V3_最终三镜_真实首中尾.jpg'))
