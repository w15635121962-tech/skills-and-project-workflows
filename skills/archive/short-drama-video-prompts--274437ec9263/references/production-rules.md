# Production Rules

## Format C checklist

Use this order for a full group:

1. `GROUP｜scene｜dramatic function`
2. `GLOBAL CONFIGURATION / 全局设定`
3. `开场状态锁定`
4. `环境`
5. `光照基调`
6. Repeated shots: `duration`, `镜头`, `画面`, `微表演`, `对白反应`, `人物背景融合`, `光影`, `音频`, `运动强度`, `负面提示词`.

Give each shot a subject, framing, angle, movement, focal length, depth-of-field intent, and a clear focal target. Use 35mm for establishing space, 50mm for movement and medium coverage, 65-70mm for contextual detail, 85mm for emotional close shots, and 100mm only when the full facial performance remains legible.

## Reality baseline

Default visual wording when the user has not supplied a fixed opening:

`写实照片级、超写实质感、真人实拍电影剧照，阿莱 Alexa 65摄影机质感，竖版9:16画幅，浅景深，细腻胶片颗粒。真实皮肤纹理、可见毛孔与轻微瑕疵，非完美对称，真实布料垂坠和接触压痕，真实接触投影，空气中少量浮尘。真人眼眸只保留环境反射，禁止眼球自发光；禁止塑料假肤、蜡质假面、CG建模质感、卡通画风、无神空洞双眼。`

Do not repeat strong detail words excessively. In dark scenes, prioritize low-key readable contours over pore-level sharpness.

## Lighting continuity

Define and keep four items constant across a contiguous scene:

- Key source and direction.
- Secondary ambient or bounce source.
- Shadow strategy and retained dark detail.
- Palette lock: dominant hue, dark-value strategy, highlight restraint, and permitted accent color.

Film references must become usable facts. Example: `参考《Normal People》的克制窗光：窗侧柔和漫射光为主，室内向纵深自然衰减，生活痕迹保留，禁止摄影棚均匀补光。`

Night correction wording:

`低照度可辨面光，人物脸部不明亮，只在暗部保留眼睛、鼻梁、嘴唇与下颌的轮廓信息；背景比人物更暗，人物不被补光照亮。`

Avoid these conflicts:

- no visible source + strong key light;
- no exterior spill + doorway spill;
- no direct moonlight + moonlight outlining the face;
- dark room + repeatedly demanding fully exposed faces.

For blinds, state: `百叶窗纹理只落在墙面、窗台、课桌和地面，不落人物脸部。`

## Blocking, axis, and reference frames

- Reference images lock location, furniture, camera side, perspective, and spatial arrangement only unless the user says they also lock identity or styling.
- Repeat anchor facts in each decisive shot: seat, window side, desk row, three empty stools, foreground/background order, or walking direction.
- Use Z-axis for two people moving toward or away from each other in vertical framing.
- Carry the final frame forward as the next shot's first-frame reference only when the user asks for an A-plan / first-frame inheritance workflow.
- Do not create a frontal two-person horizontal standoff in a narrow vertical frame unless that is the deliberate reference composition.

## Coverage and short-drama editing

- Open dialogue scenes with an establishing medium/wide shot, then obtain clean reverse close shots and over-shoulder alternates.
- Cut to a reaction at the line's emotional landing, not merely after the speaker finishes.
- Use an insert only when it advances story or makes an emotion physical; preserve shoulder/body/environment context.
- Flag J-cut or L-cut opportunities in storyboard analysis. In direct video prompts, encode the actual audio cue instead of theory.
- Let a line reaction outrank generic micro-expression. Keep facial beats small and give the emotion a body action.

## Sound

Use only diegetic audio unless requested otherwise. Format examples:

`【环境·低·持续】<空教室底噪 窗边风声>【动作声·极低】<衣料轻擦>【人声·清晰·女声】Zoe（克制）：“...”`

When there is no dialogue:

`无对白，不生成说话口型，禁止字幕，禁止旁白，禁止背景音乐。`

Vary environment level with dramatic rhythm. Do not permanently force it to low: use low for secrecy, medium/high for crowd eruptions, then drop it to create an emotional vacuum.

## Contact, tears, sweat, and UI

For hand contact, state:

`两只手属于不同人物，左右方向清楚；拇指在外侧，指节自然弯曲；手掌不穿透皮肤或衣料；接触处有轻微压痕、遮挡关系和接触阴影。`

For tears or sweat, use a restrained physiological-saline description, never glow:

`半透明生理盐水质感，随重力自然滑落，只有细腻环境反射，不发光、不像油膜或玻璃珠。`

For phones/UI:

- Never ask for dense readable UI, timestamps, message lists, or app labels.
- Use a simple photo, large contact name, or abstract low-brightness screen reflection.
- Add: `禁止乱码，伪文字，错误字母，小字密集，UI错位，按钮畸形。`

## Multi-person stability

Put this only in a shot that visibly contains the crowd:

`四名人物，P1-P4拥有完全独立的五官、发型与穿搭；脸型、发色、服装颜色和款式明确区分；站位固定，面部特征全程稳定，不互换长相、不互换衣服。`

Pair it with:

`克隆脸，重复五官，人脸趋同，角色互换，同款衣服，穿搭重复，面部变形，换装，人物同化。`

## Negative vocabulary

Use only negatives relevant to the shot. Core set:

`模糊，低像素，压缩噪点，塑料皮肤，蜡质假面，CGI塑料感，3D渲染，动漫插画感，磨皮，死眼，眼球自发光，机械眨眼，表情冻结，人物边缘抠图感，贴纸感，色温不一致，光源方向混乱，接触阴影缺失，空间透视错误，背景扁平，字幕，伪文字，背景音乐。`

Add only as needed:

- Contact: `手指融合，手腕穿模，左右手反接，手掌反向，手臂穿透身体。`
- Night: `亮堂教室，强主光，棚拍补光，门缝亮光，白天窗光，百叶窗条纹打脸。`
- Space: `场景重构，人物移位，地面扭曲，墙体变形，椅子数量变化，透视错乱。`
- Crowd: use the multi-person set above.

## Prompt audit order

When asked to diagnose a prompt, check in this order:

1. Contradictory light instructions.
2. Missing or unstable blocking/axis anchors.
3. Shot subject and framing mismatch.
4. Dialogue versus mouth/scene logic.
5. Contact and hand geometry risk.
6. UI/text generation risk.
7. Excessive detail, conflicting negatives, or unrelated names/tags.
