from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import subprocess,json,io
P=Path(__file__).resolve().parent
F='/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffmpeg'
for ep in [10,11]:
 A=json.loads((P/f'EP{ep}_video_inventory.json').read_text())
 for i,a in enumerate(A):
  dur=eval(a['duration'][:-1]);ts=[min(dur-.2,t) for t in [0,2,4,6,8,10,12,14]]
  sheet=Image.new('RGB',(8*180,350),(30,30,30));d=ImageDraw.Draw(sheet)
  for n,t in enumerate(ts):
   r=subprocess.run([F,'-v','error','-ss',str(t),'-i',a['path'],'-frames:v','1','-vf','scale=180:320','-f','image2pipe','-vcodec','png','-'],capture_output=True,check=True)
   im=Image.open(io.BytesIO(r.stdout));sheet.paste(im,(n*180,20));d.text((n*180+5,3),f'{i+1} / {t:.2f}s',fill='white')
  sheet.save(P/f'素材联系_EP{ep}_{i+1:02}.jpg')
 print('EP',ep,'sheets',len(A))
