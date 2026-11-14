"""Freezer horizontal de tampas de correr, mesa de aço com máquina de escrever, armário de remédios com portas de vidro e
maca hospitalar com suporte de soro no nível realista.

Medidas em mm nas coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente. As medidas de fora e os nós que
abrem (tampa_esq, tampa_dir, gaveta_1, porta_esq, porta_dir) são os dos móveis antigos de props/mobilias. Os vidros são
malhas filhas das tampas e portas (vidro_*), trocadas pelo vidro transparente no gerar.py."""
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


# ---------------------------------------------------------------------------- FREEZER HORIZONTAL
def freezer_horizontal():
    X, Z0, Z1, H = 750, -330, 320, 860
    c = caixa(-X, X, 50, H, Z0, Z1, 'esmalte_branco', 8.0)
    cut(c, caixa(-X + 50, X - 50, 160, H + 10, Z0 + 50, Z1 - 50, 'esmalte_branco'))
    p = [c]
    l = caixa(-X + 50, X - 50, 160, H - 2, Z0 + 50, Z1 - 50, 'liner_branco')
    cut(l, caixa(-X + 56, X - 56, 166, H + 10, Z0 + 56, Z1 - 56, 'liner_branco'))
    p.append(l)
    p.append(caixa(-X + 20, X - 20, 0, 50, Z0 + 20, Z1 - 30, 'plastico_preto', 3.0))     # rodapé
    p.append(caixa(-X - 4, X + 4, H - 4, H + 18, Z0 - 4, Z1 + 4, 'plastico_cinza', 5.0)) # aro de cima com os trilhos
    cut(p[-1], caixa(-X + 44, X - 44, H - 10, H + 30, Z0 + 44, Z1 - 44, 'plastico_cinza'))
    p.append(caixa(-X + 30, X - 30, 330, 470, Z1 + 0.2, Z1 + 1.5, 'chapa_vermelha'))      # faixa e letreiro
    p.append(letreiro('SORVETES', 80, 0, 365, Z1 + 1.7, 'luminoso'))
    for k in range(14):                                                       # grade do motor na lateral
        p.append(caixa(X - 0.5, X + 2.5, 70 + k * 9, 74 + k * 9, Z0 + 80, Z0 + 260, 'plastico_preto'))
    p.append(caixa(X - 400, X - 360, 52, 58, Z1 - 5, Z1 + 25, 'plastico_cinza'))         # dreno
    # gelo nas paredes e o que sobrou dentro
    p.append(caixa(-X + 57, X - 57, 166, 200, Z0 + 57, Z1 - 57, 'gelo', 6.0))
    rnd = random.Random(5)
    for k in range(14):
        x = rnd.uniform(-X + 140, X - 140)
        z = rnd.uniform(Z0 + 120, Z1 - 120)
        if k % 2:
            o = _torno([(0, 0), (85, 0), (95, 120), (98, 128), (0, 128)], 'pote_sorvete', 0, 0, 0, n=14)
            _mover(o, lambda a, b, cc: (x + a, 200 + b + (k % 3) * 40, z + cc * 0.75))
        else:
            o = caixa(-110, 110, 0, 50, -80, 80, rnd.choice(('pacote_azul', 'sacola', 'caixa_cereal')), 18.0)
            _mover(o, lambda a, b, cc: (x + a * math.cos(k) - cc * math.sin(k), 200 + b + (k % 4) * 30, z + a * math.sin(k) + cc * math.cos(k)))
        p.append(o)
    parte('freezer', p, origem=G(0, 0, 0), grupo='A')
    for nome, x0, x1, y in (('tampa_esq', -X + 30, 15, H + 6), ('tampa_dir', -15, X - 30, H + 23)):
        zf = Z1 - 10 if nome == 'tampa_dir' else Z1 - 32                     # a de cima sai mais à frente: a mira acha ela com a de baixo aberta por baixo
        t = caixa(x0, x1, y, y + 14, Z0 + 26, zf, 'plastico_cinza', 3.0)
        cut(t, caixa(x0 + 30, x1 - 30, y - 5, y + 20, Z0 + 56, Z1 - 56, 'plastico_cinza'))
        pux = caixa(x0 + 20 if nome == 'tampa_dir' else x1 - 70, x0 + 70 if nome == 'tampa_dir' else x1 - 20, y + 14, y + 17, -150, 150, 'plastico_preto', 1.0)   # puxador rente (o jogo mira a tampa de cima)
        tampa = parte(nome, [t, pux], origem=G(0, 0, 0), grupo='B')
        parte('vidro_' + nome, [caixa(x0 + 30, x1 - 30, y + 5, y + 9, Z0 + 56, Z1 - 56, 'vidro_visor')], origem=G(0, 0, 0), pai=tampa, grupo='B')


