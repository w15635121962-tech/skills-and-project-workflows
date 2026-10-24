import sys,json,math
from pathlib import Path
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';plan=json.loads((OUT/'opening_plan_v5.json').read_text());groups=json.loads((OUT/'picture_change_groups_v5.json').read_text());baseline=json.loads((OUT/'live_before_v5.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool();t=p.GetCurrentTimeline();assert p.GetName()=='学校' and t.GetName()==plan['name']
def snap(t):
 return {typ:[{'track':k,'enabled':t.GetIsTrackEnabled(typ,k),'locked':t.GetIsTrackLocked(typ,k),'name':t.GetTrackName(typ,k),'items':[{'name':it.GetName(),'start':it.GetStart(),'end':it.GetEnd(),'offset':it.GetLeftOffset(),'path':it.GetMediaPoolItem().GetClipProperty('File Path') if it.GetMediaPoolItem() else None,'properties':it.GetProperty(),'enabled':it.GetClipEnabled(),'fusion_count':it.GetFusionCompCount()} for it in t.GetItemListInTrack(typ,k)]} for k in range(1,t.GetTrackCount(typ)+1)] for typ in ['video','audio']}
before=snap(t);assert before['audio']==baseline['snapshot']['audio'];assert before['video'][0]==baseline['snapshot']['video'][0]
title=t.GetItemListInTrack('video',2)[0];assert title.GetStart()==340 and title.GetDuration()==168
items={v.GetStart():v for v in t.GetItemListInTrack('video',1)};oldstarts={s for g in groups for s in g['old_record_frames']};remove=[items[a] for a in sorted(oldstarts)]
for v in remove:assert not v.GetLinkedItems()
assert t.DeleteClips(remove,False);assert t.GetEndFrame()==11507
folder=mp.AddSubFolder(mp.GetRootFolder(),'开篇向往感精修_v5_20261017');assert folder and mp.SetCurrentFolder(folder)
def walk(f):
 yield from f.GetClipList()
 for sf in f.GetSubFolderList():yield from walk(sf)
pool={x.GetClipProperty('File Path'):x for x in walk(mp.GetRootFolder())}
infos=[]
for g in groups:
 s=g['new']
 if s['path'] not in pool:
  imported=mp.ImportMedia([s['path']]);assert imported and len(imported)==1;pool[s['path']]=imported[0]
 m=pool[s['path']];fps=float(m.GetClipProperty('FPS'));assert fps==s['fps'];a=round(s['in']*fps);count=math.ceil(s['length_frames']/25*fps-1e-8)
 infos.append({'mediaPoolItem':m,'startFrame':a,'endFrame':a+count,'mediaType':1,'trackIndex':1,'recordFrame':s['record_frame']})
added=mp.AppendToTimeline(infos);assert added and len(added)==len(groups)
for g,v in zip(groups,added):
 s=g['new'];assert v.GetStart()==s['record_frame'] and v.GetDuration()==s['length_frames'];assert v.GetMediaPoolItem().GetClipProperty('Online Status')=='Online'
 assert v.GetNodeGraph().SetLUT(1,'Sony/SLog3SGamut3.CineToLC-709TypeA.cube');v.SetClipColor('Blue')
 if s['record_frame']==0:
  c=v.AddFusionComp();assert c;mi=c.FindToolByID('MediaIn');mo=c.FindToolByID('MediaOut');bc=c.AddTool('BrightnessContrast');assert mi and mo and bc
  assert bc.ConnectInput('Input',mi);bc.Gain=c.BezierSpline();bc.Gain[0]=0;bc.Gain[12]=1;assert mo.ConnectInput('Input',bc);assert v.ExportFusionComp(str(OUT/'v5-opening-fade.comp'),1)
 print('V5_REVISED',s['record_frame']/25,s['name'],s['length_frames']/25,flush=True)
assert t.SetTrackName('video',1,'画面_书院光影与真实师生_开篇向往感')
assert t.AddMarker(2,'Purple','v5 开篇：向往学校','古树庭院从容起笔；真实同伴互动与抬头倾听；阅读实拍；师生辅导长停留；13.60–20.32独立宋体片名。',1765,'v5-human-aspiration')
after=snap(t);assert after['audio']==baseline['snapshot']['audio']
old_untouched=[v for v in baseline['snapshot']['video'][0]['items'] if v['start'] not in oldstarts];newstarts={g['new']['record_frame'] for g in groups};new_untouched=[v for v in after['video'][0]['items'] if v['start'] not in newstarts];assert old_untouched==new_untouched
v1=t.GetItemListInTrack('video',1);assert len(v1)==119 and t.GetEndFrame()==11507;assert all(a.GetEnd()==b.GetStart() for a,b in zip(v1,v1[1:]));assert all(v.GetMediaPoolItem().GetClipProperty('Online Status')=='Online' for v in v1)
assert pm.SaveProject();assert t.SetCurrentTimecode('00:00:00:20')
(OUT/'native_build_v5.json').write_text(json.dumps({'timeline':t.GetName(),'duration_seconds':460.28,'picture_count':119,'opening_picture_count':18,'old_picture_items_revised':len(oldstarts),'new_picture_items':len(added),'audio_preserved':True,'untouched_picture_preserved':True,'picture_after_70_68_preserved':True,'title':{'start':title.GetStart(),'end':title.GetEnd(),'editable_text':True},'snapshot':after},ensure_ascii=False,indent=2))
print('V5_NATIVE_PICTURE_COMPLETE',flush=True)
