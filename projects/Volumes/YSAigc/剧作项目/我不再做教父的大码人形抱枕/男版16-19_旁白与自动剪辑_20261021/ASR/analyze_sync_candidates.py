from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,hashlib,subprocess,re,math
import numpy as np
BASE=Path(__file__).resolve().parent
FF='/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffmpeg'
inv=json.loads((BASE.parent/'准备/media_inventory.json').read_text(encoding='utf-8'))
probes={x['path']:x for e in inv['episodes'] for x in e['videos']}
index=json.loads((BASE/'转录索引.json').read_text(encoding='utf-8'))
# These candidate sources were selected after the blind recognition stage and
# source-frame review. They do not alter or feed any recognition prompt.
spoken={'男版17-5-1':[(0,24)],'男版19-1-1':[(0,3)],'男版19-2-1':[(0,15),(16,26),(27,30)],
        '男版19-2-2':[(0,15)],'男版19-3-1':[(0,29)],'男版19-3-2':[(0,29)],
        '男版19-4-1':[(0,14)],'男版19-4-2':[(0,14)]}
def db(v):return 20*math.log10(max(float(v),1e-12))
def one(row):
    p=Path(row['source_path']);d=json.loads(Path(row['json_path']).read_text(encoding='utf-8'))
    proc=subprocess.run([FF,'-v','error','-i',str(p),'-vn','-ac','1','-ar','16000','-f','f32le','pipe:1'],capture_output=True,check=True)
    a=np.frombuffer(proc.stdout,dtype='<f4');rms=db(np.sqrt(np.mean(a*a)+1e-24));pk=db(np.max(np.abs(a)))
    words=d['words'];tokens=[re.sub('[^a-z]','',w['word'].lower()) for w in words]
    counts={t:tokens.count(t) for t in set(tokens) if t}
    dominant=max(counts.values(),default=0)/max(1,len(tokens))
    name=p.stem
    cat='spoken_original_dialogue_candidate' if name in spoken else 'unapproved_asr_output_not_dialogue'
    why='Word timings and source scene support a spoken source line; still not claimed as human audition.' if name in spoken else 'Low confidence / repetitive ASR or nonlinguistic breath and environmental sound; do not convert raw output to captions or add it as dialogue.'
    if pk<-60:why='Near-silent audio signal does not support recognized text; raw ASR must not become captions.'
    ranges=[]
    for first,last in spoken.get(name,[]):
        ws=words[first:last+1];start=ws[0]['start'];end=ws[-1]['end'];frames=int(probes[str(p)]['video_streams'][0]['nb_frames'])
        inf=max(0,math.floor((start-.15)*24));outf=min(frames,math.ceil((end+.2)*24))
        ranges.append({'source_path':str(p),'source_sha256':d['source_sha256'],'episode':row['episode'],'source_fps':24,'first_word_index':first,'last_word_index':last,
            'recognized_text':''.join(w['word'] for w in ws).strip(),'source_in_frame':inf,'source_out_frame_exclusive':outf,'source_in_seconds':inf/24,'source_out_seconds':outf/24,
            'word_start_seconds':start,'word_end_seconds':end,'preserves_recognized_words':inf/24<=start and outf/24>=end,'words':ws,'human_listening_validated':False})
    return {'source_path':str(p),'filename':p.name,'source_sha256':d['source_sha256'],'episode':row['episode'],'source_duration_seconds':len(a)/16000,
        'rms_dbfs':rms,'peak_dbfs':pk,'classification':cat,'reason':why,'raw_recognized_text':d['text'],'quality_flags':d['quality_flags'],
        'mean_word_probability':sum(w.get('probability',0) for w in words)/len(words) if words else None,'repeated_word_fraction':dominant,'source_range_candidates':ranges}
with ThreadPoolExecutor(max_workers=4) as pool:files=list(pool.map(one,index['files']))
hashes={}
for f in files:hashes.setdefault(f['source_sha256'],[]).append(f['filename'])
out={'scope':'男版16–19，48原始视频离线ASR+音轨能量+接触图审查后的同期对白候选；不改源片或Resolve',
    'transcription_input_blind':True,'human_listening_validated':False,'files':files,
    'exact_duplicate_files':[v for v in hashes.values() if len(v)>1],
    'approved_dialogue_candidate_source_count':sum(f['classification']=='spoken_original_dialogue_candidate' for f in files),
    'limits':['英文原稿仅用于转录后比对，未给ASR热词或强制对齐。','非对白原片同期声仍应同画面同边界剪入，不能因无可辨对白删除音轨。','未认可ASR循环套话/嗯声为剧本台词。','EP18手机短信原稿是屏幕交流，不能擅自用叙述者朗读补成对白。','所有范围均为源秒/24fps帧边界，尚非最终时间线位置。']}
(BASE/'同期对白与音轨候选.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(BASE/'同期对白与音轨候选.json'),'source_count':len(files),'spoken_candidate_sources':out['approved_dialogue_candidate_source_count'],'exact_duplicate_files':out['exact_duplicate_files'],
    'levels':[{k:f[k] for k in ['filename','rms_dbfs','peak_dbfs','classification']} for f in files]},ensure_ascii=False))
