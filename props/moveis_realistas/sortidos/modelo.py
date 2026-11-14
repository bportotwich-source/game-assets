"""Painel de ferramentas na parede, balança médica com régua, fichário de catálogo e jukebox no nível realista.

Medidas em mm nas coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente. As medidas de fora e os nós que
abrem (gaveta_1_3 e gaveta_3_1 do fichário) são os dos móveis antigos de props/mobilias. O painel é de parede: costas em
z = 0. O vidro da jukebox é a malha vidro_frente e os tubos de luz são luz_ambar e luz_vermelha, trocados no gerar.py
pelo vidro transparente e por material aceso. As ferramentas do painel são as da bancada de trabalho."""
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
sala = _carregar('modelo_sala', 'sala')
_mover, _livro = sala._mover, sala._livro
bt = _carregar('modelo_bancada_trabalho', 'bancada_trabalho')


def _anel(prof, mat, x=0, y=0, z=0, n=20, eixo=(0, 1, 0)):
    return lib.lathe([(h, r) for r, h in prof], mat, n=n, c0=G(x, y, z), eixo=G(*eixo), anel=True)


def _moldura(x0, x1, y0, y1, z, r, mat):
    """Friso de arame (cromo, latão) em volta de um retângulo de frente."""
    return _fio([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], r, mat, fechado=True, res=1)


# ---------------------------------------------------------------------------- PAINEL DE FERRAMENTAS
PZ = 26                     # face da frente do painel perfurado


def _sombra_chave(x, y, L, R):
    """Silhueta pintada de uma chave que sumiu do painel."""
    z0, z1 = PZ - 0.2, PZ + 0.5
    return [cil((x, y, z0), (x, y, z1), R * 1.2, 'tinta_sombra', n=16), cil((x, y - L, z0), (x, y - L, z1), R * 1.35, 'tinta_sombra', n=16),
            caixa(x - R * 0.5, x + R * 0.5, y - L, y, z0, z1, 'tinta_sombra')]


def _sombra_martelo(x, y):
    z0, z1 = PZ - 0.2, PZ + 0.5
    return [frente([(x - 52, y - 16), (x + 34, y - 13), (x + 44, y), (x + 34, y + 13), (x - 52, y + 16)], z0, z1, 'tinta_sombra'),
            frente([(x - 11, y - 14), (x + 11, y - 14), (x + 14, y - 300), (x + 9, y - 312), (x - 9, y - 312), (x - 14, y - 300)], z0, z1, 'tinta_sombra')]


def _serrote(x, y):
    """Serrote pendurado pelo cabo: lâmina com dentes de um lado e cabo fechado de madeira com três rebites."""
    z = PZ + 6
    lam = [(x - 62, y - 90)] + [(x - 62 + (k / 33) * 24 + (4 if k % 2 else 0), y - 96 - k * 14) for k in range(34)] + [(x + 22, y - 570), (x + 60, y - 90)]
    p = [frente(lam, z, z + 1.2, 'aco_lamina')]
    cabo = [(x - 70, y - 70), (x + 70, y - 70), (x + 78, y + 10), (x + 66, y + 66), (x + 30, y + 90), (x - 30, y + 92), (x - 66, y + 70), (x - 80, y + 20)]
    o = frente([(a, b - 10) for a, b in cabo], z - 11, z + 12, 'faia_y', 4.0)
    cut(o, frente([(x - 40, y - 20), (x + 42, y - 20), (x + 48, y + 30), (x + 30, y + 56), (x - 30, y + 58), (x - 48, y + 30)], z - 20, z + 20, 'faia_y', 6.0))
    p.append(o)
    for dx, dy in ((-50, -50), (0, -54), (50, -50)):
        p.append(cil((x + dx, y + dy, z - 12.5), (x + dx, y + dy, z + 13.5), 6, 'latao', n=10))
    p.append(bt._gancho(x, y + 66, 46))
    return p


