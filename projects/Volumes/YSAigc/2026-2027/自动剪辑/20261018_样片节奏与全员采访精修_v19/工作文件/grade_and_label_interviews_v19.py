from common_v19 import *
r,pm,p,mp,t=connect();plan=json.loads((OUT/'interview_picture_inserted_v19.json').read_text())['new_speakers']
donor=next(x for x in t.GetItemListInTrack('video',1) if x.GetStart()==561);assert donor.GetNodeGraph().GetNumNodes()==1
added=[next(x for x in t.GetItemListInTrack('video',3) if x.GetStart()==row['record_start']) for row in plan]
r.OpenPage('color');time.sleep(.5)
for it in added:
 assert donor.CopyGrades([it]);assert it.SetCDL({'NodeIndex':'1','Slope':'1 1 1','Offset':'0 0 0','Power':'1 1 1','Saturation':'1'})
r.OpenPage('edit')
for it,row in zip(added,plan):cap(p,t,(row['record_start']+row['record_end'])//2,PRE/f"采访_色彩匹配_{row['speaker_key']}.jpg")
heads=['文汇中学教育集团','金台书院小学','前门外国语学校','文汇小学']
subs=['党建引领 · 协同发展','书院文脉 · 快乐成长','看见每个生命 · 成就每个孩子','校家社协同 · 汇聚育人合力']
clear=next(x for x in t.GetItemListInTrack('video',4) if x.GetStart()==12420)
titles=mp.AppendToTimeline([{'mediaPoolItem':it.GetMediaPoolItem(),'startFrame':row['source_in_frame'],'endFrame':row['source_out_frame_exclusive'],'recordFrame':row['record_start'],'trackIndex':4,'mediaType':1} for it,row in zip(added,plan)]);assert len(titles)==4
for it,row,head,sub in zip(titles,plan,heads,subs):
 c=it.AddFusionComp();assert c;c.SetPrefs({'Comp.FrameFormat.Width':1920,'Comp.FrameFormat.Height':1080,'Comp.FrameFormat.Rate':25})
 base=solid(c,'V19_透明画布',(0,0,0),0);panel=solid(c,'V19_墨绿姓名板',(.025,.065,.057));mask=named(c,'RectangleMask','V19_姓名板范围');setv(mask,{'Center':{1:.28,2:.12},'Width':.40,'Height':.082,'SoftEdge':.002});assert panel.ConnectInput('EffectMask',mask)
 stage=merge(c,base,panel,'V19_姓名板合成',.82)
 for name,textstring,size,y,color,fontstyle in [('V19_学校标识',head,.023,.135,(.97,.95,.88),'Bold'),('V19_采访主题',sub,.014,.098,(.83,.74,.52),'Regular')]:
  tx=named(c,'TextPlus',name);setv(tx,{'UseFrameFormatSettings':0,'Width':1920,'Height':1080,'StyledText':textstring,'Font':'Songti SC','Style':fontstyle,'Size':size,'Center':{1:.28,2:y},'Red1':color[0],'Green1':color[1],'Blue1':color[2],'Alpha1':1});stage=merge(c,stage,tx,name+'合成',1)
 fade=merge(c,base,stage,'V19_标识柔和出入',1);a=int(c.GetAttrs()['COMPN_RenderStart']);z=int(c.GetAttrs()['COMPN_RenderEnd']);fade.Blend=c.BezierSpline()
 for f,v in [(a,0),(a+9,1),(z-9,1),(z,0)]:fade.Blend[f]=v
 assert c.FindToolByID('MediaOut').ConnectInput('Input',fade)
 file=OUT/f"采访标识_{row['speaker_key']}_原生.comp";assert it.ExportFusionComp(str(file),1);assert it.ImportFusionComp(str(file));active_comp(it)
 it.GetCurrentVersion();it.GetNodeGraph().GetNumNodes();assert clear.CopyGrades([it]);assert it.SetName('采访标识｜'+head);assert it.SetClipColor('Teal')
 assert it.GetStart()==row['record_start'] and it.GetEnd()==row['record_end']
assert pm.SaveProject();assert pm.CloseProject(p);p=pm.LoadProject(PROJECT);assert p;t=p.GetCurrentTimeline();assert t.GetName()==TIMELINE;r.OpenPage('edit')
for row in plan:
 for f in [row['record_start'],row['record_start']+15,(row['record_start']+row['record_end'])//2,row['record_end']-1]:cap(p,t,f,PRE/f"采访_标识定稿_{row['speaker_key']}_{f}.jpg")
print('FOUR_INTERVIEWS_GRADED_AND_LABELED',flush=True)
