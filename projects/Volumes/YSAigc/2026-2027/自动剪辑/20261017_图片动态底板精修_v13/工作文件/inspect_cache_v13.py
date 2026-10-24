from common_v13 import *
r,pm,p,mp,t=connect();assert t.GetName()==TIMELINE
for tr in [1,3,4]:
 it=next(x for x in t.GetItemListInTrack('video',tr) if x.GetStart()==6470);c=it.GetFusionCompByIndex(1)
 print(tr,it.GetIsFusionOutputCacheEnabled(),[x for x in dir(c) if 'cache' in x.lower()],flush=True)
print('SETTINGS',{k:v for k,v in p.GetSetting().items() if any(s in k.lower() for s in ['cache','gpu','fusion'])},flush=True)
assert r.OpenPage('edit');cap(p,t,6500,PRE/'缓存复核_6470.jpg',1)
