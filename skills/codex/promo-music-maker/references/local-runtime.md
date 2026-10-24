# Local music runtime

This is a local installation addition. The upstream music-planning instructions and Mureka helper retain their recorded provenance in `upstream-source.json`.

## Local migration status (2026-10-19)

- `opencli`, `ffmpeg` and `ffprobe` are not currently on this machine's PATH. Check or install the needed runtime before using a workflow that requires it.
- The source machine's music-analysis virtual environment was not included in the export. Select or prepare a local Python environment with `librosa`, `numpy` and, for Mureka, `requests`; do not assume those packages are installed.
- Resolve connection helper: `/Users/zc/.codex/skills/davinci-resolve/scripts/resolve_bootstrap.py`.
- Music-analysis helper: `/Users/zc/.codex/skills/promo-music-maker/scripts/analyze_music.py`.

## Source existing music and measure it

Use `pixabay-music-download` with the installed `opencli-browser` skill to obtain candidate recordings and retain track-page URLs, artist, license link and any Content ID indicator. Inspect the actual recording against the picture; search titles alone are not enough to choose it.

After verifying `ffmpeg` and the analysis packages, run the measurement helper with the prepared interpreter. For example, if that interpreter is `python3`:

```sh
python3 /Users/zc/.codex/skills/promo-music-maker/scripts/analyze_music.py /absolute/path/music.mp3 --output /absolute/path/music-analysis.json
```

The helper outputs estimated tempo, beat timestamps and one-second RMS levels. It does not infer emotion, downbeats or phrase endings. Check estimates against listening and the video's emotional structure. Do not force every picture cut onto a beat. For music-only requests, preserve the user's picture cut, dialogue and total duration.

Use `davinci-resolve` to place selected music on separate, editable audio tracks, preserving original media and existing edits. Reinspect the current project and API capabilities before applying volume, fades or render settings. Verify the resulting timing and mix; a successful connection is not a finished scoring test.

## Optional generated music

The upstream `scripts/mureka.py` needs `MUREKA_API_KEY` and `requests`; neither is established by importing this skill. No key is bundled. Do not print credentials. A successful `--help` check does not establish account authorization or prove that generation works. Generate only when requested.
