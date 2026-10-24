from pathlib import Path
import json,re,subprocess,concurrent.futures,sys,math
import pymupdf
OUT=Path(__file__).parent
rows=json.loads((OUT/'footage.json').read_text())
specs=json.loads(sys.argv[1]);label=sys.argv[2]
sel=[]
for group,start,end,step in specs:
 for r in rows:
  if r['group']!=group:continue
  match=re.search(r'(?:_|^)[CD](\d+)',r['name']) or re.search(r'A\d+C(\d+)',r['name'])
  num=int(match.group(1))
  if start<=num<=end and (num-start)%step==0:sel.append(r)
def run(r):
 dest=OUT/'thumbs'/(r['key']+'_mid.jpg');tm=min(r['duration']*.5,15)
 subprocess.run(['/Users/xuan/.local/bin/ffmpeg','-v','error','-ss',str(tm),'-i',r['path'],'-frames:v','1','-vf','scale=256:-1','-y',str(dest)],capture_output=True)
 return r,dest,tm
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:res=list(ex.map(run,sel))
for start in range(0,len(res),40):
 doc=pymupdf.open();part=res[start:start+40];page=doc.new_page(width=1320,height=math.ceil(len(part)/5)*170)
 for k,(r,dest,tm) in enumerate(part):
  x=k%5*264;y=k//5*170
  if dest.exists():page.insert_image(pymupdf.Rect(x,y,x+256,y+144),filename=str(dest))
  page.insert_text((x+2,y+156),r['group']+'/'+r['name'].replace('_Proxy',''),fontsize=9)
  page.insert_text((x+2,y+167),f"{r['duration']:.1f}s  at {tm:.1f}s",fontsize=8)
 path=OUT/f'detail-{label}-{start//40+1}.jpg';page.get_pixmap().save(path);print(path)
