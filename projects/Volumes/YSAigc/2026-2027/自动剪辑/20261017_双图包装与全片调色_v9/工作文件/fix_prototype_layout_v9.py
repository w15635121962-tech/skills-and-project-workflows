from package_tools_v9 import *
r,pm,p,mp,t=connect();assert t.GetName()==NAME
record=json.loads((OUT/'package_prototype_v9.json').read_text());g=record['group'];records=[]
for track,side,kind in [(3,'left','push'),(4,'right','pull')]:
    it=t.GetItemListInTrack('video',track)[0];c=it.GetFusionCompByIndex(1)
    records.append(make_photo(it,g[side],side,g['length'],kind))
for off in [0,55,109]:capture(p,t,g['start']+off,PRE/f'双图原型修正_{off}.jpg',.3)
assert pm.SaveProject();save('package_prototype_v9.json',dict(group=g,photo_motion=records));print('NATIVE_LAYOUT_FIXED',flush=True)
