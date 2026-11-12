"""Arremessáveis do jogo no nível de detalhe da M4A1: coquetel molotov, bomba de pregos e isca
sonora (despertador). Desenho próprio, sem marcas.

Coordenadas em mm (lib.py da M4A1): u = para a frente, v = para cima, w = direita. A origem é a
mão. Mesmas medidas, nós (pavio, ponteiros, martelo) e animações dos antigos.
"""
import math
from mathutils import Matrix
from lib import *

CIMA = (0, 1, 0)


def _gira_v(o, graus):
    o.data.transform(Matrix.Rotation(math.radians(graus), 4, P(0, 1, 0).normalized()))
    return o


def _gira_w(o, graus, c=(0, 0, 0)):
    m = Matrix.Translation(P(*c)) @ Matrix.Rotation(math.radians(graus), 4, P(0, 0, 1).normalized()) @ Matrix.Translation(-P(*c))
    o.data.transform(m)
    return o


# ------------------------------------------------------------------ coquetel molotov
def coquetel_molotov():
    # o vidro tem um rebaixo onde vai o rótulo (o papel fica 1,4 mm acima do vidro, senão assa manchado)
    c0 = (0, -90, 0)
    casca = [(0, 0), (0, 30), (2, 33), (5, 34), (55, 34), (56.5, 32.8), (103.5, 32.8), (105, 34), (112, 34), (128, 30), (146, 19), (156, 14.5), (204, 13.4), (206, 15.2), (212, 15.2), (214, 14.0)]
    dentro = [(214, 11.2), (156, 11.6), (146, 16), (128, 27), (112, 31), (6, 31), (4.5, 0)]
    garrafa = parte('rotulo', [lathe([(102, 34.05), (102, 34.2), (58, 34.2), (58, 34.05)], 'papel_rotulo', n=40, c0=c0, eixo=CIMA, anel=True),
                                         lathe([(204.5, 15.3), (204.5, 15.9), (207, 15.9), (207, 15.3)], 'barbante', n=24, c0=c0, eixo=CIMA, anel=True)],
                    origem=(0, 0, 0), grupo='A')
    parte('vidro', [lathe(casca + dentro, 'vidro_garrafa', n=40, c0=c0, eixo=CIMA)], origem=(0, 0, 0), pai=garrafa, grupo='A')
    parte('combustivel', [lathe([(5, 0), (6.5, 30.6), (111, 30.6), (118, 29.5), (118, 0)], 'combustivel', n=40, c0=c0, eixo=CIMA)], origem=(0, 0, 0), pai=garrafa, grupo='A')
    # pavio: pano enfiado no gargalo, com as pontas caindo para fora, e a ponta de cima chamuscada
    p = [lathe([(170, 0), (170, 10.8), (214, 11.0), (224, 13.5), (240, 12.5), (254, 9.0), (261, 4.5), (263, 0)], 'pano_sujo', n=14, c0=c0, eixo=CIMA, lobes=0.12),
         lathe([(248, 11.0), (254, 9.2), (261, 4.7), (263.2, 0.1), (263.4, 0)], 'pano_queimado', n=14, c0=c0, eixo=CIMA, lobes=0.12)]
    for ang, comp in ((20, 62), (150, 48), (265, 70)):
        tira = extr([(13.8, 122), (17.0, 126), (19.5, 118), (20.5, 124 - comp * 0.6), (18.0, 124 - comp), (15.2, 124 - comp * 0.55), (15.6, 112)], -7.5, 7.5, 'pano_sujo', plane='uv')
        p.append(_gira_v(bevel(tira, 0.5, 1), ang))
    parte('pavio', p, origem=(0, 146, 0), pai=garrafa, grupo='A')
    return garrafa


# ------------------------------------------------------------------ bomba de pregos
def bomba_pregos():
    c0 = (0, -55, 0)
    o = [lathe([(0, 0), (0, 36.5), (1.5, 38), (3, 36.8), (4, 37.2), (108, 37.2), (109, 36.8), (110.5, 38), (112, 36.5), (112, 34.5), (110, 34.0), (110, 0)], 'lata', n=44, c0=c0, eixo=CIMA)]
    for k in range(18):                                                                       # pregos de fora, em pé, presos pelas fitas
        a = 20 * k + (7 if k % 2 else 0)
        alt = 6 + (k * 37 % 9)
        o.append(_gira_v(cyl((38.9, -52 + alt * 0.4, 0), (38.9, 44 + alt * 0.5, 0), 1.5, 'prego_velho', n=8), a))
        o.append(_gira_v(cyl((38.9, 44 + alt * 0.5, 0), (38.9, 45.2 + alt * 0.5, 0), 3.2, 'prego_velho', n=10), a))
        o.append(_gira_v(cyl((38.9, -52 + alt * 0.4, 0), (38.9, -56 + alt * 0.4, 0), 1.5, 'prego_velho', n=8, r1=0.2), a))
    for (v0, v1) in ((-36, -12), (16, 40)):                                                    # duas voltas de fita
        o.append(lathe([(v0 + 55, 37.3), (v0 + 55, 41.0), (v1 + 55, 41.0), (v1 + 55, 37.3)], 'fita_cinza', n=44, c0=c0, eixo=CIMA, anel=True))
    for a in (0, 90):                                                                          # fita em cruz na tampa
        o.append(_gira_v(bevel(box(-38.4, 38.4, 56.0, 57.6 + a / 60, -9, 9, 'fita_cinza'), 0.5, 1), a))   # a de cima passa por cima da outra
        for s in (-1, 1):
            o.append(_gira_v(bevel(box(s * 38.2 - 1.6, s * 38.2 + 1.6, 38, 57.6, -9, 9, 'fita_cinza'), 0.5, 1), a))
    lata = parte('lata', o, origem=(0, 0, 0), grupo='A')
    pav = fio([(0, 57.0, 0), (4, 68, 0.5), (11, 79, 1), (19, 88, 2), (26, 95, 3)], 1.6, 'pavio_verde', fechado=False, res=3)
    parte('pavio', [pav], origem=(0, 57.5, 0), pai=lata, grupo='A')
    return lata


