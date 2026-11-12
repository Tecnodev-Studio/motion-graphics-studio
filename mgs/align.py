# Copyright 2026 Tecnodev Studio. Licensed under the Apache License 2.0 (see LICENSE).
"""align.py - find WHEN each script phrase is spoken. No speech recognition needed (estimate), exact if you supply word timings.

Method A (default, offline, estimate): ffmpeg silencedetect -> speech segments -> dynamic programming assigns consecutive
segments to phrases so each phrase's duration matches (characters x average speaking rate).
Method B (exact): pass word timings from ANY free tool (e.g. faster-whisper / whisper.cpp) as [{"word","start","end"}].
Always tell the user which method was used. Estimated timing can be off by a word in long run-on phrases.
"""
import json, re, subprocess

def duration(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', path], capture_output=True, text=True).stdout.strip()
    return float(r)

def segments(path, noise=-33, gap=0.16):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', f'silencedetect=noise={noise}dB:d={gap}', '-f', 'null', '-'], capture_output=True, text=True).stderr
    dur = duration(path)
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', r)]; en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', r)]
    seg, cur = [], 0.0
    for s, e in zip(st, en):
        if s > cur + 0.05: seg.append((round(cur, 2), round(s, 2)))
        cur = e
    if cur < dur - 0.2: seg.append((round(cur, 2), round(dur, 2)))
    return seg, dur

def _chars(p): return max(3, len(re.sub(r'[\s\.\,\:\،\"\؟\?\!\؛\;]', '', p)))

def dp_align(segs, phrases):
    ch = [_chars(p) for p in phrases]; dur = [b - a for a, b in segs]; rate = sum(dur) / sum(ch)
    nP, nS = len(phrases), len(segs)
    if nS < nP: raise ValueError(f'only {nS} speech segments for {nP} phrases: merge phrases or lower the gap threshold (--gap 0.12)')
    INF = 1e18; f = [[INF] * (nS + 1) for _ in range(nP + 1)]; bk = [[0] * (nS + 1) for _ in range(nP + 1)]; f[0][0] = 0
    for p in range(1, nP + 1):
        for s in range(p, nS + 1):
            for k in range(p - 1, s):
                if f[p - 1][k] >= INF: continue
                d = sum(dur[k:s]); exp = rate * ch[p - 1]; c = f[p - 1][k] + (d - exp) ** 2 / (exp + 0.3)
                if c < f[p][s]: f[p][s] = c; bk[p][s] = k
    s, groups = nS, []
    for p in range(nP, 0, -1):
        k = bk[p][s]; groups.append((k, s - 1)); s = k
    return groups[::-1]

def split_words(phrase): return [w for w in phrase.split() if w]

def estimate_words(phrase, start, end):
    """spread a phrase's words over its time span proportionally to word length -> [(word, start, end)]. Used for word-synced captions."""
    ws = split_words(phrase); wt = [max(2, len(re.sub(r'[\.\,\:\،\"\؟\?\!]', '', w))) for w in ws]; tot = sum(wt) or 1
    out, t = [], start
    for w, k in zip(ws, wt):
        d = (end - start) * k / tot; out.append((w, round(t, 3), round(t + d, 3))); t += d
    return out

def from_words(phrases, words):
    """exact timing from a word list: phrase k takes the next len(split(phrase)) words. Falls back to proportional split if counts differ."""
    toks = [len(split_words(p)) for p in phrases]; res, i = [], 0
    scale = len(words) / max(sum(toks), 1)
    for p, n in zip(phrases, toks):
        take = max(1, round(n * scale)); chunk = words[i:i + take]; i += take
        if not chunk: chunk = words[-1:]
        res.append({'text': p, 'start': chunk[0]['start'], 'end': chunk[-1]['end'], 'words': [(w['word'], w['start'], w['end']) for w in chunk]})
    return res

def build_timing(voice, phrases, words=None, noise=-33, gap=0.16):
    dur = duration(voice)
    if words:
        ph = from_words(phrases, words); method = 'word-timings'; segs = []
    else:
        segs, dur = segments(voice, noise, gap); groups = dp_align(segs, phrases); method = 'estimated (silence + length matching)'
        ph = [{'text': t, 'start': segs[a][0], 'end': segs[b][1], 'segments': [a, b], 'words': estimate_words(t, segs[a][0], segs[b][1])} for t, (a, b) in zip(phrases, groups)]
    return {'duration': dur, 'method': method, 'segments': segs, 'phrases': ph}

def save(timing, path): json.dump(timing, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
def load(path): return json.load(open(path, encoding='utf-8'))
