from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as E
import json,re,shutil,datetime
BASE=Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕')
D=BASE/'达芬奇剪辑_EP21-25_20261020'
stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
backup=D/('备份_更正集号前_'+stamp);backup.mkdir()
for fn in ['剧情顺序.json','剧情顺序核对.md','build_plot_order_review.py']:
    p=D/fn
    if p.exists():shutil.copy2(p,backup/fn)
old=json.loads((D/'剧情顺序.json').read_text());old_by={e['episode']:e for e in old['episodes']}
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
def read(p):
    r=E.fromstring(ZipFile(p).read('word/document.xml'));return [''.join(t.text or '' for t in n.findall('.//w:t',NS)) for n in r.findall('.//w:p',NS)]
def eps(a):
    out={};ep=None
    for idx,t in enumerate(a):
        m=re.fullmatch(r'(?:第(\d+)集|Episode\s+(\d+))',t.strip(),re.I)
        if m:ep=int(m.group(1) or m.group(2));out[ep]=[]
        elif ep is not None and t.strip():out[ep].append({'paragraph_index_0based':idx,'text':t})
    return out
enfile=BASE/'完整剧本/我不再做教父的大码人形抱枕EN.docx';cnfile=BASE/'完整剧本/我不再做教父的大码人形抱枕.docx'
EN=eps(read(enfile));CN=eps(read(cnfile))
new=[]
for folder in range(21,26):
    eng=folder-1;media=old_by[folder]
    if eng in old_by:
        e=json.loads(json.dumps(old_by[eng],ensure_ascii=False))
        e['episode']=folder;e['source_en_items']=[dict(x) for x in e['source_en_items']]
    else:
        e={};items=[]
        speaks={596:'Matteo',602:'Matteo',608:'Eliza（十八岁回忆）',609:'Eliza（十八岁回忆）',613:'Eliza',622:'Matteo'}
        for no,x in enumerate(EN[eng],1):
            idx=x['paragraph_index_0based'];t=x['text'];stage=t.startswith('【');direct=t.startswith('"') and t.endswith('"')
            items.append({'order':no,'source_file':str(enfile),'source_episode':eng,'paragraph_index_0based':idx,'kind':'stage_direction' if stage else 'dialogue' if direct else 'source_narration','speaker':None if stage else speaks.get(idx,'Eliza / narrator'),'text_verbatim':t,'direct_dialogue_texts_verbatim':re.findall(r'"([^"]*)"',t) if direct else [],'stage_dialogue_needs_actual_audio_transcription':False,'subtitle_timing':None,'audio_verification_required':True})
        e['source_en_items']=items
        e['plot_beats']=[
            {'order':1,'source_en_paragraphs_inclusive':[593,599],'plot_summary_zh':'女主建议创伤治疗；男主请求陪坐；她落座，他握腕闭眼，床边看文件，白昼至黄昏。'},
            {'order':2,'source_en_paragraphs_inclusive':[600,602],'plot_summary_zh':'两小时后睡着；抽手惊醒，抓衣角，请她别走。'},
            {'order':3,'source_en_paragraphs_inclusive':[603,605],'plot_summary_zh':'从枕下取出保存十年的泛黄ONE WISH愿望券。'},
            {'order':4,'source_en_paragraphs_inclusive':[606,609],'plot_summary_zh':'十八岁获救后的回忆：画笑脸，送愿望券，说不要难过、可换一个愿望。'},
            {'order':5,'source_en_paragraphs_inclusive':[610,619],'plot_summary_zh':'现在递券；女主对比珍藏承诺与撕碎心意，问想换什么，并准备拒绝回庄园、陪睡、放弃纽约。'},
            {'order':6,'source_en_paragraphs_inclusive':[620,622],'plot_summary_zh':'男主攥床单红眼，只请求再抱一次。'}]
        e['script_storyboard_differences']=[]
    e['episode']=folder
    e['timeline_label_expected']=f'EP{folder:02d}'
    e['numbering_map']={'folder_episode':folder,'chinese_docx_episode':folder,'english_docx_episode':eng,'requested_visual_md_episode':folder,'visual_md_same_number_is_next_episode':True}
    e['source_zh_paragraphs_verbatim']=CN[folder]
    e['previous_differences_for_same_story_content']=e.pop('script_storyboard_differences',[])
    e['script_storyboard_differences']=[{'kind':'storyboard_number_mismatch','detail':f'视觉{folder}.md按英文{folder}集编排，内容对应中文{folder+1}，比当前素材EP{folder}实际中文{folder}/英文{eng}晚一集。不能把这个同号MD当当前剪辑顺序权威。'}]
    e['video_inventory']=media['video_inventory'];e['narration_inventory']=media['narration_inventory']
    e['media_naming_pattern']=media['media_naming_pattern']
    mdp=BASE/'视觉设计/画面设计和分镜'/f'{folder}.md';e['storyboard_file']=str(mdp);e['storyboard_text_verbatim']=mdp.read_text();e['storyboard_is_authority_for_this_folder']=False
    e['actual_visual_confirmation']='EP21–23已实看关键候选画面，符合中文同号；EP24–25由主任务平行核验确认。'
    new.append(e)
