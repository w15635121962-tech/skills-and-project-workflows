import sys,json,math,copy
from pathlib import Path
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';plan=json.loads((OUT/'deep_edit_plan_v6.json').read_text());groups=json.loads((OUT/'native_changes_v6.json').read_text());before=json.loads((OUT/'live_before_v6.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool();base=p.GetCurrentTimeline();assert p.GetName()=='学校' and base.GetName()==plan['base_timeline']
def snap(t):
 return {typ:[{'track':k,'enabled':t.GetIsTrackEnabled(typ,k),'locked':t.GetIsTrackLocked(typ,k),'name':t.GetTrackName(typ,k),'items':[{'name':it.GetName(),'start':it.GetStart(),'end':it.GetEnd(),'offset':it.GetLeftOffset(),'path':it.GetMediaPoolItem().GetClipProperty('File Path') if it.GetMediaPoolItem() else None,'properties':it.GetProperty(),'enabled':it.GetClipEnabled(),'fusion_count':it.GetFusionCompCount()} for it in t.GetItemListInTrack(typ,k)]} for k in range(1,t.GetTrackCount(typ)+1)] for typ in ['video','audio']}
assert snap(base)==before['snapshot'],'Inspect fresh manual changes before continuing'
assert plan['name'] not in [p.GetTimelineByIndex(i).GetName() for i in range(1,p.GetTimelineCount()+1)];assert pm.SaveProject();t=base.DuplicateTimeline(plan['name']);assert t and p.SetCurrentTimeline(t);assert snap(t)==before['snapshot'];assert r.OpenPage('edit')
items={v.GetStart():v for v in t.GetItemListInTrack('video',1)};titles={};oldstarts={x for g in groups for x in g['old_record_frames']};remove=[]
for start in sorted(oldstarts):
 v=items[start];assert not v.GetLinkedItems();remove.append(v)
for g in groups:
 if g['preserve_title']:
  v=items[g['record_frame']];c=v.GetFusionCompByIndex(1);text=c.FindToolByID('TextPlus');assert text;titles[v.GetStart()]=text.GetInput('StyledText')
assert t.DeleteClips(remove,False)
folder=next((f for f in mp.GetRootFolder().GetSubFolderList() if f.GetName()=='全片深度精剪_v6_20261017'),None)
if not folder:folder=mp.AddSubFolder(mp.GetRootFolder(),'全片深度精剪_v6_20261017')
assert folder and mp.SetCurrentFolder(folder)
def walk(f):
 yield from f.GetClipList()
 for sf in f.GetSubFolderList():yield from walk(sf)
pool={v.GetClipProperty('File Path'):v for v in walk(mp.GetRootFolder())}
def media(path):
 if path not in pool:
  added=mp.ImportMedia([path]);assert added and len(added)==1;pool[path]=added[0]
 return pool[path]
def info(s,track):
 m=media(s['path']);fps=float(m.GetClipProperty('FPS'));assert abs(fps-s['fps'])<.001
 a=s.get('source_start_frame',round(s['in']*fps));count=s.get('source_count_frames',math.ceil(s['length_frames']/25*fps-1e-8))
 return {'mediaPoolItem':m,'startFrame':a,'endFrame':a+count,'mediaType':1,'trackIndex':track,'recordFrame':s['record_frame']}
segments=[s for g in groups for s in g['segments']];added=mp.AppendToTimeline([info(s,1) for s in segments]);assert added and len(added)==len(segments)
native={}
for s,v in zip(segments,added):
 assert v.GetStart()==s['record_frame'] and v.GetDuration()==s['length_frames'],(s['record_frame'],v.GetDuration(),s['length_frames'])
 assert v.GetMediaPoolItem().GetClipProperty('Online Status')=='Online'
 if s['log']:assert v.GetNodeGraph().SetLUT(1,'Sony/SLog3SGamut3.CineToLC-709TypeA.cube')
 v.SetClipColor('Blue');native[s['record_frame']]=v;print('V6_PICTURE',s['record_frame']/25,s['name'],s['length_frames'],flush=True)
