"""Alambique de panela: fornalha de tijolos aberta na frente, panelão de alumínio com a tampa vedada com barro,
cano de cobre que sobe da tampa, atravessa e desce em serpentina dentro de um tambor de 200 L cheio de água fria,
e sai embaixo pingando num garrafão de vidro. Ladrão de PVC na boca do tambor e termômetro na tampa.
Medidas em mm, coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente (a boca da fornalha)."""
import math
import bpy, bmesh
import lib
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte

FX = -430                   # meio da fornalha
DX = 190                    # meio do tambor
R, ALT = 290, 880
FIADAS = 4
TOPO_F = FIADAS * 59        # em cima dos tijolos
PR, PH = 176, 250           # panelão
AGUA = 800
SX, SY = DX + R, 170        # onde o cano sai do tambor
GX = SX + 118               # garrafão
FOGO_Y, FOGO_Z = 90, 30


def _torno(prof, mat, x=0, y=0, z=0, n=24, eixo=(0, 1, 0), **k):
    """Perfil em (raio, altura ao longo do eixo); as pontas fecham no eixo."""
    return lib.lathe([(h, r) for r, h in prof], mat, n=n, c0=G(x, y, z), eixo=G(*eixo), **k)


def _sem_tampas(o, n):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if len(f.verts) >= n], context='FACES')
    bm.to_mesh(o.data)
    bm.free()
    return o


def _fio(pts, r, mat, fechado=False, res=2):
    return lib.fio([G(*p) for p in pts], r, mat, fechado=fechado, res=res)


def _cano(pts, r, mat, raio=40, n=5, res=2):
    """Cano com as curvas arredondadas."""
    return lib.fio(lib.caminho_arred([G(*p) for p in pts], raio, n=n, fechado=False), r, mat, fechado=False, res=res)


def _tij(x0, x1, y0, z0, z1):
    return bevel(caixa(x0, x1, y0, y0 + 55, z0, z1, 'tijolo'), 3.0, seg=1)


def _fornalha():
    x0, x1, z0, z1 = FX - 235, FX + 235, -205, 205
    p = []
    for k in range(FIADAS):
        y = k * 59
        d = (k * 5) % 7 - 3
        larg = (190, 190, 82) if k % 2 == 0 else (82, 190, 190)                                           # parede de trás
        x = x0
        for w in larg:
            p.append(_tij(x + 2 + d * 0.5, x + w - 2 + d * 0.5, y, z0, z0 + 90))
            x += w + 3
        comp = (190, 122) if k % 2 == 0 else (122, 190)                                                   # laterais
        for sx in (-1, 1):
            xa, xb = (x1 - 90, x1) if sx > 0 else (x0, x0 + 90)
            z = z0 + 93
            for w in comp:
                p.append(_tij(xa - d * 0.4 * sx, xb - d * 0.4 * sx, y, z + 1, z + w - 1))
                z += w + 2
    for z in (-95, 60):                                                                                   # dois ferros onde a panela senta
        p.append(caixa(x0 + 30, x1 - 30, TOPO_F - 2, TOPO_F + 10, z - 9, z + 9, 'ferro_preto', 2.0))
    p.append(caixa(x0 + 92, x1 - 92, 0, 16, z0 + 92, z1 - 6, 'cinza_fogo', 4.0))                           # cinza
    for k, (x, z, a, r) in enumerate(((-50, 40, 1.35, 40), (55, 20, 1.75, 34), (0, -30, 1.5, 44))):        # lenha entrando pela boca
        dx, dz = 170 * math.cos(a), 170 * math.sin(a)
        p.append(cil((FX + x - dx, 20 + r + k * 9, z - dz + 60), (FX + x + dx, 22 + r, z + dz + 60), r, 'casca', n=9, r1=r * 0.9))
        p.append(cil((FX + x + dx * 0.995, 22 + r, z + dz * 0.995 + 60), (FX + x + dx * 1.01, 22 + r, z + dz * 1.01 + 60), r * 0.86, 'crua_y', n=9))
    return p


def _brasa():
    p = []
    for k in range(9):
        a = k * 2.4
        rr = 26 + (k * 37) % 90
        x, z = FX + rr * math.cos(a), FOGO_Z - 60 + rr * 0.7 * math.sin(a)
        p.append(bevel(caixa(x - 20, x + 20, 14, 34 + (k % 3) * 9, z - 19, z + 19, 'carvao'), 8.0, seg=1))
    return p


