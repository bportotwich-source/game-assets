"""Facão no nível de detalhe da M4A1: lâmina longa de aço carbono escurecido que alarga na
ponta, com desbaste e fio polido, espiga inteira aparente entre talas de madeira presas com
três rebites de latão, bico no fim do cabo, ilhós e fiel de couro. Desenho próprio, sem marcas.

O contorno da lâmina é o do facão antigo (arma19_facao.py), para a bainha de lona e os pontos
de acerto (ponta, parte larga do fio) continuarem valendo.

Coordenadas em mm (lib.py da M4A1): u = para a frente (ponta), v = para cima (dorso), w = direita.
u = 0 é onde a lâmina sai do cabo.
"""
import math
import numpy as np
from shapely.geometry import Polygon, LineString
from lib import *

L = 340.0


def dorso(x):
    if x <= 220:
        return 13.5 + 2.5 * (max(x, 0) / 220)
    s = (x - 220) / (L - 220)
    return 16.0 - 11.0 * s ** 1.8


def gume(x):
    if x < 12:
        return -17.0
    if x <= 270:
        return -17.0 - 13.0 * ((x - 12) / 258) ** 1.4
    s = (x - 270) / (L - 270)
    return -30.0 + 35.0 * s ** 1.7


def esp(x):
    return 1.5 if x < 0 else 1.5 - 0.6 * (x / L)


def pl(g):
    return [(float(x), float(y)) for x, y in list(g.exterior.coords)[:-1]]


def curva(pts, n=2):
    for _ in range(n):
        q = []
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            q += [(0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]), (0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1])]
        pts = q
    return Polygon(pts)


def _catmull(pts, n=6):
    Q = np.array(pts, float)
    Q = np.vstack([Q[0] * 2 - Q[1], Q, Q[-1] * 2 - Q[-2]])
    out = []
    for i in range(1, len(Q) - 2):
        p0, p1, p2, p3 = Q[i - 1], Q[i], Q[i + 1], Q[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(tuple(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)))
    out.append(tuple(Q[-2]))
    return out


def _h_fio(x):
    return min(3.5, 0.3 * (dorso(x) - gume(x)))


def _secao(x):
    yt, yb, t = dorso(x), gume(x), esp(x)
    e = 0.1
    H = yt - yb
    yg = yb + 0.3 * H
    h = min(3.5, 0.25 * H)
    z1 = e + (t - e) * h / max(yg - yb, 0.05)
    q = min(0.7, 0.2 * H)
    return [(t * 0.8, yt), (-t * 0.8, yt), (-t, yt - q), (-t, yg), (-z1, yb + h), (-e, yb), (e, yb), (z1, yb + h), (t, yg), (t, yt - q)]


CONT = curva([(-2, 13.5), (-60, 15.2), (-110, 14.5), (-128, 12.5), (-138, 4), (-142, -12), (-136, -26),
              (-128, -22), (-115, -16.5), (-70, -18.5), (-30, -16.5), (-8, -18.5), (-2, -17)], 3)
LARG = lambda x: 9.8 + 1.2 * math.exp(-((x + 70) / 40) ** 2)
REBITES = [(-25, -1.0), (-70, -1.5), (-112, -1.0)]
FURO = (-130, -8)


def lamina():
    xs = list(np.linspace(-2, 12, 4)) + list(np.linspace(14, L - 2, 110))
    aneis = [[P(x, v, w) for w, v in _secao(x)] for x in xs]
    ult = _secao(L - 2)
    yc = float(np.mean([y for _, y in ult]))
    aneis.append([P(L, yc + (v - yc) * 0.08, w * 0.08) for w, v in ult])
    lam = loft(aneis, 'aco_facao')
    pintar(lam, 'aco_lamina', lambda p, n: p[0] > 13 and p[1] < gume(min(p[0], L)) + min(3.5, 0.25 * (dorso(min(p[0], L)) - gume(min(p[0], L)))) * 0.98 and abs(n[2]) > 0.3)
    o = [lam]
    o.append(texto('RC 340', 3.0, 14, 2.0, -(1.5 + 0.02), mat='tinta', alinhar='LEFT'))
    # espiga inteira aparente entre as talas, com o furo do fiel
    esp_ = extr(pl(CONT), -1.5, 1.5, 'aco_brasa')
    cut(esp_, cyl((FURO[0], FURO[1], -20), (FURO[0], FURO[1], 20), 3.5, 'aco_brasa', n=18))
    o.append(esp_)
    for (u, v) in REBITES:                                                                   # rebites de latão vazados
        zt = LARG(u) * 0.93 + 0.5
        r = lathe([(-zt, 1.2), (-zt, 2.2), (-zt + 0.5, 2.7), (zt - 0.5, 2.7), (zt, 2.2), (zt, 1.2)], 'latao', n=18, c0=(u, v, 0), eixo=(0, 0, 1), anel=True)
        o.append(r)
    zi = 10.4
    o.append(lathe([(-zi, 2.8), (-zi, 3.9), (-zi + 0.6, 4.3), (zi - 0.6, 4.3), (zi, 3.9), (zi, 2.8)], 'inox', n=18, c0=(FURO[0], FURO[1], 0), eixo=(0, 0, 1), anel=True))   # ilhós
    return parte('lamina', o, origem=(0, 0, 0), grupo='A', suave=32)


def cabo(pai):
    b = CONT.bounds
    us = list(np.linspace(b[0] + 0.05, b[0] + 6, 8)) + list(np.linspace(b[0] + 8, -3.5, 60)) + [-2.6, -2.05]
    aneis = []
    for u in us:
        x = CONT.intersection(LineString([(u, -60), (u, 60)])).bounds
        k = 1.0
        if u - b[0] < 6:
            k = 0.35 + 0.65 * ((u - b[0]) / 6) ** 0.5
        if u > -3.5:
            k = 0.82 + 0.18 * ((-2.0 - u) / 1.5) ** 0.5
        aneis.append([P(u, v, w) for w, v in superelipse(LARG(u) * k, (x[3] - x[1]) / 2 - 0.02, n=44, e=2.2, cy=(x[1] + x[3]) / 2)])
    talas = loft(aneis, 'madeira_facao')
    cut(talas, [box(-200, 50, -60, 60, -1.5, 1.5, 'madeira_facao'), cyl((FURO[0], FURO[1], -20), (FURO[0], FURO[1], 20), 3.9, 'madeira_facao', n=18)] +
        [cyl((u, v, -20), (u, v, 20), 2.7, 'madeira_facao', n=18) for (u, v) in REBITES])
    o = [talas]
    # fiel de couro: laço passando pelo furo e pendendo para baixo, com passador
    pts = _catmull([(-130, -6.5, 4), (-131, -8, 11.5), (-137, -18, 13), (-146, -42, 6), (-151, -66, 0), (-146, -42, -6), (-137, -18, -13), (-131, -8, -11.5), (-130, -6.5, -4)], 6)
    o.append(fio(pts, 1.6, 'couro_arco', fechado=True, res=2))
    o.append(lathe([(-3, 0), (-3, 3.2), (-2.2, 3.8), (2.2, 3.8), (3, 3.2), (3, 0)], 'couro_escuro', n=14, c0=(-150, -58, 0), eixo=(0.1, 1, 0)))
    return parte('cabo', o, origem=(-65, 0, 0), pai=pai, grupo='A', suave=40)


def montar():
    f = lamina()
    cabo(f)
