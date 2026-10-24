import json,re,hashlib,collections
from pathlib import Path
from datetime import datetime
P=Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕');B=P/'提示词3.0_逐镜复刻_前3集';O=B/'复核20261018';backup=O/'修订前备份'
fields_order=['时长','环境氛围','景别','拍摄角度','摄像机运动','人物角色和运动','人物表演','画面内容']
manifest=json.loads((B/'全部提示词工程清单.json').read_text());batches=json.loads((B/'素材上传批次/批次清单.json').read_text())
asset_categories={a:x['category']for x in batches for a in x['asset_names']}
# 车内在飞书归为道具，但实际本项目用作汽车镜头的环境空间。对角色/场景审查按使用语义归类。
asset_categories['车内']='场景'
asset_names_sorted=sorted(asset_categories,key=len,reverse=True)
asset_pattern=re.compile('@('+'|'.join(re.escape(x)for x in asset_names_sorted)+r')(?=[；（）\s，。])')
issues=[]; per_ep=[];headers=[];clothes=[];cross=[];all_ids=[];card_names=[];coverage={};all_groups=[];file_hashes={}

def add(kind,ep,version,group,detail,severity='P1'):
 issues.append({'kind':kind,'episode':ep,'version':version,'group':group,'severity':severity,'detail':detail})
def refs(text):return [m.group(1)for m in asset_pattern.finditer(text)]
def quoted_english(shots):
 out=[]
 for s in shots:
  fs=s['fields'];line=fs['人物表演']
  # 中文双引号中的英文，覆盖已制作的逐字口播；ASCII引号仅在同字段存在时补查。
  for m in re.finditer(r'“([^”]*)”|"([^"\n]*)"',line):
   x=m.group(1) if m.group(1)is not None else m.group(2)
   if re.search('[A-Za-z]',x):out.append(x)
 return out

def logical_role(asset):
 if asset.startswith('大码女主_Eliza_')or asset=='童年女主_Eliza':return 'Eliza'
 if asset.startswith('大码男主_性转_')or asset=='童年男主_性转':return '性转男主'
 if asset.startswith('Matteo_'):return 'Matteo'
 if asset.startswith('Vittoria_'):return 'Vittoria'
 if asset.startswith('Alessia_'):return 'Alessia'
 if asset.startswith('性转男情人_'):return '性转男情人'
 return asset

