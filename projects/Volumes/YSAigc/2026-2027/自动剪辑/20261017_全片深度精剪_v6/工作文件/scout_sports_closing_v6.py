import json,av
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件/体育与收束审阅';OUT.mkdir(exist_ok=True)
inventory=json.loads((ROOT.parent/'20261017_学校粗剪/工作文件/footage.json').read_text());font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',16)
targets=[('006','C0303_',[0,1.2,2.4,3.6,4.8,6,7.2,8.4]),('006','C0305_',[0,5,10,15,20,25,30,40]),('005','D0536_',[2,10,18,26,34,42,50,58]),('005','D0523_',[0,3,6,9,12,15,18,21]),('004','A001C262_',[2,8,14,20,26,32,38,44]),('007','C0119_',[0,2,4,6,8,10,12,15]),('003','A003C252_',[0,3,6,9,12,15,18,21]),('007','C0147_',[1,4,7,10,13,16,19,22])]
records=[]
for group,token,times in targets:
 s=next(z for z in inventory if z['group']==group and token in z['name']);times=[min(sec,s['duration']-.12) for sec in times];sheet=Image.new('RGB',(1440,2*228),(242,240,234));d=ImageDraw.Draw(sheet)
 for i,sec in enumerate(times):
  with av.open(s['path']) as c:
   v=c.streams.video[0];c.seek(int(sec/v.time_base),stream=v)
   for f in c.decode(v):
    if f.time>=sec:im=f.to_image();break
  im.thumbnail((360,203));xx=i%4*360;yy=i//4*228;sheet.paste(im,(xx,yy));d.text((xx+5,yy+205),f'{group}/{token} {sec:.2f}s',font=font,fill=(35,40,35))
 path=OUT/f'{group}_{token.rstrip("_")}.jpg';sheet.save(path,quality=94);records.append({'group':group,'path':s['path'],'sheet':str(path),'samples':times});print(path,flush=True)
(OUT/'source_scout.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
