"""Mesa de recarga de munição: bancada alta de caibros e pranchas com painel e prateleira atrás, prensa de recarga
de ferro fundido com alavanca aparafusada no canto, balança de pólvora de braço, bloco de madeira com as cápsulas
em pé, latas de pólvora, caixinhas de espoleta, lingotes de chumbo com a concha e o molde de projéteis; na prateleira,
latas, caixas de munição e cartuchos de espingarda; embaixo, um caixote de MUNIÇÃO e um balde de cápsulas vazias.
Medidas em mm, coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente (onde se trabalha)."""
import math, random
import bpy, bmesh
import lib
import base
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte

X, Z, H = 600, 300, 900     # meia largura, meia profundidade e altura do tampo
SH = 1165                   # em cima da prateleira
ALTO = 1275
PX, PZ = -360, 165          # prensa


def _torno(prof, mat, x=0, y=0, z=0, n=24, eixo=(0, 1, 0), **k):
    """Perfil em (raio, altura ao longo do eixo); as pontas fecham no eixo."""
    return lib.lathe([(h, r) for r, h in prof], mat, n=n, c0=G(x, y, z), eixo=G(*eixo), **k)


def _fio(pts, r, mat, fechado=False, res=2):
    return lib.fio([G(*p) for p in pts], r, mat, fechado=fechado, res=res)


def _letra_curva(s, tam, cx, y, cz, raio, mat):
    """Letreiro pintado na frente de uma lata redonda de centro (cx, cz)."""
    o = base.letreiro(s, tam, cx, y, 0, mat=mat)
    for v in o.data.vertices:
        dx = v.co.x - cx * lib.MM
        v.co.y = -(cz * lib.MM + math.sqrt(max(0.0, ((raio + 0.8) * lib.MM) ** 2 - dx * dx)))
    return o


def _estrutura():
    p = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            x0, z0 = sx * (X - 75), sz * (Z - 70)
            alto = (ALTO if sx < 0 else SH - 26) if sz < 0 else H - 45
            p.append(caixa(x0 - 35, x0 + 35, 0, alto, z0 - 35 + (0 if sz > 0 else -35), z0 + 35 + (0 if sz > 0 else -35), 'pinho_y', 3.0))
        p.append(caixa(sx * (X - 75) - 22, sx * (X - 75) + 22, H - 150, H - 45, -Z + 35, Z - 105, 'pinho_z', 2.5))      # travessas de cima, dos lados
        p.append(caixa(sx * (X - 75) - 22, sx * (X - 75) + 22, 180, 250, -Z + 35, Z - 105, 'pinho_z', 2.5))
    p.append(caixa(-X + 110, X - 110, H - 150, H - 45, Z - 127, Z - 83, 'pinho_x', 2.5))                               # saia da frente
    p.append(caixa(-X + 110, X - 110, H - 150, H - 45, -Z, -Z + 44, 'pinho_x', 2.5))
    for k, (z0, z1, d) in enumerate(((-Z + 40, -Z + 190, 4), (-Z + 196, -Z + 350, -5), (-Z + 356, Z - 96, 2))):         # prateleira de baixo
        p.append(caixa(-X + 44 + d, X - 44 + d, 250, 275, z0, z1, 'pinho_x', 2.5))
    for k in range(2):                                                                                               # painel de trás
        y = H + 4 + k * 116
        p.append(caixa(-X + 22 + k * 5, X - 22 - k * 3, y, y + 112, -Z - 5, -Z + 15, 'tampo_x', 2.5))
    p.append(caixa(-X + 6, X - 6, SH - 26, SH, -Z - 5, -Z + 175, 'tampo_x', 3.0))                                     # prateleira de cima
    for sx in (-1, 1):                                                                                               # mãos-francesas
        x = sx * (X - 75)
        p.append(perfil([(-Z + 35, SH - 26), (-Z + 160, SH - 26), (-Z + 35, SH - 150)], x - 14, x + 14, 'pinho_z', 2.0))
    return p


def _tampo():
    p = []
    for k, (z0, z1, d) in enumerate(((-Z + 16, -Z + 162, 0), (-Z + 166, -Z + 312, 7), (-Z + 316, -Z + 462, -6), (-Z + 466, Z + 8, 3))):
        p.append(caixa(-X + d, X + d * 0.5, H - 45, H, z0, z1, 'tampo_x', 3.5))
    return p


