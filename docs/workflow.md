# Workflow in detail

## Anatomy of `project.py`
```python
from mgs.engine import Project
from mgs import kit as K, components as C, fx
from mgs.mascot import Presenter            # optional character

project = Project('shorts', timing='timing.json', voice='voice.wav',   # voice optional: SFX-only video works too
                  theme=dict(bg=(241,233,223), glow=(242,195,166), ink=(26,20,18), accent=(217,130,75)), rtl=True)
P = project.P                                # P(k) = start time of phrase k (1-based), project.PE(k) = end, project.boundary(k) = midpoint of the pause before phrase k

@project.scene(0.0)                          # draw with time t (seconds). Use K.pop/K.eo3 for motion, never linear.
def intro(cv, t):
    K.title(cv, [("Hello", (26,20,18)), ("world", (217,130,75))], 90, 270, t, 0.2)

@project.scene(project.boundary(3), bg='dark', transition='wipe')      # scene start = a pause between phrases
def second(cv, t): ...

project.overlay(Presenter(keys=[...], moves=[...], outline=(26,20,18)))  # drawn above every scene
project.add_post(fx.Vignette(.35)); project.set_captions('karaoke')
project.sfx(P(2), 'pop', .3)
```
Scene backgrounds: `'light'` (theme bg+glow), `'dark'`, an RGB tuple, an image array, or a callable returning one.
Footage: `clip = K.VideoLayer('b-roll.mp4')` at module level; in a scene `clip.fill(cv, t)` (background) or `clip.draw(cv, t, cx, cy, w, h)` (window).

## Voice and timing
1. Make phrases: split the script at commas/periods; 1-6 s each. One per line in `phrases.txt`.
2. `ffmpeg -i voice.mp3 -ar 44100 -ac 1 voice.wav`
3. `python -m mgs align voice.wav phrases.txt timing.json`. Prints each phrase with its start/end. Check a few by ear; edit `timing.json` by hand to nudge.
4. **Exact timing (optional, any free recogniser).** Produce `words.json` = `[{"word","start","end"}, ...]` and run `python -m mgs align voice.wav phrases.txt timing.json --words words.json`. Example with the free faster-whisper package (not tested in this repo's CI; needs a one-time model download):
```python
from faster_whisper import WhisperModel
segs, _ = WhisperModel("small").transcribe("voice.wav", word_timestamps=True, language="ar")
import json; json.dump([{"word": w.word.strip(), "start": w.start, "end": w.end} for s in segs for w in s.words], open("words.json", "w"), ensure_ascii=False)
```
If the recogniser's spelling differs from your script, timing still maps by word count; a count mismatch falls back to proportional spreading.
**Sync drift tip:** build every animation from absolute times `P(k)`, never from "previous scene + N seconds", and let `check` compare audio/video lengths.

## Preview -> render
- `python -m mgs stills project.py 1 4 8 12` -> `sheet.png`. Look at it.
- `MGS_DURATION=5 python -m mgs all project.py` -> first 5 seconds fully rendered.
- `python -m mgs all project.py --workers 4 [--loudnorm] [--out final.mp4]`. `--loudnorm` normalises to about -14 LUFS (FFmpeg filter).
- Speed: roughly 0.2-0.5 s per 1080x1920 frame per core -> a 60 s video is 10-15 min on one core, ~3 min on 4. Chunks are saved in `mgs_chunks/`; re-run to resume.
- Other sizes: change `Project(size=...)` (`'youtube'`, `'square'`, or `(w, h)`). Positions in your scenes should use `W, H` fractions so they adapt.

## Output
`out.mp4` (H.264 + AAC), `captions.srt/.vtt` (`python -m mgs captions project.py`), `check_sheet.png`.
