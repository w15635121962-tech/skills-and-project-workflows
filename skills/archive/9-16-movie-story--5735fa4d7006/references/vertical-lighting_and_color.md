# 光影与色彩（竖屏 9:16 版）

> **适用**：竖屏影视项目的光影与色彩设计  
> **核心**：9:16 画幅下的光影色彩系统、竖屏适配、手机端优化

---

## 光影与色彩基础（竖屏版）

### 横屏 vs 竖屏光影与色彩

| 维度 | 横屏 16:9 | 竖屏 9:16 |
|------|------------|------------|
| **光影** | 左右布光 | 上下布光 |
| **色彩** | 任意 | 避免顶部 20%（状态栏） |
| **对比** | 任意 | 中心稳定区高对比 |
| **情绪** | 任意 | 眼睛位置强调 |

---

## 竖屏光影设计

### 1. 顶光 (Top Lighting)
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

### 2. 底光 (Bottom Lighting)
```
Bottom Lighting (Vertical Adaptation):
- 光源位置：画面底部（y=1.0）
- 阴影方向：垂直向上（y 减少方向）
- 适用情绪：恐惧、神秘、不安
- 电影感：upward shadows，恐怖感
```

**提示词关键词**：
```
bottom lighting, low lighting, upward shadows,
vertical frame, 9:16, mysterious,
horror lighting, unsettling
```

### 3. 侧光 (Side Lighting)
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

### 4. 顺光 (Front Lighting)
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

## 竖屏色彩设计

### 色彩情绪映射（竖屏版）
| 情绪 | 主色 | 辅色 | 强调色 | 适用场景 |
|------|------|------|--------|---------|
| **愤怒** | 深红 | 黑 | 金 | 争吵、冲突 |
| **悲伤** | 冷蓝 | 灰 | 白 | 哭泣、离别 |
| **恐惧** | 深紫 | 黑 | 红 | 惊悚、悬疑 |
| **喜悦** | 暖黄 | 白 | 橙 | 笑容、团圆 |
| **焦虑** | 冷绿 | 灰 | 红 | 紧张、等待 |
| **平静** | 中性灰 | 白 | 蓝 | 对话、日常 |
| **权力** | 深蓝 | 金 | 红 | 权谋、对峙 |
| **脆弱** | 浅紫 | 白 | 灰 | 受伤、哭泣 |

### 竖屏色彩应用规则
1. **主色占比**：60-70%（背景/服装）
2. **辅色占比**：20-30%（道具/环境）
3. **强调色占比**：5-10%（光影/细节）
4. **顶部 20%**：避免高饱和色（状态栏区域）
5. **底部 20%**：避免高饱和色（字幕区域）
6. **中心稳定区**：高对比度（人脸/主体区域）

---

## 竖屏光影与色彩提示词模板

### 模板 1：顶光 + 硬阴影（愤怒）
```
{c haracter}, top lighting, hard shadows,
chiaroscuro, vertical composition, 9:16 frame,
eyes at upper third, intense anger,
--ar 9:16 --style raw --stylize 150
```

### 模板 2：底光 + 柔光（悲伤）
```
{c haracter}, bottom lighting, soft glow,
vertical composition, 9:16 frame,
eyes at upper third, sad expression,
--ar 9:16 --style raw --stylize 100
```

### 模板 3：侧光 + 柔光（对话）
```
{t wo characters}, side lighting,
Rembrandt lighting, chiaroscuro,
vertical composition, 9:16 frame,
dialogue scene, emotional depth,
--ar 9:16 --style raw --stylize 120
```

### 模板 4：顺光 + 均匀（日常）
```
{c haracter}, front lighting, even illumination,
soft lighting, vertical composition, 9:16 frame,
peaceful daily life, natural light,
--ar 9:16 --style raw --stylize 80
```

---

## 竖屏光影与色彩检查清单

### ✅ 必选要素
- [ ] 光影方案已选择（顶光/底光/侧光/顺光）
- [ ] 色彩方案已定义（主色/辅色/强调色）
- [ ] 情绪已映射（愤怒/悲伤/恐惧/喜悦/焦虑/平静）
- [ ] 竖屏关键词已添加（`vertical composition, 9:16 frame`）
- [ ] 提示词已生成（含 `--ar 9:16`）
- [ ] 顶部/底部 20% 无高饱和色

### ✅ 进阶优化
- [ ] 使用三阶段色彩演变（冷→暖→对比）
- [ ] 使用竖屏专属构图（眼睛在画面上 1/3）
- [ ] 使用大光圈（f/1.8，浅景深）
- [ ] 使用电影感光影（chiaroscuro/Rembrandt/顶光/底光）
- [ ] 使用胶片感（film grain/35mm）

---

## 总结

竖屏光影与色彩 = **横屏光影与色彩** + **9:16 画幅适配** + **手机端优化**

**核心差异**：
1. 光影：上下布光（而非左右）
2. 色彩：避免顶部/底部 20% 高饱和色
3. 眼睛位置在画面上 1/3（y≈0.33）
4. 提示词必须含 `--ar 9:16`
