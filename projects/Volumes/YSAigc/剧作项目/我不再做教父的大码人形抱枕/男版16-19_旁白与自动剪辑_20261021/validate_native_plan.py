"""Offline only. No Resolve connection, imports or project changes."""
import argparse
import json
from native_common import load_plan

parser = argparse.ArgumentParser()
parser.add_argument('--plan', required=True)
args = parser.parse_args()
plan = load_plan(args.plan, require_all=True)
print(json.dumps({'valid': True, 'fps': 24, 'source_end_exclusive': True,
                  'episodes': [{'episode': ep['episode'], 'frames': ep['duration_frames'],
                   'video': len(ep['video']), 'linked_sync': len(ep['video']),
                   'original_speed_narration': len(ep['narration'])} for ep in plan['episodes']]}, ensure_ascii=False))
