---
name: edit-davinci-video
description: Edit videos in DaVinci Resolve using approved camera framing, screen-recording layouts, authentic source screenshots, unique B-roll, and restrained title/logo animation. Use for visual passes and additions to an existing dialogue edit.
---

# DaVinci Visual Editing

These are configurable defaults for a talking-head and screen-recording edit. Apply within the requested section and scope; newer explicit directions override defaults. Do not add B-roll when the user has excluded it. For dialogue cutting use `first-cut-davinci-dialogue`; for audio transitions use `smooth-davinci-audio-cuts`.

## Control and preservation

Prefer Resolve MCP for inspection and changes. Use computer use only for capabilities unavailable through supported APIs. Inspect the current timeline, playhead, selection, track occupancy, and source ranges each turn: the user may make manual edits between requests. A stale selected ID is not authority to edit another clip. Preserve manual edits, source offsets, sound treatment, and timing outside the request. Save a recoverable version before structural changes. Complete authorized work without unnecessary confirmations; when the user asks to approve one sample first, show a concrete rendered sample and wait before applying it throughout.

## Main-timeline additions

For future projects, label screen-recording video clips Orange and camera video clips Blue on the timeline. These are organizational clip colors, not image treatments. Preserve explicit review highlights such as yellow cut-review clips. Apply these colors to new work; preserve existing organizational colors unless asked to change them.

Place each added image, logo, title, or B-roll shot on the next free existing video layer at its intended time range, above content it must cover. Reuse available layers; do not create a new track for every asset. Simultaneous overlays need separate available tracks. Keep additions as separate named, editable main-timeline clips, not fused into the camera or nested together. Fusion inside a standalone overlay may implement animation, but the overlay must remain individually movable and trimmable. Cropping and corner masks are camera treatments, not additional editorial assets.

Use native still-image clips for screenshots and graphs, not MP4 wrappers. Store media in a stable project asset directory. Hold duration must remain adjustable. For a screen freeze filling a deleted gap, capture the preceding screen clip's exact final source frame, preserve its screen framing, and stop at the next occupied clip without ripple changes. An extracted still is acceptable; accurately describe it as a still-frame hold.

## Source authenticity and editorial coverage

Use actual screenshots or original images from the specified source. Do not redraw charts, invent posts, recreate article cards, or generate substitutes unless the user explicitly asks. Match the exact figure to a supplied reference, including its title, axes, labels, and legend; a different authentic figure from the same article is still wrong. Preserve source pixels, aspect ratio, readable labels, and attribution. A matching plain background may fill unused canvas without changing the figure.

For a varied B-roll pass, use distinct footage for repeated subjects unless reuse is requested. Check existing timeline usage and source ranges so a renamed or retrimmed copy does not disguise duplication. Prefer clean real footage that the user can use in the intended distribution. Match the footage to the spoken concept. Use simple graphics where they improve understanding, keep them clear of the speaker, and balance any appropriate sound effect beneath the dialogue.

Align every B-roll entrance, exit, and shot change to an existing dialogue/camera cut. Prefer cuts at the start of a new sentence or thought; a cut inside a sentence is not automatically a good visual-change point. Do not add an arbitrary B-roll switch shortly before a sentence ends. Hold one continuous shot across internal dialogue cuts when it still illustrates the same thought, and check downloaded footage for baked-in shot changes too.

Favor the screen recording whenever the speaker discusses relevant on-screen material. Cover requested intro passages with relevant B-roll; do not expose a private script or document as incidental screen content. When the requested layout is camera-in-corner plus screen, retain it through screen holds and script-reading sections instead of switching to full camera. Use full camera for direct delivery only when consistent with the requested layout. The request controls whether new B-roll is allowed.

## Approved visual treatment

- Time animation sound effects by their audible waveform onset, not the audio file's left edge or loudest peak. The sound should begin with the graphic's entrance/movement, rather than after it has settled on screen. Inspect leading silence and offset the audio clip earlier as needed; verify against actual animation playback. Preserve user-adjusted timing as the reference. Balance effects beneath dialogue and keep them separately editable on the next free audio track.

Read [references/approved-look.md](references/approved-look.md) when setting camera framing, screen layouts, or animation.

