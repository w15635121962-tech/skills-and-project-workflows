---
name: storyboard
version: 2.0.0
description: |
  Professional storyboard system for English short drama in 9:16 vertical format.
  Converts screenplay into numbered storyboard panels with full technical specification.
  No AI prompts — pure storyboard craft.

  TRIGGER for: "storyboard this" · "shot breakdown" · "shot list" · "coverage plan" ·
  "how should I shoot this" · any screenplay pasted/uploaded for visual planning ·
  fight / action / romance / suspense scene breakdown

  DO NOT TRIGGER for: AI prompt generation · script writing · script diagnosis
---

# Professional Storyboard System · 9:16 Vertical

> **Version 2.0.0** · Last updated: 2025-06
> Worked example → `references/worked-example.md`

---

## POSITIONING — When to Use This Skill

| Skill | Scope | Aspect Ratio | Language | Depth |
|-------|-------|-------------|----------|-------|
| `movie-story` | Full pipeline (script → storyboard → AI prompts) | Landscape (default) | CN | Deepest (12-col table + spatial coordinates + 6-dim character precision) |
| `9-16-movie-story` | Full pipeline, rebuilt for vertical | 9:16 | CN | Deep (inherits movie-story, vertical重构) |
| **`storyboard`** | **Storyboard only** (script → panels, no prompts) | **9:16** | **EN** | **Mid** (7-col table + 8 directorial laws) |

**Use `storyboard` when:** English-language script → pure storyboard output needed, fast and focused.
**Use `9-16-movie-story` when:** Chinese-language vertical short drama → full pipeline including AI prompt engineering.
**Use `movie-story` when:** Horizontal format or the most comprehensive pipeline is required.

---

## INTEGRATION — Upstream / Downstream

- **Upstream from `focal-grid`:** If a focal grid (3×3 shot progression) exists for a standoff scene, use it as the camera arc input for Step 3 — the storyboard picks up where the grid leaves off.
- **Downstream to `movie-story` / `9-16-movie-story`:** A storyboard produced here can serve as the visual plan input for a full pipeline run, which then adds visual anchors, AI prompts, and spatial coordinate locking.
- **Cross-reference with `costume-accessories-extractor` / `makeup-hair-extractor`:** Character anchors in Step 2 should align with costume/hair reference sheets if those skills have been run on the same project.

---

## WORKFLOW

Execute five steps in order. Output each step before proceeding.

```
STEP 1 → PARSE      Map the script. Count every element. Completeness contract.
STEP 2 → ANCHOR     Lock character + location + axis visuals. Immutable.
STEP 3 → ANALYSE    Per-scene: subtext, power, camera arc, type-specific block.
STEP 4 → BOARD      Output storyboard tables. Every cell filled.
STEP 5 → CHECK      Self-inspect. Fix failures. Declare pass.
```

**Hard rules:**
- Never skip, summarise, or merge script content.
- Never write a shot without a quoted script basis.
- Never output before Step 5 passes.
- Every shot answers: *"What does this shot add that no other provides?"*

---

## THE EIGHT LAWS

| # | Law | One-Line Rule | Applies |
|---|-----|--------------|---------|
| 1 | **HITCHCOCK** | At the peak: show one fragment, not the whole. The incomplete image is more powerful. | All |
| 2 | **SCOTT** | Specific enough that actor, DP, and effects each extract requirements without asking. | All |
| 3 | **MILLER** | State every spatial position. Centre-frame. Must work without subtitles. | All |
| 4 | **SPIELBERG** | State what each shot hides and why hiding serves the story. Constraints → assets. | All |
| 5 | **SCIAMMA** | Who watches whom IS the plot. Watcher shielded; watched exposed and lit. | Romance |
| 6 | **WRIGHT** | The body confesses what the face controls. Design an INSERT for the involuntary. | Romance |
| 7 | **GUADAGNINO** | Space between them IS desire. Track distance. Amplify one sensory sound. | Romance |
| 8 | **LINKLATER** | Long witness takes. Negative space contracts toward peak. Plan the empty frame. | Romance |

