"""Geladeira vertical de bebidas e carrinho de compras de arame no nível realista.

Medidas em mm nas coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente. As medidas de fora e o nó que
abre (porta da geladeira, com a dobradiça na direita) são os dos móveis antigos de props/mobilias."""
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


# ---------------------------------------------------------------------------- GELADEIRA DE BEBIDAS
def _garrafa(x, y, z, tipo, rnd):
    if tipo == 0:                                                             # lata
        return [_torno([(0, 0), (28, 0), (33, 8), (33, 112), (27, 122), (0, 122)], rnd.choice(('lata_azul', 'lata_laranja', 'lata')), x, y, z, n=10)]
    if tipo == 1:                                                             # pet de 2 L
        m = rnd.choice(('refri_escuro', 'pet_verde'))
        return [_torno([(0, 0), (48, 0), (52, 12), (52, 220), (30, 290), (15, 310), (0, 310)], m, x, y, z, n=10),
                _torno([(52.5, 90), (52.5, 170)], 'rotulo_vermelho' if m == 'refri_escuro' else 'rotulo_verde', x, y, z, n=10),
                _torno([(0, 0), (16, 0), (16, 18), (0, 18)], 'tampa_azul' if m == 'pet_verde' else 'vermelho', x, y + 310, z, n=8)]
    return [_torno([(0, 0), (32, 0), (34, 6), (34, 150), (14, 210), (13, 230), (0, 230)], 'vidro_ambar' if tipo == 2 else 'vidro_verde', x, y, z, n=10),   # long neck
            _torno([(0, 0), (15, 0), (15, 8), (0, 8)], 'latao', x, y + 230, z, n=8)]


def geladeira_bebidas():
    X, Z0, Z1, H, YB, YT = 350, -340, 300, 2000, 190, 1720
    c = caixa(-X, X, 20, H, Z0, Z1, 'chapa_vermelha', 4.0)
    cut(c, caixa(-X + 30, X - 30, YB, YT, Z0 + 40, Z1 + 5, 'chapa_vermelha'))
    p = [c]
    l = caixa(-X + 30, X - 30, YB, YT, Z0 + 40, Z1 - 2, 'liner_branco')
    cut(l, caixa(-X + 36, X - 36, YB + 6, YT - 6, Z0 + 46, Z1 + 5, 'liner_branco'))
    p.append(l)
    p.append(caixa(-X + 10, X - 10, 0, 20, Z0 + 20, Z1 - 40, 'plastico_preto', 3.0))   # base
    g = caixa(-X + 30, X - 30, 40, 170, Z1 - 3, Z1 + 1, 'plastico_preto', 2.0)          # grade do motor
    p.append(g)
    for k in range(12):
        y = 52 + k * 10
        p.append(caixa(-X + 40, X - 40, y, y + 4, Z1 + 1, Z1 + 4, 'plastico_cinza'))
    # letreiro iluminado no alto
    p.append(caixa(-X + 20, X - 20, YT + 40, H - 30, Z1, Z1 + 3, 'luminoso', 2.0))
    p.append(letreiro('BEBIDAS', 70, 0, YT + 150, Z1 + 3.2, 'vermelho'))
    p.append(letreiro('GELADAS', 44, 0, YT + 80, Z1 + 3.2, 'tinta_preta'))
    for k in range(10):                                                       # grade de cima, atrás
        p.append(caixa(-X + 40, X - 40, H - 140 + k * 12, H - 136 + k * 12, Z0 - 3, Z0, 'plastico_preto'))
    rnd = random.Random(27)
    prateleiras = [YB + 10, 470, 750, 1030, 1310]
    for i, y in enumerate(prateleiras):
        if i:
            p.append(lib.join([caixa(-X + 36, X - 36, y - 4, y, Z0 + 50, Z1 - 30, 'zincado')] +
                              [caixa(-X + 40 + k * 31, -X + 43 + k * 31, y - 6, y, Z0 + 50, Z1 - 30, 'zincado') for k in range(20)] +
                              [caixa(-X + 36, X - 36, y, y + 30, Z1 - 33, Z1 - 30, 'zincado')], 'prateleira'))
        tipo = (1, 0, 2, 3, 0)[i]
        n = 5 if tipo != 0 else 7
        for fila, zz in enumerate((Z1 - 90, Z1 - 200, Z1 - 310)):
            for k in range(n):
                if rnd.random() < (0.25 + 0.25 * fila):
                    continue
                x = -X + 36 + (2 * X - 72) * (k + 0.5) / n + rnd.uniform(-4, 4)
                p += _garrafa(x, y, zz + rnd.uniform(-6, 6), tipo, rnd)
    for x in (-X + 34, X - 34):                                                # lâmpadas de canto
        p.append(cil((x, YB + 40, Z1 - 60), (x, YT - 40, Z1 - 60), 10, 'vidro_lampada', n=8))
    parte('geladeira', p, origem=G(0, 0, 0), grupo='A')
    d = []
    fr = caixa(-X, X, 30, YT + 30, Z1, Z1 + 30, 'inox', 3.0)                  # caixilho de alumínio
    cut(fr, caixa(-X + 50, X - 50, 90, YT - 30, Z1 - 5, Z1 + 35, 'inox'))
    d.append(fr)
    d.append(caixa(-X + 20, X - 20, 34, 40, Z1 - 4, Z1, 'borracha'))
    d.append(caixa(-X + 14, -X + 34, 700, 1300, Z1 + 30, Z1 + 70, 'inox', 6.0))   # puxador comprido
    d.append(caixa(-X + 60, X - 60, 120, 200, Z1 + 18.5, Z1 + 19, 'luminoso'))    # adesivo "puxe"
    d.append(letreiro('PUXE', 30, 0, 145, Z1 + 19.2, 'vermelho'))
    porta = parte('porta', d, origem=G(X, 0, Z1 + 30), grupo='B')
    parte('vidro_porta', [caixa(-X + 50, X - 50, 90, YT - 30, Z1 + 12, Z1 + 18, 'vidro_visor')], origem=G(X, 0, Z1 + 30), pai=porta, grupo='B')   # vidro transparente (gerar.py)


