#!/usr/bin/env python3
"""Independently read live Resolve items; never change project/UI/timeline state."""
from pathlib import Path
from collections import Counter
import datetime
import hashlib
import json
import re
import sys
import traceback

HERE = Path(__file__).resolve().parent
PLAN_PATH = HERE / '剪辑执行计划.json'
REPORT_PATH = HERE / 'Resolve_同期声实际核验.json'
sys.path.insert(0, '/Users/zc/.codex/skills/davinci-resolve/scripts')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def intersect(a, b):
    lo, hi = max(a['record_frame'], b['record_frame']), min(a['record_end_frame'], b['record_end_frame'])
    return (lo, hi) if hi > lo else None


def merged(parts):
    result = []
    for lo, hi in sorted(parts):
        if result and lo <= result[-1][1]:
            result[-1][1] = max(result[-1][1], hi)
        else:
            result.append([lo, hi])
    return result


def main():
    started = datetime.datetime.now().astimezone().isoformat()
    plan_bytes = PLAN_PATH.read_bytes()
    plan = json.loads(plan_bytes)
    levels_path = HERE / '音量分析.json'
    levels = json.loads(levels_path.read_text(encoding='utf-8')) if levels_path.exists() else []
    inventory = json.loads((HERE / '素材盘点.json').read_text(encoding='utf-8'))
    source_frames = {str(Path(x['path']).resolve()): (x.get('video_streams') or [{}])[0].get('nb_frames')
                     for x in inventory['files']}
    errors, warnings, snapshots = [], [], []
    report = {'started_at': started, 'scope': 'Independent live Resolve read-only API query; no setters, imports, saves or UI changes.',
              'plan_path': str(PLAN_PATH), 'plan_sha256': digest(plan_bytes),
              'source_end_convention': 'GetEnd is exclusive. GetSourceEndFrame is exclusive for trimmed spans but reports the final valid frame index at full-source tail; normalize only the exact one-frame tail cap against ffprobe nb_frames and record duration, retaining the raw getter value.',
              'errors': errors, 'warnings': warnings, 'episodes': snapshots,
              'limitations': ['This confirms native source/time mapping and enabled/volume properties; it is not playback or subjective listening acceptance.',
                              'No claim that generated source lip-sync itself is correct, or that original mixed sound is an isolated ambience stem.',
                              'Native linked-clip membership is not exposed by the queried getters; mapping coverage is checked instead.']}

    def problem(bucket, code, **fields):
        bucket.append({'code': code, **fields})

    sequence_specs = []
    for ep in plan['episodes']:
        for v in ep['video']:
            path = Path(v['source_path'])
            m = re.search(r'\[(\d+)-(\d+)\]', path.name)
            if m:
                sequence_specs.append((str(path.parent.resolve()), path.name[:m.start()], path.name[m.end():],
                                       int(m[1]), int(m[2]), str(path.resolve())))

    def identity(path):
        if not path:
            return None
        p = Path(path).resolve()
        for folder, prefix, suffix, lo, hi, canonical in sequence_specs:
            if str(p.parent) != folder:
                continue
            if str(p) == canonical:
                return canonical
            m = re.fullmatch(re.escape(prefix) + r'(\d+)' + re.escape(suffix), p.name)
            if m and lo <= int(m[1]) <= hi:
                return canonical
        return str(p)

    def item_key(item):
        return (item['track'], identity(item['source_path']), item['source_start_frame'],
                item['source_end_frame_exclusive'], item['record_frame'], item['record_end_frame'])

    def expected_row(item):
        return dict(item, track=item.get('track', 1), record_end_frame=item['record_frame']
                    + item['source_end_frame_exclusive'] - item['source_start_frame'])

    def level_key(eno, a):
        return (eno, identity(a['source_path']), a['source_start_frame'], a['source_end_frame_exclusive'],
                a['record_frame'], a.get('track', 1))

    level_map = {level_key(a['episode'], a): a for a in levels}

    def save():
        report['finished_at'] = datetime.datetime.now().astimezone().isoformat()
        report['plan_unchanged_during_verification'] = PLAN_PATH.read_bytes() == plan_bytes
        if not report['plan_unchanged_during_verification']:
            problem(errors, 'plan_changed_during_query')
        report['status'] = 'live_native_readback_pass' if not errors and not warnings else 'live_native_errors_found' if errors else 'live_native_readback_has_unknowns'
        report['summary'] = {'timelines_queried': len(snapshots), 'errors': len(errors), 'warnings': len(warnings),
                             'MP4_picture_clips': sum(len(e.get('MP4_sync_coverage', [])) for e in snapshots),
                             'A3_clips': sum(len([a for a in e.get('audio', []) if a['track'] == 3]) for e in snapshots)}
        REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        lines = ['# Resolve 同期声实际核验', '', f'结果：{report["status"]}', '',
                 '本次直接重连并读取实际工程，没有用组装日志替代。没有修改工程、切换时间线或保存。', '',
                 '| 集数 | V1段数 | 原片画面段 | A1/A2/A3段数 | 同源同期声100%覆盖 |', '|---|---:|---:|---|---|']
        for ep in snapshots:
            aa = Counter(a['track'] for a in ep.get('audio', []))
            lines.append(f'| EP{ep["episode"]} | {len(ep.get("video", []))} | {len(ep.get("MP4_sync_coverage", []))} | {aa[1]}/{aa[2]}/{aa[3]} | {all(x["coverage_percent"] == 100 and x["duplicate_matching_frames"] == 0 for x in ep.get("MP4_sync_coverage", []))} |')
        lines += ['', '## 问题与未知项', '']
        lines += ['- ' + json.dumps(x, ensure_ascii=False) for x in errors + warnings] or ['- 无。']
        lines += ['', '## 核验边界', ''] + ['- ' + x for x in report['limitations']]
        REPORT_PATH.with_suffix('.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')

    try:
        print('connect_start', flush=True)
        from resolve_bootstrap import get_resolve
        resolve = get_resolve()
        project = resolve.GetProjectManager().GetCurrentProject()
        if not project:
            raise RuntimeError('No current project.')
        report['actual_project'] = project.GetName()
        if report['actual_project'] != plan['project']:
            raise RuntimeError(f'Wrong current project: {report["actual_project"]}')
        print('project_connected ' + report['actual_project'], flush=True)
        timelines = {}
        for ti in range(1, project.GetTimelineCount() + 1):
            timeline = project.GetTimelineByIndex(ti)
            timelines.setdefault(timeline.GetName(), []).append(timeline)
        for ep in plan['episodes']:
            eno = ep['episode']
            name = ep.get('timeline_name', f'大码_女版_EP{eno}_剧情剪辑_v1')
            candidates = timelines.get(name, [])
            if len(candidates) != 1:
                problem(errors, 'missing_or_duplicate_timeline', episode=eno, timeline=name, count=len(candidates))
                continue
            timeline = candidates[0]
            settings = timeline.GetSettings()
            snap = {'episode': eno, 'timeline': name, 'timeline_id': timeline.GetUniqueId(),
                    'start_frame': timeline.GetStartFrame(), 'end_frame': timeline.GetEndFrame(),
                    'settings': settings, 'tracks': [], 'video': [], 'audio': [], 'MP4_sync_coverage': [],
                    'SDK_source_tail_cap_observations': []}
            snapshots.append(snap)
            if float(settings.get('timelineFrameRate', 0)) != 24 or int(settings.get('timelineResolutionWidth', 0)) != 1080 or int(settings.get('timelineResolutionHeight', 0)) != 1920:
                problem(errors, 'timeline_settings_mismatch', episode=eno, settings=settings)
            if snap['start_frame'] != 0 or snap['end_frame'] != ep['duration_frames']:
                problem(errors, 'timeline_bounds_mismatch', episode=eno, actual_start=snap['start_frame'], actual_end=snap['end_frame'], expected_end=ep['duration_frames'])
            for kind in ('video', 'audio'):
                for track in range(1, timeline.GetTrackCount(kind) + 1):
                    track_enabled = timeline.GetIsTrackEnabled(kind, track)
                    current = project.GetCurrentTimeline()
                    current_name = current.GetName() if current else None
                    items = timeline.GetItemListInTrack(kind, track) or []
                    snap['tracks'].append({'kind': kind, 'track': track, 'name': timeline.GetTrackName(kind, track),
                                           'enabled': track_enabled, 'item_count': len(items),
                                           'current_timeline_during_query': current_name})
                    if items and track_enabled is False:
                        if current_name == name:
                            problem(errors, 'disabled_current_timeline_track', episode=eno, kind=kind, track=track)
                        else:
                            problem(warnings, 'noncurrent_track_enabled_false_needs_current_query', episode=eno,
                                    kind=kind, track=track, current_timeline=current_name)
                    elif items and track_enabled is not True:
                        problem(warnings, 'track_enabled_unknown', episode=eno, kind=kind, track=track, value=track_enabled)
                    for item in items:
                        media = item.GetMediaPoolItem()
                        path = media.GetClipProperty('File Path') if media else None
                        row = {'kind': kind, 'track': track, 'source_path': path,
                               'source_start_frame': item.GetSourceStartFrame(),
                               'source_end_frame_exclusive': item.GetSourceEndFrame(),
                               'record_frame': item.GetStart(), 'record_end_frame': item.GetEnd(),
                               'clip_enabled': item.GetClipEnabled(), 'track_enabled': track_enabled,
                               'track_enable_query_on_current_timeline': current_name == name,
                               'properties': item.GetProperties(), 'name': item.GetName()}
                        source_count = source_frames.get(identity(path))
                        inferred_end = row['source_start_frame'] + row['record_end_frame'] - row['record_frame']
                        if (source_count is not None and row['source_end_frame_exclusive'] == source_count - 1
                                and inferred_end == source_count):
                            row['source_end_frame_reported_raw'] = row['source_end_frame_exclusive']
                            row['source_end_frame_exclusive'] = source_count
                            snap['SDK_source_tail_cap_observations'].append({
                                'kind': kind, 'track': track, 'source_path': path,
                                'record_frame': row['record_frame'], 'raw_source_end': source_count - 1,
                                'ffprobe_source_frame_count': source_count,
                                'normalized_exclusive_source_end': source_count,
                                'evidence': 'Record duration and raw source start span the complete remaining source; getter caps at final valid frame index.'})
                        snap[kind].append(row)
                        if row['clip_enabled'] is False:
                            problem(errors, 'disabled_clip', episode=eno, kind=kind, track=track, start=row['record_frame'], source_path=path)
                        elif row['clip_enabled'] is not True:
                            problem(warnings, 'clip_enabled_unknown', episode=eno, kind=kind, track=track, start=row['record_frame'], value=row['clip_enabled'])
                        if not path:
                            problem(errors, 'missing_source_path', episode=eno, kind=kind, track=track, start=row['record_frame'])
                        if row['record_end_frame'] - row['record_frame'] != row['source_end_frame_exclusive'] - row['source_start_frame']:
                            problem(errors, 'source_record_duration_differs', episode=eno, item=row)
            for kind in ('video', 'audio'):
                want = Counter(item_key(expected_row(x)) for x in ep[kind])
                got = Counter(item_key(x) for x in snap[kind])
                for key, count in (want - got).items():
                    problem(errors, 'planned_item_not_found_exactly', episode=eno, kind=kind, count=count, key=key)
                for key, count in (got - want).items():
                    problem(errors, 'unexpected_or_differing_item', episode=eno, kind=kind, count=count, key=key)
            cursor = 0
            for v in sorted([x for x in snap['video'] if x['track'] == 1], key=lambda x: x['record_frame']):
                if v['record_frame'] != cursor:
                    problem(errors, 'V1_gap_or_overlap', episode=eno, expected_start=cursor, actual_start=v['record_frame'])
                cursor = v['record_end_frame']
                if not v['source_path'] or Path(v['source_path']).suffix.lower() != '.mp4':
                    continue
                candidates_audio = [a for a in snap['audio'] if a['track'] in (1, 3)
                                    and identity(a['source_path']) == identity(v['source_path'])
                                    and a['source_start_frame'] - a['record_frame'] == v['source_start_frame'] - v['record_frame']
                                    and intersect(a, v)]
                parts = [intersect(a, v) for a in candidates_audio]
                merged_parts = merged(parts)
                covered = sum(hi - lo for lo, hi in merged_parts)
                duplicate = sum(hi - lo for lo, hi in parts) - covered
                length = v['record_end_frame'] - v['record_frame']
                row = {'source_path': v['source_path'], 'record_frame': v['record_frame'], 'record_end_frame': v['record_end_frame'],
                       'source_start_frame': v['source_start_frame'], 'source_end_frame_exclusive': v['source_end_frame_exclusive'],
                       'coverage_frames': covered, 'picture_frames': length, 'coverage_percent': covered * 100 / length,
                       'duplicate_matching_frames': duplicate, 'covering_tracks': sorted(set(a['track'] for a in candidates_audio)),
                       'all_covering_clips_and_tracks_enabled': all(a['clip_enabled'] is True and a['track_enabled'] is True for a in candidates_audio)}
                snap['MP4_sync_coverage'].append(row)
                if covered != length or duplicate:
                    problem(errors, 'incomplete_or_duplicate_native_sync_audio', episode=eno, **row)
            if cursor != ep['duration_frames']:
                problem(errors, 'V1_end_mismatch', episode=eno, actual_end=cursor, expected_end=ep['duration_frames'])
            for a in snap['audio']:
                if a['track'] != 3:
                    continue
                exact = [x for x in ep['audio'] if item_key(expected_row(x)) == item_key(a)]
                if len(exact) != 1:
                    continue
                planned = exact[0]
                analysis = level_map.get(level_key(eno, planned))
                expected_gain = analysis['gain_db'] if analysis else planned.get('gain_db')
                props = a['properties'] or {}
                a['expected_gain_db'] = expected_gain
                if props.get('AudioVolumeEnabled') is not True:
                    problem(errors, 'A3_gain_not_enabled', episode=eno, start=a['record_frame'], properties=props)
                if expected_gain is None or props.get('AudioVolume') is None:
                    problem(warnings, 'A3_gain_unavailable', episode=eno, start=a['record_frame'], expected=expected_gain, actual=props.get('AudioVolume'))
                elif abs(float(props['AudioVolume']) - float(expected_gain)) > 0.05:
                    problem(errors, 'A3_gain_mismatch', episode=eno, start=a['record_frame'], expected=expected_gain, actual=props['AudioVolume'])
            print(json.dumps({'episode': eno, 'video': len(snap['video']), 'audio': len(snap['audio']),
                              'MP4_sync_coverage': len(snap['MP4_sync_coverage']), 'errors_so_far': len(errors)}, ensure_ascii=False), flush=True)
        save()
        print(json.dumps({'status': report['status'], 'summary': report['summary'], 'report_path': str(REPORT_PATH)}, ensure_ascii=False), flush=True)
        return 1 if errors else 0
    except Exception as exc:
        problem(errors, 'query_exception', error=str(exc), traceback=traceback.format_exc())
        save()
        print(json.dumps({'status': report['status'], 'error': str(exc), 'report_path': str(REPORT_PATH)}, ensure_ascii=False), flush=True)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
