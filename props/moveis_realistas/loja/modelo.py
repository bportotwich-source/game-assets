"""Gôndola de supermercado, balcão de caixa com registradora, armário de vestiário e banqueta giratória no nível realista.

Medidas em mm nas coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente. As medidas de fora e os nós
que abrem (gaveta_dinheiro; porta_1..3) são os dos móveis antigos de props/mobilias."""
import math, os, random, importlib.util
import lib
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte, letreiro

_spec = importlib.util.spec_from_file_location('modelo_quarto', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'quarto', 'modelo.py'))
q = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(q)
_torno, _fio, _travesseiro = q._torno, q._fio, q._travesseiro


# ---------------------------------------------------------------------------- GÔNDOLA
def _produtos(zs, y, prof, rnd):
    """Sobras de mercadoria numa prateleira (lado zs = +1 frente, -1 trás): latas, caixas e garrafas espalhadas."""
    p = []
    x = -440 + rnd.uniform(0, 60)
    while x < 400:
        tipo = rnd.choice(('lata', 'lata', 'caixa', 'garrafa', 'vazio', 'vazio'))
        z = zs * rnd.uniform(60, prof - 70)
        if tipo == 'lata':
            r, h = rnd.choice(((38, 110), (33, 120), (50, 75)))
            mat = rnd.choice(('rotulo', 'rotulo_verde', 'rotulo_vermelho'))
            p.append(_torno([(0, 0), (r - 3, 0), (r, 4), (r, h - 4), (r - 3, h), (0, h)], 'lata', x + r, y, z, n=14))
            p.append(_torno([(r + 0.6, 12), (r + 0.6, h - 14)], mat, x + r, y, z, n=14))
            x += 2 * r + rnd.uniform(4, 30)
        elif tipo == 'caixa':
            w, h, d = rnd.choice(((190, 280, 70), (140, 200, 50), (220, 160, 110)))
            if rnd.random() < 0.25:                                              # caixa tombada
                w, h = h, d
            if x + w > 465:
                break
            mat = rnd.choice(('caixa_cereal', 'caixa_azul_pac', 'papelao'))
            p.append(caixa(x, x + w, y, y + h, z - d / 2, z + d / 2, mat, 1.5))
            x += w + rnd.uniform(5, 40)
        elif tipo == 'garrafa':
            r = 45
            p.append(_torno([(0, 0), (r - 6, 0), (r, 8), (r, 160), (r - 4, 170), (r, 180), (r, 230), (16, 285), (14, 300), (0, 300)], 'pet', x + r, y, z, n=14))
            p.append(_torno([(0, 0), (16, 0), (16, 22), (0, 22)], 'tampa_azul', x + r, y + 298, z, n=10))
            p.append(_torno([(r + 0.6, 70), (r + 0.6, 140)], 'rotulo_vermelho', x + r, y, z, n=14))
            x += 2 * r + rnd.uniform(10, 40)
        else:
            x += rnd.uniform(80, 220)
    return p


