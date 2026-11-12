#!/usr/bin/env python3
# Copyright 2026 Tecnodev Studio. Licensed under the Apache License 2.0 (see LICENSE).
"""Self-test: python tests/selftest.py   (about 2-4 minutes on one core). Exits non-zero on any failure. Needs only ffmpeg + the python libs."""
import os, sys, shutil, subprocess, tempfile, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT)
import numpy as np
from scipy.io import wavfile
FAILS = []
def ok(name, cond, extra=''):
    print(('PASS ' if cond else 'FAIL ') + name + (f'  {extra}' if extra and not cond else '')); 
    if not cond: FAILS.append(name)

from mgs import kit as K, fx, transitions as T, components as C, audio as A, align as AL, captions as CP, engine as E

# ---- units
ok('easing stays in range', all(0 <= f(x / 10) <= 1.2 for f in (K.eo3, K.eio, K.smooth, K.eob) for x in range(-2, 13)))
ok('pop starts hidden', K.pop(0, 1) == (0.0, 0.0))
ok('contrast dark-on-cream >= 4.5', K.contrast((26, 20, 18), (241, 233, 223)) >= 4.5)
ok('contrast detects bad pair', K.contrast((200, 200, 200), (255, 255, 255)) < 4.5)
ok('raqm available (Arabic shaping)', K.has_raqm())
ok('rrect survives zero size (pop start)', K.rrect(0, 0, 10, (0, 0, 0)).shape[0] >= 4)
sa = K.safe_area(); ok('safe area sensible', all(v > 0 for v in sa))
K.set_canvas(1080, 1920)
a = K.solid_bg((20, 30, 40)); b = K.solid_bg((200, 180, 160))
ok('all transitions', all(f(a.copy(), b.copy(), .5).shape == a.shape for f in T.TRANSITIONS.values()))
cv = K.radial_bg((241, 233, 223), (242, 195, 166))
try:
    C.bar_chart(cv, [('A', 3), ('B', 7)], 2, 0, (540, 800, 800, 500), (0, 0, 0), (230, 230, 230), [(200, 100, 50)]); C.bar_chart(cv, [('A', 3), ('B', 7)], 2, 0, (540, 800, 800, 500), (0, 0, 0), (230, 230, 230), [(200, 100, 50)], horizontal=True)
    C.line_chart(cv, [1, 3, 2, 5], 2, 0, 1, (540, 500, 700, 300), (200, 100, 50), (100, 100, 100)); C.kinetic_text(cv, 'one two three four five six'.split(), 2, 0, 540, 300, 70, (0, 0, 0), accent={1}, accent_color=(200, 0, 0))
    C.counter(cv, 0, 99, 2, 0, 1, 540, 200, 90, (0, 0, 0)); C.confetti(cv, 1, 0, [(200, 0, 0)]); C.speed_lines(cv, .3, 0, 1, (0, 0, 0)); C.lightning(cv, (10, 10), (900, 900), .3, 0, 1, (0, 200, 255))
    C.stroke_draw(cv, [(10, 10), (400, 300)], 1, 0, 1, (0, 0, 0)); C.lower_third(cv, 'a', 'b', 1, 0, 3, 540, 1300, (255, 255, 255), (0, 0, 0), (200, 100, 50)); C.logo_reveal(cv, 'LOGO', 1, 0, 540, 700, 120, (0, 0, 0), (200, 100, 50)); C.progress_ring(cv, 540, 900, 100, .6, (200, 100, 50), (230, 230, 230))
    ok('all components draw', True)
except Exception as ex: ok('all components draw', False, repr(ex))
try:
    fx.Grain()(cv, 0, 0); fx.Vignette()(cv); fx.bloom(cv); fx.shake(cv, .1, 0); fx.punch_zoom(cv, 1.1); fx.grade(cv, tint=(1, .9, .9)); fx.chroma_split(cv); fx.flash(cv, .05, 0); ok('all fx run', True)
except Exception as ex: ok('all fx run', False, repr(ex))
ok('all sfx synthesize', all(len(f()) > 100 and np.isfinite(f()).all() for f in A.SFX.values()))

# ---- video footage layer
tmpv = tempfile.mkdtemp(prefix='mgs_vid_'); clip = os.path.join(tmpv, 'clip.mp4')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'testsrc=size=320x240:rate=15:duration=2', '-pix_fmt', 'yuv420p', clip], check=True)
try:
    vl = K.VideoLayer(clip); cvv = K.solid_bg((0, 0, 0)); vl.fill(cvv, 0.5); a1 = cvv.mean(); vl.draw(cvv, 1.0, 540, 900, 500, 300); vl.fill(cvv, 3.1)
    ok('video layer fill/draw/loop', a1 > 5 and abs(vl.duration - 2.0) < .2)
except Exception as ex: ok('video layer fill/draw/loop', False, repr(ex))
shutil.rmtree(tmpv, ignore_errors=True)
# ---- init command
tmpi = tempfile.mkdtemp(prefix='mgs_init_'); r = subprocess.run([sys.executable, '-m', 'mgs', 'init', os.path.join(tmpi, 'x'), '--template', 'whiteboard'], capture_output=True, text=True, env=dict(os.environ, PYTHONPATH=ROOT))
ok('init command copies template', r.returncode == 0 and os.path.exists(os.path.join(tmpi, 'x', 'project.py')), r.stderr[-200:]); shutil.rmtree(tmpi, ignore_errors=True)

