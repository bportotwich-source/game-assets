"""Carabina Paciência .308 no nível de detalhe da M4A1: ação de ferrolho com trilho, cano pesado
e carregador de caixa. Duas montagens da mesma ação:

  (padrão)        chassi de alumínio cor de areia, punho de pistola pontilhado, guarda-mão com
                  fendas, coronha de precisão vazada com apoio de rosto e cano estriado;
  VARIANTE=caca   coronha inteiriça de nogueira quadriculada, guarda-mato de aço azulado,
                  ponteira preta, cano liso mais curto e carregador de 5.

Desenho próprio, sem marcas de fabricante. Mesmas medidas e pontos da carabina antiga
(arma04_carabina.py), para os encaixes, os acessórios (lunetas, bocas, bipé, carregadores) e as
animações continuarem valendo. O que mudou de propósito: a coronha fica abaixo do caminho do
ferrolho (antes o ferrolho aberto atravessava a coronha e o apoio de rosto).

Coordenadas em mm (lib.py da M4A1): u = para a frente, v = para cima (0 no eixo do cano),
w = direita.
"""
import math, os
import bpy, bmesh
from shapely.geometry import Polygon, LineString, Point, box as caixa2d
from shapely.ops import unary_union
from lib import *
from lib import _obj

# ------------------------------------------------------------------ medidas
CACA = os.environ.get('VARIANTE', '') == 'caca'
RR = 16.5                          # raio do receptor (tubo)
KX0, KX1 = -70.0, 150.0            # receptor: trás e frente
CB = 100.0                         # curso do ferrolho
CAR_U, CAR_V = 45.0, -16.0         # topo do carregador (centro)
XM = KX1 + (530.0 if CACA else 560.0)          # boca do cano
P_GAT = (-24.0, -36.0 if CACA else -33.0)
V_TRILHO = RR + 4.5                # topo do trilho do receptor (encaixe_mira)
PIC = [(7.85, 0), (10.6, -2.75), (7.9, -5.5), (-7.9, -5.5), (-10.6, -2.75), (-7.85, 0)]   # perfil do trilho (x, y a partir do topo)
DU_CABO, DV_CABO = -64.5, 9.5      # o punho da Mutirão levado para baixo do chassi
METAL = 'azulado' if CACA else 'fosf'


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


def capsula(u0, u1, v, r):
    return LineString([(u0, v), (u1, v)]).buffer(r, quad_segs=5)


def esfera(c, r, mat, n=16):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=n, v_segments=n // 2, radius=r * MM)
    for v in bm.verts:
        v.co += P(*c)
    return _obj('esfera', bm, mat)


def trilho(u0, u1, v_topo, mat):
    t = extr([(x, v_topo + y) for (x, y) in PIC], u0, u1, mat, plane='wv')
    n = int((u1 - u0 - 6) / 10.008)
    cut(t, [box(u - 5.23, u, v_topo - 3, v_topo + 2.5, -12, 12, mat) for u in [u1 - 4.0 - i * 10.008 for i in range(n)]])
    return bevel(t, 0.35, 1, 40)


def corpo_u(perfil, larg, mat, e=2.5, n=120, voltas=56):
    """Corpo arredondado fatiado ao longo de u (coronhas): em cada u a altura vem do perfil e a
    meia largura de larg(u)."""
    b = perfil.bounds
    aneis = []
    for i in range(n + 1):
        u = (b[0] + 0.4) + ((b[2] - 0.4) - (b[0] + 0.4)) * i / n
        x = perfil.intersection(LineString([(u, -400), (u, 200)])).bounds
        pts = superelipse(larg(u), (x[3] - x[1]) / 2, n=voltas, e=e, cy=(x[1] + x[3]) / 2)
        aneis.append([P(u, v, w) for (w, v) in pts])
    return loft(aneis, mat)


CABO = arred([(-36.5, -43.5), (4.5, -43.5), (3.5, -56), (-3.5, -76), (-12, -100), (-19.5, -125), (-25.5, -146), (-29.5, -153.5),
              (-72.5, -155.5), (-75.5, -148), (-66, -120), (-55.5, -88), (-46.5, -62), (-42.5, -50)], 2.5, 6)


def meia_largura(v):
    return 11.8 + 3.2 * smooth(-46, -70, v) + 1.2 * math.exp(-((v + 100) / 22) ** 2)


