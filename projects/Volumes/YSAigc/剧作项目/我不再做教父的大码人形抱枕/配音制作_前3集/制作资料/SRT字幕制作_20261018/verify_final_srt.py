#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only verification of the six final SRTs; writes a separate JSON record."""

from pathlib import Path
import argparse
import datetime
import difflib
import hashlib
import json
import re


HERE = Path(__file__).resolve().parent
TIMESTAMP = re.compile(r"^(\d{2,}):([0-5]\d):([0-5]\d),(\d{3})$")
WORD = re.compile(r"[^\W_]+(?:['’][^\W_]+)*", re.UNICODE)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def words(text):
    return [w.casefold().replace("’", "'") for w in WORD.findall(text)]


def compact(text):
    return " ".join(text.split())


def milliseconds(value):
    match = TIMESTAMP.fullmatch(value)
    if not match:
        raise ValueError(f"Invalid SRT timestamp: {value!r}")
    h, m, s, ms = map(int, match.groups())
    return ((h * 60 + m) * 60 + s) * 1000 + ms


def parse_srt(path):
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    if "\u2028" in text or "\u2029" in text:
        raise ValueError("SRT contains native Unicode line separators")
    result = []
    for ordinal, block in enumerate(re.split(r"\n[ \t]*\n", text.strip()), 1):
        lines = block.split("\n")
        if len(lines) < 3 or lines[0] != str(ordinal):
            raise ValueError(f"Invalid/unsorted cue index at block {ordinal}")
        times = lines[1].split(" --> ")
        if len(times) != 2:
            raise ValueError(f"Invalid timing line at cue {ordinal}")
        start, end = map(milliseconds, times)
        body = lines[2:]
        if start < 0 or end <= start or not compact(" ".join(body)):
            raise ValueError(f"Empty/nonpositive cue {ordinal}")
        if any(not line.strip() for line in body):
            raise ValueError(f"Empty body line at cue {ordinal}")
        result.append({"index": ordinal, "start_ms": start, "end_ms": end,
                       "lines": body, "text": compact(" ".join(body))})
    return result, raw


