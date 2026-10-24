"""Post-blind-ASR comparison against exact approved narration, no regeneration."""
import datetime,difflib,json,re
from pathlib import Path
BASE=Path(__file__).resolve().parent
TASK=BASE.parents[1]
manifest=json.loads((TASK/'准备/narration_manifest.json').read_text())
index_path=BASE/'转录索引.json'
index=json.loads(index_path.read_text()) if index_path.exists() else dict(files=[])
secondary_path=BASE/'第二次盲识别索引.json'
secondary={x['source_path']:x for x in json.loads(secondary_path.read_text())['files']} if secondary_path.exists() else {}
expected={x['basename']:x for x in manifest['groups']}
paragraphs={p['docx_paragraph']:p for ep in manifest['episodes'] for p in ep['original_paragraphs_and_retained_narration']}
def tokens(text):return re.findall(r"[A-Za-z0-9]+(?:[’'\-][A-Za-z0-9]+)*",text)
def n(t):return re.sub('[^a-z0-9]','',t.lower())
files=[]
for x in index['files']:
 raw=json.loads(Path(x['json_path']).read_text());m=re.fullmatch(r'(大码男版枕头\d{2}-\d{2})-\d{2}',Path(x['source_path']).stem)
 assert m
 logical=m.group(1)+'-01';item=expected[logical]
 wanted=tokens(item['generation_text']);observed=[]
 for i,w in enumerate(raw['words']):
  for t in tokens(w['word']):observed.append(dict(token=t,source_word_index=i,start=w['start'],end=w['end'],probability=w.get('probability')))
 ops=difflib.SequenceMatcher(None,list(map(n,wanted)),[n(w['token']) for w in observed],autojunk=False).get_opcodes()
 diffs=[];anchors=[]
 for tag,a,z,c,d in ops:
  if tag=='equal':
   for i,j in zip(range(a,z),range(c,d)):
    w=observed[j];anchors.append(dict(expected_token_index=i,original_token=wanted[i],source_word_index=w['source_word_index'],observed_token=w['token'],start=w['start'],end=w['end'],probability=w['probability']))
  else:diffs.append(dict(kind=tag,expected_tokens=wanted[a:z],observed_tokens=[w['token'] for w in observed[c:d]],expected_token_indices=list(range(a,z)),observed_token_indices=list(range(c,d))))
 no_diff=not diffs
 probability=[w.get('probability',0) for w in raw['words']]
 low=sum(v<.6 for v in probability)
 status='原文词序匹配_建议采用候选_音色与听感仍需听审' if no_diff else '存在识别差异_需听审_不自动重做或改文'
 if raw.get('quality_flags'):status+='；识别质量标记待复核'
 paragraph_anchors=[];cursor=0
 expected_matches=list(re.finditer(r"[A-Za-z0-9]+(?:[’'\-][A-Za-z0-9]+)*",item['generation_text']))
 for paragraph_index in item['source_docx_paragraphs']:
  paragraph=paragraphs[paragraph_index];retained=paragraph['narration_retained_text'].strip()
  if not tokens(retained):continue
  a=item['generation_text'].find(retained,cursor)
  if a<0:raise AssertionError(('Paragraph text not found in approved generation text',logical,paragraph_index,retained))
  z=a+len(retained);cursor=z
  indices=[i for i,w in enumerate(expected_matches) if w.start()<z and a<w.end()]
  found=[x for x in anchors if x['expected_token_index'] in indices]
  paragraph_anchors.append(dict(docx_paragraph=paragraph_index,source_text=retained,generation_char_start=a,generation_char_end_exclusive=z,expected_token_indices=indices,all_tokens_exactly_observed=len(found)==len(indices),observed_exact_word_anchors=found,observed_source_start_seconds=min((x['start'] for x in found),default=None),observed_source_end_seconds=max((x['end'] for x in found),default=None),timing_limit='Observed anchors only. Missing or non-exact words are not given fabricated timings.'))
 files.append(dict(logical_basename=logical,actual_basename=Path(x['source_path']).stem,episode=x['episode'],narration_sequence=x['narration_sequence'],take=x['take'],source_path=x['source_path'],source_sha256=x['source_sha256'],decoded_duration_seconds=raw['decoded_duration_seconds'],original_generation_text=item['generation_text'],original_docx_paragraphs=item['source_docx_paragraphs'],observed_blind_text=raw['text'],expected_token_count=len(wanted),observed_token_count=len(observed),exact_normalized_original_words_in_order=no_diff,match_ratio=len(anchors)/len(wanted) if wanted else 0,differences=diffs,exact_match_word_anchors=anchors,raw_source_words=raw['words'],source_paragraph_anchors=paragraph_anchors,source_asr_json=x['json_path'],independent_secondary_blind=secondary.get(x['source_path']),quality_flags=raw.get('quality_flags',[]),mean_word_probability=sum(probability)/len(probability) if probability else None,low_confidence_word_count=low,recommendation=status,human_audition=False,voice_identity_not_proven_by_asr=True,source_changed=False,generation_or_text_changes_made=False))
logical_found={x['logical_basename'] for x in files}
result=dict(checked_at_local=datetime.datetime.now().isoformat(),expected_logical_count=len(expected),downloaded_and_blindly_recognized_files=len(files),logical_segments_recognized=len(logical_found),pending_logical_basenames=sorted(set(expected)-logical_found),exact_token_matches=sum(x['exact_normalized_original_words_in_order'] for x in files),need_audition=[x['actual_basename'] for x in files if not x['exact_normalized_original_words_in_order'] or x['quality_flags']],expected_text_given_to_recognizer=False,comparison_only_after_recognition=True,source_audio_or_script_modified=False,generation_not_repeated=True,limitations=['Normalized token match disregards punctuation and casing; this does not prove voice identity, acting quality, exact pronunciation, gain or actual 100 percent speed.','A mismatch can be ASR error or actual generated speech error; preserve both raw output and original, listen before choosing or requesting any new take.','Exact word anchors are source-relative observed intervals, not final timeline/subtitle timings.'],files=files)
p=BASE/'旁白逐词原文核验.json';temporary=p.with_suffix('.tmp');temporary.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');temporary.replace(p)
md=['# 男版09–15新旁白增量核验','',f"已识别{len(files)}个文件，覆盖{len(logical_found)}/44个段落；原文词序匹配{result['exact_token_matches']}个。未制作新音频、未改原文。",'','| 文件 | 时长秒 | 结果 |','|---|---:|---|']
md += [f"| {x['actual_basename']} | {x['decoded_duration_seconds']:.3f} | {x['recommendation']} |" for x in files]
md += ['','词序一致只说明识别结果与原文一致；音色、表演和实际听感仍需听审。存在差异的段保留原文、原始识别与逐词时码，不自动重做。']
(BASE/'旁白逐词原文核验.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(json.dumps(dict(report=str(p),recognized_files=len(files),logical_segments=len(logical_found),pending=len(result['pending_logical_basenames']),exact_token_matches=result['exact_token_matches'],need_audition=result['need_audition']),ensure_ascii=False),flush=True)
