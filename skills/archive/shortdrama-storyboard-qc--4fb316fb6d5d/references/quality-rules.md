# Storyboard Quality and Auto-Repair Rules

## Contents

1. Functional shot floor
2. Automatic shot insertion and splitting
3. Visual-language audit
4. Sound-language audit
5. Emotion audit
6. Continuity and generation hard gates
7. Scoring and defect codes

## 1. Functional shot floor

Count coverage units by scene. A shot may satisfy only one primary function when combining functions would create multiple subjects, actions, or focal targets.

| Coverage unit | Minimum | Add a shot when |
|---|---:|---|
| Scene establishment | 1 | New location/time/blocking cannot inherit from the previous scene |
| Entrance or reveal | 2 | The entrance lacks spatial establishment or a reveal reaction |
| Ordinary dramatic beat | 1 per beat | Cause, action, or result is absent |
| Dialogue turn | 2 | Only the speaker is shown; the struck listener has no reaction |
| Major line landing | 3 | Speaker, listener reaction, or resulting choice is missing |
| Action or magic | 3 | Establish geometry, impact, or aftermath is missing |
| Transformation/process effect | 3 | Build, change, or settle is missing |
| Emotional peak | 2–3 | It contains only dialogue or a facial expression, without carrier and choice |
| Story-driving prop/sigil | 1 | The object changes the plot but is not visually legible |
| Scene exit/transition | 1 | Time/space changes abruptly without visual or audio continuity |
| Cliffhanger | 1 | A suspense scene lacks a final hook image |

Target average shot lengths:

- reversal, humiliation, payoff: 1.5–3s;
- action: 1–3s;
- suspense or pressure: 3–6s;
- emotion: 4–8s;
- beauty or seduction: 4–8s.

An effective shot must have a clear subject, one main action, narrative/emotional value, and independent generatability.

## 2. Automatic shot insertion and splitting

When quantity or coverage is short, add in this priority:

1. **Cause shot**: motivation, key prop, spell build, or missing consequence.
2. **Reaction shot**: the person actually struck by a line/event.
3. **Relationship shot**: blocking, power relation, eyeline, or 180-degree axis.
4. **Choice shot**: the decisive action after emotion is suppressed.
5. **Aftermath shot**: physical result, environment response, silence, or sound vacuum.
6. **Transition/cliffhanger shot**: time-space bridge or episode hook.
7. **Atmosphere shot**: only after all functional needs are covered.

Split into 2–3 shots when one shot contains:

- two or more independent actions such as rising, walking, casting, turning, crying, and delivering a key line;
- multi-person spatial exposition plus a precision emotional close-up;
- build, burst, and settle of one effect;
- simultaneous complex performance by multiple characters;
- complex touch plus large camera movement plus tail/wing motion.

Default split: `establish/build → impact/line landing → reaction/result`.

## 3. Visual-language audit

| Dimension | Pass line | Repair |
|---|---|---|
| Shot sizes | A scene with 6+ shots uses at least 3 sizes | Convert repetitions into relation MS/LS or contextual INS |
| Repetition | Same size + angle + move no more than twice consecutively | Use reverse, over-shoulder, low angle, static hold, or relation coverage |
| Space | Every new scene has an establishment/relation shot | Add 35mm MS/LS with foreground/background, sides, entry, and focal position |
| Dialogue | Establishment + speaker + listener reaction | Add the missing unit while preserving the 180-degree axis |
| Emotional progression | Framing contracts or releases with the emotion | Rise: MS→MCU→CU; release: CU→MS/LS |
| Focal target | One primary visual focus per shot | Delete parallel tasks or split subject/result |
| Vertical 9:16 | Key element in central vertical safe zone | Use depth stacking rather than side-by-side lineup |
| Movement rhythm | Not all slow push-ins or all handheld | Add motivated static hold, track, pull-back, or one dynamic move |
| Insert | Advances plot or physicalizes emotion | Use only meaningful props, sigils, hands, tails, blood, or evidence |

Minimum patterns:

- Dialogue: relation → speaker → listener reaction → reverse/choice → result.
- Humiliation/payoff: group relation → aggressor → restrained target → reversal → opponent/crowd reaction → hook.
- Emotion: atmosphere → approach/test → restraint → physical leak → choice → afterglow.
- Action/magic: geometry → build → release/impact → hit reaction → consequence.
- Judgment/power: spatial order → low-angle authority → judged reaction → verdict → silent aftermath.

