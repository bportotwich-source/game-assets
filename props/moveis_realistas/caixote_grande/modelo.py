"""Caixote grande de tábuas: caixa de guardar feita à mão, com tábuas pregadas em sarrafos, dois
patins embaixo (não fica com o fundo no chão molhado), tampa de tábuas com três travessas (nó `tampa`,
origem na dobradiça de trás), duas dobradiças de cinta, ferrolho de aldrava na frente e alças de corda.
Por dentro é oco: quando a tampa abre, vê-se o fundo. Dá para fazer com tábuas, pregos e um par de
dobradiças, como pede a receita.
Medidas em mm, coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente (de onde se abre)."""
import math
import lib
from base import G, caixa, cil, planta, perfil, frente, letreiro, cut, bevel, parte

X, Z = 700, 350             # meia largura e meia profundidade por fora das tábuas
E = 22                      # espessura das tábuas
PATIM = 70                  # altura dos patins
Y0 = PATIM                  # debaixo do fundo
Y1 = 640                    # boca da caixa (onde a tampa assenta)
TAMPA = 26                  # espessura das tábuas da tampa
YT = Y1 + TAMPA             # em cima da tampa
N_TAB = 4                   # tábuas por lado, na altura
ALT = (Y1 - Y0) / N_TAB     # altura de cada tábua (com a fresta)


def _prego(a, eixo, r=4.2):
    b = tuple(a[i] + eixo[i] * 1.6 for i in range(3))
    return cil(a, b, r, 'ferro_preto', n=8, r1=r * 0.7)


def _corpo():
    p = []
    for k in range(N_TAB):                                          # frente, fundo e lados: tábuas deitadas
        y0, y1 = Y0 + k * ALT + 1.5, Y0 + (k + 1) * ALT - 1.5
        d = (0, 5, -4, 3)[k]
        for sz in (-1, 1):
            z0, z1 = sorted((sz * (Z - E), sz * Z))
            p.append(caixa(-X + d * (sz > 0), X + d * (sz < 0), y0, y1, z0, z1, 'pinho_x', 2.0))
        for sx in (-1, 1):
            x0, x1 = sorted((sx * (X - E), sx * X))
            p.append(caixa(x0, x1, y0, y1, -Z + E + 0.5, Z - E - 0.5, 'pinho_z', 2.0))
    for k in range(5):                                              # fundo: cinco tábuas ao comprido
        z0 = -Z + E + 1 + k * 121.4
        p.append(caixa(-X + E + 1, X - E - 1, Y0, Y0 + E, z0, z0 + 119, 'pinho_x', 1.5))
    for sx in (-1, 1):                                              # sarrafos em pé, por fora, nos cantos e no meio
        for sz in (-1, 1):
            z0, z1 = sorted((sz * Z, sz * (Z + E)))
            x0, x1 = sorted((sx * (X - 95), sx * (X + E)))
            p.append(caixa(x0, x1, Y0 - 8, Y1 - 6, z0, z1, 'tampo_y', 2.5))
            x0, x1 = sorted((sx * X, sx * (X + E)))
            z0, z1 = sorted((sz * (Z - 95), sz * Z))
            p.append(caixa(x0, x1, Y0 - 8, Y1 - 6, z0, z1, 'tampo_y', 2.5))
    for sz in (-1, 1):
        z0, z1 = sorted((sz * Z, sz * (Z + E)))
        p.append(caixa(-48, 48, Y0 - 8, Y1 - 6, z0, z1, 'tampo_y', 2.5))
    for x in (-X + 150, 0, X - 150):                                # patins atravessados
        p.append(caixa(x - 45, x + 45, 0, PATIM, -Z - 6, Z + 6, 'pinho_z', 4.0))
    for sx in (-1, 1):                                              # sarrafo de dentro, onde a tampa assenta
        x0, x1 = sorted((sx * (X - E - 30), sx * (X - E)))
        p.append(caixa(x0, x1, Y1 - 60, Y1 - 12, -Z + E + 1, Z - E - 1, 'crua_z', 1.5))
    return p


def _tampa():
    p = []
    for k, d in enumerate((0, 6, -5, 4, -3)):                       # cinco tábuas ao comprido, pontas desencontradas
        z0 = -Z - 14 + k * 146
        p.append(caixa(-X - 20 - d, X + 20 + (4 - d), Y1, YT, z0, z0 + 143, 'tampo_x', 2.5))
    for x in (-X + 150, 0, X - 150):                                # travessas em cima
        p.append(caixa(x - 48, x + 48, YT, YT + E, -Z - 10, Z + 10, 'pinho_z', 2.5))
    return p


