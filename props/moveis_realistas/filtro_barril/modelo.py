"""Filtro de água em barril: tambor de 200 L em pé sobre dois blocos de concreto e três tábuas, com a boca coberta
por um pano amarrado com corda de sisal (a água suja entra por ali e desce pelas camadas de pedra, areia e carvão),
torneira de latão num cano de PVC embaixo, mangueira de nível ao lado e um galão de 5 L aparando a água limpa.
Medidas em mm, coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente (o lado da torneira)."""
import math
import bpy, bmesh
import lib
import base
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte

BASE = 225                  # em cima das tábuas
R, ALT = 290, 880           # raio e altura do tambor
TOPO = BASE + ALT
TORN_Y = BASE + 95          # altura do cano da torneira
GZ = R + 112                # meio do galão


def _torno(prof, mat, x=0, y=0, z=0, n=24, eixo=(0, 1, 0), **k):
    """Perfil em (raio, altura ao longo do eixo); as pontas fecham no eixo."""
    return lib.lathe([(h, r) for r, h in prof], mat, n=n, c0=G(x, y, z), eixo=G(*eixo), **k)


def _sem_tampas(o, n):
    """Tira as tampas que o torno põe nas pontas do perfil (para folhas abertas, como o pano)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if len(f.verts) >= n], context='FACES')
    bm.to_mesh(o.data)
    bm.free()
    return o


def _fio(pts, r, mat, fechado=False, res=2):
    return lib.fio([G(*p) for p in pts], r, mat, fechado=fechado, res=res)


def _anel(raio, y, r, mat, n=32, fase=0.0, sobe=0.0):
    return _fio([(raio * math.cos(fase + 2 * math.pi * i / n), y + sobe * i / n, raio * math.sin(fase + 2 * math.pi * i / n)) for i in range(n)], r, mat, fechado=True, res=1)


def _estrado():
    p = []
    for z0, z1 in ((-255, -65), (65, 255)):                                                              # blocos deitados, furos para a frente
        b = caixa(-195, 195, 0, 190, z0, z1, 'bloco', 4.0)
        cut(b, [caixa(sx * 95 - 72, sx * 95 + 72, 32, 158, z0 - 10, z1 + 10, 'bloco') for sx in (-1, 1)])
        p.append(b)
    for k, (z0, z1, d) in enumerate(((-268, -96, 8), (-88, 86, -6), (94, 266, 3))):
        p.append(caixa(-325 + d, 322 + d, 190, BASE, z0, z1, 'tampo_x', 3.0))
    return p


def _tambor():
    a = ALT / 3
    prof = [(0, 0), (R - 8, 0), (R, 8), (R, a - 14), (R + 8, a), (R, a + 14), (R, 2 * a - 14), (R + 8, 2 * a), (R, 2 * a + 14),
            (R, ALT - 16), (R + 5, ALT - 10), (R + 5, ALT), (R - 3, ALT), (R - 5, ALT - 60), (0, ALT - 60)]
    return [_torno(prof, 'tambor_agua', y=BASE, n=48)]


def _pano():
    """Pano esticado na boca, afundado no meio, com a saia franzida caindo por fora, e duas voltas de corda."""
    prof = [(0, -46), (70, -44), (150, -34), (225, -17), (R - 22, -3), (R + 2, 5), (R + 9, 3), (R + 12, -22), (R + 11, -52),
            (R + 11, -84), (R + 20, -104), (R + 27, -168), (R + 24, -168), (R + 15, -106), (R + 7, -92)]
    pano = _sem_tampas(_torno(prof, 'pano_filtro', y=TOPO, n=64, lobes=0.035, lobe_min=R + 14), 64)
    y = TOPO - 68
    p = [pano, _anel(R + 15, y, 5.5, 'sisal', n=40, sobe=3), _anel(R + 15, y - 11, 5.5, 'sisal', n=40, fase=0.6, sobe=-3)]
    a = math.radians(62)                                                                                 # nó e as pontas soltas
    nx, nz = (R + 21) * math.cos(a), (R + 21) * math.sin(a)
    p.append(_torno([(0, -11), (9, -9), (12, 0), (9, 9), (0, 11)], 'sisal', nx, y - 5, nz, n=8))
    p.append(_fio([(nx, y - 8, nz), (nx + 14, y - 60, nz + 12), (nx + 10, y - 150, nz + 9)], 5.0, 'sisal', res=1))
    p.append(_fio([(nx, y - 8, nz), (nx - 16, y - 50, nz + 10), (nx - 22, y - 112, nz + 9)], 5.0, 'sisal', res=1))
    return p


def _letreiro():
    """ÁGUA pintado a pincel, acompanhando a curva do tambor."""
    p = []
    for s, tam, y in (('ÁGUA', 118, BASE + 392), ('FILTRADA', 46, BASE + 318)):
        o = base.letreiro(s, tam, 0, y, 0, mat='letra_branca')
        for v in o.data.vertices:
            v.co.y = -math.sqrt(max(0.0, ((R + 1.6) * lib.MM) ** 2 - v.co.x ** 2))
        p.append(o)
    return p


def _torneira():
    y, z = TORN_Y, R
    p = [_torno([(0, -4), (34, -4), (34, 6), (22, 10), (22, 16), (0, 16)], 'pvc', 0, y, z - 2, n=16, eixo=(0, 0, 1)),   # flange
         cil((0, y, z + 10), (0, y, z + 66), 13.5, 'pvc', n=14),
         _torno([(0, 0), (17, 0), (17, 22), (0, 22)], 'pvc', 0, y, z + 56, n=14, eixo=(0, 0, 1)),            # luva
         cil((0, y, z + 74), (0, y, z + 104), 12, 'latao', n=12),                                              # corpo da torneira
         _torno([(0, 0), (15, 0), (16, 5), (13, 9), (0, 9)], 'latao', 0, y, z + 72, n=6, eixo=(0, 0, 1)),     # porca
         cil((0, y + 6, z + 96), (0, y + 34, z + 96), 8.5, 'latao', n=10),                                     # castelo
         caixa(-27, 27, y + 34, y + 40, z + 90, z + 102, 'latao', 2.0),                                        # borboleta
         cil((0, y + 2, z + 100), (0, y - 34, z + 116), 10, 'latao', n=10, r1=8.5)]                            # bico
    # mangueira de nível: sai de um niple embaixo e sobe presa por duas cintas de arame
    a = math.radians(40)
    cx, cz = math.cos(a), math.sin(a)
    r0, r1 = R + 4, R + 13
    p.append(cil((r0 * cx, BASE + 60, r0 * cz), ((R + 30) * cx, BASE + 60, (R + 30) * cz), 9, 'pvc', n=10))
    pts = [((R + 26) * cx, BASE + 60, (R + 26) * cz), ((R + 36) * cx, BASE + 68, (R + 36) * cz), ((R + 30) * cx, BASE + 100, (R + 30) * cz), (r1 * cx, BASE + 150, r1 * cz)]
    for k in range(1, 6):
        yy = BASE + 150 + k * 110
        e = 8 if min(abs(yy - BASE - ALT / 3), abs(yy - BASE - 2 * ALT / 3)) < 60 else 0                    # passa por cima das nervuras
        pts.append(((r1 + e) * cx, yy, (r1 + e) * cz))
    p.append(_fio(pts, 6.0, 'mangueira', res=2))
    for yy in (BASE + 200, BASE + 520):
        p.append(cil(((R - 2) * cx, yy, (R - 2) * cz), ((R + 21) * cx, yy, (R + 21) * cz), 11, 'lata', n=8))     # abraçadeiras
    return p


def _galao():
    y = 0
    prof = [(0, 0), (78, 0), (86, 8), (88, 60), (84, 68), (88, 76), (88, 150), (84, 158), (88, 166), (86, 196), (62, 232), (30, 246), (24, 250), (24, 262), (0, 262)]
    p = [_torno(prof, 'galao', 0, y, GZ, n=24),
         _torno([(0, 0), (29, 0), (30, 3), (30, 16), (27, 19), (0, 19)], 'tampa_azul', 0, y + 252, GZ, n=16)]
    p.append(_fio([(-52, 236, GZ), (-70, 262, GZ), (-40, 288, GZ), (0, 296, GZ), (40, 288, GZ), (70, 262, GZ), (52, 236, GZ)], 5.0, 'tampa_azul', res=1))   # alça
    return p


def montar():
    parte('estrado', _estrado(), origem=G(0, 0, 0), grupo='A')
    parte('tambor', _tambor(), origem=G(0, 0, 0), grupo='A')
    parte('letreiro', _letreiro(), origem=G(0, 0, 0), grupo='A')
    parte('pano', _pano(), origem=G(0, 0, 0), grupo='B')
    parte('torneira', _torneira(), origem=G(0, 0, 0), grupo='B')
    parte('galao', _galao(), origem=G(0, 0, 0), grupo='B')
