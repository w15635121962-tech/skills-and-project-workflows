from pathlib import Path
import hashlib,json,math,re,subprocess
import numpy as np
from PIL import Image,ImageDraw

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent.parent
FF=Path('/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffmpeg')
WAVE=BASE/'waveform_review';WAVE.mkdir(exist_ok=True)
inv=json.loads((BASE.parent/'男版素材盘点.json').read_text())
probes={x['path']:x for ep in inv['episodes'] for x in ep['videos']}
requests={21:['3-1','5-1','6-1','6-2','7-1'],22:['2-1','2-2','3-1','4-1','5-1'],23:['2-1','3-1','5-1','6-1'],24:['2-1','2-2','5-1','6-1']}
boundaries={
 '男版21-3-1':[(0,6),(7,7)],'男版21-5-1':[(0,4)],'男版21-6-1':[(0,6),(7,14)],'男版21-6-2':[(0,6),(7,14)],'男版21-7-1':[(0,7)],
 '男版22-2-1':[(0,21)],'男版22-2-2':[(0,21)],'男版22-3-1':[(0,5),(6,13),(14,18),(19,23),(24,28)],'男版22-4-1':[(0,11),(12,17),(18,24)],'男版22-5-1':[(0,11),(12,24)],
 '男版23-2-1':[(0,4),(5,11),(12,17)],'男版23-3-1':[(0,10)],'男版23-5-1':[(0,6),(7,11)],'男版23-6-1':[(0,3)],
 '男版24-2-1':[(0,1),(2,7),(8,13)],'男版24-2-2':[(0,0),(1,11)],'男版24-5-1':[(0,7),(8,12)],'男版24-6-1':[(0,6),(7,12),(13,14),(15,24),(25,33),(34,39),(40,47)],
}

def db(x):return float(20*np.log10(max(float(x),1e-12)))
def norm(s):return re.sub('[^a-z0-9]+','',s.lower())
def frame_energy(audio,rate=16000):
    win=320;hop=160
    if len(audio)<win:audio=np.pad(audio,(0,win-len(audio)))
    chunks=np.lib.stride_tricks.sliding_window_view(audio,win)[::hop]
    rms=np.sqrt(np.mean(chunks**2,axis=1)+1e-24)
    spectrum=np.abs(np.fft.rfft(chunks*np.hanning(win),axis=1))**2
    frequencies=np.fft.rfftfreq(win,1/rate)
    band=(frequencies>=300)&(frequencies<=3400)
    brms=np.sqrt(2*np.sum(spectrum[:,band],axis=1)/(win**2)+1e-24)
    return (np.arange(len(rms))*hop+win/2)/rate,rms,brms
def metric(audio,ts,rms,brms,a,b):
    chunk=audio[max(0,int(a*16000)):min(len(audio),max(1,int(b*16000)))]
    use=(ts>=a)&(ts<=b)
    before=(ts>=max(0,a-.35))&(ts<max(0,a-.04))
    after=(ts>min(ts[-1],b+.04))&(ts<=min(ts[-1],b+.35))
    bg=np.r_[rms[before],rms[after]]
    return dict(rms_dbfs=db(np.sqrt(np.mean(chunk**2)+1e-24)) if len(chunk) else -240,
                peak_dbfs=db(np.max(np.abs(chunk))) if len(chunk) else -240,
                band_300_3400_hz_rms_dbfs=db(np.sqrt(np.mean(brms[use]**2)+1e-24)) if use.any() else -240,
                nearby_background_median_dbfs=db(np.median(bg)) if len(bg) else None,
                rms_envelope_p10_dbfs=db(np.percentile(rms[use],10)) if use.any() else -240,
                rms_envelope_p90_dbfs=db(np.percentile(rms[use],90)) if use.any() else -240)
def boundary_energy(ts,rms,t):
    m=(ts>=t-.015)&(ts<=t+.015)
    return float(np.mean(rms[m])) if m.any() else float(rms[np.argmin(np.abs(ts-t))])
def choose_cut(ts,rms,lo,hi,preferred,fps,frames):
    aa=max(0,math.ceil((lo-1e-8)*fps));bb=min(frames,math.floor((hi+1e-8)*fps))
    if aa>bb:return None
    candidates=list(range(aa,bb+1))
    # Minimize local boundary energy while staying near the requested padding.
    return min(candidates,key=lambda f:db(boundary_energy(ts,rms,f/fps))+.7*abs(f/fps-preferred)/.05)

