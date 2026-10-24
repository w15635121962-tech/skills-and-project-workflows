from pathlib import Path
import json, hashlib, subprocess, wave, math
from datetime import datetime

BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'试听'
PROJECT=BASE.parent
FFMPEG=Path('/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffmpeg')
FFPROBE=FFMPEG.with_name('ffprobe')
READBACK=BASE/'Resolve_组装回读.json'
PCMLIST=BASE/'PCM_原速准备清单.json'
SELECTION=PROJECT/'女版04-06_新旁白_20261023/最终采用清单.json'
TEXT=PROJECT/'女版04-06_新旁白_20261023/文本核验/manifest.json'
SR=48000

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def close(a,b): return abs(float(a)-float(b))<1e-8
def wave_data(path):
    with wave.open(str(path),'rb') as w:
        meta={'sample_rate':w.getframerate(),'channels':w.getnchannels(),'sample_width_bytes':w.getsampwidth(),'sample_count':w.getnframes(),'compression_type':w.getcomptype()}
        pcm=w.readframes(w.getnframes())
        assert len(pcm)==meta['sample_count']*meta['channels']*meta['sample_width_bytes'], f'incomplete WAV:{path}'
        return meta,pcm

evidence={str(p):sha(p) for p in [READBACK,PCMLIST,SELECTION,TEXT]}
r=load(READBACK); pm=load(PCMLIST); selected=load(SELECTION); text=load(TEXT)
pmi={x['basename']:x for x in pm['items']}
seli={x['basename']:x for x in selected['files']}
texti={(x['episode'],x['narration_sequence']):x for x in text['groups']}
issues=[]
def check(ok,message):
    if not ok: issues.append(message)

check(r['rate']==1.0,'global_rate_not_1')
check(len(r['timelines'])==3,'timeline_count_not_3')
check({t['episode'] for t in r['timelines']}=={4,5,6},'timeline_episodes_not_4_5_6')
check(len(pmi)==24 and len(seli)==24 and len(texti)==24,'source_manifest_count_not_24')
all_seen=[]
audits=[]
wave_cache={}
for tl in r['timelines']:
    ep=tl['episode']; expected=[x for x in pm['items'] if x['episode']==ep]
    expected.sort(key=lambda x:x['sequence'])
    expected_count={4:8,5:7,6:9}[ep]
    check(tl['name']==f'大码_女版_EP{ep:02d}_新旁白原速测试_20261023',f'EP{ep}:wrong_timeline_name')
    check(tl['track_name']==f'第{ep}集_女主新旁白_原速',f'EP{ep}:wrong_track_name')
    check(len(tl['clips'])==expected_count,f'EP{ep}:wrong_clip_count')
    check([c['basename'] for c in tl['clips']]==[c['basename'] for c in expected],f'EP{ep}:source_order_not_manifest_order')
    check(len(tl['joins'])==expected_count-1,f'EP{ep}:wrong_join_count')
    cursor=0; cliprows=[]; joinrows=[]
    for i,(c,p) in enumerate(zip(tl['clips'],expected)):
        name=c['basename']; all_seen.append(name); selection=seli[name]; original=texti[(ep,c['sequence'])]
        wav=Path(p['output_path']); meta,pcm=wave_data(wav); wave_cache[name]=(meta,pcm)
        actualsha=sha(wav)
        dur=meta['sample_count']/SR
        start_samples=round(c['start_frame']/tl['fps']*SR)
        end_samples=round(c['end_frame']/tl['fps']*SR)
        check(c['sequence']==i+1 and p['sequence']==i+1,f'{name}:sequence')
        check(c['take']==p['take']==selection['take'],f'{name}:take')
        check(c['source_path']==p['output_path'],f'{name}:exact_source_path')
        check(c['source_sha256']==p['output_sha256']==actualsha,f'{name}:PCM_SHA')
        check(c['original_mp3_sha256']==p['source_sha256']==selection['sha256'],f'{name}:original_MP3_SHA')
        check(p['source_path']==selection['audio_file'],f'{name}:selected_delivery_path')
        check(sha(p['source_path'])==p['source_sha256'],f'{name}:source_mp3_changed')
        check(c['source_start_seconds']==0.0,f'{name}:source_nonzero_inpoint')
        check(close(c['source_end_seconds'],dur),f'{name}:source_end_not_full')
        check(close(c['duration_seconds'],dur),f'{name}:duration_not_full')
        check(close((c['end_frame']-c['start_frame'])/tl['fps'],dur),f'{name}:implied_speed_not_1')
        check(c['clip_gain_db']==0.0,f'{name}:gain_not_0')
        check(start_samples==cursor and end_samples==cursor+meta['sample_count'],f'{name}:record_sample_coverage')
        check(meta=={'sample_rate':48000,'channels':1,'sample_width_bytes':3,'sample_count':p['output_sample_count'],'compression_type':'NONE'},f'{name}:WAV_format')
        check(c['text']==selection['generation_text']==original['generation_text'],f'{name}:text_not_original_manifest')
        cliprows.append({'basename':name,'sequence':c['sequence'],'take':c['take'],'source_path':str(wav),'source_sha256':actualsha,'source_in_sample':0,'source_out_sample_exclusive':meta['sample_count'],'record_start_sample':start_samples,'record_end_sample_exclusive':end_samples,'full_source_duration_seconds':dur,'clip_gain_db':c['clip_gain_db'],'implied_speed':(c['source_end_seconds']-c['source_start_seconds'])/((c['end_frame']-c['start_frame'])/tl['fps']),'original_text_exact_match':c['text']==original['generation_text']})
        cursor+=meta['sample_count']
        if i:
            j=tl['joins'][i-1]; prev=tl['clips'][i-1]
            actualgap=c['start_frame']-prev['end_frame']
            check(j['outgoing']==prev['basename'] and j['incoming']==name,f'EP{ep}:join_names_{i}')
            check(close(j['timeline_frame'],c['start_frame']) and j['gap_frames']==0.0 and close(actualgap,0.0),f'EP{ep}:join_gap_{i}')
            check(j['full_source_edges_preserved'] is True,f'EP{ep}:join_edges_{i}')
            joinrows.append({'outgoing':prev['basename'],'incoming':name,'timeline_frame':c['start_frame'],'join_sample':start_samples,'declared_gap_frames':j['gap_frames'],'recomputed_gap_frames':actualgap,'recomputed_gap_samples':start_samples-cliprows[i-1]['record_end_sample_exclusive']})
    check(close(tl['duration_seconds'],cursor/SR),f'EP{ep}:timeline_total_duration')
    audits.append({'episode':ep,'timeline_name':tl['name'],'timeline_id':tl['id'],'track_name':tl['track_name'],'timeline_fps':tl['fps'],'clip_count':len(tl['clips']),'duration_seconds':cursor/SR,'sample_count':cursor,'clips':cliprows,'joins':joinrows})
