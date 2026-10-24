# User Standards And Learned Failure Checks

Use this reference for the user's established Chinese vertical short-drama prompt workflow, especially the 九尾狐 project. It is a standing house style layered on top of `production-rules.md`.

## Output Format

- Use Chinese Format C.
- Use `shot` labels only. Do not use mixed labels such as `Shot 1-2` or `1.01`.
- Every group normally resets numbering from `shot 1`.
- Every shot title must state whose shot it is, any visible blocking character, shot size, angle, movement, lens, and duration.
- Every shot must include: `镜头`, `画面`, `微表演`, `对白反应`, `人物背景融合`, `光影`, `音频`, `运动强度`, `负面提示词`.
- For full prompt groups, include opening state, environment/spatial relationship, light baseline, audio rules, and group-level negatives.
- Full prompt groups should stay within the user's current requested character range when one is stated. Single-shot revisions, audits, or field replacements do not need to meet full-group length.

## Fixed Quality Wording

When the user asks for a full prompt group, preserve this exact fixed quality block unless the user explicitly replaces it:

```text
写实照片级、超写实质感、真人实拍电影剧照，采用阿莱 Alexa 65 摄影机拍摄，85mm 定焦镜头，光圈 T1.8，竖版 9:16画幅，180度快门角，浅景深，柔和奶油般散景，细腻胶片颗粒质感。真实皮肤纹理，清晰可见毛孔，SSS光影效果，肤色只呈现真实皮肤下轻微血色，不形成发光红脸；真人质感眼眸只保留真实环境反射，禁止眼球自发光。真实布料垂坠动态褶皱，真实接触投影，光束中漂浮细微尘埃丁达尔效果。
```

## `@` Tagging

- Use `@` only for people, props, or scenes visibly present and identifiable in the current shot.
- Do not tag off-screen characters, characters mentioned only in dialogue, or vague background silhouettes.
- Prefer `@` in visual fields such as `画面` and `微表演`.
- In `对白反应`, `音频`, and negatives, do not tag off-screen people.
- If an off-screen person must be named, write the name without `@`.

## Asset Cards

- The user has character and prop asset cards. Do not restate full wardrobe, face, hair, or prop design unless the shot needs a specific physical state.
- Use asset-card tags for visible major characters and props, such as `@Sera`, `@Lucian`, `@Ruby`, `@Theron`, `@血脉契约纹`, `@药剂瓶`, `@银蛇镇纸`, and `@羊皮卷`.
- Focus shot prose on blocking, contact, light, expression, and action state rather than re-describing the asset card.

## Character Behavior

- Sera: calm, restrained, elegant, rational, strategic. Pain makes her quieter. Do not make her cry, scream, collapse, or beg. Show pain through fingertip pressure on the contract mark, shoulder/neck tension, controlled sleeve movement, colder eyes, or prop contact.
- Lucian: proud, flirtatious, entitled, emotionally exploitative, and slow to understand harm. His cruelty is casual and taken for granted, not cartoon villain rage. Avoid roaring, glaring, or exaggerated evil smiles.
- Ruby: low-rank red fox, vain, dependent, timidly smug. She is not a queenly antagonist. Her challenge is dependency-based and small. She has exactly one red fox tail.
- Theron: future fox king, loyal and powerful, voluntarily soft toward Sera. Nine-tail motion should remain conservative and stable.

## Dialogue And Audio

- Spoken dialogue must be in English. Non-dialogue prompt prose stays Chinese.
- Every English spoken line must appear in both `对白反应` and `音频`.
- Only the speaker generates mouth movement. All other visible characters must be explicitly prohibited from mouth movement.
- No voice-over, no subtitles, no background music.
- Do not write physiological sounds such as breathing, gasping, heartbeat, swallowing, or sexual/biological sounds. Use only diegetic environment/action sounds: fabric, steps, wind, water, glass, metal, paper, magic hum, stones, doors, etc.
- Environment level should follow drama rhythm: `极低/低` for secrecy and contained reactions, `中` for battle or collapse, and `瞬间抽空` for emotional impact.

## Dialogue Reaction Field

`对白反应` is mandatory reaction logic, not a placeholder.

