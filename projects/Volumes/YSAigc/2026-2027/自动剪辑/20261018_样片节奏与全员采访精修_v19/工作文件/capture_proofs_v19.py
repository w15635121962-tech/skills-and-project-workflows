from common_v19 import *
r,pm,p,mp,t=connect();r.OpenPage('edit');assert t.GetEndFrame()==12520
frames=[0,80,116,117,174,175,233,234,286,287,340,420,507,508,560,561,613,614,11041,11042,11228,11229,11488,11489,11506,11507,11805,11806,12054,12055,12162,12163,12254,12255,12330,12331,12419,12420,12470,12508,12519]
for f in frames:cap(p,t,f,PRE/f'原生核验_{f:05d}.jpg',wait=.05)
assert max(np.array(Image.open(PRE/'原生核验_12519.jpg')).ravel())<8,'ending picture did not fade to black'
ranges=[{'name':'开篇','start':0,'end':667},{'name':'全员采访与尾声','start':10992,'end':12520}]
for row in ranges:
 folder=OUT/(row['name']+'_原生逐帧');folder.mkdir(exist_ok=True)
 for index,f in enumerate(range(row['start'],row['end'])):
  path=folder/f'{index:04d}.jpg'
  if not path.exists():cap(p,t,f,path,wait=.03)
  if index%125==0:print(row['name'],index,'/',row['end']-row['start'],flush=True)
 row['folder']=str(folder);row['frame_count']=row['end']-row['start'];row['duration_seconds']=row['frame_count']/25
(OUT/'native_capture_complete_v19.json').write_text(json.dumps({'fps':25,'width':1920,'height':1080,'ranges':ranges,'all_frames_fresh_from_active_native_timeline':True,'final_frame_near_black':True},ensure_ascii=False,indent=2))
assert t.SetCurrentTimecode(tc(0));assert pm.SaveProject();print('NATIVE_SEQUENCE_CAPTURE_COMPLETE',flush=True)
