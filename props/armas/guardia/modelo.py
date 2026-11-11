"""Pistola Guardiã 9 mm no nível de detalhe da M4A1: pistola de serviço de ação
dupla e simples, armação de alumínio cor de areia, ferrolho aberto em cima,
cão externo de anel, alavanca de desarme no ferrolho, trilho no guarda-pó e
cano com rosca. Desenho próprio, sem marcas de fabricante.

Mesmas medidas e pontos da Guardiã antiga (arma14_guardia.py), para os encaixes,
os acessórios e as animações continuarem valendo. Coordenadas em mm (lib.py da
M4A1): u = para a frente (0 na face de trás do ferrolho), v = para cima (0 no
eixo do cano), w = para a direita.
"""
import math
from shapely.geometry import Polygon, LineString, Point, box as caixa2d
from shapely.ops import unary_union
from lib import *

# ------------------------------------------------------------------ medidas
GL = 205.0                        # comprimento do ferrolho
GY0, GY1, GW = -13.5, 16.2, 9.8   # ferrolho: base, topo, meia largura
GC0, GC1 = 64.0, 187.0            # abertura de cima do ferrolho
GR = 6.8                          # raio do cano
P_TRAVA = (19.0, 6.2)             # eixo da alavanca de desarme (no ferrolho)
P_CAO = (-7.0, -19.0)             # eixo do cão
P_GAT = (71.0, -19.5)             # pino do gatilho
AN = math.radians(17)
D = (-math.sin(AN), -math.cos(AN))        # eixo do carregador (desce e vai para trás)
N = (math.cos(AN), -math.sin(AN))         # normal (frente)
T = (20.0, -16.0)                 # topo do carregador (centro)
ML, MW, MZ = 112.0, 15.4, 8.8     # carregador: comprimento, meia largura (frente-trás), meia espessura
NUC = 11.4                        # meia largura do cabo sem as talas
TALA = 15.8                       # meia largura do cabo com as talas
FA = 9.4                          # meia largura da armação


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


def contorno_cabo():
    f = lambda t, e=0.0: ax(t, MW + 5.0 + e)
    c = lambda t, e=0.0: ax(t, -(MW + 15.8 + e))
    pts = [f(2.65), f(30), f(55, 1.2), f(80, 0.6), f(104), f(113.5, -3.5), c(113.5, -2.0),
           c(104, 1.6), c(88, 1.6), c(60), c(30), c(18.43)]
    return arred(pts, 4.0, 8)


CABO = contorno_cabo()


