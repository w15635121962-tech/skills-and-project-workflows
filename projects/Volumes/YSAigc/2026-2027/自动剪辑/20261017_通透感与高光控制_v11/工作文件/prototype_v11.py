import sys,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,'/Volumes/YSAigc/2026-2027/自动剪辑/20261017_双图包装与全片调色_v9/工作文件')
from common_v9 import connect,snap,capture,tc
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'调色预览';NAME='学校_通透感与高光控制_v11_20261017'
r,pm,p,mp,t=connect();assert t.GetName()==NAME and r.OpenPage('color')
before=json.loads((OUT/'live_before_v11.json').read_text());assert snap(t)==before['snapshot']
frames={(x['track'],x['start']):x for x in json.loads((OUT/'current_frames_v11.json').read_text())}
targets=[
 (1,117,[.975]*3,[-.001]*3,[1.025]*3,1.015,'收迎校老师白外套与面部高亮，降低发白并立住深衣'),
 (1,4365,[.985]*3,[-.002]*3,[1.025]*3,1.01,'窗边朗读收亮部密度，保留孩子肤色亮度'),
 (1,396,[1.015]*3,[-.018]*3,[1.005]*3,1.015,'开篇建筑分离暗部与反光，保留真实太阳芯'),
 (1,11042,[1.02]*3,[-.018]*3,[.97]*3,1.01,'采访增加中低调分离，维持脸部和亮部，避免全局变暗'),
]
records=[];font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',23)
for track,st,slope,offset,power,sat,reason in targets:
    row=frames[track,st];it=next(x for x in t.GetItemListInTrack('video',track) if x.GetStart()==st);prior=it.GetCurrentVersion();g=it.GetNodeGraph();assert g.GetNumNodes()==1
    lut=g.GetLUT(1);name='v11_通透与高光控制';assert name not in it.GetVersionNameList(0)
    assert it.AddVersion(name,0) and it.LoadVersionByName(name,0)
    cdl={'NodeIndex':'1','Slope':' '.join(map(str,slope)),'Offset':' '.join(map(str,offset)),'Power':' '.join(map(str,power)),'Saturation':str(sat)}
    assert it.SetCDL(cdl) and it.GetNodeGraph().GetLUT(1)==lut
    after=PRE/'样板'/f'{track}_{st:05d}_after.jpg';capture(p,t,row['frame'],after,.15)
    sheet=Image.new('RGB',(1920,590),(242,239,230));draw=ImageDraw.Draw(sheet)
    for i,path in enumerate([row['path'],str(after)]):
        im=Image.open(path).convert('RGB');im.thumbnail((960,540));sheet.paste(im,(i*960,0));draw.text((i*960+20,547),'当前v10' if i==0 else '通透与高光控制样板',font=font,fill=(24,39,30))
    sheet.save(PRE/f'样板前后_{track}_{st}.jpg',quality=95)
    records.append(dict(row,prior_version=prior,lut=lut,cdl=cdl,active_version=it.GetCurrentVersion(),after=str(after),reason=reason))
    print('V11_PROTOTYPE',track,st,flush=True)
(OUT/'prototype_v11.json').write_text(json.dumps({'records':records},ensure_ascii=False,indent=2));assert pm.SaveProject();print('V11_PROTOTYPES_READY',flush=True)
