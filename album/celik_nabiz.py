#!/usr/bin/env python3
"""
ALBUM PILOT 3 - "Celik Nabiz" (Steel Pulse)
Driving industrial techno, 130 BPM, E minor. No piano / pads / plucks.
Tight kick, rolling 16th bass, toms + metal percussion, dark one-note riff,
whispered human chops.  Reuses the engine in gear_heart.py.

  python3 celik_nabiz.py --out OUTDIR [--stems]
"""
import argparse, os
import numpy as np
from scipy import signal
import gear_heart as gh

SR = gh.SR
BPM = 130
BEAT = 60.0 / BPM
BARS = 176
N = int((BARS * 4 * BEAT + 6.0) * SR)
gh.BPM, gh.BEAT, gh.BARS, gh.N = BPM, BEAT, BARS, N
rng = np.random.default_rng(130)
tarr, spos, mtof, vg = gh.tarr, gh.spos, gh.mtof, gh.vg
sos_filt, norm, place, placeS = gh.sos_filt, gh.norm, gh.place, gh.placeS


# ---------------------------------------------------------------- sounds
def tight_kick():
    n = int(0.32 * SR); t = tarr(n)
    f = 52 + 190 * np.exp(-t / 0.018) + 18 * np.exp(-t / 0.1)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * (1 - np.exp(-t / 0.0012)) * np.exp(-t / 0.115)
    y = np.tanh(3.0 * y)
    y += 0.3 * sos_filt(rng.standard_normal(n), "highpass", 3000, 2) * np.exp(-t / 0.0015)
    y *= np.clip((n - np.arange(n)) / (0.03 * SR), 0, 1)
    return norm(sos_filt(y, "highpass", 26, 2), 0.95).astype(np.float32)


def tom(f0):
    n = int(0.35 * SR); t = tarr(n)
    f = f0 * (0.62 + 0.55 * np.exp(-t / 0.05))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.11) * (1 - np.exp(-t / 0.002))
    y += 0.25 * sos_filt(rng.standard_normal(n), "bandpass", [800, 3000], 2) * np.exp(-t / 0.01)
    return norm(np.tanh(1.6 * y), 0.9).astype(np.float32)


def grind():
    n = int(0.12 * SR); t = tarr(n)
    y = sos_filt(rng.standard_normal(n), "bandpass", [700, 3200], 2) * np.exp(-t / 0.04)
    return norm(np.tanh(2 * y), 0.8).astype(np.float32)


def anvil(f0=196.0):
    n = int(1.6 * SR); t = tarr(n)
    idx = 6 * np.exp(-t / 0.08)
    y = np.sin(2 * np.pi * f0 * t + idx * np.sin(2 * np.pi * f0 * 2.76 * t))
    y += 0.5 * np.sin(2 * np.pi * f0 * 1.4142 * t) * np.exp(-t / 0.2)
    y *= np.exp(-t / 0.4) * (1 - np.exp(-t / 0.001))
    return norm(sos_filt(y, "highpass", 120, 2), 0.85).astype(np.float32)


def bass_note(f0, dur_s):
    n = int((dur_s + 0.02) * SR); t = tarr(n)
    ph = 2 * np.pi * f0 * t
    y = np.sin(ph) + 0.45 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph)
    y = np.tanh(2.4 * y)
    env = np.minimum(t / 0.003, 1) * np.clip((dur_s + 0.02 - t) / 0.02, 0, 1)
    return (y * env * 0.6).astype(np.float32)


