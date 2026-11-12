"""Bancada de carpintaria: bancada pesada de caibros e tábuas aparafusadas, com morsa de madeira na
frente, prateleira embaixo e as ferramentas do ofício (serrote pendurado, plaina, esquadro, grampo,
lata de pregos, lápis e uma tábua presa na morsa). Dá para fazer com tábuas e pregos, como pede a receita.
Medidas em mm, coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente (onde se trabalha)."""
import math
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte

H = 880                     # em cima do tampo
ESP = 38                    # espessura das tábuas do tampo
XT, ZT = 1000, 356          # meio comprimento e meia profundidade do tampo
PX, PZ, PE = 800, 270, 45   # centro dos pés e meia espessura
SAIA0, SAIA1 = 702, H - ESP # travessas de cima
TRAV0, TRAV1 = 180, 270     # travessas de baixo
MORSA_X0, MORSA_X1 = -850, -400
MORSA_Z = 378               # face de dentro do mordente (a tábua presa tem 22 mm)


def _estrutura():
    p = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            x, z = sx * PX, sz * PZ
            p.append(caixa(x - PE, x + PE, 0, SAIA1, z - PE, z + PE, 'pinho_y', 3.0))
    for sz in (-1, 1):                                              # travessas compridas de cima
        z0, z1 = sorted((sz * (PZ + PE), sz * (PZ + PE + ESP)))
        p.append(caixa(-883, 883, SAIA0, SAIA1, z0, z1, 'pinho_x', 2.5))
    z0, z1 = -(PZ + PE + ESP), -(PZ + PE)                           # travessa comprida de baixo, só atrás
    p.append(caixa(-883, 883, TRAV0, TRAV1, z0, z1, 'pinho_x', 2.5))
    for sx in (-1, 1):                                              # travessas curtas, de cima e de baixo
        x0, x1 = sorted((sx * (PX + PE), sx * (PX + PE + ESP)))
        for y0, y1 in ((SAIA0, SAIA1), (TRAV0, TRAV1)):
            p.append(caixa(x0, x1, y0, y1, -(PZ + PE), PZ + PE, 'pinho_z', 2.5))
    for k in range(3):                                              # prateleira de baixo
        z0 = -221.5 + k * 149
        p.append(caixa(-883 + 6 * k, 883 - 9 * (2 - k), TRAV1, TRAV1 + 22, z0, z0 + 145, 'pinho_x', 2.0))
    return p


def _tampo():
    p = []
    for k, d in enumerate((0, 9, -6, 12, 4)):                       # cinco tábuas, pontas desencontradas
        z0 = -ZT + k * 143
        p.append(caixa(-XT - d, XT + (7 - d), H - ESP, H, z0, z0 + 140, 'tampo_x', 3.0))
    return p


def _morsa():
    xc = (MORSA_X0 + MORSA_X1) / 2
    yc = 785
    m = caixa(MORSA_X0, MORSA_X1, 690, H, MORSA_Z, MORSA_Z + 50, 'tampo_x', 4.0)
    p = [m,
         cil((xc, yc, 300), (xc, yc, MORSA_Z + 92), 13, 'ferro_preto', n=18),                  # fuso
         cil((xc, yc, MORSA_Z + 50), (xc, yc, MORSA_Z + 56), 34, 'ferro_preto', n=24),         # arruela
         cil((xc, yc, MORSA_Z + 56), (xc, yc, MORSA_Z + 92), 24, 'ferro_preto', n=20, r1=21),  # cabeça do fuso
         cil((xc - 14, yc - 118, MORSA_Z + 74), (xc + 14, yc + 118, MORSA_Z + 74), 7.5, 'aco_ferramenta', n=14)]   # manípulo
    for s in (-1, 1):
        a = (xc + s * 14, yc + s * 118, MORSA_Z + 74)
        b = (xc + s * 16, yc + s * 134, MORSA_Z + 74)
        p.append(cil(a, b, 12, 'aco_ferramenta', n=14))
        x = xc + s * 165                                                                       # guias
        p.append(cil((x, yc - 20, 300), (x, yc - 20, MORSA_Z + 54), 10, 'aco_ferramenta', n=16))
        p.append(cil((x, yc - 20, MORSA_Z + 50), (x, yc - 20, MORSA_Z + 54), 19, 'ferro_preto', n=18))
    return p


