import json,re,hashlib
from pathlib import Path
from datetime import datetime
P=Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕');B=P/'提示词3.0_逐镜复刻_前3集';O=B/'复核20261018'
p=O/'独立重分组核验.json';report=json.loads(p.read_text());fix=json.loads((O/'资产衣装校正.json').read_text());manifest=json.loads((B/'全部提示词工程清单.json').read_text());current={};all_groups={}
for ep in range(1,4):
 for version in ['女版','性转男版']:
  gpath=B/f'EP{ep:02}'/version/'groups.json';d=json.loads(gpath.read_text());current[ep,version]=d
  for g in d['groups']:all_groups[g['card_name']]=g
rows=[];bad=[]
for card in fix['changed_cards']:
 g=all_groups[card];header=g['prompt'].split('Shot01:',1)[0];mg=next(x for x in manifest['cards']if x['card_name']==card);old_rec=next(x for x in report['header_asset_and_scope_checks']if x['card_name']==card)
 new_phrase=fix['after']in header;old_phrase=fix['before']in g['prompt'];txt_same=Path(g['prompt_path']).read_text()==g['prompt'];manifest_same=mg['prompt']==g['prompt']
 r={'card_name':card,'correct_asset_name_still_used':'Vittoria_成年_日常'in g['asset_names'],'new_wardrobe_phrase_in_header':new_phrase,'old_wardrobe_phrase_absent':not old_phrase,'txt_matches_groups':txt_same,'global_manifest_matches_groups':manifest_same,'prior_header_asset_sets_and_scopes_passed':old_rec['passed']}
 r['passed']=all(v for k,v in r.items()if isinstance(v,bool))
 if not r['passed']:bad.append(r)
 rows.append(r)
# 本轮仅校正header；检查全部当前提示词已无旧衣装词，未重做上一轮完整结构检验。
remaining=[g['card_name']for g in all_groups.values()if fix['before']in g['prompt']]
clarify=json.loads((O/'跨镜引用号澄清.json').read_text());crosschecks=[]
for x in clarify:
 ds=current[x['episode'],x['version']];candidates=[s for g in ds['groups']for s in g['shots']if s['original_source_shot']==x['source']];matches=[s for s in candidates if s['fields'][x['field']]==x['after']]
 refs=[int(n)for n in re.findall(r'原表镜\s*(\d+)',x['after'])];available={s['original_source_shot']for g in ds['groups']for s in g['shots']}
 good=bool(matches)and all(n in available for n in refs)
 c={'episode':x['episode'],'version':x['version'],'original_source_shot':x['source'],'field':x['field'],'after_text_exactly_present':bool(matches),'new_full_ids':[s['full_id']for s in matches],'target_original_numbers':refs,'targets_resolve':all(n in available for n in refs),'passed':good}
 crosschecks.append(c)
 if not good:bad.append(c)
report['structure_passed']=report['passed'];report['wardrobe_correction_recheck']={'at':datetime.now().astimezone().isoformat(),'initial_finding':'Vittoria_成年_日常在EP01男版header误写黑衬衫；实际参考为西装外套+V领排扣马甲+长裤。','asset_file':fix['asset_file'],'asset_sha256_verified':hashlib.sha256(Path(fix['asset_file']).read_bytes()).hexdigest()==fix['asset_sha256'],'observed_by_this_agent':True,'fixed_card_count':len(rows),'fixed_groups':[6,7]+list(range(9,26)),'records':rows,'old_phrase_remaining_cards':remaining,'passed':not bad and not remaining}
report['source_reference_clarification_recheck']={'changed_fields':len(clarify),'records':crosschecks,'passed':all(x['passed']for x in crosschecks)}
report['passed']=report['structure_passed'] and report['wardrobe_correction_recheck']['passed'] and report['source_reference_clarification_recheck']['passed']
report['summary']['wardrobe_corrected_headers_rechecked']=len(rows);report['summary']['clarified_cross_reference_fields_exactly_checked']=len(clarify)
report['issues']=bad
report['summary']['issues_count']=len(bad)
report['rechecked_at']=datetime.now().astimezone().isoformat()
report['input_group_sha256_after_header_correction']={str(B/f'EP{e:02}'/v/'groups.json'):hashlib.sha256((B/f'EP{e:02}'/v/'groups.json').read_bytes()).hexdigest()for e,v in current}
p.write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'passed':report['passed'],'corrected_headers':len(rows),'source_reference_fields':len(clarify),'issues':bad,'remaining_old_phrase':remaining},ensure_ascii=False,indent=2))