# ------------------------------------------------------------------ isca sonora (despertador)
RC, WF, WT = 44.0, 19.0, -18.0        # raio da caixa, face da frente e de trás (o mostrador olha para w positivo)


def _disco(w0, w1, r, mat, n=44, c=(0, 0)):
    return cyl((c[0], c[1], w0), (c[0], c[1], w1), r, mat, n=n)


def isca_sonora():
    E_, C_ = 'esmalte_relogio', 'cromado'
    eixo_w = (0, 0, 1)
    o = [lathe([(WT, 0), (WT, RC - 3), (WT + 2.5, RC), (WF - 4, RC), (WF - 4, 0)], E_, n=52, eixo=eixo_w)]
    o.append(lathe([(WF - 4, RC - 2), (WF - 4, RC + 1.4), (WF + 3.5, RC + 1.4), (WF + 6, RC - 1.5), (WF + 6, RC - 4.5), (WF + 1.5, RC - 4.5)], C_, n=52, eixo=eixo_w, anel=True))  # aro
    o.append(lathe([(WF - 3.9, 0), (WF - 3.9, RC - 2), (WF + 0.2, RC - 4.4), (WF + 0.2, 0)], 'mostrador', n=52, eixo=eixo_w))
    for k in range(60):                                                                       # marcas do mostrador
        hora = k % 5 == 0
        m = box(-0.9 if hora else -0.35, 0.9 if hora else 0.35, RC - (13 if hora else 9.5), RC - 6.5, WF + 0.2, WF + 0.27, 'tinta_preta')
        o.append(_gira_w(m, 6 * k))
    o.append(_disco(WF + 0.2, WF + 3.6, 2.6, C_, n=16))                                        # eixo dos ponteiros
    for s in (-1, 1):                                                                          # pés e campainhas
        o.append(_gira_w(cyl((0, -RC + 4, 0), (0, -RC - 5.5, 0), 3.4, C_, n=14, r1=2.2), s * 28))
        cb = (s * 30.0, 58.0)
        sino = lathe([(0, 0), (0, 4), (3, 17), (9, 21.5), (13, 21.5), (13, 19.8), (9.5, 19.8), (4.5, 15.5), (2, 4), (2, 0)], C_, n=28, c0=(cb[0], cb[1] + 14, 0), eixo=(0, -1, 0))
        o.append(_gira_w(sino, -s * 24, c=(cb[0], cb[1], 0)))
        o.append(_gira_w(cyl((cb[0], RC - 3, 0), (cb[0], cb[1] + 15.5, 0), 1.6, C_, n=10), -s * 24, c=(cb[0], cb[1], 0)))
    alca = [(42 * math.cos(math.radians(a)), 52 + 34 * math.sin(math.radians(a)), 0) for a in range(20, 161, 10)]
    o.append(fio(alca, 1.9, C_, fechado=False, res=3))                                         # alça por cima das campainhas
    o.append(_disco(WT - 6, WT, 5.5, C_, n=10, c=(0, -14)))                                    # chave de dar corda atrás
    o.append(bevel(box(-9, 9, -15.6, -12.4, WT - 9, WT - 6, C_), 0.5, 1))
    o.append(_disco(WT - 4, WT, 3.2, C_, n=14, c=(16, 12)))                                    # botão de acerto
    corpo = parte('caixa', o, origem=(0, 0, 0), grupo='A')
    parte('vidro', [_disco(WF + 4.6, WF + 5.2, RC - 4.55, 'lente_clara', n=52)], origem=(0, 0, 0), pai=corpo, grupo='A')
    # ponteiros (giram no eixo do mostrador): 10 h 10 min, alarme às 7
    def ponteiro(comp, larg, w0, mat, graus):
        return _gira_w(extr([(-larg, -6), (larg, -6), (larg * 0.5, comp), (0, comp + 2), (-larg * 0.5, comp)], w0, w0 + 0.6, mat, plane='uv'), graus)
    parte('ponteiro_horas', [ponteiro(20, 1.8, WF + 1.2, 'ponteiro', 60)], origem=(0, 0, 5), pai=corpo, grupo='A')
    parte('ponteiro_minutos', [ponteiro(30, 1.3, WF + 2.1, 'ponteiro', -60)], origem=(0, 0, 5), pai=corpo, grupo='A')
    parte('ponteiro_alarme', [ponteiro(16, 0.9, WF + 0.5, 'ponteiro_alarme', 150)], origem=(0, 0, 5), pai=corpo, grupo='A')
    # martelinho entre as campainhas
    parte('martelo', [cyl((0, 43, 3), (0, 63, 3), 1.2, 'cromado', n=10), cyl((-4.2, 64.5, 3), (4.2, 64.5, 3), 3.0, 'cromado', n=14)],
          origem=(0, 43, 3), pai=corpo, grupo='A')
    return corpo
