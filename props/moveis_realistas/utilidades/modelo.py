"""Vitrine giratória de tortas, carrinho de assadeiras, bicicleta caída e carrinho de mão no nível realista.

Medidas em mm nas coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente. As medidas de fora são as dos
móveis antigos de props/mobilias (nenhum tem nó que abre). A cúpula e as prateleiras da vitrine são malhas vidro_*,
trocadas pelo vidro transparente no gerar.py. A bicicleta está caída de lado, apoiada no pedal e na ponta do guidão."""
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
_mover, _fofo = sala._mover, sala._fofo


def _anel(prof, mat, x=0, y=0, z=0, n=20, eixo=(0, 1, 0)):
    return lib.lathe([(h, r) for r, h in prof], mat, n=n, c0=G(x, y, z), eixo=G(*eixo), anel=True)


# ---------------------------------------------------------------------------- VITRINE DE TORTAS
def _torta(rnd, x, y, z, R, recheio, fatia):
    p = [_torno([(0, 0), (R - 6, 0), (R, 8), (R + 3, 30), (R - 4, 36), (0, 34)], 'massa_assada', x, y, z, n=24)]
    p.append(_torno([(0, 30), (R - 10, 30), (R - 14, 38), (0, 40)], recheio, x, y, z, n=24))
    if fatia:                                                                 # já cortaram uma fatia
        a = rnd.uniform(0, 2 * math.pi)
        for o in p:
            corte = caixa(0, R + 20, -5, 60, 0, R + 20, recheio)
            _mover(corte, lambda xx, yy, zz: (x + xx * math.cos(a) - zz * math.sin(a), y + yy, z + xx * math.sin(a) + zz * math.cos(a)))
            cut(o, corte)
    for k in range(rnd.randint(1, 3)):                                        # bolor nas tortas esquecidas
        a, r = rnd.uniform(0, 2 * math.pi), rnd.uniform(0, R - 25)
        p.append(_torno([(0, 0), (12 + k * 4, 0), (0, 3)], 'mofo', x + r * math.cos(a), y + 40, z + r * math.sin(a), n=10))
    return p


def vitrine_tortas():
    rnd = random.Random(3)
    p = [_torno([(0, 0), (220, 0), (222, 8), (220, 30), (205, 42), (0, 42)], 'inox', n=40)]          # base
    p.append(_torno([(0, 42), (12, 42), (12, 760), (0, 760)], 'inox', n=12))                          # eixo
    for k, y in enumerate((80, 320, 560)):
        p.append(_torno([(0, y - 6), (26, y - 6), (26, y + 2), (0, y + 2)], 'inox', n=14))           # suporte da prateleira
        tortas = [(90, 0.5), (90, 0.5 + math.pi)] if k < 2 else [(0, 0)]
        for j, (r, a) in enumerate(tortas):
            R = 95 if k < 2 else 120
            p += _torta(rnd, r * math.cos(a + k), y + 8, r * math.sin(a + k), R,
                        ('recheio_morango', 'recheio_creme', 'recheio_morango')[k], j == 0 and k != 1)
    p.append(_torno([(0, 790), (40, 790), (40, 800), (14, 820), (14, 860), (22, 870), (12, 880), (0, 880)], 'inox', n=16))   # pegador da cúpula
    parte('vitrine', p, origem=G(0, 0, 0), grupo='A')
    parte('vidro_cupula', [_anel([(203, 42), (207, 42), (207, 720), (200, 760), (160, 785), (40, 795), (40, 790),
                                  (158, 781), (197, 756), (203, 720)], 'vidro_visor', n=40)], origem=G(0, 0, 0), grupo='B')
    parte('vidro_prateleiras', [_torno([(0, y), (190, y), (190, y + 6), (0, y + 6)], 'vidro_visor', n=36) for y in (80, 320, 560)],
          origem=G(0, 0, 0), grupo='B')