- Preserve the approved top-right square camera: rounded corners, centered head-and-shoulders framing, 25% tighter inside the box. Keep relevant screen content unobstructed.
- The full-screen speaker stays consistently centered with a fixed horizontal position. Sprinkle tasteful punch-ins/zooms at selected cuts or emphatic statements; avoid lateral drifting or zooming every cut.
- Tweets should be large and readable, filling the screen naturally with the profile near the top. Follow the passage: favor text while he reads it; shift vertically to show the complete graph when he discusses it. Avoid an isolated small cropped card surrounded by black space.
- Article framing: prioritize a large, complete headline and the relevant passage or key points beside the camera. Crop out irrelevant lower-page content, embedded videos, and unnecessary sidebar material instead of shrinking the article to show the whole page. A complaint about clipped content means restore the relevant text, not zoom out to include every part of the page. Match the surrounding canvas to the page color and hold the framing through the passage.
- Keep calendar/timeline visuals static unless motion is requested. For other still graphs or announcements, a subtle push-in of about 2.5% across the clip can be used when appropriate, with all important labels intact. Use an editable native Resolve/Fusion transform with a fixed center. Avoid integer-rounded crop/resize animation that produces jitter. Preserve requested hard-cut boundaries.
- Verify slow zooms in actual rendered motion at timeline frame rate, including text edges and the center of the image. First/middle/last stills and keyframe readback alone cannot prove smoothness. Correct stepping, lateral drift, or repeated-frame stutter before calling the animation finished. Keep animation editable on its own timeline clip.
- Text screenshots get static yellow highlights over the entire passage being discussed. Do not automatically highlight ordinary screen recordings. Preserve explicit exceptions, such as leaving the first excerpt unhighlighted. Highlights must leave original text readable.
- Keep an excerpt displayed while it still contains what the speaker is discussing. Switch only when the next passage requires another image, at the start of a new sentence.
- Logos are substantial and visually balanced, sized by visible artwork rather than canvas padding. Put them beside the speaker without obscuring his face; paired logos use left and right. Trigger each on its spoken name. Use a small pop-in and continuous, subtle wiggle throughout the clip, not just a settling wiggle at the beginning. Hold through the requested endpoint.
- Titles use simple smooth entrances and matching exits. When requested, tie exit motion to the title's end so trimming changes the exit timing. Use a readable sans-serif font available in the project; no specific commercial font is required.

## YouTube export default

Render directly from Resolve to H.264 MP4; keep the timeline frame rate, default 4K resolution, and AAC audio at 256 Kb/s unless the user specifies otherwise. Probe the raw camera and screen video-stream bitrates and choose a source-matched restricted delivery bitrate, accounting for which footage appears in the edit. Do not sum source bitrates or reuse a fixed 18 Mbps default without inspecting the footage.

Prefer direct, reasonably sized MP4 delivery. Do not create a large intermediate master unless requested or required by the chosen workflow. If MCP cannot set the bitrate, use available Resolve controls or a suitable local preset and verify a short MP4 test. If a further encoding pass is needed, disclose it. Verify the final file's actual bitrate, duration, frame rate, and size. Do not rerender or delete prior outputs solely to apply this default.

Where the encoder offers target bitrate control, select the target-bitrate mode rather than assuming a quality-based preset will meet a size target. Commit the value and verify that it persists. Discover available local render presets; no named preset is required or bundled. Adjust resolution, codec, and bitrate to the source and requested delivery. Preserve the chosen encoder settings when updating filename or render range, and verify a short native render before the full export when the configuration is uncertain.

## Verification

### Dialogue timing during visual work

Use the current word-timed transcript mapped to the edited timeline, checked against the processed dialogue waveform, when timing a visual to a spoken word or thought. Read [the shared waveform and word-timing audit](../first-cut-davinci-dialogue/references/waveform-word-timing.md) when making timing changes or reviewing dialogue boundaries. Keep speech intact while adjusting graphics; a visual cue must not motivate trimming a word to fit the animation. Preserve requested cut-aligned entrances and exits unless the user specifies a spoken-word cue or another timing.

Carry forward the first-cut join record and compare dialogue source ranges and boundaries before/after the visual pass. If this pass changes a dialogue edge, processing, or fade, recheck the affected outgoing/incoming words and pause against both waveform and word times, then audition the assembled join. Flag discovered dialogue problems during visual-only work without automatically recutting unrelated manual edits. A full requested dialogue review covers every join; visual screenshots and timeline coverage checks do not establish that words and thoughts are complete.

### Rendered visual verification

Verify with actual rendered timeline frames or playback, not source thumbnails or property readback alone. Check entrances, settled appearance, exits, and clip boundaries; confirm correct track, source asset, readable scale, safe positioning, and no duplicate appearance from old embedded versions. Check that animations span the clip and still work after duration changes. Preserve all unrelated clips and sync. Save after correction and clearly identify the active timeline if a new version was necessary. Never claim listening or a complete watch-through based solely on screenshots, ASR, or metadata.
