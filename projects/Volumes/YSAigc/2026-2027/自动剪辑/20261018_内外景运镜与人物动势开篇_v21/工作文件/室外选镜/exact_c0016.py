import json,av
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
p='/Volumes/YSAigc/2026-2027/文汇中学/拍摄素材转码/007/Proxies/C0016_Proxy.mov'
frames=[250,256,262,268,274,280,286,292,295];F=ImageFont.load_default(size=16);sheet=Image.new('RGB',(1440,894),(12,16,20));dr=ImageDraw.Draw(sheet);i=0
with av.open(p) as c:
 s=c.streams.video[0];c.seek(int(10/s.time_base),stream=s)
 for f in c.decode(s):
  fn=round(float(f.time)*25)
  if i>=len(frames):break
  if fn<frames[i]:continue
  im=f.to_image();im.thumbnail((480,270));xx=i%3*480;yy=i//3*298;sheet.paste(im,(xx,yy));dr.text((xx+3,yy+272),f'C0016 frame {fn} / {fn/25:.2f}s',font=F,fill='white');i+=1
q=ROOT/'C0016_250-296_精确替代九帧.jpg';sheet.save(q,quality=95)
z={'path':p,'fps':25,'source_in_frame':250,'source_out_frame_exclusive':296,'duration_frames':46,'duration_seconds':1.84,'record_frame':370,'record_end_frame_exclusive':416,'description':'晨光屋檐间的现代校园楼宇仰拍，原生轻微横摇，地面网线均在画外','contact_sheet':str(q),'previous_usage_in_live_before_v21':[{'track':1,'record_start':942,'record_end':1002,'source_in_frame':175,'source_out_frame_exclusive':235}],'overlaps_existing_source_range':False,'note':'同一整源但源区间不重复，美观优先；可复用原C0016已校验调色作为起点'}
(ROOT/'现代校园替代唯一优选_C0016.json').write_text(json.dumps(z,ensure_ascii=False,indent=2));print(q)
