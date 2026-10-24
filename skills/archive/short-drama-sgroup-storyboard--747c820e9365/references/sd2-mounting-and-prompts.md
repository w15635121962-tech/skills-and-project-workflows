# SD2.0 挂载与提示词规则

> 加载时机：写挂载 ID、Positive Prompt、Negative Prompt 时。

---

## 1. 每组必须有挂载

格式：

```md
本组挂载：`@角色-状态(ID)`、`@场景(ID)`、`@道具(ID)`、`@VFX(ID)`
```

### 1.1 人物按状态拆 ID

同一个人物在不同剧情阶段是**不同 ID**：

- 火场状态
- 重生状态
- 女仆状态
- 龙堡状态
- 怀孕状态
- 觉醒状态
- 战斗状态
- 失忆状态

### 1.2 道具按持有人/状态拆 ID

- 戒指在谁手里
- 皇冠是否被举起
- 法令是否展开
- 药剂是否在前景

**规则**：挂载只列**本组画面里真实可见**的角色、场景、道具、VFX。画外角色即使台词提到，
也**不挂载**。

---

## 2. Positive Prompt 写法

必须具体描述：

- 人物状态
- 场景
- 景别倾向
- 情绪
- 手部动作
- 关键道具
- 光线和氛围
- 防止误解的限制

**示例：**

```md
SD2.0 Positive Prompt：
`realistic cinematic fantasy drama, Diana alone in close-up, dry eyes no tears, restrained stunned
expression, shallow breath pausing then settling, fingers gripping black gold dress fabric, clean
empty stone pillar background, shallow depth of field, solemn public recognition, character micro
expressions`
```

**写法要点：**

| 要素 | 建议写法 |
|---|---|
| 风格锁定 | `realistic cinematic [题材], photorealistic live-action film still` |
| 人物与状态 | 单人直呼其名 + `alone in close-up / medium shot` |
| 情绪 | 用微表情词 + 明确否定（如 `dry eyes no tears`）防止模型加戏 |
| 手部 | 必须写明手在做什么（`fingers gripping … fabric`） |
| 背景 | 明确"干净、空、只有什么"（`clean empty stone pillar background`） |
| 光学 | `shallow depth of field`、焦段、光线方向 |
| 限制 | 一句防止误解的限制语，如 `character micro expressions` |

---

## 3. Negative Prompt 写法

必须防止：

- 重复人物
- 背景乱生人
- 同脸复制
- 错误道具
- 夸张光效
- 字幕水印
- 低质肢体

**示例：**

```md
S组生成反向约束：
`crowd, background people, extra people, duplicate faces, cloned face, same character twice,
multiple Diana, multiple Leona, group shot, wide crowd tableau, subtitles, text, watermark,
bad hands, extra fingers, deformed anatomy`
```

**通用 Negative 骨架**（每组至少包含）：

```md
crowd, background people, extra people, duplicate faces, cloned face, same character twice,
group shot, subtitles, text, watermark, bad hands, extra fingers, deformed anatomy,
glowing eyes, glowing body, excessive light effects
```

再把本集所有会露脸的角色名逐一加 `multiple <角色名>` 做去重保险。

---

## 4. 挂载 → 提示词 一致性检查

写完后逐组自问：

1. 挂载里的每个 ID，画面里是否真的可见？
2. 画面里出现的每个角色/道具，是否都已在挂载里？
3. 提示词里的人名数量 = 挂载里的角色数量？（不一致就是穿帮隐患）
4. Negative 是否覆盖了本组所有可能出现重复的角色名？

**四项全过，才允许进入下一步。**
