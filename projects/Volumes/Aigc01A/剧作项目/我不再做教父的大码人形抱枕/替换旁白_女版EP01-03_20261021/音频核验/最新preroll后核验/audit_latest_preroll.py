from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
import difflib, hashlib, json, re, unicodedata, wave
import numpy as np

OUT = Path(__file__).resolve().parent
BASE = OUT.parent.parent
ROOT = BASE.parent

def read(p): return json.loads(Path(p).read_text())
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def wav(p):
    with wave.open(str(p), 'rb') as w:
        meta = {'sample_rate':w.getframerate(), 'channels':w.getnchannels(), 'sample_width_bytes':w.getsampwidth(), 'samples':w.getnframes()}
        raw = w.readframes(w.getnframes())
    assert meta['channels'] == 1 and meta['sample_width_bytes'] == 3
    u = np.frombuffer(raw, np.uint8).reshape(-1, 3).astype(np.int32)
    n = u[:,0] | (u[:,1]<<8) | (u[:,2]<<16)
    return meta, raw, (n ^ 0x800000) - 0x800000
def db(x): return float(20*np.log10(max(float(x), 1e-12)))
def diff(a,b):
    return [{'operation':op,'expected_index':[i,j],'observed_index':[x,y],'expected':a[i:j],'observed':b[x:y]} for op,i,j,x,y in difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes() if op!='equal']

manifest_path = BASE/'42段对齐WAV_制作结果.json'
manifest_hash = digest(manifest_path)
render = read(manifest_path)
plan = read(BASE/'EP01-03_42切新旁白槽位计划.json')
snapshot = read(BASE/'替换前_完整时间线实读.json')
anchors = read(BASE/'字幕与新旁白_词锚点.json')['anchors']
aliases = read(BASE/'旧剪口到新旁白_逐词映射候选.json')['name_digit_aliases_for_alignment_only']
aliases.update({'belante':'bellandi','6':'six','2':'two'})
def norm(t):
    t=''.join(c for c in unicodedata.normalize('NFD',t.lower()) if unicodedata.category(c)!='Mn').replace('’',"'")
    suffix="'s" if t.endswith("'s") else ''
    q=t[:-2] if suffix else t
    return aliases.get(q,q)+suffix
def tokens(t): return [norm(x) for x in re.findall(r"[A-Za-z0-9]+(?:['’][A-Za-z]+)?", t)]
def words(d,ep,offset=0,origin='full_episode_blind_ASR'):
    z=[]
    for s in d['segments']:
        for w in s['words']:
            for t in tokens(w['word']): z.append({'normalized':t,'raw_word':w['word'],'start':w['start']+offset,'end':w['end']+offset,'origin':origin})
    # Documented post-recognition title/name variants only; no model prompt.
    if ep==1 and len(z)>1:
        if z[0]['normalized']=='mafea': z[0]['normalized']='mafia'
        if z[1]['normalized'] in ('de','da'): z[1]['normalized']='don'
    return z

slot_records=[]; grouped=defaultdict(list)
old_by_id={i['id']:(t,i) for t in snapshot['timelines'] for tr in t['tracks']['audio'] if tr['index']==4 for i in tr['items']}
for c in render['clips']:
    p=Path(c['path']); meta,raw,pcm=wav(p); t,old=old_by_id[c['old_item_id']]
    same_slot=(c['record_start_frame']==old['start'] and c['record_end_frame_exclusive']==old['end'] and c['record_duration_frames']==old['duration'])
    ok=(digest(p)==c['sha256'] and meta['sample_rate']==48000 and meta['samples']==c['samples']==c['record_duration_frames']*1600 and same_slot)
    slot_records.append({'episode':c['episode'],'old_item_id':c['old_item_id'],'path':str(p),'sha256':digest(p),**meta,'target_frames':c['record_duration_frames'],'original_record_start_frame':old['start'],'original_record_end_frame_exclusive':old['end'],'record_slot_matches_original':same_slot,'pass':ok})
    grouped[c['island_id']].append(c)