sources=[];flat=[];units=[];plots=[]
for ep,ss in requests.items():
 for suffix in ss:
    name=f'男版{ep}-{suffix}'
    p=BASE/'raw_large-v3-turbo'/f'EP{ep}'/'video'/(name+'.json');d=json.loads(p.read_text());src=Path(d['source_path'])
    sha=hashlib.sha256(src.read_bytes()).hexdigest();assert sha==d['source_sha256']
    cp=subprocess.run([str(FF),'-v','error','-i',str(src),'-vn','-ac','1','-ar','16000','-f','f32le','pipe:1'],capture_output=True,check=True)
    audio=np.frombuffer(cp.stdout,dtype='<f4');ts,rms,brms=frame_energy(audio)
    vr=probes[str(src)]['video_streams'][0];num,den=map(int,vr['avg_frame_rate'].split('/'));fps=num/den;frames=int(vr['nb_frames']);media_end=frames/fps
    wave=dict(source_path=str(src),source_sha256=sha,hop_seconds=.01,window_seconds=.02,times_seconds=ts.tolist(),rms_dbfs=(20*np.log10(rms+1e-12)).tolist(),speech_band_300_3400_hz_dbfs=(20*np.log10(brms+1e-12)).tolist())
    (WAVE/(name+'.envelope.json')).write_text(json.dumps(wave,ensure_ascii=False)+'\n')
    arr=[]
    for idx,(a,b) in enumerate(boundaries[name],1):
        ws=d['words'][a:b+1];wordstart=ws[0]['start'];wordend=ws[-1]['end'];text=''.join(w['word'] for w in ws).strip()
        inf=choose_cut(ts,rms,max(0,wordstart-.22),max(0,wordstart-.08),max(0,wordstart-.12),fps,frames)
        if inf is None:inf=max(0,math.floor(wordstart*fps))
        outf=choose_cut(ts,rms,min(media_end,wordend+.08),min(media_end,wordend+.24),min(media_end,wordend+.16),fps,frames)
        if outf is None:outf=min(frames,math.ceil(wordend*fps))
        cautions=[];use=True;status='waveform_and_word_times_supported_not_auditioned'
        if any(w['probability']<.6 for w in ws):cautions.append('low_confidence_word_keep_raw_text_unverified')
        if name=='男版23-2-1' and idx==1:
            cautions.append('opening_words_or_name_uncertain_do_not_use_ASR_as_caption_truth');status='source_audio_range_candidate_text_needs_review'
        if name=='男版24-2-1' and idx==1:
            use=False;status='uncertain_vocalization_not_approved_dialogue';cautions.append('possible_breath_or_ASR_hallucination')
        if name=='男版24-2-1' and idx==3:
            use=False;status='repeated_or_incomplete_question_not_auto_use';cautions.append('same_question_repeated_then_unreliable_tail_keep_first_complete_sentence')
        if name=='男版24-2-2':
            use=False;status='unreliable_text_not_auto_use';cautions.append('several_low_confidence_content_words_cannot_confirm_dialogue_from_ASR_or_energy')
        m=metric(audio,ts,rms,brms,wordstart,wordend)
        if m['peak_dbfs']<-55 or m['rms_dbfs']<-65:
            use=False;status='insufficient_signal_energy';cautions.append('low_energy_does_not_support_confident_dialogue_use')
        r=dict(source_path=str(src),source_sha256=sha,episode=ep,source_name=name,sentence_index=idx,
               recognized_text=text,first_word_index=a,last_word_index=b,word_start_seconds=wordstart,word_end_seconds=wordend,
               source_fps=fps,source_in_frame=inf,source_out_frame_exclusive=outf,source_out_frame_inclusive=outf-1,
               source_in_seconds=inf/fps,source_out_seconds=outf/fps,
               first_last_word_preserved_by_ASR=inf/fps<=wordstart+1e-5 and outf/fps>=wordend-1e-5,
               left_padding_seconds=wordstart-inf/fps,right_padding_seconds=outf/fps-wordend,
               mean_word_probability=sum(w['probability'] for w in ws)/len(ws),min_word_probability=min(w['probability'] for w in ws),
               waveform_energy=m,waveform_envelope_path=str(WAVE/(name+'.envelope.json')),
               auto_use_candidate=use,review_status=status,cautions=cautions,human_listening_validated=False,words=ws)
        assert r['first_last_word_preserved_by_ASR']
        arr.append(r)
    for j in range(len(arr)-1):
        a,b=arr[j:j+2]
        # A 10-100ms ASR inter-word gap is not a robust editing handle;
        # keep adjacent clauses continuous rather than risk consonant tails.
        if b['word_start_seconds']-a['word_end_seconds']<.16:
            a['merge_with_next_to_avoid_word_cut']=True;b['merge_with_previous_to_avoid_word_cut']=True
            continue
        if a['source_out_frame_exclusive']<=b['source_in_frame']:continue
        gaplo=a['word_end_seconds'];gaphi=b['word_start_seconds']
        cut=choose_cut(ts,rms,gaplo,gaphi,(gaplo+gaphi)/2,fps,frames)
        if cut is None:
            a['merge_with_next_to_avoid_word_cut']=True;b['merge_with_previous_to_avoid_word_cut']=True
            continue
        a['source_out_frame_exclusive']=cut;a['source_out_frame_inclusive']=cut-1;a['source_out_seconds']=cut/fps;a['right_padding_seconds']=cut/fps-a['word_end_seconds']
        b['source_in_frame']=cut;b['source_in_seconds']=cut/fps;b['left_padding_seconds']=b['word_start_seconds']-cut/fps
        a['boundary_to_next']=dict(frame=cut,time_seconds=cut/fps,rms_dbfs=db(boundary_energy(ts,rms,cut/fps)),note='shared cut lies between complete ASR words, no repeated padded audio')
    srcunits=[]
    for r in arr:
        if not r['auto_use_candidate']:continue
        if srcunits and (r.get('merge_with_previous_to_avoid_word_cut') or srcunits[-1]['source_out_frame_exclusive']>r['source_in_frame']):
            u=srcunits[-1];u['sentence_indices'].append(r['sentence_index']);u['recognized_text']+=' '+r['recognized_text'];u['source_out_frame_exclusive']=max(u['source_out_frame_exclusive'],r['source_out_frame_exclusive']);u['source_out_seconds']=u['source_out_frame_exclusive']/fps;u['reason']='adjacent sentences kept continuous because word gap is under 160ms or no safe 24fps boundary exists'
        else:
            srcunits.append(dict(source_path=str(src),source_sha256=sha,episode=ep,source_name=name,source_fps=fps,sentence_indices=[r['sentence_index']],recognized_text=r['recognized_text'],source_in_frame=r['source_in_frame'],source_out_frame_exclusive=r['source_out_frame_exclusive'],source_in_seconds=r['source_in_seconds'],source_out_seconds=r['source_out_seconds'],reason='word-complete interval with conservative handles',human_listening_validated=False))
    # One compact waveform chart per source, marking word spans and sentence bounds.
    width=1500;height=250;im=Image.new('RGB',(width,height),'#10151c');draw=ImageDraw.Draw(im)
    x0=45;x1=width-20;y0=60;yh=120
    draw.text((10,10),f'{name}  source {media_end:.3f}s / audio {len(audio)/16000:.3f}s  |  word/energy only, not auditioned',fill='white')
    for sec in range(math.ceil(media_end)+1):
        x=x0+int((x1-x0)*sec/media_end)
        if x<=x1:draw.line((x,y0,x,y0+yh),fill='#26313e');draw.text((x,190),str(sec),fill='#96a3b5')
    for ti,ri in zip(ts,rms):
        if ti>media_end:break
        x=x0+int((x1-x0)*ti/media_end);h=int(np.clip((db(ri)+70)/70,0,1)*yh)
        draw.line((x,y0+yh,x,y0+yh-h),fill='#65b8f5')
    for k,r in enumerate(arr):
        color='#58d99a' if r['auto_use_candidate'] else '#fb956c'
        xa=x0+int((x1-x0)*r['word_start_seconds']/media_end);xb=x0+int((x1-x0)*r['word_end_seconds']/media_end)
        draw.line((xa,35+k%2*10,xb,35+k%2*10),fill=color,width=4)
        draw.text((xa,211+k%2*15),f'S{r["sentence_index"]}',fill=color)
        for ti in (r['source_in_seconds'],r['source_out_seconds']):
            x=x0+int((x1-x0)*ti/media_end);draw.line((x,y0,x,y0+yh),fill=color,width=1)
    png=WAVE/(name+'.png');im.save(png);plots.append(png)
    sources.append(dict(source_path=str(src),source_sha256=sha,episode=ep,raw_text=d['text'],source_video_frames=frames,source_video_duration_seconds=media_end,decoded_audio_duration_seconds=len(audio)/16000,waveform_png_path=str(png),sentences=arr,safe_continuous_units=srcunits))
    flat.extend(arr);units.extend(srcunits)

