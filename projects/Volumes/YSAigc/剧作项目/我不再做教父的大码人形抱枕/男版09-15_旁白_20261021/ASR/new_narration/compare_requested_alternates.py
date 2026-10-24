"""Compare downloaded existing free candidate2 whole segments after blind ASR."""
import datetime,json,re
from pathlib import Path
BASE=Path(__file__).resolve().parent
requests=[('11-02','Her hand still rested on my neck','hand/hands'),('12-04','where I planned to go tomorrow','planned/plan; candidate2 adds for/from'),('12-07','She never texted back','texted/texts it'),('12-08','Unlike my tense silence','tense/tinned'),('14-01','Evan tugged at her collar','at/out'),('14-03','She thought I was dull','I/it')]
audit=json.loads((BASE/'旁白逐词原文核验.json').read_text());byname={x['actual_basename']:x for x in audit['files']}
secondary_path=BASE/'第二次盲识别索引.json';secondary={x['source_path']:x for x in json.loads(secondary_path.read_text())['files']} if secondary_path.exists() else {}
levels_path=BASE/'source_levels.json';levels={x['source_path']:x for x in json.loads(levels_path.read_text())['files']} if levels_path.exists() else {}
name_words={'Vittoria','Aldwick','Madam','Evan','Oliver','Blackwood','Blackwoods'}
def only_name(d):return len(d['expected_tokens'])==1 and d['expected_tokens'][0] in name_words
rows=[]
for segment,phrase,issue in requests:
 names=['大码男版枕头'+segment+'-'+str(n).zfill(2) for n in [1,2]];takes=[]
 for name in names:
  x=byname.get(name)
  if not x:continue
  substantive=[d for d in x['differences'] if not only_name(d)]
  takes.append(dict(basename=name,source_path=x['source_path'],source_sha256=x['source_sha256'],duration_seconds=x['decoded_duration_seconds'],original_text=x['original_generation_text'],primary_blind_text=x['observed_blind_text'],secondary_blind=secondary.get(x['source_path']),all_differences=x['differences'],content_differences_excluding_names=substantive,exact_normalized_original_words_in_order=x['exact_normalized_original_words_in_order'],source_word_anchors=x['exact_match_word_anchors'],raw_source_words=x['raw_source_words'],source_paragraph_anchors=x['source_paragraph_anchors'],levels=levels.get(x['source_path']),human_audition=False))
 a=next((x for x in takes if x['basename']==names[0]),None);z=next((x for x in takes if x['basename']==names[1]),None)
 preferred=None;status='waiting_existing_free_second_candidate_download'
 if z:
  if z['exact_normalized_original_words_in_order'] and (not a or not a['exact_normalized_original_words_in_order']):
   preferred=z['source_path'];status='candidate2_recommended_by_complete_original_token_match_pending_voice_and_normal_speed_audition'
  elif z['content_differences_excluding_names']==[] and a and a['content_differences_excluding_names']:
   preferred=z['source_path'];status='candidate2_recommended_by_improved_complete_content_with_only_name_spelling_flags_pending_audition'
  elif a and a['exact_normalized_original_words_in_order'] and not z['exact_normalized_original_words_in_order']:
   preferred=a['source_path'];status='candidate1_has_better_full_original_token_match_pending_audition'
  elif z['exact_normalized_original_words_in_order'] and a and a['exact_normalized_original_words_in_order']:
   preferred=a['source_path'];status='both_complete_original_tokens_no_need_to_switch_for_text_only'
  else:status='both_have_recognition_differences_do_not_auto_choose_or_regenerate'
 if segment=='11-02' and a:
  preferred=a['source_path'];status='candidate1_retained_provisionally_both_takes_hands_but_candidate2_has_additional_primary_ASR_phrase_discrepancy_no_whole_segment_improvement'
 if segment=='12-04' and a and z:
  preferred=a['source_path'];status='candidate1_retained_both_models_still_plan_for_planned_in_both_takes_candidate2_adds_from_for_original_for_no_whole_segment_improvement_listening_limit_retained'
 if segment=='14-01' and z:
  preferred=z['source_path'];status='candidate2_provisionally_preferred_at_restored_but_collar_color_homophone_requires_actual_audition_not_verbatim_pass'
 rows.append(dict(logical_segment=segment,original_phrase_to_check=phrase,issue=issue,expected_alternate_basename=names[1],takes=takes,recommendation=status,recommended_source_path=preferred,existing_sources_preserved=True,source_text_not_changed=True,new_generation_requested=False,timeline_not_modified=True))
result=dict(checked_at_local=datetime.datetime.now().isoformat(),scope='Compare only existing free second candidates, no regeneration, no text changes, no Resolve operations.',items=rows,limitations=['ASR word matches are evidence for selection but not a claim of normal-speed human listening or voice identity.','Read whole-segment differences before selecting; do not trade one original word for another new omission or substitution.','If only names differ, do not order a paid remake or rewrite the source.'])
p=BASE/'候选2整段比较与采用建议.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+chr(10),encoding='utf-8');tmp.replace(p)
print(json.dumps([dict(segment=x['logical_segment'],takes=len(x['takes']),recommendation=x['recommendation'],recommended_source_path=x['recommended_source_path']) for x in rows],ensure_ascii=False),flush=True)