def _ferragens_tampa():
    """Cintas das dobradiças (em cima da tampa) e a aldrava que desce na frente."""
    p = []
    for x in (-X + 150, X - 150):
        y = YT + E
        p.append(frente([(x - 20, y), (x + 20, y), (x + 20, y + 4), (x - 20, y + 4)], -Z - 12, 60, 'ferro_preto', 0.8))      # cinta
        p.append(planta([(x - 20, 60), (x + 20, 60), (x, 110)], y, y + 4, 'ferro_preto', 0.8))                              # ponta em lança
        for z in (-Z + 40, -Z + 150, -Z + 260, 30):
            p.append(_prego((x, y + 4, z), (0, 1, 0), 5.5))
        p.append(caixa(x - 20, x + 20, Y1 + 2, y + 4, -Z - 16, -Z - 12, 'ferro_preto', 0.8))                                 # dobra para trás
        p.append(cil((x - 24, Y1, -Z - 16), (x + 24, Y1, -Z - 16), 7, 'ferro_preto', n=12))                                  # canhão
    y = YT + E                                                      # aldrava: cinta do meio que dobra para a frente
    p.append(caixa(-18, 18, y, y + 4, Z - 120, Z + 16, 'ferro_preto', 0.8))
    p.append(caixa(-18, 18, Y1 - 62, y + 4, Z + E + 12, Z + E + 16, 'ferro_preto', 0.8))
    p.append(caixa(-18, 18, y, y + 4, Z + 10, Z + E + 16, 'ferro_preto', 0.8))
    for z in (Z - 100, Z - 30):
        p.append(_prego((0, y + 4, z), (0, 1, 0), 5.5))
    return p


def _alca(sx):
    """Alça de corda: sai por dois furos da tábua de cima do lado e faz barriga para baixo."""
    x = sx * (X + 3)
    y = Y1 - ALT * 0.5 - 30
    pts = []
    for i in range(13):
        t = i / 12
        z = -115 + 230 * t
        f = math.sin(math.pi * t)
        pts.append(G(x + sx * (10 + 42 * f), y - 60 * f, z))
    o = lib.fio(pts, 9.0, 'corda', fechado=False, res=3)
    p = [o]
    for z in (-115, 115):                                           # nó por fora de cada furo
        p.append(cil((x - sx * 2, y, z), (x + sx * 16, y, z), 15, 'corda', n=10, r1=12))
    return p


def _ferragens():
    p = []
    for sz in (-1, 1):                                              # pregos das tábuas nos sarrafos
        for x in (-X + 26, -X + 70, X - 26, X - 70, -22, 22):
            for k in range(N_TAB):
                y = Y0 + (k + 0.5) * ALT
                for dy in (-40, 40):
                    p.append(_prego((x, y + dy, sz * (Z + E)), (0, 0, sz)))
    for sx in (-1, 1):
        for z in (-Z + 48, Z - 48):
            for k in range(N_TAB):
                y = Y0 + (k + 0.5) * ALT
                for dy in (-40, 40):
                    p.append(_prego((sx * (X + E), y + dy, z), (sx, 0, 0)))
    # espelho da aldrava e o pino onde ela prende
    p.append(caixa(-34, 34, Y1 - 150, Y1 - 60, Z + E, Z + E + 4, 'ferro_preto', 1.0))
    p.append(cil((0, Y1 - 105, Z + E + 4), (0, Y1 - 105, Z + E + 30), 6, 'aco_ferramenta', n=10))
    a = lib.fio([G(-14, Y1 - 105, Z + E + 24), G(14, Y1 - 105, Z + E + 24), G(14, Y1 - 150, Z + E + 24), G(-14, Y1 - 150, Z + E + 24)], 3.5, 'aco_ferramenta')
    p.append(a)
    for x, y in ((-24, Y1 - 72), (24, Y1 - 72), (-24, Y1 - 138), (24, Y1 - 138)):
        p.append(_prego((x, y, Z + E + 4), (0, 0, 1), 4.5))
    return p


def montar():
    parte('corpo', _corpo(), origem=G(0, 0, 0), grupo='A')
    parte('ferragens', _ferragens(), origem=G(0, 0, 0), grupo='C')
    parte('letreiro', [letreiro('ESTOQUE', 86, -326, Y0 + 2 * ALT + 28, Z + 0.5)], origem=G(0, 0, 0), grupo='A')
    parte('alcas', _alca(-1) + _alca(1), origem=G(0, 0, 0), grupo='C')
    t = parte('tampa', _tampa(), origem=G(0, Y1, -Z - 16), grupo='B')
    parte('tampa_ferragens', _ferragens_tampa(), origem=G(0, Y1, -Z - 16), pai=t, grupo='C')
