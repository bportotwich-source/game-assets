"""Empunhaduras frontais do jogo no nível de detalhe da M4A1: reta, curta (caramelo) e dobrável.
Desenho próprio, sem marcas.

Coordenadas em mm (lib.py da M4A1): u = para a frente, v = para cima, w = direita. A origem é a
face de baixo do guarda-mão (v = 0); a empunhadura desce para v negativo. Mesmas medidas de fora,
nó `haste` e animações dobrar/abrir das antigas.
"""
import math
from lib import *


def _anel(v, rx, ry, cu=0.0, e=2.9, n=32):
    return [P(cu + x, v, y) for (x, y) in superelipse(rx, ry, n=n, e=e)]


def _corpo(secoes, mat, cu=0.0, aspero=None, aspero_mat='polim_grip'):
    """Punho por seções [(v, raio em u, raio em w)], de cima para baixo. aspero = (v de cima, v de baixo) dos painéis."""
    fino = [secoes[0]]                                   # anéis a cada 4 mm no máximo (o ponto da mão é medido pelos vértices)
    for a, b in zip(secoes, secoes[1:]):
        k = max(1, math.ceil(abs(b[0] - a[0]) / 4.0))
        fino += [tuple(a[i] + (b[i] - a[i]) * j / k for i in range(3)) for j in range(1, k + 1)]
    g = loft([_anel(v, rx, ry, cu) for (v, rx, ry) in fino], mat)
    if aspero:
        pintar(g, aspero_mat, lambda c, n: abs(n[2]) > 0.72 and aspero[1] < c[1] < aspero[0])
    return g


def _nervuras(u, v0, v1, larg, mat, passo=5.0, fundo=1.7):
    """Nervuras atrás do punho, para a palma não escorregar."""
    o = []
    v = v0
    while v > v1:
        o.append(bevel(box(u - fundo, u + 1.0, v - 2.2, v, -larg, larg, mat), 0.5, 1))
        v -= passo
    return o


def _porcas(us, v, meia, mat='inox'):
    o = []
    for u in us:
        for s in (-1, 1):
            o.append(pin(u, v, 2.6, s * meia, s * (meia - 0.25), mat, n=6))
    return o


def empunhadura_reta(Pm='polim'):
    o = [bevel(box(-18, 18, -7.5, 0, -11.0, 11.0, Pm), 1.2, 2)]
    o += _porcas((-11, 11), -3.6, 11.2)
    secoes = [(-7.0, 12.4, 10.6), (-12, 11.2, 10.0), (-30, 11.0, 10.2), (-50, 11.4, 10.6), (-66, 11.6, 10.8), (-72, 11.2, 10.4),
              (-74.8, 9.6, 8.8), (-76, 6.5, 5.8)]
    o.append(_corpo(secoes, Pm, aspero=(-16, -64)))
    o += _nervuras(-11.4, -18, -62, 4.6, Pm)
    o.append(cyl((0, -76.0, 0), (0, -75.5, 0), 4.2, 'fosf', n=20))                           # tampa do compartimento
    return parte('punho', o, origem=(0, 0, 0), grupo='A')


def empunhadura_curta_tan(Pm='polim_caramelo'):
    o = [bevel(extr([(-25, 0), (28, 0), (28, -4), (22, -7.5), (-19, -7.5), (-25, -4)], -10.5, 10.5, Pm), 1.0, 2)]
    o += _porcas((-16, 19), -3.4, 10.7)
    secoes = [(-7.0, 17.5, 11.6), (-12, 15.5, 12.2), (-26, 14.0, 12.9), (-38, 13.6, 12.6), (-44, 12.4, 11.4), (-46.4, 10.0, 9.0), (-47.3, 6.0, 5.2)]
    o.append(_corpo(secoes, Pm, cu=1.5))
    for v in (-18, -24, -30, -36):                                                          # frisos em volta, para os dedos
        o.append(loft([_anel(v + 1.1, 14.2, 12.8, 1.5), _anel(v + 0.6, 15.6, 14.3 - 1.4, 1.5), _anel(v - 0.6, 15.6, 14.3 - 1.4, 1.5), _anel(v - 1.1, 14.0, 12.6, 1.5)], Pm))
    return parte('punho', o, origem=(0, 0, 0), grupo='A')


PU, PVD = -12.0, -7.5      # eixo da dobradiça da empunhadura dobrável


