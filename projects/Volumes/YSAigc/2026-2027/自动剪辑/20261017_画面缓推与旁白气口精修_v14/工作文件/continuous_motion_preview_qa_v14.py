"""Offline QA and preview from actual Resolve frame captures; no Resolve connection.

No interpolation, generated motion, source overwrite, loudness processing or bus emulation.
The only image resampling below is for measurement/preview contact sheets and H.264
RGB-to-YUV conversion. The deliverable video uses the actual captured frames in order.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

import av
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw
from scipy.ndimage import map_coordinates
from scipy.optimize import least_squares
from scipy.signal import correlate, correlation_lags

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / '工作文件'
PRE = ROOT / '精修预览'
FRAMES = PRE / '连续运动核验'
FPS, WIDTH, HEIGHT, SR = 25, 1920, 1080, 48000
START, N = 6335, 260
AUDIO = ROOT / '旁白与混音/03_完整混音_气口精修_v14.wav'
OUTPUT = PRE / '画面缓推与旁白气口_配画预览_v14.mp4'
FINAL = False


def qa_path(stem):
    return WORK / f'{stem}{"_最终" if FINAL else ""}_v14.json'


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def rgb(path):
    with Image.open(path) as im:
        assert im.size == (WIDTH, HEIGHT), (str(path), im.size)
        return np.asarray(im.convert('RGB')).copy()


def grey(a):
    return (a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114).astype(np.float32)


def frame_paths(tag, n):
    folder = FRAMES / tag
    result = [folder / f'{i:04d}.jpg' for i in range(n)]
    for path in result:
        assert path.is_file() and path.stat().st_size > 0, path
        assert path.with_name(path.stem + '_check.jpg').is_file(), path
    # Only exactly four-digit frame filenames are accepted; *_check never enters video.
    actual = sorted(x.name for x in folder.glob('*.jpg') if len(x.stem) == 4 and x.stem.isdigit())
    assert actual == [x.name for x in result], (tag, len(actual))
    return result


def capture_stability(paths):
    mismatches, records, digests, coarse = [], [], [], []
    previous = None
    for i, path in enumerate(paths):
        a = rgb(path)
        b = rgb(path.with_name(path.stem + '_check.jpg'))
        delta = np.abs(a.astype(np.int16) - b.astype(np.int16))
        if np.any(delta):
            mismatches.append(i)
        digest = hashlib.sha256(a.tobytes()).hexdigest()
        digests.append(digest)
        small = np.asarray(Image.fromarray(a).resize((240, 135), Image.Resampling.BOX), dtype=np.float32)
        coarse.append(small)
        records.append({'index': i, 'check_max_abs_255': int(delta.max()),
                        'check_mean_abs_255': float(delta.mean()),
                        'previous_mean_abs_255': None if previous is None else float(np.abs(small - previous).mean())})
        previous = small
    duplicates = [i for i in range(1, len(digests)) if digests[i] == digests[i-1]]
    return {'count': len(paths), 'main_check_pixel_mismatch_indices': mismatches,
            'adjacent_exact_duplicate_indices': duplicates, 'frames': records}, coarse


def fit_same_source(before, after, expected):
    """Fit independent scale and translation on same-source image pair, subpixel.

    after(x,y) = before((x-cx-dx)/scale+cx, (y-cy-dy)/scale+cy).
    The expected scale is only the initial guess; no regularization toward it.
    """
    source, target = grey(before), grey(after)
    gy, gx = np.gradient(source)
    yy, xx = np.mgrid[48:HEIGHT-48:7, 48:WIDTH-48:7].astype(np.float64)
    edge = np.hypot(gx[yy.astype(int), xx.astype(int)], gy[yy.astype(int), xx.astype(int)])
    mask = edge >= np.percentile(edge, 45)
    x, y = xx[mask], yy[mask]
    values = target[y.astype(int), x.astype(int)]
    cx, cy = (WIDTH-1)/2, (HEIGHT-1)/2

    def residual(p):
        s, dx, dy = p
        sx, sy = (x-cx-dx)/s+cx, (y-cy-dy)/s+cy
        return map_coordinates(source, [sy, sx], order=1, mode='nearest') - values

    fit = least_squares(residual, [expected, 0., 0.], bounds=([.99, -3., -3.], [1.04, 3., 3.]),
                        loss='soft_l1', f_scale=1.0, x_scale=[.01, 1., 1.],
                        diff_step=[1e-5, .01, .01], max_nfev=35,
                        ftol=1e-8, xtol=1e-8, gtol=1e-8)
    # finite differences at a zero translation need a nonzero absolute step;
    # scipy's relative default step is too small for float32 interpolation.
    def jacobian(p):
        columns = []
        for k, step in enumerate([1e-5, .02, .02]):
            plus, minus = p.copy(), p.copy()
            plus[k] += step
            minus[k] -= step
            columns.append((residual(plus)-residual(minus))/(2*step))
        return np.stack(columns, axis=1)
    fit = least_squares(residual, fit.x, jac=jacobian,
                        bounds=([.99, -3., -3.], [1.04, 3., 3.]),
                        loss='soft_l1', f_scale=1.0, x_scale=[.01, 1., 1.],
                        max_nfev=35, ftol=1e-8, xtol=1e-8, gtol=1e-8)
    errors = residual(fit.x)
    return {'scale': float(fit.x[0]), 'translation_x_pixels': float(fit.x[1]),
            'translation_y_pixels': float(fit.x[2]), 'fit_median_abs_255': float(np.median(np.abs(errors))),
            'fit_rms_255': float(np.sqrt(np.mean(errors**2))), 'sample_pixels': len(values),
            'converged': bool(fit.success)}


def book_qa():
    paths0, paths1 = frame_paths('书写_原版', 57), frame_paths('书写_缓推', 57)
    stability0, _ = capture_stability(paths0)
    stability1, _ = capture_stability(paths1)
    fits = []
    for i, (p0, p1) in enumerate(zip(paths0, paths1)):
        u = i/56
        expected = 1 + .02*(3*u*u-2*u*u*u)
        fit = fit_same_source(rgb(p0), rgb(p1), expected)
        fit.update(index=i, timeline_frame=60+i, expected_scale=expected,
                   scale_error=fit['scale']-expected)
        fits.append(fit)
        if (i+1) % 10 == 0:
            print('BOOK_FIT', i+1, 'scale', round(fit['scale'], 7), flush=True)
    scales = np.array([x['scale'] for x in fits])
    expected = np.array([x['expected_scale'] for x in fits])
    tx = np.array([x['translation_x_pixels'] for x in fits])
    ty = np.array([x['translation_y_pixels'] for x in fits])
    scale_error = scales-expected
    flags = []
    for label, st in [('before', stability0), ('after', stability1)]:
        if st['main_check_pixel_mismatch_indices']:
            flags.append(label+'_unstable_capture')
        if st['adjacent_exact_duplicate_indices']:
            flags.append(label+'_exact_duplicate_frames_review')
    if np.max(np.abs(scale_error)) > .00030:
        flags.append('scale_deviation_review')
    if np.max(np.hypot(tx, ty)) > .5:
        flags.append('center_translation_review')
    if np.min(np.diff(scales)) < -.00006:
        flags.append('scale_reversal_review')
    if np.max(np.abs(np.diff(tx))) > .35 or np.max(np.abs(np.diff(ty))) > .35:
        flags.append('subpixel_translation_jump_review')
    if any(not x['converged'] for x in fits):
        flags.append('registration_not_converged_review')
    if max(x['fit_median_abs_255'] for x in fits) > 3.:
        flags.append('registration_residual_review')
    identical = [i for i, (p0, p1) in enumerate(zip(paths0, paths1)) if p0.read_bytes() == p1.read_bytes()]
    data = {'status': 'passed_numeric' if not flags else 'review', 'flags': flags,
            'method': 'All 57 same-source native frame pairs; robust photometric scale/translation registration at original resolution. No optical motion is added to preview.',
            'expected': 'Fixed center 2% enlargement, smoothstep 3u^2-2u^3, u=frame/56',
            'estimated_first_last_scale': [float(scales[0]), float(scales[-1])],
            'max_abs_scale_error': float(np.max(np.abs(scale_error))),
            'max_center_equivalent_translation_pixels': float(np.max(np.hypot(tx, ty))),
            'maximum_translation_step_pixels': float(max(np.max(np.abs(np.diff(tx))), np.max(np.abs(np.diff(ty))))),
            'minimum_scale_step': float(np.min(np.diff(scales))),
            'maximum_scale_step': float(np.max(np.diff(scales))),
            'maximum_scale_error_step': float(np.max(np.abs(np.diff(scale_error)))),
            'maximum_second_difference_scale_error': float(np.max(np.abs(np.diff(scale_error, n=2)))),
            'before_after_byte_identical_indices': identical,
            'registration_limit': 'Tests added transform against same-source matching frames; source camera/hand motion remains present and is not classified as an added-transform defect.',
            'before_stability': stability0, 'after_stability': stability1, 'fits': fits}
    dump(qa_path('连续书写缓推配准QA'), data)
    return data


def preview_frame_qa():
    paths = frame_paths('配画试听', N)
    stability, coarse = capture_stability(paths)
    before = json.loads((WORK/'live_before_v14.json').read_text())
    track = next(x for x in before['snapshot']['video'] if x['track'] == 1)
    scenes = [dict(name=x['name'], start=x['start'], end=x['end']) for x in track['items']
              if x['start'] < START+N and x['end'] > START]
    cuts = [x['start']-START for x in scenes if START < x['start'] < START+N]
    for item in stability['frames']:
        item['timeline_frame'] = START+item['index']
        item['scene_cut'] = item['index'] in cuts
    deltas = np.array([x['previous_mean_abs_255'] or 0 for x in stability['frames']])
    scene_metrics, unexpected = [], []
    for scene in scenes:
        lo, hi = max(0, scene['start']-START), min(N, scene['end']-START)
        d = deltas[lo+1:hi]
        median = float(np.median(d)) if len(d) else 0
        threshold = max(10., median*8.)
        outliers = [int(i) for i in range(lo+1, hi) if deltas[i] > threshold]
        unexpected.extend(outliers)
        scene_metrics.append({**scene, 'first_preview_index': lo, 'end_preview_index_exclusive': hi,
                              'within_scene_mean_abs_median_255': median,
                              'within_scene_mean_abs_max_255': float(d.max()) if len(d) else 0,
                              'large_change_review_indices': outliers})
    flags = []
    if stability['main_check_pixel_mismatch_indices']:
        flags.append('unstable_capture')
    if stability['adjacent_exact_duplicate_indices']:
        flags.append('exact_duplicate_frames_review')
    if unexpected:
        flags.append('within_scene_change_review')
    data = {'status': 'passed_numeric' if not flags else 'review', 'flags': flags,
            'timeline_start_frame': START, 'end_frame_exclusive': START+N,
            'duration_seconds': N/FPS, 'fps': FPS, 'scene_cut_indices': cuts,
            'scene_cut_timeline_frames': [x+START for x in cuts],
            'scene_metrics': scene_metrics, 'stability': stability,
            'detection_limit': 'Exact adjacent duplicates and larger scene-internal frame changes are tested. Coarse frame differences cannot exclude all subtle local motion or subpixel jitter; added-transform isolation is supplied only by the same-source book registration.',
            'motion_6370_6420': 'These 50-frame shots are actual native outputs. See scene metrics and chronological contact sheets; no offline transform or interpolation is applied.'}
    dump(qa_path('连续配画帧稳定QA'), data)
    return data


def encode_preview():
    if FINAL and OUTPUT.exists():
        previous = json.loads((WORK/'连续书写缓推配准QA_v14.json').read_text())
        assert previous['status'] == 'review' and 'scale_deviation_review' in previous['flags']
        archive = OUTPUT.with_name(OUTPUT.stem+'_未激活样本.mp4')
        assert not archive.exists(), 'Refusing to overwrite archived failed preview'
        OUTPUT.rename(archive)
    assert not OUTPUT.exists(), 'Refusing to overwrite existing deliverable'
    temp = OUTPUT.with_name(OUTPUT.stem+'.partial.mp4')
    assert not temp.exists(), 'Refusing to overwrite prior partial artifact'
    paths = frame_paths('配画试听', N)
    info = sf.info(AUDIO)
    assert info.samplerate == SR and info.channels == 2 and info.subtype == 'PCM_24', info
    start_sample, wanted_samples = START*SR//FPS, N*SR//FPS
    with sf.SoundFile(AUDIO) as audio:
        audio.seek(start_sample)
        samples = audio.read(wanted_samples, dtype='float32', always_2d=True)
    assert len(samples) == wanted_samples
    with av.open(str(temp), 'w', format='mp4', options={'movflags': '+faststart'}) as container:
        video = container.add_stream('libx264', rate=FPS)
        video.width, video.height, video.pix_fmt = WIDTH, HEIGHT, 'yuv420p'
        video.options = {'crf': '18', 'preset': 'medium'}
        video.codec_context.time_base = Fraction(1, FPS)
        video.codec_context.color_primaries = 1
        video.codec_context.color_trc = 1
        video.codec_context.colorspace = 1
        video.codec_context.color_range = 1
        sound = container.add_stream('aac', rate=SR)
        sound.layout = 'stereo'
        sound.bit_rate = 192000
        sound.codec_context.time_base = Fraction(1, SR)
        container.metadata['comment'] = ('Actual native Resolve captures, timeline 253.4–263.8 s. '
            'Audio is fresh source-track offline reconstructed mix; not a native master-bus render.')
        for i, path in enumerate(paths):
            vf = av.VideoFrame.from_ndarray(rgb(path), format='rgb24')
            vf = vf.reformat(format='yuv420p', dst_colorspace='ITU709')
            vf.pts, vf.time_base = i, Fraction(1, FPS)
            for packet in video.encode(vf):
                container.mux(packet)
            alo, ahi = i*SR//FPS, (i+1)*SR//FPS
            # AAC accepts arbitrary input frame length and buffers to its frame size.
            af = av.AudioFrame.from_ndarray(np.ascontiguousarray(samples[alo:ahi].T),
                                            format='fltp', layout='stereo')
            af.sample_rate, af.pts, af.time_base = SR, alo, Fraction(1, SR)
            for packet in sound.encode(af):
                container.mux(packet)
            if (i+1) % 50 == 0:
                print('ENCODE_PREVIEW', i+1, flush=True)
        for packet in video.encode(None):
            container.mux(packet)
        for packet in sound.encode(None):
            # Signal the true final duration instead of counting AAC padding.
            if packet.pts is not None and packet.time_base == Fraction(1, SR):
                packet.duration = min(packet.duration, max(0, wanted_samples-packet.pts))
            container.mux(packet)
    temp.rename(OUTPUT)
    return samples


def validate_encoded(reference_audio):
    paths = frame_paths('配画试听', N)
    extract = PRE / ('配画预览抽帧_最终' if FINAL else '配画预览抽帧')
    extract.mkdir(exist_ok=True)
    chosen = [0, 20, 34, 35, 59, 84, 85, 109, 134, 159, 184, 209, 234, 259]
    vtimes, qualities = [], []
    with av.open(str(OUTPUT)) as container:
        vs = container.streams.video[0]
        ast = container.streams.audio[0]
        streams = {'video': {'codec': vs.codec_context.name, 'width': vs.width, 'height': vs.height,
                            'pix_fmt': vs.codec_context.format.name, 'average_rate': str(vs.average_rate),
                            'stream_duration': float(vs.duration*vs.time_base)},
                   'audio': {'codec': ast.codec_context.name, 'sample_rate': ast.codec_context.sample_rate,
                            'channels': ast.codec_context.channels,
                            'stream_duration': float(ast.duration*ast.time_base)}}
        for i, frame in enumerate(container.decode(video=0)):
            vtimes.append(float(frame.pts*frame.time_base))
            if i in chosen:
                decoded = frame.to_ndarray(format='rgb24')
                source = rgb(paths[i])
                mse = float(np.mean((source.astype(np.float32)-decoded.astype(np.float32))**2))
                qualities.append({'index': i, 'psnr_db': float(10*np.log10(255**2/max(mse, 1e-12)))})
                Image.fromarray(decoded).save(extract/f'{i:04d}.jpg', quality=95)
    audio = np.zeros_like(reference_audio)
    coverage = np.zeros(len(audio), dtype=bool)
    apts, trailing_samples = [], 0
    with av.open(str(OUTPUT)) as container:
        for frame in container.decode(audio=0):
            apts.append(float(frame.pts*frame.time_base))
            start = round(float(frame.pts*frame.time_base)*SR)
            block = frame.to_ndarray()
            if block.shape[0] == 2:
                block = block.T
            else:
                block = block.reshape(-1, 2)
            lo, hi = max(0, start), min(len(audio), start+len(block))
            if hi > lo:
                audio[lo:hi] = block[lo-start:hi-start]
                coverage[lo:hi] = True
            trailing_samples += max(0, start+len(block)-len(audio))
    # Limit cross-correlation to +/- 120ms. No resampling or time shift is applied.
    ref = reference_audio.mean(axis=1)
    dec = audio.mean(axis=1)
    correlations = correlate(dec, ref, method='fft')
    lags = correlation_lags(len(dec), len(ref))
    allowed = np.abs(lags) <= int(.12*SR)
    lag = int(lags[allowed][np.argmax(correlations[allowed])])
    similarity = float(np.dot(dec, ref)/(np.linalg.norm(dec)*np.linalg.norm(ref)+1e-12))
    flags = []
    if len(vtimes) != N or max(abs(t-i/FPS) for i, t in enumerate(vtimes)) > 1e-6:
        flags.append('video_count_or_timestamp_mismatch')
    if not np.all(coverage) or abs(lag) > 2:
        flags.append('audio_coverage_or_sync_mismatch')
    if abs(streams['video']['stream_duration']-N/FPS) > 1/FPS/100:
        flags.append('video_duration_mismatch')
    if abs(streams['audio']['stream_duration']-N/FPS) > 1/SR:
        flags.append('audio_duration_mismatch')
    result = {'status': 'passed_numeric' if not flags else 'review', 'flags': flags,
              'path': str(OUTPUT), 'source_native_timeline_range_seconds': [START/FPS, (START+N)/FPS],
              'source_audio': str(AUDIO), 'source_audio_start_sample': START*SR//FPS,
              'source_audio_sample_frames': len(reference_audio), 'audio_mix_provenance':
              'Fresh source-track offline reconstructed full mix; not a native master-bus render. No gain or routing changes in this preview.',
              'streams': streams, 'decoded_video_frames': len(vtimes),
              'first_last_video_pts_seconds': [vtimes[0], vtimes[-1]],
              'expected_end_seconds_exclusive': N/FPS,
              'audio_covered_samples': int(coverage.sum()), 'audio_first_pts_seconds': apts[0],
              'aac_trailing_decode_padding_samples_excluded_by_stream_duration': trailing_samples,
              'aac_padding_note': 'AAC has codec priming/frame padding. Container valid duration is 499200 samples; decoders may trim the final frame themselves or emit padded trailing samples. The PTS-aligned comparison is explicitly restricted to the intended valid sample range.',
              'aac_audio_correlation_lag_samples': lag,
              'aac_audio_zero_lag_normalized_correlation': similarity,
              'visual_compression_psnr_samples': qualities,
              'decoded_frame_extraction_folder': str(extract),
              'audition_status': 'not_auditioned; timestamp, correlation and sample coverage verified only'}
    dump(qa_path('配画预览编码QA'), result)
    return result


def contact_sheets():
    paths = frame_paths('配画试听', N)
    sheet_paths = []
    # Every 5th native frame in 6370/6420 shots: explicit chronological samples.
    groups = {'6370': range(35, 85, 5), '6420': range(85, 135, 5),
              'preview': [0, 34, 35, 59, 84, 85, 109, 134, 159, 184, 209, 234, 259]}
    for label, indices in groups.items():
        indices = list(indices)
        sheet = Image.new('RGB', (4*480, ((len(indices)+3)//4)*294), '#151515')
        draw = ImageDraw.Draw(sheet)
        for j, i in enumerate(indices):
            with Image.open(paths[i]) as source:
                thumb = source.convert('RGB').resize((480, 270), Image.Resampling.LANCZOS)
            x, y = (j%4)*480, (j//4)*294
            sheet.paste(thumb, (x, y))
            draw.text((x+8, y+272), f'frame {START+i} / +{i/FPS:.2f}s', fill='white')
        path = PRE/f'连续运动核验_{label}_总览{"_最终" if FINAL else ""}.jpg'
        assert not path.exists(), path
        sheet.save(path, quality=94)
        sheet_paths.append(str(path))
    return sheet_paths


def main():
    global FINAL
    parser = argparse.ArgumentParser()
    parser.add_argument('--book-only', action='store_true')
    parser.add_argument('--skip-book', action='store_true')
    parser.add_argument('--final', action='store_true', help='Write distinct final reports; archive the known failed initial preview only.')
    args = parser.parse_args()
    FINAL = args.final
    if args.skip_book:
        book = json.loads(qa_path('连续书写缓推配准QA').read_text())
    else:
        book = book_qa()
    if args.book_only:
        print(json.dumps({'book_status': book['status'], 'flags': book['flags']}, ensure_ascii=False))
        return
    preview = preview_frame_qa()
    assert not book['before_stability']['main_check_pixel_mismatch_indices']
    assert not book['after_stability']['main_check_pixel_mismatch_indices']
    assert not preview['stability']['main_check_pixel_mismatch_indices']
    reference = encode_preview()
    encoded = validate_encoded(reference)
    sheets = contact_sheets()
    dump(qa_path('连续运动与配画预览总验收'), {
        'status': 'pending_visual_review', 'book': book['status'], 'frames': preview['status'],
        'encoding': encoded['status'], 'flags': book['flags']+preview['flags']+encoded['flags'],
        'output': str(OUTPUT), 'contact_sheets': sheets,
        'scope': 'Read-only source/native captures. No Resolve attachment. Outputs are preview and QA artifacts only.',
        'audio_note': encoded['audio_mix_provenance']})
    print('V14_OFFLINE_QA_ENCODE_COMPLETE', OUTPUT, flush=True)


if __name__ == '__main__':
    main()
