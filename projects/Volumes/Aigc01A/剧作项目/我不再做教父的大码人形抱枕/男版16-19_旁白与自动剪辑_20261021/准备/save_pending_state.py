import datetime
import hashlib
import json
import shutil
from pathlib import Path

out = Path(__file__).resolve().parent.parent
src = Path('/Users/zc/Downloads/男版.wav')
dst = out / '参考音色' / '男版_用户指定原始参考.wav'
dst.parent.mkdir(exist_ok=True)
if not dst.exists():
    shutil.copy2(src, dst)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(src) == sha(dst)
manifest = json.loads((out / '准备/narration_manifest.json').read_text(encoding='utf-8'))
state = {
    'updated_at': datetime.datetime.now().isoformat(),
    'scope': 'male EP16-19 narration then native editing with sync audio and SRT',
    'voice_original': str(src),
    'voice_stable_copy': str(dst),
    'voice_sha256': sha(src),
    'voice_duration_seconds': 5.619229,
    'platform': '即梦',
    'model': 'Seed TTS',
    'mode': '文本朗读',
    'browser_tab_id': '684867490',
    'status': 'awaiting_reference_audio_loaded_in_browser',
    'generation_submitted': False,
    'editing_started': False,
    'narration_speed_percent': 100,
    'external_send': False,
    'narration_manifest': str(out / '准备/narration_manifest.json'),
    'items': [],
    'blocker': 'Upload button only focuses. No chooser or reference audio was observed after user reported opening it.',
    'workflow': [
        'Load exact male.wav reference, create voice',
        'Generate 27 original English narration segments',
        'Download and rename each immediately; organize by episode',
        'Verify words and map actual timings; preserve sync dialogue',
        'Create male EP16-19 native editable timelines',
        'Import SRT captions before loading subtitle track preset',
        'Save, reopen and verify'
    ]
}
for group in manifest['groups']:
    folder = out / '音频' / ('第%d集' % group['episode'])
    folder.mkdir(parents=True, exist_ok=True)
    state['items'].append({
        'episode': group['episode'],
        'basename': group['basename'],
        'text_file': group['text_file'],
        'generation_text': group['generation_text'],
        'status': 'not_submitted',
        'planned_audio_file': str(folder / (group['basename'] + '.mp3'))
    })
assert len(state['items']) == 27
(out / '制作与剪辑进度.json').write_text(
    json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
print('27 pending segments saved; reference copy hash verified.')
