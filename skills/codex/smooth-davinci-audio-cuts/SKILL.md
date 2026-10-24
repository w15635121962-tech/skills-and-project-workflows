---
name: smooth-davinci-audio-cuts
description: Configure and use a two-frame audio crossfade shortcut in DaVinci Resolve after tightly cutting dialogue. Use when the user asks to smooth audio cuts, add very short audio transitions, or configure Shift+D for audio-only crossfades while preserving manual edits.
---

# DaVinci Audio Crossfades

Prefer Resolve MCP for supported inspection and transition operations. Use native Resolve UI controls or a supported computer-use integration only for capabilities the MCP cannot provide. Discover the controls on this machine; do not assume a particular integration is installed. Inspect the active project and current selection before acting. Preserve the user's clip positions, source trims, sync, video edits, music, and effects.

## Configure the shortcut

1. Open DaVinci Resolve > Keyboard Customization. Inspect the active custom preset; preserve its other bindings.
2. Search `transition`. Assign `Shift+D` to **Timeline > Add Audio Only Transition**.
3. Inspect and resolve shortcut conflicts while preserving unrelated bindings. Assigning a command may leave a conflicting binding on another command. Find that command and remove only the conflicting shortcut, then verify the final mapping. Do not assume the same conflict exists on every installation.
4. Save the custom preset and close the dialog.
5. Open **DaVinci Resolve > Preferences > User > Editing > General Settings**. Set **Standard transition duration** to **frames**, value **2**, and Save.

This duration preference is shared with standard video transitions. Explain that consequence when changing it. The audio-only command applies audio transitions only.

## Apply or verify

- For shortcut setup alone, test on one audio edit point, inspect the result, then undo only that test operation.
- For an authorized batch, select the intended dialogue audio edit points and press Shift+D once. Keep music, sound effects, gaps, and unwanted outer clip edges outside the selection. Inspect selection before applying; do not blindly select the entire timeline.
- Verify in the Transition Inspector: **Cross Fade 0 dB**, **Duration: 2 Frames**, centered alignment. Use the frame field as the authority; the seconds field may round to 0.1 at 29.97 fps.
- If another audio transition is the standard, select Cross Fade 0 dB in the Effects library and use its context menu to set it as the standard transition, then retest.
- If handles are insufficient, do not trim or ripple the tight dialogue edit automatically. Leave that boundary unchanged and report it.
- For a batch, enumerate the intended adjacent audio seams and verify every one received a centered Cross Fade 0 dB lasting exactly 2 frames. Use timeline data when available or inspect each transition in the UI; shortcut execution and a few spot checks do not establish full coverage. Exclude actual gaps and unintended outer clip edges. When used by `first-cut-davinci-dialogue`, include the corresponding muted reference-audio seams in a separate batch as needed.
- Preserve the underlying shared cut frame across synced video and audio layers. Centered transition overlap must not create staggered clip boundaries. Recheck alignment after applying transitions, listen across the joins, and save the project. Report any unresolved missing transition with its track and timecode rather than claiming the pass is complete.

## Word and pause check after fades

For an actual dialogue transition pass, use the existing word-timed transcript and join record from `first-cut-davinci-dialogue`, following [the waveform and word-timing audit](../first-cut-davinci-dialogue/references/waveform-word-timing.md). Check every treated join against the assembled processed waveform: the outgoing final phoneme and incoming initial consonant must survive the fade, and the pause between thoughts must remain natural without idle frames at the incoming shot. A complete transition count does not establish complete words or good pacing. A shortcut-configuration test alone does not require auditing the entire edit.

If a word is already missing, a crossfade cannot fix it. Identify the relevant word, source coverage, and timeline timecode; repair the boundary only within the authorized dialogue-edit scope and preserve synced layers. Do not lengthen or shift the user's manual edit just to obtain transition handles. If listening is unavailable, distinguish signal/transcript checks from auditory verification in the result.

## UI checks

After a shortcut test, inspect the transition to confirm the type, centered alignment, and exact two-frame duration with no video transition. Undo only the test transition while retaining the intended shortcut and preference changes. Do not infer correct behavior from a keystroke alone.

Resolve dialogs may appear as separate windows or as additional screenshots attached to the main window. Discover their current handles and use coordinates relative to the specific screenshot; never reuse stale dialog handles.
