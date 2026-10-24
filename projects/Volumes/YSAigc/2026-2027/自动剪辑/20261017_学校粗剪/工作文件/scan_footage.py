from pathlib import Path
import subprocess,json,concurrent.futures,math
import pymupdf
ROOT=Path('/Volumes/YSAigc/2026-2027/文汇中学/拍摄素材转码')
OUT=Path(__file__).parent
(OUT/'thumbs').mkdir(exist_ok=True)
files=sorted(p for p in ROOT.rglob('*') if p.suffix.lower() in ['.mov','.mp4'] and not p.name.startswith('._'))
sample=set()
for group in sorted(ROOT.iterdir()):
 fs=[p for p in files if p.relative_to(ROOT).parts[0]==group.name]
 sample.update(fs[::6]);sample.update(fs[-1:])
def run(p):
 group=p.relative_to(ROOT).parts[0]
 key=group+'_'+p.stem
 proc=subprocess.run(['/Users/xuan/.local/bin/ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)],capture_output=True,text=True)
 d=json.loads(proc.stdout);v=next(s for s in d['streams'] if s['codec_type']=='video')
 fps=eval(v['r_frame_rate'],{'__builtins__':{}})
 row={'key':key,'group':group,'path':str(p),'name':p.name,'duration':float(d['format']['duration']),'fps':fps,'video':v,'audio':[s for s in d['streams'] if s['codec_type']=='audio']}
 if p in sample:
  dest=OUT/'thumbs'/(key+'.jpg');tm=min(row['duration']*.4,5)
  subprocess.run(['/Users/xuan/.local/bin/ffmpeg','-v','error','-ss',str(tm),'-i',str(p),'-frames:v','1','-vf','scale=256:-1','-y',str(dest)],capture_output=True)
  row['thumb']=str(dest);row['thumb_time']=tm
 return row
rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
 for i,row in enumerate(ex.map(run,files)):
  rows.append(row)
  if (i+1)%200==0:print('SCANNED',i+1,flush=True)
(OUT/'footage.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
for group in sorted(set(r['group'] for r in rows)):
 rs=[r for r in rows if r['group']==group and 'thumb' in r]
 for start in range(0,len(rs),40):
  part=rs[start:start+40];doc=pymupdf.open();page=doc.new_page(width=1320,height=math.ceil(len(part)/5)*170)
  for k,row in enumerate(part):
   x=k%5*264;y=k//5*170
   try:page.insert_image(pymupdf.Rect(x,y,x+256,y+144),filename=row['thumb'])
   except Exception:pass
   label=row['name'].replace('_Proxy','')
   page.insert_text((x+2,y+156),label,fontsize=9)
   page.insert_text((x+2,y+167),f"{row['duration']:.1f}s / {row['fps']:g}fps",fontsize=8)
  dest=OUT/f"overview-{group}-{start//40+1}.jpg";page.get_pixmap().save(dest);print(dest,flush=True)
print('TOTAL',len(rows),'MINUTES',sum(r['duration'] for r in rows)/60,'SAMPLES',len(sample),flush=True)
