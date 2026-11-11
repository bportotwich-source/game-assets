"""Rifle Pardal .22 no nível de detalhe da M4A1: ação de ferrolho pequena com trilho, cano fino
e comprido com massa de túnel, carregador rotativo de 10 e coronha inteiriça.

  (padrão)             coronha de nogueira quadriculada no punho e na telha;
  VARIANTE=sintetico   a mesma coronha em polímero preto pontilhado.

Desenho próprio, sem marcas de fabricante. Mesmas medidas e pontos do rifle antigo
(arma11_rifle22.py), para os encaixes, os acessórios (luneta, alça do cano, bocas, carregadores,
placas de fixação da telha) e as animações continuarem valendo.

Coordenadas em mm (lib.py da M4A1): u = para a frente, v = para cima (0 no eixo do cano),
w = direita.
"""
import math, os
import bpy, bmesh
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
from lib import *
from lib import _obj

# ------------------------------------------------------------------ medidas
SINT = os.environ.get('VARIANTE', '') == 'sintetico'
RR = 13.5                          # raio do receptor (tubo)
KX0, KX1 = -60.0, 110.0            # receptor: trás e frente
CB = 60.0                          # curso do ferrolho
CAR_U, CAR_V = 26.0, -12.0         # topo do carregador (centro)
XM = 580.0                         # boca do cano (fim da rosca)
P_GAT = (-22.0, -34.0)
V_TRILHO = RR + 4.5                # topo do trilho do receptor (encaixe_mira)
V_MIRA = 21.5                      # linha das miras de ferro (fundo do entalhe da alça = topo da massa)
U_MASSA = 545.0
PIC = [(7.85, 0), (10.6, -2.75), (7.9, -5.5), (-7.9, -5.5), (-10.6, -2.75), (-7.85, 0)]   # perfil do trilho (x, y a partir do topo)
METAL = 'azulado'
MAD = 'polim_pardal' if SINT else 'nogueira_pardal'


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
    """Corpo arredondado fatiado ao longo de u (coronha): em cada u a altura vem do perfil e a
    meia largura de larg(u)."""
    b = perfil.bounds
    aneis = []
    for i in range(n + 1):
        u = (b[0] + 0.4) + ((b[2] - 0.4) - (b[0] + 0.4)) * i / n
        x = perfil.intersection(LineString([(u, -400), (u, 200)])).bounds
        pts = superelipse(larg(u), (x[3] - x[1]) / 2, n=voltas, e=e, cy=(x[1] + x[3]) / 2)
        aneis.append([P(u, v, w) for (w, v) in pts])
    return loft(aneis, mat)


def r_cano(u):
    """Raio do cano (o mesmo perfil do rifle antigo: a alça do cano assenta nele)."""
    pts = [(KX1 + 30, 11.8), (KX1 + 50, 10.5), (XM - 20, 8.8)]
    if u <= pts[0][0]:
        return pts[0][1]
    for (a, ra), (b, rb) in zip(pts, pts[1:]):
        if u <= b:
            return ra + (rb - ra) * (u - a) / (b - a)
    return pts[-1][1]


