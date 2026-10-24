from common_v9 import *
from PIL import Image,ImageDraw,ImageFont
import numpy as np
r,pm,p,mp,t=connect();assert t.GetName()==NAME and r.OpenPage('edit')
samples=[
 {'track':1,'start':1067,'frame':1101,'slope':[.994,.994,1.003],'offset':[0,0,0],'power':[.955,.958,.947],'sat':.99,'reason':'开篇人像提中间调并减闷黄'},
 {'track':1,'start':5035,'frame':5065,'slope':[.988,.988,.996],'offset':[.002,.002,.002],'power':[.94,.945,.934],'sat':.99,'reason':'辅导人物逆光，保护窗帘高光'},
 {'track':1,'start':6575,'frame':6600,'slope':[1,.985,1.012],'offset':[0,0,0],'power':[.992,1.002,.99],'sat':.99,'reason':'白衣白台面减黄绿'},
 {'track':1,'start':11042,'frame':11070,'slope':[.993,.993,1.001],'offset':[.001,.001,.001],'power':[.968,.97,.96],'sat':.99,'reason':'校长主画面保持自然亮度与肤色'},
 {'track':3,'start':7509,'frame':7536,'slope':[1,1,1],'offset':[0,0,0],'power':[.972,.972,.972],'sat':.98,'reason':'校长培训照片单独温和补亮，底版不变'},
]
records=[];font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',23)
for s in samples:
    it=next(x for x in t.GetItemListInTrack('video',s['track']) if x.GetStart()==s['start']);g=it.GetNodeGraph();assert g.GetNumNodes()==1
    prior=it.GetCurrentVersion();luts=[g.GetLUT(1)]
    before=PRE/'调色样板'/f"{s['track']}_{s['start']}_before.jpg";capture(p,t,s['frame'],before)
    name='v9_自然人文校色';assert name not in it.GetVersionNameList(0)
    assert it.AddVersion(name,0) and it.LoadVersionByName(name,0)
    cdl={'NodeIndex':'1','Slope':' '.join(map(str,s['slope'])),'Offset':' '.join(map(str,s['offset'])),'Power':' '.join(map(str,s['power'])),'Saturation':str(s['sat'])}
    assert it.SetCDL(cdl) and it.GetNodeGraph().GetLUT(1)==luts[0]
    after=PRE/'调色样板'/f"{s['track']}_{s['start']}_after.jpg";capture(p,t,s['frame'],after)
    sheet=Image.new('RGB',(1920,1125),(242,239,230));d=ImageDraw.Draw(sheet)
    for j,path in enumerate([before,after]):
        im=Image.open(path).convert('RGB');im.thumbnail((960,1080));sheet.paste(im,(j*960,45));d.text((j*960+20,8),'调色前' if j==0 else '人文自然校色',font=font,fill=(28,39,32))
    sheet.save(PRE/f"调色样板_{s['track']}_{s['start']}.jpg",quality=95)
    records.append(dict(s,prior_version=prior,cdl=cdl,preserved_luts=luts,before=str(before),after=str(after),active_version=it.GetCurrentVersion()))
    print('COLOR_NATIVE_PROTOTYPE',s['track'],s['start'],flush=True)
assert pm.SaveProject()
# The original v8 must still show its exact saved color version and pixels.
base=next(p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()=='学校_人物动态与缓推精修_v8_20261017')
try:
    assert p.SetCurrentTimeline(base)
    bitem=next(x for x in base.GetItemListInTrack('video',1) if x.GetStart()==5035)
    assert bitem.GetCurrentVersion()==records[1]['prior_version']
    old=PRE/'调色样板'/'v8_5035_preserved.jpg';capture(p,base,5065,old)
    aa=np.asarray(Image.open(old).convert('RGB'),dtype=float);bb=np.asarray(Image.open(records[1]['before']).convert('RGB'),dtype=float)
    delta=float(np.abs(aa-bb).mean());assert delta<.1,delta
finally:assert p.SetCurrentTimeline(t)
save('native_color_prototype_v9.json',{'samples':records,'v8_pixel_delta':delta,'v8_grade_preserved':True});assert pm.SaveProject();print('COLOR_PROTOTYPE_READY',flush=True)
