---
name: clean-davinci-dialogue
description: Build or reuse an editable Fairlight voice chain in DaVinci Resolve, reduce dialogue noise, and level speech while preserving sync. Use for audio presets, background fuzz or buzz, noisy pauses, or repeatable voice preparation during short setup.
---

# DaVinci Dialogue Cleanup

The user expects quiet pauses as well as suitable speech loudness. Loudness normalization alone is not completion: it can expose room noise. Use this stage when preparing dialogue for the editing workflow.

Build and calibrate an editable native Fairlight chain on original media, then follow the pre-cut rendering workflow below. Read [native-fairlight-chain.md](references/native-fairlight-chain.md) for adjustable starting settings and local preset creation. Avoid rebuilding an already verified chain or duplicating processing on continuation.

## Pre-cut audio workflow

For new dialogue edits, complete dialogue cleanup **before the first editorial cut**, then render the processed dialogue back out and use that rendered audio in the working timeline for smooth playback. This is the skill's default workflow, even when live effects work correctly; a QC-only render does not satisfy it.

Preserve a recoverable preparation timeline with the original audio and editable Fairlight chain. Render full continuous dialogue coverage before cutting, including the source coverage needed for later trims, as a project-local 48 kHz, 24-bit PCM WAV with a descriptive versioned filename. Preserve channel layout, duration, and established sync, including any section-specific offsets caused by OBS pauses. Verify actual rendered duration, levels, and alignment before placing it in the working timeline. Keep the rendered audio as ordinary trimmable clips linked to the corresponding picture; retain access to the original recording and live chain for revisions.

Bypass the effects and gain already baked into that rendered audio in the working timeline so it is not processed twice. Verify smooth playback, then begin the dialogue cut and add the usual two-frame audio crossfades afterward. Preserve any existing manual edits when joining a project already in progress; do not undo or rebuild an existing cut solely to impose this order retroactively. An explicit request to keep effects live overrides this default.

## Preserve speech for the word-timed cut

Prepare or reuse a word-timed transcript aligned to the original dialogue and compare its word spans with both the original and processed waveforms. Follow [the shared waveform and word-timing audit](../first-cut-davinci-dialogue/references/waveform-word-timing.md). During cleanup, check quiet word onsets, endings, and speech-to-pause transitions across the recording; investigate any processing that gates or suppresses a phoneme. A quieter pause is not an improvement if part of a word disappears. Preserve meaningful pauses and continuous source coverage rather than deleting time in this stage.

Verify the processed WAV's timing against the original signal, account for filter latency, and retain the transcript-to-source mapping with the audio preparation record. Hand this evidence to the first-cut stage, which must check every proposed join against the waveform and word times, then recheck the assembled result. Cleanup measurements alone do not establish safe cut points.

## Reusable settings

No private preset or source project is required. Read [native-fairlight-chain.md](references/native-fairlight-chain.md) to build and save a local voice chain. Measure and recalibrate for each voice and recording rather than assuming a saved gain is appropriate.

## Procedure

1. Inspect the current timeline, source path, source ranges, existing processing, and signed audio offset. Keep original media and a recoverable timeline version. Never process an already processed derivative again by accident.
2. Measure integrated loudness, true peak, and actual quiet passages. Inspect quiet speech and word endings too. Prefer noise reduction before gain/compression; use a gentle downward expander for residual noise in pauses. Do not remove timeline time or ripple-delete silence.
3. Prefer a verified native chain or saved Fairlight preset. Native and Adobe algorithms differ. If native control is unavailable or fails measured checks, a separate project-local PCM WAV is acceptable; preserve the original and record the processing recipe. Disable redundant processing on the replacement.
4. Use roughly -16 LUFS and true peak below -1.5 dBTP as the initial voice-only working target, with encoding headroom. Check the actual result; do not infer it from gain arithmetic. Loudness range across unedited takes and pauses is not by itself proof of poor speech dynamics.
5. Derive expander thresholds from this recording, not a universal preset. Keep attack short and release gradual; check consonants, breaths, and tails for truncation or pumping. Measure noise reduction in the SAME quiet time windows before/after. Audition those windows and speech transitions, or give the user a short comparison when listening tools are unavailable. Numeric silence alone does not establish natural sound.
6. Preserve sample duration and alignment. Replacing audio must preserve the current source coverage and any verified existing sync offset. Measure offsets for the current recording; do not introduce a fixed delay without evidence. Compensate any filter latency. Relink video/audio and verify their positions.
7. Render a timeline QC pass and remeasure loudness/true peak, since bus gain, plugins, or encoding may change them. Restore delivery dimensions after a low-resolution QC render. Save the project, a new backup revision, and the recipe/measurements beside the project.

## Processing and latency checks

When using an external audio processor, document its high-pass, noise reduction, expander, and limiter settings. Calibrate reduction strength, noise floor, and expander threshold against the current recording. Use peak protection after noise processing because filtering can create new peaks.

Measure processing latency with waveform alignment or correlation. If compensation is needed, shift by the measured sample count and preserve the total sample duration with appropriate tail padding. Equal file durations do not prove aligned content. Check actual tool capabilities and rendered results rather than relying on success flags or historical API behavior.