# ---- timing / captions on synthetic speech
tmp = tempfile.mkdtemp(prefix='mgs_test_'); sr = 44100
burst = lambda d, f: np.sin(2 * np.pi * f * np.arange(int(sr * d)) / sr) * 0.5; sil = np.zeros(int(sr * .4))
wav = os.path.join(tmp, 'syn.wav'); wavfile.write(wav, sr, (np.concatenate([burst(1.2, 200), sil, burst(.8, 220), sil, burst(1.6, 180)]) * 32767).astype(np.int16))
Tm = AL.build_timing(wav, ['one two three', 'four five', 'six seven eight nine'])
ok('align finds 3 phrases in order', len(Tm['phrases']) == 3 and Tm['phrases'][0]['end'] < Tm['phrases'][1]['start'] < Tm['phrases'][2]['start'])
ok('align timing close to truth', abs(Tm['phrases'][1]['start'] - 1.6) < .1 and abs(Tm['phrases'][2]['end'] - 4.4) < .15)
ok('word estimates cover phrase', abs(Tm['phrases'][0]['words'][-1][2] - Tm['phrases'][0]['end']) < .01)
W2 = AL.build_timing(wav, ['a b', 'c d e'], words=[{'word': w, 'start': i * .5, 'end': i * .5 + .4} for i, w in enumerate('a b c d e'.split())])
ok('exact word timings accepted', W2['method'] == 'word-timings' and W2['phrases'][1]['words'][0][0] == 'c')
try: AL.build_timing(wav, ['a'] * 9); ok('too many phrases raises a clear error', False)
except ValueError: ok('too many phrases raises a clear error', True)
CP.write_srt(Tm, os.path.join(tmp, 't.srt')); CP.write_vtt(Tm, os.path.join(tmp, 't.vtt'))
srt = open(os.path.join(tmp, 't.srt'), encoding='utf-8').read(); ok('SRT format', '00:00:00,000 --> 00:00:01,200' in srt and srt.startswith('1\n'))
ok('VTT format', open(os.path.join(tmp, 't.vtt'), encoding='utf-8').read().startswith('WEBVTT'))
ok('beat detector runs', isinstance(A.detect_beats(wav), list))
m = A.mix([(.5, 'pop', .4)], 3.0, voice=wav, music=wav, out=os.path.join(tmp, 'm.wav')); ok('audio mix with ducking', os.path.exists(m))

# ---- every example, end to end (tiny duration), then parallel + resume + detach
env = dict(os.environ, MGS_DURATION='1.5', PYTHONPATH=ROOT)
for name in sorted(os.listdir(os.path.join(ROOT, 'examples'))):
    src = os.path.join(ROOT, 'examples', name)
    if not os.path.isdir(src): continue
    d = os.path.join(tmp, name); shutil.copytree(src, d)
    t0 = time.time(); r = subprocess.run([sys.executable, '-m', 'mgs', 'all', os.path.join(d, 'project.py'), '--out', 'out.mp4'], cwd=d, env=env, capture_output=True, text=True)
    good = r.returncode == 0 and os.path.exists(os.path.join(d, 'out.mp4'))
    ok(f'example {name}: render+audio+mux ({time.time() - t0:.0f}s)', good, (r.stderr or r.stdout)[-300:])
    if good:
        info = E.probe(os.path.join(d, 'out.mp4')); dur = float(info['format']['duration'])
        ok(f'example {name}: duration ~1.5s and has audio', abs(dur - 1.5) < .15 and any(s['codec_type'] == 'audio' for s in info['streams']))
name = 'compare'; d = os.path.join(tmp, name)
r = subprocess.run([sys.executable, '-m', 'mgs', 'captions', os.path.join(d, 'project.py')], cwd=d, env=env, capture_output=True, text=True)
ok('captions export', r.returncode == 0 and os.path.exists(os.path.join(d, 'captions.srt')), r.stderr[-200:])
env2 = dict(env, MGS_DURATION='2'); shutil.rmtree(os.path.join(d, 'mgs_chunks'), ignore_errors=True)
code = f"import sys; sys.path.insert(0, r'{ROOT}'); from mgs import engine as E; E.render(r'{os.path.join(d, 'project.py')}', 'par.mp4', workers=2, chunk=20)"
r = subprocess.run([sys.executable, '-c', code], cwd=d, env=env2, capture_output=True, text=True)
ok('parallel render (2 workers, 3 chunks)', r.returncode == 0 and os.path.exists(os.path.join(d, 'par.mp4')), r.stderr[-300:])
t0 = time.time(); r = subprocess.run([sys.executable, '-c', code], cwd=d, env=env2, capture_output=True, text=True)
ok('resume skips finished chunks', r.returncode == 0 and time.time() - t0 < 8, f'{time.time() - t0:.1f}s')
r = subprocess.run([sys.executable, '-m', 'mgs', 'doctor'], capture_output=True, text=True, env=env); ok('doctor command', r.returncode == 0, r.stdout[-200:])
shutil.rmtree(tmp, ignore_errors=True)
print('\n' + ('ALL TESTS PASSED' if not FAILS else f'{len(FAILS)} FAILED: {FAILS}')); sys.exit(1 if FAILS else 0)
