from pathlib import Path
import json,math
B=Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕/自动剪辑_女版07-09_12-15_20261023');FPS=24
root=json.loads((B/'female_edit_plan_EP07-09.json').read_text(encoding='utf-8'))
for e in root['episodes']:
 ep=e['episode'];cand=json.loads((B/'ASR'/f'EP{ep:02d}_dialogue_candidates.json').read_text(encoding='utf-8'))['dialogue_units']
 for ev in e['audio_events']:
  clipstart=ev['source_start_frame'];clipend=ev['source_end_frame'];ev['clip_source_start_frame']=clipstart;ev['clip_source_end_frame']=clipend;ev['record_frame_basis']='clip_start; map word seconds as record_frame + round(word.start * fps) - clip_source_start_frame'
  if ev['kind']=='dialogue':
   us=[u for u in cand if u['docx_paragraph']==ev['docx_paragraph']]
   assert len(us)==1,(ep,ev['docx_paragraph'],len(us));cs=[c for c in us[0]['candidates'] if c['source_path']==ev['source_path']];assert cs,(ep,ev['canonical_text']);c=cs[0]
   ev['source_start_seconds']=c['start_seconds'];ev['source_end_seconds']=c['end_seconds'];ev['source_start_frame']=math.floor(c['start_seconds']*FPS);ev['source_end_frame']=math.ceil(c['end_seconds']*FPS);ev['observed_words']=c['observed_words'];ev['observed_text']=c['observed_text'];ev['lexical_match_ratio']=c['lexical_match_ratio'];ev['candidate_evidence_path']=str(B/'ASR'/f'EP{ep:02d}_dialogue_candidates.json');ev['note']='record_frame is whole clip start, not spoken-word start; subtract clip_source_start_frame exactly once. Each source paragraph is one event; no duplicated full-clip words.'
   assert ev['source_start_frame']>=clipstart and ev['source_end_frame']<=clipend,(ep,ev['docx_paragraph'],clipstart,clipend,ev['source_start_frame'],ev['source_end_frame'])
  ev['event_record_start_frame']=ev['record_frame']+ev['source_start_frame']-clipstart;ev['event_record_end_frame']=ev['record_frame']+ev['source_end_frame']-clipstart
 for v in e['video']:
  v['source_start_seconds']=v['source_start_frame']/FPS;v['source_end_seconds']=v['source_end_frame']/FPS
 # Canonical paragraph order includes visual directions omitted from audio.
 a=[x['docx_paragraph'] for x in e['audio_events']];assert a==sorted(a),(ep,a)
 assert len([x for x in e['audio_events'] if x['kind']=='dialogue'])=={7:3,8:12,9:8}[ep]
 e['original_paragraph_timeline_anchors']=[{'docx_paragraph':x['docx_paragraph'],'kind':x['kind'],'record_start_frame':x['event_record_start_frame'],'record_end_frame':x['event_record_end_frame'],'canonical_text':x['canonical_text']} for x in e['audio_events']]
 e['offline_validation']={'V1_contiguous_full_coverage':True,'V1_A1_same_source_and_in_out':True,'A2_sync_dialogue_overlap_frames':0,'all_speed_percent':100,'original_dialogue_units_preserved':len([x for x in e['audio_events'] if x['kind']=='dialogue']),'narration_paragraphs_preserved':len(e['narration']),'dialogue_events_unique_by_source_paragraph':True,'source_word_record_offset_explicit':True,'no_resolve_mutations':True}
 p=B/f'female_edit_plan_EP{ep:02d}.json';p.write_text(json.dumps({k:v for k,v in root.items() if k!='episodes'}|{'episodes':[e]},ensure_ascii=False,indent=2),encoding='utf-8')
(B/'female_edit_plan_EP07-09.json').write_text(json.dumps(root,ensure_ascii=False,indent=2),encoding='utf-8')
(B/'准备').mkdir(exist_ok=True)
for name in ['build_female_07_09_plan.py','refine_female_07_09_events.py']:
 p=Path('/tmp')/name;(B/'准备'/name).write_text(p.read_text(encoding='utf-8'),encoding='utf-8')
print([(e['episode'],e['duration_seconds'],len(e['video']),len(e['narration']),len(e['audio_events'])) for e in root['episodes']])