# ------------------------------------------------------------------ ferrolho
def ferrolho():
    sec = [(GW, GY0), (GW, 8.2), (8.9, 12.2), (6.4, 15.3), (3.4, GY1)]
    sec = sec + [(-w, v) for (w, v) in reversed(sec)]
    corpo = extr(sec, 0, GL, 'areia_aco', plane='wv')
    # nariz mais estreito e de cantos caídos
    planta = [(-2, -12), (GL - 14, -12), (GL - 3, -8.4), (GL + 2, -8.4), (GL + 2, 8.4), (GL - 3, 8.4), (GL - 14, 12), (-2, 12)]
    cut(corpo, extr(planta, GY0 - 5, GY1 + 5, 'areia_aco', plane='uw'), op='INTERSECT')
    lado = pl(arred([(0, GY0), (GL - 3, GY0), (GL, GY0 + 3), (GL, GY1 - 5), (GL - 7, GY1), (4, GY1), (0, GY1 - 4)], 1.2, 4))
    cut(corpo, extr(lado, -14, 14, 'areia_aco'), op='INTERSECT')
    aberto = pl(arred([(GC0, 40), (GC0, 10.8), (GC0 + 8, 2.8), (GC1 - 8, 2.8), (GC1, 10.8), (GC1, 40)], 2.5, 4))
    cortes = [extr(aberto, -30, 30, 'areia_aco'),
              cyl((50, 0, 0), (GL + 10, 0, 0), GR + 0.45, 'areia_aco', n=40),                 # caminho do cano
              cyl((GL - 14, -7.6, 0), (GL + 10, -7.6, 0), 3.7, 'areia_aco', n=24),            # guia da mola no nariz
              box(4, 182, GY0 - 10, -8.8, -7.0, 7.0, 'areia_aco'),                            # canal da armação
              box(-10, 2.4, -16, 7.2, -3.7, 3.7, 'areia_aco')]                                # rebaixo do cão
    # rebaixo de cima: a parede fica mais fina acima da linha do ombro
    for s in (-1, 1):
        a, b = sorted((s * 9.05, s * 14))
        cortes.append(extr([(46, -4.6), (GL + 10, -4.6), (GL + 10, 30), (38, 30), (38, 3.5)], a, b, 'areia_aco'))
    cut(corpo, cortes)
    cortes = []
    for s in (-1, 1):
        for i in range(10):                                                                   # serrilhas de trás
            u = 6.0 + i * 3.0
            a, b = sorted((s * (GW - 0.9), s * 14))
            cortes.append(extr([(u - 0.5, GY0 + 2.6), (u + 0.75, GY0 + 2.6), (u + 2.1, 11.2), (u + 0.85, 11.2)], a, b, 'areia_aco'))
        for i in range(6):                                                                    # serrilhas da frente
            u = 150.0 + i * 3.0
            a, b = sorted((s * (GW - 0.9), s * 14))
            cortes.append(extr([(u - 0.5, GY0 + 2.6), (u + 0.75, GY0 + 2.6), (u + 1.3, -5.4), (u + 0.05, -5.4)], a, b, 'areia_aco'))
    cortes.append(box(10.6, 25.4, GY1 - 2.2, GY1 + 3, -20, 20, 'areia_aco'))                  # cauda de andorinha da alça
    cortes.append(cyl((P_TRAVA[0], P_TRAVA[1], -14), (P_TRAVA[0], P_TRAVA[1], 14), 3.0, 'areia_aco', n=20))
    cortes.append(box(44, 63, 0.4, 5.2, GW - 0.7, 14, 'areia_aco'))                           # rebaixo do extrator
    cut(corpo, cortes)
    bevel(corpo, 0.45, 2, 34)
    o = [corpo]
    o.append(texto('GUARDIÃ 9', 3.6, 112, -2.9, -9.08))
    o.append(texto('CAL. 9 MM', 2.6, 126, -11.6, -9.83))
    o.append(texto('RC 310772', 2.4, 108, -2.4, 9.08, lado=1))
    f = parte('ferrolho', o, origem=(0, 0, 0), grupo='B')
    # alça de mira (entalhe em U, dois pontos brancos)
    yt = GY1 + 6.8
    alca = solido(arred([(11, GY1 - 2.0), (25, GY1 - 2.0), (25, yt - 1.6), (22.6, yt), (11.6, yt), (11, yt - 1.2)], 0.5, 3), -7.0, 7.0, 'fosf')
    cut(alca, [extr(pl(arred([(-1.7, GY1 + 3.2), (1.7, GY1 + 3.2), (1.7, yt + 4), (-1.7, yt + 4)], 0.9, 4)), 5, 30, 'fosf', plane='wv'),
               extr([(13.5, yt + 1), (26, yt + 1), (26, GY1 + 1.2)], -3.4, 3.4, 'fosf')])
    bevel(alca, 0.35, 1, 40)
    pts = [alca]
    for s in (-1, 1):
        pts.append(cyl((10.95, GY1 + 4.2, s * 4.0), (11.05, GY1 + 4.2, s * 4.0), 0.95, 'tinta_branca', n=14))
    parte('alca_mira', pts, origem=(18, GY1, 0), pai=f, grupo='B')
    # massa de mira (um ponto branco)
    massa = solido(arred([(188.5, GY1 - 1.6), (200, GY1 - 1.6), (199, GY1 + 5.2), (191.5, GY1 + 5.2)], 0.4, 3), -1.7, 1.7, 'fosf')
    bevel(massa, 0.3, 1, 40)
    parte('massa_mira', [massa, cyl((191.0, GY1 + 3.4, 0), (191.3, GY1 + 3.4, 0), 1.0, 'tinta_branca', n=14)],
          origem=(194, GY1, 0), pai=f, grupo='B')
    # extrator (direita) com o pino, e ponta do percussor
    ex = bevel(solido(arred([(45, 0.9), (62.4, 0.9), (63, 2.6), (62.4, 4.7), (45, 4.7)], 0.7, 3), GW - 0.75, GW + 0.25, 'fosf'), 0.25, 1, 40)
    parte('extrator', [ex, cyl((49, 2.8, GW - 0.2), (49, 2.8, GW + 0.45), 1.1, 'inox', n=12)], origem=(54, 2.8, GW), pai=f, grupo='B')
    parte('percussor', [cyl((2.2, 0, 0), (3.2, 0, 0), 2.4, 'fosf', n=16), cyl((1.4, 0, 0), (2.4, 0, 0), 1.5, 'inox', n=12)],
          origem=(2.4, 0, 0), pai=f, grupo='B')
    return f


