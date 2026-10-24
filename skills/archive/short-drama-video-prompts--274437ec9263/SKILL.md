---
name: short-drama-video-prompts
description: Create, revise, or audit cinematic AI-video prompts and editing-first storyboards for vertical short dramas, especially Chinese Format C shot groups. Use when the user asks for video prompts, prompt groups, shot breakdowns, continuity locks, character blocking, lighting continuity, dialogue reactions, performance beats, or generation-failure fixes such as face merging, bright night scenes, UI gibberish, or hand penetration.
---

# Short Drama Video Prompts

Create production-ready Chinese video prompts with an editing-first mindset. Preserve the user's established template unless explicitly asked to redesign it.

## Workflow

1. Identify the requested deliverable: full prompt group, a single shot revision, storyboard analysis, or prompt audit.
2. Extract immutable facts first: characters on screen, blocking, costume anchors, props, time of day, dialogue, emotional turn, and any supplied reference images.
3. Plan coverage before writing long prompts. Prioritize emotion, story, rhythm, eyeline, 2D composition, then 3D continuity. Include clean reverse shots and over-shoulder coverage for dialogue scenes when the user asks for a storyboard.
4. Keep every shot independently generatable while preserving continuity: repeat decisive blocking, light direction, wardrobe anchors, and prop locations inside the relevant shot.
5. Use Format C by default. Begin a group with fixed quality language, opening-state lock, environment, and lighting baseline; then write each shot with duration, camera, image, micro-performance, dialogue reaction, physical integration, lighting, audio, motion intensity, and negatives.
6. Perform a final failure-mode pass using `references/production-rules.md`.

## Format C Rules

- Write `Shot n`, then `duration`, then `镜头`, `画面`, `微表演`, `对白反应`, `人物背景融合`, `光影`, `音频`, `运动强度`, and `负面提示词`.
- State whose shot it is and the exact framing. Avoid isolated eye, lip, hand, or body-part close-ups; use contextual close shots that retain performance and spatial context.
- Use `@` only for characters, props, or scenes visibly present in that shot. Do not tag an off-screen character merely because the dialogue mentions them.
- When a group contains multiple distinct extras, put the cast-separation constraint inside that specific group-scene shot, not as a universal opening block.
- If no dialogue exists, explicitly prohibit dialogue mouth movement, subtitles, voice-over, and background music. Use diegetic sound only.
- Keep the user's requested shot count and word-count limit. Reset shot numbering to 1 per group.

## Continuity and Performance

- Give the model an unambiguous spatial relation in each shot: left/right, foreground/background, seat count, Z-axis movement, or stable object anchors.
- Do not use complex "inside/outside the door" wording unless a voyeur shot is essential. Do not let subjects of a voyeur shot play directly to the voyeur.
- Keep reverse shots on the same 180-degree axis. Name foreground shoulder and focal subject when using over-shoulder framing.
- Translate weak facial-only beats into body grammar: breath, shoulder, neck, hand, step rhythm, clothing compression, or a visible physical carrier such as moving hair and dust.
- For physical contact, specify hand ownership, entry side, contact point, natural finger bend, compression, occlusion, and contact shadow. Add anti-penetration negatives.

## Lighting and Realism

- Treat lighting as the primary quality control. Reference a mature film or series only when translating it into actual source direction, color relationship, shadow strategy, material response, and a stable look across adjacent shots.
- Never write eye-light or eye-highlights as a standalone effect. Use environment-constrained natural eye reflection; prohibit self-lit eyes.
- For night scenes, use low-key but readable exposure. Avoid contradictory instructions such as "no light source" plus "well-lit face." Avoid repeated phrases such as "face fully lit" that force artificial fill.
- Make people physically belong to the environment: contact shadows, shared color temperature, consistent reflections, material wear, cloth physics, and stable perspective.

## Safety and Scope

- Keep romance age-appropriate and non-explicit, especially in school or uniform contexts. Redirect explicit sexual actions, nudity, or sexualized body framing to emotional tension, fully clothed intimacy, or non-sexual performance beats.
- Preserve user-supplied dialogue when safe; when it is explicit or unsuitable for the setting, offer a concise safe substitute that keeps the dramatic intent.

## Reference

Read [references/production-rules.md](references/production-rules.md) before producing a full group or auditing an existing prompt. It contains the detailed Format C checklist, wording patterns, and generation failure fixes.
