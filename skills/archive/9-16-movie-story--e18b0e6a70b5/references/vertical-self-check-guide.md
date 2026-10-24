# 竖屏自检优化指南

> 本文档配合 movie-story 模块9（质量自检体系）使用，针对9:16竖屏画幅重构所有检查项。

---

## 一、竖屏六轮自检协议

| 轮次 | 检查内容 | 通过标准 | 竖屏特化 |
|------|----------|----------|------------|
| 1 | 剧本覆盖度 | 100%覆盖，无遗漏 | 竖屏节奏适配检查 |
| 2 | 竖屏构图 | 所有人脸在中心区，眼睛在上1/3 | **竖屏核心检查** |
| 3 | 镜头语法 | 所有镜头遵守竖屏铁律 | 垂直运镜/快切节奏 |
| 4 | AI提示词质量 | 每个提示词含 --ar 9:16 | 竖屏构图关键词 |
| 5 | 竖屏覆盖规划 | Vertical Coverage Strategy完整 | 垂直层次覆盖 |
| 6 | 整体验收 | 竖屏观看体验优良 | 手机端可读性 |

---

## 二、逐轮自检详解

### 第一轮：剧本覆盖度（同横屏）

**检查项**：
- [ ] 逐行逐场景对照原始剧本
- [ ] 每句对白、每个动作、每个场景段落100%覆盖
- [ ] 无总结、无浓缩、无省略

**竖屏增强检查**：
- [ ] 场景是否适合竖屏构图？需重新设计场面调度？
- [ ] 每3-5秒是否有视觉变化？（竖屏注意力模型）
- [ ] 是否有足够的"停留点"？（竖屏完播率优化）

---

### 第二轮：竖屏构图检查（竖屏核心）

**非协商铁律检查**：

| 检查项 | 标准 | 违规示例 |
|--------|------|----------|
| 眼睛位置 | 画面上1/3处 | ❌ 眼睛在画面中心 |
| 人脸位置 | 中心稳定区（60%） | ❌ 人脸偏左/偏右 |
| 头顶留白 | 上方10-15% | ❌ 头顶触碰画面上边缘 |
| 下巴位置 | 画面中心附近 | ❌ 下巴触碰画面下边缘 |
| UI遮挡区 | 底部94-140px无重要信息 | ❌ 字幕/关键动作在底部 |

**检查方法**：
1. 逐镜头检查分镜脚本中的构图描述
2. 生成测试图后，用9:16参考线叠加检查
3. 在手机上实际预览，确认构图

**自动化检查脚本**（可选）：
```python
# 检查AI提示词中是否包含竖屏构图关键词
required_keywords = ["9:16", "vertical", "upper third", "--ar 9:16"]
for prompt in all_prompts:
    assert any(kw in prompt for kw in required_keywords), f"Missing vertical keyword in: {prompt[:50]}"
```

---

### 第三轮：竖屏镜头语法检查

**竖屏不可变铁律**：

| 铁律 | 检查项 | 违规后果 |
|--------|--------|----------|
| 人脸必须在中心稳定区 | 每个镜头检查 | 观众注意力分散 |
| 眼睛必须在画面上1/3 | 每个镜头检查 | 构图中规中矩，无设计感 |
| 底部UI遮挡区禁止重要信息 | 每个镜头检查 | 平台UI遮挡关键内容 |
| 连续不超过2个相似景别 | 镜检查验 | 节奏单调 |
| 运动必须由情感或动作驱动 | 运镜描述检查 | 运镜无意义 |
| 竖屏快切：1-3秒镜头≥60% | 时长统计 | 节奏拖沓 |

**竖屏运镜检查清单**：

```
□ 垂直摇镜（Tilt Up/Down）— 有动机？
□ 升降（Crane Up/Down）— 有动机？
□ 微移（Micro Dolly）— 有动机？
□ 手持（Handheld）— 有动机？
□ 稳定器（Gimbal）— 有动机？
□ 禁用：smooth/steady/stabilized（除非刻意）
```

---

### 第四轮：竖屏AI提示词质量检查