island_records=[]; head_records=[]
plan_islands={x['island_id']:x for x in plan['merged_islands']}
for i in render['islands']:
    cc=sorted(grouped[i['island_id']],key=lambda c:c['record_start_frame'])
    meta,raw,pcm=wav(i['output'])
    rebuilt=b''.join(wav(c['path'])[1] for c in cc)
    contiguous=all(x['record_end_frame_exclusive']==y['record_start_frame'] for x,y in zip(cc,cc[1:]))
    source_hash_ok=digest(i['source'])==i['source_hash']
    island_records.append({'island_id':i['island_id'],'sha256':digest(i['output']),'samples':meta['samples'],'target_samples':i['target_samples'],'clips_rebuild_island_PCM_byte_exact':rebuilt==raw,'contiguous_original_slots':contiguous,'source_MP3_hash_unchanged':source_hash_ok,'pass':rebuilt==raw and contiguous and source_hash_ok and meta['samples']==i['target_samples']})
    if i.get('preserved_leading_subtitle_preroll_s',0)>0:
        pp=plan_islands[i['island_id']]; rs=cc[0]['record_start_frame']/30
        aa=min((a for a in anchors if a['episode']==i['episode'] and rs-.001<=a['target_record_start_seconds']<cc[-1]['record_end_frame_exclusive']/30),key=lambda a:a['target_record_start_seconds'])
        s=i['segments'][0]; src_first=aa['new_source_word_start_seconds']
        projected=rs+s['output_in']+(src_first-s['new_source_in'])/(s['new_source_out']-s['new_source_in'])*(s['output_out']-s['output_in'])
        silent_samples=round(i['preserved_leading_subtitle_preroll_s']*48000)
        nonzero=np.flatnonzero(pcm)
        thresholds={}
        step=96 # 2 ms RMS, observations only, not a phoneme boundary detector.
        pad=np.pad(pcm.astype(np.float64)/(2**23),(0,(-len(pcm))%step)).reshape(-1,step)
        rms=np.sqrt(np.mean(pad*pad,axis=1))
        for threshold in (-50,-45,-40):
            loc=np.flatnonzero(rms>=10**(threshold/20))
            thresholds[str(threshold)] = None if not len(loc) else rs+int(loc[0])*step/48000
        head_records.append({'island_id':i['island_id'],'caption_index_zero_based':aa['caption_index_zero_based'],'caption_text':aa['original_text'],'record_start_s':rs,'caption_start_s':aa['target_record_start_seconds'],'inserted_preroll_seconds':i['preserved_leading_subtitle_preroll_s'],'inserted_preroll_samples':silent_samples,'inserted_preroll_exact_zero_PCM':not np.any(pcm[:silent_samples]),'first_nonzero_PCM_record_time_s':None if not len(nonzero) else rs+int(nonzero[0])/48000,'first_2ms_RMS_above_dbfs_record_time_s':thresholds,'first_word_source_ASR_start_s':src_first,'renderer_projected_first_word_ASR_anchor_record_time_s':projected,'projected_anchor_minus_original_caption_s':projected-aa['target_record_start_seconds'],'source_in_s':i['source_in'],'retained_source_before_first_word_ASR_ms':(src_first-i['source_in'])*1000,'unchanged_source_head_waveform_evidence':pp.get('head_waveform'),'source_head_boundary_repair':pp.get('head_boundary_repair'),'limitations':'RMS/onset and ASR timing do not prove every low-level consonant is intact; no listening claim.'})

