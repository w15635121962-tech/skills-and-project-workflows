import sys,json,time
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
sys.path.insert(0,'/Volumes/YSAigc/2026-2027/自动剪辑/20261017_双图包装与全片调色_v9/工作文件')
from common_v9 import connect,snap,tc
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'调色预览';NAME='学校_通透感与高光控制_v11_20261017'
r,pm,p,mp,t=connect();assert t.GetName()==NAME and r.OpenPage('edit')
before=json.loads((OUT/'live_before_v11.json').read_text());assert snap(t)==before['snapshot']
frames={(x['track'],x['start']):x for x in json.loads((OUT/'current_frames_v11.json').read_text())}
protos={(x['track'],x['start']):x for x in json.loads((OUT/'prototype_v11.json').read_text())['records']}
prior_rows=json.loads((ROOT.parent/'20261017_双图包装与全片调色_v9/工作文件/native_color_applied_v9.json').read_text())['records']+json.loads((ROOT.parent/'20261017_人文自然调色_v10/工作文件/native_color_v10.json').read_text())['records']
known={(x['track'],x['start']):x['cdl'] for x in prior_rows}
def make(s,o,pow,sat):return {'NodeIndex':'1','Slope':' '.join(map(str,s)),'Offset':' '.join(map(str,o)),'Power':' '.join(map(str,pow)),'Saturation':str(sat)}
neutral=make([1]*3,[0]*3,[1]*3,1)
targets={key:dict(row,kind='highlights' if row['start'] in [117,4365,1340,2453] else 'density') for key,row in protos.items()}
for st,s,o,power,sat,reason in [
 (6080,.985,-.002,1.025,1.01,'与4365同场朗读轻收亮面，保留儿童柔光'),
 (6847,.988,-.002,1.018,1,'小学女生脸手与纸页增加亮面密度'),
 (3003,.985,-.002,1.01,1,'合唱白制服与日照人物轻收上部亮度'),
 (10432,.985,-.002,1.01,1,'日照讲话主体与白衬衫控制亮面，保留红幕自然色'),
 (452,1.015,-.018,1.005,1.01,'树干、楼面与光晕外围增强分离，保留太阳白芯'),
 (8220,1.015,-.012,.99,1,'展旗逆光轻定深衣与建筑暗部，保持面部与红旗'),
 (9310,1.015,-.012,.99,1.01,'跑步制服与树荫分离，保留面部和逆光空气感'),
]:
    targets[1,st]=dict(frames[1,st],cdl=make([s]*3,[o]*3,[power]*3,sat),kind='highlights' if st in [6080,6847,3003,10432] else 'density',reason=reason)
for st in [1204,1931,2641,2689,3128,4289,6575,8997]:
    old=known.get((1,st),neutral);gain=1.015 if st==8997 else 1.012;off=-.012 if st==8997 else -.009;power=.992 if st==8997 else .994
    slope=[float(x)*gain for x in old['Slope'].split()];offset=[float(x)+off for x in old['Offset'].split()];powers=[float(x)*power for x in old['Power'].split()];sat=float(old['Saturation'])*(1 if st==8997 else 1.01)
    targets[1,st]=dict(frames[1,st],cdl=make(slope,offset,powers,sat),kind='density',reason='在现有肤色与白平衡基础上轻定黑位、增加中低调分离，保持面部中间调',prior_cdl_reference=old)
old=known[1,7151];targets[1,7151]=dict(frames[1,7151],cdl=make([float(x)*.975 for x in old['Slope'].split()],[float(x)-.001 for x in old['Offset'].split()],[float(x)*1.012 for x in old['Power'].split()],float(old['Saturation'])),kind='highlights',reason='科技教师白衣与屏幕温和收亮，保留原中性校正',prior_cdl_reference=old)
assert len(targets)==22
def stable_cap(tl,f,path):
    path=Path(path);path.parent.mkdir(exist_ok=True,parents=True);check=path.with_name(path.stem+'_check.jpg')
    assert tl.SetCurrentTimecode(tc(f));time.sleep(.55);assert p.ExportCurrentFrameAsStill(str(path))
    previous=np.asarray(Image.open(path).convert('RGB'),dtype=float)
    for attempt in range(3):
        time.sleep(.25);assert p.ExportCurrentFrameAsStill(str(check));current=np.asarray(Image.open(check).convert('RGB'),dtype=float);delta=float(np.abs(previous-current).mean())
        if delta<.1:
            if attempt:path.write_bytes(check.read_bytes())
            return Image.open(path).convert('RGB'),delta
        previous=current;path.write_bytes(check.read_bytes())
    raise AssertionError(('Frame did not settle',f,delta))
original=next(p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()==before['timeline'])
try:
    assert p.SetCurrentTimeline(original) and snap(original)==before['snapshot']
    for i,(key,row) in enumerate(sorted(targets.items()),1):
        path=PRE/'调整前稳定复核'/f"{row['track']}_{row['start']:05d}.jpg";im,delta=stable_cap(original,row['frame'],path)
        row['before_stable']=str(path);row['before_capture_repeat_delta']=delta
        oldim=np.asarray(Image.open(row['path']).convert('RGB'),dtype=float);row['baseline_fast_capture_delta']=float(np.abs(oldim-np.asarray(im,dtype=float)).mean())
        if i%6==0:print('V11_BASELINE_STABLE',i,flush=True)