# ------------------------------------------------------------------ ação: receptor, cano, ferrolho, gatilho, carregador
def receptor():
    c = lathe([(KX0, 0), (KX0, RR - 1.5), (KX0 + 1.5, RR), (KX1 - 1.5, RR), (KX1, RR - 1), (KX1, 0)], METAL, n=56)
    cut(c, [box(20, 64, -2.5, 30, 2.5, 30, METAL),                                 # janela de ejeção (direita, em cima)
            box(CAR_U - 19.6, CAR_U + 19.6, -30, -7, -9.0, 9.0, METAL),            # passagem do carregador
            box(-53, -35, -6, 6, 5, 30, METAL),                                    # entalhe da alavanca
            box(-35.5, -28, 3, 30, 5, 30, METAL),                                  # caminho da alavanca ao abrir
            box(14, 104, -6.5, 6.5, -30, -12.7, METAL),                            # plano das gravações (esquerda)
            cyl((KX0 - 10, 0, 0), (70, 0, 0), 7.7, METAL, n=36)])                  # caminho do ferrolho
    bevel(c, 0.45, 2, 34)
    o = [c, trilho(KX0 + 6, KX1 - 4, V_TRILHO, 'anod')]
    tr = bevel(solido(arred([(-58, -9), (-40, -9), (-40, -3), (-58, -3)], 1.0, 3), -(RR + 1.8), -(RR - 3), 'fosf'), 0.4, 1, 40)   # trava (esquerda, atrás)
    cut(tr, [box(-56 + i * 2.6, -54.8 + i * 2.6, -11, 0, -(RR + 3), -(RR + 0.9), 'fosf') for i in range(5)])
    o.append(tr)
    o.append(cyl((-36.5, -6, -(RR + 0.25)), (-36.5, -6, -(RR - 0.4)), 1.3, 'tinta_vermelha', n=12))
    o.append(texto('PARDAL .22', 2.6, 60, 0.6, -12.72))
    o.append(texto('FERROLHO · RECOMEÇO', 1.3, 60, -3.4, -12.72))
    o.append(texto('RC 220731', 1.5, 92, 2.6, -12.72))
    return parte('receptor', o, origem=(25, 0, 0), grupo='B', suave=30)


def cano():
    c = lathe([(KX1 - 2, 2.9), (KX1 - 2, 12.6), (KX1 + 22, 12.6), (KX1 + 30, 11.8), (KX1 + 50, 10.5), (XM - 20, 8.8), (XM - 13, 8.8),
               (XM - 12, 6.35), (XM - 0.5, 6.35), (XM, 5.6), (XM, 3.3), (XM - 2.5, 2.9)], 'aco_cano', n=48, anel=True)
    o = [c]
    # massa: rampa presa por anel, lâmina com a ponta na linha de visada e túnel de proteção
    rb = r_cano(U_MASSA)
    o.append(lathe([(U_MASSA - 8, rb - 0.5), (U_MASSA - 8, rb + 1.8), (U_MASSA + 8, rb + 1.8), (U_MASSA + 8, rb - 0.5)], METAL, n=40, anel=True))
    rampa = solido(arred([(U_MASSA - 24, rb - 1), (U_MASSA + 10, rb - 1), (U_MASSA + 10, 15.6), (U_MASSA - 9, 15.6), (U_MASSA - 22, rb + 1.5)], 0.8, 3),
                   -3.6, 3.6, METAL)
    o.append(bevel(rampa, 0.4, 1, 40))
    o.append(solido(Polygon([(U_MASSA - 1.5, 15.0), (U_MASSA + 1.5, 15.0), (U_MASSA + 0.8, V_MIRA), (U_MASSA - 0.8, V_MIRA)]), -0.8, 0.8, METAL))
    o.append(esfera((U_MASSA - 0.9, V_MIRA - 1.1, 0), 1.1, 'latao', 12))                            # conta de latão virada para o olho
    tun = lathe([(0, 5.7), (0, 6.7), (15, 6.7), (15, 5.7)], METAL, n=36, c0=(U_MASSA - 7.5, V_MIRA, 0), anel=True)
    cut(tun, [box(U_MASSA - 20, U_MASSA + 20, 0, 15.9, -3.3, 3.3, METAL)])
    o.append(bevel(tun, 0.25, 1, 40))
    return parte('cano', o, origem=(KX1, 0, 0), grupo='B', suave=35)


def ferrolho():
    """Ferrolho (gira e corre no eixo do cano): corpo polido, capa de trás com indicador de armado e
    alavanca para a direita e para baixo com bola."""
    o = [cyl((KX0 + 3, 0, 0), (67, 0, 0), 7.3, 'aco_polido', n=36)]
    o.append(bevel(box(54, 67.5, 2.5, 5.5, 6.4, 7.9, 'fosf'), 0.3, 1, 40))                                                    # extrator
    o.append(lathe([(-80, 0), (-80, 6.0), (-78.6, 7.4), (-74, 9.6), (KX0 - 0.5, 9.6), (KX0 - 0.5, 0)], 'fosf', n=36, lobes=0.0))
    o.append(cyl((-81.2, 0, 0), (-80, 0, 0), 2.3, 'tinta_vermelha', n=14))
    d = (0.0, -0.5, 0.87)
    k = math.sqrt(sum(x * x for x in d))
    d = tuple(x / k for x in d)
    p0 = (-44.0, 0.0, 5.0)
    em = lambda t: tuple(p0[i] + d[i] * t for i in range(3))
    o.append(cyl(p0, em(34), 3.0, 'aco_polido', n=18))
    o.append(bevel(box(-50, -38, -3.4, 3.4, 5, 10.2, 'aco_polido'), 0.7, 2, 40))
    o.append(esfera(em(37), 7.2, 'aco_polido', 22))
    return parte('ferrolho', o, origem=(0, 0, 0), grupo='B', suave=40)


