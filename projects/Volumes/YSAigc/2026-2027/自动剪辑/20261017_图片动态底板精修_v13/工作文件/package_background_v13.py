from common_v13 import *

HISTORY={1871,1980,2183,2347,6982,9378}
SCIENCE={3749,7086,8284,9960}
PALETTES={
 'history':{'low':(16/255,43/255,40/255),'high':(38/255,60/255,50/255)},
 'humanities':{'low':(16/255,56/255,51/255),'high':(27/255,72/255,64/255)},
 'science':{'low':(16/255,46/255,54/255),'high':(24/255,68/255,74/255)}}

def setvals(tool,values):
 for k,v in values.items():tool.SetInput(k,v)
def named(c,typ,name):
 x=c.AddTool(typ);assert x,typ;x.SetAttrs({'TOOLS_Name':name});assert x.GetAttrs()['TOOLS_Name']==name;return x
def solid(c,name,color,alpha=1):
 x=named(c,'Background',name);setvals(x,{'UseFrameFormatSettings':0,'Width':1920,'Height':1080,'TopLeftRed':color[0],'TopLeftGreen':color[1],'TopLeftBlue':color[2],'TopLeftAlpha':alpha});return x
def merge(c,bg,fg,name):
 m=named(c,'Merge',name);assert m.ConnectInput('Background',bg) and m.ConnectInput('Foreground',fg);return m
def animate(c,tool,key,values,a):
 setattr(tool,key,c.BezierSpline())
 field=getattr(tool,key)
 for i,v in enumerate(values):field[a+i]=v
def moving_point(tool,key,x,y,speed,a,N):
 field=getattr(tool,key);expression=f'Point({x:.12f}+{speed:.12f}*(time-{a})/{max(1,N-1)},{y:.12f})';field.SetExpression(expression);assert field.GetExpression()==expression
 first=tool.GetInput(key,a);last=tool.GetInput(key,a+N-1);assert abs(last[1]-first[1]-speed)<1e-7,(first,last)