def gondola():
    X, ZK, H = 500, 440, 1600
    B = 'gondola_branca'
    p = []
    for sx in (-1, 1):                                                      # montantes nas pontas (meio montante: dois módulos lado a lado fecham um)
        xa, xb = sorted((sx * X, sx * (X - 28)))
        p.append(caixa(xa, xb, 20, H, -32, 32, B, 2.0))
        for zs in (-1, 1):                                                  # furação de cremalheira nas duas faces
            for y in range(180, H - 40, 50):
                xc = sx * (X - 14)
                za, zb = sorted((zs * 32, zs * 32.8))
                p.append(caixa(xc - 2.5, xc + 2.5, y, y + 18, za, zb, 'furo'))
        for zs in (-1, 1):                                                  # pé niveladores
            p.append(_torno([(0, 0), (16, 0), (16, 6), (6, 8), (6, 20), (0, 20)], 'zincado', sx * (X - 40), 0, zs * 400, n=10))
    for k, (y0, y1) in enumerate(((122, 420), (423, 720), (723, 1020), (1023, 1320), (1323, H))):   # painéis de fundo
        p.append(caixa(-X + 28, X - 28, y0, y1, -10, 10, B, 2.5))
        for zs in (-1, 1):                                                  # vinco de reforço no meio do painel
            za, zb = sorted((zs * 10, zs * 11.5))
            p.append(caixa(-X + 60, X - 60, (y0 + y1) / 2 - 12, (y0 + y1) / 2 + 12, za, zb, B, 0.6))
    p.append(caixa(-X, X, H, H + 50, -42, 42, B, 6.0))                     # cumeeira
    p.append(caixa(-X + 30, X - 30, H + 49, H + 50.5, -30, 30, 'etiqueta_amarela'))
    for zs in (-1, 1):                                                      # base: rodapé e fundo
        za, zb = sorted((zs * (ZK - 16), zs * ZK))
        p.append(caixa(-X + 4, X - 4, 22, 122, za, zb, B, 3.0))
        p.append(caixa(-X + 8, X - 8, 28, 78, *sorted((zs * (ZK + 0.2), zs * (ZK + 1.6))), 'plastico_preto', 0.5))
        za, zb = sorted((zs * 12, zs * (ZK - 16)))
        p.append(caixa(-X + 30, X - 30, 108, 122, za, zb, B, 1.5))
        p.append(caixa(-X + 30, X - 30, 25, 108, *sorted((zs * 12, zs * 30)), B))
    NIV = ((470, 400), (820, 370), (1170, 340))
    for zs in (-1, 1):
        for y, d in NIV:                                                    # prateleiras de chapa dobrada
            za, zb = sorted((zs * 14, zs * d))
            p.append(caixa(-X + 30, X - 30, y - 2, y, za, zb, B, 0.8))
            fa, fb = sorted((zs * (d - 1.5), zs * d))
            p.append(caixa(-X + 30, X - 30, y - 34, y, fa, fb, B, 0.6))
            za, zb = sorted((zs * 14, zs * (d - 1.5)))
            p.append(caixa(-X + 30, X - 30, y - 34, y - 31, *sorted((zs * (d - 30), zs * (d - 1.5))), B))
            for sx in (-1, 1):                                              # mãos-francesas encaixadas nos montantes
                xm = sx * (X - 34)
                p.append(perfil([(zs * 30, y - 2), (zs * (d - 40), y - 2), (zs * 30, y - 150)][::zs], xm - 1.5, xm + 1.5, B))
            ea, eb = sorted((zs * d, zs * (d + 3)))                         # canaleta de preço
            p.append(caixa(-X + 30, X - 30, y - 38, y + 2, ea, eb, 'etiqueta_amarela', 0.8))
            ta, tb = sorted((zs * (d + 3), zs * (d + 3.6)))
            for x in range(-420, 420, 170):
                p.append(caixa(x, x + 52, y - 30, y - 6, ta, tb, 'papel'))
        ea, eb = sorted((zs * ZK, zs * (ZK + 3)))
        p.append(caixa(-X + 30, X - 30, 82, 122, ea, eb, 'etiqueta_amarela', 0.8))
    parte('gondola', p, origem=G(0, 0, 0), grupo='A')
    rnd = random.Random(12)
    c = []
    for zs in (-1, 1):
        c += _produtos(zs, 122, ZK - 20, rnd)
        for y, d in NIV:
            if rnd.random() < 0.8:
                c += _produtos(zs, y, d, rnd)
    parte('mercadoria', c, origem=G(0, 0, 0), grupo='B')


