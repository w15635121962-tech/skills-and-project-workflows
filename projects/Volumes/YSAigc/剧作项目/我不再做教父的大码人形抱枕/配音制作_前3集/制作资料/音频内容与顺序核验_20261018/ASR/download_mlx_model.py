#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Download one pinned public MLX model with resumable anonymous ranges."""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import math
import ssl
import urllib.request
from pathlib import Path

BASE=Path(__file__).resolve().parent
CTX=ssl.create_default_context(cafile='/etc/ssl/cert.pem')


def get_json(url):
    with urllib.request.urlopen(url,context=CTX,timeout=45) as response:return json.load(response)


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda:source.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def fetch(job):
    url,path,start,end,total=job
    if path.is_file() and path.stat().st_size==end-start+1:return end-start+1
    last=None
    for attempt in range(3):
        try:
            request=urllib.request.Request(url,headers={'Range':f'bytes={start}-{end}'})
            with urllib.request.urlopen(request,context=CTX,timeout=90) as response:
                expected=f'bytes {start}-{end}/{total}'
                if response.status!=206 or response.headers.get('Content-Range')!=expected:
                    raise RuntimeError(f'Unexpected range response: {response.status}, {response.headers.get("Content-Range")}')
                data=response.read()
            if len(data)!=end-start+1:raise RuntimeError('Partial download length differs.')
            temp=path.with_suffix('.tmp');temp.write_bytes(data);temp.replace(path)
            return len(data)
        except Exception as exc:last=exc
    raise last


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model',choices=['medium.en','large-v3-turbo'],required=True)
    parser.add_argument('--workers',type=int,default=8)
    args=parser.parse_args()
    repo={'medium.en':'mlx-community/whisper-medium.en-mlx','large-v3-turbo':'mlx-community/whisper-large-v3-turbo'}[args.model]
    info=get_json(f'https://huggingface.co/api/models/{repo}?blobs=true');revision=info['sha']
    root=BASE/'models'/args.model;model=root/'weights';model.mkdir(parents=True,exist_ok=True)
    files=[item for item in info['siblings'] if item['rfilename'] in ('config.json','weights.npz','weights.safetensors')]
    jobs=[];chunk=8*1024*1024
    for item in files:
        path=model/item['rfilename'];url=f'https://huggingface.co/{repo}/resolve/{revision}/{item["rfilename"]}'
        if item['size']<chunk:
            with urllib.request.urlopen(url,context=CTX,timeout=45) as response:path.write_bytes(response.read())
            continue
        expected=item['lfs']['sha256']
        if path.is_file() and digest(path)==expected:continue
        parts=path.with_name(path.name+'.parts');parts.mkdir(exist_ok=True)
        for index in range(math.ceil(item['size']/chunk)):
            start=index*chunk;end=min(item['size']-1,start+chunk-1)
            jobs.append((url,parts/f'{index:05d}.part',start,end,item['size']))
    print(json.dumps({'model_download_start':repo,'revision':revision,'bytes':sum(x['size'] for x in files),'parts':len(jobs),'workers':args.workers}),flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures=[executor.submit(fetch,job) for job in jobs]
        count=0
        for index,future in enumerate(concurrent.futures.as_completed(futures),1):
            count+=future.result()
            if index%8==0 or index==len(futures):print(json.dumps({'parts_ready':index,'total_parts':len(futures),'bytes_ready':count}),flush=True)
    for item in files:
        path=model/item['rfilename']
        if not path.is_file():
            temporary=path.with_name(path.name+'.assembling')
            with temporary.open('wb') as target:
                for part in sorted(path.with_name(path.name+'.parts').glob('*.part')):
                    with part.open('rb') as source:
                        for block in iter(lambda:source.read(1024*1024),b''):target.write(block)
            temporary.replace(path)
        if path.stat().st_size!=item['size'] or (item.get('lfs') and digest(path)!=item['lfs']['sha256']):
            raise RuntimeError(f'Official model SHA/size verification failed: {path}')
    metadata={'engine':'mlx-whisper','model':args.model,'repo_id':repo,'revision':revision,
              'downloaded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'local_model_path':str(model),'engine_primary_documentation':'https://github.com/ml-explore/mlx-examples/tree/main/whisper',
              'model_primary_source':f'https://huggingface.co/{repo}/tree/{revision}',
              'files':[{'path':item['rfilename'],'bytes':item['size'],'sha256':digest(model/item['rfilename'])} for item in files]}
    (root/'provenance.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'model_ready':True,'repo':repo,'revision':revision}),flush=True)


if __name__=='__main__':main()
