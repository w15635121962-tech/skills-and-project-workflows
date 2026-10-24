# AI 绘画提示词全集生成 (AI Prompt Generation)

## 核心原则

AI 绘画提示词（Prompt）是将分镜视觉描述转化为 AI 可执行指令的桥梁。好的提示词 = 精准的画面控制 + 一致的风格约束。

---

## 一、提示词结构公式

### 标准公式

```
[主体描述] + [动作/姿态] + [环境/背景] + [光线] + [色彩] + [构图/机位] + [风格] + [技术参数]
```

### 权重排序（从左到右，重要性递减）

```
主体 > 环境 > 光线 > 构图 > 风格 > 技术
```

---

## 二、各元素详细指南

### 2.1 主体描述

```
基础结构：
[年龄] + [性别/种族] + [体型] + [服装] + [发型] + [表情/情绪]

示例：
"a 35-year-old East Asian man, slim build, wearing a wrinkled 
white dress shirt with sleeves rolled up, messy black hair, 
tired but determined expression"
```

**要点**：
- 年龄和种族明确（避免 AI 随机化）
- 服装描述具体（颜色+材质+状态）
- 表情用一个情绪词 + 身体语言补充

### 2.2 环境/背景

```
基础结构：
[室内/室外] + [具体地点] + [时间] + [天气] + [关键道具]

示例：
"a dimly lit cramped kitchen at night, small table with a 
laptop, empty beer cans, through the window city skyline 
at dusk"
```

**要点**：
- 先大后小（先交代空间，再填充细节）
- 明确时间（day/night/dusk/dawn）
- 提及 2-3 个关键道具

### 2.3 光线

```
基础结构：
[光源类型] + [方向] + [强度] + [氛围效果]

示例：
"warm yellow side light from a desk lamp, soft shadows, 
intimate atmosphere"

"cold blue backlight from window, creating a silhouette, 
mysterious mood"
```

**光线关键词库**：
| 类型 | 关键词 |
|------|--------|
| 自然光 | golden hour, overcast, moonlight, blue hour |
| 人工光 | desk lamp, candlelight, neon light, fluorescent |
| 方向 | side lighting, backlight, top lighting, rim light |
| 强度 | soft light, harsh light, low key, high key |
| 氛围 | dramatic lighting, moody, cinematic, ethereal |

### 2.4 构图/机位

```
基础结构：
[景别] + [角度] + [构图法] + [焦点/景深]

示例：
"medium close-up, eye level, centered composition, 
shallow depth of field, bokeh background"

"low angle wide shot, dutch angle, rule of thirds, 
deep focus"
```

**景别关键词**：
| 景别 | 英文提示词 |
|------|-----------|
| 大远景 | extreme wide shot, EWS |
| 远景 | wide shot, WS |
| 全景 | full shot, FS |
| 中景 | medium shot, MS |
| 近景 | medium close-up, MCU |
| 特写 | close-up, CU |
| 大特写 | extreme close-up, ECU |

**角度关键词**：
| 角度 | 英文 |
|------|------|
| 平视 | eye level |
| 俯拍 | high angle, top-down |
| 仰拍 | low angle, from below |
| 鸟瞰 | bird's eye view, aerial |
| 荷兰角 | dutch angle, tilted |

### 2.5 风格

```
基础结构：
[视觉风格] + [艺术风格参考] + [材质/质感]

示例：
"photorealistic, film noir aesthetic, Kodak Portra 400, 
grain texture"

"cinematic, Wong Kar-wai style, warm color palette, 
anamorphic lens flare"
```

**常用风格关键词**：
| 风格 | 关键词 |
|------|--------|
| 写实摄影 | photorealistic, photograph, 35mm film |
| 电影感 | cinematic, movie still, film grain |
| 胶片质感 | Kodak Portra 400, Fujifilm, film grain, vintage |
| 导演风格 | Wong Kar-wai style, Nolan style, Fincher style |
| 画家风格 | Caravaggio lighting, Vermeer composition |

### 2.6 技术参数

```
标准技术后缀：
"4K, ultra detailed, sharp focus, professional photography"
```

---

## 三、一致性保持策略

### 3.1 角色一致性

在所有包含同一角色的提示词中使用相同的角色锚定描述：

```
角色锚定（每次都带上）：
"a 32-year-old East Asian man with sharp jawline, 
dark brown eyes, short black hair styled in side part, 
small mole below left eye, fair skin with warm undertone"
```

### 3.2 场景一致性

在所有同一场景的提示词中使用相同的环境锚定：

```
场景锚定：
"small one-bedroom apartment, off-white walls, 
cluttered desk with laptop, single bed with gray sheets, 
window facing city skyline"
```

### 3.3 风格一致性

所有提示词末尾加上统一风格后缀：

```
项目风格后缀（固定）：
", cinematic still, Kodak Portra 400, natural film grain, 
4K, ultra detailed, professional cinematography"
```

---

## 四、提示词模板速查

### 4.1 角色特写
```
[角色锚定描述], [表情/情绪], [光线描述], 
[背景简述], [风格后缀]
```

### 4.2 环境建立
```
[场景完整描述], [时间/天气], [光线], 
[角色在场景中的位置], [风格后缀]
```

### 4.3 对话场景（双人）
```
[角色A描述] and [角色B描述], [关系/姿态], 
[环境], [光线], [构图], [风格后缀]
```

### 4.4 动作场景
```
[角色描述] in [动作姿态], [环境], 
dynamic composition, motion blur, 
dramatic lighting, [风格后缀]
```

### 4.5 情绪空镜
```
[空镜主体：物品/风景/建筑], 
[光线和氛围], [色彩描述], 
metaphorical, poetic, [风格后缀]
```

---

## 五、负面提示词 (Negative Prompt)

### 通用负面提示词

```
cartoon, anime, illustration, painting, drawing, 
blurry, low quality, deformed, disfigured, 
bad anatomy, extra limbs, extra fingers, 
watermark, text, logo, signature,
oversaturated, plastic, artificial, 
3D render, CGI
```

### 写实风格额外添加

```
smooth skin, perfect skin, doll-like, 
studio lighting (如不需要), 
stock photo look
```

### 电影感额外添加

```
modern digital look (如追求胶片感),
HDR (如不需要), 
ultra sharp (如追求胶片柔化)
```
