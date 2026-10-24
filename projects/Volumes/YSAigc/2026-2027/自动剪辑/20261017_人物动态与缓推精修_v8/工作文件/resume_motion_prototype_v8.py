import sys,json,time
from pathlib import Path
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';SEQ=OUT/'运动连续帧原型';folder=SEQ/'after';folder.mkdir(exist_ok=True)
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool();t=p.GetCurrentTimeline();assert t.GetName()=='学校_人物动态与缓推精修_v8_20261017'
v=t.GetItemListInTrack('video',1)[0];c=v.GetFusionCompByIndex(1);xf=c.FindTool('V8_GentleMotion');assert xf
a=int(c.GetAttrs()['COMPN_RenderStart']);z=int(c.GetAttrs()['COMPN_RenderEnd']);xf.Size=c.BezierSpline();values=[]
for frame in range(a,z+1):
    u=(frame-a)/(z-a);size=1+.03*u*u*(3-2*u);xf.Size[frame]=size;values.append(size)
assert abs(xf.GetInput('Size',a)-1)<1e-7 and abs(xf.GetInput('Size',z)-1.03)<1e-7
assert v.ExportFusionComp(str(OUT/'prototype-v8-opening-motion.comp'),1)
assert r.OpenPage('edit') and pm.SaveProject()
for f in range(60):
    path=folder/f'{f:04d}.jpg';assert not path.exists()
    assert t.SetCurrentTimecode(f'00:00:{f//25:02d}:{f%25:02d}');time.sleep(.10);assert p.ExportCurrentFrameAsStill(str(path))
    if (f+1)%20==0:print('V8_PROTOTYPE_FRAMES','after',f+1,flush=True)
(OUT/'motion_prototype_v8.json').write_text(json.dumps({'timeline':t.GetName(),'start':0,'duration_frames':60,'fps':25,'composition_range':[a,z],'curve':'smoothstep; native float Transform Size at every source frame','size_values':values,'filter_default':xf.GetInput('FilterMethod'),'baseline_frames':str(SEQ/'before'),'animated_frames':str(SEQ/'after'),'media_and_fade_preserved':True},ensure_ascii=False,indent=2))
assert t.SetCurrentTimecode('00:00:00:20') and pm.SaveProject();print('V8_MOTION_PROTOTYPE_READY',flush=True)
