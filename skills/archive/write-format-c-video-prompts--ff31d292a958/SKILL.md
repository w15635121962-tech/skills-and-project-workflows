---
name: write-format-c-video-prompts
description: Convert scripts, posts, dialogue, action descriptions, storyboards, or reference images into complete Chinese Format C V2.5 prompts for short-drama and narrative AI video; also revise, continue, audit, translate, or compress existing Format C prompts. Use when the user asks for Format C, production-ready per-shot AI video prompts, rhythm-enhanced coverage, no-lens eyeline control, dialogue/reaction coverage, cinematic vertical-video prompts, or optimization of an existing Format C prompt. Do not trigger for story analysis or a simple storyboard unless the user explicitly requests production-ready Format C prompts.
---

# Write Format C Video Prompts V2.5

Produce model-executable prompts, not literary shot summaries. Treat Format C as the final generation-prompt layer with a complete group header and eleven shot-specific fields.

## Load the authoritative specification

Before generating, continuing, revising, auditing, translating, or compressing any prompt, read [references/format-c-template-optimized.md](references/format-c-template-optimized.md) completely. Do this again on every new request so current rules are not replaced by remembered or project-specific variants. Use its headings and V2.5 self-check list to navigate the long reference; do not output its maintenance notes or revision history.

Treat that file as the plugin's default Format C V2.5 contract. Resolve conflicts in this order:

1. Current user instruction.
2. Currently approved prompt, storyboard, script, or reference frame.
3. Current project's explicit contract and character behavior anchors.
4. The authoritative specification bundled with this skill.

When a higher-priority source overrides shot count, duration, camera, lens, aspect ratio, model, dialogue language, or another default, state the override briefly and use it consistently. Never import facts or private rules from another project.

## Confirm the source gate

Before drafting, identify enough source material to preserve story facts:

- script excerpt, premise, dialogue, action description, storyboard, or reference image;
- target model and version when model-specific syntax, duration, or intent annotations matter;
- project-specific character, wardrobe, location, prop, behavior, and eyeline anchors;
- requested aspect ratio, total duration, shot count, output language, and delivery scope;
- permissions for narration, music, subtitles, UI text, off-screen speech, and physiological sound.

If story facts or the requested scene are missing, ask only for the missing source material. Do not invent a plot or borrow another project's contract. If low-risk technical values are unspecified, use the bundled template defaults and disclose them in one short sentence.

## Build the hidden directing ledger

Do not print this ledger unless requested. Lock:

- exact source lines, speaker ownership, causal order, decisive result, emotional turn, and group-end question;
- group type, lighting-unit boundary, shot count, declared total duration, strongest beat, and non-uniform per-shot timings;
- one narrative task, one new piece of information, shot size, angle, focal length, and visual center for every shot;
- visual-center inheritance, screen movement direction, every visible character's in-story eyeline target, and any explicitly motivated direction reversal;
- visible cast, objectives, identity, scale, wardrobe, hair, makeup, injuries, dirt, and wetness;
- location, time, weather, entrances, exits, support surfaces, screen side, facing, distance, height, and 180-degree axis;
- hand ownership, body contact, force transfer, and prop location;
- main-light direction, color-temperature relationship, exposure, face fill, shadow landing, and material response;
- reference-image identity, costume, location, prop, pose, and blocking inheritance.

Convert every beat into:

`cause → intention → action → result → reaction → stable endpoint → new question`

Every cut must add narrative, spatial, action, emotional, dialogue-ownership, sound, or attention information.

## Draft the exact V2.5 structure

Use one group per continuous space, time, key-light direction, and color temperature. Start a new group whenever any of those change, and repeat the complete group header. Unless a higher-priority source specifies otherwise:

- use 3–8 shots per group, defaulting to 5;
- use 8–24 seconds per group, defaulting to 15.0 seconds;
- keep each shot between 1.0 and 6.0 seconds;
- make the durations non-uniform and sum them exactly to the declared total at 0.1-second precision;
- restart numbering at shot 1 inside each group.

