import json,subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
B=Path('/Volumes/YSAigc/2026-2027/自动剪辑');O=B/'20261017_镜头节奏与开篇重剪_v7/工作文件/中段加密';C=json.loads((B/'20261017_学校粗剪/工作文件/footage.json').read_text());L='/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts/look.py';F=ImageFont.truetype('/System/Library/Fonts/Hiragino Sans GB.ttc',20);can=Image.new('RGB',(1440,612),(25,25,25));d=ImageDraw.Draw(can)
for row,code in enumerate(['A003C130','A003C136']):
 f=next(x for x in C if x['group']=='003' and x['name'].startswith(code+'_'));cmd=['python3',L,f['path']]
 for t in [1.04,2.34,3.64]:cmd+=['--at',str(t)]
 prefix=O/('scout_003_'+code+'.png');cmd+=['-o',str(prefix),'--no-timecode','--json','--overwrite'];r=subprocess.run(cmd,capture_output=True,text=True);(O/(code+'_look.log')).write_text(r.stdout+r.stderr);assert r.returncode==0
 for col,t in enumerate([1.04,2.34,3.64]):
  im=Image.open(O/f'scout_003_{code}_{t:.3f}s.png');im.thumbnail((480,270));can.paste(im,(480*col,306*row+36));d.text((480*col+5,306*row+7),f'{code} {t}',font=F,fill='white')
can.save(O/'图书馆替代首中尾.jpg',quality=92)
