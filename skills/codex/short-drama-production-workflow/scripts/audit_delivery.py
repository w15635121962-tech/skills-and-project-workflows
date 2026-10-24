#!/usr/bin/env python3
"""Read-only SRT/adopted-media checks. No app, network or media decoding calls."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

TIMING = re.compile(r"^(\d{2,}):(\d{2}):(\d{2}),(\d{3})\s+-->\s+(\d{2,}):(\d{2}):(\d{2}),(\d{3})$")


def compact(text):
    return re.sub(r"\s+", " ", text).strip()


def milliseconds(values):
    h, m, s, ms = map(int, values)
    if m >= 60 or s >= 60:
        raise ValueError("minute/second outside 0..59")
    return ((h * 60 + m) * 60 + s) * 1000 + ms


def check_srt(path, max_lines, expected_path=None):
    report = {"kind": "srt", "path": str(path.resolve()), "errors": [], "warnings": [], "cue_count": 0}
    content = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").strip()
    if not content:
        report["errors"].append("empty SRT")
        return report
    blocks = re.split(r"\n[ \t]*\n", content)
    texts, parsed = [], []
    for position, block in enumerate(blocks, 1):
        lines = block.splitlines()
        if len(lines) < 3:
            report["errors"].append(f"block {position}: missing number, timing or text")
            continue
        if lines[0].strip() != str(position):
            report["errors"].append(f"block {position}: expected sequential cue number {position}")
        match = TIMING.fullmatch(lines[1].strip())
        if not match:
            report["errors"].append(f"block {position}: invalid SRT timecode")
            continue
        try:
            start, end = milliseconds(match.groups()[:4]), milliseconds(match.groups()[4:])
        except ValueError as exc:
            report["errors"].append(f"block {position}: {exc}")
            continue
        if end <= start:
            report["errors"].append(f"block {position}: non-positive duration")
        if len(lines[2:]) > max_lines:
            report["errors"].append(f"block {position}: {len(lines[2:])} text lines exceeds {max_lines}")
        if not compact(" ".join(lines[2:])):
            report["errors"].append(f"block {position}: empty caption")
        if parsed and start < parsed[-1][0]:
            report["errors"].append(f"block {position}: starts before previous cue")
        if parsed and start < parsed[-1][1]:
            report["warnings"].append(f"block {position}: overlaps previous cue; review intended simultaneity")
        parsed.append((start, end))
        texts.append(" ".join(lines[2:]))
    report["cue_count"] = len(parsed)
    report["max_lines_allowed"] = max_lines
    if parsed:
        report["first_start_ms"], report["last_end_ms"] = parsed[0][0], parsed[-1][1]
    if expected_path:
        expected = compact(expected_path.read_text(encoding="utf-8-sig"))
        actual = compact(" ".join(texts))
        report["source_text_matches_ignoring_whitespace"] = actual == expected
        if actual != expected:
            report["errors"].append("caption text differs from expected source; no content was modified")
    report["not_checked"] = ["actual sound alignment", "native track insertion", "preset", "playback"]
    return report


def stable_id(value):
    text = str(value).strip()
    return str(int(text)) if text.isdigit() else text


def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def check_media(path):
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    items = payload.get("items") if isinstance(payload, dict) else None
    report = {"kind": "media-manifest", "path": str(path.resolve()), "errors": [], "warnings": [], "files": []}
    if not isinstance(items, list) or not items:
        report["errors"].append("manifest must contain a non-empty items array")
        return report
    adopted = set()
    for index, item in enumerate(items, 1):
        if not isinstance(item, dict):
            report["errors"].append(f"item {index}: expected object")
            continue
        selected = item.get("selected", True)
        if not isinstance(selected, bool):
            report["errors"].append(f"item {index}: selected must be true or false")
            continue
        if selected:
            if item.get("episode") is None or item.get("shot") is None:
                report["errors"].append(f"item {index}: selected media needs episode and shot/segment")
            key = (str(item.get("version", "")), stable_id(item.get("episode")), stable_id(item.get("shot")))
            if key in adopted:
                report["errors"].append(f"item {index}: multiple selected takes for {key}")
            adopted.add(key)
        raw_path = item.get("path")
        if not isinstance(raw_path, str) or not raw_path:
            report["errors"].append(f"item {index}: missing file path")
            continue
        media = Path(raw_path).expanduser()
        if not media.is_absolute():
            media = path.parent / media
        media = media.resolve()
        result = {"item": index, "path": str(media), "selected": selected}
        if not media.is_file():
            report["errors"].append(f"item {index}: file missing")
            report["files"].append(result)
            continue
        try:
            result["bytes"] = media.stat().st_size
            if result["bytes"] == 0:
                report["errors"].append(f"item {index}: empty file")
            expected = item.get("sha256")
            if expected is None:
                result["sha256_checked"] = False
                report["warnings"].append(f"item {index}: no expected SHA-256 supplied")
            elif not isinstance(expected, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected):
                report["errors"].append(f"item {index}: invalid SHA-256")
            else:
                actual = file_hash(media)
                result["sha256"] = actual
                result["sha256_matches"] = actual == expected.lower()
                if not result["sha256_matches"]:
                    report["errors"].append(f"item {index}: SHA-256 mismatch")
        except OSError as exc:
            report["errors"].append(f"item {index}: file read failed: {exc}")
        report["files"].append(result)
    report["selected_keys"] = len(adopted)
    report["not_checked"] = ["media decoding", "voice identity", "source text spoken", "listening quality", "timeline sync"]
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="kind", required=True)
    srt = sub.add_parser("srt")
    srt.add_argument("path", type=Path)
    srt.add_argument("--max-lines", type=int, default=3)
    srt.add_argument("--expected-text", type=Path)
    media = sub.add_parser("media-manifest")
    media.add_argument("path", type=Path)
    args = parser.parse_args()
    try:
        if args.kind == "srt":
            if args.max_lines < 1:
                raise ValueError("max-lines must be positive")
            report = check_srt(args.path, args.max_lines, args.expected_text)
        else:
            report = check_media(args.path)
    except (OSError, ValueError, TypeError) as exc:
        report = {"kind": args.kind, "errors": [str(exc)], "warnings": []}
    report["ok"] = not report["errors"]
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
