---
name: multi-angle-16-grid
description: Create a production-ready 4x4 multi-angle reference grid for a character, creature, prop, costume, vehicle, or environment, automatically completing plausible hidden scene details from a supplied reference while separating observed facts from designed additions. Use when the user asks for 16-grid, turntable, turnaround, orbit views, multi-angle reference sheets, or a single grid image containing multiple angles. Do not use for ordinary storyboards, unrelated contact sheets, or independent images with no cross-angle consistency requirement.
---

# Multi-Angle 16-Grid

## Purpose

Turn a supplied image, design brief, script scene, or subject description into one coherent 4x4 grid image. The grid is a reference asset, not sixteen unrelated illustrations: preserve the same identity, proportions, costume, materials, pose state, lighting setup, camera height, lens language, and time of day across all cells.

The default subject-centered orbit is 16 views at 22.5° increments. Define the orientation convention before writing prompts: 0° is the front hero view, 90° is the subject's right profile, 180° is the back, and 270° is the subject's left profile. If the user supplies a different convention, follow it and state it explicitly. For a subject with a meaningful front/back or left/right asymmetry, preserve that asymmetry and never mirror the design.

## Input handling

Extract and lock these facts before generating a prompt:

- subject identity and reference-image priority;
- body or object proportions, silhouette, face, hair, markings, damage, accessories, and asymmetrical details;
- wardrobe, prop state, material families, construction seams, and physically plausible wear;
- neutral turntable pose or requested action pose, with feet/contact points and support surfaces fixed;
- background/stage, camera height, focal length or perspective, crop, and aspect ratio;
- lighting direction, key/fill/rim sources, color temperature, time of day, and shadow direction;
- intended generator and any requested parameters.

If a reference image is provided, treat it as the identity authority. Do not invent hidden details that cannot be inferred; mark them as designed additions only when the user asks for a concept rather than a faithful turnaround. If the user gives no model, use a model-neutral prompt and include the requested aspect-ratio suffix only when it is valid for the chosen generator.

## Automatic scene completion

When the input shows only one side of a scene or environment, automatically complete the unseen angles so the 16-grid remains usable as a spatial reference. Read [references/scene-completion.md](references/scene-completion.md) for the completion protocol. The default is `balanced completion`: preserve visible facts, infer only what is structurally necessary, and add restrained cinematic details that belong to the same location.

Before writing the final prompt, separate the scene into three layers:

- `Observed locks`: directly visible and immutable elements, including geometry, layout, signs, vehicles, materials, weather, shadows, and color relationships.
- `Structural inferences`: hidden continuations needed for plausible 22.5° viewpoints, such as the backs of buildings, continuation of a wall, unseen road surfaces, cable paths, roof edges, doors, utility connections, and occluded support points. These must follow visible scale, construction logic, perspective, and urban function.
- `Creative completion`: optional atmosphere or background additions that are not visible but improve a coherent concept asset. Keep them subordinate to the reference and label them as designed additions in the design bible.

Do not invent named characters, plot events, logos, readable sign text, exact addresses, brands, or story facts from a location image. Preserve visible text as approximate sign shapes and color blocks unless the user explicitly requests text reconstruction. If an unseen area is genuinely underdetermined, choose the least dramatic, most physically plausible continuation and state the assumption briefly; do not ask for clarification when a conservative completion can satisfy the request.

For environment references, complete by spatial adjacency: extend brick courses, window rhythms, fire escapes, utility conduits, curb lines, pavement cracks, drainage, shadow direction, and atmospheric perspective from the visible side. Keep all completed geometry subordinate to the central orbit axis. Do not turn one street into a different neighborhood, add a landmark, or introduce a new dominant color or light source.

For characters or props, automatic completion may infer hidden surfaces, backs of garments, hair volume, fasteners, construction seams, and plausible wear, but must preserve silhouette, proportions, asymmetry, pose phase, and material family. Never use completion to alter identity, age, body type, costume design, or action.

The output must include a short `Scene completion assumptions` block before the synthesis prompt whenever any hidden geometry or design detail was completed. This block should list no more than 3–8 high-impact assumptions and distinguish `inferred` from `designed`. If the user requests strict reconstruction, set creative completion to none and flag uncertain hidden areas rather than embellishing them.

## Required construction

Always produce:

1. a compact locked design bible;
2. a 16-cell angle map in reading order, with each cell labeled by index and degree;
3. one complete synthesis prompt for a single 4x4 image;
4. representative single-cell prompts, normally 0°, 45°, 90°, 135°, 180°, 225°, 270°, and 315°;
5. a negative prompt and a short verification checklist.