def gatilho():
    px, py = P_GAT
    k = 0.8
    lam = LineString([(px + a * k, py + b * k) for a, b in ((1.5, -1), (-0.5, -7.5), (-1.8, -14), (-1.2, -19.8), (1.8, -23.5))]).buffer(1.7, quad_segs=5)
    lam = unary_union([lam, Point(px, py).buffer(2.8, 6)])
    p = solido(lam, -3.2, 3.2, 'fosf')
    cut(p, [box(px - 6, px - 3.0 + 0.2 * i, py - 8.6 - i * 2.0, py - 7.9 - i * 2.0, -5, 5, 'fosf') for i in range(4)])
    bevel(p, 0.5, 2, 40)
    return parte('gatilho', [p], origem=(px, py, 0), grupo='B')


def cartucho(c0, n=14):
    """Cartucho .22 de fogo circular deitado (base em c0): aro, estojo de latão e projétil cobreado."""
    return [lathe([(0, 0), (0, 3.45), (1.1, 3.45), (1.3, 2.85), (15.5, 2.85), (15.5, 0)], 'latao', n=n, c0=c0),
            lathe([(15.0, 0), (15.0, 2.8), (18.5, 2.8), (22.2, 2.3), (24.4, 1.3), (25.1, 0)], 'cobre', n=n, c0=c0)]


def carregador():
    """Carregador rotativo de 10, de polímero: caixa curta quase rente à coronha, base com pega
    estriada e um cartucho à vista em cima."""
    baixo = -44.0
    c = solido(arred([(CAR_U - 19, baixo), (CAR_U + 19, baixo), (CAR_U + 19, CAR_V), (CAR_U - 19, CAR_V)], 2.5, 4), -11.2, 11.2, 'polim')
    cut(c, [box(CAR_U - 17, CAR_U + 14, CAR_V - 8, CAR_V + 5, -4.2, 4.2, 'polim')])                # boca
    o = [bevel(c, 0.6, 2, 40)]
    base = solido(arred([(CAR_U - 20.5, baixo - 4.5), (CAR_U + 20.5, baixo - 4.5), (CAR_U + 20.5, baixo + 1.5), (CAR_U - 20.5, baixo + 1.5)], 1.8, 4),
                  -12.9, 12.9, 'polim')
    rs = []
    for s in (-1, 1):                                                                              # estrias de pega na base
        a, b = lados(s, 12.1, 14)
        rs += [box(CAR_U - 15 + i * 4.0, CAR_U - 13.2 + i * 4.0, baixo - 6, baixo + 3, a, b, 'polim') for i in range(8)]
    cut(base, rs)
    o.append(bevel(base, 0.6, 1, 40))
    o.append(cyl((CAR_U, baixo - 4.5, 0), (CAR_U, baixo - 5.4, 0), 6.0, 'polim', n=24))              # tampa do rotor
    o.append(bevel(box(CAR_U - 4.5, CAR_U + 4.5, baixo - 6.6, baixo - 5.2, -1.0, 1.0, 'polim'), 0.3, 1, 40))
    o.append(texto('10', 3.2, CAR_U + 9, baixo + 3.5, -11.22))
    o += cartucho((CAR_U - 15.5, CAR_V - 3.0, 0.0))
    return parte('carregador', o, origem=(CAR_U, CAR_V, 0), grupo='B', suave=40)


