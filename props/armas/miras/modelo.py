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
    # furo largo (5,2 mm, o "furo de combate"): do olho do jogador um furo fino fecha e tapa a massa
    disco = cyl((-1.1, 19.5, 0), (1.1, 19.5, 0), 5.4, A, n=40)
    cut(disco, [cyl((-3, 19.5, 0), (3, 19.5, 0), 2.6, A, n=32)])
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
UA, VA, WA, RA = 84.0, -33.0, -22.8, 21.5      # centro e raio de fora do aro (o aro inteiro fica à esquerda da janela do punho)
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
    o.append(bevel(extr([(66, -6), (66, -20), (76, VA - 7), (92, VA - 7), (92, VA + 7), (82, -6)], WA + RA - 3.1, 5.0, A, plane='uv'), 0.8, 2))
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


# ------------------------------------------------------------------ miras de ponto de pistola e revólver
# Mira aberta de ferrolho (compacta), a mesma em cima da ponte de mira, e o tubo de ponto do revólver.
# Em todas a lente de trás é uma peça à parte (`lente`), plana e recuada: o jogo acende o ponto nela.
VC = 14.5                      # altura do centro da janela da mira compacta (acima da base)
UC = 12.0                      # onde fica a lente
JW, JV0, JV1 = 8.6, 7.6, 21.4  # meia largura da janela, de onde até onde ela vai
AREIA = False                  # ponte na cor areia


def _mover(objs, du, dv):
    from mathutils import Matrix
    t = Matrix.Translation(P(du, dv, 0))
    for o in objs:
        o.data.transform(t)
    return objs


def _micro(du=0.0, dv=0.0):
    """Mira de ponto aberta: mesa baixa com o emissor atrás e o capuz da lente na frente. Devolve (corpo, lente)."""
    A = _m('anod')
    o = [bevel(extr([(-17.5, 0), (16.5, 0), (16.5, 7.0), (-13.5, 7.0), (-17.5, 4.6)], -12.0, 12.0, A), 0.7, 2)]
    # capuz: moldura em arco, mais larga embaixo, com a janela vazada
    capuz = extr([(-12.0, 6.0), (-12.0, 17.5), (-10.2, 23.2), (-6.0, 25.4), (6.0, 25.4), (10.2, 23.2), (12.0, 17.5), (12.0, 6.0)],
                 7.6, 16.5, A, plane='wv')
    cut(capuz, [extr(ret_arred(-JW, JW, JV0, JV1, 2.6, 4), 3, 21, A, plane='wv')])
    cut(capuz, [extr([(6, 31), (11.5, 31), (6, 17)], -14, 14, A)])              # o topo de trás sai em chanfro
    o.append(bevel(capuz, 0.6, 2))
    for s in (-1, 1):                                                           # esquadros do capuz até a mesa
        o.append(bevel(extr([(7.8, 6.8), (-5.5, 6.8), (7.8, 17.0)], min(s * 9.9, s * 12.0), max(s * 9.9, s * 12.0), A), 0.4, 1))
    o.append(cyl((-8.6, 6.6, 0), (-7.4, 7.6, 0), 1.5, 'led', n=14))             # emissor, virado para a lente
    o.append(bevel(box(-11.2, -5.0, 6.9, 8.3, -3.4, 3.4, A), 0.4, 1))           # casinha do emissor
    # ajustes: altura em cima (atrás), deriva do lado direito; os dois com fenda
    alt = cyl((-14.0, 5.6, 0), (-14.0, 7.5, 0), 2.5, _m('serr'), n=20, lobes=0.08)
    cut(alt, [box(-16.8, -11.2, 7.1, 8, -0.35, 0.35, A)])
    der = pin(-11.5, 3.5, 2.3, 11.8, 12.7, _m('serr'), n=20, lobes=0.08)
    cut(der, [box(-14, -9, 3.2, 3.8, 12.3, 13, A)])
    o += [alt, der]
    for s in (-1, 1):                                                           # botões de brilho, de borracha, um de cada lado
        o.append(bevel(box(-2.5, 5.5, 1.8, 5.2, min(s * 11.9, s * 12.8), max(s * 11.9, s * 12.8), 'borracha'), 0.35, 1))
        o.append(cyl((0.0, 7.0, s * 7.0), (0.0, 7.5, s * 7.0), 1.9, _m('fosf'), n=6))     # parafusos que prendem no ferrolho
        o.append(cyl((0.0, 7.5, s * 7.0), (0.0, 7.6, s * 7.0), 0.9, 'inox', n=6))
    o.append(pin(-6.0, 2.6, 4.2, -12.3, -11.9, _m('fosf'), n=24))               # tampa da pilha, do lado esquerdo
    o.append(box(-8.6, -3.4, 2.3, 2.9, -12.6, -12.25, 'inox'))
    o.append(texto('RC-2', 1.9, 11.5, 2.6, 12.06, mat='tinta', lado=1))
    lente = [box(UC - 0.4, UC + 0.4, JV0 - 0.3, JV1 + 0.3, -JW - 0.3, JW + 0.3, 'lente_clara')]
    return _mover(o, du, dv), _mover(lente, du, dv)


