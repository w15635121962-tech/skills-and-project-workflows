#!/usr/bin/env python3
"""Rebuild only A4 WAV assets from final native picture mapping + new SRT.

No Resolve, ASR, download or picture rendering. Source music and offsets are
frozen from the approved twelve cues. No existing input or cue is overwritten.
"""
from pathlib import Path
import argparse
import copy
import datetime
import hashlib
import importlib.util
import json
import math
import re


HERE = Path(__file__).resolve().parent
OLD = HERE.parent / '达芬奇剪辑_EP21-25_20261020'
RATE, FPS, SPF = 48000, 24, 2000


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def ep_number(value):
    if value.get('episode') is not None:
        return int(value['episode'])
    match = re.search(r'EP(\d+)', value.get('timeline_name', value.get('name', '')))
    if not match:
        raise ValueError('Cannot identify episode in native plan/snapshot.')
    return int(match[1])


def normalize_plan(data):
    """Accept native snapshot timelines or final native source-mapping plan."""
    result = {}
    for ep in data.get('episodes', data.get('timelines', [])):
        eno = ep_number(ep)
        if eno not in range(21, 26):
            continue
        settings = ep.get('settings') or {}
        fps = float(ep.get('fps', settings.get('timelineFrameRate', FPS)))
        if fps != FPS:
            raise ValueError(f'EP{eno}: expected 24fps, got {fps}.')
        if int(ep.get('start', ep.get('record_start_frame', 0))) != 0:
            raise ValueError(f'EP{eno}: timeline must start at frame zero.')
        duration = int(ep.get('duration_frames', ep.get('end', 0)))
        videos = ep.get('video')
        if videos is None:
            videos = [v for tr in ep['tracks']['video'] if tr['track'] == 1 for v in tr['items']]
        normalized = []
        for v in videos:
            if v.get('track', 1) != 1:
                continue
            start = int(v.get('record_frame', v.get('start', 0)))
            source_start = int(v.get('source_start_frame', v.get('source_start', 0)))
            end = v.get('record_end_frame', v.get('end'))
            if end is None:
                end = start + int(v.get('duration_frames', int(v['source_end_frame_exclusive']) - source_start))
            end = int(end)
            # Final V1 remains source-speed100%; native source-end getters can
            # cap to final valid frame index at the physical source tail.
            if end <= start:
                raise ValueError(f'EP{eno}: nonpositive V1 duration.')
            normalized.append({'source_path': str(Path(v['source_path']).resolve()),
                               'source_start_frame': source_start,
                               'source_end_frame_exclusive': (source_start + 1 if v.get('kind') == 'freeze_frame'
                                                              else source_start + end - start),
                               'record_frame': start, 'record_end_frame': end})
        cursor = 0
        for v in sorted(normalized, key=lambda x: x['record_frame']):
            if v['record_frame'] != cursor:
                raise ValueError(f'EP{eno}: V1 has a gap/overlap near frame {cursor}.')
            cursor = v['record_end_frame']
        if cursor != duration:
            raise ValueError(f'EP{eno}: V1 end {cursor} differs from duration {duration}.')
        result[eno] = {'episode': eno, 'timeline_name': ep.get('timeline_name', ep.get('name')),
                       'fps': FPS, 'duration_frames': duration, 'video': normalized}
    if sorted(result) != list(range(21, 26)):
        raise ValueError('Final input must contain all local EP21–25 exactly once.')
    return result


