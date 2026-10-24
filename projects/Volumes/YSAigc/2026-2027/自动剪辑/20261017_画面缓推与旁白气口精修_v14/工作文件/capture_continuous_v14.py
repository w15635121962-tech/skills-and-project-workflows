from common_v14 import *
r,pm,p,mp,t=connect();before=json.loads((OUT/'live_before_v14.json').read_text());records=json.loads((OUT/'native_motion_applied_v14.json').read_text());assert len(records)==27;video_unchanged(t,before,{(x['track'],x['start']) for x in records});assert graphs(t)==before['graphs'];assert pm.SaveProject()
# Drop transient viewer buffers and verify the saved native effects before the continuous-frame check.
assert pm.CloseProject(p);time.sleep(.5);p=pm.LoadProject(PROJECT);assert p;t=p.GetCurrentTimeline();assert t.GetName()==TIMELINE;assert r.OpenPage('edit')
parent=next(p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()==before['timeline']);assert p.SetCurrentTimeline(parent);assert snap(parent)==before['snapshot']
for timeline,tag in [(parent,'书写_原版'),(t,'书写_缓推')]:
 assert p.SetCurrentTimeline(timeline);folder=PRE/'连续运动核验'/tag;folder.mkdir(parents=True,exist_ok=True)
 for i in range(57):
  cap(p,timeline,60+i,folder/f'{i:04d}.jpg',.16)
  if (i+1)%25==0:print('V14_BOOK_FRAMES',tag,i+1,flush=True)
assert p.SetCurrentTimeline(t);folder=PRE/'连续运动核验'/'配画试听';folder.mkdir(parents=True,exist_ok=True)
start,N=6335,260
for i in range(N):
 cap(p,t,start+i,folder/f'{i:04d}.jpg',.16)
 if (i+1)%40==0:print('V14_AV_FRAMES',i+1,flush=True)
(OUT/'continuous_capture_v14.json').write_text(json.dumps({'fps':25,'book_before':{'folder':str(PRE/'连续运动核验'/'书写_原版'),'timeline_start':60,'frames':57},'book_after':{'folder':str(PRE/'连续运动核验'/'书写_缓推'),'timeline_start':60,'frames':57},'av_preview':{'folder':str(folder),'timeline_start':start,'frames':N,'timeline_range_seconds':[start/25,(start+N)/25]},'source':'stable real native timeline renders at every timeline frame; no offline motion or interpolation added'},ensure_ascii=False,indent=2))
assert t.SetCurrentTimecode(tc(6380));assert pm.SaveProject();print('V14_CONTINUOUS_FRAMES_READY',flush=True)
