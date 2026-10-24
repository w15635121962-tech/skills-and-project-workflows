import sys,json,zipfile,hashlib
from pathlib import Path
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='学校';mp=p.GetMediaPool();t=p.GetCurrentTimeline();assert t.GetName()=='学校_开篇人文精修_v3_20261017'
before=json.loads((OUT/'live_before_v3.json').read_text())['snapshot']
def clip(it):return {'name':it.GetName(),'start':it.GetStart(),'end':it.GetEnd(),'offset':it.GetLeftOffset(),'path':it.GetMediaPoolItem().GetClipProperty('File Path') if it.GetMediaPoolItem() else None,'properties':it.GetProperty(),'enabled':it.GetClipEnabled(),'fusion_count':it.GetFusionCompCount()}
audio=[{'track':k,'enabled':t.GetIsTrackEnabled('audio',k),'locked':t.GetIsTrackLocked('audio',k),'items':[clip(it) for it in t.GetItemListInTrack('audio',k)]} for k in range(1,5)]
assert audio==before['audio'];v1=t.GetItemListInTrack('video',1);assert len(v1)==120 and all(a.GetEnd()==b.GetStart() for a,b in zip(v1,v1[1:]));assert t.GetEndFrame()==11507
assert [clip(x) for x in v1 if x.GetStart()>=1767]==[x for x in before['video'][0]['items'] if x['start']>=1767]
assert t.GetIsTrackEnabled('video',2) and not t.GetIsTrackLocked('video',1);assert len(t.GetItemListInTrack('video',2))==1
assert t.SetCurrentTimecode('00:00:00:20');assert r.OpenPage('edit');assert pm.SaveProject()
archives=[]
for kind,path in [('drt',ROOT/'学校_开篇人文精修_v3.drt'),('drp',ROOT/'学校_开篇人文精修_v3.drp')]:
 assert not path.exists(),path
 ok=t.Export(str(path),r.EXPORT_DRT) if kind=='drt' else pm.ExportProject('学校',str(path),True);assert ok and path.exists() and path.stat().st_size>1000
 with zipfile.ZipFile(path) as z:assert z.testzip() is None
 archives.append({'path':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'zip_integrity':'passed'})
report={'timeline':t.GetName(),'duration_seconds':460.28,'opening_refined_seconds':70.68,'opening_picture_count':20,'total_picture_count':120,'independent_title_count':1,'audio_identical_to_v2':True,'picture_after_opening_identical_to_v2':True,'title_fades_verified_from_actual_frames':True,'all_original_timelines_preserved':[p.GetTimelineByIndex(i).GetName() for i in range(1,p.GetTimelineCount()+1)],'archives':archives,'limitations':['720p shooting proxies plus mixed-resolution archive assets','No final MP4 export or full-film playback/listening pass in this visual revision']}
(OUT/'final_delivery_v3.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False),flush=True)
