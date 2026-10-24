# -*- coding: utf-8 -*-
"""File-only conform planning. Does not connect to Resolve or alter edits/media."""
from pathlib import Path
import json,hashlib,re,math,datetime,xml.etree.ElementTree as E
from fractions import Fraction
R=Path(__file__).resolve().parent.parent;P=R.parent;OUT=R/'剪辑准备'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
RX=re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)?|\d+")
def norm(t):
 aliases={'mateo':'matteo',"mateo's":"matteo's",'bolandi':'bellandi','balandi':'bellandi','belandi':'bellandi'}
 return [aliases.get(x.group().lower().replace('’',"'"),x.group().lower().replace('’',"'")) for x in RX.finditer(t)]
def dur(d):return d['pcm_measurements']['decoded_duration_seconds']
manifestp=R/'准备/manifest.json';manifest=read(manifestp);adoptp=R/'最终采用清单.json';adopt=read(adoptp);snapP=P/'字幕_女版10-11_20261023/操作前实时实读.json';snap=read(snapP)
paragraphs={}
for ep in manifest['episodes']:
 for p in ep['original_paragraphs_and_retained_narration']:
  if p['narration_retained_text'].strip():paragraphs[(ep['episode'],p['docx_paragraph'])]=p['narration_retained_text'].strip()

def new_paragraphs(ep):
 results={};pending=[];sourcefiles=[]
 for g in manifest['groups']:
  if g['episode']!=ep:continue
  chosen=next(f for f in adopt['files'] if f['episode']==ep and f['narration_sequence']==g['narration_sequence'])
  ap=Path(chosen['word_timing_json'])
  if not ap.is_file():pending.append(str(ap));continue
  a=read(ap);archive=Path(a['source_path']);path=Path(chosen['delivery_path']);assert path.is_file() and archive.is_file() and sha(path)==sha(archive)==a['source_sha256']==chosen['sha256'];assert a['blind_transcription'] is True and a['initial_prompt'] is None
  assert chosen['ordinary_word_qc_pass'] is True and chosen['speed_percent']==100
  if ep==11 and g['narration_sequence']==4:assert chosen['take']==2 and a['source_sha256']=='d90515b5ab644edbfc49555a5893420c1637a9f029fcb83b6f94e91f46efd207'
  ws=a['words'];obs=[u for w in ws for u in norm(w['word'])];exp=[u for pn in g['source_docx_paragraphs'] for u in norm(paragraphs[(ep,pn)])]
  assert exp==obs,(g['basename'],exp,obs)
  starts=[];cursor=0
  for pn in g['source_docx_paragraphs']:
   n=len(norm(paragraphs[(ep,pn)]));first=cursor;last=cursor+n-1
   # All selected verified files currently have one normalized unit per ASR word.
   assert all(len(norm(w['word']))==1 for w in ws)
   starts.append((pn,first,last));cursor+=n
  assert cursor==len(ws)
  cuts=[0.0]+[(ws[starts[i-1][2]]['end']+ws[starts[i][1]]['start'])/2 for i in range(1,len(starts))]+[dur(a)]
  for i,(pn,first,last) in enumerate(starts):
   st=ws[first]['start'];en=ws[last]['end'];c0=cuts[i];c1=cuts[i+1];assert c0<=st and en<=c1
   results[pn]=dict(paragraph=pn,canonical_text=paragraphs[(ep,pn)],source_path=str(path),archive_source_path=str(archive),adopted_take=chosen['take'],source_sha256=a['source_sha256'],word_timing_source=str(ap),word_timing_sha256=sha(ap),first_source_word_index=first,last_source_word_index_inclusive=last,first_source_word=ws[first]['word'],last_source_word=ws[last]['word'],speech_start_seconds=st,speech_end_seconds=en,source_start_seconds=c0,source_end_seconds_exclusive=c1,source_duration_seconds=c1-c0,speed_percent=100.0,clock='actual MP3 decoded source seconds, no timeline-frame conversion assumed',partition_policy='Keep whole new MP3 samples, partition only in natural paragraph pauses; every selected source sample appears exactly once.',safe_word_pad_trim_option_seconds=[max(c0,st-.08),min(c1,en+.08)],safe_word_pad_option_applied=False,source_original_sample_rate=a['probe']['audio']['sample_rate'],source_lufs=a['source_integrated_lufs'],source_true_peak_dbtp=a['source_true_peak_dbtp'],gain_recommendation_db=round(min(0.0,-18-a['source_integrated_lufs'],-2-a['source_true_peak_dbtp']),2),gain_recommendation_applied=False)
  sourcefiles.append(dict(path=str(path),archive_source_path=str(archive),adopted_take=chosen['take'],sha256=a['source_sha256'],duration_seconds=dur(a),paragraphs=g['source_docx_paragraphs'],all_samples_partitioned_once=True))
 return results,pending,sourcefiles

