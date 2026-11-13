"""Móveis de banheiro no nível realista: pia de coluna, vaso sanitário com caixa e armário com espelho.

Louça branca torneada (as bacias saem de um perfil girado e esticado para ficar oval), metais de inox e o armário de
madeira pintada da cozinha. Medidas em mm nas coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente.
As medidas de fora e os nós que abrem (assento, tampa_caixa, porta_espelho) são os dos móveis antigos."""
import math, os, importlib.util
import lib
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte

_spec = importlib.util.spec_from_file_location('modelo_quarto', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'quarto', 'modelo.py'))
q = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(q)
_torno, _fio = q._torno, q._fio
L, T = 'louca', 'tinta_creme'


def _mover(o, f):
    """Aplica f(x, y, z) -> (x, y, z), em mm do jogo, a todos os vértices."""
    for v in o.data.vertices:
        x, y, z = v.co.x / lib.MM, v.co.z / lib.MM, -v.co.y / lib.MM
        v.co = lib.P(*G(*f(x, y, z)))
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def _oval(prof, mat, cz, kz, n=28, zmin=None):
    """Perfil girado em volta de y e esticado kz vezes em z, com centro em z = cz; zmin achata o fundo contra a parede."""
    o = _torno(prof, mat, 0, 0, 0, n=n)
    return _mover(o, lambda x, y, z: (x, y, max(cz + z * kz, zmin) if zmin is not None else cz + z * kz))


def _registro(x, y, z):
    """Registro de cruzeta."""
    p = [_torno([(0, 0), (17, 0), (17, 3), (11, 7), (10, 34), (14, 38), (14, 45), (0, 45)], 'inox', x, y, z, n=14)]
    for g in (20, 110):
        dx, dz = 23 * math.cos(math.radians(g)), 23 * math.sin(math.radians(g))
        p.append(cil((x - dx, y + 50, z - dz), (x + dx, y + 50, z + dz), 4.5, 'inox', n=8))
    p.append(_torno([(0, 0), (8, 0), (6, 5), (0, 6)], 'inox', x, y + 52, z, n=10))
    return p


def pia_banheiro():
    p = [_oval([(0, 0), (96, 0), (102, 12), (84, 40), (64, 120), (58, 480), (66, 600), (80, 660), (0, 660)], L, -50, 0.85, n=20)]          # coluna
    p.append(_oval([(0, 640), (80, 640), (130, 690), (232, 760), (266, 805), (270, 850), (262, 860), (247, 854), (226, 800),
                    (150, 742), (45, 726), (0, 726)], L, -8, 0.80, n=32, zmin=-225))                                                   # bacia
    p.append(bevel(caixa(-262, 262, 780, 868, -240, -150, L), 14.0, seg=3))                                                           # mesa dos metais, encostada na parede
    p.append(_torno([(0, 0), (24, 0), (24, 2), (19, 3.5), (0, 3.5)], 'inox', 0, 726, -8, n=16))
    p.append(_torno([(0, 0), (15, 0), (15, 1.2), (0, 1.2)], 'ralo', 0, 729.5, -8, n=12))
    yb, zt = 868, -196
    p.append(_torno([(0, 0), (20, 0), (20, 4), (14, 8), (12, 30), (0, 30)], 'inox', 0, yb, zt, n=16))
    arco = [(0, yb + 26, zt), (0, yb + 70, zt)]
    for k in range(1, 8):
        a = math.radians(180 - k * 22)
        arco.append((0, yb + 70 + 40 * math.sin(a), zt + 52 + 52 * math.cos(a)))
    arco.append((0, yb + 62, zt + 108))
    p.append(_fio(arco, 9.0, 'inox', res=3))
    for s in (-1, 1):
        p += _registro(s * 105, yb, zt)
    parte('pia', p, origem=G(0, 0, 0), grupo='A')


