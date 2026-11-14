"""Máquina de refrigerante de balcão, masseira de padaria, fritadeira industrial e chapa de lanchonete no nível realista.

Medidas em mm nas coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente. As medidas de fora são as dos
móveis antigos de props/mobilias (nenhum tem nó que abre). As marcas dos refrigerantes são inventadas."""
import math, os, random, importlib.util
import lib
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte, letreiro


def _carregar(nome, pasta):
    spec = importlib.util.spec_from_file_location(nome, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', pasta, 'modelo.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


q = _carregar('modelo_quarto', 'quarto')
_torno, _fio = q._torno, q._fio
_mover = _carregar('modelo_sala', 'sala')._mover


def _anel(prof, mat, x=0, y=0, z=0, n=20, eixo=(0, 1, 0)):
    return lib.lathe([(h, r) for r, h in prof], mat, n=n, c0=G(x, y, z), eixo=G(*eixo), anel=True)


def _botao(x, y, z, r, mat, n=14):
    """Botão de comando virado para a frente (+z), com a saia escura."""
    return [_torno([(0, 0), (r + 6, 0), (r + 6, 3), (0, 3)], 'tinta_preta', x, y, z, n=n, eixo=(0, 0, 1)),
            _torno([(0, 0), (r, 0), (r, 14), (r - 3, 18), (0, 19)], mat, x, y, z + 3, n=n, eixo=(0, 0, 1))]


def _pes(xs, zs, y, mat='borracha', r=16, h=12):
    return [_torno([(0, 0), (r, 0), (r - 2, h), (0, h)], mat, x, y, z, n=12) for x in xs for z in zs]


# ---------------------------------------------------------------------------- MÁQUINA DE REFRIGERANTE
SABORES = (('COLA', 'vermelho_cartaz'), ('GUARANÁ', 'plastico_verde'), ('LARANJA', 'plastico_amarelo'))


def maquina_refrigerante():
    p = _pes((-300, 300), (-260, 400), 0)
    p.append(caixa(-335, 335, 12, 52, -290, 440, 'inox', 4.0))                                   # bandeja de pingos
    cut(p[-1], caixa(-315, 315, 30, 60, 250, 420, 'inox'))
    for k in range(25):                                                                           # grelha da bandeja
        x = -300 + k * 25
        p.append(caixa(x - 3, x + 3, 38, 48, 252, 418, 'inox'))
    p.append(caixa(-340, 340, 52, 680, -300, 240, 'inox', 6.0))                                   # corpo do gelo
    p.append(caixa(-346, 346, 680, 700, -306, 246, 'inox', 4.0))                                  # tampa
    p.append(cil((-120, 708, 120), (120, 708, 120), 9, 'plastico_preto', n=10))
    for x in (-120, 120):
        p.append(cil((x, 700, 120), (x, 712, 120), 8, 'plastico_preto', n=10))
    p.append(caixa(-330, 330, 418, 662, 240, 248, 'plastico_preto', 2.0))                       # painel das marcas
    for k, (nome, cor) in enumerate(SABORES):
        x = -210 + k * 210
        p.append(caixa(x - 98, x + 98, 428, 652, 248, 252, cor, 1.5))
        p.append(cil((x, 560, 251.5), (x, 560, 253), 62, 'letra_branca', n=24))
        p.append(cil((x, 560, 252.8), (x, 560, 254), 54, cor, n=24))
        p.append(letreiro(nome, 26 if len(nome) < 6 else 21, x, 550, 254.2, 'letra_branca'))
        p.append(letreiro('GELADO', 16, x, 455, 252.2, 'letra_branca'))
    for k in range(6):                                                                            # válvulas
        x = -250 + k * 100
        cor = SABORES[k // 2][1]
        p.append(caixa(x - 32, x + 32, 300, 404, 240, 300, 'inox', 8.0))
        p.append(caixa(x - 26, x + 26, 370, 394, 300, 301, cor, 1.0))
        p.append(_torno([(0, 0), (14, 0), (14, 6), (10, 40), (0, 40)], 'pvc_branco', x, 260, 270, n=14))
        ang = 0.25 if k == 2 else 0.0                                                             # uma alavanca emperrada
        p.append(caixa(x - 8, x + 8, 222, 300, 302 + ang * 40, 316 + ang * 40, 'inox', 3.0))
    for x, z, deitado in ((-180, 330, False), (150, 360, True)):                                  # copos de papel esquecidos
        o = _torno([(0, 0), (30, 0), (42, 110), (44, 114), (0, 114)], 'copo_papel', 0, 0, 0, n=18)
        if deitado:                                                                               # tombado, boca para a direita
            _mover(o, lambda X, Y, Z, x=x, z=z: (x + Y, 48 + 40 - X * 0.95 + (Y * 0.12), z + Z))
        else:
            _mover(o, lambda X, Y, Z, x=x, z=z: (x + X, 48 + Y, z + Z))
        p.append(o)
    parte('maquina', p, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- MASSEIRA
def masseira():
    C = 'cinza_maquina'
    p = _pes((-280, 280), (-360, 260), 0, 'aco_polido', 22, 40)
    p.append(caixa(-320, 320, 40, 560, -400, 300, C, 20.0))                                       # base
    p.append(caixa(-180, 180, 540, 1030, -410, -262, C, 16.0))                                    # coluna
    p.append(caixa(-200, 200, 1020, 1238, -410, 180, C, 30.0))                                    # cabeçote
    p.append(caixa(-150, 150, 1060, 1180, 180, 181.5, 'inox', 1.0))
    p.append(letreiro('25 kg', 28, 0, 1100, 181.6, 'tinta_preta'))
    # bacia de inox com a massa
    p.append(_anel([(276, 0), (282, 0), (282, 300), (294, 306), (294, 318), (276, 318)], 'inox', 0, 560, 40, n=40))
    p.append(_torno([(0, 0), (282, 0), (282, 6), (0, 6)], 'inox', 0, 556, 40, n=40))
    p.append(_torno([(0, 0), (262, 0), (268, 40), (250, 110), (180, 150), (60, 166), (0, 168)], 'massa_clara', 0, 566, 40, n=36))
    p.append(cil((-150, 570, -150), (-150, 860, -150), 14, 'inox', n=12))                         # barra quebra-massa
    # espiral
    p.append(cil((0, 1022, 80), (0, 680, 80), 20, 'inox', n=16))
    hel = [(62 * math.cos(t * math.pi / 8), 1000 - t * 22, 80 + 62 * math.sin(t * math.pi / 8)) for t in range(17)]
    p.append(_fio(hel, 11, 'inox', res=1))
    p.append(_torno([(0, 0), (40, 0), (40, 18), (24, 30), (0, 30)], 'inox', 0, 1000, 80, n=16))
    # grade de proteção
    p.append(_fio([(300 * math.cos(math.radians(t)), 900, 40 + 300 * math.sin(math.radians(t))) for t in range(0, 360, 12)], 5, 'arame_cromo', fechado=True, res=0))
    for k in range(-3, 4):
        z = 40 + k * 80
        if abs(z - 80) < 30:
            continue
        h = math.sqrt(300 ** 2 - (k * 80) ** 2)
        p.append(cil((-h, 900, z), (h, 900, z), 4, 'arame_cromo', n=8))
    for x in (-200, 200):
        p.append(cil((x, 900, -258), (x, 900, -230), 8, 'aco_polido', n=10))                    # dobradiça da grade
    # painel de comando no lado direito do cabeçote e o botão de emergência
    p.append(caixa(200, 206, 1060, 1200, -330, -90, 'plastico_preto', 2.0))
    for k, cor in enumerate(('plastico_verde', 'plastico_vermelho', 'plastico_amarelo')):
        z = -290 + k * 80
        p.append(_torno([(0, 0), (16, 0), (16, 12), (0, 14)], cor, 206, 1110, z, n=14, eixo=(1, 0, 0)))
    p.append(_torno([(0, 0), (30, 0), (30, 10), (0, 12)], 'tinta_preta', 206, 1170, -210, n=18, eixo=(1, 0, 0)))  # relógio
    p.append(caixa(214, 218, 1165, 1192, -212, -208, 'letra_branca'))
    p.append(_torno([(0, 0), (16, 0), (16, 16), (30, 22), (30, 32), (0, 34)], 'plastico_vermelho', 140, 1238, 120, n=18))   # emergência
    p.append(_torno([(0, 0), (40, 0), (40, 4), (0, 4)], 'plastico_amarelo', 140, 1236, 120, n=18))
    p.append(caixa(-80, -40, 120, 200, -410, -400, 'plastico_preto', 3.0))                     # tomada do cabo de força
    parte('masseira', p, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- FRITADEIRA
def _cesto(x, y0, z0, z1, alto, cabo_y, cabo_z):
    """Cesto de arame de fritura: aros, varetas e cabo com punho preto."""
    w = 92
    h = 120
    p = [_fio([(x - w, y, z0), (x + w, y, z0), (x + w, y, z1), (x - w, y, z1)], 3.0, 'arame_cromo', fechado=True, res=0) for y in (y0, y0 + h)]
    for k in range(9):
        xx = x - w + k * (2 * w / 8)
        for z in (z0, z1):
            p.append(cil((xx, y0, z), (xx, y0 + h, z), 2.0, 'arame_cromo', n=5))
        p.append(cil((xx, y0, z0), (xx, y0, z1), 2.0, 'arame_cromo', n=5))
    for k in range(1, 8):
        z = z0 + k * (z1 - z0) / 8
        for s in (-1, 1):
            p.append(cil((x + s * w, y0, z), (x + s * w, y0 + h, z), 2.0, 'arame_cromo', n=5))
    p.append(cil((x - 40, y0 + h, z1), (x - 10, cabo_y, cabo_z - 120), 4.5, 'arame_cromo', n=8))
    p.append(cil((x + 40, y0 + h, z1), (x + 10, cabo_y, cabo_z - 120), 4.5, 'arame_cromo', n=8))
    p.append(cil((x, cabo_y, cabo_z - 125), (x, cabo_y + (cabo_y - y0 - h) * 0.1, cabo_z), 14, 'plastico_preto', n=12))
    for xx in (x - w + 10, x + w - 10):                                                          # ganchos de trás
        p.append(_fio([(xx, y0 + h, z0), (xx, y0 + h + 22, z0 - 4), (xx, y0 + h + 22, z0 - 22)], 2.5, 'arame_cromo', res=0))
    return p


def fritadeira():
    I = 'inox'
    p = []
    for x in (-205, 205):
        for z in (-290, 290):
            p.append(cil((x, 40, z), (x, 125, z), 20, I, n=14))
            p.append(_torno([(0, 0), (28, 0), (26, 12), (16, 22), (16, 40), (0, 40)], 'aco_polido', x, 0, z, n=14))
    corpo = caixa(-245, 245, 120, 912, -340, 330, I, 4.0)
    cut(corpo, caixa(-212, 212, 840, 930, -262, 250, I))                                          # tanque de óleo
    p.append(corpo)
    p.append(caixa(-212, 212, 836, 844, -262, 250, 'oleo_velho'))
    p.append(caixa(-236, 236, 140, 700, 330, 338, I, 3.0))                                        # porta
    for x in (-150, 150):
        p.append(cil((x, 660, 338), (x, 660, 362), 7, I, n=10))
    p.append(cil((-160, 660, 362), (160, 660, 362), 11, I, n=14))
    p.append(caixa(-240, 240, 715, 900, 330, 342, I, 3.0))                                        # painel de comando
    p += _botao(-120, 800, 342, 26, 'plastico_preto', 18)
    for k in range(9):                                                                            # escala do termostato
        a = math.radians(210 - k * 30)
        p.append(caixa(-122 + 40 * math.cos(a) - 1.2, -122 + 40 * math.cos(a) + 1.2, 800 + 40 * math.sin(a) - 4, 800 + 40 * math.sin(a) + 4, 342, 342.6, 'tinta_preta'))
    p += _botao(40, 800, 342, 18, 'plastico_preto', 14)
    p.append(_torno([(0, 0), (9, 0), (9, 6), (0, 9)], 'plastico_vermelho', 150, 800, 342, n=12, eixo=(0, 0, 1)))   # luz piloto
    p.append(caixa(-245, 245, 912, 1050, -340, -300, I, 4.0))                                     # chaminé
    p.append(caixa(-180, 180, 990, 1025, -300.5, -299.5, 'tinta_preta'))
    p.append(cil((-235, 990, -290), (235, 990, -290), 9, I, n=12))                               # suporte dos cestos
    p += _cesto(-108, 760, -230, 120, 0, 900, 410)                                                 # um mergulhado
    p += _cesto(108, 912, -240, 110, 0, 990, 400)                                                  # outro escorrendo na borda
    p.append(caixa(-245, 245, 908, 912, 250, 330, 'gordura'))                                    # óleo velho escorrido na frente
    parte('fritadeira', p, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- CHAPA DE LANCHONETE
def chapa_lanchonete():
    rnd = random.Random(8)
    I = 'inox'
    p = []
    for x in (-555, 555):
        for z in (-300, 300):
            p.append(caixa(x - 20, x + 20, 30, 805, z - 20, z + 20, I, 2.0))
            p.append(_torno([(0, 0), (22, 0), (20, 10), (12, 18), (12, 32), (0, 32)], 'aco_polido', x, 0, z, n=12))
    p.append(caixa(-560, 560, 150, 165, -310, 310, I, 2.0))                                       # prateleira de baixo
    p.append(caixa(-590, 590, 800, 880, -330, 330, I, 4.0))                                       # caixa dos queimadores
    for x in (-420, -140, 140, 420):
        p += _botao(x, 838, 330, 22, 'plastico_preto', 16)
        p.append(caixa(x - 1.5, x + 1.5, 838 + 26, 838 + 34, 330, 330.6, 'tinta_preta'))
    p.append(caixa(-580, 580, 880, 905, -320, 300, 'ferro_preto', 2.0))                          # chapa
    calha = caixa(-580, 580, 868, 905, 300, 372, I, 3.0)
    cut(calha, caixa(-562, 562, 884, 912, 310, 360, I))
    p.append(calha)
    p.append(caixa(-562, 562, 884, 886, 310, 360, 'gordura'))
    p.append(caixa(-590, 590, 905, 1000, -332, -318, I, 3.0))                                     # espelho de trás
    for s in (-1, 1):
        p.append(perfil([(-332, 905), (220, 905), (220, 925), (-332, 1000)], s * 590 - 6, s * 590 + 6, I, 2.0))
    for k in range(9):                                                                            # crosta queimada
        x, z, r = rnd.uniform(-480, 480), rnd.uniform(-240, 220), rnd.uniform(30, 90)
        pts = [(x + r * (0.7 + 0.3 * rnd.random()) * math.cos(t * math.pi / 5), z + r * 0.7 * (0.7 + 0.3 * rnd.random()) * math.sin(t * math.pi / 5)) for t in range(10)]
        p.append(planta(pts, 905, 905.8 + rnd.uniform(0, 0.8), 'gordura'))
    p.append(caixa(160, 280, 906, 908, 40, 140, 'aco_lamina', 1.0))                               # espátula
    p.append(cil((220, 909, 140), (220, 940, 340), 10, 'faia_y', n=10))
    p.append(caixa(214, 226, 906, 912, 130, 150, 'aco_lamina'))
    p.append(_torno([(0, 0), (30, 0), (32, 140), (24, 160), (10, 166), (4, 200), (0, 202)], 'plastico_vermelho', 300, 165, 100, n=16))   # bisnagas na prateleira
    p.append(_torno([(0, 0), (30, 0), (32, 140), (24, 160), (10, 166), (4, 200), (0, 202)], 'plastico_amarelo', 380, 165, 60, n=16))
    # botijão embaixo, com a mangueira até a chapa
    p.append(_torno([(0, 0), (150, 0), (160, 18), (178, 60), (178, 360), (160, 410), (100, 444), (40, 452), (0, 452)], 'botijao', -280, 165, -40, n=28))
    p.append(_anel([(150, 0), (155, 0), (155, 30), (150, 30)], 'botijao', -280, 165, -40, n=28))
    p.append(_fio([(-280 + 110 * math.cos(math.radians(t)), 650, -40 + 110 * math.sin(math.radians(t))) for t in range(-150, 151, 15)], 9, 'botijao', res=0))
    for t in (-150, 150):
        a = math.radians(t)
        p.append(cil((-280 + 110 * math.cos(a), 650, -40 + 110 * math.sin(a)), (-280 + 100 * math.cos(a), 600, -40 + 100 * math.sin(a)), 9, 'botijao', n=8))
    p.append(cil((-280, 617, -40), (-280, 660, -40), 14, 'latao', n=12))
    p.append(_torno([(0, 0), (24, 0), (24, 30), (0, 30)], 'plastico_preto', -280, 660, -40, n=14))   # registro
    p.append(_fio([(-256, 680, -40), (-180, 720, -40), (-60, 700, -120), (100, 760, -200), (200, 800, -250)], 8, 'mangueira', res=0))
    parte('chapa', p, origem=G(0, 0, 0), grupo='A')


FORMAS = {'maquina_refrigerante': maquina_refrigerante, 'masseira': masseira, 'fritadeira': fritadeira, 'chapa_lanchonete': chapa_lanchonete}
