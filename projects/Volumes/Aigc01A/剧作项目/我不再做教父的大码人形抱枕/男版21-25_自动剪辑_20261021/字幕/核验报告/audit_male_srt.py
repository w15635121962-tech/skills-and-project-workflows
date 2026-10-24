import json,pathlib,re,datetime,difflib,hashlib
B=pathlib.Path(__file__).resolve().parents[2];S=B/'字幕';N=json.loads((B/'Resolve_组装实读.json').read_text());I=json.loads((B/'ASR/转录索引.json').read_text());by={x['source_path']:x for x in I['files']};actual_dialogue=json.loads((S/'EP21-23_同期对白核验.json').read_text())
def time_ms(s):
 h,m,sec,ms=map(int,re.match(r'^(\d{2}):(\d{2}):(\d{2}),(\d{3})$',s).groups());return ((h*60+m)*60+sec)*1000+ms
aliases={'viteria':'vittoria','vitoria':'vittoria','vatoria':'vittoria','victoria':'vittoria','aldic':'aldwick','aldik':'aldwick','ember':'amber','13':'thirteen','17':'seventeen','10':'ten','2':'two','3':'three','5':'five','12':'twelve','1':'one','4':'four','7':'seven','twentyone':'twenty one'}
def words(t):
 t=t.lower().replace('’',"'").replace('‘',"'").replace('—',' ').replace('–',' ').replace('-',' ')
 return [aliases.get(x,x) for x in re.findall(r"[a-z0-9]+(?:'[a-z]+)?",t)]
