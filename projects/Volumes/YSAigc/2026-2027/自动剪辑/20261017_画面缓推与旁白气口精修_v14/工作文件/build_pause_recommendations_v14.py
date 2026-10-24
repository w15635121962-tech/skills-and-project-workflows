"""Read-only speech-clock/word/waveform audit; writes analysis sidecars only."""
from pathlib import Path
import hashlib
import json
import math
import wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE = Path('/Volumes/YSAigc/2026-2027/自动剪辑')
WORK = BASE/'20261017_画面缓推与旁白气口精修_v14/工作文件'
ART = WORK/'旁白气口波形审查'
ART.mkdir(parents=True, exist_ok=True)
CURRENT = BASE/'20261017_旁白精修/工作文件/audio_v2/01_完整旁白_归一_余量.wav'
REF_PATH = BASE/'20261017_旁白精修/工作文件/narration_aligned.json'
ASR_PATH = BASE/'20261017_全片复核精修_v4/工作文件/配音复核/voice_01_independent.json'
SIGNAL_PATH = BASE/'20261017_全片复核精修_v4/工作文件/配音复核/waveform_quality.json'
LIVE_PATH = WORK/'live_before_v14.json'
REF = json.loads(REF_PATH.read_text())
ASR = json.loads(ASR_PATH.read_text())
LIVE = json.loads(LIVE_PATH.read_text())
WORDS = [w for s in ASR['segments'] for w in s['words']]
PHRASES = {p['id']: p for p in REF['phrases']}
VIDEO = [i for t in LIVE['snapshot']['video'] if t['track']==1 for i in t['items']]
FPS, SR, SPF = 25, 48000, 1920

# Editorial decisions are semantic pairs, not silence-threshold proposals.
# Each tightening is restored at the following thought boundary in the same
# chapter. Deliberate opening, school-name cards, and spoken tail are untouched.
PAIRS = [
 ('P01',2,3,(63.08,63.74,28,29),(65.55,65.88,29,30),'让“人文与自然相融、知识与生活共生”两层关系连贯，把时间还给“让校园每一处角落”的结果句。'),
 ('P02',3,3,(85.34,85.98,37,38),(86.94,87.28,38,39),'收紧“顺势而生、应势而立”的对仗，完整落句后再进入“四校之力”。'),
 ('P03',3,3,(99.53,100.24,42,43),(103.14,103.66,43,44),'两项“从…到…”并列更连贯，收出的时间放在“九年贯通”后的集团名起句；后句起声接近2503帧画面切点。'),
 ('P04',4,2,(119.60,120.18,51,52),(125.40,125.76,55,56),'体育至舞台的并列展示轻收2帧，在四类场景说完后给“多元的舞台”留足转折。'),
 ('P05',5,2,(184.17,184.56,83,84),(186.46,186.77,84,85),'制度化、体系化、生态化作为一组并列稍连贯；“办学模式”落句后再说民生期盼。'),
 ('P06',6,3,(209.52,210.09,93,94),(212.56,213.09,95,96),'“学识为灯、仁爱为光、深耕教坛、潜心育人”保持句内连贯，停顿移至进入课堂事例前。'),
 ('P07',6,2,(215.11,215.62,96,97),(219.53,219.81,98,99),'课堂、课后两种行动轻收；“用温暖陪伴成长”前略放气口，突出学校人文关怀。'),
 ('P08',7,2,(259.03,259.50,116,117),(261.36,261.79,117,118),'培养体系四项并列收紧最后一项前停顿，把时间放到“全程护航”落句后，再进入“让成长无断层”。'),
 ('P09',9,2,(340.88,341.39,154,155),(343.59,343.93,155,156),'特色项目两层陈述轻收；让“每一位学子”作为结果与关注主体得到清楚起句。'),
 ('P10',10,4,(386.89,387.50,173,174),(389.69,390.00,174,175),'“从优质办学，到全域教育生态构建”句内连贯，完成思想后再进入集团未来承诺。'),
 ('P11',10,3,(403.90,404.48,180,181),(406.14,406.43,181,182),'贯通、融合、共生三项排比更均衡；第二项提前3帧接近10109帧画面起点，第三项恢复原时钟。'),
]


def read_audio(handle, start, end):
    start_sample, end_sample = round(start*SR), round(end*SR)
    handle.setpos(max(0,start_sample))
    raw=handle.readframes(end_sample-max(0,start_sample))
    v=np.frombuffer(raw,np.uint8).reshape(-1,3).astype(np.int32)
    v=v[:,0]|(v[:,1]<<8)|(v[:,2]<<16)
    v=np.where(v&0x800000,v-0x1000000,v).reshape(-1,2)
    return v.astype(np.float64)/8388608


def db(v):
    return None if v==0 else float(20*np.log10(v))


