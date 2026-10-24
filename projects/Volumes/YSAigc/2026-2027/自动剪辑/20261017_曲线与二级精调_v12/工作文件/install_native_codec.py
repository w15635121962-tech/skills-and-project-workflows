from pathlib import Path
import shutil,json,hashlib
src=Path(__file__).parent/'上游源码';dst=Path('/Users/xuan/Codex_YS_Data/CodexHome/skills/resolve-color');files=[]
for folder in ['resolve-advanced/vendor/drx-codec','resolve-advanced/vendor/drx-parameters']:
 for p in (src/folder).rglob('*'):
  if not p.is_file():continue
  rel=p.relative_to(src);out=dst/rel
  if out.exists():assert out.read_bytes()==p.read_bytes(),f'Existing file differs: {out}'
  else:out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
  files.append({'path':str(rel),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
p=src/'resolve-advanced/package.json';out=dst/'resolve-advanced/package.json';assert not out.exists();shutil.copy2(p,out);files.append({'path':'resolve-advanced/package.json','sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size})
proof={'repository':'samuelgursky/davinci-resolve-mcp','commit':'90eba8cdf4df333beb4ce41fe0ab198b8fa7d125','license':'MIT','installation':'Native DRX codec libraries only; no persistent MCP server or project database writer installed','runtime':'Node 24.17.0 native zstd; no npm install needed for codec','files':files,'upstream_content_unmodified':True}
(dst/'NATIVE_CODEC_PROVENANCE.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2));(Path(__file__).parent/'installed_native_codec_v12.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2));print('INSTALLED',len(files),'files',sum(x['bytes'] for x in files),'bytes')
