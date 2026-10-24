from pathlib import Path
import json,av,numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_恢弘校园开篇_v16/工作文件/开篇候选');p=Path('/Volumes/YSAigc/2026-2027/文汇中学/拍摄素材转码/007/Proxies/C0034_Proxy.mov');O=R/'C0034_12至18秒_原尺寸';O.mkdir(exist_ok=True);rows=[];prev=None
with av.open(str(p)) as c:
 s=c.streams.video[0];c.seek(int(12/s.time_base),stream=s,backward=True,any_frame=False)
 for fr in c.decode(s):
  if fr.time<12-.01:continue
  if fr.time>18+.01:break
  im=fr.to_image().convert('RGB');path=O/f'{round(fr.time*25):04d}_{fr.time:.2f}s.jpg';im.save(path,quality=98,subsampling=0);small=np.array(im.resize((256,144),Image.Resampling.LANCZOS).convert('L'),dtype=float);small=small[:64,:] # sky/architecture, no students
  if prev is not None:
   a=prev-prev.mean();b=small-small.mean();cross=np.fft.fft2(a)*np.conj(np.fft.fft2(b));cross/=np.maximum(abs(cross),1e-10);cor=np.fft.ifft2(cross).real;yy,xx=np.unravel_index(np.argmax(cor),cor.shape);dy=yy if yy<32 else yy-64;dx=xx if xx<128 else xx-256;mae=float(abs(small-prev).mean())
  else:dx=dy=0;mae=0
  rows.append({'source_frame':round(fr.time*25),'source_time':fr.time,'path':str(path),'sky_building_phase_shift_256px':[int(dx),int(dy)],'sky_building_gray_MAE':mae});prev=small
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',24);times=[12,12.5,13,13.5,14,14.5,15,15.5,16,16.5,17,17.5,18];samples=[min(rows,key=lambda x:abs(x['source_time']-t)) for t in times]
for pg,k in enumerate(range(0,len(samples),8),1):
 b=samples[k:k+8];nr=(len(b)+3)//4;im=Image.new('RGB',(1920,nr*305),(15,24,27));d=ImageDraw.Draw(im)
 for n,x in enumerate(b):
  y=(n//4)*305;xx=(n%4)*480;pic=Image.open(x['path']).resize((480,270),Image.Resampling.LANCZOS);im.paste(pic,(xx,y));d.text((xx+8,y+272),f"源{x['source_time']:.2f}s F{x['source_frame']}",font=font,fill=(225,235,230))
 im.save(R/f'C0034_12至18秒_连贯性{pg}.jpg',quality=97,subsampling=0)
(R/'C0034_12至18秒_逐帧抽取.json').write_text(json.dumps({'source':str(p),'fps':25,'dimensions':[1280,720],'rows':rows},ensure_ascii=False,indent=2));print(json.dumps({'frames':len(rows),'contacts':[str(p) for p in R.glob('C0034_12至18秒_连贯性*.jpg')]},ensure_ascii=False))
