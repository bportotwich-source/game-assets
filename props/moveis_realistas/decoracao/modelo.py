"""Decoração no nível realista: quadro de família, relógio de parede parado, vaso com planta morta e abajur.

Medidas em mm nas coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente. Os de parede têm a parede
em z = 0 e a base em y = 0, como os antigos de props/mobilias; os de chão têm o pivô no centro da base."""
import math, os, random, importlib.util
import lib
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte, letreiro

_spec = importlib.util.spec_from_file_location('modelo_quarto', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'quarto', 'modelo.py'))
q = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(q)
_torno, _fio, _malha = q._torno, q._fio, q._malha


def _disco(cx, cy, r, n=14, a0=0.0, a1=2 * math.pi, ky=1.0):
    return [(cx + r * math.cos(a0 + (a1 - a0) * k / n), cy + r * ky * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + (0 if a1 - a0 >= 2 * math.pi - 1e-6 else 1))]


def _pessoa(p, x, yc, r, larg, y0, z, roupa):
    """Silhueta de retrato: cabeça, pescoço e ombros até a borda de baixo da foto."""
    p.append(frente(_disco(x, yc, r, 14, ky=1.18), z + 0.15, z + 0.30, 'foto_pele'))
    om = yc - r * 1.55                                                      # altura dos ombros
    corpo = [(x - larg, y0), (x + larg, y0), (x + larg, om - 22)] + _disco(x + larg - 22, om - 22, 22, 4, 0, math.pi / 2)[1:] \
        + [(x + r * 0.45, om + 6), (x - r * 0.45, om + 6)] + _disco(x - larg + 22, om - 22, 22, 4, math.pi / 2, math.pi)
    p.append(frente(corpo, z, z + 0.15, roupa))
    p.append(frente([(x - r * 0.4, om), (x + r * 0.4, om), (x + r * 0.4, yc), (x - r * 0.4, yc)], z + 0.05, z + 0.20, 'foto_pele'))


def quadro_familia():
    X, H = 300, 450
    N = 'nogueira_x'
    m = bevel(caixa(-X, X, 0, H, 0, 30, N), 5.0, seg=2)                      # moldura
    cut(m, caixa(-X + 40, X - 40, 40, H - 40, 6, 40, N))
    f = caixa(-X + 38, X - 38, 38, H - 38, 6, 19, 'dourado')                 # filete dourado por dentro
    cut(f, caixa(-X + 49, X - 49, 49, H - 49, 0, 40, 'dourado'))
    pp = caixa(-X + 44, X - 44, 44, H - 44, 8, 10, 'passepartout')
    cut(pp, caixa(-200, 200, 95, 355, 0, 20, 'passepartout'))
    p = [m, f, pp, caixa(-204, 204, 91, 359, 7, 8.5, 'foto_papel')]
    z = 8.5
    _pessoa(p, -62, 285, 27, 62, 91, z, 'foto_sombra')                       # pai
    _pessoa(p, 58, 277, 25, 55, 91, z + 0.35, 'foto_meio')                   # mãe
    _pessoa(p, -128, 205, 21, 44, 91, z + 0.7, 'foto_meio')                  # filhos na frente
    _pessoa(p, 0, 190, 19, 40, 91, z + 1.05, 'foto_sombra')
    _pessoa(p, 124, 212, 21, 44, 91, z + 0.7, 'foto_sombra')
    parte('quadro', p, origem=G(0, 0, 0), grupo='A')


def _pt(ang, r, cy=160):
    """Ponto do mostrador: ângulo em graus no sentido do relógio a partir do 12."""
    a = math.radians(ang)
    return (r * math.sin(a), cy + r * math.cos(a))


def _ponteiro(ang, r, l0, l1, z, mat, tras=18):
    a, b = _pt(ang + 90, l0 / 2), _pt(ang - 90, l0 / 2)
    tip = _pt(ang, r)
    n = _pt(ang + 90, l1 / 2)
    back = _pt(ang + 180, tras)
    pts = [(a[0] + back[0], a[1] + back[1] - 160), (tip[0] + n[0], tip[1] + n[1] - 160), (tip[0] - n[0], tip[1] - n[1] + 160), (b[0] + back[0], b[1] + back[1] - 160)]
    return frente(pts, z, z + 0.8, mat)