# ---------------------------------------------------------------------------- MESA COM MÁQUINA DE ESCREVER
def _maquina(x0, y0, z0):
    """Máquina de escrever de escritório, de frente para +z, base no tampo."""
    p = []
    corpo = perfil([(-150, 0), (150, 0), (150, 40), (60, 80), (-80, 150), (-150, 150)], -210, 210, 'cinza_maquina', 6.0)
    p.append(corpo)
    p.append(caixa(-215, 215, 70, 160, -150, -80, 'cinza_maquina', 8.0))
    for r in range(4):                                                        # teclas redondas em degraus
        zz = 120 - r * 32
        yy = 52 + r * 20
        n = 11 - (r == 3)
        for k in range(n):
            xx = -150 + k * 30 + (r % 2) * 10
            p.append(cil((xx, yy, zz), (xx, yy + 12, zz - 4), 11, 'tecla_maquina', n=10))
            p.append(cil((xx, yy + 12, zz - 4), (xx, yy + 14, zz - 4.5), 9.5, 'luminoso', n=10))
    p.append(caixa(-90, 90, 20, 32, 125, 150, 'tecla_maquina', 5.0))           # barra de espaço
    p.append(cil((-240, 190, -110), (240, 190, -110), 34, 'borracha', n=18))  # rolo
    for s in (-1, 1):
        p.append(_torno([(0, 0), (30, 0), (30, 18), (24, 22), (0, 22)], 'tecla_maquina', s * 245, 190, -110, n=14, eixo=(s, 0, 0)))
    p.append(caixa(-230, 230, 160, 180, -150, -60, 'aco_polido', 2.0))        # carro
    p.append(_fio([(-235, 200, -90), (-290, 230, -60), (-300, 240, 10)], 5, 'aco_polido', res=1))   # alavanca de volta
    p.append(frente([(-105, 200), (105, 200), (105, 420), (-105, 415)], -146, -145, 'folha_sulfite'))   # folha no rolo
    for k in range(6):
        p.append(caixa(-85, -85 + (120 if k % 3 else 160), 380 - k * 14, 384 - k * 14, -144.9, -144.7, 'tinta_preta'))
    for o in p:
        _mover(o, lambda a, b, cc: (x0 + a, y0 + b, z0 + cc))
    return p


def mesa_maquina_escrever():
    X, Z0, Z1, T = 700, -360, 360, 740
    A = 'cinza_mesa'
    p = [caixa(-X, X, T, T + 22, Z0, Z1, 'formica', 3.0)]
    p.append(caixa(-X + 4, X - 4, T - 8, T, Z0 + 4, Z1 - 4, A, 2.0))
    gx0, gx1 = 160, X - 20                                                     # gaveteiro da direita
    c = caixa(gx0, gx1, 60, T - 8, Z0 + 20, Z1 - 10, A, 3.0)
    cut(c, caixa(gx0 + 15, gx1 - 15, T - 170, T - 20, Z0 + 30, Z1, A))
    p.append(c)
    for y0, y1 in ((80, 320), (340, T - 190)):                               # gavetas fixas de baixo (só a frente)
        p.append(caixa(gx0 + 18, gx1 - 18, y0, y1, Z1 - 10, Z1 + 8, A, 4.0))
        p.append(caixa((gx0 + gx1) / 2 - 60, (gx0 + gx1) / 2 + 60, (y0 + y1) / 2 + 40, (y0 + y1) / 2 + 52, Z1 + 8, Z1 + 26, 'aco_polido', 3.0))
        p.append(caixa((gx0 + gx1) / 2 - 30, (gx0 + gx1) / 2 + 30, y1 - 40, y1 - 18, Z1 + 8, Z1 + 9, 'luminoso'))   # porta-etiqueta
    p.append(caixa(gx0 + 10, gx1 - 10, 0, 60, Z0 + 30, Z1 - 30, 'plastico_preto'))
    xa = -X + 20                                                               # painel da esquerda
    p.append(caixa(xa, xa + 30, 0, T - 8, Z0 + 20, Z1 - 10, A, 3.0))
    p.append(caixa(xa + 30, gx0, 330, T - 8, Z0 + 20, Z0 + 38, A, 2.0))        # painel de trás
    # máquina, papéis, carimbo e telefone de disco
    p += _maquina(-200, T + 22, 40)
    rnd = random.Random(11)
    for k in range(5):
        f = caixa(-105, 105, 0, 0.6, -148, 148, 'folha_sulfite' if k % 2 else 'papel')
        a = rnd.uniform(-0.3, 0.3)
        _mover(f, lambda x, y, z: (330 + x * math.cos(a) - z * math.sin(a), T + 22 + k * 0.8 + y, 60 + x * math.sin(a) + z * math.cos(a)))
        p.append(f)
    p.append(caixa(500, 600, T + 22, T + 32, -260, -180, 'tinta_preta', 3.0))  # almofada de carimbo
    p.append(_torno([(0, 0), (22, 0), (22, 30), (10, 40), (12, 90), (16, 100), (0, 104)], 'baquelite', 560, T + 32, -120, n=12))
    tx, tz = 450, -230                                                         # telefone de disco
    p.append(perfil([(-90, 0), (90, 0), (70, 70), (-60, 90)], tx - 90, tx + 90, 'baquelite', 10.0))
    _mover(p[-1], lambda x, y, z: (x, T + 22 + y, tz + z))
    p.append(_torno([(0, 0), (55, 0), (55, 6), (0, 6)], 'aco_polido', tx, T + 22, tz + 30, n=20, eixo=(0, 0.6, 0.8)))
    _mover(p[-1], lambda x, y, z: (x, y + 70, z))
    p.append(_fio([(tx - 100, T + 115, tz - 20), (tx - 60, T + 135, tz - 20), (tx + 60, T + 135, tz - 20), (tx + 100, T + 115, tz - 20)], 18, 'baquelite', res=2))
    parte('mesa', p, origem=G(0, 0, 0), grupo='A')
    g = q._gaveta(gx0 + 18, gx1 - 18, T - 170, T - 20, Z0 + 40, Z1 - 10, mat_frente=A, esp=18, pux=((gx0 + gx1) / 2,))
    g.append(_torno([(0, 0), (14, 0), (14, 80), (0, 80)], 'latao', gx0 + 100, T - 150, 40, n=8, eixo=(0, 0, 1)))   # chaves
    g.append(_fio([(gx0 + 100, T - 150, 120), (gx0 + 130, T - 150, 160), (gx0 + 160, T - 150, 120), (gx0 + 130, T - 150, 100)], 3, 'latao', fechado=True, res=2))
    parte('gaveta_1', g, origem=G(0, 0, 0), grupo='B')


