"""Machadinha tática no nível de detalhe da M4A1: cabeça e espiga numa peça só de aço escurecido
(fio curvo com barba, ponta de trás para arrombar, furos de alívio), fio polido, talas de
polímero verde-oliva presas com três pinos vazados, cordão enrolado no meio do cabo, furo e
argola de cordão no pé. Desenho próprio, sem marcas.

O contorno da cabeça é o da machadinha antiga (arma20_machadinha.py), para a capa da lâmina e os
pontos de acerto (meio do fio, ponta de trás) continuarem valendo.

Coordenadas em mm (lib.py da M4A1): u = para a frente (para onde o fio aponta), v = para cima
(cabeça em cima), w = direita. v = 0 é o pé do cabo.
"""
import math
import numpy as np
from shapely.geometry import Polygon, LineString
from lib import *

V0, V1 = 255.0, 374.0              # faixa em v da cabeça


def fio_u(v):
    return 94.0 - 0.0085 * (v - 334) ** 2 - (12.0 * ((290 - v) / 35) if v < 290 else 0.0)


def tras_u(v):
    if v >= 300:
        return -20.0 - 62.0 * max(0.0, 1 - abs(v - 341) / 33)
    if v >= 285:
        return 21.0 - 41.0 * (v - 285) / 15
    return 21.0 + (285 - v) * 0.3


def esp(x, xe):
    if x < -20:
        return 6.5 - 4.8 * min(1.0, (-20 - x) / 62)
    if x <= 20:
        return 6.5
    return 4.7 - 4.3 * min(1.0, (x - 20) / max(xe - 20, 1.0))


def _secao(v):
    xe, xb = fio_u(v), tras_u(v)
    x2 = max(20.0, xb + 4)
    x1 = (xb + x2) / 2
    xf = xe - 3.5
    pts = [(xb, esp(xb, xe)), (x1, esp(x1, xe)), (x2, esp(x2, xe)), (xf, esp(xf, xe)), (xe, 0.12)]
    return pts + [(x, -z) for x, z in pts[::-1]]


def _encolhe(pts, k):
    cx = float(np.mean([p[0] for p in pts]))
    return [(cx + (x - cx) * k, z * k) for x, z in pts]


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


CONT = curva([(-17, 312), (17, 312), (16.5, 240), (15.5, 170), (17.5, 110), (16, 60), (19, 25), (24, 4),
              (18, -6), (-12, -6), (-24, 2), (-21, 30), (-17, 70), (-18.5, 120), (-16, 200), (-16.5, 260)], 3)
LARG = lambda v: 11.8 + 1.2 * math.exp(-((v - 100) / 50) ** 2)
PINOS = [270.0, 215.0, 35.0]
FURO = 6.0                          # v do furo do fiel
E = 2.6                             # meia espessura da espiga


def _faixa(v):
    x = CONT.intersection(LineString([(-80, v), (80, v)])).bounds
    return x[0], x[2]


def cabeca():
    vs = list(np.linspace(V0, V1, 70))
    sec = [(v, _secao(v)) for v in vs]
    sec = [(V0 - 0.5, _encolhe(sec[0][1], 0.8))] + sec + [(V1 + 0.5, _encolhe(sec[-1][1], 0.8))]
    cab = loft([[P(u, v, w) for u, w in pts] for v, pts in sec], 'aco_machado')
    pintar(cab, 'aco_lamina', lambda p, n: V0 < p[1] < V1 and p[0] > fio_u(p[1]) - 3.3)
    furos = [cyl((45, 330, -20), (45, 330, 20), 8.5, 'aco_machado', n=28), cyl((-4, 340, -20), (-4, 340, 20), 4.2, 'aco_machado', n=20)]
    g = LineString([(40, 293), (56, 282)]).buffer(4.2, 8)
    furos.append(extr(pl(g), -20, 20, 'aco_machado'))
    cut(cab, furos)
    o = [cab]
    o.append(texto('RC 19', 3.0, 8, 322, -(6.5 + 0.02), mat='tinta'))
    # espiga (a mesma peça de aço) aparente entre as talas, com o furo do fiel
    esp_ = extr(pl(CONT.intersection(Polygon([(-80, -20), (80, -20), (80, 310), (-80, 310)]))), -E, E, 'aco_machado')
    cut(esp_, cyl((0, FURO, -20), (0, FURO, 20), 3.6, 'aco_machado', n=18))
    o.append(esp_)
    for v in PINOS:                                                              # pinos vazados
        zt = LARG(v) * 0.96 + 0.4
        o.append(lathe([(-zt, 1.4), (-zt, 2.5), (-zt + 0.5, 3.0), (zt - 0.5, 3.0), (zt, 2.5), (zt, 1.4)], 'inox', n=18, c0=(0, v, 0), eixo=(0, 0, 1), anel=True))
    return parte('cabeca', o, origem=(0, 300, 0), grupo='A', suave=32)


def _aneis(vs, folga=0.0, k=None):
    out = []
    for i, v in enumerate(vs):
        a, b = _faixa(v)
        f = k(i) if k else 1.0
        out.append([P(u, v, w) for u, w in superelipse(((b - a) / 2 + folga) * f, (LARG(v) + folga) * f, n=44, e=2.3, cx=(a + b) / 2)])
    return out


def cabo(pai):
    b = CONT.bounds
    vs = list(np.linspace(b[1] + 0.05, b[1] + 6, 8)) + list(np.linspace(b[1] + 8, 296, 90)) + [298.5, 299.5]
    n = len(vs)

    def k(i):
        if vs[i] - b[1] < 6:
            return 0.45 + 0.55 * ((vs[i] - b[1]) / 6) ** 0.5
        if vs[i] > 297:
            return 0.80 + 0.20 * ((299.6 - vs[i]) / 2.6) ** 0.5
        return 1.0
    talas = loft(_aneis(vs, -0.02, k), 'polim_oliva')
    cut(talas, [box(-80, 80, -40, 340, -E, E, 'polim_oliva'), cyl((0, FURO, -30), (0, FURO, 30), 4.0, 'polim_oliva', n=18)] +
        [cyl((0, v, -30), (0, v, 30), 3.0, 'polim_oliva', n=18) for v in PINOS])
    o = [talas]
    # cordão enrolado no meio do cabo (as voltas vêm do relevo da textura)
    vc = [63.0, 63.6, 64.6] + list(np.linspace(66, 188, 40)) + [189.4, 190.4, 191.0]
    kc = lambda i: 1.0 if 2 < i < len(vc) - 3 else (0.90, 0.955, 0.99)[min(i, len(vc) - 1 - i)]
    o.append(loft(_aneis(vc, 1.9, kc), 'cordao'))
    # fiel: argola de cordão no furo do pé
    arg = [(0, -4.5 + 10.5 * math.cos(a), 10.5 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 30, endpoint=False)]
    o.append(fio(arg, 1.7, 'cordao', fechado=True, res=3))
    return parte('cabo', o, origem=(0, 90, 0), pai=pai, grupo='A', suave=40)


def montar():
    f = cabeca()
    cabo(f)
