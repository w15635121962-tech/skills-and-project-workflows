"""Classify the exact native audit without Resolve access or changing raw evidence.

Only documented read-context differences may be separated from actual AV edits:
track enabled flags require parent activation readback; the eight named audio
effect keys may be absent in an inactive timeline only when their available side
is literally False or numeric zero. Every other difference remains a failure.
"""
import collections
import datetime
import hashlib
import json
from pathlib import Path
import re

OUT = Path(__file__).resolve().parent
SUB = OUT.parent
DEFAULT_AUDIO_KEYS = {
    'AudioDialogueLevelerBackgroundReduction', 'AudioDialogueLevelerEnabled',
    'AudioDialogueLevelerLiftSoftDialogue', 'AudioDialogueLevelerMode',
    'AudioDialogueLevelerOutputGain', 'AudioDialogueLevelerReduceLoudDialogue',
    'AudioVoiceIsolationAmount', 'AudioVoiceIsolationEnabled',
}


def is_default(value):
    return value is False or (type(value) in (float, int) and value == 0)


raw = json.loads((OUT / 'Resolve_字幕保存重开_最终审计.json').read_text(encoding='utf-8'))
snapshot = json.loads((OUT / 'Resolve_字幕保存重开_原生实读.json').read_text(encoding='utf-8'))
before = json.loads((SUB / 'Resolve_AV冻结对照.json').read_text(encoding='utf-8'))
style = json.loads((SUB / '保存重开回读.json').read_text(encoding='utf-8'))
assert raw['project'] == before['project'] == style['project'] == '大码枕头'
old_by_ep = {e['episode']: e for e in before['episodes']}
now_by_ep = {e['episode']: e for e in snapshot}
style_by_ep = {e['ep']: e for e in style['episodes']}
report = {
    'checked_at': datetime.datetime.now().isoformat(), 'scope': 'Offline only; no Resolve connection.',
    'raw_exact_report': 'Resolve_字幕保存重开_最终审计.json',
    'raw_exact_dictionary_equal_all_episodes': all(e['av_all_fields_exact'] for e in raw['episodes']),
    'interpretation': 'Do not describe all AV fields as byte-for-byte equal. Shared AV values, source/cut boundaries, links, speed and volume must remain exact. Track enabled flags are checked independently on activated timelines. Only absent/present zero-default keys listed below are read-context differences.',
    'default_key_allowlist': sorted(DEFAULT_AUDIO_KEYS), 'episodes': [],
}
for e in raw['episodes']:
    ep = e['episode']
    track_flags, default_presence, failures = [], [], []
    for difference in e['av_differences']:
        key = difference['path'].rsplit('.', 1)[-1]
        if re.fullmatch(r'tracks\.(audio|video)\[\d+\]\.enabled', difference['path']):
            track_flags.append(difference)
        elif (difference['kind'] in ('missing_key', 'unexpected_key')
              and '.items[' in difference['path'] and '.properties.' in difference['path']
              and difference['path'].startswith('tracks.audio[')
              and key in DEFAULT_AUDIO_KEYS
              and is_default(difference.get('expected', difference.get('actual')))):
            default_presence.append(difference)
        else:
            failures.append(difference)
    old, now = old_by_ep[ep], now_by_ep[ep]['av']
    common_property_changes = []
    item_counts = {'video': 0, 'audio': 0}
    for kind in ('video', 'audio'):
        for old_track, now_track in zip(old['tracks'][kind], now['tracks'][kind]):
            for old_item, now_item in zip(old_track['items'], now_track['items']):
                item_counts[kind] += 1
                for key in old_item['properties'].keys() & now_item['properties'].keys():
                    if old_item['properties'][key] != now_item['properties'][key]:
                        common_property_changes.append({'id': old_item['id'], 'key': key,
                            'before': old_item['properties'][key], 'now': now_item['properties'][key]})
    style_ep = style_by_ep[ep]
    style_persisted = (style_ep['track_fields_hash_before'] == style_ep['track_fields_hash_reopened']
                       and style_ep['track_style_payload_persisted'])
    subtitles = now_by_ep[ep]['subtitle_tracks']
    row = {
        'episode': ep, 'video_clips': item_counts['video'], 'audio_clips': item_counts['audio'],
        'all_shared_AV_properties_exact': not common_property_changes,
        'shared_property_changes': common_property_changes,
        'all_source_boundaries_offsets_pool_ids_links_speed_volume_exact':
            not failures and e['source_offsets_and_pool_ids_exact'],
        'unexplained_or_nondefault_differences': failures,
        'read_context_zero_default_key_presence_only': {
            'difference_count': len(default_presence),
            'patterns': dict(collections.Counter(x['path'].rsplit('.', 1)[-1] + ':' + x['kind']
                                                 for x in default_presence)),
            'all_available_values_false_or_numeric_zero': all(
                is_default(x.get('expected', x.get('actual'))) for x in default_presence)},
        'track_enabled_flags': {
            'status': 'requires_independent_per_timeline_activated_readback',
            'raw_before_now_differences': track_flags,
            'native_readback': {k: [{'index': t['index'], 'enabled': t['enabled']}
                                   for t in now['tracks'][k]] for k in ('video', 'audio')},
            'subtitle_readback': [{'index': t['index'], 'enabled': t['enabled']} for t in subtitles]},
        'subtitle_count': e['actual_cues'], 'subtitle_track_name': e['subtitle_track_name'],
        'all_native_subtitle_text_and_frame_times_exact': e['text_and_frame_times_exact'],
        'all_subtitle_items_enabled': e['all_subtitle_clips_enabled'],
        'max_explicit_subtitle_lines': e['max_explicit_lines'],
        'subtitle_track_style_payload_persisted': bool(style_persisted),
        'subtitle_track_style_fields_hash': style_ep['track_fields_hash_reopened'],
        'semantic_AV_and_caption_data_pass_except_activation_flags':
            not failures and not common_property_changes and e['source_offsets_and_pool_ids_exact']
            and e['text_and_frame_times_exact'] and e['all_subtitle_clips_enabled']
            and e['subtitles_within_timeline'] and e['max_explicit_lines'] <= 3
            and e['subtitle_track_name'] == str(ep) and style_persisted,
    }
    report['episodes'].append(row)
