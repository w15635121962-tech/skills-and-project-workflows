from pathlib import Path
import hashlib,json

BASE=Path(__file__).resolve().parent.parent
manifest=BASE.parent/'Resolve_组装实读.json'
raw=manifest.read_bytes();m=json.loads(raw)
idx=json.loads((BASE/'转录索引.json').read_text())
vo_bank={}
for row in idx['files']:
    if row['kind']=='narration':vo_bank[row['source_path']]=json.loads(Path(row['json_path']).read_text())['words']
sr=json.loads((BASE/'speech_ranges.json').read_text());speech={}
for row in sr['ranges']:
    if row['auto_use_candidate']:speech.setdefault(row['source_path'],[]).extend(row['words'])
for row in idx['files']:
    if row['kind']=='video' and row['episode']==25 and Path(row['source_path']).name=='男版25-11-1.mp4':speech[row['source_path']]=json.loads(Path(row['json_path']).read_text())['words']
def mapped(row,words,fps):
    a=row['source_start']/fps;b=a+(row['end']-row['start'])/fps;rec=row['start']/fps
    return [(rec+max(a,w['start'])-a,rec+min(b,w['end'])-a,w['word']) for w in words if w.get('probability',1)>=.6 and min(b,w['end'])>max(a,w['start'])]
reports=[]
for ep in m['episodes']:
    fps=ep['fps'];vo=[]
    for row in ep['narration']:
        if row.get('enabled',True):vo.extend(mapped(row,vo_bank[row['path']],fps))
    hits=[]
    for row in ep['sync_audio']:
        if not row.get('enabled',True) or row['path'] not in speech:continue
        for a,b,w in mapped(row,speech[row['path']],fps):
            overlap=[(max(a,x),min(b,y),v) for x,y,v in vo if min(b,y)-max(a,x)>.03]
            total=sum(y-x for x,y,v in overlap)
            if total>.08:hits.append(dict(sync_clip_id=row['id'],source=row['path'],gain_db=row['gain_db'],word=w,record_start=a,record_end=b,overlap_seconds=total,vo_words=[v for x,y,v in overlap]))
    reports.append(dict(episode=ep['episode'],automatic_overlap_candidates=hits,count=len(hits)))
out=dict(input_manifest=str(manifest),input_manifest_sha256=hashlib.sha256(raw).hexdigest(),method='ASR>=0.6 source-word time intervals mapped through native source_start and exact end-start; candidate only, not audition',human_listening_validated=False,episodes=reports)
(Path(__file__).resolve().parent/'word_interval_overlap_qc.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps([{k:r[k] for k in ['episode','count']} for r in reports]))
