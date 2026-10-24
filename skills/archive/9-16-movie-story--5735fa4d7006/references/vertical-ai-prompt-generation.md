# AI 提示词生成指南（竖屏 9:16 版）

> **适用**：竖屏分镜 → AI 图像/视频生成提示词  
> **核心差异**：9:16 画幅约束、竖屏构图关键词、手机端视觉锚点

---

## 四步黄金框架（竖屏适配）

### 第一步：主体描述（Subject）
```
{Screenwriter's Description} + {Vertical Composition Keyword}
```

**竖屏构图关键词库**：
| 构图类型 | 关键词 | 适用场景 |
|---------|--------|---------|
| 中心构图 | `centered composition, vertical frame, subject fills screen` | 人物特写、情感戏 |
| 三分法 | `rule of thirds, eyes at upper third, vertical composition` | 对话、单人镜头 |
| 满屏构图 | `full-body portrait, 9:16 frame, standing vertically` | 全身镜头 |
| 极端特写 | `extreme close-up, top of frame, vertical cinematography` | 情绪爆发 |
| 低头视角 | `low angle, looking up, vertical framing` | 权力感、仰视 |
| 俯拍 | `high angle, looking down, mobile vertical shot` | 脆弱感、俯视 |

### 第二步：视觉锚点（Visual Anchors）
```
{Character Visual Bible Keywords} + {Costume/Props} + {Lighting}
```

**竖屏视觉锚点注意事项**：
- 人脸必须在 **中心稳定区**（x:0.25-0.75, y:0.25-0.65）
- 眼睛位置在 **画面上 1/3 处**
- 头顶留 **15% 呼吸空间**
- 下巴到画面底部留 **20% 空间**

### 第三步：技术参数（Technical Specs）
```
--ar 9:16 --style raw --v 6.0 --stylize 50
```

**竖屏专属参数**：
| 参数 | 值 | 说明 |
|------|-----|------|
| `--ar` | `9:16` | 竖屏画幅 |
| `--style` | `raw` | 减少 AI 美化，保留真实感 |
| `--stylize` | `50-250` | 竖屏建议 50-150（避免过度艺术化）|
| `--weird` | `0-100` | 竖屏慎用，容易破坏构图 |
| `--tile` | - | 竖屏不适用 |

**提示词模板（竖屏）**：
```
{主体描述}, {竖屏构图关键词}, {视觉锚点},
{光影情绪}, {质感层},
--ar 9:16 --style raw --stylize 100 --v 6.0
```

### 第四步：质感层（Photorealism Layer）
```
{Texture} + {Lighting} + {Camera}
```

**竖屏质感层关键词**：
| 类别 | 竖屏适配关键词 |
|------|----------------|
| 纹理 | `skin texture visible, pores, natural skin imperfections, 9:16 close-up` |
| 光影 | `soft top lighting, vertical frame lighting, shallow depth of field, bokeh background` |
| 镜头 | `85mm portrait lens, f/1.8, mobile vertical cinematography, smartphone footage aesthetic` |
| 胶片 | `Arri Alexa 65, Cooke Anamorphic, vertical mobile master, 2.39:1 desqueezed to 9:16` |

---

## 写实质感层（竖屏版）

### 皮肤纹理
```
skin texture visible, visible pores, natural skin imperfections,
fine facial details, realistic skin, 9:16 close-up portrait,
unretouched, natural skin texture
```

### 光影质感
```
soft top lighting, natural light, window light,
vertical frame lighting, mobile cinematography lighting,
shallow depth of field, bokeh, background blur
```

### 镜头质感
```
85mm portrait lens, f/1.8, Arri Alexa 65,
Cooke Anamorphic, vertical mobile master,
smartphone footage, TikTok aesthetic, Reels style
```

### 胶片质感
```
film grain, 35mm film, Kodak Vision3,
vertical film scan, mobile film aesthetic
```

---

## 负面提示词（竖屏版）

### 通用负面词
```
--no deformed, bad anatomy, disfigured, poorly drawn face,
mutation, mutated, extra limb, missing limb, floating limbs,
(long neck, disconnected head, cropped head,)
```

### 竖屏专属负面词
```
--no horizontal format, landscape format, 16:9, 4:3,
bad vertical composition, subject cut off at knees,
face not in frame, eyes not visible,
top of head cut off, chin cut off,
text, watermark, signature, bad 9:16 aspect ratio
```

### 中文负面词（Seedance/即梦）
```
避免：变形，解剖错误，脸部绘制错误，
突变，额外肢体，缺失肢体，漂浮肢体，
长脖子，头部断开，头部被裁剪，
横屏格式，16:9，4:3，
竖屏构图错误，膝盖处被切，
脸部不在画面中，眼睛不可见，
头顶被切，下巴被切
```

---

## 平台适配（竖屏版）

