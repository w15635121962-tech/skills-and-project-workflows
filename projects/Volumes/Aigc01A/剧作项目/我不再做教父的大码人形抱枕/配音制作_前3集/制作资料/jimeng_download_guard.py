#!/usr/bin/env python3
"""Fresh-download validation and immediate source renaming; no generation calls.

Call download_candidate(base, key, index, group_name=..., version=...,
                        tied=False, rename_dir=Path.home() / 'Downloads').
All browser writes use backend.cli structured actions. Evaluations read DOM.
The caller owns copying to the project disk and journal/manifest updates.
"""
import hashlib
import json
import os
import re
import time
from pathlib import Path

_USED_IDS = set()


def _identity(path):
    stat = path.stat()
    return (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns)


def _known_ids(backend, explicit):
    ids = {str(value) for value in explicit if value is not None} | _USED_IDS
    def visit(value):
        if isinstance(value, dict):
            if value.get('download_id') is not None:
                ids.add(str(value['download_id']))
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
    for name in ('JOURNAL', 'MANIFEST'):
        path = getattr(backend, name, None)
        if path is not None and Path(path).is_file():
            visit(json.loads(Path(path).read_text()))
    return ids


def record_visibility(backend, record_key):
    """Read-only diagnostic for a virtual placeholder; caller handles scrolling."""
    selector = f'[data-generated-record-key="{record_key}"]'
    return backend.evaluate(f'''(() => {{
      const e=document.querySelector({json.dumps(selector)});
      if(!e)return {{present:false}};
      const r=e.getBoundingClientRect(), ancestors=[];
      for(let p=e.parentElement;p;p=p.parentElement){{
        const s=getComputedStyle(p),b=p.getBoundingClientRect();
        if(p.scrollHeight>p.clientHeight+4 && /auto|scroll/.test(s.overflowY))
          ancestors.push({{className:p.className,top:b.top,bottom:b.bottom,
            scrollTop:p.scrollTop,clientHeight:p.clientHeight,scrollHeight:p.scrollHeight}});
      }}
      return {{present:true,key:e.getAttribute('data-generated-record-key'),
        text:e.innerText,cards:e.querySelectorAll('.audio-card-container-x_138k').length,
        rect:{{top:r.top,bottom:r.bottom,height:r.height}},viewportHeight:innerHeight,
        scrollAncestors:ancestors}};
    }})()''')


def _open_viewer(backend, record_key, index):
    selector = (f'[data-generated-record-key="{record_key}"] '
                '.audio-card-container-x_138k .left-section-Phe0vo')
    pager = None
    for attempt in range(2):
        check = backend.evaluate(f'''(() => ({{
          cards:document.querySelectorAll({json.dumps(selector)}).length,
          pager:document.querySelector('.page-number-YYNlfP')?.innerText || ''
        }}))()''')
        if check['pager']:
            raise RuntimeError('A detail viewer was already open; return to the verified record list first.')
        if check['cards'] < 2:
            raise RuntimeError('Record cards are absent/virtual placeholders; '
                               'use structured scrolling and re-read the record before downloading.')
        backend.cli('click', selector, '--nth', index)
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            pager = backend.evaluate("(() => document.querySelector('.page-number-YYNlfP')?.innerText || '')()")
            if pager:
                break
            time.sleep(0.6)
        if pager:
            break
    if not pager:
        raise RuntimeError('Detail viewer did not open after at most two observed UI attempts.')
    actual = backend.cli('get', 'text', '.page-number-YYNlfP')['value']
    if int(actual.split('/')[0]) != index + 1:
        raise RuntimeError(f'Detail viewer selected unexpected candidate: {actual}')
    media = backend.evaluate('''(() => ({
      pager:document.querySelector('.page-number-YYNlfP')?.innerText || '',
      sources:Array.from(document.querySelectorAll('audio')).map(a=>({
        src:a.currentSrc||a.src||'',duration:Number.isFinite(a.duration)?a.duration:null
      })).filter(a=>a.src)
    }))()''')
    return media


