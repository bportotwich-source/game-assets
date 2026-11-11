"""Arco recurvo desmontável no nível de detalhe da M4A1: punho de madeira laminada esculpido
(janela de mira, prateleira com feltro, buchas de latão), braços laminados de fibra preta
com miolo de bordo, presos por manípulos, pontas com reforço e entalhes, corda torcida com
reforço no meio e flecha de carbono com ponta de caça. Desenho próprio, sem marcas.

Mesmas medidas e pontos do arco antigo (arma15_arco.py), para os nós (braços, metades da
corda, flecha), os acessórios (mira de pinos, estabilizador, aljava) e as animações
continuarem valendo: eixo dos braços, ponto em que a corda deixa o braço e ponto de
encaixe da flecha não mudaram.

Coordenadas em mm (lib.py da M4A1): u = para a frente (para onde a flecha vai), v = para
cima, w = direita do arqueiro. A corda fica em u negativo.
"""
import math
import numpy as np
import bpy, bmesh
from mathutils import Matrix, Vector
from lib import *
from lib import _obj

# ------------------------------------------------------------------ medidas (as do arco antigo)
V_FLECHA = 30.0                    # altura da flecha no apoio
U_CORDA = -190.0                   # corda em repouso
P_BRACO = (22.0, 245.0)            # eixo do braço de cima (o de baixo é espelhado)
L_FLECHA = 720.0
R_FLECHA = 3.9
W_JANELA = 5.2                     # a janela de mira corta o lado esquerdo até aqui
V_OMBRO = 233.5                    # onde acaba o corpo do punho e começa o assento do braço
MAD = 'madeira_arco'


def _catmull(pts, n=14):
    Q = np.array(pts, float)
    Q = np.vstack([Q[0] * 2 - Q[1], Q, Q[-1] * 2 - Q[-2]])
    out = []
    for i in range(1, len(Q) - 2):
        p0, p1, p2, p3 = Q[i - 1], Q[i], Q[i + 1], Q[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(Q[-2])
    return np.array(out)


# linha do meio do braço de cima (de lado), do pé à ponta recurva
LINHA = _catmull([(22, 235), (20, 290), (4, 360), (-30, 440), (-80, 520), (-130, 585), (-166, 628), (-180, 660), (-172, 690),
                  (-148, 712), (-118, 724)])
_D = np.gradient(LINHA, axis=0)
_D /= np.linalg.norm(_D, axis=1)[:, None]
NOR = np.stack([-_D[:, 1], _D[:, 0]], 1)                 # aponta para a barriga (lado do arqueiro)
_L = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(LINHA, axis=0), axis=1))])
COMP = float(_L[-1])
S = _L / COMP
ESP = lambda s: 5.2 - 2.2 * s                            # meia espessura
LARG = lambda s: 20.5 - 12.5 * s ** 1.3                  # meia largura
K_ENC = int(np.argmin(LINHA[:, 0]))                      # onde a corda deixa a barriga
N_CORDA = LINHA[K_ENC] + NOR[K_ENC] * (ESP(K_ENC / (len(LINHA) - 1)) + 1.2)
K_ENT = len(LINHA) - 5                                   # entalhes da corda na ponta


def _interp(pts, v):
    """Curva suave por pontos de controle (v crescente): Chaikin e interpolação."""
    q = [tuple(map(float, p)) for p in pts]
    for _ in range(3):
        r = [q[0]]
        for a, b in zip(q, q[1:]):
            r += [(0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]), (0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1])]
        q = r + [q[-1]]
    q = np.array(q)
    return float(np.interp(v, q[:, 0], q[:, 1]))


# contorno do punho de lado: frente (lado do alvo) e trás (lado do arqueiro), por altura
FRENTE = [(-272, 30), (-233, 33), (-180, 42), (-130, 46), (-90, 43.5), (-62, 33), (-40, 24), (-12, 21), (10, 24.5), (24, 32), (60, 44),
          (110, 46), (160, 43), (200, 36), (233, 33), (272, 30)]
TRAS = [(-272, -4), (-233, -7), (-170, -9), (-110, -13), (-86, -20), (-66, -31), (-48, -37), (-30, -35.5), (-10, -27.5), (7, -20.5),
        (22, -17), (40, -15), (70, -13), (110, -12), (170, -10), (233, -7), (272, -4)]
