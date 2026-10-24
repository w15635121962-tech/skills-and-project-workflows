"""Create native SRT from REVIEWED original word events on the FINAL24fps timeline.

No ASR is run here. Never pass an uncorrected machine transcript as original words.
The event file supplies canonical_original_words_verified=true and episodes with
integer duration_frames and events[{word,start_frame,end_frame,boundary_before}].
"""
import argparse,hashlib,json
from pathlib import Path
from native_common import BASE,EPISODES,read_json,write_json
from subtitle_tools import cues_from_events,write_srt,parse_srt

def main():
    p=argparse.ArgumentParser();p.add_argument('--events',required=True);p.add_argument('--episodes',nargs='+',type=int,default=sorted(EPISODES));args=p.parse_args()
    d=read_json(args.events)
    assert d.get('canonical_original_words_verified') is True, 'Original source words must be independently corrected/aligned upstream'
    assert d.get('fps')==24 and set(args.episodes)<=EPISODES
    by={x['episode']:x for x in d['episodes']};assert set(args.episodes)<=set(by)
    report=[]
    for number in args.episodes:
        ep=by[number];assert isinstance(ep['duration_frames'],int) and ep['duration_frames']>0
        for e in ep['events']:
            assert isinstance(e['start_frame'],int) and isinstance(e['end_frame'],int)
        cues=cues_from_events(ep['events'],ep['duration_frames'])
        path=BASE/'字幕'/('EP%02d.srt'%number)
        expected=[(c['start_frame'],c['end_frame'],c['text']) for c in cues]
        if path.exists():
            assert parse_srt(path)==expected,'Existing subtitle content/timing differs; preserve and resolve before replacing'
        else:write_srt(path,cues)
        assert parse_srt(path)==expected
        report.append({'episode':number,'srt':str(path),'cue_count':len(cues),'max_explicit_lines':max(len(c['text'].splitlines()) for c in cues),'max_line_characters':max(len(line) for c in cues for line in c['text'].splitlines()),'original_event_tokens_preserved':True,'srt_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'resolve_inserted':False,'preset_loaded':False})
    write_json(BASE/'字幕/原文词事件SRT_离线核验.json',report)
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
