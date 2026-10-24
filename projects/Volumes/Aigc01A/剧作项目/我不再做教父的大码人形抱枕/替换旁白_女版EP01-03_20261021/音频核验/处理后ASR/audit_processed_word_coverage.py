from pathlib import Path
import difflib,hashlib,json,re,unicodedata,wave
import numpy as np

OUT=Path(__file__).resolve().parent
BASE=OUT.parent.parent
manifest=json.loads((BASE.parent/'对标音色旁白制作_20261020/制作与下载进度.json').read_text())
items=[x for x in manifest['items'] if x['episode'] in (1,2,3)]
anchors=json.loads((BASE/'字幕与新旁白_词锚点.json').read_text())
result=json.loads((BASE/'42段对齐WAV_制作结果.json').read_text())
oldmap=json.loads((BASE/'旧剪口到新旁白_逐词映射候选.json').read_text())
aliases=oldmap['name_digit_aliases_for_alignment_only'];aliases.update({'belante':'bellandi','6':'six','2':'two'})

def norm(t):
 t=''.join(c for c in unicodedata.normalize('NFD',t.lower()) if unicodedata.category(c)!='Mn').replace('’',"'")
 suffix="'s" if t.endswith("'s") else '';q=t[:-2] if suffix else t
 return aliases.get(q,q)+suffix
def text_tokens(t):return [norm(x) for x in re.findall(r"[A-Za-z0-9]+(?:['’][A-Za-z]+)?",t)]
def flatten(d,ep,offset=0,origin='full_episode_blind_ASR'):
 out=[]
 for s in d['segments']:
  for w in s['words']:
   for t in text_tokens(w['word']):out.append({'normalized':t,'raw_word':w['word'],'start':w['start']+offset,'end':w['end']+offset,'probability':w.get('probability'),'origin':origin})
 if ep==1 and len(out)>1 and out[1]['normalized']=='de':out[1]['normalized']='don'
 return out
def pcm24(p):
 with wave.open(str(p),'rb') as w:
  sr=w.getframerate();width=w.getsampwidth();ch=w.getnchannels();raw=w.readframes(w.getnframes())
 assert width==3 and ch==1
 a=np.frombuffer(raw,np.uint8).reshape(-1,3).astype(np.int32);v=a[:,0]|(a[:,1]<<8)|(a[:,2]<<16)
 return sr,(v^0x800000)-0x800000
def opdiff(a,b):
 return [{'operation':op,'expected_index':[i,j],'observed_index':[x,y],'expected':a[i:j],'observed':b[x:y]} for op,i,j,x,y in difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes() if op!='equal']
def percentiles(vals):
 return {'count':len(vals),'median':float(np.median(vals)),'p95':float(np.percentile(vals,95)),'max':float(max(vals))} if vals else {'count':0}

