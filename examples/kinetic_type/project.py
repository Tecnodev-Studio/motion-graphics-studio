"""Kinetic typography hook (9:16, English/LTR, neon: speed lines, camera shake, flash, logo reveal)."""
import os
from mgs.engine import Project
from mgs import kit as K, components as C, fx
HERE = os.path.dirname(os.path.abspath(__file__))
BG, PINK, CY, INK = (14, 10, 28), (255, 60, 150), (0, 230, 255), (250, 248, 255)
project = Project('shorts', timing=os.path.join(HERE, 'timing.json'), rtl=False,
                  theme=dict(bg=BG, glow=(60, 20, 90), dark_bg=(6, 4, 14), dark_glow=(0, 50, 70), ink=INK, accent=PINK))
P = project.P; W, H = project.W, project.H

@project.scene(0.0)
def hook(cv, t):
    C.kinetic_text(cv, "Stop scrolling".split(), t, .2, W / 2, H * .38, 150, INK, stagger=.25, accent={1}, accent_color=PINK, rtl=False)
    C.speed_lines(cv, t, P(1) + .5, .5, PINK)

@project.scene(project.boundary(2), transition='glitch')
def change(cv, t):
    C.kinetic_text(cv, "This changes everything".split(), t, P(2), W / 2, H * .4, 130, INK, stagger=.2, accent={2}, accent_color=CY, rtl=False)
    C.lightning(cv, (100, H * .15), (W - 100, H * .62), t, P(2) + .9, .5, CY)

@project.scene(project.boundary(3), bg='dark', transition='iris')
def three(cv, t):
    C.counter(cv, 0, 3, t, P(3), 1.0, W / 2, H * .35, 420, PINK, fmt='{:.0f}')
    K.blit(cv, K.txt("seconds", 90, INK, False), W / 2, H * .5, K.pop(t, P(3) + 1.0, .4)[1])

@project.scene(project.boundary(4), transition='wipe', tparams=dict(edge=PINK))
def finale(cv, t):
    C.logo_reveal(cv, "YOUR BRAND", t, P(4), W / 2, H * .42, 120, INK, PINK)
    C.confetti(cv, t, P(4) + 1.0, [PINK, CY, INK], seed=9)

project.add_post(lambda cv, t, i: fx.shake(cv, t, P(2) + .9, 16))
project.add_post(lambda cv, t, i: fx.flash(cv, t, P(2) + .9, .2, (255, 255, 255)))
project.add_post(lambda cv, t, i: fx.bloom(cv, 180, 28, .4))
project.add_post(fx.Grain(3.5))
project.set_captions('phrase', pill=(6, 4, 14), ink=INK, size=50)
for t0, n, g in ((P(1) + .5, 'impact', .4), (P(2) + .9, 'zap', .4), (P(3), 'riser', .3), (P(4), 'sparkle', .35)): project.sfx(t0, n, g)
