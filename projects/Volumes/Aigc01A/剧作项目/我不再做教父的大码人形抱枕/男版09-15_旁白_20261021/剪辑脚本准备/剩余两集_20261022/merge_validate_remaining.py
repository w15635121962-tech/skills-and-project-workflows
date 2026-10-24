"""Read-only audit source plans; write new EP12/15 combined delivery only.
No Resolve imports, UI, project or full44 production-state mutation.
"""
from pathlib import Path
import collections,datetime,hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;PREP=HERE.parent;TASK=PREP.parent;OUT=TASK/'剩余两集已完成_20261022';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(PREP));from subtitle_tools import parse_srt

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def norm(s):return re.sub('[^a-z0-9]','',s.lower())
manifest=json.loads((TASK/'准备/narration_manifest.json').read_text());scripts={e['episode']:e for e in manifest['episodes']}
ad=json.loads((OUT/'两集采用清单.json').read_text());adopt={r['logical_basename']:r for r in ad['selections']};assert len(adopt)==12
levels={f.get('path',f.get('source_path')):f for f in json.loads((TASK/'ASR/source_levels.json').read_text())['files']};levels.update({f['source_path']:f for f in json.loads((TASK/'ASR/new_narration/source_levels.json').read_text())['files']})
episodes=[];provenance=[];reports=[];wordsets=[];adopted_used=set()
for number in [12,15]:
 p=HERE/f'EP{number}/EP{number}_真实帧剪辑计划.json';q=HERE/f'EP{number}/EP{number}_原文词事件.json';plan=json.loads(p.read_text());e=plan['episodes'][0];events=json.loads(q.read_text())['episodes'][0]['events']
 assert e['episode']==number and plan['status']=='READY_FOR_NATIVE_ASSEMBLY'
 qcpath=HERE/f'EP{number}/mix_QC/EP{number}_独立剪辑与音频QC.json';qc=json.loads(qcpath.read_text());assert qc['plan_sha256']==sha(p) and qc['word_events_sha256']==sha(q)
 for k in ['source_word_cuts','source_words_missing','source_words_duplicated','vo_vs_role_word_overlaps','source_interval_overlaps','word_events_raw_source_timing_mismatches','word_events_frame_mapping_mismatches']:assert not qc[k],(number,k)
 assert qc['canonical_script_token_order_exact'] and all(c['complete_occurrence_count']==1 for c in qc['role_quote_occurrences'])
 for c in e['video']+e['narration']:
  assert c['speed_percent']==100
  wanted=levels[c['path']]['suggested_speech_gain_db' if c in e['narration'] or c.get('contains_protected_original_dialogue') else 'suggested_ambience_under_vo_gain_db'];assert c['gain_db']==wanted,(number,c,wanted)
 for c in e['narration']:
  selected=adopt[c['logical_basename']];assert selected['selected_audio_path']==c['path'];assert selected['selected_audio_sha256']==c['source_sha256']==sha(c['path']);adopted_used.add(c['logical_basename'])
 assert all(c['same_source_linked_sync_audio'] for c in e['video'])
 cues=parse_srt(e['subtitle_srt']);assert cues
 assert all(0<=a<b<=e['duration_frames'] and len(t.splitlines())<=3 and max(map(len,t.splitlines()))<=26 for a,b,t in cues)
 assert all(a[1]<=b[0] for a,b in zip(cues,cues[1:]))
 assert [norm(w) for _,_,t in cues for w in t.split()]==[norm(w['word']) for w in events]
 target=OUT/f'字幕/EP{number:02d}.srt';target.parent.mkdir(exist_ok=True);original=Path(e['subtitle_srt']).read_bytes()
 if target.exists():assert target.read_bytes()==original
 else:target.write_bytes(original)
 e['subtitle_srt']=str(target)
 episodes.append(e);wordsets.append({'episode':number,'duration_frames':e['duration_frames'],'events':events})
 provenance.append({'episode':number,'path':str(p),'sha256':sha(p),'word_events_path':str(q),'word_events_sha256':sha(q),'av_unmodified':True,'srt_bytes_unmodified':True,'offline_mix_qc':str(qcpath)})
 reports.append({'episode':number,'duration_frames':e['duration_frames'],'seconds':e['duration_frames']/24,'video_and_identical_source_sync_items':len(e['video']),'narration_items':len(e['narration']),'narration_logical_sources':len({c['path'] for c in e['narration']}),'original_role_quotes_complete_once':len(qc['role_quote_occurrences']),'canonical_original_token_count':qc['canonical_script_token_count'],'srt_cue_count':len(cues),'max_explicit_srt_lines':max(len(t.splitlines()) for _,_,t in cues),'subtitle_track_name':str(number),'srt_sha256':sha(target),'voice_gain_equals_measured_source_suggestions':True,'original_speed_percent':100,'integrated_loudness_lufs':qc['integrated_loudness_lufs'],'true_peak_dbfs':qc['true_peak_dbfs'],'complete_normal_speed_human_audition':False,'resolve_used_by_plan_author':False})
