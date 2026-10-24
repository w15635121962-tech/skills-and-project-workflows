# Local music runtime

This is a local installation addition. The upstream music-planning instructions and Mureka helper retain their recorded provenance in `upstream-source.json`.

## Available commands and interpreter

- `opencli`: installed under `/Users/xuan/.local/bin`; check `opencli doctor` before website work.
- `ffmpeg` and `ffprobe`: installed under `/Users/xuan/.local/bin`.
- Music-analysis interpreter: `/Users/xuan/.local/share/promo-audio/venv/bin/python`.
- Resolve connection helper: `/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts/resolve_bootstrap.py`.

## Source existing music and measure it

Use `pixabay-music-download` with the installed `opencli-browser` skill to obtain candidate recordings and retain track-page URLs, artist, license link and any Content ID indicator. Inspect the actual recording against the picture; search titles alone are not enough to choose it.

Run the local measurement helper with the interpreter above:

```sh
/Users/xuan/.local/share/promo-audio/venv/bin/python /Users/xuan/Codex_YS_Data/CodexHome/skills/promo-music-maker/scripts/analyze_music.py /absolute/path/music.mp3 --output /absolute/path/music-analysis.json
```

The helper outputs estimated tempo, beat timestamps and one-second RMS levels. It does not infer emotion, downbeats or phrase endings. Check estimates against listening and the video's emotional structure. Do not force every picture cut onto a beat. For music-only requests, preserve the user's picture cut, dialogue and total duration.

Use `davinci-resolve` to place selected music on separate, editable audio tracks, preserving original media and existing edits. Reinspect the current project and API capabilities before applying volume, fades or render settings. Verify the resulting timing and mix; a successful connection is not a finished scoring test.

## Optional generated music

The upstream `scripts/mureka.py` needs `MUREKA_API_KEY`; the local interpreter includes `requests`. No key is bundled. Do not print credentials. A successful `--help` check does not establish account authorization or prove that generation works. Generate only when requested.
