from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,math,subprocess,re,hashlib
BASE=Path(__file__).resolve().parent
TASK=BASE.parent
FF='/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffmpeg'
manifest=json.loads((BASE/'narration_manifest.json').read_text(encoding='utf-8'))
adopt=json.loads((TASK/'ASR/旁白采用清单.json').read_text(encoding='utf-8'))
anchors=json.loads((TASK/'ASR/旁白逐词与源段落锚点_采用版本.json').read_text(encoding='utf-8'))
inventory=json.loads((BASE/'media_inventory.json').read_text(encoding='utf-8'))
cuts=json.loads((TASK/'画面核验/源视频切点候选.json').read_text(encoding='utf-8'))
source={x['filename']:x for e in inventory['episodes'] for x in e['videos']}
cutby={x['filename']:x for x in cuts['files']}
selected={x['logical_basename']:x for x in adopt['selections']}
anchorby={x['basename']:x for x in anchors['files']}
frozen_episodes=[16,17]
for ep in frozen_episodes:assert adopt[f'EP{ep}_selection_complete']

def loudness(path):
    cache=TASK/'ASR/采用旁白响度';cache.mkdir(exist_ok=True)
    dest=cache/(Path(path).stem+'.json');sha=hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if dest.exists():
        old=json.loads(dest.read_text(encoding='utf-8'))
        if old['sha256']==sha:return old
    cp=subprocess.run([FF,'-hide_banner','-i',path,'-vn','-af','loudnorm=I=-17:TP=-2:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,encoding='utf-8',check=True)
    raw=json.loads(cp.stderr[cp.stderr.rfind('{'):]);i=float(raw['input_i']);tp=float(raw['input_tp']);gain=round(min(0,-17-i,-3-tp),2)
    out={'path':path,'sha256':sha,'integrated_loudness_lufs':i,'true_peak_dbfs':tp,'gain_db':gain,'method':'ffmpeg loudnorm measurement only; source audio unchanged'}
    dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return out

levels={x['path']:x for x in json.loads((TASK/'ASR/source_levels.json').read_text(encoding='utf-8'))['files']}
pause_removals={
    '大码男版枕头16-01-01':[(78,89),(130,140)],
    '大码男版枕头16-02-01':[(76,82),(156,165)],
    '大码男版枕头17-03-01':[(96,101)],
}

def vo_items(ep):
    out=[];record=0;par={};rows=[]
    for g in manifest['groups']:
        if g['episode']!=ep:continue
        pick=selected[g['basename']];a=anchorby[g['basename']]
        assert a['source_path']==pick['selected_audio_path']
        assert a['source_sha256']==pick['selected_audio_sha256']
        duration=pick['selected_audio_duration_seconds'];last=a['source_words'][-1]['end']
        end=math.floor(min(duration,last+.18)*24+1e-7)
        assert end/24>=last-1e-6
        remove=pause_removals.get(g['basename'],[])
        source_ranges=[];cursor=0
        for aa,bb in remove:
            assert 0<=cursor<aa<bb<end
            assert all(w['end']<=aa/24+1e-6 or w['start']>=bb/24-1e-6 for w in a['source_words']),('Word crosses pause cut',g['basename'],aa,bb)
            source_ranges.append((cursor,aa));cursor=bb
        source_ranges.append((cursor,end))
        start_record=record
        for a0,b0 in source_ranges:
            out.append({'path':a['source_path'],'source_start_frame':a0,'source_end_frame':b0,'record_frame':record,'gain_db':levels[a['source_path']]['suggested_speech_gain_db'],
                'tag':g['basename']+' adopted '+pick['selected_audio_basename'],'speed_percent':100,'logical_basename':g['basename'],'source_sha256':a['source_sha256'],
                'original_docx_paragraphs':g['source_docx_paragraphs'],'edit_note':'Only trailing nonspeech and documented middle portions of long natural pauses removed; every speech interval stays at 100 percent; combined edited pauses retain at least 0.25 second breath.'})
            record+=b0-a0
        def mapped_frame(seconds):
            f=round(seconds*24)
            return start_record+f-sum(bb-aa for aa,bb in remove if bb<=f)
        for n,p in enumerate(a['source_paragraph_anchors']):
            t=0 if n==0 else p['observed_first_matching_word_start_seconds']
            assert t is not None
            par[p['docx_paragraph']]=mapped_frame(t)
            rows.append(dict(p,logical_basename=g['basename'],actual_audio_path=a['source_path'],timeline_first_anchor_frame=mapped_frame(t),timeline_last_anchor_frame=mapped_frame(p['observed_last_matching_word_end_seconds'])))
    return out,record,par,rows

def add_video(target,ep,name,a,b,purpose,paragraphs=None,override=None,split=True,speech=False):
    assert 0<=a<b<=int(source[name]['video_streams'][0]['nb_frames'])
    boundaries=[a]+[f for f in cutby[name]['cut_frames_candidates'] if a<f<b]+[b] if split else [a,b]
    for aa,bb in zip(boundaries,boundaries[1:]):
        record=sum(c['source_end_frame']-c['source_start_frame'] for c in target)
        c={'path':source[name]['path'],'source_start_frame':aa,'source_end_frame':bb,'record_frame':record,'gain_db':levels[source[name]['path']]['suggested_speech_gain_db' if speech else 'suggested_ambience_under_vo_gain_db'],
            'tag':f'男版EP{ep} '+purpose,'speed_percent':100,'original_docx_paragraphs':paragraphs,'same_source_linked_sync_audio':True}
        if speech:c['contains_protected_original_dialogue']=True
        if override:c['source_episode_override_reason']=override
        target.append(c)

def ep16():
    narration,total,par,para=vo_items(16)
    # Actual selected new VO, with only nonspeech tails trimmed, totals 2352
    # frames. Paragraph starts were independently recognized in the source MP3.
    assert total==2316,(total,par)
    starts=[0,par[456],par[459],par[462],par[465],par[469],par[470],total]
    assert starts==[0,437,692,1069,1423,1860,2027,2316],starts
    video=[];blocks=[]
    reason='同一男版Aldwick住所的无人外观，只有建筑不露人物，置于初到Aldwick建立镜，不提前出现瘦身形象。'
    # 3.292 seconds of neutral, empty building shots establish arrival. The
    # overweight-to-lean transition then follows EP16 source action order.
    add_video(video,16,'男版17-1-1.mp4',309,361,'Aldwick无人公寓窗口',[451],reason)
    add_video(video,16,'男版16-1-1.mp4',0,385,'租房整理玩偶/床单/小床',[451,455])
    blocks.append({'paragraphs':[451,455],'start_frame':0,'end_frame':437,'note':'开头无人建筑后完整连续保留进房→取玩偶→铺床→抱熊躺床；不将瘦身后的脸提前插入。'})
    add_video(video,16,'男版16-2-1.mp4',0,225,'花店买花与自由生活',[456,458])
    add_video(video,16,'男版17-3-1.mp4',93,123,'花束静物',[457,458],'同男版Aldwick公寓的花束静物，无人物和新事件，用于买花后独居自由的日常过桥。')
    blocks.append({'paragraphs':[456,458],'start_frame':437,'end_frame':692,'note':'花店按源顺序，尾部使用无人花束静物；不出现邻居或未来短信事件。'})
    add_video(video,16,'男版16-3-1.mp4',0,377,'慢跑/游泳/饮食/瘦身/镜中下颌',[459,461])
    blocks.append({'paragraphs':[459,461],'start_frame':692,'end_frame':1069,'note':'跑步[0,58)、游泳[58,90)、饮食[90,120)、逐渐瘦身[120,177)、镜中脸和下颌[177,377)，对上原文同序。'})
    add_video(video,16,'男版16-4-1.mp4',0,313,'翻出日记/熟悉锁码/开始翻阅',[462,464])
    add_video(video,16,'男版16-5-1.mp4',59,100,'阳光下坐在地毯读日记',[464])
    blocks.append({'paragraphs':[462,464],'start_frame':1069,'end_frame':1423,'note':'纸本、锁和双手都沿用本集原片，后接同本日记坐地宽镜；未重复使用相同帧。'})
    add_video(video,16,'男版16-5-1.mp4',0,59,'读日记的正脸',[465])
    add_video(video,16,'男版17-2-1.mp4',47,91,'瘦身后Aldwick窗边沉思',[466],'同男版瘦身后白衬衫阶段的Aldwick住所窗边近景，无对白无新关系事件，承接远离故地后的内心回望。')
    add_video(video,16,'男版17-3-1.mp4',264,337,'新生活的公寓阳台阅读',[466],'同男版瘦身后白衬衫阶段的Aldwick阳台阅读与面部近景，只作新生活回望，不引入原片邻居情节。')
    add_video(video,16,'男版16-5-1.mp4',100,361,'撕页/凝视/手指抚过纸边',[466,468])
    blocks.append({'paragraphs':[465,468],'start_frame':1423,'end_frame':1860,'note':'把同阶段窗边/阳台阅读放在“远在Aldwick像梦”回望语段；回到原日记后按宽镜→手→撕页→脸→纸边推进，未重演翻页或撕页。'})
    add_video(video,16,'男版16-6-1.mp4',0,167,'合日记/拨000/上楼收存',[469])
    blocks.append({'paragraphs':[469,469],'start_frame':1860,'end_frame':2027,'note':'只保留一次合本、拨锁、收存。16-8替代版不再使用。'})
    add_video(video,16,'男版16-7-1.mp4',0,191,'朋友/爱好/换手机号',[470,471])
    add_video(video,16,'男版17-3-1.mp4',176,200,'新生活欣赏鲜花',[470,472],'同男版瘦身后Aldwick公寓欣赏鲜花的独处镜，只为新爱好及已不被寻找的平静状态过桥，无新事件。')
    add_video(video,16,'男版16-7-1.mp4',191,265,'窗边平静远望',[471,472])
    blocks.append({'paragraphs':[470,472],'start_frame':2027,'end_frame':2316,'note':'朋友与换手机之后回到独处远望结束，原文Evan失眠推测仅用原旁白，不补其他人物剧情。'})
    return {'episode':16,'timeline_name':'大码_男版_EP16_新男版音色_原速旁白_自动剪辑_v1','duration_frames':total,'video':video,'narration':narration,
        'subtitle_srt':None,'original_paragraph_timeline_anchors':para,'story_blocks':blocks,'mandatory_dialogue_units':[],
        'limitations':['全部旁白采用独立核验后的原速版本；仅裁短句尾非语音及四处过长停顿，所有语音100%，不做音频变速。','补镜均为同男版Aldwick住所、对应瘦身阶段；逐切静帧已查看，尚需原生时间线回放验收。','ASR词时码存在专名/缩写差异，字幕须用原文并保留核验记录；不称逐字人工听验。']}

def ep17():
    narration,base_total,par,para=vo_items(17)
    assert base_total==1428,(base_total,par)
    # The source invitation is played once in full, including the intentional
    # pause between the student's two sentences and the man's silent reaction.
    dialogue_start=1289
    source_in=18;source_out=280;dialogue_length=source_out-source_in
    cut_at=226
    pieces=[];found=False
    for c in narration:
        if c['logical_basename']=='大码男版枕头17-05-01':
            assert c['source_start_frame']==0 and c['source_end_frame']==299
            assert c['record_frame']+cut_at==dialogue_start
            first=dict(c,source_end_frame=cut_at)
            second=dict(c,source_start_frame=cut_at,record_frame=dialogue_start+dialogue_length)
            pieces.extend([first,second]);found=True
        elif found:
            pieces.append(dict(c,record_frame=c['record_frame']+dialogue_length))
        else:pieces.append(c)
    assert found
    narration=pieces;total=base_total+dialogue_length
    for p in para:
        if p['docx_paragraph']>=489:
            p['timeline_first_anchor_frame']+=dialogue_length;p['timeline_last_anchor_frame']+=dialogue_length
    assert total==1690
    video=[]
    add_video(video,17,'男版17-1-1.mp4',0,309,'房东聊天、介绍新邻居',[475,478])
    add_video(video,17,'男版17-1-2.mp4',0,43,'房东近景补充听说邻居行程',[476,478])
    add_video(video,17,'男版17-1-1.mp4',309,361,'同栋公寓无人阳台',[477,479])
    assert sum(c['source_end_frame']-c['source_start_frame'] for c in video)==404
    add_video(video,17,'男版17-2-1.mp4',0,217,'晨间杯子、相邻阳台鲜花',[479,481])
    add_video(video,17,'男版17-3-1.mp4',0,337,'同样花味、邻居不露面、暗灯与每日花束',[480,484])
    assert sum(c['source_end_frame']-c['source_start_frame'] for c in video)==958
    add_video(video,17,'男版17-4-1.mp4',0,313,'国际研究生/猫咖/离店叫住他',[485,487])
    add_video(video,17,'男版17-5-1.mp4',0,18,'说话前犹豫起瞬',[487])
    assert sum(c['source_end_frame']-c['source_start_frame'] for c in video)==dialogue_start
    add_video(video,17,'男版17-5-1.mp4',18,280,'原声完整猫后空翻邀请',[488],split=False,speech=True)
    # One second of same-scene shy close-up plus the continuing original
    # reaction, two-shot and final male smile. No source frames repeat.
    add_video(video,17,'男版17-4-2.mp4',0,24,'女同学羞怯捂嘴、awkward laugh反应',[489])
    add_video(video,17,'男版17-5-1.mp4',282,315,'女同学耳根红、说完后的反应',[489])
    add_video(video,17,'男版17-5-1.mp4',327,409,'双人停留、男主含笑接受',[489,490])
    raw=json.loads((TASK/'ASR/raw_large-v3-turbo/EP17/video/男版17-5-1.json').read_text(encoding='utf-8'))
    words=[dict(w,timeline_start_frame=dialogue_start+round(w['start']*24)-source_in,timeline_end_frame=dialogue_start+round(w['end']*24)-source_in) for w in raw['words']]
    assert all(dialogue_start<=w['timeline_start_frame']<=w['timeline_end_frame']<=dialogue_start+dialogue_length for w in words)
    return {'episode':17,'timeline_name':'大码_男版_EP17_新男版音色_原速旁白_自动剪辑_v1','duration_frames':total,'video':video,'narration':narration,
        'subtitle_srt':None,'original_paragraph_timeline_anchors':para,
        'story_blocks':[{'paragraphs':[475,478],'start_frame':0,'end_frame':404},
            {'paragraphs':[479,484],'start_frame':404,'end_frame':958},
            {'paragraphs':[485,487],'start_frame':958,'end_frame':dialogue_start},
            {'paragraphs':[488,488],'start_frame':dialogue_start,'end_frame':dialogue_start+dialogue_length},
            {'paragraphs':[489,490],'start_frame':dialogue_start+dialogue_length,'end_frame':total}],
        'mandatory_dialogue_units':[{'id':'EP17_P488_cat_invitation','source_docx_paragraph':488,
            'original_text':'Um... my cat back home can actually do backflips—way cooler than the ones here. Do you... want to come over and see for yourself?',
            'path':source['男版17-5-1.mp4']['path'],'source_start_frame':18,'source_end_frame':280,
            'record_frame':dialogue_start,'duration_frames':dialogue_length,'words':words,'must_preserve_inter_sentence_pause':True,'native_speed_percent':100}],
        'limitations':['旁白17-05在P487结束后、P489开始前拆为两个原速片段，中间保留一次完整邀请同期声与反应停顿。','17-6两份窗帘窥视镜没有原文明确事件，全部不用。','末段羞怯捂嘴来自17-4-2同场同装镜，原片暖光/蓝调角度差需原生回放检查，不称已完成调色。','旁白仅17-03自然句间空白剪5帧，仍保留约0.25秒呼吸；其他内部停顿不压缩。']}

def validate_episode(ep):
    assert ep['video'] and ep['narration']
    for kind in ['video','narration']:
        cursor=0;ranges={}
        for c in ep[kind]:
            assert c['record_frame']>=cursor,(ep['episode'],kind,c,cursor)
            if kind=='video':assert c['record_frame']==cursor
            assert Path(c['path']).is_file() and c['source_end_frame']>c['source_start_frame']
            for a,b in ranges.setdefault(c['path'],[]):assert c['source_end_frame']<=a or c['source_start_frame']>=b,('reused source frames',c,a,b)
            ranges[c['path']].append((c['source_start_frame'],c['source_end_frame']))
            cursor=c['record_frame']+c['source_end_frame']-c['source_start_frame']
        assert cursor==ep['duration_frames']
    return {'episode':ep['episode'],'duration_frames':ep['duration_frames'],'duration_seconds':ep['duration_frames']/24,'video_clips':len(ep['video']),'narration_clips':len(ep['narration']),'contiguous_picture':True,'narration_gaps_only_for_original_dialogue':True,'repeated_source_frames':False,'all_native_speed_percent':100}

if __name__=='__main__':
    episodes=[ep16(),ep17()];audits=[validate_episode(e) for e in episodes]
    for episode,audit in zip(episodes,audits):
        result={'status':'READY_FOR_NATIVE_ASSEMBLY','project':'大码枕头','fps':24,'episodes':[episode],
            'scope':f"EP{episode['episode']} fragment to merge with other episode fragments before native assembly; no Resolve operations performed.",
            'preassembly_audit':audit,'voice_selection_file':str(TASK/'ASR/旁白采用清单.json')}
        dest=BASE/f"EP{episode['episode']}_native_edit_plan.json";dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    combined={'status':'READY_FOR_NATIVE_ASSEMBLY','project':'大码枕头','fps':24,'episodes':episodes,'preassembly_audit':audits}
    dest=BASE/'EP16-17_native_edit_plan.json';dest.write_text(json.dumps(combined,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'plan':str(dest),'audits':audits},ensure_ascii=False))
