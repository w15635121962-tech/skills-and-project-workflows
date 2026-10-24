"""Author native SRT only from reviewed canonical timeline words. Never connects Resolve."""
from pathlib import Path
import json,sys,math,hashlib,datetime,re
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'剪辑脚本准备'))
from subtitle_tools import cues_from_events,write_srt,parse_srt
O=B/'字幕';O.mkdir(exist_ok=True)
report=[]
for ep in [9,10,11]:
 src=B/f'EP{ep:02d}_原文词事件.json';d=json.loads(src.read_text());assert d['canonical_original_words_verified'] is True and d['fps']==24
 x=d['episodes'][0];events=[];adjusted=[]
 for idx,original in enumerate(x['events']):
  e=dict(original);offset=e['start_frame']-math.floor(e['source_start_seconds']*24)
  # Existing planning data conservatively floors starts and ceils ends. Shared
  # adjacent word boundaries then overlap one frame despite one source instant.
  # Caption events quantize that same actual source instant to nearest frame.
  e['start_frame']=round(e['source_start_seconds']*24)+offset
  e['end_frame']=max(e['start_frame']+1,round(e['source_end_seconds']*24)+offset)
  assert abs(e['start_frame']-original['start_frame'])<=1 and abs(e['end_frame']-original['end_frame'])<=1
  assert 0<=e['start_frame']<e['end_frame']<=x['duration_frames']
  if (e['start_frame'],e['end_frame'])!=(original['start_frame'],original['end_frame']):adjusted.append({'index':idx,'word':e['word'],'before':[original['start_frame'],original['end_frame']],'caption_frames':[e['start_frame'],e['end_frame']]})
  events.append(e)
 cues=cues_from_events(events,x['duration_frames']);path=O/f'EP{ep:02d}.srt';expected=[(c['start_frame'],c['end_frame'],c['text']) for c in cues]
 if path.exists():assert parse_srt(path)==expected,'Existing conflicting SRT preserved; resolve before any overwrite'
 else:write_srt(path,cues)
 parsed=parse_srt(path);assert parsed==expected
 original_tokens=[e['word'] for e in x['events']];caption_tokens=' '.join(c[2].replace('\n',' ') for c in parsed).split();assert original_tokens==caption_tokens
 # Every cue consumes a consecutive set of canonical words; never combines VO
 # and role dialogue, or holds one past the start of the next visible cue.
 cursor=0;cue_audit=[]
 for number,(st,en,txt) in enumerate(parsed,1):
  words=txt.replace('\n',' ').split();ee=events[cursor:cursor+len(words)];cursor+=len(words)
  assert [e['word'] for e in ee]==words and len({e['source_kind'] for e in ee})==1
  assert st==ee[0]['start_frame'] and en>=ee[-1]['end_frame']
  if number<len(parsed):assert en<=parsed[number][0]
  assert len(txt.splitlines())<=3 and max(map(len,txt.splitlines()))<=26
  # Caption hold is limited by the first true word of any following speaker.
  for following in events[cursor:]:
   if following['source_kind']!=ee[-1]['source_kind']:
    assert en<=following['start_frame'];break
  cue_audit.append({'number':number,'start_frame':st,'end_frame':en,'duration_frames':en-st,'source_kind':ee[0]['source_kind'],'token_count':len(words),'text':txt})
 assert cursor==len(events)
 cap_path=O/f'EP{ep:02d}_字幕原文词事件_24fps量化.json';cap_path.write_text(json.dumps({'fps':24,'canonical_original_words_verified':True,'original_word_event_file':str(src),'quantization':'Nearest source-frame instant; original plan conservative floor/ceil stays untouched. Max caption-event change one frame; no AV edits.','episodes':[{'episode':ep,'duration_frames':x['duration_frames'],'events':events}],'quantization_adjustments':adjusted},ensure_ascii=False,indent=2))
 audit={'episode':ep,'srt':str(path),'cue_count':len(parsed),'token_count':len(original_tokens),'first_token':original_tokens[0],'last_token':original_tokens[-1],'max_lines':max(len(c[2].splitlines()) for c in parsed),'max_line_characters':max(len(line) for c in parsed for line in c[2].splitlines()),'min_duration_frames':min(c[1]-c[0] for c in parsed),'max_duration_frames':max(c[1]-c[0] for c in parsed),'timeline_duration_frames':x['duration_frames'],'first_in_frame':parsed[0][0],'last_out_frame':parsed[-1][1],'source_clock':'Relative elapsed timeline time; starts at 00:00:00:00, 24fps','sequential_numbering':True,'monotonic_nonoverlapping_timecodes':True,'all_original_tokens_in_order':True,'mixed_vo_role_cue_count':0,'caption_does_not_cover_following_role_words':True,'nearest_frame_quantization_max_delta_frames':1,'quantized_event_change_count':len(adjusted),'original_plan_and_events_unchanged':True,'cue_audit':cue_audit,'srt_bytes':path.stat().st_size,'srt_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'resolve_connected':False,'resolve_inserted':False,'preset_applied':False}
 (O/f'EP{ep:02d}_SRT逐条离线核验.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2));report.append({k:v for k,v in audit.items() if k!='cue_audit'})
manifest={'created_at':datetime.datetime.now().isoformat(),'scope':'Male EP09-11 offline SRT authoring and structural verification only','fps':24,'max_lines_per_cue':3,'total_cues':sum(x['cue_count'] for x in report),'total_original_tokens':sum(x['token_count'] for x in report),'episodes':report,'resolve_connected':False,'preset_applied':False,'human_playback_or_visual_preset_validation':False}
(O/'EP09-11_SRT清单与核验.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print(json.dumps(manifest,ensure_ascii=False,indent=2))