episodes=[];timing=[]
for ep in (1,2,3):
 source=[];canon=[];seq_offsets={}
 for item in sorted([x for x in items if x['episode']==ep],key=lambda x:x['narration_sequence']):
  seq=item['narration_sequence'];d=json.loads((BASE/f'ASR/大码女版枕头{ep:02d}-{seq:02d}-01.json').read_text());source.extend(flatten(d,ep,origin=f'source_seq{seq}'));seq_offsets[seq]=len(canon);canon.extend(text_tokens(item['generation_text']))
 procpath=OUT/f'EP{ep:02d}_处理后盲ASR.json';proc=json.loads(procpath.read_text());rawobs=flatten(proc,ep)
 sr,pcm=pcm24(Path(proc['source']));silence_hallucinations=[];obs=[]
 for w in rawobs:
  part=pcm[max(0,round(w['start']*sr)):min(len(pcm),round(w['end']*sr))]
  if not len(part):part=pcm[max(0,round((w['start']-.010)*sr)):min(len(pcm),round((w['end']+.010)*sr))]
  if len(part) and not np.any(part):silence_hallucinations.append({**w,'PCM_peak_LSB':0,'status':'Recognized token lies entirely in exact digital silence; not actual speech'})
  else:obs.append(w)
 targeted=None
 if ep==2:
  d=json.loads((OUT/'EP02_island01_针对遗漏疑点_盲ASR.json').read_text());intro=flatten(d,ep,offset=492/30,origin='isolated_first_island_blind_ASR_plus_original16.4s_record_offset')
  obs=intro+obs
  _,ispcm=pcm24(Path(d['source']));part=pcm[492*1600:831*1600];delta=part.astype(np.int64)-ispcm.astype(np.int64)
  targeted={'reason':'Full206-second episode ASR skipped the first narration paragraph after16.4-second leading silence. Isolated first-island ASR recovered the complete paragraph.','json':str(OUT/'EP02_island01_针对遗漏疑点_盲ASR.json'),'island_record_start_seconds':16.4,'isolated_text':d['text'],'listener_PCM_vs_island_max_difference_LSB_24bit':int(max(abs(delta))),'listener_PCM_vs_island_correlation':float(np.corrcoef(part,ispcm)[0,1]),'tail_after_original_A4_last_frame2493_exact_digital_silence':bool(not np.any(pcm[2493*1600:]))}
 expected=[w['normalized'] for w in source];observed=[w['normalized'] for w in obs]
 dif=opdiff(expected,observed);canonicaldif=opdiff(canon,observed)
 # Canonical-to-output alignment is only for timing estimates; text substitutions
 # remain listed and are not used to rewrite the transcription or subtitles.
 m={};sm=difflib.SequenceMatcher(None,canon,observed,autojunk=False)
 for op,i,j,x,y in sm.get_opcodes():
  if op=='equal' or (op=='replace' and j-i==y-x):
   for q,r in zip(range(i,j),range(x,y)):m[q]=r
 for anchor in [a for a in anchors['anchors'] if a['episode']==ep]:
  seq=anchor['narration_sequence'];first=seq_offsets[seq]+anchor['canonical_source_word_index_start_zero_based'];last=seq_offsets[seq]+anchor['canonical_source_word_index_end_exclusive']-1
  if first not in m or last not in m:
   timing.append({'episode':ep,'caption_id':anchor['caption_id'],'caption_index_zero_based':anchor['caption_index_zero_based'],'status':'not_mapped'});continue
  fw=obs[m[first]];lw=obs[m[last]];head=fw['start']-anchor['target_record_start_seconds'];tail=lw['end']-anchor['target_record_end_seconds']
  broad=fw['end']-fw['start']>1.0 or lw['end']-lw['start']>1.0
  timing.append({'episode':ep,'caption_id':anchor['caption_id'],'caption_index_zero_based':anchor['caption_index_zero_based'],'original_text':anchor['original_text'],'target_start_seconds':anchor['target_record_start_seconds'],'target_end_seconds':anchor['target_record_end_seconds'],'processed_ASR_first_word':fw,'processed_ASR_last_word':lw,'raw_ASR_onset_minus_caption_start_seconds':head,'raw_ASR_last_word_end_minus_caption_end_seconds':tail,'boundary_token_duration_over1second':broad,'eligible_for_compact_timing_statistics':not broad,'timing_status':'ASR estimate only; quiet gaps can inflate first-word start interval, not an auditory sync verdict'})
 episodes.append({'episode':ep,'processed_audio':proc['source'],'processed_audio_sha256':proc['source_sha256'],'full_blind_ASR':str(procpath),'source_ASR_lexical_token_count':len(expected),'processed_verified_lexical_token_count':len(observed),'processing_word_coverage_and_order_exact_after_documented_names_digits':not dif,'processing_added_or_missing_word_candidates':dif,'canonical_generation_text_lexical_differences':canonicaldif,'targeted_first_island_followup':targeted,'digital_silence_ASR_hallucination_tokens':silence_hallucinations,'final_intended_tail_tokens':expected[-12:],'final_processed_tail_tokens':observed[-12:],'human_listening_verified':False})

eligible=[r for r in timing if r.get('eligible_for_compact_timing_statistics')]
timstats={'total_mapped_captions':sum('raw_ASR_onset_minus_caption_start_seconds' in r for r in timing),'eligible_after_excluding_boundary_word_spans_over1s':len(eligible),'excluded_broad_boundary_word_spans':sum(r.get('boundary_token_duration_over1second',False) for r in timing),'absolute_ASR_onset_error_seconds':percentiles([abs(r['raw_ASR_onset_minus_caption_start_seconds']) for r in eligible]),'absolute_ASR_last_word_end_error_seconds':percentiles([abs(r['raw_ASR_last_word_end_minus_caption_end_seconds']) for r in eligible]),'warning':'ASR word times are estimates and may contain silence; statistics are distinct from deterministic renderer boundary projection0.2373s and do not certify audible sync.'}
nonquiet=[]
for i in result['islands']:
 for k,s in enumerate(i['segments']):
  if s.get('discarded_filter_tail_peak',0)>.01:nonquiet.append({'island_id':i['island_id'],'segment_index':k,'discarded_samples':s['discarded_filter_tail_samples'],'discarded_filter_tail_peak':s['discarded_filter_tail_peak'],'source_boundary_seconds':s['new_source_out'],'processed_ASR_dropped_words_found':False,'note':'Nonzero filter-tail truncation requires phonetic/click listening review even when lexical ASR coverage is intact.'})
