# 竖屏多角色处理 (Vertical Multi-Character Handling)

> 专为 9:16 竖屏画幅重构的多角色对话/群戏处理协议。原版 16:9 多角色调度直接用于竖屏会导致人物重叠、构图混乱、平台裁剪。

---

## 一、竖屏多角色核心法则

### 1.1 垂直空间分配（竖屏专属）

**横屏**：多人同框靠左右分布
**竖屏**：多人同框靠**上下分布**（垂直空间分配）

```
竖屏 2 人同框（标准）：

┌─────────────────┐
│  人物 A (上位)   │  ← 上 1/3 处（眼睛位置）
├─────────────────┤
│  (空白/分隔)     │  ← 中间留白 10-15%
├─────────────────┤
│  人物 B (下位)   │  ← 下 1/3 处（眼睛位置）
└─────────────────┘
```

```
竖屏 3 人同框（垂直分布）：

┌─────────────────┐
│  人物 A (上位)   │  ← 上 1/3 处
├─────────────────┤
│  人物 B (中位)   │  ← 中心偏上
├─────────────────┤
│  人物 C (下位)   │  ← 下 1/3 处
└─────────────────┘
```

### 1.2 人物层级与权力关系（竖屏版）

| 位置 | 权力 | 示例 | 提示词关键词 |
|------|------|------|-------------|
| **上 1/3 处** | 最高 | 皇帝/家主/胜者 | `character A at upper 1/3, dominant` |
| **中心** | 中立/过渡 | 中间人/信使 | `character B at center, neutral` |
| **下 1/3 处** | 最低 | 臣子/仆人/败者 | `character C at lower 1/3, submissive` |

### 1.3 人物大小与优先级（竖屏版）

**横屏**：人物大小靠景深（近大远小）
**竖屏**：人物大小靠**占位比例**（上半身 > 全身）

| 人物优先级 | 构图 | 占位比例 | 提示词 |
|-----------|------|---------|---------|
| **主角** | 腰部以上 | 60-70% | `waist-up, main character, 60% frame` |
| **配角** | 胸部以上 | 40-50% | `chest-up, supporting character, 40% frame` |
| **群演** | 全身 | 20-30% | `full body, background characters, 20% frame` |

---

## 二、竖屏多角色覆盖策略

### 2.1 双角色对话（竖屏 3 镜方案）

**横屏**：5-6 镜（Master + 2x Single + OTS + 2-Shot + Insert）
**竖屏**：**3 镜**（Master + 2x Single，OTS 和 2-Shot 合并）

```
镜1: Master (2 人同框，垂直分布)
      ┌─────────────────┐
      │  陆雪 (上 1/3)  │
      ├─────────────────┤
      │  (空白)          │
      ├─────────────────┤
      │  王勃 (下 1/3)  │
      └─────────────────┘
      ↓ 建立权力关系

镜2: Single A (陆雪，腰部以上，眼睛在 1/3）
      ↓ 展示表情/对白

镜3: Single B (王勃，腰部以上，眼睛在 1/3）
      ↓ 展示表情/对白
```

**提示词（双角色）**：

```
镜1 (Master)：
Lu Xue (upper 1/3) and Wang Bo (lower 1/3),
vertical two-shot, power dynamics,
rainy night, --ar 9:16, vertical framing

镜2 (Single A)：
Lu Xue, waist-up, eyes at upper 1/3,
cold smile, --ar 9:16, vertical framing

镜3 (Single B)：
Wang Bo, waist-up, eyes at upper 1/3,
anger, kneeling, --ar 9:16, vertical framing
```

### 2.2 三角色对话（竖屏 5 镜方案）

**横屏**：7-8 镜
**竖屏**：**5 镜**（Master + 3x Single + Group Shot）

```
镜1: Master (3 人同框，垂直分布)
      ┌─────────────────┐
      │  陆雪 (上 1/3)   │
      ├─────────────────┤
      │  裴子华 (中心)    │
      ├─────────────────┤
      │  王勃 (下 1/3)   │
      └─────────────────┘

镜2: Single A (陆雪)
镜3: Single B (裴子华)
镜4: Single C (王勃)
镜5: Group Shot (3 人同框，重新构图)
```

**提示词（三角色）**：

```
镜1 (Master)：
three people, vertical composition,
Lu Xue (upper 1/3), Pei Zihua (center), Wang Bo (lower 1/3),
power triangle, --ar 9:16, vertical framing
```

### 2.3 群戏（4+ 角色，竖屏策略）

**策略 1**：分批处理（每次 2-3 人）
- 镜1-3：A + B 对话
- 镜4-6：B + C 对话
- 镜7-9：A + C 对话
- 镜10：Group Shot (4+ 人)

**策略 2**：前景/后景分层
- 前景（上 1/3）：1-2 人（焦点）
- 后景（下 1/3）：2-3 人（虚化）

**提示词（群戏）**：

```
four people, vertical composition,
foreground: 2 people (upper 1/3, sharp),
background: 2 people (lower 1/3, blurred),
depth of field, --ar 9:16, vertical framing
```

---

## 三、竖屏多角色提示词工程

### 3.1 多角色提示词模板（竖屏版）

```
{人物A描述}, {位置: 上 1/3},
{人物B描述}, {位置: 下 1/3},
{人物关系}, {情绪},
--ar 9:16, vertical framing, 9:16 aspect ratio,
{质感层}, --no {负面词}
```

### 3.2 多角色提示词注意事项（竖屏）

