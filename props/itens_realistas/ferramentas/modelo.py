"""Ferramentas e materiais de craft no nível realista: martelo de unha, machado, serrote, tábua e
caixa de pregos, cano, chapa, sucata, pá, enxada, faca de cozinha e facão. Desenho próprio, sem marcas.

Coordenadas do jogo em mm (base.py dos móveis): x = comprimento (cabeça da ferramenta em +x),
y = para cima, z = frente. Cada item deitado no chão como o antigo, com o mesmo tamanho e a mesma
pega (o cabo passa por z = 0), para a mão e os golpes do jogo continuarem valendo.
"""
import math, random
import bmesh
from mathutils import Matrix, Vector
import lib
from lib import cut, bevel, parte, pintar, MM
from base import G, caixa, cil, planta, perfil, frente, letreiro


def _torno_x(prof, mat, x0, y, z=0, n=20, achata=1.0):
    """Perfil [(distância ao longo de x, raio)] girado em volta do eixo x; achata < 1 deixa oval (mais fino em y)."""
    o = lib.lathe(prof, mat, n=n, c0=G(x0, y, z), eixo=G(1, 0, 0))
    if achata != 1.0:
        c = lib.P(*G(0, y, 0))
        o.data.transform(Matrix.Translation(c) @ Matrix.Diagonal((1, 1, achata, 1)) @ Matrix.Translation(-c))
    return o


def _torno_z(prof, mat, x, y, z0, n=24, sentido=1):
    """Perfil [(distância ao longo de z, raio)] girado em volta do eixo z, a partir de z0."""
    return lib.lathe(prof, mat, n=n, c0=G(x, y, z0), eixo=G(0, 0, sentido))


def _mexer(o, f):
    """Move cada vértice: f(x, y, z) em mm do jogo -> (x, y, z)."""
    for v in o.data.vertices:
        x, y, z = v.co.x / MM, v.co.z / MM, -v.co.y / MM
        x, y, z = f(x, y, z)
        v.co = lib.P(*G(x, y, z))
    return o


def _fatias(secoes, mat):
    """Peça feita de fatias ao longo de z: [(z, x0, x1, y0, y1)] (retângulos ligados)."""
    aneis = [[lib.P(*G(x, y, z)) for (x, y) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))] for (z, x0, x1, y0, y1) in secoes]
    return lib.loft(aneis, mat)


def _curva(pts, n=2):
    """Arredonda um contorno fechado (corta os cantos n vezes)."""
    for _ in range(n):
        q = []
        for (x0, z0), (x1, z1) in zip(pts, pts[1:] + pts[:1]):
            q += [(0.75 * x0 + 0.25 * x1, 0.75 * z0 + 0.25 * z1), (0.25 * x0 + 0.75 * x1, 0.25 * z0 + 0.75 * z1)]
        pts = q
    return pts