Write every group header in this order:

`固定画质词（Fixed Quality Descriptor） | 光影基调（Lighting Tone） | 节奏结构（Beat Structure） | 景别循环（Shot Size Cycle） | 视觉动线（Visual Flow）`

Write every shot heading with subject, shot size, angle, camera movement, focal length, and duration. Then write these eleven fields in order:

`叙事任务 | 镜头 | 画面 | 视觉引导 | 微表演 | 对白反应 | 人物背景融合 | 光影细节 | 音频 | 运动强度 | 负面提示词`

Keep all dialogue, voiceover, ambience, and sound effects only in `音频（Audio）`. Do not add narration, subtitles, music, interface audio, or unintended lip movement unless the source or user explicitly permits it.

## Preserve the mandatory group-level text verbatim

Copy both mandatory blocks from the authoritative reference without paraphrasing:

- Copy the fixed quality descriptor from its first word `写实照片级` through its final words `丁达尔效果（Tyndall Effect）。`.
- Copy the entire paragraph from `强制要求： 人物皮肤须保持细腻` through `不允许省略、简写或用"皮肤真实"等笼统表述替代。`.

Before delivery, compare both spans against the reference character for character, including punctuation and spacing. Place them in every group header; never replace either with `同上`, `延续上一组`, `same as before`, or equivalent shorthand.

## Enforce rhythm and reading flow

- Give each shot one narrative task of no more than 25 Chinese characters. Split any task containing `同时`, `并且`, or `顺便`.
- State the group type, shot count, exact total, beat shape, strongest shot, coverage sequence, and visual-flow path in the group header.
- Avoid consecutive identical shot sizes or angles. Cover at least three shot-size tiers per normal group and preserve the reference's shorter-group exceptions.
- Include a clearly longer big beat and a clearly shorter small beat, or satisfy the short-group duration-gap rule in the reference.
- Keep people as roughly 80% of the visual information except for the single permitted establishing shot. Use blur, darkness, occlusion, empty space, and simplified color fields to remove competing information.
- End each group with an explicit suspense, reversal, emotion, or action hook rather than an information-free exit or fade.

For decisive action, distribute the action across at least three shots and a major action across five or more. Isolate the contact moment, cut around the 70/30 point of the moving action, and use at least two executable speed cues in high-speed shots.

## Keep every eyeline inside the story

Treat `视线不入镜头（No Eye Contact with Lens）` as mandatory and equal in priority to non-glowing eyes:

- Give every visible character a named in-story eyeline target in `视觉引导（Visual Flow）`.
- Do not let a character look into the lens, meet the viewer's gaze, or leave the eyeline aimless. A face may orient toward camera while the pupils remain directed to a clear off-axis target.
- In shot/reverse-shot, dirty singles, over-the-shoulder shots, clean singles, crying, threats, seduction, monologues, and cliffhanger close-ups, point the eyes toward the counterpart, prop, source, or a specific off-screen point.
- Use POV only when explicitly motivated and label its owner. Keep the viewed character's gaze slightly beside the optical axis rather than locked to lens center.
- Add the reference's eyeline and fourth-wall exclusions to every relevant shot-specific negative prompt.

Maintain eyeline match, 180-degree continuity, visual-center inheritance, and screen-direction consistency. Use a neutral shot or motivated action bridge before reversing direction.

## Enforce dialogue coverage and reaction logic

Use English for dialogue by default, and preserve supplied English dialogue verbatim. Keep only the current speaker's mouth moving; every other visible person remains closed-mouth, including blurred listeners and over-the-shoulder foreground owners.

For a dialogue group:

- show the owner of the first and last spoken line in that line's shot;
- vary clean single, dirty single, over-the-shoulder, two-shot, and motivated rack-focus coverage, never repeating one form for more than two consecutive shots;
- give the listener at least one dedicated focal shot;
- include at least one true silent confrontation beat and grant it meaningful duration;
- use at most one motivated rack-focus change in a shot.

