"""Offline original-speed EP18 edit, original prose and on-screen messages.

Source cuts remain native; narrative paragraphs use full, non-overlapping source
audio intervals. No new spoken messages, fabricated dialogue, loops or retiming.
"""
import json
import math
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
from subtitle_tools import cues_from_events, write_srt

FPS = 24
read = lambda p: json.loads((BASE / p).read_text())
timings = [f for f in read('ASR/旁白逐词与源段落锚点_采用版本.json')['files'] if f['episode'] == 18]
selection = {f['logical_basename']: f for f in read('ASR/旁白采用清单.json')['selections']}
levels_raw = read('ASR/source_levels.json')
levels = {f['source_path']: f for f in levels_raw['files']}
sources = {f['filename']: f for f in read('画面核验/源视频切点候选.json')['files']}
paragraphs = {}
for f in timings:
    pp = f['source_paragraph_anchors']
    duration = selection[f['basename']]['selected_audio_duration_seconds']
    final_spoken_end = max(w['end'] for w in f['source_words'])
    frame_end = math.floor(min(duration, final_spoken_end + .18) * FPS + 1e-6)
    cuts = [0]
    for a, b in zip(pp, pp[1:]):
        a_end = a['observed_last_matching_word_end_seconds']
        b_start = b['observed_first_matching_word_start_seconds']
        assert a_end is not None and b_start is not None and a_end <= b_start
        cuts.append(round((a_end + b_start) / 2 * FPS))
    cuts.append(frame_end)
    for i, p in enumerate(pp):
        paragraphs[p['docx_paragraph']] = dict(p, timing=f, source_start_frame=cuts[i], source_end_frame=cuts[i+1])

ep = {'episode': 18, 'timeline_name': '大码_男版_EP18_新男版音色_原速旁白_自动剪辑_v1',
      'video': [], 'narration': [], 'subtitle_srt': str(BASE / '字幕/EP18.srt'),
      'limitations': ['Original audio checked by independent blind ASR and waveform/level analysis; no human full audition claimed.'],
      'editorial_notes': [], 'fps': 24}
events = []
cursor = 0


def canonical_events(p, record):
    f = p['timing']
    raw = f['expected_tokens_with_exact_match_anchors']
    first, last = p['generation_char_start'], p['generation_char_end_exclusive']
    phrase = p['source_text']
    result = []
    for m in re.finditer(r'\S+', phrase):
        aa, bb = first + m.start(), first + m.end()
        tokens = [w for w in raw if w['char_start'] < bb and aa < w['char_end_exclusive']]
        anchored = [w for w in tokens if w.get('source_start_seconds') is not None]
        if anchored:
            start = min(w['source_start_seconds'] for w in anchored)
            end = max(w['source_end_seconds'] for w in anchored)
        else:
            before = [w for w in raw if w['char_end_exclusive'] <= aa and w.get('source_end_seconds') is not None]
            after = [w for w in raw if w['char_start'] >= bb and w.get('source_start_seconds') is not None]
            start = before[-1]['source_end_seconds'] if before else p['source_start_frame'] / FPS
            end = after[0]['source_start_seconds'] if after else p['source_end_frame'] / FPS
        ss = max(p['source_start_frame'], round(start * FPS))
        ee = min(p['source_end_frame'], max(ss + 1, round(end * FPS)))
        assert ss < ee, (p['docx_paragraph'], m.group(), ss, ee)
        result.append({'word': m.group(), 'start_frame': record + ss - p['source_start_frame'],
                       'end_frame': record + ee - p['source_start_frame'],
                       'source_path': f['source_path'], 'docx_paragraph': p['docx_paragraph'],
                       'timing_note': 'canonical original token mapped to reviewed ASR anchors'})
    result[0]['boundary_before'] = True
    return result