reports=[]
for e in N['episodes']:
 ep=e['episode'];p=S/f'EP{ep}.srt';r={'episode':ep,'path':str(p),'exists':p.exists(),'duration_frames':e['duration_frames'],'fps':e['fps'],'errors':[],'warnings':[]}
 if not p.exists():reports.append(r);continue
 content=p.read_text(encoding='utf-8-sig');r['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();blocks=re.split(r'\r?\n\s*\r?\n',content.strip());cues=[]
 for expected_index,b in enumerate(blocks,1):
  ls=b.splitlines()
  try:
   index=int(ls[0]);times=re.match(r'^(\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2},\d{3})\s*$',ls[1]);start=time_ms(times[1]);end=time_ms(times[2]);lines=ls[2:]
  except Exception as ex:r['errors'].append({'block':expected_index,'type':'invalid_srt_block','message':str(ex)});continue
  cue={'index':index,'start_ms':start,'end_ms':end,'lines':lines,'text':' '.join(lines)};cues.append(cue)
  if index!=expected_index:r['errors'].append({'cue':index,'type':'numbering','expected':expected_index})
  if not 0<=start<end:r['errors'].append({'cue':index,'type':'invalid_time_range'})
  if len(lines)>3:r['errors'].append({'cue':index,'type':'more_than_three_lines','count':len(lines)})
  if not lines or any(not line.strip() for line in lines):r['errors'].append({'cue':index,'type':'empty_text_line'})
  if end>round(e['duration_frames']/e['fps']*1000)+1:r['errors'].append({'cue':index,'type':'out_of_timeline_bounds','end_ms':end})
  for label,tm in [('start',start),('end',end)]:
   delta=abs(tm-round(tm*e['fps']/1000)*1000/e['fps'])
   if delta>.501:r['errors'].append({'cue':index,'type':'not_24fps_quantized','edge':label,'delta_ms':delta})
  if len(cues)>1 and start<cues[-2]['end_ms']:r['errors'].append({'cue':index,'type':'overlap_or_backward','previous_end_ms':cues[-2]['end_ms'],'start_ms':start})
 body=' '.join(c['text'] for c in cues);norm=' '.join(words(body));r['cue_count']=len(cues);r['subtitle_token_count']=len(words(body));r['first_start_ms']=cues[0]['start_ms'] if cues else None;r['last_end_ms']=cues[-1]['end_ms'] if cues else None;r['max_lines']=max((len(c['lines']) for c in cues),default=0);r['relative_timecode_basis']=bool(cues and 0<=cues[0]['start_ms']<60000 and cues[-1]['end_ms']<=e['duration_frames']/e['fps']*1000+1)
 if ep==21 and 'did she want me back in veriston' in norm:r['errors'].append({'type':'added_unrecorded_missing21_5_2_sentence'})
 for forbidden in ["i'm sorry",'going to go to the next episode','lot of water','hello hello']:
  if forbidden in norm:r['errors'].append({'type':'known_quiet_source_asr_hallucination_in_subtitle','text':forbidden})
 expected=[]
 for a in e['narration']:
  source=by[a['path']];j=json.loads(pathlib.Path(source['json_path']).read_text());ws=[w for seg in j['segments'] for w in seg.get('words',[]) if a['src0']-.015 <= (w['start']+w['end'])/2 < a['src1']+.015]
  for w in ws:expected.append((a['record']+w['start']-a['src0'],w['word'],a['path']))
 if ep<=23:
  for x in actual_dialogue['speech_segments']:
   if x['episode']!=ep:continue
   for w in x['words']:expected.append((w['record_start_seconds'],w['asr_word'],x['source_path']))
 else:
  for v in e['video']:
   if v['gain_db']!=0:continue
   source=by.get(v['path']);
   if not source:continue
   j=json.loads(pathlib.Path(source['json_path']).read_text());ws=[w for seg in j['segments'] for w in seg.get('words',[]) if v['src0']-.015 <= (w['start']+w['end'])/2 < v['src1']+.015]
   for w in ws:expected.append((v['record']+w['start']-v['src0'],w['word'],v['path']))
 # Explicitly reviewed quiet-source sleep murmur, confirmed by three unprompted local crop ASR passes.
 if ep==21:
  for v in e['video']:
   if pathlib.Path(v['path']).name=='男版21-2-1.mp4' and v['src0']<=2.2 and v['src1']>=3.6:
    expected.append((v['record']+2.2-v['src0'],'Oliver.',v['path']))
 expected.sort(key=lambda x:x[0]);source_tokens=words(' '.join(x[1] for x in expected));caption_tokens=words(body);sm=difflib.SequenceMatcher(None,source_tokens,caption_tokens,autojunk=False);diff=[]
 for tag,a0,a1,b0,b1 in sm.get_opcodes():
  if tag=='equal':continue
  diff.append({'op':tag,'source_words':' '.join(source_tokens[a0:a1]),'srt_words':' '.join(caption_tokens[b0:b1]),'source_context':' '.join(source_tokens[max(0,a0-5):min(len(source_tokens),a1+5)]),'srt_context':' '.join(caption_tokens[max(0,b0-5):min(len(caption_tokens),b1+5)])})
 r['source_asr_token_count']=len(source_tokens);r['source_srt_sequence_match_ratio']=round(sm.ratio(),6);r['lexical_differences_require_review']=diff
 reports.append(r)
report={'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'scope':'male EP21-25 actual assembled native timeline SRT only; no source/SRT/Resolve modifications','native_manifest':str(B/'Resolve_组装实读.json'),'structure_check':['sequential indices','strictly increasing positive intervals','no overlaps','relative zero-origin timecodes','24fps to nearest integer-millisecond rounding','within actual timeline length','max3lines'],'lexical_check_basis':'Native actual retained narration + gain0 synchronized dialogue windows against existing blind ASR; lexical differences may be original-script spelling correction or speech-vs-script variants and require human reasoning, not automatic failure.','episodes':reports,'all_present':all(r['exists'] for r in reports),'structure_pass':all(r['exists'] and not r['errors'] for r in reports),'total_cues':sum(r.get('cue_count',0) for r in reports)}
(S/'核验报告/SRT五集_独立结构与词覆盖核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({'all_present':report['all_present'],'structure_pass':report['structure_pass'],'episodes':[{'ep':r['episode'],'cues':r.get('cue_count'),'errors':r['errors'],'lexical_differences':r.get('lexical_differences_require_review')} for r in reports]},ensure_ascii=False,indent=2))
