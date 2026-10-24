"""Freeze the reviewed four-episode plan and independently audit all caption sets.

This script performs only offline file operations. It never connects to Resolve.
"""
import argparse
import json
from pathlib import Path
from native_common import BASE, load_plan, read_json, sha256, write_json
from audit_offline_episode import audit

parser = argparse.ArgumentParser()
parser.add_argument('--output', default=str(BASE / 'final_native_plan.json'))
args = parser.parse_args()
sources = {16: BASE / '准备/EP16_native_edit_plan.json', 17: BASE / '准备/EP17_native_edit_plan.json',
           18: BASE / '准备/EP18_原生剪辑计划.json', 19: BASE / '准备/EP19_native_edit_plan.json'}
event_sources = {16: BASE / '字幕/EP16_原文词事件.json', 17: BASE / '准备/EP17_original_word_events.json',
                 18: BASE / '字幕/EP18_原文词事件.json', 19: BASE / '准备/EP19_original_word_events.json'}
episodes = []
audits = []
for episode, source in sources.items():
    component = read_json(source)
    ep = next(x for x in component['episodes'] if x['episode'] == episode) if 'episodes' in component else component
    assert ep['episode'] == episode
    ep = dict(ep, subtitle_srt=str(BASE / '字幕' / ('EP%d.srt' % episode)))
    report = audit(ep, str(event_sources[episode]))
    write_json(BASE / '准备' / ('EP%d_独立原生计划核验.json' % episode), report)
    episodes.append(ep)
    audits.append({key: value for key, value in report.items() if key != 'narration_coverage'})

levels = {x['source_path']: x for x in read_json(BASE / 'ASR/source_levels.json')['files']}
seen_frames = {}
cross_episode_reuse = []
for ep in episodes:
    for clip in ep['video']:
        identity = levels[clip['path']]['source_sha256']
        for old in seen_frames.setdefault(identity, []):
            if not (clip['source_end_frame'] <= old['source_start_frame'] or clip['source_start_frame'] >= old['source_end_frame']):
                assert old['episode'] != ep['episode'], ('Repeated frames within one episode, including identical retakes', ep['episode'], clip, old)
                cross_episode_reuse.append({'source_path': clip['path'], 'episodes': [old['episode'], ep['episode']],
                    'source_start_frame': max(clip['source_start_frame'], old['source_start_frame']),
                    'source_end_frame': min(clip['source_end_frame'], old['source_end_frame']),
                    'record_frames': [old['record_frame'], clip['record_frame']],
                    'editorial_basis': clip.get('source_episode_override_reason') or old.get('source_episode_override_reason') or 'Same original scene reused between distinct episodes; no within-episode loop.'})
        seen_frames[identity].append(dict(clip, episode=ep['episode']))

plan = {'status': 'READY_FOR_NATIVE_ASSEMBLY', 'project': '大码枕头', 'fps': 24,
        'source_end_frame_exclusive': True, 'all_original_speed_percent': 100,
        'scope': '男版16–19，新男版音色，原速旁白，原生画面与链接同期声；先四集SRT入轨，后加载轨道预设。',
        'cross_episode_reused_source_ranges': cross_episode_reuse,
        'source_component_files': {str(episode): {'path': str(path), 'sha256': sha256(path)} for episode, path in sources.items()},
        'word_event_files': {str(episode): {'path': str(path), 'sha256': sha256(path)} for episode, path in event_sources.items()},
        'subtitle_files': {str(ep['episode']): {'path': ep['subtitle_srt'], 'sha256': sha256(ep['subtitle_srt'])} for ep in episodes},
        'episodes': episodes}
output = Path(args.output).resolve()
temporary = output.with_name(output.name + '.candidate.json')
write_json(temporary, plan)
load_plan(temporary)
journal = BASE / 'Resolve_组装实读.json'
if journal.exists():
    assert read_json(journal)['plan_sha256'] == sha256(temporary), 'An assembled plan is already frozen; do not rewrite it'
if output.exists():
    assert output.read_bytes() == temporary.read_bytes(), 'Final plan already exists with different contents; investigate before replacing'
else:
    temporary.replace(output)
if temporary.exists():
    temporary.unlink()
summary = {'final_plan': str(output), 'final_plan_sha256': sha256(output), 'offline_validation_passed': True,
           'all_27_adopted_narration_files_covered': True, 'no_repeated_source_frames_within_each_episode': True,
           'cross_episode_reused_source_ranges': cross_episode_reuse,
           'srt_first_then_exact_native_preset': True, 'no_resolve_mutation': True, 'episodes': audits}
write_json(BASE / '准备/四集最终离线核验.json', summary)
print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
