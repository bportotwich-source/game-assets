"""Fuzil Brasa 7,62 no nível de detalhe da M4A1: receptor estampado com rebites, tampa nervurada,
transportador com alavanca de manejo, seletor de alavanca, alça tangente, bloco de gás, torre da
massa com orelhas, vareta de limpeza e carregador curvo de aço.

A coronha, o guarda-mão e o freio de boca são acessórios (como no Brasa antigo, arma06_ak.py) e
saem daqui também: coronha_madeira(), guarda_mao_madeira() e freio().

Desenho próprio, sem marcas de fabricante. Mesmas medidas e pontos do fuzil antigo, para os
encaixes, os outros acessórios e as animações continuarem valendo. O que mudou de propósito:
a alavanca do seletor é mais curta (não sai mais para baixo do receptor no modo semi), a tampa
vai até o bloco da alça e a alça de mira deita sobre um bloco mais alto.

Coordenadas em mm (lib.py da M4A1): u = para a frente, v = para cima (0 no eixo do cano),
w = direita. u é o x do fuzil antigo e v é o y antigo + 6.
"""
import math, os
import bpy, bmesh
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
from lib import *
from lib import _obj

# ------------------------------------------------------------------ medidas
KX0, KX1 = -75.0, 165.0            # receptor: trás e munhão
KB, KT = -24.0, 12.0               # fundo e borda de cima do receptor
KW = 13.0                          # meia largura do receptor
TOPO = 32.0                        # topo da tampa
XM = 585.0                         # boca do cano
CAR_U, CAR_V = 92.0, -24.0         # topo do carregador (centro)
V_GAS = 24.0                       # eixo do tubo de gás
V_MIRA = 42.5                      # ponta da massa = fundo do entalhe da alça
DU_CABO, DV_CABO = 6.0, 26.5       # o punho arredondado da Mutirão no lugar do punho deste fuzil
VARIANTE = os.environ.get('VARIANTE', '')       # 'tatico' (fuzil preto e usado) ou 'gasto' (acessórios usados)
USADO = VARIANTE in ('tatico', 'gasto')
ACO = 'aco_brasa_gasto' if USADO else 'aco_brasa'
POLIM = 'polim_gasto' if USADO else 'polim'
ANOD = 'anod_gasto' if USADO else 'anod'
MADEIRA = 'madeira_brasa'
PIC = [(7.85, 0), (10.6, -2.75), (7.9, -5.5), (-7.9, -5.5), (-10.6, -2.75), (-7.85, 0)]   # perfil do trilho (x, y a partir da face de fora)


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


def corpo_u(perfil, larg, mat, e=2.5, n=120, voltas=56):
    """Corpo arredondado fatiado ao longo de u (coronha, guarda-mão): em cada u a altura vem do
    perfil e a meia largura de larg(u)."""
    b = perfil.bounds
    aneis = []
    for i in range(n + 1):
        u = (b[0] + 0.4) + ((b[2] - 0.4) - (b[0] + 0.4)) * i / n
        x = perfil.intersection(LineString([(u, -400), (u, 200)])).bounds
        pts = superelipse(larg(u), (x[3] - x[1]) / 2, n=voltas, e=e, cy=(x[1] + x[3]) / 2)
        aneis.append([P(u, v, w) for (w, v) in pts])
    return loft(aneis, mat)


def trilho_em(u0, u1, mat, f):
    """Trilho de encaixe ao longo de u; f(x, y) leva o perfil (x de lado, y = 0 na face de fora) para (w, v)."""
    t = extr([f(x, y) for (x, y) in PIC], u0, u1, mat, plane='wv')
    n = int((u1 - u0 - 6) / 10.008)
    cut(t, [extr([f(-12, -3), f(12, -3), f(12, 2.5), f(-12, 2.5)], u - 5.23, u, mat, plane='wv') for u in [u1 - 4.0 - i * 10.008 for i in range(n)]])
    return bevel(t, 0.35, 1, 40)


def rebite(u, v, s, r=2.1, h=1.2, mat=ACO, w=KW):
    """Cabeça de rebite (ou de pino) no lado s do receptor."""
    return lathe([(-0.5, r), (h * 0.55, r * 0.86), (h * 0.9, r * 0.5), (h, 0)], mat, n=14, c0=(u, v, s * w), eixo=(0, 0, s))


CABO = arred([(-36.5, -43.5), (4.5, -43.5), (3.5, -56), (-3.5, -76), (-12, -100), (-19.5, -125), (-25.5, -146), (-29.5, -153.5),
              (-72.5, -155.5), (-75.5, -148), (-66, -120), (-55.5, -88), (-46.5, -62), (-42.5, -50)], 2.5, 6)


def meia_largura(v):
    return 0.95 * (11.8 + 3.2 * smooth(-46, -70, v) + 1.2 * math.exp(-((v + 100) / 22) ** 2))


