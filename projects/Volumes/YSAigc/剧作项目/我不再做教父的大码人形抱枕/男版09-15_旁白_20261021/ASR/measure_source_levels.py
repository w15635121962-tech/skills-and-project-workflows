"""Offline read-only original video stream loudness analysis, no audio altered."""
import datetime,hashlib,json,re,subprocess,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
BASE=Path(__file__).resolve().parent
FF=Path('/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffmpeg')
INVENTORY=BASE.parent/'剪辑素材只读核查_20261022.json'
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def last(pattern,text):
 x=re.findall(pattern,text,re.MULTILINE)
 return float(x[-1]) if x and x[-1] not in ['-inf','inf','nan'] else None
def one(row):
 p=Path(row['path']);h=digest(p);started=time.monotonic()
 cmd=[str(FF),'-nostdin','-hide_banner','-nostats','-i',str(p),'-vn','-af','ebur128=peak=true,volumedetect','-f','null','-']
 q=subprocess.run(cmd,capture_output=True,text=True,timeout=180)
 assert q.returncode==0,q.stderr[-1000:]
 assert digest(p)==h,'Source changed'
 folder=BASE/'source_levels'/f"EP{row['episode']}";folder.mkdir(parents=True,exist_ok=True)
 log=folder/(p.stem+'.log');log.write_text(q.stderr,encoding='utf-8')
 x=dict(source_path=str(p),filename=p.name,source_sha256=h,episode=row['episode'],kind='video',analysis_log=str(log),source_unchanged=True,gain_applied=False,
 integrated_loudness_lufs=last(r'^\s*I:\s*([-+\d.inf]+)\s*LUFS',q.stderr),true_peak_dbfs=last(r'^\s*Peak:\s*([-+\d.inf]+)\s*dBFS',q.stderr),loudness_range_lu=last(r'^\s*LRA:\s*([-+\d.inf]+)\s*LU',q.stderr),mean_volume_dbfs=last(r'mean_volume:\s*([-+\d.inf]+)\s*dB',q.stderr),max_volume_dbfs=last(r'max_volume:\s*([-+\d.inf]+)\s*dB',q.stderr))
 limits=[0]
 if x['true_peak_dbfs'] is not None:limits.append(-2-x['true_peak_dbfs'])
 if x['integrated_loudness_lufs'] is not None:limits.append(-18-x['integrated_loudness_lufs'])
 gain=round(min(limits),2)
 x.update(suggested_speech_gain_db=gain,suggested_ambience_under_vo_gain_db=min(gain,-12),runtime_seconds=round(time.monotonic()-started,3))
 return x
inv=json.loads(INVENTORY.read_text());rows=[dict(x,episode=ep['episode']) for ep in inv['episodes'] for x in ep['videos']]
finished=[];errors=[]
with ThreadPoolExecutor(max_workers=4) as pool:
 fs={pool.submit(one,row):row for row in rows}
 for f in as_completed(fs):
  try:finished.append(f.result())
  except Exception as e:errors.append(dict(source_path=fs[f]['path'],error=repr(e)))
  if (len(finished)+len(errors))%20==0:print(json.dumps(dict(completed=len(finished),errors=len(errors),total=len(rows))),flush=True)
result=dict(created_at=datetime.datetime.now().isoformat(),source_count=len(rows),completed=len(finished),errors=errors,source_files_not_modified=True,gain_not_applied=True,method='Original entire-stream EBU R128 and true-peak measurements before signed16 volumedetect conversion.',limitations=['Gain suggestions only; whole-stream loudness is not isolated dialogue loudness.','Do not mute or cut a real dialogue based on this report; allocate a narration-free interval and use same source bounds linked to video.','Music presence or absence and independent stem availability cannot be proven by these measurements.'],files=sorted(finished,key=lambda x:(x['episode'],x['filename'])))
p=BASE/'source_levels.json';p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(output=str(p),completed=len(finished),errors=len(errors))),flush=True)
assert len(finished)==104 and not errors
