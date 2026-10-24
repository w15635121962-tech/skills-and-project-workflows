from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import hashlib,json,subprocess,re,datetime

root=Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕')
work=root/'男版20_新旁白与自动剪辑_20261023/准备'
base=root/'剧梦生成视频片段/男版/《人形抱枕》（男版）EP16--EP20视频/EP20'
ffprobe=Path('/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffprobe')
paths=sorted(base.glob('*.mp4'),key=lambda p:tuple(map(int,re.findall(r'\d+',p.stem))))

def read(p):
    cmd=[str(ffprobe),'-v','error','-show_format','-show_streams','-of','json',str(p)]
    proc=subprocess.run(cmd,capture_output=True,text=True,timeout=40)
    raw=json.loads(proc.stdout) if not proc.returncode else {}
    streams=raw.get('streams',[])
    video=[s for s in streams if s.get('codec_type')=='video' and not s.get('disposition',{}).get('attached_pic')]
    audio=[s for s in streams if s.get('codec_type')=='audio']
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    m=re.fullmatch(r'男版(\d+)-(\d+)-(\d+)',p.stem)
    def value(v):
        try:return float(v)
        except (TypeError,ValueError):return None
    def fps(v):
        try:
            a,b=v.split('/');return float(a)/float(b) if float(b) else None
        except (TypeError,ValueError):return None
    return {'episode':int(m[1]) if m else None,'kind':'video' if video else 'audio',
            'filename':p.name,'path':str(p),'resolved_path':str(p.resolve()),
            'group_or_segment':int(m[2]) if m else None,'version_number':int(m[3]) if m else None,
            'suffix_semantics':'Filename suffix only; may denote supplement or alternate take. Not automatically a newer/better version.',
            'size_bytes':p.stat().st_size,'sha256':h.hexdigest(),'probe_returncode':proc.returncode,
            'probe_error':proc.stderr.strip() or None,'duration_seconds':value(raw.get('format',{}).get('duration')),
            'video_stream_count':len(video),'audio_stream_count':len(audio),
            'video_streams':[{'index':s.get('index'),'codec':s.get('codec_name'),'width':s.get('width'),
                              'height':s.get('height'),'fps':fps(s.get('avg_frame_rate')),
                              'avg_frame_rate':s.get('avg_frame_rate'),'r_frame_rate':s.get('r_frame_rate'),
                              'nb_frames':int(s['nb_frames']) if s.get('nb_frames') else None,
                              'duration_seconds':value(s.get('duration')),'pixel_format':s.get('pix_fmt')} for s in video],
            'audio_streams':[{'index':s.get('index'),'codec':s.get('codec_name'),
                              'sample_rate':s.get('sample_rate'),'channels':s.get('channels'),
                              'channel_layout':s.get('channel_layout'),'start_time':value(s.get('start_time')),
                              'duration_seconds':value(s.get('duration'))} for s in audio]}

with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(read,paths))
groups=defaultdict(list);hashes=defaultdict(list)
for r in rows:groups[r['group_or_segment']].append(r);hashes[r['sha256']].append(r['path'])
group_rows=[{'group':n,'suffix_numbers':[r['version_number'] for r in rr],
             'durations_seconds':[r['duration_seconds'] for r in rr],
             'paths':[r['path'] for r in rr]} for n,rr in sorted(groups.items())]
out={'created_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
     'scope':'Read-only exact male EP20 source inventory. No Resolve/browser operation or source mutation.',
     'project_root':str(root),'source_root':str(base),'ffprobe_path':str(ffprobe),'files':rows,
     'total':{'video_files':len(rows),'video_groups':len(groups),'standalone_narration_files_found':0,
              'video_total_all_suffixes_seconds':round(sum(r['duration_seconds'] or 0 for r in rows),6)},
     'episodes':[{'episode':20,'video_directory':str(base),'video_count':len(rows),
                  'video_groups':group_rows,'video_number_gaps_within_observed_range':
                  [n for n in range(1,max(groups)+1) if n not in groups],
                  'video_without_audio':[r['path'] for r in rows if not r['audio_stream_count']]}],
     'exact_duplicate_groups':[{'sha256':h,'paths':pp} for h,pp in hashes.items() if len(pp)>1],
     'probe_failures':[r['path'] for r in rows if r['probe_returncode']],
     'existing_narration_search':{'matches':[],
         'searched_project_locations':[str(root/'剧梦生成视频片段'),str(root/'达芬奇项目'),
                                       str(root/'对标音色旁白制作_20261020')],
         'searched_downloads':'/Users/zc/Downloads, audio filename matching male20 or EP20 only',
         'finding':'No exact male EP20 named standalone MP3/WAV/M4A/AAC/FLAC found at inventory time. Embedded source-video audio is present and listed. Generic unnamed downloads are not asserted to be male EP20.'},
     'limits':['Filename continuity does not establish script coverage or canonical source episode.',
               'Male current character identities are Vittoria/Evan/Oliver; no female Matteo/Eliza narration was substituted.',
               'All suffixes are candidates for visual and audible review. No automatic largest-suffix choice.',
               'No whole-clip listening or generated-film quality validation is claimed.']}
work.mkdir(parents=True,exist_ok=True)
(work/'素材盘点.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'total':out['total'],'groups':group_rows,'duplicates':len(out['exact_duplicate_groups']),
                  'probe_failures':out['probe_failures']},ensure_ascii=False,indent=2))
