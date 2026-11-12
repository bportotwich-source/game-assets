"""Miras de ponto e miras de ferro rebatíveis do jogo, no nível de detalhe da M4A1. Desenho próprio,
sem marcas.

- mira_reflexa: mira de ponto de corpo baixo, com a janela redonda num capuz inclinado. A lente é
  uma peça separada (`lente`), que no jogo vira vidro transparente e recebe o ponto vermelho.
- alca_rebativel e massa_rebativel: miras de ferro que deitam (nó `lamina`, animação dobrar).

GASTO = True troca alumínio e aço pelos mesmos materiais bem usados (ids "_gasto").

Coordenadas em mm (lib.py da M4A1): u = para a frente, v = para cima, w = direita.
u = 0 no meio do suporte, v = 0 no topo do trilho.
"""
import math
import numpy as np
from lib import *

GASTO = False
D = -30.25         # o perfil da base é o da M4A1, que tem o topo do trilho em v = 30,25


def _m(nome):
    return nome + '_gasto' if GASTO else nome


def _base(u0, u1, topo, porcas=2, alavanca=False):
    """Base que abraça o trilho, com a barra de aperto e as porcas (ou a alavanca) do lado esquerdo."""
    b = extr([(-14.2, 22.6 + D), (-14.2, topo), (14.2, topo), (14.2, 22.6 + D), (11.0, 22.6 + D), (11.0, 0.0), (-11.0, 0.0),
              (-11.0, 22.6 + D)], u0, u1, _m('anod'), plane='wv')
    bevel(b, 0.8, 1)
    o = [b, bevel(box(u0 + 3, u1 - 3, 22.4 + D, 29.6 + D, -16.4, -14.0, _m('anod')), 0.5, 1)]
    for i in range(porcas):
        u = u0 + (u1 - u0) * (i + 0.5) / porcas
        o.append(pin(u, 27.5 + D, 5.0, -19.0, -16.3, _m('fosf'), n=6))
        o.append(pin(u, 27.5 + D, 2.2, -19.8, -18.9, 'inox', n=10))
    return o


# ------------------------------------------------------------------ mira reflexa
VL, UL, RL = 33.0, 26.5, 14.0      # centro da lente (altura, posição) e raio


def mira_reflexa():
    A = _m('anod')
    o = _base(-23, 29, 5.0, 2)
    # corpo baixo: caixa do emissor atrás, rampa até o capuz
    corpo = bevel(extr([(-34, 4.5), (-34, 17.5), (-30, 21.0), (-17, 21.0), (-12, 17.0), (20, 17.0), (20, 4.5)], -13.5, 13.5, A), 1.4, 2, 35)
    o.append(corpo)
    o.append(cyl((-17.2, 17.0, 0), (-15.6, 16.2, 0), 2.4, 'led', n=16))                    # emissor do ponto, virado para a lente
    # capuz: anel em volta da lente, cortado em diagonal atrás (o topo avança para trás como uma pala)
    capuz = lathe([(9, RL), (9, RL + 3.6), (33, RL + 3.6), (34, RL + 2.8), (34, RL)], A, n=48, c0=(0, VL, 0), anel=True)
    cut(capuz, [extr([(8, 4), (27.5, 4), (8, 54)], -25, 25, A)])
    bevel(capuz, 0.5, 1)
    o.append(capuz)
    # pés do capuz, dos dois lados, descendo até a base
    for s in (-1, 1):
        o.append(bevel(extr([(18, 4.5), (34, 4.5), (34, VL - 4), (26, VL - 4)], s * 13.2, s * 17.4, A), 1.0, 1))
    # ajustes: elevação em cima do corpo, deriva do lado direito
    o.append(cyl((-23.5, 20.8, 0), (-23.5, 23.2, 0), 4.6, _m('serr'), n=24, lobes=0.08))
    o.append(cyl((-23.5, 23.2, 0), (-23.5, 23.8, 0), 2.2, 'inox', n=10))
    o.append(pin(-23.5, 13.0, 4.6, 13.3, 15.9, _m('serr'), n=24, lobes=0.08))
    o.append(pin(-23.5, 13.0, 2.2, 15.9, 16.5, 'inox', n=10))
    # tampa da pilha (o ponto de trítio não usa, mas o corpo é o mesmo) e parafusos da tampa do lado esquerdo
    for u in (-2, 12):
        o.append(pin(u, 10.5, 1.7, -14.3, -13.4, _m('fosf'), n=6))
    # risco branco de alinhamento em cima do capuz
    o.append(box(13, 19, VL + RL + 3.62, VL + RL + 3.68, -0.5, 0.5, 'tinta'))
    o.append(texto('RC-7', 2.6, 4, 9.5, 13.56, mat='tinta', lado=1))
    m = parte('mira', o, origem=(0, 0, 0), grupo='A')
    parte('lente', [cyl((UL - 0.4, VL, 0), (UL + 0.4, VL, 0), RL - 0.05, 'lente_clara', n=48)], origem=(0, 0, 0), grupo='A')
    return m


