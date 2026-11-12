"""Lâmpada improvisada no poste: caibro em pé numa cruzeta de tábuas com quatro mãos-francesas, braço no alto
com o refletor feito de lata e a lâmpada pendurada, interruptor de caixinha e o fio descendo grampeado até
um rolo no pé.
Medidas em mm, coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente (para onde o braço aponta)."""
import math
import lib
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte, letreiro

ALTO = 1900
BRACO = 300                 # até onde o braço vai para a frente
LUZ = (0, 1640, BRACO)      # centro da lâmpada (vai para o catálogo como ponto_luz)


def _fio(pts, r, mat):
    return lib.fio([G(*p) for p in pts], r, mat, fechado=False)


def _poste():
    p = [caixa(-36, 36, 40, ALTO, -36, 36, 'pinho_y', 3.0),                                               # caibro
         caixa(-330, 330, 0, 40, -48, 48, 'pinho_x', 2.5),                                                # cruzeta
         caixa(-48, 48, 0, 40, -330, -48, 'pinho_z', 2.5),
         caixa(-48, 48, 0, 40, 48, 330, 'pinho_z', 2.5)]
    for a in range(4):                                                                                   # mãos-francesas
        c, s = round(math.cos(a * math.pi / 2)), round(math.sin(a * math.pi / 2))
        p.append(cil((c * 280, 42, s * 280), (c * 30, 430, s * 30), 24, 'pinho_y', n=4))
    p.append(caixa(-28, 28, ALTO - 110, ALTO - 50, 36, BRACO + 40, 'pinho_z', 2.5))                       # braço
    p.append(cil((0, ALTO - 300, 40), (0, ALTO - 112, BRACO - 30), 20, 'pinho_y', n=4))                   # escora do braço
    for y in (300, 700, 1100, 1500):                                                                     # pregos tortos à mostra
        p.append(cil((-20, y, 36), (-20, y, 41), 4, 'ferrugem', n=6))
    p.append(caixa(-60, 60, 0, 6, -60, 60, 'ferrugem', 1.0))                                              # chapa no pé
    return p


def _luminaria():
    x, y, z = LUZ
    topo = ALTO - 110
    p = [_fio([(0, topo, z), (0, y + 105, z)], 3.2, 'isolante_preto'),                                    # pendente
         cil((0, y + 60, z), (0, y + 108, z), 19, 'plastico_preto', n=14, r1=15)]                         # soquete
    # refletor: fundo de lata cortada, aberto para baixo
    p.append(lib.lathe([(0, 0), (0, 24), (26, 30), (118, 112), (122, 109), (30, 25), (5, 0)], 'lata', n=26, c0=G(0, y + 100, z), eixo=G(0, -1, 0)))
    # lâmpada
    p.append(lib.lathe([(0, 0), (0, 13), (26, 15), (48, 30), (74, 36), (98, 26), (108, 0)], 'esmalte_branco', n=20, c0=G(0, y + 62, z), eixo=G(0, -1, 0)))
    # fio: do braço desce o poste até o interruptor e segue até o rolo no pé
    p.append(_fio([(0, topo, z), (8, topo + 68, z - 20), (8, topo + 68, 60), (22, topo + 30, 40), (40, 1560, 22), (40, 1262, 22)], 3.2, 'isolante_preto'))
    p.append(caixa(36, 62, 1180, 1262, -26, 26, 'plastico_bege', 4.0))                                    # interruptor
    p.append(caixa(62, 68, 1206, 1236, -9, 9, 'plastico_preto', 1.5))
    p.append(_fio([(40, 1180, 22), (40, 420, 22), (60, 120, 60), (150, 46, 150)], 3.2, 'isolante_preto'))
    for y2 in (1420, 900, 560):                                                                          # grampos
        p.append(caixa(36, 46, y2 - 4, y2 + 4, 14, 30, 'zincado', 0.8))
    # rolo de fio sobrando no pé
    aro = []
    for i in range(33):
        a = i * 2 * math.pi / 8
        aro.append((150 + 70 * math.cos(a), 46 + i * 0.9, 150 + 70 * math.sin(a)))
    p.append(_fio(aro, 3.2, 'isolante_preto'))
    p.append(_fio([aro[-1], (240, 12, 180), (330, 6, 240)], 3.2, 'isolante_preto'))
    return p


def montar():
    parte('poste', _poste(), origem=G(0, 0, 0), grupo='A')
    parte('luminaria', _luminaria(), origem=G(0, 0, 0), grupo='A')