def stats(a):
    return {'sample_count_per_channel':len(a),
            'peak_dbfs':db(float(np.max(np.abs(a)))),
            'rms_dbfs':db(float(np.sqrt(np.mean(a*a)))),
            'nonzero_channel_samples':int(np.count_nonzero(a)),
            'all_samples_exact_zero':bool(not np.any(a))}


def best_window(handle, a, b, length_frames):
    # Search only within a semantically chosen, previously measured gap.
    # One frame either side is measured to protect a centered two-frame fade.
    vals=[]
    for s in range(math.ceil(a*FPS+1),math.floor(b*FPS-1)-length_frames+1):
        e=s+length_frames
        signal=read_audio(handle,(s-1)/FPS,(e+1)/FPS)
        vals.append((float(np.mean(signal*signal)),s,e,stats(signal)))
    if not vals:raise ValueError(('No guarded quiet window',a,b,length_frames))
    _,s,e,m=min(vals,key=lambda q:q[:3])
    return s,e,m


def best_insert(handle,a,b):
    vals=[]
    for p in range(math.ceil(a*FPS+1),math.floor(b*FPS-1)+1):
        signal=read_audio(handle,(p-1)/FPS,(p+1)/FPS)
        vals.append((float(np.mean(signal*signal)),p,stats(signal)))
    _,p,m=min(vals,key=lambda q:q[:2])
    return p,m


def anchor(sec,new_sec):
    f=round(sec*FPS)
    active=next((i for i in VIDEO if i['start']<=f<i['end']),None)
    nearest=min(VIDEO,key=lambda i:abs(i['start']-round(new_sec*FPS)))
    return {'source_next_activity_candidate_seconds':sec,
            'planned_next_activity_candidate_timeline_seconds':new_sec,
            'planned_next_activity_candidate_frame':round(new_sec*FPS),
            'current_active_picture':{k:active[k] for k in ('name','start','end','path')} if active else None,
            'nearest_existing_picture_cut':{k:nearest[k] for k in ('name','start','end','path')},
            'difference_to_nearest_picture_cut_frames':new_sec*FPS-nearest['start'],
            'note':'下一声能活动为旧实测低能量窗结束，用于导航；不是人工逐音素起声结论。视频不移动，组内第二次动作后源时钟完整恢复。'}


def plot_action(handle,r):
    fnt='/System/Library/Fonts/STHeiti Medium.ttc'
    font=ImageFont.truetype(fnt,21);small=ImageFont.truetype(fnt,17)
    im=Image.new('RGB',(1920,345),'#faf9f4');d=ImageDraw.Draw(im)
    src=r['source_gap_seconds'];lo=max(0,src[0]-1.05);hi=src[1]+1.05
    a=read_audio(handle,lo,hi).mean(axis=1)
    x0,x1=100,1890; px=lambda t:x0+(t-lo)/(hi-lo)*(x1-x0)
    d.text((18,8),f'{r["id"]} | 源{src[0]:.2f}–{src[1]:.2f}s | {r["operation"]} {r["delta_frames"]:+d}f | {r["previous_phrase"]} → {r["next_phrase"]}',font=font,fill='#142f2a')
    d.text((18,38),f'建议操作源帧 {r["source_start_frame"]}–{r["source_end_frame"]}；校验静区 {r["safe_signal_window_seconds"]}；audition_available=false',font=small,fill='#4b5953')
    for yy in (77,144,214,310):d.line((x0,yy,x1,yy),fill='#c4ccc8')
    g0,g1=r['safe_signal_window_seconds'];gx0,gx1=px(g0),px(g1)
    d.rectangle((gx0,68,gx1,310),fill='#ddf0df')
    for j in range(x1-x0):
        i0=int(j*len(a)/(x1-x0));i1=max(i0+1,int((j+1)*len(a)/(x1-x0)))
        chunk=a[i0:i1];amp=.55
        d.line((x0+j,111-min(32,float(chunk.max())/amp*32),x0+j,111-max(-32,float(chunk.min())/amp*32)),fill='#346c72')
    points=[]
    for n in range(0,len(a)-480,480):
        rms=np.sqrt(np.mean(a[n:n+480]**2));level=max(-110,20*np.log10(max(rms,1e-12)))
        points.append((px(lo+n/SR),207-(level+110)/110*58))
    d.line(points,fill='#b06c30',width=2)
    # A real-source STFT makes residual phonetic energy visible around the gap.
    nfft,hop=2048,240
    frames=np.lib.stride_tricks.sliding_window_view(a,nfft)[::hop]
    spec=np.abs(np.fft.rfft(frames*np.hanning(nfft),axis=1))/(nfft/2)
    spec=spec[:,np.fft.rfftfreq(nfft,1/SR)<=8000]
    levels=np.clip((20*np.log10(np.maximum(spec,1e-8))+110)/95,0,1)
    rgb=np.empty((*levels.T.shape,3),dtype=np.uint8)
    strength=levels.T[::-1];rgb[:,:,0]=(strength*245).astype('uint8');rgb[:,:,1]=(strength*200).astype('uint8');rgb[:,:,2]=(strength*125).astype('uint8')
    tile=Image.fromarray(rgb).resize((x1-x0,88),Image.Resampling.BILINEAR)
    im.paste(tile,(x0,218))
    d=ImageDraw.Draw(im)
    for p in (r['source_start_frame']/FPS,r['source_end_frame']/FPS):d.line((px(p),70,px(p),308),fill='#61d278',width=2)
    d.text((10,93),'波形',font=small,fill='#346c72');d.text((10,165),'RMS',font=small,fill='#ad682a');d.text((10,241),'0–8kHz',font=small,fill='#333333')
    for t in np.arange(math.ceil(lo*2)/2,hi,.5):
        xx=px(float(t));d.line((xx,309,xx,315),fill='#44534b');d.text((xx-18,318),f'{t:.2f}',font=small,fill='#44534b')
    path=ART/f'{r["id"]}_源波形频谱.png';im.save(path)
    return path


