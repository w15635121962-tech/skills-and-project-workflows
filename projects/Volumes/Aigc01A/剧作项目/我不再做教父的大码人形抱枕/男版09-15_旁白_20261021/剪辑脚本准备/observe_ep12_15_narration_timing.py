"""Read actual new-VO ASR only. Map canonical source tokens to OBSERVED word spans.
No invented word timings, forced recognition, audio changes, or Resolve operations.
These are candidate timings until actual takes/content are reviewed and adopted.
"""
from pathlib import Path
import hashlib,json,math,re
ROOT=Path(__file__).resolve().parent.parent
OUT=Path(__file__).resolve().parent
manifest=json.loads((ROOT/'准备/narration_manifest.json').read_text())
audit=json.loads((ROOT/'ASR/new_narration/旁白逐词原文核验.json').read_text())
result={'status':'ACTUAL_SOURCE_TIMING_CANDIDATES_NOT_FINAL_ADOPTED_EDIT','fps':24,'scope':'Observed source audio word times and original text mapping only; no interpolation or missing audio duration supplied. All lexical differences remain explicit review items.','canonical_original_words_verified_for_final_srt':False,'files':[],'pending':[]}
rows={}
for f in audit['files']:rows.setdefault(f['logical_basename'],[]).append(f)
for g in manifest['groups']:
 if g['episode'] not in range(12,16):continue
 if not rows.get(g['basename']):result['pending'].append(g['basename']);continue
 for f in rows[g['basename']]:
  assert Path(f['source_path']).exists()
  assert hashlib.sha256(Path(f['source_path']).read_bytes()).hexdigest()==f['source_sha256']
  display=g['generation_text'].split();assert len(display)==f['expected_token_count'],g['basename']
  mapped={x['expected_token_index']:{'original_word':display[x['expected_token_index']],'start':x['start'],'end':x['end'],'observed_source_word_indices':[x['source_word_index']],'observed_source_tokens':[x['observed_token']],'mapping':'exact_normalized_ASR_word'} for x in f['exact_match_word_anchors']}
  for diff in f['differences']:
   ee=diff['expected_token_indices'];oo=diff['observed_token_indices']
   # A single canonical written token may map to an actually observed expansion
   # (e.g. twenty-three ->23, I'd ->I had). Its true span is the observed union.
   # This records time evidence but NEVER certifies the pronunciation/content.
   if diff['kind']=='replace' and len(ee)==1 and oo:
    observed=[f['raw_source_words'][j] for j in oo]
    mapped[ee[0]]={'original_word':display[ee[0]],'start':min(w['start'] for w in observed),'end':max(w['end'] for w in observed),'observed_source_word_indices':oo,'observed_source_tokens':[w['word'] for w in observed],'mapping':'actual_observed_replacement_span_requires_lexical_review','difference':diff}
  missing=sorted(set(range(f['expected_token_count']))-set(mapped))
  pp=[]
  for p in f['source_paragraph_anchors']:
   indices=p['expected_token_indices'];words=[mapped[j] for j in indices if j in mapped]
   pp.append({'docx_paragraph':p['docx_paragraph'],'original_text':p['source_text'],'expected_token_indices':indices,'unmapped_token_indices':[j for j in indices if j not in mapped],'source_first_observed_word_start_seconds':min((w['start'] for w in words),default=None),'source_last_observed_word_end_seconds':max((w['end'] for w in words),default=None),'canonical_word_events_source_seconds':words,'all_expected_tokens_have_actual_observed_span':len(words)==len(indices)})
  assert len({p['docx_paragraph'] for p in pp})==len(pp)
  row={'logical_basename':g['basename'],'actual_basename':f['actual_basename'],'episode':g['episode'],'source_path':f['source_path'],'source_sha256':f['source_sha256'],'decoded_duration_seconds':f['decoded_duration_seconds'],'original_generation_text':g['generation_text'],'source_asr_json':f['source_asr_json'],'differences':f['differences'],'all_expected_tokens_have_actual_observed_span':not missing,'missing_token_indices':missing,'paragraphs':pp,'lexical_or_pronunciation_review_complete':bool(f['exact_normalized_original_words_in_order'] and not f['quality_flags']),'human_audition_claimed':False}
  # Source-only paragraph splits: midpoint of two observed word boundaries.
  # Frames remain 100%; no output record times are inferred here.
  if not missing:
   ends=[max(mapped[j]['end'] for j in p['expected_token_indices']) for p in f['source_paragraph_anchors']]
   starts=[min(mapped[j]['start'] for j in p['expected_token_indices']) for p in f['source_paragraph_anchors']]
   borders=[0]
   for i in range(len(pp)-1):
    a,b=ends[i],starts[i+1];assert a<=b+1e-5,(g['basename'],i,a,b)
    borders.append(round((a+b)*12))
   end=min(math.floor(f['decoded_duration_seconds']*24),math.ceil(ends[-1]*24)+4)
   borders.append(end)
   assert all(a<b for a,b in zip(borders,borders[1:]))
   for i,p in enumerate(pp):
    p.update(candidate_source_start_frame=borders[i],candidate_source_end_frame_exclusive=borders[i+1],candidate_duration_frames=borders[i+1]-borders[i])
   row['candidate_last_voice_safe_end_frame']=end
  result['files'].append(row)
result['logical_observed_count']=len({f['logical_basename'] for f in result['files']})
p=OUT/'新旁白实际源词时码_EP12-15_候选待采用.json';p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'output':str(p),'logical_observed':result['logical_observed_count'],'pending':result['pending'],'mapping_rows':len(result['files']),'all_present_rows_have_observed_spans':all(f['all_expected_tokens_have_actual_observed_span'] for f in result['files'])},ensure_ascii=False))
