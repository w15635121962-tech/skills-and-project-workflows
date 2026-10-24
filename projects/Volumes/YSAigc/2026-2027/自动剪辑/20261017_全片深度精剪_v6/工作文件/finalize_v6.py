import sys,json,hashlib,zipfile
from pathlib import Path
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve

ROOT=Path(__file__).parents[1]
OUT=ROOT/'工作文件'
plan=json.loads((OUT/'deep_edit_plan_v6.json').read_text())
build=json.loads((OUT/'native_build_v6.json').read_text())
before=json.loads((OUT/'live_before_v6.json').read_text())
qa=json.loads((OUT/'native_verification_v6.json').read_text())
r=get_resolve()
pm=r.GetProjectManager()
p=pm.GetCurrentProject()
mp=p.GetMediaPool()
t=p.GetCurrentTimeline()
assert p.GetName()=='学校' and t.GetName()==plan['name']

def snap(timeline):
    return {typ:[{'track':k,'enabled':timeline.GetIsTrackEnabled(typ,k),'locked':timeline.GetIsTrackLocked(typ,k),'name':timeline.GetTrackName(typ,k),'items':[{'name':it.GetName(),'start':it.GetStart(),'end':it.GetEnd(),'offset':it.GetLeftOffset(),'path':it.GetMediaPoolItem().GetClipProperty('File Path') if it.GetMediaPoolItem() else None,'properties':it.GetProperty(),'enabled':it.GetClipEnabled(),'fusion_count':it.GetFusionCompCount()} for it in timeline.GetItemListInTrack(typ,k)]} for k in range(1,timeline.GetTrackCount(typ)+1)] for typ in ['video','audio']}

assert snap(t)==build['snapshot'],'v6 changed after build; review before exporting'
base=next(p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()==plan['base_timeline'])
# Track enabled/locked getters only report reliably for the active timeline.
try:
    assert p.SetCurrentTimeline(base)
    base_snapshot=snap(p.GetCurrentTimeline())
finally:
    assert p.SetCurrentTimeline(t)
assert base_snapshot==before['snapshot'],'v5 must remain untouched'
(OUT/'base_v5_final_snapshot.json').write_text(json.dumps(base_snapshot,ensure_ascii=False,indent=2))
assert build['snapshot']['audio']==before['snapshot']['audio']
assert len(t.GetItemListInTrack('video',1))==121
assert len(t.GetItemListInTrack('video',2))==4
assert t.GetEndFrame()-t.GetStartFrame()==11507
for track in range(1,t.GetTrackCount('video')+1):
    for v in t.GetItemListInTrack('video',track):
        m=v.GetMediaPoolItem()
        assert m and m.GetClipProperty('Online Status')=='Online'
        assert Path(m.GetClipProperty('File Path')).exists()

assert r.OpenPage('edit')
assert t.SetCurrentTimecode('00:00:00:20')
assert pm.SaveProject()
drt=ROOT/'学校_全片深度精剪_v6.drt'
drp=ROOT/'学校_全片深度精剪_v6.drp'
assert not drt.exists() and not drp.exists(),'Never overwrite delivery archives'
assert t.Export(str(drt),r.EXPORT_DRT)
print('V6_TIMELINE_EXPORTED',flush=True)
assert pm.ExportProject(p.GetName(),str(drp),True)
print('V6_PROJECT_EXPORTED',flush=True)

archives=[]
for path in [drt,drp]:
    assert path.stat().st_size>10000 and zipfile.is_zipfile(path)
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        members=z.namelist()
    archives.append({'path':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'zip_integrity_passed':True,'archive_members':members})

samples=qa['midpoint_frames']+qa['revised_picture_triplets']+qa['interview_cutaway_samples']+qa['caption_samples']+qa['boundary_samples']
unique_frames={x['path'] for x in samples}
assert all(Path(x).exists() for x in unique_frames)
record={'project':p.GetName(),'active_timeline':t.GetName(),'duration_seconds':460.28,'duration_timecode':'00:07:40:07','timeline_fps':25,'resolution':'1920x1080','picture_items':121,'video_tracks':2,'audio_tracks':4,'revised_picture_groups':20,'interview_cutaways':2,'prior_v5_preserved':True,'all_audio_exactly_preserved':True,'native_snapshot_matches_completed_build':True,'all_picture_media_online':True,'unique_actual_resolve_stills':len(unique_frames),'continuous_full_watch_or_listen_completed':False,'mp4_rendered':False,'archives':archives}
(OUT/'final_delivery_v6.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in record.items() if k!='archives'},ensure_ascii=False),flush=True)
print('V6_FINAL_DELIVERY_READY',flush=True)
