# -*- coding: utf-8 -*-
"""Map verified new narration words and protected old actor words to proposed conform time.
No ASR/model calls, UI, Resolve or source mutations.
"""
from pathlib import Path
import json,re,hashlib,math,datetime
ROOT=Path(__file__).resolve().parent.parent;PROJECT=ROOT.parent;OUT=ROOT/'剪辑准备';SUB=ROOT/'字幕';SUB.mkdir(exist_ok=True)
RX=re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)?|\d+")
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def norm(t):
 a={'mateo':'matteo',"mateo's":"matteo's",'bolandi':'bellandi','balandi':'bellandi','belandi':'bellandi'}
 return [a.get(m.group().lower().replace('’',"'"),m.group().lower().replace('’',"'")) for m in RX.finditer(t)]
def wrap(t,width=28):
 words=t.split()
 if len(t)<=width:return [t]
 candidates=[]
 for i in range(1,len(words)):
  ls=[' '.join(words[:i]),' '.join(words[i:])]
  if max(map(len,ls))<=width:candidates.append((sum((len(l)-len(t)/2)**2 for l in ls),ls))
 if candidates:return min(candidates,key=lambda x:x[0])[1]
 for i in range(1,len(words)-1):
  for j in range(i+1,len(words)):
   ls=[' '.join(words[:i]),' '.join(words[i:j]),' '.join(words[j:])]
   if max(map(len,ls))<=width:candidates.append((sum((len(l)-len(t)/3)**2 for l in ls)+sum(50 for l in ls if len(l.split())==1),ls))
 assert candidates,(t,'cannot fit3lines28chars')
 return min(candidates,key=lambda x:x[0])[1]
def tc(t):
 n=round(t*1000);h,n=divmod(n,3600000);m,n=divmod(n,60000);s,ms=divmod(n,1000);return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'
# Meaningful thought/breath groups, preserving all original words and punctuation.
CHUNKS={
 310:['She told me to pack everything','and never show my face around Matteo again.'],
 312:['Her tone was cold,',"as if she were afraid I'd use my ten years with Matteo",'as an excuse to cling to the Bellandi family.'],
 317:['After leaving the estate,',"for the first time, I didn't know where to go."],
 318:['For years, Matteo had come before','every plan I made for my own life.'],
 319:['My professor once recommended me','for a visiting medical research program in New York.'],
 320:['I turned it down without a second thought',"because I couldn't leave him."],
 327:['I finally realized:','no one should wait in place forever for someone else.'],
 331:['I started preparing my application materials','while packing up my things.'],
 332:['On the second night,','Matteo came to my apartment as usual.'],
 333:['He opened the closet','and immediately noticed two of my pajama tops were missing.'],
 337:['Once we were in bed,','he instinctively wrapped an arm around my waist.'],
 339:['The finger-shaped bruises from that night','still marked the soft skin around my waist.'],
 348:['He bought ointment downstairs,','gently working it into my bruises with his own hands.'],
 350:['His belated concern still made my eyes sting,','but I no longer dared mistake habit for love.'],
 355:["Before I could tell him I wasn't renewing,",'Alessia called.'],
 361:["He didn't even cap the ointment",'before pulling on his coat.']}
