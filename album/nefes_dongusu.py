#!/usr/bin/env python3
"""
ALBUM PILOT 2 - "Nefes Dongusu" (Breath Loop)
Minimal / melodic techno, 122 BPM, D minor.  The human side of Machine & Human.
Reuses the engine in gear_heart.py (voices, reverb, MIDI/WAV writers).

  python3 nefes_dongusu.py --out OUTDIR [--stems]
"""
import argparse, os
import numpy as np
import gear_heart as gh

SR = gh.SR
BPM = 122
BEAT = 60.0 / BPM
BARS = 160
N = int((BARS * 4 * BEAT + 6.0) * SR)
gh.BPM, gh.BEAT, gh.BARS, gh.N = BPM, BEAT, BARS, N     # engine globals
rng = np.random.default_rng(122)
tarr, spos, mtof, vg = gh.tarr, gh.spos, gh.mtof, gh.vg
sos_filt, norm, place, placeS = gh.sos_filt, gh.norm, gh.place, gh.placeS


# ---------------------------------------------------------------- sounds
def soft_kick():
    n = int(0.5 * SR); t = tarr(n)
    f = 50 + 105 * np.exp(-t / 0.022)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * (1 - np.exp(-t / 0.002)) * np.exp(-t / 0.17)
    y = np.tanh(1.5 * y) * np.clip((n - np.arange(n)) / (0.05 * SR), 0, 1)
    return norm(sos_filt(y, "highpass", 28, 2), 0.9).astype(np.float32)


def shaker():
    n = int(0.06 * SR); t = tarr(n)
    y = sos_filt(rng.standard_normal(n), "bandpass", [5500, 13000], 2) * np.exp(-t / 0.018)
    y *= np.minimum(t / 0.004, 1)
    return norm(y, 0.8).astype(np.float32)


def soft_clap():
    return sos_filt(gh.make_clap(), "lowpass", 5500, 2).astype(np.float32)


def pluck(f0, dur_s, decay=1.0):
    n = int((dur_s + 0.9) * SR); t = tarr(n)
    hn = int(min(8000 / f0, 26))
    L = np.zeros(n, np.float32); R = np.zeros(n, np.float32)
    for cents, pan in [(-5, -0.45), (5, 0.45)]:
        ff = f0 * 2 ** (cents / 1200)
        ph = 2 * np.pi * ff * t
        y = np.zeros(n, np.float32)
        for h in range(1, hn + 1):
            y += np.sin(h * ph).astype(np.float32) / h * np.exp(-t * (2.2 + 1.1 * h) / decay).astype(np.float32)
        placeS(L, R, 0, y, 1.0, pan)
    env = np.minimum(t / 0.003, 1) * np.clip((n - np.arange(n)) / (0.04 * SR), 0, 1)
    pk = max(np.max(np.abs(L)), 1e-9)
    return (L * env / pk).astype(np.float32), (R * env / pk).astype(np.float32)


_pad_cache = {}


def pad_chord(notes, dur_beats):
    key = (tuple(notes), dur_beats)
    if key in _pad_cache: return _pad_cache[key]
    tail = 2.0
    n = int((dur_beats + tail) * BEAT * SR); t = tarr(n)
    L = np.zeros(n, np.float32); R = np.zeros(n, np.float32)
    for k, m in enumerate(notes):
        for j, (cents, pan) in enumerate([(-12, -0.6), (0, 0.0), (12, 0.6)]):
            f = mtof(m) * 2 ** (cents / 1200)
            ph = 2 * np.pi * f * t
            y = np.zeros(n, np.float32)
            for h in range(1, 8):
                mod = 0.65 + 0.35 * np.sin(2 * np.pi * 0.09 * t + h + k + j)
                y += (np.sin(h * ph + j) / h ** 1.5 * mod).astype(np.float32)
            placeS(L, R, 0, y, 1.0 / np.sqrt(len(notes)), pan)
    atk, rel = int(1.3 * SR), int(tail * BEAT * SR)
    env = np.ones(n, np.float32); env[:atk] = np.linspace(0, 1, atk) ** 2
    env[-rel:] = np.linspace(1, 0, rel) ** 1.5
    pk = max(np.max(np.abs(L)), np.max(np.abs(R)), 1e-9)
    res = (L * env / pk, R * env / pk)
    _pad_cache[key] = res
    return res


def sub_note(f0, dur_s):
    n = int((dur_s + 0.02) * SR); t = tarr(n)
    y = np.sin(2 * np.pi * f0 * t) + 0.25 * np.sin(4 * np.pi * f0 * t)
    env = np.minimum(t / 0.006, 1) * np.clip((dur_s + 0.02 - t) / 0.03, 0, 1) * np.exp(-t / 0.45)
    return (np.tanh(1.2 * y) * env).astype(np.float32)


