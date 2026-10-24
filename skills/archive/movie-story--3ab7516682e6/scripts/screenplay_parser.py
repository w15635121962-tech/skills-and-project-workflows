#!/usr/bin/env python3
"""
screenplay_parser.py

剧本解析辅助脚本：读取剧本文本文件，提取场景结构、角色、台词统计，
输出结构化摘要供分镜生成参考。

用法：
    python3 screenplay_parser.py <screenplay.txt> [--output summary.json]
"""

import re
import sys
import json
import argparse
from dataclasses import dataclass, field, asdict
from typing import List, Optional


@dataclass
class DialogueLine:
    character: str
    text: str
    parenthetical: Optional[str] = None


@dataclass
class Scene:
    index: int
    header: str          # e.g. "INT. 咖啡馆 - 日"
    location_type: str   # INT / EXT / INT./EXT.
    location: str        # 地点
    time: str            # 日 / 夜 / 傍晚 / etc.
    action_lines: List[str] = field(default_factory=list)
    dialogues: List[DialogueLine] = field(default_factory=list)
    characters: List[str] = field(default_factory=list)
    prop_hints: List[str] = field(default_factory=list)   # 从动作行提取的道具关键词

    @property
    def estimated_duration_seconds(self) -> int:
        """粗略估算场景时长：每行动作约3秒，每行台词约2秒"""
        action_time = len(self.action_lines) * 3
        dialogue_time = sum(len(d.text) // 20 * 2 for d in self.dialogues)
        return max(action_time + dialogue_time, 10)

    @property
    def suggested_shot_count(self) -> int:
        """建议镜头数量"""
        dur = self.estimated_duration_seconds
        # 基础：每10秒约2-4个镜头
        base = max(3, dur // 10 * 3)
        # 台词多的场景增加镜头（正反打）
        dialogue_bonus = len(self.dialogues) * 2
        return min(base + dialogue_bonus, 40)

    @property
    def dominant_tone(self) -> str:
        """从关键词推断场景基调"""
        text = " ".join(self.action_lines).lower()
        tone_keywords = {
            "紧张/悬疑": ["枪", "追", "跑", "警察", "逃", "危险", "恐惧", "颤抖", "黑暗"],
            "温馨/抒情": ["微笑", "拥抱", "温暖", "阳光", "笑", "爱", "幸福"],
            "悲伤/沉重": ["哭", "泪", "死", "离开", "失去", "遗憾", "痛苦"],
            "幽默/轻松": ["笑", "滑稽", "搞笑", "轻松", "玩笑"],
            "动作/激烈": ["打", "战斗", "爆炸", "冲突", "激烈"],
        }
        scores = {}
        for tone, keywords in tone_keywords.items():
            scores[tone] = sum(1 for kw in keywords if kw in text)
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "中性/叙事"


def parse_screenplay(text: str) -> List[Scene]:
    """解析剧本文本，返回场景列表"""
    lines = text.splitlines()
    scenes: List[Scene] = []
    current_scene: Optional[Scene] = None
    i = 0

    scene_header_re = re.compile(
        r"^(INT\.|EXT\.|INT\./EXT\.|EXT\./INT\.)\s+(.+?)\s*[-–—]\s*(.+)$",
        re.IGNORECASE
    )
    # 角色名：全大写，居中或行首，不超过30字符
    character_re = re.compile(r"^\s{10,}([A-Z\u4E00-\u9FFF][A-Z\u4E00-\u9FFF\s]{0,20})\s*$")
    parenthetical_re = re.compile(r"^\s*\((.+)\)\s*$")

    prop_keywords = [
        "手枪", "枪", "刀", "手机", "电话", "钱", "包", "文件", "照片",
        "车", "汽车", "摩托", "钥匙", "箱子", "桌子", "椅子", "窗", "门",
        "gun", "knife", "phone", "car", "key", "box", "table", "door", "window"
    ]

    current_character = None

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 检测场景头
        m = scene_header_re.match(stripped)
        if m:
            if current_scene:
                scenes.append(current_scene)
            loc_type = m.group(1).upper().rstrip(".")
            location = m.group(2).strip()
            time_of_day = m.group(3).strip()
            current_scene = Scene(
                index=len(scenes) + 1,
                header=stripped,
                location_type=loc_type,
                location=location,
                time=time_of_day,
            )
            current_character = None
            i += 1
            continue

        if current_scene is None:
            i += 1
            continue

        # 检测角色名
        cm = character_re.match(line)
        if cm:
            current_character = cm.group(1).strip()
            if current_character not in current_scene.characters:
                current_scene.characters.append(current_character)
            i += 1
            continue

        # 检测舞台提示
        pm = parenthetical_re.match(stripped)
        if pm and current_character:
            # 舞台提示归属于当前角色
            i += 1
            continue

        # 检测台词（当前有角色名时，缩进行视为台词）
        if current_character and line.startswith("    ") and stripped:
            # 读取连续台词行
            dialogue_text = stripped
            current_scene.dialogues.append(
                DialogueLine(character=current_character, text=dialogue_text)
            )
            i += 1
            continue

        # 动作行：非空且非纯符号
        if stripped and not stripped.startswith("#"):
            if not line.startswith("    " * 3):  # 排除过度缩进的台词
                current_scene.action_lines.append(stripped)
                # 提取道具关键词
                for prop in prop_keywords:
                    if prop in stripped and prop not in current_scene.prop_hints:
                        current_scene.prop_hints.append(prop)
            current_character = None  # 动作行重置角色上下文

        i += 1

    if current_scene:
        scenes.append(current_scene)

    return scenes


def generate_summary(scenes: List[Scene]) -> dict:
    """生成分析摘要"""
    total_duration = sum(s.estimated_duration_seconds for s in scenes)
    total_shots = sum(s.suggested_shot_count for s in scenes)

    all_characters: dict = {}
    for s in scenes:
        for c in s.characters:
            all_characters[c] = all_characters.get(c, 0) + 1

    return {
        "统计信息": {
            "场景总数": len(scenes),
            "预估总时长": f"{total_duration // 60}分{total_duration % 60}秒",
            "建议镜头总数": total_shots,
            "主要角色": dict(sorted(all_characters.items(), key=lambda x: -x[1])[:10]),
        },
        "场景列表": [
            {
                "编号": f"SC-{s.index:03d}",
                "场景头": s.header,
                "在场角色": s.characters,
                "情绪基调": s.dominant_tone,
                "预估时长": f"{s.estimated_duration_seconds}秒",
                "建议镜头数": s.suggested_shot_count,
                "关键道具": s.prop_hints,
                "台词行数": len(s.dialogues),
                "动作行数": len(s.action_lines),
            }
            for s in scenes
        ]
    }


def main():
    parser = argparse.ArgumentParser(description="剧本结构解析工具")
    parser.add_argument("screenplay", help="剧本文本文件路径")
    parser.add_argument("--output", "-o", help="输出摘要 JSON 文件路径（默认打印到控制台）")
    args = parser.parse_args()

    try:
        with open(args.screenplay, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"错误：找不到文件 {args.screenplay}", file=sys.stderr)
        sys.exit(1)

    scenes = parse_screenplay(text)
    if not scenes:
        print("⚠️  未能识别到任何场景。请确认剧本格式包含 INT./EXT. 场景头。", file=sys.stderr)
        sys.exit(1)

    summary = generate_summary(scenes)

    output_text = json.dumps(summary, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_text)
        print(f"✅ 分析完成，摘要已保存至：{args.output}")
    else:
        print(output_text)


if __name__ == "__main__":
    main()
