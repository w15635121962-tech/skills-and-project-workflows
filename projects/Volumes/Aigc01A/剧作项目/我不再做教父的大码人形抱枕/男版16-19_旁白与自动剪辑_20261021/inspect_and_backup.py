"""Save/export a recoverable project backup; never creates/imports timeline content."""
import datetime
from native_common import BASE, PROJECT, connect, sha256, timeline_inventory, write_json


def main():
    resolve, manager, project, media_pool = connect()
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    timeline = project.GetCurrentTimeline()
    before = timeline_inventory(project)
    report = {'created_at': datetime.datetime.now().isoformat(), 'project': PROJECT,
              'resolve_version': resolve.GetVersionString(),
              'current_timeline': timeline.GetName() if timeline else None,
              'current_timeline_id': timeline.GetUniqueId() if timeline else None,
              'current_timecode': timeline.GetCurrentTimecode() if timeline else None,
              'project_settings': project.GetSetting(), 'timelines': before,
              'backup_scope': '完整DRP工程结构及全部现有时间线；外部媒体保持原路径，不复制源媒体。',
              'no_imports_or_timeline_mutation': True}
    candidates = [x for x in before if any(('男版_EP%d_' % ep) in x['name'] for ep in range(16, 20))]
    report['existing_male_16_19_candidates'] = candidates
    assert manager.SaveProject(), 'Save current work before backup failed'
    backup = BASE / '备份' / ('大码枕头_男版16-19剪辑前_%s.drp' % stamp)
    backup.parent.mkdir(exist_ok=True)
    assert not backup.exists()
    assert manager.ExportProject(PROJECT, str(backup)), 'Full project export failed'
    assert backup.stat().st_size > 0
    assert timeline_inventory(project) == before, 'Backup unexpectedly changed timeline structure'
    report.update(backup=str(backup), backup_bytes=backup.stat().st_size, backup_sha256=sha256(backup))
    snapshot = BASE / '备份' / ('Resolve_操作前实读_%s.json' % stamp)
    write_json(snapshot, report)
    write_json(BASE / 'Resolve_操作前实读.json', report)
    print(__import__('json').dumps({'backup': str(backup), 'bytes': report['backup_bytes'],
          'sha256': report['backup_sha256'], 'timeline_count': len(before),
          'current_timeline': report['current_timeline'],
          'existing_male_16_19_candidates': [x['name'] for x in candidates],
          'timeline_content_unchanged': True}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()