def _rename_source(source, target, original_identity):
    if not source.is_file() or _identity(source) != original_identity:
        raise RuntimeError(f'Download source was moved or changed before renaming: {source}')
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() == target.resolve():
        return
    # link() creates the destination exclusively, so a concurrent user's file
    # cannot be overwritten between an exists check and rename(). Downloads and
    # its version subdirectories are on the same filesystem.
    try:
        os.link(source, target)
    except FileExistsError:
        raise RuntimeError(f'Refusing to replace an existing renamed audio: {target}')
    except OSError as exc:
        raise RuntimeError(f'Could not safely rename the local download to {target}: {exc}')
    try:
        source.unlink()
    except OSError as exc:
        raise RuntimeError(f'Renamed copy exists at {target}, but the original could not be removed: {exc}')


def _verify_existing(target, metadata, record_key, candidate_index):
    if not isinstance(metadata, dict) or metadata.get('record_key') != record_key:
        raise RuntimeError('Existing named download lacks matching record-key provenance; refusing replacement.')
    if metadata.get('selected_candidate') not in (None, candidate_index + 1):
        raise RuntimeError('Existing named download belongs to a different candidate.')
    expected = metadata.get('sha256')
    if not expected or not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != expected:
        raise RuntimeError(f'Existing named audio hash differs from its proven metadata: {target}')


def _preserve_existing(target, metadata, record_key, candidate_index):
    _verify_existing(target, metadata, record_key, candidate_index)
    backup = target.with_name(target.name + f'.before-redownload-{time.time_ns()}.bak')
    os.link(target, backup)  # Exclusive backup creation; never overwrite another file.
    # Recheck after linking in case another process changed the original bytes.
    if hashlib.sha256(backup.read_bytes()).hexdigest() != metadata['sha256']:
        raise RuntimeError(f'Existing download changed during backup; original left untouched: {target}')
    backup_metadata = {'record_key':record_key, 'selected_candidate':candidate_index + 1,
                       'sha256':metadata['sha256'], 'original_path':str(target),
                       'backup_path':str(backup), 'preserved_at':time.time()}
    backup.with_name(backup.name + '.json').write_text(
        json.dumps(backup_metadata, ensure_ascii=False, indent=2) + '\n')
    target.unlink()
    return backup