# ------------------------------------------------------------------ receptor, punho
def receptor():
    perfil = arred([(KX0, KT), (KX1, KT), (KX1, KB + 4), (KX1 - 6, KB), (KX0 + 8, KB), (KX0, KB + 8)], 2.0, 4)
    c = solido(perfil, -KW, KW, ACO)
    cortes = [box(KX0 + 5, KX1 - 22, KB + 6, KT + 10, -10.2, 10.2, ACO),                       # caixa aberta em cima
              box(CAR_U - 28.2, CAR_U + 28.2, KB - 20, KB + 14, -10.0, 10.0, ACO),             # poço do carregador
              box(38, 60, KB - 10, KB + 8, -3.6, 3.6, ACO)]                                   # fenda do gatilho
    for s in (-1, 1):                                                                         # covas estampadas acima do poço
        a, b = lados(s, KW - 1.2, KW + 5)
        cortes.append(solido(arred([(79, -19.5), (113, -19.5), (113, -8), (79, -8)], 4.0, 5), a, b, ACO))
    cortes.append(box(30, KX1 - 20, KT - 2.0, KT + 5, 9, 20, ACO))                            # rasgo da alavanca de manejo (direita)
    cut(c, cortes)
    o = [bevel(c, 0.6, 2, 34)]
    for s in (-1, 1):
        for (u, v) in ((KX1 - 21, -1), (KX1 - 8, -1), (KX1 - 21, -15), (KX1 - 8, -15),         # munhão da frente
                       (KX0 + 12, -4), (KX0 + 12, -15), (KX0 + 26, -9.5),                      # munhão de trás
                       (121, -20), (70, -20)):                                                 # reforço do poço
            o.append(rebite(u, v, s))
        for (u, v) in ((5, -12), (65, -11)):                                                   # eixos do cão e do gatilho
            o.append(lathe([(-0.5, 2.6), (0.9, 2.6), (1.3, 2.2), (1.3, 0)], 'inox', n=16, c0=(u, v, s * KW), eixo=(0, 0, s)))
    o.append(fio([(5, -12, -KW - 1.0), (20, -17, -KW - 1.0), (50, -15.5, -KW - 1.0), (65, -11, -KW - 1.0)], 0.7, 'inox', fechado=False))   # trava dos eixos
    # trilho lateral de cauda de andorinha (esquerda) para a mira lateral
    tr = extr([(-KW - 0.2, -10), (-KW - 4.6, -12.5), (-KW - 4.6, 10.5), (-KW - 0.2, 8)], 0, 86, ACO, plane='wv')
    cut(tr, [box(-5, 4, -4, 2, -KW - 6, -KW - 2.6, ACO), box(60, 66, -14, -6, -KW - 6, -KW - 2.2, ACO)])
    o.append(bevel(tr, 0.4, 1, 40))
    for u in (14, 74):
        o.append(lathe([(-0.5, 2.3), (0.7, 2.3), (1.0, 1.8), (1.0, 0)], 'inox', n=14, c0=(u, -1, -KW - 4.6), eixo=(0, 0, -1)))
    # anel de trás (onde a coronha encaixa) e guarda-mato estampado com o retém do carregador
    o.append(bevel(solido(arred([(KX0 - 6, KB + 2), (KX0 + 2, KB + 2), (KX0 + 2, KT + 9), (KX0 - 6, KT + 9)], 2.0, 4), -KW - 1.8, KW + 1.8, ACO), 0.5, 1, 40))
    fora = arred([(13, KB + 1.5), (64, KB + 1.5), (63.5, -31), (56.5, -49), (25, -51.5), (12, -42)], 4.5, 6)
    dentro = arred([(18.5, KB - 1.5), (59.5, KB - 1.5), (59, -31), (53, -45.5), (27, -48), (17, -40)], 3.5, 6)
    o.append(bevel(solido(fora.difference(dentro), -4.6, 4.6, ACO), 0.9, 2, 40))
    ret = solido(arred([(59.5, KB + 2), (64.5, KB + 2), (66.5, -41), (60.5, -47), (56.5, -44), (59, -38)], 1.2, 4), -6.5, 6.5, ACO)
    cut(ret, [box(55, 70, -44.5 + i * 2.4, -43.3 + i * 2.4, 5.4, 8, ACO) for i in range(3)] +
             [box(55, 70, -44.5 + i * 2.4, -43.3 + i * 2.4, -8, -5.4, ACO) for i in range(3)])
    o.append(bevel(ret, 0.5, 1, 40))
    o.append(cyl((62, -27, -7.2), (62, -27, 7.2), 1.6, 'inox', n=12))
    # gravações (esquerda) e marcas do seletor (direita)
    o.append(texto('BRASA 7,62', 3.0, 118, 4.2, -(KW + 0.02)))
    o.append(texto('RC 762031 · RECOMEÇO', 1.7, 118, 0.6, -(KW + 0.02)))
    if VARIANTE == 'tatico':                                                                   # riscado à faca por um sobrevivente
        o.append(texto('NÃO DESISTA', 4.6, 40, -21.5, -(KW + 0.02)))
    o.append(texto('AUTO', 2.3, 47, -7.6, KW + 0.02, lado=1))
    o.append(texto('SEMI', 2.3, 47, -19.0, KW + 0.02, lado=1))
    f = parte('receptor', o, origem=(40, -6, 0), grupo='A', suave=30)

    # punho arredondado de baquelite, quadriculado pelo relevo
    cb = CABO.bounds
    aneis, n = [], 60
    for i in range(n + 1):
        v = (cb[3] - 0.4) + ((cb[1] + 0.4) - (cb[3] - 0.4)) * i / n
        x = CABO.intersection(LineString([(-200, v), (120, v)])).bounds
        pts = superelipse((x[2] - x[0]) / 2, meia_largura(v), n=40, e=2.3, cx=(x[0] + x[2]) / 2 + DU_CABO)
        aneis.append([P(u, v + DV_CABO, w) for (u, w) in pts])
    g = bevel(loft(aneis, 'polim_brasa_grip' if VARIANTE == 'tatico' else 'baquelite_grip'), 1.2, 2, 50)
    pf = lathe([(0, 0), (0, 4.2), (1.2, 4.2), (1.8, 3.4), (1.8, 0)], 'inox', n=18, c0=(-51 + DU_CABO, -155.2 + DV_CABO, 0), eixo=(0, -1, 0))
    fenda = box(-55.5 + DU_CABO, -46.5 + DU_CABO, -158 + DV_CABO, -156.3 + DV_CABO, -0.7, 0.7, 'inox')
    cut(pf, [fenda])
    parte('punho', [g, pf], origem=(-18, -84, 0), grupo='A', suave=50)
    return f


