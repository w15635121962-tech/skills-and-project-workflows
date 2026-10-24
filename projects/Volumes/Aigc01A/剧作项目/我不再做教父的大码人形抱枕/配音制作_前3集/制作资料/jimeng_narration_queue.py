#!/usr/bin/env python3
"""Bounded Jimeng UI queue; OpenCLI mutations only, eval reads DOM only.

Examples (run after stopping jimeng_narration_batch.py):
  python3 jimeng_narration_queue.py --version 女版 --voice 大码女版 --groupcount 3
  python3 jimeng_narration_queue.py --version 性转版 --voice 大码性转版 --groupcount 6 --inflight 3

No submission is retried automatically. A click with an unknown outcome stays in
the shared journal until its single generated record can be recovered.
"""
import argparse
import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
import jimeng_narration_batch as base
import jimeng_download_guard as download_guard

ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / '制作资料/200字旁白生成计划.json'
MANIFEST = ROOT / '制作资料/已下载音频清单.json'
JOURNAL = ROOT / '制作资料/即梦提交与下载记录.json'
PROBE = '/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts/probe.py'
SESSION = 'dama-current'
WORKSPACE = '23561838050060'
TRACKED = {}
REJECTIONS = ('积分不足', '余额不足', '次数不足', '同时生成任务已达上限',
              '任务数量已达上限', '生成任务过多', '生成中任务过多',
              '当前排队任务过多', '当前有任务正在生成', '请等待当前任务完成',
              '生成频繁', '操作频繁')


def emit(**data):
    print(json.dumps(data, ensure_ascii=False), flush=True)


