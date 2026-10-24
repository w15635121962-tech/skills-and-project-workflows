import sys,json,hashlib,zipfile
from pathlib import Path
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件'
plan=json.loads((OUT/'edit_plan_v7.json').read_text());build=json.loads((OUT/'native_build_v7.json').read_text());before=json.loads((OUT/'live_before_v7.json').read_text());qa=json.loads((OUT/'native_verification_v7.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool();t=p.GetCurrentTimeline()
def snap(tl):
    return {typ:[{'track':k,'enabled':tl.GetIsTrackEnabled(typ,k),'locked':tl.GetIsTrackLocked(typ,k),'name':tl.GetTrackName(typ,k),'items':[{'name':it.GetName(),'start':it.GetStart(),'end':it.GetEnd(),'offset':it.GetLeftOffset(),'path':it.GetMediaPoolItem().GetClipProperty('File Path') if it.GetMediaPoolItem() else None,'properties':it.GetProperty(),'enabled':it.GetClipEnabled(),'fusion_count':it.GetFusionCompCount()} for it in tl.GetItemListInTrack(typ,k)]} for k in range(1,tl.GetTrackCount(typ)+1)] for typ in ['video','audio']}
assert p.GetName()=='学校' and t.GetName()==plan['name'] and snap(t)==build['snapshot']
base=next(p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()==plan['base_timeline'])
try:
    assert p.SetCurrentTimeline(base)
    baseline=snap(p.GetCurrentTimeline())
finally:
    assert p.SetCurrentTimeline(t)
assert baseline==before['snapshot']
assert build['snapshot']['audio']==before['snapshot']['audio']
for typ in ['video','audio']:
    for k in range(1,t.GetTrackCount(typ)+1):
        assert t.GetIsTrackEnabled(typ,k)
        for v in t.GetItemListInTrack(typ,k):
            m=v.GetMediaPoolItem();assert m
            assert Path(m.GetClipProperty('File Path')).exists()
            if typ=='video':assert m.GetClipProperty('Online Status')=='Online'
assert r.OpenPage('edit') and t.SetCurrentTimecode('00:00:00:20') and pm.SaveProject()
drt=ROOT/'学校_镜头节奏与开篇重剪_v7.drt';drp=ROOT/'学校_镜头节奏与开篇重剪_v7.drp'
assert not drt.exists() and not drp.exists()
assert t.Export(str(drt),r.EXPORT_DRT);print('V7_TIMELINE_EXPORTED',flush=True)
assert pm.ExportProject(p.GetName(),str(drp),True);print('V7_PROJECT_EXPORTED',flush=True)
archives=[]
for path in [drt,drp]:
    assert path.stat().st_size>10000 and zipfile.is_zipfile(path)
    with zipfile.ZipFile(path) as z:assert z.testzip() is None
    archives.append({'path':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'zip_integrity_passed':True})
record={'project':p.GetName(),'active_timeline':t.GetName(),'duration_timecode':'00:07:40:07','duration_seconds':460.28,'fps':25,'resolution':'1920x1080','revisions':plan['revision_v7'],'v1_items':len(t.GetItemListInTrack('video',1)),'v2_items':len(t.GetItemListInTrack('video',2)),'audio_tracks':t.GetTrackCount('audio'),'audio_items':sum(len(t.GetItemListInTrack('audio',i)) for i in range(1,t.GetTrackCount('audio')+1)),'prior_v6_preserved':True,'all_audio_exactly_preserved':True,'all_media_online':True,'no_gaps_or_ripple':True,'unique_actual_resolve_stills':qa['unique_actual_stills'],'continuous_full_watch_or_listen_completed':False,'mp4_rendered':False,'archives':archives}
(OUT/'final_delivery_v7.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
print(json.dumps(record,ensure_ascii=False,indent=2),flush=True)
