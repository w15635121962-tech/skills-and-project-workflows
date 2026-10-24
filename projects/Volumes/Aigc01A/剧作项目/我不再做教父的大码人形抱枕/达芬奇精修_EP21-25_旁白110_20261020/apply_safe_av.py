#!/usr/bin/env python3
"""Prepared offline. Default checks files only; --apply connects to Resolve.

Replaces only V1/A1/A3 of the five named working timelines. A2 native110,
all subtitles and A4 are fingerprinted and left untouched. No settings API
is called. Official local SDK README documents ImportMedia/AppendToTimeline,
DeleteClips/SetClipsLinked/track locks/timeline markers; Resolve21.1's
SetProperties/GetProperties are used as in this project's verified scripts,
with documented singular SetProperty/GetProperty fallbacks.
"""
import argparse
import copy
import datetime
import hashlib
import json
import math
import re
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
MAP=HERE/'原生110_安全画面与A1A3执行映射.json'
SNAP=HERE/'Resolve_精修前实时实读.json'
NATIVE=HERE/'原生110分组实测.json'
FREEZE=HERE/'剪辑静帧/EP22_起身停顿9帧/导入信息.json'
README='/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/README.txt'

def read(p):return json.loads(Path(p).read_text())
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,default=str).encode()).hexdigest()
def near(a,b):
 if isinstance(a,(int,float)) and isinstance(b,(int,float)):return math.isclose(float(a),float(b),abs_tol=1e-5)
 return a==b
def props(item):
 try:v=item.GetProperties()
 except Exception:v=None
 return v if isinstance(v,dict) else (item.GetProperty() or {})
def setprops(item,expected):
 if not expected:return
 try:ok=item.SetProperties(expected)
 except Exception:ok=False
 if not ok:
  for k,v in expected.items():assert item.SetProperty(k,v),(item.GetName(),'property rejected',k,v)
 actual=props(item)
 for k,v in expected.items():assert k in actual and near(actual[k],v),(item.GetName(),'property readback',k,v,actual.get(k))
def seqkey(path):
 return re.sub(r'\[(\d+)-(\d+)\]|%0\d+d','<sequence>',str(path))
def media_path(item):
 m=item.GetMediaPoolItem()
 return m.GetClipProperty('File Path') if m else None
def itemrow(item):
 m=item.GetMediaPoolItem()
 return {'id':item.GetUniqueId(),'name':item.GetName(),'start':item.GetStart(),'end':item.GetEnd(),
         'duration':item.GetDuration(),'source_start':item.GetSourceStartFrame() if m else None,
         'source_end':item.GetSourceEndFrame() if m else None,'source_path':media_path(item),
         'properties':props(item),'enabled':item.GetClipEnabled(),'fusion_count':item.GetFusionCompCount()}
def rows(t,kind,idx):return [itemrow(i) for i in t.GetItemListInTrack(kind,idx) or []]
def basic_rows(rows_):return [(r['start'],r['end'],r.get('source_start'),r.get('source_end'),seqkey(r.get('source_path'))) for r in rows_]
def protected(t):
 out={}
 for kind in ['video','audio','subtitle']:
  for idx in range(1,t.GetTrackCount(kind)+1):
   if (kind,idx) in [('video',1),('audio',1),('audio',3)]:continue
   out[f'{kind}:{idx}']=rows(t,kind,idx)
 return out
def snapshot_tracks(t):
 return {kind:[{'track':i,'locked':t.GetIsTrackLocked(kind,i),'enabled':t.GetIsTrackEnabled(kind,i),
                'name':t.GetTrackName(kind,i),'items':rows(t,kind,i)} for i in range(1,t.GetTrackCount(kind)+1)]
         for kind in ['video','audio','subtitle']}
def normalise_video(entries,freeze):
 out=[]
 for p in copy.deepcopy(entries):
  if p['kind']=='freeze_frame' and out and out[-1]['kind']=='freeze_frame' and out[-1]['record_frame']+out[-1]['duration_frames']==p['record_frame'] and p['source_path']==out[-1]['source_path'] and p['freeze_source_frame']==out[-1]['freeze_source_frame']:
   out[-1]['duration_frames']+=p['duration_frames'];continue
  out.append(p)
 for p in out:
  if p['kind']=='freeze_frame':
   assert p['duration_frames']==9 and p['record_frame']==576 and p['freeze_source_frame']==44
   p['original_freeze_source']=p['source_path'];p['source_path']=freeze['display_path']
   p['source_start_frame']=0;p['source_end_frame_exclusive']=9
   p['kind']='image_sequence';p['import_media']=freeze['import_media']
   p['freeze_materialized']=True
 return out
