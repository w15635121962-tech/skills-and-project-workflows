"""Rebuild only local SRTs with the current reviewed grouping function."""
import argparse
import json
from native_common import BASE, read_json, sha256, write_json
from subtitle_tools import cues_from_events, parse_srt, write_srt

parser = argparse.ArgumentParser()
parser.add_argument('--word-events', nargs='+', required=True)
args = parser.parse_args()
report = []
for event_path in args.word_events:
    before_hash = sha256(event_path)
    source = read_json(event_path)
    episodes = source['episodes'] if 'episodes' in source else [source]
    for ep in episodes:
        assert ep['episode'] in {16, 17, 18, 19}
        words = [x['word'] for x in sorted(ep['events'], key=lambda x: (x['start_frame'], x['end_frame']))]
        cues = cues_from_events(ep['events'], ep['duration_frames'])
        output = BASE / '字幕' / ('EP%d.srt' % ep['episode'])
        write_srt(output, cues)
        actual = parse_srt(output)
        assert words == ' '.join(text.replace('\n', ' ') for _, _, text in actual).split()
        report.append({'episode': ep['episode'], 'srt': str(output), 'cue_count': len(actual),
                       'word_count': len(words), 'original_word_order_exact': True,
                       'minimum_cue_frames': min(b - a for a, b, _ in actual),
                       'max_lines': max(len(text.splitlines()) for _, _, text in actual),
                       'max_characters_per_line': max(len(line) for _, _, text in actual for line in text.splitlines()),
                       'word_events_source': event_path, 'word_events_sha256': before_hash,
                       'srt_sha256': sha256(output), 'no_resolve_mutation': True})
    assert before_hash == sha256(event_path), 'Word event source changed'
write_json(BASE / '字幕/本次字幕重平衡回读.json', report)
print(json.dumps(report, ensure_ascii=False, indent=2))
