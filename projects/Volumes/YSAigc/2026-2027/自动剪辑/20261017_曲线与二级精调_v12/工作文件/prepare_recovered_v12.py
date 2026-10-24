import sys,json
from pathlib import Path
sys.path.insert(0,'/Volumes/YSAigc/2026-2027/自动剪辑/20261017_双图包装与全片调色_v9/工作文件')
from common_v9 import snap
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
R=Path(__file__).resolve().parents[1];r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='学校_曲线二级精修_v12'
t=p.GetCurrentTimeline();print('CURRENT',t.GetName(),flush=True);assert t.GetName()=='学校_通透感与高光控制_v11_20261017';before=json.loads((R/'工作文件/live_before_v12.json').read_text());assert snap(t)==before['snapshot'];assert pm.SaveProject()
n=t.DuplicateTimeline('学校_曲线与二级精调_v12_20261017');assert n and p.SetCurrentTimeline(n);assert snap(n)==before['snapshot'];assert r.OpenPage('edit');assert pm.SaveProject();print('RECOVERED_V12_NATIVE_BASE_READY',flush=True)
