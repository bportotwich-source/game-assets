"""Lanterna compacta de arma no nível de detalhe da M4A1: garra de trilho lateral, corpo recartilhado,
cabeça com coroa dentada, refletor, vidro e botão de borracha atrás. Desenho próprio, sem marcas.

GASTO = True troca alumínio e aço pelos mesmos materiais bem usados (id "_gasto").

Coordenadas em mm (lib.py da M4A1): u = para a frente, v = para cima, w = direita. A origem é a
face do trilho lateral; a lanterna fica para w positivo, com o eixo em w = 20 (nó `feixe` na frente).
"""
import math
from mathutils import Matrix
from lib import *

GASTO = False
WE, R = 20.0, 13.2        # eixo e raio da cabeça
U0, U1 = -45.0, 31.0


def _m(nome):
    return nome + '_gasto' if GASTO else nome


def _rev(prof, mat, furo=None, n=40, lobes=0.0, lobe_min=0.0):
    if furo is None:
        return lathe(prof, mat, n=n, c0=(0, 0, WE), lobes=lobes, lobe_min=lobe_min)
    return lathe([(prof[0][0], furo)] + list(prof) + [(prof[-1][0], furo)], mat, n=n, c0=(0, 0, WE), lobes=lobes, lobe_min=lobe_min, anel=True)


def lanterna():
    A = _m('anod')
    o = []
    # tampa de trás com o botão de borracha
    o.append(_rev([(U0 + 3, 0), (U0 + 3, 9.6), (U0 + 4, 10.6), (U0 + 13, 10.6), (U0 + 13.6, 9.8)], A, n=40, lobes=0.05, lobe_min=10.5))
    o.append(_rev([(U0, 0), (U0, 5.6), (U0 + 0.8, 6.6), (U0 + 3, 6.8)], 'borracha', n=28))
    # corpo recartilhado
    o.append(_rev([(U0 + 13.6, 9.8), (U0 + 14.2, 10.2), (-6, 10.2), (-5.4, 9.8)], _m('serr'), n=48, lobes=0.045, lobe_min=10.1))
    # pescoço e cabeça
    o.append(_rev([(-5.4, 9.8), (-4, 10.4), (2, 10.4), (6, R - 0.6), (8, R - 0.6), (8.6, R - 1.3), (9.8, R - 1.3), (10.4, R - 0.6),
                   (22, R - 0.6), (22.6, R - 1.2)], A, n=48))
    coroa = _rev([(22.6, R - 1.2), (23.2, R), (U1, R), (U1, R - 1.6), (26.2, R - 2.2)], _m('fosf'), furo=R - 2.9, n=48)
    dentes = []
    for k in range(6):                                                                         # coroa dentada (quebra vidro)
        c = cyl((U1 + 1.2, R + 1, 0), (U1 + 1.2, R - 6, 0), 3.4, A, n=14)
        c.data.transform(Matrix.Translation(P(0, 0, WE)))
        c.data.transform(Matrix.Translation(P(0, 0, WE)) @ Matrix.Rotation(math.radians(60 * k), 4, P(1, 0, 0).normalized()) @ Matrix.Translation(-P(0, 0, WE)))
        dentes.append(c)
    cut(coroa, dentes)
    o.append(coroa)
    # refletor fundo e o LED
    o.append(_rev([(26.0, R - 2.9), (16.0, 3.2), (15.6, 0)], 'refletor', n=40))
    # garra do trilho: braço até a face do trilho, mandíbula e o parafuso de aperto
    o.append(bevel(extr([(0, -9.5), (7.5, -9.5), (9.5, -6), (9.5, 6), (7.5, 9.5), (0, 9.5)], -22, 2, A, plane='wv'), 0.8, 2))
    o.append(bevel(box(-20, 0, -12.6, -9.0, 0, 5.0, A), 0.5, 1))
    o.append(bevel(box(-20, 0, 9.0, 12.6, 0, 5.0, A), 0.5, 1))
    o.append(cyl((-10, 12.6, 3.0), (-10, 15.6, 3.0), 3.4, _m('serr'), n=20, lobes=0.09))         # borboleta de aperto
    o.append(cyl((-10, 15.6, 3.0), (-10, 16.2, 3.0), 1.6, 'inox', n=8))
    o.append(texto('L-300', 2.2, 15.5, 0, WE + R - 0.56, mat='tinta', lado=1))
    m = parte('lanterna', o, origem=(0, 0, 0), grupo='A')
    parte('led', [cyl((15.7, 0, WE), (17.2, 0, WE), 2.6, 'led_frio', n=16)], origem=(0, 0, 0), grupo='A')
    parte('vidro', [cyl((25.6, 0, WE), (26.2, 0, WE), R - 2.95, 'lente_clara', n=40)], origem=(0, 0, 0), grupo='A')
    return m


