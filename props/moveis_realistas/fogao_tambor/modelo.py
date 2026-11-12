"""Fogão a lenha de tambor: um tambor de 200 L deitado em berços de chapa sobre tijolos, porta de fornalha
numa ponta (nó `porta_fornalha`, dobradiça em DOBRA), chapa de cozinhar em cima com duas bocas, chaminé de
cano até 2,4 m com chapéu, panela e chaleira na chapa, lenha empilhada ao lado e atiçador.
Medidas em mm, coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente (onde se cozinha)."""
import math
import lib
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte

R, L = 290, 880             # tambor deitado ao longo de x
YC = R + 222                # eixo do tambor
TOPO = YC + R               # em cima do tambor
PX = -L / 2                 # ponta da porta
DOBRA = (PX - 5, YC - 100, 130)
FOGO_Y = YC - 120
CX, CZ = 335, -40           # chaminé
ALTO = 2400


def _torno(prof, mat, x=0, y=0, z=0, n=24, eixo=(0, 1, 0)):
    """Perfil em (raio, altura ao longo do eixo); as pontas fecham no eixo."""
    return lib.lathe([(h, r) for r, h in prof], mat, n=n, c0=G(x, y, z), eixo=G(*eixo))


def _fio(pts, r, mat, fechado=False, res=3):
    return lib.fio([G(*p) for p in pts], r, mat, fechado=fechado, res=res)


def _tijolo(x0, y0, z0, ao_longo='z', mat='tijolo'):
    dx, dz = (90, 190) if ao_longo == 'z' else (190, 90)
    return bevel(caixa(x0, x0 + dx, y0, y0 + 57, z0, z0 + dz, mat), 3.0, seg=1)


def _corpo():
    a = L / 3
    prof = [(0, 0), (R - 10, 0), (R, 8), (R, a - 14), (R + 8, a), (R, a + 14), (R, 2 * a - 14), (R + 8, 2 * a), (R, 2 * a + 14), (R, L - 8), (R - 10, L), (0, L)]
    p = [_torno(prof, 'tambor_queimado', PX, YC, 0, n=40, eixo=(1, 0, 0))]
    for sx in (-1, 1):                                                                                   # pés: tijolos e berço de chapa
        x = sx * 300
        for k in range(2):
            for z0 in (-198, 6):
                p.append(_tijolo(x - 45 + (k * 6 - 3) * sx, k * 60, z0 + k * 4))
        arco = [(294 * math.cos(math.radians(t)), YC + 294 * math.sin(math.radians(t))) for t in range(322, 217, -8)]
        p.append(perfil([(-236, 118), (236, 118), (236, arco[0][1])] + arco + [(-236, arco[-1][1])], x - 4, x + 4, 'ferrugem', 1.0))
        p.append(caixa(x - 40, x + 40, 118, 124, -236, 236, 'ferrugem', 1.0))
    p.append(caixa(PX + 8, PX + 40, YC - 190, YC - 150, -150, 150, 'tambor_queimado', 2.0))                  # cinzeiro embaixo da porta
    return p


def _chamine():
    y0 = TOPO - 12
    p = [cil((CX, y0, CZ), (CX, ALTO - 110, CZ), 62, 'chamine', n=20),
         _torno([(0, 0), (92, 0), (88, 10), (66, 34), (0, 34)], 'chamine', CX, y0 - 2, CZ, n=20)]         # colarinho
    for y in (y0 + 520, y0 + 1040):                                                                      # emendas
        p.append(_torno([(0, 0), (66, 0), (67, 8), (66, 26), (0, 26)], 'chamine', CX, y, CZ, n=20))
    p.append(_torno([(0, 0), (120, 0), (118, 6), (8, 62), (0, 64)], 'chamine', CX, ALTO - 64, CZ, n=20))   # chapéu
    for a in (0.4, 2.5, 4.6):
        dx, dz = 58 * math.cos(a), 58 * math.sin(a)
        p.append(cil((CX + dx, ALTO - 130, CZ + dz), (CX + dx * 1.6, ALTO - 60, CZ + dz * 1.6), 4, 'chamine', n=6))
    return p


def _chapa():
    y = TOPO - 6
    x0, x1 = -410, 236
    p = [caixa(x0, x1, y, y + 10, -225, 225, 'chapa_fogao', 2.0)]
    for sz in (-1, 1):                                                                                   # saias que fecham o vão até o tambor
        p.append(perfil([(sz * 222, y), (sz * 226, y), (sz * 214, y - 96), (sz * 208, y - 96)], x0 + 6, x1 - 6, 'tambor_queimado', 0.8))
    for xb, rb in ((-250, 105), (10, 88)):                                                               # bocas com tampa de argolas
        p.append(_torno([(0, 0), (rb, 0), (rb, 3.5), (rb - 6, 5), (0, 5)], 'ferro_preto', xb, y + 10, 0, n=24))
        p.append(_torno([(0, 0), (rb * 0.45, 0), (rb * 0.45, 2.5), (0, 2.5)], 'chapa_fogao', xb, y + 15, 0, n=18))
        p.append(caixa(xb - 14, xb + 14, y + 17.5, y + 21, -4, 4, 'ferro_preto', 1.0))
    return p


