import json, sys
from pathlib import Path
sys.path.insert(0, '/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
OUT=Path(__file__).resolve().parent
assert (OUT/'备份/大码枕头_女版11集自动剪辑前完整备份.drp').stat().st_size>0
a=json.loads((OUT/'准备/EP16-19_选片与新旁白方案.json').read_text(encoding='utf-8'))
b=json.loads((OUT/'准备/EP26_EP28/剪辑候选_EP26_EP28.json').read_text(encoding='utf-8'))
episodes=[]
for e in a['episodes']:
    episodes.append({'ep':e['episode'],'english_ep':e['english_episode'],'clips':[{'path':x['source_path'],'src0':x['source_start_frame'],'src1':x['source_end_frame_exclusive'],'tag':x['tag']} for x in e['video']]})
for e in b['episodes']:
    episodes.append({'ep':e['episode_local_chinese'],'english_ep':e['english_docx_episode'],'clips':[{'path':x['source_path'],'src0':x['source_in_frame'],'src1':x['source_out_frame_exclusive'],'tag':x['narrative_role']} for x in e['clips']]})
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool()
assert p.GetName()=='大码枕头'
ts={p.GetTimelineByIndex(i).GetName():p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)}
def walk(f):
    d={m.GetClipProperty('File Path'):m for m in f.GetClipList() or [] if m.GetClipProperty('File Path')}
    for sub in f.GetSubFolderList() or []:d.update(walk(sub))
    return d
media=walk(mp.GetRootFolder())
folder=next(f for f in mp.GetRootFolder().GetSubFolderList() if f.GetName()=='女版11集自动剪辑_20261020')
assert mp.SetCurrentFolder(folder)
needed=sorted({c['path'] for e in episodes for c in e['clips']}-set(media))
if needed:
    added=mp.ImportMedia(needed);assert len(added)==len(needed)
    media.update({m.GetClipProperty('File Path'):m for m in added})
log=[]
for e in episodes:
    name=f"大码_女版_EP{e['ep']}_画面同期声粗排_v1"
    assert name not in ts,'Do not overwrite edits: '+name
    t=mp.CreateEmptyTimeline(name);assert t and p.SetCurrentTimeline(t)
    assert t.SetStartTimecode('00:00:00:00')
    assert float(t.GetSetting('timelineFrameRate'))==24
    assert t.SetTrackName('video',1,'画面_源剧情顺序')
    assert t.SetTrackName('audio',1,'原片同期声_与画面链接')
    assert t.AddTrack('audio','mono')
    assert t.SetTrackName('audio',2,'新旁白_待按句避让对白')
    rec=0;rows=[]
    for c in e['clips']:
        infos={'mediaPoolItem':media[c['path']],'startFrame':c['src0'],'endFrame':c['src1'],'recordFrame':rec,'trackIndex':1}
        handles=[]
        for typ in [1,2]:
            items=mp.AppendToTimeline([dict(infos,mediaType=typ)])
            assert items and len(items)==1
            x=items[0]
            assert x.GetStart()==rec and x.GetEnd()==rec+c['src1']-c['src0'],(name,c,typ,x.GetStart(),x.GetEnd())
            handles.append(x)
        assert t.SetClipsLinked(handles,True)
        t.AddMarker(rec,'Blue',c['tag'],f"本地EP{e['ep']} / 英文Episode{e['english_ep']}；画面和同期声同源同入出，均100%。",1)
        rows.append(dict(c,record_frame=rec,end_frame=handles[0].GetEnd(),video_id=handles[0].GetUniqueId(),audio_id=handles[1].GetUniqueId()))
        rec=handles[0].GetEnd()
    assert pm.SaveProject()
    (OUT/'原生时间线').mkdir(exist_ok=True)
    assert t.Export(str(OUT/'原生时间线'/(name+'.drt')),r.EXPORT_DRT)
    assert t.Export(str(OUT/'原生时间线'/(name+'.otio')),r.EXPORT_OTIO)
    log.append({'episode':e['ep'],'timeline':name,'id':t.GetUniqueId(),'duration_frames':rec,'clips':rows,'status':'picture and linked source audio assembled; narration mix pending'})
    (OUT/'Resolve_新建6集画面同期声回读.json').write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'episode':e['ep'],'timeline':name,'video':len(rows),'sync_audio':len(rows),'seconds':rec/24},ensure_ascii=False),flush=True)
assert pm.SaveProject()
