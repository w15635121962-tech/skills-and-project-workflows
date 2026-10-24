"""Add the subtitle track, import/verify SRT, then leave preset application for native UI.

The generic official AppendToTimeline(MediaPoolItem) SRT path was verified in this
installed Resolve 21.1; there is no invented dedicated subtitle import API.
"""
import argparse
import json
from native_common import (BASE, TASK_FOLDER, child_folder, connect, load_plan,
                           read_json, sha256, timelines, write_json)
from subtitle_tools import parse_srt


def clean(text):
    return text.replace('\u2028', '\n').replace('\r\n', '\n').strip()


def native_cues(timeline):
    return [(int(x.GetStart()), int(x.GetEnd()), clean(x.GetName()))
            for x in timeline.GetItemListInTrack('subtitle', 1) or []]


def av_snapshot(timeline):
    return {kind: [[(x.GetUniqueId(), x.GetStart(), x.GetEnd(), x.GetSourceStartFrame(),
                     x.GetSourceEndFrame(), x.GetMediaPoolItem().GetClipProperty('File Path'), x.GetClipEnabled())
                    for x in timeline.GetItemListInTrack(kind, i) or []]
                   for i in range(1, timeline.GetTrackCount(kind) + 1)] for kind in ['video', 'audio']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', required=True)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    plan = load_plan(args.plan)
    journal = read_json(BASE / 'Resolve_组装实读.json')
    expected = {}
    for ep in plan['episodes']:
        cues = parse_srt(ep['subtitle_srt'])
        assert cues and all(0 <= a < b <= ep['duration_frames'] for a, b, _ in cues)
        expected[ep['episode']] = cues
    if not args.execute:
        print('Offline SRT validation passed; no Resolve mutation.')
        return
    resolve, manager, project, pool = connect()
    live = {t.GetUniqueId(): t for t in timelines(project)}
    own = {x['episode']: x for x in journal['episodes']}
    task = child_folder(pool, pool.GetRootFolder(), TASK_FOLDER)
    subfolder = child_folder(pool, task, 'SRT_男版16-19')
    report = []
    for ep in plan['episodes']:
        row = own[ep['episode']]
        timeline = live[row['id']]
        assert timeline.GetName() == ep['timeline_name'] and project.SetCurrentTimeline(timeline)
        assert timeline.GetStartFrame() == 0 and float(timeline.GetSetting('timelineFrameRate')) == 24
        assert timeline.GetEndFrame() == ep['duration_frames']
        before = av_snapshot(timeline)
        if timeline.GetTrackCount('subtitle') == 0:
            assert timeline.AddTrack('subtitle'), 'Add subtitle track before importing SRT'
        assert timeline.GetTrackCount('subtitle') == 1
        old = native_cues(timeline)
        if old:
            assert old == expected[ep['episode']], 'Existing conflicting subtitles; do not duplicate/overwrite'
            action = 'reused_matching_native_subtitles'
        else:
            destination = child_folder(pool, subfolder, str(ep['episode']))
            assert pool.SetCurrentFolder(destination)
            existing = {x.GetClipProperty('File Path'): x for x in destination.GetClipList() or []}
            path = ep['subtitle_srt']
            if path in existing:
                item = existing[path]
            else:
                imported = pool.ImportMedia([path])
                assert imported and len(imported) == 1
                item = imported[0]
            assert timeline.SetCurrentTimecode('00:00:00:00')
            made = pool.AppendToTimeline([item])
            assert made and native_cues(timeline) == expected[ep['episode']], 'SRT times/text did not land exactly'
            action = 'inserted_and_read_back_native_srt'
        assert timeline.SetTrackName('subtitle', 1, str(ep['episode']))
        assert timeline.SetTrackEnable('subtitle', 1, True)
        assert timeline.GetIsTrackEnabled('subtitle', 1)
        assert before == av_snapshot(timeline), 'SRT insertion changed picture/audio'
        assert manager.SaveProject()
        report.append({'episode': ep['episode'], 'timeline': timeline.GetName(), 'id': timeline.GetUniqueId(),
                       'srt': ep['subtitle_srt'], 'srt_sha256': sha256(ep['subtitle_srt']),
                       'action': action, 'cue_count': len(expected[ep['episode']]),
                       'track_name': timeline.GetTrackName('subtitle', 1), 'text_and_frames_exact': True,
                       'av_unchanged': True, 'preset_status': 'PENDING_NATIVE_UI_LOAD_AFTER_IMPORT',
                       'preset_required': '九州海外短剧 Preset 字幕 Preset'} )
        write_json(BASE / '字幕/SRT_原生入轨回读.json', report)
        print(json.dumps(report[-1], ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