def optica_reflexa():
    return {'tipo': 'ponto', 'aumento': [1, 1], 'ocular_m': [0.0, VL / 1000, round(-(UL - 0.4) / 1000, 4)],
            'raio_ocular_m': round((RL - 0.05) / 1000, 4), 'iluminado': True}


# ------------------------------------------------------------------ miras de ferro rebatíveis
PV = 6.0           # altura do eixo da dobradiça


def _pe():
    """Pé das miras rebatíveis: base curta no trilho, com um parafuso atravessado e as orelhas da dobradiça."""
    A = _m('anod')
    o = _base(-12, 12, 4.2, 1)
    for s in (-1, 1):
        o.append(bevel(extr([(-5.5, 3.5), (5.5, 3.5), (5.5, PV + 1.0), (3.2, PV + 3.6), (-3.2, PV + 3.6), (-5.5, PV + 1.0)], s * 9.3, s * 12.6, A), 0.7, 1))
    o.append(pin(0, PV, 1.9, -13.6, 13.6, _m('fosf'), n=12))                                # eixo
    o.append(pin(0, PV, 3.0, 12.6, 13.4, _m('fosf'), n=6))
    return parte('base', o, origem=(0, 0, 0), grupo='A')


def alca_rebativel():
    A = _m('anod')
    base = _pe()
    # lâmina: cubo na dobradiça, haste e o disco com o furo
    l = [pin(0, PV, 3.4, -9.0, 9.0, A, n=20),
         bevel(extr([(-4, PV + 1.0), (4, PV + 1.0), (3.2, 15.0), (-3.2, 15.0)], -8.6, 8.6, A), 0.8, 1)]
    disco = cyl((-1.6, 19.5, 0), (1.6, 19.5, 0), 5.0, A, n=32)
    cut(disco, [cyl((-3, 19.5, 0), (3, 19.5, 0), 1.25, A, n=20)])
    bevel(disco, 0.4, 1)
    l.append(disco)
    l.append(bevel(extr([(-1.6, 14.0), (1.6, 14.0), (1.6, 16.5), (-1.6, 16.5)], -6.0, 6.0, A), 0.4, 1))
    # botão de deriva do lado direito, recartilhado
    l.append(pin(0, 10.5, 3.9, 8.6, 12.6, _m('serr'), n=24, lobes=0.09))
    l.append(pin(0, 10.5, 1.6, 12.6, 13.1, 'inox', n=10))
    parte('lamina', l, origem=(0, PV, 0), pai=base, grupo='A')
    return base


