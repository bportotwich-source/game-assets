"""Itens de água no nível realista: garrafa PET de 2 L, garrafa de água de 1,5 L, galão de 5 L,
garrafa de vidro, cantil e caneca de lata. Desenho próprio, sem marcas.

Cada vasilha transparente tem a casca (plástico ou vidro) e a água em malhas separadas: gerar.py
tira a água para fazer o item vazio e troca a cor dela para fazer o de água suja e o de água limpa.

Coordenadas em mm (lib.py da M4A1): u = para trás, v = para cima, w = direita. Pivô no centro da base.
"""
import math
from mathutils import Matrix
from lib import *

CIMA = (0, 1, 0)


def _torno(prof, mat, n=40, **k):
    """Perfil [(altura, raio)] girado em volta do eixo de pé."""
    return lathe(prof, mat, n=n, eixo=CIMA, **k)


def _sem_tampas(o, n):
    """Tira a tampa que o torno põe na ponta aberta do perfil (boca de garrafa)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if len(f.verts) >= n], context='FACES')
    bm.to_mesh(o.data)
    bm.free()
    return o


def _cheio(prof, nivel, folga=1.5):
    """Perfil da água dentro de uma casca: o mesmo perfil, um pouco para dentro, até o nível."""
    out = [(folga, 0)]
    for (t0, r0), (t1, r1) in zip(prof, prof[1:]):
        if r0 > folga and t0 < nivel and t0 + folga > out[-1][0] - 1e-6:
            out.append((t0 + folga if t0 < 30 else t0, r0 - folga))
        if t0 < nivel <= t1:
            out.append((nivel, r0 + (r1 - r0) * (nivel - t0) / (t1 - t0) - folga))
            break
    out.append((nivel, 0))
    return out


def _petalas(o, alt=26.0, fundo=7.0, n=5):
    """Fundo de garrafa PET: cinco pés, com o meio e os vãos entre eles levantados."""
    ax, ex, ez = P(0, 1, 0).normalized(), P(1, 0, 0).normalized(), P(0, 0, 1).normalized()
    for v in o.data.vertices:
        t = v.co.dot(ax) / MM
        if t >= alt:
            continue
        rad = v.co - ax * (t * MM)
        r = rad.length / MM
        k = 1 - t / alt
        vale = 0.5 - 0.5 * math.cos(n * math.atan2(rad.dot(ez), rad.dot(ex))) if r > 1e-3 else 1.0
        meio = min(1.0, max(0.0, 1 - (r - 12) / 14))
        v.co = ax * ((t + fundo * k * max(vale, meio)) * MM) + rad * (1 - 0.06 * vale * k)
    return o


def _deitar(objs, comp, raio):
    """Deita a garrafa no chão, com o comprimento na largura (w) e o meio dela no pivô."""
    m = Matrix.Translation(P(0, raio, -comp / 2)) @ Matrix.Rotation(math.radians(90), 4, P(1, 0, 0).normalized())
    for o in objs:
        o.data.transform(m)
    return objs


# ------------------------------------------------------------------ garrafa PET de 2 L (deitada)
def garrafa_pet():
    prof = [(0, 0), (0, 18), (2, 34), (8, 46), (16, 52.5), (28, 55), (94, 55), (98, 53), (102, 55), (120, 55), (124, 53), (128, 55),
            (214, 55), (226, 54), (242, 49.5), (258, 41.5), (272, 31), (284, 21), (292, 15.2), (297, 13.6), (300, 13.6),
            (300.6, 16.8), (302.4, 16.8), (303, 13.4), (306, 13.4)]
    casca = _petalas(_torno(prof, 'pet'))
    agua = _petalas(_torno(_cheio(prof, 264), 'agua'))
    tampa = [_torno([(304.2, 13.9), (304.2, 15.4), (306, 15.4), (306, 13.9)], 'tampa_vermelha', n=24, anel=True),      # lacre
             _torno([(306.6, 13.5), (306.6, 15.8), (321.5, 15.8), (323.4, 14.6), (324, 0)], 'tampa_vermelha', n=36, lobes=0.035, lobe_min=15)]
    _deitar([casca, agua] + tampa, 324, 55)
    raiz = parte('tampa', tampa, origem=(0, 0, 0), grupo='A')
    parte('casca', [casca], origem=(0, 0, 0), pai=raiz, grupo='A')
    parte('agua', [agua], origem=(0, 0, 0), pai=raiz, grupo='A')
    return raiz


# ------------------------------------------------------------------ garrafa de água de 1,5 L (em pé, lacrada)
def garrafa_agua():
    prof = [(0, 0), (0, 15), (2, 29), (7, 38.5), (14, 43.5), (24, 45.5)]
    t = 30
    for _ in range(5):
        prof += [(t, 45.5), (t + 3.5, 43.4), (t + 7, 45.5)]
        t += 15
    prof += [(112, 45.5), (114, 43.6), (196, 43.6), (198, 45.5)]                               # rebaixo do rótulo
    t = 204
    for _ in range(2):
        prof += [(t, 45.5), (t + 3.5, 43.4), (t + 7, 45.5)]
        t += 15
    prof += [(240, 45.5), (252, 43.5), (266, 36.5), (279, 26), (288, 18), (293, 14.5), (296, 13.6), (298, 13.6),
             (298.6, 16.6), (300.2, 16.6), (300.8, 13.4), (303, 13.4)]
    casca = _petalas(_torno(prof, 'pet'), alt=22.0, fundo=6.0)
    agua = _petalas(_torno(_cheio(prof, 270), 'agua'), alt=22.0, fundo=6.0)
    raiz = parte('tampa', [_torno([(115, 44.85), (115, 45.0), (195, 45.0), (195, 44.85)], 'rotulo_agua', anel=True),
                           _torno([(301.2, 13.9), (301.2, 15.3), (303, 15.3), (303, 13.9)], 'tampa_azul', n=24, anel=True),
                           _torno([(303.6, 13.5), (303.6, 15.7), (317.5, 15.7), (319.4, 14.5), (320, 0)], 'tampa_azul', n=36, lobes=0.035, lobe_min=15)],
                 origem=(0, 0, 0), grupo='A')
    parte('casca', [casca], origem=(0, 0, 0), pai=raiz, grupo='A')
    parte('agua', [agua], origem=(0, 0, 0), pai=raiz, grupo='A')
    return raiz


# ------------------------------------------------------------------ galão de 5 L
def galao_agua():
    prof = [(0, 0), (0, 74), (3, 80), (9, 84), (16, 85), (70, 85), (76, 81.5), (82, 85), (150, 85), (156, 81.5), (162, 85),
            (212, 85), (222, 83), (240, 72), (256, 55), (268, 38), (274, 30), (278, 25.5), (282, 24.5), (292, 24.5)]
    alca = [(0, 282, -27), (0, 292, -62), (0, 312, -60), (0, 324, -30), (0, 327, 0), (0, 324, 30), (0, 312, 60), (0, 292, 62), (0, 282, 27)]
    raiz = parte('tampa', [_torno([(286, 25.2), (286, 29.5), (302, 29.5), (304, 27.5), (304.6, 0)], 'tampa_azul', n=36, lobes=0.03, lobe_min=29),
                           _torno([(279, 25), (279, 28.5), (284, 28.5), (284, 25)], 'tampa_azul', n=28, anel=True),
                           fio(caminho_arred(alca, 10, n=4, fechado=False), 3.2, 'tampa_azul', fechado=False, res=2)],
                 origem=(0, 0, 0), grupo='A')
    parte('casca', [_torno(prof, 'pet', n=44)], origem=(0, 0, 0), pai=raiz, grupo='A')
    parte('agua', [_torno(_cheio(prof, 236, folga=3.5), 'agua', n=44)], origem=(0, 0, 0), pai=raiz, grupo='A')
    return raiz


# ------------------------------------------------------------------ garrafa de vidro
def garrafa_vidro():
    prof = [(7, 0), (5, 16), (0, 26), (0, 30), (1.5, 33.6), (5, 35.5), (40, 35.5), (41.5, 34.1), (128, 34.1), (129.5, 35.5), (150, 35.5),
            (170, 33), (190, 25), (205, 18), (216, 14.6), (226, 13.4), (278, 12.6), (279, 14.6), (286, 14.6), (287, 13.4), (292, 13.4)]
    casca = _sem_tampas(_torno(prof + [(292, 10.6), (272, 10.6)], 'vidro_verde'), 40)
    agua = [(9, 0), (7, 15), (2.5, 25), (2.5, 29), (4, 32), (6.5, 33.2), (42, 32.6), (128, 32.6), (150, 33.6), (170, 31.2), (190, 23.2), (198, 19.5), (198, 0)]
    raiz = parte('rotulo', [_torno([(44, 35.5), (44, 35.65), (126, 35.65), (126, 35.5)], 'rotulo_velho', anel=True)], origem=(0, 0, 0), grupo='A')
    parte('casca', [casca], origem=(0, 0, 0), pai=raiz, grupo='A')
    parte('agua', [_torno(agua, 'agua')], origem=(0, 0, 0), pai=raiz, grupo='A')
    parte('rolha', [_torno([(276, 0), (276, 10.2), (292, 10.5), (297, 11.6), (299, 10.6), (299.6, 0)], 'rolha', n=20)], origem=(0, 0, 0), pai=raiz, grupo='A')
    return raiz


# ------------------------------------------------------------------ cantil de alumínio (em pé)
def cantil():
    def anel(y, rw, ru, e=2.9):
        return [P(u, y, w) for (w, u) in superelipse(rw, ru, n=36, e=e)]
    niveis = [(0, 44, 21), (2, 54, 27), (8, 61, 31.5), (18, 64, 33.5), (86, 65, 34), (90, 63.6, 32.8), (94, 65, 34), (140, 64, 33.5),
              (160, 58, 31.5), (174, 46, 28), (184, 32, 23), (190, 22, 19), (194, 16, 16)]
    corpo = [loft([anel(*n) for n in niveis], 'cantil_verde'),
             _torno([(193, 0), (193, 15), (207, 15), (207, 0)], 'aluminio', n=24)]                 # gargalo de rosca
    elo = [(0, 196, 15.5), (0, 196, 24), (0, 207, 30), (0, 220, 27), (0, 226, 19)]                  # tira que prende a tampa
    corpo.append(fio(elo, 1.3, 'plastico_preto', fechado=False, res=2))
    corpo.append(_torno([(194, 15.2), (194, 17.2), (198, 17.2), (198, 15.2)], 'plastico_preto', n=24, anel=True))
    raiz = parte('corpo', corpo, origem=(0, 0, 0), grupo='A')
    parte('tampa', [_torno([(203, 0), (203, 18.5), (222, 18.5), (225, 16.5), (226, 0)], 'plastico_preto', n=32, lobes=0.04, lobe_min=18)],
          origem=(0, 203, 0), pai=raiz, grupo='A')
    return raiz


# ------------------------------------------------------------------ caneca de lata com alça de arame
def caneca_lata():
    prof = [(0, 0), (0, 35), (1.2, 37.5), (3, 36.8), (4.5, 37.5)]
    for t in range(18, 67, 8):
        prof += [(t, 37.5), (t + 2, 36.6), (t + 4, 37.5)]
    prof += [(84, 37.5), (86, 38.5), (88.4, 38.5), (89, 37.6), (88.4, 36.6), (86, 36.4), (6, 36.3), (4.5, 0)]
    p = [_torno(prof, 'lata_fuligem', n=44)]
    for t in (20.5, 68.5):                                                                      # arame em volta da lata
        p.append(_torno([(t - 1.4, 37.4), (t - 1.4, 39.6), (t + 1.4, 39.6), (t + 1.4, 37.4)], 'arame', n=32, anel=True))
    alca = [(0, 68.5, 38.5), (0, 70, 54), (0, 62, 74), (0, 44.5, 80), (0, 27, 74), (0, 19, 54), (0, 20.5, 38.5)]
    p.append(fio(caminho_arred(alca, 9, n=4, fechado=False), 1.5, 'arame', fechado=False, res=2))
    raiz = parte('lata', p, origem=(0, 0, 0), grupo='A')
    parte('agua', [_torno([(58, 0), (58, 36.25), (60, 36.25), (60, 0)], 'agua', n=44)], origem=(0, 0, 0), pai=raiz, grupo='A')
    return raiz


FORMAS = {'garrafa_pet': garrafa_pet, 'garrafa_agua': garrafa_agua, 'galao_agua': galao_agua,
          'garrafa_vidro': garrafa_vidro, 'cantil': cantil, 'caneca_lata': caneca_lata}
