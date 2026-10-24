import json,time
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from common_v12 import *
r,pm,p,mp,t=connect();assert t.GetName()==TIMELINE;assert r.OpenPage('edit');initial=json.loads((OUT/'live_before_v12.json').read_text());assert snap(t)==initial['snapshot'];specs=json.loads((OUT/'all_grade_specs_v12.json').read_text())['records'];samples={ (x['track'],x['start']):x for x in json.loads((OUT/'native_samples_qa_v12.json').read_text())['records']}
parent=next(p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()==BASELINE);assert p.SetCurrentTimeline(parent) and snap(parent)==initial['snapshot'];before_graphs=[]
for tr in range(1,parent.GetTrackCount('video')+1):
 for it in parent.GetItemListInTrack('video',tr):
  g=it.GetNodeGraph();before_graphs.append({'track':tr,'start':it.GetStart(),'version':it.GetCurrentVersion(),'nodes':g.GetNumNodes(),'luts':[g.GetLUT(j) for j in range(1,g.GetNumNodes()+1)],'tools':[g.GetToolsInNode(j) for j in range(1,g.GetNumNodes()+1)]})
assert before_graphs==initial['graphs'],'Recovered baseline grades differ from task start'
records=[]
for i,s in enumerate(specs,1):
 it=next(x for x in parent.GetItemListInTrack('video',s['track']) if x.GetStart()==s['start']);end=it.GetEnd()-1
 if s['start']==11042:end=11152
 frame_info=[]
 for label,f in [('入',it.GetStart()),('中',s['frame']),('出',end)]:
  path=PRE/'二级精调前'/f"{s['track']}_{s['start']:05d}_{label}.jpg";pic=stable_cap(p,parent,f,path);frame_info.append({'label':label,'frame':f,'before':str(path),'before_stats':stats(pic)})
 g=it.GetNodeGraph();records.append(dict(s,frames=frame_info,prior_version=it.GetCurrentVersion(),prior_nodes=g.GetNumNodes(),lut=g.GetLUT(1) or ''))
 if i%5==0:print('NATIVE_BEFORE_TRIPLETS',i,flush=True)
