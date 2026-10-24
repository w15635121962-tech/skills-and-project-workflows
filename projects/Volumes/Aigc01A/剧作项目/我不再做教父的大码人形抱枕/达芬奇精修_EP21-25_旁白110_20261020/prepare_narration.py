import json,re,sys
from pathlib import Path
sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
OUT=Path(__file__).resolve().parent
snap=json.loads((OUT/'Resolve_精修前实时实读.json').read_text())
cuts={a['live_A2_item_id']:a for a in json.loads((OUT/'音频精修确定剪口.json').read_text())['proposals']}
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool()
ts={p.GetTimelineByIndex(i).GetName():p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)}
def walk(f):
 for x in f.GetClipList() or []:
  path=x.GetClipProperty('File Path')
  if path:media[path]=x
 for c in f.GetSubFolderList() or []:walk(c)
media={};walk(mp.GetRootFolder())
plan={'episodes':[]}
for old in snap['timelines']:
 ep=int(re.search(r'EP(\d+)',old['name'])[1]);base=ts[old['name']]
 name=f'大码_女版_EP{ep}_精修_旁白110_v2'
 work=ts.get(name) or base.DuplicateTimeline(name);assert work
 prep=base.DuplicateTimeline(f'EP{ep}_旁白110准备_v2');assert prep;p.SetCurrentTimeline(prep)
 for kind in ['video','audio','subtitle']:
  for i in range(1,prep.GetTrackCount(kind)+1):
   prep.SetTrackLock(kind,i,False)
   items=prep.GetItemListInTrack(kind,i) or []
   if items:assert prep.DeleteClips(items,False)
 for kind in ['subtitle','audio']:
  target=0 if kind=='subtitle' else 2
  for i in range(prep.GetTrackCount(kind),target,-1):prep.DeleteTrack(kind,i)
 assert prep.GetTrackCount('subtitle')==0
 assert all(not prep.GetItemListInTrack(k,i) for k in ['video','audio'] for i in range(1,prep.GetTrackCount(k)+1))
 groups=[];removed=0;ordinal=0
 for item in old['tracks']['audio'][1]['items']:
  src0=item['source_start'];src1=src0+item['end']-item['start']
  keep=cuts.get(item['id'],{}).get('new_keep_source_ranges_frames',[[src0,src1]])
  record=item['start']-removed;parts=[]
  for a,b in keep:
   result=mp.AppendToTimeline([{'mediaPoolItem':media[item['source_path']],'startFrame':a,'endFrame':b,'recordFrame':record,'trackIndex':2,'mediaType':2}]);assert result and result[0]
   x=result[0];assert x.GetStart()==record and x.GetEnd()==record+b-a
   assert x.SetProperties({'AudioVolume':item['properties']['AudioVolume'],'AudioVolumeEnabled':True})
   parts.append({'ordinal':ordinal,'source_start':a,'source_end':b,'pre_record_start':record,'pre_record_end':record+b-a})
   ordinal+=1;record+=b-a
  removed+=(src1-src0)-sum(b-a for a,b in keep)
  groups.append({'old':item,'kept_source_ranges':keep,'parts':parts})
 plan['episodes'].append({'episode':ep,'original':old['name'],'working':name,'prep':prep.GetName(),'groups':groups,'precut_removed_frames':removed})
 print(ep,prep.GetName(),'clips',ordinal,'silence_tail_removed',removed,flush=True)
(OUT/'旁白原生110执行计划.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
p.SetCurrentTimeline(next(p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()==plan['episodes'][0]['prep']))
assert pm.SaveProject()
