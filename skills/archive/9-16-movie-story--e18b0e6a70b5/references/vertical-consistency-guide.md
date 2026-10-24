# 视觉一致性参考（竖屏 9:16 版）

> **适用**：竖屏影视项目的视觉一致性设计  
> **核心**：9:16 画幅下的视觉一致性、竖屏适配、手机端优化

---

## 视觉一致性基础（竖屏版）

### 横屏 vs 竖屏视觉一致性

| 维度 | 横屏 16:9 | 竖屏 9:16 |
|------|------------|------------|
| **角色一致性** | 六维精度 | 六维精度（相同） |
| **场景一致性** | 完整锚点 | 完整锚点（相同） |
| **色彩一致性** | 色彩系统 | 色彩系统（相同） |
| **光影一致性** | 光影方案 | 光影方案（相同） |
| **构图一致性** | 横屏构图 | 竖屏构图（中心/三分法/满屏） |
| **提示词一致性** | `--ar 16:9` | `--ar 9:16` |

---

## 竖屏视觉一致性检查清单

### ✅ 角色一致性（六维精度）
- [ ] 面容一致（正面/2/3 侧面，眼睛在画面上 1/3）
- [ ] 发型一致（头顶+发髻，头顶留 15% 呼吸空间）
- [ ] 服装一致（全身/细节，服装占满画面）
- [ ] 配饰一致（特写+全景，配饰在中心稳定区）
- [ ] 姿态一致（全身上下满屏，姿态在画面中心）
- [ ] 光影一致（单光源，垂直方向）

### ✅ 场景一致性（7 要素）
- [ ] 场景名称一致
- [ ] 时间段一致
- [ ] 天气一致
- [ ] 光源类型一致
- [ ] 色彩方案一致
- [ ] 构图方案一致
- [ ] 运镜方案一致

### ✅ 色彩一致性（三阶段色彩演变）
- [ ] 冷色调阶段（<20% 进度）：冷蓝灰 (#2A3B4A)
- [ ] 暖色调阶段（30-40% 进度）：金琥珀 (#C8A03C)
- [ ] 对比色调阶段（>60% 进度）：金 (#C8A03C) + 蓝 (#2A3B4A)

### ✅ 光影一致性（单光源）
- [ ] 顶光一致（top lighting, hard shadows）
- [ ] 底光一致（bottom lighting, upward shadows）
- [ ] 侧光一致（side lighting, Rembrandt lighting）
- [ ] 顺光一致（front lighting, even illumination）

### ✅ 构图一致性（竖屏构图）
- [ ] 中心构图一致（centered composition, eyes at upper third）
- [ ] 三分法一致（rule of thirds, eyes at upper third）
- [ ] 满屏构图一致（full-frame vertical, fills screen）
- [ ] 留白构图一致（negative space, vertical framing）

### ✅ 提示词一致性（竖屏适配）
- [ ] `--ar 9:16` 已添加
- [ ] 竖屏构图关键词已添加（`vertical composition, 9:16 frame`）
- [ ] 眼睛位置在画面上 1/3（y≈0.33）
- [ ] 人脸在中心稳定区（x:0.25-0.75, y:0.25-0.65）
- [ ] 负面提示词已添加（`--no deformed, bad anatomy, horizontal format`）

---

## 竖屏视觉一致性提示词模板

### 模板 1：角色一致性（特写）
```
Close-up of {Character},
{Facial Features}, eyes at upper third, ALWAYS,
{Hairstyle}, head room 15%, ALWAYS,
{Costume}, {Accessories}, ALWAYS,
{Posture}, {Lighting}, ALWAYS,
vertical composition, 9:16 frame, ALWAYS,
--ar 9:16 --style raw --stylize 150 --v 6.0,
--no deformed, bad anatomy, inconsistent
```

### 模板 2：场景一致性（定场）
```
Establishing shot, {Location},
{Time of Day}, ALWAYS,
{Weather}, ALWAYS,
{Light Source Type}, ALWAYS,
{Color Scheme}, ALWAYS,
{Composition Scheme}, ALWAYS,
{Camera Movement}, ALWAYS,
vertical composition, 9:16 frame, ALWAYS,
--ar 9:16 --style raw --stylize 50 --v 6.0,
--no inconsistent lighting, inconsistent color
```

### 模板 3：色彩一致性（三阶段）
```
{Character} in {Location},
{Color Scheme}: {Cool Tone / Warm Tone / Contrast Tone},
ALWAYS use {Primary Color} + {Secondary Color} + {Accent Color},
vertical composition, 9:16 frame,
--ar 9:16 --style raw --stylize 100 --v 6.0,
--no inconsistent color, wrong color palette
```

### 模板 4：光影一致性（单光源）
```
{Close-up / Medium / Wide} of {Character},
{Lighting Scheme}: {Top / Bottom / Side / Front},
ALWAYS use single light source,
vertical composition, 9:16 frame,
--ar 9:16 --style raw --stylize 150 --v 6.0,
--no inconsistent lighting, multiple light sources
```

---

## 竖屏视觉一致性常见错误

### ❌ 错误 1：角色面容不一致
**后果**：AI 生成不同角度的面容，角色"变脸"。  
**解决**：在提示词中固定面容描述（正面/2/3 侧面），并添加 `ALWAYS`。

### ❌ 错误 2：角色服装不一致
**后果**：AI 生成不同服装，角色"换装"。  
**解决**：在提示词中固定服装描述（深蓝圆领袍，领口金色牡丹刺绣），并添加 `ALWAYS`。

### ❌ 错误 3：场景光源不一致
**后果**：AI 生成不同光影，场景"跳光"。  
**解决**：在提示词中固定光源类型（烛光，单光源，画面右侧），并添加 `ALWAYS`。

### ❌ 错误 4：色彩方案不一致
**后果**：AI 生成不同色彩，场景"变色"。  
**解决**：在提示词中固定色彩方案（冷蓝灰 + 深红/黑 + 烛火黄），并添加 `ALWAYS`。

### ❌ 错误 5：构图不一致
**后果**：AI 生成不同构图，镜头"跳构"。  
**解决**：在提示词中固定构图方案（三分法，眼睛在上横线），并添加 `ALWAYS`。

---

## 总结

竖屏视觉一致性 = **横屏视觉一致性** + **9:16 画幅适配** + **手机端优化**

**核心要点**：
1. 角色一致性：六维精度（面容/发型/服装/配饰/姿态/光影）
2. 场景一致性：7 要素（名称/时间段/天气/光源/色彩/构图/运镜）
3. 色彩一致性：三阶段色彩演变（冷→暖→对比）
4. 光影一致性：单光源（顶/底/侧/顺）
5. 构图一致性：竖屏构图（中心/三分法/满屏/留白）
6. 提示词一致性：含 `--ar 9:16` + `ALWAYS`
