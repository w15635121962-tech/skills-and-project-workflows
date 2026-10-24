"""One-time explicit rebase before EP20. Default does not connect or mutate."""
import argparse,datetime,shutil
from native_common import *
V1_JSON=DEFAULT_BASELINE_JSON
V1_DRP=DEFAULT_BACKUP
V2_JSON=BASE/'剪辑前_项目与时间线实读_v2.json'
V2_DRP=BASE/'大码枕头_男版EP20自动剪辑前_20261023_v2.drp'
ARCHIVE=BASE/'追加人工修改前_原始基线备份'
EVIDENCE=BASE/'诊断/原时间线清单差异_20261023T061730_060375Z.json'

def archive_v1():
    ARCHIVE.mkdir(exist_ok=True)
    sources=[V1_JSON,V1_DRP,EVIDENCE]
    if BASELINE_POINTER.exists():sources.append(BASELINE_POINTER)
    entries=[]
    for source in sources:
        assert source.is_file(),('Missing original evidence',source)
        before=sha(source);dest=ARCHIVE/source.name
        if dest.exists():assert sha(dest)==before,('Never overwrite earlier archive',dest)
        else:shutil.copy2(source,dest)
        assert sha(dest)==before and sha(source)==before
        entries.append({'original_path':str(source),'archived_path':str(dest),
                        'sha256':before,'size_bytes':source.stat().st_size,
                        'source_unchanged':True,'copy_verified':True})
    manifest=ARCHIVE/'manifest.json'
    if manifest.exists():assert read(manifest)['entries']==entries,'Archive manifest conflict'
    else:write(manifest,{'purpose':'Recoverable v1 baseline, full DRP, external-change evidence and previous pointer.',
                         'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'entries':entries})
    return entries

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    if not args.execute:
        print('Offline v2 rebase prepared. No copies, Resolve connection, save/export or pointer update performed.')
        return
    assert baseline_paths()==(V1_JSON,V1_DRP),'One-time v1 to v2 rebase only.'
    assert not V2_JSON.exists() and not V2_DRP.exists(),'Do not overwrite previous/partial v2; inspect before retry.'
    v1=read(V1_JSON)
    assert v1['project']==PROJECT and v1['backup_drp']==str(V1_DRP)
    assert sha(V1_DRP)==v1['backup_sha256']
    original_ids={x['id'] for x in v1['timelines']}
    assert len(original_ids)==73,'Expected the original 73 timelines.'
    copies=archive_v1()
    resolve,manager,project,pool=connect()
    current=timelines(project)
    assert all(t.GetName()!=TIMELINE for t in current),'EP20 target already exists; cannot rebase after task edits.'
    assert original_ids<={t.GetUniqueId() for t in current},'An original timeline is missing.'
    assert manager.SaveProject(),'Save the latest external user edits before a fresh baseline.'
    before=inventory(project)
    states=[{'id':t.GetUniqueId(),'name':t.GetName(),'state':timeline_state(t)} for t in timelines(project)]
    assert manager.ExportProject(PROJECT,str(V2_DRP)) and V2_DRP.stat().st_size>100000
    assert inventory(project)==before,'Timeline inventory changed during v2 export.'
    live={t.GetUniqueId():t for t in timelines(project)}
    for old in states:
        after=timeline_state(live[old['id']])
        a=baseline_semantic_state(old['state']);b=baseline_semantic_state(after)
        if digest(a)!=digest(b):
            failure=diagnostic_path('v2基线采集中再次发生变化')
            write(failure,{'timeline_id':old['id'],'timeline_name':old['name'],
                           'before':old['state'],'after':after,'differences':state_differences(a,b),
                           'v2_drp':str(V2_DRP),'pointer_updated':False})
            raise AssertionError(('State changed during v2 capture; old pointer retained',str(failure)))
        old['state_sha256']=digest(old['state'])
    report={'project':PROJECT,'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'baseline_version':2,'timelines':before,'timeline_states':states,
            'backup_drp':str(V2_DRP),'backup_sha256':sha(V2_DRP),'backup_bytes':V2_DRP.stat().st_size,
            'target_timeline':TIMELINE,'new_timeline_created':False,
            'scope':'Explicit adoption of user external edits. No clips or timelines edited by this script.',
            'previous_baseline_path':str(V1_JSON),'previous_baseline_sha256':sha(V1_JSON),
            'previous_drp_path':str(V1_DRP),'previous_drp_sha256':sha(V1_DRP),
            'immutable_archive_manifest':str(ARCHIVE/'manifest.json'),
            'accepted_external_change_evidence':{'path':str(EVIDENCE),'sha256':sha(EVIDENCE)},
            'original_timeline_ids_preserved':len(original_ids),'latest_timeline_count':len(before)}
    write(V2_JSON,report)
    assert sha(V1_JSON)==next(x['sha256'] for x in copies if x['original_path']==str(V1_JSON))
    assert sha(V1_DRP)==next(x['sha256'] for x in copies if x['original_path']==str(V1_DRP))
    pointer={'project':PROJECT,'episode':20,'version':2,'baseline_json':str(V2_JSON),
             'baseline_sha256':sha(V2_JSON),'backup_drp':str(V2_DRP),'backup_sha256':sha(V2_DRP),
             'activated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'reason':'Explicitly adopt saved user edits before any EP20 timeline exists.',
             'previous_baseline_json':str(V1_JSON),'previous_backup_drp':str(V1_DRP),
             'archive_manifest':str(ARCHIVE/'manifest.json')}
    write(BASELINE_POINTER,pointer);assert read(BASELINE_POINTER)==pointer
    write(BASE/'准备/基线v2显式重建记录.json',{'success':True,'copied_originals':copies,
          'v1_files_unchanged':True,'new_baseline':str(V2_JSON),'new_drp':str(V2_DRP),
          'active_pointer':pointer,'original_timeline_count_preserved':len(original_ids),
          'no_timeline_selected_or_edited':True,'next_step':'Start a new assemble_native process; active baseline v2 is fully frozen.'})
    print(json.dumps({'active_baseline':str(V2_JSON),'new_drp':str(V2_DRP),
                      'original_timelines_preserved':len(original_ids),'latest_timeline_count':len(before)},ensure_ascii=False))

if __name__=='__main__':main()
