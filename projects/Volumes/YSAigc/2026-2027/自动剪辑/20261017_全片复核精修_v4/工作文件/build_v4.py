import sys,json,math,copy
from pathlib import Path
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';plan=json.loads((OUT/'refined_plan_v4.json').read_text());groups=json.loads((OUT/'native_change_groups_v4.json').read_text());before=json.loads((OUT/'live_before_v4.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='学校';mp=p.GetMediaPool();base=p.GetCurrentTimeline();assert base.GetName()==plan['base_timeline']
def snap(t):
 return {typ:[{'track':k,'enabled':t.GetIsTrackEnabled(typ,k),'locked':t.GetIsTrackLocked(typ,k),'name':t.GetTrackName(typ,k),'items':[{'name':it.GetName(),'start':it.GetStart(),'end':it.GetEnd(),'offset':it.GetLeftOffset(),'path':it.GetMediaPoolItem().GetClipProperty('File Path') if it.GetMediaPoolItem() else None,'properties':it.GetProperty(),'enabled':it.GetClipEnabled(),'fusion_count':it.GetFusionCompCount()} for it in t.GetItemListInTrack(typ,k)]} for k in range(1,t.GetTrackCount(typ)+1)] for typ in ['video','audio']}
assert snap(base)==before['snapshot'],'Preserve any manual edits; baseline drift requires review'
assert plan['name'] not in [p.GetTimelineByIndex(i).GetName() for i in range(1,p.GetTimelineCount()+1)]
assert pm.SaveProject();t=base.DuplicateTimeline(plan['name']);assert t and p.SetCurrentTimeline(t);assert snap(t)==before['snapshot'];assert r.OpenPage('edit')
items={v.GetStart():v for v in t.GetItemListInTrack('video',1)};remove=[]
for g in groups:
 v=items[g['record_frame']];assert v.GetDuration()==g['original_length_frames'] and v.GetMediaPoolItem().GetClipProperty('File Path')==g['old']['path'];assert not v.GetLinkedItems();remove.append(v)
assert t.DeleteClips(remove,False);assert t.GetEndFrame()==11507
folder=mp.AddSubFolder(mp.GetRootFolder(),'全片复核精修_v4_20261017');assert folder and mp.SetCurrentFolder(folder)
def walk(f):
 yield from f.GetClipList()
 for sf in f.GetSubFolderList():yield from walk(sf)
pool={x.GetClipProperty('File Path'):x for x in walk(mp.GetRootFolder())};new=[s for g in groups for s in g['segments']]
for s in new:
 if s['path'] not in pool:
  imported=mp.ImportMedia([s['path']]);assert imported and len(imported)==1;pool[s['path']]=imported[0]
infos=[]
for s in new:
 media=pool[s['path']];fps=float(media.GetClipProperty('FPS'));a=round(s['in']*fps);count=math.ceil(s['length_frames']/25*fps-1e-8);infos.append({'mediaPoolItem':media,'startFrame':a,'endFrame':a+count,'mediaType':1,'trackIndex':1,'recordFrame':s['record_frame']})
added=mp.AppendToTimeline(infos);assert added and len(added)==len(new)
for s,v in zip(new,added):
 assert v.GetStart()==s['record_frame'] and v.GetDuration()==s['length_frames'];assert v.GetMediaPoolItem().GetClipProperty('Online Status')=='Online'
 if s['log']:assert v.GetNodeGraph().SetLUT(1,'Sony/SLog3SGamut3.CineToLC-709TypeA.cube')
 v.SetClipColor('Blue');print('REVISED_PICTURE',v.GetStart()/25,s['name'],flush=True)
# Refine existing embedded identifiers without moving their picture or dialogue.
title_records=[]
for v in t.GetItemListInTrack('video',1):
 comp=v.GetFusionCompByIndex(1) if v.GetFusionCompCount() else None
 if not comp:continue
 text=comp.FindToolByID('TextPlus')
 if not text:continue
 # The opening title is already an independent verified track and is not touched here.
 merge1=comp.FindTool('Merge1');merge2=comp.FindTool('Merge2');bg=comp.FindTool('Background1');rect=comp.FindTool('Rectangle1');assert all([merge1,merge2,bg,rect]),v.GetStart()
 kind='school' if v.GetStart() in [3749,3832,3891,3954] else ('principal' if v.GetStart()==11042 else 'closing')
 clock=float(v.GetMediaPoolItem().GetClipProperty('FPS'))/25;first=comp.GetAttrs()['COMPN_RenderStart'];last=comp.GetAttrs()['COMPN_RenderEnd']
 text.Alpha1=comp.BezierSpline();text.Alpha1[first]=1;text.Alpha1[last]=1
 fade=min(12,max(6,v.GetDuration()//6))*clock
 for merge in [merge1,merge2]:
  merge.Blend=comp.BezierSpline();merge.Blend[first]=0;merge.Blend[first+fade]=1;merge.Blend[last-fade]=1;merge.Blend[last]=0
 if kind=='school':
  text.SetInput('Size',.033);text.SetInput('Center',{1:.5,2:.115});rect.SetInput('Center',{1:.5,2:.115});rect.SetInput('Width',.64);rect.SetInput('Height',.085);bg.SetInput('TopLeftAlpha',.4)
 elif kind=='closing':
  text.SetInput('Size',.040);text.SetInput('Center',{1:.5,2:.19});rect.SetInput('Center',{1:.5,2:.19});rect.SetInput('Width',.78);rect.SetInput('Height',.175);bg.SetInput('TopLeftAlpha',.3)
 assert v.ExportFusionComp(str(OUT/f'v4-title-{v.GetStart()}.comp'),1)
 title_records.append({'start':v.GetStart(),'duration':v.GetDuration(),'kind':kind,'text':text.GetInput('StyledText'),'fade_frames':fade});print('REFINED_TITLE',kind,v.GetStart(),flush=True)
assert len(title_records)==6
review=json.loads((OUT/'配音复核/v4_voice_review_markers.json').read_text())
for marker in review['markers']:assert t.AddMarker(marker['frame'],marker['color'],marker['name'],marker['note'],marker['duration'],'v4-voice-review')
assert t.AddMarker(1,'Green','v4 全片复核精修','完整配音再次转写及波形核查；16处画面/动作节奏修正，6处既有字幕淡入淡出；3:55一处字音待听辨。',1,'v4-audit')
after=snap(t);assert after['audio']==before['snapshot']['audio'];assert after['video'][1]==before['snapshot']['video'][1]
modified={g['record_frame'] for g in groups};old_untouched=[x for x in before['snapshot']['video'][0]['items'] if x['start'] not in modified];new_untouched=[x for x in after['video'][0]['items'] if x['start'] not in modified and x['start']!=4289];assert old_untouched==new_untouched
v1=t.GetItemListInTrack('video',1);assert len(v1)==121 and t.GetEndFrame()==11507;assert all(a.GetEnd()==b.GetStart() for a,b in zip(v1,v1[1:]));assert pm.SaveProject();assert t.SetCurrentTimecode('00:00:00:20')
(OUT/'native_build_v4.json').write_text(json.dumps({'timeline':t.GetName(),'duration_seconds':460.28,'video_count':121,'changed_original_picture_items':len(groups),'inserted_picture_segments':len(new),'refined_titles':title_records,'audio_preserved':True,'unmodified_picture_items_preserved':True,'opening_title_preserved':True,'snapshot':after},ensure_ascii=False,indent=2),encoding='utf-8');print('BUILT_V4',flush=True)