Fight/shock → HITCHCOCK primary · Romance → Laws 5–8 primary · All scenes → Laws 1–4 always

---

## STEP 1 — PARSE

```
SCRIPT INVENTORY
Title: ___  |  Genre: ___  |  Scenes: ___

 #  | Slugline                  | I/E | Time  | Characters       | Type
----|---------------------------|-----|-------|------------------|----------
 1  | INT. COFFEE SHOP — NIGHT  | INT | NIGHT | MAYA, JAKE       | DIALOGUE
 2  | ...                       |     |       |                  |

COMPLETENESS CONTRACT:
  Dialogue: ___  |  Action beats: ___  |  Parentheticals: ___  |  Props: ___  |  Transitions: ___
```

---

## STEP 2 — ANCHORS

### Character Anchor (one per character)
```
CHARACTER: [NAME] — [role]
  Age/build: ___
  Face: eyes=___ · jaw=___ · skin=___ · rest expression=___
  Hair: ___ · condition: ___
  Costume (LOCKED): ___
  Posture: ___ · Stress tell (WRIGHT): ___ · Breath: ___
  Screen default: [L/C/R], [upper/mid/lower 1/3]
  NEVER CONTRADICT: 1.___ 2.___
```

### Location Anchor (one per unique location)
```
LOCATION: [SLUGLINE]
  Type: INT/EXT · Time: ___ · Scale: intimate/mid/large/vast
  Atmosphere: ___
  HIDES (SPIELBERG): ___
  Architecture: → ___ (position) · → ___ (position)
  Spatial map: 12=___ · 3=___ · 6=___ · 9=___
  Light: source=___ · dir=___ · quality=hard/soft · temp=___K · hides=___
  Palette: dominant ___ | secondary ___ | accent ___
```

### 180° Axis (multi-character scenes)
```
AXIS: [Slugline]
  [A]=LEFT/RIGHT · [B]=LEFT/RIGHT · Camera zone: ___
  OTS A→B looks: ___ · OTS B→A looks: ___
  Axis cross: PLANNED Shot ### / NOT PLANNED
```

---

## STEP 3 — SCENE ANALYSIS

### All scene types:
```
SCENE ANALYSIS: [SLUGLINE]
  Type: DIALOGUE / FIGHT / ROMANCE / SUSPENSE / ACTION
  Primary law: ___ · Why: ___
  Surface: ___ · Subtext: ___ · Position: SETUP/COMPLICATION/TURNING/CLIMAX/RESOLUTION
  [A] WANTS ___ / NEEDS ___ · [B] WANTS ___ / NEEDS ___
  Power: opens=___ → shifts at [___] → closes=___
  Arc: open=___ → pivot=[___] → close=___
  Subtext visible through: ___ (NOT dialogue)
  Camera: open=___ → escalation=___ → peak=___ → close=___
  Contract: ___ dial / ___ beats / ___ paren / ___ props · Shots: ___ · ≥65% react = ___
```

### Romance scenes — add:
```
ROMANCE: [SLUGLINE]
  Gaze (SCIAMMA): watcher open=___ | reversal at=[___] | close=___
  Distance (GUADAGNINO): open=___ | peak=___ | close=___ | between them: ___
  Involuntary (WRIGHT): [A] body=___ | [B] body=___
  Sound (SCIAMMA+GUADAGNINO): score=YES/NO | diegetic=___ | amplified moment=___
  Long take (LINKLATER): YES ___s / NO · Empty frame: YES Shot ### / NO
```

