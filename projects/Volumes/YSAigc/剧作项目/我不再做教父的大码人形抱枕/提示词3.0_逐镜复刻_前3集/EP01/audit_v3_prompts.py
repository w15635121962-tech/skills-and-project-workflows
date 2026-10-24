#!/usr/bin/env python3
"""Read inputs and final prompt files, write only an independent local audit."""
from pathlib import Path
from decimal import Decimal
import hashlib
import json
import re
import zipfile
import xml.etree.ElementTree as ET

H=Path(__file__).resolve().parent
R=H.parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=json.loads((H/'source_shots.json').read_text(encoding='utf-8'))
assets=json.loads((R/'平台工作/飞书资产下载清单.json').read_text(encoding='utf-8'))['assets']
assets_by_name={x['local_asset_name']:x for x in assets}
assert sha(source['source_workbook']['path'])==source['source_workbook']['sha256']
with zipfile.ZipFile(source['source_workbook']['path']) as z:
    assert z.testzip() is None
    ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    sheet=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    shared=[]
    if 'xl/sharedStrings.xml' in z.namelist():
        shared=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml'))]
    original={}
    for row in sheet.findall('.//s:sheetData/s:row',ns):
        cells={}
        for c in row.findall('s:c',ns):
            col=re.match(r'[A-Z]+',c.attrib['r']).group()
            value=''.join(t.text or '' for t in c.findall('.//s:t',ns))
            v=c.find('s:v',ns)
            if not value and v is not None:
                value=v.text or ''
                if c.attrib.get('t')=='s':value=shared[int(value)]
            cells[col]=value
        original[int(row.attrib['r'])]=cells
    for s in source['shots']:
        for c,value in s['source_fields_by_column'].items():
            assert value==original[s['source_excel_row']].get(c,''),(s['source_shot'],c)
assert all(sha(s['screenshot']['path'])==s['screenshot']['sha256'] for s in source['shots'])
assert all(sha(s['path'])==s['sha256'] for s in source['auxiliary_english_sources'].values())