actions=[];pair_rows=[]
with wave.open(str(CURRENT)) as h:
    assert h.getparams()[:3]==(2,3,SR)
    for pair_id,chapter,n,shorten,expand,reason in PAIRS:
        pair_actions=[];offset=0
        for j,(a,b,previous_id,next_id) in enumerate((shorten,expand)):
            previous,nextp=PHRASES[previous_id],PHRASES[next_id]
            delta=-n if j==0 else n
            if j==0:
                s,e,m=best_window(h,a,b,n);guard=((s-1)/FPS,(e+1)/FPS)
            else:
                s,m=best_insert(h,a,b);e=s;guard=((s-1)/FPS,(s+1)/FPS)
            context=[w for w in WORDS if w['end']>=a-.5 and w['start']<=b+.5]
            overlaps=[w for w in context if w['end']>guard[0] and w['start']<guard[1]]
            r={'id':pair_id+('_收' if j==0 else '_放'),'pair_id':pair_id,'chapter_id':chapter,
               'operation':'remove_silence' if j==0 else 'insert_digital_zero_in_existing_quiet',
               'source_gap_seconds':[a,b],'source_start_frame':s,'source_end_frame':e,
               'source_start_seconds':s/FPS,'source_end_seconds':e/FPS,
               'source_start_sample':s*SPF,'source_end_sample':e*SPF,
               'delta_frames':delta,'delta_seconds':delta/FPS,'delta_samples':delta*SPF,
               'previous_phrase_id':previous_id,'next_phrase_id':next_id,
               'previous_phrase':previous['text'],'next_phrase':nextp['text'],
               'reference_previous_words':previous['words'][-3:],'reference_next_words':nextp['words'][:3],
               'noninterpolated_independent_asr_words_near_gap':context,
               'asr_token_spans_overlapping_quiet_guard':overlaps,
               'asr_overlap_interpretation':'ASR词时段可能把静音分配给相邻字；本建议不按token时间截字，只操作实际波形/频谱确认为静区的中心。' if overlaps else '独立ASR相邻词时间与静区相容。',
               'safe_signal_window_seconds':list(guard),'safe_signal_window_source_frames':[round(guard[0]*FPS),round(guard[1]*FPS)],
               'actual_guard_signal':m,
               'confidence':'high_digital_zero_signal_semantic_verified_no_audition' if m['all_samples_exact_zero'] else 'supported_near_zero_residual_signal_semantic_verified_no_audition',
               'waveform_visual_reviewed':False,'audition_available':False,
               'original_to_new_cumulative_frames_before_action':offset,
               'timeline_action_frame_before_action':s+offset,
               'original_to_new_cumulative_frames_after_action':offset+delta,
               'picture_anchor':anchor(b,b+(offset+delta)/FPS),
               'reason':reason,
               'implementation':'移除仅含静区的指定源帧；可在实际拼口两侧各1帧已测静区内做居中2帧去咔，必须把总时长减少量保持为delta_frames。' if j==0 else '只在指定原静区整帧点插入delta_frames数字零，原有呼吸与全部源样本继续保留；不要复制含呼吸的整段，也不要跨空隙加交叉淡化。'}
            r['cut_point_10ms_signal']=stats(read_audio(h,s/FPS-.005,s/FPS+.005))
            r['cut_point_10ms_source_sample_range']=[s*SPF-240,s*SPF+240]
            r['manipulated_speech_samples']=0
            if j==1:
                assert r['cut_point_10ms_signal']['all_samples_exact_zero']
                r['confidence']='high_exact_zero_cut_point_semantic_and_spectrogram_verified_no_audition'
                r['insertion_guard_note']='指定插入点周围10ms逐样本全零；80ms邻域即使有极低电平残余亦不修改。原呼吸全部保留，插入空隙无需淡化。'
            r['waveform_spectrogram_image']=str(plot_action(h,r))
            actions.append(r);pair_actions.append(r['id']);offset+=delta
        assert offset==0
        pair_rows.append({'pair_id':pair_id,'chapter_id':chapter,'actions':pair_actions,'net_delta_frames':offset,'reason':reason,
                          'original_clock_restored_at_source_frame':actions[-1]['source_start_frame'],
                          'source_span_seconds':[shorten[0],expand[1]]})