# ---------------------------------------------------------------------------- CARRINHO DE ASSADEIRAS
def _rodizio(x, z, r=45):
    return [caixa(x - 28, x + 28, 92, 100, z - 28, z + 28, 'inox', 2.0),
            caixa(x - 18, x + 18, r - 4, 92, z - r * 0.5, z + 8, 'inox', 2.0),
            _torno([(0, -12), (r - 8, -12), (r, -5), (r, 5), (r - 8, 12), (0, 12)], 'borracha', x, r, z - r * 0.3, n=16, eixo=(1, 0, 0))]


def _pao(x, y, z, mat, giro):
    o = _torno([(0, 0), (30, 0), (38, 12), (36, 28), (24, 40), (0, 44)], mat, 0, 0, 0, n=10)
    c, s = math.cos(giro), math.sin(giro)
    _mover(o, lambda a, b, cc: (x + a * c - cc * 1.6 * s, y + b, z + a * s + cc * 1.6 * c))     # pão alongado
    return o


def carrinho_assadeiras():
    X, Z, H = 255, 365, 1720
    rnd = random.Random(47)
    p = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            x, z = sx * X, sz * Z
            p.append(caixa(x - 13, x + 13, 100, H, z - 13, z + 13, 'inox', 2.0))           # montantes
            p += _rodizio(x, z)
        for k in range(12):                                                       # cantoneiras das bandejas
            y = 200 + k * 120
            xa, xb = sorted((sx * (X - 13), sx * (X - 35)))
            p.append(caixa(xa, xb, y, y + 3, -Z + 13, Z - 13, 'inox'))
            xa, xb = sorted((sx * (X - 13), sx * (X - 16)))
            p.append(caixa(xa, xb, y, y + 22, -Z + 13, Z - 13, 'inox'))
    for y in (100, H - 25):                                                       # quadros de cima e de baixo
        for sz in (-1, 1):
            p.append(caixa(-X + 13, X - 13, y, y + 25, sz * Z - 12, sz * Z + 12, 'inox', 2.0))
    for k in range(12):                                                           # assadeiras, algumas tiradas
        if rnd.random() < 0.4:
            continue
        y = 203 + k * 120
        za = rnd.uniform(-40, 30) if rnd.random() < 0.3 else 0.0                # uma ou outra puxada para fora
        b = caixa(-X + 37, X - 37, y, y + 22, -Z + 20 + za, Z - 20 + za, 'assadeira', 3.0)
        cut(b, caixa(-X + 43, X - 43, y + 2, y + 30, -Z + 26 + za, Z - 26 + za, 'assadeira'))
        p.append(b)
        for i in range(3):
            for j in range(5):
                if rnd.random() < 0.3:
                    continue
                mat = 'mofo' if rnd.random() < 0.12 else rnd.choice(('massa_assada', 'massa_clara'))
                p.append(_pao(-140 + i * 140 + rnd.uniform(-8, 8), y + 2, -270 + j * 135 + za + rnd.uniform(-8, 8), mat, math.pi / 2 + rnd.uniform(-0.2, 0.2)))
    parte('carrinho', p, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- BICICLETA CAÍDA
def _roda_bici(z, R=330):
    p = [_anel([(R - 26, -16), (R - 8, -19), (R, -10), (R, 10), (R - 8, 19), (R - 26, 16)], 'borracha', 0, R, z, n=40, eixo=(1, 0, 0))]
    p.append(_anel([(R - 44, -10), (R - 26, -11), (R - 26, 11), (R - 44, 10)], 'cromo', 0, R, z, n=40, eixo=(1, 0, 0)))
    p.append(_torno([(0, -50), (16, -50), (16, -30), (22, -28), (22, 28), (16, 30), (16, 50), (0, 50)], 'cromo', 0, R, z, n=12, eixo=(1, 0, 0)))
    for k in range(20):                                                       # raios
        a = 2 * math.pi * k / 20
        dx = 24 if k % 2 else -24
        p.append(cil((dx, R + 20 * math.sin(a), z + 20 * math.cos(a)), (0, R + (R - 44) * math.sin(a + 0.25), z + (R - 44) * math.cos(a + 0.25)), 1.3, 'inox', n=3))
    return p


def bicicleta():
    Q = 'quadro_bici'
    p = _roda_bici(-520) + _roda_bici(520)
    A, B, C, D, E = (0, 330, -520), (0, 300, -60), (0, 850, -140), (0, 860, 360), (0, 330, 520)
    for a, b, r in ((B, C, 16), (C, D, 15), (B, D, 19)):                       # quadro
        p.append(cil(a, b, r, Q, n=12))
    for s in (-1, 1):
        p.append(cil((s * 45, A[1], A[2]), (s * 18, B[1], B[2]), 10, Q, n=10))     # garfo traseiro de baixo
        p.append(cil((s * 45, A[1], A[2]), (s * 14, C[1] - 30, C[2] - 10), 9, Q, n=10))   # de cima
        p.append(cil((s * 45, E[1], E[2]), (s * 28, 820, 375), 11, 'cromo', n=10))     # garfo da frente
    p.append(cil((0, 810, 372), (0, 920, 348), 18, Q, n=12))                    # caixa de direção
    p.append(cil((0, 920, 348), (0, 1000, 330), 13, 'cromo', n=10))             # avanço
    p.append(cil((-290, 1000, 320), (290, 1000, 320), 12, 'cromo', n=10))      # guidão
    for s in (-1, 1):
        xa, xb = sorted((s * 190, s * 300))
        p.append(cil((xa, 1000, 320), (xb, 1000, 320), 17, 'borracha', n=10))   # manoplas
    p.append(cil((0, 850, -140), (0, 960, -165), 12, 'cromo', n=10))           # canote
    p.append(_fofo(-75, 75, 955, 1005, -280, -40, 'banco_bici', r=22.0, bojo=6.0, cortes=5))     # selim
    p.append(_torno([(0, -25), (30, -25), (30, 25), (0, 25)], 'cromo', 0, 300, -60, n=14, eixo=(1, 0, 0)))   # movimento central
    p.append(_anel([(80, -3), (95, -3), (95, 3), (80, 3)], 'aco_polido', 50, 300, -60, n=32, eixo=(1, 0, 0)))   # coroa
    p.append(_anel([(28, -3), (36, -3), (36, 3), (28, 3)], 'aco_polido', 50, 330, -520, n=16, eixo=(1, 0, 0)))  # catraca
    for y, zz in ((395, -60), (205, -60)):
        p.append(_fio([(50, y, zz), (50, 330 + (y - 300) * 0.36, -520)], 3.0, 'ferrugem', fechado=False, res=1))   # corrente
    for s, sy in ((1, 1), (-1, -1)):                                           # pedivelas em pé: o pedal de baixo segura a bicicleta
        x = s * 70
        top = (x, 300 + sy * 170, -60)
        p.append(cil((x, 300, -60), top, 9, 'cromo', n=8))
        xa, xb = sorted((x, x + s * 95))
        p.append(caixa(xa, xb, top[1] - 12, top[1] + 12, -100, -20, 'plastico_preto', 3.0))
    p.append(cil((-40, 290, -150), (-60, 30, -320), 7, 'cromo', n=8))          # descanso recolhido
    # deita de lado (75 graus em volta de z), apoiada no pedal e na ponta do guidão
    f = math.radians(75)
    c, s = math.cos(f), math.sin(f)
    for o in p:
        _mover(o, lambda x, y, z: (40 + x * c + y * s, -x * s + y * c, z))
    chao = min(sala._xyz(v)[1] for o in p for v in o.data.vertices)          # encosta o ponto mais baixo no chão
    for o in p:
        _mover(o, lambda x, y, z: (x, y - chao, z))
    parte('bicicleta', p, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- CARRINHO DE MÃO
def _abrir(o, y0, y1, kx, kz, dx=0.0):
    """Abre a caixa para cima como uma caçamba: em y1 fica kx vezes mais larga em x e kz em z."""
    _mover(o, lambda x, y, z: (dx + x * (1 + (kx - 1) * (y - y0) / (y1 - y0)) + 60 * (y - y0) / (y1 - y0),
                               y, z * (1 + (kz - 1) * (y - y0) / (y1 - y0))))
    return o


def carrinho_mao():
    V = 'cacamba_verde'
    rnd = random.Random(8)
    Y0, Y1 = 380, 660
    c = _abrir(caixa(-320, 320, Y0, Y1, -210, 210, V, 6.0), Y0, Y1, 1.33, 1.45, 30)
    dentro = _abrir(caixa(-314, 314, Y0 + 5, Y1 + 40, -204, 204, V), Y0 + 5, Y1 + 40, 1.37, 1.5, 30)
    cut(c, dentro)
    p = [c]
    p.append(_abrir(caixa(-330, 330, Y1 - 4, Y1 + 10, -216, 216, V, 3.0), Y0, Y1, 1.33, 1.45, 30))   # beirada dobrada
    cut(p[-1], _abrir(caixa(-318, 318, Y1 - 10, Y1 + 20, -206, 206, V), Y0, Y1, 1.33, 1.45, 30))
    p.append(_fofo(-260, 300, Y0 + 5, Y0 + 130, -170, 170, 'areia', r=60.0, bojo=40.0, cortes=7, semente=4.0))   # resto de areia
    for k in range(3):                                                         # tijolos quebrados por cima
        x, z, a = rnd.uniform(-180, 150), rnd.uniform(-90, 90), rnd.uniform(0, 3)
        t = caixa(-95, 95 - k * 30, 0, 55, -45, 45, 'tijolo', 4.0)
        _mover(t, lambda xx, yy, zz: (x + xx * math.cos(a) - zz * math.sin(a), Y0 + 120 + yy + k * 20, z + xx * math.sin(a) + zz * math.cos(a)))
        p.append(t)
    for s in (-1, 1):                                                          # braços de tubo, do eixo da roda até as manoplas
        p.append(cil((640, 200, s * 70), (380, 360, s * 190), 15, 'ferro_preto', n=10))
        p.append(cil((380, 360, s * 190), (-820, 600, s * 265), 15, 'ferro_preto', n=10))
        p.append(cil((-640, 564, s * 255), (-858, 607, s * 268), 19, 'cabo_madeira_x', n=10))    # cabo de madeira
        p.append(cil((-300, 470, s * 240), (-360, 0, s * 240), 13, 'ferro_preto', n=10))         # perna
        p.append(caixa(-400, -320, 0, 14, s * 240 - 25, s * 240 + 25, 'ferro_preto', 2.0))      # sapata
        p.append(cil((-330, 300, s * 240), (-20, 420, s * 215), 9, 'ferro_preto', n=8))         # mão-francesa
    p.append(cil((-300, 470, -240), (-300, 470, 240), 11, 'ferro_preto', n=8))                  # travessa
    p.append(cil((250, 390, -170), (250, 390, 170), 11, 'ferro_preto', n=8))
    # roda de pneu com aro de chapa
    p.append(_anel([(150, -40), (175, -45), (195, -30), (198, 0), (195, 30), (175, 45), (150, 40)], 'borracha', 640, 200, 0, n=36, eixo=(0, 0, 1)))
    p.append(_torno([(0, -35), (150, -35), (150, 35), (0, 35)], 'cacamba_verde', 640, 200, 0, n=28, eixo=(0, 0, 1)))
    p.append(cil((640, 200, -75), (640, 200, 75), 12, 'ferrugem', n=10))
    parte('carrinho', p, origem=G(0, 0, 0), grupo='A')


FORMAS = {'vitrine_tortas': vitrine_tortas, 'carrinho_assadeiras': carrinho_assadeiras, 'bicicleta': bicicleta, 'carrinho_mao': carrinho_mao}