def _parafuso(a, eixo, r=10.0, h=5.0):
    b = tuple(a[i] + eixo[i] * h for i in range(3))
    return cil(a, b, r, 'ferro_preto', n=12, r1=r * 0.55)


def _ferragens():
    p = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            for y in (SAIA0 + 35, SAIA1 - 35, TRAV0 + 45):          # parafusos franceses nos pés
                if not (sz > 0 and y < 300):
                    p.append(_parafuso((sx * (PX - 12), y, sz * (PZ + PE + ESP)), (0, 0, sz)))
                p.append(_parafuso((sx * (PX + PE + ESP), y, sz * (PZ - 12)), (sx, 0, 0)))
    for k in range(5):                                               # parafusos do tampo, sobre as travessas
        z0 = -ZT + k * 143
        for sx in (-1, 1):
            for dz in (38, 102):
                p.append(_parafuso((sx * 864, H, z0 + dz), (0, 1, 0), 5.0, 2.6))
    p.append(cil((883, 812, 0), (906, 818, 0), 3.2, 'ferro_preto', n=8))                        # prego do serrote
    p.append(cil((906, 818, 0), (908, 818.5, 0), 6.5, 'ferro_preto', n=10))
    return p


def _serrote():
    """Pendurado no prego da travessa da direita: cabo em cima, lâmina para baixo. Perfil em (z, y)."""
    x0 = 886
    dentes = []
    n = 70
    for i in range(n):                                              # fio dos dentes, de baixo para cima
        y = 250 + i * 6.5
        z = -36 - (y - 250) * 0.062
        dentes += [(z, y), (z - 3.6, y + 3.2)]
    lam = perfil([(-12, 250), (16, 250), (58, 705), (-64, 705)] + dentes[::-1], x0 + 9, x0 + 10.6, 'aco_lamina')
    cabo = perfil([(-70, 690), (64, 690), (72, 720), (66, 800), (40, 838), (8, 846), (-30, 836), (-58, 800), (-78, 756), (-86, 716)],
                  x0, x0 + 20, 'faia_y', 4.0)
    cut(cabo, perfil([(-34, 742), (34, 742), (38, 790), (20, 812), (-18, 812), (-36, 790)], x0 - 5, x0 + 25, 'faia_y'))
    bevel(cabo, 3.0)
    p = [lam, cabo]
    for z, y in ((-40, 716), (36, 716), (-52, 730)):                # parafusos de latão do cabo
        p.append(cil((x0 + 20, y, z), (x0 + 22.2, y, z), 6.5, 'latao', n=12, r1=5.5))
    return p


def _plaina(x0, z0):
    """Plaina de madeira em cima do tampo: corpo, cunha, ferro e punho. Perfil em (x, y)."""
    y = H
    corpo = caixa(x0, x0 + 290, y, y + 62, z0, z0 + 68, 'faia_x', 4.0)
    cut(corpo, frente([(x0 + 150, y + 20), (x0 + 196, y + 70), (x0 + 118, y + 70)], z0 + 12, z0 + 56, 'faia_x'))      # boca
    p = [corpo,
         frente([(x0 + 152, y + 16), (x0 + 156, y + 15), (x0 + 236, y + 132), (x0 + 232, y + 134)], z0 + 14, z0 + 54, 'aco_ferramenta', 0.6),   # ferro
         frente([(x0 + 146, y + 26), (x0 + 204, y + 104), (x0 + 190, y + 108), (x0 + 128, y + 66)], z0 + 15, z0 + 53, 'faia_y', 2.0),           # cunha
         frente([(x0 + 228, y + 58), (x0 + 282, y + 58), (x0 + 284, y + 82), (x0 + 276, y + 128), (x0 + 286, y + 146),
                 (x0 + 262, y + 152), (x0 + 244, y + 120), (x0 + 240, y + 84)], z0 + 22, z0 + 46, 'faia_y', 5.0),                             # punho
         cil((x0 + 44, y + 58, z0 + 34), (x0 + 44, y + 96, z0 + 34), 19, 'faia_y', n=18, r1=24),                                           # pomo da frente
         cil((x0 + 44, y + 96, z0 + 34), (x0 + 44, y + 106, z0 + 34), 24, 'faia_y', n=18, r1=15)]
    return p


