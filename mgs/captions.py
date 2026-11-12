# Copyright 2026 Tecnodev Studio. Licensed under the Apache License 2.0 (see LICENSE).
"""captions.py - subtitle export (SRT/VTT for platform upload) and on-screen captions: phrase pill or word-synced karaoke."""
from . import kit as K
from .kit import blit, txt, rrect, eo3, cl

def _ts(t, sep=','):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); sec, ms = divmod(ms, 1000)
    return f'{h:02d}:{m:02d}:{sec:02d}{sep}{ms:03d}'

def write_srt(timing, path, fix=lambda s: s):
    with open(path, 'w', encoding='utf-8') as f:
        for i, p in enumerate(timing['phrases'], 1): f.write(f"{i}\n{_ts(p['start'])} --> {_ts(p['end'])}\n{fix(p['text'])}\n\n")
def write_vtt(timing, path, fix=lambda s: s):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('WEBVTT\n\n')
        for p in timing['phrases']: f.write(f"{_ts(p['start'], '.')} --> {_ts(p['end'], '.')}\n{fix(p['text'])}\n\n")

def draw_phrase(cv, timing, t, style, fix=lambda s: s):
    """whole-phrase caption pill with a quick slide-up. style: pill, ink, size, y (fraction of height), rtl."""
    for p in timing['phrases']:
        if p['start'] - 0.03 <= t <= p['end'] + 0.14:
            x = (t - p['start'] + 0.03) / 0.14
            spr = K.subtitle_sprite(fix(p['text']), tuple(style['pill']), tuple(style['ink']), style.get('size', 54), int(cv.shape[1] * .87), style.get('rtl', True))
            blit(cv, spr, cv.shape[1] / 2, cv.shape[0] * style.get('y', .805) + (1 - eo3(x)) * 22, cl(x * 1.4)); return

def draw_karaoke(cv, timing, t, style, fix=lambda s: s):
    """word-synced captions: the current word is highlighted (accent colour + slight scale) inside a pill showing the whole phrase.
    Uses exact word times when the timing file has them, estimated otherwise."""
    size = style.get('size', 54); rtl = style.get('rtl', True); maxw = cv.shape[1] * .86
    for p in timing['phrases']:
        if not (p['start'] - 0.03 <= t <= p['end'] + 0.14): continue
        words = p.get('words') or []
        if not words: return draw_phrase(cv, timing, t, style, fix)
        ws = [fix(w[0]) for w in words]
        lines, cur, cw = [], [], 0; gap = size * .3
        for i, w in enumerate(ws):
            wv = txt(w, size, tuple(style['ink']), rtl).shape[1] - 24
            if cur and cw + wv + gap > maxw: lines.append(cur); cur, cw = [], 0
            cur.append((i, w, wv)); cw += wv + gap
        lines.append(cur)
        lh = size * 1.3; ph = len(lines) * lh + 40; pw = max(sum(wv for _, _, wv in ln) + gap * (len(ln) - 1) for ln in lines) + 70
        cy = cv.shape[0] * style.get('y', .805); x_in = (t - p['start'] + 0.03) / 0.14
        cy += (1 - eo3(x_in)) * 22; a = cl(x_in * 1.4)
        blit(cv, rrect(int(pw), int(ph), 36, tuple(style['pill']), 235), cv.shape[1] / 2, cy, a)
        cur_i = max([i for i, w in enumerate(words) if w[1] <= t] or [0])
        y = cy - ph / 2 + 20 + lh / 2
        for ln in lines:
            total = sum(wv for _, _, wv in ln) + gap * (len(ln) - 1); x = cv.shape[1] / 2 + (total / 2 if rtl else -total / 2)
            for i, w, wv in ln:
                hot = i == cur_i; col = tuple(style['accent'] if hot else style['ink'])
                xc = x - wv / 2 if rtl else x + wv / 2
                blit(cv, txt(w, size, col, rtl), xc, y, a, 1.12 if hot else 1.0)
                x += -(wv + gap) if rtl else (wv + gap)
            y += lh
        return
