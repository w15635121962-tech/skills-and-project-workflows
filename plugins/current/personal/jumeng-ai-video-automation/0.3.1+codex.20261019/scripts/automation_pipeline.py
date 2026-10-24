#!/usr/bin/env python3
"""Compatibility entrypoint for the retired local prompt generator.

Current prompt authoring uses short-drama-prompts-v3. Platform work uses
jumeng-episode-producer. This compatibility command never rewrites project
files, uploads assets, or submits generation jobs.
"""
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="旧自动流水线已替换。新提示词使用 short-drama-prompts-v3；剧梦操作使用 jumeng-episode-producer。"
    )
    parser.parse_known_args()
    parser.exit(
        2,
        "此历史生成器已停用。请读取 /Users/zc/.codex/skills/short-drama-prompts-v3/SKILL.md "
        "编写Format C V2.5提示词；平台操作读取 /Users/zc/.codex/skills/jumeng-episode-producer/SKILL.md。\n"
    )


if __name__ == "__main__":
    main()
