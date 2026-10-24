import json,subprocess,io,concurrent.futures
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
W=Path(__file__).parent
F=json.loads(Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_学校粗剪/工作文件/footage.json').read_text())
choices=[('006_C0182',2.0),('006_C0206',1.0),('006_C0223',8.0),('006_C0250',2.0),('006_C0272',2.0),('006_C0275',5.0),('006_C0280',6.0),('006_C0281',5.0),('006_C0290',4.0),('006_C0296',5.0),('003_A003C178',2.0),('003_A003C182',2.0),('003_A003C184',3.0),('003_A003C214',2.0),('004_A001C230',2.0),('004_A001C232',2.0),('004_A001C075',2.0),('004_A001C077',2.0),('004_A001C320',1.0),('004_A001C322',1.0),('005_20260921_D0499',2.0),('005_20260921_D0500',2.0),('005_20260921_D0559',2.0),('005_20260921_D0570',2.0),('005_20260921_D0578',2.0),('007_C0035',5.0),('007_C0068',2.0),('007_C0069',2.0),('007_C0084',3.0),('007_C0104',4.0),('007_C0110',2.0),('002_A002C002',2.0),('002_A002C010',2.0),('006_C0329',3.0)]
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16)
items=[]
for prefix,start in choices:
 matches=[x for x in F if x['key'].startswith(prefix+'_')]
 if len(matches)!=1: print('SKIP',prefix,len(matches));continue
 x=matches[0];x=dict(x);x['scout_id']=prefix;start=min(start,max(0,float(x['video'].get('duration',x['duration']))-2.44));x['times']=[start,start+1.16,start+2.28];items.append(x)
def make(x):
 pr=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',x['path']]))
 x['current_probe']=pr
 tiles=[]
 for t in x['times']:
  b=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',x['path'],'-frames:v','1','-vf','scale=360:203','-f','image2pipe','-vcodec','mjpeg','-threads','1','-'])
  
  if not b: print('EMPTY',x['scout_id'],t,x['duration'],flush=True); im=Image.new('RGB',(360,203),'red')
  else: im=Image.open(io.BytesIO(b)).convert('RGB')
  q=W/(x['scout_id']+'_'+str(t)+'.jpg');im.save(q,quality=90);tiles.append(im);
 row=Image.new('RGB',(1080,230),'white');d=ImageDraw.Draw(row)
 for i,im in enumerate(tiles):row.paste(im,(i*360,0));d.text((i*360+4,205),x['scout_id']+' @'+str(x['times'][i])+'s',font=font,fill='black')
 return x,row
results=list(concurrent.futures.ThreadPoolExecutor(max_workers=4).map(make,items))
for page in range((len(results)+7)//8):
 sub=results[page*8:(page+1)*8];sheet=Image.new('RGB',(1080,len(sub)*230),'white')
 for i,(_,r) in enumerate(sub):sheet.paste(r,(0,i*230))
 sheet.save(W/('candidate_scout_%02d.jpg'%(page+1)),quality=92)
(W/'candidate_scout.json').write_text(json.dumps([x for x,r in results],ensure_ascii=False,indent=2))
print('scouted',len(results))
