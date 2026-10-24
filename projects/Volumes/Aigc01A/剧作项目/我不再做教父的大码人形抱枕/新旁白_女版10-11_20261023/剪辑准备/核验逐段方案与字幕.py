# -*- coding: utf-8 -*-
"""Read-only verification of the locked plan and SRT files. Writes a task-local QC report only."""
from pathlib import Path
import json,hashlib,re,math
R=Path(__file__).resolve().parent.parent;P=R/'剪辑准备/paragraph_conform_plan.json'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def normalized(t):return re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)?|\d+",t.lower().replace('’',"'"))
d=read(P);results=[]
for e in d['episodes']:
 ep=e['episode'];a=read(R/f'字幕/EP{ep}_新旁白正片_词码与原文.json');by={};cursor=0;oldend=0;prot=[];words_by_path={}
 assert a['plan_sha256']==sha(P)
 for ev in e['events']:
  assert ev['proposed_record_relative_frame']==cursor and ev['old_core_start_frame']==oldend
  cursor=ev['proposed_record_end_frame_exclusive'];oldend=ev['old_core_end_frame_exclusive']
  if ev['kind'] in ['character_dialogue','written_message']:
   head=ev['old_speech_start_seconds']-ev['old_core_start_seconds'];tail=ev['old_core_end_seconds_exclusive']-ev['old_speech_end_seconds']
   assert head>=.05-1e-7 and tail>=.05-1e-7,(ep,ev['paragraphs'],head,tail)
   assert ev['proposed_duration_frames']==ev['old_core_end_frame_exclusive']-ev['old_core_start_frame'] and ev['protected_video_source_audio']
   prot.append(dict(conform_event_id=ev['event_id'],source_paragraphs=ev['paragraphs'],old_source_word_start=ev['old_speech_start_seconds'],old_source_word_end=ev['old_speech_end_seconds'],old_protected_start=ev['old_core_start_seconds'],old_protected_end=ev['old_core_end_seconds_exclusive'],head_pad_ms=head*1000,tail_pad_ms=tail*1000,duration_frames=ev['proposed_duration_frames'],native_AV_speed_percent=100))
  else:
   for n in ev['new_narration']:
    assert n['source_start_seconds']<=n['speech_start_seconds'] and n['speech_end_seconds']<=n['source_end_seconds_exclusive']
    assert n['proposed_record_end_seconds_exclusive']<=cursor/24+1e-8
    assert sha(Path(n['source_path']))==n['source_sha256'] and sha(Path(n['word_timing_source']))==n['word_timing_sha256']
    by.setdefault(n['source_path'],[]).append(n)
 for src,ns in by.items():
  ns.sort(key=lambda x:x['source_start_seconds']);s=0;inds=[]
  for n in ns:
   assert abs(n['source_start_seconds']-s)<1e-8;s=n['source_end_seconds_exclusive'];inds.extend(range(n['first_source_word_index'],n['last_source_word_index_inclusive']+1))
   # Source24kHz partitions remain representable exactly in original decoded sample clock.
   assert abs(n['source_start_seconds']*n['source_original_sample_rate']-round(n['source_start_seconds']*n['source_original_sample_rate']))<1e-6
  f=next(f for f in e['new_source_files'] if f['path']==src);assert abs(s-f['duration_seconds'])<1e-8
  raw=read(ns[0]['word_timing_source']);assert inds==list(range(len(raw['words'])))
  words_by_path[src]=dict(source_sha256=f['sha256'],source_seconds=s,ASR_word_count=len(inds),covered_word_indices=inds,all_samples_once=True,adopted_take=f['adopted_take'])
 if ep==11:
  assert next(n for v in e['events'] for n in v['new_narration'] if n['paragraph']==345)['adopted_take']==2
  assert len([n for v in e['events'] for n in v['new_narration'] if n['paragraph']==348])==1
  assert set([343,344,345,346]).issubset({n['paragraph'] for v in e['events'] for n in v['new_narration']})
 assert a['new_narration_whitespace_words']=={10:185,11:188}[ep] and cursor==e['proposed_total_frames'] and oldend==e['program_core_end_frame']
 last=0
 for c in a['cues']:
  assert c['start_seconds']>=last-1e-8 and c['end_seconds']>c['start_seconds'];last=c['end_seconds'];assert len(c['lines'])<=3 and max(map(len,c['lines']))<=28
  for w in c['word_times']:assert c['start_seconds']<=w['record_start_seconds']+1e-8 and w['record_end_seconds']<=c['end_seconds']+1e-8
 srt=Path(a['srt_path']);assert sha(srt)==a['srt_sha256'];blocks=srt.read_text(encoding='utf-8-sig').strip().split('\n\n');assert len(blocks)==len(a['cues'])
 for i,(block,c) in enumerate(zip(blocks,a['cues']),1):
  lines=block.splitlines();assert int(lines[0])==i and lines[2:]==c['lines']
 assert normalized(' '.join(' '.join(b.splitlines()[2:]) for b in blocks))==normalized(' '.join(v['canonical_text'] for v in a['events']))
 results.append(dict(episode=ep,status='MACHINE_FILEPLAN_AND_SRT_PASS_NATIVE_IMPLEMENTATION_SEPARATE',new_source_full_seconds=e['new_narration_full_file_seconds'],new_narrative_paragraphs=sum(len(v['new_narration']) for v in e['events']),new_source_files=len(by),narration_original_whitespace_words=a['new_narration_whitespace_words'],protected_original_audio_events=len(prot),protected_boundaries=prot,minimum_protected_head_pad_ms=min(v['head_pad_ms'] for v in prot),minimum_protected_tail_pad_ms=min(v['tail_pad_ms'] for v in prot),all_source_samples_partitioned_once=True,all_ASR_source_word_indices_covered_once=True,source_files=words_by_path,planned_audio_protected_overlap_count=0,proposed_frames=cursor,proposed_seconds=cursor/24,srt_cues=len(a['cues']),srt_maxlines=a['max_lines'],srt_maxchars=a['max_line_characters'],srt_last_end=last,source_media_modified=False,native_Resolve_or_UI=False,human_listening_or_visual_audition=False))
q=R/f'剪辑准备/全保护边界与字幕_核验_{sha(P)[:12]}.json';q.write_text(json.dumps(dict(status='PASS_FILES_ONLY_ALL_PROTECTED_EDGES_AT_LEAST50MS',plan_path=str(P),plan_sha256=sha(P),episodes=results),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(report=str(q),plan_sha256=sha(P),summary=[dict(episode=v['episode'],frames=v['proposed_frames'],seconds=v['proposed_seconds'],minheadms=v['minimum_protected_head_pad_ms'],mintailms=v['minimum_protected_tail_pad_ms'],narrationwords=v['narration_original_whitespace_words']) for v in results]),ensure_ascii=False),flush=True)
