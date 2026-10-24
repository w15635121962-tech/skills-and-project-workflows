---
name: shortdrama-storyboard-qc
description: Create, audit, and automatically repair generation-ready vertical short-drama storyboards. Use when the user asks to 拆分镜、做分镜、生成镜头、检查分镜、自检分镜、补镜头、增加镜头量、丰富视听语言、优化人物情绪、修复镜头节奏，or turn a script/episode/scene into a shot list that must automatically fill missing narrative coverage, reactions, audiovisual layers, emotional beats, continuity locks, and AI-video prompts. Also use for the 九尾狐 project, where character-specific emotion and nine-tail generation constraints must be enforced.
---

# Short-Drama Storyboard QC and Auto-Repair

Turn a script into a complete, generation-ready 9:16 storyboard, or audit an existing storyboard and directly repair it. Do not merely list problems: add, split, reorder, or rewrite shots until the result passes.

## Required resources

- Read [references/quality-rules.md](references/quality-rules.md) completely before planning or auditing shots.
- When the task belongs to the 《九尾狐驯养指南》 project, also read [references/jiuweihu-overlay.md](references/jiuweihu-overlay.md) and the project sources it routes to.
- Use [assets/storyboard-qc-template.md](assets/storyboard-qc-template.md) for the final deliverable.

## Choose the workflow

- **Script only**: read the full requested script range, build the storyboard, then run the complete QC and auto-repair loop.
- **Existing storyboard**: read the matching script and asset bible first, audit the storyboard, repair all defects, renumber it, and return the complete revised version.
- **Partial scene or selected shots**: preserve surrounding continuity from available material; repair the requested range and state any inherited opening/closing state.
- **No asset bible**: build a lightweight lock table for every named character: hair, eyes, signature marker, palette, wardrobe, non-human traits, and energy color. Reuse exact tokens without paraphrasing.

Do not stop for non-critical clarifications. Infer runtime, generation model, and style from project files when possible; otherwise use the rules below and label the assumption.

## Workflow

### 1. Lock immutable facts

Read the full script range and relevant project material. Extract:

- scene location and continuous time;
- characters, blocking, wardrobe, props, magic state, injuries, wetness, and time of day;
- verbatim dialogue and who hears it;
- emotional turn, action result, and scene-ending hook;
- supplied face, costume, prop, scene, first-frame, or turnaround references;
- target generation model and prompt-density requirements.

Never change plot facts, safe dialogue, relationships, identity anchors, costume assignments, or magic rules to make the storyboard easier.

### 2. Segment scenes and beats

Treat one location plus continuous time as a scene. Treat every action, reveal, decisive line, reaction, choice, and consequence as a dramatic beat.

Plan each beat as one effective shot by default. Split when the subject, camera basis, action, emotional focus, or effect phase changes. Prefer one subject, one coherent action, and one core effect per shot.

### 3. Calculate the functional shot floor

Build the required coverage table before writing long prompts. Calculate:

```text
N_function = sum of non-mergeable coverage units
N_time = ceil(scene duration / target average shot length)
N_floor = max(N_function, N_time)
missing = max(0, N_floor - effective existing shots)
```

Do not count repeated atmosphere shots, synonymous facial close-ups, or shots without new narrative/emotional information as effective. When short, automatically add the highest-priority missing functions from `quality-rules.md`; do not ask for permission.

### 4. Draft generation-ready shot cards

For every shot assign:

- scene.shot number, shot size, duration, lens, angle, movement, and focal target;
- one visible subject/action and precise vertical blocking;
- micro-performance plus 0–5 emotion intensity;
- dialogue/reaction logic and diegetic audio layers;
- effect/transition, lighting integration, continuity state, and generation mode;
- full ready-to-paste prompt and relevant negatives.

Use image-to-video for identity-critical hero shots, emotional close coverage, transformation, and signature moments. Use text-to-video for environment, atmosphere, crowds, and free-camera movement. Attach the exact reference required.

### 5. Run the auto-repair loop

Audit in this order:

1. narrative cause/effect and beat coverage;
2. effective shot count and one-shot-one-action compliance;
3. character emotion loop and listener reactions;
4. blocking, axis, identity, wardrobe, props, magic, and lighting continuity;
5. visual-language variety and 9:16 composition;
6. diegetic sound variety and dialogue/mouth logic;
7. AI-generation risks: contact, crowds, hands, tails/wings, transformations, UI/text, night exposure.

Create a defect queue using `NAR`, `QTY`, `EMO`, `CONT`, `VIS`, `AUD`, and `GEN`. Repair higher-priority defects first. Add or split shots rather than overloading an existing shot. After repair, renumber the full storyboard and preserve an old-to-new mapping.

Repeat at most three times. Pass only when the score is at least 85/100, all hard gates pass, and no red-line defect remains. If a third pass still fails, use the conservative fallback: split overloaded shots, add listener reactions and spatial relations, reduce simultaneous effects, then report any truly irreducible source ambiguity.

### 6. Deliver the complete result

Output in this order:

1. `A. 自检结论`
2. `B. 缺陷清单`
3. `C. 自动修复日志` with old-to-new shot mapping
4. `D. 修复后完整分镜`
5. `E. 复检统计与最终得分`

Always return the complete repaired storyboard, not only advice or inserted shots. For a long episode, write the result to a Markdown file and link it.

## Non-negotiable production rules

- Keep the key subject inside the central vertical safe zone; stage two people in foreground/background or upper/lower depth rather than a horizontal lineup.
- Preserve the 180-degree axis and repeat decisive spatial anchors inside relevant shots.
- Express emotion through breath, shoulders, hands, steps, cloth pressure, hair, tails, wings, scales, props, and distance before relying on facial micro-expression.
- Use diegetic sound only unless the user explicitly requests otherwise. With no dialogue, prohibit speaking mouth motion, subtitles, voice-over, and background music.
- Keep lighting direction, ambient source, shadow strategy, and palette stable across a contiguous scene.
- For contact, name hand ownership, entry side, contact point, finger bend, compression, occlusion, and contact shadow.
- For crowds, lock distinct faces, hair, wardrobe, and positions; add anti-cloning and anti-swap negatives.
- For transformations and process effects, split into build → change → settle; obscure the topology-changing peak.
- Preserve the user's established output template if they explicitly require one, while still adding the QC report and repair log around it.
