#!/usr/bin/env python3
"""Copy only a subtitle-track EffectFiltersBA value into a new DRT archive.

Pure offline interchange preparation. No Resolve API, DB or media writes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import xml.etree.ElementTree as ET
import zipfile


def digest(data):
    return hashlib.sha256(data).hexdigest()


def keyed_spans(data):
    assert len(data) >= 8 and int.from_bytes(data[:4], "big") == 1
    count = int.from_bytes(data[4:8], "big")
    result, pos = [], 8
    for _ in range(count):
        start = pos
        size = int.from_bytes(data[pos:pos + 4], "big")
        pos += 4
        key = data[pos:pos + size].decode("utf-16-be")
        pos += size
        kind = int.from_bytes(data[pos:pos + 4], "big")
        subtype = data[pos + 4]
        pos += 5
        value_start = pos
        if kind == 1:
            pos += 1
        elif kind in (2, 3):
            pos += 4
        elif kind in (4, 5, 6):
            pos += 8
        elif kind in (10, 12):
            length = int.from_bytes(data[pos:pos + 4], "big")
            pos += 4
            if length != 0xffffffff:
                pos += length
        elif kind == 16:
            pos += 9
        else:
            raise ValueError((key, kind))
        assert pos <= len(data)
        result.append({"key": key, "kind": kind, "subtype": subtype, "start": start,
                       "value_start": value_start, "end": pos})
    assert pos == len(data)
    assert len({entry["key"] for entry in result}) == count
    return result


def find_track(archive):
    tracks = []
    for name in archive.namelist():
        if not name.startswith("SeqContainer/"):
            continue
        data = archive.read(name)
        # Limit the replacement to the subtitle-track vector, never audio/items.
        for vector in re.finditer(rb"<SubtitleTrackVec>.*?</SubtitleTrackVec>", data, re.S):
            for match in re.finditer(rb"<Sm2TiTrack\b[^>]*>.*?</Sm2TiTrack>", vector.group(), re.S):
                track_data = match.group()
                root = ET.fromstring(track_data)
                assert root.findtext("Type") == "2"
                field = re.search(rb"<FieldsBlob>([0-9a-fA-F]+)</FieldsBlob>", track_data)
                assert field
                tracks.append({"entry": name, "track_id": root.get("DbId"),
                               "track_name": root.findtext("UserDefinedName"),
                               "caption_count": len(root.findall("./Items/Element/*")),
                               "blob": bytes.fromhex(field[1].decode()),
                               "hex_start": vector.start() + match.start() + field.start(1),
                               "hex_end": vector.start() + match.start() + field.end(1)})
    assert len(tracks) == 1, "Expected exactly one subtitle track in the entire DRT"
    return tracks[0]


def prepare(reference, source_path, output_path):
    assert source_path.resolve() != output_path.resolve()
    assert not output_path.exists(), "Refusing to overwrite an existing DRT"
    with zipfile.ZipFile(reference) as archive:
        reference_track = find_track(archive)
    source_style = next(s for s in keyed_spans(reference_track["blob"]) if s["key"] == "EffectFiltersBA")
    assert source_style["kind"] == 12 and source_style["subtype"] == 0
    # Copy the full typed BYTE value, including its length and original zstd envelope.
    style_value = reference_track["blob"][source_style["value_start"]:source_style["end"]]
    style_envelope = style_value[4:]
    assert int.from_bytes(style_value[:4], "big") == len(style_envelope) == 236
    assert digest(style_envelope) == "59efe5e6a040f91c48f4f9b8cb255fdd2946189910db775cbda110971c6df739"
    with zipfile.ZipFile(source_path) as archive:
        target = find_track(archive)
        assert target["caption_count"] > 0, "Refusing an export without the final captions"
        spans = keyed_spans(target["blob"])
        existing = next((s for s in spans if s["key"] == "EffectFiltersBA"), None)
        if existing:
            assert existing["kind"] == 12 and existing["subtype"] == 0
            edited = target["blob"][:existing["value_start"]] + style_value + target["blob"][existing["end"]:]
        else:
            entry = reference_track["blob"][source_style["start"]:source_style["end"]]
            edited = target["blob"][:4] + struct.pack(">I", len(spans) + 1) + target["blob"][8:] + entry
        edited_spans = keyed_spans(edited)
        for before in spans:
            if before["key"] == "EffectFiltersBA":
                continue
            after = next(s for s in edited_spans if s["key"] == before["key"])
            assert target["blob"][before["start"]:before["end"]] == edited[after["start"]:after["end"]]
        entry_data = archive.read(target["entry"])
        edited_entry = entry_data[:target["hex_start"]] + edited.hex().encode() + entry_data[target["hex_end"]:]
        # Every character outside this one FieldsBlob value remains untouched.
        assert entry_data[:target["hex_start"]] == edited_entry[:target["hex_start"]]
        assert entry_data[target["hex_end"]:] == edited_entry[target["hex_start"] + len(edited.hex()):]
        with zipfile.ZipFile(output_path, "w") as output:
            for entry in archive.infolist():
                output.writestr(entry, edited_entry if entry.filename == target["entry"] else archive.read(entry.filename))
            output.comment = archive.comment
    with zipfile.ZipFile(source_path) as before, zipfile.ZipFile(output_path) as after:
        assert before.namelist() == after.namelist()
        changed = [name for name in before.namelist() if before.read(name) != after.read(name)]
        assert changed in ([], [target["entry"]])
        verified = find_track(after)
        assert verified["caption_count"] == target["caption_count"]
        assert verified["track_id"] == target["track_id"]
        found = next(s for s in keyed_spans(verified["blob"]) if s["key"] == "EffectFiltersBA")
        assert verified["blob"][found["value_start"]:found["end"]] == style_value
    return {"input_drt": str(source_path.resolve()), "input_sha256": digest(source_path.read_bytes()),
            "output_drt": str(output_path.resolve()), "output_sha256": digest(output_path.read_bytes()),
            "reference_drt": str(reference.resolve()), "reference_style_sha256": digest(style_envelope),
            "reference_style_bytes": len(style_envelope), "changed_archive_entries": changed,
            "changed_field": "SubtitleTrackVec/Element/Sm2TiTrack/FieldsBlob keyed-dict EffectFiltersBA value only",
            "track_id_preserved": True, "nonstyle_key_entries_byte_identical": True,
            "all_caption_text_timing_and_other_track_bytes_identical": True,
            "all_audio_compounds_sources_timemaps_mix_and_other_archive_entries_byte_identical": True,
            "caption_count": target["caption_count"], "track_name_preserved": target["track_name"],
            "imported_into_resolve": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.reference, args.input, args.output), ensure_ascii=False, indent=2))