def massa_rebativel():
    A = _m('anod')
    base = _pe()
    l = [pin(0, PV, 3.4, -9.0, 9.0, A, n=20),
         bevel(extr([(-4, PV + 1.0), (4, PV + 1.0), (3.4, 12.5), (-3.4, 12.5)], -8.6, 8.6, A), 0.8, 1)]
    for s in (-1, 1):                                                                       # orelhas de proteção
        l.append(bevel(extr([(-3.4, 12.0), (3.4, 12.0), (4.6, 17.5), (2.6, 23.6), (-0.6, 23.6), (-2.6, 17.5)], s * 5.6, s * 8.2, A), 0.7, 1))
    l.append(cyl((0.8, 12.0, 0), (0.8, 13.6, 0), 2.6, _m('serr'), n=16, lobes=0.12))        # roseta de elevação
    l.append(cyl((0.8, 13.6, 0), (0.8, 19.4, 0), 1.05, _m('fosf'), n=12))                   # poste
    l.append(cyl((0.8, 19.4, 0), (0.8, 19.5, 0), 0.95, 'tinta', n=12))                      # ponta branca
    parte('lamina', l, origem=(0, PV, 0), pai=base, grupo='A')
    return base


# ------------------------------------------------------------------ mira de pinos do arco composto
# Origem = bucha de cima do punho do arco (face direita). O aro fica para dentro, sobre a flecha.
UA, VA, WA, RA = 84.0, -33.0, -12.8, 21.5      # centro e raio de fora do aro
PINOS = ((8.0, 'verde'), (4.0, 'amarelo'), (0.0, 'vermelho'), (-4.0, 'verde'), (-8.0, 'amarelo'))   # 10 a 50 m


