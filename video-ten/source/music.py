"""Musique d'ambiance originale (synthèse procédurale) — corporate / inspirant, 96 BPM."""
import numpy as np, wave, sys

SR = 44100
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 80.0
BPM = 96
BEAT = 60 / BPM
BAR = 4 * BEAT
N = int(SR * (DUR + 4))
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)

def midi(n): return 440 * 2 ** ((n - 69) / 12)

# Progression (2 mesures par accord) : Cmaj9 – Am9 – Fmaj7#11 – G6/9
CHORDS = [
    [48, 55, 59, 62, 64],   # C maj9
    [45, 52, 55, 59, 60],   # A m9
    [41, 48, 52, 55, 57],   # F maj7
    [43, 50, 55, 57, 59],   # G 6/9
]
ARP = [
    [60, 64, 67, 71, 74, 71, 67, 64],
    [57, 60, 64, 67, 71, 67, 64, 60],
    [53, 57, 60, 64, 67, 64, 60, 57],
    [55, 59, 62, 64, 69, 64, 62, 59],
]

def add(sig, start, pan=0.0, gain=1.0):
    i = int(start * SR)
    if i >= N: return
    sig = sig[: N - i] * gain
    L[i:i + len(sig)] += sig * np.sqrt(0.5 * (1 - pan))
    R[i:i + len(sig)] += sig * np.sqrt(0.5 * (1 + pan))

def env_adsr(n, a, d, s, r):
    e = np.ones(n) * s
    A, D, Rr = int(a * SR), int(d * SR), int(r * SR)
    e[:A] = np.linspace(0, 1, A)
    e[A:A + D] = np.linspace(1, s, D)
    e[-Rr:] *= np.linspace(1, 0, Rr)
    return e

def pad(note, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    f = midi(note); s = np.zeros(n)
    for det in (-0.12, 0.0, 0.11):
        ff = f * 2 ** (det / 12)
        for h, amp in ((1, 1), (2, .35), (3, .12), (4, .06)):
            s += amp * np.sin(2 * np.pi * ff * h * t + rng.uniform(0, 6.28))
    s *= 1 + 0.15 * np.sin(2 * np.pi * 0.2 * t)
    return s * env_adsr(n, 1.2, 0.5, 0.8, 1.5) / 6

def keys(note, dur=1.6):
    n = int(dur * SR); t = np.arange(n) / SR
    f = midi(note); s = np.zeros(n)
    for h, amp, dec in ((1, 1, 2.2), (2, .5, 3.5), (3, .22, 5), (4, .12, 7), (5, .05, 9)):
        s += amp * np.sin(2 * np.pi * f * h * t * (1 + 0.0004 * h)) * np.exp(-dec * t)
    att = np.minimum(1, t / 0.004)
    return s * att / 2.2

def bass(note, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    f = midi(note)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    return s * env_adsr(n, 0.02, 0.3, 0.7, 0.2) / 1.4

def kick():
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 50 + 90 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 7)

def hat():
    n = int(0.08 * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n); x = np.diff(np.concatenate([[0], x]))  # high-pass
    return x * np.exp(-t * 60) * 0.25

def clap():
    n = int(0.25 * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    x = np.convolve(x, np.ones(6) / 6, 'same') - np.convolve(x, np.ones(40) / 40, 'same')
    return x * np.exp(-t * 18) * 0.9

nbars = int(np.ceil(DUR / BAR))
for b in range(nbars):
    t0 = b * BAR
    ci = (b // 2) % 4
    ending = t0 > DUR - 2 * BAR
    if b % 2 == 0:
        for k, nt in enumerate(CHORDS[ci][1:]):
            add(pad(nt, 2 * BAR + (2.5 if ending else 0.4)), t0, pan=(k - 1.5) * 0.35, gain=0.55)
    # arpèges dès la mesure 2
    if b >= 2 and not ending:
        for i, nt in enumerate(ARP[ci]):
            vel = 0.75 if i % 2 == 0 else 0.5
            add(keys(nt + (12 if b >= 12 and i in (3, 4) else 0)), t0 + i * BEAT / 2, pan=0.3 * np.sin(i), gain=0.35 * vel)
    # basse dès la mesure 6
    if b >= 6:
        root = CHORDS[ci][0] - 12
        for i in range(2):
            add(bass(root, BEAT * 2 - 0.05), t0 + i * 2 * BEAT, gain=0.55)
    # rythmique mesures 8 → fin-2 (break léger 18-19)
    if 8 <= b < nbars - 2 and b not in (18, 19):
        for i in range(4):
            add(kick(), t0 + i * BEAT, gain=0.55 if i in (0, 2) else 0.25)
            add(hat(), t0 + i * BEAT + BEAT / 2, pan=0.4, gain=0.5)
            if b >= 12:
                add(hat(), t0 + i * BEAT + BEAT * 0.75, pan=-0.4, gain=0.22)
            if i in (1, 3) and b >= 10:
                add(clap(), t0 + i * BEAT, pan=0.05, gain=0.18)
# accord final
add(keys(72, 4), (nbars - 2) * BAR, gain=0.3)
add(keys(76, 4), (nbars - 2) * BAR + 0.05, gain=0.25)
add(keys(79, 4), (nbars - 2) * BAR + 0.1, gain=0.22)

# réverbération (convolution FFT)
irn = int(2.4 * SR); ti = np.arange(irn) / SR
def rev(x, seed):
    ir = np.random.default_rng(seed).standard_normal(irn) * np.exp(-ti * 2.8)
    ir = np.convolve(ir, np.ones(8) / 8, 'same')
    m = len(x) + irn
    nfft = 1 << (m - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[:len(x)]
    return y / np.max(np.abs(ir).sum() ** 0.5)
Lw, Rw = rev(L, 1), rev(R, 2)
Lo = L + 0.35 * Lw / (np.abs(Lw).max() + 1e-9) * np.abs(L).max()
Ro = R + 0.35 * Rw / (np.abs(Rw).max() + 1e-9) * np.abs(R).max()

st = np.stack([Lo, Ro], 1)[: int(DUR * SR)]
# fondus
fi, fo = int(1.0 * SR), int(4.0 * SR)
st[:fi] *= np.linspace(0, 1, fi)[:, None]
st[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
# compression douce + normalisation
st = np.tanh(st / np.percentile(np.abs(st), 99.5) * 0.9)
st = st / np.abs(st).max() * 0.85
with wave.open(sys.argv[2] if len(sys.argv) > 2 else 'music.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype('<i2').tobytes())
print('ok', DUR)
