# AIGC 结构化提示词（竖屏 9:16 版）

> **适用**：竖屏影视项目的 AIGC 结构化提示词设计  
> **核心**：9:16 画幅下的结构化提示词、竖屏适配、手机端优化

---

## 结构化提示词基础（竖屏版）

### 横屏 vs 竖屏结构化提示词

| 维度 | 横屏 16:9 | 竖屏 9:16 |
|------|------------|------------|
| **结构** | 4 步（主体+锚点+技术+质感） | 4 步（相同，但竖屏适配） |
| **构图关键词** | 左右构图 | 上下构图 |
| **技术参数** | `--ar 16:9` 或 `--ar 2.39:1` | `--ar 9:16` |
| **负面提示词** | 横屏专属 | 竖屏专属 |

---

## 竖屏结构化提示词（4 步黄金框架）

### 第一步：主体描述（Subject）
```
{Screenwriter's Description} + {Vertical Composition Keyword}
```

**竖屏构图关键词库**：
| 构图类型 | 关键词 | 适用场景 |
|---------|--------|---------|
| 中心构图 | `centered composition, vertical frame, subject fills screen` | 人物特写、情感戏 |
| 三分法 | `rule of thirds, eyes at upper third, vertical composition` | 对话、单人镜头 |
| 满屏构图 | `full-body portrait, 9:16 frame, standing vertically` | 全身镜头 |
| 极端特写 | `extreme close-up, top of frame, vertical cinematography` | 情绪爆发 |
| 低头视角 | `low angle, looking up, vertical framing` | 权力感、仰视 |
| 俯拍 | `high angle, looking down, mobile vertical shot` | 脆弱感、俯视 |

### 第二步：视觉锚点（Visual Anchors）
```
{Character Visual Bible Keywords} + {Costume/Props} + {Lighting}
```

**竖屏视觉锚点注意事项**：
- 人脸必须在 **中心稳定区**（x:0.25-0.75, y:0.25-0.65）
- 眼睛位置在 **画面上 1/3 处**
- 头顶留 **15% 呼吸空间**
- 下巴到画面底部留 **20% 空间**

### 第三步：技术参数（Technical Specs）
```
--ar 9:16 --style raw --v 6.0 --stylize 50
```

**竖屏专属参数**：
| 参数 | 值 | 说明 |
|------|-----|------|
| `--ar` | `9:16` | 竖屏画幅 |
| `--style` | `raw` | 减少 AI 美化，保留真实感 |
| `--stylize` | `50-250` | 竖屏建议 50-150（避免过度艺术化）|
| `--weird` | `0-100` | 竖屏慎用，容易破坏构图 |
| `--tile` | - | 竖屏不适用 |

### 第四步：质感层（Photorealism Layer）
```
{Texture} + {Lighting} + {Camera}
```

**竖屏质感层关键词**：
| 类别 | 竖屏适配关键词 |
|------|----------------|
| 纹理 | `skin texture visible, pores, natural skin imperfections, 9:16 close-up` |
| 光影 | `soft top lighting, vertical frame lighting, shallow depth of field, bokeh background` |
| 镜头 | `85mm portrait lens, f/1.8, mobile vertical cinematography, smartphone footage aesthetic` |
| 胶片 | `film grain, 35mm film, Kodak Vision3, vertical film scan, mobile film aesthetic` |

---

## 竖屏结构化提示词模板

### 模板 1：对话镜（中景）
```
Medium shot, two people facing each other,
{Character A description}, {Character B description},
vertical composition, 9:16 frame,
{dialogue emotion}, {lighting},
--ar 9:16 --style raw --stylize 100
```

### 模板 2：情绪特写
```
Extreme close-up, {character's face},
{emotion}: {detailed emotion description},
eyes at upper third, vertical framing,
{lighting}, {skin texture},
--ar 9:16 --style raw --stylize 150
```

### 模板 3：动作镜（快切）
```
{motion description}, {character} {action},
dynamic motion, motion blur,
vertical composition, 9:16 frame,
{lighting}, high shutter speed,
--ar 9:16 --style raw --stylize 200
```

### 模板 4：定场镜（外景）
```
Establishing shot, {location},
exterior, {time of day}, {weather},
vertical composition, 9:16 frame,
wide shot, full location visible,
--ar 9:16 --style raw --stylize 50
```

---

## 竖屏结构化提示词检查清单

### ✅ 必选要素
- [ ] `--ar 9:16` 参数已添加
- [ ] 主体描述包含竖屏构图关键词
- [ ] 人脸在中心稳定区（x:0.25-0.75, y:0.25-0.65）
- [ ] 眼睛位置在画面上 1/3 处
- [ ] 负面提示词包含竖屏专属负面词
- [ ] 质感层包含竖屏适配关键词

### ✅ 平台适配
- [ ] Midjourney：`--style raw --v 6.0`
- [ ] Seedance：中文主体描述 + `--ar 9:16`
- [ ] Kling：详细动作描述 + `--ar 9:16`
- [ ] Runway：简洁提示词 + 垂直构图关键词
- [ ] Pika：`cinematic, photorealistic` + `vertical 9:16`

### ✅ 视觉一致性
- [ ] 角色视觉锚点关键词已添加（六维精度）
- [ ] 场景视觉锚点关键词已添加
- [ ] 服装/道具锚点已添加
- [ ] 光影情绪关键词已添加

---

## 总结

竖屏结构化提示词 = **横屏结构化提示词** + **竖屏构图适配** + **9:16 技术参数**

**核心差异**：
1. 必须加 `--ar 9:16`
2. 主体描述加竖屏构图关键词
3. 人脸位置在画面上 1/3
4. 负面提示词加竖屏专属负面词
5. 质感层加 `vertical cinematography` 等关键词
