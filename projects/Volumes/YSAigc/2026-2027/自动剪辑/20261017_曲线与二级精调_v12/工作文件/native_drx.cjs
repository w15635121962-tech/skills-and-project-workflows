// Project adapter for the pinned MIT upstream DRX codec. Never modifies source media or project DB.
const fs=require('node:fs'),path=require('node:path'),z=require('node:zlib'),crypto=require('node:crypto');
const base=path.join(__dirname,'上游源码/resolve-advanced/vendor/drx-codec');
const gen=require(path.join(base,'drx-generator-local-compat.js'));const parser=require(path.join(base,'drx-parser.js'));
function decode(hex){const b=Buffer.from(hex,'hex');if(b[0]===0x80)return b.subarray(1);if(b[0]!==0x81)throw Error('Unknown Body');return z.zstdDecompressSync(b.subarray(1));}
function parsed(buf){return new parser.ProtobufParser(buf).parse(12);}
function v(n){let a=[];do{let b=n%128;n=Math.floor(n/128);a.push(b|(n?128:0));}while(n);return Buffer.from(a);}
function bytes(f,b){return Buffer.concat([v(f*8+2),v(b.length),b]);}
function rebuild(buf,fields,replacements){return Buffer.concat(fields.map((f,i)=>[...replacements.entries()].find(([k])=>k.pos===f.pos&&k.fieldNum===f.fieldNum)?.[1]??buf.subarray(f.pos,i+1<fields.length?fields[i+1].pos:buf.length)));}
function field(msg,num){const f=parsed(msg)._fields.filter(x=>x.fieldNum===num&&x.wireType===2);if(f.length!==1)throw Error('Expected one field '+num+', got '+f.length);return f[0];}
function firstNode(body){const r=decode(body);const f1=field(r,1);const f7=parsed(f1.rawValue)._fields.find(x=>x.fieldNum===7);if(!f7)throw Error('Missing node');return Buffer.from(f7.rawValue);}
function fixCustomCurveMeta(body){
 const dec=decode(body);let count=0;
 for(const id of [0x860000bb,0x860000bd,0x860000be,0x860000bf]){const prefix=Buffer.concat([Buffer.from([8]),v(id),Buffer.from([0x12,2,0x10])]);let pos=0;while((pos=dec.indexOf(prefix,pos))>=0){const at=pos+prefix.length;if(dec[at]>=128)throw Error('Unsupported curve meta');dec[at]=2;count++;pos=at+1;}}
 return '81'+z.zstdCompressSync(dec).toString('hex');
}
function transplant(generatedBody,originalBody){
 const originalNode=firstNode(originalBody),sourceF9=field(originalNode,9);const dec=decode(generatedBody),root=parsed(dec),f1=field(dec,1),fc=Buffer.from(f1.rawValue),fp=parsed(fc),n=fp._fields.find(f=>f.fieldNum===7),nc=Buffer.from(n.rawValue),np=parsed(nc),f9=field(nc,9);
 const newNode=rebuild(nc,np._fields,new Map([[f9,bytes(9,Buffer.from(sourceF9.rawValue))]]));const newFC=rebuild(fc,fp._fields,new Map([[n,bytes(7,newNode)]]));const newRoot=rebuild(dec,root._fields,new Map([[f1,bytes(1,newFC)]]));const out='81'+z.zstdCompressSync(newRoot).toString('hex');
 const outF9=field(firstNode(out),9);if(!Buffer.from(outF9.rawValue).equals(Buffer.from(sourceF9.rawValue)))throw Error('Original correction bytes changed');return out;
}
async function make(originalBody,adjustments,label,out){
 const existing=await parser.parseDRXBody(originalBody);if(existing.nodes.length>1)throw Error('Only zero or one original node is supported');const hasOriginal=existing.nodes.length===1;const nodes=[{label:hasOriginal?'01_BASE_v11_PRESERVED':'01_BASE_UNGRADED',params:hasOriginal?{contrast:1.01}:{}},...adjustments];const con=nodes.slice(1).map((_,i)=>({from:i+1,to:i+2}));let xml=await gen.generateMultiNodeDRX(nodes,con,{label,sourceTimeline:'学校_曲线与二级精调_v12_20261017',recordTC:'00:00:00:00'});
 const body=xml.match(/<Body>([^<]+)<\/Body>/)[1],merged=hasOriginal?transplant(fixCustomCurveMeta(body),originalBody):fixCustomCurveMeta(body);xml=xml.replace(body,merged);fs.writeFileSync(out,xml);const p=await parser.parseDRXContent(xml);
 return {path:out,nodes:p.nodes.map(x=>({id:x.id,label:x.label,params:x.params,customCurves:x.customCurves,hslCurves:x.hslCurves,qualifier:x.qualifier})),connections:p.connections,originalF9SHA256:hasOriginal?crypto.createHash('sha256').update(field(firstNode(originalBody),9).rawValue).digest('hex'):null,preservedF9SHA256:hasOriginal?crypto.createHash('sha256').update(field(firstNode(merged),9).rawValue).digest('hex'):null,originalNodeCount:existing.nodes.length};
}
module.exports={make,decode,parsed,field,firstNode,gen,parser};
if(require.main===module)(async()=>{const r=JSON.parse(fs.readFileSync(path.join(__dirname,'original_grade_bodies_v11.json'))).find(x=>x.track===1&&x.start===117);const out=path.join(__dirname,'../原生调色文件/identity_preserve117.drx');const result=await make(r.body,[{label:'02_IDENTITY_TEST',params:{}}],'v12_identity_preserve117',out);fs.writeFileSync(path.join(__dirname,'identity_drx117.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({nodes:result.nodes.length,hash_preserved:result.originalF9SHA256===result.preservedF9SHA256,path:out}));})();
