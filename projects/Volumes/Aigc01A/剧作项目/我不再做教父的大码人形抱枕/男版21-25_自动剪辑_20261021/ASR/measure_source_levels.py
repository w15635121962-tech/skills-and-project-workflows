from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import datetime,hashlib,json,re,subprocess,time

BASE=Path(__file__).resolve().parent
FF=Path('/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffmpeg')
INDEX=json.loads((BASE/'转录索引.json').read_text())
OUT=BASE/'source_levels';OUT.mkdir(exist_ok=True)

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def last(pattern,s):
    a=re.findall(pattern,s,re.M)
    if not a:return None
    v=a[-1]
    return None if v in ('-inf','inf','nan') else float(v)
def one(row):
    p=Path(row['source_path']);start=time.monotonic()
    if sha(p)!=row['source_sha256']:raise RuntimeError('Source changed before analysis: '+str(p))
    cmd=[str(FF),'-nostdin','-hide_banner','-nostats','-i',str(p),'-vn','-af','volumedetect,ebur128=peak=true','-f','null','-']
    cp=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
    if cp.returncode:raise RuntimeError(cp.stderr[-2000:])
    if sha(p)!=row['source_sha256']:raise RuntimeError('Source changed during analysis: '+str(p))
    log=cp.stderr
    target=OUT/f"EP{row['episode']}"/row['kind'];target.mkdir(parents=True,exist_ok=True)
    logfile=target/(p.stem+'.log');logfile.write_text(log)
    return dict(source_path=str(p),source_sha256=row['source_sha256'],episode=row['episode'],kind=row['kind'],source_duration_seconds=row['decoded_duration_seconds'],
                mean_volume_dbfs=last(r'mean_volume:\s*([-+\d.inf]+)\s*dB',log),
                max_volume_dbfs=last(r'max_volume:\s*([-+\d.inf]+)\s*dB',log),
                integrated_loudness_lufs=last(r'^\s*I:\s*([-+\d.inf]+)\s*LUFS',log),
                loudness_range_lu=last(r'^\s*LRA:\s*([-+\d.inf]+)\s*LU',log),
                true_peak_dbfs=last(r'^\s*Peak:\s*([-+\d.inf]+)\s*dBFS',log),
                analysis_log_path=str(logfile),runtime_seconds=round(time.monotonic()-start,3),source_unchanged=True,gain_applied=False,muted=False)

rows=INDEX['files'];results=[];errors=[]
with ThreadPoolExecutor(max_workers=4) as ex:
    futures=[ex.submit(one,r) for r in rows]
    for j,(row,f) in enumerate(zip(rows,futures),1):
        try:results.append(f.result())
        except Exception as e:errors.append(dict(source_path=row['source_path'],error=str(e)))
        if j%10==0 or j==len(rows):print(json.dumps(dict(completed=j,total=len(rows),errors=len(errors)),ensure_ascii=False),flush=True)
results.sort(key=lambda r:(r['episode'],r['kind'],r['source_path']))
def distribution(rs,key):
    a=sorted(r[key] for r in rs if r[key] is not None)
    return dict(count=len(a),minimum=a[0],median=(a[len(a)//2] if len(a)%2 else (a[len(a)//2-1]+a[len(a)//2])/2),maximum=a[-1]) if a else dict(count=0)
summary={}
for kind in ('video','narration'):
    rs=[r for r in results if r['kind']==kind]
    summary[kind]={k:distribution(rs,k) for k in ('mean_volume_dbfs','max_volume_dbfs','integrated_loudness_lufs','true_peak_dbfs')}
output=dict(created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),method='FFmpeg volumedetect + EBU R128 true-peak measurement over each entire original audio stream',
            source_count=len(rows),completed=len(results),errors=errors,source_audio_rewritten=False,source_volume_changed=False,source_audio_muted=False,
            cautions=['Whole-source loudness includes original environment/music/gaps; it is not isolated dialogue loudness.','Volume measurements do not confirm words, sync, speaker identity or mix quality.','No normalization or muting has been applied; levels are measurements only.'],
            distributions=summary,files=results)
(BASE/'source_levels.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(output=str(BASE/'source_levels.json'),completed=len(results),errors=len(errors),distributions=summary),ensure_ascii=False),flush=True)
if errors:raise SystemExit(1)