old['episodes']=new;old['authority']={'english_source':str(enfile),'chinese_source':str(cnfile),'primary_episode_numbering':'本地素材文件夹EP21–25与中文DOCX第21–25集；英文对应Episode20–24','numbering_correction':'实看EP21握手陪睡/愿望券等画面后更正了先前EN同号假设；旧核对已完整备份。','visual_md_warning':'同号视觉21–25.md对应下一集剧情，不作为当前剪辑顺序权威。'}
old['excluded_context']={'not_in_folder_EP25':{'english_episode_25':'纽约新生活/正式聘用/慢一点/退回道歉信/花店镜中价值，中文第26集；不自动插进本批EP25。'}}
old['counts']={'video_files':sum(len(e['video_inventory']) for e in new),'narration_files_single_set':sum(len(e['narration_inventory']) for e in new),'narration_duplicate_sets':2,'source_english_items':sum(len(e['source_en_items']) for e in new)}
old['numbering_corrected_at']=datetime.datetime.now().isoformat();old['previous_review_backup']=str(backup)
(D/'剧情顺序.json').write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
lines=['# EP21–25剧情顺序核对（实看后集号更正）','','本批按本地素材EP21–25及中文剧本第21–25集，英文原稿对应Episode20–24。此前以EN同号推断素材集号的版本已备份：'+str(backup),'','视觉设计/画面设计和分镜/21.md–25.md内容整体是下一集，不能作为当前同号素材的剪辑顺序权威。实际EP21已看见陪坐握手、睡着惊醒、愿望券回忆，明确属于中文21/英文20。','','未估字幕时码；叙述项只是原稿候选，不证明已录旁白。最终SRT依实际采用音轨，不新增旁白。','']
for e in new:
    n=e['episode'];lines += [f"## 素材EP{n} / 中文第{n}集 / EN Episode{n-1}",'','剧情节拍：','']
    lines += [str(b['order'])+'. '+b['plot_summary_zh'] for b in e['plot_beats']]
    lines += ['','英文原文顺序：','']
    for x in e['source_en_items']:
        label={'stage_direction':'画面说明，不朗读','dialogue':'对白','mixed_narration_and_dialogue':'叙述含原对白','source_narration':'原文叙述候选'}[x['kind']]
        lines.append(f"- [{x['paragraph_index_0based']}] {label} / {x['speaker'] or '无说话人'}：{x['text_verbatim']}")
    lines += ['','中文同号原文顺序：','']+[f"- [{x['paragraph_index_0based']}] {x['text']}" for x in e['source_zh_paragraphs_verbatim']]
    lines += ['','旧分镜适配风险：','']+['- '+x['detail'] for x in e['script_storyboard_differences']]
    if e['previous_differences_for_same_story_content']:
        lines += ['','针对该剧情的旧视觉稿差异历史参考（不改变本批素材集号）：','']+['- '+x['detail'] for x in e['previous_differences_for_same_story_content'] if x['kind']!='episode_number']
    lines += ['','当前候选视频文件（末尾数字可能为版本或续镜，须实看）：','']+['- '+x['filename'] for x in e['video_inventory']]
    lines += ['','现有独白（两目录同名文件SHA256一致，只用一套）：','']+['- '+x['filename'] for x in e['narration_inventory']]+['']
lines += ['## 本批边界','','素材EP25/中文25/EN24以女主离开病房、男主未追、飞机回纽约、二十八岁把自己放第一位及不回头结束。EN25/中文26的纽约新生活不能因文件同号误入。','']
(D/'剧情顺序核对.md').write_text('\n'.join(lines))
# Disable accidental use of the obsolete same-number generator, preserving its full source in backup.
oldbuilder=D/'build_plot_order_review.py'
if oldbuilder.exists():oldbuilder.write_text("# Obsolete same-number assumption. Full source preserved in "+str(backup/'build_plot_order_review.py')+"\nraise SystemExit('Do not regenerate obsolete numbering; use corrected 剧情顺序.json')\n")
print('CORRECTED',old['counts'],'BACKUP',backup)

