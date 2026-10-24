from common_v13 import *
from package_background_v13 import build
from PIL import ImageDraw,ImageFont
r,pm,p,mp,t=connect();assert t.GetName()==TIMELINE;assert r.OpenPage('edit');records=[]
for st in [1871,3749,7509]:
 g=next(x for x in GROUPS if x['start']==st);it=next(x for x in t.GetItemListInTrack('video',1) if x.GetStart()==st);c=it.GetFusionCompByIndex(1);c.Lock()
 try:row=build(c,g,t)
 finally:c.Unlock()
 assert it.ExportFusionComp(str(OUT/f'动态底板样板_{st}.comp'),1)
 path=PRE/f'动态底板样板_{st}.jpg';cap(p,t,st+g['length']//2,path,.8);row['preview']=str(path);records.append(row);print('V13_PROTOTYPE',st,row['new_native_nodes'],flush=True)
(OUT/'package_prototypes_v13.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));assert pm.SaveProject()