def download_candidate(backend, record_key, candidate_index, *, group_name, version,
                       tied=False, forbidden_ids=(), rename_dir=None, expected_url=None,
                       downloads_dir=None, wait_seconds=30, replace_existing=False,
                       existing_metadata=None):
    """Download once, reject stale lifecycle results, immediately rename locally.

    tied=True yields <group>__候选01.mp3 for internal comparison. The caller must
    rename its selected winner to <group>.mp3 before copying it to the project.
    Default rename directory is Downloads; pass a version directory explicitly
    for colliding female/gender-swapped names. No old ID/file is ever accepted.
    For an explicitly requested redownload, replace_existing=True requires the
    old file's matching {record_key, sha256, selected_candidate} metadata. Its
    verified bytes and metadata are preserved as .bak before the new rename.
    """
    if not re.fullmatch(r'[A-Za-z0-9_-]+', record_key):
        raise RuntimeError('Unexpected record key format.')
    if not group_name or Path(group_name).name != group_name or group_name in ('.', '..'):
        raise RuntimeError('Unsafe group name.')
    if not isinstance(candidate_index, int) or candidate_index < 0:
        raise RuntimeError('Candidate index must be a nonnegative integer.')
    downloads = Path(downloads_dir or Path.home() / 'Downloads').resolve()
    rename_root = Path(rename_dir or downloads).resolve()
    suffix = f'__候选{candidate_index + 1:02d}' if tied else ''
    target = rename_root / f'{group_name}{suffix}.mp3'
    if target.exists():
        if not replace_existing:
            raise RuntimeError(f'Renamed target already exists; inspect instead of redownloading: {target}')
        _verify_existing(target, existing_metadata, record_key, candidate_index)
    target_existed = target.exists()
    media = _open_viewer(backend, record_key, candidate_index)
    forbidden = _known_ids(backend, forbidden_ids)
    before_files = {str(path.resolve()):_identity(path) for path in downloads.glob('*.mp3') if path.is_file()}
    download_ref = backend.visible_ref('button.left-button-dckY70')
    before = time.time()
    backend.cli('click', download_ref)  # Exactly one download click, never retried here.
    deadline = time.monotonic() + wait_seconds
    rejected_ids = set()
    result = None
    while time.monotonic() < deadline:
        remaining = max(1, min(5, deadline - time.monotonic()))
        try:
            observed = backend.cli('wait', 'download', expected_url or '.mp3',
                                   '--timeout', int(remaining * 1000), timeout=15)
        except RuntimeError as exc:
            if 'download_not_seen' in str(exc):
                continue
            raise
        download_id = observed.get('id')
        if download_id is None:
            raise RuntimeError('Download lifecycle response has no ID; cannot prove freshness.')
        path = Path(observed.get('filename', '')).expanduser()
        stale = str(download_id) in forbidden
        if path.is_absolute() and str(path.resolve()) in before_files:
            stale = True
        if stale:
            rejected_ids.add(str(download_id))
            time.sleep(0.5)
            continue
        if observed.get('state') != 'complete':
            raise RuntimeError(f'Download is not complete: {observed}')
        if not path.is_absolute() or path.parent.resolve() != downloads:
            raise RuntimeError(f'Download response points outside the observed Downloads directory: {path}')
        if not path.is_file():
            raise RuntimeError(f'Fresh download source is missing or was moved by the user: {path}')
        if path.stat().st_ctime < before - 0.2:
            raise RuntimeError(f'Download predates this click and cannot be accepted: {path}')
        if expected_url and expected_url not in observed.get('url', ''):
            raise RuntimeError('Fresh download URL does not match the selected candidate URL.')
        result = observed
        break
    if result is None:
        raise RuntimeError(f'No fresh download ID and new file appeared within {wait_seconds}s; '
                           f'ignored old IDs {sorted(rejected_ids)}. No download/generation click was retried.')
    source = Path(result['filename']).resolve()
    identity = _identity(source)
    data = backend.probe(source)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    backup = None
    if target.exists():
        if not target_existed or not replace_existing:
            raise RuntimeError(f'A named file appeared during download; refusing to replace it: {target}')
        backup = _preserve_existing(target, existing_metadata, record_key, candidate_index)
    _rename_source(source, target, identity)
    if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != digest:
        raise RuntimeError(f'Renamed audio verification failed: {target}')
    _USED_IDS.add(str(result['id']))
    candidate = {'candidate':candidate_index + 1, 'download_path':str(target),
                 'original_download_path':str(source), 'download_id':result['id'],
                 'download_url':result.get('url'), 'duration_seconds':data['duration'],
                 'bytes':target.stat().st_size, 'sample_rate':data['audio']['sample_rate'],
                 'channels':data['audio']['channels'], 'sha256':digest,
                 'fresh_download_verified':True, 'download_clicked_at':before,
                 'rejected_old_download_ids':sorted(rejected_ids), 'viewer_source':media,
                 'record_key':record_key, 'group_name':group_name, 'version':version,
                 'temporary_tie_filename':bool(tied),
                 'previous_named_download_backup':str(backup) if backup else None}
    # Save data immediately in caller on return. A failed back navigation never
    # makes this verified/renamed download disappear from the caller's result.
    try:
        backend.cli('click', backend.visible_ref('button.back-button-Msd9gi'))
    except Exception as exc:
        candidate['viewer_return_error'] = str(exc)
    return candidate