def native_support(t,st,en,kind):
 out=[]
 for typ in ['video','audio']:
  for tr in t['tracks'][typ]:
   if not tr.get('enabled',True):continue
   for i,c in enumerate(tr['items']):
    if not c.get('enabled',True):continue
    a=(c['start']-t['start'])/t['fps'];b=(c['end']-t['start'])/t['fps']
    if a < en-1e-8 and b > st+1e-8:
     out.append(dict(type=typ,track_index=tr['index'],track_name=tr['name'],item_index=i,name=c['name'],path=c.get('path'),old_relative_start_seconds=a,old_relative_end_seconds=b,source_left_offset_frames=c.get('left'),source_right_offset_frames=c.get('right'),native_properties_retained=True,source_clock_note='Do not linearize source offsets across existing native retimes; preserve native segment/timeMap and original J/L audio structure.'))
 return out

def existing_visual_issues(ep,t):
 xmlp=OUT/f'原时间线_EP{ep}.fcpxml/Info.fcpxml';x=E.parse(xmlp);titles=[dict(name=c['name'],track=tr['index'],start=(c['start']-t['start'])/24,end=(c['end']-t['start'])/24) for tr in t['tracks']['video'] for c in tr['items'] if c['name']=='Text+'];gaps=[]
 for c in x.find('.//project/sequence/spine'):
  if c.tag=='gap':
   st=float(Fraction(c.attrib['offset'][:-1]))-3600;en=st+float(Fraction(c.attrib['duration'][:-1]));gaps.append([st,en])
 return dict(source_public_xml=str(xmlp),source_public_xml_sha256=sha(xmlp),native_visual_textplus_items=titles,public_xml_exported_title_count=len(x.findall('.//title')),public_xml_effect_resource_count=len(x.findall('.//resources/effect')),public_xml_spine_gaps=gaps,warning='Root read native Text+ content and confirmed allsix are Chinese editorialnotes, not intended picture/effects. Deliberately exclude notes from NEWcut; original timeline untouched. PublicXML omission ofthese notes is correct. Real primarytrackgaps need same-scene verifiedexistingfootage/reaction coverage, no blackgap or Chinese productiontext.',native_textplus_content_evidence=str(OUT/'原TextPlus内容.json'),editorial_notes_excluded_from_new_cut=True)