# ====================================================================== lanternas e lasers de trilho, cano e guarda-mão
# (lanterna_pistola, laser_pistola, combo_lanterna_laser, lanterna_cano_12, lanterna_fuzil, laser_fuzil)
# Cada função devolve a peça "corpo"; as peças de material liso (led, vidro, emissor) entram soltas, como na compacta.

def _torno(prof, mat, v, w, n=40, furo=None, lobes=0.0, lobe_min=0.0):
    """Revolução em volta de um eixo paralelo ao cano, em (v, w). prof = [(u, raio)]."""
    if furo is None:
        return lathe(prof, mat, n=n, c0=(0, v, w), lobes=lobes, lobe_min=lobe_min)
    return lathe([(prof[0][0], furo)] + list(prof) + [(prof[-1][0], furo)], mat, n=n, c0=(0, v, w), lobes=lobes, lobe_min=lobe_min, anel=True)


def _farol(u0, u1, v, w, R, mat='anod', dentes=6, fundo=10.0):
    """Cabeça de lanterna de u0 a u1 (a frente): coroa dentada, refletor fundo. Devolve (peças do corpo, led, vidro)."""
    o = []
    coroa = _torno([(u0, R - 0.6), (u0 + 0.6, R), (u1, R), (u1, R - 1.5), (u1 - 4.6, R - 2.1)], mat, v, w, furo=R - 2.8, n=48)
    if dentes:
        cs = []
        for k in range(dentes):
            c = cyl((u1 + 1.0, R + 1, 0), (u1 + 1.0, R - 5.5, 0), R * 0.25, mat, n=14)
            c.data.transform(Matrix.Translation(P(0, v, w)) @ Matrix.Rotation(math.radians(360.0 / dentes * (k + 0.5)), 4, P(1, 0, 0).normalized()))
            cs.append(c)
        cut(coroa, cs)
    o.append(coroa)
    o.append(_torno([(u1 - 4.8, R - 2.8), (u1 - fundo, 3.0), (u1 - fundo - 0.4, 0)], 'refletor', v, w, n=40))
    led = cyl((u1 - fundo - 0.3, v, w), (u1 - fundo + 1.2, v, w), 2.4, 'led_frio', n=16)
    vidro = cyl((u1 - 5.2, v, w), (u1 - 4.6, v, w), R - 2.85, 'lente_clara', n=40)
    return o, led, vidro


def _emissor(u1, v, w, r, mat='anod', n=20):
    """Janela de laser na frente (em u1): aro saliente com a lente no fundo. Devolve (peças do corpo, lente)."""
    aro = _torno([(u1 - 2.5, r + 1.6), (u1 + 0.8, r + 1.6), (u1 + 0.8, r + 0.6)], mat, v, w, furo=r, n=n)
    return [aro], cyl((u1 - 1.2, v, w), (u1 - 0.4, v, w), r + 0.05, 'lente_laser', n=n)