def _porta():
    """Porta da fornalha na ponta do tambor, com registro de ar. As frestas acesas ficam na parte `brasa`."""
    x0, x1 = PX - 11, PX - 3
    y0, y1 = YC - 100, YC + 86
    p = [caixa(x0, x1, y0, y1, -130, 130, 'tambor_queimado', 3.0)]
    for y in (y0 + 30, y1 - 30):                                                                         # dobradiças
        p.append(cil((x0 - 2, y - 16, 134), (x0 - 2, y + 16, 134), 7, 'ferro_preto', n=10))
        p.append(caixa(x0 - 3, x0, y - 11, y + 11, 60, 132, 'ferro_preto', 1.0))
    p.append(_fio([(x0, YC + 30, -104), (x0 - 40, YC + 30, -100), (x0 - 40, YC - 30, -100), (x0, YC - 30, -104)], 6.0, 'aco_ferramenta'))   # puxador
    p.append(caixa(x0 - 3, x0, YC - 8, YC + 8, -128, -84, 'ferro_preto', 1.0))                              # tranca
    for k in range(4):                                                                                   # registro: fendas escuras
        z = -42 + k * 32
        p.append(caixa(x0 - 0.6, x0, y0 + 22, y0 + 62, z, z + 14, 'carvao'))
    p.append(caixa(x0 - 4, x0 - 0.8, y0 + 12, y0 + 20, -56, 96, 'ferro_preto', 1.0))
    return p


def _brasa():
    x = PX - 11.9
    y0 = YC - 100
    return [caixa(x, x + 0.4, y0 + 25, y0 + 59, -42 + k * 32 + 2.5, -42 + k * 32 + 11.5, 'carvao') for k in range(4)]


def _panelas():
    y = TOPO + 14
    px = -250                                                                                            # panelão de alumínio com tampa
    p = [_torno([(0, 0), (128, 0), (134, 6), (138, 150), (146, 150), (146, 157), (131, 157), (127, 9), (0, 9)], 'aluminio', px, y, 0, n=28),
         _torno([(0, 0), (140, 0), (142, 4), (60, 22), (0, 26)], 'aluminio', px, y + 157, 0, n=28),
         _torno([(0, 0), (10, 0), (16, 14), (16, 20), (0, 22)], 'plastico_preto', px, y + 181, 0, n=12)]
    for s in (-1, 1):
        p.append(_fio([(px + s * 138, y + 128, -28), (px + s * 172, y + 128, -22), (px + s * 172, y + 128, 22), (px + s * 138, y + 128, 28)], 5.0, 'aluminio'))
    cx, cz = 50, 40                                                                                      # chaleira de ágata azul
    p.append(_torno([(0, 0), (82, 0), (96, 20), (98, 80), (70, 128), (40, 140), (0, 140)], 'esmalte_azul', cx, y, cz, n=24))
    p.append(_torno([(0, 0), (42, 0), (40, 6), (12, 14), (10, 26), (0, 28)], 'esmalte_azul', cx, y + 140, cz, n=16))
    p.append(cil((cx + 80, y + 70, cz + 30), (cx + 150, y + 140, cz + 62), 14, 'esmalte_azul', n=10, r1=8))  # bico
    p.append(_fio([(cx - 52, y + 132, cz), (cx - 60, y + 210, cz), (cx, y + 240, cz), (cx + 60, y + 210, cz), (cx + 52, y + 132, cz)], 5.0, 'ferro_preto'))
    return p


def _lenha():
    p = []
    x0 = 560
    k = 0
    for j, (n, y) in enumerate(((4, 62), (3, 172), (2, 276))):
        for i in range(n):
            z = -170 + i * 118 + j * 58
            r = 52 + (k * 7) % 12
            p.append(cil((x0 + (k % 3) * 14, y, z), (x0 + 330 + (k % 2) * 30, y + (k % 3) * 4, z + (k % 2) * 16 - 8), r, 'casca', n=9, r1=r * 0.92))
            p.append(cil((x0 + (k % 3) * 14 - 1.5, y, z), (x0 + (k % 3) * 14 + 6, y, z), r * 0.9, 'crua_y', n=9))
            k += 1
    # atiçador encostado no pé
    p.append(cil((-560, 6, 200), (-470, 640, 250), 6, 'ferro_preto', n=8))
    p.append(_fio([(-470, 640, 250), (-462, 690, 254), (-430, 700, 258), (-420, 668, 256), (-452, 650, 252)], 5.0, 'ferro_preto'))
    p.append(cil((-560, 6, 200), (-590, 10, 150), 6, 'ferro_preto', n=8))
    return p


def montar():
    parte('tambor', _corpo(), origem=G(0, 0, 0), grupo='A')
    parte('chamine', _chamine(), origem=G(0, 0, 0), grupo='A')
    parte('chapa', _chapa(), origem=G(0, 0, 0), grupo='B')
    parte('porta_fornalha', _porta(), origem=G(*DOBRA), grupo='B')
    parte('panelas', _panelas(), origem=G(0, 0, 0), grupo='B')
    parte('lenha', _lenha(), origem=G(0, 0, 0), grupo='C')
    parte('brasa', _brasa(), origem=G(0, 0, 0), grupo='C')
