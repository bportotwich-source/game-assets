"""Besta recurva no nível de detalhe da M4A1: coronha esqueletada de polímero verde-oliva com
soleira de borracha e apoio de rosto, caixa do gatilho com trava de corda e segurança dos dois
lados, punho pontilhado, trilho de voo de alumínio com canaleta, guarda-mão com abas que
protegem os dedos, um trilho curto embaixo, cabeça de alumínio com bolsos e braços recurvos de
fibra, corda com reforços e virote de carbono. Desenho próprio, sem marcas.

Mesmas medidas e pontos da besta antiga (arma17_besta.py), para os nós (braços, metades da
corda, trava, gatilho, segurança, virote), os acessórios (luneta, miras rebatíveis, estribo,
lanterna ou laser no trilho curto) e as animações continuarem valendo. O modelo parado está
ARMADO e carregado.

Coordenadas em mm (lib.py da M4A1): u = para a frente, v = para cima, w = direita. A besta fica
deitada: os braços abrem para os lados (em w) no plano v = LY.
"""
import math
import numpy as np
import bpy, bmesh
from mathutils import Matrix, Vector
from shapely.geometry import Polygon, LineString, Point, box as caixa2d
from shapely.ops import unary_union
from lib import *
from lib import _obj

# ------------------------------------------------------------------ medidas (as da besta antiga)
LY = 38.5                          # plano dos braços, da corda e do centro do virote
V_TRILHO = 34.0                    # topo do trilho de voo
U_ARMADA = 60.0                    # corda na trava
U_SOLTA = 360.0                    # corda em repouso (desarmada)
RAIZ = (545.0, 45.0)               # eixo do braço direito no plano (u, w)
L_VIROTE = 430.0
R_VIROTE = 4.5
V_MIRA = 63.5                      # topo dos trilhos de mira
PIC = [(7.85, 0), (10.6, -2.75), (7.9, -5.5), (-7.9, -5.5), (-10.6, -2.75), (-7.85, 0)]   # perfil do trilho (x, y a partir do topo)
OLIVA = 'polim_oliva'


def _catmull(pts, n=12):
    Q = np.array(pts, float)
    Q = np.vstack([Q[0] * 2 - Q[1], Q, Q[-1] * 2 - Q[-2]])
    out = []
    for i in range(1, len(Q) - 2):
        p0, p1, p2, p3 = Q[i - 1], Q[i], Q[i + 1], Q[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(Q[-2])
    return np.array(out)


def _roty(p, c, graus):
    """Gira o ponto (u, w) em torno de c pelo eixo +v."""
    t = math.radians(graus)
    du, dw = p[0] - c[0], p[1] - c[1]
    return np.array([c[0] + du * math.cos(t) + dw * math.sin(t), c[1] - du * math.sin(t) + dw * math.cos(t)])


LINHA = _catmull([(535, 30), (550, 75), (546, 130), (528, 185), (500, 235), (474, 270), (458, 297), (452, 318), (458, 334), (474, 343)])
ESP = lambda s: 4.8 - 1.6 * s
ALT = lambda s: 11.5 - 3.5 * s


def _normais(L):
    d = np.gradient(L, axis=0)
    d /= np.linalg.norm(d, axis=1)[:, None]
    return np.stack([-d[:, 1], d[:, 0]], 1)


def _nock():
    nor = _normais(LINHA)
    k = int(np.argmin(LINHA[:, 0]))
    s = k / (len(LINHA) - 1)
    lado = -1 if nor[k][0] > 0 else 1
    return LINHA[k] + nor[k] * lado * (ESP(s) + 1.4), k, lado


N_SOLTA, K_NOCK, LADO = _nock()
L_CORDA = float(np.linalg.norm(N_SOLTA - np.array([U_SOLTA, 0.0])))


def _acha_armado():
    a0, a1 = -70.0, 0.0
    for _ in range(60):
        am = (a0 + a1) / 2
        if np.linalg.norm(_roty(N_SOLTA, RAIZ, am) - np.array([U_ARMADA, 0.0])) > L_CORDA:
            a1 = am
        else:
            a0 = am
    return (a0 + a1) / 2


A_ARMADO = _acha_armado()
N_ARMADA = _roty(N_SOLTA, RAIZ, A_ARMADO)
LINHA_A = np.array([_roty(p, RAIZ, A_ARMADO) for p in LINHA])        # o braço direito na posição armada
NOR_A = _normais(LINHA_A)
_LL = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(LINHA_A, axis=0), axis=1))])
S_A = _LL / _LL[-1]


