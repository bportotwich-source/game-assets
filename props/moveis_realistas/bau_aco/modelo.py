"""Baú de aço: caixa grande de guardar feita na forja com o que se acha: armação de cantoneira
rebitada, pintada de amarelo de obra, fechada com chapa ondulada galvanizada, em cima de dois patins.
Tampa de chapa com aba (nó `tampa`, origem no eixo das dobradiças, atrás), três dobradiças, alças de
vergalhão nos lados e porta-cadeado na frente, com o cadeado da receita pendurado. Oco por dentro.
Medidas em mm, coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente (de onde se abre)."""
import math
import lib
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte

X, Z = 750, 350             # meia largura e meia profundidade por fora da armação
YB = 90                     # debaixo da caixa (altura dos patins)
Y1 = 620                    # boca da caixa
C = 45                      # aba da cantoneira
T = 5                       # espessura da cantoneira
ABA = 56                    # altura da tampa
EIXO_Z = -Z - 12            # eixo das dobradiças
ONDA, AMP = 76.0, 8.0       # passo e meia altura da onda da chapa


def _ondulada(a0, a1, fixo, lado, y0, y1, eixo):
    """Chapa ondulada em pé. Corre de a0 a a1 no eixo dado ('x' ou 'z'); `fixo` é onde fica a linha
    do meio no outro eixo; `lado` (+1/-1) é para onde fica o lado de fora."""
    n = max(8, int(round((a1 - a0) / ONDA * 8)))
    fora, dentro = [], []
    for i in range(n + 1):
        s = a0 + (a1 - a0) * i / n
        d = AMP * math.cos(2 * math.pi * (s - a0) / ONDA)
        fora.append((s, fixo + lado * 1.2 + d))
        dentro.append((s, fixo - lado * 1.2 + d))
    pts = fora + dentro[::-1]
    if eixo == 'z':
        pts = [(b, a) for a, b in pts]
    return planta(pts, y0, y1, 'zinco')


def _rebite(a, eixo, r=6.5):
    b = tuple(a[i] + eixo[i] * 3.2 for i in range(3))
    return cil(a, b, r, 'aco_ocre', n=8, r1=r * 0.55)


def _corpo():
    p = []
    m = Z - T - AMP - 1.2                                           # linha do meio das chapas da frente e de trás
    for sz in (-1, 1):
        p.append(_ondulada(-X + 16, X - 16, sz * m, sz, YB, Y1 - 3, 'x'))
    mx = X - T - AMP - 1.2
    for sx in (-1, 1):
        p.append(_ondulada(-Z + 8, Z - 8, sx * mx, sx, YB, Y1 - 3, 'z'))
    p.append(caixa(-X + 8, X - 8, YB, YB + 4, -Z + 8, Z - 8, 'chapa_cinza'))                # fundo
    return p


def _armacao():
    p = []
    for sz in (-1, 1):                                              # frente e trás
        z0, z1 = sorted((sz * (Z - T), sz * Z))
        for sx in (-1, 1):                                          # montantes dos cantos
            x0, x1 = sorted((sx * (X - C), sx * X))
            p.append(caixa(x0, x1, YB, Y1, z0, z1, 'aco_ocre', 1.2))
        for y0, y1 in ((YB, YB + C), (Y1 - C, Y1)):                 # travessas de baixo e de cima
            p.append(caixa(-X + C, X - C, y0, y1, z0, z1, 'aco_ocre', 1.2))
        p.append(caixa(-32, 32, YB + C, Y1 - C, z0, z1, 'aco_ocre', 1.2))                    # montante do meio
    for sx in (-1, 1):                                              # lados
        x0, x1 = sorted((sx * (X - T), sx * X))
        for sz in (-1, 1):
            z0, z1 = sorted((sz * (Z - C), sz * (Z - T)))
            p.append(caixa(x0, x1, YB, Y1, z0, z1, 'aco_ocre', 1.2))
        for y0, y1 in ((YB, YB + C), (Y1 - C, Y1)):
            p.append(caixa(x0, x1, y0, y1, -Z + C, Z - C, 'aco_ocre', 1.2))
    # aba de cima da cantoneira, virada para dentro: é onde a tampa assenta
    for sz in (-1, 1):
        z0, z1 = sorted((sz * (Z - 34), sz * (Z - T)))
        p.append(caixa(-X + T, X - T, Y1 - T, Y1, z0, z1, 'aco_ocre', 1.0))
    for sx in (-1, 1):
        x0, x1 = sorted((sx * (X - 34), sx * (X - T)))
        p.append(caixa(x0, x1, Y1 - T, Y1, -Z + 34, Z - 34, 'aco_ocre', 1.0))
    for x in (-X + 230, X - 230):                                   # patins: tubo retangular atravessado
        p.append(caixa(x - 50, x + 50, 0, YB, -Z - 10, Z + 10, 'aco_ocre', 4.0))
    return p


