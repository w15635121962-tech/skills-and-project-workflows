from pathlib import Path
from fractions import Fraction
import av,numpy as np,wave,hashlib,json
R=Path(__file__).resolve().parent
p=R/'_pcm_clock_2frame_test.mov'
x=(np.arange(3840*2,dtype=np.int32).reshape(-1,2)*47-8000)
if p.exists():p.unlink()
with av.open(str(p),'w') as o:
 v=o.add_stream('libx264',rate=25);v.width=16;v.height=16;v.pix_fmt='yuv420p';v.options={'preset':'ultrafast','tune':'zerolatency','crf':'51','bf':'0'};v.codec_context.thread_count=1
 a=o.add_stream('pcm_s24le',rate=48000);a.layout='stereo';a.time_base=Fraction(1,48000)
 for n in range(2):
  vf=av.VideoFrame.from_ndarray(np.zeros((16,16,3),np.uint8),format='rgb24');vf.pts=n;vf.time_base=Fraction(1,25)
  for pk in v.encode(vf):o.mux(pk)
  z=(x[n*1920:(n+1)*1920]<<8).reshape(1,-1)
  af=av.AudioFrame.from_ndarray(z,format='s32',layout='stereo');af.sample_rate=48000;af.pts=n*1920;af.time_base=Fraction(1,48000)
  for pk in a.encode(af):o.mux(pk)
 for pk in v.encode():o.mux(pk)
 for pk in a.encode():o.mux(pk)
y=[]
with av.open(str(p)) as c:
 s=c.streams.audio[0];print(s.codec_context.name,s.codec_context.format,s.time_base,s.duration)
 for f in c.decode(s):
  print(f.format,f.to_ndarray().shape,f.sample_rate,f.pts);y.append((f.to_ndarray().reshape(-1,2)>>8))
y=np.concatenate(y)
assert np.array_equal(x,y),(x.shape,y.shape,x[:4],y[:4]);print('PCM_CLOCK_OFFLINE_TEST_PASS',p,p.stat().st_size)
