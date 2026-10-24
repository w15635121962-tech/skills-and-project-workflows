import sys,json,time
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
sys.path.insert(0,'/Volumes/YSAigc/2026-2027/自动剪辑/20261017_双图包装与全片调色_v9/工作文件')
from common_v9 import connect,snap,capture,tc
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'调色预览';NAME='学校_人文自然调色_v10_20261017'
r,pm,p,mp,t=connect();assert t.GetName()==NAME
baseline=json.loads((OUT/'live_before_v10.json').read_text());assert snap(t)==baseline['snapshot']
fresh={x['start']:x for x in json.loads((OUT/'fresh_candidates_v10.json').read_text())}
v9=json.loads((ROOT.parent/'20261017_双图包装与全片调色_v9/工作文件/native_color_applied_v9.json').read_text());oldgrades={(x['track'],x['start']):x for x in v9['records']}
recipes={
2263:([.996,.995,1.003],[0,0,0],[.955,.96,.948],.99,'课堂女生面部与白校服轻提中间调，保留窗边光比'),
2549:([.996,.995,1.003],[0,0,0],[.973,.978,.965],.99,'同场课堂与开篇已校镜头匹配，轻减闷黄'),
4289:([1,1,1],[0,0,0],[.97,.97,.97],1,'化学实验全景等RGB提中间调，保持原中性偏冷环境'),
4439:([.996,.995,1.003],[0,0,0],[.962,.967,.954],.99,'后排学生面部提亮，白校服轻微减黄'),
4492:([.998,.996,1.004],[0,0,0],[.97,.975,.962],.99,'书写手部与纸面亮度匹配，保留木桌暖色'),
5382:([.994,.994,1.004],[0,0,0],[.962,.967,.954],.99,'展示区学生面部稍提亮，白校服避免闷黄'),
}
targets=[]
for st in [2263,2549,4289,4439,4492,5382,6420,9243]:
    assert (1,st) not in oldgrades
    if st in recipes:
        slope,offset,power,sat,reason=recipes[st]
        cdl={'NodeIndex':'1','Slope':' '.join(map(str,slope)),'Offset':' '.join(map(str,offset)),'Power':' '.join(map(str,power)),'Saturation':str(sat)}
    else:
        hero=60 if st==6420 else 836;cdl=oldgrades[1,hero]['cdl'];reason=f'与同源已校镜头{hero}帧保持一致；核对纸张、肤色和白校服'
    targets.append(dict(fresh[st],cdl=cdl,reason=reason))
records=[];assert pm.SaveProject() and r.OpenPage('color')
for row in targets:
    it=next(x for x in t.GetItemListInTrack('video',1) if x.GetStart()==row['start']);prior=it.GetCurrentVersion();graph=it.GetNodeGraph();assert graph.GetNumNodes()==1
    lut=graph.GetLUT(1);name='v10_人文镜间匹配';assert name not in it.GetVersionNameList(0)
    assert it.AddVersion(name,0) and it.LoadVersionByName(name,0) and it.SetCDL(row['cdl']);assert it.GetNodeGraph().GetLUT(1)==lut
    images={}
    for label,f in [('入',it.GetStart()),('中',row['frame']),('出',it.GetEnd()-1)]:
        path=PRE/'调色后'/f"{row['start']:05d}_{label}.jpg";images[label]=str(path);capture(p,t,f,path,.15)
    before=Image.open(row['path']).convert('RGB');after=Image.open(images['中']).convert('RGB')
    a=np.asarray(before,dtype=float)/255;b=np.asarray(after,dtype=float)/255
    def values(x):
        y=.2126*x[:,:,0]+.7152*x[:,:,1]+.0722*x[:,:,2]
        return {'p01_p50_p99':np.quantile(y,[.01,.5,.99]).tolist(),'white':float(np.mean(np.all(x>.985,axis=2))),'black':float(np.mean(np.all(x<.008,axis=2)))}
    av=values(a);bv=values(b);delta=float(np.abs(a-b).mean()*255);flags=[]
    if bv['white']-av['white']>.01:flags.append('新增纯白过多')
    if bv['black']-av['black']>.015:flags.append('新增死黑过多')
    if delta<.03:flags.append('疑似未生效')
    records.append(dict(row,before=row['path'],after=images['中'],after_triplet=images,prior_version=prior,active_version=it.GetCurrentVersion(),lut=lut,before_stats=av,after_stats=bv,mean_pixel_delta=delta,flags=flags))
    print('V10_NATIVE_COLOR_CORRECTED',row['start'],flush=True)
assert snap(t)==baseline['snapshot'] and pm.SaveProject()
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',21)
for a in range(0,len(records),4):
    part=records[a:a+4];sheet=Image.new('RGB',(1920,4*305),(242,239,230));d=ImageDraw.Draw(sheet)
    for j,x in enumerate(part):
        for k,key in enumerate(['before','after']):
            im=Image.open(x[key]).convert('RGB');im.thumbnail((960,270));px=480 if k==0 else 1440
            # Full frame is fit at 480x270, with text beside it for a compact row.
            sheet.paste(im,(k*960,j*305));d.text((k*960+490,j*305+110),f"{x['start']/25:.2f}s\n{'调色前 v9' if k==0 else '调色后 v10'}",font=font,fill=(25,42,33))
    sheet.save(PRE/f'镜间匹配前后_{a//4+1}.jpg',quality=95)
(OUT/'native_color_v10.json').write_text(json.dumps({'timeline':NAME,'records':records,'additional_footage_grades':8,'inherited_footage_grades':49,'inherited_photo_grades':8,'snapshot_unchanged':True,'all_audio_and_edits_preserved':True,'flags':[{'start':x['start'],'flags':x['flags']} for x in records if x['flags']]},ensure_ascii=False,indent=2))
assert t.SetCurrentTimecode(tc(2263+42)) and pm.SaveProject();print('V10_COLOR_MATCHING_COMPLETE',flush=True)
