"""Offline PCM sum from current native audio item positions, including subframes.
Not a native Fairlight render; no undocumented bus processing is inferred.
No Resolve modules imported or connected.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,hashlib,wave,subprocess,sys,math
import numpy as np
import av

ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/'工作文件';OUT=ROOT/'旁白与配乐';TRACKS=OUT/'独立音轨重建';LOG=OUT/'完整混音测量';PRE=OUT/'试听'
for p in (TRACKS,LOG,PRE):p.mkdir(parents=True,exist_ok=True)
NATIVE=WORK/'native_audio_applied_v19.json';native_bytes=NATIVE.read_bytes();native=json.loads(native_bytes)
assert native['status']=='passed_native_positions_and_source_clock' and native['duration_frames']==12520 and native['duration_seconds']==500.8
music=json.loads((OUT/'配乐每40秒/配乐每40秒_原生回装清单_v19.json').read_text())
interviews=json.loads((OUT/'采访原生时钟/五人采访_25fps原生回装清单_v19.json').read_text())
SR,FPS,SPF=48000,25,1920;TOTAL=12520*1920
OLDROOT=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_画面缓推与旁白气口精修_v14')
voicemov=str(OLDROOT/'旁白与混音/04_旁白精修_25帧无损PCM时钟封装_v14.mov')
voicewav=OLDROOT/'旁白与混音/01_完整旁白_气口精修_v14_48k24.wav'
paths={voicemov:{'wav':str(voicewav),'kind':'original narration','previous_bit_exact_verification':str(OLDROOT/'工作文件/pcm_clock_container_probe_v14.json')}}
for c in music['cues']:paths[c['clock_container_path']]={'wav':c['wav_path'],'expected_pcm_hash':c['pcm_sha256'],'kind':'new music cue','cue':c['cue']}
for c in interviews['interviews']:paths[c['container_path']]={'wav':c['full_source_stereo_wav'],'expected_pcm_hash':c['clock_container_verification']['wav_pcm_sha256'],'kind':'interview','speaker':c['speaker_key']}

def dec24(raw):
 b=np.frombuffer(raw,np.uint8).reshape(-1,3).astype(np.int32);x=b[:,0]|b[:,1]<<8|b[:,2]<<16
 return np.where(x&0x800000,x-0x1000000,x).astype(np.int32).reshape(-1,2)
def enc24(z):
 v=np.asarray(z,np.int32).reshape(-1)
 return np.column_stack((v&255,(v>>8)&255,(v>>16)&255)).astype(np.uint8).tobytes()
def sha_wav(p):
 sha=hashlib.sha256()
 with wave.open(str(p)) as h:
  assert (h.getnchannels(),h.getsampwidth(),h.getframerate())==(2,3,SR),(p,h.getparams())
  n=h.getnframes()
  while True:
   b=h.readframes(SR*10)
   if not b:break
   sha.update(b)
 return sha.hexdigest(),n

def source_check(pair):
 mov,d=pair;p=Path(d['wav']);assert p.exists() and Path(mov).exists()
 want,n=sha_wav(p)
 if d.get('expected_pcm_hash'):assert want==d['expected_pcm_hash'],(p,'PCM changed after prior check')
 sha=hashlib.sha256();ns=0
 with av.open(mov) as c:
  st=c.streams.audio[0];assert st.codec_context.name=='pcm_s24le' and st.codec_context.sample_rate==SR
  for f in c.decode(st):
   assert f.format.name=='s32' and len(f.layout.channels)==2
   z=f.to_ndarray().reshape(-1,2)>>8;sha.update(enc24(z));ns+=len(z)
 assert sha.hexdigest()==want and n==ns,(p,n,ns,'MOV PCM differs')
 return mov,{**d,'wav_pcm_sha256':want,'mov_decoded_pcm_sha256':sha.hexdigest(),'source_n_samples':n,'pcm_bit_exact':True}
with ThreadPoolExecutor(max_workers=2) as pool:checked=dict(pool.map(source_check,paths.items()))
print('CONTAINER_PCM_SOURCE_CHECKS_PASS',len(checked),flush=True)

items=[];handles={};source_hashes={}
for i in native['native_audio_items']:
 if not i.get('enabled',True):continue
 p=i['path'];wav=Path(paths[p]['wav']) if p in paths else Path(p)
 assert wav.suffix.lower()=='.wav' and wav.exists(),wav
 h=handles.get(str(wav))
 if h is None:
  h=wave.open(str(wav),'rb');assert (h.getnchannels(),h.getsampwidth(),h.getframerate())==(2,3,SR)
  handles[str(wav)]=h
 a=round(i['record_start_frame']/FPS*SR);b=round(i['record_end_frame_exclusive']/FPS*SR);s=round(i['source_start_seconds']*SR)
 assert 0<=a<b<=TOTAL and 0<=s and s+b-a<=h.getnframes(),(i,s,b-a,h.getnframes())
 mapping=json.loads(i['audio_mapping']);assert mapping['track_mapping']['1']['channel_idx']==[1,2] and not mapping['track_mapping']['1']['mute']
 items.append({**i,'wav_path':str(wav),'record_start_sample':a,'record_end_sample_exclusive':b,'duration_samples':b-a,'source_start_sample':s,'source_end_sample_exclusive':s+b-a,'clip_gain_db':0,'samples_per_frame':1920,'no_resampling':True})
for tr in range(1,5):
 its=sorted((x for x in items if x['track']==tr),key=lambda x:x['record_start_sample'])
 assert all(a['record_end_sample_exclusive']<=b['record_start_sample'] for a,b in zip(its,its[1:])),('unexpected same-track overlap',tr)
sec=next(x for x in items if x['name']=='全员采访原声｜书记');group=next(x for x in items if '群体现场口号' in x['name'])
assert sec['record_start_sample']==group['record_end_sample_exclusive']
assert sec['source_start_sample']==1104560 and sec['record_start_sample']==21201200,(sec['source_start_sample'],sec['record_start_sample'])
assert sec['source_start_seconds']<23.04
print('NATIVE_SAMPLE_CLOCK_PASS',len(items),'secretary',sec['record_start_sample'],sec['source_start_sample'],flush=True)

track_paths={n:TRACKS/f'A{n}_原生范围精确重建_v19_48k24.wav' for n in range(1,5)}
voice=OUT/'02_讲话总线_完整旁白与全员采访_v19.wav';full=OUT/'03_完整混音_样片节奏与全员采访_v19.wav'
files={**{f'A{n}':p for n,p in track_paths.items()},'speech':voice,'mix':full}
outs={}
for key,p in files.items():
 assert not p.exists(),('Refusing existing output',p)
 h=wave.open(str(p),'wb');h.setnchannels(2);h.setsampwidth(3);h.setframerate(SR);outs[key]=h
peaks={k:0 for k in files};clipped={k:0 for k in files}
for pos in range(0,TOTAL,SR*10):
 end=min(TOTAL,pos+SR*10);n=end-pos
 blocks={tr:np.zeros((n,2),np.int64) for tr in range(1,5)}
 for i in items:
  a=max(pos,i['record_start_sample']);b=min(end,i['record_end_sample_exclusive'])
  if b<=a:continue
  off=i['source_start_sample']+a-i['record_start_sample'];h=handles[i['wav_path']];h.setpos(off);raw=h.readframes(b-a)
  assert len(raw)==(b-a)*6
  blocks[i['track']][a-pos:b-pos]+=dec24(raw)
 speech=blocks[1]+blocks[2];mix=speech+blocks[3]+blocks[4]
 data={**{f'A{tr}':z for tr,z in blocks.items()},'speech':speech,'mix':mix}
 for key,z in data.items():
  peaks[key]=max(peaks[key],int(np.max(np.abs(z))));clipped[key]+=int(np.count_nonzero((z>8388607)|(z<-8388608)))
  assert clipped[key]==0,('mix would clip; need common trim and native matching instruction',key,peaks[key])
  outs[key].writeframesraw(enc24(z))
for h in outs.values():h.close()
for h in handles.values():h.close()
print('TRACKS_AND_FULL_MIX_WRITTEN',peaks,flush=True)

# Verify source slices are present verbatim in their independent native track WAV.
for i in items:
 n=i['duration_samples'];sw=wave.open(i['wav_path'],'rb');tw=wave.open(str(track_paths[i['track']]),'rb')
 hs,ht=hashlib.sha256(),hashlib.sha256();sw.setpos(i['source_start_sample']);tw.setpos(i['record_start_sample'])
 left=n
 while left:
  take=min(left,SR*10);bs=sw.readframes(take);bt=tw.readframes(take);assert bs==bt,(i['name'],'PCM source slice mismatch');hs.update(bs);ht.update(bt);left-=take
 sw.close();tw.close();i['selected_source_pcm_sha256']=hs.hexdigest();i['native_track_slice_pcm_sha256']=ht.hexdigest();i['source_slice_bit_exact']=True
# Independent sum from written 4 tracks, plus music-only comparison to prepared bus.
ins={tr:wave.open(str(p),'rb') for tr,p in track_paths.items()};sp=wave.open(str(voice),'rb');mh=wave.open(str(full),'rb');bh=wave.open(music['music_bus_wav'],'rb')
for pos in range(0,TOTAL,SR*10):
 n=min(TOTAL-pos,SR*10);z={tr:dec24(h.readframes(n)).astype(np.int64) for tr,h in ins.items()}
 assert enc24(z[1]+z[2])==sp.readframes(n)
 assert enc24(z[3]+z[4])==bh.readframes(n),'Native music differs from new music bus'
 assert enc24(sum(z.values()))==mh.readframes(n),'Independent 4-track sum differs'
for h in [*ins.values(),sp,mh,bh]:h.close()
print('ALL_PCM_SLICE_AND_INDEPENDENT_SUM_VERIFIED',flush=True)

# Auditions use exact sections, no new normalization, compression or limiting.
auditions=[]
for a,b,name in [(0.,40.,'04_开篇试听_0至40秒_v19.wav'),(438.68,500.8,'05_全员采访与尾声试听_438p68至500p8秒_v19.wav')]:
 a_s,b_s=round(a*SR),round(b*SR);p=PRE/name;assert not p.exists()
 with wave.open(str(full),'rb') as h:
  h.setpos(a_s);raw=h.readframes(b_s-a_s);assert len(raw)==(b_s-a_s)*6
 with wave.open(str(p),'wb') as h:h.setnchannels(2);h.setsampwidth(3);h.setframerate(SR);h.writeframes(raw)
 auditions.append({'path':str(p),'source_start_seconds':a,'source_end_seconds':b,'duration_seconds':b-a,'sample_start':a_s,'sample_end_exclusive':b_s,'pcm_sha256':hashlib.sha256(raw).hexdigest(),'exact_range_from_current_mix':True})

SKILL=Path('/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts');PY='/Users/xuan/.local/share/promo-audio/venv/bin/python'
def measure(pair):
 key,p=pair;proc=subprocess.run([PY,str(SKILL/'loudness.py'),str(p),'--measure-only','--json'],capture_output=True,text=True,check=True);a=json.loads(proc.stdout);assert a['status']=='completed'
 (LOG/(key+'_实际响度.json')).write_text(json.dumps(a,ensure_ascii=False,indent=2));return key,a['measured']
with ThreadPoolExecutor(max_workers=3) as pool:measured=dict(pool.map(measure,files.items()))
assert float(measured['mix']['input_tp'])<0,'True peak would clip; correspondingly trim native mix before delivery'
assert NATIVE.read_bytes()==native_bytes,'Native input manifest changed mid reconstruction'
report={'status':'passed_fresh_native_source_range_reconstruction','native_manifest':str(NATIVE),'native_manifest_sha256':hashlib.sha256(native_bytes).hexdigest(),'fps':FPS,'duration_frames':12520,'duration_seconds':500.8,'sample_rate':SR,'samples':TOTAL,'channels':2,'bit_depth':24,'current_native_audio_items_reconstructed':len(items),'source_containers_and_wavs_pcm_bit_exact':checked,'all_source_slices_bit_exact_in_independent_track':True,'independent_four_track_sum_bit_exact_to_full_mix':True,'independent_A1_A2_sum_bit_exact_to_speech_bus':True,'native_A3_A4_sum_bit_exact_to_prepared_music_bus':True,'secretary_actual_subframe_clock':{'record_start_frame':sec['record_start_frame'],'record_start_sample':sec['record_start_sample'],'source_start_seconds':sec['source_start_seconds'],'source_start_sample':sec['source_start_sample'],'retains_pre_speech_silence_before_23p04':True,'group_end_equals_secretary_start_sample':True},'track_files':{k:str(v) for k,v in track_paths.items()},'speech_bus':str(voice),'full_mix':str(full),'actual_loudness':measured,'sample_peaks_dbfs':{k:20*math.log10(max(v,1)/8388608) for k,v in peaks.items()},'samples_clipped':clipped,'common_trim_db':0.0,'limiter_added':False,'native_gain_change_required':False,'auditions':auditions,'items':items,'render_method':'Offline sample-accurate 0dB stereo PCM sum of actual native audio item ranges; not a native Fairlight render. Does not assert undocumented Fairlight bus/plugin processing.','audio_subjective_listening':'unavailable; source-clock/PCM/loudness/true-peak/waveform verification only','old_complete_mix_reused':False,'resolve_connected_or_modified':False,'look':'not needed; audio-only reconstruction'}
for key,p in files.items():
 s,n=sha_wav(p);assert n==TOTAL
 report.setdefault('output_pcm_sha256',{})[key]=s
(WORK/'fresh_native_mix_qa_v19.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'status':'passed','full_mix':str(full),'speech_bus':str(voice),'items':len(items),'samples':TOTAL,'duration':500.8,'actual_mix_loudness':measured['mix'],'sample_peak_dbfs':report['sample_peaks_dbfs']['mix'],'trim_db':0,'native_gain_change_required':False,'auditions':auditions,'qa':str(WORK/'fresh_native_mix_qa_v19.json')},ensure_ascii=False),flush=True)
