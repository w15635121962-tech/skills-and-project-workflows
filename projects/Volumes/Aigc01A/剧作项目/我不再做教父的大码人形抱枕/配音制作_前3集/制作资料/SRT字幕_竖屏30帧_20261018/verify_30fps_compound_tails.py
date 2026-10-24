#!/usr/bin/env python3
"""Offline-only DRT/source audit. Never connects to Resolve or modifies media."""
import argparse
import array
import concurrent.futures
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile


def xml_root(data):
    # Resolve's native XML contains C++ class tags such as ListMgt::LmVersionTable.
    # Normalize tag names only in memory so the standard XML reader can inspect it.
    text = data.decode("utf-8")
    text = re.sub(r"(<\/?)([A-Za-z_][\w:.-]*)", lambda m: m[1] + m[2].replace(":", "_"), text)
    return ET.fromstring(text)


def native_frame(text):
    integer, separator, fraction = (text or "0").partition("|")
    return float(integer or 0) + (struct.unpack("<d", bytes.fromhex(fraction))[0] if separator else 0)


def qbytearray(hex_string, key):
    data = bytes.fromhex(hex_string)
    encoded_key = key.encode("utf-16-be")
    pos = data.index(encoded_key) + len(encoded_key)
    assert int.from_bytes(data[pos:pos + 4], "big") == 12
    assert data[pos + 4] == 0
    length = int.from_bytes(data[pos + 5:pos + 9], "big")
    result = data[pos + 9:pos + 9 + length]
    assert len(result) == length
    return result


def varint(data, pos):
    value = shift = 0
    while True:
        octet = data[pos]
        pos += 1
        value |= (octet & 127) << shift
        if octet < 128:
            return value, pos
        shift += 7
        assert shift < 70


def timemap_endpoint(clip):
    data = qbytearray(clip.findtext("MediaTimemapBA"), "KeyframesBA")
    points, pos = [], 0
    while pos < len(data):
        tag, pos = varint(data, pos)
        field, wire = tag >> 3, tag & 7
        if wire == 0:
            _, pos = varint(data, pos)
        elif wire == 2:
            length, pos = varint(data, pos)
            payload = data[pos:pos + length]
            pos += length
            if field == 1:
                assert len(payload) == 18 and payload[0] == 9 and payload[9] == 17
                points.append((struct.unpack("<d", payload[1:9])[0], struct.unpack("<d", payload[10:18])[0]))
        else:
            raise ValueError((field, wire))
    assert len(points) == 1, "Only an origin plus one linear endpoint is supported"
    return points[0]


def dbfs(amplitude):
    return 20 * math.log10(amplitude) if amplitude else None


def metrics(samples, start, end):
    values = samples[max(0, start):max(0, end)]
    if not values:
        return {"sample_count": 0, "peak_dbfs": None, "rms_dbfs": None, "above_minus60_count": 0}
    peak = max(abs(v) for v in values)
    rms = math.sqrt(math.fsum(v * v for v in values) / len(values))
    return {"sample_count": len(values), "peak_dbfs": dbfs(peak), "rms_dbfs": dbfs(rms),
            "above_minus60_count": sum(abs(v) > 0.001 for v in values)}


