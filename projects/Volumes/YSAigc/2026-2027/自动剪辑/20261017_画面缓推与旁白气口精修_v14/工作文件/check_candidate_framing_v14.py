from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,math
R=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_画面缓推与旁白气口精修_v14/工作文件');O=R/'源画面运动审阅';allrows=json.load(open(R/'source_motion_diagnostics_v14.json'));idx={(x['track'],x['start']):x for x in allrows}
selected=[60,234,340,942,1067,1819,2263,2595,3003,3675,4161,4609,4854,5717,6260,6370,6420,6909,7965,9045,9092,9175,9243,9627,9690,10162,10622,10850]
f=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',22)
for page,j in enumerate(range(0,len(selected),6),1):
 batch=selected[j:j+6];can=Image.new('RGB',(1920,len(batch)*240),(16,24,28));d=ImageDraw.Draw(can)
 for row,start in enumerate(batch):
  x=idx[1,start];y=row*240
  for c,si in enumerate([0,3,6]):
   src=Image.open(x['samples'][si]['path']).convert('RGB');w,h=src.size;s=1.025
   after=src.transform(src.size,Image.Transform.AFFINE,(1/s,0,w*(1-1/s)/2,0,1/s,h*(1-1/s)/2),resample=Image.Resampling.BICUBIC)
   for q,im in enumerate([src,after]):
    im=im.resize((320,180),Image.Resampling.LANCZOS);xx=c*640+q*320;can.paste(im,(xx,y));d.text((xx+6,y+183),f'{["首","中","尾"][c]}  {"原构图" if q==0 else "2.5%推近终点"}',font=f,fill=(215,225,218))
  d.text((6,y+211),f"T1 R{start} {x['length_frames']/25:.2f}s  {x['name']}  {x['intent'][:32]}",font=f,fill=(230,235,229))
 can.save(O/f'候选2.5%构图核查_{page}.jpg',quality=95,subsampling=0)
print('WROTE',len(selected),'candidates','5 sheets')