def _trena_pendurada(x, y):
    z = PZ + 4
    o = frente([(x - 38, y - 40), (x + 38, y - 40), (x + 38, y + 10), (x + 20, y + 36), (x - 20, y + 36), (x - 38, y + 16)], z, z + 34, 'plastico_amarelo', 7.0)
    return [o, caixa(x + 38, x + 60, y - 37, y - 35, z + 7, z + 27, 'lata'), cil((x, y, z + 34), (x, y, z + 36), 15, 'plastico_preto', n=14),
            bt._gancho(x, y + 40, 30)]


def _extensao(x, y):
    """Rolo de extensão pendurado: voltas de fio laranja caídas num gancho."""
    p = [bt._gancho(x, y, 50)]
    for k in range(5):
        a = 0.25 * (k - 2)
        pts = [(x + 70 * math.sin(t) + 6 * k - 12, y - 70 + 70 * math.cos(t) - 6 * abs(k - 2), PZ + 24 + 7 * k + 8 * math.sin(t + a)) for t in [i * math.pi / 8 for i in range(16)]]
        p.append(_fio(pts, 4.5, 'isolante_vermelho', fechado=True, res=0))
    p.append(_fio([(x - 10, y - 140, PZ + 40), (x - 18, y - 200, PZ + 46), (x - 8, y - 240, PZ + 44)], 4.5, 'isolante_vermelho', res=0))
    p.append(caixa(x - 26, x + 10, y - 290, y - 240, PZ + 30, PZ + 62, 'plastico_preto', 3))                   # plugue
    return p