### Midjourney (v6/v7)
```
{提示词} --ar 9:16 --style raw --stylize 100 --v 6.0 --weird 0
```
**注意**：MJ v6 对 9:16 支持良好，但需注意主体不被裁剪。

### Seedance 2.0（即梦）
```
【镜头描述】
【主体描述，竖屏构图】
【动作/表情】
【光影色彩】
【质感层】
【--ar 9:16】
```
**注意**：即梦对中文提示词理解更好，建议用中文写主体描述。

### Kling 3.0
```
{Subject}, {Action}, {Vertical Composition},
{Lighting}, {Texture}, --ar 9:16
```
**注意**：Kling 对动作描述敏感，建议详细写动作。

### Runway Gen-3
```
{Subject} {Action} {Vertical Frame} {Lighting}
```
**注意**：Runway 提示词要简洁，避免过长。

### Pika 2.0
```
{Subject}, {Action}, vertical 9:16, {Lighting}, {Style}
```
**注意**：Pika 对风格词敏感，建议加 `cinematic, photorealistic`。

---

## 竖屏提示词检查清单

### ✅ 必选要素
- [ ] `--ar 9:16` 参数已添加
- [ ] 主体描述包含竖屏构图关键词
- [ ] 人脸在中心稳定区（x:0.25-0.75, y:0.25-0.65）
- [ ] 眼睛位置在画面上 1/3 处
- [ ] 负面提示词包含竖屏专属负面词
- [ ] 质感层包含竖屏适配关键词

### ✅ 平台适配
- [ ] Midjourney：`--style raw --v 6.0`
- [ ] Seedance：中文主体描述 + `--ar 9:16`
- [ ] Kling：详细动作描述 + `--ar 9:16`
- [ ] Runway：简洁提示词 + 垂直构图关键词
- [ ] Pika：`cinematic, photorealistic` + `vertical 9:16`

### ✅ 视觉一致性
- [ ] 角色视觉锚点关键词已添加（六维精度）
- [ ] 场景视觉锚点关键词已添加
- [ ] 服装/道具锚点已添加
- [ ] 光影情绪关键词已添加

---

## 示例：完整竖屏提示词

### 示例 1：王勃 特写（情感戏）
```
Close-up of young man, early 20s, wearing dark blue round-collar robe,
golden peony embroidery at collar, hair in tightly bound Daoist topknot,
piercing phoenix eyes with starlight, intense gaze,
vertical composition, eyes at upper third, 9:16 frame,
dim candlelight, chiaroscuro, side lighting from right,
skin texture visible, pores, natural skin imperfections,
85mm portrait lens, f/1.8, shallow depth of field,
Arri Alexa 65, vertical mobile master,
--ar 9:16 --style raw --stylize 100 --v 6.0
--no deformed, bad anatomy, horizontal format, face cut off
```

### 示例 2：陆雪 中景（动作戏）
```
Medium shot, young woman, early 20s, wearing apricot pink tight-sleeved top,
silk billowing sleeves, hair in elaborate cross-bun with pearl hairpin,
determined expression, drawing sword,
vertical composition, centered, 9:16 frame,
dim candlelight, sunset glow through window,
dynamic motion, wind blowing sleeves,
80mm lens, f/2.8, vertical cinematography,
--ar 9:16 --style raw --stylize 150 --v 6.0
--no static, boring, horizontal format, bad vertical composition
```

### 示例 3：裴子华 全景（权力感）
```
Full body shot, man in 40s, handsome and gentle,
parallel-collar deep indigo robe, python-patterned belt,
standing confidently, slight smile,
low angle, looking up, vertical framing, 9:16,
opal platform, candlelight, golden glow,
32mm lens, f/4.0, deep depth of field,
--ar 9:16 --style raw --stylize 50 --v 6.0
--no high angle, weak posture, horizontal format
```

---

## 常见错误

### ❌ 错误 1：忘记 `--ar 9:16`
**后果**：生成横屏图，无法使用。  
**解决**：每个提示词必须包含 `--ar 9:16`。

### ❌ 错误 2：人脸不在中心稳定区
**后果**：人脸被裁剪或位置尴尬。  
**解决**：添加 `eyes at upper third, vertical composition` 等关键词。

### ❌ 错误 3：使用横屏构图关键词
**后果**：AI 生成横屏构图，主体太小。  
**解决**：使用竖屏专属构图关键词（见第一步）。

### ❌ 错误 4：负面提示词缺少竖屏专属词
**后果**：生成横屏图或构图错误。  
**解决**：添加 `--no horizontal format, 16:9, bad vertical composition`。

---

## 总结

竖屏 AI 提示词 = **横屏提示词** + **竖屏构图适配** + **9:16 技术参数**

**核心差异**：
1. 必须加 `--ar 9:16`
2. 主体描述加竖屏构图关键词
3. 人脸位置在画面上 1/3
4. 负面提示词加竖屏专属负面词
5. 质感层加 `vertical cinematography` 等关键词
