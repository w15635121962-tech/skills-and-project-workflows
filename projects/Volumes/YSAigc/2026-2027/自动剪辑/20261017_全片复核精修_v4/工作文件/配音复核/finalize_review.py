from pathlib import Path
import json,hashlib,importlib.metadata as md
O=Path(__file__).parent;B=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_旁白精修/工作文件');P=Path('/Volumes/YSAigc/2026-2027/文汇中学/文汇中学集团宣传策划.pdf')
wave=json.loads((O/'waveform_quality.json').read_text());comp=json.loads((O/'all_58_sentence_comparison.json').read_text());identity=json.loads((O/'source_identity_and_timing.json').read_text());short=json.loads((O/'疑点短窗再识别与声谱.json').read_text());mix=json.loads((O/'mix_transition_boundary_audit.json').read_text())
def fingerprint(p):
 p=Path(p);h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(4*1024*1024),b''):h.update(x)
 return {'path':str(p),'bytes':p.stat().st_size,'sha256':h.hexdigest()}
issues=[
 {'id':'VOICE_REVIEW_01','status':'unconfirmed_listen_required','severity':'review_only','timeline_start':235.2,'timeline_end':236.08,'frame_start':5880,'frame_duration':22,'source_script':'学校的素质教育之花绚丽绽放','pdf_pages':[32,33],'expected_word':'绚丽','expected_pinyin':'xuan4 li4','independent_asr_word':'顺利','asr_pinyin':'shun4 li4','evidence':'Whole processed narration and original 10s unprompted windows with beam 1/5 all produce 顺利. This is the SAME acoustic model, so repeated output does not confirm pronunciation.','action':'Keep original audio. Add a review marker. If real listening later confirms a misread, replace the complete phrase/whole sentence using a verified alternate take or matching rerecord; do not synthesize or splice guessed syllables.','clip':short[0]['clip'],'waveform_spectrogram':short[0]['waveform_spectrogram'],'audio_changed':False},
 {'id':'VOICE_REVIEW_02','status':'asr_ambiguity_downgraded_keep_audio','severity':'informational','timeline_start':306.0,'timeline_end':308.92,'frame_start':7650,'frame_duration':73,'source_script':'搭建名师引领、骨干赋能、青年精进的三级成长平台','pdf_pages':[37,38],'expected_word':'青年精进','expected_pinyin':'qing1 nian2 jing1 jin4','asr_alternatives':['青年精进','青年经济'],'evidence':'No-prompt original-audio short window, beam 1 gives 青年精进; beam 5 gives 青年经济. Final nasal consonant and language-model context are ambiguous.','action':'No correction. Keep all words. Optional informational marker only.','clip':short[1]['clip'],'waveform_spectrogram':short[1]['waveform_spectrogram'],'audio_changed':False},
 {'id':'TEXT_REVIEW_03','status':'script_spelling_only','severity':'informational','timeline_start':338.93,'timeline_end':340.81,'source_script':'同科异构百花齐放','pdf_pages':[37,38],'action':'Source literally uses 同科异构. Its homophone ASR output cannot determine intended spelling. Do not treat as a confirmed voice error; only review wording if authoring subtitles.','audio_changed':False},
 {'id':'INTERVIEW_TEXT_04','status':'transcript_spelling_unverified','severity':'informational','timeline_start':441.68,'timeline_end':456.28,'source_script':None,'evidence':'No authoritative interview manuscript in the supplied promo PDF. ASR produces 文型兼修/会同中西/开放世界/盛任未来; these contain homophones. Whole goal statement has clear complete grammar and intact end.','action':'Keep actual interview. Do not generate exact quotation subtitles from unverified ASR spellings.','audio_changed':False}
]
markers=[{'frame':5880,'duration':22,'color':'Yellow','name':'配音复听：绚丽/顺利（未确认）','note':'源稿绚丽；本地small多次输出顺利，尚未人工听辨。保留原声，不作无依据修音。复听原声230–240秒。'},{'frame':7650,'duration':73,'color':'Blue','name':'配音核对：青年精进，保留原声','note':'无提示短窗beam 1识别正确，beam 5识别为青年经济；判为ASR歧义，不修音。'}]
(O/'v4_voice_review_markers.json').write_text(json.dumps({'fps':25,'apply_to':'v4 timeline with unchanged narration placement','markers':markers},ensure_ascii=False,indent=2))
report={
 'review_id':'v4_full_voice_review_20261017','review_scope':{'narration_seconds':[0,433.68],'narration_original_duration':433.6588125,'narration_sentences':58,'location_voices':3,'location_ranges':[[434,437.4],[437.4,441.68],[441.68,456.28]],'full_mix_effective_duration':460.28},
 'review_type':['full no-initial-prompt ASR of actual processed audio','original versus processed waveform identity and timing','all-sample peak/non-finite/low-energy scan','all 58 reference sentence boundaries','two original-sound 10s no-prompt short-window beam comparisons','waveform and spectrogram inspection','music-overlap and voice-boundary sample analysis'],
 'human_listening_completed':False,'final_native_render_listened':False,'local_models_available':['Systran/faster-whisper-small'],'second_acoustic_model_used':False,'new_model_downloaded':False,'environment_changed':False,'resolve_touched':False,'old_files_modified':False,
 'result':'signal_and_content_integrity_checks_pass_two_wording_items_tracked_without_audio_change','confirmed_audio_repairs':[],'recommended_new_denoise':False,'recommended_new_crossfades':False,'audio_content_modified':False,
 'checks':{
  'reference_and_asr_character_count':{'reference':comp['reference_character_count'],'asr':comp['independent_character_count']},'asr_alignment_insertions':sum(x['type']=='insert' for x in comp['changes']),'asr_alignment_deletions':sum(x['type']=='delete' for x in comp['changes']),'character_substitution_spans_not_confirmed_errors':len(comp['changes']),
  'narration_original_same_time_windows':len(identity[0]['windows']),'narration_same_time_window_minimum_correlation':identity[0]['minimum_correlation'],'location_measured_lags_seconds':[x['measured_lag_seconds'] for x in identity[1:]],'speech_full_scale_sample_counts':[x['samples_at_or_above_0_9999'] for x in wave['voices']],'speech_nonfinite_samples':[x['non_finite_samples'] for x in wave['voices']],
  'narration_longest_low_energy_candidate_seconds':max(x['duration'] for x in wave['voices'][0]['low_energy_below_minus50_dbfs_candidates']),'narration_tail':mix['narration_tail_actual_last_sample_above_threshold'],'music_native_overlap_seconds':[x['native_overlap_seconds'] for x in mix['music_overlaps']],'mix_peak_dbfs':mix['mix_peak_dbfs'],'mix_full_scale_samples':mix['mix_full_scale_samples'],'unusual_transition_sample_jump_count':sum(x['unusually_large_exact_boundary_jump'] for o in mix['music_overlaps'] for x in (o['mix_start_boundary'],o['mix_end_boundary'])),'voice_file_end_samples_zero':all(x['last_sample_abs_dbfs']==-240 for x in mix['voice_boundaries'])},
 'review_items':issues,
 'source_version_differences_not_errors':['Recording opening places 深耕/film title before 青春筑梦, matching actual waveform order.','从学段独立 and 文汇中学教育集团 match PDF p25; p29 aggregate copy uses 学段割裂 / 文汇教育集团.','Closing 满怀激情/不断创新 matches p42; p43 has alternate 热忱/创新不断/蒸蒸日上, which is not in this recording.'],
 'transition_recommendation':'Retain existing fades/overlaps and silence handles. Four voice files begin/end at zero; actual word tails precede cuts with safety margin. No measured evidence warrants new crossfade or repeated denoise.',
 'limitations':['ASR is the same small acoustic model across runs; beam and context changes do not equal a second independent acoustic model.','Spectrograms and sample continuity cannot alone prove phoneme identity, tonal accuracy, perceived noise, masking or lack of clicks.','No person completed a full perceptual listen, and no new Resolve render was played.','Full mix WAV has BGM05 ending 1 frame later than the current native placement; this is within the fade tail, not voice.','No phoneme forced alignment or verified interview manuscript was provided.','No audio words, speed, pauses or processing were modified. Only original-sound review excerpts were extracted.'],
 'artifacts':{'sentence_comparison':str(O/'all_58_sentence_comparison.json'),'independent_full_asr':str(O/'independent_asr_all.json'),'waveform_quality':str(O/'waveform_quality.json'),'original_timing_identity':str(O/'source_identity_and_timing.json'),'mix_transition_report':str(O/'mix_transition_boundary_audit.json'),'short_window_evidence':str(O/'疑点短窗再识别与声谱.json'),'marker_suggestions':str(O/'v4_voice_review_markers.json')},
 'inputs_fingerprinted':[fingerprint(p) for p in [B/'audio_plan_v2.json',B/'narration_aligned.json',P,Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_开篇人文精修_v3/工作文件/native_build_v3.json')]],
 'tool_versions':{x:md.version(x) for x in ['faster-whisper','numpy','scipy','soundfile','pymupdf']}}
(O/'v4_voice_acceptance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
text='''本轮完整配音复核报告

结论：完整无提示识别、原声对照和信号完整性检查通过；未确认需要剪掉、替换或重录的字句。保留全部独特词句。没有新增降噪、语速变化或交叉淡化。
本轮不是人耳完整听审，也没有播放最终达芬奇渲染成片；以下是实际音频样本、自动识别与波形/声谱证据。

检查范围：0–433.68秒完整旁白、434.00–437.40秒教师、437.40–441.68秒群体、441.68–456.28秒校长；另扫描460.28秒完整混音（文件末0.25秒安全静音）。
本地只有small模型；本轮无初始提示、无策划词表，重新识别了实际归一化音频。未下载模型，未改环境，未操作Resolve，未改旧文件。

一、已核实的完整性
- 58句参考共1352个规范化汉字/数字，独立再识别也是1352个；单调对齐没有插入、没有删除。111处字面差异主要是同音/近音ASR字，不能据此判为配音错误。
- 原始旁白与处理旁白在87个连续5秒窗口（覆盖完整录音）保持同一采样时间；最低波形相关性0.996155。没有测到移时、漏段、重复拼入的证据。
- 三段现场声与原代理音频匹配，时移0或一个16kHz采样；分别保留完整口号、完整三项育人目标句。
- 全部四条语音无满幅削波、无非有限样本。旁白最长低能量间隔1.22秒，在开篇自然句间；不是异常大段停顿。
- 58句的首尾窗口均已记录。ASR字级时间并非逐音素边界，不据此压缩语音呼吸。
- 旁白最后明显字尾到433.620秒，低电平尾部到433.634秒；当前轨保留到433.680秒。末字无提前淡出或截断。

二、带时间码待听项（不自动修音）
1. 03:55.20–03:56.08：“绚丽绽放”。策划第32/33页为“绚丽”；完整无提示和原声10秒短窗beam 1/5都识别成“顺利”。xuan4/shun4并非完全同音，但这些结果来自同一small声学模型，不能据此确认错读。已输出230–240秒原声与波形/声谱。建议v4留黄色待听标记5880帧起22帧；现阶段保持原声。如果真实复听后确认错读，优先用已验证替代录音或重录完整短语/整句，不拼接猜测音节。
2. 05:06.00–05:08.92：“青年精进”。策划第37/38页为“青年精进”；完整识别给“青年经济”。但无提示原声短窗beam 1识别出了“青年精进”，beam 5仍给“青年经济”，说明解码上下文和尾鼻音辨识不稳定。此项已降级为ASR歧义，保留原声；可选蓝色说明标记7650帧起73帧。
3. 05:38.93–05:40.81：“同科异构”为源稿第37/38页原字。声音无法区分“科/课”等同音字，这是字幕审词事项，不是已确认错读。
4. 尾声校长采访：没有权威逐字采访稿，ASR的“文型/会同/世界/盛任”等字形不能直接用于精确引语字幕；句子结构和尾音完整，保持实际录音。

三、配乐及相邻语音边界
- 现有五处配乐交叠分别为2.00/2.00/2.00/2.00/1.96秒；已存在渐入渐出，不需要再叠加一次交叉淡化。
- 完整混音样本峰值-1.696 dBFS，无满幅削波。交叠点未测到异常大的单采样跳变。
- 四条语音有效范围首尾采样均为零；教师、群体、校长最后50毫秒RMS约-65.6/-57.1/-59.7 dBFS，末端已低电平收束，没有证据需要再加淡化或降噪。
- 教师、群体、校长最后识别词结束后分别仍有约0.50/0.41/1.12秒余量。它们是句尾呼吸与环境，不应仅为了节奏删掉完整词尾。
- 现有完整混音WAV的BGM05计划比native晚1帧结束，在淡出尾部；不是旁白或现场语音问题。报表已明确记录这个限制。

四、证据文件
v4_voice_acceptance.json：本轮新鲜验收、限制、输入SHA-256、待听项。
v4_voice_review_markers.json：供主任务添加v4标记，不自动操作Resolve。
all_58_sentence_comparison.json：58句完整对照。
independent_asr_all.json：无提示全长新识别。
source_identity_and_timing.json：完整原声时间对照。
mix_transition_boundary_audit.json：交叠、峰值、尾音、边界数据。
疑点短窗再识别与声谱.json：两处原声10秒短窗beam 1/5结果。
01/02_原声*.wav及对应PNG：原始MP3仅解码取样，无增益、无降噪、无变速。

明确限制：未完成人耳完整听审，未使用第二个声学模型，未逐音素强制对齐，未听最终native渲染；声谱不能单独决定汉字或断言语音正确。本轮只提供证据和保守处理建议，不把自动分析包装成主观听感结论。
'''
(O/'配音复核报告.txt').write_text(text)
print(json.dumps({'acceptance':str(O/'v4_voice_acceptance.json'),'confirmed_repairs':len(report['confirmed_audio_repairs']),'review_items':len(issues),'full_same_time_windows':len(identity[0]['windows']),'clips':[x['clip'] for x in short]},ensure_ascii=False))
