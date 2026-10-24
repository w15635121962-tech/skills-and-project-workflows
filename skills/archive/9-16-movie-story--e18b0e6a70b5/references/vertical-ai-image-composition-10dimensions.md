# AI 图像构图 10 维度（竖屏 9:16 版）

> **适用**：竖屏 AI 图像生成的构图设计  
> **核心**：9:16 画幅下的 10 维度构图、竖屏适配、手机端优化

---

## 10 维度构图基础（竖屏版）

### 横屏 vs 竖屏 10 维度构图

| 维度 | 横屏 16:9 | 竖屏 9:16 |
|------|------------|------------|
| **1. 主体大小** | 任意 | 满屏或中心 |
| **2. 主体位置** | 中心/三分法 | 中心/上 1/3 |
| **3. 视线方向** | 水平 | 垂直/对角线 |
| **4. 光影方向** | 左右 | 上下 |
| **5. 色彩重心** | 中心 | 中心稳定区 |
| **6. 动态线** | 对角线 | 对角线（相同） |
| **7. 景深** | 浅/深 | 浅（竖屏优先） |
| **8. 帧内空间** | 左右平衡 | 上下平衡 |
| **9. 文本空间** | 任意 | 底部 20% |
| **10. 负面空间** | 左右 | 上下 |

---

## 竖屏 10 维度构图详解

### 1. 主体大小（Subject Size）
```
Subject Size (Vertical):
- 特写：占画面 60-80%
- 中景：占画面 40-60%
- 全景：占画面 10-20%
- 竖屏适配：满屏或中心
```

**提示词关键词**：
```
close-up, fills screen, vertical frame,
medium shot, waist-up, vertical composition,
wide shot, full location, 9:16 frame
```

### 2. 主体位置（Subject Position）
```
Subject Position (Vertical):
- 中心构图：x=0.5, y=0.4
- 三分法：眼睛在上横线（y≈0.33）
- 满屏构图：y=0.05-0.95
- 竖屏适配：眼睛在画面上 1/3
```

**提示词关键词**：
```
centered composition, eyes at upper third,
rule of thirds vertical, vertical framing,
full-frame vertical, fills screen
```

### 3. 视线方向（Gaze Direction）
```
Gaze Direction (Vertical):
- 垂直：上←→下
- 对角线：左上←→右下 或 右上←→左下
- 水平：左←→右（不推荐）
- 竖屏适配：垂直或对角线
```

**提示词关键词**：
```
looking up, looking down, vertical gaze,
diagonal gaze, looking at camera,
 avoiding horizontal gaze
```

### 4. 光影方向（Lighting Direction）
```
Lighting Direction (Vertical):
- 顶光：y=0.0，阴影向下
- 底光：y=1.0，阴影向上
- 侧光：x=0.0 或 x=1.0，阴影水平
- 竖屏适配：单光源，垂直方向
```

**提示词关键词**：
```
top lighting, bottom lighting, side lighting,
vertical frame lighting, single light source,
chiaroscuro, Rembrandt lighting
```

### 5. 色彩重心（Color Weight）
```
Color Weight (Vertical):
- 主色在中心稳定区（x:0.25-0.75, y:0.25-0.65）
- 辅色在边缘区
- 强调色在眼睛位置（y≈0.33）
- 竖屏适配：中心稳定区高对比
```

**提示词关键词**：
```
color contrast, center stable zone,
eyes at upper third, color emphasis,
vertical color weight, 9:16 frame
```

### 6. 动态线（Dynamic Lines）
```
Dynamic Lines (Vertical):
- 对角线：左上→右下 或 右上→左下
- 垂直线：上→下
- 水平线：左→右（不推荐）
- 竖屏适配：对角线或垂直线
```

**提示词关键词**：
```
diagonal composition, vertical lines,
dynamic diagonal, cinematic composition,
avoiding horizontal lines
```

### 7. 景深（Depth of Field）**竖屏优先：浅景深**
```
Depth of Field (Vertical Priority: Shallow):
- 浅景深：f/1.8-f/2.8，背景虚化
- 深景深：f/8.0-f/11.0，全景清晰
- 竖屏适配：浅景深（突出主体）
```

**提示词关键词**：
```
shallow depth of field, bokeh background,
f/1.8, f/2.8, portrait lens,
vertical cinematography, subject isolation
```