MEIA = [(-272, 19.5), (-240, 19.5), (-205, 13.4), (-75, 13.4), (-36, 14.8), (5, 13.6), (25, 13.4), (205, 13.4), (240, 19.5), (272, 19.5)]
EXPO = [(-272, 3.2), (-100, 3.0), (-60, 2.35), (-10, 2.35), (20, 3.0), (272, 3.2)]


def _gira_u(o, graus, v0=V_FLECHA):
    """Gira a malha em torno do eixo da flecha (reta em u por v = v0, w = 0)."""
    c = P(0, v0, 0)
    o.data.transform(Matrix.Translation(c) @ Matrix.Rotation(math.radians(graus), 4, 'Y') @ Matrix.Translation(-c))
    return o


# ------------------------------------------------------------------ punho
def punho():
    aneis = []
    for v in np.linspace(-272, 272, 137):
        uf, ur, hw, e = _interp(FRENTE, v), _interp(TRAS, v), _interp(MEIA, v), _interp(EXPO, v)
        aneis.append([P((uf + ur) / 2 + x, v, w) for x, w in superelipse((uf - ur) / 2, hw, n=52, e=e)])
    c = loft(aneis, MAD)
    cortes = []
    # janela de mira: tira o lado esquerdo acima da prateleira; em cima sobe em rampa
    cortes.append(extr([(-40, V_FLECHA - 5.4), (W_JANELA - 3, V_FLECHA - 5.4), (W_JANELA, V_FLECHA - 2.4), (W_JANELA, 150), (-2, 168),
                        (-16, 178), (-40, 182)], -60, 80, MAD, plane='wv'))
    # assentos dos braços: plano na frente, do ombro até a ponta do punho
    b0 = LINHA[0] + NOR[0] * ESP(0)
    k1 = int(np.argmin(abs(LINHA[:, 1] - 285)))
    b1 = LINHA[k1] + NOR[k1] * ESP(S[k1])
    for s in (1, -1):
        cortes.append(extr([(b0[0] - 0.15, s * V_OMBRO), (90, s * V_OMBRO), (90, s * 300), (b1[0] - 0.15, s * 300)][::s], -40, 40, MAD))
    cut(c, cortes)
    o = [bevel(c, 1.6, 3, 28)]
    # buchas de latão do lado direito (mira e aljava) e bucha do estabilizador na frente
    for (u, v) in ((12, 100), (12, 130), (12, -150), (12, 200)):
        o.append(lathe([(0, 3.3), (2.5, 3.3), (2.5, 1.7), (1.0, 1.7), (1.0, 0)], 'latao', n=20, c0=(u, v, 11.3), eixo=(0, 0, 1)))
    o.append(lathe([(0, 5.4), (3.6, 5.4), (4.2, 4.8), (4.2, 2.6), (1.6, 2.6), (1.6, 0)], 'latao', n=24, c0=(39.9, -90, 0)))
    # feltro da prateleira e placa de couro onde a flecha encosta
    o.append(bevel(extr(ret_arred(-12.5, 25, -9.5, W_JANELA - 0.3, 3.0, 4), V_FLECHA - 5.5, V_FLECHA - R_FLECHA - 0.05, 'feltro', plane='uw'), 0.5, 2, 40))
    o.append(bevel(extr(ret_arred(-9, 15, V_FLECHA - 3.6, V_FLECHA + 19, 2.5, 4), R_FLECHA + 0.1, W_JANELA + 0.2, 'couro_arco'), 0.4, 1, 40))
    # manípulos que prendem os braços (arruela de aço e botão recartilhado)
    for s in (1, -1):
        o.append(lathe([(0, 10.5), (1.4, 10.5), (1.4, 9.2)], 'inox', n=32, c0=(27.3, s * 258, 0)))
        o.append(lathe([(1.4, 9.2), (9.0, 9.2), (10.6, 7.6), (10.6, 3.4), (7.2, 3.4), (7.2, 0)], 'fosf', n=40, c0=(27.3, s * 258, 0),
                       lobes=0.07, lobe_min=7.0))
    o.append(texto('RC 240817', 2.6, 16, -152, -13.36, mat='tinta_ouro'))
    o.append(texto('62 pol   40 lb', 2.6, 16, -160, -13.36, mat='tinta_ouro'))
    return parte('punho', o, origem=(0, 0, 0), grupo='A', suave=38)


