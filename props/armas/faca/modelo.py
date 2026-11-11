"""Faca de combate no nível de detalhe da M4A1: lâmina de 18 cm de aço escurecido com ponta
recortada, falso fio, desbaste plano, fio polido, serrilha perto do cabo e sulco; guarda de aço
com o braço de baixo curvado para a frente; cabo de polímero pontilhado com frisos e cavas para
os dedos; espaçador de aço; pomo com quebra-vidro, furo e cordão. Desenho próprio, sem marcas.

O contorno da lâmina é o da faca antiga (arma18_faca.py), para a bainha de cinto e os pontos
de acerto (ponta, meio do fio) continuarem valendo.

Coordenadas em mm (lib.py da M4A1): u = para a frente (ponta), v = para cima (dorso), w = direita.
u = 0 é a face da frente da guarda.
"""
import math
import numpy as np
from shapely.geometry import Polygon, LineString
from lib import *

L = 178.0                          # comprimento da lâmina


def dorso(x):
    if x <= 105:
        return 12.0
    s = (x - 105) / (L - 105)
    return 12.0 - 11.2 * (1 - (1 - s) ** 2)


def gume(x):
    if x < 8:
        return -16.5
    if x < 16:
        s = (x - 8) / 8
        return -16.5 + 4.5 * math.sin(math.pi * s) - 2.5 * s          # cava do dedo (choil)
    if x <= 120:
        return -19.0
    s = (x - 120) / (L - 120)
    return -19.0 + 19.8 * s ** 2.2


def esp(x):
    return 2.6 if x <= 100 else 2.6 - 2.0 * ((x - 100) / (L - 100)) ** 1.3


def pl(g):
    return [(float(x), float(y)) for x, y in list(g.exterior.coords)[:-1]]


def arred(pts, r, n=6):
    g = pts if hasattr(pts, 'exterior') else Polygon(pts)
    return g.buffer(-r, quad_segs=n).buffer(2 * r, quad_segs=n).buffer(-r, quad_segs=n)


def curva(pts, n=2):
    for _ in range(n):
        q = []
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            q += [(0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]), (0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1])]
        pts = q
    return Polygon(pts)


def _secao(x):
    """Seção da lâmina em x: dorso com falso fio, lados planos, desbaste e o chanfro do fio."""
    yt, yb, t = dorso(x), gume(x), esp(x)
    e = 0.12
    H = yt - yb
    sc = 0.0 if x <= 105 else (x - 105) / (L - 105)
    sw = min(0.6 + 3.5 * sc, 0.3 * H)
    tt = t * (1 - 0.75 * sc) if sc else t * 0.82
    yg = min(yb + 0.45 * H, yt - sw - 0.05 * H)
    h = min(3.2, 0.3 * H)
    z1 = e + (t - e) * h / max(yg - yb, 0.05)
    return [(tt, yt), (-tt, yt), (-t, yt - sw), (-t, yg), (-z1, yb + h), (-e, yb), (e, yb), (z1, yb + h), (t, yg), (t, yt - sw)]