def offline_inputs(map_path=MAP):
 plan=read(map_path);snap=read(SNAP);native=read(NATIVE);freeze=read(FREEZE)
 assert len(plan['episodes'])==5 and plan['validation']['groups']==27
 assert Path(README).is_file()
 for i in range(9):assert Path(freeze['import_media']['FilePath'].replace('%04d',f'{i:04d}')).is_file()
 snap_by={t['name']:t for t in snap['timelines']};native_by={e['episode']:e for e in native['episodes']}
 for e in plan['episodes']:
  assert re.fullmatch(r'大码_女版_EP2[1-5]_精修_旁白110_v2',e['timeline_name'])
  e['video']=normalise_video(e['video'],freeze)
  base=snap_by[e['original_timeline_name']]
  assert e['duration_frames']==base['end']-base['start']-e['total_removed_frames']
  a1=e['audio_A1'];old=base['tracks']['audio'][0]['items']
  assert len(a1)==len(old)
  for p,q in zip(a1,old):
   assert (p['source_path'],p['source_start_frame'],p['source_end_frame_exclusive'])==(q['source_path'],q['source_start'],q['source_start']+q['duration'])
  for a in e['audio_A3']:
   pool=base['tracks']['audio'][2]['items']
   matches=[q for q in pool if q['source_path']==a['source_path'] and q['source_start']<=a['source_start_frame']<q['source_start']+q['duration']]
   if not matches:matches=[q for q in pool if q['source_path']==a['source_path']]
   inherited=copy.deepcopy(matches[0]['properties']) if matches else {}
   inherited.update(a.get('properties',{}));a['properties']=inherited
  for key in ['video','audio_A1','audio_A3']:
   for p in e[key]:
    assert p['speed_ratio']==1 and p['duration_frames']==p['source_end_frame_exclusive']-p['source_start_frame']
    assert p['record_frame']>=0 and p['record_frame']+p['duration_frames']<=e['duration_frames']
  assert e['video'][0]['record_frame']==0 and e['video'][-1]['record_frame']+e['video'][-1]['duration_frames']==e['duration_frames']
  assert all(a['record_frame']+a['duration_frames']==b['record_frame'] for a,b in zip(e['video'],e['video'][1:]))
  assert len(e['groups'])==len(native_by[e['episode']]['groups'])
 return plan,snap,native,freeze
def import_info(path):
 m=re.search(r'\[(\d+)-(\d+)\]',str(path))
 if not m:return str(path)
 a,b=m.groups();return {'FilePath':str(path)[:m.start()]+f'%0{len(a)}d'+str(path)[m.end():],
                         'StartIndex':int(a),'EndIndex':int(b)}
def walk(folder):
 result={seqkey(m.GetClipProperty('File Path')):m for m in folder.GetClipList() or [] if m.GetClipProperty('File Path')}
 for child in folder.GetSubFolderList() or []:result.update(walk(child))
 return result
def marker_map(x,groups):
 # Identical source-time mapping used by the native110 subtitle plan.
 for g in groups:
  old=g['old']
  if old['start']<=x<old['end']:
   src=old['source_start']+x-old['start']
   for part,actual in zip(g['parts'],g['native_110']):
    if src<part['source_start']:return actual['start']
    if src<=part['source_end']:return min(actual['end'],actual['start']+(src-part['source_start'])/1.1)
   return g['new_end']
 return x-sum(g['removed_frames'] for g in groups if x>=g['old']['end'])
