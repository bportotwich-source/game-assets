"""Forma do sedã Rumo: perfis, seções e a casca da carroceria dividida em painéis.

Medidas (m): comprimento da carroceria 4,34 (4,46 com para-choques), largura 1,68 (sem retrovisores), altura 1,39,
entre-eixos 2,55, bitola 1,42, rodas 185/70 aro 14 (raio 0,305). Pivô no chão, no meio dos eixos. Frente +Z, esquerda +X.
"""
import math
import numpy as np, trimesh
from shapely.geometry import Polygon, box as sbox, LineString
from shapely.ops import unary_union
from forma import (chaikin, anel_xy, loft, menos, uniao, inter, prisma_zy, prisma_xz, caixa, cil_x, espelhar_x)

ZF, ZR = 2.10, -2.24          # frente e traseira da carroceria (sem para-choques)
HW = 0.84                     # meia largura
EIXO_D, EIXO_T = 1.27, -1.28  # eixos
R_RODA = 0.305; Y_RODA = 0.305; X_RODA = 0.71
R_CAIXA = 0.375; Y_CAIXA = 0.33
ZWS, ZBL = 0.64, -1.68        # base do para-brisa e do vidro traseiro
FOLGA = 0.004                 # vão entre painéis
Y_TETO_CORTE = 1.305          # onde a porta encontra o teto (calha)
T = 0.02                      # espessura da chapa (visual)


def _i(z, tab):
    zs, ys = zip(*tab); return float(np.interp(z, zs, ys))


def yt(z):  # topo da carroceria de baixo: capô, linha de cintura, tampa do porta-malas
    return _i(z, [(-2.24, 0.885), (-2.2, 0.945), (-2.12, 0.968), (-1.95, 0.978), (-1.7, 0.98), (-1.2, 0.968), (-0.4, 0.952),
                  (0.3, 0.935), (0.64, 0.925), (0.8, 0.905), (1.2, 0.86), (1.6, 0.81), (1.85, 0.78), (2.0, 0.755), (2.07, 0.73), (2.10, 0.70)])


def yb(z):  # fundo
    return _i(z, [(-2.24, 0.37), (-2.18, 0.31), (-2.06, 0.25), (-1.85, 0.228), (-1.6, 0.225), (1.65, 0.225), (1.85, 0.25), (2.0, 0.29), (2.10, 0.33)])


def fx(z):  # arredondado das pontas em planta (superelipse)
    d = z / ZF if z > 0 else z / ZR
    d = min(abs(d), 1.0)
    return max((1 - d ** 9) ** (1 / 9), 0.02)


def hw(z):  # meia largura (a frente é um pouco mais estreita)
    return HW - 0.025 * max(0.0, z / ZF) ** 2 - 0.012 * max(0.0, z / ZR) ** 2


def ytop(z):  # perfil do teto: para-brisa, teto, vidro traseiro
    return _i(z, [(-1.68, 0.975), (-1.56, 1.035), (-1.42, 1.12), (-1.27, 1.215), (-1.12, 1.31), (-1.0, 1.36), (-0.8, 1.383),
                  (-0.5, 1.39), (-0.32, 1.383), (-0.22, 1.365), (-0.08, 1.31), (0.12, 1.225), (0.34, 1.12), (0.52, 1.02), (0.64, 0.93)])


def meio_baixo(z, enc=0.0):
    """Meio perfil da carroceria de baixo em z (enc = encolhe para a casca de dentro)."""
    w = hw(z) - enc; b = yb(z) + enc; t = yt(z) - enc
    vinco = min(0.615, t - 0.13); larga = min(0.50, vinco - 0.07)
    pts = [(0, b), (w - 0.17, b), (w - 0.07, b + 0.012), (w - 0.03, b + 0.05), (w - 0.008, b + 0.13), (w, larga), (w, vinco - 0.02),
           (w - 0.002, vinco), (w - 0.006, vinco + 0.006), (w - 0.018, t - 0.10), (w - 0.032, t - 0.045), (w - 0.07, t - 0.013),
           (w - 0.16, t - 0.003), (0, t)]
    return pts


