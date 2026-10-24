from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
from datetime import datetime
import hashlib
import json
import re
import subprocess

ROOT=Path(__file__).resolve().parent.parent
VIDEO=ROOT/'剧梦生成视频片段/男版/《人形抱枕》（男版）EP21--EP25视频素材'
AUDIO=ROOT/'达芬奇项目/《人性抱枕》（男版）独白EP21--EP25'
PROBE=Path('/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffprobe')
video_re=re.compile(r'^男版(\d+)-(\d+)-(\d+)\.mp4$')
audio_re=re.compile(r'^男版(\d+)-(\d+)(?:-(\d+))?\.mp3$')

def num_sort(p):
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)',p.name)]

def probe(p):
    cp=subprocess.run([str(PROBE),'-v','error','-show_format','-show_streams','-of','json',str(p)],capture_output=True,text=True,timeout=45)
    if cp.returncode:
        return {'path':str(p),'error':cp.stderr[-1000:]}
    d=json.loads(cp.stdout)
    st=d.get('streams',[])
    vs=[x for x in st if x.get('codec_type')=='video']
    au=[x for x in st if x.get('codec_type')=='audio']
    return dict(path=str(p),filename=p.name,bytes=p.stat().st_size,
                duration_seconds=float(d.get('format',{}).get('duration',0)),
                format_name=d.get('format',{}).get('format_name'),
                video_streams=[{k:x.get(k) for k in ('index','codec_name','width','height','pix_fmt','r_frame_rate','avg_frame_rate','nb_frames','duration','start_time')} for x in vs],
                audio_streams=[{k:x.get(k) for k in ('index','codec_name','sample_rate','channels','channel_layout','duration','start_time')} for x in au],
                has_video=bool(vs),has_embedded_audio=bool(au),
                modification_time_local=datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec='seconds'))

paths=[]
for ep in range(21,26):
    paths.extend(sorted((VIDEO/f'EP{ep}').glob('*.mp4'),key=num_sort))
    paths.extend(sorted((AUDIO/f'EP{ep}').glob('*.mp3'),key=num_sort))
with ThreadPoolExecutor(max_workers=6) as ex:
    data=dict(zip(paths,ex.map(probe,paths)))

episodes=[]
warnings=[]
for ep in range(21,26):
    vf=[];af=[];groups={};aseq={}
    for p in sorted((VIDEO/f'EP{ep}').glob('*.mp4'),key=num_sort):
        r=dict(data[p]);m=video_re.match(p.name)
        if not m:
            r['filename_parse_error']=True
            warnings.append(dict(episode=ep,type='unparsed_video_filename',path=str(p)))
        else:
            declared,g,seg=map(int,m.groups())
            r.update(episode_directory=ep,episode_in_filename=declared,group_number=g,within_group_number=seg,order_key_candidate=[ep,g,seg])
            if declared!=ep:
                r['episode_filename_mismatch']=True
                r['candidate_interpretation']='疑似文件名漏写2；仅作为EP24组7段1候选，不修改文件名，不视为已内容核验。'
                warnings.append(dict(episode=ep,type='episode_filename_mismatch',path=str(p),filename_episode=declared,directory_episode=ep,suspected_order_key=[ep,g,seg],requires_content_check=True))
            groups.setdefault(g,[]).append(seg)
        vf.append(r)
    vf.sort(key=lambda x:x.get('order_key_candidate',[ep,999,999]))
    for p in sorted((AUDIO/f'EP{ep}').glob('*.mp3'),key=num_sort):
        r=dict(data[p]);m=audio_re.match(p.name)
        if not m:
            r['filename_parse_error']=True
            warnings.append(dict(episode=ep,type='unparsed_audio_filename',path=str(p)))
        else:
            declared,seq,sub=m.groups();declared=int(declared);seq=int(seq);sub=int(sub) if sub else None
            r.update(episode_directory=ep,episode_in_filename=declared,narration_sequence=seq,subnumber=sub,order_key_candidate=[ep,seq,sub or 0])
            aseq.setdefault(seq,[]).append(sub)
        af.append(r)
    af.sort(key=lambda x:x.get('order_key_candidate',[ep,999,999]))
    vgaps=[n for n in range(1,max(groups,default=0)+1) if n not in groups]
    sgaps={str(g):[n for n in range(1,max(ids)+1) if n not in ids] for g,ids in groups.items() if any(n not in ids for n in range(1,max(ids)+1))}
    agaps=[n for n in range(1,max(aseq,default=0)+1) if n not in aseq]
    asgaps={str(s):[n for n in range(1,max(v for v in ids if v is not None)+1) if n not in ids] for s,ids in aseq.items() if any(v is not None for v in ids)}
    asgaps={k:v for k,v in asgaps.items() if v}
    if asgaps:warnings.append(dict(episode=ep,type='audio_subnumber_gap',gaps=asgaps,note='只是命名缺号，是否真正缺旁白或该编号属于替代版本须听辨/对照男版剧本，不能直接断言缺句。'))
    episodes.append(dict(episode=ep,version='male_gender_swap_only',video_directory=str(VIDEO/f'EP{ep}'),audio_directory=str(AUDIO/f'EP{ep}'),
                         video_count=len(vf),video_group_count=len(groups),group_numbers=sorted(groups),within_group_numbers={str(k):sorted(v) for k,v in sorted(groups.items())},
                         video_total_duration_seconds=round(sum(x.get('duration_seconds',0) for x in vf),6),
                         video_with_embedded_audio=sum(x.get('has_embedded_audio',False) for x in vf),
                         narration_count=len(af),narration_primary_sequence_numbers=sorted(aseq),
                         narration_total_duration_seconds=round(sum(x.get('duration_seconds',0) for x in af),6),
                         name_sequence_gaps=dict(video_group_number_gaps=vgaps,video_within_group_number_gaps=sgaps,narration_primary_gaps=agaps,narration_subnumber_gaps=asgaps),
                         completeness='五集目录及素材均存在；仅能核验当前编号内部是否缺号，原剧本尾部或内容漏镜尚需父任务对照剧本与画面判断。',
                         videos=vf,narration_audio=af))

