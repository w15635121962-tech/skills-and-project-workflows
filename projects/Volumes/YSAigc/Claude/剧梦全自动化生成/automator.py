#!/usr/bin/env python3
"""剧梦全自动化生成框架的安全骨架。平台操作默认 dry-run。"""
from __future__ import annotations
import argparse, json, re, uuid, hashlib
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def discover_doubao_output(cfg):
    dcfg = cfg.get("doubao", {})
    explicit = dcfg.get("output_path", "")
    if explicit and Path(explicit).exists():
        return Path(explicit)
    if not dcfg.get("auto_discover", True):
        return None
    root = Path(dcfg.get("output_dir", "/Users/zc/Doubao/chats"))
    candidates = [p for p in root.rglob("*.md") if "导演分镜" in p.name or "结构化结果" in p.name]
    return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None

def read_claude_split(path: Path | None):
    """Read Claude's local structural storyboard export without treating it as script fact."""
    if not path or not path.is_file():
        return {"status": "not_found", "path": "", "raw_sha256": "", "characters": 0, "split_units": []}
    raw = path.read_text(encoding="utf-8")
    units = list(dict.fromkeys(re.findall(r"\bEP\d+(?:[-_][A-Z]?\d+)*(?:[-_]S\d+)?\b", raw, re.I)))
    return {"status": "found", "path": str(path), "raw_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
            "characters": len(raw), "split_units": units, "source_note": "Claude output is a structural draft; verify against the source script."}

def read_doubao_design(path: Path | None):
    if not path or not path.exists():
        return {"status": "not_found", "path": "", "shots": [], "characters": [], "raw_sha256": ""}
    raw = path.read_text(encoding="utf-8")
    shots = []
    block_re = re.compile(r"^####\s+((?:EP\d+)-S\d+)\s*$([\s\S]*?)(?=^####\s+|^###\s+|\Z)", re.M)
    field_re = re.compile(r"^-\s*\*\*(.+?)\*\*[:：]\s*(.*)$", re.M)
    field_map = {"时长": "duration", "景别/机位": "camera", "画面构图": "composition", "角色走位": "blocking",
                 "戏内视线": "eyeline", "演员微表演": "performance", "对白与对白反应": "dialogue_reaction",
                 "道具连续性": "prop_continuity", "光影": "lighting", "音频": "audio",
                 "运动强度": "motion", "负面约束": "negative"}
    for match in block_re.finditer(raw):
        values = {field_map.get(k, k): v.strip() for k, v in field_re.findall(match.group(2))}
        values["id"] = match.group(1)
        values["episode"] = re.match(r"EP\d+", values["id"]).group(0)
        values["source"] = "doubao"
        shots.append(values)
    return {"status": "found", "path": str(path), "shots": shots,
            "raw_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
            "source_note": "Doubao output is a design draft and must be checked against the source script."}

def text_overlap(a: str, b: str):
    a, b = re.sub(r"\s", "", a), re.sub(r"\s", "", b)
    if not a or not b:
        return 0
    if a in b or b in a:
        return min(len(a), len(b))
    best = 0
    for size in range(min(12, len(a), len(b)), 3, -1):
        if any(a[i:i+size] in b for i in range(len(a) - size + 1)):
            best = size
            break
    return best

def match_doubao_design(text: str, doubao):
    ranked = sorted(((text_overlap(text, d.get("dialogue_reaction", "")), d) for d in doubao.get("shots", [])), key=lambda x: x[0], reverse=True)
    return ranked[0][1] if ranked and ranked[0][0] >= 4 else None

def narrative_story_design(text: str):
    """Create a story-action contract so a narration segment cannot become a static pose."""
    return {
        "story_progression": "把已审计剧本事实转成可见事件推进；镜内必须发生至少一次因果变化。",
        "pre_dialogue_state": "先展示人物当下目标、身体状态和空间关系，再让触发事件进入画面；不能一开始就站定说话。",
        "conflict": "明确人物想要什么、受到什么阻力，以及阻力如何迫使人物改变动作或位置。",
        "escalation": "通过接近/阻挡/夺取/保护/后退/失控等可见动作逐步升级，不用连续静态表情代替冲突。",
        "climax": "把信息揭示、关键动作或台词放在情绪与动作积累后的高潮点；说话者或被影响者必须可见。",
        "result": "台词或高潮之后必须留下结果性反应，并以新的稳定状态或下一镜的行动目标收尾。"
    }