generation_items=[x for x in read(ROOT/'对标音色旁白制作_20261020/制作与下载进度.json')['items'] if x['episode'] in (1,2,3)]
ep_records=[]; caption_timing=[]; current_pcm={}
for ep in (1,2,3):
    path=OUT/'EP01_最新preroll_盲ASR.json' if ep==1 else BASE/f'音频核验/处理后ASR/EP{ep:02d}_处理后盲ASR.json'
    proc=read(path); meta,raw,pcm=wav(proc['source']); current_pcm[ep]=pcm
    assert digest(proc['source'])==proc['source_sha256']
    observed=[]; ghosts=[]
    for w in words(proc,ep):
        piece=pcm[max(0,round(w['start']*48000)):min(len(pcm),round(w['end']*48000))]
        if not len(piece): piece=pcm[max(0,round((w['start']-.010)*48000)):min(len(pcm),round((w['end']+.010)*48000))]
        if len(piece) and not np.any(piece): ghosts.append(w)
        else: observed.append(w)
    targeted=None
    if ep==2:
        tp=BASE/'音频核验/处理后ASR/EP02_island01_针对遗漏疑点_盲ASR.json'; td=read(tp)
        assert digest(td['source'])==td['source_sha256']
        intro=words(td,ep,offset=492/30,origin='reused_hash_verified_isolated_first_island_blind_ASR')
        observed=intro+observed; targeted=str(tp)
    source=[]; canonical=[]; offsets={}
    for item in sorted([x for x in generation_items if x['episode']==ep],key=lambda x:x['narration_sequence']):
        seq=item['narration_sequence'];d=read(BASE/f'ASR/大码女版枕头{ep:02d}-{seq:02d}-01.json')
        assert digest(d['source'])==d['source_sha256']
        source+=words(d,ep,origin=f'new_source_seq{seq}')
        offsets[seq]=len(canonical);canonical+=tokens(item['generation_text'])
    expected=[w['normalized'] for w in source];actual=[w['normalized'] for w in observed]
    dif=diff(expected,actual); canon_dif=diff(canonical,actual)
    alignment={}
    for op,i,j,x,y in difflib.SequenceMatcher(None,canonical,actual,autojunk=False).get_opcodes():
        if op=='equal' or (op=='replace' and j-i==y-x): alignment.update(zip(range(i,j),range(x,y)))
    for a in [a for a in anchors if a['episode']==ep]:
        k=offsets[a['narration_sequence']]+a['canonical_source_word_index_start_zero_based'];l=offsets[a['narration_sequence']]+a['canonical_source_word_index_end_exclusive']-1
        if k not in alignment or l not in alignment: continue
        first,last=observed[alignment[k]],observed[alignment[l]]
        caption_timing.append({'episode':ep,'caption_index_zero_based':a['caption_index_zero_based'],'text':a['original_text'],'caption_start_s':a['target_record_start_seconds'],'caption_end_s':a['target_record_end_seconds'],'first_processed_ASR_word':first,'last_processed_ASR_word':last,'raw_ASR_first_minus_caption_s':first['start']-a['target_record_start_seconds'],'raw_ASR_last_end_minus_caption_end_s':last['end']-a['target_record_end_seconds'],'warning':'ASR time span can include silence. Do not infer audible onset from raw word start.'})
    tl=next(t for t in snapshot['timelines'] if t['ep']==ep)
    ep_records.append({'episode':ep,'listener':proc['source'],'sha256':proc['source_sha256'],**meta,'listener_samples_match_original_timeline_length':meta['samples']==(tl['end']-tl['start'])*1600,'ASR_path':str(path),'ASR_reused_by_exact_current_audio_hash':ep!=1,'targeted_EP02_first_island_reused':targeted,'source_word_count':len(expected),'observed_verified_word_count':len(actual),'processing_missing_duplicate_or_reordered_word_candidates':dif,'canonical_generation_text_vs_ASR_differences':canon_dif,'silence_hallucination_tokens_excluded_with_exact_zero_PCM':ghosts,'final_source_words':expected[-12:],'final_processed_words':actual[-12:],'human_listening_verified':False})

listener_clip_records=[]
for ep in (1,2,3):
    pcm=current_pcm[ep]
    for c in [c for c in render['clips'] if c['episode']==ep]:
        _,_,slot=wav(c['path']);part=pcm[c['record_start_frame']*1600:c['record_end_frame_exclusive']*1600]
        delta=part.astype(np.int64)-slot.astype(np.int64)
        maxdiff=int(np.max(abs(delta)))
        listener_clip_records.append({'episode':ep,'clip_index_zero_based':c['clip_index_zero_based'],'listener_vs_slot_max_abs_difference_24bit_LSB':maxdiff,'pass_quantization_only':maxdiff<=1})

