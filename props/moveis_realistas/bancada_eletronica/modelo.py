"""Bancada de eletrônica: mesa de tábuas com prateleira alta e painel de compensado atrás, bateria de carro
embaixo ligada por cabos a uma régua de bornes, e em cima o que se usa no conserto: rádio aberto, placa de
circuito, ferro de solda no suporte, multímetro com pontas, carretéis de fio e de solda, gaveteiro de
pecinhas, luminária, chaves e alicate.
Medidas em mm, coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente (onde se senta)."""
import math
import lib
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte, letreiro
from lib import pintar

H = 760                     # em cima do tampo
XT, ZT = 750, 310
PRAT = 1080                 # em cima da prateleira alta
TOPO = 1290


def _torno(prof, mat, x=0, y=0, z=0, n=24, eixo=(0, 1, 0)):
    return lib.lathe(prof, mat, n=n, c0=G(x, y, z), eixo=G(*eixo))


def _fio(pts, r, mat):
    return lib.fio([G(*p) for p in pts], r, mat, fechado=False)


def _estrutura():
    p = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            x, z = sx * 690, sz * 255
            alto = TOPO if sz < 0 else H - 30
            p.append(caixa(x - 35, x + 35, 0, alto, z - 22, z + 22, 'pinho_y', 2.5))
        p.append(caixa(sx * 690 - 22, sx * 690 + 22, H - 130, H - 30, -233, 233, 'pinho_z', 2.0))     # travessas laterais
        p.append(caixa(sx * 690 - 22, sx * 690 + 22, 130, 200, -233, 233, 'pinho_z', 2.0))
    p.append(caixa(-655, 655, H - 130, H - 30, -277, -255, 'pinho_x', 2.0))                             # saia de trás
    p.append(caixa(-655, 655, H - 110, H - 30, 255, 277, 'pinho_x', 2.0))                               # saia da frente
    p.append(caixa(-712, 712, 200, 222, -240, 140, 'pinho_x', 2.0))                                     # prateleira de baixo (bateria)
    p.append(caixa(-725, 725, PRAT - 22, PRAT, -310, -110, 'pinho_x', 2.5))                             # prateleira alta
    p.append(caixa(-655, 655, H, TOPO - 20, -277, -268, 'compensado', 1.5))                             # painel de compensado
    p.append(caixa(-735, 735, TOPO - 20, TOPO + 3, -306, -226, 'pinho_x', 2.0))                             # cumeeira, cobre o topo dos pés
    return p


def _tampo():
    p = []
    for k, d in enumerate((0, 8, -5, 6)):
        z0 = -ZT + k * 156
        p.append(caixa(-XT - d, XT + (5 - d), H - 30, H, z0, z0 + 153, 'tampo_x', 2.5))
    return p


def _bateria():
    x0, x1, y0, z0, z1 = 300, 540, 222, -200, -25
    p = [caixa(x0, x1, y0, y0 + 150, z0, z1, 'plastico_preto', 5.0),
         caixa(x0 - 3, x1 + 3, y0 + 150, y0 + 172, z0 - 3, z1 + 3, 'plastico_bege', 4.0)]
    for k in range(6):                                                                                    # tampas das células
        p.append(cil((x0 + 30 + k * 36, y0 + 172, -112), (x0 + 30 + k * 36, y0 + 178, -112), 13, 'plastico_amarelo', n=12))
    for x, mat in ((x0 + 35, 'isolante_vermelho'), (x1 - 35, 'isolante_preto')):                           # polos e garras
        p.append(cil((x, y0 + 172, -160), (x, y0 + 194, -160), 10, 'chumbo', n=14, r1=8.5))
        p.append(caixa(x - 16, x + 16, y0 + 180, y0 + 192, -176, -144, 'chumbo', 2.0))
        p.append(_fio([(x, y0 + 190, -176), (x, y0 + 215, -215), (x + 40, y0 + 330, -262), (x + 60, H - 60, -262), (x + 60, H + 40, -262)], 5.0, mat))
    p.append(letreiro('12 V', 34, (x0 + x1) / 2, y0 + 70, z1 + 0.3, 'tinta_branca'))
    return p


