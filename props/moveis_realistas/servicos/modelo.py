"""Pallet de madeira, banco de espera, estante de biblioteca dupla face e frigobar no nível realista.

Medidas em mm nas coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente. As medidas de fora e os nós
que abrem (porta do frigobar) são os dos móveis antigos de props/mobilias."""
import math, os, random, importlib.util
import lib
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte, letreiro


def _carregar(nome, pasta):
    spec = importlib.util.spec_from_file_location(nome, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', pasta, 'modelo.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


q = _carregar('modelo_quarto', 'quarto')
sala = _carregar('modelo_sala', 'sala')
_torno, _fio = q._torno, q._fio
N = q.N


# ---------------------------------------------------------------------------- PALLET
def pallet():
    X, Z, H = 600, 400, 144
    rnd = random.Random(4)
    p = []
    for z in (-Z + 50, 0, Z - 50):                                          # tábuas de baixo
        p.append(caixa(-X, X, 0, 22, z - 50, z + 50, 'crua_x', 2.5))
    for z in (-Z + 50, 0, Z - 50):                                          # tacos
        for x in (-X + 50, 0, X - 50):
            p.append(caixa(x - 50 + rnd.uniform(0, 2), x + 50 - rnd.uniform(0, 2), 22, 122, z - 48, z + 48, 'crua_y', 4.0))
    xs = [-X + 50 + k * (2 * X - 100) / 6 for k in range(7)]
    for k, x in enumerate(xs):                                              # tábuas de cima
        larg = 50 if k in (0, 6, 3) else 46
        y1 = H + rnd.uniform(-1.5, 0.5)
        if k == 2:                                                          # uma tábua partida e afundada
            p.append(caixa(x - larg, x + larg, 122, y1, -Z, -60, 'crua_z', 2.0))
            p.append(frente([(x - larg, 122), (x + larg, 122), (x + larg, y1 - 4), (x - larg, y1 - 9)], 70, 260, 'crua_z'))
            p.append(caixa(x - larg, x + larg, 122, y1, 300, Z, 'crua_z', 2.0))
            continue
        p.append(caixa(x - larg, x + larg, 122, y1, -Z + rnd.uniform(0, 3), Z - rnd.uniform(0, 3), 'crua_z', 2.5))
        for z in (-Z + 50, 0, Z - 50):                                      # pregos
            for dx in (-larg * 0.5, larg * 0.5):
                p.append(_torno([(0, 0), (4.5, 0), (4.5, 0.8), (0, 1.2)], 'ferrugem' if rnd.random() < 0.6 else 'zincado', x + dx, y1 - 0.3, z + rnd.uniform(-12, 12), n=6))
    for x in (-X + 50, X - 50):                                             # carimbo de tratamento no taco do meio
        p.append(letreiro('HT', 22, x, 60, Z - 1.6, 'tinta_preta'))
    parte('pallet', p, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- BANCO DE ESPERA
def _concha(x):
    """Concha de polipropileno: assento e encosto numa peça só, curvada (faixas ao longo do perfil, 7 mm de espessura)."""
    w, e = 245, 7.0
    linha = [(212, 440), (196, 456), (120, 459), (-10, 454), (-140, 446), (-188, 458), (-212, 510), (-232, 640), (-252, 776), (-268, 850)]
    out = []
    for (z0, y0), (z1, y1) in zip(linha, linha[1:]):
        dz, dy = z1 - z0, y1 - y0
        l = math.hypot(dz, dy)
        nz, ny = -dy / l * e, dz / l * e                                    # normal para cima/frente
        if ny < 0:
            nz, ny = -nz, -ny
        out.append(perfil([(z0 - nz / 2, y0 - ny / 2), (z1 - nz / 2, y1 - ny / 2), (z1 + nz / 2, y1 + ny / 2), (z0 + nz / 2, y0 + ny / 2)][::-1 if dz * ny - dy * nz < 0 else 1], x - w, x + w, 'assento_azul'))
    return lib.join(out, 'concha')


def banco_espera():
    A = 'aco_banco'
    p = [cil((-950, 300, 0), (950, 300, 0), 26, A, n=16)]
    p.append(_torno([(0, 0), (26, 0), (28, 4), (28, 10), (0, 10)], 'plastico_preto', -950, 300, 0, n=16, eixo=(-1, 0, 0)))
    p.append(_torno([(0, 0), (26, 0), (28, 4), (28, 10), (0, 10)], 'plastico_preto', 950, 300, 0, n=16, eixo=(1, 0, 0)))
    for s in (-1, 1):                                                       # pés em T
        x = s * 750
        p.append(caixa(x - 30, x + 30, 0, 300, -30, 30, A, 6.0))
        p.append(caixa(x - 35, x + 35, 0, 40, -250, 250, A, 8.0))
        for z in (-235, 235):
            p.append(_torno([(0, 0), (22, 0), (22, 8), (0, 8)], 'borracha', x, -1, z, n=12))
        p.append(caixa(x - 34, x + 34, 270, 330, -34, 34, A, 6.0))          # abraçadeira na viga
    for k in range(3):
        x = -600 + k * 600
        p.append(_concha(x))
        p.append(caixa(x - 40, x + 40, 326, 438, -60, 60, A, 4.0))          # suporte da concha
        p.append(caixa(x - 150, x + 150, 430, 440, -120, 140, A, 2.0))
        for dx in (-110, 110):                                              # parafusos
            for dz in (-90, 110):
                p.append(_torno([(0, 0), (7, 0), (6, 2.5), (0, 3)], 'zincado', x + dx, 455, dz, n=8))
        if k < 2:                                                           # braço entre lugares
            xb = x + 300
            p.append(_fio([(xb, 330, -40), (xb, 600, -80), (xb, 620, 120), (xb, 480, 170)], 12, A, res=1))
            p.append(caixa(xb - 22, xb + 22, 604, 630, -100, 130, 'plastico_preto', 8.0))
    p.append(caixa(380, 540, 460.5, 462, -40, 140, 'papel'))                 # senha esquecida no assento
    p.append(_torno([(0, 0), (34, 0), (34, 95), (0, 95)], 'pet', -560, 459, 120, n=12))   # copo descartável caído
    parte('banco', p, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- ESTANTE DE BIBLIOTECA
def _fileira(y, zs, rnd, ocupa):
    """Livros de uma prateleira de um lado (zs = +1 frente, -1 trás), com vãos de saque."""
    liv = []
    x, fim = -440.0, 440.0
    while x < fim - 25:
        if rnd.random() > ocupa:
            if rnd.random() < 0.3 and x + 260 < fim:                         # pilha deitada no vão
                yy = y
                for _ in range(rnd.randint(1, 3)):
                    w, h, d = rnd.uniform(22, 40), rnd.uniform(190, 240), rnd.uniform(150, 200)
                    o = sala._livro(w, h, d, f'capa_{rnd.randint(1, 6)}', rnd)
                    liv.append(sala._por(o, x + 10, yy + w, 290 - rnd.uniform(0, 20), deitado=True))
                    if zs < 0:
                        sala._mover(o, lambda px, py, pz, xm=x + 10 + h / 2: (2 * xm - px, py, -pz))
                    yy += w
                x += 270
            else:
                x += rnd.uniform(90, 200)
            continue
        w, h, d = rnd.uniform(20, 48), rnd.uniform(200, 300), rnd.uniform(160, 230)
        if x + w > fim:
            break
        o = sala._livro(w, h, d, f'capa_{rnd.randint(1, 6)}', rnd)
        sala._por(o, x, y, 288 - rnd.uniform(0, 14))
        if zs < 0:                                                          # do outro lado: lombada para -z
            sala._mover(o, lambda px, py, pz, xm=x + w / 2: (2 * xm - px, py, -pz))
        liv.append(o)
        x += w + rnd.uniform(0.6, 2.0)
    return liv


def estante_biblioteca():
    X, H, Z = 500, 2200, 300
    NIV = [100, 500, 900, 1300, 1700]
    p = []
    for s in (-1, 1):                                                       # laterais de almofada
        xa, xb = sorted((s * X, s * (X - 30)))
        p.append(caixa(xa, xb, 0, H, -Z, Z, N + 'y', 2.0))
        xc, xd = sorted((s * (X + 0.2), s * (X + 3)))
        for zs in (-1, 1):
            za, zb = sorted((zs * 60, zs * (Z - 60)))
            p.append(caixa(xc, xd, 160, H - 160, za, zb, N + 'y', 1.5))     # almofadas em relevo dos dois lados
        for zs in (-1, 1):                                                  # plaqueta de assunto (latão)
            za, zb = sorted((zs * Z, zs * (Z + 2)))
    p.append(caixa(-X - 20, X + 20, H, H + 20, -Z - 20, Z + 20, N + 'x', 3.0))   # cornija
    p.append(caixa(-X - 8, X + 8, H + 20, H + 50, -Z - 8, Z + 8, N + 'x', 6.0))
    p.append(caixa(-X + 30, X - 30, 0, 100, -Z + 20, Z - 20, N + 'x', 2.0))     # rodapé recuado
    p.append(caixa(-X + 30, X - 30, 100, H, -6, 6, N + 'y'))                   # fundo do meio
    for y in NIV + [H - 22]:
        p.append(caixa(-X + 30, X - 30, y - 22, y, -Z + 4, Z - 4, N + 'x', 1.5))
    for zs in (-1, 1):                                                      # placa de classificação de latão no alto
        za, zb = sorted((zs * (Z + 20), zs * (Z + 22)))
        p.append(caixa(-110, 110, H + 24, H + 46, za, zb, 'latao', 0.6))
    p.append(letreiro('HISTÓRIA', 15, 0, H + 29, Z + 22.2, 'tinta_preta'))
    t = letreiro('LITERATURA', 15, 0, H + 29, Z + 22.2, 'tinta_preta')
    sala._mover(t, lambda x, y, z: (-x, y, -z))
    p.append(t)
    parte('estante', p, origem=G(0, 0, 0), grupo='A')
    rnd = random.Random(23)
    liv = []
    for zs in (-1, 1):
        for k, y in enumerate(NIV):
            liv += _fileira(y, zs, rnd, 0.55 if k in (1, 2) else 0.75)
    parte('livros', liv, origem=G(0, 0, 0), grupo='B')


# ---------------------------------------------------------------------------- FRIGOBAR
def frigobar():
    X, Z0, Z1, H = 240, -240, 220, 550
    c = caixa(-X, X, 30, H, Z0, Z1, N + 'y')
    cut(c, caixa(-X + 22, X - 22, 52, H - 22, Z0 + 22, Z1 + 5, N + 'y'))
    p = [bevel(c, 2.0)]
    l = caixa(-X + 22, X - 22, 52, H - 22, Z0 + 22, Z1 - 2, 'liner_branco')    # caixa interna de plástico
    cut(l, caixa(-X + 30, X - 30, 60, H - 30, Z0 + 30, Z1 + 5, 'liner_branco'))
    p.append(bevel(l, 3.0, seg=2))
    p.append(caixa(-X + 30, X - 30, H - 120, H - 30, Z0 + 30, Z0 + 140, 'inox', 2.0))   # evaporador
    p.append(caixa(-X + 10, X - 10, 0, 30, Z0 + 20, Z1 - 30, 'plastico_preto', 3.0))     # base
    for k in range(10):                                                     # grade do compressor atrás
        p.append(cil((-X + 40, 120 + k * 30, Z0 - 6), (X - 40, 120 + k * 30, Z0 - 6), 2.2, 'esmalte_preto', n=6))
    for x in range(-180, 200, 60):
        p.append(cil((x, 110, Z0 - 6), (x, 400, Z0 - 6), 2.2, 'esmalte_preto', n=6))
    p.append(_torno([(0, 0), (60, 0), (60, 90), (0, 90)], 'esmalte_preto', 0, 60, Z0 - 45, n=14, eixo=(0, 0, 1)))   # compressor
    p.append(lib.join([caixa(-X + 32, X - 32, 278, 280, Z0 + 32, Z1 - 30, 'zincado')] +
                           [caixa(-X + 32 + k * 25, -X + 34 + k * 25, 278, 282, Z0 + 32, Z1 - 30, 'zincado') for k in range(17)], 'grade'))   # prateleira de arame
    rnd = random.Random(61)
    for y in (60, 282):
        for i in range(4):
            if rnd.random() < 0.3:
                continue
            x = -150 + i * 95
            if i % 2:
                p.append(_torno([(0, 0), (31, 0), (33, 5), (33, 110), (28, 118), (0, 118)], 'lata', x, y, -60, n=14))
                p.append(_torno([(33.6, 20), (33.6, 95)], 'rotulo_vermelho' if i == 1 else 'rotulo_verde', x, y, -60, n=14))
            else:
                p.append(_torno([(0, 0), (30, 0), (32, 6), (32, 120), (12, 170), (11, 190), (0, 190)], 'vidro_ambar' if i == 2 else 'pet', x, y, -60, n=12))
                p.append(_torno([(0, 0), (13, 0), (13, 14), (0, 14)], 'tampa_azul' if i == 0 else 'latao', x, y + 188, -60, n=10))
    p.append(caixa(-60, 60, 282, 296, 40, 120, 'chocolate', 2.0))
    parte('frigobar', p, origem=G(0, 0, 0), grupo='A')
    d = [bevel(caixa(-X, X, 32, H - 2, Z1, Z1 + 26, N + 'y'), 2.5, seg=2)]
    d.append(caixa(-X + 20, X - 20, 52, H - 22, Z1 - 4, Z1, 'borracha', 2.0))    # gaxeta
    d.append(caixa(-X + 40, X - 40, 70, H - 40, Z1 - 40, Z1 - 4, 'liner_branco', 4.0))   # contraporta
    for y in (140, 330):                                                    # prateleiras da porta com garrafinhas
        d.append(caixa(-X + 40, X - 40, y, y + 50, Z1 - 75, Z1 - 40, 'liner_branco', 2.0))
        for k in range(4):
            if rnd.random() < 0.4:
                continue
            x = -150 + k * 95
            d.append(_torno([(0, 0), (18, 0), (19, 4), (19, 90), (8, 120), (7, 135), (0, 135)], 'vidro_verde' if k % 2 else 'vidro_ambar', x, y + 4, Z1 - 58, n=10))
    d.append(bevel(caixa(X - 62, X - 30, 290, 450, Z1 + 26, Z1 + 42, 'latao'), 4.0, seg=2))   # puxador
    d.append(caixa(-60, 60, H - 70, H - 40, Z1 + 26, Z1 + 27, 'latao'))                       # plaqueta do hotel
    d.append(letreiro('MINIBAR', 12, 0, H - 61, Z1 + 27.2, 'tinta_preta'))
    parte('porta', d, origem=G(-X, 0, Z1 + 12), grupo='B')


FORMAS = {'pallet': pallet, 'banco_espera': banco_espera, 'estante_biblioteca': estante_biblioteca, 'frigobar': frigobar}
