---
name: motion-graphics-studio
description: Build finished motion-graphics videos (YouTube Shorts, Reels, TikTok, 16:9 explainers) with code, for free and offline - script and hook, voice-over timing, animated scenes (titles, cards, charts, counters, kinetic typography, whiteboard drawing, lower thirds, logo reveals), transitions, effects, synthesized sound effects, word-synced captions, optional robot presenter, render and self-check. Use whenever the user asks to make, edit, fix the timing of, restyle, or analyse the style of a motion-graphics / explainer / promo / Shorts video, asks for a video idea or script, a colour palette, subtitles/SRT, or wants a video built from a voice-over file. Works with any AI agent that can run shell commands.
---

# Motion Graphics Studio - agent workflow

Toolkit: `python -m mgs <command>` (repo root). Free + offline: Python (numpy, scipy, opencv, Pillow) and FFmpeg. Read the linked doc only when you reach that step.

## 0. Setup (once)
`pip install -r requirements.txt`, install FFmpeg, then `python -m mgs doctor` (must show raqm = True for Arabic/RTL). If a font is missing set `MGS_FONT=/path/to/font.ttf` (any free font, e.g. Noto/Cairo, SIL OFL).

## 1. Understand the request
Ask at most one question, only if it blocks the work. Capture: topic, platform/size (`shorts`, `youtube`, `square`), language + dialect, voice-over available?, palette/style, mascot wanted?, any reference video. If the user gives a reference video, analyse it **before** building (method: `docs/style-analysis.md`) and report transitions / motion / sound / palette, with honest confidence (you cannot hear audio; you measure it).
If `profiles/` has a file for this user/channel, follow it (language rules, brand colours, recurring CTA).

## 2. Idea and script  (`docs/script-craft.md`)
- Offer 3-4 ideas, recommend one with an honest reason, flag repeated/overdone topics and what you could not verify. Search the web for facts if you can; never invent examples, numbers or "I tried it" claims. Mark illustrative visuals "illustrative".
- Script = short phrases (one idea per comma/period), hook in the first 3 s, one honest limitation, a CTA. Platform length limits in the doc. Deliver the script alone if asked.
- Voice: the user supplies the audio (their own recording or any TTS they have rights to). Never depend on a paid service.

## 3. Timing
Write phrases one per line -> `python -m mgs align voice.mp3 phrases.txt timing.json [--words words.json]`.
Default is an **estimate** (silence + length matching): say so and offer to nudge it. Exact timing: pass word timings from any free recogniser (`docs/workflow.md`). Convert voice to wav for the project: `ffmpeg -i voice.mp3 -ar 44100 -ac 1 voice.wav`.

## 4. Build
`python -m mgs init <dir> --template compare|data_story|kinetic_type|whiteboard`, then edit `project.py`: theme, scenes (`@project.scene(start)`), overlays (`Presenter` mascot, HUD), captions (`set_captions('karaoke'|'phrase')`), post-fx, `project.sfx(t, name)`. Components and rules: `docs/components.md`. Design rules that worked: persistent canvas; title with ONE coloured word; cards sliding in from alternating sides, decelerating; verdict stamps; one dark scene for emphasis; sounds land ~3 frames before the visual; keep key content inside `K.safe_area()`; text contrast >= 4.5:1 (`check` warns).

## 5. Look before rendering (mandatory)
`python -m mgs stills project.py t1 t2 ...` -> view `sheet.png`; cover every scene. Fix overlaps/clipping/low contrast. Quick preview: `MGS_DURATION=5 python -m mgs all project.py`.

## 6. Render and verify
`python -m mgs all project.py --workers N` (or `render --detach` for long jobs; resume by re-running). It writes `out.mp4` and runs `check` (length/sync, streams, contrast, raqm, size, contact sheet `check_sheet.png`) - view the sheet, fix every warning. `python -m mgs captions project.py` writes `captions.srt/.vtt`. Self-review against `docs/review-checklist.md`.

## 7. Deliver
Give the user the mp4 (+ srt/vtt). Short summary of what is in it, then "honest notes": what is estimated, illustrative, unverified or not possible (`docs/limits.md`). Offer specific edits ("scene 3 timing, a different palette"). Publishing help: `docs/publishing.md`.

## Rules
Free-only and offline. Be honest about uncertainty. Don't redo a 15-minute render to fix something stills would have shown. Don't use brand logos/photos/music you can't license. Never run project files you didn't write or inspect.