def lamina():
    xs = list(np.linspace(-4, 8, 4)) + list(np.linspace(8.5, 16, 10)) + list(np.linspace(17, L - 1.5, 80))
    aneis = [[P(x, v, w) for w, v in _secao(max(x, 0.0))] for x in xs]
    ult = _secao(L - 1.5)
    yc = float(np.mean([y for _, y in ult]))
    aneis.append([P(L, yc + (v - yc) * 0.08, w * 0.08) for w, v in ult])
    lam = loft(aneis, 'fosf')
    pintar(lam, 'aco_lamina', lambda p, n: p[0] > 16 and p[1] < gume(min(p[0], L)) + min(3.2, 0.35 * (dorso(min(p[0], L)) - gume(min(p[0], L)))) * 0.98 and abs(n[2]) > 0.5)
    cortes = [cyl((x, gume(x) - 1.1, -10), (x, gume(x) - 1.1, 10), 2.7, 'aco_lamina', n=18) for x in np.linspace(21, 47, 6)]      # serrilha
    for s in (1, -1):                                                                                                         # sulco
        g = LineString([(30, 3.5), (92, 3.5)]).buffer(2.6, 8)
        a, b = sorted((s * 1.15, s * 20))
        cortes.append(bevel(extr(pl(g), a, b, 'fosf'), 0.5, 2, 30))
    cut(lam, cortes)
    o = [lam]
    o.append(texto('RC 180', 2.4, 11, 2.0, -(2.6 + 0.02), mat='tinta', alinhar='LEFT'))
    o.append(texto('1095', 1.8, 11, -3.4, 2.6 + 0.02, mat='tinta', lado=1, alinhar='LEFT'))
    # guarda de aço: o braço de baixo curva para a frente e protege o dedo
    gd = curva([(-8, 19), (0.5, 19), (0.5, -23), (7, -31), (4.5, -36), (-3, -32), (-8, -25)], 2)
    o.append(bevel(extr(pl(gd), -6.8, 6.8, 'aco_brasa'), 1.5, 3, 30))
    # espaçador de aço entre a guarda e o cabo
    o.append(loft([[P(u, v, w) for w, v in superelipse(12.6, 16.6, n=36, e=2.4, cy=-3.6)] for u in (-13.0, -8.0)], 'inox'))
    # pomo com furo do cordão e quebra-vidro
    pm = curva([(-123, 12.5), (-132, 12.0), (-138.5, 6), (-138.5, -12), (-131, -19.5), (-123, -19.5)], 2)
    b = pm.bounds
    aneis = []
    for u in np.linspace(b[0] + 0.05, -123, 16):
        x = pm.intersection(LineString([(u, -60), (u, 60)])).bounds
        k = min(1.0, 0.45 + 0.55 * ((u - b[0]) / 5.0) ** 0.5) if u - b[0] < 5 else 1.0
        aneis.append([P(u, v, w) for w, v in superelipse(11.8 * k, (x[3] - x[1]) / 2, n=36, e=2.6, cy=(x[1] + x[3]) / 2)])
    pomo = loft(aneis, 'aco_brasa')
    cut(pomo, cyl((-130.5, -4.5, -20), (-130.5, -4.5, 20), 2.8, 'aco_brasa', n=18))
    o.append(pomo)
    o.append(lathe([(-146.5, 0), (-142.5, 3.2), (-137.0, 4.0), (-137.0, 0)], 'inox', n=6, c0=(0, 3.5, 0)))
    f = parte('lamina', o, origem=(0, 0, 0), grupo='A', suave=32)
    return f


CONT = curva([(-7, 11), (-60, 13.5), (-110, 12.8), (-125, 11.2), (-127, -6), (-122, -19), (-105, -18.5), (-90, -21.5), (-75, -18.5), (-60, -21.5),
              (-45, -18.5), (-30, -21.5), (-16, -18), (-7, -18.5)], 3)
LARG = lambda x: 10.8 + 1.6 * math.exp(-((x + 70) / 35) ** 2)
FRISOS = [u for u in np.arange(-112, -24, 11.0)]


def _friso(u):
    """Quanto o cabo afunda em u (frisos de 3 mm de largura e 1,5 mm de fundo, com rampas)."""
    d = min(abs(u - f) for f in FRISOS)
    return 1.5 * max(0.0, min(1.0, (2.6 - d) / 1.1))


def cabo(pai):
    us = sorted(set([round(float(u), 3) for u in np.linspace(-124.5, -11.5, 70)] + [f + d for f in FRISOS for d in (-2.6, -1.5, 1.5, 2.6)]))
    aneis = []
    for u in us:
        x = CONT.intersection(LineString([(u, -60), (u, 60)])).bounds
        r = _friso(u)
        aneis.append([P(u, v, w) for w, v in superelipse(LARG(u) - r, (x[3] - x[1]) / 2 - r, n=44, e=2.3, cy=(x[1] + x[3]) / 2)])
    o = [loft(aneis, 'polim_arco_grip')]
    # cordão (fiel) passado no furo do pomo
    cai = lambda u: -4.5 - 0.012 * max(0.0, -130.5 - u) ** 1.7
    laco = [(u, cai(u), w) for u, w in ((-130.5, -13), (-130.5, 13), (-141, 17), (-158, 8), (-171, 2.2), (-171, -2.2), (-158, -8), (-141, -17))]
    o.append(fio(caminho_arred(laco, 5.0, 5), 1.7, 'corda_besta', fechado=True, res=3))
    o.append(lathe([(-176, 0), (-176, 3.0), (-175, 3.8), (-169, 3.8), (-168, 3.0), (-168, 0)], 'corda_reforco', n=14, c0=(0, cai(-172), 0)))   # nó
    return parte('cabo', o, origem=(-65, -3, 0), pai=pai, grupo='A', suave=40)


def montar():
    f = lamina()
    cabo(f)
