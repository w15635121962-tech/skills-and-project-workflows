#!/usr/bin/env python3
"""Validate downloaded narration, then create six native Resolve timelines.

Default: validate all six episode groups and print a plan without changing Resolve.
--apply: use a dedicated project and reuse matching bins, media and timelines.
--export-fcpxml DIR: write offline FCPXML files; never import them automatically.
--allow-partial: explicitly permit missing downloads, mark results PARTIAL/未完成.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
import xml.etree.ElementTree as ET


SKILL_SCRIPTS = Path('/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
VERSIONS = ('女版', '性转版')
EXPECTED_GROUPS = {(v, ep) for v in VERSIONS for ep in (1, 2, 3)}


def require(value, message):
    if value is None or value is False:
        raise RuntimeError(message)
    return value


def natural_key(value):
    return [int(part) if part.isdigit() else part for part in re.split(r'(\d+)', str(value))]


def sha256(path):
    result = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def probe(path):
    ffprobe = shutil.which('ffprobe')
    if not ffprobe:
        raise RuntimeError('ffprobe is required to verify downloaded audio.')
    process = subprocess.run(
        [ffprobe, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)],
        check=True, capture_output=True, text=True, encoding='utf-8',
    )
    data = json.loads(process.stdout)
    audio = [item for item in data.get('streams', []) if item.get('codec_type') == 'audio']
    video = [item for item in data.get('streams', []) if item.get('codec_type') == 'video' and not item.get('disposition', {}).get('attached_pic')]
    if len(audio) != 1 or video:
        raise ValueError(f'Expected an audio-only file with one audio stream: {path}')
    stream = audio[0]
    duration = stream.get('duration', data.get('format', {}).get('duration'))
    if duration is None or not math.isfinite(float(duration)) or float(duration) <= 0:
        raise ValueError(f'Audio duration cannot be verified: {path}')
    if stream.get('duration_ts') is not None and stream.get('time_base'):
        exact = int(stream['duration_ts']) * Fraction(stream['time_base'])
    else:
        exact = Fraction(str(duration))
    sample_rate = int(stream.get('sample_rate') or 48000)
    decoded = subprocess.run(
        [ffprobe, '-v', 'error', '-select_streams', 'a:0', '-show_frames',
         '-show_entries', 'frame=nb_samples', '-of', 'json', str(path)],
        check=True, capture_output=True, text=True, encoding='utf-8',
    )
    if decoded.stderr.strip():
        raise ValueError(f'Audio decoder reported errors for {path}: {decoded.stderr.strip()}')
    samples = sum(int(frame.get('nb_samples', 0)) for frame in json.loads(decoded.stdout).get('frames', []))
    if samples <= 0:
        raise ValueError(f'Audio decoder produced no samples: {path}')
    audible = Fraction(samples, sample_rate)
    return {
        'duration_seconds': float(audible),
        'duration_rational': str(audible),
        'container_duration_seconds': float(exact),
        'container_duration_rational': str(exact),
        'decoded_samples': samples,
        'sample_rate': sample_rate,
        'channels': int(stream.get('channels') or 1),
        'codec': stream.get('codec_name'),
    }


def clip_key(row):
    return (row.get('version'), int(row.get('episode', 0)), row.get('name'))


def normalize_whitespace(value):
    return re.sub(r'\s+', ' ', value.strip())


def load_manifest(path, allow_partial=False):
    manifest_bytes = path.read_bytes()
    raw = json.loads(manifest_bytes)
    metadata = dict(raw) if isinstance(raw, dict) else {}
    rows = metadata.get('clips') if isinstance(raw, dict) else raw
    if not isinstance(rows, list) or not rows:
        raise ValueError('Manifest must contain a nonempty clips array.')
    expected_count = int(metadata['expected_clip_count']) if metadata.get('expected_clip_count') is not None else None
    planned = {}
    plan_path = metadata.get('generation_plan')
    if plan_path:
        plan_path = Path(plan_path)
        if not plan_path.is_absolute():
            plan_path = path.parent / plan_path
        plan_bytes = plan_path.resolve(strict=True).read_bytes()
        prepared = json.loads(plan_bytes)
        for group in prepared.get('groups', []):
            key = clip_key(group)
            if key in planned or key[:2] not in EXPECTED_GROUPS or not key[2]:
                raise ValueError(f'Duplicate/invalid group in generation plan: {key}')
            text = group.get('generation_text') or group.get('text')
            if not isinstance(text, str) or not text.strip() or len(text) > 200:
                raise ValueError(f'Generation plan group has invalid >200-character/empty text: {key}')
            planned[key] = group
        if not planned or {key[:2] for key in planned} != EXPECTED_GROUPS:
            raise ValueError('Generation plan must cover all six requested episodes.')
        if int(prepared.get('total_group_count', len(planned))) != len(planned):
            raise ValueError('Generation plan total_group_count does not match its groups.')
        if expected_count is not None and expected_count != len(planned):
            raise ValueError('Manifest expected_clip_count differs from generation plan.')
        expected_count = len(planned)
        metadata['generation_plan_sha256'] = hashlib.sha256(plan_bytes).hexdigest()
    if expected_count is not None:
        if len(rows) > expected_count or (len(rows) != expected_count and not allow_partial):
            raise ValueError(f'Manifest clip count {len(rows)} does not match expected_clip_count {expected_count}. Use --allow-partial only for an explicitly marked incomplete delivery.')
    elif allow_partial:
        raise ValueError('--allow-partial requires expected_clip_count or a generation_plan.')
    groups = defaultdict(list)
    seen = set()
    seen_paths = set()
    for row in rows:
        version = row.get('version')
        episode = int(row.get('episode', 0))
        if (version, episode) not in EXPECTED_GROUPS:
            raise ValueError(f'Unexpected version/episode: {version!r}/{episode}')
        local = row.get('local_path') or row.get('file_path') or row.get('path')
        if not local or not Path(local).is_absolute():
            raise ValueError(f'An absolute local audio path is required: {row}')
        audio = Path(local).resolve(strict=True)
        if not audio.is_file() or audio.stat().st_size == 0:
            raise ValueError(f'Audio file is missing or empty: {audio}')
        if row.get('status', 'downloaded') not in ('downloaded', 'verified', 'complete'):
            raise ValueError(f'Audio is not downloaded: {row.get("name", audio.name)}')
        name = row.get('name') or audio.stem
        key = (version, episode, name)
        if key in seen:
            raise ValueError(f'Duplicate manifest version/episode/name: {key}')
        seen.add(key)
        if str(audio) in seen_paths:
            raise ValueError(f'One physical audio file is assigned to multiple clips: {audio}')
        seen_paths.add(str(audio))
        if name != audio.stem:
            raise ValueError(f'Manifest name differs from downloaded filename: {name} / {audio.name}')
        if planned:
            if key not in planned:
                raise ValueError(f'Manifest clip is not in the authoritative generation plan: {key}')
            expected_text = planned[key].get('generation_text') or planned[key].get('text')
            if not isinstance(row.get('text'), str) or normalize_whitespace(row['text']) != normalize_whitespace(expected_text):
                raise ValueError(f'Downloaded generation text differs from the authoritative plan: {key}')
        digest = sha256(audio)
        if row.get('sha256') and row['sha256'] != digest:
            raise ValueError(f'Downloaded audio SHA256 differs from the manifest: {key}')
        measured = probe(audio)
        if row.get('duration_seconds') is not None:
            recorded_duration = float(row['duration_seconds'])
            if min(abs(recorded_duration - measured['duration_seconds']), abs(recorded_duration - measured['container_duration_seconds'])) > .002:
                raise ValueError(f'Downloaded duration differs from actual decoded/container audio: {key}')
        groups[(version, episode)].append({
            'version': version, 'episode': episode, 'name': name,
            'local_path': str(audio), 'bytes': audio.stat().st_size,
            'sha256': digest, **measured,
            **{field: row[field] for field in ('text', 'model', 'voice_name', 'selected_candidate', 'record_key') if field in row},
        })
    if set(groups) != EXPECTED_GROUPS and not allow_partial:
        missing = sorted(EXPECTED_GROUPS - set(groups))
        raise ValueError(f'All six episode groups must contain downloaded audio. Missing: {missing}')
    missing_keys = sorted(set(planned) - seen, key=lambda key: (VERSIONS.index(key[0]), key[1], natural_key(key[2])))
    if missing_keys and not allow_partial:
        raise ValueError(f'Manifest is missing {len(missing_keys)} planned audio groups.')
    for items in groups.values():
        items.sort(key=lambda item: natural_key(item['name']))
        if len({item['name'] for item in items}) != len(items):
            raise ValueError('Duplicate audio names in one episode.')
    fps = Fraction(str(metadata.get('fps') or '24'))
    if fps <= 0 or fps > 120:
        raise ValueError('Unsupported timeline frame rate.')
    expected_count = expected_count if expected_count is not None else len(rows)
    metadata['coverage'] = {
        'scope_status': 'complete' if len(rows) == expected_count and set(groups) == EXPECTED_GROUPS and not missing_keys else 'partial',
        'expected_clip_count': expected_count,
        'downloaded_clip_count': len(rows),
        'requested_episode_count': 6,
        'episodes_with_audio': len(groups),
        'skipped_empty_episodes': [{'version': v, 'episode': ep} for v, ep in sorted(EXPECTED_GROUPS - set(groups))],
        'missing_planned_clips': [{'version': v, 'episode': ep, 'name': name} for v, ep, name in missing_keys],
    }
    metadata['expected_counts_by_episode'] = {
        f'{v}/{ep}': sum(1 for key in planned if key[:2] == (v, ep))
        for v, ep in EXPECTED_GROUPS
    } if planned else {}
    metadata['manifest_sha256'] = hashlib.sha256(manifest_bytes).hexdigest()
    return metadata, dict(groups), fps


def timeline_name(version, episode):
    return f'大码_{version}_EP{episode:02d}_配音'


def plan(metadata, groups, fps):
    coverage = metadata['coverage']
    partial = coverage['scope_status'] == 'partial'
    project_name = metadata.get('project_name') or '大码_前3集配音'
    if partial:
        project_name += '_PARTIAL_未完成'
    timelines = []
    for version in VERSIONS:
        for episode in (1, 2, 3):
            clips = groups.get((version, episode))
            if not clips:
                continue  # Partial delivery never creates an empty episode timeline.
            expected = metadata['expected_counts_by_episode'].get(f'{version}/{episode}')
            name = timeline_name(version, episode)
            if partial:
                name += f'_PARTIAL_未完成_{len(clips):02d}of{expected:02d}' if expected else f'_PARTIAL_未完成_{len(clips):02d}段'
            timelines.append({
                'version': version, 'episode': episode, 'name': name,
                'clip_count': len(clips), 'expected_clip_count': expected,
                'scope_status': 'partial' if partial else 'complete',
                'duration_seconds': sum(item['duration_seconds'] for item in clips),
                'clips': clips,
            })
    return {
        'project_name': project_name,
        'fps': str(fps),
        'coverage': coverage,
        'manifest_sha256': metadata['manifest_sha256'],
        'generation_plan_sha256': metadata.get('generation_plan_sha256'),
        'timelines': timelines,
    }


def get_resolve():
    sys.path.insert(0, str(SKILL_SCRIPTS))
    from resolve_bootstrap import get_resolve as bundled_get_resolve
    return bundled_get_resolve()


def find_or_create_bin(pool, parent, name):
    matches = [folder for folder in (parent.GetSubFolderList() or []) if folder.GetName() == name]
    if len(matches) > 1:
        raise RuntimeError(f'Multiple bins named {name}; refusing an ambiguous import.')
    return matches[0] if matches else require(pool.AddSubFolder(parent, name), f'Cannot create bin: {name}')


def media_path(item):
    value = item.GetClipProperty('File Path')
    return str(Path(value).resolve()) if value else None


def verify_timeline(timeline, expected):
    items = []
    for track in range(1, int(timeline.GetTrackCount('audio')) + 1):
        track_items = timeline.GetItemListInTrack('audio', track) or []
        if track != 1 and track_items:
            raise RuntimeError(f'Expected all narration on audio track 1: {timeline.GetName()}')
        items.extend(track_items)
    items.sort(key=lambda item: item.GetStart(True))
    actual = [media_path(require(item.GetMediaPoolItem(), 'Timeline item has no source media.')) for item in items]
    target = [clip['local_path'] for clip in expected]
    if actual != target:
        raise RuntimeError(f'Timeline source count/order mismatch in {timeline.GetName()}. Expected {target}; got {actual}. Existing timeline was not changed.')
    for track in range(1, int(timeline.GetTrackCount('video')) + 1):
        if timeline.GetItemListInTrack('video', track):
            raise RuntimeError(f'Unexpected video items in narration timeline: {timeline.GetName()}')
    previous = float(timeline.GetStartFrame())
    placements = []
    timeline_fps = float(timeline.GetSetting('timelineFrameRate'))
    for item, clip in zip(items, expected):
        start, end = float(item.GetStart(True)), float(item.GetEnd(True))
        api_duration = float(item.GetDuration(True))
        if end <= start:
            raise RuntimeError(f'Zero-duration timeline item: {clip["name"]}')
        if abs(api_duration - (end - start)) > 0.001:
            raise RuntimeError(f'Conflicting timeline duration/endpoints: {clip["name"]}')
        candidate_seconds = [clip['duration_seconds'], clip.get('container_duration_seconds', clip['duration_seconds'])]
        duration_error = min(abs(api_duration - seconds * timeline_fps) for seconds in candidate_seconds)
        if duration_error > 1.1:
            raise RuntimeError(f'Timeline duration differs from source audio: {clip["name"]}')
        if abs(start - previous) > 0.001:
            raise RuntimeError(f'Audio gap/overlap before {clip["name"]}')
        previous = end
        source_properties = item.GetMediaPoolItem().GetClipProperty()
        placements.append({
            'name': clip['name'], 'audio_track': 1,
            'start_frame': start, 'end_frame': end,
            'source_fps': source_properties.get('FPS'),
            'source_frames': source_properties.get('Frames'),
            'source_duration_display': source_properties.get('Duration'),
            'expected_duration_seconds': clip['duration_seconds'],
            'container_duration_seconds': clip.get('container_duration_seconds'),
            'duration_error_frames': duration_error,
        })
    return placements


def ensure_partial_marker(timeline, entry, coverage):
    signature = hashlib.sha256(json.dumps(
        [(clip['name'], clip['sha256']) for clip in entry['clips']],
        ensure_ascii=False, separators=(',', ':'),
    ).encode('utf-8')).hexdigest()[:16]
    custom_data = f'dama-partial:v1:{entry["version"]}:{entry["episode"]}:{signature}'
    markers = timeline.GetMarkers() or {}
    if any(marker.get('customData') == custom_data for marker in markers.values()):
        return custom_data
    missing = [item['name'] for item in coverage['missing_planned_clips']
               if item['version'] == entry['version'] and item['episode'] == entry['episode']]
    note = (
        f'PARTIAL / 未完成。此时间线仅包含已下载的 {entry["clip_count"]} 段旁白；'
        f'本集计划 {entry.get("expected_clip_count") or "待核"} 段。'
        f'两版前三集计划共 {coverage["expected_clip_count"]} 段，不能据此宣称全任务完成。'
        f'本集缺少：{", ".join(missing) if missing else "本集已齐，其他集仍缺少"}。'
    )
    require(timeline.AddMarker(0, 'Red', 'PARTIAL 未完成：仅已下载旁白', note, 1, custom_data),
            f'Cannot add prominent partial-delivery marker: {entry["name"]}')
    markers = timeline.GetMarkers() or {}
    if not any(marker.get('customData') == custom_data for marker in markers.values()):
        raise RuntimeError(f'Partial marker verification failed: {entry["name"]}')
    return custom_data


def apply_to_resolve(outline, report_path):
    resolve = get_resolve()
    pm = require(resolve.GetProjectManager(), 'Cannot get Resolve project manager.')
    current = pm.GetCurrentProject()
    project_name = outline['project_name']
    project = current if current and current.GetName() == project_name else None
    created_project = False
    if project is None:
        names = pm.GetProjectListInCurrentFolder() or []
        if project_name in names:
            project = require(pm.LoadProject(project_name), f'Cannot load dedicated project: {project_name}')
        else:
            project = require(pm.CreateProject(project_name), f'Cannot create dedicated project: {project_name}')
            created_project = True
    if created_project:
        require(project.SetSetting('timelineFrameRate', str(float(Fraction(outline['fps'])))), 'Cannot set new project frame rate.')
    actual_fps = Fraction(str(project.GetSetting('timelineFrameRate')))
    if abs(float(actual_fps - Fraction(outline['fps']))) > 0.0001:
        raise RuntimeError(f'Dedicated project frame rate {actual_fps} differs from manifest {outline["fps"]}; settings were not overwritten.')
    pool = require(project.GetMediaPool(), 'Cannot get media pool.')
    root = require(pool.GetRootFolder(), 'Cannot get media pool root bin.')
    prior_folder = pool.GetCurrentFolder()
    previous_report = json.loads(report_path.read_text(encoding='utf-8')) if report_path.exists() else {}
    prior_hashes = {clip['local_path']: clip['sha256'] for tl in previous_report.get('timelines', []) for clip in tl.get('clips', [])}
    report = {
        'project_name': project_name, 'project_id': project.GetUniqueId(), 'fps': str(actual_fps),
        'coverage': outline['coverage'], 'scope_status': outline['coverage']['scope_status'],
        'import_state': 'in_progress', 'manifest_sha256': outline['manifest_sha256'],
        'generation_plan_sha256': outline.get('generation_plan_sha256'), 'timelines': [],
    }
    try:
        timelines = {}
        for index in range(1, int(project.GetTimelineCount()) + 1):
            timeline = require(project.GetTimelineByIndex(index), 'Timeline lookup failed.')
            name = timeline.GetName()
            if name in timelines:
                raise RuntimeError(f'Duplicate timeline name in dedicated project: {name}')
            timelines[name] = timeline
        # Preflight existing timelines before adding media or creating new timelines.
        for entry in outline['timelines']:
            existing = timelines.get(entry['name'])
            if existing:
                verify_timeline(existing, entry['clips'])
                for clip in entry['clips']:
                    old_hash = prior_hashes.get(clip['local_path'])
                    if old_hash and old_hash != clip['sha256']:
                        raise RuntimeError(f'Audio bytes changed at an existing source path: {clip["local_path"]}')
        for entry in outline['timelines']:
            version_bin = find_or_create_bin(pool, root, entry['version'])
            episode_bin = find_or_create_bin(pool, version_bin, f'EP{entry["episode"]:02d}_旁白')
            require(pool.SetCurrentFolder(episode_bin), 'Cannot select episode bin.')
            existing = timelines.get(entry['name'])
            if existing:
                timeline, status = existing, 'reused_verified'
            else:
                available = {}
                for item in episode_bin.GetClipList() or []:
                    path = media_path(item)
                    if path:
                        available[path] = item
                missing = [clip['local_path'] for clip in entry['clips'] if clip['local_path'] not in available]
                if missing:
                    imported = require(pool.ImportMedia(missing), 'Resolve did not import audio.')
                    for item in imported:
                        path = media_path(item)
                        if path:
                            available[path] = item
                absent = [clip['local_path'] for clip in entry['clips'] if clip['local_path'] not in available]
                if absent:
                    raise RuntimeError(f'Some audio files were not imported: {absent}')
                ordered = [available[clip['local_path']] for clip in entry['clips']]
                # Atomic construction from real media prevents empty placeholder timelines.
                timeline = require(pool.CreateTimelineFromClips(entry['name'], ordered), f'Cannot create timeline: {entry["name"]}')
                timelines[entry['name']] = timeline
                status = 'created'
            placements = verify_timeline(timeline, entry['clips'])
            marker = ensure_partial_marker(timeline, entry, outline['coverage']) if outline['coverage']['scope_status'] == 'partial' else None
            timeline_id = require(timeline.GetUniqueId(), f'Cannot get timeline ID: {entry["name"]}')
            report['timelines'].append({**entry, 'timeline_id': timeline_id, 'status': status, 'placements': placements, 'partial_marker_custom_data': marker})
            require(pm.SaveProject(), 'Resolve failed to save the dedicated project.')
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        expected_timelines = len(outline['timelines'])
        if (len(report['timelines']) != expected_timelines
                or len({entry['timeline_id'] for entry in report['timelines']}) != expected_timelines
                or (outline['coverage']['scope_status'] == 'complete' and expected_timelines != 6)):
            raise RuntimeError('Resolve did not return the expected distinct nonempty narration timelines.')
        if sum(entry['clip_count'] for entry in report['timelines']) != outline['coverage']['downloaded_clip_count']:
            raise RuntimeError('Timeline source coverage does not match all downloaded manifest clips.')
        require(project.SetCurrentTimeline(timelines[outline['timelines'][0]['name']]), 'Cannot select a completed narration timeline.')
        require(pm.SaveProject(), 'Final project save failed.')
        report['import_state'] = 'verified'
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        return report
    finally:
        if prior_folder:
            require(pool.SetCurrentFolder(prior_folder), 'Cannot restore selected bin.')


def rational_time(value):
    value = Fraction(value)
    return f'{value.numerator}/{value.denominator}s'


def export_fcpxml(outline, destination):
    destination.mkdir(parents=True, exist_ok=True)
    exported = []
    fps = Fraction(outline['fps'])
    for entry in outline['timelines']:
        tree = ET.Element('fcpxml', {'version': '1.9'})
        resources = ET.SubElement(tree, 'resources')
        ET.SubElement(resources, 'format', {'id': 'r1', 'name': f'FFVideoFormat1080p{float(fps):g}', 'frameDuration': rational_time(1 / fps), 'width': '1920', 'height': '1080', 'colorSpace': '1-1-1 (Rec. 709)'})
        for index, clip in enumerate(entry['clips'], 2):
            asset = ET.SubElement(resources, 'asset', {'id': f'r{index}', 'name': clip['name'], 'start': '0s', 'duration': rational_time(clip['duration_rational']), 'hasAudio': '1', 'audioSources': '1', 'audioChannels': str(clip['channels']), 'audioRate': str(clip['sample_rate'])})
            ET.SubElement(asset, 'media-rep', {'kind': 'original-media', 'src': Path(clip['local_path']).as_uri()})
        library = ET.SubElement(tree, 'library')
        event = ET.SubElement(library, 'event', {'name': f'大码_{entry["version"]}'})
        project = ET.SubElement(event, 'project', {'name': entry['name']})
        total = sum((Fraction(clip['duration_rational']) for clip in entry['clips']), Fraction())
        sequence = ET.SubElement(project, 'sequence', {'format': 'r1', 'duration': rational_time(total), 'tcStart': '0s', 'tcFormat': 'NDF', 'audioLayout': 'stereo', 'audioRate': '48k'})
        spine = ET.SubElement(sequence, 'spine')
        offset = Fraction()
        for index, clip in enumerate(entry['clips'], 2):
            duration = Fraction(clip['duration_rational'])
            asset_clip = ET.SubElement(spine, 'asset-clip', {'name': clip['name'], 'ref': f'r{index}', 'offset': rational_time(offset), 'start': '0s', 'duration': rational_time(duration), 'audioRole': 'dialogue'})
            if index == 2 and outline['coverage']['scope_status'] == 'partial':
                ET.SubElement(asset_clip, 'marker', {'start': '0s', 'duration': rational_time(1 / fps), 'value': 'PARTIAL 未完成：仅已下载旁白', 'note': f'完整任务应有 {outline["coverage"]["expected_clip_count"]} 段旁白；此文件为不完整成果。'})
            offset += duration
        ET.indent(tree, space='  ')
        output = destination / f'{entry["name"]}.fcpxml'
        body = ET.tostring(tree, encoding='utf-8', xml_declaration=True)
        content = body.replace(b'?>', b'?>\n<!DOCTYPE fcpxml>', 1) + b'\n'
        if output.exists() and output.read_bytes() != content:
            raise FileExistsError(f'Refusing to overwrite a different FCPXML file: {output}')
        output.write_bytes(content)
        ET.parse(output)
        exported.append(str(output))
    return exported


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--apply', action='store_true', help='Create/reuse dedicated Resolve project and six native audio timelines.')
    action.add_argument('--export-fcpxml', type=Path, metavar='DIR', help='Generate an offline fallback only; do not launch/import.')
    parser.add_argument('--allow-partial', action='store_true', help='Explicitly allow missing downloads; create only nonempty episode timelines in a separate PARTIAL/未完成 project with red markers.')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    metadata, groups, fps = load_manifest(args.manifest.resolve(strict=True), allow_partial=args.allow_partial)
    outline = plan(metadata, groups, fps)
    if args.apply:
        report_path = args.report or Path(__file__).with_name('达芬奇导入结果_PARTIAL.json' if outline['coverage']['scope_status'] == 'partial' else '达芬奇导入结果.json')
        result = apply_to_resolve(outline, report_path)
    elif args.export_fcpxml:
        result = {'mode': 'offline_fcpxml', 'coverage': outline['coverage'], 'files': export_fcpxml(outline, args.export_fcpxml)}
    else:
        result = {'mode': 'validated_plan_only', **outline}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        raise SystemExit(1)
