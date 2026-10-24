import json,pathlib,datetime,re
B=pathlib.Path(__file__).resolve().parents[2]
D=json.loads((B/'Resolve_组装实读.json').read_text());A=json.loads((B/'ASR/转录索引.json').read_text());lookup={x['source_path']:x for x in A['files']}
canonical={
'男版21-3-1':[(0,2.08,"If there's nothing else, I'm heading out."),(6.28,6.72,'Wait.')],
'男版21-5-1':[(8,9.44,"Don't be mad anymore, okay?")],
'男版21-6-2':[(.5,1.58,'What do you want to wish for?'),(8.48,10.46,'Let me hold you one more time, please?')],
'男版21-7-1':[(9.78,11.66,'Vittoria, this wish expired a long time ago.')],
'男版22-1-1':[(6.5,7.9,'Oliver.')],
'男版22-2-2':[(0,6.2,'If I told you that even though I was drunk that night, I always knew it was you... would you believe me?')],
'男版22-3-1':[(.5,2.16,'None of that matters anymore, Vittoria.'),(6.14,10.64,"I know you need to focus on school. I can move to Aldwick. I can wait for you. Please don't leave me, okay?")],
'男版22-4-1':[(0,2.5,"That apartment next to mine in Old Town, it's yours, isn't it?"),(7.12,10.02,"I... I didn't mean anything by it. I just wanted to be near you.")],
'男版22-5-1':[(.7,3.78,'Vittoria, no one should spend their entire life waiting for someone else.'),(4.3,7.82,'See a doctor, fix your sleep schedule. You need to move on, too.')],
'男版23-2-1':[(2.48,3.92,"I'm only in it for the cash."),(4.16,5.6,"I don't feel anything for Vittoria.")],
'男版23-3-1':[(3.82,6.42,"As long as I pay, you'll sleep with me, won't you?")],
'男版23-5-1':[(3.78,4.84,'Boss, where do you want to go?'),(6.78,8.3,'Take me somewhere to sleep.')],
'男版23-6-1':[(4.16,5.44,'Take me to Oliver.')]
}
rows=[];empty=[];issues=[]
for e in D['episodes']:
 if e['episode'] not in [21,22,23]:continue
 for i,v in enumerate(e['video']):
  if v.get('gain_db')!=0:continue
  a=lookup.get(v['path']);stem=pathlib.Path(v['path']).stem
  if not a:issues.append({'episode':e['episode'],'clip_index':i,'error':'source missing from ASR index'});continue
  j=json.loads(pathlib.Path(a['json_path']).read_text());hits=[s for s in j['segments'] if s['start']<v['src1']-.001 and s['end']>v['src0']+.001]
  if not hits:empty.append({'episode':e['episode'],'clip_index':i,'native_clip_id':v['id'],'filename':pathlib.Path(v['path']).name,'source_range':[v['src0'],v['src1']],'record_range':[v['start']/24,v['end']/24],'result':'no speech segment; do not subtitle ASR hallucination or repeat preceding line'});continue
  for s in hits:
   c=[x for x in canonical.get(stem,[]) if abs(x[0]-s['start'])<.11 and abs(x[1]-s['end'])<.11]
   if not c:issues.append({'episode':e['episode'],'clip_index':i,'error':'unmatched canonical speech','raw':s['text']});continue
   shift=v['start']/24-v['source_start']/24
   wds=[{'asr_word':w['word'].strip(),'source_start_seconds':w['start'],'source_end_seconds':w['end'],'record_start_seconds':round(w['start']+shift,6),'record_end_seconds':round(w['end']+shift,6),'probability':w.get('probability')} for w in s.get('words',[])]
   row={'episode':e['episode'],'timeline':e['timeline'],'clip_index':i,'native_clip_id':v['id'],'source_path':v['path'],'source_clip_in_seconds':v['src0'],'source_clip_out_seconds':v['src1'],'record_clip_start_frame':v['start'],'record_clip_end_frame_exclusive':v['end'],'source_speech_start_seconds':s['start'],'source_speech_end_seconds':s['end'],'record_speech_start_seconds':round(s['start']+shift,6),'record_speech_end_seconds':round(s['end']+shift,6),'canonical_script_text':c[0][2],'raw_asr_text':s['text'].strip(),'canonical_name_normalizations_only':['Viteria -> Vittoria','Aldic -> Aldwick'],'canonical_punctuation_from_script':True,'words':wds,'all_word_ranges_inside_kept_clip':all(w['source_start_seconds']>=v['src0']-.03 and w['source_end_seconds']<=v['src1']+.03 for w in wds),'manual_audio_listening_performed':False,'verification_basis':'Native read clip/source windows + previous blind source ASR + exact original male script; not fresh human listening'}
   rows.append(row)
R={'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'scope':'EP21-23 actual native gain_db=0 source dialogue','source_native_read':str(B/'Resolve_组装实读.json'),'episodes':[21,22,23],'speech_segments':rows,'no_speech_gain0_clips':empty,'issues':issues,'missing_narration_do_not_add':'EP21 Did she want me back in Veriston? no21-5-2recording found; no subtitle added','no_dialogue_duplicates':len({(r['episode'],r['source_path'],r['source_speech_start_seconds'],r['source_speech_end_seconds']) for r in rows})==len(rows),'clip_words_not_truncated':all(r['all_word_ranges_inside_kept_clip'] for r in rows),'EP25_visual_fix_current_native_read':'25-4-1 source9.000–11.791667 atrecordframe437 confirmed; source2.4167–5.2083badgold range not used'}
(B/'字幕/EP21-23_同期对白核验.json').write_text(json.dumps(R,ensure_ascii=False,indent=2));print(json.dumps({'speech_segments':len(rows),'silent_gain0clips':len(empty),'issues':issues,'duplicates':not R['no_dialogue_duplicates'],'truncated':not R['clip_words_not_truncated']},ensure_ascii=False))
