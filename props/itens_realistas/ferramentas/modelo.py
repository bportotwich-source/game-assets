"""Ferramentas e materiais de craft no nível realista: martelo de unha, machado, serrote, tábua e
caixa de pregos. Desenho próprio, sem marcas.

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


FORMAS = {'martelo': martelo, 'machado': machado, 'serrote': serrote, 'tabua': tabua, 'caixa_pregos': caixa_pregos,
          'cano_metal': cano_metal, 'chapa_metal': chapa_metal, 'sucata_metal': sucata_metal}
