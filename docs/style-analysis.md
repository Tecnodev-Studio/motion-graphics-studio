# Analysing a reference video, and house styles

## Method (all free: ffmpeg + python)
1. `ffprobe` size/fps/duration. 2. Cuts: `ffmpeg -i ref.mp4 -vf "scale=288:512,select='gt(scene,0.06)',showinfo" -an -f null -` (few cuts = continuous canvas style). 3. Frame grid: `-vf "fps=1/2,scale=216:384,tile=8x4"`. 4. Fast strips around transitions: `-ss T -t 1.6 -vf "fps=10,scale=180:320,tile=8x2"`. 5. Colours: sample corner (bg), centre (glow), most saturated pixels (accent). 6. Audio: spectrogram + RMS + motion curve; stereo side/mid ratio (hidden SFX); silence ratio (music bed?). 7. Report **transitions, motion language, typography, palette, rhythm (beats per minute), sound** and your confidence; you cannot hear, you measure. Then build; reuse numbers (e.g. entrance 0.3-0.4 s, one beat every 2-3 s).

## Styles that were built and tested
- **Cream & copper explainer** (from a real reference): bg #F1E9DF, glow #F2C3A6, ink #1A1412, accent #D9824B, white cards, one dark scene #171415. Cards slide in from alternating sides; titles with one coloured word; stamps; no music. Example: `examples/compare`.
- **Forest & copper brand**: #0F2A21 / glow #24634C / text #EEF2EA / accent #D9824B.
- **Midnight teal**: #0B1620 / #1A4C61 / #E8F1F2 / #2ED3B7. **Ink violet**: #141018 / #43307A / #F3EEF8 / #9A7BFF.
- **Neon tech** (navy/cyan/orange, lightning + bloom): `examples/data_story`, `examples/kinetic_type`.
- **Whiteboard explainer** (white bg, marker strokes, karaoke captions, 16:9): `examples/whiteboard`.
Show palette options with the robot/title on each background and let the user choose; keep their pick.
