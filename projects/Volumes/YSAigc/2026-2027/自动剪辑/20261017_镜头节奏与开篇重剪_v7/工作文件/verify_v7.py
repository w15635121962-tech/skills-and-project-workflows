import sys,json,time,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'精剪预览'
FR=PRE/'全片实际画面';DET=PRE/'开篇与采访切口';FR.mkdir(exist_ok=True);DET.mkdir(exist_ok=True)
plan=json.loads((OUT/'edit_plan_v7.json').read_text());build=json.loads((OUT/'native_build_v7.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool();t=p.GetCurrentTimeline();assert t.GetName()==plan['name'];assert r.OpenPage('edit')
def tc(f):
    ss,ff=divmod(f,25);mm,ss=divmod(ss,60);hh,mm=divmod(mm,60);return f'{hh:02}:{mm:02}:{ss:02}:{ff:02}'
def cap(frame,path):
    if path.exists():
        im=Image.open(path).convert('RGB');assert im.size==(1920,1080);return im
    assert t.SetCurrentTimecode(tc(frame));time.sleep(.12)
    assert p.ExportCurrentFrameAsStill(str(path));im=Image.open(path).convert('RGB');assert im.size==(1920,1080);return im
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',17)
records=[];mids=[]
for s in plan['shots']:
    frame=s['record_frame']+s['length_frames']//2;path=FR/f"{s['index']:03d}_{tc(frame).replace(':','-')}.jpg";im=cap(frame,path)
    records.append({'index':s['index'],'start':s['record_frame'],'frame':frame,'path':str(path),'changed':s.get('revision_v7',False)});mids.append((s,im))
    if len(mids)%20==0:print('V7_ACTUAL_MAIN_FRAMES',len(mids),flush=True)
for start in range(0,len(mids),24):
    part=mids[start:start+24];sheet=Image.new('RGB',(1440,math.ceil(len(part)/4)*250),(244,242,236));d=ImageDraw.Draw(sheet)
    for i,(s,im) in enumerate(part):
        x=i%4*360;y=i//4*250;im=im.copy();im.thumbnail((360,203));sheet.paste(im,(x,y));d.text((x+5,y+205),f"{s['index']:03d} {tc(s['record_frame'])}  {s['length_frames']/25:.2f}s",font=font,fill=(28,33,30));d.text((x+5,y+227),s['intent'][:20],font=font,fill=(28,33,30))
    sheet.save(PRE/f'全片实际复核_{start//24+1}.jpg',quality=94)
opening=[s for s in plan['shots'] if s['record_frame']<1767];opening_recs=[];opening_rows=[]
for s in opening:
    row=[]
    for label,off in [('入',0),('中',s['length_frames']//2),('出',s['length_frames']-1)]:
        frame=s['record_frame']+off
        if label=='中':path=Path(next(a['path'] for a in records if a['start']==s['record_frame']));im=Image.open(path).convert('RGB')
        else:path=DET/f"开篇_{s['record_frame']}_{label}.jpg";im=cap(frame,path)
        opening_recs.append({'start':s['record_frame'],'label':label,'frame':frame,'path':str(path)});row.append((label,im))
    opening_rows.append((s,row))
    if len(opening_rows)%10==0:print('V7_OPENING_TRIPLETS',len(opening_rows),flush=True)
for start in range(0,len(opening_rows),10):
    part=opening_rows[start:start+10];sheet=Image.new('RGB',(1440,len(part)*295),(244,242,236));d=ImageDraw.Draw(sheet)
    for i,(s,row) in enumerate(part):
        for j,(label,im) in enumerate(row):
            im=im.copy();im.thumbnail((480,270));x=j*480;y=i*295;sheet.paste(im,(x,y));d.text((x+5,y+272),f"{tc(s['record_frame'])}  {label}  {s['intent'][:16]}",font=font,fill=(28,33,30))
    sheet.save(PRE/f'开篇首中尾实际复核_{start//10+1}.jpg',quality=95)
overlays=[];ovimgs=[]
for s in plan['interview_overlays_v7']:
    for label,off in [('入',0),('中',s['length_frames']//2),('出',s['length_frames']-1)]:
        frame=s['record_frame']+off;path=DET/f"采访_{s['record_frame']}_{label}.jpg";im=cap(frame,path);overlays.append({'start':s['record_frame'],'label':label,'frame':frame,'path':str(path)});ovimgs.append((s,label,im))
sheet=Image.new('RGB',(1440,len(plan['interview_overlays_v7'])*295),(244,242,236));d=ImageDraw.Draw(sheet)
for i,(s,label,im) in enumerate(ovimgs):
    im=im.copy();im.thumbnail((480,270));x=i%3*480;y=i//3*295;sheet.paste(im,(x,y));d.text((x+5,y+272),f"{tc(s['record_frame'])}  {label}  {s['intent'][:15]}",font=font,fill=(28,33,30))
sheet.save(PRE/'校长原声补画_实际复核.jpg',quality=95)
title_samples=[]
for frame in [0,6,340,352,395,451,507,3861,4002,11407,11457,11506]:
    path=DET/f'字幕衔接_{frame}.jpg';cap(frame,path);title_samples.append({'frame':frame,'path':str(path)})
v1=t.GetItemListInTrack('video',1)
assert len(v1)==len(plan['shots']) and t.GetEndFrame()==11507
for s,v in zip(plan['shots'],v1):
    assert v.GetStart()==s['record_frame'] and v.GetDuration()==s['length_frames']
    assert v.GetMediaPoolItem().GetClipProperty('File Path')==s['path']
    assert v.GetMediaPoolItem().GetClipProperty('Online Status')=='Online'
    if s.get('revision_v7'):assert v.GetLeftOffset()==round(s['in']*25)
assert all(a.GetEnd()==b.GetStart() for a,b in zip(v1,v1[1:]))
files={x['path'] for x in records+opening_recs+overlays+title_samples}
result={'timeline':t.GetName(),'method':'Real Resolve exported stills, including actual LUT, Fusion, and track compositing','duration_seconds':460.28,'picture_count':len(v1),'main_frames':records,'opening_triplets':opening_recs,'interview_samples':overlays,'title_samples':title_samples,'unique_actual_stills':len(files),'all_picture_media_online':True,'no_picture_gaps':True,'complete_continuous_listen_or_watch':False}
(OUT/'native_verification_v7.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
assert t.SetCurrentTimecode('00:00:00:20') and pm.SaveProject();print('V7_ACTUAL_QA_READY',len(files),flush=True)
