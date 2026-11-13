"""Remédios no nível realista: kit de primeiros socorros, frasco de comprimidos, rolo de atadura, seringa,
lata de costura, garrafa de álcool, curativo de pano, tala, maço de ervas e remédio de ervas. Desenho próprio, sem marcas.

Coordenadas do jogo em mm (base.py dos móveis): x = largura, y = para cima, z = frente. Cada item fica na
mesma posição do antigo e com tamanho próximo.
"""
import os, math, random, importlib.util
from mathutils import Vector
import lib
from lib import bevel, parte, pintar, MM
from base import G, caixa, cil, planta, perfil, frente

_spec = importlib.util.spec_from_file_location('modelo_comida', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'comida', 'modelo.py'))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)
letreiro, _mexer, _na_lata, _deitado, _ret_arred, _sup = C.letreiro, C._mexer, C._na_lata, C._deitado, C._ret_arred, C._sup


def _anel(pts, y, d=0.0):
    return [lib.P(*G(x * (1 - d / max(1, abs(x))) if d else x, y, z * (1 - d / max(1, abs(z))) if d else z)) for (x, z) in pts]


def _cruz(x, y, z, t, mat, esp=0.4):
    """Cruz deitada de braço t, centrada em (x, z)."""
    a, b = t, t / 3.0
    return planta([(x - b, z - a), (x + b, z - a), (x + b, z - b), (x + a, z - b), (x + a, z + b), (x + b, z + b), (x + b, z + a), (x - b, z + a),
                   (x - b, z + b), (x - a, z + b), (x - a, z - b), (x - b, z - b)][::-1], y, y + esp, mat)