# ------------------------------------------------------------------ martelo de unha
def martelo():
    Y = 16.0
    cabo = _torno_x([(0, 0), (0, 13.5), (3, 16), (28, 16.5), (75, 15), (130, 13), (200, 12), (245, 12.5), (262, 13), (296, 13), (296, 0)],
                    'faia_x', -156, Y, n=20, achata=0.80)
    X0, X1 = 104.0, 132.0
    cab = [bevel(caixa(X0, X1, Y - 13.5, Y + 13.5, -27, 21, 'aco_ferramenta'), 2.5, 2)]
    cab.append(_torno_z([(0, 0), (0, 11.8), (6, 10.6), (20, 10.6), (23.5, 14.6), (37, 14.6), (39, 13.2), (39.4, 0)], 'aco_ferramenta', (X0 + X1) / 2, Y, 20))
    # unha: vista de cima é uma cunha curva que vai afinando; uma fenda em V separa as duas pontas
    fora = [(X1, -25), (X1 - 1, -45), (X1 - 6, -66), (X1 - 15, -85), (X1 - 27, -100)]
    dentro = [(X1 - 29.5, -99), (X1 - 22, -84), (X1 - 20, -66), (X1 - 23, -45), (X0, -25)]
    unha = bevel(planta(fora + dentro, Y - 13, Y + 13, 'aco_ferramenta'), 1.2, 2)
    cut(unha, [perfil([(-104, Y - 5.5), (-104, Y + 5.5), (-52, Y)], X0 - 40, X1 + 10, 'aco_ferramenta')])
    cab.append(unha)
    cab.append(caixa(X1 - 0.3, X1 + 0.9, Y - 2.2, Y + 2.2, -9, 9, 'aco_lamina'))                 # cunha que trava o cabo no olho
    j = lib.join(cab, 'cab')
    pintar(j, 'aco_lamina', lambda c, n: -c[0] > 59.0)                                           # face de bater, polida de uso
    raiz = parte('cabo', [cabo], origem=G(0, 0, 0), grupo='A')
    parte('cabeca', [j], origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


# ------------------------------------------------------------------ machado
def machado():
    Y = 19.0
    cabo = _torno_x([(0, 0), (0, 18), (4, 21), (40, 21.5), (95, 18.5), (200, 16.5), (450, 17), (600, 18), (665, 19), (737, 19), (737, 0)],
                    'faia_x', -365, Y, n=20, achata=0.66)
    _mexer(cabo, lambda x, y, z: (x, y, z - 11.0 * ((-290 - x) / 75) ** 2) if x < -290 else (x, y, z))   # pé do cabo virado para o lado do fio
    # cabeça em fatias ao longo de z: da nuca (z -58) ao fio (z 131), afinando em y e abrindo em x
    sec = [(-58, 323, 369, Y - 15, Y + 15), (-52, 321, 371, Y - 17, Y + 17), (-28, 320, 372, Y - 18, Y + 18), (12, 320, 371, Y - 18, Y + 18),
           (40, 316, 373, Y - 13.5, Y + 13.5), (70, 308, 377, Y - 8.5, Y + 8.5), (100, 298, 383, Y - 4.2, Y + 4.2),
           (120, 292, 386, Y - 1.6, Y + 1.6), (131, 290, 387, Y - 0.15, Y + 0.15)]
    cab = bevel(_fatias(sec, 'ferro_preto'), 1.6, 2)
    pintar(cab, 'aco_lamina', lambda c, n: -c[0] > 108.0)                                        # fio amolado
    olho = caixa(371.5, 373.0, Y - 3, Y + 3, -20, 16, 'aco_lamina')                              # cunha de aço no topo do cabo
    raiz = parte('cabo', [cabo], origem=G(0, 0, 0), grupo='A')
    parte('cabeca', [cab, olho], origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


# ------------------------------------------------------------------ serrote
def serrote():
    Y = 11.5
    dentes = []
    x = -232.0
    while x < 334:
        dentes += [(x, -62.0), (x + 1.2, -65.5)]
        x += 4.6
    lam = planta(dentes + [(337, -62), (340, -22), (-232, 58)], Y - 0.55, Y + 0.55, 'aco_lamina')
    # cabo fechado de serrote de carpinteiro: chifres em cima e embaixo, frente inclinada sobre a lâmina
    fora = [(-340, -30), (-334, -66), (-300, -80), (-262, -70), (-236, -74), (-200, -64), (-178, -30), (-184, 30), (-204, 60),
            (-232, 74), (-262, 62), (-296, 78), (-330, 66), (-342, 36), (-328, 16), (-330, -8)]
    cabo = bevel(planta(_curva(fora), 0, 23, 'faia_x'), 5.0, 3)
    furo = bevel(planta(_curva([(-312, -30), (-296, -52), (-264, -48), (-250, -22), (-252, 26), (-268, 46), (-298, 44), (-312, 22)]), -5, 28, 'faia_x'), 3.0, 2)
    cut(cabo, [furo])
    cut(cabo, [caixa(-236, -180, Y - 0.9, Y + 0.9, -70, 70, 'faia_x')])                           # rasgo onde entra a lâmina
    p = [cabo]
    for (x, z) in ((-218, -46), (-202, 0), (-220, 46)):                                           # parafusos de latão
        p.append(cil((x, -0.6, z), (x, 23.6, z), 5.5, 'latao', n=14))
    raiz = parte('cabo', p, origem=G(0, 0, 0), grupo='A')
    parte('lamina', [lam], origem=G(0, 0, 0), pai=raiz, grupo='A', suave=20)
    return raiz


# ------------------------------------------------------------------ tábua
def tabua():
    rnd = random.Random(7)
    t = bevel(caixa(-750, 750, 0, 26, -75, 75, 'pinho_x'), 1.6, 2)
    # ponta rachada e canto lascado (tábua tirada de móvel ou de cerca)
    cut(t, [planta([(752, 18), (752, 24), (640, 21)], -5, 31, 'pinho_x'),
            planta([(-752, -77), (-712, -77), (-752, -52)], 14, 31, 'pinho_x')])
    p = [t]
    for (x, z, ang) in ((-690, 38, 25), (-690, -36, -40), (700, -30, 60)):                        # pregos velhos entortados
        r = math.radians(ang)
        p.append(cil((x, 20, z), (x, 33, z), 1.7, 'ferrugem', n=8))
        p.append(cil((x, 33, z), (x + 9 * math.cos(r), 37, z + 9 * math.sin(r)), 1.7, 'ferrugem', n=8))
    for (x, z) in ((-60, 30), (-60, -32), (420, 34)):                                             # cabeças de prego no meio
        p.append(cil((x, 25.2, z), (x, 27.0, z), 3.6, 'ferrugem', n=10))
    raiz = parte('tabua', p[:1], origem=G(0, 0, 0), grupo='A')
    parte('pregos', p[1:], origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


# ------------------------------------------------------------------ caixa de pregos
def _prego(x, y, z, ang, inclina, comp=44.0):
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    dy = comp * math.sin(math.radians(inclina))
    h = comp * math.cos(math.radians(inclina))
    a, b = (x - c * h / 2, y - dy / 2, z - s * h / 2), (x + c * h / 2, y + dy / 2, z + s * h / 2)
    cab = (a[0] - c * 1.0, a[1], a[2] - s * 1.0)
    return [cil(a, (b[0] - c * 5, b[1] - dy * 0.11, b[2] - s * 5), 1.25, 'prego', n=6),
            cil((b[0] - c * 5, b[1] - dy * 0.11, b[2] - s * 5), b, 1.25, 'prego', n=6, r1=0.15),
            cil(cab, a, 3.0, 'prego', n=8)]


def caixa_pregos():
    rnd = random.Random(3)
    L, A, P_ = 96.0, 44.0, 62.0                    # caixinha de papelão aberta, com as abas para fora
    fora = bevel(caixa(-L / 2, L / 2, 0, A, -P_ / 2, P_ / 2, 'papelao'), 0.8, 1)
    cut(fora, [caixa(-L / 2 + 1.2, L / 2 - 1.2, 1.2, A + 5, -P_ / 2 + 1.2, P_ / 2 - 1.2, 'papelao')])
    p = [fora]
    for s in (-1, 1):                              # abas compridas dobradas para fora, as curtas em pé
        p.append(perfil([(s * P_ / 2, A - 0.6), (s * (P_ / 2 + 5.5), A + 22), (s * (P_ / 2 + 6.6), A + 21.6), (s * (P_ / 2 + 1.1), A - 0.6)][::s], -L / 2 + 0.5, L / 2 - 0.5, 'papelao'))
        p.append(frente([(s * L / 2, A - 0.6), (s * (L / 2 + 6.5), A + 20), (s * (L / 2 + 7.5), A + 19.4), (s * (L / 2 + 1.1), A - 0.6)][::s], -P_ / 2 + 2, P_ / 2 - 2, 'papelao'))
    rot = [caixa(-34, 34, 9, 35, P_ / 2 + 0.05, P_ / 2 + 0.35, 'papel')]                           # etiqueta colada na frente
    rot.append(letreiro('PREGOS', 9.5, 0, 22, P_ / 2 + 0.36, mat='letra_preta'))
    rot.append(letreiro('17 x 27  ·  1 kg', 5.0, 0, 13, P_ / 2 + 0.36, mat='letra_preta'))
    pr = []
    for k in range(46):                            # pregos amontoados até quase a boca
        y = 5 + 32 * (k / 45) ** 0.8
        pr += _prego(rnd.uniform(-22, 22), y, rnd.uniform(-6, 6), rnd.uniform(-22, 22) + (180 if rnd.random() < 0.5 else 0), rnd.uniform(-12, 12))
    for (x, z, ang) in ((-8, 20, 75), (14, -19, 100), (28, 17, 60)):                              # alguns atravessados por cima
        pr += _prego(x, 38.5, z * 0.3, ang - 90, rnd.uniform(-4, 4))
    raiz = parte('caixa', p, origem=G(0, 0, 0), grupo='A')
    parte('etiqueta', rot, origem=G(0, 0, 0), pai=raiz, grupo='A')
    parte('pregos', pr, origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


# ------------------------------------------------------------------ cano de ferro
def cano_metal():
    Y, R, RI = 21.0, 17.0, 13.6
    X0 = -375.0
    rosca = []
    t = 3.0
    while t < 34:                                  # rosca cortada na ponta livre
        rosca += [(t, R - 1.3), (t + 1.3, R - 0.1)]
        t += 2.6
    prof = [(0, RI), (0, R - 1.6), (1.5, R - 1.2)] + rosca + [(36, R), (722, R), (722, RI)]
    tubo = lib.lathe(prof, 'ferro_preto', n=20, c0=G(X0, Y, 0), eixo=G(1, 0, 0), anel=True)
    # luva rosqueada na outra ponta, com as duas bordas reforçadas
    luva = lib.lathe([(0, RI + 1.5), (0, 20.2), (1.5, 21), (8, 21), (9.5, 19.6), (40.5, 19.6), (42, 21), (48.5, 21), (50, 20.2), (50, RI + 1.5)],
                     'aco_ferramenta', n=20, c0=G(325, Y, 0), eixo=G(1, 0, 0), anel=True)
    raiz = parte('cano', [tubo], origem=G(0, 0, 0), grupo='A')
    parte('luva', [luva], origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


# ------------------------------------------------------------------ chapa de metal ondulada
def chapa_metal():
    L, P_, PASSO, ALT, ESP = 900.0, 600.0, 75.0, 8.5, 0.9

    def alto(x, z):
        y = ALT + ALT * math.sin(2 * math.pi * (z + 300) / PASSO - math.pi / 2)
        y += 2.5 * math.sin(x / 170.0 + z / 240.0)                                       # chapa velha: empenada
        a, b = max(0.0, (x - 190) / 260), max(0.0, (z - 20) / 280)
        y += 66.0 * (a * b) ** 1.6                                                       # canto dobrado para cima
        return y + 2.6
    xs = [-L / 2 + L * i / 12 for i in range(13)]
    zs = [-P_ / 2 + P_ * k / 48 for k in range(49)]
    aneis = []
    for x in xs:
        cima = [(x, alto(x, z), z) for z in zs]
        baixo = [(x, y - ESP, z) for (x, y, z) in reversed(cima)]
        aneis.append([lib.P(*G(*p)) for p in cima + baixo])
    ch = lib.loft(aneis, 'zinco')
    p = []
    for (x, z) in ((-410, -262), (-410, 38), (-410, 188), (-60, -262), (-60, 113), (330, -187)):   # parafusos de telhado com arruela
        y = alto(x, z)
        p.append(cil((x, y - 0.2, z), (x, y + 1.0, z), 7.5, 'borracha', n=12))
        p.append(cil((x, y + 1.0, z), (x, y + 4.2, z), 4.6, 'prego', n=6))
    raiz = parte('chapa', [ch], origem=G(0, 0, 0), grupo='A', suave=60)
    parte('parafusos', p, origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


# ------------------------------------------------------------------ punhado de sucata
def _girar(o, ang, cx=0.0, cz=0.0):
    """Gira a peça em volta do eixo vertical que passa por (cx, cz)."""
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return _mexer(o, lambda x, y, z: (cx + (x - cx) * c - (z - cz) * s, y, cz + (x - cx) * s + (z - cz) * c))


def _porca(x, y, z, r=7.0, h=6.0, mat='aco_ferramenta'):
    o = lib.lathe([(0, r * 0.52), (0, r - 0.8), (0.8, r), (h - 0.8, r), (h, r - 0.8), (h, r * 0.52)], mat, n=6, c0=G(x, y, z), eixo=G(0, 1, 0), anel=True)
    return o


def sucata_metal():
    p = []
    # cantoneira cortada, deitada
    c = bevel(perfil([(-19, 0), (19, 0), (19, 3.2), (-15.8, 3.2), (-15.8, 36), (-19, 36)], -128, 40, 'ferrugem'), 0.6, 1)
    cut(c, [cil((-100, 18, -30), (-100, 18, 0), 4.5, 'ferrugem', n=10), cil((10, 18, -30), (10, 18, 0), 4.5, 'ferrugem', n=10)])
    p.append(_girar(_mexer(c, lambda x, y, z: (x, y, z - 38)), -4, -40, -40))
    # chapa recortada e amassada, com furos
    ch = planta([(-70, -22), (62, -30), (78, 14), (30, 34), (-20, 26), (-74, 30)], 0, 2.0, 'zinco')
    cut(ch, [cil((-40, -5, 0), (-40, 8, 0), 6, 'zinco', n=10), cil((30, -5, -6), (30, 8, -6), 6, 'zinco', n=10)])
    _mexer(ch, lambda x, y, z: (x, y + 0.2 + 0.0016 * (x + 20) ** 2 + 0.004 * max(0.0, z) ** 2, z))
    p.append(_girar(_mexer(ch, lambda x, y, z: (x + 52, y, z + 20)), 12, 52, 20))
    # toco de cano
    t = lib.lathe([(0, 9.5), (0, 13), (72, 13), (72, 9.5)], 'ferro_preto', n=14, c0=G(-120, 13, 22), eixo=G(1, 0, 0), anel=True)
    p.append(_girar(t, 17, -84, 22))
    # vergalhão torto
    p.append(lib.fio(lib.caminho_arred([G(-30, 5.2, 50), G(40, 5.2, 58), G(96, 5.2, 46), G(136, 12, 20)], 14.0, n=4, fechado=False), 4.6, 'ferrugem', fechado=False, res=2))
    # mola de válvula, parafuso, porcas e arruelas soltas
    mola = [G(104 + 9 * math.cos(a), 3 + 26 * a / (2 * math.pi * 6.5) , -34 + 9 * math.sin(a)) for a in [2 * math.pi * k / 10 for k in range(66)]]
    p.append(lib.fio(mola, 1.5, 'aco_ferramenta', fechado=False, res=1))
    p.append(cil((60, 5, -50), (112, 5, -58), 4.0, 'ferro_preto', n=10))
    p.append(cil((54, 5, -49.1), (60, 5, -50), 8.0, 'ferro_preto', n=6))
    p.append(_porca(126, 0, 44, 8.5, 7))
    p.append(_porca(-136, 0, 54, 7, 6, 'ferrugem'))
    p.append(_porca(-6, 2.2, 6, 6.5, 5.5))
    for (x, z, r, mat) in ((-112, -8, 11, 'aco_ferramenta'), (134, -8, 9, 'ferrugem'), (20, 44, 12, 'cobre_velho')):
        p.append(lib.lathe([(0, r * 0.45), (0, r), (1.6, r), (1.6, r * 0.45)], mat, n=14, c0=G(x, 0, z), eixo=G(0, 1, 0), anel=True))
    return parte('sucata', p, origem=G(0, 0, 0), grupo='A')


# ------------------------------------------------------------------ pá de bico
def _fita(pts, larg, y0, y1, mat):
    """Fita de aço vista de cima: poligonal [(x, z)] com largura larg, de y0 a y1."""
    esq, dir_ = [], []
    for i, (x, z) in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        dx, dz = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dz)
        nx, nz = -dz / d, dx / d
        esq.append((x + nx * larg / 2, z + nz * larg / 2))
        dir_.append((x - nx * larg / 2, z - nz * larg / 2))
    return planta(esq + dir_[::-1], y0, y1, mat)


def _gume(secoes, mat, Y):
    """Lâmina em fatias ao longo de x: [(x, z do dorso, z do começo do chanfro, z do fio, espessura)]."""
    aneis = []
    for (x, zs, zm, ze, e) in secoes:
        pts = [(zs, e / 2), (zm, e * 0.42), (ze, 0.12), (ze, -0.12), (zm, -e * 0.42), (zs, -e / 2)]
        aneis.append([lib.P(*G(x, Y + dy, z)) for (z, dy) in pts])
    return lib.loft(aneis, mat)


def pa():
    Y = 24.0
    cabo = _torno_x([(0, 0), (0, 17), (60, 17.5), (500, 18), (900, 19), (1040, 19), (1040, 0)], 'faia_x', -610, Y, n=18)
    # punho em D: luva de aço, duas fitas abrindo em forquilha e a travessa de madeira rebitada
    luva = lib.lathe([(0, 17), (0, 19.5), (2, 20.5), (70, 20.5), (78, 19), (78, 17)], 'aco_ferramenta', n=18, c0=G(-646, Y, 0), eixo=G(1, 0, 0), anel=True)
    fer = [luva]
    for s in (-1, 1):
        fer.append(_fita([(-585, s * 19.5), (-628, s * 22), (-668, s * 52), (-688, s * 57.5), (-708, s * 57.5)][::s], 4.0, Y - 10, Y + 10, 'aco_ferramenta'))
        fer.append(cil((-694, Y, s * 59.5), (-694, Y, s * 61.6), 5.5, 'aco_lamina', n=12))
    trav = _torno_z([(0, 0), (0, 12.5), (4, 14.5), (55.5, 16.5), (107, 14.5), (111, 12.5), (111, 0)], 'faia_z', -694, Y, -55.5, n=16)

    # lâmina de bico: costas no chão, abaulada, com os pisantes dobrados nos ombros
    def meia(x):
        if x < 510:
            return 108.0 + 10.0 * min(1.0, (x - 478) / 20.0) ** 0.5
        t = max(0.0, (x - 690) / 141.0)
        return max(2.5, 118.0 * (1.0 - t ** 1.9))

    def alto(x, z):
        t = max(0.0, (x - 690) / 141.0)
        h = meia(x)
        return 3.4 + 7.0 * t * t + 30.0 * (1.0 - 0.45 * t) * (h / 118.0) ** 2 * (z / h) ** 2
    aneis = []
    for x in (478, 484, 495, 510, 540, 580, 620, 660, 690, 715, 740, 762, 782, 800, 814, 824, 830):
        h = meia(x)
        zs = [h * (k / 6.0 - 1.0) for k in range(13)]
        cima = [(x, alto(x, z), z) for z in zs]
        baixo = [(x, y - 2.4, z) for (x, y, z) in reversed(cima)]
        aneis.append([lib.P(*G(*p)) for p in cima + baixo])
    lam = lib.loft(aneis, 'ferro_preto')
    pintar(lam, 'aco_lamina', lambda c, n: c[2] > 770.0)                      # ponta lixada de tanto cavar
    # encaixe do cabo: tubo que achata e morre no meio da lâmina
    enc = []
    for (x, cy, ry, rz) in ((392, Y, 21.5, 21.5), (396, Y, 22.5, 22.5), (470, Y - 1, 21.5, 23), (520, 19, 16.5, 27), (570, 12.5, 10.5, 31),
                            (620, 8.5, 6.0, 30), (670, 6.2, 3.2, 20), (715, 5.5, 1.4, 6)):
        enc.append([lib.P(*G(x, cy + ry * math.sin(2 * math.pi * k / 16), rz * math.cos(2 * math.pi * k / 16))) for k in range(16)])
    enc = lib.loft(enc, 'ferro_preto')
    pis = []
    for s in (-1, 1):
        pis.append(lib.fio([G(481, alto(481, s * z) + 1.6, s * z) for z in (34, 50, 66, 82, 98, 112)], 3.4, 'ferro_preto', fechado=False, res=2))
    reb = [cil((430, Y + 20.5, 0), (430, Y + 23.2, 0), 4.6, 'aco_lamina', n=10)]                  # rebite que prende o cabo
    raiz = parte('cabo', [cabo, trav], origem=G(0, 0, 0), grupo='A')
    parte('punho', fer, origem=G(0, 0, 0), pai=raiz, grupo='A')
    parte('lamina', [lam, enc] + pis + reb, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    return raiz


# ------------------------------------------------------------------ enxada
def enxada():
    FI = math.radians(20.0)                                # a lâmina fecha para o lado do cabo
    sf, cf = math.sin(FI), math.cos(FI)
    cabo = _torno_x([(0, 0), (0, 15), (5, 17), (700, 17), (1250, 18.5), (1330, 20), (1356, 20.5), (1356, 0)], 'faia_x', -700, 0, n=18)
    olho = lib.lathe([(0, 19.5), (0, 26), (3, 28), (45, 28), (48, 26), (48, 19.5)], 'ferro_preto', n=20, c0=G(600, 0, 0), eixo=G(1, 0, 0), anel=True)

    def fatias(secoes, mat):
        aneis = []
        for (s, hw, e, rec) in secoes:
            cx, cz = 624 - s * sf - rec * cf, 20 + s * cf - rec * sf
            aneis.append([lib.P(*G(cx + a * cf * e / 2, b * hw, cz + a * sf * e / 2)) for (a, b) in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
        return lib.loft(aneis, mat)
    lam = bevel(fatias([(0, 22, 13, 0), (16, 30, 10, 0), (36, 66, 5.5, 0), (58, 86, 3.8, 0), (120, 90, 3.2, 0), (196, 93, 2.6, 0), (216, 93, 0.5, 0)], 'ferro_preto'), 1.0, 2)
    pintar(lam, 'aco_lamina', lambda c, n: -c[0] > 20 + 186 * cf)                                # fio amolado na pedra
    nerv = fatias([(0, 9, 12, 5), (60, 8, 7, 3.5), (118, 5, 2.5, 1.6)], 'ferro_preto')            # nervura de reforço nas costas
    cunha = caixa(655.6, 657.2, -3, 3, -15, 15, 'aco_lamina')
    pecas = [cabo, olho, lam, nerv, cunha]
    # deitada: a ponta do cabo e a quina da lâmina tocam o chão, o cabo sobe até a cabeça
    TILT = math.asin(77.0 / 1340.0)
    ct, st = math.cos(TILT), math.sin(TILT)
    for o in pecas:
        _mexer(o, lambda x, y, z: (-700 + (x + 700) * ct - y * st, 16.0 + (x + 700) * st + y * ct, z))
    raiz = parte('cabo', [cabo], origem=G(0, 0, 0), grupo='A')
    parte('cabeca', [olho, lam, nerv, cunha], origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


# ------------------------------------------------------------------ faca de cozinha
def _cabo_faca(contorno, Y, esp, mat, rebites, mat_reb, espiga='inox'):
    """Cabo de faca de espiga inteira: duas talas rebitadas com o aço aparecendo no meio."""
    c = _curva(contorno, 2)
    p = [planta(c, Y - 1.3, Y + 1.3, espiga)]
    for s in (-1, 1):
        a, b = sorted((Y + s * 1.3, Y + s * esp))
        p.append(bevel(planta([(x * 0.992, z * 0.985) for (x, z) in c], a, b, mat), 2.4, 2))
    reb = [cil((x, Y - esp - 0.25, z), (x, Y + esp + 0.25, z), r, mat_reb, n=12) for (x, z, r) in rebites]
    return p, reb


def faca_cozinha():
    Y = 9.3
    sec = []
    for k in range(21):
        x = 200.0 * k / 20
        zs = -19.0 if x < 110 else -19.0 + 17.5 * ((x - 110) / 90.0) ** 2.2
        ze = 25.0 if x < 60 else 25.0 - 26.0 * ((x - 60) / 140.0) ** 1.8
        ze = max(ze, zs + 0.6)
        sec.append((x, zs, zs + 0.72 * (ze - zs), ze, 2.3 * (1.0 - 0.62 * x / 200.0)))
    sec[-1] = (200.0, -1.3, -1.25, -1.2, 0.3)                                                    # ponta fechada
    lam = _gume(sec, 'aco_lamina', Y)
    gola = bevel(caixa(-11, 1.5, Y - 8.6, Y + 8.6, -20.0, 9.0, 'inox'), 2.2, 2)                    # gola forjada entre a lâmina e o cabo
    talas, reb = _cabo_faca([(-9, -19.4), (-9, 8.4), (-38, 9.5), (-78, 6.5), (-104, 8.5), (-121, 12.5), (-129, 6), (-129, -14), (-121, -20.6), (-60, -20)],
                            Y, 9.0, 'plastico_preto', [(-31, -5, 3.3), (-66, -6.5, 3.3), (-101, -5, 3.3)], 'inox')
    raiz = parte('cabo', talas, origem=G(0, 0, 0), grupo='A')
    parte('lamina', [lam], origem=G(0, 0, 0), pai=raiz, grupo='A', suave=25)
    parte('ferragem', [gola] + reb, origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


# ------------------------------------------------------------------ facão
def facao():
    Y = 10.6
    sec = []
    xs = [-124.0 + 424.0 * k / 12 for k in range(13)] + [312, 324, 336, 346, 355, 362, 367, 371, 373.5]
    for x in xs:
        zs = -19.0 - 3.0 * (x + 124) / 498.0
        ze = 17.0 + 10.5 * min(1.0, (x + 124) / 424.0) if x <= 300 else 27.5 - 47.0 * ((x - 300) / 73.5) ** 2.0
        ze = max(ze, zs + 0.8)
        sec.append((x, zs, max(zs + 0.3, ze - 9.5), ze, 2.7 * (1.0 - 0.35 * (x + 124) / 498.0)))
    lam = _gume(sec, 'aco_ferramenta', Y)

    def zm(x):
        return next((s[2] for s in sec if s[0] >= x - 1e-6), sec[-1][2])
    pintar(lam, 'aco_lamina', lambda c, n: abs(n[1]) < 0.985 and -c[0] > zm(c[2]) - 12.0 and -c[0] > -8.0)   # chanfro do fio, amolado
    talas, reb = _cabo_faca([(-118, -21.5), (-118, 17.5), (-158, 15), (-214, 16), (-246, 20.5), (-262, 28), (-273, 22), (-273, -12), (-262, -22), (-190, -20.5)],
                            Y, 10.4, 'imbuia_x', [(-140, -2, 3.6), (-190, -2.5, 3.6), (-240, -1, 3.6)], 'latao', espiga='aco_ferramenta')
    furo = lib.lathe([(0, 2.6), (0, 4.4), (21.4, 4.4), (21.4, 2.6)], 'latao', n=12, c0=G(-262, Y - 10.7, 12), eixo=G(0, 1, 0), anel=True)   # ilhós do cordão
    raiz = parte('cabo', talas, origem=G(0, 0, 0), grupo='A')
    parte('lamina', [lam], origem=G(0, 0, 0), pai=raiz, grupo='A', suave=25)
    parte('ferragem', reb + [furo], origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


# ------------------------------------------------------------------ pé de cabra
def pe_de_cabra():
    Y, R = 11.0, 9.5
    caminho = [(-298, 10.0, 0.10, 1.6), (-290, 6.4, 0.28, 1.5), (-281, 3.2, 0.5, 1.3), (-271, 1.0, 0.8, 1.1), (-260, 0, 1, 1)]   # (x, z, achatado, alargado)
    caminho += [(-260 + 485.0 * k / 12, 0, 1, 1) for k in range(1, 13)]
    CX, CZ, RC = 225.0, 62.0, 62.0
    for k in range(1, 17):
        a = math.radians(-90 + 205.0 * k / 16)
        caminho.append((CX + RC * math.cos(a), CZ + RC * math.sin(a), 1, 1))
    a = math.radians(115)
    px, pz, tx, tz = CX + RC * math.cos(a), CZ + RC * math.sin(a), -math.sin(a), math.cos(a)
    for d, sn, sy in ((9, 0.8, 1.1), (18, 0.5, 1.3), (27, 0.28, 1.5), (36, 0.10, 1.6)):
        caminho.append((px + tx * d, pz + tz * d - 0.012 * d * d, sn, sy))
    aneis = []
    for i, (x, z, sn, sy) in enumerate(caminho):
        a_, b_ = caminho[max(i - 1, 0)], caminho[min(i + 1, len(caminho) - 1)]
        dx, dz = b_[0] - a_[0], b_[1] - a_[1]
        d = math.hypot(dx, dz)
        nx, nz = -dz / d, dx / d
        anel = []
        for k in range(6):
            g = math.radians(60 * k + 30)
            oy, on = R * math.cos(g) * sy, R * math.sin(g) * sn
            anel.append(lib.P(*G(x + nx * on, Y + oy, z + nz * on)))
        aneis.append(anel)
    barra = lib.loft(aneis, 'esmalte_azul')
    pintar(barra, 'aco_lamina', lambda c, n: c[2] < -268 or (-c[0] > 84 and c[2] < 214))             # pontas lixadas, sem tinta
    fenda = [caminho[-1], caminho[-3]]
    unha = planta([(fenda[0][0] - 1.5, fenda[0][1] - 1.5), (fenda[1][0], fenda[1][1] + 0.4), (fenda[0][0] + 1.0, fenda[0][1] + 2.0)], Y - 2.4, Y + 2.4, 'ferro_preto')   # fenda de arrancar prego
    raiz = parte('barra', [barra], origem=G(0, 0, 0), grupo='A', suave=35)
    parte('fenda', [unha], origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


# ------------------------------------------------------------------ chave inglesa
def chave_inglesa():
    Y = 6.5
    cabo = bevel(planta(_curva([(-109, -9), (-109, 9), (-100, 12), (30, 13.5), (44, 15), (44, -14), (30, -12.5), (-100, -12)], 1), Y - 4.2, Y + 4.2, 'aco_ferramenta'), 1.2, 2)
    borda = [bevel(planta([(-88, 8.2), (26, 9.8), (26, 12.6), (-88, 11.2)], Y - 5.4, Y + 5.4, 'aco_ferramenta'), 0.8, 1),
             bevel(planta([(-88, -11.2), (26, -11.8), (26, -9.0), (-88, -8.2)], Y - 5.4, Y + 5.4, 'aco_ferramenta'), 0.8, 1)]      # nervuras do cabo
    furo = lib.lathe([(0, 5.0), (0, 8.6), (9.6, 8.6), (9.6, 5.0)], 'aco_ferramenta', n=16, c0=G(-99, Y - 4.8, 0), eixo=G(0, 1, 0), anel=True)
    corpo = bevel(planta(_curva([(36, -13), (50, -26), (72, -30), (92, -27), (107, -15), (107, -6), (84, -6), (84, 15), (64, 23), (36, 14)], 1), Y - 6.5, Y + 6.5, 'aco_ferramenta'), 1.4, 2)
    pintar(corpo, 'aco_lamina', lambda c, n: -n[0] > 0.9 and c[2] > 84 and -c[0] < -4)             # face do mordente fixo
    movel = bevel(planta([(84.4, 10), (107, 10), (107, 17), (99, 27), (86, 30), (84.4, 28)], Y - 6.5, Y + 6.5, 'aco_ferramenta'), 1.2, 2)
    pintar(movel, 'aco_lamina', lambda c, n: -n[0] < -0.9 and c[2] > 86)
    guia = caixa(78, 84.4, Y - 2.6, Y + 2.6, -4, 29, 'aco_ferramenta')
    janela = caixa(64, 80, Y - 6.7, Y + 6.7, 0.5, 19.5, 'ferro_preto')
    prof = [(0, 0), (0, 6.2)]
    for k in range(8):
        prof += [(0.4 + 2.1 * k, 7.3), (1.5 + 2.1 * k, 7.3), (2.0 + 2.1 * k, 6.2)]
    prof += [(17.6, 6.2), (17.6, 0)]
    rosca = lib.lathe(prof, 'inox', n=14, c0=G(72, Y, 1.2), eixo=G(0, 0, 1))
    txt = [_deitado_x('200 mm', 5.0, -30, 0.6, Y + 4.25)]
    raiz = parte('cabo', [cabo, furo] + borda, origem=G(0, 0, 0), grupo='A', suave=35)
    parte('cabeca', [corpo, guia, janela], origem=G(0, 0, 0), pai=raiz, grupo='A', suave=35)
    parte('mordente', [movel, rosca], origem=G(0, 0, 0), pai=raiz, grupo='A', suave=35)
    parte('letras', txt, origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


def _deitado_x(s, tam, x, z, y, mat='aco_lamina'):
    """Texto gravado numa face de cima, lido por quem olha de +z."""
    o = letreiro(s, tam, 0, 0, 0, mat=mat)
    return _mexer(o, lambda px, py, pz: (x + px, y, z - py + tam * 0.35))


# ------------------------------------------------------------------ faca de pedra lascada
def faca_pedra():
    Y = 9.5
    rnd = random.Random(21)
    sec = []
    xs = [-18 + 148.0 * k / 16 for k in range(17)]
    for i, x in enumerate(xs):
        u = (x + 18) / 148.0
        larg = 21.0 * math.sin(math.pi * (0.16 + 0.80 * u)) ** 0.7 if u < 0.97 else 1.5
        zs = -larg * 0.85 + rnd.uniform(-1.6, 1.6)
        ze = larg * 1.0 + rnd.uniform(-2.4, 2.4)
        sec.append((x, zs, zs + 0.45 * (ze - zs) + rnd.uniform(-3, 3), ze, max(1.2, 8.5 * (1 - 0.75 * u) + rnd.uniform(-1.2, 1.2))))
    sec[-1] = (130.0, 1.0, 1.4, 1.8, 0.8)
    lam = _gume(sec, 'pedra_lascada', Y)
    cabo = _torno_x([(0, 0), (0, 9.5), (3, 11), (40, 11.6), (80, 10.6), (104, 11.4), (108, 9), (108, 0)], 'crua_x', -122, Y, n=14, achata=0.82)
    amarra = []
    for k in range(9):
        x = 86 + k * 3.3
        r = 11.6 + (0.5 if k % 2 else 0.0) + 0.5
        amarra.append(lib.lathe([(x, r - 1.6), (x, r), (x + 3.1, r), (x + 3.1, r - 1.6)], 'sisal', n=14, c0=G(-122, Y, 0), eixo=G(1, 0, 0), anel=True))
    for o in amarra:
        c = lib.P(*G(0, Y, 0))
        o.data.transform(Matrix.Translation(c) @ Matrix.Diagonal((1, 1, 0.86, 1)) @ Matrix.Translation(-c))
    raiz = parte('cabo', [cabo], origem=G(0, 0, 0), grupo='A', suave=40)
    parte('lamina', [lam], origem=G(0, 0, 0), pai=raiz, grupo='A', suave=12)
    parte('amarra', amarra, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    return raiz


# ------------------------------------------------------------------ lâmina forjada (sem cabo)
def lamina_forjada():
    Y = 3.0
    sec = []
    for k in range(19):
        x = -20 + 190.0 * k / 18
        u = k / 18
        zs = -17.0 + 1.2 * math.sin(u * 9) if u < 0.6 else -17.0 + 15.0 * ((u - 0.6) / 0.4) ** 2.0
        ze = 19.0 + 1.0 * math.sin(u * 7 + 1) if u < 0.45 else 19.0 - 19.5 * ((u - 0.45) / 0.55) ** 1.7
        ze = max(ze, zs + 0.8)
        sec.append((x, zs, zs + 0.70 * (ze - zs), ze, 4.2 * (1 - 0.55 * u)))
    sec[-1] = (170.0, -1.6, -1.5, -1.4, 0.5)
    lam = _gume(sec, 'ferro_preto', Y)

    def zm(x):
        return next((s_[2] for s_ in sec if s_[0] >= x - 1e-6), sec[-1][2])
    pintar(lam, 'aco_lamina', lambda c, n: -c[0] > zm(c[2]) + 0.3)            # o fio já desbastado na pedra
    espiga = bevel(planta([(-20, -9), (-20, 9), (-70, 6.5), (-104, 4.5), (-106, -4.5), (-70, -6.5)], Y - 1.9, Y + 1.9, 'ferro_preto'), 0.8, 1)
    furos = [cil((x, Y - 2.0, 0), (x, Y + 2.0, 0), 2.3, 'carvao', n=10) for x in (-42, -78)]
    raiz = parte('lamina', [lam], origem=G(0, 0, 0), grupo='A', suave=25)
    parte('espiga', [espiga] + furos, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=30)
    return raiz


FORMAS = {'martelo': martelo, 'machado': machado, 'serrote': serrote, 'tabua': tabua, 'caixa_pregos': caixa_pregos,
          'cano_metal': cano_metal, 'chapa_metal': chapa_metal, 'sucata_metal': sucata_metal,
          'pa': pa, 'enxada': enxada, 'faca_cozinha': faca_cozinha, 'facao': facao,
          'pe_de_cabra': pe_de_cabra, 'chave_inglesa': chave_inglesa, 'faca_pedra': faca_pedra, 'lamina_forjada': lamina_forjada}