# ----------------------------------------------------------- arrangement
LAYERS = {
    "kick":   [(8, 64), (80, 160), (160, 168)],
    "bass":   [(24, 64), (80, 160)],
    "hat_c":  [(4, 64), (80, 168)],
    "hat_o":  [(16, 64), (80, 168)],
    "clap":   [(32, 64), (96, 160)],
    "rim":    [(20, 64), (80, 160)],
    "tom":    [(16, 64), (80, 160)],
    "grind":  [(2, 64), (64, 80), (80, 164)],
    "clank":  [(12, 80), (96, 164)],
    "stab":   [(40, 64), (88, 160)],
    "anvil":  [(64, 80), (112, 128)],
    "chops":  [(64, 80), (112, 128), (136, 160)],
    "riser":  [(28, 32), (76, 80), (124, 128)],
    "roll":   [(30, 32), (78, 80), (126, 128)],
    "crash":  [(32, 33), (80, 81), (128, 129)],
}
PATS = {
    "a": [0, None, None, 0, None, None, 3, None, 0, None, 7, None, None, 0, None, None],
    "b": [0, None, 0, None, None, 0, None, 5, 0, None, None, 3, None, 0, 10, None],
    "c": [0, 0, None, 0, None, None, 7, None, 0, None, 0, None, 5, None, 3, None],
}
CLANK_NOTES = [52, 55, 59, 64, 57]


def act(l, bar): return any(a <= bar < b for a, b in LAYERS[l])


