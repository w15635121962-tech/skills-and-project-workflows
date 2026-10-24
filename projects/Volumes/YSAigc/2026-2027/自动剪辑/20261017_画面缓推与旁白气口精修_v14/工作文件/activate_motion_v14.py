from common_v14 import *
import shutil
r,pm,p,mp,t=connect();before=json.loads((OUT/'live_before_v14.json').read_text());records=json.loads((OUT/'native_motion_applied_v14.json').read_text());assert len(records)==27
for parent,name in [(PRE,'缓推后'),(PRE/'连续运动核验','书写_缓推'),(PRE/'连续运动核验','配画试听')]:
 path=parent/name;archive=parent/(name+'_未激活旧样本')
 if path.exists() and not archive.exists():path.rename(archive)
for filename in ['native_motion_applied_v14.json','continuous_capture_v14.json']:
 path=OUT/filename;archive=path.with_name(path.stem+'_首次未激活记录'+path.suffix)
 if path.exists() and not archive.exists():shutil.copy2(path,archive)
for i,row in enumerate(records,1):
 tr,st=row['track'],row['start'];it=next(x for x in t.GetItemListInTrack('video',tr) if x.GetStart()==st);assert t.SetCurrentTimecode(tc(st+row['duration']//2))
 if it.GetFusionCompCount()==0:
  c=it.ImportFusionComp(str(OUT/f'原生缓推_{tr}_{st}.comp'));assert c;c.SetPrefs({'Comp.FrameFormat.Width':1920,'Comp.FrameFormat.Height':1080,'Comp.FrameFormat.Rate':25})
 names=it.GetFusionCompNameList();assert len(names)==1;name=next(iter(names.values())) if isinstance(names,dict) else names[0];c=it.LoadFusionCompByName(name);assert c and c.FindTool('V14_StaticGentlePush');assert it.GetFusionCompCount()==1
 row['active_composition']=name;row['explicit_native_load_performed']=True
 if i%6==0:print('V14_COMPS_ACTIVATED',i,flush=True)
assert pm.SaveProject();assert pm.CloseProject(p);p=pm.LoadProject(PROJECT);assert p;t=p.GetCurrentTimeline();assert t.GetName()==TIMELINE;assert r.OpenPage('edit');qa=[]
for i,row in enumerate(records,1):
 st,tr,N=row['start'],row['track'],row['duration'];it=next(x for x in t.GetItemListInTrack('video',tr) if x.GetStart()==st);assert it.GetFusionCompCount()==1;c=it.GetFusionCompByIndex(1);xf=c.FindTool('V14_StaticGentlePush');assert xf;row['composition_persisted_after_reopen']=True
 frames=[]
 for label,f in [('入',st),('中',st+N//2),('出',st+N-1)]:
  path=PRE/'缓推后'/f'{tr}_{st}_{label}.jpg';im=cap(p,t,f,path,.28);frames.append({'label':label,'frame':f,'path':str(path)})
  if label=='中':
   delta=float(abs(np.array(im,float)-np.array(Image.open(row['before']),float)).mean());assert delta>.05,(st,delta);qa.append({'track':tr,'start':st,'native_midframe_mean_rgb_difference':delta,'not_identical_to_unmodified_source':True})
 row['after_frames']=frames
 if i%6==0:print('V14_ACTUAL_PUSH_CAPTURES',i,flush=True)
video_unchanged(t,before,{(x['track'],x['start']) for x in records});assert graphs(t)==before['graphs'];assert pm.SaveProject();(OUT/'native_motion_applied_v14.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));(OUT/'native_motion_actual_output_qa_v14.json').write_text(json.dumps({'explicitly_activated':27,'persisted_after_reopen':27,'actual_frames':81,'midframe_output_checks':qa,'all_midframes_show_actual_transform':True,'initial_unactivated_attempt_preserved_as_history':True},ensure_ascii=False,indent=2));print('V14_ACTUAL_MOTION_ACTIVATED_AND_VERIFIED',len(records),flush=True)