# ------------------------------------------------------------------ ajudas
def pl(g):
    return [(float(x), float(y)) for x, y in list(g.exterior.coords)[:-1]]


def arred(pts, r, n=6):
    g = pts if hasattr(pts, 'exterior') else Polygon(pts)
    return g.buffer(-r, quad_segs=n).buffer(2 * r, quad_segs=n).buffer(-r, quad_segs=n)


def curva(pts, n=2):
    for _ in range(n):
        q = []
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            q += [(0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]), (0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1])]
        pts = q
    return Polygon(pts)


def solido(g, a, b, mat, plane='uv'):
    o = extr(pl(g), a, b, mat, plane)
    if g.interiors:
        m = 1.0 if a < b else -1.0
        cut(o, [extr([(float(x), float(y)) for x, y in list(i.coords)[:-1]], a - m, b + m, mat, plane) for i in g.interiors])
    return o


def lados(g, w0, w1, mat, bv=0.0):
    """A mesma placa dos dois lados (de w0 a w1 e espelhada)."""
    out = []
    for s in (1, -1):
        a, b = sorted((s * w0, s * w1))
        o = solido(g, a, b, mat)
        out.append(bevel(o, bv, 2, 30) if bv else o)
    return out


def _levar(o, M):
    o.data.transform(M)
    if M.determinant() < 0:
        o.data.flip_normals()
    return o


def _espelho_w(o):
    return _levar(o, Matrix.Diagonal((-1, 1, 1, 1)))


def _gira_u(o, graus, v0=LY):
    c = P(0, v0, 0)
    return _levar(o, Matrix.Translation(c) @ Matrix.Rotation(math.radians(graus), 4, 'Y') @ Matrix.Translation(-c))


def trilho(u0, u1, v_topo, mat, baixo=False):
    """Trilho de acessórios ao longo de u; baixo=True: virado para baixo (v_topo é a face de baixo)."""
    s = -1 if baixo else 1
    t = extr([(x, v_topo + s * y) for (x, y) in (PIC[::-1] if baixo else PIC)], u0, u1, mat, plane='wv')
    n = int((u1 - u0 - 6) / 10.008)
    va, vb = sorted((v_topo - s * 3, v_topo + s * 2.5))
    cut(t, [box(u - 5.23, u, va, vb, -12, 12, mat) for u in [u1 - 4.0 - i * 10.008 for i in range(n)]])
    return bevel(t, 0.35, 1, 40)


