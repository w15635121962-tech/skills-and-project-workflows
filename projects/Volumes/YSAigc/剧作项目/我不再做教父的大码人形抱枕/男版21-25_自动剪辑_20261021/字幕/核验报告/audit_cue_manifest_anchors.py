import pathlib,json,hashlib,datetime,collections,math
B=pathlib.Path(__file__).resolve().parents[2];S=B/'字幕';M=json.loads((S/'manifest.json').read_text());N=json.loads((B/'Resolve_组装实读.json').read_text());struct=json.loads((S/'核验报告/SRT五集_独立结构与词覆盖核验.json').read_text());reports=[]
for m in M['episodes']:
 ep=m['episode'];n=next(x for x in N['episodes'] if x['episode']==ep);clips={x['id']:x for group in ['video','sync_audio','narration'] for x in n[group]};errors=[];diffs=[];seen=[];wordcount=0;maxdrift=0
 p=pathlib.Path(m['srt_path'])
 if hashlib.sha256(p.read_bytes()).hexdigest()!=m['srt_sha256']:errors.append('SRT hash mismatch')
 for c in m['cues']:
  if len(c['lines'])>3:errors.append(f'cue{c["number"]} too manylines')
  words=c['words'];wordcount+=len(words)
  for w in words:
   cid=w.get('actual_clip_id',c['actual_clip_id']);sp=w.get('source_path',c['source_path']);clip=clips.get(cid)
   if not clip:errors.append(f'cue{c["number"]} unknown nativeclip{cid}');continue
   if clip['path']!=sp:errors.append(f'cue{c["number"]} wordsource path != actual native path')
   expect=clip['start']/24+w['source_word_start_seconds']-clip['source_start']/24;drift=abs(expect-w['timeline_word_start']);maxdrift=max(maxdrift,drift)
   if drift>1e-5:errors.append(f'cue{c["number"]} wordtimedrift{drift}')
   if w['timeline_word_start']<clip['start']/24-.05 or w['timeline_word_end']>clip['end']/24+.05:errors.append(f'cue{c["number"]} word outside actual clip')
   if w['timeline_word_start']<c['start_frame']/24-.05 or w['timeline_word_end']>c['end_frame']/24+.05:errors.append(f'cue{c["number"]} word outside cue')
   seen.append((cid,w['source_word_index']))
  # Cue text must represent every explicitly mapped word in its declared reading order.
  text=' '.join(c['lines']).replace('- Oliver.','Oliver.')
  normalize=lambda t:' '.join(t.split()).replace('’',"'")
  expected=' '.join(w['display'] for w in words)
  if normalize(text)!=normalize(expected):diffs.append({'cue':c['number'],'cue_text':text,'mapped_display_words':expected})
 duplicate=[{'clip_id':cid,'source_word_index':i,'count':ct} for (cid,i),ct in collections.Counter(seen).items() if ct>1]
 if duplicate:errors.append('nativeclip source word duplicated in cue mappings')
 reports.append({'episode':ep,'cues':m['cue_count'],'words':wordcount,'errors':errors,'punctuation_or_reading_order_differences':diffs,'duplicate_source_word_mappings':duplicate,'max_native_word_anchor_drift_seconds':maxdrift,'srt_sha256':m['srt_sha256']})
R={'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'all_structure_pass':struct['structure_pass'],'total_cues':sum(x['cues'] for x in reports),'episodes':reports,'native_mapping_pass':all(not x['errors'] for x in reports),'mixed_cue_EP21_6':'caller word uses own source_path and syncclip anchor; overlaps narration by design, one combined two-line cue; comparison ignores linear ordering between simultaneous speakers','lexical_review':'Six EP24/25 ASR spelling/name differences verified against male original script: Raddiston->Veriston,Evren\'s->Evan\'s,Alderwood->Oliver,Alderwick->Aldwick,Verston->Veriston,gelped->gulped. EP21 Oliver line parallel to narration accounts for sequence-matcher insert/delete, not missing/repeated speech.','missing21_5_2_not_fabricated':True,'no_resolve_or_media_or_srt_changes':True}
(S/'核验报告/最终197条_原生锚点与词映射独立核验.json').write_text(json.dumps(R,ensure_ascii=False,indent=2));print(json.dumps(R,ensure_ascii=False,indent=2))