def _radio(x0, z0):
    """Rádio de válvulas aberto, sem a tampa de cima: caixa de chapa, mostrador, botões e as tripas."""
    y, w, h, d = H, 330, 170, 210
    cx = caixa(x0, x0 + w, y, y + h, z0, z0 + d, 'chapa_cinza')
    cut(cx, caixa(x0 + 3, x0 + w - 3, y + 3, y + h + 5, z0 + 3, z0 + d - 3, 'chapa_cinza'))
    bevel(cx, 1.5)
    zf = z0 + d
    p = [cx,
         caixa(x0 + 24, x0 + 190, y + 86, y + 142, zf, zf + 2.5, 'chapa_creme', 1.0),                     # mostrador
         caixa(x0 + 30, x0 + 184, y + 92, y + 136, zf + 2.5, zf + 4.0, 'vidro_escuro'),
         caixa(x0 + 214, x0 + 306, y + 30, y + 142, zf, zf + 2.5, 'plastico_preto', 1.0),                 # tela do alto-falante
         caixa(x0 + 40, x0 + 130, y + 3, y + 96, z0 + 22, z0 + 110, 'plastico_preto', 4.0),               # transformador
         caixa(x0 + 34, x0 + 136, y + 30, y + 70, z0 + 16, z0 + 116, 'chapa_cinza', 2.0)]
    for k in range(9):
        p.append(caixa(x0 + 220 + k * 10, x0 + 224 + k * 10, y + 36, y + 136, zf + 2.5, zf + 5, 'chapa_cinza'))
    for k, xb in enumerate((x0 + 50, x0 + 107, x0 + 164)):                                                # botões
        p.append(cil((xb, y + 44, zf), (xb, y + 44, zf + 20), 17, 'plastico_bege', n=18, r1=15))
        p.append(caixa(xb - 1.2, xb + 1.2, y + 44, y + 60, zf + 20, zf + 21.5, 'isolante_preto'))
    for k, (xv, zv) in enumerate(((x0 + 180, z0 + 50), (x0 + 240, z0 + 60), (x0 + 290, z0 + 110), (x0 + 200, z0 + 130))):   # válvulas e capacitores
        if k < 3:
            p.append(cil((xv, y + 3, zv), (xv, y + 22, zv), 17, 'plastico_preto', n=14))
            p.append(_torno([(22, 0), (22, 14), (80, 14), (96, 9), (104, 0)], 'vidro_escuro', xv, y, zv, n=14))
        else:
            p.append(cil((xv, y + 3, zv), (xv, y + 95, zv), 19, 'chumbo', n=16))
    return p


def _placa(x0, z0):
    y = H + 12
    p = [caixa(x0, x0 + 190, y, y + 1.8, z0, z0 + 120, 'placa_verde')]
    for dx, dz in ((6, 6), (184, 6), (6, 114), (184, 114)):                                               # espaçadores
        p.append(cil((x0 + dx, H, z0 + dz), (x0 + dx, y + 4, z0 + dz), 3.6, 'latao', n=8))
    for k in range(3):                                                                                    # circuitos integrados
        p.append(caixa(x0 + 24 + k * 50, x0 + 56 + k * 50, y + 1.8, y + 7, z0 + 70, z0 + 82, 'plastico_preto', 0.6))
    for k in range(4):                                                                                    # capacitores
        xc, zc = x0 + 30 + k * 38, z0 + 30
        p.append(cil((xc, y + 1.8, zc), (xc, y + 20 + 5 * (k % 2), zc), 6.5 + (k % 2), 'plastico_azul', n=12))
    for k in range(7):                                                                                    # resistores deitados
        zc = z0 + 96 + (k % 2) * 10
        p.append(cil((x0 + 22 + k * 22, y + 4.5, zc), (x0 + 34 + k * 22, y + 4.5, zc), 2.4, 'plastico_bege', n=8))
    p.append(caixa(x0 + 160, x0 + 184, y + 1.8, y + 16, z0 + 36, z0 + 84, 'plastico_bege', 1.2))          # borne
    return p


