from native_common import *
from insert_srt import parse_srt,native_cues
r,m,p,pool=connect();plan=load_plan(BASE/'final_native_plan_含SRT.json');e=plan['episodes'][0]
row=read(BASE/'Resolve_组装实读.json')['episodes'][0];t=p.GetCurrentTimeline();assert t.GetUniqueId()==row['id'] and t.GetName()==TIMELINE
expected=parse_srt(e['subtitle_srt']);before=av(t);actual=native_cues(t);assert len(actual)==len(expected)==31
assert actual==[[a+1594,b+1594,c] for a,b,c in expected]
proof=read(BASE/'字幕/导入差异_首次实读.json');assert proof['id']==t.GetUniqueId() and proof['actual']==actual
archive=BASE/'修订前可恢复备份';archive.mkdir(exist_ok=True);drt=archive/'EP20_首次字幕误追加至尾部.drt';assert not drt.exists();assert t.Export(str(drt),r.EXPORT_DRT)
write(archive/'EP20_首次字幕误追加至尾部.json',{'timeline_id':t.GetUniqueId(),'cues':actual,'drt':str(drt),'reason':'AppendToTimeline without explicit recordFrame appends SRT to timeline end. Only these proven task-owned captions are revised.'})
assert t.DeleteClips(t.GetItemListInTrack('subtitle',1),False);assert not native_cues(t) and av(t)==before
items=media(pool.GetRootFolder());srt=items[e['subtitle_srt']]
assert p.GetCurrentTimeline().GetUniqueId()==t.GetUniqueId()
made=pool.AppendToTimeline([{'mediaPoolItem':srt,'startFrame':0,'endFrame':expected[-1][1],'recordFrame':0,'trackIndex':1}])
now=native_cues(t);write(BASE/'字幕/显式零时码入轨实读.json',{'timeline_id':t.GetUniqueId(),'returned_items':len(made or []),'expected':expected,'actual':now,'matches':now==expected})
assert made and now==expected
assert t.SetTrackName('subtitle',1,'20') and t.SetTrackEnable('subtitle',1,True)
assert av(t)==before and t.GetEndFrame()==1594 and m.SaveProject()
print(json.dumps({'subtitle_count':len(now),'record_frame_zero':True,'av_unchanged':True},ensure_ascii=False))