def remap_markers(t,original,groups,duration):
 old=original.GetMarkers() or {};working=t.GetMarkers() or {};result={};moves=[]
 def signature(m):return (m.get('name'),m.get('note'),m.get('color'),m.get('customData'))
 def insert(frame,m,origin):
  frame=max(0,min(duration-1,int(round(frame))));m=copy.deepcopy(m)
  m['duration']=max(1,min(duration-frame,int(round(m.get('duration',1)))))
  if frame in result:
   prev=result[frame];prev['name']+=' | '+m.get('name','')
   prev['note']+='\n[合并同帧标记] '+m.get('name','')+'\n'+m.get('note','')
   prev['customData']=json.dumps({'merged_customData':[prev.get('customData',''),m.get('customData','')]},ensure_ascii=False)
  else:result[frame]=m
  moves.append({'old_frame':origin,'new_frame':frame,'name':m.get('name','')})
 for frame,m in old.items():
  start=marker_map(float(frame),groups);end=marker_map(float(frame)+float(m.get('duration',1)),groups)
  q=copy.deepcopy(m);q['duration']=max(1,round(end-start));insert(start,q,float(frame))
 for frame,m in working.items():
  original_at=next((q for k,q in old.items() if near(float(k),float(frame)) and signature(q)==signature(m)),None)
  if original_at is None:insert(float(frame),m,'working_only_preserved')
 for frame in working:assert t.DeleteMarkerAtFrame(float(frame)),('delete marker',frame)
 for frame,m in sorted(result.items()):
  assert t.AddMarker(frame,m.get('color','Blue'),m.get('name',''),m.get('note',''),m.get('duration',1),m.get('customData','')),('add marker',frame,m)
 actual=t.GetMarkers() or {};assert len(actual)==len(result)
 for frame,m in result.items():
  a=next(v for k,v in actual.items() if near(float(k),frame))
  assert all(near(a.get(k),v) for k,v in m.items() if k in ['color','name','note','duration','customData'])
 return moves
def assert_item(item,p):
 assert (item.GetStart(),item.GetEnd(),item.GetDuration())==(p['record_frame'],p['record_frame']+p['duration_frames'],p['duration_frames']),('record/duration mismatch',p,itemrow(item))
 assert item.GetSourceStartFrame()==p['source_start_frame'],('source in mismatch',p,item.GetSourceStartFrame())
 actual_end=item.GetSourceEndFrame();expected_end=p['source_end_frame_exclusive']
 full_frames=int(item.GetMediaPoolItem().GetClipProperty('Frames'))
 assert actual_end==expected_end or (actual_end==expected_end-1 and expected_end==full_frames),('source out mismatch',p,actual_end)
 assert seqkey(media_path(item))==seqkey(p['source_path']),('source path mismatch',p,media_path(item))
def expected_track(rows_,entries):
 return len(rows_)==len(entries) and all((r['start'],r['end'],r['source_start'],seqkey(r['source_path']))==(p['record_frame'],p['record_frame']+p['duration_frames'],p['source_start_frame'],seqkey(p['source_path'])) for r,p in zip(rows_,entries))
def inherit_live_properties(e,t,base):
 # Duplicate-timeline IDs differ from baseline IDs. The approved old source/
 # record signature has already been checked, so its ordinal is a safe bridge.
 original_by_id={q['id']:(kind,tr['track'],idx,q) for kind,tracks in base['tracks'].items()
                 for tr in tracks for idx,q in enumerate(tr['items'])}
 current={(kind,idx):rows(t,kind,idx) for kind,idx in [('video',1),('audio',1),('audio',3)]}
 for key,kind,track in [('video','video',1),('audio_A1','audio',1),('audio_A3','audio',3)]:
  baseline_pool=base['tracks'][kind][track-1]['items']
  for p in e[key]:
   old=None;live=None;ref=original_by_id.get(p.get('original_item_id'))
   if ref and ref[:2]==(kind,track):
    _,_,ordinal,old=ref;live=current[kind,track][ordinal]
   elif key=='audio_A3':
    matches=[(i,q) for i,q in enumerate(baseline_pool) if q['source_path']==p['source_path'] and q['source_start']<=p['source_start_frame']<q['source_start']+q['duration']]
    if matches:
     ordinal,old=matches[0];live=current[kind,track][ordinal]
   if live is None:continue
   # Preserve intervening visual/audio property adjustments; overlay only
   # intentional recipe changes such as the two EP22 framing corrections.
   intended={k:v for k,v in p.get('properties',{}).items() if k not in old['properties'] or not near(v,old['properties'][k])}
   merged=copy.deepcopy(live['properties']);merged.update(intended);p['properties']=merged
def verify_coverage(e):
 for v in e['video']:
  if not v['source_path'].lower().endswith('.mp4'):continue
  s=v['record_frame'];end=s+v['duration_frames'];spans=[]
  for a in e['audio_A1']+e['audio_A3']:
   x=max(s,a['record_frame']);y=min(end,a['record_frame']+a['duration_frames'])
   if x<y and a['source_path']==v['source_path'] and a['source_start_frame']+x-a['record_frame']==v['source_start_frame']+x-s:spans.append((x,y))
  at=s
  for x,y in sorted(spans):assert x<=at;at=max(at,y)
  assert at==end,('V1 same-source audio uncovered',v)

