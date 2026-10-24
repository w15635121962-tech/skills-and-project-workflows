"""Replace only female EP01-03 A4 narration in native duplicated timelines.

No ripple edits. Original timelines are retained as explicitly named backups.
"""
import datetime
import hashlib
import json
from pathlib import Path
import sys
import time

sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve

BASE=Path(__file__).resolve().parent
frozen=json.loads((BASE/'替换前_完整时间线实读.json').read_text(encoding='utf-8'))
media_plan=json.loads((BASE/'42段对齐WAV_制作结果.json').read_text(encoding='utf-8'))
assert len(media_plan['clips'])==42
assert Path(frozen['backup']).stat().st_size>1000000
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool()
assert p.GetName()=='大码枕头'

def stable_select(t):
    assert p.SetCurrentTimeline(t)
    time.sleep(.3)
    assert p.GetCurrentTimeline().GetUniqueId()==t.GetUniqueId()

def item(c):
    m=c.GetMediaPoolItem()
    return {'name':c.GetName(),'start':c.GetStart(),'end':c.GetEnd(),
            'left':c.GetLeftOffset(),'right':c.GetRightOffset(),
            'enabled':c.GetClipEnabled(),'source_start':c.GetSourceStartTime(),
            'source_end':c.GetSourceEndTime(),'media_id':m.GetMediaId() if m else None,
            'properties':c.GetProperty()}

def read(t):
    return {'name':t.GetName(),'id':t.GetUniqueId(),'start':t.GetStartFrame(),'end':t.GetEndFrame(),
            'fps':t.GetSetting('timelineFrameRate'),'tracks':{k:[{
              'index':i,'name':t.GetTrackName(k,i),'enabled':t.GetIsTrackEnabled(k,i),
              'items':[item(c) for c in t.GetItemListInTrack(k,i) or []]}
              for i in range(1,t.GetTrackCount(k)+1)] for k in ['video','audio','subtitle']}}

def semantic_old(old):
    return {'start':old['start'],'end':old['end'],'fps':old['fps'],
       'tracks':{k:[{**{a:b for a,b in tr.items() if a!='items'},
         'items':[{key:c[key] for key in ['name','start','end','left','right','enabled','source_start','source_end','media_id','properties']}
                  for c in tr['items']]} for tr in ts] for k,ts in old['tracks'].items()}}

def outside_narration(state):
    x=json.loads(json.dumps(state))
    x.pop('name',None);x.pop('id',None)
    x['tracks']['audio'][3]['items']=[]
    return x

existing={p.GetTimelineByIndex(i).GetUniqueId():p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)}
folder=next((f for f in mp.GetRootFolder().GetSubFolderList() or [] if f.GetName()=='前3集_新对标旁白_20261021'),None)
folder=folder or mp.AddSubFolder(mp.GetRootFolder(),'前3集_新对标旁白_20261021');assert folder
assert mp.SetCurrentFolder(folder)
paths=[x['path'] for x in media_plan['clips']]
for x in media_plan['clips']:
    assert hashlib.sha256(Path(x['path']).read_bytes()).hexdigest()==x['sha256']
lookup={x.GetClipProperty('File Path'):x for x in folder.GetClipList() or []}
missing=[f for f in paths if f not in lookup]
if missing:
    imported=mp.ImportMedia(missing);assert imported and len(imported)==len(missing)
    lookup.update({x.GetClipProperty('File Path'):x for x in imported})
