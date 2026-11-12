"""Apetrechos que o jogo monta nas armas, no nível de detalhe da M4A1: estribo da besta, soltador
de pulso do arco composto e os elásticos de câmara de pneu do fuzil. Desenho próprio, sem marcas.

Coordenadas em mm (lib.py da M4A1): u = para a frente, v = para cima, w = direita; a origem é o
encaixe de cada peça. Mesmas medidas de fora das antigas.
"""
import math
import numpy as np
from lib import *


def _curva(pts, n=8):
    """Catmull-Rom aberta passando pelos pontos."""
    p = [np.array(q, float) for q in pts]
    p = [p[0]] + p + [p[-1]]
    out = []
    for i in range(1, len(p) - 2):
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * ((2 * p[i]) + (-p[i - 1] + p[i + 1]) * t + (2 * p[i - 1] - 5 * p[i] + 4 * p[i + 1] - p[i + 2]) * t * t
                                    + (-p[i - 1] + 3 * p[i] - 3 * p[i + 1] + p[i + 2]) * t ** 3)))
    out.append(tuple(p[-2]))
    return out


def estribo_besta():
    S = 'aco_estribo'
    o = [lathe([(0, 0), (0, 9.5), (14, 9.5), (18, 7.0), (18, 0)], 'anod', n=28)]                   # bucha que entra no trilho da besta
    o.append(bevel(box(12, 20, -6, 6, -46, 46, S), 1.2, 2))                                      # travessa
    for s in (-1, 1):
        o.append(bevel(extr(ret_arred(-2, 20, -12, 12, 4.0), s * 34, s * 46, S, plane='uv'), 0.9, 2))
        o.append(pin(9, 0, 3.4, s * 46, s * 47.2, 'fosf', n=6))
    arco = _curva([(14, -4, 40), (40, -12, 75), (100, -30, 80), (140, -40, 50), (150, -42, 0), (140, -40, -50), (100, -30, -80), (40, -12, -75), (14, -4, -40)], 10)
    o.append(fio(arco, 5.8, S, fechado=False, res=4))
    meio = len(arco) // 2
    o.append(fio(arco[meio - 14:meio + 15], 8.5, 'borracha', fechado=False, res=4))              # sapata de borracha (o pé pisa aqui)
    return parte('estribo', o, origem=(0, 0, 0), grupo='A')


def soltador_pulso():
    o = []
    # cabeça: garras que fecham no laço D, corpo e gatilho de dedo
    for s in (-1, 1):
        o.append(bevel(extr([(-13, 0.4), (-2, 0.9), (2.6, 1.6), (3.7, 0.5), (2.2, 3.4), (-4, 4.6), (-13, 3.6)], -2.6, 2.6, 'inox') if s > 0 else
                       extr([(-13, -0.4), (-13, -3.6), (-4, -4.6), (2.2, -3.4), (3.7, -0.5), (2.6, -1.6), (-2, -0.9)], -2.6, 2.6, 'inox'), 0.4, 1))
    o.append(lathe([(-50, 0), (-50, 5.0), (-48, 6.2), (-34, 6.2), (-33, 5.4), (-27, 5.4), (-26, 6.2), (-14, 6.2), (-12, 4.6), (-12, 0)], 'anod', n=28))
    o.append(lathe([(-33, 5.42), (-33, 6.3), (-27, 6.3), (-27, 5.42)], 'anod_laranja', n=28, anel=True))
    o.append(bevel(extr([(-24, -5), (-19, -5), (-21.5, -21), (-24, -23.6), (-27.5, -22)], -2.2, 2.2, 'inox'), 0.6, 2))   # gatilho
    o.append(pin(-21.5, -6.5, 1.3, -3.2, 3.2, 'fosf', n=10))
    # haste de fita trançada até a pulseira
    o.append(lathe([(-112, 0), (-112, 3.4), (-50, 3.4), (-50, 0)], 'fita_nylon', n=14, lobes=0.0))
    for k in range(9):
        u = -108 + k * 6.6
        o.append(lathe([(u, 3.42), (u, 4.1), (u + 2.6, 4.1), (u + 2.6, 3.42)], 'fita_nylon', n=14, anel=True))
    o.append(bevel(box(-120, -110, -5.2, 5.2, -6.5, 6.5, 'inox'), 0.8, 1))                       # fivela
    # pulseira: cinta aberta em C com a almofada
    n = 40
    cinta = []
    for i in range(n + 1):
        a = math.radians(30 + 300 * i / n)                                                   # aberta do lado da haste
        c, s = math.cos(a), math.sin(a)
        cinta.append([P(-140 + r * c, -4 + dv, r * s) for (r, dv) in ((23.6, 19.0), (23.6, -19.0), (21.0, -19.0), (21.0, 19.0))])
    o.append(bevel(loft(cinta, 'fita_nylon'), 0.5, 1))
    return parte('soltador', o, origem=(0, 0, 0), grupo='A')


def elastico_ak():
    o = []
    n = 48
    for inc in (0.238, -0.238):                                                                 # duas tiras cruzadas em volta do guarda-mão
        aneis = []
        for i in range(n + 1):
            a = 2 * math.pi * i / n
            c, s = math.cos(a), math.sin(a)
            e = 2.8                                                                           # volta de cantos redondos (o guarda-mão é quase reto dos lados)
            cw, sv = math.copysign(abs(c) ** (2 / e), c), math.copysign(abs(s) ** (2 / e), s)
            aneis.append([P(du + inc * (rv * sv), rv * sv, rw * cw) for (rw, rv, du) in
                          ((21.5, 34.8, -4.0), (21.5, 34.8, 4.0), (19.7, 33.0, 4.0), (19.7, 33.0, -4.0))])
        o.append(bevel(loft(aneis, 'camara_pneu', cap=False), 0.35, 1))
    return parte('elastico', o, origem=(0, 0, 0), grupo='A')