def mira_pinos():
    A = 'anod'
    # placa presa nas duas buchas do punho, com rasgos para subir e descer
    placa = bevel(extr(ret_arred(-14, 16, -30, 31, 4.0), 0.0, 5.0, A, plane='uv'), 0.7, 2)
    cut(placa, [extr(ret_arred(-9, -5, -8, 8, 1.9), -1, 6, A, plane='uv'), extr(ret_arred(7, 11, -8, 8, 1.9), -1, 6, A, plane='uv')])
    o = [placa]
    for (u, v) in ((-2, -21), (2, 21)):
        o.append(pin(u, v, 3.6, 5.0, 6.6, 'fosf', n=20))
        o.append(pin(u, v, 1.8, 6.6, 6.9, 'inox', n=6))
    # barra de cauda de andorinha com a escala, e o carro que corre nela
    o.append(bevel(extr([(2.0, -15), (8.0, -15), (11.2, -12.8), (11.2, -3.2), (8.0, -1), (2.0, -1)], 4, 66, A, plane='wv'), 0.5, 1))
    for i in range(13):
        u = 14 + i * 3.0
        o.append(box(u - 0.2, u + 0.2, -6.4 if i % 4 else -8.2, -3.2, 11.2, 11.26, 'tinta'))
    carro = bevel(extr(ret_arred(50, 72, -22, 6, 3.0), 1.0, 16.0, A, plane='uv'), 0.9, 2)
    o.append(carro)
    o.append(pin(61, -8, 6.4, 16.0, 24.0, 'anod_laranja', n=28, lobes=0.10))                # botão de altura
    o.append(pin(61, -8, 2.4, 24.0, 24.6, 'inox', n=6))
    o.append(pin(67, 2, 2.2, 16.0, 17.4, 'fosf', n=6))                                      # trava do carro
    for i in range(9):
        o.append(box(53.0, 55.5 if i % 4 else 57.0, -19.5 + i * 2.6, -19.1 + i * 2.6, 16.0, 16.06, 'tinta'))
    # cotovelo: do carro até o lado direito do aro
    o.append(bevel(extr([(66, -6), (66, -20), (76, VA - 7), (92, VA - 7), (92, VA + 7), (82, -6)], 5.6, 9.4, A, plane='uv'), 0.8, 2))
    # aro, com o friso claro virado para o arqueiro
    aro = lathe([(-8, RA - 3.0), (-8, RA - 0.6), (-7.4, RA), (7.4, RA), (8, RA - 0.6), (8, RA - 3.0)], A, n=56, c0=(UA, VA, WA), anel=True)
    o.append(aro)
    o.append(lathe([(-8.06, RA - 2.6), (-8.06, RA - 1.0), (-8.0, RA - 1.0), (-8.0, RA - 2.6)], 'tinta_viva', n=56, c0=(UA, VA, WA), anel=True))
    # lâminas dos pinos, do lado direito do aro até o meio
    for i, (dv, cor) in enumerate(PINOS):
        o.append(extr([(UA - 3.0, VA + dv - 0.8), (UA + 2.0, VA + dv - 0.8), (UA + 2.0, VA + dv + 0.8), (UA - 3.0, VA + dv + 0.8)],
                      WA + 1.4 + 0.3 * i, WA + RA - 2.6, 'fosf'))
    # carretel da fibra do lado direito e a luz em cima do aro
    o.append(pin(UA, VA + 12, 6.2, WA + RA - 1.5, WA + RA + 5.5, A, n=28))
    o.append(pin(UA, VA + 12, 7.2, WA + RA + 10.6, WA + RA + 11.6, A, n=28))
    vt = VA + RA + 2.6
    o.append(bevel(cyl((UA - 7, vt, WA), (UA + 8, vt, WA), 4.4, A, n=28), 0.5, 1))
    o.append(cyl((UA - 9.2, vt, WA), (UA - 7, vt, WA), 4.7, 'serr', n=28, lobes=0.08))       # tampa da pilha
    o.append(pin(UA - 1, vt, 1.9, WA + 4.2, WA + 6.0, 'anod_laranja', n=16))                 # botão da luz
    # nível de bolha embaixo
    nv = bevel(box(UA - 4.5, UA + 4.5, VA - RA - 3.2, VA - RA + 2.4, WA - 9.0, WA + 9.0, A), 0.7, 1)
    cut(nv, [box(UA - 6, UA - 2.2, VA - RA - 1.6, VA - RA + 1.6, WA - 6.0, WA + 6.0, A)])
    o.append(nv)
    o.append(texto('P5', 3.2, 60, 2.0, 16.06, mat='tinta', lado=1))
    m = parte('mira', o, origem=(0, 0, 0), grupo='A')
    # vidros (transparentes no jogo): tampa do aro e o tubo do nível
    parte('vidro', [cyl((UA + 6.6, VA, WA), (UA + 7.2, VA, WA), RA - 3.05, 'lente_clara', n=56),
                    cyl((UA - 3.4, VA - RA, WA - 5.6), (UA - 3.4, VA - RA, WA + 5.6), 1.5, 'lente_clara', n=16)], origem=(0, 0, 0), grupo='A')
    # fibras: acendem no jogo (uma peça por cor)
    cores = {}
    for i, (dv, cor) in enumerate(PINOS):
        wt = WA + 1.4 + 0.3 * i
        f = [cyl((UA - 5.2, VA + dv, wt), (UA - 2.6, VA + dv, wt), 0.6, 'fibra_' + cor, n=10),         # ponta virada para o arqueiro
             cyl((UA - 5.5, VA + dv, wt), (UA - 5.2, VA + dv, wt), 0.95, 'fibra_' + cor, n=12),
             fio([(UA - 2.6, VA + dv, wt), (UA - 2.4, VA + dv, WA + RA - 2.8), (UA - 2.4, VA + dv + 0.5, WA + RA + 6.0)], 0.5, 'fibra_' + cor, fechado=False)]
        cores.setdefault(cor, []).extend(f)
    for k in range(5):                                                                       # voltas da fibra no carretel
        w = WA + RA + 6.1 + 1.0 * k
        cor = 'verde' if k % 2 else 'amarelo'
        cores[cor].append(fio([(UA + 5.2 * math.cos(a), VA + 12 + 5.2 * math.sin(a), w) for a in np.linspace(0, 2 * math.pi, 20, endpoint=False)], 0.5, 'fibra_' + cor))
    cores['verde'].append(cyl((UA - 3.4, VA - RA, WA + 0.4), (UA - 3.4, VA - RA, WA + 2.4), 1.0, 'fibra_verde', n=10))   # bolha
    for cor, objs in cores.items():
        parte('fibra_' + cor, objs, origem=(0, 0, 0), grupo='A')
    parte('luz', [cyl((UA + 8, vt, WA), (UA + 8.6, vt, WA), 3.0, 'luz_fria', n=20)], origem=(0, 0, 0), grupo='A')
    return m
