from common_v22 import *
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--start',type=int,default=0);ap.add_argument('--end',type=int,default=667);args=ap.parse_args();assert 0<=args.start<args.end<=667
r,pm,p,mp,t=connect();r.OpenPage('edit');before=snap(t);beforegraph=graphs(t);seq=OUT/'开篇_原生逐帧';seq.mkdir(exist_ok=True);beg=time.time()
for f in range(args.start,args.end):
 assert p.GetCurrentTimeline().GetName()==TIMELINE
 image=cap(p,t,f,seq/f'{f:04d}.jpg',wait=.025);assert image.size==(1920,1080)
 assert t.GetCurrentTimecode()==tc(f)
 if (f-args.start+1)%50==0:print('CAPTURED',f+1,'elapsed',round(time.time()-beg,1),flush=True)
assert snap(t)==before and graphs(t)==beforegraph
(OUT/f'native_capture_batch_{args.start}_{args.end}_v22.json').write_text(json.dumps({'range':[args.start,args.end],'count':args.end-args.start,'fps':25,'width':1920,'height':1080,'source':'DaVinci Resolve actual active timeline frame exports','stable_frame_recheck_each_frame':True,'timeline_unchanged_during_capture':True,'elapsed_seconds':time.time()-beg},indent=2))
assert t.SetCurrentTimecode(tc(0));assert pm.SaveProject();print('CAPTURE_COMPLETE',args.start,args.end,flush=True)
