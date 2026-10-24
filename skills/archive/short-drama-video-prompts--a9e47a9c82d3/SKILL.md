---
name: short-drama-video-prompts
description: Create, revise, or audit cinematic AI-video prompts and editing-first storyboards for vertical short dramas, especially Chinese Format C shot groups. Use when the user asks for video prompts, prompt groups, shot breakdowns, continuity locks, character blocking, lighting continuity, dialogue reactions, performance beats, or generation-failure fixes such as face merging, bright night scenes, UI gibberish, hand penetration, outfit swapping, subtitles, or non-diegetic audio.
---

# Short Drama Video Prompts

Create production-ready Chinese video prompts with an editing-first mindset. Preserve the user's established template unless explicitly asked to redesign it.

## Workflow

1. Identify the requested deliverable: full prompt group, single shot revision, storyboard analysis, prompt audit, or generation-failure fix.
2. Extract immutable facts first: characters on screen, blocking, costume anchors, props, time of day, dialogue, emotional turn, supplied reference images, and model constraints.
3. Plan coverage before writing long prompts. Prioritize emotion, story rhythm, eyeline, 2D composition, then 3D continuity. Include clean reverse shots and over-shoulder coverage for dialogue scenes when the user asks for a storyboard.
4. Keep every shot independently generatable while preserving continuity: repeat decisive blocking, light direction, wardrobe anchors, prop locations, camera axis, and contact details inside the relevant shot.
5. Use Format C by default. Begin a group with fixed quality language, opening-state lock, environment, and lighting baseline; then write each shot with duration, camera, image, micro-performance, dialogue reaction, physical integration, lighting, audio, motion intensity, and negatives.
6. Perform a final failure-mode pass using [production-rules.md](references/production-rules.md) before producing a full group or auditing an existing prompt.
7. When working on the user's established short-drama prompt workflow, especially the 九尾狐 project or any request that mentions prior rules, output standards, learned problems, `@` tagging, dialogue reactions, magic particles, lighting continuity, or prompt failure fixes, also read [user-standards.md](references/user-standards.md) and apply it as the user's standing house style.
8. For 九尾狐 magic effects, energy colors, magic attacks, enemy attacks, mark appearance/dissolution, iris activation, or four-clan VFX descriptions, read [jiuweihu-magic-vfx.md](references/jiuweihu-magic-vfx.md). Use it together with `user-standards.md` so the magic remains photorealistic, local, and controllable.
9. For full vertical prompt groups, coverage planning, over-shoulder dialogue, vertical composition, action/reaction rhythm, scale continuity, or generation-failure repair, also read [vertical-directing.md](references/vertical-directing.md). It carries the user's cross-project directing grammar learned from production tests; direct current user instructions and project overlays override it when they conflict.

## Default Format

- Write in Chinese unless the user requests another language.
- Use five shots per group by default for Chinese short-drama prompt groups. Reset shot numbering to `shot 1` for every group.
- Put shot duration and focal length directly in the shot title, not only in the body, for example `【shot 1 | 近景 | 平视 | 固定 | 85mm | duration: 2.5s】`.
- Start each group with opening state, environment, light baseline, camera/quality baseline, audio rules, and group-level negatives.
- Use `@` only for characters, props, or scenes visibly present in that shot. Do not tag an off-screen character merely because dialogue mentions them.
- If the user provides an established template, preserve its field names and order unless explicitly asked to redesign it.
- If the user asks for analysis across dimensions, use those dimensions as an internal checklist and do not rewrite the template unless requested.

## Required Format C Fields

For each shot, include:

- `镜头`: whose shot it is, exact framing, camera angle, camera movement, duration, and focal length.
- `画面`: visible composition, left/right or foreground/background relations, props, and wardrobe anchors.
- `微表演`: physical performance grammar such as breath, shoulders, neck, hands, step rhythm, clothing compression, hair, dust, or pause length.
- `对白反应`: spoken line if present, or visible reaction to off-screen dialogue. If no dialogue exists, explicitly prohibit dialogue mouth movement.
- `人物背景融合`: contact shadows, shared color temperature, perspective, reflections, material wear, cloth physics, and spatial anchoring.
- `光影`: practical source direction, color relationship, shadow strategy, material response, and continuity with adjacent shots.
- `音频`: diegetic-only sound. Use low environment sound by default. Do not add background music, subtitles, or voice-over unless the user asks.
- `运动强度`: keep motion intensity controlled and compatible with the requested model.
- `负面提示词`: include shot-specific failures, plus common identity, lighting, audio, text, and contact negatives.

## Reference Routing

Read [references/production-rules.md](references/production-rules.md) before producing a full prompt group, auditing a prompt, rewriting a storyboard, or fixing model failures. It contains the detailed Format C checklist, wording patterns, Seedance-2.0 defaults, and failure-mode fixes.

Read [references/user-standards.md](references/user-standards.md) after `production-rules.md` whenever the task depends on the user's accumulated standards, including 九尾狐 prompts, established Format C outputs, dialogue/audio constraints, `@` tagging precision, no-dialogue reaction logic, light continuity, magic control, character behavior, or learned failure patterns.

Read [references/jiuweihu-magic-vfx.md](references/jiuweihu-magic-vfx.md) whenever a 九尾狐 prompt needs magic particles, magic attacks, enemy attacks, mark surfacing/dissolving, iris activation, clan energy colors, holy spring light, dark curse mist, or any magic VFX prompt language.

Read [references/vertical-directing.md](references/vertical-directing.md) before writing a full group, revising multi-shot continuity, planning coverage, or fixing spatial, over-shoulder, scale, eye, lighting, action, text/UI, or realism failures. Start from [assets/format-c-shot-group-template.md](assets/format-c-shot-group-template.md) when the user asks for a new reusable Format C group or template.