planP=OUT/'paragraph_conform_plan.json';plan=read(planP);results=[]
for eplan in plan['episodes']:
 ep=eplan['episode'];assert eplan['status']=='FILE_PLAN_COMPLETE_READY_FOR_ROOT_CONFORM';oldP=Path(eplan['old_alignment_file']);old=read(oldP);oldBy={e['event_id']:e for e in old['events']};canP=PROJECT/f'字幕_女版10-11_20261023/原文/episode{ep}_canonical.json';can=read(canP);events=[];cues=[];source_indices={};protected_ids=[]
 def emit(typed,parts):
  events.append(typed)
  assert ' '.join(' '.join(w['text'] for w in part) for part in parts)==' '.join(typed['canonical_text'].split())
  for part in parts:
   text=' '.join(w['text'] for w in part);lines=wrap(text)
   cues.append(dict(event_id=typed['event_id'],conform_event_id=typed['conform_event_id'],kind=typed['kind'],speaker=typed['speaker'],source_paragraphs=typed['source_paragraphs'],text=text,lines=lines,start_seconds=part[0]['record_start_seconds'],speech_end_seconds=part[-1]['record_end_seconds'],word_times=part))
 for e in eplan['events']:
  if e['new_narration']:
   for n in e['new_narration']:
    a=read(n['word_timing_source']);lo=n['first_source_word_index'];hi=n['last_source_word_index_inclusive']+1;ws=a['words'][lo:hi];text=n['canonical_text'];obs=[]
    for j,w in enumerate(ws,lo):
     for tok in norm(w['word']):obs.append(dict(token=tok,source_word_index=j,source_start_seconds=w['start'],source_end_seconds=w['end']))
    exp=[(norm(m.group())[0],m.start(),m.end()) for m in RX.finditer(text)];assert [x[0] for x in exp]==[o['token'] for o in obs]
    timed=[]
    for m in re.finditer(r'\S+',text):
     ids=[j for j,v in enumerate(exp) if v[1]>=m.start() and v[2]<=m.end()];assert ids
     st=min(obs[j]['source_start_seconds'] for j in ids);en=max(obs[j]['source_end_seconds'] for j in ids)
     timed.append(dict(text=m.group(),source_word_indices=sorted(set(obs[j]['source_word_index'] for j in ids)),source_start_seconds=st,source_end_seconds=en,record_start_seconds=n['proposed_record_start_seconds']+st-n['source_start_seconds'],record_end_seconds=n['proposed_record_start_seconds']+en-n['source_start_seconds']))
    source_indices.setdefault(n['source_path'],[]).extend(range(lo,hi));pn=n['paragraph'];typed=dict(event_id=f'EP{ep}-N-P{pn}',conform_event_id=e['event_id'],kind='new_narration',speaker='Eliza (narrator)',source_paragraphs=[pn],canonical_text=text,source_path=n['source_path'],source_sha256=n['source_sha256'],adopted_take=n['adopted_take'],source_clip_start_seconds=n['source_start_seconds'],source_clip_end_seconds=n['source_end_seconds_exclusive'],record_clip_start_seconds=n['proposed_record_start_seconds'],record_clip_end_seconds=n['proposed_record_end_seconds_exclusive'],word_timing_source=n['word_timing_source'],word_timing_sha256=n['word_timing_sha256'],speed_percent=100,words=timed)
    forced=CHUNKS.get(pn)
    if forced:
     assert ' '.join(forced)==' '.join(text.split()),(pn,forced,text);parts=[];cursor=0
     for chunk in forced:
      count=len(chunk.split());parts.append(timed[cursor:cursor+count]);cursor+=count
     assert cursor==len(timed)
    else:
     wrap(text);parts=[timed]
    emit(typed,parts)
  else:
   assert e['kind'] in ['character_dialogue','written_message'];assert len(e['old_event_ids'])==1
   oldid=e['old_event_ids'][0];o=oldBy[oldid];shift=e['proposed_record_start_seconds']-e['old_core_start_seconds'];timed=[dict(text=w['text'],source_start_seconds=w['start'],source_end_seconds=w['end'],record_start_seconds=w['start']+shift,record_end_seconds=w['end']+shift) for w in o['source_word_times']];speakers=list(dict.fromkeys(s['speaker'] for s in can['segments'] if [s['source_docx_paragraph'],s['kind']] in o['source_paragraph_kinds']));protected_ids.append(oldid)
   typed=dict(event_id=f'EP{ep}-PROTECTED-{oldid}',conform_event_id=e['event_id'],kind=e['kind'],speaker=' / '.join(speakers),source_paragraphs=e['paragraphs'],canonical_text=o['canonical_or_approved_actual_text'],source_path='ORIGINAL_NATIVE_VIDEO_AUDIO_IN_CORE',original_native_video_audio=e['protected_video_source_audio'],old_actual_mix_clock_start_seconds=e['old_core_start_seconds'],record_clip_start_seconds=e['proposed_record_start_seconds'],record_clip_end_seconds=e['proposed_record_end_frame_exclusive']/24,word_timing_source=str(oldP),word_timing_sha256=sha(oldP),original_actual_mix_shift_seconds=shift,speed_percent=100,words=timed,prior_approved_phonetic_corrections_preserved=True)
   oldCues=[c for c in old['cues'] if c['event_id']==oldid];parts=[];cursor=0
   for c in oldCues:
    cnt=len(c['word_times']);part=timed[cursor:cursor+cnt];assert ' '.join(w['text'] for w in part)==c['text'];parts.append(part);cursor+=cnt
   assert cursor==len(timed);emit(typed,parts)
 for i,c in enumerate(cues):
  nxt=cues[i+1]['start_seconds'] if i+1<len(cues) else eplan['proposed_total_seconds'];end=min(max(c['speech_end_seconds']+.08,c['start_seconds']+.65),nxt-.001)
  c['end_seconds']=max(c['speech_end_seconds'],end)
  if i+1<len(cues) and c['end_seconds']>nxt:c['end_seconds']=nxt
  c['cue_number']=i+1;assert c['end_seconds']>c['start_seconds'] and len(c['lines'])<=3 and max(map(len,c['lines']))<=28
  assert c['start_seconds']>=0 and c['end_seconds']<=eplan['proposed_total_seconds']+1e-6
  for w in c['word_times']:assert c['start_seconds']<=w['record_start_seconds']+1e-7 and w['record_end_seconds']<=c['end_seconds']+1e-7
 for path,inds in source_indices.items():
  item=next(f for f in eplan['new_source_files'] if f['path']==path);ar=next(n for e in eplan['events'] for n in e['new_narration'] if n['source_path']==path);aw=read(ar['word_timing_source'])['words'];assert inds==list(range(len(aw))),('Missing/duplicatednewVOwords',path,inds)
 file=SUB/f'EP{ep}_新旁白正片_相对0.srt';file.write_text('\n\n'.join(f'{i}\n{tc(c["start_seconds"])} --> {tc(c["end_seconds"])}\n'+'\n'.join(c['lines']) for i,c in enumerate(cues,1))+'\n',encoding='utf-8-sig')
 # Verify full narrative source text exactly once; actor and source messages remain originalapproved words.
 narrtext=' '.join(t['canonical_text'] for t in events if t['kind']=='new_narration');mg=read(ROOT/'准备/manifest.json');canonNarr=' '.join(g['generation_text'].strip() for g in mg['groups'] if g['episode']==ep);assert norm(narrtext)==norm(canonNarr)
 report=dict(episode=ep,status='PROPOSED_CONFORM_SRT_MACHINE_VALIDATED_PENDING_NATIVE_IMPLEMENTATION',plan_file=str(planP),plan_sha256=sha(planP),original_timeline_id=eplan['original_timeline_id'],fps=24,timeline_start_frame=86400,srt_clock='Relative0, nativeimport offsets to timeline startonce; do notuse01hSRTwithnativeAppend.',srt_path=str(file),srt_sha256=sha(file),cue_count=len(cues),max_lines=max(len(c['lines']) for c in cues),max_line_characters=max(len(l) for c in cues for l in c['lines']),first_cue_seconds=cues[0]['start_seconds'],last_cue_end_seconds=cues[-1]['end_seconds'],proposed_program_duration_seconds=eplan['proposed_total_seconds'],new_narration_whitespace_words=len(narrtext.split()),new_narration_source_word_count=sum(len(v) for v in source_indices.values()),new_narration_word_index_missing=0,new_narration_word_index_repeated=0,new_narration_count_once_per_original_paragraph=True,protected_original_event_ids=protected_ids,source_name_punctuation_policy='Canonical originalfemale words; acceptedpropernames/spelling per completedblindASR QC. Existingprotectedwincing canonical choice copiedfromRootapprovedsource; nooldnarrativeextra to carriedinto newP350.',original_timeline_or_source_modified=False,human_listening_performed=False,normal_speed_visual_audition=False,Resolve_or_UI=False,events=events,cues=cues)
 ap=SUB/f'EP{ep}_新旁白正片_词码与原文.json';ap.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');results.append(dict(episode=ep,srt_path=str(file),srt_sha256=sha(file),word_map_path=str(ap),word_map_sha256=sha(ap),cue_count=len(cues),narration_words=report['new_narration_whitespace_words'],last_cue_seconds=report['last_cue_end_seconds'],proposed_program_duration_seconds=eplan['proposed_total_seconds']))
summary=dict(status='BOTH_EPISODE_CONFORM_AND_SRT_FILES_READY_FOR_ROOT_IMPLEMENTATION',created_at=datetime.datetime.now().astimezone().isoformat(),conform_plan=str(planP),conform_plan_sha256=sha(planP),adopted_audio_manifest=str(ROOT/'最终采用清单.json'),adopted_audio_manifest_sha256=sha(ROOT/'最终采用清单.json'),files=results,native_edit_or_import_done=False,notes='Do not equate this fileplan/SRT mapping with actualconformednativeplayback. Rootimplements oldcore fillgaps, excludesChineseeditorialnotes, retainsprotectedvoices1:1 and confirms result beforefinalsubtitlesimport.')
sp=OUT/'逐段对应与字幕_交付清单.json';sp.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,ensure_ascii=False),flush=True)
