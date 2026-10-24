"""Read local sources/prompts and build the draft project manifest. No platform calls.

Usage: python3 audit_prompt_project.py [--root PATH] [--build]
Without --build, prints a fresh audit only; --build writes the two root JSON outputs.
Original XLS, images, episode source JSON, groups JSON and TXT are never changed.
"""
import argparse
import hashlib
import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from xml.etree import ElementTree as ET

FIELDS = ['时长', '环境氛围', '景别', '拍摄角度', '摄像机运动', '人物角色和运动', '人物表演', '画面内容']
EXPECTED = {1:122, 2:57, 3:56}
PREFIX = {'女版':'大码女版', '性转男版':'性转版男版'}
NS = {'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def digest(path):
 return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def tc_seconds(value):
 parts=value.split(':')
 return sum(Decimal(x)*Decimal(60)**i for i,x in enumerate(reversed(parts)))

def xlsx_shots(path):
 """Independently read source numeric shot rows and TC from the original workbook."""
 with zipfile.ZipFile(path) as z:
  strings=[''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml'))] if 'xl/sharedStrings.xml' in z.namelist() else []
  out=[]
  for part in sorted(n for n in z.namelist() if re.fullmatch(r'xl/worksheets/sheet\d+\.xml',n)):
   for row in ET.fromstring(z.read(part)).findall('.//m:sheetData/m:row',NS):
    cells={}
    for c in row:
     col=re.sub(r'\d+','',c.get('r',''))
     if c.get('t')=='inlineStr': value=''.join(c.find('m:is',NS).itertext())
     else:
      e=c.find('m:v',NS); value=e.text if e is not None else ''
      if c.get('t')=='s':value=strings[int(value)]
     cells[col]=value
    if not re.fullmatch(r'\d+',cells.get('A','').strip()):continue
    shot=int(cells['A']); tc=cells.get('C','')
    match=re.search(r'(\d+:\d+(?:\.\d+)?)\s*-\s*(\d+:\d+(?:\.\d+)?)',tc)
    if not match:continue
    start,end=map(tc_seconds,match.groups());duration=end-start
    listed=re.search(r'\(([0-9.]+)\s*s\)',tc)
    assert duration>0 and (not listed or duration==Decimal(listed[1])),('source duration',path,shot)
    out.append({'source_shot':shot,'source_row':int(row.get('r')),'source_tc':tc,'start':start,'end':end,'duration':duration})
 return out

def field_blocks(prompt):
 blocks=re.findall(r'^Shot(\d+(?:-\d+-\d+)?)\s*:\s*\n(.*?)(?=\n\s*Shot\d+(?:-\d+-\d+)?\s*:|\n\s*出场角色：|\Z)',prompt,re.M|re.S)
 results=[]
 for num,body in blocks:
  keys=re.findall(r'^(时长|环境氛围|景别|拍摄角度|摄像机运动|人物角色和运动|人物表演|画面内容)：',body,re.M)
  assert keys==FIELDS,('eight field order',num,keys)
  duration=re.search(r'^时长：([0-9.]+)\s*秒',body,re.M)
  assert duration,('missing duration',num)
  results.append((num,Decimal(duration[1])))
 return results

def run(root):
 recorded_inputs={}; errors=[]; warnings=[]; all_cards=[]; episode_summary=[]; used_names=set()
 def read_json(path):
  recorded_inputs[str(path)]=digest(path)
  return json.loads(path.read_text())
 assets_path=root/'平台工作/飞书资产下载清单.json'
 asset_doc=read_json(assets_path); asset_lookup={x['local_asset_name']:x for x in asset_doc['assets']}
 assert len(asset_lookup)==len(asset_doc['assets']),'duplicate downloaded asset names'
 for ep,count in EXPECTED.items():
  source_path=root/f'EP{ep:02d}/source_shots.json'; source=read_json(source_path)
  workbook=source.get('source_workbook',source.get('source_xlsx')); wb_path=Path(workbook['path'])
  assert digest(wb_path)==workbook['sha256'],('source workbook hash',ep)
  recorded_inputs[str(wb_path)]=workbook['sha256']
  truth=xlsx_shots(wb_path); assert [t['source_shot'] for t in truth]==list(range(1,count+1)),('XLS source count/order',ep)
  assert [s['source_shot'] for s in source['shots']]==list(range(1,count+1)),('source JSON count/order',ep)
  assert truth[0]['start']==0 and all(a['end']==b['start'] for a,b in zip(truth,truth[1:])),('source TC gap/overlap',ep)
  source_total=sum((t['duration'] for t in truth),Decimal(0));source_by_num={t['source_shot']:t for t in truth}
  for version,prefix in PREFIX.items():
   group_path=root/f'EP{ep:02d}'/version/'groups.json'
   if group_path.exists(): groups_doc=read_json(group_path);groups=groups_doc['groups']
   else:
    alternate=root/f'EP{ep:02d}/groups.json'
    if not alternate.exists():raise FileNotFoundError(str(group_path))
    groups_doc=read_json(alternate)
    if 'versions' in groups_doc:groups=next(x['groups'] for x in groups_doc['versions'] if x['version']==version)
    else:groups=[g for g in groups_doc['groups'] if g['version']==version]
    group_path=alternate
   assert len(groups)==(count+4)//5,('group count',ep,version,len(groups))
   nums=[];version_duration=Decimal(0)
   for ordinal,g in enumerate(groups,1):
    expected=list(range((ordinal-1)*5+1,min(ordinal*5,count)+1))
    assert g['source_shots']==expected,('source shot group/order',ep,version,ordinal)
    nums+=expected;card_name=f'{prefix}{ep:02d}-{ordinal:02d}-01'
    path=Path(g.get('prompt_path',g.get('prompt_file','')))
    assert path.is_file(),('missing prompt file',path)
    prompt=path.read_text();recorded_inputs[str(path)]=digest(path)
    assert prompt==g['prompt'],('TXT/JSON mismatch',path)
    assert len(prompt)<=5000,('card >5000chars',card_name,len(prompt))
    blocks=field_blocks(prompt)
    original_labels=[label for label,d in blocks]
    assert original_labels in ([f'{n:02d}' for n in expected],g.get('shot_ids',[])),('prompt source/alias labels order',card_name,original_labels)
    for n,(label,duration) in zip(expected,blocks):assert duration==source_by_num[n]['duration'],('prompt duration differs from XLS',card_name,n)
    time_lines=re.findall(r'^时长：[^\n]+',prompt,re.M)
    assert len(time_lines)==len(expected),('duration field count',card_name)
    for local_i,line in enumerate(time_lines,1):
     assert f'{prefix}{ep:02d}-{ordinal:02d}-{local_i:02d}' in line,('full shot ID missing from duration field',card_name,local_i)
    total=sum((d for n,d in blocks),Decimal(0)); assert Decimal(str(g['total_duration']))==total,('group duration differs',card_name)
    version_duration+=total
    named=set(g['asset_names']); assert not(named-set(asset_lookup)),('unknown asset name',card_name,sorted(named-set(asset_lookup)))
    text_refs=set(re.findall(r'@([^\s；;，,。）：)（(、\n]+)',prompt))
    assert not(text_refs-set(asset_lookup)),('unknown inline @reference',card_name,sorted(text_refs-set(asset_lookup)))
    assert not(text_refs-named),('inline @asset absent from group asset_names',card_name,sorted(text_refs-named))
    used_names|=named
    originals=g.get('shots',[]);shot_lookup={s['source_shot']:s for s in originals}
    assert sorted(shot_lookup)==expected,('shot detail coverage',card_name)
    aliases=g.get('shot_ids',[]);assert len(aliases)==len(expected) and len(set(aliases))==len(expected),('shot alias mapping',card_name)
    # Historical source slots remain as traceability aliases after selection; they are
    # not unresolved merely because the key still exists. Audit the current text/status.
    pending=bool(re.search(r'【(?:对白|台词|原句)[^】]*(?:槽|待)|原句待回填|DIALOGUE_PENDING',prompt,re.I)) or ('pending' in g.get('status','').lower() and bool(g.get('dialogue_slot_ids') or any(shot_lookup[n].get('dialogue_slot') for n in expected)))
    reference_pending=g.get('reference_pending',[])
    if reference_pending:warnings.append({'card_name':card_name,'type':'reference_not_yet_assigned','source_names_or_notes':reference_pending})
    card_shots=[]
    for i,n in enumerate(expected):
     s=shot_lookup[n];t=source_by_num[n]
     full_id=f'{prefix}{ep:02d}-{ordinal:02d}-{i+1:02d}'
     card_shots.append({'source_shot':n,'source_shot_label':f'Shot{n:02d}','prompt_label_original':f'Shot{original_labels[i]}','full_id':full_id,'card_source_shot_uid':f'{card_name}-Shot{n:02d}',
       'source_shot_id_alias':aliases[i],'source_excel_row':t['source_row'],'source_timecode':t['source_tc'],
       'duration_seconds':float(t['duration']),'dialogue_slot':s.get('dialogue_slot'),'dialogue_slot_ids':s.get('dialogue_slot_ids',[]),
       'unresolved_reference_notes':s.get('unresolved_reference_notes',[])})
    all_cards.append({'card_name':card_name,'platform_card_name_planned':card_name,'episode':ep,'version':version,'platform_version_prefix':prefix,
      'group_index':ordinal,'source_group_id_alias':g.get('group_id'),'source_shots':expected,'shot_ids':aliases,'shots':card_shots,
      'source_groups_json':str(group_path),'source_groups_json_sha256':recorded_inputs[str(group_path)],
      'prompt_path':str(path),'prompt_sha256':recorded_inputs[str(path)],'prompt':prompt,'character_count':len(prompt),
      'asset_names':sorted(named),'reference_pending':reference_pending,'dialogue_slot_ids':g.get('dialogue_slot_ids',[]),
      'source_dialogue_catalog':[slot for slot in groups_doc.get('dialogue_slots',[]) if slot.get('slot_id') in g.get('dialogue_slot_ids',[])],
      'total_duration':float(total),'stage':'dialogue_pending' if pending else 'visual_draft',
      'visual_stage':'visual_draft','actual_platform_reference_binding':False,'generation_submitted':False})
   assert nums==list(range(1,count+1)),('missing/duplicate/reversed source shots',ep,version)
   assert version_duration==source_total,('episode total duration',ep,version)
   episode_summary.append({'episode':ep,'version':version,'source_shots':count,'groups':len(groups),'last_group_shots':groups[-1]['source_shots'],'duration_seconds':float(source_total)})
 verified_assets=[]
 for name in sorted(used_names):
  a=asset_lookup[name];path=Path(a['local_path']);assert path.is_file(),('missing asset file',name)
  actual=digest(path);assert actual==a['sha256'],('asset SHA mismatch',name)
  verified_assets.append({'asset_name':name,'local_path':str(path),'sha256':actual,'bytes':path.stat().st_size,'nodeId':a.get('nodeId'),'download_manifest_index':a.get('index'),'verification':'local_file_exists_sha256_matches_download_manifest','actual_platform_reference_binding':False})
 assert len(all_cards)==98 and sum(len(c['source_shots']) for c in all_cards)==470,'project cardinalities'
 assert len({c['card_name'] for c in all_cards})==98,'duplicate card names'
 full_ids=[s['full_id'] for c in all_cards for s in c['shots']];assert len(set(full_ids))==470,'duplicate full shot IDs'
 # Refuse a mixed snapshot if another episode writer changed a file during this audit.
 changed=[p for p,h in recorded_inputs.items() if digest(p)!=h]
 assert not changed,('source changed during audit; rerun after writer finishes',changed)
 now=datetime.now(timezone.utc).isoformat();pending=[c['card_name'] for c in all_cards if c['stage']=='dialogue_pending']
 report={'schema_version':1,'checked_at_utc':now,'audit_status':'passed_local_draft_checks','stage':'dialogue_pending' if pending else 'visual_draft',
  'episodes':episode_summary,'cards_per_version':49,'cards_total':98,'source_shots_per_version':235,'shot_occurrences_total':470,
  'duration_per_version_seconds':float(sum((Decimal(str(x['duration_seconds'])) for x in episode_summary if x['version']=='女版'),Decimal(0))),
  'max_card_characters':max(c['character_count'] for c in all_cards),'used_assets_verified':len(verified_assets),
  'source_xlsx_read_fresh':True,'complete_source_order_no_duplicates_or_omissions':True,'eight_fields_in_order_all_shots':True,
  'all_cards_at_most5000_characters':True,'durations_match_original_xlsx':True,'no_unknown_asset_or_gender_swapped_scene_names':True,
  'card_names_match_user_latest_episode_group_local_shot_choice':True,'every_full_shot_id_present_in_duration_field':True,'pending_dialogue_cards':pending,'generation_ready':False,
  'platform_bound':False,'generation_submitted':False,'limitations':['Local prompt/asset-file audit only; platform true @binding and generation have not been performed.','Unassigned extra source-character references remain explicit warnings; original-dialogue source has been confirmed by the user.','Static contact-sheet evidence does not verify a generated motion clip or exact spoken duration.'],
  'inputs':recorded_inputs,'errors':errors,'warnings':warnings}
 dialogue_catalogs=[]
 for ep in EXPECTED:
  p=root/f'EP{ep:02d}/dialogue_slots.json'
  if p.is_file():dialogue_catalogs.append({'episode':ep,'path':str(p),'sha256':digest(p),'status':'Source/adaptation traceability catalog; may retain historical candidates. Current selected speech follows the stable episode groups and TXT.'})
 manifest={'schema_version':1,'created_at_utc':now,'project':'我不再做教父的大码人形抱枕','stage':report['stage'],
  'scope':'两版前三集；三份源XLS及截图逐镜复刻；本地视觉正文草稿，未发布未生成。',
  'naming':{'female':'大码女版EE-GG-SS','gender_swapped_male':'性转版男版EE-GG-SS','segments':'episode-group-intragroupShot; user confirmed','card_name':'first shot full ID, SS=01','shot_full_id':'prefix + episode-group-intragroupShot','card_source_shot_uid':'card_name + -Shot + original source shot number, retained for additional provenance','old_group_and_shot_ids':'retained as aliases; no original group JSON or TXT renamed'},
  'summary':{k:report[k] for k in ('episodes','cards_per_version','cards_total','source_shots_per_version','shot_occurrences_total','duration_per_version_seconds','used_assets_verified','max_card_characters')},
  'source_snapshot_inputs':recorded_inputs,'dialogue_catalog_files':dialogue_catalogs,'assets':verified_assets,'cards':all_cards,
  'audit_report_path':str(root/'全部提示词工程核验.json'),'actual_platform_reference_binding':False,'generation_submitted':False}
 return manifest,report

if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parent);ap.add_argument('--build',action='store_true');args=ap.parse_args()
 try:manifest,report=run(args.root.resolve())
 except (AssertionError,KeyError,ValueError,FileNotFoundError,StopIteration) as e:
  print(json.dumps({'audit_status':'not_passed','error':str(e),'outputs_written':False},ensure_ascii=False));sys.exit(2)
 if args.build:
  for name,doc in [('全部提示词工程清单.json',manifest),('全部提示词工程核验.json',report)]:
   target=args.root/name;temp=target.with_suffix('.json.tmp');temp.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n');temp.replace(target)
 print(json.dumps({k:report[k] for k in ('audit_status','stage','cards_total','shot_occurrences_total','used_assets_verified','max_card_characters','generation_ready')},ensure_ascii=False))