def _solda(x0, z0):
    """Ferro de solda deitado no suporte de mola, e o carretel de solda ao lado."""
    y = H
    p = [caixa(x0, x0 + 110, y, y + 8, z0, z0 + 70, 'chapa_cinza', 2.0)]
    helice = []
    for i in range(49):                                                                                   # mola do suporte
        a = i * 2 * math.pi / 8
        t = i / 48
        helice.append((x0 + 30 + 22 * math.cos(a), y + 30 + 60 * t + 0 * a, z0 + 35 + 22 * math.sin(a) + 50 * t))
    p.append(_fio(helice, 1.6, 'chumbo'))
    a, b = (x0 + 30, y + 26, z0 + 30), (x0 + 30, y + 150, z0 + 134)                                        # o ferro, dentro da mola
    d = tuple(b[i] - a[i] for i in range(3))
    pt = lambda t: tuple(a[i] + d[i] * t for i in range(3))
    p += [cil(pt(0.0), pt(0.10), 2.2, 'cobre', n=8, r1=4.0), cil(pt(0.10), pt(0.42), 4.0, 'chumbo', n=10),
          cil(pt(0.42), pt(0.50), 11, 'plastico_preto', n=14, r1=13), cil(pt(0.50), pt(1.0), 13, 'plastico_azul', n=14, r1=10),
          _fio([pt(1.0), pt(1.12), (b[0] + 40, y + 60, b[2] + 60), (b[0] + 130, y + 5, b[2] + 30), (b[0] + 260, y + 5, b[2] - 60)], 2.8, 'isolante_preto')]
    xs, zs = x0 + 150, z0 + 20                                                                            # carretel de solda
    p.append(_torno([(0, 0), (0, 24), (3, 24), (3, 9), (33, 9), (33, 24), (36, 24), (36, 0)], 'plastico_bege', xs, y, zs, n=18))
    p.append(_torno([(3, 9), (3, 19), (33, 19), (33, 9)], 'chumbo', xs, y, zs, n=18))
    return p


def _multimetro(x0, z0):
    y = H
    corpo = caixa(x0, x0 + 86, y, y + 38, z0, z0 + 160, 'plastico_amarelo', 7.0)
    p = [corpo,
         caixa(x0 + 8, x0 + 78, y + 30, y + 40, z0 + 8, z0 + 152, 'plastico_preto', 2.5),
         caixa(x0 + 16, x0 + 70, y + 40, y + 41.5, z0 + 16, z0 + 50, 'vidro_escuro'),
         cil((x0 + 43, y + 40, z0 + 96), (x0 + 43, y + 50, z0 + 96), 23, 'plastico_preto', n=20, r1=21),
         caixa(x0 + 40.5, x0 + 45.5, y + 50, y + 53, z0 + 76, z0 + 116, 'plastico_bege', 1.0)]
    for k, mat in enumerate(('isolante_vermelho', 'isolante_preto')):
        xb = x0 + 28 + k * 30
        p.append(cil((xb, y + 40, z0 + 140), (xb, y + 52, z0 + 140), 5.0, mat, n=10))
        s = 1 if k == 0 else -1
        fim = (x0 + 43 + s * 150, y + 6, z0 + 60 - 110 * k)
        p.append(_fio([(xb, y + 52, z0 + 140), (xb, y + 70, z0 + 150), (xb + s * 40, y + 30, z0 + 190), (xb + s * 110, y + 4, z0 + 150), fim], 2.0, mat))
        p.append(cil(fim, (fim[0] + s * 70, y + 6, fim[2] - 20), 5.0, mat, n=10, r1=3.5))                  # ponta de prova
        p.append(cil((fim[0] + s * 70, y + 6, fim[2] - 20), (fim[0] + s * 96, y + 6, fim[2] - 27), 1.2, 'chumbo', n=6))
    return p


def _carretel(x, y, z, mat):
    return [_torno([(0, 0), (0, 52), (5, 52), (5, 16), (75, 16), (75, 52), (80, 52), (80, 0)], 'plastico_preto', x, y, z, n=22),
            _torno([(5, 16), (5, 40), (40, 43), (75, 40), (75, 16)], mat, x, y, z, n=22)]


