"""Preserve supplied original words; map source word times through 100% native edits."""
import math
import re
import textwrap
from pathlib import Path

FPS = 24
MAX_LINE = 26
MAX_LINES = 3


def continuous_source_windows(clips, audio_path):
    """Join edit items only when source AND record frames are perfectly contiguous.

    Such a native clip seam removes no samples and does not cut off a spoken word.
    Real pause removal, source reorder or shifted records remain separate windows.
    """
    relevant = sorted([x for x in clips if x['path'] == str(audio_path)], key=lambda x: x['record_frame'])
    windows = []
    for clip in relevant:
        if windows and windows[-1]['source_end_frame'] == clip['source_start_frame'] and (
            windows[-1]['record_frame'] + windows[-1]['source_end_frame'] - windows[-1]['source_start_frame'] == clip['record_frame']):
            windows[-1]['source_end_frame'] = clip['source_end_frame']
        else:
            windows.append(dict(clip))
    return windows


def original_words_on_timeline(words, audio_path, clips):
    """words: original text in word/text plus source seconds start/end.

    ASR corrected canonical words must be supplied upstream, never synthesized here.
    Clip end is exclusive; removed/shifted cuts inside a spoken word are rejected.
    Perfectly source/record-contiguous native clip seams are treated as continuous.
    """
    output = []
    relevant = continuous_source_windows(clips, audio_path)
    for index, word in enumerate(words):
        text = word.get('original_word', word.get('word', word.get('text')))
        assert isinstance(text, str) and text.strip()
        start = round(float(word['start']) * FPS)
        end = max(start + 1, round(float(word['end']) * FPS))
        matching = [c for c in relevant if c['source_start_frame'] <= start and end <= c['source_end_frame']]
        assert len(matching) == 1, ('Word cut, missing, or duplicated', audio_path, index, text, start, end)
        clip = matching[0]
        offset = clip['record_frame'] - clip['source_start_frame']
        output.append({'word': text.strip(), 'start_frame': start + offset, 'end_frame': end + offset,
                       'source_path': str(audio_path), 'source_word_index': index})
    return output


def wrap_original(words):
    text = ' '.join(words)
    assert all(len(word) <= MAX_LINE for word in words), 'Word exceeds the preset line width'
    return textwrap.wrap(text, MAX_LINE, break_long_words=False, break_on_hyphens=False)


def cues_from_events(events, timeline_end):
    """Sorted original word events -> <=3 explicit lines, <=26 characters each.

    Separate speakers/paragraphs with boundary_before=True upstream when needed.
    No textual rewriting or automated ASR substitution is performed here.
    """
    events = sorted(events, key=lambda x: (x['start_frame'], x['end_frame']))
    assert events
    for index, event in enumerate(events):
        assert 0 <= event['start_frame'] < event['end_frame'] <= timeline_end
        if index:
            assert event['start_frame'] >= events[index - 1]['start_frame']
    groups = []
    current = []
    for event in events:
        proposed = current + [event]
        if current and (event.get('boundary_before') or
                        event['start_frame'] - current[-1]['end_frame'] > 18 or
                        event['end_frame'] - current[0]['start_frame'] > 96 or
                        len(wrap_original([x['word'] for x in proposed])) > MAX_LINES):
            groups.append(current)
            current = []
        current.append(event)
        # Full stops create natural cues once the displayed phrase is readable.
        if re.search(r'[.!?][\"”\']?$', event['word']) and len(' '.join(x['word'] for x in current)) >= 12:
            groups.append(current)
            current = []
    if current:
        groups.append(current)
    # Avoid flashing a one-word tail after a full three-line cue. Move the
    # preceding words with their real timestamps; never cross a paragraph,
    # speaker/message boundary, sentence ending, or a substantial silent gap.
    for index in range(1, len(groups)):
        before, tail = groups[index - 1], groups[index]
        if tail[0].get('boundary_before') or tail[0]['start_frame'] - before[-1]['end_frame'] > 18:
            continue
        while (len(tail) < 3 or tail[-1]['end_frame'] - tail[0]['start_frame'] < 24) and len(before) > 3:
            if re.search(r'[.!?][\"”\']?$', before[-1]['word']):
                break
            candidate = [before[-1]] + tail
            if len(wrap_original([x['word'] for x in candidate])) > MAX_LINES:
                break
            tail.insert(0, before.pop())
    result = []
    for index, words in enumerate(groups):
        start = words[0]['start_frame']
        end = max(start + 1, words[-1]['end_frame'])
        next_start = groups[index + 1][0]['start_frame'] if index + 1 < len(groups) else timeline_end
        # Preserve voiced end. Add at most four frames of reading hold in a real gap.
        end = min(timeline_end, max(end, min(next_start, end + 4)))
        assert end <= next_start, ('Different speech overlaps; resolve dialogue/VO before subtitle assembly', index)
        lines = wrap_original([x['word'] for x in words])
        assert len(lines) <= MAX_LINES and all(len(line) <= MAX_LINE for line in lines)
        result.append({'start_frame': start, 'end_frame': end, 'text': '\n'.join(lines)})
    assert [x['word'] for x in events] == ' '.join(x['text'].replace('\n', ' ') for x in result).split(), 'Original words changed'
    return result


def srt_time(frame):
    millis = round(frame * 1000 / FPS)
    hours, millis = divmod(millis, 3600000)
    minutes, millis = divmod(millis, 60000)
    seconds, millis = divmod(millis, 1000)
    return '%02d:%02d:%02d,%03d' % (hours, minutes, seconds, millis)


def write_srt(path, cues):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = '\n\n'.join('%d\n%s --> %s\n%s' %
                          (index + 1, srt_time(cue['start_frame']), srt_time(cue['end_frame']), cue['text'])
                          for index, cue in enumerate(cues)) + '\n'
    path.write_text(content, encoding='utf-8-sig')
    assert parse_srt(path) == [(c['start_frame'], c['end_frame'], c['text']) for c in cues]


def parse_srt(path):
    def frame(tc):
        h, m, s, ms = map(int, re.split('[:,]', tc))
        return round((h * 3600 + m * 60 + s + ms / 1000) * FPS)
    cues = []
    content = Path(path).read_text(encoding='utf-8-sig').replace('\r\n', '\n').strip()
    for block in re.split(r'\n\s*\n', content):
        lines = block.splitlines()
        assert len(lines) >= 3 and int(lines[0]) == len(cues) + 1
        start, end = lines[1].split(' --> ')
        cue = (frame(start), frame(end), '\n'.join(lines[2:]))
        assert cue[0] < cue[1]
        assert len(lines[2:]) <= MAX_LINES and all(len(x) <= MAX_LINE for x in lines[2:])
        if cues:
            assert cue[0] >= cues[-1][1]
        cues.append(cue)
    return cues

