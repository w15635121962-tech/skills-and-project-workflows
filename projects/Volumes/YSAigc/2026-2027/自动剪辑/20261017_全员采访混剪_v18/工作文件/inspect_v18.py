import sys,json,time
from pathlib import Path
sys.path.insert(0,'/Volumes/YSAigc/2026-2027/自动剪辑/20261017_片尾第三轨大方选镜_v17/工作文件')
from common_v17 import get_resolve,snap,graphs
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'工作文件'
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p and p.GetName()=='学校_曲线二级精修_v12'
t=p.GetCurrentTimeline();assert t
before={'project':p.GetName(),'timeline':t.GetName(),'snapshot':snap(t),'fps':t.GetSetting('timelineFrameRate'),'width':t.GetSetting('timelineResolutionWidth'),'height':t.GetSetting('timelineResolutionHeight'),'start':t.GetStartFrame(),'end':t.GetEndFrame(),'playhead':t.GetCurrentTimecode(),'page':r.GetCurrentPage()}
assert not (OUT/'live_before_v18.json').exists()
(OUT/'live_before_v18.json').write_text(json.dumps(before,ensure_ascii=False,indent=2))
(OUT/'live_graphs_before_v18.json').write_text(json.dumps(graphs(t),ensure_ascii=False,indent=2))
assert pm.SaveProject();assert pm.ExportProject(p.GetName(),str(OUT/'本轮修改前工程备份.drp'))
print(json.dumps({k:v for k,v in before.items() if k!='snapshot'},ensure_ascii=False))
for kind in ['video','audio']:
 for tr in before['snapshot'][kind]:
  print(kind,tr['track'],tr.get('name'),len(tr['items']))
  if kind=='audio':
   print(json.dumps(tr,ensure_ascii=False))