def composition_parameters(camera_text="", shot_size="MS"):
    """Return concrete vertical-storyboard composition parameters from the supplied manual."""
    label = camera_text or ""
    if "OTS" in label.upper() or "过肩" in label or "内反打" in label:
        return {"shot_size": "OTS_MCU", "focal_length_mm": 65, "camera_height": "eye_level_minus_8cm",
                "axis": "A_side", "composition_ratio": {"foreground_subject_width_pct": 20, "focus_subject_height_pct": 48},
                "depth_of_field": "shallow_f2.0", "eyeline_offset_deg": 20, "foreground_occlusion": True}
    if "大特写" in label or "ECU" in label.upper():
        return {"shot_size": "ECU", "focal_length_mm": 100, "camera_height": "eye_level",
                "axis": "A_side", "composition_ratio": {"focus_subject_height_pct": 80, "headroom_pct": 3, "chin_room_pct": 2},
                "depth_of_field": "shallow_f1.8", "eyeline_offset_deg": 0, "foreground_occlusion": False}
    if "特写" in label or re.search(r"\bCU\b", label, re.I):
        return {"shot_size": "CU", "focal_length_mm": 65, "camera_height": "eye_level",
                "axis": "A_side", "composition_ratio": {"focus_subject_height_pct": 68, "headroom_pct": 7, "chin_room_pct": 6},
                "depth_of_field": "shallow_f2.0", "eyeline_offset_deg": 15, "foreground_occlusion": False}
    if "中近景" in label or re.search(r"\bMCU\b", label, re.I):
        return {"shot_size": "MCU", "focal_length_mm": 50, "camera_height": "eye_level",
                "axis": "A_side", "composition_ratio": {"focus_subject_height_pct": 50, "headroom_pct": 10, "chin_room_pct": 10},
                "depth_of_field": "medium_f2.8", "eyeline_offset_deg": 15, "foreground_occlusion": False}
    if "中全景" in label or re.search(r"\bMFS\b", label, re.I):
        return {"shot_size": "MFS", "focal_length_mm": 28, "camera_height": "eye_level",
                "axis": "A_side", "composition_ratio": {"focus_subject_height_pct": 25, "headroom_pct": 10, "chin_room_pct": 12},
                "depth_of_field": "medium_f4.0", "eyeline_offset_deg": 15, "foreground_occlusion": True}
    if "全景" in label or re.search(r"\bFS\b", label, re.I):
        return {"shot_size": "FS", "focal_length_mm": 24, "camera_height": "eye_level",
                "axis": "A_side", "composition_ratio": {"focus_subject_height_pct": 70, "headroom_pct": 10, "chin_room_pct": 10},
                "depth_of_field": "deep_f5.6", "eyeline_offset_deg": 0, "foreground_occlusion": True}
    return {"shot_size": shot_size, "focal_length_mm": 35, "camera_height": "eye_level",
            "axis": "A_side", "composition_ratio": {"focus_subject_height_pct": 35, "headroom_pct": 10, "chin_room_pct": 12},
            "depth_of_field": "medium_f2.8", "eyeline_offset_deg": 15, "foreground_occlusion": True}

def extract_original_dialogue(text: str):
    """Keep only quoted lines from the supplied English script, preserving wording."""
    found = []
    # Do not treat apostrophes in English contractions (don't, I'm, etc.) as quote delimiters.
    quote_re = re.compile(r'''[“"]([^”"]+)[”"]''')
    for line_no, raw in enumerate(text.splitlines(), 1):
        values = [v.strip() for v in quote_re.findall(raw) if v.strip()]
        if values:
            found.append({"line": line_no, "text": " ".join(values), "source": "original_english_script"})
    return found

def read_script(path: Path) -> str:
    if path.suffix.lower() == ".docx":
        from zipfile import ZipFile
        from xml.etree import ElementTree as ET
        with ZipFile(path) as z:
            xml = z.read("word/document.xml")
        root = ET.fromstring(xml)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        return "\n".join("".join(t.text or "" for t in p.findall(".//w:t", ns)) for p in root.findall(".//w:p", ns))
    return path.read_text(encoding="utf-8")

