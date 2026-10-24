from common_v9 import *
from PIL import Image, ImageOps

PAPER=(242,239,230)
INK=(.105,.17,.155)
GOLD=(.57,.46,.29)

def inp(tool,values):
    for key,val in values.items():tool.SetInput(key,val)

def label(comp,text,name,x,y,size,color=INK,font='Heiti SC',style='Light'):
    tx=comp.AddTool('TextPlus');assert tx
    tx.SetAttrs({'TOOLS_Name':name})
    inp(tx,{'StyledText':text,'Font':font,'Style':style,'Size':size,'Center':{1:x,2:y},'Red1':color[0],'Green1':color[1],'Blue1':color[2],'Alpha1':1,'UseFrameFormatSettings':0,'Width':1920,'Height':1080})
    return tx

def merge(comp,bg,fg,name):
    m=comp.AddTool('Merge');assert m and m.ConnectInput('Background',bg) and m.ConnectInput('Foreground',fg)
    m.SetAttrs({'TOOLS_Name':name});return m

def line(comp,bg,x,y,width,height,name,color=GOLD):
    solid=comp.AddTool('Background');mask=comp.AddTool('RectangleMask');assert solid and mask
    inp(solid,{'UseFrameFormatSettings':0,'Width':1920,'Height':1080,'TopLeftRed':color[0],'TopLeftGreen':color[1],'TopLeftBlue':color[2],'TopLeftAlpha':1})
    inp(mask,{'Center':{1:x,2:y},'Width':width,'Height':height,'SoftEdge':0})
    assert solid.ConnectInput('EffectMask',mask)
    return merge(comp,bg,solid,name)

def make_package(item,group):
    c=item.AddFusionComp();assert c
    c.SetPrefs({'Comp.FrameFormat.Width':1920,'Comp.FrameFormat.Height':1080,'Comp.FrameFormat.Rate':25})
    mi=c.FindToolByID('MediaIn');mo=c.FindToolByID('MediaOut');assert mi and mo
    bg=line(c,mi,.5,.815,.88,.0014,'细金横线')
    bg=line(c,bg,.5,.51,.0007,.56,'双图分隔')
    title=label(c,group['title'],'主题题签',.5,.874,.034)
    bg=merge(c,bg,title,'主题合成')
    for j,side in enumerate(['left','right']):
        x=.265 if j==0 else .735
        text=group.get(side+'_label','')
        if text:bg=merge(c,bg,label(c,text,'左图说明' if j==0 else '右图说明',x,.137,.024),'图注合成'+str(j))
    footer=label(c,'文汇中学教育集团  ·  资料影像','资料标记',.5,.065,.016,color=(.40,.43,.39))
    bg=merge(c,bg,footer,'资料标记合成');assert mo.ConnectInput('Input',bg)
    return c

def make_photo(item,path,side,length,kind='push'):
    im=ImageOps.exif_transpose(Image.open(path));w,h=im.size
    zoom=min(828/w,612/h)/1.018
    x=.265 if side=='left' else .735
    assert item.SetProperty({'ZoomX':1,'ZoomY':1,'Pan':0,'Tilt':0})
    c=item.GetFusionCompByIndex(1) if item.GetFusionCompCount() else item.AddFusionComp();assert c
    c.SetPrefs({'Comp.FrameFormat.Width':1920,'Comp.FrameFormat.Height':1080,'Comp.FrameFormat.Rate':25})
    mi=c.FindToolByID('MediaIn');mo=c.FindToolByID('MediaOut');xf=c.FindTool('V9_PhotoGentleMotion') or c.AddTool('Transform')
    assert mi and mo and xf and xf.ConnectInput('Input',mi)
    canvas=c.AddTool('Background');assert canvas
    inp(canvas,{'UseFrameFormatSettings':0,'Width':1920,'Height':1080,'TopLeftAlpha':0})
    merged=merge(c,canvas,xf,'单图透明画布')
    merged.SetInput('Center',{1:x,2:.51});assert mo.ConnectInput('Input',merged)
    xf.SetAttrs({'TOOLS_Name':'V9_PhotoGentleMotion'})
    inp(xf,{'Center':{1:.5,2:.5},'Pivot':{1:.5,2:.5}});xf.Size=c.BezierSpline()
    a=int(c.GetAttrs()['COMPN_RenderStart']);z=int(c.GetAttrs()['COMPN_RenderEnd'])
    assert z-a+1==length,(a,z,length)
    for f in range(a,z+1):
        u=(f-a)/max(1,z-a);v=u*u*(3-2*u);size=zoom*(1+.018*(v if kind=='push' else 1-v));xf.Size[f]=size
    assert item.SetClipColor('Blue')
    return {'source_dimensions':[w,h],'fusion_base_scale':zoom,'canvas':[1920,1080],'center':[x,.51],'source_clock':[a,z],'size_start':xf.GetInput('Size',a),'size_end':xf.GetInput('Size',z),'side':side}

def append_native(mp,pool,path,track,start,length,timeline):
    if str(path) not in pool:
        a=mp.ImportMedia([str(path)]);assert a and len(a)==1;pool[str(path)]=a[0]
    m=pool[str(path)]
    # Resolve 21 ignores still endFrame in an empty track. Precisely bound the
    # gap with two temporary one-frame video clips, then remove them unrippled.
    borders=[]
    if track>=3:
        existing=timeline.GetItemListInTrack('video',track)
        assert not any(it.GetStart()<=f<it.GetEnd() for it in existing for f in [start-1,start+length])
        donor=next(it.GetMediaPoolItem() for it in timeline.GetItemListInTrack('video',1) if it.GetName()=='C0206_Proxy.mov')
        borders=mp.AppendToTimeline([{'mediaPoolItem':donor,'startFrame':0,'endFrame':1,'mediaType':1,'trackIndex':track,'recordFrame':f} for f in [start-1,start+length]])
        assert borders and len(borders)==2 and all(it.GetDuration()==1 for it in borders)
    try:
        added=mp.AppendToTimeline([{'mediaPoolItem':m,'startFrame':0,'endFrame':length,'mediaType':1,'trackIndex':track,'recordFrame':start}])
    finally:
        if borders:assert timeline.DeleteClips(borders,False)
    assert added and len(added)==1
    it=added[0];assert it.GetStart()==start and it.GetDuration()==length,(start,length,it.GetStart(),it.GetDuration())
    return it
