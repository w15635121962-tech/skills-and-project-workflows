---
name: short-drama-sgroup-storyboard
version: 1.2.0
description: |
  短剧 S 组分镜系统（SD2.0 挂载版）。把剧本重新设计成"能看懂、能代入、能剪出来"的镜头方案：
  情绪优先 → S 组情绪钩子 → 台词画面绑定 → 表演气口 → 组间尾帧衔接 → SD2.0 挂载与
  Positive/Negative 提示词 → 单人镜头防穿帮 → 自检 → Word 输出。

  每条输出都包含：全集资产清单、人物/场景/道具/VFX 挂载 ID、每个 S 组的剧情与情绪任务、
  逐镜时长/景别/画面/调度运镜/声音台词/尾帧、每组 SD2.0 正反向提示词、台词画面绑定说明、自检表。

  触发词：短剧分镜 · S组分镜 · S组 · 分镜SD2 · SD2.0挂载 · 挂载ID · 台词画面绑定 ·
  表演气口 · 情绪钩子 · 组间衔接 · 尾帧设计 · 防穿帮 · 单人镜头 · 人脸一致性 ·
  重复人物 · 背景乱生人 · 月纹 · 身体发光 · 分镜经验总结 · 爆款短剧分镜 · 分镜自检 ·
  短剧导演 · 一集分镜 · 单集分镜 · 竖屏短剧分镜 · short drama storyboard · S-group ·
  shot group · mounting ID · dialogue-visual binding · anti-artifact

  不触发：纯分镜表格（→storyboard-table）· AI 视频提示词组 Format C（→short-drama-video-prompts）·
  焦段提示词网格（→focal-grid）· 多镜头序列提示词（→multishot-cinematic）·
  角色/场景/道具资产提取（→character-asset / scene-asset / script-props-extractor）·
  剧本创作与诊断
agent_created: true
---

# 短剧 S 组分镜系统 · Short Drama S-Group Storyboard

把剧本重新设计成观众能看懂、能代入、能剪出来的镜头方案。分镜不是把剧本翻译成画面，而是把
**剧情情绪、人物关系、台词气口和剪辑节奏**重新设计一遍。

## 最高优先级硬规则（不得绕过、简化或妥协）

1. **每个 S 组 ≤ 15 秒。** 超过 15 秒必须拆成 A/B 组。
2. **每个 S 组必须有至少一个明确情绪钩子**（轻蔑变僵硬 / 强撑变松动 / 炫耀变失控 …），
   不能只是"人走、人看、人站"。
3. **每句台词必须有画面绑定**：说话人近景 / 听者反应 / 手部动作 / 道具证据 / 站位变化 / 情绪特写，至少其一。
4. **严禁 1.8 秒塞完整长句。** 超长句必须拆镜、切听者反应、留气口。
5. **每个 S 组必须有挂载 + SD2.0 Positive Prompt + Negative Prompt。** 三者缺一不可。
6. **每个 S 组必须有尾帧/剪辑设计**，下一组首镜要接住上一组的动作、声音或道具。
7. **每组尽量一镜一张清晰脸。** 多人关系靠切镜，不靠同框；背景人物只能虚化、背影、侧影。
8. **禁止词零出现**：月纹、眼睛冒光、瞳孔发光、身体发光、发亮/亮起、露骨、血腥、
   莫名其妙空镜、不解释的白布与无意义遮挡物。
9. **输出前必须过自检表**，未通过不得交付。
10. **默认输出 Word 可打开文档**（用户另有要求除外）。
11. **无台词组必须连续编号且数量准确。** 每个无台词组在台词绑定行标注「**第 N 个无台词组**」，
    编号从 1 连续排到最后，不许出现"第 1～6 个"却实际有 9 个的情况。无台词组不是空镜，必须靠
    **2–3 个手部/身体动作 + 一段呼吸或环境声**撑住，时长压到 **8–10 秒**。交付前复核：

    ```bash
    grep -c -E '台词绑定\*\*：本组无台词' part-*.md    # 实际数量
    grep -o -E '第[一二三四五六七八九十]+个无台词组' part-*.md   # 编号序列
    ```