assert p.SetCurrentTimeline(t);assert pm.SaveProject();(OUT/'native_before_triplets_v12.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
for i,s in enumerate(records,1):
 it=next(x for x in t.GetItemListInTrack('video',s['track']) if x.GetStart()==s['start']);vname='v12_曲线与精细二级'
 if (s['track'],s['start']) not in samples:
  assert it.AddVersion(vname,0) and it.LoadVersionByName(vname,0);assert it.GetNodeGraph().ApplyGradeFromDRX(s['path'],0)
 else:assert it.LoadVersionByName(vname,0)
 g=it.GetNodeGraph();assert g.GetNumNodes()==len(s['nodes']) and (g.GetLUT(1) or '')==s['lut'];s['active_version']=it.GetCurrentVersion();s['actual_node_labels']=[g.GetNodeLabel(j) for j in range(1,g.GetNumNodes()+1)];s['actual_tools']=[g.GetToolsInNode(j) for j in range(1,g.GetNumNodes()+1)]
 # Prove original grade survives by disabling every newly appended correction.
 for n in range(2,g.GetNumNodes()+1):assert g.SetNodeEnabled(n,False)
 back=stable_cap(p,t,s['frame'],PRE/'逐镜原调色保留'/f"{s['track']}_{s['start']:05d}.jpg");ref=Image.open(s['frames'][1]['before']).convert('RGB');s['base_preserved_delta']=float(abs(np.array(back,float)-np.array(ref,float)).mean());assert s['base_preserved_delta']<.2,(s['start'],'Old grade changed',s['base_preserved_delta'])
 for n in range(2,g.GetNumNodes()+1):assert g.SetNodeEnabled(n,True)
 flags=[]
 for frame in s['frames']:
  path=PRE/'二级精调后'/f"{s['track']}_{s['start']:05d}_{frame['label']}.jpg";pic=stable_cap(p,t,frame['frame'],path);before=Image.open(frame['before']).convert('RGB');delta=float(abs(np.array(pic,float)-np.array(before,float)).mean());st=stats(pic);frame.update(after=str(path),after_stats=st,mean_pixel_delta=delta)
  if delta>15:flags.append(frame['label']+':large_image_change')
  if st['white98']-frame['before_stats']['white98']>.005:flags.append(frame['label']+':increased_white_clipping')
  if st['black008']-frame['before_stats']['black008']>.005:flags.append(frame['label']+':increased_black_clipping')
 # Isolate the native secondary correction and prove a selected, non-global contribution.
 assert g.SetNodeEnabled(2,False);keypic=stable_cap(p,t,s['frame'],PRE/'逐镜二级单独效果'/f"{s['track']}_{s['start']:05d}.jpg");d=abs(np.array(keypic,float)-np.array(ref,float));s['secondary_mean_delta']=float(d.mean());s['secondary_affected_above_1']=float((d.max(2)>1).mean());assert g.SetNodeEnabled(2,True)
 if s['secondary_mean_delta']<.005:flags.append('secondary_no_op')
 s['flags']=flags;assert pm.SaveProject();print('NATIVE_CURVES_SECONDARY_VERIFIED',i,s['track'],s['start'],'base',s['base_preserved_delta'],'key',s['secondary_mean_delta'],'flags',flags,flush=True)
 (OUT/'native_color_qa_v12.json').write_text(json.dumps({'records':records[:i],'count':i,'flags':[{'track':x['track'],'start':x['start'],'flags':x['flags']} for x in records[:i] if x['flags']]},ensure_ascii=False,indent=2))
assert snap(t)==initial['snapshot'];assert p.SetCurrentTimeline(parent);assert snap(parent)==initial['snapshot'];after_graphs=[]
for tr in range(1,parent.GetTrackCount('video')+1):
 for it in parent.GetItemListInTrack('video',tr):
  g=it.GetNodeGraph();after_graphs.append({'track':tr,'start':it.GetStart(),'version':it.GetCurrentVersion(),'nodes':g.GetNumNodes(),'luts':[g.GetLUT(j) for j in range(1,g.GetNumNodes()+1)],'tools':[g.GetToolsInNode(j) for j in range(1,g.GetNumNodes()+1)]})
assert before_graphs==after_graphs;assert p.SetCurrentTimeline(t) and pm.SaveProject();font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',20)
for first in range(0,len(records),4):
 part=records[first:first+4];im=Image.new('RGB',(1440,len(part)*440),(242,239,230));draw=ImageDraw.Draw(im)
 for i,s in enumerate(part):
  for j,field in enumerate(['before','after']):
   pic=Image.open(s['frames'][1][field]).convert('RGB');pic.thumbnail((720,405));im.paste(pic,(j*720,i*440));draw.text((j*720+10,i*440+408),f"V{s['track']} {s['start']/25:.2f}s · {'本轮前' if j==0 else 'v12 曲线与二级'}",font=font,fill=(22,38,30))
 im.save(PRE/f'全片曲线二级对照_{first//4+1}.jpg',quality=96)
summary={'records':records,'count':len(records),'actual_before_frames':len(records)*3,'actual_after_frames':len(records)*3,'all_prior_grade_frames_preserved':all(x['base_preserved_delta']<.2 for x in records),'original_timeline_grades_unchanged':before_graphs==after_graphs,'picture_edit_fusion_audio_unchanged':snap(t)==initial['snapshot'],'flags':[{'track':x['track'],'start':x['start'],'flags':x['flags']} for x in records if x['flags']]};(OUT/'native_color_qa_v12.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print('COMPLETE_NATIVE_QA',summary['count'],summary['flags'],flush=True)
