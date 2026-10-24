import json, pathlib, subprocess, concurrent.futures, math
from PIL import Image,ImageDraw,ImageFont
root=pathlib.Path(__file__).resolve().parent
D=json.loads((root.parent/'准备/media_inventory.json').read_text(encoding='utf-8'))
ff='/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffmpeg'
frames=root/'frames';frames.mkdir(exist_ok=True)
font=ImageFont.truetype('/Users/zc/Library/Fonts/NotoSansHans-Black.otf',19)
small=ImageFont.truetype('/Users/zc/Library/Fonts/NotoSansHans-Black.otf',16)
manifest=[]
def extract(v):
 dur=float(v['video_streams'][0]['duration']); ts=[.15,dur/3,dur*2/3,max(.15,dur-.25)]; fs=[]
 for i,t in enumerate(ts):
  dest=frames/(v['filename'][:-4]+f'_{i}_{t:.3f}.jpg')
  if not dest.exists():
   subprocess.run([ff,'-v','error','-ss',str(t),'-i',v['path'],'-frames:v','1','-vf','scale=220:-2','-q:v','2',str(dest)],check=True,capture_output=True)
  fs.append({'time_seconds':round(t,3),'image':str(dest)})
 return {'filename':v['filename'],'source_path':v['path'],'duration_seconds':dur,'frames':fs}
for e in D['episodes']:
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex: clips=list(ex.map(extract,e['videos']))
 for pg in range(math.ceil(len(clips)/5)):
  sub=clips[pg*5:(pg+1)*5];cw=220;gap=8;top=52;head=34;ih=392;rh=head+ih+30
  im=Image.new('RGB',(4*cw+5*gap,top+len(sub)*rh),(245,245,245));dr=ImageDraw.Draw(im)
  dr.text((gap,8),f'男版 EP{e["episode"]} 画面核验 Page {pg+1}: begin / 1/3 / 2/3 / tail',font=font,fill='black')
  for row,c in enumerate(sub):
   y=top+row*rh;dr.text((gap,y),f'{c["filename"]}  video {c["duration_seconds"]:.3f}s',font=font,fill='black')
   for k,f in enumerate(c['frames']):
    fr=Image.open(f['image']).convert('RGB');im.paste(fr,(gap+k*(cw+gap),y+head));dr.text((gap+k*(cw+gap),y+head+ih),f'{f["time_seconds"]:.3f}s',font=small,fill='black')
  dest=root/f'EP{e["episode"]}_contact_{pg+1}.jpg';im.save(dest,quality=93);manifest.append({'episode':e['episode'],'contact_sheet':str(dest),'clips':sub});print(dest,flush=True)
(root/'contact_sheet_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