def _prensa():
    x, z, y = PX, PZ, H
    q = [caixa(x - 62, x + 62, y, y + 14, z - 86, z + 86, 'esmalte_vermelho', 4.0)]
    pts = [(z - 46, y + 12), (z + 46, y + 12), (z + 64, y + 60), (z + 64, y + 268), (z + 44, y + 300), (z - 44, y + 300), (z - 64, y + 268), (z - 64, y + 60)]
    quadro = perfil(pts, x - 27, x + 27, 'esmalte_vermelho', 6.0)
    cut(quadro, bevel(caixa(x - 40, x + 40, y + 76, y + 222, z - 36, z + 36, 'esmalte_vermelho'), 10.0, seg=2))
    q.append(quadro)
    q.append(_torno([(0, 0), (33, 0), (33, 16), (27, 22), (0, 22)], 'esmalte_vermelho', x, y + 296, z, n=20))            # ressalto de cima
    q.append(cil((x, y + 200, z), (x, y + 372, z), 17, 'aco_ferramenta', n=16))                                        # matriz
    q.append(_torno([(0, 0), (25, 0), (25, 11), (0, 11)], 'aco_ferramenta', x, y + 320, z, n=6))                        # contraporca
    q.append(_torno([(0, 0), (13, 0), (13, 16), (9, 20), (0, 20)], 'latao', x, y + 372, z, n=12))
    q.append(cil((x, y + 14, z), (x, y + 128, z), 15, 'aco_ferramenta', n=16))                                         # êmbolo
    q.append(_torno([(0, 0), (19, 0), (19, 9), (0, 9)], 'aco_ferramenta', x, y + 128, z, n=16))
    q.append(cil((x, y + 137, z), (x, y + 182, z), 5.6, 'latao', n=8))                                                 # uma cápsula no êmbolo
    for sx in (-1, 1):                                                                                               # garfo e alavanca
        q.append(caixa(x + sx * 20 - 6, x + sx * 20 + 6, y + 22, y + 66, z + 58, z + 104, 'esmalte_vermelho', 2.5))
    q.append(cil((x - 30, y + 46, z + 88), (x + 30, y + 46, z + 88), 6.5, 'aco_ferramenta', n=10))
    q.append(cil((x, y + 40, z + 86), (x, y + 404, z + 152), 8.5, 'aco_ferramenta', n=12))
    q.append(_torno([(0, -22), (14, -18), (22, 0), (14, 18), (0, 22)], 'plastico_preto', x, y + 420, z + 155, n=14))
    for sx in (-1, 1):                                                                                               # parafusos da base
        for sz in (-1, 1):
            q.append(_torno([(0, 0), (9, 0), (9, 6), (0, 6)], 'aco_ferramenta', x + sx * 46, y + 14, z + sz * 70, n=6))
    return q


def _balanca():
    y = H
    q = [caixa(-150, 70, y, y + 16, -105, -30, 'chapa_cinza', 4.0),
         caixa(-26, -12, y + 16, y + 118, -76, -58, 'chapa_cinza', 2.0),
         caixa(-170, 62, y + 112, y + 120, -70, -64, 'latao', 1.0),                                                  # braço
         caixa(-60, -40, y + 106, y + 126, -72, -62, 'aco_ferramenta', 1.0),                                         # cursor
         caixa(56, 64, y + 70, y + 156, -90, -44, 'chapa_cinza', 2.0),                                               # escala do fiel
         _torno([(0, 0), (22, 0), (40, 12), (42, 12), (42, 15), (38, 15), (21, 3), (0, 3)], 'latao', -160, y + 34, -67, n=18)]   # prato
    q.append(_fio([(-198, y + 47, -67), (-170, y + 114, -67), (-160, y + 122, -67), (-150, y + 114, -67), (-122, y + 47, -67)], 1.4, 'aco_ferramenta', res=1))
    for sx in (-1, 1):                                                                                               # pés niveladores
        q.append(_torno([(0, 0), (11, 0), (11, 5), (0, 5)], 'latao', -40 + sx * 96, y + 16, -40, n=10))
    return q


def _bloco():
    """Bloco de madeira com as cápsulas em pé; as três primeiras filas já com o projétil."""
    y = H
    q = [caixa(150, 372, y, y + 30, 46, 160, 'faia_x', 3.0)]
    for i in range(9):
        for j in range(5):
            x, z = 170 + i * 22.8, 62 + j * 20.5
            if (i * 5 + j) % 11 == 7:
                continue                                                                                             # furos vazios
            q.append(cil((x, y + 24, z), (x, y + 66, z), 5.6, 'latao', n=7))
            if i < 3:
                q.append(cil((x, y + 66, z), (x, y + 84, z), 5.0, 'cobre', n=7, r1=1.6))
    return q