def trava(pai):
    """Alavanca ambidestra de desarme do cão: tambor no ferrolho e aba estriada para trás (em cima = fogo)."""
    px, py = P_TRAVA
    aba = arred([(px - 2.4, py - 3.9), (px - 15.5, py + 2.2), (px - 17.6, py + 6.4), (px - 14.0, py + 8.0), (px + 3.2, py + 3.6), (px + 3.4, py - 1.5)], 1.3, 5)
    o = [cyl((px, py, -GW - 0.4), (px, py, GW + 0.4), 2.9, 'fosf', n=20)]
    for s in (-1, 1):
        a, b = sorted((s * (GW + 0.05), s * (GW + 2.3)))
        p = solido(aba, a, b, 'fosf')
        cortes = []
        for i in range(5):
            u = px - 15.4 + i * 2.0
            c, d = sorted((s * (GW + 1.7), s * (GW + 4)))
            cortes.append(extr([(u, py + 1.5), (u + 0.9, py + 1.5), (u + 1.9, py + 9), (u + 1.0, py + 9)], c, d, 'fosf'))
        cut(p, cortes)
        o.append(bevel(p, 0.45, 2, 40))
        o.append(cyl((px, py, s * (GW + 0.05)), (px, py, s * (GW + 2.7)), 4.4, 'fosf', n=28))
        o.append(cyl((px + 0.6, py + 0.2, s * (GW + 2.65)), (px + 0.6, py + 0.2, s * (GW + 2.78)), 1.0, 'tinta_vermelha', n=12))
    return parte('trava', o, origem=(px, py, 0), pai=pai, grupo='B')


# ------------------------------------------------------------------ cano e cão
def cano():
    prof = [(60, 4.55), (60, 7.5), (88, 7.5), (94, GR), (GL + 4, GR), (GL + 4.6, 6.3)]
    u = GL + 4.6
    while u < GL + 15.6:                                # rosca
        prof += [(u + 0.25, 6.75), (u + 0.75, 6.75), (u + 1.0, 6.3)]
        u += 1.0
    prof += [(GL + 16, 6.3), (GL + 16, 6.9), (GL + 16.6, 6.9), (GL + 17, 6.4), (GL + 17, 5.2), (GL + 16.2, 4.55)]
    tubo = lathe(prof, 'aco_cano', n=40, anel=True)
    o = [tubo]
    bloco = bevel(solido(arred([(70, -10.8), (94, -10.8), (96, -4), (68, -4)], 1.0, 3), -4.5, 4.5, 'aco_cano'), 0.4, 1, 40)
    o.append(bloco)
    o.append(bevel(box(60, 71, 3.0, 8.6, -5.6, 5.6, 'aco_cano'), 0.6, 1, 40))          # ressalto da câmara
    o.append(lathe([(61.0, 0), (61.0, 4.5), (61.6, 4.5), (61.6, 0)], 'latao', n=20))   # culote do cartucho na câmara
    c = parte('cano', o, origem=(0, 0, 0), grupo='B')
    return c