### 8. 帧内空间（Frame Space）
```
Frame Space (Vertical):
- 上下平衡（而非左右平衡）
- 头顶留 15%（y≈0.15）
- 下巴留 20%（y≈0.8）
- 竖屏适配：上下平衡
```

**提示词关键词**：
```
vertical balance, head room 15%,
chin room 20%, vertical framing,
9:16 composition, balanced vertical
```

### 9. 文本空间（Text Space）
```
Text Space (Vertical):
- 底部 20%（y=0.8-1.0）
- 避免遮挡人脸
- 字幕大小：60-80px
- 竖屏适配：底部 20%
```

**提示词关键词**：
```
text at bottom 20%, subtitle space,
no face occlusion, vertical text space,
9:16 frame, mobile subtitle
```

### 10. 负面空间（Negative Space）
```
Negative Space (Vertical):
- 顶部留白（y=0.0-0.2）
- 底部留白（y=0.8-1.0）
- 左右留白（x=0.0-0.1, x=0.9-1.0）
- 竖屏适配：上下留白
```

**提示词关键词**：
```
negative space at top, negative space at bottom,
vertical negative space, 9:16 frame,
breathing room, vertical composition
```

---

## 竖屏 10 维度构图检查清单

### ✅ 必选要素
- [ ] 主体大小已定义（特写/中景/全景）
- [ ] 主体位置已定义（中心/上 1/3）
- [ ] 视线方向已定义（垂直/对角线）
- [ ] 光影方向已定义（顶光/底光/侧光）
- [ ] 色彩重心已定义（中心稳定区）
- [ ] 动态线已定义（对角线/垂直线）
- [ ] 景深已定义（浅景深优先）
- [ ] 帧内空间已定义（上下平衡）
- [ ] 文本空间已定义（底部 20%）
- [ ] 负面空间已定义（上下留白）

### ✅ 进阶优化
- [ ] 使用中心构图（特写/情绪镜）
- [ ] 使用三分法（对话镜/中景）
- [ ] 使用满屏构图（情绪爆发）
- [ ] 使用对角线布局（电影感）
- [ ] 使用浅景深（f/1.8，突出主体）

---

## 示例：竖屏 10 维度构图提示词

### 示例 1：对话镜（中景）
```
Medium shot, two people facing each other,
subject position: centered, eyes at upper third,
gaze direction: vertical (looking down/up),
lighting direction: side lighting, chiaroscuro,
color weight: center stable zone, warm vs cold,
dynamic lines: diagonal composition,
depth of field: shallow (f/1.8),
frame space: vertical balance,
text space: bottom 20%,
negative space: top 15%,
vertical composition, 9:16 frame,
--ar 9:16 --style raw --stylize 150
```

### 示例 2：情绪特写
```
Extreme close-up, {character}'s face,
subject size: fills screen (60-80%),
subject position: eyes at upper third (y≈0.33),
gaze direction: looking at camera,
lighting direction: top lighting, hard shadows,
color weight: eyes emphasized (warm highlight),
dynamic lines: vertical lines (intense gaze),
depth of field: extremely shallow,
frame space: head room 15%, chin room 20%,
text space: bottom 20%,
negative space: minimal,
vertical composition, 9:16 frame,
--ar 9:16 --style raw --stylize 200
```

### 示例 3：定场镜（全景）
```
Establishing shot, {location},
subject size: small (10-20%),
subject position: centered, rule of thirds,
gaze direction: N/A (landscape),
lighting direction: natural light, soft,
color weight: balanced,
dynamic lines: horizontal (landscape) or diagonal,
depth of field: deep (f/8.0),
frame space: vertical balance,
text space: bottom 20%,
negative space: top 20%,
vertical composition, 9:16 frame,
--ar 9:16 --style raw --stylize 80
```

---

## 总结

竖屏 10 维度构图 = **横屏 10 维度构图** + **9:16 画幅适配** + **手机端优化**

**核心差异**：
1. 主体位置：眼睛在画面上 1/3（而非水平中心）
2. 视线方向：垂直或对角线（而非水平）
3. 光影方向：单光源，垂直方向（而非左右）
4. 帧内空间：上下平衡（而非左右平衡）
5. 文本空间：底部 20%（而非底部 10%）
6. 提示词必须含 `--ar 9:16`
