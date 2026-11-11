"""Espingarda Mutirão 12 no nível de detalhe da M4A1: bombeamento, receptor de alumínio com
trilho, punho de pistola, tubo do carregador embaixo do cano, protetor de calor ventilado e
telha estriada com placas de fixação. Desenho próprio, sem marcas de fabricante.

VARIANTE=curta faz a de cano curto (mesmo receptor, cano, tubo, protetor e telha menores).

Mesmas medidas e pontos da Mutirão antiga (arma03_espingarda.py), para os encaixes, os
acessórios (coronhas, chokes, prolongador, lanterna) e as animações continuarem valendo.
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
CURTA = os.environ.get('VARIANTE', '') == 'curta'
RX0, RX1 = -35.0, 205.0           # receptor: trás e frente
RY0, RY1 = -47.0, 17.0            # receptor: baixo e topo
RW = 14.5                         # meia largura do receptor
RB, RA = 10.6, 9.3                # raio externo do cano e da alma (calibre 12)
TY, TR = -25.0, 12.5              # eixo e raio do tubo do carregador
XM = RX1 + (356.0 if CURTA else 508.0)        # boca do cano
XT = RX1 + (330.0 if CURTA else 400.0)        # ponta do tubo
F0 = 292.0 if CURTA else 295.0                # telha: trás
FL = 155.0 if CURTA else 180.0                # telha: comprimento
HS0, HS1 = RX1 + 40.0, XM - (130.0 if CURTA else 170.0)     # protetor de calor
P_GAT = (41.0, -50.0)
V_MIRA = RY1 + 5.5 + 11.0          # altura da linha de visada (centro do anel da alça, topo do poste da massa)
U_ALCA = RX0 + 17.0                # alça de anel, no fundo do trilho
PIC = [(7.85, 0), (10.6, -2.75), (7.9, -5.5), (-7.9, -5.5), (-10.6, -2.75), (-7.85, 0)]   # perfil do trilho (x, y a partir do topo)


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


def tubo(u0, u1, r_fora, r_dentro, mat, v=0.0, n=40):
    return lathe([(u0, r_dentro), (u0, r_fora), (u1, r_fora), (u1, r_dentro)], mat, n=n, c0=(0, v, 0), anel=True)


CABO = arred([(-36.5, -43.5), (4.5, -43.5), (3.5, -56), (-3.5, -76), (-12, -100), (-19.5, -125), (-25.5, -146), (-29.5, -153.5),
              (-72.5, -155.5), (-75.5, -148), (-66, -120), (-55.5, -88), (-46.5, -62), (-42.5, -50)], 2.5, 6)


def meia_largura(v):
    return 11.8 + 3.2 * smooth(-46, -70, v) + 1.2 * math.exp(-((v + 100) / 22) ** 2)


# ------------------------------------------------------------------ receptor
def receptor():
    M_ = 'anod'
    sec = [(RW, RY0 - 1), (RW, RY1 - 3.5), (RW - 3.5, RY1)]
    sec = sec + [(-w, v) for (w, v) in reversed(sec)]
    c = extr(sec, RX0 - 1, RX1 + 1, M_, plane='wv')
    perfil = arred([(RX0, 12), (RX0 + 5, RY1), (RX1, RY1), (RX1, -30), (RX1 - 13, RY0), (RX0, RY0)], 2.2, 4)
    cut(c, solido(perfil, -30, 30, M_), op='INTERSECT')
    pd = arred([(-24, -40), (112, -40), (112, -18.5), (108, -14.5), (-18, -14.5), (-24, -20)], 3.0, 4)
    pe = arred([(-24, -40), (170, -40), (185, -30), (185, 9), (-12, 9), (-24, 0)], 4.0, 4)
    cortes = [box(120, 200, -12.5, 11.5, 0, 30, M_),                               # janela de ejeção (direita)
              box(115, RX1 - 0.4, -12.5, 11.5, -11.5, 11.5, M_),                   # caixa do ferrolho
              box(90, 190, -60, -12.5, -11.8, 11.8, M_),                           # janela de carga (embaixo)
              solido(pd, RW - 0.9, RW + 10, M_),                                   # painel rebaixado (direita)
              solido(pe, -RW - 10, -RW + 0.9, M_),                                 # painel rebaixado (esquerda)
              cyl((RX1 - 8, 0, 0), (RX1 + 5, 0, 0), 12.9, M_, n=40),               # assento do cano
              cyl((RX1 - 12, TY, 0), (RX1 + 5, TY, 0), TR + 0.1, M_, n=40)]        # assento do tubo
    for s in (-1, 1):                                                              # canais das barras de ação
        a, b = lados(s, 10.4, 12.8)
        cortes.append(box(RX1 - 40, RX1 + 5, -21.8, -17.2, a, b, M_))
    cut(c, cortes)
    bevel(c, 0.7, 2, 34)
    o = [c]
    o.append(bevel(solido(arred([(196, -12.5), (204, -12.5), (204, 11.5), (196, 11.5)], 0.8, 3), RW - 0.2, RW + 1.4, M_), 0.3, 1, 40))    # defletor
    # tampa de trás (onde entra a coronha) com parafuso
    o.append(bevel(solido(arred([(RX0 - 1.6, -42), (RX0 + 0.4, -42), (RX0 + 0.4, 1), (RX0 - 1.6, 1)], 0.6, 3), -12.5, 12.5, 'fosf'), 0.4, 1, 40))
    o.append(texto('MUTIRÃO 12', 5.4, 44, -28.5, RW - 0.87, lado=1))
    o.append(texto('BOMBEAMENTO · RECOMEÇO', 2.4, 44, -35.5, RW - 0.87, lado=1))
    o.append(texto('CAL. 12 · CÂMARA 76 MM', 3.2, 95, -26.5, -(RW - 0.87)))
    o.append(texto('SÓ CARTUCHO 12', 2.2, 95, -32.5, -(RW - 0.87)))
    o.append(texto('RC 120558', 2.6, 150, 1.5, -(RW - 0.87)))
    # trilho de cima
    t = extr([(x, RY1 + 5.5 + y) for (x, y) in PIC], RX0 + 6, RX1 - 6, M_, plane='wv')
    cut(t, [box(u - 5.23, u, RY1 + 2.5, RY1 + 8, -12, 12, M_) for u in [192.0 - i * 10.008 for i in range(22)]])
    o.append(bevel(t, 0.35, 1, 40))
    # alça de anel em cima do trilho (a linha de visada passa pelo centro do anel, v = V_MIRA)
    ba = solido(arred([(-12.6, 18.6), (12.6, 18.6), (12.6, 24.0), (8.5, 26.5), (-8.5, 26.5), (-12.6, 24.0)], 0.8, 3), U_ALCA - 9, U_ALCA + 9, 'fosf', plane='wv')
    o.append(bevel(ba, 0.4, 1, 40))
    o.append(bevel(tubo(U_ALCA - 3.2, U_ALCA + 3.2, 9.6, 6.0, 'fosf', v=V_MIRA, n=40), 0.5, 2, 40))
    o.append(cyl((U_ALCA, 21.4, 12.4), (U_ALCA, 21.4, 14.6), 2.7, 'inox', n=14))
    # alojamento do gatilho e guarda-mato (polímero)
    cx = arred([(RX0 + 1, RY0 + 1), (88, RY0 + 1), (88, -52), (82, -56.5), (0, -56.5), (RX0 + 1, -52)], 1.5, 3)
    al = solido(cx, -12.8, 12.8, 'polim')
    cut(al, box(30, 54, -70, -45, -4.2, 4.2, 'polim'))
    o.append(bevel(al, 0.8, 2, 40))
    fora = arred([(0, -54), (84, -54), (84, -61), (72, -80), (60, -85.5), (6, -87.5), (-6, -78)], 6.0, 6)
    dentro = arred([(9, -56.5), (70, -56.5), (72, -63), (61, -77), (12, -80.5), (5, -71)], 5.5, 6)
    o.append(bevel(solido(fora.difference(dentro), -5.8, 5.8, 'polim'), 1.4, 3, 40))
    # punho de pistola, pontilhado pelo relevo
    b = CABO.bounds
    aneis, n = [], 84
    for i in range(n + 1):
        v = (b[3] - 0.4) + ((b[1] + 0.4) - (b[3] - 0.4)) * i / n
        x = CABO.intersection(LineString([(-200, v), (120, v)])).bounds
        pts = superelipse((x[2] - x[0]) / 2, meia_largura(v), n=52, e=2.3, cx=(x[0] + x[2]) / 2)
        aneis.append([P(u, v, w) for (u, w) in pts])
    o.append(bevel(loft(aneis, 'polim_esp_grip'), 1.2, 2, 50))
    pf = cyl((-51, -156.4, 0), (-51, -154.6, 0), 3.2, 'inox', n=18)                                    # parafuso da base do punho
    cut(pf, cyl((-51, -158, 0), (-51, -155.6, 0), 1.5, 'inox', n=6))
    o.append(pf)
    f = parte('receptor', o, origem=(80, -15, 0), grupo='A', suave=28)

    # pinos, trava de segurança e alavanca de destrave da telha
    pn = []
    for (u, v) in ((4, -40), (78, -40)):
        pn.append(cyl((u, v, -RW - 0.5), (u, v, RW + 0.5), 2.1, 'inox', n=16))
    pn.append(cyl((21, -51, -13.8), (21, -51, 13.8), 3.4, 'fosf', n=20))
    pn.append(lathe([(0, 2.2), (0, 3.55), (1.1, 3.55), (1.1, 2.2)], 'tinta_vermelha', n=20, c0=(21, -51, -14.3), eixo=(0, 0, 1), anel=True))
    lev = solido(arred([(60, -54.5), (85, -54.5), (90, -50.5), (85, -48), (64, -50.5)], 1.2, 3), -14.6, -12.6, 'fosf')
    cut(lev, [box(77 + i * 2.4, 78 + i * 2.4, -56, -46, -16, -14.0, 'fosf') for i in range(4)])
    pn.append(bevel(lev, 0.3, 1, 40))
    parte('pinos', pn, pai=f, grupo='A')
    return f


# ------------------------------------------------------------------ cano, tubo e protetor
def cano(pai):
    prof = [(RX1 - 6, RA), (RX1 - 6, 12.8), (RX1 + 34, 12.8), (RX1 + 50, RB), (XM - 1.5, RB), (XM, RB - 1.2), (XM, RA + 0.6), (XM - 2.0, RA)]
    o = [lathe(prof, 'aco_cano', n=48, anel=True)]
    # massa de mira: abraçadeira, rampa, poste com ponto branco e orelhas de proteção
    u0, u1 = XM - 56.0, XM - 38.0
    o.append(bevel(tubo(u0, u1, RB + 2.6, RB - 0.5, 'fosf', n=40), 0.4, 1, 40))
    ms = solido(Polygon([(u0, RB + 1.2), (u1, RB + 1.2), (u1, 22.0), (u0 + 7, 22.0), (u0, RB + 5.5)]), -9.6, 9.6, 'fosf')
    juntar = [box(u0 + 9.5, u0 + 13.0, 20.0, V_MIRA, -1.8, 1.8, 'fosf')]
    for s in (-1, 1):
        a, b = lados(s, 7.0, 9.6)
        juntar.append(solido(Polygon([(u0 + 6, 20.0), (u1, 20.0), (u1, V_MIRA + 3.5), (u0 + 13, V_MIRA + 3.5), (u0 + 6, V_MIRA - 5)]), a, b, 'fosf'))
    cut(ms, juntar, op='UNION')
    o.append(bevel(ms, 0.4, 1, 40))
    o.append(cyl((u0 + 9.5 - 0.15, V_MIRA - 2.2, 0), (u0 + 9.6, V_MIRA - 2.2, 0), 1.3, 'tinta_branca', n=14))
    # tubo do carregador, abraçadeira em 8 e olhal da bandoleira
    o.append(lathe([(RX1 - 10, 0), (RX1 - 10, TR), (XT, TR), (XT, 0)], 'aco_cano', n=48, c0=(0, TY, 0)))
    oito = unary_union([Point(0, 0).buffer(RB + 2.8, 12), Point(0, TY).buffer(TR + 1.4, 12), caixa2d(-7.5, TY, 7.5, 0)])
    ab = solido(oito, XT - 18, XT, 'fosf', plane='wv')
    cut(ab, [cyl((XT - 30, 0, 0), (XT + 10, 0, 0), RB - 0.05, 'fosf', n=40), cyl((XT - 30, TY, 0), (XT + 10, TY, 0), TR - 0.05, 'fosf', n=40)])
    o.append(bevel(ab, 0.6, 2, 40))
    for s in (-1, 1):                                                                              # parafuso da abraçadeira
        a, b = lados(s, 6.5, 8.6)
        o.append(cyl((XT - 9, TY / 2 - 1, a), (XT - 9, TY / 2 - 1, b), 2.0, 'inox', n=12))
    o.append(bevel(solido(arred([(XT - 14, TY - TR - 1), (XT - 4, TY - TR - 1), (XT - 5, TY - TR - 6), (XT - 13, TY - TR - 6)], 1.0, 3), -3.5, 3.5, 'fosf'), 0.4, 1, 40))
    cc = (XT - 9, TY - TR - 10.5)
    o.append(fio([(cc[0] + 5.2 * math.cos(2 * math.pi * i / 20), cc[1] + 5.2 * math.sin(2 * math.pi * i / 20), 0) for i in range(20)], 1.2, 'inox'))
    f = parte('cano', o, origem=(RX1, 0, 0), pai=pai, grupo='B')

    # protetor de calor ventilado em cima do cano
    R0, R1 = RB + 1.6, RB + 3.0
    arc = [(R1 * math.sin(a), R1 * math.cos(a)) for a in [math.radians(-108 + 216 * i / 28) for i in range(29)]]
    arc += [(R0 * math.sin(a), R0 * math.cos(a)) for a in [math.radians(108 - 216 * i / 28) for i in range(29)]]
    capa = extr(arc, HS0, HS1, 'fosf', plane='wv')
    furos = []
    nf = int((HS1 - HS0 - 30) / 22)
    for i in range(nf + 1):
        u = HS0 + 15 + i * (HS1 - HS0 - 30) / max(nf, 1)
        furos.append(solido(arred([(u - 7.9, 3.8), (u + 7.9, 3.8), (u + 7.9, 8.6), (u - 7.9, 8.6)], 2.3, 5), -30, 30, 'fosf'))           # lados
        if i < nf:
            furos.append(solido(arred([(u + 3.6, -1.9), (u + 18.4, -1.9), (u + 18.4, 1.9), (u + 3.6, 1.9)], 1.8, 5), 5, 30, 'fosf', plane='uw'))   # topo
    cut(capa, furos)
    o = [bevel(capa, 0.3, 1, 40)]
    for u in (HS0, HS1 - 6):                                                                       # cintas de fixação
        arc2 = [((RB + 3.6) * math.sin(a), (RB + 3.6) * math.cos(a)) for a in [math.radians(-116 + 232 * i / 28) for i in range(29)]]
        arc2 += [(RB * math.sin(a), RB * math.cos(a)) for a in [math.radians(116 - 232 * i / 28) for i in range(29)]]
        o.append(bevel(extr(arc2, u, u + 6, 'fosf', plane='wv'), 0.3, 1, 40))
        for s in (-1, 1):
            a, b = lados(s, RB + 2.5, RB + 4.6)
            o.append(cyl((u + 3, 0, a), (u + 3, 0, b), 1.5, 'inox', n=12))
    parte('protetor', o, origem=(HS0, 0, 0), pai=pai, grupo='B', suave=40)
    return f


def tampa_tubo():
    """Tampa recartilhada da ponta do tubo do carregador."""
    o = [lathe([(0, 0), (0, TR + 0.6), (1.5, TR + 1.6), (4.0, TR + 1.6), (4.0, TR + 2.1), (13.5, TR + 2.1), (13.5, TR + 1.6), (16.5, TR + 1.6),
                (20.5, TR - 0.8), (21.2, 4.5), (19.5, 4.5), (19.5, 0)], 'fosf', n=48, c0=(XT, TY, 0), lobes=0.035, lobe_min=TR + 2.0)]
    o.append(cyl((XT + 19, TY, 0), (XT + 21.4, TY, 0), 2.8, 'inox', n=16))
    return parte('tampa_tubo', o, origem=(XT, TY, 0), grupo='B')


# ------------------------------------------------------------------ telha, ferrolho, elevador, gatilho
def telha():
    """Telha (guarda-mão que bombeia): corpo arredondado em volta do tubo, anéis de pega, barras de ação
    e placas de fixação à esquerda e embaixo."""
    f1 = F0 + FL
    perfil = arred([(F0, -11.5), (f1, -11.5), (f1 + 2, -17), (f1 + 1.5, -50.5), (f1 - 7, -52.5), (f1 - 15, -46.8),
                    (F0 + 16, -46.8), (F0 + 6, -50.5), (F0 - 2, -49), (F0 - 2, -17)], 2.0, 5)
    b = perfil.bounds
    larg = lambda u: 19.8 + 1.8 * (smooth(f1 - 22, f1, u) + smooth(F0 + 22, F0, u))
    aneis, n = [], 96
    for i in range(n + 1):
        u = (b[0] + 0.4) + ((b[2] - 0.4) - (b[0] + 0.4)) * i / n
        x = perfil.intersection(LineString([(u, -200), (u, 100)])).bounds
        pts = superelipse(larg(u), (x[3] - x[1]) / 2, n=56, e=2.5, cy=(x[1] + x[3]) / 2)
        aneis.append([P(u, v, w) for (w, v) in pts])
    c = loft(aneis, 'polim')
    cortes = [cyl((F0 - 10, 0, 0), (f1 + 10, 0, 0), RB + 3.4, 'polim', n=40),                      # canal do cano
              cyl((F0 - 10, TY, 0), (f1 + 10, TY, 0), TR + 0.3, 'polim', n=40),                    # passagem do tubo
              box(F0 - 10, f1 + 10, -9, 5, -RB - 3.4, RB + 3.4, 'polim')]
    u = F0 + 29.0
    while u + 4.5 < f1 - 26:                                                                       # vãos entre os anéis de pega
        for s in (-1, 1):
            a, bb = lados(s, 18.4, 30)
            cortes.append(box(u + 4.2, u + 7.5, -44.5, -15.5, a, bb, 'polim'))
        u += 7.5
    cut(c, cortes)
    o = [bevel(c, 0.8, 2, 40)]
    for s in (-1, 1):                                                                              # barras de ação
        a, bb = lados(s, 10.6, 12.6)
        o.append(bevel(box(RX1 - 30, F0 + 10, -21.5, -17.5, a, bb, 'fosf'), 0.3, 1, 40))
    o.append(tubo(F0 - 3, F0 + 4, TR + 1.2, TR + 0.2, 'fosf', v=TY))                               # bucha da telha
    # placa de fixação à esquerda (laser) e embaixo (empunhadura)
    pe = solido(arred([(f1 - 56, -35.5), (f1 - 8, -35.5), (f1 - 8, -22.5), (f1 - 56, -22.5)], 1.6, 4), -22.5, -19.0, 'anod')
    cut(pe, [solido(arred([(f1 - 51 + k * 22, -31), (f1 - 35 + k * 22, -31), (f1 - 35 + k * 22, -27), (f1 - 51 + k * 22, -27)], 1.8, 4), -30, -21.0, 'anod') for k in range(2)])
    o.append(bevel(pe, 0.4, 1, 40))
    uc = (F0 + f1) / 2
    pb = solido(arred([(uc - 30, -6.5), (uc + 30, -6.5), (uc + 30, 6.5), (uc - 30, 6.5)], 1.6, 4), -50.0, -45.2, 'anod', plane='uw')
    cut(pb, [solido(arred([(uc - 24 + k * 26, -2), (uc - 2 + k * 26, -2), (uc - 2 + k * 26, 2), (uc - 24 + k * 26, 2)], 1.8, 4), -60, -48.4, 'anod', plane='uw') for k in range(2)])
    o.append(bevel(pb, 0.4, 1, 40))
    return parte('telha', o, origem=(F0, TY, 0), grupo='B', suave=40)


def ferrolho(pai):
    """Ferrolho (aparece pela janela de ejeção): bloco com face, unha do extrator e ranhuras."""
    b = solido(arred([(136, -12.2), (RX1 - 0.6, -12.2), (RX1 - 0.6, 11.2), (136, 11.2)], 1.5, 3), -11.2, 11.2, 'aco_polido')
    cut(b, [box(140, 188, -3.5, 3.5, 9.5, 20, 'aco_polido'),
            *[box(142, 186, v - 0.6, v + 0.6, 10.2, 20, 'aco_polido') for v in (-8.5, 7.5)]])
    ex = bevel(solido(arred([(188.5, 3), (RX1 + 0.6, 3), (RX1 + 0.6, 8.5), (188.5, 8.5)], 0.6, 3), 9.6, 11.6, 'fosf'), 0.25, 1, 40)
    return parte('ferrolho', [bevel(b, 0.5, 1, 40), ex], origem=(RX1, 0, 0), pai=pai, grupo='B')


def elevador():
    lam = solido(arred([(95, -44.6), (178, -44.6), (186, -41.5), (178, -40.5), (95, -40.8)], 0.8, 3), -10.4, 10.4, 'fosf_escuro')
    cut(lam, box(120, 165, -50, -30, -3.5, 3.5, 'fosf_escuro'))
    return parte('elevador', [bevel(lam, 0.3, 1, 40)], origem=(95, -42.5, 0), grupo='B')


def gatilho():
    """Gatilho curvo com a ponta para a frente e estrias."""
    px, py = P_GAT
    lam = LineString([(42.5, -51), (40.5, -57.5), (39.2, -64), (39.8, -69.8), (42.8, -73.5)]).buffer(1.9, quad_segs=5)
    lam = unary_union([lam, Point(px, py).buffer(3.2, 6)])
    p = solido(lam, -4.0, 4.0, 'fosf')
    cut(p, [box(36, 38.0 + 0.25 * i, -60.6 - i * 2.2, -59.8 - i * 2.2, -5, 5, 'fosf') for i in range(4)])
    bevel(p, 0.6, 2, 40)
    return parte('gatilho', [p], origem=(px, py, 0), grupo='B')


def montar():
    f = receptor()
    cano(f)
    tampa_tubo()
    t = telha()
    ferrolho(t)
    elevador()
    gatilho()
