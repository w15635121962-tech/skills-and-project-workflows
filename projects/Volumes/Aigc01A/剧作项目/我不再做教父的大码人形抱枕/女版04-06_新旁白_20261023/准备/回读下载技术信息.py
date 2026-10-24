import csv,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROGRESS=ROOT/'制作进度.json'
BIN=Path('/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin')
p=json.loads(PROGRESS.read_text(encoding='utf-8'))
for x in p['items']+p.get('alternate_versions',[]):
    if not x.get('audio_file') or x.get('technical_decode')=='passed':continue
    f=Path(x['audio_file']);b=f.read_bytes();sha=hashlib.sha256(b).hexdigest()
    assert sha==x['audio_sha256'] and len(b)==x['audio_bytes'],x['basename']
    z=subprocess.run([str(BIN/'ffprobe'),'-v','error','-show_format','-show_streams','-of','json',str(f)],capture_output=True,text=True,check=True)
    info=json.loads(z.stdout);audio=[s for s in info['streams'] if s.get('codec_type')=='audio'];assert audio
    d=subprocess.run([str(BIN/'ffmpeg'),'-v','error','-i',str(f),'-map','0:a','-f','null','-'],capture_output=True,text=True,check=True)
    status='downloaded_verified_technical' if x.get('take',1)==1 else 'downloaded_existing_variant_technical_verified_pending_content_review'
    x.update(duration_seconds=float(info['format']['duration']),audio_streams=audio,technical_decode='passed',status=status,model=p['model'])
    if x.get('take',1)>1:
        (f.parent/(x['basename']+'_记录.json')).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
p['downloaded_count']=sum(bool(x.get('audio_file')) for x in p['items'])
p['technical_verified_count']=sum(x.get('technical_decode')=='passed' for x in p['items'])
PROGRESS.write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
cols=['basename','episode','narration_sequence','status','voice','model','submitted_at','downloaded_at','download_original_filename','audio_file','audio_bytes','audio_sha256','duration_seconds','platform_record_label']
with (ROOT/'制作进度.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');w.writeheader();w.writerows(p['items'])
print(json.dumps({'downloaded':p['downloaded_count'],'decoded':p['technical_verified_count'],'items':[{'name':x['basename'],'seconds':x.get('duration_seconds')} for x in p['items'] if x.get('audio_file')]},ensure_ascii=False))
