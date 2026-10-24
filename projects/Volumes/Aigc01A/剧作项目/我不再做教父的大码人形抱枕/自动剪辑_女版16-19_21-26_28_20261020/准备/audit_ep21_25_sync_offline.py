from pathlib import Path
import json,re,datetime,hashlib
root=Path.cwd();base=root/'自动剪辑_女版16-19_21-26_28_20261020';p=base/'Resolve_操作前实时实读.json';history=root/'达芬奇精修_EP21-25_旁白110_20261020/最终交付/最终核验_最终重开核验.json';expectpath=root/'达芬奇精修_EP21-25_旁白110_20261020/最终核验基准_只读整理.json'
c=json.loads(p.read_text());h=json.loads(history.read_text());ex=json.loads(expectpath.read_text());hm={e['episode']:e for e in h['episodes']};em={e['episode']:e for e in ex['episodes']}
def union(parts):
 r=[]
 for a,b in sorted(parts):
  if b<=a:continue
  if r and a<=r[-1][1]:r[-1][1]=max(r[-1][1],b)
  else:r.append([a,b])
 return r
def gaps(lo,hi,parts):
 r=[];prev=lo
 for a,b in union(parts):
  if a>prev:r.append([prev,a])
  prev=max(prev,b)
 if prev<hi:r.append([prev,hi])
 return r
def path(x):return str(Path(x['source_path']))
def normalized(x):
 dur=x['end']-x['start'];span=x['source_end']-x['source_start'];props=x.get('media_properties',{});total=props.get('Frames')
 try:total=int(total)
 except:total=None
 cap=span==dur-1 and total is not None and x['source_end']==total-1
 return {'span_exclusive':span+int(cap),'tail_cap_normalized':cap,'is_100_percent':span==dur or cap,'duration_consistent':dur==x['duration'],'raw_span':span,'source_total_frames':total}
report={'created_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'scope':'Offline analysis of saved live-read JSON only; no Resolve/browser/audio/media access or mutations.','input':str(p),'input_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'historical_reopened_baseline':str(history),'baseline_sha256':hashlib.sha256(history.read_bytes()).hexdigest(),'expected_gain_checklist':str(expectpath),'frame_convention':'24fps timeline frames; [start,end) exclusive. Resolve exact full-source-tail getter is normalized only if media Frames verifies last index.','audio_tracks_counted':[1,3],'audio_tracks_excluded':{'2':'Eliza voiceover','4':'music'},'episodes':[],'findings':[],'limitations':['This is mapping/enable/gain-property verification; no listening or final playback.','No API retime curve/keyframe data in snapshot. Exact 1:1 start/end/duration permits constant-100% mapping inference, not nonlinear-retime proof.','No bus gain/mute, automation, plugins or waveform levels included; gain anomaly means difference from saved final baseline, not new loudness measurement.','Image/PNG sequence holds have no embedded audio; counted separately and excluded from original-video same-source coverage.']}
for t in c['targets']:
 ep=int(re.search(r'EP(\d+)',t['name'])[1]);b=hm[ep];e=em[ep];fps=float(t['settings']['timelineFrameRate']);aud=[];video=[];trackissues=[];rateissues=[];gainissues=[];drift=[]
 for typ in ['video','audio']:
  for tr in t['tracks'][typ]:
   if typ=='audio' and tr['index'] not in (1,3):continue
   if not tr['enabled']:trackissues.append({'kind':typ,'track':tr['index'],'issue':'disabled_track'})
   bt=next(x for x in b['tracks'][typ] if x['track']==tr['index']);bm={x['id']:x for x in bt['items']}
   for x in tr['items']:
    v=dict(x,track=tr['index'],track_enabled=tr['enabled']);v['normalization']=normalized(x)
    if typ=='audio':aud.append(v)
    else:video.append(v)
    if not x['enabled']:trackissues.append({'kind':typ,'track':tr['index'],'id':x['id'],'issue':'disabled_item'})
    if not v['normalization']['is_100_percent'] or not v['normalization']['duration_consistent']:rateissues.append({'kind':typ,'track':tr['index'],'name':x['name'],'start':x['start'],'normalization':v['normalization']})
    y=bm.get(x['id'])
    if not y:drift.append({'kind':typ,'track':tr['index'],'id':x['id'],'issue':'new_item_vs_historical'});continue
    df={k:{'baseline':y.get(k),'current':x.get(k)} for k in ['start','end','duration','source_start','source_end','source_path','enabled'] if x.get(k)!=y.get(k)}
    if df:drift.append({'kind':typ,'track':tr['index'],'name':x['name'],'id':x['id'],'changes':df})
    if typ=='audio':
     actual=x.get('properties',{}).get('AudioVolume');expected=y.get('properties',{}).get('AudioVolume')
     if actual!=expected:gainissues.append({'track':tr['index'],'name':x['name'],'start':x['start'],'actual_gain_db':actual,'baseline_gain_db':expected})
     if actual is not None and (actual < -45 or actual>12):gainissues.append({'track':tr['index'],'name':x['name'],'start':x['start'],'actual_gain_db':actual,'issue':'obvious_extreme_gain'})
 vs=[v for v in video if Path(v['source_path']).suffix.lower() in ('.mp4','.mov','.mkv') and int(v.get('media_properties',{}).get('Audio Ch') or 0)>0]
 rows=[]
 for v in vs:
  matched=[];wrong=[]
  for a in aud:
   lo=max(v['start'],a['start']);hi=min(v['end'],a['end'])
   if hi<=lo or not a['enabled'] or not a['track_enabled']:continue
   exact=path(a)==path(v) and a['source_start']-a['start']==v['source_start']-v['start'] and a['normalization']['is_100_percent'] and v['normalization']['is_100_percent']
   event={'track':a['track'],'audio_id':a['id'],'audio_name':a['name'],'timeline_overlap':[lo,hi],'audio_source_frame_at_start':a['source_start']+(lo-a['start']),'picture_source_frame_at_start':v['source_start']+(lo-v['start'])}
   if exact:matched.append(event)
   else:wrong.append(dict(event,same_source_file=path(a)==path(v),offset_error_frames=event['audio_source_frame_at_start']-event['picture_source_frame_at_start']))
  parts=[x['timeline_overlap'] for x in matched];merged=union(parts);covered=sum(b-a for a,b in merged);duplicated=sum(b-a for a,b in parts)-covered;uncovered=gaps(v['start'],v['end'],parts)
  row={'video_id':v['id'],'video_name':v['name'],'timeline_range':[v['start'],v['end']],'source_range_normalized':[v['source_start'],v['source_start']+v['duration']],'source_path':v['source_path'],'video_frames':v['duration'],'matched_frames':covered,'coverage_percent':covered/v['duration']*100,'duplicate_matching_audio_frames':duplicated,'uncovered_timeline_ranges':uncovered,'matching_audio':matched,'other_original_audio_overlap':wrong}
  rows.append(row)
  if uncovered or duplicated:report['findings'].append({'episode':ep,'kind':'mapping_gap' if uncovered else 'duplicate_sync_audio','video_name':v['name'],'video_id':v['id'],'uncovered_timeline_ranges':uncovered,'duplicate_matching_audio_frames':duplicated,'other_original_audio_overlap':wrong})
 total=sum(v['duration'] for v in vs);covered=sum(x['matched_frames'] for x in rows)
 result={'episode':ep,'timeline':t['name'],'timeline_fps':fps,'duration_frames':t['end']-t['start'],'matches_historical_duration':t['end']-t['start']==b['duration_frames'],'original_video_clips':len(vs),'silent_image_or_sequence_clips':[{'name':v['name'],'start':v['start'],'end':v['end']} for v in video if v not in vs],'original_video_frames':total,'same_source_same_offset_matched_frames':covered,'overall_coverage_percent':covered/total*100,'all_video_frames_exactly_once_sync_covered':all(x['coverage_percent']==100 and x['duplicate_matching_audio_frames']==0 for x in rows),'source_rate_or_duration_issues':rateissues,'enable_issues':trackissues,'gain_changes_or_extremes':gainissues,'A1_gain_range_db':[min(a['properties']['AudioVolume'] for a in aud if a['track']==1),max(a['properties']['AudioVolume'] for a in aud if a['track']==1)],'A3_gain_range_db':[min(a['properties']['AudioVolume'] for a in aud if a['track']==3),max(a['properties']['AudioVolume'] for a in aud if a['track']==3)],'drift_vs_historical':drift,'coverage_by_original_video_clip':rows}
 report['episodes'].append(result)
