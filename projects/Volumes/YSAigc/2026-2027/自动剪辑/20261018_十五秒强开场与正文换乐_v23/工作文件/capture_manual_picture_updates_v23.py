from common_v23 import *
import shutil
r,pm,p,mp,t=connect();before=json.loads((OUT/'final_native_snapshot_v23.json').read_text());g=json.loads((OUT/'final_graphs_v23.json').read_text());assert snap(t)==before and graphs(t)==g
oldroot=ROOT.parent/'20261018_开头提速与首镜重选_v22/工作文件';old=json.loads((oldroot/'final_native_snapshot_v22.json').read_text());oldg=json.loads((oldroot/'final_graphs_v22.json').read_text());changed=set()
for now,previous in zip(before['video'],old['video']):
 assert now['enabled']==previous['enabled']
 for a,b in [(now,previous),(previous,now)]:
  for item in a['items']:
   if item not in b['items']:changed.update(range(max(0,int(item['start'])),min(667,int(item['end']))))
# A changed grade without an item trim/property change also requires new native frames.
gm={(x['track'],x['start']):x for x in g};ogm={(x['track'],x['start']):x for x in oldg}
for tr in before['video']:
 for item in tr['items']:
  key=(tr['track'],item['start'])
  if gm.get(key)!=ogm.get(key):changed.update(range(max(0,int(item['start'])),min(667,int(item['end']))))
seq=OUT/'开篇_原生逐帧';seq.mkdir(exist_ok=True);assert not any(seq.glob('*.jpg'))
for f in range(667):shutil.copy2(oldroot/f'开篇_原生逐帧/{f:04d}.jpg',seq/f'{f:04d}.jpg')
r.OpenPage('edit');start=time.time()
for k,f in enumerate(sorted(changed)):
 assert p.GetCurrentTimeline().GetName()==TIMELINE;im=cap(p,t,f,seq/f'{f:04d}.jpg',wait=.025);assert im.size==(1920,1080)
 if (k+1)%25==0:print('UPDATED_NATIVE',k+1,'of',len(changed),flush=True)
assert snap(t)==before and graphs(t)==g
q={'total_frames':667,'fps':25,'resolution':[1920,1080],'new_native_frames':len(changed),'new_native_frame_indices':sorted(changed),'reused_verified_native_frames':667-len(changed),'fresh_manual_edits_preserved':True,'timeline_unchanged_during_capture':True,'copied_images_are_independent_files':True,'actual_unchanged_picture_checks':'native_apply_qa_v23.json','elapsed_seconds':time.time()-start};(OUT/'native_preview_capture_qa_v23.json').write_text(json.dumps(q,ensure_ascii=False,indent=2));assert t.SetCurrentTimecode(tc(0));assert pm.SaveProject();print('ALL_667_NATIVE_IMAGES_READY',len(changed),flush=True)