### Fight scenes — add:
```
FIGHT: [SLUGLINE]
  Physical stakes: ___ | Emotional stakes: ___
  Pre-impact: static/slow push (NEVER handheld)
  Impact move: crash zoom / jump cut / whip pan (ONE per impact)
  Post-impact: ECU static ≥1.5s
  Fragments (HITCHCOCK): NOT shown whole=___ | Frag 1=___ | Frag 2=___ | Frag 3=___
```

---

## STEP 4 — STORYBOARD TABLES

This is the primary output. Output storyboards as professional tables.

### Scene Header (before each scene's table)

```
═══════════════════════════════════════════════
SCENE [N] — [SLUGLINE]
═══════════════════════════════════════════════
Function: ___ · Subtext: ___ · Law: ___
Power: ___→___→___ · Camera: ___→___→___
Axis: ___ · Shots: ___ · ≥65% react = ___
Contract: ___ dial / ___ beats / ___ paren / ___ props
═══════════════════════════════════════════════
```

### TABLE 1 — Full Professional Storyboard

This is the primary deliverable. Every cell must be filled. No cell may be left vague.

| Shot No. | Shot Type | Camera Movement | Visual Description | Performance / Action | Dialogue / SFX | Duration (s) | Notes / Lighting / Continuity |
|----------|-----------|----------------|--------------------|---------------------|---------------|-------------|-------------------------------|
| ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ |

**Column guide — what goes in each cell:**

**Shot No.**: Sequential number. Use sub-shots (03A, 03B) for fragment sequences sharing a dramatic beat. Sub-shots = HITCHCOCK fragmentation in the same emotional unit (e.g. 03A=WS context, 03B=ECU fragment detail of the same moment).

**Shot Type**: ECU / CU / MCU / MS / WS / ELS / INSERT / FRAGMENT / LINGER / INVOLUNTARY / EMPTY FRAME / TWO-SHOT WIDE

**Shot Type disambiguation rules:**
- **FRAGMENT vs INSERT:** FRAGMENT = a piece of a whole that the audience must mentally assemble (Hitchcock: the peak is incomplete). INSERT = functional information the audience needs to read (a letter, a clock, a phone screen). When both apply, ask: "Is the audience reading information or assembling an image?" Reading → INSERT. Assembling → FRAGMENT.
- **LINGER vs INVOLUNTARY:** LINGER = extended gaze, the camera dwells on a face/space because desire or study demands it. INVOLUNTARY = the body betrays what the face controls (a twitch, a jaw release, fingers pressing flat). When both apply, use INVOLUNTARY as Shot Type and note LINGER in Duration (≥4.0s).

**Camera Movement**: Static / Slow Push-in / Pull Back / Tilt Up / Tilt Down / Crane Up / Crane Down / Handheld / Crash Zoom / Rack Focus / Micro-drift / Whip Pan / Walk-and-Talk Steadicam / Linger Hold / Empty Frame Hold. Always add speed qualifier if not static (slow / subtle / imperceptible / fast / sudden).

**Visual Description** (what you would draw — SCOTT LAW): Describe the frame as if sketching it for a storyboard artist. Name the subject position in frame (upper/mid/lower 1/3), what fills the background, any foreground elements, the overall composition. This is the "thumbnail" — the image itself. Be concrete: "Character sitting at desk, rain on window behind, qipao fabric texture visible" — never abstract.

**Performance / Action** (physical specifics — SCOTT LAW): Describe what the character's body does — jaw, eyes, brow, lips, breath, posture, gesture. Never use vague emotion words ("sad", "angry", "nervous"). Always physical: "Micro eye movement, slow blink, jaw tension, fingers press flat." This is the cell the actor reads. Fuse character movement and camera movement: "Slight forward lean as camera pushes in, hand gripping edge of table."

**Dialogue / SFX**: Exact dialogue in quotes. SFX described specifically (not "ambient" — name the sound: "rain on glass + distant traffic"). If no dialogue: "No dialogue" + describe the diegetic sound. Music direction if relevant: "Score: tense strings fade in" or "No score (SCIAMMA: diegetic only)."

