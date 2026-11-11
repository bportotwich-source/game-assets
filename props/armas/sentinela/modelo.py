"""Pistola Sentinela 9 mm no nível de detalhe da M4A1: pistola de polímero com percussor
lançado, ferrolho de aço quadrado com chanfros largos, rebaixo de mira com tampa, punho
com cavas dos dedos e pontilhado, trilho no guarda-pó e cano com rosca. Desenho próprio,
sem marcas de fabricante.

Mesmas medidas e pontos da Sentinela antiga (gerar_armas.py), para os encaixes, os
acessórios e as animações continuarem valendo. Coordenadas em mm (lib.py da M4A1):
u = para a frente (0 na face de trás do ferrolho), v = para cima (0 no eixo do cano),
w = para a direita.
"""
import math
import bpy, bmesh
from shapely.geometry import Polygon, LineString, Point, box as caixa2d
from shapely.ops import unary_union
from lib import *
from lib import _obj

# ------------------------------------------------------------------ medidas
SL = 186.0                        # comprimento do ferrolho
Y0, Y1, W = -13.5, 17.5, 12.5     # ferrolho: base, topo, meia largura
CH = 4.2                          # chanfro de cima do ferrolho
R = 6.8                           # raio do cano
FA = 11.1                         # meia largura da armação (a ponte de mira abraça por fora)
P_GAT = (71.0, -21.5)             # pino do gatilho
AN = math.radians(17)
D = (-math.sin(AN), -math.cos(AN))        # eixo do carregador (desce e vai para trás)
N = (math.cos(AN), -math.sin(AN))         # normal (frente)
T = (21.5, -16.0)                 # topo do carregador (centro)
ML, MW, MZ = 106.0, 14.5, 8.8     # carregador: comprimento, meia largura (frente-trás), meia espessura
FUNDO = ML - 1.0                  # o pé do punho acaba aqui, medido no eixo do carregador


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


def elipsoide(c, r, mat, n=20):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=n, v_segments=n // 2, radius=1.0)
    for v in bm.verts:
        v.co = P(c[0] + v.co.y * r[0], c[1] + v.co.z * r[1], c[2] + v.co.x * r[2])
    return _obj('el', bm, mat)