def empunhadura_dobravel():
    Pm = 'polim'
    b = [bevel(box(-22, 18, -4.6, 1.5, -12.5, 12.5, Pm), 1.0, 2)]
    for s in (-1, 1):                                                                        # orelhas da dobradiça
        b.append(bevel(extr([(PU - 7, -4), (PU + 7, -4), (PU + 6, PVD - 3.5), (PU + 2.5, PVD - 6), (PU - 2.5, PVD - 6), (PU - 6, PVD - 3.5)],
                            s * 8.0, s * 12.5, Pm), 0.8, 1))
    b.append(pin(PU, PVD, 2.0, -13.0, 13.0, 'fosf', n=12))                                   # eixo
    b.append(pin(PU, PVD, 3.4, 12.5, 13.0, 'fosf', n=6))
    b += _porcas((8,), -1.6, 12.7)
    b.append(bevel(box(-2, 6, -6.4, -4.4, -4, 4, 'fosf'), 0.4, 1))                           # trava que segura a haste aberta
    base = parte('base', b, origem=(0, 0, 0), grupo='A')
    h = [pin(PU, PVD, 5.2, -7.6, 7.6, Pm, n=24)]
    secoes = [(PVD - 3.0, 7.0, 7.4), (-15, 9.6, 9.4), (-30, 9.8, 9.8), (-52, 10.2, 10.2), (-68, 10.4, 10.4), (-72.5, 9.4, 9.4), (-75.5, 6.0, 6.0)]
    h.append(_corpo(secoes, Pm, cu=PU + 0.5, aspero=(-20, -66)))
    h += _nervuras(PU + 0.5 - 9.9, -22, -64, 4.2, Pm)
    h.append(cyl((PU + 0.5, -75.5, 0), (PU + 0.5, -75.0, 0), 3.8, 'fosf', n=20))
    parte('haste', h, origem=(PU, PVD, 0), pai=base, grupo='A')
    return base


def empunhadura_reta_tan():
    return empunhadura_reta('polim_caramelo')


def empunhadura_curta():
    return empunhadura_curta_tan('polim')


def _base(meio, mat, larg=11.0):
    """Sapata que prende nos rasgos de baixo do guarda-mão, com as duas porcas de cada lado."""
    o = [bevel(box(-meio, meio, -7.5, 0, -larg, larg, mat), 1.2, 2)]
    return o + _porcas((-meio + 7, meio - 7), -3.6, larg + 0.2)


def empunhadura_vertical():
    """Alta e arredondada, com as ondas dos dedos na frente e tampa de rosca embaixo."""
    Pm = 'polim'
    o = _base(20, Pm)
    secoes = [(-7.0, 16.0, 11.4), (-14, 14.6, 11.8), (-24, 13.6, 12.4), (-34, 14.4, 12.9), (-44, 13.6, 13.2), (-54, 14.6, 13.4), (-64, 13.8, 13.2),
              (-74, 14.8, 13.0), (-84, 14.2, 12.8), (-91, 14.6, 12.6), (-94.5, 13.0, 11.6), (-96, 10.5, 9.6)]
    o.append(_corpo(secoes, Pm, aspero=(-20, -86)))
    o += _nervuras(-13.6, -22, -84, 5.0, Pm)
    o.append(cyl((0, -95.6, 0), (0, -98.6, 0), 9.5, 'serr', n=36, lobes=0.06))                # tampa do compartimento de pilhas
    o.append(cyl((0, -98.6, 0), (0, -99.0, 0), 7.6, 'fosf', n=24))
    o.append(box(-5.0, 5.0, -99.3, -99.0, -0.7, 0.7, 'inox'))                                # fenda de moeda
    return parte('punho', o, origem=(0, 0, 0), grupo='A')


def empunhadura_angulada():
    """Rampa para a palma, com degraus atrás e apoio do polegar na frente."""
    Pm = 'polim'
    o = [bevel(box(-36, 36, -6.0, 0, -11.0, 11.0, Pm), 1.0, 2)]
    o += _porcas((-27, 27), -3.0, 11.2)
    cunha = extr([(-34, -5), (34, -5), (32, -13), (21, -30), (9, -37), (-3, -34.5), (-32, -12)], -11.6, 11.6, Pm)
    o.append(bevel(cunha, 2.6, 3))
    du, dv = 29.0, -22.5                                                                     # direção da rampa, de trás para a frente
    L = math.hypot(du, dv)
    tu, tv = du / L, dv / L
    nu, nv = tv, -tu                                                                         # para fora da rampa (para baixo e para trás)
    for i in range(6):                                                                       # degraus da rampa
        cu, cv = -29.0 + tu * (5 + i * 5.0), -13.6 + tv * (5 + i * 5.0)
        o.append(bevel(extr([(cu - tu * 1.3 - nu * 1.0, cv - tv * 1.3 - nv * 1.0), (cu + tu * 1.3 - nu * 1.0, cv + tv * 1.3 - nv * 1.0),
                             (cu + tu * 0.8 + nu * 1.0, cv + tv * 0.8 + nv * 1.0), (cu - tu * 0.8 + nu * 1.0, cv - tv * 0.8 + nv * 1.0)],
                            -9.0, 9.0, 'polim_grip'), 0.3, 1))
    for s in (-1, 1):                                                                        # apoio do polegar de cada lado
        o.append(bevel(extr([(14, -7), (33, -7), (31, -13), (24, -18), (16, -14)], s * 11.2, s * 13.0, Pm), 0.7, 1))
    return parte('punho', o, origem=(0, 0, 0), grupo='A')