def build_events():
    keys = ["kick", "clap", "hat_c", "hat_o", "rim", "tom", "grind", "bass", "stab", "clank",
            "chops", "roll", "anvil"]
    ev = {k: [] for k in keys}
    r = np.random.default_rng(3)
    for bar in range(BARS):
        b0 = bar * 4
        if act("kick", bar):
            for i in range(4): ev["kick"].append((b0 + i, 0.25, 36, 124))
        if act("clap", bar):
            for i in (1, 3): ev["clap"].append((b0 + i, 0.25, 39, 108))
        if act("hat_c", bar):
            for i in range(4):
                ev["hat_c"].append((b0 + i + 0.25, 0.1, 42, 56 + int(r.integers(0, 14))))
                ev["hat_c"].append((b0 + i + 0.75, 0.1, 42, 72 + int(r.integers(0, 14))))
        if act("hat_o", bar):
            for i in range(4): ev["hat_o"].append((b0 + i + 0.5, 0.25, 46, 96))
        if act("rim", bar):
            for st in (3, 6, 11, 14): ev["rim"].append((b0 + st * 0.25, 0.1, 37, 84))
        if act("tom", bar):
            pat = [(2, 47), (5, 45), (7, 50), (10, 47), (13, 45)] if bar % 2 == 0 else [(2, 47), (6, 50), (9, 45), (13, 47)]
            for st, p in pat: ev["tom"].append((b0 + st * 0.25, 0.2, p, 80))
            if bar % 8 == 7:   # tom fill
                for k, st in enumerate(range(8, 16)):
                    ev["tom"].append((b0 + st * 0.25, 0.2, (50, 47, 45)[k % 3], 70 + k * 5))
        if act("grind", bar):
            gate = "x.xx.x.xx.x.xx.x" if bar % 2 == 0 else "x..x.xx.x.x..xx."
            for st, c in enumerate(gate):
                if c == "x": ev["grind"].append((b0 + st * 0.25, 0.1, 56, 40 + 22 * (st % 2) + int(r.integers(0, 14))))
        if act("bass", bar):
            alt = 31 if bar % 4 == 3 else 28
            for i in range(4):
                ev["bass"].append((b0 + i + 0.25, 0.2, 28, 78))
                ev["bass"].append((b0 + i + 0.5, 0.2, alt if i == 3 else 28, 112))
                if not (i == 3 and bar % 2 == 1):
                    ev["bass"].append((b0 + i + 0.75, 0.2, 28, 88))
        if act("stab", bar):
            pat = PATS["a" if bar < 64 else ("b" if (bar // 8) % 2 == 0 else "c")]
            for st, off in enumerate(pat):
                if off is None: continue
                ev["stab"].append((b0 + st * 0.25, 0.2, 40 + off, 112 if st % 4 == 0 else 86))
        if act("clank", bar):
            for k, st in enumerate([0, 3, 6, 9, 12, 14]):
                ev["clank"].append((b0 + st * 0.25, 0.2, CLANK_NOTES[(k + bar) % 5], 80 if k % 2 == 0 else 62))
        if act("anvil", bar) and bar % 2 == 0:
            ev["anvil"].append((b0, 1.5, 55 if (bar // 2) % 2 == 0 else 52, 108))
        if act("chops", bar):
            for k, st in enumerate([3, 7, 10, 14] if bar % 2 == 0 else [2, 6, 11, 15]):
                ev["chops"].append((b0 + st * 0.25, 0.2, 52 + (3 if k % 2 else 0), 88 - 6 * (k % 3)))
        if act("roll", bar):
            first = [s for s, e in LAYERS["roll"] if s <= bar < e][0]
            last = bar == [e for s, e in LAYERS["roll"] if s == first][0] - 1
            if not last:
                for st in range(16): ev["roll"].append((b0 + st * 0.25, 0.1, 38, 55 + int(st * 3.2)))
            else:
                for st in range(32): ev["roll"].append((b0 + st * 0.125, 0.06, 38, 70 + int(st * 1.8)))
    return ev


def render(ev, stems_dir=None):
    z = lambda: np.zeros(N, np.float32)
    kb, bb, cb, hb, rb, tb, gb, stb, chopb, fx, breath, anb = (z() for _ in range(12))
    clL, clR = z(), z()
    kick, clap, snr = tight_kick(), gh.make_clap(), gh.make_snare()
    hat_c, hat_o, tick = gh.make_hat(True), gh.make_hat(False), gh.make_tick()
    toms = {p: tom(mtof(p) * 2) for p in (45, 47, 50)}
    grindS, anv = grind(), {55: anvil(196), 52: anvil(165)}
    crash_hf, crash_sub = gh.make_crash()
    clanks = {m: gh.make_clank(mtof(m + 24)) for m in CLANK_NOTES}

    print("drums…")
    for b, d, m, v in ev["kick"]: place(kb, spos(b), kick, vg(v))
    starts = [spos(b) for b, *_ in ev["kick"]]
    for b, d, m, v in ev["clap"]: place(cb, spos(b), clap, vg(v))
    for b, d, m, v in ev["roll"]: place(cb, spos(b), snr, vg(v))
    for b, d, m, v in ev["hat_c"]: place(hb, spos(b), hat_c, vg(v))
    for b, d, m, v in ev["hat_o"]: place(hb, spos(b), hat_o, vg(v))
    for b, d, m, v in ev["rim"]: place(rb, spos(b), tick, vg(v))
    for b, d, m, v in ev["tom"]: place(tb, spos(b), toms[m], vg(v))
    for b, d, m, v in ev["grind"]: place(gb, spos(b), grindS, vg(v))
    for i, (b, d, m, v) in enumerate(ev["clank"]):
        placeS(clL, clR, spos(b), clanks[m], vg(v), pan=-0.6 if i % 2 == 0 else 0.6)
    for b, d, m, v in ev["anvil"]: place(anb, spos(b), anv[m], vg(v))

    print("bass / riff…")
    bcache = {}
    for b, d, m, v in ev["bass"]:
        if m not in bcache: bcache[m] = bass_note(mtof(m), d * BEAT)
        place(bb, spos(b), bcache[m], vg(v))
    for b, d, m, v in ev["stab"]:
        bar = int(b // 4)
        base = 320 + 700 * (0.5 + 0.5 * np.sin(2 * np.pi * bar / 12.0))
        place(stb, spos(b), np.tanh(2.2 * gh.acid_note(mtof(m), d * BEAT, v >= 100, base, q=5.0)), vg(v))
    print("voices / fx…")
    for b, d, m, v in ev["chops"]:
        place(chopb, spos(b), gh.chop(m, ["o", "u", "a"][int(b * 4) % 3]), vg(v))
    for a, e in LAYERS["chops"]:
        place(breath, max(spos(a * 4) - int(0.9 * SR), 0), gh.make_breath(1.3, 1500), 0.5)
    place(breath, spos(168 * 4), gh.make_breath(3.2, 1300), 0.8)
    for a, e in LAYERS["riser"]:
        place(fx, spos(a * 4), gh.make_riser((e - a) * 4 * BEAT), 0.55)
    for a, e in LAYERS["crash"]:
        place(fx, spos(a * 4), crash_hf, 0.4); place(fx, spos(a * 4), crash_sub, 0.5)

    print("sidechain…")
    sc_h, sc_m, sc_s = gh.sidechain(starts, 0.9, 0.09), gh.sidechain(starts, 0.5, 0.10), gh.sidechain(starts, 0.28, 0.10)
    bb *= sc_h; stb *= sc_m; chopb *= sc_s; gb *= sc_s; clL *= sc_s; clR *= sc_s; anb *= sc_s
    out_env = gh.level_ramp(160, 168, 1.0, 0.0)
    for bus in (kb, bb, cb, hb, rb, tb, gb, stb, clL, clR, chopb):
        bus *= out_env

    print("reverbs…")
    irP, irH = gh.make_ir(0.7, 8000, 0.006, 31), gh.make_ir(3.2, 4500, 0.02, 32)
    sendP = sos_filt(0.5 * cb + 0.4 * (clL + clR) + 0.4 * tb + 0.25 * rb, "highpass", 300, 2).astype(np.float32)
    wetP = gh.reverb(sendP, irP)
    sendH = sos_filt(0.8 * anb + 0.5 * chopb + 0.6 * fx + 0.5 * breath + 0.2 * stb, "highpass", 200, 2).astype(np.float32)
    wH = gh.reverb(sendH, irH)
    wH = [w * sc_s for w in wH]

    print("mix…")
    drums_sum = 0.95 * kb
    def mixch(cl, wp, wh):
        return (0.95 * kb + 0.50 * bb + 0.50 * cb + 0.24 * hb + 0.2 * rb + 0.4 * tb + 0.22 * gb + 0.34 * stb
                + 0.3 * cl + 0.3 * chopb + 0.45 * anb + 0.38 * fx + 0.5 * breath + 0.22 * wp + 0.5 * wh)
    ML, MR = mixch(clL, wetP[0], wH[0]), mixch(clR, wetP[1], wH[1])
    if stems_dir:
        os.makedirs(stems_dir, exist_ok=True)
        st = {"kick": (kb, kb), "bass_rolling": (bb, bb), "clap_roll": (cb, cb), "hats": (hb, hb),
              "rim": (rb, rb), "toms": (tb, tb), "grind": (gb, gb), "riff_stab": (stb, stb),
              "metal_clank": (clL, clR), "anvil": (anb, anb), "whisper_chops": (chopb, chopb),
              "fx_breath": (fx + breath, fx + breath), "reverb_return": (wetP[0] + wH[0], wetP[1] + wH[1])}
        for k, (l, r_) in st.items():
            gh.write_wav(os.path.join(stems_dir, f"stem_{k}.wav"), l, r_, normalise=True)
    return ML, MR


def export_midi(ev, d):
    os.makedirs(d, exist_ok=True)
    drums = [(b, dd, p, v) for k in ("kick", "clap", "hat_c", "hat_o", "rim", "tom", "grind", "roll") for b, dd, p, v in ev[k]]
    w = lambda n, tr: gh.write_midi(os.path.join(d, n), tr)
    w("01_drums_GM.mid", [("Drums (GM ch10)", 9, drums)])
    w("02_rolling_bass.mid", [("Bass", 0, ev["bass"])])
    w("03_riff_stab.mid", [("Riff", 0, ev["stab"])])
    w("04_metal_clank.mid", [("Clank", 0, ev["clank"])])
    w("05_anvil.mid", [("Anvil", 0, ev["anvil"])])
    w("06_whisper_chops.mid", [("Chops", 0, ev["chops"])])
    w("00_FULL_ARRANGEMENT.mid", [("Drums", 9, drums), ("Bass", 1, ev["bass"]), ("Riff", 2, ev["stab"]),
                                  ("Clank", 3, ev["clank"]), ("Anvil", 4, ev["anvil"]), ("Chops", 5, ev["chops"])])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--stems", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ev = build_events()
    export_midi(ev, os.path.join(a.out, "midi"))
    L, R = render(ev, os.path.join(a.out, "stems") if a.stems else None)
    L, R = gh.master(L, R)
    gh.write_wav(os.path.join(a.out, "03_celik_nabiz.wav"), L, R, normalise=False)
    print("done", N / SR, "s")