# ------------------------------------------------------------------ kit de primeiros socorros
def kit_medico():
    HX, HZ, R = 130.0, 99.0, 20.0
    aneis = [_anel(_ret_arred(HX - 3, HZ - 3, R - 3), 0), _anel(_ret_arred(HX, HZ, R), 3), _anel(_ret_arred(HX, HZ, R), 54),
             _anel(_ret_arred(HX - 1.6, HZ - 1.6, R - 1.6), 54.8), _anel(_ret_arred(HX - 1.6, HZ - 1.6, R - 1.6), 57.2),
             _anel(_ret_arred(HX, HZ, R), 58), _anel(_ret_arred(HX, HZ, R), 88), _anel(_ret_arred(HX - 2, HZ - 2, R - 2), 92.5),
             _anel(_ret_arred(HX - 7, HZ - 7, R - 6), 94)]
    cx = lib.loft(aneis, 'plastico_verm')
    pintar(cx, 'plastico_preto', lambda c, n: 54.6 < c[1] < 57.4)                                # junta da tampa
    est = [planta(_ret_arred(HX - 14, HZ - 14, R - 8), 94, 94.6, 'plastico_verm'),
           lib.lathe([(0, 0), (0, 44), (0.5, 44), (0.5, 0)], 'plastico_branco', n=36, c0=G(0, 94.6, 0), eixo=G(0, 1, 0)), _cruz(0, 95.1, 0, 31, 'letra_vermelha')]
    alto = lambda x, z: 94.9
    txt = [_deitado('PRIMEIROS SOCORROS', 12.5, 0, 74, alto, 'letra_branca')]
    fer = []
    for x in (-72, 72):                                                                          # dois fechos na frente
        fer += [bevel(caixa(x - 14, x + 14, 44, 70, HZ, HZ + 5, 'plastico_branco'), 1.6, 2), caixa(x - 10, x + 10, 40, 46, HZ, HZ + 3.2, 'plastico_branco')]
    fer += [caixa(-52, -40, 60, 80, HZ, HZ + 9, 'plastico_branco'), caixa(40, 52, 60, 80, HZ, HZ + 9, 'plastico_branco'),
            bevel(caixa(-52, 52, 62, 78, HZ + 9, HZ + 19, 'plastico_branco'), 4.0, 3)]              # alça
    for x in (-80, 80):                                                                          # dobradiças atrás
        fer.append(cil((x - 16, 56, -HZ - 1.5), (x + 16, 56, -HZ - 1.5), 3.6, 'plastico_branco', n=10))
    raiz = parte('caixa', [cx], origem=G(0, 0, 0), grupo='A', suave=45)
    parte('estampa', est, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    parte('letras', txt, origem=G(0, 0, 0), pai=raiz, grupo='A')
    parte('ferragens', fer, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    return raiz


# ------------------------------------------------------------------ frasco de comprimidos
def frasco_remedio():
    R, H = 21.0, 58.0
    corpo = lib.lathe([(0, 0), (0, R - 2), (2, R), (H - 6, R), (H - 2, R - 3.5), (H + 4, R - 3.5), (H + 4, 0)], 'frasco_laranja', n=28, c0=G(0, 0, 0), eixo=G(0, 1, 0))
    rot = lib.lathe([(9, R), (9, R + 0.3), (38, R + 0.3), (46, R + 0.3), (46, R)], 'rot_branco', n=28, c0=G(0, 0, 0), eixo=G(0, 1, 0))
    pintar(rot, 'rot_azul', lambda c, n: c[1] > 38)
    prof = [(H + 2, R - 3), (H + 2, R + 1.4)]
    for k in range(6):                                                                           # tampa com estrias
        y = H + 3 + k * 3.4
        prof += [(y, R + 2.0), (y + 2.2, R + 2.0), (y + 2.8, R + 1.2)]
    prof += [(H + 24.4, R + 1.6), (H + 26, R - 0.5), (H + 26, 0)]
    tampa = lib.lathe(prof, 'plastico_branco', n=28, c0=G(0, 0, 0), eixo=G(0, 1, 0))
    txt = [_na_lata('COMPRIMIDOS', 4.6, 40.2, R + 0.55, 'letra_branca'), _na_lata('analgésico', 4.4, 28, R + 0.55, 'letra_azul'),
           _na_lata('500 mg  ·  30 un', 3.2, 20, R + 0.55, 'letra_preta'), _na_lata('tomar 1 a cada 8 horas', 2.4, 13, R + 0.55, 'letra_preta')]
    raiz = parte('frasco', [corpo], origem=G(0, 0, 0), grupo='A', suave=40)
    parte('rotulo', [rot], origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    parte('letras', txt, origem=G(0, 0, 0), pai=raiz, grupo='A')
    parte('tampa', [tampa], origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    return raiz


# ------------------------------------------------------------------ rolo de atadura
def atadura():
    R, L = 30.0, 78.0
    prof = [(0, 0)]
    r = 5.0
    while r < R - 2:                                                                             # voltas à mostra no topo do rolo
        prof += [(0.0, r), (0.9, r + 1.2), (0.0, r + 2.4)]
        r += 2.4
    prof += [(0.4, R), (L - 0.4, R)]
    r = R - 1.0
    while r > 6:
        prof += [(L, r), (L - 0.9, r - 1.2), (L, r - 2.4)]
        r -= 2.4
    prof += [(L, 0)]
    rolo = lib.lathe(prof, 'gaze', n=32, c0=G(-L / 2, R, 0), eixo=G(1, 0, 0))
    aneis = []
    for k in range(15):                                                                          # ponta solta que desce do rolo até o chão
        u = k / 14
        a = math.radians(55 - 60 * min(1.0, u / 0.35))
        if u <= 0.35:
            z, y = (R + 0.6) * math.sin(a) * -1 + 0, R + (R + 0.6) * math.cos(a)
            z = (R + 0.6) * math.sin(math.radians(-5 + 60 * u / 0.35))
            y = R + (R + 0.6) * math.cos(math.radians(-5 + 60 * u / 0.35))
        else:
            v = (u - 0.35) / 0.65
            z0, y0 = (R + 0.6) * math.sin(math.radians(55)), R + (R + 0.6) * math.cos(math.radians(55))
            z, y = z0 + 13 * v, max(0.9, y0 * (1 - v) ** 1.6 + 0.9)
        aneis.append([lib.P(*G(-L / 2 + 1, y, z)), lib.P(*G(L / 2 - 1, y, z)), lib.P(*G(L / 2 - 1, y - 0.8, z - 0.3)), lib.P(*G(-L / 2 + 1, y - 0.8, z - 0.3))][::-1])
    ponta = lib.loft(aneis, 'gaze')
    presilha = [bevel(caixa(-9, 9, 2 * R - 0.2, 2 * R + 1.3, -4, 4, 'lata'), 0.5, 1)]
    raiz = parte('rolo', [rolo, ponta], origem=G(0, 0, 0), grupo='A', suave=40)
    parte('presilha', presilha, origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


# ------------------------------------------------------------------ seringa com antibiótico
def seringa():
    Y, X0 = 9.0, -69.0
    ax = dict(c0=G(X0, Y, 0), eixo=G(1, 0, 0))
    corpo = lib.lathe([(34, 0), (34, 6.6), (35, 7.4), (88, 7.4), (90, 6.2), (91, 2.4), (97, 2.0), (97, 0)], 'seringa_corpo', n=20, **ax)
    pintar(corpo, 'remedio_liq', lambda c, n: X0 + 52 < c[2] < X0 + 88.5)                         # o antibiótico dentro
    aba = [bevel(planta_x(X0 + 33.0, X0 + 35.0, Y, 9.0, 12.0), 0.3, 1)]
    emb = [lib.lathe([(0, 0), (0, 8.6), (1.8, 8.6), (1.8, 2.4), (33, 2.4), (33, 0)], 'plastico_branco', n=16, **ax),
           lib.lathe([(48, 0), (48, 6.9), (52, 6.9), (52, 0)], 'borracha', n=16, **ax)]
    agulha = [lib.lathe([(97, 0), (97, 3.2), (104, 2.6), (105, 0.55), (136, 0.55), (139, 0)], 'inox', n=10, **ax)]
    pintar(agulha[0], 'plastico_amarelo', lambda c, n: c[2] < X0 + 104.6)
    marcas = []
    for k in range(11):
        x = X0 + 40 + k * 4.6
        marcas.append(caixa(x, x + 0.5, Y + 7.3, Y + 7.75, -(3.4 if k % 5 == 0 else 1.9), (3.4 if k % 5 == 0 else 1.9), 'letra_preta'))
    raiz = parte('corpo', [corpo] + aba, origem=G(0, 0, 0), grupo='A', suave=40)
    parte('embolo', emb, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    parte('agulha', agulha, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    parte('marcas', marcas, origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


def planta_x(x0, x1, yc, ry, rz):
    """Aba oval em pé (plano yz) entre x0 e x1."""
    return perfil([(rz * math.cos(2 * math.pi * k / 16), yc + ry * math.sin(2 * math.pi * k / 16)) for k in range(16)], x0, x1, 'seringa_corpo')


# ------------------------------------------------------------------ lata de costura
def _carretel(x, y, z, cor, R=13.0, H=30.0):
    return [lib.lathe([(0, 0), (0, R), (2.2, R), (2.2, 5), (H - 2.2, 5), (H - 2.2, R), (H, R), (H, 3.2), (H - 3, 3.2), (H - 3, 0)], 'faia_x', n=16, c0=G(x, y, z), eixo=G(0, 1, 0)),
            lib.lathe([(2.2, 5), (2.2, R - 2.5), (4, R - 1.4), (H - 4, R - 1.4), (H - 2.2, R - 2.5), (H - 2.2, 5)], cor, n=16, c0=G(x, y, z), eixo=G(0, 1, 0), anel=True)]


def kit_costura():
    HX, HZ, R, H = 113.0, 77.0, 22.0, 46.0
    aneis = [_anel(_ret_arred(HX - 2, HZ - 2, R - 2), 0), _anel(_ret_arred(HX, HZ, R), 2), _anel(_ret_arred(HX, HZ, R), H - 2),
             _anel(_ret_arred(HX + 1.2, HZ + 1.2, R + 1.2), H - 1), _anel(_ret_arred(HX + 1.2, HZ + 1.2, R + 1.2), H),
             _anel(_ret_arred(HX - 1.4, HZ - 1.4, R - 1.4), H), _anel(_ret_arred(HX - 1.4, HZ - 1.4, R - 1.4), 3.0)]
    lata = lib.loft(aneis, 'rot_azul')
    pintar(lata, 'lata', lambda c, n: c[1] > H - 2.2 or (n[1] > 0.5 and c[1] < 4) or (abs(n[1]) < 0.5 and (c[2] ** 2 / (HX - 1) ** 2 + c[0] ** 2 / (HZ - 1) ** 2) < 0.9 and False))
    pintar(lata, 'lata', lambda c, n: c[1] > 2.5 and c[1] < H - 0.2 and _dentro(c[2], -c[0], HX - 0.7, HZ - 0.7, R - 0.7))
    pintar(lata, 'rot_creme', lambda c, n: 14 < c[1] < 30 and not _dentro(c[2], -c[0], HX - 0.7, HZ - 0.7, R - 0.7))
    forro = [planta(_ret_arred(HX - 1.6, HZ - 1.6, R - 1.6), 2.6, 4.0, 'pano_vermelho')]
    itens = _carretel(-78, 4, -40, 'linha_verm') + _carretel(-44, 4, -42, 'letra_branca') + _carretel(-80, 4, -6, 'linha_preta')
    itens += [lib.lathe([(0, 0), (0, 26), (6, 30), (16, 30), (27, 20), (31, 0)], 'pano_vermelho', n=20, c0=G(-58, 4, 38), eixo=G(0, 1, 0))]     # alfineteiro
    rnd = random.Random(3)
    pinos = []
    for k in range(9):
        a, r = rnd.uniform(0, 6.283), rnd.uniform(4, 20)
        x, z, y = -58 + r * math.cos(a), 38 + r * math.sin(a), 4 + 31 - 9 * (r / 26) ** 2
        pinos += [cil((x, y - 6, z), (x + 2 * math.cos(a), y + 9, z + 2 * math.sin(a)), 0.45, 'inox', n=4),
                  lib.lathe([(0, 0), (0.8, 1.7), (2.2, 2.0), (3.4, 1.4), (3.8, 0)], ('letra_amarela', 'letra_branca', 'letra_azul')[k % 3], n=6, c0=G(x + 2 * math.cos(a), y + 8.5, z + 2 * math.sin(a)), eixo=G(0, 1, 0))]
    # tesoura deitada no fundo
    tes = []
    for s in (-1, 1):
        g = math.radians(8 * s)
        def gira(px, pz, g=g):
            return (30 + px * math.cos(g) - pz * math.sin(g), 4 + px * math.sin(g) + pz * math.cos(g))
        lam = [gira(-8, -2.5 * s), gira(62, 0.0), gira(-8, 6.5 * s)]
        tes.append(planta(lam if s > 0 else lam[::-1], 4.2 + (1.0 if s > 0 else 0), 5.2 + (1.0 if s > 0 else 0), 'inox'))
        cx_, cz_ = gira(-26, 13 * s)
        tes.append(lib.lathe([(0, 9), (0, 13.5), (3.4, 13.5), (3.4, 9)], 'plastico_preto', n=18, c0=G(cx_, 4.1, cz_), eixo=G(0, 1, 0), anel=True))
        p0, p1 = gira(-8, 3 * s), gira(-16, 7 * s)
        tes.append(cil((p0[0], 5.4, p0[1]), (p1[0], 5.4, p1[1]), 2.6, 'plastico_preto', n=6))
    tes.append(cil((30, 4.2, 4), (30, 6.8, 4), 2.2, 'inox', n=8))
    # fita métrica enrolada, botões e dedal
    fita = [lib.lathe([(0, 6.0 + 1.9 * k), (0, 7.2 + 1.9 * k), (13, 7.2 + 1.9 * k), (13, 6.0 + 1.9 * k)], 'letra_amarela', n=20, c0=G(68, 4, -40), eixo=G(0, 1, 0), anel=True) for k in range(7)]
    bot = []
    for (x, z, r, m) in ((20, -48, 7, 'plastico_branco'), (4, -34, 5.5, 'plastico_preto'), (26, -28, 6, 'rot_marrom'), (84, 40, 7, 'rot_marrom'), (70, 52, 5, 'plastico_branco'), (-14, -52, 5, 'letra_azul')):
        bot.append(lib.lathe([(0, 0), (0, r), (1.4, r), (2.0, r - 1), (1.3, r - 2.2), (1.3, 0)], m, n=12, c0=G(x, 4, z), eixo=G(0, 1, 0)))
    dedal = [lib.lathe([(0, 8.5), (0, 9.6), (1.2, 9.6), (16, 7.6), (19, 5), (19.6, 0)], 'lata', n=14, c0=G(96, 4, 12), eixo=G(0, 1, 0))]
    raiz = parte('lata', [lata], origem=G(0, 0, 0), grupo='A', suave=45)
    parte('forro', forro, origem=G(0, 0, 0), pai=raiz, grupo='A')
    parte('carreteis', itens + fita, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    parte('miudezas', pinos + bot + dedal, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    parte('tesoura', tes, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    return raiz


def _dentro(x, z, hx, hz, r):
    ax, az = abs(x), abs(z)
    if ax > hx or az > hz:
        return False
    if ax > hx - r and az > hz - r:
        return (ax - hx + r) ** 2 + (az - hz + r) ** 2 < r * r
    return True


# ------------------------------------------------------------------ garrafa de álcool
def alcool():
    RX, RZ, H = 44.0, 29.0, 170.0
    prof = [(0, 0.90), (2, 0.985), (6, 1.0), (30, 1.0), (92, 1.0), (118, 1.0), (124, 1.0), (140, 0.93), (156, 0.66), (166, 0.42), (170, 0.36), (176, 0.36)]

    def f(t, a):
        y, s = prof[min(len(prof) - 1, int(round(t * (len(prof) - 1))))]
        c, sn = math.cos(a), math.sin(a)
        e = 2 / 2.6
        return (RX * s * math.copysign(abs(sn) ** e, sn), y, RZ * s * math.copysign(abs(c) ** e, c))
    corpo = _sup(f, len(prof), 32, 'frasco_claro')
    pintar(corpo, 'rot_branco', lambda c, n: 30 < c[1] < 118 and abs(n[1]) < 0.3)
    pintar(corpo, 'rot_azul', lambda c, n: 92 < c[1] < 118 and abs(n[1]) < 0.3)
    tampa = [lib.lathe([(176, 0), (176, 17.5), (178, 18.5), (196, 18.5), (199, 16.5), (199, 9), (206, 8), (213, 6.5), (214, 0)], 'plastico_verm', n=20, c0=G(0, 0, 0), eixo=G(0, 1, 0))]
    face = lambda x: RZ * max(0.0, 1 - min(1.0, abs(x) / RX) ** 2.6) ** (1 / 2.6) + 0.45

    def colar(o):
        return _mexer(o, lambda x, y, z: (x, y, face(x)))
    txt = [colar(letreiro('ÁLCOOL', 12.5, 0, 100, 0, mat='letra_branca')), colar(letreiro('70 %', 17.0, 0, 68, 0, mat='letra_azul')),
           colar(letreiro('etílico hidratado', 5.0, 0, 58, 0, mat='letra_azul')), colar(letreiro('INFLAMÁVEL', 5.6, 0, 42, 0, mat='letra_vermelha')),
           colar(letreiro('500 ml', 5.0, 0, 34, 0, mat='letra_preta'))]
    raiz = parte('garrafa', [corpo], origem=G(0, 0, 0), grupo='A', suave=40)
    parte('tampa', tampa, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    parte('letras', txt, origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


# ------------------------------------------------------------------ curativo de pano fervido
def _dobra(x0, x1, z0, z1, y0, h, mat, n=24, fase=0.0):
    """Pano dobrado: almofada baixa de bordas arredondadas, com rugas leves."""
    hx, hz, cx, cz = (x1 - x0) / 2, (z1 - z0) / 2, (x0 + x1) / 2, (z0 + z1) / 2

    def f(t, a):
        z = -hz + 2 * hz * t
        k = min(1.0, (hz - abs(z)) / 5.0) ** 0.5
        c, sn = math.cos(a), math.sin(a)
        e = 2 / 5.0
        x = hx * math.copysign(abs(c) ** e, c)
        y = h / 2 * (1 + k * math.copysign(abs(sn) ** e, sn)) + (0.8 * math.sin(x / 9.0 + z / 13.0 + fase) if sn > 0.3 else 0)
        return (cx + x, y0 + y * (0.25 + 0.75 * k) if sn > 0 else y0 + y, cz + z)
    return _sup(f, 18, n, mat)


def curativo_improvisado():
    p = [_dobra(-68, 68, -42, 42, 0, 14, 'pano_cru'), _dobra(-64, 62, -40, 38, 12.5, 13, 'pano_cru', fase=2.0), _dobra(-60, 64, -37, 40, 24, 12, 'pano_cru', fase=4.0)]
    tira = []
    for x in (-8,):                                                                              # tira que amarra o maço
        aneis = []
        for (dx, e_) in ((-9, 0), (9, 0)):
            pass
        pts = [(-44.5, 0.3), (-44.5, 37), (44.5, 37.8), (44.5, 0.3)]
        tira.append(perfil([(-44.6, 0.2), (44.6, 0.2), (44.6, 37.6), (-44.6, 37.6)], x - 9, x + 9, 'pano_cinza'))
        tira.append(lib.lathe([(0, 0), (3, 6), (7, 7), (11, 5), (13, 0)], 'pano_cinza', n=10, c0=G(x - 6, 37.4, 6), eixo=G(1, 0, 0)))   # nó
        tira.append(bevel(caixa(x - 5, x + 3, 37.4, 39, 8, 30, 'pano_cinza'), 0.5, 1))
        tira.append(bevel(caixa(x + 2, x + 9, 37.4, 38.6, -20, 4, 'pano_cinza'), 0.5, 1))
    raiz = parte('panos', p, origem=G(0, 0, 0), grupo='A', suave=50)
    parte('tira', tira, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    return raiz


# ------------------------------------------------------------------ tala de tábua e pano
def tala_improvisada():
    tab = []
    rnd = random.Random(7)
    for s in (-1, 1):
        z0 = s * 34.0
        tab.append(bevel(caixa(-208 + (6 if s > 0 else 0), 208 - (0 if s > 0 else 9), 2.5, 14.5, z0 - 26, z0 + 26, 'pinho_x'), 1.2, 2))
    faixas = []
    for x in (-150, -10, 132):                                                                   # três amarras de pano
        w = 17
        faixas.append(bevel(perfil([(-62.5, 0.0), (62.5, 0.0), (62.5, 17.0), (-62.5, 17.0)], x - w, x + w, 'pano_cru'), 1.6, 2))
        faixas.append(lib.lathe([(0, 0), (4, 8), (10, 9.5), (16, 7), (19, 0)], 'pano_cru', n=10, c0=G(x - 9, 17.0, s * 0 + 10), eixo=G(1, 0, 0)))
        faixas.append(bevel(caixa(x - 6, x + 5, 17.0, 19, 14, 44, 'pano_cru'), 0.7, 1))
        faixas.append(bevel(caixa(x - 2, x + 9, 17.0, 18.6, -26, 8, 'pano_cru'), 0.7, 1))
    acolch = [_dobra(-110, 70, -30, 30, 15.0, 13, 'pano_cinza', fase=1.0),                         # pano dobrado de acolchoar, preso nas amarras
              lib.lathe([(0, 0), (0, 14), (3, 16), (52, 16), (55, 14), (55, 0)], 'gaze', n=18, c0=G(150, 33, -28), eixo=G(0, 0, 1))]   # rolo de tira de reserva
    raiz = parte('tabuas', tab, origem=G(0, 0, 0), grupo='A', suave=40)
    parte('amarras', faixas, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    parte('pano', acolch, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=50)
    return raiz


# ------------------------------------------------------------------ maço de ervas e remédio de ervas
def _folha(base, ponta, larg, mat, dobra=6.0):
    """Folha em lança de base a ponta, com a nervura afundada."""
    b, p = Vector(base), Vector(ponta)
    d = p - b
    lado = d.cross(Vector((0, 1, 0)))
    lado = lado.normalized() if lado.length > 1e-6 else Vector((1, 0, 0))
    aneis = []
    for k in range(8):
        u = k / 7
        w = larg * math.sin(math.pi * (0.06 + 0.9 * u)) ** 0.8
        c = b + d * u + Vector((0, dobra * math.sin(math.pi * u), 0))
        aneis.append([lib.P(*G(*(c - lado * w + Vector((0, 0.35 * w, 0))))), lib.P(*G(*(c - Vector((0, 0.0, 0))))), lib.P(*G(*(c + lado * w + Vector((0, 0.35 * w, 0))))),
                      lib.P(*G(*(c - Vector((0, 0.9, 0)))))])
    return lib.loft(aneis, mat)


def ervas():
    rnd = random.Random(11)
    talos, folhas = [], []
    for k in range(9):
        z = rnd.uniform(-12, 12)
        y = 4 + rnd.uniform(0, 12)
        x1 = rnd.uniform(-10, 40)
        talos.append(cil((-95, 5 + rnd.uniform(0, 8), z * 0.5), (x1, y, z * 1.6), 1.5, 'talo', n=5))
        for j in range(4):
            u = 0.45 + 0.17 * j
            bx = -95 + (x1 + 95) * u
            s = 1 if (j + k) % 2 else -1
            folhas.append(_folha((bx, y * u + 5, z * (0.5 + 1.1 * u)), (bx + rnd.uniform(30, 48), y + rnd.uniform(4, 18), z * 1.6 + s * rnd.uniform(18, 40)), rnd.uniform(8, 12), 'alface' if (j + k) % 3 else 'alface_claro'))
    amarra = [lib.lathe([(0, 8), (0, 11.5), (9, 11.5), (9, 8)], 'sisal', n=14, c0=G(-80, 9.5, 0), eixo=G(1, 0, 0), anel=True),
              lib.fio([G(-76, 20, 0), G(-70, 23, 8), G(-62, 21, 14), G(-66, 20, 4)], 1.1, 'sisal', fechado=True)]
    raiz = parte('talos', talos, origem=G(0, 0, 0), grupo='A', suave=40)
    parte('folhas', folhas, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=60)
    parte('amarra', amarra, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    return raiz


def remedio_ervas():
    R = 20.0
    vidro = lib.lathe([(0, 0), (0, R - 3), (3, R), (44, R), (52, R - 6), (56, 9.5), (68, 9.5), (70, 11), (73, 11), (73, 0)], 'vidro_verde', n=24, c0=G(0, 0, 0), eixo=G(0, 1, 0))
    pintar(vidro, 'cha_verde', lambda c, n: 4 < c[1] < 40 and abs(n[1]) < 0.4)
    rolha = [lib.lathe([(70, 0), (70, 8.6), (82, 9.6), (83, 8.6), (83, 0)], 'rolha', n=14, c0=G(0, 0, 0), eixo=G(0, 1, 0))]
    rot = lib.lathe([(14, R), (14, R + 0.3), (36, R + 0.3), (36, R)], 'papel', n=24, c0=G(0, 0, 0), eixo=G(0, 1, 0), anel=True)
    pintar(rot, 'cha_verde', lambda c, n: c[2] < -4 or c[0] < 0)                                  # rótulo só na frente
    txt = [_na_lata('ERVAS', 7.0, 25, R + 0.55, 'letra_preta'), _na_lata('chá de remédio', 3.2, 18.5, R + 0.55, 'letra_preta')]
    cordao = [lib.lathe([(57, 9.5), (57, 10.9), (59.4, 10.9), (59.4, 9.5)], 'sisal', n=14, c0=G(0, 0, 0), eixo=G(0, 1, 0), anel=True)]
    raiz = parte('vidro', [vidro], origem=G(0, 0, 0), grupo='A', suave=40)
    parte('rolha', rolha + cordao, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    parte('rotulo', [rot], origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    parte('letras', txt, origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


FORMAS = {'kit_medico': kit_medico, 'frasco_remedio': frasco_remedio, 'atadura': atadura, 'seringa': seringa, 'kit_costura': kit_costura, 'alcool': alcool,
          'curativo_improvisado': curativo_improvisado, 'tala_improvisada': tala_improvisada, 'ervas': ervas, 'remedio_ervas': remedio_ervas}
