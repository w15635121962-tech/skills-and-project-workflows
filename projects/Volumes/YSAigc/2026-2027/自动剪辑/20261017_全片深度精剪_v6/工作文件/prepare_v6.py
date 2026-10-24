import json,copy,hashlib,av,math
from pathlib import Path
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件'
old=json.loads((ROOT.parent/'20261017_开篇向往感精修_v5/工作文件/opening_plan_v5.json').read_text())
front=json.loads((OUT/'前半画面审阅/front_picture_patches_v6.json').read_text())['patches']
tail=[s for s in json.loads((OUT/'后半画面审阅/v6_tail_change_groups.json').read_text())['changes'] if s['record_frame']!=8332]
root=json.loads((OUT/'体育与收束审阅/root_picture_proposals_v6.json').read_text())
patches=front+tail+root;starts=[s['record_frame'] for s in patches];assert len(starts)==len(set(starts))
plan=copy.deepcopy(old);plan['name']='学校_全片深度精剪_v6_20261017';plan['base_timeline']=old['name'];plan['style']='人文、厚重、唯美；以真实操作、师生关系与动作完成度加强全片叙事，保留完整旁白与460.28秒时长'
changes=[]
for patch in sorted(patches,key=lambda s:s['record_frame']):
 original=next(s for s in old['shots'] if s['record_frame']==patch['record_frame']);assert original['length_frames']==patch['length_frames']
 s=next(s for s in plan['shots'] if s['record_frame']==patch['record_frame'])
 path=Path(patch['path']);assert path.is_file()
 with av.open(str(path)) as c:
  v=c.streams.video[0];fps=float(v.average_rate);duration=float(v.duration*v.time_base);resolution=[v.width,v.height]
 assert patch['in']+patch['length_frames']/25<=duration+.001
 s.update({'path':str(path),'name':path.name,'in':patch['in'],'out':patch['in']+patch['length_frames']/25,'fps':fps,'speed':1,'is_photo':False,'log':'拍摄素材转码' in str(path),'resolution':resolution,'asset_id':None,'source_photo':None,'intent':patch['intent'],'revision_v6':True})
 s['source_start_frame']=math.ceil(patch['in']*fps-1e-8);s['source_count_frames']=math.ceil(s['length_frames']/25*fps-1e-8);s['in_requested']=patch['in'];s['in']=s['source_start_frame']/fps;s['source_out_exclusive']=(s['source_start_frame']+s['source_count_frames'])/fps;s['out']=s['source_out_exclusive']
 if not patch.get('preserve_title'):s['title']=None
 changes.append({'record_frame':s['record_frame'],'old_record_frames':[s['record_frame']],'old':[original],'segments':[copy.deepcopy(s)],'preserve_title':patch.get('preserve_title',False),'closing_rebuild':patch.get('closing_rebuild',False),'evidence':patch.get('evidence')})
group_specs=json.loads((OUT/'体育与收束审阅/photo_rhythm_groups_v6.json').read_text())
for group in group_specs:
 originals=[s for s in plan['shots'] if s['record_frame'] in group['old_record_frames']];assert len(originals)==len(group['old_record_frames'])
 assert all(a['record_frame']+a['length_frames']==b['record_frame'] for a,b in zip(originals,originals[1:]))
 assert sum(s['length_frames'] for s in group['segments'])==sum(s['length_frames'] for s in originals)
 segments=[]
 for spec in group['segments']:
  base=next(s for s in originals if s['record_frame']==spec.get('copy_record_frame',originals[0]['record_frame']))
  s=copy.deepcopy(base);s.update(spec);s['revision_v6']=True
  with av.open(s['path']) as c:
   v=c.streams.video[0];s['fps']=float(v.average_rate);duration=float(v.duration*v.time_base);s['resolution']=[v.width,v.height]
  s['out']=s['in']+s['length_frames']/25;s['speed']=1;assert s['out']<=duration+.001
  if 'copy_record_frame' not in spec:s.update({'is_photo':False,'log':'拍摄素材转码' in s['path'],'name':Path(s['path']).name,'asset_id':None,'source_photo':None,'title':None})
  s['source_start_frame']=math.ceil(s['in']*s['fps']-1e-8);s['source_count_frames']=math.ceil(s['length_frames']/25*s['fps']-1e-8);s['in_requested']=s['in'];s['in']=s['source_start_frame']/s['fps'];s['source_out_exclusive']=(s['source_start_frame']+s['source_count_frames'])/s['fps'];s['out']=s['source_out_exclusive']
  segments.append(s)
 assert all(a['record_frame']+a['length_frames']==b['record_frame'] for a,b in zip(segments,segments[1:]))
 assert segments[0]['record_frame']==originals[0]['record_frame'] and segments[-1]['record_frame']+segments[-1]['length_frames']==originals[-1]['record_frame']+originals[-1]['length_frames']
 plan['shots']=[s for s in plan['shots'] if s['record_frame'] not in group['old_record_frames']]+segments
 changes.append({'record_frame':originals[0]['record_frame'],'old_record_frames':group['old_record_frames'],'old':originals,'segments':segments,'preserve_title':False,'closing_rebuild':False,'evidence':group['intent']})
plan['shots'].sort(key=lambda s:s['record_frame'])
for i,s in enumerate(plan['shots'],1):s['index']=i
overlay_file=OUT/'后半画面审阅/v6_interview_broll_recommendations.json';overlays=json.loads(overlay_file.read_text())['changes']
assert len(overlays)==2 and [s['record_frame'] for s in overlays]==[11242,11318] and [s['length_frames'] for s in overlays]==[76,89]
for s in overlays:
 assert Path(s['path']).is_file();s['out']=s['in']+s['length_frames']/25;s['speed']=1;s['log']=True;s['track']=2
 with av.open(s['path']) as c:s['fps']=float(c.streams.video[0].average_rate)
plan['interview_overlays_v6']=overlays
assert len(plan['shots'])==121 and plan['shots'][-1]['record_frame']+plan['shots'][-1]['length_frames']==11507
assert all(a['record_frame']+a['length_frames']==b['record_frame'] for a,b in zip(plan['shots'],plan['shots'][1:]))
reference=ROOT.parent.parent/'文汇中学/文汇中学集团宣传片_剪辑使用清单与剪辑思路.md';plan['reference']={'path':str(reference),'sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),'use':'Asset guide and editorial reference; source scenes verified independently, no automatic execution of every suggestion.'}
reuses=[]
sources=[{**s,'track':1} for s in plan['shots']]+overlays
for i,a in enumerate(sources):
 for j,b in enumerate(sources):
  if j<=i or a['path']!=b['path'] or not (a.get('revision_v6') or b.get('revision_v6') or a['track']==2 or b['track']==2):continue
  overlap=min(a['out'],b['out'])-max(a['in'],b['in'])
  if overlap>.04:reuses.append({'a':a['record_frame'],'b':b['record_frame'],'source':a['path'],'overlap_seconds':overlap})
assert not reuses,reuses
(OUT/'deep_edit_plan_v6.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
(OUT/'native_changes_v6.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2))
print('V6_PLAN_READY',len(changes),'revised picture items,',len(overlays),'interview cutaways; duration',plan['duration_seconds'],flush=True)
