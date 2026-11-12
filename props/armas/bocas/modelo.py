"""Bocas de cano do jogo (supressores, quebra-chamas, freios e protetores de rosca) no nível de
detalhe da M4A1. Desenho próprio, sem marcas.

Coordenadas em mm (lib.py da M4A1): u = para a frente, v = para cima, w = direita. O eixo do cano é
v = w = 0 e u = 0 é a boca do cano (onde o encaixe da arma fica); a peça avança para u positivo e
abraça a rosca para trás. Mesmas medidas de fora das peças antigas.
"""
import math
from mathutils import Matrix
from lib import *


def _gira(o, graus):
    """Gira a peça em torno do eixo do cano."""
    o.data.transform(Matrix.Rotation(math.radians(graus), 4, P(1, 0, 0).normalized()))
    return o


def _tubo(fora, furo, mat, n=40, lobes=0.0, lobe_min=0.0):
    """Peça de revolução oca: perfil de fora [(u, raio)] e o raio do furo."""
    prof = [(fora[0][0], furo)] + list(fora) + [(fora[-1][0], furo)]
    return lathe(prof, mat, n=n, lobes=lobes, lobe_min=lobe_min, anel=True)


def _radial(u, r, alt, graus, mat='fosf'):
    """Cortador redondo saindo do eixo para fora, no ângulo dado."""
    return _gira(cyl((u, 0, 0), (u, alt, 0), r, mat, n=16), graus)


def _fenda(u0, u1, larg, alt, graus, mat='fosf'):
    return _gira(box(u0, u1, 0, alt, -larg / 2, larg / 2, mat), graus)


def supressor(comp, raio, furo, mat, gasto=False, trava=True):
    A = 'aco_boca_gasto' if gasto else 'aco_boca'
    r = raio
    o = [_tubo([(-6, r - 6.5), (-6, r - 4.2), (0, r - 4.2)], furo + 4.6, A),                    # gola sobre a rosca
         _tubo([(0, r - 2.6), (2, r), (16, r), (17.5, r - 1.0)], furo + 0.4, 'serr', n=48, lobes=0.035, lobe_min=r - 0.1)]
    corpo = [(17.5, r - 1.0), (19, r - 0.2), (comp * 0.5 - 1.2, r - 0.2), (comp * 0.5 - 0.6, r - 0.9), (comp * 0.5 + 0.6, r - 0.9),
             (comp * 0.5 + 1.2, r - 0.2), (comp - 16, r - 0.2), (comp - 15.2, r - 1.0), (comp - 14.4, r - 0.2), (comp - 3, r - 0.2), (comp, r - 3.2),
             (comp, r - 8.0), (comp - 3.5, r - 9.5)]
    o.append(_tubo(corpo, furo + 0.4, mat, n=48))
    o.append(_tubo([(comp - 3.5, r - 9.5), (comp - 3.6, furo + 3.0)], furo + 0.4, 'fuligem', n=32))   # fundo da tampa, sujo de pólvora
    for a in range(0, 360, 60):                                                                 # furos de chave na tampa da frente
        o.append(_gira(cyl((comp - 2.0, r - 5.6, 0), (comp + 0.1, r - 5.6, 0), 1.3, 'fuligem', n=10), a))
    if trava:                                                                                   # trava de engate rápido em cima da gola
        o.append(bevel(extr([(1, r - 1.5), (15, r - 1.5), (13, r + 2.4), (3, r + 2.4)], -4.2, 4.2, 'fosf'), 0.6, 1))
        o.append(pin(8, r + 0.6, 1.5, -5.0, 5.0, 'inox', n=10))
    return parte('boca', o, origem=(0, 0, 0), grupo='A')


def supressor_556_tan():
    return supressor(170, 20.6, 3.4, 'ceramica_tan')


def supressor_762_gasto():
    return supressor(190, 22.6, 4.4, 'aco_boca_gasto', gasto=True, trava=False)


