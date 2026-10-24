from pathlib import Path
import json,math
BASE=Path(__file__).resolve().parent
TASK=BASE.parent
coverage=json.loads((BASE/'同期对白_画面覆盖与源范围草案.json').read_text(encoding='utf-8'))
manifest=json.loads((BASE/'narration_manifest.json').read_text(encoding='utf-8'))
insertions=json.loads((BASE/'旁白段内同期对白插入点.json').read_text(encoding='utf-8'))
sync=json.loads((TASK/'ASR/同期对白与音轨候选.json').read_text(encoding='utf-8'))
cuts=json.loads((TASK/'画面核验/源视频切点候选.json').read_text(encoding='utf-8'))
cutby={x['filename']:x for x in cuts['files']}
sourceby={x['filename']:x for x in sync['files']}
base_scripts=TASK.parent/'男版21-25_自动剪辑_20261021'

# This source plan intentionally has no final timeline positions or fabricated
# narration durations. It becomes executable only after new VO ASR alignment.
spec={
 'E17_cat_invitation':('男版17-5-1.mp4',0,24,488),
 'E19_question':('男版19-1-1.mp4',0,3,524),
 'E19_nurse_report':('男版19-2-2.mp4',0,15,526),
 'E19_nurse_question':('男版19-2-1.mp4',16,26,527),
 'E19_nurse_answer':('男版19-2-1.mp4',27,30,528),
 'E19_mother_devalues':('男版19-3-2.mp4',0,29,532),
 'E19_mother_impatient':('男版19-4-2.mp4',0,14,535),
}
dialogues={}
for key,(name,a,b,paragraph) in spec.items():
    raw=TASK/'ASR/raw_large-v3-turbo'/f'EP{name[2:4]}'/'video'/(name[:-4]+'.json')
    d=json.loads(raw.read_text(encoding='utf-8'));ws=d['words'][a:b+1]
    inf=max(0,math.floor((ws[0]['start']-.15)*24));outf=min(cutby[name]['video_frames'],math.ceil((ws[-1]['end']+.20)*24))
    dialogues[key]={'id':key,'episode':d['episode'],'source_docx_paragraph':paragraph,'source_path':d['source_path'],'source_sha256':d['source_sha256'],
        'source_in_frame':inf,'source_out_frame_exclusive':outf,'source_fps':24,'source_in_seconds':inf/24,'source_out_seconds':outf/24,
        'recognized_text':''.join(w['word'] for w in ws).strip(),'first_word_seconds':ws[0]['start'],'last_word_seconds':ws[-1]['end'],
        'word_indices':[a,b],'words':ws,'source_range_status':'ASR_with_conservative_handles_not_auditioned',
        'timeline_record_frame':None,'sync_audio_must_link_to_picture':True,'narration_must_not_cover_spoken_words':True,
        'note':'源片17-5-1内两句之间停顿也保留，不能把对方反应切掉后再重复提问。' if key=='E17_cat_invitation' else ''}