def apply(plan,snap,native,freeze,selected):
 # This is the only function that imports/connects the official SDK.
 sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
 from resolve_bootstrap import get_resolve
 r=get_resolve();pm=r.GetProjectManager();project=pm.GetCurrentProject()
 assert project and project.GetName()==snap['project']=='大码枕头'
 timelines={project.GetTimelineByIndex(i).GetName():project.GetTimelineByIndex(i) for i in range(1,project.GetTimelineCount()+1)}
 originals={t['name']:t for t in snap['timelines']};native_by={e['episode']:e for e in native['episodes']}
 episodes=[e for e in plan['episodes'] if not selected or e['episode'] in selected]
 assert len(episodes)==(len(selected) if selected else 5)
 for e in episodes:assert e['timeline_name'] in timelines and e['original_timeline_name'] in timelines
 current=project.GetCurrentTimeline();current_tc=current.GetCurrentTimecode() if current else None
 media_pool=project.GetMediaPool();media=walk(media_pool.GetRootFolder())
 needed={seqkey(p['source_path']):p for e in episodes for key in ['video','audio_A1','audio_A3'] for p in e[key]}
 for k,p in needed.items():
  if k not in media:
   request=p.get('import_media',import_info(p['source_path']))
   imported=media_pool.ImportMedia([request]);assert imported and len(imported)==1 and imported[0],('import failed',request)
   media[k]=imported[0]
  assert seqkey(media[k].GetClipProperty('File Path'))==k
  assert float(media[k].GetClipProperty('FPS'))==24,('media FPS must already be24; no project settings will be mutated',p['source_path'])
 log={'started_at':datetime.datetime.now().isoformat(),'project':project.GetName(),'sdk_readme':README,'episodes':[]}
 backupdir=HERE/'应用安全AV前备份';backupdir.mkdir(exist_ok=True)
 assert pm.SaveProject()
 try:
  for e in episodes:
   t=timelines[e['timeline_name']];base=originals[e['original_timeline_name']];ne=native_by[e['episode']]
   assert project.SetCurrentTimeline(t);assert t.GetStartFrame()==0
   for k in ['video','audio','subtitle']:
    assert t.GetTrackCount(k)>=({'video':1,'audio':4,'subtitle':1}[k])
   before_protected=protected(t);before_hash=digest(before_protected)
   actual_a2=rows(t,'audio',2);expected_a2=[a for g in ne['groups'] for a in g['native_110']]
   assert len(actual_a2)==len(expected_a2)
   for a,b in zip(actual_a2,expected_a2):
    assert (a['start'],a['end'],a['source_start'],a['source_end'],a['source_path'])==(b['start'],b['end'],b['source_start'],b['source_end'],b['path']),('native A2 changed',e['episode'],a,b)
   targets=[('video',1,'video'),('audio',1,'audio_A1'),('audio',3,'audio_A3')]
   already=all(expected_track(rows(t,k,idx),e[key]) for k,idx,key in targets)
   if already:
    log['episodes'].append({'episode':e['episode'],'timeline':t.GetName(),'status':'already_applied_targets_match','protected_hash':before_hash})
    continue
   # Refuse to overwrite intervening manual V1/A1/A3 edits or a partial run.
   for k,idx,key in targets:
    assert basic_rows(rows(t,k,idx))==basic_rows(base['tracks'][k][idx-1]['items']),('working target differs from approved baseline',e['episode'],k,idx)
   inherit_live_properties(e,t,base)
   backup=backupdir/(t.GetName()+'_安全AV替换前.drt')
   assert not backup.exists(),('pre-AV backup already exists; inspect previous run',str(backup))
   assert t.Export(str(backup),r.EXPORT_DRT)
   state={'episode':e['episode'],'timeline':t.GetName(),'backup_drt':str(backup),'before_tracks':snapshot_tracks(t),'before_markers':t.GetMarkers() or {},'protected_hash_before':before_hash,'status':'prepared'}
   log['episodes'].append(state);dump(HERE/'安全AV应用回读.json',log)
   restore={}
   for k in ['video','audio','subtitle']:
    for idx in range(1,t.GetTrackCount(k)+1):
     match=next((a for a in base['tracks'].get(k,[]) if a['track']==idx),None)
     restore[k,idx]=match['locked'] if match else t.GetIsTrackLocked(k,idx)
   try:
    # Protect all other tracks from linked deletion; no ripple delete is used.
    for k,idx in restore:assert t.SetTrackLock(k,idx,(k,idx) not in [('video',1),('audio',1),('audio',3)])
    olditems=[i for k,idx,key in targets for i in t.GetItemListInTrack(k,idx) or []]
    if olditems:assert t.SetClipsLinked(olditems,False)
    for k,idx,key in targets:
     items=t.GetItemListInTrack(k,idx) or []
     if items:assert t.DeleteClips(items,False),(e['episode'],'non-ripple delete failed',k,idx)
     assert not t.GetItemListInTrack(k,idx)
    made={}
    for k,idx,key in targets:
     made[key]=[]
     for p in e[key]:
      info={'mediaPoolItem':media[seqkey(p['source_path'])],'startFrame':p['source_start_frame'],
            'endFrame':p['source_end_frame_exclusive'],'recordFrame':p['record_frame'],
            'trackIndex':idx,'mediaType':1 if k=='video' else 2}
      q=media_pool.AppendToTimeline([info]);assert q and len(q)==1 and q[0],('Append failed',e['episode'],p)
      item=q[0];assert_item(item,p);setprops(item,p.get('properties',{}));made[key].append(item)
     actual=t.GetItemListInTrack(k,idx) or [];assert len(actual)==len(e[key])
     for item,p in zip(actual,e[key]):assert_item(item,p)
    # Restore editable matching V1/sync-audio links only. A2 remains independent.
    for vi,v in enumerate(e['video']):
     if not v['source_path'].lower().endswith('.mp4'):continue
     linked=[made['video'][vi]]
     for key in ['audio_A1','audio_A3']:
      for ai,a in enumerate(e[key]):
       if a['source_path']==v['source_path'] and a['source_start_frame']-a['record_frame']==v['source_start_frame']-v['record_frame'] and max(v['record_frame'],a['record_frame'])<min(v['record_frame']+v['duration_frames'],a['record_frame']+a['duration_frames']):linked.append(made[key][ai])
     if len(linked)>1:assert t.SetClipsLinked(linked,True)
    verify_coverage(e)
    state['marker_moves']=remap_markers(t,timelines[e['original_timeline_name']],ne['groups'],e['duration_frames'])
    assert digest(protected(t))==before_hash,'A2/subtitle/A4/other protected content changed'
    picture=t.GetItemListInTrack('video',1);assert picture[-1].GetEnd()==e['duration_frames']
    state['after_targets']={key:rows(t,k,idx) for k,idx,key in targets}
    state['picture_tail']=picture[-1].GetEnd();state['timeline_tail_including_untouched_A4']=t.GetEndFrame()
    state['protected_hash_after']=digest(protected(t));state['status']='targets_applied_verified'
   finally:
    failures=[]
    for (k,idx),locked in restore.items():
     try:
      assert t.SetTrackLock(k,idx,locked)
      assert t.GetIsTrackLocked(k,idx)==locked
     except Exception as exc:failures.append((k,idx,str(exc)))
    state['locks_restored_to_original_baseline']=not failures
    if failures:raise RuntimeError(('lock restoration failed',failures))
    dump(HERE/'安全AV应用回读.json',log)
   assert pm.SaveProject()
   print(json.dumps({'episode':e['episode'],'status':state['status'],'picture_tail':state['picture_tail'],'protected_unchanged':True},ensure_ascii=False),flush=True)
  log['completed_at']=datetime.datetime.now().isoformat();log['status']='completed_requested_target_tracks_only'
 except Exception as exc:
  log['status']='failed_no_automatic_rollback';log['error']=repr(exc)
  raise
 finally:
  if current:
   project.SetCurrentTimeline(current)
   if current_tc:current.SetCurrentTimecode(current_tc)
  dump(HERE/'安全AV应用回读.json',log)
 return log

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--apply',action='store_true',help='Explicitly connect to running Resolve and apply; omitted is OFFLINE ONLY.')
 parser.add_argument('--episode',type=int,action='append',choices=range(21,26))
 args=parser.parse_args();plan,snap,native,freeze=offline_inputs()
 for e in plan['episodes']:verify_coverage(e)
 if args.apply:apply(plan,snap,native,freeze,set(args.episode or []))
 else:print(json.dumps({'status':'OFFLINE_VALIDATED_NOT_EXECUTED','Resolve_connected':False,'episodes':[(e['episode'],e['duration_frames']) for e in plan['episodes']],'freeze_merged_to_9frame_sequence':True},ensure_ascii=False))