def relogio_parede():
    C = 160
    p = [_torno([(0, 0), (150, 0), (160, 6), (160, 30), (156, 40), (149, 45), (143, 45), (139, 22), (0, 22)], 'plastico_preto', 0, C, 0, n=40, eixo=(0, 0, 1)),
         _torno([(0, 0), (138.5, 0), (138.5, 0.8), (0, 0.8)], 'mostrador', 0, C, 22, n=40, eixo=(0, 0, 1))]
    for k in range(60):                                                     # marcas dos minutos e das horas
        hora = k % 5 == 0
        r0, r1, w = (114, 132, 4.0) if hora else (124, 132, 1.2)
        a, b = _pt(k * 6, r0), _pt(k * 6, r1)
        n = _pt(k * 6 + 90, w / 2)
        n = (n[0], n[1] - C)
        p.append(frente([(a[0] + n[0], a[1] + n[1]), (b[0] + n[0], b[1] + n[1]), (b[0] - n[0], b[1] - n[1]), (a[0] - n[0], a[1] - n[1])], 22.8, 23.1, 'letra_preta'))
    for h in range(1, 13):
        x, y = _pt(h * 30, 96)
        p.append(letreiro(str(h), 24, x, y - 9, 23.0, 'letra_preta'))
    p.append(_ponteiro(98.5, 68, 9, 4, 25.0, 'tinta_preta'))                 # parado às 3:17
    p.append(_ponteiro(102, 112, 6, 2.5, 26.5, 'tinta_preta'))
    p.append(_ponteiro(258, 122, 1.6, 1.0, 28.0, 'ponteiro', tras=30))
    p.append(_torno([(0, 0), (7, 0), (7, 5.5), (4, 7.5), (0, 7.5)], 'latao', 0, C, 23, n=14, eixo=(0, 0, 1)))
    parte('relogio', p, origem=G(0, 0, 0), grupo='A')


def _folha(cx, cy, cz, comp, larg, giro, queda, enrola, mat='folha_seca'):
    """Folha seca: nasce em (cx, cy, cz), aponta para `giro` (graus em volta de y), cai `queda` graus e enrola nas bordas."""
    nu, nv = 5, 3
    g, d = math.radians(giro), math.radians(queda)
    pts = []
    for i in range(nu):
        t = i / (nu - 1)
        w = larg * math.sin(math.pi * (0.12 + 0.88 * t) ** 0.8) * 0.5 + 0.6
        dd = d + enrola * t * t                                             # a ponta dobra mais
        l, h = comp * t * math.cos(dd), -comp * t * math.sin(dd)
        lin = []
        for j in range(nv):
            s = j - 1
            u = s * w
            hh = h + abs(s) * w * 0.55                                      # bordas levantadas
            lin.append((cx + l * math.sin(g) + u * math.cos(g), cy + hh, cz + l * math.cos(g) - u * math.sin(g)))
        pts.append(lin)
    return _malha(pts, nu, nv, mat, esp=0.7)


