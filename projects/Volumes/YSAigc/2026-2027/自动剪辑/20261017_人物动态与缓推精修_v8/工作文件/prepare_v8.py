import json,copy,math,hashlib
from pathlib import Path
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件'
base=json.loads((OUT/'base_plan_v7.json').read_text());old={s['record_frame']:s for s in base['shots']}
replacements=[];motion=[];inputs=[]
for folder in ['开篇动态','中段动态','后段动态']:
    for fn,key,target in [('source_replacements_v8.json','replacements',replacements),('motion_suggestions_v8.json','motion',motion)]:
        path=OUT/folder/fn;data=json.loads(path.read_text());target.extend(data[key] if isinstance(data,dict) else data);inputs.append({'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
assert len({s['record_frame'] for s in replacements})==len(replacements)
for s in replacements:
    a=old[s['record_frame']];assert s['length_frames']==a['length_frames'] and s['record_frame']<10850
    assert Path(s['path']).exists() and not s['is_photo'] and s['speed']==1 and s['fps']==25
    s.update(revision_v8=True,out=s['in']+s['length_frames']/25,source_start_frame=round(s['in']*s['fps']),source_count_frames=math.ceil(s['length_frames']/25*s['fps']-1e-8))
    s['name']=Path(s['path']).name
by={s['record_frame']:s for s in replacements};shots=[copy.deepcopy(by.get(s['record_frame'],s)) for s in base['shots']]
assert len(shots)==188 and all(a['record_frame']+a['length_frames']==b['record_frame'] for a,b in zip(shots,shots[1:]))
assert shots[-1]['record_frame']+shots[-1]['length_frames']==11507
assert len({m['record_frame'] for m in motion})==len(motion)
for m in motion:
    s=next(x for x in shots if x['record_frame']==m['record_frame'])
    assert not s['is_photo'] and s['fps']==25 and m['record_frame'] not in [3749,3832,3891,3954]
    low=min(m['start_size'],m['end_size'])
    if low>1:
        m['proposed_sizes']=[m['start_size'],m['end_size']]
        m['start_size']/=low;m['end_size']/=low
    assert 1<=m['start_size']<=1.04 and 1<=m['end_size']<=1.04
    assert m['center_start']==m['center_end']==[.5,.5]
    assert m['kind'] in ['push','pull']
    m.update(track=1,length_frames=s['length_frames'],curve='smoothstep',node_name='V8_GentleMotion')
assert next(m for m in motion if m['record_frame']==0)['end_size']==1.03
conflicts=[];all_motion=[s for s in shots+base['interview_overlays_v7'] if not s.get('is_photo')]
for i,a in enumerate(all_motion):
    for b in all_motion[i+1:]:
        if a['path']!=b['path']:continue
        overlap=min(a['in']+a['length_frames']/25,b['in']+b['length_frames']/25)-max(a['in'],b['in'])
        if overlap>.041:conflicts.append({'a':a['record_frame'],'b':b['record_frame'],'path':a['path'],'seconds':overlap})
(OUT/'source_overlap_v8.json').write_text(json.dumps(conflicts,ensure_ascii=False,indent=2));assert not conflicts,conflicts
plan=copy.deepcopy(base);plan.update(name='学校_人物动态与缓推精修_v8_20261017',base_timeline=base['name'],shots=shots,motion_v8=sorted(motion,key=lambda m:m['record_frame']),source_replacements_v8=replacements,revision_v8={'source_replacements':len(replacements),'editable_camera_motions':len(motion),'push':sum(m['kind']=='push' for m in motion),'pull':sum(m['kind']=='pull' for m in motion),'motion_size_range':[min(min(m['start_size'],m['end_size']) for m in motion),max(max(m['start_size'],m['end_size']) for m in motion)],'picture_count':188,'duration_frames':11507,'duration_seconds':460.28,'all_centers_fixed':True,'existing_photo_animation_preserved':True,'all_audio_preserved':True,'input_files':inputs})
(OUT/'edit_plan_v8.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2));print(json.dumps(plan['revision_v8'],ensure_ascii=False,indent=2))
