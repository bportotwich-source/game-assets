"""Revólver Vigia .38 no nível de detalhe da M4A1: seis tiros, tambor que abre para a
esquerda, cano com costela e proteção da vareta, cão de espora, talas de nogueira
quadriculadas. Desenho próprio, sem marcas de fabricante.

Mesmas medidas e pontos do revólver antigo (arma02_revolver.py), para os encaixes, os
acessórios e as animações continuarem valendo. Coordenadas em mm (lib.py da M4A1):
u = para a frente (0 na face de trás do tambor), v = para cima (0 no eixo do cano),
w = para a direita.
"""
import math
from shapely.geometry import Polygon, LineString, Point, box as caixa2d
from shapely.ops import unary_union
from lib import *

# ------------------------------------------------------------------ medidas
CY = -12.5                        # eixo do tambor (abaixo do eixo do cano)
RT = 18.6                         # raio do tambor
RC = 12.5                         # raio do círculo das câmaras
TL = 40.0                         # comprimento do tambor
FA = 9.2                          # meia largura da armação
P_CAO = (-17.0, -6.0)
P_GAT = (4.5, -29.0)
P_BRACO = (44.0, -26.0)
AZ = 'azulado'


def pl(g):
    return [(float(x), float(y)) for x, y in list(g.exterior.coords)[:-1]]


def arred(pts, r, n=6):
    g = pts if hasattr(pts, 'exterior') else Polygon(pts)
    return g.buffer(-r, quad_segs=n).buffer(2 * r, quad_segs=n).buffer(-r, quad_segs=n)


def solido(g, a, b, mat, plane='uv'):
    o = extr(pl(g), a, b, mat, plane)
    if g.interiors:
        m = 1.0 if a < b else -1.0
        cut(o, [extr([(float(x), float(y)) for x, y in list(i.coords)[:-1]], a - m, b + m, mat, plane) for i in g.interiors])
    return o


