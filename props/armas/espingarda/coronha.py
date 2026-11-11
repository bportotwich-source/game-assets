"""Coronha retrátil da Mutirão 12 (acessório coronha_retratil_12) no nível de detalhe da M4A1:
tubo com trilho de 5 posições, colar recartilhado encostado no receptor e corpo de polímero
com soleira de borracha, trava e zarelho. É a coronha da M4A1 levada para o encaixe da
espingarda; o corpo (nó "soleira") corre no tubo. Desenho próprio, sem marcas.

Coordenadas em mm, as mesmas do modelo.py (a coronha já fica no lugar de montagem).
"""
import math
import bpy
from mathutils import Matrix
from lib import *

ENC = (-35.0, -4.0)               # encaixe_coronha: fundo do receptor, eixo do tubo
DU, DV = ENC[0] + 197.0, ENC[1]   # da M4A1 (tubo começa em u = -197, v = 0) para a espingarda


def mv(o):
    o.data.transform(Matrix.Translation(P(DU, DV, 0)))
    return o


def montar():
    tubo = mv(lathe([(-185, 0), (-185, 14.6), (-391, 14.6), (-393, 13.4), (-393, 0)], 'anod_tubo', n=32))    # entra 12 mm no receptor
    trilho = bevel(box(-391, -232, -21.5, -12, -4.8, 4.8, 'anod_tubo'), 0.6, 1)
    cut(trilho, [cyl((u, -25, 0), (u, -17, 0), 3.2, 'anod_tubo', n=12) for u in (-262, -290, -318, -346, -374)])
    colar = mv(lathe([(-209, 14.7), (-209, 15.4), (-207.5, 16.3), (-198.5, 16.3), (-197, 15.6), (-197, 14.7)],
                     'fosf', n=36, lobes=0.06, lobe_min=16.0, anel=True))
    t = parte('tubo_coronha', [tubo, mv(trilho), colar], origem=ENC + (0,), grupo='C')

    # corpo da coronha
    sec = arco(0, 0, 19.6, 0, 180, 12) + [(-19.6, -6), (-17.5, -30), (-14, -36.5), (14, -36.5), (17.5, -30), (19.6, -6)]
    U0, U1 = -270, -436
    luva = extr(sec, U1, U0, 'polim', plane='wv')
    cortes = [cyl((-405, 0, 0), (-260, 0, 0), 15.1, 'polim', n=28),
              box(-405, -260, -22.5, -8, -5.4, 5.4, 'polim')]
    for i in range(4):
        u = -283 - i * 26.5
        for s in (-1, 1):
            cortes.append(box(u - 22, u, -29, -10, s * 16.6, s * 26, 'polim'))
    for s in (-1, 1):
        cortes.append(box(-434, -396, 6, 12.5, s * 17.2, s * 26, 'polim'))
    cut(luva, cortes)
    bevel(luva, 1.1, 2, 35)
    alma = extr([(-300, -35), (-438, -35), (-440, -108), (-428, -108)], -4.2, 4.2, 'polim')
    cut(alma, [extr(ret_arred(-431, -401, -47, -41, 2.5, 3), -10, 10, 'polim')])        # passador da bandoleira
    bevel(alma, 0.6, 1)
    viga = bevel(extr([(-291, -35), (-312, -35), (-437, -101.5), (-437, -114.5), (-427, -114.5)], -8, 8, 'polim'), 1.6, 2)
    sol = extr([(-434, 19.6), (-446.5, 17), (-449.5, -114.5), (-434, -114.5)], -17.5, 17.5, 'borracha')
    bevel(sol, 2.2, 2, 35)
    cut(sol, [box(-455, -445.5 + 0.0228 * (v - 17), v - 2.2, v, -14.5, 14.5, 'borracha') for v in range(10, -108, -5)])
    bloco = bevel(box(-336, -296, -44, -35, -9, 9, 'polim'), 1.0, 1)
    c = parte('coronha_corpo', [mv(x) for x in (luva, alma, viga, sol, bloco)], origem=(U0 + DU, DV, 0), grupo='C', suave=40)
    tr = bevel(extr([(-299, -44), (-344, -44), (-346, -47), (-333, -49.5), (-303, -52.5), (-298, -50)], -7.2, 7.2, 'polim'), 1.2, 2)
    parte('trava_coronha', [mv(x) for x in (tr, cyl((-318, -52, 0), (-318, -25, 0), 3.0, 'fosf', n=12),
                                            pin(-306, -46, 1.4, -9.3, 9.3, 'inox', n=8))], origem=(-306 + DU, -46 + DV, 0), grupo='C')
    laco = caminho_arred([(-437, -112, -6), (-437, -112, -15), (-446, -133, -15), (-446, -133, 15),
                          (-437, -112, 15), (-437, -112, 6)], 3.5, 5)
    parte('zarelho_traseiro', [mv(x) for x in (fio(laco, 1.7, 'fosf'), pin(-437, -112, 2.6, -9.4, 9.4, 'fosf', n=12))],
          origem=(-437 + DU, -112 + DV, 0), grupo='C')
    return t
