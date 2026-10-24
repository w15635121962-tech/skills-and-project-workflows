#!/usr/bin/env python3
"""Summarize evidence and uncertainties without changing either raw ASR pass."""
import csv
from collections import Counter, defaultdict
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent


def main():
    first=json.loads((ROOT/'转录索引.json').read_text())
    second=json.loads((ROOT/'第二模型复核索引.json').read_text())
    inventory=json.loads((ROOT.parent/'素材盘点.json').read_text())
    reviews={x['source_path']:x for x in second['files']}
    aliases=defaultdict(list)
    for row in inventory['files']:
        aliases[row['sha256']].append(row['path'])
    rows=[]
    total_words=0
    for row in first['files']:
        raw=json.loads(Path(row['json_path']).read_text())
        words=raw['words']
        tokens=re.findall(r"[a-z]+(?:'[a-z]+)?",row['text'].lower())
        flags=list(row['quality_flags'])
        zeros=sum(w['end']<=w['start'] for w in words)
        if zeros: flags.append('zero_duration_word')
        if not tokens: flags.append('no_lexical_words')
        repeated=[]
        for n, threshold in [(2,4),(4,3)]:
            counts=Counter(tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1))
            repeated.extend([' '.join(k) for k,v in counts.items() if v>=threshold])
        if repeated: flags.append('repeated_phrase')
        review=reviews.get(row['source_path'])
        if review and review['token_sequence_similarity']<0.65:
            flags.append('second_model_disagrees')
        strong=[x for x in flags if x in ['no_lexical_words','repeated_phrase',
                                         'second_model_disagrees','word_time_out_of_source_bounds']]
        lexical=[w for w in words if re.search('[A-Za-z]',w['word'])]
        total_words+=len(words)
        rows.append(dict(episode=row['episode'],kind=row['kind'],source_path=row['source_path'],
                         source_sha256=row['source_sha256'],same_bytes_other_paths=[x for x in aliases[row['source_sha256']] if x!=row['source_path']],
                         decoded_duration_seconds=row['decoded_duration_seconds'],
                         first_word_start=lexical[0]['start'] if lexical else None,
                         last_word_end=lexical[-1]['end'] if lexical else None,
                         word_count=len(words),zero_duration_word_count=zeros,
                         recognized_text=row['text'].strip(),quality_flags=flags,
                         repeated_ngrams=sorted(set(repeated)),
                         second_model_text=review['second_pass_text'].strip() if review else None,
                         token_sequence_similarity=review['token_sequence_similarity'] if review else None,
                         unreliable_for_unreviewed_dialogue_subtitles=bool(strong),
                         human_listening_validation=False,
                         first_pass_json=row['json_path'],
                         second_pass_json=review['review_json'] if review else None))
    report=dict(scope='EP21–25, 64 video sources and 18 canonical narration sources',
                raw_asr_unchanged=True,source_media_unchanged=True,
                expected_script_supplied_to_model=False,audio_uploaded=False,
                first_pass=dict(model='large-v3-turbo',files=first['completed'],errors=first['errors'],words=total_words),
                second_pass=dict(model='small.en',files=second['completed']),
                source_timestamp_basis='seconds relative to original source audio; ASR-estimated alignment, not timeline time',
                subtitle_status='Source ASR SRT sidecars only; final edit and final timeline SRT are outside this transcription task.',
                hearing_capability='Offline model recognition/alignment was executed. No per-file subjective listening or lip-sync acceptance was performed.',
                flag_counts=dict(Counter(flag for row in rows for flag in row['quality_flags'])),
                files_requiring_review_before_dialogue_subtitles=sum(x['unreliable_for_unreviewed_dialogue_subtitles'] for x in rows),
                files=rows)
    (ROOT/'转录质量核对.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    columns=['episode','kind','source_path','decoded_duration_seconds','first_word_start','last_word_end',
             'word_count','zero_duration_word_count','quality_flags','unreliable_for_unreviewed_dialogue_subtitles',
             'recognized_text','second_model_text','token_sequence_similarity','first_pass_json','second_pass_json']
    with (ROOT/'转录质量核对.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,columns,extrasaction='ignore')
        writer.writeheader()
        for row in rows:
            writer.writerow({**row,'quality_flags':'; '.join(row['quality_flags'])})
    for episode in range(21,26):
        text=[]
        for row in rows:
            if row['episode']==episode:
                text.append(f"[{row['kind']}] {Path(row['source_path']).name}\n{row['recognized_text']}\n")
        (ROOT/f'EP{episode}_原始听写.txt').write_text('\n'.join(text),encoding='utf-8')
    readme=f'''# EP21–25本地盲转录

已完成large-v3-turbo首轮82条（64视频、18独白），{total_words}个原始词条，运行错误0；其中34条由small.en独立复核。

这些是本机对真实源音频的自动识别输出及模型估计的词级/段落对齐，不是按剧本填词。模型从未接收源剧本、预期对白或人物姓名提示。不同take独立保留；独白的另一套相同字节路径在质量表same_bytes_other_paths记录。没有上传音频，也没有修改源媒体或操作Resolve。

- `转录索引.json`：82条源、原始听写、低置信标记及文件位置。
- `raw_large-v3-turbo/EP*/video或narration/*.json`：完整原始结果、逐词start/end/probability和段落时间。
- 同目录`*.words.tsv`及`*.segments.srt`：源音频时基的词表和段落字幕。尚未换算成最终剪辑时间线。
- `第二模型复核索引.json`、`raw_small.en_review/`：34条独立第二模型结果，未覆盖首轮。
- `转录质量核对.json/.csv`：同字节路径、首末词范围、零时长词、重复片语和模型分歧。

质量表中{report['files_requiring_review_before_dialogue_subtitles']}条有无词、异常重复或两模型明显分歧，不能未经听音复核就自动作为对白字幕。无对白/音乐片段可能被Whisper听成厨房、加水或重复道歉等无关句子，原始结果保留为证据。低置信词也可能只是人名或专有词，并非自动判定素材错误。词时码为ASR对齐估计；零时长词不应用作精确剪切边界。

实际听音能力：已执行离线音频识别与词对齐，尚未对每条做主观听音、人物归属或口型验收。最终SRT只能依据实际采用且确认可听的轨道；不要把画外独白同时保留两份，也不要把模型幻听写进成片。

环境复用：原ASR虚拟环境的Python框架已不存在，其MLX轮子针对macOS26；本次使用Codex内置Python3.12和隔离目录`runtime_compatible`的macOS15轮子，复用原有mlx-whisper包及本地模型。模型及源媒体在识别前后均校验SHA-256，离线模式禁止模型联网下载。
'''
    (ROOT/'转录说明.md').write_text(readme,encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['first_pass','second_pass','flag_counts','files_requiring_review_before_dialogue_subtitles']},ensure_ascii=False))


if __name__=='__main__':main()