episodes=[]
capacity=[]
for epc in coverage['episodes']:
    ep=epc['episode'];blocks=[]
    for c in epc['groups']:
        g=c['source_group'];main=c['source_candidates'][0];name=main['filename'];shotlist=cutby[name]['shots']
        enabled=not(ep==17 and g==6)
        block={'block_id':f'EP{ep}_G{g:02}','order':g,'enabled_by_default':enabled,'episode':ep,'source_group':g,
            'source_docx_paragraph_range':c['source_docx_paragraph_range'],'purpose':c['coverage'],'editing_note':c['editing_note'],
            'primary_picture':{'path':main['path'],'source_sha256':sourceby[name]['source_sha256'],'source_fps':24,
                'source_in_frame':0,'source_out_frame_exclusive':cutby[name]['video_frames'],'source_in_seconds':0,'source_out_seconds':cutby[name]['video_duration_seconds'],
                'ordered_source_shots':shotlist,'native_speed_percent':100,'same_source_sync_audio':True},
            'alternative_or_insert_sources':c['source_candidates'][1:],'mandatory_dialogue_ids':[],
            'narration_sentence_anchors':[],'timeline_record_frame':None,'timeline_duration_frames':None,
            'fit_strategy':'先按新旁白实际句边映射本组原文，再剪短各非对白镜；需延长时只用未用过的同场补镜，不循环同动作、不自动冻结/慢放，不铺黑。'}
        if ep==17 and g==5:block['mandatory_dialogue_ids']=['E17_cat_invitation']
        if ep==19:
            block['mandatory_dialogue_ids']={1:['E19_question'],2:['E19_nurse_report','E19_nurse_question','E19_nurse_answer'],3:['E19_mother_devalues'],4:['E19_mother_impatient']}.get(g,[])
            if g==2:
                block['selected_dialogue_audio_video_sequence']=['E19_nurse_report','E19_nurse_question','E19_nurse_answer']
                block['range_exclusions']=[{'source':'男版19-2-1.mp4','source_in_frame':0,'source_out_frame_exclusive':84,'reason':'第一句用2-2的安全入声特写，不能再播放2-1同句重复。'}]
            if g==3:
                block['primary_picture']['path']=sourceby['男版19-3-2.mp4']['source_path']
                block['warning']='此处只是门缝听见，正式进入在P536；不能把19-3-1开头拉门与19-4-3完整推门连续重复。'
            if g==4:
                block['post_dialogue_picture']={'path':sourceby['男版19-4-3.mp4']['source_path'],'source_in_frame':0,'source_out_frame_exclusive':cutby['男版19-4-3.mp4']['video_frames'],'source_fps':24,'native_speed_percent':100,'purpose':'P536说完母亲不耐烦台词后，Oliver真正推门进入；该动作只用一次。'}
        if ep==16 and g==6:block['replacement_option']='若用16-8-1密码特写，只替换16-6-1中同一锁动作；不要完整顺拼两个合本/拨锁。'
        if ep==17 and g==6:block['exclusion_reason']='原稿EP17未明确出现窗帘窥视动作，默认不使用；保留作候选证据，不能为延长旁白强行新增剧情。'
        if ep==18 and g==2:
            name='男版18-2-3.mp4';block['primary_picture'].update(path=sourceby[name]['source_path'],source_sha256=sourceby[name]['source_sha256'],source_out_frame_exclusive=cutby[name]['video_frames'],source_out_seconds=cutby[name]['video_duration_seconds'],ordered_source_shots=cutby[name]['shots'])
            block['alternative_or_insert_sources']=[c['source_candidates'][0]]
        picture=block['primary_picture']
        block['picture_order_source_units']=[{'path':picture['path'],'source_in_frame':picture['source_in_frame'],
            'source_out_frame_exclusive':picture['source_out_frame_exclusive'],'source_fps':24,'native_speed_percent':100,
            'same_source_same_bounds_linked_sync_audio':True,'record_frame':None}]
        if ep==19 and g==2:
            block['picture_order_source_units']=[
                {'path':sourceby['男版19-2-2.mp4']['source_path'],'source_in_frame':0,'source_out_frame_exclusive':121,'source_fps':24,'native_speed_percent':100,
                 'same_source_same_bounds_linked_sync_audio':True,'record_frame':None,'purpose':'护士首句只在此播放一次，有半秒安全起声。'},
                {'path':sourceby['男版19-2-1.mp4']['source_path'],'source_in_frame':84,'source_out_frame_exclusive':481,'source_fps':24,'native_speed_percent':100,
                 'same_source_same_bounds_linked_sync_audio':True,'record_frame':None,'purpose':'避开已播放的首句（3.28秒结束），保留Oliver反应、护士后两句和向病房走；不重复第一句。'}]
        if block.get('post_dialogue_picture'):
            q=block['post_dialogue_picture']
            block['picture_order_source_units'].append({'path':q['path'],'source_in_frame':q['source_in_frame'],'source_out_frame_exclusive':q['source_out_frame_exclusive'],
                'source_fps':24,'native_speed_percent':100,'same_source_same_bounds_linked_sync_audio':True,'record_frame':None,'purpose':q['purpose']})
        pars=c['source_docx_paragraph_range']
        if pars:
            for group in manifest['groups']:
                if group['episode']!=ep:continue
                hits=[p for p in group['source_docx_paragraphs'] if pars[0]<=p<=pars[1]]
                if hits:block['narration_sentence_anchors'].append({'audio_basename':group['basename'],'planned_audio_path':group['planned_audio_path'],'source_docx_paragraphs':hits,'new_audio_word_ranges':None,'record_frame':None})
        blocks.append(block)
    vo=[g for g in manifest['groups'] if g['episode']==ep]
    words=sum(g['words'] for g in vo)
    primary_frames=sum(c['source_out_frame_exclusive']-c['source_in_frame'] for b in blocks if b['enabled_by_default'] for c in b['picture_order_source_units'])
    dialogue_seconds=sum((d['source_out_frame_exclusive']-d['source_in_frame'])/24 for d in dialogues.values() if d['episode']==ep)
    seconds=primary_frames/24
    cap={'episode':ep,'narration_words':words,'new_narration_duration_seconds':None,'selected_main_source_seconds_upper_bound':seconds,
        'mandatory_dialogue_candidate_seconds_including_handles':dialogue_seconds,'main_source_non_dialogue_seconds_upper_bound':max(0,seconds-dialogue_seconds),
        'minimum_average_vo_wpm_to_fit_main_sources_without_extra_shots':round(words/max(.1,seconds-dialogue_seconds)*60,1),
        'length_status':'待新旁白实测，不能据估计拍板','note':'这是原速主版本全部源帧的上限，包含不一定能用的停顿/重复构图；实际可用时长可能更短。补特写仅在不复演同动作时追加。'}
    capacity.append(cap)
    episodes.append({'episode':ep,'timeline_name_candidate':f'大码_男版_EP{ep}_新男版音色_原速旁白_自动剪辑_v1','source_fps':24,'timeline_fps':24,'timeline_start_timecode':'00:00:00:00',
        'timeline_duration_frames':None,'track_plan':{'V1':f'男版{ep}_剧情画面','A1':'同期声_与画面链接','A2':'Oliver新男版音色_100%旁白'},
        'blocks':blocks,'narration_files':[{'basename':g['basename'],'path':g['planned_audio_path'],'source_docx_paragraphs':g['source_docx_paragraphs'],'word_count':g['words'],'native_speed_percent':100,'source_in_frame':None,'source_out_frame_exclusive':None,'record_frame':None} for g in vo],
        'dialogue_order':[k for k,d in dialogues.items() if d['episode']==ep],'capacity_audit':cap})
