# 竖屏 AI 提示词工程 (9:16 Prompt Engineering)

> 为 9:16 竖屏画幅完全重构的 AI 提示词体系。原版 16:9 提示词直接用于竖屏会导致构图失衡、主体偏移、平台裁剪。

---

## 一、四步黄金框架（竖屏重构版）

### 1.1 原版 vs 竖屏版对比

| 步骤 | 16:9 横屏 | 9:16 竖屏 |
|------|-----------|-----------|
| 1. 主体+动作 | 人物+动作 | 人物+动作+**垂直位置** |
| 2. 环境+光影 | 环境+光影 | 环境+光影+**顶部/底部处理** |
| 3. 技术参数 | --ar 16:9 | --ar 9:16 + **vertical framing** |
| 4. 质感层 | 写实质感 | 写实质感+**手机屏显示优化** |

### 1.2 竖屏四步模板

```
{主体}, {动作}, {垂直位置:眼睛在1/3处},
{环境}, {光影},
{技术参数: --ar 9:16, vertical framing, 9:16 aspect ratio},
{质感层: 手机屏优化}
```

### 1.3 示例对比

**横屏原版**：
```
中年男人，蓝色官袍，偏殿跪拜，
阴雨夜，闪电，冷蓝调，
--ar 16:9, cinematic lighting, hyper-detailed
```

**竖屏重构版**：
```
中年男人，蓝色官袍，偏殿跪拜，眼睛在画面上1/3处，
阴雨夜，闪电，冷蓝调，画面底部留互动区，
--ar 9:16, vertical framing, 9:16 aspect ratio, cinematic lighting,
mobile display optimized, hyper-detailed
```

---

## 二、竖屏构图关键词库

### 2.1 垂直位置控制（必须加）

| 关键词 | 效果 | 使用场景 |
|--------|------|---------|
| `eyes at upper 1/3` | 眼睛在画面上 1/3 | 人物中景/特写 |
| `face centered vertically` | 人脸垂直居中 | 正面特写 |
| `full body, feet at bottom` | 脚贴底，头顶留白 | 全身镜头 |
| `headroom 15%` | 头顶留白 15% | 所有人物镜头 |
| `subject in upper frame` | 主体在上半屏 | 揭示下半屏内容 |
| `subject in lower frame` | 主体在下半屏 | 俯拍/权力镜头 |

### 2.2 竖屏专属构图

| 构图 | 关键词 | 说明 |
|------|--------|------|
| 垂直三分法 | `vertical rule of thirds, eyes at 1/3` | 标准竖屏构图 |
| 中心构图 | `centered composition, vertical symmetry` | 权威/对称场景 |
| top-heavy | `top-heavy composition, subject in upper frame` | 权力关系（上位者） |
| bottom-heavy | `bottom-heavy composition, subject in lower frame` | 弱势/屈服 |
| 垂直引导线 | `vertical leading lines, architectural` | 建筑/楼梯场景 |

### 2.3 避免的横屏关键词（替换）

| ❌ 横屏关键词 | ✅ 竖屏替换 | 原因 |
|--------------|------------|------|
| `centered` | `face centered vertically` | 横屏的 centered 是水平居中 |
| `rule of thirds` | `vertical rule of thirds` | 明确指定垂直三分 |
| `wide shot` | `vertical wide shot, full body` | 避免被理解为横宽 |
| `over the shoulder` | `over the shoulder, vertical framing` | OTS 在竖屏需重新构图 |

---

## 三、平台专属提示词

### 3.1 Midjourney (v7) 竖屏

```
{SUBJECT}, {ACTION}, eyes at upper 1/3, vertical framing,
{ENVIRONMENT}, {LIGHTING},
--ar 9:16 --style raw --v 7 --stylize 250
```

**注意事项**：
- `--style raw` 减少 AI 美化，更接近实拍
- `--stylize 250` 中等风格化（默认 100，太高会失真）
- 加 `--tile` 可生成无缝纹理（用于服装/背景）

### 3.2 Seedance 2.0 多模态（竖屏）

```
参考图中人物，
垂直推进镜头，从脚推到脸部，眼睛保持在画面上1/3处，
阴雨夜，闪电，冷蓝调，浅景深，
9:16竖屏构图，电影感，--ar 9:16
```