Variety is not a quota. Every camera change must have narrative motivation.

## 4. Sound-language audit

Use diegetic sound by default. Select only relevant layers:

1. environment bed;
2. action/contact sound;
3. physiological sound;
4. dialogue with voice, intensity, distance, and reverb;
5. directional spatial/off-screen sound;
6. silence or deliberate noise reduction.

Pass rules:

- Every scene has a stable environment bed plus at least one changing sound layer.
- Every major turn changes sound intensity, distance, direction, reverb, or presence.
- Do not repeat identical sound text for three consecutive shots.
- Crowd scenes may use medium/high ambience; secret/intimate scenes use low ambience; key lines may drop ambience to very low.
- A reaction may carry off-screen dialogue as a J-cut/L-cut; state that the voice is off-screen so the listener does not move their mouth.
- With no dialogue, write exactly: `无对白，不生成说话口型，禁止字幕，禁止旁白，禁止背景音乐。`

Repair sound in this order: contact/action → physiological/voice change → directional space → silence/noise drop. Never use background music as a substitute for emotional design unless explicitly requested.

## 5. Emotion audit

Every major emotional turn must complete:

```text
Trigger → restraint/instinct → leak → choice/action → aftermath
```

Ordinary turns need at least four stages; peaks need all five. If the storyboard has only dialogue plus a facial adjective, it fails.

Label each key character per shot:

| Level | State | Performance scale |
|---:|---|---|
| 0 | neutral/observing | stable posture and breath |
| 1 | slight disturbance | gaze pause, fingertip or tail-tip change |
| 2 | visible restraint | shallow breath, rigid shoulder/neck, hesitation |
| 3 | emotional leak | voice/rhythm change, retreat/approach, prop pressure |
| 4 | decisive release | refusal, protection, attack, cast, or counteraction |
| 5 | peak/collapse | major consequence followed by an aftermath shot |

Repair rules:

- Three unchanged levels without narrative reason: create an internal change.
- Jump from 1 to 5 without a sudden event: insert restraint/leak transition.
- Peak followed by immediate scene cut: add reaction or aftermath.
- Major line without the struck listener: add the listener reaction.
- Repeated crying, glaring, or facial close-ups: convert to breath, body, hands, steps, costume pressure, non-human traits, props, or distance.
- Characterization mismatch: rewrite the physical action from the asset bible/character arc; do not preserve the wrong expression.

## 6. Continuity and generation hard gates

Fail delivery if any remains:

- identity tokens, wardrobe, props, injuries, wetness, magic state, or time of day drift;
- missing left/right, foreground/background, entry, or eyeline anchors in a new scene;
- reverse coverage crosses the 180-degree axis;
- multi-action shot, simultaneous complex multi-character acting, or complex contact plus complex camera movement;
- contact lacks ownership, direction, contact point, occlusion, compression, natural finger bend, or contact shadow;
- crowds lack distinct faces, hair, wardrobe, positions, and anti-swap negatives;
- contradictory lighting such as no source plus a brightly keyed face;
- self-lit eyes or glowing/glass-bead tears and sweat;
- dense readable UI or generated small text;
- transformation exposes an unstable half-formed topology;
- tails/wings perform uncontrolled simultaneous large movement.

Use image-to-video for identity-critical character shots, emotional hero shots, and transformations. Use text-to-video for environment, atmosphere, crowds, and free camera. Keep one subject, one main action, one core effect; keep text-to-video parallel elements at three or fewer.

## 7. Scoring and defect codes

| Module | Points |
|---|---:|
| Narrative and cause/effect coverage | 25 |
| Effective shot count | 20 |
| Visual language | 15 |
| Sound language | 10 |
| Emotion and character arc | 20 |
| Continuity and generatability | 10 |

Pass at 85/100 with every hard gate passed.

- `NAR`: missing narrative cause, beat, or consequence.
- `QTY`: effective shot quantity below floor.
- `VIS`: weak shot-size, angle, movement, or composition variety.
- `AUD`: weak sound layers or sound changes.
- `EMO`: incomplete emotion loop, flat curve, or wrong characterization.
- `CONT`: spatial, identity, wardrobe, prop, light, or axis discontinuity.
- `GEN`: overloaded action, contact, crowd, appendage, transformation, or other generation risk.

Repair priority: `NAR/EMO → CONT/GEN → QTY → VIS/AUD`.
