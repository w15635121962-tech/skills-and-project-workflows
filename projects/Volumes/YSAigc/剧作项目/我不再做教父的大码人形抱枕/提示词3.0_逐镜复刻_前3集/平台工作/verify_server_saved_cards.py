#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Offline-only verification of previously captured real storyboard list responses.

Reads six captures, six approved groups.json files and the filling progress.
Never accesses a browser, network, credentials, editor or generation endpoint.
"""

from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
import datetime
import difflib
import hashlib
import json
import re


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PREFIX = {'女版': '大码女版', '性转男版': '性转版男版'}
NEWLINES = re.compile(r'[\r\n\u2028\u2029]')
FULL_NAME = re.compile(r'(?:大码女版|性转版男版)\d{2}-\d{2}-\d{2}')
SHOT_TAG = re.compile(r'^Shot\d+(?:-\d+)*:', re.MULTILINE)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest_file(path):
    return sha(Path(path).read_bytes())


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def ignore_linebreaks_only(text):
    # Spaces, tabs, NBSP, punctuation and English apostrophes are NOT normalized.
    return NEWLINES.sub('', text)


class HTMLText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.fragments = []

    def handle_data(self, text):
        self.fragments.append(text)

    def handle_starttag(self, tag, attrs):
        if tag in {'p', 'div', 'br', 'li'}:
            self.fragments.append('\n')

    def handle_endtag(self, tag):
        if tag in {'p', 'div', 'li'}:
            self.fragments.append('\n')


def html_text(markup):
    if not isinstance(markup, str):
        raise ValueError('Expected an HTML string')
    parser = HTMLText()
    parser.feed(markup)
    parser.close()
    return ''.join(parser.fragments)


def difference(expected, actual):
    if expected == actual:
        return []
    result = []
    for op, a, b, c, d in difflib.SequenceMatcher(None, expected, actual, autojunk=False).get_opcodes():
        if op != 'equal':
            result.append({'operation': op, 'expected_range': [a, b], 'actual_range': [c, d],
                           'expected_excerpt': expected[a:b][:180], 'actual_excerpt': actual[c:d][:180]})
        if len(result) == 12:
            break
    return result


def main():
    progress_path = HERE / '剧梦填写进度.json'
    progress = load(progress_path)
    input_hashes = {str(progress_path): digest_file(progress_path)}
    failures, expected, actual_rows, capture_summaries = [], {}, [], []

    def check(condition, label, detail):
        if not condition:
            failures.append({'check': label, 'detail': detail})
        return bool(condition)

    for episode in (1, 2, 3):
        for version in ('女版', '性转男版'):
            path = ROOT / f'EP{episode:02d}' / version / 'groups.json'
            data = load(path)
            input_hashes[str(path)] = digest_file(path)
            source_sequence = []
            for group in data['groups']:
                index = group.get('group', group.get('group_number'))
                name = group.get('platform_card_name', group.get('card_name'))
                names = [PREFIX[version] + f'{episode:02d}-{index:02d}-{i:02d}'
                         for i in range(1, len(group['source_shots']) + 1)]
                check(name == names[0], 'expected_card_named_after_first_full_shot', name)
                check(name not in expected, 'expected_card_names_unique', name)
                path_to_prompt = Path(group.get('prompt_file', group.get('prompt_path')))
                prompt = path_to_prompt.read_text(encoding='utf-8')
                input_hashes[str(path_to_prompt)] = digest_file(path_to_prompt)
                check(prompt == group['prompt'], 'approved_groups_json_and_txt_exact', name)
                expected[name] = {'name': name, 'version': version, 'episode': episode, 'group': index,
                                  'source_shots': group['source_shots'], 'full_shot_names': names,
                                  'prompt': prompt, 'prompt_path': str(path_to_prompt),
                                  'groups_path': str(path), 'asset_names': group['asset_names']}
                source_sequence.extend(group['source_shots'])
            check(source_sequence == list(range(1, len(source_sequence) + 1)),
                  'expected_source_shot_sequence_has_no_gaps_or_duplicates', {'version': version, 'episode': episode})

    expected_cards = len(expected)
    expected_shots = sum(len(plan['source_shots']) for plan in expected.values())
    progress_by_name = {card['name']: card for card in progress['cards']}
    check(len(progress_by_name) == len(progress['cards']) == expected_cards,
          'progress_expected_unique_cards', len(progress['cards']))
    check(set(progress_by_name) == set(expected), 'progress_names_equal_six_approved_group_files',
          {'missing': sorted(set(expected) - set(progress_by_name)), 'extra': sorted(set(progress_by_name) - set(expected))})

    for episode in (1, 2, 3):
        for version in ('女版', '性转男版'):
            path = HERE / f'服务端保存实读_{version}_EP{episode:02d}.json'
            captures = load(path)
            input_hashes[str(path)] = digest_file(path)
            check(isinstance(captures, list) and bool(captures), 'nonempty_capture_array', str(path))
            if not captures:
                continue
            # The current six files contain one complete capture each. If recaptured,
            # use the newest real list response and record how many were present.
            capture = max(captures, key=lambda row: row['timestamp'])
            check('requestHeaders' not in capture and 'responseHeaders' not in capture,
                  'capture_is_header_free', str(path))
            check(capture['responseStatus'] == 200 and capture['responseBodyTruncated'] is False,
                  'complete_http200_response', str(path))
            response = json.loads(capture['responsePreview'])
            check(str(response.get('code')) == '0', 'backend_success_code', str(path))
            result = response['result']
            cards = result['list']
            request = json.loads(capture['requestBodyPreview'])
            series_id = request['seriesId']
            plans = sorted((e for e in expected.values() if (e['version'], e['episode']) == (version, episode)),
                           key=lambda e: e['group'])
            check(result['total'] == len(cards) == len(plans), 'complete_series_no_missing_or_extra_cards',
                  {'version': version, 'episode': episode, 'total': result['total'], 'returned': len(cards), 'expected': len(plans)})
            check(sorted(card['boardIndex'] for card in cards) == list(range(1, len(plans) + 1)),
                  'board_indices_exactly_once_and_contiguous', {'version': version, 'episode': episode})
            by_name = {card['name']: card for card in cards}
            check(len(by_name) == len(cards), 'series_card_names_unique', {'version': version, 'episode': episode})
            check(set(by_name) == {p['name'] for p in plans}, 'series_names_exact',
                  {'version': version, 'episode': episode, 'actual': sorted(by_name)})
            capture_summaries.append({'capture_path': str(path), 'capture_sha256': digest_file(path),
                                      'capture_count': len(captures), 'used_timestamp': capture['timestamp'],
                                      'responseStatus': capture['responseStatus'], 'responseBodyTruncated': capture['responseBodyTruncated'],
                                      'responsePreview_sha256': sha(capture['responsePreview'].encode('utf-8')),
                                      'version': version, 'episode': episode, 'seriesId': series_id,
                                      'server_total': result['total'], 'returned_cards': len(cards)})
            for plan in plans:
                name = plan['name']
                card = by_name.get(name)
                if card is None:
                    continue
                prior = progress_by_name.get(name)
                check(prior is not None, 'card_in_progress', name)
                identity = prior is not None and card['id'] == prior['storyBoardId'] and card['seriesId'] == prior['seriesId'] == series_id
                identity = identity and card['boardIndex'] == plan['group'] == prior['group'] and card['projectId'] == progress['project_id']
                identity = identity and prior['episode'] == episode and prior['version'] == version and prior['source_shots'] == plan['source_shots']
                check(identity, 'id_name_boardIndex_seriesId_projectId_match_progress_and_groups', name)
                check(card['isErase'] == 0, 'card_is_not_erased', name)
                plain = html_text(card['videoPrompt'])
                normalized = ignore_linebreaks_only(plain)
                expected_text = ignore_linebreaks_only(plan['prompt'])
                text_match = normalized == expected_text
                check(text_match, 'server_videoPrompt_exact_except_linebreaks', name)
                extra = json.loads(card['extraJson']) if isinstance(card['extraJson'], str) else card['extraJson']
                omni = extra['workspaces']['omni']
                omni_plain = html_text(omni['prompt'])
                omni_match = ignore_linebreaks_only(omni_plain) == normalized
                check(omni_match, 'extra_omni_prompt_matches_videoPrompt', name)
                full_names = FULL_NAME.findall(plain)
                full_names_match = full_names == plan['full_shot_names'] and len(full_names) == len(set(full_names))
                check(full_names_match, 'all_full_shot_names_exact_once_in_order', name)
                shot_count = len(SHOT_TAG.findall(plain))
                check(shot_count == len(plan['source_shots']), 'persisted_shot_tag_count_matches_source_shots', name)
                refs = {workspace: value.get('referenceAssets') for workspace, value in extra['workspaces'].items()}
                reference_counts = {workspace: len(value) if isinstance(value, list) else None for workspace, value in refs.items()}
                check(all(isinstance(value, list) for value in refs.values()), 'referenceAssets_have_verifiable_array_values', name)
                reference_bound = any(bool(value) for value in refs.values())
                no_generation = card['videoTaskId'] == card['videoTaskStatus'] == 0 and not card['videoList']
                check(no_generation, 'no_current_video_generation_task_or_result', name)
                actual_rows.append({'name': name, 'version': version, 'episode': episode, 'group': plan['group'],
                                    'id': card['id'], 'boardIndex': card['boardIndex'], 'seriesId': card['seriesId'],
                                    'projectId': card['projectId'], 'isErase': card['isErase'],
                                    'identity_matches_progress_and_group': bool(identity), 'source_shots': plan['source_shots'],
                                    'full_shot_names_expected': plan['full_shot_names'], 'full_shot_names_actual': full_names,
                                    'full_names_exact_once_in_order': full_names_match, 'persisted_shot_tag_count': shot_count,
                                    'videoPrompt_text_matches_except_linebreaks': text_match,
                                    'expected_text_sha256_ignoring_only_linebreaks': sha(expected_text.encode('utf-8')),
                                    'server_text_sha256_ignoring_only_linebreaks': sha(normalized.encode('utf-8')),
                                    'expected_text_length_ignoring_only_linebreaks': len(expected_text),
                                    'server_text_length_ignoring_only_linebreaks': len(normalized),
                                    'text_difference_operations': difference(expected_text, normalized),
                                    'extra_omni_prompt_matches_videoPrompt_text': omni_match,
                                    'extra_omni_prompt_raw_html_equal_to_videoPrompt': omni['prompt'] == card['videoPrompt'],
                                    'referenceAssets_counts': reference_counts, 'reference_binding_status': 'bound' if reference_bound else 'not_bound',
                                    'textual_at_names_are_not_real_reference_binding': True,
                                    'videoTaskId': card['videoTaskId'], 'videoTaskStatus': card['videoTaskStatus'],
                                    'video_result_count': len(card['videoList'] or []),
                                    'video_result_field_is_null': card['videoList'] is None,
                                    'no_current_video_generation_task_or_result': no_generation,
                                    'imageTaskId': card['imageTaskId'], 'imageTaskStatus': card['imageTaskStatus'],
                                    'audioTaskId': card['audioTaskId'], 'audioTaskStatus': card['audioTaskStatus'],
                                    'planned_prompt_path': plan['prompt_path'], 'capture_path': str(path),
                                    'server_createAt': card.get('createAt'), 'server_updateAt': card.get('updateAt')})

    ids = [r['id'] for r in actual_rows]
    all_names = [r['name'] for r in actual_rows]
    full_names = [n for r in actual_rows for n in r['full_shot_names_actual']]
    check(len(actual_rows) == len(set(ids)) == len(set(all_names)) == expected_cards,
          'expected_unique_server_cards_ids_names', len(actual_rows))
    check(len(full_names) == len(set(full_names)) == expected_shots,
          'expected_unique_persisted_full_shot_names', len(full_names))
    check(set(all_names) == set(expected), 'no_missing_extra_cards_across_six_series', len(all_names))
    for path, original in input_hashes.items():
        check(digest_file(path) == original, 'read_inputs_unchanged_during_audit', path)
    reference_states = Counter(r['reference_binding_status'] for r in actual_rows)
    report = {'schema_version': 1, 'checked_at': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
              'status': 'server_save_verified_references_not_bound_no_generation' if not failures and reference_states.get('not_bound') == expected_cards else 'inspect_findings',
              'save_verification_passed': not failures, 'failure_count': len(failures), 'failures': failures,
              'scope': 'Read-only offline parsing of six real complete backend api/list response bodies, the progress record and six approved group JSONs. No browser/network/Resolve calls and no source/progress/prompt mutation.',
              'comparison_policy': 'HTMLParser decodes HTML text; only CR, LF, U+2028 and U+2029 linebreaks are ignored. English word spaces, tabs, NBSP, apostrophes and punctuation remain exact.',
              'summary': {'captured_series': len(capture_summaries), 'persisted_cards': len(actual_rows),
                          'unique_card_ids': len(set(ids)), 'persisted_shots': len(full_names), 'unique_full_shot_names': len(set(full_names)),
                          'cards_body_text_exact_except_linebreaks': sum(r['videoPrompt_text_matches_except_linebreaks'] for r in actual_rows),
                          'cards_omni_prompt_matches_videoPrompt': sum(r['extra_omni_prompt_matches_videoPrompt_text'] for r in actual_rows),
                          'cards_omni_raw_html_equal': sum(r['extra_omni_prompt_raw_html_equal_to_videoPrompt'] for r in actual_rows),
                          'references_not_bound_cards': reference_states.get('not_bound', 0), 'references_bound_cards': reference_states.get('bound', 0),
                          'cards_with_no_current_video_task_or_result': sum(r['no_current_video_generation_task_or_result'] for r in actual_rows),
                          'progress_generation_submitted_flag': progress.get('generation_submitted')},
              'captures': capture_summaries, 'cards': actual_rows, 'inputs_sha256': input_hashes,
              'limitations': ['This audit proves saved content in the captured real server responses at their capture times; it performs no fresh browser request.',
                              'Textual @asset names alone do not bind assets; the report records actual referenceAssets array counts.',
                              'Zero videoTaskId/videoTaskStatus with no results describes current card task state, not a claim that any video has been generated.'],
              'credentials_or_headers_copied_into_report': False}
    output = HERE / '剧梦服务端逐卡保存核验.json'
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    text_report = [f'服务端逐卡保存核验：{"通过" if not failures else "需核对"}',
                   f'6集／两版：{len(actual_rows)}卡，{len(full_names)}镜；卡ID、名称、集seriesId及boardIndex逐项对照。',
                   f'仅忽略换行后，正文完全一致：{report["summary"]["cards_body_text_exact_except_linebreaks"]}/{expected_cards}卡；omni正文一致：{report["summary"]["cards_omni_prompt_matches_videoPrompt"]}/{expected_cards}卡。',
                   f'完整镜名唯一数：{len(set(full_names))}；缺卡／重号等核验失败数：{len(failures)}。',
                   f'参考素材：{reference_states.get("not_bound", 0)}卡尚未绑定，@文字不算真实绑定。',
                   f'当前视频任务及结果：{report["summary"]["cards_with_no_current_video_task_or_result"]}卡均videoTaskId=0、videoTaskStatus=0且无结果，未见生成。',
                   '本次只读既有服务端响应，未更改正文、进度或清单，未操作浏览器。']
    (HERE / '剧梦服务端逐卡保存核验.txt').write_text('\n'.join(text_report) + '\n', encoding='utf-8')
    print(json.dumps({'save_verification_passed': report['save_verification_passed'], 'failure_count': len(failures),
                      'failures': failures, 'summary': report['summary'], 'output': str(output)}, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == '__main__':
    raise SystemExit(main())