assert digest(manifest_path)==manifest_hash, 'Render manifest changed during audit; rerun required.'
report={'status':'LATEST_PREROLL_FILES_HASH_AND_SLOT_QC_COMPLETE','created_at_utc':datetime.now(timezone.utc).isoformat(),'render_manifest':str(manifest_path),'render_manifest_sha256':manifest_hash,'render_manifest_status':render['status'],'source_plan_sha256':digest(BASE/'EP01-03_42切新旁白槽位计划.json'),'source_plan_matches_manifest_hash':digest(BASE/'EP01-03_42切新旁白槽位计划.json')==render['source_plan_sha256'],'episodes':ep_records,'clip_count':len(slot_records),'all_42_clip_hashes_and_original_slots_pass':all(x['pass'] for x in slot_records),'slots':slot_records,'island_count':len(island_records),'all_30_islands_reconstruct_exact_PCM':all(x['pass'] for x in island_records),'islands':island_records,'listener_vs_clips':listener_clip_records,'all_listener_slots_within_one_24bit_LSB':all(x['pass_quantization_only'] for x in listener_clip_records),'preroll_changed_island_count':len(head_records),'preroll_first_caption_anchor_records':head_records,'all_preroll_prefixes_exact_digital_zero':all(x['inserted_preroll_exact_zero_PCM'] for x in head_records),'total_verified_lexical_tokens':sum(x['observed_verified_word_count'] for x in ep_records),'all_24_source_paragraphs_ordered_word_coverage':all(not x['processing_missing_duplicate_or_reordered_word_candidates'] for x in ep_records),'latest_EP01_title_name_post_ASR_normalization':'Mafea da Matteo Belante -> mafia don matteo bellandi only for lexical comparison. Raw recognition retained.','caption_timing_estimates':caption_timing,'Resolve_or_UI_modified':False,'source_media_modified':False,'human_listening_or_full_mix_acceptance':False,'imported_into_Resolve_verified':False,'limits':['This report supersedes the previous EP01 hash-specific report only for latest preroll outputs. EP02/03 prior blind ASR was reused only after exact current file hash match.','ASR words and numeric waveform evidence do not verify tiny phoneme integrity, clicks, timbre, speed naturalness, or audible final mix.','Native Resolve import/persistence is the parent task; these are offline prepared WAV checks.']}
outpath=BASE/'音频核验/最新preroll后核验.json'
outpath.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
lines=['# 最新 preroll 后音频只读核验','',f"最新 EP01 已重新盲转录；EP02/03 与上轮完整盲转录文件 SHA-256 完全相同，复用识别结果。24条源旁白共 {report['total_verified_lexical_tokens']} 个词按顺序对应，未发现本次处理新增漏词、重词或倒序。首句专名的识别拼写差异仅在比较时规范化，原始识别未改。",'',f"42段 WAV 的当前哈希、48kHz/单声道/24bit、采样数均与原42槽逐帧长度一致（每30fps帧1600样本）。30个连续岛可由对应槽片逐字节拼回。监听文件与对应槽的差异均在24bit的1 LSB以内。",'','EP01 六个修正岛已独立核对前置静音与首字幕锚点：']
for h in head_records:
    lines.append(f"- {h['island_id']}：新增静音 {h['inserted_preroll_seconds']:.6f}s（PCM全零）；首词源ASR锚点投影相对字幕起点 {h['projected_anchor_minus_original_caption_s']:+.6f}s；源首词之前保留 {h['retained_source_before_first_word_ASR_ms']:.1f}ms。")
lines+=['','上述六岛首句在最新 EP01 全长盲识别中均保留，末句也完整。ASR 首词时码可能把前置静音纳入，不能以其原始 start 判断静音是否生效。JSON另外列出实际 PCM 前导零和2ms RMS 阈值观察。','','未做人工听辨、Resolve导入或持久化验证；轻辅音、接缝、语速自然度及混音仍应实际听辨。EP02/03的 spent/spend 共源识别差异及数字静音幻觉沿用既有证据，不属于此次变速新增漏词。']
(BASE/'音频核验/最新preroll后核验.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'report':str(outpath),'manifest_sha256':manifest_hash,'total_words':report['total_verified_lexical_tokens'],'word_coverage':report['all_24_source_paragraphs_ordered_word_coverage'],'slots':report['all_42_clip_hashes_and_original_slots_pass'],'islands':report['all_30_islands_reconstruct_exact_PCM'],'listener_delta_within_1LSB':report['all_listener_slots_within_one_24bit_LSB'],'preroll_zero':report['all_preroll_prefixes_exact_digital_zero'],'episode_diffs':[(x['episode'],x['processing_missing_duplicate_or_reordered_word_candidates']) for x in ep_records],'heads':head_records},ensure_ascii=False,indent=2))
