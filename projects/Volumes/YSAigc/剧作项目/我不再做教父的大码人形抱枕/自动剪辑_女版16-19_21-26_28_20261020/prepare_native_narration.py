import json, sys
from pathlib import Path
sys.path.insert(0, '/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
assert (OUT/'备份/大码枕头_女版11集自动剪辑前完整备份.drp').stat().st_size > 0
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool()
name='女版16-19_新旁白110准备_20261020'
ts={p.GetTimelineByIndex(i).GetName():p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)}
folder=next((f for f in mp.GetRootFolder().GetSubFolderList() or [] if f.GetName()=='女版11集自动剪辑_20261020'), None)
folder=folder or mp.AddSubFolder(mp.GetRootFolder(),'女版11集自动剪辑_20261020');assert folder
assert mp.SetCurrentFolder(folder)
paths=sorted((ROOT/'对标音色旁白制作_20261020/音频').glob('第1[6-9]集/*.mp3'))
assert len(paths)==29
media=[x for x in folder.GetClipList() or [] if x.GetClipProperty('File Path') in [str(f) for f in paths]]
if not media:
    media=mp.ImportMedia([str(f) for f in paths])
assert len(media)==29
lookup={x.GetClipProperty('File Path'):x for x in media}
t=ts.get(name) or mp.CreateEmptyTimeline(name);assert t and p.SetCurrentTimeline(t)
assert not t.GetItemListInTrack('audio',1), 'Existing audio must be inspected before resume'
assert t.SetStartTimecode('00:00:00:00')
assert str(t.GetSetting('timelineFrameRate')) in ['24','24.0']
assert t.SetTrackName('audio',1,'新对标旁白_原声_待原生110')
rec=0;rows=[]
for f in paths:
    m=lookup[str(f)]
    item=mp.AppendToTimeline([m])
    assert item and len(item)==1
    x=item[0];assert x.GetDuration()>0
    rows.append({'path':str(f),'name':x.GetName(),'id':x.GetUniqueId(),'start':x.GetStart(),'end':x.GetEnd(),'source_start':x.GetSourceStartFrame(),'source_end':x.GetSourceEndFrame(),'properties':x.GetProperties()})
    rec=x.GetEnd()+24
assert pm.SaveProject()
(OUT/'准备/新旁白原生110_变速前.json').write_text(json.dumps({'timeline':name,'id':t.GetUniqueId(),'items':rows},ensure_ascii=False,indent=2),encoding='utf-8')
print('NATIVE_PREPARATION_READY',name,len(rows),rec,flush=True)
