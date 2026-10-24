# 竖屏对话情绪控制 (Vertical Dialogue & Emotion Control)

> 专为 9:16 竖屏画幅重构的对话场景情绪控制协议。原版 16:9 对话情绪表达直接用于竖屏会导致人脸占比小、情绪传递弱、手机屏上不清晰。

---

## 一、竖屏对话核心差异

### 1.1 原版 vs 竖屏版对比

| 概念 | 16:9 横屏 | 9:16 竖屏 | 原因 |
|------|-----------|-----------|------|
| 人脸占比 | 20-40% | **40-60%** | 竖屏人脸更大，情绪更清晰 |
| 对白密度 | 正常 | **压缩 50%** | 竖屏字幕小，难阅读 |
| 情绪传递 | 靠对白 | **靠表情（微表情）** | 竖屏人脸大，微表情可见 |
| 镜头长度 | 3-5秒 | **1-3秒** | 竖屏节奏快 |
| 正反打 | 常用 | **少用（用单镜同框替代）** | 竖屏可以 2 人同框 |

### 1.2 竖屏对话场景最小覆盖（3 镜方案）

**横屏**：Master + 2x Single + OTS + Insert = 5-6 镜
**竖屏**：Master (2-shot) + 2x Single = **3 镜**

```
镜1: Master (2-shot, 垂直分布)
      ┌─────────────────┐
      │  人物A (上 1/3)  │
      ├─────────────────┤
      │  (空白)          │
      ├─────────────────┤
      │  人物B (下 1/3)  │
      └─────────────────┘
      ↓ 建立权力关系 + 对话开始

镜2: Single A (腰部以上，眼睛在 1/3）
      ↓ 人物A对白 + 表情

镜3: Single B (腰部以上，眼睛在 1/3）
      ↓ 人物B对白 + 表情
```

**为什么竖屏可以少 2-3 镜？**
- OTS（过肩镜头）：竖屏 Master (2-shot) 已经展示两人，不需要单独 OTS
- Insert（插入镜）：竖屏 Single 可以包含道具（人物手持），不需要单独 Insert

---

## 二、竖屏对话情绪传递

### 2.1 情绪传递渠道（竖屏版）

| 渠道 | 横屏权重 | 竖屏权重 | 原因 |
|------|---------|---------|------|
| **对白** | 60% | **30%** | 竖屏字幕小，难阅读 |
| **表情（微表情）** | 30% | **60%** | 竖屏人脸大，微表情清晰 |
| **肢体语言** | 10% | **10%** | 一致 |

### 2.2 微表情捕捉（竖屏版）

**横屏**：微表情需要特写镜头（Close-Up）
**竖屏**：微表情在腰部以上镜头就可见（因为人脸占比 40-60%）

| 微表情 | 横屏需要 | 竖屏需要 | 提示词关键词 |
|--------|---------|---------|-------------|
| 瞳孔收缩 | Close-Up (特写) | Waist-Up (腰部以上) | `pupil constriction, close-up, 50fps` |
| 嘴角抽动 | Close-Up | Waist-Up | `lip twitch, micro-expression` |
| 眉毛上扬 | Close-Up | Waist-Up | `eyebrow raise, forehead detail` |
| 鼻翼扩张 | Close-Up | Waist-Up | `nostril flare, nose detail` |
| 眼轮匝肌收缩 | Close-Up | Waist-Up | `crow's feet, eye detail` |

### 2.3 情绪渐变（竖屏版）

**横屏**：3-5 秒完成情绪渐变
**竖屏**：**1-2 秒**完成情绪渐变（竖屏节奏快）

**提示词（情绪渐变）**：

```
fast emotion transition, from shock to anger in 1 second,
micro-expression capture, 50fps, high detail,
vertical framing, --ar 9:16
```

---

## 三、竖屏对话提示词工程

### 3.1 对话场景提示词模板（竖屏版）

```
{人物A}, {位置: 上 1/3}, {情绪/微表情},
{人物B}, {位置: 下 1/3}, {情绪/微表情},
对话场景, {人物关系},
--ar 9:16, vertical framing, 9:16 aspect ratio,
{质感层: 手机屏优化}, --no {负面词}
```

### 3.2 对白压缩策略（竖屏版）

**问题**：竖屏字幕小，对白太长用户来不及看。

**解决方案**：对白压缩 50%，用**表情**传递剩余信息。

```
横屏原版（30 字）：
陆雪："王勃，你的《斗鸡檄》震动京城，可曾想过，有些文字，写了便是死罪？"

竖屏重构版（15 字）：
陆雪（冷笑，微表情：嘴角右牵 3°）："《斗鸡檄》——写了，便是死。"
```

**提示词（对白压缩）**：

```
dialogue condensed 50%, subtitles at bottom 12-18%,
micro-expressions convey 60% emotion,
vertical framing, --ar 9:16
```

### 3.3 对话场景运镜（竖屏版）

| 运镜 | 横屏 | 竖屏 | 提示词关键词 |
|------|------|------|-------------|
| 静态（对话） | 固定镜头 | **固定镜头**（竖屏对话常用） | `static shot, dialogue, vertical framing` |
| 微推（强调） | Push-In | **垂直推进**（锁眼睛 1/3） | `vertical push-in, eyes locked at 1/3` |
| 微拉（揭示） | Pull-out | **垂直拉远**（揭示人物关系） | `vertical pull-out, reveal power dynamics` |
| 眨眼切（情绪） | Cut on glance | **眨眼切**（竖屏更明显） | `cut on blink, micro-timing` |

