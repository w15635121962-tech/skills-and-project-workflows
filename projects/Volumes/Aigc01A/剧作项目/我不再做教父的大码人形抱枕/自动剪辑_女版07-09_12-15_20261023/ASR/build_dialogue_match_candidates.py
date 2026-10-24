"""Compare completed blind observations against canonical source AFTER recognition.

This does not rerun recognition or feed any source text into either ASR model.
Candidate timing is approximate until words and cuts are independently checked.
"""
from pathlib import Path
import difflib
import json
import re

HERE = Path(__file__).resolve().parent
TASK = HERE.parent
EPISODE_MAP = {7:7, 8:8, 9:9, 12:11, 13:12, 14:13, 15:14}
paragraphs = json.loads((TASK / '\u539f\u6587\u9010\u6bb5.json').read_text(encoding='utf-8'))
index = json.loads((HERE / '\u8f6c\u5f55\u7d22\u5f15.json').read_text(encoding='utf-8'))
secondary = json.loads((HERE / '\u7591\u4f3c\u5e7b\u89c9_\u4e8c\u6b21\u76f2\u8bc6\u522b.json').read_text(encoding='utf-8'))
diagnostic = {r['source_path']:r for r in secondary['files']}
authority = json.loads((TASK / '\u5267\u672c\u987a\u5e8f\u4f9d\u636e.json').read_text(encoding='utf-8'))
classified = {r['docx_paragraph_1_based']:r['kind'] for ep in authority['episodes'] for r in ep['ordered_source_entries']}

def words(text):
    return re.findall(r"[a-z0-9]+(?:['\u2019][a-z0-9]+)*", text.lower())

def norm(word):
    token = re.sub(r'[^a-z0-9]', '', word.lower())
    aliases = {'mateo':'matteo', 'metello':'matteo', 'mattelo':'matteo', 'mattelio':'matteo',
               'matelo':'matteo', 'mateel':'matteo', 'alicia':'alessia', 'alesia':'alessia',
               'belandi':'bellandi', 'belandis':'bellandis'}
    return aliases.get(token, token)

units = []
chapter = None
for para, text in enumerate(paragraphs, 1):
    heading = re.fullmatch(r'Episode (\d+)', text.strip())
    if heading:
        chapter = int(heading[1])
    if chapter not in set(EPISODE_MAP.values()):
        continue
    if para in classified and classified[para] != 'character_dialogue':
        continue
    for quote in re.findall(r'"([^"\n]+)"', text):
        tokens = [norm(w) for w in words(quote)]
        if tokens:
            units.append(dict(source_episode=chapter, docx_paragraph=para,
                              original_text=quote.strip(), canonical_tokens=tokens))

def best_window(canonical, observed):
    target = [norm(x['word']) for x in observed]
    best = None
    count = len(canonical)
    for start in range(len(target)):
        for length in range(max(1, count-3), min(len(target)-start, count+3)+1):
            part = target[start:start+length]
            ratio = difflib.SequenceMatcher(None, canonical, part, autojunk=False).ratio()
            exact = part == canonical
            score = (ratio, exact, -abs(length-count))
            if best is None or score > best[0]:
                best = (score, start, start+length)
    return best

all_reports = []
for local_ep, source_ep in EPISODE_MAP.items():
    files = []
    for row in index['files']:
        if row['episode'] == local_ep and row['kind'] == 'video':
            raw = json.loads(Path(row['json_path']).read_text(encoding='utf-8'))
            files.append((row, raw))
    reports = []
    for unit in [u for u in units if u['source_episode'] == source_ep]:
        candidates = []
        for row, raw in files:
            best = best_window(unit['canonical_tokens'], raw['words'])
            if best is None:
                continue
            score, start, stop = best
            threshold = 1.0 if len(unit['canonical_tokens']) <= 2 else .74
            if score[0] < threshold:
                continue
            selected = raw['words'][start:stop]
            candidate = dict(source_path=row['source_path'], filename=Path(row['source_path']).name,
                             lexical_match_ratio=round(score[0], 6), exact_normalized_tokens=score[1],
                             start_seconds=selected[0]['start'], end_seconds=selected[-1]['end'],
                             observed_text=' '.join(w['word'].strip() for w in selected),
                             observed_word_indices=list(range(start, stop)),
                             observed_words=selected, raw_json=row['json_path'],
                             suspected_hallucination_diagnostic=diagnostic.get(row['source_path']),
                             human_listening_verified=False)
            candidates.append(candidate)
        candidates.sort(key=lambda x:(-x['lexical_match_ratio'], x['filename'], x['start_seconds']))
        reports.append(dict(**unit, candidates=candidates,
                            status='OBSERVED_LEXICAL_CANDIDATE_NOT_FINAL_CUT' if candidates else 'NO_MATCH_CANDIDATE',
                            human_listening_verified=False))
    report = dict(local_episode=local_ep, source_episode=source_ep,
                  mapping_basis='Actual blind video and VO story content; local EP12-15 is source Episode11-14.',
                  dialogue_units=reports,
                  missing_candidates=[r['original_text'] for r in reports if not r['candidates']],
                  no_initial_prompt_or_hotwords_supplied=True,
                  timing_is_source_relative_seconds=True,
                  human_listening_verified=False,
                  caveat='Lexical alignment is not a completed audio/content audit; source spelling and actual audible delivery must be checked before final cut/subtitles.')
    path = HERE / ('EP%02d_dialogue_candidates.json' % local_ep)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = ['# EP%02d dialogue candidates (source Episode %d)' % (local_ep, source_ep), '',
             'Blind ASR was completed before reading source text. Candidate times below are source-relative seconds; not final timeline cuts or human listening approval.', '']
    for r in reports:
        lines += ['## P%d: %s' % (r['docx_paragraph'], r['original_text']), '']
        if not r['candidates']:
            lines += ['NO MATCH CANDIDATE; investigate delivery/missing audio.', '']
        for c in r['candidates']:
            lines += ['- %s | %.3f-%.3fs | lexical %.3f | %s%s' %
                      (c['filename'], c['start_seconds'], c['end_seconds'], c['lexical_match_ratio'],
                       c['observed_text'], ' | SUSPECTED HALLUCINATION DIAGNOSTIC' if c['suspected_hallucination_diagnostic'] else '')]
        lines += ['']
    (HERE / ('EP%02d_dialogue_candidates.md' % local_ep)).write_text('\n'.join(lines), encoding='utf-8')
    all_reports.append(report)
(HERE / '\u5bf9\u767d\u6e90\u65f6\u7801\u5019\u9009\u603b\u7d22\u5f15.json').write_text(json.dumps(dict(episodes=all_reports, human_listening_verified=False), ensure_ascii=False, indent=2), encoding='utf-8')
