---
name: camera-movement
description: "电影运镜专精系统 — 从叙事意图到镜头运动的完整映射与决策链。只做运镜，不做分镜表格、角色资产、场景资产、AI提示词。触发词：运镜、镜头运动、camera movement、运镜设计、运镜方案、机位规划、镜头调度、运镜决策、怎么运镜、运镜策略、镜头怎么动。当用户要求为某段剧情/场景/节拍设计运镜方案时使用。"
agent_created: true
---

# Camera Movement — 电影运镜专精系统

> **Version 1.0.0** · 2026-06
> 参考文档 → `references/vertical-camera-philosophy.md`

---

## 定位 — 只做运镜

| 技能 | 职责 | 本技能边界 |
|------|------|----------|
| `storyboard-table` | 分镜表格输出 | ❌ 不做 |
| `character-asset` | 角色外貌/服装/配饰 | ❌ 不做 |
| `scene-asset` | 场景卡/灯光/调色 | ❌ 不做 |
| `multishot-cinematic` | 战斗多镜头AI提示词 | ❌ 不做 |
| **`camera-movement`** | **运镜决策+映射+规则+自检** | ✅ 只做这个 |

**用本技能当：** 已知叙事意图/情绪/场景阶段，需要推导运镜方案。
**用 storyboard-table 当：** 需要把运镜填进完整的分镜表格。

---

## 核心法则

1. **Motivated 原则**：每次运镜必须有叙事动机。无动机=无效镜头。
2. **入出连贯**：每个镜头的运镜出点流入下一个镜头的运镜入点。
3. **禁止矛盾方向**：缓推→紧接缓拉、急推→急推、手持→立刻静态锁定，均为禁止组合。
4. **景别匹配**：运镜类型必须匹配景别叙事功能（详见景别-运镜映射表）。

---

## 工作流

按四步顺序执行，每步输出后再进入下一步。

```
STEP 1 → INTENT    识别叙事意图 + 故事阶段 + 能量级别
STEP 2 → MAP       运镜映射决策（横屏 / 竖屏 / 焦段递进）
STEP 3 → CHAIN     运镜链路编排（入点→出点→桥接）
STEP 4 → CHECK     运镜自检，修复，通过声明
```

**硬规则：**
- Step 1 未完成不得进入 Step 2
- Step 4 未通过前不输出最终结果
- 每个运镜回答：**"这个运镜让观众感受到什么？为什么是这个而不是另一个？"**

---

## STEP 1 — INTENT（叙事意图识别）

### 1.1 叙事意图 → 运镜种子

**15类叙事意图**：

| 意图 | 含义 | 运镜种子 |
|------|------|---------|
| RevealInformation | 揭示信息/秘密 | Slow Push In |
| HideInformation | 遐藏真相 | Static / Slow Lateral |
| BuildSuspense | 制造悬念 | Slow Push In |
| BuildEmotion | 强化情绪 | Motivated Push |
| ShiftPower | 权力变化 | Push In to Dominant |
| EstablishRelationship | 建立关系 | Static / Slow Track |
| CreateIsolation | 强调孤独 | Pull Out |
| CreateIntimacy | 强调亲密 | Static / Slow Push |
| CreateThreat | 制造威胁 | Slow Creep |
| CreateRelief | 缓解压力 | Pull Out |
| Foreshadowing | 埋伏笔 | Static / Rack Focus |
| MisleadAudience | 误导 | Static (Blocked Composition) |
| BreakTrust | 信任破裂 | Axis Shift |
| MoralChoice | 道德选择 | Locked / Micro Push |
| ConfirmSuspicion | 确认怀疑 | Rack Focus to Evidence |

**输出格式**：
```
Scene Intent:
  Primary: [意图] — [具体说明]
  Secondary: [意图] — [具体说明]
  Anti-Intent: [必须避免] — [原因]
```

### 1.2 故事阶段 → 运镜基调

**7阶段场景结构**：

| 阶段 | 含义 | 运镜基调 | 剪辑速度 |
|------|------|---------|---------|
| Setup | 建立场景/关系 | Slow or Static | Slow |
| Development | 推进/互动 | Motivated Tracking | Moderate |
| Conflict | 冲突升级 | Push In / Handheld | Faster |
| Crisis | 被迫选择 | Locked / Slow Push | Delayed |
| Climax | 最高点 | Fast Push / Impact | Fastest |
| Resolution | 结果显现 | Pull Out | Slower |
| Aftermath | 余波/沉默 | Static | Long Hold |

**输出格式**：
```
Story Stage: [阶段]
Energy Level: [0.0-1.0]
Energy Direction: [Rising/Falling/Plateau/Peak/Drop]
```

### 1.3 能量级别 → 运镜强度

