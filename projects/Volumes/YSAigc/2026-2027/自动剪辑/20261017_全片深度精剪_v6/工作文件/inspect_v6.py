import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件'
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool();t=p.GetCurrentTimeline();assert p.GetName()=='学校'
def snap(t):
 return {typ:[{'track':k,'enabled':t.GetIsTrackEnabled(typ,k),'locked':t.GetIsTrackLocked(typ,k),'name':t.GetTrackName(typ,k),'items':[{'name':it.GetName(),'start':it.GetStart(),'end':it.GetEnd(),'offset':it.GetLeftOffset(),'path':it.GetMediaPoolItem().GetClipProperty('File Path') if it.GetMediaPoolItem() else None,'properties':it.GetProperty(),'enabled':it.GetClipEnabled(),'fusion_count':it.GetFusionCompCount()} for it in t.GetItemListInTrack(typ,k)]} for k in range(1,t.GetTrackCount(typ)+1)] for typ in ['video','audio']}
current=snap(t);prior=json.loads((ROOT.parent/'20261017_开篇向往感精修_v5/工作文件/native_build_v5.json').read_text())['snapshot']
record={'project':p.GetName(),'timeline':t.GetName(),'page':r.GetCurrentPage(),'timecode':t.GetCurrentTimecode(),'selected_pool':[x.GetName() for x in (mp.GetSelectedClips() or [])],'snapshot':current,'matches_delivered_v5':current==prior,'markers':t.GetMarkers()}
(OUT/'live_before_v6.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
assert t.GetName()=='学校_开篇向往感精修_v5_20261017' and current==prior,'Manual edits detected: inspect before planning mutations'
assert pm.SaveProject();path=ROOT/'学校_全片深度精剪前备份.drt';assert not path.exists();assert t.Export(str(path),r.EXPORT_DRT)
for v in t.GetItemListInTrack('video',1):
 if v.GetFusionCompCount():assert v.ExportFusionComp(str(OUT/f'baseline-v1-{v.GetStart()}.comp'),1)
title=t.GetItemListInTrack('video',2)[0];assert title.ExportFusionComp(str(OUT/'baseline-opening-title.comp'),1)
print(json.dumps({'timeline':t.GetName(),'matches_v5':True,'video_items':[len(x['items']) for x in current['video']],'audio_items':[len(x['items']) for x in current['audio']],'backup':str(path)},ensure_ascii=False))
