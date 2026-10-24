from pathlib import Path
import json,os,subprocess,math,concurrent.futures,hashlib,re
from PIL import Image,ImageDraw,ImageFont
BASE=Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕');D=BASE/'达芬奇剪辑_EP21-25_20261020'
planpath=D/'剪辑执行计划.json';raw=planpath.read_bytes();P=json.loads(raw)
O=D/'画面核验/序列核验_EP21-22';O.mkdir(exist_ok=True)
os.environ['PATH']='/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin:'+os.environ['PATH']
PY='/Users/zc/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3';LOOK='/Users/zc/.codex/skills/ffmpeg-skill/scripts/look.py'
meta={r['file']:r for r in json.loads((D/'ffmpeg_skill_probe_EP21-25.json').read_text()) if r.get('video')}
old=json.loads((D/'画面核验/EP21-23_抽帧索引.json').read_text())
cache={}
for r in old:
 for t,f in zip(r['sample_times_seconds'],r['frames']):cache[(r['source'],round(t*24))]=Path(f)
frames=[];needed={}
for ep in P['episodes']:
 if ep['episode'] not in [21,22]:continue
 fps=ep['fps']
 for i,c in enumerate(ep['video']):
  st,en=c['source_start_frame'],c['source_end_frame_exclusive'];dur=en-st
  offsets=[0,dur//2,dur-1]
  for role,off in zip(['START','MID','END-1'],offsets):
   sf=st+off;src=c['source_path'];still=Path(src).suffix.lower()=='.png'
   if still:f=Path(src)
   else:
    key=(src,sf)
    if key not in cache:
     folder=O/'frames'/Path(src).stem;folder.mkdir(parents=True,exist_ok=True);f=folder/f'f{sf:06d}.png';cache[key]=f
     if not f.exists():needed.setdefault(src,[]).append(sf)
    f=cache[key]
   frames.append({'episode':ep['episode'],'clip_index':i,'sample':role,'source':src,'source_frame':sf if not still else None,'source_seconds':sf/fps if not still else None,'record_frame':c['record_frame']+off,'timeline_seconds':(c['record_frame']+off)/fps,'tag':c['tag'],'still':still,'properties':c.get('properties'),'frame_path':str(f)})
def extract(item):
 src,ns=item
 for n in sorted(set(ns)):
  sec=math.floor(n/24*1000+1e-8)/1000
  cmd=[PY,LOOK,src,'-o',str(cache[(src,n)]),'--at',f'{sec:.3f}','--width','480','--no-timecode','--json','--timeout','120']
  r=subprocess.run(cmd,capture_output=True,text=True)
  if r.returncode:raise RuntimeError(src+' '+r.stderr[-300:])
 return src
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for src in pool.map(extract,needed.items()):print('EXTRACTED',Path(src).name,flush=True)
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',13);titlefont=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',19)
pages=[]
for ep in [21,22]:
 fs=[x for x in frames if x['episode']==ep]
 for pg in range(math.ceil(len(fs)/24)):
  current=fs[pg*24:(pg+1)*24];cols=6;cw=180;ih=320;ch=377;head=50;nr=math.ceil(len(current)/cols)
  sh=Image.new('RGB',(cols*cw,nr*ch+head),(18,18,18));d=ImageDraw.Draw(sh)
  d.text((8,5),f'EP{ep} planned V1 sequence | page {pg+1} | each clip START/MID/END-1 | crop simulated',font=titlefont,fill='white')
  for j,x in enumerate(current):
   im=Image.open(x['frame_path']).convert('RGB')
   if x.get('properties'):
    native=meta[x['source']]['video'];sx=im.width/native['width'];sy=im.height/native['height']
    box=(round(230*sx),round(180*sy),round((230+240)*sx),round((180+427)*sy))
    im=im.crop(box);x['simulated_crop_native']={'x':230,'y':180,'width':240,'height':427};x['note']='Simulated requested native crop, not verified Resolve Pan/Tilt rendering'
   im.thumbnail((cw,ih));xx=j%cols*cw;yy=head+j//cols*ch
   sh.paste(im,(xx+(cw-im.width)//2,yy+(ih-im.height)//2))
   label=Path(x['source']).stem.replace('女版','NV').replace('EP21_','21_')
   d.text((xx+3,yy+ih+1),f"C{x['clip_index']:02d} {x['sample']} {label}",font=font,fill='white')
   st='STILL' if x['still'] else f"S {x['source_seconds']:.3f}s F{x['source_frame']}"
   d.text((xx+3,yy+ih+18),f"TL {x['timeline_seconds']:.3f}s | {st}",font=font,fill='white')
   if x.get('properties'):d.text((xx+3,yy+ih+35),'CROP x230 y180 240x427',font=font,fill='#ffdd66')
  dest=O/f'EP{ep}_sequence_page{pg+1:02d}.png';sh.save(dest);pages.append(str(dest))
R={'plan':str(planpath),'plan_sha256':hashlib.sha256(raw).hexdigest(),'scope':'EP21/22 planned V1 only; requested source start/mid/end-1 samples, not complete dynamic playback','source_seek_method':'24fps frame index converted to seconds then floored to milliseconds so the look.py seek does not round past requested frame','crop_scope':'Physical x230,y180,w240,h427 simulated for the single flagged EP21 clip. Resolve API Pan/Tilt transform not visually rendered or verified.','pages':pages,'samples':frames,'actual_view_status':'pending'}
(O/'序列抽帧索引.json').write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n')
print('TOTAL',len(frames),'samples',len(pages),'pages')