**Duration (s)**: Calculated number. Show the calculation in Notes if complex. Minimum floors: ECU≥1.0 · CU≥2.0 · MCU≥3.0 · MS≥3.5 · WS≥2.0 · INSERT≥1.5 · LINGER≥4.0 · FRAGMENT≥0.5.

**Dialogue timing by language:**
- **English:** words ÷ 2.2 wps + pause (0.8–2.0s) + action (0.5–1.5s) + hold (0.8–1.8s) × 1.12 buffer
- **Chinese:** characters ÷ 3.5 cps (conversation) or ÷ 2.8 cps (dramatic/contemplative) + pause + action + hold × 1.12 buffer
- **Mixed EN/CN:** apply per-line based on the language of that specific dialogue line

**Notes / Lighting / Continuity:** This cell carries three structured sub-sections:
1. **[LIGHTING]** key source + direction + temp + quality + ratio + specific detail (e.g. "Subsurface scattering, catchlight 11 o'clock, warm shadow"). Name what lighting HIDES (SPIELBERG).
2. **[FUNCTION]** What this shot adds that no other provides. The Law applied.
3. **[CONTINUITY]** Character position at cut, eye direction, prop state, camera exit state for next shot. What remains hidden.

Format: `[LIGHTING] ___ [FUNCTION] ___ [CONTINUITY] ___`

### TABLE 2 — Compact Quick-Reference

Output after Table 1 as a quick-scan summary:

| Shot | Framing | Cam Move | Screen Content & Action | Dial / SFX | Dur | Notes |
|------|---------|----------|------------------------|-----------|-----|-------|
| ___ | ___ | ___ | ___ | ___ | ___ | ___ |

This table is a compressed version for fast iteration. Each cell = the essence of Table 1's corresponding cell in fewer words. Output both tables for every scene.

### Sub-Shot Convention (Fragment Sequences)

When a dramatic beat requires multiple rapid shots (HITCHCOCK fragmentation), number them as sub-shots:

| Shot No. | Shot Type | Camera Movement | Visual Description | Performance / Action | Dialogue / SFX | Duration (s) | Notes |
|----------|-----------|----------------|--------------------|---------------------|---------------|-------------|-------|
| 03A | Wide Shot | Subtle Handheld | Establishing room, character small in frame, night city outside | Lonely posture, slow head turn | Distant rain + room tone | 3.5 | Volumetric light, realistic environment scale |
| 03B | ECU | Crash Zoom | Extreme detail on single tear rolling down cheek, skin pores, fabric edge | Intense micro-performance, eye dart | Sharp inhale + tear drop sound | 1.8 | High contrast, emotional peak, realistic skin detail. HITCHCOCK: fragment of 03A's wider moment |

Sub-shots share a dramatic beat but use different scales — the wide context (A) and the fragment detail (B/C). This is the Hitchcock principle made structural: the audience assembles the whole from the fragments.

### Scene Close

```
── SCENE [N] CLOSE ──────────────────────────────
Panels: ___ · Reaction: ___ (___% ≥65%)
Runtime: ___s
Contract: dial [N/N]✓ · beats [N/N]✓ · paren [N/N]✓ · props [N/N]✓
Exit state: ___ · Hidden carries: ___
──────────────────────────────────────────────────
```

---

## REFERENCE TABLES

### Shot Sizes