def optica_micro(du=0.0, dv=0.0):
    return {'tipo': 'ponto', 'aumento': [1, 1], 'ocular_m': [0.0, round((dv + VC) / 1000, 4), round(-(du + UC - 0.4) / 1000, 4)],
            'raio_ocular_m': round((JV1 - JV0) / 2000, 4), 'iluminado': True}


def mira_compacta():
    o, lente = _micro()
    m = parte('mira', o, origem=(0, 0, 0), grupo='A')
    parte('lente', lente, origem=(0, 0, 0), grupo='A')
    return m


# Ponte: origem no meio das garras (o encaixe_ponte da pistola); a mira fica 48,2 mm acima.
PU, PV0 = 1.5, 48.2


def ponte_mira():
    """Duas placas presas na armação, por fora do ferrolho, e a travessa por cima dele com a mira de ponto."""
    A = 'tan' if AREIA else _m('anod')
    o = []
    lado = [(-68, -7), (26, -7), (30, -3), (30, PV0), (-22, PV0), (-27, PV0 - 4), (-27, 26), (-47, 6.5), (-65, 6.5), (-68, 4)]
    for s in (-1, 1):
        a, b = min(s * 12.8, s * 15.3), max(s * 12.8, s * 15.3)
        pl = extr(lado, a, b, A)
        fora = s * 15.3
        cut(pl, [extr(ret_arred(-17, 21, 12.5, 35.5, 3.5, 4), fora - 1.1, fora + 1.1, A),          # rebaixo grande
                 extr(ret_arred(-61, -31, -4.2, 2.6, 1.6, 3), fora - 0.8, fora + 0.8, A)] +        # rebaixo da garra
                [pin(u, 24.0, 2.6, a - 1, b + 1, A, n=14) for u in (-8, 2, 12)])                  # furos de alívio
        o.append(bevel(pl, 0.6, 2))
        o.append(bevel(box(-66, 28, -7, 6, min(s * 11.1, s * 12.9), max(s * 11.1, s * 12.9), A), 0.4, 1))     # garra na armação
        for u in (-58, 20):                                                                         # parafusos das garras
            o.append(pin(u, -0.5, 2.3, min(s * 15.2, s * 16.3), max(s * 15.2, s * 16.3), _m('fosf'), n=6))
            o.append(pin(u, -0.5, 1.0, min(s * 16.2, s * 16.5), max(s * 16.2, s * 16.5), 'inox', n=6))
        o.append(pin(24.5, PV0 - 3.5, 1.8, min(s * 15.2, s * 16.2), max(s * 15.2, s * 16.2), _m('fosf'), n=6))
    topo = box(-27, 30, PV0 - 6.7, PV0, -15.3, 15.3, A)
    cut(topo, [box(-29, 32, PV0 - 8, PV0 - 1.9, -2.4, 2.4, A)])                                     # fenda por onde passa a massa de mira
    o.append(bevel(topo, 0.6, 2))
    o.append(texto('PM-9', 2.4, -42, -0.8, 15.36, mat='tinta', lado=1))
    mo, lente = _micro(PU, PV0)
    m = parte('mira', o + mo, origem=(0, 0, 0), grupo='A')
    parte('lente', lente, origem=(0, 0, 0), grupo='A')
    return m


# Tubo de ponto do revólver: origem no meio da base, na ponte do revólver.
YT, RT = 21.5, 11.45           # altura do eixo do tubo e raio da lente de trás


