import json,sys
from pathlib import Path
sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
OUT=Path(__file__).resolve().parent
plan=json.loads((OUT/'A4配乐导入计划.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool();current=p.GetCurrentTimeline()
ts={p.GetTimelineByIndex(i).GetName():p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)}
report={'episodes':[]}
def kept(t):
 return [(k,j,i.GetUniqueId(),i.GetStart(),i.GetEnd(),i.GetName()) for k in ['video','audio','subtitle'] for j in range(1,t.GetTrackCount(k)+1) if not(k=='audio' and j==4) for i in t.GetItemListInTrack(k,j) or []]
folder=mp.AddSubFolder(mp.GetRootFolder(),'EP21-25_精修110配乐');assert folder;mp.SetCurrentFolder(folder)
for e in plan['episodes']:
 t=ts[e['timeline_name']];p.SetCurrentTimeline(t);guard=kept(t);locked=t.GetIsTrackLocked('audio',4);t.SetTrackLock('audio',4,False)
 old=t.GetItemListInTrack('audio',4) or []
 if old:assert t.DeleteClips(old,False)
 for c in e['cues']:
  media=mp.ImportMedia([c['path']]);assert media and media[0]
  a=mp.AppendToTimeline([{'mediaPoolItem':media[0],'startFrame':0,'endFrame':c['duration_frames'],'recordFrame':c['record_frame'],'trackIndex':4,'mediaType':2}]);assert a and a[0]
  item=a[0];assert (item.GetStart(),item.GetEnd())==(c['record_frame'],c['record_frame']+c['duration_frames']);assert item.SetProperties({'AudioVolume':0,'AudioVolumeEnabled':True})
 assert kept(t)==guard
 assert t.GetEndFrame()==e['duration_frames']
 t.SetTrackLock('audio',4,locked)
 report['episodes'].append({'episode':e['episode'],'timeline':t.GetName(),'cues':len(e['cues']),'duration_frames':t.GetEndFrame(),'other_tracks_preserved':True})
 print(report['episodes'][-1],flush=True)
p.SetCurrentTimeline(current);assert pm.SaveProject()
(OUT/'配乐110原生应用核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