# ---------------------------------------------------------------------------- BALCÃO DE CAIXA
def balcao_caixa():
    X, Z, H = 900, 300, 860
    L = 'laminado_branco'
    corpo = bevel(caixa(-X, X, 80, H, -Z, Z, L), 5.0, seg=2)
    cut(corpo, caixa(-820, 300, 150, 770, 120, Z + 10, L))                    # nicho de sacolas do lado da operadora
    cut(corpo, caixa(415, 785, 745, H - 4, -205, Z + 10, L))                  # vão da gaveta
    p = [corpo, caixa(-820, 300, 455, 472, 120, Z - 10, L, 1.5)]
    p.append(caixa(-X + 25, X - 25, 0, 82, -Z + 25, Z - 45, 'plastico_preto', 2.0))      # rodapé recuado
    for sx in (-1, 1):                                                       # cantoneiras de alumínio
        for sz in (-1, 1):
            xa, xb = sorted((sx * X, sx * (X + 2)))
            za, zb = sorted((sz * (Z - 30), sz * (Z + 2)))
            p.append(caixa(xa, xb, 82, H - 2, za, zb, 'inox'))
            xa, xb = sorted((sx * (X - 30), sx * (X + 2)))
            za, zb = sorted((sz * Z, sz * (Z + 2)))
            p.append(caixa(xa, xb, 82, H - 2, za, zb, 'inox'))
    p.append(caixa(-X + 20, X - 20, 300, 340, -Z - 14, -Z, 'plastico_cinza', 4.0))    # para-choque do lado do cliente
    p.append(bevel(caixa(-X - 20, X + 20, H, H + 40, -Z - 20, Z + 20, 'granito'), 4.0, seg=2))
    # esteira: trilhos, lona e roletes
    for sz in (-1, 1):
        za, zb = sorted((sz * 252, sz * 272))
        p.append(caixa(-870, 125, H + 40, H + 72, za, zb, 'inox', 2.0))
    p.append(caixa(-850, 100, H + 40, H + 58, -250, 250, 'borracha'))
    for x in range(-830, 100, 30):
        p.append(caixa(x, x + 6, H + 58, H + 60, -248, 248, 'borracha'))
    for x in (-850, 100):
        p.append(cil((x, H + 49, -250), (x, H + 49, 250), 10, 'borracha', n=12))
    p.append(perfil([(-200, H + 60), (-200, H + 80), (-170, H + 100), (-140, H + 80), (-140, H + 60)], -700, -480, 'plastico_cinza', 2.0))   # bastão divisor
    # balança embutida e janela do leitor
    p.append(caixa(120, 360, H + 38, H + 44, -170, 170, 'inox', 1.0))
    for k in range(9):
        p.append(caixa(140, 340, H + 44, H + 45, -150 + k * 36, -136 + k * 36, 'inox'))
    p.append(caixa(150, 330, H + 40, H + 45.2, -170 + 6, -150, 'vidro_escuro'))
    p.append(caixa(130, 350, H + 44, H + 160, -235, -195, 'plastico_preto', 4.0))   # leitor vertical
    p.append(caixa(150, 330, H + 60, H + 145, -195, -194, 'vidro_leitor'))
    # sacolas e bobina no nicho
    rnd = random.Random(3)
    for k in range(3):                                                        # maços de sacolas plásticas
        x0 = -680 + k * 260
        for j in range(2):
            p.append(_travesseiro(x0 + rnd.uniform(-10, 10), 472 + 18 + j * 34, 210, 105, 65, 17, mat='sacola', giro=rnd.uniform(-0.2, 0.2), semente=k + j * 3.0, n=8))
            p.append(_travesseiro(x0 + rnd.uniform(-10, 10), 150 + 18 + j * 34, 210, 105, 65, 17, mat='sacola', giro=rnd.uniform(-0.2, 0.2), semente=k * 2 + j, n=8))
    p.append(_torno([(0, 0), (40, 0), (40, 57), (0, 57)], 'papel', 120, 472, 220, n=16, eixo=(1, 0, 0)))
    parte('balcao', p, origem=G(0, 0, 0), grupo='A')
    # registradora (bege dos anos 90), impressora e visor
    r = [bevel(caixa(400, 800, H + 40, H + 120, -220, 140, 'plastico_bege'), 8.0, seg=2)]
    r.append(perfil([(140, H + 120), (-220, H + 120), (-220, H + 175), (-60, H + 160)], 410, 790, 'plastico_bege', 6.0))
    for i in range(6):                                                        # teclado inclinado
        for j in range(4):
            x0 = 425 + i * 50
            z0 = -40 + j * 42
            yy = H + 120 + (40 - j * 12) * 0.32
            r.append(caixa(x0, x0 + 40, yy, yy + 12, z0, z0 + 34, 'tecla' if (i < 5 or j > 1) else 'tecla_vermelha', 3.0))
    r.append(caixa(725, 785, H + 121, H + 132, 40, 130, 'tecla_vermelha', 3.0))
    r.append(caixa(430, 700, H + 140, H + 175, -200, -100, 'plastico_bege', 3.0))   # visor da operadora
    r.append(perfil([(-110, H + 150), (-110, H + 172), (-100, H + 172), (-100, H + 150)], 450, 680, 'vidro_visor'))
    for x in (450, 650):                                                      # visor do cliente no poste
        pass
    r.append(cil((600, H + 175, -180), (600, 1060, -180), 14, 'plastico_preto', n=12))
    r.append(bevel(caixa(500, 700, 1060, 1150, -205, -160, 'plastico_preto'), 6.0, seg=2))
    r.append(caixa(515, 685, 1072, 1138, -160, -159, 'vidro_visor'))
    r.append(caixa(515, 685, 1072, 1138, -206, -205, 'vidro_visor'))
    r.append(bevel(caixa(250, 380, H + 40, H + 150, -60, 130, 'plastico_preto'), 10.0, seg=2))   # impressora de cupom
    r.append(caixa(270, 360, H + 149, H + 151, 60, 110, 'tinta_preta'))
    r.append(frente([(275, H + 150), (355, H + 150), (352, H + 230), (362, H + 280), (278, H + 275), (272, H + 220)], 85, 85.6, 'papel'))
    parte('registradora', r, origem=G(0, 0, 0), grupo='B')
    g = [bevel(caixa(420, 780, 750, 855, Z - 2, Z + 6, 'plastico_bege'), 3.0, seg=2)]
    g.append(cil((600, 820, Z + 6), (600, 820, Z + 10), 7, 'inox', n=10))     # fechadura
    g.append(caixa(598.5, 601.5, 815, 825, Z + 9.8, Z + 10.3, 'tinta_preta'))
    g.append(caixa(450, 750, 762, 776, Z + 5, Z + 8, 'plastico_preto', 2.0))  # pega
    t = caixa(425, 775, 752, 850, -200, Z - 2, 'plastico_cinza')
    cut(t, caixa(432, 768, 762, 860, -193, Z - 9, 'plastico_cinza'))
    g.append(t)
    for k in range(3):                                                        # divisórias
        x = 432 + (k + 1) * 84
        g.append(caixa(x - 2, x + 2, 762, 840, -193, 40, 'plastico_cinza'))
    g.append(caixa(432, 768, 762, 840, 38, 42, 'plastico_cinza'))
    for k, mat in enumerate(('cedula_verde', 'cedula_azul', 'cedula_verde', 'cedula_rosa')):   # notas presas pela mola
        x = 432 + k * 84
        g.append(caixa(x + 8, x + 76, 763, 772 + rnd.uniform(0, 8), -180, 30, mat))
        g.append(caixa(x + 30, x + 54, 772, 785, -100, 10, 'zincado'))
    for k in range(5):                                                        # moedas
        x = 450 + k * 66
        g.append(_torno([(0, 0), (24, 0), (24, 14), (0, 14)], 'cobre' if k % 2 else 'latao', x + 20, 763, 120, n=14))
    parte('gaveta_dinheiro', g, origem=G(0, 0, 0), grupo='B')


