import json, sys, datetime
from pathlib import Path
sys.path.insert(0, '/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve

out=Path(__file__).resolve().parent
(out/'备份').mkdir(exist_ok=True)
r=get_resolve(); pm=r.GetProjectManager(); p=pm.GetCurrentProject()
assert p and p.GetName()=='大码枕头'
original=p.GetCurrentTimeline()
report={'project':p.GetName(),'version':r.GetVersionString(),'time':datetime.datetime.now().isoformat(),
        'current_timeline':original.GetName(),'current_timecode':original.GetCurrentTimecode(),
        'settings':p.GetSetting(),'timelines':[],'media':[]}
assert pm.SaveProject()
backup=out/'备份/大码枕头_男版21-25剪辑前.drp'
if not backup.exists():
    assert pm.ExportProject(p.GetName(),str(backup))
assert backup.stat().st_size>0
report['backup']=str(backup)
for i in range(1,p.GetTimelineCount()+1):
    t=p.GetTimelineByIndex(i)
    row={'index':i,'name':t.GetName(),'id':t.GetUniqueId(),'start':t.GetStartFrame(),'end':t.GetEndFrame(),'tracks':{}}
    detailed=('男' in t.GetName() or '性转' in t.GetName())
    if detailed: row['settings']=t.GetSetting()
    for typ in ['video','audio','subtitle']:
        row['tracks'][typ]=[]
        for j in range(1,t.GetTrackCount(typ)+1):
            items=t.GetItemListInTrack(typ,j) or []
            a={'index':j,'name':t.GetTrackName(typ,j),'count':len(items),'enabled':t.GetIsTrackEnabled(typ,j)}
            if detailed:
                a['items']=[]
                for x in items:
                    m=x.GetMediaPoolItem()
                    a['items'].append({'name':x.GetName(),'start':x.GetStart(),'end':x.GetEnd(),
                        'source_start':x.GetSourceStartFrame() if m else None,'source_end':x.GetSourceEndFrame() if m else None,
                        'source_path':m.GetClipProperty('File Path') if m else None,'properties':x.GetProperty()})
            row['tracks'][typ].append(a)
    report['timelines'].append(row)
def walk(f,parent=''):
    path=parent+'/'+f.GetName()
    for x in f.GetClipList() or []:
        report['media'].append({'folder':path,'id':x.GetUniqueId(),'name':x.GetName(),'properties':x.GetClipProperty()})
    for sub in f.GetSubFolderList() or []: walk(sub,path)
walk(p.GetMediaPool().GetRootFolder())
(out/'Resolve_操作前实读.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'project':p.GetName(),'backup_bytes':backup.stat().st_size,'timelines':[
    {'name':x['name'],'seconds':(x['end']-x['start'])/24,
     'counts':{k:sum(y['count'] for y in v) for k,v in x['tracks'].items()}} for x in report['timelines']],
    'media_count':len(report['media'])},ensure_ascii=False),flush=True)
