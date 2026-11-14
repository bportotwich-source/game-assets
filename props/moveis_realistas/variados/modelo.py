"""Carrinho de emergência, estante porta-pallet, prateleira de pães e beliche de abrigo no nível realista.

Medidas em mm nas coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente. As medidas de fora e o nó que
abre (gaveta_1 do carrinho) são os dos móveis antigos de props/mobilias. O porta-pallet usa o pallet realista de servicos/."""
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
serv = _carregar('modelo_servicos', 'servicos')


def _rodizio(x, z, r=50, alt=110):
    return [caixa(x - 24, x + 24, alt - 8, alt, z - 24, z + 24, 'zincado', 2.0),
            caixa(x - 16, x + 16, r - 6, alt - 8, z - r * 0.6 - 4, z + 6, 'zincado', 1.5),
            _torno([(0, -12), (r - 8, -12), (r, -5), (r, 5), (r - 8, 12), (0, 12)], 'borracha', x, r, z - r * 0.4, n=16, eixo=(1, 0, 0))]


# ---------------------------------------------------------------------------- CARRINHO DE EMERGÊNCIA
def carrinho_emergencia():
    X, Z0, Z1, YB, YT = 330, -270, 270, 130, 1000
    V = 'vermelho_carro'
    c = caixa(-X, X, YB, YT, Z0, Z1, V, 6.0)
    VAOS = [(YT - 150, YT - 30), (YT - 290, YT - 170), (YT - 430, YT - 310), (YT - 600, YT - 450), (YB + 30, YT - 620)]
    for y0, y1 in VAOS:
        cut(c, caixa(-X + 30, X - 30, y0, y1, Z0 + 30, Z1 + 5, V))
    p = [c]
    for i, (y0, y1) in enumerate(VAOS[1:]):                                  # gavetas fixas (só a frente)
        p.append(caixa(-X + 32, X - 32, y0 + 2, y1 - 2, Z1 - 20, Z1 + 4, V, 5.0))
        p.append(caixa(-150, 150, y1 - 40, y1 - 20, Z1 + 4, Z1 + 26, 'plastico_cinza', 6.0))       # puxador de alça embutido
        p.append(caixa(-60, 60, (y0 + y1) / 2 - 18, (y0 + y1) / 2 + 2, Z1 + 4.2, Z1 + 5, 'luminoso'))   # etiqueta
    p.append(caixa(-X - 10, X + 10, YT, YT + 20, Z0 - 10, Z1 + 10, 'plastico_cinza', 6.0))   # tampo com borda
    p.append(caixa(-X - 10, X + 10, YT + 20, YT + 50, Z1 - 10, Z1 + 10, 'plastico_cinza', 5.0))    # beirais do tampo
    p.append(caixa(-X - 10, X + 10, YT + 20, YT + 50, Z0 - 10, Z0 + 10, 'plastico_cinza', 5.0))
    for z in (Z0 + 60, Z1 - 60):                                             # alça lateral
        p.append(cil((X, 900, z), (X + 80, 900, z), 12, 'cromo', n=8))
    p.append(cil((X + 80, 900, Z0 + 60), (X + 80, 900, Z1 - 60), 14, 'cromo', n=10))
    p.append(cil((-X - 60, 300, -60), (-X - 60, 900, -60), 70, 'aco_verde', n=16))    # cilindro de oxigênio
    p.append(_torno([(0, 0), (70, 0), (70, 20), (40, 60), (20, 70), (20, 110), (0, 110)], 'aco_verde', -X - 60, 900, -60, n=16))
    p.append(_torno([(0, 0), (22, 0), (22, 30), (0, 30)], 'latao', -X - 60, 1010, -60, n=10))
    for y in (380, 820):
        p.append(cil((-X - 60, y, -130), (-X, y, -130), 6, 'cromo', n=6))
        p.append(_anel_cinta(-X - 60, y, -60, 74))
    # desfibrilador e caixa de luvas no tampo
    p.append(caixa(-250, 50, YT + 20, YT + 150, -180, 80, 'plastico_amarelo', 14.0))
    p.append(caixa(-230, -60, YT + 120, YT + 151, -150, 40, 'vidro_escuro', 4.0))
    for k in range(2):
        p.append(_torno([(0, 0), (35, 0), (35, 60), (25, 70), (0, 70)], 'plastico_cinza', -200 + k * 100, YT + 150, 50, n=12, eixo=(0, 1, 0)))
    p.append(_fio([(-200, YT + 220, 50), (-150, YT + 260, 0), (-100, YT + 220, 50)], 4, 'plastico_preto', res=2))
    p.append(caixa(120, 300, YT + 20, YT + 95, -100, 30, 'liner_branco', 3.0))
    p.append(caixa(150, 270, YT + 95, YT + 96, -70, 0, 'pano_azul'))
    for x, z in ((-X + 50, Z0 + 50), (X - 50, Z0 + 50), (-X + 50, Z1 - 50), (X - 50, Z1 - 50)):
        p += _rodizio(x, z, r=55, alt=YB)
    parte('carrinho', p, origem=G(0, 0, 0), grupo='A')
    y0, y1 = VAOS[0]
    g = [caixa(-X + 32, X - 32, y0 + 2, y1 - 2, Z1 - 20, Z1 + 4, V, 5.0)]
    g.append(caixa(-150, 150, y1 - 40, y1 - 20, Z1 + 4, Z1 + 26, 'plastico_cinza', 6.0))
    g.append(caixa(-X + 40, X - 40, y0 + 4, y0 + 10, Z0 + 40, Z1 - 20, 'liner_branco'))
    for k in range(5):                                                       # ampolas e seringas
        g.append(_torno([(0, 0), (8, 0), (8, 40), (4, 50), (0, 52)], 'vidro_soro', -200 + k * 30, y0 + 10, -100, n=8))
    g.append(caixa(0, 160, y0 + 10, y0 + 40, -150, 40, 'caixa_azul', 2.0))
    parte('gaveta_1', g, origem=G(0, 0, 0), grupo='B')


