#!/usr/bin/env python3
"""Submit only male EP3 group 6 once from the observed audio homepage.

No download or automatic resubmission. The regular queue resumes after the new
workspace and its unique generated record have both been saved.
"""
import fcntl
import json
import re
import time
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import jimeng_narration_queue as q

base = q.base
SESSION = 'dama-current'
VOICE = '大码性转男版'
GROUP_NAME = '大码性转男版03-01-06'
INFO = q.ROOT / '制作资料/最后3条新账号工作区.json'
TEXTAREA = 'textarea.prompt-textarea-U6goqo'
SUBMIT = 'button.submit-button-PqSGK1[data-generator-submit-available="true"]'


def url_workspace(url, *, require_home=False):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if parsed.scheme != 'https' or parsed.netloc != 'jimeng.jianying.com':
        raise RuntimeError('Unexpected site; refusing this submission.')
    home = parsed.path.rstrip('/') == '/ai-tool/home' and query.get('type') == ['audio']
    if require_home:
        if not home:
            raise RuntimeError('Expected the current audio homepage before submitting.')
        return None
    if home:
        return None
    workspace = query.get('workspace', [])
    if parsed.path.rstrip('/') == '/ai-tool/generate' and not workspace:
        return None  # The page can redirect before its workspace query is ready.
    if (parsed.path.rstrip('/') != '/ai-tool/generate' or len(workspace) != 1
            or not re.fullmatch(r'[0-9]+', workspace[0])):
        raise RuntimeError('No verified generate-page workspace in the observed URL.')
    return workspace[0]


def main():
    q.SESSION = base.SESSION = SESSION
    lock_path = q.ROOT / '制作资料/.jimeng_narration_queue.lock'
    with lock_path.open('a+') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('Another queue runner is active; no UI action was performed.')
        plan = json.loads(q.PLAN.read_text())
        manifest = json.loads(q.MANIFEST.read_text())
        journal = json.loads(q.JOURNAL.read_text()) if q.JOURNAL.exists() else {}
        q.TRACKED.update({q.JOURNAL: q.file_digest(q.JOURNAL),
                          q.MANIFEST: q.file_digest(q.MANIFEST),
                          INFO: q.file_digest(INFO)})
        groups = [g for g in plan['groups']
                  if g['version'] == '性转版' and g['name'] == GROUP_NAME]
        if len(groups) != 1:
            raise RuntimeError('Expected exactly the requested group in the official plan.')
        group = groups[0]
        text = q.generation_text(group)
        if Path(group['text_file']).read_text() != text:
            raise RuntimeError('Group TXT differs from the verified generation text.')
        key = q.group_key(group)
        done = q.manifest_index(manifest)
        if key in done:
            q.emit(skipped=key, reason='already_downloaded', automatic_resubmission=False)
            return
        if key in journal:
            raise RuntimeError('This group already has a journal entry; recover it instead of clicking again.')
        if group.get('submit_generation') is False or INFO.exists():
            raise RuntimeError('Existing reuse/workspace state requires review before any new click.')
        if any(k not in done and (entry.get('record_key') or entry.get('status') in
                ('submitting', 'submission_uncertain', 'submission_rejected_no_record'))
               for k, entry in journal.items()):
            raise RuntimeError('Other unfinished submissions exist; refusing a new homepage click.')
        old_keys = {row['record_key'] for row in manifest['clips'] if row.get('record_key')}
        if len(manifest['clips']) != 44 or len(old_keys) != 44:
            raise RuntimeError('Expected all 44 prior downloads and their unique record keys.')
        old_workspaces = {str(row['workspace']) for row in manifest['clips'] if row.get('workspace')}
        state = base.snapshot()
        url_workspace(state['url'], require_home=True)
        ref = q.visible_ref(TEXTAREA)
        q.cli('fill', f'[data-opencli-ref="{ref}"]', text)
        ref = q.visible_ref(TEXTAREA)
        selector = f'[data-opencli-ref="{ref}"]'
        if q.cli('get', 'value', selector).get('value') != text:
            raise RuntimeError('Homepage text readback differs from the verified source.')
        form = q.evaluate(f'''(() => document.querySelector({json.dumps(selector)})
            ?.closest('.layout-U1hCE5')?.innerText || '')()''')
        if not isinstance(form, str) or not all(value in form for value in (VOICE, 'Seed TTS', '文本朗读')):
            raise RuntimeError(f'Unexpected homepage voice/model controls: {form}')
        state = base.snapshot()
        url_workspace(state['url'], require_home=True)
        # The observed collapsed sibling is invisible; never click by a shared
        # unqualified submit selector or a stale reference.
        submit_ref = q.visible_ref(SUBMIT)
        submit_selector = f'[data-opencli-ref="{submit_ref}"]'
        enabled = q.evaluate(f'''(() => {{const e=document.querySelector({json.dumps(submit_selector)});
            if(!e)return false;const r=e.getBoundingClientRect();
            return !e.disabled && e.getAttribute('data-generator-submit-available')==='true'
                && r.width>0 && r.height>0;}})()''')
        if enabled is not True:
            raise RuntimeError('The unique visible full submit button is not enabled.')
        before = old_keys | {r['key'] for r in state['records']} | q.reserved_keys(journal, manifest)
        entry = {'status': 'submitting', 'text': text, 'character_count': len(text),
                 'voice': VOICE, 'session': SESSION, 'before_keys': sorted(before),
                 'click_intent_at': time.time(), 'credit_click_attempted': 'unknown',
                 'submission_entrypoint': 'audio_homepage', 'before_url': state['url']}
        journal[key] = entry
        q.save(q.JOURNAL, journal)
        q.emit(click_intent=key, characters=len(text), prior_record_keys=len(before))
        try:
            q.cli('click', submit_selector)  # Exactly one submission click.
            entry.update(credit_click_attempted=True, clicked_at=time.time())
            q.save(q.JOURNAL, journal)
            deadline = time.monotonic() + 45
            while time.monotonic() < deadline:
                state = base.snapshot()  # Workspace does not exist until this redirect.
                workspace = url_workspace(state['url'])
                new, matching = q.match_new_records(state, entry, journal, manifest, key)
                if len(new) > 1:
                    raise RuntimeError('Multiple unclaimed new records; no unique submission binding.')
                if workspace and workspace in old_workspaces:
                    raise RuntimeError('Redirect returned a prior-account workspace; refusing attribution.')
                if workspace and len(new) == len(matching) == 1:
                    entry.update(workspace=workspace, session=SESSION, workspace_url=state['url'])
                    q.WORKSPACE = workspace
                    q.bind_record(key, entry, matching[0], journal)
                    info = {'workspace': workspace, 'session': SESSION,
                            'first_group_name': GROUP_NAME, 'record_key': matching[0]['key'],
                            'url': state['url']}
                    q.save(INFO, info)
                    q.emit(homepage_submitted_once=True, **info, automatic_resubmission=False)
                    return
                rejection = next((message for message in q.REJECTIONS if message in state['text']), None)
                if rejection and not new:
                    raise RuntimeError(f'Homepage submission rejected: {rejection}; no second click.')
                time.sleep(1.5)
            raise RuntimeError('No unique new record plus new workspace within 45 seconds; no second click.')
        except Exception as exc:
            if entry.get('status') != 'submitted':
                entry.update(status='submission_uncertain', last_error=str(exc))
                q.save(q.JOURNAL, journal)
            raise


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        q.emit(stopped=str(exc), automatic_resubmission=False)
        raise SystemExit(1)