# ------------------------------------------------------------------ coronha, caixa do gatilho, punho
def corpo():
    cont = curva([(-75, 34), (-160, 36), (-300, 30), (-392, 36), (-402, 30), (-404, -78), (-390, -86), (-330, -72), (-200, -50), (-110, -40),
                  (-70, -30), (-60, 0)])
    jan = curva([(-130, 16), (-300, 12), (-330, -5), (-330, -50), (-300, -58), (-200, -38), (-135, -26), (-120, -6)])
    o = [bevel(solido(cont.difference(jan), -17, 17, OLIVA), 4.5, 4, 30)]
    # soleira de borracha com frisos
    sol = solido(arred([(-403, 33), (-421, 31), (-423, -81), (-403, -81)], 4), -18.5, 18.5, 'borracha')
    cut(sol, [box(-430, -420.5, v, v + 3.2, -30, 30, 'borracha') for v in np.linspace(-70, 20, 10)])
    o.append(bevel(sol, 1.6, 2, 30))
    # apoio de rosto regulável, em duas colunas
    o.append(bevel(solido(arred([(-292, 33), (-158, 35), (-158, 52), (-270, 52)], 8), -13, 13, 'polim'), 4.0, 4, 30))
    for u in (-250, -190):
        o.append(cyl((u, 24, 0), (u, 36, 0), 3.2, 'anod', n=14))
    o.append(cyl((-360, -30, -17.6), (-360, -30, 17.6), 3.2, 'inox', n=16))                 # pino da bandoleira
    # caixa do gatilho com a canaleta de voo no topo
    rec = solido(arred([(-80, -22), (120, -22), (170, -15), (170, V_TRILHO), (-80, V_TRILHO)], 4), -21, 21, 'polim')
    cut(rec, [box(-200, 300, V_TRILHO - 12, 100, -3.6, 3.6, 'polim')] +
        [solido(arred([(62, -14), (150, -12), (158, 0), (158, 24), (70, 24)], 5), a, b, 'polim') for a, b in ((18.4, 30), (-30, -18.4))])
    o.append(bevel(rec, 2.2, 3, 30))
    for s in (-1, 1):
        a, b = sorted((s * 18.2, s * 20.4))
        o.append(solido(arred([(64, -12), (149, -10), (156, 0), (156, 22), (72, 22)], 4), a, b, OLIVA))
        for (u, v) in ((-70, 26), (-70, -12), (12, 26), (165, 26), (120, -16)):
            o.append(cyl((u, v, s * 20.6), (u, v, s * 21.9), 2.3, 'inox', n=6))
        # paredes da trava: a corda passa entre elas e o suporte da mira
        a, b = sorted((s * 6.2, s * 14.5))
        o.append(bevel(solido(arred([(18, V_TRILHO - 2), (58, V_TRILHO - 2), (55, 50), (24, 52)], 3), a, b, 'polim'), 1.0, 2, 30))
        o.append(cyl((42, 30, s * 14.3), (42, 30, s * 15.7), 2.3, 'inox', n=12))
    # suporte e trilho da mira, atrás da trava
    o.append(bevel(solido(arred([(-78, V_TRILHO - 3), (16, V_TRILHO - 3), (12, V_MIRA - 5.5), (-74, V_MIRA - 5.5)], 3), -12, 12, 'polim'), 1.5, 2, 30))
    o.append(trilho(-78, 14, V_MIRA, 'anod'))
    # guarda-mato
    gm = curva([(50, -21), (50, -30), (35, -50), (-10, -52), (-24, -48), (-26, -40), (-12, -42), (30, -42), (40, -30), (40, -21)])
    o.append(bevel(solido(gm, -6, 6, 'polim'), 1.5, 2, 30))
    o.append(texto('RC 151006', 2.6, 20, 14, -(21 + 0.02), mat='tinta'))
    o.append(texto('165 lb', 2.6, 110, 5, -(20.4 + 0.02), mat='tinta'))
    o.append(texto('S     F', 2.4, 6, 15.5, 21 + 0.02, mat='tinta_vermelha', lado=1))
    f = parte('corpo', o, origem=(0, 0, 0), grupo='A', suave=35)

    # punho de pistola pontilhado
    cp = curva([(-12, -20), (-52, -20), (-66, -60), (-80, -112), (-72, -124), (-42, -124), (-36, -100), (-22, -60)], 3)
    b = cp.bounds
    aneis = []
    for v in np.linspace(b[1] + 0.3, -17, 60):
        x = cp.intersection(LineString([(-200, max(v, b[1] + 0.3) if v < b[3] - 0.3 else b[3] - 0.3), (100, max(v, b[1] + 0.3) if v < b[3] - 0.3 else b[3] - 0.3)])).bounds
        aneis.append([P((x[0] + x[2]) / 2 + du, v, w) for du, w in superelipse((x[2] - x[0]) / 2, 14.5, n=40, e=2.4)])
    parte('punho', [bevel(loft(aneis, 'polim_arco_grip'), 3.0, 3, 40)], origem=(-45, -70, 0), pai=f, grupo='A', suave=45)
    return f


