from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as E
import re, json, hashlib
BASE=Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕')
OUT=BASE/'达芬奇剪辑_EP21-25_20261020'
OUT.mkdir(exist_ok=True)
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
def read_docx(p):
    root=E.fromstring(ZipFile(p).read('word/document.xml'))
    return [''.join(t.text or '' for t in n.findall('.//w:t',NS)) for n in root.findall('.//w:p',NS)]
def split_episodes(paras):
    result={}; ep=None
    for idx,text in enumerate(paras):
        m=re.fullmatch(r'(?:第(\d+)集|Episode\s+(\d+))',text.strip(),re.I)
        if m:
            ep=int(m.group(1) or m.group(2));result[ep]=[]
        elif ep is not None and text.strip():
            result[ep].append({'paragraph_index_0based':idx,'text':text})
    return result
en_path=BASE/'完整剧本/我不再做教父的大码人形抱枕EN.docx'
zh_path=BASE/'完整剧本/我不再做教父的大码人形抱枕.docx'
en=split_episodes(read_docx(en_path)); zh=split_episodes(read_docx(zh_path))
speaker_override={
    21:{630:'Eliza',633:'Eliza',634:'Eliza',636:'Matteo',640:'Matteo',641:'Matteo',643:'Matteo',644:'Eliza',**{i:'Matteo' for i in range(646,655)}},
    22:{658:'Eliza',659:'Eliza',660:'Eliza',662:'Matteo',663:'Matteo',665:'Eliza',**{i:'Matteo' for i in range(668,681)}},
    23:{i:'Matteo' for i in range(683,710)},
    24:{**{i:'Eliza' for i in range(715,722)},723:'Matteo',724:'Eliza',728:'Eliza',729:'Eliza'},
    25:{743:'Professor / 导师（原稿未写性别）',751:'Eliza',753:'Evan'}
}
beats={
21:[(625,631,'病房静默—看愿望券忆日记—撕券入垃圾桶—男主僵住—愿望过期—脸色苍白'),
    (632,639,'女主起身整理外套—劝治疗—到门口—醉夜认人告白叫停—迟到一年'),
    (640,643,'男主说明Vincent欲联系Alessia—车内按住手机闪回—从头到尾想找Eliza'),
    (644,647,'女主追问为何羞辱—男主垂眼—五年前东翼钥匙与医疗中心'),
    (648,654,'听见只为钱—读日记后受骗感—报复动机—把她变回雇员以否认影响')],
22:[(657,663,'女主指出知道是她仍扔支票的残忍—男主慌乱下床—愿去纽约等原谅'),
    (664,671,'女主想起鲜花—拆穿邻居身份—男主僵住承认—第三个月找到她—Vincent搜索与身份迟疑'),
    (672,680,'纽约街头闪回：女主抱花与朋友走出咖啡馆，男主黑车旁—欲带回但看到轻松笑容—前进两步又退回阴影—不敢叫她')],
23:[(683,690,'买邻居公寓、换花、复刻床品玩偶、靠墙—听归家才关灯—交钥匙和推床闪回—听走动才闭眼'),
    (691,696,'声音渐低—她一夜未归—手抵墙闪回—等到天亮—猜她是否恋爱、亲吻和拥抱别人'),
    (697,700,'想起她每次在酒店外等待—想敲门却无资格—理解她等他带女人回去的感受'),
    (701,709,'回芝加哥后的噩梦—梦里Eliza说疼—醒来加药—酒精忘剂量住院—对比她忍受十年—道歉')],
24:[(712,721,'听完不被迟来真相打动—指出邻居跟踪不尊重—没有问是否愿意—生活被当财产—秘密邻居不是保护'),
    (722,729,'男主问是否爱上别人—已经与你无关—手垂下—最后看他—不再原地等珍惜—回头时已离开'),
    (730,736,'推病房门走向亮走廊，男主未追—飞机回纽约—十八岁先他、二十八岁先自己—晨昏线—不回头')],
25:[(739,746,'纽约医学研究所继续工作，不表演新生活—导师正式合同与劝告—签名—无教育信托、无陪睡附加条件'),
    (747,753,'Evan与捡球猫、偶尔吃饭—不急证值得—他正式表白—女主说慢一点—Evan接受'),
    (754,757,'隔壁公寓再出售—新邻居不换花不监听—睡得更好'),
    (758,760,'Serafina道歉信未拆退回—原谅非受伤者义务'),
    (761,765,'一年后同一花店镜中健康与自在笑容—不再以男人选择证明价值')]
}
differences={
21:[
{'kind':'episode_number','detail':'视觉21.md与EN Episode21相同，对应中文第22集。中文第21集为EN20的陪病与愿望券来历，不能剪进当前EP21开头。'},
{'kind':'order_changed','detail':'旧21.md先描写男主脸色惨白，再女主起身整理大衣说愿望过期；原文是手僵住→Eliza说愿望过期→脸色苍白→起身整理大衣。'},
{'kind':'dialogue_omitted','source_en_paragraphs':[640,641],'detail':'旧分镜跳过男主关于Vincent问去哪里、他阻止联系Alessia的两句解释，直接进入车内闪回。原稿两句仍属本集。'},
{'kind':'untranslated_stage_dialogue','source_en_paragraphs':[642],'detail':'EN DOCX闪回舞台说明中的台词仍为中文“带我去找Eliza。”，没有给英文版本。字幕须依素材实际英文口播转写，不自行把翻译冒充英文原稿。'},
{'kind':'direction_only','detail':'捂脸定格、门把手特写、黑屏等是旧分镜的拍摄/剪辑处理，不等于新增剧情，不能因此删掉原剧情。'}],
22:[
{'kind':'episode_number','detail':'EN22及视觉22.md对应中文23。'},
{'kind':'dialogue_omitted','source_en_paragraphs':[670,671],'detail':'旧22.md遗漏Vincent查遍访问研究项目、医院和实验室，以及男主真正看到女主时不知道以何种身份靠近的两句。'},
{'kind':'expanded_direction','detail':'旧分镜“不顾输液针头、踉跄跌下床”比原稿“慌乱地下床”更具体；原稿并无拔针或摔伤事件，不把素材的额外事故当剧情。'},
{'kind':'expanded_direction','detail':'旧分镜的“试图穿过马路”是路线解释；原稿明确动作只有前走两步、见她笑而停、退回阴影。不得剪成已经横穿街道或与女主见面。'}],
23:[
{'kind':'episode_number','detail':'EN23及视觉23.md对应中文24。'},
{'kind':'order_changed','source_en_paragraphs':[688,689,690],'detail':'原文先说听她回家才敢关灯，再交钥匙/推床闪回，再说听她走动才闭眼；旧分镜在同段OS先说走动闭眼后说回家关灯。按原文顺序排对白。'},
{'kind':'order_changed_or_omitted','source_en_paragraphs':[697,698,699,700],'detail':'原文顺序为想起她每夜酒店外等待→想敲门→知道无资格→那晚明白带女人回去时她的等待；旧分镜省略酒店外等待句，并把“那晚明白”移到想敲门前。'},
{'kind':'expanded_direction','detail':'“什么家具都没买，只买一张床”、贴墙听声、泪滴地板等为旧分镜细节，不是原稿新增对白；不得扩成女主回邻居屋或两人隔墙互动等新事件。'}],
24:[
{'kind':'episode_number','detail':'EN24及视觉24.md对应中文25。'},
{'kind':'direction_only','detail':'女主前行一步、男主后退一步、门缝特写、机翼空镜、黑屏等是旧分镜的表现手段；原稿核心顺序是边界对白→追问别人→最终拒绝→手垂下→离房未追→回纽约飞机。'},
{'kind':'narration_scope','detail':'原文包含飞机穿云、晨昏线等叙述；它们也可由画面承载。是否作为已录旁白或字幕必须以现有音轨实听为准，不为覆盖文字另写/另录旁白。'}],
25:[
{'kind':'episode_number','detail':'EN25及视觉25.md对应中文26；不是中文第25集的离开病房与回纽约飞机。'},
{'kind':'invented_dialogue','detail':'旧25.md增加Evan“我是认真的，我想成为陪你走下去的那个人”；原稿只叙述他正式表白，没有给他此句直接对白。若素材实际含此句，应标为改编对白，不可当原剧本保留。'},
{'kind':'dialogue_expanded','source_en_paragraphs':[751],'detail':'旧25.md的Eliza“谢谢你，Evan。但我需要慢一点。”比原文增添道谢与称呼；英文原句仅“I need to take things slowly.”。Evan回答原文为“Then we’ll take it slowly.”（以原文拼写字符为准）。'},
{'kind':'new_detail','detail':'白发女导师、年轻夫妇新邻居、Bellandi火漆、收件包、日历、向日葵及衣物颜色是旧分镜视觉具体化；原稿未规定这些身份/物件细节。剪辑可用相容画面，不能据此新增台词或事件因果。'},
{'kind':'order_changed','detail':'原文先叙述公寓出售/新邻居/睡更安稳，再Serafina信件，最后一年后花店；旧分镜把具体入睡画面排在退信后。若按剧情顺序，应把安睡表现归回新邻居段，再退信，再一年后。'},
{'kind':'end_boundary','detail':'本集止于不需要男人选择证明价值。之后Matteo系统治疗和最后纽约街角合流属于后续集，不能自动拼入EP25。'}]
}
episodes=[]
for ep in range(21,26):
    items=[]
    for no,item in enumerate(en[ep],1):
        text=item['text'];idx=item['paragraph_index_0based']
        stage=text.startswith('【')
        direct=text.startswith('"') and text.endswith('"')
        mixed=ep==25 and idx==751
        kind='stage_direction' if stage else ('mixed_narration_and_dialogue' if mixed else ('dialogue' if direct else 'source_narration'))
        speaker=None if stage else (speaker_override[ep].get(idx,'UNKNOWN') if direct or mixed else 'Eliza / narrator')
        quoted=re.findall(r'"([^"]*)"',text)
        items.append({'order':no,'source_file':str(en_path),'source_episode':ep,'paragraph_index_0based':idx,'kind':kind,'speaker':speaker,'text_verbatim':text,'direct_dialogue_texts_verbatim':quoted if not stage else [],'stage_dialogue_needs_actual_audio_transcription':bool(stage and quoted),'subtitle_timing':None,'audio_verification_required':True})
    vdir=BASE/'剧梦生成视频片段/女版'/f'EP{ep}'
    def media_key(path):
        m=re.fullmatch(r'女版(\d+)-(\d+)([A-Z]?)-(\d+)\.mp4',path.name)
        return (int(m[2]),m[3],int(m[4])) if m else (999,'',999)
    vids=[]
    for path in sorted(vdir.glob('*.mp4'),key=media_key):
        key=media_key(path)
        vids.append({'path':str(path),'filename':path.name,'numeric_group':key[0],'group_suffix':key[1],'trailing_number':key[2],'content_match_status':'name_only_not_playback_verified','trailing_number_meaning':'可能是替代take或连续片段，须由画面与实际对白核验，不可只取最大数字'})
    aud=[]
    for path in sorted((BASE/'剧梦生成视频片段/独白'/f'EP{ep}').glob('*.mp3'),key=lambda p:int(re.search(r'-(\d+)\.mp3$',p.name)[1])):
        dup=BASE/'剧梦生成视频片段/女版/独白'/f'EP{ep}'/path.name
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        aud.append({'path':str(path),'filename':path.name,'sha256':digest,'duplicate_path':str(dup),'duplicate_sha256_matches':dup.exists() and hashlib.sha256(dup.read_bytes()).hexdigest()==digest,'transcript_status':'not_listened_in_this_review','content_assignment':'需将既有MP3实听/转写后映射原稿叙述；不要因序号相同就重复铺两套'})
    eps_beats=[{'order':k+1,'source_en_paragraphs_inclusive':[a,z],'plot_summary_zh':desc,'media_group_assignment':'pending_audio_visual_verification'} for k,(a,z,desc) in enumerate(beats[ep])]
    mdpath=BASE/'视觉设计/画面设计和分镜'/f'{ep}.md'
    episodes.append({'episode':ep,'timeline_label_expected':f'EP{ep:02d}','numbering_map':{'english_docx_episode':ep,'visual_md_episode':ep,'chinese_docx_episode':ep+1},'source_en_items':items,'source_zh_paragraphs_verbatim':zh[ep+1],'plot_beats':eps_beats,'storyboard_file':str(mdpath),'storyboard_text_verbatim':mdpath.read_text(),'script_storyboard_differences':differences[ep],'media_naming_pattern':f'女版{ep}-组号-末尾号.mp4（EP21/22常用两位补零；EP22含05B/05C）','video_inventory':vids,'narration_inventory':aud})