def _garra_trilho(u0, u1, mat='anod', meia=10.9, aperto=-1):
    """Garra que abraça o trilho curto embaixo do cano (origem na face de baixo do trilho, v = 0)."""
    o = []
    for s in (-1, 1):
        o.append(bevel(extr([(s * meia, -3.0), (s * (meia + 2.9), -3.0), (s * (meia + 2.9), 1.0), (s * (meia + 1.5), 2.6), (s * (meia - 0.9), 2.6),
                             (s * meia, 1.4)][::s], u0, u1, mat, plane='wv'), 0.45, 1))
    um = (u0 + u1) / 2
    o.append(cyl((um, -0.2, -meia - 2.9), (um, -0.2, meia + 2.9), 2.0, 'fosf', n=12))                  # parafuso de travessa (entra na fenda do trilho)
    o.append(cyl((um, -0.2, aperto * (meia + 2.9)), (um, -0.2, aperto * (meia + 6.6)), 4.6, 'serr', n=20, lobes=0.09))     # porca de aperto recartilhada
    o.append(cyl((um, -0.2, aperto * (meia + 6.6)), (um, -0.2, aperto * (meia + 7.2)), 2.0, 'inox', n=8))
    o.append(cyl((um, -0.2, -aperto * (meia + 2.9)), (um, -0.2, -aperto * (meia + 3.7)), 3.0, 'inox', n=6))
    return o


def _aletas(u0, u1, v, w, r0, r1, mat, passo=3.0, n=40):
    """Aletas de resfriamento: discos finos em volta do corpo."""
    o, u = [], u0
    while u + 1.2 <= u1:
        o.append(_torno([(u, r0), (u + 0.25, r1), (u + 1.0, r1), (u + 1.25, r0)], mat, v, w, n=n))
        u += passo
    return o


def _parafuso(u, v, w, eixo, r=2.2, mat='inox'):
    d = {'w+': (0, 0, 1), 'w-': (0, 0, -1), 'v+': (0, 1, 0), 'v-': (0, -1, 0)}[eixo]
    a = (u, v, w)
    b = (u + d[0] * 0.7, v + d[1] * 0.7, w + d[2] * 0.7)
    return cyl(a, b, r, mat, n=6)


def _soltas(led=None, vidro=None, emissor=None):
    if led is not None:
        parte('led', [led], origem=(0, 0, 0), grupo='A')
    if vidro is not None:
        parte('vidro', [vidro], origem=(0, 0, 0), grupo='A')
    if emissor is not None:
        parte('emissor', emissor if isinstance(emissor, list) else [emissor], origem=(0, 0, 0), grupo='A')


def lanterna_pistola():
    """Lanterna de trilho de 600 lm: caixa de alumínio com a pilha atravessada, cabeça redonda e teclas dos dois lados atrás."""
    V, R = -17.0, 13.6
    o = _garra_trilho(-26, -6)
    o.append(bevel(extr(ret_arred(-12.6, 12.6, -29.5, -2.6, 4.0, n=4), -34, 3, 'anod', plane='wv'), 0.6, 2))        # caixa da pilha
    o += [_parafuso(u, -8.0, s * 12.6, 'w+' if s > 0 else 'w-', 1.7, 'fosf') for u in (-28, -4) for s in (-1, 1)]
    o.append(_torno([(3, 12.2), (5, R - 0.6), (6.2, R - 0.6), (6.8, R - 1.4), (8.0, R - 1.4), (8.6, R - 0.6)], 'anod', V, 0, n=48))
    o += _aletas(-1.5, 3.0, V, 0, 11.6, 12.9, 'anod', passo=2.2)
    f, led, vidro = _farol(8.6, 28.0, V, 0, R, 'fosf')
    o += f
    # tampa da pilha atrás, com dobradiça embaixo e trava em cima; teclas de borracha dos dois lados
    o.append(bevel(extr(ret_arred(-11.4, 11.4, -28.3, -4.0, 3.4, n=4), -37.0, -34, 'anod', plane='wv'), 0.5, 1))
    o.append(pin(-35.5, -29.0, 1.5, -8.0, 8.0, 'inox', n=10))
    o.append(bevel(box(-37.6, -34.4, -4.6, -2.2, -3.4, 3.4, 'fosf'), 0.3, 1))
    for s in (-1, 1):
        o.append(bevel(extr([(-47, -24.5), (-37.2, -27), (-37.2, -8), (-47, -10.5)], s * 9.2, s * 13.2, 'borracha'), 0.9, 2))
        for k in range(3):
            o.append(bevel(box(-45.6 + k * 2.8, -44.5 + k * 2.8, -22.5, -12.5, s * 13.0, s * 13.9, 'borracha'), 0.2, 1))
    o.append(texto('L-600', 2.4, -16, -24.5, 12.66, mat='tinta', lado=1))
    o.append(texto('L-600', 2.4, -16, -24.5, -12.66, mat='tinta', lado=-1))
    m = parte('corpo', o, origem=(0, 0, 0), grupo='A')
    _soltas(led, vidro)
    return m