def cao():
    cx, cy = P_CAO
    perfil = arred([(cx - 4.2, cy - 6), (cx + 5.5, cy - 4), (cx + 6.8, cy + 10), (cx + 6.4, cy + 31.5), (cx + 3.4, cy + 36.6),
                    (cx - 3.6, cy + 37.4), (cx - 7.6, cy + 33.5), (cx - 7.8, cy + 27.5), (cx - 5.2, cy + 12)], 1.6, 5)
    anel = Point(cx - 0.6, cy + 30.6).buffer(2.9, 10)
    p = solido(perfil.difference(anel), -3.2, 3.2, 'fosf')
    cortes = []
    for i in range(6):                                                                 # serrilhas da espora
        v = cy + 24.5 + i * 2.1
        cortes.append(extr([(cx - 12, v), (cx - 6.9, v + 0.2), (cx - 6.9, v + 1.1), (cx - 12, v + 1.3)], -5, 5, 'fosf'))
    for s in (-1, 1):                                                                  # lados aliviados
        a, b = sorted((s * 2.3, s * 5))
        cortes.append(solido(arred([(cx - 3.2, cy - 1), (cx + 4.4, cy), (cx + 4.8, cy + 22), (cx - 4.0, cy + 22)], 1.2, 3), a, b, 'fosf'))
    cut(p, cortes)
    bevel(p, 0.5, 2, 40)
    return parte('cao', [p, cyl((cx, cy, -3.5), (cx, cy, 3.5), 2.2, 'inox', n=16)], origem=(cx, cy, 0), grupo='B')


# ------------------------------------------------------------------ armação
def _perfil_car(folga=0.0, extra=0.0):
    a, b = ax(0, -MW), ax(0, MW)
    c, d = ax(ML + extra, MW), ax(ML + extra, -MW)
    g = Polygon([a, b, c, d])
    return g.buffer(folga, join_style=2) if folga else g


