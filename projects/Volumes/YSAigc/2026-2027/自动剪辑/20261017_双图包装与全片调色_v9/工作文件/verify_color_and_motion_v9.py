from common_v9 import *
from PIL import Image,ImageDraw,ImageFont
import numpy as np
r,pm,p,mp,t=connect();assert t.GetName()==NAME and r.OpenPage('edit')
data=json.loads((OUT/'native_color_applied_v9.json').read_text());records=[];actual=[]
def stats(im):
    a=np.asarray(im.convert('RGB'),dtype=float)/255;y=.2126*a[:,:,0]+.7152*a[:,:,1]+.0722*a[:,:,2]
    return {'luma_quantiles':np.quantile(y,[.01,.10,.5,.9,.99]).tolist(),'white':float(np.mean(np.all(a>.985,axis=2))),'black':float(np.mean(np.all(a<.008,axis=2))),'clipped_any_channel':float(np.mean(np.max(a,axis=2)>.995))}
cache={}
for s in data['records']:
    item=next(x for x in t.GetItemListInTrack('video',s['track']) if x.GetStart()==s['start'])
    first=s['start'];last=s['start']+item.GetDuration()-1
    if s['track']==1 and s['start']==11042:last=11152
    for label,f in [('入',first),('中',s['frame']),('出',last)]:
        path=PRE/'调色后实际画面'/f"{s['track']}_{s['start']:05d}_{label}.jpg"
        if f not in cache:cache[f]=(path,capture(p,t,f,path,.13))
        else:
            op,im=cache[f];im.save(path,quality=95)
        im=cache[f][1];actual.append({'track':s['track'],'start':s['start'],'label':label,'frame':f,'path':str(path)})
        if label=='中':midpath=path;after=im.copy()
    before=Image.open(s['before']).convert('RGB');a=stats(before);b=stats(after)
    ar=np.asarray(after,dtype=float);br=np.asarray(before,dtype=float)
    mean_delta=float(np.abs(ar-br).mean())
    flags=[]
    if b['white']-a['white']>.01:flags.append('white_clipping_increase_over_1pct')
    if b['black']-a['black']>.015:flags.append('black_crush_increase_over_1_5pct')
    if mean_delta<.03:flags.append('possible_noop')
    records.append(dict(s,after=str(midpath),before_stats=a,after_stats=b,mean_pixel_delta=mean_delta,flags=flags))
    if len(records)%10==0:print('V9_COLOR_TRIPLETS',len(records),flush=True)
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',18)
for start in range(0,len(records),8):
    part=records[start:start+8];sheet=Image.new('RGB',(1920,4*310),(242,239,230));d=ImageDraw.Draw(sheet)
    for n,x in enumerate(part):
        col=n%2;row=n//2
        for k,key in enumerate(['before','after']):
            im=Image.open(x[key]).convert('RGB');im.thumbnail((480,270));px=col*960+k*480;py=row*310;sheet.paste(im,(px,py));d.text((px+5,py+275),f"V{x['track']} {x['start']/25:.2f}s {'调色前' if k==0 else '调色后'}",font=font,fill=(25,38,32))
    sheet.save(PRE/f'逐镜调色对照_{start//8+1}.jpg',quality=94)
save('native_color_qa_v9.json',{'records':records,'actual_after_frames':actual,'actual_frames_count':len(actual),'unique_frames':len(cache),'automated_flags':[{'track':x['track'],'start':x['start'],'flags':x['flags']} for x in records if x['flags']],'stats_are_display_frame_comparisons_not_camera_scene_luminance':True,'continuous_manual_full_watch':False})
print('V9_COLOR_QA_CAPTURED',len(records),flush=True)
# Every native timeline frame of the full 4.4-second paired-photo prototype.
seq=OUT/'双图连续25帧';seq.mkdir(exist_ok=True)
for i in range(110):
    path=seq/f'{i:04d}.jpg';capture(p,t,4051+i,path,.11)
    if (i+1)%25==0:print('V9_NATIVE_PAIR_MOTION_FRAMES',i+1,flush=True)
assert t.SetCurrentTimecode(tc(7536)) and pm.SaveProject();print('V9_COLOR_AND_CONTINUOUS_PAIR_READY',flush=True)
