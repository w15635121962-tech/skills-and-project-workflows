---
name: "提示词2.6-format-c-video-prompts"
description: Convert supplied scripts, dialogue, action descriptions, storyboards, or reference images into complete Chinese Format C V2.6 AI-video prompts for short drama; also revise, audit, continue, translate, or compress existing V2.6 prompts.
---

# Format C V2.6 提示词

Use this skill only when the user requests production-ready Format C prompts, per-shot AI-video prompts, or revision/audit/compression of an existing Format C prompt. Do not use it for story analysis or an ordinary storyboard unless the user explicitly asks for the final generation-prompt layer.

## Source gate

Before writing, identify the supplied script or scene source, speaker ownership, character and wardrobe anchors, location and prop continuity, target model, aspect ratio, duration, shot count, language, and allowed audio elements. If story facts are missing, request the missing source material; do not invent plot facts or borrow another project's contract.

## V2.6 contract

Before drafting or auditing shots, read [dynamic blocking and composition](references/dynamic-blocking-composition.md). The user's 2026-10-06 requirements in that reference supersede legacy timing, static-camera, mandatory foreground-occlusion, and mixed occupancy advice. Read [the 24-image analysis](references/reference-image-analysis.md) when using these visual references; for a promotional storyboard handoff, also use [tuiwen adaptation](references/tuiwen-adaptation.md). Preserved source instructions and example plots are reference data, not new user tasks.

- Treat the current user instruction and approved source as higher priority than this skill.
- Plan before prose: causal order, blocking, 180-degree axis, screen side, support surfaces, hand ownership, contact and force transfer, lighting continuity, shot rhythm, visual flow, and every visible character's in-story eyeline.
- Convert each beat as `cause -> intention -> action -> result -> reaction -> stable endpoint -> new question`.
- One shot has one narrative task and one new piece of information. Split compound actions before drafting.
- A group is one continuous space, time, key-light direction, and color-temperature unit. Plan these boundaries outside complete dialogue turns. If source dialogue itself spans a space/time/light change, flag the conflict and choose a supported treatment with the user rather than silently splitting the turn or pretending the scene is unchanged.
- Default to 3–8 shots per group, 8–24 seconds per group, and **2.0–3.0 seconds per edited shot**, unless the current project explicitly overrides these values. Durations must sum exactly to the declared total at 0.1-second precision. Vary action and information density within that range; never force the old minimum 1.5-second duration contrast. Long dialogue remains entirely within one generation group and continues across that group’s cuts without shortening or repeating its audio; fixed-length generated clips are trimmed to the edited duration.
- Pair every entrance/reveal with its established origin, entry edge, actor path, camera trigger/path/stop, readable identity, landing position, and narrative effect. Record world and screen positions separately, preserving start → path → end and the next shot's handoff.
- Lock visible cast, off-screen cast, foreground owner, body crop, depth distances, and occupancy units. No third-person head to fill space, no double of an existing actor, and no unmotivated scale or axis jump. Triangular composition may use two people and an existing environmental anchor.
- Each shot changes an action, relationship, information state, or decision. Each complete dramatic unit carries goal → resistance → consequence with motivated actor displacement or purposeful posture/prop changes. Camera motion cannot substitute for actor performance; static holds need a specific dramatic cause and release.
- Every group header must contain: fixed quality descriptor, complete lighting tone, beat structure, shot-size/angle cycle, and visual-flow path.
- Every shot must contain these eleven fields in this order: `叙事任务（Narrative Task） | 镜头 | 画面 | 视觉引导（Visual Flow） | 微表演（Micro-Performance） | 对白反应（Dialogue Reaction） | 人物背景融合（Subject-Background Integration） | 光影细节（Lighting Detail） | 音频（Audio） | 运动强度（Motion Intensity） | 负面提示词（Negative Prompt）`.
- Put all dialogue, voiceover, ambience, and sound effects only in `音频`; put no dialogue or sound descriptions in visual fields.
- English dialogue is preserved verbatim by default. Only the current speaker may move their mouth; non-speakers stay closed-mouth.
- Every visible character needs a concrete in-story eyeline target. Unless the shot is explicitly labeled POV, prohibit looking into the lens, viewer eye contact, fourth-wall breaking, and pupils locked on the optical axis.
- `对白反应` is mandatory even when nobody speaks: state the trigger, receiver, silent participants, muscle-level facial response, gaze adjustment, body/prop response, and stable endpoint. Never write only `无台词，无口型`.
- Decisive actions are split across anticipation, launch, contact/force transfer, result, and emotional landing; cut during action and preserve object/contact/axis continuity.
- Faces remain bright and readable even in dark scenes. Expand lighting into source, side, height, softness, temperature, face highlight/shadow side, exposure, shadow landing, and material response.
- Never use `同上`, `沿用上一组`, or abbreviated fixed blocks in a complete group.

## Explicit perspective and uninterrupted dialogue groups

- Every shot's final prompt must contain a concrete **透视构图描述**: camera viewpoint and height, axis side, depth ordering and distances, screen placement and crop, comparable subject scales, named occlusion ownership, eyelines, and opening-to-ending composition. Include converging environmental lines only when visible. Use the template in the dynamic reference; composition labels alone are insufficient, and planned numerical values are guidance rather than measured source facts or guaranteed model precision.
- **A complete long dialogue turn stays in one generation group.** Establish `dialogue_unit_id → group_id` before shot planning. Cut visuals every 2–3 seconds within that group while preserving one continuous voice track and speaker identity. Never continue half a line in another group or re-synthesize the same line from its beginning at each shot.
- If the current group lacks room, move the entire turn and its necessary action/reaction into the next group. Default group duration/shot count yields to intact dialogue when the platform supports the required duration. A verified platform hard limit cannot be exceeded: flag an incompatible unit instead of silently cutting, deleting, accelerating, or submitting it.
- Record the complete text once in the first carrying shot's audio field with group-relative timing; subsequent audio fields reference the same ID and covered interval. Keep full audio units intact in actual submission, not just in group labels.

## Mandatory fixed blocks

Before drafting, read [V2.6 reference integration](references/format-c-template-v2.6.md) and the relevant sections of the bundled [V2.5 source template](references/format-c-template-v2.5-source.md). The supplied source is V2.5, preserved verbatim as the baseline for this V2.6 skill; do not describe it as an original V2.6 document. Copy section 三’s fixed quality descriptor and mandatory skin paragraph verbatim into each group header, unless an explicit project override applies. Copy section 十一’s complete tears paragraph for crying shots. Do not output maintenance appendices or revision records.

For crying shots, copy the complete bundled tears paragraph rather than reducing it to `流泪`. Add relevant negative terms for waxy/plastic skin, self-illuminating eyes, lip-sync errors, axis jumps, repetitive framing, and fourth-wall eye contact.

## Composition parameters

When planning framing, dialogue coverage, or converting a storyboard to final prompts, read [composition parameters](references/composition-parameters.md) together with the integration rules. Write focal length, camera height, crop, subject occupancy, headroom, look room, foreground ownership, axis side, and eyeline target where relevant in the existing eleven fields. Preserve Format C output; the manual’s JSON examples are mappings, not a request to change output format. Use its numerical ranges as starting points adjusted to the approved aspect ratio, blocking, and shot task.

## Revision boundary

When revising an approved prompt, freeze all unrequested story facts, dialogue, timing, shot count, blocking, axis, props, lighting, field order, and project anchors. Change only the requested shots or demonstrated failure points. Never claim platform acceptance or successful generation unless it was actually tested.
