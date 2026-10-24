# 光影提示词库（竖屏 9:16 版）

> **适用**：竖屏分镜的光影提示词快速查找  
> **核心**：9:16 竖屏光影关键词、情绪映射、平台适配

---

## 光影情绪映射表（竖屏版）

| 情绪 | 光影方案 | 竖屏适配关键词 | 适用场景 |
|------|---------|----------------|---------|
| **愤怒** | 顶光 + 硬阴影 | `top lighting, hard shadows, vertical frame, chiaroscuro` | 争吵、冲突 |
| **悲伤** | 底光 + 柔光 | `bottom lighting, soft glow, vertical composition, teardrop highlights` | 哭泣、离别 |
| **恐惧** | 侧光 + 阴影 | `side lighting, deep shadows, vertical framing, hidden face` | 惊悚、悬疑 |
| **喜悦** | 顺光 + 均匀 | `front lighting, even illumination, vertical frame, sparkle in eyes` | 笑容、团圆 |
| **焦虑** | 顶光 + 高对比 | `top lighting, high contrast, vertical cinematography, sweat highlights` | 紧张、等待 |
| **平静** | 柔光 + 低对比 | `soft lighting, low contrast, vertical composition, natural light` | 对话、日常 |
| **权力** | 底光 + 阴影 | `bottom lighting, upward shadows, low angle, vertical framing, powerful` | 权谋、对峙 |
| **脆弱** | 顶光 + 柔光 | `top lighting, soft shadows, high angle, vertical frame, vulnerable` | 受伤、哭泣 |

---

## 时间段光影（竖屏版）

### 清晨（05:00-07:00）
```
cold blue gel, pre-dawn stillness,
vertical frame, soft top lighting,
shadows long and blue, 9:16 composition
```

### 上午（07:00-11:00）
```
clear morning light, neutral color temperature,
vertical composition, even lighting,
natural window light, 9:16 frame
```

### 正午（11:00-13:00）
```
harsh overhead sun, small high highlights,
vertical frame, top lighting,
short shadows, high contrast
```

### 下午（13:00-17:00）
```
warm golden glow, long shadows,
vertical composition, side lighting,
sunset warm, 9:16 frame
```

### 傍晚（17:00-19:00）
```
golden hour, warm orange and pink,
vertical frame, backlight,
silhouette option, 9:16 composition
```

### 夜晚（19:00-05:00）
```
dim candlelight, chiaroscuro,
vertical frame, single light source,
deep shadows, 9:16 composition,
color temperature: warm 3200K
```

---

## 光源类型（竖屏版）

### 自然光
| 光源 | 关键词 | 竖屏适配 |
|------|--------|----------|
| **窗户光** | `window light, soft directional, vertical frame` | 眼睛在画面上 1/3，光从侧面来 |
| **阳光** | `direct sunlight, hard shadows, 9:16` | 避免人脸过曝，用反光板 |
| **月光** | `moonlight, cold blue, soft, vertical composition` | 低光照，用大光圈 |

### 人造光
| 光源 | 关键词 | 竖屏适配 |
|------|--------|----------|
| **烛光** | `candlelight, warm glow, chiaroscuro, 9:16` | 单光源，强调面部轮廓 |
| **灯笼** | `lantern light, soft warm, vertical frame` | 多个灯笼，营造氛围 |
| **火光** | `firelight, flickering, warm, vertical composition` | 动态光影，用慢快门 |
| **油灯** | `oil lamp, dim warm, vertical frame, 9:16` | 低光照，用大光圈 |

---

## 光影质感层（竖屏版）

### 皮肤质感
```
skin texture visible, pores, natural skin imperfections,
vertical close-up, 9:16 frame,
soft top lighting, shallow depth of field
```

### 光影质感
```
chiaroscuro, Rembrandt lighting,
vertical frame, single light source,
deep shadows, 9:16 composition
```

### 镜头质感
```
85mm portrait lens, f/1.8,
vertical cinematography, 9:16,
shallow depth of field, bokeh background
```

---

## 平台适配（竖屏版）

### Midjourney (v6/v7)
```
{光影描述}, {情绪},
vertical composition, 9:16 frame,
--ar 9:16 --style raw --stylize 100
```

### Seedance 2.0（即梦）
```
【光影】：{光影描述}
【情绪】：{情绪}
【构图】：竖屏 9:16
【--ar 9:16】
```

### Kling 3.0
```
{Lighting}, {Emotion},
vertical 9:16, cinematic,
--ar 9:16
```

### Runway Gen-3
```
{Lighting} {vertical frame} {cinematic}
```

### Pika 2.0
```
{Lighting}, vertical 9:16,
cinematic, photorealistic
```

---

## 竖屏光影提示词检查清单

### ✅ 必选要素
- [ ] 光影描述已添加（顶光/底光/侧光/顺光）
- [ ] 情绪已映射（愤怒/悲伤/恐惧/喜悦/焦虑/平静）
- [ ] 时间段已标注（清晨/上午/正午/下午/傍晚/夜晚）
- [ ] 光源类型已指定（窗户光/阳光/月光/烛光/灯笼/火光）
- [ ] 竖屏关键词已添加（`vertical composition, 9:16 frame`）
- [ ] 负面提示词已添加（`--no flat lighting, boring`)

### ✅ 进阶优化
- [ ] 使用 `chiaroscuro` 强调对比
- [ ] 使用 `Rembrandt lighting` 经典布光
- [ ] 使用 `single light source` 单光源
- [ ] 使用 `shallow depth of field` 浅景深
- [ ] 使用 `bokeh background` 背景虚化

---

## 示例：完整竖屏光影提示词

### 示例 1：愤怒（顶光 + 硬阴影）
```
Close-up of young man, early 20s,
angry expression, veins bulging,
top lighting, hard shadows, chiaroscuro,
vertical composition, eyes at upper third, 9:16 frame,
--ar 9:16 --style raw --stylize 150
--no flat lighting, soft lighting, smiling
```

### 示例 2：悲伤（底光 + 柔光）
```
Medium shot of young woman, early 20s,
crying, teardrops, sad expression,
bottom lighting, soft glow,
vertical composition, 9:16 frame,
--ar 9:16 --style raw --stylize 100
--no top lighting, harsh shadows, smiling
```

### 示例 3：权力（底光 + 阴影）
```
Low angle shot of man in 40s,
confident smile, powerful stance,
bottom lighting, upward shadows,
vertical framing, 9:16,
--ar 9:16 --style raw --stylize 50
--no high angle, weak posture, flat lighting
```

---

## 总结

竖屏光影提示词 = **横屏光影提示词** + **竖屏构图适配** + **9:16 关键词**

**核心差异**：
1. 必须加 `vertical composition, 9:16 frame`
2. 眼睛位置在画面上 1/3（顶光适用）
3. 人脸在中心稳定区（底光适用）
4. 单光源从侧面来（避免面部过曝）
5. 负面提示词加 `--no flat lighting, boring`
