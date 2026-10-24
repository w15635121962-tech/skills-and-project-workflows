import json,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from common_v12 import *
r,pm,p,mp,t=connect();assert t.GetName()==TIMELINE;qa=json.loads((OUT/'native_color_qa_v12.json').read_text());assert qa['count']==21
archive=OUT/'21镜候选验证完整记录.json';assert not archive.exists();shutil.copy2(OUT/'native_color_qa_v12.json',archive)
skip=next(x for x in qa['records'] if x['track']==1 and x['start']==1135);it=next(x for x in t.GetItemListInTrack('video',1) if x.GetStart()==1135);v=skip['prior_version'];assert it.LoadVersionByName(v['versionName'],v['versionType']);checks=[]
for f in skip['frames']:
 im=stable_cap(p,t,f['frame'],PRE/'低收益镜头原样保留'/f"1135_{f['label']}.jpg");old=Image.open(f['before']).convert('RGB');delta=float(abs(np.array(im,float)-np.array(old,float)).mean());assert delta<.1;checks.append({'frame':f['frame'],'delta':delta})
assert it.DeleteVersionByName('v12_曲线与精细二级',0);skip_report={'track':1,'start':1135,'reason':'图书馆近景环境色本来低饱和，二级贡献过低，无需调整，完整保留本轮开始时原调色','original_version_restored':it.GetCurrentVersion(),'actual_first_mid_last_reversion_checks':checks}
qa['records']=[x for x in qa['records'] if not (x['track']==1 and x['start']==1135)];qa['count']=len(qa['records']);qa['actual_before_frames']=qa['count']*3;qa['actual_after_frames']=qa['count']*3;qa['flags']=[];qa['skipped']=skip_report
(OUT/'native_color_qa_v12.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2));plan=json.loads((OUT/'all_grade_specs_v12.json').read_text());plan['records']=[x for x in plan['records'] if not(x['track']==1 and x['start']==1135)];plan['count']=len(plan['records']);plan['skipped']=skip_report;(OUT/'all_grade_specs_v12.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
for f in sorted(PRE.glob('全片曲线二级对照_*.jpg')):
 d=OUT/'21镜候选对照';d.mkdir(exist_ok=True);shutil.move(str(f),str(d/f.name))
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',20)
for first in range(0,len(qa['records']),4):
 part=qa['records'][first:first+4];im=Image.new('RGB',(1440,len(part)*440),(242,239,230));draw=ImageDraw.Draw(im)
 for i,s in enumerate(part):
  for j,field in enumerate(['before','after']):
   pic=Image.open(s['frames'][1][field]).convert('RGB');pic.thumbnail((720,405));im.paste(pic,(j*720,i*440));draw.text((j*720+10,i*440+408),f"V{s['track']} {s['start']/25:.2f}s · {'本轮前' if j==0 else 'v12 曲线与二级'}",font=font,fill=(22,38,30))
 im.save(PRE/f'全片曲线二级对照_{first//4+1}.jpg',quality=96)
# Keep the working project tidy by removing only our obsolete recovery-check duplicate.
obsolete=next((p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()=='学校_恢复检查_旧导出备份_v12'),None)
if obsolete:assert mp.DeleteTimelines([obsolete])
assert snap(t)==json.loads((OUT/'live_before_v12.json').read_text())['snapshot'];assert pm.SaveProject();print('FINAL_EFFECTIVE_SECONDARY_SHOTS',qa['count'],'SKIP_REVERTED',checks,flush=True)
