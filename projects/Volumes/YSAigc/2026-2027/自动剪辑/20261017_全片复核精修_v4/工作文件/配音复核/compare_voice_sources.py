from pathlib import Path
import json,numpy as np,soundfile as sf
from scipy.signal import resample_poly,correlate,correlation_lags
import math
OUT=Path(__file__).parent
BASE=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_旁白精修/工作文件')
ap=json.loads((BASE/'audio_plan_v2.json').read_text())
rawroot=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_学校粗剪/工作文件/speech')
rawpaths=[BASE/'narration_16k.wav',rawroot/'001_20260924_C0043_Proxy.wav',rawroot/'001_20260924_C0160_Proxy.wav',rawroot/'001_20260924_C0163_Proxy.wav']
def load(p):
 a,sr=sf.read(p,dtype='float32')
 if a.ndim>1:a=a.mean(axis=1)
 if sr!=16000:
  g=math.gcd(sr,16000);a=resample_poly(a,16000//g,sr//g).astype('float32')
 return a
res=[]
for i,(r,item) in enumerate(zip(rawpaths,ap['speech']),1):
 original=load(r);target=load(item['path']);start=round(item['source_in']*16000);expected=original[start:start+round(item['duration_frames']/25*16000)]
 if i==1:
  target=target[:len(expected)];windows=[]
  for t in range(0,434,5):
   a=expected[t*16000:min((t+5)*16000,len(expected))];bb=target[t*16000:t*16000+len(a)]
   cor=float(np.corrcoef(a,bb)[0,1]);windows.append({'start':t,'end':t+len(a)/16000,'waveform_pearson_same_time':round(cor,6)})
  row={'index':i,'raw_reference':str(r),'processed_file':item['path'],'windows':windows,'minimum_correlation':min(x['waveform_pearson_same_time'] for x in windows),'note':'Original narration and processed narration remain at same sample timeline; normalization changes amplitude, not text.'}
 else:
  n=min(len(expected),len(target));aa=expected[:n];bb=target[:n]
  cc=correlate(bb,aa,mode='full',method='fft');lags=correlation_lags(len(bb),len(aa),mode='full');mask=np.abs(lags)<8000
  lag=int(lags[mask][np.argmax(cc[mask])]);
  if lag>=0:x=aa[:n-lag];y=bb[lag:n]
  else:x=aa[-lag:n];y=bb[:n+lag]
  corr=float(np.corrcoef(x,y)[0,1]);row={'index':i,'raw_reference':str(r),'processed_file':item['path'],'source_in':item['source_in'],'source_out':item['source_out'],'measured_lag_seconds':lag/16000,'correlation_after_lag':corr,'note':'Denoise/normalization may change sample values; correlation only checks source identity and timing.'}
 res.append(row)
(OUT/'source_identity_and_timing.json').write_text(json.dumps(res,ensure_ascii=False,indent=2))
for r in res:print(json.dumps(r if r['index']>1 else {k:v for k,v in r.items() if k!='windows'},ensure_ascii=False))