def _lata(x, z, r, h, mat, y, letra=None, tam=17):
    q = [_torno([(0, 0), (r, 0), (r, h), (r - 3, h + 3), (0, h + 3)], mat, x, y, z, n=20),
         _torno([(0, 0), (r * 0.45, 0), (r * 0.45, 12), (r * 0.40, 14), (0, 14)], 'lata', x, y + h + 3, z, n=12)]
    if letra:
        q.append(_letra_curva(letra, tam, x, y + h * 0.48, z, r, 'letra_branca'))
    return q


def _caixinha(x0, x1, y0, h, z0, z1, mat, gira=0.0):
    return [caixa(x0, x1, y0, y0 + h, z0, z1, mat, 2.0)]


def _miudezas():
    y = H
    q = _lata(455, -175, 50, 150, 'esmalte_vermelho', y, 'PÓLVORA', 19) + _lata(340, -200, 42, 118, 'aco_verde', y)
    for k, (dx, dz) in enumerate(((0, 0), (5, -4), (-4, 3))):                                                        # espoletas
        q += _caixinha(96 + dx, 176 + dx, y + k * 23, 22, -215 + dz, -160 + dz, 'papelao' if k != 1 else 'caixa_azul')
    for k in range(3):                                                                                               # lingotes de chumbo
        z0 = 190 + (k % 2) * 22 - (k == 2) * 8
        yy = y + (k == 2) * 26
        x0 = 440 + (k if k < 2 else 0.5) * 62 - 30
        q.append(perfil([(z0 - 60, yy), (z0 + 60, yy), (z0 + 52, yy + 26), (z0 - 52, yy + 26)], x0, x0 + 54, 'chumbo', 4.0))
    cx, cz = 470, 50                                                                                                 # concha de derreter
    q.append(_torno([(0, 0), (20, 0), (38, 18), (40, 30), (36, 30), (32, 20), (18, 5), (0, 5)], 'ferro_preto', cx, y, cz, n=16))
    q.append(_torno([(0, 6), (30, 18)], 'chumbo', cx, y, cz, n=12))
    q.append(cil((cx + 34, y + 26, cz + 8), (cx + 120, y + 34, cz + 40), 5, 'ferro_preto', n=8))
    q.append(cil((cx + 112, y + 33, cz + 37), (cx + 108 + 22, y + 34 + 2, cz + 37 + 9), 11, 'faia_x', n=10))
    q.append(caixa(214, 262, y, y + 34, -150, -90, 'ferro_preto', 3.0))                                              # molde de projéteis
    q.append(caixa(214, 262, y, y + 34, -88, -84, 'ferro_preto', 1.0))
    for dz in (-136, -104):
        q.append(cil((262, y + 17, dz), (300, y + 17, dz), 5, 'ferro_preto', n=8))
        q.append(cil((298, y + 17, dz), (388, y + 15, dz - 4 + (dz > -120) * 8), 10, 'faia_x', n=10, r1=11))
    q.append(caixa(-75, 115, H + 30, H + 222, -Z + 15, -Z + 15.8, 'papel'))                                          # tabela de cargas pregada
    for dx in (-66, 106):
        q.append(_torno([(0, 0), (4.5, 0), (3, 2.2), (0, 2.4)], 'lata', dx, H + 213, -Z + 15.8, n=8, eixo=(0, 0, 1)))
    # luminária de garra no pé de trás
    lx, lz = -X + 75, -Z + 40
    q.append(caixa(lx - 30, lx + 30, ALTO - 70, ALTO - 30, lz - 6, lz + 46, 'esmalte_preto', 3.0))
    q.append(_fio([(lx, ALTO - 34, lz + 36), (lx + 10, ALTO + 40, lz + 60), (lx + 60, ALTO + 70, lz + 130), (lx + 120, ALTO + 40, lz + 200), (lx + 140, ALTO - 10, lz + 232)], 6.5, 'esmalte_preto', res=2))
    q.append(_torno([(0, 0), (24, 0), (30, 26), (78, 110), (80, 116), (76, 116), (0, 30)], 'esmalte_preto', lx + 140, ALTO - 2, lz + 232, n=20, eixo=(0.12, -1, 0.3)))
    return q