def infer_entities(text: str):
    known = ["Aria", "Hades", "Mia", "Leo", "Foster先生", "Foster夫人", "Blackwood家族", "Foster家族"]
    scenes = ["Blackwood庄园", "主卧", "恒温箱", "商场", "宴会厅", "加长黑色劳斯莱斯", "露台", "深渊之眼"]
    props = ["小黑蛇", "恒温箱", "生牛肉", "黑卡", "香槟杯", "红酒", "戒指", "禁忌残卷", "结界"]
    return {
      "characters": [{"name": n, "mentions": text.count(n)} for n in known if n in text],
      "scenes": [{"name": n, "mentions": text.count(n)} for n in scenes if n in text],
      "props": [{"name": n, "mentions": text.count(n)} for n in props if n in text],
      "worldview": {"genre": "现代超自然", "rules": ["远古神明可寄居黑蛇形态", "真爱之血与诅咒转移有关", "神力会造成形态与生命代价"], "confidence": "script-derived"},
      "social_background": "现代豪门联姻、阶层权力与家族继承秩序；为剧本推断，需人工确认",
      "character_design": {"Aria": "被长期压抑但观察敏锐，逐步建立边界与主动选择", "Hades": "外冷暴烈、对Aria极度保护并逐步学习人类边界", "Mia": "以宠爱和阶层优势维持控制，受挫后升级为报复", "Leo": "执行家族秩序，同时对Aria抱有复杂同情"}
    }

def extract_monologue(text: str, chars_per_second: float = 4.5):
    """Treat every non-dialogue narrative line as monologue and estimate duration."""
    entries = []
    dialogue_pattern = re.compile(r"[“”\"‘’']([^“”\"‘’']*)[”\"’']")
    skip_pattern = re.compile(r"^(?:EP\s*\d+|第\s*\d+\s*集|风格[:：].*|《.*》|[-—_\s]{4,})$", re.I)
    for line_no, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if (not line or skip_pattern.match(line) or
                (line.startswith("《") and line.endswith("》")) or
                line.startswith("【】里的") or
                line == "玻璃箱里的神明"):
            continue
        explicit = re.match(r"^\s*(?:独白|旁白|内心独白|V\.?O\.?|VO)\s*[:：]\s*(.+)$", line, re.I)
        value = explicit.group(1).strip() if explicit else dialogue_pattern.sub("", line).strip()
        value = re.sub(r"^[:：]\s*", "", value)
        if not value or value in {"画面", "场景", "镜头"}:
            continue
        chars = len(re.sub(r"\s|[，。！？；：、,.!?;:…—\-]", "", value))
        duration = max(1.0, round(chars / chars_per_second, 2))
        entries.append({"index": len(entries) + 1, "line": line_no, "text": value,
                        "characters": chars, "duration": duration,
                        "source": "local_narrative_as_monologue"})
    total = round(sum(e["duration"] for e in entries), 2)
    return {"speech_rate_chars_per_second": chars_per_second, "segments": entries,
            "total_duration": total, "mode": "all_non_dialogue_is_monologue",
            "status": "found" if entries else "not_found"}

def bind_assets(story, manifest, root: Path, required_character_names=None):
    items = manifest.get("assets", []) if manifest else []
    required_character_names = set(required_character_names or [])
    bindings, missing, prompt_completion = [], [], []
    for group in ("characters", "scenes", "props"):
        for entity in story[group]:
            hits = [a for a in items if a.get("name") == entity["name"] or entity["name"] in a.get("tags", [])]
            existing = [a for a in hits if (root / a.get("path", "")).exists()]
            record = {"entity": entity["name"], "category": group, "assets": existing, "status": "bound" if existing else "missing"}
            if existing:
                bindings.append(record)
            else:
                missing.append(record)
                if group in ("scenes", "props") or (group == "characters" and entity["name"] not in required_character_names):
                    prompt_completion.append({"entity": entity["name"], "category": group,
                                              "instruction": "参考图缺失或角色非主角，使用文字描述补全；保持身份、年龄、体型、服装意图和动作阶段稳定，设计保持中性、虚构、不可识别，不添加现实地名、建筑名称、警察标志、商标或Logo。"})
    return {"bindings": bindings, "missing": missing,
            "character_blockers": [m for m in missing if m["category"] == "characters" and m["entity"] in required_character_names],
            "prompt_completion": prompt_completion}

