#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Anonymous downloads from official PyPI/HF files; resume parts and verify SHA256."""
import concurrent.futures
import hashlib
import json
import math
import ssl
import urllib.request
from pathlib import Path
from pip._vendor.packaging.tags import sys_tags
from pip._vendor.packaging.utils import parse_wheel_filename

BASE = Path(__file__).resolve().parent
CTX = ssl.create_default_context(cafile='/etc/ssl/cert.pem')
PACKAGES = {
    'mlx-whisper':'0.4.3','mlx':'0.32.4','mlx-metal':'0.32.4','numba':'0.68.0',
    'numpy':'2.5.4','tqdm':'4.70.1','more-itertools':'11.2.1',
    'tiktoken':'0.14.0','huggingface-hub':'2.2.0','scipy':'1.18.1','click':'8.5.0',
    'filelock':'4.2.1','fsspec':'2026.9.0','hf-xet':'1.7.0','httpx2':'2.13.1',
    'packaging':'26.3','pyyaml':'6.0.3','typing-extensions':'4.16.0','llvmlite':'0.50.0',
    'regex':'2026.9.29','requests':'2.34.2','setuptools':'84.0.0',
    'anyio':'4.15.1','httpcore2':'2.13.1',
    'idna':'3.20','truststore':'0.10.5','h11':'0.16.0',
    'charset-normalizer':'3.5.2','urllib3':'2.8.0','certifi':'2026.7.22',
}


def get_json(url):
    with urllib.request.urlopen(url, context=CTX, timeout=45) as response:
        return json.load(response)


def digest(path):
    result=hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda:source.read(1024*1024), b''):
            result.update(chunk)
    return result.hexdigest()


TAGS = {tag:index for index,tag in enumerate(sys_tags())}
def package_info(pair):
    name,version=pair
    metadata=get_json(f'https://pypi.org/pypi/{name}/{version}/json')
    candidates=[]
    for item in metadata['urls']:
        if item['packagetype']!='bdist_wheel':continue
        try:tags=parse_wheel_filename(item['filename'])[3]
        except Exception:continue
        ranks=[TAGS[tag] for tag in tags if tag in TAGS]
        if ranks:candidates.append((min(ranks),item))
    if not candidates:raise RuntimeError(f'No compatible official wheel for {name}=={version}')
    item=min(candidates,key=lambda value:value[0])[1]
    return {'name':name,'version':version,'url':item['url'],'size':item['size'],
            'sha256':item['digests']['sha256'],'path':str(BASE/'dependency_wheels'/item['filename'])}


def fetch_part(job):
    url,part,start,end,full=job
    part=Path(part)
    if part.is_file() and part.stat().st_size==end-start+1:return
    error=None
    for attempt in range(3):
        try:
            request=urllib.request.Request(url,headers={} if full else {'Range':f'bytes={start}-{end}'})
            with urllib.request.urlopen(request,context=CTX,timeout=90) as response:
                data=response.read()
                if response.status!=(200 if full else 206) or len(data)!=end-start+1:
                    raise RuntimeError(f'Bad partial response {response.status}: {len(data)} vs {end-start+1}')
            part.write_bytes(data)
            return
        except Exception as exc:error=exc
    raise error


def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        packages=list(executor.map(package_info,PACKAGES.items()))
    (BASE/'official_wheel_metadata.json').write_text(json.dumps(packages,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'official_wheel_bytes':sum(x['size'] for x in packages),'files':len(packages)}),flush=True)
    repo='mlx-community/whisper-small.en-mlx'
    info=get_json(f'https://huggingface.co/api/models/{repo}?blobs=true')
    revision=info['sha']
    model_dir=BASE/'models/small.en/weights'
    model_dir.mkdir(parents=True,exist_ok=True)
    assets=[]
    for item in info['siblings']:
        name=item['rfilename']
        if name not in ('config.json','weights.npz'):continue
        assets.append({'name':name,'url':f'https://huggingface.co/{repo}/resolve/{revision}/{name}',
                       'size':item['size'],'sha256':item.get('lfs',{}).get('sha256'),
                       'path':str(model_dir/name)})
    records=packages+assets
    jobs=[]
    chunk=4*1024*1024
    for item in records:
        path=Path(item['path']);path.parent.mkdir(parents=True,exist_ok=True)
        if path.is_file() and (not item['sha256'] or digest(path)==item['sha256']):continue
        if item['size']<=chunk:
            jobs.append((item['url'],str(path),0,item['size']-1,True))
            continue
        parts=path.with_name(path.name+'.parts');parts.mkdir(exist_ok=True)
        for index in range(math.ceil(item['size']/chunk)):
            start=index*chunk;end=min(item['size']-1,start+chunk-1)
            jobs.append((item['url'],str(parts/f'{index:05d}.part'),start,end,False))
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures=[executor.submit(fetch_part,job) for job in jobs]
        for index,future in enumerate(concurrent.futures.as_completed(futures),1):
            future.result()
            if index%8==0 or index==len(futures):
                print(json.dumps({'parts_completed':index,'total_parts':len(futures)}),flush=True)
    for item in records:
        path=Path(item['path'])
        if not path.is_file():
            parts=path.with_name(path.name+'.parts')
            with path.open('wb') as target:
                for part in sorted(parts.glob('*.part')):
                    with part.open('rb') as source:
                        for block in iter(lambda:source.read(1024*1024),b''):target.write(block)
        if path.stat().st_size!=item['size'] or (item['sha256'] and digest(path)!=item['sha256']):
            raise RuntimeError(f'Final size/hash mismatch: {path}')
    provenance={'engine':'mlx-whisper','model':'small.en','repo_id':repo,'revision':revision,
                'local_model_path':str(model_dir),
                'engine_primary_documentation':'https://github.com/ml-explore/mlx-examples/tree/main/whisper',
                'model_primary_source':f'https://huggingface.co/{repo}/tree/{revision}',
                'files':[{'path':Path(item['path']).name,'bytes':item['size'],'sha256':digest(Path(item['path']))} for item in assets]}
    (model_dir.parent/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'download_complete':True,'wheel_count':len(packages),'model_revision':revision}),flush=True)


if __name__=='__main__':main()
