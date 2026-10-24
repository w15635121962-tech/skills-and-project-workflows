from common_v19 import *
r,pm,p,mp,t=connect();baseline=json.loads((OUT/'live_before_v19.json').read_text());SPLIT=11042;SHIFT=1013;END=12520
plan=json.loads((OUT/'采访最终方案/four_speaker_plan_final.json').read_text());at=SPLIT
for x in plan:x['record_start']=at;at+=x['timeline_duration_frames_25fps'];x['record_end']=at
added=[it for it in t.GetItemListInTrack('video',3) if SPLIT<=it.GetStart()<12055];assert len(added)==4
by_path={it.GetMediaPoolItem().GetClipProperty('File Path'):it.GetMediaPoolItem() for it in added}
for it,x in zip(added,plan):
 assert (it.GetStart(),it.GetEnd(),it.GetLeftOffset())==(x['record_start'],x['record_end'],x['source_in_frame'])
 h,m,s,f=map(int,it.GetMediaPoolItem().GetClipProperty('Start TC').split(':'));tc_seconds=h*3600+m*60+s+f/25
 assert abs(it.GetSourceStartTime()-tc_seconds-x['source_in_sec'])<1e-7
 assert it.SetName('全员采访｜'+x['speaker_key']);assert it.SetClipColor('Blue');it.GetCurrentVersion();it.GetNodeGraph().GetNumNodes()
parent=next(p.GetTimelineByIndex(k) for k in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(k).GetName()==baseline['timeline']);clones=[]
for tr in range(1,5):
 for old in parent.GetItemListInTrack('video',tr):
  if old.GetStart()<SPLIT:continue
  row={'track':tr,'old_start':old.GetStart(),'new_start':old.GetStart()+SHIFT,'duration':old.GetDuration(),'source_start':old.GetSourceStartFrame(),'source_end':old.GetSourceStartFrame()+round(old.GetDuration()/25*float(old.GetMediaPoolItem().GetClipProperty('FPS'))),'properties':old.GetProperty(),'name':old.GetName(),'version':old.GetCurrentVersion(),'enabled':old.GetClipEnabled(),'color':old.GetClipColor(),'comp_files':[str(OUT/'原生片尾保留'/f'V{tr}_{old.GetStart()}_{c}.comp') for c in range(1,old.GetFusionCompCount()+1)]}
  clones.append((old,row))
assert len(t.GetItemListInTrack('video',5))==1
source=(OUT/'insert_interview_picture_v19.py').read_text()
exec(compile(source[source.index('# Keep the 10-second'):],str(OUT/'insert_interview_picture_v19.py'),'exec'))
