from common_v13 import *
r,pm,p,mp,t=connect();assert t.GetName()==TIMELINE;assert r.OpenPage('edit')
records=[];photo_checks=[];built=json.loads((OUT/'package_native_build_v13.json').read_text());before=json.loads((OUT/'live_before_v13.json').read_text())
# Real rendered entrance and exit frames for every photo package, including native photo zoom endpoints.
for i,g in enumerate(GROUPS,1):
 for label,f in [('入',g['start']),('中',g['start']+g['length']//2),('出',g['start']+g['length']-1)]:
  path=PRE/'精修后'/f"{g['start']}.jpg" if label=='中' else PRE/'进出画面核验'/f"{g['start']}_{label}.jpg"
  im=cap(p,t,f,path,.35);records.append({'start':g['start'],'label':label,'frame':f,'path':str(path)})
  if label=='中':
   row=next(x for x in built if x['start']==g['start']);baseline_path=PRE/'原版保留检查'/'9960_mid.jpg' if g['start']==9960 else PRE/'调整前'/f"{g['start']}.jpg"
   old=np.array(Image.open(baseline_path).convert('RGB'),float);new=np.array(im,float)
   for ph in row['photo_frames']:
    w,h=ph['dimensions'];size=ph['photo_size_first_mid_last'][1];cx,cy=ph['center'];pw,phh=w*size,h*size
    x0,x1=int(cx*1920-pw*.25),int(cx*1920+pw*.25);y0,y1=int((1-cy)*1080-phh*.25),int((1-cy)*1080+phh*.25)
    delta=float(abs(old[y0:y1,x0:x1]-new[y0:y1,x0:x1]).mean());assert delta<.1,(g['start'],ph['side'],delta)
    photo_checks.append({'start':g['start'],'side':ph['side'],'interior_mean_rgb_difference':delta,'reference':str(baseline_path)})
 if i%5==0:print('V13_PACKAGE_BOUNDARIES',i,flush=True)
assert snap(t)==before['snapshot'];assert graphs(t)==before['graphs'];assert len(photo_checks)==44
(OUT/'package_boundary_frames_v13.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
(OUT/'package_visual_qa_v13.json').write_text(json.dumps({'groups':22,'actual_native_frames':len(records),'photo_checks':photo_checks,'all_clip_timing_and_properties_preserved':True,'all_color_nodes_and_versions_preserved':True,'transient_preview_reloaded':True},ensure_ascii=False,indent=2))
(OUT/'final_native_snapshot_v13.json').write_text(json.dumps(snap(t),ensure_ascii=False,indent=2))
for st in [7509,4051]:
 g=next(x for x in GROUPS if x['start']==st);N=g['length'];seq=PRE/'连续运动校验'/str(st);seq.mkdir(parents=True,exist_ok=True)
 for i in range(N):
  cap(p,t,st+i,seq/f'{i:04d}.jpg',.20)
  if (i+1)%20==0:print('V13_MOTION_FRAMES',st,i+1,flush=True)
assert t.SetCurrentTimecode(tc(7536));assert pm.SaveProject();print('V13_MOTION_CAPTURE_READY',flush=True)