def plan(ep):
 t=next(t for t in snap['timelines'] if t['name']==f'大码_女版_EP{ep}')
 oldp=P/f'字幕_女版10-11_20261023/对齐/EP{ep}_候选词码与原文.json';old=read(oldp);new,pending,files=new_paragraphs(ep);core_end={10:1882,11:2377}[ep]/24
 events=[]
 for o in old['events']:
  spec=o['source_paragraph_kinds'];events.append(dict(old_event_ids=[o['event_id']],paragraphs=[v[0] for v in spec],kind=spec[0][1],canonical_text=o['canonical_or_approved_actual_text'],old_speech_start_seconds=o['start_seconds'],old_speech_end_seconds=o['end_seconds']))
 if ep==11:
  # First mistaken VO348/349 is replaced by canonical missing343-346, preserving protected347 below.
  i=next(i for i,e in enumerate(events) if e['old_event_ids']==['EP11-E14'])
  e=events[i];f=events[i+1];events[i:i+2]=[dict(old_event_ids=e['old_event_ids']+f['old_event_ids'],paragraphs=[343,344,345,346],kind='narration_missing_replacing_wrong_repeat',canonical_text=' '.join(paragraphs[(ep,p)] for p in [343,344,345,346]),old_speech_start_seconds=e['old_speech_start_seconds'],old_speech_end_seconds=f['old_speech_end_seconds'],correction='Remove only the first erroneous348/349 old VO occurrence. Insert source343–346 narration here; later348/349 remains once. No new visual action invented; existing11-04 picture requires visual confirmation for these four actions.')]
 boundaries=[0]+[round((events[i-1]['old_speech_end_seconds']+events[i]['old_speech_start_seconds'])/2*24)/24 for i in range(1,len(events))]+[core_end]
 # Actor/message edge quantization always points OUTWARD with at least50ms margin; replacing old narration never justifies shaving an actor word tail.
 for bi in range(1,len(boundaries)-1):
  prev=events[bi-1];cur=events[bi];v=boundaries[bi]
  if prev['kind'] in ['character_dialogue','written_message']:v=max(v,math.ceil((prev['old_speech_end_seconds']+.05)*24-1e-8)/24)
  if cur['kind'] in ['character_dialogue','written_message']:v=min(v,math.floor((cur['old_speech_start_seconds']-.05)*24+1e-8)/24)
  assert v>boundaries[bi-1]
  boundaries[bi]=v
 record=0;timepoints=[dict(output_relative_frame=0,old_core_relative_seconds=0.0)];limitations=[]
 for i,e in enumerate(events):
  st=boundaries[i];en=boundaries[i+1];e.update(event_id=f'EP{ep}-C{i+1:02d}',old_core_start_seconds=st,old_core_end_seconds_exclusive=en,old_core_start_frame=round(st*24),old_core_end_frame_exclusive=round(en*24),old_native_timecode_start_seconds=3600+st,old_native_timecode_end_seconds=3600+en,old_slot_duration_seconds=en-st,original_native_support=native_support(t,st,en,e['kind']))
  if e['kind'] in ['character_dialogue','written_message']:
   e.update(action='PRESERVE_ORIGINAL_NATIVE_AV_1_TO_1',audio_speed_percent=100.0,picture_time_mapping='identity within protected old-native interval; shift as a unit only',proposed_duration_frames=round((en-st)*24),new_narration=[],sync_preservation_required=True)
   # Native actor/message audio is sourced from original video, not the new TTS.
   e['protected_video_source_audio']=[s for s in e['original_native_support'] if s['type']=='audio' and s.get('path') and Path(s['path']).suffix.lower() in ['.mp4','.mov']]
  else:
   n=[new[p] for p in e['paragraphs'] if p in new];missing=[p for p in e['paragraphs'] if p not in new]
   e.update(action='REPLACE_OLD_NARRATION_WITH_NEW_100_PERCENT',new_narration=n,missing_new_source_paragraphs=missing,old_narrator_audio_action='Disable old narrator MP3 in this new derivative only; original timeline/source untouched.',nonverbal_native_A1_action='Retain room/synchronous native track at original relative synchronization; protected actor/message windows must remain1:1.',picture_retime_permission='Proposal only: preserve native existing cuts/retimes/transforms/full-track composite, stretch only nonverbal interval. Root decides method and verifies visual action, no invented coverage.')
   e['proposed_duration_frames']=None if missing else math.ceil(sum(x['source_duration_seconds'] for x in n)*24-1e-8)
  if e['proposed_duration_frames'] is not None and record is not None:
   e.update(proposed_record_relative_frame=record,proposed_record_absolute_frame=86400+record,proposed_record_start_seconds=record/24)
   cursor=record/24
   for n in e['new_narration']:
    n['proposed_record_start_seconds']=cursor;n['proposed_record_end_seconds_exclusive']=cursor+n['source_duration_seconds'];cursor=n['proposed_record_end_seconds_exclusive']
   e['proposed_record_end_frame_exclusive']=record+e['proposed_duration_frames'];e['slot_tail_frame_alignment_silence_seconds']=max(0,(record+e['proposed_duration_frames'])/24-cursor) if e['new_narration'] else 0
   record+=e['proposed_duration_frames'];timepoints.append(dict(output_relative_frame=record,old_core_relative_seconds=en))
  else:record=None
 if ep==11:limitations.append('EP11 missing narrative343–346 currently replaced by erroneous348/349 at40.84–48.32s. Replace narration only atthisanchor; inspect existing11-04 visual before asserting allfourvisible actions are covered.')
 if ep==10:limitations.append('P322/P324 original written-message lines are audible video-source synchronous sound; retain1:1. They were intentionally excluded from new narrationTTS, not missing generation.')
 v=existing_visual_issues(ep,t)
 if v['native_visual_textplus_items']:limitations.append('Allsix nativeText+areconfirmedChineseeditorialnotes and excludedfromNEWcut byRoot. Fill actualprimarytrackgapswithsame-sceneexistingfootage; noChineseeditorialnotes or blackgaps. See public_xml_picture_integrity evidence.')
 return dict(episode=ep,status='FILE_PLAN_COMPLETE_READY_FOR_ROOT_CONFORM' if not pending else 'WAITING_NEW_AUDIO_WORD_TIMES',original_timeline_name=t['name'],original_timeline_id=t['id'],fps=24,timeline_start_frame=86400,original_full_timeline_duration_seconds=(t['end']-t['start'])/24,program_core_end_seconds=core_end,program_core_end_frame=round(core_end*24),excluded_tail_policy='Original source timeline remains untouched. Do not append post-core music/gap/stray snippets to new narrative program.',excluded_tail_intervals_seconds=[[core_end,(t['end']-t['start'])/24]],new_narration_full_file_seconds=sum(f['duration_seconds'] for f in files),new_source_files=files,pending_new_asr_files=pending,events=events,proposed_total_frames=record,proposed_total_seconds=None if record is None else record/24,proposed_picture_time_map_points=timepoints,proposed_time_map_clock='Output timeline-relative frames24fps; old core time seconds relative originalnative01:00:00:00. Actor/message subintervals derivative1, never retimed.',protected_word_pad_policy='Original protected speech intervals include neighboring natural pause allocated at midpoint and quantized24fps. All actual actor/message words lie inside; retain native original J/L sources and per-clip retimes.',new_voice_partition_policy='100% source-speed. Full decoded MP3duration included, split at midpoint of existing paragraph pauses only; 50–100ms word-safe trim option is reported but NOT applied. Frame-align only slot silence, never stretch voice.',public_xml_picture_integrity=v,limitations=limitations,old_alignment_file=str(oldp),old_alignment_sha256=sha(oldp),human_listening_or_visual_audition_performed=False,resolve_UI_or_API_operated=False)

