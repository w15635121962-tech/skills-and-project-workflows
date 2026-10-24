#!/usr/bin/env python3
"""Export and correct Resolve-generated captions, retaining an audit of edits."""
import copy
import json
import re
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent.parent
FPS = 24


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def plain(text):
    return re.sub(r'\s+', ' ', text).strip()


def stamp(frame):
    ms = round(frame * 1000 / FPS)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'


def wrap(text, width=36):
    lines = textwrap.wrap(text, width=width, break_long_words=False,
                          break_on_hyphens=False)
    if len(lines) > 2:
        # Native Resolve may emit >72 characters. Preserve the spoken words;
        # a maximum of 42 characters per line is preferable to three lines.
        lines = textwrap.wrap(text, width=42, break_long_words=False,
                              break_on_hyphens=False)
    return lines


def write_srt(path, cues):
    path.parent.mkdir(parents=True, exist_ok=True)
    parts = []
    for i, cue in enumerate(cues, 1):
        parts.append(f"{i}\n{stamp(cue['start'])} --> {stamp(cue['end'])}\n" +
                     '\n'.join(wrap(cue['text'])))
    path.write_text('\n\n'.join(parts) + '\n', encoding='utf-8')


snapshot = read(HERE / '字幕制作前快照.json')
native = {d['name']: d for d in
          [read(f) for f in HERE.glob('原生生成*.json')]}
