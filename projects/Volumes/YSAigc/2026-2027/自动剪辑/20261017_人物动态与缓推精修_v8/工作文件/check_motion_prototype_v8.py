import json,hashlib
from pathlib import Path
import numpy as np
import av
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'精剪预览'
spec=json.loads((OUT/'motion_prototype_v8.json').read_text());before=Path(spec['baseline_frames']);after=Path(spec['animated_frames'])
xs=np.linspace(70,1850,180).astype(int);ys=np.linspace(45,1035,100).astype(int)
records=[]
for f in range(7,60):
    a=np.asarray(Image.open(before/f'{f:04d}.jpg').convert('L'),dtype=np.float32)
    b=np.asarray(Image.open(after/f'{f:04d}.jpg').convert('L'),dtype=np.float32)[np.ix_(ys,xs)]
    expected=spec['size_values'][f];candidates=np.linspace(expected-.0015,expected+.0015,31);scores=[]
    for scale in candidates:
        xx=(xs-960)/scale+960;yy=(ys-540)/scale+540;x0=np.floor(xx).astype(int);y0=np.floor(yy).astype(int);wx=(xx-x0)[None,:];wy=(yy-y0)[:,None]
        pred=(a[np.ix_(y0,x0)]*(1-wx)+a[np.ix_(y0,x0+1)]*wx)*(1-wy)+(a[np.ix_(y0+1,x0)]*(1-wx)+a[np.ix_(y0+1,x0+1)]*wx)*wy
        scores.append(float(np.abs(pred-b).mean()))
    j=int(np.argmin(scores));records.append({'frame':f,'expected_size':expected,'estimated_size_from_actual_pixels':float(candidates[j]),'gray_mae':scores[j]})
errors=[abs(x['estimated_size_from_actual_pixels']-x['expected_size']) for x in records]
estimated=np.array([x['estimated_size_from_actual_pixels'] for x in records]);expected=np.array([x['expected_size'] for x in records]);delta_error=np.diff(estimated)-np.diff(expected)
hashes=[hashlib.sha256((after/f'{f:04d}.jpg').read_bytes()).hexdigest() for f in range(7,60)]
result={'fps':25,'native_contiguous_frames_examined':60,'baseline_and_animation_frames':120,'method':'Compare every native rendered animation frame against the same native unanimated frame; fit subpixel scale from actual pixels. Exclude 7 fade frames from scale fitting.','per_frame':records,'max_scale_error':max(errors),'max_adjacent_scale_delta_error':float(np.max(np.abs(delta_error))),'min_estimated_scale_step':float(np.min(np.diff(estimated))),'adjacent_duplicate_frame_count':sum(a==b for a,b in zip(hashes,hashes[1:])),'no_manual_continuous_watch_or_listen':True}
result['passed']=max(errors)<.0012 and result['max_adjacent_scale_delta_error']<.00065 and result['min_estimated_scale_step']>-.00035 and result['adjacent_duplicate_frame_count']==0
(OUT/'motion_prototype_pixel_verification_v8.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='per_frame'},ensure_ascii=False,indent=2),flush=True)
assert result['passed'],'Review measured rendered motion before applying it broadly'
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',25)
dest=PRE/'开篇缓推_25帧连续画面对比.mp4';assert not dest.exists()
with av.open(str(dest),'w') as container:
    stream=container.add_stream('libx264',rate=25);stream.width=1920;stream.height=600;stream.pix_fmt='yuv420p';stream.options={'crf':'20','preset':'medium'}
    for f in range(60):
        panel=Image.new('RGB',(1920,600),(244,242,235));d=ImageDraw.Draw(panel)
        for i,folder in enumerate([before,after]):
            im=Image.open(folder/f'{f:04d}.jpg').convert('RGB').resize((960,540),Image.Resampling.LANCZOS);panel.paste(im,(i*960,50))
        d.text((20,10),'原构图',font=font,fill=(35,39,31));d.text((980,10),'v8 · 3%缓推 · 固定中心',font=font,fill=(35,39,31))
        frame=av.VideoFrame.from_image(panel)
        for packet in stream.encode(frame):container.mux(packet)
    for packet in stream.encode():container.mux(packet)
with av.open(str(dest)) as c:
    s=c.streams.video[0];count=sum(1 for _ in c.decode(s));duration=float(s.duration*s.time_base);assert count==60 and abs(float(s.average_rate)-25)<1e-6 and abs(duration-2.4)<.01
result['comparison_preview']={'path':str(dest),'width':1920,'height':600,'fps':25,'frames':count,'duration_seconds':duration,'audio':False,'only_encoded_native_stills_for_motion_review':True}
(OUT/'motion_prototype_pixel_verification_v8.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
sheet=Image.new('RGB',(1440,3*430),(244,242,235));d=ImageDraw.Draw(sheet)
for row,f in enumerate([8,30,59]):
    for col,folder in enumerate([before,after]):
        im=Image.open(folder/f'{f:04d}.jpg').convert('RGB').resize((720,405),Image.Resampling.LANCZOS);sheet.paste(im,(col*720,row*430));d.text((col*720+7,row*430+405),f'{f/25:.2f}s  '+('原构图' if col==0 else 'v8 缓推'),font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',18),fill=(35,39,31))
sheet.save(PRE/'开篇缓推_连续帧检查.jpg',quality=95)
print('V8_MOTION_PIXEL_CHECK_AND_PREVIEW_READY',flush=True)