for ep,nold,nnew in [(1,122,122),(2,57,57),(3,56,57)]:
 for version in ['女版','性转男版']:
  p=B/f'EP{ep:02}'/version/'groups.json';oldp=backup/f'EP{ep:02}'/version/'groups.json';d=json.loads(p.read_text());old=json.loads(oldp.read_text());file_hashes[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
  gs=d['groups'];ss=[s for g in gs for s in g['shots']];olds=[s for g in old['groups'] for s in g['shots']];orig=[s['original_source_shot']for s in ss];newseq=[s['source_shot']for s in ss]
  expected=list(range(1,nold+1));expected_orig=[1,1]+list(range(2,nold+1)) if ep==3 else expected
  if len(ss)!=nnew:add('shot_count',ep,version,None,[len(ss),nnew])
  if newseq!=list(range(1,nnew+1)):add('new_sequence',ep,version,None,newseq)
  if orig!=expected_orig:add('source_mapping',ep,version,None,orig)
  counts=collections.Counter(orig);coverage[f'EP{ep:02}/{version}']={'source_rows':len(counts),'counts':dict(counts)}
  for s in ss:
   no=s['original_source_shot'];want_parts=2 if ep==3 and no==1 else 1
   if s['split_total']!=want_parts:add('split_total',ep,version,None,[s['full_id'],s['split_total']])
   if no not in expected:add('unmapped_original',ep,version,None,no)
   if list(s['fields'])!=fields_order:add('field_order',ep,version,None,[s['full_id'],list(s['fields'])])
   if abs(s['end_seconds']-s['start_seconds']-s['duration_seconds'])>1e-6:add('duration_arithmetic',ep,version,None,s['full_id'])
  if any(abs(ss[i]['start_seconds']-ss[i-1]['end_seconds'])>1e-6 for i in range(1,len(ss))):add('timeline_gaps_overlaps',ep,version,None,[(ss[i-1]['full_id'],ss[i]['full_id'])for i in range(1,len(ss))if abs(ss[i]['start_seconds']-ss[i-1]['end_seconds'])>1e-6])
  old_q=quoted_english(olds);new_q=quoted_english(ss)
  if new_q!=old_q:add('quoted_english_order_changed',ep,version,None,{'old':old_q,'new':new_q})
  expected_sizes=[5]*(nnew//5)+([nnew%5]if nnew%5 else [])
  sizes=[len(g['shots'])for g in gs]
  if sizes!=expected_sizes:add('group_sizes',ep,version,None,{'actual':sizes,'expected':expected_sizes})
  ep_total=sum(s['duration_seconds']for s in ss)
  if abs(ep_total-d['total_duration'])>1e-6:add('episode_duration',ep,version,None,[ep_total,d['total_duration']])
  for gi,g in enumerate(gs,1):
   all_groups.append(g);card_names.append(g['card_name']);shotids=[];assetunion=set(a for s in g['shots']for a in s['asset_names']);prompt=g['prompt'];header=prompt.split('Shot01:',1)[0];firstlines=header.splitlines();roleline=next((x for x in firstlines if x.startswith('出场角色：')),'');sceneline=next((x for x in firstlines if x.startswith('场景：')),'')
   expected_roles={a for a in assetunion if asset_categories.get(a)=='角色'};expected_scenes={a for a in assetunion if asset_categories.get(a)=='场景'};got_roles=set(refs(roleline));got_scenes=set(refs(sceneline));header_refs=set(refs(header));
   if expected_roles!=got_roles:add('header_role_set',ep,version,gi,{'expected':sorted(expected_roles),'actual':sorted(got_roles)})
   if expected_scenes!=got_scenes:add('header_scene_set',ep,version,gi,{'expected':sorted(expected_scenes),'actual':sorted(got_scenes)})
   if assetunion!=set(g['asset_names']):add('group_asset_union',ep,version,gi,{'shot_union':sorted(assetunion),'group_assets':g['asset_names']})
   if not header.startswith('出场角色：')or '以下所有Shot出场的角色和场景统一锁定参考图。'not in header or '画幅：竖屏9:16。'not in header:add('header_contract',ep,version,gi,header)
   unknown=set(a for a in assetunion if a not in asset_categories)
   if unknown:add('unknown_asset_classification',ep,version,gi,sorted(unknown),'P2')
   if 'prompt_path'in g and Path(g['prompt_path']).read_text()!=prompt:add('txt_prompt_mismatch',ep,version,gi,g['prompt_path'])
   if len(prompt)!=g['character_count'] or len(prompt)>5000:add('prompt_length',ep,version,gi,[len(prompt),g['character_count']])
   if abs(sum(s['duration_seconds']for s in g['shots'])-g['total_duration'])>1e-6:add('group_duration',ep,version,gi,g['total_duration'])
   # 按实际header文字读取每张角色参考的适用Shot，不复用builder的解析函数。
   rrefs=list(asset_pattern.finditer(roleline));scope_rows=[]
   for ri,m in enumerate(rrefs):
    asset=m.group(1);segment=roleline[m.end():rrefs[ri+1].start() if ri+1<len(rrefs) else len(roleline)];limit=re.search(r'（仅本组([^）]+)）',segment)
    specified={int(x)for x in re.findall(r'Shot(\d+)',limit.group(1))}if limit else set(range(1,len(g['shots'])+1))
    actual={j for j,s in enumerate(g['shots'],1)if asset in s['asset_names']}
    if specified!=actual:add('role_shot_scope',ep,version,gi,{'asset':asset,'header_scope':sorted(specified),'shot_usage':sorted(actual),'segment':segment})
    scope_rows.append({'asset':asset,'header_scope':sorted(specified),'actual_scope':sorted(actual),'passed':specified==actual})
   byrole=collections.defaultdict(list)
   for a in expected_roles:byrole[logical_role(a)].append(a)
   mixed={k:sorted(a)for k,a in byrole.items()if len(a)>1}
   if mixed:
    clothes.append({'episode':ep,'version':version,'group':gi,'mixed_role_variants':mixed,'all_scopes_correct':all(x['passed']for x in scope_rows),'scopes':scope_rows})
   headers.append({'episode':ep,'version':version,'group':gi,'card_name':g['card_name'],'role_assets_expected':sorted(expected_roles),'role_assets_header':sorted(got_roles),'scene_assets_expected':sorted(expected_scenes),'scene_assets_header':sorted(got_scenes),'role_scopes':scope_rows,'passed':expected_roles==got_roles and expected_scenes==got_scenes and all(x['passed']for x in scope_rows)})
   for si,s in enumerate(g['shots'],1):
    prefix='大码女版'if version=='女版'else'性转版男版';expected_id=f'{prefix}{ep:02}-{gi:02}-{si:02}';all_ids.append(s['full_id']);shotids.append(s['full_id'])
    if s['full_id']!=expected_id or s['shot_id']!=f'{ep:02}-{gi:02}-{si:02}' or s['prompt_label']!=f'Shot{si:02}':add('full_id_sequence',ep,version,gi,{'expected':expected_id,'shot':s['full_id'],'label':s['prompt_label']})
    if s['full_id']not in s['fields']['时长']:add('duration_id_missing',ep,version,gi,s['full_id'])
    body='\n'.join(s['fields'].values())
    fieldlabels=re.findall(r'(?m)^([^：\n]+)：',prompt.split(f'Shot{si:02}:',1)[1].split(f'Shot{si+1:02}:',1)[0]);
    if fieldlabels!=fields_order:add('rendered_field_order',ep,version,gi,[s['full_id'],fieldlabels])
    roleconf=collections.defaultdict(list)
    for a in s['asset_names']:
     if asset_categories.get(a)=='角色':roleconf[logical_role(a)].append(a)
    for role,assets in roleconf.items():
     if len(assets)>1:
      crossphase=bool(re.search(r'叠化|转场|闪白|残影|重影|过渡|淡入|淡出|成长|十年前|成年|童年',body))
      if not crossphase:add('same_shot_role_variants_unexplained',ep,version,gi,{'shot':s['full_id'],'role':role,'assets':assets})
    for m in re.finditer(r'原表镜\s*(\d{1,3})',body):
     num=int(m.group(1));ok=1<=num<=nold
     if not ok:add('cross_reference_out_of_range',ep,version,gi,[s['full_id'],m.group()])
     cross.append({'shot':s['full_id'],'source_reference':num,'resolves':ok,'target_new_full_ids':[x['full_id']for x in ss if x['original_source_shot']==num]})
    bare=re.findall(r'(?:接|回)\s*(\d{1,3})(?![\d年月秒])',body)
    if bare:add('remaining_bare_cross_ref',ep,version,gi,[s['full_id'],bare],'P2')
   if g['full_shot_ids']!=shotids:add('group_id_manifest',ep,version,gi,g['card_name'])
  per_ep.append({'episode':ep,'version':version,'revision':d.get('revision'),'original_rows':len(set(orig)),'new_shots':len(ss),'groups':len(gs),'group_sizes':sizes,'duration_seconds':round(ep_total,4),'start_seconds':ss[0]['start_seconds'],'end_seconds':ss[-1]['end_seconds'],'quoted_english_before':old_q,'quoted_english_after':new_q,'quoted_english_exact_order':old_q==new_q})
if len(all_ids)!=len(set(all_ids)):issues.append({'kind':'duplicate_full_id','detail':[x for x,n in collections.Counter(all_ids).items()if n>1]})
if len(card_names)!=len(set(card_names)):issues.append({'kind':'duplicate_card_name'})
if len(all_groups)!=98 or len(all_ids)!=472:issues.append({'kind':'global_count','cards':len(all_groups),'shots':len(all_ids)})
manifest_cards=manifest['cards'];manifest_map={g['card_name']:g for g in manifest_cards}
for g in all_groups:
 mg=manifest_map.get(g['card_name'])
 if mg is None or mg['prompt']!=g['prompt']or mg['full_shot_ids']!=g['full_shot_ids']:issues.append({'kind':'global_manifest_body_mismatch','card':g['card_name']})
if set(manifest_map)!=set(card_names):issues.append({'kind':'global_manifest_card_names'})
report={'audited_at':datetime.now().astimezone().isoformat(),'revision':2,'mode':'independent_read_only_local_regroup_audit','passed':not issues,'summary':{'cards':len(all_groups),'full_shot_ids':len(all_ids),'all_unique':len(all_ids)==len(set(all_ids)),'original_rows_per_version':235,'new_shots_per_version':236,'tail_sizes_per_episode':[2,2,2],'quoted_english_order_all_six_pass':all(x['quoted_english_exact_order']for x in per_ep),'header_records_checked':len(headers),'mixed_variant_groups_checked':len(clothes),'source_cross_ref_occurrences':len(cross),'issues_count':len(issues)},'issues':issues,'episodes':per_ep,'source_coverage':coverage,'header_asset_and_scope_checks':headers,'mixed_wardrobe_scope_checks':clothes,'source_cross_references':cross,'asset_category_exception':{'车内':'飞书道具分类，在本剧用作车内镜头场景；按实际空间语义核对场景header。手机/续约合同仍属道具，未强求列入角色/场景头。'},'input_group_sha256':file_hashes,'limits':'核验当前六份groups、TXT与总清单正文及本次重分组；未操作浏览器、未修改工程、未重新抽帧。角色衣服适用Shot按header显式限定与该Shot实际asset_names比对，非声称平台真实引用已绑定。'}
(O/'独立重分组核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'passed':not issues,'summary':report['summary'],'issues':issues},ensure_ascii=False,indent=2))
