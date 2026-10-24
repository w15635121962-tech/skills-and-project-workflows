# short-drama-sgroup-storyboard · 短剧 S 组分镜系统

> 从《短剧分镜经验总结｜新对话使用版》提炼而成。v1.0.0 · 2026-09-10

## 这个技能做什么

把短剧剧本重新设计成**能看懂、能代入、能剪出来**的镜头方案。核心是"S 组"方法论 +
SD2.0 挂载 + 防穿帮 + 自检，最终输出分镜 MD 与 Word 文档。

## 硬规则一句话版

每组 ≤15 秒 · 每组有情绪钩子 · 每句台词有画面绑定 · 长句必须拆气口 ·
每组有挂载 + 正反向提示词 · 每组有尾帧衔接 · 一镜一张清晰脸 ·
禁止月纹/身体发光/背景乱生人 · 输出前过自检。

## 文件结构

```
short-drama-sgroup-storyboard/
├── SKILL.md                                  主入口：硬规则 / 工作流 / 快速参考 / 路由
├── references/
│   ├── sgroup-and-shot-language.md           S组规则、15秒控制、景别职责
│   ├── dialogue-and-performance.md           台词时长、画面绑定、气口、表演细节库
│   ├── continuity-and-antiartifact.md        组间衔接、防穿帮、禁止画面、多角色同场
│   ├── sd2-mounting-and-prompts.md           挂载ID规则、Positive/Negative 写法与一致性检查
│   ├── troubleshooting.md                    六类常见问题的原因与修正
│   ├── output-and-selfcheck.md               标准输出结构、自检清单、通过声明、新对话提示词
│   └── source-experience-summary.md          原文逐字留档（无损）
└── assets/
    └── episode-storyboard-template.md        单集分镜可复制骨架
```

## 使用方式

在对话里直接说："用 S 组逻辑给这个剧本做分镜"、"按短剧分镜经验总结拆 S 组"、
"这组 SD 老是生重复人物，帮我改" 等，即可触发。

新对话首次使用时，可把 [references/output-and-selfcheck.md](references/output-and-selfcheck.md)
第 3 节的"新对话使用提示词"复制给助手，快速对齐标准。

## 与其他技能的边界

| 需求 | 用哪个 |
|---|---|
| 短剧 S 组分镜 + SD2.0 挂载 + 防穿帮 | **本技能** |
| 只要纯分镜表格（横竖屏/中英文/推文） | `storyboard-table` |
| AI 视频提示词组（Format C 逐镜） | `short-drama-video-prompts` |
| 焦段提示词网格 / 多镜头序列 | `focal-grid` / `multishot-cinematic` |
| 角色、场景、道具资产提取 | `character-asset` / `scene-asset` / `script-props-extractor` |