def _anel_cinta(x, y, z, r):
    return lib.lathe([(-8, r), (8, r), (8, r + 4), (-8, r + 4)], 'cromo', n=16, c0=G(x, y, z), eixo=G(0, 1, 0), anel=True)


# ---------------------------------------------------------------------------- PORTA-PALLET
def _pallet():
    """O pallet realista de servicos/ (1200 x 800), devolvido como lista de objetos."""
    pecas = []
    orig = serv.parte
    serv.parte = lambda nome, objs, **k: pecas.append(list(objs))
    try:
        serv.pallet()
    finally:
        serv.parte = orig
    return lib.join(pecas[0], 'pallet')


def _carga(rnd, x, y, z):
    """Caixas de papelão empilhadas no pallet, enroladas em filme."""
    p = []
    for cam in range(rnd.randint(2, 4)):
        for i in range(2):
            for j in range(3):
                if cam == 3 and rnd.random() < 0.5:
                    continue
                w, d, h = 380, 360, 260
                xx, zz = x - 400 + i * 400 + rnd.uniform(-6, 6), z - 560 + j * 380 + rnd.uniform(-6, 6)
                p.append(caixa(xx, xx + w, y + cam * h, y + cam * h + h - 2, zz, zz + d, 'papelao', 4.0))
                p.append(caixa(xx + 100, xx + w - 100, y + cam * h + h - 2, y + cam * h + h - 1.4, zz - 0.5, zz + d + 0.5, 'fita_crepe'))
    return p


