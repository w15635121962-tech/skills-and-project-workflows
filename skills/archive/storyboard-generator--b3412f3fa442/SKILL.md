---
name: storyboard-generator
description: "Generate professional cinematic storyboards (分镜脚本) from movie or short film scripts. Includes built-in self-review, optimization, and full script fidelity. Produces detailed shot-by-shot professional breakdown with camera angles, movements, framing, lighting setups, duration estimates, and AI image-ready prompts. Also supports industrial-grade character costume design (Detail Sheet + Turnaround View) and prop concept design (Split View tech sheet + deconstruction). Triggers: generate storyboard, create fenjing, 剧本生成分镜, professional storyboard from script, optimize script and make shot list, 分镜 from 剧本, storyboard this script, 剧本转分镜, 拆分镜, 角色服化道, 服装设计, Detail Sheet, Turnaround View, 道具设计, 道具拆解, 道具技术图, prop design, prop concept, prop tech sheet, costume design."
agent_created: true
---

# Professional Storyboard Generator from Script

## MANDATORY: Execute ALL 5 phases in order. Never skip self-inspection (Phase 2). Full script fidelity is non-negotiable — never omit, summarize, or condense any dialogue, action, or scene.

## Phase 1: Ingestion & Structured Parsing

Accept script as pasted text, file path (use Read tool), or URL.

**Full Fidelity Parsing (Mandatory):** Read and index the COMPLETE script. Create an exhaustive inventory:
- Every scene heading (INT./EXT., location, time)
- Every single line of dialogue with speaker attribution and parentheticals
- Every action/description block
- Every transition or slugline

Parse into:
- **Header**: Title, Writer, Genre, Tone, Target length, Aspect ratio (default 2.39:1 cinematic)
- **Logline / Premise** (infer if missing)
- **Complete scene-by-scene inventory** with dialogue count
- **Character bible** (main + supporting, key traits, arcs)
- **Key props, symbols, recurring motifs**

Output a "Script Summary" section (1-2 paragraphs + bullet metadata) plus note: "Full script loaded — X scenes, Y dialogue lines, Z action blocks. 100% coverage verified at end."

## Phase 2: Rigorous Self-Inspection & Optimization (Non-Negotiable)

Treat script as a professional script doctor + director + cinematographer. Output the full "Script Health Report" visibly.

### Mandatory Audit Checklist (scene-by-scene + globally):

- **Plot & Logic**: Holes, contradictions, unresolved setups, forced coincidences. Propose concrete fixes.
- **Pacing & Structure**: Slow sections, info dumps, weak act breaks. Recommend trims, expansions, montage inserts, scene reordering.
- **Visual Storytelling Audit**: Flag every "tell" (exposition via dialogue) and convert to "show" opportunities. Suggest specific shots/symbols.
- **Dialogue & Character**: Stilted lines, on-the-nose dialogue, unique voices. Suggest rewrites for subtext, economy, physical actions that reveal.
- **Cinematic Language**: Identify 3-7 "signature shots" that define the film's look. Define global visual language (color palette, lens choice, movement style, lighting philosophy).
- **Tone & Genre Fidelity**: Every shot supports intended emotion/genre.
- **Production Practicality**: Note VFX-heavy shots, location challenges, continuity risks.
- **Modern Standards**: Inclusive representation, avoid lazy stereotypes.

### Output of Phase 2 (always show):
- **Script Health Score** (out of 10) with justification
- **Issues Found** (Critical / Major / Polish)
- **Specific Optimizations Applied** (list changes)
- **Revised Script Excerpts** (bold for additions, strikethrough for deletions)
- **Director's Vision Statement** (2-3 sentences)

## Phase 3: Professional Cinematic Storyboard Creation

Break the **optimized** script into industry-standard shots. Number shots globally (SHOT 001, 002...) and per scene (e.g., 3.4 = Scene 3, Shot 4).

### For Every Scene:
- Scene header + purpose (story beat it delivers)
- Recommended total shots + rationale
- Overall lighting/mood

### For Each Individual Shot — Use This Exact Template:

```
**SHOT 047 – 4.2**
**Scene**: INT./EXT. LOCATION - TIME (post-optimized)
**Framing**: [Shot size], [composition details], [DOF notes]
**Camera**: [Movement], [lens], [duration]
**Action/Blocking**: [What happens in frame, character blocking, micro-expressions]
**Lighting & Color**: [Key light position + film reference], [color palette], [mood]
**Duration**: [seconds] (hold Xs on [key moment] for impact)
**Sound/Dialogue**: [Lines, SFX, score notes]
**Optimization Note**: [What was improved from original]
**AI Image Prompt (copy-paste ready)**: "[Full prompt with photorealism layer]"
```

