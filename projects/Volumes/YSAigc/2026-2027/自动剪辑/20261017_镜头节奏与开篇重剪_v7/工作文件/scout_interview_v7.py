import json,av
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件/采访节奏';OUT.mkdir(exist_ok=True)
inventory=json.loads((ROOT.parent/'20261017_学校粗剪/工作文件/footage.json').read_text())
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',18)
records=[]
for group,token,times in [('006','C0265_',[1,1.7,2.4,3.4]),('006','C0256_',[1,1.7,2.4,3.4]),('005','D0501_',[1,1.6,2.2,3.2])]:
    s=next(x for x in inventory if x['group']==group and token in x['name'])
    sheet=Image.new('RGB',(1440,230),(242,240,235));d=ImageDraw.Draw(sheet)
    for i,sec in enumerate(times):
        with av.open(s['path']) as c:
            v=c.streams.video[0];c.seek(int(sec/v.time_base),stream=v)
            im=next(f.to_image() for f in c.decode(v) if f.time>=sec)
        im.thumbnail((360,203));sheet.paste(im,(i*360,0));d.text((i*360+4,205),f'{group}/{token} {sec:.2f}s',font=font,fill=(32,35,30))
    path=OUT/f'{group}_{token}.jpg';sheet.save(path,quality=95);records.append({'path':s['path'],'sheet':str(path),'times':times})
(OUT/'scout_interview_v7.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print(json.dumps(records,ensure_ascii=False))
