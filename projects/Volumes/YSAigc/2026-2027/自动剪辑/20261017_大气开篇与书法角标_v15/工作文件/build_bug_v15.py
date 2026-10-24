from common_v15 import *
r,pm,p,mp,t=connect()
a=json.loads((OUT/'live_before_v15.json').read_text())
for k in range(4):
 for it,x in zip(t.GetItemListInTrack('video',k+1),a['video'][k]['items']):
  if it.GetName()!=x['name']:assert it.SetName(x['name'])
b=snap(t);assert b['audio']==a['audio'] and b['video'][:4]==a['video']
assert graphs(t)[:-1]==json.loads((OUT/'live_graphs_before_v15.json').read_text())
(OUT/'full_length_roundtrip_qa.json').write_text(json.dumps({'original_tracks_and_audio_exact':True,'overlay_track':b['video'][4]},ensure_ascii=False,indent=2))
it=t.GetItemListInTrack('video',5)[0];assert it.GetDuration()==11507
assert it.SetName('文汇中学教育集团｜书法角标 · 10秒光线循环')
c=it.AddFusionComp();assert c
c.SetPrefs({'Comp.FrameFormat.Width':1920,'Comp.FrameFormat.Height':1080,'Comp.FrameFormat.Rate':25})
attrs=c.GetAttrs();print('comp_time',{k:v for k,v in attrs.items() if k.startswith('COMPN_')})
a=int(attrs['COMPN_RenderStart']);z=int(attrs['COMPN_RenderEnd'])
# Independent transparent overlay, all typography stays native and editable.
base=solid(c,'V15_透明画布',(0,0,0),0)
def text(name,string,font,style,size,center,color,tracking=1):
 x=named(c,'TextPlus',name);setv(x,{'UseFrameFormatSettings':0,'Width':1920,'Height':1080,'StyledText':string,'Font':font,'Style':style,'Size':size,'Center':{1:center[0],2:center[1]},'Red1':color[0],'Green1':color[1],'Blue1':color[2],'Alpha1':1,'Tracking':tracking});return x
main=text('V15_书法校名','文汇中学','Songti SC','Black',.028,(.882,.918),(.97,.94,.85),1.08)
shadow=text('V15_校名柔影','文汇中学','Songti SC','Black',.028,(.8826,.917),(.035,.065,.058),1.08)
base=merge(c,base,shadow,'V15_校名影合成',.65)
base=merge(c,base,main,'V15_校名合成',.94)
sub=text('V15_集团副标','教育集团','Songti SC','Regular',.010,(.882,.873),(.89,.82,.65),1.6)
ss=text('V15_副标柔影','教育集团','Songti SC','Regular',.010,(.8826,.872),(.025,.045,.035),1.6)
base=merge(c,base,ss,'V15_副标影合成',.6);base=merge(c,base,sub,'V15_副标合成',.95)
# Fine golden underline is always present; a low-key light travels across in a 250-frame cycle.
line=solid(c,'V15_金线',(.73,.62,.38));mask=named(c,'RectangleMask','V15_金线轮廓');setv(mask,{'Center':{1:.882,2:.892},'Width':.126,'Height':.00105,'SoftEdge':.00035});assert line.ConnectInput('EffectMask',mask)
base=merge(c,base,line,'V15_恒定细金线',.58)
light=solid(c,'V15_流光',(.98,.88,.62));lm=named(c,'RectangleMask','V15_流光羽化');setv(lm,{'Center':{1:.882,2:.892},'Width':.016,'Height':.003,'SoftEdge':.006});assert light.ConnectInput('EffectMask',lm)
# Cosine movement is differentiable at the loop boundary. Opacity falls to zero there.
u=f'((time-{a})%250)/250'
lm.Center.SetExpression(f'Point(0.819+0.126*(0.5-0.5*cos(6.28318530718*({u}))),0.892)')
mg=merge(c,base,light,'V15_十秒循环流光');mg.Blend.SetExpression(f'0.32*(sin(3.14159265359*({u})))^4')
out=c.FindToolByID('MediaOut');assert out.ConnectInput('Input',mg)
assert it.ExportFusionComp(str(OUT/'文汇中学_原生动态角标_v15.comp'),1)
assert it.ImportFusionComp(str(OUT/'文汇中学_原生动态角标_v15.comp'));active_comp(it)
assert pm.SaveProject();r.OpenPage('edit')
for frame,label in [(30,'开篇'),(400,'实拍'),(1988,'深色照片包装'),(11070,'校长讲话'),(11450,'片尾')]:
 cap(p,t,frame,PRE/f'角标初稿_{label}.jpg')
(OUT/'bug_native_design.json').write_text(json.dumps({'duration':11507,'loop_frames':250,'render_start':a,'render_end':z,'main_font':'Songti SC','style':'Black','main_text':'文汇中学','sub_text':'教育集团','bounding_design_px':[1560,58,1840,150]},ensure_ascii=False,indent=2))
