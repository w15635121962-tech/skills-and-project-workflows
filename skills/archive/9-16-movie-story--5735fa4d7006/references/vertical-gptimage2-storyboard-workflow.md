# GPT Image 2 分镜工作流（竖屏 9:16 版）

> **适用**：使用 GPT Image 2 生成竖屏分镜图像的工作流  
> **核心**：9:16 画幅下的 GPT Image 2 工作流、竖屏适配、手机端优化

---

## GPT Image 2 分镜工作流基础（竖屏版）

### 横屏 vs 竖屏 GPT Image 2 分镜工作流

| 维度 | 横屏 16:9 | 竖屏 9:16 |
|------|------------|------------|
| **提示词格式** | 自然语言 | 自然语言（相同） |
| **画幅参数** | 无（默认 1:1） | 后期裁剪为 9:16 |
| **构图** | 左右平衡 | 上下平衡 |
| **生成质量** | 高 | 高（相同） |
| **迭代速度** | 快 | 快（相同） |

---

## 竖屏 GPT Image 2 分镜工作流

### 阶段 1：分镜设计
1. **使用 `9-16-movie-story` 技能生成竖屏分镜**
2. **确定镜头列表**：镜头号/场景/构图/主体/动作/视线/光影/时长
3. **编写提示词**：每个镜头编写完整 GPT Image 2 提示词

### 阶段 2：提示词生成
1. **主体描述**：`Generate a vertical 9:16 cinematic shot of {description}.`
2. **构图关键词**：`Vertical composition, 9:16 frame.`
3. **视线方向**：`{Character A} on the right side, looking left.`
4. **光影方案**：`{Lighting}: {lighting description}.`
5. **质感层**：`{Texture}: {texture description.}`

### 阶段 3：图像生成
1. **输入提示词**：将上述提示词输入 GPT Image 2
2. **生成图像**：等待生成结果（约 10-30 秒）
3. **评估质量**：检查构图/光影/质感/一致性
4. **迭代提示词**：根据生成结果迭代提示词

### 阶段 4：后期裁剪
1. **裁剪为 9:16**：使用 Photoshop/CapCut 裁剪为 9:16
2. **调整构图**：确保眼睛在画面上 1/3
3. **导出图像**：导出为 PNG/JPG（1080x1920）

### 阶段 5：分镜合成
1. **导入分镜软件**：将裁剪后的图像导入分镜软件（Studio Binder / Shot Designer）
2. **添加时间码**：添加时间码（HH:MM:SS:FF）
3. **添加提示词**：添加提示词（复制粘贴）
4. **导出分镜脚本**：导出为 PDF/HTML/Markdown

---

## 竖屏 GPT Image 2 分镜工作流示例

### 示例：《大唐文圣》EP01 SHOT 001

**阶段 1：分镜设计**
```
镜头号：SHOT 001
场景：S1-1（周王府偏殿·暴雨夜）
构图：中心构图（特写）
主体：王勃（特写）
动作：暴雨中抬头，瞳孔电光炸亮，决绝
视线：直视镜头（观众）
光影：烛火侧光，画面左暗右亮，ratio 1:4
时长：2.0 秒
```

**阶段 2：提示词生成**
```
Generate a vertical 9:16 extreme close-up of young man, early 20s.
Wearing dark blue round-collar robe, golden peony embroidery at collar.
Eyes at upper third, vertical framing, 9:16 frame.
Lighting: candlelight, chiaroscuro, right side lighting.
Texture: skin texture visible, pores, natural skin imperfections.
No horizontal format, no 16:9, no 4:3.
```

**阶段 3：图像生成**
- 输入提示词到 GPT Image 2
- 生成图像（约 10-30 秒）
- 评估质量（构图/光影/质感/一致性）
- 迭代提示词（如需）

**阶段 4：后期裁剪**
- 使用 Photoshop/CapCut 裁剪为 9:16
- 调整构图（确保眼睛在画面上 1/3）
- 导出图像（PNG/JPG，1080x1920）

**阶段 5：分镜合成**
- 导入分镜软件（Studio Binder / Shot Designer）
- 添加时间码（`00:00:00:00 - 00:00:02:00`）
- 添加提示词（复制粘贴）
- 导出分镜脚本（PDF/HTML/Markdown）

---

## 竖屏 GPT Image 2 分镜工作流检查清单

### ✅ 必选要素
- [ ] 分镜已设计（使用 `9-16-movie-story` 技能）
- [ ] 提示词已生成（含 `vertical 9:16` 关键词）
- [ ] 图像已生成（GPT Image 2）
- [ ] 图像已裁剪（9:16）
- [ ] 分镜已合成（Studio Binder / Shot Designer）
- [ ] 时间码已添加（`HH:MM:SS:FF`）
- [ ] 提示词已添加（复制粘贴）

### ✅ 进阶优化
- [ ] 使用竖屏构图关键词（`eyes at upper third, rule of thirds vertical.`）
- [ ] 使用竖屏视觉锚点（六维精度）
- [ ] 使用竖屏光影方案（顶光/底光/侧光/顺光）
- [ ] 使用竖屏质感层（`skin texture visible, pores.`）
- [ ] 使用后期裁剪（Photoshop/CapCut）

---

## 总结

竖屏 GPT Image 2 分镜工作流 = **横屏 GPT Image 2 分镜工作流** + **竖屏构图适配** + **后期裁剪**

**核心差异**：
1. 提示词加 `vertical 9:16` 关键词
2. 构图上下平衡（而非左右平衡）
3. 视线垂直或对角线（而非水平）
4. 生成后需裁剪为 9:16（GPT Image 2 不支持 `--ar` 参数）
5. 分镜合成需添加时间码和提示词
