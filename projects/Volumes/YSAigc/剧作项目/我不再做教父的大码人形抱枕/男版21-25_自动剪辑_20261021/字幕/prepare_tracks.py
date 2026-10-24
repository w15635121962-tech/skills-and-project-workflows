import json,sys
from pathlib import Path
sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
OUT=Path(__file__).resolve().parent
baseline=json.loads((OUT/'Resolve_字幕操作前完整基线.json').read_text(encoding='utf-8'))
assert Path(baseline['backup']['path']).stat().st_size>0
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='大码枕头'
ts={p.GetTimelineByIndex(i).GetName():p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)}
original=p.GetCurrentTimeline()
def av(t):
    return {kind:[{'track':j,'name':t.GetTrackName(kind,j),'enabled':t.GetIsTrackEnabled(kind,j),
                  'items':[{'id':x.GetUniqueId(),'start':x.GetStart(),'end':x.GetEnd(),
                  'source_start':x.GetSourceStartFrame(),'source_end':x.GetSourceEndFrame(),'properties':x.GetProperties(),
                  'path':x.GetMediaPoolItem().GetClipProperty('File Path')} for x in t.GetItemListInTrack(kind,j) or []]}
                  for j in range(1,t.GetTrackCount(kind)+1)] for kind in ['video','audio']}
report=[]
for ep in range(21,26):
    name=f'大码_男版_EP{ep}_原速旁白_自动剪辑_v1';t=ts[name]
    assert p.SetCurrentTimeline(t) and p.GetCurrentTimeline().GetUniqueId()==t.GetUniqueId()
    before=av(t);count=t.GetTrackCount('subtitle')
    assert count in [0,1]
    if count==0:assert t.AddTrack('subtitle')
    assert t.GetTrackCount('subtitle')==1
    assert not (t.GetItemListInTrack('subtitle',1) or []),'Existing captions must be checked rather than overwritten'
    named=t.SetTrackName('subtitle',1,str(ep));assert t.GetTrackName('subtitle',1)==str(ep)
    enabled=t.SetTrackEnable('subtitle',1,True)
    if not t.GetIsTrackEnabled('subtitle',1):
        assert t.SetTrackEnable('subtitle',1,True)
    assert t.GetIsTrackEnabled('subtitle',1)
    assert av(t)==before
    report.append({'ep':ep,'timeline':name,'id':t.GetUniqueId(),'track_name':t.GetTrackName('subtitle',1),'cue_count':0,'av_unchanged':True})
assert p.SetCurrentTimeline(original);assert pm.SaveProject()
(OUT/'字幕轨_创建回读.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False),flush=True)
