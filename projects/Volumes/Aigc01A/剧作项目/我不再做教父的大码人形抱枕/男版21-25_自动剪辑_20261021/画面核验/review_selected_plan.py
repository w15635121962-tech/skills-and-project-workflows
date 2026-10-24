import json,pathlib,subprocess,math
from PIL import Image,ImageDraw,ImageFont
B=pathlib.Path(__file__).resolve().parent;D=json.loads((B.parent/'男版素材盘点.json').read_text());vs={v['filename']:v for e in D['episodes'] for v in e['videos']}
ff='/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffmpeg';font=ImageFont.truetype('/Users/zc/Library/Fonts/NotoSansHans-Black.otf',16);out=B/'plan_review';out.mkdir(exist_ok=True)
for name in ['男版21-4-1.mp4','男版21-4-2.mp4','男版21-6-1.mp4','男版21-6-2.mp4','男版21-7-1.mp4','男版22-1-1.mp4','男版23-6-1.mp4','男版23-6-2.mp4']:
 v=vs[name];dur=float(v['video_streams'][0]['duration']);ts=[i+.25 for i in range(math.floor(dur))];W=160;H=284;rh=309;im=Image.new('RGB',(5*W,40+math.ceil(len(ts)/5)*rh),'white');dr=ImageDraw.Draw(im);dr.text((3,3),name,font=font,fill='black')
 for j,t in enumerate(ts):
  dest=out/f'{name[:-4]}_{t:.2f}.jpg'
  subprocess.run([ff,'-v','error','-ss',str(t),'-i',v['path'],'-frames:v','1','-vf','scale=160:-2','-q:v','2','-y',str(dest)],capture_output=True,check=True)
  x=(j%5)*W;y=40+(j//5)*rh;im.paste(Image.open(dest),(x,y));dr.text((x,y+H),f'{t:.2f}s',font=font,fill='black')
 im.save(out/f'{name[:-4]}_1fps.jpg',quality=94);print(name,flush=True)
