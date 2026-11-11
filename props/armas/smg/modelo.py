"""Submetralhadora Faísca 9 mm no nível de detalhe da M4A1: arma curta de polímero com o
carregador dentro do punho, coronha de duas varetas que corre por dentro do corpo, trilho
inteiro em cima, trilhos curtos embaixo e à direita, alavanca de manejo em T atrás e cano
com rosca. Desenho próprio, sem marcas de fabricante.

Mesmas medidas e pontos da Faísca antiga (arma07_smg.py), para os encaixes, os acessórios
e as animações continuarem valendo. Coordenadas em mm (lib.py da M4A1): u = para a frente
(0 na face de trás da janela do ferrolho), v = para cima (0 no eixo do cano), w = direita.
"""
import math
import bpy, bmesh
from shapely.geometry import Polygon, LineString, Point, box as caixa2d
from shapely.ops import unary_union
from lib import *
from lib import _obj

# ------------------------------------------------------------------ medidas
U0, U1 = -72.0, 200.0             # corpo: trás e frente
VT, VB = 26.0, -24.0              # topo (o trilho fica por cima) e fundo do corpo
W = 19.5                          # meia largura do corpo
CS = 1.8                          # quanto a casca de trás é mais larga
XM = 233.0                        # fim da rosca do cano
AN = math.radians(8)
D = (-math.sin(AN), -math.cos(AN))        # eixo do carregador (desce e vai para trás)
N = (math.cos(AN), -math.sin(AN))         # normal (frente)
T = (31.0, -26.0)                 # topo do carregador (centro)
ML, MW, MZ = 142.0, 16.2, 10.5    # carregador: comprimento, meia largura (frente-trás), meia espessura
VV, WV, RV = -12.0, 14.5, 4.2     # varetas da coronha: altura, afastamento, raio
P_GAT = (82.0, -30.0)             # pino do gatilho
P_SEL = (12.0, -12.0)             # eixo do seletor
PIC = [(7.85, 0), (10.6, -2.75), (7.9, -5.5), (-7.9, -5.5), (-10.6, -2.75), (-7.85, 0)]   # perfil do trilho (x, y a partir do topo)


def ax(t, n=0.0):
    """Ponto (u, v) a t mm ao longo do eixo do carregador e n mm para a frente dele."""
    return (T[0] + D[0] * t + N[0] * n, T[1] + D[1] * t + N[1] * n)


def pl(g):
    return [(float(x), float(y)) for x, y in list(g.exterior.coords)[:-1]]


def arred(pts, r, n=6):
    """Polígono com os cantos arredondados (raio r)."""
    g = pts if hasattr(pts, 'exterior') else Polygon(pts)
    return g.buffer(-r, quad_segs=n).buffer(2 * r, quad_segs=n).buffer(-r, quad_segs=n)


def solido(g, a, b, mat, plane='uv'):
    """Extrusão de um polígono shapely (os furos viram cortes)."""
    o = extr(pl(g), a, b, mat, plane)
    if g.interiors:
        m = 1.0 if a < b else -1.0
        cut(o, [extr([(float(x), float(y)) for x, y in list(i.coords)[:-1]], a - m, b + m, mat, plane) for i in g.interiors])
    return o


def lados(s, a, b):
    """Intervalo em w do lado s (-1 esquerda, 1 direita), já em ordem."""
    return sorted((s * a, s * b))


