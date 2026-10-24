"""Independent EP09 source-word, timeline-boundary and exact-plan offline mix QC."""
from pathlib import Path
import collections,datetime,difflib,hashlib,json,math,re,subprocess
BASE=Path(__file__).resolve().parent;TASK=BASE.parents[1];FPS=24;SR=48000;SPF=2000
FF=Path('/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffmpeg')
PLAN=TASK/'剪辑计划_EP09_可落地帧计划.json';EVENTS=TASK/'EP09_原文词事件.json'
plan=json.loads(PLAN.read_text());ep=plan['episodes'][0];assert ep['episode']==9
events=json.loads(EVENTS.read_text())['episodes'][0]['events']
manifest=json.loads((TASK/'准备/narration_manifest.json').read_text())
script=next(x for x in manifest['episodes'] if x['episode']==9)
source_audit=json.loads((TASK/'ASR/同期对白与原带音轨核查.json').read_text())
video_raw={x['source_path']:json.loads(Path(x['json_path']).read_text()) for x in json.loads((TASK/'ASR/转录索引.json').read_text())['files']}
vo_raw={x['source_path']:json.loads(Path(x['json_path']).read_text()) for x in json.loads((TASK/'ASR/new_narration/转录索引.json').read_text())['files']}
def norm(t):return re.sub('[^a-z0-9]','',t.lower())
def tokens(s):return re.findall(r"[A-Za-z0-9]+(?:[’'\-][A-Za-z0-9]+)*",s)
def digest(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for x in iter(lambda:f.read(1048576),b''):h.update(x)
 return h.hexdigest()
def mapword(w,clips):
 start=float(w['start']);end=float(w['end'])
 found=[];partial=[]
 for i,c in enumerate(clips):
  a=c['source_start_frame']/FPS;z=c['source_end_frame']/FPS
  if a<=start+1e-8 and end<=z+1e-8:
   found.append(dict(clip_index=i,start_seconds=start+(c['record_frame']-c['source_start_frame'])/FPS,end_seconds=end+(c['record_frame']-c['source_start_frame'])/FPS,gain_db=c['gain_db']))
  elif max(a,start)<min(z,end)-1e-8:partial.append(i)
 return found,partial
checks=[];timed_vo=[];timed_role=[];role_counts=[];cut_words=[];missing=[];duplicates=[]
for path,raw in vo_raw.items():
 clips=[x for x in ep['narration'] if x['path']==path]
 if not clips:continue
 for i,w in enumerate(raw['words']):
  found,partial=mapword(w,clips)
  if partial:cut_words.append(dict(kind='new_narration',source_path=path,index=i,word=w['word'],source_start=w['start'],source_end=w['end'],partial_clips=partial))
  if len(found)!=1:(missing if not found else duplicates).append(dict(kind='new_narration',source_path=path,index=i,word=w['word'],occurrences=len(found)))
  for v in found:timed_vo.append(dict(**v,source_path=path,source_word_index=i,word=w['word']))
for unit in [u for u in source_audit['dialogue_units'] if u['episode']==9]:
 candidates=[]
 for candidate in unit['source_candidates']:
  path=candidate['source_path'];clips=[x for x in ep['video'] if x['path']==path]
  if not clips:continue
  word_maps=[]
  for w in candidate['word_events']:
   found,partial=mapword(w,clips)
   if partial:cut_words.append(dict(kind='sync_role',unit=unit['id'],source_path=path,word=w['original_word'],source_start=w['start'],source_end=w['end'],partial_clips=partial))
   word_maps.append(found)
  complete=all(len(x)==1 for x in word_maps)
  if complete:
   flat=[x[0] for x in word_maps]
   u=dict(id=unit['id'],original_text=unit['original_text'],source_path=path,record_start_seconds=min(x['start_seconds'] for x in flat),record_end_seconds=max(x['end_seconds'] for x in flat),word_count=len(flat),gain_db_values=sorted(set(x['gain_db'] for x in flat)))
   candidates.append(u)
   for w,m in zip(candidate['word_events'],flat):timed_role.append(dict(**m,source_path=path,unit=unit['id'],word=w['original_word']))
  elif any(word_maps):
   missing.append(dict(kind='sync_role_incomplete_unit',unit=unit['id'],source_path=path))
 role_counts.append(dict(id=unit['id'],original_text=unit['original_text'],complete_occurrence_count=len(candidates),candidates=candidates))
 if len(candidates)!=1:(missing if not candidates else duplicates).append(dict(kind='sync_role_unit',id=unit['id'],count=len(candidates)))
overlap=[]
for a in timed_vo:
 for c in timed_role:
  duration=min(a['end_seconds'],c['end_seconds'])-max(a['start_seconds'],c['start_seconds'])
  if duration>1e-8:overlap.append(dict(vo_word=a['word'],role_word=c['word'],unit=c['unit'],overlap_seconds=duration))
expected=[t for p in script['original_paragraphs_and_retained_narration'] for t in tokens(p['text'])]
actual=[t for e in events for t in tokens(e['word'])]
canonical_match=list(map(norm,expected))==list(map(norm,actual))
assert canonical_match,'Original script token sequence mismatch'
raw_event_mismatch=[];event_coverage_mismatch=[]
for e in events:
 raw=(vo_raw if e['source_kind']=='new_narration' else video_raw)[e['source_path']]
 if 'source_word_index' in e:w=raw['words'][e['source_word_index']]
 else:
  observed=[w for w in raw['words'] if abs(w['start']-e['source_start_seconds'])<1e-7 and abs(w['end']-e['source_end_seconds'])<1e-7]
  assert len(observed)==1,('Nonunique raw word time',e)
  w=observed[0]
 if abs(w['start']-e['source_start_seconds'])>1e-7 or abs(w['end']-e['source_end_seconds'])>1e-7:raw_event_mismatch.append(dict(event=e,actual_word=w))
 clips=[x for x in (ep['narration'] if e['source_kind']=='new_narration' else ep['video']) if x['path']==e['source_path']]
 found,partial=mapword(w,clips)
 if len(found)!=1:event_coverage_mismatch.append(dict(event=e,occurrences=len(found),partial=partial))
 else:
  c=found[0]
  if abs(e['start_frame']/FPS-c['start_seconds'])>1/FPS+.0001 or abs(e['end_frame']/FPS-c['end_seconds'])>1/FPS+.0001:event_coverage_mismatch.append(dict(event=e,actual_timeline_word=c))
for kind in ['video','narration']:
 clips=ep[kind];last=0
 for c in clips:
  assert c['record_frame']>=last
  if kind=='video':assert c['record_frame']==last
  last=c['record_frame']+c['source_end_frame']-c['source_start_frame']
  assert last<=ep['duration_frames'] and c['speed_percent']==100
 if kind=='video':assert last==ep['duration_frames']
assert not missing and not duplicates and not cut_words and not overlap and not raw_event_mismatch and not event_coverage_mismatch
paths=sorted({x['path'] for k in ['video','narration'] for x in ep[k]});hashes={p:digest(p) for p in paths}
input_index={p:i for i,p in enumerate(paths)}
channels={}
for path in paths:
 proc=subprocess.run([str(FF.with_name('ffprobe')),'-v','error','-select_streams','a:0','-show_entries','stream=channels','-of','json',path],capture_output=True,text=True,check=True)
 channels[path]=json.loads(proc.stdout)['streams'][0]['channels']
 assert channels[path] in [1,2]

uses=collections.Counter(x['path'] for k in ['video','narration'] for x in ep[k]);feed={};filter_lines=[]
for path,n in uses.items():
 labels=[f'src{input_index[path]}_{i}' for i in range(n)];feed[path]=iter(labels)
 core=f'[{input_index[path]}:a]aresample={SR}'+(',pan=stereo|c0=c0|c1=c0' if channels[path]==1 else '')+',aformat=sample_fmts=fltp:channel_layouts=stereo'
 if n==1:filter_lines.append(core+'['+labels[0]+']')
 else:filter_lines.append(core+f',asplit={n}'+''.join('['+s+']' for s in labels))
for kind in ['video','narration']:
 sequence=[];cursor=0
 for i,c in enumerate(ep[kind]):
  if c['record_frame']>cursor:
   label=f'{kind}_gap{i}';samples=(c['record_frame']-cursor)*SPF
   filter_lines.append(f'anullsrc=channel_layout=stereo:sample_rate={SR},atrim=end_sample={samples}[{label}]');sequence.append(label)
  source=next(feed[c['path']]);label=f'{kind}_clip{i}'
  filter_lines.append(f'[{source}]atrim=start_sample={c["source_start_frame"]*SPF}:end_sample={c["source_end_frame"]*SPF},asetpts=PTS-STARTPTS,volume={c["gain_db"]}dB[{label}]');sequence.append(label)
  cursor=c['record_frame']+c['source_end_frame']-c['source_start_frame']
 if cursor<ep['duration_frames']:
  label=f'{kind}_tail';samples=(ep['duration_frames']-cursor)*SPF
  filter_lines.append(f'anullsrc=channel_layout=stereo:sample_rate={SR},atrim=end_sample={samples}[{label}]');sequence.append(label)
 filter_lines.append(''.join('['+s+']' for s in sequence)+f'concat=n={len(sequence)}:v=0:a=1[{kind}_track]')
filter_lines.append('[video_track][narration_track]amix=inputs=2:duration=longest:dropout_transition=0:normalize=0[mix]')
filt=BASE/'exact_plan_filter.txt';filt.write_text(';\n'.join(filter_lines),encoding='utf-8')
wave=BASE/'EP09_按计划原始增益_通道幅度保持_完整音频mix.wav';assert not wave.exists()
cmd=[str(FF),'-nostdin','-hide_banner','-loglevel','error']
for p in paths:cmd += ['-i',p]
cmd += ['-filter_complex_script',str(filt),'-map','[mix]','-c:a','pcm_s24le','-ar',str(SR),'-t',str(ep['duration_frames']/FPS),str(wave)]
q=subprocess.run(cmd,capture_output=True,text=True);assert q.returncode==0,q.stderr
preview=BASE/'EP09_按计划原始增益_通道幅度保持_试听.mp3';assert not preview.exists()
q=subprocess.run([str(FF),'-nostdin','-hide_banner','-loglevel','error','-i',str(wave),'-c:a','libmp3lame','-b:a','160k',str(preview)],capture_output=True,text=True);assert q.returncode==0,q.stderr
q=subprocess.run([str(FF),'-nostdin','-hide_banner','-nostats','-i',str(wave),'-af','ebur128=peak=true,volumedetect','-f','null','-'],capture_output=True,text=True);assert q.returncode==0
log=BASE/'EP09_mix_loudness.log';log.write_text(q.stderr,encoding='utf-8')
def last(pattern):
 m=re.findall(pattern,q.stderr,re.MULTILINE)
 return float(m[-1]) if m and m[-1] not in ['-inf','inf','nan'] else None
for p,h in hashes.items():assert digest(p)==h,'Source altered'
report=dict(checked_at_local=datetime.datetime.now().isoformat(),episode=9,plan=str(PLAN),plan_sha256=digest(PLAN),word_events_path=str(EVENTS),word_events_sha256=digest(EVENTS),timeline_frames=ep['duration_frames'],seconds=ep['duration_frames']/FPS,canonical_script_token_count=len(expected),word_events_count=len(events),canonical_script_token_order_exact=canonical_match,new_narration_words_checked=len(timed_vo),sync_role_words_checked=len(timed_role),source_word_cuts=cut_words,source_words_missing=missing,source_words_duplicated=duplicates,vo_vs_role_word_overlaps=overlap,word_events_raw_source_timing_mismatches=raw_event_mismatch,word_events_frame_mapping_mismatches=event_coverage_mismatch,role_quote_occurrences=role_counts,whole_project_original_role_quotes=40,this_episode_original_role_quotes=len(role_counts),other_episodes_not_in_this_mix=34,source_files_unchanged=True,source_sha256=hashes,original_speed_percent=100,full_mix_wav=str(wave),small_preview_mp3=str(preview),rendered_mix_gain_policy='Proposed plan clip gains only; mono input duplicated amplitude-preserving into stereo. No hidden equal-power attenuation, normalization, compression, crossfade, speed change or invented ducking in QC.',source_audio_channels=channels,mono_to_stereo_policy='mono c0 copied at unity to both output channels; conservative peak preview. Actual Resolve pan law is not queried and can change playback level.',integrated_loudness_lufs=last(r'^\s*I:\s*([-+\d.inf]+)\s*LUFS'),true_peak_dbfs=last(r'^\s*Peak:\s*([-+\d.inf]+)\s*dBFS'),mean_volume_dbfs=last(r'mean_volume:\s*([-+\d.inf]+)\s*dB'),max_volume_dbfs=last(r'max_volume:\s*([-+\d.inf]+)\s*dB'),gain_recommendation='Current VO plan clips still use 0dB; use source-specific recommendations in ASR/new_narration/source_levels.json before final mix. This render intentionally reflects the current plan.',human_normal_speed_audition_performed=False,limits=['Source word time and plan checks do not prove actor lip sync, music absence or final human listening quality.','Only six original role quotes belong to EP09; remaining34 across EP10-15 are not expected in this episode.','Source-relative word handles are observed ASR evidence; phonetic/proper-name differences are preserved as pending audition, never regenerated by QC.'])
(BASE/'EP09_独立剪辑与音频QC.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['episode','seconds','canonical_script_token_count','new_narration_words_checked','sync_role_words_checked','source_word_cuts','vo_vs_role_word_overlaps','integrated_loudness_lufs','true_peak_dbfs','full_mix_wav','small_preview_mp3']},ensure_ascii=False,indent=2))