# ---------------------------------------------------------------------------- CARRINHO DE COMPRAS
def _contorno(xa, z0, z1, y):
    """Retângulo de cima (x de -xa a xa, z de z0 a z1) na altura y, como lista de 4 cantos."""
    return [(-xa, y, z0), (xa, y, z0), (xa, y, z1), (-xa, y, z1)]


def _no_contorno(cs, t):
    """Ponto no perímetro (t de 0 a 1) do contorno de 4 cantos."""
    lados = [math.dist(cs[i], cs[(i + 1) % 4]) for i in range(4)]
    d = t * sum(lados)
    for i in range(4):
        if d <= lados[i] or i == 3:
            f = min(d / lados[i], 1.0)
            a, b = cs[i], cs[(i + 1) % 4]
            return tuple(a[k] + (b[k] - a[k]) * f for k in range(3))
        d -= lados[i]


def carrinho_compras():
    A = 'arame_cromo'
    topo = _contorno(272, -470, 470, 900)
    fundo = _contorno(215, -330, 420, 520)
    w = []
    w.append(_fio(topo, 6, A, fechado=True, res=1))
    w.append(_fio(fundo, 4, A, fechado=True, res=1))
    for k in range(1, 6):                                                     # arames deitados das laterais
        f = k / 6
        w.append(_fio([tuple(fundo[i][j] + (topo[i][j] - fundo[i][j]) * f for j in range(3)) for i in range(4)], 2.5, A, fechado=True, res=1))
    for k in range(64):                                                       # arames em pé
        t = (k + 0.5) / 64
        a, b = _no_contorno(fundo, t), _no_contorno(topo, t)
        w.append(cil(a, b, 2.5, A, n=5))
    for k in range(10):                                                       # fundo da cesta
        x = -200 + k * 400 / 9
        w.append(cil((x, 520, -330), (x, 520, 420), 2.5, A, n=5))
    p = [lib.join(w, 'cesta')]
    # alça, cadeirinha e chassi
    p.append(cil((-280, 1000, -500), (280, 1000, -500), 9, A, n=10))
    p.append(cil((-225, 1000, -500), (225, 1000, -500), 16, 'plastico_vermelho', n=14))
    for s in (-1, 1):
        p.append(_fio([(s * 272, 900, -470), (s * 278, 960, -490), (s * 280, 1000, -500)], 7, A, res=2))
        p.append(_fio([(s * 265, 990, -495), (s * 250, 700, -470), (s * 225, 200, -430), (s * 215, 140, -380), (s * 200, 135, 300), (s * 185, 140, 450)], 11, A, res=2))
        p.append(cil((s * 240, 500, -450), (s * 215, 520, -330), 5, A, n=6))
        p.append(cil((s * 210, 520, 380), (s * 190, 140, 420), 6, A, n=6))
    p.append(lib.join([cil((x, 180, -380), (x, 180, 380), 2.5, A, n=5) for x in [-190 + k * 380 / 8 for k in range(9)]] +
                      [cil((-200, 180, z), (200, 180, z), 3, A, n=5) for z in (-380, 0, 380)], 'bandeja'))
    for sx in (-1, 1):                                                       # bandeja presa no chassi
        for sz in (-1, 1):
            p.append(cil((sx * 190, 180, sz * 380), (sx * 205, 140, sz * 380), 3, A, n=5))
    p.append(caixa(-180, 180, 905, 960, -478, -462, 'plastico_vermelho', 4.0))   # plaquinha da alça
    for x, z in ((-185, -380), (185, -380), (-170, 440), (170, 440)):           # rodízios
        p.append(caixa(x - 25, x + 25, 120, 132, z - 25, z + 25, 'zincado', 2.0))
        for s in (-1, 1):
            p.append(caixa(x + s * 18 - 2.5, x + s * 18 + 2.5, 60, 122, z - 28, z + 8, 'zincado', 1.0))
        p.append(_torno([(0, -16), (52, -16), (60, -10), (62, 0), (60, 10), (52, 16), (0, 16)], 'borracha', x, 62, z - 10, n=18, eixo=(1, 0, 0)))
        p.append(cil((x - 20, 62, z - 10), (x + 20, 62, z - 10), 6, 'zincado', n=8))
    parte('carrinho', p, origem=G(0, 0, 0), grupo='A')


FORMAS = {'geladeira_bebidas': geladeira_bebidas, 'carrinho_compras': carrinho_compras}
