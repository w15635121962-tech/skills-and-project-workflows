"""Offline-only school score preparation: 13 editable stems plus exact PCM clocks.
FFmpeg skill audio.py is closest for a single ducked bed; per-item handles and a
bit-exact 25fps PCM source clock require the existing PyAV workflow here.
No Resolve import or connection is used.
"""
from pathlib import Path
from fractions import Fraction
from concurrent.futures import ThreadPoolExecutor
import argparse,json,sys,math,wave,hashlib,subprocess,time
import numpy as np
import av

REF=Path(__file__).resolve().parent
ROOT=REF.parents[1]
WORK=ROOT/'工作文件'
OUT=ROOT/'旁白与配乐/配乐每40秒'
CLOCK=OUT/'25帧时钟封装'
MEAS=OUT/'测量'
RAW=WORK/'参考与音乐/配乐原始截段'
SR,FPS,SPF=48000,25,1920
END=500.8;FRAMES=12520;TOTAL=FRAMES*SPF
PY='/Users/xuan/.local/share/promo-audio/venv/bin/python'
SKILL=Path('/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts')
VOICE=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_画面缓推与旁白气口精修_v14/旁白与混音/01_完整旁白_气口精修_v14_48k24.wav')
base=json.loads((REF/'music_cue_plan_v19.json').read_text())
tracks=base['tracks']
rows=[dict(c) for c in base['cues'][:11]]
rows.append({'cue':12,'track_id':'6','source_in_core_seconds':90.12,'section':'全员采访混剪：维持管弦色彩，低音量持续托住讲话','energy_1_to_5':3})
rows.append({'cue':13,'track_id':'3','source_in_core_seconds':91.72,'section':'总校长讲话与片尾：主题呼应，496.8秒附近进入录音舒缓收束','energy_1_to_5':3})
for n,c in enumerate(rows):
 a=n*40.;b=min((n+1)*40.,END);rs=max(0.,a-.8);re=min(END,b+.8)
 si=round(c['source_in_core_seconds']-(a-rs),5);so=round(c['source_in_core_seconds']+(re-a),5)
 t=tracks[c['track_id']]
 assert si>=0 and so<t['duration_seconds'],(n,si,so,t['duration_seconds'])
 c.update(file=t['file'],core_start_seconds=a,core_end_seconds=b,core_start_frame=round(a*25),core_end_frame=round(b*25),record_start_seconds=rs,record_end_seconds=re,record_start_frame=round(rs*25),record_end_frame_exclusive=round(re*25),source_in_with_handles_seconds=si,source_out_with_handles_seconds=so,source_in_with_handles_frame=round(si*25),duration_frames=round((re-rs)*25),duration_samples=round((re-rs)*SR),source_start_frame=0,source_end_frame_exclusive=round((re-rs)*25),track_index_recommended=3+n%2,clip_gain_db=0.0,baked_equal_power_overlap_seconds=1.6)
 c['target_base_lufs']=(-27.0 if n==0 else -31.0 if n>=11 else -30.0)
 label=Path(c['file']).stem
 c['wav_path']=str(OUT/f'{n+1:02d}_{int(a):03d}至{b:g}秒_{label}_配乐v19.wav')
 c['clock_container_path']=str(CLOCK/f'{n+1:02d}_{int(a):03d}至{b:g}秒_25fps_PCM_v19.mov')
 c['raw_cut_path']=str(RAW/f'{n+1:02d}_源范围48k24.wav')
 assert c['duration_samples']==c['duration_frames']*SPF
assert all(rows[i]['track_id']!=rows[i-1]['track_id'] for i in range(1,13))

