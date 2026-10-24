from pathlib import Path
import json,av
from PIL import Image,ImageDraw,ImageFont
ROOT=Path('/Volumes/YSAigc/2026-2027');OUT=Path(__file__).parent
F=json.load(open(ROOT/'自动剪辑/20261017_学校粗剪/工作文件/footage.json'))
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',18)
def lookup(g,t):return next(a for a in F if a['group']==g and t in a['name'])
def frame(path,sec):
 with av.open(path) as c:
  v=c.streams.video[0];c.seek(int(max(0,sec-.25)/v.time_base),stream=v)
  for f in c.decode(v):
   if f.time>=sec-.0001:return f.to_image()
 raise RuntimeError((path,sec))
def sheet(rows,name):
 im=Image.new('RGB',(1440,len(rows)*298),(245,243,238));d=ImageDraw.Draw(im)
 for i,(g,t,times) in enumerate(rows):
  a=lookup(g,t)
  for j,sec in enumerate(times):
   f=frame(a['path'],min(sec,a['duration']-.08));f=f.resize((480,270));im.paste(f,(j*480,i*298));d.text((j*480+6,i*298+272),f'{g}/{t}  {sec:.2f}s',font=font,fill=(30,30,30))
 p=OUT/name;im.save(p,quality=93);print(p,flush=True)
if __name__=='__main__':
 batches=[
 [('004','A001C002',[1,4,7]),('004','A001C007',[.3,2.5,4.8]),('004','A001C014',[1,4,7]),('004','A001C021',[1,5,9]),('004','A001C031',[2,5,8]),('004','A001C033',[3,7,11])],
 [('004','A001C048',[1,4,7]),('004','A001C050',[1,4,7]),('004','A001C051',[1,6,11]),('004','A001C070',[1,5,9]),('004','A001C071',[1,5,9]),('004','A001C078',[2,6,10])],
 [('001','C0001',[.4,2.8,5.2]),('001','C0006',[3,6,9]),('001','C0010',[3,9,15]),('001','C0011',[3,10,17]),('003','A003C139',[6,8,10]),('003','A003C140',[3,6,9])],
 [('003','A003C132',[3,6,9]),('003','A003C129',[2,5,8]),('003','A003C125',[3,6,9]),('006','C0151',[3,7,11]),('006','C0205',[3,7,11]),('006','C0280',[3,6,9])],
 [('004','A001C081',[8,15,22]),('004','A001C082',[1,3,5]),('004','A001C083',[2,5,8]),('004','A001C084',[2,5,8]),('004','A001C086',[2,5,8]),('004','A001C089',[5,12,19])]
 ]
 for i,b in enumerate(batches,1):sheet(b,f'候选拼图_{i:02d}.jpg')
