# Copyright 2026 Tecnodev Studio. Licensed under the Apache License 2.0 (see LICENSE).
"""engine.py - Project: scenes + overlays + captions + sfx -> frames -> video. Parallel, resumable, offline (needs ffmpeg only)."""
import os, sys, json, math, subprocess, runpy, time, inspect
import numpy as np
from PIL import Image
from . import kit as K, transitions, captions as C, audio as A

DEFAULT_THEME = dict(bg=(241, 233, 223), glow=(242, 195, 166), dark_bg=(23, 20, 21), dark_glow=(92, 52, 30),
                     ink=(26, 20, 18), accent=(217, 130, 75), card=(255, 255, 255), muted=(150, 134, 122), soft=(232, 222, 210))

class Project:
    def __init__(self, size='shorts', fps=30, timing=None, voice=None, duration=None, theme=None, music=None, rtl=True):
        w, h = K.PRESETS[size] if isinstance(size, str) else size
        K.set_canvas(w, h, fps); K.set_rtl(rtl); self.W, self.H, self.fps = w, h, fps
        self.theme = dict(DEFAULT_THEME, **(theme or {})); self.rtl = rtl
        self.timing = json.load(open(timing, encoding='utf-8')) if isinstance(timing, str) else timing
        self.voice, self.music = voice, music
        self.duration = duration or ((self.timing['duration'] + 0.4) if self.timing else None)
        if not self.duration: raise ValueError('give duration= or a timing file')
        if os.environ.get('MGS_DURATION'): self.duration = min(self.duration, float(os.environ['MGS_DURATION']))   # quick preview: MGS_DURATION=5
        self.scenes, self.overlays, self.post, self.events = [], [], [], []
        self.captions, self.caption_style, self.caption_fix = None, None, (lambda s: s)
        self.auto_sfx = True; self._env = None; self._bgc = {}

    # ---- building
    def scene(self, start, bg='light', transition='crossfade', tdur=0.2, tparams=None):
        """decorator: @project.scene(start_time, bg='light'|'dark'|colour|callable)"""
        def deco(fn): self.scenes.append(dict(start=start, fn=fn, bg=bg, tr=transition, td=tdur, tp=tparams or {})); self.scenes.sort(key=lambda s: s['start']); return fn
        return deco
    def overlay(self, fn):
        """fn(cv, t, i) or fn(cv, t, i, env) - env = voice loudness 0..1 (lip-sync / audio-reactive)."""
        try: has_env = len(inspect.signature(fn).parameters) >= 4
        except (TypeError, ValueError): has_env = False
        self.overlays.append((fn, has_env)); return fn
    def add_post(self, fn): self.post.append(fn); return fn              # fn(cv, t, i) -> cv
    def sfx(self, t, name, gain=0.3): self.events.append((t, name, gain))
    def set_captions(self, mode='phrase', pill=None, ink=(255, 255, 255), accent=None, size=54, y=.805, fix=None):
        self.captions = mode; self.caption_fix = fix or self.caption_fix
        self.caption_style = dict(pill=pill or self.theme['dark_bg'], ink=ink, accent=accent or self.theme['accent'], size=size, y=y, rtl=self.rtl)
    def P(self, k): return self.timing['phrases'][k - 1]['start']      # start of phrase k (1-based)
    def PE(self, k): return self.timing['phrases'][k - 1]['end']
    def boundary(self, k): return (self.PE(k - 1) + self.P(k)) / 2      # good scene start: midpoint of the pause before phrase k

    # ---- frames
    def env(self, i):
        if self._env is None:
            self._env = A.envelope(A.read_mono(self.voice), self.fps, int(self.duration * self.fps) + 2) if self.voice else np.zeros(int(self.duration * self.fps) + 2)
        return float(self._env[min(i, len(self._env) - 1)])

    def _bg(self, spec):
        key = spec if isinstance(spec, (str, tuple)) else id(spec)
        if key in self._bgc: return self._bgc[key]
        th = self.theme
        if spec == 'light': b = K.radial_bg(tuple(th['bg']), tuple(th['glow']))
        elif spec == 'dark': b = K.radial_bg(tuple(th['dark_bg']), tuple(th['dark_glow']))
        elif isinstance(spec, tuple): b = K.solid_bg(spec)
        elif callable(spec): b = spec()
        else: b = spec
        self._bgc[key] = b; return b

    def _scene_frame(self, si, t):
        s = self.scenes[si]; cv = self._bg(s['bg']).copy(); s['fn'](cv, t); return cv

    def frame(self, i):
        t = i / self.fps
        idx = max([k for k, s in enumerate(self.scenes) if s['start'] <= t] or [0]); s = self.scenes[idx]
        cv = self._scene_frame(idx, t)
        if idx > 0 and t - s['start'] < s['td'] and s['tr'] != 'cut':
            p = K.eo3((t - s['start']) / s['td']); cv = transitions.TRANSITIONS[s['tr']](self._scene_frame(idx - 1, t), cv, p, **s['tp'])
        for o, has_env in self.overlays:
            o(cv, t, i, self.env(i)) if has_env else o(cv, t, i)
        if self.captions and self.timing:
            (C.draw_karaoke if self.captions == 'karaoke' else C.draw_phrase)(cv, self.timing, t, self.caption_style, self.caption_fix)
        for f in self.post: cv = f(cv, t, i)
        return cv

    def stills(self, times, out='sheet.png', cols=6, w=360):
        h = int(w * self.H / self.W); ims = [Image.fromarray(self.frame(int(t * self.fps))).resize((w, h)) for t in times]
        sheet = Image.new('RGB', (w * cols, h * math.ceil(len(ims) / cols)))
        for k, im in enumerate(ims): sheet.paste(im, ((k % cols) * w, (k // cols) * h))
        sheet.save(out); return out

    # ---- audio / captions
    def build_audio(self, out='final_audio.wav'):
        ev = list(self.events)
        if self.auto_sfx: ev += [(s['start'] - 0.05, 'whoosh', .22) for s in self.scenes[1:]]
        return A.mix(ev, self.duration, self.voice, self.music, out=out)
    def export_captions(self, base='captions'):
        C.write_srt(self.timing, base + '.srt', self.caption_fix); C.write_vtt(self.timing, base + '.vtt', self.caption_fix)

# ------------------------------------------------------------------ rendering (module-level so multiprocessing can import it)
_PROJ = {}
def load_project(path):
    path = os.path.abspath(path)
    if path not in _PROJ:
        sys.path.insert(0, os.path.dirname(path)); os.chdir(os.path.dirname(path))
        ns = runpy.run_path(path); _PROJ[path] = ns['project']
    return _PROJ[path]

def _chunk(args):
    path, a, b, out, crf = args
    if os.path.exists(out + '.done'): return out
    pr = load_project(path); W, H = pr.W, pr.H
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(pr.fps), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', str(crf), '-g', str(pr.fps), '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    fr = None
    for i in range(a, b):
        try: fr = pr.frame(i)
        except Exception as ex:
            print(f'frame {i} failed: {ex!r:.100}', flush=True)       # repeat the previous frame instead of losing the whole render
            if fr is None: fr = np.zeros((H, W, 3), np.uint8)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait(); open(out + '.done', 'w').close(); return out

def render(path, out='silent.mp4', workers=None, crf=20, chunk=150):
    """frames -> video in parallel chunks (resumable: re-run the same command after an interruption)."""
    import multiprocessing as mp
    pr = load_project(path); n = int(pr.duration * pr.fps); wd = 'mgs_chunks'; os.makedirs(wd, exist_ok=True)
    jobs = [(os.path.abspath(path), a, min(a + chunk, n), os.path.join(wd, f'c{a // chunk:04d}.mp4'), crf) for a in range(0, n, chunk)]
    workers = max(1, min(workers or os.cpu_count() or 1, len(jobs))); t0 = time.time(); done = 0
    if workers == 1: it = map(_chunk, jobs)
    else: pool = mp.get_context('spawn' if sys.platform == 'win32' else 'fork').Pool(workers); it = pool.imap(_chunk, jobs)
    for _ in it:
        done += 1; print(f'chunk {done}/{len(jobs)}  {time.time() - t0:.0f}s', flush=True)
    if workers > 1: pool.close(); pool.join()
    lst = os.path.join(wd, 'list.txt'); open(lst, 'w').write(''.join("file '{}'\n".format(os.path.abspath(j[3]).replace('\\', '/').replace("'", "'\\''")) for j in jobs))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', out], check=True)
    print('rendered', out); return out

def mux(pr, silent='silent.mp4', audio='final_audio.wav', out='out.mp4', crf=23, loudnorm=False):
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', silent, '-i', audio, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', str(crf),
           '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-t', f'{pr.duration:.2f}', '-movflags', '+faststart']
    if loudnorm: cmd[cmd.index('-c:a'):cmd.index('-c:a')] = ['-af', 'loudnorm=I=-14:TP=-1.5:LRA=11']
    subprocess.run(cmd + [out], check=True); return out

def probe(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,width,height,r_frame_rate,duration', '-show_entries', 'format=duration,size', '-of', 'json', path],
                       capture_output=True, text=True).stdout
    return json.loads(r)

def check(pr, video='out.mp4', n=12, sheet='check_sheet.png'):
    """sanity report: duration/sync, streams, theme contrast, contact sheet of n frames. Returns list of warnings."""
    info = probe(video); warns = []; streams = {s['codec_type']: s for s in info['streams']}
    if 'audio' not in streams: warns.append('no audio stream')
    dv = float(streams['video'].get('duration', info['format']['duration'])); da = float(streams.get('audio', {}).get('duration', dv))
    if abs(dv - da) > 0.12: warns.append(f'audio/video length differ by {abs(dv - da):.2f}s (sync risk)')
    if abs(dv - pr.duration) > 0.2: warns.append(f'video length {dv:.2f}s != project duration {pr.duration:.2f}s')
    if (streams['video']['width'], streams['video']['height']) != (pr.W, pr.H): warns.append('unexpected video size')
    th = pr.theme
    for nm, a, b in (('ink on bg', th['ink'], th['bg']), ('caption ink on pill', (255, 255, 255), th['dark_bg'])):
        if K.contrast(a, b) < 4.5: warns.append(f'low contrast ({nm}): {K.contrast(a, b):.1f}:1, aim for >= 4.5')
    if not K.has_raqm(): warns.append('PIL has no raqm: Arabic/RTL text will look broken')
    if os.path.getsize(video) > 250e6: warns.append('file > 250 MB: raise crf in mux')
    ts = np.linspace(0.5, pr.duration - 0.5, n); ims = []
    for t in ts:
        tmp = 'mgs_check_tmp.png'; subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{t:.2f}', '-i', video, '-frames:v', '1', '-vf', 'scale=300:-1', tmp], check=True); ims.append(Image.open(tmp).copy())
    if os.path.exists('mgs_check_tmp.png'): os.remove('mgs_check_tmp.png')
    w, h = ims[0].size; cols = min(6, n); S = Image.new('RGB', (w * cols, h * math.ceil(n / cols)))
    for k, im in enumerate(ims): S.paste(im, ((k % cols) * w, (k // cols) * h))
    S.save(sheet); return warns
