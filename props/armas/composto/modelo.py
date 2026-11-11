"""Arco composto no nível de detalhe da M4A1: punho de alumínio usinado em treliça, pega de
polímero, braços divididos de fibra em bolsos de alumínio, polias excêntricas vazadas com
módulo de cabos, corda e cabos torcidos, protetor de cabos com deslizador, batente da corda,
apoio de flecha que cai, visor na corda, laço D e flecha de carbono. Desenho próprio, sem marcas.

Mesmas medidas e pontos do arco antigo (arma16_composto.py), para os nós (braços, polias,
metades da corda, cabos, laço D, visor, apoio, flecha), os acessórios (mira de pinos com luz,
soltador, estabilizador, aljava) e as animações continuarem valendo.

Coordenadas em mm (lib.py da M4A1): u = para a frente (para onde a flecha vai), v = para
cima, w = direita do arqueiro. A corda fica em u negativo.
"""
import math
import numpy as np
import bpy, bmesh
from mathutils import Matrix, Vector
from shapely.geometry import Polygon, LineString, Point, box as caixa2d
from shapely.ops import unary_union
from shapely import affinity
from lib import *
from lib import _obj

# ------------------------------------------------------------------ medidas (as do arco antigo)
V_FLECHA = 30.0
U_CORDA = -200.0                   # corda em repouso
U_PUXADA = -640.0
R_CORDA = 45.0                     # raio da trilha da corda na polia
R_CABO = 26.0                      # raio do módulo dos cabos
C_POLIA = (-155.0, 385.0)          # eixo da polia de cima (a de baixo é espelhada)
PK = (70.0, 300.0)                 # eixo do bolso do braço de cima
A_BRACO = 7.0
P_GUIA = (-77.0, 70.0)             # deslizador do protetor de cabos
W_GUIA = 31.0
L_FLECHA = 740.0
R_FLECHA = 3.1
MEIA = 12.0                        # meia espessura do punho
W_JANELA = 4.6
AL = 'anod_arco'
PRETO = 'anod'


def _rot2(p, c, graus):
    t = math.radians(graus)
    d = np.array(p, float) - np.array(c, float)
    return np.array(c, float) + np.array([d[0] * math.cos(t) - d[1] * math.sin(t), d[0] * math.sin(t) + d[1] * math.cos(t)])


def _tangente(C, r, Pt, sinal):
    C = np.array(C, float)
    Pt = np.array(Pt, float)
    d = Pt - C
    D = np.linalg.norm(d)
    b = math.atan2(d[1], d[0])
    a = math.acos(r / D)
    for t in (b + a, b - a):
        T = C + r * np.array([math.cos(t), math.sin(t)])
        u, w = T - C, Pt - T
        if (u[0] * w[1] - u[1] * w[0]) * sinal > 0:
            return T
    return C + r * np.array([math.cos(b + a), math.sin(b + a)])


def _ang(v):
    return math.degrees(math.atan2(v[1], v[0]))


def _linha(C, r, P0, Pd, sy, sinal, phi):
    pk = np.array([PK[0], sy * PK[1]])
    C0 = np.array(C, float)
    Cd = _rot2(C0, pk, phi)
    T0 = _tangente(C0, r, P0, sinal)
    Td = _tangente(Cd, r, Pd, sinal)
    return T0, float(np.linalg.norm(np.array(Pd) - Td)), Td


C_POLIA_B = (C_POLIA[0], -C_POLIA[1])
NOCK0 = (U_CORDA, V_FLECHA)
NOCKD = (U_PUXADA, V_FLECHA)
T_CC, LD_CC, TD_CC = _linha(C_POLIA, R_CORDA, NOCK0, NOCKD, 1, 1, A_BRACO)
T_CB, LD_CB, _ = _linha(C_POLIA_B, R_CORDA, NOCK0, NOCKD, -1, -1, -A_BRACO)
T_KC, _, _ = _linha(C_POLIA, R_CABO, P_GUIA, P_GUIA, 1, -1, A_BRACO)
T_KB, _, _ = _linha(C_POLIA_B, R_CABO, P_GUIA, P_GUIA, -1, 1, -A_BRACO)
_U = (TD_CC - np.array(NOCKD)) / np.linalg.norm(TD_CC - np.array(NOCKD))
S_VISOR = 72.0 / _U[1]
VISOR0 = (U_CORDA, V_FLECHA + S_VISOR)
G_VISOR = _ang(_U) - 90.0
ANG_BRACO = _ang(np.array(C_POLIA) - np.array(PK))
L_BRACO = float(np.linalg.norm(np.array(C_POLIA) - np.array(PK)))