def smooth(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def faixa(t0, t1, meia):
    """Faixa ao longo do eixo do carregador."""
    return Polygon([ax(t0, -meia), ax(t0, meia), ax(t1, meia), ax(t1, -meia)])


def poco(mat):
    return solido(faixa(-3.0, 200.0, MW + 0.6), -MZ - 0.7, MZ + 0.7, mat)


def furos_varetas(mat):
    return [cyl((U0 - 6, VV, s * WV), (100, VV, s * WV), RV + 0.5, mat, n=24) for s in (-1, 1)]


def janela(mat):
    return solido(arred([(30, 2), (72, 2), (72, 16), (30, 16)], 2.5, 4), W - 7, W + 6, mat)


CABO = arred([(3, -26), (56, -26), (55, -45), (52, -70), (48, -100), (44, -128), (38, -138), (-8, -138), (-14, -130),
              (-11, -100), (-5, -70), (-1, -48), (-8, -40), (-6, -26)], 2.5, 6)


def meia_largura(v):
    return 14.8 + 1.0 * smooth(-40, -80, v) + 0.8 * smooth(-118, -134, v)


# ------------------------------------------------------------------ corpo
def _trilho(a, b, mapa, fenda, u_fenda, n):
    """Trilho de acessórios de a até b; mapa leva (x, y) do perfil para (w, v)."""
    t = extr([mapa(x, y) for (x, y) in PIC], a, b, 'anod', plane='wv')
    cut(t, [fenda(u_fenda - i * 10.008) for i in range(n)])
    return bevel(t, 0.35, 1, 40)


def corpo():
    M_ = 'pol_smg'
    sec = [(W, VB - 14), (W, VT - 6), (W - 6, VT)]
    sec = sec + [(-w, v) for (w, v) in reversed(sec)]
    c = extr(sec, U0 - 1, U1 + 1, M_, plane='wv')
    perfil = arred([(U0, VT), (U1 - 12, VT), (U1, VT - 10), (U1, VB + 10), (U1 - 12, VB), (118, VB), (112, -34), (-14, -34),
                    (-30, VB), (U0 + 8, VB + 2), (U0, VB + 10)], 3.0, 5)
    planta = [(U0 - 3, -W - 1), (193, -W - 1), (193, -W), (U1, -W + 3), (U1 + 3, -W + 3),
              (U1 + 3, W - 3), (U1, W - 3), (193, W), (193, W + 1), (U0 - 3, W + 1)]
    cut(c, [solido(perfil, -30, 30, M_), extr(planta, -60, 40, M_, plane='uw')], op='INTERSECT')
    cortes = [janela(M_), poco(M_), *furos_varetas(M_),
              box(-12, 114, 0.5, 17.5, -13, W - 3, M_),                                   # caminho do ferrolho
              cyl((150, 0, 0), (U1 + 5, 0, 0), 9.7, M_, n=32),                            # passagem do cano
              box(-80, -40, 15.5, 21.5, -3.6, 3.6, M_)]                                   # canal da haste da alavanca
    for s in (-1, 1):
        a, b = lados(s, W - 3.0, W + 6)
        for x0 in (104, 132, 160):                                                         # fendas de ventilação
            cortes.append(solido(arred([(x0, 13.0), (x0 + 16, 13.0), (x0 + 21, 18.8), (x0 + 5, 18.8)], 2.2, 4), a, b, M_))
        a, b = lados(s, W - 0.8, W + 6)
        cortes.append(box(93, 190, -17.6, -16.4, a, b, M_))                               # emenda das duas metades
    a, b = lados(-1, W - 2.4, W + 6)
    for x0 in (128, 162):                                                                  # fendas de fixação (esquerda)
        cortes.append(solido(arred([(x0, -5.5), (x0 + 28, -5.5), (x0 + 28, 2.5), (x0, 2.5)], 2.0, 4), a, b, M_))
    cut(c, cortes)
    bevel(c, 0.8, 2, 34)
    o = [c]
    # casca de trás, um pouco mais larga, com a borda da frente inclinada
    casca = arred([(U0 + 3, 17.0), (65, 17.0), (90, -8), (90, -31), (-12, -31), (-28, VB + 1), (U0 + 3, VB + 4)], 4.0, 5)
    k = solido(casca, -W - CS, W + CS, M_)
    cortes = [janela(M_), poco(M_), *furos_varetas(M_)]
    for s in (-1, 1):
        a, b = lados(s, W + CS - 1.0, W + 6)
        for i in range(6):                                                                 # estrias de pega atrás
            u = -60.0 + i * 5.0
            cortes.append(extr([(u, -7), (u + 2.2, -7), (u + 4.8, 10), (u + 2.6, 10)], a, b, M_))
        cortes.append(cyl((P_SEL[0], P_SEL[1], a), (P_SEL[0], P_SEL[1], b), 6.2, M_, n=24))    # assento do seletor
    cut(k, cortes)
    o.append(bevel(k, 1.1, 2, 34))
    # guarda-mato
    fora = arred([(58, -33), (118, -33), (116, -40), (104, -56), (66, -58), (56, -50)], 4.0, 5)
    dentro = arred([(62, -35.5), (111, -35.5), (108, -41), (99, -52), (68, -54), (61, -49)], 3.0, 5)
    o.append(bevel(solido(fora.difference(dentro), -6.0, 6.0, M_), 1.4, 3, 40))
    # punho de seção arredondada, com o poço do carregador
    b = CABO.bounds
    aneis, n = [], 80
    for i in range(n + 1):
        v = (b[3] - 0.4) + ((b[1] + 0.4) - (b[3] - 0.4)) * i / n
        x = CABO.intersection(LineString([(-80, v), (120, v)])).bounds
        pts = superelipse((x[2] - x[0]) / 2, meia_largura(v), n=52, e=2.5, cx=(x[0] + x[2]) / 2)
        aneis.append([P(u, v, w) for (u, w) in pts])
    p = loft(aneis, 'pol_smg_grip')
    cut(p, [poco('pol_smg_grip'),
            solido(Polygon([ax(100, -MW - 1.4), ax(100, MW + 1.4), ax(122, MW + 3.6), ax(122, -MW - 3.6)]), -MZ - 2.0, MZ + 2.0, 'pol_smg_grip')])   # boca do poço mais aberta
    o.append(bevel(p, 1.0, 2, 50))
    # gravações
    o.append(texto('FAÍSCA 9', 4.4, 44, 7.5, -(W + CS + 0.03)))
    o.append(texto('CAL. 9 MM', 2.6, 44, 1.5, -(W + CS + 0.03)))
    o.append(texto('FEITA NO RECOMEÇO', 2.0, 158, -13.5, -(W + 0.03)))
    o.append(texto('RC 311207', 2.6, 58, -22.5, W + CS + 0.03, lado=1))
    for s in (-1, 1):                                                                      # posições do seletor
        for (letra, ang) in (('T', 0), ('1', -45), ('A', -90)):
            a = math.radians(ang)
            o.append(texto(letra, 2.4, P_SEL[0] + 17.6 * math.cos(a) * 1.0, P_SEL[1] + 16.2 * math.sin(a) - 1.1,
                           s * (W + CS + 0.03), lado=s))
    f = parte('corpo', o, origem=(20, -20, 0), grupo='A', suave=28)

    # trilhos: inteiro em cima, curtos embaixo e à direita
    tr = [_trilho(U0 + 4, U1 - 8, lambda x, y: (x, VT + 5.5 + y), lambda u: box(u - 5.23, u, VT + 2.5, VT + 8, -12, 12, 'anod'), 186.0, 25),
          _trilho(130, U1 - 6, lambda x, y: (x, VB - 5.5 - y), lambda u: box(u - 5.23, u, VB - 8, VB - 2.5, -12, 12, 'anod'), 188.0, 6),
          _trilho(130, U1 - 6, lambda x, y: (W + 5.5 + y, -1.0 + x), lambda u: box(u - 5.23, u, -13, 11, W + 2.5, W + 8, 'anod'), 188.0, 6)]
    for u in (-50, 60, 170):                                                               # parafusos do trilho de cima
        pf = cyl((u + 2.4, VT + 3.2, 0), (u + 2.4, VT + 4.4, 0), 2.2, 'fosf', n=16)
        cut(pf, cyl((u + 2.4, VT + 3.6, 0), (u + 2.4, VT + 6, 0), 1.1, 'fosf', n=6))
        tr.append(pf)
    parte('trilhos', tr, pai=f, grupo='B')

    # cano com ressalto e rosca 9 mm
    prof = [(168, 4.5), (168, 9.5), (207, 9.5), (209, 7.8), (220.4, 7.8), (221.0, 6.3)]
    u = 221.0
    while u < XM - 1.2:
        prof += [(u + 0.25, 6.75), (u + 0.75, 6.75), (u + 1.0, 6.3)]
        u += 1.0
    prof += [(XM - 0.5, 6.3), (XM, 5.8), (XM, 5.0), (XM - 0.8, 4.5)]
    cn = [lathe(prof, 'aco_cano', n=40, anel=True)]
    porca = lathe([(U1 - 0.2, 9.5), (U1 - 0.2, 13.0), (U1 + 4.2, 13.0), (U1 + 5.0, 12.2), (U1 + 5.0, 9.5)], 'fosf', n=12)      # porca do cano
    cn.append(bevel(porca, 0.4, 1, 20))
    parte('cano', cn, origem=(U1, 0, 0), pai=f, grupo='B')

    # pinos, retém do carregador, trava da coronha e argola da bandoleira
    pn = []
    for (u, v, z, r) in ((8, -22, W + CS, 2.1), (-52, -14, W + CS, 2.1), (100, -27, W, 2.1), (124, 6, W, 1.8)):
        pn.append(cyl((u, v, -z - 0.5), (u, v, z + 0.5), r, 'fosf', n=16))
    pn.append(cyl((176, -19, -W - 0.5), (176, -19, W - 0.2), 2.1, 'fosf', n=16))
    bt = cyl((55.5, -40.5, -13.6), (55.5, -40.5, 13.6), 4.2, 'fosf', n=20)                 # botão que atravessa, atrás do guarda-mato
    cut(bt, [cyl((55.5, -40.5, s * 13.0), (55.5, -40.5, s * 15), r, 'fosf', n=20) for s in (-1, 1) for r in (1.4,)])
    pn.append(bevel(bt, 0.4, 1, 40))
    tv = solido(arred([(U0 - 2.4, -5), (U0 + 6, -5), (U0 + 6, 6), (U0 - 2.4, 6)], 1.6, 3), -8, 8, 'fosf')                # trava da coronha (atrás)
    cut(tv, [box(U0 - 4, U0 - 1.6, -3.4 + i * 2.0, -2.5 + i * 2.0, -10, 10, 'fosf') for i in range(5)])
    pn.append(bevel(tv, 0.4, 1, 40))
    ca = (U0 + 8, -12)
    aro = [(ca[0] + 5.2 * math.cos(2 * math.pi * i / 20), ca[1] + 5.2 * math.sin(2 * math.pi * i / 20), -(W + CS + 2.6)) for i in range(20)]
    pn.append(fio(aro, 1.25, 'fosf'))
    pn.append(cyl((ca[0], ca[1] + 5.2, -(W + CS - 0.5)), (ca[0], ca[1] + 5.2, -(W + CS + 3.4)), 2.3, 'fosf', n=14))
    parte('pinos', pn, pai=f, grupo='B')
    return f


# ------------------------------------------------------------------ peças que mexem
def ferrolho():
    b = box(0, 110, 1.5, 16.5, -12.4, W - 3.6, 'aco_polido')
    cut(b, [box(56, 71, 5.4, 12.6, W - 4.6, W, 'aco_polido'),                              # rebaixo do extrator
            *[box(u, u + 2.4, -2, 20, W - 4.3, W, 'aco_polido') for u in (20, 26, 32, 80, 86, 92)]])
    ex = bevel(solido(arred([(57, 6.2), (69.4, 6.2), (70.2, 9), (69.4, 11.8), (57, 11.8)], 0.7, 3), W - 4.6, W - 3.3, 'fosf'), 0.25, 1, 40)
    return parte('ferrolho', [bevel(b, 0.5, 1, 40), ex], origem=(0, 0, 0), grupo='B')


def alavanca():
    """Alavanca de manejo em T atrás, embaixo do trilho (puxa para trás), com ganchos para os dedos."""
    pts = [(-84, -27.5), (-68, -27.5), (-68, -22.6), (-75.2, -22.6), (-75.2, 22.6), (-68, 22.6), (-68, 27.5), (-84, 27.5)]
    t = solido(arred(pts, 1.2, 3), 14.5, 22.6, 'polim', plane='uw')
    cut(t, [box(-86, -83.0, 10, 30, s * w0, s * w0 + 1.6, 'polim') for s in (-1, 1) for w0 in (17.5, 20.7, 23.9)] +
           [box(-86, -83.0, 10, 30, -1.6 - s * 1.6 - 0.8, -s * 1.6 + 0.8 - 0.8, 'polim') for s in (0,)])
    haste = bevel(box(-76, -42, 16.2, 20.8, -3.0, 3.0, 'fosf'), 0.4, 1, 40)
    return parte('alavanca', [bevel(t, 0.7, 2, 40), haste], origem=(0, 0, 0), grupo='B')


def seletor():
    """Seletor ambidestro: alavanca curta com apoio estriado."""
    px, py = P_SEL
    o = []
    for s in (-1, 1):
        a, b = lados(s, W + CS - 1.2, W + CS + 1.6)
        o.append(cyl((px, py, a), (px, py, b), 5.6, 'fosf', n=24))
        lev = arred([(3, -16), (16, -15.5), (26, -10.5), (24, -7), (12, -8.5), (3, -9)], 1.3, 4)
        a, b = lados(s, W + CS + 0.9, W + CS + 3.4)
        t = solido(lev, a, b, 'fosf')
        c, d = lados(s, W + CS + 2.8, W + CS + 5)
        cut(t, [box(15.5 + i * 2.0, 16.4 + i * 2.0, -18, -4, c, d, 'fosf') for i in range(5)] +
               [cyl((px, py, c), (px, py, d), 1.5, 'fosf', n=6)])
        o.append(bevel(t, 0.3, 1, 40))
    return parte('seletor', o, origem=(px, py, 0), grupo='B')


def gatilho():
    px, py = P_GAT
    d = [(0.2, -2.0), (-1.6, -8.0), (-2.2, -13.0), (-1.2, -16.2), (1.2, -18.4)]
    lam = LineString([(px + a, py + b) for a, b in d]).buffer(1.9, quad_segs=5)
    lam = unary_union([lam, Point(px, py).buffer(3.4, 6)])
    p = solido(lam, -3.4, 3.4, 'fosf')
    cut(p, [box(px - 0.4 + 0.0, px + 6, py - 6.5 - i * 2.2, py - 5.6 - i * 2.2, -5, 5, 'fosf') for i in range(5)])     # estrias da frente
    bevel(p, 0.6, 2, 40)
    return parte('gatilho', [p, cyl((px, py, -4.2), (px, py, 4.2), 1.5, 'fosf_escuro', n=14)], origem=(px, py, 0), grupo='B')


def coronha():
    """Coronha de duas varetas que corre por dentro do corpo; soleira de polímero com borracha estriada."""
    vr = []
    for s in (-1, 1):
        vr.append(lathe([(0, 0), (0, RV), (96, RV), (96.8, RV - 0.8), (98.6, RV - 0.8), (99.4, RV), (184, RV), (185, RV - 1), (185, 0)],
                        'fosf_escuro', n=24, c0=(U0 - 16, VV, s * WV)))
    f = parte('varetas', vr, origem=(U0, 0, 0), grupo='B')
    sol = solido(arred([(U0 - 18, 11), (U0 - 4, 11), (U0 - 4, -4), (U0 - 8.5, -68), (U0 - 12, -72), (U0 - 18, -72)], 3.0, 5), -21, 21, 'pol_smg')
    cortes = []
    for s in (-1, 1):
        a, b = lados(s, 21 - 1.6, 26)
        cortes.append(solido(arred([(U0 - 15.5, -24), (U0 - 8.2, -24), (U0 - 11.2, -62), (U0 - 15.5, -64)], 1.8, 4), a, b, 'pol_smg'))
    cortes.append(box(U0 - 12, U0, -66, -24, -11, 11, 'pol_smg'))                             # alívio na frente, entre as varetas
    cut(sol, cortes)
    o = [bevel(sol, 1.6, 3, 40)]
    for s in (-1, 1):                                                                         # buchas das varetas
        o.append(bevel(cyl((U0 - 5, VV, s * WV), (U0 - 1.5, VV, s * WV), 6.4, 'pol_smg', n=20), 0.6, 1, 40))
    pad = solido(arred([(U0 - 24, 11), (U0 - 18, 11), (U0 - 18, -72), (U0 - 24, -72)], 2.2, 4), -21, 21, 'borracha')
    cut(pad, [box(U0 - 26, U0 - 22.8, v, v + 2.4, -18.5, 18.5, 'borracha') for v in [-66 + 6.0 * i for i in range(13)]])
    o.append(bevel(pad, 0.5, 2, 40))
    parte('soleira', o, origem=(U0, 0, 0), pai=f, grupo='A', suave=40)
    return f


def cartucho(base, dir_, mat_e='latao', mat_p='cobre'):
    """Cartucho 9 mm: base = centro do culote (u, v, w), dir_ = direção (u, v) da ponta."""
    e = (dir_[0], dir_[1], 0)
    est = lathe([(0, 0), (0, 4.6), (0.4, 4.95), (1.2, 4.95), (1.5, 4.5), (2.2, 4.5), (2.5, 4.95), (19.1, 4.85), (19.1, 4.45)], mat_e, n=18, c0=base, eixo=e)
    pro = lathe([(18.6, 4.48), (22.5, 4.4), (25.5, 3.7), (28.0, 2.4), (29.3, 1.0), (29.6, 0)], mat_p, n=18, c0=base, eixo=e)
    return [est, pro]


def carregador():
    """Carregador reto de polímero, fila dupla, com canal de reforço, furos de contagem e base com apoio de dedo."""
    corpo_ = solido(arred(faixa(0, ML, MW), 2.6, 5), -MZ, MZ, 'polim')
    topo = Polygon([ax(-4, -MW - 2), ax(-4, MW + 2), ax(4.5, MW + 2), ax(9.0, -MW + 14), ax(9.0, -MW - 2)])     # boca: mais baixa atrás
    oco = Polygon([ax(-5, -MW + 1.6), ax(-5, MW - 1.6), ax(16, MW - 1.6), ax(16, -MW + 1.6)])
    cortes = [solido(topo, -20, 20, 'polim'), solido(oco, -MZ + 1.4, MZ - 1.4, 'polim'),
              box(T[0] - 16, T[0] + 14, T[1] - 6, T[1] + 14, -3.6, 3.6, 'polim')]
    for s in (-1, 1):
        a, b = lados(s, MZ - 0.9, MZ + 3)
        cortes.append(solido(arred(faixa(26, ML - 16, 3.4), 2.4, 4), a, b, 'polim'))               # canal de reforço
    for i in range(4):                                                                              # furos de contagem (atrás, à esquerda)
        c = ax(40 + i * 22.0, -11.0)
        cortes.append(cyl((c[0], c[1], -20), (c[0], c[1], -MZ + 1.6), 1.7, 'polim', n=14))
    cut(corpo_, cortes)
    o = [bevel(corpo_, 0.6, 2, 40)]
    o.append(solido(Polygon([ax(10.5, -MW + 1.8), ax(8.4, MW - 1.8), ax(13, MW - 1.8), ax(15, -MW + 1.8)]), -MZ + 1.5, MZ - 1.5, 'polim_claro'))   # transportador
    f = lambda t, n: ax(ML + t, n)
    base = arred([f(-1.0, -18.6), f(-1.0, 19.6), f(4.5, 22.0), f(9.0, 21.4), f(9.0, -18.6)], 1.5, 4)
    bp = solido(base, -12.6, 12.6, 'polim')
    cut(bp, [solido(Polygon([f(7.2, -14 + i * 4.2), f(7.2, -12.5 + i * 4.2), f(11, -12.5 + i * 4.2), f(11, -14 + i * 4.2)]), -9, 9, 'polim') for i in range(8)])
    o.append(bevel(bp, 1.4, 3, 40))
    cb = ax(4.4, -13.6)
    o += cartucho((cb[0], cb[1], 0), (math.cos(math.radians(4)) * N[0], N[1] + math.sin(math.radians(4))))
    c = ax(ML - 9, 0)
    o.append(texto('30', 3.4, c[0], c[1] - 1.5, -(MZ + 0.03)))
    c = ax(ML - 9, 0)
    o.append(texto('9 MM', 2.6, c[0], c[1] - 1.2, MZ + 0.03, lado=1))
    return parte('carregador', o, origem=(T[0], T[1], 0), grupo='B')


def montar():
    corpo()
    ferrolho()
    alavanca()
    seletor()
    gatilho()
    coronha()
    carregador()