def storyboard(story, monologue=None, doubao=None, english_dialogue=None):
    if monologue and monologue.get("segments"):
        shots = []
        for segment in monologue["segments"]:
            remaining = segment["duration"]
            part = 1
            while remaining > 0:
                # Format C requires 1.0-6.0s shots. Fold a short tail into the
                # preceding shot so the local monologue timing remains exact.
                if remaining < 1.0 and shots and shots[-1].get("monologue_segment") == segment["index"]:
                    shots[-1]["duration"] = round(shots[-1]["duration"] + remaining, 2)
                    remaining = 0
                    break
                duration = min(4.0, remaining)
                design = match_doubao_design(segment["text"], doubao or {})
                story_design = narrative_story_design(segment["text"])
                english_for_segment = [d["text"] for d in (english_dialogue or []) if d["line"] == segment["line"]]
                comp = composition_parameters(design.get("camera", "") if design else "")
                shots.append({
                    "id": f"MONO{segment['index']:02d}-S{part:02d}", "duration": duration,
                    "task": "独白驱动分镜", "characters": [c["name"] for c in story["characters"][:1]],
                    "scene": story["scenes"][0]["name"] if story["scenes"] else "待确认场景",
                    "action": "将叙述中的触发事件、阻力和结果转成连续可见动作，避免纯人物状态，镜尾停在新的稳定终态",
                    "eyeline": "视线服务于独白对象；无对象时保持明确的内心视线方向",
                    "performance": "眼神、下颌、喉部、手指、肩颈和呼吸随独白情绪渐变",
                    "dialogue": "", "english_dialogue": " ".join(english_for_segment),
                    "monologue_segment": segment["index"],
                    "monologue_duration": segment["duration"], "asset_refs": [],
                    "doubao_design": design or {"source": "fallback", "reason": "no matching Doubao shot"},
                    **comp,
                    **story_design
                })
                if design:
                    shots[-1].update({"camera": design.get("camera", ""), "composition": design.get("composition", ""),
                                      "blocking": design.get("blocking", ""), "eyeline": design.get("eyeline", shots[-1]["eyeline"]),
                                      "performance": design.get("performance", shots[-1]["performance"]),
                                      "lighting": design.get("lighting", ""), "audio": design.get("audio", ""),
                                      "motion": design.get("motion", "")})
                remaining = round(remaining - duration, 2)
                part += 1
            if english_for_segment:
                shots[-1]["dialogue"] = shots[-1]["english_dialogue"]
        return {"model": "豆包2.1Turbo", "timing_source": "local_monologue",
                "axis": "每场戏独立建立180度轴线，连续镜头保持屏幕方向", "shots": shots}
    return {"model": "豆包2.1Turbo", "axis": "每场戏独立建立180度轴线，连续镜头保持屏幕方向", "shots": [
      {"id": "EP01-S01", "duration": 5, "task": "黑门关闭建立牺牲处境", "characters": ["Aria"], "scene": "Blackwood庄园", "action": "背后黑色大门沉重合拢，Aria肩背绷紧却不回头", "eyeline": "前方庄园内", "performance": "下颌收紧、手指攥住衣角，呼吸短促后强行稳定", "dialogue": "无", "asset_refs": ["character_aria"]},
      {"id": "EP01-S02", "duration": 5, "task": "恒温箱揭示联姻对象", "characters": ["Aria"], "scene": "主卧", "action": "镜头绕过Aria肩侧揭示中央恒温箱内的小黑蛇", "eyeline": "恒温箱内", "performance": "惊惧预备转为松弛，眉间展开，掌心贴上玻璃", "dialogue": "看来，你和我一样，都很孤单。", "asset_refs": ["character_aria"]},
      {"id": "EP07-S01", "duration": 5, "task": "真相形态转换与保护", "characters": ["Aria", "Hades"], "scene": "别墅客厅", "action": "暗金光芒散去，Hades半跪在Aria身前，蛇尾隐现并将她护入怀中", "eyeline": "Aria看Hades，Hades看Aria伤口", "performance": "Aria失焦后认出蓝色竖瞳；Hades暴怒压低身体，抱起时手掌托住她背部", "dialogue": "谁给你们的胆子，敢在我的面前，动我的新娘？", "asset_refs": ["character_aria", "character_hades_human"]}
    ]}

