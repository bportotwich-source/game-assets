"""Carregador de pilhas: mesinha de caibros com o carregador em cima (caixa de plástico com quatro berços e
pilhas dentro, luz de carga), a fonte, uma lata com pilhas soltas e um rolo de fio na prateleira de baixo.
Medidas em mm, coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente."""
import math
import lib
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte, letreiro

H = 640                     # em cima do tampo


def _fio(pts, r, mat):
    return lib.fio([G(*p) for p in pts], r, mat, fechado=False)


def _torno(prof, mat, x, y, z, n=20):
    return lib.lathe(prof, mat, n=n, c0=G(x, y, z), eixo=G(0, 1, 0))


def _pilha(x, y, z, mat, deitada=True, dx=1.0, dz=0.0):
    """Pilha AA (50 × 14 mm), deitada ao longo de (dx, dz) ou em pé."""
    if deitada:
        a, b = (x - 24 * dx, y, z - 24 * dz), (x + 24 * dx, y, z + 24 * dz)
        c = (x + 26.5 * dx, y, z + 26.5 * dz)
    else:
        a, b, c = (x, y, z), (x, y + 48, z), (x, y + 50.5, z)
    return [cil(a, b, 7.0, mat, n=10), cil(b, c, 2.6, 'zincado', n=8)]


def _estrutura():
    p = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            x, z = sx * 185, sz * 125
            p.append(caixa(x - 19, x + 19, 0, H - 24, z - 19, z + 19, 'pinho_y', 2.0))
        p.append(caixa(sx * 185 - 14, sx * 185 + 14, H - 90, H - 24, -106, 106, 'pinho_z', 1.5))
        p.append(caixa(sx * 185 - 14, sx * 185 + 14, 170, 220, -106, 106, 'pinho_z', 1.5))
    p.append(caixa(-166, 166, H - 90, H - 24, -139, -125, 'pinho_x', 1.5))
    p.append(caixa(-166, 166, H - 90, H - 24, 125, 139, 'pinho_x', 1.5))
    for k, d in enumerate((0, 5)):                                                                        # tampo de duas tábuas
        z0 = -160 + k * 162
        p.append(caixa(-225 - d, 225 + d, H - 24, H, z0, z0 + 158, 'tampo_x', 2.5))
    p.append(caixa(-204, 204, 220, 238, -120, 120, 'pinho_x', 2.0))                                       # prateleira de baixo
    return p


def _carregador():
    y = H
    x0, x1, z0, z1 = -150, 70, -40, 90
    cx = caixa(x0, x1, y, y + 46, z0, z1, 'plastico_bege', 5.0)
    p = []
    for k in range(4):                                                                                   # berços
        xb = x0 + 34 + k * 46
        cut(cx, caixa(xb - 9, xb + 9, y + 26, y + 60, z0 + 26, z1 - 14, 'plastico_bege'))
        p += _pilha(xb, y + 33, (z0 + 26 + z1 - 14) / 2, ('plastico_azul', 'chapa_escura', 'plastico_azul', 'cobre')[k], True, 0.0, 1.0)
        p.append(caixa(xb - 5, xb + 5, y + 28, y + 40, z1 - 16, z1 - 14, 'zincado'))                     # mola
    p.append(cx)
    p.append(caixa(x0, x1, y + 46, y + 48, z0, z0 + 22, 'plastico_preto', 1.0))                           # faixa das luzes
    for k in range(4):
        p.append(cil((x0 + 34 + k * 46, y + 48, z0 + 11), (x0 + 34 + k * 46, y + 51, z0 + 11), 4.5, 'isolante_vermelho' if k % 2 else 'plastico_amarelo', n=8))
    p.append(letreiro('CARGA AA', 15, (x0 + x1) / 2, y + 12, z1 + 0.4, 'tinta_preta'))
    # fonte e os fios
    p.append(caixa(110, 195, y, y + 62, -120, -40, 'plastico_preto', 6.0))
    p.append(_fio([(110, y + 20, -80), (95, y + 8, -70), (82, y + 8, -30), (70, y + 16, -10)], 3.0, 'isolante_preto'))
    p.append(_fio([(195, y + 25, -80), (232, y + 20, -100), (238, 400, -150), (228, 20, -150), (290, 6, -120)], 3.5, 'isolante_preto'))
    # lata com pilhas soltas
    lx, lz = 150, 70
    lata = cil((lx, y, lz), (lx, y + 85, lz), 37, 'lata', n=20)
    cut(lata, cil((lx, y + 6, lz), (lx, y + 95, lz), 35.5, 'lata', n=20))
    p.append(lata)
    for k, mat in enumerate(('plastico_azul', 'cobre', 'chapa_escura', 'plastico_azul', 'cobre')):
        a = k * 1.26
        p += _pilha(lx + 18 * math.cos(a), y + 44 + 3 * k, lz + 18 * math.sin(a), mat, False)
    p += _pilha(-175, y + 7, 120, 'cobre', True, 0.9, 0.44)
    p += _pilha(-120, y + 7, 128, 'plastico_azul', True, 1.0, 0.0)
    # rolo de fio na prateleira de baixo
    p.append(_torno([(0, 0), (0, 70), (6, 70), (6, 20), (70, 20), (70, 70), (76, 70), (76, 0)], 'plastico_preto', -80, 238, 10))
    p.append(_torno([(6, 20), (6, 52), (38, 56), (70, 52), (70, 20)], 'isolante_vermelho', -80, 238, 10))
    return p


def montar():
    parte('estrutura', _estrutura(), origem=G(0, 0, 0), grupo='A')
    parte('carregador', _carregador(), origem=G(0, 0, 0), grupo='A')
