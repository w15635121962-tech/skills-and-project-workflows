# Human POV 人眼主观视角插件

适用于 DaVinci Resolve / Fusion 的单节点 GPU Fuse。它把普通稳定素材变成人物第一视角，包含：

- 静止、行走、奔跑、惊慌四种人物状态；
- 呼吸、步伐起伏、头部摆动、微颤、眼球扫视；
- 自动随机眨眼、连续眨眼、手动闭眼；
- 注视中心、周边视觉虚化/降饱和、轻微色散、生理暗角；
- 曝光适应、曲率、运动拖影和自动裁边。

## macOS 安装

1. 退出 DaVinci Resolve。
2. 双击 `install_macos.command`。如果系统阻止运行，在终端执行：

   ```zsh
   chmod +x install_macos.command uninstall_macos.command
   ./install_macos.command
   ```

3. 重启 Resolve，在“特效库 > 工具箱 > 特效 > Fusion Effects”中搜索 `Human POV`。

也可以在 Fusion 页面按 `Shift+Space`，搜索 `Human POV 人眼主观视角`，直接添加 Fuse 节点。

## 使用建议

- 把插件拖到视频片段上，先选择“人物状态”。
- 把“时间线帧率”设成当前时间线帧率，否则动作速度会不准确。
- 横屏素材通常保持 5% 自动裁边；竖屏或“奔跑/惊慌”可提高到 7%–10%。
- 用“手动水平/垂直观察”和“手动闭眼”打关键帧，可以精确配合角色看向目标、昏迷或醒来。
- 剪辑期间可用“草稿”采样，最终输出切到“标准”或“高”。

## Windows / Linux 手动安装

把 `Fuses/HumanPOV.fuse` 放入 Resolve 的 Fusion `Fuses` 目录；把 `Templates/Edit/Effects/Human POV/Human POV.setting` 放入 `Templates/Edit/Effects/Human POV`。重启 Resolve。

常见用户级路径：

- Windows Fuse：`%PROGRAMDATA%\\Blackmagic Design\\DaVinci Resolve\\Support\\Fusion\\Fuses`
- Windows 模板：`%APPDATA%\\Blackmagic Design\\DaVinci Resolve\\Support\\Fusion\\Templates\\Edit\\Effects\\Human POV`
- Linux Fuse：`~/.local/share/DaVinciResolve/Fusion/Fuses`
- Linux 模板：`~/.local/share/DaVinciResolve/Fusion/Templates/Edit/Effects/Human POV`

## 卸载

macOS 双击 `uninstall_macos.command`，然后重启 Resolve。

## 兼容性

依据 DaVinci Resolve 20.2.2 随附的 Fusion Fuse SDK 构建。Fuse 使用 Resolve/Fusion 的 DVIP GPU 路径；若 GPU 内核无法编译，会安全回退为原始画面，不会让合成断链。

当前版本：1.0.0。