def armacao():
    alto = arred([(-14.8, -4.5), (-1.5, -4.5), (-1.5, -13.4), (189.5, -13.4), (192.5, -16), (192.5, -26.5), (188.5, -30.5),
                  (100.5, -30.5), (100.5, -34.5), (44, -34.5), (38, -30), (-10.5, -30), (-18.5, -23.5), (-21.5, -17.0),
                  (-19.6, -11.6)], 1.2, 4)
    ch = solido(alto, -FA, FA, 'areia_al')
    cortes = [box(-16.5, 0.6, -27, 10, -3.6, 3.6, 'areia_al'),                 # janela do cão
              box(62, 82, -40, -16, -3.3, 3.3, 'areia_al'),                    # fenda do gatilho
              box(2, 186, -22, -12, -6.0, 6.0, 'areia_al')]                    # canal da mola
    for s in (-1, 1):                                                          # guarda-pó mais fino que a caixa do gatilho
        a, b = sorted((s * 8.7, s * 14))
        cortes.append(extr([(112, -14.6), (200, -14.6), (200, -29.4), (120, -29.4)], a, b, 'areia_al'))
    cut(ch, cortes)
    planta = [(-30, -5.4), (-19, -6.6), (-4, FA + 1), (210, FA + 1), (210, -FA - 1), (-4, -FA - 1), (-19, 6.6), (-30, 5.4)]
    cut(ch, extr(planta[::-1], -60, 10, 'areia_al', plane='uw'), op='INTERSECT')       # cauda mais estreita atrás
    bevel(ch, 0.6, 2, 34)
    o = [ch]
    # guarda-mato e a raiz dele no cabo
    fora = arred([(40, -33), (100.5, -33), (104.8, -36.5), (103.8, -47.5), (98.5, -53), (60, -53), (40, -51.2), (26, -46), (28, -34)], 2.8, 6)
    dentro = arred([(50, -34.2), (96.4, -34.2), (97.6, -46.0), (93.5, -48.8), (62, -48.8), (51.5, -44.5), (47, -38.5)], 3.4, 6)
    o.append(bevel(solido(fora.difference(dentro), -5.3, 5.3, 'areia_al'), 1.5, 3, 40))
    o.append(bevel(solido(arred([(98.2, -53), (104.2, -53), (104.2, -50.2), (98.2, -50.2)], 0.8, 3), -5.3, 5.3, 'areia_al'), 0.5, 1, 40))
    raiz = arred([(27, -31), (49, -31), (51, -38), (46.5, -46.5), (30.5, -48.5), (24, -40)], 2.5, 5)
    o.append(bevel(solido(raiz, -FA, FA, 'areia_al'), 1.0, 2, 40))
    # cabo: núcleo da armação com o poço do carregador
    nuc = solido(CABO, -NUC, NUC, 'areia_al')
    cortes = [solido(_perfil_car(0.5), -MZ - 0.4, MZ + 0.4, 'areia_al'),
              solido(Polygon([ax(ML - 8, -MW - 1.5), ax(ML - 8, MW + 1.5), ax(ML + 6, MW + 3), ax(ML + 6, -MW - 3)]), -MZ - 1.4, MZ + 1.4, 'areia_al')]
    for i in range(30):                                                         # estrias da frente do cabo
        t = 30.0 + i * 2.5
        a, b, c, d = ax(t, MW + 4.45), ax(t, MW + 9), ax(t + 1.0, MW + 9), ax(t + 1.0, MW + 4.45)
        cortes.append(extr([a, b, c, d], -5.6, 5.6, 'areia_al'))
    for i in range(28):                                                         # estrias das costas
        t = 34.0 + i * 2.5
        a, b, c, d = ax(t, -MW - 15.25), ax(t, -MW - 20), ax(t + 1.0, -MW - 20), ax(t + 1.0, -MW - 15.25)
        cortes.append(extr([d, c, b, a], -5.2, 5.2, 'areia_al'))
    cut(nuc, cortes)
    bevel(nuc, 3.2, 4, 50)
    o.append(nuc)
    # trilho do guarda-pó (3 fendas)
    sec = [(-6.6, 0), (6.6, 0), (6.6, -1.4), (9.5, -2.9), (9.5, -4.5), (8.5, -5.5), (-8.5, -5.5), (-9.5, -4.5), (-9.5, -2.9), (-6.6, -1.4)]
    tr = extr([(w, v - 30.4) for (w, v) in sec], 125, 186, 'areia_al', plane='wv')
    cut(tr, [box(u - 2.65, u + 2.65, -40, -33.2, -12, 12, 'areia_al') for u in (145.5, 155.5, 165.5)])
    o.append(bevel(tr, 0.35, 1, 40))
    # olhal do cordão no pé do cabo
    b0 = ax(ML, -(MW + 9.5))
    olhal = Point(b0[0] - 1.0, b0[1] + 1.5).buffer(4.3, 8).difference(Point(b0[0] - 1.0, b0[1] + 1.5).buffer(2.3, 8))
    o.append(bevel(solido(olhal, -2.6, 2.6, 'fosf'), 0.5, 1, 40))
    o.append(texto('RC 310772', 2.3, 150, -23.6, 8.73, lado=1))
    o.append(texto('FEITA NO RECOMEÇO', 1.9, 152, -18.6, -8.73))
    f = parte('armacao', o, origem=(60, -25, 0), grupo='A')
    # pinos (dos dois lados)
    pinos = []
    for (u, v, r) in ((P_GAT[0], P_GAT[1], 1.5), (P_CAO[0], P_CAO[1], 1.7), (-12, -24.5, 1.3), (52, -17, 1.3), (20, -22, 1.2)):
        pinos.append(cyl((u, v, -FA - 0.25), (u, v, FA + 0.25), r, 'inox', n=14))
    parte('pinos', pinos, pai=f, grupo='A')
    # alavanca de desmontagem (esquerda) e o botão dela (direita)
    al = [cyl((83, -20.5, -FA - 1.3), (83, -20.5, -FA + 0.2), 5.6, 'fosf', n=28),
          bevel(solido(arred([(79, -29.4), (98, -28.8), (98.6, -25.2), (80, -23.2)], 1.4, 4), -FA - 1.6, -FA + 0.2, 'fosf'), 0.4, 2, 40)]
    for i in range(4):
        u = 90.0 + i * 2.0
        al.append(box(u, u + 0.9, -28.6, -25.2, -FA - 2.0, -FA - 1.5, 'fosf'))
    parte('alavanca_desmontagem', al, origem=(83, -20.5, -FA), pai=f, grupo='A')
    parte('botao_desmontagem', [cyl((83, -20.5, FA - 0.2), (83, -20.5, FA + 0.9), 2.5, 'fosf', n=18, lobes=0.12)],
          origem=(83, -20.5, FA), pai=f, grupo='A')
    # retém do carregador: botão redondo estriado (esquerda) e a cabeça do eixo (direita)
    bt = cyl((39.5, -40.2, -FA - 2.0), (39.5, -40.2, -FA + 0.3), 3.9, 'fosf', n=24)
    cut(bt, [box(39.5 - 4.5 + i * 1.5, 39.5 - 3.9 + i * 1.5, -46, -34, -FA - 3, -FA - 1.6, 'fosf') for i in range(6)])
    parte('retem_carregador', [bevel(bt, 0.3, 1, 40), cyl((39.5, -40.2, FA - 0.3), (39.5, -40.2, FA + 0.6), 2.4, 'fosf', n=16)],
          origem=(39.5, -40.2, 0), pai=f, grupo='A')
    return f