**每个AI提示词必须包含**：

```
必选其一（画幅指定）：
✅ --ar 9:16（Midjourney）
✅ 9:16 aspect ratio（其他平台）
✅ vertical orientation（通用）
✅ mobile phone screen ratio（强调手机端）

必选其一（构图关键词）：
✅ vertical composition
✅ subject centered
✅ eye level at upper third
✅ rule of thirds vertical
✅ vertical framing

必选（质感层）：
✅ subsurface scattering（皮肤）
✅ natural skin texture（皮肤）
✅ fabric weave visible（面料）
✅ anamorphic characteristics / mobile lens characteristics（光学）
✅ NO plastic skin, CGI look, over-sharpened（负面）
```

**检查清单**：

```
□ 是否包含画幅指定（--ar 9:16 或等效）？
□ 是否包含竖屏构图关键词（vertical composition 等）？
□ 是否包含写实质感层（皮肤/眼睛/材质/光学）？
□ 是否包含负面提示词（避免塑料感）？
□ 是否标注了光影与色彩（情绪密码）？
□ 是否指定了运镜与角度（竖屏垂直运镜）？
□ 是否避免了横屏关键词（horizontal/landscape/2.39:1）？
```

**提示词质量评级**：

| 等级 | 标准 | 处理方式 |
|------|------|----------|
| ⭐⭐⭐⭐⭐ | 包含所有必需项+质感层+负面词 | 直接可用 |
| ⭐⭐⭐⭐ | 包含画幅+构图+光影，缺质感层 | 补充质感层后可用 |
| ⭐⭐⭐ | 包含画幅+构图，缺光影/质感 | 需补充后使用 |
| ⭐⭐ | 仅有画幅指定，内容空洞 | 需重写 |
| ⭐ | 无画幅指定/横屏构图 | 必须重写 |

---

### 第五轮：竖屏覆盖规划检查

**Vertical Coverage Strategy 检查**：

```
□ 每个主要对话/互动场景是否有Vertical Coverage Strategy？
□ 覆盖是否≥V1-V6（全景/中景/近景/特写/极特写/Insert）？
□ 垂直层次（上/中/下）是否明确？
□ 单镜构图变化（变焦/微移）是否标注？
□ 视线方向一致性是否检查？（避免跳切）
□ 竖屏快切节奏（1-3秒）是否体现？
```

**竖屏覆盖 vs 横屏覆盖对比检查**：

| 维度 | 横屏（已检查） | 竖屏（需检查） |
|--------|----------------|----------------|
| 空间关系 | Master Axis锁定 | 垂直层次（上/中/下） |
| 对话戏 | OTS/单人中景/全景 | 垂直构图变化 |
| 运镜 | 水平摇镜/跟拍 | 垂直摇镜/升降/微移 |
| 剪辑节奏 | 2-6秒 | 1-3秒（竖屏快切） |
| 轴线 | 180°法则 | 垂直中心线（可越，但需动机） |

---

### 第六轮：竖屏整体验收

**竖屏观看体验检查**：

```
视觉体验：
□ 人脸始终在中心稳定区？
□ 眼睛位置始终在上1/3处？
□ 色彩高饱和、手机屏幕可见性良好？
□ 光影适配顶光/侧光优先逻辑？

节奏体验：
□ 1-3秒镜头占比 ≥ 60%？
□ 每3-5秒有视觉变化？
□ 是否有足够的"停留点"？

技术体验：
□ 所有AI提示词包含 --ar 9:16？
□ 所有提示词包含竖屏构图关键词？
□ 写实质感层应用于每个提示词？
□ 底部UI遮挡区无重要信息？

平台适配：
□ TikTok/Reels/抖音 画幅正确（9:16）？
□ Instagram 备选画幅（4:5）已考虑？
□ 字幕（如有）在安全区内？
```

---

## 三、竖屏专项检查清单

### 3.1 竖屏构图专项