def _prateleira():
    y = SH
    q = []
    for k, (x, r, h, mat) in enumerate(((-520, 44, 120, 'lata'), (-418, 40, 104, 'lata'), (-325, 46, 132, 'esmalte_azul'))):
        q += _lata(x, -Z + 78 + (k % 2) * 14, r, h, mat, y)
    for k, (x0, yy, mat, d) in enumerate(((-250, 0, 'caixa_verde', 0), (-112, 0, 'caixa_verde', 6), (-240, 47, 'caixa_azul', 3), (-104, 47, 'caixa_verde', -5), (-180, 94, 'papelao', 0))):
        q += _caixinha(x0, x0 + 132, y + yy, 46, -Z + 28 + d, -Z + 108 + d, mat)
    for i in range(11):                                                                                              # cartuchos de espingarda
        for j in range(2):
            if (i + j * 3) % 7 == 5:
                continue
            x, z = 70 + i * 24.5, -Z + 60 + j * 26
            q.append(cil((x, y + 13, z), (x, y + 62, z), 10.2, 'cartucho', n=8))
            q.append(_torno([(0, 0), (11.2, 0), (11.2, 2.5), (10.4, 3), (10.4, 13.5), (0, 13.5)], 'latao', x, y, z, n=8))
    q.append(caixa(380, 570, y, y + 30, -Z + 20, -Z + 150, 'caixa_azul', 2.5))                                        # manual de recarga
    q.append(caixa(384, 567, y + 3, y + 27, -Z + 22, -Z + 152.5, 'papel'))
    return q


def _embaixo():
    y = 275
    x0, x1, z0, z1, h = -480, 20, -170, 150, 250                                                                     # caixote de munição
    q = []
    for k in range(2):
        yy = y + 10 + k * 122
        q.append(caixa(x0, x1, yy, yy + 118, z1 - 18, z1, 'crua_x', 2.0))
        q.append(caixa(x0, x1, yy, yy + 118, z0, z0 + 18, 'crua_x', 2.0))
        for xa in (x0, x1 - 18):
            q.append(caixa(xa, xa + 18, yy, yy + 118, z0 + 18, z1 - 18, 'crua_z', 2.0))
    q.append(caixa(x0 - 8, x1 + 8, y + h + 4, y + h + 24, z0 - 8, z1 + 8, 'crua_x', 2.5))                               # tampa
    q.append(caixa(x0 + 4, x1 - 4, y, y + 12, z0 + 4, z1 - 4, 'crua_x', 1.5))
    for xa in (x0 + 60, x1 - 100):
        q.append(caixa(xa, xa + 40, y + 6, y + h + 2, z1, z1 + 14, 'crua_y', 2.0))                                     # sarrafos
    for sx, xa in ((-1, x0), (1, x1)):                                                                               # alças de corda
        q.append(_fio([(xa, y + 180, -70), (xa + sx * 26, y + 150, -50), (xa + sx * 30, y + 136, 0), (xa + sx * 26, y + 150, 50), (xa, y + 180, 70)], 6.0, 'sisal', res=1))
    q.append(base.letreiro('MUNIÇÃO', 54, (x0 + x1) / 2 - 10, y + 150, z1 + 0.7, mat='letra_preta'))
    bx, bz = 300, 0                                                                                                  # balde de cápsulas vazias
    q.append(_torno([(0, 0), (112, 0), (116, 6), (140, 236), (146, 240), (146, 246), (136, 246), (133, 212), (0, 212)], 'lata', bx, y, bz, n=24))
    q.append(_fio([(bx - 142, y + 232, bz), (bx - 150, y + 150, bz + 40), (bx - 60, y + 96, bz + 128), (bx + 60, y + 96, bz + 128), (bx + 150, y + 150, bz + 40), (bx + 142, y + 232, bz)], 3.2, 'aco_ferramenta', res=1))
    q.append(_torno([(0, 228), (60, 224), (124, 213)], 'latao_fosco', bx, y, bz, n=14))
    rnd = random.Random(11)
    for _ in range(46):
        a, r = rnd.uniform(0, 2 * math.pi), 118 * math.sqrt(rnd.random())
        c = (bx + r * math.cos(a), y + 226 - (r / 118) ** 2 * 11, bz + r * math.sin(a))
        d = [rnd.uniform(-1, 1), rnd.uniform(-0.25, 0.4), rnd.uniform(-1, 1)]
        m = math.sqrt(sum(v * v for v in d))
        d = [v / m * 21 for v in d]
        q.append(cil(tuple(c[i] - d[i] for i in range(3)), tuple(c[i] + d[i] for i in range(3)), 5.6, 'latao_fosco', n=6))
    return q


def montar():
    parte('estrutura', _estrutura(), origem=G(0, 0, 0), grupo='A')
    parte('tampo', _tampo(), origem=G(0, 0, 0), grupo='A')
    parte('prensa', _prensa(), origem=G(0, 0, 0), grupo='B')
    parte('balanca', _balanca(), origem=G(0, 0, 0), grupo='B')
    parte('capsulas', _bloco(), origem=G(0, 0, 0), grupo='B')
    parte('miudezas', _miudezas(), origem=G(0, 0, 0), grupo='C')
    parte('prateleira', _prateleira(), origem=G(0, 0, 0), grupo='C')
    parte('embaixo', _embaixo(), origem=G(0, 0, 0), grupo='C')
