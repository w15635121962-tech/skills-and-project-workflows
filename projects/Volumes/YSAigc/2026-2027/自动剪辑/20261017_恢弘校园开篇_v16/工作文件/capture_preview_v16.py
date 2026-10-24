from common_v16 import *
r,pm,p,mp,t=connect();r.OpenPage('edit');frames=OUT/'开篇原生逐帧';frames.mkdir(exist_ok=True)
for frame in range(175):
 path=frames/f'{frame:04d}.jpg'
 if not path.exists():cap(p,t,frame,path,wait=.06)
 if frame%50==0:print('native_opening_frames',frame+1,'/175',flush=True)
assert t.SetCurrentTimecode(tc(40));assert pm.SaveProject();print('native_preview_capture_done',flush=True)
