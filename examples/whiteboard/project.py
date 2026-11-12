"""Whiteboard explainer (16:9 YouTube, English/LTR): marker strokes draw themselves, word-synced captions."""
import os
from mgs.engine import Project
from mgs import kit as K, components as C
HERE = os.path.dirname(os.path.abspath(__file__))
BG, INK, BLUE, RED = (250, 250, 246), (30, 30, 36), (40, 110, 220), (220, 70, 60)
project = Project('youtube', timing=os.path.join(HERE, 'timing.json'), rtl=False,
                  theme=dict(bg=BG, glow=(255, 255, 255), dark_bg=(30, 30, 36), dark_glow=(60, 60, 70), ink=INK, accent=BLUE, card=(255, 255, 255)))
P = project.P; W, H = project.W, project.H

def chip_drawing(cv, t, t0, cx, cy, s=1.0):
    pts = [(cx - 160 * s, cy - 90 * s), (cx + 160 * s, cy - 90 * s), (cx + 160 * s, cy + 90 * s), (cx - 160 * s, cy + 90 * s), (cx - 160 * s, cy - 90 * s)]
    C.stroke_draw(cv, pts, t, t0, 1.2, INK, 8, wobble=1.2)
    for k in range(5):
        x = cx - 120 * s + k * 60 * s
        C.stroke_draw(cv, [(x, cy - 90 * s), (x, cy - 140 * s)], t, t0 + 1.0 + k * .1, .3, INK, 8); C.stroke_draw(cv, [(x, cy + 90 * s), (x, cy + 140 * s)], t, t0 + 1.0 + k * .1, .3, INK, 8)

@project.scene(0.0)
def notebook(cv, t):
    K.title(cv, [("Memory is a very fast", INK), ("notebook", BLUE)], 80, 130, t, .2)
    chip_drawing(cv, t, P(1) + .2, W * .5, H * .55)

@project.scene(project.boundary(2), transition='slide')
def loop(cv, t):
    K.title(cv, [("Read it", INK), ("again and again", RED)], 80, 130, t, project.boundary(2) + .15)
    C.stroke_draw(cv, [(W * .3, H * .6), (W * .5, H * .4), (W * .7, H * .6), (W * .5, H * .78), (W * .3, H * .6)], t, P(2) + .3, 1.6, BLUE, 10, wobble=1.5)
    C.progress_ring(cv, W * .5, H * .6, 90, K.eo3((t - P(2) - .5) / 1.8), BLUE, (225, 225, 220))

@project.scene(project.boundary(3), transition='wipe', tparams=dict(edge=BLUE))
def fewer(cv, t):
    K.title(cv, [("More memory,", INK), ("fewer slow trips", BLUE)], 80, 130, t, project.boundary(3) + .15)
    C.bar_chart(cv, [("Small", 9), ("Medium", 5), ("Large", 2)], t, P(3) + .3, (W / 2, H * .55, 900, 460), INK, (225, 225, 220), [RED, BLUE, BLUE], size=34, rtl=False)

project.set_captions('karaoke', pill=(30, 30, 36), ink=(255, 255, 255), accent=(255, 205, 60), size=42, y=.88)
for t0, n, g in ((P(1) + .2, 'tick', .25), (P(2) + .3, 'swipe', .25), (P(3) + .3, 'pop', .3), (P(4), 'ding', .3)): project.sfx(t0, n, g)
