"""Data story (16:9 YouTube, English/LTR, navy + cyan, animated counter + charts + lower third + word-synced captions + bloom)."""
import os
from mgs.engine import Project
from mgs import kit as K, components as C, fx
HERE = os.path.dirname(os.path.abspath(__file__))
NAVY, CY, OR, INK = (10, 22, 40), (0, 214, 255), (255, 150, 60), (235, 245, 255)
project = Project('youtube', timing=os.path.join(HERE, 'timing.json'), rtl=False,
                  theme=dict(bg=NAVY, glow=(20, 70, 100), dark_bg=(5, 10, 20), dark_glow=(0, 60, 80), ink=INK, accent=CY, card=(20, 40, 68), muted=(120, 150, 180), soft=(30, 55, 88)))
P = project.P; W, H = project.W, project.H

@project.scene(0.0)
def growth(cv, t):
    K.title(cv, [("Our users", INK), ("grew", CY), ("every month", INK)], 84, 150, t, .2)
    C.counter(cv, 2000, 42000, t, P(2), 2.0, W * .28, H * .5, 170, CY)
    C.bar_chart(cv, [("Jan", 2), ("Mar", 6), ("May", 15), ("Jul", 28), ("Sep", 42)], t, P(2) + .4, (W * .68, H * .52, 760, 520), INK, (30, 55, 88), [CY, CY, CY, CY, OR], size=30, rtl=False)
    C.lower_third(cv, "Growth report", "Monthly active users", t, .6, 3.5, W * .2, H * .7, (20, 40, 68), INK, CY, rtl=False)

@project.scene(project.boundary(3), bg='dark', transition='zoom')
def revenue(cv, t):
    K.title(cv, [("Revenue", CY), ("followed the curve", INK)], 84, 150, t, project.boundary(3) + .15)
    C.line_chart(cv, [3, 4, 6, 9, 15, 22, 34, 46], t, P(3) + .2, 2.0, (W / 2, H * .55, 1100, 460), CY, (120, 150, 180), th=10)
    C.lightning(cv, (W * .15, H * .2), (W * .3, H * .5), t, P(3) + 1.5, .4, CY)

@project.scene(project.boundary(4), transition='wipe', tparams=dict(edge=OR))
def end(cv, t):
    C.kinetic_text(cv, "Here is what we learned".split(), t, P(4), W / 2, H * .42, 96, INK, accent={4}, accent_color=CY, rtl=False)
    C.confetti(cv, t, P(5), [CY, OR, INK], seed=4)

project.add_post(lambda cv, t, i: fx.bloom(cv, 170, 30, .35))
project.add_post(fx.Vignette(.35))
project.set_captions('karaoke', pill=(5, 10, 20), ink=INK, accent=CY, size=44, y=.9)
for t0, n, g in ((P(2), 'riser', .25), (P(3) + 1.5, 'zap', .35), (P(5), 'sparkle', .3)): project.sfx(t0, n, g)
