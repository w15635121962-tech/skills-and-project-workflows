from common_v14 import *
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--final',action='store_true');args=parser.parse_args()
first=[60,234,942,2595,3003,3675,4609,4854,5717,6260,6370,6420,6909,7965,9092,9243,9690,10162,10622,10850]
selected=json.loads((OUT/'motion_candidates_v14.json').read_text())['selected'] if args.final else [{'track':1,'start':st,'amplitude':.025 if st in [942,3003,3675,6260,9092] else .02} for st in first]
r,pm,p,mp,t=connect();before=json.loads((OUT/'live_before_v14.json').read_text());assert r.OpenPage('edit');recordpath=OUT/'native_motion_applied_v14.json';records=json.loads(recordpath.read_text()) if recordpath.exists() else []
for row in selected:
 tr,st=int(row['track']),int(row['start']);amp=float(row['amplitude']);assert .01<=amp<=.025
 if any(x['track']==tr and x['start']==st for x in records):continue
 it=next(x for x in t.GetItemListInTrack('video',tr) if x.GetStart()==st);old=next(x for x in before['fusion'] if x['track']==tr and x['start']==st);assert it.GetDuration()==old['duration'] and it.GetFusionCompCount()==0 and old['fusion_comp_count']==0
 n=int(it.GetDuration());mid=st+n//2;baseline=PRE/'缓推前'/f'{tr}_{st}.jpg';cap(p,t,mid,baseline,.45)
 c=it.AddFusionComp();assert c;mi=c.FindToolByID('MediaIn');mo=c.FindToolByID('MediaOut');assert mi and mo
 a=int(c.GetAttrs()['COMPN_RenderStart']);z=int(c.GetAttrs()['COMPN_RenderEnd']);assert z-a+1==n,(st,a,z,n)
 c.Lock()
 try:
  xf=c.AddTool('Transform');assert xf;xf.SetAttrs({'TOOLS_Name':'V14_StaticGentlePush'});assert xf.ConnectInput('Input',mi) and mo.ConnectInput('Input',xf)
  xf.SetInput('Center',{1:.5,2:.5});xf.SetInput('Pivot',{1:.5,2:.5});xf.Size=c.BezierSpline()
  for i in range(n):
   u=i/max(1,n-1);xf.Size[a+i]=1+amp*(u*u*(3-2*u))
  assert abs(xf.GetInput('Size',a)-1)<1e-7 and abs(xf.GetInput('Size',z)-(1+amp))<1e-7
 finally:c.Unlock()
 assert it.ExportFusionComp(str(OUT/f'原生缓推_{tr}_{st}.comp'),1)
 frames=[]
 for label,f in [('入',st),('中',mid),('出',st+n-1)]:
  path=PRE/'缓推后'/f'{tr}_{st}_{label}.jpg';cap(p,t,f,path,.25);frames.append({'label':label,'frame':f,'path':str(path)})
 records.append({'track':tr,'start':st,'duration':n,'source_path':next(x['path'] for q in before['snapshot']['video'] if q['track']==tr for x in q['items'] if x['start']==st),'amplitude':amp,'native_comp_range':[a,z],'size_first_mid_last':[xf.GetInput('Size',a),xf.GetInput('Size',a+n//2),xf.GetInput('Size',z)],'center':xf.GetInput('Center'),'pivot':xf.GetInput('Pivot'),'filter':xf.GetInput('FilterMethod'),'before':str(baseline),'after_frames':frames,'reason':row.get('reason','independently inspected source motion and crop safety')})
 recordpath.write_text(json.dumps(records,ensure_ascii=False,indent=2));print('V14_NATIVE_PUSH',len(records),tr,st,amp,flush=True)
video_unchanged(t,before,{(x['track'],x['start']) for x in records});assert graphs(t)==before['graphs'];assert pm.SaveProject();print('V14_MOTION_BATCH_SAVED',len(records),flush=True)