# ---------------------------------------------------------------------------- ARMÁRIO DE REMÉDIOS
def armario_remedios():
    X, Z0, Z1, H = 450, -190, 190, 1800
    B = 'esmalte_branco'
    c = caixa(-X, X, 120, H - 60, Z0, Z1, B, 4.0)
    cut(c, caixa(-X + 25, X - 25, 145, H - 85, Z0 + 20, Z1 + 5, B))
    p = [c]
    for s in (-1, 1):                                                          # pés
        for z in (Z0 + 30, Z1 - 30):
            p.append(_torno([(0, 0), (22, 0), (18, 10), (16, 120), (0, 120)], 'cromo', s * (X - 35), 0, z, n=12))
    p.append(caixa(-X - 5, X + 5, H - 60, H - 40, Z0 - 5, Z1 + 5, B, 4.0))     # chapéu
    p.append(caixa(-X + 20, X - 20, H - 40, H, Z0 + 5, Z1 - 20, B, 4.0))
    p.append(caixa(-60, 60, H - 30, H - 10, Z1 - 20, Z1 - 19, B))
    p.append(frente([(-12, H - 38), (12, H - 38), (12, H - 26), (24, H - 26), (24, H - 14), (12, H - 14), (12, H - 2), (-12, H - 2),
                     (-12, H - 14), (-24, H - 14), (-24, H - 26), (-12, H - 26)], Z1 - 19, Z1 - 18, 'cruz_vermelha'))
    rnd = random.Random(19)
    for y in (420, 740, 1060, 1380):                                           # prateleiras de vidro com remédios
        p.append(caixa(-X + 26, X - 26, y, y + 6, Z0 + 22, Z1 - 30, 'vidro_soro'))
        x = -X + 50
        while x < X - 60:
            t = rnd.random()
            if t < 0.25:
                x += rnd.uniform(40, 90)
                continue
            if t < 0.6:
                r = rnd.uniform(18, 30)
                p.append(_torno([(0, 0), (r, 0), (r, r * 3), (r * 0.5, r * 3.6), (r * 0.5, r * 4), (0, r * 4)], rnd.choice(('vidro_ambar', 'pet', 'vidro_soro')), x + r, y + 6, rnd.uniform(-60, 40), n=10))
                p.append(_torno([(0, 0), (r * 0.55, 0), (r * 0.55, 14), (0, 14)], rnd.choice(('tampa_azul', 'plastico_preto', 'liner_branco')), x + r, y + 6 + r * 4, 0, n=8))
                x += 2 * r + 10
            else:
                w, h, d = rnd.uniform(30, 70), rnd.uniform(60, 140), rnd.uniform(60, 120)
                p.append(caixa(x, x + w, y + 6, y + 6 + h, -d / 2 - 20, d / 2 - 20, rnd.choice(('caixa_azul', 'caixa_verde', 'liner_branco', 'cal_papel')), 2.0))
                x += w + 6
    p.append(caixa(-X + 25, X - 25, 145, 380, Z0 + 20, Z0 + 21, B))
    parte('armario', p, origem=G(0, 0, 0), grupo='A')
    for nome, s in (('porta_esq', -1), ('porta_dir', 1)):
        x0, x1 = sorted((s * X, 0))
        fr = caixa(x0 + 2, x1 - 2, 125, H - 65, Z1, Z1 + 22, B, 3.0)
        cut(fr, caixa(x0 + 45, x1 - 45, 175, H - 115, Z1 - 5, Z1 + 30, B))
        d = [fr]
        if s < 0:
            d.append(caixa(-30, -10, 850, 980, Z1 + 22, Z1 + 40, 'cromo', 4.0))
            d.append(_torno([(0, 0), (12, 0), (12, 8), (0, 10)], 'latao', -20, 1010, Z1 + 22, n=10, eixo=(0, 0, 1)))   # fechadura
        else:
            d.append(caixa(10, 30, 850, 980, Z1 + 22, Z1 + 40, 'cromo', 4.0))
        porta = parte(nome, d, origem=G(s * X, 0, Z1 + 11), grupo='B')
        parte('vidro_' + nome, [caixa(x0 + 45, x1 - 45, 175, H - 115, Z1 + 9, Z1 + 13, 'vidro_visor')], origem=G(s * X, 0, Z1 + 11), pai=porta, grupo='B')


