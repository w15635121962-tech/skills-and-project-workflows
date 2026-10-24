#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"
RESOLVE_ROOT="${HOME}/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion"
FUSE_DEST="${RESOLVE_ROOT}/Fuses"
EFFECT_DEST="${RESOLVE_ROOT}/Templates/Edit/Effects/Human POV"

mkdir -p "${FUSE_DEST}" "${EFFECT_DEST}"
install -m 0644 "${SCRIPT_DIR}/Fuses/HumanPOV.fuse" "${FUSE_DEST}/HumanPOV.fuse"
install -m 0644 "${SCRIPT_DIR}/Templates/Edit/Effects/Human POV/Human POV.setting" "${EFFECT_DEST}/Human POV.setting"

echo "Human POV 已安装。"
echo "请重启 DaVinci Resolve，然后在：特效库 > 工具箱 > 特效 > Fusion Effects 中搜索 Human POV。"