def _rebites():
    p = []
    for sz in (-1, 1):
        for y in (YB + C / 2, Y1 - C / 2):
            for k in range(15):
                p.append(_rebite((-X + 50 + k * (2 * X - 100) / 14, y, sz * Z), (0, 0, sz)))
        for x in (-X + C / 2, X - C / 2, 0):
            for k in range(1, 5):
                p.append(_rebite((x, YB + C / 2 + k * (Y1 - YB - C) / 5, sz * Z), (0, 0, sz)))
    for sx in (-1, 1):
        for y in (YB + C / 2, Y1 - C / 2):
            for k in range(7):
                p.append(_rebite((sx * X, y, -Z + 50 + k * (2 * Z - 100) / 6), (sx, 0, 0)))
        for z in (-Z + C / 2 + 4, Z - C / 2 - 4):
            for k in range(1, 5):
                p.append(_rebite((sx * X, YB + C / 2 + k * (Y1 - YB - C) / 5, z), (sx, 0, 0)))
    return p


def _alca(sx):
    """Alça de vergalhão dobrado, caída, presa em dois olhais numa chapa de reforço."""
    x = sx * X
    y = Y1 - 150
    p = [caixa(min(x, x + sx * 4), max(x, x + sx * 4), y - 40, y + 40, -120, 120, 'aco_ocre', 1.0)]
    pts = [G(x + sx * 16, y + 8, -85), G(x + sx * 34, y - 62, -85), G(x + sx * 34, y - 62, 85), G(x + sx * 16, y + 8, 85)]
    p.append(lib.fio(lib.caminho_arred(pts, 16, n=4, fechado=False), 6.5, 'ferro_preto', fechado=False, res=3))
    for z in (-85, 85):                                             # olhais
        p.append(cil((x + sx * 4, y + 8, z - 11), (x + sx * 4, y + 8, z + 11), 16, 'ferro_preto', n=12))
        p.append(caixa(min(x + sx * 4, x + sx * 18), max(x + sx * 4, x + sx * 18), y - 4, y + 20, z - 11, z + 11, 'ferro_preto', 1.5))
        for dy in (-26, 28):
            p.append(_rebite((x + sx * 4, y + dy, z + (30 if z > 0 else -30)), (sx, 0, 0), 5.5))
    return p


def _fecho():
    """Na caixa: o olhal por onde passa o cadeado, e o cadeado aberto pendurado nele."""
    y = Y1 - 78
    z = Z
    p = [caixa(-26, 26, y - 26, y + 26, z, z + 3, 'ferro_preto', 0.8)]
    p.append(lib.fio([G(0, y + 12, z + 2), G(0, y + 12, z + 26), G(0, y - 12, z + 26), G(0, y - 12, z + 2)], 4.0, 'aco_ferramenta', fechado=False))
    # cadeado: corpo de latão e a haste passando pelo olhal
    yc = y - 62
    p.append(caixa(-24, 24, yc - 22, yc + 20, z + 12, z + 30, 'cadeado', 3.5))
    h = [G(-13, yc + 20, z + 21), G(-13, yc + 52, z + 21), G(13, yc + 52, z + 21), G(13, yc + 30, z + 21)]
    p.append(lib.fio(lib.caminho_arred(h, 11, n=4, fechado=False), 4.2, 'aco_ferramenta', fechado=False, res=3))
    p.append(cil((0, yc - 8, z + 30), (0, yc - 8, z + 31.2), 6, 'aco_ferramenta', n=12))         # miolo
    return p