For dialogue shots, write:

- who speaks;
- the exact English line;
- who hears it;
- who is changed by it;
- who is forbidden to speak or mouth words;
- how the line lands in body grammar, props, distance, or magic state.

For no-dialogue shots, do not merely write `无台词，无口型`. Still state:

- which implied plot line, prior dialogue, or off-screen event triggers the shot;
- who receives or bears the emotional impact;
- who remains silent;
- how the reaction is visible through shoulders, hands, eyes, props, magic, or blocking;
- continue prohibiting voice-over, subtitles, and unintended mouth movement.

## Lighting

- Mature film/TV references must be executed, not merely named.
- For every light reference, specify source direction, source quality, color relationship, shadow strategy, material reflections, and continuity across adjacent shots.
- A contiguous scene uses one main lighting logic. Do not change film references or light direction shot by shot.
- Day study default: use the Pride and Prejudice manor study day interior look. Right-rear tall window daylight filtered by thin curtain is the fixed key; it illuminates the desk right edge and Lucian/Ruby warm zone. Left shelves and stone walls absorb light; Sera stays in a cool gray sky-scatter zone. Warmth comes only from daylight bounced by honey wood, obsidian, and metal, not from fireplace or night sources.
- Night scenes need a clear bright practical source, readable subject exposure, and textured shadows. Avoid both dead-black underexposure and fake daylight brightness.
- Eyes should contain only environment-constrained reflections, never self-lit highlights.

## Eye Direction

- Do not write vague `looks at`.
- Specify where the gaze starts, where it lands, and whether pupils have a clear focus point.
- For Lucian speaking to Sera while Ruby is visible, state that his gaze passes over Ruby or the desk and lands on Sera's eyes or wrist direction.
- Add negatives for empty gaze, dead-fish eyes, unfocused pupils, staring into nowhere, and self-lit eyes when needed.

## Tears And Tear Control

- Whenever a prompt includes tears, tear sheen, wet eyes, crying, or a tearful reaction, describe the tear physically rather than using a vague `含泪` or `泪光`.
- State the source and progression: a real human tear slowly wells from the inner eye corner or lower lid; it is translucent saline, not a glowing bead; it reflects only the current practical/environment light; it follows an irregular gravity path along the cheek, may gather at the cheekbone, and leaves a small wet reflective tear trace on skin texture. If relevant, add tiny droplets held at lash roots.
- Keep the emotion restrained when that fits the character. For Sera, tense facial muscles and a slight lip tremor may coexist with a controlled expression; she does not sob, cry out, or collapse. Never add crying, gasping, choking, or breath sounds as audio.
- Tie the tear reflection to the active scene light: candlelight, cold moonlight, rain-gray skylight, or cold green-silver interior light. Never make tears self-lit, magical, oversized, or uniformly symmetrical.
- Add shot negatives when tears are visible: `卡通眼泪，假泪贴片，眼泪发光，泪流满面，嚎哭，哭喊口型`.

## Magic And Particles

- Magic is local, restrained, and physically integrated. Do not let it become screen-wide light pollution.
- For 九尾狐 magic color, attack phases, mark surfacing/dissolving, iris activation, and clan-specific VFX descriptors, also use [jiuweihu-magic-vfx.md](jiuweihu-magic-vfx.md). That file provides project energy colors and phrase banks; this file still controls restraint, light hierarchy, and realism.
- For `@血脉契约纹`, keep magic on the wrist surface and around subcutaneous old lines. Dark red travels along the original snake-shaped mark.
- Particle rules: no more than roughly a dozen particles; needle-tip size; floating one to two centimeters above skin; brightness lower than the main light; no room-wide red fill; final motion should have a clear endpoint, often pressed back under the skin by Sera's fingertip.
- The mark must follow skin texture, pores, wrist curvature, occlusion, and fingertip pressure.
- Negatives: red light explosion, full-screen particles, particle spray, floating magic circle, magic column, red smoke, room dyed red, mark detaching from skin, mark crawling over the whole body.

## Physical Contact

Always specify:

- hand ownership;
- entry side;
- contact point;
- natural finger bend;
- pressure;
- occlusion;
- contact shadow;
- cloth, skin, fur, or prop deformation;
- start and end state.

