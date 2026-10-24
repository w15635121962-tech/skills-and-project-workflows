from common_v19 import *
r,pm,p,mp,t=connect();baseline=json.loads((OUT/'live_before_v19.json').read_text())
SPLIT=11042;SHIFT=1013;END=12520
plan=json.loads((OUT/'采访最终方案/four_speaker_plan_final.json').read_text())
assert sum(x['timeline_duration_frames_25fps'] for x in plan)==SHIFT
parent=next(p.GetTimelineByIndex(k) for k in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(k).GetName()==baseline['timeline'])
assert p.SetCurrentTimeline(parent);assert snap(parent)==baseline['snapshot'];assert p.SetCurrentTimeline(t)
assert t.GetEndFrame()==11507
comps=OUT/'原生片尾保留';comps.mkdir(exist_ok=True)
clones=[]
for tr in range(1,5):
 for old in parent.GetItemListInTrack('video',tr):
  if old.GetStart()<SPLIT:continue
  row={'track':tr,'old_start':old.GetStart(),'new_start':old.GetStart()+SHIFT,'duration':old.GetDuration(),'source_start':old.GetSourceStartFrame(),'source_end':old.GetSourceStartFrame()+round(old.GetDuration()/25*float(old.GetMediaPoolItem().GetClipProperty('FPS'))),'properties':old.GetProperty(),'name':old.GetName(),'version':old.GetCurrentVersion(),'enabled':old.GetClipEnabled(),'color':old.GetClipColor(),'comp_files':[]}
  for c in range(1,old.GetFusionCompCount()+1):
   file=comps/f'V{tr}_{old.GetStart()}_{c}.comp';assert old.ExportFusionComp(str(file),c);row['comp_files'].append(str(file))
  clones.append((old,row))
remove=[it for tr in range(1,5) for it in t.GetItemListInTrack('video',tr) if it.GetStart()>=SPLIT]
assert t.DeleteClips(remove,False)
newitems=mp.AppendToTimeline([{'mediaPoolItem':old.GetMediaPoolItem(),'startFrame':x['source_start'],'endFrame':x['source_end'],'recordFrame':x['new_start'],'trackIndex':x['track'],'mediaType':1} for old,x in clones]);assert len(newitems)==len(clones)
for it,(old,x) in zip(newitems,clones):
 assert (it.GetStart(),it.GetEnd(),it.GetSourceStartFrame())==(x['new_start'],x['new_start']+x['duration'],x['source_start'])
 assert it.SetName(x['name']);assert it.SetClipEnabled(x['enabled'])
 if x['color']:assert it.SetClipColor(x['color'])
 for k,v in x['properties'].items():
  if it.GetProperty(k)!=v:assert it.SetProperty(k,v),(k,v)
 for file in x['comp_files']:assert it.ImportFusionComp(file)
 if x['comp_files']:active_comp(it)
 it.GetCurrentVersion();it.GetVersionNameList(0);it.GetNodeGraph().GetNumNodes()
r.OpenPage('color');time.sleep(.8)
for it,(old,x) in zip(newitems,clones):
 assert old.CopyGrades([it]),x['name']
 current=it.GetCurrentVersion()
 if current['versionName']!=x['version']['versionName']:
  assert it.RenameVersionByName(current['versionName'],x['version']['versionName'],0)
 assert it.GetCurrentVersion()==x['version']
 assert it.GetProperty()==x['properties']
# Four new main-timeline camera items on the requested V3 layer.
media=mp.ImportMedia([x['source'] for x in plan]);assert len(media)==4;by_path={x.GetClipProperty('File Path'):x for x in media}
at=SPLIT
for x in plan:
 x['record_start']=at;at+=x['timeline_duration_frames_25fps'];x['record_end']=at
added=mp.AppendToTimeline([{'mediaPoolItem':by_path[x['source']],'startFrame':x['source_in_frame'],'endFrame':x['source_out_frame_exclusive'],'recordFrame':x['record_start'],'trackIndex':3,'mediaType':1} for x in plan]);assert len(added)==4 and at==12055
for it,x in zip(added,plan):
 assert (it.GetStart(),it.GetEnd(),it.GetLeftOffset())==(x['record_start'],x['record_end'],x['source_in_frame'])
 assert abs(it.GetSourceStartTime()-x['source_in_sec'])<1e-8
 assert it.SetName('全员采访｜'+x['speaker_key']);assert it.SetClipColor('Blue');it.GetCurrentVersion();it.GetNodeGraph().GetNumNodes()
# Keep the 10-second native corner animation continuous as the programme grows.
bug=t.GetItemListInTrack('video',5)[0];c=active_comp(bug);fade=c.FindTool('V15_片尾同步淡出');assert fade
fade.Blend.SetExpression(f'iif(time<{END-12},1,iif(time>{END-1},0,1-((time-{END-12})/11)^2*(3-2*((time-{END-12})/11))))')
bugfile=OUT/'原生角标_延长覆盖_v19.comp';assert bug.ExportFusionComp(str(bugfile),1)
carrier=by_path[plan[2]['source']]
newbug=mp.AppendToTimeline([{'mediaPoolItem':carrier,'startFrame':0,'endFrame':SHIFT,'recordFrame':11507,'trackIndex':5,'mediaType':1}])[0]
assert (newbug.GetStart(),newbug.GetEnd())==(11507,END);assert newbug.ImportFusionComp(str(bugfile));c2=active_comp(newbug)
u='((time+11507)%250)/250'
c2.FindTool('V15_流光羽化').Center.SetExpression(f'Point(0.819+0.126*(0.5-0.5*cos(6.28318530718*({u}))),0.892)')
c2.FindTool('V15_十秒循环流光').Blend.SetExpression(f'0.32*(sin(3.14159265359*({u})))^4')
c2.FindTool('V15_片尾同步淡出').Blend.SetExpression(f'iif(time<{SHIFT-12},1,iif(time>{SHIFT-1},0,1-((time-{SHIFT-12})/11)^2*(3-2*((time-{SHIFT-12})/11))))')
assert newbug.SetName(bug.GetName());assert bug.CopyGrades([newbug]);assert newbug.ExportFusionComp(str(OUT/'原生角标_新增尾段_v19.comp'),1)
assert newbug.ImportFusionComp(str(OUT/'原生角标_新增尾段_v19.comp'));active_comp(newbug)
assert bug.ExportFusionComp(str(bugfile),1);assert bug.ImportFusionComp(str(bugfile));active_comp(bug)
assert t.GetEndFrame()==END;assert pm.SaveProject()
(OUT/'interview_picture_inserted_v19.json').write_text(json.dumps({'split_frame':SPLIT,'shift_frames':SHIFT,'end_frame':END,'new_speakers':plan,'moved_original_clips':[x for old,x in clones],'corner_extension_range':[11507,END],'original_narration_and_slogans_intact':True},ensure_ascii=False,indent=2))
r.OpenPage('edit')
for x in plan:cap(p,t,(x['record_start']+x['record_end'])//2,PRE/f"采访_未匹配_{x['speaker_key']}.jpg")
print('INTERVIEW_PICTURE_INSERTED',len(added),'moved',len(clones),'end',END,flush=True)
