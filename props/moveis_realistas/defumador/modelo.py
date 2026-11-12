"""Defumador de tábuas: caixa alta de tábuas com frestas sobre uma base de tijolos com boca de fogo na frente,
telhado de zinco de duas águas, porta de tábuas com travessas e dobradiças de cinta (nó `porta`, dobradiça em
DOBRA) e, dentro, duas varas com carne e linguiça penduradas.
Medidas em mm, coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente."""
import math
import lib
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte

X, Z = 400, 350             # meia largura e meia profundidade da caixa
BASE = 290                  # em cima dos tijolos
H = 1700                    # em cima da caixa
DOBRA = (X, BASE + 10, Z + 5)
FOGO_Y, FOGO_Z = 90, 150


def _torno(prof, mat, x=0, y=0, z=0, n=24, eixo=(0, 1, 0)):
    """Perfil em (raio, altura ao longo do eixo); as pontas fecham no eixo."""
    return lib.lathe([(h, r) for r, h in prof], mat, n=n, c0=G(x, y, z), eixo=G(*eixo))


def _fio(pts, r, mat, fechado=False, res=2):
    return lib.fio([G(*p) for p in pts], r, mat, fechado=fechado, res=res)


def _tij(x0, x1, y0, z0, z1):
    return bevel(caixa(x0, x1, y0, y0 + 55, z0, z1, 'tijolo'), 3.0, seg=1)


def _base():
    p = []
    for k in range(5):
        y = k * 58
        d = 6 if k % 2 else 0
        for i in range(4):                                                                               # parede de trás
            p.append(_tij(-X + i * 200 + 2 - d * (i % 2), -X + i * 200 + 198 - d * (i % 2), y, -Z, -Z + 90))
        for sx in (-1, 1):                                                                               # laterais
            xa, xb = (X - 90, X) if sx > 0 else (-X, -X + 90)
            for i in range(3):
                p.append(_tij(xa, xb, y, -Z + 94 + i * 172 + d, -Z + 94 + i * 172 + 168 + d * 0.5))
        if k < 3:                                                                                        # frente: dois pilares e a boca de fogo
            p.append(_tij(-X + 94, -X + 284, y, Z - 90, Z))
            p.append(_tij(X - 284, X - 94, y, Z - 90, Z))
        else:
            for i in range(3):
                p.append(_tij(-X + 94 + i * 205 + d * 0.5, -X + 94 + i * 205 + 200, y, Z - 90, Z))
    p.append(caixa(-X + 100, X - 100, 172, 177, Z - 88, Z - 2, 'ferrugem', 1.0))                          # verga de chapa sobre a boca
    return p


def _caixa():
    p = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            p.append(caixa(sx * X - (45 if sx > 0 else 0), sx * X + (0 if sx > 0 else 45), BASE, H, sz * Z - (45 if sz > 0 else 0), sz * Z + (0 if sz > 0 else 45), 'pinho_y', 2.5))
    k = 0
    y = BASE + 6
    while y + 125 <= H:
        d = (k * 5) % 9 - 4
        for sx in (-1, 1):
            p.append(caixa(sx * X + (0 if sx > 0 else -20), sx * X + (20 if sx > 0 else 0), y, y + 125, -Z - 6 + d, Z + 4 + d, 'fumo_z', 2.0))
        p.append(caixa(-X - 14 + d, X + 12 + d, y, y + 125, -Z - 20, -Z, 'fumo_x', 2.0))
        y += 139
        k += 1
    for sx in (-1, 1):                                                                                   # oitões fechados
        p.append(perfil([(-Z - 6, H), (Z + 6, H), (0, H + 118)], sx * X - 10, sx * X + 10, 'fumo_z', 1.5))
    p.append(caixa(-X, X, H - 60, H, Z - 22, Z, 'fumo_x', 2.0))                                          # verga da porta
    return p


def _telhado():
    a = [(-Z - 110, H - 22), (0, H + 136), (Z + 110, H - 22), (Z + 110, H - 28), (0, H + 129), (-Z - 110, H - 28)]
    p = [perfil(a, -X - 70, X + 70, 'zinco', 0.6),
         perfil([(-70, H + 122), (0, H + 146), (70, H + 122), (70, H + 118), (0, H + 141), (-70, H + 118)], -X - 76, X + 76, 'zinco', 0.6)]   # cumeeira
    for sz in (-1, 1):                                                                                   # caibros
        p.append(perfil([(sz * 20, H + 118), (sz * (Z + 96), H - 30), (sz * (Z + 96), H - 62), (sz * 20, H + 86)], -X - 40, -X - 10, 'pinho_z', 1.5))
        p.append(perfil([(sz * 20, H + 118), (sz * (Z + 96), H - 30), (sz * (Z + 96), H - 62), (sz * 20, H + 86)], X + 10, X + 40, 'pinho_z', 1.5))
    return p


