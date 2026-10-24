"""Select a verified task timeline and a real subtitle preview frame; no content edit."""
import argparse
import json
from native_common import BASE, connect, read_json, timelines

parser = argparse.ArgumentParser()
parser.add_argument('episode', type=int, choices=[16, 17, 18, 19])
parser.add_argument('sample', type=int, nargs='?', default=0)
args = parser.parse_args()
resolve, manager, project, pool = connect()
rows = read_json(BASE / '准备/字幕预览取点.json')
row = next(r for r in rows if r['episode'] == args.episode)
point = row['samples'][args.sample]
journal = read_json(BASE / 'Resolve_组装实读.json')
owned = next(r for r in journal['episodes'] if r['episode'] == args.episode)
timeline = next(t for t in timelines(project) if t.GetUniqueId() == owned['id'])
assert timeline.GetName() == row['timeline']
assert project.SetCurrentTimeline(timeline)
frame = point['frame']
h, remainder = divmod(frame, 24 * 3600)
m, remainder = divmod(remainder, 24 * 60)
s, f = divmod(remainder, 24)
tc = '%02d:%02d:%02d:%02d' % (h, m, s, f)
assert timeline.SetCurrentTimecode(tc)
assert timeline.GetCurrentTimecode() == tc
print(json.dumps(dict(point, episode=args.episode, timecode=tc, timeline=timeline.GetName()), ensure_ascii=False))