12. **非逐句取自原稿的台词必须标注校对清单。** 原稿不在工作区时**不许静默补写**：要在该集分片顶部
    加可见横幅，并在自检文件里按集列出逐句校对清单，通过声明后追加「保留项」。规程见
    [references/output-and-selfcheck.md](references/output-and-selfcheck.md) 第 2.4 节。

## 工作流

按五步顺序执行，每步产出后再进入下一步。

```
STEP 1 → SCOPE    读剧本，拆 S 组，定情绪主线与全集资产清单
STEP 2 → LOCK     人物/场景/道具/VFX 挂载 ID 与全集人脸一致性锁定
STEP 3 → BOARD    逐组输出：情绪卡 + 台词绑定卡 + 挂载 + SD2.0 提示词 + 逐镜表
STEP 4 → CHECK    过自检清单，逐项修复
STEP 5 → EXPORT   输出分镜 MD + Word 文件
```

**硬规则：**
- 不跳过、不合并、不省略任何 S 组。
- 每个镜头都要回答：**"观众为什么需要看到这个画面？"**
- STEP 4 未通过前不声明完成。
- 找不到对应规则时，回到本文件"关键判断标准"。

## 核心原则速记

| 原则 | 含义 | 反面 |
|---|---|---|
| **情绪优先** | 先定"这组要让观众感受到什么"，再排画面 | 先摆画面再补情绪 |
| **故事叙事优先** | 每个镜头都要推进剧情或关系 | 空镜太多、镜头好看但不推进 |
| **证据链** | 道具 → 角色反应 → 关系变化 → 结果 | 道具突然出现却不解释 |
| **台词画面绑定** | 台词说的是 A，画面就得拍 A | 台词说 A，画面拍 B |
| **可剪辑** | 每组有起点、变化、尾帧 | 前后组突然跳戏、接不上 |

**常见情绪任务**：炫耀（靠近、压低声音、拨弄道具、看对方反应）· 委屈（手指、喉咙、呼吸、
眼神躲闪、衣料被抓皱，不要只写哭）· 冷眼看戏（不哭不崩溃，静看对手毁灭）· 震惊（呼吸停住、
肩颈僵住、眼神失焦，不是大张嘴）· 安抚（手的落点、身体遮挡、低声鼓励、视线稳定）·
史诗感（事件因果、空间层级、站位、声画节奏，不靠堆大场面）。

## 快速参考

### 景别职责

| 景别 | 负责内容 | 使用原则 |
|---|---|---|
| 远景 | OS、心境、孤独、命运感 | 少用，只承载氛围与心理距离 |
| 全景 | 故事发展、空间关系 | 少用，避免 SD 生成多人穿帮 |
| 中景 | 调度、动作逻辑、人物位置关系 | 讲清谁从哪来、谁挡住谁、谁靠近谁 |
| 近景 | 对峙、台词、人物关系 | 台词戏主力景别 |
| 特写 | 表情、情绪、手部、道具证据 | 情绪爆点与信息锚点 |

### 台词时长估算

| 台词长度 | 时长 |
|---|---|
| 短句 1-4 英文词 | 1.2-1.8 秒 |
| 普通句 5-9 英文词 | 2.2-3.5 秒 |
| 长句 10-16 英文词 | 3.8-5.5 秒 |
| 超长句 | 必须拆镜，不得塞进 1.8 秒 |

中文台词按语速换算（日常约 3.5 字/秒、情感 2.8 字/秒、金句 2.0 字/秒），再叠加停顿与反应时间。

### 组间衔接方式

动作衔接（手伸出 → 下一组抓住）· 道具衔接（卷轴展开 → 下一组宣读）·
声音衔接（脚步声入 → 下一组人物进场）· 视线衔接（看向门口 → 下一组门口人物出现）·
情绪衔接（呼吸停住 → 下一组冲突爆发）· 光影衔接（火光压下 → 下一组冷光空间）。

### 挂载格式

```md
本组挂载：`@角色-状态(ID)`、`@场景(ID)`、`@道具(ID)`、`@VFX(ID)`
```

人物与道具都按**状态**拆 ID（火场状态 / 重生状态 / 女仆状态 / 怀孕状态 / 觉醒状态 / 战斗状态 / 失忆状态；
戒指在谁手里 / 皇冠是否被举起 / 法令是否展开 / 药剂是否在前景）。

