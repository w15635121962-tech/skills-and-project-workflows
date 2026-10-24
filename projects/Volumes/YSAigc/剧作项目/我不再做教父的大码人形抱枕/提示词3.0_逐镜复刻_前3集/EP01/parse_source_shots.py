#!/usr/bin/env python3
"""Read original XLSX OOXML and preserve all EP01 source shot cells verbatim."""
from pathlib import Path
from decimal import Decimal
import collections
import hashlib
import json
import posixpath
import re
import zipfile
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parent.parent
SOURCE=PROJECT/'对标剧分镜截图和对标剧样片'
WORKBOOK=SOURCE/'分镜表格/电影级落地拍摄分镜脚本_人形抱枕第一集.xlsx'
IMAGES=SOURCE/'分镜截图/01人形抱枕_分镜截图_按时间 2'
TIMECODES=IMAGES/'分镜时间码清单.txt'
SCRIPT_PATHS={
    '女版':PROJECT/'配音制作_前3集/英文剧本/女版/女版_第01集_纯英文全文.txt',
    '性转男版':PROJECT/'配音制作_前3集/英文剧本/性转版/性转版_第01集_纯英文全文.txt',
}
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'd':'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing',
    'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'p':'http://schemas.openxmlformats.org/package/2006/relationships'}
COLS=list('ABCDEFGHIJK')


def sha(data):return hashlib.sha256(data).hexdigest()
def hashfile(p):return sha(p.read_bytes())
def text_nodes(node):return ''.join(n.text or '' for n in node.findall('.//m:t',NS)) if node is not None else ''
def secs(minutes, seconds):return Decimal(minutes)*60+Decimal(seconds)


def jpeg_dimensions(data):
    i=2
    while i<len(data):
        if data[i]!=255:i+=1;continue
        while data[i]==255:i+=1
        marker=data[i];i+=1
        if marker in [0xd8,0xd9] or 0xd0<=marker<=0xd7:continue
        length=int.from_bytes(data[i:i+2],'big')
        if marker in [0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf]:
            return {'width':int.from_bytes(data[i+5:i+7],'big'),'height':int.from_bytes(data[i+3:i+5],'big')}
        i+=length
    return None


def scene_category(text):
    first=text.split('。')[0]
    if '转场空间' in first:return 'transition_between_source_scenes'
    if '酒店' in first:return 'hotel_corridor' if '走廊' in first else 'hotel_suite_bedroom'
    if '豪车' in first:return 'luxury_car_driver_cabin' if '驾驶' in first else 'luxury_car_interior'
    if '会客厅' in first:return 'manor_reception_room'
    if '大厅' in first:return 'manor_grand_hall'
    if '走廊' in first:return 'manor_corridor_bedroom_entrance'
    if '主卧门' in first:return 'manor_bedroom_doorway'
    if '主卧' in first:return 'manor_master_bedroom'
    return 'unclassified_source_environment'


def role_mentions(text):
    result=[]
    if re.search(r'男主(?!情人|母亲)',text):result.append('source_boss_young' if '少年期' in text else 'source_boss_adult')
    if '女主' in text:result.append('source_narrator_young' if '童年期' in text else 'source_narrator_adult')
    if '教父夫人' in text or '男主母亲' in text:result.append('source_boss_mother')
    if '男主情人' in text:
        result.append('source_lover_redhair' if '红发' in text else 'source_lover_blonde')
    if '管家/送行者' in text:result.append('source_adult_escort_hand')
    return result


PROP_RULES={
    'contract_papers':('hero_prop',['合同','契约文件','纸张']),
    'checkbook_and_checks':('hero_prop',['支票']),
    'pen':('hero_prop',['钢笔']),
    'mobile_phone':('hero_prop',['手机']),
    'watch':('wardrobe_accessory',['腕表','名表','手表']),
    'teacup_saucer':('hero_prop',['茶杯','茶碟','茶托']),
    'ring_earrings':('wardrobe_accessory',['钻戒','戒指','耳坠']),
    'steering_wheel':('scene_integral_prop',['方向盘']),
    'bed_bedding_pillow':('scene_integral_prop',['大床','床头','床单','被子','锦被','枕头','抱枕']),
    'table_chair':('scene_integral_prop',['茶几','红木桌','扶手椅','丝绒椅']),
    'lamps_chandelier':('scene_integral_prop',['台灯','壁灯','吊灯']),
    'door_handle_doorframe':('scene_integral_prop',['门把手','门框','门扇','房门','木门']),
    'heels_underwear_wineglass':('visible_story_prop',['高跟鞋','内衣','高脚杯']),
    'lipstick_mark_on_collar':('body_or_costume_state',['唇印','口红印','唇痕']),
    'tattoos':('body_identity_state',['纹身']),
}


