# 几何光影（竖屏 9:16 版）

> **适用**：竖屏影视项目的几何光影设计  
> **核心**：9:16 画幅下的几何光影、竖屏构图、手机端优化

---

## 几何光影基础（竖屏版）

### 横屏 vs 竖屏几何光影

| 维度 | 横屏 16:9 | 竖屏 9:16 |
|------|------------|------------|
| **光源位置** | 左/右/中心 | 上/下/中心 |
| **阴影方向** | 水平 | 垂直 |
| **构图** | 左右平衡 | 上下平衡 |
| **视线** | 水平 | 垂直/对角线 |

---

## 竖屏几何光影类型

### 1. 顶光（Top Lighting）
```
Top Lighting (Vertical Adaptation):
- 光源位置：画面顶部（y=0.0）
- 阴影方向：垂直向下（y 增加方向）
- 适用情绪：愤怒、权力、审讯
- 电影感：硬阴影，高对比
```

**提示词关键词**：
```
top lighting, overhead lighting, hard shadows,
vertical frame, 9:16, high contrast,
chiaroscuro, dramatic lighting
```

### 2. 底光（Bottom Lighting）
```
Bottom Lighting (Vertical Adaptation):
- 光源位置：画面底部（y=1.0）
- 阴影方向：垂直向上（y 减少方向）
- 适用情绪：恐惧、神秘、不安
- 电影感： upward shadows，恐怖感
```

**提示词关键词**：
```
bottom lighting, low lighting, upward shadows,
vertical frame, 9:16, mysterious,
horror lighting, unsettling
```

### 3. 侧光（Side Lighting）
```
Side Lighting (Vertical Adaptation):
- 光源位置：画面左侧或右侧（x=0.0 或 x=1.0）
- 阴影方向：水平（x 方向）
- 适用情绪：对话、沉思、矛盾
- 电影感：Rembrandt lighting，明暗对比
```

**提示词关键词**：
```
side lighting, Rembrandt lighting, chiaroscuro,
vertical frame, 9:16, half face in shadow,
dramatic lighting, emotional depth
```

### 4. 顺光（Front Lighting）
```
Front Lighting (Vertical Adaptation):
- 光源位置：摄像机后方（观众方向）
- 阴影方向：背后（不可见）
- 适用情绪：喜悦、平静、日常
- 电影感：均匀光照，柔和
```

**提示词关键词**：
```
front lighting, even illumination, soft lighting,
vertical frame, 9:16, natural light,
gentle shadows, peaceful
```

---

## 竖屏几何光影组合

### 1. 顶光 + 侧光（对话戏）
```
Top + Side Lighting:
- 光源 1：画面顶部（y=0.0），强度 70%
- 光源 2：画面左侧（x=0.0），强度 30%
- 阴影：垂直向下 + 水平向右
- 适用情绪：对话，矛盾，紧张
```

**提示词关键词**：
```
top and side lighting, mixed lighting,
vertical frame, 9:16, dramatic,
high contrast, emotional dialogue
```

### 2. 底光 + 侧光（恐怖戏）
```
Bottom + Side Lighting:
- 光源 1：画面底部（y=1.0），强度 60%
- 光源 2：画面右侧（x=1.0），强度 40%
- 阴影：垂直向上 + 水平向左
- 适用情绪：恐惧，神秘，不安
```

**提示词关键词**：
```
bottom and side lighting, horror lighting,
vertical frame, 9:16, unsettling,
upward and side shadows, mysterious
```

### 3. 顺光 + 顶光（日常戏）
```
Front + Top Lighting:
- 光源 1：摄像机后方，强度 60%
- 光源 2：画面顶部（y=0.0），强度 40%
- 阴影：轻微向下阴影
- 适用情绪：日常，平静，温柔
```

**提示词关键词**：
```
front and top lighting, soft mixed lighting,
vertical frame, 9:16, natural,
gentle shadows, peaceful daily life
```

---

## 竖屏几何光影情绪映射

| 情绪 | 几何光影方案 | 竖屏适配关键词 |
|------|--------------|----------------|
| **愤怒** | 顶光 + 硬阴影 | `top lighting, hard shadows, vertical frame` |
| **悲伤** | 底光 + 柔光 | `bottom lighting, soft glow, vertical composition` |
| **恐惧** | 侧光 + 阴影 | `side lighting, deep shadows, vertical framing` |
| **喜悦** | 顺光 + 均匀 | `front lighting, even illumination, vertical frame` |
| **焦虑** | 顶光 + 高对比 | `top lighting, high contrast, vertical cinematography` |
| **平静** | 顺光 + 低对比 | `front lighting, low contrast, vertical composition` |
| **权力** | 底光 + 阴影 | `bottom lighting, upward shadows, low angle` |
| **脆弱** | 顶光 + 柔光 | `top lighting, soft shadows, high angle` |

---

## 竖屏几何光影检查清单

### ✅ 必选要素
- [ ] 光源位置已定义（上/下/左/右/中心）
- [ ] 阴影方向已定义（垂直/水平/对角线）
- [ ] 情绪已映射（愤怒/悲伤/恐惧/喜悦/焦虑/平静）
- [ ] 光影方案已选择（顶光/底光/侧光/顺光/组合）
- [ ] 竖屏关键词已添加（`vertical frame, 9:16`）
- [ ] 电影感关键词已添加（`chiaroscuro, Rembrandt lighting`）

### ✅ 进阶优化
- [ ] 使用多光源（2-3 个光源）
- [ ] 使用明暗对比（chiaroscuro）
- [ ] 使用经典布光（Rembrandt lighting）
- [ ] 使用单光源（single light source）
- [ ] 使用浅景深（shallow depth of field）

---

## 示例：竖屏几何光影提示词

### 示例 1：愤怒（顶光 + 硬阴影）
```
Close-up of young man, early 20s,
angry expression, veins bulging,
top lighting, hard shadows, chiaroscuro,
vertical composition, eyes at upper third, 9:16 frame,
--ar 9:16 --style raw --stylize 150
--no flat lighting, soft lighting, smiling
```

### 示例 2：恐惧（底光 + 侧光）
```
Medium shot of young woman, early 20s,
fearful expression, looking at camera,
bottom lighting, side lighting, upward shadows,
vertical composition, 9:16 frame, mysterious,
--ar 9:16 --style raw --stylize 200
--no top lighting, front lighting, peaceful
```

### 示例 3：权力（底光 + 阴影）
```
Low angle shot of man in 40s,
confident smile, powerful stance,
bottom lighting, upward shadows,
vertical framing, 9:16, dramatic,
--ar 9:16 --style raw --stylize 50
--no high angle, weak posture, flat lighting
```

---

## 总结

竖屏几何光影 = **横屏几何光影** + **9:16 画幅适配** + **垂直阴影方向**

**核心差异**：
1. 光源位置：上/下/中心（而非左/右/中心）
2. 阴影方向：垂直（而非水平）
3. 构图：上下平衡（而非左右平衡）
4. 提示词必须含 `vertical frame, 9:16`
