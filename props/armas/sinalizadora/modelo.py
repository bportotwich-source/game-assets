"""Pistola sinalizadora no nível de detalhe da M4A1: um tiro, cano curto e grosso que bascula
para baixo, cão externo, guarda-mato redondo e cabo curvo com talas pretas quadriculadas.
Armação e cano de alumínio anodizado laranja. Desenho próprio, sem marcas de fabricante.

Mesmas medidas e pontos da sinalizadora antiga (arma12_sinalizadora.py), para os nós (cano,
cartucho, cão, gatilho, trava), os cartuchos de sinal e as animações continuarem valendo.

Coordenadas em mm (lib.py da M4A1): u = para a frente (0 na culatra), v = para cima (0 no eixo
do cano), w = direita.
"""
import math
import bpy, bmesh
from shapely.geometry import Polygon, LineString, Point, box as caixa2d
from shapely.ops import unary_union
from shapely import affinity
from lib import *
from lib import _obj

# ------------------------------------------------------------------ medidas
SR = 14.5                          # raio de fora do cano
SB = 10.6                          # raio da alma (calibre 12 de sinal)
SL = 118.0                         # comprimento do cano
SH = (24.0, -21.0)                 # dobradiça do cano
P_CAO = (-30.0, -4.0)
P_GAT = (2.0, -27.0)
P_TRAVA = (-4.0, 9.0)
FA = 12.5                          # meia largura da armação
NUC = 10.8                         # meia largura do cabo sem as talas
TALA = 15.0                        # meia largura do cabo com as talas
V_MIRA = 18.5                      # linha de visada (entalhe atrás, dente na boca)
AL = 'laranja_sinal'


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


def curva(pts, n=5):
    """Contorno suavizado (Chaikin) de uma lista de pontos fechada."""
    for _ in range(n and 2):
        q = []
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            q += [(0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]), (0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1])]
        pts = q
    return Polygon(pts)


CABO = curva([(-16, -12), (-24, -26), (-31, -50), (-40, -75), (-52, -98), (-60, -112), (-72, -121), (-88, -118),
              (-93, -105), (-86, -86), (-75, -64), (-64, -40), (-56, -18), (-49, 2), (-40, 4)])


