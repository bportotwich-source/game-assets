"""Bastões de madeira melhorados na bancada, no nível de detalhe da M4A1: taco de freixo claro
com pomo, cabo fino enrolado em fita isolante, barril grosso com mossas de uso, e na parte grossa
ou uns vinte pregos batidos (alguns entortados) ou arame farpado de dois fios torcidos, com farpas
de quatro pontas e as pontas amarradas. Desenho próprio, sem marcas.

Mesmas medidas dos bastões antigos (arma22_bastao.py): os pontos das mãos, do barril e da ponta
e as animações continuam valendo.

Coordenadas em mm (lib.py da M4A1): u = para a frente (do pomo para a ponta grossa), v = para cima,
w = direita. u = 0 é o pé do pomo.
"""
import math
import numpy as np
from lib import *

L = 840.0
FITA = (30.0, 270.0)


def raio(x):
    """Raio do taco em x (0 = pomo, L = ponta)."""
    if x < 14:
        return 22.0
    if x < 30:
        return 22.0 - (22.0 - 12.8) * (x - 14) / 16
    if x < 300:
        return 12.8 + 1.2 * (x - 30) / 270
    if x < 620:
        s = (x - 300) / 320
        return 14.0 + (33.5 - 14.0) * (3 * s * s - 2 * s ** 3)
    return 33.5


def _radial(x, a, r):
    return np.array([x, r * math.cos(a), r * math.sin(a)])


def taco(rng):
    prof = [(0.0, 0.0), (0.0, 17.0), (3.0, 21.0), (9.0, 22.0), (14.0, 20.5), (20.0, 16.5), (26.0, 13.6)]
    xs = sorted(set([FITA[0], FITA[1], FITA[1] + 0.6] + [round(float(x), 2) for x in np.linspace(34, L - 12, 84)]))
    prof += [(x, raio(x)) for x in xs]
    prof += [(L - 6, 32.0), (L - 2, 28.5), (L, 18.0), (L + 1, 0.0)]
    corpo = lathe(prof, 'madeira_taco', n=44)
    pintar(corpo, 'fita_isolante', lambda p, n: FITA[0] < p[0] < FITA[1])
    mossas = []                                                          # amassados e lascas de uso no barril
    for _ in range(14):
        x = rng.uniform(500, 820)
        a = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(3.0, 6.0)
        k = rng.uniform(1.0, 2.2)
        c = _radial(x, a, raio(x) + 0.55 * r)
        s = lathe([(-r * k, 0.0)] + [(-r * k * math.cos(t), r * math.sin(t)) for t in np.linspace(0.3, math.pi - 0.3, 7)] + [(r * k, 0.0)], 'madeira_lasca', n=10, c0=tuple(c))
        mossas.append(s)
    cut(corpo, mossas)
    return corpo


def pregos(rng):
    o = []
    n = 0
    for i, x in enumerate(np.linspace(600, 810, 6)):                     # 6 anéis de 3 a 4 pregos, girados entre si
        k = 3 if i % 2 else 4
        for j in range(k):
            a = 2 * math.pi * j / k + i * 0.7 + rng.uniform(-0.25, 0.25)
            r = raio(x)
            fora = rng.uniform(22, 40)
            rad = np.array([0, math.cos(a), math.sin(a)])
            d = np.array([rng.uniform(-0.25, 0.25), math.cos(a), math.sin(a)])
            d /= np.linalg.norm(d)
            p0 = np.array([x, 0, 0]) + rad * (r - 18)
            p1 = np.array([x, 0, 0]) + rad * r + d * fora
            if n % 5 == 3:                                               # alguns entortados de bater
                meio = (p0 + p1) / 2 + d * 4
                dobra = np.cross(d, [1, 0, 0])
                dobra /= np.linalg.norm(dobra)
                pts = [p0, meio, meio + d * 6 + dobra * 4, meio + d * 8 + dobra * 12]
                o.append(fio(caminho_arred([tuple(p) for p in pts], 3.0, 4, fechado=False), 1.5, 'aco_prego', fechado=False, res=2))
                p1 = pts[-1]
                d = (pts[-1] - pts[-2]) / np.linalg.norm(pts[-1] - pts[-2])
            else:
                o.append(cyl(tuple(p0), tuple(p1), 1.5, 'aco_prego', n=8))
            mat = 'prego_ferrugem' if n % 3 == 0 else 'aco_prego'
            o.append(lathe([(-0.4, 0.0), (-0.4, 3.3), (0.2, 3.7), (0.9, 3.5), (1.1, 0.0)], mat, n=14, c0=tuple(p1), eixo=tuple(d)))
            n += 1
    return o


