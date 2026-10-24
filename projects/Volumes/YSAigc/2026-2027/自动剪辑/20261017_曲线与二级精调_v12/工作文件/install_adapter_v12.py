from pathlib import Path
import json,hashlib
r=Path(__file__).parent;dst=Path('/Users/xuan/Codex_YS_Data/CodexHome/skills/resolve-color');script=(r/'native_drx.cjs').read_text();script=script[:script.index('if(require.main===module)')]
script=script.replace("path.join(__dirname,'上游源码/resolve-advanced/vendor/drx-codec')","path.join(__dirname,'../resolve-advanced/vendor/drx-codec')")
script=script.replace("async function make(originalBody,adjustments,label,out){","""async function make(originalBody,adjustments,label,out){
 const original=await parser.parseDRXBody(originalBody);if(original.nodes.length!==1)throw Error('Preserve adapter supports exactly one static original node. Use a full byte-preserving graph workflow for multi-node grades.');
 for(const n of adjustments){
  for(const pts of Object.values(n.params?.customCurves||{})){
   if(!Array.isArray(pts)||pts.some(p=>!Number.isFinite(p.x)||!Number.isFinite(p.y)||p.x<=0||p.x>=1||p.y<0||p.y>1))throw Error('Custom curve control points must be finite INTERIOR points (0 < x < 1). The upstream encoder supplies endpoints; duplicate endpoints can crash Resolve.');
   if(pts.some((p,i)=>i&&p.x<=pts[i-1].x))throw Error('Custom curve x coordinates must strictly increase.');
  }
  if(Object.keys(n.params?.hslCurves||{}).some(k=>['hueVsHue','hueVsSat','hueVsLum'].includes(k)))throw Error('Hue-axis cage emission requires the upstream canonicalizer. Raw hue-axis lists are refused by this minimal adapter.');
 }
""")
script+='''\nif(require.main===module)(async()=>{const request=process.argv[2];if(!request)throw Error('Usage: node native-secondary-grade.cjs request.json');const job=JSON.parse(fs.readFileSync(request));const body=job.baseBody || fs.readFileSync(job.baseDrx,'utf8').match(/<Body>([^<]+)<\\/Body>/)?.[1];if(!body)throw Error('Missing baseBody/baseDrx');if(fs.existsSync(job.output))throw Error('Output exists; choose a new file');const result=await make(body,job.nodes,job.label||'Native Curves and Secondary',job.output);if(job.report)fs.writeFileSync(job.report,JSON.stringify(result,null,2));console.log(JSON.stringify({path:result.path,nodeCount:result.nodes.length,baseCorrectionByteIdentical:result.originalF9SHA256===result.preservedF9SHA256}));})().catch(e=>{console.error(e.message);process.exitCode=1;});\n'''
out=dst/'scripts/native-secondary-grade.cjs';out.parent.mkdir(exist_ok=True);assert not out.exists();out.write_text(script)
note='''# 本机原生曲线与二级工具补充\n\n上游技能：samuelgursky/davinci-resolve-mcp 的 resolve-color，固定 commit 90eba8cdf4df333beb4ce41fe0ab198b8fa7d125，MIT。技能正文和上游 codec 保持原文，新增本地适配器便于既有官方 Python 脚本调用。未安装常驻 MCP 服务。\n\n`resolve-advanced/vendor/drx-codec` 与 `drx-parameters` 为逐字节复制的上游库，`NATIVE_CODEC_PROVENANCE.json` 记录每个文件哈希。Node 24 原生 zstd 可直接运行，不需要 npm 安装。\n\n`scripts/native-secondary-grade.cjs` 接收 request.json：`baseBody` 或 `baseDrx`、`nodes`（新增节点列表，params 内为原生 customCurves/qualifier/lumaQualifier/rgbQualifier）、`label`、`output` 和可选 `report`。已有单个静态节点的完整 F9 工具与 LUT 字节被保留，新曲线和二级节点串联在其后。复杂多节点、关键帧、OFX 等不得用这个最小适配器代替完整图复制。新文件再通过官方 `Graph.ApplyGradeFromDRX(path,0)` 应用到明确指定的克隆时间线/本地调色版本。\n\n自定义 YRGB 曲线只传 0<x<1 的内部控制点，编码器自带端点；严禁重复 x=1。Hue 轴曲线须使用上游 canonicalizer，本适配器拒绝原始 hue 轴列表。普通 drx-merger 会重建旧参数，不能作为无损保留原调色的捷径。\n\n执行前查看原生当前画面、保存版本和导出备份，先在隔离测试工程验证，再应用正式克隆时间线。应用后必须实帧比对并停用新节点验证原调色保留，不能把仅生成/离线解码通过当作达芬奇生效。\n'''
(dst/'LOCAL_NATIVE_CURVES.md').write_text(note)
manifest={'source':'Local integration adapter for pinned upstream codec','file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'curve_endpoints_guarded':True,'raw_hue_axis_refused':True,'base_node_tool_bytes_preserved':True,'full_mcp_installed':False,'live_compatibility':'Pending isolated Resolve 21 curve and qualifier verification; identity native test passed'}
(dst/'LOCAL_ADAPTER_PROVENANCE.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print('ADAPTER_INSTALLED',out)
