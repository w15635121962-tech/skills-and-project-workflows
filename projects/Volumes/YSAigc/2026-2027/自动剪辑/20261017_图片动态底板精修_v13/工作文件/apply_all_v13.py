from common_v13 import *
from package_background_v13 import build
r,pm,p,mp,t=connect();assert t.GetName()==TIMELINE
before=json.loads((OUT/'live_before_v13.json').read_text())
parent=next(p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()==PARENT)
assert p.SetCurrentTimeline(parent);assert snap(parent)==before['snapshot'];assert graphs(parent)==before['graphs'];assert r.OpenPage('edit')
parent_checks=[]
for st in [1871,3749,7509]:
 g=next(x for x in GROUPS if x['start']==st);it=next(x for x in parent.GetItemListInTrack('video',1) if x.GetStart()==st);c=it.GetFusionCompByIndex(1)
 assert not any(x.GetAttrs()['TOOLS_Name'].startswith('V13_') for x in c.GetToolList(False).values())
 image=cap(p,parent,st+g['length']//2,PRE/'原版保留检查'/f'{st}.jpg',.8)
 baseline=Image.open(PRE/'调整前'/f'{st}.jpg').convert('RGB');diff=float(abs(np.array(image,float)-np.array(baseline,float)).mean());assert diff<.05,(st,diff)
 parent_checks.append({'start':st,'unchanged_mean_rgb_difference':diff})
assert p.SetCurrentTimeline(t);records=[]
for i,g in enumerate(GROUPS,1):
 it=next(x for x in t.GetItemListInTrack('video',1) if x.GetStart()==g['start']);c=it.GetFusionCompByIndex(1);c.Lock()
 try:row=build(c,g,t)
 finally:c.Unlock()
 assert it.ExportFusionComp(str(OUT/f"动态底板_{g['start']}.comp"),1)
 path=PRE/'精修后'/f"{g['start']}.jpg";im=cap(p,t,g['start']+g['length']//2,path,.65)
 baseline_path=PRE/'原版保留检查'/'9960_mid.jpg' if g['start']==9960 else PRE/'调整前'/f"{g['start']}.jpg"
 old=np.array(Image.open(baseline_path).convert('RGB'),float);new=np.array(im,float);photo_checks=[]
 for ph in row['photo_frames']:
  w,h=ph['dimensions'];size=ph['photo_size_first_mid_last'][1];cx,cy=ph['center'];pw,phh=w*size,h*size
  # The central half of the original photo must remain pixel-identical; new graphics only sit behind it.
  x0,x1=int(cx*1920-pw*.25),int(cx*1920+pw*.25);y0,y1=int((1-cy)*1080-phh*.25),int((1-cy)*1080+phh*.25)
  delta=float(abs(old[y0:y1,x0:x1]-new[y0:y1,x0:x1]).mean());assert delta<.1,(g['start'],ph['side'],delta)
  photo_checks.append({'side':ph['side'],'interior_mean_rgb_difference':delta})
 row['photo_preservation']=photo_checks;row['photo_pixel_reference']=str(baseline_path);row['preview']=str(path);records.append(row)
 print('V13_PACKAGE',i,g['start'],g['title'],flush=True)
assert snap(t)==before['snapshot'];assert graphs(t)==before['graphs']
sources=[x['path'] for track in before['snapshot']['video'] if track['track'] in [3,4] for x in track['items']];assert len(sources)==44 and len(set(sources))==44
report={'timeline':t.GetName(),'groups':records,'photos':44,'unique_photos':44,'prior_timeline_checks':parent_checks,'all_clip_timing_and_properties_preserved':True,'all_color_nodes_and_versions_preserved':True,'source_photos_pixel_preserved':True}
(OUT/'package_build_and_qa_v13.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(OUT/'final_native_snapshot_v13.json').write_text(json.dumps(snap(t),ensure_ascii=False,indent=2));assert pm.SaveProject();print('V13_ALL_PACKAGES_READY',len(records),flush=True)
