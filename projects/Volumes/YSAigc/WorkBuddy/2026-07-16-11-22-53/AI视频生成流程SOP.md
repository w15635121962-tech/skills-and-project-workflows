# AI 视频生成流程 SOP

> 版本：v1.0 | 更新日期：2026-07-16
> 适用场景：推文短视频 AI 生成全流程

---

## 目录

1. [流程总览](#1-流程总览)
2. [Phase 1 — 推文创作与剧本准备](#phase-1--推文创作与剧本准备)
3. [Phase 2 — 英文分镜制作](#phase-2--英文分镜制作)
4. [Phase 3 — 旁白与台词规范](#phase-3--旁白与台词规范)
5. [Phase 4 — 达芬奇修音](#phase-4--达芬奇修音)
6. [Phase 5 — 抽卡提示词生成](#phase-5--抽卡提示词生成)
7. [Phase 6 — 画面配图与视觉策略](#phase-6--画面配图与视觉策略)
8. [关键规则速查表](#关键规则速查表)
9. [各阶段交付物清单](#各阶段交付物清单)

---

## 1. 流程总览

```
推文创作（周更）
    ↓
中文剧本（仅参考）
    ↓
英文分镜制作 ← 旁白拆分到反应中
    ↓
台词 + 旁白生成（不加他人反应）
    ↓
达芬奇修音
    ↓
抽卡提示词生成（AI 固定格式）
    ↓
画面配图（想象力 + 欧美审美 + 擦边 + 强冲突）
    ↓
成片
```

**核心原则：**
- 中文剧本 **只做参考**，不直接用于 AI 生成
- 分镜、提示词一律使用 **英文** 输出
- 旁白与台词 **独立生成**，不混入他人反应
- 抽卡提示词走 **AI 固定格式**，保证一致性
- 画面风格偏 **欧美审美**，适当擦边，矛盾冲突要强

---

## Phase 1 — 推文创作与剧本准备

### 1.1 推文创作

| 项目 | 要求 |
|------|------|
| 频率 | 一周一篇推文 |
| 语言 | 中文（作为参考剧本素材） |
| 核心驱动 | **矛盾冲突要强** |
| 风格倾向 | 擦边元素（欧美受众较受欢迎） |

**创作要点：**
- 开头 3 秒必须制造钩子（hook），让观众停不下来
- 每段推文内含一个冲突点或反转点
- 角色之间要有明确的对立关系
- 适当加入擦边/暧昧元素，提升完播率
- 可以用 AI 辅助：直接问 AI「欧美观众喜欢什么样的故事/冲突/角色关系」

### 1.2 中文剧本定位

```
中文剧本 = 参考素材 ≠ 直接投入生成
```

- 中文剧本用于：理清故事线、角色关系、情绪节奏
- 中文剧本 **不用于**：直接喂给 AI 抽卡工具
- 后续所有 AI 生成环节均基于 **英文分镜**

### 1.3 欧美审美参考（可选 AI 辅助）

在创作阶段可以问 AI 以下问题来获取方向：

```
提示词模板：
"What types of conflicts and storylines are popular with Western/European 
audiences on social media short videos?"

"What character dynamics create the strongest engagement in 
vertical short-form content?"

"What borderline/edgy content themes perform well without 
violating platform guidelines?"
```

---

## Phase 2 — 英文分镜制作

### 2.1 为什么要用英文

| 维度 | 英文优势 |
|------|----------|
| AI 抽卡工具兼容性 | 主流 AI 工具（Midjourney/SD/Runway 等）对英文提示词理解最精准 |
| 提示词生态 | 英文 Lora、Embedding、风格词库更丰富 |
| 画面描述精度 | 英文空间/光影/材质描述词更成熟 |

### 2.2 分镜制作流程

1. **通读中文剧本**，提取每场戏的核心叙事 beats
2. **将每个 beat 翻译/改写为英文画面描述**
3. **按镜头拆分**，每个镜头包含：
   - 镜号（Shot No.）
   - 景别（Close-up / Medium / Wide 等）
   - 画面描述（Visual Description - English）
   - 角色动作（Action - English）
   - 台词/旁白（Dialogue/Narration - English）
4. **旁白处理**：将旁白拆分到对应镜头的角色反应中（详见 Phase 3）

### 2.3 分镜表格模板

| Shot | Scene | Shot Type | Visual Description | Action | Dialogue | Narration |
|------|-------|-----------|-------------------|--------|----------|-----------|
| 01 | Opening | CU | Dark room, single light | Character looks up | "What do you want?" | — |
| 02 | Opening | MS | Two figures facing off | B steps forward | — | He knew this moment would come. |
| 03 | Opening | CU | A's eyes narrow | A clenches fist | "You don't belong here." | — |

---

## Phase 3 — 旁白与台词规范

### 3.1 核心规则

> **做台词和旁白时，不加别人的反应。**

这意味着：
- 角色A的台词就是角色A的台词，不要在A的台词块里写「B皱眉」
- 旁白就是旁白，不要在旁白里夹带其他角色的动作描写
- 每个文本块（台词/旁白）保持 **单一来源、单一视角**

**正确示例：**
```
Shot 03:
  Dialogue (A): "You don't belong here."
  Narration: He knew this moment would come.
  Action: A clenches fist.        ← 动作独立，不混入台词
```

**错误示例：**
```
Shot 03:
  Dialogue (A): "You don't belong here." B frowned.    ← 错误：混入了B的反应
  Narration: He knew this moment would come. A turned away.  ← 错误：混入了A的动作
```

### 3.2 旁白拆分规则

> **在拆分镜时，旁白也要加入到反应中。**

- 旁白不是独立的旁白层，而是要 **分配到对应镜头的反应描述中**
- 旁白起到补充角色内心活动/情绪反应的作用
- 拆分时：先确定镜头 → 再确定该镜头的角色反应 → 旁白作为反应的一部分嵌入

**拆分逻辑：**
```
镜头 → 角色反应 = 动作 + 表情 + 旁白（内心独白/画外音）
```

### 3.3 生成规则

> **生成时连旁白一起生成出来。**

- 台词和旁白 **一次性生成**，不分两轮
- 生成结果直接包含：台词 + 旁白 + 动作描述
- 生成完成后，直接进入达芬奇修音环节

**一次性生成输出格式：**
```
[Shot 03]
DIALOGUE: "You don't belong here."
NARRATION: He knew this moment would come.
ACTION: A clenches fist, jaw tight.
```

---

## Phase 4 — 达芬奇修音

### 4.1 前置条件

- Phase 3 的台词+旁白已一次性生成完毕
- 音频文件已录制/生成

### 4.2 修音流程

1. **导入音频**：将生成的台词+旁白音频导入 DaVinci Resolve
2. **降噪处理**：Fairlight 页面，使用噪声门/降噪插件
3. **EQ 均衡**：调整人声频段（通常提升 2-5kHz 增强清晰度）
4. **压缩**：控制动态范围，使台词音量稳定
5. **响度标准化**：统一到目标响度（推荐 -16 LUFS for 社交媒体）
6. **导出**：导出修音后的音频轨

### 4.3 注意事项

- 旁白和台词可以在同一轨处理，也可以分轨
- 如果分轨：台词轨和旁白轨分别处理，最后混音
- 修音完成后，音频即可用于最终成片合成

---

## Phase 5 — 抽卡提示词生成

### 5.1 原则

> **根据做好的分镜去生成提示词，用 AI 做固定格式的输出。**

- 提示词 **基于分镜**，不是凭空生成
- 使用 AI 工具，指定 **固定输出格式**
- 每个镜头对应一组提示词

### 5.2 AI 固定格式输出模板

向 AI 发送以下指令，确保输出格式统一：

```
You are a prompt engineer for AI image/video generation.
Based on the storyboard below, generate prompts in this EXACT format for each shot.

OUTPUT FORMAT (per shot):
---
SHOT: [shot number]
POSITIVE: [subject description], [action/pose], [environment/setting], 
[lighting], [camera angle/shot type], [style modifiers], [quality tags]
NEGATIVE: [standard negative prompts]
PARAMS: aspect ratio, [other generation parameters]
---

STORYBOARD:
[粘贴英文分镜内容]
```

### 5.3 提示词构成要素

| 要素 | 说明 | 示例 |
|------|------|------|
| Subject | 主体描述 | a young woman with dark hair |
| Action/Pose | 动作姿态 | clenching fist, jaw tight |
| Environment | 场景环境 | dimly lit room, single overhead light |
| Lighting | 光照 | dramatic chiaroscuro lighting |
| Camera | 机位/景别 | close-up shot, eye level |
| Style | 风格修饰 | cinematic, film grain, moody atmosphere |
| Quality | 质量标签 | highly detailed, 8k, sharp focus |

### 5.4 固定格式示例输出

```
---
SHOT: 03
POSITIVE: a young man with sharp features and dark eyes, clenching fist with jaw tight, 
dimly lit concrete room with single overhead light, dramatic chiaroscuro lighting, 
extreme close-up shot eye level, cinematic film grain moody atmosphere, 
highly detailed 8k sharp focus
NEGATIVE: blurry, deformed, extra fingers, low quality, watermark, text, cartoon
PARAMS: --ar 9:16 --style raw --v 6
---
```

---

## Phase 6 — 画面配图与视觉策略

### 6.1 核心原则

> **在给配画面时，要发挥想象力。**

- 不要照搬分镜字面描述，要在分镜基础上 **创意延展**
- 画面要有视觉冲击力，能独立吸引注意力
- 配画面时可以考虑问 AI 欧美受众的审美偏好

### 6.2 视觉策略

#### 擦边策略
- 适度擦边：利用服装、姿态、光影暗示，不越过平台红线
- 擦边元素服务于叙事，不为了擦边而擦边
- 欧美受众对擦边接受度较高，但仍需注意平台规则

#### 矛盾冲突视觉化
- 用 **空间关系** 表现对立（两人对峙、背向、逼近）
- 用 **光影对比** 强化冲突（明暗分割、硬阴影）
- 用 **构图张力** 制造压迫感（倾斜构图、极端景别）
- 用 **色彩对立** 暗示阵营（暖色 vs 冷色）

#### 欧美审美参考

可以用 AI 辅助获取方向：
```
"What visual styles and aesthetics are trending with Western 
audiences in short-form video content?"

"What color palettes and lighting setups create the most 
dramatic tension in cinematic vertical videos?"
```

### 6.3 配画面检查清单

- [ ] 画面是否比文字描述更有想象力？
- [ ] 矛盾冲突是否在视觉上一目了然？
- [ ] 擦边元素是否适度且服务叙事？
- [ ] 风格是否符合欧美审美偏好？
- [ ] 镜头之间是否有视觉连贯性？
- [ ] 是否有足够的视觉钩子（前3帧抓住注意力）？

---

## 关键规则速查表

| 规则 | 说明 |
|------|------|
| 中文剧本只做参考 | 不直接用于 AI 生成 |
| 分镜用英文 | 所有 AI 生成环节基于英文 |
| 旁白拆分到反应中 | 旁白作为角色反应的一部分嵌入镜头 |
| 台词旁白不加他人反应 | 每个文本块保持单一来源单一视角 |
| 生成时连旁白一起 | 台词+旁白一次性生成 |
| 生成后进达芬奇修音 | 修音环节紧跟生成 |
| 抽卡基于分镜 | 提示词从分镜推导，不凭空生成 |
| 提示词固定格式 | AI 输出统一格式，保证一致性 |
| 推文一周一篇 | 保持周更节奏 |
| 配画面发挥想象力 | 在分镜基础上创意延展 |
| 欧美审美 | 适当擦边，矛盾冲突要强 |

---

## 各阶段交付物清单

| 阶段 | 交付物 | 格式 |
|------|--------|------|
| Phase 1 | 中文推文剧本 | 文本 |
| Phase 2 | 英文分镜表 | 表格（Shot/Scene/Type/Visual/Action/Dialogue/Narration） |
| Phase 3 | 台词+旁白生成稿 | 文本（含 DIALOGUE/NARRATION/ACTION 标签） |
| Phase 4 | 修音音频文件 | WAV/MP3 |
| Phase 5 | 抽卡提示词集 | 文本（固定格式 POSITIVE/NEGATIVE/PARAMS） |
| Phase 6 | 画面素材 | 图片/视频 |
| 最终 | 成片 | MP4（竖版 9:16） |

---

## 附录：AI 辅助提示词模板库

### A1. 推文创作辅助
```
Write a weekly social media thread story with:
- Strong interpersonal conflict
- Borderline/suggestive elements (within platform guidelines)
- Western audience appeal
- Hook in the first 3 seconds
- Character dynamics that create tension
Genre: [填写类型]
```

### A2. 中文剧本转英文分镜
```
Convert the following Chinese script into an English storyboard table.
Each shot must include: Shot No, Scene, Shot Type, Visual Description, 
Action, Dialogue, and Narration.
Split narration into corresponding character reactions.
Do NOT add other characters' reactions in dialogue or narration blocks.

Chinese script:
[粘贴中文剧本]
```

### A3. 台词+旁白一次性生成
```
Based on the storyboard below, generate dialogue and narration together 
for each shot. Output in this format:
[Shot X]
DIALOGUE: "..."
NARRATION: ...
ACTION: ...

Rules:
- Do NOT include other characters' reactions in dialogue or narration
- Narration should reflect the character's internal state
- Generate all shots in one pass

Storyboard:
[粘贴分镜]
```

### A4. 抽卡提示词生成
```
Based on the storyboard below, generate AI image/video prompts.
Use EXACT format:
SHOT: [number]
POSITIVE: [subject], [action], [environment], [lighting], [camera], [style], [quality]
NEGATIVE: [standard negatives]
PARAMS: [generation parameters]

Storyboard:
[粘贴分镜]
```

### A5. 欧美审美参考
```
What visual aesthetics, color palettes, and lighting styles are most 
appealing to Western/European audiences in short-form vertical video content?
Focus on: dramatic tension, character dynamics, borderline appeal.
Provide specific examples.
```

---

*SOP 维护：如有流程变更，更新本文档并注明版本号。*
