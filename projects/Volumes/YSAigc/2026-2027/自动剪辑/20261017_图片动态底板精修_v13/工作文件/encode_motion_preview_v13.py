#!/usr/bin/env python3
"""Encode actual Resolve screenshots; inspect their pixels and decoded motion.

Offline only: no Resolve imports, connections, timeline writes, image synthesis,
or source-image modifications. Run only after the parent confirms capture ready.
"""

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

import av
import numpy as np
from PIL import Image, ImageDraw


ROOT = Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_图片动态底板精修_v13')
FPS = 25
SIZE = (1920, 1080)
JOBS = {
    7509: {'expected_count': 55, 'output_name': '图片动态底板_校长段预览_v13.mp4'},
    4051: {'expected_count': 110, 'output_name': '图片动态底板_双图段预览_v13.mp4'},
}
# Fixed interior areas selected after viewing the actual 7509 card. The photo
# ROIs deliberately exclude moving borders, captions, and animated background.
ROIS = {
    'left_photo_interior': (165, 335, 850, 740),
    'right_photo_interior': (1070, 345, 1755, 735),
    'main_title': (755, 95, 1165, 185),
    'left_caption': (300, 895, 720, 975),
    'right_caption': (1190, 895, 1640, 975),
    'background_upper_left': (25, 25, 720, 180),
    'background_lower_right': (1660, 880, 1880, 1025),
}
PHOTO_ROIS = ('left_photo_interior', 'right_photo_interior')


def digest(a):
    return hashlib.sha256(a.tobytes()).hexdigest()


def crops(a):
    result = {'full_frame': a}
    for name, (x0, y0, x1, y1) in ROIS.items():
        result[name] = a[y0:y1, x0:x1]
    return result


def pair_metrics(a, b):
    diff = np.abs(a.astype(np.int16) - b.astype(np.int16))
    # The 99th percentile is sampled evenly, while means/changes use all pixels.
    return {
        'mean_absolute_difference_8bit': float(diff.mean()),
        'p99_absolute_difference_8bit': float(np.percentile(diff[::4, ::4], 99)),
        'changed_pixel_fraction': float(np.any(diff != 0, axis=2).mean()),
        'changed_above_2_fraction': float(np.max(diff, axis=2).__gt__(2).mean()),
        'exact_duplicate': bool(not np.any(diff)),
    }


def runs(indices):
    result = []
    for i in indices:
        if result and i == result[-1][-1] + 1:
            result[-1].append(i)
        else:
            result.append([i])
    return [{'from_frame': r[0] - 1, 'through_frame': r[-1],
             'adjacent_pairs': len(r)} for r in result]


class MotionScan:
    def __init__(self):
        self.first = None
        self.previous = None
        self.last = None
        self.hashes = []
        self.pairs = {name: [] for name in ('full_frame', *ROIS)}

    def add(self, a, index):
        if a.shape != (SIZE[1], SIZE[0], 3):
            raise ValueError(f'Frame {index}: unexpected RGB shape {a.shape}')
        self.hashes.append(digest(a))
        if self.first is None:
            self.first = a.copy()
        if self.previous is not None:
            old, new = crops(self.previous), crops(a)
            for name in self.pairs:
                self.pairs[name].append({'to_frame': index,
                                         **pair_metrics(old[name], new[name])})
        self.previous = a.copy()
        self.last = a.copy()

    def report(self):
        output = {}
        first, last = crops(self.first), crops(self.last)
        for name, items in self.pairs.items():
            maes = np.array([p['mean_absolute_difference_8bit'] for p in items])
            median = float(np.median(maes))
            # A conservative outlier guard, not a claim that every non-outlier
            # is attractive. Slow easing near either end is allowed.
            jump_threshold = max(6.0, median * 10.0)
            exact = [p['to_frame'] for p in items if p['exact_duplicate']]
            nearzero = [p['to_frame'] for p in items
                        if p['mean_absolute_difference_8bit'] < 0.02]
            output[name] = {
                'roi_xyxy': [0, 0, *SIZE] if name == 'full_frame' else list(ROIS[name]),
                'adjacent_pairs': items,
                'mae_min_median_max_8bit': [float(maes.min()), median, float(maes.max())],
                'exact_adjacent_duplicate_to_frames': exact,
                'long_near_zero_motion_runs': [r for r in runs(nearzero)
                                               if r['adjacent_pairs'] >= 10],
                'jump_threshold_mae_8bit': jump_threshold,
                'large_jump_to_frames': [p['to_frame'] for p in items
                                         if p['mean_absolute_difference_8bit'] > jump_threshold],
                'first_to_last': pair_metrics(first[name], last[name]),
            }
        return {'frames': len(self.hashes), 'unique_rgb_frames': len(set(self.hashes)),
                'rgb_sha256_by_frame': self.hashes, 'regions': output}


