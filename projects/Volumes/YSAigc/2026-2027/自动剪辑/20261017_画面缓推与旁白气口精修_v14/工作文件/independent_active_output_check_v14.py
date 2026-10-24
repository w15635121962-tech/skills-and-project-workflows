"""Offline only. Run after root confirms all replacement native images are complete."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
R=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_画面缓推与旁白气口精修_v14');W=R/'工作文件'
rows=json.loads((W/'native_motion_applied_v14.json').read_text());out=[]
for x in rows:
 before=Image.open(x['before']).convert('RGB');midfr=next(f for f in x['after_frames'] if f['label']=='中');after=Image.open(midfr['path']).convert('RGB');assert before.size==after.size==(1920,1080)
 aa=np.asarray(after,dtype=np.float32);bb=np.asarray(before,dtype=np.float32);raw=float(np.abs(aa-bb).mean());expected=float(x['size_first_mid_last'][1]);a=after.resize((640,360),Image.Resampling.LANCZOS);b=before.resize((640,360),Image.Resampling.LANCZOS);ref=np.asarray(a,dtype=np.float32);scores=[]
 # For R340 protect independently composited V2 title: compare image area above title.
 roi=(slice(12,220),slice(12,628)) if x['start']==340 else (slice(12,348),slice(12,628))
 for scale in sorted(set([1.0,expected]+[1+i*.001 for i in range(1,18)])):
  warped=b.transform(b.size,Image.Transform.AFFINE,(1/scale,0,320*(1-1/scale),0,1/scale,180*(1-1/scale)),resample=Image.Resampling.BICUBIC)
  err=float(np.abs(np.asarray(warped,dtype=np.float32)[roi]-ref[roi]).mean());scores.append({'scale':scale,'mae_8bit':err})
 best=min(scores,key=lambda y:y['mae_8bit']);base=next(y['mae_8bit'] for y in scores if y['scale']==1.0);exp=min(scores,key=lambda y:abs(y['scale']-expected))['mae_8bit']
 out.append({'track':x['track'],'start':x['start'],'before_mid':x['before'],'after_mid':midfr['path'],'raw_full_resolution_mid_MAD_8bit':raw,'pixel_identical':bool(np.array_equal(aa,bb)),'expected_mid_scale':expected,'best_fit_scale':best['scale'],'expected_scale_error_8bit':exp,'baseline_error_8bit':base,'expected_scale_error_reduction_fraction':1-exp/base if base else None,'comparison_roi':'image above independent V2 title' if x['start']==340 else 'full image minus12px margins at640px','before_sha256':hashlib.sha256(Path(x['before']).read_bytes()).hexdigest(),'after_sha256':hashlib.sha256(Path(midfr['path']).read_bytes()).hexdigest(),'scale_search':scores})
result={'scope':'离线独立比较27段同时间原生中帧的缓推前后输出，并拟合画面放大比例。非Resolve参数读回。','clip_count':len(out),'pixel_identical_starts':[x['start'] for x in out if x['pixel_identical']],'all_expected_scale_reduces_error':all(x['expected_scale_error_8bit']<x['baseline_error_8bit'] for x in out),'rows':out,'limitations':'PIL采样与Fusion滤镜不同；比例拟合为实际输出变化的独立交叉证据，不能替代连续视频检查。'}
(W/'缓推实际输出独立比对_v14.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({'path':str(W/'缓推实际输出独立比对_v14.json'),'clips':len(out),'identical':result['pixel_identical_starts'],'all_expected_scale_reduces_error':result['all_expected_scale_reduces_error'],'min_mid_MAD':min(x['raw_full_resolution_mid_MAD_8bit'] for x in out),'scale_fit':[{k:x[k] for k in ['start','expected_mid_scale','best_fit_scale','expected_scale_error_reduction_fraction']} for x in out]},ensure_ascii=False,indent=2))
