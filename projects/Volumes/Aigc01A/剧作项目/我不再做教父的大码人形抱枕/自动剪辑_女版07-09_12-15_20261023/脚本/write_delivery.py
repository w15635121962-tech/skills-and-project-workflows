from native_common import *
p=load_plan(BASE/'final_native_plan.json');v=read(BASE/'Resolve_保存重开核验.json')
lines=['# 女版7、8、9、12、13、14、15集自动剪辑','',
       '工程：`大码枕头`。本次另建七条可编辑时间线；原有66条时间线保留。画面与原片同期声逐段同源、同入出点并链接，新女版旁白按100%原速逐句穿插原对白。','',
       '| 素材集号 | 原文Episode | 时长 | 画面/链接同期声段数 | 旁白段数 | SRT条数 |',
       '|---|---|---:|---:|---:|---:|']
for e in p['episodes']:
    lines.append(f"| {e['episode']} | {e['source_script_episode']} | {e['duration_frames']/24:.3f}秒 | {len(e['video'])} | {len(e['narration'])} | {e['subtitle_cue_count']} |")
lines+=['','七集共155组链接画面/同期声、82段旁白、221条原生SRT。时间线24fps、1080×1920；源视频为480×854，沿用源片清晰度。每条字幕最多三行，已按语义合并短尾词；字幕轨数字为7、8、9、12、13、14、15。','',
        '流程：新建字幕轨 → SRT按时间码入轨并逐条回读 → 激活字幕轨检查器 → 指定预设“九州海外短剧 Preset 字幕 Preset” → 加载预设 → 保存重开回读。','',
        '## 可编辑时间线及最终SRT','']
for e in p['episodes']:
    lines.append(f"- 第{e['episode']}集：`{e['timeline_name']}`；[SRT]({e['subtitle_srt']})。")
lines+=['','## 核验','',
        '- 原文剧情、旁白/原对白顺序、源词时码、实际PCM剪口已核对；无旁白覆盖对白、无重复源帧。第8集四处句首专名已恢复，第9集重复反应画面已替换。',
        '- 每条画面与对应同期声的源文件、源入出点、时间线入出点均一致并原生链接。全部旁白与画面保持原速。',
        '- 电平分析七集无采样削波；紧余量EP08/12/13真峰值约-1.0/-1.4/-1.3 dBTP。',
        '- 七集各完成一次约4秒实际短段播放，播放头推进102–103帧，停止后帧稳定。',
        '- 七集各查看首条、中段、最长、末条字幕，共28处实际Resolve查看器画面。三行字幕未越出竖屏画幅。截图在画面验收文件夹。',
        '- 已保存并重开工程，回读源范围、同源链接、轨道启用、全部字幕文字/时间码及字幕样式持久化。',
        '', '## 实际边界','',
        '- 完成自动剪辑及以上抽查，尚未逐帧通看全片或做完整人耳听审。',
        '- 源旁白07“stroked/struck”、源同期12“wincing”的发音存在识别歧义；保留用户源录音，字幕按原文，未擅自重新配音。',
        '- 片内“next video”等高压缩重复识别经过二次盲识别复核，未写入字幕；原片自然声保留。',
        '- 未提交成片渲染或外部发送。DRP为工程备份，DRT为可编辑时间线备份。',
        '', '## 文件','',
        f"- [最新工程备份]({v['project_export']})。",
        '- [保存重开核验](Resolve_保存重开核验.json)、[短段回放](短段实际播放核验.json)、[字幕原生回读](字幕/SRT_原生入轨回读.json)、[全部剪辑计划](final_native_plan.json)。',
        '- [第7集字幕画面抽查](画面验收/EP07_字幕画面抽查.jpg)。']
(BASE/'女版七集_剪辑与字幕清单.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
write(BASE/'画面验收/人工视觉抽查记录.json',{'episodes':[e['episode'] for e in p['episodes']],
      'case_count':28,'observed_cases':['first','middle','longest','last'],'checked_in_actual_resolve_viewer':True,
      'text_visible_within_portrait':True,'maximum_explicit_lines':3,'contact_sheets':[str(BASE/f'画面验收/EP{e["episode"]:02}_字幕画面抽查.jpg') for e in p['episodes']],
      'limit':'Still-frame visual sample review plus short transport playback, not full shot-by-shot watch-through or complete auditory acceptance.'})
print('Delivery document and 28-case visual review record written.')
