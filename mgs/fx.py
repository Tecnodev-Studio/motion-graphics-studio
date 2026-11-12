# Copyright 2026 Tecnodev Studio. Licensed under the Apache License 2.0 (see LICENSE).
"""fx.py - post effects applied to a finished frame: grain, vignette, bloom, camera shake, punch zoom, grade, chroma split."""
import math, numpy as np, cv2

class Grain:
    def __init__(self, strength=4.5, tiles=3, seed=3):
        self.s, self.tiles, self.seed, self._t = strength, tiles, seed, None
    def __call__(self, cv, t=0, i=0):
        if self._t is None or self._t[0].shape[:2] != cv.shape[:2]:
            rng = np.random.default_rng(self.seed)
            self._t = [rng.normal(0, self.s, cv.shape[:2] + (1,)).astype(np.float32) for _ in range(self.tiles)]
        return np.clip(cv.astype(np.float32) + self._t[i % self.tiles], 0, 255).astype(np.uint8)

class Vignette:
    def __init__(self, strength=0.4): self.s, self._m = strength, None
    def __call__(self, cv, t=0, i=0):
        if self._m is None or self._m.shape[:2] != cv.shape[:2]:
            h, w = cv.shape[:2]; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
            d = ((xx - w / 2) / (w * .78)) ** 2 + ((yy - h / 2) / (h * .72)) ** 2
            self._m = (1 - self.s * np.clip(d, 0, 1.2))[..., None].astype(np.float32)
        return np.clip(cv.astype(np.float32) * self._m, 0, 255).astype(np.uint8)

def bloom(cv, threshold=190, radius=25, strength=0.45):
    """soft glow around bright areas (neon / lightning look)."""
    g = cv.max(2); m = (g > threshold)[..., None] * cv
    small = cv2.resize(m, (cv.shape[1] // 4, cv.shape[0] // 4), interpolation=cv2.INTER_AREA)
    blur = cv2.GaussianBlur(small, (0, 0), max(1, radius / 4))
    up = cv2.resize(blur, (cv.shape[1], cv.shape[0]), interpolation=cv2.INTER_LINEAR)
    return np.clip(cv.astype(np.float32) + up.astype(np.float32) * strength, 0, 255).astype(np.uint8)

def shake(cv, t, t0, amp=14, dur=0.35, freq=40):
    """camera shake that decays after t0 (use on impacts)."""
    x = t - t0
    if x < 0 or x > dur: return cv
    k = (1 - x / dur) ** 2 * amp
    dx, dy = math.sin(x * freq) * k, math.cos(x * freq * 1.3) * k
    return cv2.warpAffine(cv, np.float32([[1, 0, dx], [0, 1, dy]]), (cv.shape[1], cv.shape[0]), borderMode=cv2.BORDER_REPLICATE)

def punch_zoom(cv, scale):
    """scale > 1 zooms in about the centre."""
    if abs(scale - 1) < 1e-3: return cv
    h, w = cv.shape[:2]; M = cv2.getRotationMatrix2D((w / 2, h / 2), 0, scale)
    return cv2.warpAffine(cv, M, (w, h), borderMode=cv2.BORDER_REPLICATE)

def grade(cv, lift=0.0, gamma=1.0, gain=1.0, tint=(1.0, 1.0, 1.0)):
    """simple colour grade: out = ((in/255)^(1/gamma) * gain + lift) * tint."""
    x = (cv.astype(np.float32) / 255) ** (1 / gamma) * gain + lift
    return np.clip(x * np.array(tint, np.float32) * 255, 0, 255).astype(np.uint8)

def chroma_split(cv, px=6):
    """RGB channel offset (glitch / impact)."""
    out = cv.copy(); out[:, px:, 0] = cv[:, :-px, 0]; out[:, :-px, 2] = cv[:, px:, 2]; return out

def flash(cv, t, t0, dur=0.18, color=(255, 255, 255), peak=0.8):
    """full-frame flash that fades out (hit frame)."""
    x = (t - t0) / dur
    if x < 0 or x > 1: return cv
    a = peak * (1 - x) ** 2
    return np.clip(cv.astype(np.float32) * (1 - a) + np.array(color, np.float32) * a, 0, 255).astype(np.uint8)