# ------------------------------------------------------------------ trilho de voo, guarda-mão, cabeça
def trilho_voo():
    sec = [(-20, V_TRILHO), (-3.6, V_TRILHO), (-3.6, V_TRILHO - 12), (3.6, V_TRILHO - 12), (3.6, V_TRILHO), (20, V_TRILHO), (21, V_TRILHO - 2), (21, 4),
           (18.5, -4), (-18.5, -4), (-21, 4), (-21, V_TRILHO - 2)]
    tr = extr(sec, 165, 510, 'anod', plane='wv')
    cut(tr, [solido(LineString([(u - 8, 16), (u + 8, 16)]).buffer(4.5, 6), -30, 30, 'anod') for u in np.linspace(360, 460, 4)])
    o = [bevel(tr, 0.7, 2, 30)]
    o.append(box(165, 510, V_TRILHO - 12.25, V_TRILHO - 11.2, -3.5, 3.5, 'fita_deslize'))          # fita de deslize no fundo da canaleta
    # guarda-mão de polímero com frisos de borracha e abas que protegem os dedos
    fe = curva([(165, -3), (340, -3), (340, -12), (325, -30), (200, -32), (180, -26), (165, -15)])
    g = solido(fe, -19.5, 19.5, OLIVA)
    cut(g, [box(u, u + 5, -40, -9, s * 18.6, s * 30, OLIVA) if s > 0 else box(u, u + 5, -40, -9, -30, -18.6, OLIVA) for u in np.linspace(206, 314, 8) for s in (1, -1)])
    o.append(bevel(g, 2.6, 3, 30))
    for u in np.linspace(206, 314, 8):
        o += lados(arred([(u + 0.2, -30.5), (u + 4.8, -30.5), (u + 4.8, -11), (u + 0.2, -11)], 1.6), 17.8, 19.9, 'borracha')
    o += lados(arred([(170, 0), (335, 0), (330, 18), (175, 18)], 4), 20.5, 30, OLIVA, 1.8)
    for s in (1, -1):
        a, b = sorted((s * 29.9, s * 30.25))
        o.append(box(326, 329.5, 2.5, 15.5, a, b, 'tinta_vermelha'))
    # trilho curto embaixo (lanterna OU laser OU os dois juntos)
    o.append(bevel(solido(arred([(392, -4.6), (468, -4.6), (468, -3.5), (392, -3.5)], 0.4), -10.5, 10.5, 'anod'), 0.3, 1, 30))
    o.append(trilho(395, 465, -10.0, 'anod', baixo=True))
    # cabeça de alumínio: ponte de baixo e bolsos dos braços
    o.append(bevel(solido(arred([(500, -16), (585, -16), (600, 0), (590, 22), (500, 22)], 8), -62, 62, 'anod_cabeca'), 3.0, 3, 30))
    pod = arred([(505, 21), (582, 21), (590, 30), (580, 56), (520, 57), (505, 48)], 7)
    for s in (1, -1):
        a, b = sorted((s * 20, s * 64))
        p = solido(pod, a, b, 'anod_cabeca')
        a, b = sorted((s * 26, s * 90))
        cut(p, box(380, 640, LY - 12.4, LY + 12.4, a, b, 'anod_cabeca'))
        o.append(bevel(p, 1.6, 2, 30))
        o.append(cyl((RAIZ[0], -18, s * RAIZ[1]), (RAIZ[0], 60, s * RAIZ[1]), 3.6, 'inox', n=14))
        o.append(cyl((RAIZ[0], 57, s * RAIZ[1]), (RAIZ[0], 62, s * RAIZ[1]), 7.2, 'inox', n=6))
        o.append(lathe([(584, 0), (584, 6.5), (592, 6.5), (594, 5.0), (594, 0)], 'borracha', n=18, c0=(0, LY, s * 52)))
        # ponte da massa por cima do virote
        a, b = sorted((s * 17.5, s * 21.5))
        o.append(bevel(solido(arred([(478, V_TRILHO - 2), (512, V_TRILHO - 2), (512, V_MIRA - 5.5), (478, V_MIRA - 5.5)], 3), a, b, 'anod'), 0.8, 2, 30))
    o.append(bevel(solido(arred([(478, V_MIRA - 10.5), (512, V_MIRA - 10.5), (512, V_MIRA - 5.5), (478, V_MIRA - 5.5)], 2), -21.5, 21.5, 'anod'), 0.8, 2, 30))
    o.append(trilho(478, 512, V_MIRA, 'anod'))
    o.append(lathe([(596, 0), (596, 7.2), (604.5, 7.2), (606, 6.0), (606, 3.6), (601, 3.6), (601, 0)], 'anod', n=20))     # bucha do estribo
    return parte('trilho_voo', o, origem=(340, 10, 0), grupo='B', suave=35)


