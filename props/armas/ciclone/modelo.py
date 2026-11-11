"""Submetralhadora Ciclone 9 mm no nível de detalhe da M4A1: corpo de cima de alumínio, longo
e baixo (cano alto, na linha do ombro), com guarda-mão de fendas ovais; chassi de polímero em
V com o laço do guarda-mato inclinado como o punho, painel triangular pontilhado e o
carregador inclinado na frente; coronha de esqueleto que dobra para a direita. Desenho
próprio, sem marcas de fabricante.

Mesmas medidas e pontos da Ciclone antiga (arma10_ciclone.py), para os encaixes, os
acessórios e as animações continuarem valendo. Coordenadas em mm (lib.py da M4A1):
u = para a frente, v = para cima (0 no eixo do cano), w = direita.
"""
import math
import bpy, bmesh
from shapely.geometry import Polygon, LineString, Point, box as caixa2d
from shapely.ops import unary_union
from lib import *
from lib import _obj

# ------------------------------------------------------------------ medidas
CX0, CX1 = -112.0, 258.0          # corpo de cima: trás e frente (o guarda-mão começa em 170)
CY0, CY1 = -20.0, 22.0            # fundo e topo do corpo de cima (o trilho fica por cima)
CW = 16.5                         # meia largura do corpo de cima
WC = 15.9                         # meia largura do chassi
XM = 296.0                        # fim da rosca do cano
AN = math.radians(18)
TG = math.tan(AN)
D = (-math.sin(AN), -math.cos(AN))        # eixo do carregador (desce e vai para trás)
N = (math.cos(AN), -math.sin(AN))         # normal (frente)
T = (124.0, CY0)                  # topo do carregador (centro)
ML, MW, MZ = 162.0, 15.8, 10.8    # carregador: comprimento, meia largura (frente-trás), meia espessura
GX0 = -36.0                       # frente do punho no topo
HX, HY, HZ = CX0 + 4, 4.0, CW + 4.0       # dobradiça da coronha (lado direito)
P_GAT = (-12.0, -28.0)
P_SEL = (-50.0, -8.0)
PIC = [(7.85, 0), (10.6, -2.75), (7.9, -5.5), (-7.9, -5.5), (-10.6, -2.75), (-7.85, 0)]   # perfil do trilho (x, y a partir do topo)
TRI = Polygon([(34, -30), (100, -30), (60, -100)]).buffer(-4, join_style=2).buffer(2, quad_segs=4)   # painel do chassi


def gx(v):
    """Frente do punho em cada altura."""
    return GX0 - (CY0 - v) * TG


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


def oval(u0, u1, v0, v1, a, b, mat, r=None):
    r = (v1 - v0) / 2 - 0.1 if r is None else r
    return solido(arred([(u0, v0), (u1, v0), (u1, v1), (u0, v1)], r, 5), a, b, mat)


def _trilho(a, b, mapa, fenda, u_fenda, n):
    """Trilho de acessórios de a até b; mapa leva (x, y) do perfil para (w, v)."""
    t = extr([mapa(x, y) for (x, y) in PIC], a, b, 'anod', plane='wv')
    cut(t, [fenda(u_fenda - i * 10.008) for i in range(n)])
    return bevel(t, 0.35, 1, 40)