FORMAT_C_QUALITY = (
    "写实照片级、超写实质感、真人实拍电影剧照，采用 ARRI Alexa 65 摄影机拍摄，85mm 定焦镜头（Prime Lens），"
    "光圈 T1.8，竖版 9:16 画幅（Aspect Ratio），180 度快门角（180-Degree Shutter Angle），浅景深（Shallow Depth of Field），"
    "柔和奶油般散景（Bokeh），细腻胶片颗粒质感（Film Grain）。真实皮肤纹理，哑光质感（Matte, Non-Glossy），"
    "清晰可见毛孔与细微皮肤纹理起伏，真实次表面散射（Subsurface Scattering / SSS）光影效果，肤色只呈现真实皮肤下轻微血色，"
    "不形成发光红脸；皮肤高光仅允许在鼻梁、颧骨等自然出油区域出现极细微、局部的自然反光，不得形成大面积油亮色块或蜡质反光层；"
    "皮肤色调在面部各区域必须均匀一致，不得因参考图融合产生局部色差、色块拼接感或纹理断层。真人质感眼眸只保留真实环境反射，"
    "禁止眼球自发光（No Self-Illuminating Eyes）。真实布料垂坠动态褶皱，真实接触投影（Contact Shadow），光束中漂浮细微尘埃丁达尔效果（Tyndall Effect）。"
)
FORMAT_C_SKIN = (
    "人物皮肤须保持细腻、紧致、哑光通透的真实质感，毛孔与皮肤纹理清晰可辨但不夸张、不放大为颗粒感；皮肤表面禁止出现以下任一状态——"
    "粗糙颗粒感、明显油光、不健康的浮油质感、过度磨皮导致的塑料感/蜡感、皮肤纹理消失导致的假面感、局部色调不均或色块拼接感、"
    "五官边缘与皮肤融合产生的模糊塌陷。若本组镜头基于多张参考图（垫图）生成，须额外保证：不同参考图来源的皮肤质感、色温、"
    "纹理清晰度在最终画面中完全统一，不得保留原图各自的皮肤处理痕迹或产生融合接缝。"
)
ASSET_COMPLETION_GUIDANCE = (
    "场景或道具参考图缺失时，允许依据当前镜头文字描述进行保守补全：保持空间功能、材质、尺度、位置、光影和连续性；"
    "所有建筑名称、实际地名、警察标志、警徽、政府机构标识、物品商标、品牌Logo、商业招牌和可读文字均禁止出现，"
    "补全元素必须是虚构、无品牌、无现实机构归属的中性设计。"
)
REAL_WORLD_MARKS_NEGATIVE = (
    "严禁出现任何建筑名称、实际地名、街道名、城市名、国家名、警察标志、警徽、警车标识、"
    "政府机构标识、制服徽章、物品商标、品牌Logo、商业招牌、可识别现实机构文字或现实世界专属符号；"
    "所有文字、标识和徽章必须删除、模糊化或设计为不可辨识的虚构中性元素。"
)

def _prompt_groups(shots):
    """Group adjacent shots into independent 3-8 shot / 8-24s lighting units."""
    groups, current, total = [], [], 0.0
    for shot in shots:
        duration = float(shot.get("duration", 1.0))
        if current and (len(current) >= 5 or (len(current) >= 3 and total >= 15.0)):
            groups.append(current); current, total = [], 0.0
        current.append(shot); total += duration
    if current and len(current) < 3 and groups and sum(float(x.get("duration", 1.0)) for x in groups[-1]) + total <= 24.0:
        groups[-1].extend(current)
    elif current:
        groups.append(current)
    return groups

