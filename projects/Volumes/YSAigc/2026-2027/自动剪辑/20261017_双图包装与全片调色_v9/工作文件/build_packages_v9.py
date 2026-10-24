from package_tools_v9 import *
import hashlib
r,pm,p,mp,t=connect();assert t.GetName()==NAME
before=json.loads((OUT/'live_before_v9.json').read_text())
assets=json.loads((OUT/'图片候选/final_photo_pairs_v9.json').read_text());assert assets['unique_sha256_count']==44
groups=[]
for source in assets['groups']:
    g={'start':source['record_frame'],'length':source['length_frames'],'title':source['suggested_title'],'left':source['source_photo_paths'][0],'right':source['source_photo_paths'][1],'left_label':source['images'][0]['caption'],'right_label':source['images'][1]['caption'],'original_records':source['absorbed_original_records']}
    if g['start']==3749:g['title']='文汇中学 · 科创领航'
    if g['start']==4051:g['title']='各美其美 · 美美与共'
    groups.append(g)
assert len(groups)==22 and sum(g['length'] for g in groups)==1428
all_paths=[g[s] for g in groups for s in ['left','right']]
assert len(set(all_paths))==44 and len({hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in all_paths})==44
assert pm.SaveProject()
current={it.GetStart():it for it in t.GetItemListInTrack('video',1)}
remove=[current[f] for g in groups if g['start']!=4051 for f in g['original_records']]
assert len(remove)==21 and all(not it.GetLinkedItems() for it in remove)
assert t.DeleteClips(remove,False)
pool={m.GetClipProperty('File Path'):m for m in walk(mp.GetRootFolder())};record=[]
for g in groups:
    if g['start']==4051:
        rec=json.loads((OUT/'package_prototype_v9.json').read_text());record.append(dict(g,photo_motion=rec['photo_motion'],prototype_reused=True));continue
    bg=ROOT/'画面包装'/f"双图底版_{g['start']:05d}.png";assert not bg.exists();Image.new('RGB',(1920,1080),PAPER).save(bg)
    back=append_native(mp,pool,bg,1,g['start'],g['length'],t);assert back.SetName('双图包装｜'+g['title']);comp=make_package(back,g)
    assert back.ExportFusionComp(str(OUT/f"双图包装_{g['start']}.comp"),1)
    motions=[]
    for j,side in enumerate(['left','right']):
        it=append_native(mp,pool,g[side],3+j,g['start'],g['length'],t)
        motion=make_photo(it,g[side],side,g['length'],'push' if j==0 else 'pull')
        assert it.SetName('双图'+('左' if j==0 else '右')+'｜'+g[side+'_label'])
        assert it.ExportFusionComp(str(OUT/f"原图_{g['start']}_{side}.comp"),1)
        motions.append(motion)
    record.append(dict(g,photo_motion=motions))
    print('V9_PAIR_INSTALLED',g['start'],g['title'],flush=True)
assert t.SetTrackName('video',1,'画面_双图包装与人文调色_v9')
snapshot=snap(t);assert snapshot['audio']==before['snapshot']['audio'] and snapshot['video'][1]==before['snapshot']['video'][1]
original_photos={f for g in groups for f in g['original_records']}
assert [i for i in before['snapshot']['video'][0]['items'] if i['start'] not in original_photos]==[i for i in snapshot['video'][0]['items'] if i['start'] not in original_photos]
v1=t.GetItemListInTrack('video',1);assert len(v1)==187 and all(a.GetEnd()==b.GetStart() for a,b in zip(v1,v1[1:])) and t.GetEndFrame()==11507
for track in [3,4]:
    its=t.GetItemListInTrack('video',track);assert len(its)==22
    for g,it in zip(groups,its):assert it.GetStart()==g['start'] and it.GetDuration()==g['length'] and it.GetMediaPoolItem().GetClipProperty('File Path')==g['left' if track==3 else 'right']
save('native_packages_v9.json',{'groups':record,'photo_count':44,'unique_photo_count':44,'picture_count':187,'photo_total_frames':1428,'snapshot':snapshot,'all_audio_preserved':True,'all_v2_preserved':True,'all_unrelated_v1_preserved':True})
assert pm.SaveProject();assert t.SetCurrentTimecode(tc(7536));print('V9_ALL_NATIVE_PAIRS_READY',flush=True)
