"""Offline captions from reviewed original word events at final timeline positions."""
import argparse
import json
from native_common import BASE, read_json, write_json
from subtitle_tools import cues_from_events, write_srt

parser = argparse.ArgumentParser()
parser.add_argument('--word-events', required=True)
args = parser.parse_args()
source = read_json(args.word_events)
report = []
for ep in source['episodes']:
    assert ep['episode'] in {16, 17, 18, 19}
    cues = cues_from_events(ep['events'], ep['duration_frames'])
    destination = BASE / '字幕' / ('EP%d.srt' % ep['episode'])
    write_srt(destination, cues)
    report.append({'episode': ep['episode'], 'srt': str(destination), 'cue_count': len(cues),
                   'duration_frames': ep['duration_frames'], 'original_word_events_preserved': True,
                   'max_lines': max(len(x['text'].splitlines()) for x in cues),
                   'max_characters_per_line': max(len(line) for x in cues for line in x['text'].splitlines())})
write_json(BASE / '字幕/生成清单.json', report)
print(json.dumps(report, ensure_ascii=False, indent=2))

