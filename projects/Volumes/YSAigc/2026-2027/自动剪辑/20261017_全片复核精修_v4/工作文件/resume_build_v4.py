import sys,json
from pathlib import Path
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';plan=json.loads((OUT/'refined_plan_v4.json').read_text());groups=json.loads((OUT/'native_change_groups_v4.json').read_text());before=json.loads((OUT/'live_before_v4.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='学校';mp=p.GetMediaPool();t=p.GetCurrentTimeline();assert t.GetName()==plan['name']
def snap(t):
 return {typ:[{'track':k,'enabled':t.GetIsTrackEnabled(typ,k),'locked':t.GetIsTrackLocked(typ,k),'name':t.GetTrackName(typ,k),'items':[{'name':it.GetName(),'start':it.GetStart(),'end':it.GetEnd(),'offset':it.GetLeftOffset(),'path':it.GetMediaPoolItem().GetClipProperty('File Path') if it.GetMediaPoolItem() else None,'properties':it.GetProperty(),'enabled':it.GetClipEnabled(),'fusion_count':it.GetFusionCompCount()} for it in t.GetItemListInTrack(typ,k)]} for k in range(1,t.GetTrackCount(typ)+1)] for typ in ['video','audio']}
assert t.AddMarker(1,'Green','v4 全片复核精修','完整配音再次转写及波形核查；16处画面/动作节奏修正，6处既有字幕淡入淡出；3:55一处字音待听辨。',1,'v4-audit')
after=snap(t);assert after['audio']==before['snapshot']['audio'];assert after['video'][1]==before['snapshot']['video'][1]
modified={g['record_frame'] for g in groups};old_untouched=[x for x in before['snapshot']['video'][0]['items'] if x['start'] not in modified];new_untouched=[x for x in after['video'][0]['items'] if x['start'] not in modified and x['start']!=4289];assert old_untouched==new_untouched
v1=t.GetItemListInTrack('video',1);assert len(v1)==121 and t.GetEndFrame()==11507;assert all(a.GetEnd()==b.GetStart() for a,b in zip(v1,v1[1:]));assert v1[0].GetStart()==0
for s,v in zip(plan['shots'],v1):assert v.GetStart()==s['record_frame'] and v.GetDuration()==s['length_frames'] and v.GetMediaPoolItem().GetClipProperty('File Path')==s['path']
titles=[]
for v in v1:
 if v.GetStart() not in [3749,3832,3891,3954,11042,11407]:continue
 comp=v.GetFusionCompByIndex(1);text=comp.FindToolByID('TextPlus');assert comp.FindTool('Merge1').GetInput('Blend',0)==0 and comp.FindTool('Merge2').GetInput('Blend',v.GetDuration()-1)==0
 titles.append({'start':v.GetStart(),'duration':v.GetDuration(),'text':text.GetInput('StyledText')})
assert len(titles)==6;assert pm.SaveProject();assert t.SetCurrentTimecode('00:00:00:20')
(OUT/'native_build_v4.json').write_text(json.dumps({'timeline':t.GetName(),'duration_seconds':460.28,'video_count':121,'changed_original_picture_items':len(groups),'inserted_picture_segments':sum(len(g['segments']) for g in groups),'refined_titles':titles,'audio_preserved':True,'unmodified_picture_items_preserved':True,'opening_title_preserved':True,'snapshot':after},ensure_ascii=False,indent=2),encoding='utf-8');print('BUILT_V4',len(v1),flush=True)