# ------------------------------------------------------------------ braços e corda
def _secao(a, b, k=3):
    c = min(1.0, a * 0.45, b * 0.45)
    out = []
    for (cx, cy, a0) in ((a - c, b - c, 0), (-a + c, b - c, 90), (-a + c, -b + c, 180), (a - c, -b + c, 270)):
        for i in range(k + 1):
            t = math.radians(a0 + 90 * i / k)
            out.append((cx + c * math.cos(t), cy + c * math.sin(t)))
    return out


def _pb(i, x, dv):
    p = LINHA_A[i] + NOR_A[i] * x
    return (float(p[0]), LY + dv, float(p[1]))


def braco(s=1):
    """Braço recurvo de fibra (direito; s = -1 espelha): faces de carbono, ponta de reforço e laço da corda."""
    n = len(LINHA_A)
    alt = lambda i: ALT(S_A[i]) * (math.sqrt(max(0.03, 1 - ((6 - (_LL[-1] - _LL[i])) / 6.2) ** 2)) if _LL[-1] - _LL[i] < 6 else 1.0)
    aneis = [[P(*_pb(i, x, dv)) for x, dv in _secao(ESP(S_A[i]), alt(i))] for i in range(n)]
    c = loft(aneis, 'fibra_arco')
    pintar(c, 'fibra_faixa', lambda p, nn: abs(nn[1]) < 0.3 and abs(p[1] - LY) < 5.5)
    i0 = int(np.searchsorted(_LL, _LL[-1] - 26))
    ref = [[P(*_pb(i, x, dv)) for x, dv in _secao(ESP(S_A[i]) + 1.0, alt(i) + 0.9, 2)] for i in range(i0, n)]
    r = loft(ref, 'fenolico')
    k = K_NOCK
    for alvo in (c, r):
        cut(alvo, [cyl(_pb(k, -14, d * (ALT(S_A[k]) + 1.2)), _pb(k, 14, d * (ALT(S_A[k]) + 1.2)), 2.0, 'fibra_arco', n=14) for d in (1, -1)])
    o = [c, r]
    a, b = ESP(S_A[k]) + 1.9, ALT(S_A[k]) - 0.2
    laco = [_pb(k, x, dv) for x, dv in ((a * LADO, b), (-a * LADO, b), (-a * LADO, -b), (a * LADO, -b))]
    o.append(fio(caminho_arred(laco, 1.6, 3), 1.5, 'corda_reforco', fechado=True, res=2))
    if s < 0:
        o = [_espelho_w(x) for x in o]
    return parte('braco_dir' if s > 0 else 'braco_esq', o, origem=(RAIZ[0], LY, s * RAIZ[1]), grupo='B', suave=40)


def corda(s=1):
    n = Vector((float(N_ARMADA[0]), LY, float(N_ARMADA[1])))
    c = Vector((U_ARMADA, LY, 0.0))
    d = (c - n).normalized()
    o = [cyl(tuple(n), tuple(c + d * 1.5), 1.7, 'corda_besta', n=12),
         cyl(tuple(c - d * 52), tuple(c + d * 1.5), 2.15, 'corda_reforco', n=12),
         cyl(tuple(n + d * 3), tuple(n + d * 46), 2.15, 'corda_reforco', n=12)]
    pm = n + d * 82
    for k in range(8):                                                                         # silenciador de fios de borracha
        a = k * math.pi / 4
        o.append(cyl(tuple(pm), tuple(pm + Vector((math.sin(a) * 4, math.cos(a) * 9, math.sin(a) * 6))), 0.9, 'borracha', n=6))
    if s < 0:
        o = [_espelho_w(x) for x in o]
    return parte('corda_dir' if s > 0 else 'corda_esq', o, origem=(float(N_ARMADA[0]), LY, s * float(N_ARMADA[1])), grupo='B', suave=40)