parser=argparse.ArgumentParser();parser.add_argument('--dry-run',action='store_true');parser.add_argument('--resume',action='store_true');args=parser.parse_args()
for p in (OUT,CLOCK,MEAS,RAW):p.mkdir(parents=True,exist_ok=True)
plan={'status':'planned' if args.dry_run else 'running','fps':25,'sample_rate':SR,'pcm_bits':24,'duration_seconds':END,'duration_frames':FRAMES,'samples':TOTAL,'cue_count':13,'tracks':tracks,'cues':rows,'new_interview_range_seconds':[441.68,482.20],'principal_range_seconds':[482.20,496.80],'final_title_range_seconds':[496.8,500.8],'gain_contract':'All 13 stems include their own envelopes and crossfades. Append mediaType=2 only on alternating A3/A4, clip volume 0dB, without additional fades. Never add the full mixed bed simultaneously.'}
(REF/'music_cue_plan_v19_500p8_seconds.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
if args.dry_run:
 print(json.dumps({'status':'planned','duration':END,'cues':13,'sample_clock':SR,'frame_clock':25,'outputs':str(OUT),'native_ranges':[(c['record_start_frame'],c['record_end_frame_exclusive']) for c in rows]},ensure_ascii=False));sys.exit(0)

def decode24(raw):
 b=np.frombuffer(raw,np.uint8).reshape(-1,3).astype(np.int32);x=b[:,0]|b[:,1]<<8|b[:,2]<<16
 return np.where(x&0x800000,x-0x1000000,x).astype(np.int32).reshape(-1,2)
def encode24(z):
 x=np.asarray(z,np.int32).reshape(-1)
 return np.column_stack((x&255,(x>>8)&255,(x>>16)&255)).astype(np.uint8).tobytes()
def write24(p,z):
 p=Path(p)
 if p.exists() and not args.resume:raise AssertionError(f'Refusing existing output {p}')
 with wave.open(str(p),'wb') as h:
  h.setnchannels(2);h.setsampwidth(3);h.setframerate(SR)
  for i in range(0,len(z),SR*10):h.writeframesraw(encode24(z[i:i+SR*10]))
def quant(z):
 assert np.isfinite(z).all()
 y=np.rint(z*8388608).astype(np.int64)
 assert not np.any(y>8388607) and not np.any(y<-8388608),'Would clip new PCM'
 return y.astype(np.int32)
def decode_source(p):
 z=[]
 with av.open(str(p)) as c:
  stream=c.streams.audio[0];rs=av.AudioResampler(format='fltp',layout='stereo',rate=SR)
  for fr in c.decode(stream):
   for q in rs.resample(fr):z.append(q.to_ndarray().T.copy())
  for q in rs.resample(None):z.append(q.to_ndarray().T.copy())
 return np.concatenate(z).astype(np.float32)
def measure(p,log):
 if Path(log).exists() and args.resume:return json.loads(Path(log).read_text())['measured']
 proc=subprocess.run([PY,str(SKILL/'loudness.py'),str(p),'--measure-only','--json'],capture_output=True,text=True,check=True)
 a=json.loads(proc.stdout);assert a.get('status')=='completed' and 'measured' in a,a
 Path(log).write_text(json.dumps(a,ensure_ascii=False,indent=2));return a['measured']
def pcm_hash(p):
 sha=hashlib.sha256();n=0
 with wave.open(str(p)) as h:
  assert (h.getnchannels(),h.getsampwidth(),h.getframerate())==(2,3,SR)
  while True:
   b=h.readframes(SR*10)
   if not b:break
   sha.update(b);n+=len(b)//6
 return sha.hexdigest(),n

# Only long, clearly quiet voice gaps can receive a small slow musical release.
# Interview and slogan section receives constant duck; no weak-voice gate is used.
with wave.open(str(VOICE)) as h:
 voice=decode24(h.readframes(h.getnframes())).astype(np.float32)/8388608
block=4800;nb=len(voice)//block
rms=np.sqrt(np.mean(voice[:nb*block].reshape(nb,block,2)**2,axis=(1,2)))
db=20*np.log10(rms+1e-15);quiet=db<-39
bounds=np.flatnonzero(np.diff(np.r_[False,quiet,False])).reshape(-1,2)
# 100ms envelope grid; interpolation is smooth and never changes dialogue.
tgrid=np.arange(0,END+.100001,.1,dtype=np.float64)
release=np.zeros(len(tgrid),np.float64);release_rows=[]
for ia,ib in bounds:
 a=ia*.1;b=ib*.1
 if b-a<.79 or a<3 or b>433.68:continue
 left=a+.08;right=b-.16
 if right-left<.5:continue
 idx=np.flatnonzero((tgrid>=left)&(tgrid<=right))
 if len(idx)<3:continue
 x=(tgrid[idx]-left)/(right-left)
 bump=2.5*np.sin(np.pi*x)**2
 release[idx]=np.maximum(release[idx],bump)
 release_rows.append({'quiet_start':a,'quiet_end':b,'max_release_db':float(max(bump))})
# Gentle opening transient presence before narration enters; no rapid sidechain.
release[tgrid<=.2]=1.5
m=(tgrid>.2)&(tgrid<.37);release[m]=1.5*(.37-tgrid[m])/.17
# Hold all location speech and interviews at the planned low bed.
release[(tgrid>=433.68)&(tgrid<496.8)]=0
m=tgrid>=496.8;release[m]=np.minimum((tgrid[m]-496.8)/.6,1)*3.
(REF/'music_gain_envelope_plan_v19.json').write_text(json.dumps({'voice_reference':str(VOICE),'method':'100ms RMS below -39dBFS, only >=0.8s quiet runs after first3s; small smooth sin^2 swell within measured gap, return before speech; constant interview duck 433.68-496.8s','voice_rms_percentiles_dbfs':dict(zip(['p5','p20','p50','p80','p95'],[float(v) for v in np.percentile(db,[5,20,50,80,95])])),'release_windows':release_rows,'envelope_grid_seconds':tgrid.tolist(),'release_db':release.tolist(),'dialogue_samples_modified':False},ensure_ascii=False,indent=2))

cache={}
for c in rows:
 path=c['file']
 if path not in cache:
  cache[path]=decode_source(path)
  print('DECODED',Path(path).name,len(cache[path]),flush=True)
 start=round(c['source_in_with_handles_seconds']*SR);n=c['duration_samples'];src=cache[path][start:start+n]
 assert len(src)==n,(c['cue'],start,n,len(src))
 c['source_decoded_samples_total']=len(cache[path]);c['source_sample_start']=start;c['source_sample_end_exclusive']=start+n
 if not (Path(c['raw_cut_path']).exists() and args.resume):write24(c['raw_cut_path'],quant(src*.5))
 c['raw_measurement_pre_gain_db']=-6.020599913279624

def raw_measure(c):
 s=measure(c['raw_cut_path'],MEAS/f"{c['cue']:02d}_源截段响度.json")
 assert not s.get('silent',False);return c['cue'],s
with ThreadPoolExecutor(max_workers=3) as pool:
 rawstats=dict(pool.map(raw_measure,rows))
print('RAW_MEASUREMENTS_COMPLETE',flush=True)

mix=np.zeros((TOTAL,2),np.int64)
for c in rows:
 n=c['duration_samples'];rs=c['record_start_seconds'];re=c['record_end_seconds'];a=c['core_start_seconds'];b=c['core_end_seconds'];tm=rs+np.arange(n,dtype=np.float64)/SR
 source=cache[c['file']][c['source_sample_start']:c['source_sample_end_exclusive']]
 measured=float(rawstats[c['cue']]['input_i'])-c['raw_measurement_pre_gain_db'];gain=c['target_base_lufs']-measured
 local_release=np.interp(tm,tgrid,release)
 shape=np.ones(n,np.float64)
 if c['cue']>1:
  m=tm<a+.8;phase=np.clip((tm[m]-(a-.8))/1.6,0,1);shape[m]*=np.sin(phase*np.pi/2)
 else:
  m=tm<.08;shape[m]*=np.sin(np.clip(tm[m]/.08,0,1)*np.pi/2)
 if c['cue']<13:
  m=tm>b-.8;phase=np.clip((tm[m]-(b-.8))/1.6,0,1);shape[m]*=np.cos(phase*np.pi/2)
 else:
  m=tm>END-2.;phase=np.clip((tm[m]-(END-2.))/2.,0,1);shape[m]*=np.cos(phase*np.pi/2)**2
 curve=(10**((gain+local_release)/20))*shape
 z=quant(source.astype(np.float64)*curve[:,None]);write24(c['wav_path'],z)
 start=c['record_start_frame']*SPF;mix[start:start+n]+=z
 c['raw_loudness']=rawstats[c['cue']];c['normalization_gain_db']=round(gain,4)
 c['baked_release_db_max']=round(float(local_release.max()),4)
 c['peak_sample_dbfs']=round(float(20*np.log10(max(np.max(np.abs(z)),1)/8388608)),4)
 c['pcm_sha256'],c['samples_verified']=pcm_hash(c['wav_path'])
 assert c['samples_verified']==n
 print('WROTE_STEM',c['cue'],n,c['normalization_gain_db'],c['peak_sample_dbfs'],flush=True)
assert np.max(np.abs(mix))<8388607
full=OUT/'00_全片每40秒换曲_音乐总线_v19_48k24.wav'
write24(full,mix.astype(np.int32));fullsha,fullsamples=pcm_hash(full);assert fullsamples==TOTAL
# Quantized per-stem reconstruction is exactly equal to the full bus.
rebuild=np.zeros_like(mix)
for c in rows:
 with wave.open(c['wav_path']) as h:z=decode24(h.readframes(h.getnframes())).astype(np.int64)
 a=c['record_start_frame']*SPF;rebuild[a:a+len(z)]+=z
assert np.array_equal(rebuild,mix),'Independent 13-stem sum differs'
del rebuild


def clock_container(wav_path,mov_path):
 wav_path,mov_path=Path(wav_path),Path(mov_path)
 if mov_path.exists() and not args.resume:raise AssertionError(f'Refusing existing output {mov_path}')
 with wave.open(str(wav_path)) as h,av.open(str(mov_path),'w') as o:
  count=h.getnframes();assert count%SPF==0
  video=o.add_stream('libx264',rate=FPS);video.width=16;video.height=16;video.pix_fmt='yuv420p';video.options={'preset':'ultrafast','tune':'zerolatency','crf':'51','bf':'0'};video.codec_context.thread_count=1
  audio=o.add_stream('pcm_s24le',rate=SR);audio.layout='stereo';audio.time_base=Fraction(1,SR)
  o.metadata['comment']='PCM source clock carrier only. Append AUDIO ONLY (mediaType=2); do not place its black video.'
  o.metadata['title']=mov_path.stem
  black=np.zeros((16,16,3),np.uint8)
  for f in range(count//SPF):
   frame=av.VideoFrame.from_ndarray(black,format='rgb24');frame.pts=f;frame.time_base=Fraction(1,FPS)
   for packet in video.encode(frame):o.mux(packet)
   raw=h.readframes(SPF);assert len(raw)==SPF*6
   z=decode24(raw)
   af=av.AudioFrame.from_ndarray((z<<8).reshape(1,-1),format='s32',layout='stereo');af.sample_rate=SR;af.pts=f*SPF;af.time_base=Fraction(1,SR)
   for packet in audio.encode(af):o.mux(packet)
  for packet in video.encode():o.mux(packet)
  for packet in audio.encode():o.mux(packet)
 # Verify actual codec/clock/sample values with a fresh decode.
 sha=hashlib.sha256();ns=0;ptsrows=[]
 with av.open(str(mov_path)) as c:
  vs=c.streams.video[0];st=c.streams.audio[0]
  assert vs.average_rate==25 and vs.codec_context.width==16 and vs.codec_context.height==16
  assert vs.frames==count//SPF,(vs.frames,count//SPF)
  assert st.codec_context.name=='pcm_s24le' and st.codec_context.sample_rate==SR
  assert st.start_time==0
  assert st.duration==count
  for af in c.decode(st):
   assert af.format.name=='s32' and af.sample_rate==SR and len(af.layout.channels)==2
   if len(ptsrows)<3:ptsrows.append({'pts':af.pts,'samples':af.samples,'time_base':str(af.time_base)})
   assert af.pts==ns,(af.pts,ns)
   z=af.to_ndarray().reshape(-1,2)>>8;sha.update(encode24(z));ns+=len(z)
 expect,nwav=pcm_hash(wav_path);actual=sha.hexdigest();assert ns==nwav==count and actual==expect,(mov_path,ns,nwav,actual,expect)
 return {'path':str(mov_path),'size_bytes':mov_path.stat().st_size,'fps':25,'resolution':[16,16],'video_codec':'h264','audio_codec':'pcm_s24le','sample_rate':SR,'channels':2,'samples':count,'duration_seconds':count/SR,'video_frames':count//SPF,'wav_pcm_sha256':expect,'mov_decoded_pcm_sha256':actual,'pcm_values_bit_identical':True,'first_decoded_audio_packets':ptsrows,'source_start_time':0,'source_audio_only_import_required':True}

with ThreadPoolExecutor(max_workers=2) as pool:
 reports=list(pool.map(lambda c:clock_container(c['wav_path'],c['clock_container_path']),rows))
for c,r in zip(rows,reports):c['clock_container_verification']=r
print('13_CLOCK_CONTAINERS_VERIFIED',flush=True)
fullmov=CLOCK/'00_全片配乐音乐总线_25fps_PCM_v19.mov'
fullclock=clock_container(full,fullmov)
print('FULL_CLOCK_VERIFIED',flush=True)

def final_measure(c):return c['cue'],measure(c['wav_path'],MEAS/f"{c['cue']:02d}_实际成品响度.json")
with ThreadPoolExecutor(max_workers=3) as pool:finalstats=dict(pool.map(final_measure,rows))
for c in rows:c['actual_loudness']=finalstats[c['cue']]
fullstats=measure(full,MEAS/'00_全片实际配乐响度.json')
# 100ms RMS is a waveform check, not subjective audio review.
ms=mix.astype(np.float64)/8388608
bins=TOTAL//4800;energy=np.sqrt(np.mean(ms[:bins*4800].reshape(bins,4800,2)**2,axis=(1,2)));edb=20*np.log10(energy+1e-15)
active=edb[:-20];assert np.min(active)>-90,('unexpected music dropout',np.min(active))
# Envelope shape is continuous at each core boundary, crossfades overlap by exactly40f.
trans=[]
for c in rows[1:]:
 b=c['core_start_frame'];around=edb[round((b/25-.8)*10):round((b/25+.8)*10)];trans.append({'boundary_frame':b,'boundary_seconds':b/25,'overlap_frames':40,'window_rms_dbfs_min':float(np.min(around)),'window_rms_dbfs_max':float(np.max(around))})
plan.update(status='complete_offline_ready_for_native_import',cues=rows,music_bus_wav=str(full),music_bus_clock_container=str(fullmov),music_bus_pcm_sha256=fullsha,music_bus_clock_verification=fullclock,music_bus_actual_loudness=fullstats,music_bus_peak_sample_dbfs=float(20*np.log10(np.max(np.abs(mix))/8388608)),independent_stem_sum_bit_exact=True,transitions=trans,all_source_files_exist=True,audio_channels=2,all_native_source_start_frames=0,all_clip_gains_db=0.0,source_video_carriers_never_placed_on_timeline=True,normal_speed_subjective_audio_listening='unavailable; actual source/PCM/waveform/LUFS/true-peak checks performed; not claiming listening',resolve_objects_modified=False)
(OUT/'配乐每40秒_原生回装清单_v19.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
(REF/'music_cue_plan_v19_500p8_seconds.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
(OUT/'配乐实际响度与时钟核验_v19.json').write_text(json.dumps({'status':'passed','duration_seconds':END,'frames':FRAMES,'samples':TOTAL,'stem_count':13,'independent_stem_sum_bit_exact':True,'full_music_loudness':fullstats,'full_music_clock':fullclock,'stems':[{'cue':c['cue'],'path':c['wav_path'],'clock':c['clock_container_path'],'recordFrame':c['record_start_frame'],'endFrame':c['record_end_frame_exclusive'],'source_start_frame':0,'source_end_frame_exclusive':c['duration_frames'],'track_recommended':c['track_index_recommended'],'clip_gain_db':0,'actual_loudness':c['actual_loudness'],'sample_peak_dbfs':c['peak_sample_dbfs'],'pcm_bit_exact':True} for c in rows],'transitions':trans,'speech_pcm_modified':False,'look':'not needed: audio-only work; black16x16 carrier is intentional and never goes on video tracks'},ensure_ascii=False,indent=2))
print(json.dumps({'status':'passed','directory':str(OUT),'manifest':str(OUT/'配乐每40秒_原生回装清单_v19.json'),'stem_count':13,'total_seconds':END,'total_frames':FRAMES,'actual_loudness':fullstats,'peak_sample_dbfs':plan['music_bus_peak_sample_dbfs'],'bit_exact_14_pcm_containers':True,'clip_native_ranges':[(c['record_start_frame'],c['record_end_frame_exclusive'],c['duration_frames']) for c in rows]},ensure_ascii=False),flush=True)
