from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
R=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_画面缓推与旁白气口精修_v14');W=R/'工作文件';O=R/'精修预览/缓推独立核查';O.mkdir(exist_ok=True)
rows=sorted(json.loads((W/'native_motion_applied_v14.json').read_text()),key=lambda x:(x['track'],x['start']));font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',24)
assert len(rows)==27
for page,k in enumerate(range(0,len(rows),9),1):
 batch=rows[k:k+9];can=Image.new('RGB',(1920,len(batch)*432+50),(16,24,28));draw=ImageDraw.Draw(can);draw.text((12,8),f'学校宣传片 v14｜原生缓推首中尾独立核查 {page}/3',font=font,fill=(225,235,230))
 for j,x in enumerate(batch):
  y=50+j*432;draw.text((10,y+3),f"T{x['track']} R{x['start']}  {x['duration']/25:.2f}秒  缓推{x['amplitude']*100:g}%  {Path(x['source_path']).name}",font=font,fill=(225,235,230))
  for c,fr in enumerate(x['after_frames']):
   im=Image.open(fr['path']).convert('RGB').resize((640,360),Image.Resampling.LANCZOS);can.paste(im,(c*640,y+34));draw.text((c*640+10,y+396),f"{fr['label']}｜R{fr['frame']}",font=font,fill=(205,220,210))
 can.save(O/f'最终27段_已激活缓推_首中尾_{page}.jpg',quality=96,subsampling=0)
print(json.dumps({'rows':len(rows),'pages':[str(p) for p in sorted(O.glob('最终27段_已激活缓推_首中尾_*.jpg'))]},ensure_ascii=False))
