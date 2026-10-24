# 视频提示词语镜头参考（竖屏 9:16 版）

> **适用**：竖屏影视项目的视频提示词语镜头设计  
> **核心**：9:16 画幅下的镜头语言、竖屏提示词、手机端优化

---

## 镜头语言基础（竖屏版）

### 横屏 vs 竖屏镜头语言

| 维度 | 横屏 16:9 | 竖屏 9:16 |
|------|------------|------------|
| **镜头类型** | 全景/中景/特写 | 全景/中景/特写（相同） |
| **构图** | 左右平衡 | 上下平衡 |
| **视线** | 水平（左←→右） | 垂直（上←→下）或对角线 |
| **运镜** | 左右摇/推拉 | 上下摇/推拉 |
| **剪辑节奏** | 2-4 秒/镜 | 1-3 秒/镜（快切） |

---

## 竖屏镜头语言

### 1. 全景（Establishing Shot）
```
Establishing Shot (Vertical):
- 展示环境全貌
- 人物占画面 10-20%
- 适用：定场、转场
```

**提示词关键词**：
```
establishing shot, wide shot, full location,
vertical composition, 9:16 frame,
environment visible, cinematic
```

### 2. 中景（Medium Shot）
```
Medium Shot (Vertical):
- 人物腰部以上
- 人物占画面 40-60%
- 适用：对话、动作
```

**提示词关键词**：
```
medium shot, waist-up, vertical composition,
9:16 frame, rule of thirds,
dialogue scene, cinematic
```

### 3. 特写（Close-Up）
```
Close-Up (Vertical):
- 人物胸部以上
- 人物占画面 60-80%
- 适用：情绪、细节
```

**提示词关键词**：
```
close-up, chest-up, vertical composition,
9:16 frame, eyes at upper third,
emotional scene, cinematic
```

### 4. 极端特写（Extreme Close-Up）
```
Extreme Close-Up (Vertical):
- 人物面部占满画面
- 眼睛/嘴巴占画面 50% 以上
- 适用：情绪爆发、细节
```

**提示词关键词**：
```
extreme close-up, face fill frame,
vertical composition, 9:16 frame,
intense emotion, cinematic
```

---

## 竖屏镜头语言提示词模板

### 模板 1：全景（定场）
```
Establishing shot, {location},
exterior, {time of day}, {weather},
vertical composition, 9:16 frame,
wide shot, full location visible,
--ar 9:16 --style raw --stylize 50
```

### 模板 2：中景（对话）
```
Medium shot, {character} and {character},
waist-up, vertical composition, 9:16 frame,
rule of thirds, eyes at upper third,
dialogue scene, cinematic,
--ar 9:16 --style raw --stylize 100
```

### 模板 3：特写（情绪）
```
Close-up, {character}'s face,
{emotion}: {detailed emotion description},
eyes at upper third, vertical framing,
{lighting}, {skin texture},
--ar 9:16 --style raw --stylize 150
```

### 模板 4：极端特写（情绪爆发）
```
Extreme close-up, {character}'s eyes,
intense emotion, eyes fill frame,
vertical composition, 9:16 frame,
{lighting}, {skin texture},
--ar 9:16 --style raw --stylize 200
```

---

## 竖屏镜头语言检查清单

### ✅ 必选要素
- [ ] 镜头类型已选择（全景/中景/特写/极端特写）
- [ ] 构图已选择（中心/三分法/满屏）
- [ ] 人物在中心稳定区（x:0.25-0.75, y:0.25-0.65）
- [ ] 眼睛位置在画面上 1/3（y≈0.33）
- [ ] 提示词已生成（含 `--ar 9:16`）
- [ ] 竖屏关键词已添加（`vertical composition, 9:16 frame`）

### ✅ 进阶优化
- [ ] 使用浅景深（shallow depth of field）
- [ ] 使用电影感构图（cinematic）
- [ ] 使用情绪强化（emotional intensity）
- [ ] 使用动态构图（dynamic composition）
- [ ] 使用光影质感（lighting and texture）

---

## 总结

竖屏镜头语言 = **横屏镜头语言** + **9:16 构图适配** + **垂直视线**

**核心差异**：
1. 人物在画面中心或上 1/3
2. 视线以垂直/对角线为主
3. 眼睛位置在画面上 1/3
4. 提示词必须含 `--ar 9:16`