def vaso_sanitario():
    CZ, KZ = 150, 1.52
    p = [_oval([(0, 0), (112, 0), (116, 14), (102, 60), (96, 150), (120, 250), (172, 340), (190, 384), (190, 400), (166, 400), (152, 340),
                (100, 272), (50, 252), (0, 252)], L, CZ, KZ, n=28)]                                                                   # bacia e pé
    p.append(_oval([(0, 262), (96, 262), (96, 264), (0, 264)], 'agua_vaso', CZ, KZ, n=20))
    p.append(bevel(caixa(-150, 150, 230, 400, -230, -100, L), 30.0, seg=3))                                                           # pescoço até a caixa
    for s in (-1, 1):
        p.append(_torno([(0, 0), (13, 0), (12, 9), (6, 14), (0, 15)], 'liner', s * 118, 14, 40, n=10))                                # capas dos parafusos
    cx = bevel(caixa(-196, 196, 400, 770, -335, -150, L), 18.0, seg=3)
    cut(cx, caixa(-176, 176, 425, 790, -317, -168, L))
    p.append(cx)
    p.append(_torno([(0, 0), (12, 0), (12, 6), (8, 9), (0, 9)], 'inox', -130, 700, -150, n=12, eixo=(0, 0, 1)))                        # alavanca da descarga
    p.append(cil((-130, 700, -141), (-70, 690, -138), 5.0, 'inox', n=8))
    parte('vaso', p, origem=G(0, 0, 0), grupo='A')
    a = [_oval([(112, 400), (192, 400), (196, 408), (190, 418), (118, 418), (110, 410), (112, 400)], 'liner', CZ, KZ, n=28),           # assento
         _oval([(0, 419), (194, 419), (197, 426), (188, 434), (0, 436)], 'liner', CZ, KZ, n=28)]                                      # tampa
    a.append(caixa(-110, 110, 400, 436, -150, -120, 'liner', 6.0))
    for s in (-1, 1):
        a.append(cil((s * 60, 420, -150), (s * 110, 420, -150), 11.0, 'liner', n=10))
    parte('assento', a, origem=G(0, 400, -150), grupo='B')
    parte('tampa_caixa', [bevel(caixa(-202, 202, 770, 795, -340, -145, L), 8.0, seg=3), caixa(-172, 172, 762, 772, -313, -172, L)],
          origem=G(0, 780, 0), grupo='B')


def armario_banheiro():
    X, Z0, ZC, H = 250, -20, 125, 640
    c = caixa(-X, X, 0, H, Z0, ZC, T)
    cut(c, caixa(-X + 16, X - 16, 16, H - 16, Z0 + 6, ZC + 5, T))
    p = [bevel(c, 1.2)]
    for y in (215, 425):
        p.append(caixa(-X + 16, X - 16, y - 4, y + 4, Z0 + 6, ZC - 22, 'vidro_fosco', 1.0))
    p.append(bevel(caixa(-X - 8, X + 8, H - 4, H + 14, Z0, ZC + 22, T), 4.0, seg=2))                         # cimalha
    p.append(caixa(-150, 150, H + 14, H + 34, Z0 + 4, Z0 + 46, 'inox', 3.0))                                 # luminária: base e tubo fosco
    p.append(cil((-140, H + 44, Z0 + 52), (140, H + 44, Z0 + 52), 16.0, 'vidro_fosco', n=14))
    for s in (-1, 1):
        p.append(cil((s * 140, H + 44, Z0 + 52), (s * 152, H + 44, Z0 + 52), 18.0, 'inox', n=14))
    parte('corpo', p, origem=G(0, 0, 0), grupo='A')
    m = 34
    d = [caixa(-X + 2, -X + 2 + m, 2, H - 6, ZC, ZC + 18, T, 1.6), caixa(X - 2 - m, X - 2, 2, H - 6, ZC, ZC + 18, T, 1.6),
         caixa(-X + 2 + m, X - 2 - m, 2, 2 + m, ZC, ZC + 18, T, 1.6), caixa(-X + 2 + m, X - 2 - m, H - 6 - m, H - 6, ZC, ZC + 18, T, 1.6),
         caixa(-X + m - 2, X - m + 2, m - 2, H - m - 2, ZC + 4, ZC + 12, 'espelho'),
         caixa(-X + m - 2, X - m + 2, m - 2, H - m - 2, ZC + 1, ZC + 4, T)]
    d.append(_torno([(0, 0), (6, 0), (6, 8), (11, 12), (11, 18), (0, 20)], 'inox', X - 20, H / 2, ZC + 18, n=12, eixo=(0, 0, 1)))
    for y in (110, H - 110):
        d.append(cil((-X + 2, y - 22, ZC + 18), (-X + 2, y + 22, ZC + 18), 4.0, 'zincado', n=10))
    parte('porta_espelho', d, origem=G(-X, 0, ZC + 18), grupo='B')


FORMAS = {'pia_banheiro': pia_banheiro, 'vaso_sanitario': vaso_sanitario, 'armario_banheiro': armario_banheiro}