def save_visuals(samples, preview, start, sample_indices):
    sheet = Image.new('RGB', (1920, 780), 'white')
    for j, i in enumerate(sample_indices):
        x, y = (j % 3) * 640, (j // 3) * 390
        sheet.paste(samples[i].resize((640, 360), Image.Resampling.LANCZOS), (x, y))
        ImageDraw.Draw(sheet).text((x + 10, y + 365), f'frame {i:04d} / {i / FPS:.2f}s', fill='black')
    sheet_path = preview / f'双图{start}_连续运动抽帧_v13.jpg'
    sheet.save(sheet_path, quality=94)
    overlay = samples[0].copy()
    draw = ImageDraw.Draw(overlay)
    for i, (name, box) in enumerate(ROIS.items(), 1):
        draw.rectangle(box, outline=(255, 225, 55), width=3)
        draw.text((box[0] + 4, box[1] + 4), f'{i}: {name}', fill=(255, 225, 55))
    overlay_path = preview / f'双图{start}_运动检测区域_v13.jpg'
    overlay.save(overlay_path, quality=94)
    return str(sheet_path), str(overlay_path)


def validate_sequence(source, count):
    expected = [source / f'{i:04d}.jpg' for i in range(count)]
    # Native capture also keeps *_check.jpg companions for stability checks.
    # They are not sequence frames and must never enter the encoded movie.
    found = sorted(p for p in source.glob('*.jpg') if p.stem.isdigit() and len(p.stem) == 4)
    if found != expected:
        missing = [str(p.name) for p in expected if p not in found]
        extra = [str(p.name) for p in found if p not in expected]
        raise ValueError(f'{source}: expected exactly 0000..{count-1:04d}.jpg; missing={missing}, extra={extra}')
    return expected


def encode_segment(root, start, count, output_name, overwrite):
    preview = root / '包装预览'
    source = preview / '连续运动校验' / str(start)
    output = preview / output_name
    report_path = root / '工作文件' / f'motion_preview_verified_v13_{start}.json'
    sample_indices = tuple(int(round(t)) for t in np.linspace(0, count - 1, 6))
    temporary = output.with_name(output.stem + '.encoding.tmp.mp4')
    for p in (output, temporary, report_path):
        if p.exists() and not overwrite:
            raise FileExistsError(f'Refusing to overwrite existing artifact: {p}')
    expected = validate_sequence(source, count)
    preview.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    source_scan = MotionScan()
    file_hashes = []
    capture_repeat_deltas = []
    with av.open(str(temporary), 'w', options={'movflags': '+faststart'}) as container:
        stream = container.add_stream('libx264', rate=FPS)
        stream.width, stream.height = SIZE
        stream.pix_fmt = 'yuv420p'
        stream.time_base = Fraction(1, FPS)
        stream.options = {'crf': '19', 'preset': 'medium'}
        for i, path in enumerate(expected):
            file_hashes.append(hashlib.sha256(path.read_bytes()).hexdigest())
            with Image.open(path) as im:
                if im.size != SIZE:
                    raise ValueError(f'{path}: unexpected image size {im.size}')
                rgb = im.convert('RGB')
                a = np.asarray(rgb)
                source_scan.add(a, i)
                check_path = path.with_name(path.stem + '_check.jpg')
                if check_path.exists():
                    with Image.open(check_path) as check_im:
                        b = np.asarray(check_im.convert('RGB'))
                        capture_repeat_deltas.append({'frame': i, 'mean_rgb_delta_8bit':
                            float(np.abs(a.astype(np.int16) - b.astype(np.int16)).mean())})
                frame = av.VideoFrame.from_image(rgb)
            frame.pts = i
            frame.time_base = Fraction(1, FPS)
            for packet in stream.encode(frame):
                container.mux(packet)
        for packet in stream.encode():
            container.mux(packet)

    decoded_scan = MotionScan()
    samples, timestamps, fidelity = {}, [], []
    with av.open(str(temporary)) as container:
        video = container.streams.video[0]
        media = {'codec': video.codec_context.name,
                 'pixel_format': video.codec_context.format.name,
                 'resolution': [video.width, video.height],
                 'fps': float(video.average_rate), 'fps_rational': str(video.average_rate),
                 'audio_streams': len(container.streams.audio),
                 'time_base': str(video.time_base),
                 'stream_duration_seconds': float(video.duration * video.time_base)
                 if video.duration is not None else None}
        for i, frame in enumerate(container.decode(video)):
            a = frame.to_ndarray(format='rgb24')
            decoded_scan.add(a, i)
            timestamps.append(float(frame.pts * frame.time_base))
            if i >= count:
                raise ValueError(f'Decoded video has more than {count} frames')
            with Image.open(expected[i]) as im:
                source_rgb = np.asarray(im.convert('RGB'))
                fidelity.append(float(np.abs(a.astype(np.int16) - source_rgb.astype(np.int16)).mean()))
            if i in sample_indices:
                samples[i] = Image.fromarray(a)
    source_report, decoded_report = source_scan.report(), decoded_scan.report()
    issues, warnings = [], []
    if any(r['mean_rgb_delta_8bit'] > 0 for r in capture_repeat_deltas):
        warnings.append({'reason': 'native_capture_repeat_not_pixel_identical',
                         'frames': [r for r in capture_repeat_deltas if r['mean_rgb_delta_8bit'] > 0]})
    if decoded_report['frames'] != count:
        issues.append(f'decoded_frame_count_not_{count}')
    if (media['codec'], media['pixel_format'], media['resolution'], media['fps'], media['audio_streams']) != (
            'h264', 'yuv420p', [1920, 1080], 25, 0):
        issues.append('output_format_mismatch')
    if len(timestamps) != count or not np.allclose(timestamps, np.arange(count) / FPS, atol=1e-7):
        issues.append('nonuniform_or_incorrect_frame_timestamps')
    for kind, scan in [('actual_source_screenshots', source_report), ('decoded_video', decoded_report)]:
        for name, region in scan['regions'].items():
            if name == 'full_frame' and region['exact_adjacent_duplicate_to_frames']:
                issues.append({'kind': kind, 'region': name, 'adjacent_duplicates': region['exact_adjacent_duplicate_to_frames']})
            if name in PHOTO_ROIS:
                if region['first_to_last']['mean_absolute_difference_8bit'] < 0.1:
                    issues.append({'kind': kind, 'region': name, 'reason': 'photo_motion_not_demonstrated'})
                if region['long_near_zero_motion_runs']:
                    warnings.append({'kind': kind, 'region': name, 'near_zero_runs': region['long_near_zero_motion_runs']})
            if name in ('full_frame', *PHOTO_ROIS) and region['large_jump_to_frames']:
                issues.append({'kind': kind, 'region': name, 'large_jump_to_frames': region['large_jump_to_frames']})
    if max(fidelity, default=math.inf) > 8:
        warnings.append({'reason': 'large_source_to_decoded_rgb_error', 'maximum_mean_error_8bit': max(fidelity)})
    sheet, overlay = save_visuals(samples, preview, start, sample_indices) if len(samples) == len(sample_indices) else (None, None)
    temporary.replace(output)
    report = {
        'status': 'failed' if issues else ('needs_visual_review' if warnings else 'passed'),
        'output': str(output), 'input_sequence': str(source),
        'source': f'{count} actual sequential native timeline screenshots; no synthetic interpolation or motion added offline',
        'timeline_record_start': start,
        'timeline_record_end_exclusive': start + count,
        'timeline_last_included_record_frame': start + count - 1,
        'length_manifest': str(root / '工作文件' / 'package_baselines_v13.json'),
        'expected_frames': count, 'fps': FPS, 'duration_seconds': count / FPS,
        'encoding': {'encoder': 'libx264', 'crf': 19, 'preset': 'medium', 'pixel_format': 'yuv420p'},
        'output_media': media, 'decoded_frame_timestamps_seconds': timestamps,
        'input_file_sha256_by_frame': file_hashes,
        'native_capture_repeat_pixel_deltas': capture_repeat_deltas,
        'capture_check_companions_excluded_from_video': True,
        'actual_source_screenshot_pixel_motion': source_report,
        'actual_decoded_pixel_motion': decoded_report,
        'source_to_decoded_rgb_mae_min_mean_max_8bit': [min(fidelity), float(np.mean(fidelity)), max(fidelity)],
        'issues': issues, 'warnings': warnings, 'contact_sheet': sheet, 'roi_reference_image': overlay,
        'roi_interpretation': 'Photo interior ROIs prove image content motion independently of moving borders/background. Title/caption/background differences are measured separately; background animation beneath stationary text can cause nonzero text-ROI differences.',
        'limits': 'Pixel metrics flag exact freezes and large jumps; they do not establish aesthetic quality, text tracking quality, or every subpixel artifact. Inspect the contact sheet/video before final visual approval.',
        'resolve_connected_or_modified': False, 'source_images_modified': False,
        'whole_film_exported': False,
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'status': report['status'], 'output': str(output), 'qa': str(report_path),
                      'decoded_frames': decoded_report['frames'],
                      'source_adjacent_duplicates': source_report['regions']['full_frame']['exact_adjacent_duplicate_to_frames'],
                      'decoded_adjacent_duplicates': decoded_report['regions']['full_frame']['exact_adjacent_duplicate_to_frames'],
                      'issues': issues, 'warnings': warnings}, ensure_ascii=False))
    return report