# ------------------------------------------------------------------ corpo de cima
def corpo():
    M_ = 'anod'
    sec = [(CW, CY0 - 1), (CW, CY1 - 4), (CW - 4, CY1)]
    sec = sec + [(-w, v) for (w, v) in reversed(sec)]
    c = extr(sec, CX0 - 1, CX1 + 1, M_, plane='wv')
    lado = arred([(CX0, CY1), (CX1, CY1), (CX1, CY0 + 4), (CX1 - 4, CY0), (CX0 + 4, CY0), (CX0, CY0 + 4)], 2.0, 4)
    cut(c, solido(lado, -30, 30, M_), op='INTERSECT')
    cortes = [solido(arred([(98, -11), (142, -11), (142, 13), (98, 13)], 2.5, 4), CW - 6, CW + 6, M_),       # janela do estojo
              box(20, 156, -13, 15, -11.5, CW - 2.5, M_),                                                   # caminho do ferrolho
              box(171, 254, -16.5, 18.5, -CW + 3.0, CW - 3.0, M_),                                          # guarda-mão oco
              cyl((150, 0, 0), (CX1 + 5, 0, 0), 10.8, M_, n=32),                                            # passagem do cano
              oval(30, 95, -6.5, -1.5, -CW - 6, -CW + 1.8, M_, r=1.5)]                                      # trilho da alavanca (esquerda)
    for s in (-1, 1):
        a, b = lados(s, CW - 4, CW + 6)
        for x0 in (176, 206):                                                                               # fendas ovais do guarda-mão
            for (y0, y1) in ((4, 12), (-12, -4)):
                cortes.append(oval(x0, x0 + 24, y0, y1, a, b, M_))
        cortes.append(oval(236, 250, 4, 12, a, b, M_))
        a, b = lados(s, CW - 2.2, CW + 6)
        cortes.append(oval(158, 168, -2.5, 2.5, a, b, M_))                                                  # furo pequeno
        a, b = lados(s, CW - 0.8, CW + 6)
        cortes.append(box(CX0 + 20, 90, 11.4, 12.8, a, b, M_))                                              # emenda de cima
    cut(c, cortes)
    bevel(c, 0.7, 2, 34)
    o = [c]
    o.append(bevel(box(CX0 - 0.4, CX0 + 8, -12, 16, CW - 2, HZ + 3.5, M_), 0.6, 1, 40))                     # bloco da dobradiça
    o.append(cyl((HX, -14, HZ), (HX, 18, HZ), 3.4, 'fosf', n=18))
    o.append(texto('CICLONE 9', 4.4, 0, 2.6, -(CW + 0.03)))
    o.append(texto('CAL. 9 MM', 2.6, 0, -3.4, -(CW + 0.03)))
    o.append(texto('RC 470032', 2.6, 40, 2.0, CW + 0.03, lado=1))
    for s in (-1, 1):                                                                                       # posições do seletor (a cauda aponta)
        for k, letra in enumerate(('T', '1', '2', 'A')):
            a = math.radians(180 - 40 * k)
            o.append(texto(letra, 2.0, P_SEL[0] + 9.8 * math.cos(a), P_SEL[1] + 9.8 * math.sin(a) - 0.9, s * (CW + 0.03), lado=s))
    f = parte('corpo', o, origem=(0, 0, 0), grupo='B', suave=28)
    tr = [_trilho(CX0 + 4, CX1 - 4, lambda x, y: (x, CY1 + 5.5 + y), lambda u: box(u - 5.23, u, CY1 + 2.5, CY1 + 8, -12, 12, 'anod'), 250.0, 36),
          _trilho(178, CX1 - 4, lambda x, y: (x, CY0 - 5.5 - y), lambda u: box(u - 5.23, u, CY0 - 8, CY0 - 2.5, -12, 12, 'anod'), 248.0, 7)]
    for u in (-90, 40, 160, 236):
        pf = cyl((u + 2.4, CY1 + 3.2, 0), (u + 2.4, CY1 + 4.4, 0), 2.2, 'fosf', n=16)
        cut(pf, cyl((u + 2.4, CY1 + 3.6, 0), (u + 2.4, CY1 + 6, 0), 1.1, 'fosf', n=6))
        tr.append(pf)
    parte('trilhos', tr, pai=f, grupo='B')
    # cano com porca e rosca 9 mm
    prof = [(160, 4.5), (160, 7.8), (247, 7.8), (247, 10.5), (265, 10.5), (268, 7.8), (283.4, 7.8), (284.0, 6.3)]
    u = 284.0
    while u < XM - 1.2:
        prof += [(u + 0.25, 6.75), (u + 0.75, 6.75), (u + 1.0, 6.3)]
        u += 1.0
    prof += [(XM - 0.5, 6.3), (XM, 5.8), (XM, 5.0), (XM - 0.8, 4.5)]
    cn = [lathe(prof, 'aco_cano', n=40, anel=True)]
    porca = lathe([(CX1 - 0.2, 10.5), (CX1 - 0.2, 13.2), (CX1 + 3.6, 13.2), (CX1 + 4.4, 12.4), (CX1 + 4.4, 10.5)], 'fosf', n=12)
    cn.append(bevel(porca, 0.4, 1, 20))
    parte('cano', cn, origem=(CX1, 0, 0), pai=f, grupo='B')
    return f