# ---------------------------------------------------------------------------- ARMÁRIO DE VESTIÁRIO
def armario_vestiario():
    X, Z0, Z1, H = 450, -250, 240, 1850
    V = 'armario_verde'
    c = bevel(caixa(-X, X, 100, H, Z0, Z1, V), 3.0, seg=2)
    for i in range(3):
        x0 = -X + i * 300
        cut(c, caixa(x0 + (8 if i == 0 else 6), x0 + 300 - (8 if i == 2 else 6), 108, H - 8, Z0 + 8, Z1 + 10, V))
    p = [c, caixa(-X + 10, X - 10, 0, 100, Z0 + 20, Z1 - 20, 'esmalte_preto', 3.0)]
    for i in range(3):
        x0 = -X + i * 300
        a, b = x0 + 12, x0 + 288
        p.append(caixa(a, b, 1540, 1552, Z0 + 8, Z1 - 12, V, 1.0))            # prateleira do chapéu
        p.append(caixa(a, b, 1520, 1552, Z1 - 14, Z1 - 12, V))
        p.append(cil((a, 1490, -20), (b, 1490, -20), 8, 'inox', n=10))         # varão
        for k in range(3):                                                     # ganchos
            xg = x0 + 80 + k * 70
            p.append(_fio([(xg, 1490, -20), (xg, 1440, -20), (xg, 1420, 10), (xg, 1440, 30)], 2.5, 'inox', res=1))
    for i, (y, xx) in enumerate(((1700, -X + 2), (300, -X + 2), (1700, -X + 302), (300, -X + 302), (1700, -X + 602), (300, -X + 602))):
        p.append(cil((xx + 3, y - 40, Z1 + 3), (xx + 3, y + 40, Z1 + 3), 6, 'inox', n=8))   # dobradiças
    rnd = random.Random(7)
    # coisas deixadas para trás: toalha no varão, mochila na prateleira, botas no fundo
    p.append(cil((-X + 70, 1497, -20), (-X + 220, 1497, -20), 11, 'pano_azul', n=10))
    for s in (-1, 1):
        p.append(caixa(-X + 72, -X + 218, 1060 + (60 if s > 0 else 0), 1497, -20 + s * 4 - 3 + (6 if s > 0 else 0), -20 + s * 4 + 3 + (6 if s > 0 else 0), 'pano_azul', 2.0))
    p.append(_travesseiro(0, 1612, -60, 110, 120, 55, mat='pano_vermelho', semente=4.0, n=10))
    for k in range(2):
        xb = 220 + k * 105
        p.append(bevel(caixa(xb, xb + 90, 108, 260, -150, 90, 'couro'), 18.0, seg=2))
        p.append(caixa(xb - 3, xb + 93, 108, 125, -155, 95, 'borracha', 3.0))
    parte('carcaca', p, origem=G(0, 0, 0), grupo='A')
    for i in range(3):
        x0 = -X + i * 300 + 3
        x1 = x0 + 294
        d = [bevel(caixa(x0, x1, 103, H - 3, Z1, Z1 + 15, V), 2.0, seg=2)]
        for y0 in (200, 1620):                                                 # venezianas estampadas
            for k in range(6):
                y = y0 + k * 30
                d.append(caixa(x0 + 60, x1 - 60, y, y + 12, Z1 + 14.6, Z1 + 15.2, 'furo'))
                d.append(perfil([(Z1 + 15, y + 12), (Z1 + 15, y + 16), (Z1 + 21, y + 13.5), (Z1 + 21, y + 12)][::-1], x0 + 58, x1 - 58, V))
        for k in range(2):                                                     # vincos de reforço
            y = 620 + k * 560
            d.append(caixa(x0 + 40, x1 - 40, y, y + 20, Z1 + 15, Z1 + 17, V, 1.0))
        d.append(bevel(caixa(x1 - 64, x1 - 26, 940, 1110, Z1 + 15, Z1 + 30, 'aco_polido'), 3.0, seg=2))   # puxador de alavanca
        d.append(caixa(x1 - 58, x1 - 32, 960, 1090, Z1 + 30.2, Z1 + 31.6, 'plastico_preto'))
        d.append(caixa(x1 - 54, x1 - 36, 1120, 1150, Z1 + 15, Z1 + 30, 'aco_polido', 2.0))   # orelha do cadeado
        d.append(bevel(caixa(x0 + 97, x1 - 97, 1455, 1500, Z1 + 15, Z1 + 17, 'aco_polido'), 1.0, seg=1))   # plaqueta do número
        d.append(letreiro(str(i + 1), 32, (x0 + x1) / 2, 1463, Z1 + 17.2, 'tinta_preta'))
        d.append(caixa(x0 + 80, x1 - 80, 1380, 1420, Z1 + 15, Z1 + 16.5, 'zincado'))   # porta-etiqueta com nome
        d.append(caixa(x0 + 84, x1 - 84, 1384, 1416, Z1 + 16.5, Z1 + 17, 'papel'))
        if i == 1:                                                             # cadeado
            d.append(bevel(caixa(x1 - 66, x1 - 24, 1040, 1088, Z1 + 32, Z1 + 50, 'latao'), 4.0, seg=2))
            d.append(_fio([(x1 - 58, 1088, Z1 + 41), (x1 - 58, 1130, Z1 + 41), (x1 - 45, 1148, Z1 + 41), (x1 - 32, 1130, Z1 + 41), (x1 - 32, 1088, Z1 + 41)], 4.5, 'inox', res=1))
        for k in range(rnd.randint(1, 3)):                                     # adesivos e amassados
            pass
        parte(f'porta_{i + 1}', d, origem=G(x0, 0, Z1 + 15), grupo='B')