# ---------------------------------------------------------------------------- MACA
def maca():
    Xm, Z0, Z1, YC = 320, -900, 900, 640                                       # meia largura, pés e cabeceira, altura do colchão
    A = 'cromo'
    p = []
    for s in (-1, 1):                                                          # longarinas e pernas em X
        p.append(cil((s * Xm, YC - 60, Z0), (s * Xm, YC - 60, Z1), 14, A, n=10))
        p.append(cil((s * (Xm - 30), 180, Z0 + 150), (s * (Xm - 30), YC - 70, Z1 - 150), 16, A, n=10))
        p.append(cil((s * (Xm - 30), 180, Z1 - 150), (s * (Xm - 30), YC - 70, Z0 + 150), 16, A, n=10))
        p.append(cil((s * (Xm - 30), 180, Z0 + 120), (s * (Xm - 30), 180, Z1 - 120), 18, A, n=10))
    for z in (Z0, Z1, Z0 + 150, Z1 - 150):
        y = YC - 60 if abs(z) == Z1 else 180
        p.append(cil((-Xm, y, z), (Xm, y, z), 12, A, n=8))
    for sx in (-1, 1):                                                         # rodízios
        for z in (Z0 + 120, Z1 - 120):
            x = sx * (Xm - 30)
            p.append(cil((x, 180, z), (x, 120, z), 12, 'zincado', n=8))
            p.append(caixa(x - 22, x + 22, 80, 125, z - 30, z + 10, 'zincado', 2.0))
            p.append(_torno([(0, -14), (48, -14), (55, -8), (56, 0), (55, 8), (48, 14), (0, 14)], 'borracha', x, 56, z - 15, n=16, eixo=(1, 0, 0)))
    p.append(caixa(-Xm + 10, Xm - 10, YC - 50, YC - 30, Z0 + 20, Z1 - 20, 'aco_banco', 2.0))     # estrado
    # colchão: pés retos, encosto levantado
    ZD = 150
    p.append(caixa(-Xm + 15, Xm - 15, YC - 30, YC + 70, Z0 + 20, ZD, 'vinil_maca', 30.0))
    e = caixa(-Xm + 15, Xm - 15, 0, 100, 0, Z1 - 20 - ZD, 'vinil_maca', 30.0)
    a = math.radians(32)
    _mover(e, lambda x, y, z: (x, YC - 30 + y * math.cos(a) + z * math.sin(a), ZD + z * math.cos(a) - y * math.sin(a)))
    p.append(e)
    ap = caixa(-Xm + 30, Xm - 30, 0, 20, 0, Z1 - 60 - ZD, 'aco_banco', 2.0)   # apoio do encosto
    _mover(ap, lambda x, y, z: (x, YC - 50 + y * math.cos(a) + z * math.sin(a), ZD + z * math.cos(a) - y * math.sin(a)))
    p.append(ap)
    p.append(cil((-Xm + 40, YC - 50, Z1 - 220), (-Xm + 40, YC + 180, Z1 - 340), 10, A, n=8))
    p.append(cil((Xm - 40, YC - 50, Z1 - 220), (Xm - 40, YC + 180, Z1 - 340), 10, A, n=8))
    l = caixa(-Xm + 12, Xm - 12, YC + 70, YC + 72, Z0 + 18, ZD - 20, 'lencol', 1.0)     # lençol
    p.append(l)
    for s in (-1, 1):                                                          # abas do lençol caídas dos lados
        xa, xb = sorted((s * (Xm - 13), s * (Xm - 11)))
        p.append(caixa(xa, xb, YC - 40, YC + 72, Z0 + 18, ZD - 20, 'lencol'))
    t = q._travesseiro(0, 0, 0, 220, 150, 55)
    for o in (t if isinstance(t, list) else [t]):
        _mover(o, lambda x, y, z: (x, YC + 70 + 450 * math.sin(a) + y * math.cos(a) + z * math.sin(a), ZD + 450 * math.cos(a) - 40 + z * math.cos(a) - y * math.sin(a)))
        p.append(o)
    for s in (-1, 1):                                                          # grades laterais abaixadas
        x = s * (Xm + 25)
        p.append(cil((x, YC - 10, Z0 + 250), (x, YC - 10, Z1 - 500), 9, A, n=8))
        p.append(cil((x, YC - 90, Z0 + 250), (x, YC - 90, Z1 - 500), 9, A, n=8))
        for z in (Z0 + 250, (Z0 + Z1 - 250) / 2, Z1 - 500):
            p.append(cil((x, YC - 90, z), (x, YC - 10, z), 8, A, n=6))
        p.append(cil((x, YC - 60, Z0 + 250), (s * Xm, YC - 60, Z0 + 250), 8, A, n=6))
    # suporte de soro na cabeceira, com a bolsa
    sx, sz = Xm - 10, Z1 - 10
    p.append(cil((sx, YC - 60, sz), (sx, 1820, sz), 11, 'inox', n=10))
    for k in range(2):
        a2 = math.pi * k
        p.append(_fio([(sx, 1820, sz), (sx + 60 * math.cos(a2), 1860, sz), (sx + 80 * math.cos(a2), 1840, sz)], 4, 'inox', res=2))
    bx = sx + 80
    p.append(_fio([(bx, 1840, sz), (bx, 1800, sz)], 2, 'inox', res=1))
    p.append(_torno([(0, 0), (12, 0), (40, 40), (55, 160), (45, 230), (0, 245)], 'vidro_soro', bx, 1555, sz, n=12))
    _mover(p[-1], lambda x, y, z: (bx + (x - bx), y, sz + (z - sz) * 0.4))
    p.append(_fio([(bx, 1555, sz), (bx - 20, 1300, sz - 30), (bx - 150, 900, sz - 200), (40, YC + 120, 80)], 2.0, 'borracha_soro', res=3))
    parte('maca', p, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- GLOBO TERRESTRE
_CONTINENTES = [   # (latitude, longitude, raio em graus) de manchas que somadas lembram os continentes
    (50, -100, 18), (40, -90, 14), (60, -120, 14), (65, -45, 9), (25, -100, 8), (15, -88, 5),       # América do Norte e Groenlândia
    (-10, -60, 15), (-25, -60, 11), (-40, -68, 7), (5, -70, 8),                                    # América do Sul
    (10, 20, 16), (-10, 25, 13), (-28, 25, 8), (25, 10, 12), (-20, 47, 4),                          # África
    (50, 15, 9), (55, 40, 12), (60, 90, 18), (45, 80, 14), (35, 105, 14), (25, 80, 8), (20, 45, 8),   # Europa e Ásia
    (65, 140, 12), (0, 115, 6), (-25, 135, 12), (-40, 172, 3), (-78, 0, 14), (-78, 120, 14), (-78, -120, 14)]


def globo_terrestre():
    R, CY = 150, 250
    p = [_torno([(0, 0), (100, 0), (104, 6), (100, 14), (60, 24), (40, 30), (30, 40), (22, 44), (0, 44)], 'nogueira_y', 0, 0, 0, n=24)]
    p.append(_torno([(0, 44), (12, 44), (12, 70), (0, 70)], 'latao', 0, 0, 0, n=10))
    inc = math.radians(23.5)
    def gira(x, y, z):                                                       # eixo inclinado para o lado (em torno de z)
        return (x * math.cos(inc) - y * math.sin(inc), CY + x * math.sin(inc) + y * math.cos(inc), z)
    esf = _torno([(R * math.sin(math.radians(a)), -R * math.cos(math.radians(a))) for a in range(0, 181, 10)], 'globo_mar', 0, 0, 0, n=28)
    _mover(esf, gira)
    p.append(esf)
    rnd = random.Random(23)
    import bmesh
    centro = lib.P(*G(*gira(0, 0, 0)))
    def ponto(a, b, h=R + 1.0):
        x, y, z = h * math.cos(a) * math.cos(b), h * math.sin(a), h * math.cos(a) * math.sin(b)
        return lib.P(*G(*gira(x, y, z)))
    N = 14
    for lat, lon, r in _CONTINENTES:                                          # manchas de terra: leque em dois anéis, rente à esfera
        for _ in range(3):
            la, lo = math.radians(lat + rnd.uniform(-r, r) * 0.45), math.radians(lon + rnd.uniform(-r, r) * 0.45)
            fs = [rnd.uniform(0.55, 1.0) * math.radians(r * 0.75) for _ in range(N)]
            bm = bmesh.new()
            c = bm.verts.new(ponto(la, lo))
            aneis = [[bm.verts.new(ponto(la + f * rr * math.sin(2 * math.pi * k / N), lo + f * rr * math.cos(2 * math.pi * k / N) / max(math.cos(la), 0.3)))
                      for k, rr in enumerate(fs)] for f in (0.5, 1.0)]
            fa = [bm.faces.new((c, aneis[0][k], aneis[0][(k + 1) % N])) for k in range(N)]
            fa += [bm.faces.new((aneis[0][k], aneis[1][k], aneis[1][(k + 1) % N], aneis[0][(k + 1) % N])) for k in range(N)]
            bm.normal_update()
            if fa[0].normal.dot(c.co - centro) < 0:                           # virada para fora da esfera
                for f in fa:
                    f.normal_flip()
            me = lib.bpy.data.meshes.new('mancha')
            bm.to_mesh(me)
            o = lib.bpy.data.objects.new('mancha', me)
            lib.bpy.context.scene.collection.objects.link(o)
            o.data.materials.append(lib.bpy.data.materials.get('globo_terra') or _mat_de('globo_terra'))
            p.append(o)
    mer = _anel([(R + 6, -3), (R + 12, -3), (R + 12, 3), (R + 6, 3)], 'latao', 0, 0, 0, n=40, eixo=(0, 0, 1))   # meridiano
    _mover(mer, gira)
    p.append(mer)
    p.append(cil(gira(0, -R - 14, 0), gira(0, R + 14, 0), 4, 'latao', n=8))
    a, b = gira(0, -R - 12, 0), (0, 70, 0)
    p.append(_fio([b, (b[0] + (a[0] - b[0]) * 0.5, (a[1] + b[1]) / 2, 0), a], 7, 'latao', res=2))
    parte('globo', p, origem=G(0, 0, 0), grupo='A')


def _mat_de(nome):
    o = _torno([(0, 0), (1, 0), (0, 1)], nome, n=3)
    m = o.data.materials[0]
    lib.bpy.data.objects.remove(o)
    return m


def _anel(prof, mat, x=0, y=0, z=0, n=20, eixo=(0, 1, 0)):
    return lib.lathe([(h, r) for r, h in prof], mat, n=n, c0=G(x, y, z), eixo=G(*eixo), anel=True)


# ---------------------------------------------------------------------------- CESTA DE COMPRAS
def cesta_compras():
    V = 'plastico_vermelho'
    X0, Z0, X1, Z1, H = 235, 145, 205, 120, 300                               # meia largura e meio fundo em cima e embaixo
    def lado(f, y):                                                           # contorno na altura y (f de 0 embaixo a 1 em cima)
        x, z = X1 + (X0 - X1) * f, Z1 + (Z0 - Z1) * f
        return [(-x, y, -z), (x, y, -z), (x, y, z), (-x, y, z)]
    p = [caixa(-X1, X1, 0, 8, -Z1, Z1, V, 2.0)]                               # fundo
    for k in range(9):
        x = -X1 + 20 + k * (2 * X1 - 40) / 8
        p.append(caixa(x - 3, x + 3, -3, 0, -Z1 + 6, Z1 - 6, V))                # pezinhos de baixo
    for k in range(7):                                                        # arcos deitados das paredes
        f = (k + 0.5) / 7
        p.append(_fio(lado(f, 12 + f * (H - 30)), 4, V, fechado=True, res=1))
    p.append(_fio(lado(1, H - 8), 9, V, fechado=True, res=1))                  # borda grossa
    n = 30
    for k in range(n):                                                        # montantes
        t = (k + 0.5) / n
        a = _no_perim(lado(0, 6), t)
        b = _no_perim(lado(1, H - 8), t)
        p.append(cil(a, b, 4, V, n=5))
    for s in (-1, 1):                                                         # alças deitadas para fora
        arco = [(s * (X0 - 20), H - 4, -110)] + [(s * (X0 + 40 + 30 * math.sin(math.radians(t))), H - 4 - 28 * math.sin(math.radians(t)), -110 * math.cos(math.radians(t))) for t in range(20, 180, 20)] + [(s * (X0 - 20), H - 4, 110)]
        p.append(_fio(arco, 7, 'plastico_preto', res=2))
    p.append(caixa(-60, 60, H - 60, H - 20, Z0 + 4, Z0 + 6, 'luminoso', 1.0))   # etiqueta do mercado
    p.append(letreiro('MERCADO', 12, 0, H - 46, Z0 + 6.2, 'vermelho'))
    p.append(_torno([(0, 0), (28, 0), (33, 8), (33, 112), (27, 122), (0, 122)], 'lata_laranja', 0, 0, 0, n=12))   # uma lata deitada esquecida
    _mover(p[-1], lambda x, y, z: (y - 60, 41 + x, -30 + z))
    parte('cesta', p, origem=G(0, 0, 0), grupo='A')


def _no_perim(cs, t):
    lados = [math.dist(cs[i], cs[(i + 1) % 4]) for i in range(4)]
    d = t * sum(lados)
    for i in range(4):
        if d <= lados[i] or i == 3:
            f = min(d / lados[i], 1.0)
            a, b = cs[i], cs[(i + 1) % 4]
            return tuple(a[k] + (b[k] - a[k]) * f for k in range(3))
        d -= lados[i]


# ---------------------------------------------------------------------------- CADEIRA DE RODAS
def _roda(x, y, z, R, raios=24):
    """Roda grande de cadeira de rodas, no plano yz (eixo x)."""
    p = [_anel([(R - 22, -14), (R - 6, -16), (R, -8), (R, 8), (R - 6, 16), (R - 22, 14)], 'borracha', x, y, z, n=40, eixo=(1, 0, 0))]   # pneu
    p.append(_anel([(R - 34, -9), (R - 22, -9), (R - 22, 9), (R - 34, 9)], 'cromo', x, y, z, n=40, eixo=(1, 0, 0)))                        # aro
    s = 1 if x > 0 else -1
    p.append(_anel([(R - 40, -5), (R - 30, -5), (R - 30, 5), (R - 40, 5)], 'cromo', x + s * 34, y, z, n=36, eixo=(1, 0, 0)))               # aro de empurrar
    for k in range(6):
        a = 2 * math.pi * k / 6
        p.append(cil((x, y + (R - 30) * math.sin(a), z + (R - 30) * math.cos(a)), (x + s * 34, y + (R - 35) * math.sin(a), z + (R - 35) * math.cos(a)), 3, 'cromo', n=5))
    p.append(_torno([(0, -30), (30, -30), (30, 30), (0, 30)], 'cromo', x, y, z, n=14, eixo=(1, 0, 0)))                                       # cubo
    for k in range(raios):
        a = 2 * math.pi * k / raios
        dx = 24 if k % 2 else -24
        p.append(cil((x + dx, y + 24 * math.sin(a + 0.3), z + 24 * math.cos(a + 0.3)), (x, y + (R - 34) * math.sin(a), z + (R - 34) * math.cos(a)), 1.4, 'inox', n=4))
    return p


def _rodizio(x, z):
    p = [cil((x, 300, z), (x, 210, z), 10, 'cromo', n=8)]
    p.append(caixa(x - 26, x + 26, 190, 214, z - 50, z + 10, 'cromo', 3.0))
    for s in (-1, 1):
        p.append(caixa(x + s * 22 - 3, x + s * 22 + 3, 75, 200, z - 50, z - 30, 'cromo', 1.5))
    p.append(_torno([(0, -16), (65, -16), (75, -8), (76, 0), (75, 8), (65, 16), (0, 16)], 'borracha', x, 78, z - 40, n=18, eixo=(1, 0, 0)))
    return p


def cadeira_rodas():
    A, W, ZT, ZF = 'cromo', 230, -200, 280                                    # meia largura do assento, eixo das rodas, frente
    p = []
    for s in (-1, 1):
        x = s * W
        p += _roda(s * 300, 300, ZT, 300)
        p.append(cil((s * 300, 300, ZT), (x, 300, ZT), 9, A, n=8))             # eixo
        p.append(_fio([(x, 960, -330), (x, 880, -320), (x, 520, -280), (x, 300, -250), (x, 300, ZF), (x, 520, ZF - 20), (x, 520, -250)], 12, A, res=2))   # quadro lateral
        p.append(cil((x, 960, -330), (x, 1000, -420), 12, A, n=10))           # manopla
        p.append(_torno([(0, 0), (16, 0), (17, 6), (17, 110), (16, 116), (0, 116)], 'borracha', 0, 0, 0, n=10, eixo=(0, 0.4, -0.92)))
        _mover(p[-1], lambda a, b, c, x=x: (x + a, 960 + b + 22, -330 + c - 50))
        p.append(_fio([(x, 520, 200), (x, 700, 190), (x, 700, -180), (x, 560, -260)], 10, A, res=2))      # braço
        p.append(caixa(x - 25, x + 25, 700, 728, -170, 170, 'plastico_preto', 8.0))                      # apoio de braço
        p += _rodizio(s * (W - 10), ZF)
        p.append(_fio([(x, 520, ZF - 10), (x - s * 10, 300, ZF + 90), (x - s * 10, 140, ZF + 150)], 10, A, res=2))   # perna do apoio de pé
        p.append(caixa(x - s * 10 - 95 * (s > 0) - 5 * (s < 0), x - s * 10 + 95 * (s < 0) + 5 * (s > 0), 130, 142, ZF + 120, ZF + 240, 'plastico_preto', 4.0))   # apoio de pé
    p.append(cil((-W, 300, -250), (W, 300, ZF - 30), 9, A, n=8))               # X dobrável embaixo do assento
    p.append(cil((W, 300, -250), (-W, 300, ZF - 30), 9, A, n=8))
    assento = caixa(-W + 6, W - 6, 508, 520, -250, ZF - 20, 'pano_azul', 4.0)
    _mover(assento, lambda x, y, z: (x, y - 18 * (1 - (x / W) ** 2), z))      # lona cede no meio
    p.append(assento)
    enc = caixa(-W + 6, W - 6, 530, 900, -2, 6, 'pano_azul', 3.0)
    _mover(enc, lambda x, y, z: (x, y, -300 - (y - 530) * 0.08 + z - 14 * (1 - (x / W) ** 2)))
    p.append(enc)
    parte('cadeira', p, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- BIOMBO
def biombo():
    A, H, L = 'cromo', 1700, 540
    # três folhas em zigue-zague, vista de cima
    cantos = [(-810, -60), (-280, 60), (280, -60), (810, 60)]
    p = []
    for i in range(3):
        (xa, za), (xb, zb) = cantos[i], cantos[i + 1]
        if i == 0:
            p.append(_fio([(xa, 120, za), (xa, H, za)], 12, A, res=1))
        p.append(_fio([(xb, 120, zb), (xb, H, zb)], 12, A, res=1))
        for y in (300, H - 40):
            p.append(cil((xa, y, za), (xb, y, zb), 9, A, n=8))
        # cortina franzida entre as barras
        n = 26
        pts = []
        for k in range(n + 1):
            f = k / n
            x, z = xa + (xb - xa) * f, za + (zb - za) * f
            nx, nz = -(zb - za) / math.dist((xa, za), (xb, zb)), (xb - xa) / math.dist((xa, za), (xb, zb))
            o = 14 * math.sin(f * math.pi * 12)
            pts.append((x + nx * o, z + nz * o))
        for k in range(n):
            (x0, z0), (x1, z1) = pts[k], pts[k + 1]
            p.append(planta(_quad(x0, z0, x1, z1), 320, H - 60, 'cortina_verde'))
        for k in range(10):                                                    # argolas
            f = (k + 0.5) / 10
            x, z = xa + (xb - xa) * f, za + (zb - za) * f
            p.append(_anel([(10, -3), (14, -3), (14, 3), (10, 3)], A, x, H - 52, z, n=10, eixo=(0, 0, 1)))
    for x, z in cantos:                                                        # rodízios
        p.append(caixa(x - 18, x + 18, 100, 122, z - 18, z + 18, A, 2.0))
        p.append(caixa(x - 12, x + 12, 40, 100, z - 30, z + 4, 'zincado', 1.5))
        p.append(_torno([(0, -10), (34, -10), (40, -4), (40, 4), (34, 10), (0, 10)], 'borracha', x, 40, z - 18, n=14, eixo=(1, 0, 0)))
        p.append(_torno([(0, 0), (14, 0), (14, 10), (8, 14), (0, 14)], 'plastico_preto', x, H, z, n=10))
    parte('biombo', p, origem=G(0, 0, 0), grupo='A')


def _quad(x0, z0, x1, z1):
    """Faixa fina de cortina (2 mm) entre dois pontos vistos de cima."""
    d = math.dist((x0, z0), (x1, z1)) or 1
    nx, nz = -(z1 - z0) / d, (x1 - x0) / d
    pts = [(x0 - nx, z0 - nz), (x1 - nx, z1 - nz), (x1 + nx, z1 + nz), (x0 + nx, z0 + nz)]
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1]))
    return pts if area > 0 else pts[::-1]


FORMAS = {'freezer_horizontal': freezer_horizontal, 'mesa_maquina_escrever': mesa_maquina_escrever, 'armario_remedios': armario_remedios, 'maca': maca, 'globo_terrestre': globo_terrestre, 'cesta_compras': cesta_compras,
          'cadeira_rodas': cadeira_rodas, 'biombo': biombo}