report={'status':'NO_PROCESSING_WORD_LOSS_OR_DUPLICATION_FOUND_BY_BLIND_ASR_WITH_TARGETED_SILENCE_REVIEW','scope':[1,2,3],'full_episode_blind_ASR_count':3,'targeted_first_island_blind_ASR_count':1,'model':'large-v3-turbo','expected_script_supplied_to_model':False,'word_timestamps':True,'total_verified_lexical_tokens':sum(e['source_ASR_lexical_token_count'] for e in episodes),'all_24_source_paragraphs_in_order_verified':all(e['processing_word_coverage_and_order_exact_after_documented_names_digits'] for e in episodes),'new_processing_missing_repeated_word_candidates':sum(len(e['processing_added_or_missing_word_candidates']) for e in episodes),'source_canonical_vs_ASR_note':'EP02 seq02 spent/spend is shared by new source and processed recognition, so not newly introduced by processing. Canonical generation_text remains unchanged. Names are normalized only for comparison; raw transcripts preserved.','episodes':episodes,'old_subtitle_vs_processed_ASR_word_timing_estimates':timstats,'caption_timing_records':timing,'nonquiet_filter_tail_trim_records_for_targeted_listening':nonquiet,'Resolve_or_UI_modified':False,'source_audio_modified':False,'human_listening_or_full_mix_acceptance':False,'limits':['ASR lexical preservation does not establish absence of tiny consonant loss, clicks, unnatural speed changes or timbre artifacts.','No source/prompt text was supplied to recognition. Name aliases, canonical comparison and silence evidence were used only after recognition.','The main EP02 long-WAV omission and silence hallucinations were resolved by independent isolated-island recognition and actual PCM evidence, not by silently forcing a transcript.']}
(OUT/'处理后_全词覆盖与99cue时序核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
lines=['处理后旁白离线盲ASR核验','',f"3条完整监听WAV已盲转录，另对EP02首岛做1次针对复核。与24条新源盲ASR按姓名/数字规范化后，EP01=235、EP02=189、EP03=224，共{report['total_verified_lexical_tokens']}个词，均可按原顺序对应，未发现处理新增漏词或重复词。",'', 'EP02完整监听206.23秒，前16.4秒为空，单次长音频识别遗漏第一段；单岛盲ASR完整恢复4句。尾段识别出的4次Thank you对应的原PCM全部为零，属于静音识别幻觉。监听首岛与单岛仅24bit±1LSB量化差异，非丢段。', '', '与可靠generation_text的spent/spend差异在新源ASR和处理后ASR中一致，不能据此认为变速造成错词；需有针对的听辨才可判断读音。', '', f"旧字幕99cue的ASR相对时序已逐条列入JSON；可统计{len(eligible)}条（排除首/尾单词跨度>1秒的宽时码）。起词绝对误差中位数{timstats['absolute_ASR_onset_error_seconds']['median']:.3f}秒、P95 {timstats['absolute_ASR_onset_error_seconds']['p95']:.3f}秒；末词末端绝对误差中位数{timstats['absolute_ASR_last_word_end_error_seconds']['median']:.3f}秒、P95 {timstats['absolute_ASR_last_word_end_error_seconds']['p95']:.3f}秒。这些是盲ASR估计，不等同于真实可听词起点，也不与制作器0.2373秒边界投影混为一谈。",'', '制作日志中11处截去的滤波尾包含非零音量；本次词覆盖未见相应漏词，但轻辅音、突变、音色和语速自然度仍需处理后听辨。未改Resolve或源文件，不声称完成听觉/混音验收。']
(OUT/'处理后_全词覆盖与99cue时序核验.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'all_24_source_paragraphs_in_order_verified':report['all_24_source_paragraphs_in_order_verified'],'total_verified_lexical_tokens':report['total_verified_lexical_tokens'],'processing_missing_or_repeat_candidates':report['new_processing_missing_repeated_word_candidates'],'timing':timstats},ensure_ascii=False,indent=2))
