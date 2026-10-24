from common_v21 import *
import ast
r,pm,p,mp,t=connect();base=json.loads((OUT/'live_before_v21.json').read_text());before=base['snapshot'];oldgraphs=json.loads((OUT/'live_graphs_before_v21.json').read_text())
tree=ast.parse((OUT/'build_opening_v21.py').read_text());rows=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(k,ast.Name) and k.id=='rows' for k in n.targets)))
src=Path('/Volumes/YSAigc/2026-2027/文汇中学/拍摄素材转码')
plan=[dict(path=str(src/a),start=b,end=c,source_in=d,source_out_exclusive=d+c-b,label=e,slope=f,power=g) for a,b,c,d,e,f,g in rows]
old=next(i for i in t.GetItemListInTrack('video',3) if i.GetStart()==324);assert t.DeleteClips([old],False)
path=src/'004/Proxies/A001C035_260921KV_Proxy.mov';m=mp.ImportMedia([str(path)]);assert len(m)==1 and float(m[0].GetClipProperty('FPS'))==25
it=mp.AppendToTimeline([dict(mediaPoolItem=m[0],startFrame=175,endFrame=221,mediaType=1,trackIndex=3,recordFrame=324)])[0]
assert (it.GetStart(),it.GetEnd(),it.GetLeftOffset())==(324,370,175);assert it.SetName('开篇精选｜晨光穿树 · 梦想生长');assert it.SetClipColor('Blue')
it.GetCurrentVersion();it.GetNodeGraph().GetNumNodes();r.OpenPage('color');time.sleep(.4)
neutral=next(i for i in t.GetItemListInTrack('video',1) if i.GetStart()==340);assert neutral.CopyGrades([it])
assert it.SetCDL(dict(NodeIndex='1',Slope='.98 .98 .98',Offset='0 0 0',Power='1 1 1',Saturation='1'))
for start,slope,power in [(145,1.08,.96),(370,1.02,.94)]:
 target=next(i for i in t.GetItemListInTrack('video',3) if i.GetStart()==start)
 assert target.SetCDL(dict(NodeIndex='1',Slope=' '.join([str(slope)]*3),Offset='0 0 0',Power=' '.join([str(power)]*3),Saturation='1'))
 for row in plan:
  if row['start']==start:row.update(slope=slope,power=power)
# A restrained native 2.5 percent push complements the subtle real foliage motion.
c=it.AddFusionComp();assert c;c.SetPrefs({'Comp.FrameFormat.Width':1920,'Comp.FrameFormat.Height':1080,'Comp.FrameFormat.Rate':25})
mi=c.FindToolByID('MediaIn');mo=c.FindToolByID('MediaOut');xf=named(c,'Transform','V21_晨光缓推_2p5percent');assert xf.ConnectInput('Input',mi) and mo.ConnectInput('Input',xf)
xf.SetInput('Center',{1:.5,2:.5});xf.SetInput('Pivot',{1:.5,2:.5});xf.Size=c.BezierSpline()
a=int(c.GetAttrs()['COMPN_RenderStart']);z=int(c.GetAttrs()['COMPN_RenderEnd']);assert z-a+1==46
for f in range(a,z+1):
 u=(f-a)/(z-a);xf.Size[f]=1+.025*(3*u*u-2*u*u*u)
assert it.ExportFusionComp(str(OUT/'晨光_原生缓推_v21.comp'),1);assert it.ImportFusionComp(str(OUT/'晨光_原生缓推_v21.comp'));active_comp(it)
row=next(x for x in plan if x['start']==324);row.update(path=str(path),source_in=175,source_out_exclusive=221,label='晨光穿树 · 梦想生长',slope=.98,power=1,native_fusion_push=[1,1.025])
report=dict(timeline=TIMELINE,range=[0,667],fps=25,shots=plan,original_native_title_range=[340,508],title_track=4,real_people_action_shots=5,first_music_changed_only=[0,40.8],old_timeline_preserved=True,narration_and_live_speech_unchanged=True)
(OUT/'opening_edit_plan_v21.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
assert pm.SaveProject();after=snap(t);g=graphs(t);assert pm.CloseProject(p);p=pm.LoadProject(PROJECT);assert p;t=p.GetCurrentTimeline();assert t.GetName()==TIMELINE;assert snap(t)==after and graphs(t)==g
parent=next(p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()==PARENT);assert p.SetCurrentTimeline(parent);assert snap(parent)==before and graphs(parent)==oldgraphs;assert p.SetCurrentTimeline(t)
r.OpenPage('edit')
frames=sorted(set([0,59,60,97,98,144,145,206,207,253,254,323,324,339,340,346,369,370,415,416,461,462,507,508,553,554,600,601,666,667]+[(x['start']+x['end'])//2 for x in plan]))
for f in frames:cap(p,t,f,PRE/f'原生终版_{f:04d}.jpg',wait=.035)
(OUT/'picture_ready_snapshot_v21.json').write_text(json.dumps(after,ensure_ascii=False,indent=2));(OUT/'picture_ready_graphs_v21.json').write_text(json.dumps(g,ensure_ascii=False,indent=2));assert t.SetCurrentTimecode(tc(0));assert pm.SaveProject();print('V21_REOPEN_VERIFIED_AND_STILLS_READY',len(frames),flush=True)