def painel_ferramentas():
    p = []
    for x in (-860, -300, 300, 860):                                                    # sarrafos atrás
        p.append(caixa(x - 25, x + 25, 10, 890, 0, 20, 'pinho_y', 1.5))
    for y in (40, 860):
        p.append(caixa(-890, 890, y - 22, y + 22, 0, 19.5, 'pinho_x', 1.5))
    p.append(caixa(-900, 900, 0, 900, 20, PZ, 'eucatex', 0.8))
    for x in (-860, -300, 300, 860):
        for y in (40, 860):
            p.append(_torno([(0, 0), (7, 0), (6, 2), (0, 3)], 'aco_ferramenta', x, y, PZ, n=10, eixo=(0, 0, 1)))
    bt.PAINEL_Z, bt.H = PZ, 80
    p += bt._arco_serra(-600, 720) + bt._martelo(-815, 610) + bt._chaves_fenda(-420, 420) + bt._alicate(-180, 460)
    for k, (L, R) in enumerate(((190, 15), (215, 17), (240, 19.5))):
        p += bt._chave(-20 + k * 80, 800, L, R)
    p += _sombra_chave(220, 800, 270, 22)                                                # a maior sumiu
    p += _sombra_martelo(400, 800)                                                      # e um martelo
    p += [bt._gancho(400 - 36, 784, 44), bt._gancho(400 + 26, 784, 44)]
    p += _serrote(640, 760) + _trena_pendurada(110, 380) + _extensao(800, 520)
    # prateleira de baixo com as latas
    p.append(caixa(-880, 880, 60, 80, PZ, 170, 'pinho_x', 2.0))
    for x in (-700, 0, 700):
        p.append(perfil([(PZ, 60), (150, 60), (PZ, -0.5)], x - 3, x + 3, 'aco_verde', 0.8))
    p += bt._almotolia(-760, 100) + bt._lata_parafusos(-600, 100) + bt._porcas(-420, 100)
    p.append(_anel([(28, 0), (52, 0), (52, 48), (28, 48)], 'fita_crepe', -250, 80, 100, n=22))
    p.append(_torno([(0, 0), (58, 0), (60, 4), (60, 120), (56, 126), (0, 126)], 'lata_azul', 330, 80, 95, n=22))      # lata de tinta
    p.append(_fio([(272, 200, 95), (300, 250, 95), (360, 250, 95), (388, 200, 95)], 2.0, 'arame_cromo', res=0))
    p.append(_torno([(0, 0), (40, 0), (42, 4), (42, 92), (30, 100), (30, 108), (0, 108)], 'vidro_ambar', 470, 80, 100, n=18))   # pote de vidro
    p.append(_torno([(0, 0), (32, 0), (32, 14), (0, 14)], 'lata', 470, 188, 100, n=18))
    parte('painel', p, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- BALANÇA MÉDICA
def balanca_medica():
    E = 'esmalte_balanca'
    p = []
    for x in (-160, 160):                                                               # pés de borracha
        for z in (-260, 210):
            p.append(_torno([(0, 0), (16, 0), (14, 12), (0, 12)], 'borracha', x, 0, z, n=12))
    p.append(planta([(-190, -290), (190, -290), (190, 230), (178, 242), (-178, 242), (-190, 230)], 12, 80, E, 6.0))   # caixa da plataforma
    p.append(planta([(-172, -205), (172, -205), (172, 222), (-172, 222)], 80, 86, 'borracha', 2.0))                    # tapete
    for k in range(15):
        z = -190 + k * 28
        p.append(caixa(-160, 160, 86, 89, z - 4, z + 4, 'borracha', 1.0))
    # coluna atrás
    p.append(planta([(-48, -285), (48, -285), (48, -175), (-48, -175)], 80, 170, E, 8.0))
    p.append(caixa(-30, 30, 170, 1420, -260, -200, E, 4.0))
    p.append(caixa(-60, 60, 1300, 1430, -278, -150, E, 8.0))                                                          # cabeça dos braços
    p.append(caixa(-24, 24, 1000, 1170, -200, -199, 'cartaz_velho'))                                                  # tabela de peso colada
    for k in range(8):
        p.append(caixa(-18, 18 - (k % 3) * 6, 1150 - k * 18, 1153 - k * 18, -199, -198.6, 'tinta_cartaz'))
    # braços de peso: cima de 10 em 10 kg, baixo de 100 em 100 g
    for y, passo, n, mx in ((1395, 25, 11, 'kg'), (1340, 10, 26, 'g')):
        p.append(caixa(-60, 195, y - 10, y + 10, -172, -158, 'aco_polido', 1.2))
        for k in range(n):
            x = -40 + k * (235 / (n - 1))
            alto = 7 if k % 5 == 0 or mx == 'kg' else 4
            p.append(caixa(x - 0.6, x + 0.6, y + 10 - alto, y + 10, -158, -157.4, 'tinta_preta'))
        if mx == 'kg':
            for k in range(0, 11, 2):
                p.append(letreiro(str(k * 10), 7, -40 + k * 23.5, y - 7, -157.4, 'tinta_preta'))
    p.append(frente([(10, 1380), (44, 1380), (48, 1410), (40, 1424), (14, 1424), (6, 1410)], -184, -146, 'aco_polido', 3.0))   # peso grande
    p.append(frente([(86, 1328), (104, 1328), (106, 1350), (100, 1358), (90, 1358), (84, 1350)], -180, -150, 'aco_polido', 2.0))  # peso pequeno
    p.append(_fio([(192, 1300, -165), (214, 1300, -165), (214, 1440, -165), (192, 1440, -165)], 3.5, 'aco_polido', res=0))      # alça do fiel
    p.append(cil((195, 1395, -165), (212, 1395, -165), 3, 'aco_polido', n=8))
    # régua de altura que sobe da coluna, com o esquadro de cabeça
    p.append(caixa(-11, 11, 1430, 1985, -236, -222, 'aco_polido', 1.0))
    for k in range(56):
        y = 1440 + k * 10
        p.append(caixa(-11, -11 + (9 if k % 5 == 0 else 5), y - 0.5, y + 0.5, -222, -221.4, 'tinta_preta'))
    for k in range(0, 56, 10):
        p.append(letreiro(str(140 + k), 5, 4, 1438 + k * 10, -221.4, 'tinta_preta'))
    p.append(caixa(-16, 16, 1940, 1965, -244, -214, 'aco_polido', 2.0))                                              # cursor
    p.append(cil((-18, 1952, -229), (18, 1952, -229), 5, 'aco_polido', n=10))
    p.append(caixa(-10, 10, 1946, 1958, -214, 60, 'aco_polido', 1.0))                                                # esquadro da cabeça
    p.append(_torno([(0, 0), (9, 0), (10, 6), (8, 12), (0, 15)], 'baquelite', 0, 1985, -229, n=12))
    p.append(_torno([(0, 0), (14, 0), (16, 8), (12, 18), (0, 20)], 'baquelite', 0, 1435, -200, n=14, eixo=(0, 0, 1)))  # trava da régua
    parte('balanca', p, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- FICHÁRIO DE CATÁLOGO
COLS = (-380, -190, 0, 190, 380)
LINHAS = (600, 760, 920, 1080)
ABREM = {(-190, 920): 'gaveta_1_3', (190, 760): 'gaveta_3_1'}
FZ = 250                    # frente da carcaça


def _gaveta_ficha(x, y, k, aberta, rnd):
    p = [caixa(x - 88, x + 88, y - 73, y + 73, FZ, FZ + 18, 'nogueira_x', 2.5)]
    z = FZ + 18
    p += [caixa(x - 34, x + 34, y + 8, y + 12, z, z + 2, 'latao'), caixa(x - 34, x + 34, y + 44, y + 48, z, z + 2, 'latao'),
          caixa(x - 34, x - 30, y + 8, y + 48, z, z + 2, 'latao'), caixa(x + 30, x + 34, y + 8, y + 48, z, z + 2, 'latao'),
          caixa(x - 30, x + 30, y + 12, y + 44, z, z + 0.8, 'ficha')]
    p.append(letreiro('ABCDEFGHIJLMNOPRSTUV'[k] + '-' + 'ABCDEFGHIJLMNOPRSTUV'[min(k + 1, 19)].lower(), 13, x, y + 22, z + 0.9, 'tinta_preta'))
    p.append(_torno([(0, 0), (9, 0), (7, 4), (6, 10), (12, 15), (12, 19), (0, 21)], 'latao_puxador', x, y - 30, z, n=12, eixo=(0, 0, 1)))
    if aberta:
        a, b = FZ - 470, FZ
        p += [caixa(x - 82, x - 76, y - 66, y + 52, a, b, 'pinho_z'), caixa(x + 76, x + 82, y - 66, y + 52, a, b, 'pinho_z'),
              caixa(x - 82, x + 82, y - 68, y - 62, a, b, 'pinho_z'), caixa(x - 82, x + 82, y - 66, y + 40, a, a + 6, 'pinho_z')]
        for j in range(24):
            zc = b - 26 - j * 17
            alto = 46 if j % 6 == 0 else 32 + rnd.uniform(-2, 2)
            p.append(caixa(x - 72, x + 72, y - 62, y + alto, zc - 0.7, zc + 0.7, 'etiqueta_amarela' if j % 6 == 0 else 'ficha'))
        p.append(cil((x, y - 42, a + 6), (x, y - 42, b - 4), 3, 'latao', n=8))                                          # varão das fichas
    return p


def fichario_catalogo():
    rnd = random.Random(9)
    car = caixa(-490, 490, 520, 1200, -250, FZ, 'nogueira_y', 2.0)
    for (x, y) in ABREM:
        cut(car, caixa(x - 84, x + 84, y - 69, y + 69, -232, FZ + 5, 'nogueira_z'))
    p = [car, caixa(-520, 520, 1200, 1240, -270, 270, 'nogueira_x', 4.0), caixa(-505, 505, 500, 520, -262, 262, 'nogueira_x', 3.0)]
    for k, y in enumerate(LINHAS[::-1]):
        for j, x in enumerate(COLS):
            if (x, y) not in ABREM:
                p += _gaveta_ficha(x, y, (k * 5 + j) % 19, False, rnd)
    # mesa de pernas torneadas embaixo
    for x in (-460, 460):
        for z in (-230, 230):
            p.append(_torno([(0, 0), (15, 0), (17, 12), (21, 26), (21, 60), (16, 84), (18, 160), (24, 200), (24, 250), (28, 290), (28, 420), (0, 420)],
                            'nogueira_y', x, 0, z, n=16))
            p.append(caixa(x - 28, x + 28, 420, 500, z - 28, z + 28, 'nogueira_y', 2.0))
    for z in (-226, 226):
        p.append(caixa(-432, 432, 440, 498, z - 10, z + 10, 'nogueira_x', 2.0))
    for x in (-456, 456):
        p.append(caixa(x - 10, x + 10, 440, 498, -202, 202, 'nogueira_z', 2.0))
    p.append(caixa(-452, 452, 110, 130, -210, 210, 'nogueira_x', 2.0))                                              # prateleira de baixo
    for x in (-460, 460):
        p.append(caixa(x - 14, x + 14, 104, 132, -202, 202, 'nogueira_z', 1.0))
    xx = -400
    for k in range(6):                                                                                              # catálogos encadernados
        w, h = rnd.uniform(36, 58), rnd.uniform(260, 300)
        o = _livro(w, h, 220, 'capa_%d' % (k % 5 + 1), rnd)
        _mover(o, lambda a, b, c, xx=xx: (a + xx, b + 130, c + 150))
        p.append(o)
        xx += w + 2
    o = _livro(50, 280, 220, 'capa_2', rnd)                                                                         # um tombado
    _mover(o, lambda a, b, c, xx=xx: (xx + 6 + (a * 0.4 + b * 0.92) - 0, 130 + (b * 0.38 - a * 0.92) + 50, c + 150))
    p.append(o)
    p.append(caixa(120, 420, 130, 310, -170, 150, 'papelao', 3.0))                                                   # caixa de fichas soltas
    for j in range(10):
        p.append(caixa(130, 410, 300, 318 + rnd.uniform(0, 8), 130 - j * 26, 131.4 - j * 26, 'ficha'))
    parte('fichario', p, origem=G(0, 0, 0), grupo='A')
    for (x, y), nome in ABREM.items():
        parte(nome, _gaveta_ficha(x, y, 3 if nome == 'gaveta_1_3' else 11, True, rnd), origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- JUKEBOX
JZ = 280                    # frente do corpo de madeira
RA = 400                    # raio do arco de luz


def jukebox():
    rnd = random.Random(5)
    arco = [(450, 40), (450, 1100)] + [(450 * math.cos(math.radians(t)), 1100 + 450 * math.sin(math.radians(t))) for t in range(6, 175, 6)] + [(-450, 1100), (-450, 40)]
    corpo = frente(arco, -300, JZ, 'nogueira_y', 6.0)
    cut(corpo, caixa(-300, 300, 880, 1260, 120, JZ + 10, 'plastico_preto'))                                         # nicho dos discos
    p = [corpo, caixa(-440, 440, 0, 40, -290, 300, 'tinta_preta', 3.0), caixa(-442, 442, 34, 44, -292, 302, 'cromo', 1.5)]
    # grade do alto-falante
    p.append(caixa(-300, 300, 120, 640, JZ - 4, JZ + 4, 'tela_som'))
    for k in range(9):
        x = -280 + k * 70
        p.append(cil((x, 128, JZ + 12), (x, 632, JZ + 12), 7, 'cromo', n=10))
    for y in (128, 632):
        p.append(cil((-290, y, JZ + 4), (290, y, JZ + 4), 5, 'cromo', n=8))
    p.append(_moldura(-306, 306, 114, 646, JZ + 6, 9, 'cromo'))
    # painel de seleção: títulos, teclas e a moedeira
    p.append(caixa(-310, 310, 660, 860, JZ, JZ + 20, 'cromo', 4.0))
    p.append(caixa(-290, 200, 712, 846, JZ + 20, JZ + 23, 'plastico_preto'))
    for c in range(2):
        for l in range(8):
            p.append(caixa(-280 + c * 240, -60 + c * 240, 718 + l * 16, 731 + l * 16, JZ + 23, JZ + 23.8, 'papel'))
    for k in range(10):
        x = -240 + k * 50
        p.append(caixa(x - 18, x + 18, 672, 700, JZ + 20, JZ + 34 - (8 if k == 3 else 0), 'tecla', 3.0))
        p.append(letreiro('ABCDEFGHJK'[k], 12, x, 680, JZ + 34.2 - (8 if k == 3 else 0), 'tinta_preta'))
    p.append(caixa(214, 294, 712, 846, JZ + 20, JZ + 28, 'cromo', 2.0))
    p.append(caixa(246, 262, 780, 828, JZ + 28, JZ + 29, 'tinta_preta'))                                              # fenda da ficha
    p.append(caixa(236, 272, 724, 752, JZ + 28, JZ + 29, 'tinta_preta'))
    p.append(_moldura(-302, 302, 874, 1266, JZ + 6, 10, 'cromo'))
    # o toca-discos e o carrossel de discos atrás do vidro
    p.append(cil((0, 884, 210), (0, 900, 210), 70, 'cromo', n=24))
    p.append(cil((0, 900, 210), (0, 904, 210), 118, 'disco', n=32))
    p.append(cil((0, 904, 210), (0, 905, 210), 40, 'rotulo_disco', n=20))
    p.append(_fio([(220, 890, 150), (220, 930, 150), (200, 935, 170), (80, 912, 225)], 3.5, 'cromo', res=0))
    p.append(cil((220, 884, 150), (220, 920, 150), 14, 'cromo', n=12))
    for k in range(15):
        x = -154 + k * 22
        y = 1090 + rnd.uniform(-3, 3)
        p.append(cil((x, y, 210), (x + 2.2, y, 210), 82, 'disco', n=24))
        p.append(cil((x - 0.3, y, 210), (x + 2.5, y, 210), 28, 'rotulo_disco' if k % 3 else 'papel', n=12))
    p.append(cil((-170, 1090, 210), (170, 1090, 210), 6, 'cromo', n=10))
    p.append(_torno([(0, 0), (16, 0), (10, 10), (6, 16), (0, 19)], 'cromo', 0, 1550, 0, n=14))                      # ponteira do arco
    for s in (-1, 1):                                                                                                 # frisos de cromo nas laterais
        p.append(caixa(s * 450 - 2.5, s * 450 + 2.5, 60, 1100, 236, 262, 'cromo'))
    for s in (-1, 1):                                                                                                 # tampas dos tubos
        p.append(_torno([(0, 0), (34, 0), (34, 18), (26, 26), (0, 26)], 'cromo', s * RA, 60, JZ + 20, n=16))
    p.append(_fio([(RA * 0.86 * math.cos(math.radians(t)), 1100 + RA * 0.86 * math.sin(math.radians(t)), JZ + 6) for t in range(0, 181, 6)], 9, 'cromo', res=0))
    parte('jukebox', p, origem=G(0, 0, 0), grupo='A')
    parte('luz_ambar', [_fio([(RA * math.cos(math.radians(t)), 1100 + RA * math.sin(math.radians(t)), JZ + 20) for t in range(0, 181, 6)], 22, 'luz_tubo', res=1)],
          origem=G(0, 0, 0), grupo='B')
    parte('luz_vermelha', [cil((s * RA, 86, JZ + 20), (s * RA, 1100, JZ + 20), 26, 'luz_tubo', n=16) for s in (-1, 1)], origem=G(0, 0, 0), grupo='B')
    parte('vidro_frente', [caixa(-300, 300, 880, 1260, JZ - 2, JZ + 2, 'vidro_visor')], origem=G(0, 0, 0), grupo='B')


FORMAS = {'painel_ferramentas': painel_ferramentas, 'balanca_medica': balanca_medica, 'fichario_catalogo': fichario_catalogo, 'jukebox': jukebox}
