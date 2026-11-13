"""Sinais de saque (cacos de vidro, louça quebrada, papéis espalhados, cadeira quebrada), pilha de livros e tambor de 200 L no nível realista.

Medidas em mm nas coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente. As medidas de fora são as dos
móveis antigos de props/mobilias; a cadeira quebrada é a cadeira realista (sala) caída de lado sem um pé."""
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
_mover = sala._mover


def _girar_y(o, a, cx=0.0, cz=0.0, dx=0.0, dy=0.0, dz=0.0):
    """Gira em torno do eixo vertical que passa por (cx, cz) e depois desloca."""
    c, s = math.cos(a), math.sin(a)
    return _mover(o, lambda x, y, z: (cx + (x - cx) * c + (z - cz) * s + dx, y + dy, cz - (x - cx) * s + (z - cz) * c + dz))


def _poligono(pts, y0, y1, mat):
    """Contorno visto de cima [(x, z)], com a ordem acertada para a planta."""
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1]))
    return planta(pts if area > 0 else pts[::-1], y0, y1, mat)


# ---------------------------------------------------------------------------- TAMBOR
def tambor_200l():
    R, H = 286, 880
    perf = [(0, 4), (R - 12, 4), (R - 4, 0), (R + 4, 0), (R + 6, 6), (R + 4, 22), (R, 30)]
    for y in (H / 3, 2 * H / 3):                                            # aros de rolagem
        perf += [(R, y - 22), (R + 9, y - 12), (R + 9, y + 12), (R, y + 22)]
    for y in (130, H - 130):                                                # frisos leves
        perf += [(R, y - 8), (R + 3, y), (R, y + 8)]
    perf = sorted(perf[:7], key=lambda t: t[1]) + sorted(perf[7:], key=lambda t: t[1])
    perf += [(R, H - 30), (R + 4, H - 22), (R + 6, H - 6), (R + 4, H), (R - 4, H), (R - 12, H - 6), (0, H - 6)]
    p = [_torno(perf, 'tambor', n=40)]
    p.append(_torno([(0, -0.5), (R + 1, -0.5), (R + 1, 1), (0, 1)], 'ferrugem', n=40))
    for x, z, r in ((170, 0, 30), (-180, 60, 16)):                          # bujões da tampa
        p.append(_torno([(0, 0), (r + 6, 0), (r + 6, 4), (r, 6), (r, 12), (0, 12)], 'zincado', x, H - 7, z, n=14))
        p.append(caixa(x - r * 0.6, x + r * 0.6, H + 4, H + 10, z - 3, z + 3, 'zincado'))
    p.append(_fio([(R + 1, 300, 0), (R + 2, 220, 8), (R + 3, 80, 4)], 3.0, 'ferrugem', res=1))   # escorrido
    parte('tambor', p, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- CACOS DE VIDRO
def cacos_vidro():
    rnd = random.Random(12)
    p = []
    for i in range(55):
        r = abs(rnd.gauss(0, 260))
        a = rnd.uniform(0, 2 * math.pi)
        cx, cz = r * math.cos(a), r * math.sin(a)
        s = rnd.uniform(12, 60) * (2.0 if i < 6 else 1.0)
        n = rnd.randint(3, 5)
        ang = sorted(rnd.uniform(0, 2 * math.pi) for _ in range(n))
        pts = [(cx + s * math.cos(t) * rnd.uniform(0.4, 1.0), cz + s * math.sin(t) * rnd.uniform(0.4, 1.0)) for t in ang]
        y0 = rnd.uniform(0, 1.5) if i > 6 else 0
        p.append(_poligono(pts, y0, y0 + 3, 'vidro_caco'))
    for k in range(2):                                                      # pedaço do caixilho com o vidro preso
        o = [caixa(-250, 250, 0, 30, -22, 22, 'esmalte_branco', 3.0), caixa(-250, -210, 0, 30, -22, 300, 'esmalte_branco', 3.0)]
        o.append(_poligono([(-210, 22), (-60, 22), (-150, 120), (-210, 220)], 13, 16, 'vidro_caco'))
        j = lib.join(o, 'caixilho')
        _girar_y(j, 0.5 + k * 2.4, dx=150 - k * 420, dz=-250 + k * 380)
        p.append(j)
        break
    parte('cacos', p, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- LOUÇA QUEBRADA
def louca_quebrada():
    rnd = random.Random(14)
    p = []
    def caco(cx, cz, a0, a1, r=120, y=0.0):
        arco = [(cx + r * math.cos(t), cz + r * math.sin(t)) for t in [a0 + (a1 - a0) * k / 8 for k in range(9)]]
        miolo = [(cx + rnd.uniform(-8, 8), cz + rnd.uniform(-8, 8))]
        p.append(_poligono(miolo + arco, y, y + 6, 'louca'))
        p.append(lib.join([_poligono([(cx + (r - 2) * math.cos(t0), cz + (r - 2) * math.sin(t0)), (cx + (r - 2) * math.cos(t1), cz + (r - 2) * math.sin(t1)),
                                      (cx + (r - 14) * math.cos(t1), cz + (r - 14) * math.sin(t1)), (cx + (r - 14) * math.cos(t0), cz + (r - 14) * math.sin(t0))], y + 6, y + 6.8, 'ceramica_azul')
                           for t0, t1 in [(a0 + (a1 - a0) * k / 8, a0 + (a1 - a0) * (k + 1) / 8) for k in range(8)]], 'friso'))
    caco(0, 0, 0.3, 2.1); caco(60, 50, 2.4, 3.6, y=6.5); caco(-120, -80, 4.0, 5.2)
    caco(200, -150, 0.0, 1.0, 100); caco(-300, 120, 1.0, 3.0, 100)
    for k in range(20):                                                     # lascas
        cx, cz = rnd.gauss(0, 180), rnd.gauss(0, 180)
        s = rnd.uniform(8, 28)
        p.append(_poligono([(cx, cz), (cx + s, cz + s * 0.3), (cx + s * 0.4, cz + s)], 0, 4, 'louca'))
    x0, z0 = 300, 200                                                       # xícara deitada sem asa
    xi = _torno([(0, 0), (22, 0), (24, 4), (33, 30), (38, 70), (35, 70), (30, 32), (21, 8), (0, 8)], 'louca', 0, 0, 0, n=20)
    _mover(xi, lambda x, y, z: (x0 + y, 36 + x * 0.98, z0 + z))
    p.append(xi)
    p.append(_poligono([(x0 + 60, z0 - 40), (x0 + 80, z0 - 36), (x0 + 74, z0 - 20)], 0, 9, 'louca'))   # a asa solta
    parte('louca', p, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- PAPÉIS ESPALHADOS
def _folha(rnd, texto=True):
    """Folha A4 (210 x 297) com uma ponta levantada e linhas de texto."""
    o = [caixa(-105, 105, 0, 0.5, -148, 60, 'folha_sulfite')]
    dobra = caixa(-105, 105, 0, 0.5, 60, 148, 'folha_sulfite')
    a = math.radians(rnd.uniform(4, 14))
    _mover(dobra, lambda x, y, z: (x, y + (z - 60) * math.sin(a), 60 + (z - 60) * math.cos(a)))
    o.append(dobra)
    if texto:
        for k in range(rnd.randint(6, 11)):                                 # linhas de texto e um carimbo
            z = -120 + k * 16
            if z > 50:
                break
            w = rnd.uniform(90, 170)
            o.append(caixa(-85, -85 + w, 0.5, 0.7, z, z + 5, 'tinta_preta'))
        if rnd.random() < 0.5:
            o.append(caixa(30, 80, 0.5, 0.75, 20, 45, 'carimbo_azul'))
    return lib.join(o, 'folha')


def papeis_espalhados():
    rnd = random.Random(15)
    p = []
    for i in range(14):
        f = _folha(rnd, texto=i % 3 != 0)
        _girar_y(f, rnd.uniform(0, math.pi), dx=rnd.gauss(0, 330), dy=0.6 * i, dz=rnd.gauss(0, 300))
        p.append(f)
    pasta = lib.join([caixa(-120, 120, 0, 2, -160, 160, 'pasta_parda', 0.6), caixa(-120, 120, 2, 3, -160, 150, 'folha_sulfite'),
                      caixa(60, 120, 2, 3.2, 160, 175, 'pasta_parda')], 'pasta')
    _girar_y(pasta, 0.6, dx=-60, dy=9, dz=40)
    p.append(pasta)
    parte('papeis', p, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- CADEIRA QUEBRADA
def cadeira_quebrada():
    pecas = []
    orig = sala.parte
    sala.parte = lambda nome, objs, **k: pecas.append(list(objs))
    try:
        sala.cadeira()
    finally:
        sala.parte = orig
    armacao, assento = pecas
    perna = armacao.pop(6)                                                 # o pé da frente da direita saiu
    lib.bpy.data.objects.remove(perna)
    XF, YA, ZF = 210, 430, 205
    x = XF - 20
    armacao.append(_torno([(0, 0), (19, 0), (18, 30), (12, 52), (15, 64), (8, 80), (0, 90)], 'nogueira_y', x, YA - 90 - 90, ZF - 24, n=12))   # toco lascado
    armacao.append(_torno([(0, 0), (14, 0), (8, 18), (0, 22)], 'lasca', x, YA - 180 - 6, ZF - 24, n=8))
    tudo = armacao + assento
    for o in tudo:                                                          # deita de lado: o lado esquerdo no chão
        _mover(o, lambda a, b, c: (b - 700, XF + 4 + a, c))
    leg = _torno([(0, 0), (11, 0), (13, 6), (13, 16), (10, 24), (13, 70), (18, 200), (19, 250), (12, 262), (16, 270), (6, 282), (0, 290)], 'nogueira_y', 0, 0, 0, n=14)
    _mover(leg, lambda a, b, c: (420 + b, 19 + a * 0.98, 220 + c))           # o pé solto no chão
    tudo.append(leg)
    tudo.append(_torno([(0, 0), (12, 0), (6, 14), (0, 18)], 'lasca', 0, 0, 0, n=8))
    _mover(tudo[-1], lambda a, b, c: (420 + 290 + b, 19 + a, 220 + c))
    parte('cadeira', tudo, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- PILHA DE LIVROS
def pilha_livros():
    rnd = random.Random(91)
    p = []
    y = 0.0
    for k in range(7):
        w, h, d = rnd.uniform(22, 48), rnd.uniform(200, 260), rnd.uniform(150, 190)
        o = sala._livro(w, h, d, f'capa_{k % 6 + 1}', rnd)
        sala._por(o, -h / 2, y + w, d / 2, deitado=True)
        _girar_y(o, rnd.uniform(-0.25, 0.25), dx=rnd.uniform(-15, 15), dz=rnd.uniform(-15, 15))
        p.append(o)
        y += w
    o = sala._livro(30, 230, 170, 'capa_3', rnd)                             # um livro aberto de bruços ao lado
    sala._por(o, -115, 30, 85, deitado=True)
    _girar_y(o, 0.9, dx=230, dz=80)
    p.append(o)
    parte('livros', p, origem=G(0, 0, 0), grupo='A')


FORMAS = {'tambor_200l': tambor_200l, 'cacos_vidro': cacos_vidro, 'louca_quebrada': louca_quebrada, 'papeis_espalhados': papeis_espalhados,
          'cadeira_quebrada': cadeira_quebrada, 'pilha_livros': pilha_livros}
