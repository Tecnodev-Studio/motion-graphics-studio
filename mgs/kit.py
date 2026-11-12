# Copyright 2026 Tecnodev Studio. Licensed under the Apache License 2.0 (see LICENSE).
"""kit.py - drawing primitives on a uint8 RGB numpy canvas. Text/shapes are cached RGBA sprites blended with blit().

Canvas size is configurable: call set_canvas(w, h) once (the engine does it). Arabic/RTL needs PIL built with raqm
(has_raqm()); without it letters are disconnected - install a Pillow wheel from PyPI (they ship raqm) or libraqm.
"""
import math, os, glob
import numpy as np, cv2
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter, features

W, H, FPS = 1080, 1920, 30
RTL = True          # default text direction; Project(rtl=...) sets it. Pass rtl= explicitly to override per call.
PRESETS = {'shorts': (1080, 1920), 'reels': (1080, 1920), 'tiktok': (1080, 1920), 'youtube': (1920, 1080),
           'square': (1080, 1080), 'portrait45': (1080, 1350)}

def set_rtl(flag):
    global RTL
    RTL = bool(flag)

def set_canvas(w, h, fps=30):
    global W, H, FPS
    W, H, FPS = int(w), int(h), int(fps)
    _clear_caches()

def _clear_caches():
    for f in (radial_bg,):
        try: f.cache_clear()
        except AttributeError: pass

def safe_area():
    """(left, top, right, bottom) margins that vertical-video apps tend to cover (title, buttons, caption bar)."""
    if H > W: return (int(W * .06), int(H * .08), int(W * .13), int(H * .20))
    return (int(W * .05), int(H * .06), int(W * .05), int(H * .10))

# ------------------------------------------------------------------ fonts
_FONT_CANDIDATES = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf',
    '/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf', '/usr/share/fonts/truetype/noto/NotoNaskhArabic-Bold.ttf',
    '/usr/share/fonts/opentype/noto/NotoSansArabic-Bold.ttf', '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf',
    'C:/Windows/Fonts/tahomabd.ttf', 'C:/Windows/Fonts/arialbd.ttf', 'C:/Windows/Fonts/segoeuib.ttf',
    '/System/Library/Fonts/Supplemental/Arial Bold.ttf', '/System/Library/Fonts/GeezaPro.ttc', '/Library/Fonts/Arial Bold.ttf']
def find_font():
    env = os.environ.get('MGS_FONT')
    if env and os.path.exists(env): return env
    for p in _FONT_CANDIDATES:
        if os.path.exists(p): return p
    for pat in ('/usr/share/fonts/**/*.ttf', '/usr/local/share/fonts/**/*.ttf', os.path.expanduser('~/.fonts/**/*.ttf')):
        g = glob.glob(pat, recursive=True)
        if g: return sorted(g)[0]
    raise RuntimeError('No TrueType font found. Set MGS_FONT=/path/to/font.ttf (any free font, e.g. Noto Sans Arabic / Cairo, SIL OFL).')
FONT = None
def font_path():
    global FONT
    if FONT is None: FONT = find_font()
    return FONT
def has_raqm(): return bool(features.check('raqm'))

# ------------------------------------------------------------------ colour
def lum(c):
    def f(v): v /= 255; return v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2])
def contrast(a, b):
    """WCAG contrast ratio; body text should be >= 4.5, large text >= 3."""
    la, lb = sorted((lum(a), lum(b)), reverse=True); return (la + .05) / (lb + .05)
