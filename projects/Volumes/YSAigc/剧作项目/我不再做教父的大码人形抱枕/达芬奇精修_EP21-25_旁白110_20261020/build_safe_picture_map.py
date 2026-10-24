#!/usr/bin/env python3
"""Offline 24fps picture/A1/A3 planner. No Resolve imports or calls."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SNAPSHOT = HERE / 'Resolve_精修前实时实读.json'
NATIVE = HERE / '原生110分组实测.json'
AUDIO_AUDIT = HERE / '音频精修确定剪口.json'

# Reviewed windows, in OLD timeline frames. Head/tail is relative to this window.
# Prioritise static holds and the ends of settled reaction shots, not key actions.
WINDOWS = {
 (21,0): [(8,33,'tail','开场静帧；至少留8帧')],
 (21,226): [(431,479,'tail','男主已睡着的近景末端；保留握腕和抽手惊醒')],
 (21,613): [(796,886,'tail','纸券已展开后的读券/初反应尾部；保留枕下取券与展开')],
 (21,886): [(1032,1080,'tail','成年男主读券反应末端')],
 (21,1080): [(1256,1300,'tail','paper静帧；保留所有画券动作和青年男主反应')],
 (21,1463): [(1753,1801,'tail','末段男主静默反应；保留递券、接券、女主反应')],
 (21,1839): [(2134,2182,'tail','女主眼部/广角反应尾；保留放券和后续接触')],
 (21,2182): [(2391,2439,'tail','泪眼反应尾；保留攥床单及随后的全部拥抱请求对白')],
 (22,0): [(0,36,'head','开场已建立的病房静默广角')],
 (22,224): [(224,248,'head','撕纸前持券停顿；不删纸撕开/落桶')],
 (22,382): [(392,404,'tail','女主眼部反应末端；保留男主伸手动作')],
 (22,525): [(617,635,'tail','补回起身后的短hold；另保留635..636非A2一帧')],
 (22,732): [(732,746,'head','男主反应尾；保留女主走向门口')],
 (22,868): [(992,1052,'tail','哭泣近景末端；保留脚步停住及最初眼泪')],
 (22,1681): [(1747,1771,'tail','男主已低眼后的静默尾部')],
 (23,0): [(36,50,'tail','女主静默反应尾部；后续支票质问对白不动')],
 (23,566): [(664,688,'tail','花束插入镜末端')],
 (23,746): [(746,774,'head','男主无声反应前置停顿；Yes对白完全保留')],
 (24,1141): [(1163,1179,'tail','声音渐低的脸部反应尾')],
 (24,3073): [(3109,3129,'tail','听者泪眼反应尾；不改Sorry对白')],
 (25,0): [(244,264,'tail','男主看向女主的反应尾，止于原生切点'),(275,287,'tail','女主窗前背影尾部')],
 (25,998): [(1020,1036,'tail','男主低眼反应尾；后续问句不动')],
 (25,1213): [(1213,1255,'head','受击初始停顿；完整保留落手及最后看他')],
 (25,1995): [(2035,2059,'tail','脚停在门口后的静态尾；保留站起和停步')],
 (25,2059): [(2112,2144,'tail','飞机/窗边镜尾；后续使用去重连续画面池重整')],
 (25,2144): [(2144,2179,'head','源234..269的重复窗边画面，计入本组缩短预算')],
 (25,2354): [(2466,2498,'tail','窗外天际空镜末端，止于源144原生切点；保留女主、手与末尾飞机')],
}

def read(path):
 return json.loads(Path(path).read_text())
def sha(path):
 return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def samepath(a,b):
 return str(a)==str(b)
def overlap(a,b,c,d):
 return max(a,c)<min(b,d)
def norm(item):
 return {'start':int(item['start']), 'end':int(item['end']),
         'source_start':int(item['source_start']), 'source_path':item['source_path'],
         'properties':copy.deepcopy(item.get('properties',{})),
         'kind':'video' if Path(item['source_path']).suffix.lower()=='.mp4' else 'image_sequence',
         'original_item_id':item.get('id'), 'name':item.get('name','')}
def cutpiece(p,a,b):
 q=copy.deepcopy(p);q['start']=a;q['end']=b
 if q['kind']!='freeze_frame': q['source_start']+=a-p['start']
 return q
def replace(parts,a,b,newparts):
 assert sum(p['end']-p['start'] for p in newparts)==b-a
 out=[]
 for p in parts:
  if not overlap(p['start'],p['end'],a,b):out.append(p);continue
  if p['start']<a:out.append(cutpiece(p,p['start'],a))
  if p['end']>b:out.append(cutpiece(p,b,p['end']))
 out.extend(newparts)
 return sorted(out,key=lambda p:p['start'])
def media_part(template,a,b,source_start,kind='video'):
 p=copy.deepcopy(template);p.update(start=a,end=b,source_start=source_start,kind=kind)
 return p
def mapper(windows):
 def f(frame):
  return frame-sum(max(0,min(frame,b)-a) for a,b in windows if frame>a)
 return f
def subtract(parts,windows,f):
 out=[]
 for p in parts:
  remains=[(p['start'],p['end'])]
  for a,b in windows:
   new=[]
   for x,y in remains:
    if not overlap(x,y,a,b):new.append((x,y));continue
    if x<a:new.append((x,a))
    if b<y:new.append((b,y))
   remains=new
  for a,b in remains:
   q=cutpiece(p,a,b);q['old_slot_start']=a;q['old_slot_end']=b
   q['start']=f(a);q['end']=f(b);out.append(q)
 return sorted(out,key=lambda p:p['start'])
def export(p,track):
 return {**{k:v for k,v in p.items() if k not in ['start','end','source_start']},
         'record_frame':p['start'],'duration_frames':p['end']-p['start'],
         'source_start_frame':p['source_start'],
         'source_end_frame_exclusive':p['source_start']+(p['end']-p['start']) if p['kind']!='freeze_frame' else p['source_start']+1,
         'track':track,'speed_ratio':1.0}

def continuity_baseline(ep,parts):
 fixes=[]
 if ep==22:
  t=next(p for p in parts if p['start']==224)
  first=media_part(t,224,267,0);first['properties'].update(ZoomX=2,ZoomY=2,Pan=0,Tilt=389.25)
  middle=media_part(t,267,355,43)
  bucket=media_part(t,355,382,131);bucket['properties'].update(ZoomX=1.6,ZoomY=1.6,Pan=-216,Tilt=324)
  parts=replace(parts,224,382,[first,middle,bucket])
  t=next(p for p in parts if p['start']==572)
  rise=media_part(t,572,617,0)
  hold=media_part(t,617,636,44,'freeze_frame')
  hold['freeze_source_frame']=44
  hold['freeze_note']='Extract real source frame44 as PNG/image sequence; do not play MP4 frame44 onward. Hold remainder depends on N.'
  parts=replace(parts,572,636,[rise,hold])
  fixes.append('EP22: source22-02 split0..43 tight hands/43..131 original/131..158 tight bucket; source22-03 rise0..45+short frame44 hold, then original treatment45..141.')
 if ep==23:
  t=next(p for p in parts if p['start']==1503)
  street=media_part(t,1503,1571,48)
  t=next(p for p in parts if p['start']==1619)
  ward=media_part(t,1571,1672,451)
  parts=replace(parts,1503,1672,[street,ward])
  fixes.append('EP23 picture-only: street48..116 then ward451..552; total169f unchanged, ward451 matches existing A1 at old1571.')
 return parts,fixes

def make_a3(video,a1,old_a3,old_windows,f):
 out=[]
 # Existing source-wise gain boundaries preserve -12/-3 choices where applicable.
 for p in video:
  if p['kind']!='video':continue
  bounds={p['start'],p['end']}
  for a in a1:
   if overlap(p['start'],p['end'],a['start'],a['end']):bounds.update([max(p['start'],a['start']),min(p['end'],a['end'])])
  for a in old_a3:
   if samepath(a['source_path'],p['source_path']):
    for source_edge in [a['source_start'],a['source_start']+a['end']-a['start']]:
     edge=p['start']+source_edge-p['source_start']
     if p['start']<edge<p['end']:bounds.add(edge)
  bounds=sorted(bounds)
  for x,y in zip(bounds,bounds[1:]):
   q=cutpiece(p,x,y);ss=q['source_start']
   covered=any(a['start']<=x and y<=a['end'] and samepath(a['source_path'],q['source_path']) and a['source_start']+x-a['start']==ss for a in a1)
   if covered:continue
   source_matches=[a for a in old_a3 if samepath(a['source_path'],q['source_path']) and a['source_start']<=ss<a['source_start']+a['end']-a['start']]
   gain=source_matches[0]['properties'].get('AudioVolume',-12) if source_matches else -12
   q['properties']={'AudioVolume':gain,'AudioVolumeEnabled':True}
   q['gain_db']=gain;q['a3_reason']='matching V1 MP4 source at100%; A1 identical source already excluded'
   out.append(q)
 # A freeze has no moving-media sync requirement. Preserve old quiet reaction
 # source audio underneath the brief freeze instead of synthesising a loop.
 baseline_a3=subtract(old_a3,old_windows,f)
 for p in video:
  if p['kind']!='freeze_frame':continue
  for a in baseline_a3:
   if overlap(p['start'],p['end'],a['start'],a['end']):
    q=cutpiece(a,max(p['start'],a['start']),min(p['end'],a['end']))
    q['gain_db']=q['properties'].get('AudioVolume',-12);q['a3_reason']='existing reaction roomtone under brief real-frame hold,100%'
    out.append(q)
 out.sort(key=lambda p:p['start'])
 assert all(a['end']<=b['start'] for a,b in zip(out,out[1:])), 'A3 overlaps'
 return out

def build_safe_picture_map(native_path=NATIVE,snapshot_path=SNAPSHOT):
 snap=read(snapshot_path);native=read(native_path);audit=read(AUDIO_AUDIT)
 timelines={t['name']:t for t in snap['timelines']}
 result={'scope':'Offline source/frame mapping only; no Resolve access. A2 remains existing native110/pitch-corrected result; V1/A1/A3 are100%.',
         'input_hashes':{str(p):sha(p) for p in [Path(snapshot_path),Path(native_path),AUDIO_AUDIT]},
         'frame_convention':'24fps, all outpoints exclusive','episodes':[],
         'review_limits':'Reviewed contact sheets and selected exact source frames. Full dynamic/audio join audition still required.'}
 for e in native['episodes']:
  ep=e['episode'];t=timelines[e['original']]
  video=[norm(i) for i in t['tracks']['video'][0]['items']]
  original_video=copy.deepcopy(video)
  audio={tr['track']:[norm(i) for i in tr['items']] for tr in t['tracks']['audio']}
  a1=audio[1];old_a3=audio[3]
  video,fixes=continuity_baseline(ep,video)
  windows=[];group_log=[]
  for g in e['groups']:
   s,en,n=g['old']['start'],g['old']['end'],int(g['removed_frames']);need=n;chosen=[]
   for a,b,direction,reason in WINDOWS[(ep,s)]:
    assert s<=a<b<=en
    take=min(need,b-a)
    if take:
     x,y=(a,a+take) if direction=='head' else (b-take,b)
     chosen.append({'old_start_frame':x,'old_end_frame_exclusive':y,'duration_frames':take,'reason':reason})
     windows.append((x,y));need-=take
    if not need:break
   if need:raise ValueError(f'EP{ep} A2{s}: N{n} exceeds reviewed safe capacity by{need} frames; no automatic key-action removal.')
   group_log.append({'old_start_frame':s,'old_end_frame_exclusive':en,'removed_frames':n,
                     'native_new_start':g['new_start'],'native_new_end':g['new_end'],
                     'delete_windows':chosen,'A2_kept_source_ranges':g.get('kept_source_ranges')})
  windows.sort();assert all(a[1]<=b[0] for a,b in zip(windows,windows[1:]))
  for a,b in windows:
   assert not any(overlap(a,b,c['start'],c['end']) for c in a1),f'EP{ep} deletion intersects A1'
  f=mapper(windows)
  for g in group_log:
   assert f(g['old_start_frame'])==g['native_new_start']
   assert f(g['old_end_frame_exclusive'])==g['native_new_end']
  final_video=subtract(video,windows,f)
  final_a1=subtract(a1,windows,f)
  assert len(final_a1)==len(a1)
  for old,new in zip(a1,final_a1):
   assert old['source_start']==new['source_start'] and old['end']-old['start']==new['end']-new['start']
  if ep==25:
   # Replace two adjacent pure-VO slots by a continuous unique-source pool.
   # This eliminates all35 duplicated frames even when N for one group is20.
   start,mid,end=f(2059),f(2144),f(2354)
   wanted=end-start;tail=wanted-177
   assert 24<=tail<=97, f'EP25 unique pool requires25-7-2 tail{tail} outside reviewed24..97'
   tpl=next(p for p in original_video if p['start']==2059)
   p1=media_part(tpl,start,start+177,184)
   tpl=next(p for p in original_video if p['start']==2271)
   p2=media_part(tpl,start+177,end,0);assert p2['end']-p2['start']==tail
   final_video=replace(final_video,start,end,[p1,p2])
   # Split at native A2 group edge for direct review/matching of each budget.
   rebuilt=[]
   for p in final_video:
    if p['start']<mid<p['end']:rebuilt.extend([cutpiece(p,p['start'],mid),cutpiece(p,mid,p['end'])])
    else:rebuilt.append(p)
   final_video=rebuilt
   fixes.append(f'EP25: unique pool25-6-1[184,361)+25-7-2[0,{tail}); native A2 slots[{start},{mid}) and[{mid},{end}); removes all35 duplicate frames, adds{tail-83} unused tail frames ifpositive.')
  final_a3=make_a3(final_video,final_a1,old_a3,windows,f)
  old_duration=t['end']-t['start'];loss=sum(b-a for a,b in windows);new_duration=old_duration-loss
  assert loss==e['total_removed_frames']
  assert final_video[0]['start']==0 and final_video[-1]['end']==new_duration
  assert all(a['end']==b['start'] for a,b in zip(final_video,final_video[1:])), 'V1 gap/overlap'
  assert sum(p['end']-p['start'] for p in final_video)==new_duration
  result['episodes'].append({'episode':ep,'original_timeline_name':e['original'],'timeline_name':e['working'],
    'fps':24,'old_duration_frames':old_duration,'total_removed_frames':loss,'duration_frames':new_duration,
    'groups':group_log,'delete_windows_old_frames':[list(w) for w in windows],
    'video':[export(p,1) for p in final_video],
    'audio_A1':[export(p,1) for p in final_a1], 'audio_A3':[export(p,3) for p in final_a3],
    'continuity_fixes':fixes,'validation':{'all_group_losses_match_native':True,
    'no_deletion_intersects_A1':True,'A1_source_start_end_frames_identical':True,
    'V1_contiguous_zero_to_exact_tail':True,'all_V1_A1_A3_speed_100_percent':True,
    'matching_A3_for_every_moving_V1_MP4_unless_identical_A1':True},
    'A2_policy':'Keep native110 parts exactly as already measured. Do not recreate or externally render A2.',
    'A3_policy':'100% matching video source, original source-wise gain where available; fallback-12dB only for newly exposed sync ambience. Review intelligible source speech underVO before mix signoff.'})
 result['validation']={'episodes':len(result['episodes']),'groups':sum(len(e['groups']) for e in result['episodes']),
                       'total_removed_frames':sum(e['total_removed_frames'] for e in result['episodes']),
                       'snapshot_unchanged':sha(snapshot_path)==result['input_hashes'][str(Path(snapshot_path))],
                       'native_measurement_unchanged':sha(native_path)==result['input_hashes'][str(Path(native_path))]}
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--native',type=Path,default=NATIVE);p.add_argument('--snapshot',type=Path,default=SNAPSHOT)
 p.add_argument('--out',type=Path,default=HERE/'原生110_安全画面与A1A3执行映射.json');args=p.parse_args()
 result=build_safe_picture_map(args.native,args.snapshot)
 args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'output':str(args.out),'validation':result['validation'],
                   'durations':[(e['episode'],e['duration_frames']) for e in result['episodes']]},ensure_ascii=False))