def narration(paragraph):
    global cursor
    p = paragraphs[paragraph]
    path = p['timing']['source_path']
    item = {'path': path, 'source_start_frame': p['source_start_frame'], 'source_end_frame': p['source_end_frame'],
            'record_frame': cursor, 'gain_db': levels[path]['suggested_speech_gain_db'],
            'tag': 'P%d %s' % (paragraph, p['source_text']), 'source_docx_paragraphs': [paragraph], 'speed_percent': 100}
    ep['narration'].append(item)
    events.extend(canonical_events(p, cursor))
    cursor += p['source_end_frame'] - p['source_start_frame']


def message(paragraph, text, seconds):
    global cursor
    words = text.split()
    frames = round(seconds * FPS)
    start = cursor
    for i, word in enumerate(words):
        events.append({'word': word, 'start_frame': cursor + round(i * frames / len(words)),
                       'end_frame': cursor + max(round((i + 1) * frames / len(words)), round(i * frames / len(words)) + 1),
                       'docx_paragraph': paragraph, 'boundary_before': i == 0, 'type': 'silent_written_message'})
    cursor += frames
    ep['editorial_notes'].append({'type': 'original_written_message_no_voice', 'docx_paragraph': paragraph,
                                  'start_frame': start, 'end_frame': cursor, 'text': text})


def pictures(start, end, pool):
    """Trim distinct source shots, never stretch or loop. Centre trim quiet reactions."""
    need = end - start
    lengths = [out - inp for _, inp, out, _ in pool]
    assert all(x > 0 for x in lengths)
    assert sum(lengths) >= need, ('Insufficient unique picture coverage', start, end, need, sum(lengths))
    assigned = [max(1, math.floor(n * need / sum(lengths))) for n in lengths]
    for i in sorted(range(len(pool)), key=lambda i: lengths[i] - assigned[i], reverse=True):
        if sum(assigned) == need:
            break
        if assigned[i] < lengths[i]:
            assigned[i] += 1
    assert sum(assigned) == need
    pos = start
    for (filename, inp, out, tag), duration in zip(pool, assigned):
        path = sources[filename]['source_path']
        cut_in = inp + (out - inp - duration) // 2
        item = {'path': path, 'source_start_frame': cut_in, 'source_end_frame': cut_in + duration,
                'record_frame': pos, 'gain_db': levels[path]['suggested_ambience_under_vo_gain_db'],
                'tag': tag, 'speed_percent': 100, 'same_source_same_bounds_linked_sync_audio': True}
        if not filename.startswith('男版18-'):
            item['source_episode_override_reason'] = '同一Aldwick公寓无人外景，承接邻居消失与七天时间经过，不引入其他剧情或人物状态。'
        ep['video'].append(item)
        pos += duration
    assert pos == end


def block(label, entries, pool):
    start = cursor
    for entry in entries:
        if isinstance(entry, int):
            narration(entry)
        else:
            message(*entry)
    pictures(start, cursor, pool)
    ep['editorial_notes'].append({'type': 'story_block', 'label': label, 'start_frame': start, 'end_frame': cursor})


# Reserve a distinct empty-balcony tail outside EP17's selected source ranges.
# Updated only after the other episode planner confirms the unused range.
cross = read('准备/EP18开头同场补镜.json')
block('Neighbour disappears and flowers wither', [493, 494, 495], [
    (cross['filename'], cross['source_start_frame'], cross['source_end_frame'], '同公寓无人阳台时间过场'),
    ('男版18-1-1.mp4', 0, 217, '门口观察、鲜花到枯花，保留七天变化')])
block('Meeting and unfamiliar text', [496, (497, 'Mr. Carter, do you have a minute to talk?', 3.8), 498], [
    ('男版18-2-3.mp4', 0, 36, '会议建立'),
    ('男版18-2-1.mp4', 0, 50, '继续开会，另一侧机位'),
    ('男版18-2-1.mp4', 50, 80, '短信亮屏'),
    ('男版18-2-3.mp4', 69, 116, '收到信息的短暂分神'),
    ('男版18-2-1.mp4', 80, 165, '放下疑问、继续记录'),
    ('男版18-2-3.mp4', 116, 193, '手写笔记，搁置信息'),
    ('男版18-2-1.mp4', 165, 193, '手机已放下')])
