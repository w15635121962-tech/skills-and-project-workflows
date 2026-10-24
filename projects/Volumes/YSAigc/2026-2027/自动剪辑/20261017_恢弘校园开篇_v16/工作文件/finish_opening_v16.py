from common_v16 import *
r,pm,p,mp,t=connect();first,book=t.GetItemListInTrack('video',1)[:2];source=Path(first.GetMediaPoolItem().GetClipProperty('File Path'));parent=next(p.GetTimelineByIndex(k) for k in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(k).GetName()=='学校_大气开篇与书法动态角标_v15_20261017');bookdonor=next(x for x in parent.GetItemListInTrack('video',1) if x.GetStart()==60)
# Match against the already inspected adjacent source take from the same outdoor ceremony.
donor=next(x for x in t.GetItemListInTrack('video',1) if x.GetStart()==9045)
r.OpenPage('color');time.sleep(.65)
for it,name,d in [(first,'v16_恢弘开篇_自然人文校色',donor),(book,'v9_自然人文校色',bookdonor)]:
 it.GetNodeGraph().GetNumNodes()
 if name not in it.GetVersionNameList(0):assert it.AddVersion(name,0),('AddVersion',name)
 assert it.LoadVersionByName(name,0)
 assert d.CopyGrades([it])
r.OpenPage('edit');cap(p,t,40,PRE/'学生方阵_同场色彩匹配.jpg')
# Preserve an independently editable, gentle center push on the shortened book detail.
c=book.AddFusionComp();assert c;c.SetPrefs({'Comp.FrameFormat.Width':1920,'Comp.FrameFormat.Height':1080,'Comp.FrameFormat.Rate':25})
mi0=c.FindToolByID('MediaIn');mo=c.FindToolByID('MediaOut');xf=named(c,'Transform','V16_书写轻推');assert xf.ConnectInput('Input',mi0);assert mo.ConnectInput('Input',xf)
a=int(c.GetAttrs()['COMPN_RenderStart']);z=int(c.GetAttrs()['COMPN_RenderEnd']);assert z-a+1==37
xf.Size=c.BezierSpline()
for f in range(a,z+1):
 u=(f-a)/(z-a);xf.Size[f]=1+.014*(3*u*u-2*u*u*u)
assert book.ExportFusionComp(str(OUT/'书写细节_原生缓推_v16.comp'),1);assert book.ImportFusionComp(str(OUT/'书写细节_原生缓推_v16.comp'));active_comp(book)
assert pm.SaveProject();assert pm.CloseProject(p);p=pm.LoadProject(PROJECT);assert p;t=p.GetCurrentTimeline();assert t.GetName()==TIMELINE
r.OpenPage('edit')
for f in [0,20,40,60,79,80,98,116,117,150,400,1988,11070,11506]:cap(p,t,f,PRE/f'精修帧_{f:05d}.jpg')
assert t.GetEndFrame()==11507
(OUT/'opening_edit_v16.json').write_text(json.dumps({'first_shot':{'source':str(source),'source_fps':25,'source_in':350,'source_out_exclusive':430,'record_start':0,'record_end':80,'seconds':3.2,'camera_motion':'authentic original camera movement; no digital crop'},'book_detail':{'source_in':150,'source_out_exclusive':187,'record_start':80,'record_end':117,'gentle_push':.014},'all_after_frame_117_unchanged':True,'sound_not_edited':True,'reference_sentence':'这里，是书香浸润的沃土；'},ensure_ascii=False,indent=2))
print('new native opening 0..80 wide student formation; 80..117 book; reopened',flush=True)
