"""Musique originale 30 s — tension (0-7 s) puis montée énergique, 120 BPM, grille calée sur t=1.0 s."""
import numpy as np, wave, sys
SR = 44100; DUR = 30.0
BEAT = 0.5; OFF = 1.0          # temps forts à 1.0 + 0.5k ; mesures à 1,3,5,...
N = int(SR * (DUR + 3)); L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(3)
def midi(n): return 440 * 2 ** ((n - 69) / 12)
def add(sig, start, pan=0.0, gain=1.0):
    i = int(start * SR)
    if i < 0: sig = sig[-i:]; i = 0
    if i >= N: return
    sig = sig[:N - i] * gain
    L[i:i+len(sig)] += sig*np.sqrt(.5*(1-pan)); R[i:i+len(sig)] += sig*np.sqrt(.5*(1+pan))
def tt(d): return np.arange(int(d*SR))/SR
def env(n, a, r):
    e = np.ones(n); A = max(1, int(a*SR)); Rr = max(1, int(r*SR))
    e[:A] = np.linspace(0, 1, A); e[-Rr:] *= np.linspace(1, 0, Rr); return e
def lp(x, k):  # passe-bas simple (moyenne glissante)
    return np.convolve(x, np.ones(k)/k, 'same')
def saw(f, t): return 2*((f*t) % 1) - 1
def pad(notes, d, bright=1.0):
    t = tt(d); s = np.zeros_like(t)
    for n in notes:
        for det in (-.1, .1):
            s += saw(midi(n)*2**(det/12), t)
    s = lp(s, int(30/bright)) / (len(notes)*2)
    return s*env(len(t), .6, .8)
def pluck(n, d=.45):
    t = tt(d); f = midi(n)
    s = sum(a*np.sin(2*np.pi*f*h*t)*np.exp(-t*(6+4*h)) for h, a in ((1,1),(2,.5),(3,.3),(4,.15)))
    return s*np.minimum(1, t/.003)
def bassn(n, d):
    t = tt(d); f = midi(n)
    s = np.tanh(2.2*(np.sin(2*np.pi*f*t)+.35*saw(f, t)))
    return lp(s, 12)*env(len(t), .005, .05)*.6
def kick(g=1):
    t = tt(.4); f = 45+110*np.exp(-t*30); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*8)*g
def hat(d=.05):
    t = tt(d); x = np.diff(np.concatenate([[0], rng.standard_normal(len(t))])); return x*np.exp(-t*80)*.22
def clap():
    t = tt(.22); x = rng.standard_normal(len(t)); x = lp(x, 4)-lp(x, 30)
    e = np.exp(-t*20); e[:int(.012*SR)] *= 1.6; return x*e*.9
def riser(d):
    t = tt(d); f = 200*2**(t/d*4); ph = 2*np.pi*np.cumsum(f)/SR
    nz = rng.standard_normal(len(t)); nz = nz-lp(nz, int(40-30*0))
    return (0.25*np.sin(ph)+.5*nz*(t/d))*(t/d)**2
def impact():
    t = tt(2.5); f = 30+80*np.exp(-t*6)
    s = np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*1.6)
    nz = rng.standard_normal(len(t))*np.exp(-t*5)*.35
    return s+lp(nz, 3)
def tick():
    t = tt(.03); return np.sin(2*np.pi*2400*t)*np.exp(-t*200)*.35

# --- 0 → 7 s : tension (La mineur), pulsation
add(pad([57, 60, 64, 69], 7.4, .7), 0.0, gain=.55)
for k in range(int((7-0.0)/0.25)):
    tk = k*0.25
    if tk >= 6.75: break
    add(bassn(33 if (k//8) % 2 == 0 else 31, .2), tk+OFF*0, gain=.35 + .25*(tk/7))
    if k % 2 == 1: add(tick(), tk, pan=.3*(-1)**k, gain=.8)
for i, (tm, n) in enumerate([(1.0, 76), (3.0, 77), (5.0, 76)]):
    add(pluck(n, 1.2), tm, pan=-.3, gain=.25)
add(riser(2.2), 4.8, gain=.55)
add(impact(), 7.0, gain=1.0)
add(pluck(81, 2.0), 7.0, gain=.3); add(pluck(76, 2.0), 7.01, gain=.25)

# --- 7 → 27 s : montée (C – G – Am – F), une mesure (2 s) par accord
PROG = [([48, 60, 64, 67, 71], 36), ([43, 59, 62, 67, 69], 31), ([45, 60, 64, 69, 72], 33), ([41, 57, 60, 65, 69], 29)]
ARP = [[72, 76, 79, 76, 84, 79, 76, 79], [71, 74, 79, 74, 81, 79, 74, 79], [72, 76, 81, 76, 84, 81, 76, 81], [69, 72, 77, 72, 81, 77, 72, 77]]
for b in range(10):
    t0 = 7.0 + 2*b
    ch, root = PROG[b % 4]
    add(pad(ch[1:], 2.15, 1.3), t0, gain=.42)
    for i in range(8):
        add(pluck(ARP[b % 4][i] + (12 if b >= 5 and i % 4 == 3 else 0)), t0 + i*.25, pan=.35*np.sin(i*1.3), gain=.22)
    for i in range(8):  # basse en croches décalées
        add(bassn(root, .2), t0 + i*.25 + .125*(i % 2 == 1), gain=.45)
    drums = not (b == 4 and False)
    for i in range(4):
        add(kick(), t0 + i*.5, gain=.8)
        if i in (1, 3): add(clap(), t0 + i*.5, gain=.35)
        for j in range(4):
            add(hat(), t0 + i*.5 + j*.125, pan=.4*(-1)**j, gain=.9 if j == 2 else .45)
# petite montée avant les associés (17 s) et avant la fin (27 s)
add(riser(1.6), 15.4, gain=.35); add(impact(), 17.0, gain=.45)
add(riser(2.0), 25.0, gain=.5)
# --- 27 → 30 s : impact + accord final
add(impact(), 27.0, gain=1.0)
add(pad([48, 60, 64, 67, 71, 76], 3.2, 1.2), 27.0, gain=.55)
for k, n in enumerate([72, 76, 79, 84]):
    add(pluck(n, 2.5), 27.0 + k*.06, gain=.28)

# réverbération
irn = int(1.8*SR); ti = np.arange(irn)/SR
def rev(x, seed):
    ir = np.random.default_rng(seed).standard_normal(irn)*np.exp(-ti*3.5); ir = lp(ir, 6)
    nfft = 1 << (len(x)+irn-1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, nfft)*np.fft.rfft(ir, nfft), nfft)[:len(x)]
Lw, Rw = rev(L, 1), rev(R, 2)
Lo = L + .25*Lw/np.abs(Lw).max()*np.abs(L).max(); Ro = R + .25*Rw/np.abs(Rw).max()*np.abs(R).max()
st = np.stack([Lo, Ro], 1)[:int(DUR*SR)]
fi, fo = int(.3*SR), int(1.6*SR)
st[:fi] *= np.linspace(0, 1, fi)[:, None]; st[-fo:] *= np.linspace(1, 0, fo)[:, None]**1.3
st = np.tanh(st/np.percentile(np.abs(st), 99.7)*1.0); st = st/np.abs(st).max()*.89
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'music30.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype('<i2').tobytes())
print('ok')