# ------------------------------------------------------------------ coronha, ferragem e placas
PERFIL = [(328, -7), (120, -1.5), (-56, -1.5), (-64, -11), (-140, -11), (-156, 3), (-300, 8), (-336, 8), (-349, 5), (-349, -106),
          (-338, -112), (-290, -103), (-170, -73), (-128, -76), (-108, -101), (-90, -98), (-66, -60), (-52, -34), (60, -33), (230, -29.5), (310, -26),
          (326, -20)]


def meia_largura(u):
    return (15.5 - 1.5 * smooth(120, 200, u) - 1.6 * smooth(250, 328, u) - 3.4 * math.exp(-((u + 95) / 40) ** 2)
            + 3.0 * smooth(-150, -260, u))


def coronha():
    """Coronha inteiriça: telha fina de ponta arredondada, punho de pistola, pente alto atrás do
    caminho do ferrolho e soleira de borracha. O quadriculado (ou pontilhado) vem do relevo."""
    perfil = arred(PERFIL, 3.0, 5)

    def bloco(mat, u0, u1):
        c = corpo_u(perfil, meia_largura, mat, e=2.4, n=170, voltas=48)
        cut(c, [box(u0, u1, -200, 100, -60, 60, mat)], op='INTERSECT')
        return c
    corpo = bloco(MAD, -338.2, 400)
    cut(corpo, [cyl((KX0 - 12, 0, 0), (KX1 + 2, 0, 0), RR + 0.4, MAD, n=56),
                cyl((KX1, 0, 0), (360, 0, 0), 12.4, MAD, n=44),                                    # canal do cano
                box(CAR_U - 19.7, CAR_U + 19.7, -200, -8, -11.8, 11.8, MAD),                       # poço do carregador
                box(-34, -11, -60, -8, -5, 5, MAD),                                                # passagem do gatilho
                box(-55, -33, -22, 10, 9, 40, MAD)])                                               # entalhe da alavanca
    sol = bloco('borracha', -400, -338.2)
    cut(sol, [box(-360, -347.2, v - 2.0, v, -18, 18, 'borracha') for v in range(0, -104, -6)])
    o = [bevel(corpo, 0.8, 2, 34), bevel(sol, 0.8, 2, 34)]
    f = parte('coronha', o, origem=(0, -40, 0), grupo='A', suave=34)

    # ferragem de baixo: guarda-mato e chapa de aço azulado, retém do carregador, pinos da bandoleira
    fora = arred([(-54, -31.5), (0, -31.5), (-2, -46), (-14, -61), (-44, -63), (-58, -50)], 5.0, 6)
    dentro = arred([(-47, -36.5), (-6, -36.5), (-8, -46), (-17, -56.5), (-41, -58), (-51, -48)], 4.0, 6)
    fe = [bevel(solido(fora.difference(dentro), -5.0, 5.0, METAL), 1.1, 3, 40)]
    ch = solido(arred([(-62, -35.6), (50, -35.0), (50, -30), (-62, -30)], 1.0, 3), -7.5, 7.5, METAL)
    cut(ch, [box(CAR_U - 19.7, CAR_U + 19.7, -60, -20, -11.8, 11.8, METAL), box(-34, -11, -60, -10, -3.6, 3.6, METAL)])
    fe.append(bevel(ch, 0.4, 1, 40))
    fe.append(bevel(solido(arred([(-4.5, -42.5), (5.2, -41.5), (5.2, -35.2), (-3.5, -35.2)], 1.0, 3), -3.4, 3.4, METAL), 0.4, 1, 40))   # retém
    for (u, v) in ((-56, -35.8), (48 - 3.5, -35.2)):                                               # parafusos da chapa
        fe.append(cyl((u, v + 2, 0), (u, v - 0.5, 0), 2.6, 'inox', n=14))
    for (u, v) in ((290, -26.2), (-300, -104.5)):
        fe.append(cyl((u, v + 3, 0), (u, v - 6.0, 0), 2.4, 'inox', n=14))
        fe.append(fio([(u + 5.0 * math.cos(2 * math.pi * i / 20), v - 10.3 + 5.0 * math.sin(2 * math.pi * i / 20), 0) for i in range(20)], 1.1, 'inox'))
    parte('ferragem', fe, origem=(0, -45, 0), grupo='B', suave=40)

    # placas de fixação pretas na telha: lanterna (direita), laser (esquerda) e empunhadura (embaixo)
    pc = []
    for s in (-1, 1):
        a, b = lados(s, 11.0, 17.5)
        p = solido(arred([(241, -22.5), (303, -22.5), (303, -8.5), (241, -8.5)], 1.6, 4), a, b, 'polim')
        c0, c1 = lados(s, 16.0, 30)
        cut(p, [solido(arred([(247 + k * 27, -18), (270 + k * 27, -18), (270 + k * 27, -13), (247 + k * 27, -13)], 2.0, 4), c0, c1, 'polim') for k in range(2)])
        pc.append(bevel(p, 0.4, 1, 40))
    pb = solido(arred([(171, -7), (233, -7), (233, 7), (171, 7)], 1.6, 4), -34.5, -27.5, 'polim', plane='uw')
    cut(pb, [solido(arred([(177 + k * 27, -2.2), (200 + k * 27, -2.2), (200 + k * 27, 2.2), (177 + k * 27, 2.2)], 2.0, 4), -50, -33.0, 'polim', plane='uw') for k in range(2)])
    pc.append(bevel(pb, 0.4, 1, 40))
    parte('placas', pc, origem=(240, -20, 0), grupo='B', suave=40)
    return f


