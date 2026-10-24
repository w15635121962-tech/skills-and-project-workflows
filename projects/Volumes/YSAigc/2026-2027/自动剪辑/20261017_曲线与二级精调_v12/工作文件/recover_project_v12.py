import sys,json,time
from pathlib import Path
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
R=Path(__file__).resolve().parents[1];r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();print('CURRENT',p.GetName() if p else None,flush=True);print('PROJECTS',pm.GetProjectListInCurrentFolder(),flush=True)
name='学校_曲线二级精修_v12';backup=R/'学校_异常测试版本_完整保留.drp'
if not backup.exists():print('PRESERVE_AFFECTED_PROJECT',pm.ExportProject('学校',str(backup)),flush=True)
if name not in pm.GetProjectListInCurrentFolder():
 original=R.parent/'20261017_通透感与高光控制_v11/学校_通透感与高光控制_v11.drp';assert pm.ImportProject(str(original),name);print('IMPORTED_COMPLETE_V11_BACKUP',flush=True)
p=pm.LoadProject(name);assert p;print('RECOVERED_PROJECT_LOADED',p.GetName(),flush=True);assert r.OpenPage('edit');assert pm.SaveProject();print('RECOVERY_COMPLETE',flush=True)