def tampa(com_trilho=False):
    """Tampa do receptor: chapa em arco com nervuras atravessadas, janela de ejeção à direita e o
    botão do retém atrás. Vai de trás do receptor até o bloco da alça. com_trilho: no lugar das
    nervuras, um trilho de mira em cima, com a trava da frente (acessório tampa_trilho_ak)."""
    sec = Polygon([(11.3, KT - 2)] + [(11.3 * math.cos(t), 15.0 + (TOPO - 15.0) * math.sin(t)) for t in [math.pi * i / 28 for i in range(29)]]
                  + [(-11.3, KT - 2)]).buffer(0)
    X0, X1 = KX0 + 2, KX1 + 4
    t = extr(pl(sec), X0, X1, ACO, plane='wv')
    cut(t, [extr(pl(sec.buffer(-2.0, quad_segs=4)), X0 + 2.5, X1 + 5, ACO, plane='wv'),
            solido(arred([(27, KT - 4), (KX1 - 17, KT - 4), (KX1 - 17, 23.5), (37, 23.5), (27, 19)], 2.5, 4), 3.5, 30, ACO)])
    o = [bevel(t, 0.5, 2, 34)]
    if com_trilho:
        o.append(bevel(box(X0 + 4, KX1 - 24, TOPO - 5.0, TOPO + 0.2, -9.6, 9.6, ACO), 0.6, 1, 40))             # mesa do trilho
        o.append(trilho_em(X0 + 6, KX1 - 28, ANOD, lambda x, y: (x, TOPO + 5.5 + y)))
        o.append(bevel(solido(arred([(KX1 - 30, KT + 3), (KX1 - 10, KT + 3), (KX1 - 10, TOPO + 1.8), (KX1 - 30, TOPO + 1.8)], 1.8, 4), -12.9, 12.9, ACO), 0.6, 2, 40))   # trava da frente
        for s in (-1, 1):
            o.append(lathe([(-0.5, 2.6), (1.0, 2.6), (1.5, 2.0), (1.5, 0)], 'inox', n=14, c0=(KX1 - 20, KT + 12, s * 12.9), eixo=(0, 0, s)))
    u = X0 + 30
    while not com_trilho and u + 7 < X1 - 30:                                                 # nervuras estampadas
        n = extr(pl(sec.buffer(1.7, quad_segs=6)), u, u + 6, ACO, plane='wv')
        cut(n, [box(u - 2, u + 9, -10, 17.0, -30, 30, ACO)])
        o.append(bevel(n, 0.7, 2, 40))
        u += 30.0
    o.append(bevel(solido(arred([(KX0 - 5.5, 15), (KX0 + 5, 15), (KX0 + 5, 24.5), (KX0 - 5.5, 24.5)], 2.0, 4), -4.6, 4.6, 'fosf'), 0.8, 2, 40))   # botão do retém
    return parte('tampa', o, origem=(KX1 - 22, KT, 0), grupo='A', suave=34)


def ferrolho():
    """Transportador do ferrolho em aço polido, com o pistão, a cabeça do ferrolho e a alavanca de
    manejo curva para a direita. Corre 115 mm."""
    c = extr(ret_arred(-8.2, 8.2, 12.6, 28.0, 3.0, 4), 42, 152, 'aco_polido', plane='wv')
    cut(c, [solido(capsula(64, 100, 21.5, 3.6), 6.4, 12, 'aco_polido'),                       # alívio do lado direito
            box(126, 160, 10, 17.5, 4.0, 12, 'aco_polido')])                                  # rampa da janela
    o = [bevel(c, 0.6, 2, 34)]
    o.append(cyl((150, V_GAS, 0), (200, V_GAS, 0), 6.6, 'aco_polido', n=24))                  # pistão (dentro do tubo de gás)
    o.append(lathe([(96, 0), (96, 6.2), (146, 6.2), (148, 5.2), (150, 5.2), (150, 0)], 'fosf', n=24, c0=(0, 5.0, 0)))   # ferrolho
    o.append(bevel(box(138, 150, 6.5, 10.2, 4.6, 7.4, 'fosf'), 0.4, 1, 40))                    # extrator
    br = solido(arred([(111, 13.5), (125, 13.5), (125, 21.5), (111, 21.5)], 2.0, 4), 7.0, 17.0, 'aco_polido')
    o.append(bevel(br, 0.6, 2, 40))
    aneis = []                                                                                 # manopla curva (meia-lua)
    for i in range(15):
        t = i / 14
        w = 15.0 + 17.0 * t
        du = -5.0 * t * t
        dv = -3.5 * t * t
        r = 5.3 - 1.1 * t + 0.9 * math.sin(math.pi * t) * (1 - t)
        aneis.append([P(118 + du + r * 1.15 * math.cos(a), 17.5 + dv + r * 0.82 * math.sin(a), w) for a in [2 * math.pi * k / 20 for k in range(20)]])
    o.append(bevel(loft(aneis, 'aco_polido'), 0.8, 2, 50))
    return parte('ferrolho', o, origem=(0, 6, 0), grupo='B', suave=38)


def seletor():
    """Alavanca do seletor no lado direito (pivô atrás): chapa estampada com nervura e o apoio do dedo."""
    pu, pv = KX0 + 14, 4.5
    lev = unary_union([arred([(pu - 2, pv - 5), (pu + 8, pv - 7.2), (20, -2.2), (33, 0.2), (36.5, 4.2), (33, 7.4), (pu + 8, 9.2), (pu - 2, pv + 4.6)], 1.6, 4),
                       Point(pu, pv).buffer(6.2, quad_segs=6)])
    p = solido(lev, KW + 0.1, KW + 1.8, ACO)
    o = [bevel(p, 0.5, 1, 40)]
    o.append(bevel(solido(capsula(pu + 16, 14, 2.6, 1.7), KW + 1.6, KW + 3.3, ACO), 0.7, 2, 40))               # nervura
    ap = solido(arred([(25, -6.2), (34.5, -6.2), (34.5, 3.5), (25, 3.5)], 1.8, 4), KW + 0.1, KW + 6.2, ACO)     # apoio do dedo
    cut(ap, [box(20, 40, -5.0 + i * 2.3, -3.9 + i * 2.3, KW + 5.0, KW + 8, ACO) for i in range(4)])
    o.append(bevel(ap, 0.5, 1, 40))
    o.append(lathe([(0, 0), (0, 4.4), (2.4, 4.4), (3.6, 3.4), (3.6, 0)], ACO, n=20, c0=(pu, pv, KW + 1.6), eixo=(0, 0, 1)))
    o.append(box(pu - 3.2, pu + 3.2, pv - 0.6, pv + 0.6, KW + 4.6, KW + 5.25, 'tinta_preta'))
    return parte('seletor', o, origem=(pu, pv, KW - 1.2), grupo='A', suave=40)


