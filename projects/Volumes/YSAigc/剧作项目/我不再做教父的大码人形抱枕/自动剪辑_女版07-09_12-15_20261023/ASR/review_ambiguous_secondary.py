"""Independent local small.en blind pass for repeated/template-like primary output.

Candidate rules are acoustic-ASR diagnostics only, never expected script text.
Disagreement is not proof of silence or authority to mute original sound.
"""
from pathlib import Path
import importlib.util
import json
import re
import time

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('primary_runtime', HERE / 'run_blind_female.py')
primary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(primary)
from mlx_whisper.audio import load_audio, SAMPLE_RATE
import mlx_whisper

index = json.loads((HERE / '\u8f6c\u5f55\u7d22\u5f15.json').read_text(encoding='utf-8'))
assert index.get('finished_at_utc') and index['completed'] == 123 and not index['errors']
model_base = primary.runtime.OLD_ASR / 'models/small.en'
model = model_base / 'weights'
provenance = json.loads((model_base / 'provenance.json').read_text(encoding='utf-8'))
for item in provenance['files']:
    assert primary.digest(model / item['path']) == item['sha256']

results = []
for row in index['files']:
    if row['kind'] != 'video':
        continue
    raw = json.loads(Path(row['json_path']).read_text(encoding='utf-8'))
    ratio = max([s.get('compression_ratio', 0) for s in raw['segments']] or [0])
    template = bool(re.search(r'next video|little bit of|bathroom|hello everyone|thank you for watching|i.m so excited', raw['text'], re.I))
    if not (ratio > 2.4 or template):
        continue
    source = Path(row['source_path'])
    target = HERE / 'secondary_small.en' / ('EP%02d' % row['episode']) / (source.stem + '.json')
    sha = primary.digest(source)
    started = time.monotonic()
    if target.exists():
        secondary = json.loads(target.read_text(encoding='utf-8'))
        assert secondary['source_sha256'] == sha
    else:
        audio = load_audio(str(source))
        result = mlx_whisper.transcribe(audio, path_or_hf_repo=str(model), **primary.PARAMETERS)
        assert primary.digest(source) == sha
        words = [w for s in result.get('segments', []) for w in s.get('words', [])]
        secondary = dict(source_path=str(source), source_sha256=sha, episode=row['episode'],
                         model='small.en', model_revision=provenance['revision'],
                         decode_parameters=primary.PARAMETERS, blind_transcription=True,
                         expected_script_supplied_to_model=False, human_listening_validation=False,
                         source_files_modified=False, decoded_duration_seconds=len(audio)/SAMPLE_RATE,
                         text=result.get('text', ''), segments=result.get('segments', []), words=words,
                         no_recognized_words=not bool(words), raw_result=result,
                         runtime_seconds=time.monotonic()-started)
        primary.save(target, secondary)
        primary.runtime.sidecars(secondary, target)
    report = dict(source_path=str(source), source_sha256=sha, episode=row['episode'],
                  primary_text=raw['text'], primary_max_compression_ratio=ratio,
                  primary_template_pattern=template, secondary_text=secondary['text'],
                  secondary_no_recognized_words=secondary['no_recognized_words'],
                  secondary_json=str(target), requires_audio_review=True,
                  never_use_unreviewed_asr_as_subtitle_original=True,
                  not_proof_of_silence_do_not_mute_source=True)
    results.append(report)
    primary.save(HERE / '\u7591\u4f3c\u5e7b\u89c9_\u4e8c\u6b21\u76f2\u8bc6\u522b.json', dict(files=results, human_listening_validation=False, expected_script_supplied_to_model=False))
    print(json.dumps(report, ensure_ascii=False), flush=True)

primary.save(HERE / '\u7591\u4f3c\u5e7b\u89c9_\u4e8c\u6b21\u76f2\u8bc6\u522b.json', dict(files=results, completed=True,
             count=len(results), human_listening_validation=False, expected_script_supplied_to_model=False))
