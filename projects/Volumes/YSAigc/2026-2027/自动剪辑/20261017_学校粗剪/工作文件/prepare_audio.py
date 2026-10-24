from pathlib import Path
import json,subprocess,sys,concurrent.futures,numpy as np,soundfile as sf
from scipy.signal import resample_poly
OUT=Path(__file__).parent;ROOT=OUT.parent;SK=Path('/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts')
plan=json.loads((OUT/'edit_plan.json').read_text());audio_dir=ROOT/'声音';audio_dir.mkdir(exist_ok=True)
logs=OUT/'audio_logs';logs.mkdir(exist_ok=True)
def call(script,args,tag):
 proc=subprocess.run([sys.executable,str(SK/script),*map(str,args),'--json-brief'],capture_output=True,text=True)
 (logs/(tag+'.log')).write_text(proc.stdout+'\n'+proc.stderr,encoding='utf-8')
 if proc.returncode:raise RuntimeError(tag+': '+proc.stdout[-1000:]+proc.stderr[-1000:])
def voice(job):
 i,s=job;clean=OUT/(f'voice-{i+1}-clean.wav');trim=OUT/(f'voice-{i+1}-trim.wav');dest=audio_dir/(f'{i+1:03d}_'+s['section'].replace(' ','_')+'.wav')
 if not dest.exists():
  if not clean.exists():call('audio.py',[s['path'],'-o',clean,'--voice','light','--stereo'],f'voice-{i+1}-clean')
  data,sr=sf.read(clean,always_2d=True,dtype='float32');a=round(s['in']*sr);n=round(s['length_frames']/25*sr);data=data[a:a+n]
  assert len(data)==n
  fade=min(round(sr*.012),len(data)//2);data[:fade]*=np.linspace(0,1,fade)[:,None];data[-fade:]*=np.linspace(1,0,fade)[:,None]
  sf.write(trim,data,sr,subtype='PCM_24')
  call('loudness.py',[trim,'-o',dest,'-I','-16','--tp','-2','--sample-rate','48000'],f'voice-{i+1}-normal')
 return {'kind':'speech','path':str(dest),'record_frame':s['record_frame'],'duration_frames':s['length_frames'],'section':s['section'],'shot_index':i,'source':s['path'],'source_in':s['in']}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
 voices=list(ex.map(voice,[(i,s) for i,s in enumerate(plan['shots']) if s['voice']]))
print('VOICES',len(voices),flush=True)
music=sorted((ROOT/'配乐').glob('*.mp3'));normal=[]
for i,p in enumerate(music):
 dest=OUT/f'music{i+1:02d}_normal.wav'
 if not dest.exists():call('loudness.py',[p,'-o',dest,'-I',('-18' if i==1 else '-20'),'--tp','-3','--sample-rate','48000'],f'music-{i+1}-normal')
 normal.append(dest)
sr=48000;total=plan['duration_frames']/25
cues=[(0,0,118.4,0,1.2,1.2),(1,116,86.4,0,1.2,1.2),(2,200,84.44,0,1.2,3),(0,280.24,total-280.24,15,2.8,2.4)]
stems=[]
for i,(track,at,dur,src_in,fi,fo) in enumerate(cues):
 data,rate=sf.read(normal[track],always_2d=True,dtype='float32')
 if rate!=sr:
  from math import gcd
  g=gcd(sr,rate);data=resample_poly(data,sr//g,rate//g,axis=0)
 a=round(src_in*sr);n=round(dur*sr);data=data[a:a+n].copy();assert len(data)==n
 ts=np.arange(n)/sr+at;gain=np.ones(n,dtype=np.float32)
 gain*=np.minimum(1,np.arange(n)/max(1,fi*sr));gain*=np.minimum(1,(n-1-np.arange(n))/max(1,fo*sr))
 # Speech starts at 250.8s. Music fades down ahead of the first word.
 if at+dur>250.4:
  duck=np.interp(ts,[0,250.25,250.8,total-2.6,total-1.25,total],[0,0,-12,-12,-4,-4]);gain*=10**(duck/20)
 data*=gain[:,None]
 dest=audio_dir/(f'BGM_{i+1:02d}_'+Path(music[track]).stem)
 dest=Path(str(dest)+'.wav');sf.write(dest,data,sr,subtype='PCM_24')
 stems.append({'kind':'music','path':str(dest),'record_frame':round(at*25),'duration_frames':round(dur*25),'track':i%2+2,'source':str(music[track]),'source_in':src_in,'fade_in':fi,'fade_out':fo,'duck_db':-12 if at+dur>250.4 else 0})
mixed=np.zeros((round(total*sr),2),dtype=np.float32)
for item in voices+stems:
 data,rate=sf.read(item['path'],always_2d=True,dtype='float32')
 if rate!=sr:
  from math import gcd
  g=gcd(sr,rate);data=resample_poly(data,sr//g,rate//g,axis=0)
 a=round(item['record_frame']/25*sr);n=min(len(data),len(mixed)-a);mixed[a:a+n]+=data[:n]
peak=float(np.max(np.abs(mixed)));print('MIX_PEAK_DBFS',20*np.log10(peak),flush=True)
assert peak<.99,'Mix clipping: lower music or speech gain'
sf.write(audio_dir/'粗剪混音试听.wav',mixed,sr,subtype='PCM_24')
(OUT/'audio_plan.json').write_text(json.dumps({'speech':voices,'music':stems,'mix_peak_dbfs':float(20*np.log10(peak))},ensure_ascii=False,indent=2),encoding='utf-8')
print('AUDIO_READY',flush=True)