def mira_tubo_revolver():
    A = _m('anod')
    o = [bevel(box(-18, 30, 0, 6, -5.5, 5.5, A), 0.6, 1)]
    for u in (-12, 24):                                                         # parafusos da base, dos dois lados
        o.append(pin(u, 3, 1.6, -6.1, 6.1, _m('fosf'), n=6))
    for u0 in (-12, 16):                                                        # dois anéis de peça única com a tampa de cima
        anel = extr(ret_arred(-16.2, 16.2, 5.0, YT + 16.4, 5.0, 4), u0, u0 + 10, A, plane='wv')
        cut(anel, [cyl((u0 - 1, YT, 0), (u0 + 11, YT, 0), 12.45, A, n=40),
                   box(u0 - 1, u0 + 11, YT - 0.6, YT + 0.6, 12.0, 20, A), box(u0 - 1, u0 + 11, YT - 0.6, YT + 0.6, -20, -12.0, A)])
        o.append(bevel(anel, 0.6, 1))
        for s in (-1, 1):                                                       # parafusos da tampa do anel
            o.append(cyl((u0 + 5, YT + 3.0, s * 14.4), (u0 + 5, YT - 3.0, s * 14.4), 1.5, _m('fosf'), n=6))
    tubo = lathe([(-30, RT + 0.05), (-30, 13.4), (-28.4, 13.9), (-23, 13.9), (-21.5, 12.5), (27, 12.5), (33, 14.6), (43, 14.6),
                  (44, 14.0), (44, 12.9), (33.5, 12.3), (-22, RT + 0.05)], _m('anod_tubo'), n=48, c0=(0, YT, 0), anel=True)
    o.append(bevel(tubo, 0.3, 1))
    o.append(lathe([(-27.6, 13.9), (-27.6, 14.3), (-24.0, 14.3), (-24.0, 13.9)], _m('serr'), n=40, c0=(0, YT, 0), lobes=0.05, anel=True))
    # torre da pilha e do brilho do lado direito; ajustes de altura (em cima) e deriva (esquerda) com tampa
    o.append(pin(6, YT, 6.0, 12.0, 15.0, A, n=24))
    o.append(pin(6, YT, 6.6, 15.0, 19.4, _m('serr'), n=28, lobes=0.07))
    o.append(pin(6, YT, 4.2, 19.4, 19.9, _m('fosf'), n=20))
    o.append(box(3.2, 8.8, YT - 0.3, YT + 0.3, 19.9, 20.2, 'inox'))
    o.append(cyl((6, YT + 12.0, 0), (6, YT + 14.0, 0), 4.6, A, n=20))
    o.append(cyl((6, YT + 14.0, 0), (6, YT + 17.6, 0), 4.9, _m('serr'), n=24, lobes=0.07))
    o.append(pin(6, YT, 4.6, -14.0, -12.0, A, n=20))
    o.append(pin(6, YT, 4.9, -17.6, -14.0, _m('serr'), n=24, lobes=0.07))
    o.append(cyl((-3.5, YT + 11.4, -4.8), (-2.9, YT + 12.2, -4.8), 1.2, 'led', n=10))        # só enfeite: luz de pilha fraca
    o.append(texto('RT-1', 2.2, 20, YT - 8.6, 9.5, mat='tinta', lado=1))
    m = parte('mira', o, origem=(0, 0, 0), grupo='A')
    parte('lente', [cyl((-26.0, YT, 0), (-25.2, YT, 0), RT, 'lente_clara', n=40)], origem=(0, 0, 0), grupo='A')
    parte('vidro', [cyl((39.4, YT, 0), (40.2, YT, 0), 12.6, 'lente_clara', n=40)], origem=(0, 0, 0), grupo='A')
    return m


def optica_tubo_revolver():
    return {'tipo': 'ponto', 'aumento': [1, 1], 'ocular_m': [0.0, YT / 1000, 0.026], 'raio_ocular_m': round(RT / 1000, 4), 'iluminado': True}


# ------------------------------------------------------------------ mira holográfica
HV, HW0, HW1 = 28.75, 14.0, 43.5      # centro da janela, de onde até onde ela vai (meia largura 15)


def mira_holografica():
    """Corpo comprido e baixo com a caixa das pilhas atrás e o arco de proteção em volta da janela."""
    A = _m('anod')
    o = _base(-42, 42, 5.0, 2)
    o.append(bevel(extr([(-45, 4.5), (-45, 15.0), (-41, 17.5), (-16, 17.5), (-12, 13.5), (34, 13.5), (34, 4.5)], -14.0, 14.0, A), 1.2, 2))
    capuz = extr(ret_arred(-18, 18, 11.0, 47.0, 5.0, 5), -10, 33, A, plane='wv')
    cut(capuz, [extr(ret_arred(-15, 15, HW0, HW1, 3.2, 4), -14, 37, A, plane='wv')])
    cut(capuz, [extr([(-12, 51), (2, 51), (-12, 31)], -20, 20, A)])                     # atrás o arco sobe inclinado
    cut(capuz, [extr(ret_arred(-2, 25, 20, 38, 3, 3), -21, 21, A)])                     # janelas dos lados, para aliviar
    o.append(bevel(capuz, 0.7, 2))
    for i, w in enumerate((-7.5, 0.0, 7.5)):                                            # três botões atrás
        o.append(bevel(box(-46.0, -44.6, 7.0, 12.0, w - 2.6, w + 2.6, 'borracha'), 0.4, 1))
    o.append(pin(-30, 10.8, 5.6, 13.8, 16.8, _m('serr'), n=28, lobes=0.07))             # tampa das pilhas (direita)
    o.append(box(-33, -27, 10.5, 11.1, 16.8, 17.1, 'inox'))
    for u in (4, 16):                                                                   # ajustes de altura e deriva (direita)
        k = pin(u, 9.0, 3.0, 13.8, 15.2, _m('serr'), n=20, lobes=0.08)
        cut(k, [box(u - 3.5, u + 3.5, 8.7, 9.3, 14.8, 16, A)])
        o.append(k)
    o.append(cyl((-13.4, 13.8, 0), (-12.2, 14.8, 0), 2.0, 'led', n=14))                 # saída do laser do retículo
    o.append(texto('HG-1', 3.0, -30, 12.0, -14.06, mat='tinta', lado=-1))
    m = parte('mira', o, origem=(0, 0, 0), grupo='A')
    parte('lente', [box(1.0, 1.8, HW0 - 0.3, HW1 + 0.3, -15.3, 15.3, 'lente_clara')], origem=(0, 0, 0), grupo='A')
    parte('vidro', [box(29.0, 29.8, HW0 - 0.3, HW1 + 0.3, -15.3, 15.3, 'lente_clara')], origem=(0, 0, 0), grupo='A')
    return m


