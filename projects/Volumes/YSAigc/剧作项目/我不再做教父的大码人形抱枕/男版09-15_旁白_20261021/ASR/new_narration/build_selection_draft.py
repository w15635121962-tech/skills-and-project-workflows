"""Build a 44-slot provisional narration selection with explicit missing slots."""
import csv,datetime,hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parent;TASK=BASE.parents[1]
manifest=json.loads((TASK/'准备/narration_manifest.json').read_text())
audit=json.loads((BASE/'旁白逐词原文核验.json').read_text());files={x['actual_basename']:x for x in audit['files']}
levels={x['source_path']:x for x in json.loads((BASE/'source_levels.json').read_text())['files']}
selections=[]
overrides={'11-02':1,'12-04':1,'12-07':2,'12-08':2,'14-01':2,'14-03':2}
reasons={'12-04':'Retain01: both independent models still plan for original planned in01 and02;02 additionally has from me for original for me in both models.01 is the better complete source, with the planned/plan listening limit explicitly retained. No audio or source text changed.','11-02':'Keep01 provisionally: both01/02 models still hands for original hand;02 large model has extra playing-it discrepancy, no clear whole-segment improvement. Human audition pending.','12-07':'Adopt02 by two independent whole-segment recognizers: original texted restored.01 has model disagreement texts it vs texted.','12-08':'Adopt02 by two independent recognizers: original tense restored,01 both tinned.','14-01':'Provisional02: original at restored vs01 out. Both02 recognizers still color for original collar, a near-homophone requiring actual audition; not declared verbatim pass.','14-03':'Adopt02: both models restore She thought I was dull. Secondary whined/wined is a same-pronunciation spelling flag.'}
missing_reasons={'大码男版枕头12-04-01':'Platform generation failed; root observed credits not consumed. Needs successful new generation after account availability.','大码男版枕头15-03-01':'Not generated; root observed insufficient credits.','大码男版枕头15-04-01':'Not generated; root observed insufficient credits.'}
for g in manifest['groups']:
 logical=g['basename'];segment=f"{g['episode']:02d}-{g['narration_sequence']:02d}";take=overrides.get(segment,1)
 preferred=logical[:-2]+str(take).zfill(2);x=files.get(preferred)
 if x is None and take>1:x=files.get(logical)
 source=x['source_path'] if x else None;level=levels.get(source)
 if source:
  assert Path(source).is_file();h=hashlib.sha256(Path(source).read_bytes()).hexdigest();assert h==x['source_sha256']
  status='PROVISIONAL_SELECTED_AUDIO_AUDITION_PENDING'
  reason=reasons.get(segment,'First downloaded original-speed candidate retained; ASR differences and voice/audition limits remain in linked evidence.')
 else:
  h=None;status='MISSING_AUDIO_EXPLICITLY_EMPTY';reason=missing_reasons.get(logical,'Root reports generated item awaiting final download/recognition; no substitute fabricated.')
 selections.append(dict(logical_basename=logical,episode=g['episode'],narration_sequence=g['narration_sequence'],selected_basename=x['actual_basename'] if x else None,selected_take=x['take'] if x else None,selected_audio_path=source,source_sha256=h,selected_audio_sha256=h,duration_seconds=x['decoded_duration_seconds'] if x else None,suggested_gain_db=level['suggested_speech_gain_db'] if level else None,integrated_loudness_lufs=level['integrated_loudness_lufs'] if level else None,true_peak_dbfs=level['true_peak_dbfs'] if level else None,selection_status=status,selection_reason=reason,generation_speed_percent_requested=100,retime_applied=False,source_docx_paragraphs=g['source_docx_paragraphs'],original_generation_text_sha256=g['generation_text_sha256'],original_generation_text=g['generation_text'],source_asr_json=x['source_asr_json'] if x else None,post_asr_differences=x['differences'] if x else None,complete_original_token_match=x['exact_normalized_original_words_in_order'] if x else None,human_audition_completed=False,voice_identity_proven_by_asr=False))
missing=[x['logical_basename'] for x in selections if x['selected_audio_path'] is None]
levels_pending=[x['logical_basename'] for x in selections if x['selected_audio_path'] and x['suggested_gain_db'] is None]
selection_state='DRAFT_EXPLICIT_MISSING_SLOTS_NOT_FINAL44' if missing else 'ALL44_AUDIO_SELECTED_LOUDNESS_PENDING' if levels_pending else 'ALL44_AUDIO_SOURCES_SELECTED_WITH_AUDITION_LIMITS'
result=dict(created_at_local=datetime.datetime.now().isoformat(),status=selection_state,scope='Male09-15 narrator source selection only. No Resolve mutation or regeneration.',expected_logical_segment_count=44,downloaded_and_recognized_source_file_count=len(files),selected_successful_logical_segments=44-len(missing),missing_logical_basenames=missing,known_failed_generation=[x for x in ['大码男版枕头12-04-01'] if x in missing],known_not_generated_insufficient_credits=[x for x in ['大码男版枕头15-03-01','大码男版枕头15-04-01'] if x in missing],loudness_pending_logical_basenames=levels_pending,all_selected_original_speed_percent_requested=100,source_audio_not_modified=True,all_candidate_files_preserved=True,authority_limit='Source-file adoption only; all44 source availability is complete only when missing and loudness_pending lists are empty. Does not overwrite root generation progress, prove voice identity or exact pronunciation, or claim normal-speed human audition.',selections=selections)
p=BASE.parent/'旁白采用清单_草稿.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+chr(10),encoding='utf-8');tmp.replace(p)
if not missing and not levels_pending:
 final=BASE.parent/'旁白采用清单.json';temporary=final.with_suffix('.tmp');temporary.write_text(json.dumps(result,ensure_ascii=False,indent=2)+chr(10),encoding='utf-8');temporary.replace(final)
c=BASE.parent/'旁白采用清单_草稿.csv'
with c.open('w',newline='',encoding='utf-8-sig') as f:
 writer=csv.DictWriter(f,fieldnames=['episode','narration_sequence','logical_basename','selected_basename','selected_take','duration_seconds','suggested_gain_db','selection_status','selected_audio_path','selection_reason'])
 writer.writeheader();writer.writerows({k:x[k] for k in writer.fieldnames} for x in selections)
print(json.dumps(dict(draft=str(p),selected=44-len(missing),expected=44,missing=missing,source_files=len(files),selected_alternates=[x['selected_basename'] for x in selections if x['selected_take']==2]),ensure_ascii=False),flush=True)