def anel_baixo(z, enc=0.0):
    a = anel_xy(meio_baixo(z, enc), z)
    a = chaikin(a[:, :2], 2)
    a[:, 0] *= fx(z)
    return np.column_stack([a, np.full(len(a), z)])


def zs_amostras(z0, z1, n=110):
    u = np.linspace(0, 1, n); s = (1 - np.cos(np.pi * u)) / 2
    s = 0.55 * s + 0.45 * u
    return z0 + (z1 - z0) * s


def corpo_baixo(enc=0.0):
    zs = zs_amostras(ZR + enc * 1.2, ZF - enc * 1.2)
    return loft([anel_baixo(z, enc) for z in zs])


def larg_cintura(z):
    """Meia largura do topo da carroceria (onde a cabine apoia)."""
    return (hw(z) - 0.062) * fx(z)


def meio_cabine(z, enc=0.0, desce=0.0):
    yb_ = yt(z) - 0.03 - (0.06 if enc else 0.0) - desce
    yt_ = max(ytop(z) - enc, yt(z) + 0.004)
    h = yt_ - (yt(z) - 0.03)
    wb = larg_cintura(z) - enc
    wt = wb - 0.13 * min(h, 0.46) / 0.46
    pts = [(0, yb_), (wb, yb_)] + ([(wb, yt(z) - 0.03)] if enc else []) + [(wb - 0.006, yt(z) + 0.02), (wt + 0.035, yt_ - 0.055), (wt + 0.012, yt_ - 0.02),
           (wt - 0.03, yt_ - 0.004), (wt - 0.2, yt_), (0, yt_ + 0.004)]
    return pts


def anel_cabine(z, enc=0.0, desce=0.0):
    a = anel_xy(meio_cabine(z, enc, desce), z)
    a = chaikin(a[:, :2], 2)
    return np.column_stack([a, np.full(len(a), z)])


def corpo_cabine(enc=0.0, desce=0.0, pontas=None):
    p = (0.03 if enc else 0) if pontas is None else pontas
    zs = zs_amostras(ZBL + p, ZWS - p, 70)
    return loft([anel_cabine(z, enc, desce) for z in zs])


def quina_cabine(z):
    """(x, y) da quina lateral-superior da cabine em z (por onde passam as colunas)."""
    h = ytop(z) - (yt(z) - 0.03); wb = larg_cintura(z); wt = wb - 0.13 * min(h, 0.46) / 0.46
    return wt + 0.02, ytop(z) - 0.04


# ---------------------------------------------------------------------------- janelas (plano z, y)
def _curva_coluna_a(desloc):
    pts = []
    for z in np.linspace(ZWS, -0.36, 40):
        y = min(ytop(z) - 0.075, Y_TETO_CORTE - 0.035)
        pts.append((z - desloc, y))
    return pts


def janela_dianteira(borda=0.0):
    zf_ = -0.40 - 0.045 + borda
    top = [(z, min(y + borda, Y_TETO_CORTE - 0.035 + borda)) for (z, y) in _curva_coluna_a(0.075 - borda)]
    top = [(z, y) for (z, y) in top if z > zf_]
    pg = Polygon([(zf_, yt(zf_) + 0.012 - borda)] + [(zf_, top[-1][1])] + top[::-1] + [(top[0][0], yt(top[0][0]) + 0.012 - borda)])
    lim = Polygon([(z, yt(z) + 0.012 - borda) for z in np.linspace(1.0, -1.0, 30)] + [(-1.0, 2), (1.0, 2)])
    return pg.buffer(0).intersection(lim)


