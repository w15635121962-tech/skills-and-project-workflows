"""Offline audit only; never connects to Resolve or changes source media."""
from pathlib import Path
import json, hashlib, sys
from collections import Counter
from datetime import datetime
sys.path.insert(0,str(Path(__file__).resolve().parent))
from subtitle_tools import parse_srt
R=Path(__file__).resolve().parent.parent;O=Path(__file__).resolve().parent
manifest=json.loads((R/'准备/narration_manifest.json').read_text())
inv=json.loads((O/'media_inventory_native.json').read_text())
sources={v['path']:v for e in inv['episodes'] for v in e['videos']}
quotes=json.loads((R/'ASR/同期对白与原带音轨核查.json').read_text())['dialogue_units']
timing=json.loads((O/'新旁白实际源词时码_EP12-15_候选待采用.json').read_text())['files']
report={'scope':'EP13/14 offline plan and source-word/SRT audit only','created_at_local':datetime.now().astimezone().isoformat(),'fps':24,'resolve_used':False,'human_audition_or_continuous_picture_playback_claimed':False,'episodes':[],'limitations':['Source shot choices reviewed with 232 original-frame contact-sheet stills and source scene cuts, not complete real-time playback.','Canonical script words in SRT are preserved; ASR proper-name and homophone differences remain actual-listening limits.','EP14-01 collar/color remains a listening check; not silently called a verified pronunciation.','Plans are single-episode fragments; full all-seven timeline assembly requires final adopted44-VO list and remaining three jobs.']}
for ep in [13,14]:
 p=O/f'EP{ep}_真实帧剪辑计划.json';plan=json.loads(p.read_text());assert plan['fps']==24 and len(plan['episodes'])==1
 e=plan['episodes'][0];assert e['episode']==ep and plan['status']=='READY_FOR_NATIVE_ASSEMBLY'
 words=e['original_word_events'];cues=parse_srt(e['subtitle_srt']);assert [w['word'] for w in words]==' '.join(c[2].replace('\n',' ') for c in cues).split()
 for i,w in enumerate(words):
  assert 0<=w['start_frame']<w['end_frame']<=e['duration_frames']
  assert all(isinstance(w[k],int) for k in ['start_frame','end_frame'])
  if i: assert w['start_frame']>=words[i-1]['start_frame']
 for i,c in enumerate(cues):
  assert c[0]<c[1]<=e['duration_frames']
  if i:assert c[0]>=cues[i-1][1]
  assert len(c[2].splitlines())<=3 and max(map(len,c[2].splitlines()))<=26
 expected_narr=' '.join(g['generation_text'] for g in manifest['groups'] if g['episode']==ep).split()
 narr_words=[w['word'] for w in words if w['type']=='original_new_narration'];assert narr_words==expected_narr
 epq=[q for q in quotes if q['episode']==ep]
 expected_quote=' '.join(q['original_text'] for q in epq).split()
 quote_words=[w['word'] for w in words if w['type']=='original_sync_dialogue'];assert quote_words==expected_quote
 qids=Counter(b['dialogue_unit_id'] for b in e['story_blocks'] if b.get('dialogue_unit_id'));assert qids==Counter({q['id']:1 for q in epq})
 used_files={};last=0
 for c in e['video']:
  assert c['record_frame']==last and c['speed_percent']==100 and c['same_source_linked_sync_audio']
  assert c['path'] in sources and sources[c['path']]['episode_group_segment'][0]==ep and sources[c['path']]['has_embedded_audio']
  assert 0<=c['source_start_frame']<c['source_end_frame']<=int(sources[c['path']]['video_streams'][0]['nb_frames'])
  for a,b in used_files.setdefault(c['path'],[]):assert c['source_end_frame']<=a or c['source_start_frame']>=b
  used_files[c['path']].append((c['source_start_frame'],c['source_end_frame']));last=c['record_frame']+c['source_end_frame']-c['source_start_frame']
 assert last==e['duration_frames']
 narration_files={}
 for c in e['narration']:
  assert c['speed_percent']==100
  narration_files.setdefault(c['path'],[]).append((c['source_start_frame'],c['source_end_frame']))
 for path,ranges in narration_files.items():
  ranges.sort();t=[t for t in timing if t['source_path']==path];assert len(t)==1;t=t[0]
  assert ranges[0][0]==0 and ranges[-1][1]==t['candidate_last_voice_safe_end_frame']
  assert all(a[1]==b[0] for a,b in zip(ranges,ranges[1:]))
  assert Path(path).is_file() and hashlib.sha256(Path(path).read_bytes()).hexdigest()==t['source_sha256']
 prohibited={14:{'男版14-1-1.mp4':[(0,167)],'男版14-1-2.mp4':[(0,20)],'男版14-8-1.mp4':[(0,56)],'男版14-8-2.mp4':[(0,51)]}}.get(ep,{})
 for c in e['video']:
  for a,b in prohibited.get(Path(c['path']).name,[]):assert c['source_end_frame']<=a or c['source_start_frame']>=b
 report['episodes'].append({'episode':ep,'plan':str(p),'plan_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'duration_frames':e['duration_frames'],'duration_seconds':e['duration_frames']/24,'video_and_identical_bound_linked_sync_items':len(e['video']),'narration_items':len(e['narration']),'narration_sources_complete_once':len(narration_files),'original_role_dialogue_quotes_complete_once':len(epq),'srt':e['subtitle_srt'],'srt_sha256':hashlib.sha256(Path(e['subtitle_srt']).read_bytes()).hexdigest(),'cue_count':len(cues),'max_lines':max(len(c[2].splitlines()) for c in cues),'max_line_characters':max(len(l) for c in cues for l in c[2].splitlines()),'original_narration_word_count':len(narr_words),'original_dialogue_word_count':len(quote_words),'all_original_words_once_in_order':True,'nearest24fps_integer_events':True,'cue_overlap_frames':0,'arbitrary4second_split_used':False,'speed_percent':100,'picture_gaps_or_duplicate_source_frames':False,'all_source_audio_cut_together_with_picture':True,'source_non_script_speech_windows_avoided':True,'selected_takes':{Path(path).name:hashlib.sha256(Path(path).read_bytes()).hexdigest() for path in narration_files}})
combined={'status':'READY_FOR_NATIVE_ASSEMBLY','project':'大码枕头','fps':24,'episodes':[],'scope':'EP13/14 fragments only. Merge all seven episodes and final44 narration selection before calling all-episode assembler.'}
for ep in [13,14]:combined['episodes']+=json.loads((O/f'EP{ep}_真实帧剪辑计划.json').read_text())['episodes']
(O/'EP13-14_真实帧剪辑计划_待合并全七集.json').write_text(json.dumps(combined,ensure_ascii=False,indent=2)+'\n')
(O/'EP13-14_离线计划与字幕回读核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps([{k:e[k] for k in ['episode','duration_frames','duration_seconds','cue_count','original_narration_word_count','original_dialogue_word_count','original_role_dialogue_quotes_complete_once']} for e in report['episodes']],ensure_ascii=False,indent=2))
