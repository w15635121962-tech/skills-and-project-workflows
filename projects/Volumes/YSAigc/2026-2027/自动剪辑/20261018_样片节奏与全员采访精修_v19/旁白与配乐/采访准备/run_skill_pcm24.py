"""Run the installed skill with an explicit 24-bit PCM override in memory only."""
import os, runpy, sys
from pathlib import Path

scripts=Path('/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts')
sys.path.insert(0,str(scripts))
import _common
_common.AUDIO_CODECS['.wav']=['-c:a','pcm_s24le']
tool=sys.argv.pop(1)
sys.argv[0]=str(scripts/tool)
if tool=='audio.py' and os.environ.get('V19_VOICE_THRESHOLD'):
    # Calibrate this project-local chain per recording, never edit the installed skill.
    spec=__import__('importlib.util',fromlist=['spec_from_file_location'])
    module_spec=spec.spec_from_file_location('audio_v19',scripts/'audio.py')
    module=spec.module_from_spec(module_spec);module_spec.loader.exec_module(module)
    threshold=float(os.environ['V19_VOICE_THRESHOLD'])
    module.VOICE_LEVELS['light']=(f'highpass=f=80,acompressor=threshold={threshold:g}dB'
                                ':ratio=2:attack=15:release=160:makeup=1')
    raise SystemExit(module.main())
runpy.run_path(str(scripts/tool),run_name='__main__')
