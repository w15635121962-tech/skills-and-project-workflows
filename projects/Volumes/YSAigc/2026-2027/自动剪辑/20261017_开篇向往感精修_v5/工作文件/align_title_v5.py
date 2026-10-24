import sys,json,time
from pathlib import Path
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'开篇预览'
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool();t=p.GetCurrentTimeline();assert t.GetName()=='学校_开篇向往感精修_v5_20261017'
old=t.GetItemListInTrack('video',2)[0];assert old.GetStart()==383 and old.GetDuration()==125
saved=OUT/'v5-independent-title.comp';assert saved.exists()
seed=next(v for v in t.GetItemListInTrack('video',1) if v.GetStart()==340).GetMediaPoolItem();assert seed
assert t.DeleteClips([old],False)
added=mp.AppendToTimeline([{'mediaPoolItem':seed,'startFrame':400,'endFrame':568,'mediaType':1,'trackIndex':2,'recordFrame':340}]);assert added and len(added)==1
title=added[0];assert title.GetStart()==340 and title.GetDuration()==168
c=title.ImportFusionComp(str(saved));assert c and title.GetFusionCompCount()==1
# A native, independent Fusion overlay. The source seed is disconnected: only text/rule reaches MediaOut.
assert not c.FindToolByID('MediaIn');assert c.FindToolByID('MediaOut') and c.FindTool('Merge4')
first=c.GetAttrs()['COMPN_RenderStart'];last=c.GetAttrs()['COMPN_RenderEnd'];assert first==0 and last==167,(first,last)
for node,alpha in [('Template',1),('Text1',1),('Text2',.30),('Text3',.30)]:
 v=c.FindTool(node);assert v;v.Alpha1=c.BezierSpline();v.Alpha1[first]=alpha;v.Alpha1[last]=alpha
fade=c.FindTool('Merge4');fade.Blend=c.BezierSpline();fade.Blend[first]=0;fade.Blend[first+18]=1;fade.Blend[last-18]=1;fade.Blend[last]=0
assert title.SetName('汇启新章 · 共育未来｜书院气韵·独立可编辑片名')
assert title.ExportFusionComp(str(OUT/'v5-independent-title-aligned.comp'),1)
assert t.SetTrackName('video',2,'片名_宋体留白_13秒60同步旁白')
assert t.GetEndFrame()==11507;assert pm.SaveProject();assert t.SetCurrentTimecode('00:00:17:05');time.sleep(.35)
path=PRE/'片名样张_旁白对齐.jpg';assert not path.exists();assert p.ExportCurrentFrameAsStill(str(path))
(OUT/'title_aligned_v5.json').write_text(json.dumps({'start':340,'duration':168,'fusion_range':[first,last],'fade_frames':18,'source_seed_disconnected':True,'description':'Native video item on V2 with independent Text+ composition; seed media is not connected to output; no rasterized title or inserted generator ripple.'},ensure_ascii=False,indent=2))
print('TITLE_ALIGNED',first,last,path,flush=True)
