# Copyright 2026 Tecnodev Studio. Licensed under the Apache License 2.0 (see LICENSE).
"""audio.py - synthesized sound effects (no samples, no licences), voice/music mixing with ducking, beat detection."""
import os, subprocess, tempfile
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 44100
_rng = np.random.default_rng(7)
def _tt(d): return np.arange(int(SR * d)) / SR
def _bp(x, lo, hi): return sosfilt(butter(2, [lo, min(hi, SR / 2 - 100)], 'band', fs=SR, output='sos'), x)
def _hp(x, f): return sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)
def _lp(x, f): return sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)

def whoosh(d=0.4, f0=300, f1=4000):
    n = int(SR * d); out = np.zeros(n); noise = _rng.standard_normal(n); ch = 14; sz = n // ch
    for i in range(ch):
        f = f0 * (f1 / f0) ** (i / (ch - 1)); seg = noise[i * sz:(i + 1) * sz if i < ch - 1 else n]
        out[i * sz:i * sz + len(seg)] = _bp(seg, f * 0.6, f * 1.6)
    t = np.arange(n) / SR
    return out * np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.5 * 1.6
def whoosh_s(): return whoosh(.3, 500, 2200)
def thud(d=0.5, f0=140, f1=38):
    t = _tt(d); ph = 2 * np.pi * np.cumsum(f1 + (f0 - f1) * np.exp(-t * 18)) / SR
    return np.sin(ph) * np.exp(-t * 7) * 1.4 + _lp(_rng.standard_normal(len(t)), 300) * np.exp(-t * 30) * .5
def pop(f=520, d=0.14):
    t = _tt(d); ph = 2 * np.pi * np.cumsum(f * (1 + 1.2 * np.exp(-t * 40))) / SR
    return np.sin(ph) * np.exp(-t * 28)
def ding(f=880, d=0.7):
    t = _tt(d)
    return (np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * f * 2.01 * t) + .25 * np.sin(2 * np.pi * f * 3.9 * t)) * np.exp(-t * 6.5) * .6
def tick(f=1800, d=0.03):
    t = _tt(d); return _hp(_rng.standard_normal(len(t)), 1500) * np.exp(-t * 160) * .7 + np.sin(2 * np.pi * f * t) * np.exp(-t * 200) * .4
def clunk():
    t = _tt(0.3); return (np.sin(2 * np.pi * 170 * t) * np.exp(-t * 24) + _bp(_rng.standard_normal(len(t)), 300, 2500) * np.exp(-t * 60) * .8) * 1.2
def buzz(d=0.28):
    t = _tt(d); saw = 2 * ((140 * t) % 1) - 1
    return _lp(saw, 1200) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 28 * t))) * np.minimum((d - t) / 0.03, 1) * .8
def sparkle(d=0.7):
    out = np.zeros(int(SR * d))
    for k in range(9):
        f = _rng.choice([1568, 1976, 2349, 2637, 3136]); t = _tt(.18); s = np.sin(2 * np.pi * f * t) * np.exp(-t * 22) * .35
        o = int(k * .045 * SR); out[o:o + len(s)] += s[:len(out) - o]
    return out
def riser(d=1.1, f0=300, f1=1400):
    t = _tt(d); ph = 2 * np.pi * np.cumsum(f0 * (f1 / f0) ** (t / d)) / SR
    return (np.sin(ph) * .4 + _bp(_rng.standard_normal(len(t)), 800, 6000) * .25) * (t / d) ** 1.3 * np.minimum((d - t) / 0.02, 1)
def notif():
    out = np.zeros(int(SR * .7))
    for i, f in enumerate((1318, 1760)):
        s = ding(f, .45) * .8; o = int(i * .13 * SR); out[o:o + len(s)] += s
    return out
def _add(a, b):
    n = max(len(a), len(b)); o = np.zeros(n); o[:len(a)] += a; o[:len(b)] += b; return o
def impact():
    return _add(thud(.7, 90, 32) * 1.1, whoosh(.25, 2000, 200) * .5)
def zap(d=0.35):
    t = _tt(d); f = 2400 * np.exp(-t * 9) + 300
    return (np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * .3 + _hp(_rng.standard_normal(len(t)), 3000) * .4) * np.exp(-t * 7)