def _etiqueta(u0, u1, v0, v1, w, lado, linhas):
    """Etiqueta amarela de aviso com texto preto, colada num lado (w)."""
    e = 0.35
    o = [bevel(box(u0, u1, v0, v1, min(w, w + lado * e), max(w, w + lado * e), 'rotulo'), 0.1, 1)]
    for (s, tam, v) in linhas:
        o.append(texto(s, tam, (u0 + u1) / 2, v, w + lado * (e + 0.06), mat='tinta_preta', lado=lado))
    return o


def laser_pistola():
    """Mira laser de trilho: caixinha de polímero com a janela do laser na frente, ajustes de latão e botão dos dois lados."""
    V = -17.5
    o = _garra_trilho(-28, -10, 'polim')
    corpo = bevel(extr([(-40, -4), (-40, -21), (-36, -25.6), (4, -25.6), (11, -22.5), (11, -8), (6, -2.6), (-36, -2.6)], -12.0, 12.0, 'polim'), 1.3, 2)
    o.append(corpo)
    a, lente = _emissor(11.0, V, 0, 2.7, 'fosf')
    o += a
    o.append(cyl((2.0, -25.6, 0), (2.0, -26.6, 0), 2.6, 'latao', n=10))                              # ajuste de elevação (embaixo)
    o.append(cyl((2.0, V, 12.0), (2.0, V, 13.0), 2.6, 'latao', n=10))                                # ajuste de deriva (lado direito)
    o.append(bevel(box(1.0, 3.0, -26.7, -26.55, -0.4, 0.4, 'fosf'), 0.05, 1))
    for s in (-1, 1):                                                                                # botões de borracha atrás
        o.append(lathe([(0, 4.6), (1.2, 4.4), (2.0, 3.2), (2.3, 0)], 'borracha', n=18, c0=(-33.5, -14.0, s * 12.0), eixo=(0, 0, s)))
    o.append(cyl((-16.0, -14.0, -12.0), (-16.0, -14.0, -12.8), 7.2, 'polim', n=28))                  # tampa da pilha de moeda
    o.append(bevel(box(-21.0, -11.0, -14.5, -13.5, -13.1, -12.7, 'fosf'), 0.1, 1))
    o += _etiqueta(-24, -6, -22.5, -8.5, 12.0, 1, [('PERIGO', 2.2, -13.0), ('LASER', 2.2, -16.4), ('CLASSE 3', 1.5, -19.6)])
    m = parte('corpo', o, origem=(0, 0, 0), grupo='A')
    _soltas(emissor=lente)
    return m


