#!/usr/bin/env python3
"""
ALBUM PILOT - 01 "Disli Kalp" (Gear Heart)
Peak-time / hard techno, 138 BPM, F# minor.  Concept: Machine & Human.

One note list drives both the MIDI export (drag into FL Studio) and the audio
render (demo mix), so they always match.

  python3 gear_heart.py --out OUTDIR [--stems]
"""
import argparse, os, struct
import numpy as np
from scipy import signal

SR = 44100
BPM = 138
BEAT = 60.0 / BPM
BARS = 192
TAIL = 6.0
N = int((BARS * 4 * BEAT + TAIL) * SR)
rng = np.random.default_rng(138)


def tarr(n): return np.arange(n) / SR
def spos(beat): return int(round(beat * BEAT * SR))
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12.0)
def vg(v): return (v / 127.0) ** 1.3


def sos_filt(x, kind, f, order=4):
    sos = signal.butter(order, f, btype=kind, fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def norm(x, peak=1.0):
    m = np.max(np.abs(x))
    return x * (peak / m) if m > 0 else x


def place(bus, pos, x, g=1.0):
    if pos >= len(bus) or pos < 0:
        return
    e = min(len(bus), pos + len(x))
    bus[pos:e] += g * x[: e - pos]


def placeS(bl, br, pos, x, g=1.0, pan=0.0):
    a = (pan + 1) * np.pi / 4
    place(bl, pos, x, g * np.cos(a))
    place(br, pos, x, g * np.sin(a))


# ---------------------------------------------------------------- one-shots
def make_kick():
    n = int(0.44 * SR); t = tarr(n)
    f = 47 + 175 * np.exp(-t / 0.026) + 22 * np.exp(-t / 0.16)
    ph = 2 * np.pi * np.cumsum(f) / SR
    amp = (1 - np.exp(-t / 0.0015)) * np.exp(-t / 0.20)
    body = np.sin(ph) * amp
    body = np.tanh(3.2 * body)
    click = sos_filt(rng.standard_normal(n), "highpass", 2500, 2) * np.exp(-t / 0.0018) * 0.35
    y = body + click
    y *= np.clip((n - np.arange(n)) / (0.04 * SR), 0, 1)
    return norm(sos_filt(y, "highpass", 25, 2), 0.95).astype(np.float32)


def make_clap():
    n = int(0.30 * SR); t = tarr(n)
    env = np.zeros(n)
    for i, off in enumerate([0, 0.010, 0.021]):
        m = t >= off
        env[m] += np.exp(-(t[m] - off) / 0.004)
    m = t >= 0.03
    env[m] += 0.9 * np.exp(-(t[m] - 0.03) / 0.07)
    nz = sos_filt(rng.standard_normal(n), "bandpass", [900, 4200], 2)
    return norm(nz * env, 0.9).astype(np.float32)


def make_snare():
    n = int(0.16 * SR); t = tarr(n)
    nz = sos_filt(rng.standard_normal(n), "bandpass", [1500, 7000], 2) * np.exp(-t / 0.035)
    body = np.sin(2 * np.pi * (185 + 90 * np.exp(-t / 0.02)) * t) * np.exp(-t / 0.05)
    return norm(0.8 * nz + 0.6 * body, 0.9).astype(np.float32)


def make_hat(closed=True):
    n = int((0.09 if closed else 0.34) * SR); t = tarr(n)
    metal = sum(np.sign(np.sin(2 * np.pi * f * t)) for f in
                [205.3, 304.4, 369.6, 522.7, 540.0, 800.0]) / 6
    x = 0.7 * rng.standard_normal(n) + 0.5 * metal
    x = sos_filt(x, "highpass", 7000 if closed else 6000, 4)
    x *= np.exp(-t / (0.022 if closed else 0.10))
    x *= np.clip((n - np.arange(n)) / (0.01 * SR), 0, 1)
    return norm(x, 0.8).astype(np.float32)


def make_clank(f0):
    n = int(0.28 * SR); t = tarr(n)
    idx = 5.0 * np.exp(-t / 0.05)
    y = np.sin(2 * np.pi * f0 * t + idx * np.sin(2 * np.pi * f0 * 1.4142 * t))
    y = y * np.exp(-t / 0.07) * (1 - np.exp(-t / 0.0008))
    return norm(sos_filt(y, "highpass", 400, 2), 0.8).astype(np.float32)


def make_tick():
    n = int(0.03 * SR); t = tarr(n)
    y = sos_filt(rng.standard_normal(n), "bandpass", [2200, 6500], 2) * np.exp(-t / 0.005)
    return norm(y, 0.8).astype(np.float32)


def make_thump(f=58):
    n = int(0.40 * SR); t = tarr(n)
    ff = f * 0.68 + f * 0.4 * np.exp(-t / 0.04)
    y = np.sin(2 * np.pi * np.cumsum(ff) / SR) * np.exp(-t / 0.09) * (1 - np.exp(-t / 0.004))
    y = sos_filt(np.tanh(1.8 * y), "lowpass", 180, 2)
    return norm(y, 0.9).astype(np.float32)


def make_crash():
    n = int(3.2 * SR); t = tarr(n)
    y = sos_filt(rng.standard_normal(n), "highpass", 3500, 4) * np.exp(-t / 0.9)
    sub = np.sin(2 * np.pi * 41 * t) * np.exp(-t / 1.1) * 0.9
    return norm(0.85 * y + 0.0, 0.8).astype(np.float32), norm(sub, 0.9).astype(np.float32)


def make_riser(dur):
    n = int(dur * SR); t = tarr(n); x = t / dur
    f = 180 * (36 ** x)
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = (np.sin(ph) + 0.5 * np.sin(1.5 * ph)) * x ** 2
    nz = sos_filt(rng.standard_normal(n), "highpass", 1800, 2) * x ** 2.5
    y = (0.35 * tone + 0.9 * nz) * np.clip(x * 4, 0, 1)
    y *= np.clip((n - np.arange(n)) / (0.01 * SR), 0, 1)
    return norm(y, 0.85).astype(np.float32)


def make_breath(dur, centre=1800):
    n = int(dur * SR); x = np.linspace(0, 1, n)
    nz = sos_filt(rng.standard_normal(n), "bandpass", [centre * 0.5, centre * 1.8], 2)
    env = np.sin(np.pi * x) ** 2.2
    return norm(nz * env, 0.8).astype(np.float32)


# ------------------------------------------------------- human voice (formant)
VOW = {
    "a": [(800, 80, 1.0), (1150, 90, 0.5), (2900, 120, 0.15), (3500, 130, 0.08)],
    "o": [(450, 70, 1.0), (800, 80, 0.5), (2830, 120, 0.10)],
    "u": [(325, 60, 1.0), (700, 70, 0.4), (2530, 120, 0.08)],
    "e": [(400, 60, 1.0), (1600, 80, 0.4), (2700, 120, 0.12)],
    "i": [(270, 60, 1.0), (2140, 90, 0.35), (2950, 120, 0.15)],
}


def vowel_gain(fr, v):
    g = 0.0
    for fc, bw, a in VOW[v]:
        g = g + a / (1 + ((fr - fc) / bw) ** 2)
    return g


def voice(f0, n, vows, vib_rate=5.3, vib_depth=0.007, vib_delay=0.5, phase0=0.0, hmax_hz=6500):
    t = tarr(n)
    vib = vib_depth * np.sin(2 * np.pi * vib_rate * t + phase0) * np.clip(t / vib_delay, 0, 1)
    drift = 0.0012 * np.sin(2 * np.pi * 0.37 * t + phase0 * 1.7)
    ph = 2 * np.pi * np.cumsum(f0 * (1 + vib + drift)) / SR
    hmax = int(min(hmax_hz / f0, 60))
    out = np.zeros(n)
    p = np.linspace(0, len(vows) - 1, n) if len(vows) > 1 else None
    for h in range(1, hmax + 1):
        amps = [vowel_gain(h * f0, v) / h ** 0.85 for v in vows]
        a = np.interp(p, np.arange(len(vows)), amps) if p is not None else amps[0]
        out += a * np.sin(h * ph)
    return out.astype(np.float32)


_choir_cache = {}


def choir_segment(notes, dur_beats, vows, tail_beats=2.0):
    key = (tuple(notes), dur_beats, tuple(vows))
    if key in _choir_cache:
        return _choir_cache[key]
    n = int((dur_beats + tail_beats) * BEAT * SR)
    L = np.zeros(n, np.float32); R = np.zeros(n, np.float32)
    for k, m in enumerate(notes):
        for j, (cents, pan) in enumerate([(-9, -0.7), (9, 0.7)]):
            f0 = mtof(m) * 2 ** (cents / 1200)
            v = voice(f0, n, vows, phase0=k * 1.3 + j * 2.1)
            v = v / (np.max(np.abs(v)) + 1e-9)
            placeS(L, R, 0, v, 1.0 / np.sqrt(len(notes) * 2) * 1.4, pan)
    x = np.linspace(0, 1, n)
    atk = int(0.9 * SR); rel = int(tail_beats * BEAT * SR)
    env = np.ones(n); env[:atk] = np.linspace(0, 1, atk) ** 2
    env[-rel:] = np.linspace(1, 0, rel) ** 1.5
    # slow swell breathing
    env *= 0.82 + 0.18 * np.sin(2 * np.pi * x * dur_beats / 8)
    L *= env.astype(np.float32); R *= env.astype(np.float32)
    pk = max(np.max(np.abs(L)), np.max(np.abs(R)), 1e-9)
    res = (L / pk, R / pk)
    _choir_cache[key] = res
    return res


def solo_voice(m, dur_beats, vows, vib=True):
    n = int((dur_beats + 1.0) * BEAT * SR)
    L = np.zeros(n, np.float32); R = np.zeros(n, np.float32)
    for cents, pan in [(-6, -0.4), (0, 0.0), (6, 0.4)]:
        v = voice(mtof(m) * 2 ** (cents / 1200), n, vows, vib_depth=0.011, vib_delay=0.35,
                  phase0=cents * 0.2)
        v = v / (np.max(np.abs(v)) + 1e-9)
        placeS(L, R, 0, v, 0.6, pan)
    atk = int(0.12 * SR); rel = int(0.7 * SR)
    env = np.ones(n); env[:atk] = np.linspace(0, 1, atk) ** 1.5
    env[-rel:] = np.linspace(1, 0, rel)
    return (L * env).astype(np.float32), (R * env).astype(np.float32)


_chop_cache = {}


def chop(m, v):
    key = (m, v)
    if key in _chop_cache:
        return _chop_cache[key]
    n = int(0.16 * SR); t = tarr(n)
    y = voice(mtof(m), n, [v], vib_depth=0.002, vib_delay=1.0)
    y = y / (np.max(np.abs(y)) + 1e-9)
    env = (1 - np.exp(-t / 0.004)) * np.exp(-t / 0.075)
    h = sos_filt(rng.standard_normal(n), "bandpass", [1500, 5000], 2) * np.exp(-t / 0.012) * 0.5
    y = (y * env + h) * np.clip((n - np.arange(n)) / (0.02 * SR), 0, 1)
    res = norm(np.tanh(1.5 * y), 0.9).astype(np.float32)
    _chop_cache[key] = res
    return res


# ----------------------------------------------------------- acid / sub synth
def acid_note(f0, dur_s, accent, cut_base, q=7.0):
    n = int((dur_s + 0.03) * SR); t = tarr(n)
    hn = int(min(9000 / f0, 110))
    h = np.arange(1, hn + 1, dtype=np.float32)[:, None]
    fh = h * np.float32(f0)
    fc = (cut_base + (3400 if accent else 2100) * np.exp(-t / 0.075)).astype(np.float32)
    r = fh / fc[None, :]
    mag = 1.0 / np.sqrt((1 - r ** 2) ** 2 + (r / q) ** 2)
    ph = (2 * np.pi * f0 * t).astype(np.float32)
    y = (np.sin(h * ph[None, :]) / h * mag).sum(0)
    env = np.minimum(t / 0.002, 1) * np.exp(-t / (0.16 if accent else 0.11))
    rel = np.clip((dur_s + 0.03 - t) / 0.03, 0, 1)
    y = np.tanh(1.6 * y * env * rel / 4.0)
    return y.astype(np.float32)


def sub_note(f0, dur_s):
    n = int((dur_s + 0.02) * SR); t = tarr(n)
    y = np.sin(2 * np.pi * f0 * t) + 0.35 * np.sin(4 * np.pi * f0 * t)
    y = np.tanh(1.4 * y)
    env = np.minimum(t / 0.004, 1) * np.clip((dur_s + 0.02 - t) / 0.02, 0, 1) * np.exp(-t / 0.5)
    return (y * env).astype(np.float32)


# --------------------------------------------------------------- reverb / fx
def make_ir(t60, lp_hz, predelay=0.012, seed=1):
    r = np.random.default_rng(seed)
    n = int((t60 * 1.15 + predelay) * SR); t = tarr(n)
    out = []
    for c in range(2):
        x = r.standard_normal(n)
        x = sos_filt(x, "lowpass", lp_hz, 2)
        x *= np.exp(-6.9 * t / t60)
        k = int(predelay * SR)
        x = np.concatenate([np.zeros(k), x[:-k]])
        out.append(x / np.sqrt(np.sum(x ** 2)))
    return out


def reverb(x, irs):
    return [signal.oaconvolve(x, ir, mode="full")[: len(x)].astype(np.float32) for ir in irs]


def sidechain(starts, depth, tau):
    g = np.ones(N, np.float32)
    L = int(0.5 * SR); t = np.arange(L) / SR
    curve = (1 - depth * np.exp(-t / tau)).astype(np.float32)
    ramp = np.clip(t / 0.004, 0, 1).astype(np.float32)       # tiny anti-click attack
    curve = 1 - (1 - curve) * ramp
    for s in starts:
        if s >= N: continue
        seg = g[s: s + L]
        np.minimum(seg, curve[: len(seg)], out=seg)
    return g


# -------------------------------------------------------------- arrangement
def R(*ranges):
    return list(ranges)


LAYERS = {
    # name: bar ranges (end exclusive)
    "heart":   R((0, 6), (184, 190)),
    "ticks":   R((2, 186)),
    "kick":    R((8, 63), (80, 112), (112, 176), (176, 184)),
    "rumble":  R((16, 63), (80, 160)),
    "sub":     R((24, 63), (80, 160)),
    "hat_o":   R((16, 63), (80, 168)),
    "hat_c":   R((12, 63), (84, 112), (120, 168)),
    "clap":    R((24, 63), (80, 112), (120, 168)),
    "clank":   R((12, 64), (84, 112), (112, 168)),
    "lead":    R((40, 62), (88, 112), (124, 160)),
    "choir":   R((48, 80), (96, 112), (112, 128), (136, 164), (186, 192)),
    "melody":  R((64, 80), (128, 152)),
    "chops":   R((56, 62), (96, 112), (136, 160)),
    "riser":   R((28, 32), (76, 80), (124, 128)),
    "roll":    R((30, 32), (78, 80), (126, 128)),
    "crash":   R((32, 33), (80, 81), (128, 129), (160, 161)),
}


def act(layer, bar):
    return any(a <= bar < b for a, b in LAYERS[layer])


def level_ramp(a_bar, b_bar, g0, g1):
    e = np.ones(N, np.float32)
    ia, ib = spos(a_bar * 4), spos(b_bar * 4)
    e[ia:ib] = np.linspace(g0, g1, ib - ia)
    e[ib:] = g1
    return e


CHORDS = [  # i - VI - III - VII  (2 bars each)
    [42, 54, 57, 61],   # F#m
    [38, 54, 57, 62],   # D
    [45, 52, 57, 61],   # A
    [40, 52, 56, 59],   # E
]
PATS = {
    "sparse": [0, None, None, 0, None, None, 12, None, 0, None, None, 3, None, None, 0, None],
    "roll":   [0, 0, 12, 0, 0, 3, 0, 12, 0, 0, 7, 0, 0, 5, 3, 0],
    "drive":  [0, 12, 0, 15, 0, 12, 0, 10, 0, 12, 0, 8, 0, 7, 5, 3],
    "phryg":  [0, None, 1, 0, None, 0, 13, None, 0, None, 1, 0, None, 12, None, 8],
}
MELODY = [  # (beat_in_8bar_loop, dur_beats, midi)
    (0, 3, 73), (3, 1, 71), (4, 4, 69),
    (8, 3, 74), (11, 1, 73), (12, 4, 69),
    (16, 3, 76), (19, 1, 74), (20, 4, 73),
    (24, 2, 71), (26, 2, 68), (28, 2, 71), (30, 2, 73),
]
CLANK_STEPS = [0, 3, 6, 9, 12, 14]
CLANK_NOTES = [78, 85, 81, 90, 76, 83]


def lead_pattern(bar):
    if bar < 48: return "sparse"
    if bar < 64: return "roll"
    if bar < 112: return "phryg" if (bar // 8) % 2 else "roll"
    if bar < 128: return "sparse"
    return "drive" if (bar // 8) % 2 == 0 else "phryg"


def build_events():
    ev = {k: [] for k in ["kick", "clap", "hat_c", "hat_o", "tick", "clank", "roll",
                          "sub", "lead", "choir", "melody", "chops", "heart"]}
    r = np.random.default_rng(5)
    for bar in range(BARS):
        b0 = bar * 4
        if act("kick", bar):
            for i in range(4): ev["kick"].append((b0 + i, 0.25, 36, 124))
        if act("clap", bar):
            for i in (1, 3): ev["clap"].append((b0 + i, 0.25, 39, 112))
        if act("hat_o", bar):
            for i in range(4): ev["hat_o"].append((b0 + i + 0.5, 0.25, 46, 100))
        if act("hat_c", bar):
            for i in range(4):
                ev["hat_c"].append((b0 + i + 0.25, 0.1, 42, 58 + int(r.integers(0, 14))))
                ev["hat_c"].append((b0 + i + 0.75, 0.1, 42, 74 + int(r.integers(0, 14))))
        if act("ticks", bar):
            for st in range(16):
                v = [96, 38, 62, 38][st % 4]
                ev["tick"].append((b0 + st * 0.25, 0.1, 37, v))
        if act("clank", bar):
            for k, st in enumerate(CLANK_STEPS):
                pitch = CLANK_NOTES[(k + bar) % len(CLANK_NOTES)]
                ev["clank"].append((b0 + st * 0.25, 0.2, pitch, 84 if k % 2 == 0 else 66))
        if act("sub", bar):
            root = 28 if bar % 8 == 7 else 30
            for i in range(4): ev["sub"].append((b0 + i + 0.5, 0.4, root, 108))
        if act("roll", bar):
            last = bar == [e - 1 for _, e in LAYERS["roll"]][[s for s, _ in LAYERS["roll"]].index(
                max(s for s, e in LAYERS["roll"] if s <= bar))]
            if not last:
                for st in range(16):
                    ev["roll"].append((b0 + st * 0.25, 0.1, 38, 55 + int(st * 3.2)))
            else:
                for st in range(32):
                    ev["roll"].append((b0 + st * 0.125, 0.06, 38, 70 + int(st * 1.8)))
        if act("lead", bar):
            pat = PATS[lead_pattern(bar)]
            for st, off in enumerate(pat):
                if off is None: continue
                acc = st % 4 == 0 or (st % 8 == 6)
                ev["lead"].append((b0 + st * 0.25, 0.22, 42 + off, 112 if acc else 84))
        if act("chops", bar):
            ch = CHORDS[(bar // 2) % 4]
            steps = [3, 6, 10, 11, 14] if bar % 2 == 0 else [2, 5, 9, 10, 13]
            for k, st in enumerate(steps):
                ev["chops"].append((b0 + st * 0.25, 0.2, ch[2 + (k % 2)] + (12 if k == 4 else 0),
                                    100 - 8 * (k % 3)))
        if act("heart", bar):
            for t0 in (0, 2):
                ev["heart"].append((b0 + t0, 0.3, 24, 100))
                ev["heart"].append((b0 + t0 + 0.7, 0.25, 24, 70))
        # chord / melody segments start on even bars
        if act("choir", bar) and bar % 2 == 0:
            ch = CHORDS[(bar // 2) % 4]
            for m in ch: ev["choir"].append((b0, 8, m, 90))
        if act("melody", bar) and bar % 8 == 0:
            for (bt, d, m) in MELODY: ev["melody"].append((b0 + bt, d, m, 100))
    return ev


# ------------------------------------------------------------------- render
def render(ev, stems_dir=None):
    kick_s, clap_s, snr_s = make_kick(), make_clap(), make_snare()
    hat_c, hat_o, tick = make_hat(True), make_hat(False), make_tick()
    thump = make_thump()
    crash_hf, crash_sub = make_crash()
    clanks = {m: make_clank(mtof(m)) for m in CLANK_NOTES}

    z = lambda: np.zeros(N, np.float32)
    kickb, subb, clapb, hatb, tickb, leadb, chopb, heartb = z(), z(), z(), z(), z(), z(), z(), z()
    clankL, clankR = z(), z()
    chL, chR, meL, meR = z(), z(), z(), z()
    fxb, fxsub = z(), z()
    breath = z()

    print("drums…")
    for b, d, m, v in ev["kick"]: place(kickb, spos(b), kick_s, vg(v))
    kick_starts = [spos(b) for b, *_ in ev["kick"]]
    for b, d, m, v in ev["clap"]: place(clapb, spos(b), clap_s, vg(v))
    for b, d, m, v in ev["roll"]: place(clapb, spos(b), snr_s, vg(v))
    for b, d, m, v in ev["hat_c"]: place(hatb, spos(b), hat_c, vg(v))
    for b, d, m, v in ev["hat_o"]: place(hatb, spos(b), hat_o, vg(v))
    for b, d, m, v in ev["tick"]: place(tickb, spos(b), tick, vg(v))
    for i, (b, d, m, v) in enumerate(ev["clank"]):
        placeS(clankL, clankR, spos(b), clanks[m], vg(v), pan=-0.6 if i % 2 == 0 else 0.6)
    for b, d, m, v in ev["heart"]: place(heartb, spos(b), thump, vg(v))

    print("rumble…")
    kick_only = kickb.copy()
    n_ir = int(0.5 * SR); tt = tarr(n_ir)
    ir = sos_filt(rng.standard_normal(n_ir), "lowpass", 110, 4) * np.exp(-tt / 0.15) * (1 - np.exp(-tt / 0.02))
    ir = ir / np.sqrt(np.sum(ir ** 2))
    rum_mask = np.zeros(N, np.float32)
    for a, bb in LAYERS["rumble"]: rum_mask[spos(a * 4): spos(bb * 4)] = 1
    rum_src = np.zeros(N, np.float32)
    for b, d, m, v in ev["kick"]:
        if rum_mask[spos(b)] > 0: place(rum_src, spos(b), kick_s, 1.0)
    rumble = signal.oaconvolve(rum_src, ir)[:N].astype(np.float32)
    rumble = sos_filt(np.tanh(3.0 * rumble / (np.max(np.abs(rumble)) + 1e-9)), "bandpass", [32, 140], 2).astype(np.float32)
    rumble *= sidechain(kick_starts, 1.0, 0.07)
    rumble *= rum_mask

    print("sub / acid…")
    for b, d, m, v in ev["sub"]: place(subb, spos(b), sub_note(mtof(m), d * BEAT), vg(v))
    for b, d, m, v in ev["lead"]:
        bar = int(b // 4)
        base = 380 + 1300 * (0.5 + 0.5 * np.sin(2 * np.pi * bar / 16.0)) + (500 if bar >= 80 else 0)
        place(leadb, spos(b), acid_note(mtof(m), d * BEAT, v >= 100, base), vg(v))
    print("voices…")
    for b, d, m, v in ev["chops"]:
        vow = ["a", "o", "e"][int(b * 4) % 3]
        place(chopb, spos(b), chop(m, vow), vg(v))
    # choir segments (group notes by start beat)
    segs = {}
    for b, d, m, v in ev["choir"]: segs.setdefault((b, d), []).append(m)
    for (b, d), notes in sorted(segs.items()):
        bar = int(b // 4)
        vows = ["u", "o"] if bar < 96 or bar >= 160 else ["o", "a"]
        if bar >= 186: vows = ["u"]
        Lc, Rc = choir_segment(notes, d, vows)
        g = 0.75 if bar < 186 else 0.9
        place(chL, spos(b), Lc, g); place(chR, spos(b), Rc, g)
        if bar % 8 == 0 or bar in (186,):
            br = make_breath(1.3, 1700)
            place(breath, max(spos(b) - int(0.9 * SR), 0), br, 0.5)
    for b, d, m, v in ev["melody"]:
        vows = ["a", "o"] if d >= 3 else ["a"]
        Lm, Rm = solo_voice(m, d, vows)
        place(meL, spos(b), Lm, 0.8); place(meR, spos(b), Rm, 0.8)
    # final breath – the human remains
    place(breath, spos(190 * 4) + int(0.2 * SR), make_breath(2.8, 1400), 0.9)

    print("fx…")
    for a, bb in LAYERS["riser"]:
        dur = (bb - a) * 4 * BEAT
        place(fxb, spos(a * 4), make_riser(dur), 0.55)
    for a, bb in LAYERS["crash"]:
        place(fxb, spos(a * 4), crash_hf, 0.45)
        place(fxsub, spos(a * 4), crash_sub, 0.7)

    # sidechains
    sc_hard = sidechain(kick_starts, 0.85, 0.11)
    sc_mid = sidechain(kick_starts, 0.55, 0.11)
    sc_soft = sidechain(kick_starts, 0.30, 0.10)
    subb *= sc_hard
    leadb *= sc_mid
    chopb *= sc_soft
    chL *= sc_mid; chR *= sc_mid
    meL *= sc_soft; meR *= sc_soft
    clankL *= sc_soft; clankR *= sc_soft
    tickb *= sc_soft
    hatb *= np.minimum(1.0, 0.75 + 0.25 * sc_soft)

    # machine fade in intro / out in outro; ticks swell
    machine_out = level_ramp(176, 186, 1.0, 0.0)
    tick_in = level_ramp(2, 16, 0.25, 1.0)
    tickb *= tick_in
    for bus in (kickb, subb, clapb, hatb, tickb, leadb, chopb, clankL, clankR, rumble):
        bus *= machine_out

    # leads stereo (haas)
    d14 = int(0.014 * SR)
    leadL = leadb
    leadR = np.concatenate([np.zeros(d14, np.float32), leadb[:-d14]])

    print("reverbs…")
    irP = make_ir(0.9, 9000, 0.008, seed=11)
    irH = make_ir(3.6, 6500, 0.025, seed=12)
    send_p = 0.55 * clapb + 0.25 * (clankL + clankR) + 0.18 * leadb + 0.4 * (kickb * 0.0)
    send_p = sos_filt(send_p, "highpass", 250, 2).astype(np.float32)
    wetP = reverb(send_p, irP)
    send_hl = 0.55 * (chL + meL) + 0.5 * chopb + 0.7 * fxb + 0.35 * breath + 0.2 * heartb
    send_hr = 0.55 * (chR + meR) + 0.5 * chopb + 0.7 * fxb + 0.35 * breath + 0.2 * heartb
    send_hl = sos_filt(send_hl, "highpass", 220, 2).astype(np.float32)
    send_hr = sos_filt(send_hr, "highpass", 220, 2).astype(np.float32)
    wetHL = signal.oaconvolve(send_hl, irH[0])[:N].astype(np.float32)
    wetHR = signal.oaconvolve(send_hr, irH[1])[:N].astype(np.float32)
    wetHL *= sc_soft; wetHR *= sc_soft

    print("mix…")
    rum_g = 0.55
    ML = (0.95 * kickb + rum_g * rumble + 0.34 * subb + 0.50 * clapb + 0.26 * hatb + 0.16 * tickb
          + 0.30 * clankL + 0.30 * leadL + 0.38 * chL + 0.40 * meL + 0.30 * chopb
          + 0.38 * fxb + 0.55 * fxsub + 0.28 * breath + 0.55 * heartb + 0.22 * wetP[0] + 0.55 * wetHL)
    MR = (0.95 * kickb + rum_g * rumble + 0.34 * subb + 0.50 * clapb + 0.26 * hatb + 0.16 * tickb
          + 0.30 * clankR + 0.30 * leadR + 0.38 * chR + 0.40 * meR + 0.30 * chopb
          + 0.38 * fxb + 0.55 * fxsub + 0.28 * breath + 0.55 * heartb + 0.22 * wetP[1] + 0.55 * wetHR)

    if stems_dir:
        os.makedirs(stems_dir, exist_ok=True)
        st = {
            "kick": (kickb, kickb), "rumble": (rumble, rumble), "sub": (subb, subb),
            "clap_roll": (clapb, clapb), "hats": (hatb, hatb), "ticks": (tickb, tickb),
            "clank": (clankL, clankR), "acid_lead": (leadL, leadR), "choir": (chL, chR),
            "human_melody": (meL, meR), "vocal_chops": (chopb, chopb),
            "fx_riser_crash": (fxb + fxsub, fxb + fxsub), "breath_heart": (breath + heartb, breath + heartb),
            "reverb_return": (wetP[0] + wetHL, wetP[1] + wetHR),
        }
        for k, (l, r_) in st.items():
            write_wav(os.path.join(stems_dir, f"stem_{k}.wav"), l, r_, normalise=True)
    return ML, MR


def master(L, R):
    x = np.stack([L, R]).astype(np.float64)
    sos = signal.butter(2, 22, "highpass", fs=SR, output="sos")
    x = signal.sosfilt(sos, x, axis=1)
    x = np.tanh(0.85 * x / np.percentile(np.abs(x), 99.9))
    x = x / np.max(np.abs(x)) * 0.89            # -1 dBFS peak
    return x[0].astype(np.float32), x[1].astype(np.float32)


def write_wav(path, L, R, normalise=True, bits=24):
    x = np.stack([L, R], axis=1)
    if normalise: x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    x = np.clip(x, -1, 1)
    i = (x * (2 ** (bits - 1) - 1)).astype(np.int32)
    raw = i.astype("<i4").view(np.uint8).reshape(-1, 4)[:, 0:3].tobytes()
    ch, bps = 2, bits // 8
    with open(path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", 36 + len(raw)) + b"WAVEfmt ")
        f.write(struct.pack("<IHHIIHH", 16, 1, ch, SR, SR * ch * bps, ch * bps, bits))
        f.write(b"data" + struct.pack("<I", len(raw)) + raw)


# --------------------------------------------------------------------- MIDI
def vlq(n):
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.append((n & 0x7F) | 0x80); n >>= 7
    return bytes(reversed(out))


def midi_track(name, channel, notes, ppq=480):
    evs = []
    for b, d, p, v in notes:
        on = int(round(b * ppq)); off = int(round((b + d) * ppq))
        evs.append((on, 1, 0x90 | channel, p, int(v)))
        evs.append((off, 0, 0x80 | channel, p, 0))
    evs.sort(key=lambda e: (e[0], e[1]))
    nm = name.encode()
    data = b"\x00\xff\x03" + vlq(len(nm)) + nm
    last = 0
    for t, _, st, p, v in evs:
        data += vlq(t - last) + bytes([st, p, v]); last = t
    data += b"\x00\xff\x2f\x00"
    return b"MTrk" + struct.pack(">I", len(data)) + data


def write_midi(path, tracks, ppq=480):
    tempo = int(60_000_000 / BPM)
    meta = (b"\x00\xff\x03\x05Tempo" + b"\x00\xff\x51\x03" + tempo.to_bytes(3, "big")
            + b"\x00\xff\x58\x04\x04\x02\x18\x08" + b"\x00\xff\x2f\x00")
    chunks = [b"MTrk" + struct.pack(">I", len(meta)) + meta]
    for i, (name, ch, notes) in enumerate(tracks):
        chunks.append(midi_track(name, ch, notes, ppq))
    hdr = b"MThd" + struct.pack(">IHHH", 6, 1, len(chunks), ppq)
    with open(path, "wb") as f:
        f.write(hdr + b"".join(chunks))


def export_midi(ev, outdir):
    os.makedirs(outdir, exist_ok=True)
    drums = [(b, d, p, v) for k in ("kick", "clap", "hat_c", "hat_o", "tick", "roll") for b, d, p, v in ev[k]]
    write_midi(os.path.join(outdir, "01_drums_GM.mid"), [("Drums (GM ch10)", 9, drums)])
    write_midi(os.path.join(outdir, "02_sub_bass_F#1.mid"), [("Sub bass", 0, ev["sub"])])
    write_midi(os.path.join(outdir, "03_acid_lead.mid"), [("Acid lead", 0, ev["lead"])])
    write_midi(os.path.join(outdir, "04_perc_clank.mid"), [("Metal clank", 0, ev["clank"])])
    write_midi(os.path.join(outdir, "05_choir_chords.mid"), [("Choir chords", 0, ev["choir"])])
    write_midi(os.path.join(outdir, "06_human_melody.mid"), [("Human melody", 0, ev["melody"])])
    write_midi(os.path.join(outdir, "07_vocal_chops.mid"), [("Vocal chops", 0, ev["chops"])])
    write_midi(os.path.join(outdir, "08_heartbeat.mid"), [("Heartbeat", 0, ev["heart"])])
    allt = [("Drums", 9, drums), ("Sub", 1, ev["sub"]), ("Acid", 2, ev["lead"]), ("Clank", 3, ev["clank"]),
            ("Choir", 4, ev["choir"]), ("Melody", 5, ev["melody"]), ("Chops", 6, ev["chops"]),
            ("Heart", 7, ev["heart"])]
    write_midi(os.path.join(outdir, "00_FULL_ARRANGEMENT.mid"), allt)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--stems", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ev = build_events()
    export_midi(ev, os.path.join(a.out, "midi"))
    L, R = render(ev, os.path.join(a.out, "stems") if a.stems else None)
    L, R = master(L, R)
    write_wav(os.path.join(a.out, "01_disli_kalp.wav"), L, R, normalise=False)
    print("done", N / SR, "s")
