# Copyright 2026 Tecnodev Studio. Licensed under the Apache License 2.0 (see LICENSE).
"""Presenter: wraps the robot as a screen overlay that talks (lip-sync), emotes, points at screen targets and walks between spots."""
import math, numpy as np
from .robot import Timeline, draw_robot
from .. import kit as K

class Presenter:
    """keys  : [(time, emotion, gesture, target)]  gesture in GEST or 'aim' (target=(x, y) on screen) ; target None otherwise
    moves : [(t0, t1, x, y, scale)]  walk/hop to a new spot between t0 and t1
    home  : (x, y, scale)  start position. outline: colour for a thin outline (needed on light backgrounds), None for dark ones."""
    def __init__(self, keys, moves=(), home=(210, 1215, 0.58), outline=None, shadow=(120, 85, 60), blend=0.3):
        self.keys, self.moves, self.home, self.outline, self.shadow = list(keys), list(moves), home, outline, shadow
        self.tl = Timeline([(k[0], k[1], 'rest' if k[2] == 'aim' else k[2]) for k in self.keys], blend=blend)

    def pos(self, t):
        x, y, s = self.home
        for t0, t1, nx, ny, ns in self.moves:
            if t < t0: break
            if t >= t1: x, y, s = nx, ny, ns
            else:
                q = K.eio((t - t0) / (t1 - t0)); return x + (nx - x) * q, y + (ny - y) * q - math.sin(q * math.pi) * 40, s + (ns - s) * q, q
        return x, y, s, 1.0

    @staticmethod
    def _aim(x, y, s, tx, ty):
        right = tx >= x; sx = x + (130 if right else -130) * s; sy = y + 115 * s
        return right, max(0, min(200, math.degrees(math.atan2((tx - sx) if right else -(tx - sx), ty - sy))))

    def pose(self, t, speak=0.0):
        i = max([k for k, kk in enumerate(self.keys) if kk[0] <= t] or [0])
        P = self.tl.pose_at(t, speak=speak); x, y, s, q = self.pos(t)
        def apply(key, w):
            right, ang = self._aim(x, y, s, key[3][0], key[3][1])
            if right: P.ra += (ang - P.ra) * w; P.rb *= (1 - w)
            else: P.la += (ang - P.la) * w; P.lb *= (1 - w)
            P.look_x += (0.9 if right else -0.9) * w
        w = K.eo3((t - self.keys[i][0]) / 0.3)
        if self.keys[i][2] == 'aim': apply(self.keys[i], w)
        elif i > 0 and self.keys[i - 1][2] == 'aim' and w < 1: apply(self.keys[i - 1], 1 - w)
        if q < 1: P.tilt += 6 * math.sin(q * math.pi)
        return P, x, y, s

    def __call__(self, cv, t, i, env=0.0):
        P, x, y, s = self.pose(t, env)
        K.blit(cv, K.rrect(300, 34, 17, tuple(self.shadow), 70), x, y + 262 * s + 16, 1.0, s / .52 * (1 - max(0, -P.body_dy) / 260))
        spr = np.array(draw_robot(P)); spr = K.outlined(spr, self.outline) if self.outline else spr
        K.blit(cv, spr, x, y, 1.0, s)
