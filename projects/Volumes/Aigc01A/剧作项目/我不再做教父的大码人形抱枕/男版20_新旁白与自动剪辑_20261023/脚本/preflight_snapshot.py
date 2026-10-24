"""Explicit execution only: preserve all existing timelines before the EP20 edit."""
import argparse,datetime
from native_common import *

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--execute',action='store_true')
    args=parser.parse_args()
    if not args.execute:
        print('Offline preparation only. No Resolve connection, snapshot, export or save performed.')
        return
    target=BASELINE_JSON
    assert not target.exists() and not BACKUP.exists(),'Do not replace an earlier recoverable baseline.'
    r,m,p,pool=connect()
    assert all(t.GetName()!=TIMELINE for t in timelines(p)), 'Target name already exists; inspect before proceeding.'
    assert m.SaveProject(),'Save pre-existing user work before full export'
    before=inventory(p)
    states=[{'id':t.GetUniqueId(),'name':t.GetName(),'state':timeline_state(t)} for t in timelines(p)]
    assert m.ExportProject(PROJECT,str(BACKUP)) and BACKUP.stat().st_size>100000
    assert inventory(p)==before
    for row in states:row['state_sha256']=digest(row['state'])
    report={'project':PROJECT,'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'timelines':before,'timeline_states':states,'backup_drp':str(BACKUP),
            'backup_sha256':sha(BACKUP),'backup_bytes':BACKUP.stat().st_size,
            'target_timeline':TIMELINE,'new_timeline_created':False,
            'scope':'Full pre-edit DRP and existing timeline AV/caption/marker state; no clips or timelines changed.'}
    write(target,report);assert_baseline(p)
    print(json.dumps({'backup':str(BACKUP),'existing_timelines_preserved':len(before)},ensure_ascii=False))

if __name__=='__main__':main()