finally:assert p.SetCurrentTimeline(t)
records=[];assert pm.SaveProject()
for i,(key,row) in enumerate(sorted(targets.items()),1):
    it=next(x for x in t.GetItemListInTrack('video',row['track']) if x.GetStart()==row['start']);g=it.GetNodeGraph();assert g.GetNumNodes()==1;lut=g.GetLUT(1)
    if key in protos:prior=protos[key]['prior_version'];assert it.GetCurrentVersion()['versionName']=='v11_通透与高光控制'
    else:
        prior=it.GetCurrentVersion();assert 'v11_通透与高光控制' not in it.GetVersionNameList(0)
        assert it.AddVersion('v11_通透与高光控制',0) and it.LoadVersionByName('v11_通透与高光控制',0)
    assert it.SetCDL(row['cdl']) and it.GetNodeGraph().GetLUT(1)==lut
    records.append(dict(row,prior_version=prior,active_version=it.GetCurrentVersion(),lut=lut))
assert snap(t)==before['snapshot'] and pm.SaveProject();(OUT/'native_color_applied_v11.json').write_text(json.dumps({'records':records,'count':len(records),'picture_timing_fusion_layout_and_audio_unchanged':True},ensure_ascii=False,indent=2));print('V11_ALL_NATIVE_COLORS_APPLIED',flush=True)
def stats(im):
    a=np.asarray(im,dtype=float)/255;y=.2126*a[:,:,0]+.7152*a[:,:,1]+.0722*a[:,:,2]
    return {'luma_quantiles':np.quantile(y,[.01,.1,.5,.9,.95,.99]).tolist(),'above_95':float(np.mean(y>.95)),'white_all_98':float(np.mean(np.all(a>.98,axis=2))),'black_all_008':float(np.mean(np.all(a<.008,axis=2))),'any_channel_995':float(np.mean(np.max(a,axis=2)>.995))}
actual=[]
for i,row in enumerate(records,1):
    it=next(x for x in t.GetItemListInTrack('video',row['track']) if x.GetStart()==row['start']);end=it.GetEnd()-1
    if row['start']==11042:end=11152
    for label,f in [('入',it.GetStart()),('中',row['frame']),('出',end)]:
        path=PRE/'调整后'/f"{row['track']}_{row['start']:05d}_{label}.jpg";im,delta=stable_cap(t,f,path);actual.append({'track':row['track'],'start':row['start'],'label':label,'frame':f,'path':str(path),'capture_repeat_delta':delta})
        if label=='中':after=im.copy();row['after_stable']=str(path)
    bef=Image.open(row['before_stable']).convert('RGB');a=stats(bef);b=stats(after);delta=float(np.abs(np.asarray(bef,dtype=float)-np.asarray(after,dtype=float)).mean());flags=[]
    if delta>30:flags.append('possible_wrong_or_unsettled_frame')
    if delta<.03:flags.append('possible_noop')
    if b['white_all_98']-a['white_all_98']>.005:flags.append('white_clipping_increased')
    if b['black_all_008']-a['black_all_008']>.015:flags.append('dark_clipping_increased')
    row.update({'before_stats':a,'after_stats':b,'mean_pixel_delta':delta,'flags':flags})
    print('V11_STABLE_ACTUAL_TRIPLET',i,row['start'],flush=True)
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',21)
for a in range(0,len(records),4):
    part=records[a:a+4];sheet=Image.new('RGB',(1920,len(part)*305),(242,239,230));draw=ImageDraw.Draw(sheet)
    for i,row in enumerate(part):
        for j,key in enumerate(['before_stable','after_stable']):
            im=Image.open(row[key]).convert('RGB');im.thumbnail((480,270));x=i%1*960+j*960;y=i*305;sheet.paste(im,(x,y));draw.text((x+490,y+95),f"{row['start']/25:.2f}s\n{'当前v10' if j==0 else 'v11 高光' if row['kind']=='highlights' else 'v11 层次'}",font=font,fill=(22,38,30))
    sheet.save(PRE/f'逐镜通透与高光对照_{a//4+1}.jpg',quality=95)
result={'records':records,'count':len(records),'highlights_count':sum(x['kind']=='highlights' for x in records),'density_count':sum(x['kind']=='density' for x in records),'actual_first_middle_last_frames':actual,'actual_after_stills':len(actual),'stable_double_captures':True,'flags':[{'start':x['start'],'flags':x['flags']} for x in records if x['flags']],'all_edits_audio_fusion_and_layout_unchanged':snap(t)==before['snapshot'],'whole_film_exported':False}
(OUT/'native_color_qa_v11.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));assert pm.SaveProject();print('V11_NATIVE_COLOR_QA_READY',result['count'],result['flags'],flush=True)
