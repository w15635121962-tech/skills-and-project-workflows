import json,hashlib
from pathlib import Path
import av,numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'精剪预览';spec=json.loads((OUT/'pull_sample_v8.json').read_text())
before=Path(spec['baseline_frames']);after=Path(spec['animated_frames']);xs=np.linspace(70,1850,180).astype(int);ys=np.linspace(45,1035,100).astype(int);records=[]
for f,value in enumerate(spec['size_values']):
    a=np.asarray(Image.open(before/f'{f:04d}.jpg').convert('L'),dtype=np.float32);b=np.asarray(Image.open(after/f'{f:04d}.jpg').convert('L'),dtype=np.float32)[np.ix_(ys,xs)]
    candidates=np.linspace(value-.0015,value+.0015,31);scores=[]
    for scale in candidates:
        xx=(xs-960)/scale+960;yy=(ys-540)/scale+540;x0=np.floor(xx).astype(int);y0=np.floor(yy).astype(int);wx=(xx-x0)[None,:];wy=(yy-y0)[:,None]
        pred=(a[np.ix_(y0,x0)]*(1-wx)+a[np.ix_(y0,x0+1)]*wx)*(1-wy)+(a[np.ix_(y0+1,x0)]*(1-wx)+a[np.ix_(y0+1,x0+1)]*wx)*wy
        scores.append(float(np.abs(pred-b).mean()))
    j=int(np.argmin(scores));records.append({'frame':f,'expected_size':value,'estimated_size_from_actual_pixels':float(candidates[j]),'gray_mae':scores[j]})
estimated=np.array([x['estimated_size_from_actual_pixels'] for x in records]);expected=np.array(spec['size_values']);hashes=[hashlib.sha256((after/f'{f:04d}.jpg').read_bytes()).hexdigest() for f in range(len(records))]
result={'fps':25,'native_contiguous_pull_frames_examined':len(records),'paired_native_stills':len(records)*2,'max_scale_error':float(np.max(np.abs(estimated-expected))),'max_adjacent_scale_delta_error':float(np.max(np.abs(np.diff(estimated)-np.diff(expected)))),'min_monotonic_motion_progress':float(np.min(-np.diff(estimated))),'adjacent_duplicate_frame_count':sum(a==b for a,b in zip(hashes,hashes[1:])),'per_frame':records,'manual_continuous_watch_claimed':False}
result['passed']=result['max_scale_error']<.0012 and result['max_adjacent_scale_delta_error']<.00065 and result['min_monotonic_motion_progress']>-.00035 and result['adjacent_duplicate_frame_count']==0
(OUT/'pull_pixel_verification_v8.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='per_frame'},ensure_ascii=False,indent=2));assert result['passed']
push=json.loads((OUT/'motion_prototype_v8.json').read_text());samples=[dict(push,kind='缓推3%'),dict(spec,kind='拉远2.9%')];font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',25)
dest=PRE/'缓推与拉远_25帧实际对比预览_无声.mp4';assert not dest.exists();total=0
with av.open(str(dest),'w') as container:
    stream=container.add_stream('libx264',rate=25);stream.width=1920;stream.height=600;stream.pix_fmt='yuv420p';stream.options={'crf':'20','preset':'medium'}
    for sample in samples:
        for f in range(len(sample['size_values'])):
            panel=Image.new('RGB',(1920,600),(244,242,235));d=ImageDraw.Draw(panel)
            for col,key in enumerate(['baseline_frames','animated_frames']):
                im=Image.open(Path(sample[key])/f'{f:04d}.jpg').convert('RGB').resize((960,540),Image.Resampling.LANCZOS);panel.paste(im,(col*960,50))
            d.text((20,10),'原构图',font=font,fill=(35,39,31));d.text((980,10),'v8 · 固定中心 · '+sample['kind'],font=font,fill=(35,39,31))
            frame=av.VideoFrame.from_image(panel)
            for packet in stream.encode(frame):container.mux(packet)
            total+=1
    for packet in stream.encode():container.mux(packet)
with av.open(str(dest)) as c:
    s=c.streams.video[0];count=sum(1 for _ in c.decode(s));duration=float(s.duration*s.time_base);assert count==total and abs(float(s.average_rate)-25)<1e-6 and abs(duration-total/25)<.01
meta={'path':str(dest),'fps':25,'frames':count,'duration_seconds':duration,'width':1920,'height':600,'audio':False,'method':'Encode paired actual native timeline stills at 25fps; not a full-film export','push_frame_pixel_check':True,'pull_frame_pixel_check':True}
(OUT/'motion_preview_verification_v8.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));print('V8_MOTION_PREVIEW_READY',json.dumps(meta,ensure_ascii=False),flush=True)
