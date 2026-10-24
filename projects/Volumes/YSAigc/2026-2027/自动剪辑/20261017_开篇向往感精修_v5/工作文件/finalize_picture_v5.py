import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';plan=json.loads((OUT/'opening_plan_v5.json').read_text());baseline=json.loads((OUT/'live_before_v5.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool();t=p.GetCurrentTimeline();assert t.GetName()==plan['name'];assert r.OpenPage('edit')
v=next(x for x in t.GetItemListInTrack('video',1) if x.GetStart()==1397);assert v.GetDuration()==126 and v.GetLeftOffset()==114
media=v.GetMediaPoolItem();assert 'A003C097_' in media.GetClipProperty('File Path');assert t.DeleteClips([v],False)
added=mp.AppendToTimeline([{'mediaPoolItem':media,'startFrame':175,'endFrame':301,'mediaType':1,'trackIndex':1,'recordFrame':1397}]);assert added and len(added)==1
v=added[0];assert v.GetDuration()==126 and v.GetLeftOffset()==175 and v.GetStart()==1397;assert v.GetNodeGraph().SetLUT(1,'Sony/SLog3SGamut3.CineToLC-709TypeA.cube');v.SetClipColor('Blue')
def snap(t):
 return {typ:[{'track':k,'enabled':t.GetIsTrackEnabled(typ,k),'locked':t.GetIsTrackLocked(typ,k),'name':t.GetTrackName(typ,k),'items':[{'name':it.GetName(),'start':it.GetStart(),'end':it.GetEnd(),'offset':it.GetLeftOffset(),'path':it.GetMediaPoolItem().GetClipProperty('File Path') if it.GetMediaPoolItem() else None,'properties':it.GetProperty(),'enabled':it.GetClipEnabled(),'fusion_count':it.GetFusionCompCount()} for it in t.GetItemListInTrack(typ,k)]} for k in range(1,t.GetTrackCount(typ)+1)] for typ in ['video','audio']}
after=snap(t);assert after['audio']==baseline['snapshot']['audio'];assert [x for x in after['video'][0]['items'] if x['start']>=1767]==[x for x in baseline['snapshot']['video'][0]['items'] if x['start']>=1767]
assert len(t.GetItemListInTrack('video',1))==119 and t.GetEndFrame()==11507;assert pm.SaveProject()
f=OUT/'native_build_v5.json';rec=json.loads(f.read_text());rec['snapshot']=after;rec['teacher_source_final']={'record_frame':1397,'length_frames':126,'source_in':7.0,'source_out':12.04,'reason':'avoid source6.31–6.81 foreground crossing; retain teacher natural response'};f.write_text(json.dumps(rec,ensure_ascii=False,indent=2))
print('TEACHER_FINAL_SOURCE',v.GetLeftOffset()/25,flush=True)