check(len(all_seen)==24 and len(set(all_seen))==24 and set(all_seen)==set(pmi),'24_source_coverage')
check(len([x for x in audits for j in x['joins']])==21,'join_count_not_21')
if issues:
    (BASE/'Resolve_三条原速测试时间线_独立交叉核验_失败.json').write_text(json.dumps({'status':'FAIL','issues':issues,'evidence':evidence},ensure_ascii=False,indent=2),encoding='utf-8')
    raise RuntimeError('\n'.join(issues))

previews=[]
for a in audits:
    ep=a['episode']; dest=OUT/f'女版EP{ep:02d}_原速旁白测试试听.wav'
    concat=OUT/f'女版EP{ep:02d}_同源同序.ffconcat'
    paths=[x['source_path'] for x in a['clips']]
    content='ffconcat version 1.0\n'+''.join("file '"+p.replace("'","'\\''")+"'\n" for p in paths)
    concat.write_text(content,encoding='utf-8')
    command=[str(FFMPEG),'-hide_banner','-nostdin','-v','error','-xerror','-n','-f','concat','-safe','0','-i',str(concat),'-map','0:a:0','-c:a','copy','-map_metadata','-1','-fflags','+bitexact',str(dest)]
    if dest.exists(): raise FileExistsError(f'Refuse replacing preexisting preview: {dest}')
    run=subprocess.run(command,capture_output=True,text=True)
    if run.returncode: raise RuntimeError(run.stderr)
    om,ob=wave_data(dest)
    assert om=={'sample_rate':48000,'channels':1,'sample_width_bytes':3,'sample_count':a['sample_count'],'compression_type':'NONE'},(dest,om)
    source_payload=b''.join(wave_cache[x['basename']][1] for x in a['clips'])
    assert ob==source_payload, f'PCM payload not exactly concatenated: {dest}'
    offset=0; regions=[]
    for row in a['clips']:
        m,pcm=wave_cache[row['basename']]
        length=len(pcm); region=ob[offset:offset+length]
        assert region==pcm
        regions.append({'basename':row['basename'],'source_pcm_payload_sha256':hashlib.sha256(pcm).hexdigest(),'preview_region_payload_sha256':hashlib.sha256(region).hexdigest(),'preview_start_sample':offset//3,'sample_count':m['sample_count'],'byte_identical':True})
        offset+=length
    joinwindows=[]
    for j in a['joins']:
        sample=j['join_sample']; s=max(0,sample-4800); e=min(om['sample_count'],sample+4800)
        actual=ob[s*3:e*3]; expected=source_payload[s*3:e*3]
        assert actual==expected
        joinwindows.append({'sample':sample,'window_start_sample':s,'window_end_sample_exclusive':e,'window_ms_each_side':100,'expected_sha256':hashlib.sha256(expected).hexdigest(),'actual_sha256':hashlib.sha256(actual).hexdigest(),'byte_identical':True})
    dec=subprocess.run([str(FFMPEG),'-hide_banner','-nostdin','-v','error','-xerror','-i',str(dest),'-map','0:a:0','-f','null','-'],capture_output=True,text=True)
    assert dec.returncode==0,dec.stderr
    probe=subprocess.run([str(FFPROBE),'-v','error','-show_streams','-show_format','-of','json',str(dest)],capture_output=True,text=True,check=True)
    pd=json.loads(probe.stdout); st=pd['streams'][0]
    assert st['codec_name']=='pcm_s24le' and st['sample_rate']=='48000' and st['channels']==1 and st['bits_per_sample']==24
    previews.append({'episode':ep,'path':str(dest),'sha256':sha(dest),'file_bytes':dest.stat().st_size,'sample_count':om['sample_count'],'duration_seconds':om['sample_count']/SR,'sample_rate':48000,'channels':1,'bits_per_sample':24,'codec':'pcm_s24le','concat_file':str(concat),'concat_sha256':sha(concat),'ffmpeg_arguments':command,'processing':'concat demuxer plus PCM stream copy; no audio filter, resampling, normalization, fade, time stretch, trim or padding','entire_pcm_payload_equals_concatenated_sources':True,'pcm_payload_sha256':hashlib.sha256(ob).hexdigest(),'full_ffmpeg_decode_returncode':dec.returncode,'source_regions':regions,'join_windows':joinwindows,'not_Resolve_bus_render':True,'human_listening_verified':False})
    print(f'EP{ep:02d} PASS {om["sample_count"]} samples {om["sample_count"]/SR:.3f}s',flush=True)

# Final immutable-input reread. No source files are changed by concat or validation.
for p,h in evidence.items(): assert sha(p)==h,f'Input JSON changed during review: {p}'
for p in pm['items']:
    assert sha(p['output_path'])==p['output_sha256']
    assert sha(p['source_path'])==p['source_sha256']
result={'status':'PASS_THREE_TIMELINE_JSON_CROSSCHECK_AND_SAMPLE_EXACT_OFFLINE_PREVIEWS','checked_at':datetime.now().astimezone().isoformat(),'scope':'Read-only crosscheck of saved Resolve_组装回读.json against immutable PCM/source/text manifests; no Resolve or UI calls. Preview WAVs use the same native-edit PCM source order, no Resolve bus render and no human listening certification.','input_evidence_sha256':evidence,'all24_source_paths_SHA_full_source_zero_inpoint_and_order_match':True,'all24_original_text_exact_match':True,'all24_source_and_PCM_files_unchanged':True,'timeline_count':3,'clip_count':24,'join_count':21,'all_join_gaps_zero':True,'all_pcm_payload_bytes_exact':True,'original_speed_implied_by_full_source_and_record_duration':True,'total_sample_count':sum(x['sample_count'] for x in previews),'total_duration_seconds':sum(x['sample_count'] for x in previews)/SR,'timelines':audits,'previews':previews,'issues':[],'limitations':['No new application readback was performed by this reviewer; platform state evidence is the supplied saved readback JSON.','The offline previews reproduce the approved PCM sequence only, not Resolve bus processing or monitoring.','No human auditory listening check has been claimed.']}
report=BASE/'Resolve_三条原速测试时间线_独立交叉核验.json'
report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md=['# 女版04—06原速测试时间线独立交叉核验与试听','','三条时间线保存回读JSON与24份PCM清单、最终采用清单及原文分段清单一致。集数、顺序、4个02采用版本、完整源入点0、片段时长、0dB片段增益及21个无缝接点全部通过；按源时长和时间线时长推导为100%原速。实际24源文件SHA与清单一致，未修改原音频。','','本报告只读核验父任务提供的原生组装回读JSON，没有再次连接Resolve或操作UI。试听WAV按与原生剪辑相同的24份PCM同源同序，用FFmpeg concat及PCM流复制制作；不是Resolve bus渲染，不代表人工核听完成。','','| 集数 | 时间线名称 | 段数 | 接点 | 48k样本数 | 秒 | 试听 |','|---|---|---:|---:|---:|---:|---|']
for a,p in zip(audits,previews): md.append(f'| {a["episode"]:02d} | {a["timeline_name"]} | {a["clip_count"]} | {len(a["joins"])} | {a["sample_count"]} | {a["duration_seconds"]:.3f} | [{Path(p["path"]).name}]({p["path"]}) |')
md+=['',f'总计24段、21个接点、{result["total_sample_count"]}个48k样本，{result["total_duration_seconds"]:.3f}秒。','', '试听格式48kHz/24bit/mono；未再次应用增益、重采样、音效、淡化、变速、剪时长或补时长。每份试听的全部PCM负载与对应源PCM按序拼接逐字节相等；每个接点前后各100毫秒及每个完整源区域亦逐字节一致，样本总数严格相等。完整FFmpeg解码和实际文件格式回读通过。','',f'详细文件SHA、逐段映射、21个接点窗口哈希与执行参数见[{report.name}]({report})。']
(BASE/'Resolve_三条原速测试时间线_独立交叉核验.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
(OUT/'试听清单.json').write_text(json.dumps({'status':'PASS_SAMPLE_EXACT_CONCAT','report_path':str(report),'report_sha256':sha(report),'previews':previews,'not_Resolve_bus_render':True,'human_listening_verified':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('REPORT',report,sha(report),flush=True)
