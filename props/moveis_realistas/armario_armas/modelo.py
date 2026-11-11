"""Armário de armas de aço (delegacia, quartel): duas portas com venezianas, maçaneta e fechadura;
dentro, bandeja de borracha para as coronhas, barra com 5 berços para os canos, prateleira
forrada de feltro para pistolas e prateleira de munição. Medidas em mm, coordenadas do jogo
(ver ../base.py). Largura 1,0 m, altura 1,9 m, profundidade 0,5 m: as mesmas do armário antigo."""
import math
from base import G, caixa, cil, planta, perfil, frente, letreiro, cut, bevel, parte
from lib import pintar

W, H = 500, 1900            # meia largura, altura
ZT, ZF = -250, 205          # fundo e frente da carcaça
E = 15                      # parede (chapa dobrada, dupla)
ZP0, ZP1 = 207, 227         # porta fechada
REBAIXO = 224               # fundo do painel estampado da porta
EIXO_Z = 217                # eixo das dobradiças
VAGAS_X = (-360, -180, 0, 180, 360)
BANDEJA_Y = 136             # onde a coronha apoia
BARRA_Y = 757               # meio da barra dos canos
BERCO_Z = -150              # centro do berço do cano
PRAT1_Y, PRAT2_Y = 1309, 1609   # em cima do feltro
DOBRADICAS_Y = (250, 950, 1650)


def _carcaca():
    o = caixa(-W, W, 60, H, ZT, ZF, 'chapa_verde')
    cut(o, caixa(-W + E, W - E, 60 + E, H - E, ZT + 12, ZF + 5, 'chapa_verde'))
    bevel(o, 1.6)
    # por dentro a pintura é clara
    pintar(o, 'chapa_clara', lambda c, n: abs(c[2]) < W - E + 0.6 and 60 + E - 0.6 < c[1] < H - E + 0.6 and -ZF + 1 < c[0] < -(ZT + 12) + 0.6)
    pecas = [o, caixa(-W + 8, W - 8, 0, 62, ZT + 8, ZF - 12, 'chapa_escura', 1.6)]
    for s in (-1, 1):
        for y in DOBRADICAS_Y:                       # aba da dobradiça presa na lateral, com 3 parafusos
            x0, x1 = sorted((s * W, s * (W + 3)))
            pecas.append(caixa(x0, x1, y - 36, y + 36, 150, ZF + 4, 'zincado', 0.8))
            for dy in (-24, 0, 24):
                pecas.append(cil((s * (W + 3), y + dy, 172), (s * (W + 5), y + dy, 172), 4.5, 'zincado', n=10, r1=3.6))
    return pecas


def _berco(x, r):
    """Contorno em U do berço (aberto para a frente), raio r."""
    z0 = -100
    return [(x + r, z0)] + [(x + r * math.cos(math.radians(a)), BERCO_Z - r * math.sin(math.radians(a))) for a in range(0, 181, 15)] + [(x - r, z0)]


def _interior():
    pecas = [caixa(-W + E, W - E, 60 + E, 128, ZT + 12, 160, 'chapa_escura', 1.6),              # bandeja das coronhas
             caixa(-W + E + 6, W - E - 6, 128, BANDEJA_Y, ZT + 18, 154, 'borracha', 1.2)]
    for k in range(6):                                                                         # nervuras entre as armas
        x = -450 + k * 180
        pecas.append(caixa(x - 5, x + 5, BANDEJA_Y - 1, BANDEJA_Y + 16, ZT + 18, 154, 'borracha', 2.0))
    # barra dos canos: pente de 5 berços, forrados de borracha
    pts = [(-W + E, ZT + 12), (W - E, ZT + 12), (W - E, -100)]
    for x in reversed(VAGAS_X):
        pts += _berco(x, 35)
    pts += [(-W + E, -100)]
    pecas.append(planta(pts, BARRA_Y - 15, BARRA_Y + 15, 'chapa_escura', 1.4))
    for x in VAGAS_X:
        fora, dentro = _berco(x, 35), _berco(x, 30)
        pecas.append(planta(fora + dentro[::-1], BARRA_Y - 20, BARRA_Y + 20, 'borracha', 1.2))
    for y, yf in ((1290, PRAT1_Y), (1590, PRAT2_Y)):                                           # prateleiras
        pecas.append(caixa(-W + E, W - E, y, y + 15, ZT + 12, 185, 'chapa_clara', 1.4))
        pecas.append(caixa(-W + E, W - E, y, y + 34, 183, 195, 'chapa_clara', 1.4))            # aba da frente
        pecas.append(caixa(-W + E + 6, W - E - 6, y + 15, yf, ZT + 18, 180, 'feltro', 1.0))
        for s in (-1, 1):                                                                      # cantoneiras
            pecas.append(perfil([(ZT + 14, y), (ZT + 14, y - 70), (ZT + 84, y)], s * (W - E) - 3, s * (W - E) + 3, 'zincado', 0.8))
    # berços das pistolas: calço baixo de feltro para cada uma
    for x in (-360, -120, 120, 360):
        pecas.append(perfil([(-70, PRAT1_Y - 1), (-70, PRAT1_Y + 14), (-52, PRAT1_Y + 14), (-40, PRAT1_Y - 1)], x - 110, x + 110, 'feltro', 1.5))
    return pecas


