import json, sys, time
from pathlib import Path
sys.path.insert(0, '/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '工作文件'
PRE = ROOT / '精修预览'
BASE = ROOT.parent / '20261017_人物动态与缓推精修_v8' / '工作文件'
NAME = '学校_双图包装与人文调色_v9_20261017'

def connect():
    r=get_resolve(); pm=r.GetProjectManager(); p=pm.GetCurrentProject()
    assert p and p.GetName()=='学校'
    return r,pm,p,p.GetMediaPool(),p.GetCurrentTimeline()

def snap(t):
    return {typ:[{'track':k,'enabled':t.GetIsTrackEnabled(typ,k),'locked':t.GetIsTrackLocked(typ,k),'name':t.GetTrackName(typ,k),'items':[{'name':it.GetName(),'start':it.GetStart(),'end':it.GetEnd(),'offset':it.GetLeftOffset(),'path':it.GetMediaPoolItem().GetClipProperty('File Path') if it.GetMediaPoolItem() else None,'properties':it.GetProperty(),'enabled':it.GetClipEnabled(),'fusion_count':it.GetFusionCompCount()} for it in t.GetItemListInTrack(typ,k)]} for k in range(1,t.GetTrackCount(typ)+1)] for typ in ['video','audio']}

def save(name,data):
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2))

def tc(f):
    sec,fr=divmod(int(f),25);mi,sec=divmod(sec,60);hr,mi=divmod(mi,60)
    return f'{hr:02d}:{mi:02d}:{sec:02d}:{fr:02d}'

def capture(p,t,f,path,wait=.12):
    from PIL import Image
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    assert t.SetCurrentTimecode(tc(f));time.sleep(wait)
    assert p.ExportCurrentFrameAsStill(str(path)),str(path)
    im=Image.open(path).convert('RGB');assert im.size==(1920,1080)
    return im

def walk(folder):
    yield from folder.GetClipList()
    for f in folder.GetSubFolderList():yield from walk(f)
