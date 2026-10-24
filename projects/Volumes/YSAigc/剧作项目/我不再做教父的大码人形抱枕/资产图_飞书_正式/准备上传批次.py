#!/usr/bin/env python3
"""核验全部下载完成后，按来源顺序准备剧梦上传批次；不上传。"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "逐张下载命名清单.json"
CATEGORY_COUNTS = {"角色": 36, "场景": 32, "道具": 16}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inside_root(path: Path) -> bool:
    return path.resolve().is_relative_to(ROOT)


def main() -> None:
    source = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if source.get("downloads_complete") is not True:
        raise SystemExit("下载清单尚未标记 downloads_complete=true，未创建批次。")
    assets = source["assets"]
    if len(assets) != 84 or [a["index"] for a in assets] != list(range(1, 85)):
        raise SystemExit("来源资产必须为顺序完整的 01–84。")
    if len({a["local_asset_name"] for a in assets}) != 84:
        raise SystemExit("资产名称存在重复。")

    batch_root = ROOT / "上传批次"
    plans = []
    sequence = 0
    for category, expected_count in CATEGORY_COUNTS.items():
        selected = sorted(
            (a for a in assets if a["category"] == category),
            key=lambda a: a["index"],
        )
        if len(selected) != expected_count:
            raise SystemExit(f"{category} 数量不是 {expected_count}。")
        for offset in range(0, len(selected), 10):
            sequence += 1
            chunk = selected[offset : offset + 10]
            folder = batch_root / f"{sequence:02d}_{category}_{len(chunk):02d}张"
            entries = []
            for asset in chunk:
                path = Path(asset["local_path"])
                if not path.is_absolute() or not inside_root(path):
                    raise SystemExit(f"输入文件超出正式资产目录：{path}")
                if not path.is_file() or path.parent != ROOT / category:
                    raise SystemExit(f"输入文件不存在或分类目录不符：{path}")
                data = path.read_bytes()
                extension = ".png" if data.startswith(b"\x89PNG\r\n\x1a\n") else (
                    ".jpg" if data.startswith(b"\xff\xd8\xff") else None
                )
                if extension is None:
                    raise SystemExit(f"文件格式无法识别：{path}")
                expected_name = asset["local_asset_name"] + extension
                if path.name != expected_name or asset["filename"] != expected_name:
                    raise SystemExit(f"资产名称或真实扩展名不一致：{path}")
                if len(data) != asset["bytes"] or digest(path) != asset["sha256"]:
                    raise SystemExit(f"源文件大小或 SHA 校验失败：{path}")
                destination = folder / expected_name
                if not inside_root(destination):
                    raise SystemExit("输出路径超出正式资产目录。")
                if destination.exists() and (
                    not destination.is_file() or digest(destination) != asset["sha256"]
                ):
                    raise SystemExit(f"已有输出与源文件不一致，未覆盖：{destination}")
                entries.append({
                    "source_index": asset["index"],
                    "asset_name": asset["local_asset_name"],
                    "filename": expected_name,
                    "source_path": str(path),
                    "upload_path": str(destination),
                    "sha256": asset["sha256"],
                    "bytes": asset["bytes"],
                    "platform_uploaded": False,
                })
            plans.append({
                "batch_number": sequence,
                "category": category,
                "folder": str(folder),
                "count": len(entries),
                "assets": entries,
            })
    if len(plans) != 10 or sum(p["count"] for p in plans) != 84:
        raise SystemExit("批次数量或总数校验失败。")

    # 所有输入与已有目标先核验，再开始创建及复制；不修改来源图和下载日志。
    for batch in plans:
        Path(batch["folder"]).mkdir(parents=True, exist_ok=True)
        for asset in batch["assets"]:
            destination = Path(asset["upload_path"])
            if not destination.exists():
                shutil.copy2(asset["source_path"], destination)
            if digest(destination) != asset["sha256"]:
                raise SystemExit(f"复制后的 SHA 校验失败：{destination}")

    result = {
        "source_manifest": str(MANIFEST),
        "download_complete_verified": True,
        "count": 84,
        "batch_count": 10,
        "category_counts": CATEGORY_COUNTS,
        "ordering": "分类顺序为角色、场景、道具；每类按飞书 source_index 递增，每批至多10张。",
        "naming": "文件主体保持剧梦提示词中的标准资产名称，扩展名按实际 PNG/JPEG 格式。",
        "platform_uploaded": False,
        "generation_submitted": False,
        "batches": plans,
    }
    output = batch_root / "上传清单.json"
    temporary = batch_root / ".上传清单.json.tmp"
    temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(output)
    print(json.dumps({"status": "prepared", "count": 84, "batch_count": 10,
                      "manifest": str(output), "platform_uploaded": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