def build(c,g,timeline):
 a=int(c.GetAttrs()['COMPN_RenderStart']);z=int(c.GetAttrs()['COMPN_RenderEnd']);N=z-a+1;assert N==g['length']
 first=c.FindTool('细金横线');mi=c.FindToolByID('MediaIn');assert first and mi
 # All prior original title/line/photo nodes stay; a prototype revision replaces only our new background nodes.
 assert first.ConnectInput('Background',mi)
 for x in list(c.GetToolList(False).values()):
  if x.GetAttrs()['TOOLS_Name'].startswith('V13_'):x.Delete()
 kind='history' if g['start'] in HISTORY else 'science' if g['start'] in SCIENCE else 'humanities';colors=PALETTES[kind]
 noise=named(c,'FastNoise','V13_有机流光底');setvals(noise,{'UseFrameFormatSettings':0,'Width':1920,'Height':1080,'Detail':1.4,'Contrast':1.05,'Brightness':0,'XScale':2.3,'YScale':1.7,'SeetheRate':0,'Discontinuous':0,'Color1Red':colors['low'][0],'Color1Green':colors['low'][1],'Color1Blue':colors['low'][2],'Color1Alpha':1,'Color2Red':colors['high'][0],'Color2Green':colors['high'][1],'Color2Blue':colors['high'][2],'Color2Alpha':1})
 phase=.35+g['start']*.00043;rate=.002 if g['start']!=7509 else .0013
 expression=f'{phase:.8f}+{rate:.8f}*(time-{a})';noise.Seethe.SetExpression(expression);assert noise.Seethe.GetExpression()==expression
 # A broad warm reflection stays behind the photos and text.
 glow=solid(c,'V13_暖金漫反射',(.60,.45,.25),1)
 gm=named(c,'EllipseMask','V13_暖光柔边');setvals(gm,{'Width':1.4,'Height':1.05,'SoftEdge':.48,'Angle':-18});assert glow.ConnectInput('EffectMask',gm)
 speed=.032 if g['start']!=7509 else .018
 xs=.18+.1*math.sin(g['start']*.031)
 moving_point(gm,'Center',xs,.20+.06*math.sin(g['start']*.017),speed,a,N)
 bg=merge(c,noise,glow,'V13_底板暖光合成');bg.SetInput('Blend',.068 if kind=='history' else .048)
 # Soft window shadows drift smoothly across the entire native plate.
 for j in range(3):
  shade=solid(c,f'V13_窗影{j+1}',(0,0,0),.12 if g['start']!=7509 else .085);mask=named(c,'RectangleMask',f'V13_窗影柔边{j+1}');setvals(mask,{'Width':.105+(j%2)*.025,'Height':2.1,'Angle':-24,'SoftEdge':.045});assert shade.ConnectInput('EffectMask',mask)
  x0=-.16+j*.31+.045*math.sin(g['start']*.023)
  moving_point(mask,'Center',x0,.49,speed,a,N)
  bg=merge(c,bg,shade,f'V13_窗影合成{j+1}')
 photo_frames=[]
 for j,side in enumerate(['left','right']):
  item=next(it for it in timeline.GetItemListInTrack('video',3+j) if it.GetStart()==g['start']);pc=item.GetFusionCompByIndex(1);xf=pc.FindTool('V9_PhotoGentleMotion');pmg=pc.FindTool('单图透明画布');assert xf and pmg
  ca=pmg.GetInput('Center');cx,cy=ca[1],ca[2];pa=int(pc.GetAttrs()['COMPN_RenderStart']);w,h=g['photo_motion'][j]['source_dimensions'];sizes=[float(xf.GetInput('Size',pa+i)) for i in range(N)];assert abs(xf.GetInput('Angle') or 0)<1e-5
  widths=[(w*v+4)/1920 for v in sizes];heights=[(h*v+4)/1080 for v in sizes]
  shadow=solid(c,f'V13_{side}_柔影',(0,0,0),.40);sm=named(c,'RectangleMask',f'V13_{side}_柔影遮罩');setvals(sm,{'Center':{1:cx+.0025,2:cy-.0055},'SoftEdge':.025});animate(c,sm,'Width',widths,a);animate(c,sm,'Height',heights,a);assert shadow.ConnectInput('EffectMask',sm);bg=merge(c,bg,shadow,f'V13_{side}_柔影合成')
  frame=solid(c,f'V13_{side}_细边',(.43,.49,.42),.75);fm=named(c,'RectangleMask',f'V13_{side}_细边遮罩');setvals(fm,{'Center':{1:cx,2:cy},'SoftEdge':.0003});animate(c,fm,'Width',widths,a);animate(c,fm,'Height',heights,a);assert frame.ConnectInput('EffectMask',fm);bg=merge(c,bg,frame,f'V13_{side}_细边合成')
  photo_frames.append({'side':side,'center':[cx,cy],'dimensions':[w,h],'photo_size_first_mid_last':[sizes[0],sizes[N//2],sizes[-1]],'frame_width_first_mid_last':[widths[0],widths[N//2],widths[-1]],'frame_height_first_mid_last':[heights[0],heights[N//2],heights[-1]]})
 assert first.ConnectInput('Background',bg)
 text=[]
 for x in c.GetToolList(False).values():
  a0=x.GetAttrs();name=a0['TOOLS_Name']
  if a0['TOOLS_RegID']=='TextPlus':
   col=(.91,.885,.81) if name=='主题题签' else (176/255,191/255,182/255) if name=='资料标记' else (.83,.86,.80)
   setvals(x,{'Red1':col[0],'Green1':col[1],'Blue1':col[2]});text.append({'name':name,'text':x.GetInput('StyledText'),'color':col})
  elif a0['TOOLS_RegID']=='Background' and not name.startswith('V13_'):
   setvals(x,{'TopLeftRed':.60,'TopLeftGreen':.51,'TopLeftBlue':.34})
 assert abs(noise.GetInput('Seethe',a)-phase)<1e-5 and noise.GetInput('Seethe',z)>phase
 return {'start':g['start'],'length':g['length'],'kind':kind,'title':g['title'],'noise_expression':expression,'noise_start':noise.GetInput('Seethe',a),'noise_end':noise.GetInput('Seethe',z),'window_drift_pixels':speed*1920,'photo_frames':photo_frames,'text':text,'new_native_nodes':sum(x.GetAttrs()['TOOLS_Name'].startswith('V13_') for x in c.GetToolList(False).values())}
