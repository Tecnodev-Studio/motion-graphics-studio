# Copyright 2026 Tecnodev Studio. Licensed under the Apache License 2.0 (see LICENSE).
"""components.py - ready-made motion pieces. Every function is pure drawing: components.x(cv, ..., t, t0, ...) draws the state at time t."""
import math, numpy as np, cv2
from . import kit as K
from .kit import blit, txt, rrect, eo3, eio, cl, pop

def counter(cv, v0, v1, t, t0, d, cx, cy, size, color, fmt='{:,.0f}', suffix='', rtl=False):
    """number that rolls from v0 to v1."""
    q = eo3((t - t0) / d)
    if t < t0: return
    v = v0 + (v1 - v0) * q
    blit(cv, txt(fmt.format(v) + suffix, size, tuple(color), rtl), cx, cy)

def bar_chart(cv, data, t, t0, box, ink, track, colors, stagger=0.15, size=36, rtl=None, horizontal=False):
    """data=[(label, value)], box=(cx, cy, w, h). Bars grow with a stagger; label + value shown."""
    cx, cy, w, h = box; n = len(data); mx = max(v for _, v in data) or 1
    slot = (h if horizontal else w) / n
    for i, (lab, v) in enumerate(data):
        p = eo3((t - t0 - i * stagger) / 0.7)
        if p <= 0: continue
        col = tuple(colors[i % len(colors)])
        if horizontal:
            y = cy - h / 2 + slot * (i + .5); bw = int((w * .62) * v / mx * p)
            blit(cv, rrect(int(w * .62), 30, 15, tuple(track)), cx + w * .12, y)
            if bw > 20: blit(cv, rrect(bw, 30, 15, col), cx + w * .12 - w * .31 + bw / 2, y)
            blit(cv, txt(str(lab), size, tuple(ink), rtl), cx - w * .36 if not rtl else cx + w * .42, y, cl(p * 2))
        else:
            x = cx - w / 2 + slot * (i + .5); bh = int(h * .8 * v / mx * p); bw = int(slot * .55)
            if bh > 12: blit(cv, rrect(bw, bh, min(14, bw // 2), col), x, cy + h / 2 - bh / 2 - size)
            blit(cv, txt(str(lab), size, tuple(ink), rtl), x, cy + h / 2, cl(p * 2))
            if p > .6: blit(cv, txt(f'{v:,.0f}', int(size * .9), tuple(ink), False), x, cy + h / 2 - bh - size * 1.6, cl((p - .6) * 3))

def line_chart(cv, values, t, t0, d, box, col, axis, th=8, dots=True):
    """polyline revealed left to right. box=(cx, cy, w, h)."""
    cx, cy, w, h = box; n = len(values); lo, hi = min(values), max(values); span = (hi - lo) or 1
    pts = [(cx - w / 2 + w * i / (n - 1), cy + h / 2 - h * (v - lo) / span) for i, v in enumerate(values)]
    K.line(cv, (cx - w / 2, cy + h / 2), (cx + w / 2, cy + h / 2), axis, 3); K.line(cv, (cx - w / 2, cy - h / 2), (cx - w / 2, cy + h / 2), axis, 3)
    q = eo3((t - t0) / d) * (n - 1)
    for i in range(n - 1):
        if q >= i + 1: K.line(cv, pts[i], pts[i + 1], col, th)
        elif q > i:
            f = q - i; K.line(cv, pts[i], (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f), col, th)
    if dots:
        for i, p_ in enumerate(pts):
            if q >= i: K.circle(cv, p_, th * 1.1, col)

def kinetic_text(cv, words, t, t0, cx, cy, size, color, stagger=0.12, accent=None, accent_color=None, rtl=None, maxw=None, line_gap=1.25):
    rtl = K.RTL if rtl is None else rtl
    """words appear one by one (pop + rise), wrapped and centred. accent = set of word indexes drawn in accent_color."""
    maxw = maxw or cv.shape[1] * .86; accent = accent or set()
    sprs = [txt(w, size, tuple(accent_color if (i in accent and accent_color) else color), rtl) for i, w in enumerate(words)]
    gap = size * .3; lines, cur, cw = [], [], 0
    for i, s in enumerate(sprs):
        wv = s.shape[1] - 24
        if cur and cw + wv + gap > maxw: lines.append(cur); cur, cw = [], 0
        cur.append((i, s, wv)); cw += wv + gap
    lines.append(cur)
    y = cy - (len(lines) - 1) * size * line_gap / 2
    for ln in lines:
        total = sum(wv for _, _, wv in ln) + gap * (len(ln) - 1); x = cv.shape[1] / 2 + (cx - cv.shape[1] / 2) + (total / 2 if rtl else -total / 2)
        for i, s, wv in ln:
            sc, al = pop(t, t0 + i * stagger, 0.35)
            if al > 0:
                xc = x - wv / 2 if rtl else x + wv / 2
                blit(cv, s, xc, y + (1 - eo3((t - t0 - i * stagger) / .35)) * 26, al, 0.85 + 0.15 * min(sc, 1.15))
            x += -(wv + gap) if rtl else (wv + gap)
        y += size * line_gap

def lower_third(cv, line1, line2, t, t0, dur, x, y, bg, ink, accent, rtl=None, w=700):
    rtl = K.RTL if rtl is None else rtl
    """name/title bar that slides in, holds, slides out."""
    a = eo3((t - t0) / .45); b = eo3((t - (t0 + dur - .4)) / .4)
    p = a * (1 - b)
    if p <= 0: return
    off = (1 - p) * -w * (1 if not rtl else -1)
    blit(cv, rrect(w, 130, 22, tuple(bg)), x + off, y, 1.0); blit(cv, rrect(10, 130, 5, tuple(accent)), x + off + (-w / 2 + 5 if not rtl else w / 2 - 5), y)
    blit(cv, K.txtf(line1, w - 80, 50, ink, rtl), x + off, y - 20); blit(cv, K.txtf(line2, w - 80, 32, accent, rtl), x + off, y + 30)

def logo_reveal(cv, text, t, t0, cx, cy, size, color, accent, rtl=False):
    """text revealed by a growing mask, underline sweep and a pulse ring."""
    if t < t0: return
    s = txt(text, size, tuple(color), rtl); q = eo3((t - t0) / .7)
    h, w = s.shape[:2]; m = s.copy(); cut = int(w * q)
    if rtl: m[:, :w - cut, 3] = 0
    else: m[:, cut:, 3] = 0
    blit(cv, m, cx, cy)
    K.line(cv, (cx - w / 2, cy + h * .62), (cx - w / 2 + w * eo3((t - t0 - .3) / .5), cy + h * .62), accent, max(4, size // 14))
    K.ring(cv, int(cx), int(cy), size * .6 + (t - t0) * 400, 5, accent, max(0, .8 - (t - t0)))

def progress_ring(cv, cx, cy, r, p, col, track, th=18):
    K.circle(cv, (cx, cy), r, track, th)
    cv2.ellipse(cv, (int(cx), int(cy)), (int(r), int(r)), -90, 0, 360 * cl(p), tuple(int(c) for c in col), int(th), cv2.LINE_AA)

def confetti(cv, t, t0, colors, n=60, dur=2.2, seed=1, origin=None):
    """burst of confetti from origin (default: upper centre)."""
    x = t - t0
    if x < 0 or x > dur: return
    rng = np.random.default_rng(seed); ox, oy = origin or (cv.shape[1] / 2, cv.shape[0] * .35)
    for i in range(n):
        ang = rng.uniform(-math.pi, 0); sp = rng.uniform(300, 900); sz = rng.uniform(8, 18); col = colors[i % len(colors)]
        px = ox + math.cos(ang) * sp * x; py = oy + math.sin(ang) * sp * x + 900 * x * x
        K.poly(cv, [[px - sz, py - sz / 2], [px + sz, py - sz / 2], [px + sz, py + sz / 2], [px - sz, py + sz / 2]], col) if (i % 2) else K.circle(cv, (px, py), sz / 2, col)

def speed_lines(cv, t, t0, dur, col, n=26, seed=2):
    """radial manga-style speed lines (impact / dramatic reveal)."""
    x = (t - t0) / dur
    if x < 0 or x > 1: return
    rng = np.random.default_rng(seed); h, w = cv.shape[:2]; c = (w / 2, h / 2); a = 1 - x
    ov = cv.copy()
    for _ in range(n):
        ang = rng.uniform(0, 2 * math.pi); r0 = rng.uniform(.25, .45) * min(w, h); r1 = r0 + rng.uniform(.3, .6) * min(w, h)
        K.line(ov, (c[0] + math.cos(ang) * r0, c[1] + math.sin(ang) * r0), (c[0] + math.cos(ang) * r1, c[1] + math.sin(ang) * r1), col, int(rng.integers(3, 9)))
    cv[:] = cv2.addWeighted(ov, 0.7 * a, cv, 1 - 0.7 * a, 0)

def stroke_draw(cv, pts, t, t0, d, col, th=8, wobble=0.0, seed=0):
    """hand-drawn feel: the polyline is drawn progressively like a marker (whiteboard explainers)."""
    if t < t0 or len(pts) < 2: return
    rng = np.random.default_rng(seed); seglen = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total = sum(seglen) or 1; target = total * eio((t - t0) / d); acc = 0
    for i, L in enumerate(seglen):
        if acc >= target: break
        f = min(1.0, (target - acc) / (L or 1)); p0, p1 = pts[i], pts[i + 1]
        j = (rng.normal(0, wobble, 2) if wobble else (0, 0))
        K.line(cv, (p0[0] + j[0], p0[1] + j[1]), (p0[0] + (p1[0] - p0[0]) * f, p0[1] + (p1[1] - p0[1]) * f), col, th); acc += L

def lightning(cv, p0, p1, t, t0, dur, col, seed=3, glow=(255, 255, 255)):
    """jagged bolt between two points that flickers; pair with fx.bloom for a neon glow."""
    x = (t - t0) / dur
    if x < 0 or x > 1: return
    rng = np.random.default_rng(seed + int(t * 24)); n = 9
    pts = [(p0[0] + (p1[0] - p0[0]) * k / n + (rng.normal(0, 28) if 0 < k < n else 0), p0[1] + (p1[1] - p0[1]) * k / n + (rng.normal(0, 28) if 0 < k < n else 0)) for k in range(n + 1)]
    th = max(2, int(10 * (1 - x)))
    for i in range(n): K.line(cv, pts[i], pts[i + 1], col, th * 2); K.line(cv, pts[i], pts[i + 1], glow, max(1, th // 2))
