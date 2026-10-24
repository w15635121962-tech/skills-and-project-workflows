#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Preserve the entire EP03 XLSX storyboard with XML/image provenance. Read-only input."""

from pathlib import Path, PurePosixPath
from zipfile import ZipFile
from decimal import Decimal
from collections import Counter
import datetime
import hashlib
import json
import posixpath
import re
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
XLSX = ROOT / '对标剧分镜截图和对标剧样片/分镜表格/电影级落地拍摄分镜脚本_人形抱枕第三集.xlsx'
IMAGE_DIR = ROOT / '对标剧分镜截图和对标剧样片/分镜截图/03人形抱枕_分镜截图_按时间 2'
SCRIPTS = {
    '女版': ROOT / '配音制作_前3集/英文剧本/女版/女版_第03集_纯英文全文.txt',
    '性转男版': ROOT / '配音制作_前3集/英文剧本/性转版/性转版_第03集_纯英文全文.txt',
}
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
      'p': 'http://schemas.openxmlformats.org/package/2006/relationships',
      'd': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def jpeg_dimensions(data):
    if data[:2] != b'\xff\xd8':
        return None
    cursor = 2
    frame_markers = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                     0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    while cursor < len(data):
        if data[cursor] != 255:
            cursor += 1
            continue
        while data[cursor] == 255:
            cursor += 1
        marker = data[cursor]
        cursor += 1
        if marker in {0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
            continue
        length = int.from_bytes(data[cursor:cursor + 2], 'big')
        if marker in frame_markers:
            return [int.from_bytes(data[cursor + 5:cursor + 7], 'big'),
                    int.from_bytes(data[cursor + 3:cursor + 5], 'big')]
        if length < 2:
            raise ValueError('Invalid JPEG segment length')
        cursor += length
    raise ValueError('No JPEG frame dimensions found')


def resolve_part(base, target):
    return target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join(posixpath.dirname(base), target))


def relationships(archive, source):
    part = str(PurePosixPath(source).parent / '_rels' / (PurePosixPath(source).name + '.rels'))
    if part not in archive.namelist():
        return {}
    return {r.get('Id'): {'type': r.get('Type'), 'target': resolve_part(source, r.get('Target')),
                          'target_mode': r.get('TargetMode')}
            for r in ET.fromstring(archive.read(part)).findall('p:Relationship', NS)}


def range_set(*ranges):
    return {n for low, high in ranges for n in range(low, high + 1)}


ROLES = [
    ('adult_pillow_pajamas', '原片成年女主／人形抱枕（碎花睡衣）', range_set((1, 6)),
     '浅棕长发、碎刘海；米白底粉色小碎花翻领睡衣。两版按同一镜头作形象/性别适配，实际素材名待飞书。'),
    ('adult_don_black_robe', '原片成年男主／黑帮教父（黑色睡袍）', {1, 2},
     '黑发、胡茬、颈胸玫瑰纹身；黑色丝绸滚边敞领睡袍。'),
    ('young_don_13', '原片13岁少年男主（黑色西装礼服）', range_set((8, 9), (19, 26)),
     '黑色三件套西装、白衬衫、黑领结；13岁是本次源表年龄，不以旧女版英文18岁改写。'),
    ('psychologist', '心理医生', range_set((10, 11)), '深色西装；手持黑金钢笔及黑色A4文件夹／写字板。'),
    ('family_elder', '家族长老及戒指手部', range_set((10, 13)), '深色西装；部分白发；前景右手戴两枚黑宝石金戒指。'),
    ('family_head', '背对镜头的家族首领', {11}, '中央深红丝绒高背主位；背对摄影机。'),
    ('candidate_children', '候选少男少女群演', range_set((14, 16), (21, 21)), '随盛装家长排队；后续女稿角色体型锁定等待实际素材。'),
    ('candidate_parents', '候选人家长群演', range_set((14, 16), (18, 18), (21, 21)), '西装／套裙正装；浅粉套裙贵妇，米色正装父母等按源图分别核。'),
    ('maid', '门口侍女／管家', range_set((14, 15)), '粉色套裙；台阶旁站立，是否持续入画待逐图核。'),
    ('young_pillow_13', '原片13岁童年女主／候选人', range_set((14, 18), (21, 21)),
     '破旧深藏青连帽卫衣戴兜帽，水洗破洞牛仔裤；站立困倦后在柱脚／花坛角落席地熟睡。'),
    ('bodyguards_pair', '两名黑西装保镖', {19}, '黑西装、黑领带；随少年走出门后分列两侧。'),
    ('adult_pillow_daywear', '原片成年女主／人形抱枕（日常衬衫开衫）',
     range_set((28, 30), (34, 41), (45, 46), (48, 56)),
     '米白彼得潘花边领打褶衬衫、米色针织开衫、浅米百褶裙；部分镜头只见开衫右手或领口。'),
    ('don_mother', '原片男主母亲／教父夫人', range_set((31, 33)),
     '深棕盘发、黑色修身西装套裙；左手无名指钻戒；深红丝绒高背扶手椅上交腿端坐。'),
    ('adult_don_burgundy_shirt', '原片成年男主／黑帮教父（酒红衬衫）', range_set((41, 44), (47, 47)),
     '酒红敞领衬衫、黑西裤、玫瑰纹身；右手指节原片字母纹身。'),
    ('adult_blonde_lover', '原片成年金发女伴', range_set((41, 44)),
     '白色抹胸、黑西装外套搭在腰腿；44镜左手金戒覆在成年男主右手背。'),
]

