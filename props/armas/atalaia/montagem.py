"""Fuzil Atalaia .308 de precisão no nível de detalhe da M4A1: receptores, ferrolho, alavanca,
controles e punho são as peças da própria M4A1 (../m4a1/modelo.py), aumentadas 10 % (o fuzil
.308 é maior que o 5,56 em tudo), em verde-oliva. Guarda-mão octogonal longo com trilho
contínuo e fendas grandes, cano pesado e carregador de caixa de 20 são peças deste arquivo.
Sem coronha e sem miras: coronha de precisão, luneta, miras rebatíveis e freio de boca são
acessórios nos encaixes, como no Atalaia antigo (arma13_precisao.py).

VARIANTE=curto encurta o cano e o guarda-mão.

As peças nascem nas coordenadas da M4A1 (mm), são aumentadas em torno do eixo do cano e levadas
158 mm para a frente: assim o punho e o gatilho caem nos mesmos pontos do Atalaia antigo. O
punho não é aumentado (é o mesmo punho dos outros fuzis), só acompanha o receptor.
"""
import sys, os, math
import bpy
from mathutils import Matrix, Vector
from shapely.geometry import Polygon
from lib import *
import modelo as m4          # ../m4a1/modelo.py (este arquivo não se chama modelo.py para não o esconder)
import acessorios as m4ac

ESC = 1.10
DU = 158.0
VARIANTE = os.environ.get('VARIANTE', '')
CURTO = VARIANTE == 'curto'
U1 = 247.0 if CURTO else 365.0          # ponta do guarda-mão (antes de aumentar): 430 / 560 mm no fuzil pronto
UB = 324.5 if CURTO else 479.1          # ombro da rosca da boca: 515 / 685 mm no fuzil pronto
VERDE = {'anod': 'verde_anod', 'polim': 'verde_polim', 'polim_grip': 'verde_grip'}
PINTADAS = ('receptor_superior', 'receptor_inferior', 'tampa_janela', 'alavanca_manejo', 'guarda_mato', 'punho', 'guarda_mao_oct')
GRUPO_B = ('cano', 'guarda_mao_oct', 'porca_cano', 'bloco_gas', 'carregador_308')


def _filho(o, pai):
    o.parent = pai
    bpy.context.view_layer.update()
    o.matrix_parent_inverse = pai.matrix_world.inverted()


def _gravacao(s, *a, **k):
    """As gravações do receptor da M4A1, com o nome deste fuzil; não há posição AUTO."""
    if s == 'AUTO':
        return box(-150, -149.6, -30, -29.6, -1, 1, 'anod')       # grão escondido dentro do receptor
    return texto({'FUZIL M4A1': 'FUZIL ATALAIA', 'CAL. 5,56 MM': 'CAL. .308', 'RC 104517': 'RC 308771'}.get(s, s), *a, **k)


def guarda_mao():
    """Guarda-mão octogonal flutuante: trilho contínuo em cima, duas fileiras de fendas grandes
    de cada lado, fendas embaixo, abraçadeira atrás e copos de bandoleira."""
    U0 = 4
    oct_ = [(9, -31), (20, -20), (20, 9)]
    meia = oct_ + m4ac.TRILHO
    sec = meia + [(-w, v) for (w, v) in reversed(meia)]
    g = extr(sec, U0, U1, 'anod', plane='wv')
    dentro = Polygon(oct_ + [(9.6, 20.6), (-9.6, 20.6)] + [(-w, v) for (w, v) in reversed(oct_)]).buffer(-2.3, join_style=2)
    cortes = [extr([(float(x), float(y)) for x, y in list(dentro.exterior.coords)[:-1]], U0 - 5, U1 + 5, 'anod', plane='wv')]
    n = int((U1 - U0 - 8) / 10.008)
    cortes += [box(U1 - 4 - i * 10.008 - 5.23, U1 - 4 - i * 10.008, 27, 31, -12, 12, 'anod') for i in range(n)]
    u = 40.0
    while u + 30 < U1 - 22:
        for vc in (3.0, -12.5):                                                         # duas fileiras de cada lado
            cortes.append(extr([(a, b + vc) for (a, b) in m4ac.estadio(u, u + 30, 7.0)], -30, 30, 'anod'))
        cortes.append(m4ac.prisma(m4ac.estadio(u + 2, u + 28, 7.0), 180, 20, 40))       # embaixo
        u += 42.0
    cut(g, cortes)
    bevel(g, 0.4, 1, 40)
    o = [g]
    for s in (-1, 1):
        o.append(bevel(box(8, 30, -36.5, -30, s * 3.5, s * 10.5, 'anod'), 0.8, 1))      # abraçadeira de trás com parafusos
        for uu in (14, 24):
            o.append(cyl((uu, -33.4, s * 10.0), (uu, -33.4, s * 12.2), 2.6, 'fosf', n=6))
        o.append(cyl((U1 - 22, -5, s * 19.4), (U1 - 22, -5, s * 21.2), 4.4, 'inox', n=20))    # copo de bandoleira
        o.append(cyl((U1 - 22, -5, s * 20.9), (U1 - 22, -5, s * 21.4), 2.8, 'fosf', n=16))
    gm = parte('guarda_mao_oct', o, origem=(170, 0, 0), grupo='B')
    parte('porca_cano', lathe([(3, 12.4), (3, 15.4), (26, 15.4), (26, 12.4)], 'fosf', n=24, lobes=0.05, lobe_min=15, anel=True), grupo='B')
    ug = U1 - 112
    bg = [bevel(lathe([(ug, 9.5), (ug, 12.8), (ug + 28, 12.8), (ug + 28, 9.5)], 'fosf', n=24, anel=True), 0.6, 1),
          bevel(box(ug, ug + 28, 6, 16.4, -5.2, 5.2, 'fosf'), 1.0, 1),
          cyl((ug + 6, -13.4, 0), (ug + 6, -11, 0), 1.8, 'inox', n=6), cyl((ug + 22, -13.4, 0), (ug + 22, -11, 0), 1.8, 'inox', n=6),
          cyl((2, 14.6, 0), (ug + 2, 14.6, 0), 1.9, 'inox', n=10)]                       # tubo de gás
    parte('bloco_gas', bg, grupo='B')
    return gm