def gatilho():
    px, py = 48.0, -20.0
    lam = LineString([(px + a, py + b) for a, b in ((1.4, -1), (-0.4, -6.5), (-1.6, -12), (-1.1, -17), (1.6, -20.4))]).buffer(1.9, quad_segs=5)
    lam = unary_union([lam, Point(px, py).buffer(3.0, 6)])
    p = solido(lam, -3.2, 3.2, 'fosf')
    bevel(p, 0.6, 2, 40)
    return parte('gatilho', [p], origem=(px, py, 0), grupo='B')


def cartucho(c0, mat='laca_verde'):
    """Cartucho 7,62: estojo cônico de aço laqueado e ponta de cobre (deitado, ponta para a frente)."""
    return [lathe([(0, 0), (0, 5.6), (1.2, 5.6), (1.6, 4.8), (2.4, 4.8), (3.0, 5.6), (30.5, 5.0), (32.5, 4.3), (38.7, 4.3), (38.7, 0)], mat, n=18, c0=c0),
            lathe([(38.4, 0), (38.4, 3.9), (43, 3.9), (50.5, 3.3), (54.5, 1.8), (56.2, 0.5), (56.3, 0)], 'cobre', n=18, c0=c0)]


def carregador(grade=False, arco=200.0, base=True, mat=None):
    """Carregador curvo de aço de 30: nervura comprida estampada de cada lado, costura atrás,
    gancho na frente, trava atrás, chapa de base e um cartucho à vista.
    grade=True: de polímero, com quadros rebaixados dos lados (o do fuzil tático).
    arco = comprimento do corpo pela curva (mm; o de 40 é mais comprido), base=False sem a chapa
    de base (torre do tambor), mat troca o material do corpo."""
    ACO = mat or (POLIM if grade else globals()['ACO'])
    R, G = 240.0, 28.0
    cx, cy = CAR_U + R, CAR_V
    fi = arco / R
    th = [math.pi + fi * i / 48 for i in range(49)]
    em = lambda r, t: (cx + r * math.cos(t), cy + r * math.sin(t))
    perfil = Polygon([em(R - G, t) for t in th] + [em(R + G, t) for t in th[::-1]]).buffer(0)
    perfil = unary_union([perfil, Polygon([(CAR_U - G, CAR_V - 1), (CAR_U + G, CAR_V - 1), (CAR_U + G, CAR_V + 11), (CAR_U - G, CAR_V + 11)])])
    c = solido(arred(perfil, 2.2, 5), -11.5, 11.5, ACO)
    cut(c, [box(CAR_U - G + 2.2, CAR_U + G - 2.2, CAR_V + 4, CAR_V + 20, -8.0, 8.0, ACO)])     # boca
    cs = []
    for s in (-1, 1):                                                                         # degrau da parte que entra no poço
        a, b = lados(s, 9.7, 14)
        cs.append(box(CAR_U - G - 2, CAR_U + G + 2, CAR_V - 1.5, CAR_V + 20, a, b, ACO))
    if grade:                                                                                 # quadros rebaixados (grade)
        nl = max(1, round(6 * arco / 200.0))
        dt = (fi - 0.10) / nl
        for s in (-1, 1):
            a, b = lados(s, 9.9, 14)
            for i in range(nl):
                for (ra, rb) in ((R - G + 4.5, R - 2.2), (R + 2.2, R + G - 4.5)):
                    tt = [math.pi + 0.07 + i * dt + 0.010 + (dt - 0.020) * k / 3 for k in range(4)]
                    q = Polygon([em(ra, t) for t in tt] + [em(rb, t) for t in tt[::-1]])
                    cs.append(solido(arred(q, 2.0, 2), a, b, ACO))
    cut(c, cs)
    o = [bevel(c, 0.7, 1 if grade else 2, 34)]
    for s in (() if grade else (-1, 1)):
        a, b = lados(s, 11.0, 13.1)
        t2 = [math.pi + 0.07 + (fi - 0.14) * i / 30 for i in range(31)]
        nerv = LineString([em(R + 6, t) for t in t2]).buffer(4.6, quad_segs=5)
        o.append(bevel(solido(nerv, a, b, ACO), 0.9, 2, 40))
        for k in range(3):                                                                    # três nervuras curtas embaixo
            t0 = math.pi + fi - 0.07 - k * 0.075
            o.append(bevel(solido(LineString([em(R - 20, t0), em(R - 6, t0)]).buffer(2.2, quad_segs=4), a, b - 0.5, ACO), 0.6, 1, 40))
    if not grade:
        costura = LineString([em(R + G, t) for t in th[2:-2]]).buffer(1.6, quad_segs=3)
        o.append(solido(costura.intersection(perfil.buffer(3)), -3.0, 3.0, ACO))
    o.append(bevel(solido(arred([(CAR_U + G - 1, CAR_V + 2), (CAR_U + G + 6, CAR_V + 2), (CAR_U + G + 6, CAR_V - 7), (CAR_U + G - 1, CAR_V - 11)], 1.2, 4),
                          -5.5, 5.5, ACO), 0.5, 1, 40))                                       # gancho da frente
    o.append(bevel(solido(arred([(CAR_U - G - 4.5, CAR_V - 4), (CAR_U - G + 1, CAR_V - 4), (CAR_U - G + 1, CAR_V - 12), (CAR_U - G - 4.5, CAR_V - 9)], 1.0, 4),
                          -5.0, 5.0, ACO), 0.5, 1, 40))                                       # dente da trava
    t = math.pi + fi
    c_, s_ = math.cos(t), math.sin(t)
    b0 = (cx + R * c_, cy + R * s_)
    d, nn = (c_, s_), (-s_, c_)                                                               # ao longo da base (para trás) e para fora (para baixo)
    pt = lambda a, b: (b0[0] + d[0] * a + nn[0] * b, b0[1] + d[1] * a + nn[1] * b)
    base_ = arred([pt(-G - 2.5, -1.5), pt(G + 2.5, -1.5), pt(G + 3.2, 4.2), pt(-G - 3.2, 4.2)], 1.5, 4)
    if base:
        o.append(bevel(solido(base_, -12.9, 12.9, ACO), 0.8, 2, 40))
    if base:
        o.append(lathe([(0, 3.2), (1.4, 3.2), (1.9, 2.4), (1.9, 0)], 'fosf', n=14, c0=(*pt(-6, 4.2), 0), eixo=(nn[0], nn[1], 0)))   # botão da base
    for s in (-1, 1):                                                                         # lábios
        a, b = lados(s, 4.6, 8.0)
        o.append(box(CAR_U - G + 3, CAR_U + G - 6, CAR_V + 7.0, CAR_V + 11.4, a, b, globals()['ACO']))
    o += cartucho((CAR_U - G + 1.5, CAR_V + 6.8, 1.2))
    return parte('carregador', o, origem=(CAR_U, CAR_V, 0), grupo='B', suave=36)


