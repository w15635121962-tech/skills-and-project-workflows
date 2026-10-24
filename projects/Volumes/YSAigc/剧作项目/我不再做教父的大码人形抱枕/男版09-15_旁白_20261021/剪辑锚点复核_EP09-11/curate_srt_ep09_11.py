"""Canonical English paragraph/phrase captions. Only local SRT files, no Resolve."""
from pathlib import Path
import json,re,math,sys,hashlib,datetime,shutil
B=Path(__file__).resolve().parents[1];O=B/'字幕';sys.path.insert(0,str(B/'剪辑脚本准备'))
from subtitle_tools import wrap_original,write_srt,parse_srt
M=json.loads((B/'准备/narration_manifest.json').read_text())
OV={286:['Her voice was chilling,',"as if she feared I'd use ten years of history to cling to the Blackwoods."],294:['Even when Professor Warren asked about the Aldwick exchange,','I turned it down without a second thought.'],297:['Under the dim streetlights,','I texted Professor Warren to ask if a spot was still open.'],298:['She texted back fast, saying there was one,','promising to help me get it.'],300:['Friends drift, lovers leave,','and nobody should put their life on pause for someone else.'],303:['I started packing my clothes,','moving them from the closet into my suitcase.'],306:['Ever since that night at my place,','she had grown obsessed with my bed.'],321:['I saw it in the mirror while showering—scratches across my back and neck',"where she'd clawed into me."],328:['The tangled scratches stood out on my skin,','showing how wild that night was.'],330:["You always say you're fine, even when you're hurting.",'But your brow knits together every single time.',"Lie still. I'll go grab some ointment."],333:['Fifteen minutes later,','she walked back in with ointment from the pharmacy downstairs.'],339:['As if something came to mind,','she asked casually while rubbing the cream in.']}
# Preserve the provisional hard-four-second drafts made in this task; they were never imported.
old=O/'版本留痕/初版_4秒硬断_未导入';old.mkdir(parents=True,exist_ok=True)
for ep in [9,10,11]:
 p=O/f'EP{ep:02d}.srt'
 if p.exists() and not (old/p.name).exists():shutil.copy2(p,old/p.name)
if (O/'EP09-11_SRT清单与核验.json').exists() and not (old/'EP09-11_SRT清单与核验.json').exists():shutil.copy2(O/'EP09-11_SRT清单与核验.json',old/'EP09-11_SRT清单与核验.json')
def balanced_wrap(words):
    # Keep the minimum line count fitting the preset width, then balance those
    # lines without leaving an article/preposition or a one-word orphan tail.
    from itertools import combinations
    minimum=len(wrap_original(words));assert minimum<=3
    if minimum==1:return [' '.join(words)]
    options=[];function_words={'a','an','the','my','your','her','his','their','our','to','of','for','and','but','if','as','or','in','on','with','into','from','at','by'}
    for breaks in combinations(range(1,len(words)),minimum-1):
        pts=(0,)+breaks+(len(words),);lines=[' '.join(words[pts[i]:pts[i+1]]) for i in range(minimum)]
        if max(map(len,lines))>26:continue
        target=sum(map(len,lines))/minimum;score=sum((len(line)-target)**2 for line in lines)
        for i,line in enumerate(lines[:-1]):
            if words[pts[i+1]-1].lower().strip(',.;:!?') in function_words:score+=80
            if line.endswith((',', ';', ':')):score-=10
        if len(words[pts[-2]:])==1:score+=200
        options.append((score,lines))
    assert options;return min(options,key=lambda z:z[0])[1]