# ------------------------------------------------------------------ ação: receptor, cano, ferrolho, gatilho, carregador
def receptor():
    c = lathe([(KX0, 0), (KX0, RR - 2), (KX0 + 2, RR), (KX1 - 2, RR), (KX1, RR - 1), (KX1, 0)], METAL, n=64)
    cut(c, [box(30, 112, -4, 30, 3, 30, METAL),                                    # janela de ejeção (direita, em cima)
            box(0, 100, -30, -10, -11.5, 11.5, METAL),                             # passagem do carregador
            box(-62, -34, -7, 7, 6, 30, METAL),                                    # entalhe da alavanca
            cyl((KX0 - 10, 0, 0), (118, 0, 0), 9.6, METAL, n=40)])                 # caminho do ferrolho
    bevel(c, 0.5, 2, 34)
    o = [c, trilho(KX0 + 8, KX1 - 4, V_TRILHO, 'anod')]
    o.append(bevel(solido(arred([(130, -30), (150, -30), (150, -12), (130, -12)], 1.5, 3), -12, 12, METAL), 0.4, 1, 40))      # garra de recuo
    tr = bevel(solido(arred([(-60, -6), (-30, -6), (-30, 2), (-60, 2)], 1.0, 3), RR - 3, RR + 1.6, 'fosf'), 0.4, 1, 40)       # trava de 3 posições
    cut(tr, [box(-57 + i * 2.6, -55.8 + i * 2.6, -8, 4, RR + 0.8, RR + 3, 'fosf') for i in range(4)])
    o.append(tr)
    o.append(cyl((-36, -2, RR + 1.55), (-36, -2, RR + 1.7), 1.3, 'tinta_vermelha', n=12))
    o.append(texto('PACIÊNCIA .308', 2.9, 62, 2.2, -(RR + 0.02)))
    o.append(texto('FERROLHO · RECOMEÇO', 1.6, 62, 6.2, -(RR - 0.9)))
    o.append(texto('RC 308417', 1.8, 122, 2.6, -(RR + 0.02)))
    return parte('receptor', o, origem=(40, 0, 0), grupo='A', suave=30)


def cano():
    r_em = lambda u: 14.5 + (u - (KX1 + 60)) * (10.8 - 14.5) / (XM - 30 - KX1 - 60)
    c = lathe([(KX1 - 2, 3.9), (KX1 - 2, 15.8), (KX1 + 40, 15.8), (KX1 + 60, 14.5), (XM - 30, 10.8), (XM - 16, 10.8), (XM - 15, 8.5),
               (XM - 0.5, 8.5), (XM, 7.5), (XM, 4.4), (XM - 2.5, 3.9)], 'aco_cano', n=56, anel=True)
    if not CACA:                                                                   # estrias de alívio
        ua, ub = KX1 + 100, XM - 90
        cs = []
        for i in range(6):
            a = math.radians(30 + i * 60)
            ra, rb = r_em(ua) + 1.3, r_em(ub) + 1.3
            cs.append(cyl((ua, ra * math.cos(a), ra * math.sin(a)), (ub, rb * math.cos(a), rb * math.sin(a)), 2.9, 'aco_cano', n=14))
            for u, r in ((ua, ra), (ub, rb)):
                cs.append(esfera((u, r * math.cos(a), r * math.sin(a)), 2.9, 'aco_cano', 12))
        cut(c, cs)
    return parte('cano', [c], origem=(KX1, 0, 0), grupo='B', suave=35)


