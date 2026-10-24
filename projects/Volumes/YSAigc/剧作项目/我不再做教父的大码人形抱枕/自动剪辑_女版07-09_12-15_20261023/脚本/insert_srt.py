import argparse,re,json
from native_common import *
def parse_srt(path):
    def frames(s):
        h,m,se,ms=map(int,re.split(r'[:,]',s));return round((h*3600+m*60+se+ms/1000)*24)
    cues=[]
    for block in Path(path).read_text(encoding='utf-8-sig').strip().split('\n\n'):
        rows=block.splitlines();a,b=rows[1].split(' --> ');text='\n'.join(rows[2:]);assert 1<=len(rows[2:])<=3
        cues.append([frames(a),frames(b),text])
    return cues
def native_cues(t):
    return [[int(x.GetStart()),int(x.GetEnd()),x.GetName().replace('\u2028','\n').replace('\r\n','\n').strip()] for x in t.GetItemListInTrack('subtitle',1) or []]
def main():
    a=argparse.ArgumentParser();a.add_argument('--plan',required=True);a.add_argument('--execute',action='store_true');a.add_argument('--replace-owned-subtitles',action='store_true');args=a.parse_args();plan=load_plan(args.plan)
    for e in plan['episodes']:
        cues=parse_srt(e['subtitle_srt']);assert cues and cues[-1][1]<=e['duration_frames']
    if not args.execute:print('SRT offline validation passed');return
    r,m,p,pool=connect();own={x['episode']:x for x in read(BASE/'Resolve_组装实读.json')['episodes']};live={t.GetUniqueId():t for t in timelines(p)}
    root=child(pool,pool.GetRootFolder(),BASE.name);sub=child(pool,root,'按集SRT字幕_先入轨后预设')
    reportpath=BASE/'字幕/SRT_原生入轨回读.json';report=read(reportpath) if reportpath.exists() else []
    for e in plan['episodes']:
        row=own[e['episode']];t=live[row['id']];assert t.GetName()==e['timeline_name'];assert p.SetCurrentTimeline(t)
        assert t.GetEndFrame()==e['duration_frames'] and t.GetStartFrame()==0
        for kind,track,clips in [('video',1,e['video']),('audio',1,e['video']),('audio',2,e['narration'])]:
            items=t.GetItemListInTrack(kind,track);assert len(items)==len(clips)
            for item,c in zip(items,clips):assert_clip(item,c)
        before=av(t);expected=parse_srt(e['subtitle_srt'])
        if t.GetTrackCount('subtitle')==0:assert t.AddTrack('subtitle')
        assert t.GetTrackCount('subtitle')==1
        existing=native_cues(t)
        if existing and existing!=expected and args.replace_owned_subtitles:
            oldrow=next(x for x in report if x['episode']==e['episode'])
            assert oldrow['id']==t.GetUniqueId() and existing==parse_srt(oldrow['srt']), 'Only task-owned, unchanged captions may be revised'
            assert [re.sub(r'\s+','',x[2]) for x in existing] != []
            assert re.sub(r'\s+','',''.join(x[2] for x in existing))==re.sub(r'\s+','',''.join(x[2] for x in expected)), 'Semantic reflow must preserve every text character'
            write(BASE/'修订前可恢复备份'/('EP%02d_语义分句前字幕.json'%e['episode']),{'cues':existing,'previous_source':oldrow['srt']})
            assert t.DeleteClips(t.GetItemListInTrack('subtitle',1),False)
            assert not native_cues(t);existing=[]
        if existing:assert existing==expected
        else:
            folder=child(pool,sub,'EP%02d'%e['episode']);assert pool.SetCurrentFolder(folder)
            made=pool.ImportMedia([e['subtitle_srt']]);assert made and len(made)==1
            assert t.SetCurrentTimecode('00:00:00:00');made=pool.AppendToTimeline([made[0]])
            assert made and native_cues(t)==expected, 'Exact native cue text/times required'
        assert t.SetTrackName('subtitle',1,str(e['episode']));assert t.SetTrackEnable('subtitle',1,True)
        assert av(t)==before;assert m.SaveProject()
        entry={'episode':e['episode'],'timeline':t.GetName(),'id':t.GetUniqueId(),'srt':e['subtitle_srt'],'srt_sha256':sha(e['subtitle_srt']),
               'cue_count':len(expected),'track_name':str(e['episode']),'exact_native_cues':True,'av_unchanged':True,
               'preset_status':'PENDING_NATIVE_UI_LOAD_AFTER_IMPORT','preset_required':'九州海外短剧 Preset 字幕 Preset'}
        report=[x for x in report if x['episode']!=e['episode']]+[entry];report.sort(key=lambda x:x['episode']);write(reportpath,report)
        print(json.dumps({'episode':e['episode'],'native_subtitle_count':len(expected),'numeric_track_name':str(e['episode']),'av_unchanged':True},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