def file_digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def save(path, data):
    # A different runner/user edit must never be silently overwritten. The old
    # sequential batch has no lock, so stop it before launching this queue.
    if path in TRACKED and file_digest(path) != TRACKED[path]:
        raise RuntimeError(f'Another writer changed {path}; stopping without overwriting it.')
    temp = path.with_name(path.name + f'.queue-{os.getpid()}.tmp')
    with temp.open('w', encoding='utf-8') as stream:
        stream.write(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    temp.replace(path)
    TRACKED[path] = file_digest(path)


def cli(*args, timeout=35):
    result = subprocess.run(['opencli', 'browser', SESSION, *map(str, args)],
                            capture_output=True, text=True, encoding='utf-8', timeout=timeout)
    if result.returncode:
        raise RuntimeError(result.stdout.strip() + '\n' + result.stderr.strip())
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError:
        return result.stdout.strip()
    if isinstance(value, dict) and value.get('error'):
        raise RuntimeError(json.dumps(value, ensure_ascii=False))
    return value


def evaluate(js):
    return cli('eval', js)


def norm(text):
    return ' '.join(text.split())


def snapshot():
    state = evaluate('''(() => ({url:location.href,text:document.body.innerText,
      records:Array.from(document.querySelectorAll('[data-generated-record-key]')).map(e=>({
        key:e.getAttribute('data-generated-record-key'),
        handoff:e.getAttribute('data-generated-record-handoff-key'),text:e.innerText,
        cards:Array.from(e.querySelectorAll('.audio-card-container-x_138k')).map(c=>c.innerText)
      }))}))()''')
    if not isinstance(state, dict) or f'workspace={WORKSPACE}' not in state.get('url', ''):
        raise RuntimeError('Unexpected workspace; refusing further UI actions.')
    return state


def visible_entries(selector):
    try:
        result = cli('find', '--css', selector, '--limit', '40', '--text-max', '60')
    except RuntimeError as exc:
        if 'selector_not_found' in str(exc):
            return []
        raise
    return [entry for entry in result.get('entries', []) if entry.get('visible')]


def visible_ref(selector):
    entries = visible_entries(selector)
    if len(entries) != 1:
        raise RuntimeError(f'Expected one visible control for {selector}: {len(entries)}')
    return str(entries[0]['ref'])


def ensure_list_view():
    # Recover from an interrupted download while the detail viewer is open.
    if visible_entries('.page-number-YYNlfP'):
        cli('click', visible_ref('button.back-button-Msd9gi'))
        wait_for_record()


def wait_for_record(record_key=None):
    # OpenCLI's selector wait can fail immediately during this app's layout
    # transitions. Poll read-only DOM observations for a bounded ten seconds.
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        state = snapshot()
        if any(record_key is None or record['key'] == record_key for record in state['records']):
            return
        time.sleep(0.5)
    raise RuntimeError('Generated record list did not return after leaving the detail viewer.')


def durations(card_texts):
    return [max((int(a) * 60 + int(b) for a, b in re.findall(r'(\d+):(\d{2})', txt)), default=0)
            for txt in card_texts]


def probe(path):
    result = subprocess.run([sys.executable, PROBE, str(path), '--json'], check=True,
                            capture_output=True, text=True, encoding='utf-8')
    data = json.loads(result.stdout)
    if not data.get('audio') or data.get('video') or data.get('duration', 0) <= 0:
        raise RuntimeError(f'Invalid downloaded audio: {path}')
    return data


def group_key(group):
    return f"{group['version']}/{group['name']}"


def generation_text(group):
    text = group.get('generation_text', group['text']).strip()
    if not text or len(text) > 200 or any(q in text for q in ('"', '“', '”')):
        raise RuntimeError(f'{group_key(group)} violates the narration/200-character contract.')
    if text[-1] not in '.!?' or group.get('sentence_boundary_verified') is False:
        raise RuntimeError(f'{group_key(group)} is not verified as complete sentences.')
    expected = group.get('generation_sha256')
    if expected and hashlib.sha256(text.encode()).hexdigest() != expected:
        raise RuntimeError(f'{group_key(group)} generation text differs from its verified hash.')
    return text


def manifest_index(manifest):
    index = {}
    for row in manifest['clips']:
        key = group_key(row)
        if key in index:
            raise RuntimeError(f'Duplicate manifest clip: {key}')
        path = Path(row['local_path'])
        if not path.is_file() or not path.stat().st_size:
            raise RuntimeError(f'Manifest audio is missing/empty: {path}')
        if row.get('sha256') and file_digest(path) != row['sha256']:
            raise RuntimeError(f'Manifest audio hash differs: {path}')
        index[key] = row
    return index


def reserved_keys(journal, manifest, exclude=None):
    keys = {row['record_key'] for row in manifest['clips'] if row.get('record_key')}
    keys.update(entry['record_key'] for key, entry in journal.items()
                if key != exclude and entry.get('record_key'))
    return keys


def match_new_records(state, entry, journal, manifest, key):
    # Exclude all keys known BEFORE this click, plus every other task's key.
    # A later completed in-flight task must never be attributed to this click.
    excluded = set(entry['before_keys']) | reserved_keys(journal, manifest, exclude=key)
    new = [record for record in state['records'] if record['key'] not in excluded]
    matching = [record for record in new if not record['text'].strip() or
                (norm(entry['text']) in norm(record['text']) and entry['voice'] in record['text'])]
    return new, matching


def bind_record(key, entry, record, journal):
    entry.update(record_key=record['key'], status='submitted', record_observed_at=time.time())
    entry.pop('last_error', None)
    save(JOURNAL, journal)
    emit(submitted=key, characters=len(entry['text']), record_key=record['key'])


def recover_submission(key, entry, journal, manifest):
    if 'before_keys' not in entry or not entry.get('text') or not entry.get('voice'):
        raise RuntimeError(f'{key}: incomplete prior submission journal; refusing a duplicate submission.')
    state = snapshot()
    new, matching = match_new_records(state, entry, journal, manifest, key)
    if len(new) == len(matching) == 1:
        bind_record(key, entry, matching[0], journal)
        return
    raise RuntimeError(f'{key}: previous click outcome unresolved ({len(new)} new records, '
                       f'{len(matching)} prompt/voice matches); no generation will be retried.')


def submit_group(group, voice, journal, manifest):
    key = group_key(group)
    text = generation_text(group)
    prior = journal.get(key, {})
    if prior.get('record_key') or prior.get('status') in (
            'submitting', 'submission_uncertain', 'submission_rejected_no_record'):
        raise RuntimeError(f'{key}: prior submission exists; recovery is required before any new click.')
    snapshot()  # Verify workspace before changing the form.
    ref = visible_ref('textarea.prompt-textarea-U6goqo')
    cli('fill', f'[data-opencli-ref="{ref}"]', text)
    ref = visible_ref('textarea.prompt-textarea-U6goqo')
    if cli('get', 'value', f'[data-opencli-ref="{ref}"]')['value'] != text:
        raise RuntimeError('Text readback differs from the verified source.')
    form = evaluate(f'''(() => document.querySelector('[data-opencli-ref="{ref}"]')
        .closest('[data-generate-content-generator]').innerText)()''')
    if voice not in form or 'Seed TTS' not in form or '文本朗读' not in form:
        raise RuntimeError(f'Unexpected voice/model controls: {form}')
    state = snapshot()
    # Determine the control before writing a click-intent record: if the control
    # is unavailable, no click happened and this group remains safe to submit.
    submit = visible_ref('button[data-generator-submit-available="true"]')
    before = {record['key'] for record in state['records']} | reserved_keys(journal, manifest)
    entry = journal.setdefault(key, {})
    entry.update(status='submitting', text=text, character_count=len(text), voice=voice,
                 before_keys=sorted(before), click_intent_at=time.time(),
                 credit_click_attempted='unknown')
    save(JOURNAL, journal)
    try:
        cli('click', submit)
        entry.update(credit_click_attempted=True, clicked_at=time.time())
        save(JOURNAL, journal)
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            state = snapshot()
            new, matching = match_new_records(state, entry, journal, manifest, key)
            if len(new) == len(matching) == 1:
                bind_record(key, entry, matching[0], journal)
                return make_job(group, entry)
            if len(new) > 1:
                raise RuntimeError('Multiple unclaimed new records; cannot safely identify this submission.')
            rejection = next((message for message in REJECTIONS if message in state['text']), None)
            if rejection and not new:
                entry.update(status='submission_rejected_no_record', last_error=rejection)
                save(JOURNAL, journal)
                raise RuntimeError(f'Jimeng refused this click ({rejection}) and no new record appeared; '
                                   'stopping without retrying or using further credits.')
            time.sleep(1.5)
        raise RuntimeError('No uniquely matching generation record appeared within 45 seconds; '
                           'stopping without retrying this click.')
    except Exception as exc:
        if entry.get('status') not in ('submitted', 'submission_rejected_no_record'):
            entry.update(status='submission_uncertain', last_error=str(exc))
            save(JOURNAL, journal)
        raise


def make_job(group, entry):
    return {'key':group_key(group), 'group':group, 'entry':entry,
            'deadline':time.monotonic() + 240}


def ready_record(job, state, journal):
    entry = job['entry']
    record = next((r for r in state['records'] if r['key'] == entry['record_key']), None)
    if record and any(message in record['text'] for message in ('生成失败', '审核未通过')):
        entry.update(status='generation_failed', last_error=record['text'][:500])
        save(JOURNAL, journal)
        raise RuntimeError(f'{job["key"]}: generation failed; no regeneration will be submitted.')
    if record and len(record['cards']) >= 2 and all(value > 0 for value in durations(record['cards'])):
        if norm(entry['text']) not in norm(record['text']) or entry['voice'] not in record['text']:
            raise RuntimeError(f'{job["key"]}: generated prompt/voice differs from the verified source.')
        return record
    if time.monotonic() > job['deadline']:
        raise RuntimeError(f'{job["key"]}: generation wait exceeded 240 seconds; '
                           'its record key is saved, so the next run can resume without submitting again.')
    return None


def download_candidate(record_key, candidate_index, group, *, tied=False):
    if not re.fullmatch(r'[A-Za-z0-9_-]+', record_key):
        raise RuntimeError('Unexpected record key format; refusing to build a selector.')
    # The guard rejects old lifecycle IDs/files, clicks download once, and
    # renames the local source before returning. Persist its result before any
    # subsequent UI wait, so a failed back navigation cannot lose provenance.
    return download_guard.download_candidate(
        base, record_key, candidate_index, group_name=group['name'],
        version=group['version'], tied=tied, rename_dir=Path.home() / 'Downloads')


def finalize_selected_name(selected, group):
    source = Path(selected['download_path'])
    target = source.parent / (group['name'] + '.mp3')
    expected = selected.get('sha256')
    if not expected or not source.is_file() or file_digest(source) != expected:
        raise RuntimeError(f'Selected local download is missing/changed before final naming: {source}')
    if source != target:
        if target.exists():
            if file_digest(target) != expected:
                raise RuntimeError(f'Refusing to replace a different named download: {target}')
        else:
            os.link(source, target)  # Exclusive final-name creation on the same local filesystem.
        if file_digest(target) != expected:
            raise RuntimeError(f'Final named download hash differs: {target}')
        source.unlink()
        selected['tie_comparison_download_path'] = str(source)
        selected['download_path'] = str(target)
    selected.update(temporary_tie_filename=False, selected=True)
    return target


def finish_group(job, ready, journal, manifest):
    group, entry, key = job['group'], job['entry'], job['key']
    shown = durations(ready['cards'])
    tied = [index for index, value in enumerate(shown) if value == min(shown)]
    entry.update(status='ready', displayed_durations=shown, handoff=ready['handoff'])
    save(JOURNAL, journal)
    cached = {}
    for candidate in entry.get('downloaded_candidates', []):
        if candidate['candidate'] - 1 not in tied:
            continue
        if not candidate.get('fresh_download_verified') or candidate.get('record_key') != entry['record_key']:
            raise RuntimeError(f'{key}: cached candidate lacks fresh-download/record provenance; inspect before continuing.')
        path = Path(candidate['download_path'])
        # Recover a crash between promoting a tie winner and saving its new
        # path, only when the exact final filename has the proven same bytes.
        if not path.is_file() and candidate.get('temporary_tie_filename'):
            promoted = path.parent / (group['name'] + '.mp3')
            if candidate.get('sha256') and promoted.is_file() and file_digest(promoted) == candidate['sha256']:
                candidate = dict(candidate, download_path=str(promoted), temporary_tie_filename=False)
                path = promoted
        if not path.is_file() or not candidate.get('sha256') or file_digest(path) != candidate['sha256']:
            raise RuntimeError(f'{key}: cached local candidate is missing or changed: {path}')
        if any(old.get('download_id') == candidate.get('download_id') or
               old['download_path'] == str(path) for old in cached.values()):
            raise RuntimeError(f'{key}: multiple candidates reuse one download ID/path; inspect before continuing.')
        measured = probe(path)
        cached[candidate['candidate']] = dict(candidate,
            duration_seconds=measured['duration'], bytes=path.stat().st_size,
            sample_rate=measured['audio']['sample_rate'], channels=measured['audio']['channels'])
    for index in tied:
        if index + 1 in cached:
            continue
        candidate = download_candidate(entry['record_key'], index, group, tied=len(tied) > 1)
        candidate['selected'] = len(tied) == 1
        cached[candidate['candidate']] = candidate
        entry['downloaded_candidates'] = list(cached.values())
        save(JOURNAL, journal)
        # One source has already been renamed and journaled before a following
        # candidate can be downloaded. No two download clicks can overlap.
        if index != tied[-1]:
            ensure_list_view()
            wait_for_record(entry['record_key'])
    candidates = [cached[index + 1] for index in tied]
    selected = min(candidates, key=lambda candidate: candidate['duration_seconds'])
    for candidate in candidates:
        candidate['selected'] = candidate is selected
    source = finalize_selected_name(selected, group)
    entry.update(downloaded_candidates=candidates, selected_candidate=selected['candidate'],
                 selected_download_path=str(source))
    save(JOURNAL, journal)
    out = Path(group['output_dir']) / (group['name'] + '.mp3')
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and out.read_bytes() != source.read_bytes():
        raise RuntimeError(f'Refusing to replace different audio: {out}')
    if not out.exists():
        shutil.copy2(source, out)
    digest = file_digest(out)
    if digest != file_digest(source):
        raise RuntimeError('Copied audio hash differs from the downloaded file.')
    row = {'version':group['version'], 'episode':group['episode'], 'name':group['name'],
           'local_path':str(out), 'status':'downloaded', 'model':'Seed TTS',
           'voice_name':entry['voice'], 'text':entry['text'], 'character_count':len(entry['text']),
           'workspace':WORKSPACE, 'record_key':entry['record_key'], 'handoff':ready['handoff'],
           'displayed_candidate_seconds':shown, 'downloaded_candidates':candidates,
           'selected_candidate':selected['candidate'], 'duration_seconds':selected['duration_seconds'],
           'selected_download_path':str(source),
           'sha256':digest,
           'selection_rule':'minimum display duration; tied outputs compared by measured duration',
           'speech_word_coverage':'generation text verified; offline ASR unavailable'}
    if any(group_key(existing) == key for existing in manifest['clips']):
        raise RuntimeError(f'{key}: manifest entry appeared during processing; refusing a duplicate row.')
    manifest['clips'].append(row)
    save(MANIFEST, manifest)
    entry.update(status='downloaded', local_path=str(out), selected_candidate=selected['candidate'],
                 downloaded_candidates=candidates)
    save(JOURNAL, journal)
    emit(saved=key, seconds=selected['duration_seconds'], displayed_candidates=shown,
         candidate=selected['candidate'], downloaded_total=len(manifest['clips']))
    ensure_list_view()
    wait_for_record(entry['record_key'])


def drain_ready(pending, journal, manifest):
    state = snapshot()
    finished = []
    for job in list(pending):
        key = job['entry']['record_key']
        record = next((r for r in state['records'] if r['key'] == key), None)
        # Virtualized records can exist as empty placeholders. Use a structured
        # hover to scroll the observed record into view before reading readiness.
        if record is not None and not record['cards']:
            selector = f'[data-generated-record-key="{key}"]'
            cli('find', '--css', selector, '--limit', '1', '--text-max', '80')
            cli('hover', selector)
            time.sleep(0.5)
            state = snapshot()
        ready = ready_record(job, state, journal)
        if ready:
            finish_group(job, ready, journal, manifest)
            pending.remove(job)
            finished.append(job)
            state = snapshot()
        else:
            # Download strictly in creation/source order even if a later job finishes first.
            break
    return finished


def recover_jobs(plan, journal, manifest, resolve_uncertain=False):
    groups = {group_key(group):group for group in plan['groups']}
    done = manifest_index(manifest)
    jobs = []
    for key, entry in journal.items():
        if key in done:
            continue
        if not entry.get('record_key') and entry.get('status') not in (
                'submitting', 'submission_uncertain', 'submission_rejected_no_record'):
            if entry.get('status') == 'downloaded':
                raise RuntimeError(f'{key}: downloaded journal entry has no manifest/record; inspect before continuing.')
            continue
        # Download all known submitted records before an unresolved/rejected
        # later click can stop recovery. This never authorizes another click.
        if not entry.get('record_key') and not resolve_uncertain:
            continue
        if key not in groups:
            raise RuntimeError(f'Outstanding journal group is absent from the plan: {key}')
        group = groups[key]
        text = generation_text(group)
        if entry.get('text') != text or not entry.get('voice'):
            raise RuntimeError(f'{key}: prior submission text/voice does not match the verified plan.')
        if not entry.get('record_key'):
            recover_submission(key, entry, journal, manifest)
        if entry.get('status') == 'generation_failed':
            raise RuntimeError(f'{key}: prior generation failed; no automatic resubmission is allowed.')
        jobs.append(make_job(group, entry))
    assigned = [entry['record_key'] for entry in journal.values() if entry.get('record_key')]
    if len(assigned) != len(set(assigned)):
        raise RuntimeError('Multiple journal groups claim the same record key; inspect before continuing.')
    return jobs


def positive_count(value):
    value = int(value)
    if value < 1:
        raise argparse.ArgumentTypeError('must be a positive integer')
    return value


def workspace_id(value):
    if not re.fullmatch(r'[0-9]+', value):
        raise argparse.ArgumentTypeError('workspace must contain ASCII digits only')
    return value


def session_name(value):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', value):
        raise argparse.ArgumentTypeError('session must start with a letter/digit and contain only letters, digits, _ or -')
    return value


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', choices=['女版', '性转版'], required=True)
    parser.add_argument('--voice', required=True)
    parser.add_argument('--workspace', type=workspace_id, default=WORKSPACE,
                        help='Jimeng workspace ID (default 23561838050060)')
    parser.add_argument('--session', type=session_name, default=SESSION,
                        help='OpenCLI browser session (default dama-current)')
    parser.add_argument('--groupcount', '--limit', dest='groupcount', type=positive_count, default=3,
                        help='number of new downloads for the selected version (default 3; e.g. 3 or 6)')
    parser.add_argument('--inflight', type=int, choices=[2, 3], default=2,
                        help='maximum simultaneous submitted tasks (default 2)')
    return parser.parse_args(argv)


def main():
    global WORKSPACE, SESSION
    args = parse_args()
    WORKSPACE = args.workspace
    SESSION = args.session
    base.SESSION = SESSION
    lock = (ROOT / '制作资料/.jimeng_narration_queue.lock').open('a+')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise RuntimeError('Another queue runner is active; this runner will not touch the UI.')
    # Retain the descriptor for the entire run.
    with lock:
        plan = json.loads(PLAN.read_text())
        manifest = json.loads(MANIFEST.read_text())
        journal = json.loads(JOURNAL.read_text()) if JOURNAL.exists() else {}
        TRACKED.update({MANIFEST:file_digest(MANIFEST), JOURNAL:file_digest(JOURNAL)})
        manifest['expected_clip_count'] = plan['total_group_count']
        manifest['generation_plan'] = str(PLAN)
        manifest_index(manifest)
        # Validate every relevant source before the first UI interaction.
        for group in plan['groups']:
            if group['version'] == args.version:
                generation_text(group)
                if group.get('submit_generation') is False and group_key(group) not in manifest_index(manifest):
                    raise RuntimeError(f'{group_key(group)} must be reused from the manifest, never regenerated.')
        ensure_list_view()
        pending = recover_jobs(plan, journal, manifest)
        recovered = []
        if pending:
            emit(recovering=[job['key'] for job in pending], new_submissions_paused=True)
        # Existing submitted work is drained first, even for the other version.
        # Downloading it needs no form/voice changes and spends no new credits.
        while pending:
            finished = drain_ready(pending, journal, manifest)
            recovered.extend(finished)
            if pending and not finished:
                time.sleep(2)
        # Only after known submissions have been saved, bind any uniquely
        # identifiable late record from an uncertain click, or stop for review.
        pending = recover_jobs(plan, journal, manifest, resolve_uncertain=True)
        if pending:
            emit(recovering=[job['key'] for job in pending], new_submissions_paused=True)
        while pending:
            finished = drain_ready(pending, journal, manifest)
            recovered.extend(finished)
            if pending and not finished:
                time.sleep(2)
        recovered_selected = sum(job['group']['version'] == args.version for job in recovered)
        done = manifest_index(manifest)
        budget = max(0, args.groupcount - recovered_selected)
        groups = [group for group in plan['groups'] if group['version'] == args.version
                  and group.get('submit_generation') is not False and group_key(group) not in done][:budget]
        remaining = iter(groups)
        next_group = next(remaining, None)
        downloaded = 0
        submitted = 0
        while next_group is not None or pending:
            while next_group is not None and len(pending) < args.inflight:
                job = submit_group(next_group, args.voice, journal, manifest)
                pending.append(job)
                submitted += 1
                emit(inflight=len(pending), maximum_inflight=args.inflight)
                next_group = next(remaining, None)
            if pending:
                finished = drain_ready(pending, journal, manifest)
                downloaded += len(finished)
                if pending and not finished:
                    time.sleep(2)
        emit(batch_finished=True, inflight_limit=args.inflight, requested_groupcount=args.groupcount,
             newly_submitted=submitted, recovered_downloads=len(recovered),
             new_downloads=downloaded + len(recovered), downloaded_total=len(manifest['clips']))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        emit(stopped=str(exc), automatic_resubmission=False)
        raise SystemExit(1)
