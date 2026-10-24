from pathlib import Path
import json, subprocess, hashlib, re, os, datetime
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, Counter
root=Path.cwd()
base=root/'剧梦生成视频片段'
out=root/'达芬奇剪辑_EP21-25_20261020'
tool_dir=Path('/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin')
ffprobe=tool_dir/'ffprobe'
media_ext={'.mp4','.mov','.mkv','.m4v','.avi','.webm','.mp3','.wav','.m4a','.aif','.aiff','.flac','.aac','.ogg','.opus'}
files=[]
for p in base.rglob('*'):
 if p.is_file() and p.suffix.lower() in media_ext and any(re.fullmatch(r'EP2[1-5]',v) for v in p.parts):files.append(p)
files.sort(key=lambda p:str(p))
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def inspect(p):
 cmd=[str(ffprobe),'-v','error','-show_format','-show_streams','-show_chapters','-of','json',str(p)]
 result=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
 raw=json.loads(result.stdout) if result.returncode==0 else {}
 streams=raw.get('streams',[])
 vs=[s for s in streams if s.get('codec_type')=='video' and not s.get('disposition',{}).get('attached_pic')]
 aa=[s for s in streams if s.get('codec_type')=='audio']
 ep=int(next(re.fullmatch(r'EP(2[1-5])',v).group(1) for v in p.parts if re.fullmatch(r'EP2[1-5]',v)))
 vmatch=re.fullmatch(r'女版(\d+)-(\d+)([A-Za-z]?)-(\d+)',p.stem)
 amatch=re.fullmatch(r'女版(\d+)-(\d+)',p.stem)
 def frac(v):
  try:
   n,d=map(float,v.split('/'));return n/d if d else None
  except:return None
 fmt=raw.get('format',{})
 row={'path':str(p),'relative_path':str(p.relative_to(root)),'resolved_path':str(p.resolve()),'episode':ep,'kind':'video' if vs else 'audio','size_bytes':p.stat().st_size,'sha256':digest(p),'ffprobe_returncode':result.returncode,'probe_error':result.stderr.strip() or None,'duration_seconds':float(fmt['duration']) if fmt.get('duration') else None,'video_stream_count':len(vs),'audio_stream_count':len(aa),'subtitle_stream_count':sum(s.get('codec_type')=='subtitle' for s in streams),'video_streams':[{'index':s.get('index'),'codec':s.get('codec_name'),'width':s.get('width'),'height':s.get('height'),'avg_frame_rate':s.get('avg_frame_rate'),'r_frame_rate':s.get('r_frame_rate'),'fps':frac(s.get('avg_frame_rate','0/0')),'duration_seconds':float(s['duration']) if s.get('duration') else None,'nb_frames':int(s['nb_frames']) if s.get('nb_frames') else None,'pixel_format':s.get('pix_fmt'),'sample_aspect_ratio':s.get('sample_aspect_ratio'),'display_aspect_ratio':s.get('display_aspect_ratio'),'color_transfer':s.get('color_transfer'),'color_primaries':s.get('color_primaries')} for s in vs],'audio_streams':[{'index':s.get('index'),'codec':s.get('codec_name'),'channels':s.get('channels'),'channel_layout':s.get('channel_layout'),'sample_rate':int(s['sample_rate']) if s.get('sample_rate') else None,'duration_seconds':float(s['duration']) if s.get('duration') else None,'bit_rate':s.get('bit_rate'),'start_time':s.get('start_time')} for s in aa],'raw_ffprobe':raw}
 if vmatch:row.update({'shot_group':str(int(vmatch.group(2)))+vmatch.group(3).upper(),'shot_group_number':int(vmatch.group(2)),'shot_group_suffix':vmatch.group(3).upper() or None,'version_number':int(vmatch.group(4))})
 if amatch:row.update({'narration_segment':int(amatch.group(2)),'canonical_narration_copy':p.parent.parent==base/'独白'})
 return row
