import json,subprocess,concurrent.futures
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
B=Path('/Volumes/YSAigc/2026-2027/自动剪辑');O=B/'20261017_镜头节奏与开篇重剪_v7/工作文件/中段加密';C=json.loads((B/'20261017_学校粗剪/工作文件/footage.json').read_text());L='/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts/look.py'
req={'001':['C0008'],'002':['A002C013','A002C030','A002C038'],'003':['A003C021','A003C139'],'004':['A001C075','A001C114','A001C224'],'005':['D0375','D0379','D0437','D0441','D0445','D0504','D0566'],'006':['C0180','C0205','C0206','C0208','C0213','C0219','C0221','C0224','C0237','C0257','C0262','C0275','C0280','C0295','C0304','C0316']}
items=[]
for g,terms in req.items():
 for t in terms:
  fs=[f for f in C if f['group']==g and (f['name'].startswith(t+'_') or f['name'].startswith('20260924_'+t+'_') or f['name'].startswith('20260921_'+t+'_'))];assert len(fs)==1,(g,t,len(fs));items.append({'group':g,'code':t,'path':fs[0]['path'],'duration':fs[0]['duration'],'times':[1.04,2.34,3.64]})
def make(x):
 stem=f"scout_{x['group']}_{x['code']}";cmd=['python3',L,x['path']]
 for t in x['times']:cmd+=['--at',str(t)]
 cmd+=['-o',str(O/(stem+'.png')),'--no-timecode','--json','--overwrite'];r=subprocess.run(cmd,capture_output=True,text=True);(O/(stem+'.log')).write_text(r.stdout+r.stderr);assert r.returncode==0; x['frames']=[str(O/f'{stem}_{t:.3f}s.png') for t in x['times']];return x
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as p:items=list(p.map(make,items))
(O/'scout_candidates.json').write_text(json.dumps(items,ensure_ascii=False,indent=2));font=ImageFont.truetype('/System/Library/Fonts/Hiragino Sans GB.ttc',20)
for page in range((len(items)+4)//5):
 its=items[page*5:page*5+5];can=Image.new('RGB',(1440,306*len(its)),(25,25,25));d=ImageDraw.Draw(can)
 for row,x in enumerate(its):
  for col,fn in enumerate(x['frames']):
   im=Image.open(fn).convert('RGB');im.thumbnail((480,270));can.paste(im,(col*480,row*306+36));d.text((col*480+5,row*306+7),f"{x['group']} {x['code']} {x['times'][col]:.2f}s",font=font,fill='white')
 can.save(O/f'候选首中尾_{page+1:02d}.jpg',quality=91)
print(len(items))
