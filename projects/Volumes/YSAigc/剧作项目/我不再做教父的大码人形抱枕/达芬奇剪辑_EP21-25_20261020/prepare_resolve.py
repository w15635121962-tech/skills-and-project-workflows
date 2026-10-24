import json
import sys
from pathlib import Path

sys.path.insert(0, '/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve

out = Path(__file__).parent
base = out.parent
resolve = get_resolve()
pm = resolve.GetProjectManager()
project = pm.GetCurrentProject()
assert project and project.GetName() == '大码枕头', 'Unexpected active project'
pool = project.GetMediaPool()
root = pool.GetRootFolder()
assert pm.SaveProject(), 'Pre-edit project save failed'
backup = out / '大码枕头_剪辑前原工程备份.drp'
if not backup.exists():
    assert pm.ExportProject(project.GetName(), str(backup), True), 'Project backup failed'
assert backup.stat().st_size > 0, 'Empty project backup'

def ensure_folder(parent, name):
    for child in parent.GetSubFolderList() or []:
        if child.GetName() == name:
            return child
    folder = pool.AddSubFolder(parent, name)
    assert folder, 'Folder creation failed: ' + name
    return folder

def existing_paths(folder):
    found = {}
    for clip in folder.GetClipList() or []:
        path = clip.GetClipProperty('File Path')
        if path:
            found[path] = clip
    for child in folder.GetSubFolderList() or []:
        found.update(existing_paths(child))
    return found

existing = existing_paths(root)
top = ensure_folder(root, 'EP21-25_剪辑素材')
result = {'project': project.GetName(), 'backup': str(backup), 'episodes': []}
for ep in range(21, 26):
    episode_bin = ensure_folder(top, f'EP{ep:02d}')
    episode = {'episode': ep, 'media': []}
    for label, source_dir, extension in [
        ('视频_所有候选', base / '剧梦生成视频片段' / '女版' / f'EP{ep:02d}', '*.mp4'),
        ('独白_去重单套', base / '剧梦生成视频片段' / '女版' / '独白' / f'EP{ep:02d}', '*.mp3')]:
        folder = ensure_folder(episode_bin, label)
        assert pool.SetCurrentFolder(folder), 'Set current bin failed'
        paths = sorted(source_dir.glob(extension))
        assert paths, str(source_dir)
        missing = [str(p) for p in paths if str(p) not in existing]
        if missing:
            imported = pool.ImportMedia(missing)
            assert imported and len(imported) == len(missing), f'Partial import EP{ep} {label}'
            for clip in imported:
                existing[clip.GetClipProperty('File Path')] = clip
        for path in paths:
            clip = existing[str(path)]
            props = clip.GetClipProperty()
            episode['media'].append({'path': str(path), 'id': clip.GetUniqueId(), 'properties': props})
    result['episodes'].append(episode)
assert pool.SetCurrentFolder(top)
assert pm.SaveProject(), 'Post-import save failed'
(out / 'Resolve_素材导入回读.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'backup': str(backup), 'imported_or_reused': {e['episode']: len(e['media']) for e in result['episodes']}}, ensure_ascii=False))