def allowed_native_text(text, key):
    """Explicitly enumerated editorial corrections, independent of final cue JSON."""
    replacements = [(r"\bMateo\b", "Matteo"),
                    (r"\bBellendi\b", "Bellandi"),
                    (r"\bBelandi\b", "Bellandi"),
                    (r"\bBelandis\b", "Bellandis")]
    if key == "F01":
        replacements += [(r"\bDonmeter\b", "don Matteo"),
                         (r"\bblack tea\b", "black tee")]
    if key == "F03":
        replacements += [(r"\bBelandia State\b", "Bellandi estate"),
                         (r"\bfeel nothing from me\b", "feel nothing for me")]
    if key == "M02":
        replacements += [(r"\bVictoria\b", "Vittoria")]
    if key == "M03":
        replacements += [(r"\bBlackwood Air\b", "Blackwood heir")]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def timeline_key(name):
    return ("M" if "性转" in name else "F") + re.search(r"_EP(\d+)_", name).group(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "最终SRT独立核验.json")
    args = parser.parse_args()
    report_path = HERE / "SRT字幕校正与时间核验.json"
    snapshot_path = HERE / "字幕制作前快照.json"
    reference_path = HERE.parent / "音频内容与顺序核验_20261018" / "SRT校正_47条原音频词时间与原文对照.json"
    corrected = load(report_path)
    snapshots = {t["id"]: t for t in load(snapshot_path)["timelines"]}
    references = load(reference_path)["clips"]
    native = {}
    inputs = [report_path, snapshot_path, reference_path]
    for path in sorted(HERE.glob("原生生成_*.json")):
        data = load(path)
        native[data["id"]] = data
        inputs.append(path)
    input_before = {str(p): digest(p) for p in inputs}
    failures = []

    def require(condition, label, detail):
        if not condition:
            failures.append({"check": label, "detail": detail})
        return bool(condition)

    results = []
    by_key = {}
    for timeline in corrected["timelines"]:
        key = timeline_key(timeline["timeline_name"])
        srt_path = Path(timeline["srt_path"])
        inputs.append(srt_path)
        input_before[str(srt_path)] = digest(srt_path)
        try:
            cues, _ = parse_srt(srt_path)
        except (UnicodeError, ValueError) as exc:
            failures.append({"check": "strict_srt_parse", "path": str(srt_path), "detail": str(exc)})
            continue
        snapshot = snapshots[timeline["timeline_id"]]
        audio = [item for track in snapshot["audio_tracks"] for item in track["items"]]
        native_cues = [c for tr in native[timeline["timeline_id"]]["tracks"] for c in tr["cues"]]
        fps = float(snapshot["fps"])
        raw_native = compact(" ".join(c["text"] for c in native_cues))
        expected = words(allowed_native_text(raw_native, key))
        actual = words(" ".join(c["text"] for c in cues))
        diffs = [{"op": op, "expected": expected[a:b], "actual": actual[c:d]}
                 for op, a, b, c, d in difflib.SequenceMatcher(None, expected, actual, autojunk=False).get_opcodes()
                 if op != "equal"]
        require(not diffs, "entire_native_word_sequence_after_explicit_corrections", {"timeline": key, "diffs": diffs})
        require(len(cues) == len(timeline["cues"]) == timeline["final_cue_count"], "cue_counts", key)
        rows = []
        for i, cue in enumerate(cues):
            described = timeline["cues"][i] if i < len(timeline["cues"]) else None
            if i:
                require(cue["start_ms"] >= cues[i - 1]["end_ms"], "no_cue_overlap", {"timeline": key, "index": cue["index"]})
            require(1 <= len(cue["lines"]) <= 2 and all(len(line) <= 36 for line in cue["lines"]),
                    "double_line_max36", {"timeline": key, "index": cue["index"], "lines": cue["lines"]})
            require(cue["end_ms"] - cue["start_ms"] >= 800, "no_under_point8_flash_cue", {"timeline": key, "index": cue["index"]})
            # Half a millisecond allowance is solely for SRT rounding of exact frame values.
            containing = [a for a in audio
                          if cue["start_ms"] >= float(a["start"]) / fps * 1000 - 0.501
                          and cue["end_ms"] <= float(a["end"]) / fps * 1000 + 0.501]
            require(len(containing) == 1, "one_source_mp3_contains_entire_cue", {"timeline": key, "cue": cue, "containing": [a["name"] for a in containing]})
            if described:
                require(compact(described["text"]) == cue["text"], "srt_matches_correction_json_text", {"timeline": key, "index": cue["index"]})
                require(cue["start_ms"] == round(float(described["start"]) / fps * 1000)
                        and cue["end_ms"] == round(float(described["end"]) / fps * 1000),
                        "srt_matches_correction_json_frame_times", {"timeline": key, "index": cue["index"]})
                require(not containing or containing[0]["name"] == described["audio_name"],
                        "source_assignment_matches_independent_snapshot", {"timeline": key, "index": cue["index"]})
            rows.append({**cue, "source_mp3": containing[0]["name"] if len(containing) == 1 else None,
                         "native_indices": described["native_indices"] if described else None,
                         "start_frame_from_srt": cue["start_ms"] / 1000 * fps,
                         "end_frame_from_srt": cue["end_ms"] / 1000 * fps})
        result = {"key": key, "timeline_name": timeline["timeline_name"], "timeline_id": timeline["timeline_id"],
                  "srt_path": str(srt_path), "sha256": digest(srt_path), "fps": fps,
                  "native_cue_count": len(native_cues), "final_cue_count": len(cues),
                  "native_lexical_tokens": len(words(raw_native)), "expected_lexical_tokens_after_allowed_edits": len(expected),
                  "final_lexical_tokens": len(actual), "entire_word_sequence_equal": not diffs,
                  "word_sequence_diffs": diffs, "cues": rows}
        results.append(result)
        by_key[key] = result

    special = []

    def check_pair(key, left_text, right_text, frame, label):
        rows = by_key[key]["cues"]
        left = [c for c in rows if c["text"] == left_text]
        right = [c for c in rows if c["text"] == right_text]
        expected_ms = round(frame / 24 * 1000)
        ok = len(left) == len(right) == 1 and left[0]["end_ms"] == right[0]["start_ms"] == expected_ms
        require(ok, label, {"timeline": key, "left": left, "right": right, "expected_boundary_frame": frame})
        special.append({"check": label, "passed": ok, "timeline": key, "boundary_frame": frame,
                        "boundary_ms": expected_ms, "left": left, "right": right})

    check_pair("M01", "I'd never walk away.", "Until my 10-year contract with the Blackwoods ran out.", 499, "real_cross_source_split_male_ep1")
    check_pair("F03", "the Bellandi estate.", "Claiming to feel nothing for me,", 588, "real_cross_source_split_female_ep3_estate")
    check_pair("F03", "Just like every night before.", "At 18, Matteo was kidnapped by rivals and", 746, "real_cross_source_split_female_ep3_at18")
    check_pair("F01", "On renewal day, his mother slid me", "a half-pay contract, certain I wouldn't dare refuse.", 479, "half_pay_word_and_boundary")
    check_pair("F03", "As if that wasn't clear enough, he added.", "I closed my eyes and pretended to be asleep.", 316, "i_closed_word_and_boundary")

    merged = []
    for key, native_indices, tail in [("F02", [14, 15], "plushies."), ("M01", [18, 19], "yet."),
                                       ("M01", [24, 25], "me."), ("M01", [37, 38], "She thought it over."),
                                       ("M02", [4, 5], "I nodded."), ("M03", [17, 18], "in the corner.")]:
        matches = [c for c in by_key[key]["cues"] if c["native_indices"] == native_indices]
        ok = len(matches) == 1 and matches[0]["text"].endswith(tail) and matches[0]["end_ms"] - matches[0]["start_ms"] >= 800
        require(ok, "six_short_cues_merged_without_losing_tail", {"timeline": key, "native_indices": native_indices})
        merged.append({"timeline": key, "native_indices": native_indices, "passed": ok, "final_cues": matches})

    variants = [("F03", "that Bellandis"), ("F03", "the hallway corner"), ("M01", "she kicked"),
                ("M01", "desires still burning"), ("M02", "One leg tossed"), ("M03", "Madame Blackwood")]
    preserved = []
    for key, phrase in variants:
        text = " ".join(c["text"] for c in by_key[key]["cues"])
        ok = phrase in text
        require(ok, "native_disputed_word_retained", {"timeline": key, "phrase": phrase})
        preserved.append({"timeline": key, "phrase": phrase, "passed": ok})

    audio_integrity = []
    for clip in references:
        audio_path = Path(clip["audio_path"])
        actual_sha = digest(audio_path)
        ok = actual_sha == clip["audio_sha256"]
        require(ok, "original_mp3_sha_unchanged", str(audio_path))
        audio_integrity.append({"name": clip["name"], "path": str(audio_path), "expected_sha256": clip["audio_sha256"],
                                "current_sha256": actual_sha, "unchanged": ok})
    inputs_after = {str(path): digest(path) for path in inputs}
    require(input_before == inputs_after, "all_inputs_stable_during_verification", "Input digests changed during this run" if input_before != inputs_after else "stable")
    require(len(results) == 6 and sum(r["final_cue_count"] for r in results) == 160, "six_srt_160_cues", len(results))
    out = {"schema_version": 1, "checked_at": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
           "success": not failures, "failure_count": len(failures), "failures": failures,
           "method": "Strict independent SRT parse + native entire-word-order comparison under explicit allowed substitutions + actual 110% snapshot source boundaries + source SHA",
           "scope": "Only new QC JSON is written; original SRT/audio/Resolve/native captions are not modified; no new ASR or listening.",
           "timelines": results, "special_resegmentation_checks": special, "six_short_cue_merges": merged,
           "native_disputed_words_retained": preserved, "original_audio_integrity": audio_integrity,
           "inputs_sha256": inputs_after, "srt_rounding_tolerance_ms": 0.501,
           "limits": ["Two original ASR models share the Whisper family; subtitle edits do not establish pronunciation accuracy.",
                      "Native caption timing is already on the current 110 percent timeline; no second speed conversion is applied.",
                      "This checker establishes text order and source bounds, not human-confirmed phoneme-level timing or absence of all ASR errors."]}
    args.output.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"success": out["success"], "failure_count": len(failures), "failures": failures,
                      "timelines": len(results), "cues": sum(r["final_cue_count"] for r in results),
                      "audio_sha_checked": len(audio_integrity), "output": str(args.output)}, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
