from common_v23 import *
base=json.loads((OUT/'live_before_v23.json').read_text());before=base['snapshot'];bg=json.loads((OUT/'live_graphs_before_v23.json').read_text());plan=json.loads((ROOT/'旁白与配乐/十五秒音乐分界_原生回装清单_v23.json').read_text())
assert len(plan['items'])==2 and all(x['container_pcm_bit_identical_to_wav'] for x in plan['items'])
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p and p.GetName()==PROJECT;mp=p.GetMediaPool();parent=p.GetCurrentTimeline();assert parent.GetName()==base['timeline'] and snap(parent)==before and graphs(parent)==bg
assert not any(p.GetTimelineByIndex(k).GetName()==TIMELINE for k in range(1,p.GetTimelineCount()+1))
t=parent.DuplicateTimeline(TIMELINE);assert t and p.SetCurrentTimeline(t);assert snap(t)==before
previous=mp.GetCurrentFolder();folder=mp.AddSubFolder(mp.GetRootFolder(),'v23_十五秒强开场与正文配乐');assert folder and mp.SetCurrentFolder(folder)
media=mp.ImportMedia([x['container_path'] for x in plan['items']]);assert len(media)==2;lookup={m.GetClipProperty('File Path'):m for m in media};assert mp.SetCurrentFolder(previous)
for x in plan['items']:assert Path(x['wav_path']).is_file() and float(lookup[x['container_path']].GetClipProperty('FPS'))==25
old=next(i for i in t.GetItemListInTrack('audio',3) if i.GetStart()==0);assert old.GetEnd()==2861;assert t.DeleteClips([old],False)
items=mp.AppendToTimeline([{**x['native_append'],'mediaPoolItem':lookup[x['container_path']]} for x in plan['items']]);assert len(items)==2
for it,row,expected in zip(items,plan['items'],[(0,375),(375,2861)]):
 assert (it.GetStart(True),it.GetEnd(True),it.GetLeftOffset(True))==(float(expected[0]),float(expected[1]),0.0);assert it.SetName(row['name']);assert it.SetClipColor('Orange')
after=snap(t);g=graphs(t);assert after['video']==before['video'] and g==bg;assert t.GetEndFrame()==11507
for tr in [0,1,3]:assert after['audio'][tr]==before['audio'][tr]
assert after['audio'][2]['items'][2:]==before['audio'][2]['items'][1:]
assert p.SetCurrentTimeline(parent);assert snap(parent)==before and graphs(parent)==bg;assert p.SetCurrentTimeline(t);assert t.SetCurrentTimecode(tc(0));r.OpenPage('edit');assert pm.SaveProject()
assert pm.CloseProject(p);p=pm.LoadProject(PROJECT);assert p;t=p.GetCurrentTimeline();assert t.GetName()==TIMELINE and snap(t)==after and graphs(t)==g
r.OpenPage('edit');checks=[]
prev=ROOT.parent/'20261018_开头提速与首镜重选_v22/工作文件/开篇_原生逐帧'
for f in [20,374,375,600]:
 path=PRE/f'音乐更换后画面核验_{f:04d}.jpg';cap(p,t,f,path,wait=.04);a=np.array(Image.open(path).convert('RGB'),float);b=np.array(Image.open(prev/f'{f:04d}.jpg').convert('RGB'),float);mad=float(abs(a-b).mean());assert mad<.2,(f,mad);checks.append({'frame':f,'unchanged_picture_RGB_MAD':mad})
(OUT/'final_native_snapshot_v23.json').write_text(json.dumps(after,ensure_ascii=False,indent=2));(OUT/'final_graphs_v23.json').write_text(json.dumps(g,ensure_ascii=False,indent=2));(OUT/'native_apply_qa_v23.json').write_text(json.dumps({'active_timeline':TIMELINE,'audio_only':True,'native_music_ranges':[[i.GetStart(),i.GetEnd()] for i in t.GetItemListInTrack('audio',3)[:2]],'switch_seconds':15,'fps':25,'duration_frames':11507,'duration_seconds':460.28,'all_video_and_grades_unchanged':True,'narration_and_live_speech_unchanged':True,'later_music_clips_unchanged':True,'parent_timeline_preserved':True,'reopen_persistence_verified':True,'actual_native_picture_checks':checks},ensure_ascii=False,indent=2));assert t.SetCurrentTimecode(tc(0));assert pm.SaveProject();print('V23_TWO_NATIVE_MUSIC_ITEMS_READY',flush=True)
