"""Offline opening score only, no Resolve connection or source modification.

Closest ffmpeg-skill routine: audio.py --music --duck. This job needs an
exact 25 fps PCM source carrier and a bit-exact old tail, so it reuses the
previously verified PyAV source-clock design and measures with loudness.py.
"""
from pathlib import Path
from fractions import Fraction
import argparse, hashlib, json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import soundfile as sf
import av

WORK=Path(__file__).resolve().parent
ROOT=WORK.parents[1]
OUT=ROOT/'旁白与配乐'
V19=ROOT.parent/'20261018_样片节奏与全员采访精修_v19'
V20=ROOT.parent/'20261018_开篇三素材与强配乐_v20'
PLAN=json.loads((V19/'工作文件/参考与音乐/music_cue_plan_v19.json').read_text())
OLD=ROOT.parent/'20261017_旁白精修/工作文件/audio_v2/BGM_01_书香与文脉_余量.wav'
VOICE=ROOT.parent/'20261017_画面缓推与旁白气口精修_v14/旁白与混音/01_完整旁白_气口精修_v14_48k24.wav'
PREVIOUS=V20/'旁白与配乐/01_开篇配乐_强起势至40秒后回归原版_v20_48k24.wav'
PY='/Users/xuan/.local/share/promo-audio/venv/bin/python'
SKILL=Path('/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts')
SR,FPS,SPF=48000,25,1920
CORE=40.;CUE_END=40.8;LO=round(39.2*SR);HI=round(CUE_END*SR)
FRAMES=2861;N=FRAMES*SPF
CANDIDATES=[{'track_id':'6','source_in_seconds':31.96,'rank':1,'choice':'主案_明亮管弦','target_lufs':-24.5},
            {'track_id':'7','source_in_seconds':52.20,'rank':2,'choice':'备选_坚定管弦','target_lufs':-24.5}]
