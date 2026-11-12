"""Forja de tambor com fole: tambor de 200 L cortado, em pé sobre duas fiadas de tijolos, com a boca
forrada de barro e o carvão dentro; fole de couro num cavalete, soprando por um cano; bigorna de trilho
de trem pregada num toco, com o martelo; e a tenaz apoiada na boca do tambor.
Medidas em mm, coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente (onde se trabalha)."""
import math, random
import lib
from base import G, caixa, cil, perfil, frente, bevel, parte
from lib import pintar

BASE = 118                  # em cima dos tijolos
R, ALT = 290, 624           # raio e altura do tambor
BOCA = BASE + ALT
FOGO_Y = BASE + 606         # em cima do carvão, no meio
TOCO_X, TOCO_Z, TOCO_R, TOCO_H = -750, 100, 170, 500
CANO_Y = BASE + 468


def _torno(prof, mat, x=0, y=0, z=0, n=48):
    return lib.lathe(prof, mat, n=n, c0=G(x, y, z), eixo=G(0, 1, 0))


def _fornalha():
    prof = [(0, 0), (0, 286), (6, 290), (200, 290), (205, 298), (215, 298), (220, 290), (400, 290), (405, 298), (415, 298), (420, 290),
            (545, 290), (612, 290), (620, 294), (ALT, 290), (ALT, 276), (610, 270), (600, 255), (520, 120), (480, 95), (480, 0)]
    t = _torno(prof, 'tambor', y=BASE)
    pintar(t, 'tambor_queimado', lambda c, n: c[1] > BASE + 546 and math.hypot(c[0], c[2]) > 272)
    pintar(t, 'barro', lambda c, n: c[1] > BASE + 470 and math.hypot(c[0], c[2]) <= 272)
    p = [t]
    rnd = random.Random(7)
    for sz in (-1, 1):                                              # duas fiadas de tijolos de cada lado
        for fiada in range(2):
            for sx in (-1, 1):
                d = rnd.uniform(-5, 5)
                x0, x1 = sorted((sx * 3 + d, sx * 193 + d))
                z0, z1 = sorted((sz * 168 + d * 0.6, sz * 258 + d * 0.6))
                p.append(caixa(x0, x1, fiada * 59, fiada * 59 + 57, z0, z1, 'tijolo', 2.5))
    p.append(cil((296, CANO_Y, 0), (287, CANO_Y, 0), 36, 'ferrugem', n=20))   # flange da entrada de ar
    return p


def _pedras(mat, n, raio, y0, r0, r1, semente, queda=25):
    rnd = random.Random(semente)
    p = []
    for _ in range(n):
        a, r = rnd.uniform(0, 2 * math.pi), raio * math.sqrt(rnd.random())
        c = (r * math.cos(a), y0 - (r / max(raio, 1)) ** 2 * queda, r * math.sin(a))
        d = [rnd.uniform(-1, 1), rnd.uniform(-0.5, 0.5), rnd.uniform(-1, 1)]
        m = math.sqrt(sum(v * v for v in d)) or 1.0
        h = rnd.uniform(9, 15)
        d = [v / m * h for v in d]
        p.append(cil(tuple(c[i] - d[i] for i in range(3)), tuple(c[i] + d[i] for i in range(3)), rnd.uniform(r0, r1), mat, n=5, r1=rnd.uniform(r0, r1) * 0.8))
    return p


def _carvao():
    return [_torno([(540, 0), (540, 150), (565, 195), (585, 170), (598, 110), (604, 0)], 'carvao', y=BASE, n=28)] + \
        _pedras('carvao', 44, 175, BASE + 606, 13, 21, 3)


def _brasa():
    return [_torno([(596, 0), (596, 80), (606, 55), (611, 0)], 'carvao', y=BASE, n=20)] + _pedras('carvao', 12, 70, BASE + 616, 9, 14, 5, queda=8)


