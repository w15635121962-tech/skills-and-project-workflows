import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'工作文件'
sys.path.insert(0,'/Volumes/YSAigc/2026-2027/自动剪辑/20261017_图片动态底板精修_v13/工作文件')
from common_v13 import snap,graphs,get_resolve
before=json.loads((OUT/'live_before_v14.json').read_text());r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p and p.GetName()==before['project'];t=p.GetCurrentTimeline();assert t.GetName()==before['timeline'] and snap(t)==before['snapshot'];assert graphs(t)==before['graphs'];assert pm.SaveProject()
assert t.Export(str(ROOT/'学校_缓推气口调整前_v13备份.drt'),r.EXPORT_DRT);assert pm.ExportProject(p.GetName(),str(ROOT/'学校_缓推气口调整前_完整工程备份.drp'))
name='学校_画面缓推与旁白气口精修_v14_20261017';assert name not in [p.GetTimelineByIndex(i).GetName() for i in range(1,p.GetTimelineCount()+1)];new=t.DuplicateTimeline(name);assert new and p.SetCurrentTimeline(new);assert snap(new)==before['snapshot'] and graphs(new)==before['graphs'];assert pm.SaveProject();print('V14_PREPARED',name,flush=True)
