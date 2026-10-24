from pathlib import Path
import concurrent.futures, json, subprocess
from PIL import Image, ImageDraw, ImageFont

OUT=Path(__file__).parent
BASE=Path('/Volumes/YSAigc/2026-2027/文汇中学')
PROXY=BASE/'拍摄素材转码'
CANDIDATES=[
 {'id':'75_live_handwork','path':str(PROXY/'004/Proxies/A001C319_2609216R_Proxy.mov'),'start':2.0,'duration':3.72,'target_index':75,'record_frame':7211,'length_frames':93},
 {'id':'81_live_teacher','path':str(PROXY/'006/Proxies/C0192_Proxy.mov'),'start':8.0,'duration':3.8,'target_index':81,'record_frame':7840,'length_frames':95},
 {'id':'85_complete_salute','path':str(PROXY/'004/Proxies/A001C092_2609218H_Proxy.mov'),'start':3.4,'duration':2.56,'target_index':85,'record_frame':8220,'length_frames':64},
 {'id':'102_live_english','path':str(PROXY/'006/Proxies/C0234_Proxy.mov'),'start':3.0,'duration':5.0,'target_index':102,'record_frame':9627,'length_frames':125},
 {'id':'106_courtyard_group','path':str(BASE/'学校素材资料/2-集团发展与历史档案素材/4集团研讨/MAH01146.MP4'),'start':7.6,'duration':4.24,'target_index':106,'record_frame':10056,'length_frames':106},
 {'id':'110_clean_ceremony_C0055','path':str(PROXY/'007/Proxies/C0055_Proxy.mov'),'start':2.0,'duration':5.2,'target_index':110,'record_frame':10492,'length_frames':130},
 {'id':'110_clean_ceremony_C0067','path':str(PROXY/'007/Proxies/C0067_Proxy.mov'),'start':4.0,'duration':5.2,'target_index':110,'record_frame':10492,'length_frames':130},
 {'id':'110_clean_ceremony_C0103','path':str(PROXY/'007/Proxies/C0103_Proxy.mov'),'start':5.0,'duration':5.2,'target_index':110,'record_frame':10492,'length_frames':130},
]

def extract(c):
 times=[c['start']+.04,c['start']+c['duration']/2,c['start']+c['duration']-.08]
 args=['python3','/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts/look.py',c['path'],'-o',str(OUT/(c['id']+'.png')),'--no-timecode','--json']
 for t in times:args+=['--at',str(t)]
 log=OUT/(c['id']+'.log.json')
 if log.exists() and json.loads(log.read_text()).get('status')=='completed':
  parsed=json.loads(log.read_text())
 else:
  p=subprocess.run(args,capture_output=True,text=True)
  log.write_text(p.stdout)
  if p.returncode:raise RuntimeError(p.stdout+p.stderr)
  parsed=json.loads(p.stdout)
 c=dict(c);c['frames']=parsed['outputs'];c['times']=times
 return c

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 result=list(ex.map(extract,CANDIDATES))
font=ImageFont.truetype('/System/Library/Fonts/Hiragino Sans GB.ttc',20)
for i in range(0,len(result),4):
 part=result[i:i+4];can=Image.new('RGB',(1536,len(part)*346),(24,24,28));draw=ImageDraw.Draw(can)
 for j,c in enumerate(part):
  y=j*346;draw.text((6,y+2),c['id']+' '+Path(c['path']).name+' '+str(c['start'])+'–'+str(c['start']+c['duration']),font=font,fill='white')
  for k,f in enumerate(c['frames']):
   im=Image.open(f).convert('RGB');im.thumbnail((508,286));can.paste(im,(k*512,y+32));draw.text((k*512+8,y+317),str(c['times'][k]),font=font,fill='white')
 can.save(OUT/f'替换候选首中末_{i//4+1:02d}.jpg',quality=88)
(OUT/'replacement_scout.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print('scouted',len(result))
