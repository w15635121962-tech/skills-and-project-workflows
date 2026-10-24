from common_v15 import *
r,pm,p,mp,t=connect();r.OpenPage('edit')
loop=OUT/'角标原生循环逐帧';opening=OUT/'开篇原生逐帧';loop.mkdir(exist_ok=True);opening.mkdir(exist_ok=True)
states=[t.GetIsTrackEnabled('video',k) for k in range(1,5)]
try:
 for k in range(1,5):assert t.SetTrackEnable('video',k,False)
 time.sleep(.6)
 for frame in range(251):
  path=loop/f'{frame:04d}.jpg'
  if not path.exists():im=cap(p,t,frame,path,wait=.06)
  if frame%50==0:print('loop_native_frames',frame+1,'/251',flush=True)
finally:
 for k,state in enumerate(states,1):assert t.SetTrackEnable('video',k,state)
 time.sleep(.5)
 assert pm.SaveProject()
for frame in range(175):
 path=opening/f'{frame:04d}.jpg'
 if not path.exists():cap(p,t,frame,path,wait=.06)
 if frame%50==0:print('opening_native_frames',frame+1,'/175',flush=True)
assert t.SetCurrentTimecode(tc(30));assert pm.SaveProject()
print('all_native_motion_frames_done',flush=True)
