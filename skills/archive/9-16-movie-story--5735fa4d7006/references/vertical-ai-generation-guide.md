# 竖屏 AI 生成指南 (Vertical AI Generation Guide)

> 专为 9:16 竖屏画幅重构的 AI 生成指南。原版 16:9 生成流程直接用于竖屏会导致画幅错误、构图失衡、平台裁剪。

---

## 一、AI 生成核心差异

### 1.1 原版 vs 竖屏版对比

| 概念 | 16:9 横屏 | 9:16 竖屏 | 原因 |
|------|-----------|-----------|------|
| 画幅设置 | `--ar 16:9` | `--ar 9:16` | 竖屏必须 |
| 构图指令 | `centered composition` | `vertical framing, eyes at 1/3` | 竖屏构图规则 |
| 提示词长度 | 正常 | **压缩 30%** | 竖屏模型理解力弱 |
| 迭代次数 | 3-5 次 | **1-2 次** | 竖屏需要快速迭代 |
| 平台适配 | 无 | **必须** | 抖音/Reels 算法 |

### 1.2 竖屏 AI 生成四步法

```
第一步：画幅确认（必须 --ar 9:16）
   ↓
第二步：构图指令（vertical framing + eyes at 1/3）
   ↓
第三步：提示词压缩（≤200 词，竖屏模型限制）
   ↓
第四步：平台适配（抖音/Reels/Shorts 关键词）
```

---

## 二、竖屏提示词工程（四步黄金框架）

### 2.1 四步黄金框架（竖屏重构版）

```
{主体}, {动作}, {垂直位置: 眼睛在 1/3 处},
{环境}, {光影}, {底部处理: 留空 20%},
--ar 9:16, vertical framing, 9:16 aspect ratio,
{质感层: 手机屏优化, OLED optimized},
--no {负面词: horizontal composition, face cropped}
```

### 2.2 提示词压缩策略（竖屏版）

**问题**：竖屏模型（Seedance/Kling）对长提示词理解力弱。

**解决方案**：提示词压缩 30%，保留核心关键词。

```
横屏原版（250 词）：
中年男人，蓝色官袍，偏殿跪拜，阴雨夜，闪电照亮，
冷蓝调，电影感，Arri Alexa 65, Master Prime 35mm,
Kodak Vision3 500T, 湿气/雨滴/布料纹理，...

竖屏重构版（150 词）：
Wang Bo, blue official robe, kneeling, eyes at upper 1/3,
rainy night, lightning, cold blue, --ar 9:16,
vertical framing, mobile display optimized,
--no horizontal composition, face cropped
```

### 2.3 负面提示词（竖屏专用）

| 负面词 | 防止的问题 |
|--------|-----------|
| `horizontal composition` | 防止 AI 生成横屏构图 |
| `letterbox` | 防止上下黑边 |
| `face cropped` | 防止人脸被裁切 |
| `eyes at bottom` | 防止眼睛在画面底部 |
| `bottom frame cluttered` | 防止底部杂乱（影响互动区） |
| `UI overlapping` | 防止与平台 UI 重叠 |

---

## 三、竖屏 AI 生成工作流

### 3.1 工作流（竖屏版）

```
加载剧本（第 X 集）
   ↓
模块 1：剧本健康诊断（竖屏视角）
   ↓
模块 2：视觉锚点体系（六维精度，竖屏重构）
   ↓
模块 1.5：覆盖拍摄规划（竖屏版，垂直空间）
   ↓
模块 3：分镜脚本生成（12 列表格，竖屏构图）
   ↓
模块 4：AI 图像提示词生成（四步框架，--ar 9:16）
   ↓
模块 5：AI 视频序列生成（Seedance/Kling，竖屏模式）
   ↓
模块 6：剪辑与交付（竖屏节奏，硬切为主）
   ↓
模块 9：质量自检（六轮协议，竖屏专项）
```

### 3.2 分镜生成（竖屏版）

**步骤 1**：读取剧本，提取场景/人物/对白
**步骤 2**：应用竖屏构图法则（眼睛在 1/3 处，头顶留白 15%）
**步骤 3**：生成 12 列分镜表（新增"垂直构图"列）
**步骤 4**：为每个镜头撰写 AI 提示词（含 --ar 9:16）
**步骤 5**：自检（六轮协议，竖屏专项）

**输出文件**：
- `{项目名}_EP{XX}_分镜脚本_竖屏 9-16.md`
- `{项目名}_EP{XX}_AI 提示词库_竖屏.json`

---

## 四、竖屏 AI 生成质量检查

### 4.1 生成前检查

- [ ] 是否包含 `--ar 9:16`？
- [ ] 是否包含 `vertical framing` 或 `9:16 aspect ratio`？
- [ ] 是否指定了眼睛位置（`eyes at upper 1/3`）？
- [ ] 是否指定了头顶留白（`headroom 15%`）？
- [ ] 是否包含竖屏负面词（`--no horizontal composition, face cropped`）？
- [ ] 是否包含手机屏优化（`mobile display optimized`）？