def pingpong(L, R, beats=(0.75, 1.5, 2.25, 3.0), gains=(0.5, 0.36, 0.25, 0.16)):
    m = sos_filt((L + R) * 0.5, "lowpass", 4200, 2).astype(np.float32)
    oL = np.zeros(N, np.float32); oR = np.zeros(N, np.float32)
    for i, (b, g) in enumerate(zip(beats, gains)):
        d = int(b * BEAT * SR)
        tgt = oL if i % 2 == 0 else oR
        tgt[d:] += g * m[: N - d]
    return oL, oR


# ----------------------------------------------------------- arrangement
LAYERS = {
    "pad":    [(0, 154)],
    "kick":   [(8, 48), (64, 112), (128, 152)],
    "sub":    [(16, 48), (64, 112), (128, 152)],
    "hat_c":  [(4, 48), (64, 112), (120, 152)],
    "hat_o":  [(16, 48), (64, 112), (128, 152)],
    "shaker": [(12, 48), (64, 112), (120, 152)],
    "rim":    [(24, 48), (64, 112), (128, 152)],
    "clap":   [(32, 48), (80, 112), (128, 150)],
    "arp":    [(8, 48), (64, 112), (120, 152)],
    "lead":   [(48, 64), (80, 112), (128, 148)],
    "choir":  [(40, 64), (96, 128), (136, 152), (154, 160)],
    "chops":  [(80, 112), (136, 152)],
    "riser":  [(44, 48), (60, 64), (124, 128)],
    "crash":  [(48, 49), (64, 65), (128, 129)],
}
CHORDS = [[50, 53, 57, 62], [46, 50, 53, 58], [48, 53, 57, 60], [48, 52, 55, 60]]  # Dm Bb F C pad voicings
ARPN = [[62, 65, 69, 74], [58, 62, 65, 70], [60, 65, 69, 72], [60, 64, 67, 72]]
ROOTS = [38, 34, 29, 36]
MELODY = [(0, 1.5, 74), (1.5, 0.5, 72), (2, 2, 69), (4, 1, 65), (5, 3, 69),
          (8, 3, 70), (11, 1, 69), (12, 4, 65),
          (16, 1.5, 72), (17.5, 0.5, 69), (18, 2, 72), (20, 4, 77),
          (24, 2, 76), (26, 2, 72), (28, 2, 67), (30, 2, 71)]
ARP_STEPS = [0, 3, 6, 8, 11, 14]
ARP_IDX = [0, 2, 1, 3, 2, 1]


def act(l, bar): return any(a <= bar < b for a, b in LAYERS[l])