| 能量 | 运镜强度 | 推荐运镜 | 剪辑 |
|------|---------|---------|------|
| 低 (0.0-0.3) | 极低 | Static | Slow |
| 中 (0.3-0.6) | 中 | Slow Push | Moderate |
| 高 (0.6-0.8) | 高 | Push / Handheld | Fast |
| 极高 (0.8-1.0) | 极高 | Handheld / Fast Push | Fastest |
| 骤降 (Peak→Drop) | 归零 | Pull Out / Locked | Long Hold |

### 1.4 心理状态 → 运镜映射

| 心理状态 | 推荐景别 | 推荐运镜 | 推荐构图 |
|---------|---------|---------|---------|
| fear | CU, 85mm+ | Slight Push In | 主体偏侧，负空间放大恐惧 |
| anger | CU, Handheld | Unstable Push | 主体居中，压迫构图 |
| shame | High Angle CU | Static | 面部被遮挡 |
| dominance | Low Angle | Stable, Longer Lens | 主体占60%+，居中 |
| deception | Single Shot | Slow Lateral | 半阴影，视线不稳 |
| grief | Wide → CU | Slow Push + Hold | 负空间表达孤独 |

---

## STEP 2 — MAP（运镜映射决策）

### 2.1 运镜类型全表

| 运镜 | 中文名 | 叙事功能 | 禁止紧接 | 推荐后续 |
|------|--------|---------|---------|---------|
| Static | 静态 | 重量/稳定/蓄势 | 无动机快切 | 另一Static · Slow Push |
| Slow Push In | 缓推 | 压迫/聚焦/揭示 | 紧接缓拉 | Hold · Linger |
| Pull Back | 缓拉 | 孤立/疏离/释放 | 紧接缓推 | Static · Empty Frame |
| Tilt Up | 上摇 | 权力/仰望/揭示 | 紧接下摇 | Hold High · Crane Up |
| Tilt Down | 下摇 | 羞耻/俯视/压抑 | 紧接上摇 | Hold Low · Settle |
| Crane Up | 升/摇臂上 | 升华/超越/全局 | 无特殊 | Static Hold |
| Crane Down | 降/摇臂下 | 沉入/揭示/细节 | 无特殊 | Static Hold |
| Handheld | 手持 | 紧迫/不安/纪实 | 紧接锁定静态 | 另一Handheld · Settle to Drift |
| Crash Zoom | 急推/冲击式 | 震惊/冲击/暴击 | 无≥0.5s恢复的一切 | Static ≥1.5s · ECU Freeze |
| Rack Focus | 焦点切换 | 信息揭示/注意力引导 | 无特殊 | Static · Slow Push |
| Micro-drift | 微漂移 | 恐惧/不安/亲密 | 加速 | Decelerate to Static · Linger |
| Whip Pan | 甩镜/急摇 | 紧迫/惊吓/转场 | 无特殊 | Settle · Static |
| Walk-and-Talk | 行走对话 | 伴随/见证/流畅 | 硬切中间句 | Natural Pause · Settle |
| Linger Hold | 凝视保持 | 渴望/不舍/沉溺 | 快切 | Static · Slow Pull |
| Empty Frame Hold | 空镜保持 | 余韵/缺席/留白 | 快切 | Static · Slow Push In |

### 2.2 景别递进 + 运镜递进

#### 标准递进（情感加强）

```
运镜: Static(建立) → Slow Push(进入) → Motivated Push(亲近) → Crash/Lock(强调) → ECU Freeze/Linger(极致)
景别: WS → MS → MCU → CU → ECU
```

#### 标准递退（情感释放）

```
运镜: Locked/Linger(余韵) → Slow Pull(回稳) → Static(释放)
景别: CU/ECU → MCU → WS
```

#### 打斗递进

```
运镜: Static/Slow Push(对峙) → Handheld/Fast Track(交手) → Crash Zoom(撞击碎片) → Static ≥1.5s(间隔)
景别: WS → MS → CU/ECU → WS
```

**打斗铁律**：
- 撞击前：静态/缓推（绝不用手持）
- 撞击时：Crash Zoom / Whip Pan（每次撞击只用一个运动）
- 撞击后：ECU Static ≥1.5s（不切，不摇）

#### 暧昧递进

```
运镜: Static(距离) → Micro-drift(靠近) → Locked(凝视) → Linger ≥4.0s(失控) → Static(空镜余韵)
景别: WS/MS → MCU → CU → LINGER/ECU → 空镜
```

**暧昧铁律**：
- 运镜减速 · 峰值=静态 · 拉远=人物驱动 · 凝视=静态 · 空镜=静态

### 2.3 焦段递进运镜（来自 focal-grid）

