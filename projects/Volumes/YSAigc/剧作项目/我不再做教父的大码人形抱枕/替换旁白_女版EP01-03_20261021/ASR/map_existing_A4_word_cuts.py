from pathlib import Path
import difflib,hashlib,json,re,unicodedata

BASE=Path(__file__).resolve().parent.parent
ASR=BASE/'ASR'
SNAP=BASE/'替换前_完整时间线实读.json'
snapshot=json.loads(SNAP.read_text())

ALIASES={'mateo':'matteo','mattel':'matteo','matea':'matteo','belendi':'bellandi','belandi':'bellandi','belanti':'bellandi','bolendi':'bellandi','blandi':'bellandi','bolandi':'bellandi','balandi':'bellandi','belongde':'bellandi','balandas':'bellandis','balanda':'bellandi','balandis':'bellandis','belandis':'bellandis','varena':'varenna','verena':'varenna','pantaos':'penthouse','10':'ten','18':'eighteen'}
def normalized(s):
 s=''.join(ch for ch in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(ch)!='Mn').replace('’',"'")
 s=re.sub(r'[^a-z0-9\']','',s);suffix="'s" if s.endswith("'s") else '';q=s[:-2] if suffix else s
 return ALIASES.get(q,q)+suffix
def tokens(d,ep,seq):
 out=[];wi=0
 for seg in d['segments']:
  for w in seg['words']:
   q=normalized(w['word']);exp=['don','matteo'] if q=='donmeteo' else ['don'] if ep==1 and seq==1 and q=='de' else [q]
   for norm in exp:out.append({'normalized':norm,'asr_word_index':wi,'word':w})
   wi+=1
 return out

pair_records=[];clip_records=[]
for e in snapshot['timelines']:
 ep=e['ep'];fps=e['fps'];a4=next(t for t in e['tracks']['audio'] if t['index']==4);clips=a4['items']
 names=list(dict.fromkeys(c['name'] for c in clips))
 for name in names:
  seq=int(Path(name).stem.split('-')[-1]);old_path=ASR/(Path(name).stem+'.json');new_path=ASR/f'大码女版枕头{ep:02d}-{seq:02d}-01.json'
  old=json.loads(old_path.read_text());new=json.loads(new_path.read_text());ot=tokens(old,ep,seq);nt=tokens(new,ep,seq)
  oa=[x['normalized'] for x in ot];na=[x['normalized'] for x in nt]
  matcher=difflib.SequenceMatcher(None,oa,na,autojunk=False);mapping={};diff=[]
  for op,i,j,x,y in matcher.get_opcodes():
   if op=='equal':
    for k,l in zip(range(i,j),range(x,y)):mapping[k]=l
   else:
    diff.append({'operation':op,'old_normalized_tokens':oa[i:j],'new_normalized_tokens':na[x:y],'old_ASR_words':[t['word']['word'] for t in ot[i:j]],'new_ASR_words':[t['word']['word'] for t in nt[x:y]],'old_word_times':[t['word'] for t in ot[i:j]],'new_word_times':[t['word'] for t in nt[x:y]],'status':'ASR-only lexical difference, not proof of spoken/source-text change; canonical generation_text retained separately'})
    # An equal-size substitution can be located by its surrounding exact word run,
    # but the literal discrepancy remains explicit and is not silently corrected.
    if op=='replace' and j-i==y-x:
     for k,l in zip(range(i,j),range(x,y)):mapping[k]=l
  group=[(i,c) for i,c in enumerate(clips) if c['name']==name]
  assigned={i:[] for i,c in group};zero_overlap=[]
  for k,tok in enumerate(ot):
   w=tok['word'];scores=[]
   for i,c in group:
    lo,hi=c['source_start'],c['source_end'];over=max(0,min(hi,w['end'])-max(lo,w['start']));distance=max(lo-w['end'],w['start']-hi,0)
    scores.append((over,-distance,-i,i))
   score=max(scores);chosen=score[3];assigned[chosen].append(k)
   if score[0]<=0:zero_overlap.append({'old_token_index':k,'word':w,'assigned_to_clip_index':chosen,'reason':'No overlap with any retained old range, closest adjacent clip chosen only as a review candidate'})
  pr={'episode':ep,'sequence':seq,'old_source':old['source'],'new_source':new['source'],'old_ASR':str(old_path),'new_ASR':str(new_path),'old_source_sha256':old['source_sha256'],'new_source_sha256':new['source_sha256'],'old_decoded_duration':old['duration'],'new_decoded_duration':new['duration'],'raw_old_ASR_text':old['text'],'raw_new_ASR_text':new['text'],'new_canonical_generation_text':new['generation_text_after_recognition_only'],'tokens_equal_after_documented_name_digit_aliases':oa==na,'ASR_only_differences':diff,'old_tokens_without_any_retained_overlap':zero_overlap,'all_old_tokens_mapped_to_new':len(mapping)==len(ot),'timeline_clip_count':len(group)}
  pair_records.append(pr)
  for i,c in group:
   ks=assigned[i];ns=sorted({mapping[k] for k in ks if k in mapping});assert ks and ns
   nw=[];seen=set()
   for k in ns:
    w=nt[k]
    if w['asr_word_index'] not in seen:nw.append(w['word']);seen.add(w['asr_word_index'])
   ni=nw[0]['start'];no=nw[-1]['end'];slot=c['duration']/fps;span=no-ni;speed=span/slot*100
   ow=[];seen=set()
   for k in ks:
    t=ot[k]
    if t['asr_word_index'] not in seen:ow.append(t['word']);seen.add(t['asr_word_index'])
   crossed_in=[w for s in old['segments'] for w in s['words'] if w['start']<c['source_start']<w['end']]
   crossed_out=[w for s in old['segments'] for w in s['words'] if w['start']<c['source_end']<w['end']]
   naive_in=[w for s in new['segments'] for w in s['words'] if w['start']<c['source_start']<w['end']]
   naive_out=[w for s in new['segments'] for w in s['words'] if w['start']<c['source_end']<w['end']]
   clip_records.append({'episode':ep,'clip_index_zero_based':i,'old_clip_id':c['id'],'record_start_frame':c['start'],'record_end_frame_exclusive':c['end'],'record_duration_frames':c['duration'],'timeline_fps':fps,'record_slot_duration_seconds':slot,'old_source_name':name,'old_source':old['source'],'old_source_in_seconds':c['source_start'],'old_source_out_seconds':c['source_end'],'old_native_speed_percent_estimated':(c['source_end']-c['source_start'])/slot*100,'old_ASR_words_crossing_in':crossed_in,'old_ASR_words_crossing_out':crossed_out,'intended_old_complete_words':ow,'new_source':new['source'],'new_source_sha256':new['source_sha256'],'new_complete_words':nw,'new_complete_words_text':' '.join(w['word'].strip() for w in nw),'candidate_new_ASR_word_span_in_seconds':ni,'candidate_new_ASR_word_span_out_seconds':no,'candidate_span_seconds':span,'speed_percent_to_fit_ASR_word_span_in_unchanged_record_slot':round(speed,4),'relative_rate_to_old110':round(speed/110,6),'ASR_word_span_duration_at110':span/1.1,'overrun_seconds_at110':max(0,span/1.1-slot),'unused_record_slot_seconds_at110':max(0,slot-span/1.1),'naive_same_old_source_offsets_cross_new_ASR_word_at_in':naive_in,'naive_same_old_source_offsets_cross_new_ASR_word_at_out':naive_out,'matching_status':'all intended words mapped, documented ASR-only substitutions need targeted listening' if diff else 'all intended words mapped after documented name/digit aliases','waveform_and_phoneme_boundaries_verified':False,'final_new_source_range_ready_for_import':False,'notes':['ASR first/last-word spans are candidate lexical bounds, not final waveform-safe trims.','Speed estimate uses actual new per-phrase word span divided by unchanged record slot, never total-file duration scaling.','Keep pitch correction if native retiming is chosen; no retime or audio export performed.','If a phrase is shorter than its slot at110, preserve deliberate pause instead of forcing slow motion.']})