report['summary']={'timelines':len(report['episodes']),'original_video_clips':sum(e['original_video_clips'] for e in report['episodes']),'original_video_frames':sum(e['original_video_frames'] for e in report['episodes']),'matched_frames':sum(e['same_source_same_offset_matched_frames'] for e in report['episodes']),'missing_exact_sync_frames':sum(e['original_video_frames']-e['same_source_same_offset_matched_frames'] for e in report['episodes']),'duplicate_sync_frames':sum(r['duplicate_matching_audio_frames'] for e in report['episodes'] for r in e['coverage_by_original_video_clip']),'gain_issues':sum(len(e['gain_changes_or_extremes']) for e in report['episodes']),'enable_issues':sum(len(e['enable_issues']) for e in report['episodes']),'rate_duration_issues':sum(len(e['source_rate_or_duration_issues']) for e in report['episodes'])}
report['recommendation']={'status':'one 5-frame exact-sync mapping exception; all other original-video frames match','episode21_exception':'Picture cut has been moved 5 frames earlier vs historical final baseline (209→204), while A1/A3 cut stayed209. In [204,209), picture is source247–252 but audible A1 is same file source188–193: offset-59 frames. This is a possible deliberate 5-frame L-cut, not silence or missing spoken-word evidence. Do not restore picture timing or trim outgoing dialogue blindly.','should_repair_this_request':'If the current requirement is strict every-frame same-source sync, add/extend A3 head by5frames to cover timeline204–209 from same source247–252 at the existing A3 gain, preserving outgoing A1 words and current picture cut. This is the minimal candidate; audition overlap before acceptance. If this was user intentional L-cut and strict synchronous ambience not required, preserve it. No other21–25 sync/gain repair supported by this snapshot.','minimal_candidate':{'episode':21,'picture_video_id':'cbb71dac-63d8-45b4-bcb0-a15a8be92fb6','track':3,'source_path':str(root/'剧梦生成视频片段/女版/EP21/女版21-01-01.mp4'),'timeline_in_frame':204,'timeline_out_frame_exclusive':209,'source_in_frame':247,'source_out_frame_exclusive':252,'gain_db':-12,'keep_existing_A1':True,'new_audio_duration_seconds':5/24,'not_executed':True}}
q=base/'准备/EP21-25_当前同期声审计.json';q.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(q);print(report['summary']);print([(e['episode'],e['overall_coverage_percent'],len(e['drift_vs_historical'])) for e in report['episodes']])