| 焦段位置 | 镜头 | 运镜逻辑 |
|---------|------|---------|
| [1,1] 16-20mm | 极广角 | 极低运动感，搜索感 Subtle Push |
| [1,2] 24-35mm | 广角 | 低运动感，人群环绕 Slow Push |
| [1,3] 35-50mm | 中广角 | 低-中，对峙主导 Slow Push / Micro-drift |
| [2,1] 50-85mm | 中景 | 中，身体张力 Motivated Push |
| [2,2] 85mm | 中近景 | 中-高，锁定眼神+准备 Crash Zoom |
| [2,3] 100-135mm | 近景 | 高，攻击性 Crash Zoom + Motion Blur |
| [3,1] 135mm+ | 特写 | 高-极高，微表情+汗珠 Micro-drift |
| [3,2] 微距 | 极特写 | 极高，纹理级 Micro-drift / Near-Static |
| [3,3] 极端 | 抽象碎片 | 极高，重度 Motion Blur + Lens Distortion |

### 2.4 画幅适配决策

| 画幅 | 运镜偏好 | 运镜禁忌 |
|------|---------|---------|
| **16:9 横屏** | 水平运动优先：Pan / Track / Dolly / Push(水平) | 无特殊禁忌 |
| **9:16 竖屏** | 垂直运动优先：Tilt Up/Down / Crane Up/Down / Push(纵向) | ❌ 水平Pan（宽度不足） ❌ Roll旋转（易眩晕） ❌ 水平Follow无中心锁定 |

**竖屏运镜适配表**：

| 运镜 | 9:16竖屏适配 | 16:9横屏适配 |
|------|-------------|-------------|
| 推 | 优先纵向推（上→下或下→上） | 优先水平推（左→右或右→左） |
| 拉 | 优先纵向拉远 | 优先水平拉远 |
| 摇 | 优先上下摇 | 优先左右摇 |
| 横移 | 少用，竖屏横向空间有限 | 常用，自然运动方向 |
| 环绕 | 人物为轴心垂直环绕 | 人物为轴心水平环绕 |

---

## STEP 3 — CHAIN（运镜链路编排）

### 3.1 运镜链路输出格式

```
═══════════════════════════════════════════
运镜链路: [场景名]
═══════════════════════════════════════════
Intent: ___ · Stage: ___ · Energy: ___
画幅: ___ · 焦段弧: ___
═══════════════════════════════════════════

| 镜号 | 景别 | 运镜 | 叙事动机 | 入点状态 | 出点状态 | 桥接 |
|------|------|------|---------|---------|---------|------|
| 01   | ___  | ___  | ___     | ___     | ___     | ___  |
| 02   | ___  | ___  | ___     | ___     | ___     | ___  |
```

**各列填写规范**：

**镜号**：顺序编号。

**景别**：ELS / WS / MS / MCU / CU / ECU / INSERT / FRAGMENT / LINGER / INVOLUNTARY / EMPTY FRAME

景别叙事功能速查：

| 景别 | 内容占比 | 时长地板 | 叙事功能 |
|------|---------|---------|---------|
| ELS | <15% | 2.5s | 定场/建立 |
| WS | 15-30% | 2.0s | 空间锁定 |
| MS | 30-50% | 3.5s | 对话默认 |
| MCU | 40-60% | 3.0s | 亲密阈值 |
| CU | 50-70% | 2.0s | 强调/隐藏 |
| ECU | 70-100% | 1.0s | 碎片/极致 |
| INSERT | varies | 1.5s | 信息阅读 |
| FRAGMENT | varies | 0.5s | 观众拼合 |
| LINGER | varies | 4.0s | 凝视驻留 |
| INVOLUNTARY | varies | 2.0s | 身体泄露 |
| EMPTY FRAME | varies | 2.5s | 缺席留白 |

**运镜**：从 2.1 运镜全表中选择，必须标注速度（slow / subtle / imperceptible / fast / sudden）。

**叙事动机**：每个运镜必须写明让观众感受到什么，为什么是这个而不是另一个。禁止写"氛围""感觉"。

**入点状态**：运镜开始时的画面状态（从上一个镜头的出点流入）。

**出点状态**：运镜结束时的画面状态（流入下一个镜头的入点）。

**桥接**：如有禁止组合需要桥接，标注桥接镜头类型。

### 3.2 桥接规则

遇到禁止组合时，必须插入中性桥接镜头：

| 禁止组合 | 原因 | 桥接方案 |
|---------|------|---------|
| 缓推 → 紧接缓拉 | 方向矛盾 | 插入 Static ≥2.0s 或 INSERT |
| 急推 → 急推 | 连续冲击无呼吸 | 急推后 ≥0.5s 恢复 Static |
| 手持 → 锁定静态 | 观众眩晕 | 先减速至微漂移，再至静止 |
| 上摇 → 下摇 | 方向矛盾 | 插入高位保持镜头 |
| 无动机运动 | 运镜无叙事目的 | 删除运动或补动机 |

