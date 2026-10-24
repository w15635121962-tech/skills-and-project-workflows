from pathlib import Path
import json,sys,subprocess,concurrent.futures,math,av
from PIL import Image,ImageOps,ImageDraw,ImageFont
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';VIS=ROOT/'画面资料';VIS.mkdir(exist_ok=True)
plan=json.loads((OUT/'narrative_edit_plan.json').read_text());SK=Path('/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts');logs=OUT/'visual_logs';logs.mkdir(exist_ok=True)
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',30)
def build_photo(task):
 target=Path(task['output']);canvas=VIS/(task['id']+'_完整构图.png')
 if target.exists() and target.stat().st_size>1000:return task['id']
 src=ImageOps.exif_transpose(Image.open(task['path'])).convert('RGB');src.thumbnail((1816,960),Image.Resampling.LANCZOS)
 image=Image.new('RGB',(1920,1080),(233,230,222));x=(1920-src.width)//2;y=(1020-src.height)//2;image.paste(src,(x,y))
 draw=ImageDraw.Draw(image)
 if task['label']:draw.text((52,1027),task['label'],font=font,fill=(58,62,61))
 image.save(canvas)
 args=[sys.executable,str(SK/'insert.py'),str(canvas),'-o',str(target),'--duration',str(task['duration']),'--width','1920','--height','1080','--fps','25','--zoom','in','--zoom-amount','1.025','--fast','--json-brief']
 for dry in [True,False]:
  proc=subprocess.run(args+(['--dry-run'] if dry else []),capture_output=True,text=True);(logs/f"{task['id']}-{dry}.log").write_text(proc.stdout+'\n'+proc.stderr,encoding='utf-8');assert proc.returncode==0,proc.stdout+proc.stderr
 return task['id']
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for aid in pool.map(build_photo,plan['photo_tasks']):print('PHOTO_READY',aid,flush=True)
# Check real metadata of all picture sources and prepare a contact sheet of new choices.
cache={}
for s in plan['shots']:
 if s['path'] not in cache:
  with av.open(s['path']) as c:
   v=c.streams.video[0];cache[s['path']]={'duration':c.duration/1e6 if c.duration else (v.duration*float(v.time_base)),'fps':float(v.average_rate or v.base_rate),'width':v.width,'height':v.height}
  assert Path(s['path']).exists()
 m=cache[s['path']];assert s['out']<=m['duration']+.04,(s['index'],s['out'],m['duration'])
 s['fps']=m['fps'];s['resolution']=[m['width'],m['height']]
(OUT/'narrative_edit_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8');(OUT/'visual_sources.json').write_text(json.dumps(cache,ensure_ascii=False,indent=2),encoding='utf-8')
def frame(s):
 tm=(s['in']+s['out'])/2
 with av.open(s['path']) as c:
  v=c.streams.video[0];c.seek(int(tm/v.time_base),stream=v)
  for f in c.decode(v):
   if (f.time or 0)>=tm:
    im=f.to_image();im.thumbnail((320,180));return s,im
 raise RuntimeError(s['path'])
fnt=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',14)
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:imgs=list(pool.map(frame,plan['shots']))
for start in range(0,len(imgs),28):
 part=imgs[start:start+28];sheet=Image.new('RGB',(1280,math.ceil(len(part)/4)*224),'white');draw=ImageDraw.Draw(sheet)
 for k,(s,im) in enumerate(part):
  x=k%4*320;y=k//4*224;sheet.paste(im,(x,y));draw.text((x+3,y+181),f"{s['index']:03d}  {s['record_frame']/25:.2f}s  {s['chapter'][:15]}",font=fnt,fill='black');draw.text((x+3,y+200),s['intent'][:21],font=fnt,fill='black')
 dest=OUT/f"v2-selects-{start//28+1}.jpg";sheet.save(dest);print(dest,flush=True)
print('VISUALS_READY',len(imgs),flush=True)