# ------------------------------------------------------------------ chassi de baixo
CAB = arred([(GX0 - 46, CY0), (GX0, CY0), (gx(-50), -50), (gx(-100) - 2, -100), (gx(-128) - 3, -128), (gx(-138) - 8, -138),
             (gx(-138) - 38, -138), (gx(-130) - 44, -130), (gx(-80) - 44, -80), (GX0 - 44, -30)], 2.5, 6)


def meia_largura(v):
    return 12.8 + 1.6 * smooth(-35, -60, v) + 0.6 * smooth(-120, -134, v)


def chassi(pai):
    M_ = 'pol_cic'
    fr = lambda v: T[0] + 22.2 - (CY0 - v) * TG                # frente do chassi: segue a frente do carregador
    fora = arred([(GX0 - 46, CY0 + 1), (fr(CY0) + 4, CY0 + 1), (fr(-116), -116), (fr(-116) - 30, -120), (40, -124), (gx(-128) - 4, -130),
                  (gx(-100) - 8, -100), (gx(-40) - 8, -40), (GX0 - 34, -28)], 3.5, 5)
    ya, yb = -35.0, -114.0
    laco = arred([(gx(ya) + 4, ya), (22, ya), (22 + (yb - ya) * TG, yb), (gx(yb) + 4, yb)], 6.0, 6)
    c = solido(fora.difference(laco), -WC, WC, M_)
    barra = Polygon([(gx(yb) - 20, yb - 0.5), (60, yb - 0.5), (75, -150), (gx(yb) - 20, -150)])
    cortes = [solido(faixa(-3, 300, MW + 0.8), -MZ - 0.6, MZ + 0.6, M_),                   # poço do carregador
              box(P_GAT[0] - 8, P_GAT[0] + 8, -42, CY0 + 3, -4.4, 4.4, M_)]                # fenda do gatilho
    for s in (-1, 1):
        a, b = lados(s, 7.8, 40)
        cortes.append(solido(barra, a, b, M_))                                             # barra de baixo mais fina
        a, b = lados(s, WC - 1.8, 40)
        cortes.append(solido(TRI, a, b, M_))                                               # painel triangular rebaixado
        a, b = lados(s, WC - 0.8, 40)
        cortes.append(extr([(fr(-30) - 3.0, -30), (fr(-30) - 1.6, -30), (fr(-108) - 1.6, -108), (fr(-108) - 3.0, -108)], a, b, M_))   # friso da frente
    cut(c, cortes)
    bevel(c, 1.2, 2, 34)
    pintar(c, 'pol_cic_painel', lambda p, n: abs(n[2]) > 0.9 and abs(abs(p[2]) - (WC - 1.8)) < 0.2 and TRI.contains(Point(p[0], p[1])))
    o = [c]
    # punho inclinado, pontilhado pelo relevo
    b = CAB.bounds
    aneis, n = [], 80
    for i in range(n + 1):
        v = (b[3] - 0.4) + ((b[1] + 0.4) - (b[3] - 0.4)) * i / n
        x = CAB.intersection(LineString([(-200, v), (120, v)])).bounds
        pts = superelipse((x[2] - x[0]) / 2, meia_largura(v), n=52, e=2.6, cx=(x[0] + x[2]) / 2)
        aneis.append([P(u, v, w) for (u, w) in pts])
    o.append(bevel(loft(aneis, 'pol_cic_grip'), 1.0, 2, 50))
    o.append(texto('FEITA NO RECOMEÇO', 2.0, 62, -26.0, -(WC + 0.03)))
    f = parte('chassi', o, origem=(0, -70, 0), pai=pai, grupo='A', suave=28)

    # pinos, retém do carregador e argola da bandoleira
    pn = []
    for (u, v, z) in ((GX0 - 30, -6, CW), (30, -6, CW), (75, 4, CW), (155, -8, CW), (215, -16, CW),
                      (88, -108, WC), (35, -119, 7.8), (6, -27, WC)):
        pn.append(cyl((u, v, -z - 0.5), (u, v, z + 0.5), 2.3, 'fosf', n=16))
    for s in (-1, 1):
        a, b = lados(s, 8, WC + 1.5)
        t = solido(arred([(23, -53), (30.5, -53), (30.5, -41), (23, -41)], 1.5, 3), a, b, 'fosf')
        c0, d0 = lados(s, WC + 0.9, WC + 4)
        cut(t, [box(20, 34, -51.4 + i * 2.2, -50.4 + i * 2.2, c0, d0, 'fosf') for i in range(5)])
        pn.append(bevel(t, 0.3, 1, 40))
    ca = (CX0 + 12, -6)
    aro = [(ca[0] + 5.2 * math.cos(2 * math.pi * i / 20), ca[1] + 5.2 * math.sin(2 * math.pi * i / 20), -(CW + 2.6)) for i in range(20)]
    pn.append(fio(aro, 1.25, 'fosf'))
    pn.append(cyl((ca[0], ca[1] + 5.2, -(CW - 0.5)), (ca[0], ca[1] + 5.2, -(CW + 3.4)), 2.3, 'fosf', n=14))
    parte('pinos', pn, pai=pai, grupo='B')
    return f


