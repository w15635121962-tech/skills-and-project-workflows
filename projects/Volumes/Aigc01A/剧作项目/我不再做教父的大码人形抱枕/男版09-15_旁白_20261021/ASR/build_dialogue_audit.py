"""Post-recognition original-script comparison; never modifies ASR or audio.

Manual source-to-script candidates are explicit below. Transcript is not forced
into speech; substantive spoken-word variants remain flagged and unselected.
"""
from pathlib import Path
import json,re,difflib,math,datetime
BASE=Path(__file__).resolve().parent
TASK=BASE.parent
manifest=json.loads((TASK/'准备/narration_manifest.json').read_text())
index=json.loads((BASE/'转录索引.json').read_text())
levels=json.loads((BASE/'source_levels.json').read_text())
inventory=json.loads((TASK/'剪辑素材只读核查_20261022.json').read_text())
secondary=json.loads((BASE/'第二次盲识别索引.json').read_text())
assert index['completed']==104 and not index['errors'] and levels['completed']==104 and not levels['errors']
probes={x['path']:x for ep in inventory['episodes'] for x in ep['videos']}
level={x['source_path']:x for x in levels['files']}
secondary={x['source_path']:x for x in secondary['files']}
mapping={
'9-1-1':[274],'9-1-2':[274],'9-3-1':[278],'9-3-2':[278],'9-4-1':[280],'9-4-2':[280],'9-5-1':[282],'9-7-1':[285],'9-8-1':[288],'9-8-2':[288],
'10-8-1':[309,311,312],'10-9-1':[314],
'11-2-1':[323],'11-3-1':[326],'11-5-1':[330],'11-8-1':[340],'11-9-1':[344,345],'11-9-2':[344,345],
'12-1-1':[353],'12-1-2':[353],'12-2-1':[355],'12-3-1':[359],'12-3-2':[359],'12-4-1':[362],'12-4-2':[362],'12-6-1':[368],'12-10-1':[377],
'13-1-1':[382],'13-1-2':[382],'13-2-1':[384,385],'13-2-2':[385],'13-3-1':[387],'13-3-2':[387],
'14-2-2':[402],'14-6-1':[416],
'15-2-1':[428,430],'15-3-1':[431,433],'15-4-1':[434,435],'15-5-1':[439],'15-6-1':[441],'15-6-2':[441],'15-7-1':[443],'15-7-2':[443],'15-8-1':[445,446],'15-8-2':[445]}
units={};bypara={};ep_narr={}
for ep in manifest['episodes']:
 ep_narr[ep['episode']]=[x for p in ep['original_paragraphs_and_retained_narration'] for x in p['narration_retained_text'].split()]
 for q in ep['quoted_spans']:
  if q['action']!='exclude_role_or_message_dialogue':continue
  para=q['docx_paragraphs'][0];n=len(bypara.get(para,[]))+1;uid=f'EP{ep["episode"]:02d}_P{para:04d}_Q{n}'
  unit=dict(id=uid,episode=ep['episode'],docx_paragraph=para,quote_number_in_paragraph=n,original_text=q['text'][1:-1],source_candidates=[])
  units[uid]=unit;bypara.setdefault(para,[]).append(uid)
