# AI Multi-Character Blocking & Scene Staging Protocol

AI多人物锁站位与场面调度协议

## Core Principle

The hardest part of multi-character AI generation is not the characters themselves, but **stable spatial relationships**, **continuous camera logic**, and **character identity without drift**. Diffusion models fundamentally don't understand 3D space — they do 2D probability prediction. Multi-person scenes easily collapse.

**Priority**: Spatial structure > Camera direction > Blocking > Movement paths > Character anchors > Character details.

## 1. Screen Position System (最重要)

Use screen coordinates, NOT relative positions:
- screen left / screen right / center frame
- foreground / midground / background / deep background
- viewer left / camera left

Example: "primary subject screen left foreground, secondary subject screen right midground"

## 2. Camera Lock (摄影机锁定)

Must fix camera facing direction (camera facing east/north etc.). Subsequent shots only change framing (wide/medium/close-up), NOT camera direction, to avoid axis crossing and spatial collapse.

Recommended: "camera facing east, 35mm lens, eye level, static shot"

## 3. 180° Rule & Axis (180°法则与轴线)

Multi-person dialogue/confrontation scenes must strictly maintain camera on the same side of the axis.
Recommended: "consistent camera orientation, camera remains on same side of axis"

## 4. Character Hierarchy & Anchors (角色层级与锚点)

Use: Primary subject / Secondary subject / Background extras structure.
Characters must have strong visual anchors (scar-faced commander, silver-haired queen, red-armored general), NOT generic man/woman.
Priority-describe the primary subject for significantly improved stability.

## 5. Negative Space (负空间)

Multi-person scenes must preserve sufficient negative space to prevent character merging or limb overlap.
Recommended: "large negative space between characters, empty center composition"

## 6. Most Stable Compositions (最稳定构图)

- **Symmetrical composition**: Dialogue, confrontation, ritual
- **Triangular composition**: Three-person relationships, group portraits
- **Depth layering**: foreground + midground + background (most recommended)

## 7. Industrial Prompt Structure Order

1. CAMERA (position, focal length, facing direction)
2. SPACE (environment, composition, negative space)
3. BLOCKING (character screen positions + foreground/midground/background)
4. RELATIONSHIP (distance, sightlines, power dynamics)
5. LIGHTING
6. DETAILS (character specifics)

## 8. Optimal Workflow

1. Generate empty scene first (lock space, perspective, lighting)
2. Lock camera direction
3. Add characters (described by hierarchy)
4. Maintain axis and movement path consistency
