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
 sheet([('006','C0273',[.4,1.48,2.52]),('006','C0292',[1,4,7]),('003','A003C008',[1,3,5]),('003','A003C004',[1,3,5]),('003','A003C128',[1,3,5]),('003','A003C131',[1,3,5])],'动作替换候选_01.jpg')
