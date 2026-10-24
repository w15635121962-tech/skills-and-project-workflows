import sys,json,time,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'精剪预览';FR=PRE/'动态精修实际画面';FR.mkdir(exist_ok=True)
plan=json.loads((OUT/'edit_plan_v8.json').read_text());build=json.loads((OUT/'native_build_v8.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool();t=p.GetCurrentTimeline();assert t.GetName()==plan['name'];assert r.OpenPage('edit')
def tc(f):
    ss,ff=divmod(f,25);mm,ss=divmod(ss,60);return f'00:{mm:02d}:{ss:02d}:{ff:02d}'
def cap(f,path):
    if path.exists():
        im=Image.open(path).convert('RGB');assert im.size==(1920,1080);return im
    assert t.SetCurrentTimecode(tc(f));time.sleep(.10);assert p.ExportCurrentFrameAsStill(str(path));im=Image.open(path).convert('RGB');assert im.size==(1920,1080);return im
# Continuous native frames of a second representative shot verify the pull-out
# and a 1920x1080 source. Bypass only the new Transform, restore it before saving.
rep=next(m for m in build['motion_records'] if m['record_frame']==2453);item=next(v for v in t.GetItemListInTrack('video',1) if v.GetStart()==2453);comp=item.GetFusionCompByIndex(1);xf=comp.FindTool('V8_GentleMotion');assert xf
seq=OUT/'拉远连续帧2453';seq.mkdir(exist_ok=True);assert pm.SaveProject()
try:
    for label,bypass in [('before',True),('after',False)]:
        folder=seq/label;folder.mkdir(exist_ok=True);xf.SetAttrs({'TOOLB_PassThrough':bypass});assert xf.GetAttrs()['TOOLB_PassThrough']==bypass
        for off in range(rep['length_frames']):
            cap(rep['record_frame']+off,folder/f'{off:04d}.jpg')
            if (off+1)%25==0:print('V8_PULL_CONTINUOUS',label,off+1,flush=True)
finally:
    xf.SetAttrs({'TOOLB_PassThrough':False});assert not xf.GetAttrs()['TOOLB_PassThrough']
(OUT/'pull_sample_v8.json').write_text(json.dumps(dict(rep,baseline_frames=str(seq/'before'),animated_frames=str(seq/'after')),ensure_ascii=False,indent=2))
changed={s['record_frame'] for s in plan['source_replacements_v8']}|{m['record_frame'] for m in plan['motion_v8']};motions={m['record_frame']:m for m in plan['motion_v8']};repls={s['record_frame'] for s in plan['source_replacements_v8']}
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',17);records=[];rows=[]
for s in plan['shots']:
    if s['record_frame'] not in changed:continue
    row=[]
    for label,off in [('入',0),('中',s['length_frames']//2),('出',s['length_frames']-1)]:
        f=s['record_frame']+off;path=FR/f"{s['record_frame']}_{label}.jpg";im=cap(f,path);records.append({'start':s['record_frame'],'frame':f,'label':label,'path':str(path)});row.append((label,im))
    rows.append((s,row))
    if len(rows)%10==0:print('V8_ACTUAL_TRIPLETS',len(rows),flush=True)
for start in range(0,len(rows),8):
    part=rows[start:start+8];sheet=Image.new('RGB',(1440,len(part)*295),(244,242,235));d=ImageDraw.Draw(sheet)
    for i,(s,row) in enumerate(part):
        m=motions.get(s['record_frame']);flag=('动态换镜 ' if s['record_frame'] in repls else '')+({'push':'缓推','pull':'拉远'}.get(m['kind'],'') if m else '')
        for j,(label,im) in enumerate(row):
            im=im.copy();im.thumbnail((480,270));x=j*480;y=i*295;sheet.paste(im,(x,y));d.text((x+5,y+272),f"{s['record_frame']/25:.2f}s {label} {flag} {s['intent'][:12]}",font=font,fill=(32,37,30))
    sheet.save(PRE/f'动态与缓推_实际首中尾_{start//8+1}.jpg',quality=95)
titles=[]
for f in [395,396,424,451,452,480,507]:
    path=FR/f'片名_{f}.jpg';cap(f,path);titles.append({'frame':f,'path':str(path)})
v1=t.GetItemListInTrack('video',1);assert len(v1)==188 and t.GetEndFrame()==11507
for s,v in zip(plan['shots'],v1):
    assert v.GetStart()==s['record_frame'] and v.GetDuration()==s['length_frames'] and v.GetMediaPoolItem().GetClipProperty('File Path')==s['path']
    assert v.GetMediaPoolItem().GetClipProperty('Online Status')=='Online'
    if s['record_frame'] in repls:assert v.GetLeftOffset()==round(s['in']*25)
for m in plan['motion_v8']:
    v=next(v for v in v1 if v.GetStart()==m['record_frame']);c=v.GetFusionCompByIndex(1);xf=c.FindTool('V8_GentleMotion');assert xf and not xf.GetAttrs()['TOOLB_PassThrough']
    center=xf.GetInput('Center');assert abs(center[1]-.5)<1e-8 and abs(center[2]-.5)<1e-8 and abs(center.get(3,0))<1e-8
    a=int(c.GetAttrs()['COMPN_RenderStart']);z=int(c.GetAttrs()['COMPN_RenderEnd'])
    for f in range(a,z+1):
        u=(f-a)/(z-a);expected=m['start_size']+(m['end_size']-m['start_size'])*u*u*(3-2*u);assert abs(xf.GetInput('Size',f)-expected)<1e-7
assert all(a.GetEnd()==b.GetStart() for a,b in zip(v1,v1[1:]))
result={'timeline':t.GetName(),'affected_main_shots':len(changed),'actual_triplet_stills':records,'title_samples':titles,'unique_affected_actual_stills':len({x['path'] for x in records+titles}),'motion_comp_count':len(motions),'each_native_frame_curve_readback_passed':True,'all_centers_fixed':True,'all_new_transforms_enabled':True,'all_picture_media_online':True,'no_gaps':True,'duration_seconds':460.28,'picture_count':188,'continuous_pull_sample_frames':rep['length_frames']*2,'continuous_manual_whole_film_watch_or_listen':False}
(OUT/'native_verification_v8.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));assert t.SetCurrentTimecode('00:00:00:20') and pm.SaveProject();print('V8_NATIVE_QA_READY',len(changed),len(records)+len(titles),flush=True)