def optica_holografica():
    return {'tipo': 'holografica', 'aumento': [1, 1], 'ocular_m': [0.0, HV / 1000, -0.001], 'raio_ocular_m': 0.0147, 'iluminado': True}


# ------------------------------------------------------------------ tubo de ponto para trilho (com tampas)
TV, TR = 30.0, 13.3            # altura do eixo e raio da lente de trás
TAMPAS = ((38.0, 1), (-34.0, -1))   # dobradiça de cada tampa (u) e para que lado ela fecha


def mira_tubo():
    from mathutils import Matrix
    A = _m('anod')
    o = _base(-21, 21, 5.0, 1, alavanca=True)
    o.append(bevel(extr([(-16, 4.5), (16, 4.5), (12, TV - 12.8), (-12, TV - 12.8)], -8.5, 8.5, A), 1.0, 1))      # pedestal
    anel = extr(ret_arred(-17.6, 17.6, TV - 17.6, TV + 17.6, 6.0, 5), -9, 9, A, plane='wv')
    cut(anel, [cyl((-10, TV, 0), (10, TV, 0), 14.45, A, n=44), box(-10, 10, TV - 0.6, TV + 0.6, 13, 20, A)])
    o.append(bevel(anel, 0.6, 1))
    for u in (-5, 5):
        o.append(cyl((u, TV + 4.0, 15.6), (u, TV - 4.0, 15.6), 1.6, _m('fosf'), n=6))
    tubo = lathe([(-34, TR + 0.05), (-34, 15.8), (-31, 16.3), (-22.5, 16.3), (-19.5, 14.5), (22, 14.5), (27, 17.2), (37, 17.2),
                  (38, 16.6), (38, 15.4), (27.5, 14.0), (-22, TR + 0.05)], _m('anod_tubo'), n=56, c0=(0, TV, 0), anel=True)
    o.append(bevel(tubo, 0.3, 1))
    o.append(lathe([(-30.4, 16.3), (-30.4, 16.75), (-24.5, 16.75), (-24.5, 16.3)], _m('serr'), n=44, c0=(0, TV, 0), lobes=0.05, anel=True))
    # torres: altura em cima, pilha e brilho do lado direito
    o.append(cyl((0, TV + 14.0, 0), (0, TV + 17.5, 0), 6.6, A, n=28))
    o.append(cyl((0, TV + 17.5, 0), (0, TV + 22.5, 0), 7.2, _m('serr'), n=32, lobes=0.06))
    o.append(pin(0, TV, 6.6, 14.0, 17.5, A, n=28))
    o.append(pin(0, TV, 7.2, 17.5, 24.0, _m('serr'), n=32, lobes=0.06))
    o.append(pin(0, TV, 4.6, 24.0, 24.5, _m('fosf'), n=20))
    o.append(box(-3, 3, TV - 0.3, TV + 0.3, 24.5, 24.8, 'inox'))
    o.append(pin(-10, TV, 3.2, -16.6, -14.2, 'borracha', n=20))                                                 # botão de brilho (esquerda)
    o.append(texto('RT-3', 2.6, 10, TV - 10.6, 8.56, mat='tinta', lado=1))
    for u, s in TAMPAS:                                                                                         # orelhas das dobradiças
        o.append(bevel(box(u - 2.2, u + 2.2, TV + 15.5, TV + 20.0, -4.0, 4.0, 'polim'), 0.5, 1))
    m = parte('mira', o, origem=(0, 0, 0), grupo='A')
    parte('lente', [cyl((-28.5, TV, 0), (-27.7, TV, 0), TR, 'lente_clara', n=44)], origem=(0, 0, 0), grupo='A')
    parte('vidro', [cyl((31.8, TV, 0), (32.6, TV, 0), 15.3, 'lente_clara', n=44)], origem=(0, 0, 0), grupo='A')
    # tampas de polímero: modeladas fechadas e giradas 150° para a posição aberta (a animação fecha)
    for (u, s), nome, r in zip(TAMPAS, ('tampa_frente', 'tampa_tras'), (17.6, 16.7)):
        t = [cyl((u + s * 0.3, TV, 0), (u + s * 2.3, TV, 0), r, 'polim', n=40),
             lathe([(0, r - 1.6), (0, r), (-s * 3.0, r), (-s * 3.0, r - 1.6)] if s > 0 else [(0, r), (0, r - 1.6), (-s * 3.0, r - 1.6), (-s * 3.0, r)],
                   'polim', n=40, c0=(u + s * 0.3, TV, 0), anel=True),
             pin(u, TV + 18.5, 1.5, -3.8, 3.8, 'polim', n=10),
             bevel(box(u + min(0, s * 2.3), u + max(0, s * 2.3), TV + 14, TV + 19.6, -3.6, 3.6, 'polim'), 0.4, 1),
             bevel(box(u + min(s * 0.3, s * 2.3), u + max(s * 0.3, s * 2.3), TV - r - 3.0, TV - r + 1.0, -3.0, 3.0, 'polim'), 0.4, 1)]   # aba de abrir
        h = P(u, TV + 18.5, 0)
        g = Matrix.Translation(h) @ Matrix.Rotation(math.radians(150 * s), 4, 'X') @ Matrix.Translation(-h)
        for x in t:
            x.data.transform(g)
        parte(nome, t, origem=(u, TV + 18.5, 0), pai=m, grupo='A')
    return m