def _porta():
    z0 = Z + 2
    p = []
    for i in range(6):
        d = (i * 7) % 11 - 5
        p.append(caixa(-X + 3 + i * 133, -X + 3 + i * 133 + 129, BASE + 14 + d, H - 66 + d * 0.4, z0, z0 + 20, 'fumo_y', 2.0))
    for y in (BASE + 190, H - 330):                                                                      # travessas e cintas
        p.append(caixa(-X + 26, X - 26, y, y + 100, z0 + 20, z0 + 40, 'fumo_x', 2.0))
        p.append(caixa(X - 330, X + 2, y + 34, y + 66, z0 + 40, z0 + 44, 'ferro_preto', 1.0))
        p.append(cil((X + 4, y + 22, z0 + 42), (X + 4, y + 78, z0 + 42), 8, 'ferro_preto', n=10))
        for xb in (X - 300, X - 180, X - 60):
            p.append(cil((xb, y + 50, z0 + 44), (xb, y + 50, z0 + 47), 6, 'ferro_preto', n=8))
    ya, yb = BASE + 290, H - 330                                                                         # escora em diagonal
    p.append(frente([(-X + 30, ya), (-X + 120, ya), (X - 30, yb), (X - 120, yb)], z0 + 20, z0 + 38, 'fumo_y', 2.0))
    p.append(caixa(-X + 30, -X + 150, 1010, 1050, z0 + 20, z0 + 34, 'ferro_preto', 1.5))                   # ferrolho
    p.append(cil((-X + 20, 1030, z0 + 38), (-X + 170, 1030, z0 + 38), 7, 'aco_ferramenta', n=10))
    p.append(cil((-X + 120, 1030, z0 + 38), (-X + 120, 1030, z0 + 62), 6, 'aco_ferramenta', n=8))
    return p


def _peca(x, y, z, k):
    """Uma peça pendurada num barbante: manta de carne, pernil ou linguiça."""
    p = [cil((x, y, z), (x, y - 70, z), 1.6, 'pano_cru', n=5)]
    t = k % 3
    if t == 0:                                                                                           # manta
        p.append(bevel(caixa(x - 55, x + 55, y - 330, y - 66, z - 14, z + 14, 'carne_seca'), 12.0, seg=2))
    elif t == 1:                                                                                         # pernil
        p.append(_torno([(0, 0), (22, 0), (30, 40), (62, 150), (70, 220), (52, 270), (0, 285)], 'carne_seca', x, y - 70, z, n=10, eixo=(0, -1, 0)))
    else:                                                                                                # linguiça em volta
        p.append(_fio([(x + 46 * math.cos(i * math.pi / 8), y - 190 + 120 * math.sin(i * math.pi / 8) , z + 8 * math.sin(i * math.pi / 4)) for i in range(16)], 14.0, 'carne_seca', fechado=True))
    return p


def _dentro():
    p = []
    k = 0
    for j, (y, zz) in enumerate(((1560, -120), (1560, 120), (1180, 0))):
        p.append(cil((-X + 10, y, zz), (X - 10, y, zz), 13, 'crua_x', n=8))
        for i in range(4):
            p += _peca(-270 + i * 180 + (j % 2) * 40, y - 12, zz, k)
            k += 1
    return p


def _fogo():
    """Cinza e toras meio queimadas na base, à mostra pela boca de fogo."""
    p = [caixa(-X + 92, X - 92, 0, 14, -Z + 92, Z - 4, 'cinza_fogo', 3.0)]
    for k, (x, z, a, r) in enumerate(((-60, 120, 0.3, 42), (60, 150, -0.5, 36), (0, 40, 1.4, 46), (-120, -40, 0.9, 34))):
        dx, dz = 150 * math.cos(a), 150 * math.sin(a)
        p.append(cil((x - dx, 18 + r + k * 6, z - dz), (x + dx, 18 + r + k * 10, z + dz), r, 'carvao', n=8, r1=r * 0.85))
    return p


def _brasa():
    p = []
    for k in range(9):
        a = k * 2.4
        rr = 30 + (k * 37) % 110
        p.append(bevel(caixa(rr * math.cos(a) - 22, rr * math.cos(a) + 22, 14, 34 + (k % 3) * 8, FOGO_Z - 40 + rr * 0.6 * math.sin(a) - 20, FOGO_Z - 40 + rr * 0.6 * math.sin(a) + 20, 'carvao'), 8.0, seg=1))
    return p


def montar():
    parte('base', _base(), origem=G(0, 0, 0), grupo='A')
    parte('caixa', _caixa(), origem=G(0, 0, 0), grupo='A')
    parte('telhado', _telhado(), origem=G(0, 0, 0), grupo='B')
    parte('porta', _porta(), origem=G(*DOBRA), grupo='B')
    parte('dentro', _dentro(), origem=G(0, 0, 0), grupo='C')
    parte('fogo', _fogo(), origem=G(0, 0, 0), grupo='C')
    parte('brasa', _brasa(), origem=G(0, 0, 0), grupo='C')
