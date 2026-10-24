from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from PIL import Image,ImageDraw,ImageFont
import av,json,math
import numpy as np
OUT=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_恢弘校园开篇_v16/工作文件/航拍与大景核查')
items=json.loads((OUT/'学校档案33视频清单.json').read_text());font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Songti.ttc',15,index=6)
def getframe(c,s,sec):
 c.seek(max(0,int(sec/float(s.time_base))),stream=s,backward=True)
 for f in c.decode(s):
  if f.pts is not None and float(f.pts*s.time_base)+1e-7>=sec:return f.to_image().convert('RGB'),float(f.pts*s.time_base)
 raise RuntimeError('no frame '+str(sec))
def run(pair):
 idx,item=pair;dur=item['duration_seconds'];start=[0,2,4,6,8,10,14,18,22,26,30]
 if idx==8:ts=sorted(set([t for t in range(0,math.floor(dur)-1,10)]+[t for t in start if t<dur-1]))
 else:ts=sorted(set([t for t in start[:7] if t<dur-1]+[round(t,2) for t in np.linspace(0,max(0,dur-1),13)]))
 frames=OUT/'档案抽帧'/f'{idx:02d}';frames.mkdir(parents=True,exist_ok=True);rs=[];thumbs=[]
 with av.open(item['path']) as c:
  s=c.streams.video[0];s.thread_type='AUTO'
  for n,t in enumerate(ts):
   try:
    im,actual=getframe(c,s,float(t));save=frames/f'{n:03d}_{actual:08.3f}s.jpg';im.save(save,quality=90);rs.append({'requested_seconds':t,'actual_seconds':actual,'path':str(save)})
    thumb=Image.new('RGB',(384,238),(17,28,26));thumbim=im.copy();thumbim.thumbnail((384,216));thumb.paste(thumbim,((384-thumbim.width)//2,0));d=ImageDraw.Draw(thumb);d.text((8,217),f'{idx:02d} / {actual:.3f}s',font=font,fill=(238,231,210));thumbs.append(thumb)
   except Exception as e:rs.append({'requested_seconds':t,'error':str(e)})
 sheets=[]
 for page in range(math.ceil(len(thumbs)/24)):
  chunk=thumbs[page*24:(page+1)*24];im=Image.new('RGB',(1536,40+238*math.ceil(len(chunk)/4)),(30,40,37));d=ImageDraw.Draw(im);d.text((8,8),f'{idx:02d}  {Path(item["path"]).name[:80]}  / 第{page+1}页',font=font,fill=(238,231,210))
  for n,th in enumerate(chunk):im.paste(th,((n%4)*384,40+(n//4)*238))
  sp=OUT/f'档案检索_{idx:02d}_{page+1}.jpg';im.save(sp,quality=93);sheets.append(str(sp))
 return idx,{'index':idx,**item,'frames':rs,'contact_sheets':sheets}
res=[]
with ThreadPoolExecutor(max_workers=4) as ex:
 for fut in as_completed([ex.submit(run,v) for v in enumerate(items)]):
  idx,r=fut.result();res.append(r);print(idx,len(r['frames']),flush=True)
res.sort(key=lambda x:x['index']);(OUT/'档案抽帧索引.json').write_text(json.dumps(res,ensure_ascii=False,indent=2));print('completed',sum(len(x['frames']) for x in res),flush=True)