# ------------------------------------------------------------------ peças que mexem
def ferrolho():
    b = box(60, 150, -10.5, 12.5, -10.5, CW - 3.1, 'aco_polido')
    cut(b, [box(126.5, 141, -3, 5, CW - 4.1, CW, 'aco_polido'),
            *[box(u, u + 2.4, -14, 16, CW - 3.8, CW, 'aco_polido') for u in (100, 106, 112)]])
    ex = bevel(solido(arred([(127.5, -2.2), (139.4, -2.2), (140.2, 1), (139.4, 4.2), (127.5, 4.2)], 0.7, 3), CW - 4.1, CW - 2.8, 'fosf'), 0.25, 1, 40)
    return parte('ferrolho', [bevel(b, 0.5, 1, 40), ex], origem=(0, 0, 0), grupo='B')


def alavanca():
    """Alavanca de manejo do lado esquerdo: corrediça de aço e pega de polímero estriada."""
    cor = bevel(box(84, 94, -5.9, -2.1, -CW - 0.6, -CW + 1.6, 'fosf'), 0.3, 1, 40)
    pega = solido(arred([(83, -8.4), (97, -8.4), (97, 0.4), (83, 0.4)], 2.0, 4), -CW - 12.5, -CW - 0.5, 'polim')
    cut(pega, [box(96.2, 99, -12, 4, -CW - 3.2 - i * 2.4, -CW - 2.0 - i * 2.4, 'polim') for i in range(4)])
    return parte('alavanca', [cor, bevel(pega, 0.7, 2, 40)], origem=(0, 0, 0), grupo='B')


