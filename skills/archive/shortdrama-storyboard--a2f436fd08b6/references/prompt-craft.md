# Prompt Craft Reference (生成提示词写法)

Read this during generation-mode routing and prompt writing (workflow Steps 4–5).

## Contents
1. Prompt structure
2. Master-quality suffix + negative
3. Camera vocabulary
4. Image-to-video vs text-to-video routing
5. Three-beat effect/transformation formula
6. Consistency tokens

---

## 1. Prompt structure (six segments, in order)

```
[camera move] + [subject + locked appearance tokens] + [one coherent action]
+ [one core effect with direction] + [environment] + [lighting/mood] + [quality suffix]
```

- Lead with the **camera move** — it sets the motion basis (critical for text-to-video).
- Insert the subject's **locked appearance tokens verbatim** from the asset bible.
- **One coherent action** only. Two actions blur — split into two shots.
- Effects must state **direction** (see §5).
- Keep parallel elements ≤ 3 for text-to-video.

## 2. Model-aware quality suffix + negative

Adapt the concrete look and prompt density to the target model. Do not assume that
more quality adjectives produce a better result.

General-purpose default:

```
cinematic film still, shot on ARRI Alexa, shallow depth of field, volumetric lighting,
photorealistic, hyper-detailed, filmic color grading, [PROJECT ART-DIRECTION KEYWORDS],
8k, vertical 9:16
```

For **Seedance 2.0**, compress the suffix and avoid stacking `8k`,
`hyper-detailed`, aggressive HDR, and repeated realism terms. Prefer:

```
cinematic realism, natural skin texture, controlled highlights, filmic color,
[PROJECT ART-DIRECTION KEYWORDS], vertical 9:16
```

Keep prompts concise for Seedance 2.0: prioritize subject identity, one action,
camera motion, spatial direction, and continuity. Remove decorative adjectives
before removing identity or blocking constraints.

Default negative (extend per project):
```
extra limbs, deformed hands, extra fingers, inconsistent face, identity drift,
plastic waxy skin, flat lighting, cartoon, anime, watermark, text, blurry, low detail
```

## 3. Camera vocabulary (effective in generators)

| 中文 | English |
|---|---|
| 缓慢推近 | slow dolly-in / push-in |
| 拉远 | slow dolly-out / pull back |
| 环绕 | orbiting shot / camera circling |
| 升 / 降 | crane up / crane down |
| 跟随 | tracking shot following |
| 手持 | handheld shaky cam |
| 仰拍 | low-angle looking up |
| 俯拍 | high-angle looking down |
| 静态微动 | static shot, subtle motion |
| 慢镜 | slow motion |

Even static shots should say `static shot, subtle motion` so the frame doesn't drift.

## 4. Image-to-video vs text-to-video routing

| 维度 | image-to-video 图生 | text-to-video 文生 |
|---|---|---|
| 参考 | 需首帧/面卡/turnaround | 无需参考 |
| 强项 | 脸/身份一致性、变身、特写 | 运镜自由、环境、群像、空间 |
| 适用镜 | 主角特写、化形、名场面主体 | 建立镜、氛围、过场、群像 |
| 一致性靠 | reference image + 复述 tokens | 文字复述 tokens(每镜) |

Rule of thumb: **hero/character = image-to-video; mood/space = text-to-video.**
In text-to-video, restate the 3 identity anchors (e.g. hair + eyes + signature
marker) every shot, since there's no reference image.

## 5. Three-beat effect / transformation formula

Any process effect (magic cast, transformation, dissolve) = **build → change → settle**,
each beat with a concrete visual anchor:

**Magic cast:**
```
[build] energy gathering inward toward [carrier], runes waking;
[change] condensing into [form], particles spiraling, casting [color] glow;
[settle] bursting/releasing in [direction] with [particle] trailing.
```

**Animal↔human transformation (highest crash risk):**
Wrap the topology-changing middle frame in a light cocoon so the model never renders
a half-formed hybrid:
```
[phase 1] the animal, glowing, light gathering;
[phase 2] its body dissolving into a swirling cocoon of [energy-color] light,
silhouette elongating(→human) or folding(→animal) within the glow, form obscured
by radiant energy at the peak;
[phase 3] the light dispersing to reveal the [human/animal], [preserved anchors]
remaining, particles settling.
```
Rules: obscure the peak frame; keep 2–3 identity anchors present throughout; direction
= rising to become human, folding to become animal; cocoon color = the character's
energy color; keep it 1.5–2.5s.

## 6. Consistency tokens

For each character, lock and reuse **verbatim**: hair (color+style), eyes (color+detail),
one signature marker (sigil / ears / tail / scar), palette, energy color. Restate the
top 3 in every prompt. Never paraphrase — "silver hair" and "platinum-silver hair"
read as different people to the model.