# ------------------------------------------------------------------ cano, bloco de gás, miras
def cano():
    o = [lathe([(KX1 - 2, 0), (KX1 - 2, 11.6), (KX1 + 23, 11.6), (KX1 + 25, 10.4), (KX1 + 40, 10.4), (KX1 + 40, 8.5), (420, 8.5), (425, 7.5), (XM - 15, 7.5),
                (XM - 15, 7.0), (XM - 0.6, 7.0), (XM, 6.4), (XM, 3.4), (XM - 3, 2.9), (XM - 3, 0)], 'aco_cano', n=40)]
    # anéis que seguram o guarda-mão (acessório): o de trás na frente do receptor e o da frente com a trava
    sec = Polygon(ret_arred(-18.8, 18.8, -31.0, 14.0, 5.0, 5))
    o.append(bevel(extr(ret_arred(-17.4, 17.4, -30.0, 13.0, 7.0, 6), 190, 196.5, ACO, plane='wv'), 0.7, 2, 40))
    fr = extr(pl(sec), 385, 397, ACO, plane='wv')
    cut(fr, [extr(pl(sec.buffer(-2.4, quad_segs=5)), 380, 393.5, ACO, plane='wv')])            # copo para a ponta do guarda-mão
    o.append(bevel(fr, 0.6, 2, 40))
    o.append(cyl((391, -8, 17.5), (391, -8, 23.0), 2.6, ACO, n=14))                            # eixo da trava
    o.append(bevel(solido(arred([(388, -11), (394, -11), (395, 6), (391, 9.5), (387.5, 6)], 1.2, 4), 20.2, 22.6, ACO), 0.5, 1, 40))   # alavanca da trava
    # bloco da alça de mira (sobre o munhão)
    bl = solido(arred([(KX1 + 2, 2), (KX1 + 52, 2), (KX1 + 52, 33.0), (KX1 + 42, 35.5), (KX1 + 9, 35.5), (KX1 + 2, 29)], 2.0, 4), -10.6, 10.6, ACO)
    cut(bl, [box(KX1 + 4, KX1 + 60, 31.0, 50, -6.0, 6.0, ACO)])                                # leito da folha
    o.append(bevel(bl, 0.6, 2, 34))
    for s in (-1, 1):
        o.append(lathe([(-0.5, 2.0), (0.8, 2.0), (1.1, 1.5), (1.1, 0)], 'inox', n=12, c0=(KX1 + 46, 33.2 - 3.0, s * 10.6), eixo=(0, 0, s)))   # eixo da folha
        o.append(rebite(KX1 + 12, 7, s, w=10.6))
    # folha da alça (tangente) com entalhe, cursor e marcas
    fo = solido(arred([(KX1 + 8.5, 31.2), (KX1 + 50, 31.0), (KX1 + 50, 34.2), (KX1 + 13, 36.0), (KX1 + 13, V_MIRA + 4.6), (KX1 + 8.5, V_MIRA + 4.6)], 0.5, 3),
                -5.6, 5.6, ACO)
    cut(fo, [box(KX1 + 5, KX1 + 16, V_MIRA, V_MIRA + 9, -1.25, 1.25, ACO),                     # entalhe em U
             extr([(-5.8, V_MIRA + 2.2), (-5.8, V_MIRA + 6), (-2.6, V_MIRA + 6)], KX1 + 5, KX1 + 16, ACO, plane='wv'),
             extr([(5.8, V_MIRA + 2.2), (2.6, V_MIRA + 6), (5.8, V_MIRA + 6)], KX1 + 5, KX1 + 16, ACO, plane='wv')])
    o.append(bevel(fo, 0.35, 1, 40))
    cur = box(KX1 + 24, KX1 + 30, 30.4, 35.6, -8.6, 8.6, ACO)                                  # cursor
    cut(cur, [box(KX1 + 20, KX1 + 34, 31.0, 34.0, -5.7, 5.7, ACO)])
    o.append(bevel(cur, 0.4, 1, 40))
    for s in (-1, 1):
        a, b = lados(s, 8.4, 10.4)
        bt = box(KX1 + 23.5, KX1 + 30.5, 31.2, 35.0, a, b, 'fosf')
        cut(bt, [box(KX1 + 24.4 + i * 1.6, KX1 + 25.1 + i * 1.6, 30, 36, s * 9.8 - 1, s * 9.8 + 1.5, 'fosf') for i in range(4)])
        o.append(bt)
    for i in range(8):                                                                        # marcas de distância
        u = KX1 + 33 + i * 2.0
        vt = 34.2 + (31.0 - 34.2) * 0 + (36.0 - 34.2) * (KX1 + 50 - u) / 37.0
        o.append(box(u, u + 0.45, vt - 0.3, vt + 0.03, -4.4 if i % 2 == 0 else -3.2, -1.6, 'tinta_branca'))
    # tubo de gás (o meio fica dentro do guarda-mão) e bloco de gás
    o.append(lathe([(216, 0), (216, 8.5), (384, 8.5), (384, 9.9), (389, 9.9), (389, 8.5), (406, 8.5), (406, 0)], ACO, n=32, c0=(0, V_GAS, 0)))
    bg = solido(arred([(405, -11.5), (440, -11.5), (440, 14), (428, 33.5), (411, 34.5), (405, 30)], 2.5, 4), -9.6, 9.6, ACO)
    cs = []
    for s in (-1, 1):                                                                         # alívios dos lados
        a, b = lados(s, 8.0, 14)
        cs.append(solido(arred([(410, 10.5), (436, 10.5), (431, 15.5), (410, 15.5)], 1.5, 3), a, b, ACO))
    cut(bg, cs)
    o.append(bevel(bg, 0.7, 2, 34))
    o.append(lathe([(402, 0), (402, 10.2), (414, 10.2), (416, 9.4), (416, 0)], ACO, n=32, c0=(0, V_GAS, 0)))
    o.append(lathe([(440, 9.6), (446, 9.6), (447.5, 8.6)], ACO, n=32))
    # torre da massa: colar no cano, duas orelhas, poste e tambor de regulagem
    tw = solido(arred([(525, -11), (552, -11), (552, 20), (549.5, V_MIRA + 6.5), (527.5, V_MIRA + 6.5), (525, 20)], 3.0, 5), -9.2, 9.2, ACO)
    cut(tw, [solido(arred([(530, 18), (547, 18), (547, 70), (530, 70)], 2.0, 4), -6.4, 6.4, ACO),
             cyl((538.5, V_MIRA - 0.5, -20), (538.5, V_MIRA - 0.5, 20), 5.4, ACO, n=28),       # furo das orelhas
             box(531.5, 545.5, -30, -6.0, -3.6, 3.6, ACO)])
    o.append(bevel(tw, 0.6, 2, 34))
    o.append(lathe([(521, 9.4), (525.5, 10.6), (551.5, 10.6), (556, 9.2)], ACO, n=32))
    o.append(cyl((538.5, 13, -8.0), (538.5, 13, 8.0), 4.4, ACO, n=24))                         # tambor da massa
    o.append(lathe([(18, 0), (18, 1.9), (V_MIRA - 1.2, 1.25), (V_MIRA - 0.1, 0.95), (V_MIRA, 0.6), (V_MIRA, 0)], 'fosf', n=12, c0=(538.5, 0, 0), eixo=(0, 1, 0)))
    o.append(lathe([(V_MIRA - 1.3, 1.3), (V_MIRA - 0.05, 1.0), (V_MIRA + 0.03, 0.62), (V_MIRA + 0.03, 0)], 'tinta_branca', n=12, c0=(538.5, 0, 0), eixo=(0, 1, 0)))
    # olhal da baioneta e da bandoleira, vareta de limpeza
    ol = solido(arred([(500, -17.5), (518, -17.5), (518, -6), (500, -6)], 2.0, 4), -4.6, 4.6, ACO)
    o.append(bevel(ol, 0.6, 2, 40))
    o.append(lathe([(498, 9.2), (501, 9.9), (517, 9.9), (520, 9.2)], ACO, n=32))
    o.append(cyl((509, -12.5, -9.8), (509, -12.5, 9.8), 2.0, 'inox', n=12))
    o.append(fio(caminho_arred([(503, -12.5, -8.5), (503, -12.5, -17), (503, -27, -17), (515, -27, -17), (515, -12.5, -17), (515, -12.5, -8.5)], 2.5, 4,
                               fechado=False), 1.3, ACO, fechado=False))
    o.append(cyl((398, -11.5, 0), (540, -11.5, 0), 2.5, 'fosf', n=14))
    cab = lathe([(539, 0), (539, 3.5), (547.5, 3.5), (548.5, 2.6), (548.5, 0)], 'fosf', n=16, c0=(0, -11.5, 0))
    cut(cab, [box(542, 544.4, -20, 0, -0.8, 0.8, 'fosf')])
    o.append(cab)
    o.append(texto('7,62', 2.2, 422, 4.5, -(9.62)))
    return parte('cano', o, origem=(KX1, 0, 0), grupo='B', suave=34)


