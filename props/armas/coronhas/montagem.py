"""Coronhas de troca no nível de detalhe da M4A1: fixa dos fuzis 5,56 e da espingarda, leve vazada
(tubo de 5 posições), e as coronhas do fuzil 7,62 (polímero, rebatível de tubo, adaptador com a
retrátil e adaptador com a leve). Desenho próprio, sem marcas.

Coordenadas em mm (../m4a1/lib.py): u = para a frente, v = para cima, w = direita. As peças do tubo
nascem nas coordenadas da M4A1 (o tubo começa em u = -197, no fundo do receptor) e a origem de cada
acessório (config.py) é o encaixe_coronha da arma: u = -197 nas coronhas de tubo e u = -165 nas do
fuzil 7,62, onde o adaptador de aço (32 mm) fica entre o receptor e o tubo.
"""
import math, os, importlib.util
import bpy
from shapely.geometry import Polygon, LineString
from lib import *
import modelo as m4               # ../m4a1/modelo.py (este arquivo não se chama modelo.py para não o esconder)

VARIANTE = os.environ.get('VARIANTE', '')
POL = 'tan' if VARIANTE == 'tan' else 'polim'
ACO = 'aco_brasa'
U_AK = -165.0                     # encaixe_coronha do fuzil 7,62 (face de trás do receptor)


