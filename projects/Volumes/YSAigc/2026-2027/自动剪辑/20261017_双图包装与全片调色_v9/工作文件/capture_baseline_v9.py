from common_v9 import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np
r,pm,p,mp,t=connect();assert t.GetName()==NAME
assert r.OpenPage('edit')
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',18)
plan=json.loads((BASE/'edit_plan_v8.json').read_text());shots={s['record_frame']:s for s in plan['shots']}
frames=[]
for track in [1,2]:
    for it in t.GetItemListInTrack('video',track):
        if track==2 and it.GetStart()<10842:continue
        f=it.GetStart()+it.GetDuration()//2
        path=PRE/'调色前'/f'{track}_{it.GetStart():05d}.jpg'
        if path.exists():im=Image.open(path).convert('RGB')
        else:im=capture(p,t,f,path)
        ar=np.asarray(im,dtype=float)/255
        y=ar@np.array([.2126,.7152,.0722]);active=y>.01
        vals=y[active]
        frames.append({'track':track,'start':it.GetStart(),'frame':f,'length':it.GetDuration(),'path':str(path),'source':it.GetMediaPoolItem().GetClipProperty('File Path'),'photo':shots.get(it.GetStart(),{}).get('is_photo',False),'luma_quantiles':np.quantile(vals,[.01,.10,.50,.90,.99]).tolist(),'bright_pixel_fraction':float(np.mean(np.max(ar,axis=2)>.985)),'mean_rgb':ar[active].mean(axis=0).tolist()})
        if len(frames)%20==0:print('V9_BASELINE_FRAMES',len(frames),flush=True)
for a in range(0,len(frames),16):
    part=frames[a:a+16];sheet=Image.new('RGB',(1920,4*305),(244,241,232));d=ImageDraw.Draw(sheet)
    for n,x in enumerate(part):
        im=Image.open(x['path']).convert('RGB');im.thumbnail((480,270));px=n%4*480;py=n//4*305;sheet.paste(im,(px,py))
        title=f"{x['start']/25:.2f}s {'图片' if x['photo'] else '实拍'} {Path(x['source']).name[:24]}"
        d.text((px+5,py+273),title,font=font,fill=(25,32,29))
    sheet.save(PRE/f'调色前总览_{a//16+1:02d}.jpg',quality=94)
save('color_baseline_v9.json',frames);assert t.SetCurrentTimecode('00:00:00:20')
print('V9_BASELINE_CAPTURED',len(frames),flush=True)