def combo_lanterna_laser():
    """Lanterna com laser: corpo de alumínio com a cabeça da lanterna em cima e o módulo do laser pendurado embaixo."""
    V, R = -21.0, 12.9
    o = _garra_trilho(-36, -14)
    o.append(bevel(extr(ret_arred(-12.6, 12.6, -31.5, -2.6, 4.2, n=4), -50, 2, 'anod', plane='wv'), 0.6, 2))
    o += [_parafuso(u, -7.0, s * 12.6, 'w+' if s > 0 else 'w-', 1.7, 'fosf') for u in (-44, -6) for s in (-1, 1)]
    o.append(_torno([(2, 12.0), (4, R - 0.6), (5.2, R - 0.6), (5.8, R - 1.4), (7.0, R - 1.4), (7.6, R - 0.6)], 'anod', V, 0, n=48))
    f, led, vidro = _farol(7.6, 27.5, V, 0, R, 'fosf')
    o += f
    # módulo do laser embaixo, mais curto, com a janela na frente
    o.append(bevel(extr([(-30, -30), (-30, -36.5), (-27, -39.0), (-2, -39.0), (1.5, -37.0), (1.5, -30)], -7.6, 7.6, 'anod'), 0.9, 2))
    a, lente = _emissor(1.5, -35.0, 0, 2.2, 'fosf', n=16)
    o += a
    o.append(cyl((-10.0, -35.0, 7.6), (-10.0, -35.0, 8.5), 2.3, 'latao', n=10))
    o.append(cyl((-10.0, -39.0, 0), (-10.0, -39.9, 0), 2.3, 'latao', n=10))
    # atrás: tampa das pilhas e a chave de três posições (lanterna, laser, os dois)
    o.append(bevel(extr(ret_arred(-11.2, 11.2, -30.0, -4.2, 3.6, n=4), -53.0, -50, 'anod', plane='wv'), 0.5, 1))
    o.append(lathe([(0, 6.4), (2.2, 6.4), (2.8, 5.2), (2.8, 0)], 'serr', n=24, c0=(-53.0, -17.0, 0), eixo=(-1, 0, 0), lobes=0.08, lobe_min=6.0))
    o.append(bevel(box(-61.8, -55.6, -19.0, -15.0, -1.3, 1.3, 'fosf'), 0.5, 1))                       # alavanca da chave
    for s in (-1, 1):
        o.append(bevel(extr([(-61, -26.5), (-53.2, -28.5), (-53.2, -22.0), (-61, -21.5)], s * 6.5, s * 12.0, 'borracha'), 0.8, 2))
    o += _etiqueta(-36, -16, -27.5, -15.5, 12.6, 1, [('PERIGO', 2.2, -19.2), ('LASER', 2.2, -22.4), ('CLASSE 3', 1.5, -25.4)])
    o.append(texto('LL-500', 2.4, -26, -9.6, -12.66, mat='tinta', lado=-1))
    m = parte('corpo', o, origem=(0, 0, 0), grupo='A')
    _soltas(led, vidro, lente)
    return m


def lanterna_cano_12():
    """Lanterna de cano da espingarda: abraçadeira de duas voltas (cano e tubo) com a lanterna de 800 lm do lado direito."""
    V, W, R = -3.0, 31.0, 15.8
    o = []
    for (v, r) in ((13.5, 16.0), (-13.5, 14.8)):                                                     # as duas voltas da abraçadeira
        o.append(lathe([(-9, r + 2.6), (-8.2, r + 3.2), (8.2, r + 3.2), (9, r + 2.6), (9, r), (-9, r)], 'anod', n=44, c0=(0, v, 0), anel=True))
    for s in (-1, 1):                                                                                # orelhas e parafusos de aperto, na esquerda
        o.append(bevel(box(-7, 7, s * 1.2, s * 5.2, -24.5, -12.0, 'anod'), 0.6, 1))
    o.append(cyl((0, -6.4, -19.5), (0, 6.4, -19.5), 2.0, 'fosf', n=10))
    o.append(cyl((0, 5.2, -19.5), (0, 7.6, -19.5), 3.6, 'inox', n=6))
    o.append(cyl((0, -5.2, -19.5), (0, -7.4, -19.5), 3.4, 'fosf', n=6))
    # berço da lanterna: braço até o anel que segura o corpo
    o.append(bevel(extr([(12.0, -9.0), (20.0, -12.0), (20.0, 7.0), (12.0, 9.0)], -8, 8, 'anod', plane='wv'), 0.8, 2))
    o.append(lathe([(-8, 15.4), (-7.2, 16.0), (7.2, 16.0), (8, 15.4), (8, 12.6), (-8, 12.6)], 'anod', n=40, c0=(0, V, W), anel=True))
    o.append(cyl((0, V + 15.6, W), (0, V + 19.0, W), 3.2, 'serr', n=16, lobes=0.09))                    # borboleta do anel
    # a lanterna: tampa de trás com botão, corpo recartilhado, aletas e cabeça
    o.append(_torno([(-60, 0), (-60, 10.8), (-59, 11.8), (-47, 11.8), (-46.4, 11.0)], 'anod', V, W, n=40, lobes=0.05, lobe_min=11.7))
    o.append(_torno([(-66, 0), (-66, 7.4), (-64.8, 8.6), (-60, 8.8)], 'borracha', V, W, n=28))
    o.append(_torno([(-46.4, 11.0), (-45.8, 12.6), (-10, 12.6), (-9.4, 11.8)], 'serr', V, W, n=48, lobes=0.045, lobe_min=12.5))
    o.append(_torno([(-9.4, 11.8), (9.4, 11.8), (10, 12.6), (12, 12.6), (17, R - 0.6), (18.2, R - 0.6)], 'anod', V, W, n=48))
    o += _aletas(10.5, 16.5, V, W, 12.8, 15.0, 'anod', passo=2.0)
    f, led, vidro = _farol(18.2, 30.5, V, W, R, 'fosf')
    o += f
    o.append(texto('L-800', 2.6, -28, V, W + 12.56, mat='tinta', lado=1))
    m = parte('corpo', o, origem=(0, 0, 0), grupo='A')
    _soltas(led, vidro)
    return m


