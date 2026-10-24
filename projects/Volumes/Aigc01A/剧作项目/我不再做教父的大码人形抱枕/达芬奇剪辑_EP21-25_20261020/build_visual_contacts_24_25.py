from pathlib import Path
import json,subprocess,math
from concurrent.futures import ThreadPoolExecutor
from PIL import Image,ImageDraw,ImageFont
root=Path.cwd();base=root/'达芬奇剪辑_EP21-25_20261020';out=base/'画面核验';out.mkdir(exist_ok=True)
inventory=json.loads((base/'素材盘点.json').read_text())
rows=[r for r in inventory['files'] if r['kind']=='video' and r['episode'] in (24,25)]
rows.sort(key=lambda r:(r['episode'],r['shot_group_number'],r['version_number']))
ffmpeg=Path(inventory['ffmpeg_path'])
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf',18)
font_big=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf',23)
font_small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf',15)
def one(r):
 p=Path(r['path']);v=r['video_streams'][0];fps=v['fps'];nf=v['nb_frames']
 if not nf:nf=round(v['duration_seconds']*fps)
 indices={0,nf//2,nf-1}
 for n in range(0,nf,round(2*fps)):indices.add(n)
 indices=sorted(indices)
 slug=f'EP{r["episode"]}_G{r["shot_group_number"]:02d}_V{r["version_number"]:02d}'
 fd=out/slug;fd.mkdir(exist_ok=True)
 expr='+'.join(f'eq(n,{n})' for n in indices)
 cmd=[str(ffmpeg),'-hide_banner','-loglevel','error','-nostdin','-i',str(p),'-vf',f"select='{expr}'",'-vsync','0','-q:v','3','-y',str(fd/'frame_%03d.jpg')]
 res=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
 if res.returncode:raise RuntimeError(str(p)+':'+res.stderr)
 frames=sorted(fd.glob('frame_*.jpg'))
 assert len(frames)==len(indices),(p,len(frames),len(indices))
 tw,th=224,round(224*v['height']/v['width']);gap=10;caption=43;cols=4;nr=math.ceil(len(frames)/cols);header=86
 canvas=Image.new('RGB',(cols*(tw+gap)+gap,header+nr*(th+caption+gap)+gap),(24,27,34));d=ImageDraw.Draw(canvas)
 d.text((10,9),p.name,font=font_big,fill='white')
 d.text((10,42),f'{nf/fps:.3f}s video | {v["width"]}x{v["height"]} | {fps:g}fps | frames: start, every 2s, middle, last',font=font_small,fill=(200,205,215))
 infos=[]
 for i,(fp,n) in enumerate(zip(frames,indices)):
  x=gap+(i%cols)*(tw+gap);y=header+(i//cols)*(th+caption+gap)
  im=Image.open(fp).convert('RGB').resize((tw,th),Image.Resampling.LANCZOS);canvas.paste(im,(x,y))
  t=n/fps
  label=f'{p.stem}  t={t:.3f}s'
  d.text((x,y+th+2),label,font=font_small,fill='white')
  d.text((x,y+th+21),f'frame {n}/{nf-1}',font=font_small,fill=(185,195,210))
  infos.append({'path':str(fp),'frame_index':n,'time_seconds':t})
 contact=out/(slug+'_contact.jpg');canvas.save(contact,quality=91)
 return {'source':str(p),'episode':r['episode'],'group':r['shot_group'],'version':r['version_number'],'video_duration_seconds':nf/fps,'container_duration_seconds':r['duration_seconds'],'fps':fps,'contact_sheet':str(contact),'frames':infos}
with ThreadPoolExecutor(max_workers=4) as pool:manifest=list(pool.map(one,rows))
(out/'联系表索引_EP24-25.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(f'{len(manifest)} contact sheets, {sum(len(r["frames"]) for r in manifest)} timestamped frames.')
for m in manifest:print(Path(m['contact_sheet']).name)
