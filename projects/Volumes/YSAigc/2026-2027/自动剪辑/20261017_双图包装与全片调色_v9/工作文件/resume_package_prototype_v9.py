from package_tools_v9 import *
r,pm,p,mp,t=connect();assert t.GetName()==NAME
plan=json.loads((BASE/'edit_plan_v8.json').read_text());photos={s['record_frame']:s for s in plan['shots'] if s['is_photo']}
g={'start':4051,'length':110,'title':'各美其美 · 美美与共','left':photos[4051]['source_photo'],'right':photos[4101]['source_photo'],'left_label':'文汇小学','right_label':'金台书院小学'}
pool={m.GetClipProperty('File Path'):m for m in walk(mp.GetRootFolder())};records=[]
for j,side in enumerate(['left','right']):
    assert not t.GetItemListInTrack('video',3+j)
    it=append_native(mp,pool,g[side],3+j,g['start'],g['length'],t);motion=make_photo(it,g[side],side,g['length'],'push' if j==0 else 'pull');assert it.SetName('双图'+('左' if j==0 else '右')+'｜'+g[side+'_label']);records.append(motion)
assert snap(t)['audio']==json.loads((OUT/'live_before_v9.json').read_text())['snapshot']['audio']
assert t.GetEndFrame()==11507 and len(t.GetItemListInTrack('video',1))==187
assert r.OpenPage('edit')
for off in [0,55,109]:capture(p,t,g['start']+off,PRE/f'双图原型_{off}.jpg',.3)
assert pm.SaveProject();save('package_prototype_v9.json',dict(group=g,photo_motion=records))
print('V9_NATIVE_PAIR_PROTOTYPE_READY',flush=True)
