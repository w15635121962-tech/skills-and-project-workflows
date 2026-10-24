import av,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from concurrent.futures import ThreadPoolExecutor
R=Path('/Volumes/YSAigc/2026-2027/文汇中学/拍摄素材转码');O=Path(__file__).parent
names=['C0125_Proxy','A003C200','A003C201','A003C221','A001C338','C0289_Proxy','C0298_Proxy','A003C137']
paths=[]
for n in names:paths.extend(list(R.rglob(n+'*mov'))[:1])
fnt=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',20)
def job(p):
 c=av.open(str(p));s=c.streams.video[0];fps=float(s.average_rate);dur=float(s.duration*s.time_base);inds=[int((.06+.105*i)*dur*fps) for i in range(9)];im=Image.new('RGB',(1440,876),(15,15,15));d=ImageDraw.Draw(im);actual=[]
 for i,idx in enumerate(inds):
  ts=int(idx/fps/s.time_base);c.seek(ts,stream=s,backward=True);f=None
  for f in c.decode(s):
   if float(f.time)+.0001>=idx/fps:break
  if f is None:continue
  rgb=f.to_image();rgb.thumbnail((480,270));x=(i%3)*480;y=(i//3)*292;im.paste(rgb,(x,y));d.text((x+8,y+270),f'{p.stem} fr {int(round(f.time*fps))}',font=fnt,fill='white');actual.append(int(round(f.time*fps)))
 im.save(O/(p.stem+'_rough9.jpg'),quality=90);c.close();return {'path':str(p),'fps':fps,'duration':dur,'rough_frames':actual}
with ThreadPoolExecutor(max_workers=3) as e: rows=list(e.map(job,paths))
(O/'rough_scan_v22.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print(json.dumps(rows,ensure_ascii=False))
