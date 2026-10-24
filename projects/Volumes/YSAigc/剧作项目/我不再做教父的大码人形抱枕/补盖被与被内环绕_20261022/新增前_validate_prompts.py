from pathlib import Path
from decimal import Decimal
import json
import re
import hashlib

ROOT = Path(__file__).parent
BASE = ROOT.parent / '复刻全集_人物动作核验_20261022'
baseline = json.loads((BASE / '复刻全集_人物动作修正版.json').read_text())['groups']
source = Path('/Users/zc/.codex/skills/short-drama-prompts-v3/references/format-c-v2.5-source.md').read_text()
quality = next(x for x in source.splitlines() if x.startswith('写实照片级、'))
skin = next(x for x in source.splitlines() if x.startswith('强制要求： 人物皮肤须'))
old = json.loads((BASE / '21组_修订前平台完整备份.json').read_text())
allowed_dialogue = [x for g in baseline for x in g['dialogue_lines']]
removed_vo = [s for g in old for s in re.findall(r'\{([^{}]+)\}', g['text']) if s not in allowed_dialogue]
fields = ['叙事任务（Narrative Task）', '镜头', '画面', '视觉引导（Visual Flow）',
          '微表演（Micro-Performance）', '对白反应（Dialogue Reaction）',
          '人物背景融合（Subject-Background Integration）', '光影细节（Lighting Detail）',
          '音频（Audio）', '运动强度（Motion Intensity）', '负面提示词（Negative Prompt）']
groups = []
for file in sorted(ROOT.glob('分组??-??.json')):
    groups.extend(json.loads(file.read_text())['groups'])
groups.sort(key=lambda g: g['timeline_position'])
results = []
for g in groups:
    b = baseline[g['timeline_position'] - 1]
    p = g['prompt']
    errors = []
    for k in ['index', 'episode', 'timeline_position', 'title', 'duration', 'source_paragraphs', 'dialogue_lines']:
        if g[k] != b[k]: errors.append('metadata_changed:' + k)
    refs = re.findall(r'§ASSET:([^§]+)§', p)
    if refs != re.findall(r'§ASSET:([^§]+)§', b['prompt']): errors.append('asset_mapping_changed')
    heads = list(re.finditer(r'【shot\s+\d+[^】]*】', p, re.I))
    header_count = p.count('固定画质词（Fixed Quality Descriptor）')
    if p.count(quality) != header_count: errors.append('fixed_quality_not_exact')
    if p.count(skin) != header_count: errors.append('skin_not_exact')
    if header_count == 0: errors.append('missing_group_header')
    if len(heads) != len(g['shots']): errors.append('shot_metadata_count')
    duration = sum((Decimal(x) for x in re.findall(r'duration:\s*([\d.]+)s', p)), Decimal(0))
    if duration != Decimal(str(g['duration'])): errors.append('duration_total')
    meta_duration = sum((Decimal(str(s['duration'])) for s in g['shots']), Decimal(0))
    if meta_duration != duration: errors.append('duration_metadata')
    for i, head in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(p)
        section = p[head.end():end]
        for f in fields:
            if len(re.findall('^' + re.escape(f) + '：', section, re.M)) != 1:
                errors.append(f'shot_{i+1}_field:{f}')
        if not re.search(r'^画面：.*(?:位置锁定|床位锁定|实际位置)', section, re.M):
            errors.append(f'shot_{i+1}_position_lock')
    for line in b['dialogue_lines']:
        if p.count(line) != 1: errors.append('dialogue_count:' + line)
        if not any(line in x for x in re.findall(r'^音频（Audio）：(.*)$', p, re.M)):
            errors.append('dialogue_outside_audio:' + line)
    if any(v in p for v in removed_vo): errors.append('removed_voiceover_returned')
    if len(p) >= 15000: errors.append('platform_character_limit')
    if re.search(r'§ASSET:[^§]*$|请选择|<集号>|<本组', p): errors.append('unfinished_placeholder')
    results.append({'position':g['timeline_position'], 'episode':g['episode'], 'title':g['title'],
                    'seconds':g['duration'], 'shots':len(heads), 'lighting_units':header_count,
                    'chars':len(p), 'assets':len(refs), 'errors':errors})
report = {'groups':len(groups), 'seconds':sum(g['duration'] for g in groups),
          'shots':sum(x['shots'] for x in results), 'lighting_units':sum(x['lighting_units'] for x in results),
          'asset_references':sum(x['assets'] for x in results), 'dialogue_lines':sum(len(g['dialogue_lines']) for g in groups),
          'results':results, 'passed':all(not x['errors'] for x in results)}
(ROOT / '新版正文结构核验.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print(json.dumps(report, ensure_ascii=False, indent=2))
if not report['passed']: raise SystemExit(1)
if len(groups) == 21:
    assert [g['timeline_position'] for g in groups] == list(range(1,22))
    document = {'projectId':446187, 'seriesId':3009063, 'template':'Format C V2.5',
                'group_count':21, 'lighting_units':report['lighting_units'],
                'total_planned_seconds':report['seconds'], 'groups':groups}
    (ROOT / '复刻全集_FormatC_V25_全部提示词.json').write_text(json.dumps(document, ensure_ascii=False, indent=2))
    (ROOT / '复刻全集_FormatC_V25_全部提示词.md').write_text('\n\n---\n\n'.join(g['prompt'] for g in groups))
    print('ALL_21_READY', hashlib.sha256((ROOT / '复刻全集_FormatC_V25_全部提示词.json').read_bytes()).hexdigest())
