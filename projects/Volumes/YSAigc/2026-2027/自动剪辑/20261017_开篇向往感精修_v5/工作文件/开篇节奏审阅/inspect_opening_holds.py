from pathlib import Path
import json,subprocess,concurrent.futures
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).parent
B=Path('/Volumes/YSAigc/2026-2027/文汇中学/拍摄素材转码')
C=[
 {'id':'古树庭院_开场候选','path':str(B/'004/Proxies/A001C049_260921K6_Proxy.mov'),'in':9.4,'duration':4.68},
 {'id':'师生辅导_延长候选','path':str(B/'003/Proxies/A003C097_260924S5_Proxy.mov'),'in':4.56,'duration':5.04},
 {'id':'翻书_长停留备选','path':str(B/'003/Proxies/A003C139_260924UW_Proxy.mov'),'in':7.0,'duration':4.68},
 {'id':'阅读学生_长停留备选','path':str(B/'003/Proxies/A003C133_26092422_Proxy.mov'),'in':0.8,'duration':4.68},
 {'id':'专注学生_长停留备选','path':str(B/'006/Proxies/C0210_Proxy.mov'),'in':7.4,'duration':6.36},
 {'id':'师生围读_延长备选','path':str(B/'003/Proxies/A003C205_26092428_Proxy.mov'),'in':13.0,'duration':5.04},
 {'id':'实验动作_提前入点备选','path':str(B/'002/Proxies/A002C043_260924B8_Proxy.mov'),'in':1.4,'duration':2.68},
]
def f(c):
 c=dict(c);ts=[c['in']+.04,c['in']+c['duration']/2,c['in']+c['duration']-.08]
 args=['python3','/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts/look.py',c['path'],'-o',str(O/(c['id']+'.png')),'--no-timecode','--json']
 for t in ts:args+=['--at',f'{t:.3f}']
 p=subprocess.run(args,capture_output=True,text=True);(O/(c['id']+'.log.json')).write_text(p.stdout)
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 c['frames']=json.loads(p.stdout)['outputs'];c['times']=ts;return c
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:R=list(ex.map(f,C))
font=ImageFont.truetype('/System/Library/Fonts/Hiragino Sans GB.ttc',20)
for n in range(0,len(R),4):
 sub=R[n:n+4];im=Image.new('RGB',(1536,len(sub)*345),(22,25,28));dr=ImageDraw.Draw(im)
 for i,c in enumerate(sub):
  y=i*345;dr.text((8,y+1),c['id']+' '+Path(c['path']).name+f" 源{c['in']:.2f}–{c['in']+c['duration']:.2f}",font=font,fill='white')
  for k,f in enumerate(c['frames']):
   p=Image.open(f).convert('RGB');p.thumbnail((508,286));im.paste(p,(k*512,y+32));dr.text((k*512+8,y+317),f"源{c['times'][k]:.3f}s",font=font,fill='white')
 im.save(O/f'开篇长停留候选首中末_{n//4+1:02d}.jpg',quality=90)
(O/'opening_candidate_evidence.json').write_text(json.dumps(R,ensure_ascii=False,indent=2))
print('evidence_ready',len(R))