def optica_tubo():
    return {'tipo': 'ponto', 'aumento': [1, 1], 'ocular_m': [0.0, TV / 1000, 0.0285], 'raio_ocular_m': round(TR / 1000, 4), 'iluminado': True}


# ------------------------------------------------------------------ miras rebatíveis de polímero
POLIM = 'polim'                # config troca por 'tan' na versão caramelo
PH = (-6.0, 6.0)               # dobradiça (u, v)


def _pe_polimero():
    Pm = POLIM
    o = [bevel(extr([(-19, 0.2), (19, 0.2), (19, 4.0), (15, 7.5), (-15, 7.5), (-19, 4.0)], -10.5, 10.5, Pm), 0.8, 1)]
    b = extr([(-13.0, 22.6 + D), (-13.0, 3.0), (13.0, 3.0), (13.0, 22.6 + D), (11.0, 22.6 + D), (11.0, 0.0), (-11.0, 0.0), (-11.0, 22.6 + D)],
             -16, 16, Pm, plane='wv')
    o.append(bevel(b, 0.6, 1))
    o.append(pin(11, 27.5 + D, 4.2, 13.0, 14.8, _m('fosf'), n=20))                       # parafuso da garra, com fenda
    o.append(box(8, 14, 27.2 + D, 27.8 + D, 14.8, 15.1, 'inox'))
    o.append(pin(PH[0], PH[1], 1.5, -10.8, 10.8, 'inox', n=12))                         # eixo
    for s in (-1, 1):                                                                   # orelhas da dobradiça
        o.append(bevel(extr([(-10.5, 3.5), (-1.5, 3.5), (-1.5, 7.0), (-3.6, 9.6), (-8.4, 9.6), (-10.5, 7.0)],
                            min(s * 9.2, s * 10.5), max(s * 9.2, s * 10.5), Pm), 0.5, 1))
    return parte('base', o, origem=(0, 0, 0), grupo='A')


def alca_polimero():
    Pm = POLIM
    base = _pe_polimero()
    lam = extr(ret_arred(-9.0, 9.0, 4.5, 25.2, 2.2, 4), -10.0, -2.0, Pm, plane='wv')
    cut(lam, [cyl((-12, 19.5, 0), (0, 19.5, 0), 2.6, Pm, n=28),                         # furo largo
              cyl((-10.6, 19.5, 0), (-8.4, 19.5, 0), 5.2, Pm, n=28, r1=2.6),            # boca do furo, em funil, do lado do olho
              extr([(-5.0, 8.5), (5.0, 8.5), (0.0, 14.0)], -12, 0, Pm, plane='wv')])    # janela triangular de alívio
    l = [bevel(lam, 0.5, 1),
         pin(-6.0, 12.5, 4.8, 9.0, 13.5, _m('serr'), n=24, lobes=0.08),                 # tambor de deriva
         pin(-6.0, 12.5, 3.0, 13.5, 14.1, Pm, n=20)]
    parte('lamina', l, origem=(PH[0], PH[1], 0), pai=base, grupo='A')
    return base