# ---------------------------------------------------------------------------- BANQUETA GIRATÓRIA
def banqueta_giratoria():
    p = [_torno([(0, 0), (200, 0), (201, 6), (198, 14), (150, 24), (70, 40), (44, 52), (38, 62), (0, 62)], 'cromo', n=36)]   # base de cúpula
    p.append(_torno([(0, -0.5), (204, -0.5), (204, 3), (0, 3)], 'borracha', n=36))
    p.append(_torno([(0, 60), (35, 60), (35, 640), (40, 650), (40, 662), (0, 662)], 'cromo', n=24))       # coluna
    p.append(_torno([(0, 380), (44, 380), (44, 412), (0, 412)], 'cromo', n=20))                            # luva do apoio de pés
    p.append(_torno([(156, 386), (170, 384), (176, 396), (170, 408), (156, 406), (152, 396)], 'cromo', n=40))   # anel de pés
    for k in range(3):
        a = k * 2 * math.pi / 3 + 0.4
        p.append(cil((40 * math.cos(a), 396, 40 * math.sin(a)), (156 * math.cos(a), 396, 156 * math.sin(a)), 8, 'cromo', n=10))
    p.append(_torno([(0, 662), (95, 662), (95, 672), (60, 680), (0, 680)], 'ferro_preto', n=24))           # rolamento giratório
    p.append(_torno([(0, 678), (192, 678), (200, 684), (200, 718), (194, 722), (0, 722)], 'cromo', n=48))  # aro de inox
    for k in range(4):
        y = 688 + k * 8
        p.append(_torno([(200.2, y), (200.6, y + 1.5), (200.2, y + 3)], 'cromo', n=48))
    p.append(_torno([(0, 720), (186, 720), (196, 728), (198, 742), (194, 760), (178, 778), (140, 788), (0, 790)], 'vinil_vermelho', n=48))   # almofada
    p.append(_torno([(194, 735), (197.6, 737.5), (194, 740)], 'vinil_vermelho', n=48))                    # vivo
    for k in range(6):                                                      # costuras em gomos no tampo
        a = k * math.pi / 3
        p.append(_fio([(30 * math.cos(a), 790.3, 30 * math.sin(a)), (100 * math.cos(a), 787.5, 100 * math.sin(a)), (160 * math.cos(a), 781, 160 * math.sin(a))], 1.2, 'vinil_costura', fechado=False, res=1))
    p.append(_torno([(0, 788.6), (30, 788.6), (30, 791), (0, 791.2)], 'vinil_costura', n=16))
    for k in range(10):                                                     # tachas do aro
        a = k * 2 * math.pi / 10
        p.append(_torno([(0, 0), (5, 0), (4, 2.5), (0, 3.2)], 'cromo', 200 * math.cos(a), 700, 200 * math.sin(a), n=8, eixo=(math.cos(a), 0, math.sin(a))))
    parte('banqueta', p, origem=G(0, 0, 0), grupo='A')


FORMAS = {'gondola': gondola, 'balcao_caixa': balcao_caixa, 'armario_vestiario': armario_vestiario, 'banqueta_giratoria': banqueta_giratoria}
