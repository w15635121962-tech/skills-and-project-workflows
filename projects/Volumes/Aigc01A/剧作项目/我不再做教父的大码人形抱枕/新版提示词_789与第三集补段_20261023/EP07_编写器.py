import json,re,argparse,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'输入/EP07_当前批准稿.json'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def fmt(v):
    s=f'{float(v):.2f}'.rstrip('0').rstrip('.')
    return s if '.' in s else s+'.0'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--batch',required=True);args=ap.parse_args()
    source=load(SOURCE);by={x['shot']:x for x in source}
    output=ROOT/'EP07_新版提示词.json'
    current=load(output) if output.exists() else []
    merged={x['source_id']:x for x in current}
    for r in load(Path(args.batch)):
        old=by[r['shot']];d=old['duration'];segments=r['segments']
        assert segments[0][0]==0 and segments[-1][1]==d,(r['shot'],segments,d)
        for i,s in enumerate(segments):
            assert s[0]<s[1] and (i==0 or segments[i-1][1]==s[0])
        assets='；'.join('@'+x for x in old['asset_names']) if old['asset_names'] else '本镜无具象角色或场景引用'
        movement='；'.join(fmt(a)+'—'+fmt(b)+'秒：'+text for a,b,text in segments)+'。'
        lines=['**Shot '+str(r['shot'])+'：'+r['title']+'（'+old['source_id']+'）**','',
               '参考资产：'+assets+'。画幅9:16，正常速度；人物身份、体型及外观以对应既定资产为准，衣物扣合并保持遮盖。','',
               '时长：'+fmt(d)+'秒。','环境氛围：'+r['environment']+'。',
               '景别：'+r['size']+'。','拍摄角度：'+r['angle']+'。',
               '摄像机运动：'+r['camera_movement']+'。',
               '人物角色和运动：'+movement,'人物表演：'+r['performance']+'。',
               '画面内容：'+r['frame']+'。']
        dialogues=old['dialogue'];sounds=r.get('sounds','轻微衣料和床面接触声、正常轻微呼吸及房间底声')
        audio=sounds+'。'
        for q in dialogues:
            who=q['speaker'];mode=q.get('delivery')
            audio+=who+('（电话画外音，画内两人不跟随其台词张口）' if mode=='telephone_offscreen' else '（画内原对白）')+'：“'+q['text']+'”。'
            if q.get('continuation_of'):audio+='承接上一镜同一通话句，不重复已说词语。'
        audio+='无旁白、背景音乐、字幕或其他新增对白；'+('仅原说话者按原句自然同步口型，其他可见人物保持沉默。' if any(q.get('delivery')=='in_scene' for q in dialogues) else '画内人物不产生说话口型。')
        lines.append('音频：'+audio)
        prompt='\n'.join(lines)
        for q in dialogues:assert prompt.count(q['text'])==1
        assert not any(s in prompt for s in ['FIRST FRAME','STIMULUS','POSITION LOCK','固定画质词','叙事任务（'])
        merged[old['source_id']]={'source_id':old['source_id'],'duration':d,'asset_names':old['asset_names'],'new_prompt':prompt,'issues':r.get('issues',[])}
    result=sorted(merged.values(),key=lambda x:int(x['source_id'].split('S')[-1]))
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'EP07_新版提示词.md').write_text('# 女版第7集·新版逐镜提示词\n\n'+ '\n\n---\n\n'.join(x['new_prompt'] for x in result),encoding='utf-8')
    print(json.dumps({'written':len(result),'latest_batch':args.batch,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest()},ensure_ascii=False))
if __name__=='__main__':main()