---

## 四、竖屏对话质量检查

### 4.1 对话场景必检项

- [ ] 对白是否压缩 ≥50%？
- [ ] 情绪是否 60% 靠表情传递（不是对白）？
- [ ] 人脸占比是否 40-60%（不是 20-40%）？
- [ ] 眼睛位置是否在 1/3 处？
- [ ] 底部 12-18% 是否有字幕（不被 UI 遮挡）？
- [ ] 镜头长度是否 1-3 秒（不是 3-5 秒）？

### 4.2 对话提示词必检项

- [ ] 是否包含 `--ar 9:16` 和 `vertical framing`？
- [ ] 是否指定了人物位置（`upper 1/3` / `lower 1/3`）？
- [ ] 是否指定了微表情（`micro-expression, pupil constriction`）？
- [ ] 是否包含竖屏负面词（`--no horizontal composition, face cropped`）？
- [ ] 是否包含手机屏优化（`mobile display optimized`）？

### 4.3 对话场景常见错误与修正

| 错误 | 原因 | 修正 |
|------|------|------|
| 对白太长 | 横屏思维（字幕可读性好） | 压缩 50%，用表情传递 |
| 情绪靠对白 | 未利用竖屏人脸大的优势 | 增加微表情描写，减少对白 |
| 镜头太长 | 横屏节奏（3-5秒） | 缩短到 1-3 秒 |
| 人脸占比小 | 用了横屏构图（全景） | 用腰部以上构图（人脸占比 40-60%） |
| 字幕被 UI 遮挡 | 字幕在底部 20% | 字幕在 12-18%（不更低） |

---

## 五、竖屏对话场景交付物

### 5.1 交付文件

| 文件 | 格式 | 内容 |
|------|------|------|
| `{项目名}_EP{XX}_对话分镜_竖屏.md` | Markdown | 完整对话分镜 |
| `{项目名}_EP{XX}_对白压缩对照表_竖屏.xlsx` | Excel | 对白压缩前后对比 |
| `{项目名}_EP{XX}_对话提示词库_竖屏.json` | JSON | 对话场景提示词库 |

### 5.2 对话提示词库 JSON 格式（竖屏）

```json
{
  "project": "大唐文圣",
  "episode": 1,
  "aspect_ratio": "9:16",
  "dialogue_shots": {
    "001": {
      "shot_type": "Master (2-shot)",
      "characters": ["陆雪", "王勃"],
      "dialogue": "《斗鸡檄》——写了，便是死。",
      "original_length": 30,
      "compressed_length": 15,
      "emotion_conveyed_by": "micro-expression (60%), dialogue (30%), body language (10%)",
      "prompt": "Lu Xue (upper 1/3) and Wang Bo (lower 1/3), dialogue, cold smile, anger, --ar 9:16, vertical framing",
      "platform": "all"
    }
  }
}
```

---

## 六、竖屏对话实战案例

### 6.1 案例：《大唐文圣》第一集（偏殿对话）

**场景**：陆雪给王勃看休书，对话 1 分钟。

**横屏原版**：
- 镜头数：10-12 镜
- 对白密度：100%
- 情绪传递：对白 60% + 表情 30% + 肢体 10%

**竖屏重构版**：
- 镜头数：**5-6 镜**（减少 50%）
- 对白密度：**50%**（压缩 50%）
- 情绪传递：对白 30% + **表情 60%** + 肢体 10%

**分镜（竖屏 5 镜方案）**：

```
镜001 (Master - 2-shot, 5秒)：
建立权力关系，陆雪冷笑："王勃，可认得此物？"
（对白 10 字，微表情：冷笑）

镜002 (Single A - 陆雪, 3秒)：
陆雪展开休书："休书。你自由了。"
（对白 8 字，微表情：嘴角右牵 3°）

镜003 (Single B - 王勃, 3秒)：
王勃震惊："你……你怎可——"
（对白 8 字，微表情：瞳孔骤缩）

镜004 (Single A - 陆雪, 2秒)：
陆雪转身："签了它。"
（对白 4 字，微表情：侧脸，决绝）

镜005 (Single B - 王勃, 5秒)：
王勃颤抖，拿起笔："……好。"
（对白 3 字，微表情：咬肌鼓起，鼻翼扩张）
```

**提示词（竖屏对话）**：

```
镜001：
Lu Xue (upper 1/3), cold smile, holding divorce paper,
Wang Bo (lower 1/3), shock, kneeling,
vertical two-shot, dialogue scene,
--ar 9:16, vertical framing

镜002：
Lu Xue, waist-up, eyes at upper 1/3,
unfolding divorce paper, micro-expression (lip twitch),
dialogue: "Sign it.", --ar 9:16, vertical framing

镜003：
Wang Bo, waist-up, eyes at upper 1/3,
shock, pupil constriction, micro-expression,
dialogue: "You... how could you...", --ar 9:16, vertical framing
```

---

*专为 9:16 竖屏画幅重构，适配抖音/TikTok/Reels/Shorts 等平台。*
