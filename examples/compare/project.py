"""Comparison explainer (9:16, Arabic/RTL, cream & copper, robot presenter that points at each side)."""
import os, math
from mgs.engine import Project
from mgs import kit as K
from mgs.mascot import Presenter
HERE = os.path.dirname(os.path.abspath(__file__))
project = Project('shorts', timing=os.path.join(HERE, 'timing.json'))     # add voice='voice.wav' for lip-sync + real audio
th = project.theme; INK, ACC, WHITE = th['ink'], th['accent'], th['card']
P = project.P

@project.scene(0.0)
def intro(cv, t):
    K.title(cv, [("لابتوب عادي", INK), ("ولا", ACC), ("جهاز قوي؟", INK)], 84, 270, t, 0.2)
    for x, side, nm, t0 in ((770, 1, "لابتوب عادي", P(1) + .3), (310, -1, "جهاز قوي", P(1) + .7)):
        r = K.slide_card(cv, x, 640, 420, 380, t, t0, side)
        if r: cx, al = r; K.blit(cv, K.txtf(nm, 360, 52, INK), cx, 640, al)

@project.scene(project.boundary(2))
def pros(cv, t):
    K.title(cv, [("مين", INK), ("يناسبك؟", ACC)], 90, 270, t, project.boundary(2) + .15)
    for k, (t0, y, txt_, ok) in enumerate(((P(2), 520, "اللابتوب: خفيف وسهل", True), (P(3), 700, "الجهاز القوي: أسرع بكثير", True), (P(4), 880, "كل واحد لشغل مختلف", False))):
        r = K.slide_card(cv, 540, y, 880, 140, t, t0, 1 if k % 2 == 0 else -1)
        if r: cx, al = r; K.blit(cv, K.txtf(txt_, 640, 48, INK), cx + 40, y, al); K.stamp(cv, cx - 370, y, t, t0 + .4, ok, ACC, 32)

@project.scene(project.boundary(5), bg='dark', transition='wipe', tparams=dict(edge=ACC))
def cta(cv, t):
    sc, al = K.pop(t, P(5), .5)
    K.blit(cv, K.cardspr(860, 280, 60, ACC), 540, 620, al, sc); K.blit(cv, K.txtf("اكتب رأيك بالتعليقات", 760, 78, WHITE), 540, 620, al, sc)
    K.arrow_down(cv, 900, 1000 + abs(math.sin(t * 5)) * 26, 110, ACC)

robot = Presenter(keys=[(0, 'neutral', 'rest', None), (P(1) + .8, 'happy', 'aim', (770, 640)), (P(1) + 1.4, 'thinking', 'aim', (310, 640)),
                        (P(2), 'happy', 'aim', (540, 520)), (P(3), 'excited', 'aim', (540, 700)), (P(4), 'serious', 'shrug', None), (P(5), 'excited', 'wave', None)],
                  moves=[(P(5) - .1, P(5) + .5, 540, 1215, .62)], outline=INK)
project.overlay(robot)
project.set_captions('karaoke')
for t0, n, g in ((P(1) + .3, 'pop', .3), (P(1) + .7, 'pop', .3), (P(2), 'tick', .3), (P(3), 'tick', .3), (P(4), 'ding', .3), (P(5), 'sparkle', .3)): project.sfx(t0, n, g)
