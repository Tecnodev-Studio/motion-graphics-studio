# Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Arabic letters disconnected or reversed | PIL without raqm. `pip install --upgrade Pillow` (wheels include it) or install libraqm. `python -m mgs doctor` shows `raqm: True` when fine. |
| `No TrueType font found` | `MGS_FONT=/path/to/NotoSansArabic-Bold.ttf` (free, SIL OFL). Windows/macOS fonts are auto-detected. |
| `ffmpeg: MISSING` | install FFmpeg (free) and restart the terminal. |
| Render dies when the terminal/tool call ends | use `render --detach`; re-run the same command to resume (finished chunks are kept in `mgs_chunks/`). |
| Very slow | add `--workers N`, use `MGS_DURATION=5` to preview, avoid huge `fx.bloom` radius, fewer full-frame effects. |
| Captions/animations drift from the voice | build from absolute `P(k)` times; re-run `align`; for exact words give `--words`. `check` shows length mismatches. |
| `only N speech segments for M phrases` | merge short phrases or `align ... --gap 0.12`; noisy audio: `--noise -28`. |
| Text clipped at the edges | use `K.txtf` / `K.title` (auto-fit) and check with `stills`. |
| Output huge | `mux` re-encodes at crf 23; raise to 26-28. |
| Windows: workers hang | run via `python -m mgs ...` (spawn mode needs the CLI entry point); use `--workers 1` to debug. |
| Frame error lines in the log | a scene raised an exception; the previous frame is repeated. Fix the scene (try `stills` at that time). |
