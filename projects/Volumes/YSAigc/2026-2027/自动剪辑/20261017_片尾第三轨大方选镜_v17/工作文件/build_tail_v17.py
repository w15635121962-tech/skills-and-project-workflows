from common_v17 import *
r,pm,p,mp,t=connect();before=json.loads((OUT/'live_before_v17.json').read_text())
selected=json.loads((OUT/'片尾选镜/selected_three_v17.json').read_text())['selected']
plan=[{'path':x['path'],'start':x['start'],'end':x['end'],'source_in':x['source_in_frame'],'source_out':x['source_out_exclusive_frame'],'label':x['scene']} for x in selected]
plan.append({'path':'/Volumes/YSAigc/2026-2027/文汇中学/拍摄素材转码/007/Proxies/C0117_Proxy.mov','start':11407,'end':11507,'source_in':10,'source_out':110,'label':'学生并肩向前 · 舒展收尾'})
for x in plan:
 assert not any(it['path']==x['path'] for tr in before['video'] for it in tr['items']),x['path']
 assert not any(it.GetStart()<x['end'] and it.GetEnd()>x['start'] for it in t.GetItemListInTrack('video',3))
media=mp.ImportMedia([x['path'] for x in plan]);assert len(media)==4
by_path={i.GetClipProperty('File Path'):i for i in media}
infos=[]
for x in plan:
 m=by_path[x['path']];assert float(m.GetClipProperty('FPS'))==25
 infos.append({'mediaPoolItem':m,'startFrame':x['source_in'],'endFrame':x['source_out'],'mediaType':1,'trackIndex':3,'recordFrame':x['start']})
items=mp.AppendToTimeline(infos);assert len(items)==4
for x,it in zip(plan,items):
 assert (it.GetStart(),it.GetEnd(),it.GetLeftOffset())==(x['start'],x['end'],x['source_in'])
 assert it.SetName('尾段精选｜'+x['label']);assert it.SetClipColor('Blue')
r.OpenPage('edit')
# Frame-first matching to existing humanistic grades from corresponding camera/subject scenes.
for x in plan:cap(p,t,(x['start']+x['end'])//2,PRE/f"未匹配_{x['start']}.jpg")
donors=[next(i for i in t.GetItemListInTrack('video',1) if i.GetStart()==561),next(i for i in t.GetItemListInTrack('video',2) if i.GetStart()==11189),next(i for i in t.GetItemListInTrack('video',1) if i.GetStart()==1584),next(i for i in t.GetItemListInTrack('video',1) if i.GetStart()==10782)]
for i in items:i.GetCurrentVersion();i.GetVersionNameList(0);i.GetNodeGraph().GetNumNodes()
r.OpenPage('color');time.sleep(.7)
for it,donor in zip(items,donors):
 assert donor.GetNodeGraph().GetNumNodes()==1,('Do not transfer targeted secondary grade',donor.GetName())
 assert donor.CopyGrades([it]),('copy grade',it.GetName())
# A native fade on the new V3 ending keeps it opaque over the original layers through black.
last=items[-1];c=last.AddFusionComp();assert c;c.SetPrefs({'Comp.FrameFormat.Width':1920,'Comp.FrameFormat.Height':1080,'Comp.FrameFormat.Rate':25})
mi=c.FindToolByID('MediaIn');mo=c.FindToolByID('MediaOut');fade=named(c,'BrightnessContrast','V17_片尾画面柔和淡出');assert fade.ConnectInput('Input',mi);assert mo.ConnectInput('Input',fade)
a=int(c.GetAttrs()['COMPN_RenderStart']);z=int(c.GetAttrs()['COMPN_RenderEnd']);assert z-a+1==100
fade.Gain=c.BezierSpline()
for f in range(a,z+1):
 u=max(0.,(f-(z-30))/30);fade.Gain[f]=1-(3*u*u-2*u*u*u)
assert last.ExportFusionComp(str(OUT/'片尾群像_原生淡出_v17.comp'),1);assert last.ImportFusionComp(str(OUT/'片尾群像_原生淡出_v17.comp'));active_comp(last)
# Keep the unchanged editable ending title above the requested V3 footage.
oldtitle=next(x for x in t.GetItemListInTrack('video',2) if x.GetStart()==11407)
assert oldtitle.ExportFusionComp(str(OUT/'原片尾标题_保留样式.comp'),1)
newtitle=mp.AppendToTimeline([{'mediaPoolItem':oldtitle.GetMediaPoolItem(),'startFrame':oldtitle.GetLeftOffset(),'endFrame':oldtitle.GetLeftOffset()+100,'mediaType':1,'trackIndex':4,'recordFrame':11407}])[0]
assert (newtitle.GetStart(),newtitle.GetEnd())==(11407,11507)
assert newtitle.ImportFusionComp(str(OUT/'原片尾标题_保留样式.comp'));active_comp(newtitle)
newtitle.GetCurrentVersion();newtitle.GetNodeGraph().GetNumNodes();r.OpenPage('color');time.sleep(.4);assert oldtitle.CopyGrades([newtitle]);assert newtitle.SetName(oldtitle.GetName())
assert t.DeleteClips([oldtitle],False)
assert pm.SaveProject();assert pm.CloseProject(p);p=pm.LoadProject(PROJECT);assert p;t=p.GetCurrentTimeline();assert t.GetName()==TIMELINE
newtail=[i for i in t.GetItemListInTrack('video',3) if i.GetStart()>=11150];assert len(newtail)==4 and newtail[-1].GetFusionCompCount()==1
assert next(i for i in t.GetItemListInTrack('video',4) if i.GetStart()==11407).GetFusionCompCount()==1
r.OpenPage('edit')
frames=[11149,11150,11195,11241,11242,11280,11317,11318,11362,11406,11407,11432,11457,11482,11500,11506]
for f in frames:cap(p,t,f,PRE/f'精修帧_{f:05d}.jpg')
(OUT/'tail_edit_plan_v17.json').write_text(json.dumps({'range':[11150,11507],'track':3,'fps':25,'selected':plan,'title_moved_from_track':2,'title_moved_to_track':4,'title_range':[11407,11507],'title_style_and_timing_unchanged':True,'last_picture_fade_frames':30,'audio_not_edited':True,'preserved_user_snapshot':'live_before_v17.json'},ensure_ascii=False,indent=2))
print('V3 four new shots, V4 original title, native reopen checked',flush=True)
