"""Import available sources without creating or changing any timeline."""
import argparse
import datetime
from pathlib import Path
from native_common import (BASE, TASK_FOLDER, child_folder, connect, read_json,
                           sha256, timeline_inventory, walk_media, write_json)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    inventory = read_json(Path(__file__).parent / 'media_inventory_native.json')
    progress = read_json(BASE / '制作进度.json')
    candidates = progress.get('candidate_downloads', [])
    # Keep all original audio files; these are the independently compared takes.
    recommended_two = {24, 25, 31, 33}
    rows = []
    for ep in inventory['episodes']:
        rows.extend((ep['episode'], '视频与同期声', x['path']) for x in ep['videos'])
    for index, item in enumerate(progress['items']):
        if not item.get('path'):
            continue
        path = item['path']
        if index in recommended_two:
            choices = [x for x in candidates if x['idx'] == index]
            assert len(choices) == 1
            path = choices[0]['path']
        rows.append((item['episode'], '男版新音色_原速旁白', path))
    assert sum(label == '视频与同期声' for _, label, _ in rows) == 104
    assert all(Path(path).is_file() for _, _, path in rows)
    if not args.execute:
        print({'offline_available_media': len(rows), 'timeline_changes': False})
        return
    baseline = read_json(BASE / 'Resolve_操作前实读.json')
    assert sha256(baseline['backup']) == baseline['backup_sha256']
    resolve, manager, project, pool = connect()
    before = timeline_inventory(project)
    original_folder = pool.GetCurrentFolder()
    folder = child_folder(pool, pool.GetRootFolder(), TASK_FOLDER)
    media = walk_media(pool.GetRootFolder())
    imported = []
    log = []
    try:
        for episode in range(9, 16):
            ep_folder = child_folder(pool, folder, '男版EP%d' % episode)
            for label in ['视频与同期声', '男版新音色_原速旁白']:
                dest = child_folder(pool, ep_folder, label)
                assert pool.SetCurrentFolder(dest)
                paths = [path for ep, kind, path in rows if ep == episode and kind == label]
                needed = [path for path in paths if path not in media]
                for offset in range(0, len(needed), 30):
                    batch = needed[offset:offset + 30]
                    clips = pool.ImportMedia(batch)
                    assert clips and len(clips) == len(batch)
                    for clip in clips:
                        path = clip.GetClipProperty('File Path')
                        assert path in batch
                        media[path] = clip
                        imported.append(path)
                for path in paths:
                    clip = media[path]
                    properties = clip.GetClipProperty()
                    assert properties['Online Status'] == 'Online'
                    if label == '视频与同期声':
                        assert float(properties['FPS']) == 24
                    log.append({'episode': episode, 'kind': label, 'path': path,
                                'media_pool_id': clip.GetUniqueId(), 'properties': properties})
        assert timeline_inventory(project) == before, 'Timeline changed during source import'
        assert manager.SaveProject()
    finally:
        if original_folder:
            assert pool.SetCurrentFolder(original_folder)
    report = {'updated_at': datetime.datetime.now().isoformat(), 'project': project.GetName(),
              'resolve_version': resolve.GetVersionString(), 'timeline_count': len(before),
              'timeline_content_unchanged': True, 'available_media_count': len(rows),
              'newly_imported_count': len(imported), 'sources': log,
              'not_a_timeline_assembly': True, 'remaining_narration': progress['not_generated_or_failed_basenames']}
    write_json(BASE / 'Resolve_现成素材导入实读.json', report)
    print({key: report[key] for key in ['available_media_count', 'newly_imported_count',
          'timeline_count', 'timeline_content_unchanged', 'not_a_timeline_assembly']})


if __name__ == '__main__':
    main()
