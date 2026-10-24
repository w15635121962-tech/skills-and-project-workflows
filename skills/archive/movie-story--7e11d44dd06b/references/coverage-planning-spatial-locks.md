# Coverage Planning & Spatial Coordinate Locking Protocol

## 概述

覆盖拍摄规划与空间坐标锁定协议，确保 AI 分镜具备实拍级别的覆盖规划和精确空间坐标控制。

## 强制触发条件

凡场景中包含以下内容，必须执行本协议：
- 显著对话
- 情绪互动
- 权力关系变化
- 多人物对峙
- 需要后期节奏控制

纯动作戏或极简场景可酌情简化，但仍需标注基础坐标。

## 一、Coverage Planning 执行步骤

### Step 1: 分析对话节拍的情绪功能

为每个主要对话段落判断：
- 权力动态 / 情绪反转
- 潜台词与心理距离变化
- 高潮点 / 情绪爆发 / 沉默张力
- 信息传递 vs 情绪传递

### Step 2: 制定场景级 Coverage Strategy

**对话戏最小覆盖标准**（可上调）：
1. **1个 Master / 全景** — 建立空间关系与初始权力
2. **双方 Clean Single（中景或近景）**
3. **至少1个 OTS（Over the Shoulder）**，建议不对称处理
4. **1-2个 Reaction / Insert** — 手、道具、眼泪、环境细节
5. **可选**：极端情绪时增加 ECU 或反应特写

### Step 3: 输出格式

```markdown
**Coverage Strategy — Scene X**

| 编号 | 镜头类型 | 核心作用 | 后期用途 |
|------|---------|---------|---------|
| C1 | Master (WS/MS) | 锁定空间关系与初始权力动态 | 定场 + 全景揭示 |
| C2 | Clean Single - A (MCU) | 给予A表演空间与情绪微表情 | 情绪切入 |
| C3 | Clean Single - B (MCU) | 给予B表演空间与反应空间 | 反应剪辑 |
| C4 | OTS → A (MCU) | 强化关系张力与偷看感 | 对话节奏 |
| C5 | OTS → B (CU) | 不对称处理 | 权力暗示 |
| C6 | Insert/Reaction | 手/道具/眼泪 | 情绪高潮切入点 |

**后期灵活性说明**：[描述角度切换可实现的视觉权力反转/节奏变化]
```

## 二、Spatial Coordinate Locking 系统

### 坐标系统定义

| 要素 | 定义 |
|------|------|
| Master Axis (C1) | 场景第一个 Master 镜头确立的主轴线，后续镜头必须保持在轴线同一侧（180°法则） |
| 坐标原点 | 主要家具中心或房间关键结构 |
| 高度基准 | Eye Level ≈ 1.6m |
| 距离单位 | 米（m） |

### SHOT 坐标标注格式

```markdown
**Spatial Coordinates**:
- Axis: [Maintaining/Intentionally Breaking] Master Axis C1
- Camera Position: C[X], [Eye/Low/High] Level (Z=[X.XX]m), Distance to subject: [X.X]m
- Primary Subject: Screen [left/right/center], Depth ≈ [X.X]m from camera plane
- Secondary Subject: Screen [left/right], Depth ≈ [X.X]m from camera plane
- Framing Note: [Rule of thirds / Center / Golden ratio + 负空间方向]
```

### 坐标标注原则

1. 第一个详细镜头必须**定义并锁定 Master Axis C1**
2. 后续镜头必须声明 "Maintaining Master Axis C1"
3. 故意越轴时必须在备注中说明理由
4. 与9机位参考图体系配合：坐标锁定机位距离，9机位提供视觉参考

### AI 提示词坐标锚定指令

```
"Strictly maintain Master Axis C1 and spatial relationships. Camera position and subject depth exactly as described in Spatial Coordinates. No axis crossing unless explicitly noted."
```

## 三、自检清单

- [ ] 每个主要对话节拍有明确 Coverage Strategy？
- [ ] 覆盖 ≥ Master + 双方 Single + OTS？
- [ ] 第一个详细镜头已定义 Master Axis C1？
- [ ] 所有后续镜头声明了轴线一致性？
- [ ] 坐标标注有具体距离/屏幕位置/高度？
- [ ] 坐标与9机位系统协调一致？

## 四、与现有系统的关系

| 系统 | 职责 | 配合方式 |
|------|------|---------|
| Coverage Planning | 决定"拍哪些角度" | 生成 Coverage Strategy 表 |
| Spatial Coordinate Locking | 锁定"每个镜头的精确机位" | 写入每个 SHOT 的坐标字段 |
| 9机位场景参考图集 | 提供视觉参考 | 坐标系统引用机位编号 |
| 镜头模板 (模块3) | 单镜头描述格式 | 新增 Spatial Coordinates 字段 |
| Screen Position (模块11) | 画面构图定位 | 与坐标的 Framing Note 协调 |
