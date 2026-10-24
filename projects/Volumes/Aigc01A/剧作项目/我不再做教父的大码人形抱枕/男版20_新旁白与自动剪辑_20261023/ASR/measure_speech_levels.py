"""Read-only source PCM loudness/true-peak measurements. No gain is applied.

Measures downloaded EP20 VO plus all eight source-dialogue units, using word
boundaries with a short pad. Recommendations attenuate only, never normalize
destructively, change rate, replace a voice, or connect to Resolve.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import datetime as dt
import hashlib
import json
import math
import re
import subprocess

HERE=Path(__file__).resolve().parent
TASK=HERE.parent
FF='/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffmpeg'
OUT=HERE/'speech_levels'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def last(pattern,text):
    values=re.findall(pattern,text,re.M)
    return float(values[-1])if values and values[-1]not in ['-inf','inf','nan']else None

def one(row):
    path=Path(row['source_path']);digest=sha(path)
    key=row['id'];target=OUT/(key+'.json')
    if target.exists():
        old=json.loads(target.read_text(encoding='utf-8'))
        if old['source_sha256']==digest and old['start_seconds']==row['start_seconds']and old['end_seconds']==row['end_seconds']:
            return old
    start=row['start_seconds'];end=row['end_seconds']
    filters='atrim=start=%.9f:end=%.9f,asetpts=PTS-STARTPTS,ebur128=peak=true,volumedetect'%(start,end)
    result=subprocess.run([FF,'-nostdin','-hide_banner','-nostats','-i',str(path),'-vn','-af',filters,'-f','null','-'],capture_output=True,text=True,encoding='utf-8',timeout=120)
    assert result.returncode==0,result.stderr[-1500:]
    assert sha(path)==digest,'Source modified during level measurement'
    log=OUT/(key+'.log');log.parent.mkdir(parents=True,exist_ok=True);log.write_text(result.stderr,encoding='utf-8')
    rec=dict(**row,source_sha256=digest,analysis_log=str(log),
        integrated_loudness_lufs=last(r'^\s*I:\s*([-+\d.inf]+)\s*LUFS',result.stderr),
        true_peak_dbtp=last(r'^\s*Peak:\s*([-+\d.inf]+)\s*dBFS',result.stderr),
        mean_volume_dbfs=last(r'mean_volume:\s*([-+\d.inf]+)\s*dB',result.stderr),
        sample_peak_dbfs=last(r'max_volume:\s*([-+\d.inf]+)\s*dB',result.stderr),
        source_files_modified=False,gain_applied=False,speed_percent=100,human_listening_verified=False)
    limits=[0.0]
    if rec['true_peak_dbtp']is not None:limits.append(-2.0-rec['true_peak_dbtp'])
    if rec['integrated_loudness_lufs']is not None:limits.append(-18.0-rec['integrated_loudness_lufs'])
    rec['conservative_gain_db']=round(min(limits),2)
    rec['estimated_lufs_after_suggested_gain']=None if rec['integrated_loudness_lufs']is None else round(rec['integrated_loudness_lufs']+rec['conservative_gain_db'],2)
    rec['estimated_true_peak_after_suggested_gain']=None if rec['true_peak_dbtp']is None else round(rec['true_peak_dbtp']+rec['conservative_gain_db'],2)
    save(target,rec);return rec

def main():
    units=json.loads((HERE/'EP20_\u539f\u5bf9\u767d\u4e0e\u6e90\u65f6\u7801\u5019\u9009.json').read_text(encoding='utf-8'))['dialogue_units']
    rows=[]
    for unit in units:
        candidates=unit['source_candidates']
        # Approved continuity draft uses male white-T insert3-2 for P554 and
        # female-only main3-1 for P557; never substitute by filename recency.
        filename='\u7537\u724820-3-2.mp4'if unit['docx_paragraph']==554 else None
        c=next((c for c in candidates if Path(c['source_path']).name==filename),candidates[0])
        rows.append(dict(id='P%d_%s'%(unit['docx_paragraph'],Path(c['source_path']).stem),kind='source_dialogue',docx_paragraph=unit['docx_paragraph'],canonical_text=unit['original_text'],source_path=c['source_path'],start_seconds=max(0,c['start_seconds']-.15),end_seconds=c['end_seconds']+.18))
    narration_path=HERE/'narration_index.json'
    if narration_path.exists():
        for row in json.loads(narration_path.read_text(encoding='utf-8'))['files']:
            raw=json.loads(Path(row['json_path']).read_text(encoding='utf-8'))
            rows.append(dict(id=Path(row['source_path']).stem+'_full',kind='new_narration',sequence=row['sequence'],source_path=row['source_path'],start_seconds=0,end_seconds=raw['decoded_duration_seconds']))
    results=[];errors=[]
    with ThreadPoolExecutor(max_workers=2)as pool:
        futures={pool.submit(one,row):row for row in rows}
        for future in as_completed(futures):
            try:results.append(future.result())
            except Exception as exc:errors.append(dict(row=futures[future],error=str(exc)))
    results.sort(key=lambda x:(0 if x['kind']=='new_narration'else 1,x.get('sequence',x.get('docx_paragraph',0))))
    report=dict(measured_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),files=results,errors=errors,
                source_dialogue_units=8,new_narration_files=sum(x['kind']=='new_narration'for x in results),
                method='Original source decode; EBU R128 integrated LUFS and true peak before volumedetect conversion; dialogue word window plus150ms head/180ms tail pad.',
                recommendation='Conservative attenuation only: min(0,-18LUFS-I,-2dBTP-TP). No upward gain, limiter or rate change applied.',
                source_files_modified=False,gain_applied=False,human_listening_verified=False,
                limits=['Short dialogue LUFS can differ from a full narration segment because of delivery and natural pauses.','Peak/loudness diagnostics do not prove absence of background speech/music.','Final balancing requires actual native timeline listening; these recommendations are not automatic replacement audio.'])
    save(HERE/'speech_levels.json',report)
    print(json.dumps(dict(output=str(HERE/'speech_levels.json'),new_narration_files=report['new_narration_files'],dialogue_units=8,errors=errors),ensure_ascii=False),flush=True)
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