def ferrolho():
    """Ferrolho (gira e corre no eixo do cano): corpo polido, capa de trás com indicador de armado,
    alavanca para a direita e para baixo com bola (caça) ou pomo recartilhado (chassi)."""
    o = [cyl((KX0 + 5, 0, 0), (117, 0, 0), 9.2, 'aco_polido', n=40)]
    o.append(bevel(box(100, 118, 3.5, 7.5, 8.2, 9.9, 'fosf'), 0.3, 1, 40))                                                    # extrator
    o.append(lathe([(-100, 0), (-100, 7.6), (-98.5, 9.0), (-93, 11.8), (KX0 - 0.5, 11.8), (KX0 - 0.5, 0)], 'fosf', n=40))
    o.append(cyl((-101.4, 0, 0), (-100, 0, 0), 2.8, 'tinta_vermelha', n=16))
    d = (0.0, -0.45, 0.89)
    k = math.sqrt(sum(x * x for x in d))
    d = tuple(x / k for x in d)
    p0 = (-48.0, 0.0, 6.0)
    em = lambda t: tuple(p0[i] + d[i] * t for i in range(3))
    o.append(cyl(p0, em(48), 3.6, 'aco_polido', n=20))
    o.append(bevel(box(-55, -41, -4, 4, 6, 11.4, 'aco_polido'), 0.8, 2, 40))
    if CACA:
        o.append(esfera(em(52), 8.5, 'aco_polido', 24))
    else:
        o.append(cyl(em(42), em(64), 9.5, 'anod', n=40, lobes=0.09))
        o.append(cyl(em(63.5), em(66), 7.5, 'anod', n=24, r1=6.0))
    return parte('ferrolho', o, origem=(0, 0, 0), grupo='B', suave=40)


def gatilho():
    px, py = P_GAT
    lam = LineString([(px + a, py + b) for a, b in ((1.5, -1), (-0.5, -7.5), (-1.8, -14), (-1.2, -19.8), (1.8, -23.5))]).buffer(1.9, quad_segs=5)
    lam = unary_union([lam, Point(px, py).buffer(3.0, 6)])
    p = solido(lam, -3.8, 3.8, 'fosf')
    cut(p, [box(px - 6, px - 3.4 + 0.2 * i, py - 10.6 - i * 2.2, py - 9.8 - i * 2.2, -5, 5, 'fosf') for i in range(4)])
    bevel(p, 0.6, 2, 40)
    return parte('gatilho', [p], origem=(px, py, 0), grupo='B')


def carregador():
    """Carregador de caixa de polímero (10 no chassi, 5 na de caça) com base, lábios de aço e um cartucho à vista."""
    baixo = -66.0 if CACA else -105.0
    c = solido(arred([(CAR_U - 39, baixo), (CAR_U + 39, baixo), (CAR_U + 39, CAR_V), (CAR_U - 39, CAR_V)], 2.0, 4), -11, 11, 'polim')
    rs = []
    v = CAR_V - 26.0
    while v > baixo + 10:                                                          # canaletas de pega
        for s in (-1, 1):
            a, b = lados(s, 9.4, 14)
            rs.append(box(CAR_U - 33, CAR_U + 33, v - 2.0, v + 2.0, a, b, 'polim'))
        v -= 9.0
    cut(c, rs + [box(CAR_U - 37, CAR_U + 37, CAR_V - 9, CAR_V + 5, -8.6, 8.6, 'polim')])
    o = [bevel(c, 0.6, 2, 40)]
    o.append(bevel(solido(arred([(CAR_U - 42, baixo - 6), (CAR_U + 43, baixo - 6), (CAR_U + 43, baixo + 3), (CAR_U - 42, baixo + 3)], 2.0, 4),
                          -12.9, 12.9, 'polim'), 0.8, 2, 40))
    o.append(texto('5' if CACA else '10', 4.0, CAR_U - 24, baixo + 10, -11.05))
    for s in (-1, 1):                                                              # lábios
        a, b = lados(s, 5.2, 8.8)
        o.append(box(CAR_U - 36, CAR_U + 30, CAR_V - 3.2, CAR_V + 1.2, a, b, 'fosf'))
    c0 = (CAR_U - 37, CAR_V - 4.6, 1.2)
    o.append(lathe([(0, 0), (0, 6), (1.2, 6), (1.6, 5.1), (2.2, 5.1), (2.9, 6), (39, 5.8), (42.6, 4.4), (51.3, 4.4), (51.3, 0)], 'latao', n=18, c0=c0))
    o.append(lathe([(51.0, 0), (51.0, 3.9), (56.5, 3.9), (62.5, 3.4), (67.5, 2.2), (70.8, 0.7), (71.1, 0)], 'cobre', n=18, c0=c0))
    return parte('carregador', o, origem=(CAR_U, CAR_V, 0), grupo='B', suave=40)