def main():
    initial_workbook_sha=hashfile(WORKBOOK)
    scripts={v:{'path':str(p),'sha256':hashfile(p),'text':p.read_text(encoding='utf-8'),
                'authority':'Identity/name and corresponding-dialogue auxiliary only; never changes the XLSX shot count, order, framing or source action.'}
             for v,p in SCRIPT_PATHS.items()}
    image_files=sorted(IMAGES.glob('shot_*.jpg'))
    image_index=collections.defaultdict(list)
    for p in image_files:
        match=re.fullmatch(r'shot_(\d+)_(\d+)m([\d.]+)s\.jpg',p.name)
        assert match,p.name
        image_index[int(match[1])].append((p,secs(match[2],match[3])))
    timecode_entries={}
    for line in TIMECODES.read_text(encoding='utf-8').splitlines():
        match=re.fullmatch(r'(\d+)\t(\d+)m([\d.]+)s\t(.+)',line)
        if match:timecode_entries[int(match[1])]={'start_seconds_exact':str(secs(match[2],match[3])),'filename':match[4]}
    issues=[];shots=[];headers={};sheet_metadata=[]
    with zipfile.ZipFile(WORKBOOK) as z:
        assert z.testzip() is None
        shared=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            shared=[text_nodes(si) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS)]
        book=ET.fromstring(z.read('xl/workbook.xml'))
        rels={r.get('Id'):r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        for sheet in book.findall('m:sheets/m:sheet',NS):
            target=rels[sheet.get('{'+NS['r']+'}id')]
            sheet_path=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target)
            xml=ET.fromstring(z.read(sheet_path));rows=xml.findall('m:sheetData/m:row',NS)
            cells_by_row={}
            formula_count=0
            for row in rows:
                cells={}
                for c in row.findall('m:c',NS):
                    typ=c.get('t');value_node=c.find('m:v',NS)
                    value=value_node.text or '' if value_node is not None else ''
                    if typ=='inlineStr':value=text_nodes(c.find('m:is',NS))
                    elif typ=='s':value=shared[int(value)]
                    formula=c.find('m:f',NS)
                    formula_count+=formula is not None
                    col=re.sub(r'\d+$','',c.get('r'))
                    cells[col]={'address':c.get('r'),'cell_type':typ,'value':value,
                                'formula':formula.text if formula is not None else None,
                                'style_index':c.get('s')}
                cells_by_row[int(row.get('r'))]=cells
            header_row=next(i for i,cells in cells_by_row.items() if cells.get('A',{}).get('value')=='镜号')
            headers={col:cells_by_row[header_row][col]['value'] for col in COLS}
            # Resolve drawing anchors back to the actual worksheet row and B column.
            srp=posixpath.dirname(sheet_path)+'/_rels/'+posixpath.basename(sheet_path)+'.rels'
            sheet_rels={r.get('Id'):r.get('Target') for r in ET.fromstring(z.read(srp))}
            draw_rid=xml.find('m:drawing',NS).get('{'+NS['r']+'}id')
            draw_target=sheet_rels[draw_rid]
            draw_path=draw_target.lstrip('/') if draw_target.startswith('/') else posixpath.normpath(posixpath.dirname(sheet_path)+'/'+draw_target)
            drp=posixpath.dirname(draw_path)+'/_rels/'+posixpath.basename(draw_path)+'.rels'
            draw_rels={r.get('Id'):r.get('Target') for r in ET.fromstring(z.read(drp))}
            anchors=collections.defaultdict(list)
            for anchor in ET.fromstring(z.read(draw_path)):
                origin=anchor.find('d:from',NS)
                if origin is None:continue
                rr=int(origin.find('d:row',NS).text)+1;cc=int(origin.find('d:col',NS).text)
                blip=anchor.find('.//a:blip',NS)
                image_rid=blip.get('{'+NS['r']+'}embed')
                image_target=draw_rels[image_rid]
                image_path=image_target.lstrip('/') if image_target.startswith('/') else posixpath.normpath(posixpath.dirname(draw_path)+'/'+image_target)
                data=z.read(image_path)
                anchors[rr].append({'cell':chr(65+cc)+str(rr),'drawing_path':draw_path,
                    'relationship_id':image_rid,'embedded_archive_path':image_path,
                    'sha256':sha(data),'bytes':len(data),'dimensions':jpeg_dimensions(data),'anchor_column_zero_based':cc})
            sheet_metadata.append({'name':sheet.get('name'),'path':sheet_path,
                'dimension':xml.find('m:dimension',NS).get('ref'),
                'xml_sha256':sha(z.read(sheet_path)),'source_rows':len(rows),
                'header_row':header_row,'formula_count':formula_count,
                'merged_cells':[x.get('ref') for x in xml.findall('m:mergeCells/m:mergeCell',NS)],
                'preamble_rows':[{'row':i,'cells':cells} for i,cells in cells_by_row.items() if i<header_row]})
            for rownum,cells in cells_by_row.items():
                if rownum<=header_row:continue
                label=cells.get('A',{}).get('value','')
                if not re.fullmatch(r'\d+',label):
                    issues.append({'type':'unparsed_non_shot_row','row':rownum,'cells':cells});continue
                number=int(label)
                values={col:cells.get(col,{}).get('value','') for col in COLS}
                tc=values['C']
                match=re.fullmatch(r'(\d+):(\d+(?:\.\d+)?)\s*-\s*(\d+):(\d+(?:\.\d+)?)\s*\n\(([\d.]+)s\)',tc)
                assert match,(number,tc)
                start,end,listed=secs(match[1],match[2]),secs(match[3],match[4]),Decimal(match[5])
                row_issues=[]
                if end-start!=listed:row_issues.append({'type':'TC_duration_conflicts_listed_seconds','calculated':str(end-start),'listed':str(listed)})
                candidates=image_index[number]
                if len(candidates)!=1:row_issues.append({'type':'screenshot_count_not_one','count':len(candidates)})
                screenshot=None
                if len(candidates)==1:
                    p,filename_start=candidates[0];screenshot={'path':str(p),'filename':p.name,'sha256':hashfile(p),
                        'dimensions':jpeg_dimensions(p.read_bytes()),
                        'bytes':p.stat().st_size,'filename_start_seconds':float(filename_start),
                        'matches_XLSX_TC_start':filename_start==start,
                        'timecode_list_entry':timecode_entries.get(number)}
                    if filename_start!=start:row_issues.append({'type':'screenshot_TC_mismatch'})
                    if timecode_entries.get(number,{}).get('filename')!=p.name:row_issues.append({'type':'timecode_list_filename_mismatch'})
                embedded=anchors.get(rownum,[])
                if len(embedded)!=1:row_issues.append({'type':'embedded_image_anchor_count_not_one','count':len(embedded)})
                if screenshot and len(embedded)==1:
                    screenshot['byte_identical_to_XLSX_embedded_image']=screenshot['sha256']==embedded[0]['sha256']
                    screenshot['embedded_image_half_dimensions']=(screenshot['dimensions']['width']==2*embedded[0]['dimensions']['width'] and screenshot['dimensions']['height']==2*embedded[0]['dimensions']['height'])
                    screenshot['image_provenance_note']='External screenshots are 720x1280; workbook copies are 360x640 downscaled/recompressed JPEGs, so byte hashes differ. Byte difference is not a shot-number/TC mismatch or proof of different visual content.' if not screenshot['byte_identical_to_XLSX_embedded_image'] else 'Byte-identical image copies.'
                role_candidates=role_mentions(values['E'])
                visible_text=values['E']+'\n'+values['G']
                props=[{'id':key,'kind':kind,'matched_terms':[w for w in words if w in visible_text],
                        'status':'source-visible-description candidate; separate asset binding pending'}
                       for key,(kind,words) in PROP_RULES.items() if any(w in visible_text for w in words)]
                quoted=[]
                for qm in re.finditer(r'"([^"\n]*)"|“([^”\n]*)”',values['F']):
                    qt=qm.group(1) if qm.group(1) is not None else qm.group(2)
                    quoted.append({'text':qt,'span_in_source_performance':[qm.start(),qm.end()],
                        'prefix_context':values['F'][max(0,qm.start()-32):qm.start()],
                        'contains_english_letters':bool(re.search('[A-Za-z]',qt)),
                        'speaker_and_VO_ownership':'not automatically inferred from on-screen character; preserve source label and verify correspondence'})
                shots.append({'episode':1,'source_shot':number,'source_shot_label':label,
                    'source_sheet':sheet.get('name'),'source_excel_row':rownum,
                    'source_cells':cells,'source_fields':{headers[col]:values[col] for col in COLS},
                    'source_fields_by_column':values,
                    'timecode':{'raw':tc,'start_seconds':float(start),'end_seconds':float(end),
                        'duration_seconds':float(listed),'start_seconds_exact':str(start),
                        'end_seconds_exact':str(end),'duration_seconds_exact':str(listed),
                        'TC_duration_equals_listed':end-start==listed},
                    'screenshot':screenshot,'embedded_images':embedded,
                    'reference_requirements':{
                        'role_candidates':role_candidates,
                        'visibility_status':'provisional source mentions only; foreground/offscreen ownership must be checked on contact sheet before final asset references',
                        'role_source_text':values['E'],
                        'scene_category':scene_category(values['D']),
                        'scene_literal':values['D'].split('。')[0],
                        'scene_source_text':values['D'],'prop_candidates':props,
                        'bound_asset_names':None,'platform_binding_verified':False},
                    'quoted_source_audio_spans':quoted,
                    'v3_source_mapping':{'时长':'C','环境氛围':'D','景别':'H',
                        '拍摄角度':['J','I'],'摄像机运动':'K','人物角色和运动':'E',
                        '人物表演':'F','画面内容':['G','I']},
                    'source_correspondence_issues':row_issues,
                    'contact_sheet_visual_verification_status':'pending_parent_contact_sheets',
                    'final_group_name':None,'female_prompt':None,'gender_swapped_prompt':None})
    assert [s['source_shot'] for s in shots]==list(range(1,123))
    for prev,current in zip(shots,shots[1:]):
        a=prev['timecode']['end_seconds_exact'];b=current['timecode']['start_seconds_exact']
        if Decimal(a)!=Decimal(b):issues.append({'type':'non_contiguous_TC','after':prev['source_shot'],'before':current['source_shot'],'end':a,'start':b})
    for shot in shots:
        issues.extend(dict(issue,source_shot=shot['source_shot'],excel_row=shot['source_excel_row']) for issue in shot['source_correspondence_issues'])
    allroles=collections.defaultdict(list);allscenes=collections.defaultdict(list);allprops=collections.defaultdict(list)
    for s in shots:
        for role in s['reference_requirements']['role_candidates']:allroles[role].append(s['source_shot'])
        allscenes[s['reference_requirements']['scene_category']].append(s['source_shot'])
        for prop in s['reference_requirements']['prop_candidates']:allprops[prop['id']].append(s['source_shot'])
    role_requirements=[
        {'id':'source_boss_young','source_state':'13岁黑发少年，浅灰白黑滚边睡衣，失眠；源1–3、11–14。','female_version_identity':'Matteo Bellandi少年期；实际资产待确认','gender_swapped_identity':'Vittoria Blackwood少年期；实际资产待确认'},
        {'id':'source_narrator_young','source_state':'13岁瘦弱女孩，浅棕微卷长发，米白宽松睡袍/旧鞋；源4–14。','female_version_identity':'大码女主幼年版本：年龄与体型的明确资产覆盖待根线程确认','gender_swapped_identity':'大码男主幼年版本：年龄与体型的明确资产覆盖待根线程确认'},
        {'id':'source_boss_adult','source_state':'成年男教父；主卧黑色丝绸金边睡袍；豪车黑西装/酒红敞领衬衫；酒店酒红衬衫/黑裤，腕表和纹身。','female_version_identity':'Matteo Bellandi；按源场景服装状态对应资产待确认','gender_swapped_identity':'Vittoria Blackwood；性别服装适配资产待确认'},
        {'id':'source_narrator_adult','source_state':'成年纤细女性抱枕；主卧米白棉睡衣；会客厅/酒店彼得潘领衬衫+米色开衫+浅米百褶短裙/平底鞋。','female_version_identity':'大码女主全镜体型/身份稳定；服装按源镜状态对应资产待确认','gender_swapped_identity':'大码男主全镜体型/身份稳定；性别服装适配资产待确认'},
        {'id':'source_boss_mother','source_state':'男主母亲/教父夫人，深棕盘发、黑色修身西装套裙、耳坠戒指，手持茶杯茶托。','female_version_identity':'Matteo的母亲，姓名与资产待确认；不能从技能示例硬编码Serafina','gender_swapped_identity':'Madam Blackwood，实际素材名称待确认'},
        {'id':'source_lover_blonde','source_state':'金发波浪长发女性，白色丝绸抹胸裙；源15及42起酒店情人。是否同一资产须联系表确认。','female_version_identity':'酒店情人对应Alessia Varenna；蒙太奇同一身份与否待视觉核验','gender_swapped_identity':'Vittoria的男性情人，名字/外观资产待确认'},
        {'id':'source_lover_redhair','source_state':'源16/20红发女伴，香槟色吊带丝绸睡裙/睡袍；须与金发女伴区分。','female_version_identity':'红发情人，姓名与资产待确认','gender_swapped_identity':'独立男性情人状态，姓名与资产待确认'},
        {'id':'source_adult_escort_hand','source_state':'源4成年送行者/管家候选手，深色西装袖口；只见手，身份不确定。','female_version_identity':'手部/服装参考待确认','gender_swapped_identity':'手部/服装参考待确认'},
    ]
    for r in role_requirements:r['source_mention_shots']=allroles.get(r['id'],[])
    conflicts=[
        {'id':'body_shape_override','kind':'source_vs_user_adaptation','shots':[4,5,6,7,8,9,10,12,13,14,21,22,23,24,25,28,96],
         'detail':'源表写13岁瘦弱女孩、纤细手/腰，且成年人物为纤细体型；本轮女版大码女主与性转大码男主须稳定。保留源文，不自行把大码锁改回瘦弱；幼年与成年具体资产覆盖由根线程确认。'},
        {'id':'legacy_names','kind':'identity_mapping','shots':[s['source_shot'] for s in shots if 'Dante' in s['source_fields_by_column']['F'] or 'DeLuca' in s['source_fields_by_column']['F']],
         'detail':'Dante DeLuca/DeLuca Family是对标源名，不得作为当前两版最终名；分别对应Matteo Bellandi/Bellandi与Vittoria Blackwood/Blackwoods，参考素材名待根线程确认。'},
        {'id':'ambiguous_hand_owner','kind':'source_ambiguity','shots':[27,28],
         'detail':'27明确写“女主或教父夫人的手”，28只写左手翻合同；不能仅凭文本锁定手部人物，等待联系表核验。'},
        {'id':'tattoo_state_variation','kind':'source_continuity_review','shots':[15,16,19,48,56,60,62,63,64,71,80,90,96,100,107,111,112],
         'detail':'源纹身描述出现黑玫瑰、十字架、胸部对称图腾、手腕纹身。可能为多个既存纹身/不同角度，也可能文本不一致；保留原文，不自动统一或新增纹身，联系表和资产需确认。'},
        {'id':'check_count_and_handedness','kind':'source_continuity_review','shots':[65,66,67,68,69,70,74,75,76,77,78,90,91,92],
         'detail':'65–68签/撕/递支票，69–78显式两张；90–91右手摩挲/举票、92左手捏票。不得静默改为一张或统一换手，按截图核验再标继承关系。'},
        {'id':'VO_vs_dialogue_ownership','kind':'source_audio_label_ambiguity','shots':[37,38,39,53,54,55,56,58,62,63,80,81,82],
         'detail':'37同时含VO和No.；38/39标“台词/旁白”且画面为母亲反应；部分对白跨多个源镜片段、反应镜中声音可能来自画外。保留所有原引用，不把VO或被提到的人名自动绑定为口型说话者。'},
        {'id':'female_EP1_auxiliary_scope_difference','kind':'auxiliary_script_difference','shots':[4,5,6,7,8,9,10,11,12,13,14,30,31,32]+list(range(98,123)),
         'detail':'现女版EP1无送入庄园幼年明说、豪车追逐三天戏，且正文在抱腰埋颈结束；对标源98–122仍含衣领唇印、抱上床、换地点去住处等。按本轮源122镜保留，不用旧英文稿删镜或借后集填覆盖。'},
        {'id':'male_auxiliary_visible_mark_difference','kind':'auxiliary_script_difference','shots':[99,100,109,110,112],
         'detail':'源是酒红衬衫后衣领唇印和“lipstick on your shirt”，性转男版辅助稿是neck hickey/mark并wash scent。保留源机位和可见标记，台词只对可对应源镜者适配，差异不静默替换。'},
        {'id':'female_auxiliary_costume_dialogue_difference','kind':'auxiliary_script_difference','shots':[37,38,50,53,54,56,58,71,80,81,82],
         'detail':'旧女版为大码女主oversized black tee、情人silk robe，且多段对白与源英文措辞不同；源会客厅/酒店为米白衬衫开衫短裙及金发白抹胸裙。源镜动作/服装状态为最高基准，既有资产如何覆盖由根线程确认，不直接搬旧稿对白。'},
        {'id':'grouping_remainder','kind':'grouping_pending_user_choice','shots':[121,122],
         'detail':'122=24×5+2。最终组/文件命名由根线程等用户口径，本阶段仅episode/source_shot，不固定末组。'},
    ]
    duration=sum(Decimal(s['timecode']['duration_seconds_exact']) for s in shots)
    report={'schema_version':1,'episode':1,'stage':'source_extraction_and_reference_requirements',
        'status':'parsed_complete_pending_visual_contact_sheet_and_actual_asset_mapping',
        'source_priority':'Current user: XLSX plus its screenshots are highest for every shot, visual camera/composition/action/order/time; auxiliary English cannot add/remove/reorder shots.',
        'source_workbook':{'path':str(WORKBOOK),'sha256':initial_workbook_sha,'zip_crc_test_passed':True,
            'parser':'Python standard-library zipfile and ElementTree; no workbook rewriting/recalculation',
            'sheets':sheet_metadata,'headers_by_column':headers},
        'source_screenshot_directory':str(IMAGES),
        'source_timecode_list':{'path':str(TIMECODES),'sha256':hashfile(TIMECODES),'entry_count':len(timecode_entries)},
        'auxiliary_english_sources':scripts,
        'summary':{'source_shots':len(shots),'source_excel_shot_rows':[4,125],
            'unique_shot_numbers':len(set(s['source_shot'] for s in shots)),
            'external_screenshots':len(image_files),'embedded_image_anchors':sum(len(s['embedded_images']) for s in shots),
            'embedded_external_images_byte_identical':sum(s['screenshot'].get('byte_identical_to_XLSX_embedded_image',False) for s in shots),
            'embedded_images_half_external_dimensions':sum(s['screenshot'].get('embedded_image_half_dimensions',False) for s in shots),
            'TC_start_seconds':shots[0]['timecode']['start_seconds'],
            'TC_end_seconds':shots[-1]['timecode']['end_seconds'],
            'sum_durations_seconds':float(duration),'minimum_shot_seconds':min(s['timecode']['duration_seconds'] for s in shots),
            'maximum_shot_seconds':max(s['timecode']['duration_seconds'] for s in shots),
            'source_shots_under_one_second':sum(s['timecode']['duration_seconds']<1 for s in shots),
            'structural_or_image_correspondence_issue_count':len(issues),
            'visual_contact_sheet_shots_verified':0,'assets_bound':0,'final_prompts_prepared':0},
        'requirements_inventory':{'character_states':role_requirements,
            'scene_candidates':[{'id':key,'shots':value,'literal_source_labels':sorted(set(s['reference_requirements']['scene_literal'] for s in shots if s['reference_requirements']['scene_category']==key)),'actual_asset_name':None} for key,value in allscenes.items()],
            'prop_candidates':[{'id':key,'kind':PROP_RULES[key][0],'shots':value,'actual_asset_name':None} for key,value in allprops.items()],
            'policy':'Candidate requirements extracted from source wording, not verified visibility or platform binding. Scene-integral furniture/body states need not be separate @ assets. Exact names arrive from root/Feishu later.'},
        'structural_issues':issues,'source_and_adaptation_review_items':conflicts,
        'grouping_status':'deferred; source shots remain individually addressable by episode/source_shot',
        'shots':shots,
        'sources_unchanged_after_parse':True}
    assert hashfile(WORKBOOK)==initial_workbook_sha
    for shot in shots:assert hashfile(Path(shot['screenshot']['path']))==shot['screenshot']['sha256']
    for value in scripts.values():assert hashfile(Path(value['path']))==value['sha256']
    output=HERE/'source_shots.json'
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(output),'sha256':hashfile(output),'summary':report['summary'],
        'structural_issues':issues,'role_candidate_counts':{k:len(v) for k,v in allroles.items()},
        'scene_counts':{k:len(v) for k,v in allscenes.items()}},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