out={'schema':'male_episode_source_framework_v1','status':'AWAITING_NEW_NARRATION_MEASURED_TIMES_NOT_EXECUTABLE','frame_boundary_convention':'All source_out_frame_exclusive excludes the final frame; 24fps, exact integer source frames.',
    'no_resolve_mutation':True,'new_narration_seconds_intentionally_unset':True,'episodes':episodes,'mandatory_dialogue_units':list(dialogues.values()),
    'quoted_text_insertion_anchors':insertions,
    'do_not_loop_or_duplicate':[
        {'sources':['男版18-3-2.mp4','男版18-3-5.mp4'],'reason':'SHA256完全同文件，只能用一次。'},
        {'sources':['男版18-4-2.mp4','男版18-4-4.mp4'],'reason':'SHA256完全同文件，只能用一次。'},
        {'sources':['男版18-2-1.mp4','男版18-2-3.mp4'],'reason':'同次开会手机提醒重做，不得顺拼成两次来信。'},
        {'sources':['男版18-3-1.mp4','男版18-3-3.mp4'],'reason':'同次好友申请/惊讶重做，择一主版。'},
        {'sources':['男版18-4-1.mp4','男版18-4-3.mp4'],'reason':'同次厨房看回复重做，择一主版。'},
        {'sources':['男版18-6-1.mp4','男版18-6-2.mp4','男版18-6-3.mp4'],'reason':'同一次坐窗边看手机/思索重做，不能串三个完整版本。'},
        {'sources':['男版18-7-1.mp4','男版18-7-2.mp4'],'reason':'同次看请求/窗边反应重做，择一。'},
        {'sources':['男版19-2-1.mp4','男版19-2-2.mp4'],'reason':'护士第一句重复，不能念两遍；后两句仅2-1有。'},
        {'sources':['男版19-3-1.mp4','男版19-3-2.mp4'],'reason':'母亲同一贬低段对白两个版本，择一。'},
        {'sources':['男版19-4-1.mp4','男版19-4-2.mp4'],'reason':'同一句母亲不耐烦对白，择一；之后只一次推门。'},
        {'sources':['男版16-6-1.mp4','男版16-8-1.mp4'],'reason':'同一次日记收本/拨锁；补特写替换，不能为了旁白时长重复完整动作。'}],
    'black_frame_guard':{'final_edit_has_no_timeline_positions_yet':True,'required_before_assembly':['用新VO逐词ASR与原文句子对齐，设置真实源入出和record位置。','展开视频列表必须从frame0连续覆盖到最后音频尾，逐片段检查无空隙/黑场。','若原速旁白+完整对白超过可用画面，先用未用的同场独立镜头补覆盖；仍不足则记录具体缺口，不能循环动作、黑场、偷偷加速/拉长静帧。','每个V1片段必须有A1同源同入出同record且链接；所有素材路径存在。','源解码瞬态已测部分>0dBFS，混音后检查真峰并适当衰减。']},
    'parent_scripts_to_adapt':[str(base_scripts/'assemble_native.py'),str(base_scripts/'verify_save_reopen.py')],
    'remaining_limits':['候选源范围来自ASR和抽样画面，尚未逐句人工听验。','手机文字未逐字验收，不假设生成英文短信已正确。','EP16-3-1游泳[58,90)与饮食[90,120)已逐切核验，纳入原文旁白。']}
dest=BASE/'男版16-19_自动剪辑计划框架.json'
dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(BASE/'主版本画面容量_待旁白实测.json').write_text(json.dumps(capacity,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'framework':str(dest),'episodes':len(episodes),'ordered_blocks':sum(len(e['blocks']) for e in episodes),'mandatory_original_dialogue_units':len(dialogues),'capacity':capacity},ensure_ascii=False))
