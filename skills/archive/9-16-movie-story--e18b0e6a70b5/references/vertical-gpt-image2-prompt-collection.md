# GPT Image 2 提示词集（竖屏 9:16 版）

> **适用**：使用 GPT Image 2 生成竖屏分镜图像  
> **核心**：9:16 画幅下的 GPT Image 2 提示词、竖屏适配、手机端优化

---

## GPT Image 2 基础（竖屏版）

### 横屏 vs 竖屏 GPT Image 2

| 维度 | 横屏 16:9 | 竖屏 9:16 |
|------|------------|------------|
| **提示词格式** | 自然语言 | 自然语言（相同） |
| **画幅参数** | 无（默认 1:1） | `--ar 9:16`（需后期裁剪） |
| **构图** | 左右平衡 | 上下平衡 |
| **生成质量** | 高 | 高（相同） |
| **迭代速度** | 快 | 快（相同） |

**注意**：GPT Image 2 不支持 `--ar` 参数，需生成后裁剪为 9:16。

---

## 竖屏 GPT Image 2 提示词模板

### 模板 1：对话镜（中景）
```
Generate a vertical 9:16 cinematic shot of {description}.
Vertical composition, 9:16 frame.
{Character A} on the right side, looking left.
{Character B} on the left side, looking right.
{Eyes at upper third, rule of thirds vertical.}
{Lighting}: {lighting description}.
{Texture}: {texture description}.
{No horizontal format, no 16:9, no 4:3.}
```

### 模板 2：情绪特写
```
Generate a vertical 9:16 extreme close-up of {character}'s face.
{Eyes at upper third, vertical framing.}
{Emotion}: {detailed emotion description}.
{Lighting}: {lighting description}.
{Texture}: {skin texture visible, pores, natural skin imperfections.}
{No horizontal format, no 16:9.}
```

### 模板 3：动作镜（快切）
```
Generate a vertical 9:16 action shot of {character} {action}.
{Dynamic motion, motion blur.}
{Vertical composition, 9:16 frame.}
{Lighting}: {lighting description}.
{Texture}: {texture description.}
{No static, no boring, no horizontal format.}
```

### 模板 4：定场镜（外景）
```
Generate a vertical 9:16 establishing shot of {location}.
{Exterior, time of day, weather.}
{Vertical composition, 9:16 frame.}
{Wide shot, full location visible.}
{No close-up, no portrait, no horizontal format.}
```

---

## 竖屏 GPT Image 2 提示词生成流程

### 阶段 1：提示词编写
1. **主体描述**：`Generate a vertical 9:16 cinematic shot of {description}.`
2. **构图关键词**：`Vertical composition, 9:16 frame.`
3. **视线方向**：`{Character A} on the right side, looking left.`
4. **光影方案**：`{Lighting}: {lighting description}.`
5. **质感层**：`{Texture}: {texture description.}`

### 阶段 2：图像生成
1. **输入提示词**：将上述提示词输入 GPT Image 2
2. **生成图像**：等待生成结果（约 10-30 秒）
3. **评估质量**：检查构图/光影/质感/一致性

### 阶段 3：后期裁剪
1. **裁剪为 9:16**：使用 Photoshop/CapCut 裁剪为 9:16
2. **调整构图**：确保眼睛在画面上 1/3
3. **导出图像**：导出为 PNG/JPG（1080x1920）

---

## 竖屏 GPT Image 2 提示词检查清单

### ✅ 必选要素
- [ ] 提示词已编写（自然语言）
- [ ] 构图关键词已添加（`Vertical composition, 9:16 frame.`）
- [ ] 视线方向已描述（`on the right side, looking left.`）
- [ ] 光影方案已描述（`{Lighting}: {description}.`）
- [ ] 质感层已描述（`{Texture}: {description}.`）
- [ ] 负面提示词已添加（`No horizontal format, no 16:9.`）
- [ ] 图像已生成（GPT Image 2）
- [ ] 图像已裁剪（9:16）

### ✅ 进阶优化
- [ ] 使用竖屏构图关键词（`eyes at upper third, rule of thirds vertical.`）
- [ ] 使用竖屏视觉锚点（六维精度）
- [ ] 使用竖屏光影方案（顶光/底光/侧光/顺光）
- [ ] 使用竖屏质感层（`skin texture visible, pores.`）
- [ ] 使用后期裁剪（Photoshop/CapCut）

---

## 总结

竖屏 GPT Image 2 提示词 = **横屏 GPT Image 2 提示词** + **竖屏构图适配** + **后期裁剪**

**核心差异**：
1. 提示词加 `vertical 9:16` 关键词
2. 构图上下平衡（而非左右平衡）
3. 视线垂直或对角线（而非水平）
5. 生成后需裁剪为 9:16（GPT Image 2 不支持 `--ar` 参数）
