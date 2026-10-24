from pathlib import Path
from datetime import datetime,timezone
import csv,hashlib,json,math,re,subprocess,sys,wave
import numpy as np
ROOT=Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕')
NARR=ROOT/'女版04-06_新旁白_20261023';TASK=ROOT/'达芬奇_女版04-06旁白剪辑_20261023';OUT=TASK/'PCM_原速准备';LOG=OUT/'核验记录'
FFBIN=Path('/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin');FF=str(FFBIN/'ffmpeg');FP=str(FFBIN/'ffprobe')
SEL=NARR/'最终采用清单.json';SEL_BYTES=SEL.read_bytes();S=json.loads(SEL_BYTES);SRC_MAN=NARR/'文本核验/manifest.json';SRC_MAN_SHA=hashlib.sha256(SRC_MAN.read_bytes()).hexdigest()
SR=48000;TARGET_I=-16.0;TARGET_TP=-1.5;RECIPE_TP=-1.6;RESAMPLE='aresample=48000:exact_rational=1:dither_method=none'
SHA=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(args,raw=False):
 p=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
 err=p.stderr.decode('utf-8','replace')
 if p.returncode:raise RuntimeError({'argv':args,'returncode':p.returncode,'stderr':err})
 return (p.stdout if raw else p.stdout.decode('utf-8','replace')),err

def decode(path,rate=None,af=None):
 args=[FF,'-hide_banner','-nostdin','-v','error','-xerror','-i',str(path),'-map','0:a:0','-vn','-sn','-dn']
 if af:args+=['-af',af]
 if rate:args+=['-ar',str(rate)]
 args+=['-ac','1','-c:a','pcm_f32le','-f','f32le','-']
 raw,err=run(args,True);assert not err.strip(),err
 return np.frombuffer(raw,dtype='<f4').astype(np.float64),args