def arame(rng):
    o = []
    x0, x1, voltas = 500.0, 815.0, 7.5
    t = np.linspace(0, 1, 520)
    X = x0 + (x1 - x0) * t
    ang = 2 * math.pi * voltas * t
    R = np.array([raio(x) + 2.4 for x in X])
    C = np.stack([X, R * np.cos(ang), R * np.sin(ang)], 1)
    Nr = np.stack([np.zeros_like(X), np.cos(ang), np.sin(ang)], 1)
    T = np.gradient(C, axis=0)
    T /= np.linalg.norm(T, axis=1)[:, None]
    B = np.cross(T, Nr)
    for s in (0, math.pi):                                               # dois fios torcidos
        tor = 2 * math.pi * 70 * t + s
        f = C + 1.1 * (np.cos(tor)[:, None] * Nr + np.sin(tor)[:, None] * B)
        o.append(fio([tuple(p) for p in f], 0.9, 'arame_farpado', fechado=False, res=1))
    Lc = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(C, axis=0), axis=1))])
    for sb in np.arange(20, Lc[-1] - 10, 38):                            # farpas: dois arames cruzados com 4 pontas
        i = int(np.searchsorted(Lc, sb))
        p, n_, b_, tt = C[i], Nr[i], B[i], T[i]
        for k, (a, b) in enumerate(((0.75, 0.66), (0.75, -0.66))):
            d = a * n_ + b * b_ + 0.25 * tt * (1 if k else -1)
            d /= np.linalg.norm(d)
            p0 = p + tt * (1.4 if k else -1.4)
            o.append(lathe([(-0.5, 0.0), (-0.5, 0.75), (8.0, 0.75), (11.0, 0.08), (11.0, 0.0)], 'arame_farpado', n=6, c0=tuple(p0), eixo=tuple(d)))
            d2 = -d * 8.5 + n_ * 6.0
            l2 = float(np.linalg.norm(d2))
            o.append(lathe([(-0.5, 0.0), (-0.5, 0.75), (l2 - 3, 0.75), (l2, 0.08), (l2, 0.0)], 'arame_farpado', n=6, c0=tuple(p0 + n_ * 0.5), eixo=tuple(d2 / l2)))
        o.append(lathe([(-2.2, 1.5), (-2.2, 2.5), (2.2, 2.5), (2.2, 1.5)], 'arame_farpado', n=8, c0=tuple(p), eixo=tuple(tt), anel=True))   # nó da farpa
    for xa, sgn, a0 in ((x0, -1, 0.0), (x1, 1, 2 * math.pi * voltas)):   # pontas amarradas: voltas apertadas e rabicho torcido
        for k in range(3):
            xk = xa + sgn * (4 + k * 3.2)
            rk = raio(xk) + 1.3
            o.append(fio([tuple(_radial(xk + 0.8 * math.sin(a), a, rk)) for a in np.linspace(0, 2 * math.pi, 28, endpoint=False)], 0.9, 'arame_farpado', fechado=True, res=1))
        r = raio(xa) + 1.8
        base = _radial(xa, a0, r)
        ra = np.array([0, math.cos(a0), math.sin(a0)])
        for s in (0, math.pi):
            uu = np.linspace(0, 1, 22)
            pts = [base + ra * 16 * u + 1.0 * np.array([math.cos(8 * math.pi * u + s), 0, math.sin(8 * math.pi * u + s)]) + np.array([sgn * 6 * u, 0, 0]) for u in uu]
            o.append(fio([tuple(p) for p in pts], 0.75, 'arame_farpado', fechado=False, res=1))
    return o


def montar_pregos():
    rng = np.random.default_rng(31)
    parte('taco', [taco(rng)] + pregos(rng), origem=(60, 0, 0), grupo='A', suave=40)


def montar_arame():
    rng = np.random.default_rng(37)
    parte('taco', [taco(rng)] + arame(rng), origem=(60, 0, 0), grupo='A', suave=40)