SCENES = [
    ('apartment_bedroom_night', '女主公寓卧室／床头，暖黄夜景', range_set((1, 6))),
    ('estate_inner_doors_memory', '庄园内部黑色双开木门／哥特拱窗，冷调回忆', range_set((4, 7))),
    ('estate_consulting_room', '庄园心理诊疗／会客室', range_set((8, 10))),
    ('estate_meeting_hall_day', '庄园挑高会客大厅，日间议事', range_set((11, 13))),
    ('estate_forecourt_day', '庄园大门前庭院车道／石柱花坛角落，白天', range_set((14, 18), (21, 21))),
    ('estate_entry_steps_day', '庄园主楼正门拱廊及台阶，白天', range_set((19, 26))),
    ('estate_hall_night', '庄园挑高大厅／冷蓝高窗月光，夜晚', range_set((25, 30), (36, 41))),
    ('estate_reception_warning', '庄园会客厅／主母训话，暖暗调', range_set((31, 36))),
    ('estate_luxury_bedroom_night', '庄园奢华主卧／酒红金雕床头，夜晚', range_set((41, 44), (47, 47))),
    ('estate_bedroom_corridor_night', '庄园主卧木门外走廊／垂直门缝，夜晚', range_set((45, 46), (48, 56))),
]

PROP_TERMS = ['床头', '床品', '枕头', '台灯', '双开', '门把手', '格纹', '钢笔', '文件夹', '写字板',
              '诊断报告', '候选人名单', '档案', '黑宝石', '黑曜石', '钻戒', '金戒', '扶手椅', '丝绒沙发',
              '水晶吊灯', '油画', '肖像画', '茶几', '地毯', '斗柜', '边柜', '石柱', '花坛', '绣球花',
              '喷泉', '栏杆', '门框', '门板', '窗帘', '纹身', '领结', '兜帽', '牛仔裤']