for start in range(0,len(plots),6):
    ims=[Image.open(p) for p in plots[start:start+6]]
    sheet=Image.new('RGB',(1500,250*len(ims)),'black')
    for j,im in enumerate(ims):sheet.paste(im,(0,j*250))
    sheet.save(WAVE/f'contact_{start//6+1}.png')

out=dict(scope='18 male EP21-24 source videos, sentence-level recommendations only',source_count=len(sources),sentence_count=len(flat),safe_continuous_unit_count=len(units),
         model_input_blind=True,expected_script_supplied_to_model=False,source_timing='source-relative seconds; native video 24fps frame edges',waveform_method='mono16k decode, 20ms RMS window / 10ms hop; 300-3400Hz band energy; conservative 80-240ms handles; cuts constrained outside ASR word spans',
         human_listening_validated=False,limits=['波形能量只支持有信号/边界，不证明信号必为对白，也不能纠正低置信识别词。','ASR词时码有误差；保守保留词前后余量，人工复听可进一步确认，不把此结果称为逐字听验。','相邻句没有安全24fps字间切点时，推荐连续保留，禁止把重叠带余量范围逐一顺拼。','source_out_frame_exclusive为不含结束帧；若SDK要求含结束帧，应减1。','视频尾部与AAC时长可能相差约一帧，源剪辑边界以视频帧数为限。'],sources=sources,ranges=flat,safe_continuous_units=units)
(BASE/'speech_ranges.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(sources=len(sources),sentences=len(flat),auto_use_sentence_candidates=sum(r['auto_use_candidate'] for r in flat),continuous_units=len(units),output=str(BASE/'speech_ranges.json')),ensure_ascii=False))