# ------------------------------------------------------------------ acessórios que vêm montados
def coronha_madeira():
    """Coronha fixa de madeira laminada: chapa de encaixe no receptor, espiga de cima com dois
    parafusos, soleira de aço com a tampa do estojo de limpeza e zarelho da bandoleira embaixo.
    Origem do acessório em (KX0 - 6, 1), o encaixe_coronha do fuzil."""
    E = KX0 - 6
    perfil = arred([(E, 13), (E - 30, 13), (E - 200, 3), (E - 330, -9), (E - 339, -12.5), (E - 342, -22), (E - 342, -119), (E - 337, -129),
                    (E - 300, -124), (E - 180, -88), (E - 60, -47), (E - 10, -35), (E, -34)], 3.0, 5)
    larg = lambda u: 12.4 + 7.6 * smooth(E - 10, E - 220, u)

    def bloco(mat, u0, u1, extra=0.0):
        c = corpo_u(perfil, lambda u: larg(u) + extra, mat, e=2.4, n=64, voltas=36)
        cut(c, [box(u0, u1, -300, 100, -60, 60, mat)], op='INTERSECT')
        return c
    corpo = bloco(MADEIRA, E - 336.0, E + 5)
    o = [bevel(corpo, 1.0, 2, 34)]
    sol = bloco(ACO, E - 400, E - 336.0, 0.5)                                                  # soleira de aço
    o.append(bevel(sol, 0.8, 2, 34))
    o.append(lathe([(0, 0), (0, 7.5), (0.9, 7.5), (1.5, 6.6), (1.5, 0)], ACO, n=24, c0=(E - 341.6, -40, 0), eixo=(-1, 0, 0)))    # tampa do estojo
    o.append(cyl((E - 343.4, -40, 0), (E - 342.6, -40, 0), 2.0, 'fosf', n=12))
    for v in (-22, -110):                                                                      # parafusos da soleira
        pf = lathe([(0, 0), (0, 3.0), (0.8, 3.0), (1.2, 2.3), (1.2, 0)], 'inox', n=14, c0=(E - 341.8, v, 0), eixo=(-1, 0, 0))
        cut(pf, [box(E - 345, E - 342.3, v - 4, v + 4, -0.5, 0.5, 'inox')])
        o.append(pf)
    ch = solido(arred([(E - 7, -35.5), (E + 6, -35.5), (E + 6, 14), (E - 7, 14)], 1.5, 4), -13.4, 13.4, ACO)                     # chapa de encaixe
    o.append(bevel(ch, 0.6, 2, 40))
    aneis = []                                                                                 # espiga de cima
    for i in range(21):                                                                        # acompanha a queda da coronha
        u = E - 2 - 58.0 * i / 20
        vt = perfil.intersection(LineString([(u, -400), (u, 200)])).bounds[3]
        aneis.append([P(u, vt - 3.0, -4.4), P(u, vt + 1.7, -4.4), P(u, vt + 1.7, 4.4), P(u, vt - 3.0, 4.4)])
    o.append(bevel(loft(aneis, ACO), 0.5, 1, 40))
    for u in (E - 20, E - 46):
        vt = perfil.intersection(LineString([(u, -400), (u, 200)])).bounds[3]
        pf = lathe([(0, 0), (0, 2.9), (0.6, 2.9), (0.95, 2.2), (0.95, 0)], 'inox', n=14, c0=(u, vt + 1.6, 0), eixo=(0, 1, 0))
        cut(pf, [box(u - 4, u + 4, vt + 2.1, vt + 4, -0.5, 0.5, 'inox')])
        o.append(pf)
    # zarelho da bandoleira embaixo
    uz = E - 250
    vz = perfil.intersection(LineString([(uz, -400), (uz, 200)])).bounds[1]
    o.append(bevel(solido(arred([(uz - 16, vz - 1.6), (uz + 16, vz + 10.2), (uz + 15, vz + 13.4), (uz - 17, vz + 1.6)], 1.2, 3), -6.5, 6.5, ACO), 0.5, 1, 40))
    o.append(fio(caminho_arred([(uz - 7, vz + 2, -9), (uz - 12, vz - 13, -9), (uz - 12, vz - 13, 9), (uz - 7, vz + 2, 9)], 3.0, 4, fechado=False),
                 1.5, ACO, fechado=False))
    return parte('coronha', o, origem=(E, 1, 0), grupo='A', suave=34)