# ------------------------------------------------------------------ braços e corda
def _larg(i):
    """Meia largura com o pé e a ponta arredondados."""
    b = LARG(S[i])
    d0, d1 = _L[i], COMP - _L[i]
    if d0 < 12:
        b *= math.sqrt(max(0.02, 1 - ((12 - d0) / 12.3) ** 2))
    if d1 < 7:
        b *= math.sqrt(max(0.02, 1 - ((7 - d1) / 7.2) ** 2))
    return b


def _secao(a, b, k=3):
    """Retângulo de cantos arredondados: x = para a barriga, y = largura (w)."""
    c = min(0.9, a * 0.45, b * 0.45)
    out = []
    for (cx, cy, a0) in ((a - c, b - c, 0), (-a + c, b - c, 90), (-a + c, -b + c, 180), (a - c, -b + c, 270)):
        for i in range(k + 1):
            t = math.radians(a0 + 90 * i / k)
            out.append((cx + c * math.cos(t), cy + c * math.sin(t)))
    return out


def _pt(i, x, w, sv):
    p = LINHA[i] + NOR[i] * x
    return P(p[0], sv * p[1], w)


def _pt3(i, x, w, sv):
    p = LINHA[i] + NOR[i] * x
    return (p[0], sv * p[1], w)


def _texto_braco(s, tam, d0, sv):
    """Letras deitadas na barriga do braço (o lado que o arqueiro vê), lidas ao longo dele."""
    cu = bpy.data.curves.new('t', 'FONT')
    cu.body = s
    cu.size = tam * MM
    cu.align_x = 'LEFT'
    cu.resolution_u = 2
    tmp = bpy.data.objects.new('t', cu)
    bpy.context.scene.collection.objects.link(tmp)
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(tmp)
    for vv in me.vertices:
        x, y = vv.co.x / MM, vv.co.y / MM
        d = d0 + x
        i = int(np.clip(np.searchsorted(_L, d), 1, len(_L) - 1))
        t = (d - _L[i - 1]) / (_L[i] - _L[i - 1])
        p = LINHA[i - 1] * (1 - t) + LINHA[i] * t
        n = NOR[i - 1] * (1 - t) + NOR[i] * t
        e = ESP(d / COMP) + 0.03
        vv.co = P(p[0] + n[0] * e, sv * (p[1] + n[1] * e), -sv * (y - tam * 0.35))
    o = bpy.data.objects.new('t', me)
    bpy.context.scene.collection.objects.link(o)
    me.materials.clear()
    me.materials.append(M('tinta'))
    return o


def braco(sv=1):
    nome = 'braco_cima' if sv > 0 else 'braco_baixo'
    n = len(LINHA)
    aneis = [[_pt(i, x, w, sv) for x, w in _secao(ESP(S[i]), _larg(i))] for i in range(n)]
    c = loft(aneis if sv > 0 else [r[::-1] for r in aneis], 'fibra_arco')
    # reforço da ponta, por fora (lado do alvo): camadas claras que afinam para o braço
    i0 = int(np.searchsorted(_L, COMP - 62))
    alt = lambda i: 2.4 * min(1.0, (_L[i] - _L[i0]) / 30.0) * min(1.0, 0.35 + (COMP - _L[i]) / 6.0) + 0.05
    ref = [[_pt(i, -ESP(S[i]) - alt(i) / 2 + x + 0.25, w, sv) for x, w in _secao(alt(i) / 2 + 0.25, max(0.6, _larg(i) - 0.5), 2)] for i in range(i0, n)]
    r = loft(ref if sv > 0 else [q[::-1] for q in ref], 'fenolico')
    # entalhes da corda dos dois lados da ponta
    e = K_ENT
    for alvo in (c, r):
        cut(alvo, [cyl(_pt3(e, -12, s * (_larg(e) + 0.5), sv), _pt3(e, 12, s * (_larg(e) + 0.5), sv), 2.1, 'fibra_arco', n=16) for s in (1, -1)])
    pintar(c, 'lamina_bordo', lambda p, nn: abs(nn[2]) > 0.985)
    o = [c, r]
    # o pedaço da corda que dorme na barriga, do encosto até o laço nos entalhes
    cam = [_pt3(i, ESP(S[i]) + 1.25, 0, sv) for i in range(K_ENC, e + 1)]
    o.append(fio(cam, 1.3, 'corda', fechado=False, res=2))
    a, b = ESP(S[e]) + 1.25, _larg(e) - 1.5
    laco = [_pt3(e, x, w, sv) for x, w in ((a, 0), (a, b), (-a - 1.6, b), (-a - 1.6, -b), (a, -b))]
    o.append(fio(caminho_arred(laco[1:], 1.6, 3), 1.3, 'corda_reforco', fechado=True, res=2))
    o.append(_texto_braco('RECURVO 62 pol' if sv > 0 else '40 lb a 28 pol', 5.0, 95, sv))
    return parte(nome, o, origem=(P_BRACO[0], sv * P_BRACO[1], 0), grupo='B', suave=40)


