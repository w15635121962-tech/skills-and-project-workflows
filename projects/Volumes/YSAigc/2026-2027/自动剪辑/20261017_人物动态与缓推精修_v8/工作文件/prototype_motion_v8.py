import sys,json,time
from pathlib import Path
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'精剪预览';SEQ=OUT/'运动连续帧原型';SEQ.mkdir(exist_ok=True)
before=json.loads((OUT/'live_before_v8.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool();base=p.GetCurrentTimeline()
assert p.GetName()=='学校' and base.GetName()==before['timeline']
name='学校_人物动态与缓推精修_v8_20261017'
assert name not in [p.GetTimelineByIndex(i).GetName() for i in range(1,p.GetTimelineCount()+1)]
def tc(f):
    sec,ff=divmod(f,25);mm,ss=divmod(sec,60);return f'00:{mm:02d}:{ss:02d}:{ff:02d}'
def capture(t,label):
    folder=SEQ/label;folder.mkdir(exist_ok=True)
    for frame in range(60):
        path=folder/f'{frame:04d}.jpg';assert not path.exists()
        assert t.SetCurrentTimecode(tc(frame));time.sleep(.10);assert p.ExportCurrentFrameAsStill(str(path))
        if (frame+1)%20==0:print('V8_PROTOTYPE_FRAMES',label,frame+1,flush=True)
assert r.OpenPage('edit');capture(base,'before')
t=base.DuplicateTimeline(name);assert t and p.SetCurrentTimeline(t)
v=t.GetItemListInTrack('video',1)[0];assert v.GetStart()==0 and v.GetDuration()==60 and v.GetFusionCompCount()==1
c=v.GetFusionCompByIndex(1);mi=c.FindToolByID('MediaIn');bc=c.FindToolByID('BrightnessContrast');assert mi and bc
xf=c.AddTool('Transform');assert xf;xf.SetAttrs({'TOOLS_Name':'V8_GentleMotion'})
assert xf.ConnectInput('Input',mi) and bc.ConnectInput('Input',xf)
xf.SetInput('Center',{1:.5,2:.5});xf.SetInput('Pivot',{1:.5,2:.5});xf.Size=c.BezierSpline()
start=int(c.GetAttrs()['COMPN_RenderStart']);end=int(c.GetAttrs()['COMPN_RenderEnd']);assert end-start==59
values=[]
for frame in range(start,end+1):
    u=(frame-start)/(end-start);size=1+.03*(u*u*(3-2*u));xf.Size[frame]=size;values.append(size)
assert abs(xf.GetInput('Size',start)-1)<1e-7 and abs(xf.GetInput('Size',end)-1.03)<1e-7
assert v.ExportFusionComp(str(OUT/'prototype-v8-opening-motion.comp'),1)
assert pm.SaveProject();capture(t,'after')
(OUT/'motion_prototype_v8.json').write_text(json.dumps({'timeline':name,'start':0,'duration_frames':60,'fps':25,'composition_range':[start,end],'curve':'smoothstep; native float Transform Size at every source frame','size_values':values,'filter_default':xf.GetInput('FilterMethod'),'baseline_frames':str(SEQ/'before'),'animated_frames':str(SEQ/'after'),'media_and_fade_preserved':True},ensure_ascii=False,indent=2))
assert t.SetCurrentTimecode('00:00:00:20') and pm.SaveProject();print('V8_MOTION_PROTOTYPE_READY',flush=True)