def build_events():
    ev = {k: [] for k in ["kick", "clap", "hat_c", "hat_o", "shaker", "rim", "sub", "arp",
                          "lead", "pad", "choir", "chops"]}
    r = np.random.default_rng(9)
    for bar in range(BARS):
        b0 = bar * 4; ci = (bar // 2) % 4
        if act("kick", bar):
            for i in range(4): ev["kick"].append((b0 + i, 0.25, 36, 118))
        if act("clap", bar):
            for i in (1, 3): ev["clap"].append((b0 + i, 0.25, 39, 88))
        if act("hat_c", bar):
            for i in range(4): ev["hat_c"].append((b0 + i + 0.75, 0.1, 42, 52 + int(r.integers(0, 14))))
        if act("hat_o", bar):
            for i in range(4): ev["hat_o"].append((b0 + i + 0.5, 0.25, 46, 78))
        if act("shaker", bar):
            for st in range(16):
                ev["shaker"].append((b0 + st * 0.25, 0.1, 70, [70, 34, 52, 34][st % 4]))
        if act("rim", bar):
            for st in (3, 7, 11, 14): ev["rim"].append((b0 + st * 0.25, 0.1, 37, 70))
        if act("sub", bar):
            for i in range(4): ev["sub"].append((b0 + i + 0.5, 0.4, ROOTS[ci], 100))
        if act("arp", bar):
            for k, st in enumerate(ARP_STEPS):
                ev["arp"].append((b0 + st * 0.25, 0.2, ARPN[ci][ARP_IDX[(k + bar) % 6] % 4],
                                  104 if k % 2 == 0 else 78))
        if act("pad", bar) and bar % 2 == 0:
            for m in CHORDS[ci]: ev["pad"].append((b0, 8, m, 80))
        if act("choir", bar) and bar % 2 == 0:
            for m in CHORDS[ci]: ev["choir"].append((b0, 8, m + 12 if m < 50 else m, 80))
        if act("lead", bar) and bar % 8 == 0:
            for (bt, d, m) in MELODY: ev["lead"].append((b0 + bt, d, m, 100))
        if act("chops", bar):
            ch = ARPN[ci]
            for k, st in enumerate([3, 7, 11, 14] if bar % 2 == 0 else [2, 6, 10, 15]):
                ev["chops"].append((b0 + st * 0.25, 0.2, ch[1 + (k % 2)], 92 - 6 * (k % 3)))
    return ev


def render(ev, stems_dir=None):
    z = lambda: np.zeros(N, np.float32)
    kb, sb, cb, hb, shb, rb, chopb, fx, breath = z(), z(), z(), z(), z(), z(), z(), z(), z()
    arpL, arpR, leadL, leadR, padL, padR, chL, chR = z(), z(), z(), z(), z(), z(), z(), z()
    kick, clap = soft_kick(), soft_clap()
    hat_c, hat_o, tick, shk = gh.make_hat(True), gh.make_hat(False), gh.make_tick(), shaker()
    crash_hf, crash_sub = gh.make_crash()

    print("drums…")
    for b, d, m, v in ev["kick"]: place(kb, spos(b), kick, vg(v))
    starts = [spos(b) for b, *_ in ev["kick"]]
    for b, d, m, v in ev["clap"]: place(cb, spos(b), clap, vg(v))
    for b, d, m, v in ev["hat_c"]: place(hb, spos(b), hat_c, vg(v))
    for b, d, m, v in ev["hat_o"]: place(hb, spos(b), hat_o, vg(v))
    for b, d, m, v in ev["shaker"]: place(shb, spos(b), shk, vg(v))
    for b, d, m, v in ev["rim"]: place(rb, spos(b), tick, vg(v))
    print("bass / plucks…")
    for b, d, m, v in ev["sub"]: place(sb, spos(b), sub_note(mtof(m), d * BEAT), vg(v))
    cache = {}
    for b, d, m, v in ev["arp"]:
        key = (m, "a")
        if key not in cache: cache[key] = pluck(mtof(m), 0.3, 0.55)
        Lp, Rp = cache[key]
        place(arpL, spos(b), Lp, vg(v)); place(arpR, spos(b), Rp, vg(v))
    for b, d, m, v in ev["lead"]:
        key = (m, d)
        if key not in cache: cache[key] = pluck(mtof(m), d * BEAT, 1.5)
        Lp, Rp = cache[key]
        place(leadL, spos(b), Lp, vg(v)); place(leadR, spos(b), Rp, vg(v))
    print("pads / voices…")
    segs = {}
    for b, d, m, v in ev["pad"]: segs.setdefault((b, d), []).append(m)
    for (b, d), notes in sorted(segs.items()):
        Lp, Rp = pad_chord(notes, d)
        place(padL, spos(b), Lp, 1.0); place(padR, spos(b), Rp, 1.0)
    segs = {}
    for b, d, m, v in ev["choir"]: segs.setdefault((b, d), []).append(m)
    for (b, d), notes in sorted(segs.items()):
        bar = int(b // 4)
        Lc, Rc = gh.choir_segment(notes, d, ["u", "o"] if bar < 112 else ["o", "a"])
        place(chL, spos(b), Lc, 0.8); place(chR, spos(b), Rc, 0.8)
        if bar % 16 == 8 or bar >= 154:
            place(breath, max(spos(b) - int(0.9 * SR), 0), gh.make_breath(1.3, 1700), 0.5)
    for b, d, m, v in ev["chops"]:
        place(chopb, spos(b), gh.chop(m, ["a", "o", "e"][int(b * 4) % 3]), vg(v))
    place(breath, spos(157 * 4), gh.make_breath(3.0, 1400), 0.9)
    for a, bb in LAYERS["riser"]:
        place(fx, spos(a * 4), gh.make_riser((bb - a) * 4 * BEAT), 0.4)
    for a, bb in LAYERS["crash"]:
        place(fx, spos(a * 4), crash_hf, 0.25)

    print("sidechain + delay…")
    sc_h, sc_m, sc_s = gh.sidechain(starts, 0.75, 0.10), gh.sidechain(starts, 0.45, 0.10), gh.sidechain(starts, 0.25, 0.10)
    sb *= sc_h
    padL *= sc_m; padR *= sc_m; chL *= sc_m; chR *= sc_m
    arpL *= sc_s; arpR *= sc_s; leadL *= sc_s; leadR *= sc_s
    chopb *= sc_s
    arpDL, arpDR = pingpong(arpL, arpR)
    leadDL, leadDR = pingpong(leadL, leadR, gains=(0.55, 0.42, 0.3, 0.2))
    hb *= 0.9
    out_env = gh.level_ramp(146, 154, 1.0, 0.0)
    for bus in (kb, sb, cb, hb, shb, rb, arpL, arpR, arpDL, arpDR, leadL, leadR, leadDL, leadDR, chopb):
        bus *= out_env

    print("reverbs…")
    irP, irH = gh.make_ir(0.8, 9000, 0.006, 21), gh.make_ir(3.0, 6500, 0.02, 22)
    sendP = sos_filt(0.5 * cb + 0.3 * rb + 0.3 * shb, "highpass", 300, 2).astype(np.float32)
    wetP = gh.reverb(sendP, irP)
    hl = sos_filt(0.4 * (padL + chL + leadL) + 0.3 * arpL + 0.5 * chopb + 0.6 * fx + 0.4 * breath + 0.3 * (arpDL + leadDL),
                  "highpass", 220, 2).astype(np.float32)
    hr = sos_filt(0.4 * (padR + chR + leadR) + 0.3 * arpR + 0.5 * chopb + 0.6 * fx + 0.4 * breath + 0.3 * (arpDR + leadDR),
                  "highpass", 220, 2).astype(np.float32)
    from scipy import signal
    wHL = signal.oaconvolve(hl, irH[0])[:N].astype(np.float32) * sc_s
    wHR = signal.oaconvolve(hr, irH[1])[:N].astype(np.float32) * sc_s

    print("mix…")
    def side(c, a, d, l, ld, p, ch, wp, wh):
        return (0.9 * kb + 0.42 * sb + 0.30 * cb + 0.17 * hb + 0.11 * shb + 0.2 * rb + 0.38 * a + 0.28 * d
                + 0.36 * l + 0.28 * ld + 0.32 * p + 0.30 * ch + 0.26 * chopb + 0.35 * fx + 0.5 * breath
                + 0.2 * wp + 0.5 * wh + 0.0 * c)
    ML = side(0, arpL, arpDL, leadL, leadDL, padL, chL, wetP[0], wHL)
    MR = side(0, arpR, arpDR, leadR, leadDR, padR, chR, wetP[1], wHR)
    if stems_dir:
        os.makedirs(stems_dir, exist_ok=True)
        st = {"kick": (kb, kb), "sub": (sb, sb), "clap": (cb, cb), "hats_shaker": (hb + shb, hb + shb),
              "rim": (rb, rb), "arp_pluck": (arpL + arpDL, arpR + arpDR), "lead_pluck": (leadL + leadDL, leadR + leadDR),
              "pad": (padL, padR), "choir": (chL, chR), "vocal_chops": (chopb, chopb),
              "fx_breath": (fx + breath, fx + breath), "reverb_return": (wetP[0] + wHL, wetP[1] + wHR)}
        for k, (l, r_) in st.items():
            gh.write_wav(os.path.join(stems_dir, f"stem_{k}.wav"), l, r_, normalise=True)
    return ML, MR


def master(L, R):
    from scipy import signal
    x = np.stack([L, R]).astype(np.float64)
    x = signal.sosfilt(signal.butter(2, 22, "highpass", fs=SR, output="sos"), x, axis=1)
    x = np.tanh(0.7 * x / np.percentile(np.abs(x), 99.9))
    x = x / np.max(np.abs(x)) * 0.89
    return x[0].astype(np.float32), x[1].astype(np.float32)


def export_midi(ev, d):
    os.makedirs(d, exist_ok=True)
    drums = [(b, dd, p, v) for k in ("kick", "clap", "hat_c", "hat_o", "shaker", "rim") for b, dd, p, v in ev[k]]
    gh.BPM = BPM
    w = lambda n, tr: gh.write_midi(os.path.join(d, n), tr)
    w("01_drums_GM.mid", [("Drums (GM ch10)", 9, drums)])
    w("02_sub_bass.mid", [("Sub", 0, ev["sub"])])
    w("03_arp_pluck.mid", [("Arp", 0, ev["arp"])])
    w("04_lead_pluck.mid", [("Lead", 0, ev["lead"])])
    w("05_pad_chords.mid", [("Pad", 0, ev["pad"])])
    w("06_choir_chords.mid", [("Choir", 0, ev["choir"])])
    w("07_vocal_chops.mid", [("Chops", 0, ev["chops"])])
    w("00_FULL_ARRANGEMENT.mid", [("Drums", 9, drums), ("Sub", 1, ev["sub"]), ("Arp", 2, ev["arp"]),
                                  ("Lead", 3, ev["lead"]), ("Pad", 4, ev["pad"]), ("Choir", 5, ev["choir"]),
                                  ("Chops", 6, ev["chops"])])


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
    gh.write_wav(os.path.join(a.out, "02_nefes_dongusu.wav"), L, R, normalise=False)
    print("done", N / SR, "s")