report={
    'episode':1,'scope':'Two local V3 prompt versions; no browser or platform generation.',
    'source_priority':'XLSX + source stills control shot count, order, TC, framing and action. Feishu controls identity/costume/space. User selected corresponding project original dialogue.',
    'independent_source_reparse':{'source_workbook_path':source['source_workbook']['path'],
        'sha256':sha(source['source_workbook']['path']), 'all_122_A_to_K_fields_match_source_JSON':True,
        'all_122_screenshot_sha256_unchanged':True,'both_EP01_auxiliary_source_sha256_unchanged':True,
        'source_shots_json_sha256':sha(H/'source_shots.json')},
    'versions':{},
    'visual_reference_limits':[
        'All 122 provided stills reviewed; one still cannot prove full motion, camera trajectory or dialogue timing.',
        'Embedded 360x640 XLSX previews and external720x1280 stills have distinct hashes; this is recorded, not claimed byte-identical.',
        'Feishu cards are only identity/costume/space references; prompt excludes card layouts, labels and collage.',
        'Source27/28 hand owner and source4 escort hand identity are unknown; no added face or invented Vincent assignment.',
        'Source16 red-haired lover has no confirmed assigned card. Source20 back-view hair differs under light and identity is not proven.',
        'Source25 still eyelids and XLSX opened-eyes end state differ; retain source action and note the single-frame limitation.',
        'Source29 mother face is cropped at top; prompt does not force full head into frame.',
        'Source43 begins occluded; full face is not revealed prematurely. Source47 heel remains on carpet, not bed.',
        'Source99/100 lipstick stays on back collar fabric in both versions, not moved onto neck skin.',
        'Source69/70 two checks retained; source90 onward one held. Source91 right-hand/source92 left-hand cut not filled with invented handoff.',
        'All source117–122 white-flash microshots retained separately, not deduplicated.',
    ],
    'explicit_identity_and_costume_substitutions':[
        'Source Dante/DeLuca names are replaced by Matteo Bellandi for female and Vittoria Blackwood for gender-swapped version.',
        'Adult large-bodied protagonist uses assets01/03 and02/04. Thin assets05/06 never referenced.',
        'Childhood uses07/08 and16/17, separate from adults; nonsexual companionship only.',
        'Main female lover uses20 (pink robe); male lover uses19 (black-gold robe). No unsupported source white minidress or long hair is forced onto male card.',
        'Mother uses22 light pink suit dress, not source black suit. Boss daytime uses09/12; bedroom uses11/13.',
        'Source34 exact visible title EMPLOYMENT RENEWAL AGREEMENT differs from71 card heading CONTRACT RENEWAL AGREEMENT; source requested visible title is explicitly retained while card controls document form.',
    ],
    'remaining_material_decisions':[
        {'source_shots':[16,20],'groups':[4],'issue':'Distinct/unidentified montage lovers lack confirmed corresponding reference cards for both versions.',
         'handling':'Explicit reference_pending; no invented @ name or platform binding.'},
        {'source_shots':[110,112],'issue':'Both project versions refer to neck/mark and shower or washing scent; source stills show collar cloth lipstick and source line offers change of clothes.',
         'handling':'Project quotes remain byte-exact, source visuals remain unchanged. Semantic difference recorded for root/user review.'},
    ],
}
expected_fields=['时长','环境氛围','景别','拍摄角度','摄像机运动','人物角色和运动','人物表演','画面内容']
all_ids=[]
used_assets=set()
for version,prefix in [('女版','大码女版'),('性转男版','性转版男版')]:
    path=H/version/'groups.json'
    d=json.loads(path.read_text(encoding='utf-8'))
    groups=d['groups']
    shots=[s for g in groups for s in g['shots']]
    assert len(groups)==25 and [s['source_shot'] for s in shots]==list(range(1,123))
    assert [len(g['shots']) for g in groups]==[5]*24+[2]
    assert sum(Decimal(s['duration_seconds_exact']) for s in shots)==Decimal('142.2')
    for g in groups:
        assert Path(g['prompt_path']).read_text(encoding='utf-8')==g['prompt']
        assert sha(g['prompt_path'])==g['prompt_sha256']
        assert g['card_name']==g['shots'][0]['full_shot_id']
        assert len(g['prompt'])<5000
        assert set(re.findall(r'@([^；）\s。]+)',g['prompt']))<=set(g['asset_names'])
        assert all(name in assets_by_name for name in g['asset_names'])
        used_assets.update(g['asset_names'])
    for s in shots:
        src=source['shots'][s['source_shot']-1]
        assert s['source_fields_verbatim']==src['source_fields_by_column']
        assert s['duration_seconds_exact']==src['timecode']['duration_seconds_exact']
        assert s['fields']['景别']==src['source_fields_by_column']['H']
        assert s['fields']['摄像机运动']==src['source_fields_by_column']['K']
        assert list(s['fields'])==expected_fields
        assert s['fields']['拍摄角度'].startswith(src['source_fields_by_column']['J']+'；')
        assert s['full_shot_id']==prefix+s['shot_id']
        all_ids.append(s['full_shot_id'])
    emitted=[]
    for s in shots:
        emitted+=re.findall(r'“([^”]+)”',s['fields']['人物表演'])
    expected=[t for ev in d['dialogue_events'] for part in ev['parts'] for t in part['texts_verbatim']]
    assert emitted==expected,(version,emitted,expected)
    for ev in d['dialogue_events']:
        assert sha(ev['source_file'])==ev['source_sha256']
        text=Path(ev['source_file']).read_text(encoding='utf-8')
        quotes=re.findall(r'["“]([^"”]+)["”]',text,re.S)
        assert all(unit in quotes for unit in ev['original_quoted_units_verbatim'])
        assert ' '.join(t for p in ev['parts'] for t in p['texts_verbatim'])==' '.join(ev['original_quoted_units_verbatim'])
    report['versions'][version]={
        'groups_json_path':str(path),'groups_json_sha256':sha(path),'groups':25,'shots':122,
        'last_group_shots':2,'duration_seconds':142.2,
        'all_source_fields_unchanged_in_audit':True,'all_TC_order_and_duration_preserved':True,
        'all_H_J_K_source_camera_values_preserved':True,'all_8_fields_ordered':True,
        'all_25_TXT_match_groups_JSON_and_recorded_SHA256':True,'all_122_full_shot_ids_correct':True,
        'maximum_prompt_characters':max(len(g['prompt']) for g in groups),
        'dialogue_events':len(d['dialogue_events']),'dialogue_fragments_emitted':len(emitted),
        'all_quoted_English_exactly_matches_source_and_appears_once':True,
        'project_EP01_dialogue_coverage':d['project_EP01_dialogue_coverage'],
        'same_scene_cross_project_episode_events':[x for x in d['dialogue_events'] if x['source_episode']!=1],
        'timing_risks_not_audio_measured':[{k:x[k] for k in ['event_id','source_shots','english_word_count','support_duration_seconds','words_per_second_for_risk_only','notes']}
            for x in d['dialogue_events'] if x['words_per_second_for_risk_only']>3],
        'reference_pending_groups':[g['group_number'] for g in groups if g['reference_pending']],
        'platform_binding_verified':False,'platform_submission_performed':False,
    }
assert len(all_ids)==len(set(all_ids))==244
assert not {'女主_Eliza_瘦身','男主_性转_瘦身'}&used_assets
for name in used_assets:
    a=assets_by_name[name]
    assert sha(a['local_path'])==a['sha256'],name
report['unique_shot_ids_both_versions']=244
report['referenced_asset_count']=len(used_assets)
report['all_referenced_local_asset_hashes_unchanged']=True
report['referenced_asset_names']=sorted(used_assets)
report['asset_contact_sheets_personally_reviewed']=[
    {'path':str(R/'飞书资产联系表'/f'assets_{suffix}.png'),'sha256':sha(R/'飞书资产联系表'/f'assets_{suffix}.png')}
    for suffix in ['01_04','05_08','09_12','13_16','17_20','21_24','37_40','41_44','45_48','49_52','53_56','69_72','77_80','81_84']]
out=H/'EP01_逐镜复刻与台词适配差异.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'audit_path':str(out),'sha256':sha(out),'all_checks_passed':True,
                  'total_shots':244,'referenced_assets':len(used_assets),'reference_pending_groups_each_version':[4]},ensure_ascii=False,indent=2))
