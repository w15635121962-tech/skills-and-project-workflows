import json,subprocess,io,concurrent.futures
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
W=Path(__file__).parent
G=json.loads((W/'groups_v7.json').read_text());S=[s for g in G for s in g['segments']]
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16)
unique=list(dict.fromkeys(s['path'] for s in S))
def probe(p):
 z=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',p]));return p,z
probes=dict(concurrent.futures.ThreadPoolExecutor(max_workers=4).map(probe,unique))
(W/'final_source_probes_v7.json').write_text(json.dumps(probes,ensure_ascii=False,indent=2))
def make(s):
 v=next(v for v in probes[s['path']]['streams'] if v['codec_type']=='video')
 assert float(v.get('duration',probes[s['path']]['format']['duration']))+0.04>=s['out'],(s['path'],s['out'])
 first=s['source_start_frame'];count=s['source_count_frames'];fr=[first,first+(count-1)//2,first+count-1];times=[f/s['fps'] for f in fr]
 tiles=[];paths=[]
 for t in times:
  b=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',s['path'],'-frames:v','1','-vf','scale=360:203','-f','image2pipe','-vcodec','mjpeg','-threads','1','-']);assert b,(s['path'],t)
  im=Image.open(io.BytesIO(b)).convert('RGB');q=W/('final_%05d_%.3fs.jpg'%(s['record_frame'],t));im.save(q,quality=93);tiles.append(im);paths.append(str(q))
 row=Image.new('RGB',(1080,230),'white');d=ImageDraw.Draw(row)
 for i,im in enumerate(tiles):row.paste(im,(i*360,0));d.text((i*360+3,205),'F%s %s @%.2fs'%(s['record_frame'],Path(s['path']).name[:24],times[i]),font=font,fill='black')
 s['evidence']={'first_middle_last_viewed':False,'source_times_seconds':times,'source_frames':fr,'frames':paths,'duration_seconds':s['length_frames']/25,'probe_verified':True}
 return row
rows=list(concurrent.futures.ThreadPoolExecutor(max_workers=4).map(make,S))
for page in range((len(rows)+5)//6):
 sub=rows[page*6:(page+1)*6];sheet=Image.new('RGB',(1080,len(sub)*230),'white')
 for i,row in enumerate(sub):sheet.paste(row,(0,i*230))
 sheet.save(W/('final_evidence_%02d.jpg'%(page+1)),quality=94)
(W/'groups_v7.json').write_text(json.dumps(G,ensure_ascii=False,indent=2));print('FINAL',len(rows),'segments',len(unique),'sources',(len(rows)+5)//6,'sheets')