For Lucian holding Ruby's waist: his right hand enters from behind Ruby, touches only her right waist, fingers naturally curved, with cloth compression, occlusion, and warm daylight contact shadow.

For Lucian touching Ruby's tail: hand touches only the outer fur layer, does not pass through the tail or break the root; fur changes direction under pressure and slowly rebounds.

## Ruby Fox Traits

- Ruby has exactly one red fox tail.
- Lock tail root direction, fur texture, contact shadows, and deformation.
- Tail must not glow, multiply, pass through desk/clothes/body, or become a decorative ribbon.
- Fox ears must have root attachment and action rhythm. Example: both ears press back, right ear trembles first, left ear follows half a beat later. Ears must not become floating accessories.

## Multi-Character Separation

For two or more visible characters, actively separate identities in positive text:

- distinct facial features;
- distinct face shapes;
- distinct hair colors;
- distinct species traits;
- distinct material silhouettes;
- fixed positions;
- no color/light bleeding between characters.

Use negatives when relevant: cloned faces, face merging, character swapping, outfit swapping, `blended-faces`, `duplicate-characters`, `facial color-bleed`.

## Form Change And Residual-Body Prevention

- Before writing a transformation, lock both endpoints: identify the exact start form, exact end form, and whether the end form retains any species traits. Never leave this implicit.
- For `狐形 → 纯人身`, write the completed end state plainly: the fox body, fox head, muzzle, paws, fur, ears, tail roots, and all duplicate animal silhouettes have completely disappeared; only one stable human body remains on the original contact surface. Do not write `尾影` or a background fox silhouette in the same shot.
- If the requested end state is `人形保留九尾`, state that it is one human body with nine tails attached at the human lower back; the original fox torso, head, paws, ears, and fur are fully gone. Do not mix this with `纯人身`.
- Use a three-part occluded transition: energy gathers to a controlled anchor, curtain/tails/mist/light briefly hide topology change, then the end form settles with a fixed head, shoulders, hips, feet, and contact shadow. Do not show both forms at once unless the user explicitly asks for a split-form image.
- Add transformation negatives as applicable: `狐形残留，双重身体，残留狐头，残留狐爪，残留狐身，重复动物轮廓，人狐叠影，狐头人身，兽形与人形同时存在，尾根错位，骨骼拉伸，面部融化`.

## Fox-Human Scale And Support-Plane Lock

- When fox form and a human appear in one shot, declare a readable real-world scale anchor instead of only saying `小狐`: state where the fox's head reaches relative to the human hand, forearm, knee, or pillow; state whether it is held, on the bed, or on the floor; and give both bodies one shared bed/floor plane.
- For a small fox held by Sera, lock: its head fits beneath her palm/at her inner forearm, its body occupies only a limited section of the pillow or her lap, and its paws create small localized mattress compression. Never allow it to reach adult torso scale.
- For the human endpoint after transformation, lock the new body independently: one adult human body on the same bed plane, hips and shoulders resting at plausible adult scale, mattress compression widening under body weight, head/shoulder height consistent with Sera. Do not preserve the fox's small-body scale after the occlusion transition.
- Do not show an adult human and the small fox in the same uncovered frame during transformation. Use the occluding curtain/light/tail phase to hide the scale change; before and after frames must each have their own stable physical scale.
- In every two-character frame, state that perspective changes only focus and occlusion, never head size, body scale, distance, or contact-plane height.
- Add negatives: `狐狸巨型化，小狐成人体积，人形缩小成玩具，人狐比例失衡，头身比例错误，前景巨人化，后景玩具人，不同透视空间，床面高度错位，床垫压痕错误，身体缩放跳变`.

## Spatial Locks And Over-Shoulder Grammar

