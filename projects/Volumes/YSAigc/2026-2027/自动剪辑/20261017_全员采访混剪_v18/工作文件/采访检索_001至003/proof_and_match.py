import json,re
from pathlib import Path
import numpy as np,soundfile as sf,av
from scipy.signal import resample_poly,correlate
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).parent
R=json.loads((O/'formal_candidates.json').read_text())
F=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',16)
for r in R:
 d=r['duration'];times=[min(.8,d*.1),d*.5,max(0,d-.8)];sheet=Image.new('RGB',(1440,315),'#111111');draw=ImageDraw.Draw(sheet)
 for i,t in enumerate(times):
  with av.open(r['path']) as c:
   st=c.streams.video[0];c.seek(int(t/float(st.time_base)),stream=st,backward=True)
   for f in c.decode(st):
    if f.time>=t:
     im=f.to_image();im.thumbnail((480,270));sheet.paste(im,(i*480,0));break
  draw.text((i*480+5,275),f"{r['name']}  {t:.2f}s",fill='white',font=F)
 sheet.save(O/(r['key']+'_首中末.jpg'),quality=92)
p=O/'ASR完整/001_20260924_C0163_Proxy_channels.wav';x,sr=sf.read(p,dtype='float32',always_2d=True);x=x[:,0]
y,ysr=sf.read('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_旁白精修/工作文件/audio_v2/04_校长完整讲话_余量.wav',dtype='float32',always_2d=True);y=y.mean(axis=1);y=resample_poly(y,1,3)[:int(14.6*16000)]
c=correlate(x,y,mode='valid',method='fft');ix=int(np.argmax(c));seg=x[ix:ix+len(y)];cc=float(np.dot(seg,y)/(np.linalg.norm(seg)*np.linalg.norm(y)))
result={'existing_audio':'04_校长完整讲话_余量.wav','confirmed_source':str(next(r['path'] for r in R if r['key']=='001_20260924_C0163_Proxy')),'signal_matched_source_start_seconds':ix/16000,'source_out_seconds':ix/16000+14.6,'normalized_waveform_correlation':cc,'expected_start':47.88,'note':'Direct PCM correlation against fresh camera-source decode; processing may slightly alter waveform.'}
(O/'existing_principal_audio_source_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(result)