with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(inspect,files))
# Skill probe provides a second compact probe and suspected-VFR indicator, using the same local ffprobe.
env=os.environ.copy();env['PATH']=str(tool_dir)+os.pathsep+env.get('PATH','')
skill_cmd=['python3','/Users/zc/.codex/skills/ffmpeg-skill/scripts/probe.py']+[str(p) for p in files]
skill_result=subprocess.run(skill_cmd,capture_output=True,text=True,timeout=120,env=env)
skill_doc=json.loads(skill_result.stdout) if skill_result.returncode==0 else None
if skill_doc is not None:
 (out/'ffmpeg_skill_probe_EP21-25.json').write_text(json.dumps(skill_doc,ensure_ascii=False,indent=2)+'\n')
 for r,s in zip(rows,skill_doc if isinstance(skill_doc,list) else [skill_doc]):
  r['variable_frame_rate_suspected']=s.get('video',{}).get('variable_frame_rate_suspected') if s.get('video') else None
hashes=defaultdict(list)
for r in rows:hashes[r['sha256']].append(r['path'])
dups=[{'sha256':h,'paths':paths,'count':len(paths)} for h,paths in hashes.items() if len(paths)>1]
episodes=[]
for ep in range(21,26):
 es=[r for r in rows if r['episode']==ep];videos=[r for r in es if r['kind']=='video'];audio=[r for r in es if r['kind']=='audio'];canonical=[r for r in audio if r.get('canonical_narration_copy')]
 groups=defaultdict(list)
 for r in videos:groups[r.get('shot_group','unparsed')].append(r)
 sortgroup=lambda x:(int(re.match(r'\d+',x).group()) if re.match(r'\d+',x) else 999,x)
 gv=[]
 for name in sorted(groups,key=sortgroup):
  g=sorted(groups[name],key=lambda r:r.get('version_number',0))
  gv.append({'group':name,'version_count':len(g),'version_numbers':[r.get('version_number') for r in g],'files':[r['path'] for r in g],'durations_seconds':[r['duration_seconds'] for r in g],'all_versions_identical_bytes':len(set(r['sha256'] for r in g))==1})
 nums=sorted(set(r.get('shot_group_number') for r in videos if r.get('shot_group_suffix') is None))
 missing=[n for n in range(1,max(nums)+1) if n not in nums] if nums else None
 episodes.append({'episode':ep,'video_file_count':len(videos),'video_group_count':len(groups),'base_group_numbers_present':nums,'number_gaps_within_observed_base_groups':missing,'supplemental_suffix_groups':[g['group'] for g in gv if re.search('[A-Z]',g['group'])],'video_total_all_versions_seconds':round(sum(r['duration_seconds'] or 0 for r in videos),6),'video_total_one_first_numbered_version_per_group_seconds':round(sum(sorted(groups[k],key=lambda r:r.get('version_number',0))[0]['duration_seconds'] or 0 for k in groups),6),'video_groups':gv,'groups_with_alternative_versions':[g['group'] for g in gv if g['version_count']>1],'narration_physical_file_count':len(audio),'narration_unique_sha256_count':len(set(r['sha256'] for r in audio)),'narration_segment_numbers':sorted(r['narration_segment'] for r in canonical),'narration_canonical_files':[r['path'] for r in sorted(canonical,key=lambda r:r['narration_segment'])],'narration_total_unique_seconds':round(sum(r['duration_seconds'] or 0 for r in canonical),6),'subtitle_files_found_for_episode':[],'video_without_audio':[r['path'] for r in videos if not r['audio_stream_count']]})
subtitle_paths=[]
for directory,dirs,names in os.walk(root):
 dirs[:]=[d for d in dirs if d not in {'skills-export-20261019','node_modules','.git','ASR'}]
 for name in names:
  p=Path(directory)/name
  if p.suffix.lower() in {'.srt','.ass','.vtt','.sub'}:subtitle_paths.append(str(p))
