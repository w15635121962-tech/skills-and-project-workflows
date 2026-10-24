"""Offline musical contrast at15s. Never connects to Resolve.
Closest ffmpeg-skill tool is audio.py; exact PCM clocks use the verified PyAV
workflow. Pitch-preserving atempo=.88 is run through libavfilter with explicit
stereo/fltp output; the local sine test independently checked pitch and length.
"""
from pathlib import Path
from fractions import Fraction
import json,hashlib,subprocess,argparse,sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import soundfile as sf
import av
from scipy.signal import lfilter

W=Path(__file__).resolve().parent;R=W.parents[1];OUT=R/'旁白与配乐';PRE=R/'开篇预览'
V21=R.parent/'20261018_内外景运镜与人物动势开篇_v21'
V19=R.parent/'20261018_样片节奏与全员采访精修_v19'
PLAN=json.loads((V19/'工作文件/参考与音乐/music_cue_plan_v19.json').read_text())
BASE_MAN=json.loads((V21/'旁白与配乐/开篇配乐_原生回装清单_v21.json').read_text())
BASE=Path(BASE_MAN['wav_path'])
VOICE=R.parent/'20261017_画面缓推与旁白气口精修_v14/旁白与混音/01_完整旁白_气口精修_v14_48k24.wav'
GUITAR=Path(PLAN['tracks']['4']['file'])
SR,FPS,SPF=48000,25,1920;FRAMES=2861;N=FRAMES*SPF;SPLIT=375*SPF
TRANS=[round(x*SR) for x in [14.84,15.16]]
BACK=[round(x*SR) for x in [110.84,112.44]]
TEMPO=.88;SOURCE_AT15=2.96;SOURCE_START=SOURCE_AT15-(15-14.84)*TEMPO
PY='/Users/xuan/.local/share/promo-audio/venv/bin/python';SKILL=Path('/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts')
ap=argparse.ArgumentParser();ap.add_argument('--dry-run',action='store_true');ap.add_argument('--resume',action='store_true');args=ap.parse_args()
for d in [W,OUT,PRE]:d.mkdir(parents=True,exist_ok=True)
MAN=OUT/'十五秒音乐分界_原生回装清单_v23.json'
FULL=OUT/'00_前114p44秒_十五秒分界整体音乐_v23_48k24.wav'
MIX45=OUT/'开篇45秒_原旁白与十五秒换乐_v23.wav'
MIX114=OUT/'前114p44秒_原旁白与既有A4衔接核验_v23.wav'
MIXPRE=PRE/'开篇26p68秒_原旁白与十五秒换乐_v23.wav'
items=[]
for no,a,b,stem in [(1,0,375,'前15秒_强管弦起势'),(2,375,2861,'15秒后_舒展木吉他正文')]:
 items.append({'name':stem+'_v23','wav_path':str(OUT/f'{no:02d}_{stem}_v23_48k24.wav'),'container_path':str(OUT/f'{no:02d}_{stem}_v23_25fps_PCM.mov'),'native_append':{'startFrame':0,'endFrame':b-a,'recordFrame':a,'trackIndex':3,'mediaType':2},'record_start_frame':a,'record_end_frame_exclusive':b,'duration_frames':b-a,'duration_seconds':(b-a)/FPS,'duration_samples':(b-a)*SPF,'clip_gain_db':0,'no_additional_native_fades':True})