def _porta(lado):
    """lado = -1 (esquerda) ou +1 (direita). Devolve (peças, origem na dobradiça)."""
    x0, x1 = sorted((lado * (W - 2), lado * 1.5))
    xc = (x0 + x1) / 2
    f = caixa(x0, x1, 68, H - 7, ZP0, ZP1, 'chapa_verde')
    cut(f, caixa(x0 + 45, x1 - 45, 68 + 45, H - 7 - 45, REBAIXO, ZP1 + 5, 'chapa_verde'))      # painel estampado
    bevel(f, 1.6)
    pintar(f, 'chapa_clara', lambda c, n: n[0] > 0.9 and c[0] > -ZP0 - 0.5)                    # face de dentro
    pecas = [f, caixa(xc - 45, xc + 45, 150, H - 90, ZP0 - 9, ZP0 + 1, 'chapa_clara', 1.6)]    # reforço por dentro
    for y0 in (190, 1560):                                                                     # venezianas
        for k in range(6):
            y = y0 + k * 32
            v = perfil([(REBAIXO - 1, y + 22), (REBAIXO + 8, y + 6), (REBAIXO + 8, y), (REBAIXO - 1, y)], xc - 125, xc + 125, 'chapa_veneziana', 0.8)
            pintar(v, 'tinta_preta', lambda c, n: n[1] < -0.9)
            pecas.append(v)
    for y in DOBRADICAS_Y:                                                                     # canhões das dobradiças
        pecas.append(cil((lado * W, y - 36, EIXO_Z), (lado * W, y + 36, EIXO_Z), 8.5, 'zincado', n=16))
        for yy in (y - 37.5, y + 37.5):
            pecas.append(cil((lado * W, yy - 2.5, EIXO_Z), (lado * W, yy + 2.5, EIXO_Z), 6.0, 'zincado', n=12))
        xa, xb = sorted((lado * W, lado * (W - 40)))
        pecas.append(caixa(xa, xb, y - 30, y + 30, ZP1 - 1, ZP1 + 2.2, 'zincado', 0.8))        # aba na porta
    if lado < 0:
        pecas.append(letreiro('ARMAMENTO', 54, xc, 1385, REBAIXO + 0.25))
        pecas.append(letreiro('ACESSO RESTRITO', 24, xc, 1330, REBAIXO + 0.25, 'tinta_amarela'))
    else:
        pecas.append(caixa(-14, 2, 68, H - 7, ZP1 - 1, ZP1 + 3, 'chapa_verde', 1.2))           # batente que cobre a fresta
        pecas.append(caixa(10, 42, 890, 1050, ZP1 - 1, ZP1 + 4, 'zincado', 1.6))               # espelho da maçaneta
        pecas.append(cil((26, 1005, ZP1 + 3), (26, 1005, ZP1 + 34), 8.5, 'zincado', n=18))
        pecas.append(cil((20, 1005, ZP1 + 30), (118, 1005, ZP1 + 30), 8.0, 'zincado', n=18, r1=6.5))
        pecas.append(cil((26, 925, ZP1 + 3), (26, 925, ZP1 + 10), 10.5, 'latao', n=24))        # miolo da fechadura
        pecas.append(caixa(24.6, 27.4, 918, 932, ZP1 + 9.9, ZP1 + 10.3, 'tinta_preta'))
        pecas.append(caixa(xc - 70, xc + 70, 1370, 1420, REBAIXO - 1, REBAIXO + 2.5, 'latao', 1.0))   # plaqueta
        pecas.append(letreiro('PAT. 0417', 20, xc, 1387, REBAIXO + 2.75, 'tinta_preta'))
        for sx in (-62, 62):
            pecas.append(cil((xc + sx, 1395, REBAIXO + 2), (xc + sx, 1395, REBAIXO + 4), 3.2, 'zincado', n=10, r1=2.4))
    return pecas, G(lado * W, 0, EIXO_Z)


def montar():
    parte('corpo', _carcaca(), origem=G(0, 0, 0), grupo='A')
    parte('interior', _interior(), origem=G(0, 0, 0), grupo='B')
    for nome, lado in (('porta_esq', -1), ('porta_dir', 1)):
        pecas, org = _porta(lado)
        parte(nome, pecas, origem=org, grupo='C')