def _brasa():
    """Os ajudantes de forma do Brasa (arred, solido, corpo_u...) sem esconder o modelo.py da M4A1."""
    aqui = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    spec = importlib.util.spec_from_file_location('brasa_modelo', os.path.join(aqui, 'brasa', 'modelo.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


B = _brasa()
arred, solido, corpo_u, lados, smooth, capsula = B.arred, B.solido, B.corpo_u, B.lados, B.smooth, B.capsula


def _grupo(g='A'):
    for o in PARTES:
        o['grupo'] = g


# ------------------------------------------------------------------ tubo de 5 posições (o da M4A1)
def tubo(u0=-197.0):
    """Tubo, placa traseira e porca castelo. u0 = onde o tubo encosta (a rosca entra 12 mm)."""
    tb = lathe([(u0 + 12, 0), (u0 + 12, 13.2), (u0, 13.2), (u0, 14.6), (-391, 14.6), (-393, 13.4), (-393, 0)], 'anod_tubo', n=32)
    trilho = bevel(box(-391, -232, -21.5, -12, -4.8, 4.8, 'anod_tubo'), 0.6, 1)
    cut(trilho, [cyl((u, -25, 0), (u, -17, 0), 3.2, 'anod_tubo', n=12) for u in (-262, -290, -318, -346, -374)])
    t = parte('tubo_coronha', [tb, trilho], origem=(u0, 0, 0))
    placa = extr(superelipse(16.5, 24.5, n=28, e=3.2, cy=-6), -216.6, -213.1, 'fosf', plane='wv')
    cut(placa, [cyl((-220, 0, 0), (-210, 0, 0), 14.7, 'fosf', n=28)])
    parte('placa_traseira', bevel(placa, 0.6, 1), pai=t)
    porca = lathe([(-229, 14.7), (-229, 18.2), (-224, 18.2), (-223.5, 19.8), (-216.7, 19.8), (-216.7, 14.7)],
                  'fosf', n=36, lobes=0.085, lobe_min=19, anel=True)
    parte('porca_castelo', porca, pai=t)
    return t


# ------------------------------------------------------------------ coronha fixa (fuzil 5,56 e espingarda)
def coronha_fixa():
    """Coronha fixa inteiriça de polímero: corpo oco por dentro (só a casca), apoio de rosto reto,
    porta do compartimento na soleira, zarelho embaixo e soleira de borracha nervurada.
    A soleira encosta no ombro 338 mm atrás do encaixe."""
    U0, UB, US = -197.0, -521.0, -535.0          # frente, fim do corpo, fim da soleira
    perfil = arred([(U0, 15.5), (-230, 17.5), (UB, 19.5), (UB, -121), (-505, -124), (-470, -114), (-300, -54),
                    (-222, -30), (U0, -27)], 3.0, 5)
    larg = lambda u: 15.8 + 2.8 * smooth(-215, -480, u)
    c = corpo_u(perfil, larg, POL, e=2.6, n=96, voltas=44)
    cs = [cyl((U0 + 5, 0, 0), (U0 - 40, 0, 0), 13.4, POL, n=28)]                              # o tubo de rosca entra aqui
    for s in (-1, 1):                                                                         # painéis rebaixados dos lados (2 mm ou mais)
        a, b = lados(s, 14.0, 30)
        cs.append(solido(arred([(-262, -8), (-452, -2), (-452, -78), (-300, -40), (-262, -26)], 7.0, 6), a, b, POL))
    cut(c, cs)
    o = [bevel(c, 0.8, 2, 36)]
    o.append(lathe([(U0 + 12, 0), (U0 + 12, 13.2), (U0 - 4, 13.2), (U0 - 4, 0)], 'anod_tubo', n=28))   # rosca que entra no receptor
    o.append(lathe([(U0 + 0.6, 13.2), (U0 + 0.6, 17.6), (U0 - 4.0, 17.6), (U0 - 4.0, 13.2)], 'fosf', n=36, lobes=0.06, lobe_min=17, anel=True))
    sol = corpo_u(arred([(UB + 0.5, 19.0), (US + 2, 17.6), (US, -118), (UB + 0.5, -121.5)], 2.0, 4), lambda u: larg(UB) - 0.2, 'borracha', e=2.8, n=10, voltas=44)
    cut(sol, [box(US - 6, US + 1.4 + 0.012 * (v - 17), v - 2.2, v, -16, 16, 'borracha') for v in range(10, -112, -6)])
    o.append(sol)
    porta = solido(arred([(UB + 1.2, -18), (UB + 1.2, -62), (UB - 0.6, -62), (UB - 0.6, -18)], 0.4, 2), -10.5, 10.5, 'fosf')
    o.append(porta)
    for v in (-10, -110):                                                                     # parafusos da soleira
        pf = lathe([(0, 0), (0, 3.4), (0.8, 3.4), (1.3, 2.6), (1.3, 0)], 'inox', n=14, c0=(US + 0.4, v, 0), eixo=(-1, 0, 0))
        cut(pf, [box(US - 3, US - 0.4, v - 4, v + 4, -0.5, 0.5, 'inox')])
        o.append(pf)
    uz, vz = -470.0, -114.0                                                                   # zarelho embaixo
    o.append(bevel(solido(arred([(uz - 15, vz - 1.0), (uz + 15, vz + 9.0), (uz + 14, vz + 12.5), (uz - 16, vz + 2.6)], 1.2, 3), -6.0, 6.0, 'fosf'), 0.5, 1, 40))
    o.append(fio(caminho_arred([(uz - 4, vz + 1, -8.5), (uz - 10, vz - 15, -8.5), (uz - 10, vz - 15, 8.5), (uz - 4, vz + 1, 8.5)], 3.0, 4, fechado=False),
                 1.6, 'fosf', fechado=False))
    return parte('coronha', o, origem=(U0, 0, 0), suave=36)


def montar_fixa():
    coronha_fixa()
    _grupo()


# ------------------------------------------------------------------ coronha leve vazada (corre no tubo)
def corpo_leve(nome='coronha'):
    """Coronha leve: luva sobre o tubo, quadro de baixo vazado em triângulo, apoio de rosto com
    janelas, trava embaixo e soleira de borracha. Nasce estendida 0 mm (encostada na porca)."""
    sec = arco(0, 0, 19.8, 0, 180, 12) + [(-19.8, -6), (-17.2, -27), (-13, -33), (13, -33), (17.2, -27), (19.8, -6)]
    luva = extr(sec, -443, -268, POL, plane='wv')
    cs = [cyl((-410, 0, 0), (-258, 0, 0), 15.1, POL, n=28), box(-410, -258, -22.5, -8, -5.4, 5.4, POL)]
    for s in (-1, 1):
        for i in range(3):                                                                   # janelas que mostram o tubo
            u = -296 - i * 36
            cs.append(solido(capsula(u - 22, u, 2.0, 4.2), *lados(s, 12, 30), POL))
        cs.append(box(-436, -398, 7.5, 13, s * 17.4, s * 26, POL))                           # canal da bandoleira de cima
    cut(luva, cs)
    o = [bevel(luva, 1.1, 2, 35)]
    fora = arred([(-300, -30), (-446, -30), (-446, -121), (-433, -121)], 3.0, 5)
    vao = arred([(-338, -40), (-431, -40), (-431, -104)], 6.0, 6)
    q = solido(fora.difference(vao), -8.5, 8.5, POL)
    cut(q, [solido(arred([(-420, -52), (-412, -52), (-412, -38), (-420, -38)], 2.4, 4), -30, 30, POL)])   # passador da bandoleira
    o.append(bevel(q, 1.4, 2, 35))
    tras = extr([(-433, 19.8), (-446, 18.2), (-447, -121), (-433, -121)], -17.0, 17.0, POL)
    cut(tras, [extr([(-455, v), (-455, v - 8), (-441, v - 4)], s * 18, s * 9.5, POL) for v in range(4, -112, -14) for s in (-1, 1)])
    o.append(bevel(tras, 1.8, 2, 35))
    sol = extr([(-446.5, 19), (-459, 16.5), (-461, -121.5), (-446.5, -121.5)], -17.5, 17.5, 'borracha')
    bevel(sol, 2.2, 2, 35)
    cut(sol, [box(-466, -459.6 + 0.012 * (v - 17), v - 2.2, v, -14.5, 14.5, 'borracha') for v in range(10, -114, -5)])
    o.append(sol)
    c = parte(nome, o, origem=(-268, 0, 0), suave=38)
    tr = bevel(extr([(-299, -33), (-344, -33), (-346, -36), (-333, -38.5), (-303, -41.5), (-298, -39)], -7.2, 7.2, POL), 1.2, 2)
    parte('trava_coronha', [tr, cyl((-318, -40, 0), (-318, -25, 0), 3.0, 'fosf', n=12), pin(-306, -35, 1.4, -9.3, 9.3, 'inox', n=8)],
          origem=(-306, -35, 0), pai=c)
    return c


def montar_leve():
    tubo()
    corpo_leve()
    _grupo()


# ------------------------------------------------------------------ fuzil 7,62
def adaptador():
    """Adaptador de aço do 7,62 para o tubo: chapa que entra no receptor, bloco com o furo de rosca
    e dois parafusos de cada lado. Vai de U_AK (encaixe) até u = -197, onde o tubo encosta."""
    o = [bevel(solido(arred([(U_AK - 1, -37.5), (U_AK + 6, -37.5), (U_AK + 6, 11.4), (U_AK - 1, 11.4)], 1.5, 4), -13.4, 13.4, ACO), 0.6, 2, 40)]
    blk = corpo_u(arred([(U_AK - 0.5, 16.0), (-197.5, 16.5), (-197.5, -22), (-185, -36.5), (U_AK - 0.5, -36.5)], 2.5, 5),
                  lambda u: 14.6, ACO, e=3.2, n=24, voltas=36)
    o.append(bevel(blk, 0.6, 2, 36))
    for s in (-1, 1):
        for (u, v) in ((-175, 4), (-175, -24)):
            pf = lathe([(-0.4, 3.3), (1.2, 3.3), (1.8, 2.5), (1.8, 0)], 'fosf', n=16, c0=(u, v, s * 14.4), eixo=(0, 0, s))
            cut(pf, [cyl((u, v, s * 15.4), (u, v, s * 17), 1.4, 'fosf', n=6)])
            o.append(pf)
    return parte('adaptador', o, origem=(U_AK, 0, 0))


def montar_retratil_ak():
    adaptador()
    m4.coronha()                                           # tubo, placa, porca e o corpo retrátil da M4A1
    _grupo()


def montar_leve_ak():
    adaptador()
    tubo()
    corpo_leve()
    _grupo()


def coronha_polimero():
    """Coronha fixa de polímero do 7,62 no desenho da de madeira (mesma queda), com painel
    rebaixado dos lados, chapa de encaixe de aço e soleira de borracha."""
    E = U_AK
    perfil = arred([(E, 12), (E - 30, 12), (E - 200, 2), (E - 319, -10), (E - 328, -13.5), (E - 330, -23), (E - 330, -120), (E - 325, -130),
                    (E - 295, -125), (E - 180, -89), (E - 60, -48), (E - 10, -36), (E, -35)], 3.0, 5)
    larg = lambda u: 12.6 + 7.2 * smooth(E - 10, E - 220, u)
    c = corpo_u(perfil, larg, 'polim', e=2.6, n=96, voltas=40)
    pain = arred([(E - 130, -8), (E - 272, -12), (E - 272, -100), (E - 200, -80), (E - 130, -52)], 8.0, 6)
    cs = [solido(pain, *lados(s, 15.0, 40), 'polim') for s in (-1, 1)]                        # rebaixo de 2 a 4,8 mm
    cut(c, cs)
    o = [bevel(c, 0.9, 2, 36)]
    sol = corpo_u(arred([(E - 329.5, 9), (E - 344, 7.5), (E - 344, -125), (E - 329.5, -128)], 2.2, 4), lambda u: larg(E - 329) + 0.3, 'borracha', e=2.8, n=10, voltas=40)
    cut(sol, [box(E - 349, E - 342.6, v, v + 2.4, -20, 20, 'borracha') for v in range(-118, 4, 7)])
    o.append(sol)
    o.append(bevel(solido(arred([(E - 7, -36.5), (E + 6, -36.5), (E + 6, 13), (E - 7, 13)], 1.5, 4), -13.4, 13.4, ACO), 0.6, 2, 40))   # chapa de encaixe
    aneis = []                                                                                # espiga de cima
    for i in range(21):
        u = E - 2 - 58.0 * i / 20
        vt = perfil.intersection(LineString([(u, -400), (u, 200)])).bounds[3]
        aneis.append([P(u, vt - 3.0, -4.4), P(u, vt + 1.7, -4.4), P(u, vt + 1.7, 4.4), P(u, vt - 3.0, 4.4)])
    o.append(bevel(loft(aneis, ACO), 0.5, 1, 40))
    for u in (E - 20, E - 46):
        vt = perfil.intersection(LineString([(u, -400), (u, 200)])).bounds[3]
        pf = lathe([(0, 0), (0, 2.9), (0.6, 2.9), (0.95, 2.2), (0.95, 0)], 'inox', n=14, c0=(u, vt + 1.6, 0), eixo=(0, 1, 0))
        cut(pf, [box(u - 4, u + 4, vt + 2.1, vt + 4, -0.5, 0.5, 'inox')])
        o.append(pf)
    for v in (-20, -112):                                                                     # parafusos da soleira
        pf = lathe([(0, 0), (0, 3.2), (0.8, 3.2), (1.2, 2.4), (1.2, 0)], 'inox', n=14, c0=(E - 343.8, v, 0), eixo=(-1, 0, 0))
        cut(pf, [box(E - 347, E - 344.3, v - 4, v + 4, -0.5, 0.5, 'inox')])
        o.append(pf)
    uz = E - 250                                                                              # zarelho da bandoleira
    vz = perfil.intersection(LineString([(uz, -400), (uz, 200)])).bounds[1]
    o.append(bevel(solido(arred([(uz - 16, vz - 1.6), (uz + 16, vz + 10.2), (uz + 15, vz + 13.4), (uz - 17, vz + 1.6)], 1.2, 3), -6.5, 6.5, ACO), 0.5, 1, 40))
    o.append(fio(caminho_arred([(uz - 7, vz + 2, -9), (uz - 12, vz - 13, -9), (uz - 12, vz - 13, 9), (uz - 7, vz + 2, 9)], 3.0, 4, fechado=False),
                 1.5, ACO, fechado=False))
    return parte('coronha', o, origem=(E, 0, 0), suave=34)


def montar_polimero_ak():
    coronha_polimero()
    _grupo()


def coronha_rebativel():
    """Coronha de tubo de aço que dobra para a esquerda: base presa ao receptor com a dobradiça
    do lado esquerdo (nó "dobra", eixo em pé) e o quadro de tubos com a soleira de borracha."""
    E = U_AK
    HU, HW = E - 12.0, -13.5                                                                  # eixo da dobradiça
    o = [bevel(solido(arred([(E - 7, -37.5), (E + 6, -37.5), (E + 6, 11.4), (E - 7, 11.4)], 1.5, 4), -13.4, 13.4, ACO), 0.6, 2, 40)]
    for (v0, v1) in ((-2, 10), (-34, -22)):                                                   # orelhas da dobradiça (a base)
        o.append(bevel(solido(arred([(E - 6.5, v0), (HU - 6.5, v0), (HU - 6.5, v1), (E - 6.5, v1)], 2.0, 4), -13.4, -4, ACO), 0.5, 1, 40))
        o.append(cyl((HU, v0, HW), (HU, v1, HW), 6.4, ACO, n=24))
    o.append(cyl((HU, 12.6, HW), (HU, -36.6, HW), 2.6, 'inox', n=14))                         # pino da dobradiça
    o.append(lathe([(0, 0), (0, 3.4), (0.9, 3.4), (1.3, 2.6), (1.3, 0)], 'inox', n=14, c0=(HU, 12.0, HW), eixo=(0, 1, 0)))
    o.append(bevel(solido(arred([(E - 6.5, -20), (E - 2, -20), (E - 2, -4), (E - 6.5, -4)], 1.5, 3), 4, 13.4, ACO), 0.5, 1, 40))   # dente da trava (direita)
    parte('base', o, origem=(E, 0, 0))

    q = [cyl((HU, -21.6, HW), (HU, -2.4, HW), 6.6, ACO, n=24)]                                # olhal do quadro (entre as orelhas)
    q.append(bevel(solido(arred([(HU + 4, -21.6), (HU - 26, -21.6), (HU - 26, -2.4), (HU + 4, -2.4)], 3.0, 4), HW - 6, 8.0, ACO), 0.6, 2, 40))   # bloco do quadro
    topo = [(HU - 22, 3.0, -2.0), (E - 120, 1.5, -2.0), (E - 240, -2.0, -2.0), (E - 292, -4.0, -2.0)]
    baixo = [(HU - 22, -18.0, -2.0), (E - 110, -48.0, -2.0), (E - 230, -88.0, -2.0), (E - 292, -100.0, -2.0)]
    q.append(fio(topo, 8.0, ACO, fechado=False))
    q.append(fio(baixo, 7.0, ACO, fechado=False))
    q.append(fio([(E - 165, -1.0, -2.0), (E - 165, -63.0, -2.0)], 5.5, ACO, fechado=False))  # travessa
    for v in (-1.0, -63.0):                                                                   # soldas da travessa
        q.append(lathe([(0, 0), (0, 7.6), (2.2, 6.0), (3.0, 0)], ACO, n=18, c0=(E - 165, v, -2.0), eixo=(0, 1 if v < -30 else -1, 0)))
    sp = arred([(E - 288, 8.0), (E - 300, 7.0), (E - 300, -110.0), (E - 288, -110.0)], 3.0, 5)  # soleira de aço
    q.append(bevel(solido(sp, -16.5, 12.5, ACO), 0.8, 2, 40))
    sr = arred([(E - 299.5, 7.0), (E - 313, 5.5), (E - 313, -108.5), (E - 299.5, -109.5)], 3.0, 5)  # borracha
    s_ = solido(sr, -16.0, 12.0, 'borracha')
    cut(s_, [box(E - 318, E - 311.2, v, v + 2.4, -20, 20, 'borracha') for v in range(-101, 1, 7)])
    q.append(bevel(s_, 0.8, 1, 40))
    for v in (-4, -96):
        pf = lathe([(0, 0), (0, 3.0), (0.8, 3.0), (1.2, 2.3), (1.2, 0)], 'inox', n=14, c0=(E - 312.8, v, -2.0), eixo=(-1, 0, 0))
        cut(pf, [box(E - 316, E - 313.3, v - 4, v + 4, -2.5, -1.5, 'inox')])
        q.append(pf)
    q.append(fio(caminho_arred([(E - 270, -92, -12), (E - 270, -108, -17), (E - 270, -108, 13), (E - 270, -92, 8)], 3.0, 4, fechado=False),
                 1.6, ACO, fechado=False))                                                    # argola da bandoleira
    q.append(bevel(box(HU - 18, HU - 4, -16.0, -8.0, 7.5, 11.5, ACO), 0.5, 1, 40))            # botão da trava
    parte('coronha', q, origem=(HU, 0, HW), suave=40)


def montar_rebativel_ak():
    coronha_rebativel()
    _grupo()
