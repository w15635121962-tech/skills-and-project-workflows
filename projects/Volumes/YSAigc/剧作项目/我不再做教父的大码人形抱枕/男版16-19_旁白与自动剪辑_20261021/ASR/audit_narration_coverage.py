#!/usr/bin/env python3
"""Compare completed blind ASR with immutable original narration after recognition.

This script does not invoke an ASR model, modify audio, or force source words into
recognition. Exact token matches receive observed source-relative word anchors;
mismatches remain explicit and require listening/secondary recognition review.
"""
from __future__ import annotations

import argparse
from collections import Counter
import datetime as dt
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import re

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
MANIFEST = BASE / '准备/narration_manifest.json'
TOKEN = re.compile(r"[A-Za-z0-9]+(?:[’'\-][A-Za-z0-9]+)*")


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def tokens(text):
    return [{'text': m.group(), 'normalized': m.group().lower().replace('’', "'"), 'char_start': m.start(), 'char_end_exclusive': m.end()} for m in TOKEN.finditer(text)]


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--episodes', type=int, nargs='+', default=[16, 17, 18, 19])
    ap.add_argument('--only-existing', action='store_true')
    ap.add_argument('--selection-file', type=Path, help='Explicit take selection overrides, without changing source narration manifest.')
    args = ap.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    assert digest(manifest['source_docx']) == manifest['source_docx_sha256'], 'Source DOCX changed'
    groups = [g for g in manifest['groups'] if g['episode'] in args.episodes]
    assert groups and set(args.episodes) <= {16, 17, 18, 19}
    episodes = {e['episode']: e for e in manifest['episodes']}
    selections = {}
    if args.selection_file:
        selection_doc = json.loads(args.selection_file.read_text(encoding='utf-8'))
        selections = {s['logical_basename']: s for s in selection_doc['selections']}
    pending, reports, timing_maps = [], [], []
    for group in groups:
        selected = selections.get(group['basename'])
        audio = Path(selected['selected_audio_path'] if selected else group['planned_audio_path'])
        if selected:
            assert digest(audio) == selected['selected_audio_sha256'], 'Selected take hash mismatch'
        path = OUT / 'raw_large-v3-turbo' / f"EP{group['episode']}" / 'narration' / (audio.stem + '.json')
        if selected and selected.get('preferred_blind_asr_json'):
            path = Path(selected['preferred_blind_asr_json'])
        if not path.is_file() or not audio.is_file():
            pending.append({'basename': group['basename'], 'audio_exists': audio.is_file(), 'blind_asr_exists': path.is_file()})
            continue
        raw = json.loads(path.read_text(encoding='utf-8'))
        errors = []
        if digest(audio) != raw['source_sha256']:
            errors.append('ASR source hash mismatch')
        if not raw['blind_transcription'] or raw.get('expected_script_supplied_to_model') is not False or raw.get('decode_parameters', {}).get('initial_prompt') is not None:
            errors.append('Blind transcription provenance invalid')
        if raw.get('speed') != 1.0:
            errors.append('Source speed is not documented as 100 percent')
        expected = group['generation_text']
        assert Path(group['text_file']).read_text(encoding='utf-8') == expected
        assert hashlib.sha256(expected.encode('utf-8')).hexdigest() == group['generation_text_sha256']
        ref = tokens(expected)
        observed = []
        for i, word in enumerate(raw['words']):
            if word['start'] < 0 or word['end'] < word['start'] or word['end'] > raw['decoded_duration_seconds'] + .1:
                errors.append('Observed word time outside decoded source bounds')
            for token in tokens(word['word']):
                observed.append({**token, 'source_word_index': i, 'word': word['word'], 'source_start_seconds': word['start'], 'source_end_seconds': word['end'], 'probability': word.get('probability')})
        if not observed:
            errors.append('No observed word tokens')
        if any(float(b['start']) < float(a['start']) for a, b in zip(raw['words'], raw['words'][1:])):
            errors.append('Nonmonotonic observed word starts')
        a = [t['normalized'] for t in ref]
        b = [t['normalized'] for t in observed]
        matcher = SequenceMatcher(None, a, b, autojunk=False)
        mapping, differences, counts = {}, [], Counter()
        for tag, ai, az, bi, bz in matcher.get_opcodes():
            if tag == 'equal':
                for x, y in zip(range(ai, az), range(bi, bz)):
                    mapping[x] = y
                counts['exact_match'] += az - ai
            else:
                counts[tag + '_expected_words'] += az - ai
                counts[tag + '_observed_words'] += bz - bi
                differences.append({'operation': tag, 'expected_token_start': ai, 'expected_token_end_exclusive': az,
                                    'observed_token_start': bi, 'observed_token_end_exclusive': bz,
                                    'expected': ' '.join(t['text'] for t in ref[ai:az]),
                                    'observed': ' '.join(t['text'] for t in observed[bi:bz]),
                                    'observed_word_indices': list(dict.fromkeys(t['source_word_index'] for t in observed[bi:bz])),
                                    'observed_start_seconds': observed[bi]['source_start_seconds'] if bi < len(observed) else None,
                                    'observed_end_seconds': observed[bz - 1]['source_end_seconds'] if bz > bi else None,
                                    'review_status': 'unreviewed_difference_do_not_silently_correct'})
        token_map = []
        for i, token in enumerate(ref):
            native = observed[mapping[i]] if i in mapping else None
            token_map.append({**token, 'expected_token_index': i, 'exact_blind_asr_match': native is not None,
                              'source_word_index': native['source_word_index'] if native else None,
                              'source_start_seconds': native['source_start_seconds'] if native else None,
                              'source_end_seconds': native['source_end_seconds'] if native else None,
                              'probability': native['probability'] if native else None})
        paragraph_map, cursor = [], 0
        for record in episodes[group['episode']]['original_paragraphs_and_retained_narration']:
            if record['docx_paragraph'] not in group['source_docx_paragraphs'] or not record['narration_retained_text'].strip():
                continue
            text = record['narration_retained_text']
            pos = expected.find(text, cursor)
            assert pos >= 0, ('Source paragraph not found in generation text', group['basename'], record['docx_paragraph'])
            end = pos + len(text)
            cue_words = [w for w in token_map if w['char_start'] >= pos and w['char_end_exclusive'] <= end]
            matched = [w for w in cue_words if w['exact_blind_asr_match']]
            paragraph_map.append({'docx_paragraph': record['docx_paragraph'], 'source_text': text,
                                  'generation_char_start': pos, 'generation_char_end_exclusive': end,
                                  'expected_words': len(cue_words), 'matched_words': len(matched),
                                  'all_words_exact_blind_asr_match': len(cue_words) == len(matched),
                                  'observed_first_matching_word_start_seconds': matched[0]['source_start_seconds'] if matched else None,
                                  'observed_last_matching_word_end_seconds': matched[-1]['source_end_seconds'] if matched else None,
                                  'boundary_anchor_is_partial_if_words_mismatch': len(cue_words) != len(matched)})
            cursor = end
        quality = raw.get('quality_flags', [])
        reports.append({'episode': group['episode'], 'narration_sequence': group['narration_sequence'],
                        'basename': group['basename'], 'actual_audio_basename': audio.stem, 'source_path': str(audio), 'source_sha256': raw['source_sha256'],
                        'blind_asr_json': str(path), 'expected_text': expected, 'blind_asr_text': raw['text'],
                        'expected_token_count': len(ref), 'observed_token_count': len(observed),
                        'strict_normalized_equal': a == b, 'exact_matched_token_count': len(mapping),
                        'exact_match_fraction': len(mapping) / len(ref) if ref else 1,
                        'difference_counts': dict(counts), 'differences': differences,
                        'quality_flags': quality, 'decoded_duration_seconds': raw['decoded_duration_seconds'],
                        'source_timing_valid': not errors, 'errors': errors,
                        'human_listening_verified': False,
                        'status': 'blind_asr_lexically_exact' if a == b and not errors else 'review_required'})
        timing_maps.append({'episode': group['episode'], 'basename': group['basename'], 'actual_audio_basename': audio.stem, 'source_path': str(audio),
                            'source_sha256': raw['source_sha256'], 'timing_basis': 'Original 100 percent speed source-relative seconds',
                            'source_words': raw['words'], 'expected_tokens_with_exact_match_anchors': token_map,
                            'source_paragraph_anchors': paragraph_map,
                            'mismatched_expected_words_are_not_forced_into_audio': True})

    result = {'checked_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
              'manifest_path': str(MANIFEST), 'manifest_sha256': digest(MANIFEST),
              'take_selection_file': str(args.selection_file.resolve()) if args.selection_file else None,
              'analysis_after_blind_recognition': True, 'audio_or_script_modified': False,
              'source_relative_word_times_not_timeline_times': True,
              'normalization': 'case, curly apostrophe and punctuation only; no proper-name replacement, number expansion, stemming or semantic substitution',
              'selected_episodes': args.episodes, 'expected_files': len(groups), 'completed_files': len(reports),
              'pending_files': pending, 'expected_words': sum(r['expected_token_count'] for r in reports),
              'observed_tokens': sum(r['observed_token_count'] for r in reports),
              'exact_matched_tokens': sum(r['exact_matched_token_count'] for r in reports),
              'all_downloads_and_asr_present': not pending,
              'all_present_source_hashes_and_timings_valid': all(r['source_timing_valid'] for r in reports),
              'all_present_lexically_exact': bool(reports) and all(r['strict_normalized_equal'] for r in reports),
              'human_listening_verified': False, 'files': reports,
              'review_note': 'Name/number/contraction differences remain flagged. A high match fraction alone does not prove complete or accurate narration. Check every non-equal span against audio or independent blind recognition.',
              'synchronous_dialogue_anchor_path': str(BASE / '准备/旁白段内同期对白插入点.json')}
    suffix = '_采用版本' if args.selection_file else ''
    save(OUT / ('旁白原文覆盖核验' + suffix + '.json'), result)
    save(OUT / ('旁白逐词与源段落锚点' + suffix + '.json'), {'files': timing_maps, 'pending_files': pending})
    print(json.dumps({k: result[k] for k in ['expected_files', 'completed_files', 'expected_words', 'observed_tokens', 'exact_matched_tokens', 'all_downloads_and_asr_present', 'all_present_source_hashes_and_timings_valid', 'all_present_lexically_exact']}, ensure_ascii=False, indent=2))
    for row in reports:
        if row['status'] == 'review_required':
            print(json.dumps({'basename': row['basename'], 'differences': row['differences'], 'errors': row['errors']}, ensure_ascii=False))
    if pending and not args.only_existing:
        raise SystemExit(2)
    if any(r['errors'] for r in reports):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
