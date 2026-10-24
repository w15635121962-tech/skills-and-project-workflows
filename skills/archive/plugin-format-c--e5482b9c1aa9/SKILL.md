---
name: "提示词26-format-c-video-prompts"
description: Convert supplied scripts, dialogue, action descriptions, storyboards, or reference images into complete Chinese Format C V2.6 AI-video prompts for short drama; also revise, audit, continue, translate, or compress existing V2.6 prompts.
---

# Format C V2.6 提示词

Use this skill only when the user requests production-ready Format C prompts, per-shot AI-video prompts, or revision/audit/compression of an existing Format C prompt. Do not use it for story analysis or an ordinary storyboard unless the user explicitly asks for the final generation-prompt layer.

## Source gate

Before writing, identify the supplied script or scene source, speaker ownership, character and wardrobe anchors, location and prop continuity, target model, aspect ratio, duration, shot count, language, and allowed audio elements. If story facts are missing, request the missing source material; do not invent plot facts or borrow another project's contract.

## V2.6 contract

- Treat the current user instruction and approved source as higher priority than this skill.
- Plan before prose: causal order, blocking, 180-degree axis, screen side, support surfaces, hand ownership, contact and force transfer, lighting continuity, shot rhythm, visual flow, and every visible character's in-story eyeline.
- Convert each beat as `cause -> intention -> action -> result -> reaction -> stable endpoint -> new question`.
- One shot has one narrative task and one new piece of information. Split compound actions before drafting.
- A group is one continuous space, time, key-light direction, and color-temperature unit. Start a new complete group header whenever any of these changes.
- Default to 3–8 shots per group, 8–24 seconds per group, and 1.0–6.0 seconds per shot. Durations must sum exactly to the declared total at 0.1-second precision, with non-uniform rhythm and an explicit group-end hook.
- Every group header must contain: fixed quality descriptor, complete lighting tone, beat structure, shot-size/angle cycle, and visual-flow path.
- Every shot must contain these eleven fields in this order: `叙事任务（Narrative Task） | 镜头 | 画面 | 视觉引导（Visual Flow） | 微表演（Micro-Performance） | 对白反应（Dialogue Reaction） | 人物背景融合（Subject-Background Integration） | 光影细节（Lighting Detail） | 音频（Audio） | 运动强度（Motion Intensity） | 负面提示词（Negative Prompt）`.
- Put all dialogue, voiceover, ambience, and sound effects only in `音频`; put no dialogue or sound descriptions in visual fields.
- English dialogue is preserved verbatim by default. Only the current speaker may move their mouth; non-speakers stay closed-mouth.
- Every visible character needs a concrete in-story eyeline target. Unless the shot is explicitly labeled POV, prohibit looking into the lens, viewer eye contact, fourth-wall breaking, and pupils locked on the optical axis.
- `对白反应` is mandatory even when nobody speaks: state the trigger, receiver, silent participants, muscle-level facial response, gaze adjustment, body/prop response, and stable endpoint. Never write only `无台词，无口型`.
- Decisive actions are split across anticipation, launch, contact/force transfer, result, and emotional landing; cut during action and preserve object/contact/axis continuity.
- Faces remain bright and readable even in dark scenes. Expand lighting into source, side, height, softness, temperature, face highlight/shadow side, exposure, shadow landing, and material response.
- Never use `同上`, `沿用上一组`, or abbreviated fixed blocks in a complete group.

## Mandatory fixed blocks

For each group, copy the fixed quality descriptor and mandatory skin paragraph verbatim from the project's authoritative V2.6 reference before drafting. If the project supplies no override, use the bundled default reference at `/Users/zc/.codex/skills/write-format-c-video-prompts/references/format-c-template-v2.6.md`. Do not reproduce its maintenance appendix or revision record in generated prompts.

For crying shots, copy the complete V2.6 tears paragraph rather than reducing it to `流泪`. Add relevant negative terms for waxy/plastic skin, self-illuminating eyes, lip-sync errors, axis jumps, repetitive framing, and fourth-wall eye contact.

## Revision boundary

When revising an approved prompt, freeze all unrequested story facts, dialogue, timing, shot count, blocking, axis, props, lighting, field order, and project anchors. Change only the requested shots or demonstrated failure points. Never claim platform acceptance or successful generation unless it was actually tested.
