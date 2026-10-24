#!/usr/bin/env python3
from pathlib import Path
import ctypes
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
FUSE = ROOT / "Fuses" / "HumanPOV.fuse"
SETTING = ROOT / "Templates" / "Edit" / "Effects" / "Human POV" / "Human POV.setting"


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


for path in (FUSE, SETTING, ROOT / "README.md", ROOT / "install_macos.command"):
    if not path.is_file() or path.stat().st_size == 0:
        fail(f"missing or empty file: {path}")

fuse_text = FUSE.read_text(encoding="utf-8")
setting_text = SETTING.read_text(encoding="utf-8")

if 'FuRegisterClass("HumanPOV", CT_Tool' not in fuse_text:
    fail("Fuse class registration not found")
if 'REG_TimeVariant    = true' in fuse_text:
    pass
elif 'REG_TimeVariant = true' not in fuse_text:
    fail("Fuse must be time variant")
if 'DVIPComputeNode(req, "HumanPOVKernel"' not in fuse_text:
    fail("GPU compute path not found")
if "HumanPOV_1 = HumanPOV" not in setting_text:
    fail("Edit effect does not instantiate HumanPOV")

fuse_inputs = set(re.findall(r'add_(?:number|checkbox)\("[^"]+",\s*"([A-Za-z0-9_]+)"', fuse_text))
fuse_inputs.update(re.findall(r'self:AddInput\("[^"]+",\s*"([A-Za-z0-9_]+)"', fuse_text))
setting_sources = set(re.findall(r'Source = "([A-Za-z0-9_]+)"', setting_text))

ignored = {"Input", "Output"}
missing = sorted((setting_sources - ignored) - fuse_inputs)
if missing:
    fail("template references unknown Fuse inputs: " + ", ".join(missing))

for text, label in ((fuse_text, "Fuse"), (setting_text, "setting")):
    if text.count("{") != text.count("}"):
        fail(f"unbalanced braces in {label}")

resolve_lua = Path(
    "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/"
    "Fusion/libluajit-5.1.2.dylib"
)
if resolve_lua.is_file():
    lua = ctypes.CDLL(str(resolve_lua))
    lua.luaL_newstate.restype = ctypes.c_void_p
    lua.luaL_loadfile.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lua.luaL_loadfile.restype = ctypes.c_int
    lua.lua_tolstring.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_size_t),
    ]
    lua.lua_tolstring.restype = ctypes.c_char_p
    lua.lua_close.argtypes = [ctypes.c_void_p]
    state = lua.luaL_newstate()
    status = lua.luaL_loadfile(state, str(FUSE).encode("utf-8"))
    if status:
        size = ctypes.c_size_t()
        message = lua.lua_tolstring(state, -1, ctypes.byref(size))
        error = message[: size.value].decode("utf-8", errors="replace")
        lua.lua_close(state)
        fail("Resolve LuaJIT syntax error: " + error)
    lua.lua_close(state)

print("PASS: Human POV package structure and control references are valid")