def _lighting_header(shots):
    lighting = next((s.get("lighting") for s in shots if s.get("lighting")), "")
    return (lighting or "室内主光源位于画面左前方约45度、略高于眼睛，柔化直射光与右侧冷色反射光形成冷暖对比；"
            "人物脸部保持明亮，五官和眼神清晰可辨，面部亮面在画面左侧、暗面落向画面右侧；阴影落在地面与衣料，"
            "玻璃和金属只保留受环境光控制的局部反射，背景压暗并用浅景深分离主体。")

def _shot_title(s, n):
    camera = s.get("camera", "固定机位") or "固定机位"
    angle = "越肩" if "OTS" in str(s.get("shot_size", "")) else "平角"
    movement = str(s.get("motion", "") or "固定机位")
    return f"【shot {n}｜{'、'.join(s.get('characters', [])) or '主体'}｜{s.get('shot_size', 'MS')}｜{angle}｜{movement}｜{s.get('focal_length_mm', 35)}mm｜duration: {float(s.get('duration', 1.0)):.1f}s】"

def format_c(sb, generation_model="剧梦2.5Pro", resolution="480P"):
    """Codex final prompt layer: Format C V2.6, with monologue excluded."""
    out = ["# Format C V2.6 提示词（Codex生成）",
           f"\n最终提示词生成器：Codex；规划模型：豆包2.1Turbo；剧梦生成模型：{generation_model}；分辨率：{resolution}。",
           "独白/旁白不写入提示词；仅保留原英文对白，且只放在音频字段。每组为独立光影单元。",
           f"场景/道具资产补全规则：{ASSET_COMPLETION_GUIDANCE}\n"]
    fields = ["叙事任务", "镜头", "画面", "视觉引导", "微表演", "对白反应", "人物背景融合", "光影细节", "音频", "运动强度", "负面提示词"]
    for gi, group in enumerate(_prompt_groups(sb["shots"]), 1):
        total = sum(float(s.get("duration", 1.0)) for s in group)
        cycle = " → ".join(f"{s.get('shot_size', 'MS')}平角" for s in group)
        durations = " / ".join(f"{float(s.get('duration', 1.0)):.1f}s" for s in group)
        out.extend([
            f"## G{gi:02d}｜光影连续单元｜{len(group)}镜｜{total:.1f}s",
            "【组头｜固定画质词与光影基调】",
            f"固定画质词（Fixed Quality Descriptor）：{FORMAT_C_QUALITY}",
            f"皮肤强制要求：{FORMAT_C_SKIN}",
            f"光影基调（Lighting Tone）：{_lighting_header(group)}",
            f"节奏结构（Beat Structure）：组型：{'对白组' if any(s.get('dialogue') for s in group) else '情绪/动作组'}｜{len(group)}镜｜共 {total:.1f}s；铺垫→递进→高潮→结果，最强拍落在 shot {max(range(1, len(group)+1), key=lambda i: float(group[i-1].get('duration', 1.0)))}；时长分配：{durations}",
            f"景别循环（Shot Size Cycle）：{cycle}",
            "视觉动线（Visual Flow）：主体占约80%视觉信息量，重心沿剧情动作方向迁移；所有视线落在明确戏内目标，不直视镜头。",
            ""
        ])
        for n, s in enumerate(group, 1):
            comp = f"景别：{s.get('shot_size', 'MS')}；焦段：全画幅等效 {s.get('focal_length_mm', 35)}mm；机位高度：{s.get('camera_height', 'eye_level')}；轴线：{s.get('axis', 'A_side')}；构图比例：{json.dumps(s.get('composition_ratio', {}), ensure_ascii=False)}；景深：{s.get('depth_of_field', 'medium_f2.8')}；前景遮挡：{str(s.get('foreground_occlusion', False)).lower()}；视线偏移：{s.get('eyeline_offset_deg', 15)}°。"
            dialogue = s.get("dialogue", "")
            vals = {
                "叙事任务": str(s.get("task", "推进当前动作"))[:25],
                "镜头": f"{comp}{s.get('camera', '')}；场景：{s.get('scene', '')}；保持180度轴线与屏幕方向连续。",
                "画面": f"{s.get('composition', '')} {s.get('action', '')}；先完成触发与阻力，再形成可见结果；{s.get('climax', '')}。",
                "视觉引导": f"视觉重心落在画面中部偏{'左' if n % 2 else '右'}，主运动方向沿轴线推进；{s.get('eyeline', '视线落在戏内道具或画外对手')}；禁止直视镜头。",
                "微表演": f"{s.get('pre_dialogue_state', '')} {s.get('performance', '')}；眼睑、下颌、手指或肩颈产生可读的细微变化，动作结束于稳定终态。",
                "对白反应": (f"说话者仅生成口型，其他可见人物闭口；触发：英文对白进入情绪高潮；承受者回应：眉眼、下颌和重心出现具体微反应；原英文对白见音频字段：{dialogue}"
                               if dialogue else "无原英文对白；禁止生成旁白、独白、字幕和任何口型；触发者、承受者与沉默者均以眼神、肌肉和道具反应完成情绪传递。"),
                "人物背景融合": f"角色：{'、'.join(s.get('characters', [])) or '按绑定资产卡'}；资产引用：{'、'.join(s.get('asset_refs', [])) or '使用对应人物资产卡'}；场景与道具按镜头文字描述补全，保持功能、材质、尺度、位置和光影连续；{ASSET_COMPLETION_GUIDANCE}",
                "光影细节": s.get("lighting") or "机位变化只引起面部亮暗面和道具反光的局部变化，不改变组头主光方向；脸部保持明亮、五官清晰。",
                "音频": (f"原英文对白（仅保留此原文）：{dialogue}；仅当前说话者口型同步。" if dialogue else "现场环境音与动作音效；无独白、无旁白、无背景音乐、无字幕。"),
                "运动强度": s.get("motion") or "中低强度；遵循触发→重心变化→动作→结果→情绪落点，切点落在动作进行中。",
                "负面提示词": (s.get('doubao_design', {}).get('negative') or "") + "；角色换脸、资产错配、左右互换、轴线跳变、背景锚点消失、额外人物、断肢融脸、非说话者张口、错误口型、字幕、水印、眼球自发光、直视镜头、与观众对视、主体居中呆板、动作完成后静止；" + REAL_WORLD_MARKS_NEGATIVE
            }
            out.append(_shot_title(s, n))
            out.extend(f"**{f}**：{vals[f]}" for f in fields)
            out.append("")
    return "\n".join(out)

