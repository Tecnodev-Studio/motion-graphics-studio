# Copyright 2026 Tecnodev Studio. Licensed under the Apache License 2.0 (see LICENSE).
"""python -m mgs <command> ... (see README). Commands: init, align, stills, audio, render, mux, check, captions, all, doctor"""
import argparse, os, sys, json, shutil, subprocess

def doctor():
    ok = True
    for tool in ('ffmpeg', 'ffprobe'):
        p = shutil.which(tool); print(f'{tool}:', p or 'MISSING (install ffmpeg: free, https://ffmpeg.org)'); ok &= bool(p)
    try:
        import numpy, cv2, PIL, scipy; from . import kit
        print('python libs: ok | raqm (Arabic shaping):', kit.has_raqm(), '| font:', kit.font_path()); ok &= kit.has_raqm()
    except Exception as e: print('python libs problem:', e); ok = False
    print('cpu cores:', os.cpu_count()); return 0 if ok else 1

def main(argv=None):
    ap = argparse.ArgumentParser(prog='mgs'); sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('doctor'); s = sub.add_parser('init'); s.add_argument('dir'); s.add_argument('--template', default='compare')
    s = sub.add_parser('align'); s.add_argument('voice'); s.add_argument('phrases'); s.add_argument('out'); s.add_argument('--words'); s.add_argument('--noise', type=float, default=-33); s.add_argument('--gap', type=float, default=0.16)
    for c in ('stills', 'audio', 'render', 'mux', 'check', 'captions', 'all'):
        s = sub.add_parser(c); s.add_argument('project')
        if c == 'stills': s.add_argument('times', type=float, nargs='+'); s.add_argument('--out', default='sheet.png')
        if c in ('render', 'all'): s.add_argument('--workers', type=int); s.add_argument('--detach', action='store_true'); s.add_argument('--crf', type=int, default=20)
        if c in ('mux', 'all'): s.add_argument('--loudnorm', action='store_true'); s.add_argument('--out', default='out.mp4')
    a = ap.parse_args(argv)
    if a.cmd == 'doctor': return doctor()
    if a.cmd == 'init':
        src = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'examples', a.template, 'project.py')
        if not os.path.exists(src): sys.exit(f'unknown template {a.template}')
        os.makedirs(a.dir, exist_ok=True); shutil.copy(src, os.path.join(a.dir, 'project.py')); print('created', a.dir + '/project.py'); return 0
    from . import align as AL
    if a.cmd == 'align':
        phrases = [l.strip() for l in open(a.phrases, encoding='utf-8') if l.strip()]
        words = json.load(open(a.words, encoding='utf-8')) if a.words else None
        T = AL.build_timing(a.voice, phrases, words, a.noise, a.gap); AL.save(T, a.out)
        print(T['method'], f"{T['duration']:.1f}s", len(phrases), 'phrases')
        for i, p in enumerate(T['phrases'], 1): print(i, round(p['start'], 2), round(p['end'], 2), p['text'][:46])
        return 0
    from . import engine as E
    path = os.path.abspath(a.project)
    if a.cmd == 'render' and a.detach:
        args = [sys.executable, '-m', 'mgs', 'render', path] + (['--workers', str(a.workers)] if a.workers else []) + ['--crf', str(a.crf)]
        kw = dict(creationflags=0x00000008 | 0x00000200) if sys.platform == 'win32' else dict(start_new_session=True)
        p = subprocess.Popen(args, stdout=open('render.log', 'w'), stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, **kw)
        print(f'rendering in the background (pid {p.pid}); follow with: tail -f render.log   (re-run the same command to resume after an interruption)'); return 0
    pr = E.load_project(path)
    if a.cmd == 'stills': print(pr.stills(a.times, a.out))
    elif a.cmd == 'audio': print(pr.build_audio())
    elif a.cmd == 'render': E.render(path, workers=a.workers, crf=a.crf)
    elif a.cmd == 'mux': print(E.mux(pr, out=a.out, loudnorm=a.loudnorm))
    elif a.cmd == 'captions': pr.export_captions(); print('captions.srt / captions.vtt')
    elif a.cmd == 'check':
        w = E.check(pr, 'out.mp4'); print('\n'.join('WARNING: ' + x for x in w) or 'all checks passed'); return 1 if w else 0
    elif a.cmd == 'all':
        pr.build_audio(); E.render(path, workers=a.workers, crf=a.crf); E.mux(pr, out=a.out, loudnorm=a.loudnorm)
        w = E.check(pr, a.out); print('\n'.join('WARNING: ' + x for x in w) or 'all checks passed')
    return 0

if __name__ == '__main__': sys.exit(main())
