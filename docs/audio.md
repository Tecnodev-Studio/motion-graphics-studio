# Audio

- **Voice-over is yours**: record it, or use any text-to-speech you have the rights to. The toolkit never calls an online service. Convert to mono wav (`ffmpeg -i in.mp3 -ar 44100 -ac 1 voice.wav`).
- **SFX are synthesized** (`mgs.audio.SFX`: whoosh, whoosh_s, swipe, pop, tick, ding, thud, impact, clunk, buzz, zap, riser, notif, sparkle). Place with `project.sfx(t, 'pop', gain)`; they are shifted 0.08 s early so they land with the visual. Auto whooshes are added at scene changes (`project.auto_sfx = False` to disable).
- **House mix**: voice x1.5, SFX x0.30 (gains per event 0.15-0.45), no music unless asked. Verdict X = low thud, check = ding, steps = tick, card slide = soft whoosh, CTA = chime.
- **Music** (optional): `Project(music='bed.mp3')` loops, fades in/out and is **ducked under the voice** automatically (`audio.mix(duck=0.65, music_gain=0.18)`). Use music you own or CC0/public-domain/royalty-free-for-commercial (read the licence; keep proof). Cut to the beat: `audio.detect_beats('bed.mp3')` -> list of times.
- **Loudness**: `python -m mgs all project.py --loudnorm` (about -14 LUFS, good for Shorts/Reels/YouTube). Peak is limited to -0.7 dB.
- **Audio-reactive visuals**: overlay signature `fn(cv, t, i, env)`; `env` is the voice loudness 0..1 (the robot's mouth uses it).
- **Sync checks**: `check` warns when audio and video lengths differ by > 0.12 s.