def talas():
    """Talas de polímero que abraçam o cabo: borda lisa e abaulada, quadriculado no meio (no relevo da textura), dois parafusos de fenda."""
    forma = arred(CABO.buffer(-2.6).intersection(caixa2d(-80, -140, 60, -33.5)), 3.2, 8)
    o = []
    for s, nome in ((-1, 'tala_esquerda'), (1, 'tala_direita')):
        a, b = sorted((s * (NUC - 1.5), s * TALA))
        p = solido(forma, a, b, 'polim_areia_grip')
        bevel(p, 2.6, 4, 50)
        o.append(parte(nome, [p], origem=(0, -75, s * NUC), grupo='A', suave=50))
    par = []
    for (u, v) in ((6.4, -46.5), (-13.8, -111.0)):
        for s in (-1, 1):
            c = cyl((u, v, s * (TALA - 0.9)), (u, v, s * (TALA + 0.35)), 2.7, 'fosf', n=20)
            a, b = sorted((s * (TALA - 0.1), s * (TALA + 2)))
            cut(c, box(u - 3.2, u + 3.2, v - 0.4, v + 0.4, a, b, 'fosf'))
            par.append(bevel(c, 0.3, 1, 40))
            par.append(cyl((u, v, s * (TALA - 1.4)), (u, v, s * (TALA - 0.5)), 3.6, 'polim_areia', n=20))
    parte('parafusos_talas', par, pai=o[0], grupo='A')
    return o