def _panela():
    y = TOPO_F + 10
    yt = y + PH
    corpo = _torno([(0, 0), (PR - 10, 0), (PR, 10), (PR + 2, PH - 6), (PR + 9, PH - 6), (PR + 9, PH), (0, PH)], 'panela_alu', FX, y, 0, n=36)
    p = [corpo,
         _torno([(PR + 12, -9), (PR + 17, 0), (PR + 13, 12), (PR - 8, 16), (PR - 14, 10)], 'barro', FX, yt, 0, n=28, anel=True),   # barro vedando a tampa
         _torno([(0, 8), (PR - 6, 8), (PR - 20, 22), (110, 44), (56, 58), (40, 62), (0, 62)], 'panela_alu', FX, yt, 0, n=36),      # tampa abaulada
         _torno([(0, 0), (40, 0), (36, 34), (16, 62), (15, 96), (0, 96)], 'cobre_velho', FX, yt + 60, 0, n=18),                     # capacete de cobre
         _torno([(18, -8), (22, 0), (18, 9), (12, 9), (12, -8)], 'pano_cru', FX, yt + 152, 0, n=10, anel=True)]                      # trapo na emenda
    for s in (-1, 1):                                                                                     # alças
        p.append(_fio([(FX + s * (PR + 1), yt - 62, -34), (FX + s * (PR + 40), yt - 62, -28), (FX + s * (PR + 40), yt - 62, 28), (FX + s * (PR + 1), yt - 62, 34)], 5.5, 'panela_alu'))
    tx, tz = FX + 78, 92                                                                                  # termômetro de relógio espetado na tampa
    p.append(cil((tx, yt + 30, tz), (tx, yt + 78, tz), 4, 'lata', n=8))
    p.append(_torno([(0, 0), (30, 0), (32, 4), (32, 13), (28, 16), (0, 16)], 'lata', tx, yt + 104, tz - 8, n=18, eixo=(0, 0.35, 1)))
    p.append(_torno([(0, 16.6), (26, 16.6)], 'mostrador', tx, yt + 104, tz - 8, n=18, eixo=(0, 0.35, 1)))
    return p


def _serpentina():
    y0 = TOPO_F + 10 + PH + 150
    ex = DX - 190                                                                                         # onde entra na água
    pts = [(FX, y0, 0), (FX, 985, 0), (FX + 130, 1010, 0), (ex - 40, 960, 0), (ex, 900, 0), (ex, 842, 6)]
    p = [_cano(pts, 9.5, 'cobre_velho', raio=120, n=7)]
    volta = []                                                                                            # uma volta e meia à vista, sumindo na água
    for i in range(31):
        t = i / 20
        a = math.pi + 2 * math.pi * t
        volta.append((DX + 190 * math.cos(a), 842 - 62 * t, -190 * math.sin(a)))
    p.append(_fio(volta, 9.5, 'cobre_velho', res=2))
    p.append(_cano([(SX - 12, SY, 0), (SX + 84, SY - 6, 0), (SX + 118, SY - 22, 0), (SX + 118, SY - 46, 0)], 9.5, 'cobre_velho', raio=22, n=4))   # saída
    p.append(_torno([(18, -9), (23, 0), (18, 9), (11, 9), (11, -9)], 'pano_cru', SX + 4, SY, 0, n=10, eixo=(1, 0, 0), anel=True))
    return p


def _tambor():
    a = ALT / 3
    prof = [(0, 0), (R - 8, 0), (R, 8), (R, a - 14), (R + 8, a), (R, a + 14), (R, 2 * a - 14), (R + 8, 2 * a), (R, 2 * a + 14),
            (R, ALT - 16), (R + 5, ALT - 10), (R + 5, ALT), (R - 3, ALT), (R - 5, AGUA - 4)]
    p = [_sem_tampas(_torno(prof, 'tambor_frio', DX, 0, 0, n=48), 48),
         _torno([(0, 0), (R - 5, 0)], 'agua_tambor', DX, AGUA, 0, n=32)]
    a = math.radians(58)                                                                                  # ladrão de PVC
    cx, cz = math.cos(a), math.sin(a)
    r0, r1 = R - 4, R + 78
    p.append(cil((DX + r0 * cx, 770, r0 * cz), (DX + r1 * cx, 770, r1 * cz), 21, 'pvc', n=14))
    p.append(_torno([(0, 0), (27, 0), (27, 20), (0, 20)], 'pvc', DX + (R + 2) * cx, 770, (R + 2) * cz, n=14, eixo=(cx, 0, cz)))
    p.append(_torno([(0, -27), (26, -27), (27, 0), (27, 27), (0, 27)], 'pvc', DX + r1 * cx, 770, r1 * cz, n=14, eixo=(cx, 0, cz)))   # joelho
    p.append(cil((DX + r1 * cx, 770, r1 * cz), (DX + r1 * cx, 640, r1 * cz), 21, 'pvc', n=14))
    return p


def _garrafao():
    prof = [(0, 0), (70, 0), (78, 8), (80, 96), (66, 124), (30, 146), (24, 152), (24, 176), (28, 178), (28, 186), (0, 186)]
    p = [_torno(prof, 'vidro_verde', GX, 0, 0, n=20)]
    for x, z, h, cheio in ((GX - 40, 150, 250, True), (GX + 46, 172, 250, True), (GX - 150, 215, 250, False)):   # garrafas já cheias, arrolhadas
        p.append(_torno([(0, 0), (34, 0), (38, 6), (38, h * 0.55), (14, h * 0.80), (13, h), (0, h)], 'pinga' if cheio else 'vidro_verde', x, 0, z, n=14))
        p.append(_torno([(0, 0), (11, 0), (13, 16), (0, 16)], 'rolha', x, h - 4, z, n=8))
    return p


def montar():
    parte('fornalha', _fornalha(), origem=G(0, 0, 0), grupo='A')
    parte('tambor', _tambor(), origem=G(0, 0, 0), grupo='A')
    parte('panela', _panela(), origem=G(0, 0, 0), grupo='B')
    parte('serpentina', _serpentina(), origem=G(0, 0, 0), grupo='B')
    parte('garrafas', _garrafao(), origem=G(0, 0, 0), grupo='B')
    parte('brasa', _brasa(), origem=G(0, 0, 0), grupo='B')