def _fole():
    p = [caixa(560, 1010, 560, 582, -150, 150, 'tampo_x', 3.0)]                                          # tábua de baixo
    for k in range(4):                                                                                    # gomos de couro
        h = 140 if k % 2 == 0 else 122
        x1 = 1000 if k % 2 == 0 else 990
        a0, a1 = 582 + 18 * k / 4, 582 + 18 * (k + 1) / 4
        b0, b1 = 582 + 172 * k / 4, 582 + 172 * (k + 1) / 4
        p.append(frente([(575, a0), (x1, b0), (x1, b1), (575, a1)], -h, h, 'couro', 2.0))
    p.append(frente([(560, 600), (1010, 754), (1010, 776), (560, 622)], -150, 150, 'tampo_x', 3.0))      # tábua de cima
    p.append(frente([(1000, 752), (1130, 796), (1130, 818), (1000, 774)], -20, 20, 'pinho_x', 3.0))      # alavanca
    p.append(caixa(552, 578, 576, 628, -153, 153, 'couro', 2.5))                                          # couro da dobradiça
    p.append(cil((578, 592, 0), (500, CANO_Y + 2, 0), 31, 'ferrugem', n=18, r1=23))                       # bico
    p.append(cil((504, CANO_Y, 0), (282, CANO_Y, 0), 22, 'ferrugem', n=18))                               # cano de ar
    for x in (620, 960):                                                                                  # cavalete
        for sz in (-1, 1):
            p.append(caixa(x - 22, x + 22, 0, 560, sz * 120 - 22, sz * 120 + 22, 'pinho_y', 2.5))
    for sz in (-1, 1):
        z0, z1 = sorted((sz * 142, sz * 164))
        p.append(caixa(590, 990, 300, 345, z0, z1, 'pinho_x', 2.0))
    for x0 in (576, 982):
        p.append(caixa(x0, x0 + 22, 300, 345, -142, 142, 'pinho_z', 2.0))
    return p


def _bigorna():
    x, z, y = TOCO_X, TOCO_Z, TOCO_H
    toco = _torno([(0, 0), (0, TOCO_R + 30), (40, TOCO_R + 13), (120, TOCO_R + 3), (TOCO_H - 6, TOCO_R - 4), (TOCO_H, TOCO_R - 9), (TOCO_H, 0)], 'casca', x=x, z=z, n=28)
    pintar(toco, 'crua_y', lambda c, n: n[1] > 0.7)
    zc = z + 30
    trilho = perfil([(zc - 60, y), (zc + 60, y), (zc + 60, y + 12), (zc + 12, y + 22), (zc + 12, y + 72), (zc + 35, y + 80), (zc + 35, y + 112),
                     (zc - 35, y + 112), (zc - 35, y + 80), (zc - 12, y + 72), (zc - 12, y + 22), (zc - 60, y + 12)], x - 130, x + 110, 'trilho', 2.0)
    pintar(trilho, 'trilho_batido', lambda c, n: n[1] > 0.9 and c[1] > y + 100)
    p = [toco, trilho, cil((x + 108, y + 94, zc), (x + 215, y + 102, zc), 30, 'trilho', n=18, r1=7)]      # chifre
    for sx in (-90, 70):                                                                                  # pregos de linha
        for sz in (-52, 52):
            p.append(cil((x + sx, y + 12, zc + sz), (x + sx, y + 24, zc + sz), 11, 'ferrugem', n=8, r1=9))
    return p


def _ferramentas():
    y = TOCO_H
    p = [cil((-890, y + 20, 5), (-655, y + 20, 14), 13, 'faia_x', n=14, r1=15),                           # martelo no toco
         caixa(-662, -620, y, y + 40, -40, 68, 'ferro_preto', 4.0)]
    for dz, dz2 in ((0, 0), (18, -18)):                                                                   # tenaz apoiada na boca
        p.append(cil((-30, BASE + 606, 40 + dz), (360, BASE + 656, 300 + dz2), 5.5, 'ferro_preto', n=8))
    p.append(caixa(-48, -24, BASE + 598, BASE + 612, 30, 70, 'ferro_preto', 2.0))                          # mordentes
    return p


def montar():
    parte('fornalha', _fornalha(), origem=G(0, 0, 0), grupo='A')
    parte('carvao', _carvao(), origem=G(0, 0, 0), grupo='A')
    parte('brasa', _brasa(), origem=G(0, 0, 0), grupo='C')
    parte('fole', _fole(), origem=G(0, 0, 0), grupo='B')
    parte('bigorna', _bigorna(), origem=G(0, 0, 0), grupo='C')
    parte('ferramentas', _ferramentas(), origem=G(0, 0, 0), grupo='C')
