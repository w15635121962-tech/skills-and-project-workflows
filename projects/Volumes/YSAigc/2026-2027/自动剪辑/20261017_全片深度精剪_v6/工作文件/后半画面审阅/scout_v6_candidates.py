from pathlib import Path
import json,subprocess,concurrent.futures
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).parent
V5=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_开篇向往感精修_v5/工作文件/opening_plan_v5.json')
plan=json.loads(V5.read_text())
C=[]
for c in json.loads((O/'candidate_probes.json').read_text()):
 d=dict(c);d['id']='新候选_'+Path(c['path']).stem;d['times']=[1.04,3.5,5.92];C.append(d)
for rec in [5035,5157,5435,6370,9752]:
 s=next(s for s in plan['shots'] if s['record_frame']==rec)
 C.append({'id':f'原用段_{rec}','path':s['path'],'times':[s['in']+.04,(s['in']+s['out'])/2,s['out']-.08]})

def f(c):
 c=dict(c);log=O/(c['id']+'.log.json')
 if log.exists():r=json.loads(log.read_text())
 else:
  args=['python3','/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts/look.py',c['path'],'-o',str(O/(c['id']+'.png')),'--no-timecode','--json']
  for t in c['times']:args+=['--at',f'{t:.3f}']
  p=subprocess.run(args,capture_output=True,text=True);log.write_text(p.stdout)
  if p.returncode:raise RuntimeError(p.stdout+p.stderr)
  r=json.loads(p.stdout)
 c['frames']=r['outputs'];return c
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:R=list(ex.map(f,C))
font=ImageFont.truetype('/System/Library/Fonts/Hiragino Sans GB.ttc',20)
for n in range(0,len(R),5):
 sub=R[n:n+5];im=Image.new('RGB',(1536,len(sub)*342),(22,25,28));dr=ImageDraw.Draw(im)
 for row,c in enumerate(sub):
  y=row*342;dr.text((8,y+1),c['id']+' '+Path(c['path']).name,font=font,fill='white')
  for col,p in enumerate(c['frames']):
   x=Image.open(p).convert('RGB');x.thumbnail((508,286));im.paste(x,(col*512,y+30));dr.text((col*512+8,y+315),f"源{c['times'][col]:.3f}s",font=font,fill='white')
 im.save(O/f'新候选与原用段首中末_{n//5+1:02d}.jpg',quality=90)
(O/'scout_evidence.json').write_text(json.dumps(R,ensure_ascii=False,indent=2))
print('scouted',len(R))
