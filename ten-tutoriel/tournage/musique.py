"""Musique d'ambiance originale, entraînante et légère (synthèse numpy, aucun échantillon externe).

Usage : python musique.py <durée_en_secondes> <sortie.wav>
120 BPM, progression I–V–vi–IV en ré majeur, pad + arpège pincé + basse + batterie douce,
pompe de compression rythmique, intro et fin en fondu.
"""
import sys
import wave

import numpy as np

SR = 44100
BPM = 120
BEAT = 60 / BPM
BAR = 4 * BEAT
rng = np.random.default_rng(7)


def note(n):  # numéro MIDI -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)


def filtre(x, coupure_basse=None, coupure_haute=None):
    """Filtre par FFT (passe-haut / passe-bas doux)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    if coupure_haute:
        g *= 1 / np.sqrt(1 + (f / coupure_haute) ** 4)
    if coupure_basse:
        g *= 1 / np.sqrt(1 + (coupure_basse / np.maximum(f, 1e-3)) ** 4)
    return np.fft.irfft(X * g, len(x))


def env(n, a, d, s=0.0, r=0.0):
    t = np.arange(n) / SR
    e = np.where(t < a, t / max(a, 1e-4), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4)))
    if r:
        fin = int(r * SR)
        e[-fin:] *= np.linspace(1, 0, fin)
    return e


def scie(freq, n, detune=0.0):
    t = np.arange(n) / SR
    s = np.zeros(n)
    for k in range(1, 14):
        s += np.sin(2 * np.pi * k * freq * (1 + detune) * t) / k
    return s * 0.55


# I – V – vi – IV en ré majeur : D, A, Bm, G
ACCORDS = [
    (50, [62, 66, 69, 74]),  # D
    (45, [61, 64, 69, 73]),  # A
    (47, [62, 66, 71, 74]),  # Bm
    (43, [62, 67, 71, 74]),  # G
]


def piste(duree):
    n_total = int(duree * SR)
    nb_mesures = int(np.ceil(duree / BAR)) + 1
    L = nb_mesures * int(BAR * SR) + SR
    pad = np.zeros((L, 2))
    arp = np.zeros((L, 2))
    basse = np.zeros(L)
    kick = np.zeros(L)
    caisse = np.zeros(L)
    hat = np.zeros(L)
    pompe = np.ones(L)

    nb = int(BAR * SR)
    # sections : intro 8 mesures sans batterie, pont en milieu, fin sans kick
    milieu = nb_mesures // 2

    def section(m):
        if m < 4:
            return "intro"
        if m < 8:
            return "montee"
        if milieu - 2 <= m < milieu + 2:
            return "pont"
        if m >= nb_mesures - 5:
            return "fin"
        return "plein"

    # échantillons de batterie
    nk = int(0.35 * SR)
    tk = np.arange(nk) / SR
    son_kick = np.sin(2 * np.pi * (48 * tk + 90 * (1 - np.exp(-tk * 28)) / 28)) * np.exp(-tk * 9)
    ns = int(0.22 * SR)
    son_caisse = filtre(rng.standard_normal(ns), 900, 7000) * np.exp(-np.arange(ns) / SR * 22) * 0.6
    son_caisse += np.sin(2 * np.pi * 190 * np.arange(ns) / SR) * np.exp(-np.arange(ns) / SR * 30) * 0.35
    nh = int(0.06 * SR)
    son_hat = filtre(rng.standard_normal(nh), 7000) * np.exp(-np.arange(nh) / SR * 60)

    motif_arp = [0, 1, 2, 3, 2, 1, 2, 3, 0, 2, 1, 3, 2, 3, 1, 2]

    for m in range(nb_mesures):
        base, acc = ACCORDS[m % 4]
        deb = m * nb
        sec = section(m)
        # pad (deux voix désaccordées, stéréo)
        e = env(nb, 0.35, 9.0, 0.85, 0.25)
        g = 0.07 if sec != "pont" else 0.09
        for i, n_ in enumerate(acc):
            v = scie(note(n_), nb, 0.0035) * e * g
            w = scie(note(n_), nb, -0.0035) * e * g
            pad[deb:deb + nb, 0] += v * (0.6 + 0.1 * i)
            pad[deb:deb + nb, 1] += w * (1.0 - 0.1 * i)
        # arpège en doubles croches
        if sec != "intro" or m >= 2:
            pas = int(BEAT / 4 * SR)
            for k in range(16):
                n_ = acc[motif_arp[k]] + 12
                d = deb + k * pas
                ln = int(0.32 * SR)
                t = np.arange(ln) / SR
                f0 = note(n_)
                son = (np.sin(2 * np.pi * f0 * t) + 0.3 * np.sin(2 * np.pi * 2 * f0 * t)
                       + 0.12 * np.sin(2 * np.pi * 3 * f0 * t)) * np.exp(-t * 11)
                vol = 0.085 * (1.0 if k % 4 == 0 else 0.7)
                pan = 0.5 + 0.35 * np.sin(k * 0.8)
                arp[d:d + ln, 0] += son * vol * (1 - pan)
                arp[d:d + ln, 1] += son * vol * pan
        # basse en croches (sauf intro et pont)
        if sec in ("montee", "plein", "fin"):
            pas = int(BEAT / 2 * SR)
            for k in range(8):
                f0 = note(base - 12 + (12 if k in (3, 7) else 0))
                ln = int(BEAT / 2 * SR * 0.9)
                t = np.arange(ln) / SR
                son = np.tanh(1.8 * (np.sin(2 * np.pi * f0 * t) + 0.25 * np.sin(4 * np.pi * f0 * t)))
                son *= env(ln, 0.005, 0.18, 0.55, 0.03)
                basse[deb + k * pas: deb + k * pas + ln] += son * 0.2
        # batterie
        for b in range(4):
            d = deb + int(b * BEAT * SR)
            if sec in ("plein", "montee") or (sec == "pont" and m >= milieu + 1 and b >= 2):
                kick[d:d + nk] += son_kick * 0.75
                pompe[d:d + int(0.3 * SR)] = np.minimum(pompe[d:d + int(0.3 * SR)],
                                                         0.45 + 0.55 * np.linspace(0, 1, int(0.3 * SR)) ** 0.7)
            if sec == "plein" and b in (1, 3):
                caisse[d:d + ns] += son_caisse * 0.55
            if sec in ("plein", "fin", "montee"):
                dh = d + int(BEAT / 2 * SR)
                hat[dh:dh + nh] += son_hat * (0.16 if sec != "montee" else 0.09)
                hat[d:d + nh] += son_hat * 0.05

    pad = np.stack([filtre(pad[:, 0], 120, 2600), filtre(pad[:, 1], 120, 2600)], 1)
    pad *= pompe[:, None]
    # écho sur l'arpège (croche pointée)
    dl = int(BEAT * 0.75 * SR)
    for c, dec in ((0, dl), (1, dl + int(0.02 * SR))):
        echo = np.zeros(L)
        echo[dec:] = arp[:-dec, 1 - c] * 0.32
        arp[:, c] += echo
    arp = np.stack([filtre(arp[:, 0], 250, 9000), filtre(arp[:, 1], 250, 9000)], 1)
    basse = filtre(basse, 35, 900)

    mono = basse + kick + caisse * 0.9
    mix = pad + arp * pompe[:, None] ** 0.5
    mix[:, 0] += mono + hat * 0.8
    mix[:, 1] += mono + hat
    mix = mix[:n_total]
    # fondus
    fi, fo = int(2.5 * SR), int(5 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)[:, None]
    mix[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
    # normalisation douce
    mix = np.tanh(mix * 1.1)
    mix /= np.max(np.abs(mix)) / 0.89
    return mix


if __name__ == "__main__":
    duree, sortie = float(sys.argv[1]), sys.argv[2]
    m = piste(duree)
    pcm = (m * 32767).astype("<i2")
    with wave.open(sortie, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("ok", sortie, f"{duree:.1f}s")
