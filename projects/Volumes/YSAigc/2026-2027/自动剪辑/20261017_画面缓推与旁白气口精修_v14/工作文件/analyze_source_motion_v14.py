from pathlib import Path
import json,math,concurrent.futures,hashlib
import av,numpy as np
from PIL import Image,ImageOps,ImageDraw,ImageFont
R=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_画面缓推与旁白气口精修_v14/工作文件');O=R/'源画面运动审阅';O.mkdir(exist_ok=True)
a=json.load(open(R/'live_before_v14.json'));base=json.load(open(R/'motion_candidates_v14.json'));fusion={(x['track'],x['start']):x for x in a['fusion']};items=[]
for x in base['eligible']:
 if any(t['type']=='TextPlus' for t in fusion[x['track'],x['start']]['tools']):continue
 items.append(x)
def corr(a,b):
 h,w=a.shape;window=np.outer(np.hanning(h),np.hanning(w));fa=np.fft.rfft2((a-a.mean())*window);fb=np.fft.rfft2((b-b.mean())*window);cross=fb*np.conj(fa);cross/=np.maximum(np.abs(cross),1e-12);co=np.abs(np.fft.irfft2(cross,s=(h,w)));yy,xx=np.unravel_index(np.argmax(co),co.shape);xx=xx-w if xx>w//2 else xx;yy=yy-h if yy>h//2 else yy
 return [int(xx),int(yy),float(co.max()/(co.mean()+1e-12))]
def analyze(x):
 t0=x['offset']/25;dt=(x['length_frames']-1)/25;times=[t0+dt*i/6 for i in range(7)];out=O/f"T{x['track']}_{x['start']:05d}";out.mkdir(exist_ok=True);frameList=[];allgray=[]
 c=av.open(x['path']);st=c.streams.video[0];st.thread_type='AUTO';c.seek(max(0,int(times[0]/float(st.time_base))),stream=st,backward=True,any_frame=False);i=0
 for fr in c.decode(st):
  t=float(fr.pts*st.time_base) if fr.pts is not None else float(fr.time or 0)
  while i<7 and t>=times[i]-.5/float(st.average_rate or 25):
   im=fr.to_image().convert('RGB');im.thumbnail((640,360));p=out/f'{i}_{times[i]:.3f}s.jpg';im.save(p,quality=91);g=np.asarray(im.convert('L').resize((256,144)),dtype=np.float32)/255;allgray.append(g);frameList.append({'sample':i,'requested_time':times[i],'actual_time':t,'path':str(p)});i+=1
  if i==7:break
 c.close()
 if len(frameList)!=7:raise RuntimeError((x['start'],len(frameList),times))
 diffs=[float(np.mean(np.abs(b-v))) for v,b in zip(allgray,allgray[1:])];shift=[corr(v,b) for v,b in zip(allgray,allgray[1:])];shifts=[math.hypot(s[0],s[1]) for s in shift]
 return {**x,'samples':frameList,'diagnostics':{'mean_luma_difference':float(np.mean(diffs)),'max_luma_difference':max(diffs),'gray_mae_pairs':diffs,'global_shift_pairs_at_256px':shift,'median_global_shift_at_256px':float(np.median(shifts)),'max_global_shift_at_256px':max(shifts)},'viewed':False}
res=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 fut={pool.submit(analyze,x):x for x in items}
 for i,f in enumerate(concurrent.futures.as_completed(fut),1):
  try:res.append(f.result())
  except Exception as e:print('FAILED',fut[f]['track'],fut[f]['start'],repr(e),flush=True);raise
  if i%20==0:print('EXTRACTED',i,'/',len(items),flush=True)
res.sort(key=lambda x:(x['track'],x['start']));json.dump(res,open(R/'source_motion_diagnostics_v14.json','w'),ensure_ascii=False,indent=2)
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',19)
for page,j in enumerate(range(0,len(res),9),1):
 batch=res[j:j+9];can=Image.new('RGB',(1680,175*len(batch)),(16,24,28));d=ImageDraw.Draw(can)
 for row,x in enumerate(batch):
  y=row*175
  for k,s in enumerate(x['samples']):
   im=Image.open(s['path']);im.thumbnail((240,135));can.paste(im,(240*k,y))
  dg=x['diagnostics'];d.text((6,y+137),f"T{x['track']} R{x['start']} {x['length_frames']/25:.2f}s {Path(x['path']).name[:35]}  diff {dg['mean_luma_difference']:.4f}  shift {dg['median_global_shift_at_256px']:.1f}/{dg['max_global_shift_at_256px']:.1f}  {x['intent'][:25]}",font=font,fill=(230,235,228))
 can.save(O/f'七点源帧_{page:02d}.jpg',quality=94,subsampling=0)
print('COMPLETE',len(res),flush=True)
