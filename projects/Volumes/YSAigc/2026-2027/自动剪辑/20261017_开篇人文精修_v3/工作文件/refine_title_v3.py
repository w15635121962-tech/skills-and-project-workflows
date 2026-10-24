import sys,json,time
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'开篇预览';DEST=PRE/'最终标题';DEST.mkdir(exist_ok=True)
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='学校';mp=p.GetMediaPool();t=p.GetCurrentTimeline();assert t.GetName()=='学校_开篇人文精修_v3_20261017';title=t.GetItemListInTrack('video',2)[0];c=title.GetFusionCompByIndex(1);mo=c.FindToolByID('MediaOut')
for name,xy,alpha in [('Template',(.325,.275),1),('Text1',(.325,.195),1),('Text2',(.326,.273),.65),('Text3',(.326,.193),.65)]:
 txt=c.FindTool(name);assert txt;txt.SetInput('Center',{1:xy[0],2:xy[1]});txt.Alpha1=c.BezierSpline();txt.Alpha1[0]=alpha;txt.Alpha1[124]=alpha
background=c.AddTool('Background');fade=c.AddTool('Merge');assert background and fade;background.SetInput('UseFrameFormatSettings',1);background.SetInput('TopLeftAlpha',0)
assert fade.ConnectInput('Background',background) and fade.ConnectInput('Foreground',c.FindTool('Merge3'));fade.Blend=c.BezierSpline();fade.Blend[0]=0;fade.Blend[12]=1;fade.Blend[112]=1;fade.Blend[124]=0;assert mo.ConnectInput('Input',fade)
assert title.ExportFusionComp(str(OUT/'v3-independent-title-final.comp'),1);assert pm.SaveProject()
def tc(frame):
 sec,fr=divmod(frame,25);mins,ss=divmod(sec,60);hh,mm=divmod(mins,60);return f'{hh:02d}:{mm:02d}:{ss:02d}:{fr:02d}'
def capture(frame,name):
 path=DEST/(name+'.png');assert not path.exists();assert t.SetCurrentTimecode(tc(frame));time.sleep(.5);assert p.ExportCurrentFrameAsStill(str(path));return path,np.array(Image.open(path).convert('RGB'))
checks=[]
for frame in [383,389,399,430,495,501,507]:
 assert t.SetTrackEnable('video',2,True);path,arr=capture(frame,f'{frame}_含片名');assert t.SetTrackEnable('video',2,False);base,barr=capture(frame,f'{frame}_底片');assert t.SetTrackEnable('video',2,True)
 delta=np.abs(arr.astype(np.int16)-barr.astype(np.int16));checks.append({'frame':frame,'path':str(path),'base':str(base),'difference_sum':int(delta.sum()),'difference_max':int(delta.max())})
print('FADE_QA',checks,flush=True)
assert checks[0]['difference_max']==0 and checks[-1]['difference_max']==0,'Title must be invisible at both fade endpoints'
assert checks[3]['difference_sum']>100000,'Title must be visible during settled display'
assert 0<checks[1]['difference_sum']<checks[3]['difference_sum'],'Entrance should be a partial fade'
assert 0<checks[-2]['difference_sum']<checks[3]['difference_sum'],'Exit should be a partial fade'
(OUT/'title_fade_qa_v3.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
frame=424;assert t.SetCurrentTimecode(tc(frame));time.sleep(.5);dest=DEST/'片名实际画面.jpg';assert not dest.exists();assert p.ExportCurrentFrameAsStill(str(dest))
plan=json.loads((OUT/'opening_plan_v3.json').read_text());frames=json.loads((OUT/'native_verification_v3.json').read_text())['frames'];font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',16);sheet=Image.new('RGB',(1440,1270),(245,244,240));d=ImageDraw.Draw(sheet)
for i,(s,rec) in enumerate(zip(plan['shots'],frames)):
 im=Image.open(dest if s['index']==5 else rec['path']).convert('RGB');im.thumbnail((360,203));x=i%4*360;y=i//4*254;sheet.paste(im,(x,y));d.text((x+5,y+205),f"{s['record_frame']/25:.2f}–{(s['record_frame']+s['length_frames'])/25:.2f}s",font=font,fill=(35,40,38));d.text((x+5,y+228),s['intent'][:22],font=font,fill=(35,40,38))
sheet.save(PRE/'开篇人文精修总览.jpg',quality=94);assert t.SetCurrentTimecode('00:00:00:20');assert pm.SaveProject();print('FINAL_TITLE_QA_COMPLETE',flush=True)