def janela_traseira(borda=0.0):
    z0, z1 = -0.50 - 0.045 + borda, -1.27 - borda
    top = []
    for z in np.linspace(z0, z1, 30):
        top.append((z, min(Y_TETO_CORTE - 0.035, ytop(z + 0.1) - 0.08) + borda))
    bot = [(z, yt(z) + 0.012 - borda) for z in np.linspace(z1, z0, 10)]
    return Polygon(top + bot).buffer(0)


def janela_terceira(borda=0.0):
    z0 = -1.325 + borda
    top = []
    for z in np.linspace(z0, -1.7, 40):
        y = min(Y_TETO_CORTE - 0.035, ytop(z + 0.075) - 0.075) + borda
        if y <= yt(z) + 0.03: break
        top.append((z, y))
    bot = [(z, yt(z) + 0.012 - borda) for z in np.linspace(top[-1][0], z0, 8)]
    return Polygon(top + bot).buffer(0)


def regiao_porta(qual, lado=1, g=0.0):
    """Regiao (solido) de uma porta: parte de baixo (chapa) + moldura da janela. lado = +1 esquerda, -1 direita.
    g = folga (a regiao cresce g para todo lado: e o vao cortado na carroceria)."""
    if qual == 'd':
        z0, z1 = 0.605, -0.40
        jan = janela_dianteira(0.032)
    else:
        z0, z1 = -0.50, -1.27
        jan = janela_traseira(0.032)
    baixo = Polygon([(z1, 0.305), (z0, 0.305), (z0, yt(z0) + 0.05), (z1, yt(z1) + 0.05)])
    zona = unary_union([baixo, jan]).intersection(sbox(min(z0, z1), 0.0, max(z0, z1), Y_TETO_CORTE))
    if g: zona = zona.buffer(g, join_style=2)
    m = prisma_zy(zona, 0.40, 1.2)
    return m if lado > 0 else espelhar_x(m)


def _planta(z0, z1, rec, minfx=0.0, n=30):
    zs = np.linspace(z0, z1, n)
    return Polygon([((hw(z) - rec) * max(fx(z), minfx), z) for z in zs] + [(-(hw(z) - rec) * max(fx(z), minfx), z) for z in zs[::-1]])


def regiao_capo(g=0.0):
    pg = _planta(0.70, 2.035, 0.085)
    if g: pg = pg.buffer(g, join_style=2)
    return prisma_xz(pg, 0.55, 2.0)


def regiao_tampa(g=0.0):
    pg = _planta(-1.75, -2.5, 0.085, 0.6).intersection(sbox(-2, -2.5, 2, -1.75))
    if g: pg = pg.buffer(g, join_style=2)
    deck = prisma_xz(pg, yt(-2.0) - 0.06 - g, 2.0)
    face = caixa(-0.50 - g, 0.50 + g, 0.64 - g, 2.0, -2.5, -2.10 + g)
    return uniao([deck, face])


def regiao_paralama(lado=1, g=0.0):
    pg = Polygon([(0.605 + 0.004, 0.305), (2.3, 0.305), (2.3, 2.0), (0.605 + 0.004, 2.0)])
    if g: pg = pg.buffer(g, join_style=2)
    m = prisma_zy(pg, 0.66 - g, 1.2)
    return m if lado > 0 else espelhar_x(m)




def z_ponta(x, frente=True, k=0.985):
    """z da superficie da frente (ou da traseira) na meia largura x (planta)."""
    a, b = (0.0, ZF) if frente else (ZR, 0.0)
    f = lambda z: (hw(z) - 0.0) * fx(z) * k - x
    lo, hi = (1.0, ZF) if frente else (ZR, -1.0)
    for _ in range(50):
        m = (lo + hi) / 2
        if frente: lo, hi = (m, hi) if f(m) > 0 else (lo, m)
        else: lo, hi = (lo, m) if f(m) > 0 else (m, hi)
    return (lo + hi) / 2


def x_lado(z, k=0.99):
    return hw(z) * fx(z) * k
