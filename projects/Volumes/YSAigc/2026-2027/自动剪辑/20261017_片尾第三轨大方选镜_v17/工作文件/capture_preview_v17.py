from common_v17 import *
r,pm,p,mp,t=connect();r.OpenPage('edit');frames=OUT/'尾段原生逐帧';frames.mkdir(exist_ok=True)
start=11105;end=11507
for index,frame in enumerate(range(start,end)):
 path=frames/f'{index:04d}.jpg'
 if not path.exists():cap(p,t,frame,path,wait=.06)
 if index%50==0:print('native_tail_frames',index+1,'/',end-start,flush=True)
assert t.SetCurrentTimecode(tc(11150));assert pm.SaveProject();print('native_tail_capture_done',flush=True)