def cano():
    """Cano pesado de precisão, com coroa rebaixada e rosca na boca (a mesma dos acessórios .308)."""
    prof = [(-16, 0), (-16, 11.0), (-14, 12.6), (-1, 12.6), (-1, 14.6), (2.5, 14.6), (2.5, 12.3), (38, 12.3), (41, 11.0),
            (U1 - 120, 11.0), (U1 - 116, 9.6), (U1 - 80, 9.6), (U1 - 78, 9.0), (UB - 3, 9.0), (UB - 2, 8.4), (UB, 8.4), (UB, 7.6),
            (UB + 13.2, 7.6), (UB + 13.6, 7.0), (UB + 13.6, 5.0), (UB + 12.4, 3.6), (UB - 30, 3.6), (UB - 30, 0)]
    c = lathe(prof, 'fosf', n=32)
    cut(c, [lathe([(UB + 1.2 + i * 1.5, 7.25), (UB + 1.2 + i * 1.5, 9), (UB + 1.9 + i * 1.5, 9), (UB + 1.9 + i * 1.5, 7.25)], 'fosf', n=32, anel=True)
            for i in range(8)])                                                          # filetes da rosca
    return parte('cano', [c], origem=(180, 0, 0), grupo='B')


def carregador():
    """Carregador de caixa .308 de 20: quase reto, de polímero, com painéis rebaixados, nervura
    de trás, base com ressalto e a mesa de cor clara."""
    meia = [(31, 0.0), (31, 3), (30.2, 4), (30.2, 8.4), (27.2, 11.6), (-27.2, 11.6), (-30.4, 8.4), (-30.4, 3), (-31.6, 2.2), (-31.6, 0.0)]
    R, S0, LT = 900.0, 70.0, 132.0
    corpo, anel, quadro = m4ac._corpo_carregador(meia, R, S0, LT, 'polim')
    cortes = [box(-67.5, -12.5, -40, -10, -9.6, 9.6, 'polim')]
    for s in (-1, 1):
        for i in range(3):                                                               # painéis acompanhando a curva
            c, e = quadro(80 + i * 17)
            t = Vector((-e.y, e.x))
            p = [tuple(c + e * x + t * y) for (x, y) in ((-24, -6.5), (20, -6.5), (20, 6.5), (-24, 6.5))]
            cortes.append(extr(p, s * 10.8, s * 20, 'polim'))
    m4ac._triangular(corpo)
    cut(corpo, cortes)
    bevel(corpo, 0.5, 1, 40)
    fundo = loft([anel(LT - 0.2), anel(LT, 1.8), anel(LT + 6, 1.8), anel(LT + 8, 0.4)], 'polim')
    tr = bevel(extr([(-66.5, -40), (-66.5, -27.5), (-40, -26), (-13.5, -28), (-13.5, -40)], -9.4, 9.4, 'polim_claro'), 1.0, 1)
    return parte('carregador_308', [corpo, fundo, tr], origem=(-40, -22, 0), grupo='B')


def _aumentar():
    """Aumenta tudo ESC vezes em torno do eixo do cano (menos o punho, que só acompanha) e leva DU para a frente."""
    bpy.context.view_layer.update()
    pos = {o.name: o.matrix_world.translation.copy() for o in PARTES}
    desl = P(DU, 0, 0)
    topo_punho = P(-160.0, -56.0, 0)
    ordem = sorted(PARTES, key=lambda o: 0 if o.parent is None else 1)
    for o in ordem:
        if o.name == 'punho':
            novo = pos[o.name] + topo_punho * (ESC - 1) + desl
        else:
            o.data.transform(Matrix.Scale(ESC, 4))
            novo = pos[o.name] * ESC + desl
        o.matrix_world = Matrix.Translation(novo)
        bpy.context.view_layer.update()


def montar():
    m4.texto = _gravacao
    sup = m4.receptor_superior()
    for f in (m4.impulsor, m4.tampa_janela, m4.ferrolho, m4.alavanca_manejo):
        _filho(f(), sup)
    inf = m4.receptor_inferior()
    m4.controles(inf)
    m4.punho(inf)
    cano()
    guarda_mao()
    carregador()
    _aumentar()
    for o in PARTES:
        o['grupo'] = 'B' if o.name in GRUPO_B else 'A'
        if o.name in PINTADAS:
            for i, m in enumerate(o.data.materials):
                if m and m.name in VERDE:
                    o.data.materials[i] = M(VERDE[m.name])
    bpy.context.view_layer.update()
