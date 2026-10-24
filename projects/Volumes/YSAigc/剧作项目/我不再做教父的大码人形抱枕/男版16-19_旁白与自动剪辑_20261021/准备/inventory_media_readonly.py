from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json, re, subprocess, sys

OUT=Path(__file__).resolve().parent
ROOT=OUT.parent.parent
VIDEO=ROOT/'剧梦生成视频片段/男版/《人形抱枕》（男版）EP16--EP20视频'
PROBE=Path('/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffprobe')
def probe(p):
    c=subprocess.run([str(PROBE),'-v','error','-show_streams','-show_format','-of','json',str(p)],capture_output=True,text=True,encoding='utf-8',timeout=45)
    if c.returncode:return {'path':str(p),'filename':p.name,'probe_error':c.stderr}
    d=json.loads(c.stdout);streams=d.get('streams',[]);v=[s for s in streams if s['codec_type']=='video'];a=[s for s in streams if s['codec_type']=='audio']
    m=re.match(r'^男版(\d+)-(\d+)-(\d+)\.mp4$',p.name)
    return {'path':str(p),'filename':p.name,'bytes':p.stat().st_size,'duration_seconds':float(d.get('format',{}).get('duration',0)),
        'video_streams':[{k:s.get(k) for k in ['index','codec_name','width','height','r_frame_rate','avg_frame_rate','nb_frames','duration','start_time']} for s in v],
        'audio_streams':[{k:s.get(k) for k in ['index','codec_name','sample_rate','channels','channel_layout','duration','start_time']} for s in a],
        'has_embedded_audio':bool(a),'episode_group_segment':list(map(int,m.groups())) if m else None}
paths=sorted([p for ep in range(16,20) for p in (VIDEO/f'EP{ep}').glob('*.mp4')],key=lambda p:tuple(map(int,re.findall(r'\d+',p.stem))))
with ThreadPoolExecutor(max_workers=6) as ex:media=list(ex.map(probe,paths))
episodes=[]
for ep in range(16,20):
    rows=[d for d in media if d['episode_group_segment'] and d['episode_group_segment'][0]==ep]
    groups={}
    for row in rows:groups.setdefault(row['episode_group_segment'][1],[]).append(row['episode_group_segment'][2])
    episodes.append({'episode':ep,'version':'male_gender_swap','video_directory':str(VIDEO/f'EP{ep}'),'video_count':len(rows),
        'group_numbers':sorted(groups),'within_group_numbers':{str(k):sorted(v) for k,v in groups.items()},
        'missing_filename_group_numbers':[g for g in range(1,max(groups,default=0)+1) if g not in groups],
        'within_group_filename_gaps':{str(g):[i for i in range(1,max(v)+1) if i not in v] for g,v in groups.items() if any(i not in v for i in range(1,max(v)+1))},
        'raw_video_total_seconds':round(sum(d['duration_seconds'] for d in rows),3),'with_embedded_audio':sum(d['has_embedded_audio'] for d in rows),'videos':rows})
resolve={'read_only':True,'ui_switch':False,'save':False}
try:
    sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
    from resolve_bootstrap import get_resolve
    r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();current=p.GetCurrentTimeline()
    resolve.update(project=p.GetName(),version=r.GetVersionString(),current_timeline=current.GetName() if current else None,timeline_count=p.GetTimelineCount())
    names=[]
    for i in range(1,p.GetTimelineCount()+1):
        t=p.GetTimelineByIndex(i);name=t.GetName()
        names.append({'index':i,'name':name,'id':t.GetUniqueId()})
    resolve['all_timelines']=names
    resolve['male_ep16_19_existing_timelines']=[x for x in names if ('男版' in x['name'] or '性转' in x['name']) and re.search(r'(?:EP|第|_|版)(?:0?16|0?17|0?18|0?19)(?:_|集|\b)',x['name'],re.I)]
except Exception as e:resolve['error']=repr(e)
reusable=[]
for filename,note in [
    ('assemble_native.py','已实际用于男版21–25原生时间线，画面/同期声同源同边界并链接，旁白100%；本脚本硬编码21–25目录/备份/轨名/人物，不能直接运行，需复制改造。'),
    ('build_ep21_23_plan.py','分段剪辑计划示例，依赖该集转录与源片实际事件；只能复用结构，不得照搬内容。'),
    ('verify_save_reopen.py','保存/重开后逐片段、链接同期声与旁白时间核验参考。'),
    ('ASR/run_blind_asr.py','本地音频逐词转录入口，可为16–19画面及旁白提供剪点，需重做目标清单。'),
    ('ASR/measure_source_levels.py','素材响度分析，可保留源片同期声并在旁白段按需衰减。')]:
    q=ROOT/'男版21-25_自动剪辑_20261021'/filename
    if q.exists():reusable.append({'path':str(q),'note':note})
out={'created_local':datetime.now().isoformat(timespec='seconds'),'task':'男版EP16–19，新男版.wav制作旁白后自动剪辑','mutation_scope':'仅新建本准备清单/脚本；未改源素材及Resolve。',
    'version_identity':{'male_script_english':str(ROOT/'性转版/没有你我睡不着（大码性转）-EN.docx'),'characters':['Oliver','Vittoria','Evan'],
        'episode_numbering':'男版源剧本集号直接对应男版视频同号；不得套用女版的不同集号或Matteo/Eliza身份。'},
    'new_voice_reference':probe(Path('/Users/zc/Downloads/男版.wav')),
    'scan_scope':{'primary_video_root':str(VIDEO),'additional_roots_searched_by_rg':['/Users/zc/Downloads','/Volumes/Aigc01A/01_AI剧项目','/Volumes/Aigc02B/01_AI剧项目','/Volumes/YSAigc/剧作项目','/Volumes/YSAigc/Claude','/Volumes/Aigc02B/cloude'],
        'narration_reference_roots':[str(ROOT/'达芬奇项目'),str(ROOT/'剧梦生成视频片段/大码人形抱枕/旁白/男版')],
        'old_male_ep16_19_narration_found':[],'old_narration_note':'本次文件名检索未找到男版16–19现成独白，男版独白10–15和21–25存在但不属本范围；女版16–19不得替代。'},
    'total_video_count':len(media),'episodes':episodes,'resolve':resolve,'reusable_scripts':reusable,
    'limitations':['文件名仅提供组序候选；同组多段可能是连续拆镜或替代版本，须根据男版剧本和源视频内容审查选用。','ffprobe确认音轨存在，不证明对白非静音、内容或同步正确；后续实际转录/试听/画面核验。','EP18的组2缺第2子编号，只说明文件名缺号，不能直接认定漏剧情；需画面和剧本核对。','新音色旁白尚待根任务制作下载；清单不能冒充旁白或剪辑已完成。']}
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'media_inventory.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(OUT/'media_inventory.json'),'episodes':[{k:e[k] for k in ['episode','video_count','group_numbers','raw_video_total_seconds','with_embedded_audio','within_group_filename_gaps']} for e in episodes],
    'resolve_project':resolve.get('project'),'existing_targets':resolve.get('male_ep16_19_existing_timelines'),'resolve_error':resolve.get('error')},ensure_ascii=False))