| Code | Content | Ratio | Floor | Law | Disambiguation |
|------|---------|-------|-------|-----|----------------|
| ELS | Subject tiny | <15% | 2.5s | Miller | Establishing only |
| WS | Full body | 15–30% | 2.0s | Miller | Spatial lock |
| MS | Waist up | 30–50% | 3.5s | Scott | Dialogue default |
| MCU | Chest up | 40–60% | 3.0s | Scott | Intimacy threshold |
| CU | Full face | 50–70% | 2.0s | Spielberg | Emphasis / HIDE |
| ECU | Eyes/mouth/detail | 70–100% | 1.0s | Hitchcock | Fragment candidate |
| INSERT | Object/body part | varies | 1.5s | Hitchcock | Audience READS info |
| FRAGMENT | One sensation | varies | 0.5s | Hitchcock | Audience ASSEMBLES image |
| LINGER | Extended hold | varies | 4.0s | Sciamma | Camera dwells (desire/study) |
| INVOLUNTARY | Body betrays | varies | 2.0s | Wright | Body confesses (jaw/hand/breath) |
| EMPTY FRAME | Absence | varies | 2.5s | Linklater | Negative space speaks |

### Camera Movements

| Move | Meaning | Forbidden Next | Preferred Follow |
|------|---------|---------------|-----------------|
| Push In | Pressure | Immediate pull | Hold static · Linger |
| Pull Back | Isolation | Immediate push | Static settle · Empty frame |
| Tilt Up | Power | Immediate tilt down | Hold high angle · Crane up |
| Tilt Down | Shame | Immediate tilt up | Hold low angle · Settle to subject |
| Static | Weight | Unmotivated fast move | Another static · Slow push |
| Handheld | Urgency | Locked static immediately | Another handheld · Settle to slow drift |
| Crash Zoom | Shock | Any move without ≥0.5s recovery | Static hold ≥1.5s · ECU freeze |
| Micro-drift | Dread/intimacy | Acceleration | Decelerate to static · Linger |
| Linger | Desire/study | Fast cut | Static hold · Slow pull |
| Walk-and-Talk | Witness | Hard cut mid-sentence | Natural pause cut · Settle to static |

### Parenthetical Reference

| Parenthetical | Shot Implication | Example |
|---------------|-----------------|---------|
| `(beat)` | Hold ≥1.0s before next line | CU hold → MCU reaction |
| `(quietly)` | CU or closer · lower audio energy | CU static, whisper-level |
| `(to herself)` | Single shot, no OTS · isolated | CU/MCU single, no listener |
| `(off)` | Show the listener, not the speaker | Reaction CU of listener |
| `(V.O.)` | Show environment or listener face | WS/MCU of space or listener |
| `(crying)` | ECU static ≥3.0s · no handheld | ECU tear, skin detail |
| `(pause)` | Static hold weighted · no cut | Same framing, hold 1.5–3.0s |
| `(re:[prop])` | INSERT of prop + reaction row | INSERT prop → CU reaction |

### Timing

**English dialogue:**
Words ÷ 2.2 wps + pause (0.8–2.0s) + action (0.5–1.5s) + move + hold (0.8–1.8s) × 1.12

**Chinese dialogue:**
Characters ÷ 3.5 cps (conversation pace) or ÷ 2.8 cps (dramatic/contemplative) + pause + action + hold × 1.12

**Mixed EN/CN:** Apply per-line based on the language of each specific dialogue line.

**Subtitle timing:** ≤8 words/card (EN) / ≤12 characters/card (CN) · +0.3s/card

---

## STEP 5 — SELF-CHECK

Run after all tables complete. Fix every failure before pass declaration.

**A · COMPLETENESS** — cross-ref Step 1 contract vs each row's content:
- [ ] Every scene has a table · no scenes merged/skipped · order matches script
- [ ] Every dialogue line quoted in at least one row
- [ ] Every action beat has a corresponding row
- [ ] Parentheticals reflected: (beat)→hold ≥1.0s · (quietly)→CU+ · (to herself)→single · (off)→listener · (crying)→ECU ≥3.0s
- [ ] Every named prop appears · significant props have INSERT row
- [ ] All transitions noted
→ **Fail fix:** Missing row → add it with explicit script reference. Missing prop → add INSERT row. Missing parenthetical → adjust shot type/duration. Re-count contract, re-run A.