def smooth(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


CABO = arred([(-16.5, -30), (-17.5, -46), (-22.5, -68), (-27.5, -92), (-30.5, -108), (-33.5, -114.8), (-54.5, -114.8), (-58.2, -108.5),
              (-57.5, -96), (-51.5, -66), (-43, -42), (-35.5, -30)], 2.5, 8)


def larg_tala(v):
    return 8.5 + 6.8 * smooth(-30, -48, v) + 0.8 * math.exp(-((v + 80) / 20) ** 2)


# ------------------------------------------------------------------ armação e cano
def armacao():
    fora = [(56, 12.2), (56, -12), (50, -24), (40, -32.5), (20, -33.5), (21, -40), (19, -50), (10, -58), (-3, -59), (-12, -53),
            (-16, -60), (-25, -84), (-30, -104), (-52, -104), (-54, -94), (-46, -60), (-36, -30), (-30, -14), (-24, -2), (-20, 6),
            (-12, 12.2)]
    perfil = arred(fora, 1.8, 5)
    vao = arred([(-4, -34.5), (16, -34.5), (15.5, -44.5), (8, -52.5), (-3, -53), (-8, -47)], 3.0, 6)
    alto = perfil.difference(vao).difference(caixa2d(-80, -200, -12.8, -33))
    ch = solido(alto, -FA, FA, AZ)
    cortes = [box(-0.6, TL + 0.6, CY - RT - 1.2, CY + RT + 0.6, -30, 30, AZ),          # janela do tambor
              box(-27, -10.5, -12, 20, -3.6, 3.6, AZ),                                 # fenda do cão
              box(1, 12.5, -45, -26, -4.7, 4.7, AZ),                                   # fenda do gatilho
              cyl((-20, 0, 0), (0, 0, 0), 1.4, AZ, n=12),                              # furo do percussor
              box(4, 38, 10.6, 20, -1.3, 1.3, AZ),                                     # sulco de mira na ponte
              box(-13, -3.5, 9.4, 20, -1.5, 1.5, AZ)]                                  # entalhe da alça
    for s in (-1, 1):                                                                  # guarda-mato mais fino
        a, b = sorted((s * 5.2, s * 14))
        cortes.append(extr([(-13, -36.5), (24, -36.5), (24, -62), (-13, -62)], a, b, AZ))
    cut(ch, cortes)
    bevel(ch, 0.8, 2, 34)
    o = [ch]
    # escudo de recuo (atrás do tambor)
    esc = lathe([(-6, 0), (-6, RT + 0.8), (-1.2, RT + 0.8), (-1.2, 0)], AZ, n=64, c0=(0, CY, 0))
    cut(esc, [box(-10, 0, -31.5, 12.2, -19.5, 19.5, AZ)], op='INTERSECT')
    cut(esc, [box(-27, 0, -12, 20, -3.6, 3.6, AZ), cyl((-20, 0, 0), (2, 0, 0), 1.4, AZ, n=12)])
    o.append(bevel(esc, 0.5, 2, 34))
    # núcleo de aço do cabo (aparece na frente e nas costas, entre as talas)
    nuc = solido(CABO, -6.4, 6.4, AZ)
    cortes = []
    for i in range(30):                                                                # estrias finas das costas
        t = i / 29.0
        u, v = -41.2 - 15.2 * t, -42 - 62 * t
        cortes.append(extr([(u - 6, v), (u + 0.45, v + 0.2), (u + 0.45, v + 0.9), (u - 6, v + 0.7)], -4.6, 4.6, AZ))
    cut(nuc, cortes)
    o.append(bevel(nuc, 1.2, 3, 40))
    # cano com costela estriada e proteção da vareta
    tubo = lathe([(50, 4.6), (50, 8.8), (157.4, 8.8), (158.2, 8.0), (158.8, 8.0), (159.2, 7.4), (159.2, 5.6), (157.6, 4.6)], AZ, n=40, anel=True)
    o.append(tubo)
    lug = solido(arred([(52, -5.5), (150, -5.5), (152, -16), (146, -21.5), (60, -21.5), (52, -18)], 2.0, 5), -7.2, 7.2, AZ)
    cut(lug, [cyl((TL + 1, CY, 0), (TL + 41, CY, 0), 3.6, AZ, n=20), box(TL, TL + 39, CY - 3.6, CY + 3.6, -20, 0, AZ)])   # leito da vareta, aberto à esquerda
    o.append(bevel(lug, 1.6, 3, 40))
    cos = solido(arred([(52, 5.5), (157, 5.5), (157, 10.8), (52, 10.8)], 0.6, 3), -3.6, 3.6, AZ)
    cut(cos, [box(60 + i * 2.5, 60.9 + i * 2.5, 10.2, 12, -2.9, 2.9, AZ) for i in range(31)])
    o.append(bevel(cos, 0.3, 1, 40))
    # trilho curto embaixo da proteção
    sec = [(-5.0, 0), (5.0, 0), (5.0, -1.5), (8.0, -3.0), (8.0, -4.5), (7.0, -5.5), (-7.0, -5.5), (-8.0, -4.5), (-8.0, -3.0), (-5.0, -1.5)]
    tr = extr([(w, v - 20.3) for (w, v) in sec], 90, 144, AZ, plane='wv')
    cut(tr, [box(u - 2.65, u + 2.65, -30, -23.1, -12, 12, AZ) for u in (104, 117, 130)])
    o.append(bevel(tr, 0.35, 1, 40))
    # massa de mira em rampa com inserto laranja
    rampa = solido(arred([(138, 10.3), (155, 10.3), (155, 18.2), (151, 18.6)], 0.4, 3), -1.5, 1.5, AZ)
    cut(rampa, [box(138 + i * 1.5, 138.6 + i * 1.5, 10 + i * 1.0, 12.4 + i * 1.0, -3, 3, AZ) for i in range(7)])
    o.append(rampa)
    o.append(solido(arred([(150.6, 14.8), (154.6, 14.8), (154.6, 18.15), (150.6, 18.15)], 0.3, 2), -1.56, 1.56, 'tinta_laranja'))
    # alça de mira: lâmina na traseira da ponte
    al = solido(arred([(-12.5, 11.4), (-3.5, 11.4), (-3.5, 15.8), (-12.5, 15.8)], 0.5, 3), -6.2, 6.2, 'fosf')
    cut(al, box(-14, -2, 13.2, 17, -1.5, 1.5, 'fosf'))
    o.append(bevel(al, 0.3, 1, 40))
    # placa lateral (direita) com três parafusos de fenda, e o pino do cão
    o.append(bevel(solido(arred([(-26, -30), (40, -30), (50, -22), (50, -12), (-16, -4), (-26, -16)], 2.0, 5), FA - 0.2, FA + 0.35, AZ), 0.3, 1, 40))
    for (u, v) in ((6, -12), (-22, -27), (30, -26)):
        pf = cyl((u, v, FA + 0.2), (u, v, FA + 0.9), 2.0, 'inox', n=18)
        cut(pf, box(u - 2.4, u + 2.4, v - 0.3, v + 0.3, FA + 0.55, FA + 2, 'inox'))
        o.append(pf)
    o.append(cyl((P_CAO[0], P_CAO[1], -FA - 0.5), (P_CAO[0], P_CAO[1], FA + 0.5), 1.4, 'inox', n=14))
    o.append(texto('VIGIA .38', 3.0, 100, -15.2, -7.23))
    o.append(texto('RC 114038', 2.2, 100, -15.0, 7.23, lado=1))
    return parte('armacao', o, origem=(0, -20, 0), grupo='A')


def talas():
    """Talas de nogueira que seguem a curva do cabo; quadriculado no relevo da textura, medalhão e parafuso."""
    dentro = CABO.buffer(-0.7)
    aneis = []
    n = 64
    v1, v0 = dentro.bounds[1] + 0.4, dentro.bounds[3] - 0.4
    for i in range(n + 1):
        v = v0 + (v1 - v0) * i / n
        x = dentro.intersection(LineString([(-90, v), (40, v)])).bounds
        ub, uf = x[0], x[2]
        k = 1.0 - 0.35 * (1 - smooth(0, 5, v - v1)) - 0.25 * (1 - smooth(0, 3, v0 - v))       # fecha em cima e no pé
        aneis.append([P(u, v, w) for (u, w) in superelipse((uf - ub) / 2, larg_tala(v) * k, n=44, e=2.3, cx=(ub + uf) / 2)])
    p = loft(aneis, 'nogueira')
    o = [p]
    for s in (-1, 1):
        o.append(cyl((-38.5, -58, s * 14.0), (-38.5, -58, s * 16.05), 4.6, 'latao', n=28))          # medalhão
        pf = cyl((-41, -89, s * 14.0), (-41, -89, s * 16.55), 2.5, 'inox', n=18)
        a, b = sorted((s * 16.2, s * 18))
        cut(pf, box(-44, -38, -89.35, -88.65, a, b, 'inox'))
        o.append(pf)
    return parte('talas', o, origem=(-40, -70, 0), grupo='A', suave=50)


# ------------------------------------------------------------------ cão, gatilho, trava
def cao():
    cx, cy = P_CAO
    perf = arred([(-19, -12), (-12, -8), (-11.5, 4), (-8, 9.5), (-9.5, 12), (-17, 12), (-26, 17), (-31, 17.5), (-32, 14.5),
                  (-24, 9), (-21, 0), (-21, -8)], 0.8, 4)
    p = solido(perf, -3.3, 3.3, AZ)
    cut(p, [extr([(-31 + i * 1.6, 15.5 - i * 0.2), (-30.2 + i * 1.6, 15.4 - i * 0.2), (-30.2 + i * 1.6, 20), (-31 + i * 1.6, 20)], -5, 5, AZ) for i in range(6)])
    bevel(p, 0.5, 2, 40)
    return parte('cao', [p, cyl((-9.2, 0, 0), (-6.2, 0, 0), 1.2, 'inox', n=12)], origem=(cx, cy, 0), grupo='B')


def gatilho():
    lam = LineString([(6.2, -30.5), (4.6, -37), (4.2, -42.5), (5.2, -46.5), (8.2, -49.2)]).buffer(1.9, quad_segs=5)
    lam = unary_union([lam, Point(P_GAT).buffer(3.0, 6)])
    p = solido(lam, -4.3, 4.3, AZ)
    cut(p, [box(5.4, 9, -38.3 - i * 2.2, -37.6 - i * 2.2, -3.4, 3.4, AZ) for i in range(4)])
    bevel(p, 0.8, 2, 40)
    return parte('gatilho', [p], origem=(P_GAT[0], P_GAT[1], 0), grupo='B')


def trava():
    """Botão da trava do tambor (esquerda): empurra para a frente para abrir."""
    p = solido(arred([(-12, -4), (-2, -4), (-2, 1.5), (-12, 1.5)], 1.2, 4), -FA - 2.0, -FA + 0.1, AZ)
    cut(p, [box(-11 + i * 1.6, -10.3 + i * 1.6, -5, 3, -FA - 4, -FA - 1.5, AZ) for i in range(6)])
    return parte('trava', [bevel(p, 0.3, 1, 40)], origem=(0, 0, 0), grupo='B')


# ------------------------------------------------------------------ braço, tambor, extrator
def braco():
    b = solido(arred([(TL + 0.6, -30), (52, -30), (52, CY + 4), (TL + 0.6, CY + 4)], 1.5, 4), -7.2, 7.2, AZ)
    o = [bevel(b, 0.6, 2, 40), cyl((TL - 0.2, CY, 0), (TL + 6, CY, 0), 3.4, AZ, n=20)]
    return parte('braco', o, origem=(P_BRACO[0], P_BRACO[1], 0), grupo='B')


def tambor(pai):
    corpo = lathe([(0, 4.5), (0, RT - 0.8), (0.8, RT), (TL - 3, RT), (TL, RT - 2.5), (TL, 4.5)], AZ, n=72, c0=(0, CY, 0), anel=True)
    cortes = []
    for i in range(6):
        a = i * math.pi / 3
        cv, cw = CY + RC * math.cos(a), RC * math.sin(a)
        cortes.append(cyl((-10, cv, cw), (TL + 10, cv, cw), 4.95, AZ, n=24))                       # câmaras
        b = a + math.pi / 6
        r = RT + 1.7
        fv, fw = CY + r * math.cos(b), r * math.sin(b)
        cortes.append(lathe([(8, 0), (9, 2.4), (11.5, 3.7), (34, 3.7), (52, 3.7), (52, 0)], AZ, n=18, c0=(0, fv, fw)))    # canaletas, abertas na frente
        # entalhes de parada
        n1 = (math.cos(a), math.sin(a))
        t1 = (-math.sin(a), math.cos(a))
        q = lambda dr, dt: (CY + (RT + dr) * n1[0] + dt * t1[0], (RT + dr) * n1[1] + dt * t1[1])
        pts = [q(-1.1, -1.4), q(2, -1.4), q(2, 1.4), q(-1.1, 1.4)]
        cortes.append(extr([(w, v) for (v, w) in pts], 3.5, 7.5, AZ, plane='wv'))
    cortes.append(cyl((-1, CY, 0), (1.6, CY, 0), 9.9, AZ, n=32))                                   # alojamento da estrela
    cut(corpo, cortes)
    bevel(corpo, 0.3, 1, 40)
    return parte('tambor', [corpo], origem=(0, CY, 0), pai=pai, grupo='B')


def cartucho(base, mat_e='latao', mat_p='chumbo'):
    """Cartucho .38 deitado em u (aro em base)."""
    est = lathe([(0, 0), (0, 5.5), (0.6, 5.6), (1.4, 5.5), (1.6, 4.9), (29, 4.85), (29, 4.4)], mat_e, n=18, c0=base)
    pro = lathe([(28.5, 4.5), (31, 4.55), (31.8, 4.6), (32.2, 3.8), (36, 3.4), (38, 2.6), (38.6, 0)], mat_p, n=18, c0=base)
    esp = lathe([(-0.05, 0), (-0.05, 2.2), (0.3, 2.2)], 'inox', n=12, c0=base)
    return [est, pro, esp]


def extrator(pai):
    st = Point(0, 0).buffer(9.75, 12)
    for i in range(6):
        a = i * math.pi / 3
        st = st.difference(Point(RC * math.sin(a), RC * math.cos(a)).buffer(4.6, 8))
    est = extr([(w, v + CY) for (w, v) in pl(st)], 0.05, 1.6, AZ, plane='wv')
    o = [est, cyl((1.6, CY, 0), (TL + 31, CY, 0), 2.6, AZ, n=16),
         lathe([(TL + 28, 0), (TL + 28, 3.2), (TL + 30, 3.4), (TL + 37, 3.4), (TL + 39, 2.8), (TL + 39, 0)], 'fosf', n=20, c0=(0, CY, 0), lobes=0.1, lobe_min=3.3)]
    for i in range(6):
        a = i * math.pi / 3
        o += cartucho((-1.2, CY + RC * math.cos(a), RC * math.sin(a)))
    return parte('extrator', o, origem=(0, CY, 0), pai=pai, grupo='B')


def montar():
    armacao()
    talas()
    cao()
    gatilho()
    trava()
    b = braco()
    t = tambor(b)
    extrator(t)
