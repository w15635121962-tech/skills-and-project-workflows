# Vertical Short-Drama Directing And Generation Repair

Use this cross-project reference for production-ready 9:16 Format C prompts. It captures the user's tested directing priorities. A direct current user instruction or a project overlay overrides any conflicting generic rule here.

## 1. Priority Order

Use this order when prompt space is limited:

1. Per-shot visible action, screen position, facing, contact, and action result.
2. Lighting source, shared environment response, and real material integration.
3. Dialogue reaction or silent reaction logic.
4. Character-specific body grammar and eyeline.
5. Audio rhythm and motion intensity.
6. Negatives as a final guardrail only.

Opening state and duration guide continuity and editing but do not replace per-shot blocking. State the correct result positively before suppressing failures with negatives.

## 2. Format C And Delivery

- Preserve the user's current field order and stated shot count. Reset `shot` numbering inside every group.
- Every full group needs: fixed quality baseline, opening-state lock, environment/spatial relation, group lighting logic, audio rule, group negatives, then complete independent shots.
- Every shot needs: `镜头`, `画面`, `微表演`, `对白反应`, `人物背景融合`, `光影`, `音频`, `运动强度`, `负面提示词`.
- Name the exact camera subject, framing, camera height/side, movement, lens, focus plane, and duration in the shot title or `镜头` field.
- Never add dialogue not supplied or requested. If no dialogue exists, prohibit mouth movement, subtitles, narration, and score while still explaining what visible event creates the silent reaction.
- Use `@` only for identifiable characters, locations, and props actually visible in that shot.

## 3. One Beat Per Shot

- Build a shot around one readable action beat: trigger, concrete action, physical consequence, and end state.
- Split a complex interaction when the action, receiver reaction, camera basis, or magic phase changes.
- Pair action and reaction. A useful short-drama chain is: establish action → receiver reaction → opponent/third-party reaction → emotional punctuation or hook.
- Give each action an intention: want → obstacle → tactic → action → reaction. Convert interior states into hands, shoulders, gaze, clothing, prop contact, distance, or a controlled pause.
- Use primary action, one micro-leak, and one counter-action when appropriate: a person acts, involuntarily leaks feeling, then suppresses or redirects it.

## 4. Vertical Composition And Coverage

- Keep the emotional face in the vertical center-safe region; keep eyes near the upper third and do not place essential action in the bottom UI-safe band.
- In 9:16, prefer foreground/background depth, upper/lower hierarchy, hallways, stairs, or diagonal staging over a horizontal two-person lineup.
- Put the core performance in the middle layer. Foreground should frame or create parallax without hiding a face; background should retain place but lower contrast and detail.
- Use full/wide frames for a spatial promise or a payoff, medium shots for readable action, medium close-ups for dialogue, and close-ups for reaction. Avoid isolated eye, lip, or hand inserts unless their surrounding body/space remains legible.
- Do not repeat the same shot size more than twice without a narrative reason. Let a rising emotion generally move medium → medium close → close; let emotional release open back out.
- For dialogue and conflict, plan usable coverage: speaker, listener, reverse, shared relation shot when stable, third-party reaction if story-relevant, and a final emotional landing.

## 5. Spatial, Axis, And Over-Shoulder Locks

- Establish the master scene geography in the first relation shot: fixed screen side, depth layer, facing, shared support plane, and a stable axis. Repeat decisive locks in every independently generated shot.
- For every over-shoulder shot, write: `camera behind A's left/right shoulder`; where A's shoulder/head occupies the frame; focal person B; camera direction along the established axis; and both bodies' facing. A shoulder-less frame is not OTS.
- Focus pulls change sharpness only. They never change actor size, left/right placement, body facing, support-plane height, or shoulder side.
- For two characters, state shared floor/bed/seat plane, realistic distance, contact shadow, and unchanged perspective. Use `left/right swap`, `axis jump`, `wrong shoulder`, `different support plane`, and `scale drift` negatives when relevant.
- Do not create ambiguous door-inside/door-outside double spaces unless the user explicitly asks for a voyeur shot. For voyeur framing, the observed person must not perform toward the watcher or camera.

## 6. Scale, Transformation, And Body Continuity

