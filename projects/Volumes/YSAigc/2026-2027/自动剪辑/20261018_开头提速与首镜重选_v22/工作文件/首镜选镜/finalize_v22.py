import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
R=json.load(open(ROOT/'首镜三候选_原始信息.json'))
B=ROOT.parent/'live_before_v22.json';S=json.load(open(B))['snapshot'];U={}
for t in S['video']:
 for i in t['items']:
  if i.get('enabled',True):U.setdefault(i.get('path',''),[]).append({'track':t['track'],'record_start':i['start'],'record_end':i['end'],'source_in':i['offset'],'source_out':i['offset']+i['end']-i['start']})
for r in R:
 r['fresh_usage']=U.get(r['path'],[]);r['whole_source_unused_in_live_v22']=r['path'] not in U
 probe=ROOT/(r['group']+'_'+r['name'].split('_')[0]+'_probe.json');z=subprocess.run(['/Users/xuan/.local/share/promo-audio/venv/bin/python','/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts/probe.py',r['path'],'--json'],capture_output=True,text=True,check=True);probe.write_text(z.stdout);r['probe_path']=str(probe)
 if r['group']=='002':
  r.update({'rank':1,'chosen_for_first_shot':True,'source_out_frame_exclusive':115,'duration_seconds':1.60,'duration_frames':40,'visual_qa':'低机位仰拍教学楼，建筑向上汇聚，原生后移并轻下摇，运动中等；各帧楼体清晰、主体无遮挡。右上有两条细电线，广角透视明显，但没有前景树干和球网。用1.6秒首镜，切出干脆。','reason':'比红柱长廊更有建筑体量，比C308更少杂乱前景，比楼梯更适合建立学校气势'})
 elif r['group']=='004':r.update({'rank':2,'chosen_for_first_shot':False,'duration_frames':46,'visual_qa':'晨光与校园楼宇有层次，但右侧树干和支架较多，地面前景仍有球网；原生运镜轻。可穿插，不建议首镜。'})
 else:r.update({'rank':3,'chosen_for_first_shot':False,'duration_frames':46,'visual_qa':'科技主题楼梯、平稳后拉并略水平调整；画面清晰，但楼梯尺度普通，右侧红色出口标识显眼。仅作室内插镜备选。'})
R.sort(key=lambda z:z['rank'])
Q={'baseline':str(B),'unique_top_choice':R[0],'candidates':R,'expanded_new_scan_count':len(json.load(open(ROOT/'scan_manifest_v22.json'))),'additional_cached_005_thumbnails_reviewed':42,'long_source_checks':['004 A001C307 7.60–68.08秒均匀9帧','004 A001C308 5.56–49.80秒均匀9帧','002 A002C008 1.04–9.20秒均匀9帧','002 A002C009 1.00–8.80秒均匀9帧','002 A002C012 1.00–8.68秒均匀9帧','001 C0012 4.44–39.80秒均匀9帧'],'excluded':['C048大树广角畸变','C0327前景网线','C070廊道及近似廊道'],'did_not_connect_resolve':True,'did_not_modify_v21':True}
q=ROOT/'v22首镜唯一优选_教学楼仰拍.json';q.write_text(json.dumps(Q,ensure_ascii=False,indent=2));print(q);print(Q['expanded_new_scan_count'])