def lanterna_fuzil():
    """Lanterna de fuzil de 1000 lm: corpo comprido de duas pilhas, cabeça larga com aletas e suporte de dois parafusos nas fendas."""
    V, W, R = 0.0, 18.5, 14.6
    o = []
    # suporte: sapata nas fendas do guarda-mão e os dois anéis que seguram o corpo
    o.append(bevel(box(-34, 2, -7.0, 7.0, 0, 3.4, 'anod'), 0.7, 2))
    for u in (-28, -4):
        o.append(bevel(box(u - 4.5, u + 4.5, -9.5, 9.5, 2.0, 9.0, 'anod'), 0.8, 2))
        o.append(lathe([(u - 4.5, 14.0), (u - 3.8, 14.6), (u + 3.8, 14.6), (u + 4.5, 14.0), (u + 4.5, 9.5), (u - 4.5, 9.5)], 'anod', n=40, c0=(0, V, W), anel=True))
        o.append(cyl((u, 9.5, 5.6), (u, 10.3, 5.6), 2.6, 'inox', n=6))
        o.append(cyl((u, -9.5, 5.6), (u, -10.3, 5.6), 2.6, 'inox', n=6))
    # tampa de trás com o botão e a argola do cordão
    o.append(_torno([(-62, 0), (-62, 10.2), (-61, 11.4), (-49, 11.4), (-48.4, 10.6)], 'anod', V, W, n=40, lobes=0.05, lobe_min=11.3))
    o.append(_torno([(-68, 0), (-68, 6.8), (-66.8, 8.0), (-62, 8.2)], 'borracha', V, W, n=28))
    # corpo: recartilhado atrás e na frente dos anéis, liso entre eles
    o.append(_torno([(-48.4, 10.6), (-47.8, 11.5), (-46.5, 11.5)], 'anod', V, W, n=48))
    o.append(_torno([(-46.5, 11.5), (-46, 11.95), (-34, 11.95), (-33.5, 11.5)], 'serr', V, W, n=48, lobes=0.04, lobe_min=11.9))
    o.append(_torno([(-33.5, 11.5), (-22.5, 11.5)], 'anod', V, W, n=48))
    o.append(_torno([(-22.5, 11.5), (-22, 11.95), (-10, 11.95), (-9.5, 11.5)], 'serr', V, W, n=48, lobes=0.04, lobe_min=11.9))
    o.append(_torno([(-9.5, 11.5), (4, 11.5), (4.6, 10.8)], 'anod', V, W, n=48))
    # pescoço com aletas e cabeça
    o.append(_torno([(4.6, 10.8), (6, 11.6), (14, 11.6), (18.5, R - 0.6), (19.6, R - 0.6)], 'anod', V, W, n=48))
    o += _aletas(6.5, 14.0, V, W, 11.7, 13.4, 'anod', passo=2.4)
    f, led, vidro = _farol(19.6, 30.5, V, W, R, _m('fosf'), dentes=8, fundo=9.0)
    o += f
    o.append(texto('L-1000', 2.4, -16, V, W + 11.56, mat='tinta', lado=1))
    m = parte('corpo', o, origem=(0, 0, 0), grupo='A')
    _soltas(led, vidro)
    return m


