# 剧梦全自动化生成流程框架

这是一个以本机文件为输入、以结构化中间产物为核心的 AI 短剧视频流水线骨架。它将剧本分析、资产绑定、分镜设计、Format C 提示词、剧梦浏览器自动化和生成后自检拆成可暂停、可重试、可审计的阶段。

## 安全边界

- 登录状态只使用本机独立浏览器配置目录，不读取或复制密码、Cookie、`auth.json` 等敏感文件。
- 剧梦网址、浏览器配置目录、资产目录和积分授权均从本地配置读取，不写入源码。
- 积分生成默认需要人工确认；只有在明确设置 `credit_authorization.confirm_before_generate=false` 后才允许批量提交。
- 平台页面可能改版，浏览器适配器只负责定位和报告，发现选择器变化时停止，不盲点。

## 快速开始

```bash
python3 automator.py init
python3 automator.py run --input 02剧本/玻璃箱里的神明.docx
# 若独白是单独生成的本地文件：
python3 automator.py run --input 02剧本/玻璃箱里的神明.docx --monologue 路径/独白稿.txt
# 若要指定豆包结构化分镜文件：
python3 automator.py run --input 02剧本/玻璃箱里的神明.docx --doubao-output /Users/zc/Doubao/chats/目录/导演分镜结构化结果.md
# 若要指定 Claude 的结构化拆镜文件：
python3 automator.py run --input 01自动化项目素材/玻璃箱的神明/完整剧本/玻璃箱里的神明.docx --claude-output 路径/claude_storyboard.md
# 若要指定英文原台词剧本：
python3 automator.py run --input 02剧本/玻璃箱里的神明.docx --dialogue 02剧本/玻璃箱里的神明-EN.docx
python3 automator.py check --run runs/<run_id>
```

运行后会在 `runs/<run_id>/` 生成：

- `story_bible.json`：人物、场景、道具、世界观和不确定性
- `asset_bindings.json`：图片资产与剧本实体的绑定及缺失项
- `storyboard.json`：镜头、时长、动作因果、视线和表演设计
- `monologue_timing.json`：本地独白段落、字数、语速和计算时长；分镜时长以此为准
- `doubao_design.json`：自动读取的豆包人物表演、走位、视线、冲突和镜头设计，并记录源文件哈希
- `claude_split.json`：Claude 结构化拆镜文件的来源、哈希和拆镜单元；默认是下游分镜的结构边界依据
- `format_c_prompts.md`：由 Codex 生成的 Format C V2.6 提示词，按光影连续单元分组，含 11 个固定字段、具体构图参数与焦段
- `qa_report.json`：阻断项、警告和待人工确认项

独白驱动规则：对白引号内的内容排除，其他叙述、画面描述和内心叙述全部按独白处理。默认按每秒 4.5 个中文有效字估算，可在 `config/local.json` 的 `quality.monologue_chars_per_second` 调整。每个独白段按不超过 4 秒拆成镜头，生成的提示词按镜头顺序写入 `format_c_prompts.md`，之后才允许复制到剧梦对应分镜提示词框。

豆包文件读取：默认从 `/Users/zc/Doubao/chats` 自动选择最新的“导演分镜/结构化结果”Markdown 文件；也可以用 `--doubao-output` 指定。系统按独白文本与豆包镜头中的“对白与对白反应”做文本匹配，匹配成功时继承豆包的机位、构图、走位、视线、微表演、光影、音频、运动强度和负面约束。

台词规则：提示词不输出中文独白、旁白或叙述原文；从 `project.dialogue_script` 或 `--dialogue` 指定的英文剧本中提取原英文台词，只在对应高潮镜头保留英文原文。没有英文台词的镜头明确写“禁止生成口型”，只表现动作、冲突和结果。

构图规则：分镜提示词必须写出具体景别、全画幅等效焦段（mm）、机位高度、轴线、构图比例、景深、视线偏移和前景遮挡状态。规则来源为 [分镜构图参数手册.md](/Users/zc/Downloads/分镜构图参数手册.md)，并已复制进短剧分镜技能的 references 目录。

Claude 规则：Claude 不由本自动化流程操控。用户手动投喂 Claude；如将结果保存到本地并通过 `--claude-output` 提供，Codex可读取为可选结构参考。未提供时不会阻断下游。

提示词规则：Codex 是最终提示词生成器。Claude 只提供用户手动保存的可选结构拆分，豆包负责表演、走位和冲突设计；独白/旁白不会写入生成提示，只保留原英文对白。

## 接入真实平台

编辑 `config/local.json`：填写剧梦网址、独立浏览器配置目录和资产库目录；先以 `dry_run=true` 运行。确认资产绑定、提示词和 QA 报告无误后，再在浏览器中手动完成一次登录，运行 `browser inspect` 验证页面结构，最后逐批启用生成。

本仓库不包含真实平台 API，也不会伪造积分授权。平台适配器采用“页面状态识别 → 草稿填写 → 截图/状态记录 → 人工确认 → 提交”的闸门设计。
