"""Offline v20 opening-only score replacement. No Resolve access.
Use existing new cue fade, add original bed equal-power return only39.2-40.8s;
copy all original samples after40.8s exactly. Proven clock carrier via PyAV.
"""
from pathlib import Path
from fractions import Fraction
import argparse,json,sys,hashlib,wave,subprocess
import soundfile as sf
import numpy as np
import av
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'旁白与配乐';OUT.mkdir(exist_ok=True)
OLD=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_旁白精修/工作文件/audio_v2/BGM_01_书香与文脉_余量.wav')
MP=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261018_样片节奏与全员采访精修_v19/旁白与配乐/配乐每40秒/配乐每40秒_原生回装清单_v19.json')
mc=json.loads(MP.read_text())['cues'][0];NEW=Path(mc['wav_path'])
SR=48000;FPS=25;SPF=1920;N=2861*SPF;DURATION=114.44
p=argparse.ArgumentParser();p.add_argument('--dry-run',action='store_true');args=p.parse_args()
name='开篇配乐_强起势至40秒后回归原版_v20'
WAV=OUT/('01_'+name+'_48k24.wav');MOV=OUT/('01_'+name+'_25fps_PCM.mov')
a,sa=sf.read(OLD,dtype='int32',always_2d=True);b,sb=sf.read(NEW,dtype='int32',always_2d=True)
assert sa==sb==SR and a.shape[1]==b.shape[1]==2
assert sf.info(OLD).subtype==sf.info(NEW).subtype=='PCM_24'
lo,hi=round(39.2*SR),round(40.8*SR);old_native_end=round(2747/24*SR)
assert len(a)>=old_native_end and len(b)==hi
assert not np.any(a[N:old_native_end]),'Omitted old native subframe tail is NOT digital zero'
plan={'status':'planned','name':name,'original_first_bgm':str(OLD),'new_strong_opening_cue':str(NEW),'fps':25,'sample_rate':SR,'channels':2,'pcm_bits':24,'duration_seconds':DURATION,'duration_frames':2861,'samples':N,'crossfade_seconds':[39.2,40.8],'crossfade_samples':[lo,hi],'before39p2':'new strong cue only','39p2_to40p8':'existing new cue contains cos fade-out; add original bed sin fade-in over same1.6s window','after40p8':'copy original first BGM PCM exactly','omitted_old_native_subframe_tail':{'seconds':[DURATION,2747/24],'samples':[N,old_native_end],'count':old_native_end-N,'all_digital_zero':True,'nonzero_values':0},'source_wav_padding_after_old_native_end':{'samples':len(a)-old_native_end,'all_digital_zero':bool(not np.any(a[old_native_end:]))},'wav_path':str(WAV),'container_path':str(MOV),'native_append':{'startFrame':0,'endFrame':2861,'recordFrame':0,'trackIndex':3,'mediaType':2},'source_start_frame':0,'source_end_frame_exclusive':2861,'record_start_frame':0,'record_end_frame_exclusive':2861,'native_clip_gain_db':0,'no_further_fades':True,'changes_interviews':False,'modifies_other_bgm_items':False,'resolve_connected':False}
(OUT/'开篇配乐_制作计划_v20.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
if args.dry_run:
 print(json.dumps(plan,ensure_ascii=False));sys.exit(0)
assert not WAV.exists() and not MOV.exists()
y=a[:N].copy();y[:lo]=b[:lo]
phase=np.arange(hi-lo,dtype=np.float64)/(hi-lo)
mixed=b[lo:hi].astype(np.float64)+a[lo:hi].astype(np.float64)*np.sin(phase*np.pi/2)[:,None]
q=np.rint(mixed/256).astype(np.int64)*256
assert np.max(q)<2147483648 and np.min(q)>=-2147483648,'crossfade would clip'
y[lo:hi]=q.astype(np.int32)
sf.write(WAV,y,SR,subtype='PCM_24')
z,sz=sf.read(WAV,dtype='int32',always_2d=True)
assert np.array_equal(y,z) and sz==SR
assert np.array_equal(z[:lo],b[:lo])
assert np.array_equal(z[hi:],a[hi:N]),'Old tail PCM not exact'

def enc24(s32):
 x=(np.asarray(s32,np.int32)>>8).reshape(-1)
 return np.column_stack((x&255,(x>>8)&255,(x>>16)&255)).astype(np.uint8).tobytes()
sha=hashlib.sha256(enc24(y)).hexdigest()
with av.open(str(MOV),'w') as o:
 vs=o.add_stream('libx264',rate=FPS);vs.width=16;vs.height=16;vs.pix_fmt='yuv420p';vs.options={'preset':'ultrafast','tune':'zerolatency','crf':'51','bf':'0'};vs.codec_context.thread_count=1
 ast=o.add_stream('pcm_s24le',rate=SR);ast.layout='stereo';ast.time_base=Fraction(1,SR)
 o.metadata['comment']='Opening-only music source clock. Append AUDIO ONLY mediaType2 to native0..2861. Original BGM PCM unchanged after40.8s.'
 o.metadata['title']=name;black=np.zeros((16,16,3),np.uint8)
 for f in range(2861):
  vf=av.VideoFrame.from_ndarray(black,format='rgb24');vf.pts=f;vf.time_base=Fraction(1,FPS)
  for pk in vs.encode(vf):o.mux(pk)
  af=av.AudioFrame.from_ndarray(y[f*SPF:(f+1)*SPF].reshape(1,-1),format='s32',layout='stereo');af.sample_rate=SR;af.pts=f*SPF;af.time_base=Fraction(1,SR)
  for pk in ast.encode(af):o.mux(pk)
 for pk in vs.encode():o.mux(pk)
 for pk in ast.encode():o.mux(pk)
ns=0;hs=hashlib.sha256()
with av.open(str(MOV)) as c:
 vs=c.streams.video[0];st=c.streams.audio[0]
 assert vs.average_rate==25 and vs.frames==2861 and vs.codec_context.width==16 and vs.codec_context.height==16
 assert st.codec_context.name=='pcm_s24le' and st.codec_context.sample_rate==SR and st.duration==N and st.start_time==0
 for f in c.decode(st):
  assert f.pts==ns and f.format.name=='s32' and len(f.layout.channels)==2
  zz=f.to_ndarray().reshape(-1,2);hs.update(enc24(zz));ns+=len(zz)
assert ns==N and hs.hexdigest()==sha
SKILL='/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts/loudness.py';PY='/Users/xuan/.local/share/promo-audio/venv/bin/python'
proc=subprocess.run([PY,SKILL,str(WAV),'--measure-only','--json'],capture_output=True,text=True,check=True);measure=json.loads(proc.stdout)
(OUT/'开篇配乐_实际响度_v20.json').write_text(json.dumps(measure,ensure_ascii=False,indent=2))
assert float(measure['measured']['input_tp'])<0
plan.update(status='passed_ready_for_native_audio_only_import',actual_loudness=measure['measured'],sample_peak_dbfs=float(20*np.log10(np.max(np.abs(y.astype(np.int64)))/2147483648)),new_cue_before39p2_pcm_bit_identical=True,original_bgm_after40p8_pcm_bit_identical=True,original_preserved_after40p8_samples=N-hi,entire_new_wav_pcm_sha256=sha,container_decoded_pcm_sha256=hs.hexdigest(),container_pcm_bit_identical_to_wav=True,container_video={'fps':25,'resolution':[16,16],'frames':2861,'codec':'h264','never_place_on_picture_track':True},limiter_added=False,common_trim_db=0,subjective_listening='unavailable; actual sample values, clock, RMS/LUFS/truepeak checks only',other_audio_or_timeline_modified=False)
(OUT/'开篇配乐_原生回装清单_v20.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
print(json.dumps({'status':'passed','manifest':str(OUT/'开篇配乐_原生回装清单_v20.json'),'wav_path':str(WAV),'container_path':str(MOV),'duration_seconds':DURATION,'frames':2861,'samples':N,'after40p8_pcm_exact':True,'omitted_native_tail_digital_zero_samples':old_native_end-N,'actual_loudness':plan['actual_loudness'],'native_append':plan['native_append']},ensure_ascii=False),flush=True)
