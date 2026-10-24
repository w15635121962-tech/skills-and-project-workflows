from common_v14 import *
r,pm,p,mp,t=connect();records=json.loads((OUT/'native_motion_applied_v14.json').read_text());assert len(records)==27;assert r.OpenPage('edit')
for row in records:
 it=next(x for x in t.GetItemListInTrack('video',row['track']) if x.GetStart()==row['start']);assert it.GetFusionCompCount()==1 and it.GetFusionCompByIndex(1).FindTool('V14_StaticGentlePush')
for folder,st,N in [(PRE/'连续运动核验'/'书写_缓推',60,57),(PRE/'连续运动核验'/'配画试听',6335,260)]:
 folder.mkdir(parents=True,exist_ok=True)
 for i in range(N):
  cap(p,t,st+i,folder/f'{i:04d}.jpg',.16)
  if (i+1)%40==0:print('V14_ACTUAL_CONTINUOUS',st,i+1,flush=True)
 if st==60:
  old=np.array(Image.open(PRE/'连续运动核验'/'书写_原版'/'0056.jpg'),float);new=np.array(Image.open(folder/'0056.jpg'),float);delta=float(abs(old-new).mean());assert delta>.05;print('V14_ACTUAL_FINAL_FRAME_DELTA',delta,flush=True)
(OUT/'continuous_capture_v14.json').write_text(json.dumps({'fps':25,'book_before':{'folder':str(PRE/'连续运动核验'/'书写_原版'),'timeline_start':60,'frames':57},'book_after':{'folder':str(PRE/'连续运动核验'/'书写_缓推'),'timeline_start':60,'frames':57},'av_preview':{'folder':str(PRE/'连续运动核验'/'配画试听'),'timeline_start':6335,'frames':260,'timeline_range_seconds':[253.4,263.8]},'native_compositions_explicitly_active_and_reopened':27,'source':'actual native timeline per-frame renders after explicit composition activation; no offline movement added','initial_unactivated_outputs_preserved_as_history':True},ensure_ascii=False,indent=2));assert t.SetCurrentTimecode(tc(6380));assert pm.SaveProject();print('V14_FINAL_CONTINUOUS_READY',flush=True)