def norm(s):return re.sub(r'[^a-z0-9]','',s.lower())
files=[]
for row in index['files']:
 path=row['source_path'];name=Path(path).stem;key=name[2:]
 raw=json.loads(Path(row['json_path']).read_text());words=raw['words'];spoken=[w['word'].strip() for w in words]
 dn=[norm(x) for x in ep_narr[row['episode']]];sn=[norm(x) for x in spoken]
 longest=difflib.SequenceMatcher(None,dn,sn,autojunk=False).find_longest_match()
 sec=secondary.get(path)
 result=dict(source_path=path,filename=Path(path).name,episode=row['episode'],order_key=row['order_key'],source_sha256=row['source_sha256'],raw_asr_json=row['json_path'],raw_text=row['text'],raw_quality_flags=row['quality_flags'],source_duration_seconds=row['decoded_duration_seconds'],mean_word_probability=sum(w.get('probability',0) for w in words)/len(words) if words else None,source_audio_stream_count=len(probes[path]['audio_streams']),source_audio_single_mixed_stream=len(probes[path]['audio_streams'])==1,source_audio_gain_suggestions={k:level[path][k] for k in ['integrated_loudness_lufs','true_peak_dbfs','suggested_speech_gain_db','suggested_ambience_under_vo_gain_db']},longest_same_episode_narration_word_match_count=longest.size,secondary_blind_result=sec,dialogue_units=[])
 if key in mapping:
  uids=[u for para in mapping[key] for u in bypara[para]]
  expected=[w for u in uids for w in units[u]['original_text'].split()]
  ops=difflib.SequenceMatcher(None,list(map(norm,expected)),sn,autojunk=False).get_opcodes()
  alignment={};differences=[];substantive=False
  for tag,a,z,c,d in ops:
   if tag=='equal':
    for i,j in zip(range(a,z),range(c,d)):alignment[i]=[j]
   else:
    e=expected[a:z];o=spoken[c:d]
    if [norm(t) for t in e]==['vittoria'] and len(o)==1 and norm(o[0]) in ['victoria','viteria']:
     reason='proper_name_ASR_spelling_variant';alignment[a]=[c]
    elif e==['Mhm?'] and [norm(t) for t in o]==['mm','hmm']:
     reason='one_original_hum_token_two_observed_ASR_tokens';alignment[a]=list(range(c,d))
    elif [norm(t) for t in e]==['your','brow','knits'] and [norm(t) for t in o]==['youre','brown','nuts']:
     reason='two_models_same_phonetic_ASR_words_needs_actual_audition_before_claiming_exact_pronunciation'
     for i,j in zip(range(a,z),range(c,d)):alignment[i]=[j]
    elif key=='12-1-1' and e==['bad...'] and o==['hard.']:
     reason='substantive_bad_vs_hard_variant_supported_by_both_models_prefer_12-1-2';substantive=True
    else:raise AssertionError((key,tag,e,o))
    differences.append(dict(kind=tag,expected_original_words=e,observed_asr_words=o,original_word_indices=list(range(a,z)),observed_word_indices=list(range(c,d)),reason=reason))
  result.update(classification='source_dialogue_content_variant' if substantive else 'original_script_role_dialogue_candidate',original_docx_paragraphs=mapping[key],post_asr_differences=differences,caption_policy='Do not caption this substantive variant as exact canonical words' if substantive else 'Use original English text with observed word spans; keep phonetic/name review flags and do not invent missing spoken words',audio_policy='Keep linked same-source sync audio; reserve narration-free space for original dialogue; source bounds must contain entire words and natural action onsets')
  cursor=0
  for uid in uids:
   unit=units[uid];ew=unit['original_text'].split();indices=list(range(cursor,cursor+len(ew)));cursor+=len(ew)
   mapped=[]
   for i,orig in zip(indices,ew):
    if i not in alignment:continue
    ws=[words[j] for j in alignment[i]]
    mapped.append(dict(original_word=orig,start=min(w['start'] for w in ws),end=max(w['end'] for w in ws),observed_source_word_indices=alignment[i],observed_source_words=[w['word'] for w in ws],source_probability_min=min(w.get('probability',0) for w in ws)))
   assert mapped
   first=min(w['start'] for w in mapped);last=max(w['end'] for w in mapped);frames=int(probes[path]['video_streams'][0]['nb_frames'])
   start=max(0,math.floor((first-.15)*24));end=min(frames,math.ceil((last+.2)*24))
   candidate=dict(unit_id=uid,original_text=unit['original_text'],source_path=path,source_sha256=row['source_sha256'],source_asr_json=row['json_path'],word_start_seconds=first,word_end_seconds=last,source_in_frame=start,source_out_frame_exclusive=end,source_in_seconds=start/24,source_out_seconds=end/24,source_fps=24,complete_original_words_observed=len(mapped)==len(ew),substantive_content_variant=substantive,mean_observed_word_probability=sum(w['source_probability_min'] for w in mapped)/len(mapped),word_events=mapped,source_clip_total_frames=frames,human_listening_validated=False,visual_speaker_identity_validated=False,alignment_differences=differences,cut_note='Bounds are source-relative candidate speech handles, not final action edit points; do not use silence thresholds or words alone to cut gestures.')
   result['dialogue_units'].append(candidate);unit['source_candidates'].append(candidate)
 else:
  agreed=sec and norm(row['text'])==norm(sec['secondary_text']) and len(spoken)>=2
  noncanonical=key in ['14-1-1','14-1-2','14-8-1','14-8-2']
  result.update(classification='non_script_speech_suspect_review' if noncanonical else 'no_approved_script_dialogue_or_narration',audio_policy='Do not subtitle or duplicate this non-script text. Audition before using source under VO; lower noncanonical voice only if heard, preserving same-source linked ambience.' if noncanonical else 'Keep same-boundary linked source sync/ambience; lower under new narrator only if it masks narration. Do not turn low-confidence repetitive ASR into dialogue/captions.',caption_policy='No canonical caption from raw ASR',secondary_agreement_lexical=bool(agreed),original_narration_confirmed=False)
 files.append(result)
for u in units.values():
 ok=[x for x in u['source_candidates'] if x['complete_original_words_observed'] and not x['substantive_content_variant']]
 assert ok,('No complete canonical source candidate',u['id'])
 best=max(ok,key=lambda x:x['mean_observed_word_probability'])
 u.update(preferred_audio_candidate=best['source_path'],preferred_audio_candidate_reason='Highest mean word probability among complete script-aligned local candidates; provisional audio choice only, actual frame continuity must choose compatible picture and avoid duplicate lines.',unique_dialogue_covered=True)
