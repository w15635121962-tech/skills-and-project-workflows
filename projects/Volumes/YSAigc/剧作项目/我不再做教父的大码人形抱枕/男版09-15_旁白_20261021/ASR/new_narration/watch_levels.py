"""Keep source levels current for new narrator files already blindly recognized."""
import json,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
started=time.monotonic();previous=None
while time.monotonic()-started<3600:
 p=HERE/'转录索引.json'
 if p.exists():
  x=json.loads(p.read_text());signature=tuple((f['source_path'],f['source_sha256']) for f in x['files'])
  if signature!=previous:
   q=subprocess.run([sys.executable,str(HERE/'measure_new_narration.py')],check=True)
   previous=signature
   print(json.dumps(dict(levels_updated_for=len(signature),elapsed_seconds=round(time.monotonic()-started))),flush=True)
 time.sleep(5)
