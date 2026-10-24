const fs=require('node:fs'),path=require('node:path'),lib=require('./native_drx.cjs');const root=path.resolve(__dirname,'..'),original=JSON.parse(fs.readFileSync(path.join(__dirname,'original_grade_bodies_v11.json'))),advice=JSON.parse(fs.readFileSync(path.join(__dirname,'二级逐镜建议.json'))).candidates;
const cage=(lift=0,toe=0,shoulder=0)=>[{x:1/6,y:1/6+toe},{x:1/3,y:1/3+lift*.55},{x:.5,y:.5+lift},{x:2/3,y:2/3+lift*.55},{x:5/6,y:5/6+shoulder}];
const curves=p=>({customCurvesFormat:'bezier-cage',customCurves:{y:p,r:p,g:p,b:p}});
const skin=(extra={})=>({hueCenter:33.5,hueWidth:17,hueSoft:6,hueSymmetry:50,satLow:1.5,satHigh:100,satLowSoft:.7,satHighSoft:0,lumLow:15,lumHigh:85,lumLowSoft:10,lumHighSoft:10,...extra});
const scene={label:'02_GENTLE_TONAL_CURVE',params:curves(cage(.004,-.0005,0))};
(async()=>{let records=JSON.parse(fs.readFileSync(path.join(__dirname,'sample_specs_v12.json')));for(const row of advice.filter(x=>x.priority==='gentle_match')){const track=row.track,start=row.record_frame;if(records.some(x=>x.track===track&&x.start===start))continue;let nodes=[scene],q=skin(),params={},label='03_SKIN_FINE_BALANCE';
 if(row.group==='科技教室肤色一致性')params={...curves(cage(start===7151?.006:.009,0,0)),tint:1.2,temperature:-15};
 else if(row.group==='化学实验肤色一致性')params={...curves(cage(.006,0,0)),saturation:48.5,tint:-.5,temperature:15};
 else if(start===1135){label='03_LIBRARY_CYAN_GREEN';q={hueCenter:64,hueWidth:24,hueSoft:8,hueSymmetry:50,satLow:1.5,satHigh:100,satLowSoft:.6,satHighSoft:0,lumLow:10,lumHigh:90,lumLowSoft:10,lumHighSoft:10};params={saturation:48.5};}
 else if(start===6195)params={...curves(cage(.006)),tint:.7,temperature:15};
 else if(start===5382){q=skin({satHigh:8,satHighSoft:1});params={...curves(cage(.005)),saturation:49,temperature:-20,tint:.4};}
 else if(start===6909){label='03_TROPHY_GREEN_BACKGROUND';q={hueCenter:62,hueWidth:24,hueSoft:6,hueSymmetry:50,satLow:2,satHigh:100,satLowSoft:.7,satHighSoft:0,lumLow:8,lumHigh:94,lumLowSoft:8,lumHighSoft:6};params={saturation:46};nodes=[{label:'02_GOLD_DETAIL_CURVE',params:curves(cage(.003,0,-.002))}];}
 else throw Error('Unmapped shot '+start);
 nodes.push({label,params:{...params,qualifier:q}});const old=original.find(x=>x.track===track&&x.start===start);if(!old)throw Error('Missing base '+start);const target=path.join(root,'原生调色文件',`v12_${track}_${start}.drx`);const result=await lib.make(old.body,nodes,`v12_${track}_${start}`,target);records.push({track,start,frame:row.examined_frame,reason:row.conservative_goal,group:row.group,...result});}
 records.sort((a,b)=>a.track-b.track||a.start-b.start);fs.writeFileSync(path.join(__dirname,'all_grade_specs_v12.json'),JSON.stringify({count:records.length,records},null,2));console.log('ALL_NATIVE_GRADES_READY',records.length);})();