block('Friend request, recognition and old memories', [499, 500, 501, 502, 503, 504, 505], [
    ('男版18-3-1.mp4', 0, 83, '厨房、拿手机查看新申请'),
    ('男版18-3-6.mp4', 65, 97, 'Madam Blackwood头像插入，只用一次'),
    ('男版18-3-1.mp4', 83, 313, '认出她、旧事浮现、沉思'),
    ('男版18-4-1.mp4', 0, 212, '同一厨房回忆、迟疑与放下手机'),
    ('男版18-4-2.mp4', 48, 97, '接受申请并礼貌询问')])
block('Swift reply and the unchanged matriarch', [506, 507, 508], [
    ('男版18-4-3.mp4', 73, 309, '等待、观察手机、神情变化'),
    ('男版18-4-1.mp4', 384, 457, '强硬口吻后的面部反应'),
    ('男版18-4-5.mp4', 0, 97, '坐下继续读信息')])
block('Hospital demand, a written message', [(509, 'Oliver, Vittoria is in the hospital. Get back to Veriston.', 4.2)], [
    ('男版18-4-1.mp4', 259, 384, '医院信息屏幕插入，原文只作文字')])
block('Medical student and specialist resources', [510, 511], [
    ('男版18-5-1.mp4', 0, 163, '疑惑面部、医学书与思考')])
block('Polite reply, remembered obligation and the second question', [
    512, (513, "Madam Blackwood, I'm only a medical student. There is very little I can do.", 5.2),
    514, 515, 516, (517, 'What is her condition? I could consult Professor Warren for advice.', 4.5), 518], [
    ('男版18-6-4.mp4', 0, 97, '坐窗边取手机、第一次输入回复'),
    ('男版18-6-3.mp4', 85, 190, '回复后近景读屏，恩情与心结'),
    ('男版18-6-3.mp4', 0, 41, '暂别屏幕，望向窗外'),
    ('男版18-6-1.mp4', 0, 54, '窗边思索另一机位'),
    ('男版18-6-1.mp4', 90, 212, '回看手机、压下旧情'),
    ('男版18-6-5.mp4', 0, 97, '拿起手机补充问题'),
    ('男版18-6-2.mp4', 212, 289, '等待进一步回复'),
    ('男版18-6-3.mp4', 190, 289, '三点闪动、手机亮起，延续等待')])
start = cursor
message(519, "The doctors can't do anything for her. We need you. Can you come?", 5.0)
cursor += 36
pictures(start, cursor, [('男版18-7-2.mp4', 0, 217, '读到请求、转向窗外，停在决定前')])
ep['duration_frames'] = cursor

# Every source narrator interval remains once, at original speed, with message gaps.
for f in timings:
    clips = sorted([c for c in ep['narration'] if c['path'] == f['source_path']], key=lambda c: c['source_start_frame'])
    assert clips[0]['source_start_frame'] == 0
    assert all(a['source_end_frame'] == b['source_start_frame'] for a, b in zip(clips, clips[1:]))
assert all(a['record_frame'] + a['source_end_frame'] - a['source_start_frame'] == b['record_frame'] for a, b in zip(ep['video'], ep['video'][1:]))
cues = cues_from_events(events, cursor)
write_srt(ep['subtitle_srt'], cues)
(BASE / '准备/EP18_原生剪辑计划.json').write_text(json.dumps(ep, ensure_ascii=False, indent=2))
(BASE / '字幕/EP18_原文词事件.json').write_text(json.dumps({'episode': 18, 'duration_frames': cursor, 'events': events}, ensure_ascii=False, indent=2))
print(json.dumps({'episode': 18, 'duration_seconds': cursor / FPS, 'video_clips': len(ep['video']),
                  'narration_clips': len(ep['narration']), 'subtitle_cues': len(cues), 'status': 'offline plan'}, ensure_ascii=False))