def decode_and_measure(row):
    path = row["source_path"]
    probe = json.loads(subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=sample_rate,channels", "-of", "json", path]))
    info = probe["streams"][0]
    assert int(info["channels"]) == 1, "Expected original mono voice file"
    rate = int(info["sample_rate"])
    decoded = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-map", "0:a:0", "-f", "f32le", "-acodec", "pcm_f32le", "pipe:1"])
    samples = array.array("f")
    samples.frombytes(decoded)
    if sys.byteorder != "little":
        samples.byteswap()
    source_end = row["calculated_source_end_seconds"]
    cutoff = min(len(samples), max(0, math.floor(source_end * rate)))
    tail = metrics(samples, cutoff, len(samples))
    after_one = min(len(samples), max(0, math.floor((source_end + row["speed_ratio"] / row["timeline_fps"]) * rate)))
    last_active = next((i for i in range(len(samples) - 1, cutoff - 1, -1) if abs(samples[i]) > 0.001), None)
    needed = 0 if last_active is None else max(1, math.ceil(((last_active + 1) / rate - source_end) / row["speed_ratio"] * row["timeline_fps"]))
    row.update({"source_sample_rate": rate, "source_decoded_sample_count": len(samples),
                "source_decoded_duration_seconds": len(samples) / rate,
                "uncovered_tail_seconds": max(0, len(samples) / rate - source_end),
                "tail_start_sample_floor_conservative": cutoff, "uncovered_tail": tail,
                "tail_if_extended_one_timeline_frame": metrics(samples, after_one, len(samples)),
                "last_above_minus60_sample_end_seconds_in_tail": None if last_active is None else (last_active + 1) / rate,
                "minimum_extra_timeline_frames_to_cover_above_minus60_tail": needed,
                "needs_tail_review": bool(tail["above_minus60_count"])})
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, default=Path(__file__).with_name("30fps竖屏实际时间线快照.json"))
    parser.add_argument("--manifest", type=Path, default=Path(__file__).parent.parent / "已下载音频清单.json")
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("30fps六时间线47复合源绑定速度及尾音核验.json"))
    args = parser.parse_args()
    assert not args.output.exists(), "Refusing to overwrite an existing audit"
    snapshot = json.loads(args.snapshot.read_text())
    manifest = json.loads(args.manifest.read_text())
    by_path = {str(Path(c["local_path"]).resolve()): c for c in manifest["clips"]}
    rows, timelines = [], []
    for timeline in snapshot["timelines"]:
        fps = float(timeline["fps"])
        assert fps == 30 and timeline["width"] == "1080" and timeline["height"] == "1920"
        current = {c["name"]: c for track in timeline["audio_tracks"] for c in track["items"]}
        drt = Path(timeline["drt_path"])
        with zipfile.ZipFile(drt) as archive:
            pool = xml_root(archive.read("MediaPool/Master/MpFolder.xml"))
            media = {c.get("DbId"): c for c in pool.findall("./MediaVec/Element/*")}
            sequences = {Path(n).stem: xml_root(archive.read(n)) for n in archive.namelist() if n.startswith("SeqContainer/")}
            matches = [(key, root) for key, root in sequences.items() if {c.findtext("Name") for c in root.findall(".//Sm2TiAudioClip")} == set(current)]
            assert len(matches) == 1
            main_id, main_sequence = matches[0]
            timeline_rows = []
            for clip in main_sequence.findall(".//Sm2TiAudioClip"):
                item = current[clip.findtext("Name")]
                assert native_frame(clip.findtext("MediaStartTime")) == 0 and item["left_offset"] == 0
                duration = native_frame(clip.findtext("Duration"))
                assert abs(duration - (item["end"] - item["start"])) < 1e-7
                compound = media[clip.findtext("MediaRef")]
                assert compound.tag == "Sm2MpCompoundClip"
                blob = bytes.fromhex(compound.find("./Sequence/Sm2Sequence/FieldsBlob").text)
                child_ids = [key for key in sequences if key.encode("utf-16-be") in blob or key.encode() in blob]
                assert len(child_ids) == 1
                children = sequences[child_ids[0]].findall(".//Sm2TiAudioClip")
                assert len(children) == 1
                child = children[0]
                assert native_frame(child.findtext("MediaStartTime")) == 0
                original = media[child.findtext("MediaRef")]
                assert original.tag == "Sm2MpAudioClip"
                source = Path(child.findtext("MediaFilePath")).resolve()
                expected = by_path[str(source)]
                assert str(source) == str(Path(item["expected_original_mp3_path"]).resolve())
                digest = hashlib.sha256(source.read_bytes()).hexdigest()
                assert digest == expected["sha256"]
                endpoint_time, endpoint_source = timemap_endpoint(clip)
                speed = endpoint_source / endpoint_time
                assert abs(speed - 1.1) < 1e-6
                row = {"timeline_name": timeline["name"], "timeline_id": timeline["id"], "timeline_fps": fps,
                       "name": clip.findtext("Name"), "item_id": item["id"], "drt_clip_dbid": clip.get("DbId"), "start_frame": item["start"],
                       "end_frame": item["end"], "duration_frames": duration, "duration_seconds": duration / fps,
                       "old_24fps_duration_seconds": (item["reference_24fps_end"] - item["reference_24fps_start"]) / 24,
                       "compound_id": compound.get("DbId"), "child_container_id": child_ids[0],
                       "original_media_id": original.get("DbId"), "source_path": str(source), "source_sha256": digest,
                       "manifest_sha256_matches": True, "native_timemap_endpoint_seconds": [endpoint_time, endpoint_source],
                       "speed_ratio": speed, "calculated_source_start_seconds": 0,
                       "calculated_source_end_seconds": duration / fps * speed}
                row["resample_duration_delta_ms"] = (row["duration_seconds"] - row["old_24fps_duration_seconds"]) * 1000
                timeline_rows.append(row)
            timeline_rows.sort(key=lambda c: c["start_frame"])
            gaps = [b["start_frame"] - a["end_frame"] for a, b in zip(timeline_rows, timeline_rows[1:])]
            assert all(g > -1e-7 for g in gaps), gaps
            timelines.append({"name": timeline["name"], "id": timeline["id"], "count": len(timeline_rows),
                              "drt_path": str(drt), "drt_sha256": hashlib.sha256(drt.read_bytes()).hexdigest(),
                              "main_container_id": main_id, "maximum_absolute_gap_frames": max(map(abs, gaps), default=0)})
            rows.extend(timeline_rows)
    assert len(rows) == len(manifest["clips"]) == 47
    assert len({r["source_path"] for r in rows}) == 47
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        rows = list(executor.map(decode_and_measure, rows))
    risks = [r for r in rows if r["needs_tail_review"]]
    report = {"scope": "Offline read-only native DRT plus original MP3 decode; no Resolve calls, new ASR, render or media changes",
              "snapshot_path": str(args.snapshot.resolve()), "snapshot_sha256": hashlib.sha256(args.snapshot.read_bytes()).hexdigest(),
              "manifest_sha256": hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
              "source_end_method": "Origin and MediaStartTime are 0; linear source end = actual native duration_frames / 30 * slope from MediaTimemapBA KeyframesBA. Inner MediaFrameRate/source frame integers are not interpreted as 24fps.",
              "tail_metric_method": "Decode original mono MP3 via ffmpeg to native-rate float32 PCM in memory. Tail starts at floor(source_end * sample_rate), conservatively including at most one boundary sample. Amplitude reference 1.0; threshold abs(sample)>0.001 (-60 dBFS). Null dBFS denotes empty or zero-energy window.",
              "timeline_count": len(timelines), "clip_count": len(rows), "all_source_paths_hashes_and_linear_110_verified": True,
              "speed_range_percent": [min(r["speed_ratio"] * 100 for r in rows), max(r["speed_ratio"] * 100 for r in rows)],
              "tail_risk_threshold_dbfs": -60, "tail_risk_count": len(risks),
              "tail_risks": [{k: r[k] for k in ["timeline_name", "name", "item_id", "start_frame", "end_frame", "calculated_source_end_seconds", "uncovered_tail_seconds", "uncovered_tail", "minimum_extra_timeline_frames_to_cover_above_minus60_tail", "tail_if_extended_one_timeline_frame"]} for r in risks],
              "timelines": timelines, "clips": rows,
              "limitation": "Energy above threshold is a tail-review flag, not a word/content classification. Preserve pitch is not independently decoded here."}
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": str(args.output.resolve()), "timeline_count": len(timelines), "clip_count": len(rows),
                      "speed_range_percent": report["speed_range_percent"], "tail_risk_count": len(risks), "tail_risks": report["tail_risks"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