p=argparse.ArgumentParser();p.add_argument('--dry-run',action='store_true');p.add_argument('--resume',action='store_true');args=p.parse_args()
for d in (WORK,OUT):d.mkdir(exist_ok=True,parents=True)
name='开篇配乐_明亮管弦强起势与气口_v21'
WAV=OUT/f'01_{name}_48k24.wav';MOV=OUT/f'01_{name}_25fps_PCM.mov'
meta={'status':'planned','name':name,'duration_seconds':114.44,'duration_frames':FRAMES,'samples':N,'sample_rate':SR,'fps':FPS,'pcm_bits':24,'channels':2,'candidates':CANDIDATES,'new_music_range_seconds':[0,40.8],'music_crossfade_seconds':[39.2,40.8],'original_bgm_after40p8':'PCM bit-identical; no normalization, limiter, or fade after this point','original_first_bgm':str(OLD),'voice_reference':str(VOICE),'wav_path':str(WAV),'container_path':str(MOV),'native_append':{'startFrame':0,'endFrame':2861,'recordFrame':0,'trackIndex':3,'mediaType':2},'native_clip_gain_db':0,'no_further_fades':True,'changes_interviews':False,'resolve_connected':False,'subjective_listening':'unavailable; waveform, energy, beat estimates, metadata and numerical loudness QC only'}
(OUT/'开篇配乐_制作计划_v21.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
if args.dry_run:
 print(json.dumps(meta,ensure_ascii=False));sys.exit(0)
if not args.resume:assert not WAV.exists() and not MOV.exists()

def read(p,start=0,stop=None):
 z,s=sf.read(p,dtype='int32',always_2d=True,start=start,stop=stop);assert s==SR and z.shape[1]==2;return z
def write(p,z):
 sf.write(p,z,SR,subtype='PCM_24')
def quant(z):
 q=np.rint(z*8388608).astype(np.int64)*256
 assert np.max(q)<2147483648 and np.min(q)>=-2147483648
 return q.astype(np.int32)
def decode(p):
 rows=[]
 with av.open(str(p)) as c:
  a=c.streams.audio[0];rs=av.AudioResampler(format='fltp',layout='stereo',rate=SR)
  for f in c.decode(a):
   for q in rs.resample(f):rows.append(q.to_ndarray().T.copy())
  for q in rs.resample(None):rows.append(q.to_ndarray().T.copy())
 return np.concatenate(rows).astype(np.float32)
def measure(p,label):
 f=WORK/f'{label}_实际测量.json'
 identity=hashlib.sha256(Path(p).read_bytes()).hexdigest()
 if f.exists() and args.resume:
  cached=json.loads(f.read_text())
  if cached.get('source_file_sha256')==identity:return cached['measured']
 r=subprocess.run([PY,str(SKILL/'loudness.py'),str(p),'--measure-only','--json'],capture_output=True,text=True,check=True)
 a=json.loads(r.stdout);assert a['status']=='completed' and 'input_i' in a['measured'];a['source_file_sha256']=identity;f.write_text(json.dumps(a,ensure_ascii=False,indent=2));return a['measured']
def enc24(z):
 x=(np.asarray(z,np.int32)>>8).reshape(-1)
 return np.column_stack((x&255,(x>>8)&255,(x>>16)&255)).astype(np.uint8).tobytes()
def hashpcm(z):return hashlib.sha256(enc24(z)).hexdigest()
def peak(z):return float(20*np.log10(np.max(np.abs(z.astype(np.int64)))/2147483648))

# Fresh byte identity and source metadata for all seven local music files.
verified=[]
sources=json.loads((V19/'工作文件/参考与音乐/music_files_verified_v19.json').read_text())
for row in sources:
 f=Path(row['file']);assert f.exists();s=hashlib.sha256(f.read_bytes()).hexdigest();assert s==row['sha256']
 with av.open(str(f)) as c:
  a=c.streams.audio[0];assert len(a.codec_context.layout.channels)==2
  d=float(c.duration/av.time_base);assert abs(d-row['duration'])<.02
 verified.append({**row,'fresh_sha256':s,'fresh_container_duration_seconds':d,'fresh_channels':len(a.codec_context.layout.channels)})
(WORK/'七首本地音乐_新鲜检索核验_v21.json').write_text(json.dumps(verified,ensure_ascii=False,indent=2))

voice=read(VOICE,stop=45*SR)
assert len(voice)==45*SR
vf=voice.astype(np.float64)/2147483648
vblocks=vf[:HI//4800*4800].reshape(-1,4800,2)
vrms=np.sqrt(np.mean(vblocks*vblocks,axis=(1,2)))
vdb=20*np.log10(vrms+1e-15)
quiet=vdb<-39
gaps=np.flatnonzero(np.diff(np.r_[False,quiet,False])).reshape(-1,2)
tm=np.arange(HI,dtype=np.float64)/SR
release=np.zeros(HI,np.float64);release_rows=[]
for ia,ib in gaps:
 a,b=ia*.1,ib*.1
 if b-a<.79 or a<3:continue
 left,right=a+.08,b-.16
 if right-left<.5:continue
 idx=np.flatnonzero((tm>=left)&(tm<=right));x=(tm[idx]-left)/(right-left)
 bump=1.75*np.sin(np.pi*x)**2
 release[idx]=np.maximum(release[idx],bump)
 release_rows.append({'quiet_start_seconds':a,'quiet_end_seconds':b,'release_db_max':float(max(bump)),'swell_start_seconds':left,'swell_end_seconds':right})
# A short pre-voice accent; settled before original narration at 0.37 s.
release[tm<=.17]=1.5
m=(tm>.17)&(tm<.37);release[m]=1.5*(1+np.cos(np.pi*(tm[m]-.17)/.2))/2
(WORK/'旁白气口_慢释放包络_v21.json').write_text(json.dumps({'voice_modified':False,'method':'Measured 100 ms voice RMS < -39 dBFS for >=0.8 s; 1.75 dB sin² release inside gap with 80 ms / 160 ms margins. Leading accent falls completely by 0.37 s. No syllable-triggered pumping.','release_windows':release_rows,'sample_rate':SR},ensure_ascii=False,indent=2))

candidate_rows=[];candidate_pcm={}
for item in CANDIDATES:
 t=PLAN['tracks'][item['track_id']];src=decode(t['file']);start=round(item['source_in_seconds']*SR)
 z=src[start:start+HI].astype(np.float64);assert len(z)==HI
 raw=WORK/f"候选{item['rank']}_{item['choice']}_原段48k24.wav"
 # half attenuation prevents source-decoding intersample over values from clipping.
 write(raw,quant(z*.5));rawstats=measure(raw,f"候选{item['rank']}_源40p8秒")
 raw_i=float(rawstats['input_i'])+6.020599913279624
 gain=item['target_lufs']-raw_i
 z*=10**((gain+release[:,None])/20)
 # The Mountain's opening forte is intrinsically stronger than its later part.
 # Let the complete first sentence stay around -24.4 LUFS, then recover slowly
 # over six seconds. This is one musical contour, not rapid speech ducking.
 intro_speech_trim=np.zeros(HI,np.float64)
 if item['rank']==1:
  intro_speech_trim[tm<12]=-1.2
  m=(tm>=12)&(tm<18)
  intro_speech_trim[m]=-1.2*(1+np.cos(np.pi*(tm[m]-12)/6))/2
  z*=10**(intro_speech_trim[:,None]/20)
 # Retain musical dynamics. Ten ms de-click, not a slow fade over first hit.
 m=tm<.01;z[m]*=np.sin(np.clip(tm[m]/.01,0,1)*np.pi/2)[:,None]
 # This envelope is baked only into new music. Original gets complementary sin return.
 x=np.arange(HI-LO,dtype=np.float64)/(HI-LO)
 z[LO:]*=np.cos(x*np.pi/2)[:,None]
 out=OUT/f"候选{item['rank']}_{item['choice']}_0至40p8秒_v21_48k24.wav"
 q=quant(z);write(out,q);actual=measure(out,f"候选{item['rank']}_成品40p8秒")
 # Compare the first narration sentence separately from 40-second averaged strength.
 first=WORK/f"候选{item['rank']}_音乐前12秒核验.wav";write(first,q[:12*SR]);firststats=measure(first,f"候选{item['rank']}_前12秒")
 beats=json.loads(Path(t['analysis_file']).read_text())['beat_seconds'];nearest=min(beats,key=lambda b:abs(b-item['source_in_seconds']))
 relbeats=[round(b-item['source_in_seconds'],6) for b in beats if item['source_in_seconds']<=b<item['source_in_seconds']+CUE_END]
 nearframes=sorted(set(round(b*FPS) for b in relbeats))
 eb=q[:HI//4800*4800].astype(np.float64).reshape(-1,4800,2)/2147483648
 mdb=20*np.log10(np.sqrt(np.mean(eb*eb,axis=(1,2)))+1e-15)
 active=vdb>-30;diff=vdb[active]-mdb[active]
 row={**item,'file':t['file'],'title':t['title'],'artist':t['artist'],'source_in_samples':start,'source_out_samples_exclusive':start+HI,'source_out_seconds':item['source_in_seconds']+CUE_END,'estimated_bpm':t['estimated_bpm'],'source_metadata_description':t.get('source_description_observed',''),'source_url':t.get('source_url'),'license_url':t.get('license_url'),'content_id_registered':t.get('content_id_registered'),'nearest_estimated_source_beat_seconds':nearest,'distance_from_entry_seconds':nearest-item['source_in_seconds'],'relative_estimated_beats_seconds':relbeats,'estimated_beat_frames_25fps':nearframes,'beat_boundaries_not_human_verified':True,'raw_loudness_before_gain':raw_i,'gain_db':gain,'slow_first_sentence_trim_db':-1.2 if item['rank']==1 else 0,'slow_first_sentence_trim_hold_seconds':[0,12] if item['rank']==1 else None,'slow_first_sentence_trim_recovery_seconds':[12,18] if item['rank']==1 else None,'actual_loudness':actual,'actual_first12_loudness':firststats,'wav_path':str(out),'sample_peak_dbfs':peak(q),'voice_active_RMS_minus_music_RMS_db_percentiles':dict(zip(['p05','p25','p50','p75','p95'],[float(a) for a in np.percentile(diff,[5,25,50,75,95])]))}
 candidate_rows.append(row);candidate_pcm[item['rank']]=q
 print(json.dumps({'candidate':item['rank'],'actual':actual,'first12':firststats,'voice_music_margin':row['voice_active_RMS_minus_music_RMS_db_percentiles']},ensure_ascii=False),flush=True)

# Assemble only the first native BGM source; the rest is exactly original PCM.
old=read(OLD);assert sf.info(OLD).subtype=='PCM_24'
old_native_end=round(2747/24*SR);assert not np.any(old[N:old_native_end])
y=old[:N].copy();new=candidate_pcm[1];y[:LO]=new[:LO]
ph=np.arange(HI-LO,dtype=np.float64)/(HI-LO)
mixed=new[LO:HI].astype(np.float64)/2147483648+(old[LO:HI].astype(np.float64)/2147483648)*np.sin(ph*np.pi/2)[:,None]
y[LO:HI]=quant(mixed)
write(WAV,y);again=read(WAV);assert np.array_equal(y,again)
assert np.array_equal(y[HI:],old[HI:N])

with av.open(str(MOV),'w') as o:
 vs=o.add_stream('libx264',rate=FPS);vs.width=16;vs.height=16;vs.pix_fmt='yuv420p';vs.options={'preset':'ultrafast','tune':'zerolatency','crf':'51','bf':'0'};vs.codec_context.thread_count=1
 ast=o.add_stream('pcm_s24le',rate=SR);ast.layout='stereo';ast.time_base=Fraction(1,SR)
 o.metadata['comment']='25fps PCM clock only. Append AUDIO ONLY mediaType2 on A3 0..2861; never use black video. After40.8s old BGM PCM is unchanged.';o.metadata['title']=name
 black=np.zeros((16,16,3),np.uint8)
 for f in range(FRAMES):
  vf1=av.VideoFrame.from_ndarray(black,format='rgb24');vf1.pts=f;vf1.time_base=Fraction(1,FPS)
  for pk in vs.encode(vf1):o.mux(pk)
  af=av.AudioFrame.from_ndarray(y[f*SPF:(f+1)*SPF].reshape(1,-1),format='s32',layout='stereo');af.sample_rate=SR;af.pts=f*SPF;af.time_base=Fraction(1,SR)
  for pk in ast.encode(af):o.mux(pk)
 for pk in vs.encode():o.mux(pk)
 for pk in ast.encode():o.mux(pk)
ns=0;sha=hashlib.sha256()
with av.open(str(MOV)) as c:
 vs=c.streams.video[0];st=c.streams.audio[0]
 assert vs.average_rate==25 and vs.frames==FRAMES and vs.codec_context.width==16 and vs.codec_context.height==16
 assert st.codec_context.name=='pcm_s24le' and st.duration==N and st.start_time==0
 for af in c.decode(st):
  assert af.pts==ns and af.format.name=='s32' and len(af.layout.channels)==2
  zz=af.to_ndarray().reshape(-1,2);sha.update(enc24(zz));ns+=len(zz)
assert ns==N and sha.hexdigest()==hashpcm(y)

# Actual direct 45-second sum: narration samples untouched, no common bus gain.
mix64=voice.astype(np.int64)+y[:45*SR].astype(np.int64)
assert np.max(mix64)<2147483648 and np.min(mix64)>=-2147483648
mix=mix64.astype(np.int32);MIX=OUT/'开篇配乐与40秒衔接_原旁白试听_v21.wav';write(MIX,mix)
prev=read(PREVIOUS,stop=45*SR)
oldcut=WORK/'v20音乐前40p8秒核验.wav';write(oldcut,prev[:HI]);newcut=WORK/'v21音乐前40p8秒含回接核验.wav';write(newcut,y[:HI])
prevfirst=WORK/'v20音乐前12秒核验.wav';write(prevfirst,prev[:12*SR])
jobs=[(WAV,'原生音乐源114p44秒'),(MIX,'原旁白加新音乐45秒'),(oldcut,'v20前40p8秒'),(newcut,'v21前40p8秒含回接'),(prevfirst,'v20音乐前12秒')]
with ThreadPoolExecutor(max_workers=3) as pool:measurements=dict(pool.map(lambda x:(x[1],measure(*x)),jobs))
assert float(measurements['原旁白加新音乐45秒']['input_tp'])<0
assert float(measurements['原生音乐源114p44秒']['input_tp'])<0
delta=float(measurements['v21前40p8秒含回接']['input_i'])-float(measurements['v20前40p8秒']['input_i'])
meta.update(status='passed_ready_for_native_audio_only_import',selected_candidate=candidate_rows[0],candidates=candidate_rows,actual_loudness=measurements['原生音乐源114p44秒'],opening_loudness=measurements['v21前40p8秒含回接'],opening_loudness_increase_from_v20_LU=delta,opening_v20_loudness=measurements['v20前40p8秒'],first12_music_LU_increase_from_v20=float(candidate_rows[0]['actual_first12_loudness']['input_i'])-float(measurements['v20音乐前12秒']['input_i']),mix_first45_loudness=measurements['原旁白加新音乐45秒'],mix_first45_sample_peak_dbfs=peak(mix),mix_first45_wav_path=str(MIX),narration_samples_modified=False,mix_uses_direct_unprocessed_stereo_sum=True,sample_peak_dbfs=peak(y),original_bgm_after40p8_pcm_bit_identical=True,original_preserved_after40p8_samples=N-HI,old_native_fractional_tail_digital_zero=True,omitted_old_native_subframe_tail={'seconds':[114.44,2747/24],'count':old_native_end-N,'all_digital_zero':True},entire_new_wav_pcm_sha256=hashpcm(y),container_decoded_pcm_sha256=sha.hexdigest(),container_pcm_bit_identical_to_wav=True,container_video={'fps':25,'frames':FRAMES,'resolution':[16,16],'codec':'h264','never_place_on_picture_track':True},new_cue_before39p2_pcm_bit_identical=True,limiter_added=False,common_trim_db=0,voice_release_windows=release_rows,measurements=measurements)
(OUT/'开篇配乐_原生回装清单_v21.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
(WORK/'音乐候选_实测比较_v21.json').write_text(json.dumps(candidate_rows,ensure_ascii=False,indent=2))
print(json.dumps({'status':meta['status'],'manifest':str(OUT/'开篇配乐_原生回装清单_v21.json'),'new_music_actual':meta['opening_loudness'],'increase_vs_v20_LU':delta,'first12_increase_LU':meta['first12_music_LU_increase_from_v20'],'mix_peak_dbfs':meta['mix_first45_sample_peak_dbfs'],'mix_tp':meta['mix_first45_loudness']['input_tp'],'tail_exact':True,'carrier_pcm_exact':True,'files':[str(WAV),str(MOV),str(MIX)]},ensure_ascii=False),flush=True)
