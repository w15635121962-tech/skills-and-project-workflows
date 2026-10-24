import json,math,copy,statistics
from pathlib import Path
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件'
base=json.loads((OUT/'base_plan_v6.json').read_text())
old={s['record_frame']:s for s in base['shots']}
groups=[]
for folder in ['开篇重选','中段加密','后段加密']:
    data=json.loads((OUT/folder/'groups_v7.json').read_text())
    if isinstance(data,dict):data=data['groups']
    groups.extend(data)
groups.sort(key=lambda g:g['record_frame'])
claimed=set();new=[]
for g in groups:
    starts=g['old_record_frames']
    assert starts and not claimed.intersection(starts)
    assert all(a in old for a in starts)
    items=sorted([old[a] for a in starts],key=lambda s:s['record_frame'])
    assert all(a['record_frame']+a['length_frames']==b['record_frame'] for a,b in zip(items,items[1:]))
    assert g['record_frame']==items[0]['record_frame']
    length=sum(s['length_frames'] for s in items)
    assert g['length_frames']==length
    assert sum(s['length_frames'] for s in g['segments'])==length
    cursor=g['record_frame']
    for s in g['segments']:
        assert s['record_frame']==cursor and s['length_frames']>=25
        assert s.get('speed',1)==1
        assert Path(s['path']).exists()
        s.update(revision_v7=True,out=s['in']+s['length_frames']/25)
        s['name']=Path(s['path']).name
        s['source_start_frame']=round(s['in']*s['fps'])
        s['source_count_frames']=math.ceil(s['length_frames']/25*s['fps']-1e-8)
        cursor+=s['length_frames'];new.append(s)
    claimed.update(starts)
shots=sorted([copy.deepcopy(s) for s in base['shots'] if s['record_frame'] not in claimed]+new,key=lambda s:s['record_frame'])
assert shots[0]['record_frame']==0 and shots[-1]['record_frame']+shots[-1]['length_frames']==11507
assert all(a['record_frame']+a['length_frames']==b['record_frame'] for a,b in zip(shots,shots[1:]))
for i,s in enumerate(shots,1):s['index']=i
overlays=copy.deepcopy(base['interview_overlays_v6'])
engineering=next(s for s in overlays if s['record_frame']==11318)
engineering.update(length_frames=44,out=engineering['in']+44/25,revision_v7=True,intent='创新能力：保留实践台前学生协作中景1.76秒，再接教师近景')
overlays+=json.loads((OUT/'interview_new_overlays_v7.json').read_text())
overlays.sort(key=lambda s:s['record_frame'])
assert all(a['record_frame']+a['length_frames']<=b['record_frame'] for a,b in zip(overlays,overlays[1:]))
for s in overlays:
    s['source_start_frame']=round(s['in']*s['fps']);s['source_count_frames']=math.ceil(s['length_frames']/25*s['fps']-1e-8)

# Repeated still evidence is intentional; moving image source ranges must remain distinct.
conflicts=[]
motion=[s for s in shots+overlays if not s.get('is_photo')]
for i,a in enumerate(motion):
    for b in motion[i+1:]:
        if a['path']!=b['path']:continue
        overlap=min(a['in']+a['length_frames']/25,b['in']+b['length_frames']/25)-max(a['in'],b['in'])
        if overlap>.041:conflicts.append({'path':a['path'],'record_a':a['record_frame'],'record_b':b['record_frame'],'overlap_seconds':overlap})
(OUT/'source_overlap_audit_v7.json').write_text(json.dumps(conflicts,ensure_ascii=False,indent=2))
assert not conflicts,conflicts
def stats(slist):
    lengths=[s['length_frames']/25 for s in slist if s['record_frame']<10850]
    opening=[s for s in slist if s['record_frame']<1767]
    return {'total_v1_items':len(slist),'narration_picture_items':len(lengths),'mean_narration_shot_seconds':statistics.mean(lengths),'median_narration_shot_seconds':statistics.median(lengths),'shots_over_3_15_seconds':sum(x>3.15 for x in lengths),'shots_over_4_seconds':sum(x>4 for x in lengths),'opening_picture_items':len(opening),'opening_mean_seconds':70.68/len(opening),'photo_seconds':sum(s['length_frames']/25 for s in slist if s.get('is_photo'))}
plan=copy.deepcopy(base)
plan.update(name='学校_镜头节奏与开篇重剪_v7_20261017',base_timeline='学校_全片深度精剪_v6_20261017',shots=shots,interview_overlays_v7=overlays,revision_v7={'groups':len(groups),'old_items_replaced':len(claimed),'new_items':len(new),'before':stats(base['shots']),'after':stats(shots),'no_source_interval_repeats':True})
(OUT/'native_changes_v7.json').write_text(json.dumps(groups,ensure_ascii=False,indent=2))
(OUT/'edit_plan_v7.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
print(json.dumps(plan['revision_v7'],ensure_ascii=False,indent=2))
