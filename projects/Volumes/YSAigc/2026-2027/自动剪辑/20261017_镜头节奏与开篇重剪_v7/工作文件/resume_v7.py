import sys,json
from pathlib import Path
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件'
plan=json.loads((OUT/'edit_plan_v7.json').read_text());groups=json.loads((OUT/'native_changes_v7.json').read_text());before=json.loads((OUT/'live_before_v7.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool();t=p.GetCurrentTimeline();assert p.GetName()=='学校' and t.GetName()==plan['name']
def snap(t):
    return {typ:[{'track':k,'enabled':t.GetIsTrackEnabled(typ,k),'locked':t.GetIsTrackLocked(typ,k),'name':t.GetTrackName(typ,k),'items':[{'name':it.GetName(),'start':it.GetStart(),'end':it.GetEnd(),'offset':it.GetLeftOffset(),'path':it.GetMediaPoolItem().GetClipProperty('File Path') if it.GetMediaPoolItem() else None,'properties':it.GetProperty(),'enabled':it.GetClipEnabled(),'fusion_count':it.GetFusionCompCount()} for it in t.GetItemListInTrack(typ,k)]} for k in range(1,t.GetTrackCount(typ)+1)] for typ in ['video','audio']}
vs=t.GetItemListInTrack('video',1);assert len(vs)==188
for s,v in zip(plan['shots'],vs):
    assert v.GetStart()==s['record_frame'] and v.GetDuration()==s['length_frames'] and v.GetMediaPoolItem().GetClipProperty('File Path')==s['path']
assert vs[0].GetFusionCompCount()==1
v2=t.GetItemListInTrack('video',2);assert len(v2)==7
overlays={v.GetStart():v for v in v2}
for s in plan['interview_overlays_v7']:
    v=overlays[s['record_frame']]
    assert v.GetDuration()==s['length_frames'] and v.GetMediaPoolItem().GetClipProperty('File Path')==s['path']
    if s.get('revision_v7'):
        assert v.GetNodeGraph().SetLUT(1,'Sony/SLog3SGamut3.CineToLC-709TypeA.cube')
        assert v.SetClipColor('Blue')
        assert v.SetName('校长原声补画｜'+s['intent'])
assert t.SetTrackName('video',1,'画面_短镜与光线_开篇重剪v7') and t.SetTrackName('video',2,'片名与校长补画_独立可编辑')
markers=t.GetMarkers();pos=next(i for i in range(1,25) if i not in markers)
assert t.AddMarker(pos,'Green','v7 开篇重选与全片短镜','保留完整旁白和460.28秒。重新挑选前70秒，课堂与动作远近景交替，主画面多数约2至3秒。',1,'v7-rhythm-opening')
after=snap(t);assert after['audio']==before['snapshot']['audio']
oldstarts={x for g in groups for x in g['old_record_frames']};segments=[s for g in groups for s in g['segments']];newstarts={s['record_frame'] for s in segments}
assert [x for x in before['snapshot']['video'][0]['items'] if x['start'] not in oldstarts]==[x for x in after['video'][0]['items'] if x['start'] not in newstarts]
for start in [340,11407]:assert next(x for x in after['video'][1]['items'] if x['start']==start)==next(x for x in before['snapshot']['video'][1]['items'] if x['start']==start)
assert t.GetEndFrame()==11507 and all(a.GetEnd()==b.GetStart() for a,b in zip(vs,vs[1:]))
assert pm.SaveProject() and t.SetCurrentTimecode('00:00:00:20')
(OUT/'native_build_v7.json').write_text(json.dumps({'timeline':t.GetName(),'duration_seconds':460.28,'fps':25,'picture_count':len(vs),'revision_v7':plan['revision_v7'],'audio_exactly_preserved':True,'untouched_picture_preserved':True,'opening_and_closing_titles_preserved':True,'complete_principal_video_preserved':True,'snapshot':after,'resume_note':'Resolved unsupported Cyan metadata color using supported Blue; all inserted pictures verified before resuming.'},ensure_ascii=False,indent=2))
print('V7_NATIVE_COMPLETE',len(vs),len(v2),flush=True)
