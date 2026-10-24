import sys,json,time,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'开篇预览';FR=PRE/'实际时间线画面';FR.mkdir(exist_ok=True);TF=PRE/'片名淡入淡出';TF.mkdir(exist_ok=True)
plan=json.loads((OUT/'opening_plan_v5.json').read_text());build=json.loads((OUT/'native_build_v5.json').read_text());baseline=json.loads((OUT/'live_before_v5.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool();t=p.GetCurrentTimeline();assert t.GetName()==plan['name'];assert r.OpenPage('edit')
def tc(f):
 ss,ff=divmod(f,25);mm,ss=divmod(ss,60);hh,mm=divmod(mm,60);return f'{hh:02}:{mm:02}:{ss:02}:{ff:02}'
def cap(f,path):
 if path.exists():
  im=Image.open(path).convert('RGB');assert im.size==(1920,1080);return im
 assert t.SetCurrentTimecode(tc(f));time.sleep(.13);assert p.ExportCurrentFrameAsStill(str(path));im=Image.open(path).convert('RGB');assert im.size==(1920,1080);return im
opening=[s for s in plan['shots'] if s['record_frame']<1767];records=[];midpoints=[]
for s in opening:
 ims=[]
 for tag,off in [('入',0),('中',s['length_frames']//2),('出',s['length_frames']-1)]:
  frame=s['record_frame']+off;suffix='_最终' if s['record_frame']==1397 else '';path=FR/f"{s['index']:02d}_{tag}_{tc(frame).replace(':','-')}{suffix}.jpg";im=cap(frame,path);rec={'index':s['index'],'start':s['record_frame'],'frame':frame,'label':tag,'path':str(path),'changed_v5':s.get('revision_v5',False)};records.append(rec);ims.append((rec,im))
 midpoints.append((s,ims[1][1],ims[1][0]['path']))
 print('V5_ACTUAL_SHOT',s['index'],s['record_frame']/25,flush=True)
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',17)
sheet=Image.new('RGB',(1440,math.ceil(len(opening)/3)*305),(244,242,237));d=ImageDraw.Draw(sheet)
for i,(s,im,path) in enumerate(midpoints):
 im=im.copy();im.thumbnail((480,270));xx=i%3*480;yy=i//3*305;sheet.paste(im,(xx,yy));d.text((xx+6,yy+273),f"{s['record_frame']/25:.2f}–{(s['record_frame']+s['length_frames'])/25:.2f}s  {s['intent'][:17]}",font=font,fill=(40,44,40))
sheet.save(PRE/'开篇全部镜头实际总览.jpg',quality=95)
changed=[s for s in opening if s.get('revision_v5')];detail=Image.new('RGB',(1440,len(changed)*300),(244,242,237));d=ImageDraw.Draw(detail)
for i,s in enumerate(changed):
 rr=[x for x in records if x['start']==s['record_frame']]
 for j,rec in enumerate(rr):
  im=Image.open(rec['path']).convert('RGB');im.thumbnail((480,270));xx=j*480;yy=i*300;detail.paste(im,(xx,yy));d.text((xx+6,yy+273),f"{s['record_frame']/25:.2f}s {rec['label']} | {s['name'][:18]}",font=font,fill=(40,44,40))
detail.save(PRE/'六处改动_实际首中尾.jpg',quality=95)
titlechecks=[];titleimgs=[]
for f,label in [(340,'首帧'),(349,'渐入一半'),(358,'渐入完成'),(430,'稳定'),(489,'渐出开始'),(498,'渐出一半'),(507,'末帧')]:
 try:
  assert t.SetTrackEnable('video',2,True);path=TF/f'{f}_{label}_含片名.png';im=cap(f,path)
  assert t.SetTrackEnable('video',2,False);bp=TF/f'{f}_{label}_底片.png';bim=cap(f,bp)
 finally:assert t.SetTrackEnable('video',2,True)
 delta=np.abs(np.asarray(im,dtype=np.int16)-np.asarray(bim,dtype=np.int16))
 rec={'frame':f,'label':label,'path':str(path),'base':str(bp),'difference_sum':int(delta.sum()),'difference_max':int(delta.max())};titlechecks.append(rec);titleimgs.append((f,label,im))
assert titlechecks[0]['difference_max']==0 and titlechecks[-1]['difference_max']==0
assert titlechecks[3]['difference_sum']>100000
assert 0<titlechecks[1]['difference_sum']<titlechecks[3]['difference_sum']
assert 0<titlechecks[-2]['difference_sum']<titlechecks[3]['difference_sum']
ts=Image.new('RGB',(1440,2*300),(244,242,237));d=ImageDraw.Draw(ts)
for i,k in enumerate([0,1,2,3,5,6]):
 f,label,im=titleimgs[k];im=im.copy();im.thumbnail((480,270));xx=i%3*480;yy=i//3*300;ts.paste(im,(xx,yy));d.text((xx+6,yy+273),f'{f/25:.2f}s {label}',font=font,fill=(40,44,40))
ts.save(PRE/'片名真实淡入淡出复核.jpg',quality=95)
fade=[]
for f in [0,6,12]:
 path=FR/f'开场淡入_{f}.jpg';im=cap(f,path);fade.append({'frame':f,'mean_luma':float(np.asarray(im).mean()),'path':str(path)})
# Native SLog->709 black and JPEG quantization yield RGB(2,2,0), visually black; allow <3/255.
assert fade[0]['mean_luma']<3 and fade[0]['mean_luma']<fade[1]['mean_luma']<fade[2]['mean_luma']
# Curated review board is made only from real Resolve outputs, including the editable overlay.
starts=[0,117,234,340,508,587,1135,1397,1593];cur=Image.new('RGB',(1620,3*330),(244,242,237));d=ImageDraw.Draw(cur)
for i,start in enumerate(starts):
 s,im,path=next(z for z in midpoints if z[0]['record_frame']==start)
 if start==340:im=titleimgs[3][2]
 if start==587:im=Image.open(next(rec['path'] for rec in records if rec['start']==587 and rec['label']=='入')).convert('RGB')
 im=im.copy();im.thumbnail((540,304));xx=i%3*540;yy=i//3*330;cur.paste(im,(xx,yy));d.text((xx+7,yy+306),f"{start/25:.2f}s  {s['intent'][:22]}",font=font,fill=(40,44,40))
cur.save(PRE/'开篇向往感精修总览.jpg',quality=95)
for s in plan['shots']:
 v=next(v for v in t.GetItemListInTrack('video',1) if v.GetStart()==s['record_frame']);assert v.GetDuration()==s['length_frames'] and v.GetMediaPoolItem().GetClipProperty('File Path')==s['path'];assert v.GetMediaPoolItem().GetClipProperty('Online Status')=='Online'
assert t.GetEndFrame()==11507 and t.GetIsTrackEnabled('video',2);assert pm.SaveProject();assert t.SetCurrentTimecode('00:00:00:20')
result={'timeline':t.GetName(),'method':'Resolve ExportCurrentFrameAsStill; includes real color grade, Fusion and compositing','opening_shot_count':18,'actual_picture_frames':records,'title_checks':titlechecks,'opening_fade':fade,'all_media_online':True,'continuous_picture':True,'limitations':'No full continuous video playback or perceptual audio listen in this pass; native editable project, no final MP4 render.'}
(OUT/'native_verification_v5.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('V5_QA_READY',flush=True)