# ------------------------------------------------------------------ armação, talas
def armacao():
    fora = arred([(-50, -4), (-46, 11), (-36, 17.2), (0, 17.2), (0, -15.6), (40, -15.6), (46, -19), (44, -28), (30, -32), (0, -31),
                  (-27, -27)], 2.5, 5)
    c = solido(fora, -FA, FA, AL)
    cortes = [box(-46, -14, -12, 30, -3.8, 3.8, AL),                                # janela do cão
              box(8, 50, -34, -15.4, -6.6, 6.6, AL),                                # garfo da dobradiça (o ressalto do cano entra aqui)
              box(-6, 12, -34, -20, -3.0, 3.0, AL)]                                 # fenda do gatilho
    for s in (-1, 1):                                                               # rebaixo dos lados, atrás da culatra
        a, b = sorted((s * 11.0, s * 20))
        cortes.append(solido(arred([(-40, -8), (-6, -8), (-6, 10), (-34, 10), (-42, 2)], 2.5, 4), a, b, AL))
    cut(c, cortes)
    o = [bevel(c, 0.8, 2, 34)]
    # entalhe de mira em cima, atrás
    al = solido(arred([(-41, 16.5), (-31, 16.5), (-31, 21.0), (-39, 21.0)], 0.6, 3), -6.0, 6.0, AL)
    cut(al, [box(-45, -25, V_MIRA, 25, -1.6, 1.6, AL), box(-45, -25, 10, 25, -3.8, 3.8, AL)])
    o.append(bevel(al, 0.3, 1, 40))
    # guarda-mato redondo
    anel = affinity.scale(Point(4, -50).buffer(22.5, 16).difference(Point(4, -50).buffer(18.5, 16)), 1.08, 0.94)
    o.append(bevel(solido(anel.difference(caixa2d(-100, -29.5, 100, 100)), -4.5, 4.5, AL), 1.2, 3, 40))
    # cabo: núcleo da armação
    nuc = solido(CABO, -NUC, NUC, AL)
    o.append(bevel(nuc, 3.0, 4, 50))
    # olhal do cordão no pé do cabo
    ol = Point(-80, -119).buffer(5.2, 8).difference(Point(-80, -120.5).buffer(2.6, 8))
    o.append(bevel(solido(ol, -2.4, 2.4, 'inox'), 0.5, 1, 40))
    o.append(cyl((SH[0], SH[1], -FA - 0.3), (SH[0], SH[1], FA + 0.3), 3.2, 'inox', n=20))     # pino da dobradiça
    o.append(cyl((-0.6, 0, 0), (0.3, 0, 0), 2.4, 'fosf', n=16))                               # bucha do percussor
    for (u, v) in ((-30, -4), (4, -24), (-20, -18), (32, -25)):                               # pinos da armação
        o.append(cyl((u, v, -FA - 0.3), (u, v, FA + 0.3), 1.6, 'fosf', n=14))
    o.append(texto('SINAL 12', 2.6, -22, 2.0, -(11.0 + 0.02), mat='tinta_preta'))
    o.append(texto('RC 120459', 1.8, -22, 2.0, 11.0 + 0.02, mat='tinta_preta', lado=1))
    f = parte('armacao', o, origem=(-10, -10, 0), grupo='A', suave=40)

    # talas pretas que abraçam o cabo: borda lisa e abaulada, quadriculado no meio (relevo), um parafuso
    forma = arred(CABO.buffer(-2.4).intersection(caixa2d(-120, -116, 20, -14)), 3.0, 8)
    par = []
    for s, nome in ((-1, 'tala_esquerda'), (1, 'tala_direita')):
        a, b = sorted((s * 6.4, s * TALA))
        parte(nome, [bevel(solido(forma, a, b, 'polim_sinal_grip'), 4.2, 6, 50)], origem=(-60, -68, s * NUC), pai=f, grupo='A', suave=50)
        cp = cyl((-60, -68, s * (TALA - 0.9)), (-60, -68, s * (TALA + 0.35)), 2.7, 'inox', n=20)
        a, b = sorted((s * (TALA - 0.1), s * (TALA + 2)))
        cut(cp, box(-63.2, -56.8, -68.4, -67.6, a, b, 'inox'))
        par.append(bevel(cp, 0.3, 1, 40))
        par.append(cyl((-60, -68, s * (TALA - 1.4)), (-60, -68, s * (TALA - 0.5)), 3.7, 'polim', n=20))
    parte('parafusos_talas', par, pai=f, grupo='A')
    return f


# ------------------------------------------------------------------ cano, cartucho, cão, gatilho, trava
def cano():
    """Cano basculante: culatra reforçada, anéis de pega, coroa na boca, ressalto da dobradiça
    embaixo, dente da trava em cima e dente de mira na boca."""
    c = lathe([(0, SB), (0, SR + 1.4), (20, SR + 1.4), (23, SR), (SL - 9, SR), (SL - 8, SR + 1.0), (SL - 1.5, SR + 1.0), (SL, SR - 0.6),
               (SL, SB + 1.2), (SL - 1.2, SB)], AL, n=56, anel=True)
    cut(c, [lathe([(0, SR + 0.25), (0, SR + 3), (1.4, SR + 3), (1.4, SR + 0.25)], AL, n=56, c0=(u, 0, 0), anel=True) for u in (66, 71, 76, 81)])
    o = [c]
    res = solido(arred([(9, -25), (39, -25), (39, -8), (9, -8)], 4.0, 5), -6.2, 6.2, AL)                                     # ressalto da dobradiça
    o.append(bevel(res, 0.5, 1, 40))
    o.append(bevel(solido(arred([(0, 13), (14, 13), (14, 18.6), (0, 18.6)], 1.0, 3), -4.0, 4.0, AL), 0.4, 1, 40))            # dente da trava
    o.append(lathe([(0, SB - 0.1), (0, SB + 1.8), (2.5, SB + 1.8), (2.5, SB - 0.1)], 'inox', n=48, anel=True))                 # anel extrator
    o.append(solido(Polygon([(SL - 9, SR), (SL - 2.5, SR), (SL - 3.5, V_MIRA), (SL - 6.5, V_MIRA)]), -1.1, 1.1, AL))            # dente de mira
    o.append(texto('SÓ CARTUCHO DE SINAL', 2.2, 46, -1.0, -(SR + 0.02), mat='tinta_preta'))
    return parte('cano', o, origem=(SH[0], SH[1], 0), grupo='B', suave=40)


