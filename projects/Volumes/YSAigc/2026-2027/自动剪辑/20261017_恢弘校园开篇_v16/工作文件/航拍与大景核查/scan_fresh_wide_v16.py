from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from concurrent.futures import ThreadPoolExecutor,as_completed
import json,av,numpy as np,math
OUT=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_恢弘校园开篇_v16/工作文件/航拍与大景核查');SCHOOL=Path('/Volumes/YSAigc/2026-2027/文汇中学');font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Songti.ttc',17,index=6)
records=[]
for folder,keys in [('007',['C0025','C0026','C0027','C0028','C0034','C0074','C0075','C0076','C0077','C0103','C0104','C0105','C0106','C0107','C0108','C0109']),('006',['C0308','C0313','C0327','C0328']),('003',['A003C031'])]:
 for p in sorted((SCHOOL/'拍摄素材转码'/folder/'Proxies').iterdir()):
  if any(p.stem.startswith(s) for s in keys):records.append({'path':str(p),'id':folder+'_'+p.stem})
snap=json.loads(Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_大气开篇与书法角标_v15/工作文件/final_native_snapshot_v15.json').read_text())
used={}
for tr in snap['video']:
 for it in tr['items']:
  if it.get('path'):used.setdefault(it['path'],[]).append({'track':tr['track'],'record_start':it['start'],'record_end_exclusive':it['end'],'source_in_frame':it['offset'],'source_out_frame_exclusive':it['offset']+(it['end']-it['start'])})
def run(it):
 p=Path(it['path']);fs=[];thumbs=[]
 with av.open(str(p)) as c:
  s=c.streams.video[0];s.thread_type='AUTO';duration=float(s.duration*s.time_base) if s.duration else c.duration/av.time_base;fps=float(s.average_rate)
  for n,sec in enumerate(np.linspace(.4,max(.4,duration-.4),9)):
   c.seek(max(0,int(sec/float(s.time_base))),stream=s,backward=True)
   for f in c.decode(s):
    if f.pts is not None and float(f.pts*s.time_base)+1e-7>=sec:
     im=f.to_image().convert('RGB');actual=float(f.pts*s.time_base);break
   dest=OUT/'实拍补查'/it['id'];dest.mkdir(parents=True,exist_ok=True);q=dest/f'{n}_{actual:.3f}s.jpg';im.save(q,quality=94)
   fs.append({'seconds':actual,'frame':round(actual*fps),'path':str(q)});th=Image.new('RGB',(512,312),(18,29,26));sub=im.copy();sub.thumbnail((512,288));th.paste(sub,((512-sub.width)//2,0));dr=ImageDraw.Draw(th);dr.text((8,289),f'{actual:.3f}s / {round(actual*fps)}f',font=font,fill=(238,230,207));thumbs.append(th)
  data={**it,'duration_seconds':duration,'width':s.width,'height':s.height,'fps':str(s.average_rate),'v15_current_uses':used.get(it['path'],[]),'frames':fs}
 sheet=Image.new('RGB',(1536,986),(29,39,35));dr=ImageDraw.Draw(sheet);dr.text((8,8),it['id'],font=font,fill=(238,230,207))
 for i,th in enumerate(thumbs):sheet.paste(th,((i%3)*512,50+(i//3)*312))
 sp=OUT/f'现场大景_{it["id"]}.jpg';sheet.save(sp,quality=94);data['contact_sheet']=str(sp);return data
res=[]
with ThreadPoolExecutor(max_workers=4) as ex:
 for f in as_completed([ex.submit(run,it) for it in records]):res.append(f.result())
res.sort(key=lambda x:x['id']);(OUT/'现场大景补查索引.json').write_text(json.dumps(res,ensure_ascii=False,indent=2))
# Actual environmental still contact sheet.
photos=[]
for p in sorted((SCHOOL/'学校素材资料/3-校园环境').rglob('*')):
 if p.suffix.lower() in ['.jpg','.png']:
  im=Image.open(p).convert('RGB');th=Image.new('RGB',(384,256),(17,27,23));sub=im.copy();sub.thumbnail((384,216));th.paste(sub,((384-sub.width)//2,0));dr=ImageDraw.Draw(th);dr.text((8,217),p.name[:21],font=font,fill=(238,230,207));dr.text((8,238),str(im.size),font=font,fill=(180,196,182));photos.append((th,str(p),list(im.size)))
sheet=Image.new('RGB',(1536,256*math.ceil(len(photos)/4)),(29,39,35))
for i,(th,_,_) in enumerate(photos):sheet.paste(th,((i%4)*384,(i//4)*256))
sheet.save(OUT/'校园环境原图核查.jpg',quality=94);(OUT/'校园环境照片索引.json').write_text(json.dumps([{'path':p,'size':s} for _,p,s in photos],ensure_ascii=False,indent=2));print('fresh',len(res),'photos',len(photos))
