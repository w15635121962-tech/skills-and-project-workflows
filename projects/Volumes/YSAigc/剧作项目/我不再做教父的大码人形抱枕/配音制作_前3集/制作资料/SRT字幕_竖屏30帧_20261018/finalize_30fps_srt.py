#!/usr/bin/env python3
"""Map the reviewed semantic caption plan to the actual 30fps clip snapshot."""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import math
import re

HERE = Path(__file__).resolve().parent
MEDIA = HERE.parent.parent
PLAN = HERE/'句子半句_竖屏字幕中间方案.json'
SNAP = HERE/'30fps竖屏实际时间线快照_修尾后.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def near_frame(value):
    return math.floor(value+.5)


def stamp(frame):
    ms = near_frame(frame*1000/30)
    h, rem = divmod(ms, 3600000)
    m, rem = divmod(rem, 60000)
    s, milli = divmod(rem, 1000)
    assert near_frame(ms*30/1000) == frame
    return f'{h:02}:{m:02}:{s:02},{milli:03}'


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot',type=Path,default=SNAP)
    ap.add_argument('--update-existing',action='store_true',
                    help='Update only the six generated 30fps SRT paths after an authorized snapshot change.')
    args=ap.parse_args()
    actual_snapshot=args.snapshot.resolve()
    plan, snapshot = read(PLAN), read(actual_snapshot)
    inputs = {str(PLAN):sha(PLAN), str(actual_snapshot):sha(actual_snapshot)}
    for path, expected in plan['input_hashes'].items():
        assert sha(Path(path)) == expected, path
        inputs[path] = expected
    assert snapshot['fps'] == 30
    assert snapshot['width'] == 1080 and snapshot['height'] == 1920
    by_reference = {t['reference_24fps_timeline_id']:t for t in snapshot['timelines']}
    assert len(by_reference) == 6
    results = []
    for t in plan['timelines']:
        actual = by_reference[t['timeline_id_reference']]
        assert float(actual['fps']) == 30
        assert int(actual['width']) == 1080 and int(actual['height']) == 1920
        assert actual['start_frame'] == 0
        items = [item for track in actual['audio_tracks'] for item in track['items']]
        by_audio = {Path(item['name']).stem:item for item in items}
        assert len(by_audio) == len(t['clips'])
        output_cues = []; output_clips = []
        for clip in t['clips']:
            item = by_audio[clip['audio_name']]
            assert item['left_offset'] == 0.0
            clip_start = math.ceil(item['start']-1e-7)
            clip_end = math.floor(item['end']+1e-7)
            assert abs(item['start']-clip_start)<1e-6 and abs(item['end']-clip_end)<1e-6
            local = [c for c in t['cues'] if c['audio_name']==clip['audio_name']]
            assert local
            assert all(Path(c['audio_path'])==Path(item['expected_original_mp3_path']) for c in local)
            mapped = []
            for cue in local:
                c = copy.deepcopy(cue)
                float_start = item['start']+c['source_caption_start_seconds']/1.1*30
                float_end = item['start']+c['source_caption_end_seconds']/1.1*30
                frame_start = max(clip_start,near_frame(float_start))
                frame_end = min(clip_end,near_frame(float_end))
                assert clip_start <= frame_start < frame_end <= clip_end
                assert not mapped or mapped[-1]['frame_end_30fps'] <= frame_start
                assert len(c['lines'])<=3 and max(map(len,c['lines']))<=28
                assert ' '.join(c['lines']) == c['text']
                c.update(actual_timeline_name=actual['name'],actual_timeline_id=actual['id'],
                    actual_audio_item_id=item['id'],actual_audio_item_start_frame=clip_start,
                    actual_audio_item_end_frame=clip_end,
                    actual_audio_item_wrapper_type=item.get('source_wrapper_type'),
                    frame_start_30fps=frame_start,frame_end_30fps=frame_end,
                    mapped_start_frame_float_30fps=float_start,
                    mapped_end_frame_float_30fps=float_end,
                    start_seconds_30fps=frame_start/30,end_seconds_30fps=frame_end/30,
                    duration_seconds_30fps=(frame_end-frame_start)/30,
                    characters_per_second_30fps=round(len(c['text'])/((frame_end-frame_start)/30),3),
                    srt_start=stamp(frame_start),srt_end=stamp(frame_end),
                    fps=30,requires_30fps_snapshot_rebase=False,
                    quantization_start_error_ms=(frame_start-float_start)/30*1000,
                    quantization_end_error_ms=(frame_end-float_end)/30*1000)
                for word in c['words']:
                    fs=item['start']+word['source_mp3_start_seconds']/1.1*30
                    fe=item['start']+word['source_mp3_end_seconds']/1.1*30
                    word.update(actual_timeline_id=actual['id'],
                        timeline_start_frame_float_30fps=fs,
                        timeline_end_frame_float_30fps=fe,
                        timeline_start_seconds_30fps=fs/30,
                        timeline_end_seconds_30fps=fe/30)
                    assert item['start']-1e-7<=fs<=fe<=item['end']+1e-7
                assert c['duration_seconds_30fps']>=.8
                mapped.append(c)
            assert ' '.join(c['text'] for c in mapped)==clip['canonical_text']
            output_cues.extend(mapped)
            output_clips.append(dict(clip,actual_audio_item=item,
                actual_timeline_start_seconds=clip_start/30,
                actual_timeline_end_seconds=clip_end/30))
        assert ' '.join(c['text'] for c in output_cues)==' '.join(c['text'] for c in t['cues'])
        assert [c['index'] for c in output_cues]==list(range(1,len(output_cues)+1))
        assert all(output_cues[i-1]['frame_end_30fps']<=output_cues[i]['frame_start_30fps'] for i in range(1,len(output_cues)))
        version='性转男版' if '性转' in actual['name'] else '女版'
        ep=int(re.search(r'EP(\d+)',actual['name']).group(1))
        prefix='大码性转男版' if version=='性转男版' else '大码女版'
        output=MEDIA/'字幕'/'竖屏30帧'/version/f'{prefix}{ep:02}_30fps.srt'
        output.parent.mkdir(parents=True,exist_ok=True)
        text='\n\n'.join(f"{c['index']}\n{c['srt_start']} --> {c['srt_end']}\n"+'\n'.join(c['lines']) for c in output_cues)+'\n'
        previous_srt_sha256=sha(output) if output.exists() else None
        content_changed=output.exists() and output.read_text(encoding='utf-8')!=text
        if output.exists() and not args.update_existing:
            assert not content_changed, 'Existing output differs; do not overwrite without review: '+str(output)
        if not output.exists() or content_changed:
            output.write_text(text,encoding='utf-8')
        results.append({'timeline_name':actual['name'],'timeline_id':actual['id'],
            'reference_24fps_timeline_name':t['timeline_name'],
            'reference_24fps_timeline_id':t['timeline_id_reference'],
            'fps':30,'width':1080,'height':1920,
            'episode':ep,'version':version,'srt_path':str(output),'srt_sha256':sha(output),
            'previous_srt_sha256':previous_srt_sha256,
            'SRT_timing_updated_from_previous_export':bool(content_changed),
            'cue_count':len(output_cues),'clip_count':len(output_clips),
            'no_cross_clip_cues':True,'no_overlap':True,'full_corrected_word_order_unchanged':True,
            'clips':output_clips,'cues':output_cues})
    for path, expected in inputs.items():assert sha(Path(path))==expected
    cues=[c for t in results for c in t['cues']]
    assert len(cues)==159
    edge_quantization=[]
    for c in cues:
        ws=min(w['timeline_start_frame_float_30fps'] for w in c['words'])
        we=max(w['timeline_end_frame_float_30fps'] for w in c['words'])
        start_delta=max(0,c['frame_start_30fps']-ws)
        end_delta=max(0,we-c['frame_end_30fps'])
        if max(start_delta,end_delta)>1e-7:
            assert max(start_delta,end_delta)<=.5+1e-7
            edge_quantization.append({'timeline_name':c['actual_timeline_name'],
                'cue_index':c['index'],'first_word_edge_rounding_ms':start_delta/30*1000,
                'last_word_edge_rounding_ms':end_delta/30*1000})
    text=' '.join(c['text'] for c in cues)
    for phrase in ['that Bellandis','the hallway corner','she kicked','tossed','Madame','desires']:
        assert phrase in text
    report={'status':'six_30fps_SRTs_prepared_pending_Resolve_import_and_UI_layout_validation',
        'actual_snapshot_path':str(actual_snapshot),
        'actual_snapshot_sha256':sha(actual_snapshot),
        'snapshot_tail_frame_extensions':snapshot.get('tail_frame_extensions',[]),
        'fps':30,'resolution':[1080,1920],
        'method':'Reviewed sentence/semantic-half-sentence wording mapped independently for each actual 30fps clip: actual clip start frames + original MP3 word/padding seconds / 1.1 * 30; nearest-frame quantization, constrained within clip.',
        'cue_end_frames_are_exclusive':True,
        'time_origin':'Each actual timeline starts at frame zero; SRT milliseconds round-trip to the recorded 30fps frame.',
        'source_media_or_Resolve_modified':False,'old_six_SRTs_overwritten':False,
        'ordinary_word_policy':'Preserve current corrected that/the/she kicked/tossed/Madame/desires; no new text edits.',
        'asr_word_timing_limit':'Word positions remain ASR estimates. At continuous-speech cue boundaries nearest-frame quantization can place an estimated word edge up to half a frame (16.67ms) across a caption boundary. This does not cut audio and is not manual phoneme verification or resolution of prior pronunciation disputes.',
        'subframe_word_edge_quantization_cases':edge_quantization,
        'inputs_sha256':inputs,
        'summary':{'timelines':6,'source_MP3s':sum(t['clip_count'] for t in results),
            'SRTs':len(results),'cues':len(cues),
            'cue_counts':[t['cue_count'] for t in results],
            'minimum_duration_seconds':min(c['duration_seconds_30fps'] for c in cues),
            'maximum_duration_seconds':max(c['duration_seconds_30fps'] for c in cues),
            'maximum_lines':max(len(c['lines']) for c in cues),
            'maximum_line_characters':max(max(map(len,c['lines'])) for c in cues),
            'clip_boundary_violations':0,'cue_overlaps':0,'missing_or_reordered_words':0},
        'timelines':results}
    target=HERE/'30fps竖屏字幕_落帧完成与校验.json'
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'report':str(target),'summary':report['summary'],
        'SRTs':[{'timeline_id':t['timeline_id'],'path':t['srt_path'],'cues':t['cue_count']} for t in results]},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