- For different-sized people, animals, or forms, anchor scale to a visible reference: hand, forearm, chair, pillow, floor joint, doorway, or tabletop. State their shared support plane and real compression/contact shadow.
- Lock form-change endpoints. For pure human form, remove all animal body parts and duplicate silhouettes. For human form retaining tails, keep one human body and attach the specified tails only at the lower back; do not leave fox head, muzzle, paws, ears, torso, or a second animal body.
- Hide animal-to-adult scale change behind one soft occlusion stage: localized energy gathers → cloth/curtain/tail/mist briefly blocks topology change → final form settles with adult scale, stable feet/hips/shoulders, and support-surface compression.
- Do not show the small animal and adult endpoint together in an uncovered frame. Do not carry small-animal proportions into the adult body.
- Use negatives as applicable: `残留兽形，双重身体，人兽叠影，狐头人身，兽形与人形同时存在，狐狸巨型化，小狐成人体积，人形缩小成玩具，尾根错位，身体缩放跳变，骨骼拉伸，面部融化`.

## 7. Lighting, Materials, Eyes, And Tears

- Execute a film/series reference through practical source direction, source quality, color relation, shadow falloff, material reflection/absorption, and continuity across shots. Do not merely name a title.
- Use one coherent lighting system per contiguous scene. A change in color or light direction requires a story reason and a new scene baseline.
- Night scenes need a named practical or motivated source, readable low-key faces, and textured darks. Avoid both dead-black compression noise and fake daytime fill.
- Make bodies share the scene's light and air: contact shadows, cloth compression, floor/seat impressions, material wear, background perspective, natural edge softness, and controlled reflections.
- Eyes require a clear gaze start and landing point. Permit only reflections from the named environment; prohibit self-lit eyes, empty gaze, dead-fish eyes, and unfocused pupils.
- If tears or wet eyes appear, write their full physical behavior: translucent saline from inner corner/lower lid, environment-only reflection, irregular gravity-led cheek path, cheekbone gathering, wet skin reflection, and restrained facial tension. Do not add crying, gasping, choking, or breath audio unless expressly permitted.

## 8. Movement, Editing, And Sound

- Camera movement needs a motive: push for psychological approach, pull for separation, follow for escape/departure, controlled drift for intimacy or unease, static for weight, and a high/low angle for power or isolation.
- Prefer simple stable movement. Use speed ramps, long take stitches, freeze effects, and morphs only as rare emotional punctuation, not default decoration.
- In action, show preparation → collision → force transfer → consequence. Let feet, weight, mud/cloth/hair, weapon pressure, and recovery communicate impact; avoid uniform robotic motion.
- Use diegetic sound only unless the user explicitly says otherwise. Adjust environment level to drama: low for secrecy, medium for active conflict, sudden reduction at an emotional hit, then a specific object or room sound as the punctuation.
- Use J-cut/L-cut, prop relay, action match, or hard cut when they serve story continuity. Do not add score, captions, narration, or unrequested speech.

## 9. Common Failure Repairs

| Symptom | Positive repair | Targeted negatives |
|---|---|---|
| Face merge / clone | Fix positions, independent facial silhouettes, hair/material separation, separate light response, distinct extras' actions | `克隆脸，融脸，人物同化，角色互换，blended-faces，duplicate-characters` |
| Character or clothing swap | Repeat visible identity/wardrobe anchor only where needed; lock screen position and silhouette | `换脸，换装，服装互换，角色互换` |
| Empty eyes | Write gaze origin, destination, and environment reflection | `眼神空洞，死鱼眼，瞳孔失焦，眼球自发光` |
| Sticker / green-screen person | State shared key light, contact shadow, material compression, air perspective, and edge falloff | `抠图感，贴纸感，绿幕残留，悬浮，接触阴影缺失` |
| Bad night image | Name a practical source, stable face exposure, retained dark texture, no competing fills | `低像素夜景，压缩色块，死黑阴影，过曝夜景` |
| Hand or tail penetration | State ownership, entry side, contact point, finger/fur direction, pressure, occlusion, and end state | `手指穿透，尾巴穿模，接触点错位，衣料无压痕` |
| UI/text gibberish | Replace complex UI with a photo/color field or one large readable element | `字幕，随机文字，伪文字，错误字母，复杂UI，水印` |
| Space rebuild | Repeat anchor furniture, floor/bed plane, axis, light direction, and only change camera view | `场景重绘，空间错位，墙体变形，地面偏移，透视错乱` |

## 10. Final Check

Before delivery, verify:

1. The visible result is positively described before negatives.
2. Every shot has one core beat, a clear receiver, and a finished action state.
3. Every visible person, prop, scale relation, support plane, gaze, and focus plane is unambiguous.
4. Every OTS locks foreground shoulder, camera side, axis, focal person, and facing.
5. Light, color, dark detail, and materials remain continuous across the scene.
6. Dialogue, mouth movement, audio, subtitles, narration, and music conform to the user's current rules.
7. Full groups respect the user-requested shot count and length range.
8. Failures are handled with a corresponding positive repair, not negatives alone.