# ------------------------------------------------------------------ montagem de chassi
def chassi():
    M_ = 'areia'
    pf = arred([(-77, 0), (170, 0), (170, -26), (94, -30), (94, -53), (-1, -53), (-4, -34), (-77, -34)], 2.0, 4)
    c = solido(pf, -17.5, 17.5, M_)
    cortes = [cyl((KX0 - 10, 0, 0), (KX1 + 30, 0, 0), RR + 0.3, M_, n=64),
              box(CAR_U - 39.8, CAR_U + 39.8, -200, -15, -11.8, 11.8, M_),         # poço do carregador
              box(-35, -12, -50, -10, -4.2, 4.2, M_)]                              # passagem do gatilho
    for s in (-1, 1):                                                              # alívios nos lados
        a, b = lados(s, 15.8, 30)
        for u in (100, 135):
            cortes.append(solido(arred([(u, -24.5), (u + 30, -24.5), (u + 30, -15.5), (u, -15.5)], 3.0, 4), a, b, M_))
        cortes.append(solido(arred([(-68, -28), (-42, -28), (-42, -8), (-68, -8)], 3.0, 4), a, b, M_))
    cut(c, cortes)
    o = [bevel(c, 0.7, 2, 34)]
    fora = arred([(-66, -32), (-3, -32), (-3, -46), (-13, -64), (-50, -68), (-68, -58)], 5.0, 6)
    dentro = arred([(-56, -37.5), (-9, -37.5), (-9, -47), (-17, -58), (-46, -61), (-58, -52)], 4.0, 6)
    o.append(bevel(solido(fora.difference(dentro), -5.8, 5.8, M_), 1.3, 3, 40))
    ret = bevel(solido(arred([(-7.5, -52), (5, -50), (5, -44), (-6, -44)], 1.0, 3), -4.0, 4.0, 'fosf'), 0.4, 1, 40)            # retém do carregador
    o.append(ret)
    for (u, v) in ((-60, -18), (120, -8)):                                         # parafusos da ação
        o.append(cyl((u, v, -18.3), (u, v, 18.3), 2.4, 'inox', n=14))
    o.append(texto('SÓ MUNIÇÃO .308', 2.2, 30, -9, -17.52))
    f = parte('chassi', o, origem=(40, -20, 0), grupo='A', suave=30)

    # punho de pistola, pontilhado pelo relevo
    cb = CABO.bounds
    aneis, n = [], 84
    for i in range(n + 1):
        v = (cb[3] - 0.4) + ((cb[1] + 0.4) - (cb[3] - 0.4)) * i / n
        x = CABO.intersection(LineString([(-200, v), (120, v)])).bounds
        pts = superelipse((x[2] - x[0]) / 2, meia_largura(v), n=52, e=2.3, cx=(x[0] + x[2]) / 2 + DU_CABO)
        aneis.append([P(u, v + DV_CABO, w) for (u, w) in pts])
    g = bevel(loft(aneis, 'polim_car_grip'), 1.2, 2, 50)
    pf = cyl((-51 + DU_CABO, -156.4 + DV_CABO, 0), (-51 + DU_CABO, -154.6 + DV_CABO, 0), 3.2, 'inox', n=18)
    parte('punho', [g, pf], origem=(-93, -80, 0), grupo='A', suave=50)
    return f


def guarda_mao():
    M_ = 'areia'
    X0, X1 = 170.0, 500.0
    fora = arred([(-22, -31), (22, -31), (22, 19.5), (-22, 19.5)], 9.0, 6)
    g = solido(fora.difference(fora.buffer(-2.6, quad_segs=6)), X0, X1, M_, plane='wv')
    cortes = []
    u = X0 + 30.0
    while u + 26 < X1 - 12:
        cortes.append(solido(capsula(u, u + 26, -5.5, 3.6), -30, 30, M_))                          # lados
        cortes.append(solido(capsula(u, u + 26, 0.0, 3.6), -40, -20, M_, plane='uw'))              # embaixo
        for s in (-1, 1):                                                                          # quinas de cima
            a, b = lados(s, 12, 30)
            cortes.append(solido(capsula(u + 3, u + 23, 14.5, 2.4), a, b, M_))
        u += 42.0
    cut(g, cortes)
    o = [bevel(g, 0.5, 2, 34), trilho(X0 + 4, X1 - 4, 19.5 + 5.5, M_)]
    o.append(cyl((X1 - 30, -6, 21.6), (X1 - 30, -6, 23.4), 4.5, 'inox', n=20))                     # copo da bandoleira
    for u in (X0 + 12, X0 + 26):
        for s in (-1, 1):
            a, b = lados(s, 21.0, 22.9)
            o.append(cyl((u, -22, a), (u, -22, b), 2.3, 'inox', n=12))
    return parte('guarda_mao', o, origem=(X0, 0, 0), grupo='B', suave=34)