def measure(path,label):
 args=[FF,'-hide_banner','-nostdin','-i',str(path),'-map','0:a:0','-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']
 stdout,stderr=run(args);matches=re.findall(r'\{\s*"input_i"\s*:.*?\}',stderr,re.S);assert matches,stderr[-1500:]
 d=json.loads(matches[-1]);(LOG/f'{label}_实际响度.log').write_text(stderr,encoding='utf-8')
 rec={'measurement_only':True,'media_output':'null only','argv':args,'measured_input':d};(LOG/f'{label}_实际响度.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 return {'integrated_lufs':float(d['input_i']),'true_peak_dbtp':float(d['input_tp']),'lra_lu':float(d['input_lra']),'input_threshold_lufs':float(d['input_thresh']),'measurement_file':str(LOG/f'{label}_实际响度.json')}

def db(a):
 v=float(a);return 20*math.log10(v) if v>0 else None

def pcm_stats(a,sr):
 w=max(1,round(sr*.01));chunks=a[:len(a)//w*w].reshape(-1,w);rms=np.sqrt(np.mean(chunks**2,axis=1))
 return {'decoded_sample_count':int(len(a)),'decoded_sample_rate':sr,'decoded_duration_seconds':len(a)/sr,'sample_peak_dbfs':db(np.max(np.abs(a))),'overall_rms_dbfs':db(np.sqrt(np.mean(a*a))),'samples_over_full_scale':int(np.count_nonzero(np.abs(a)>1.0)),'leading50ms_rms_dbfs':db(np.sqrt(np.mean(a[:round(sr*.05)]**2))),'trailing50ms_rms_dbfs':db(np.sqrt(np.mean(a[-round(sr*.05):]**2))),'minimum10ms_rms_dbfs':db(np.min(rms)),'zero_sample_count':int(np.count_nonzero(a==0)),'diagnostic_only_no_gate_no_trim':True}

def compare(ref,out,linear):
 assert len(ref)==len(out)
 x=ref-ref.mean();y=out-out.mean();n=len(ref);nfft=1<<(2*n-1).bit_length()
 corr=np.fft.irfft(np.fft.rfft(y,nfft)*np.conj(np.fft.rfft(x,nfft)),nfft)
 pa=int(np.argmax(corr[:n]));na=int(np.argmax(corr[-(n-1):])) if n>1 else 0
 nv=float(corr[-(n-1)+na]) if n>1 else -float('inf');pv=float(corr[pa])
 lag=pa if pv>=nv else na-(n-1);peak=max(pv,nv);den=float(np.linalg.norm(x)*np.linalg.norm(y));coef=peak/den
 ratio=float(np.dot(ref,out)/np.dot(ref,ref));res=out-ref*linear
 return {'method':'full-length zero-mean normalized FFT cross-correlation on common48000Hz source-reference and output; global valid lags searched','lag_output_relative_to_source_samples_48000':lag,'lag_seconds':lag/SR,'maximum_normalized_correlation':float(coef),'zero_lag_normalized_correlation':float(np.dot(x,y)/den),'estimated_constant_gain_db':20*math.log10(ratio),'maximum_abs_residual_vs_source_reference_times_gain':float(np.max(np.abs(res))),'rms_residual_vs_constant_gain':float(np.sqrt(np.mean(res**2))),'zero_latency_compensation_needed':lag==0}

def save():
 MAN['items']=items;MAN['completed_files']=len(items);MAN['updated_at']=datetime.now(timezone.utc).isoformat()
 (TASK/'PCM_原速准备清单.json').write_text(json.dumps(MAN,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

assert S['selected_count']==24 and len(S['files'])==24 and S['total_duration_seconds']==277.152
assert {(f['episode'],f['sequence']) for f in S['files'] if f['take']==2}=={(5,3),(6,1),(6,2),(6,9)}
MAN={'status':'PREPARING','selection_file':str(SEL),'selection_sha256':hashlib.sha256(SEL_BYTES).hexdigest(),'original_text_manifest_sha256':SRC_MAN_SHA,'scope':'Full continuous48kHz24bit mono PCM for24 accepted narration sources, only constant gain and required format conversion','source_count':24,'sample_rate':SR,'codec':'pcm_s24le','valid_bits_per_sample':24,'channels':1,'target_integrated_lufs':TARGET_I,'required_true_peak_ceiling_dbtp':TARGET_TP,'recipe_true_peak_ceiling_with_margin_dbtp':RECIPE_TP,'recipe':'gain_db=min(-16-source_integrated_lufs,-1.6-source_true_peak_dbtp); full continuous decode,48kHz resampling,constant volume only','not_applied':['denoise','gate','expander','compressor','limiter','equalizer','highpass','time_stretch','atempo','trim','silence_removal','tail_padding'],'Resolve_or_UI_operations':False,'downstream_instruction':'Gain baked into WAV. Import at0dB/100% speed; do not reapply loudness normalization or a cleanup/dynamics chain.','items':[]}
items=[];clocks=[]
for f in S['files']:
 base=f['basename'];src=Path(f['audio_file']);orig=Path(f['source_audio_file']);assert SHA(src)==SHA(orig)==f['sha256'];srcstat=src.stat();origstat=orig.stat()
 asrp=NARR/'ASR/raw_large-v3-turbo/narration'/f'{base}.json';A=json.loads(asrp.read_text(encoding='utf-8'));assert A['source_sha256']==f['sha256']
 lp=NARR/'ASR/measurements'/f'{base}_loudness.json';L=json.loads(lp.read_text(encoding='utf-8'));cached=L['result']['measured'];source_lufs=float(cached['input_i']);source_tp=float(cached['input_tp'])
 gain=round(min(TARGET_I-source_lufs,RECIPE_TP-source_tp),6);linear=10**(gain/20)
 probe_text,_=run([FP,'-v','error','-show_streams','-show_format','-of','json',str(src)]);probe=json.loads(probe_text);stream=[s for s in probe['streams'] if s['codec_type']=='audio'][0];native_sr=int(stream['sample_rate']);assert native_sr==24000 and stream['channels']==1
 native,decode_args=decode(src,rate=native_sr);reference,reference_args=decode(src,rate=SR,af=RESAMPLE);assert len(reference)==len(native)*2
 assert len(reference)==A['pcm_measurements']['decoded_sample_count']*3
 assert abs(len(reference)/SR-f['duration_seconds'])<1e-8
 outdir=OUT/f'第{f["episode"]:02d}集';outdir.mkdir(parents=True,exist_ok=True);dst=outdir/f'{base}_48k24bit_mono_原速_恒增益v1.wav';assert not dst.exists(),f'Unexpected existing output, refuse overwrite: {dst}'
 tmp=outdir/f'{base}_准备中.wav';assert not tmp.exists()
 recipe_args=[FF,'-hide_banner','-nostdin','-v','error','-xerror','-n','-i',str(src),'-map','0:a:0','-vn','-sn','-dn','-af',RESAMPLE+f',volume={gain:.6f}dB:precision=double','-ar',str(SR),'-ac','1','-c:a','pcm_s24le','-map_metadata','-1',str(tmp)]
 _,err=run(recipe_args);assert not err.strip(),err
 with wave.open(str(tmp),'rb') as w:
  assert w.getnchannels()==1 and w.getframerate()==SR and w.getsampwidth()==3
  outframes=w.getnframes()
 output,_=decode(tmp,rate=SR);assert len(output)==outframes==len(reference)
 output_levels=measure(tmp,base)
 if output_levels['true_peak_dbtp']>TARGET_TP:
  raise AssertionError(('TP safeguard requires smaller constant gain before publishing',base,gain,output_levels))
 corr=compare(reference,output,linear);assert corr['lag_output_relative_to_source_samples_48000']==0 and corr['zero_lag_normalized_correlation']>.9999999
 assert corr['maximum_abs_residual_vs_source_reference_times_gain']<2e-6
 assert abs(corr['estimated_constant_gain_db']-gain)<.0001
 assert np.max(np.abs(output))<1
 tmp.replace(dst)
 outprobe_text,_=run([FP,'-v','error','-show_streams','-show_format','-of','json',str(dst)]);outprobe=json.loads(outprobe_text);outs=[s for s in outprobe['streams'] if s['codec_type']=='audio'][0];assert outs['codec_name']=='pcm_s24le' and int(outs['sample_rate'])==SR and outs['channels']==1 and int(outs['bits_per_sample'])==24
 assert SHA(src)==SHA(orig)==f['sha256'] and src.stat().st_mtime_ns==srcstat.st_mtime_ns and orig.stat().st_mtime_ns==origstat.st_mtime_ns
 wordmap=[]
 for word in A['words']:
  start=float(word['start']);end=float(word['end']);wordmap.append({'word':word['word'],'source_asr_start_seconds':start,'source_asr_end_seconds':end,'output_start_sample_48000_floor':math.floor(start*SR+1e-9),'output_end_sample_48000_ceil':math.ceil(end*SR-1e-9),'timestamp_within_source_coverage':0<=start<=end<=outframes/SR})
 clock={'basename':base,'episode':f['episode'],'sequence':f['sequence'],'take':f['take'],'source_audio_path':str(src),'original_download_path':str(orig),'source_sha256':f['sha256'],'output_pcm_path':str(dst),'output_pcm_sha256':SHA(dst),'source_native_decoded_sample_rate':native_sr,'source_native_decoded_sample_count':len(native),'source_asr_decoded_sample_rate':A['pcm_measurements']['decoded_sample_rate'],'source_asr_decoded_sample_count':A['pcm_measurements']['decoded_sample_count'],'output_sample_rate':SR,'output_sample_count':outframes,'duration_seconds':outframes/SR,'source_start_seconds':0.0,'output_start_seconds':0.0,'source_to_output_rate':1.0,'measured_delay_samples_48000':0,'native_sample_to_output_sample_ratio':2,'asr_sample_to_output_sample_ratio':3,'mapping_formula':'output_time_seconds=source_ASR_time_seconds; output_sample=source_seconds*48000; native24k sample maps to2output samples, ASR16k sample to3output samples','source_clock_origin':'ffmpeg full decoded content sample0, matching the existing blind-ASR clock; not raw packet PTS','no_source_time_deleted_or_added':True,'asr_word_file':str(asrp),'asr_word_file_sha256':SHA(asrp),'words':wordmap}
 clocks.append(clock)
 row={'basename':base,'episode':f['episode'],'sequence':f['sequence'],'take':f['take'],'source_path':str(src),'original_download_path':str(orig),'source_sha256':f['sha256'],'source_asr_record':str(asrp),'source_loudness_evidence':{'path':str(lp),'sha256':SHA(lp),'source_identity_bound_by_ASR_record_sha256':True,'integrated_lufs':source_lufs,'true_peak_dbtp':source_tp,'measurement_only':True},'native_decoded_pcm':pcm_stats(native,native_sr),'reference_decoded_48000_pcm':pcm_stats(reference,SR),'gain_db':gain,'gain_linear':linear,'gain_limited_by':'true_peak_headroom' if RECIPE_TP-source_tp<TARGET_I-source_lufs else 'integrated_loudness_target','processing_arguments':recipe_args,'output_path':str(dst),'output_sha256':SHA(dst),'output_bytes':dst.stat().st_size,'output_sample_rate':SR,'output_sample_count':outframes,'output_channels':1,'output_codec':'pcm_s24le','output_bits_per_sample':24,'output_duration_seconds':outframes/SR,'output_measured_levels':output_levels,'output_pcm':pcm_stats(output,SR),'alignment':corr,'source_clock_map':{k:v for k,v in clock.items() if k!='words'},'source_files_unchanged':True,'full_continuous_coverage_preserved':True,'downstream_clip_gain_db':0.0,'downstream_playback_speed_percent':100,'bypass_additional_voice_processing':True}
 items.append(row);save();(TASK/'PCM_源时钟映射.json').write_text(json.dumps({'status':'BUILDING' if len(clocks)<24 else 'READY','items':clocks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'file':base,'gain_db':gain,'output_LUFS':output_levels['integrated_lufs'],'output_TP':output_levels['true_peak_dbtp'],'samples48k':outframes,'lag_samples':corr['lag_output_relative_to_source_samples_48000'],'completed':len(items)},ensure_ascii=False),flush=True)
assert len(items)==24 and sum(i['output_sample_count'] for i in items)==round(277.152*SR)
assert SEL.read_bytes()==SEL_BYTES and SHA(SRC_MAN)==SRC_MAN_SHA
MAN['status']='PASS_24_FULL_COVERAGE_PCM_READY';MAN['total_duration_seconds']=round(sum(i['output_duration_seconds'] for i in items),6);MAN['all24_alignment_lag_zero']=True;MAN['all24_true_peak_below_minus1point5']=True;MAN['all_sources_unchanged']=True;MAN['original_manifest_unchanged']=True;save()
with (TASK/'PCM_精确路径与源时钟映射.csv').open('w',encoding='utf-8-sig',newline='') as fp:
 fields=['basename','episode','sequence','take','source_path','output_path','gain_db','output_sample_rate','output_sample_count','output_duration_seconds'];writer=csv.DictWriter(fp,fieldnames=fields);writer.writeheader();writer.writerows({k:i[k] for k in fields} for i in items)
md='# 女版04—06原速PCM准备\n\n24份全覆盖WAV已完成，48kHz、24bit、mono。只作必要格式转换及恒定增益，没有降噪、门限、压缩、限幅、EQ、变速、剪时长或补时长。原下载、交付MP3及文本manifest均未修改。\n\n目标以-16LUFS起步，峰值保留至少1.5dBTP余量，实际配方采用-1.6dBTP安全目标，二者冲突取更小gain。响度分析过滤器仅输出null供量测，未写入媒体；WAV实际处理链只有重采样和固定volume。\n\n24份输出已逐一实测响度和真峰值，完整解码样本数与48k输出全覆盖时长一致；原解码波形与输出在共同48k时钟的全长归一化互相关延迟均为0，恒定增益残差符合24bit量化误差。原16kASR词时码仍为同一秒时钟：output_sample=source_seconds×48000，时间比例1，无偏移。映射不等于剪点验收，后续每个剪点仍需核对词头词尾与波形。\n\n导入Resolve时用原速100%、片段增益0dB并旁路重复语音处理，避免再次施加本次已烘焙增益。\n\n| 文件 | 固定gain(dB) | 实测LUFS | 实测dBTP | 秒 | 延迟样本 |\n|---|---:|---:|---:|---:|---:|\n'
for i in items:md+=f'| {i["basename"]} | {i["gain_db"]:.3f} | {i["output_measured_levels"]["integrated_lufs"]:.2f} | {i["output_measured_levels"]["true_peak_dbtp"]:.2f} | {i["output_duration_seconds"]:.3f} | 0 |\n'
md+=f'\n总时长{MAN["total_duration_seconds"]:.3f}秒。精确路径、SHA、样本数、配方和实测记录见PCM_原速准备清单.json，逐词原/输出样本时钟见PCM_源时钟映射.json。本次未操作Resolve/UI，没有声称完成剪辑或整条时间线听验。\n'
(TASK/'PCM_原速准备报告.md').write_text(md,encoding='utf-8')
print(json.dumps({'status':MAN['status'],'manifest':str(TASK/'PCM_原速准备清单.json'),'files':24,'seconds':MAN['total_duration_seconds'],'lufs_range':[min(i['output_measured_levels']['integrated_lufs'] for i in items),max(i['output_measured_levels']['integrated_lufs'] for i in items)],'max_true_peak':max(i['output_measured_levels']['true_peak_dbtp'] for i in items),'all_lag_samples_zero':True},ensure_ascii=False),flush=True)