def map_boundary(eno, old_frame, old_ep, new_ep, overrides):
    if old_frame == 0:
        return 0, {'method': 'new timeline start'}
    if old_frame == old_ep['duration_frames']:
        return new_ep['duration_frames'], {'method': 'new timeline end'}
    override = overrides.get(str(eno), {}).get(str(old_frame))
    if override is not None:
        return int(override), {'method': 'explicit supplied old-to-new boundary', 'old_frame': old_frame}
    containing = [v for v in old_ep['video'] if v['record_frame'] <= old_frame
                  < v['record_frame'] + v['source_end_frame_exclusive'] - v['source_start_frame']]
    if len(containing) != 1:
        raise ValueError(f'EP{eno}: old music boundary {old_frame} has no unique V1 anchor.')
    original = containing[0]
    path = str(Path(original['source_path']).resolve())
    source_frame = original['source_start_frame'] + old_frame - original['record_frame']
    matches = [v['record_frame'] + source_frame - v['source_start_frame'] for v in new_ep['video']
               if v['source_path'] == path and v['source_start_frame'] <= source_frame < v['source_end_frame_exclusive']]
    if len(matches) != 1:
        raise ValueError(f'EP{eno}: source anchor for old boundary {old_frame} was removed/duplicated; supply '
                         f'--boundary-map JSON {{"{eno}":{{"{old_frame}":NEW_FRAME}}}}.')
    return matches[0], {'method': 'same V1 source path/source frame', 'old_frame': old_frame,
                        'source_path': path, 'source_frame': source_frame, 'new_frame': matches[0]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', required=True, help='Final native mapping plan OR final live snapshot JSON.')
    parser.add_argument('--srt-dir', required=True, help='Final retimed SRT folder containing EP21.srt through EP25.srt.')
    parser.add_argument('--boundary-map', help='Optional {episode:{old_music_boundary_frame:new_frame}} JSON.')
    parser.add_argument('--output', default=str(HERE / '配乐110重制'))
    parser.add_argument('--render', action='store_true', help='Actually write new WAVs. Default performs input preflight only.')
    args = parser.parse_args()
    plan_path, srt_dir, output = Path(args.plan).resolve(), Path(args.srt_dir).resolve(), Path(args.output).resolve()
    old_music_path = OLD / '配乐/配乐执行计划.json'
    old_edit_path = OLD / '剪辑执行计划.json'
    license_path = OLD / '配乐/配乐来源与授权.json'
    old_music = read_json(old_music_path)
    old_edit = {e['episode']: e for e in read_json(old_edit_path)['episodes']}
    final = normalize_plan(read_json(plan_path))
    overrides = read_json(args.boundary_map) if args.boundary_map else {}
    mapped, frozen = [], {plan_path, old_music_path, old_edit_path, license_path}
    if args.boundary_map:
        frozen.add(Path(args.boundary_map).resolve())
    for episode in old_music['episodes']:
        eno = episode['episode']
        srt = srt_dir / f'EP{eno}.srt'
        if not srt.is_file():
            raise FileNotFoundError(srt)
        frozen.add(srt)
        cues = []
        for original in episode['cues']:
            start, start_evidence = map_boundary(eno, original['record_frame'], old_edit[eno], final[eno], overrides)
            old_end = original['record_frame'] + original['duration_frames']
            end, end_evidence = map_boundary(eno, old_end, old_edit[eno], final[eno], overrides)
            if not 0 <= start < end <= final[eno]['duration_frames']:
                raise ValueError(f'{original["id"]}: invalid mapped range {start}..{end}.')
            source = Path(original['source_info']['path'])
            frozen.add(source)
            if sha(source) != original['source_info']['sha256']:
                raise ValueError(f'Original music source hash changed: {source}')
            cues.append({'original': original, 'record_frame': start, 'end_frame': end,
                         'duration_frames': end - start,
                         'boundary_evidence': {'start': start_evidence, 'end': end_evidence}})
        if cues[0]['record_frame'] != 0 or cues[-1]['end_frame'] != final[eno]['duration_frames']:
            raise ValueError(f'EP{eno}: music does not span whole new timeline.')
        if any(a['end_frame'] != b['record_frame'] for a, b in zip(cues, cues[1:])):
            raise ValueError(f'EP{eno}: music cue gap/overlap.')
        mapped.append({'episode': eno, 'timeline_name': final[eno]['timeline_name'], 'fps': FPS,
                       'duration_frames': final[eno]['duration_frames'], 'srt_path': str(srt), 'cues': cues})
    if sum(len(e['cues']) for e in mapped) != 12:
        raise ValueError('Expected exactly twelve preserved music cues.')
    input_hashes = {str(p): sha(p) for p in sorted(frozen)}
    preflight = {'mode': 'render' if args.render else 'preflight_only',
                 'episodes': [{'episode': e['episode'], 'duration_frames': e['duration_frames'],
                               'cues': [{'id': c['original']['id'], 'record_frame': c['record_frame'],
                                         'duration_frames': c['duration_frames'],
                                         'original_music_source_start_sample_48000': c['original']['source_info']['source_start_sample_48000']}
                                        for c in e['cues']]} for e in mapped]}
    print(json.dumps(preflight, ensure_ascii=False, indent=2), flush=True)
    if not args.render:
        print('Preflight only; no files written or media processed.', flush=True)
        return
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f'Refusing to overwrite nonempty output folder: {output}')
    output.mkdir(parents=True, exist_ok=True)
    analysis = output / '分析'
    analysis.mkdir()
    spec = importlib.util.spec_from_file_location('approved_music_builder', OLD / '配乐/build_music_cues.py')
    music = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(music)
    music.ANALYSIS = analysis  # Only new outputs; original helper main() never runs.
    np = music.np
    decoded = {}
    result = {'created_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'scope': 'Rebuilt A4 WAV assets only from final native mapping/SRT; no Resolve/ASR/original input mutation.',
              'plan_path': str(plan_path), 'plan_sha256': input_hashes[str(plan_path)],
              'fps': FPS, 'sample_rate': RATE, 'samples_per_frame': SPF,
              'import_policy': 'Native A4; source_start0, exclusive source_end=duration_frames; clip gain0dB because gain/duck/fades baked into asset.',
              'source_music_offsets_frozen': True, 'license_manifest': str(license_path),
              'no_subjective_full_mix_listening_claimed': True, 'episodes': []}
    for ep in mapped:
        intervals = music.parse_srt(Path(ep['srt_path']))
        if not intervals:
            raise ValueError(f'EP{ep["episode"]}: no SRT intervals.')
        for i, (a, b) in enumerate(intervals):
            if not 0 <= a < b <= ep['duration_frames'] / FPS + 0.001:
                raise ValueError(f'EP{ep["episode"]}: SRT cue{i+1} outside final timeline.')
            if i and a < intervals[i - 1][1] - 0.001:
                raise ValueError(f'EP{ep["episode"]}: SRT overlap near cue{i+1}.')
        cue_dir = output / 'Cues' / f'EP{ep["episode"]}'
        cue_dir.mkdir(parents=True)
        completed = []
        for cue in ep['cues']:
            old = cue['original']
            source = old['source_info']['path']
            if source not in decoded:
                raw = music.run([music.FFMPEG, '-v', 'error', '-i', source, '-vn', '-ar', str(RATE),
                                 '-ac', '2', '-f', 'f32le', 'pipe:1']).stdout
                decoded[source] = np.frombuffer(raw, dtype='<f4').reshape(-1, 2).copy()
            length = cue['duration_frames'] * SPF
            offset = int(old['source_info']['source_start_sample_48000'])
            x = decoded[source][offset:offset + length].copy()
            if len(x) != length:
                raise ValueError(f'{old["id"]}: frozen music source offset is too short for new duration; no loop/pad permitted.')
            speech, protect, edges, clipped, env = music.envelopes(length, cue['record_frame'] / FPS, intervals)
            x *= edges[:, None]
            raw_speech = music.analyse_array(x[speech])
            if not raw_speech or not math.isfinite(raw_speech['input_i']):
                raise ValueError(f'{old["id"]}: no measurable new-SRT speech region; inspect boundaries/SRT.')
            base_gain = -32 - raw_speech['input_i']
            x *= np.float32(10 ** (base_gain / 20))
            gap_mask = (~speech) & (protect < 0.05) & (edges > 0.95)
            gap_before = music.analyse_array(x[gap_mask])
            boost = (3.0 if not gap_before or not math.isfinite(gap_before['input_i'])
                     else min(3.0, max(0.0, -29 - gap_before['input_i'])))
            x *= np.power(10, boost * (1 - protect) / 20).astype(np.float32)[:, None]
            filename = f'{old["id"]}_native110_{cue["record_frame"]:05d}-{cue["end_frame"]:05d}.wav'
            wav = cue_dir / filename
            music.run([music.FFMPEG, '-v', 'error', '-f', 'f32le', '-ar', str(RATE), '-ac', '2',
                       '-i', 'pipe:0', '-c:a', 'pcm_s24le', '-ar', str(RATE), '-ac', '2', str(wav)],
                      np.asarray(x, dtype='<f4').tobytes())
            probe = json.loads(music.run([music.FFPROBE, '-v', 'error', '-select_streams', 'a:0',
                                         '-show_streams', '-of', 'json', str(wav)]).stdout)
            stream = probe['streams'][0]
            if not (stream['codec_name'] == 'pcm_s24le' and int(stream['sample_rate']) == RATE
                    and stream['channels'] == 2 and int(stream['bits_per_raw_sample']) == 24
                    and stream['time_base'] == '1/48000' and int(stream['duration_ts']) == length):
                raise AssertionError(f'{old["id"]}: PCM format/sample-frame duration mismatch.')
            actual = music.analyse_wav(wav)
            speech_metric = music.analyse_array(x[speech])
            gap_metric = music.analyse_array(x[gap_mask])
            if actual['input_tp'] >= -12 or abs(speech_metric['input_i'] + 32) > 0.2:
                raise AssertionError(f'{old["id"]}: unexpected music peak or speech-region loudness.')
            if not (np.all(x[0] == 0) and np.all(x[-1] == 0)):
                raise AssertionError('Music edge fade must start/end at exact zero.')
            envelope_path = analysis / (wav.stem + '_envelope.png')
            music.plot_cue(envelope_path, x, protect, edges, wav.stem)
            metrics = {'actual_pcm24_wav_r128': actual, 'speech_regions_concatenated': speech_metric,
                       'unprotected_gap_regions_concatenated': gap_metric,
                       'sample_peak_dbfs': music.db(np.max(np.abs(x))),
                       'speech_seconds': int(np.count_nonzero(speech)) / RATE,
                       'unprotected_gap_seconds': int(np.count_nonzero(gap_mask)) / RATE,
                       'note': 'Subset concatenation is only a metric, not a playback edit. No subjective listening claim.'}
            analysis_path = analysis / (wav.stem + '_analysis.json')
            dump(analysis_path, {'ffprobe': probe, 'loudness': metrics, 'boundary_evidence': cue['boundary_evidence']})
            item = {'id': old['id'], 'path': str(wav), 'sha256': sha(wav), 'record_frame': cue['record_frame'],
                    'duration_frames': cue['duration_frames'], 'source_start_frame': 0,
                    'source_end_frame_exclusive': cue['duration_frames'], 'track': 4,
                    'resolve_item_gain_db': 0, 'gain_already_baked_into_asset': True,
                    'purpose': old['purpose'], 'sample_rate': RATE, 'channels': 2, 'pcm_bit_depth': 24,
                    'sample_count': length, 'duration_seconds': length / RATE, 'loop_count': 0,
                    'source_info': dict(copy.deepcopy(old['source_info']),
                                        source_end_seconds_exclusive=(offset + length) / RATE,
                                        entry_selection={'method': 'Exact original approved source offset retained; no new selection.'}),
                    'processing': dict(env, base_gain_relative_to_decoded_original_db=round(base_gain, 6),
                                       gap_boost_db=round(boost, 6), speech_intervals_relative_seconds=clipped,
                                       edge_curve='squared sine/cosine', duck_curve='new SRT union protection envelopes',
                                       compressor_or_limiter=False),
                    'loudness_analysis': metrics, 'license': old['license'],
                    'analysis_path': str(analysis_path), 'envelope_plot': str(envelope_path),
                    'old_record_frame': old['record_frame'], 'boundary_mapping': cue['boundary_evidence']}
            completed.append(item)
            print(f'{item["id"]}: {cue["duration_frames"]}fr, frozen source{offset/RATE:.3f}s, speechI{speech_metric["input_i"]:.2f}, TP{actual["input_tp"]:.2f}', flush=True)
        result['episodes'].append({k: ep[k] for k in ('episode', 'timeline_name', 'fps', 'duration_frames', 'srt_path')}
                                  | {'audio_track': 4, 'srt_sha256': sha(ep['srt_path']), 'cues': completed})
    if {str(p): sha(p) for p in frozen} != input_hashes:
        raise RuntimeError('An immutable input changed during music creation; do not import these assets.')
    result['validation'] = {'cue_count': 12, 'episode_count': 5,
                            'all_original_music_source_offsets_preserved_exactly': True,
                            'all_outputs_pcm_24bit_stereo_48000': True,
                            'all_sample_counts_equal_duration_frames_times_2000': True,
                            'all_cues_nonoverlapping_and_within_final_episode': True,
                            'all_A4_spans_exact_final_timeline_bounds': True,
                            'new_SRT_protection_baked': True,
                            'all_speech_subset_loudness_within_0_2_lu_of_minus_32': True,
                            'all_output_true_peaks_below_minus12_dbtp': True,
                            'all_cues_nonlooping': True, 'immutable_input_hashes_unchanged': input_hashes}
    destination = output / '配乐执行计划_原生旁白110.json'
    dump(destination, result)
    print(f'COMPLETE: {destination}; no Resolve/ASR/input mutations.', flush=True)


if __name__ == '__main__':
    main()