def coronha_precisao():
    """Coronha vazada de precisão: viga embaixo do caminho do ferrolho, pente atrás dele, soleira de borracha."""
    M_ = 'areia'
    perfil = arred([(-70, -12.5), (-203, -12.5), (-216, 7), (-330, 10), (-346, 9), (-352, -112), (-340, -121), (-300, -120),
                    (-200, -70), (-120, -46), (-77, -36), (-70, -34)], 3.0, 5)
    larg = lambda u: 16.6 + 3.4 * smooth(-100, -240, u)
    furo = arred([(-140, -29), (-268, -22), (-294, -58), (-274, -92), (-215, -72)], 8.0, 6)

    def bloco(mat, u0, u1):
        c = corpo_u(perfil, larg, mat, e=2.6, n=90, voltas=44)
        cut(c, [box(u0, u1, -200, 100, -60, 60, mat)], op='INTERSECT')
        return c
    corpo = bloco(M_, -340.5, 0)
    cut(corpo, [solido(furo, -50, 50, M_), cyl((-318, -105, -50), (-318, -105, 50), 4.5, M_, n=24),
                box(-300, -212, 3, 30, -9.5, 9.5, M_)])                                            # leito do apoio de rosto
    sol = bloco('borracha', -400, -340.5)
    cut(sol, [box(-360, -350.6, v - 2.0, v, -15, 15, 'borracha') for v in range(0, -112, -6)])
    o = [bevel(corpo, 1.0, 2, 34), bevel(sol, 0.8, 2, 34)]
    for s in (-1, 1):                                                                              # roda de regulagem do apoio
        a, b = lados(s, 18.0, 23.2)
        o.append(cyl((-256, -4, a), (-256, -4, b), 6.5, 'anod', n=28, lobes=0.08))
    f = parte('coronha', o, origem=(-210, -50, 0), grupo='A', suave=34)

    ap = arred([(-214, 8.5), (-298, 10.5), (-298, 23), (-290, 27), (-224, 27), (-214, 22)], 3.0, 5)
    a = bevel(corpo_u(ap, lambda u: 13.5, M_, e=3.0, n=40, voltas=40), 0.8, 2, 40)
    hs = [cyl((u, -6, 0), (u, 12, 0), 3.0, 'inox', n=16) for u in (-235, -278)]
    parte('apoio_face', [a] + hs, origem=(-256, 18, 0), grupo='A', suave=40)
    return f


