# 运镜指南（竖屏 9:16 版）

> **适用**：竖屏影视项目的运镜设计  
> **核心**：9:16 画幅下的运镜语言、竖屏适配、手机端优化

---

## 运镜基础（竖屏版）

### 横屏 vs 竖屏运镜

| 维度 | 横屏 16:9 | 竖屏 9:16 |
|------|------------|------------|
| **推 (Push-in)** | 水平推入 | 垂直推入（从脚到头）或中心推入 |
| **拉 (Pull-out)** | 水平拉出 | 垂直拉出（从头到脚）或全景拉出 |
| **摇 (Pan)** | 左右摇 | 上下摇（而非左右） |
| **俯仰 (Tilt)** | 上下摇 | 上下摇（强调权力关系） |
| **手持 (Handheld)** | 模拟真实 | 模拟手机拍摄 |
| **定镜 (Static)** | 少用 | 更少用（避免无聊） |

---

## 竖屏运镜详解

### 1. 推 (Push-in)
```
Push-in (Vertical Adaptation):
- 缓慢推入，强调情绪
- 速度：慢（2-3 秒）
- 方向：垂直推入（从脚到头）或中心推入
- 电影感：浅景深，背景虚化
```

**提示词关键词**：
```
slow push-in, vertical push-in, cinematic push-in,
shallow depth of field, bokeh background,
emotional impact, intense
```

### 2. 拉 (Pull-out)
```
Pull-out (Vertical Adaptation):
- 拉出全景，展示环境
- 速度：中（1-2 秒）
- 方向：垂直拉出（从头到脚）或全景拉出
- 电影感：深景深，环境清晰
```

**提示词关键词**：
```
slow pull-out, vertical pull-out, cinematic pull-out,
deep depth of field, full environment visible,
establishing shot, wide shot
```

### 3. 摇 (Pan → Tilt)
```
Tilt (Vertical Adaptation):
- 上下摇摄，强调情绪或权力关系
- 速度：慢（1-2 秒）
- 方向：从下往上（权力）/ 从上往下（脆弱）
- 电影感：动态构图，情绪变化
```

**提示词关键词**：
```
vertical tilt, tilt up, tilt down,
low angle, high angle,
power dynamics, emotional shift
```

### 4. 手持 (Handheld)
```
Handheld (Vertical Adaptation):
- 模拟手机拍摄
- 速度：快（0.5-1 秒）
- 方向：随机晃动
- 电影感：沉浸式，真实感
```

**提示词关键词**：
```
handheld camera, shaky camera,
realistic, immersive,
vertical cinematography, smartphone footage
```

---

## 竖屏运镜提示词模板

### 模板 1：推 (Push-in)
```
{s ubject}, slow push-in,
vertical push-in, cinematic,
shallow depth of field, bokeh background,
--ar 9:16 --style raw --stylize 150
```

### 模板 2：拉 (Pull-out)
```
{s ubject}, slow pull-out,
vertical pull-out, cinematic,
deep depth of field, wide shot,
--ar 9:16 --style raw --stylize 100
```

### 模板 3：俯仰 (Tilt)
```
{s ubject}, vertical tilt,
tilt up/down, cinematic,
power dynamics/emotional shift,
--ar 9:16 --style raw --stylize 120
```

### 模板 4：手持 (Handheld)
```
{s ubject}, handheld camera,
shaky camera, realistic,
vertical cinematography, immersive,
--ar 9:16 --style raw --stylize 200
```

---

## 竖屏运镜检查清单

### ✅ 必选要素
- [ ] 运镜类型已选择（推/拉/摇/手持）
- [ ] 运镜方向已定义（垂直/中心/上下）
- [ ] 运镜速度已定义（慢/中/快）
- [ ] 竖屏关键词已添加（`vertical cinematography, 9:16 frame`）
- [ ] 提示词已生成（含 `--ar 9:16`）
- [ ] 电影感关键词已添加（`cinematic, shallow depth of field`）

### ✅ 进阶优化
- [ ] 使用浅景深（shallow depth of field）
- [ ] 使用深景深（deep depth of field）
- [ ] 使用电影感运镜（cinematic push-in/pull-out/tilt）
- [ ] 使用手持晃动（handheld camera, shaky camera）
- [ ] 使用情绪强化（emotional impact, power dynamics）

---

## 总结

竖屏运镜 = **横屏运镜** + **9:16 画幅适配** + **垂直运动**

**核心差异**：
1. 推拉方向：垂直（而非水平）
2. 摇摄方向：上下（而非左右）
3. 手持：模拟手机拍摄
4. 提示词必须含 `--ar 9:16`
