import sys,json
from pathlib import Path
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件'
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool();t=p.GetCurrentTimeline()
assert p.GetName()=='学校' and t.GetName()=='学校_全片复核精修_v4_20261017'
def snap(t):
 return {typ:[{'track':k,'enabled':t.GetIsTrackEnabled(typ,k),'locked':t.GetIsTrackLocked(typ,k),'name':t.GetTrackName(typ,k),'items':[{'name':it.GetName(),'start':it.GetStart(),'end':it.GetEnd(),'offset':it.GetLeftOffset(),'path':it.GetMediaPoolItem().GetClipProperty('File Path') if it.GetMediaPoolItem() else None,'properties':it.GetProperty(),'enabled':it.GetClipEnabled(),'fusion_count':it.GetFusionCompCount()} for it in t.GetItemListInTrack(typ,k)]} for k in range(1,t.GetTrackCount(typ)+1)] for typ in ['video','audio']}
snapshot=snap(t)
prior=json.loads((ROOT.parent/'20261017_全片复核精修_v4/工作文件/native_build_v4.json').read_text())['snapshot']
assert snapshot['audio']==prior['audio']
assert all(a['start']==b['start'] and a['end']==b['end'] and a['path']==b['path'] for a,b in zip(snapshot['video'][0]['items'],prior['video'][0]['items']))
title=t.GetItemListInTrack('video',2)[0];c=title.GetFusionCompByIndex(1)
tools=[{'name':v.GetAttrs()['TOOLS_Name'],'id':v.GetAttrs()['TOOLS_RegID']} for v in c.GetToolList().values()]
fonts=r.Fusion().FontManager.GetFontList()
rec={'project':p.GetName(),'timeline':t.GetName(),'page':r.GetCurrentPage(),'timecode':t.GetCurrentTimecode(),'selected_pool_media':[x.GetName() for x in (mp.GetSelectedClips() or [])],'snapshot':snapshot,'title_tools':tools,'candidate_fonts':{k:v for k,v in fonts.items() if any(a in k.lower() for a in ['songti','kaiti','heiti','baskerville','times'])}}
(OUT/'live_before_v5.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2))
assert pm.SaveProject();backup=ROOT/'学校_开篇向往感精修前备份.drt';assert not backup.exists();assert t.Export(str(backup),r.EXPORT_DRT)
print(json.dumps({'timeline':t.GetName(),'title_tools':tools,'fonts':rec['candidate_fonts'],'audio':snapshot['audio']},ensure_ascii=False,indent=2))
