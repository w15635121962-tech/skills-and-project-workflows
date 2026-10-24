import json,sys
from pathlib import Path
sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
out=Path(__file__).resolve().parent
inventory=json.loads((out/'男版素材盘点.json').read_text(encoding='utf-8'))
assert (out/'备份/大码枕头_男版21-25剪辑前.drp').stat().st_size>0
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='大码枕头'
mp=p.GetMediaPool();root=mp.GetRootFolder()
def child(f,name):
    match=[x for x in f.GetSubFolderList() or [] if x.GetName()==name]
    return match[0] if match else mp.AddSubFolder(f,name)
parent=child(root,'男版21-25_自动剪辑_20261021');assert parent
report=[]
for ep in inventory['episodes']:
    folder=child(parent,f"男版EP{ep['episode']}");assert folder
    for key,label in [('videos','视频与同期声'),('narration_audio','原速旁白')]:
        sources=ep.get(key)
        if sources is None:
            assert key=='narration_audio'
            sources=ep.get('narration_files',ep.get('narration',ep.get('audios')))
        assert isinstance(sources,list),(key,ep.keys())
        sub=child(folder,label);assert sub and mp.SetCurrentFolder(sub)
        existing={x.GetClipProperty('File Path'):x for x in sub.GetClipList() or []}
        paths=[x['path'] for x in sources]
        needed=[x for x in paths if x not in existing]
        if needed:
            added=mp.ImportMedia(needed);assert added and len(added)==len(needed),(key,ep['episode'])
            existing.update({x.GetClipProperty('File Path'):x for x in added})
        for path in paths:
            x=existing[path];props=x.GetClipProperty()
            report.append({'episode':ep['episode'],'kind':key,'path':path,'id':x.GetUniqueId(),'properties':props})
        print(ep['episode'],label,len(paths),flush=True)
assert pm.SaveProject()
(out/'Resolve_媒体导入实读.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