result={'project':BASE.name,'created_date':'2026-10-20','purpose':'EP21–25剪辑用原稿顺序与素材命名核对，未操作Resolve、未生成字幕时码。','authority':{'english_source':str(en_path),'chinese_source':str(zh_path),'primary_episode_numbering':'英文DOCX Episode21–25，与视觉分镜21–25及现有视频EP21–25目录一致','chinese_numbering_warning':'相同剧情对应中文第22–26集；中文第21集为英文20，不能按中文21标题拼入当前EP21。'},'source_handling':{'dialogue':'英文对白逐段原文保留；舞台说明不朗读。','narration':'source_narration是原文叙述候选，并不证明MP3已录该句；最终SRT仅按实际采用且可听音轨转写。','no_new_voiceover':True,'no_estimated_subtitle_timestamps':True,'variant_take_warning':'末尾数字并不能单独证明是版本号还是续镜，必须核验内容。'},'episodes':episodes,'excluded_context':{'chinese_episode_21_equals_english_20':zh[21]},'counts':{'video_files':sum(len(e['video_inventory']) for e in episodes),'narration_files_single_set':sum(len(e['narration_inventory']) for e in episodes),'narration_duplicate_sets':2,'source_english_items':sum(len(e['source_en_items']) for e in episodes)}}
(OUT/'剧情顺序.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
md=['# EP21–25剧情顺序核对','',
'本核对读取完整中英DOCX、视觉设计/画面设计和分镜/21.md–25.md及当前素材文件名。未播放素材、未操作Resolve，未估字幕时码，未新写旁白。','',
'## 集号须先对齐','',
'现有视频EP21–25和视觉21.md–25.md按英文DOCX集号：对应中文DOCX第22–26集。中文第21集“陪坐/愿望券来历”是英文第20集，不应误接在当前EP21开头。','',
'英文原稿是本批英文对白与集号的排序依据，中文用于核对剧情含义。文件名只能确定候选组号，不能证明具体画面或对白，也不能仅凭末尾号决定take。两处独白目录每套18份MP3逐一SHA256相同，铺轨时只用一套。','',
'## 各集原文与顺序','']
for e in episodes:
    ep=e['episode']
    md += [f'### EP{ep}（英文{ep} / 中文{ep+1} / 视觉分镜{ep}）','']
    md += ['剧情顺序：','']+[f"{b['order']}. {b['plot_summary_zh']}（EN XML段落{b['source_en_paragraphs_inclusive'][0]}–{b['source_en_paragraphs_inclusive'][1]}）" for b in e['plot_beats']]+['']
    md += ['英文原文顺序（XML段落为从0计数；旁白仅为原文叙述候选，是否发声以实际音轨为准）：','']
    for it in e['source_en_items']:
        label={'stage_direction':'画面说明/不朗读','dialogue':'对白','mixed_narration_and_dialogue':'叙述含原对白','source_narration':'原文叙述'}[it['kind']]
        speaker=(' / '+it['speaker']) if it['speaker'] else ''
        md += [f"- [{it['paragraph_index_0based']}] **{label}{speaker}**：{it['text_verbatim']}"]
    md += ['','中文原稿同段（保留原文顺序）：','']
    md += [f"- [{x['paragraph_index_0based']}] {x['text']}" for x in e['source_zh_paragraphs_verbatim']]
    md += ['','旧分镜与原稿的差异：','']
    md += ['- '+x['detail'] for x in e['script_storyboard_differences']]
    md += ['','现有视频候选（按组号自然排序，尚未画面验收；末尾号不自动视作需全部顺接或只留最新版）：','']
    md += ['- '+x['filename'] for x in e['video_inventory']]
    md += ['','既有独白单套文件：','']
    md += ['- '+x['filename']+'（另一目录同名文件SHA256一致）' for x in e['narration_inventory']]
    md += ['','素材命名预期：'+e['media_naming_pattern']+'；具体段落归属须由素材音画核验，JSON中均标为待核验。','']
md += ['## 剪辑与字幕边界','',
'保留源剧情和已采用音轨的真实发声顺序；旧分镜的改编对白、漏句与重排应先核对。纯舞台说明、无声可见行动和没有录制的原文叙述不自动生成字幕。没有实际音轨对齐前，不填SRT时间码。','',
'本批结束于EN25“我不再需要男人选择证明价值”。后续Matteo治疗、纽约朋友合流不自动拼入。','']
(OUT/'剧情顺序核对.md').write_text('\n'.join(md))
print(json.dumps(result['counts'],ensure_ascii=False))
print(OUT/'剧情顺序核对.md')
print(OUT/'剧情顺序.json')