def massa_polimero():
    Pm = POLIM
    base = _pe_polimero()
    lam = extr([(-8.5, 4.5), (8.5, 4.5), (8.5, 20.5), (6.4, 25.2), (4.6, 25.2), (4.6, 12.0), (-4.6, 12.0), (-4.6, 25.2), (-6.4, 25.2), (-8.5, 20.5)],
               -10.0, -2.0, Pm, plane='wv')                                             # forquilha: duas orelhas e o poste no meio
    l = [bevel(lam, 0.5, 1),
         cyl((-6.0, 11.0, 0), (-6.0, 12.8, 0), 2.6, _m('serr'), n=16, lobes=0.12),      # roseta de elevação
         cyl((-6.0, 12.8, 0), (-6.0, 19.4, 0), 1.05, _m('fosf'), n=12),                 # poste
         cyl((-6.0, 19.4, 0), (-6.0, 19.5, 0), 0.95, 'tinta', n=12)]
    parte('lamina', l, origem=(PH[0], PH[1], 0), pai=base, grupo='A')
    return base


# ------------------------------------------------------------------ montagem lateral do fuzil 7,62
# Origem = face do trilho de cauda de andorinha, do lado esquerdo do receptor. w cresce para a direita:
# o meio do fuzil fica em w = ZL. O braço sobe por fora e a ponte passa por cima da tampa.
ZL = 16.3
LV, LR = 58.0, 12.0            # tubo de ponto: altura do eixo e raio da lente de trás
NV = 61.0                      # luneta: altura do eixo


def _lateral():
    S = 'fosf'
    # sapata que abraça o trilho, com as duas garras
    o = [bevel(extr([(-7.0, -11), (0.0, -11), (0.0, -8.2), (-2.4, -6.6), (-2.4, 6.6), (0.0, 8.2), (0.0, 11), (-7.0, 11)], -46, 42, S, plane='wv'), 0.5, 1)]
    # braço e ponte numa peça só
    arco = extr([(-9.5, 5), (-6.0, 5), (-6.0, 33.5), (ZL + 12.5, 33.5), (ZL + 14, 35), (ZL + 14, 38.5), (ZL + 11.5, 41), (-5.5, 41), (-9.5, 37)],
                -44, 40, S, plane='wv')
    cut(arco, [extr(ret_arred(-36, -8, 15, 28, 3.5), -12, -3, S, plane='uv'),                 # janelas de alívio do braço
               extr(ret_arred(4, 32, 15, 28, 3.5), -12, -3, S, plane='uv')])
    o.append(bevel(arco, 0.7, 2))
    # alavanca de trava com o eixo e a porca de regulagem
    o.append(bevel(extr([(-34, -6.5), (-2, -6.5), (4, -3.5), (6, 0.5), (2, 1.5), (-4, -2.2), (-34, -2.2)], -11.4, -8.2, S, plane='uv'), 0.6, 1))
    o.append(pin(-30, -4.2, 3.4, -13.2, -7.0, 'inox', n=20))
    o.append(pin(-30, -4.2, 4.6, -8.2, -7.0, S, n=6))
    o.append(pin(22, 0, 3.6, -9.4, -7.0, S, n=6))
    o.append(pin(22, 0, 1.6, -10.2, -9.3, 'inox', n=10))
    return o


def _aneis(us, vc, r_in, topo=40.5, larg=12.0):
    """Anéis em duas metades presos na ponte."""
    o = []
    for u in us:
        o.append(bevel(lathe([(u - larg / 2, r_in), (u - larg / 2, r_in + 3.6), (u + larg / 2, r_in + 3.6), (u + larg / 2, r_in)],
                             'anod', n=44, c0=(0, vc, ZL), anel=True), 0.5, 1))
        for s in (-1, 1):
            o.append(bevel(box(u - larg / 2, u + larg / 2, vc - 2.0, vc + 2.0, ZL + s * (r_in + 2.6), ZL + s * (r_in + 7.4), 'anod'), 0.5, 1))
            o.append(cyl((u, vc + 2.0, ZL + s * (r_in + 5.2)), (u, vc + 4.0, ZL + s * (r_in + 5.2)), 1.8, 'fosf', n=6))
        o.append(bevel(extr([(u - 7, topo), (u + 7, topo), (u + 5.5, vc - r_in - 2.2), (u - 5.5, vc - r_in - 2.2)], ZL - 8, ZL + 8, 'anod'), 0.7, 1))
    return o


