# Copyright 2026 Tecnodev Studio. Licensed under the Apache License 2.0 (see LICENSE).
"""Optional mascot: a drawn robot presenter (lip-sync, emotions, gestures). Pure PIL, no assets. Replace with your own character the same way."""
import math
from dataclasses import dataclass, fields
from PIL import Image, ImageDraw

OFF = (238, 242, 234, 255); OFFD = (205, 214, 204, 255); COP = (217, 130, 75, 255)
DK = (10, 35, 27, 255); MUT = (150, 175, 160, 255)
S = 2; CW, CH = 800, 900

@dataclass
class Pose:
    eye_open: float = 1.0; eye_happy: float = 0.0; eye_size: float = 1.0
    look_x: float = 0.0; look_y: float = 0.0
    brow: float = 0.0; lift: float = 0.0
    smile: float = 0.6; mouth_open: float = 0.0
    tilt: float = 0.0; head_dy: float = 0.0; body_dy: float = 0.0
    swing: float = 0.0; light: float = 1.0; bright: float = 0.0   # bright: antenna/light turns white
    la: float = 12; lb: float = 8; ra: float = 12; rb: float = 8   # arm angles (0 = down, 90 = out, 180 = up)

def lerp(a, b, t):
    return Pose(**{f.name: getattr(a, f.name) + (getattr(b, f.name) - getattr(a, f.name)) * t for f in fields(Pose)})

EMO = {
    'neutral': {},
    'happy': dict(eye_happy=1, smile=1, tilt=-4),
    'excited': dict(eye_size=1.2, smile=1, lift=0.4),
    'surprised': dict(eye_size=1.55, lift=1, smile=0, bright=1),
    'annoyed': dict(eye_open=0.45, brow=0.9, smile=-0.5, tilt=3),
    'sad': dict(brow=-1, smile=-1, eye_open=0.8, head_dy=14, tilt=6),
    'serious': dict(brow=0.5, smile=0.0, eye_open=0.9),
    'thinking': dict(look_x=1, look_y=-1, smile=0.0, eye_open=0.9, tilt=-6, brow=-0.25),
    'proud': dict(eye_happy=0.0, smile=1, eye_open=0.85, tilt=-3, lift=0.2),
}
GEST = {
    'rest': dict(la=12, lb=8, ra=12, rb=8),
    'cheer': dict(la=122, lb=50, ra=122, rb=50),
    'point': dict(la=12, lb=8, ra=100, rb=0),
    'present': dict(la=12, lb=8, ra=72, rb=-35),
    'shrug': dict(la=62, lb=-55, ra=62, rb=55),
    'wave': dict(la=12, lb=8, ra=140, rb=-15),
    'think': dict(la=12, lb=8, ra=215, rb=45),
    'hips': dict(la=35, lb=-70, ra=35, rb=70),
}

def make_pose(emo='neutral', gest='rest', **extra):
    d = {}; d.update(EMO.get(emo, {})); d.update(GEST.get(gest, {})); d.update(extra)
    return Pose(**d)

