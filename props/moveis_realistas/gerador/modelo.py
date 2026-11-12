"""Gerador portátil a gasolina: quadro de tubo preto, tanque vermelho em cima, motor de um cilindro com aletas
e partida de corda, alternador, escapamento com proteção e painel com duas tomadas, disjuntor e voltímetro.
Medidas em mm, coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente (o lado do painel)."""
import math
import lib
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte, letreiro

X, Z, H = 330, 250, 540          # meia largura e meia profundidade do quadro, altura


def _torno(prof, mat, c0, eixo, n=24):
    return lib.lathe(prof, mat, n=n, c0=G(*c0), eixo=G(*eixo))


def _fio(pts, r, mat, fechado=False):
    return lib.fio([G(*p) for p in pts], r, mat, fechado=fechado)


def _estrutura():
    p = []
    for z in (-Z, Z):                                                                                    # dois arcos de tubo
        laco = lib.caminho_arred([G(-X, 45, z), G(X, 45, z), G(X, H, z), G(-X, H, z)], 60, n=6, fechado=True)
        p.append(lib.fio(laco, 14, 'ferro_preto', fechado=True, res=4))
    for x, y in ((-X + 60, 45), (X - 60, 45), (-X, H - 60), (X, H - 60), (-X, 300), (X, 300)):          # travessas
        p.append(cil((x, y, -Z), (x, y, Z), 12, 'ferro_preto', n=12))
    p.append(caixa(-285, 285, 52, 60, -205, 205, 'chapa_escura', 2.0))                                  # bandeja
    for x in (-X + 60, X - 60):
        for z in (-Z, Z):                                                                                # pés de borracha
            p.append(cil((x, 0, z), (x, 34, z), 26, 'borracha', n=14, r1=20))
    return p


def _tanque():
    t = caixa(-290, 290, 405, 522, -200, 200, 'esmalte_vermelho', 34.0)
    p = [t,
         cil((130, 518, 10), (130, 530, 10), 46, 'zincado', n=20),                                        # bocal
         cil((130, 530, 10), (130, 548, 10), 42, 'plastico_preto', n=20, r1=38),                          # tampa
         cil((-120, 520, 60), (-120, 527, 60), 30, 'plastico_preto', n=18),                               # marcador de nível
         cil((-120, 527, 60), (-120, 528.5, 60), 25, 'mostrador', n=18),
         caixa(-121.5, -118.5, 528.5, 529.6, 44, 62, 'isolante_vermelho'),
         letreiro('GASOLINA', 30, 0, 448, 200.4, 'tinta_branca')]
    for x in (-250, 250):                                                                                # cintas que prendem o tanque
        p.append(caixa(x - 14, x + 14, 400, 524, -203, 203, 'zincado', 1.0))
    return p