**B · NARRATIVE** — every row earns its place:
- [ ] Every row has a specific function in Notes (not "mood" or "looks good")
- [ ] No two rows do identical work
- [ ] Reaction rows ≥65% per dialogue scene: ___/___=___% [PASS/FAIL]
- [ ] Subtext visible through shot choices, not just dialogue
- [ ] Short answers ("Fine." "Sure.") have reaction rows
- [ ] Silence held in duration — not cut
- [ ] Power shift → framing change · dominant=upper 1/3
- [ ] Scale tracks arc: wider setup → tighter climax
→ **Fail fix:** Duplicate rows → merge or reassign function. Low reaction % → add reaction rows for each dialogue line. Missing power shift → adjust framing at shift point. Re-run B.

**C · CAMERA CONTINUITY**:
- [ ] Each row's camera exit flows into next row's camera entry (stated in Notes)
- [ ] 180° axis respected · no cross without neutral bridge
- [ ] Forbidden: no push→pull · no tilt up→down · no crash→crash · no handheld→locked static
- [ ] Every move has narrative motivation
- [ ] Fight: pre-impact static · one move per impact · post-impact ECU static ≥1.5s
- [ ] Romance: decelerate · peak=static · pull=character-motivated · linger=static · empty=static
→ **Fail fix:** Forbidden pair → insert neutral bridge shot (static WS or insert). Axis cross → add OTS neutral. Missing exit/entry → add to Notes continuity. Re-run C.

**D · EXPLICITIZATION** — no vague language in any cell:
- [ ] BANNED without physical spec: "sad" "angry" "scared" "happy" "nervous" → must state jaw/eyes/brow/lips/breath
- [ ] Eye gaze + breathing in every CU/ECU Performance cell
- [ ] Catchlight + shadow colour in every CU/ECU Notes cell
- [ ] Every light motivated by named practical · HIDES stated
- [ ] Romance: distance in spatial terms · involuntary=body part+movement+duration · linger=micro-by-micro ≥4s
- [ ] Fight: impact=force+reaction+delay · consequence=individual muscle/breath/pupil
→ **Fail fix:** Vague emotion → replace with physical spec (jaw tension, breath pattern, eye movement). Missing catchlight → add direction + source. Missing HIDES → state what darkness conceals and why. Re-run D.

**E · TIMING**:
- [ ] Every Duration cell has calculated number
- [ ] No row below floor: ECU≥1.0 · CU≥2.0 · MCU≥3.0 · MS≥3.5 · WS≥2.0 · INSERT≥1.5 · LINGER≥4.0
- [ ] Fight consequence ≥1.5s · Romance peak ≥2.5s · Subtitle ≤8 words/card (EN) / ≤12 chars/card (CN)
→ **Fail fix:** Under-floor → raise to floor minimum and add hold. Missing calc → apply formula from Timing section. Subtitle overflow → split into multiple cards with +0.3s each. Re-run E.

**PASS:**
```
═══════════════════════════════════════════
STORYBOARD: PASSED
═══════════════════════════════════════════
Laws: ___
Script: scenes [N/N]✓ dial [N/N]✓ beats [N/N]✓
        paren [N/N]✓ props [N/N]✓ trans [N/N]✓
Reaction: Sc1=___% · Sc2=___% (all ≥65%✓)
Continuity: PASS · Axis:0 · Forbidden:0
Explicit: PASS · Vague:0
Timing: PASS · Under-floor:0
Shots: ___ · Runtime: ___
READY FOR PRODUCTION.
═══════════════════════════════════════════
```

---

## CHANGELOG

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2025-06 | Full optimization: removed Claude hardcode, fixed PILLAR 2 orphan, added CN timing, added POSITIONING + INTEGRATION blocks, moved worked example to references/, added Shot Type disambiguation, expanded Parenthetical ref, added Preferred Follow column, added Step 5 failure fix guides, structured Notes cell format, added version + changelog |
| 1.0.0 | — | Initial release |