report['native_subtitle_total'] = sum(e['subtitle_count'] for e in report['episodes'])
report['all_197_subtitle_text_frames_exact'] = (
    report['native_subtitle_total'] == 197
    and all(e['all_native_subtitle_text_and_frame_times_exact'] for e in report['episodes']))
report['semantic_data_pass_except_activation_flags'] = all(
    e['semantic_AV_and_caption_data_pass_except_activation_flags'] for e in report['episodes'])
report['context_unchanged_during_native_audit'] = raw['context_unchanged']
activation_path = OUT / '逐集激活_轨启用回读.json'
if activation_path.exists():
    activation = json.loads(activation_path.read_text(encoding='utf-8'))
    active_by_ep = {e['ep']: e for e in activation['episodes']}
    assert sorted(active_by_ep) == sorted(old_by_ep), 'Activation evidence must cover exactly all five targets'
    report['independent_activation_evidence'] = {
        'path': str(activation_path), 'checked_at': activation['checked_at'],
        'sha256': hashlib.sha256(activation_path.read_bytes()).hexdigest(),
        'method': activation['reason'], 'read_offline_by_this_audit': True,
    }
    for e in report['episodes']:
        ep = e['episode']
        active = active_by_ep[ep]
        base = old_by_ep[ep]
        passed = (active['timeline_id'] == active['active_timeline_id'] == base['id']
                  and active['subtitle_name'] == str(ep)
                  and active['subtitle_enabled'] is True
                  and len(active['video_enabled']) == len(base['tracks']['video'])
                  and len(active['audio_enabled']) == len(base['tracks']['audio'])
                  and all(x is True for x in active['video_enabled'])
                  and all(x is True for x in active['audio_enabled'])
                  and active['cue_count'] == e['subtitle_count'])
        e['track_enabled_flags']['status'] = 'verified_enabled_while_exact_target_timeline_active' if passed else 'FAILED'
        e['track_enabled_flags']['activation_evidence'] = active
        e['track_enabled_flags']['activation_verified'] = passed
        e['final_semantic_audit_passed'] = (
            e['semantic_AV_and_caption_data_pass_except_activation_flags'] and passed)
    report['all_activation_checks_passed'] = all(
        e['track_enabled_flags']['activation_verified'] for e in report['episodes'])
    report['all_semantic_native_and_activation_checks_passed'] = (
        all(e['final_semantic_audit_passed'] for e in report['episodes'])
        and report['all_197_subtitle_text_frames_exact']
        and report['context_unchanged_during_native_audit'])
    report['final_conclusion'] = (
        '五集语义审计总体通过：共有AV属性、源边界、offset、源池ID、链接、速度与音量精确不变；197条字幕正文与帧入出逐条一致，轨名21–25，显式最多三行；各集在其本身为当前时间线时视频、两条音频及字幕轨均启用；字幕轨样式FieldsBlob保存重开哈希一致。原始全字典受上下文默认键及非当前轨标记影响，未声称全部字段逐字一致。'
        if report['all_semantic_native_and_activation_checks_passed'] else '存在未通过项，详见分集报告。')
else:
    report['all_activation_checks_passed'] = None
    report['all_semantic_native_and_activation_checks_passed'] = None
path = OUT / 'Resolve_字幕保存重开_语义审计.json'
path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'path': str(path), 'all_197_subtitle_text_frames_exact': report['all_197_subtitle_text_frames_exact'],
                  'semantic_data_pass_except_activation_flags': report['semantic_data_pass_except_activation_flags'],
                  'raw_full_AV_dict_equal': report['raw_exact_dictionary_equal_all_episodes'],
                  'all_activation_checks_passed': report['all_activation_checks_passed'],
                  'all_semantic_native_and_activation_checks_passed':
                    report['all_semantic_native_and_activation_checks_passed']},
                 ensure_ascii=False, indent=2))
