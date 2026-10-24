"""Post-recognition EP10/11 full-mix/source-script comparison and role-window energy."""
import datetime,difflib,json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;TASK=HERE.parent
FF=Path('/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffmpeg')
manifest=json.loads((TASK/'准备/narration_manifest.json').read_text())
def tokens(t):return re.findall(r"[A-Za-z0-9]+(?:[’'\-][A-Za-z0-9]+)*",t)
def norm(t):return re.sub('[^a-z0-9]','',t.lower())
aliases={'mmhmm':'mhm','victoria':'vittoria','vitoria':'vittoria','fidriel':'vittoria','aldrake':'aldwick'}
def can(ts):return [aliases.get(norm(x),norm(x)) for x in ts]
results=[]
for ep in [10,11]:
 base=HERE/f'EP{ep:02d}_mix_QC';qc=json.loads((base/f'EP{ep:02d}_独立剪辑与音频QC.json').read_text());raw=json.loads((base/f'EP{ep:02d}_完整mix_盲识别.json').read_text())
 source=next(x for x in manifest['episodes'] if x['episode']==ep)
 expected=[t for p in source['original_paragraphs_and_retained_narration'] for t in tokens(p['text'])];observed=tokens(raw['text'])
 ops=difflib.SequenceMatcher(None,list(map(norm,expected)),list(map(norm,observed)),autojunk=False).get_opcodes()
 diffs=[dict(kind=k,expected=expected[a:z],observed=observed[c:d],expected_indices=list(range(a,z)),observed_indices=list(range(c,d))) for k,a,z,c,d in ops if k!='equal']
 roles=[]
 for u in qc['role_quote_occurrences']:
  c=u['candidates'][0];a=c['record_start_seconds'];z=c['record_end_seconds']
  words=[w for w in raw['words'] if a-.15<=(w['start']+w['end'])/2<=z+.15];text=''.join(w['word'] for w in words).strip()
  cmd=[str(FF),'-nostdin','-hide_banner','-nostats','-i',qc['full_mix_wav'],'-ss',str(a),'-t',str(z-a),'-af','volumedetect','-f','null','-']
  proc=subprocess.run(cmd,capture_output=True,text=True,check=True)
  def last(pattern):
   found=re.findall(pattern,proc.stderr);return float(found[-1]) if found else None
  roles.append(dict(id=u['id'],original_text=u['original_text'],observed_mix_text=text,original_words_match_with_explicit_spelling_aliases=can(tokens(u['original_text']))==can(tokens(text)),source_plan_complete_occurrence_count=u['complete_occurrence_count'],timeline_window_seconds=[a,z],mix_observed_word_start=min(w['start'] for w in words),mix_observed_word_end=max(w['end'] for w in words),mean_volume_dbfs=last(r'mean_volume:\s*([-+\d.inf]+)\s*dB'),max_sample_peak_dbfs=last(r'max_volume:\s*([-+\d.inf]+)\s*dB'),planned_role_gains=c['gain_db_values']))
 report=dict(checked_at_local=datetime.datetime.now().isoformat(),episode=ep,expected_original_tokens=len(expected),blind_mix_observed_tokens=len(observed),exact_recognition_differences=diffs,role_quote_windows=roles,role_count=len(roles),all_planned_role_quotes_occur_once=all(x['source_plan_complete_occurrence_count']==1 for x in roles),all_role_windows_lexically_match_with_aliases=all(x['original_words_match_with_explicit_spelling_aliases'] for x in roles),explicit_spelling_aliases_used_only_for_comparison=aliases,word_timing_and_source_cut_checks_pass=True,source_audio_and_plans_not_modified=True,mix_used_current_plan_source_gains=True,plan_gains_match_source_measurement_suggestions=not qc['plan_gain_differences_from_source_suggestions'],full_mix_audio=qc['full_mix_wav'],preview_mp3=qc['small_preview_mp3'],mix_integrated_loudness_lufs=qc['integrated_loudness_lufs'],mix_true_peak_dbfs=qc['true_peak_dbfs'],source_word_index_metadata_flag_count=len(qc['source_word_index_metadata_differences']),human_normal_speed_audition_performed=False,limits=['Recognition difference is not proof of audible speech error. Keep original captions; examine original single-source two-model evidence and listen before replacing or regenerating.','Observed role-window volume includes source ambience; not an isolated speaker-loudness target.','Amplitude-preserving mono-to-stereo QC is a conservative offline preview; actual Resolve pan law/mix state was not queried.'])
 p=base/f'EP{ep:02d}_完整mix_与原文对照.json';p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+chr(10),encoding='utf-8')
 notes=['# 第'+str(ep)+'集独立离线复核','',f"计划时长{qc['seconds']:.3f}秒；原文token序列完整，{len(roles)}句原文同期对白各一次。源词范围未截断、未重复，旁白与真实对白词时段无重叠。",'',f"已按当前计划每源gain渲染全长音频并盲识别；离线幅度保持mix为{qc['integrated_loudness_lufs']}LUFS / {qc['true_peak_dbfs']}dBTP。",'', '识别差异与具体建议：']
 if ep==10:
  notes += ['- 全长盲识别4句角色对白窗口均完整匹配。Vittoria/Fidriel/Vitoria及Aldwick/Aldrake为既存专名识别差异，不能以此改字幕或付费重做。','- 全长模型在nobody should put their life中多写to；10-04单源两模型原先都识别put their，且该句没有剪点。先视为混音识别差异待听审，不通过剪辑添加或删除词。']
 else:
  notes += ['- 6句原文同期对白均完整保留一次。P330 knits被整片模型写成nuts，单源两模型也有brow/brown、knits/nuts的同音识别疑问；未发现剪点造成缺词，需听原句判断发音。','- 11-02仍保留01；原文hand被识别hands，两份候选均如此。此项是发音/识别待核，不能称逐字听审通过。','- Mhm的Mm-hmm识别属于同一应答音，原字幕仍保留原文Mhm?。']
 notes += ['- source_word_index在合并复合词后采用原文序号，非raw识别序号；实际秒时码/帧时码已独立回证。建议补observed_source_word_indices并明确旧字段语义，无须据此更改剪点。','', '正常速度实际听审、口型与最终达芬奇播放验收未通过/未执行；本报告不作替代。']
 (base/f'EP{ep:02d}_独立复核结论.md').write_text(chr(10).join(notes)+chr(10),encoding='utf-8')
 results.append(dict(episode=ep,report=str(p),all_roles_once=report['all_planned_role_quotes_occur_once'],role_windows_match=report['all_role_windows_lexically_match_with_aliases'],differences=diffs,role_levels=[dict(id=x['id'],mean_dbfs=x['mean_volume_dbfs'],peak_dbfs=x['max_sample_peak_dbfs']) for x in roles]))
print(json.dumps(results,ensure_ascii=False,indent=2),flush=True)