def seletor():
    """Seletor dos dois lados: alavanca comprida estriada, com a cauda apontando a posição."""
    px, py = P_SEL
    o = []
    for s in (-1, 1):
        a, b = lados(s, CW - 0.4, CW + 2.0)
        o.append(cyl((px, py, a), (px, py, b), 4.8, 'fosf', n=24))
        lev = arred([(-57, -11.5), (-36, -11), (-28, -7), (-34, -4.2), (-57, -4.5)], 1.3, 4)
        a, b = lados(s, CW + 0.8, CW + 3.2)
        t = solido(lev, a, b, 'fosf')
        c, d = lados(s, CW + 2.6, CW + 5)
        cut(t, [box(-41 + i * 2.0, -40.1 + i * 2.0, -14, -2, c, d, 'fosf') for i in range(5)] +
               [cyl((px, py, c), (px, py, d), 1.5, 'fosf', n=6)])
        o.append(bevel(t, 0.3, 1, 40))
    return parte('seletor', o, origem=(px, py, 0), grupo='B')


def gatilho():
    px, py = P_GAT
    d = [(0.2, -2.0), (-1.4, -9.0), (-2.4, -16.0), (-1.6, -21.0), (1.0, -24.0)]
    lam = LineString([(px + a, py + b) for a, b in d]).buffer(1.9, quad_segs=5)
    lam = unary_union([lam, Point(px, py).buffer(3.4, 6)])
    p = solido(lam, -3.4, 3.4, 'fosf')
    cut(p, [box(px - 0.6, px + 6, py - 10.5 - i * 2.2, py - 9.6 - i * 2.2, -5, 5, 'fosf') for i in range(5)])     # estrias da frente
    bevel(p, 0.6, 2, 40)
    return parte('gatilho', [p, cyl((px, py, -4.2), (px, py, 4.2), 1.5, 'fosf_escuro', n=14)], origem=(px, py, 0), grupo='B')


def coronha():
    """Coronha de esqueleto: barra de cima reta (apoio do rosto), barra de baixo inclinada, soleira com borracha.
    Aberta fica no meio; dobra 180° para a direita em volta do pino (nó coronha)."""
    X = HX
    sup = LineString([(X - 6, 11), (X - 220, 11)]).buffer(8.5, cap_style=2)
    inf = LineString([(X - 6, -4), (X - 80, -30), (X - 218, -64.5)]).buffer(6.8, cap_style=1, join_style=1, quad_segs=5)
    sol = arred([(X - 232, 19), (X - 212, 19), (X - 212, -75), (X - 232, -75)], 4.0, 5)
    furo = arred([(X - 228, 1), (X - 216.5, 1), (X - 216.5, -50), (X - 228, -50)], 3.5, 5)
    cab = caixa2d(X - 15, -11, X - 4.6, 19.5)                                               # cabeça da dobradiça
    g = unary_union([sup, inf, sol, cab]).difference(furo)
    g = Polygon(g.exterior, [i for i in g.interiors if Polygon(i).area > 30])
    c = solido(g, -11, 11, 'pol_cic')
    cortes = []
    for s in (-1, 1):
        a, b = lados(s, 11 - 1.5, 20)
        cortes.append(oval(X - 190, X - 40, 8.2, 13.8, a, b, 'pol_cic', r=2.6))             # canal ao longo da barra de cima
    cut(c, cortes)
    o = [bevel(c, 2.0, 3, 40)]
    o.append(bevel(box(X - 15, X - 4.6, -8, 16, 8, HZ + 5.5, 'pol_cic'), 1.2, 2, 40))       # braço até o pino
    bt = cyl((X - 9.5, 4, HZ + 5.0), (X - 9.5, 4, HZ + 7.2), 3.2, 'fosf', n=18)             # botão da trava
    o.append(bevel(bt, 0.4, 1, 40))
    pad = solido(arred([(X - 239, 19), (X - 231, 19), (X - 231, -75), (X - 239, -75)], 3.0, 4), -14.5, 14.5, 'borracha')
    cut(pad, [box(X - 241, X - 237.8, v, v + 2.4, -12.5, 12.5, 'borracha') for v in [-70 + 6.0 * i for i in range(15)]])
    o.append(bevel(pad, 0.5, 2, 40))
    return parte('coronha', o, origem=(HX, HY, HZ), grupo='A', suave=34)


