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


def empunhadura_reta():
    Pm = 'polim'
    o = [bevel(box(-18, 18, -7.5, 0, -11.0, 11.0, Pm), 1.2, 2)]
    o += _porcas((-11, 11), -3.6, 11.2)
    secoes = [(-7.0, 12.4, 10.6), (-12, 11.2, 10.0), (-30, 11.0, 10.2), (-50, 11.4, 10.6), (-66, 11.6, 10.8), (-72, 11.2, 10.4),
              (-74.8, 9.6, 8.8), (-76, 6.5, 5.8)]
    o.append(_corpo(secoes, Pm, aspero=(-16, -64)))
    o += _nervuras(-11.4, -18, -62, 4.6, Pm)
    o.append(cyl((0, -76.0, 0), (0, -75.5, 0), 4.2, 'fosf', n=20))                           # tampa do compartimento
    return parte('punho', o, origem=(0, 0, 0), grupo='A')


def empunhadura_curta_tan():
    Pm = 'polim_caramelo'
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