def encode_joined_preview(root, overwrite):
    """Encode the same screenshots in the requested order, without transitions."""
    preview = root / '包装预览'
    output = preview / '图片动态底板_完整动效预览_v13_6.6秒.mp4'
    temporary = output.with_name(output.stem + '.encoding.tmp.mp4')
    report_path = root / '工作文件' / 'motion_preview_joined_verified_v13.json'
    for path in (output, temporary, report_path):
        if path.exists() and not overwrite:
            raise FileExistsError(f'Refusing to overwrite existing artifact: {path}')
    segments = [(4051, 110), (7509, 55)]
    paths = [path for start, count in segments
             for path in validate_sequence(preview / '连续运动校验' / str(start), count)]
    count = len(paths)
    with av.open(str(temporary), 'w', options={'movflags': '+faststart'}) as container:
        stream = container.add_stream('libx264', rate=FPS)
        stream.width, stream.height = SIZE
        stream.pix_fmt = 'yuv420p'
        stream.time_base = Fraction(1, FPS)
        stream.options = {'crf': '19', 'preset': 'medium'}
        for i, path in enumerate(paths):
            with Image.open(path) as im:
                frame = av.VideoFrame.from_image(im.convert('RGB'))
            frame.pts, frame.time_base = i, Fraction(1, FPS)
            for packet in stream.encode(frame):
                container.mux(packet)
        for packet in stream.encode():
            container.mux(packet)
    scan = MotionScan()
    timestamps, fidelity, samples = [], [], {}
    sample_indices = (0, 54, 109, 110, 137, 164)
    with av.open(str(temporary)) as container:
        video = container.streams.video[0]
        media = {'codec': video.codec_context.name,
                 'pixel_format': video.codec_context.format.name,
                 'resolution': [video.width, video.height], 'fps': float(video.average_rate),
                 'fps_rational': str(video.average_rate),
                 'audio_streams': len(container.streams.audio),
                 'stream_duration_seconds': float(video.duration * video.time_base)
                 if video.duration is not None else None}
        for i, frame in enumerate(container.decode(video)):
            if i >= count:
                raise ValueError('Joined preview has more than 165 frames')
            a = frame.to_ndarray(format='rgb24')
            scan.add(a, i)
            timestamps.append(float(frame.pts * frame.time_base))
            with Image.open(paths[i]) as im:
                b = np.asarray(im.convert('RGB'))
                fidelity.append(float(np.abs(a.astype(np.int16) - b.astype(np.int16)).mean()))
            if i in sample_indices:
                samples[i] = Image.fromarray(a)
    motion = scan.report()
    cut = 110
    issues = []
    if motion['frames'] != 165:
        issues.append('joined_decoded_frame_count_not_165')
    if (media['codec'], media['pixel_format'], media['resolution'], media['fps'], media['audio_streams']) != (
            'h264', 'yuv420p', [1920, 1080], 25, 0):
        issues.append('joined_output_format_mismatch')
    if len(timestamps) != count or not np.allclose(timestamps, np.arange(count) / FPS, atol=1e-7):
        issues.append('joined_frame_timestamps_incorrect')
    duplicates = motion['regions']['full_frame']['exact_adjacent_duplicate_to_frames']
    if duplicates:
        issues.append({'joined_adjacent_duplicate_to_frames': duplicates})
    for name in ('full_frame', *PHOTO_ROIS):
        unexpected = [i for i in motion['regions'][name]['large_jump_to_frames'] if i != cut]
        if unexpected:
            issues.append({'region': name, 'unexpected_large_jump_to_frames': unexpected})
    if max(fidelity, default=math.inf) > 8:
        issues.append({'reason': 'joined_frame_source_mismatch', 'maximum_rgb_mae_8bit': max(fidelity)})
    sheet, overlay = save_visuals(samples, preview, '完整6.6秒', sample_indices)
    temporary.replace(output)
    result = {
        'status': 'failed' if issues else 'passed', 'output': str(output),
        'segments_in_order': [{'record_start': start, 'frames': n, 'seconds': n / FPS}
                              for start, n in segments],
        'source': 'The same actual sequential screenshots, encoded directly once; no new visuals or transitions',
        'expected_frames': 165, 'decoded_frames': motion['frames'], 'fps': FPS,
        'duration_seconds': 6.6, 'output_media': media,
        'direct_cut_to_frame': cut, 'direct_cut_time_seconds': cut / FPS,
        'intentional_cut_excluded_from_jump_flags': True,
        'decoded_frame_timestamps_seconds': timestamps,
        'actual_decoded_pixel_motion': motion,
        'source_to_decoded_rgb_mae_min_mean_max_8bit': [min(fidelity), float(np.mean(fidelity)), max(fidelity)],
        'issues': issues, 'contact_sheet': sheet, 'roi_reference_image': overlay,
        'resolve_connected_or_modified': False, 'source_images_modified': False,
        'whole_film_exported': False,
    }
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'joined_status': result['status'], 'output': str(output),
                      'qa': str(report_path), 'decoded_frames': motion['frames'],
                      'adjacent_duplicates': duplicates, 'issues': issues}, ensure_ascii=False), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--overwrite', action='store_true',
                        help='Replace only this task\'s previously generated preview/QA artifacts.')
    args = parser.parse_args()
    root = args.root.resolve()
    manifest_path = root / '工作文件' / 'package_baselines_v13.json'
    manifest = {r['start']: r for r in json.loads(manifest_path.read_text(encoding='utf-8'))}
    summary_path = root / '工作文件' / 'motion_preview_verified_v13.json'
    if summary_path.exists() and not args.overwrite:
        raise FileExistsError(f'Refusing to overwrite existing artifact: {summary_path}')
    # Validate both capture sets and their authoritative lengths before encoding
    # anything. Each sequence stays inside its own timeline card boundaries.
    for start, job in JOBS.items():
        if start not in manifest or int(manifest[start]['length']) != job['expected_count']:
            raise ValueError(f'{start}: manifest does not match confirmed length {job["expected_count"]}')
        validate_sequence(root / '包装预览' / '连续运动校验' / str(start), job['expected_count'])
    reports = []
    for start, job in JOBS.items():
        reports.append(encode_segment(root, start, job['expected_count'], job['output_name'], args.overwrite))
    joined = encode_joined_preview(root, args.overwrite)
    status = ('failed' if any(r['status'] == 'failed' for r in [*reports, joined])
              else 'needs_visual_review' if any(r['status'] == 'needs_visual_review' for r in reports)
              else 'passed')
    summary = {
        'status': status, 'length_manifest': str(manifest_path),
        'separate_previews': [{k: r[k] for k in ('timeline_record_start', 'timeline_record_end_exclusive',
                              'expected_frames', 'fps', 'duration_seconds', 'output', 'status',
                              'issues', 'warnings', 'contact_sheet', 'roi_reference_image')} for r in reports],
        'total_verified_frames': sum(r['expected_frames'] for r in reports),
        'total_seconds_in_separate_previews': sum(r['duration_seconds'] for r in reports),
        'per_segment_qa': [str(root / '工作文件' / f'motion_preview_verified_v13_{start}.json') for start in JOBS],
        'joined_video_created': True,
        'joined_preview': {k: joined[k] for k in ('output', 'status', 'decoded_frames', 'duration_seconds',
                                                  'direct_cut_time_seconds', 'contact_sheet', 'issues')},
        'joined_qa': str(root / '工作文件' / 'motion_preview_joined_verified_v13.json'),
        'resolve_connected_or_modified': False,
        'source_images_modified': False, 'whole_film_exported': False,
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'status': status, 'summary': str(summary_path)}, ensure_ascii=False))
    if status == 'failed':
        raise SystemExit(2)


if __name__ == '__main__':
    main()
