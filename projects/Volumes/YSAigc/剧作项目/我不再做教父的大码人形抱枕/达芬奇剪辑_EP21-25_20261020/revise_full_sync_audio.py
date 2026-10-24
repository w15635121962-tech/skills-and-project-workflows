#!/usr/bin/env python3
"""Add missing source-synchronous MP4 audio to A3 without changing V1/A1/A2.

This revises a local edit plan only. It never connects to Resolve, alters media,
or edits subtitle files. Original source audio is a mix, not an isolated stem.
"""
from pathlib import Path
from collections import Counter
import argparse
import copy
import datetime
import hashlib
import json
import os
import shutil
import tempfile


HERE = Path(__file__).resolve().parent


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def record_end(item):
    return (item['record_frame'] + item['source_end_frame_exclusive']
            - item['source_start_frame'])


def source_key(item, base):
    path = Path(item['source_path'])
    if not path.is_absolute():
        path = base / path
    return str(path.resolve())


def overlap(a, b):
    lo = max(a['record_frame'], b['record_frame'])
    hi = min(record_end(a), record_end(b))
    return (lo, hi) if hi > lo else None


def same_mapping(a, v, base):
    return (source_key(a, base) == source_key(v, base)
            and a['source_start_frame'] - a['record_frame']
            == v['source_start_frame'] - v['record_frame'])


def union(intervals):
    out = []
    for lo, hi in sorted(intervals):
        if out and lo <= out[-1][1]:
            out[-1][1] = max(out[-1][1], hi)
        else:
            out.append([lo, hi])
    return out


def covered_ranges(v, audio, base):
    return union([ix for a in audio if same_mapping(a, v, base)
                  and (ix := overlap(a, v))])


def counts(values):
    return dict(sorted(Counter(values).items()))