result={'created_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'scope':'Only EP21–25 generated media, local narration copies, and existing subtitle availability. No source media modified; no Resolve operations; no downloads; no new generation.','project_root':str(root),'ffprobe_path':str(ffprobe),'ffmpeg_path':str(tool_dir/'ffmpeg'),'tool_version':'8.1.2','ffmpeg_skill_probe_returncode':skill_result.returncode,'ffmpeg_skill_probe_error':skill_result.stderr.strip() or None,'file_count':len(rows),'video_file_count':sum(r['kind']=='video' for r in rows),'audio_physical_file_count':sum(r['kind']=='audio' for r in rows),'audio_unique_sha256_count':len(set(r['sha256'] for r in rows if r['kind']=='audio')),'episodes':episodes,'exact_duplicate_groups':dups,'files':rows,'subtitle_search':{'search_root':str(root),'excluded_directories':['skills-export-20261019','node_modules','.git','ASR'],'all_existing_subtitle_files':sorted(subtitle_paths),'EP21_to_EP25_existing_subtitle_files':[],'finding':'Only existing EP01–03 subtitle files were found in this project; no EP21–25 SRT/ASS/VTT found.'},'missing_and_limits':{'missing_entire_episodes':[e['episode'] for e in episodes if not e['video_file_count']],'missing_numbered_groups_by_filename':{str(e['episode']):e['number_gaps_within_observed_base_groups'] for e in episodes},'script_content_coverage':'Not validated by metadata or sequential filenames; internal shots/dialogue coverage and version choice require matching actual clips to English script. No assumption that highest version number is best.','audio_stream_presence':'Track presence alone does not prove intelligible dialogue, complete words, or correct lip sync.','subtitle_timing':'No EP21–25 subtitle timing existed to validate.','external_media_references':'No EP21–25 external-media reference path or symlink found in the inspected current-project generated-media directory and previous import records. Resolve media-pool external paths are outside this read-only inventory unless supplied.'}}
(out/'素材盘点.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
summary=['EP21–25素材只读盘点（2026-10-20）',f'共{result["video_file_count"]}条视频，{sum(e["video_group_count"] for e in episodes)}个文件名镜组；音频{result["audio_physical_file_count"]}个路径，SHA-256去重后{result["audio_unique_sha256_count"]}条。']
for e in episodes:summary.append(f'EP{e["episode"]}：视频{e["video_file_count"]}条/{e["video_group_count"]}组，主镜组{e["base_group_numbers_present"]}；多版本组{e["groups_with_alternative_versions"]}；独白{e["narration_unique_sha256_count"]}条/{e["narration_total_unique_seconds"]:.3f}秒。')
summary+=['EP21–25未缺整集；当前文件名主镜组编号均连续。但不能据此声称剧本全部内镜/对白完整。','EP22额外有5B、5C两个带字母镜组，保留为独立补充分组，不自动当作05替代。','两套独白路径“剧梦生成视频片段/独白/EPxx”与“剧梦生成视频片段/女版/独白/EPxx”逐条做了整文件SHA-256校验，重复音频不应重复入时间线。','项目现有字幕仅前3集，EP21–25未发现SRT/ASS/VTT；需按最终剪辑后制作。','元数据、音轨存在和文件名编号不能代替内容/台词/口型验收，也未自动选最高版本。']
(out/'素材盘点摘要.txt').write_text('\n'.join(summary)+'\n')
print('\n'.join(summary))
print('JSON:',str(out/'素材盘点.json'))
print('Probe failures:',[r['path'] for r in rows if r['ffprobe_returncode']])
print('Video formats:',Counter((r['video_streams'][0]['width'],r['video_streams'][0]['height'],r['video_streams'][0]['fps']) for r in rows if r['kind']=='video'))
print('Video audio tracks:',Counter(r['audio_stream_count'] for r in rows if r['kind']=='video'))
