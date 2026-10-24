from native_common import *
from insert_srt import parse_srt,native_cues
r,m,p,pool=connect();e=load_plan(BASE/'final_native_plan_含SRT.json')['episodes'][0];row=read(BASE/'Resolve_组装实读.json')['episodes'][0];t=next(t for t in timelines(p) if t.GetUniqueId()==row['id']);assert t.GetName()==TIMELINE and p.SetCurrentTimeline(t)
for k,i,key in [('video',1,'video'),('audio',1,'video'),('audio',2,'narration')]:
 items=t.GetItemListInTrack(k,i);assert len(items)==len(e[key])
 for item,c in zip(items,e[key]):assert_clip(item,c)
before=av(t);expected=parse_srt(e['subtitle_srt']);actual=native_cues(t)
if actual:
 assert actual==[[a+1594,b+1594,c] for a,b,c in expected]
 write(BASE/'修订前可恢复备份/EP20_重开后确认首次错误字幕.json',{'id':t.GetUniqueId(),'cues':actual,'only_task_owned':True})
 assert t.DeleteClips(t.GetItemListInTrack('subtitle',1),False)
 assert not native_cues(t) and av(t)==before and t.GetEndFrame()==1594
 assert m.SaveProject()
if not t.GetTrackCount('subtitle'):assert t.AddTrack('subtitle')
assert t.GetTrackCount('subtitle')==1 and not native_cues(t)
root=child(pool,pool.GetRootFolder(),BASE.name);folder=child(pool,child(pool,root,'按集SRT字幕_先入轨后预设'),'EP20');assert pool.SetCurrentFolder(folder)
found=[x for x in folder.GetClipList() or [] if x.GetClipProperty('File Path')==e['subtitle_srt']]
if not found:
 found=pool.ImportMedia([e['subtitle_srt']]);assert found and len(found)==1
assert r.OpenPage('edit') and t.SetCurrentTimecode('00:00:00:00') and m.SaveProject()
write(BASE/'字幕/SRT_原生菜单准备.json',{'timeline':t.GetName(),'id':t.GetUniqueId(),'folder':'EP20','media_name':found[0].GetName(),'source':e['subtitle_srt'],'empty_subtitle_track_added':True,'av_unchanged':av(t)==before,'current_native_av_end':t.GetEndFrame(),'next':'Use native context menu insert subtitles using timecode. Never AppendToTimeline.'})
print(json.dumps({'media_name':found[0].GetName(),'folder':'EP20','empty_subtitle_track':True,'av_end':t.GetEndFrame()},ensure_ascii=False))
