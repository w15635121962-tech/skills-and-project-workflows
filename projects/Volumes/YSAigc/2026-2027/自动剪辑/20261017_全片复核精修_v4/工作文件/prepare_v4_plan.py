import json,copy,av
from pathlib import Path
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';original=json.loads((OUT/'original_plan_v3_full.json').read_text());old={s['record_frame']:s for s in original['shots']}
middle=json.loads((OUT/'画面复核中段/middle_picture_patches.json').read_text())['patches'];tail=json.loads((OUT/'画面复核后段/tail_change_proposals.json').read_text())['patches'];patches=middle+tail
for record,point,reason in [(1273,2.8,'实验镜头提前入点，保留操作动作并避开挠头尾帧'),(1462,4.56,'教师辅导从回应学生开始，避开看镜头的瞬间')]:
 s=old[record];patches.append({'record_frame':record,'path':s['path'],'in':point,'length_frames':s['length_frames'],'reason':reason})
groups={}
for patch in patches:
 anchor=4234 if patch['record_frame']==4289 else patch['record_frame'];assert anchor in old
 group=groups.setdefault(anchor,{'record_frame':anchor,'original_length_frames':old[anchor]['length_frames'],'old':old[anchor],'segments':[]})
 row=copy.deepcopy(old[anchor]);row.update({'record_frame':patch['record_frame'],'path':patch['path'],'name':Path(patch['path']).name,'in':patch['in'],'length_frames':patch['length_frames'],'speed':1,'out':patch['in']+patch['length_frames']/25,'title':None,'asset_id':None,'source_photo':None,'is_photo':'画面资料' in patch['path'],'log':'拍摄素材转码' in patch['path'],'intent':patch['reason'],'revision_v4':True})
 with av.open(row['path']) as c:
  stream=c.streams.video[0];row['fps']=float(stream.average_rate);row['resolution']=[stream.width,stream.height];dur=float(stream.duration*stream.time_base) if stream.duration else c.duration/1e6
 assert row['out']<=dur+.04,(row['path'],row['out'],dur)
 group['segments'].append(row)
for group in groups.values():
 group['segments'].sort(key=lambda s:s['record_frame']);assert sum(s['length_frames'] for s in group['segments'])==group['original_length_frames'];assert group['segments'][0]['record_frame']==group['record_frame']
 for a,b in zip(group['segments'],group['segments'][1:]):assert a['record_frame']+a['length_frames']==b['record_frame']
shots=[]
for s in original['shots']:shots.extend(groups[s['record_frame']]['segments'] if s['record_frame'] in groups else [s])
for i,s in enumerate(shots,1):s['index']=i
assert len(shots)==121 and shots[0]['record_frame']==0 and shots[-1]['record_frame']+shots[-1]['length_frames']==11507
for a,b in zip(shots,shots[1:]):assert a['record_frame']+a['length_frames']==b['record_frame']
def photo_runs(rows):
 runs=[];current=[]
 for s in rows:
  if s['is_photo']:current.append(s)
  elif current:runs.append(current);current=[]
 if current:runs.append(current)
 return [{'start':run[0]['record_frame']/25,'duration':sum(s['length_frames'] for s in run)/25,'clips':len(run)} for run in runs]
original['shots']=shots;original['total_picture_count']=121;original['refinement_notes']=[{'record_frame':g['record_frame'],'old_path':g['old']['path'],'new_paths':[s['path'] for s in g['segments']],'reason':[s['intent'] for s in g['segments']]} for g in groups.values()];original['rhythm_metrics']={'before_photo_runs':photo_runs(list(old.values())),'after_photo_runs':photo_runs(shots),'before_count':120,'after_count':121,'total_seconds':460.28,'longest_photo_run_before':max(x['duration'] for x in photo_runs(list(old.values()))),'longest_photo_run_after':max(x['duration'] for x in photo_runs(shots))}
(OUT/'refined_plan_v4.json').write_text(json.dumps(original,ensure_ascii=False,indent=2),encoding='utf-8');(OUT/'native_change_groups_v4.json').write_text(json.dumps(list(groups.values()),ensure_ascii=False,indent=2),encoding='utf-8');print('READY_V4',len(groups),'changed picture items',len(patches),'new segments',original['rhythm_metrics']['longest_photo_run_before'],original['rhythm_metrics']['longest_photo_run_after'])