### Professional Standards in Every Shot:
- Always start new location with wide/establishing or revealing master shot
- Vary angles and sizes: never more than 2 consecutive similar framings
- Use cinematic grammar: OTS for tension, low-angle for power, high-angle for vulnerability, Dutch for unease, rack focus for revelation
- Movement motivated by emotion or action (never random)
- Inserts & cutaways for information, irony, or foreshadowing
- Emotional beats get time (lingering close-ups or slow moves)
- Action scenes: multiple coverage angles, whip pans, crash zooms, slow-mo inserts
- Dialogue scenes: master + clean singles + OTS + reaction inserts + prop close-ups
- End scenes with strong visual button or transition setup

### Global Elements (define once):
- Film-wide visual language
- Recurring visual motifs
- Color psychology per character/arc

### Mandatory Reference Modules — Load as needed:

When generating prompts for specific scene types, load the corresponding reference:

- **All human shots** → `references/photorealism-layer.md` (skin, eyes, tears, DOF, texture)
- **Lighting descriptions** → `references/cinematic-lighting.md` (8 professional light positions + film references)
- **Fight/action scenes** → `references/fight-scenes.md` (Universal Pattern, 9-shot template, handheld, action aesthetics)
- **Dialogue/emotional scenes** → `references/dialogue-emotion.md` (sightlines, pauses, power shifts, breathing lens, focal length psychology)
- **Romance/intimacy scenes** → `references/romance-intimacy.md` (spatial distance, body language leaks, Wong Kar-wai style, intimacy design)
- **Multi-character scenes** → `references/multi-character.md` (screen position system, camera lock, 180° rule, hierarchy, negative space)
- **Character/scene bibles** → `references/character-scene-bible.md` (consistency templates, 16-grid reference, prop design)
- **AIGC structured prompts** → `references/aigc-structured-prompt.md` (9-component template, 4-element framework, few-shot anchoring, prompt generator pattern, version management)
- **Visual consistency @reference** → `references/visual-consistency-reference.md` (@标注语法, 三类参考图体系, 一致性校验清单, 状态追踪表)
- **Visual design master** → `references/visual-design-master.md` (7-role identity, 7-asset pack per scene: scene info card + emotional arc + color script + storyboard + 360° holographic + 16-grid + contact sheet, PBR mandatory rules, model-specific parameters MJ/Flux/Kling, negative prompt)
- **Costume & character art** → `references/costume-character-bible.md` (电影服化道总监3步工作流: Step1材质拆解表 + Step2 Detail Sheet提示词多角度面部/微距/配饰 + Step3 Turnaround View提示词三视图/重力打样 + 面料物理控制词速查表 + SSS/anisotropic铁律 + 重力drape铁律 + @一致性锁定集成)
- **Prop design & concept art** → `references/prop-design-master.md` (电影道具美术总监3步工作流: Step1材质介质拆解表 + Step2 Split View道具设计图提示词组装全景/结构拆解/5色色卡 + 材质物理控制词速查表 + 去塑料感/微痕具象/重力接地铁律 + @一致性锁定集成)
- **Quality check** → `references/self-inspection.md` (post-generation checklist + upgrade rules)

## Phase 4: Delivery, Validation & Extras

### Final Output Structure (always this order):
1. **Title & Logline** + overall runtime estimate
2. **Script Health Report** (from Phase 2, concise)
3. **Visual Style Bible** (1 paragraph + bullet motifs + reference films)
4. **Full Storyboard** (scene-grouped, SHOT templates)
5. **Shot Count Summary** by scene + pacing notes
6. **Self-Validation Results**: "All script beats covered. Professional coverage achieved. Full Fidelity Self-Check: 100% of original dialogue lines and scene segments preserved — no omissions."

### Validation Self-Check (run before output — MANDATORY):
- [ ] Full Script Coverage: Line-by-line and scene-by-scene cross-check against ORIGINAL script. Every dialogue, action, scene segment accounted for.
- [ ] Fight/Action Check: Broken into detailed multi-shot sequences following Universal Fighting Pattern. No summarization.
- [ ] Every major story beat has dedicated visual moment(s)?
- [ ] Camera directions specific, practical, cinematic?
- [ ] Image prompts detailed enough for professional image generation?
- [ ] Total feels like a real director's shot list?

### User Options (offer at end):
- "Generate key hero shot images?"
- "Export full storyboard as PDF?"
- "Create Excel shot timing sheet?"
- "Iterate: make more [dynamic / horror / minimalist]?"

## Phase 5: Iteration Protocol

On feedback ("too slow", "add more close-ups", "change ending tone"):
- Return to Phase 2 with new directives
- Re-optimize affected sections only
- Update affected shots + re-validate

## Key Film Terminology Reference

**Shots**: ECU, CU, MCU, MS, WS, LS, ELS, OTS, POV, Insert, Cutaway, Montage, Sequence shot
**Moves**: Static, Pan, Tilt, Dolly (in/out), Truck (left/right), Pedestal, Crane, Handheld, Steadicam, Gimbal, Zoom (slow/crash), Rack focus, Whip pan, Dutch tilt
**Lighting**: High-key, Low-key, Practical, Motivated, Volumetric, Chiaroscuro, Neon noir, Golden hour, Blue hour
**Always specify**: lens (35mm, 50mm, 85mm, anamorphic), aspect ratio, film stock emulation if relevant