def _dobradicas_corpo():
    p = []
    for x in (-X + 180, 0, X - 180):
        p.append(caixa(x - 90, x + 90, Y1 - 64, Y1 - 2, -Z - 4, -Z, 'ferro_preto', 0.8))
        for k in (0, 2):                                            # canhões da folha de baixo
            x0 = x - 90 + k * 72
            p.append(cil((x0, Y1 + 2, EIXO_Z), (x0 + 36, Y1 + 2, EIXO_Z), 8, 'ferro_preto', n=12))
            p.append(caixa(x0, x0 + 36, Y1 - 20, Y1 + 2, -Z - 12, -Z - 4, 'ferro_preto', 0.8))
        for dx in (-60, 60):
            p.append(cil((x + dx, Y1 - 36, -Z - 4), (x + dx, Y1 - 36, -Z - 6.5), 5.5, 'aco_ferramenta', n=8, r1=3.5))
    return p


def _tampa():
    yt = Y1 + ABA
    f = 9                                                            # quanto a tampa passa da caixa
    p = [caixa(-X - f, X + f, yt - 4, yt, -Z - f, Z + f, 'aco_ocre', 1.5)]                       # chapa de cima
    p.append(caixa(-X - f, X + f, Y1 - 22, yt - 4, Z + f - 4, Z + f, 'aco_ocre', 1.2))          # aba da frente
    p.append(caixa(-X - f, X + f, Y1 + 10, yt - 4, -Z - f, -Z - f + 4, 'aco_ocre', 1.2))        # aba de trás (mais curta: gira)
    for sx in (-1, 1):
        x0, x1 = sorted((sx * (X + f - 4), sx * (X + f)))
        p.append(perfil([(-Z - f + 4, Y1 + 10), (-Z + 60, Y1 - 22), (Z + f - 4, Y1 - 22), (Z + f - 4, yt - 4), (-Z - f + 4, yt - 4)], x0, x1, 'aco_ocre'))
    for x in (-X + 260, 0, X - 260):                                # nervuras de chapa dobrada em cima
        p.append(perfil([(-Z + 30, yt), (-Z + 44, yt + 12), (Z - 44, yt + 12), (Z - 30, yt)], x - 34, x + 34, 'aco_ocre', 2.0))
    return p


def _ferragens_tampa():
    yt = Y1 + ABA
    p = []
    for x in (-X + 180, 0, X - 180):                                # folha de cima das dobradiças
        p.append(caixa(x - 90, x + 90, Y1 + 12, yt - 6, -Z - 13, -Z - 9, 'ferro_preto', 0.8))
        x0 = x - 90 + 36
        for xa in (x0, x0 + 72):
            p.append(cil((xa, Y1 + 2, EIXO_Z), (xa + 36, Y1 + 2, EIXO_Z), 8, 'ferro_preto', n=12))
            p.append(caixa(xa, xa + 36, Y1 + 2, Y1 + 20, -Z - 16, -Z - 12, 'ferro_preto', 0.8))
        p.append(cil((x - 96, Y1 + 2, EIXO_Z), (x + 96, Y1 + 2, EIXO_Z), 3.2, 'aco_ferramenta', n=8))  # pino
        for dx in (-60, 60):
            p.append(cil((x + dx, Y1 + 34, -Z - 13), (x + dx, Y1 + 34, -Z - 15.5), 5.5, 'aco_ferramenta', n=8, r1=3.5))
    # lingueta do porta-cadeado: desce da aba da frente e tem o rasgo por onde sai o olhal
    y = Y1 - 78
    l = caixa(-20, 20, y - 30, Y1 + 20, Z + 9, Z + 12.5, 'ferro_preto', 1.0)
    cut(l, caixa(-7, 7, y - 18, y + 18, Z, Z + 20, 'ferro_preto'))
    p.append(l)
    for dx in (-11, 11):
        p.append(cil((dx, Y1 + 6, Z + 12.5), (dx, Y1 + 6, Z + 15), 5, 'aco_ferramenta', n=8, r1=3.2))
    for sz in (-1, 1):                                              # rebites da tampa
        for k in range(9):
            p.append(_rebite((-X + 60 + k * (2 * X - 120) / 8, yt, sz * (Z - 12)), (0, 1, 0), 5.5))
    return p


def montar():
    parte('corpo', _corpo(), origem=G(0, 0, 0), grupo='A')
    parte('armacao', _armacao() + _rebites(), origem=G(0, 0, 0), grupo='B')
    parte('ferragens', _alca(-1) + _alca(1) + _fecho() + _dobradicas_corpo(), origem=G(0, 0, 0), grupo='C')
    t = parte('tampa', _tampa(), origem=G(0, Y1 + 2, EIXO_Z), grupo='B')
    parte('tampa_ferragens', _ferragens_tampa(), origem=G(0, Y1 + 2, EIXO_Z), pai=t, grupo='C')