def cartucho():
    """Cartucho de sinal vermelho na câmara: culote de latão com espoleta, casco de plástico e faixas brancas."""
    o = [lathe([(0, 0), (0, 11.9), (1.6, 11.9), (1.9, 10.3), (13, 10.3), (13, 0)], 'latao', n=32),
         lathe([(-0.1, 0), (-0.1, 2.8), (0.5, 2.8), (0.5, 0)], 'inox', n=16),
         lathe([(12, 0), (12, 10.1), (64, 10.1), (66, 9.4), (66.8, 7.2), (67.2, 0)], 'casco_vermelho', n=32)]
    for u in (30, 46):
        o.append(lathe([(u, 9.9), (u, 10.3), (u + 4, 10.3), (u + 4, 9.9)], 'tinta_branca', n=32, anel=True))
    return parte('cartucho', o, origem=(0, 0, 0), grupo='B', suave=40)


def cao():
    # espora deitada para trás, abaixo da linha de visada (não tampa o entalhe da mira)
    perfil = arred([(-35, -9), (-25, -7), (-22, 4), (-23, 12), (-30, 15.5), (-50, 15.5), (-55, 13.5), (-54, 10.5), (-42, 9), (-36, 4),
                    (-37, -2)], 1.4, 5)
    c = solido(perfil, -3.2, 3.2, 'fosf')
    cut(c, [box(-52.0 + i * 2.0, -51.1 + i * 2.0, 14.9, 18, -5, 5, 'fosf') for i in range(5)])        # serrilhas da espora
    return parte('cao', [bevel(c, 0.5, 2, 40), cyl((-30, -4, -3.6), (-30, -4, 3.6), 2.2, 'inox', n=16)], origem=(P_CAO[0], P_CAO[1], 0), grupo='B')


def gatilho():
    px, py = P_GAT
    d = [(1.0, -0.5), (-0.6, -7.0), (-1.8, -14.0), (-1.2, -20.0), (1.8, -24.0)]
    lam = LineString([(px + a, py + b) for a, b in d]).buffer(1.8, quad_segs=5)
    lam = unary_union([lam, Point(px, py).buffer(3.0, 6)])
    p = solido(lam, -2.8, 2.8, 'fosf')
    cut(p, [box(px - 6, px - 2.8 + 0.22 * abs(3 - i), py - 8.0 - i * 2.1, py - 7.2 - i * 2.1, -2.1, 2.1, 'fosf') for i in range(7)])
    return parte('gatilho', [bevel(p, 0.5, 2, 40)], origem=(px, py, 0), grupo='B')


def trava():
    """Alavanca da esquerda que solta o cano."""
    lev = arred([(-9, 4), (6, 6), (8, 12), (2, 16), (-9, 13)], 1.8, 5)
    p = solido(lev, -(FA + 1.9), -(FA - 0.2), 'fosf')
    cut(p, [box(-8 + i * 1.8, -7.1 + i * 1.8, 8, 17, -(FA + 2.6), -(FA + 1.4), 'fosf') for i in range(4)])
    return parte('trava', [bevel(p, 0.35, 1, 40), cyl((-4, 9, -(FA + 2.4)), (-4, 9, -(FA - 0.2)), 2.8, 'fosf', n=18)],
                 origem=(P_TRAVA[0], P_TRAVA[1], 0), grupo='B')


def montar():
    armacao()
    cano()
    cartucho()
    cao()
    gatilho()
    trava()
