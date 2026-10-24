# 写实质感层 — 防 AI 塑料感 (Realism Layer)

## 核心问题

AI 生成的图像/视频有一种难以言说的"塑料感"，主要表现为：
1. **皮肤过于完美**，像打了蜡的苹果
2. **光线过于均匀**，缺乏真实的明暗对比
3. **色彩过于饱和**，像调色过度
4. **材质缺乏质感**，像塑料模型
5. **构图过于对称**，缺乏生活的不规则感

本文档提供一套系统化的方案，在 AI 提示词中加入"写实质感层"，大幅降低 AI 塑料感。

---

## 一、皮肤真实感

### 1.1 问题诊断

| AI 塑料感表现 | 原因 | 解决方案 |
|---------------|------|----------|
| 皮肤零毛孔 | AI 默认"美化" | 明确要求毛孔和纹理 |
| 皮肤过亮/发光 | 全局均匀光线 | 增加阴影和肤色不均 |
| 无瑕疵 | AI 倾向完美 | 要求可见的皮肤特征 |
| 妆容太完美 | AI 默认精致妆 | 指定自然妆或裸妆 |

### 1.2 真实皮肤提示词

```
// 替代 "smooth skin"
"visible skin pores, natural skin texture, subtle skin imperfections, 
slightly uneven skin tone, fine lines around eyes, natural skin 
redness on cheeks"

// 不同年龄的真实皮肤
// 20多岁：
"youthful but natural skin, minimal pores, light freckles"

// 30多岁：
"visible pores, slight fine lines around eyes, natural skin texture"

// 40多岁：
"visible skin texture, laugh lines, slight sagging under eyes, 
natural age spots"

// 50+：
"deep wrinkles, age spots, visible pores, thinning skin, 
natural aging signs"
```

### 1.3 头发真实感

```
// 替代 "perfect hair"
"slightly messy hair, individual hair strands visible, 
flyaway hairs, natural hair movement, 
not perfectly styled, hair falling naturally"
```

---

## 二、光线真实感

### 2.1 问题诊断

| AI 塑料感表现 | 原因 | 解决方案 |
|---------------|------|----------|
| 全局均匀亮 | 缺乏方向性光源 | 指定单一主光源 |
| 无明显阴影 | AI 回避暗部 | 要求阴影和高光区域 |
| 漫反射过多 | 光线缺乏层次 | 增加明暗对比度 |
| 人物面部无阴影 | 平光效果 | 使用侧光/顶光 |

### 2.2 真实光线提示词

```
// 核心原则：一个明确的主光源 + 自然阴影

// 室内：
"single overhead fluorescent light casting harsh shadows, 
uneven lighting, dark corners, light falloff"

"warm desk lamp as only light source, strong directional light, 
deep shadows on opposite side of face, light falloff"

// 室外：
"harsh midday sunlight with deep shadows, high contrast, 
dappled light through leaves, hot spots on pavement"

"overcast sky, soft diffused light, even but flat lighting, 
subtle shadows, muted colors"

// 夜间：
"practical lighting only (street lamps, neon signs), 
strong light sources with rapid falloff, 
deep shadows, pools of light and darkness"
```

### 2.3 阴影真实感

```
// 要求自然阴影
"natural shadows, soft shadow edges, ambient occlusion, 
contact shadows under objects, realistic shadow falloff"

// 避免的：
"even lighting, studio lighting, flat lighting, 
fill light (unless specifically needed)"
```

---

## 三、材质真实感

### 3.1 常见材质提示词

```
// 金属
"brushed metal texture, visible scratches, fingerprints on surface, 
oxidation marks, not perfectly polished"

// 木质
"visible wood grain, natural imperfections, slight wear marks, 
not uniformly colored, natural wood texture"

// 布料
"visible fabric weave, natural wrinkles, slight pilling, 
not perfectly smooth, fabric texture"

// 皮革
"worn leather, patina, creases at stress points, 
not glossy new leather, natural aging marks"

// 食物
"not perfectly arranged food, natural food colors, 
slightly melted edges, natural food texture, 
steam rising from hot food"
```

### 3.2 环境真实感

```
// 不完美的环境
"slightly cluttered, lived-in space, not perfectly clean, 
visible dust in light beams, water stains on ceiling, 
scuffed floor, everyday mess"

// 避免的：
"perfectly clean, pristine, showroom, 
studio set, artificial looking"
```

---

## 四、色彩真实感

### 4.1 问题诊断

| AI 塑料感表现 | 解决方案 |
|---------------|----------|
| 过饱和 | 降低饱和度，指定胶片风格 |
| 色彩过于鲜艳 | 指定自然色温和色调 |
| 色彩一致性过高 | 允许局部色彩变化 |
| HDR 过度 | 指定单一曝光 |

### 4.2 真实色彩提示词

```
// 降低饱和度
"natural color palette, slightly desaturated, 
muted tones, earth tones, not oversaturated"

// 胶片色感
"Kodak Portra 400, natural skin tones, 
slightly warm highlights, muted shadows, 
film grain, analog color"

"Fujifilm Superia, cool tones, slight green cast, 
natural everyday colors, 35mm film look"

// 色温控制
"warm color temperature, tungsten white balance, 
slightly orange tint from indoor lighting"
```

---

## 五、构图真实感

### 5.1 打破完美构图

```
// 替代完美居中
"slightly off-center composition, rule of thirds, 
not perfectly symmetrical, natural framing"

// 加入前景/中景/背景层次
"foreground elements slightly out of focus, 
mid-ground action, background context, 
natural depth layers"

// 允许不完美
"slightly tilted horizon (if appropriate), 
not perfectly level, natural camera position, 
found footage feel"
```

### 5.2 日常感构图

```
// 生活化的视角
"eye-level camera, ordinary perspective, 
as if a friend took this photo, 
snapshot aesthetic, not posed"
```

---

## 六、综合写实提示词模板

### 标准写实后缀

将以下内容添加到所有提示词末尾：

```
", photorealistic, natural skin texture with visible pores, 
slightly uneven lighting, natural shadows, 
not perfectly composed, film grain, 
analog photography, Kodak Portra 400, 
slightly desaturated, muted tones, 
4K, ultra detailed, raw photo"
```

### 按场景调整

| 场景 | 额外添加 |
|------|----------|
| 室内 | "warm color temperature, incandescent light, cluttered background" |
| 室外 | "natural daylight, slight lens flare, atmospheric haze" |
| 夜间 | "low light, visible noise, practical lighting only" |
| 特写 | "macro detail, micro texture, visible imperfections" |

---

## 七、自查清单

生成 AI 图像后，对照以下清单检查：

- [ ] 皮肤是否有可见的纹理和毛孔？
- [ ] 光线是否有明确的方向和阴影？
- [ ] 色彩是否自然，不鲜艳过头？
- [ ] 材质是否有真实质感（不是塑料感）？
- [ ] 环境是否"生活化"（不是展厅感）？
- [ ] 构图是否自然（不是完美对称）？
- [ ] 人物是否看起来像真人（不是人偶）？
- [ ] 整体是否有胶片/摄影质感（不是数字渲染感）？