def quebra_chamas_556():
    A = 'aco_boca'
    base = _tubo([(-6, 9.0), (-5, 11.0), (11, 11.0), (12.5, 10.2)], 5.6, A, n=32)
    cut(base, [box(-7, 13, 10.5, 14, -14, 14, A), box(-7, 13, -14, -10.5, -14, 14, A)])          # faces para a chave
    gaiola = _tubo([(12.5, 10.2), (14, 10.5), (51, 10.5), (55, 8.6)], 6.2, A, n=40)
    cut(gaiola, [_fenda(19, 49, 3.0, 14, a) for a in (0, 62, -62, 124, -124)])                   # 5 fendas, fechado embaixo
    bevel(gaiola, 0.3, 1)
    return parte('boca', [base, gaiola, _tubo([(12.4, 6.3), (12.5, 6.3)], 3.3, 'fuligem', n=24)], origem=(0, 0, 0), grupo='A')


def freio_boca_308():
    A = 'aco_boca'
    gola = _tubo([(-12, 9.6), (-11, 11.0), (5, 11.0), (6, 10.4)], 5.9, A, n=32)
    cut(gola, [box(-13, 7, 10.2, 14, -14, 14, A), box(-13, 7, -14, -10.2, -14, 14, A)])
    corpo = bevel(extr(ret_arred(-12.8, 12.8, -11.8, 11.8, 4.5, n=5), 6, 68, A, plane='wv'), 0.9, 2)
    cortes = [cyl((0, 0, 0), (70, 0, 0), 4.7, A, n=24)]
    for u0 in (14, 32, 50):                                                                      # três câmaras abertas para os lados
        cortes.append(bevel(box(u0, u0 + 12, -7.0, 7.0, -20, 20, A), 1.6, 2))
    for u in (20, 38):                                                                           # dois furos em cima seguram a boca no lugar
        cortes.append(cyl((u, 2, 0), (u, 15, 0), 2.0, A, n=14))
    cut(corpo, cortes)
    return parte('boca', [gola, corpo], origem=(0, 0, 0), grupo='A')


def freio_rompimento_12():
    F = 'fosf'
    gola = _tubo([(-19, 13.4), (-18, 14.8), (-1, 14.8), (0, 13.6)], 10.6, F, n=40)
    o = [gola, bevel(box(-15, -5, 13.5, 15.4, -5, 5, F), 0.5, 1), pin(-10, 14.6, 1.8, -6.0, 6.0, 'inox', n=8)]   # abraçadeira e o parafuso
    corpo = _tubo([(0, 13.6), (1.5, 13.6), (28, 13.6), (30, 13.0)], 9.8, F, n=40)
    cut(corpo, [_radial(14, 3.3, 20, a) for a in range(0, 360, 60)])                             # janelas laterais
    o.append(corpo)
    coroa = _tubo([(30, 13.0), (31, 14.8), (42, 14.8)], 10.4, 'inox', n=40)
    dentes = []
    for a in (0, 45, 90, 135):                                                                   # oito dentes
        dentes.append(_gira(extr([(43, -4.6), (43, 4.6), (34.5, 0)], -20, 20, 'inox', plane='uv'), a))
    cut(coroa, dentes)
    o.append(coroa)
    return parte('boca', o, origem=(0, 0, 0), grupo='A')


def protetor_rosca(comp, raio, furo):
    A = 'aco_boca'
    o = [_tubo([(0, raio - 1.2), (1.2, raio - 0.3), (3.5, raio - 0.3), (4, raio - 1.2)], furo, A, n=40),
         _tubo([(4, raio - 1.2), (4.3, raio), (comp - 4.3, raio), (comp - 4, raio - 1.2)], furo, 'serr', n=48, lobes=0.045, lobe_min=raio - 0.1),
         _tubo([(comp - 4, raio - 1.2), (comp - 3.5, raio - 0.3), (comp - 1.0, raio - 0.3), (comp, raio - 1.4)], furo, A, n=40)]
    return parte('boca', o, origem=(0, 0, 0), grupo='A')


def protetor_rosca_308():
    return protetor_rosca(18.0, 11.2, 4.6)


def protetor_rosca_9mm():
    return protetor_rosca(13.8, 9.0, 4.9)
