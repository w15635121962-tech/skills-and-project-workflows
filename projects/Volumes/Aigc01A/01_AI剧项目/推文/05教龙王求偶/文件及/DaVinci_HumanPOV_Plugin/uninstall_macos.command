#!/bin/zsh
set -euo pipefail

RESOLVE_ROOT="${HOME}/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion"
FUSE_FILE="${RESOLVE_ROOT}/Fuses/HumanPOV.fuse"
EFFECT_FILE="${RESOLVE_ROOT}/Templates/Edit/Effects/Human POV/Human POV.setting"

[[ -f "${FUSE_FILE}" ]] && rm "${FUSE_FILE}"
[[ -f "${EFFECT_FILE}" ]] && rm "${EFFECT_FILE}"

echo "Human POV 已卸载。重启 DaVinci Resolve 后生效。"

