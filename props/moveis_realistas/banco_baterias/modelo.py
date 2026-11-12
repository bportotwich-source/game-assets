"""Banco de baterias: cavalete de caibros com duas baterias de carro na prateleira, ligadas em paralelo por
cabos grossos, e um quadro de compensado atrás com o controlador de carga (caixa de chapa com mostrador),
a chave de faca e a régua de bornes. Um telhadinho de tábua protege da chuva.
Medidas em mm, coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente."""
import math
import lib
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte, letreiro

PRAT = 190                  # em cima da prateleira das baterias
ALTO = 930


def _fio(pts, r, mat):
    return lib.fio([G(*p) for p in pts], r, mat, fechado=False)


def _estrutura():
    p = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            x, z = sx * 345, sz * 150
            p.append(caixa(x - 24, x + 24, 0, ALTO if sz < 0 else 420, z - 24, z + 24, 'pinho_y', 2.5))
        p.append(caixa(sx * 345 - 18, sx * 345 + 18, PRAT - 90, PRAT - 22, -126, 126, 'pinho_z', 2.0))    # travessas
        p.append(caixa(sx * 345 - 18, sx * 345 + 18, 340, 400, -126, 126, 'pinho_z', 2.0))
    for k, d in enumerate((0, 6, -4)):                                                                    # prateleira de três tábuas
        z0 = -170 + k * 114
        p.append(caixa(-385 - d, 385 + d, PRAT - 22, PRAT, z0, z0 + 110, 'tampo_x', 2.5))
    p.append(caixa(-321, 321, 450, ALTO - 30, -172, -160, 'compensado', 1.5))                            # quadro
    p.append(perfil([(-215, ALTO - 22), (95, ALTO - 62), (95, ALTO - 40), (-215, ALTO)], -410, 410, 'pinho_x', 2.0))   # telhadinho
    return p


def _bateria(x0):
    x1, y0, z0, z1 = x0 + 250, PRAT, -95, 85
    p = [caixa(x0, x1, y0, y0 + 160, z0, z1, 'plastico_preto', 5.0),
         caixa(x0 - 3, x1 + 3, y0 + 160, y0 + 182, z0 - 3, z1 + 3, 'plastico_bege', 4.0),
         letreiro('12 V', 36, (x0 + x1) / 2, y0 + 70, z1 + 0.4, 'tinta_branca')]
    for k in range(6):
        p.append(cil((x0 + 35 + k * 36, y0 + 182, 10), (x0 + 35 + k * 36, y0 + 188, 10), 13, 'plastico_amarelo', n=12))
    for x in (x0 + 38, x1 - 38):                                                                          # polos com garra
        p.append(cil((x, y0 + 182, -55), (x, y0 + 204, -55), 10, 'chumbo', n=14, r1=8.5))
        p.append(caixa(x - 17, x + 17, y0 + 190, y0 + 202, -72, -38, 'chumbo', 2.0))
    p.append(_fio([(x0 + 30, y0 + 150, z1 + 2), (x0 + 30, y0 + 215, z1 + 14), (x1 - 30, y0 + 215, z1 + 14), (x1 - 30, y0 + 150, z1 + 2)], 5.0, 'sisal'))   # alça
    return p


def _baterias():
    p = _bateria(-300) + _bateria(50)
    y = PRAT + 196
    for (xa, xb, mat) in ((-262, 88, 'isolante_vermelho'), (-88, 262, 'isolante_preto')):               # ligadas em paralelo
        p.append(_fio([(xa, y, -55), (xa, y + 40, -70), ((xa + xb) / 2, y + 62, -84), (xb, y + 40, -70), (xb, y, -55)], 6.5, mat))
    p.append(_fio([(88, y, -55), (110, y + 70, -110), (150, 470, -150), (150, 560, -152)], 6.5, 'isolante_vermelho'))   # sobem para o quadro
    p.append(_fio([(262, y, -55), (270, y + 70, -110), (225, 470, -150), (225, 560, -152)], 6.5, 'isolante_preto'))
    return p


def _quadro():
    z = -160
    p = [caixa(-270, -40, 580, 860, z, z + 75, 'chapa_cinza', 4.0)]                                       # controlador de carga
    zf = z + 75
    p.append(cil((-155, 770, zf), (-155, 770, zf + 6), 58, 'plastico_preto', n=26))                       # mostrador
    p.append(cil((-155, 770, zf + 6), (-155, 770, zf + 7.5), 52, 'mostrador', n=26))
    p.append(caixa(-156.5, -153.5, 770, 812, zf + 7.5, zf + 8.6, 'isolante_vermelho'))
    for k, mat in enumerate(('isolante_vermelho', 'plastico_amarelo', 'plastico_azul')):                # luzes
        p.append(cil((-215 + k * 60, 668, zf), (-215 + k * 60, 668, zf + 7), 9, mat, n=10))
    p.append(letreiro('CARGA', 22, -155, 612, zf + 0.4, 'tinta_preta'))
    for k in range(6):                                                                                   # frestas
        p.append(caixa(-272, -270, 600 + k * 40, 618 + k * 40, z + 15, z + 60, 'ferro_preto'))
    # chave de faca
    p.append(caixa(60, 240, 640, 850, z, z + 14, 'plastico_bege', 3.0))
    for x in (110, 190):
        p.append(caixa(x - 9, x + 9, 665, 690, z + 14, z + 44, 'latao', 1.0))
        p.append(caixa(x - 9, x + 9, 790, 815, z + 14, z + 44, 'latao', 1.0))
        p.append(caixa(x - 3, x + 3, 672, 812, z + 22, z + 40, 'cobre', 0.8))                            # lâminas fechadas
    p.append(caixa(95, 205, 812, 826, z + 26, z + 40, 'plastico_preto', 2.0))
    p.append(cil((150, 826, z + 33), (150, 826, z + 110), 15, 'plastico_preto', n=14, r1=18))            # cabo da chave
    # régua de bornes e a saída para a casa
    p.append(caixa(60, 240, 540, 590, z, z + 20, 'plastico_preto', 2.0))
    for k in range(4):
        p.append(cil((84 + k * 44, 565, z + 20), (84 + k * 44, 565, z + 25), 8, 'latao', n=10))
    p.append(_fio([(-40, 720, z + 40), (10, 735, z + 45), (60, 745, z + 20)], 5.0, 'isolante_preto'))
    p.append(_fio([(240, 565, z + 12), (300, 560, z + 14), (322, 420, -120), (322, 60, -110), (380, 8, -60)], 5.5, 'isolante_preto'))
    return p


def montar():
    parte('estrutura', _estrutura(), origem=G(0, 0, 0), grupo='A')
    parte('baterias', _baterias(), origem=G(0, 0, 0), grupo='B')
    parte('quadro', _quadro(), origem=G(0, 0, 0), grupo='B')
