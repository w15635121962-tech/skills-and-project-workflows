"""Bounded local file watcher; recognizes each newly completed EP20 download.

This is part of the current authorized task, not a scheduled automation.
No UI, network upload, generation, or Resolve. Recognizer never reads the script.
"""
from pathlib import Path
import argparse
import json
import re
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
DIRECTORY=HERE.parent/'\u97f3\u9891/\u7b2c20\u96c6'
PATTERN=re.compile(r'\u5927\u7801\u7537\u7248\u6795\u593420-(\d{2})-(\d{2})\.mp3')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--max-seconds',type=int,default=1800);args=ap.parse_args()
    assert 1<=args.max_seconds<=7200
    started=time.monotonic();seen={};last_status=None
    while time.monotonic()-started<args.max_seconds:
        current={}
        for path in sorted(DIRECTORY.glob('*.mp3')) if DIRECTORY.exists() else []:
            if not PATTERN.fullmatch(path.name):continue
            stat=path.stat()
            if stat.st_size>0 and time.time()-stat.st_mtime>=2:
                current[str(path)]=(stat.st_size,stat.st_mtime_ns)
        if current and current!=seen:
            completed=subprocess.run([sys.executable,str(HERE/'recognize_downloaded_narration.py'),'--execute'],capture_output=True,text=True,encoding='utf-8')
            print(completed.stdout,flush=True)
            if completed.returncode:
                print(completed.stderr,flush=True)
                # A source may have only just finished moving. Keep its failure
                # visible and retry after the next stable observation.
            else:seen=current
        index_path=HERE/'narration_index.json'
        index=json.loads(index_path.read_text(encoding='utf-8'))if index_path.exists()else{'files':[],'errors':[]}
        logical={x['sequence']for x in index['files']}
        status=(len(index['files']),tuple(sorted(logical)),len(index['errors']))
        if status!=last_status:
            print(json.dumps(dict(recognized_files=status[0],logical_segments=list(status[1]),errors=status[2]),ensure_ascii=False),flush=True);last_status=status
        if set(range(1,10))<=logical and not index['errors']:
            print(json.dumps(dict(completed=True,logical_segments=9,all_expected_source_files_recognized=True),ensure_ascii=False),flush=True);return
        time.sleep(5)
    print(json.dumps(dict(stopped_at_time_limit=True,last_status=last_status),ensure_ascii=False),flush=True)

if __name__=='__main__':main()