reports=[]
for ep in [9,10,11]:
 d=json.loads((B/f'EP{ep:02d}_原文词事件.json').read_text());x=d['episodes'][0];events=[];adj=[]
 for i,src in enumerate(x['events']):
  e=dict(src);off=e['start_frame']-math.floor(e['source_start_seconds']*24);e['start_frame']=round(e['source_start_seconds']*24)+off;e['end_frame']=max(e['start_frame']+1,round(e['source_end_seconds']*24)+off)
  assert abs(e['start_frame']-src['start_frame'])<=1 and abs(e['end_frame']-src['end_frame'])<=1
  if (e['start_frame'],e['end_frame'])!=(src['start_frame'],src['end_frame']):adj.append({'index':i,'word':e['word'],'before':[src['start_frame'],src['end_frame']],'caption_frames':[e['start_frame'],e['end_frame']]})
  events.append(e)
 source_ep=next(z for z in M['episodes'] if z['episode']==ep);groups=[];cursor=0
 for p in source_ep['original_paragraphs_and_retained_narration']:
  raw=p['raw_source_text'].strip().replace('"','');ww=raw.split();ee=events[cursor:cursor+len(ww)];cursor+=len(ww);assert [e['word'] for e in ee]==ww,(ep,p['docx_paragraph'])
  if p['docx_paragraph'] in OV:phrases=[s.split() for s in OV[p['docx_paragraph']]]
  else:
   phrases=[];current=[]
   for w in ww:
    current.append(w)
    if re.search(r'[.!?][\"”\']?$',w) and len(' '.join(current))>=12:phrases.append(current);current=[]
   if current:phrases.append(current)
  assert [w for v in phrases for w in v]==ww
  k=0
  for phrase in phrases:
   pe=ee[k:k+len(phrase)];k+=len(phrase);sub=[]
   for e in pe:
    if sub and e['source_kind']!=sub[-1]['source_kind']:groups.append({'paragraph':p['docx_paragraph'],'events':sub});sub=[]
    sub.append(e)
   if sub:groups.append({'paragraph':p['docx_paragraph'],'events':sub})
 assert cursor==len(events)
 cues=[];cueaudit=[]
 for i,g in enumerate(groups):
  ee=g['events'];st=ee[0]['start_frame'];en=ee[-1]['end_frame'];nxt=groups[i+1]['events'][0]['start_frame'] if i+1<len(groups) else x['duration_frames'];en=min(nxt,x['duration_frames'],en+4)
  assert st<en<=nxt
  lines=balanced_wrap([e['word'] for e in ee]);assert len(lines)<=3,(ep,g['paragraph'],lines)
  cues.append({'start_frame':st,'end_frame':en,'text':'\n'.join(lines)})
  cueaudit.append({'number':i+1,'docx_paragraph':g['paragraph'],'start_frame':st,'end_frame':en,'duration_frames':en-st,'source_kind':ee[0]['source_kind'],'token_count':len(ee),'text':'\n'.join(lines)})
 path=O/f'EP{ep:02d}.srt';write_srt(path,cues);parsed=parse_srt(path);assert parsed==[(z['start_frame'],z['end_frame'],z['text']) for z in cues]
 assert [e['word'] for e in events]==' '.join(z['text'].replace('\n',' ') for z in cues).split()
 for i,z in enumerate(cues):
  assert 0<=z['start_frame']<z['end_frame']<=x['duration_frames'];assert i==0 or z['start_frame']>=cues[i-1]['end_frame']
  ee=groups[i]['events'];assert len({e['source_kind'] for e in ee})==1
  nextrole=[e for e in events if e['start_frame']>=ee[-1]['end_frame'] and e['source_kind']!=ee[-1]['source_kind']]
  if nextrole:assert z['end_frame']<=nextrole[0]['start_frame']
 cap_path=O/f'EP{ep:02d}_字幕原文词事件_24fps量化.json';cap_path.write_text(json.dumps({'fps':24,'canonical_original_words_verified':True,'original_word_event_file':str(B/f'EP{ep:02d}_原文词事件.json'),'quantization':'Nearest same-source frame instant; original floor/ceil planning events and all AV data unchanged; max delta one frame.','episodes':[{'episode':ep,'duration_frames':x['duration_frames'],'events':events}],'quantization_adjustments':adj},ensure_ascii=False,indent=2))
 audit={'episode':ep,'srt':str(path),'cue_count':len(cues),'token_count':len(events),'first_token':events[0]['word'],'last_token':events[-1]['word'],'max_lines':max(len(z['text'].splitlines()) for z in cues),'max_line_characters':max(len(line) for z in cues for line in z['text'].splitlines()),'min_duration_frames':min(z['end_frame']-z['start_frame'] for z in cues),'max_duration_frames':max(z['end_frame']-z['start_frame'] for z in cues),'timeline_duration_frames':x['duration_frames'],'first_in_frame':cues[0]['start_frame'],'last_out_frame':cues[-1]['end_frame'],'clock':'24fps elapsed timeline time; timeline starts at 00:00:00:00','sequential_numbering':True,'monotonic_nonoverlapping_timecodes':True,'all_original_tokens_in_order':True,'mixed_vo_role_cue_count':0,'caption_does_not_cover_following_role_words':True,'quantization_max_delta_frames':1,'original_av_plan_and_events_unchanged':True,'phrase_break_method':'Original paragraph/sentence and reviewed clause boundaries; balanced lines <=26 chars, no orphan word tail, no forced four-second split.','srt_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'srt_bytes':path.stat().st_size,'cue_audit':cueaudit,'resolve_connected':False,'resolve_inserted':False,'preset_applied':False}
 (O/f'EP{ep:02d}_SRT逐条离线核验.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2));reports.append({k:v for k,v in audit.items() if k!='cue_audit'})
report={'created_at':datetime.datetime.now().isoformat(),'scope':'Male EP09-11 final locally authored SRTs; not inserted or preset-applied','fps':24,'max_lines_per_cue':3,'total_cues':sum(z['cue_count'] for z in reports),'total_original_tokens':sum(z['token_count'] for z in reports),'episodes':reports,'human_audition_and_Resolve_preview_verified':False}
(O/'EP09-11_SRT清单与核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