def atomic_write(path, data):
    fd, tmp = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', nargs='?', default=str(HERE / '剪辑执行计划.json'))
    parser.add_argument('--report', default=str(HERE / '同期声全覆盖计划核验.json'))
    args = parser.parse_args()
    plan_path = Path(args.plan).resolve()
    report_path = Path(args.report).resolve()
    before_bytes = plan_path.read_bytes()
    before = json.loads(before_bytes)
    updated = copy.deepcopy(before)
    base = plan_path.parent.parent
    additions_by_ep = {}

    for ep in updated['episodes']:
        if ep.get('fps') != 24:
            raise ValueError(f'EP{ep["episode"]}: expected 24fps plan.')
        existing = ep['audio'][:]
        added = []
        for vi, v in enumerate(ep['video']):
            if Path(v['source_path']).suffix.lower() != '.mp4':
                continue
            if not Path(source_key(v, base)).is_file():
                raise FileNotFoundError(v['source_path'])
            start, stop = v['record_frame'], record_end(v)
            coverage = covered_ranges(v, existing + added, base)
            cuts = {start, stop}
            for lo, hi in coverage:
                cuts.update((lo, hi))
            # Split precisely where selected dialogue/VO starts or stops.
            for a in existing:
                if a.get('track') in (1, 2) and (ix := overlap(a, v)):
                    cuts.update(ix)
            points = sorted(cuts)
            for lo, hi in zip(points, points[1:]):
                if any(c <= lo and d >= hi for c, d in coverage):
                    continue
                speech_cover = any(a.get('track') in (1, 2)
                                   and a['record_frame'] <= lo
                                   and record_end(a) >= hi for a in existing)
                gain = -12 if speech_cover else -3
                item = {
                    'source_path': v['source_path'],
                    'source_start_frame': v['source_start_frame'] + lo - start,
                    'source_end_frame_exclusive': v['source_start_frame'] + hi - start,
                    'record_frame': lo,
                    'track': 3,
                    'subtitle': False,
                    'tag': '同期底声｜' + v.get('tag', f'video_{vi}'),
                    'gain_db': gain,
                }
                # Adjacent fragments of the same clip/mapping/gain may merge.
                if (added and added[-1]['source_path'] == item['source_path']
                        and added[-1]['gain_db'] == gain
                        and added[-1]['tag'] == item['tag']
                        and record_end(added[-1]) == lo
                        and added[-1]['source_end_frame_exclusive'] == item['source_start_frame']):
                    added[-1]['source_end_frame_exclusive'] = item['source_end_frame_exclusive']
                else:
                    added.append(item)
        ep['audio'].extend(added)
        additions_by_ep[ep['episode']] = added

    # Assert that no pre-existing row, timeline length, metadata, or picture changed.
    stripped = copy.deepcopy(updated)
    for old_ep, new_ep in zip(before['episodes'], stripped['episodes']):
        new_ep['audio'] = new_ep['audio'][:len(old_ep['audio'])]
    if stripped != before:
        raise AssertionError('Modification outside appended A3 audio detected.')

    checks = []
    for ep in updated['episodes']:
        all_audio = ep['audio']
        # A3 itself must be cleanly edited, with no overlap of any added rows.
        a3 = sorted([a for a in all_audio if a.get('track') == 3],
                    key=lambda a: a['record_frame'])
        for a, b in zip(a3, a3[1:]):
            if record_end(a) > b['record_frame']:
                raise AssertionError(f'EP{ep["episode"]}: A3 overlap.')
        clip_checks = []
        for vi, v in enumerate(ep['video']):
            if Path(v['source_path']).suffix.lower() != '.mp4':
                continue
            covered = covered_ranges(v, all_audio, base)
            want = [[v['record_frame'], record_end(v)]]
            if covered != want:
                raise AssertionError(f'EP{ep["episode"]} V{vi}: incomplete sync coverage {covered}.')
            matching = [a for a in all_audio if same_mapping(a, v, base) and overlap(a, v)]
            # Not only covered: matching source audio must never be doubled.
            total_frames = sum(ix[1] - ix[0] for a in matching if (ix := overlap(a, v)))
            if total_frames != record_end(v) - v['record_frame']:
                raise AssertionError(f'EP{ep["episode"]} V{vi}: duplicate sync audio.')
            clip_checks.append({
                'video_index': vi,
                'source_path': v['source_path'],
                'source_start_frame': v['source_start_frame'],
                'source_end_frame_exclusive': v['source_end_frame_exclusive'],
                'record_frame': v['record_frame'],
                'record_end_frame_exclusive': record_end(v),
                'synchronous_audio_coverage_frames': total_frames,
                'coverage_percent': 100,
                'covering_tracks': sorted(set(a.get('track') for a in matching)),
                'tag': v.get('tag'),
            })
        added = additions_by_ep[ep['episode']]
        added_frames = sum(record_end(a) - a['record_frame'] for a in added)
        checks.append({
            'episode': ep['episode'], 'fps': ep['fps'],
            'duration_frames_unchanged': ep['duration_frames'],
            'mp4_video_clip_count': len(clip_checks),
            'all_mp4_clips_have_100_percent_matching_original_audio': True,
            'new_A3_clips': len(added),
            'new_A3_duration_frames': added_frames,
            'new_A3_duration_seconds': round(added_frames / 24, 6),
            'new_A3_clip_count_by_gain_db': counts(a['gain_db'] for a in added),
            'new_A3_frames_by_gain_db': {
                str(g): sum(record_end(a) - a['record_frame'] for a in added if a['gain_db'] == g)
                for g in sorted(set(a['gain_db'] for a in added))
            },
            'new_A3_audio': added,
            'clip_coverage': clip_checks,
        })

    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    stamp = now.strftime('%Y%m%d_%H%M%S_%f')
    backup = plan_path.with_name(plan_path.stem + f'.同期声补齐前_{stamp}.json')
    shutil.copy2(plan_path, backup)
    if backup.read_bytes() != before_bytes:
        raise AssertionError('Backup differs from input plan.')
    # Refuse to overwrite a plan that another task changed while this script ran.
    if plan_path.read_bytes() != before_bytes:
        raise RuntimeError('Plan changed concurrently; backup kept and update cancelled.')
    after_bytes = (json.dumps(updated, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    atomic_write(plan_path, after_bytes)
    if plan_path.read_bytes() != after_bytes:
        raise AssertionError('Plan readback differs.')
    report = {
        'created_at': now.isoformat(),
        'scope': 'Local edit-plan modification and readback only; no Resolve operation or listening acceptance.',
        'plan_path': str(plan_path), 'backup_path': str(backup),
        'before_sha256': sha256(before_bytes), 'after_sha256': sha256(after_bytes),
        'status': 'all_mp4_picture_source_audio_covered_100_percent_in_plan',
        'existing_video_A1_A2_and_timing_unchanged': True,
        'existing_all_fields_unchanged_except_appended_A3_items': True,
        'subtitle_files_edited': False,
        'still_images_without_audio_not_fabricated': True,
        'A3_gain_policy_db': {'under_A1_dialogue_or_A2_voiceover': -12, 'pure_picture_no_A1_A2': -3},
        'notes': [
            'A3 supplements only missing same-path/same-source-time intervals; existing synchronized A1 audio is not duplicated.',
            'Different-source A1 dialogue over flashback/listener pictures remains untouched; the current picture source sound is added quietly underneath.',
            'Source original sound is an existing mixed track, not an isolated ambience stem. Gain adjustments are plan values only until Resolve applies them.',
            'No subjective audio balance, lip-sync, playback, Resolve save, or final timeline verification is claimed.',
        ],
        'episodes': checks,
    }
    atomic_write(report_path, (json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    print(json.dumps({
        'status': report['status'], 'backup_path': str(backup),
        'after_sha256': report['after_sha256'],
        'episodes': [{k: e[k] for k in ('episode', 'mp4_video_clip_count', 'new_A3_clips', 'new_A3_duration_seconds', 'new_A3_clip_count_by_gain_db')}
                     for e in checks],
        'report_path': str(report_path),
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
