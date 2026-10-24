import argparse,json,sys,math
from pathlib import Path
sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
out=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--plan',required=True);args=parser.parse_args()
plan=json.loads(Path(args.plan).read_text(encoding='utf-8'))
assert (out/'备份/大码枕头_男版21-25剪辑前.drp').stat().st_size>0
levels={x['source_path']:x for x in json.loads((out/'ASR/source_levels.json').read_text(encoding='utf-8'))['files']}
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p and p.GetName()=='大码枕头'
mp=p.GetMediaPool();root=mp.GetRootFolder()
parent=next(x for x in root.GetSubFolderList() if x.GetName()=='男版21-25_自动剪辑_20261021')
assert mp.SetCurrentFolder(parent)
def walk(f):
    d={x.GetClipProperty('File Path'):x for x in f.GetClipList() or [] if x.GetClipProperty('File Path')}
    for sub in f.GetSubFolderList() or []:d.update(walk(sub))
    return d
media=walk(parent)
new_paths=sorted({c['path'] for ep in plan['episodes'] for c in ep['video'] if c['path'] not in media})
if new_paths:
    assert all(Path(x).suffix.lower()=='.png' and Path(x).exists() for x in new_paths)
    still_folder=mp.AddSubFolder(parent,'剪辑静帧');assert still_folder and mp.SetCurrentFolder(still_folder)
    imported=mp.ImportMedia(new_paths);assert imported and len(imported)==len(new_paths)
    media.update({x.GetClipProperty('File Path'):x for x in imported})
    assert mp.SetCurrentFolder(parent)
names={p.GetTimelineByIndex(i).GetName():p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)}
def frames(s):return round(s*24)
native=out/'原生时间线';native.mkdir(exist_ok=True)
logfile=out/'Resolve_组装实读.json'
log=json.loads(logfile.read_text(encoding='utf-8')) if logfile.exists() else {'project':p.GetName(),'episodes':[]}
for ep in plan['episodes']:
    number=ep['episode'];name=f'大码_男版_EP{number}_原速旁白_自动剪辑_v1'
    assert name not in names,'Do not overwrite existing edits: '+name
    for kind in ['video','narration']:
        for c in ep[kind]:
            assert c['path'] in media and Path(c['path']).exists(),c
            if kind=='video' and c.get('kind')=='still':
                assert '/男版21-25_自动剪辑_20261021/剪辑静帧/' in c['path'] and Path(c['path']).suffix.lower()=='.png'
            else:
                assert ('/男版/' in c['path'] if kind=='video' else '（男版）' in c['path']),c
                assert Path(c['path']).suffix.lower()==('.mp4' if kind=='video' else '.mp3')
    t=mp.CreateEmptyTimeline(name);assert t and p.SetCurrentTimeline(t)
    settings=t.GetSettings()
    assert float(settings['timelineFrameRate'])==24
    assert str(settings['timelineResolutionWidth'])=='1080' and str(settings['timelineResolutionHeight'])=='1920'
    assert t.SetStartTimecode('00:00:00:00')
    while t.GetTrackCount('audio')<2:assert t.AddTrack('audio','mono')
    assert t.SetTrackName('video',1,f'男版{number}_剧情画面')
    assert t.SetTrackName('audio',1,'同期声_与画面链接')
    assert t.SetTrackName('audio',2,'Oliver原速旁白' if number<23 else 'Vittoria原速旁白')
    result={'episode':number,'timeline':name,'id':t.GetUniqueId(),'fps':24,'video':[],'sync_audio':[],'narration':[],
            'limitations':ep.get('limitations',[])}
    for c in ep['video']:
        inf={'mediaPoolItem':media[c['path']],'startFrame':frames(c['src0']),'endFrame':frames(c['src1']),
             'recordFrame':frames(c['record']),'trackIndex':1}
        made=[]
        kinds=[('video',1)] if c.get('kind')=='still' else [('video',1),('sync_audio',2)]
        for kind,typ in kinds:
            added=mp.AppendToTimeline([dict(inf,mediaType=typ)]);assert added and len(added)==1
            item=added[0];made.append(item)
            assert item.GetStart()==inf['recordFrame']
            assert item.GetEnd()==inf['recordFrame']+inf['endFrame']-inf['startFrame']
            assert item.GetSourceStartFrame()==inf['startFrame']
            if kind=='sync_audio':
                gain=float(c.get('gain_db',0))
                # Original stream remains enabled; reduce ambience under voiceover.
                assert item.SetProperties({'AudioVolumeEnabled':True,'AudioVolume':gain})
                assert abs(item.GetProperties()['AudioVolume']-gain)<.01
            row=dict(c,id=item.GetUniqueId(),start=item.GetStart(),end=item.GetEnd(),
                     source_start=item.GetSourceStartFrame(),source_end=item.GetSourceEndFrame(),enabled=item.GetClipEnabled())
            assert row['enabled']
            result[kind].append(row)
        if len(made)==2:
            assert t.SetClipsLinked(made,True)
            linked=made[0].GetLinkedItems() or []
            assert made[1].GetUniqueId() in [x.GetUniqueId() for x in linked]
        t.AddMarker(inf['recordFrame'],'Blue',c['tag'],'男版原稿本集同号；画面和原片同期声同源同剪，均100%。',1)
    for c in ep['narration']:
        inf={'mediaPoolItem':media[c['path']],'startFrame':frames(c['src0']),'endFrame':frames(c['src1']),
             'recordFrame':frames(c['record']),'trackIndex':2,'mediaType':2}
        added=mp.AppendToTimeline([inf]);assert added and len(added)==1
        x=added[0]
        assert x.GetStart()==inf['recordFrame'] and x.GetEnd()==inf['recordFrame']+inf['endFrame']-inf['startFrame']
        lev=levels[c['path']]
        gain=round(min(0,-17-lev['integrated_loudness_lufs'],-2-lev['true_peak_dbfs']),2)
        assert x.SetProperties({'AudioVolumeEnabled':True,'AudioVolume':gain})
        assert abs(x.GetProperties()['AudioVolume']-gain)<.01
        result['narration'].append(dict(c,id=x.GetUniqueId(),start=x.GetStart(),end=x.GetEnd(),
                source_start=x.GetSourceStartFrame(),source_end=x.GetSourceEndFrame(),gain_db=gain,enabled=x.GetClipEnabled()))
    assert t.GetStartFrame()==0 and t.GetEndFrame()==frames(ep['duration_seconds'])
    assert t.GetIsTrackEnabled('video',1) and t.GetIsTrackEnabled('audio',1) and t.GetIsTrackEnabled('audio',2)
    result['duration_frames']=t.GetEndFrame();result['settings']=t.GetSettings()
    for i,warning in enumerate(result['limitations'],1):
        t.AddMarker(i,'Yellow','源素材待补',warning,1)
    assert pm.SaveProject()
    result['drt']=str(native/(name+'.drt'));assert t.Export(result['drt'],r.EXPORT_DRT)
    result['otio']=str(native/(name+'.otio'));assert t.Export(result['otio'],r.EXPORT_OTIO)
    log['episodes'].append(result)
    logfile.write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'timeline':name,'seconds':t.GetEndFrame()/24,'video':len(result['video']),
                     'linked_sync':len(result['sync_audio']),'vo_segments':len(result['narration'])},ensure_ascii=False),flush=True)
assert pm.SaveProject()
