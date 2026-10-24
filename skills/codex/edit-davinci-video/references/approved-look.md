# Framing and Animation Reference

These are adjustable examples for a 3840x2160 canvas and source. Adapt to the actual source dimensions, aspect ratio, timeline frame rate, and the user's approved layout. Inspect the current clip and render a comparison before broad application. No external screenshot or private project is required.

## Camera

- Example top-right square: Edit Zoom X/Y 0.4, Pan 1440, Tilt 600, Crop Left/Right 840, Top/Bottom 0 for a 3840x2160 source. This produces an approximately 864x864 displayed square. Confirm Resolve's coordinate conventions and rendered position.
- Enlarge the subject inside that fixed box with an upstream Fusion Transform Size of about 1.25. Keep the face centered and headroom modest; adapt to the original composition.
- Example rounded mask in source coordinates: Width 0.5625, Height 1, Center (0.5, 0.5), CornerRadius 0.08. Route MediaIn through the framing Transform to a Merge foreground, with a transparent Background and rounded mask, then MediaOut. Verify that the outer box stays fixed while the subject is enlarged.
- When full-screen camera is requested, establish one horizontal center and retain it across punch-ins. Do not carry source-specific pan values into another recording.

## Screen and articles

Screen pan and zoom depend on the content. Make post text large and readable, keep its profile/source identity near the top, and position the main content clear of the camera. Shift vertically when needed to reveal the complete graph or relevant passage.

For an article, prioritize the complete headline, source identity, and discussed text or key points. Crop irrelevant lower-page content, embedded video, and sidebars instead of reducing the whole article to an unreadable size. Keep that framing through the passage. Match unused canvas and crop surrounds to the adjacent page or B-roll background color so screen edges do not create unnecessary black rectangles. Inspect each source; there is no universal article transform.

Preserve the camera-in-corner and screen layout where requested. Keep calendar or chronological timeline graphics static unless the user requests animation.

## Animation and overlays

- Align sound effects by their audible onset, accounting for leading silence, rather than by their file edge or loudest peak. Measure each source; do not use a fixed offset from another edit.
- Use a readable, available sans-serif font. A title can slide smoothly in from one side and exit toward that same side. A 12-frame entrance at roughly 30 fps is a starting example; scale duration to the project. Anchor the exit to the clip end when trimming should preserve it.
- Size paired logos by visible artwork, not transparent padding. Positions around x=0.18 and x=0.82, y=0.5 are optional starting points when they avoid the speaker and important screen content. Keep original artwork and source attribution as appropriate.
- Optional restrained pop expression: `u=clamp((time-start)/duration,0,1); scale=base*(1+1.4*(u-1)^3+0.4*(u-1)^2)`. Define the expression variables in the chosen animation setup and verify the result.
- Optional gentle persistent wiggle in degrees: `0.65*sin((time-start)*0.075+phase)+0.2*sin((time-start)*0.13+phase)`. Adapt speed to frame rate; use slightly different phases for pairs.
- When a still-image push-in is appropriate, use a native Transform with a fixed center, for example Size 1.0 to 1.025 over the visible duration. Keep all required labels intact and review actual motion for stepping or drift. Static-layout requests override this example.
- Excerpt highlights can use pale yellow at about 42% opacity where readable. Cover the complete referenced lines while preserving source text and pixels. Keep highlights reversible and respect any requested exceptions.

## Resolve integration checks

Fusion keyframe readback does not prove the active timeline output uses that composition. Inspect the intended composition and its MediaIn or Loader path, then verify rendered output before adding duplicate effects.

After inserting stills, titles, or other overlays, read back their actual start/end and inspect affected tracks. Integrations may use default durations or different record-frame conventions; a successful call does not prove correct placement. Inspect render marks after frame capture. Correct unintended ripples or duration errors from a recoverable version.

Prefer supported direct duration and retime controls. If interchange reconstruction is necessary, preserve unrelated tracks, media, grades, Fusion, audio, keyframes, and manual changes. Import as an identified version and verify output and timing before using it as the working edit.
