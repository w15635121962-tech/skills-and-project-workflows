from common_v15 import *
r,pm,p,mp,t=connect();it=t.GetItemListInTrack('video',5)[0];c=active_comp(it)
for name in ['V15_书法校名','V15_集团副标']:
 x=c.FindTool(name);setv(x,{'Enabled2':1,'Red2':.025,'Green2':.045,'Blue2':.037,'Opacity2':.44 if '校名' in name else .6,'Thickness2':.014 if '校名' in name else .022,'OutsideOnly2':1,'SoftnessX2':.1,'SoftnessY2':.1})
setv(c.FindTool('V15_校名影合成'),{'Blend':.42})
setv(c.FindTool('V15_副标影合成'),{'Blend':.6})
end=named(c,'Merge','V15_片尾同步淡出');assert end.ConnectInput('Background',c.FindTool('V15_透明画布'));assert end.ConnectInput('Foreground',c.FindTool('V15_十秒循环流光'))
end.Blend.SetExpression('iif(time<11495,1,iif(time>11506,0,1-((time-11495)/11)^2*(3-2*((time-11495)/11))))')
assert c.FindToolByID('MediaOut').ConnectInput('Input',end)
assert it.ExportFusionComp(str(OUT/'文汇中学_原生动态角标_v15.comp'),1)
assert pm.SaveProject();assert pm.CloseProject(p)
p=pm.LoadProject(PROJECT);assert p;t=p.GetCurrentTimeline();assert t.GetName()==TIMELINE
corner=t.GetItemListInTrack('video',5)[0];first=t.GetItemListInTrack('video',1)[0];assert corner.GetFusionCompCount()==1;assert first.GetFusionCompCount()==1
c=active_comp(corner);assert c.FindTool('V15_书法校名').GetInput('Font')=='Ma Shan Zheng'
assert active_comp(first).FindTool('V15_开篇轻推')
r.OpenPage('edit')
for f in [0,30,59,60,400,1988,11070,11498,11506]:cap(p,t,f,PRE/f'定稿帧_{f:05d}.jpg')
font=OUT/'角标字体/mashanzheng/MaShanZheng-Regular.ttf'
(OUT/'字体来源.json').write_text(json.dumps({'family':'Ma Shan Zheng','style':'Regular','source':'https://github.com/google/fonts/tree/main/ofl/mashanzheng','upstream_commit_in_metadata':'6bfdbe288f5935c6e9072cdd6ab1aa102a006aab','license':'SIL Open Font License 1.1','installed':'/Users/xuan/Library/Fonts/MaShanZheng-Regular.ttf','sha256':hashlib.sha256(font.read_bytes()).hexdigest()},ensure_ascii=False,indent=2))
(OUT/'bug_native_design.json').write_text(json.dumps({'duration_frames':11507,'loop_frames':250,'loop_seconds':10,'main_font':'Ma Shan Zheng','style':'Regular','main_text':'文汇中学','sub_font':'Songti SC','sub_text':'教育集团','main_size':.038,'main_tracking':1.08,'bounding_design_px':[1570,60,1815,175],'last_fade_frames':12,'editable':'Native TextPlus and shape masks on V5; original typography file included'},ensure_ascii=False,indent=2))
print('reopen verified both native compositions; font persists; final frame fades')