assert len(native) == 6
all_results = []
for timeline in snapshot['timelines']:
    name = timeline['name']
    data = native[name]
    original = [copy.deepcopy(c) for t in data['tracks'] for c in t['cues']]
    assert original and timeline['fps'] == FPS
    for i, cue in enumerate(original, 1):
        cue['text'] = plain(cue['text'])
        cue['native_indices'] = [i]
    write_srt(HERE / '原生识别未校正SRT' / f'{name}.srt', original)
    cues = copy.deepcopy(original)
    changes = []

    def change(cue, text, reason):
        if cue['text'] != text:
            changes.append({'native_indices': cue['native_indices'],
                            'before': cue['text'], 'after': text,
                            'reason': reason})
            cue['text'] = text

    female = '_女版_' in name
    ep = int(re.search(r'EP(\d+)', name).group(1))
    for cue in cues:
        text = cue['text']
        # Proper names are editorial spellings, not a claim to repair audio.
        text = re.sub(r'\bMateo\b', 'Matteo', text)
        text = re.sub(r'\b(?:Bellendi|Belandi|Belandis)\b',
                      lambda m: 'Bellandis' if m[0].endswith('s') else 'Bellandi', text)
        if not female:
            text = re.sub(r'\b(?:Victoria|Vitoria)\b', 'Vittoria', text)
        if female and ep == 1 and cue['native_indices'] == [1]:
            text = text.replace('Donmeter Bellandi', 'don Matteo Bellandi')
        text = text.replace('black tea', 'black tee')
        text = text.replace('Blackwood Air', 'Blackwood heir')
        change(cue, text, '按原稿统一人物/地点书写或同音词书写；音频发音疑点另存，不改变音频')

    by_index = {c['native_indices'][0]: c for c in cues}
    extra_after = {}
    remove = set()
    if female and ep == 1:
        a, b = by_index[8], by_index[9]
        change(a, 'On renewal day, his mother slid me', '把half-pay放在同一字幕，不拆复合词')
        change(b, "a half-pay contract, certain I wouldn't dare refuse.", '复合词重新分段')
        a['end'] = b['start'] = 479  # source word "a" ~= 479.2 after 110% mapping
        changes.append({'native_indices':[8,9], 'boundary_frame':479,
                        'reason':'字幕分界移至a前附近，匹配词时间映射，非只移动文字'})
    if female and ep == 2:
        change(by_index[6], 'After a moment, he said. That surprised me.',
               '被排除台词后的标点和句界修复，不增删已读词')
    if female and ep == 3:
        change(by_index[4], "As if that wasn't clear enough, he added.", '恢复句界，将I与closed放在同一字幕')
        change(by_index[5], 'I closed my eyes and pretended to be asleep.', '移回上条末尾的I，不增删已读词')
        by_index[4]['end'] = by_index[5]['start'] = 316
        changes.append({'native_indices':[4,5], 'boundary_frame':316,
                        'reason':'I原音频2.74s，映射至当前时间线316.0帧附近'})
        c = by_index[8]
        change(c, 'the Bellandi estate.', 'estate词界和专名拼写按原文及两轮识别核对')
        c['end'] = 588
        extra_after[8] = [dict(start=588, end=626,
                               text='Claiming to feel nothing for me,',
                               native_indices=[8])]
        change(by_index[9], 'he still held me tight, leaving not an inch between us.',
               '保留上一字幕逗号后的连续句意')
        changes.append({'native_indices':[8], 'boundary_frame':588,
                        'reason':'跨原MP3合句在24.5s真实音频切点拆开；from改为for有原稿及双模型一致支持'})
        change(by_index[10], 'Just like every night before.', '前句在before结束，不把18岁接到上一句')
        by_index[10]['end'] = 746
        change(by_index[11], 'At 18, Matteo was kidnapped by rivals and',
               'At 18移回所属音频段，接完整后句')
        by_index[11]['start'] = 746
        changes.append({'native_indices':[10,11], 'boundary_frame':746,
                        'reason':'在31.0833s实际MP3切点分句，At 18与同段下一字幕合并'})
    if not female and ep == 1:
        change(by_index[8], "I'd never walk away.", '分开两条源MP3的句意')
        by_index[8]['end'] = 499
        change(by_index[9], 'Until my 10-year contract with the Blackwoods ran out.',
               '完整保留下一音频段的Until从句')
        by_index[9]['start'] = 499
        changes.append({'native_indices':[8,9], 'boundary_frame':499,
                        'reason':'在20.7917s真实音频切点拆开合句'})
    if not female and ep == 3:
        change(by_index[11], 'Dressed in threadbare rags,', '恢复与I waited连续的逗号，不增删词')

    expanded = []
    for cue in cues:
        idx = cue['native_indices'][0]
        if idx not in remove:
            expanded.append(cue)
        expanded.extend(extra_after.get(idx, []))
    clips = timeline['audio_tracks'][0]['items']
    for cue in expanded:
        mid = (cue['start'] + cue['end']) / 2
        hits = [c for c in clips if c['start'] <= mid < c['end']]
        assert len(hits) == 1, (name, cue)
        clip = hits[0]
        before = [cue['start'], cue['end']]
        # SRT timestamps are whole frames; ceil/floor avoid crossing gaps.
        import math
        cue['start'] = max(cue['start'], math.ceil(clip['start'] - 1e-8))
        cue['end'] = min(cue['end'], math.floor(clip['end'] + 1e-8))
        cue['audio_name'] = clip['name']
        if before != [cue['start'], cue['end']]:
            changes.append({'native_indices':cue['native_indices'],
                            'before_frames':before,
                            'after_frames':[cue['start'],cue['end']],
                            'reason':'夹紧原生字幕在源音频边界处的约一帧越界，不延入下一段'})
        assert cue['start'] < cue['end']

    # Merge native flash captions into an adjacent cue of the same source audio.
    merged = []
    for cue in expanded:
        previous = merged[-1] if merged else None
        if ((cue['end']-cue['start'])/FPS < .8 and previous and
                previous['audio_name'] == cue['audio_name'] and
                cue['start']-previous['end'] <= FPS*.7 and
                cue['end']-previous['start'] <= FPS*6 and
                len(previous['text']+' '+cue['text']) <= 72):
            changes.append({'native_indices':previous['native_indices']+cue['native_indices'],
                            'reason':'把不足0.8秒闪字并入同源相邻字幕，保留词序和末端点'})
            previous['end'] = cue['end']
            previous['text'] += ' ' + cue['text']
            previous['native_indices'] += cue['native_indices']
        else:
            merged.append(cue)
    final = merged
    for i, cue in enumerate(final, 1):
        cue['index'] = i
        cue['lines'] = wrap(cue['text'])
        cue['duration_seconds'] = (cue['end']-cue['start'])/FPS
        cue['characters_per_second'] = round(len(cue['text'])/cue['duration_seconds'], 2)
        assert 0 <= cue['start'] < cue['end'] <= timeline['end_frame']
        assert i == 1 or final[i-2]['end'] <= cue['start']
        assert len(cue['lines']) <= 2, (name, cue)
        assert max(map(len,cue['lines'])) <= 42
    prefix = '大码女版' if female else '大码性转男版'
    output = BASE/'字幕'/('女版' if female else '性转男版')/f'{prefix}{ep:02}.srt'
    write_srt(output, final)
    all_results.append({'timeline_name':name,'timeline_id':timeline['id'],
                        'fps':FPS,'srt_path':str(output),
                        'native_cue_count':len(original),'final_cue_count':len(final),
                        'changes':changes,'cues':final})

report={'method':'Resolve native English captions on the current 110 percent timeline; cue and text corrections with source audio boundary checks',
        'srt_timing_is_current_timeline_not_source_mp3':True,
        'all_source_audio_unchanged':True,
        'proper_name_spellings_are_editorial_and_do_not_verify_audio_pronunciation':True,
        'unresolved_audio_cases_retained_in_prior_content_audit':True,
        'ordinary_word_policy':'Keep native that/the/she kicked/tossed/Madame/desires; do not silently restore the script. from→for is supported by both blind models and source.',
        'timelines':all_results}
(HERE/'SRT字幕校正与时间核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([{'timeline':x['timeline_name'],'cues':x['final_cue_count'],
                   'min_seconds':min(c['duration_seconds'] for c in x['cues']),
                   'max_cps':max(c['characters_per_second'] for c in x['cues']),
                   'path':x['srt_path']} for x in all_results],ensure_ascii=False,indent=2))