def mix(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

# ------------------------------------------------------------------ easing (never animate linearly)
def cl(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo3(x): x = cl(x); return 1 - (1 - x) ** 3
def eo5(x): x = cl(x); return 1 - (1 - x) ** 5
def eio(x): x = cl(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def eob(x, s=1.70158): x = cl(x); return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2
def smooth(x): x = cl(x); return x * x * (3 - 2 * x)
def pop(t, t0, d=0.4):
    """(scale, alpha) for something that appears at t0 with a springy overshoot."""
    x = (t - t0) / d
    if x <= 0: return 0.0, 0.0
    return max(eob(x), 0.0), cl(x * 4)
def spring(t, t0, k=14.0, damp=6.0):
    """damped spring 0 -> 1 after t0 (for UI-like bounces)."""
    x = t - t0
    if x <= 0: return 0.0
    return 1 - math.exp(-damp * x) * math.cos(k * x)

# ------------------------------------------------------------------ sprites
def txt(s, size, color, rtl=None):
    """cached text sprite; rtl=None uses the project default (K.RTL)."""
    return _txt(s, int(size), tuple(color), RTL if rtl is None else bool(rtl))

@lru_cache(None)
def _txt(s, size, color, rtl):
    f = ImageFont.truetype(font_path(), int(size))
    kw = dict(direction='rtl', language='ar') if (rtl and has_raqm()) else {}
    tmp = ImageDraw.Draw(Image.new('RGBA', (4, 4)))
    l, t, r, b = tmp.textbbox((0, 0), s, font=f, **kw)
    pad = 12
    im = Image.new('RGBA', (max(4, r - l + 2 * pad), max(4, b - t + 2 * pad)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((pad - l, pad - t), s, font=f, fill=tuple(color) + (255,), **kw)
    return np.array(im)

def txtf(s, maxw, size, color, rtl=None):
    """text that shrinks until it fits maxw."""
    while True:
        sp = txt(s, size, tuple(color), rtl)
        if sp.shape[1] <= maxw or size < 16: return sp
        size -= 2

@lru_cache(512)
def rrect(w, h, r, fill, alpha=255, outline=None, ow=0):
    w = max(4, int(w)); h = max(4, int(h)); r = max(0, min(int(r), min(w, h) // 2))
    S = 3
    im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, w * S - 1, h * S - 1], r * S, fill=tuple(fill) + (alpha,),
                                         outline=(tuple(outline) + (255,)) if outline else None, width=int(ow) * S)
    return np.array(im.resize((w, h), Image.LANCZOS))

@lru_cache(256)
def cardspr(w, h, r=34, fill=(255, 255, 255), outline=None, ow=0, shadow=(90, 60, 40, 80)):
    """UI card with a soft drop shadow."""
    pad = 46
    base = Image.new('RGBA', (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 10, pad + w, pad + h + 10], r, fill=shadow)
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    ImageDraw.Draw(base).rounded_rectangle([pad, pad, pad + w, pad + h], r, fill=tuple(fill) + (255,),
                                           outline=(tuple(outline) + (255,)) if outline else None, width=int(ow))
    return np.array(base)

def compose(base, over, dy=0):
    """paste RGBA `over` centred on RGBA `base`."""
    out = base.copy(); h, w = over.shape[:2]; H0, W0 = base.shape[:2]
    x0 = (W0 - w) // 2; y0 = (H0 - h) // 2 + dy
    al = over[..., 3:4].astype(np.float32) / 255.0
    reg = out[y0:y0 + h, x0:x0 + w].astype(np.float32)
    out[y0:y0 + h, x0:x0 + w, :3] = (reg[..., :3] * (1 - al) + over[..., :3] * al).astype(np.uint8)
    out[y0:y0 + h, x0:x0 + w, 3] = np.maximum(out[y0:y0 + h, x0:x0 + w, 3], over[..., 3])
    return out

@lru_cache(256)
def chip(s, size, fill, tc, px=44, py=22, outline=None):
    t = txt(s, size, tuple(tc)); w, h = t.shape[1] + 2 * px, t.shape[0] + 2 * py
    return compose(rrect(w, h, h // 2, fill, 255, outline, 4 if outline else 0), t)

def blit(cv, spr, cx, cy, a=1.0, s=1.0):
    """alpha-blend an RGBA sprite centred at (cx, cy), optional scale."""
    if a <= 0.004 or s <= 0.004: return
    if abs(s - 1.0) > 1e-3:
        spr = cv2.resize(spr, (max(1, int(spr.shape[1] * s)), max(1, int(spr.shape[0] * s))),
                         interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR)
    h, w = spr.shape[:2]; x0 = int(round(cx - w / 2)); y0 = int(round(cy - h / 2))
    ax0, ay0, ax1, ay1 = max(x0, 0), max(y0, 0), min(x0 + w, cv.shape[1]), min(y0 + h, cv.shape[0])
    if ax0 >= ax1 or ay0 >= ay1: return
    s2 = spr[ay0 - y0:ay1 - y0, ax0 - x0:ax1 - x0]
    al = (s2[..., 3:4].astype(np.float32) / 255.0) * a
    roi = cv[ay0:ay1, ax0:ax1]
    roi[:] = (roi * (1 - al) + s2[..., :3] * al).astype(np.uint8)

# ------------------------------------------------------------------ images (photos / logos the user supplies or has rights to)
@lru_cache(64)
def image_sprite(path, w, h, radius=28, fit='cover'):
    im = Image.open(path).convert('RGBA'); iw, ih = im.size
    sc = max(w / iw, h / ih) if fit == 'cover' else min(w / iw, h / ih)
    im = im.resize((max(1, int(iw * sc)), max(1, int(ih * sc))), Image.LANCZOS)
    canvas = Image.new('RGBA', (w, h), (0, 0, 0, 0)); canvas.paste(im, ((w - im.width) // 2, (h - im.height) // 2), im)
    mask = Image.new('L', (w, h), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius, fill=255)
    a = np.array(canvas.split()[3]); canvas.putalpha(Image.fromarray(np.minimum(a, np.array(mask))))
    return np.array(canvas)

def ken_burns(cv, spr, cx, cy, t, t0, dur, z0=1.0, z1=1.12, a=1.0):
    """slow zoom on a photo sprite (makes stills feel like video)."""
    q = smooth((t - t0) / max(dur, 1e-3)); blit(cv, spr, cx, cy, a, z0 + (z1 - z0) * q)

# ------------------------------------------------------------------ video footage as a layer (b-roll, screen recordings, your own clips)
class VideoLayer:
    """Use an existing video file as a background or a rounded 'window' inside a scene. Safe with parallel rendering (reopens per process).
        clip = VideoLayer('clip.mp4')            # module level in project.py
        clip.fill(cv, t)                          # full-frame background (cover-fit, loops)
        clip.draw(cv, t, cx, cy, w, h, radius=30) # picture-in-picture window
    Effects (grade, bloom, ...) apply on top because they run on the finished frame."""
    def __init__(self, path, loop=True, offset=0.0):
        self.path, self.loop, self.offset, self._cap, self._pid, self._pos = path, loop, offset, None, None, -2
        c = cv2.VideoCapture(path)
        if not c.isOpened(): raise FileNotFoundError(f'cannot open video: {path}')
        self.fps = c.get(cv2.CAP_PROP_FPS) or 30.0; self.n = max(1, int(c.get(cv2.CAP_PROP_FRAME_COUNT))); self.duration = self.n / self.fps; c.release()
    def _open(self):
        if self._cap is None or self._pid != os.getpid():
            self._cap = cv2.VideoCapture(self.path); self._pid = os.getpid(); self._pos = -2
    def raw(self, t):
        """RGB frame at time t (seconds) at the clip's own size."""
        self._open(); idx = int((t + self.offset) * self.fps)
        idx = idx % self.n if self.loop else min(max(idx, 0), self.n - 1)
        if idx != self._pos + 1: self._cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, fr = self._cap.read()
        if not ok: self._cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, idx - 1)); ok, fr = self._cap.read()
        self._pos = idx
        return cv2.cvtColor(fr, cv2.COLOR_BGR2RGB) if ok else np.zeros((H, W, 3), np.uint8)
    @staticmethod
    def _cover(fr, w, h):
        ih, iw = fr.shape[:2]; sc = max(w / iw, h / ih); r = cv2.resize(fr, (max(w, int(iw * sc)), max(h, int(ih * sc))), interpolation=cv2.INTER_AREA)
        y0 = (r.shape[0] - h) // 2; x0 = (r.shape[1] - w) // 2; return r[y0:y0 + h, x0:x0 + w]
    def fill(self, cv, t): cv[:] = self._cover(self.raw(t), cv.shape[1], cv.shape[0])
    def draw(self, cv, t, cx, cy, w, h, radius=30, a=1.0, s=1.0):
        fr = self._cover(self.raw(t), int(w), int(h)); spr = np.dstack([fr, rrect(int(w), int(h), radius, (255, 255, 255))[..., 3]])
        blit(cv, spr, cx, cy, a, s)

# ------------------------------------------------------------------ vector bits (cv2 anti-aliased)
def line(cv, p, q, col, th): cv2.line(cv, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), tuple(int(c) for c in col), int(th), cv2.LINE_AA)
def circle(cv, c, r, col, th=-1): cv2.circle(cv, (int(c[0]), int(c[1])), int(max(r, 0)), tuple(int(v) for v in col), int(th), cv2.LINE_AA)
def poly(cv, pts, col): cv2.fillConvexPoly(cv, np.array(pts, np.int32), tuple(int(c) for c in col), cv2.LINE_AA)

def check(cv, cx, cy, sz, col, p=1.0):
    pts = [(cx - .5 * sz, cy), (cx - .15 * sz, cy + .4 * sz), (cx + .55 * sz, cy - .4 * sz)]; th = max(2, int(sz * .2))
    if p < 0.5:
        q = p / .5; line(cv, pts[0], (pts[0][0] + (pts[1][0] - pts[0][0]) * q, pts[0][1] + (pts[1][1] - pts[0][1]) * q), col, th)
    else:
        q = (p - .5) / .5; line(cv, pts[0], pts[1], col, th)
        line(cv, pts[1], (pts[1][0] + (pts[2][0] - pts[1][0]) * q, pts[1][1] + (pts[2][1] - pts[1][1]) * q), col, th)

def cross(cv, cx, cy, sz, col, p=1.0):
    th = max(3, int(sz * .2)); a = min(1, p * 2)
    line(cv, (cx - sz / 2, cy - sz / 2), (cx - sz / 2 + sz * a, cy - sz / 2 + sz * a), col, th)
    if p > .5:
        q = (p - .5) * 2; line(cv, (cx + sz / 2, cy - sz / 2), (cx + sz / 2 - sz * q, cy - sz / 2 + sz * q), col, th)

def arrow_down(cv, cx, cy, sz, col):
    poly(cv, [[cx - sz * .22, cy - sz * .5], [cx + sz * .22, cy - sz * .5], [cx + sz * .22, cy], [cx + sz * .5, cy],
              [cx, cy + sz * .5], [cx - sz * .5, cy], [cx - sz * .22, cy]], col)

def warn(cv, cx, cy, sz, col, ink):
    poly(cv, [[cx, cy - sz * .5], [cx + sz * .55, cy + sz * .45], [cx - sz * .55, cy + sz * .45]], col)
    line(cv, (cx, cy - sz * .12), (cx, cy + sz * .17), ink, max(3, int(sz * .1)))
    circle(cv, (cx, cy + sz * .31), max(2, int(sz * .06)), ink)

def search_icon(cv, cx, cy, s, col):
    circle(cv, (cx - 6 * s, cy - 6 * s), 26 * s, col, max(3, int(6 * s)))
    line(cv, (cx + 12 * s, cy + 12 * s), (cx + 34 * s, cy + 34 * s), col, max(4, int(8 * s)))

def meter(cv, cx, cy, w, p, col, track):
    blit(cv, rrect(w, 22, 11, tuple(track)), cx, cy)
    fw = int(w * cl(p))
    if fw > 14: blit(cv, rrect(fw, 22, 11, tuple(col)), cx - w / 2 + fw / 2, cy)

def ring(cv, cx, cy, r, th, col, a):
    """expanding translucent ring (pulse)."""
    if a <= 0.01 or r <= 1: return
    R_ = int(r + th + 4); x0, y0, x1, y1 = max(int(cx) - R_, 0), max(int(cy) - R_, 0), min(int(cx) + R_, cv.shape[1]), min(int(cy) + R_, cv.shape[0])
    if x1 <= x0 or y1 <= y0: return
    roi = cv[y0:y1, x0:x1]; ov = roi.copy(); circle(ov, (cx - x0, cy - y0), r, col, th)
    roi[:] = cv2.addWeighted(ov, a, roi, 1 - a, 0)

def stamp(cv, cx, cy, t, t0, ok, col, size=44):
    """check / cross badge that pops in."""
    sc, al = pop(t, t0, 0.3)
    if al <= 0: return
    circle(cv, (cx, cy), size * .9 * min(sc, 1.1), col)
    (check if ok else cross)(cv, cx, cy + (2 if ok else 0), size * .8 * min(sc, 1.1), (255, 255, 255), cl((t - t0) / .25))

# ------------------------------------------------------------------ layout helpers
def title(cv, parts, size, y, t, t0, dy=30, rtl=None, maxw=None):
    """title from [(text, colour), ...] in READING order (RTL: first part ends up rightmost; LTR: leftmost).
    One coloured word = house style. Shrinks automatically if wider than maxw (default 92% of the canvas)."""
    rtl = RTL if rtl is None else rtl; maxw = maxw or cv.shape[1] * .92
    sc, al = pop(t, t0, 0.5)
    if al <= 0: return
    while True:
        sprs = [txt(s_, size, tuple(c), rtl) for s_, c in parts]; gap = int(size * .28)
        total = sum(s_.shape[1] - 24 for s_ in sprs) + gap * (len(sprs) - 1)
        if total <= maxw or size < 24: break
        size = int(size * maxw / total) - 1
    yy = y + (1 - eo3((t - t0) / 0.5)) * dy
    x = cv.shape[1] / 2 + (total / 2 if rtl else -total / 2)
    for s_ in sprs:
        wv = s_.shape[1] - 24
        blit(cv, s_, x - wv / 2 if rtl else x + wv / 2, yy, al)
        x += -(wv + gap) if rtl else (wv + gap)

def slide_card(cv, cx, cy, w, h, t, t0, side=1, fill=(255, 255, 255), outline=None, ow=0, d=0.45):
    """card slides in from the side (+1 right, -1 left), decelerating. Returns (current_x, alpha) or None before t0."""
    x = (t - t0) / d
    if x <= 0: return None
    off = (1 - eo3(x)) * cv.shape[1] * .48 * side; al = cl(x * 3)
    blit(cv, cardspr(int(w), int(h), 34, tuple(fill), outline, ow), cx + off, cy, al)
    return cx + off, al

@lru_cache(8)
def radial_bg(base, glow, cy_frac=0.34, w=None, h=None):
    w = w or W; h = h or H
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.clip(np.sqrt(((xx - w / 2) / (w * .62)) ** 2 + ((yy - h * cy_frac) / (h * .3)) ** 2), 0, 1)[..., None] ** 1.4
    return (np.array(glow, np.float32) * (1 - d) + np.array(base, np.float32) * d).astype(np.uint8)

def solid_bg(color, w=None, h=None):
    return np.full((h or H, w or W, 3), color, np.uint8)

def outlined(spr, col, k=13):
    """thin outline around an RGBA sprite (keeps a light mascot visible on a light background)."""
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)); d = cv2.dilate(spr[..., 3], ker)
    out = np.zeros_like(spr, dtype=np.float32); out[..., :3] = col; out[..., 3] = d
    al = spr[..., 3:4].astype(np.float32) / 255
    out[..., :3] = out[..., :3] * (1 - al) + spr[..., :3] * al; out[..., 3] = np.maximum(out[..., 3], spr[..., 3])
    return out.astype(np.uint8)

@lru_cache(None)
def subtitle_sprite(s, pill=(23, 20, 21), ink=(255, 255, 255), size=54, maxw=940, rtl=None):
    rtl = RTL if rtl is None else rtl
    f = ImageFont.truetype(font_path(), int(size)); tmp = ImageDraw.Draw(Image.new('RGBA', (4, 4)))
    kw = dict(direction='rtl', language='ar') if (rtl and has_raqm()) else {}
    lines, cur = [], ''
    for wd in s.split(' '):
        c = (cur + ' ' + wd).strip()
        if tmp.textlength(c, font=f, **kw) <= maxw or not cur: cur = c
        else: lines.append(cur); cur = wd
    lines.append(cur)
    sps = [txt(l, size, tuple(ink), rtl) for l in lines]
    w = max(x.shape[1] for x in sps) + 70; h = sum(x.shape[0] for x in sps) - 8 * (len(sps) - 1) + 44
    base = rrect(w, h, 36, tuple(pill), 235); y = 10
    for x in sps:
        base = compose(base, x, dy=int(y + x.shape[0] / 2 - h / 2)); y += x.shape[0] - 8
    return base