def school_caption(v,text):
 c=v.AddFusionComp();assert c;mi=c.FindToolByID('MediaIn');mo=c.FindToolByID('MediaOut');bg=c.AddTool('Background');rect=c.AddTool('RectangleMask');tx=c.AddTool('TextPlus');m1=c.AddTool('Merge');m2=c.AddTool('Merge');assert all([mi,mo,bg,rect,tx,m1,m2])
 c.SetPrefs({'Comp.FrameFormat.Width':1280,'Comp.FrameFormat.Height':720,'Comp.FrameFormat.Rate':25});first=c.GetAttrs()['COMPN_RenderStart'];last=c.GetAttrs()['COMPN_RenderEnd'];clock=float(v.GetMediaPoolItem().GetClipProperty('FPS'))/25
 bg.SetInput('UseFrameFormatSettings',1)
 for k,val in [('TopLeftRed',.035),('TopLeftGreen',.045),('TopLeftBlue',.05),('TopLeftAlpha',.4)]:bg.SetInput(k,val)
 rect.SetInput('Center',{1:.5,2:.115});rect.SetInput('Width',.64);rect.SetInput('Height',.085);rect.SetInput('SoftEdge',.004);assert bg.ConnectInput('EffectMask',rect)
 for k,val in [('UseFrameFormatSettings',1),('StyledText',text),('Font','Heiti SC'),('Style','Light'),('Size',.033),('Center',{1:.5,2:.115}),('Red1',.97),('Green1',.97),('Blue1',.94),('Alpha1',1)]:tx.SetInput(k,val)
 assert m1.ConnectInput('Background',mi) and m1.ConnectInput('Foreground',bg);assert m2.ConnectInput('Background',m1) and m2.ConnectInput('Foreground',tx);assert mo.ConnectInput('Input',m2)
 fade=min(12,max(6,v.GetDuration()//6))*clock
 for m in [m1,m2]:m.Blend=c.BezierSpline();m.Blend[first]=0;m.Blend[first+fade]=1;m.Blend[last-fade]=1;m.Blend[last]=0
 assert tx.GetInput('StyledText')==text;assert v.ExportFusionComp(str(OUT/f'v6-school-{v.GetStart()}.comp'),1)
 return {'start':v.GetStart(),'duration':v.GetDuration(),'text':text,'source_clock_range':[first,last]}
caption_records=[school_caption(native[start],text) for start,text in titles.items()]
# Closing picture receives only the picture fade. The matching brand title remains independently editable on V2.
closing=native[11407];c=closing.AddFusionComp();assert c;mi=c.FindToolByID('MediaIn');mo=c.FindToolByID('MediaOut');bc=c.AddTool('BrightnessContrast');assert bc.ConnectInput('Input',mi);bc.Gain=c.BezierSpline();bc.Gain[0]=1;bc.Gain[69]=1;bc.Gain[99]=0;assert mo.ConnectInput('Input',bc);assert closing.ExportFusionComp(str(OUT/'v6-closing-picture.comp'),1)
overlays=plan['interview_overlays_v6'];ov=mp.AppendToTimeline([info(s,2) for s in overlays]);assert ov and len(ov)==2
for s,v in zip(overlays,ov):
 assert v.GetStart()==s['record_frame'] and v.GetDuration()==s['length_frames'];assert v.GetNodeGraph().SetLUT(1,'Sony/SLog3SGamut3.CineToLC-709TypeA.cube');v.SetClipColor('Cyan');assert v.SetName('校长原声补画｜'+s['intent']);print('V6_INTERVIEW_BROLL',v.GetStart()/25,v.GetDuration()/25,flush=True)
closing_spec=next(s for s in plan['shots'] if s['record_frame']==11407);title_added=mp.AppendToTimeline([info(closing_spec,2)]);assert title_added and len(title_added)==1;title=title_added[0]
c=title.ImportFusionComp(str(OUT/'baseline-opening-title.comp'));assert c and title.GetFusionCompCount()==1 and not c.FindToolByID('MediaIn');assert c.GetAttrs()['COMPN_RenderEnd']==99
for node,alpha in [('Template',1),('Text1',1),('Text2',.30),('Text3',.30)]:
 text=c.FindTool(node);assert text;text.Alpha1=c.BezierSpline();text.Alpha1[0]=alpha;text.Alpha1[99]=alpha
fade=c.FindTool('Merge4');assert fade;fade.Blend=c.BezierSpline();fade.Blend[0]=0;fade.Blend[12]=1;fade.Blend[69]=1;fade.Blend[99]=0
assert title.SetName('汇启新章 · 共育未来｜片尾宋体品牌呼应');assert title.ExportFusionComp(str(OUT/'v6-closing-title.comp'),1)
assert t.SetTrackName('video',1,'画面_全片深度精剪_人文与科学');assert t.SetTrackName('video',2,'片名与采访补画_独立可编辑')
assert t.AddMarker(3,'Green','v6 全片深度精剪','保留完整旁白及460.28秒。实验/师生语义纠偏、体育动作、照片连段、两处采访补画与同行片尾。',1,'v6-deep-edit')
after=snap(t);assert after['audio']==before['snapshot']['audio'];assert after['video'][1]['items'][0]==before['snapshot']['video'][1]['items'][0]
newstarts={s['record_frame'] for s in segments};assert [v for v in before['snapshot']['video'][0]['items'] if v['start'] not in oldstarts]==[v for v in after['video'][0]['items'] if v['start'] not in newstarts]
v1=t.GetItemListInTrack('video',1);assert len(v1)==121 and t.GetEndFrame()==11507;assert all(a.GetEnd()==b.GetStart() for a,b in zip(v1,v1[1:]));assert len(t.GetItemListInTrack('video',2))==4;assert pm.SaveProject();assert t.SetCurrentTimecode('00:00:00:20')
(OUT/'native_build_v6.json').write_text(json.dumps({'timeline':t.GetName(),'duration_seconds':460.28,'fps':25,'picture_count':121,'revised_groups':len(groups),'old_picture_items_revised':len(oldstarts),'new_picture_items':len(segments),'interview_cutaway_count':2,'rebuilt_school_captions':caption_records,'audio_preserved':True,'untouched_picture_preserved':True,'opening_title_preserved':True,'principal_underlying_video_preserved':True,'snapshot':after},ensure_ascii=False,indent=2))
print('V6_NATIVE_COMPLETE',flush=True)
