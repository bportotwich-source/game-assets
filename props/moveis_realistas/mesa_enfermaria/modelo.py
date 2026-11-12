"""Mesa de enfermaria improvisada: tábuas sobre dois cavaletes com colchão de listras, lençol, cobertor e
travesseiro, um soro pendurado num pau amarrado à cabeceira e, ao lado, um caixote com cruz vermelha que
serve de criado: bacia de ágata, frascos, ataduras e bandeja de instrumentos.
Medidas em mm, coordenadas do jogo (ver ../base.py): x largura (cabeceira em -x), y altura, +z a frente."""
import math
import lib
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte

H = 780                     # em cima das tábuas
XT, ZT = 950, 320
CX = 1250                   # meio do caixote-criado
CY = 520                    # em cima do caixote


def _torno(prof, mat, x=0, y=0, z=0, n=24, eixo=(0, 1, 0)):
    """Perfil em (raio, altura ao longo do eixo)."""
    return lib.lathe([(h, r) for r, h in prof], mat, n=n, c0=G(x, y, z), eixo=G(*eixo))


def _fio(pts, r, mat, fechado=False, res=3):
    return lib.fio([G(*p) for p in pts], r, mat, fechado=fechado, res=res)


def _cavalete(x):
    yt = H - 30
    p = [caixa(x - 40, x + 40, yt - 70, yt, -310, 310, 'pinho_z', 2.5)]
    for sx in (-1, 1):
        for sz in (-1, 1):
            z0, z1 = sz * 330, sz * 200
            pts = [(z0 - 32, 0), (z0 + 32, 0), (z1 + 32, yt - 20), (z1 - 32, yt - 20)]
            p.append(perfil(pts, x + sx * 40, x + sx * 62, 'pinho_y', 2.0))
        p.append(caixa(x + sx * 62, x + sx * 80, 260, 330, -290, 290, 'pinho_z', 2.0))              # travessa
    return p


def _estrado():
    p = _cavalete(-650) + _cavalete(650)
    for k, d in enumerate((0, 12, -8, 6, -3)):
        z0 = -ZT + k * 128
        p.append(caixa(-XT - d, XT + (8 - d), H - 30, H, z0, z0 + 126, 'tampo_x', 3.0))
    return p


def _caixote():
    x0, x1, z0, z1 = CX - 220, CX + 220, -170, 170
    p = []
    for k in range(4):                                                                               # laterais e fundo de ripas
        y = 12 + k * 126
        p.append(caixa(x0, x0 + 18, y, y + 118, z0, z1, 'crua_z', 2.0))
        p.append(caixa(x1 - 18, x1, y, y + 118, z0, z1, 'crua_z', 2.0))
        p.append(caixa(x0 + 18, x1 - 18, y, y + 118, z0, z0 + 16, 'crua_x', 2.0))
    p.append(caixa(x0 - 6, x1 + 6, CY - 20, CY, z0 - 6, z1 + 6, 'crua_x', 2.5))                      # tampo
    p.append(caixa(x0 + 18, x1 - 18, 250, 268, z0 + 16, z1 - 4, 'crua_x', 2.0))                      # prateleira
    p.append(caixa(x0 + 18, x1 - 18, 0, 16, z0 + 16, z1 - 4, 'crua_x', 2.0))
    for sx in (-1, 1):
        for sz in (-1, 1):
            p.append(caixa(CX + sx * 196 - 14, CX + sx * 196 + 14, 0, CY - 20, sz * 150 - 14, sz * 150 + 14, 'crua_y', 2.0))
    # a cruz vermelha pintada na lateral virada para a frente... fica na tábua de cima da frente
    p.append(caixa(x0 + 18, x1 - 18, CY - 150, CY - 20, z1 - 16, z1, 'crua_x', 2.0))
    return p


def _cama():
    y = H
    p = [caixa(-915, 915, y, y + 70, -295, 295, 'colchao', 26.0),
         caixa(-905, 905, y + 62, y + 76, -300, 300, 'lencol', 6.0)]
    for sz in (-1, 1):                                                                               # lençol caindo dos lados
        p.append(caixa(-880, 880, y - 40, y + 72, sz * 298 - 4, sz * 298 + 4, 'lencol', 3.0))
    manta = [(-348, y - 135), (-326, y + 30), (-300, y + 98), (300, y + 98), (326, y + 30), (348, y - 135),
             (339, y - 135), (317, y + 28), (294, y + 89), (-294, y + 89), (-317, y + 28), (-339, y - 135)]
    p.append(perfil(manta, 125, 915, 'cobertor', 3.0))                                               # cobertor até o meio, caindo dos lados
    p.append(perfil([(-300, y + 96), (300, y + 96), (304, y + 108), (296, y + 120), (-296, y + 120), (-304, y + 108)], 118, 300, 'cobertor', 8.0))   # a dobra
    p.append(perfil([(-300, y + 60), (300, y + 60), (300, y + 96), (-300, y + 96)], 905, 925, 'cobertor', 4.0))
    trav = caixa(-880, -560, y + 74, y + 170, -230, 230, 'fronha', 40.0)
    p.append(trav)
    return p


