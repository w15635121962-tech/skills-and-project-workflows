from common_v9 import *
from PIL import Image
import numpy as np
import av
seq=OUT/'双图连续25帧';paths=sorted(seq.glob('*.jpg'));assert len(paths)==110
dest=PRE/'双图分屏与缓推_25帧预览_无声.mp4';assert not dest.exists()
container=av.open(str(dest),'w');stream=container.add_stream('libx264',rate=25);stream.width=1920;stream.height=1080;stream.pix_fmt='yuv420p';stream.options={'crf':'19','preset':'medium'}
prev=None;duplicates=0;boxes={'left':[],'right':[]}
for i,path in enumerate(paths):
    im=Image.open(path).convert('RGB');a=np.asarray(im);paper=a[50,50,:].astype(int)
    if prev is not None and np.array_equal(a[215:850,70:1850],prev[215:850,70:1850]):duplicates+=1
    prev=a.copy()
    for side,(x0,x1) in {'left':(60,950),'right':(975,1860)}.items():
        sub=a[215:850,x0:x1].astype(int);mask=np.max(np.abs(sub-paper),axis=2)>28;yy,xx=np.nonzero(mask)
        assert len(xx)>10000
        boxes[side].append([int(xx.min()+x0),int(yy.min()+215),int(xx.max()+x0),int(yy.max()+215)])
    frame=av.VideoFrame.from_image(im)
    for packet in stream.encode(frame):container.mux(packet)
for packet in stream.encode():container.mux(packet)
container.close()
box_checks=[]
for side,items in boxes.items():
    b=np.array(items);width=b[:,2]-b[:,0]+1;cx=(b[:,0]+b[:,2])/2
    u=np.arange(110)/109;curve=u*u*(3-2*u)
    expected=width[0]+(width[-1]-width[0])*curve
    result={'side':side,'first_last_width':[int(width[0]),int(width[-1])],'smooth_curve_max_pixel_error':float(np.max(np.abs(width-expected))),'center_max_drift_pixels':float(np.max(np.abs(cx-cx[0]))),'max_adjacent_width_step':int(np.max(np.abs(np.diff(width))))}
    assert result['smooth_curve_max_pixel_error']<=3 and result['center_max_drift_pixels']<=1.5 and result['max_adjacent_width_step']<=2,result
    assert width[-1]>width[0] if side=='left' else width[-1]<width[0]
    box_checks.append(result)
with av.open(str(dest)) as f:
    v=f.streams.video[0];decoded=sum(1 for _ in f.decode(v));fps=float(v.average_rate);size=[v.width,v.height];audio_count=len(f.streams.audio)
assert decoded==110 and fps==25 and size==[1920,1080] and audio_count==0 and duplicates==0
save('pair_motion_preview_verified_v9.json',{'path':str(dest),'seconds':4.4,'fps':fps,'frames':decoded,'resolution':size,'audio_streams':audio_count,'native_timeline_sequence':str(seq),'adjacent_duplicate_frames':duplicates,'rendered_image_motion_checks':box_checks,'native_floating_point_editable_transforms':True,'whole_film_exported':False})
print('V9_PAIR_PREVIEW_VERIFIED',box_checks,flush=True)
