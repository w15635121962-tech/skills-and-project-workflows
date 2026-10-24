import sys,json,time,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
sys.path.insert(0,'/Volumes/YSAigc/2026-2027/自动剪辑/20261017_双图包装与全片调色_v9/工作文件')
from common_v9 import connect,snap,capture,tc
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'调色预览';NAME='学校_通透感与高光控制_v11_20261017'
r,pm,p,mp,t=connect();assert t.GetName()=='学校_人文自然调色_v10_20261017',t.GetName()
last=ROOT.parent/'20261017_人文自然调色_v10/工作文件/final_native_snapshot_v10.json';assert snap(t)==json.loads(last.read_text()),'Inspect manual changes before editing'
graphs=[]
for track in range(1,t.GetTrackCount('video')+1):
    for it in t.GetItemListInTrack('video',track):
        g=it.GetNodeGraph();graphs.append({'track':track,'start':it.GetStart(),'version':it.GetCurrentVersion(),'nodes':g.GetNumNodes(),'luts':[g.GetLUT(j) for j in range(1,g.GetNumNodes()+1)]})
settings=p.GetSetting();color_settings={k:v for k,v in settings.items() if any(s in k.lower() for s in ['color','gamma','gamut','luminance','tonemap'])}
before={'timeline':t.GetName(),'snapshot':snap(t),'graphs':graphs,'page':r.GetCurrentPage(),'timecode':t.GetCurrentTimecode(),'color_settings':color_settings}
(OUT/'live_before_v11.json').write_text(json.dumps(before,ensure_ascii=False,indent=2));assert pm.SaveProject()
backup=ROOT/'学校_通透与高光调整前_v10备份.drt';assert not backup.exists() and t.Export(str(backup),r.EXPORT_DRT)
new=t.DuplicateTimeline(NAME);assert new and p.SetCurrentTimeline(new) and snap(new)==before['snapshot'];assert r.OpenPage('color') and pm.SaveProject()
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',18);frames=[]
def sheet(rows,index):
    image=Image.new('RGB',(1920,math.ceil(len(rows)/4)*305),(242,239,230));draw=ImageDraw.Draw(image)
    for i,row in enumerate(rows):
        im=Image.open(row['path']).convert('RGB');im.thumbnail((480,270));x=i%4*480;y=i//4*305;image.paste(im,(x,y));draw.text((x+4,y+273),f"V{row['track']} {row['start']/25:.2f}s · {Path(row['source']).name[:22]}",font=font,fill=(23,38,29))
    image.save(PRE/f'当前画面总览_{index:02d}.jpg',quality=94)
for track in [1,2]:
    for it in new.GetItemListInTrack('video',track):
        if track==2 and it.GetStart()==340:continue
        f=it.GetStart()+it.GetDuration()//2
        if track==1 and it.GetStart()==11042:f=11070
        path=PRE/'调整前'/f'{track}_{it.GetStart():05d}.jpg';im=capture(p,new,f,path,.12)
        a=np.asarray(im,dtype=float)/255;y=.2126*a[:,:,0]+.7152*a[:,:,1]+.0722*a[:,:,2]
        frames.append({'track':track,'start':it.GetStart(),'length':it.GetDuration(),'frame':f,'path':str(path),'source':it.GetMediaPoolItem().GetClipProperty('File Path'),'luma_quantiles':np.quantile(y,[.01,.1,.5,.9,.95,.99]).tolist(),'fraction_y_above_90':float(np.mean(y>.90)),'fraction_y_above_95':float(np.mean(y>.95)),'fraction_white_all_rgb_98':float(np.mean(np.all(a>.98,axis=2))),'fraction_any_channel_995':float(np.mean(np.max(a,axis=2)>.995))})
        if len(frames)%16==0:sheet(frames[-16:],len(frames)//16);print('V11_CURRENT_FRAMES',len(frames),flush=True)
if len(frames)%16:sheet(frames[-(len(frames)%16):],len(frames)//16+1)
(OUT/'current_frames_v11.json').write_text(json.dumps(frames,ensure_ascii=False,indent=2))
assert new.SetCurrentTimecode(tc(146)) and pm.SaveProject();print('V11_LIVE_BASELINE_READY',len(frames),flush=True)