| 注意事项 | 横屏 | 竖屏 | 修正 |
|---------|------|------|------|
| 人物顺序 | 任何 | **权力高→低** | `Lu Xue (upper), Wang Bo (lower)` |
| 眼睛位置 | 任何 | **各在 1/3 处** | `eyes at upper 1/3 for both` |
| 头顶留白 | 任何 | **各留白 15%** | `headroom 15% for both` |
| 底部留空 | 无 | **20% 留空** | `bottom 20% empty` |

### 3.3 多角色提示词示例（竖屏）

**双角色（对话）**：

```
Lu Xue, waist-up, eyes at upper 1/3, cold smile,
Wang Bo, waist-up, eyes at upper 1/3, anger, kneeling,
vertical two-shot, power dynamics,
rainy night, lightning, --ar 9:16, vertical framing,
mobile display optimized, OLED optimized,
--no horizontal composition, face cropped, watermark
```

**三角色（群戏）**：

```
three people, vertical composition,
Lu Xue (upper 1/3), cold expression,
Pei Zihua (center), sinister smile,
Wang Bo (lower 1/3), angry, kneeling,
power triangle, tang dynasty, night,
--ar 9:16, vertical framing,
--no horizontal composition, face cropped
```

---

## 四、竖屏多角色质量检查

### 4.1 多角色构图必检项

- [ ] 人物是否按权力关系垂直分布（上位者在上）？
- [ ] 每个人物的眼睛是否都在 1/3 处（或各自的有效位置）？
- [ ] 人物之间是否有留白（避免重叠）？
- [ ] 底部 20% 是否为空（或被字幕占用）？
- [ ] 人物大小是否符合优先级（主角 > 配角 > 群演）？

### 4.2 多角色提示词必检项

- [ ] 是否包含 `--ar 9:16` 和 `vertical framing`？
- [ ] 是否指定了每个人物的位置（`upper 1/3` / `center` / `lower 1/3`）？
- [ ] 是否指定了眼睛位置（`eyes at upper 1/3`）？
- [ ] 是否包含竖屏负面词（`--no horizontal composition, face cropped`）？
- [ ] 是否包含手机屏优化（`mobile display optimized`）？

### 4.3 多角色常见错误与修正

| 错误 | 原因 | 修正 |
|------|------|------|
| 人物重叠 | 未留垂直留白 | 人物之间加 10-15% 留白 |
| 眼睛位置不一致 | 未指定垂直位置 | 所有人物提示词加 `eyes at upper 1/3` |
| 底部被 UI 遮挡 | 未留空 20% | 提示词加 `bottom 20% empty` |
| 人物大小混乱 | 未区分优先级 | 主角腰部以上，配角胸部以上，群演全身 |
| 权力关系不清 | 位置分配错误 | 上位者在上 1/3，下位者在下 1/3 |

---

## 五、竖屏多角色交付物

### 5.1 交付文件

| 文件 | 格式 | 内容 |
|------|------|------|
| `{项目名}_EP{XX}_多角色分镜_竖屏.md` | Markdown | 完整多角色分镜 |
| `{项目名}_EP{XX}_人物位置图_竖屏.pdf` | PDF | 人物垂直分布图示 |
| `{项目名}_EP{XX}_多角色提示词库_竖屏.json` | JSON | 多角色提示词库 |

### 5.2 多角色提示词库 JSON 格式（竖屏）

```json
{
  "project": "大唐文圣",
  "episode": 1,
  "aspect_ratio": "9:16",
  "multi_character_shots": {
    "001": {
      "shot_type": "Master (2-shot)",
      "characters": {
        "A": {
          "name": "陆雪",
          "position": "upper 1/3",
          "expression": "cold smile"
        },
        "B": {
          "name": "王勃",
          "position": "lower 1/3",
          "expression": "anger, kneeling"
        }
      },
      "prompt": "Lu Xue (upper 1/3) and Wang Bo (lower 1/3), vertical two-shot, power dynamics, --ar 9:16, vertical framing",
      "platform": "all"
    }
  }
}
```

---

## 六、竖屏多角色实战案例

### 6.1 案例：《大唐文圣》第一集（偏殿对话）

**场景**：周王府偏殿，暴雨夜，陆雪(上位) 给 王勃(下位) 看休书。

**分镜（竖屏 3 镜方案）**：

```
镜001 (Master - 2-shot)：
┌─────────────────┐
│  陆雪 (上 1/3)   │  腰部以上，冷笑
├─────────────────┤
│  (空白 15%)      │
├─────────────────┤
│  王勃 (下 1/3)   │  腰部以上，愤怒，跪拜
└─────────────────┘
提示词：
Lu Xue (upper 1/3) and Wang Bo (lower 1/3),
vertical two-shot, power dynamics, rainy night,
--ar 9:16, vertical framing

镜002 (Single A - 陆雪)：
陆雪，腰部以上，眼睛在 1/3 处，
冷笑，展开休书，
提示词：
Lu Xue, waist-up, eyes at upper 1/3, cold smile,
holding divorce paper, --ar 9:16, vertical framing

镜003 (Single B - 王勃)：
王勃，腰部以上，眼睛在 1/3 处，
愤怒，手握拳头，
提示词：
Wang Bo, waist-up, eyes at upper 1/3, anger,
clenching fist, kneeling, --ar 9:16, vertical framing
```

---

*专为 9:16 竖屏画幅重构，适配抖音/TikTok/Reels/Shorts 等平台。*
