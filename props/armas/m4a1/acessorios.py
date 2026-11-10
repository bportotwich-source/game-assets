"""Acessórios da M4A1, cada um como peça própria já na posição de montagem.
Desenho próprio, sem marcas de fabricante. Grupos de textura: E (frente),
F (miras, laser), G (coronhas, punho, carregadores)."""
import math
import bpy
from mathutils import Vector
from lib import *
from modelo import LINHA_BAIXO

TRILHO = [(9.6, 20.6), (9.6, 21.6), (7.9, 22.6), (7.9, 24.5), (10.6, 27.25), (7.85, 30)]


def girar(o, phi, cw=0.0, cv=0.0):
    """Gira em torno do eixo do cano; phi > 0 leva o topo para a direita."""
    c, s = math.cos(math.radians(phi)), math.sin(math.radians(phi))
    for v in o.data.vertices:
        dw, dv = v.co.x / MM - cw, v.co.z / MM - cv
        v.co.x = (cw + dw * c + dv * s) * MM
        v.co.z = (cv - dw * s + dv * c) * MM
    return o


def prisma(pts_ut, phi, r0, r1, mat='anod'):
    """Polígono (u, t) extrudado no sentido radial r0..r1 e girado para o ângulo phi."""
    return girar(extr(pts_ut, r0, r1, mat, plane='uw'), phi)