# ------------------------------------------------------------------ trava, gatilho, segurança, virote
def trava():
    """Garras de aço que seguram a corda armada, com a alavanca laranja contra disparo em vazio."""
    g = arred([(34, 26), (48, 26), (66, 36), (68, 46), (62, 47), (56, 40), (36, 36)], 1.2)
    o = [bevel(x, 0.3, 1, 30) for x in lados(g, 4.7, 6.0, 'inox')]
    o.append(cyl((40, 30, -6.2), (40, 30, 6.2), 2.4, 'inox', n=14))
    o.append(bevel(solido(arred([(30, 37), (38, 37), (40, 47), (32, 47)], 1.0), -1.5, 1.5, 'laranja_trava'), 0.3, 1, 30))
    return parte('trava_corda', o, origem=(40, 30, 0), grupo='B', suave=40)


def gatilho():
    g = curva([(16, -20), (26, -20), (25, -30), (22, -40), (16, -45), (14, -43), (18, -32), (17, -24)])
    return parte('gatilho', [bevel(solido(g, -3.5, 3.5, 'fosf'), 0.6, 2, 40)], origem=(22, -20, 0), grupo='B', suave=40)


def seguranca():
    g = arred([(-4, 6), (16, 6), (16, 11), (-4, 11)], 2.2)
    o = []
    for x in lados(g, 20.6, 24.6, 'polim'):
        o.append(bevel(x, 0.6, 1, 30))
    o.append(cyl((3, 8.5, -22), (3, 8.5, 22), 2.0, 'inox', n=10))
    return parte('seguranca', o, origem=(3, 8.5, 21), grupo='B', suave=40)


def virote():
    """Virote de carbono: entalhe em meia-lua na corda, pena ímpar (branca) para baixo, na canaleta."""
    u0, L, r = U_ARMADA, L_VIROTE, R_VIROTE
    c0 = (u0, LY, 0)
    nock = lathe([(0, 0), (0, r + 0.3), (12, r + 0.3), (14, r), (14, 0)], 'nock_vermelho', n=20, c0=c0)
    cut(nock, cyl((u0 - 1.2, LY, -10), (u0 - 1.2, LY, 10), 3.4, 'nock_vermelho', n=16))
    o = [bevel(nock, 0.25, 1, 40)]
    o.append(lathe([(14, 0), (14, r), (L - 12, r), (L - 12, 0)], 'carbono', n=20, c0=c0))
    o.append(lathe([(98, r + 0.02), (98, r + 0.14), (110, r + 0.14), (110, r + 0.02)], 'envoltorio', n=20, c0=c0, anel=True))
    o.append(lathe([(L - 16, 0), (L - 16, r + 0.4), (L - 10, r + 0.4), (L - 10, 0)], 'anod', n=20, c0=c0))
    perfil = [(30, 0), (32, 5.0), (40, 8.4), (52, 9.6), (68, 9.4), (80, 6.4), (85, 0)]
    for k in range(3):
        pena = extr([(u0 + a, LY + r - 0.3 + b) for a, b in perfil], -0.5, 0.5, 'pena_branca' if k == 0 else 'pena_vermelha')
        o.append(_gira_u(bevel(pena, 0.18, 1, 40), 180 + 120 * k))
    o.append(lathe([(L - 10, 0), (L - 10, 4.1), (L - 4, 5.2), (L + 6, 4.9), (L + 16, 4.2), (L + 32, 0)], 'inox', n=20, c0=c0))
    for k in range(3):
        lam = extr([(u0 + L - 2, LY + 2.0), (u0 + L + 28, LY + 1.4), (u0 + L + 4, LY + 13.8), (u0 + L - 2, LY + 12.2)], -0.45, 0.45, 'aco_lamina')
        cut(lam, extr([(u0 + L + 0.5, LY + 5.6), (u0 + L + 13.5, LY + 5.2), (u0 + L + 4.4, LY + 10.4), (u0 + L + 0.5, LY + 9.8)], -2, 2, 'aco_lamina'))
        o.append(_gira_u(lam, 60 + 120 * k))
    return parte('virote', o, origem=c0, grupo='B', suave=40)


def montar():
    corpo()
    trilho_voo()
    for s in (1, -1):
        braco(s)
        corda(s)
    trava()
    gatilho()
    seguranca()
    virote()