def guarda_mao_madeira():
    """Guarda-mão de madeira laminada: a telha de baixo com as barrigas de apoio da palma e a capa
    de cima em volta do tubo de gás, com as duas braçadeiras de aço. Origem em (190, 0)."""
    perfil = arred([(199, -28.5), (250, -30.5), (360, -30.5), (386, -28.5), (391, -16), (391, 12), (198, 12), (195, -16)], 4.0, 5)
    larg = lambda u: 15.6 + 3.6 * math.exp(-((u - 300) / 52) ** 2)
    b = corpo_u(perfil, larg, MADEIRA, e=3.0, n=56, voltas=40)
    cut(b, [cyl((150, 0, 0), (450, 0, 0), 9.8, MADEIRA, n=40), box(150, 450, 0, 40, -9.8, 9.8, MADEIRA),
            cyl((150, -11.5, 0), (450, -11.5, 0), 3.4, MADEIRA, n=16), box(150, 450, 11.2, 40, -40, 40, MADEIRA)])
    gs = []
    for s in (-1, 1):                                                                         # sulco dos dedos de cada lado
        aneis = []
        for i in range(25):
            u = 216 + 154.0 * i / 24
            r = 3.4 * (0.25 + 0.75 * smooth(0, 0.12, i / 24) * smooth(1, 0.88, i / 24))
            aneis.append([P(u, 3.5 + r * math.sin(a), s * (larg(u) + 1.7) + r * math.cos(a)) for a in [2 * math.pi * k / 12 for k in range(12)]])
        gs.append(loft(aneis, MADEIRA))
    cut(b, gs)
    o = [bevel(b, 0.9, 2, 34)]
    c = lathe([(206, 0), (206, 10.2), (210, 12.0), (378, 12.0), (384, 10.6), (384, 0)], MADEIRA, n=36, c0=(0, V_GAS, 0))
    cut(c, [cyl((150, V_GAS, 0), (450, V_GAS, 0), 8.9, MADEIRA, n=32), box(150, 450, -40, 18.0, -40, 40, MADEIRA)])
    o.append(bevel(c, 0.8, 2, 34))
    for (u0, u1) in ((203.5, 208.5), (380.5, 385)):                                            # braçadeiras da capa
        br = lathe([(u0, 0), (u0, 12.9), (u1, 12.9), (u1, 0)], ACO, n=44, c0=(0, V_GAS, 0))
        cut(br, [cyl((150, V_GAS, 0), (450, V_GAS, 0), 8.9, ACO, n=32), box(150, 450, -40, 17.2, -40, 40, ACO)])
        o.append(bevel(br, 0.5, 1, 40))
    return parte('guarda_mao', o, origem=(190, 0, 0), grupo='A', suave=34)