# ------------------------------------------------------------------ acessórios que vêm no rifle
def alca_cano():
    """Alça de lâmina com entalhe em U, presa no cano por uma sela; a lâmina deita para trás.
    Origem em (180, raio do cano): o fundo do entalhe fica na linha de visada."""
    U, V0 = 180.0, 10.4
    sela = solido(arred([(U - 9, V0 - 2.0), (U + 9, V0 - 2.0), (U + 9, V0 + 1.6), (U + 3.2, V0 + 4.0), (U - 3.2, V0 + 4.0), (U - 9, V0 + 1.6)], 0.6, 3),
                  -5.6, 5.6, METAL)
    cut(sela, [cyl((U - 20, 0, 0), (U + 20, 0, 0), r_cano(U) - 0.05, METAL, n=48),
               box(U - 1.25, U + 1.25, V0 + 1.0, V0 + 6, -4.0, 4.0, METAL)])                        # fenda da lâmina
    o = [bevel(sela, 0.35, 1, 40)]
    o.append(cyl((U, V0 + 2.0, -5.9), (U, V0 + 2.0, 5.9), 1.0, 'inox', n=12))                      # eixo
    f = parte('base', o, origem=(U, V0, 0), grupo='A', suave=40)
    lam = solido(arred([(-6.6, 0.4), (6.6, 0.4), (6.6, 12.2), (5.0, 13.8), (-5.0, 13.8), (-6.6, 12.2)], 0.5, 3), U - 0.9, U + 0.9, METAL, plane='wv')
    for vv in lam.data.vertices:
        vv.co.z += (V0 + 0.6) * MM
    cut(lam, [cyl((U - 3, V_MIRA + 1.3, 0), (U + 3, V_MIRA + 1.3, 0), 1.3, METAL, n=16), box(U - 3, U + 3, V_MIRA + 1.3, V_MIRA + 6, -1.3, 1.3, METAL)])
    parte('lamina', [bevel(lam, 0.25, 1, 40)], origem=(U, V0 + 2.0, 0), grupo='A', suave=40)
    return f


def protetor_rosca():
    """Capinha recartilhada que protege a rosca da boca. Origem no começo da rosca."""
    U = XM - 12.0
    c = lathe([(0, 6.45), (0, 8.9), (11.6, 8.9), (13.0, 7.6), (13.0, 3.6), (12.0, 3.6), (12.0, 6.45)], METAL, n=48, c0=(U, 0, 0), lobes=0.045, lobe_min=7.9, anel=True)
    return parte('protetor', [c], origem=(U, 0, 0), grupo='A', suave=40)


def montar():
    receptor()
    cano()
    ferrolho()
    gatilho()
    carregador()
    coronha()
