"""Verify source bounds/linking, native SRT and persistence. No playback claim."""
import argparse
import datetime
import hashlib
import json
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
from native_common import BASE, PROJECT, EPISODES, assert_clip, connect, load_plan, timelines
from native_common import read as read_json, write as write_json, inventory as timeline_inventory
OUTPUT_DIR=BASE
from insert_srt import parse_srt


def style_payload_hash(path):
    with zipfile.ZipFile(path) as archive:
        name = next(n for n in archive.namelist() if n.startswith('SeqContainer/') and n.endswith('.xml'))
        sequence = ET.fromstring(archive.read(name))
        track = sequence.find('.//SubtitleTrackVec/Element/Sm2TiTrack')
        if track is None:
            return None
        value = track.findtext('FieldsBlob')
        return hashlib.sha256(value.encode('utf-8')).hexdigest() if value else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', required=True)
    parser.add_argument('--reopen', action='store_true')
    parser.add_argument('--execute', action='store_true', help='Required for save/export/reopen; default validates the offline plan only')
    args = parser.parse_args()
    plan = load_plan(args.plan)
    if not args.execute:
        print('Offline plan validated. No Resolve connection/save/export/reopen; add --execute for the authorized verification stage.')
        return
    journal = read_json(OUTPUT_DIR / 'Resolve_组装实读.json')
    baseline = read_json(OUTPUT_DIR / '剪辑前_项目与时间线实读.json')
    own = {x['episode']: x for x in journal['episodes']}
    resolve, manager, project, pool = connect()
    report = {'checked_at': datetime.datetime.now().isoformat(), 'project': PROJECT,
              'saved_and_reopened': False, 'episodes': [],
              'verification_scope': '官方API原生片段、同源同期声链接、原速边界、SRT正文和时码、保存回读。此报告不代表完整正常速度实听或画面艺术验收。'}
    assert manager.SaveProject()
    count = project.GetTimelineCount()
    before_style = {}
    export = OUTPUT_DIR / '原生时间线'
    export.mkdir(parents=True, exist_ok=True)
    by_id = {x.GetUniqueId(): x for x in timelines(project)}
    for ep in plan['episodes']:
        timeline = by_id[own[ep['episode']]['id']]
        path = export / ('EP%d_保存前.drt' % ep['episode'])
        assert timeline.Export(str(path), resolve.EXPORT_DRT)
        before_style[ep['episode']] = style_payload_hash(path)
    if args.reopen:
        assert manager.CloseProject(project)
        project = manager.LoadProject(PROJECT)
        assert project and project.GetTimelineCount() == count
        report['saved_and_reopened'] = True
    by_id = {x.GetUniqueId(): x for x in timelines(project)}
    original_ids = {x['id'] for x in baseline['timelines']}
    old_now = [x for x in timeline_inventory(project) if x['id'] in original_ids]
    assert old_now == baseline['timelines'], 'An existing user timeline changed'
    report['original_timelines_preserved'] = len(original_ids)
    for ep in plan['episodes']:
        row = own[ep['episode']]
        timeline = by_id[row['id']]
        assert timeline.GetName() == ep['timeline_name'] and project.SetCurrentTimeline(timeline)
        assert timeline.GetStartFrame() == 0 and timeline.GetEndFrame() == ep['duration_frames']
        assert float(timeline.GetSetting('timelineFrameRate')) == 24
        assert int(timeline.GetSetting('timelineResolutionWidth')) == 1080
        assert int(timeline.GetSetting('timelineResolutionHeight')) == 1920
        video = sorted(timeline.GetItemListInTrack('video', 1) or [], key=lambda x: x.GetStart())
        audio = sorted(timeline.GetItemListInTrack('audio', 1) or [], key=lambda x: x.GetStart())
        narration = sorted(timeline.GetItemListInTrack('audio', 2) or [], key=lambda x: x.GetStart())
        assert len(video) == len(audio) == len(ep['video'])
        assert len(narration) == len(ep['narration'])
        av = []
        for picture, sound, clip in zip(video, audio, ep['video']):
            assert_clip(picture, clip)
            assert_clip(sound, clip)
            assert picture.GetSourceEndFrame() == sound.GetSourceEndFrame()
            assert sound.GetUniqueId() in [x.GetUniqueId() for x in picture.GetLinkedItems() or []]
            assert picture.GetMediaPoolItem().GetClipProperty('Online Status') == 'Online'
            assert abs(sound.GetProperties()['AudioVolume'] - clip['gain_db']) < 0.01
            av.append({'video_id': picture.GetUniqueId(), 'sync_id': sound.GetUniqueId(),
                       'start': picture.GetStart(), 'end': picture.GetEnd(),
                       'source_start': picture.GetSourceStartFrame(), 'source_end': picture.GetSourceEndFrame(),
                       'same_source_and_boundaries': True, 'linked': True, 'enabled': True})
        for item, clip in zip(narration, ep['narration']):
            assert_clip(item, clip)
            assert item.GetMediaPoolItem().GetClipProperty('Online Status') == 'Online'
            assert abs(item.GetProperties()['AudioVolume'] - clip['gain_db']) < 0.01
        assert all(timeline.GetIsTrackEnabled(k, n) for k, n in [('video', 1), ('audio', 1), ('audio', 2)])
        result = {'episode': ep['episode'], 'timeline': timeline.GetName(), 'id': timeline.GetUniqueId(),
                  'duration_frames': timeline.GetEndFrame(), 'seconds': timeline.GetEndFrame() / 24,
                  'video_count': len(video), 'linked_sync_count': len(audio), 'narration_count': len(narration),
                  'same_source_linked_sync_audio': True, 'all_clips_at_original_speed': True,
                  'no_video_gaps': True, 'media_online': True, 'av_checks': av}
        if ep.get('subtitle_srt'):
            assert timeline.GetTrackCount('subtitle') == 1
            assert timeline.GetTrackName('subtitle', 1) == str(ep['episode'])
            assert timeline.GetIsTrackEnabled('subtitle', 1)
            subtitles = [(int(x.GetStart()), int(x.GetEnd()), x.GetName().replace('\u2028', '\n').replace('\r\n', '\n').strip())
                         for x in timeline.GetItemListInTrack('subtitle', 1) or []]
            expected = parse_srt(ep['subtitle_srt'])
            assert subtitles == [tuple(x) for x in expected]
            result.update(subtitle_count=len(subtitles), subtitle_track_name=str(ep['episode']),
                          srt_text_and_frame_times_exact=True,
                          max_explicit_lines=max(len(x[2].splitlines()) for x in subtitles))
        drt = export / ('EP%d_保存后回读.drt' % ep['episode'])
        assert timeline.Export(str(drt), resolve.EXPORT_DRT)
        after_hash = style_payload_hash(drt)
        assert after_hash == before_style[ep['episode']], 'Subtitle track style payload changed on reopen'
        result.update(drt=str(drt), subtitle_track_style_payload_hash=after_hash,
                      subtitle_track_style_payload_persisted=bool(after_hash),
                      hash_proves_persistence_not_named_preset_identity=True)
        report['episodes'].append(result)
    first = by_id[own[min(EPISODES)]['id']]
    assert project.SetCurrentTimeline(first) and first.SetCurrentTimecode('00:00:00:00')
    assert manager.SaveProject()
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = BASE / ('大码枕头_女版07-09_12-15_原速剪辑_含字幕_%s.drp' % stamp)
    assert not backup.exists() and manager.ExportProject(PROJECT, str(backup)) and backup.stat().st_size > 0
    report.update(project_export=str(backup), project_export_bytes=backup.stat().st_size)
    write_json(OUTPUT_DIR / 'Resolve_保存重开核验.json', report)
    print(json.dumps({key: value for key, value in report.items() if key != 'episodes'}, ensure_ascii=False), flush=True)
    print(json.dumps([dict(x, av_checks='see report') for x in report['episodes']], ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