def mira_lateral():
    o = _lateral()
    c = (0, LV, ZL)
    tubo = lathe([(-35, LR + 0.05), (-35, 15.2), (-33.8, 16.0), (-25, 16.0), (-23, 14.4), (26, 14.4), (30, 16.6), (41, 16.6), (42, 16.0),
                  (42, 14.6), (30.5, 13.4), (-24, LR + 0.05)], 'anod_tubo', n=56, c0=c, anel=True)
    o.append(bevel(tubo, 0.3, 1))
    o += _aneis((-13, 15), LV, 14.5)
    # torres de altura (em cima) e de lado (direita), com tampa recartilhada; pilha e brilho na esquerda
    o.append(cyl((1, LV + 14.0, ZL), (1, LV + 16.5, ZL), 6.0, 'anod', n=28))
    o.append(cyl((1, LV + 16.5, ZL), (1, LV + 21.0, ZL), 6.6, 'serr', n=32, lobes=0.06))
    o.append(pin(1, LV, 6.0, ZL + 14.0, ZL + 16.5, 'anod', n=28))
    o.append(pin(1, LV, 6.6, ZL + 16.5, ZL + 21.0, 'serr', n=32, lobes=0.06))
    o.append(pin(1, LV, 7.2, ZL - 17.0, ZL - 14.0, 'anod', n=28))
    o.append(pin(1, LV, 8.0, ZL - 23.5, ZL - 17.0, 'serr', n=36, lobes=0.05))
    o.append(pin(1, LV, 5.2, ZL - 24.1, ZL - 23.5, 'fosf', n=20))
    o.append(box(-2.6, 4.6, LV - 0.35, LV + 0.35, ZL - 24.4, ZL - 24.1, 'inox'))
    o.append(lathe([(32, 16.6), (32, 17.0), (39, 17.0), (39, 16.6)], 'serr', n=44, c0=c, lobes=0.04, anel=True))
    m = parte('mira', o, origem=(0, 0, 0), grupo='A')
    parte('lente', [cyl((-29.5, LV, ZL), (-28.7, LV, ZL), LR, 'lente_clara', n=44)], origem=(0, 0, 0), grupo='A')
    parte('vidro', [cyl((36.0, LV, ZL), (36.8, LV, ZL), 14.1, 'lente_clara', n=44)], origem=(0, 0, 0), grupo='A')
    return m


def optica_lateral():
    return {'tipo': 'ponto', 'aumento': [1, 1], 'ocular_m': [ZL / 1000, LV / 1000, 0.0295], 'raio_ocular_m': round(LR / 1000, 4), 'iluminado': True}


NR, NF, N_OC, N_OB, NT = -90.0, 98.0, 14.6, 16.0, 12.7    # luneta 4×: pontas, raio das lentes e do tubo


def luneta_lateral():
    o = _lateral()
    c = (0, NV, ZL)
    Roc, Rob = N_OC + 2.8, N_OB + 3.0
    prof = [(NR + 6, 0.0), (NR + 6, N_OC), (NR, N_OC), (NR, Roc - 1.8), (NR + 8, Roc - 1.8), (NR + 8, Roc), (NR + 22, Roc), (NR + 22, Roc - 2.2),
            (NR + 36, Roc - 2.2), (NR + 36, Roc), (NR + 39, Roc), (NR + 44, NT + 1.2), (NR + 48, NT),
            (-13, NT), (-10, NT + 3.4), (12, NT + 3.4), (15, NT), (48, NT), (66, Rob), (89, Rob), (89.6, Rob - 0.9), (90.8, Rob - 0.9), (91.4, Rob),
            (NF - 0.8, Rob), (NF, Rob - 0.8), (NF, N_OB), (NF - 6, N_OB), (NF - 6, 0.0)]
    o.append(lathe(prof, 'anod_tubo', n=64, c0=c))
    o.append(lathe([(NR - 0.6, N_OC + 0.6), (NR - 0.6, Roc + 0.3), (NR + 0.6, Roc + 1.0), (NR + 7.0, Roc + 1.0), (NR + 7.9, Roc + 0.1),
                    (NR + 7.9, N_OC + 0.6)], 'borracha', n=64, c0=c, anel=True))
    o.append(lathe([(NR + 23, Roc - 2.0), (NR + 23, Roc + 1.0), (NR + 35, Roc + 1.0), (NR + 35, Roc - 2.0)], 'serr', n=64, c0=c, lobes=0.035, anel=True))
    rs = NT + 3.4
    for dv, dw in ((1, 0), (0, 1)):                                                     # torres de altura e de lado, com tampa
        p = lambda d: (1, NV + dv * d, ZL + dw * d)
        o += [cyl(p(rs - 1), p(rs + 3.5), 9.4, 'anod', n=28), cyl(p(rs + 3.5), p(rs + 10.5), 8.8, 'serr', n=36, lobes=0.045),
              cyl(p(rs + 10.5), p(rs + 11.6), 7.4, 'anod', n=24)]
    o += _aneis((-26, 30), NV, NT + 0.1)
    o.append(texto('4x32', 2.8, 2, 24, -9.56, mat='tinta', lado=-1))
    m = parte('luneta', o, origem=(0, 0, 0), grupo='A')
    parte('lente', [cyl((NR + 6.5, NV, ZL), (NR + 5.7, NV, ZL), N_OC - 0.05, 'lente', n=64),
                    cyl((NF - 6.5, NV, ZL), (NF - 5.7, NV, ZL), N_OB - 0.05, 'lente', n=64)], origem=(0, 0, 0), grupo='A')
    return m