def corda(sv=1):
    """Metade da corda: do encosto no braço ao ponto de encaixe da flecha, com reforço no meio."""
    n0 = (float(N_CORDA[0]), sv * float(N_CORDA[1]), 0.0)
    c = (U_CORDA, V_FLECHA, 0.0)
    d = Vector(c) - Vector(n0)
    d.normalize()
    m = tuple(Vector(c) - d * 82)
    o = [cyl(n0, m, 1.3, 'corda', n=12), cyl(m, c, 1.75, 'corda_reforco', n=12)]
    if sv > 0:                                               # anel de latão logo acima da flecha
        o.append(lathe([(0, 1.7), (0, 2.5), (0.5, 2.8), (2.4, 2.8), (2.9, 2.5), (2.9, 1.7)], 'latao', n=16, c0=(U_CORDA, V_FLECHA + 4.7, 0),
                       eixo=(0, 1, 0), anel=True))
    return parte('corda_cima' if sv > 0 else 'corda_baixo', o, origem=n0, grupo='B', suave=40)


# ------------------------------------------------------------------ flecha
def flecha():
    """Flecha de carbono com 3 penas de plástico e ponta de caça de 3 lâminas; entalhe em (U_CORDA, V_FLECHA)."""
    u0, v0, L, r = U_CORDA, V_FLECHA, L_FLECHA, R_FLECHA
    c0 = (u0, v0, 0)
    nock = lathe([(-1.2, 0), (-1.2, 2.6), (0.5, 3.7), (4.5, 4.15), (10, 4.15), (11.5, r), (11.5, 0)], 'nock', n=20, c0=c0)
    cut(nock, box(u0 - 3, u0 + 4.6, v0 - 8, v0 + 8, -1.85, 1.85, 'nock'))
    o = [bevel(nock, 0.3, 1, 40)]
    o.append(lathe([(11.5, 0), (11.5, r), (L - 30, r), (L - 30, 0)], 'carbono', n=20, c0=c0))
    o.append(lathe([(17, r + 0.02), (17, r + 0.12), (108, r + 0.12), (108, r + 0.02)], 'envoltorio', n=20, c0=c0, anel=True))
    o.append(lathe([(L - 31.5, 0), (L - 31.5, r + 0.25), (L - 26, r + 0.25), (L - 24.5, r - 0.4), (L - 24.5, 0)], 'aluminio_flecha', n=20, c0=c0))
    # penas: uma branca para fora (lado esquerdo), duas laranja
    perfil = [(22, 0), (24, 5.5), (30, 10.2), (40, 12.6), (56, 12.9), (76, 10.2), (92, 5.0), (99, 0)]
    for k in range(3):
        pena = extr([(u0 + a, v0 + r - 0.3 + b) for a, b in perfil], -0.5, 0.5, 'pena_branca' if k == 0 else 'pena_laranja')
        o.append(_gira_u(bevel(pena, 0.18, 1, 40), -90 + 120 * k))
    # ponta de caça: corpo de aço e 3 lâminas vazadas
    o.append(lathe([(L - 24.5, 0), (L - 24.5, 3.4), (L - 21, 4.3), (L - 12, 4.3), (L - 4, 3.4), (L + 12, 0)], 'inox', n=20, c0=c0))
    for k in range(3):
        lam = extr([(u0 + L - 23, v0 + 2.0), (u0 + L + 7.5, v0 + 1.6), (u0 + L - 14, v0 + 13.6), (u0 + L - 22, v0 + 12.4)], -0.45, 0.45, 'aco_lamina')
        cut(lam, extr([(u0 + L - 20, v0 + 5.4), (u0 + L - 6.5, v0 + 5.1), (u0 + L - 14.8, v0 + 10.4), (u0 + L - 20, v0 + 10.0)], -2, 2, 'aco_lamina'))
        o.append(_gira_u(lam, -30 + 120 * k))
    return parte('flecha', o, origem=c0, grupo='A', suave=40)


def montar():
    punho()
    for sv in (1, -1):
        braco(sv)
        corda(sv)
    flecha()
