# Automatic Scene Completion Protocol

Use this reference whenever a single image must become a 16-angle environment, character, prop, or vehicle reference grid.

## Completion modes

Choose one mode from the request, or use `balanced completion` by default:

- `strict reconstruction`: preserve only visible facts; infer minimum hidden geometry; flag uncertainty.
- `balanced completion`: infer physically necessary hidden structure and add restrained, same-location details.
- `concept expansion`: allow clearly labeled designed additions, while keeping visible reference elements dominant.

## Evidence ledger

Write an internal ledger before the prompt:

| Layer | What belongs here | Prompt treatment |
|---|---|---|
| Observed locks | visible objects, proportions, colors, materials, light, weather, camera relationship | state as fixed facts |
| Structural inferences | occluded backs, hidden continuations, support surfaces, cable/road/building continuation | state as plausible continuity |
| Creative completion | non-visible atmosphere, restrained background detail, optional set dressing | label as designed addition |

Never promote a structural inference or creative completion into an observed fact. The final prompt may be confident and concise, but the design bible must retain this distinction.

## Environment completion heuristics

For an architectural or street scene, complete in this order:

1. Establish a center axis and a ground plane from curbs, road vanishing lines, walls, and horizon.
2. Continue visible building masses, wall thickness, floor levels, window spacing, fire escapes, rooflines, gates, and service doors using the same construction system.
3. Continue utilities along plausible attachment points: poles, cables, junction boxes, pipes, conduits, drains, and lighting fixtures.
4. Continue surface logic: brick courses, mortar, cracks, patches, stains, graffiti layers, curb wear, puddles, leaves, and contact shadows.
5. Keep traffic objects and street furniture anchored to the same curb, lane, sidewalk, and scale. Do not teleport cars, bins, bicycles, signs, or poles between angles.
6. Preserve the same atmospheric depth, weather, sun direction, shadow softness, and reflected color. A hidden side may be darker or less detailed because of occlusion, not because the time of day changed.

For a character, creature, prop, or vehicle, complete in this order:

1. Lock silhouette, proportions, pose phase, contact points, and all visible asymmetry.
2. Infer hidden surfaces from construction logic, not from a new design direction.
3. Continue seams, fasteners, panel breaks, hair/fur/scale direction, material roughness, wear, and edge damage.
4. Preserve identity and do not mirror asymmetrical details.

## Prompt language

Use explicit completion language such as:

`complete the unseen sides with physically plausible structural continuity inferred from the visible reference; extend the same wall thickness, window rhythm, cable routing, curb geometry, pavement wear, material response, and shadow logic; restrained designed additions only, subordinate to the observed reference; no new landmark, no new dominant subject, no invented readable signage.`

For a strict reconstruction use:

`hidden areas remain conservative and minimally inferred, no decorative invention, flag uncertain geometry rather than changing the visible design.`

For a narrative character use:

`emotional arc: [current node] remains unchanged across the orbit; completion affects only unseen construction details, never identity, expression, action, or costume intent.`

## Assumption block format

Add this before the synthesis prompt when needed:

`Scene completion assumptions:
1. Inferred — [hidden structural continuation].
2. Inferred — [material/utility/ground continuation].
3. Designed — [optional restrained atmosphere or set dressing].`

Keep assumptions concrete and short. Do not list every visible object again.
