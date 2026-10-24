# Production Rules

Use this reference before writing full Format C groups, auditing prompts, or fixing generation failures.

## Deliverable Decision

- Full prompt group: produce the requested number of groups or shots, normally five shots per group, with group numbering reset to `shot 1`.
- Single shot revision: keep the user's surrounding template and revise only the requested shot unless continuity requires a small note.
- Storyboard analysis: plan coverage first, then identify missing emotional beats, eyeline problems, axis breaks, lighting breaks, and generation risks.
- Prompt audit: lead with actionable risks and fixes; do not rewrite everything unless asked.
- Failure fix: identify the visual symptom, likely prompt cause, and a minimal wording repair.

When the request is for the user's established workflow or 九尾狐 project, apply this file together with [user-standards.md](user-standards.md). The user-standards reference overrides generic defaults for fixed quality wording, strict `@` scope, dialogue reaction logic, no physiological audio, magic particle control, character-specific behavior, and learned failure checks.

## Immutable Facts Checklist

Extract these before writing:

- On-screen characters and whether they are foreground, background, seated, standing, entering, or leaving.
- Costume anchors, hair anchors, makeup anchors, visible props, and scene references.
- Time of day, source direction, color temperature, and whether adjacent shots must match.
- Dialogue, silence, reaction beats, and who hears whom.
- Physical contact ownership: whose hand, entry side, contact point, finger bend, compression, occlusion, contact shadow.
- Reference images. Add `@` before visible referenced people, props, and scenes.
- Safety and age context. Keep romance age-appropriate and non-explicit, especially in school or uniform contexts.

## Format C Checklist

Begin each group with:

- Fixed quality language and model-safe photographic baseline.
- Opening-state lock: exact character positions, props, body orientation, facial state, and what has already happened.
- Environment: weather, surface, depth layers, practical light sources, material condition, and spatial anchors.
- Lighting baseline: source direction, color relationship, shadow depth, exposure strategy, and continuity rule.
- Audio rule: diegetic sound only, low environment sound by default, no background music, no subtitles, no voice-over unless requested.
- Group-level negatives: identity drift, face merging, outfit swapping, subtitles, UI text, text gibberish, bad hands, plastic skin, over-sharpening.

For each shot, write:

```text
【shot n | 景别 | 视角 | 运镜 | 焦段 | duration: x.xs】
镜头：
画面：
微表演：
对白反应：
人物背景融合：
光影：
音频：
运动强度：
负面提示词：
```

Avoid isolated eye, lip, hand, or body-part close-ups. Use contextual close shots that retain performance and spatial context.

## Continuity And Coverage

- Give each shot an unambiguous spatial relation: left/right, foreground/background, seat count, Z-axis movement, stable object anchor, or doorway relation.
- Keep reverse shots on the same 180-degree axis. For over-shoulder framing, name the foreground shoulder and focal subject.
- Use voyeur framing only when essential. Do not make subjects in a voyeur shot perform directly to the hidden viewer.
- Repeat decisive continuity information inside every independently generatable shot.
- In dialogue scenes, cover the speaker, listener reaction, reverse angle, shared two-shot, and emotional punctuation when shot count allows.
- Translate weak facial-only beats into body grammar: breath, shoulder drop, neck tension, hand pause, step rhythm, fabric compression, moving hair, dust, or contact with a prop.

### Over-Shoulder Lock

- For an over-shoulder shot, state foreground shoulder ownership and side, its frame position/coverage, the focal character, camera direction, both actors' facing, and the established 180-degree axis. A shoulder-less frame is not an over-shoulder shot.
- Preserve screen left/right and the shared floor/seat/bed plane through reverse coverage. Focus pulls may change sharpness only, never standing positions, actor scale, or shoulder side.
- Use negatives when relevant: `站位漂移，左右互换，越肩主体错误，前景肩膀消失，错误过肩，轴线跳变，人物朝向混乱，视线方向冲突，不同地面平面，距离关系错误`.

### Transformation Endpoint Lock

- State the start form and final form independently. For a pure human endpoint, state that the animal body is completely gone and only one human body remains on the same physical support surface.
- Separate `pure human form` from `human form retaining tails`: in the latter, tails attach to one human lower back and no fox head, torso, paws, ears, or duplicate silhouette remains.
- Use an occluding transition rather than displaying both forms: anchored energy gathers, a curtain/veil/mist/tails briefly hides topology change, then the final body settles with stable contact shadow. Add negatives for residual animal body, duplicate bodies, animal-human overlay, and malformed transformation.

### Cross-Form Scale Lock

- When animal and human forms share a shot, anchor the animal's scale against a visible human hand, forearm, knee, lap, pillow, floor joint, or doorway; declare the shared physical support plane and localized weight/compression.
- Hide an animal-to-adult scale change behind the occlusion stage. Do not place a small animal and its adult human endpoint in the same uncovered frame, and do not carry small-animal proportions into the human endpoint.
- In the human endpoint, restate adult head/shoulder/pelvis scale, contact shadow, and bed/floor compression relative to the other person. Focus depth may change sharpness only, not body size or support-plane height.
- Add negatives when relevant: `狐狸巨型化，小狐成人体积，人形缩小成玩具，人狐比例失衡，头身比例错误，前景巨人化，后景玩具人，不同透视空间，床面高度错位，身体缩放跳变`.

