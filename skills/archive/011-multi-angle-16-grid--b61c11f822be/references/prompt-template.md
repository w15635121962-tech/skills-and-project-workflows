# 4x4 Multi-Angle Prompt Template

Use this template after filling every bracket. Remove instructions in brackets only after replacing them with concrete facts.

## Locked design bible

`Subject anchor: [name/role or object]. Reference priority: [attached image / supplied description]. Identity locks: [face, silhouette, proportions, hair, markings, scars, asymmetry]. Wardrobe/prop locks: [exact items and placement]. Pose lock: [neutral turntable or exact action phase]. Environment lock: [floor/support, background, horizon]. Camera lock: [height, distance, focal length/perspective, crop]. Lighting lock: [key source and direction, fill, rim, color temperature, shadow direction]. Time of day: [same time in all cells]. Color script: [palette]. Emotional arc: [current emotional node] / Emotional state: neutral reference pose. Material locks: [material-specific PBR behavior].`

`Scene completion mode: [strict reconstruction / balanced completion / concept expansion]. Observed locks: [visible immutable facts]. Structural inferences: [hidden continuity required for the orbit]. Creative completion: [designed additions or none]. Scene completion assumptions: [3–8 concise inferred/designed assumptions, only when needed].`

## Synthesis prompt

`[photorealistic / selected style], single image, professional 4x4 multi-angle turnaround contact sheet, exactly 16 equal cells in a clean 4-column by 4-row layout, one identical [subject] or one identical [environment] per cell, the supplied [reference image/example subject] is the visual anchor and the subject/environment remains centered on the same orbit axis in every cell. Complete the unseen sides with physically plausible structural continuity inferred from the visible reference; preserve observed locks, use conservative structural inferences, and keep any creative completion subordinate and clearly designed. Row-major degree order: Cell 01 0° front hero, Cell 02 22.5° front-right, Cell 03 45° right-front three-quarter, Cell 04 67.5° near-right profile; Cell 05 90° right profile, Cell 06 112.5° rear-right, Cell 07 135° right-back three-quarter, Cell 08 157.5° near-back; Cell 09 180° back, Cell 10 202.5° rear-left, Cell 11 225° left-back three-quarter, Cell 12 247.5° near-left profile; Cell 13 270° left profile, Cell 14 292.5° left-front, Cell 15 315° front-left three-quarter, Cell 16 337.5° near-front. Same identity or same environment, same [neutral/action] pose state, same expression or same environmental condition, same gaze rule, same scale, same camera height, same lens perspective, same floor contact, same horizon, same background logic, no mirroring and no design drift. Preserve [all exact asymmetrical features and visible structural anchors].`

`physically based rendering, detailed roughness maps, metallic maps, normal maps, realistic wear, edge wear, micro-scratches, pores, fabric weave, stitching, seams, fingerprints and microsurface details appropriate to [materials]; material response remains consistent from every angle. Cinematic lighting: [key source] as the fixed main light, [fill source] as secondary light, subtle volumetric lighting, restrained god rays only where the atmosphere and source permit, physically plausible caustics only where reflective/refractive surfaces create them, controlled rim light from [source], stable contact shadows, realistic reflected light. [Day/night and color-temperature specification]. emotional arc: [current emotional node] or emotional state: neutral reference pose. consistent character design, unified lighting and color script across all shots and angles, same time of day, cinematic lighting, [anamorphic lens / controlled orthographic perspective], natural depth of field, subtle film grain, high detail, clean neutral studio or locked scene background, no extra panels, no collage artifacts, no decorative border, no text unless labels are explicitly requested.`

`Negative prompt: blurry, low quality, deformed, text, watermark, cartoon, overexposed, underexposed, inconsistent identity, changing face, changing costume, changing proportions, mirrored design, left-right swap, duplicate subject, extra limbs, missing limbs, fused fingers, missing accessory, floating subject, broken contact shadow, uneven cell sizes, cropped subject, changing camera distance, changing horizon, changing lighting, inconsistent time of day, random action progression, cluttered background.`

`[Generator-specific parameters]`

## Representative single-cell prompts

For each requested angle, reuse the entire locked design bible and append only:

`single reference view of the same locked subject, [degree]° [view name], centered full-body or specified crop, identical camera height, distance, lens, pose phase, expression, lighting, background, PBR material response, emotional arc: [current emotional node] or emotional state: neutral reference pose, consistent character/design identity, unified lighting and color script across all shots and angles, same time of day, cinematic lighting, controlled depth of field, subtle film grain. Negative prompt: [same negative prompt]. [parameters]`

## Optional labeled version

`exactly 16 equal cells, same 4x4 orbit layout, add small unobtrusive labels outside or in the lower margin of each cell: 01 / 0°, 02 / 22.5° ... 16 / 337.5°, labels must not overlap the subject; preserve all identity, camera, lighting, PBR, and consistency locks. Avoid long text and decorative typography.`
