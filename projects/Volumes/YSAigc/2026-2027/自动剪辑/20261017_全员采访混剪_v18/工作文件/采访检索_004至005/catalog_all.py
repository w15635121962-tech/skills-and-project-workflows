import json,pathlib,concurrent.futures,av
from PIL import Image,ImageDraw,ImageFont
ROOT=pathlib.Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_全员采访混剪_v18/工作文件/采访检索_004至005');ROOT.mkdir(exist_ok=True,parents=True);(ROOT/'mid').mkdir(exist_ok=True)
D=json.loads(pathlib.Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_学校粗剪/工作文件/footage.json').read_text());A=[x for x in D if x['group'] in ['004','005']]
def one(x):
 out=ROOT/'mid'/(x['key']+'.jpg')
 if out.exists():return
 with av.open(x['path']) as c:
  s=c.streams.video[0];s.thread_type='AUTO';s.thread_count=1;t=x['duration']*.5;c.seek(int(t/s.time_base),stream=s,backward=True)
  for f in c.decode(s):
   if float(f.time)>=t-.08:
    f.to_image().resize((320,180)).save(out,quality=85);return
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(one,A))
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16)
for g in ['004','005']:
 a=[x for x in A if x['group']==g]
 for off in range(0,len(a),60):
  sub=a[off:off+60];im=Image.new('RGB',(1920,((len(sub)+5)//6)*205),'#222222');d=ImageDraw.Draw(im)
  for i,x in enumerate(sub):
   p=ROOT/'mid'/(x['key']+'.jpg')
   if p.exists():im.paste(Image.open(p),((i%6)*320,(i//6)*205))
   label=x['name'].split('_26')[0].replace('_Proxy.mov','').replace('20260921_','');d.text(((i%6)*320,(i//6)*205+180),label+' '+str(round(x['duration']))+'s',font=font,fill='white')
  im.save(ROOT/f'{g}_full_{off:03d}.jpg')
print('DONE',len(A))
