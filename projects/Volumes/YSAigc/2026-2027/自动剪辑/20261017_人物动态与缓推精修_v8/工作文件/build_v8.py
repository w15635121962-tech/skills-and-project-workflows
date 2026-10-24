import sys,json,math
from pathlib import Path
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';plan=json.loads((OUT/'edit_plan_v8.json').read_text());before=json.loads((OUT/'live_before_v8.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool();t=p.GetCurrentTimeline();assert p.GetName()=='学校' and t.GetName()==plan['name']
def snap(t):
    return {typ:[{'track':k,'enabled':t.GetIsTrackEnabled(typ,k),'locked':t.GetIsTrackLocked(typ,k),'name':t.GetTrackName(typ,k),'items':[{'name':it.GetName(),'start':it.GetStart(),'end':it.GetEnd(),'offset':it.GetLeftOffset(),'path':it.GetMediaPoolItem().GetClipProperty('File Path') if it.GetMediaPoolItem() else None,'properties':it.GetProperty(),'enabled':it.GetClipEnabled(),'fusion_count':it.GetFusionCompCount()} for it in t.GetItemListInTrack(typ,k)]} for k in range(1,t.GetTrackCount(typ)+1)] for typ in ['video','audio']}
assert snap(t)==before['snapshot'],'Only verified first-clip prototype may have changed inside Fusion'
pixel=json.loads((OUT/'motion_prototype_pixel_verification_v8.json').read_text());assert pixel['passed']
items={v.GetStart():v for v in t.GetItemListInTrack('video',1)};repls=plan['source_replacements_v8'];remove=[items[s['record_frame']] for s in repls]
assert all(v.GetFusionCompCount()==0 and not v.GetLinkedItems() for v in remove)
assert pm.SaveProject() and t.DeleteClips(remove,False)
folder=mp.AddSubFolder(mp.GetRootFolder(),'人物动态与缓推精修_v8_20261017');assert folder and mp.SetCurrentFolder(folder)
def walk(f):
    yield from f.GetClipList()
    for sf in f.GetSubFolderList():yield from walk(sf)
pool={v.GetClipProperty('File Path'):v for v in walk(mp.GetRootFolder())};infos=[]
for s in repls:
    if s['path'] not in pool:
        added=mp.ImportMedia([s['path']]);assert added and len(added)==1;pool[s['path']]=added[0]
    m=pool[s['path']];assert float(m.GetClipProperty('FPS'))==s['fps'];a=round(s['in']*s['fps']);n=math.ceil(s['length_frames']/25*s['fps']-1e-8)
    infos.append({'mediaPoolItem':m,'startFrame':a,'endFrame':a+n,'mediaType':1,'trackIndex':1,'recordFrame':s['record_frame']})
added=mp.AppendToTimeline(infos);assert added and len(added)==len(repls)
for s,v in zip(repls,added):
    assert v.GetStart()==s['record_frame'] and v.GetDuration()==s['length_frames'] and v.GetMediaPoolItem().GetClipProperty('Online Status')=='Online'
    if s['log']:assert v.GetNodeGraph().SetLUT(1,'Sony/SLog3SGamut3.CineToLC-709TypeA.cube')
    assert v.SetClipColor('Blue')
items={v.GetStart():v for v in t.GetItemListInTrack('video',1)};records=[]
for m in plan['motion_v8']:
    v=items[m['record_frame']];s=next(s for s in plan['shots'] if s['record_frame']==m['record_frame'])
    if v.GetFusionCompCount():
        assert m['record_frame']==0;c=v.GetFusionCompByIndex(1);xf=c.FindTool('V8_GentleMotion');assert xf
    else:
        c=v.AddFusionComp();assert c;c.SetPrefs({'Comp.FrameFormat.Width':s['resolution'][0],'Comp.FrameFormat.Height':s['resolution'][1],'Comp.FrameFormat.Rate':s['fps']})
        mi=c.FindToolByID('MediaIn');mo=c.FindToolByID('MediaOut');xf=c.AddTool('Transform');assert xf and xf.ConnectInput('Input',mi) and mo.ConnectInput('Input',xf);xf.SetAttrs({'TOOLS_Name':'V8_GentleMotion'})
    xf.SetInput('Center',{1:.5,2:.5});xf.SetInput('Pivot',{1:.5,2:.5});xf.Size=c.BezierSpline()
    a=int(c.GetAttrs()['COMPN_RenderStart']);z=int(c.GetAttrs()['COMPN_RenderEnd']);assert z-a==v.GetDuration()-1
    values=[]
    for f in range(a,z+1):
        u=(f-a)/(z-a);value=m['start_size']+(m['end_size']-m['start_size'])*u*u*(3-2*u);xf.Size[f]=value;values.append(value)
    assert max(abs(xf.GetInput('Size',a+i)-val) for i,val in enumerate(values))<1e-7
    assert v.ExportFusionComp(str(OUT/f"v8-motion-{m['record_frame']}.comp"),1)
    records.append(dict(m,source_clock_range=[a,z],size_values=values,filter_method=xf.GetInput('FilterMethod')))
    if len(records)%10==0:print('V8_EDITABLE_MOTIONS',len(records),flush=True)
assert t.SetTrackName('video',1,'画面_人物动态与缓推精修_v8')
pos=next(i for i in range(1,25) if i not in t.GetMarkers());assert t.AddMarker(pos,'Green','v8 人物动态与缓推','保持188镜和完整声音。真实人物动作优先，适合镜头加入可编辑2.5%至3.5%固定中心微推拉。',1,'v8-motion')
after=snap(t);assert after['audio']==before['snapshot']['audio'] and after['video'][1]['items']==before['snapshot']['video'][1]['items']
changed={s['record_frame'] for s in repls}|{m['record_frame'] for m in records}
assert [s for s in before['snapshot']['video'][0]['items'] if s['start'] not in changed]==[s for s in after['video'][0]['items'] if s['start'] not in changed]
vs=t.GetItemListInTrack('video',1);assert len(vs)==188 and t.GetEndFrame()==11507 and all(a.GetEnd()==b.GetStart() for a,b in zip(vs,vs[1:]));assert pm.SaveProject() and t.SetCurrentTimecode('00:00:00:20')
(OUT/'native_build_v8.json').write_text(json.dumps({'timeline':t.GetName(),'duration_seconds':460.28,'picture_count':188,'revision_v8':plan['revision_v8'],'motion_records':records,'all_audio_preserved':True,'all_v2_titles_and_interview_preserved':True,'untouched_picture_preserved':True,'snapshot':after},ensure_ascii=False,indent=2));print('V8_NATIVE_COMPLETE',len(repls),len(records),flush=True)
