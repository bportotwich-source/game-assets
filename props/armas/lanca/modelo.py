"""Lança improvisada no nível de detalhe da M4A1: cabo de vassoura pintado de azul, com a tinta
lascada mostrando a madeira, rosca de plástico atrás e cordão no furo de pendurar; pega de trás de
fita prata e pega da frente de tira de pano enrolada; na ponta, uma faca de cozinha sem as talas
presa com fita prata, arame, um prego atravessado e duas abraçadeiras de mangueira.
Desenho próprio, sem marcas.

Mesmas medidas da lança antiga (arma21_lanca.py): os nós (amarração e faca saem na animação),
os pontos das mãos, da ponta e do fio e as animações continuam valendo.

Coordenadas em mm (lib.py da M4A1): u = para a frente (ponta da faca), v = para cima (o fio da
faca fica para baixo), w = direita.
"""
import math
import numpy as np
from shapely.geometry import Polygon
from lib import *

U0, U1 = -448.0, 922.0             # cabo: rosca de trás até a ponta
R = 12.5                           # raio do cabo
XB, LB = 925.0, 200.0              # calcanhar da lâmina e comprimento
V_PONTA = -16.0
FITA_T = (-330.0, -166.0)          # pega de trás (fita prata)
PANO = (120.0, 292.0)              # pega da frente (pano)


def pl(g):
    return [(float(x), float(y)) for x, y in list(g.exterior.coords)[:-1]]


def arred(pts, r, n=6):
    g = Polygon(pts)
    return g.buffer(-r, quad_segs=n).buffer(2 * r, quad_segs=n).buffer(-r, quad_segs=n)


def _radial(x, a, r):
    return (x, r * math.cos(a), r * math.sin(a))


def _luva(u0, u1, mat, folga=1.5):
    """Faixa enrolada por cima do cabo (as voltas vêm do relevo da textura)."""
    r = R + folga
    return lathe([(u0, R - 1.0), (u0, r - 0.5), (u0 + 0.6, r), (u1 - 0.6, r), (u1, r - 0.5), (u1, R - 1.0)], mat, n=32, anel=True)


# ------------------------------------------------------------------ cabo
def cabo():
    rng = np.random.default_rng(21)
    us = sorted(set([-420.5, FITA_T[0], FITA_T[1], 790.0, U1 - 4] + [round(float(x), 1) for x in np.linspace(-410, 780, 60)]))
    prof = [(-420.5, 0.0)] + [(u, R) for u in us] + [(U1, R - 1.2), (U1, 0.0)]
    c = lathe(prof, 'cabo_pintado', n=32)
    pintar(c, 'fita_prata', lambda p, n: FITA_T[0] < p[0] < FITA_T[1])
    pintar(c, 'madeira_lasca', lambda p, n: p[0] > 791 or (p[0] < -420 and abs(n[0]) > 0.9))
    lascas = []                                                          # tinta lascada: a madeira aparece
    for x in list(rng.uniform(-410, -352, 4)) + list(rng.uniform(-145, 100, 8)) + list(rng.uniform(325, 780, 14)) + list(rng.uniform(700, 790, 5)):
        a = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(2.5, 6.0)
        k = rng.uniform(1.2, 2.6)
        lascas.append(lathe([(-r * k, 0.0)] + [(-r * k * math.cos(t), r * math.sin(t)) for t in np.linspace(0.3, math.pi - 0.3, 7)] + [(r * k, 0.0)],
                            'madeira_lasca', n=10, c0=_radial(x, a, R + 0.45 * r)))
    cut(c, lascas + [cyl((-405, 0, -30), (-405, 0, 30), 2.6, 'madeira_lasca', n=16)])
    o = [c]
    prof = [(U0, 0.0)]                                                   # rosca de plástico (ponta da vassoura)
    for k in range(8):
        x = U0 + 3 + k * 2.6
        prof += [(x, 7.8), (x + 1.3, 9.3)]
    prof += [(-425.5, 7.8), (-424.5, 9.5), (-421.0, R + 1.6), (-417.0, R + 1.6), (-417.0, R - 1.0)]
    o.append(lathe(prof, 'plastico_cinza', n=28))
    # cordão no furo de pendurar, com nó e duas pontas
    laco = [(-405, -24 + 24 * math.cos(t), 24 * math.sin(t) * 0.8) for t in np.linspace(0, 2 * math.pi, 36, endpoint=False)]
    o.append(fio(laco, 1.6, 'barbante', fechado=True, res=2))
    o.append(lathe([(-5, 0.0), (-4, 3.0), (0, 4.4), (4, 3.0), (5, 0.0)], 'barbante', n=12, c0=(-405, -49, 0), eixo=(0, 1, 0)))
    for dz in (-4, 4):
        o.append(fio([(-405, -51, dz * 0.5), (-403, -60, dz), (-401, -68, dz * 1.6)], 1.5, 'barbante', fechado=False, res=2))
    # pega da frente: tira de pano enrolada, com a ponta solta
    o.append(_luva(PANO[0], PANO[1], 'pano_vermelho'))
    o.append(fio(caminho_arred([(290.5, R + 1.2, 0), (299, R + 1.4, 6), (306, 8, 13.5), (311, -4, 15.5), (314, -18, 16)], 4.0, 4, fechado=False), 1.9, 'pano_vermelho', fechado=False, res=2))
    return parte('cabo', o, origem=(-250, 0, 0), grupo='A', suave=40)