def _quadrado(v, r, e=5.5, n=40):
    return [P(x, v, y) for (x, y) in superelipse(r, r, n=n, e=e)]


def empunhadura_quadrada():
    """Alta, de seção quadrada com cantos chanfrados, três sulcos e tampa recartilhada."""
    Pm = 'polim'
    o = _base(22, Pm, 11.5)
    o.append(bevel(extr([(-20, -6), (20, -6), (20, -11), (13.5, -24), (-13.5, -24), (-20, -11)], -12.6, 12.6, Pm), 1.4, 2))    # cabeça
    cortes = (-44, -64, -84)
    v0 = -22.0
    for c in cortes + (-108.0,):
        topo = v0
        fundo = c + 1.0 if c in cortes else c
        aneis = [_quadrado(topo, 12.6), _quadrado(topo - 1.0, 13.5)]
        v = topo - 1.0
        while v - 4.0 > fundo + 1.0:
            v -= 4.0
            aneis.append(_quadrado(v, 13.5))
        aneis += [_quadrado(fundo + 1.0, 13.5), _quadrado(fundo, 12.6)]
        g = loft(aneis, Pm)
        pintar(g, 'polim_grip', lambda cc, nn, a=topo - 3, b=fundo + 3: max(abs(nn[0]), abs(nn[2])) > 0.9 and b < cc[1] < a)
        o.append(g)
        v0 = c - 1.0
    o.append(loft([_quadrado(v, 12.4) for v in (-21.0, -40.0, -60.0, -80.0, -100.0, -108.5)], Pm))        # miolo, visto no fundo dos sulcos
    o.append(loft([_quadrado(-108.0, 14.1), _quadrado(-110.5, 14.1)], Pm))
    o.append(cyl((0, -110.5, 0), (0, -117.6, 0), 12.5, 'serr', n=44, lobes=0.05))
    o.append(cyl((0, -117.6, 0), (0, -119.0, 0), 10.5, 'anod', n=32))
    return parte('punho', o, origem=(0, 0, 0), grupo='A')


def empunhadura_cilindrica():
    """Cilindro de alumínio recartilhado num bloco inclinado."""
    A = 'anod'
    o = _base(22, A)
    o.append(bevel(extr([(-22, -5), (22, -5), (20, -13), (16, -30), (-5, -30), (-20, -12)], -11.0, 11.0, A), 1.2, 2))
    a = math.radians(-100)
    eu, ev = math.cos(a), math.sin(a)
    pt = lambda t: (6.0 + eu * t, -26.0 + ev * t, 0.0)
    R = 15.5
    for t0, t1, r, mat, lob in ((0, 2, None, A, 0), (2, 12, R, A, 0), (12, 38, R + 0.5, 'serr', 0.035), (38, 38.6, R, A, 0), (38.6, 40.1, R + 0.9, A, 0),
                                (40.1, 41.9, R, A, 0), (41.9, 43.4, R + 0.9, A, 0), (43.4, 44, R, A, 0), (44, 78, R + 0.5, 'serr', 0.035),
                                (78, 87, R, A, 0), (87, 90, None, A, 0)):
        if r is None:
            o.append(cyl(pt(t0), pt(t1), R - 2.4 if t0 == 0 else R, A, n=48, r1=R if t0 == 0 else R - 3.0))
        else:
            o.append(cyl(pt(t0), pt(t1), r, mat, n=48, lobes=lob))
    o.append(cyl(pt(90), pt(90.5), 8.5, 'fosf', n=6))                                        # parafuso de baixo
    return parte('punho', o, origem=(0, 0, 0), grupo='A')


def batente_mao():
    """Gancho vazado: a mão encosta nele e não escorrega para a frente."""
    Pm = 'polim'
    o = [bevel(box(-34, 34, -6.0, 0, -9.0, 9.0, Pm), 0.9, 2)]
    o += _porcas((-25, 25), -3.0, 9.2)
    fora = [(34, -5), (-36, -5), (-42, -12), (-42, -30), (-34, -44), (-22, -46), (-12, -36), (20, -12), (34, -8.5)]
    g = extr(fora, -7.5, 7.5, Pm)
    cut(g, [extr([(-12, -11.5), (-31, -11.5), (-35, -20), (-33, -33), (-25, -37), (-18, -30)], -9, 9, Pm)])
    o.append(bevel(g, 1.6, 3))
    for i in range(5):                                                                       # frisos onde a mão encosta (atrás do gancho)
        v = -15.0 - i * 4.0
        o.append(bevel(box(-43.0, -41.5, v - 1.2, v + 1.2, -6.0, 6.0, 'polim_grip'), 0.4, 1))
    return parte('punho', o, origem=(0, 0, 0), grupo='A')