## Character Separation

When a group contains multiple distinct extras or multiple similar characters, put cast-separation constraints inside the specific group-scene shot:

```text
四名人物，P1-P4 分别拥有完全独立的五官、发型、穿搭；每个人脸型、发色、服装颜色和款式完全区分；角色站位固定；面部特征全程稳定，不互换长相，不互换衣服。
```

Use negatives such as:

```text
克隆脸，重复五官，人脸趋同，角色互换，同款衣服，穿搭重复，面部变形，换装，人物同化，blended-faces，duplicate-characters，facial color-bleed
```

Do not make cast separation a universal opening block when no group-scene risk exists.

## Physical Contact

For touch, always specify:

- Hand ownership and entry side.
- Contact point and pressure.
- Natural finger bend.
- Which surface or body part occludes which.
- Contact shadow and skin or cloth compression.
- Movement start and end state.

Add negatives:

```text
手指穿透，手掌漂浮，接触点错位，多余手指，手臂断裂，身体穿模，衣料无压痕，缺少接触阴影
```

## Lighting And Realism

- Treat lighting as primary quality control.
- Reference a mature film or series only when translating it into source direction, color relationship, shadow strategy, material response, and a stable look across adjacent shots.
- Never write eye-light or eye-highlights as a standalone effect. Use environment-constrained natural eye reflection and prohibit self-lit eyes.
- For night scenes, use low-key but readable exposure. Avoid contradictions such as "no light source" plus "well-lit face."
- Avoid repeated phrases like "face fully lit"; they force artificial fill.
- Make people belong to the environment: contact shadows, shared color temperature, consistent reflections, material wear, cloth physics, stable perspective, lived-in surfaces, restrained skin texture, pores, small imperfections, and air dust when appropriate.
- Avoid one-note quality stacking such as `8K ultra-realistic`, strong HDR, and `hyper detailed` unless the user specifically wants that style.

## Tears And Emotional Wetness

- When tears, tear sheen, or wet eyes are visible, describe real tear physics: translucent saline liquid slowly welling from the inner corner or lower lid, practical-light reflection only, an irregular gravity-led path along the cheek, small cheekbone gathering, and wet skin reflection that follows pores and facial contour.
- Do not use glowing tears, sticker-like droplets, symmetrical tracks, or generic `tearful eyes` without a physical carrier. Keep the applicable character's emotional grammar intact; do not turn restraint into a sobbing collapse.
- Do not put crying, sobbing, gasping, choking, or breath sounds in audio unless the user expressly requests and the project rules permit them. Add negatives for cartoon tears, glowing tears, fake tear overlays, and exaggerated wailing when relevant.

## Audio Rules

- Default to diegetic-only audio.
- Use low or very low environment sound by default.
- If no dialogue exists, explicitly prohibit dialogue mouth movement, subtitles, voice-over, and background music.
- If dialogue exists, preserve user-supplied dialogue when safe.
- Use sound effects, footsteps, cloth rustle, room tone, rain, door, phone vibration, or object sounds as appropriate; add physiological sounds only when the user expressly requests them and project rules permit them.

## Seedance-2.0 Defaults

Use this mode when the user mentions Seedance-2.0 or when long cinematic prompts are causing unstable generation:

- Keep prompts short, precise, and low-weight.
- Use strong logic isolation for people, light, props, and scene layers.
- Suggested baseline: `9:16, 24fps, 180° shutter, CFG 6-7`.
- Suggested denoise: group scenes `0.50-0.58`; single-person close shots `0.58-0.64`.
- Use negative weight around `1.2` when the interface supports it.
- For group scenes, add `independent lighting for each character` and `independent rim-light on each character` only when needed to reduce face merging.
- Common negatives: `plastic-like skin, wax skin, CG render, over-sharpened, facial color-bleed, blended-faces, duplicate-characters, crushed shadow`.

## Safety And Scope

- Keep romance fully clothed and non-explicit.
- Avoid sexualized body framing, nudity, explicit sexual actions, or minors in romanticized adult framing.
- If unsafe dialogue or action is supplied, offer a concise safe substitute that preserves the dramatic intent.

## Failure Fixes

- Face merging or identity swapping: add character separation, fixed left/right blocking, independent wardrobe colors, independent light, and negatives for blended faces and duplicate characters.
- Outfit swapping: repeat wardrobe anchors inside the shot, lock color and silhouette, and add negatives for wardrobe exchange and same-clothes duplication.
- Bright night scene: name a practical source, reduce fill, preserve readable low-key exposure, and add negatives for flat daylight or overexposed face.
- Self-lit eyes: replace eye-highlight language with natural reflection from the named light source; add negative `自发光眼球`.
- UI gibberish or subtitles: explicitly prohibit subtitles, captions, UI overlays, random text, watermark, and unreadable screen text unless the shot requires a readable prop screen.
- Hand penetration: specify ownership, entry side, contact point, occlusion, compression, and contact shadow; add anti-penetration negatives.
- Plastic skin: remove over-sharp quality stacking; use restrained skin texture, pores, slight imperfection, soft contrast, and film-grain restraint.
- Background music leakage: state diegetic-only, no score, no background music, no music swell.