# ------------------------------------------------------------------ ajudas
def pl(g):
    return [(float(x), float(y)) for x, y in list(g.exterior.coords)[:-1]]


def arred(pts, r, n=6):
    g = pts if hasattr(pts, 'exterior') else Polygon(pts)
    return g.buffer(-r, quad_segs=n).buffer(2 * r, quad_segs=n).buffer(-r, quad_segs=n)


def solido(g, a, b, mat, plane='uv'):
    """Extrusão de um polígono shapely (os furos viram cortes)."""
    o = extr(pl(g), a, b, mat, plane)
    if g.interiors:
        m = 1.0 if a < b else -1.0
        cut(o, [extr([(float(x), float(y)) for x, y in list(i.coords)[:-1]], a - m, b + m, mat, plane) for i in g.interiors])
    return o


def _catmull(pts, n=10):
    Q = np.array(pts, float)
    Q = np.vstack([Q[0] * 2 - Q[1], Q, Q[-1] * 2 - Q[-2]])
    out = []
    for i in range(1, len(Q) - 2):
        p0, p1, p2, p3 = Q[i - 1], Q[i], Q[i + 1], Q[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(Q[-2])
    return np.array(out)


def _levar(o, M):
    o.data.transform(M)
    if M.determinant() < 0:
        o.data.flip_normals()
    return o


def _espelho(o):
    """Espelha em v (peça de cima -> peça de baixo)."""
    return _levar(o, Matrix.Diagonal((1, 1, -1, 1)))


def _m_braco():
    """Do referencial do braço de cima (u ao longo dele, do bolso para a polia; v para fora) para o arco."""
    t = math.radians(ANG_BRACO)
    d, n = (math.cos(t), math.sin(t)), (math.sin(t), -math.cos(t))
    M = Matrix.Identity(4)
    M[1][1], M[2][1] = d[0], d[1]
    M[1][2], M[2][2] = n[0], n[1]
    M[1][3], M[2][3] = PK[0] * MM, PK[1] * MM
    return M


M_BRACO = _m_braco()


def no_braco(o, sv=1):
    _levar(o, M_BRACO)
    return o if sv > 0 else _espelho(o)


def _gira_w(o, graus, c):
    """Gira no plano de lado em torno do ponto c = (u, v)."""
    p = P(c[0], c[1], 0)
    return _levar(o, Matrix.Translation(p) @ Matrix.Rotation(math.radians(graus), 4, 'X') @ Matrix.Translation(-p))


def _gira_u(o, graus, v0=V_FLECHA):
    c = P(0, v0, 0)
    return _levar(o, Matrix.Translation(c) @ Matrix.Rotation(math.radians(graus), 4, 'Y') @ Matrix.Translation(-c))


def _sv(o, sv):
    return o if sv > 0 else _espelho(o)


def _arco_pts(C, r, t0, t1, w, n=14, sv=1):
    return [(C[0] + r * math.cos(t), C[1] + r * math.sin(t), w) for t in np.radians(np.linspace(t0, t1, n))]


# ------------------------------------------------------------------ punho usinado
LINHA_PUNHO = _catmull([(86, 283), (80, 240), (64, 180), (47, 120), (35, 60), (31, 0), (35, -60), (47, -120), (64, -180), (80, -240),
                        (86, -283)], 10)


def _perfil_punho():
    ln = LineString(LINHA_PUNHO)
    fora = ln.buffer(20, quad_segs=16, cap_style='round')
    # reforço atrás da prateleira e ponte até o suporte do batente
    fora = unary_union([fora, arred([(8, 44), (30, 44), (30, -20), (8, -20)], 3)])
    miolo = ln.buffer(14.2, quad_segs=12, cap_style='flat')
    furos = []
    for (v0, v1) in ((98, 262), (-262, -128)):
        zona = miolo.intersection(caixa2d(-50, min(v0, v1), 200, max(v0, v1)))
        n = 4
        almas = []
        for k in range(n + 1):                                     # almas em zigue-zague entre as duas longarinas
            va = v0 + (v1 - v0) * k / n
            vb = v0 + (v1 - v0) * (k + (0.5 if k < n else 0)) / n
            ia, ib = (int(np.argmin(abs(LINHA_PUNHO[:, 1] - x))) for x in (va, vb))
            ca, cb = LINHA_PUNHO[ia], LINHA_PUNHO[ib]
            na = np.array([1.0, -(LINHA_PUNHO[min(ia + 1, len(LINHA_PUNHO) - 1)][0] - LINHA_PUNHO[max(ia - 1, 0)][0]) /
                           (LINHA_PUNHO[min(ia + 1, len(LINHA_PUNHO) - 1)][1] - LINHA_PUNHO[max(ia - 1, 0)][1])])
            na /= np.linalg.norm(na)
            s = 1 if k % 2 else -1
            almas.append(LineString([tuple(ca + na * 22 * s), tuple(cb - na * 22 * s)]).buffer(3.4))
            if k < n:
                vc = v0 + (v1 - v0) * (k + 1) / n
                ic = int(np.argmin(abs(LINHA_PUNHO[:, 1] - vc)))
                almas.append(LineString([tuple(cb - na * 22 * s), tuple(LINHA_PUNHO[ic] + na * 22 * s)]).buffer(3.4))
        resto = zona.difference(unary_union(almas))
        for g in (resto.geoms if hasattr(resto, 'geoms') else [resto]):
            g = g.buffer(-2.6, quad_segs=5).buffer(2.6, quad_segs=5)
            for h in (g.geoms if hasattr(g, 'geoms') else [g]):
                if h.area > 60:
                    furos.append(h)
    furos.append(Point(41, -70).buffer(5.5, 12))
    furos.append(Point(36, -38).buffer(4.0, 12))
    return fora, fora.difference(unary_union(furos))


def punho():
    fora, perfil = _perfil_punho()
    c = solido(perfil, -MEIA, MEIA, AL)
    # janela de mira: o lado esquerdo sai, para a flecha passar no plano da corda
    cut(c, extr([(-40, V_FLECHA - 12), (W_JANELA - 2.5, V_FLECHA - 12), (W_JANELA, V_FLECHA - 9.5), (W_JANELA, 150), (-4, 166), (-40, 170)],
                -120, 220, AL, plane='wv'))
    o = [bevel(c, 1.3, 2, 30)]
    # rebaixos usinados dos lados, acompanhando o arco do punho perto dos bolsos
    for s in (1, -1):
        ln = LineString(_catmull([(83, 272 * s), (70, 215 * s), (57, 170 * s)], 8))
        friso = ln.buffer(17.4, quad_segs=10).difference(ln.buffer(15.8, quad_segs=10)).intersection(fora.buffer(-1.5))
        for g in (friso.geoms if hasattr(friso, 'geoms') else [friso]):
            for (a, b) in ((MEIA - 0.2, MEIA + 0.5), (-MEIA - 0.5, -MEIA + 0.2)):
                o.append(solido(g, a, b, 'anod_laranja'))
    # bolsos dos braços (alumínio preto), eixo e parafuso de tensão
    for s in (1, -1):
        bl = box(-48, 24, -17, 5, -21.5, 21.5, PRETO)
        cut(bl, [box(-60, 40, -6.3, 20, -18.6, 18.6, PRETO), box(-60, -20, -30, 20, -5.5, 5.5, PRETO)])
        o.append(no_braco(bevel(bl, 1.0, 2, 30), s))
        o.append(_sv(cyl((PK[0], PK[1], -23.3), (PK[0], PK[1], 23.3), 3.2, 'inox', n=18), s))
        for w in (-1, 1):
            o.append(_sv(cyl((PK[0], PK[1], w * 21.5), (PK[0], PK[1], w * 23.9), 5.4, PRETO, n=6), s))
        o.append(no_braco(cyl((-34, -12, 0), (-34, 9.5, 0), 4.2, 'inox', n=18), s))
        cab = lathe([(9.5, 0), (9.5, 7.8), (14.5, 7.8), (15.5, 6.8), (15.5, 3.0), (13.0, 3.0), (13.0, 0)], PRETO, n=28, c0=(-34, 0, 0), eixo=(0, 1, 0),
                    lobes=0.06, lobe_min=6.5)
        o.append(no_braco(cab, s))
        o.append(no_braco(box(-46, -22, 5.9, 9.4, -19, 19, 'inox'), s))                         # chapa que aperta os braços
    # buchas: estabilizador (frente, abaixo da mão), mira e aljava (lado direito)
    o.append(lathe([(0, 0), (0, 8.6), (17.5, 8.6), (20.5, 6.6), (20.5, 4.4), (18.5, 4.4), (18.5, 0)], PRETO, n=28, c0=(50, -100, 0)))
    o.append(lathe([(18.4, 4.5), (19.6, 4.5), (19.6, 2.6), (18.4, 2.6)], 'latao', n=20, c0=(50, -100, 0), anel=True))
    for (u, v) in ((56, 106), (60, 148), (60, -112), (62, -150)):
        o.append(lathe([(0, 3.0), (1.3, 3.0), (1.3, 1.6), (0.4, 1.6), (0.4, 0)], 'latao', n=18, c0=(u, v, MEIA - 0.5), eixo=(0, 0, 1)))
    # protetor de cabos: suporte no lado direito e haste de carbono para trás
    o.append(bevel(solido(arred([(4, 57), (37, 57), (37, 83), (4, 83)], 4), MEIA - 0.3, 16.5, PRETO), 0.6, 1, 30))
    o.append(bevel(solido(arred([(0, 61), (17, 61), (17, 79), (0, 79)], 4), 15.5, W_GUIA + 6.5, PRETO), 0.8, 2, 30))
    o.append(cyl((-116, P_GUIA[1], W_GUIA), (9, P_GUIA[1], W_GUIA), 3.6, 'carbono', n=20))
    o.append(lathe([(-123, 0), (-123, 3.6), (-121.5, 4.6), (-113, 4.6), (-113, 0)], 'borracha', n=20, c0=(0, P_GUIA[1], W_GUIA)))
    # deslizador por onde passam os cabos
    gu, gv = P_GUIA
    des = solido(arred([(gu - 10.5, gv - 27), (gu + 10.5, gv - 27), (gu + 10.5, gv + 27), (gu - 10.5, gv + 27)], 5.5), W_GUIA - 9, W_GUIA + 11, 'polim')
    cut(des, [cyl((gu - 30, gv + dv, W_GUIA + dw), (gu + 30, gv + dv, W_GUIA + dw), 2.0, 'polim', n=12) for dv in (-17, 17) for dw in (-2.5, 4.5)])
    o.append(bevel(des, 1.0, 2, 30))
    # batente da corda: haste embaixo da mão, com ponta de borracha logo na frente da corda
    o.append(cyl((U_CORDA + 30, -130, 0), (40, -130, 0), 3.4, 'carbono', n=18))
    o.append(lathe([(12, 0), (12, 7.4), (16, 9.6), (28, 9.6), (34, 5.2), (34, 0)], 'borracha', n=24, c0=(U_CORDA, -130, 0)))
    o.append(lathe([(26, 0), (26, 6.2), (52, 6.2), (52, 0)], PRETO, n=20, c0=(0, -130, 0)))
    # corpo do apoio de flecha, preso no lado direito
    va = V_FLECHA
    o.append(bevel(solido(arred([(-57, va - 37), (-34, va - 37), (-34, va - 6), (-57, va - 6)], 4.5), 3.2, 17.2, PRETO), 0.7, 2, 30))
    o.append(bevel(solido(arred([(-40, va - 12.5), (27, va - 12.5), (27, va - 5), (-40, va - 5)], 2.2), MEIA - 0.2, 17.2, PRETO), 0.5, 1, 30))
    o.append(lathe([(17.2, 0), (17.2, 5.4), (19.6, 5.4), (19.6, 0)], 'anod_laranja', n=24, c0=(-46, va - 26, 0), eixo=(0, 0, 1), lobes=0.08))
    for (u, v) in ((-8, va - 8.7), (18, va - 8.7)):
        o.append(cyl((u, v, 17.0), (u, v, 18.2), 2.4, 'inox', n=6))
    o.append(texto('RC 310522', 2.6, 32, -12, -(MEIA + 0.02), mat='tinta'))
    o.append(texto('60 lb   alívio 80%', 2.2, 33, -12, MEIA + 0.02, mat='tinta', lado=1))
    f = parte('punho', o, origem=(0, 0, 0), grupo='A', suave=35)

    # pega de polímero presa nas costas do punho
    tras = [(-96, 5), (-86, -1), (-72, -8), (-52, -14.5), (-32, -19.5), (-14, -22), (-2, -20), (8, -14), (17, -5)]
    aneis = []
    for v in np.linspace(-96, 17, 46):
        ur = float(np.interp(v, [p[0] for p in tras], [p[1] for p in tras]))
        hw = 13.6 - 1.2 * max(0.0, (v + 20) / 37) - 1.6 * max(0.0, (-80 - v) / 16)
        aneis.append([P((19 + ur) / 2 + x, v, w) for x, w in superelipse((19 - ur) / 2, hw, n=40, e=2.5)])
    g = loft(aneis, 'polim_arco_grip')
    cut(g, box(16.6, 60, -120, 40, -30, 30, 'polim_arco_grip'))
    pg = [bevel(g, 2.2, 3, 40)]
    for v in (-25, -70):
        pg.append(cyl((8, v, 12.3), (8, v, 13.9), 2.3, 'inox', n=6))
    parte('pega', pg, origem=(-8, -40, 0), pai=f, grupo='A', suave=45)
    return f


# ------------------------------------------------------------------ braços, polias
def _secao(a, b, k=3):
    c = min(1.1, a * 0.45, b * 0.45)
    out = []
    for (cx, cy, a0) in ((a - c, b - c, 0), (-a + c, b - c, 90), (-a + c, -b + c, 180), (a - c, -b + c, 270)):
        for i in range(k + 1):
            t = math.radians(a0 + 90 * i / k)
            out.append((cx + c * math.cos(t), cy + c * math.sin(t)))
    return out


def braco(sv=1):
    """Braço dividido: duas lâminas de fibra, uma de cada lado da polia, eixo, casquilhos e amortecedores."""
    pts = _catmull([(-50, 0), (0, 0), (90, 5), (180, 4), (L_BRACO + 12, 0)], 12)
    d = np.gradient(pts, axis=0)
    d /= np.linalg.norm(d, axis=1)[:, None]
    nor = np.stack([-d[:, 1], d[:, 0]], 1)
    L = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    S = L / L[-1]
    o = []
    for wc in (-12.5, 12.5):
        aneis = []
        for i in range(len(pts)):
            a, b = 5.8 - 1.6 * S[i], 5.5
            aneis.append([P(pts[i][0] + nor[i][0] * x, pts[i][1] + nor[i][1] * x, wc + w) for x, w in _secao(a, b)])
        lam = loft(aneis, 'fibra_arco')
        pintar(lam, 'fibra_faixa', lambda p, n: 60 < p[0] < 205 and abs(n[2]) < 0.3 and n[1] > 0.5)
        o.append(no_braco(lam, sv))
        pt = solido(arred([(L_BRACO - 23, -7.2), (L_BRACO + 13.5, -7.2), (L_BRACO + 13.5, 7.2), (L_BRACO - 23, 7.2)], 4.5), wc - 6.3, wc + 6.3, PRETO)
        o.append(no_braco(bevel(pt, 0.8, 2, 30), sv))
        amo = solido(arred([(84, 4.2), (122, 4.6), (116, 13), (90, 12)], 2.4), wc - 4.2, wc + 4.2, 'borracha')
        o.append(no_braco(bevel(amo, 0.8, 2, 30), sv))
    o.append(no_braco(cyl((L_BRACO, 0, -20), (L_BRACO, 0, 20), 3.4, 'inox', n=18), sv))
    for w in (-1, 1):
        o.append(no_braco(cyl((L_BRACO, 0, w * 18.8), (L_BRACO, 0, w * 20.6), 5.0, PRETO, n=6), sv))
    return parte('braco_cima' if sv > 0 else 'braco_baixo', o, origem=(PK[0], sv * PK[1], 0), grupo='B', suave=38)


def polia(sv=1):
    """Polia excêntrica: trilha da corda, módulo dos cabos dos dois lados, rasgos e pino de parada."""
    cx, cy = C_POLIA
    lobo = unary_union([Point(cx, cy).buffer(R_CORDA + 1.8, 20), Point(cx + 14, cy - 12).buffer(40, 16)])
    vaz = []
    for k in range(5):
        a0 = math.radians(k * 72 + 20)
        vaz.append(LineString([(cx + 31 * math.cos(a0 + t), cy + 31 * math.sin(a0 + t)) for t in np.linspace(-0.36, 0.36, 9)]).buffer(5.2, 5))
    vaz.append(Point(cx + 30, cy - 34).buffer(5.5, 8))
    placa = solido(lobo.difference(unary_union(vaz)), -4.2, 4.2, PRETO)
    cut(placa, lathe([(-1.15, R_CORDA + 6), (-1.15, R_CORDA - 0.9), (1.15, R_CORDA - 0.9), (1.15, R_CORDA + 6)], PRETO, n=64, c0=(cx, cy, 0), eixo=(0, 0, 1), anel=True))
    o = [bevel(placa, 0.5, 1, 30)]
    md = Point(cx, cy).buffer(R_CABO + 1.5, 16).union(Point(cx - 8, cy + 10).buffer(19, 12)).difference(
        unary_union([Point(cx + 14 * math.cos(math.radians(a)), cy + 14 * math.sin(math.radians(a))).buffer(4.2, 6) for a in (30, 150, 270)]))
    for (a, b) in ((4.15, 6.4), (-6.4, -4.15)):
        m = solido(md, a, b, 'anod_laranja')
        zc = (a + b) / 2
        cut(m, lathe([(zc - 0.55, R_CABO + 5), (zc - 0.55, R_CABO - 0.7), (zc + 0.55, R_CABO - 0.7), (zc + 0.55, R_CABO + 5)], 'anod_laranja', n=48,
                     c0=(cx, cy, 0), eixo=(0, 0, 1), anel=True))
        o.append(m)
    o.append(cyl((cx, cy, -7.1), (cx, cy, 7.1), 6.2, PRETO, n=24))
    o.append(cyl((cx + 30, cy - 30, -7.4), (cx + 30, cy - 30, 7.4), 1.6, 'inox', n=10))
    o.append(cyl((cx + 30, cy - 30, 4.25), (cx + 30, cy - 30, 7.2), 2.9, 'borracha', n=14))
    for a in range(0, 360, 60):
        u, v = cx + 19.5 * math.cos(math.radians(a)), cy + 19.5 * math.sin(math.radians(a))
        for s in (1, -1):
            o.append(cyl((u, v, s * 6.3), (u, v, s * 6.9), 1.3, 'inox', n=6))
    o = [_sv(x, sv) for x in o]
    return parte('polia_cima' if sv > 0 else 'polia_baixo', o, origem=(cx, sv * cy, 0), grupo='B', suave=35)


# ------------------------------------------------------------------ corda, cabos, laço D, visor, apoio
def corda(sv=1):
    """Metade da corda: enrolada na trilha, desce reta até o ponto de encaixe. O prolongamento (mais fino)
    fica dentro da outra metade em repouso e cobre a distância maior com o arco puxado."""
    C = C_POLIA if sv > 0 else C_POLIA_B
    T = T_CC if sv > 0 else T_CB
    LD = LD_CC if sv > 0 else LD_CB
    n0 = np.array(NOCK0)
    d = (n0 - T) / np.linalg.norm(n0 - T)
    L0 = float(np.linalg.norm(n0 - T))
    p = lambda q: (float(q[0]), float(q[1]), 0.0)
    o = [cyl(p(T), p(n0), 1.35, 'corda', n=12), cyl(p(n0), p(T + d * (LD + 4)), 1.0, 'corda', n=8)]
    tT = _ang(T - np.array(C))
    o.append(fio(_arco_pts(C, R_CORDA - 0.2, tT - 120 * sv, tT, 0.0, 16), 1.35, 'corda', fechado=False, res=2))
    o.append(cyl(p(T), p(T + d * 50), 1.75, 'corda_reforco', n=12))
    o.append(cyl(p(n0 - d * 62), p(n0), 1.75, 'corda_reforco', n=12))
    # silenciador de borracha a 1/3 da corda
    pm = T + d * (L0 * 0.36)
    for k in range(8):
        a = k * math.pi / 4
        o.append(cyl(p(pm), (float(pm[0] + math.cos(a) * 8), float(pm[1] + sv * 3), math.sin(a) * 8), 0.9, 'borracha', n=6))
    return parte('corda_cima' if sv > 0 else 'corda_baixo', o, origem=(C[0], C[1], 0), grupo='B', suave=40)


def cabo(sv=1):
    """Duas pernas de cabo do módulo da polia até o deslizador do protetor (lado direito)."""
    C = C_POLIA if sv > 0 else C_POLIA_B
    T = T_KC if sv > 0 else T_KB
    o = []
    tT = _ang(T - np.array(C))
    for wc, wg in ((5.3, W_GUIA - 2.5), (-5.3, W_GUIA + 4.5)):
        p0, p1 = Vector((float(T[0]), float(T[1]), wc)), Vector((P_GUIA[0], P_GUIA[1] + sv * 17, wg))
        o.append(cyl(tuple(p0), tuple(p1), 1.2, 'cabo', n=10))
        o.append(cyl(tuple(p0.lerp(p1, 0.02)), tuple(p0.lerp(p1, 0.2)), 1.55, 'corda_reforco', n=10))
        o.append(fio(_arco_pts(C, R_CABO - 0.3, tT, tT + 110 * sv, wc, 12), 1.2, 'cabo', fechado=False, res=2))
    return parte('cabo_cima' if sv > 0 else 'cabo_baixo', o, origem=(C[0], C[1], 0), grupo='B', suave=40)


def laco_d():
    u, v = NOCK0
    pts = _catmull([(u, v + 7.8), (u - 7, v + 7.4), (u - 13.5, v + 3), (u - 13.5, v - 3), (u - 7, v - 7.4), (u, v - 7.8)], 6)
    o = [fio([(float(a), float(b), 0.0) for a, b in pts], 1.4, 'cordel', fechado=False, res=2)]
    for dv in (7.8, -7.8):
        o.append(lathe([(-2.0, 0), (-1.6, 2.2), (0, 2.8), (1.6, 2.2), (2.0, 0)], 'cordel', n=12, c0=(u, v + dv, 0), eixo=(0, 1, 0)))
    o.append(lathe([(0, 1.7), (0, 2.3), (1.3, 2.3), (1.3, 1.7)], 'latao', n=12, c0=(u, v + 4.4, 0), eixo=(0, 1, 0), anel=True))
    return parte('laco_d', o, origem=(u, v, 0), grupo='B', suave=40)


def visor():
    """Visor de corda (peep): disco com furo, já inclinado para ficar de frente para o olho com o arco puxado."""
    c0 = (VISOR0[0], VISOR0[1], 0)
    d = lathe([(-2.2, 1.9), (-2.2, 5.0), (-1.0, 6.2), (1.0, 6.2), (2.2, 5.0), (2.2, 1.9)], 'anod_laranja', n=28, c0=c0, anel=True)
    cut(d, [lathe([(-0.6, 5.6), (-0.6, 8), (0.6, 8), (0.6, 5.6)], 'anod_laranja', n=28, c0=c0, anel=True)])
    return parte('visor_corda', [_gira_w(d, -G_VISOR, VISOR0)], origem=c0, grupo='B', suave=40)


def apoio():
    """Lançador do apoio que cai: haste com forquilha forrada de feltro."""
    va = V_FLECHA
    pu, pv = -40.0, va - 20.0
    o = [cyl((pu, pv, 0), (pu, pv, 3.6), 2.6, PRETO, n=14)]
    o.append(bevel(solido(arred([(pu - 3.4, pv - 3.4), (pu + 4.5, pv - 4.2), (-13.5, va - 8), (-19.5, va - 4.2)], 1.5), -1.5, 1.5, PRETO), 0.4, 1, 30))
    for s in (1, -1):
        g = extr([(-21.5, va - 8), (-12.5, va - 8), (-12.5, va - 3.6), (-16, va - 0.2), (-21.5, va - 2.2)], 0.0, 1.5, 'feltro')
        o.append(_levar(g, Matrix.Translation(P(0, va - 8, 0)) @ Matrix.Rotation(math.radians(-32 * s), 4, 'Y') @ Matrix.Translation(-P(0, va - 8, 0))))
    return parte('apoio', o, origem=(pu, pv, 0), grupo='B', suave=40)


# ------------------------------------------------------------------ flecha
def flecha():
    """Flecha fina de carbono com 3 penas curtas, entalhe vermelho e ponta de caça; entalhe em (U_CORDA, V_FLECHA)."""
    u0, v0, L, r = U_CORDA, V_FLECHA, L_FLECHA, R_FLECHA
    c0 = (u0, v0, 0)
    nock = lathe([(-1.0, 0), (-1.0, 2.2), (0.5, 3.0), (4.0, 3.4), (9, 3.4), (10.5, r), (10.5, 0)], 'nock_vermelho', n=18, c0=c0)
    cut(nock, box(u0 - 3, u0 + 4.2, v0 - 8, v0 + 8, -1.85, 1.85, 'nock_vermelho'))
    o = [bevel(nock, 0.25, 1, 40)]
    o.append(lathe([(10.5, 0), (10.5, r), (L - 14, r), (L - 14, 0)], 'carbono', n=18, c0=c0))
    o.append(lathe([(13, r + 0.02), (13, r + 0.12), (105, r + 0.12), (105, r + 0.02)], 'envoltorio', n=18, c0=c0, anel=True))
    o.append(lathe([(L - 16, 0), (L - 16, r + 0.35), (L - 9.5, r + 0.35), (L - 9.5, 0)], PRETO, n=18, c0=c0))
    perfil = [(30, 0), (31.5, 4.2), (37, 7.6), (46, 9.0), (60, 8.6), (70, 5.8), (75, 0)]
    for k in range(3):
        pena = extr([(u0 + a, v0 + r - 0.3 + b) for a, b in perfil], -0.5, 0.5, 'pena_laranja' if k == 0 else 'pena_verde')
        o.append(_gira_u(bevel(pena, 0.18, 1, 40), -90 + 120 * k))
    o.append(lathe([(L - 9.5, 0), (L - 9.5, 3.4), (L - 6, 3.9), (L + 4, 3.7), (L + 12, 3.2), (L + 26, 0)], 'inox', n=18, c0=c0))
    for k in range(3):
        lam = extr([(u0 + L - 3, v0 + 1.6), (u0 + L + 22, v0 + 1.2), (u0 + L + 3, v0 + 12.2), (u0 + L - 3, v0 + 10.8)], -0.42, 0.42, 'aco_lamina')
        cut(lam, extr([(u0 + L - 0.8, v0 + 4.8), (u0 + L + 10.5, v0 + 4.5), (u0 + L + 3.2, v0 + 9.0), (u0 + L - 0.8, v0 + 8.4)], -2, 2, 'aco_lamina'))
        o.append(_gira_u(lam, -30 + 120 * k))
    return parte('flecha', o, origem=c0, grupo='B', suave=40)


def montar():
    punho()
    for sv in (1, -1):
        braco(sv)
        polia(sv)
        corda(sv)
        cabo(sv)
    laco_d()
    visor()
    apoio()
    flecha()