def main():
    original = XLSX.read_bytes()
    issues, shots, sheet_metadata, all_source_rows = [], [], [], []
    with ZipFile(XLSX) as archive:
        shared = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            shared = [''.join(si.findall('.//m:t', NS)[j].text or '' for j in range(len(si.findall('.//m:t', NS))))
                      for si in ET.fromstring(archive.read('xl/sharedStrings.xml')).findall('m:si', NS)]
        workbook = ET.fromstring(archive.read('xl/workbook.xml'))
        workbook_rels = relationships(archive, 'xl/workbook.xml')
        for sheet in workbook.findall('m:sheets/m:sheet', NS):
            part = workbook_rels[sheet.get('{%s}id' % NS['r'])]['target']
            xml = ET.fromstring(archive.read(part))
            headers, image_anchors = {}, {}
            sheet_rels = relationships(archive, part)
            for drawing in xml.findall('m:drawing', NS):
                drawing_part = sheet_rels[drawing.get('{%s}id' % NS['r'])]['target']
                drawing_rels = relationships(archive, drawing_part)
                for anchor in ET.fromstring(archive.read(drawing_part)):
                    origin = anchor.find('d:from', NS)
                    blip = anchor.find('.//a:blip', NS)
                    if origin is None or blip is None:
                        issues.append({'type': 'unmapped_drawing_anchor', 'drawing_part': drawing_part})
                        continue
                    row = int(origin.findtext('d:row', namespaces=NS)) + 1
                    col = int(origin.findtext('d:col', namespaces=NS)) + 1
                    rid = blip.get('{%s}embed' % NS['r'])
                    media_part = drawing_rels[rid]['target']
                    data = archive.read(media_part)
                    image_anchors.setdefault(row, []).append({'drawing_part': drawing_part, 'relationship_id': rid,
                                                              'anchor_row': row, 'anchor_column': col,
                                                              'media_part': media_part, 'sha256': digest(data),
                                                              'byte_count': len(data), 'pixel_dimensions': jpeg_dimensions(data)})
            rows = []
            for row in xml.findall('m:sheetData/m:row', NS):
                cells = {}
                for cell in row.findall('m:c', NS):
                    address, kind = cell.get('r'), cell.get('t')
                    column = re.sub(r'\d+', '', address)
                    value = cell.findtext('m:v', default='', namespaces=NS)
                    if kind == 's':
                        value = shared[int(value)]
                    elif kind == 'inlineStr':
                        value = ''.join(t.text or '' for t in cell.findall('m:is//m:t', NS))
                    formula = cell.findtext('m:f', default=None, namespaces=NS)
                    cells[column] = {'address': address, 'value': value, 'cell_type': kind,
                                     'style_index': cell.get('s'), 'formula': formula,
                                     'xml': ET.tostring(cell, encoding='unicode')}
                row_record = {'sheet': sheet.get('name'), 'row': int(row.get('r')),
                              'row_attributes': dict(row.attrib), 'cells': cells}
                rows.append(row_record)
                if row_record['row'] == 3:
                    headers = {col: c['value'] for col, c in cells.items()}
            sheet_metadata.append({'name': sheet.get('name'), 'sheet_id': sheet.get('sheetId'),
                                   'xml_part': part, 'xml_sha256': digest(archive.read(part)),
                                   'dimension': xml.find('m:dimension', NS).get('ref'),
                                   'merged_cells': [m.get('ref') for m in xml.findall('m:mergeCells/m:mergeCell', NS)],
                                   'header_row': 3, 'headers': headers})
            all_source_rows.extend(rows)
            for row in rows:
                number = row['cells'].get('A', {}).get('value', '')
                if row['row'] <= 3 or not re.fullmatch(r'\d+', number):
                    continue
                shot = int(number)
                fields = {headers[col]: row['cells'].get(col, {}).get('value', '') for col in 'ABCDEFGHIJK'}
                timing = fields['时长 (TC/秒)']
                match = re.fullmatch(r'(\d{2}):(\d{2}\.\d+)\s*-\s*(\d{2}):(\d{2}\.\d+)\s*\((\d+(?:\.\d+)?)s\)', timing)
                if match is None:
                    raise ValueError(f'Unparsed exact TC: {timing!r}')
                sm, ss, em, es, duration = match.groups()
                start, end, duration = Decimal(sm) * 60 + Decimal(ss), Decimal(em) * 60 + Decimal(es), Decimal(duration)
                if end - start != duration:
                    issues.append({'type': 'duration_vs_tc_mismatch', 'source_shot': shot})
                candidates = sorted(IMAGE_DIR.glob(f'shot_{shot:03d}_*.jpg'))
                if len(candidates) != 1:
                    issues.append({'type': 'screenshot_count_mismatch', 'source_shot': shot, 'paths': list(map(str, candidates))})
                external = candidates[0] if len(candidates) == 1 else None
                filename_match = re.fullmatch(r'shot_(\d+)_(\d+)m(\d+(?:\.\d+)?)s\.jpg', external.name) if external else None
                filename_start = Decimal(filename_match[2]) * 60 + Decimal(filename_match[3]) if filename_match else None
                anchors = image_anchors.get(row['row'], [])
                if len(anchors) != 1 or any(a['anchor_column'] != 2 for a in anchors):
                    issues.append({'type': 'xlsx_image_anchor_mismatch', 'source_shot': shot, 'anchors': anchors})
                external_bytes = external.read_bytes() if external else None
                external_hash = digest(external_bytes) if external_bytes else None
                byte_identical = len(anchors) == 1 and anchors[0]['sha256'] == external_hash
                if filename_start != start:
                    issues.append({'type': 'screenshot_tc_mismatch', 'source_shot': shot})
                rawtext = '\n'.join(str(v) for v in fields.values())
                raw_quotes = []
                for m in re.finditer(r'“([^”]*)”', rawtext):
                    raw_quotes.append({'text': m[1], 'prefix_context': rawtext[max(0, m.start() - 70):m.start()]})
                shots.append({'episode': 3, 'source_shot': shot, 'source_shot_label': number,
                              'sheet': row['sheet'], 'source_row': row['row'], 'source_fields': fields,
                              'source_cells': row['cells'],
                              'timing': {'raw': timing, 'start_tc': f'{sm}:{ss}', 'end_tc': f'{em}:{es}',
                                         'start_seconds_decimal': str(start), 'end_seconds_decimal': str(end),
                                         'duration_seconds_decimal': str(duration), 'duration_seconds': float(duration)},
                              'screenshot': {'path': str(external) if external else None, 'sha256': external_hash,
                                             'external_pixel_dimensions': jpeg_dimensions(external_bytes) if external_bytes else None,
                                             'filename_tc_seconds_decimal': str(filename_start), 'xlsx_anchors': anchors,
                                             'embedded_external_byte_identical': byte_identical,
                                             'encoding_note': 'XLS thumbnail is 360x640; external reference is 720x1280. Different byte hashes are expected after resize/re-encoding; row/index/TC agree, visual content still awaits eye review.',
                                             'visual_review_status': 'pending_root_contact_sheet'},
                              'source_asset_requirements': {
                                  'roles': [{'id': key, 'source_label': label, 'source_wardrobe_notes': notes,
                                             'actual_asset_name': None} for key, label, ids, notes in ROLES if shot in ids],
                                  'scenes': [{'id': key, 'source_label': label, 'actual_asset_name': None}
                                             for key, label, ids in SCENES if shot in ids],
                                  'prop_or_wardrobe_terms_found_in_source': [term for term in PROP_TERMS if term in rawtext],
                                  'role_visibility_note': 'Transition rows may contain residual/dissolving figures; these source-based requirements await per-image visual verification.'},
                              'quoted_spans_verbatim_not_yet_classified': raw_quotes,
                              'provisional_group_5': (shot - 1) // 5 + 1,
                              'version_prompt_status': {'女版': 'pending_actual_assets_and_visual_review',
                                                        '性转男版': 'pending_actual_assets_and_visual_review'}})
    shots.sort(key=lambda s: s['source_shot'])
    if [s['source_shot'] for s in shots] != list(range(1, 57)):
        issues.append({'type': 'source_shot_numbers_not_exactly_1_to_56'})
    if len(list(IMAGE_DIR.glob('shot_*.jpg'))) != 56:
        issues.append({'type': 'unexpected_external_image_count'})
    for left, right in zip(shots, shots[1:]):
        if left['timing']['end_seconds_decimal'] != right['timing']['start_seconds_decimal']:
            issues.append({'type': 'tc_gap_or_overlap', 'between': [left['source_shot'], right['source_shot']]})
    if XLSX.read_bytes() != original:
        raise RuntimeError('Source workbook changed during read')
    scripts = {version: {'path': str(path), 'sha256': digest(path.read_bytes()), 'full_text': path.read_text(encoding='utf-8')}
               for version, path in SCRIPTS.items()}
    report = {
        'schema_version': 1, 'episode': 3,
        'prepared_at': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
        'stage': 'source_parse_and_requirements_only',
        'authority': '本次XLS及截图为视觉、动作、镜序、时序、对白主源；现两版英文稿仅帮助身份和命名，不补入其新增剧情。两版基于同一56个原镜作形象／性别适配。',
        'source_workbook': {'path': str(XLSX), 'sha256': digest(original), 'unchanged_during_read': True,
                            'parser': 'Python standard library zipfile + ElementTree; no source workbook rewrite/recalculation'},
        'screenshot_directory': str(IMAGE_DIR), 'source_sheets': sheet_metadata,
        'workbook_all_rows_including_titles_and_headers': all_source_rows,
        'summary': {'source_shots': len(shots), 'source_rows': [4, 59], 'external_screenshots': 56,
                    'xlsx_embedded_images_mapped': sum(len(s['screenshot']['xlsx_anchors']) for s in shots),
                    'embedded_external_images_byte_identical': sum(s['screenshot']['embedded_external_byte_identical'] for s in shots),
                    'xlsx_thumbnail_dimensions': sorted({tuple(a['pixel_dimensions']) for s in shots for a in s['screenshot']['xlsx_anchors']}),
                    'external_image_dimensions': sorted({tuple(s['screenshot']['external_pixel_dimensions']) for s in shots}),
                    'start_seconds': float(Decimal(shots[0]['timing']['start_seconds_decimal'])),
                    'end_seconds': float(Decimal(shots[-1]['timing']['end_seconds_decimal'])),
                    'duration_sum_seconds': float(sum(Decimal(s['timing']['duration_seconds_decimal']) for s in shots)),
                    'duration_histogram_seconds': dict(Counter(s['timing']['duration_seconds_decimal'] for s in shots)),
                    'source_rows_under_one_second': [s['source_shot'] for s in shots if Decimal(s['timing']['duration_seconds_decimal']) < 1],
                    'provisional_five_shot_groups': 12, 'last_group_source_shots': [56],
                    'source_integrity_issue_count': len(issues), 'visual_image_reviews_done': 0},
        'source_integrity_issues': issues, 'shots': shots,
        'source_role_inventory': [{'id': key, 'source_label': label, 'shots': sorted(ids), 'wardrobe_notes': notes,
                                   'actual_assets_status': 'awaiting_root_Feishu_asset_names'} for key, label, ids, notes in ROLES],
        'source_scene_inventory': [{'id': key, 'source_label': label, 'shots': sorted(ids),
                                    'actual_assets_status': 'awaiting_root_Feishu_asset_names'} for key, label, ids in SCENES],
        'current_english_scripts_reference_only': scripts,
        'adaptation_difference_notes': [
            {'topic': '旧片命名', 'source': '表格VO／对白使用Dante、DeLuca、Mrs. DeLuca；最后催睡原片对白Dante, it\'s time to sleep.',
             'existing_scripts': '女稿Matteo Bellandi；性转男稿Vittoria Blackwood。实际素材名待根线程提供，未擅改原始字段。'},
            {'topic': '女版现英文第三集不是同一逐镜内容', 'source_shots': list(range(1, 57)),
             'difference': '源表从亲密睡姿进入13岁创伤／选伴回忆，再到成年后主母戒备及门外催睡；女稿含床沿拉回、腰间轻捏及三句床上对白，18岁绑架、洗衣房母亲、教育基金等。按本轮指示不为这些女稿新增剧情补镜或改源镜。'},
            {'topic': '年龄与体型', 'source': '原片少男／少女均写13岁，童年女主写瘦弱；成年女主标注年轻柔美女孩／翻拍大码女孩。',
             'instruction': '保留原字段。两版具体形象／大码体型及少年资产等待飞书映射，不偷用现女稿18岁替换源年龄。'},
            {'topic': '当前性转男稿吻合度', 'difference': '其13岁选伴、主母警告、十年陪睡、门外催睡与源片段大体对应，但Her需按性转角色改为Him；末句现稿Vittoria, time to sleep.与源片Dante, it\'s time to sleep.文字不同，后续以本次源镜与用户确定的命名适配，不直接移植旧稿。'},
        ],
        'source_ambiguities_pending_visual_review': [
            {'source_shot': 18, 'issue': 'G字段写向上摇移（或画面下移展现上半身），K字段为Tilt Up；保留两者，不能仅凭静态图确认运镜。'},
            {'source_shot': 22, 'issue': 'E字段视线右上方，G字段抬右手在画面左下示意；须按截图锁定眼线／手部而非自由修正。'},
            {'source_shot': 34, 'issue': 'E字段“端坐（或乖巧站立）”未唯一确定姿态，需逐图核定。'},
            {'source_shot': 38, 'issue': 'K字段“固定镜头（轻微呼吸感推进）”混合定机与轻推表述；按原片可见运动决定，单截图不能验证动态。'},
        ],
        'pending': ['root提供6格联系表后逐格目视记录，不将文件哈希对应称作已目视核验',
                    'root提供飞书资产准确名称后才编写两版@引用',
                    '末组仅56镜及最终命名等待根线程；不删补镜凑五镜',
                    '原0.1–0.3秒转场逐条保留；实际生成时长限制不在阶段1擅改'],
        'platform_or_Resolve_actions': False, 'generation_submitted': False,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    output = OUT / 'source_shots.json'
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(output), 'summary': report['summary'], 'issues': issues}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