manifest={'status':'planned','fps':25,'sample_rate':SR,'pcm_bits':24,'channels':2,'duration_frames':FRAMES,'duration_seconds':114.44,'items':items,'whole_music_wav':str(FULL),'full_music_wav':str(FULL),'mix45_wav_path':str(MIX45),'preview26p68_wav_path':str(MIXPRE),'full_mix114p44_wav_path':str(MIX114),'old_first_bgm':str(BASE),'old_first_bgm_native_container':BASE_MAN['container_path'],'narration_reference':str(VOICE),'opening_recording':PLAN['tracks']['6'],'body_recording':PLAN['tracks']['4'],'body_tempo_multiplier':TEMPO,'body_source_at15_seconds':SOURCE_AT15,'body_source_start_with_transition':SOURCE_START,'estimated_BPM':{'opening':129.2,'body_source_half_tempo':80.75,'body_after_time_stretch':80.75*TEMPO,'human_listening_verified':False},'opening_target_LU_increase_over_v22':2.5,'body_target_LUFS_core15_to105':-29,'opening_voice_space_EQ':{'music_only':True,'peaking_frequency_hz':1800,'gain_db':-1.8,'Q':.7,'voice_unchanged':True},'transition_center_seconds':15,'transition_range_seconds':[14.84,15.16],'back_to_original_A3_seconds':[110.84,112.44],'after112p44_original_A3_PCM_exact':True,'all_later_music_items_unchanged':True,'resolve_connected':False,'subjective_listening':'unavailable; source metadata, waveform, estimated tempo and measured PCM/loudness QC only'}
(OUT/'十五秒音乐分界_制作计划_v23.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
if args.dry_run:
 print(json.dumps(manifest,ensure_ascii=False));sys.exit(0)
if not args.resume:assert not FULL.exists() and all(not Path(x['wav_path']).exists() and not Path(x['container_path']).exists() for x in items)

def read(p,start=0,stop=None):
 z,s=sf.read(p,dtype='int32',always_2d=True,start=start,stop=stop);assert s==SR and z.shape[1]==2;return z
def q24(z):
 x=np.rint(np.asarray(z)*8388608).astype(np.int64)*256
 assert np.max(x)<2147483648 and np.min(x)>=-2147483648,'PCM would clip'
 return x.astype(np.int32)
def write(p,z):sf.write(p,z,SR,subtype='PCM_24')
def enc24(z):
 x=(np.asarray(z,np.int32)>>8).reshape(-1)
 return np.column_stack((x&255,(x>>8)&255,(x>>16)&255)).astype(np.uint8).tobytes()
def pcmhash(z):return hashlib.sha256(enc24(z)).hexdigest()
def peak(z):return float(20*np.log10(np.max(np.abs(z.astype(np.int64)))/2147483648))
def measure(p,label):
 f=W/f'{label}_实测.json';identity=hashlib.sha256(Path(p).read_bytes()).hexdigest()
 if f.exists() and args.resume:
  v=json.loads(f.read_text())
  if v.get('source_file_sha256')==identity:return v['measured']
 argv=[PY,str(SKILL/'loudness.py'),str(p),'--measure-only','--json']
 pr=subprocess.run(argv,capture_output=True,text=True,check=True);v=json.loads(pr.stdout);assert v['status']=='completed';v['source_file_sha256']=identity;v['actual_argv']=argv;v['actual_exit_code']=0;f.write_text(json.dumps(v,ensure_ascii=False,indent=2));return v['measured']
def decode(p):
 rows=[]
 with av.open(str(p)) as c:
  st=c.streams.audio[0];rs=av.AudioResampler(format='fltp',layout='stereo',rate=SR)
  for f in c.decode(st):
   for q in rs.resample(f):rows.append(q.to_ndarray().T.copy())
  for q in rs.resample(None):rows.append(q.to_ndarray().T.copy())
 return np.concatenate(rows).astype(np.float32)
def stretch(x):
 g=av.filter.Graph();src=g.add_abuffer(sample_rate=SR,format='fltp',layout='stereo',time_base=Fraction(1,SR));tempo=g.add('atempo',str(TEMPO));fmt=g.add('aformat','sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo');sink=g.add('abuffersink');src.link_to(tempo);tempo.link_to(fmt);fmt.link_to(sink);g.configure();rows=[]
 def pull():
  while True:
   try:
    f=sink.pull();assert f.format.name=='fltp' and len(f.layout.channels)==2;rows.append(f.to_ndarray().T.copy())
   except (av.error.BlockingIOError,av.error.EOFError):break
 for i in range(0,len(x),SPF):
  f=av.AudioFrame.from_ndarray(x[i:i+SPF].T.copy(),format='fltp',layout='stereo');f.sample_rate=SR;f.pts=i;f.time_base=Fraction(1,SR);src.push(f);pull()
 src.push(None);pull();return np.concatenate(rows).astype(np.float32)

fresh=json.loads((R/'工作文件/live_before_v23.json').read_text());sn=fresh['snapshot'];old_item=sn['audio'][2]['items'][0];a4=sn['audio'][3]['items'][0]
assert (old_item['start'],old_item['end'],old_item['offset'])==(0,2861,0)
assert old_item['path']==BASE_MAN['container_path']
assert (a4['start'],a4['offset'])==(2811,0)
base=read(BASE);assert len(base)==N and pcmhash(base)==BASE_MAN['entire_new_wav_pcm_sha256']
for key in ['6','1','4']:
 t=PLAN['tracks'][key];assert hashlib.sha256(Path(t['file']).read_bytes()).hexdigest()==t['verification']['sha256']
assert json.loads((W/'保留音高延展_本地过滤器核验_v23.json').read_text())['passed']

# Music-only broad 1.8kHz space; gain is calibrated on the actual 0..14.5s PCM.
st=base[:TRANS[1]].astype(np.float64)/2147483648
A=10**(-1.8/40);om=2*np.pi*1800/SR;al=np.sin(om)/(2*.7);den=1+al/A
b=np.array([1+al*A,-2*np.cos(om),1-al*A])/den;aa=np.array([1+al/A,-2*np.cos(om),1-al/A])/den
st=lfilter(b,aa,st,axis=0)
ref=round(14.5*SR);oldcore=W/'v22音乐0至14p5秒_基线.wav';eqcore=W/'v23强开场中频让位后_归一前.wav';write(oldcore,base[:ref]);write(eqcore,q24(st[:ref]))
oldstat=measure(oldcore,'v22基线音乐0至14p5秒');eqstat=measure(eqcore,'v23中频让位归一前0至14p5秒');gain=float(oldstat['input_i'])+2.5-float(eqstat['input_i']);st*=10**(gain/20)

# Raw guitar is stretched once with pitch held, never looped or repeated.
raw=decode(GUITAR);sample_in=round(SOURCE_START*SR);guit=stretch(raw[sample_in:]);needed=N-TRANS[0];assert len(guit)>=needed
guit=guit[:needed].astype(np.float64)
normstart=round((15-14.84)*SR);normend=round((105-14.84)*SR)
rawref=W/'木吉他延展后15至105秒_归一前.wav';write(rawref,q24(guit[normstart:normend]*.5));gs=measure(rawref,'木吉他延展后15至105秒_归一前');raw_i=float(gs['input_i'])+6.020599913279624;guitar_gain=-29-raw_i
voice=read(VOICE,stop=N);assert len(voice)==N;v=voice.astype(np.float64)/2147483648
block=4800;nb=len(v)//block;vb=np.sqrt(np.mean(v[:nb*block].reshape(nb,block,2)**2,axis=(1,2)));quiet=20*np.log10(vb+1e-15)<-39
gaps=np.flatnonzero(np.diff(np.r_[False,quiet,False])).reshape(-1,2);tm=14.84+np.arange(needed)/SR;release=np.zeros(needed,np.float64);windows=[]
for ia,ib in gaps:
 a,b=ia*.1,ib*.1
 if b-a<.79 or a<15.5 or b>105:continue
 left,right=a+.08,b-.16
 if right-left<.5:continue
 ii=np.flatnonzero((tm>=left)&(tm<=right));x=(tm[ii]-left)/(right-left);bump=1.5*np.sin(np.pi*x)**2;release[ii]=np.maximum(release[ii],bump);windows.append({'start':left,'end':right,'max_db':float(bump.max())})
guit*=10**((guitar_gain+release[:,None])/20)

y=base.astype(np.float64)/2147483648
y[:TRANS[0]]=st[:TRANS[0]]
phase=np.arange(TRANS[1]-TRANS[0])/(TRANS[1]-TRANS[0])
y[TRANS[0]:TRANS[1]]=st[TRANS[0]:TRANS[1]]*np.cos(phase*np.pi/2)[:,None]+guit[:TRANS[1]-TRANS[0]]*np.sin(phase*np.pi/2)[:,None]
y[TRANS[1]:BACK[0]]=guit[TRANS[1]-TRANS[0]:BACK[0]-TRANS[0]]
phase=np.arange(BACK[1]-BACK[0])/(BACK[1]-BACK[0])
y[BACK[0]:BACK[1]]=guit[BACK[0]-TRANS[0]:BACK[1]-TRANS[0]]*np.cos(phase*np.pi/2)[:,None]+(base[BACK[0]:BACK[1]].astype(np.float64)/2147483648)*np.sin(phase*np.pi/2)[:,None]
y=q24(y);y[BACK[1]:]=base[BACK[1]:];write(FULL,y)
assert np.array_equal(read(FULL),y) and np.array_equal(y[BACK[1]:],base[BACK[1]:])

def carrier(item):
 a=item['record_start_frame']*SPF;b=item['record_end_frame_exclusive']*SPF;z=y[a:b];wav=Path(item['wav_path']);mov=Path(item['container_path']);write(wav,z)
 with av.open(str(mov),'w') as o:
  vs=o.add_stream('libx264',rate=FPS);vs.width=16;vs.height=16;vs.pix_fmt='yuv420p';vs.options={'preset':'ultrafast','tune':'zerolatency','crf':'51','bf':'0'};vs.codec_context.thread_count=1
  ast=o.add_stream('pcm_s24le',rate=SR);ast.layout='stereo';ast.time_base=Fraction(1,SR)
  o.metadata['comment']='AUDIO ONLY source clock. mediaType2, A3,0dB,no further fades; black16x16 never belongs on picture.';o.metadata['title']=item['name'];black=np.zeros((16,16,3),np.uint8)
  for i in range(item['duration_frames']):
   f=av.VideoFrame.from_ndarray(black,format='rgb24');f.pts=i;f.time_base=Fraction(1,FPS)
   for pk in vs.encode(f):o.mux(pk)
   f=av.AudioFrame.from_ndarray(z[i*SPF:(i+1)*SPF].reshape(1,-1),format='s32',layout='stereo');f.sample_rate=SR;f.pts=i*SPF;f.time_base=Fraction(1,SR)
   for pk in ast.encode(f):o.mux(pk)
  for pk in vs.encode():o.mux(pk)
  for pk in ast.encode():o.mux(pk)
 n=0;h=hashlib.sha256()
 with av.open(str(mov)) as c:
  vs=c.streams.video[0];st=c.streams.audio[0];assert vs.average_rate==25 and vs.frames==item['duration_frames'] and st.start_time==0 and st.duration==len(z)
  assert vs.codec_context.width==vs.codec_context.height==16 and st.codec_context.name=='pcm_s24le'
  for f in c.decode(st):
   assert f.pts==n and f.format.name=='s32' and len(f.layout.channels)==2
   zz=f.to_ndarray().reshape(-1,2);h.update(enc24(zz));n+=len(zz)
 assert n==len(z) and h.hexdigest()==pcmhash(z)
 item.update(pcm_hash=pcmhash(z),container_pcm_hash=h.hexdigest(),container_pcm_bit_identical_to_wav=True,samples_verified=n,actual_sample_peak_dbfs=peak(z),carrier_never_use_video=True)
 return item
for i in items:carrier(i)
assert np.array_equal(np.concatenate([read(x['wav_path']) for x in items]),y)

# Exact PCM sums, no processing or change to original VO. Include unchanged A4
# at its fresh native112.44s start for transition/headroom verification.
mix=voice.astype(np.int64)+y.astype(np.int64);second=read(a4['path'],stop=N-a4['start']*SPF);assert len(second)==N-a4['start']*SPF
mix[a4['start']*SPF:]+=second.astype(np.int64)
assert mix.max()<2147483648 and mix.min()>=-2147483648,'Narration plus music would clip'
mix=mix.astype(np.int32);write(MIX114,mix);write(MIX45,mix[:45*SR]);write(MIXPRE,mix[:667*SPF])
assert np.array_equal(read(MIX45),mix[:45*SR]) and np.array_equal(read(MIXPRE),mix[:667*SPF])
parts=[('强开场0至14p5秒',0,14.5),('正文15p5至30秒',15.5,30),('正文15p5至105秒',15.5,105),('15秒过门14至16秒',14,16),('回接原曲110至114p44秒',110,114.44)]
jobs=[(FULL,'整体音乐114p44秒'),(MIX45,'原VO加新音乐45秒'),(MIX114,'原VO加新音乐与既有A4_114p44秒'),(MIXPRE,'原VO加新音乐26p68秒')]
for label,a,b in parts:
 f=W/(label+'_音乐实样.wav');write(f,y[round(a*SR):round(b*SR)]);jobs.append((f,label))
for no,it in enumerate(items):jobs.append((it['wav_path'],f'原生分段{no+1}'))
with ThreadPoolExecutor(max_workers=3) as ex:stats=dict(ex.map(lambda a:(a[1],measure(*a)),jobs))
for label,s in stats.items():assert float(s['input_tp'])<=-1,(label,s)
opening_delta=float(stats['强开场0至14p5秒']['input_i'])-float(oldstat['input_i'])
contrast=float(stats['强开场0至14p5秒']['input_i'])-float(stats['正文15p5至30秒']['input_i'])
assert 2<=opening_delta<=3 and contrast>=4,(opening_delta,contrast)
for n,it in enumerate(items):it['actual_loudness']=stats[f'原生分段{n+1}']
manifest.update(status='passed_ready_for_native_audio_only_import',items=items,whole_music_pcm_hash=pcmhash(y),independent_items_concatenation_PCM_exact=True,after112p44_original_A3_PCM_exact=True,preserved_original_tail_samples=N-BACK[1],original_A4_unchanged=True,original_A4_native_start_frame=a4['start'],narration_PCM_unchanged=True,actual_measurements=stats,opening_reference_v22_loudness=oldstat,actual_opening_increase_LU=opening_delta,actual_opening_vs_body_contrast_LU=contrast,opening_actual_gain_db=gain,body_actual_gain_db=guitar_gain,body_source_reference_lufs_after_stretch=raw_i,body_slow_release_windows=windows,mix114p44_sample_peak_dbfs=peak(mix),original_inputs_modified=False,other_music_clips_modified=False,body_source_looped=False,body_pitch_preserving_filter='atempo=.88,aformat=fltp/stereo/48000',body_stretched_available_samples=len(guit),whole_music_samples=N,preview26p68_samples=667*SPF,no_additional_native_fades=True,transition_baked_into_whole_PCM_before_split=True)
MAN.write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print(json.dumps({'status':manifest['status'],'manifest':str(MAN),'opening_increase_LU':opening_delta,'opening_body_contrast_LU':contrast,'actual_opening':stats['强开场0至14p5秒'],'actual_body':stats['正文15p5至30秒'],'mix114':stats['原VO加新音乐与既有A4_114p44秒'],'tail_exact':True,'split_join_exact':True,'preview':str(MIXPRE)},ensure_ascii=False),flush=True)