def smooth(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


# contorno lateral do punho: costas retas, três cavas dos dedos na frente
def _frente_cabo():
    pts = []
    for i in range(38):
        v = -121.0 + 74.0 * i / 37
        u = 45.2 + (v + 47.0) * 0.296
        if -119.0 < v < -50.0:
            u -= 1.7 * math.sin(math.pi * (v + 50.0) / 23.0) ** 2
        pts.append((u, v))
    return pts


CABO = arred([(-12.5, -26.2), (-16.8, -44), (-23.5, -68), (-30.5, -94), (-34.5, -114), (-36.5, -124), (-33, -131), (22, -131)] +
             _frente_cabo() + [(47.8, -31), (40, -26.2)], 1.0, 6)


def meia_largura(v):
    """Meia largura do punho na altura v: abre abaixo da armação e incha no apoio da palma."""
    return FA + 3.2 * smooth(-31, -52, v) + 1.2 * math.exp(-((v + 75) / 20) ** 2) + 0.5 * smooth(-108, -120, v)


# ------------------------------------------------------------------ ferrolho
def ferrolho():
    sec = [(W - 0.6, Y0), (W, Y0 + 0.6), (W, Y1 - CH), (W - CH, Y1)]
    sec = sec + [(-w, v) for (w, v) in reversed(sec)]
    corpo = extr(sec, 0, SL, 'aco_sent', plane='wv')
    planta = [(-2, -W - 1), (SL - 22, -W - 1), (SL - 22, -W), (SL, -W + 1.8), (SL + 2, -W + 1.8),
              (SL + 2, W - 1.8), (SL, W - 1.8), (SL - 22, W), (SL - 22, W + 1), (-2, W + 1)]
    cut(corpo, extr(planta, Y0 - 5, Y1 + 5, 'aco_sent', plane='uw'), op='INTERSECT')              # nariz mais estreito
    lado = pl(arred([(0, Y0), (SL - 4, Y0), (SL, Y0 + 4), (SL, Y1 - 6), (SL - 7, Y1), (2, Y1), (0, Y1 - 2)], 0.8, 3))
    cut(corpo, extr(lado, -14, 14, 'aco_sent'), op='INTERSECT')
    cortes = [box(70, 112, 3.0, 30, -3.5, 30, 'aco_sent'),                                        # janela de ejeção (topo e direita)
              box(66, 115, -9, 16.4, -8.8, 8.8, 'aco_sent'),                                      # alojamento da câmara
              cyl((40, 0, 0), (SL + 10, 0, 0), R + 0.15, 'aco_sent', n=40),                       # caminho do cano
              cyl((SL - 14, -10.4, 0), (SL + 10, -10.4, 0), 2.7, 'aco_sent', n=24),               # guia da mola
              box(4, 180, Y0 - 10, -6.5, -8.6, 8.6, 'aco_sent'),                                  # canal da armação
              box(24, 60, Y1 - 2.2, Y1 + 10, -10.6, 10.6, 'aco_sent'),                            # rebaixo da mira de ferrolho
              box(-10, 1.2, -8.6, 7.6, -6.3, 6.3, 'aco_sent'),                                    # rebaixo da placa traseira
              box(57.5, 70.5, 3.2, 8.3, W - 0.8, 14, 'aco_sent'),                                 # rebaixo do extrator
              box(3.6, 16.9, Y1 - 1.6, Y1 + 3, -20, 20, 'aco_sent')]                              # cauda de andorinha da alça
    cut(corpo, cortes)
    cortes = []
    for s in (-1, 1):
        a, b = sorted((s * (W - 0.9), s * 14))
        for i in range(10):                                                                       # serrilhas de trás, quase em pé
            u = 6.0 + i * 3.1
            cortes.append(extr([(u - 0.65, Y0 + 3.5), (u + 0.65, Y0 + 3.5), (u + 2.6, Y1 + 1), (u + 1.3, Y1 + 1)], a, b, 'aco_sent'))
        for i in range(7):                                                                        # serrilhas da frente, deitadas
            u = 136.0 + i * 3.1
            cortes.append(extr([(u - 0.65, Y0 + 3.5), (u + 0.65, Y0 + 3.5), (u - 10.6, Y1 + 1), (u - 11.9, Y1 + 1)], a, b, 'aco_sent'))
    cut(corpo, cortes)
    bevel(corpo, 0.4, 2, 34)
    o = [corpo,
         cyl((SL - 2.2, -10.4, 0), (SL - 0.7, -10.4, 0), 2.3, 'polim', n=20),                     # ponta da guia da mola
         texto('SENTINELA 9', 3.6, 96, -1.6, -(W + 0.03)),
         texto('CAL. 9 MM', 2.4, 96, -8.2, -(W + 0.03)),
         texto('RC 208115', 2.4, 124, -3.0, W + 0.03, lado=1)]
    f = parte('ferrolho', o, origem=(0, 0, 0), grupo='B')
    # tampa do rebaixo da mira, com dois parafusos sextavados
    tp = extr([(-10.25, Y1 - 2.15), (10.25, Y1 - 2.15), (8.3, Y1 - 0.2), (-8.3, Y1 - 0.2)], 24.25, 59.75, 'aco_sent', plane='wv')
    furos = [cyl((u, Y1 - 1.0, 0), (u, Y1 + 2, 0), 2.1, 'aco_sent', n=18) for u in (31, 53)]
    cut(tp, furos)
    o = [bevel(tp, 0.3, 1, 40)]
    for u in (31, 53):
        pf = cyl((u, Y1 - 1.6, 0), (u, Y1 - 0.45, 0), 1.9, 'inox', n=18)
        cut(pf, cyl((u, Y1 - 1.0, 0), (u, Y1 + 1, 0), 0.95, 'inox', n=6))
        o.append(pf)
    parte('tampa_mira', o, origem=(42, Y1, 0), pai=f, grupo='B')
    # alça de mira (entalhe em U, dois pontos brancos)
    yt = Y1 + 6.4
    alca = solido(arred([(4, Y1 - 1.5), (16.5, Y1 - 1.5), (16.5, yt - 0.8), (15.6, yt), (5.2, yt), (4, yt - 0.9)], 0.45, 3), -7.6, 7.6, 'fosf')
    cut(alca, [extr(pl(arred([(-1.6, Y1 + 2.9), (1.6, Y1 + 2.9), (1.6, yt + 4), (-1.6, yt + 4)], 0.9, 4)), -5, 30, 'fosf', plane='wv'),
               extr([(8.5, yt + 1), (20, yt + 1), (20, Y1 + 1.0)], -3.2, 3.2, 'fosf')])
    bevel(alca, 0.35, 1, 40)
    pts = [alca]
    for s in (-1, 1):
        pts.append(cyl((3.95, Y1 + 3.9, s * 3.9), (4.05, Y1 + 3.9, s * 3.9), 0.95, 'tinta_branca', n=14))
    parte('alca_mira', pts, origem=(10, Y1, 0), pai=f, grupo='B')
    # massa de mira (um ponto branco)
    massa = solido(arred([(166, Y1 - 1.2), (178, Y1 - 1.2), (176.6, Y1 + 5.8), (169.4, Y1 + 5.8)], 0.4, 3), -1.75, 1.75, 'fosf')
    bevel(massa, 0.3, 1, 40)
    parte('massa_mira', [massa, cyl((168.3, Y1 + 3.7, 0), (168.75, Y1 + 3.7, 0), 1.05, 'tinta_branca', n=14)],
          origem=(172, Y1, 0), pai=f, grupo='B')
    # extrator (direita) e placa traseira com a ponta do percussor
    ex = bevel(solido(arred([(58, 3.6), (69.4, 3.6), (70.1, 5.6), (69.4, 7.9), (58, 7.9)], 0.7, 3), W - 0.85, W + 0.2, 'fosf'), 0.25, 1, 40)
    parte('extrator', [ex, cyl((61, 5.8, W - 0.2), (61, 5.8, W + 0.4), 1.1, 'inox', n=12)], origem=(64, 5.8, W), pai=f, grupo='B')
    pt = bevel(solido(arred([(-0.35, -8.3), (1.3, -8.3), (1.3, 7.3), (-0.35, 7.3)], 0.3, 2), -6.1, 6.1, 'polim'), 0.3, 1, 40)
    parte('placa_traseira', [pt, cyl((-0.75, 0, 0), (0.2, 0, 0), 1.6, 'inox', n=14)], origem=(0, 0, 0), pai=f, grupo='B')
    return f


# ------------------------------------------------------------------ cano
def cano():
    prof = [(62, 4.5), (62, R), (SL + 0.2, R), (SL + 0.7, 6.3)]
    u = SL + 0.7
    while u < SL + 11.2:                                # rosca
        prof += [(u + 0.25, 6.75), (u + 0.75, 6.75), (u + 1.0, 6.3)]
        u += 1.0
    prof += [(SL + 11.6, 6.3), (SL + 11.6, 6.9), (SL + 12.8, 6.9), (SL + 13.2, 6.4), (SL + 13.2, 5.2), (SL + 12.4, 4.5)]
    o = [lathe(prof, 'aco_cano', n=40, anel=True)]
    blc = box(70.2, 111.8, -6.8, 16.1, -8.5, 8.5, 'aco_cano')                                     # bloco da câmara (aparece na janela)
    cut(blc, cyl((60, 0, 0), (120, 0, 0), 4.5, 'aco_cano', n=24))
    o.append(bevel(blc, 0.5, 2, 40))
    o.append(lathe([(70.6, 0), (70.6, 4.5), (71.2, 4.5), (71.2, 0)], 'latao', n=20))              # culote do cartucho na câmara
    o.append(bevel(solido(arred([(84, -12.6), (104, -12.6), (107, -6), (80, -6)], 1.0, 3), -4.5, 4.5, 'aco_cano'), 0.4, 1, 40))
    return parte('cano', o, origem=(0, 0, 0), grupo='A')


# ------------------------------------------------------------------ armação
def _perfil_car(folga=0.0, extra=0.0):
    a, b = ax(0, -MW), ax(0, MW)
    c, d = ax(ML + extra, MW), ax(ML + extra, -MW)
    g = Polygon([a, b, c, d])
    return g.buffer(folga, join_style=2) if folga else g


def _punho(mat, folga=0.0):
    """Punho de seção arredondada: fatias horizontais do contorno, largura por meia_largura(v)."""
    aneis = []
    n = 76
    for i in range(n + 1):
        v = -26.6 - (130.6 - 26.6) * i / n
        x = CABO.intersection(LineString([(-80, v), (80, v)])).bounds
        ub, uf = x[0], x[2]
        pts = superelipse((uf - ub) / 2 + folga, meia_largura(v) + folga, n=48, e=2.5, cx=(ub + uf) / 2)
        aneis.append([P(u, v, w) for (u, w) in pts])
    return loft(aneis, mat)


def armacao():
    fora = [(-3, Y0 - 0.1), (-16, -17.2), (-22.5, -21.5), (-22.2, -25.2), (-13.5, -31), (-18, -50), (-27, -85), (-33, -112),
            (-34, -119), (-28, -123), (19, -123), (24, -118), (25, -110), (30, -100), (29, -93), (34, -83), (33, -76),
            (39, -66), (38, -58), (44, -47), (48, -44.5), (60, -50.5), (94, -51.5), (98.5, -49.5), (99.2, -46), (97.5, -34),
            (102.5, -30), (180, -30), (183, -27), (183, Y0 - 0.1)]
    perfil = arred(fora, 1.4, 4)
    vao = arred([(51, -43.5), (62, -46.5), (90, -47), (93.5, -44.5), (93.5, -33.5), (89, -26.5), (53, -26.5), (47, -34)], 2.8, 6)
    alto = perfil.intersection(caixa2d(-60, -30.4, 200, 0))
    ch = solido(alto, -FA, FA, 'pol_sent')
    cortes = [box(60, 82, -40, -12, -4.5, 4.5, 'pol_sent'),                    # fenda do gatilho
              box(2, 181, -22, -10, -8.4, 8.4, 'pol_sent')]                    # canal do ferrolho e da mola
    for s in (-1, 1):                                                          # rebaixo raso ao longo do guarda-pó
        a, b = sorted((s * (FA - 0.5), s * 14))
        cortes.append(solido(arred([(106, -27.6), (178, -27.6), (178, -17.4), (112, -17.4)], 1.4, 3), a, b, 'pol_sent'))
    cut(ch, cortes)
    planta = [(-30, -6.4), (-17, -7.6), (-3, -FA - 1), (210, -FA - 1), (210, FA + 1), (-3, FA + 1), (-17, 7.6), (-30, 6.4)]
    cut(ch, extr(planta, -60, 10, 'pol_sent', plane='uw'), op='INTERSECT')                # rabo de castor mais estreito
    bevel(ch, 0.7, 2, 34)
    o = [ch]
    # guarda-mato: frente reta com gancho, mais fino que a armação
    gm = perfil.intersection(caixa2d(42, -60, 110, -29)).difference(vao)
    g = solido(gm, -6.6, 6.6, 'pol_sent')
    cut(g, [box(98.6 - 0.14 * i * 2.0, 104, -45.2 + i * 2.0, -44.3 + i * 2.0, -8, 8, 'pol_sent') for i in range(6)])     # estrias da frente
    o.append(bevel(g, 1.6, 3, 40))
    # punho
    p = _punho('pol_sent_grip')
    pe = Polygon([ax(FUNDO, -80), ax(FUNDO, 80), ax(FUNDO + 60, 80), ax(FUNDO + 60, -80)])
    cortes = [solido(pe, -30, 30, 'pol_sent_grip'),
              solido(_perfil_car(0.6), -MZ - 0.5, MZ + 0.5, 'pol_sent_grip'),
              solido(Polygon([ax(FUNDO - 9, -MW - 1.2), ax(FUNDO - 9, MW + 1.2), ax(FUNDO + 6, MW + 3.2), ax(FUNDO + 6, -MW - 3.2)]),
                     -MZ - 1.7, MZ + 1.7, 'pol_sent_grip'),                    # boca do poço mais aberta
              box(60, 82, -40, -12, -4.5, 4.5, 'pol_sent_grip')]
    for s in (-1, 1):
        cortes.append(elipsoide((-9.5, -113.5, s * 17.0), (9, 6.5, 3.2), 'pol_sent_grip'))    # cava para puxar o carregador
    cut(p, cortes)
    bevel(p, 0.9, 2, 50)
    o.append(p)
    # trilho do guarda-pó (2 fendas)
    sec = [(-6.5, 0), (6.5, 0), (6.5, -1.5), (9.5, -3.0), (9.5, -4.5), (8.5, -5.5), (-8.5, -5.5), (-9.5, -4.5), (-9.5, -3.0), (-6.5, -1.5)]
    tr = extr([(w, v - 29.6) for (w, v) in sec], 105, 177, 'pol_sent', plane='wv')
    cut(tr, [box(u - 2.65, u + 2.65, -40, -32.4, -12, 12, 'pol_sent') for u in (128, 154)])
    o.append(bevel(tr, 0.4, 1, 40))
    # alça do cordão no pé do punho
    c = ax(FUNDO - 4.5, -MW - 9.0)
    olhal = Point(c).buffer(3.6, 8).difference(Point(c).buffer(1.7, 8))
    o.append(bevel(solido(olhal, -2.4, 2.4, 'pol_sent'), 0.5, 1, 40))
    # plaqueta de aço do número, embutida no guarda-pó (direita)
    o.append(bevel(solido(arred([(118, -26.4), (150, -26.4), (150, -21.0), (118, -21.0)], 1.0, 3), FA - 0.55, FA - 0.2, 'fosf_escuro'), 0.2, 1, 40))
    o.append(texto('RC 208115', 2.5, 134, -24.9, FA - 0.17, lado=1))
    o.append(texto('FEITA NO RECOMEÇO', 1.9, 142, -23.2, -(FA - 0.47)))
    f = parte('armacao', o, origem=(60, -25, 0), grupo='A', suave=40)
    # pinos (dos dois lados)
    pinos = [cyl((u, v, -FA - 0.2), (u, v, FA + 0.2), r, 'fosf', n=14) for (u, v, r) in ((72, -22, 1.5), (52, -20, 1.4), (-6, -22, 1.4))]
    parte('pinos', pinos, pai=f, grupo='B')
    # retém do ferrolho (esquerda): lâmina comprida com apoio estriado para o polegar
    lev = arred([(30, -20.2), (60, -19.8), (64, -17.4), (60, -15.2), (44, -15.2), (37, -14.0), (30, -14.6)], 0.8, 4)
    rf = [bevel(solido(lev, -FA - 1.25, -FA + 0.1, 'fosf'), 0.3, 1, 40)]
    ap = solido(arred([(30.4, -19.8), (41, -19.5), (41, -15.0), (37, -14.4), (30.4, -14.9)], 0.7, 3), -FA - 2.1, -FA - 0.9, 'fosf')
    cut(ap, [box(31.6 + i * 1.9, 32.5 + i * 1.9, -21, -13, -FA - 4, -FA - 1.7, 'fosf') for i in range(5)])
    rf.append(bevel(ap, 0.25, 1, 40))
    parte('retem_ferrolho', rf, origem=(58, -17.5, -FA), pai=f, grupo='B')
    # alavanca de desmontagem (dos dois lados), estriada
    al = []
    for s in (-1, 1):
        a, b = sorted((s * (FA - 0.1), s * (FA + 1.1)))
        t = solido(arred([(83, -21.2), (95, -21.2), (95, -16.8), (83, -16.8)], 1.1, 3), a, b, 'fosf')
        c, d = sorted((s * (FA + 0.6), s * (FA + 3)))
        cut(t, [box(84.6 + i * 2.4, 85.6 + i * 2.4, -23, -15, c, d, 'fosf') for i in range(4)])
        al.append(bevel(t, 0.25, 1, 40))
    parte('alavanca_desmontagem', al, origem=(89, -19, 0), pai=f, grupo='B')
    # retém do carregador: botão quadriculado dos dois lados
    bt = []
    for s in (-1, 1):
        a, b = sorted((s * 10.4, s * 13.0))
        t = solido(arred([(40.5, -41.5), (50.5, -41.5), (50.5, -32.5), (40.5, -32.5)], 1.4, 3), a, b, 'polim')
        c, d = sorted((s * 12.5, s * 15))
        cut(t, [box(41.6 + i * 1.6, 42.3 + i * 1.6, -43, -31, c, d, 'polim') for i in range(6)] +
               [box(39, 52, -40.6 + i * 1.6, -39.9 + i * 1.6, c, d, 'polim') for i in range(5)])
        bt.append(bevel(t, 0.25, 1, 40))
    parte('retem_carregador', bt, origem=(45.5, -37, 0), pai=f, grupo='A')
    return f


# ------------------------------------------------------------------ gatilho e carregador
def gatilho():
    """Gatilho curvo (ponta para a frente) com a tecla de segurança no meio."""
    px, py = P_GAT
    d = [(0.2, -2.0), (-1.8, -8.0), (-2.4, -14.0), (-1.2, -18.3), (1.8, -21.0)]
    lam = LineString([(px + a, py + b) for a, b in d]).buffer(1.9, quad_segs=5)
    lam = unary_union([lam, Point(px, py).buffer(3.2, 6)])
    p = solido(lam, -3.5, 3.5, 'polim')
    cut(p, box(px - 8, px - 1.2, py - 19.6, py - 6.4, -1.15, 1.15, 'polim'))               # fenda da tecla
    bevel(p, 0.7, 2, 40)
    tec = LineString([(px - 2.9, py - 7.2), (px - 3.6, py - 13.8), (px - 2.4, py - 18.4)]).buffer(1.15, quad_segs=4)
    return parte('gatilho', [p, bevel(solido(tec, -0.9, 0.9, 'fosf'), 0.25, 1, 40), cyl((px, py, -3.8), (px, py, 3.8), 1.5, 'fosf', n=14)],
                 origem=(px, py, 0), grupo='A')


def cartucho(base, dir_, mat_e='latao', mat_p='cobre'):
    """Cartucho 9 mm: base = centro do culote (u, v, w), dir_ = direção (u, v) da ponta."""
    e = (dir_[0], dir_[1], 0)
    est = lathe([(0, 0), (0, 4.6), (0.4, 4.95), (1.2, 4.95), (1.5, 4.5), (2.2, 4.5), (2.5, 4.95), (19.1, 4.85), (19.1, 4.45)], mat_e, n=18, c0=base, eixo=e)
    pro = lathe([(18.6, 4.48), (22.5, 4.4), (25.5, 3.7), (28.0, 2.4), (29.3, 1.0), (29.6, 0)], mat_p, n=18, c0=base, eixo=e)
    return [est, pro]


def carregador():
    """Carregador de aço de fila dupla com furos de contagem, lábios, cartucho no topo e base de polímero."""
    corpo = solido(_perfil_car(), -MZ, MZ, 'fosf')
    topo = Polygon([ax(-2, -MW - 2), ax(-2, MW + 2), ax(5.5, MW + 2), ax(9.5, -MW + 13), ax(9.5, -MW - 2)])     # boca: mais baixa na frente
    oco = Polygon([ax(-3, -MW + 1.2), ax(-3, MW - 1.2), ax(16, MW - 1.2), ax(16, -MW + 1.2)])
    cortes = [solido(topo, -20, 20, 'fosf'), solido(oco, -MZ + 0.9, MZ - 0.9, 'fosf'),
              box(T[0] - 13, T[0] + 10, T[1] - 4, T[1] + 14, -3.4, 3.4, 'fosf')]                              # entre os lábios
    for i in range(6):                                             # furos de contagem (atrás, à esquerda)
        c = ax(20 + i * 12.0, -11.8)
        cortes.append(cyl((c[0], c[1], -20), (c[0], c[1], 0), 1.2, 'fosf', n=12))
    cut(corpo, cortes)
    bevel(corpo, 0.5, 2, 40)
    o = [corpo]
    for s in (-1, 1):                                              # nervura de reforço dos dois lados
        a, b = sorted((s * MZ, s * (MZ + 0.35)))
        o.append(bevel(solido(Polygon([ax(22, 2.6), ax(22, 6.4), ax(96, 6.4), ax(96, 2.6)]).buffer(-0.2).buffer(1.0, quad_segs=3), a, b, 'fosf'), 0.3, 1, 30))
    o.append(solido(Polygon([ax(10.5, -MW + 1.3), ax(8.0, MW - 1.3), ax(13, MW - 1.3), ax(15, -MW + 1.3)]), -MZ + 1.0, MZ - 1.0, 'polim'))   # transportador
    f = lambda t, n: ax(ML + t, n)
    base = arred([f(-1.0, -16.8), f(-1.0, 18.5), f(5.5, 19.2), f(8.5, 18.5), f(8.5, -17.2)], 1.5, 4)
    bp = solido(base, -12.8, 12.8, 'polim')
    cut(bp, [solido(Polygon([f(6.6, -12 + i * 4.0), f(6.6, -10.6 + i * 4.0), f(10, -10.6 + i * 4.0), f(10, -12 + i * 4.0)]), -9, 9, 'polim') for i in range(7)])
    o.append(bevel(bp, 1.6, 3, 40))
    cb = ax(4.6, -9.6)
    o += cartucho((cb[0], cb[1] + 0.2, 0), (math.cos(math.radians(-4)) * N[0], math.sin(math.radians(4))))
    return parte('carregador', o, origem=(T[0], T[1], 0), grupo='A')


def montar():
    ferrolho()
    cano()
    armacao()
    gatilho()
    carregador()
