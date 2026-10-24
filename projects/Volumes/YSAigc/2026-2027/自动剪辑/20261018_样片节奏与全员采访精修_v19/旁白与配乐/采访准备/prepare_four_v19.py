import json, os, subprocess, sys, concurrent.futures
from pathlib import Path
import numpy as np, soundfile as sf

ROOT=Path(__file__).resolve().parent
WRAP=ROOT/'run_skill_pcm24.py'
plan=json.loads((ROOT.parents[1]/'工作文件/采访最终方案/four_speaker_plan_final.json').read_text())
settings={
 '书记':{'nf':60,'threshold':-18},
 '金台书院小学':{'nf':53,'threshold':-28},
 '前门外国语学校':{'nf':50,'threshold':-29},
 '文汇小学':{'nf':51,'threshold':-25},
}

def run(row):
    stem=Path(row['source']).stem
    src=ROOT/f'{stem}_channel0_原声全覆盖.wav'
    nr=ROOT/f'{stem}_01_轻降噪_全覆盖.wav'
    eq=ROOT/f'{stem}_02_高通与温和压缩_全覆盖.wav'
    norm=ROOT/f'{stem}_03_目标电平_全覆盖.wav'
    cfg=settings[row['speaker_key']]
    env=os.environ.copy();env['PYTHONUTF8']='1'
    cmds=[('probe',[str(Path('/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts/probe.py')),str(src),'--json']),
          ('source_loudness',[str(WRAP),'loudness.py',str(src),'--measure-only','-I','-16','--tp','-2.2','--json']),
          ('denoise',[str(WRAP),'audio.py',str(src),'--denoise','--denoise-strength',str(cfg['nf']),'-o',str(nr),'--json']),
          ('voice',[str(WRAP),'audio.py',str(nr),'--voice','light','-o',str(eq),'--json']),
          ('normalize',[str(WRAP),'loudness.py',str(eq),'-I','-16','--tp','-2.2','--lra','20','--sample-rate','48000','-o',str(norm),'--json'])]
    rec={'speaker':row['speaker_key'],'original':row['channels_wav'],'channel_zero_based':0,
         'source_channel0':str(src),'intermediate_normalized':str(norm),'settings':cfg,'steps':[],
         'recipe':{'noise_reduction':f'afftdn=nf=-{cfg["nf"]}:tn=1',
                   'highpass':'highpass=f=80',
                   'compressor':f'acompressor=threshold={cfg["threshold"]}dB:ratio=2:attack=15:release=160:makeup=1',
                   'normalization':'two-pass loudnorm I=-16 TP=-2.2 LRA=20 48k PCM24',
                   'gate':'none','time_editing':'none','audition':'unavailable; measurements and waveform comparison only'}}
    for label,args in cmds:
        stage_env=env.copy()
        if label=='voice':stage_env['V19_VOICE_THRESHOLD']=str(cfg['threshold'])
        command=[sys.executable,*args]
        if label in ['denoise','voice','normalize']:
            dry=command+['--dry-run']
            result=subprocess.run(dry,env=stage_env,capture_output=True,text=True)
            (ROOT/f'{stem}_{label}_dryrun.json').write_text(result.stdout)
            (ROOT/f'{stem}_{label}_dryrun.log').write_text(result.stderr)
            if result.returncode:raise RuntimeError(label+' dryrun '+result.stdout+result.stderr)
        result=subprocess.run(command,env=stage_env,capture_output=True,text=True)
        (ROOT/f'{stem}_{label}.json').write_text(result.stdout)
        (ROOT/f'{stem}_{label}.log').write_text(result.stderr)
        if result.returncode:raise RuntimeError(label+' '+result.stdout+result.stderr)
        rec['steps'].append({'label':label,'command':command,'log':str(ROOT/f'{stem}_{label}.log'),
                             'result':json.loads(result.stdout)})
    (ROOT/f'{stem}_recipe.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2))
    return rec

if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(run,plan))
    (ROOT/'processing_recipes_v19.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
    print(json.dumps([{'speaker':r['speaker'],'file':r['intermediate_normalized']} for r in results],ensure_ascii=False))