def qa(story, assets, sb, cfg, monologue=None):
    issues = []
    character_blockers = assets.get("character_blockers", [m for m in assets.get("missing", []) if m.get("category") == "characters"])
    if character_blockers and cfg["quality"].get("require_asset_binding", True):
        issues.append({"level":"blocker", "code":"MISSING_CHARACTER_ASSET", "items": character_blockers})
    for item in assets.get("prompt_completion", []):
        issues.append({"level":"warning", "code":"PROMPT_COMPLETION_ASSET", "category": item["category"], "entity": item["entity"], "message": item["instruction"]})
    for s in sb["shots"]:
        for k in ("action", "performance", "eyeline", "story_progression", "pre_dialogue_state", "conflict", "climax", "result", "shot_size", "focal_length_mm", "camera_height", "axis", "composition_ratio", "depth_of_field"):
            if not s.get(k): issues.append({"level":"blocker", "code":"MISSING_SHOT_FIELD", "shot":s["id"], "field":k})
        if not isinstance(s.get("focal_length_mm"), (int, float)) or not 14 <= s.get("focal_length_mm", 0) <= 135:
            issues.append({"level":"blocker", "code":"INVALID_FOCAL_LENGTH", "shot":s["id"]})
        if not 1.0 <= float(s.get("duration", 0)) <= 6.0:
            issues.append({"level":"blocker", "code":"INVALID_SHOT_DURATION", "shot":s["id"], "duration":s.get("duration")})
        if s.get("action", "").strip() in {"纯人物状态", "站着看", "坐着看"}:
            issues.append({"level":"blocker", "code":"STATIC_STATE_SHOT", "shot":s["id"]})
    if monologue and monologue.get("status") == "found":
        expected = monologue["total_duration"]
        actual = round(sum(s["duration"] for s in sb["shots"]), 2)
        if abs(expected - actual) > 0.05:
            issues.append({"level":"blocker", "code":"MONOLOGUE_TIMING_MISMATCH", "expected": expected, "actual": actual})
    return {"status": "blocked" if any(i["level"] == "blocker" for i in issues) else "pass", "issues": issues, "human_gates": ["核对角色与场景资产", "确认豆包输出没有偏离剧本", "确认剧梦生成将消耗积分"]}

