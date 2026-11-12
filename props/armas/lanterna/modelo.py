"""Lanterna compacta de arma no nível de detalhe da M4A1: garra de trilho lateral, corpo recartilhado,
cabeça com coroa dentada, refletor, vidro e botão de borracha atrás. Desenho próprio, sem marcas.

GASTO = True troca alumínio e aço pelos mesmos materiais bem usados (id "_gasto").

Coordenadas em mm (lib.py da M4A1): u = para a frente, v = para cima, w = direita. A origem é a
face do trilho lateral; a lanterna fica para w positivo, com o eixo em w = 20 (nó `feixe` na frente).
"""
import math
from mathutils import Matrix
from lib import *

GASTO = False
WE, R = 20.0, 13.2        # eixo e raio da cabeça
U0, U1 = -45.0, 31.0


def _m(nome):
    return nome + '_gasto' if GASTO else nome


def _rev(prof, mat, furo=None, n=40, lobes=0.0, lobe_min=0.0):
    if furo is None:
        return lathe(prof, mat, n=n, c0=(0, 0, WE), lobes=lobes, lobe_min=lobe_min)
    return lathe([(prof[0][0], furo)] + list(prof) + [(prof[-1][0], furo)], mat, n=n, c0=(0, 0, WE), lobes=lobes, lobe_min=lobe_min, anel=True)


def lanterna():
    A = _m('anod')
    o = []
    # tampa de trás com o botão de borracha
    o.append(_rev([(U0 + 3, 0), (U0 + 3, 9.6), (U0 + 4, 10.6), (U0 + 13, 10.6), (U0 + 13.6, 9.8)], A, n=40, lobes=0.05, lobe_min=10.5))
    o.append(_rev([(U0, 0), (U0, 5.6), (U0 + 0.8, 6.6), (U0 + 3, 6.8)], 'borracha', n=28))
    # corpo recartilhado
    o.append(_rev([(U0 + 13.6, 9.8), (U0 + 14.2, 10.2), (-6, 10.2), (-5.4, 9.8)], _m('serr'), n=48, lobes=0.045, lobe_min=10.1))
    # pescoço e cabeça
    o.append(_rev([(-5.4, 9.8), (-4, 10.4), (2, 10.4), (6, R - 0.6), (8, R - 0.6), (8.6, R - 1.3), (9.8, R - 1.3), (10.4, R - 0.6),
                   (22, R - 0.6), (22.6, R - 1.2)], A, n=48))
    coroa = _rev([(22.6, R - 1.2), (23.2, R), (U1, R), (U1, R - 1.6), (26.2, R - 2.2)], _m('fosf'), furo=R - 2.9, n=48)
    dentes = []
    for k in range(6):                                                                         # coroa dentada (quebra vidro)
        c = cyl((U1 + 1.2, R + 1, 0), (U1 + 1.2, R - 6, 0), 3.4, A, n=14)
        c.data.transform(Matrix.Translation(P(0, 0, WE)))
        c.data.transform(Matrix.Translation(P(0, 0, WE)) @ Matrix.Rotation(math.radians(60 * k), 4, P(1, 0, 0).normalized()) @ Matrix.Translation(-P(0, 0, WE)))
        dentes.append(c)
    cut(coroa, dentes)
    o.append(coroa)
    # refletor fundo e o LED
    o.append(_rev([(26.0, R - 2.9), (16.0, 3.2), (15.6, 0)], 'refletor', n=40))
    # garra do trilho: braço até a face do trilho, mandíbula e o parafuso de aperto
    o.append(bevel(extr([(0, -9.5), (7.5, -9.5), (9.5, -6), (9.5, 6), (7.5, 9.5), (0, 9.5)], -22, 2, A, plane='wv'), 0.8, 2))
    o.append(bevel(box(-20, 0, -12.6, -9.0, 0, 5.0, A), 0.5, 1))
    o.append(bevel(box(-20, 0, 9.0, 12.6, 0, 5.0, A), 0.5, 1))
    o.append(cyl((-10, 12.6, 3.0), (-10, 15.6, 3.0), 3.4, _m('serr'), n=20, lobes=0.09))         # borboleta de aperto
    o.append(cyl((-10, 15.6, 3.0), (-10, 16.2, 3.0), 1.6, 'inox', n=8))
    o.append(texto('L-300', 2.2, 15.5, 0, WE + R - 0.56, mat='tinta', lado=1))
    m = parte('lanterna', o, origem=(0, 0, 0), grupo='A')
    parte('led', [cyl((15.7, 0, WE), (17.2, 0, WE), 2.6, 'led_frio', n=16)], origem=(0, 0, 0), grupo='A')
    parte('vidro', [cyl((25.6, 0, WE), (26.2, 0, WE), R - 2.95, 'lente_clara', n=40)], origem=(0, 0, 0), grupo='A')
    return m
