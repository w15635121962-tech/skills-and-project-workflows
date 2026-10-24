import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common_v12 import *
r,pm,p,mp,t=connect();assert t.GetName()==TIMELINE;assert pm.SaveProject();assert t.SetName('学校_恢复检查_旧导出备份_v12')
latest=mp.ImportTimelineFromFile(str(ROOT/'学校_曲线二级精调前_v11备份.drt'),{'timelineName':'学校_本轮开始前完整保留_v11_20261017'});assert latest;assert latest.SetName('学校_本轮开始前完整保留_v11_20261017') and p.SetCurrentTimeline(latest)
before=json.loads((OUT/'live_before_v12.json').read_text());assert snap(latest)==before['snapshot'];it=next(x for x in latest.GetItemListInTrack('video',1) if x.GetStart()==117);print('LATEST_117_TOOLS',it.GetNodeGraph().GetToolsInNode(1),flush=True);assert '自定义曲线' in it.GetNodeGraph().GetToolsInNode(1)
new=latest.DuplicateTimeline(TIMELINE);assert new and p.SetCurrentTimeline(new);assert snap(new)==before['snapshot'];assert r.OpenPage('edit');assert pm.SaveProject();print('LATEST_USER_GRADES_AND_TIMELINE_RESTORED',flush=True)
