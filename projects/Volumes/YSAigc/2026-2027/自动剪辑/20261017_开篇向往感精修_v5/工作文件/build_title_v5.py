import sys,json,time
from pathlib import Path
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'开篇预览'
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool();base=p.GetCurrentTimeline();assert p.GetName()=='学校'
name='学校_开篇向往感精修_v5_20261017';assert base.GetName()=='学校_全片复核精修_v4_20261017'
assert name not in [p.GetTimelineByIndex(i).GetName() for i in range(1,p.GetTimelineCount()+1)]
t=base.DuplicateTimeline(name);assert t and p.SetCurrentTimeline(t);assert r.OpenPage('edit')
title=t.GetItemListInTrack('video',2)[0];assert title.GetStart()==383 and title.GetDuration()==125
c=title.GetFusionCompByIndex(1);assert c
for node,content,size,xy,font,style,color,alpha in [
 ('Template','汇启新章 · 共育未来',.049,(.335,.292),'Songti SC','Regular',(.99,.97,.91),1),
 ('Text1','文汇中学教育集团',.020,(.335,.195),'Heiti SC','Light',(.98,.96,.91),1),
 ('Text2','汇启新章 · 共育未来',.049,(.3358,.2906),'Songti SC','Regular',(.06,.065,.055),.30),
 ('Text3','文汇中学教育集团',.020,(.3358,.1936),'Heiti SC','Light',(.06,.065,.055),.30)]:
  v=c.FindTool(node);assert v;v.SetInput('StyledText',content);v.SetInput('Size',size);v.SetInput('Center',{1:xy[0],2:xy[1]});v.SetInput('Font',font);v.SetInput('Style',style)
  for k,val in zip(['Red1','Green1','Blue1'],color):v.SetInput(k,val)
  v.Alpha1=c.BezierSpline();v.Alpha1[0]=alpha;v.Alpha1[124]=alpha
  assert v.GetInput('Font')==font and v.GetInput('StyledText')==content
rule=c.AddTool('Background');mask=c.AddTool('RectangleMask');merge=c.AddTool('Merge');assert rule and mask and merge
rule.SetAttrs({'TOOLS_Name':'V5_WarmGoldRule'});mask.SetAttrs({'TOOLS_Name':'V5_RuleMask'});merge.SetAttrs({'TOOLS_Name':'V5_TitleRuleMerge'})
rule.SetInput('UseFrameFormatSettings',1)
for k,v in [('TopLeftRed',.83),('TopLeftGreen',.74),('TopLeftBlue',.52),('TopLeftAlpha',.8)]:rule.SetInput(k,v)
mask.SetInput('Center',{1:.335,2:.237});mask.SetInput('Width',.135);mask.SetInput('Height',.0012);mask.SetInput('SoftEdge',0)
assert rule.ConnectInput('EffectMask',mask);assert merge.ConnectInput('Background',c.FindTool('Merge3')) and merge.ConnectInput('Foreground',rule)
fade=c.FindTool('Merge4');assert fade.ConnectInput('Foreground',merge);fade.Blend=c.BezierSpline();fade.Blend[0]=0;fade.Blend[20]=1;fade.Blend[104]=1;fade.Blend[124]=0
assert title.SetName('汇启新章 · 共育未来｜书院气韵·宋体留白')
assert title.ExportFusionComp(str(OUT/'v5-independent-title.comp'),1);assert pm.SaveProject()
assert t.SetCurrentTimecode('00:00:17:05');time.sleep(.4);path=PRE/'片名样张_初校.jpg';assert not path.exists();assert p.ExportCurrentFrameAsStill(str(path))
(OUT/'title_build_v5.json').write_text(json.dumps({'timeline':t.GetName(),'title_start':383,'title_duration':125,'font':'Songti SC Regular','all_audio_untouched':True,'sample':str(path)},ensure_ascii=False,indent=2))
print('V5_TITLE_READY',path,flush=True)