assert all(path in lookup for path in paths)
results=[];working=[]
for old in frozen['timelines']:
    ep=old['ep'];original=existing[old['id']]
    stable_select(original);before=read(original)
    assert outside_narration(before)==outside_narration(semantic_old(old)),('Original was edited since freeze',ep)
    old_items=original.GetItemListInTrack('audio',4)
    assert [x.GetUniqueId() for x in old_items]==[x['id'] for x in old['tracks']['audio'][3]['items']]
    work_name=f"大码_女版_EP{ep:02d}_新旁白对齐_20261021"
    assert work_name not in {x.GetName() for x in existing.values()},'Inspect existing work before resume'
    work=original.DuplicateTimeline(work_name);assert work
    stable_select(work);pre=read(work)
    assert outside_narration(pre)==outside_narration(before)
    was_locked=work.GetIsTrackLocked('audio',4)
    if was_locked:assert work.SetTrackLock('audio',4,False)
    clips=work.GetItemListInTrack('audio',4) or []
    assert len(clips)==len(old_items)
    assert work.DeleteClips(clips,False)
    rows=sorted([x for x in media_plan['clips'] if x['episode']==ep],key=lambda x:x['record_start_frame'])
    actual=[]
    for entry,old_clip in zip(rows,old['tracks']['audio'][3]['items']):
        assert entry['old_item_id']==old_clip['id']
        assert p.GetCurrentTimeline().GetUniqueId()==work.GetUniqueId()
        added=mp.AppendToTimeline([{'mediaPoolItem':lookup[entry['path']],
               'recordFrame':entry['record_start_frame'],'trackIndex':4,'mediaType':2}])
        assert added and len(added)==1
        c=added[0]
        assert (c.GetStart(),c.GetEnd())==(entry['record_start_frame'],entry['record_end_frame_exclusive']),('Range mismatch',ep,c.GetStart(),c.GetEnd(),entry)
        assert c.SetProperties(old_clip['properties'])
        assert c.SetClipEnabled(old_clip['enabled'])
        assert c.GetProperty()==old_clip['properties']
        assert c.GetMediaPoolItem().GetClipProperty('File Path')==entry['path']
        actual.append(item(c))
    if was_locked:assert work.SetTrackLock('audio',4,True)
    after=read(work)
    assert outside_narration(after)==outside_narration(before),'Unexpected change outside A4'
    assert [(x['start'],x['end']) for x in actual]==[(x['start'],x['end']) for x in old['tracks']['audio'][3]['items']]
    result={'episode':ep,'old_id':original.GetUniqueId(),'working_id':work.GetUniqueId(),
            'original_name':old['name'],'working_name':work.GetName(),'new_clips':actual,
            'picture_subtitles_other_audio_unchanged':True,'all_record_slots_unchanged':True,
            'source_files':len(set(x['source_new_mp3'] for x in rows)),'after':after,
            'save_returned':pm.SaveProject()}
    results.append(result);working.append((original,work,old['name']))
    (BASE/'替换执行中_原生回读.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'ep':ep,'clips':len(actual),'all_other_editing_unchanged':True,'working':work.GetName()},ensure_ascii=False),flush=True)

for original,work,name in working:
    backup_name=name+'_旧旁白备份_20261021'
    assert original.SetName(backup_name)
    assert work.SetName(name)
    assert (original.GetName(),work.GetName())==(backup_name,name)
    row=next(x for x in results if x['working_id']==work.GetUniqueId())
    row['backup_timeline']=backup_name;row['final_timeline']=name
    assert work.Export(str(BASE/'备份'/(name+'_新旁白已替换.drt')),r.EXPORT_DRT)
stable_select(working[0][1]);assert working[0][1].SetCurrentTimecode('00:00:00:00')
saved=pm.SaveProject()
out=BASE/'备份'/'大码枕头_前3集新旁白已替换.drp'
assert pm.ExportProject(p.GetName(),str(out))
final={'status':'REPLACED_NATIVE_PENDING_REOPEN_QC','project':p.GetName(),'episodes':results,
       'source_files':24,'timeline_clips':42,'final_save_returned':saved,'final_project_backup':str(out),
       'user_requested_picture_subtitle_sync_sound_timing_preserved':True,
       'local_tempo_adaptation_baked_into_editable_wav_clips':True,
       'completed_at':datetime.datetime.now().isoformat()}
(BASE/'前三集_替换后原生回读.json').write_text(json.dumps(final,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'complete':True,'source_files':24,'timeline_clips':42,'final_save':saved},ensure_ascii=False),flush=True)
