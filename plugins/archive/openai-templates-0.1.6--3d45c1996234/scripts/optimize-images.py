"""Optimize template images while preserving PNG dimensions and alpha support.

Run with Pillow installed and pngquant on PATH. The output directory is separate
from the input so original assets remain available for visual comparison.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import posixpath
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote
from zipfile import ZIP_DEFLATED, ZipFile

from PIL import Image


def optimize_image(raw: bytes, quality: int, edge: int, pngquant: str) -> tuple[bytes, str | None]:
    try:
        image = Image.open(io.BytesIO(raw))
        image.load()
    except (OSError, ValueError):
        return raw, None
    mime = Image.MIME.get(image.format)
    if len(raw) <= 50_000:
        return raw, mime
    has_alpha = ("A" in image.getbands() and image.getchannel("A").getextrema()[0] < 255) or (
        image.mode == "P" and "transparency" in image.info
    )
    if has_alpha:
        lossless = io.BytesIO()
        image.save(lossless, format="PNG", optimize=True)
        candidates = [raw, lossless.getvalue()]
        quantized = subprocess.run(
            [pngquant, "--quality=70-95", "--speed=4", "--output", "-", "-"],
            input=lossless.getvalue(),
            capture_output=True,
            check=False,
        )
        if quantized.returncode == 0:
            optimized = Image.open(io.BytesIO(quantized.stdout))
            assert optimized.size == image.size
            if "transparency" in optimized.info or "A" in optimized.getbands():
                candidates.append(quantized.stdout)
        elif quantized.returncode != 99:
            raise RuntimeError(quantized.stderr.decode(errors="replace"))
        return min(candidates, key=len), "image/png"
    photo = image.convert("RGB")
    photo.thumbnail((edge, edge), Image.Resampling.LANCZOS)
    output = io.BytesIO()
    photo.save(output, format="JPEG", quality=quality, subsampling=0, optimize=True)
    candidate = output.getvalue()
    return (candidate, "image/jpeg") if len(candidate) < len(raw) else (raw, mime)


def optimize_pptx(source: Path, target: Path, optimize) -> None:
    with ZipFile(source) as archive:
        files = {info.filename: archive.read(info) for info in archive.infolist()}
    changed_types = {}
    renamed = {}
    for name, raw in list(files.items()):
        if not name.startswith("ppt/media/"):
            continue
        optimized, mime = optimize(raw)
        target_name = name
        if mime == "image/jpeg" and not name.lower().endswith((".jpg", ".jpeg")):
            target_name = name.rsplit(".", 1)[0] + "-optimized.jpg"
            if target_name in files:
                raise ValueError(f"Media rename collision: {target_name}")
            renamed[name] = target_name
            del files[name]
        files[target_name] = optimized
        if mime and (optimized != raw or target_name != name):
            changed_types["/" + target_name] = mime

    # Update relationships wherever media is used: slides, layouts, and masters.
    rel_namespace = "http://schemas.openxmlformats.org/package/2006/relationships"
    ET.register_namespace("", rel_namespace)
    for name in list(files):
        if not name.endswith(".rels"):
            continue
        root = ET.fromstring(files[name])
        owner_directory = posixpath.dirname(posixpath.dirname(name))
        changed = False
        for relationship in root:
            if relationship.attrib.get("TargetMode") == "External":
                continue
            rel_target = unquote(relationship.attrib.get("Target", ""))
            resolved = posixpath.normpath(posixpath.join(owner_directory, rel_target)).lstrip("/")
            if resolved in renamed:
                relationship.set("Target", posixpath.relpath(renamed[resolved], owner_directory))
                changed = True
        if changed:
            files[name] = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    content_types = ET.fromstring(files["[Content_Types].xml"])
    ET.register_namespace("", "http://schemas.openxmlformats.org/package/2006/content-types")
    namespace = "{http://schemas.openxmlformats.org/package/2006/content-types}"
    for node in content_types:
        part = node.attrib.get("PartName", "").lstrip("/")
        if part in renamed:
            node.set("PartName", "/" + renamed[part])
    overrides = {child.attrib.get("PartName"): child for child in content_types}
    for name, mime in changed_types.items():
        node = overrides.get(name)
        if node is None:
            node = ET.SubElement(content_types, namespace + "Override", PartName=name)
        node.set("ContentType", mime)
    files["[Content_Types].xml"] = ET.tostring(
        content_types, encoding="utf-8", xml_declaration=True
    )
    if "docProps/core.xml" in files:
        metadata = ET.fromstring(files["docProps/core.xml"])
        for node in metadata.iter():
            if node.tag.rsplit("}", 1)[-1] in {
                "creator",
                "lastModifiedBy",
                "created",
                "modified",
                "lastPrinted",
                "revision",
            }:
                node.text = None
        files["docProps/core.xml"] = ET.tostring(metadata, encoding="utf-8", xml_declaration=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(target, "w", compression=ZIP_DEFLATED) as archive:
        for name, raw in files.items():
            archive.writestr(name, raw)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--jpeg-quality", type=int, default=85)
    parser.add_argument("--photo-max-edge", type=int, default=1440)
    parser.add_argument("--pngquant", default="pngquant")
    parser.add_argument("--raw-images", action="store_true")
    parser.add_argument("--image-index", type=Path, required=True)
    args = parser.parse_args()
    index = {}
    cache = args.image_index.parent / "optimized-images"
    cache.mkdir(parents=True, exist_ok=True)

    def optimize(raw):
        digest = hashlib.sha256(raw).hexdigest()
        if digest not in index:
            optimized, mime = optimize_image(
                raw, args.jpeg_quality, args.photo_max_edge, args.pngquant
            )
            target = cache / digest
            target.write_bytes(optimized)
            index[digest] = {
                "path": str(target),
                "mime": mime,
                "sourceBytes": len(raw),
                "bytes": len(optimized),
            }
        item = index[digest]
        return Path(item["path"]).read_bytes(), item["mime"]

    if args.input.is_file():
        optimize_pptx(args.input, args.output, optimize)
    else:
        for source in sorted(args.input.rglob("*")):
            if source.is_file():
                target = args.output / source.relative_to(args.input)
                if source.suffix.lower() == ".pptx":
                    optimize_pptx(source, target, optimize)
                else:
                    optimized = (
                        optimize(source.read_bytes())[0] if args.raw_images else source.read_bytes()
                    )
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(optimized)
    args.image_index.write_text(json.dumps(index, indent=2) + "\n")


if __name__ == "__main__":
    main()