**多模态额外指令**：
- 上传参考图后，明确说"保持人物面孔不变"
- 加"竖屏构图，眼睛在1/3处"强化构图约束
- 如果人物变形，加"reference fidelity 0.8"

### 3.3 Kling 3 竖屏

```json
{
  "prompt": "{SUBJECT}, {ACTION}, vertical framing, 9:16",
  "camera_movement": "vertical_push_in",
  "aspect_ratio": "9:16",
  "subject_lock": "eyes_at_1_3"
}
```

**Kling 3 竖屏特性**：
- 支持 `camera_movement` 参数（vertical_push_in / vertical_pull_out / tilt_up / tilt_down）
- `subject_lock` 可锁定眼睛位置
- 竖屏模式下，默认 `refine_prompt: true`（自动优化提示词）

### 3.4 Runway Gen-3 (RunwayML) 竖屏

```
{SUBJECT}, {ACTION},
vertical composition, eyes at 1/3, 9:16 aspect ratio,
{LIGHTING}, cinematic, hyper-realistic
```

**Runway 竖屏注意**：
- 在 web 端选择 `Aspect Ratio: 9:16 (Portrait)`
- 提示词里也要写 `--ar 9:16`（双保险）
- `Motion Score: 5-7`（太低会卡顿，太高会抖动）

### 3.5 即梦 (Dreamina) 竖屏

```
{主体}, {动作}, 竖屏构图, 眼睛在画面上1/3,
{环境}, {光影},
--ar 9:16, 电影感, 写实风格
```

**即梦特性**：
- 中文提示词效果更好
- 支持"参考人物"功能（上传剧照保持面孔）
- 竖屏模式下，自动添加 `mobile optimized` 后缀

---

## 四、负面提示词（竖屏专用）

### 4.1 基础负面词

```
--no horizontal composition, letterbox, black bars on sides,
face cropped, head missing, eyes at bottom,
bottom frame cluttered, UI overlapping,
double chin, distorted face, bad anatomy,
watermark, text, logo
```

### 4.2 竖屏专属负面词

| 负面词 | 防止的问题 |
|--------|-----------|
| `horizontal composition` | 防止 AI 生成横屏构图 |
| `letterbox` | 防止上下黑边 |
| `face cropped` | 防止人脸被裁切 |
| `eyes at bottom` | 防止眼睛在画面底部 |
| `bottom frame cluttered` | 防止底部杂乱（影响互动区） |
| `UI overlapping` | 防止与平台 UI 重叠 |

### 4.3 各平台负面提示词格式

| 平台 | 格式 |
|------|------|
| Midjourney | `--no {关键词}` 或 `negative prompt: {关键词}` |
| Seedance | `负面提示词: {关键词}`（多模态界面输入框） |
| Kling 3 | `"negative_prompt": "{关键词}"` |
| Runway | `Negative Prompt` 输入框 |
| 即梦 | `负面提示词` 输入框 |

---

## 五、写实质感层（竖屏增强版）

### 5.1 原版质感层

```
摄影质感：Arri Alexa 65, Master Prime 镜头, ProRes 4444
胶片质感：Kodak Vision3 500T, 5207 批次, 轻微颗粒
光影质感：Raking Light 侧光, Chiaroscuro 明暗对比
环境质感：湿气/雾气/灰尘/毛发/织物纹理
```

### 5.2 竖屏增强质感层

在上方基础上，增加：

```
手机屏显示优化：high contrast for mobile, OLED optimized,
small screen readability, sharp details at 720p
竖屏防抖：stabilized for vertical viewing,
no horizontal motion blur
平台适配：optimized for TikTok/Reels/Shorts/Douyin,
safe zone compliant
```

### 5.3 完整竖屏提示词示例

```
中年男人，蓝色官袍，偏殿跪拜，眼睛在画面上1/3处，
阴雨夜，闪电，冷蓝调，画面底部留互动区，
--ar 9:16, vertical framing, 9:16 aspect ratio,
Arri Alexa 65, Master Prime 35mm, ProRes 4444,
Kodak Vision3 500T, 湿气/雨滴/布料纹理,
mobile display optimized, high contrast for mobile,
OLED optimized, optimized for TikTok/Reels/Shorts,
--no horizontal composition, letterbox, face cropped,
eyes at bottom, bottom frame cluttered, watermark
```

