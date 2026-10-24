# 技能与项目流程迁移库

2026-10-24 的完整迁移快照，保存于私有仓库。原始本地文件保留。

- **6,014 个技能来源**，包含 **1,218 种 SKILL.md 正文版本**；技能附件与插件依赖不同的版本分别保存，共 2,058 个可恢复目录。
- **1,438 份项目资料**：流程规则、制作脚本、依赖声明，以及字幕、Fairlight 音频、渲染、Fusion 效果和调色预设。
- **19,672 个有效载荷文件**，约 506.4 MiB。Git 自动复用相同文件内容。
- 覆盖 Codex、Agents、Cursor、已安装插件、技能历史备份、WorkBuddy，以及三块已挂载资料盘中的项目流程。

## 目录

| 目录 | 内容 |
| --- | --- |
| [skills/codex](skills/codex) | 当前 Codex 技能与系统技能 |
| [skills/agents](skills/agents) | 当前 Agents 技能 |
| [Cursor 技能入口](catalog/CURRENT_SKILLS.md) | 当前 Cursor 技能的来源与去重映射 |
| [skills/bundled-cursor](skills/bundled-cursor) | Cursor 内置技能 |
| [skills/archive](skills/archive) | 历史技能、备份及额外项目技能 |
| [plugins/current](plugins/current) | 当前插件包中的技能、脚本、参考资料和模板 |
| [plugins/archive](plugins/archive) | 历史插件版本及其依赖资料 |
| [projects](projects) | 各项目流程、脚本和制作预设，按来源路径镜像保存 |
| [catalog/skills.json](catalog/skills.json) | 每个技能来源到仓库目录的对应关系 |
| [catalog/projects.json](catalog/projects.json) | 项目资料来源与类别 |
| [catalog/excluded.json](catalog/excluded.json) | 排除项及原因，只有路径与说明 |
| [catalog/files.json](catalog/files.json) | 文件大小及 SHA-256 校验值 |

## 校验与恢复

下载或克隆整个仓库后，使用 Python 3.9 或更新版本：

```sh
python3 tools/verify.py
python3 tools/restore.py --destination /path/to/new-workspace --profile all
python3 tools/restore.py --destination /path/to/new-workspace --profile all --apply
```

恢复工具默认预览，`--apply` 才写入；目标必须是新目录或空目录。`current` 恢复当前技能与当前插件包，`projects` 恢复项目流程和预设，`all` 同时保留历史归档。恢复工具不会登录账号、执行制作脚本、安装插件或提交生成任务。

完整仓库文件另附 [SHA256SUMS](SHA256SUMS)，可执行 `shasum -a 256 -c SHA256SUMS` 检查。

## 迁移边界

账号配置、登录状态、Cookie、API 密钥、SSH 私钥、环境凭据、聊天记录、应用数据库、依赖缓存和已编译应用安装包均不迁移。第三方文档中的公开 API 示例与占位符保留；本次内容扫描未对正文作自动改写。

保留技能和流程所需的模板、样例资产、脚本、参考资料和许可证。剧本、按集分镜、字幕成品、视频素材与成片不属于本次项目流程迁移范围。技能内自带的示例媒体作为技能资源保留。

项目旧脚本中的本机绝对路径是原始项目事实，迁移未更改；换机器使用前应调整路径并安装对应依赖。历史技能仅作归档，当前任务仍以当前项目规则及用户最新要求为准。插件的云端连接、模型服务、认证及官方运行环境需在目标机器重新配置。

扫描范围与不可访问来源限制见 [catalog/scan-scope.json](catalog/scan-scope.json)。未挂载磁盘和云端未连接资料不在本机快照内。原作者许可证继续适用，仓库没有额外授予第三方内容许可。
