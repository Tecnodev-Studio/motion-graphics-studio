# Motion Graphics Studio (mgs)

**English** · [العربية](README.ar.md)

Build motion-graphics videos (YouTube Shorts / Reels / TikTok / 16:9 explainers) **with code**, for free, offline, and with any AI assistant that can run shell commands.

No subscriptions, no API keys, no cloud render, no paid assets. Everything is Python + FFmpeg.

## What you get
- **Scenes as code** - titles, cards that slide in, stamps, counters, bar/line charts, kinetic typography, lower thirds, logo reveals, whiteboard stroke drawing, confetti, speed lines, lightning, progress rings.
- **9 transitions** (crossfade, dip, slide, wipe, zoom, glitch, iris, cut) and **post-fx** (grain, vignette, bloom, camera shake, punch zoom, grade, flash).
- **Captions** - whole-phrase pills or **word-synced karaoke**, plus **SRT/VTT export** for platform upload. Arabic/RTL and any LTR language.
- **Timing from your voice-over** - finds when each script phrase is spoken (estimated offline, or exact if you give word timings).
- **Sound design without samples** - synthesized whooshes, pops, dings, impacts; voice + optional music with automatic ducking; beat detection.
- **Optional character** - a drawn robot presenter that lip-syncs, emotes, points at things and walks between spots.
- **Fast & safe renders** - parallel chunks, resumable, one command to render, mux, and self-check.
- **Canvas presets** - `shorts` 1080x1920, `youtube` 1920x1080, `square`, `portrait45`.

## Install (3 commands)
```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate  (recommended; some systems block global pip installs)
pip install -r requirements.txt        # numpy, scipy, opencv-python-headless, Pillow
# install FFmpeg (free): apt install ffmpeg | brew install ffmpeg | winget install ffmpeg
python -m mgs doctor                    # checks ffmpeg, libraries, Arabic shaping (raqm), font
# optional: `pip install -e .` gives a short `mgs ...` command and lets you run it from any folder
```

## 60-second tour
```bash
python -m mgs init my-video --template compare      # templates: compare, data_story, kinetic_type, whiteboard
cd my-video
python -m mgs stills project.py 1 3 5 7 9           # contact sheet -> sheet.png  (always look before rendering)
MGS_DURATION=5 python -m mgs all project.py         # quick 5 s preview: audio + render + mux + checks
python -m mgs all project.py --workers 4            # the full video -> out.mp4
```
With your own voice-over:
```bash
python -m mgs align voice.mp3 phrases.txt timing.json     # one phrase per line in phrases.txt
# then in project.py:  Project('shorts', timing='timing.json', voice='voice.wav')
```
Long renders: `python -m mgs render project.py --detach` runs in the background (`tail -f render.log`); run it again to resume.

## Using it with an AI assistant
Point the assistant at `SKILL.md` (Agent-Skills format; works as a Claude skill) or `AGENTS.md` (Codex, Cursor, Gemini CLI, Aider, local models...). It carries the full workflow: idea -> script -> voice -> timing -> scenes -> look at stills -> render -> verify. See `docs/agents.md`.

## Honest limits
It draws motion graphics; it does **not** generate AI video, re-animate anime/footage, interpolate frames or upscale. See `docs/limits.md`. Estimated timing can be off by a word; the tool says so and lets you nudge it.

## Docs
`docs/workflow.md` · `components.md` · `audio.md` · `style-analysis.md` · `script-craft.md` · `review-checklist.md` · `publishing.md` · `troubleshooting.md` · `limits.md` · `agents.md`

## Licence
Apache License 2.0 (see `LICENSE` and `NOTICE`). Third-party notes in `THIRD_PARTY.md`. Only run `project.py` files you trust (they are Python code).
