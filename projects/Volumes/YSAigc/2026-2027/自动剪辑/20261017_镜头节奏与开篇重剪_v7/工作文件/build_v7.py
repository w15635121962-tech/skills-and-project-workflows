import sys,json,math
from pathlib import Path
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件'
plan=json.loads((OUT/'edit_plan_v7.json').read_text());groups=json.loads((OUT/'native_changes_v7.json').read_text());before=json.loads((OUT/'live_before_v7.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool();base=p.GetCurrentTimeline()
def snap(t):
    return {typ:[{'track':k,'enabled':t.GetIsTrackEnabled(typ,k),'locked':t.GetIsTrackLocked(typ,k),'name':t.GetTrackName(typ,k),'items':[{'name':it.GetName(),'start':it.GetStart(),'end':it.GetEnd(),'offset':it.GetLeftOffset(),'path':it.GetMediaPoolItem().GetClipProperty('File Path') if it.GetMediaPoolItem() else None,'properties':it.GetProperty(),'enabled':it.GetClipEnabled(),'fusion_count':it.GetFusionCompCount()} for it in t.GetItemListInTrack(typ,k)]} for k in range(1,t.GetTrackCount(typ)+1)] for typ in ['video','audio']}
assert p.GetName()=='学校' and base.GetName()==plan['base_timeline'] and snap(base)==before['snapshot']
assert plan['name'] not in [p.GetTimelineByIndex(i).GetName() for i in range(1,p.GetTimelineCount()+1)]
assert pm.SaveProject();t=base.DuplicateTimeline(plan['name']);assert t and p.SetCurrentTimeline(t) and snap(t)==before['snapshot'];assert r.OpenPage('edit')
oldstarts={a for g in groups for a in g['old_record_frames']}
remove=[v for v in t.GetItemListInTrack('video',1) if v.GetStart() in oldstarts]
assert len(remove)==len(oldstarts) and all(not v.GetLinkedItems() for v in remove)
assert t.DeleteClips(remove,False)
folder=mp.AddSubFolder(mp.GetRootFolder(),'镜头节奏与开篇重剪_v7_20261017');assert folder and mp.SetCurrentFolder(folder)
def walk(f):
    yield from f.GetClipList()
    for sf in f.GetSubFolderList():yield from walk(sf)
pool={v.GetClipProperty('File Path'):v for v in walk(mp.GetRootFolder())}
def info(s,track):
    path=s['path']
    if path not in pool:
        imported=mp.ImportMedia([path]);assert imported and len(imported)==1;pool[path]=imported[0]
    m=pool[path];fps=float(m.GetClipProperty('FPS'));assert abs(fps-s['fps'])<.001
    start=round(s['in']*fps);count=math.ceil(s['length_frames']/25*fps-1e-8)
    return {'mediaPoolItem':m,'startFrame':start,'endFrame':start+count,'mediaType':1,'trackIndex':track,'recordFrame':s['record_frame']}
def add(specs,track):
    added=[]
    for a in range(0,len(specs),35):
        batch=specs[a:a+35];vs=mp.AppendToTimeline([info(s,track) for s in batch]);assert vs and len(vs)==len(batch)
        for s,v in zip(batch,vs):
            assert v.GetStart()==s['record_frame'] and v.GetDuration()==s['length_frames'],(s['record_frame'],v.GetStart(),v.GetDuration(),s['length_frames'])
            assert v.GetMediaPoolItem().GetClipProperty('Online Status')=='Online'
            if s['log']:assert v.GetNodeGraph().SetLUT(1,'Sony/SLog3SGamut3.CineToLC-709TypeA.cube')
            assert v.SetClipColor('Blue')
        added.extend(vs);print('V7_NATIVE_ITEMS',track,len(added),flush=True)
    return added
segments=[s for g in groups for s in g['segments']];added=add(segments,1)
first=next(v for v in added if v.GetStart()==0);c=first.AddFusionComp();assert c
mi=c.FindToolByID('MediaIn');mo=c.FindToolByID('MediaOut');bc=c.AddTool('BrightnessContrast');assert bc.ConnectInput('Input',mi) and mo.ConnectInput('Input',bc)
a=c.GetAttrs()['COMPN_RenderStart'];z=c.GetAttrs()['COMPN_RenderEnd'];bc.Gain=c.BezierSpline();bc.Gain[a]=0;bc.Gain[a+6]=1;bc.Gain[z]=1
assert first.ExportFusionComp(str(OUT/'v7-opening-picture.comp'),1)

# Keep every original interview frame and all synchronous audio below V2.
old_overlay=next(v for v in t.GetItemListInTrack('video',2) if v.GetStart()==11318)
assert old_overlay.GetDuration()==89 and t.DeleteClips([old_overlay],False)
new_overlays=[s for s in plan['interview_overlays_v7'] if s.get('revision_v7')]
ovs=add(new_overlays,2)
for s,v in zip(new_overlays,ovs):assert v.SetName('校长原声补画｜'+s['intent'])
assert t.SetTrackName('video',1,'画面_短镜与光线_开篇重剪v7')
assert t.SetTrackName('video',2,'片名与校长补画_独立可编辑')
markers=t.GetMarkers();pos=next(i for i in range(1,25) if i not in markers)
assert t.AddMarker(pos,'Green','v7 开篇重选与全片短镜','保留完整旁白和460.28秒。重新挑选前70秒，课堂与动作远近景交替，主画面多数约2至3秒。',1,'v7-rhythm-opening')
after=snap(t)
assert after['audio']==before['snapshot']['audio']
assert [x for x in before['snapshot']['video'][0]['items'] if x['start'] not in oldstarts]==[x for x in after['video'][0]['items'] if x['start'] not in {s['record_frame'] for s in segments}]
for start in [340,11407]:
    assert next(x for x in after['video'][1]['items'] if x['start']==start)==next(x for x in before['snapshot']['video'][1]['items'] if x['start']==start)
vs=t.GetItemListInTrack('video',1);assert len(vs)==len(plan['shots']) and t.GetEndFrame()==11507
assert all(a.GetEnd()==b.GetStart() for a,b in zip(vs,vs[1:]))
assert pm.SaveProject() and t.SetCurrentTimecode('00:00:00:20')
(OUT/'native_build_v7.json').write_text(json.dumps({'timeline':t.GetName(),'duration_seconds':460.28,'fps':25,'picture_count':len(vs),'revision_v7':plan['revision_v7'],'audio_exactly_preserved':True,'untouched_picture_preserved':True,'opening_and_closing_titles_preserved':True,'complete_principal_video_preserved':True,'snapshot':after},ensure_ascii=False,indent=2))
print('V7_NATIVE_COMPLETE',flush=True)