def draw_robot(P: Pose) -> Image.Image:
    base = Image.new('RGBA', (CW * S, CH * S), (0, 0, 0, 0)); d = ImageDraw.Draw(base)
    s = lambda v: [x * S for x in v]
    def rr(b, r, f): d.rounded_rectangle(s(b), r * S, fill=f)
    def circ(x, y, r, f): d.ellipse(s([x - r, y - r, x + r, y + r]), fill=f)
    def ln(pts, f, w):
        d.line(s(pts), fill=f, width=int(w * S))
        for i in range(0, len(pts), 2): circ(pts[i], pts[i + 1], w / 2, f)
    by = P.body_dy
    # body
    rr([270, 520 + by, 530, 740 + by], 55, OFF); rr([340, 570 + by, 460, 650 + by], 26, DK)
    lc = tuple(int(COP[i] + (OFF[i] - COP[i]) * P.bright) for i in range(3)) + (255,)
    circ(400, 610 + by, 18 * (0.85 + 0.15 * P.light), lc)
    # head layer
    hd = Image.new('RGBA', (CW * S, CH * S), (0, 0, 0, 0)); dd = ImageDraw.Draw(hd)
    hy0 = P.head_dy + by * 0.6
    def hrr(b, r, f): dd.rounded_rectangle(s([b[0], b[1] + hy0, b[2], b[3] + hy0]), r * S, fill=f)
    def hc(x, y, r, f): dd.ellipse(s([x - r, y + hy0 - r, x + r, y + hy0 + r]), fill=f)
    def hl(pts, f, w):
        q = []
        for i in range(0, len(pts), 2): q += [pts[i], pts[i + 1] + hy0]
        dd.line(s(q), fill=f, width=int(w * S))
        for i in range(0, len(q), 2): dd.ellipse(s([q[i] - w / 2, q[i + 1] - w / 2, q[i] + w / 2, q[i + 1] + w / 2]), fill=f)
    tip = 400 + P.swing * 34
    hl([400, 150, 400 + P.swing * 16, 108, tip, 70], MUT, 10); hc(tip, 64, 22, lc)
    hrr([150, 300, 200, 400], 20, COP); hrr([600, 300, 650, 400], 20, COP)
    hrr([200, 150, 600, 500], 95, OFF); hrr([245, 215, 555, 435], 62, DK)
    for k, cx in enumerate((335, 465)):
        ex = cx + P.look_x * 14; ey = 320 + P.look_y * 11; r = 30 * P.eye_size
        if P.eye_happy > 0.5:
            dd.arc(s([ex - r, ey + hy0 - r * 0.7, ex + r, ey + hy0 + r * 0.7]), 200, 340, fill=COP, width=11 * S)
        else:
            ry = max(3, r * P.eye_open)
            dd.ellipse(s([ex - r, ey + hy0 - ry, ex + r, ey + hy0 + ry]), fill=COP)
            if ry > 12: hc(ex + 10, ey - 9 * P.eye_open, 9, OFF)
        if abs(P.brow) > 0.05 or P.lift > 0.05:
            sg = -1 if k == 0 else 1
            by_ = ey - 62 * max(P.eye_size, 1) - P.lift * 20
            yi = by_ + P.brow * 16; yo = by_ - P.brow * 10
            hl([ex + sg * -36, yo, ex + sg * 30, yi], COP, 9) if False else hl([ex - sg * 36 * -1 if False else ex + (-36 if k == 0 else 36), yo, ex + (30 if k == 0 else -30), yi], COP, 9)
    cx_, cy_ = 400, 395
    if P.mouth_open > 0.08:
        h = 8 + P.mouth_open * 48; w = 62 + P.mouth_open * 12
        dd.ellipse(s([cx_ - w / 2, cy_ + hy0 - h / 2 + 4, cx_ + w / 2, cy_ + hy0 + h / 2 + 4]), fill=COP)
        if h > 30: dd.ellipse(s([cx_ - w * .3, cy_ + hy0 + h * .05 + 4, cx_ + w * .3, cy_ + hy0 + h / 2 + 2]), fill=(176, 92, 52, 255))
    else:
        if P.smile >= 0:
            dd.arc(s([355, 365 + hy0, 445, 365 + hy0 + 28 + 50 * P.smile]), 20, 160, fill=COP, width=10 * S)
        else:
            dd.arc(s([360, 405 + hy0, 440, 405 + hy0 + 55]), 200, 340, fill=COP, width=10 * S)
    hd = hd.rotate(-P.tilt, resample=Image.BICUBIC, center=(400 * S, 500 * S))
    base.alpha_composite(hd)
    # arms
    for side, a, b in ((-1, P.la, P.lb), (1, P.ra, P.rb)):
        sx, sy = 400 + side * 130, 565 + by
        a1 = math.radians(a); a2 = math.radians(a + b)
        ex, ey = sx + side * math.sin(a1) * 88, sy + math.cos(a1) * 88
        hx, hy = ex + side * math.sin(a2) * 78, ey + math.cos(a2) * 78
        ln([sx, sy, ex, ey, hx, hy], OFFD, 38); circ(hx, hy, 27, OFF)
    return base.resize((CW, CH), Image.LANCZOS)

def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

class Timeline:
    """keys: [(t, emotion, gesture)]; blends over `blend` seconds starting at each key time."""
    def __init__(self, keys, blend=0.28):
        self.keys = sorted(keys); self.blend = blend
        self.poses = [make_pose(e, g) for _, e, g in self.keys]
    def pose_at(self, t, speak=0.0, dyn=True):
        i = max([k for k, (kt, _, _) in enumerate(self.keys) if kt <= t] or [0])
        cur = self.poses[i]
        if i > 0:
            P = lerp(self.poses[i - 1], cur, ease((t - self.keys[i][0]) / self.blend))
        else: P = lerp(cur, cur, 0)
        gest = self.keys[i][2]; emo = self.keys[i][1]
        if dyn:
            P.body_dy += math.sin(t * 2.6) * 10
            P.head_dy += math.sin(t * 2.6 - 0.5) * 3
            P.swing = math.sin(t * 3.1) * 0.5 + P.swing
            P.light = 0.5 + 0.5 * math.sin(t * 5)
            P.tilt += math.sin(t * 1.3) * 1.3
            ph = (t * 0.37) % 1.0
            if ph < 0.05: P.eye_open *= abs(ph - 0.025) / 0.025 * 0.9 + 0.1
            if gest == 'wave': P.rb += math.sin(t * 12) * 28; P.ra += math.sin(t * 12) * 6
            if gest == 'cheer': P.ra += math.sin(t * 9) * 10; P.la += math.sin(t * 9 + 1) * 10
            if emo == 'excited': P.body_dy -= abs(math.sin(t * 7)) * 26
            if emo == 'surprised': P.body_dy -= max(0, 1 - (t - self.keys[i][0]) * 5) * 30
            if emo == 'annoyed': P.tilt += math.sin(t * 6) * 0.8
            if emo == 'thinking': P.look_x += math.sin(t * 1.5) * 0.3
        if speak > 0.02: P.mouth_open = min(1.0, speak)
        return P