---

## 六、批量生成策略（竖屏）

### 6.1 单镜覆盖策略

横屏需要 5-8 个镜头覆盖一个对话场景，竖屏只需 **3-4 个**。

| 镜头 | 横屏 16:9 | 竖屏 9:16 |
|------|-----------|-----------|
| 1. Master | 全景建立空间 | 全身景，脚贴底 |
| 2. Single A | 胸部以上 | 腰部以上，眼睛在 1/3 |
| 3. Single B | 胸部以上 | 腰部以上，眼睛在 1/3 |
| 4. OTS | 过肩镜头 | 过肩+斜下（展示两人） |
| 5. Insert | 物体特写 | 物体竖直构图 |

**竖屏优化**：OTS 和 Insert 可以合并（单镜同时展示物体+人物）

### 6.2 提示词变量替换模板

创建一个 JSON 模板，批量生成：

```json
{
  "character": "王勃",
  "base_prompt": "{char}, {costume}, {action}, eyes at upper 1/3, {environment}, {lighting}, --ar 9:16, vertical framing, {texture}, --no {negative}",
  "variables": {
    "char": ["王勃", "Wang Bo"],
    "costume": ["蓝色官袍", "blue official robe", "wet silk"],
    "action": ["跪拜", "kneeling", "kowtowing"],
    "environment": ["周王府偏殿", "prince's mansion side hall", "rainy night"],
    "lighting": ["闪电照亮", "lit by lightning", "cold blue"],
    "texture": ["mobile display optimized", "OLED optimized"],
    "negative": ["horizontal composition", "face cropped"]
  }
}
```

然后用 Python 批量生成：

```python
import json

with open('vertical_prompt_template.json') as f:
    template = json.load(f)

prompts = []
for char in template['variables']['char']:
    for action in template['variables']['action']:
        prompt = template['base_prompt'].format(
            char=char,
            costume=template['variables']['costume'][0],
            action=action,
            environment=template['variables']['environment'][0],
            lighting=template['variables']['lighting'][0],
            texture=template['variables']['texture'][0],
            negative=', '.join(template['variables']['negative'])
        )
        prompts.append(prompt)
```

---

## 七、质量检查（竖屏提示词）

### 7.1 必检项

- [ ] 是否包含 `--ar 9:16`？
- [ ] 是否包含 `vertical framing` 或 `9:16 aspect ratio`？
- [ ] 是否指定了眼睛位置（`eyes at upper 1/3`）？
- [ ] 是否指定了头顶留白（`headroom 15%`）？
- [ ] 是否包含竖屏负面词（`no horizontal composition, face cropped`）？
- [ ] 是否包含手机屏优化（`mobile display optimized`）？

### 7.2 A/B 测试策略

为同一个镜头生成两个版本：

**版本 A**（基础竖屏）：
```
王勃，蓝色官袍，跪拜，--ar 9:16
```

**版本 B**（完整竖屏）：
```
王勃，蓝色官袍，跪拜，眼睛在画面上1/3处，
阴雨夜，闪电，冷蓝调，--ar 9:16, vertical framing,
mobile display optimized, --no face cropped, horizontal composition
```

然后对比：
- 眼睛位置是否正确？
- 构图是否竖屏友好？
- 人脸是否变形？

---

## 八、常见错误与修正

### 8.1 眼睛位置错误

- ❌ 错误：`.center composition`（横屏理解）
- ✅ 修正：`eyes at upper 1/3, vertical rule of thirds`

### 8.2 人脸变形

- ❌ 错误：提示词只写 `--ar 9:16`，没指定构图
- ✅ 修正：加 `face centered vertically, headroom 15%`

### 8.3 平台 UI 重叠

- ❌ 错误：主体在画面底部 20%
- ✅ 修正：加 `bottom frame empty, space for UI/interaction buttons`

### 8.4 横屏构图残留

- ❌ 错误：提示词包含 `wide shot, panoramic`
- ✅ 修正：替换为 `vertical wide shot, full body, feet at bottom`

---

*针对 9:16 竖屏画幅完全重构，适配 Midjourney/Seedance/Kling/Runway/即梦等平台。*
