import json,subprocess,concurrent.futures
from pathlib import Path
B=Path('/Volumes/YSAigc/2026-2027/自动剪辑');O=B/'20261017_镜头节奏与开篇重剪_v7/工作文件/中段加密';C=json.loads((B/'20261017_学校粗剪/工作文件/footage.json').read_text());L='/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts/look.py'
req=[('001','C0008'),('003','A003C139'),('006','C0305'),('006','C0316'),('005','D0569'),('006','C0235'),('006','C0241')]
def run(gt):
 g,t=gt;f=next(f for f in C if f['group']==g and any(f['name'].startswith(s) for s in [t+'_','20260924_'+t+'_','20260921_'+t+'_']));cmd=['python3',L,f['path'],'--tiles','4x2','--width','1600','-o',str(O/f'全段查窗_{g}_{t}.png'),'--json','--overwrite'];r=subprocess.run(cmd,capture_output=True,text=True);(O/f'全段查窗_{g}_{t}.log').write_text(r.stdout+r.stderr);assert not r.returncode;return {'group':g,'code':t,'path':f['path'],'duration':f['duration']}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as p:r=list(p.map(run,req))
(O/'adjustment_candidates.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(len(r))