When the user asks for “图中的示例” or examples in the grid, place the example subject at the center of the orbit specification and identify the example as the visual anchor. If no image is attached, use a clearly marked `[主角/主体参考图]` placeholder rather than pretending to see one. The center/orbit anchor means the subject remains the same person or object in every cell; it does not mean adding a seventeenth cell unless the user explicitly requests a center cell.

The synthesis prompt must state all of the following in positive language:

- `single image, 4x4 contact sheet, exactly 16 equal cells, one subject per cell`;
- the 16 degree positions in row-major order;
- `same subject centered in every cell, same neutral pose or locked pose state, no design drift`;
- `orthographic or controlled perspective turntable` as appropriate;
- consistent character/design identity, unified lighting and color script, same time of day;
- physically based rendering, detailed roughness/metallic/normal maps, realistic wear, microsurface detail, and material-specific responses;
- cinematic lighting, anamorphic or specified lens behavior, controlled depth of field, subtle film grain;
- `emotional arc: [current emotional node]` for a narrative character, or `emotional state: neutral reference pose` for a non-narrative asset;
- visible contact shadows and stable ground/support relationship;
- a clean unobstructed grid layout with no extra panels, duplicates, captions, watermarks, or decorative borders unless labels are requested.
- automatic completion assumptions, when the reference does not reveal all sides of the subject or scene;

Do not rely on “same as previous” or “consistent” alone. Repeat the identity anchors and the exact asymmetric features in the synthesis prompt and in representative prompts. For a moving/action pose, keep the action phase identical across cells; do not turn the grid into sixteen sequential animation frames.

## Angle map

Use this default row-major map unless the user specifies another order:

| Cell | Angle | View |
|---|---:|---|
| 01 | 0° | front hero |
| 02 | 22.5° | front-right three-quarter |
| 03 | 45° | right-front three-quarter |
| 04 | 67.5° | near-right profile |
| 05 | 90° | right profile |
| 06 | 112.5° | rear-right three-quarter |
| 07 | 135° | right-back three-quarter |
| 08 | 157.5° | near-back view |
| 09 | 180° | back |
| 10 | 202.5° | rear-left three-quarter |
| 11 | 225° | left-back three-quarter |
| 12 | 247.5° | near-left profile |
| 13 | 270° | left profile |
| 14 | 292.5° | left-front three-quarter |
| 15 | 315° | front-left three-quarter |
| 16 | 337.5° | near-front view |

The grid is a spatial orbit, not a collage. Require identical scale, eye line, camera distance, horizon, floor height, and background in all 16 cells. For faces, keep gaze and expression locked unless the request explicitly calls for a gaze turn; camera angle alone must not change the facial expression.

## Prompt blocks

Use the reusable prompt structure in [references/prompt-template.md](references/prompt-template.md). Put generator-specific parameters at the end, after the negative prompt. For Midjourney, append the user's requested suffix or the default `--ar 2:1 --stylize 650 --v 6 --q 2 --style raw --sref` only if Midjourney is explicitly selected. For Flux, write “high detail, reference strength: [value]” and do not invent unsupported command-line flags. For other generators, provide natural-language settings rather than pretending a universal parameter syntax exists.

## Failure prevention

Before delivery, check:

- exactly 16 cells and exactly one subject per cell;
- degree order is stated and matches the visual direction;
- no accidental mirror image, extra limb, changing face, changing costume, or missing accessory;
- front/back, left/right, scars, labels, buttons, seams, and prop placement remain identifiable;
- PBR details describe actual materials rather than generic “high quality”;
- key/fill/rim, volumetric lighting, god rays, caustics, and highlight behavior are attributed to real external sources; no self-emitting eyes/skin/scales unless explicitly designed;
- the grid is not asked to render long readable text. If labels are needed, provide a separate labeled-layout prompt and warn that image-model typography may be unreliable;
- negative prompt covers `blurry, low quality, deformed, text, watermark, cartoon, overexposed, underexposed, inconsistent identity, mirrored design, duplicate subject, extra limbs, missing details, uneven cells, cropped subject, changing camera, changing lighting`.

If the user requests a storyboard contact sheet as well as a 16-grid turnaround, keep them separate: the turnaround preserves viewpoint consistency, while the storyboard preserves shot-specific action and emotion. Do not merge their incompatible requirements into one image.
