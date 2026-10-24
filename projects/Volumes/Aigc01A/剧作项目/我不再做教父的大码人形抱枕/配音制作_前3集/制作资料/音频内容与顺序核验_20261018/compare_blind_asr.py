#!/usr/bin/env python3
"""Compare independent ASR checkpoints to the source-verified narration map.

Reads data only. A mismatch is a review candidate, never an automatic TTS error.
"""
import argparse
import difflib
import hashlib
import json
import re
import unicodedata
from pathlib import Path


def words(text):
    text = unicodedata.normalize('NFKC', text).casefold()
    text = text.replace('’', "'").replace('‘', "'")
    # Keep accented letters in foreign names (e.g. Vareña) as one token.
    # Do not strip accents or silently equate different name spellings.
    return re.findall(r"[^\W_]+(?:'[^\W_]+)*", text)


def alignment(ref, hyp):
    costs = [[0] * (len(hyp) + 1) for _ in range(len(ref) + 1)]
    for i in range(len(ref) + 1):
        costs[i][0] = i
    for j in range(len(hyp) + 1):
        costs[0][j] = j
    for i, a in enumerate(ref, 1):
        for j, b in enumerate(hyp, 1):
            costs[i][j] = min(costs[i-1][j] + 1,
                              costs[i][j-1] + 1,
                              costs[i-1][j-1] + (a != b))
    i, j = len(ref), len(hyp)
    ops = []
    while i or j:
        if i and j and costs[i][j] == costs[i-1][j-1] + (ref[i-1] != hyp[j-1]):
            if ref[i-1] != hyp[j-1]:
                ops.append({'type': 'substitute', 'expected': ref[i-1],
                            'heard_asr': hyp[j-1], 'reference_index': i-1,
                            'hypothesis_index': j-1})
            i -= 1
            j -= 1
        elif i and costs[i][j] == costs[i-1][j] + 1:
            ops.append({'type': 'delete', 'expected': ref[i-1],
                        'reference_index': i-1, 'hypothesis_index': j})
            i -= 1
        else:
            ops.append({'type': 'insert', 'heard_asr': hyp[j-1],
                        'reference_index': i, 'hypothesis_index': j-1})
            j -= 1
    return costs[-1][-1], list(reversed(ops))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--audit-dir', type=Path, default=Path(__file__).parent)
    ap.add_argument('--transcripts', type=Path)
    ap.add_argument('--output-stem', default='第一轮盲转写逐词对比')
    args = ap.parse_args()
    audit = args.audit_dir
    checkpoints = args.transcripts or audit / 'ASR/transcripts_small.en'
    expected = json.loads((audit / '核验输入清单.json').read_text(encoding='utf-8'))['clips']
    sources = {r['name']: words(r['expected_text']) for r in expected}
    observed = {}
    for f in sorted(checkpoints.rglob('*.json')):
        d = json.loads(f.read_text(encoding='utf-8'))
        if 'name' not in d or 'text' not in d:
            continue
        if d['name'] in observed:
            raise RuntimeError('Duplicate checkpoint name: ' + d['name'])
        observed[d['name']] = (d, f)
    rows = []
    missing = []
    for r in expected:
        name = r['name']
        if name not in observed:
            missing.append(name)
            continue
        d, f = observed[name]
        actual_sha = hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()
        if actual_sha != r['sha256'] or d.get('sha256') != r['sha256']:
            raise RuntimeError('Audio/checkpoint SHA mismatch: ' + name)
        hyp, ref = words(d['text']), sources[name]
        edits, ops = alignment(ref, hyp)
        comparisons = []
        for other, other_ref in sources.items():
            other_edits, _ = alignment(other_ref, hyp)
            comparisons.append({'name': other,
                                'normalized_edit_rate': other_edits / max(len(other_ref), len(hyp), 1),
                                'word_edits': other_edits})
        comparisons.sort(key=lambda x: (x['normalized_edit_rate'], x['word_edits'], x['name']))
        exact_candidates = [c['name'] for c in comparisons if c['word_edits'] == 0]
        rows.append({**r, 'checkpoint': str(f), 'asr_text': d['text'],
                     'reference_word_count': len(ref), 'asr_word_count': len(hyp),
                     'word_edits': edits, 'word_error_rate': edits / max(len(ref), 1),
                     'normalized_words_identical': ref == hyp, 'difference_operations': ops,
                     'exact_source_candidates': exact_candidates,
                     'best_source_candidates': comparisons[:3],
                     'best_candidate_is_expected_or_tied': any(c['name'] == name and c['normalized_edit_rate'] == comparisons[0]['normalized_edit_rate'] for c in comparisons),
                     'review_status': 'ASR_WORD_MATCH' if ref == hyp else 'NEEDS_REVIEW_NOT_PROVEN_ERROR'})
    out = {'method': 'Blind ASR, word edit alignment and all-47-source cross-match; punctuation/case ignored, no semantic rewriting.',
           'expected_count': len(expected), 'transcribed_count': len(rows),
           'missing': missing,
           'asr_word_match_count': sum(r['normalized_words_identical'] for r in rows),
           'requires_review_count': sum(not r['normalized_words_identical'] for r in rows),
           'rows': rows}
    path = audit / (args.output_stem + '.json')
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    report = [f"转写覆盖：{len(rows)}/{len(expected)}；规范大小写/标点后逐词相同：{out['asr_word_match_count']}；需复核：{out['requires_review_count']}",
              '转写差异不等于实际错读，待第二识别器/音频复核。', '']
    for r in rows:
        report.extend([r['name'] + ' — ' + r['review_status'],
                       '原文：' + r['expected_text'], 'ASR：' + r['asr_text'],
                       '差异：' + json.dumps(r['difference_operations'], ensure_ascii=False),
                       '跨47组最佳匹配：' + json.dumps(r['best_source_candidates'], ensure_ascii=False), ''])
    (audit / (args.output_stem + '.txt')).write_text('\n'.join(report), encoding='utf-8')
    print(json.dumps({k: v for k, v in out.items() if k != 'rows'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
