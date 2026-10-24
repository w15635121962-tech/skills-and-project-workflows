# 分镜规范（竖屏 9:16 版）

> **适用**：竖屏分镜脚本的绘制规范  
> **核心**：9:16 画幅下的分镜绘制、竖屏适配、手机端优化

---

## 分镜规范基础（竖屏版）

### 横屏 vs 竖屏分镜规范

| 维度 | 横屏 16:9 | 竖屏 9:16 |
|------|------------|------------|
| **画幅** | 16:9 或 2.39:1 | 9:16 |
| **构图** | 左右平衡 | 上下平衡 |
| **视线** | 水平（左←→右） | 垂直（上←→下）或对角线 |
| **运镜** | 左右摇/推拉 | 上下摇/推拉 |
| **字幕** | 底部 10% | 底部 20% |
| **提示词** | `--ar 16:9` | `--ar 9:16` |

---

## 竖屏分镜规范（7 要素）

### 要素 1：镜头编号（Shot Number）
```
格式：SHOT XXX（XXX = 3 位数，从 001 开始）
示例：SHOT 001, SHOT 002, SHOT 003...
```

### 要素 2：场景描述（Scene Description）
```
格式：场景编号（场景名称）| 时间段 | 天气
示例：S1-1（周王府偏殿·暴雨夜）| 夜晚 | 暴雨
```

### 要素 3：构图类型（Framing Type）
```
中心构图：centered composition, vertical frame
三分法：rule of thirds, eyes at upper third
满屏构图：full-frame vertical, fills screen
留白构图：negative space, vertical framing
```

### 要素 4：主体描述（Subject Description）
```
角色：{角色名称}，{年龄}，{服装}，{发型}，{配饰}
环境：{场景名称}，{时间段}，{天气}
```

### 要素 5：动作描述（Action Description）
```
动作：{主体} {动作} {方向} {速度}
示例：王勃将帛书掷向陆雪，眼神决绝
```

### 要素 6：光影方案（Lighting Scheme）
```
顶光：top lighting, hard shadows, chiaroscuro
底光：bottom lighting, upward shadows, mysterious
侧光：side lighting, Rembrandt lighting, chiaroscuro
顺光：front lighting, even illumination, soft lighting
```

### 要素 7：AI 提示词（AI Prompt）
```
格式：
{主体描述} + {竖屏构图关键词} +
{视觉锚点} + {光影方案} +
{质感层} + {技术参数} +
{负面提示词}

技术参数：--ar 9:16 --style raw --stylize 100 --v 6.0
负面提示词：--no deformed, bad anatomy, horizontal format
```

---

## 竖屏分镜脚本模板

### 模板 1：对话镜（中景）
````markdown
## SHOT XXX

**场景**：S1-X（场景名称）| 时间段 | 天气
**构图**：三分法（OC1）
**主体**：{角色 A}（中景）
**动作**：{动作描述}
**视线**：{视线方向}
**光影**：{光影方案}
**时长**：{时长} 秒

**提示词**：
```
{Subject Description}, {Vertical Composition Keyword},
{Visual Anchors}, {Lighting Scheme},
{Texture Layer}, --ar 9:16 --style raw --stylize 100 --v 6.0,
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

**场景**：S1-X（场景名称）| 时间段 | 天气
**构图**：中心构图（特写）
**主体**：{角色 A}（特写）
**动作**：{情绪动作描述}
**视线**：{视线方向}
**光影**：{光影方案}
**时长**：{时长} 秒

**提示词**：
```
Extreme close-up of {Character}, {Emotion}: {Detailed Emotion},
eyes at upper third, vertical framing, 9:16 frame,
{Lighting Scheme}, {Texture Layer},
--ar 9:16 --style raw --stylize 200 --v 6.0,
--no deformed, bad anatomy, horizontal format
```

**空间坐标**：
- Camera Position (x, y): ({x}, {y})
- Subject Gaze (x, y): ({gx}, {gy})
````

### 模板 3：动作镜（快切）
````markdown
## SHOT XXX

**场景**：S1-X（场景名称）| 时间段 | 天气
**构图**：满屏构图（动作镜）
**主体**：{角色 A}（动作）
**动作**：{动作描述}
**视线**：{视线方向}
**光影**：{光影方案}
**时长**：{时长} 秒

**提示词**：
```
{Motion Description}, {Character} {Action},
dynamic motion, motion blur,
vertical composition, 9:16 frame,
{Lighting Scheme}, high shutter speed,
--ar 9:16 --style raw --stylize 200 --v 6.0,
--no static, boring, horizontal format
```

**空间坐标**：
- Camera Position (x, y): ({x}, {y})
- Subject Gaze (x, y): ({gx}, {gy})
````

### 模板 4：定场镜（外景）
````markdown
## SHOT XXX

**场景**：S1-X（场景名称）| 时间段 | {天气}
**构图**：留白构图（定场镜）
**主体**：{环境}
**动作**：{环境动作描述}
**视线**：{视线方向}
**光影**：{光影方案}
**时长**：{时长} 秒

**提示词**：
```
Establishing shot, {Location},
exterior, {Time of Day}, {Weather},
vertical composition, 9:16 frame,
wide shot, full location visible,
--ar 9:16 --style raw --stylize 50 --v 6.0,
--no close-up, portrait, horizontal format
```

**空间坐标**：
- Camera Position (x, y): ({x}, {y})
- Subject Gaze (x, y): ({gx}, {gy})
````

---

## 竖屏分镜规范检查清单

### ✅ 必选要素
- [ ] 镜头编号已标注（SHOT XXX）
- [ ] 场景描述已标注（场景编号 + 场景名称 + 时间段 + 天气）
- [ ] 构图类型已选择（中心/三分法/满屏/留白）
- [ ] 主体描述已完成（角色/环境）
- [ ] 动作描述已完成（动作/方向/速度）
- [ ] 光影方案已选择（顶光/底光/侧光/顺光）
- [ ] AI 提示词已生成（含 `--ar 9:16`）

### ✅ 进阶优化
- [ ] 空间坐标已标注（Camera Position / Subject Gaze / Master Axis / Coverage Type）
- [ ] 竖屏关键词已添加（`vertical composition, 9:16 frame`）
- [ ] 眼睛位置在画面上 1/3（y≈0.33）
- [ ] 人脸在中心稳定区（x:0.25-0.75, y:0.25-0.65）
- [ ] 负面提示词已添加（`--no deformed, bad anatomy, horizontal format`）

---

## 总结

竖屏分镜规范 = **横屏分镜规范** + **9:16 画幅适配** + **手机端优化**

**核心差异**：
1. 画幅 9:16（而非 16:9 或 2.39:1）
2. 构图：上下平衡（而非左右平衡）
3. 视线：垂直或对角线（而非水平）
4. 运镜：上下摇或推拉（而非左右摇）
5. 字幕：底部 20%（而非底部 10%）
6. 提示词必须含 `--ar 9:16`
