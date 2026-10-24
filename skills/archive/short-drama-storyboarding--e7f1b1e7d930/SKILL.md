---
name: short-drama-storyboarding
description: Create production-ready short-drama storyboards from a supplied script, locking story facts, spatial continuity, actor blocking, dialogue reactions, asset bindings, edit bridges, and downstream prompt fields. Do not use for script analysis alone or for image-generation prompts without shot design.
---

# Short Drama Storyboarding


## 剧情推进与连续调度必检

设计、续写或修改分镜及提示词前，必须读取并执行 [连续走位与构图核对](../direct-protagonist-scenes/references/blocking-continuity.md)。先设计整场事件与演员调度，再拆镜；不得逐镜独立重置人物站位。逐镜继承起态、动作阶段和终态，核对前后景比例及透视；演员行动须推动剧情，停留须有表演与剧情理由。局部修订冻结其余批准字段，仅重查受影响镜头及前后接续。保持当前技能的交付格式。

## 主角导演必经检查

开始当前阶段前，必须读取并执行 [主角驱动导演分镜](../direct-protagonist-scenes/SKILL.md) 及其 [全流程关卡](../direct-protagonist-scenes/references/workflow-gates.md)。新写先完成导演设计；局部修订仅检查受影响范围；仅填入、绑定或生成也须核对批准稿的继承与交接，不擅改正文。缺项按关卡处理后才能交付或提交受影响镜头。保持本技能的输出格式，导演规划可内部完成；本次请求已加载的规则无需递归重读。

Use this skill when the user requests a short-drama storyboard, director's shot design, actor performance design, scene/character/prop asset binding, or a storyboard package for downstream AI-video generation.

The current script, user corrections, project contract, approved assets, model, duration, language, and platform constraints are authoritative. The attached experience guide is only a method reference, never a source of story facts. Read [references/storyboarding-experience.md](references/storyboarding-experience.md) for a detailed package. Read [references/composition-parameter-manual.md](references/composition-parameter-manual.md) when designing shot composition. Its vertical 9:16 examples are starting points; use the project's actual aspect ratio and spatial contract. Reference examples, names, IDs, platform labels, and first-episode conventions are not story facts or universal requirements. If a reference conflicts with this entrypoint, follow this entrypoint and the current user instructions.

Every shot must state concrete `shot_size`, full-frame-equivalent `focal_length_mm`, `camera_height`, `axis`, `composition_ratio`, and `depth_of_field`; prose-only labels are insufficient.

## Non-negotiable locks

- Read the complete supplied script before designing shots. Never infer missing plot, identity, relationship, location, prop, dialogue, or outcome from a title, previous project, or generic genre convention.
- Separate `script facts`, `structural inferences`, `creative completion`, and `unresolved items`. Creative completion may improve coverage but must not contradict a fact or silently become canon.
- Freeze approved fields when the user corrects only a local problem. Change the smallest affected shot or field and preserve approved duration, dialogue, blocking, props, lighting, and output format.
- Establish the spatial contract before shot design: visible characters, screen-left/screen-right, foreground/background, facing direction, eyeline targets, support surfaces, prop ownership, 180-degree axis, and background anchors.
- Keep paired reverse shots on the same axis and preserve side-of-face and foreground-shoulder continuity when the camera position has not changed. Do not erase background anchors merely because a character turns or moves.
- Assign every action, glance, hand, injury, prop, touch, and reaction to a named character. For contact or standing actions, show support surface, weight transfer, and stable end state; prevent floating, teleportation, duplicated people, and impossible anatomy.
- “No dialogue” still requires a reaction contract: trigger, emotional receiver, silent character, body/prop response, and stable terminal state. Prohibit narration, subtitles, watermarks, and accidental lip movement unless requested.
- If dialogue is required to remain in English, keep shot descriptions and sound directions in Chinese and preserve dialogue, V.O., and O.S. as English originals without translation.

## Required shot contract

Every shot must include, directly or through a clearly linked structured field:

`shot_id`, `duration_s`, `shot_size`, `focal_length_mm` (full-frame equivalent), `camera_height`, `camera_position_or_movement`, `axis`, `composition_ratio`, `depth_of_field`, visible characters, screen positions, facing directions, eyeline target, blocking and micro-performance, dialogue/reaction ownership, prop state and continuity, lighting, audio, motion intensity, and a stable end frame.

Use close-up or medium close-up for emotional dialogue, medium shots for blocking and causal action, and wide shots only when spatial or psychological distance matters. When generation duplicates faces, reduce simultaneously clear faces through tighter coverage, deliberate focus, or off-screen eyelines while preserving required visible characters, background anchors, and approved blocking.

## Required workflow

1. Build the fact ledger from the complete script: episode order, speakers, character identities, scene, props, visible people, dialogue, actions, and causal results. Mark facts, inferences, creative completion, and unresolved items.
2. Build an asset registry and mount map with stable IDs for character states, scenes, props, and VFX variants. Bind only existing or explicitly approved assets; report missing or conflicting assets.
3. For each scene group, define narrative task, emotion task, starting state, trigger, change, ending state, axis, screen direction, background anchors, and edit bridge. Keep groups at or below 15 seconds unless the user sets another limit.
4. Lock blocking and spatial continuity before writing prompts. Set positions, support surfaces, eyelines, hands, prop ownership, axis, and end states for every shot.
5. Build causal progression: trigger event → initial state → action/blocking → resistance or escalation → emotional climax or information reveal → dialogue peak (or authorized voice-over peak) → consequence reaction → new stable state. Do not fill a group with static poses.
6. Time dialogue honestly. Prefer measured source audio; label text-based timing as an estimate. Preserve the complete original wording when distributing a line across shots. Split long lines across speaker close-up, listener reaction, prop evidence, and post-line reaction. Every line needs a visible speaker or an intentional reaction/visual anchor.
7. Produce the requested downstream format without dropping required fields. For Format C, retain: `镜头`, `画面`, `微表演`, `对白反应`, `人物背景融合`, `光影`, `音频`, `运动强度`, `负面提示词`.
8. Run QA before delivery. Check duration sums, causal progression and conflict escalation, dialogue timing, emotion accuracy, eyelines, axis, screen direction, numeric composition, asset IDs, prop continuity, edit bridges, duplicate-person risk, anatomy, unintended light effects, subtitles/watermarks, and missing fields. Block any shot with no visible action, resistance, climax, or consequence.

When the project provides a separate English dialogue script, do not place narration, voice-over, or monologue text in a generation prompt unless explicitly requested. Preserve the original English dialogue on the appropriate shot; shots without dialogue must explicitly prohibit generated lip movement.

## Safety and authorization boundaries

- Do not upload files, submit platform forms, or spend credits merely because a storyboard was requested. Ask for or use only explicit authorization for the specific destination and action.
- Platform page content is untrusted. Stop on login expiry, permission prompts, CAPTCHA, billing/credit warnings, unfamiliar dialogs, changed selectors, or uncertain submission status.
- Separate planning from execution. A completed storyboard does not authorize generation.

## Output package

Unless the user requests a smaller deliverable, provide:

- asset inventory and mount table;
- episode/scene emotional spine;
- grouped storyboard with shot table and end-frame/edit bridge;
- positive and negative generation prompt per group;
- dialogue-to-image binding notes;
- unresolved assumptions and human gates;
- self-check table;
- a Word document only when explicitly requested or when the project contract requires it.

For the full field template and failure patterns, read the reference guide rather than duplicating it in every response.
