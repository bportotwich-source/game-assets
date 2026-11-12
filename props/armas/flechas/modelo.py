"""Flechas e virotes soltos (munição dos arcos e da besta) no nível de detalhe da M4A1. São as
mesmas flechas modeladas com os arcos refeitos, uma por id. Desenho próprio, sem marcas.

Coordenadas em mm (lib.py da M4A1): u = para a frente. A origem é o entalhe (o ponto que encosta
na corda) e a flecha avança em u, com o eixo em v = w = 0. Mesmos comprimentos das antigas.
"""
import math
from mathutils import Matrix
from lib import *


def _gira(o, graus):
    o.data.transform(Matrix.Rotation(math.radians(graus), 4, P(1, 0, 0).normalized()))
    return o


# id: comprimento total, raio da haste, haste, entalhe, pena ímpar, outras penas, ponta, comprimento da pena, virote?
SPECS = {
    'flecha_caca':          (732, 3.6, 'haste_fibra', 'nock_branco', 'pena_branca', 'pena_laranja', 'caca', 77, False),
    'flecha_campo':         (724, 3.6, 'haste_fibra', 'nock_branco', 'pena_branca', 'pena_verde', 'campo', 77, False),
    'flecha_prego':         (758, 4.0, 'haste_madeira', 'nock_branco', 'pena_branca', 'pena_branca', 'prego', 77, False),
    'flecha_carbono':       (766, 3.1, 'carbono', 'nock_vermelho', 'pena_laranja', 'pena_verde', 'caca', 45, False),
    'flecha_carbono_campo': (756, 3.1, 'carbono', 'nock', 'pena_laranja', 'pena_verde', 'campo', 45, False),
    'virote_caca':          (462, 4.3, 'carbono', 'nock_vermelho', 'pena_branca', 'pena_vermelha', 'caca', 55, True),
    'virote_campo':         (450, 4.3, 'carbono', 'nock_vermelho', 'pena_branca', 'pena_branca', 'campo', 55, True),
    'virote_prego':         (472, 4.6, 'haste_madeira', 'nock_branco', 'pena_laranja', 'pena_laranja', 'prego', 55, True),
}
PONTA = {'caca': 34.0, 'campo': 24.0, 'prego': 46.0}       # quanto a ponta passa da haste


def flecha(qual):
    total, r, haste, nock_m, pena0, pena1, ponta, lp, virote = SPECS[qual]
    L = total - PONTA[ponta]                                 # fim da haste
    o = []
    if virote:                                               # entalhe em meia-lua
        nock = lathe([(0, 0), (0, r + 0.3), (12, r + 0.3), (14, r), (14, 0)], nock_m, n=20)
        cut(nock, cyl((-1.2, 0, -10), (-1.2, 0, 10), 3.4, nock_m, n=16))
        n0 = 14
    else:                                                    # entalhe de fenda que abraça a corda
        nock = lathe([(0, 0), (0, 2.4), (1.6, 3.4), (5.5, r + 0.7), (10.5, r + 0.7), (12, r), (12, 0)], nock_m, n=20)
        cut(nock, box(-2, 5.4, -8, 8, -1.3, 1.3, nock_m))
        n0 = 12
    o.append(bevel(nock, 0.25, 1, 40))
    o.append(lathe([(n0, 0), (n0, r), (L, r), (L, 0)], haste, n=20))
    u_p = 24 if not virote else 30                           # começo das penas
    if haste != 'haste_madeira':
        o.append(lathe([(u_p - 6, r + 0.02), (u_p - 6, r + 0.13), (u_p + lp + 8, r + 0.13), (u_p + lp + 8, r + 0.02)], 'envoltorio', n=20, anel=True))
    h = 12.6 if lp > 70 else 9.2
    perfil = [(0, 0), (0.03, 0.43), (0.11, 0.8), (0.24, 0.98), (0.45, 1.0), (0.70, 0.8), (0.9, 0.4), (1.0, 0)]
    for k in range(3):
        pena = extr([(u_p + a * lp, r - 0.3 + b * h) for a, b in perfil], -0.5, 0.5, pena0 if k == 0 else pena1)
        o.append(_gira(bevel(pena, 0.18, 1, 40), (180 if virote else -90) + 120 * k))
    if ponta == 'prego':                                     # prego amarrado com fita na ponta da haste
        o.append(cyl((L - 30, r + 1.3, 0), (L + 40, r * 0.25, 0), 1.7, 'prego_velho', n=10, r1=1.5))
        o.append(cyl((L + 40, r * 0.25, 0), (L + 46, 0, 0), 1.5, 'prego_velho', n=10, r1=0.15))
        o.append(cyl((L - 31.2, r + 1.3, 0), (L - 30, r + 1.3, 0), 3.4, 'prego_velho', n=12))
        o.append(lathe([(L - 24, 0), (L - 24, r + 3.5), (L - 2, r + 3.3), (L - 2, 0)], 'fita_cinza', n=18, c0=(0, 0.9, 0)))
        o.append(lathe([(L - 3, 0), (L - 3, r), (L, r * 0.7), (L, 0)], haste, n=20))
    else:
        o.append(lathe([(L - 6, r + 0.02), (L - 6, r + 0.4), (L + 1, r + 0.4), (L + 1, r + 0.02)], 'aluminio_flecha', n=20, anel=True))
        if ponta == 'campo':                                 # ponta de campo: ogiva simples de aço
            o.append(lathe([(L, 0), (L, r + 0.3), (L + 8, r + 0.3), (L + 15, r * 0.7), (L + 24, 0)], 'aco_ponta', n=20))
        else:                                                # ponta de caça: corpo de aço e 3 lâminas vazadas
            o.append(lathe([(L, 0), (L, 3.4), (L + 4, 4.1), (L + 12, 3.9), (L + 20, 3.2), (L + 34, 0)], 'aco_ponta', n=20))
            for k in range(3):
                lam = extr([(L + 2, 1.6), (L + 29, 1.2), (L + 8, 12.4), (L + 2, 11.0)], -0.42, 0.42, 'aco_lamina')
                cut(lam, extr([(L + 4.4, 4.9), (L + 16, 4.6), (L + 8.4, 9.2), (L + 4.4, 8.6)], -2, 2, 'aco_lamina'))
                o.append(_gira(lam, -30 + 120 * k))
    return parte('flecha', o, origem=(0, 0, 0), grupo='A', suave=40)
