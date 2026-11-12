# What this does NOT do (so nobody is surprised)

- It does **not generate video with AI** (no text-to-video, no image generation) and needs no AI service.
- It does **not re-animate or "fix" existing footage/anime**: it cannot repair character motion, foot sliding, timing or drawing quality in a clip. It can *present* footage better: cut and re-time it (with FFmpeg), grade it, add bloom/grain/vignette, shake and flash on hits, speed lines, titles, captions, sound design, transitions, picture-in-picture (`K.VideoLayer`). Frame interpolation and AI upscaling are not included (they need models; plain FFmpeg interpolation often damages anime).
- Not a 3D engine or photoreal renderer; it is 2D motion graphics.
- Voice synthesis and speech recognition are not bundled (bring your own audio; optional free recogniser for exact word timing).
- Timing from `align` is an **estimate** unless you provide word timings.
- Copyright: you are responsible for the footage, photos, logos, fonts and music you add.
