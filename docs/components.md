# Components and helpers (API)

All draw onto `cv` (RGB uint8) from the time `t`. Times are seconds. Colours are RGB tuples.

| Call | What it does |
|---|---|
| `K.title(cv, [(text, colour), ...], size, y, t, t0, rtl=None)` | title from coloured parts in reading order; auto-shrinks to fit |
| `K.slide_card(cv, cx, cy, w, h, t, t0, side=+1/-1)` | white card sliding in from a side; returns `(x, alpha)` to place content inside |
| `K.stamp(cv, cx, cy, t, t0, ok, colour)` | check / cross badge that pops |
| `K.txt / K.txtf / K.chip / K.cardspr / K.rrect` | cached text, auto-fit text, pill, card with shadow, rounded rectangle sprites (use with `K.blit`) |
| `K.blit(cv, sprite, cx, cy, alpha, scale)` | alpha-blend any RGBA sprite |
| `K.pop(t, t0, d)` -> `(scale, alpha)`; `K.eo3/eio/eob/smooth/spring` | easing (decelerate / in-out / overshoot / smooth / spring) |
| `K.image_sprite(path, w, h, radius)`, `K.ken_burns(...)` | your photos/logos with rounded corners; slow zoom |
| `K.VideoLayer(path)` `.fill/.draw` | existing video as background or window |
| `K.check/cross/arrow_down/warn/search_icon/meter/ring/line/circle/poly` | small vector icons & shapes |
| `K.contrast(a, b)`, `K.safe_area()`, `K.mix` | accessibility and layout helpers |
| `C.counter(...)` | rolling number |
| `C.bar_chart(...)`, `C.line_chart(...)` | animated charts (vertical/horizontal bars, drawn line) |
| `C.kinetic_text(cv, words, t, t0, cx, cy, size, colour, accent={i})` | words pop in one by one, wrapped & centred |
| `C.lower_third(...)`, `C.logo_reveal(...)`, `C.progress_ring(...)` | broadcast bits |
| `C.stroke_draw(cv, points, t, t0, d, colour, th, wobble)` | marker/whiteboard drawing |
| `C.confetti`, `C.speed_lines`, `C.lightning` | celebration, impact, neon bolt (pair with `fx.bloom`) |
| `fx.Grain/Vignette` (objects), `fx.bloom/shake/punch_zoom/grade/chroma_split/flash` | post effects: use `project.add_post(lambda cv,t,i: fx.shake(cv,t,3.2))` |
| `transitions.TRANSITIONS` | crossfade, dip, slide(_left/_right), wipe, zoom, glitch, iris, cut; pick per scene: `@project.scene(t, transition='wipe', tparams=dict(edge=(r,g,b)))` |
| `captions.draw_phrase / draw_karaoke / write_srt / write_vtt` | on-screen and exported captions; `project.set_captions('phrase'|'karaoke', fix=fn)` where `fix(text)` applies wording rules |
| `mgs.mascot.Presenter` | robot overlay: `keys=[(t, emotion, gesture, target)]`, `moves=[(t0, t1, x, y, scale)]`; gesture `'aim'` points at `target=(x, y)`; lips follow the voice |

Write your own component as a function `def my_thing(cv, ..., t, t0)` - pure drawing from `t`, no state.
Design rules: persistent canvas, one coloured word in titles, alternate card sides, quick (0.3 s) motions when pauses are short, content inside `K.safe_area()`, contrast >= 4.5:1.