def _motor():
    p = [caixa(-265, -25, 60, 250, -150, 110, 'aluminio', 10.0),                                          # cárter
         caixa(-225, -65, 250, 300, -120, 70, 'aluminio', 6.0)]                                           # cilindro
    for k in range(7):                                                                                   # aletas
        p.append(caixa(-240, -50, 304 + k * 13, 310 + k * 13, -135, 85, 'aluminio', 1.2))
    p.append(caixa(-215, -75, 392, 404, -110, 60, 'aluminio', 3.0))                                      # cabeçote
    p.append(cil((-145, 404, -25), (-145, 432, -25), 9, 'esmalte_branco', n=10))                         # vela
    p.append(_fio([(-145, 432, -25), (-145, 450, -10), (-80, 400, 80), (-40, 300, 100)], 4.0, 'isolante_preto'))
    # partida de corda na frente
    p.append(cil((-145, 160, 110), (-145, 160, 150), 98, 'plastico_preto', n=28, r1=90))
    for k in range(10):
        a = k * math.pi / 5
        p.append(cil((-145 + 60 * math.cos(a), 160 + 60 * math.sin(a), 150), (-145 + 60 * math.cos(a), 160 + 60 * math.sin(a), 152.5), 9, 'chapa_escura', n=8))
    p.append(cil((-70, 228, 152), (-70, 228, 168), 9, 'plastico_preto', n=10))                           # punho da corda
    p.append(cil((-98, 228, 172), (-42, 228, 172), 11, 'borracha', n=12))
    # filtro de ar e carburador
    p.append(caixa(-110, -5, 262, 392, 80, 185, 'plastico_preto', 12.0))
    for k in range(5):
        p.append(caixa(-100, -15, 280 + k * 20, 288 + k * 20, 185, 188, 'chapa_escura'))
    p.append(cil((-60, 262, 130), (-60, 235, 130), 16, 'latao_fosco', n=12))
    # escapamento atrás, com a proteção furada
    p.append(cil((-250, 345, -185), (-30, 345, -185), 52, 'chapa_fogao', n=20))
    p.append(cil((-30, 345, -185), (-5, 345, -185), 16, 'chapa_fogao', n=12))
    p.append(_fio([(-140, 300, -120), (-140, 320, -150), (-140, 345, -160)], 15.0, 'chapa_fogao'))
    for k in range(6):
        p.append(caixa(-245 + k * 40, -233 + k * 40, 290, 400, -244, -240, 'ferrugem'))
    p.append(caixa(-250, -25, 290, 298, -244, -238, 'ferrugem'))
    p.append(caixa(-250, -25, 392, 400, -244, -238, 'ferrugem'))
    # alternador à direita
    p.append(cil((-25, 180, -20), (10, 180, -20), 70, 'aluminio', n=20))
    p.append(cil((10, 180, -20), (250, 180, -20), 118, 'chapa_escura', n=28))
    p.append(cil((250, 180, -20), (278, 180, -20), 104, 'ferro_preto', n=28, r1=80))
    for k in range(12):                                                                                  # grade de ventilação
        a = k * math.pi / 6
        p.append(caixa(40, 46, 180 + 119 * math.cos(a) - 3, 180 + 119 * math.cos(a) + 3, -20 + 119 * math.sin(a) - 3, -20 + 119 * math.sin(a) + 3, 'ferro_preto'))
    p.append(caixa(20, 240, 60, 75, -110, 70, 'ferro_preto', 2.0))                                       # berço
    return p


def _painel():
    z = 228
    p = [caixa(35, 295, 268, 398, 205, z, 'chapa_cinza', 3.0)]
    for x in (85, 150):                                                                                  # tomadas
        p.append(cil((x, 345, z), (x, 345, z + 7), 24, 'plastico_preto', n=18))
        for dx in (-8, 8):
            p.append(caixa(x + dx - 2, x + dx + 2, 339, 351, z + 7, z + 7.6, 'latao'))
    p.append(cil((230, 350, z), (230, 350, z + 5), 30, 'plastico_preto', n=20))                          # voltímetro
    p.append(cil((230, 350, z + 5), (230, 350, z + 6), 26, 'mostrador', n=20))
    p.append(caixa(229, 231, 350, 372, z + 6, z + 6.8, 'isolante_vermelho'))
    p.append(caixa(214, 246, 284, 314, z, z + 6, 'plastico_preto', 2.0))                                  # chave liga-desliga
    p.append(caixa(220, 240, 296, 312, z + 6, z + 14, 'isolante_vermelho', 2.0))
    p.append(caixa(70, 110, 286, 304, z, z + 9, 'plastico_preto', 2.0))                                   # disjuntor
    p.append(letreiro('2000 W', 20, 160, 287, z + 0.4, 'tinta_preta'))
    p.append(_fio([(165, 268, 215), (165, 230, 190), (150, 200, 120)], 7.0, 'isolante_preto'))
    return p


def montar():
    parte('estrutura', _estrutura(), origem=G(0, 0, 0), grupo='A')
    parte('tanque', _tanque(), origem=G(0, 0, 0), grupo='A')
    parte('motor', _motor(), origem=G(0, 0, 0), grupo='B')
    parte('painel', _painel(), origem=G(0, 0, 0), grupo='B')