def _esquadro(x0, z0):
    y = H
    return [caixa(x0, x0 + 160, y, y + 18, z0, z0 + 46, 'faia_x', 2.0),
            caixa(x0 + 2, x0 + 6, y + 4, y + 14, z0 - 1.2, z0 + 47.2, 'latao', 0.6),
            caixa(x0 + 110, x0 + 152, y + 8.2, y + 9.8, z0 - 260, z0 + 20, 'aco_lamina')]


def _grampo(z):
    """Grampo sargento preso na ponta direita do tampo, atrás."""
    xb = XT + 14
    return [caixa(xb, xb + 7, 640, H + 24, z - 13, z + 13, 'aco_ferramenta', 1.2),                 # barra
            caixa(xb - 104, xb + 12, H, H + 22, z - 11, z + 11, 'esmalte_vermelho', 3.0),          # mordente fixo
            caixa(xb - 104, xb + 14, 716, 740, z - 13, z + 13, 'esmalte_vermelho', 3.0),           # mordente corrediço
            cil((xb - 84, 648, z), (xb - 84, H - ESP - 7, z), 6.5, 'ferro_preto', n=14),           # fuso
            cil((xb - 84, H - ESP - 7, z), (xb - 84, H - ESP, z), 15, 'ferro_preto', n=16),        # sapata
            cil((xb - 84, 556, z), (xb - 84, 650, z), 14, 'faia_y', n=16, r1=11.5),                # cabo
            cil((xb - 84, 650, z), (xb - 84, 660, z), 12.5, 'lata', n=16)]                         # virola


def _lata(x, z):
    y = H
    o = cil((x, y, z), (x, y + 96, z), 43, 'lata', n=28)
    cut(o, cil((x, y + 30, z), (x, y + 110, z), 41.4, 'lata', n=28))
    p = [o, cil((x, y + 30, z), (x, y + 64, z), 41, 'ferro_preto', n=20, r1=30)]
    for k in range(9):                                              # pregos de pé e deitados na boca da lata
        a = k * 2.4
        r = 10 + 3.1 * k
        bx, bz = x + r * math.cos(a), z + r * math.sin(a)
        tx, tz = x + (r + 9) * math.cos(a + 0.8), z + (r + 9) * math.sin(a + 0.8)
        p.append(cil((bx, y + 58, bz), (tx, y + 104 + 3 * (k % 3), tz), 1.7, 'aco_ferramenta', n=6))
        p.append(cil((tx, y + 104 + 3 * (k % 3), tz), (tx + 0.3, y + 105.5 + 3 * (k % 3), tz + 0.3), 4.0, 'aco_ferramenta', n=8))
    return p


def _lapis(x, z):
    y = H + 3.6
    return [cil((x, y, z), (x + 150, y, z + 22), 3.9, 'lapis', n=6),
            cil((x + 150, y, z + 22), (x + 164, y, z + 24), 3.9, 'crua_x', n=6, r1=1.2),
            cil((x + 164, y, z + 24), (x + 168, y, z + 24.6), 1.2, 'grafite', n=6, r1=0.3)]


def _ferramentas():
    p = _serrote() + _plaina(250, -150) + _esquadro(-330, 60) + _grampo(-290) + _lata(-860, -250) + _lapis(-120, 150)
    p.append(caixa(-720, -560, 742, 1130, ZT + 0.5, MORSA_Z - 0.5, 'crua_y', 1.5))               # tábua presa na morsa
    p.append(caixa(-560, 760, H, H + 22, -340, -200, 'crua_x', 1.5))                              # tábua deitada atrás, à espera
    p.append(caixa(-300, 620, TRAV1 + 22, TRAV1 + 44, -200, -58, 'crua_x', 1.5))                  # sobras na prateleira
    p.append(caixa(-180, 700, TRAV1 + 22, TRAV1 + 44, -40, 100, 'pinho_x', 1.5))
    p.append(caixa(-60, 560, TRAV1 + 44, TRAV1 + 66, -150, -10, 'pinho_x', 1.5))
    return p


def montar():
    parte('estrutura', _estrutura(), origem=G(0, 0, 0), grupo='A')
    parte('tampo', _tampo(), origem=G(0, 0, 0), grupo='B')
    parte('morsa', _morsa(), origem=G(0, 0, 0), grupo='B')
    parte('ferragens', _ferragens(), origem=G(0, 0, 0), grupo='C')
    parte('ferramentas', _ferramentas(), origem=G(0, 0, 0), grupo='C')
