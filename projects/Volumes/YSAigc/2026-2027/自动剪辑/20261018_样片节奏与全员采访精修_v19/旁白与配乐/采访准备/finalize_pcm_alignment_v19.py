import json, os, sys, subprocess, concurrent.futures
from pathlib import Path
import numpy as np, soundfile as sf
from scipy import signal
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent
WORK=ROOT/'完整尾音与时延校准';WORK.mkdir(exist_ok=True)
WRAP=ROOT/'run_skill_pcm24.py'
plan=json.loads((ROOT.parents[1]/'工作文件/采访最终方案/four_speaker_plan_final.json').read_text())
settings={'书记':(60,-18,-15.77),'金台书院小学':(53,-28,-15.19),'前门外国语学校':(50,-29,-15.60),'文汇小学':(51,-25,-14.49)}

def execute(label,args,stem,env=None):
    cmd=[sys.executable,str(WRAP),*map(str,args),'--json']
    result=subprocess.run(cmd,capture_output=True,text=True,env=env)
    (WORK/f'{stem}_{label}.json').write_text(result.stdout)
    (WORK/f'{stem}_{label}.log').write_text(result.stderr)
    if result.returncode:raise RuntimeError(label+' '+result.stdout+result.stderr)
    return json.loads(result.stdout)

def rmsdb(x):return float(20*np.log10(max(float(np.sqrt(np.mean(x*x))),1e-12)))

def corr(x,y,sr,a,b):
    x=x[round(a*sr):round(b*sr)];y=y[round(a*sr):round(b*sr)]
    sos=signal.butter(3,[300,5000],btype='bandpass',fs=sr,output='sos')
    x=signal.sosfiltfilt(sos,x);y=signal.sosfiltfilt(sos,y)
    c=signal.correlate(y,x,mode='full',method='fft');lags=signal.correlation_lags(len(y),len(x));sel=abs(lags)<=2400
    idx=int(np.argmax(c[sel]));lag=int(lags[sel][idx]);co=float(c[sel][idx]/np.sqrt((x*x).sum()*(y*y).sum()))
    return {'window_seconds':[a,b],'lag_samples':lag,'normalized_correlation':co}