for k in range(0,len(actions),6):
    part=actions[k:k+6];sheet=Image.new('RGB',(1920,len(part)*345+40),'white');d=ImageDraw.Draw(sheet)
    for i,r in enumerate(part):sheet.paste(Image.open(r['waveform_spectrogram_image']),(0,i*345))
    p=ART/f'气口波形频谱总览_{k//6+1}.jpg';sheet.save(p,quality=94)
    for r in part:r['waveform_contact_sheet']=str(p)

sources={'original_narration':'/Volumes/YSAigc/2026-2027/文汇中学/配音/文汇学校配音.mp3',
         'current_native_a1':str(CURRENT),'word_reference':str(REF_PATH),'independent_noninterpolated_asr':str(ASR_PATH),
         'prior_signal_audit':str(SIGNAL_PATH),'fresh_live_snapshot':str(LIVE_PATH),
         'previous_full_audio_acceptance':str(BASE/'20261017_全片复核精修_v4/工作文件/配音复核/v4_voice_acceptance.json'),
         'full_reference_text':str(BASE/'20261017_旁白精修/工作文件/narration_aligned.txt'),
         'current_A1_sha256':hashlib.sha256(CURRENT.read_bytes()).hexdigest()}
out={'status':'semantic_and_actual_signal_recommendations_pending_visual_review','fps':FPS,'sample_rate':SR,'sample_width_bits':24,
     'audition_available':False,'resolve_connected_or_modified':False,'source_audio_modified':False,
     'sources':sources,'mapping':'fresh A1 start=0, offset=0, end=10842f; existing source seconds map one-to-one to timeline until the proposed local edits. Each pair has net zero frames and restores the original clock before leaving its own short span.',
     'full_timeline_frames':11507,'original_narration_clip_end_frame':10842,'A2_fixed_anchor_frames':[10850,10935,11042],
     'fixed_chapter_reference_spans':REF['chapters'],'pairs':pair_rows,'actions':actions,
     'constraints':['全部独特词句、原有呼吸、人文长停顿保留；语音不变速。','仅处理已选语义气口中心，不用统一阈值删呼吸；每条都联查实际24bit信号、原稿字时与无提示独立ASR。','11处删除范围及其两侧各1帧guard逐样本全零；11处插入点周围10ms逐样本全零。插入点较大邻域的极低电平残余不修改，呼吸不复制不删除。任何审听或图示不确定点应整组保护。','视频、音乐、照片时长和章节总时钟不移动；每组删除/插入严格等帧，A2三时点不变。','2帧去咔只能处理实际压缩拼口，不能另多消耗2帧，也不能跨插入静音空隙做交叉淡化。'],
     'protected_points':[{'seconds':[4.01,5.22],'reason':'开篇自然入校、先建立空间的长呼吸。'},{'seconds':[19.10,20.32],'reason':'集团名后标题退出与青春起句的长呼吸。'},{'seconds':[149.97,161.59],'reason':'四校校名与原生题签逐一对应，完整保留原声时点。'},{'seconds':[300.36,311.52],'reason':'师资成长与校长双图照片/题签的核心时点，不在此处挪语音。'},{'seconds':[433.53,434.00],'reason':'最终“来”实际尾音到约433.62，保留原旁白至433.68，不按ASR433.53裁尾。'},{'seconds':[434.0,456.28],'reason':'教师、群体口号与校长采访口型和音画同步，维持固定位置与完整句尾。'}],
     'limitations':['没有直接音频输入/正常速度主观听审，audition_available=false；不声称逐音素人工听过或保证主观听感。','原字级参考含源稿插值，仅作语义导航；非插值独立ASR亦有把静区划给词的时间误差。','实际源波形、频谱与静区逐样本检查支持这些局部剪口，成片仍应提供正常速度试听。']}
path=WORK/'旁白气口精修建议_v14.json';path.write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps({'path':str(path),'pairs':len(pair_rows),'actions':len(actions),'net_frames':sum(r['delta_frames'] for r in actions),'exact_zero_guards':sum(r['actual_guard_signal']['all_samples_exact_zero'] for r in actions)},ensure_ascii=False))
for r in actions:print(r['id'],r['source_start_frame'],r['source_end_frame'],r['delta_frames'],r['actual_guard_signal'])
