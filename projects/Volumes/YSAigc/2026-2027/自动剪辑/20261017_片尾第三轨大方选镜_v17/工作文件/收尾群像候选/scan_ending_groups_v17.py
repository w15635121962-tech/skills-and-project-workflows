from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from PIL import Image,ImageDraw,ImageFont
import json,av,numpy as np
ROOT=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_片尾第三轨大方选镜_v17');OUT=ROOT/'工作文件/收尾群像候选';SCHOOL=Path('/Volumes/YSAigc/2026-2027/文汇中学/拍摄素材转码');font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Songti.ttc',18,index=6)
snap=json.loads((ROOT/'工作文件/live_before_v17.json').read_text());used={}
for tr in snap['video']:
 for x in tr['items']:
  if x.get('path'):used.setdefault(x['path'],[]).append({'track':tr['track'],'record_in':x['start'],'record_out_exclusive':x['end'],'source_in':x['offset'],'source_out_exclusive':x['offset']+(x['end']-x['start'])})
records=[]
for folder,keys in [('003',[f'A003C{x:03d}' for x in [191,192,194,195,196,197,198,201,202,207,208,209,210]]),('007',['C0115','C0116','C0117','C0118'])]:
 for p in sorted((SCHOOL/folder/'Proxies').iterdir()):
  if any(p.stem.startswith(k) for k in keys):records.append({'path':str(p),'id':folder+'_'+p.stem})
def run(it):
 data={**it};frames=[];thumbnails=[];fd=OUT/'源抽帧'/it['id'];fd.mkdir(parents=True,exist_ok=True)
 with av.open(it['path']) as c:
  s=c.streams.video[0];s.thread_type='AUTO';dur=float(s.duration*s.time_base) if s.duration else c.duration/av.time_base;fps=float(s.average_rate);data.update({'duration_seconds':dur,'fps':str(s.average_rate),'width':s.width,'height':s.height,'current_source_uses':used.get(it['path'],[])})
  ts=np.linspace(.4,max(.4,dur-.4),9)
  for n,sec in enumerate(ts):
   c.seek(int(sec/float(s.time_base)),stream=s,backward=True)
   for f in c.decode(s):
    if f.pts is not None and float(f.pts*s.time_base)+1e-8>=sec:
     im=f.to_image().convert('RGB');t=float(f.pts*s.time_base);break
   p=fd/f'{n}_{t:.3f}s.jpg';im.save(p,quality=94);frames.append({'seconds':t,'frame':round(t*fps),'path':str(p)})
   th=Image.new('RGB',(512,312),(19,30,26));im.thumbnail((512,288));th.paste(im,((512-im.width)//2,0));dr=ImageDraw.Draw(th);dr.text((8,289),f'{t:.3f}s / {round(t*fps)}f',font=font,fill=(238,230,207));thumbnails.append(th)
 sheet=Image.new('RGB',(1536,986),(29,40,34));dr=ImageDraw.Draw(sheet);dr.text((8,8),it['id']+'  已用:'+str(data['current_source_uses']),font=font,fill=(238,230,207))
 for i,im in enumerate(thumbnails):sheet.paste(im,((i%3)*512,50+(i//3)*312))
 p=OUT/(it['id']+'_检索.jpg');sheet.save(p,quality=94);data.update({'contact_sheet':str(p),'frames':frames});return data
res=[]
with ThreadPoolExecutor(max_workers=4) as ex:
 for f in as_completed([ex.submit(run,it) for it in records]):res.append(f.result())
res.sort(key=lambda x:x['id']);(OUT/'群像候选索引.json').write_text(json.dumps(res,ensure_ascii=False,indent=2))
for r in res:print(r['id'],round(r['duration_seconds'],2),r['current_source_uses'])
