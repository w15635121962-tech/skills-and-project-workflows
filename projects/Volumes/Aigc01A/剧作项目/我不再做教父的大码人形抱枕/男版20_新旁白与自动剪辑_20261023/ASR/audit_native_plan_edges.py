"""Read-only male EP20 plan edge audit; 13 video observations and 9 narration segments required.

Does not connect Resolve, rewrite a plan, change source media, or claim audition.
Accepts one or more existing plan paths; repeat after a plan revision.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import re
import subprocess
import difflib

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
TASK = HERE.parent
FPS = 24

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def norm(text):
    text = text.lower().replace('\u2019', "'")
    text = re.sub(r'[^a-z0-9 ]', '', text)
    aliases = {'mateo':'matteo', 'matelo':'matteo', 'mattelo':'matteo', 'mattelio':'matteo',
               'mateel':'matteo', 'metello':'matteo', 'mathiel':'matteo',
               'alicia':'alessia', 'alesia':'alessia', 'belandi':'bellandi',
               'belandis':'bellandis'}
    return [aliases.get(t, t) for t in text.split()]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--plan', action='append', required=True)
    ap.add_argument('--output', default=str(HERE / 'plan_edge_review'))
    args = ap.parse_args()
    output = Path(args.output)
    video_index = json.loads((HERE / 'index.json').read_text(encoding='utf-8'))
    narration_index = json.loads((HERE / 'narration_index.json').read_text(encoding='utf-8'))
    assert video_index['completed']==13 and not video_index['errors']
    assert {x['sequence'] for x in narration_index['files']} >= set(range(1,10)) and not narration_index['errors']
    index = {'files': video_index['files'] + narration_index['files']}
    sources = {r['source_path']:json.loads(Path(r['json_path']).read_text(encoding='utf-8')) for r in index['files']}
    inventory = json.loads((TASK / '\u51c6\u5907/\u7d20\u6750\u76d8\u70b9.json').read_text(encoding='utf-8'))
    ffmpeg = str(Path(inventory['ffprobe_path']).with_name('ffmpeg'))
    secondary = json.loads((HERE / '\u4e8c\u6b21\u76f2\u8bc6\u522b\u7591\u70b9\u590d\u6838.json').read_text(encoding='utf-8'))
    diagnostics = {r['source_path']:r for r in secondary['files']}
    pcm = {}
    def samples(path):
        if path not in pcm:
            data = subprocess.check_output([ffmpeg, '-v', 'error', '-i', path, '-vn', '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'])
            pcm[path] = np.frombuffer(data, dtype='<f4')
        return pcm[path]
    report = dict(plans=[dict(path=str(Path(p).resolve()),sha256=sha(p)) for p in args.plan],
                  source_files_modified=False, resolve_connected=False,
                  human_listening_verified=False, fps=FPS, episodes=[])
    episodes = []
    for p in args.plan:
        plan = json.loads(Path(p).read_text(encoding='utf-8'))
        assert plan['fps'] == FPS
        episodes.extend(plan['episodes'])
    assert len({e['episode'] for e in episodes}) == len(episodes)
    font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 14)
    for ep in sorted(episodes, key=lambda e:e['episode']):
        number = ep['episode']
        result = dict(episode=number, duration_frames=ep['duration_frames'],
                      narration_cross_word_cuts=[], dialogue_cross_word_cuts=[],
                      narration_word_coverage_errors=[], role_vo_overlaps=[],
                      duplicate_source_intervals=[], background_diagnostics=[], audio_events=[], edge_measurements=[])
        for kind in ['video', 'narration']:
            rows = ep[kind]
            for i, a in enumerate(rows):
                for b in rows[i+1:]:
                    if a['path'] == b['path'] and max(a['source_start_frame'], b['source_start_frame']) < min(a['source_end_frame'], b['source_end_frame']):
                        result['duplicate_source_intervals'].append(dict(kind=kind, first=a, second=b))
        for path in {x['path'] for x in ep['narration']}:
            clips = [x for x in ep['narration'] if x['path'] == path]
            for wi, word in enumerate(sources[path]['words']):
                if word['end'] <= word['start']:
                    continue
                matches = [c for c in clips if c['source_start_frame']/FPS <= word['start']+1e-6 and word['end'] <= c['source_end_frame']/FPS+1e-6]
                if len(matches) != 1:
                    result['narration_word_coverage_errors'].append(dict(path=path, word_index=wi, observed_word=word, covering_clips=len(matches)))
        events = []
        plotted_edges = set()
        for ev in ep.get('audio_events', []):
            path = ev['source_path']; start = ev['source_start_frame']/FPS; end = ev['source_end_frame']/FPS
            raw = sources[path]
            observed = [w for w in raw['words'] if w['end'] > w['start'] and max(start,w['start']) < min(end,w['end'])]
            actual_clips = [c for c in ep['narration' if ev['kind']=='narration' else 'video']
                            if c['path']==path and c['record_frame']==ev['record_frame']]
            if not actual_clips and 'clip_source_start_frame' not in ev:
                event_offset = ev['record_frame']-ev['source_start_frame']
                actual_clips = [c for c in ep['narration' if ev['kind']=='narration' else 'video']
                    if c['path']==path and c['record_frame']-c['source_start_frame']==event_offset
                    and c['source_start_frame']<=ev['source_start_frame']
                    and ev['source_end_frame']<=c['source_end_frame']]
            assert len(actual_clips)==1, ('Audio event must identify its actual source clip',ev,actual_clips)
            actual_clip = actual_clips[0]
            clip_start = actual_clip['source_start_frame']/FPS
            clip_end = actual_clip['source_end_frame']/FPS
            cross = [w for w in raw['words'] if w['start']+1e-6 < clip_start < w['end']-1e-6 or w['start']+1e-6 < clip_end < w['end']-1e-6]
            if cross:
                result['narration_cross_word_cuts' if ev['kind']=='narration' else 'dialogue_cross_word_cuts'].append(dict(event=ev, words=cross))
            offset = (actual_clip['record_frame']-actual_clip['source_start_frame'])/FPS
            active_start = observed[0]['start']+offset if observed else None
            active_end = observed[-1]['end']+offset if observed else None
            event = dict(ev)
            event.update(observed_text=' '.join(w['word'].strip() for w in observed), observed_words=observed,
                         active_record_start_seconds=active_start, active_record_end_seconds=active_end,
                         normalized_lexical_ratio=difflib.SequenceMatcher(None,norm(ev['canonical_text']),norm(' '.join(w['word'] for w in observed)),autojunk=False).ratio())
            events.append(event)
            # Word-event boundaries are for caption alignment. Plot the ACTUAL
            # enclosing media cut; a four-sentence clip has only two real edges.
            for edge, sec in [('start', clip_start), ('end', clip_end)]:
                key=(path,ev['kind'],edge,sec)
                if key in plotted_edges:
                    continue
                plotted_edges.add(key)
                values = samples(path)
                at = round(sec*16000)
                around = values[max(0,at-320):min(len(values),at+320)]
                peak = float(np.max(np.abs(around))) if len(around) else 0
                prior = [w for w in raw['words'] if w['end'] <= sec+1e-6]
                following = [w for w in raw['words'] if w['start'] >= sec-1e-6]
                crossing = [w for w in raw['words'] if w['start']+1e-6 < sec < w['end']-1e-6]
                result['edge_measurements'].append(dict(source_path=path, kind=ev['kind'], edge=edge,
                    cut_seconds=sec, cut_frame=round(sec*FPS), edge_basis='actual_media_clip_not_caption_word_event',
                    prior_word=prior[-1] if prior else None, next_word=following[0] if following else None,
                    crossing_words=crossing, pcm_40ms_peak_dbfs=20*math.log10(max(peak,1e-9))))
        for role in [x for x in events if x['kind']!='narration' and x['active_record_start_seconds'] is not None]:
            for narration in ep['narration']:
                start = narration['record_frame']/FPS
                end = (narration['record_frame']+narration['source_end_frame']-narration['source_start_frame'])/FPS
                if max(role['active_record_start_seconds'], start) < min(role['active_record_end_seconds'],end):
                    result['role_vo_overlaps'].append(dict(dialogue=role, narration=narration))
        result['audio_events'] = events
        for v in ep['video']:
            if v.get('gain_db',0) >= -1:
                continue
            start = v['source_start_frame']/FPS; end = v['source_end_frame']/FPS
            obs = [w for w in sources[v['path']]['words'] if max(start,w['start'])<min(end,w['end'])]
            if obs:
                result['background_diagnostics'].append(dict(clip=v, observed_words=obs,
                    secondary_diagnostic=diagnostics.get(v['path']),
                    note='Unreviewed recognition is not proof of real speech; original linked sound retained.'))
        # Small independent waveform pages, six source edges per page.
        edges = result['edge_measurements']; pages=[]
        for first in range(0,len(edges),6):
            batch = edges[first:first+6]
            im = Image.new('RGB',(1250,220*len(batch)),(25,25,25)); draw=ImageDraw.Draw(im)
            for row, edge in enumerate(batch):
                values=samples(edge['source_path']); sec=edge['cut_seconds'];lo=max(0,sec-.55);hi=min(len(values)/16000,sec+.55)
                segment=values[round(lo*16000):round(hi*16000)]
                top=row*220;mid=top+135
                label='EP%02d %s %s %s %.3fs (%df)'%(number,Path(edge['source_path']).name,edge['kind'],edge['edge'],sec,edge['cut_frame'])
                draw.text((10,top+5),label,fill='white',font=font)
                prior=edge['prior_word'];nxt=edge['next_word']
                text='Prior: %s | Next: %s | crossing=%d | peak40ms %.1fdBFS'%(
                    (prior['word'].strip()+' end %.3f'%prior['end'])if prior else 'none',
                    (nxt['word'].strip()+' start %.3f'%nxt['start'])if nxt else 'none',
                    len(edge['crossing_words']),edge['pcm_40ms_peak_dbfs'])
                draw.text((10,top+26),text,fill=(210,210,210),font=font)
                for x in range(1220):
                    sample=segment[int(x*len(segment)/1220):int((x+1)*len(segment)/1220)]
                    peak=float(np.max(np.abs(sample)))if len(sample)else 0
                    height=min(70,round(peak*125));draw.line((10+x,mid-height,10+x,mid+height),fill=(80,200,225))
                cutx=10+round((sec-lo)/max(1e-9,hi-lo)*1220);draw.line((cutx,top+52,cutx,top+214),fill=(255,90,75),width=2)
            target=output/('EP%02d_edges_%02d.jpg'%(number,first//6+1));target.parent.mkdir(parents=True,exist_ok=True);im.save(target,quality=90);pages.append(str(target))
        result['waveform_pages']=pages
        result['summary']={k:len(result[k])for k in ['narration_cross_word_cuts','dialogue_cross_word_cuts','narration_word_coverage_errors','role_vo_overlaps','duplicate_source_intervals','background_diagnostics']}
        write(output/('EP%02d_edge_audit.json'%number),result)
        report['episodes'].append(dict(episode=number,summary=result['summary'],path=str(output/('EP%02d_edge_audit.json'%number)),waveform_pages=pages))
        print(json.dumps(report['episodes'][-1],ensure_ascii=False),flush=True)
    write(output/'report.json',report)

if __name__=='__main__':
    main()
