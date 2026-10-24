"""Create native, editable male EP09--15 timelines only after narration is complete.

Default is offline validation. --execute is required for any Resolve mutation.
Existing unrelated/manual timelines are never reused, renamed or removed.
An interrupted run can resume only its own journaled timeline IDs and identical plan.
"""
import argparse
import datetime
import json
from pathlib import Path
from native_common import (BASE, PROJECT, TASK_FOLDER, assert_clip, child_folder, clip_info,
                           connect, load_plan, read_json, sha256, timeline_inventory,
                           timelines, walk_media, write_json)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', required=True)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    plan = load_plan(args.plan, require_all=True)
    if not args.execute:
        print('Offline validation passed. No Resolve connection or mutation. Add --execute only when the plan is approved.')
        return
    baseline = read_json(BASE / 'Resolve_操作前实读.json')
    backup = Path(baseline['backup'])
    assert backup.is_file() and backup.stat().st_size == baseline['backup_bytes']
    assert sha256(backup) == baseline['backup_sha256']
    resolve, manager, project, pool = connect()
    journal_path = BASE / 'Resolve_组装实读.json'
    journal = read_json(journal_path) if journal_path.exists() else {
        'project': PROJECT, 'plan': str(Path(args.plan).resolve()), 'plan_sha256': sha256(args.plan),
        'created_at': datetime.datetime.now().isoformat(), 'episodes': []}
    assert journal['plan_sha256'] == sha256(args.plan), 'Do not resume a modified plan'
    owned_ids = {x['id'] for x in journal['episodes']}
    live_before = timeline_inventory(project)
    baseline_ids = {x['id'] for x in baseline['timelines']}
    assert [x for x in live_before if x['id'] in baseline_ids] == baseline['timelines'], 'Existing user edit drift; take a fresh backup before continuing'
    assert all(x['id'] in baseline_ids | owned_ids for x in live_before), 'Unrelated timeline created since backup; refresh backup'
    names = {t.GetName(): t for t in timelines(project)}
    for ep in plan['episodes']:
        if ep['timeline_name'] in names:
            assert names[ep['timeline_name']].GetUniqueId() in owned_ids, 'Refuse to overwrite existing/manual timeline'
    task_folder = child_folder(pool, pool.GetRootFolder(), TASK_FOLDER)
    media = walk_media(pool.GetRootFolder())
    import_log = []
    for ep in plan['episodes']:
        folder = child_folder(pool, task_folder, '男版EP%d' % ep['episode'])
        for kind, label in [('video', '视频与同期声'), ('narration', '男版新音色_原速旁白')]:
            destination = child_folder(pool, folder, label)
            assert pool.SetCurrentFolder(destination)
            paths = sorted({c['path'] for c in ep[kind]})
            needed = [path for path in paths if path not in media]
            for start in range(0, len(needed), 40):
                batch = needed[start:start + 40]
                imported = pool.ImportMedia(batch)
                assert imported and len(imported) == len(batch), 'Source import incomplete'
                for item in imported:
                    path = item.GetClipProperty('File Path')
                    assert path in batch
                    media[path] = item
            for path in paths:
                item = media[path]
                assert item.GetClipProperty('Online Status') == 'Online'
                if kind == 'video':
                    assert float(item.GetClipProperty('FPS')) == 24
                import_log.append({'episode': ep['episode'], 'kind': kind, 'path': path,
                                   'media_pool_id': item.GetUniqueId(), 'properties': item.GetClipProperty()})
    write_json(BASE / 'Resolve_媒体导入实读.json', import_log)
    assert pool.SetCurrentFolder(task_folder)
    assert manager.SaveProject()
    for ep in plan['episodes']:
        timeline = names.get(ep['timeline_name'])
        record = next((x for x in journal['episodes'] if x['episode'] == ep['episode']), None)
        if timeline is None:
            timeline = pool.CreateEmptyTimeline(ep['timeline_name'])
            assert timeline
            record = {'episode': ep['episode'], 'timeline': ep['timeline_name'],
                      'id': timeline.GetUniqueId(), 'status': 'created_not_complete'}
            journal['episodes'].append(record)
            write_json(journal_path, journal)
            assert manager.SaveProject()
        assert record and timeline.GetUniqueId() == record['id']
        assert project.SetCurrentTimeline(timeline)
        if not timeline.GetItemListInTrack('video', 1):
            # Prefer inheriting correct settings. Set custom values only on this new timeline.
            desired = {'timelineFrameRate': '24', 'timelineResolutionWidth': '1080', 'timelineResolutionHeight': '1920'}
            if any(str(timeline.GetSetting(key)) != value for key, value in desired.items()):
                assert timeline.SetSetting('useCustomSettings', '1')
                for key, value in desired.items():
                    if str(timeline.GetSetting(key)) != value:
                        assert timeline.SetSetting(key, value), (key, value)
            assert timeline.SetStartTimecode('00:00:00:00')
        assert float(timeline.GetSetting('timelineFrameRate')) == 24
        assert str(timeline.GetSetting('timelineResolutionWidth')) == '1080'
        assert str(timeline.GetSetting('timelineResolutionHeight')) == '1920'
        assert timeline.GetStartFrame() == 0
        if not any(timeline.GetItemListInTrack('audio', index) for index in range(1, timeline.GetTrackCount('audio') + 1)):
            if any(timeline.GetTrackSubType('audio', index).lower() != 'stereo'
                   for index in range(1, timeline.GetTrackCount('audio') + 1)):
                # Only empty tracks on this newly owned timeline may be replaced.
                for index in range(timeline.GetTrackCount('audio'), 0, -1):
                    assert timeline.DeleteTrack('audio', index)
        while timeline.GetTrackCount('audio') < 2:
            assert timeline.AddTrack('audio', 'stereo')
        assert timeline.GetTrackCount('video') == 1 and timeline.GetTrackCount('audio') == 2
        assert all(timeline.GetTrackSubType('audio', index).lower() == 'stereo' for index in [1, 2])
        assert timeline.SetTrackName('video', 1, '男版%d_剧情画面' % ep['episode'])
        assert timeline.SetTrackName('audio', 1, '同期声_与画面链接')
        assert timeline.SetTrackName('audio', 2, 'Oliver男版新音色_100%旁白')
        for kind, index in [('video', 1), ('audio', 1), ('audio', 2)]:
            assert timeline.SetTrackEnable(kind, index, True)

        def existing(kind, track, expected):
            items = timeline.GetItemListInTrack(kind, track) or []
            mapping = {int(x.GetStart()): x for x in items}
            assert len(mapping) == len(items)
            expected_map = {c['record_frame']: c for c in expected}
            assert set(mapping) <= set(expected_map), 'Unexpected content in task-owned timeline'
            for start, item in mapping.items():
                assert_clip(item, expected_map[start])
            return mapping

        video_existing = existing('video', 1, ep['video'])
        sync_existing = existing('audio', 1, ep['video'])
        vo_existing = existing('audio', 2, ep['narration'])
        record.update(status='assembling', video=[], sync_audio=[], narration=[], limitations=ep.get('limitations', []))

        def add_clip(clip, track, media_type, previous):
            item = previous.get(clip['record_frame'])
            if item is None:
                made = pool.AppendToTimeline([clip_info(clip, media, track, media_type)])
                assert made and len(made) == 1, 'AppendToTimeline failed'
                item = made[0]
            assert_clip(item, clip)
            if media_type == 2:
                assert item.SetProperties({'AudioVolumeEnabled': True, 'AudioVolume': clip['gain_db']})
                assert abs(item.GetProperties()['AudioVolume'] - clip['gain_db']) < 0.01
            return item

        for clip in ep['video']:
            video = add_clip(clip, 1, 1, video_existing)
            audio = add_clip(clip, 1, 2, sync_existing)
            assert video.GetSourceEndFrame() == audio.GetSourceEndFrame()
            assert timeline.SetClipsLinked([video, audio], True)
            assert audio.GetUniqueId() in [x.GetUniqueId() for x in video.GetLinkedItems() or []]
            for key, item in [('video', video), ('sync_audio', audio)]:
                record[key].append(dict(clip, id=item.GetUniqueId(), start=item.GetStart(), end=item.GetEnd(),
                                        source_start=item.GetSourceStartFrame(), source_end=item.GetSourceEndFrame()))
            markers = timeline.GetMarkers() or {}
            if clip['record_frame'] not in markers:
                assert timeline.AddMarker(clip['record_frame'], 'Blue', clip.get('tag', '男版剧情'),
                       '男版源稿；画面与同期声同源同剪并链接，均为原速。', 1)
            write_json(journal_path, journal)
        for clip in ep['narration']:
            item = add_clip(clip, 2, 2, vo_existing)
            record['narration'].append(dict(clip, id=item.GetUniqueId(), start=item.GetStart(), end=item.GetEnd(),
                   source_start=item.GetSourceStartFrame(), source_end=item.GetSourceEndFrame()))
            write_json(journal_path, journal)
        assert timeline.GetEndFrame() == ep['duration_frames']
        assert all(timeline.GetIsTrackEnabled(k, n) for k, n in [('video', 1), ('audio', 1), ('audio', 2)])
        record.update(status='native_av_assembled_subtitles_pending', duration_frames=timeline.GetEndFrame(),
                      fps=24, settings=timeline.GetSetting(), original_speed_all=True,
                      no_video_gaps=True, synchronous_audio_linked=True)
        for index, note in enumerate(ep.get('limitations', []), 1):
            if index not in (timeline.GetMarkers() or {}):
                assert timeline.AddMarker(index, 'Yellow', '源素材说明', str(note), 1)
        assert manager.SaveProject()
        export = BASE / '原生时间线'
        export.mkdir(exist_ok=True)
        record['drt'] = str(export / (timeline.GetName() + '.drt'))
        record['otio'] = str(export / (timeline.GetName() + '.otio'))
        assert timeline.Export(record['drt'], resolve.EXPORT_DRT)
        assert timeline.Export(record['otio'], resolve.EXPORT_OTIO)
        write_json(journal_path, journal)
        print(json.dumps({'episode': ep['episode'], 'timeline': timeline.GetName(),
              'seconds': timeline.GetEndFrame() / 24, 'video': len(record['video']),
              'linked_sync_audio': len(record['sync_audio']), 'narration': len(record['narration'])}, ensure_ascii=False), flush=True)
    after = timeline_inventory(project)
    assert [x for x in after if x['id'] in baseline_ids] == baseline['timelines'], 'An existing timeline changed'
    journal.update(status='seven_native_av_timelines_assembled_subtitles_pending', original_timelines_preserved=len(baseline_ids))
    write_json(journal_path, journal)
    assert manager.SaveProject()


if __name__ == '__main__':
    main()
