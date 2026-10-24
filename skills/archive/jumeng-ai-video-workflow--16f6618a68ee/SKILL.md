---
name: jumeng-ai-video-workflow
description: Run the guarded local pipeline from script intake through asset binding, storyboard and prompt QA, Doubao planning, and Jumeng draft or generation gates.
---

# 剧梦 AI 视频自动化流程

Use this skill when the user wants to turn a script into a repeatable local-to-Jumeng workflow. Read the project contract and [references/automation-workflow.md](references/automation-workflow.md) before platform actions.

## Stage order

`INGEST` → `STORY_BIBLE` → `CLAUDE_STORYBOARD_SPLIT` → `ASSET_BINDING` → `ASSET_UPLOAD` → `DOUBAO_PLAN` → `STORYBOARD` → `CODEX_FORMAT_C` → `JUMENG_DRAFT` → `HUMAN_GATE` → `GENERATE` → `QA`.

Do not skip fact extraction or asset binding. Missing character assets, unresolved identity, changed platform page, expired login, or uncertain submit state block downstream generation. Missing scene or prop images are handled by conservative prompt completion and recorded as QA warnings.

`ASSET_UPLOAD` is a hard gate for character cards: upload and verify character assets first. Scene and prop cards should be uploaded when available; if their images are missing, continue with explicit text descriptions in the prompt and record the completion warning instead of blocking.

For timing-driven storyboard work, exclude quoted dialogue and treat all remaining local narrative, visual description, and inner narration as monologue. Use the resulting local text duration as the source of truth for shot timing.

When a Doubao structured storyboard file is available, read it automatically, match its dialogue/reaction fields to local narrative segments, and carry over blocking, eyelines, micro-performance, camera, conflict, lighting, audio, and negative constraints into the final prompts. Any Ciyuan Wanxiang output is limited to lighting reference only.

Claude is an optional manual-input stage: the user feeds Claude directly; this workflow does not control Claude. If the user saves a local result, read it for episode/scene/shot boundaries and dialogue placement, then verify it against the source script.

Codex is the final prompt generator: it alone writes Format C V2.6; Claude contributes only a user-supplied optional structural draft, and Doubao contributes performance/blocking/conflict design.

## Inputs and outputs

- Script: DOCX, TXT, or Markdown. Preserve the original.
- Asset registry: `assets/manifest.json`, with stable IDs and paths relative to the asset root.
- Local config: platform URL, browser profile, generation model/resolution, planning model, dry-run, and credit confirmation policy. Never store passwords or exported cookies.
- Run artifacts: `story_bible.json`, `asset_bindings.json`, `storyboard.json`, `format_c_prompts.md`, and `qa_report.json`.

## Doubao and Jumeng boundaries

Doubao may be used for planning only when the user authorizes sending the specified script to the specified local/account context. Treat its output as a draft and verify it against the source script. Jumeng may receive uploads or prompts only after the user authorizes that destination and the QA report has no blockers. Credit-consuming generation always requires a final confirmation immediately before submission unless the user explicitly changed the project policy.

## Recovery

Use the run directory as the checkpoint. Resume from the last successful stage; do not repeat an external submission whose status is unknown. Stop and report the exact blocker when a page requires login, CAPTCHA, permission, payment, or a new unfamiliar action.