```
□ 眼睛在画面上1/3处（每个镜头）
□ 人脸在中心稳定区（每个镜头）
□ 头顶留白10-15%（全景/中景）
□ 下巴不触碰画面下边缘（特写/极特写）
□ 底部94-140px无重要信息（所有镜头）
□ 垂直引导线利用（门框/树干/建筑线条）
□ 单手操作友好（重要信息在中心60%区域）
```

### 3.2 竖屏色彩专项

```
□ 高饱和度策略（手机屏幕适配）
□ 肤色保护（不因高饱和而失真）
□ 对比度增强（户外观看环境）
□ 色彩情绪映射正确（参考模块8.2）
□ 三阶段色彩演变标注（如前段/中段/后段）
```

### 3.3 竖屏运镜专项

```
□ 垂直运镜动机明确（Tilt/Crane/Micro Dolly）
□ 手持有机感（natural camera shake）
□ 反肥皂剧锁（cinematic 24fps motion）
□ 禁用词检查（smooth/steady/stabilized）
□ 运镜与情感/动作驱动匹配
```

### 3.4 竖屏AI提示词专项

```
□ --ar 9:16 或等效画幅指定（每个提示词）
□ vertical composition 或等效构图关键词（每个提示词）
□ 写实质感层（皮肤/眼睛/材质/光学）（每个提示词）
□ 负面提示词（plastic skin等）（每个提示词）
□ 竖屏打光位置（顶光/侧光优先）（每个提示词）
□ 避免横屏关键词（horizontal/landscape）（每个提示词）
```

---

## 四、竖屏自检报告模板

```markdown
## 竖屏自检报告

**项目**：[项目名称]
**集数**：[集数]
**检查日期**：[日期]
**检查人**：[姓名]

---

### 第一轮：剧本覆盖度
- 评分：X/10
- 问题：[列表]
- 通过：✅/❌

### 第二轮：竖屏构图
- 眼睛位置正确：✅/❌（X/X镜头通过）
- 人脸在中心区：✅/❌（X/X镜头通过）
- UI遮挡区检查：✅/❌
- 通过：✅/❌

### 第三轮：竖屏镜头语法
- 竖屏铁律遵守：✅/❌
- 快切节奏（1-3秒≥60%）：✅/❌
- 运镜动机明确：✅/❌
- 通过：✅/❌

### 第四轮：AI提示词质量
- 画幅指定（--ar 9:16）：✅/❌（X/X提示词通过）
- 竖屏构图关键词：✅/❌（X/X提示词通过）
- 写实质感层：✅/❌（X/X提示词通过）
- 平均质量评级：⭐⭐⭐⭐（X/X提示词）
- 通过：✅/❌

### 第五轮：竖屏覆盖规划
- Vertical Coverage Strategy完整：✅/❌
- 垂直层次明确：✅/❌
- 视线方向一致：✅/❌
- 通过：✅/❌

### 第六轮：整体验收
- 竖屏观看体验：✅/❌
- 节奏体验：✅/❌
- 技术体验：✅/❌
- 平台适配：✅/❌
- 通过：✅/❌

---

### 总体评分：[X/10]
### 需修复项：[列表]
### 优化建议：[列表]
```

---

## 五、竖屏常见问题与修复

### 5.1 构图问题

| 问题 | 原因 | 修复 |
|------|------|------|
| 眼睛不在上1/3 | 提示词未指定 | 加入 `eye level at upper third` |
| 人脸偏左/偏右 | 提示词未指定中心构图 | 加入 `subject centered, center-stable zone` |
| 头顶触碰上边缘 | 构图过满 | 加入 `generous white space at top` |
| 下巴触碰下边缘 | 构图过满 | 加入 `full figure shot, head at upper third` |

### 5.2 提示词问题

| 问题 | 原因 | 修复 |
|------|------|------|
| 生成横屏图 | 缺少画幅指定 | 加入 `--ar 9:16` 或 `vertical orientation` |
| 人物变形 | 画幅指定错误 | 检查是否为 `--ar 9:16`（不是 `16:9`） |
| 塑料感严重 | 缺少质感层 | 加入写实质感层（皮肤/材质/光学） |
| 色彩暗淡 | 缺少色彩策略 | 加入 `high saturation, mobile screen optimized` |

