#!/usr/bin/env python3
"""Validate and archive the 21 original groups plus one blanket supplement.

This script does not operate the browser and never writes to the old authority
directory. A successful run creates a NEW output directory containing the
22-group JSON/Markdown authority, mapping, statistics, and input snapshots.

Platform report: a list, or {"groups": [...]} / {"rows": [...]} / {"results": [...]}.
Each row must contain insertion-adjusted position (1..22), live `text`, native
`cards`: [{"text": asset_name, "img": image_url}], and `url`. `selected` and
`original_position` are optional, but validated when present. A row may wrap
these raw fields under `live`; an outer position is retained.

Planned prompt seconds are deliberately distinct from generation-setting or
already-generated video seconds. The latter are not inferred from this input.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import parse_qs, urlsplit


HERE = Path(__file__).resolve().parent
FIELDS = [
    '叙事任务（Narrative Task）', '镜头', '画面', '视觉引导（Visual Flow）',
    '微表演（Micro-Performance）', '对白反应（Dialogue Reaction）',
    '人物背景融合（Subject-Background Integration）', '光影细节（Lighting Detail）',
    '音频（Audio）', '运动强度（Motion Intensity）', '负面提示词（Negative Prompt）',
]
SHOT = re.compile(r'【shot\s+\d+[^】]*】', re.I)


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def norm(text: str) -> str:
    return re.sub(r'\s+', '', text)


def visible_prompt(text: str) -> str:
    return re.sub(r'§ASSET:([^§]+)§', r'\1', text)


def refs(text: str) -> list[str]:
    return re.findall(r'§ASSET:([^§]+)§', text)


def sounds(text: str) -> list[str]:
    return re.findall(r'^音频（Audio）：(.*)$', text, re.M)


def number(value: Decimal):
    return int(value) if value == value.to_integral() else float(value)


def rows_from_report(document) -> list[dict]:
    if isinstance(document, list):
        rows = document
    elif isinstance(document, dict):
        candidates = [document[k] for k in ('groups', 'rows', 'results', 'reopened')
                      if isinstance(document.get(k), list)]
        if len(candidates) != 1:
            raise ValueError('Platform report must have exactly one rows list, or be a list itself.')
        rows = candidates[0]
    else:
        raise ValueError('Unsupported platform report shape.')
    result = []
    for raw in rows:
        if not isinstance(raw, dict):
            raise ValueError('Platform rows must be objects containing actual live text and cards.')
        row = dict(raw)
        if isinstance(row.get('live'), dict):
            live = row.pop('live')
            row = {**row, **live}
        if 'position' not in row and 'timeline_position' in row:
            row['position'] = row['timeline_position']
        result.append(row)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--old', type=Path, default=HERE / '新增前_复刻全集_FormatC_V25_全部提示词.json')
    parser.add_argument('--new-group', type=Path, default=HERE / '新增盖被环绕组_待绑定.json')
    parser.add_argument('--patches', type=Path, default=HERE / '被子连续性替换清单.json')
    parser.add_argument('--platform-report', type=Path, required=True)
    parser.add_argument('--template-source', type=Path,
                        default=Path('/Users/zc/.codex/skills/short-drama-prompts-v3/references/format-c-v2.5-source.md'))
    parser.add_argument('--output', type=Path, default=HERE / '22组归档_校验输出')
    parser.add_argument('--verify-only', action='store_true', help='Validate all inputs; create no files.')
    args = parser.parse_args()

    input_paths = {k: getattr(args, k).resolve() for k in ('old', 'new_group', 'patches', 'platform_report', 'template_source')}
    old_doc = read_json(input_paths['old'])
    old_groups = old_doc['groups']
    new_group = read_json(input_paths['new_group'])
    patches = read_json(input_paths['patches'])
    live_rows = rows_from_report(read_json(input_paths['platform_report']))
    source = input_paths['template_source'].read_text(encoding='utf-8')
    quality = next(s for s in source.splitlines() if s.startswith('写实照片级、'))
    skin = next(s for s in source.splitlines() if s.startswith('强制要求： 人物皮肤须'))
    errors = []

    def check(condition, message):
        if not condition:
            errors.append(message)

    check(len(old_groups) == 21, 'old_group_count_must_be_21')
    check([g.get('timeline_position') for g in old_groups] == list(range(1, 22)), 'old_positions_not_1_through_21')
    check(new_group.get('insertion_after_original_position') == 6, 'new_group_insertion_must_follow_original_6')
    check(new_group.get('duration') == 12, 'new_group_planned_seconds_must_be_12')
    check(new_group.get('dialogue_lines') == [], 'new_group_must_not_add_dialogue')
    check(len(patches) == 26, 'continuity_patch_count_must_be_26')
    check(old_doc.get('projectId') == 446187 and old_doc.get('seriesId') == 3009063, 'wrong_project_or_series')
    if errors:
        print(json.dumps({'passed': False, 'errors': errors}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2

    originals = {g['timeline_position']: g for g in old_groups}
    revised = deepcopy(originals)
    patch_count = Counter()
    for i, patch in enumerate(patches, start=1):
        op = patch.get('original_position')
        check(op in range(7, 17), f'patch_{i}_position_outside_original_7_to_16')
        if op not in revised:
            continue
        text = revised[op]['prompt']
        old_line, new_line = patch.get('old', ''), patch.get('new', '')
        matches = text.count(old_line) if old_line else 0
        check(matches == 1, f'patch_{i}_old_line_not_single_match')
        check('\n' not in old_line and '\n' not in new_line, f'patch_{i}_must_be_one_complete_line')
        check(old_line in text.splitlines(), f'patch_{i}_old_not_complete_line')
        if patch.get('shot') is not None:
            sections = re.split(r'(?=【shot\s+\d+)', text)
            n = patch['shot']
            check(isinstance(n, int) and 0 < n < len(sections), f'patch_{i}_shot_out_of_range')
            if isinstance(n, int) and 0 < n < len(sections):
                check(old_line in sections[n].splitlines(), f'patch_{i}_line_not_in_declared_shot')
        if matches == 1:
            revised[op]['prompt'] = text.replace(old_line, new_line)
            patch_count[op] += 1

    # Explicitly permit only the same physical contact sound changing its object.
    for op, group in revised.items():
        original = originals[op]
        expected_sounds = sounds(original['prompt'])
        if op == 13:
            expected_sounds = [s.replace('一次隔衣轻压细响', '一次隔被轻压细响') for s in expected_sounds]
        check(sounds(group['prompt']) == expected_sounds, f'original_{op}_audio_changed_outside_allowed_contact_object')
        check(refs(group['prompt']) == refs(original['prompt']), f'original_{op}_asset_order_changed')
        for field in ('微表演（Micro-Performance）', '对白反应（Dialogue Reaction）'):
            extract = lambda t: re.findall('^' + re.escape(field) + '：.*$', t, re.M)
            check(extract(group['prompt']) == extract(original['prompt']), f'original_{op}_{field}_changed')
        check(SHOT.findall(group['prompt']) == SHOT.findall(original['prompt']), f'original_{op}_shot_headers_changed')

    groups = []
    for op in range(1, 22):
        group = revised[op]
        group['original_position'] = op
        group['timeline_position'] = op if op <= 6 else op + 1
        if patch_count[op]:
            group['blanket_continuity_revision_note'] = '同一被子状态与可见性同步；原表演、对白、动作事件、时长及运镜保留。'
        groups.append(group)
        if op == 6:
            supplement = deepcopy(new_group)
            supplement['original_position'] = None
            supplement['timeline_position'] = 7
            groups.append(supplement)

    check(len(groups) == 22, 'merged_group_count_not_22')
    live_by_position = {}
    for row in live_rows:
        position = row.get('position')
        check(isinstance(position, int) and 1 <= position <= 22, 'platform_row_missing_valid_new_position')
        if not isinstance(position, int) or not 1 <= position <= 22:
            continue
        check(position not in live_by_position, f'platform_duplicate_position_{position}')
        live_by_position[position] = row
    check(sorted(live_by_position) == list(range(1, 23)), 'platform_report_must_have_all_22_reopened_groups')

    results, mapping, limitations = [], [], []
    image_sources = defaultdict(set)
    storyboard_ids = []
    for group in groups:
        position = group['timeline_position']
        op = group['original_position']
        text = group['prompt']
        heads = list(SHOT.finditer(text))
        headers = text.count('固定画质词（Fixed Quality Descriptor）')
        durations = [Decimal(s) for s in re.findall(r'duration:\s*([\d.]+)s', text)]
        planned = sum(durations, Decimal(0))
        check(planned == Decimal(str(group['duration'])), f'position_{position}_prompt_duration_total')
        check(sum((Decimal(str(s['duration'])) for s in group['shots']), Decimal(0)) == planned,
              f'position_{position}_shot_metadata_duration')
        check(len(heads) == len(group['shots']), f'position_{position}_shot_metadata_count')
        check(headers > 0 and text.count(quality) == text.count(skin) == headers,
              f'position_{position}_fixed_quality_or_skin_segment')
        check(len(text) < 15000, f'position_{position}_platform_character_limit')
        for i, head in enumerate(heads):
            section = text[head.end():heads[i+1].start() if i+1 < len(heads) else len(text)]
            for field in FIELDS:
                check(len(re.findall('^' + re.escape(field) + '：', section, re.M)) == 1,
                      f'position_{position}_shot_{i+1}_field_{field}')
            check(bool(re.search(r'^画面：.*(?:位置锁定|床位锁定|实际位置)', section, re.M)),
                  f'position_{position}_shot_{i+1}_position_lock')
        expected_dialogue = originals[op]['dialogue_lines'] if op is not None else []
        check(group['dialogue_lines'] == expected_dialogue, f'position_{position}_dialogue_metadata')
        spoken = [d for audio in sounds(text) for d in re.findall(r'\{([^{}]+)\}', audio)]
        check(spoken == expected_dialogue, f'position_{position}_spoken_lines_order_or_content')
        for line in expected_dialogue:
            check(text.count(line) == 1, f'position_{position}_dialogue_occurrence_{line}')
        if op is not None:
            for key in ('index', 'episode', 'title', 'duration', 'source_paragraphs', 'dialogue_lines'):
                check(group[key] == originals[op][key], f'original_{op}_metadata_{key}_changed')

        row = live_by_position.get(position)
        body_ok = cards_ok = url_ok = False
        if row is not None:
            check('original_position' not in row or row['original_position'] == op,
                  f'position_{position}_platform_original_position_mapping')
            body_ok = isinstance(row.get('text'), str) and norm(row['text']) == norm(visible_prompt(text))
            check(body_ok, f'position_{position}_live_body_mismatch')
            cards = row.get('cards')
            cards_ok = isinstance(cards, list) and all(isinstance(c, dict) for c in cards)
            if cards_ok:
                cards_ok = [c.get('text') for c in cards] == refs(text)
                cards_ok = cards_ok and all(isinstance(c.get('img'), str) and c['img'].strip() for c in cards)
                for card in cards:
                    if card.get('text') and isinstance(card.get('img'), str):
                        image_sources[card['text']].add(card['img'].split('?', 1)[0])
            check(bool(cards_ok), f'position_{position}_native_cards_or_image_sources_mismatch')
            url = row.get('url', '')
            parts = urlsplit(url)
            query = parse_qs(parts.query)
            url_ok = ('/projects/446187/' in parts.path and query.get('seriesId') == ['3009063']
                      and len(query.get('storyBoardId', [])) == 1)
            check(url_ok, f'position_{position}_wrong_platform_target_url')
            if url_ok:
                storyboard_ids.append(query['storyBoardId'][0])
                group['storyboard_id'] = query['storyBoardId'][0]
                group['platform_url'] = url
            selected = row.get('selected')
            if isinstance(selected, str):
                m = re.search(r'分镜\s*(\d+)', selected)
                check(bool(m) and int(m.group(1)) == position, f'position_{position}_selected_slot_mismatch')
            if body_ok and cards_ok and url_ok:
                group['native_asset_status'] = 'saved_and_reopened_verified'
        raw_params = row.get('params') if row is not None else None
        reopened_seconds = None
        if isinstance(raw_params, str):
            match = re.search(r'时长\s*([\d.]+)\s*秒', raw_params)
            if match:
                reopened_seconds = number(Decimal(match.group(1)))
        generation_state = {'params_after_reopen': raw_params,
                            'draft_params_after_reopen_seconds': reopened_seconds}
        if op is None:
            limitation = ('新增盖被环绕组的提示词计划时长为12秒；当前页面曾设置12秒，'
                          '离开并重新打开后参数显示默认4秒。12秒生成参数未持久化；'
                          '正文、原生资产卡和顺序已保存回读，未提交生成。')
            generation_state.update(generation_duration_persistent=False,
                                    current_session_duration_set=12,
                                    reopens_to_default_seconds=4,
                                    limitation=limitation)
            group.update(generation_state)
            group['generation_status'] = 'not_submitted'
            limitations.append({'position': position, 'storyboard_id': group.get('storyboard_id'),
                                **generation_state})
        results.append({'position': position, 'original_position': op, 'title': group['title'],
                        'planned_seconds': number(planned), 'shots': len(heads), 'lighting_units': headers,
                        'native_asset_references': len(refs(text)), 'dialogue_lines': len(expected_dialogue),
                        'live_body_match': bool(body_ok), 'live_cards_match': bool(cards_ok), 'url_match': bool(url_ok),
                        **generation_state})
        mapping.append({'original_position': op, 'timeline_position': position, 'index': group['index'],
                        'episode': group['episode'], 'title': group['title'],
                        'storyboard_id': group.get('storyboard_id'), 'platform_url': group.get('platform_url'),
                        'continuity_patches': patch_count[op] if op is not None else 0,
                        'is_supplement': op is None})

    check(len(set(storyboard_ids)) == 22, 'platform_storyboard_ids_not_22_unique')
    for name, sources in image_sources.items():
        check(len(sources) == 1, f'asset_{name}_uses_inconsistent_native_image_sources')
    expected_seconds = sum((Decimal(str(g['duration'])) for g in old_groups), Decimal(0)) + Decimal(str(new_group['duration']))
    total_seconds = sum((Decimal(str(g['duration'])) for g in groups), Decimal(0))
    check(total_seconds == expected_seconds, 'total_planned_duration_not_old_plus_supplement')
    report = {'passed': not errors, 'scope': 'prompt_archival_and_live_readback_validation_only',
              'groups': len(groups), 'planned_seconds': number(total_seconds),
              'shots': sum(x['shots'] for x in results), 'lighting_units': sum(x['lighting_units'] for x in results),
              'asset_references': sum(x['native_asset_references'] for x in results),
              'dialogue_lines': sum(x['dialogue_lines'] for x in results),
              'continuity_patch_count': len(patches), 'original_groups': 21, 'added_groups': 1,
              'all_22_live_bodies_and_cards_verified': all(x['live_body_match'] and x['live_cards_match'] and x['url_match'] for x in results),
              'video_generation_or_playback_claimed': False,
              'generation_settings_duration_inferred_from_prompt': False,
              'limitations': limitations,
              'results': results, 'errors': errors}
    if errors:
        print(json.dumps(report, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2
    if args.verify_only:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    output = args.output.resolve()
    if output.exists():
        print(f'Refusing to overwrite existing archive directory: {output}', file=sys.stderr)
        return 2
    output.mkdir(parents=True)
    snapshots = output / 'input_snapshots'
    snapshots.mkdir()
    input_manifest = {}
    for key, path in input_paths.items():
        target = snapshots / (key + '__' + path.name)
        shutil.copy2(path, target)
        input_manifest[key] = {'path': str(path), 'sha256': sha(path), 'snapshot': str(target.relative_to(output))}
    merged = {k: deepcopy(v) for k, v in old_doc.items() if k != 'groups'}
    merged.update(group_count=22, lighting_units=report['lighting_units'], total_planned_seconds=number(total_seconds),
                  groups=groups, authority_revision='blanket_supplement_after_original_6',
                  original_position_mapping_file='原21组与新22组位置映射.json')
    write_json(output / '复刻全集_FormatC_V25_全部提示词.json', merged)
    (output / '复刻全集_FormatC_V25_全部提示词.md').write_text('\n\n---\n\n'.join(g['prompt'] for g in groups), encoding='utf-8')
    write_json(output / '22组_正文与平台回读核验.json', report)
    write_json(output / '原21组与新22组位置映射.json', mapping)
    episodes = []
    for ep in sorted({g['episode'] for g in groups}):
        subset = [x for x in groups if x['episode'] == ep]
        episodes.append({'episode': ep, 'groups': len(subset), 'planned_seconds': number(sum((Decimal(str(g['duration'])) for g in subset), Decimal(0))),
                         'shots': sum(len(g['shots']) for g in subset)})
    write_json(output / '22组_计划统计.json', {'group_count': 22, 'planned_seconds': number(total_seconds),
              'shots': report['shots'], 'lighting_units': report['lighting_units'], 'asset_references': report['asset_references'],
              'dialogue_lines': report['dialogue_lines'], 'episodes': episodes,
              'duration_basis': 'Prompt-planned seconds only; not generated-video runtime or generation settings.'})
    write_json(output / '输入快照与SHA256.json', input_manifest)
    files = [p for p in output.iterdir() if p.is_file()]
    write_json(output / '输出文件SHA256.json', {p.name: sha(p) for p in sorted(files)})
    print(json.dumps({'passed': True, 'output': str(output), 'groups': 22,
                      'planned_seconds': number(total_seconds), 'shots': report['shots'],
                      'asset_references': report['asset_references'], 'dialogue_lines': report['dialogue_lines']}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
