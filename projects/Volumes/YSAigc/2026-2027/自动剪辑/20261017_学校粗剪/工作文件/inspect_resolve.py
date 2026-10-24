import sys,json
from pathlib import Path
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool()
out=Path(__file__).parent
def folder(f):
    return {'name':f.GetName(),'clips':[{'id':x.GetMediaId(),'name':x.GetName(),'properties':x.GetClipProperty()} for x in f.GetClipList()], 'folders':[folder(x) for x in f.GetSubFolderList()]}
timelines=[]
for i in range(1,p.GetTimelineCount()+1):
 t=p.GetTimelineByIndex(i);tracks={}
 for typ in ['video','audio','subtitle']:
  tracks[typ]=[[{'name':x.GetName(),'start':x.GetStart(),'end':x.GetEnd(),'offset':x.GetLeftOffset(),'media':x.GetMediaPoolItem().GetClipProperty() if x.GetMediaPoolItem() else None} for x in t.GetItemListInTrack(typ,n)] for n in range(1,t.GetTrackCount(typ)+1)]
 timelines.append({'name':t.GetName(),'start':t.GetStartFrame(),'end':t.GetEndFrame(),'settings':t.GetSetting(),'tracks':tracks})
data={'project':p.GetName(),'settings':p.GetSetting(),'timelines':timelines,'pool':folder(mp.GetRootFolder())}
(out/'resolve_before.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
backup=out.parent/'学校_自动剪辑前备份.drp'
if not backup.exists():
 assert pm.ExportProject(p.GetName(),str(backup),True),'Backup failed'
print(json.dumps({'project':p.GetName(),'timelines':[(t['name'],t['start'],t['end'],sum(len(a) for a in t['tracks']['video'])) for t in timelines],'fps':p.GetSetting('timelineFrameRate'),'backup':str(backup)},ensure_ascii=False))