### 5.3 节奏问题

| 问题 | 原因 | 修复 |
|------|------|------|
| 节奏拖沓 | 长镜头占比过高 | 将>5秒镜头拆分为2-3个短镜头 |
| 视觉单调 | 相似景别连续 | 调整景别，避免连续2个相似景别 |
| 缺少停留点 | 剪辑过于密集 | 插入2-4秒的"呼吸镜头"（全景/环境） |

---

## 六、竖屏自检工具（可选）

### 6.1 提示词检查脚本

```python
# check_vertical_prompts.py
import re

def check_vertical_prompt(prompt):
    """检查单个提示词是否符合竖屏规范"""
    issues = []
    
    # 检查画幅指定
    if not re.search(r'--ar\s+9:16|9:16\s+aspect|vertical\s+orientation', prompt, re.I):
        issues.append("缺少画幅指定（--ar 9:16）")
    
    # 检查竖屏构图关键词
    vertical_keywords = ['vertical composition', 'upper third', 'subject centered', 'vertical framing']
    if not any(kw in prompt.lower() for kw in vertical_keywords):
        issues.append("缺少竖屏构图关键词")
    
    # 检查质感层
    texture_keywords = ['subsurface scattering', 'skin texture', 'fabric weave', 'natural texture']
    if not any(kw in prompt.lower() for kw in texture_keywords):
        issues.append("缺少写实质感层")
    
    # 检查负面词
    negative_keywords = ['plastic skin', 'CGI look', 'over-sharpened', 'wax face']
    if not any(kw in prompt.lower() for kw in negative_keywords):
        issues.append("缺少负面提示词（plastic skin等）")
    
    # 检查横屏关键词（违规）
    horizontal_keywords = ['horizontal composition', 'landscape format', '2.39:1', '--ar 16:9']
    for kw in horizontal_keywords:
        if kw in prompt:
            issues.append(f"包含横屏关键词：{kw}")
    
    return issues

# 使用示例
prompt = "portrait of a young man, --ar 9:16, vertical composition..."
issues = check_vertical_prompt(prompt)
if issues:
    print(f"问题：{issues}")
else:
    print("✅ 提示词符合竖屏规范")
```

### 6.2 构图检查脚本（参考线叠加）

```python
# check_composition.py
from PIL import Image, ImageDraw, ImageFont

def add_vertical_guides(image_path, output_path):
    """在图片上叠加竖屏构图参考线"""
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    
    width, height = img.size
    
    # 上1/3线（眼睛位置）
    eye_line_y = height // 3
    draw.line([(0, eye_line_y), (width, eye_line_y)], fill='red', width=2)
    
    # 中心稳定区（60%宽度）
    center_left = int(width * 0.2)
    center_right = int(width * 0.8)
    draw.rectangle([(center_left, 0), (center_right, height)], outline='green', width=2)
    
    # 底部UI遮挡区
    ui_zone_y = height - 140
    draw.rectangle([(0, ui_zone_y), (width, height)], fill='#FF000080')
    
    # 保存
    img.save(output_path)
    print(f"已保存带参考线的图片：{output_path}")

# 使用示例
add_vertical_guides('shot_001.png', 'shot_001_guided.png')
```

---

## 七、总结

竖屏自检的核心差异：
1. **构图检查是第一优先级**（眼睛在上1/3，人脸在中心区）
2. **AI提示词必须包含 --ar 9:16**（画幅指定是竖屏的基础）
3. **节奏更快**（1-3秒镜头≥60%）
4. **底部UI遮挡区必须检查**（平台差异）
5. **色彩高饱和策略**（手机屏幕适配）

与横屏自检的关系：
- 相同项：剧本覆盖度、视觉一致性、镜头语法、写实质感层
- 差异项：构图检查（横屏=轴线，竖屏=垂直构图）、覆盖规划（横屏=Master/Axis，竖屏=垂直层次）、节奏（横屏慢，竖屏快）
