# Grok Imagine 元提示框架（竖屏 9:16 版）

> **适用**：使用 Grok Imagine 生成竖屏分镜图像的元提示框架  
> **核心**：9:16 画幅下的 Grok Imagine 元提示、竖屏适配、手机端优化

---

## Grok Imagine 元提示基础（竖屏版）

### 横屏 vs 竖屏 Grok Imagine 元提示

| 维度 | 横屏 16:9 | 竖屏 9:16 |
|------|------------|------------|
| **提示词格式** | 自然语言 + 参数 | 自然语言 + 参数（相同） |
| **画幅参数** | `--ar 16:9` 或 `--ar 2.39:1` | `--ar 9:16` |
| **构图** | 左右平衡 | 上下平衡 |
| **生成质量** | 高 | 高（相同） |
| **迭代速度** | 快 | 快（相同） |

---

## 竖屏 Grok Imagine 元提示框架

### 元提示结构
```
{ROLE}: {Your role description.}
{TASK}: {Your task description.}
{CONTEXT}: {Your context description.}
{CONSTRAINTS}: {Your constraints description.}
{EXAMPLE}: {Your example description.}
```

### 竖屏元提示模板
```
{ROLE}: You are a professional cinematic storyboard artist specializing in vertical 9:16 format.
{TASK}: Generate a vertical 9:16 cinematic storyboard shot based on the given description.
{CONTEXT}: The storyboard is for a vertical short drama (9:16) targeting mobile viewers.
{CONSTRAINTS}: 
- Aspect ratio MUST be 9:16 (vertical full screen).
- Composition MUST be vertical (eyes at upper third, rule of thirds vertical).
- Face MUST be in center stable zone (x:0.25-0.75, y:0.25-0.65).
- Prompt MUST include `--ar 9:16`.
{EXAMPLE}: 
Input: "Close-up of young man, angry expression."
Output: "Close-up of young man, early 20s, angry expression, veins bulging, top lighting, hard shadows, chiaroscuro, vertical composition, eyes at upper third, 9:16 frame, --ar 9:16 --style raw --stylize 150 --v 6.0"
```

---

## 竖屏 Grok Imagine 元提示生成流程

### 阶段 1：元提示编写
1. **ROLE**：`You are a professional cinematic storyboard artist specializing in vertical 9:16 format.`
2. **TASK**：`Generate a vertical 9:16 cinematic storyboard shot based on the given description.`
3. **CONTEXT**：`The storyboard is for a vertical short drama (9:16) targeting mobile viewers.`
4. **CONSTRAINTS**：`Aspect ratio MUST be 9:16. Composition MUST be vertical. Face MUST be in center stable zone. Prompt MUST include --ar 9:16.`
5. **EXAMPLE**：提供一个完整示例（Input → Output）

### 阶段 2：元提示输入
1. **输入元提示**：将上述元提示输入 Grok Imagine
2. **输入分镜描述**：输入分镜描述（如 "Close-up of young man, angry expression."）
3. **生成提示词**：Grok Imagine 生成完整提示词

### 阶段 3：提示词评估
1. **检查画幅**：提示词是否含 `--ar 9:16`？
2. **检查构图**：提示词是否含 `vertical composition, 9:16 frame`？
3. **检查人脸位置**：提示词是否含 `eyes at upper third`？
4. **检查负面词**：提示词是否含 `--no horizontal format`？

### 阶段 4：提示词迭代
1. **迭代元提示**：根据生成结果迭代元提示
2. **迭代分镜描述**：根据生成结果迭代分镜描述
3. **重新生成**：重新生成提示词

---

## 竖屏 Grok Imagine 元提示检查清单

### ✅ 必选要素
- [ ] 元提示已编写（ROLE / TASK / CONTEXT / CONSTRAINTS / EXAMPLE）
- [ ] 元提示已输入（Grok Imagine）
- [ ] 分镜描述已输入（如 "Close-up of young man, angry expression."）
- [ ] 提示词已生成（Grok Imagine）
- [ ] 提示词已评估（画幅/构图/人脸位置/负面词）
- [ ] 提示词已迭代（如需）

### ✅ 进阶优化
- [ ] 使用竖屏构图关键词（`eyes at upper third, rule of thirds vertical.`）
- [ ] 使用竖屏视觉锚点（六维精度）
- [ ] 使用竖屏光影方案（顶光/底光/侧光/顺光）
- [ ] 使用竖屏质感层（`skin texture visible, pores.`）
- [ ] 使用元提示框架（ROLE / TASK / CONTEXT / CONSTRAINTS / EXAMPLE）

---

## 总结

竖屏 Grok Imagine 元提示框架 = **横屏 Grok Imagine 元提示框架** + **竖屏构图适配** + **元提示工程**

**核心差异**：
1. ROLE 加 `specializing in vertical 9:16 format`
2. TASK 加 `Generate a vertical 9:16 cinematic storyboard shot`
3. CONSTRAINS 加 `Aspect ratio MUST be 9:16. Composition MUST be vertical.`
4. EXAMPLE 加 `Output: "... --ar 9:16 ..."`
5. 生成的提示词必须含 `--ar 9:16`
