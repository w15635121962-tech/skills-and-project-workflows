from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json
R=Path(__file__).resolve().parents[2];P=R/'工作文件/开篇_原生逐帧';O=Path(__file__).parent;plan=json.load(open(R/'工作文件/opening_edit_plan_v22.json'));shots=plan['shots'];font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
imgs=[]
for i in range(667):
 im=Image.open(P/f'{i:04d}.jpg');imgs.append(np.asarray(im.resize((240,135)).convert('L'),dtype='float32'))
mad=[float(np.abs(a-b).mean()) for a,b in zip(imgs,imgs[1:])];cuts=[s['start'] for s in shots];stats=[]
for s in shots:
 a,b=s['start'],s['end'];vals=mad[a:b-1];stats.append({'start':a,'end_exclusive':b,'label':s['label'],'min':min(vals),'median':float(np.median(vals)),'mean':float(np.mean(vals)),'max':max(vals),'near_frozen_pairs':[a+i for i,m in enumerate(vals) if m<.04]})
contacts=[]
for page in range(3):
 sh=shots[page*6:(page+1)*6];sheet=Image.new('RGB',(1440,len(sh)*292),(10,10,10));d=ImageDraw.Draw(sheet)
 for row,s in enumerate(sh):
  a,b=s['start'],s['end'];inds=[a,(a+b-1)//2,b-1]
  for col,f in enumerate(inds):
   im=Image.open(P/f'{f:04d}.jpg');im.thumbnail((480,270));x=col*480;y=row*292;sheet.paste(im,(x,y));d.text((x+8,y+270),f'Native frame {f} / shot {page*6+row+1}',font=font,fill='white')
 p=O/f'v22_18镜连续动作首中尾_{page+1}.jpg';sheet.save(p,quality=93);contacts.append(str(p))
high=sorted([{'next_frame':i+1,'MAD':v} for i,v in enumerate(mad) if i+1 not in cuts],key=lambda x:x['MAD'],reverse=True)[:20]
flag=[h['next_frame'] for h in high if h['MAD']>25];context=sorted(set(max(0,min(666,f+d)) for f in flag[:6] for d in [-2,-1,0,1,2]))
if context:
 sheet=Image.new('RGB',(1440,((len(context)+2)//3)*292),(10,10,10));d=ImageDraw.Draw(sheet)
 for j,f in enumerate(context):
  im=Image.open(P/f'{f:04d}.jpg');im.thumbnail((480,270));x=j%3*480;y=j//3*292;sheet.paste(im,(x,y));d.text((x+8,y+270),f'High motion context native frame {f}',font=font,fill='white')
 p=O/'v22_高变化逐帧上下文.jpg';sheet.save(p,quality=93);contacts.append(str(p))
x={'decoded_native_frames':667,'plan_file':str(R/'工作文件/opening_edit_plan_v22.json'),'cut_frames':cuts,'cut_pair_MAD':{str(c):mad[c-1] for c in cuts if c>0},'segment_stats':stats,'highest_intra_frame_differences':high,'flagged_noncut_high_differences':flag,'contacts':contacts}
(O/'v22_全667帧连续运动_测量.json').write_text(json.dumps(x,ensure_ascii=False,indent=2));print(json.dumps(x,ensure_ascii=False))