def cartucho(base, dir_, mat_e='latao', mat_p='cobre'):
    """Cartucho 9 mm: base = centro do culote (u, v, w), dir_ = direção (u, v) da ponta."""
    e = (dir_[0], dir_[1], 0)
    est = lathe([(0, 0), (0, 4.6), (0.4, 4.95), (1.2, 4.95), (1.5, 4.5), (2.2, 4.5), (2.5, 4.95), (19.1, 4.85), (19.1, 4.45)], mat_e, n=18, c0=base, eixo=e)
    pro = lathe([(18.6, 4.48), (22.5, 4.4), (25.5, 3.7), (28.0, 2.4), (29.3, 1.0), (29.6, 0)], mat_p, n=18, c0=base, eixo=e)
    return [est, pro]


def carregador():
    """Carregador reto de pistola, fila dupla, com canal de reforço, furos de contagem e base com ressalto."""
    corpo_ = solido(arred(faixa(0, ML, MW), 2.6, 5), -MZ, MZ, 'polim')
    topo = Polygon([ax(-6, -MW - 2), ax(-6, MW + 2), ax(4.5, MW + 2), ax(9.0, -MW + 14), ax(9.0, -MW - 2)])     # boca: mais baixa atrás
    oco = Polygon([ax(-7, -MW + 1.6), ax(-7, MW - 1.6), ax(16, MW - 1.6), ax(16, -MW + 1.6)])
    cortes = [solido(topo, -20, 20, 'polim'), solido(oco, -MZ + 1.4, MZ - 1.4, 'polim'),
              box(T[0] - 18, T[0] + 16, T[1] - 8, T[1] + 14, -3.6, 3.6, 'polim')]
    for s in (-1, 1):
        a, b = lados(s, MZ - 0.9, MZ + 3)
        cortes.append(solido(arred(faixa(60, ML - 14, 3.5), 2.6, 4), a, b, 'polim'))               # canal de reforço
    for i in range(4):                                                                              # furos de contagem (atrás, à esquerda)
        c = ax(75 + i * 20.0, -10.0)
        cortes.append(cyl((c[0], c[1], -20), (c[0], c[1], -MZ + 1.6), 1.6, 'polim', n=14))
    cut(corpo_, cortes)
    o = [bevel(corpo_, 0.6, 2, 40)]
    o.append(solido(Polygon([ax(10.5, -MW + 1.8), ax(8.4, MW - 1.8), ax(13, MW - 1.8), ax(15, -MW + 1.8)]), -MZ + 1.5, MZ - 1.5, 'polim_claro'))   # transportador
    f = lambda t, n: ax(ML + t, n)
    base = arred([f(-1.0, -17.5), f(-1.0, 21.5), f(5.0, 23.5), f(9.5, 22.5), f(9.5, -17.5)], 1.6, 4)
    bp = solido(base, -12.8, 12.8, 'polim')
    cut(bp, [solido(Polygon([f(7.6, -13 + i * 4.2), f(7.6, -11.5 + i * 4.2), f(12, -11.5 + i * 4.2), f(12, -13 + i * 4.2)]), -9, 9, 'polim') for i in range(8)])
    o.append(bevel(bp, 1.4, 3, 40))
    cb = ax(4.4, -13.2)
    o += cartucho((cb[0], cb[1], 0), (math.cos(math.radians(4)) * N[0], N[1] + math.sin(math.radians(4))))
    c = ax(ML - 8, 0)
    o.append(texto('30', 3.4, c[0], c[1] - 1.5, -(MZ + 0.03)))
    o.append(texto('9 MM', 2.6, c[0], c[1] - 1.2, MZ + 0.03, lado=1))
    return parte('carregador', o, origem=(T[0], T[1], 0), grupo='B')


def montar():
    f = corpo()
    chassi(f)
    ferrolho()
    alavanca()
    seletor()
    gatilho()
    coronha()
    carregador()