# ------------------------------------------------------------------ gatilho, retém, carregador
def gatilho():
    px, py = P_GAT
    d = [(1.0, -0.5), (-1.0, -7.0), (-2.2, -14.0), (-1.6, -20.5), (1.6, -24.8)]
    lam = LineString([(px + a, py + b) for a, b in d]).buffer(1.9, quad_segs=5)
    lam = unary_union([lam, Point(px, py).buffer(3.4, 6)])
    p = solido(lam, -3.1, 3.1, 'fosf')
    cortes = []
    for i in range(7):                                             # estrias da face (ponta para a frente)
        v = py - 8.0 - i * 2.1
        cortes.append(box(px - 6, px - 2.6 + 0.25 * abs(3 - i), v, v + 0.8, -2.3, 2.3, 'fosf'))
    cut(p, cortes)
    bevel(p, 0.6, 2, 40)
    return parte('gatilho', [p, cyl((px, py, -3.4), (px, py, 3.4), 1.6, 'inox', n=14)], origem=(px, py, 0), grupo='A')


def retem():
    """Retém do ferrolho (esquerda): alavanca comprida sobre o cabo com apoio estriado para o polegar."""
    lev = arred([(24, -19.4), (60, -18.4), (63.5, -15.6), (58, -13.9), (37, -14.3), (31, -12.2), (23.4, -13.6)], 0.9, 4)
    p = solido(lev, -FA - 1.5, -FA + 0.1, 'fosf')
    apoio = solido(arred([(23.8, -18.9), (35, -18.4), (35.5, -13.6), (31, -12.6), (24, -13.9)], 0.8, 3), -FA - 2.5, -FA - 1.0, 'fosf')
    cut(apoio, [box(25.2 + i * 1.9, 26.1 + i * 1.9, -20, -11, -FA - 4, -FA - 2.0, 'fosf') for i in range(5)])
    return parte('retem', [bevel(p, 0.35, 1, 40), bevel(apoio, 0.3, 1, 40), cyl((56, -16.2, -FA - 1.7), (56, -16.2, -FA + 0.1), 1.6, 'inox', n=12)],
                 origem=(24, -13.8, 0), grupo='B')


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
    for i in range(5):                                             # furos de contagem (atrás, dos dois lados)
        c = ax(26 + i * 16.5, -9.6)
        cortes.append(cyl((c[0], c[1], -20), (c[0], c[1], 20), 1.5, 'fosf', n=12))
    cut(corpo, cortes)
    bevel(corpo, 0.5, 2, 40)
    o = [corpo]
    for s in (-1, 1):
        a, b = sorted((s * MZ, s * (MZ + 0.35)))
        o.append(bevel(solido(Polygon([ax(22, 2.6), ax(22, 6.4), ax(100, 6.4), ax(100, 2.6)]).buffer(-0.2).buffer(1.0, quad_segs=3), a, b, 'fosf'), 0.3, 1, 30))
    o.append(solido(Polygon([ax(10.5, -MW + 1.3), ax(8.0, MW - 1.3), ax(13, MW - 1.3), ax(15, -MW + 1.3)]), -MZ + 1.0, MZ - 1.0, 'polim'))   # transportador
    f = lambda t, n: ax(ML + t, n)
    base = arred([f(-1.0, -17.8), f(-1.0, 18.6), f(4.5, 19.6), f(7.4, 18.2), f(7.4, -17.8)], 1.5, 4)
    bp = solido(base, -12.4, 12.4, 'polim_areia')
    cut(bp, [solido(Polygon([f(5.6 + 0.0, -12 + i * 4.0), f(5.6, -10.6 + i * 4.0), f(9, -10.6 + i * 4.0), f(9, -12 + i * 4.0)]), -9, 9, 'polim_areia') for i in range(7)])
    o.append(bevel(bp, 1.4, 3, 40))
    cb = ax(4.6, -9.6)
    o += cartucho((cb[0], cb[1] + 0.2, 0), (math.cos(math.radians(-4)) * N[0] - 0.0, math.sin(math.radians(4))))
    return parte('carregador', o, origem=(T[0], T[1], 0), grupo='A')


def montar():
    f = ferrolho()
    trava(f)
    cano()
    cao()
    armacao()
    talas()
    gatilho()
    retem()
    carregador()
