from pathlib import Path
import json,math,av
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';x=json.loads((ROOT.parent/'20261017_学校粗剪/工作文件/footage.json').read_text())
targets=[('004','A001C241',[1,2,3,4,5,7,9,10]),('004','A001C307',[30,35,40,45,50,55,60,65]),('004','A001C001',[0,1,2,3,5,7,9,11]),('003','A003C229',[2,4,6,8,10,12,14,16]),('003','A003C211',[2,4,6,8,10,12,14,16])]
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',16)
for g,token,times in targets:
 s=next(a for a in x if a['group']==g and token in a['name']);sheet=Image.new('RGB',(1440,2*228),(240,239,235));d=ImageDraw.Draw(sheet)
 for i,sec in enumerate(times):
  with av.open(s['path']) as c:
   v=c.streams.video[0];c.seek(int(sec/v.time_base),stream=v)
   for f in c.decode(v):
    if f.time>=sec:im=f.to_image();break
  im.thumbnail((360,203));xx=i%4*360;yy=i//4*228;sheet.paste(im,(xx,yy));d.text((xx+4,yy+204),f'{token} {sec:.2f}s',font=font,fill='black')
 dest=OUT/f'候选_{g}_{token}.jpg';sheet.save(dest,quality=94);print(dest,flush=True)