def run(row):
    stem=Path(row['source']).stem;nf,threshold,target=settings[row['speaker_key']]
    x,sr=sf.read(ROOT/f'{stem}_channel0_原声全覆盖.wav');n=len(x)
    padded=WORK/f'{stem}_输入保留100ms尾部余量.wav';sf.write(padded,np.pad(x,(0,4800)),sr,subtype='PCM_24')
    nr=WORK/f'{stem}_降噪带尾部余量.wav';eq=WORK/f'{stem}_高通压缩带尾部余量.wav'
    execute('padded_denoise',['audio.py',padded,'--denoise','--denoise-strength',nf,'-o',nr],stem)
    env=os.environ.copy();env['V19_VOICE_THRESHOLD']=str(threshold);env['PYTHONUTF8']='1'
    execute('padded_voice',['audio.py',nr,'--voice','light','-o',eq],stem,env)
    # afftdn alone is measured independently; highpass phase can move the correlation peak by one sample.
    nr_x,_=sf.read(nr)
    a=row['source_in_sec'];b=row['source_out_sec_exclusive'];mid=(a+b)/2
    windows=[(a,min(a+3,b)),(max(a,b-3),b),(mid-1.5,mid+1.5)]
    nr_lags=[corr(x,nr_x[:n],sr,lo,hi) for lo,hi in windows]
    delay=int(round(np.median([r['lag_samples'] for r in nr_lags])))
    assert 1199<=delay<=1201,(stem,nr_lags)
    passes=[]
    final=ROOT/f'{stem}_采访精修_源时钟对齐_48k24bit_v19.wav'
    for trial in range(4):
        norm=WORK/f'{stem}_归一化校准{trial+1}.wav'
        result=execute(f'normalize_trial{trial+1}',['loudness.py',eq,'-I',target,'--tp','-2.2','--lra','20','--sample-rate','48000','-o',norm],stem)
        y,ysr=sf.read(norm);assert ysr==sr
        y=y[delay:delay+n];assert len(y)==n
        temp=WORK/f'{stem}_对齐校准{trial+1}.wav';sf.write(temp,y,sr,subtype='PCM_24')
        measured=execute(f'aligned_measure_trial{trial+1}',['loudness.py',temp,'--measure-only','-I','-16','--tp','-2.2'],stem)
        stats=measured.get('measured',measured)
        value=float(stats['input_i']);peak=float(stats['input_tp'])
        passes.append({'trial':trial+1,'requested_normalizer_target':target,'actual':stats,'normalizer_result':result.get('result')})
        if abs(value+16)<=.25 and peak<=-2:break
        target+=(-16-value)
    assert abs(value+16)<=.5,(stem,passes)
    assert peak<=-2,(stem,passes)
    sf.write(final,y,sr,subtype='PCM_24')
    after=[corr(x,y,sr,lo,hi) for lo,hi in windows]
    assert all(abs(r['lag_samples'])<=2 for r in after),(stem,after)
    old_nr,_=sf.read(ROOT/f'{stem}_01_轻降噪_全覆盖.wav')
    # Same source-time quiet windows, before loudness gain, to separate NR from normalization.
    source_meta=json.loads((ROOT/'source_measurement_v19.json').read_text())
    src_meta=next(r for r in source_meta if r['speaker']==row['speaker_key'])
    quiet=[]
    for lo,hi,_ in src_meta['quiet_windows']:
        start=round(lo*sr);end=round(hi*sr)
        quiet.append({'source_window':[lo,hi],'input_dbfs':rmsdb(x[start:end]),
                      'noise_reduced_before_gain_dbfs':rmsdb(nr_x[start+delay:end+delay]),
                      'final_dbfs':rmsdb(y[start:end])})
    selected_path=WORK/f'{stem}_选句仅测量.wav'
    sf.write(selected_path,y[round(a*sr):round(b*sr)],sr,subtype='PCM_24')
    selected=execute('selected_phrase_measure',['loudness.py',selected_path,'--measure-only','-I','-16','--tp','-2.2'],stem)
    # Joint word + signal check of low-level onsets and tails, including edge words.
    words=row['retained_asr_words_original'];checks=[]
    for word in words:
        wa=float(word['start']);wb=float(word['end'])
        if wb<=wa:continue
        for kind,lo,hi in [('onset',wa,min(wb,wa+.05)),('tail',max(wa,wb-.05),wb)]:
            ii=max(0,round(lo*sr));jj=min(n,round(hi*sr))
            if jj<=ii:continue
            input_rms=rmsdb(x[ii:jj]);output_rms=rmsdb(y[ii:jj]);checks.append({'word':word['word'],'part':kind,'source_window':[lo,hi],
                    'original_dbfs':input_rms,'processed_dbfs':output_rms,'gain_db':output_rms-input_rms,
                    'output_nonzero_fraction':float(np.count_nonzero(y[ii:jj])/max(1,jj-ii))})
    flagged=[c for c in checks if c['output_nonzero_fraction']<.95 or c['gain_db']<-12]
    rec={'speaker_key':row['speaker_key'],'source_video':row['source'],'source_channels_wav':row['channels_wav'],
         'prepared_wav':str(final),'source_channel_zero_based':0,'source_clock':'unchanged: full continuous source clock, no cut',
         'source_n_samples':n,'prepared_n_samples':len(y),'sample_rate':sr,'channels':1,'subtype':sf.info(final).subtype,
         'duration_seconds':n/sr,'padding_before_processing_samples':4800,'measured_afftdn_delay_samples':delay,
         'compensation':'advance measured afftdn delay, take original N samples; padded tail protects all original end samples',
         'nr_correlation_before_compensation':nr_lags,'final_correlation_after_compensation':after,
         'final_measurement':stats,'loudness_calibration_passes':passes,
         'selected_source_range':[a,b],'selected_phrase_measurement':selected.get('measured',selected),
         'quiet_same_window_before_after':quiet,'word_onset_tail_signal_checks':checks,'flagged_signal_checks':flagged,
         'recipe':{'afftdn':f'nf=-{nf}:tn=1','highpass_Hz':80,'compressor_threshold_dbfs':threshold,'ratio':2,'attack_ms':15,'release_ms':160,'makeup_linear':1,'gate':'none','normalizer':'two-pass, measured calibrated target, TP -2.2, LRA20','PCM_codec':'pcm_s24le via project-local in-memory override, installed skill unmodified'},
         'normal_speed_audition':'unavailable - no listening tool. Do not claim audition or no audible artifacts.',
         'limitation':'Waveforms and correlation cannot establish natural timbre or prove all quiet phonemes perceptually intact.'}
    # Plot exact same source clock, independently scaled lanes with envelope gain reported in JSON.
    im=Image.new('RGB',(1600,900),(245,245,245));d=ImageDraw.Draw(im)
    for j,(lo,hi) in enumerate([(a-.25,a+.75),(b-.75,b+.25)]):
        ii=max(0,round(lo*sr));jj=min(n,round(hi*sr));d.text((20,j*440+10),f'{stem} SOURCE {lo:.3f}-{hi:.3f}s (input upper / processed lower)',fill=(0,0,0))
        for k,arr in enumerate([x[ii:jj],y[ii:jj]]):
            peak=max(float(np.max(abs(arr))),1e-9);base=j*440+120+k*195
            d.line((20,base,1580,base),fill=(170,170,170))
            bins=np.linspace(0,len(arr),1561).astype(int)
            for px in range(1560):
                z=arr[bins[px]:max(bins[px]+1,bins[px+1])];p1=base-int(float(z.max())/peak*75);p2=base-int(float(z.min())/peak*75)
                d.line((20+px,p1,20+px,p2),fill=(20,75,145) if k==0 else (30,130,75))
    image=ROOT/f'{stem}_原声处理后同源时钟切口波形.jpg';im.save(image,quality=94);rec['edge_waveform_proof']=str(image)
    (ROOT/f'{stem}_最终校准记录.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2))
    print(json.dumps({'speaker':row['speaker_key'],'final':str(final),'LUFS':value,'TP':float(stats['input_tp']),'residual_lags':[r['lag_samples'] for r in after],'word_flags':len(flagged)},ensure_ascii=False),flush=True)
    return rec

if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(run,plan))
    (ROOT/'four_speaker_audio_ready_v19.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