def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    r = sub.add_parser("run"); r.add_argument("--input", required=True); r.add_argument("--monologue", help="本地独白稿；省略时从剧本中识别独白行"); r.add_argument("--dialogue", help="包含原英文台词的本地剧本；省略时读取配置"); r.add_argument("--claude-output", help="用户手动保存的 Claude 结构化拆镜文件；省略时不读取"); r.add_argument("--doubao-output", help="豆包生成的结构化分镜文件；省略时按配置自动读取最新文件"); r.add_argument("--config", default="config/local.json")
    c = sub.add_parser("check"); c.add_argument("--run", required=True)
    args = ap.parse_args()
    if args.cmd == "init":
        Path("config").mkdir(exist_ok=True); Path("config/local.json").write_text(Path("config/local.example.json").read_text(), encoding="utf-8"); print("已生成 config/local.json，请填写本机配置。"); return
    if args.cmd == "check": print(json.dumps(load_json(Path(args.run)/"qa_report.json"), ensure_ascii=False, indent=2)); return
    cfg = load_json(Path(args.config)); text = read_script(Path(args.input)); run = Path(cfg["project"]["output_root"]) / (datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]); story = infer_entities(text)
    rate = cfg.get("quality", {}).get("monologue_chars_per_second", 4.5)
    mono_text = read_script(Path(args.monologue)) if args.monologue else text
    monologue = extract_monologue(mono_text, rate)
    dialogue_path = Path(args.dialogue) if args.dialogue else Path(cfg.get("project", {}).get("dialogue_script", ""))
    english_dialogue = extract_original_dialogue(read_script(dialogue_path)) if dialogue_path.is_file() else []
    claude_cfg = cfg.get("claude", {})
    claude_path = Path(args.claude_output) if args.claude_output else Path(claude_cfg.get("output_path", ""))
    claude = read_claude_split(claude_path)
    doubao_path = Path(args.doubao_output) if args.doubao_output else discover_doubao_output(cfg)
    doubao = read_doubao_design(doubao_path)
    manifest_path = Path(cfg["asset_library"]["manifest"]); manifest = load_json(manifest_path) if manifest_path.exists() else {"assets": []}; required_character_names = cfg.get("quality", {}).get("required_character_asset_names", []); assets = bind_assets(story, manifest, Path(cfg["asset_library"]["root"]), required_character_names); sb = storyboard(story, monologue, doubao, english_dialogue); report = qa(story, assets, sb, cfg, monologue)
    if claude_cfg.get("enabled", False) and claude_cfg.get("require_split_output", True) and claude["status"] != "found":
        report["issues"].append({"level": "blocker", "code": "CLAUDE_SPLIT_MISSING", "message": "Claude结构化拆镜输出尚未保存到本地"}); report["status"] = "blocked"
    save_json(run/"story_bible.json", story); save_json(run/"monologue_timing.json", monologue); save_json(run/"claude_split.json", claude); save_json(run/"doubao_design.json", doubao); save_json(run/"asset_bindings.json", assets); save_json(run/"storyboard.json", sb); save_json(run/"qa_report.json", report); (run/"format_c_prompts.md").write_text(format_c(sb, cfg["platform"].get("model", "剧梦2.5Pro"), cfg["platform"].get("resolution", "480P")), encoding="utf-8"); print(f"完成 dry-run：{run}\nClaude拆镜：{claude['status']}，拆镜单元 {len(claude['split_units'])}\n独白：{monologue['status']}，总时长 {monologue['total_duration']} 秒\n豆包文件：{doubao['status']}，分镜设计 {len(doubao['shots'])} 条\nQA：{report['status']}，问题 {len(report['issues'])} 项")

if __name__ == "__main__": main()