### 4.2 生成后检查（手机预览）

- [ ] 画幅是否为 9:16（无黑边）？
- [ ] 眼睛是否在 1/3 处？
- [ ] 人脸是否变形？
- [ ] 底部 20% 是否为空（或被字幕占用但不遮挡互动区）？
- [ ] 在手机上播放是否清晰？

### 4.3 常见问题与修正

| 问题 | 原因 | 修正提示词 |
|------|------|-----------|
| 眼睛位置错误 | 未指定垂直位置 | `eyes at upper 1/3, vertical rule of thirds` |
| 人脸出画 | 推进时未锁定眼睛 | `face always visible, headroom 15%` |
| 构图扁平 | 所有镜头都是正脸，无垂直变化 | 交替使用 `low angle` 和 `high angle` |
| 平台裁剪 | 主体在画面边缘 | 主体在中心稳定区 (x=25-75%, y=20-70%) |
| 字幕重叠 | 对话字幕与人脸重叠 | `space at bottom for subtitles, lower frame empty` |

---

## 五、竖屏 AI 生成交付物

### 5.1 交付文件清单

| 文件 | 格式 | 内容 |
|------|------|------|
| `{项目名}_EP{XX}_分镜脚本_竖屏 9-16.md` | Markdown | 完整分镜脚本 |
| `{项目名}_EP{XX}_分镜脚本_竖屏 9-16.pdf` | PDF | 打印/分享版本 |
| `{项目名}_EP{XX}_AI 提示词库_竖屏.json` | JSON | AI 提示词库（给 PromptManager） |
| `{项目名}_EP{XX}_分镜脚本_竖屏 9-16.html` | HTML | 交互式分镜看板 |

### 5.2 提示词库 JSON 格式（竖屏版）

```json
{
  "project": "大唐文圣",
  "episode": 1,
  "aspect_ratio": "9:16",
  "characters": {
    "王勃": {
      "base_prompt": "Wang Bo, blue official robe, wet silk, --ar 9:16, vertical framing",
      "expressions": {
        "震惊": "shock, eyes wide, pupils constricted, E@1/3",
        "愤怒": "anger, jaw clenched, E@1/3, --no double chin"
      }
    }
  },
  "shots": {
    "001": {
      "shot_type": "Master",
      "prompt": "Wang Bo, blue official robe, kneeling, eyes at upper 1/3, rainy night, lightning, cold blue, --ar 9:16, vertical framing, mobile optimized",
      "platform": "all",
      "coverage": "Master"
    }
  }
}
```

---

## 六、竖屏 AI 生成实战案例

### 6.1 案例：《大唐文圣》第一集（竖屏重构）

**横屏原版**：
- 分镜数：10-12 镜
- 提示词长度：200-250 词/镜
- 画幅：`--ar 16:9`
- 构图：`centered composition`

**竖屏重构版**：
- 分镜数：**5-6 镜**（减少 50%）
- 提示词长度：**120-150 词/镜**（压缩 30%）
- 画幅：`--ar 9:16`
- 构图：`vertical framing, eyes at upper 1/3`

**分镜（竖屏 5 镜方案）**：

```
镜 001 (Master - 2-shot, 5 秒)：
建立权力关系，陆雪冷笑："王勃，可认得此物？"
（对白 10 字，微表情：冷笑）

镜 002 (Single A - 陆雪, 3 秒)：
陆雪展开休书："休书。你自由了。"
（对白 8 字，微表情：嘴角右牵 3°）

镜 003 (Single B - 王勃, 3 秒)：
王勃震惊："你……你怎可——"
（对白 8 字，微表情：瞳孔骤缩）

镜 004 (OTS merged, 2 秒)：
陆雪转身："签了它。"
（对白 4 字，微表情：侧脸，决绝）

镜 005 (Single B - 王勃, 5 秒)：
王勃颤抖，拿起笔："……好。"
（对白 3 字，微表情：咬肌鼓起，鼻翼扩张）
```

**提示词（竖屏对话）**：

```
镜 001：
Lu Xue (upper 1/3) and Wang Bo (lower 1/3),
vertical two-shot, power dynamics,
rainy night, lightning, --ar 9:16, vertical framing

镜 002：
Lu Xue, waist-up, eyes at upper 1/3,
unfolding divorce paper, micro-expression (lip twitch),
dialogue: "Sign it.", --ar 9:16, vertical framing

镜 003：
Wang Bo, waist-up, eyes at upper 1/3,
shock, pupil constriction, micro-expression,
dialogue: "You... how could you...", --ar 9:16, vertical framing
```

---

*专为 9:16 竖屏画幅重构，适配抖音/TikTok/Reels/Shorts/即梦等平台。*