out=dict(project=str(ROOT),created_local=datetime.now().isoformat(timespec='seconds'),version='男版/性转版，明确排除女版',
         scope=dict(top_level_directory_list_read=True,scan_roots=[str(VIDEO),str(AUDIO)],
                    excluded_large_export_directory=str(ROOT/'skills-export-20261019'),
                    excluded_female_roots=[str(ROOT/'剧梦生成视频片段/女版'),str(ROOT/'剧梦生成视频片段/独白'),str(ROOT/'剧梦生成视频片段/大码人形抱枕/视频/女版'),str(ROOT/'剧梦生成视频片段/大码人形抱枕/旁白/女版')],
                    file_mutation=False,resolve_used=False),
         video_naming_rule=dict(pattern='男版<集号>-<组/镜号>-<组内号>.mp4',sort='按集号、第二字段数值、第三字段数值自然顺序候选；不得按字符串把10排在2前。',
                                caveat='仅凭文件名不能断定第三字段是顺序拆分镜还是替代版本；应对照男版剧本/画面选用，不自动丢弃早号或重复拼接替代版。'),
         narration_naming_rule=dict(pattern='男版<集号>-<旁白序号>[-<细分/版本号>].mp3',sort='按集与旁白主序号自然排序；可疑子编号先比对文本/听辨，不能一律当作另一句。',
                                    ep21_sequence5='存在5-1/5-3/5-4，5-2未找到；三段的顺接/替代含义尚未核验。'),
         total_video_count=sum(x['video_count'] for x in episodes),total_narration_audio_count=sum(x['narration_count'] for x in episodes),
         missing_episode_directories=[ep for ep in range(21,26) if not (VIDEO/f'EP{ep}').is_dir() or not (AUDIO/f'EP{ep}').is_dir()],
         warnings=warnings,episodes=episodes,
         probe_limits='ffprobe确认媒体时长/流结构与有无嵌入音轨，不证明音轨是否实际非静音、音画同步或内容符合原剧本；未听辨或播放。')
target=Path(__file__).resolve().parent/'男版素材盘点.json'
target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(output=str(target),video_count=out['total_video_count'],audio_count=out['total_narration_audio_count'],episodes=[{k:x[k] for k in ('episode','video_count','video_group_count','video_with_embedded_audio','narration_count','video_total_duration_seconds','narration_total_duration_seconds')} for x in episodes],warnings=warnings),ensure_ascii=False))
