---
name: shortdrama-storyboard
description: >-
  Turn a vertical short-drama script (竖屏短剧剧本) into a shot-by-shot storyboard
  optimized for AI image/video generation. Use this whenever the user uploads or
  pastes a script, episode, or scene and wants a 分镜 / storyboard / shot list /
  镜头脚本 / shot breakdown, or asks to "把剧本做成分镜", "拆分镜", "生成镜头",
  "storyboard this", or "break this into shots". Also use when the user has a
  character/asset bible and wants scenes rendered into numbered shots with camera
  language, durations, generation-mode routing (image-to-video vs text-to-video),
  and ready-to-paste generation prompts. Trigger even if the user only says
  "分镜" or "镜头" alongside any script text.
---

# Short-Drama Storyboard (剧本 → 分镜)

Convert a script into a structured, generation-ready storyboard for vertical
(9:16) AI short drama. The output is a numbered shot list where **every shot
carries a ready-to-paste generation prompt** plus the metadata a producer needs
(camera, duration, shot size, generation mode, continuity).

## Core workflow

Follow these steps in order. Do not skip the asset-scan step — consistency is the
#1 failure mode in AI short drama.

### Step 1 — Read the script and any asset bible
- Read the full script (or the requested episode/scene range) before writing any shot.
- Check whether the user has an existing **character/asset bible or 总控表**
  (consistency sheet). If yes, use its locked values (hair/eyes/sigil/energy-color/
  wardrobe) verbatim. If no, build a lightweight one first: for each named character,
  fix hair, eyes, one signature marker, palette, and any non-human features (ears,
  tails, scales). Reuse these exact tokens in every prompt so the character doesn't drift.
- Note the global style basis (era, genre, art direction, palette) and target
  generation model. Default to reading `references/prompt-craft.md` for the
  model-aware quality suffix and camera vocabulary.

### Step 2 — Segment the script into scenes, then beats
- A **scene** = one location + continuous time. A **beat** = one dramatic unit
  (an action, a reveal, a line that turns the moment).
- Map each beat to **one shot** by default. Split into more shots when a beat
  contains a camera change, a new subject, or an effect that needs its own take.
- Read `references/shot-grammar.md` for shot-sizing, pacing, and vertical-9:16 rules.

### Step 3 — Assign per-shot metadata
For each shot decide: shot size, camera movement, duration, subjects on screen,
any VFX/transformation, continuity note, and **generation mode** (see Step 4).
Keep single-subject shots wherever possible — multi-subject shots are less reliable.

### Step 4 — Route each shot to a generation mode
- **image-to-video (图生视频)** — for character close-ups, transformations, and any
  shot needing strong face/identity consistency. Requires a locked reference image
  (face card / turnaround / first-frame). Mark which reference to attach.
- **text-to-video (文生视频)** — for environment, atmosphere, crowd, and free-camera
  motion shots where identity is secondary. No reference needed.
- Rule of thumb: **hero/character = image-to-video; mood/space = text-to-video.**
- For multi-shot effects (transformations, energy casts), apply the three-beat
  structure (build → change → settle) from `references/prompt-craft.md`.

### Step 5 — Write the generation prompt for every shot
Each prompt follows the structure in `references/prompt-craft.md`:
`[camera move] + [subject + locked appearance tokens] + [one coherent action] +
[one core effect with direction] + [environment] + [lighting/mood] + [quality suffix]`.
Text-to-video prompts lead with the camera move; keep to one subject + one action +
≤3 parallel elements. Match prompt density and the quality suffix to the target
generation model; apply the Seedance 2.0 exception in `references/prompt-craft.md`
when relevant. Always append the negative-prompt line.

### Step 6 — Output using the exact template
Produce the storyboard as a Markdown document using the structure in
`assets/storyboard-template.md`. Present one scene at a time, each with a scene
header (location/time/emotional beat) followed by its numbered shots. If the script
is long (a full episode), deliver a file via the file tools rather than inline.

## Output format (shot card)

Every shot MUST use this exact card:

```
### 镜 [scene.shot] · [shot size] · [duration]
- **画面**: [one-line description of what happens on screen, in the user's language]
- **运镜**: [camera movement]
- **主体**: [characters on screen + which locked reference to use]
- **特效/转场**: [VFX, transformation, transition — or "无"]
- **生成模式**: [image-to-video 图生 / text-to-video 文生] + [reference to attach]
- **连续性**: [continuity note — costume state, time of day, what carries from prior shot]
- **Prompt**:
  ```
  [full ready-to-paste English generation prompt + quality suffix]
  ```
- **Negative**: `[negative prompt line]`
```

## Key principles

- **Consistency first.** Reuse the exact appearance tokens (hair/eyes/marker/palette)
  from the asset bible in every single prompt. Never paraphrase them.
- **One shot, one action.** A prompt that asks the subject to do two things will blur.
  Split into two shots.
- **Effects carry direction.** Energy must state its motion (gathering inward =
  charging, bursting outward = release, coiling = wrap, withering = drain). Direction
  is the meaning.
- **Vertical safe zone.** Keep the key element (face, magic focus, prop) in the central
  vertical safe zone; let particles/light overflow the top.
- **Emotion via body, not micro-expression.** AI faces are least stable; route
  seduction/tension/power through posture, hair, hands, silhouette, and effects.
- **Keep most shots 3–10s.** Use 1–3s shots for action, impact, or rapid reversals
  when the pacing table calls for them. Longer single takes drift; build set-pieces
  from multiple shots.

## References (read as needed)

- `references/shot-grammar.md` — shot sizes, pacing categories, coverage patterns,
  vertical-9:16 composition, transition types. Read during Steps 2–3.
- `references/prompt-craft.md` — the prompt structure, model-aware quality suffix, camera
  vocabulary, the three-beat effect/transformation formula, negative prompts, and the
  image-vs-text-to-video routing table. Read during Steps 4–5.

## Asset template

- `assets/storyboard-template.md` — the exact document skeleton to fill in. Copy it
  and populate per scene.