def estadio(u0, u1, larg, n=5):
    r = larg / 2
    return ([(u1 - r + r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in range(-90, 91, 180 // n)] +
            [(u0 + r + r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in range(90, 271, 180 // n)])


def trilho(u0, n, phi, r_base, mat='anod', alt=9.0):
    """Trilho curto de n fendas, com a base apoiada em r_base, no ângulo phi."""
    L = n * 10.008 + 4.8
    sec = [(10.6, 0), (10.6, 2.6), (7.9, alt - 6.6), (7.9, alt - 5.5), (10.6, alt - 2.75), (7.85, alt)]
    sec = [(w, r_base + v) for (w, v) in sec]
    sec = sec + [(-w, v) for (w, v) in reversed(sec)]
    t = extr(sec, u0, u0 + L, mat, plane='wv')
    cut(t, [box(u0 + 4.8 + i * 10.008, u0 + 4.8 + i * 10.008 + 5.23, r_base + alt - 3, r_base + alt + 1, -12, 12, mat)
            for i in range(n)] +
        [cyl((u0 + L * f, r_base + alt - 2.5, 0), (u0 + L * f, r_base + alt + 1, 0), 2.6, mat, n=12) for f in (0.27, 0.73)])
    bevel(t, 0.35, 1, 40)
    p = [cyl((u0 + L * f, r_base + 1.5, 0), (u0 + L * f, r_base + alt - 2.4, 0), 2.3, 'fosf', n=6) for f in (0.27, 0.73)]
    return girar(join([t] + p), phi)


# ------------------------------------------------------------------ frente (grupo E)
def guarda_mao_longo():
    U0, U1 = 4, 336
    meia = [(12, -19), (20, -8), (20, 8), (12, 19)] + TRILHO
    sec = meia + [(-w, v) for (w, v) in reversed(meia)]
    g = extr(sec, U0, U1, 'anod', plane='wv')
    cortes = [cyl((U0 - 5, 0, 0), (U1 + 5, 0, 0), 16.0, 'anod', n=32)]
    cortes += [box(U1 - 4 - i * 10.008 - 5.23, U1 - 4 - i * 10.008, 27, 31, -12, 12, 'anod') for i in range(32)]
    for i in range(7):
        u = 44 + i * 41
        for phi in (90, -90):                                            # fendas laterais
            cortes.append(prisma(estadio(u, u + 32, 7), phi, 12, 26))
        cortes.append(prisma(estadio(u, u + 32, 7), 180, 12, 26))        # fendas de baixo
        for phi in (126, -126):                                          # diagonais de baixo
            cortes.append(prisma(estadio(u + 4, u + 28, 5.5), phi, 12, 28))
    for i in range(13):                                                  # janelas triangulares em cima
        u = 46 + i * 21.5
        tri = [(u, -4.2), (u + 17, -4.2), (u + 8.5, 4.2)] if i % 2 == 0 else [(u, 4.2), (u + 8.5, -4.2), (u + 17, 4.2)]
        for phi in (54, -54):
            cortes.append(prisma(tri, phi, 12, 28))
    cut(g, cortes)
    bevel(g, 0.4, 1, 40)
    o = [g]
    for s in (-1, 1):                                                    # abraçadeira de trás com parafusos
        o.append(bevel(box(8, 30, -24.5, -17, s * 4, s * 13, 'anod'), 0.8, 1))
        for u in (14, 24):
            o.append(cyl((u, -21, s * 12.5), (u, -21, s * 14.6), 2.6, 'fosf', n=6))
    gm = parte('guarda_mao_longo', o, origem=(170, 0, 0), grupo='E')
    parte('porca_cano', lathe([(3, 12.4), (3, 15.4), (26, 15.4), (26, 12.4)], 'fosf', n=24, lobes=0.05, lobe_min=15, anel=True),
          grupo='E')
    bg = [bevel(lathe([(208, 9.5), (208, 12.6), (236, 12.6), (236, 9.5)], 'fosf', n=24, anel=True), 0.6, 1),
          bevel(box(208, 236, 6, 17.6, -5.2, 5.2, 'fosf'), 1.0, 1),
          cyl((214, -13.2, 0), (214, -11, 0), 1.8, 'inox', n=6), cyl((230, -13.2, 0), (230, -11, 0), 1.8, 'inox', n=6)]
    parte('bloco_gas', bg, grupo='E')
    parte('trilho_baixo', trilho(118, 6, 180, 19.0), grupo='E')
    parte('trilho_esquerdo', trilho(262, 5, -90, 20.0), grupo='E')
    return gm


def supressor():
    prof = [(352, 6.4), (352, 13), (355, 16.5), (372, 17.5), (374, 19.5), (452, 19.5), (454, 18.6), (456, 19.5),
            (543, 19.5), (547, 17.2), (547, 9), (544, 9), (544, 4.2), (536, 4.2), (536, 0)]
    s = lathe(prof, 'fosf_escuro', n=36)
    cortes = []
    for i in range(10):
        cortes.append(prisma(estadio(382, 446, 6.5), i * 36, 18.4, 24, 'fosf_escuro'))
    cut(s, cortes)
    bevel(s, 0.5, 1, 40)
    cat = lathe([(346, 6.4), (346, 11.5), (352, 12.8), (352, 6.4)], 'fosf', n=30, lobes=0.08, lobe_min=11, anel=True)
    return parte('supressor', [s, cat], origem=(450, 0, 0), grupo='E')


def empunhaduras():
    # angulada
    fora = [(214, -28), (110, -28), (107, -32), (112, -40), (146, -66), (156, -67), (203, -42), (216, -33)]
    a = extr(fora, -13.5, 13.5, 'polim')
    cut(a, [extr([(190, -34), (128, -34), (150, -58)], -20, 20, 'polim')] +
        [box(160 + i * 6.2, 162.6 + i * 6.2, -80, -20, s * 12.9, s * 20, 'polim') for i in range(6) for s in (-1, 1)])
    bevel(a, 1.8, 2, 35)
    parte('empunhadura_angulada', [a, bevel(box(112, 212, -29.5, -26.5, -11.5, 11.5, 'polim'), 0.6, 1),
                                   pin(124, -31.5, 2.4, -14.3, 14.3, 'fosf', n=6), pin(200, -31.5, 2.4, -14.3, 14.3, 'fosf', n=6)],
          origem=(160, -28, 0), grupo='E')
    # vertical vazada (alumínio)
    f2 = [(170, -28), (132, -28), (130, -40), (118, -98), (121, -104), (146, -104), (150, -98), (158, -62), (172, -40)]
    v = extr(f2, -9, 9, 'anod')
    cut(v, [pin(151, -46, 8.5, -15, 15, 'anod', n=20), pin(142, -66, 7.5, -15, 15, 'anod', n=20),
            pin(136, -85, 6.5, -15, 15, 'anod', n=20)])
    bevel(v, 1.3, 2, 35)
    parte('empunhadura_vertical', [v, bevel(box(130, 172, -30.5, -26.5, -12.5, 12.5, 'anod'), 0.8, 1),
                                   pin(151, -32.5, 4.5, -16.5, -12.4, 'serr', n=18, lobes=0.1)],
          origem=(151, -28, 0), grupo='E')


def lanterna():
    W = -43.0
    corpo = lathe([(248, 0), (248, 9.5), (250, 11.6), (262, 11.6), (263, 10.6), (296, 10.6), (298, 12), (302, 14.8),
                   (322, 14.8), (324, 13.6), (324, 12.2), (320, 12.2), (320, 0)], 'anod', n=28, c0=(0, 0, W))
    cab = lathe([(302, 14.9), (322, 14.9), (322, 14.2), (302, 14.2)], 'anod', n=28, c0=(0, 0, W), lobes=0.04, lobe_min=14.5, anel=True)
    lente = lathe([(319.5, 0), (319.5, 12.2)], 'lente_clara', n=28, c0=(0, 0, W))
    sup = bevel(box(266, 294, -9, 9, -34, -28.6, 'anod'), 1.0, 1)
    botao = lathe([(244.5, 0), (245.5, 5.5), (248, 6.5)], 'borracha', n=16, c0=(0, 0, W))
    parte('lanterna', [corpo, cab, lente, sup, botao,
                       cyl((280, -9, -31), (280, -12.5, -31), 4.2, 'serr', n=16, lobes=0.1)], origem=(285, 0, W), grupo='E')


# ------------------------------------------------------------------ miras e laser (grupo F)
def _anel_suporte(u, vc, r_in, larg=14):
    a = bevel(lathe([(u - larg / 2, r_in), (u - larg / 2, r_in + 4.2), (u + larg / 2, r_in + 4.2), (u + larg / 2, r_in)],
                    'anod', n=28, c0=(0, vc, 0), anel=True), 0.6, 1)
    o = [a]
    for s in (-1, 1):
        o.append(bevel(box(u - larg / 2, u + larg / 2, vc - 2.2, vc + 2.2, s * (r_in + 3), s * (r_in + 8.5), 'anod'), 0.6, 1))
        for du in (-3.5, 3.5):
            o.append(cyl((u + du, vc + 2.2, s * (r_in + 6)), (u + du, vc + 4.2, s * (r_in + 6)), 1.9, 'fosf', n=6))
    return o


def _base_trilho(u0, u1, topo, porcas=2):
    b = extr([(-14.2, 22.6), (-14.2, topo), (14.2, topo), (14.2, 22.6), (11.0, 22.6), (11.0, 30.25), (-11.0, 30.25),
              (-11.0, 22.6)], u0, u1, 'anod', plane='wv')
    bevel(b, 0.8, 1)
    o = [b, bevel(box(u0 + 4, u1 - 4, 22.4, 29.6, -16.4, -14.0, 'anod'), 0.5, 1)]
    for i in range(porcas):
        u = u0 + (u1 - u0) * (i + 0.5) / porcas
        o.append(pin(u, 27.5, 6.2, -21.5, -16.3, 'fosf', n=6))
        o.append(pin(u, 27.5, 2.6, -23, -21.4, 'inox', n=10))
    return o


def luneta():
    VC = 68.0
    prof = [(-206, 16.5), (-206, 21.5), (-203, 22.5), (-172, 22.5), (-168, 21), (-152, 21), (-148, 23.4), (-136, 23.4),
            (-133, 19.5), (-128, 15), (-92, 15), (-90, 18), (-58, 18), (-56, 15), (12, 15), (22, 17), (40, 20.5),
            (72, 20.5), (74, 19.4), (74, 17.6), (66, 17.6), (66, 0)]
    corpo = lathe(prof, 'anod', n=36, c0=(0, VC, 0))
    cut(corpo, [cyl((-212, VC, 0), (-196, VC, 0), 16.5, 'anod', n=28)])
    o = [corpo,
         lathe([(-196.2, 0), (-196.2, 16.5)], 'lente', n=28, c0=(0, VC, 0)),
         lathe([(65.8, 17.6), (65.8, 0)], 'lente', n=28, c0=(0, VC, 0)),
         lathe([(-148, 23.5), (-148, 24.6), (-136, 24.6), (-136, 23.5)], 'serr', n=40, c0=(0, VC, 0), lobes=0.05, lobe_min=24, anel=True),
         bevel(box(-146, -138, VC + 22, VC + 31, -3, 3, 'anod'), 1.0, 1)]                      # alavanca de aumento
    for (eixo, d) in (((0, 1, 0), 1), ((0, 0, 1), 1), ((0, 0, -1), 1)):                       # torres
        e = Vector(eixo)
        p0 = (-74, VC + e.y * 17, e.z * 17)
        p1 = (-74, VC + e.y * 22, e.z * 22)
        p2 = (-74, VC + e.y * 34, e.z * 34)
        o.append(cyl(p0, p1, 12.5, 'anod', n=24))
        o.append(cyl(p1, p2, 11.5, 'serr', n=32, lobes=0.06))
        o.append(cyl(p2, (-74, VC + e.y * 35, e.z * 35), 9, 'anod', n=20))
    l = parte('luneta', o, origem=(-66, VC, 0), grupo='F')
    s = _base_trilho(-150, -8, 36.5, 3)
    for u in (-112, -22):
        s += _anel_suporte(u, VC, 15.1)
        s.append(bevel(extr([(u - 7, 36), (u + 7, 36), (u + 6, VC - 14), (u - 6, VC - 14)], -9, 9, 'anod'), 0.8, 1))
    parte('suporte_luneta', s, origem=(-79, 30.25, 0), grupo='F')
    return l


def mira_prismatica():
    VC = 74.0
    prof = [(-150, 14), (-150, 17.5), (-147, 18.6), (-126, 18.6), (-122, 17), (-64, 17), (-60, 19.5), (-58, 21), (-22, 21),
            (-20, 20), (-20, 18), (-27, 18), (-27, 0)]
    corpo = lathe(prof, 'anod', n=32, c0=(0, VC, 0))
    cut(corpo, [cyl((-156, VC, 0), (-143, VC, 0), 14.5, 'anod', n=24)])
    caixa = bevel(extr([(-114, VC - 18.5), (-114, VC + 16), (-108, VC + 20.5), (-74, VC + 20.5), (-66, VC + 13), (-66, VC - 18.5)],
                       -18.5, 18.5, 'anod'), 2.2, 2, 35)
    o = [corpo, caixa,
         lathe([(-143.2, 0), (-143.2, 14.5)], 'lente', n=24, c0=(0, VC, 0)),
         lathe([(-27.2, 18), (-27.2, 0)], 'lente', n=24, c0=(0, VC, 0)),
         bevel(box(-124, -70, VC - 24, VC - 17, -11, 11, 'anod'), 1.0, 1)]
    for u in (-101, -80):
        o.append(cyl((u, VC + 20, 0), (u, VC + 23, 0), 10.5, 'anod', n=24))
        o.append(cyl((u, VC + 23, 0), (u, VC + 33, 0), 9.8, 'serr', n=28, lobes=0.07))
    o.append(cyl((-92, VC, 18), (-92, VC, 25), 8, 'serr', n=24, lobes=0.06))                    # brilho do retículo
    m = parte('mira_prismatica', o, origem=(-90, VC, 0), grupo='F')
    for nome, u, r, sent in (('tampa_lente_frente', -20, 21.5, 1), ('tampa_lente_tras', -150, 19.5, -1)):
        dz = Vector((sent * 0.30, 0.954))                      # do pivô ao centro do disco aberto (u, v)
        nz = Vector((sent * 0.954, -0.30))                     # normal do disco
        cen = Vector((u, VC + r + 2.5)) + dz * r
        disco = cyl((cen.x - nz.x * 1.2, cen.y - nz.y * 1.2, 0), (cen.x + nz.x * 1.2, cen.y + nz.y * 1.2, 0), r, 'polim', n=28)
        aba = bevel(box(u - 4, u + 4, VC + r - 1, VC + r + 5, -5, 5, 'polim'), 0.8, 1)
        anel = lathe([(u - sent * 0.5, r - 0.6), (u - sent * 0.5, r + 1.4), (u - sent * 7, r + 1.4), (u - sent * 7, r - 0.6)],
                     'polim', n=28, c0=(0, VC, 0), anel=True)
        parte(nome, [disco, aba, anel], origem=(u, VC + r + 2, 0), grupo='F')
    s = _base_trilho(-124, -64, 38, 2)
    s.append(bevel(extr([(-120, 37), (-68, 37), (-72, VC - 23.5), (-116, VC - 23.5)], -11, 11, 'anod'), 1.0, 1))
    cut(s[-1], [box(-108, -80, 41, 46, -15, 15, 'anod')])
    parte('suporte_prismatica', s, origem=(-94, 30.25, 0), grupo='F')
    return m


def mira_reflex():
    U0 = 34.0
    corpo = extr([(0, 0), (46, 0), (46, 25), (36, 29), (22, 20), (20, 11), (0, 11)], -13, 13, 'anod')
    for v in corpo.data.vertices:
        v.co.y += U0 * MM
        v.co.z += 46.5 * MM
    cut(corpo, [box(U0 + 24, U0 + 52, 46.5 + 6, 46.5 + 24, -10, 10, 'anod'),
                box(U0 + 14, U0 + 30, 46.5 + 13, 46.5 + 30, -10, 10, 'anod')])
    bevel(corpo, 1.0, 2, 35)
    lente = extr([(U0 + 41, 52.5), (U0 + 43.5, 70.5), (U0 + 43.9, 70.5), (U0 + 41.4, 52.5)], -10, 10, 'lente')
    o = [corpo, lente, cyl((U0 + 9, 46.5 + 11, 0), (U0 + 9, 46.5 + 13.2, 0), 4.2, 'serr', n=18, lobes=0.1),
         pin(U0 + 12, 52, 3.2, 13, 15, 'serr', n=16, lobes=0.1)]
    mira = join(o)
    girar(mira, 45)
    parte('mira_reflex', mira, grupo='F')
    plat = girar(bevel(box(U0 + 1, U0 + 45, 37, 46.5, -12, 12, 'anod'), 0.8, 1), 45)
    braco = bevel(extr([(-14.2, 22.6), (-14.2, 36), (6, 36), (26, 30), (36, 22), (30, 16), (14.2, 28), (14.2, 22.6), (11, 22.6),
                        (11, 30.25), (-11, 30.25), (-11, 22.6)], U0 + 6, U0 + 40, 'anod', plane='wv'), 0.8, 1)
    parte('suporte_45', [plat, braco, pin(U0 + 23, 27.5, 6.2, -21.5, -14.1, 'fosf', n=6)], grupo='F')


def modulo_laser():
    U0, U1 = 246.0, 326.0
    topo = [(U0, -22), (U0 + 6, -31), (U1 - 10, -31), (U1, -24), (U1, 18), (U1 - 8, 31), (U0 + 20, 31), (U0, 14)]
    c = bevel(extr(topo, 34.5, 58, 'tan', plane='uw'), 2.2, 2, 35)
    o = [c] + [x for x in _base_trilho(U0 + 14, U1 - 14, 35.5, 2)]
    # emissores na frente
    for (w, v, r) in ((-17, 48, 7.2), (-17, 40.5, 3.2), (8, 46, 5.2), (20, 46, 4.2)):
        o.append(cyl((U1 - 0.5, v, w), (U1 + 3.5, v, w), r, 'tan', n=20))
        o.append(cyl((U1 + 3.2, v, w), (U1 + 3.8, v, w), r - 1.3, 'lente', n=16))
    # ajustes em cima, tampa da bateria, botão
    for (u, w) in ((U0 + 24, 14), (U0 + 52, -16)):
        o.append(cyl((u, 58, w), (u, 61.5, w), 5.2, 'tan', n=20, lobes=0.08))
        o.append(cyl((u, 61.5, w), (u, 62.3, w), 2.6, 'latao', n=10))
    o.append(cyl((U0 - 4, 46, 16), (U0 + 2, 46, 16), 9.5, 'tan', n=24, lobes=0.05))
    o.append(lathe([(0, 9), (1.6, 8.6), (3.2, 6), (3.8, 0)], 'borracha', n=18, c0=(U0 + 44, 58, 6), eixo=(0, 1, 0)))
    o.append(bevel(box(U0 + 30, U0 + 62, 39, 54, -31.6, -30.8, 'rotulo'), 0.2, 1))
    o.append(texto('PERIGO', 3.0, U0 + 46, 48.6, -31.66, mat='tinta_preta'))
    o.append(texto('LASER CLASSE 3', 1.9, U0 + 46, 44.8, -31.66, mat='tinta_preta'))
    o.append(texto('RC-15', 2.0, U0 + 46, 41, -31.66, mat='tinta_preta'))
    return parte('modulo_laser', o, origem=((U0 + U1) / 2, 34.5, 0), grupo='F')


# ------------------------------------------------------------------ coronhas, punho, carregadores (grupo G)
def punho_vazado():
    T, B = Vector((-160.0, -56.0)), Vector((-207.0, -146.0))
    L = (B - T).length
    a = (B - T) / L
    e = Vector((-a.y, a.x))
    if e.x < 0:
        e = -e
    q = lambda t, s: tuple(T + a * L * t + e * s)
    fora = [q(-0.25, 19), q(0.28, 19), q(0.34, 22.5), q(0.42, 19), q(0.97, 16.5), q(1.0, 13), q(1.0, -15), q(0.96, -18.5),
            q(0.2, -17.5), q(0.08, -24), q(0.0, -38), q(-0.25, -38)]
    g = extr(fora, -10.5, 10.5, 'anod')
    cut(g, [extr([q(0.13, 12), q(0.36, 13), q(0.36, -11), q(0.18, -11)], -20, 20, 'anod'),
            extr([q(0.43, 12.5), q(0.66, 11.5), q(0.66, -12), q(0.43, -11.5)], -20, 20, 'anod'),
            extr([q(0.73, 11), q(0.92, 10), q(0.92, -12.5), q(0.73, -12)], -20, 20, 'anod'),
            extr([(-110, -55)] + LINHA_BAIXO[2:] + [(-240, -29), (-240, 10), (-110, 10)], -30, 30, 'anod')])
    bevel(g, 1.4, 2, 35)
    return parte('punho_vazado', g, origem=(-160, -56, 0), grupo='G', suave=40)


def _corpo_carregador(meia, R, S0, LT, mat):
    def quadro(s):
        if s <= S0:
            return Vector((-40.0, -22.0 - s)), Vector((1.0, 0.0))
        f = (s - S0) / R
        return Vector((-40.0 + R - R * math.cos(f), -22.0 - S0 - R * math.sin(f))), Vector((math.cos(f), math.sin(f)))
    sec = meia + [(x, -y) for (x, y) in reversed(meia[1:-1])]

    def anel(s, esc=0.0):
        c, e = quadro(s)
        out = []
        for (x, y) in sec:
            q = c + e * (x + math.copysign(esc, x))
            out.append(P(q.x, q.y, y + (math.copysign(esc, y) if abs(y) > 0.01 else 0)))
        return out
    ss = [0, 2] + [S0 * i / 3 for i in range(1, 4)] + [S0 + (LT - S0) * i / 12 for i in range(1, 13)]
    return loft([anel(s) for s in ss], mat), anel, quadro


def _triangular(o):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()


def carregador_polimero():
    meia = [(31, 0.0), (31, 3), (30.2, 4), (30.2, 8.4), (27.2, 11.6), (-27.2, 11.6), (-30.4, 8.4), (-30.4, 3), (-31.6, 2.2), (-31.6, 0.0)]
    R, S0, LT = 300.0, 72.0, 182.0
    corpo, anel, quadro = _corpo_carregador(meia, R, S0, LT, 'polim')
    cortes = [box(-67.5, -12.5, -40, -10, -9.6, 9.6, 'polim')]
    for s in (-1, 1):
        cortes.append(box(-64, -16, -92, -66, s * 10.8, s * 20, 'polim'))             # painel de cima
        for i in range(4):                                                             # painéis de baixo acompanhando a curva
            c, e = quadro(108 + i * 17)
            t = Vector((-e.y, e.x))
            p = [tuple(c + e * x + t * y) for (x, y) in ((-24, -6.5), (24, -6.5), (24, 6.5), (-24, 6.5))]
            cortes.append(extr(p, s * 10.8, s * 20, 'polim'))
    _triangular(corpo)
    cut(corpo, cortes)
    bevel(corpo, 0.5, 1, 40)
    fundo = loft([anel(LT - 0.2), anel(LT, 1.6), anel(LT + 5, 1.6), anel(LT + 6.5, 0.4)], 'polim')
    tr = bevel(extr([(-66.5, -40), (-66.5, -27.5), (-40, -26), (-13.5, -28), (-13.5, -40)], -9.4, 9.4, 'polim_claro'), 1.0, 1)
    return parte('carregador_polimero', [corpo, fundo, tr], origem=(-40, -22, 0), grupo='G')


def carregador_tambor():
    torre = bevel(extr(ret_arred(-11.4, 11.4, -108, -22, 2.5, 3), -70.3, -9.7, 'polim', plane='wv'), 0.4, 1, 60)
    cut(torre, [box(-67.5, -12.5, -40, -10, -9.6, 9.6, 'polim')])
    VC = -140.0
    tb = lathe([(-80, 0), (-80, 16), (-78, 20), (-78, 44), (-74, 51), (-70, 53), (-12, 53), (-8, 51), (-4, 44), (-4, 22),
                (-1, 18), (-1, 0)], 'polim', n=44, c0=(0, VC, 0))
    cortes = []
    for i in range(12):                                                              # nervuras da tampa da frente
        ang = i * 30
        c = box(-6, 4, 26, 42, -3, 3, 'polim')
        for v in c.data.vertices:
            dw, dv = v.co.x / MM, v.co.z / MM
            cs, sn = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            v.co.x = (dw * cs + dv * sn) * MM
            v.co.z = (VC - dw * sn + dv * cs) * MM
        cortes.append(c)
    cut(tb, cortes)
    bevel(tb, 0.8, 1, 35)
    pesc = bevel(box(-72, -8, -112, -84, -18, 18, 'polim'), 3.0, 2, 35)
    alav = [cyl((-80, VC, 0), (-84, VC, 0), 13, 'polim', n=24, lobes=0.08),
            bevel(box(-87, -83.5, VC - 4, VC + 30, -4, 4, 'polim'), 1.0, 1)]
    tr = bevel(extr([(-66.5, -40), (-66.5, -27.5), (-40, -26), (-13.5, -28), (-13.5, -40)], -9.4, 9.4, 'polim_claro'), 1.0, 1)
    return parte('carregador_tambor', [torre, tb, pesc, tr] + alav, origem=(-40, -22, 0), grupo='G', suave=40)


def tubo_vermelho():
    tubo = lathe([(-197, 0), (-197, 14.6), (-230, 14.6), (-232, 15.4), (-389, 15.4), (-393, 13), (-393, 9), (-389, 9), (-389, 0)],
                 'vermelho', n=8)
    girar(tubo, 22.5)
    alma = lathe([(-198, 14.5), (-392, 14.5)], 'vermelho', n=24)
    trilho_ = bevel(box(-391, -232, -22, -12, -4.8, 4.8, 'vermelho'), 0.6, 1)
    cut(trilho_, [cyl((u, -26, 0), (u, -18, 0), 3.2, 'vermelho', n=12) for u in (-262, -290, -318, -346, -374)])
    return parte('tubo_coronha_vermelho', [tubo, alma, trilho_], origem=(-198, 0, 0), grupo='G')


def alavanca_ambi():
    T = [(-170, 6.5), (-197, 6.5), (-199, 10), (-211, 10), (-211, -10), (-199, -10), (-197, -6.5), (-170, -6.5)]
    a = bevel(extr(T, 13.2, 19.2, 'anod', plane='uw'), 0.8, 1)
    o = [a]
    for s in (-1, 1):
        asa = extr([(-196, s * 9), (-198, s * 30), (-203, s * 34), (-211, s * 33), (-213, s * 27), (-207, s * 21), (-206, s * 9)],
                   13.8, 18.6, 'tan', plane='uw')
        cut(asa, [cyl((-203.5, 10, s * 27), (-203.5, 25, s * 27), 2.6, 'tan', n=12)])
        o.append(bevel(asa, 0.7, 1))
        o.append(cyl((-200, 13.4, s * 12), (-200, 19.0, s * 12), 1.3, 'inox', n=10))
    return parte('alavanca_ambi', o, origem=(-198, 16, 0), grupo='G')


def coronha_moderna():
    sec = arco(0, 0, 20.5, 0, 180, 12) + [(-20.5, -8), (-18, -32), (-13, -38), (13, -38), (18, -32), (20.5, -8)]
    luva = extr(sec, -438, -262, 'polim', plane='wv')
    cortes = [cyl((-405, 0, 0), (-250, 0, 0), 15.7, 'polim', n=28), box(-405, -250, -23, -8, -5.4, 5.4, 'polim')]
    for s in (-1, 1):
        for i in range(3):
            u = -292 - i * 34
            cortes.append(girar(extr(estadio(u - 24, u, 6.5), 12, 30, 'polim', plane='uw'), s * 90))       # janelas (mostram o tubo)
        cortes.append(box(-330, -270, 12, 30, s * 17.5, s * 30, 'polim'))                                    # apoio de rosto rebaixado
    cut(luva, cortes)
    bevel(luva, 1.2, 2, 35)
    baixo = extr([(-300, -37), (-340, -37), (-366, -50), (-438, -50), (-444, -120), (-432, -122), (-352, -62), (-306, -47)],
                 -11, 11, 'polim')
    cut(baixo, [extr([(-378, -56), (-432, -56), (-434, -100)], -20, 20, 'polim')])
    bevel(baixo, 1.6, 2, 35)
    tras = extr([(-432, 21), (-446, 19), (-449, -121), (-432, -121)], -18.5, 18.5, 'polim')
    cut(tras, [extr([(-455, v), (-455, v - 9), (-440, v - 4.5)], s * 19.5, s * 10, 'polim') for v in range(8, -112, -13) for s in (-1, 1)])
    bevel(tras, 1.8, 2, 35)
    sol = bevel(extr([(-448.5, 20), (-457, 17.5), (-460, -122), (-448.5, -122)], -18, 18, 'borracha'), 2.4, 2, 35)
    cut(sol, [box(-466, -457.4 + 0.0215 * (v - 17), v - 2.4, v, -15, 15, 'borracha') for v in range(10, -116, -6)])
    qd = [cyl((-420, -22, s * 17.5), (-420, -22, s * 19.6), 7.5, 'fosf', n=20) for s in (-1, 1)]
    for s, c_ in zip((-1, 1), qd):
        cut(c_, [cyl((-420, -22, s * 18.4), (-420, -22, s * 25), 4.6, 'fosf', n=16)])
    c = parte('coronha_moderna', [luva, baixo, tras, sol] + qd, origem=(-262, 0, 0), grupo='G', suave=40)
    tr = bevel(extr([(-301, -46), (-348, -58), (-350, -62), (-338, -63.5), (-303, -55)], -7.2, 7.2, 'polim'), 1.2, 2)
    parte('trava_coronha_moderna', [tr, cyl((-318, -55, 0), (-318, -25, 0), 3.0, 'fosf', n=12)], origem=(-306, -48, 0), grupo='G')
    return c


def coronha_fixa():
    sec = arco(0, 0, 19.4, 0, 180, 12) + [(-19.4, -8), (-16, -22), (-11, -26), (11, -26), (16, -22), (19.4, -8)]
    luva = extr(sec, -440, -233, 'polim', plane='wv')
    cut(luva, [cyl((-405, 0, 0), (-225, 0, 0), 15.7, 'polim', n=28), box(-405, -225, -23, -8, -5.4, 5.4, 'polim')] +
        [girar(extr(estadio(-300 - i * 44, -268 - i * 44, 6), 17.6, 30, 'polim', plane='uw'), s * 90)
         for i in range(3) for s in (-1, 1)])
    bevel(luva, 1.2, 2, 35)
    quadro = extr([(-262, -24), (-440, -24), (-446, -116), (-432, -120)], -9.5, 9.5, 'polim')
    cut(quadro, [extr([(-304, -31), (-424, -31), (-428, -96)], -20, 20, 'polim')])
    bevel(quadro, 2.0, 2, 35)
    tras = bevel(extr([(-434, 20), (-446, 18), (-449, -120), (-434, -120)], -17.5, 17.5, 'polim'), 2.0, 2, 35)
    sol = bevel(extr([(-448.5, 19), (-456, 17), (-459, -121), (-448.5, -121)], -17, 17, 'borracha'), 2.4, 2, 35)
    cut(sol, [box(-466, -456.4 + 0.0215 * (v - 17), v - 2.4, v, -14, 14, 'borracha') for v in range(10, -116, -6)])
    return parte('coronha_fixa', [luva, quadro, tras, sol], origem=(-233, 0, 0), grupo='G', suave=40)


def montar():
    guarda_mao_longo()
    supressor()
    empunhaduras()
    lanterna()
    luneta()
    mira_prismatica()
    mira_reflex()
    modulo_laser()
    punho_vazado()
    carregador_polimero()
    carregador_tambor()
    tubo_vermelho()
    alavanca_ambi()
    coronha_moderna()
    coronha_fixa()