# ------------------------------------------------------------------ montagem de caça
def coronha_caca():
    """Coronha inteiriça de nogueira: telha, punho de pistola, pente atrás do caminho do ferrolho,
    ponteira preta e soleira de borracha. O quadriculado do punho e da telha vem do relevo."""
    perfil = arred([(430, -6), (150, -2), (-58, -2), (-68, -12.5), (-196, -12.5), (-214, 3), (-330, 9), (-356, 10),
                    (-370, 6), (-370, -114), (-356, -121), (-300, -112), (-160, -84), (-95, -89), (-77, -83), (-62, -60),
                    (-50, -38), (100, -38), (250, -34), (400, -28), (428, -22)], 3.0, 5)
    larg = lambda u: (18.5 + 1.0 * smooth(180, 100, u) - 4.2 * math.exp(-((u + 100) / 45) ** 2) + 2.8 * smooth(-150, -260, u)
                      - 2.0 * smooth(300, 430, u))

    def bloco(mat, u0, u1):
        c = corpo_u(perfil, larg, mat, e=2.4, n=170, voltas=52)
        cut(c, [box(u0, u1, -200, 100, -60, 60, mat)], op='INTERSECT')
        return c
    corpo = bloco('nogueira_car', -356.2, 410)
    canal = [cyl((KX0 - 12, 0, 0), (KX1 + 2, 0, 0), RR + 0.4, 'nogueira_car', n=64),
             cyl((KX1, 0, 0), (450, 0, 0), 13.2, 'nogueira_car', n=48),
             box(CAR_U - 39.8, CAR_U + 39.8, -200, -15, -11.8, 11.8, 'nogueira_car'),
             box(-40, -10, -60, -10, -6, 6, 'nogueira_car'),
             box(-66, -30, -30, 10, 12, 40, 'nogueira_car')]                                       # entalhe da alavanca
    cut(corpo, canal)
    ponta = bloco('polim', 410, 500)
    cut(ponta, [cyl((400, 0, 0), (450, 0, 0), 13.2, 'polim', n=48)])
    sol = bloco('borracha', -400, -356.2)
    cut(sol, [box(-380, -368.8, v - 2.0, v, -16, 16, 'borracha') for v in range(0, -112, -6)])
    o = [bevel(corpo, 0.8, 2, 34), bevel(ponta, 0.8, 2, 34), bevel(sol, 0.8, 2, 34)]
    f = parte('coronha', o, origem=(0, -40, 0), grupo='A', suave=34)

    # ferragem de baixo: guarda-mato e chapa de aço azulado, retém do carregador, pinos da bandoleira
    M_ = 'azulado'
    fora = arred([(-58, -36.5), (-2, -36.5), (-4, -50), (-18, -65), (-50, -67), (-62, -54)], 5.0, 6)
    dentro = arred([(-50, -41.5), (-8, -41.5), (-10, -50), (-20, -60), (-46, -62), (-55, -52)], 4.0, 6)
    fe = [bevel(solido(fora.difference(dentro), -5.5, 5.5, M_), 1.2, 3, 40)]
    ch = solido(arred([(-70, -40.2), (95, -40.2), (95, -35), (-70, -35)], 1.0, 3), -8.5, 8.5, M_)
    cut(ch, [box(CAR_U - 39.8, CAR_U + 39.8, -60, -20, -11.8, 11.8, M_), box(-40, -10, -60, -10, -4.2, 4.2, M_)])
    fe.append(bevel(ch, 0.4, 1, 40))
    fe.append(bevel(solido(arred([(-7.5, -47), (4, -45.5), (4, -40.5), (-6, -40.5)], 1.0, 3), -4.0, 4.0, M_), 0.4, 1, 40))
    for (u, v) in ((380, -29.5), (-290, -108.5)):
        fe.append(cyl((u, v + 3, 0), (u, v - 6.5, 0), 2.6, 'inox', n=14))
        fe.append(fio([(u + 5.2 * math.cos(2 * math.pi * i / 20), v - 11 + 5.2 * math.sin(2 * math.pi * i / 20), 0) for i in range(20)], 1.2, 'inox'))
    parte('ferragem', fe, origem=(0, -45, 0), grupo='B', suave=40)

    # placas de fixação pretas na telha: lanterna (direita), laser (esquerda) e empunhadura (embaixo)
    pc = []
    for s in (-1, 1):
        a, b = lados(s, 14.0, 20.5)
        p = solido(arred([(330, -24.5), (390, -24.5), (390, -10.5), (330, -10.5)], 1.6, 4), a, b, 'polim')
        c0, c1 = lados(s, 19.0, 30)
        cut(p, [solido(arred([(336 + k * 26, -20), (358 + k * 26, -20), (358 + k * 26, -15), (336 + k * 26, -15)], 2.0, 4), c0, c1, 'polim') for k in range(2)])
        pc.append(bevel(p, 0.4, 1, 40))
    pb = solido(arred([(245, -7), (305, -7), (305, 7), (245, 7)], 1.6, 4), -36.5, -28.0, 'polim', plane='uw')
    cut(pb, [solido(arred([(251 + k * 26, -2.2), (273 + k * 26, -2.2), (273 + k * 26, 2.2), (251 + k * 26, 2.2)], 2.0, 4), -50, -35.0, 'polim', plane='uw') for k in range(2)])
    pc.append(bevel(pb, 0.4, 1, 40))
    parte('placas', pc, origem=(300, -20, 0), grupo='B', suave=40)
    return f


def montar():
    receptor()
    cano()
    ferrolho()
    gatilho()
    carregador()
    if CACA:
        coronha_caca()
    else:
        chassi()
        guarda_mao()
        coronha_precisao()
