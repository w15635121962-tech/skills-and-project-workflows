#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build reviewable local EP03 prompt drafts; never calls a platform or Resolve."""

from pathlib import Path
from decimal import Decimal
import datetime
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = HERE / 'source_shots.json'
SEMANTICS = HERE / 'prompt_semantic_drafts.json'
DOWNLOADS = ROOT / '平台工作/飞书资产下载清单.json'
FIELDS = ['时长', '环境氛围', '景别', '拍摄角度', '摄像机运动', '人物角色和运动', '人物表演', '画面内容']
SOURCE_DIALOGUE = {23: 'Her.', 48: "Dante, it's time to sleep."}
PREFIXES = {'女版': '大码女版', '性转男版': '性转版男版'}
SELECTED_DIALOGUE = {'女版': {23: 'Her.', 48: "Mr. Bellandi, it's time for bed."},
                     '性转男版': {23: 'Him.', 48: 'Vittoria, time to sleep.'}}

NAMES = {1: '大码女主_Eliza_日常', 2: '大码男主_性转_日常', 3: '大码女主_Eliza_睡衣',
         4: '大码男主_性转_睡衣', 7: '童年女主_Eliza', 8: '童年男主_性转',
         9: 'Matteo_成年_日常', 11: 'Matteo_成年_睡衣', 12: 'Vittoria_成年_日常',
         13: 'Vittoria_成年_黑色睡衣', 14: 'Matteo_童年_日常', 15: 'Vittoria_童年_日常',
         18: 'Alessia_情人_日常', 21: '性转男情人_日常', 22: 'Serafina_母亲_共用',
         28: '保镖', 30: '医生', 34: '佣人', 38: 'Eliza旧卧室', 41: '性转卧室',
         44: '庄园大门', 45: '庄园客厅', 46: '庄园走廊', 47: 'Matteo卧室', 48: '庄园会客厅',
         50: '性转庄园大门', 51: '性转庄园客厅', 52: '性转庄园走廊', 53: 'Vittoria卧室', 54: '性转庄园会客厅'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def scene_keys(shot):
    if shot <= 3:
        return ['home']
    if shot <= 6:
        return ['home', 'gate']
    if shot == 7:
        return ['gate']
    if shot <= 10:
        return ['reception']
    if shot <= 13:
        return ['hall']
    if shot <= 24:
        return ['gate']
    if shot <= 26:
        return ['gate', 'hall']
    if shot <= 30:
        return ['hall']
    if shot <= 36:
        return ['reception']
    if shot <= 40:
        return ['hall']
    if shot == 41:
        return ['hall', 'bedroom']
    if shot <= 44 or shot == 47:
        return ['bedroom']
    return ['corridor']


def version_setup(version):
    female = version == '女版'
    return {
        'female': female,
        'tokens': {'P': 'Eliza' if female else '性转男主', 'D': 'Matteo' if female else 'Vittoria',
                   'Y': '少年Matteo' if female else '少女Vittoria', 'C': '童年Eliza' if female else '童年性转男主',
                   'L': 'Alessia' if female else '性转男情人'},
        'role_asset': {'adult_pillow_pajamas': 3 if female else 4,
                       'adult_don_black_robe': 11 if female else 13,
                       'young_don_13': 14 if female else 15,
                       'psychologist': 30, 'maid': 34, 'bodyguards_pair': 28,
                       'young_pillow_13': 7 if female else 8,
                       'adult_pillow_daywear': 1 if female else 2,
                       'don_mother': 22, 'adult_don_burgundy_shirt': 9 if female else 12,
                       'adult_blonde_lover': 18 if female else 21},
        'scene_asset': {'home': 38 if female else 41, 'gate': 44 if female else 50,
                        'hall': 45 if female else 51, 'reception': 48 if female else 54,
                        'bedroom': 47 if female else 53, 'corridor': 46 if female else 52},
    }


def role_name(key, setup):
    tokens = setup['tokens']
    if key.startswith('adult_pillow'):
        return tokens['P']
    if key.startswith('adult_don'):
        return tokens['D']
    return {'young_don_13': tokens['Y'], 'young_pillow_13': tokens['C'],
            'adult_blonde_lover': tokens['L'], 'don_mother': 'Serafina', 'psychologist': '医生',
            'maid': '佣人', 'bodyguards_pair': '两名保镖', 'family_elder': '家族长老',
            'family_head': '家族首领', 'candidate_children': '候选孩子群演',
            'candidate_parents': '候选家长群演'}[key]


def translated_geometry(text, setup):
    t = setup['tokens']
    replacements = {'成年男主': t['D'], '少年男主': t['Y'], '童年女主': t['C'],
                    '男女主角': t['D'] + '与' + t['L'], '教父夫人': 'Serafina',
                    '女主': t['P'], '男主': t['D'], '女伴': t['L']}
    # Apply in a single pass: 性转男主 contains 男主, so sequential replacement
    # would incorrectly turn the narrator into 性转Vittoria.
    text = re.sub('|'.join(re.escape(key) for key in replacements),
                  lambda match: replacements[match[0]], text)
    # Composition words such as 少年正脸 describe the youth don, not a new character.
    if not setup['female']:
        text = text.replace('少年正脸', '少女正脸').replace('少年半身', '少女半身')
    # The user selected the Feishu wardrobe/space cards, so source-film costume or
    # furniture-specific words cannot contradict those cards in the prompt.
    for old, new in [('粉色丝绒床头与床品', '参考卧室中的床头与床品'),
                     ('粉色床头靠垫', '参考卧室的床头与靠垫'),
                     ('兜帽包裹少女正脸', '童年角色发型轮廓围合正脸'),
                     ('酒红色丝绒拉扣金雕床头', '所引卧室参考图的床头陈设'),
                     ('酒红色丝绒床头与酒红衬衫相互呼应', '卧室陈设与角色日常服装形成层次'),
                     ('金雕床头', '参考图床头'), ('床头雕花', '参考图床头上缘'),
                     ('高耸的所引卧室参考图的床头陈设', '所引卧室参考图的床头陈设'),
                     ('黑色领结', '参考图领饰')]:
        text = text.replace(old, new)
    return text


def actor_entries(shots, setup):
    entries, seen = [], set()
    for shot in shots:
        for role in shot['source_asset_requirements']['roles']:
            key = role['id']
            asset = setup['role_asset'].get(key)
            identity = (key, asset)
            if identity in seen:
                continue
            seen.add(identity)
            name = role_name(key, setup)
            entries.append(f'{name}（@{NAMES[asset]}）' if asset else f'{name}（参考图待指定，按本镜源表的群演身份）')
    return entries or ['无实出人物；转场残影依相邻镜角色']


def header(shots, setup):
    keys = list(dict.fromkeys(k for shot in shots for k in scene_keys(shot['source_shot'])))
    scene_desc = {'home': '公寓卧室床头', 'gate': '庄园大门、台阶及前庭', 'hall': '庄园挑高大厅',
                  'reception': '庄园诊疗或主母会客区', 'bedroom': '庄园主卧床头', 'corridor': '庄园主卧门外走廊与门缝'}
    scene_line = '；'.join(f'{scene_desc[k]}（@{NAMES[setup["scene_asset"][k]]}）' for k in keys)
    return ('出场角色：' + '；'.join(actor_entries(shots, setup))
            + '。角色五官、发型、体型及服装锁定对应参考图，只提取身份与衣装形成当前镜头的单幅实景。\n'
            + '场景：' + scene_line + '。建筑与陈设依据所引参考图，镜内时段及光照按各Shot环境氛围。\n'
            + '以下所有Shot出场的角色和场景统一锁定参考图。\n'
            + '画幅：竖屏9:16。\n')


def main():
    source, semantic, downloaded = load(SOURCE), load(SEMANTICS), load(DOWNLOADS)
    records = {a['index']: a for a in downloaded['assets']}
    assert len(source['shots']) == 56 and source['summary']['visual_image_reviews_done'] == 56
    used_indices = set()
    versions = []
    dialogue_slots = []
    # Verify the exact quotation against the actual full project document.
    female_docx = ROOT.parent / '完整剧本/我不再做教父的大码人形抱枕EN.docx'
    with ZipFile(female_docx) as archive:
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        paragraphs = [''.join(t.text or '' for t in para.findall('.//w:t', ns))
                      for para in ET.fromstring(archive.read('word/document.xml')).findall('.//w:body/w:p', ns)]
    assert paragraphs[117] == '"' + SELECTED_DIALOGUE['女版'][48] + '"'
    assert 'knock on his door' in paragraphs[116]
    female_ep3 = ROOT.parent / '配音制作_前3集/英文剧本/女版/女版_第03集_纯英文全文.txt'
    male_ep3 = ROOT.parent / '配音制作_前3集/英文剧本/性转版/性转版_第03集_纯英文全文.txt'
    for version, path in [('女版', female_ep3), ('性转男版', male_ep3)]:
        project_text = path.read_text(encoding='utf-8')
        assert '"' + SELECTED_DIALOGUE[version][23] + '"' in project_text
        if version == '性转男版':
            assert '"' + SELECTED_DIALOGUE[version][48] + '"' in project_text
    for version in ['女版', '性转男版']:
        setup = version_setup(version)
        version_dir = HERE / version
        version_dir.mkdir(exist_ok=True)
        groups = []
        for offset in range(0, 56, 5):
            raw_shots = source['shots'][offset:offset + 5]
            group_number = offset // 5 + 1
            group_id = f'03-{group_number:02d}'
            text = header(raw_shots, setup) + '\n'
            shot_records = []
            group_assets = set()
            previous_scenes = None
            for local_index, shot in enumerate(raw_shots, 1):
                n = shot['source_shot']
                rid = f'03-{group_number:02d}-{local_index:02d}'
                full_name = PREFIXES[version] + rid
                active_scenes = tuple(scene_keys(n))
                # A new scene within a fixed five-source-shot group receives its own setup.
                if previous_scenes is not None and active_scenes != previous_scenes:
                    same_scene_run = []
                    for following in raw_shots[local_index - 1:]:
                        if tuple(scene_keys(following['source_shot'])) != active_scenes:
                            break
                        same_scene_run.append(following)
                    text += header(same_scene_run, setup) + '\n'
                previous_scenes = active_scenes
                sem = semantic[str(n)]
                duration = shot['timing']['duration_seconds_decimal']
                fields = {
                    '时长': duration + f'秒（{full_name}（原镜{n:02d}））',
                    '环境氛围': translated_geometry(shot['source_fields']['环境氛围'], setup),
                    '景别': shot['source_fields']['景别变化'],
                    '拍摄角度': translated_geometry(shot['source_fields']['拍摄角度'] + '；' + shot['source_fields']['画面构图'], setup),
                    '摄像机运动': shot['source_fields']['摄像机运动 (运镜指令)'],
                    '人物角色和运动': sem['movement'].format_map(setup['tokens']),
                    '人物表演': sem['performance'].format_map(setup['tokens']),
                    '画面内容': sem['content'].format_map(setup['tokens']),
                }
                if n == 10:
                    fields['人物角色和运动'] += '医生衣着为所引参考图的白大褂与浅蓝衬衫。'
                if n in [15, 16, 17, 18, 21]:
                    fields['人物角色和运动'] += ('童年Eliza保持参考图米白针织开衫与浅碎花连衣裙。' if setup['female']
                                                else '童年性转男主保持参考图白衬衫与米色短裤。')
                if n == 14 or n == 15:
                    fields['人物角色和运动'] += '佣人沿用参考图黑白制服。'
                if n in [28, 29, 30, 34, 35, 36, 37, 38, 39, 40, 41, 45, 46, 48, 49, 50, 51, 52, 53, 54, 55, 56]:
                    fields['人物角色和运动'] += ('成年Eliza保持大码体型、米白针织开衫及浅碎花连衣裙。' if setup['female']
                                                else '成年性转男主保持大码体型、白衬衫及米色短裤。')
                if n == 28 and not setup['female']:
                    fields['画面内容'] = fields['画面内容'].replace('日常衣服', '白衬衫与米色短裤')
                if n == 23:
                    fields['人物表演'] = f'【{setup["tokens"]["Y"]}】微扬下巴，冷淡地启唇，只说一次英文原台词：“{SELECTED_DIALOGUE[version][23]}”'
                elif n == 48:
                    fields['人物表演'] = f'【{setup["tokens"]["P"]}】目光平静，先注视门内，再微启唇轻声提醒，只连贯说一次英文原台词：“{SELECTED_DIALOGUE[version][48]}”'
                shot_text = f'Shot{n:02d}:\n' + '\n'.join(f'{field}：{fields[field].rstrip("；。")}'+('。' if field == '画面内容' else '；') for field in FIELDS) + '\n\n'
                text += shot_text
                indices = {setup['scene_asset'][key] for key in active_scenes}
                indices.update(setup['role_asset'][role['id']] for role in shot['source_asset_requirements']['roles'] if role['id'] in setup['role_asset'])
                group_assets.update(indices)
                used_indices.update(indices)
                slot_id = f'{version}-EP03-S{n:02d}' if n in SOURCE_DIALOGUE else None
                if slot_id:
                    dialogue_slots.append({'id': slot_id, 'version': version, 'source_shot': n, 'shot_id': rid,
                                           'source_xlsx_english_verbatim': SOURCE_DIALOGUE[n],
                                           'project_english_corresponding_verbatim': SELECTED_DIALOGUE[version][n],
                                           'project_match_note': '同一选人事件；性转对象代词按项目原句。' if n == 23
                                                                 else '女版完整英文原稿EP04第117段敲门叙述后，第118段同一门外催睡原句；按用户决定仅台词跨集界，不迁移剧情。' if setup['female']
                                                                 else '同一催睡场景，但源表与项目原句单词不完全相同。',
                                           'speaker': setup['tokens']['Y'] if n == 23 else setup['tokens']['P'],
                                           'selected_english_verbatim': SELECTED_DIALOGUE[version][n],
                                           'project_source_path': str(female_docx if setup['female'] and n == 48 else female_ep3 if setup['female'] else male_ep3),
                                           'project_source_sha256': sha(female_docx if setup['female'] and n == 48 else female_ep3 if setup['female'] else male_ep3),
                                           'source_episode': 4 if setup['female'] and n == 48 else 3,
                                           'source_docx_paragraph': 118 if setup['female'] and n == 48 else None,
                                           'cross_episode_dialogue_only': setup['female'] and n == 48,
                                           'delivery_count_across_continuous_shots': 1,
                                           'status': 'filled_from_project_english_verbatim'})
                shot_records.append({'source_shot': n, 'source_row': shot['source_row'], 'shot_id': rid,
                                     'full_name': full_name, 'full_name_with_source': f'{full_name}（原镜{n:02d}）',
                                     'prompt_label': f'Shot{n:02d}', 'duration_seconds': float(Decimal(duration)),
                                     'source_TC': shot['timing']['raw'], 'fields': fields, 'prompt': shot_text,
                                     'asset_names': [NAMES[i] for i in sorted(indices)], 'dialogue_slot': slot_id,
                                     'source_image_path': shot['screenshot']['path'], 'source_image_sha256': shot['screenshot']['sha256'],
                                     'visual_review_completed': True})
            assert len(text) < 5000, (version, group_id, len(text))
            target = version_dir / f'{version}{group_id}.txt'
            target.write_text(text.rstrip() + '\n', encoding='utf-8')
            groups.append({'version': version, 'episode': 3, 'group': group_number, 'group_id': group_id,
                           'source_shots': [s['source_shot'] for s in raw_shots], 'shot_ids': [r['shot_id'] for r in shot_records],
                           'full_shot_names': [r['full_name'] for r in shot_records],
                           'platform_card_name': shot_records[0]['full_name'],
                           'prompt_file': str(target), 'prompt': text.rstrip() + '\n', 'character_count': len(text.rstrip() + '\n'),
                           'asset_names': [NAMES[i] for i in sorted(group_assets)],
                           'total_duration': float(sum(Decimal(s['timing']['duration_seconds_decimal']) for s in raw_shots)),
                           'shots': shot_records, 'status': 'text_ready_for_upload',
                           'platform_references_actually_bound': False, 'generation_submitted': False})
        payload = {'version': version, 'episode': 3, 'source_shots_total': 56, 'groups_total': 12,
                   'prompt_format': 'short-drama-prompts-v3; original Shot01..56 retained; five source shots per group, final one retained',
                   'source_workbook_sha256': source['source_workbook']['sha256'],
                   'source_json_sha256': sha(SOURCE), 'groups': groups}
        (version_dir / 'groups.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        versions.append(payload)
    provenance = []
    for i in sorted(used_indices):
        record = records[i]
        path = Path(record['local_path'])
        if not path.exists():
            found = list((ROOT / '飞书资产').glob(f'{i:02d}_*.png'))
            assert len(found) == 1, (i, found)
            path = found[0]
        provenance.append({'index': i, 'prompt_asset_name': NAMES[i], 'download_local_name': record.get('local_asset_name'),
                           'path': str(path), 'sha256': sha(path), 'Feishu_nodeId': record['nodeId'],
                           'real_platform_binding_verified': False})
    combined = {'schema_version': 1, 'episode': 3,
                'prepared_at': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
                'status': 'two_versions_112_source_shots_text_ready_for_upload',
                'authority': source['authority'], 'source_shot_count_per_version': 56, 'versions': versions,
                'groups': [g for v in versions for g in v['groups']], 'actual_asset_provenance': provenance,
                'dialogue_slots': dialogue_slots,
                'limitations': ['True dialogue uses the user-selected original project English quotations. Female door dialogue is sourced from the same doorway reminder scene in EP04; no scene/story was moved or added.',
                               'All source TC/durations, including 0.1s transition rows and the final one-shot group, remain unchanged.',
                               'Named character costumes and appearances follow the supplied Feishu cards, replacing conflicting reference-film costumes; generic extras without cards are explicitly pending reference.',
                               'Source image eye-line/pose/dynamic ambiguities remain documented in visual_qc.json, without pretending that still frames prove complete motion.',
                               '07童年Eliza卡标注110cm及5.0头身，显著较源表13岁幼；正文采用指定卡、只称童年角色，源表年龄仍保留来源字段。',
                               'Character/scene cards are references only; multi-view collages, labels and split-screen card layout are not copied into the shot.'],
                'naming_contract': {'女版': '大码女版EE-GG-SS', '性转男版': '性转版男版EE-GG-SS',
                                    'original_source_shot_retained': True, 'platform_card_name': 'first_full_shot_name_in_group'},
                'platform_or_Resolve_actions': False, 'generation_submitted': False}
    (HERE / 'groups.json').write_text(json.dumps(combined, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (HERE / 'dialogue_slots.json').write_text(json.dumps({'status': 'all_four_filled_from_project_english_original', 'slots': dialogue_slots}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'version_counts': {v['version']: sum(len(g['source_shots']) for g in v['groups']) for v in versions},
                      'group_count': len(combined['groups']), 'max_group_characters': max(g['character_count'] for g in combined['groups']),
                      'dialogue_slots': len(dialogue_slots), 'output': str(HERE / 'groups.json')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