def freio():
    """Freio de boca inclinado: bocal cortado em diagonal, com os entalhes do retém atrás. Origem em (XM - 15, 0)."""
    U0 = XM - 15
    L, R = 30.0, 10.4
    c = lathe([(U0, 0), (U0, R - 1.0), (U0 + 1.0, R), (U0 + L + 6, R), (U0 + L + 6, 0)], ACO, n=40)
    cs = [cyl((U0 - 5, 0, 0), (U0 + L + 10, 0, 0), 4.6, ACO, n=24), cyl((U0 - 1, 0, 0), (U0 + 15.2, 0, 0), 7.1, ACO, n=32),
          extr([(U0 + L - 9, 14), (U0 + L + 12, 14), (U0 + L + 12, -12.5)], -15, 15, ACO)]     # corte em diagonal
    for i in range(4):                                                                        # entalhes do retém
        a = math.radians(45 + 90 * i)
        cs.append(cyl((U0 - 2, (R + 0.6) * math.cos(a), (R + 0.6) * math.sin(a)), (U0 + 4.5, (R + 0.6) * math.cos(a), (R + 0.6) * math.sin(a)), 2.0, ACO, n=12))
    cut(c, cs)
    return parte('freio', [bevel(c, 0.4, 1, 34)], origem=(U0, 0, 0), grupo='A', suave=34)


def coronha_esqueleto():
    """Coronha fixa de polímero com o miolo vazado em triângulo, apoio de rosto com ranhuras,
    soleira de borracha e passagem da bandoleira. Origem em (KX0 - 6, 1)."""
    E = KX0 - 6
    fora = arred([(E, 14), (E - 40, 14), (E - 285, 7), (E - 296, 5), (E - 298, -121), (E - 290, -129), (E - 270, -127), (E - 50, -45),
                  (E - 12, -36), (E, -35)], 2.5, 5)
    vao = arred([(E - 75, -5), (E - 262, -5), (E - 262, -97), (E - 85, -35)], 6.0, 6)
    c = solido(fora.difference(vao), -15.5, 15.5, POLIM)
    cs = [solido(arred([(E - 287, -56), (E - 273, -56), (E - 273, -37), (E - 287, -37)], 3.0, 5), -30, 30, POLIM)]      # passagem da bandoleira
    for s in (-1, 1):                                                                         # ranhuras do apoio de rosto
        a, b = lados(s, 13.9, 20)
        for i in range(7):
            u = E - 232 + i * 24.0
            cs.append(solido(capsula(u, u + 15, 4.6 + (u - (E - 232)) * 0.022, 2.0), a, b, POLIM))
    cut(c, cs)
    o = [bevel(c, 2.2, 2, 40)]
    sol = solido(arred([(E - 312, 7), (E - 296.5, 7), (E - 296.5, -131), (E - 312, -131)], 5.0, 5), -17.0, 17.0, 'borracha')
    cut(sol, [box(E - 316, E - 310.4, v, v + 3.0, -15, 15, 'borracha') for v in range(-121, 0, 8)])
    o.append(bevel(sol, 0.8, 2, 40))
    o.append(bevel(solido(arred([(E - 1, -37), (E + 6, -37), (E + 6, 12.4), (E - 1, 12.4)], 1.5, 4), -13.4, 13.4, ACO), 0.6, 2, 40))   # chapa de encaixe
    return parte('coronha', o, origem=(E, 1, 0), grupo='A', suave=34)


def guarda_mao_fendas():
    """Guarda-mão de polímero com fendas de encaixe, trilho curto embaixo e do lado direito, e
    tampa do tubo de gás com janelas e capa de metal na ponta. Origem em (190, 0)."""
    perfil = arred([(199, -28.5), (250, -30.5), (360, -30.5), (386, -28.5), (391, -16), (391, 12), (198, 12), (195, -16)], 4.0, 5)
    b = corpo_u(perfil, lambda u: 18.5, POLIM, e=3.6, n=40, voltas=40)
    cs = [cyl((150, 0, 0), (450, 0, 0), 9.8, POLIM, n=40), box(150, 450, 0, 40, -9.8, 9.8, POLIM),
          cyl((150, -11.5, 0), (450, -11.5, 0), 3.4, POLIM, n=16), box(150, 450, 11.2, 40, -40, 40, POLIM)]
    for u0 in (215, 262, 309):                                                                # fendas dos lados
        cs.append(solido(capsula(u0 + 4, u0 + 32, -12.0, 4.0), -30, 30, POLIM))
    for u0 in (215, 250):                                                                     # fendas de baixo
        cs.append(solido(capsula(u0 + 3, u0 + 25, 0.0, 3.6), -50, -20, POLIM, plane='uw'))
    cut(b, cs)
    o = [bevel(b, 0.8, 1, 34)]
    o.append(bevel(box(287, 384, -32.6, -29.0, -8.0, 8.0, ANOD), 0.5, 1, 40))                  # trilho de baixo
    o.append(trilho_em(285, 386, ANOD, lambda x, y: (x, -37.5 - y)))
    o.append(bevel(box(312, 384, -6.5, 9.5, 16.5, 19.6, ANOD), 0.5, 1, 40))                    # trilho da direita
    o.append(trilho_em(310, 386, ANOD, lambda x, y: (24.5 + y, 1.5 + x)))
    sec = Polygon(ret_arred(-12.6, 12.6, 12.4, 36.2, 6.5, 6))                                  # tampa do tubo de gás
    c = extr(pl(sec), 205, 385, POLIM, plane='wv')
    cut(c, [cyl((150, V_GAS, 0), (450, V_GAS, 0), 8.9, POLIM, n=32), box(150, 450, 0, 17.5, -8.0, 8.0, POLIM)] +
           [solido(capsula(u0 + 4, u0 + 36, 25.0, 4.0), -30, 30, POLIM) for u0 in (232, 288)])
    o.append(bevel(c, 0.8, 1, 34))
    cp = extr(pl(sec.buffer(1.6, quad_segs=6)), 372, 386, ANOD, plane='wv')                    # capa de metal da ponta
    cut(cp, [cyl((150, V_GAS, 0), (450, V_GAS, 0), 8.9, ANOD, n=32), box(150, 450, 0, 17.5, -8.0, 8.0, ANOD)])
    o.append(bevel(cp, 0.5, 1, 40))
    return parte('guarda_mao', o, origem=(190, 0, 0), grupo='A', suave=34)


def tampa_trilho():
    return tampa(com_trilho=True)


def montar():
    receptor()
    tampa()
    ferrolho()
    seletor()
    gatilho()
    carregador(grade=VARIANTE == 'tatico')
    cano()
