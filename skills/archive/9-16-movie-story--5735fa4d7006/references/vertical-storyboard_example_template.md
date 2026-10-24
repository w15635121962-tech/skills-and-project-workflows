# 分镜示例模板（竖屏 9:16 版）

> **适用**：竖屏分镜脚本的示例模板  
> **核心**：9:16 画幅下的分镜模板、竖屏构图、手机端优化

---

## 分镜模板基础（竖屏版）

### 横屏 vs 竖屏分镜模板

| 维度 | 横屏 16:9 | 竖屏 9:16 |
|------|------------|------------|
| **画幅** | 16:9 或 2.39:1 | 9:16 |
| **构图** | 左右平衡 | 上下平衡 |
| **视线** | 水平（左←→右） | 垂直（上←→下）或对角线 |
| **提示词** | `--ar 16:9` 或 `--ar 2.39:1` | `--ar 9:16` |
| **剪辑节奏** | 2-4 秒/镜 | 1-3 秒/镜（快切） |

---

## 竖屏分镜模板

### 模板 1：对话镜（中景）
````markdown
## SHOT XXX

**场景**：{场景编号}（{场景名称}）
**时间**：{时间段}
**画幅**：9:16

**构图**：三分法（OC1）
**主体**：{角色 A}（中景）
**动作**：{动作描述}
**视线**：{视线方向}
**光影**：{光影方案}
**时长**：{时长}

**提示词**：
```
{Subject Description}, {Vertical Composition Keyword},
{Visual Anchors}, {Lighting}, {Texture},
--ar 9:16 --style raw --stylize 100 --v 6.0
--no deformed, bad anatomy, horizontal format
```

**空间坐标**：
- Camera Position (x, y): ({x}, {y})
- Subject Gaze (x, y): ({gx}, {gy})
- Master Axis (C1): [{x1}, {y1}] → [{x2}, {y2}]
- Coverage Type: {Master / OC1 / OC2 / OTS-A / OTS-B / Insert}
````

### 模板 2：情绪特写
````markdown
## SHOT XXX

**场景**：{场景编号}（{场景名称}）
**时间**：{时间段}
**画幅**：9:16

**构图**：中心构图（特写）
**主体**：{角色 A}（特写）
**动作**：{情绪动作描述}
**视线**：{视线方向}
**光影**：{光影方案}
**时长**：{时长}

**提示词**：
```
Extreme close-up of {Character}, {emotion}: {detailed emotion},
eyes at upper third, vertical framing, 9:16 frame,
{lighting}, {skin texture},
--ar 9:16 --style raw --stylize 150 --v 6.0
--no deformed, bad anatomy, horizontal format
```

**空间坐标**：
- Camera Position (x, y): ({x}, {y})
- Subject Gaze (x, y): ({gx}, {gy})
````

### 模板 3：动作镜（快切）
````markdown
## SHOT XXX

**场景**：{场景编号}（{场景名称}）
**时间**：{时间段}
**画幅**：9:16

**构图**：满屏构图（动作镜）
**主体**：{角色 A}（动作）
**动作**：{动作描述}
**视线**：{视线方向}
**光影**：{光影方案}
**时长**：{时长}

**提示词**：
```
{motion description}, {character} {action},
dynamic motion, motion blur,
vertical composition, 9:16 frame,
{lighting}, high shutter speed,
--ar 9:16 --style raw --stylize 200 --v 6.0
--no static, boring, horizontal format
```

**空间坐标**：
- Camera Position (x, y): ({x}, {y})
- Subject Gaze (x, y): ({gx}, {gy})
````

### 模板 4：定场镜（外景）
````markdown
## SHOT XXX

**场景**：{场景编号}（{场景名称}）
**时间**：{时间段}
**画幅**：9:16

**构图**：留白构图（定场镜）
**主体**：{环境}
**动作**：{环境动作描述}
**视线**：{视线方向}
**光影**：{光影方案}
**时长**：{时长}

**提示词**：
```
Establishing shot, {location},
exterior, {time of day}, {weather},
vertical composition, 9:16 frame,
wide shot, full location visible,
--ar 9:16 --style raw --stylize 50 --v 6.0
--no close-up, portrait, horizontal format
```

**空间坐标**：
- Camera Position (x, y): ({x}, {y})
- Subject Gaze (x, y): ({gx}, {gy})
````

---

## 竖屏分镜模板检查清单

### ✅ 必选要素
- [ ] 场景已标注（场景编号 + 场景名称）
- [ ] 时间已标注（时间段）
- [ ] 画幅已标注（9:16）
- [ ] 构图已选择（中心/三分法/满屏/留白）
- [ ] 主体已描述（角色/环境）
- [ ] 动作已描述（动作/情绪）
- [ ] 视线已标注（视线方向）
- [ ] 光影已选择（顶光/底光/侧光/顺光）
- [ ] 时长已标注（1-3 秒）
- [ ] 提示词已生成（含 `--ar 9:16`）
- [ ] 空间坐标已标注（Camera Position / Subject Gaze / Master Axis / Coverage Type）

### ✅ 进阶优化
- [ ] 使用竖屏构图关键词（`vertical composition, 9:16 frame`）
- [ ] 使用竖屏视觉锚点（六维精度）
- [ ] 使用竖屏光影方案（顶光/底光/侧光/顺光）
- [ ] 使用竖屏提示词模板（4 步黄金框架）
- [ ] 使用竖屏空间坐标系统（归一化坐标）

---

## 总结

竖屏分镜模板 = **横屏分镜模板** + **9:16 构图适配** + **竖屏提示词**

**核心差异**：
1. 画幅 9:16（而非 16:9 或 2.39:1）
2. 构图上下平衡（而非左右平衡）
3. 视线垂直或对角线（而非水平）
4. 提示词必须含 `--ar 9:16`
5. 剪辑节奏快切（1-3 秒/镜）
