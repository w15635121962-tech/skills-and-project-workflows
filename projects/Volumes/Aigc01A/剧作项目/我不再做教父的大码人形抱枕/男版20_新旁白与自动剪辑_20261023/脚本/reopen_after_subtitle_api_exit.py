from native_common import *
import sys
sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
r=get_resolve();m=r.GetProjectManager();p=m.GetCurrentProject()
if p and p.GetName()=='Untitled Project':
 assert p.GetTimelineCount()==0
if not p or p.GetName()!=PROJECT:p=m.LoadProject(PROJECT)
assert p and p.GetName()==PROJECT
row=read(BASE/'Resolve_组装实读.json')['episodes'][0]
t=next(t for t in timelines(p) if t.GetUniqueId()==row['id']);assert t.GetName()==TIMELINE and p.SetCurrentTimeline(t)
actual=[]
for i in range(1,t.GetTrackCount('subtitle')+1):
 for x in t.GetItemListInTrack('subtitle',i) or []:actual.append([x.GetStart(),x.GetEnd(),x.GetName()])
report={'project':p.GetName(),'timeline_count':p.GetTimelineCount(),'timeline_id':t.GetUniqueId(),'timeline':t.GetName(),'av_counts':[len(t.GetItemListInTrack('video',1) or []),len(t.GetItemListInTrack('audio',1) or []),len(t.GetItemListInTrack('audio',2) or [])],'duration':t.GetEndFrame(),'subtitles':actual,'subtitle_tracks':t.GetTrackCount('subtitle')}
write(BASE/'诊断/字幕接口退出后重开实读.json',report);print(json.dumps(report,ensure_ascii=False))