def optica_luneta_lateral():
    return {'tipo': 'luneta', 'aumento': [4, 4], 'ocular_m': [ZL / 1000, NV / 1000, round(-(NR + 5.7) / 1000, 4)],
            'raio_ocular_m': round((N_OC - 0.05) / 1000, 4), 'objetiva_m': [ZL / 1000, NV / 1000, round(-(NF - 5.7) / 1000, 4)],
            'reticulo': 'cruz', 'iluminado': False}


# ------------------------------------------------------------------ mira de 3 pinos do arco simples
# Origem = meio da placa, na face direita do punho. O aro fica para dentro, sobre a flecha.
UB, VB, WB, RB = 73.0, -10.0, -17.6, 17.5     # centro e raio de fora do aro
PINOS_B = ((6.0, 'verde'), (0.0, 'amarelo'), (-6.0, 'vermelho'))     # 10, 20 e 30 m


def mira_pinos_arco():
    A = 'anod'
    placa = bevel(extr(ret_arred(-8, 18, -25, 25, 3.5), 0.0, 5.0, A, plane='uv'), 0.7, 2)
    cut(placa, [extr(ret_arred(2, 8, -8, 8, 2.2), -1, 6, A, plane='uv')])
    o = [placa]
    for v in (-15, 15):
        o.append(pin(0, v, 3.4, 5.0, 6.4, 'fosf', n=20))
        o.append(pin(0, v, 1.7, 6.4, 6.7, 'inox', n=6))
    # barra com a escala e o bloco que sobe e desce o aro
    o.append(bevel(box(14, 62, -15.5, -4.5, 0.6, 4.6, A), 0.6, 1))
    for i in range(10):
        u = 24 + i * 3.0
        o.append(box(u - 0.2, u + 0.2, -8.6 if i % 5 else -10.2, -5.6, 4.6, 4.66, 'tinta'))
    bloco = bevel(box(56, 68, -24, 4, -3.0, 6.0, A), 0.9, 2)
    o.append(bloco)
    o.append(pin(62, -2, 4.6, 6.0, 11.5, 'anod_laranja', n=24, lobes=0.10))                 # botão de altura
    o.append(pin(62, -2, 1.9, 11.5, 12.0, 'inox', n=6))
    o.append(pin(62, -18, 2.0, 6.0, 7.2, 'fosf', n=6))
    o.append(bevel(box(UB - 4.0, UB + 3.0, VB - 4.5, VB + 4.5, WB + RB - 1.0, -2.0, A), 0.6, 1))   # haste do bloco ao aro
    aro = lathe([(-6, RB - 3.0), (-6, RB - 0.6), (-5.4, RB), (5.4, RB), (6, RB - 0.6), (6, RB - 3.0)], A, n=56, c0=(UB, VB, WB), anel=True)
    o.append(aro)
    o.append(lathe([(-6.06, RB - 2.6), (-6.06, RB - 1.0), (-6.0, RB - 1.0), (-6.0, RB - 2.6)], 'tinta_viva', n=56, c0=(UB, VB, WB), anel=True))
    for i, (dv, cor) in enumerate(PINOS_B):                                                # lâminas dos pinos
        o.append(extr([(UB - 2.6, VB + dv - 0.7), (UB + 1.8, VB + dv - 0.7), (UB + 1.8, VB + dv + 0.7), (UB - 2.6, VB + dv + 0.7)],
                      WB + 0.3 * (i - 1), WB + RB - 2.6, 'fosf'))
    m = parte('mira', o, origem=(0, 0, 0), grupo='A')
    cores = {}
    for i, (dv, cor) in enumerate(PINOS_B):
        wt = WB + 0.3 * (i - 1)
        cores[cor] = [cyl((UB - 4.6, VB + dv, wt), (UB - 2.2, VB + dv, wt), 0.6, 'fibra_' + cor, n=10),
                      cyl((UB - 4.9, VB + dv, wt), (UB - 4.6, VB + dv, wt), 0.95, 'fibra_' + cor, n=12),
                      fio([(UB - 2.2, VB + dv, wt), (UB - 2.0, VB + dv, WB + RB - 2.8), (UB + 1.0, VB + dv + 1.0, WB + RB + 0.6),
                           (UB + 4.0, VB + dv + 2.0, WB + RB + 0.6)], 0.5, 'fibra_' + cor, fechado=False)]
    for cor, objs in cores.items():
        parte('fibra_' + cor, objs, origem=(0, 0, 0), grupo='A')
    return m