assert adopted_used==set(adopt)
combined={'status':'READY_FOR_NATIVE_ASSEMBLY','project':'大码枕头','fps':24,'scope':[12,15],'episodes':episodes,'source_plan_provenance':provenance,'adopted_narration_manifest':str(OUT/'两集采用清单.json'),'assembly_contract':{'same_source_video_and_synchronous_audio_identical_source_and_record_bounds':True,'source_end_frame_exclusive':True,'all_clip_speed_percent':100,'subtitle_import_after_native_av_assembly':True,'subtitle_preset_after_srt_native_import':True,'preserve_existing_58_timelines':True,'completed_five_episodes_frozen':[9,10,11,13,14]},'offline_verification_note':'Only EP12/15 actual8+4 adopted narration sources; all original words and role quotes complete once, voice/sync role words do not overlap. Real secondary-ASR/PCM-verified joins retain earnestly and snapped terminal speech. Full normal-speed listening and native assembly remain separate root operations.'}
final=OUT/'final_native_plan.json';final.write_text(json.dumps(combined,ensure_ascii=False,indent=2)+'\n')
(OUT/'两集_原文词事件.json').write_text(json.dumps({'fps':24,'canonical_original_words_verified':True,'episodes':wordsets,'timing_evidence':'Actual blind raw source ASR; EP12VO05 and EP15VO02 use independent small.en words supported by actual PCM/spectrum, primary evidence preserved. This does not claim human pronunciation verification.'},ensure_ascii=False,indent=2)+'\n')
report={'checked_at_local':datetime.datetime.now().isoformat(),'status':'OFFLINE_READY_NATIVE_IMPORT_NOT_EXECUTED_BY_PLAN_AUTHORS','plan_path':str(final),'plan_sha256':sha(final),'scope':[12,15],'episodes':reports,'totals':{'adopted_narration_logical_sources':len(adopt),'video_and_linked_sync_segments':sum(e['video_and_identical_source_sync_items'] for e in reports),'narration_segments':sum(e['narration_items'] for e in reports),'srt_cues':sum(e['srt_cue_count'] for e in reports),'original_tokens':sum(e['canonical_original_token_count'] for e in reports),'complete_original_role_quotes_once':sum(e['original_role_quotes_complete_once'] for e in reports)},'missing_source_media':[],'frozen_five_not_modified_by_authors':True,'full44_production_progress_not_modified_by_authors':True,'limits':['Offline source still/PCM/spectrum and rendered mix measured; no full normal-speed human audition or actor lip-sync acceptance claimed.','EP12-04 planned/plan lexical ambiguity remains in actual source; captions preserve original planned. Proper-name transcription differences remain explicit.','Source AV same-boundary link is a required contract; actual Resolve links and save/reopen need native root verification.']}
(OUT/'两集合并只读核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'final_plan':str(final),'plan_sha256':sha(final),'episodes':reports,'totals':report['totals']},ensure_ascii=False,indent=2))
