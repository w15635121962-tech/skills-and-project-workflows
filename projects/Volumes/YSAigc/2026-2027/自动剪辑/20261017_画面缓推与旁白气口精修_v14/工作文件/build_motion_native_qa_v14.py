from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
R=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_画面缓推与旁白气口精修_v14');W=R/'工作文件';O=R/'精修预览/缓推独立核查';O.mkdir(exist_ok=True)
rows=json.loads((W/'native_motion_applied_v14.json').read_text());font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',22)
for page,k in enumerate(range(0,len(rows),5),1):
 batch=rows[k:k+5];can=Image.new('RGB',(1920,len(batch)*405),(16,24,28));draw=ImageDraw.Draw(can)
 for j,x in enumerate(batch):
  y=j*405
  for c,fr in enumerate(x['after_frames']):
   im=Image.open(fr['path']).convert('RGB').resize((640,360),Image.Resampling.LANCZOS);can.paste(im,(c*640,y));draw.text((c*640+8,y+362),f"{fr['label']} R{fr['frame']}",font=font,fill=(220,230,225))
  draw.text((180,y+362),f"T{x['track']} R{x['start']} | {x['duration']/25:.2f}s | {x['amplitude']*100:g}% | {Path(x['source_path']).name}",font=font,fill=(230,235,230))
 can.save(O/f'原生缓推_首中尾_{page}.jpg',quality=96,subsampling=0)
print(json.dumps({'rows':len(rows),'pages':[str(p) for p in sorted(O.glob('原生缓推_首中尾_*.jpg'))]},ensure_ascii=False))