out=dict(status='FILE_ONLY_PROPOSAL_NOT_NATIVE_EDIT',version='female_original',created_at=datetime.datetime.now().astimezone().isoformat(),manifest_file=str(manifestp),manifest_sha256=sha(manifestp),adopted_audio_manifest=str(adoptp),adopted_audio_manifest_sha256=sha(adoptp),source_docx=manifest['source_docx'],source_docx_sha256=manifest['source_docx_sha256'],original_native_snapshot=str(snapP),original_native_snapshot_sha256=sha(snapP),requested_rate_percent=100,source_media_modified=False,original_timeline_modified=False,episodes=[plan(10),plan(11)])
p=OUT/'paragraph_conform_plan.json';p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md=['# 女版10–11集新旁白与原正片逐段对应方案','','本文件为离线可审查方案；未操作达芬奇，也未变动现有剪辑、源音频或剧本。旁白保持100%原速，人物原对白及视频同期的短信读声保留1:1。','','Root已读取原生Text+，确认六条全是中文制作备注；新剪辑不保留这些备注，原时间线不变。公开XML省略备注正确；主轨原有空段须由同场景既有画面填足，不能输出黑隙或中文备注。','']
for ep in out['episodes']:
 md += [f'## 第{ep["episode"]}集',f'- 状态：{ep["status"]}；原正片核心{ep["program_core_end_seconds"]:.6f}秒；已到新旁白{ep["new_narration_full_file_seconds"]:.3f}秒。',f'- 建议新总时长：{ep["proposed_total_seconds"] if ep["proposed_total_seconds"] is not None else "待新音频词码"}。','','|原文段|种类|旧正片范围秒|新源范围秒|建议新起点秒|','|---|---|---|---|---|']
 for e in ep['events']:
  src='; '.join(f'{Path(n["source_path"]).name} {n["source_start_seconds"]:.4f}–{n["source_end_seconds_exclusive"]:.4f}' for n in e['new_narration']) or ('原生原声1:1' if e['kind'] in ['character_dialogue','written_message'] else '待新音频')
  md.append(f'|{",".join(map(str,e["paragraphs"]))}|{e["kind"]}|{e["old_core_start_seconds"]:.4f}–{e["old_core_end_seconds_exclusive"]:.4f}|{src}|{e.get("proposed_record_start_seconds","待定")}|')
 md+=['']+['- '+l for l in ep['limitations']]+['']
(OUT/'paragraph_conform_plan.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(json.dumps(dict(path=str(p),sha256=sha(p),episodes=[dict(episode=e['episode'],status=e['status'],events=len(e['events']),newVOseconds=e['new_narration_full_file_seconds'],duration=e['proposed_total_seconds'],pending=len(e['pending_new_asr_files'])) for e in out['episodes']]),ensure_ascii=False),flush=True)
