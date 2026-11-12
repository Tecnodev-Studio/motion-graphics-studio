# Copyright 2026 Tecnodev Studio. Licensed under the Apache License 2.0 (see LICENSE).
"""transitions.py - tr(a, b, p): blend frame a (outgoing) into frame b (incoming), p in [0,1] (already eased by the engine)."""
import numpy as np, cv2

def crossfade(a, b, p): return cv2.addWeighted(b, p, a, 1 - p, 0)

def dip(a, b, p, color=(0, 0, 0)):
    """fade to a colour and back."""
    c = np.empty_like(a); c[:] = color
    return cv2.addWeighted(a, 1 - 2 * p, c, 2 * p, 0) if p < .5 else cv2.addWeighted(c, 2 - 2 * p, b, 2 * p - 1, 0)

def _slide(a, b, p, direction):
    h, w = a.shape[:2]; out = np.empty_like(a); off = int(w * p)
    if direction > 0:   # incoming pushes in from the right
        out[:, :w - off] = a[:, off:]; out[:, w - off:] = b[:, :off]
    else:
        out[:, off:] = a[:, :w - off]; out[:, :off] = b[:, w - off:]
    return out
def slide_left(a, b, p): return _slide(a, b, p, 1)
def slide_right(a, b, p): return _slide(a, b, p, -1)

def wipe(a, b, p, slant=0.12, edge=(217, 130, 75)):
    """slanted wipe with a coloured edge bar."""
    h, w = a.shape[:2]; sl = int(w * slant); x = int((w + sl) * p) - sl
    yy = np.arange(h)[:, None]; xx = np.arange(w)[None, :]
    edge_x = x + (yy / h) * sl
    mb = (xx < edge_x)[..., None]; out = np.where(mb, b, a).astype(np.uint8)
    bar = ((xx >= edge_x) & (xx < edge_x + w * .012))[..., None]
    out[bar[..., 0]] = edge
    return out

def zoom(a, b, p):
    h, w = a.shape[:2]
    def z(img, s):
        M = cv2.getRotationMatrix2D((w / 2, h / 2), 0, s); return cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
    return cv2.addWeighted(z(b, 0.85 + 0.15 * p), p, z(a, 1 + 0.25 * p), 1 - p, 0)

def glitch(a, b, p, seed=7):
    rng = np.random.default_rng(seed + int(p * 10)); src = a if p < .5 else b
    out = src.copy(); h, w = out.shape[:2]
    for _ in range(8):
        y0 = int(rng.integers(0, h - 40)); hh = int(rng.integers(10, 80)); dx = int(rng.integers(-w // 12, w // 12))
        out[y0:y0 + hh] = np.roll(out[y0:y0 + hh], dx, axis=1)
    out[:, 6:, 0] = out[:, :-6, 0]
    return out

def iris(a, b, p, center=None):
    h, w = a.shape[:2]; cx, cy = center or (w // 2, h // 2)
    r = int(np.hypot(w, h) * p); m = np.zeros((h, w), np.uint8); cv2.circle(m, (cx, cy), r, 255, -1, cv2.LINE_AA)
    mm = (m.astype(np.float32) / 255)[..., None]
    return (b * mm + a * (1 - mm)).astype(np.uint8)

TRANSITIONS = {'crossfade': crossfade, 'dip': dip, 'slide': slide_left, 'slide_left': slide_left, 'slide_right': slide_right,
               'wipe': wipe, 'zoom': zoom, 'glitch': glitch, 'iris': iris, 'cut': lambda a, b, p: b}
