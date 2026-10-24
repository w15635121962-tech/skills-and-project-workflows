import json,re,os
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕/男版20_新旁白与自动剪辑_20261023'); W=ROOT/'预览/工作'; D=W/'字幕序列';D.mkdir(exist_ok=True)
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',24)
items=[]
def sec(t):
 h,m,s=t.split(':'); return int(h)*3600+int(m)*60+float(s.replace(',','.'))
for block in (ROOT/'字幕/EP20.srt').read_text(encoding='utf-8-sig').strip().split('\n\n'):
 lines=block.splitlines(); a,b=lines[1].split(' --> '); text='\n'.join(lines[2:]); items.append((round(sec(a)*24),round(sec(b)*24),text))
assert len(items)==31
im=Image.new('RGB',(480,854),(0,255,0));blank=W/'字幕_空白.png';im.save(blank)
images=[]
for i,(a,b,text) in enumerate(items):
 im=Image.new('RGB',(480,854),(0,255,0));d=ImageDraw.Draw(im);lines=text.splitlines();line_h=29;y=854-70-len(lines)*line_h
 for line in lines:
  bb=d.textbbox((0,0),line,font=font,stroke_width=2);x=(480-(bb[2]-bb[0]))//2-bb[0];d.text((x,y),line,font=font,fill='white',stroke_width=2,stroke_fill='black');y+=line_h
 p=W/f'字幕_{i+1:02d}.png';im.save(p);images.append(p)
for f in range(1594):
 p=blank
 for i,(a,b,t) in enumerate(items):
  if a<=f<b: p=images[i];break
 target=D/f'frame_{f:04d}.png'
 if target.exists():target.unlink()
 os.link(p,target)
( W/'字幕序列_源SRT映射.json').write_text(json.dumps({'cue_count':31,'fps':24,'duration_frames':1594,'cues':[{'start_frame':a,'end_frame':b,'text':t} for a,b,t in items],'srt_original_unchanged':True},ensure_ascii=False,indent=2),encoding='utf-8')