report={'status':'WORD_MAPPING_CANDIDATES_NOT_FINAL_AUDIO_TRIMS','input_snapshot':str(SNAP),'input_snapshot_sha256':hashlib.sha256(SNAP.read_bytes()).hexdigest(),'scope':[1,2,3],'total_old_A4_clips':len(clip_records),'new_VO_count':len(pair_records),'timelines_untouched':True,'source_audio_untouched':True,'actual_speed_processing_done':False,'Resolve_UI_or_project_modified':False,'mapping_policy':'Associate whole old-ASR words with retained clips by maximum temporal overlap, map normalized name/digit aliases to new-ASR word sequence; every lexical difference remains visible. This repairs candidate word ownership where an old cut crosses a word, but requires human/waveform validation before applying.','name_digit_aliases_for_alignment_only':ALIASES,'special_aliases':['old Donmeteo -> don + matteo (same original word times retained)','new EP01seq01 de -> don for aligning known canonical Mafia Don Matteo; raw ASR retained'],'pairs':pair_records,'clips':clip_records,'limits':['No speed changes, source audio edits, Resolve changes or source media renaming.','ASR may include leading silence within first-word times and may end before quiet phoneme tails; candidate rates can change after waveform-safe repair.','Full 26-cut EP01 fixed record slots plus globally fixed110% is generally incompatible with the observed new phrase durations unless pauses/audio placement are adapted.','No full human listening acceptance claimed.']}
p=BASE/'旧剪口到新旁白_逐词映射候选.json';p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
summary={'total_clips':len(clip_records),'pairs':len(pair_records),'EP01_clip_count':sum(c['episode']==1 for c in clip_records),'EP01_speed_range':[min(c['speed_percent_to_fit_ASR_word_span_in_unchanged_record_slot'] for c in clip_records if c['episode']==1),max(c['speed_percent_to_fit_ASR_word_span_in_unchanged_record_slot'] for c in clip_records if c['episode']==1)],'ASR_differences':[{'episode':p['episode'],'sequence':p['sequence'],'diff':p['ASR_only_differences']} for p in pair_records if p['ASR_only_differences']],'zero_overlap_old_words':[{'episode':p['episode'],'sequence':p['sequence'],'words':p['old_tokens_without_any_retained_overlap']} for p in pair_records if p['old_tokens_without_any_retained_overlap']]}
print(json.dumps(summary,ensure_ascii=False,indent=2))