## Reference 路由

按需加载，不必全读。

| 场景 | 读取 |
|---|---|
| 任何一次完整分镜任务（必读） | [references/output-and-selfcheck.md](references/output-and-selfcheck.md)（标准输出结构、自检清单、新对话提示词） |
| 拆 S 组、定 15 秒、选景别 | [references/sgroup-and-shot-language.md](references/sgroup-and-shot-language.md) |
| 写台词、设计表演与气口 | [references/dialogue-and-performance.md](references/dialogue-and-performance.md) |
| 设计尾帧、做防穿帮、规避禁止画面 | [references/continuity-and-antiartifact.md](references/continuity-and-antiartifact.md) |
| 写挂载 ID 与 SD2.0 正/反向提示词 | [references/sd2-mounting-and-prompts.md](references/sd2-mounting-and-prompts.md) |
| 画面看不懂 / 情绪不对 / 台词太快 / 组间跳 / SD 重复人物 | [references/troubleshooting.md](references/troubleshooting.md) |
| 需要原文完整表述与逐条对照 | [references/source-experience-summary.md](references/source-experience-summary.md)（原文留档，逐字版） |

**脚本**：Word 导出用 [scripts/md2docx.py](scripts/md2docx.py)（Markdown → .docx）。
本机 **无 pandoc / soffice / libreoffice**，不要浪费时间试；直接用
`/Users/zc/.workbuddy/binaries/python/envs/default/bin/python scripts/md2docx.py in.md out.docx`。
用法与验收口径见 [references/output-and-selfcheck.md](references/output-and-selfcheck.md) 第 2.5 节。

**模板**：从 [assets/episode-storyboard-template.md](assets/episode-storyboard-template.md) 复制单集骨架，
按 `S01 / S02 / …` 逐组填充。

**写完必扫禁止词**（最容易被忽略的一步）：

```bash
grep -n -E "月纹|冒光|瞳孔|发亮|亮起|发光|露骨|血腥|白布" part-*.md
```

中招后按「环境光落在材质上」改写，例：`眼睛发亮`→`眼睛睁圆`、`屏幕亮起`→`冷光落在被角`、
`瞳孔放大`→`双眼睁大`；英文 prompt 同理：`glowing flushed cheeks`→`heat-flushed cheeks`、
`lights glowing warm`→`warm interior light spilling`。
注意 Negative 块里的 `glowing eyes, glowing body` 是**故意保留**的，不要一起删。

## 关键判断标准

一版分镜好不好，不看文字多不多，而看：

1. 观众能不能一眼看懂发生了什么。
2. 情绪是不是跟人物此刻心理一致。
3. 台词是不是有对应画面。
4. 镜头能不能剪。
5. SD2.0 会不会乱生人、乱生道具、乱生光效。
6. 每个 S 组是不是都有明确起点、变化和尾帧。

**最终标准：画面清楚、情绪准确、台词能说完、剪辑能接上、生成不穿帮。**

## 更新日志

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0.0 | 2026-09-10 | 初始版本：由《短剧分镜经验总结｜新对话使用版》提炼为技能，含 SKILL.md + 6 个 reference + 1 个模板 + 原文留档 |
| 1.1.0 | 2026-09-10 | 实测 EP21–EP24（44 组 / 162 镜）后回补：新增 `scripts/md2docx.py` 与 Word 导出节（本机无 pandoc/soffice，只能走 python-docx）；新增禁止词写完必扫命令与中英替换范例；新增「表格数 = S 组数 + 汇总 + 自检」的导出验收口径 |
| 1.2.0 | 2026-09-10 | 实测 EP31–EP38（8 集 / 90 组 / 379 镜）后回补：新增硬规则 11（无台词组连续编号 + 复核命令）与 12（台词来源标注）；新增 2.4 节「台词来源标注」规程；补齐多集任务的分片命名约定（`part-0N-epXX.md` + `part-99-selfcheck.md`）与多集拼接命令；导出验收口径升级为通用公式「表格数 = S 组数 + 前言 3 表 + 自检 9 表」，并新增拼接后三数自检（行数／S 组数／集数） |