### 3.3 运镜链路设计原则

1. **入出流畅**：出点 = 下一镜入点（状态连续）
2. **节奏呼吸**：高运动 → 低运动 → 高运动（不允许连续同强度）
3. **动机驱动**：运镜弧线 = 叙事弧线（Setup=低运动，Climax=高运动）
4. **金句定格归零**：金句/落点句 → 运镜归零（纯静态），不管之前多剧烈
5. **峰值碎片**：情感爆发点 → Hitchcock碎片化快切（不用全景直述）

---

## STEP 4 — CHECK（运镜自检）

全链路完成后执行。修复每个失败项后再声明通过。

**A · 动机** — 每个运镜有存在理由：
- [ ] 每个运镜列有明确叙事动机（不是"氛围""感觉"）
- [ ] 无两个镜头用完全相同的运镜做完全相同的事
- [ ] 每次运镜让观众感受到特定的东西（压迫/孤立/震惊/渴望等）
→ **修复：** 无动机→删除或补动机。重复→合并或区分功能。

**B · 连贯** — 入出点流畅：
- [ ] 每个运镜出点流入下一个运镜入点
- [ ] 无禁止组合（缓推→紧接缓拉 / 急推→急推 / 手持→立刻静态锁定）
- [ ] 桥接镜头已标注
→ **修复：** 禁止组合→插入桥接。缺连贯→补写入出点状态。

**C · 节奏** — 运镜强度匹配叙事强度：
- [ ] Setup段运镜强度低于Climax段
- [ ] 无连续同强度运镜（高→高→高需要呼吸）
- [ ] 金句/落点句 = 运镜归零（纯静态）
- [ ] 能量骤降段 = 运镜归零或Pull Out
→ **修复：** 强度错位→调整运镜类型。缺呼吸→插入低运动镜头。

**D · 景别匹配** — 运镜类型匹配景别功能：
- [ ] WS段运镜偏建立性（Static/Slow Push/Crane）
- [ ] CU段运镜偏情感性（Push/Handheld/Locked）
- [ ] ECU段运镜偏极致性（Crash Zoom/Micro-drift/Static Hold）
- [ ] LINGER段 ≥4.0s
→ **修复：** 类型错配→调整运镜类型。

**E · 画幅适配** — 如指定画幅：
- [ ] 竖屏段运镜以垂直方向为主
- [ ] 竖屏段无水平Pan
- [ ] 竖屏段无Roll旋转
- [ ] 竖屏段人脸在中心稳定区，眼在上1/3
→ **修复：** 违反→替换为垂直等效运镜。

### 通过声明

```
═══════════════════════════════════════════
运镜方案: 通过
═══════════════════════════════════════════
意图: ___ · 阶段: ___ · 能量: ___
画幅: ___ · 焦段弧: ___
动机: ___ ✓ · 连贯: ___ ✓
节奏: ___ ✓ · 景别: ___ ✓ · 画幅: ___ ✓
禁止组合: 0 · 桥接: ___
运镜总数: ___
可进入分镜编排。
═══════════════════════════════════════════
```

---

## 融合书写规则（供 storyboard-table / movie-story 引用）

当运镜被写入分镜表格时，**禁止割裂人物动作与镜头运动**：

1. **绝不割裂**：画面描述禁止把"人物动作"和"镜头运动"拆成两段独立语句
2. **必须融合**：将人物动作+微表演+惯性+情绪落点与镜头运动融合为一段流动叙述
3. **Motivated 原则**：镜头运动必须由人物动作/情感/故事节拍驱动

**融合示例**：
✅ 女主缓缓从椅子上站起，双手微微用力撑着扶手，指节泛白，眼神从低垂逐渐抬起，带着压抑的坚定。镜头从略带俯视的中景开始，随着她起身而缓慢上摇并向前推进，在她完全站立时推至中近景。

❌ 镜头：从全景缓慢推至特写。角色：从椅子上站起，表情坚定。

---

## 参考文档

本技能包含以下参考文档，按需加载：

- `references/vertical-camera-philosophy.md` — 竖屏运镜哲学完整版（运镜类型竖屏适配表 + 竖屏运镜禁忌 + 竖屏节奏DNA + 竖屏景别定义 + 竖屏不可变铁律 + 竖屏叙事意图映射 + 竖屏故事语法映射）

当指定画幅为9:16竖屏时，必须读取此参考文档。

---

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-06 | 提纯初始版：运镜四步流程，15类意图映射，7阶段映射，能量映射，心理映射，运镜全表，禁止组合桥接，景别-运镜递进，焦段递进，画幅适配，融合书写规则 |