def swipe(): return whoosh(.22, 1200, 5000) * .8
def note(f, d=.35):
    t = _tt(d); return (np.sin(2 * np.pi * f * t) + .3 * np.sin(2 * np.pi * 2 * f * t)) * np.exp(-t * 8) * .5

SFX = {'whoosh': whoosh, 'whoosh_s': whoosh_s, 'thud': thud, 'pop': pop, 'ding': ding, 'tick': tick, 'clunk': clunk, 'buzz': buzz,
       'sparkle': sparkle, 'riser': riser, 'notif': notif, 'impact': impact, 'zap': zap, 'swipe': swipe}

def to_wav(path, sr=SR):
    """any audio/video file -> mono wav at SR (needs ffmpeg). Returns the wav path (temp file)."""
    out = os.path.join(tempfile.gettempdir(), f'mgs_{abs(hash(os.path.abspath(path)))}.wav')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', path, '-vn', '-ac', '1', '-ar', str(sr), out], check=True)
    return out

def read_mono(path):
    if not path.lower().endswith('.wav'): path = to_wav(path)
    sr, v = wavfile.read(path); v = v.astype(np.float32) / (32768.0 if v.dtype == np.int16 else 1.0)
    if v.ndim > 1: v = v.mean(1)
    if sr != SR:
        n = int(len(v) * SR / sr); v = np.interp(np.linspace(0, len(v) - 1, n), np.arange(len(v)), v).astype(np.float32)
    return v

def envelope(v, fps, n_frames):
    """voice loudness per video frame, 0..1 (drives lip-sync / audio-reactive visuals)."""
    hop = SR / fps; e = np.zeros(n_frames)
    for i in range(n_frames):
        seg = v[int(i * hop):int((i + 1) * hop)]; e[i] = np.sqrt((seg ** 2).mean()) if len(seg) else 0
    e = e / (np.percentile(e, 95) + 1e-9); e = np.convolve(e, [.25, .5, .25], 'same'); return np.clip(e * 1.05, 0, 1)

def detect_beats(path, min_gap=0.25, sens=1.6):
    """onset times (s) of music, to cut/animate on the beat. Spectral-flux peak picking (free, offline)."""
    from scipy.signal import find_peaks, stft
    v = read_mono(path); f, t, Z = stft(v, SR, nperseg=1024, noverlap=512); P = np.abs(Z)
    flux = np.maximum(0, np.diff(np.log(P + 1e-6), axis=1)).sum(0)
    th = flux.mean() + sens * flux.std(); pk, _ = find_peaks(flux, height=th, distance=max(1, int(min_gap * SR / 512)))
    return [float(t[i + 1]) for i in pk]

def mix(events, duration, voice=None, music=None, music_gain=0.18, duck=0.65, sfx_gain=0.30, voice_gain=1.5, out='final_audio.wav', lead=0.08):
    """events=[(time, name|callable, gain)]. SFX land `lead` seconds early (feels in sync). Music is ducked under the voice.
    Returns out path. Peak-normalised, soft-limited."""
    N = int(SR * duration); fx = np.zeros(N)
    for t0, name, g in events:
        snd = (SFX[name]() if isinstance(name, str) else name()); i = max(0, int((t0 - lead) * SR))
        if i < N: snd = snd[:N - i]; fx[i:i + len(snd)] += snd * g
    vo = np.zeros(N)
    if voice:
        v = read_mono(voice); vo[:min(len(v), N)] = v[:N]
    bed = np.zeros(N)
    if music:
        m = read_mono(music); reps = int(np.ceil(N / max(len(m), 1))); m = np.tile(m, reps)[:N]
        fade = np.minimum(np.arange(N) / (2 * SR), 1) * np.minimum((N - np.arange(N)) / (2 * SR), 1)
        if voice:
            hop = 441; e = np.array([np.sqrt((vo[i:i + hop] ** 2).mean()) for i in range(0, N, hop)]); e = np.convolve(e / (e.max() + 1e-9), np.ones(25) / 25, 'same')
            g = np.repeat(1 - duck * np.clip(e * 4, 0, 1), hop)[:N]; g = np.pad(g, (0, N - len(g)), constant_values=1); m = m * g
        bed = m * music_gain * fade
    o = vo * voice_gain + fx * sfx_gain + bed
    o = np.tanh(o * 1.05) / np.tanh(1.05); o = o / max(abs(o).max(), 1e-6) * 0.92
    wavfile.write(out, SR, (o * 32767).astype(np.int16)); return out
