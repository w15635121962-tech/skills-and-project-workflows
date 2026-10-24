# 人像摄影提示词（竖屏 9:16 版）

> **适用**：竖屏人像摄影的 AI 提示词生成  
> **核心**：9:16 画幅下的人像提示词、竖屏构图、手机端优化

---

## 人像摄影基础（竖屏版）

### 横屏 vs 竖屏人像摄影

| 维度 | 横屏 16:9 | 竖屏 9:16 |
|------|------------|------------|
| **构图** | 左右平衡 | 上下平衡 |
| **视线** | 水平 | 垂直/对角线 |
| **光圈** | f/1.8-f/4.0 | f/1.8-f/2.8（更浅景深） |
| **焦距** | 85mm | 85mm（相同） |
| **提示词** | 任意 | 必须含 `--ar 9:16` |

---

## 竖屏人像摄影构图

### 1. 中心构图（推荐）
```
Center Composition (Portrait):
- 人脸在画面中心（x=0.5, y=0.4）
- 眼睛在画面上 1/3（y≈0.33）
- 头顶留 15% 呼吸空间（y≈0.15）
- 下巴到画面底部留 20%（y≈0.8）
- 适用：特写、情绪镜、单人镜头
```

**提示词关键词**：
```
centered composition, vertical portrait, 9:16 frame,
eyes at upper third, rule of thirds vertical,
shallow depth of field, bokeh background,
85mm portrait lens, f/1.8
```

### 2. 三分法（对话/对视）
```
Rule of Thirds (Portrait):
- 画面分成 3x3 网格
- 眼睛在上横线上（y≈0.33）
- 鼻子在中心横线上（y≈0.5）
- 嘴巴在下横线上（y≈0.66）
- 人脸在左/右竖线上（x≈0.33 或 x≈0.66）
- 适用：对话镜、中景、全身镜
```

**提示词关键词**：
```
rule of thirds vertical, eyes at upper third,
vertical framing, 9:16, off-center composition,
dynamic vertical framing
```

### 3. 满屏构图（情绪爆发）
```
Full-Frame Composition (Portrait):
- 人脸占满画面（上下贴合）
- 头顶留 5% 呼吸空间（y≈0.05）
- 下巴留 5% 呼吸空间（y≈0.95）
- 左右留 10% 呼吸空间（x≈0.1, x≈0.9）
- 适用：特写、情绪爆发、动作镜
```

**提示词关键词**：
```
full-frame vertical, close-up, extreme close-up,
fills screen, 9:16 full frame,
intense gaze, emotional impact
```

---

## 竖屏人像摄影光影

### 1. 柔光（Soft Lighting）
```
Soft Lighting (Portrait):
- 光源：窗户光/烛光/灯笼光
- 强度：低（30-50%）
- 阴影：柔和，无明显阴影
- 适用：深情对视、对话、日常亲密
```

**提示词关键词**：
```
soft lighting, gentle light, romantic,
vertical frame, 9:16, intimate moment,
shallow depth of field, bokeh background,
cinematic lighting, emotional
```

### 2. 侧光（Side Lighting）
```
Side Lighting (Portrait):
- 光源：侧面（左或右）
- 强度：中（50-70%）
- 阴影：明暗对比，Rembrandt lighting
- 适用：深情对视、亲吻、拥抱
```

**提示词关键词**：
```
side lighting, Rembrandt lighting, chiaroscuro,
vertical frame, 9:16, intimate moment,
half face in shadow, emotional depth,
cinematic lighting, romantic
```

### 3. 逆光（Backlighting）
```
Backlighting (Portrait):
- 光源：背后（摄像机对面）
- 强度：中（50-70%）
- 阴影：面部较暗，轮廓光明显
- 适用：亲吻、拥抱、剪影
```

**提示词关键词**：
```
backlighting, silhouette, romantic,
vertical frame, 9:16, intimate moment,
rim light, emotional, cinematic,
soft glow, gentle
```

---

## 竖屏人像摄影提示词模板

### 模板 1：特写（情绪）
```
Extreme close-up of {character},
{emotion}: {detailed emotion description},
eyes at upper third, vertical framing,
{lighting}, {skin texture},
85mm portrait lens, f/1.8,
shallow depth of field, bokeh background,
--ar 9:16 --style raw --stylize 200
```

### 模板 2：中景（对话）
```
Medium shot of {character},
waist-up, vertical composition, 9:16 frame,
rule of thirds, eyes at upper third,
{dialogue emotion}, {lighting},
{detailed costume description},
--ar 9:16 --style raw --stylize 150
```

### 模板 3：全身（动作）
```
Full body shot of {character},
{action}, dynamic motion,
vertical composition, 9:16 frame,
fills screen, full-body shot,
{lighting}, {texture},
--ar 9:16 --style raw --stylize 100
```

### 模板 4：多人（对话）
```
Medium shot of two people facing each other,
{character A description}, {character B description},
vertical composition, 9:16 frame,
{dialogue emotion}, {lighting},
--ar 9:16 --style raw --stylize 100
```

---

## 竖屏人像摄影检查清单

### ✅ 必选要素
- [ ] 构图已选择（中心/三分法/满屏）
- [ ] 眼睛位置在画面上 1/3（y≈0.33）
- [ ] 人脸在中心稳定区（x:0.25-0.75, y:0.25-0.65）
- [ ] 光影已选择（柔光/侧光/逆光）
- [ ] 提示词已生成（含 `--ar 9:16`）
- [ ] 竖屏关键词已添加（`vertical composition, 9:16 frame`）

### ✅ 进阶优化
- [ ] 使用浅景深（shallow depth of field）
- [ ] 使用柔光（soft lighting）
- [ ] 使用电影感光影（chiaroscuro/Rembrandt/backlighting）
- [ ] 使用情绪连接关键词（emotional connection/intimate/romantic）
- [ ] 使用 85mm 人像镜头描述

---

## 总结

竖屏人像摄影 = **横屏人像摄影** + **9:16 构图适配** + **情感强化**

**核心差异**：
1. 眼睛在画面上 1/3（而非水平中心）
2. 人脸在中心稳定区（x:0.25-0.75, y:0.25-0.65）
3. 运镜以垂直运动为主（推拉/俯仰）
4. 光影强调单光源（烛光/顶光/底光）
5. 提示词必须含 `--ar 9:16`
