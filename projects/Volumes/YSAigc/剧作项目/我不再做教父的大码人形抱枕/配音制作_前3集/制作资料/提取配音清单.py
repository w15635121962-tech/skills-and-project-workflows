#!/usr/bin/env python3
"""Extract full English source paragraphs for Episodes 1-3 without rewriting."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[’'\-][A-Za-z0-9]+)*")
SOURCES = [
    ('女版', 'female', '大码', ROOT / '完整剧本/我不再做教父的大码人形抱枕EN.docx', ROOT / '完整剧本/我不再做教父的大码人形抱枕.docx'),
    ('性转版', 'gender_swap', '大码', ROOT / '性转版/没有你我睡不着（大码性转）-EN.docx', ROOT / '性转版/没有你我睡不着（大码性转）(1).docx'),
]


def paragraphs(path):
    with ZipFile(path) as z:
        root = ET.fromstring(z.read('word/document.xml'))
    assert not root.findall('.//w:tbl', NS), 'Tables require ordered extraction'
    assert not root.findall('.//w:ins', NS), 'Tracked insertions need review'
    assert not root.findall('.//w:del', NS), 'Tracked deletions need review'
    assert not root.findall('.//w:txbxContent', NS), 'Text boxes need review'
    result = []
    for p in root.findall('./w:body/w:p', NS):
        chunks = []
        for el in p.iter():
            if el.tag == '{%s}t' % NS['w']:
                chunks.append(el.text or '')
            elif el.tag == '{%s}tab' % NS['w']:
                chunks.append('\t')
            elif el.tag in ('{%s}br' % NS['w'], '{%s}cr' % NS['w']):
                chunks.append('\n')
        result.append(''.join(chunks))
    return result


summaries = []
for label, key, prefix, source, chinese in SOURCES:
    paras = paragraphs(source)
    episodes = []
    episode = None
    exclusions = []
    records = []
    raw_first3 = []
    for index, raw in enumerate(paras, 1):
        text = raw.strip()
        match = re.fullmatch(r'(?:Episode\s+)?(\d{1,2})', text)
        if match:
            number = int(match[1])
            if number == 4:
                break
            episode = number
            if number <= 3:
                episodes.append({'episode': number, 'source_header': text, 'source_header_paragraph': index, 'segments': []})
                raw_first3.append((index, raw))
            continue
        if episode not in (1, 2, 3):
            continue
        raw_first3.append((index, raw))
        if not text:
            continue
        if text.startswith('【'):
            exclusions.append({'episode': episode, 'source_paragraph': index, 'source_text': raw, 'reason': 'non-spoken visual direction'})
            continue
        if not re.search(r'[A-Za-z]', text):
            exclusions.append({'episode': episode, 'source_paragraph': index, 'source_text': raw, 'reason': 'non-spoken scene divider'})
            continue
        segment_index = len(episodes[-1]['segments']) + 1
        name = f'{prefix}{episode:02d}-01-{segment_index:02d}'
        words = len(WORD_RE.findall(text))
        segment = {
            'name': name,
            'version': key,
            'version_label': label,
            'episode': episode,
            'paragraph': segment_index,
            'batch': 1,
            'take': 1,
            'source_paragraph': index,
            'source_text': raw,
            'text': text,
            'character_count': len(text),
            'word_count': words,
            'estimated_seconds_at_2_5_words_per_second': round(words / 2.5, 1),
            'status': 'prepared_not_generated',
        }
        assert segment['text'] == paras[index - 1].strip()
        episodes[-1]['segments'].append(segment)
        records.append(segment)
    assert [e['episode'] for e in episodes] == [1, 2, 3]
    for e in episodes:
        e['segment_count'] = len(e['segments'])
        e['word_count'] = sum(s['word_count'] for s in e['segments'])
        e['estimated_seconds_at_2_5_words_per_second'] = round(e['word_count'] / 2.5, 1)
    data = {
        'version': key,
        'version_label': label,
        'english_source_path': str(source),
        'english_source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'chinese_verification_source_path': str(chinese),
        'scope': 'Complete English Episodes 1-3 according to this version own source headings',
        'extraction_rules': [
            'Keep all English narration and quoted dialogue verbatim.',
            'One original English source paragraph per audio file.',
            'Trim only leading/trailing whitespace for the generation text; source_text retains exact extracted source.',
            'Exclude episode headings, Chinese visual directions, blank paragraphs and scene dividers from speech.',
            'Do not replace English wording with Chinese-source wording.',
        ],
        'naming': f'{prefix}EE-01-PP; EE episode, middle field fixed 01, PP original spoken paragraph. Same names stay separated in 女版 and 性转版 folders.',
        'word_count_method': "English/number tokens, internal apostrophe or hyphen retained in one word; punctuation excluded.",
        'duration_note': 'Text-based 2.5 words/s estimate only; actual duration requires generated audio.',
        'total_segment_count': len(records),
        'total_word_count': sum(s['word_count'] for s in records),
        'episodes': episodes,
        'excluded_nonspoken_paragraphs': exclusions,
    }
    target = OUT / label
    target.mkdir(exist_ok=True)
    (target / f'{label}_前3集_配音清单.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    with (target / f'{label}_前3集_配音清单.txt').open('w', encoding='utf-8') as f:
        for s in records:
            f.write(f'[{s["name"]}]\n{s["text"]}\n\n')
    with (target / f'{label}_前3集_原文逐段核验.txt').open('w', encoding='utf-8') as f:
        for index, raw in raw_first3:
            f.write(f'[{index:04d}] {raw}\n')
    for e in episodes:
        (target / f'{label}_第{e["episode"]:02d}集_纯英文全文.txt').write_text('\n'.join(s['text'] for s in e['segments']) + '\n', encoding='utf-8')
    # Independently verify generation-text coverage against every source spoken paragraph.
    expected = [(i, p.strip()) for i, p in raw_first3 if p.strip() and re.search('[A-Za-z]', p.strip()) and not p.strip().startswith('【') and not re.fullmatch(r'(?:Episode\s+)?\d{1,2}', p.strip())]
    actual = [(s['source_paragraph'], s['text']) for s in records]
    assert expected == actual, 'Source coverage mismatch'
    summaries.append({
        'version_label': label,
        'source': str(source),
        'source_sha256': data['english_source_sha256'],
        'manifest': str(target / f'{label}_前3集_配音清单.json'),
        'segment_count': len(records),
        'word_count': data['total_word_count'],
        'episodes': [{k:v for k,v in e.items() if k != 'segments'} for e in episodes],
        'source_coverage_verified': True,
    })
(OUT / '前3集_提取核验汇总.json').write_text(json.dumps(summaries, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(summaries, ensure_ascii=False, indent=2))