# ------------------------------------------------------------------ amarração
def _abracadeira(xc):
    """Abraçadeira de mangueira: fita de aço, caixa do parafuso e parafuso sextavado."""
    o = [lathe([(xc - 4.5, R - 1.0), (xc - 4.5, R + 1.6), (xc + 4.5, R + 1.6), (xc + 4.5, R - 1.0)], 'inox', n=32, anel=True)]
    cx = extr(pl(arred([(xc - 6.2, R + 0.6), (xc + 6.2, R + 0.6), (xc + 6.2, R + 7.0), (xc - 6.2, R + 7.0)], 1.2)), -5.2, 5.2, 'inox')
    o.append(bevel(cx, 0.5, 2, 30))
    o.append(cyl((xc, R + 4.2, -7.5), (xc, R + 4.2, 6.2), 2.6, 'inox', n=14))
    cab = cyl((xc, R + 4.2, 6.2), (xc, R + 4.2, 9.4), 4.1, 'inox', n=6)
    cut(cab, box(xc - 0.6, xc + 0.6, R + 1.0, R + 7.4, 8.2, 10, 'inox'))
    o.append(cab)
    return o


def amarracao(pai):
    o = [_luva(806, 857, 'fita_prata'), _luva(897, 921, 'fita_prata')]
    o += _abracadeira(867) + _abracadeira(888)
    # prego atravessando cabo e espiga, com a ponta entortada do outro lado
    o.append(cyl((877.5, -2, -R - 1.6), (877.5, -2, R + 1.0), 1.4, 'aco_prego', n=10))
    o.append(lathe([(R + 0.3, 0.0), (R + 0.3, 3.0), (R + 1.0, 3.4), (R + 1.6, 3.2), (R + 1.8, 0.0)], 'prego_ferrugem', n=16, c0=(877.5, -2, 0), eixo=(0, 0, 1)))
    o.append(fio(caminho_arred([(877.5, -2, -R - 1.0), (878, -2, -R - 3.2), (881, -2, -R - 3.6), (889, -3, -R - 3.4)], 1.5, 3, fechado=False), 1.3, 'aco_prego', fechado=False, res=2))
    # arame enrolado por cima da fita, com o rabicho torcido
    t = np.linspace(0, 6 * 2 * math.pi, 220)
    rw = R + 1.5 + 0.9
    o.append(fio([(813 + 28 * a / t[-1], rw * math.cos(a), rw * math.sin(a)) for a in t], 0.8, 'arame_farpado', fechado=False, res=1))
    for s in (0, 1):
        o.append(fio([(841.5 + 0.9 * math.cos(9 * u * math.pi + s * math.pi), rw + 1 + 11 * u, 0.9 * math.sin(9 * u * math.pi + s * math.pi) + 4 * u) for u in np.linspace(0, 1, 26)],
                     0.7, 'arame_farpado', fechado=False, res=1))
    # ponta da fita descolando
    o.append(bevel(extr(pl(arred([(842, -R - 13), (858, -R - 15), (856, -R - 0.5), (845, -R - 0.5)], 1.5)), -0.7, 0.7, 'fita_prata'), 0.2, 1, 30))
    return parte('amarracao', o, origem=(860, 0, 0), pai=pai, grupo='A', suave=40)


# ------------------------------------------------------------------ faca de cozinha
def dorso(u):
    return 6.0 if u < 120 else 6.0 - (6.0 - V_PONTA) * ((u - 120) / 80) ** 1.8


def gume(u):
    return -34.0 + 1.0 * u / 100 if u < 100 else -33.0 + (V_PONTA + 33.0) * ((u - 100) / 100) ** 2.2


def _secao(u):
    ys, ye = dorso(u), gume(u)
    t = 1.1 * (1 - 0.45 * u / LB)
    H = ys - ye
    h = min(4.0, 0.3 * H)
    return [(t * 0.6, ys), (-t * 0.6, ys), (-t, ys - min(0.4, 0.1 * H)), (-t, ys - 0.5 * H), (-0.42, ye + h), (-0.09, ye),
            (0.09, ye), (0.42, ye + h), (t, ys - 0.5 * H), (t, ys - min(0.4, 0.1 * H))]


def faca(pai):
    us = list(np.linspace(0.0, LB - 3, 60))
    aneis = [[P(XB + u, v, w) for w, v in _secao(u)] for u in us]
    ult = _secao(LB - 3)
    yc = float(np.mean([y for _, y in ult]))
    aneis.append([P(XB + LB, yc + (v - yc) * 0.1, w * 0.1) for w, v in ult])
    lam = loft(aneis, 'aco_cozinha')
    pintar(lam, 'aco_lamina', lambda p, n: p[0] > XB + 3 and p[1] < gume(min(p[0] - XB, LB)) + min(4.0, 0.3 * (dorso(min(p[0] - XB, LB)) - gume(min(p[0] - XB, LB)))) * 0.98)
    o = [lam]
    # reforço (bolster) e espiga, que fica dentro do cabo
    o.append(bevel(extr(pl(arred([(XB - 8, -12), (XB + 1, -34), (XB + 3, -34), (XB + 3, 6.5), (XB - 8, 6.5)], 1.5)), -3.4, 3.4, 'aco_cozinha'), 0.8, 2, 30))
    o.append(extr(pl(arred([(810, -8.5), (XB - 7, -10.5), (XB - 7, 5.5), (810, 3.5)], 2.0)), -1.2, 1.2, 'aco_cozinha'))
    return parte('faca', o, origem=(XB, 0, 0), pai=pai, grupo='A', suave=32)


def montar():
    c = cabo()
    amarracao(c)
    faca(c)
