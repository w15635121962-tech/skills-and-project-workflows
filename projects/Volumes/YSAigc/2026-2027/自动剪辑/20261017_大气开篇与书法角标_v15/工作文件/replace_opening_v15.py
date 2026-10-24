from common_v15 import *
r,pm,p,mp,t=connect();old=t.GetItemListInTrack('video',1)[0];assert old.GetStart()==0 and old.GetEnd()==60
source=Path('/Volumes/YSAigc/2026-2027/文汇中学/拍摄素材转码/004/Proxies/A001C240_260921JW_Proxy.mov');assert source.exists()
media=mp.ImportMedia([str(source)]);assert media;mi=media[0];assert float(mi.GetClipProperty('FPS'))==25
assert t.DeleteClips([old],False)
items=mp.AppendToTimeline([{'mediaPoolItem':mi,'startFrame':200,'endFrame':260,'mediaType':1,'trackIndex':1,'recordFrame':0}]);assert items
it=items[0];assert it.GetStart()==0 and it.GetEnd()==60 and it.GetLeftOffset()==200
assert it.SetName('大气开篇｜教学楼与晨光 · 校园广角')
r.OpenPage('edit');cap(p,t,30,PRE/'新开篇_原始未匹配.jpg')
# Same-camera campus daylight shot, already visually inspected as the current title background.
donor=next(x for x in t.GetItemListInTrack('video',1) if x.GetStart()==452)
print('donor',donor.GetName(),donor.GetNodeGraph().GetLUT(1));assert it.AddVersion('v15_晨光开篇匹配',0);assert it.LoadVersionByName('v15_晨光开篇匹配',0)
assert donor.CopyGrades([it]);cap(p,t,30,PRE/'新开篇_校园色彩匹配.jpg')
# No synthetic pan: original camera movement plus a very restrained push.
c=it.AddFusionComp();assert c;c.SetPrefs({'Comp.FrameFormat.Width':1920,'Comp.FrameFormat.Height':1080,'Comp.FrameFormat.Rate':25})
mi0=c.FindToolByID('MediaIn');mo=c.FindToolByID('MediaOut');xf=named(c,'Transform','V15_开篇轻推')
assert xf.ConnectInput('Input',mi0);xf.Size=c.BezierSpline()
a=int(c.GetAttrs()['COMPN_RenderStart']);z=int(c.GetAttrs()['COMPN_RenderEnd'])
for f in range(a,z+1):
 u=(f-a)/(z-a);xf.Size[f]=1+.012*(3*u*u-2*u*u*u)
# A short natural light lift preserves the scene from the first frame.
bc=named(c,'BrightnessContrast','V15_开篇柔入');assert bc.ConnectInput('Input',xf);bc.Gain=c.BezierSpline()
for f in range(a,a+11):
 u=(f-a)/10;bc.Gain[f]=.72+.28*(3*u*u-2*u*u*u)
assert mo.ConnectInput('Input',bc)
assert it.ExportFusionComp(str(OUT/'校园晨光开篇_原生轻推.comp'),1);assert it.ImportFusionComp(str(OUT/'校园晨光开篇_原生轻推.comp'));active_comp(it)
# Final typography proportions and a seamless ten-second highlight sweep.
corner=t.GetItemListInTrack('video',5)[0];cc=active_comp(corner)
for n in ['V15_书法校名','V15_校名柔影']:setv(cc.FindTool(n),{'Font':'Ma Shan Zheng','Style':'Regular','Size':.038,'Tracking':1.08})
for n,y in [('V15_集团副标',.851),('V15_副标柔影',.850)]:setv(cc.FindTool(n),{'Size':.014,'Tracking':1.45,'Center':{1:.882 if '柔影' not in n else .8826,2:y}})
setv(cc.FindTool('V15_金线轮廓'),{'Center':{1:.882,2:.875},'Width':.112,'Height':.0011,'SoftEdge':.00035})
u='((time)%250)/250';cc.FindTool('V15_流光羽化').Center.SetExpression(f'Point(0.826+0.112*({u}),0.875)')
cc.FindTool('V15_十秒循环流光').Blend.SetExpression(f'0.7*(sin(3.14159265359*({u})))^6')
assert corner.ExportFusionComp(str(OUT/'文汇中学_原生动态角标_v15.comp'),1)
assert pm.SaveProject()
for f in [0,15,30,59,60,400,1988,11070,11450,11506]:cap(p,t,f,PRE/f'精修帧_{f:05d}.jpg')
(OUT/'opening_replacement_v15.json').write_text(json.dumps({'source':str(source),'source_fps':25,'source_in':200,'source_out_exclusive':260,'record_in':0,'duration':60,'grade_donor_start':452,'subtle_push':.012,'light_lift_frames':10},ensure_ascii=False,indent=2))
print('replaced 60 frames; total',t.GetEndFrame())