summary=[]
for ep in range(9,16):
 fs=[x for x in files if x['episode']==ep];us=[x for x in units.values() if x['episode']==ep]
 summary.append(dict(episode=ep,source_count=len(fs),original_role_quote_count=len(us),original_role_quotes_with_complete_source_candidate=sum(x['unique_dialogue_covered'] for x in us),canonical_dialogue_source_candidates=sum(x['classification']=='original_script_role_dialogue_candidate' for x in fs),content_variant_sources=[x['filename'] for x in fs if x['classification']=='source_dialogue_content_variant'],non_script_speech_review_sources=[x['filename'] for x in fs if x['classification']=='non_script_speech_suspect_review']))
report=dict(created_at_local=datetime.datetime.now().isoformat(),scope='Male EP09-15; post-recognition exact original English dialogue comparison, not live Resolve or human playback',transcription_blind=True,source_expected_text_given_to_recognizer=False,source_media_modified=False,resolve_used=False,source_video_count=104,original_role_dialogue_quote_count=len(units),complete_role_dialogue_quote_coverage=sum(x['unique_dialogue_covered'] for x in units.values()),canonical_dialogue_source_candidate_count=sum(x['classification']=='original_script_role_dialogue_candidate' for x in files),episodes=summary,original_narration_audit=dict(confirmed_original_narrator_sources=[],basis='No blind recognition output established a continuous source-narration match; clear source speech aligns with external role dialogue, except the flagged non-script variants.',limitations='This is not a claim that every source is narrator/music free. Ambiguous or unrecognized voice still requires actual audition.'),music_audit=dict(proven_music_free=False,independent_music_stem_found=False,source_audio_layout='All 104 MP4 files contain one mixed AAC stereo audio stream. ffprobe and speech recognition do not classify or separate background music.',policy='Preserve linked same-source sync audio. If a source contains music or generated narration, automate gain only during new VO where it masks speech; never suppress complete original role lines to make space. Do not add further BGM in this task without a separate request.'),critical_actions=['Prefer 男版12-1-2.mp4 for P353: both independent models hear original bad; 12-1-1 yields hard in both models. Do not force bad captions over hard audio.','男版11-5-1.mp4 P330 brow knits is recognized as brown nuts by both models. Can be phonetic ASR error; mark exact pronunciation pending audition, not regenerated dialogue.','男版14-1-1、14-1-2、14-8-1、14-8-2 have non-script voice candidates. Two models agree on What did you do? / Just any two / Wait it in three sources. Do not caption those lines as original script; audition/duck only offending source voice if present.','Forty original external dialogue quotes across EP09-15 have a complete local candidate. EP13 P393/P397 are internal self-talk reserved for the new narrator, not roles.','Use exactly one source rendition per role line; multiple filename subnumbers often repeat the same spoken line. Split picture only on action/continuity and source word-safe bounds; do not duplicate dialogue or treat all variants as sequential.'],limitations=['Candidate speech handles are source-relative and preserve observed words with .15s/.2s handles; actions and lead/tail reactions must be checked before final cuts.','ASR+levels cannot certify speaker identity, lip sync, music-free sources, word pronunciation or complete human audition.','Gain suggestions never boost. Whole-stream levels include gaps/environment and require final mixed audition.','No current Resolve state, source frames or final timeline has been read or changed by this audit.'],dialogue_units=list(units.values()),files=files)
p=BASE/'同期对白与原带音轨核查.json';p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md=['# 男版09–15源同期声核查','',f'104个源视频已完成本地盲识别，0错误；{len(units)}条原文角色对白全部有完整源候选。识别及测量均未修改源片。','', '源范围和逐词证据：同期对白与原带音轨核查.json；逐文件识别：转录索引.json、raw_large-v3-turbo/；响度：source_levels.json。','', '| 集 | 源片 | 原文对白条数 | 原文匹配候选源 |','|---|---:|---:|---:|']
md += [f"| {x['episode']} | {x['source_count']} | {x['original_role_quote_count']} | {x['canonical_dialogue_source_candidates']} |" for x in summary]
md += ['','按源稿顺序串联40条角色对白，给角色对白留出无新旁白重叠的间隙。每个采用画面必须同时带入同源同入出点的同期声并链接。对白不按固定静音阈值截断，候选源范围还需给动作、呼吸及对手反应留位。','', '需要处理的具体问题：']
md += ['- '+x for x in report['critical_actions']]
md += ['', '未识别出可确证的原视频成段旁白，但这不等于所有源都无旁白/配乐。104个文件均只有一条混合AAC立体声音轨，没有独立音乐分轨；识别和响度检测不能证明是否含背景音乐。无原文角色对白的源声保留为同期环境，按实听决定新旁白期间的压低量；不要据循环幻听增写字幕。','', '本报告不代表完整人工试听、口型或画面验收。']
(BASE/'同期对白与原带音轨核查.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(json.dumps(dict(report=str(p),original_role_dialogue_quote_count=len(units),covered=report['complete_role_dialogue_quote_coverage'],canonical_dialogue_source_candidates=report['canonical_dialogue_source_candidate_count'],episodes=summary,max_source_narration_match=max(x['longest_same_episode_narration_word_match_count'] for x in files)),ensure_ascii=False,indent=2))