def vaso_planta_morta():
    T = 'terracota'
    p = [_torno([(0, 0), (150, 0), (162, 5), (170, 28), (161, 28), (154, 12), (0, 12)], T, n=28),                                  # pratinho
         _torno([(0, 12), (110, 12), (116, 20), (158, 288), (172, 290), (175, 296), (175, 346), (170, 355), (154, 355), (150, 349), (150, 316), (0, 316)], T, n=28)]
    parte('vaso', p, origem=G(0, 0, 0), grupo='A')
    rnd = random.Random(11)
    c = [_torno([(0, 0), (150.5, 0), (150.5, 6), (110, 10), (0, 13)], 'terra_seca', 0, 312, 0, n=20)]
    for _ in range(9):                                                      # torrões
        a, r = rnd.uniform(0, 6.28), rnd.uniform(30, 125)
        c.append(_torno([(0, 0), (rnd.uniform(9, 16), 0), (rnd.uniform(5, 9), rnd.uniform(5, 9)), (0, rnd.uniform(7, 10))], 'terra_seca', r * math.cos(a), 320, r * math.sin(a), n=6))
    pontas = []
    for k, (ang, alt, abre) in enumerate(((20, 455, 150), (140, 400, 170), (255, 430, 130), (320, 300, 110))):    # caules secos
        a = math.radians(ang)
        x0, z0 = 22 * math.cos(a), 22 * math.sin(a)
        pts = [(x0, 318, z0)]
        for t in (0.3, 0.6, 0.85, 1.0):
            d = abre * t ** 1.6
            pts.append((x0 + d * math.cos(a) + rnd.uniform(-10, 10), 318 + alt * t - 18 * t * t, z0 + d * math.sin(a) + rnd.uniform(-10, 10)))
        c.append(_fio(pts, 5.0 - k * 0.5, 'galho_seco', res=1))
        for t in (0.45, 0.7, 0.9, 1.0):                                     # raminhos com folha
            i = min(3, int(t * 4))
            b = tuple(pts[i][n] + (pts[i + 1][n] - pts[i][n]) * (t * 4 - i) for n in range(3)) if i < 4 and t < 1 else pts[-1]
            ga = ang + rnd.uniform(-110, 110)
            g = math.radians(ga)
            e = (b[0] + 45 * math.sin(g), b[1] + rnd.uniform(5, 30), b[2] + 45 * math.cos(g))
            c.append(_fio([b, e], 2.0, 'galho_seco', res=1))
            pontas.append((e, ga))
    for e, ga in pontas:
        if rnd.random() < 0.8:
            c.append(_folha(e[0], e[1], e[2], rnd.uniform(110, 160), rnd.uniform(45, 65), ga + rnd.uniform(-25, 25), rnd.uniform(35, 80), rnd.uniform(0.4, 1.1)))
    for _ in range(4):                                                      # folhas caídas na terra
        a, r = rnd.uniform(0, 6.28), rnd.uniform(20, 80)
        c.append(_folha(r * math.cos(a), 326, r * math.sin(a), rnd.uniform(90, 130), rnd.uniform(40, 55), rnd.uniform(0, 360), rnd.uniform(-4, 4), 0.25))
    for _ in range(7):                                                      # e no chão em volta
        a, r = rnd.uniform(0, 6.28), rnd.uniform(185, 225)
        c.append(_folha(r * math.cos(a), 5, r * math.sin(a) * 1.0, rnd.uniform(80, 115), rnd.uniform(38, 52), rnd.uniform(0, 360), rnd.uniform(-5, 3), 0.3))
    parte('planta', c, origem=G(0, 0, 0), grupo='B')


def abajur():
    Lt = 'latao'
    p = [_torno([(0, 0), (72, 0), (76, 4), (76, 16), (62, 22), (50, 38), (58, 60), (84, 105), (95, 160), (92, 215), (72, 270), (44, 315), (32, 338), (30, 348), (0, 348)], 'ceramica_azul', n=28),
         _torno([(0, 346), (34, 346), (36, 350), (30, 358), (11, 362), (9, 366), (9, 430), (17, 434), (18, 438), (18, 470), (15, 474), (0, 474)], Lt, n=16),
         _torno([(0, 472), (11, 472), (13, 480), (22, 500), (30, 520), (30, 532), (22, 548), (8, 556), (0, 557)], 'vidro_lampada', n=16),
         caixa(16, 24, 448, 458, -3, 3, 'plastico_preto', 1.0)]                # interruptor no soquete
    n = 28
    grade = []
    for i in range(n + 1):                                                  # cúpula de tecido
        a = 2 * math.pi * i / n
        grade.append([(r * math.cos(a), y, r * math.sin(a)) for r, y in ((170, 380), (140, 490), (110, 600))])
    cup = [_malha(grade, n + 1, 3, 'cupula', esp=1.6)]
    for r, y in ((170, 381), (110, 599)):                                   # aros debruados
        cup.append(_fio([(r * math.cos(2 * math.pi * i / 20), y, r * math.sin(2 * math.pi * i / 20)) for i in range(20)], 2.6, 'pano_cru', fechado=True, res=1))
    for k in range(3):                                                      # aranha de arame até o soquete
        a = 2 * math.pi * k / 3 + 0.5
        cup.append(_fio([(109 * math.cos(a), 598, 109 * math.sin(a)), (60 * math.cos(a), 592, 60 * math.sin(a)), (19 * math.cos(a), 470, 19 * math.sin(a))], 1.5, Lt, res=1))
    p += cup
    fio = [(0, 9, -74), (4, 5, -110), (30, 4, -190), (70, 4, -260), (60, 4, -340), (88, 4, -400)]      # fio e tomada
    p.append(_fio(fio, 3.0, 'pvc_branco', res=1))
    p.append(caixa(74, 102, 0, 16, -428, -398, 'pvc_branco', 3.0))
    for s in (-1, 1):
        p.append(cil((88 + s * 8, 8, -428), (88 + s * 8, 8, -447), 2.2, Lt, n=8))
    parte('abajur', p, origem=G(0, 0, 0), grupo='A')


FORMAS = {'quadro_familia': quadro_familia, 'relogio_parede': relogio_parede, 'vaso_planta_morta': vaso_planta_morta, 'abajur': abajur}