- Every multi-character shot must name each visible person's fixed screen position, body facing, distance layer, and shared support plane: for example, `A在画面左前景朝右，B在右中景朝左，两人站在同一地面线`.
- For every over-shoulder shot, write all five locks: camera is behind whose left or right shoulder; where that shoulder occupies the frame; who is in focus; camera direction across the 180-degree axis; and the listener/speaker body orientation. Do not label a shot `越肩` when no foreground shoulder is visible.
- Example wording: `相机位于A左后方，A左肩与后脑占画面左下15%虚焦，镜头沿既定轴线朝右前方拍B；焦点锁B双眼与上半身，A始终背向镜头，B正面微朝左。`
- Across reverse shots, preserve the same axis and screen geography. Do not swap left/right, turn both characters toward camera, let the foreground shoulder jump sides, or change their standing/seating plane merely because focus changes.
- Add multi-person spatial negatives: `站位漂移，左右互换，越肩主体错误，前景肩膀消失，错误过肩，轴线跳变，人物朝向混乱，视线方向冲突，不同地面平面，距离关系错误，人物比例失衡`.

## Story And Shot Design

- Plan storyboard first when the user asks for it, then produce prompts.
- One shot should have one core function and one coherent action. Split when action, emotion, magic phase, or camera basis changes.
- Do not let Ruby steal the core of Lucian/Sera humiliation scenes. Ruby can be a visual contrast or humiliation tool, but the emotional transaction is between Lucian and Sera.
- Abstract emotions must be converted into visible physical carriers: contract mark pressure, sleeve smoothing, silver snake paperweight touch, hair/fabric/dust movement, tail/ear motion, or spatial distance.

## Battle Memory Rules

For Sera saving Lucian, use direct visual actions rather than vague montage:

- first rescue: Sera blocks an arrow for Lucian;
- second rescue: Sera blocks a blade for Lucian;
- third rescue: Sera blocks a magic attack for Lucian.

Each rescue must make the attack path clear:

- where the attack comes from;
- which part of Lucian is targeted;
- how Sera enters the attack line;
- exactly where the attack is stopped;
- how Lucian remains in the protected position.

Avoid gore, dismemberment, spraying blood, or complex extra battle choreography. Memories may be triggered and returned through `@药剂瓶`, `@血脉契约纹`, or glass/reflection anchors so the sequence does not detach from the present scene.

## Learned Failure Checks

Before final output or audit, run these checks:

1. Did the prompt write concrete space, position, action start, and action result instead of only plot?
2. Does every no-dialogue shot still have `对白反应` reaction logic?
3. Are `@` tags limited to visible, identifiable objects in the current shot?
4. Is the lighting reference translated into source, direction, color, shadow, reflection, and continuity?
5. Are night scenes neither dead-black nor fake daylight?
6. Is every important gaze given a precise focus direction?
7. Is magic particle count, range, brightness, and endpoint controlled?
8. Is every hand/tail/body contact physically specified?
9. Is Ruby locked to one tail and stable ears?
10. Are multi-character shots protected against face merging and outfit swapping?
11. Are asset-card details not overwritten by excessive wardrobe/appearance prose?
12. Does Lucian remain casually cruel rather than cartoon evil?
13. Does Sera remain controlled rather than a crying victim?
14. Does Ruby remain dependent and low-rank rather than queenly?
15. Are Sera's rescues direct and readable: arrow, blade, magic?
16. Do memories return to a present-scene physical anchor?
17. Does audio exclude voice-over, subtitles, background music, and physiological sounds?
18. Does positive text describe the correct result before negatives suppress failures?
19. Are shot labels clean and reset by group?
20. Is one shot overloaded with too many actions or effects?
21. Are abstract emotions turned into visible physical carriers?
22. In humiliation scenes, is Ruby only a contrast tool while Lucian and Sera remain the core?
23. Is prompt length spent on blocking, light, action, contact, dialogue reaction, and failure control rather than empty adjectives?
24. If tears or wet eyes appear, are their source, saline texture, environment-only reflection, gravity path, skin wetness, and restrained performance all stated, with no physiological crying audio?
25. For every transformation, are start form, end form, retained traits, and disappearance of the old form explicitly locked so no residual fox body remains?
26. For every two-person or over-shoulder shot, are shoulder ownership, camera side, focus subject, axis direction, screen positions, facing, and shared support plane unambiguous?
27. When fox and human forms coexist or transform, are their relative scale anchors, shared floor/bed plane, body-weight compression, and hidden scale-change phase explicit?