def _soro():
    """Pau amarrado à cabeceira com um frasco de soro de cabeça para baixo e a mangueira até a cama."""
    x, z = -930, -338
    p = [cil((x, 0, z), (x, 1820, z), 17, 'crua_y', n=10, r1=14),
         cil((x, 1780, z), (x + 150, 1800, z + 40), 9, 'crua_x', n=8)]
    for y in (H - 80, H - 20):                                                                       # amarração
        p.append(_torno([(19, 0), (21, 6), (19, 12)], 'pano_cru', x, y, z, n=10))
    fx, fz, fy = x + 135, z + 36, 1560
    p.append(_fio([(fx, 1800, fz), (fx, 1770, fz)], 1.6, 'lata'))
    p.append(_torno([(0, 0), (12, 0), (14, 8), (14, 22), (36, 44), (38, 170), (30, 186), (0, 188)], 'vidro_soro', fx, fy, fz, n=18))
    p.append(_torno([(0, -14), (9, -14), (15, -2), (15, 3), (0, 3)], 'borracha_soro', fx, fy, fz, n=12))
    p.append(_fio([(fx - 30, fy + 186, fz), (fx - 26, 1772, fz), (fx + 26, 1772, fz), (fx + 30, fy + 186, fz)], 1.6, 'lata'))   # alça de arame
    p.append(_fio([(fx, fy - 14, fz), (fx, fy - 120, fz), (fx + 20, fy - 330, fz + 60), (fx + 120, H + 260, fz + 190), (fx + 330, H + 120, fz + 280), (fx + 420, H + 82, fz + 300)],
                  2.6, 'borracha_soro'))
    p.append(cil((fx, fy - 150, fz), (fx, fy - 105, fz), 7, 'vidro_soro', n=10))                     # gotejador
    return p


def _frasco(x, z, r, h, mat='vidro_ambar', y=CY):
    return [_torno([(0, 0), (r, 0), (r, h * 0.62), (r * 0.42, h * 0.80), (r * 0.42, h * 0.94), (0, h * 0.94)], mat, x, y, z, n=14),
            _torno([(0, 0), (r * 0.5, 0), (r * 0.5, h * 0.10), (0, h * 0.10)], 'plastico_preto', x, y + h * 0.92, z, n=10)]


def _rolo(a, b, r=26):
    return [cil(a, b, r, 'pano_cru', n=14), cil(tuple(a[i] - (b[i] - a[i]) * 0.01 for i in range(3)), tuple(b[i] + (b[i] - a[i]) * 0.01 for i in range(3)), r * 0.35, 'pano_cinza', n=8)]


def _miudezas():
    y = CY
    bx, bz = CX + 70, 20                                                                             # bacia de ágata
    bacia = _torno([(0, 0), (85, 0), (150, 62), (158, 62), (158, 68), (146, 68), (84, 6), (0, 6)], 'esmalte_branco', bx, y, bz, n=28)
    p = [bacia,
         _torno([(0, 0), (102, 0), (102, 1.5), (0, 1.5)], 'vidro_soro', bx, y + 20, bz, n=24)]        # água
    p.append(caixa(CX - 52, CX + 52, CY - 137, CY - 33, 170, 170 + 0.6, 'cruz_branca'))
    p.append(caixa(CX - 12, CX + 12, CY - 127, CY - 43, 170 + 0.6, 170 + 1.1, 'cruz_vermelha'))
    p.append(caixa(CX - 42, CX + 42, CY - 97, CY - 73, 170 + 1.1, 170 + 1.5, 'cruz_vermelha'))
    p += _frasco(CX - 150, -90, 32, 150) + _frasco(CX - 80, -110, 26, 120) + _frasco(CX - 165, -10, 22, 100, 'vidro_soro')
    tx0, tx1, tz0, tz1 = CX - 195, CX - 45, 50, 150                                                  # bandeja de instrumentos
    band = caixa(tx0, tx1, y, y + 16, tz0, tz1, 'lata', 4.0)
    cut(band, caixa(tx0 + 3, tx1 - 3, y + 3, y + 30, tz0 + 3, tz1 - 3, 'lata'))
    p.append(band)
    for k, dz in enumerate((22, 44, 70)):
        p.append(cil((tx0 + 14, y + 6, tz0 + dz), (tx1 - 20 - k * 12, y + 6, tz0 + dz + 6), 2.6 + 0.6 * (k == 2), 'lata', n=6))
    p.append(cil((tx0 + 20, y + 9, tz0 + 84), (tx0 + 96, y + 9, tz0 + 88), 6.5, 'vidro_soro', n=10))   # seringa de vidro
    p.append(cil((tx0 + 96, y + 9, tz0 + 88), (tx0 + 128, y + 9, tz0 + 90), 0.8, 'lata', n=5))
    p.append(cil((tx0 + 8, y + 9, tz0 + 83.4), (tx0 + 20, y + 9, tz0 + 84), 9, 'lata', n=10))
    ys = 268                                                                                         # prateleira: ataduras e um pano dobrado
    for k in range(4):
        p += _rolo((CX - 180 + k * 62, ys + 26, -60), (CX - 180 + k * 62, ys + 26, 30))
    p += _rolo((CX - 150, ys + 74, -55), (CX - 150, ys + 74, 35)) + _rolo((CX - 88, ys + 74, -50), (CX - 88, ys + 74, 40))
    p.append(caixa(CX + 60, CX + 190, ys, ys + 50, -110, 120, 'lencol', 9.0))
    p.append(caixa(CX + 64, CX + 186, ys + 50, ys + 86, -104, 114, 'pano_cinza', 9.0))
    p += _frasco(CX - 120, 40, 40, 170, 'vidro_ambar', y=16) + _frasco(CX - 20, 20, 34, 200, 'vidro_soro', y=16) + _frasco(CX + 80, 60, 44, 150, 'vidro_ambar', y=16)
    return p


def montar():
    parte('estrado', _estrado(), origem=G(0, 0, 0), grupo='A')
    parte('caixote', _caixote(), origem=G(0, 0, 0), grupo='A')
    parte('cama', _cama(), origem=G(0, 0, 0), grupo='B')
    parte('soro', _soro(), origem=G(0, 0, 0), grupo='C')
    parte('miudezas', _miudezas(), origem=G(0, 0, 0), grupo='C')