def _gaveteiro(x0):
    """Gaveteiro de pecinhas na prateleira alta: 4 × 3 gavetinhas."""
    y, z0, z1 = PRAT, -290, -130
    p = [caixa(x0, x0 + 360, y, y + 170, z0, z1, 'plastico_azul', 3.0)]
    for i in range(4):
        for j in range(3):
            gx, gy = x0 + 8 + i * 87, y + 8 + j * 53
            p.append(caixa(gx, gx + 83, gy, gy + 49, z1 - 2, z1 + 5, 'plastico_bege', 2.0))
            p.append(caixa(gx + 28, gx + 55, gy + 30, gy + 37, z1 + 5, z1 + 13, 'plastico_bege', 1.5))
    return p


def _luminaria(x, z):
    y = PRAT
    p = [cil((x, y, z), (x, y + 18, z), 70, 'chapa_cinza', n=24, r1=64),
         cil((x, y + 18, z), (x + 30, y + 150, z + 40), 7, 'chumbo', n=10),
         cil((x + 30, y + 150, z + 40), (x + 120, y + 60, z + 190), 7, 'chumbo', n=10),
         cil((x + 30, y + 150, z + 40), (x + 30, y + 150, z + 40.1), 11, 'chumbo', n=10)]
    a, b = (x + 105, y + 82, z + 165), (x + 150, y - 10, z + 240)                                          # cúpula virada para o tampo
    d = [b[i] - a[i] for i in range(3)]
    m = math.sqrt(sum(v * v for v in d))
    e = tuple(v / m for v in d)
    p.append(lib.lathe([(0, 0), (0, 24), (30, 30), (110, 78), (112, 74), (34, 26), (6, 0)], 'chapa_cinza', n=24, c0=G(*a), eixo=G(*e)))
    return p


def _miudezas():
    y = H
    p = []
    lx, lz = -610, -200                                                                                   # lata com chaves de fenda
    lata = cil((lx, y, lz), (lx, y + 110, lz), 40, 'lata', n=22)
    cut(lata, cil((lx, y + 8, lz), (lx, y + 120, lz), 38.5, 'lata', n=22))
    p.append(lata)
    for k, mat in enumerate(('isolante_vermelho', 'plastico_amarelo', 'plastico_azul', 'isolante_preto')):
        a = k * 1.7
        bx, bz = lx + 14 * math.cos(a), lz + 14 * math.sin(a)
        tx, tz = lx + 34 * math.cos(a), lz + 34 * math.sin(a)
        mid = (bx + (tx - bx) * 0.55, y + 120, bz + (tz - bz) * 0.55)
        topo = (tx + (tx - bx) * 0.9, y + 215 + 8 * k, tz + (tz - bz) * 0.9)
        p.append(cil((bx, y + 12, bz), mid, 2.6, 'aco_ferramenta', n=8))
        p.append(cil(mid, topo, 10, mat, n=10, r1=12))
    for s in (-1, 1):                                                                                     # alicate deitado
        p.append(cil((-430, y + 5, 150 + s * 3), (-380, y + 5, 150 + s * 2), 5, 'aco_ferramenta', n=8, r1=3))
        p.append(cil((-430, y + 6, 150 - s * 3), (-530, y + 6, 150 + s * 28), 6.5, 'isolante_vermelho', n=10))
    p.append(cil((-430, y, 150), (-430, y + 11, 150), 9, 'aco_ferramenta', n=12))
    xb = 360                                                                                              # régua de bornes no painel, onde chegam os cabos da bateria
    p.append(caixa(xb - 30, xb + 270, y + 30, y + 70, -268, -250, 'plastico_preto', 2.0))
    for k in range(6):
        p.append(cil((xb + k * 48, y + 50, -250), (xb + k * 48, y + 50, -245), 7, 'latao', n=10))
    return p


def _ferramentas():
    return (_radio(-330, -240) + _placa(-160, 60) + _solda(110, 10) + _multimetro(430, 20) + _carretel(-560, H, 40, 'isolante_vermelho')
            + _carretel(-200, PRAT, -210, 'cobre') + _gaveteiro(40) + _luminaria(-520, -210) + _miudezas())


def montar():
    parte('estrutura', _estrutura(), origem=G(0, 0, 0), grupo='A')
    parte('tampo', _tampo(), origem=G(0, 0, 0), grupo='A')
    parte('bateria', _bateria(), origem=G(0, 0, 0), grupo='B')
    parte('ferramentas', _ferramentas(), origem=G(0, 0, 0), grupo='B')
