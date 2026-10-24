import sys,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,'/Volumes/YSAigc/2026-2027/自动剪辑/20261017_双图包装与全片调色_v9/工作文件')
from common_v9 import connect,capture
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'调色预览'
r,pm,p,mp,t=connect();assert t.GetName()=='学校_通透感与高光控制_v11_20261017'
data=json.loads((OUT/'prototype_v11.json').read_text());records={(x['track'],x['start']):x for x in data['records']};frames={(x['track'],x['start']):x for x in json.loads((OUT/'current_frames_v11.json').read_text())};font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',23)
for st,slope,offset,power,sat,reason in [(117,.95,-.004,1.04,1.015,'迎校老师较强一档收亮和增加深衣密度'),(2453,.96,-.006,.93,1,'Rec709建筑资料压最高白，保持中间调；不声称重建无纹理天空'),(1340,.95,-.012,.92,1,'守门员前景中间调保持，温和收上部亮度，保护人物')]:
    it=next(x for x in t.GetItemListInTrack('video',1) if x.GetStart()==st);row=records.get((1,st))
    if row is None:
        row=dict(frames[1,st],prior_version=it.GetCurrentVersion(),lut=it.GetNodeGraph().GetLUT(1));assert it.AddVersion('v11_通透与高光控制',0) and it.LoadVersionByName('v11_通透与高光控制',0)
    else:row['initial_candidate_cdl']=row['cdl']
    cdl={'NodeIndex':'1','Slope':' '.join([str(slope)]*3),'Offset':' '.join([str(offset)]*3),'Power':' '.join([str(power)]*3),'Saturation':str(sat)}
    assert it.SetCDL(cdl) and it.GetNodeGraph().GetLUT(1)==row['lut']
    after=PRE/'样板'/f'1_{st:05d}_after_b.jpg';capture(p,t,row['frame'],after,.15)
    sheet=Image.new('RGB',(1920,590),(242,239,230));d=ImageDraw.Draw(sheet)
    for i,path in enumerate([row['path'],str(after)]):
        im=Image.open(path).convert('RGB');im.thumbnail((960,540));sheet.paste(im,(i*960,0));d.text((i*960+20,547),'调整前 v10' if i==0 else '高光与密度调整样板B',font=font,fill=(23,39,30))
    sheet.save(PRE/f'样板B前后_{st}.jpg',quality=95)
    records[1,st]=dict(row,cdl=cdl,after=str(after),reason=reason,active_version=it.GetCurrentVersion())
(OUT/'prototype_v11.json').write_text(json.dumps({'records':list(records.values())},ensure_ascii=False,indent=2));assert pm.SaveProject();print('V11_PROTOTYPE_B_READY',flush=True)