Treat `对白反应（Dialogue Reaction）` as mandatory even in silent shots. Name the trigger, emotional receiver, silent participants, muscle-level facial change, gaze change, body or prop response, and stable post-beat state. Never fill it with only `无台词，无口型`. Keep each character's blink, micro-expression, and off-screen-looking habit distinct and asynchronous.

## Preserve physical and visual continuity

Repeat or inherit explicitly across shots and groups:

- identity, scale, wardrobe, hair, makeup, injury, dirt, and wetness;
- screen side, facing, eyeline, axis, distance, height, and support plane;
- contact owner, contact surface, force direction, limb exits, entrances, and exits;
- prop source, hand owner, placement, carry state, and reappearance;
- light source, direction, color temperature, exposure, face fill, shadow landing, and weather;
- the prior stable endpoint as the next opening state.

In `人物背景融合`, specify shared light, body pressure on named support surfaces, contact shadows, material compression, environmental reflection, atmosphere, focal plane, aerial perspective, and continuous contact or prop chains. Do not rely on abstract phrases such as `自然融合` or `无贴图感`.

In the group lighting tone, expand the visual reference into executable source, direction, height, softness, temperature, face highlight and shadow side, exposure, shadow landing, reflections, and background luminance. State separately that faces remain bright and features readable. In `光影细节`, write only shot-local changes relative to that complete group tone.

## Control VFX and intent annotations

For transformation or complex VFX, use a visible scale reference, one common support plane, an occluded transition when required, environmental response, one stable final form, and dissipation. Keep anatomy states mutually exclusive and never leave residual or double bodies. Keep tears, sweat, eyes, skin, fur, and scales physically lit rather than self-illuminating.

Use V2.3 intent annotations according to the target model:

- Enable them selectively for Seedance 2.5 or a confirmed stronger model; reduce or disable them for Seedance 2.0 or weaker models; A/B test an unknown model when feasible.
- Write the complete measurable physical action first. After removing every annotation, the remaining prompt must still be independently generatable.
- Limit an annotation to 20 Chinese characters, one per eligible field, and normally 1–3 per shot.
- Use annotations only in `画面`, `视觉引导`, `微表演`, `对白反应`, or `运动强度`. Never use them in quality, lighting, audio, or negative-prompt fields.
- Do not let an annotation add a new action, prop, person, off-screen fact, or camera instruction.

## Revise without collateral changes

When revising an existing prompt, freeze approved story facts, dialogue, shot count, blocking, axis, props, lighting, field order, and project anchors unless the user explicitly changes them. Patch only the requested shots or demonstrated failure points. For compression or translation, preserve speaker ownership, causality, timing, fixed phrases, and required field structure; measure the final character count when a ceiling exists.

## Final audit

Before delivery, verify:

- requested layer, language, field names, and exact field order;
- source dialogue, speaker ownership, causality, emotional turn, and no invented project facts;
- group type, shot count, per-shot timing, declared total, strongest beat, and group-end hook;
- complete fixed quality and skin spans in every group, verified character for character;
- one narrative task, one primary performance target, and one stable endpoint per shot;
- shot-size and angle variation, motivated cuts, visual-flow continuity, and correct 180-degree continuity;
- an explicit in-story eyeline target for every visible character and no lens eye contact;
- dialogue coverage, silent beat, listener focus, reaction logic, and unique mouth ownership;
- identity, wardrobe, prop, hand, contact, support, scale, and light continuity;
- bright readable faces, natural eyes, and non-glowing tears, sweat, skin, fur, or scales;
- positive physical integration and manageable actor, camera, and VFX motion load;
- permitted audio only, narrow shot-specific negative prompts, and no cross-group shorthand;
- intent annotations obey the active model switch and remain removable without breaking the physical prompt.

Report measured counts or durations when required. Never claim that a target video platform accepted or successfully generated the prompt unless it was actually tested there.
