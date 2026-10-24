import sys,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'工作文件';OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,'/Volumes/YSAigc/2026-2027/自动剪辑/20261017_图片动态底板精修_v13/工作文件')
from common_v13 import snap,graphs,tc,get_resolve
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p
t=p.GetCurrentTimeline();assert t
snapshot=snap(t);fusion=[]
for tr in range(1,t.GetTrackCount('video')+1):
 for it in t.GetItemListInTrack('video',tr):
  tools=[]
  for j in range(1,it.GetFusionCompCount()+1):
   c=it.GetFusionCompByIndex(j);a=int(c.GetAttrs()['COMPN_RenderStart']);z=int(c.GetAttrs()['COMPN_RenderEnd'])
   for x in c.GetToolList(False).values():
    attr=x.GetAttrs();row={'comp':j,'name':attr['TOOLS_Name'],'type':attr['TOOLS_RegID']}
    if attr['TOOLS_RegID']=='Transform':row.update({'range':[a,z],'size':[x.GetInput('Size',a),x.GetInput('Size',(a+z)//2),x.GetInput('Size',z)],'center':x.GetInput('Center'),'angle':x.GetInput('Angle')})
    tools.append(row)
  fusion.append({'track':tr,'start':it.GetStart(),'duration':it.GetDuration(),'name':it.GetName(),'fusion_comp_count':it.GetFusionCompCount(),'tools':tools})
data={'project':p.GetName(),'timeline':t.GetName(),'page':r.GetCurrentPage(),'timecode':t.GetCurrentTimecode(),'snapshot':snapshot,'graphs':graphs(t),'fusion':fusion,'timeline_fps':t.GetSetting('timelineFrameRate'),'timeline_resolution':[t.GetSetting('timelineResolutionWidth'),t.GetSetting('timelineResolutionHeight')]}
(OUT/'live_before_v14.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
print(json.dumps({'project':data['project'],'timeline':data['timeline'],'page':data['page'],'timecode':data['timecode'],'video':[(x['track'],len(x['items'])) for x in snapshot['video']],'audio':snapshot['audio'],'existing_animated_transforms':sum(any(x['type']=='Transform' and len(set(x.get('size',[])))>1 for x in row['tools']) for row in fusion)},ensure_ascii=False,indent=2))
