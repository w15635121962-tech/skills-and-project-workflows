import csv,hashlib,json,datetime,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'制作进度.json'
p=json.loads(P.read_text(encoding='utf-8'))
items=p['items'];alts=p.get('alternate_versions',[]);allrows=items+alts
assert len(items)==24 and len(alts)==4
assert all(x.get('technical_decode')=='passed' for x in allrows)
assert len({x['audio_sha256'] for x in allrows})==28
assert all(Path(x['audio_file']).stat().st_size==x['audio_bytes'] and hashlib.sha256(Path(x['audio_file']).read_bytes()).hexdigest()==x['audio_sha256'] for x in allrows)
chosen02={'大码女版枕头05-03','大码女版枕头06-01','大码女版枕头06-02'}
for x in alts:
    key=x['basename'].rsplit('-',1)[0]
    x['adopted_by_root']=key in chosen02
    x['content_review']='Root confirmed two independent blind ASR checks; use take02' if key in chosen02 else 'Pending Root independent content review; first take nod/not failed cross-check'
    x['status']='downloaded_existing_variant_technical_verified_root_selected' if key in chosen02 else 'downloaded_existing_variant_technical_verified_pending_content_review'
    (Path(x['audio_file']).parent/(x['basename']+'_记录.json')).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
selected=[]
for x in items:
    key=x['basename'].rsplit('-',1)[0]
    q=next(a for a in alts if a['basename']==key+'-02') if key in chosen02 else x
    selected.append({'unit':key,'episode':q['episode'],'narration_sequence':q['narration_sequence'],'take':q['take'],'source_path':q['audio_file'],'sha256':q['audio_sha256'],'duration_seconds':q['duration_seconds'],'content_review':'pending small-model cross-check per Root' if key=='大码女版枕头06-09' else 'take selected per Root'})
p.update(status='COMPLETE_DOWNLOAD_AND_TECHNICAL_QC_24_UNITS_28_FILES',completed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),downloaded_count=24,alternate_downloaded_count=4,total_downloaded_files=28,technical_verified_count=24,all_file_technical_verified_count=28)
p['primary_duration_seconds']=round(sum(x['duration_seconds'] for x in items),3)
p['selected_duration_seconds']=round(sum(x['duration_seconds'] for x in selected),3)
p['per_episode_primary_seconds']={str(e):round(sum(x['duration_seconds'] for x in items if x['episode']==e),3) for e in [4,5,6]}
p['per_episode_selected_seconds']={str(e):round(sum(x['duration_seconds'] for x in selected if x['episode']==e),3) for e in [4,5,6]}
p['selection_status']={'narration_units':24,'downloaded_files':28,'confirmed_use_take02':sorted(chosen02),'all_other_units_default_take01':True,'content_review_pending':['大码女版枕头06-09'],'originals_preserved':True,'delivery_copy_by_root':'Root completed separate 24-unit delivery folder; see 最终采用清单.json. EP06-09 replacement decision is pending. No download originals replaced here.'}
p['source_manifest_sha256']=hashlib.sha256((ROOT/'文本核验/manifest.json').read_bytes()).hexdigest()
p['speed_evidence_boundary']='Requested100%; exact existing voice, Seed TTS/text reading UI. UI exposes no separate speed control. No time stretch, resample, transcoding or audio processing was applied; native downloads were byte-verified copies. File technical properties alone do not prove acoustic identity or speed.'
P.write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
cols=['basename','episode','narration_sequence','take','status','voice','model','platform_variant','audio_file','audio_bytes','audio_sha256','duration_seconds','download_original_filename','ui_record_dom_key','ui_record_handoff_key']
for filename,rows in [(ROOT/'制作进度.csv',items),(ROOT/'备选版本/备选版本进度.csv',alts)]:
    with filename.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');w.writeheader();w.writerows(rows)
(ROOT/'采用版本映射.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2),encoding='utf-8')
keys=['status','completed_at','voice','model','mode','speed_percent','generation_submissions','starting_credits_visible','credits_visible','credits_spent_observed','downloaded_count','alternate_downloaded_count','total_downloaded_files','technical_verified_count','all_file_technical_verified_count','primary_duration_seconds','selected_duration_seconds','per_episode_primary_seconds','per_episode_selected_seconds','selection_status','source_manifest_sha256','speed_evidence_boundary','completion_screenshot','forbidden_actions_confirmed']
report={k:p[k] for k in keys}
report['files']=[{k:x.get(k) for k in cols} for x in allrows]
report['scope_boundary']='Technical verification and UI/file correspondence complete. Root independent content-ASR makes final take choices; last EP06-09 word check is still pending. No successful generation was repeated and no new generation was used for alternate variants.'
(ROOT/'制作完成报告.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
shot=str((ROOT/'制作完成_女版04-06_准确对标女声.png').resolve())
md=f"""# 女版第04–06集旁白制作完成报告

共24个旁白单元：第04集8段、第05集7段、第06集9段。下载24个第一版文件，另从同一生成记录下载4个现成第二版，共28个文件。

音色为“对标女旁白_测试A_1020”，Seed TTS／文本朗读。按自然默认原速制作，没有加速或音频后处理；界面不单独显示语速百分比。24条生成实际受理，积分90→44，消耗46；4个备选只下载，没有新增生成扣费。

原24个第一版时长为第04集94.920秒、第05集88.032秒、第06集101.352秒，合计284.304秒。按当前3个已确定第二版选择后的24段合计{p['selected_duration_seconds']:.3f}秒，第06集第09段最终版本仍待核验。28文件全部通过大小、SHA、命名、音轨时长与完整解码检查，SHA无重复。

主线程已确认第05集第03段、第06集第01及02段采用第二版，其余先用第一版。第06集第09段第一版的nod/not发音疑点未通过交叉核验，已下载同记录第二版，等待主线程决定；当前交付副本中该段尚未获得内容通过。原第一版与所有下载文件保留，本报告不把28个文件称为28段采用内容。主线程已另复制24份采用文件到“交付音频”，路径与SHA见“最终采用清单.json”，第06集第09段副本将由主线程按核验结果替换；本子任务没有覆盖原下载。

制作进度JSON／CSV记录每段原文、准确音色、对应UI记录、原下载名、归档路径、大小、SHA与实际时长。备选另有记录JSON及CSV。没有发送飞书，没有操作剧梦IAB或达芬奇，没有上传新音色。

![即梦最新第6集完成记录与准确女声]({shot})
"""
(ROOT/'制作完成报告.md').write_text(md,encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='files'},ensure_ascii=False,indent=2))
print('alternates',[(x['basename'],x['duration_seconds']) for x in alts])
