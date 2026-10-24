from pathlib import Path
import json,subprocess,concurrent.futures
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).parent
ps=json.loads((O/'extra_source_probes.json').read_text())
def f(c):
 p=Path(c['path']);name=p.stem;args=['python3','/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts/look.py',str(p),'-o',str(O/('extra_'+name+'.png')),'--at','1.04','--at','3.5','--at','5.92','--no-timecode','--json']
 x=subprocess.run(args,capture_output=True,text=True);(O/('extra_'+name+'.log.json')).write_text(x.stdout)
 if x.returncode:raise RuntimeError(x.stdout+x.stderr)
 c=dict(c);c['frames']=json.loads(x.stdout)['outputs'];return c
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:r=list(ex.map(f,ps))
font=ImageFont.truetype('/System/Library/Fonts/Hiragino Sans GB.ttc',20)
for n in range(0,len(r),6):
 sub=r[n:n+6];im=Image.new('RGB',(1536,len(sub)*325),(23,26,29));dr=ImageDraw.Draw(im)
 for i,c in enumerate(sub):
  y=i*325;dr.text((7,y+2),Path(c['path']).name,font=font,fill='white')
  for k,f in enumerate(c['frames']):
   pic=Image.open(f).convert('RGB');pic.thumbnail((508,286));im.paste(pic,(k*512,y+30))
 im.save(O/f'额外未用视角首中末_{n//6+1:02d}.jpg',quality=88)
(O/'extra_source_scout.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
print(len(r))
