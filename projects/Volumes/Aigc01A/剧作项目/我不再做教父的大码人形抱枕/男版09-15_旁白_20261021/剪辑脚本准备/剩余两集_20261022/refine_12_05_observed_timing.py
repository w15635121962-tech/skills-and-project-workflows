"""Use independently observed small.en word spans for 12-05 where primary
ASR placed its paragraph border across audible earnestly decay. No forced text.
Actual waveform/spectrum checked locally; listening remains unclaimed.
"""
from pathlib import Path
import json,re,math,hashlib
O=Path(__file__).resolve().parent;R=O.parent.parent
output_path=O/'新旁白实际源词时码_EP12-15_候选待采用.json';x=json.loads(output_path.read_text())
f=next(f for f in x['files'] if f['actual_basename']=='大码男版枕头12-05-01')
rawp=R/'ASR/new_narration/secondary_small.en/EP12/大码男版枕头12-05-01.json';raw=json.loads(rawp.read_text())
assert raw['source_sha256']==f['source_sha256']==hashlib.sha256(Path(f['source_path']).read_bytes()).hexdigest()
words=f['original_generation_text'].split();assert len(words)==len(raw['words'])
def norm(s):return re.sub('[^a-z0-9]','',s.lower())
for a,w in zip(words,raw['words']):assert norm(a)==norm(w['word']) or (norm(a),norm(w['word']))==('madam','madame'),(a,w)
f['primary_source_asr_json']=f['source_asr_json'];f['source_asr_json']=str(rawp)
f['source_word_timing_basis']='Independent small.en whole-source word times, selected after joint waveform/spectrum inspection of earnestly/The boundary; raw primary retained separately.'
for p in f['paragraphs']:
 p['canonical_word_events_source_seconds']=[{'original_word':words[j],'start':raw['words'][j]['start'],'end':raw['words'][j]['end'],'observed_source_word_indices':[j],'observed_source_tokens':[raw['words'][j]['word']],'mapping':'actual_secondary_blind_ASR_word_span','source_asr_json':str(rawp)} for j in p['expected_token_indices']]
 p['source_first_observed_word_start_seconds']=p['canonical_word_events_source_seconds'][0]['start'];p['source_last_observed_word_end_seconds']=p['canonical_word_events_source_seconds'][-1]['end']
borders=[0]
for a,b in zip(f['paragraphs'],f['paragraphs'][1:]):borders.append(round((a['source_last_observed_word_end_seconds']+b['source_first_observed_word_start_seconds'])*12))
borders.append(min(math.floor(f['decoded_duration_seconds']*24),math.ceil(f['paragraphs'][-1]['source_last_observed_word_end_seconds']*24)+4))
for p,a,b in zip(f['paragraphs'],borders,borders[1:]):p.update(candidate_source_start_frame=a,candidate_source_end_frame_exclusive=b,candidate_duration_frames=b-a)
f['candidate_last_voice_safe_end_frame']=borders[-1]
f['paragraph_join_waveform_note']={'paragraphs':[367,369],'primary_ASR_border_seconds':4.26,'primary_candidate_frame':102,'selected_frame':116,'selected_seconds':116/24,'actual_secondary_outgoing_word_end_seconds':4.52,'actual_secondary_incoming_word_start_seconds':5.12,'evidence':str(O/'EP12/mix_QC/12-05_earnestly_The_实际波形频谱.png'),'normal_speed_human_audition_completed':False}
x['timing_refinements']=[f['paragraph_join_waveform_note']];output_path.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'file':f['actual_basename'],'paragraph_borders_frames':borders,'secondary_source':str(rawp)},ensure_ascii=False))