def porta_pallet():
    X, Z0, Z1 = 1350, -600, 600
    rnd = random.Random(31)
    p = []
    for x in (-X, 0, X):                                                      # colunas (quadros) com furação
        for z in (Z0, Z1):
            col = caixa(x - 45, x + 45, 0, 3600, z - 35, z + 35, 'coluna_azul', 2.0)
            p.append(col)
            p.append(caixa(x - 60, x + 60, 0, 8, z - 60, z + 60, 'zincado', 1.0))       # sapata
            zf = z + 35.3 if z > 0 else z - 35.3
            for k in range(40):
                y = 200 + k * 85
                a, b = sorted((zf, zf + (0.4 if z > 0 else -0.4)))
                p.append(caixa(x - 14, x + 14, y, y + 40, a, b, 'furo'))
        for k in range(8):                                                    # travamento do quadro
            y0, y1 = 100 + k * 430, 100 + (k + 1) * 430
            p.append(cil((x, y0, Z0 + 35), (x, y1, Z1 - 35), 12, 'coluna_azul', n=6))
        for y in (100, 3550):
            p.append(cil((x, y, Z0 + 35), (x, y, Z1 - 35), 14, 'coluna_azul', n=6))
    NIV = [1650, 3200]
    for y in NIV:                                                             # longarinas
        for xa, xb in ((-X + 45, -45), (45, X - 45)):
            for z in (Z0, Z1):
                p.append(caixa(xa, xb, y - 120, y, z - 25, z + 25, 'longarina', 3.0))
            for k in range(3):                                                # travessas de apoio
                xx = xa + 150 + k * (xb - xa - 300) / 2
                p.append(caixa(xx - 25, xx + 25, y - 30, y, Z0 + 25, Z1 - 25, 'zincado', 1.5))
    # pallets: dois no chão, um em cima à esquerda, um vazio à direita
    lugares = [(-X / 2, 0, True), (X / 2, 0, True), (-X / 2, NIV[0], True), (X / 2, NIV[0], False), (-X / 2, NIV[1], False)]
    for x, y, carga in lugares:
        o = _pallet()
        _mover(o, lambda a, b, c: (x + c, y + b, -a))                     # gira 90°: 800 de frente, 1200 de fundo
        p.append(o)
        if carga:
            p += _carga(rnd, x, y + 145, 0)
    p.append(caixa(-300, 300, NIV[0] - 110, NIV[0] - 10, Z1 + 25, Z1 + 26, 'etiqueta_amarela'))   # placa de carga
    p.append(letreiro('CARGA MÁX 1000 kg', 34, 0, NIV[0] - 75, Z1 + 26.2, 'tinta_preta'))
    parte('porta_pallet', p, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- PRATELEIRA DE PÃES
def _pao(rnd, x, y, z, tipo):
    if tipo == 0:                                                             # bisnaga
        o = _torno([(0, -1), (26, -1)] + [(32 * math.sin(math.pi * t / 10) ** 0.5, 150 * (t / 10 - 0.5) * 2) for t in range(1, 10)] + [(0, 151)], 'pao', 0, 0, 0, n=10)
        _mover(o, lambda a, b, c: (x + b * 0.9, y + 30 + c * 0.8, z + a))
        return [o]
    if tipo == 1:                                                             # pão francês
        o = _torno([(0, -60), (22, -55), (34, -30), (36, 0), (34, 30), (22, 55), (0, 60)], 'pao_claro', 0, 0, 0, n=10)
        _mover(o, lambda a, b, c: (x + b, y + 26 + c * 0.75, z + a * 1.1))
        return [o, caixa(x - 40, x + 30, y + 52, y + 54, z - 4, z + 4, 'pao_claro', 1.0)]
    o = _torno([(0, 0), (90, 0), (100, 30), (95, 70), (60, 95), (0, 102)], 'pao', 0, 0, 0, n=16)   # pão redondo
    _mover(o, lambda a, b, c: (x + a, y + b, z + c))
    return [o]


def prateleira_padaria():
    X, Z0, Z1, H = 600, -250, 250, 1630
    N = 'nogueira_'
    p = []
    for s in (-1, 1):                                                         # laterais recortadas em degraus
        pts = [(Z0, 0), (Z1, 0), (Z1, 300), (Z1 - 100, 600), (Z1 - 200, 900), (Z1 - 300, 1200), (Z0 + 120, 1500), (Z0 + 120, H), (Z0, H)]
        xa, xb = sorted((s * X, s * (X - 22)))
        p.append(perfil(pts, xa, xb, N + 'y', 3.0))
    p.append(caixa(-X + 22, X - 22, 0, H, Z0, Z0 + 15, N + 'y'))             # fundo
    p.append(caixa(-X + 22, X - 22, 0, 80, Z1 - 30, Z1 - 10, N + 'x', 2.0))   # rodapé
    p.append(caixa(-X, X, H - 60, H, Z0, Z0 + 140, N + 'x', 3.0))              # chapéu
    p.append(letreiro('PÃES', 40, 0, H - 48, Z0 + 140.5, 'luminoso'))
    rnd = random.Random(17)
    prats = [(80, Z1 - 30), (380, Z1 - 120), (680, Z1 - 220), (980, Z1 - 320)]
    for i, (y, zf) in enumerate(prats):                                       # prateleiras inclinadas com beiral
        incl = math.radians(12)
        d = zf - (Z0 + 15)
        tab = caixa(-X + 22, X - 22, -18, 0, 0, d, N + 'x', 2.0)
        _mover(tab, lambda a, b, c: (a, y + 220 + b - c * math.tan(incl), Z0 + 15 + c))
        p.append(tab)
        p.append(caixa(-X + 22, X - 22, y + 220 - d * math.tan(incl), y + 260 - d * math.tan(incl), zf - 15, zf, N + 'x', 2.0))   # beiral
        tipo = i % 3
        for k in range(18 if tipo == 1 else 9):
            if rnd.random() < 0.3:
                continue
            x = -X + 70 + (k + 0.5) * (2 * X - 140) / (18 if tipo == 1 else 9)
            zz = zf - 70 - rnd.uniform(0, 40) if tipo != 0 else (Z0 + zf) / 2 + 30
            yy = y + 220 - (zz - Z0 - 15) * math.tan(incl)
            p += _pao(rnd, x, yy, zz, tipo)
    parte('prateleira', p, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- BELICHE
def _estrado(y, Xi, Zi, A):
    p = [caixa(-Xi, Xi, y - 40, y, -Zi - 20, -Zi + 20, A, 2.0), caixa(-Xi, Xi, y - 40, y, Zi - 20, Zi + 20, A, 2.0)]
    for s in (-1, 1):
        p.append(caixa(s * Xi - 20, s * Xi + 20, y - 40, y, -Zi, Zi, A, 2.0))
    for k in range(9):                                                        # molas de fita
        z = -Zi + 80 + k * (2 * Zi - 160) / 8
        p.append(caixa(-Xi + 20, Xi - 20, y - 22, y - 18, z - 25, z + 25, 'zincado'))
    return p


def _colchao(y, Xi, Zi, rnd, coberto):
    p = [caixa(-Xi + 8, Xi - 8, y, y + 120, -Zi + 8, Zi - 8, 'colchao', 30.0)]
    t = q._travesseiro(0, 0, 0, 260, 160, 55)
    for o in (t if isinstance(t, list) else [t]):
        _mover(o, lambda a, b, c: (a, y + 120 + b, Zi - 220 + c))
        p.append(o)
    if coberto:                                                               # cobertor dobrado no pé
        p.append(caixa(-Xi + 30, Xi - 30, y + 120, y + 170, -Zi + 40, -Zi + 380, 'cobertor', 20.0))
    else:                                                                     # cobertor jogado, caindo de um lado
        c = caixa(-Xi - 40, Xi - 60, y + 120, y + 135, -Zi + 200, Zi - 400, 'cobertor', 6.0)
        p.append(c)
        p.append(caixa(-Xi - 52, -Xi - 40, y - 200, y + 125, -Zi + 200, Zi - 400, 'cobertor', 4.0))
    return p


def beliche():
    Xi, Zi, A = 440, 980, 'aco_beliche'
    rnd = random.Random(41)
    p = []
    for sx in (-1, 1):                                                        # quatro pés de tubo quadrado
        for sz in (-1, 1):
            x, z = sx * (Xi + 25), sz * (Zi + 25)
            p.append(caixa(x - 25, x + 25, 0, 1750, z - 25, z + 25, A, 3.0))
            p.append(caixa(x - 27, x + 27, 0, 15, z - 27, z + 27, 'borracha', 2.0))
            p.append(caixa(x - 25.5, x + 25.5, 1735, 1750, z - 25.5, z + 25.5, 'plastico_preto', 3.0))
    for sz in (-1, 1):                                                        # cabeceiras e pés de grade
        z = sz * (Zi + 25)
        for y in (520, 800, 1450, 1700):
            p.append(cil((-Xi, y, z), (Xi, y, z), 14, A, n=8))
        for k in range(1, 6):
            x = -Xi + k * 2 * Xi / 6
            p.append(cil((x, 520, z), (x, 800, z), 8, A, n=6))
            p.append(cil((x, 1450, z), (x, 1700, z), 8, A, n=6))
    p += _estrado(320, Xi, Zi, A) + _estrado(1250, Xi, Zi, A)
    for sx in (-1, 1):                                                        # grade de proteção em cima
        x = sx * (Xi + 25)
        p.append(cil((x, 1500, -Zi), (x, 1500, Zi * (0.2 if sx > 0 else 1)), 12, A, n=8))
    xl = Xi + 25                                                              # escada no lado direito, à frente
    for z in (Zi - 380, Zi - 30):
        p.append(cil((xl + 40, 0, z), (xl + 40, 1500, z), 13, A, n=8))
    for k in range(5):
        y = 250 + k * 270
        p.append(cil((xl + 40, y, Zi - 380), (xl + 40, y, Zi - 30), 11, A, n=8))
    p += _colchao(320, Xi, Zi, rnd, True) + _colchao(1250, Xi, Zi, rnd, False)
    p.append(caixa(-200, 200, 0, 280, -Zi + 100, -Zi + 600, 'mala_azul', 20.0))   # mochila/mala embaixo
    parte('beliche', p, origem=G(0, 0, 0), grupo='A')


FORMAS = {'carrinho_emergencia': carrinho_emergencia, 'porta_pallet': porta_pallet, 'prateleira_padaria': prateleira_padaria, 'beliche': beliche}
