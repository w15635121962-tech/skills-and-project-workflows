# 视频跟拍指南（竖屏 9:16 版）

> **适用**：竖屏影视项目的跟拍镜头设计  
> **核心**：9:16 画幅下的跟拍构图、竖屏运镜、手机端优化

---

## 跟拍基础（竖屏版）

### 横屏 vs 竖屏跟拍

| 维度 | 横屏 16:9 | 竖屏 9:16 |
|------|------------|------------|
| **构图** | 人物在画面中心或三分法 | 人物在画面中心或上 1/3 |
| **运镜** | 水平跟随 | 垂直跟随或对角线跟随 |
| **视线** | 水平（左←→右） | 垂直（上←→下）或对角线 |
| **剪辑节奏** | 3-5 秒/镜 | 2-4 秒/镜（快切） |
| **视觉焦点** | 人物 + 环境 | 人物脸部 + 上半身 |

---

## 竖屏跟拍构图

### 1. 中心构图（推荐）
```
Center Composition (Follow Shot):
- 人物在画面中心（x=0.5, y=0.4）
- 眼睛在画面上 1/3（y≈0.33）
- 头顶留 15% 呼吸空间（y≈0.15）
- 下巴到画面底部留 20%（y≈0.8）
- 适用：单人跟拍、情绪跟拍
```

**提示词关键词**：
```
centered composition, vertical follow shot, 9:16 frame,
eyes at upper third, rule of thirds vertical,
subject centered, vertical cinematography,
handheld following, dynamic motion
```

### 2. 三分法（对话跟拍）
```
Rule of Thirds (Follow Shot):
- 人物在画面左/右竖线（x≈0.33 或 x≈0.66）
- 眼睛在上横线上（y≈0.33）
- 视线方向留白（人物看向画面中心）
- 适用：双人跟拍、对话跟拍
```

**提示词关键词**：
```
rule of thirds vertical, follow shot, 9:16 frame,
eyes at upper third, off-center composition,
dynamic vertical framin, handheld following
```

### 3. 满屏构图（动作跟拍）
```
Full-Frame Composition (Follow Shot):
- 人物占满画面（上下贴合）
- 头顶留 5% 呼吸空间（y≈0.05）
- 下巴留 5% 呼吸空间（y≈0.95）
- 左右留 10% 呼吸空间（x≈0.1, x≈0.9）
- 适用：动作跟拍、打斗跟拍
```

**提示词关键词**：
```
full-frame vertical, follow shot, 9:16 frame,
fills screen, dynamic motion,
intense action, handheld following
```

---

## 竖屏跟拍运镜

### 1. 垂直跟拍（Vertical Follow）
```
Vertical Follow Shot:
- 摄像机在人物前方/后方，垂直跟随
- 速度：中（2-3 秒）
- 方向：垂直跟随（从上到下或从下到上）
- 电影感：浅景深，背景虚化
```

**提示词关键词**：
```
vertical follow shot, handheld following,
vertical cinematography, 9:16 frame,
shallow depth of field, bokeh background,
dynamic motion, cinematic
```

### 2. 对角线跟拍（Diagonal Follow）
```
Diagonal Follow Shot:
- 摄像机在人物斜前方，对角线跟随
- 速度：中（2-3 秒）
- 方向：对角线跟随（左上→右下或右上→左下）
- 电影感：动态构图，情绪变化
```

**提示词关键词**：
```
diagonal follow shot, handheld following,
diagonal motion, 9:16 frame,
dynamic composition, cinematic,
emotional journey
```

### 3. 环绕跟拍（Circular Follow）
```
Circular Follow Shot:
- 摄像机环绕人物拍摄
- 速度：慢（3-5 秒）
- 方向：360° 环绕
- 电影感：展示人物全貌，情绪强化
```

**提示词关键词**：
```
circular follow shot, handheld surrounding,
360 degree shot, 9:16 frame,
dynamic motion, cinematic,
emotional intensit
```

---

## 竖屏跟拍提示词模板

### 模板 1：单人跟拍（中心构图）
```
Medium shot, {character} walking,
centered composition, vertical follow shot,
9:16 frame, eyes at upper third,
handheld following, dynamic motion,
shallow depth of field, bokeh background,
--ar 9:16 --style raw --stylize 150
```

### 模板 2：双人跟拍（三分法）
```
Medium shot, two people walking,
rule of thirds vertical, follow shot,
9:16 frame, eyes at upper third,
handheld following, dynamic motion,
--ar 9:16 --style raw --stylize 150
```

### 模板 3：动作跟拍（满屏构图）
```
Full-body shot, {character} running,
full-frame vertical, follow shot,
9:16 frame, fills screen,
dynamic motion, handheld following,
--ar 9:16 --style raw --stylize 200
```

---

## 竖屏跟拍检查清单

### ✅ 必选要素
- [ ] 构图已选择（中心/三分法/满屏）
- [ ] 运镜已选择（垂直/对角线/环绕）
- [ ] 人物在中心稳定区（x:0.25-0.75, y:0.25-0.65）
- [ ] 眼睛位置在画面上 1/3（y≈0.33）
- [ ] 提示词已生成（含 `--ar 9:16`）
- [ ] 竖屏关键词已添加（`vertical follow shot, 9:16 frame`）

### ✅ 进阶优化
- [ ] 使用浅景深（shallow depth of field）
- [ ] 使用手持晃动（handheld following）
- [ ] 使用动态构图（dynamic composition）
- [ ] 使用电影感运镜（cinematic）
- [ ] 使用情绪强化（emotional intensity）

---

## 总结

竖屏跟拍 = **横屏跟拍** + **9:16 构图适配** + **垂直运镜**

**核心差异**：
1. 人物在画面中心或上 1/3
2. 运镜以垂直/对角线为主
3. 眼睛位置在画面上 1/3
4. 提示词必须含 `--ar 9:16`
