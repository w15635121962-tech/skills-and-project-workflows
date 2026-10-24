#!/usr/bin/env python3
"""Re-download existing UI results in verified source/creation order, rename each immediately."""
import fcntl
import hashlib
import json
import shutil
import time
from pathlib import Path
import jimeng_narration_batch as base
import jimeng_download_guard as guard

P=Path(__file__).resolve().parent
REPORT=P/'按文本顺序重新下载记录.json'

def save(p,d):
    t=p.with_suffix('.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');t.replace(p)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    with (P/'.jimeng_narration_queue.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        m=json.loads(base.MANIFEST.read_text());j=json.loads(base.JOURNAL.read_text())
        plan=json.loads(base.PLAN.read_text())
        report=json.loads(REPORT.read_text()) if REPORT.exists() else {'started_at':time.time(),'order':'English narration source order and observed generated record order','clips':[]}
        groups=[g for g in plan['groups'] if g['version']=='女版' and g['episode']==1]
        rows={(r['version'],r['name']):r for r in m['clips']}
        # Verify the observed first result has exactly the known narration source.
        state=base.snapshot()
        if 'workspace=23561838050060' not in state['url']:raise RuntimeError('Unexpected workspace')
        records=state['records']
        for g in groups:
            r=rows[(g['version'],g['name'])]
            found=[x for x in records if base.norm(r['text']) in base.norm(x['text']) and r['voice_name'] in x['text']]
            if len(found)>1:raise RuntimeError('Ambiguous text/voice record for '+g['name'])
            if found:
                key=found[0]['key']
                if r.get('record_key') and r['record_key']!=key:raise RuntimeError('Record provenance mismatch')
                r['record_key']=key
            if not r.get('record_key'):raise RuntimeError('Missing record provenance for '+g['name'])
        keys=[rows[(g['version'],g['name'])]['record_key'] for g in groups]
        actual=[x['key'] for x in records if x['key'] in keys]
        if actual!=[key for key in keys if key in actual]:raise RuntimeError('Creation order differs from source mapping')
        save(base.MANIFEST,m)
        done={x['name'] for x in report['clips']}
        for position,g in enumerate(groups,1):
            if g['name'] in done:continue
            r=rows[(g['version'],g['name'])];key=r['record_key']
            # Bring virtualized records into view using structured UI actions.
            for attempt in range(12):
                state=base.snapshot()
                rec=next((x for x in state['records'] if x['key']==key),None)
                if rec and rec['cards']:break
                known=[x for x in state['records'] if x['key'] in keys]
                if not known:raise RuntimeError('No known records available for structured scroll')
                target_index=keys.index(key)
                direction='up' if target_index < min(keys.index(x['key']) for x in known) else 'down'
                anchor=known[0] if direction=='up' else known[-1]
                anchor_selector=f'[data-generated-record-key="{anchor["key"]}"]'
                base.cli('find','--css',anchor_selector,'--limit','1','--text-max','50')
                base.cli('hover',anchor_selector)
                base.cli('scroll',direction,'--amount','2500')
                time.sleep(0.5)
            else:raise RuntimeError('Target virtual record did not load')
            selector=f'[data-generated-record-key="{key}"]'
            base.cli('find','--css',selector,'--limit','1','--text-max','100')
            base.cli('hover',selector)
            state=base.snapshot();rec=next(x for x in state['records'] if x['key']==key)
            if base.norm(r['text']) not in base.norm(rec['text']) or r['voice_name'] not in rec['text']:raise RuntimeError('Text/voice mapping changed')
            c=guard.download_candidate(base,key,r['selected_candidate']-1,group_name=g['name'],version=g['version'],rename_dir=Path('/Users/xuan/Downloads'),replace_existing=True,existing_metadata=r)
            # Rename is complete before copying to the selected project folder.
            src=Path(c['download_path']);out=Path(r['local_path'])
            report['current_download']={'name':g['name'],'download':c,'project_path':str(out)};save(REPORT,report)
            out.parent.mkdir(parents=True,exist_ok=True)
            if out.is_file() and digest(out)!=r['sha256']:raise RuntimeError('Existing project source changed')
            if not out.exists():shutil.copy2(src,out)
            if digest(out)!=c['sha256']:
                backup=P/'重新下载旧文件备份'/g['name'];backup.mkdir(parents=True,exist_ok=True)
                shutil.copy2(out,backup/out.name)
                tmp=out.with_name(out.name+'.redownload.tmp');shutil.copy2(src,tmp);tmp.replace(out)
            if digest(out)!=c['sha256']:raise RuntimeError('Copied bytes differ')
            previous={k:r.get(k) for k in ['downloaded_candidates','download_source','duration_seconds','sha256']}
            r.update(downloaded_candidates=[c],download_source=str(src),duration_seconds=c['duration_seconds'],sha256=c['sha256'],redownloaded_at=time.time(),source_order=position,creation_order_verified=True)
            save(base.MANIFEST,m)
            entry=j.setdefault(f"{g['version']}/{g['name']}",{})
            entry.update(status='downloaded',text=r['text'],voice=r['voice_name'],record_key=key,local_path=str(out),selected_candidate=r['selected_candidate'],downloaded_candidates=[c],redownloaded_at=r['redownloaded_at'])
            save(base.JOURNAL,j)
            item={'position':position,'name':g['name'],'text':r['text'],'record_key':key,'selected_candidate':r['selected_candidate'],'download':c,'project_path':str(out),'sha256':r['sha256'],'previous':previous}
            report['clips'].append(item);report.pop('current_download',None);save(REPORT,report)
            print(json.dumps({'redownloaded':g['name'],'order':position,'renamed_download':str(src),'copied_to':str(out),'duration':c['duration_seconds']},ensure_ascii=False),flush=True)
            if c.get('viewer_return_error'):raise RuntimeError(c['viewer_return_error'])
        report['completed_at']=time.time();save(REPORT,report)
        print(json.dumps({'complete':True,'redownloaded_count':len(report['clips'])}),flush=True)
if __name__=='__main__':
    try:main()
    except Exception as e:
        print(json.dumps({'stopped':str(e),'no_new_generation':True},ensure_ascii=False),flush=True)
        raise SystemExit(1)