def laser_fuzil():
    """Caixa de laser e luz do lado esquerdo do guarda-mão: laser embaixo, farolete em cima, ajustes de latão e seletor."""
    WL = -25.5
    o = [bevel(box(-36, 22, -8.0, 8.0, -3.4, 0, 'anod'), 0.7, 2)]                                     # sapata nas fendas
    caixa = bevel(extr(ret_arred(-38.5, -3.0, -19.0, 19.5, 4.5, n=4), -46, 31, 'anod', plane='wv'), 0.7, 2)
    o.append(caixa)
    for (v, r, nome) in ((7.0, 6.6, 'luz'), (-7.0, 4.2, 'laser')):                                    # torres dos emissores na frente
        o.append(_torno([(31, r + 2.4), (35.2, r + 2.4), (36, r + 1.7), (36, r + 0.3)], 'fosf', v, WL, furo=r, n=28))
    led = cyl((33.2, 7.0, WL), (34.0, 7.0, WL), 2.4, 'led_frio', n=16)
    vidro = cyl((34.8, 7.0, WL), (35.4, 7.0, WL), 6.62, 'lente_clara', n=28)
    o.append(_torno([(35.0, 6.6), (32.0, 2.6), (31.8, 0)], 'refletor', 7.0, WL, n=28))
    lente = cyl((34.6, -7.0, WL), (35.4, -7.0, WL), 4.22, 'lente_laser', n=24)
    # em cima: seletor de modo recartilhado e o botão de disparo de borracha
    o.append(lathe([(0, 8.2), (4.2, 8.2), (5.0, 7.0), (5.0, 0)], 'serr', n=28, c0=(-24, 19.5, WL + 4), eixo=(0, 1, 0), lobes=0.07, lobe_min=8.0))
    o.append(bevel(box(-25.0, -23.0, 24.4, 25.1, WL + 4.5, WL + 10.5, 'tinta'), 0.1, 1))
    o.append(lathe([(0, 5.6), (1.6, 5.2), (2.6, 3.6), (3.0, 0)], 'borracha', n=18, c0=(4, 19.5, WL + 4), eixo=(0, 1, 0)))
    # ajustes de deriva (esquerda) e elevação (em cima), de latão com fenda
    o.append(cyl((18, -7.0, -38.5), (18, -7.0, -40.0), 3.4, 'latao', n=14))
    o.append(cyl((20, 19.5, WL - 4), (20, 21.0, WL - 4), 3.4, 'latao', n=14))
    # tampa da pilha atrás, recartilhada, com fenda de moeda
    o.append(_torno([(-46, 9.4), (-50, 9.4), (-50.6, 8.4), (-50.6, 0)], 'serr', -3.0, WL + 3, n=32, lobes=0.06, lobe_min=9.0))
    o.append(bevel(box(-50.9, -50.4, -3.6, -2.4, WL - 3, WL + 9, 'fosf'), 0.1, 1))
    # tomada do cabo do botão remoto, com tampão de borracha
    o.append(_torno([(-46, 4.0), (-48.2, 4.0), (-48.8, 3.0), (-48.8, 0)], 'borracha', 12.5, WL - 6, n=18))
    o += [_parafuso(u, v, -38.5, 'w-', 1.9, 'fosf') for u in (-40, 26) for v in (-14.5, 15.0)]
    o += _etiqueta(-22, 6, -15.0, -1.0, -38.5, -1, [('PERIGO', 2.6, -5.0), ('LASER', 2.6, -9.0), ('CLASSE 3', 1.7, -12.6)])
    o.append(texto('CL-2', 3.0, -8, 8.0, -38.56, mat='tinta', lado=-1))
    m = parte('corpo', o, origem=(0, 0, 0), grupo='A')
    _soltas(led, vidro, lente)
    return m
