"""Mesa de costura com máquina manual: mesa de madeira de pés torneados simples, máquina de costura de ferro
esmaltado com manivela, quadro de linhas atrás com os carretéis, panos dobrados, tesoura, alfineteiro, fita
métrica e um cesto com rolos de pano embaixo.
Medidas em mm, coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente (onde se senta)."""
import math
import lib
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte

H = 760                     # em cima do tampo
XT, ZT = 550, 300
QUADRO = 1120               # topo do quadro de linhas
MX, MZ = 150, -60           # máquina: meio da base


def _torno(prof, mat, x=0, y=0, z=0, n=24, eixo=(0, 1, 0)):
    """Perfil em (raio, altura ao longo do eixo)."""
    return lib.lathe([(h, r) for r, h in prof], mat, n=n, c0=G(x, y, z), eixo=G(*eixo))


def _fio(pts, r, mat, fechado=False, res=3):
    return lib.fio([G(*p) for p in pts], r, mat, fechado=fechado, res=res)


def _mesa():
    p = []
    yt = H - 28
    for sx in (-1, 1):
        for sz in (-1, 1):
            x, z = sx * 490, sz * 245
            p.append(caixa(x - 26, x + 26, yt - 150, yt, z - 26, z + 26, 'pinho_y', 2.5))
            p.append(_torno([(0, 0), (15, 0), (17, 30), (22, 60), (25, 380), (20, 400), (25, 420), (25, yt - 150), (0, yt - 150)], 'pinho_y', x, 0, z, n=14))
        p.append(caixa(sx * 490 - 11, sx * 490 + 11, yt - 120, yt - 10, -219, 219, 'pinho_z', 2.0))
    for sz in (-1, 1):
        p.append(caixa(-464, 464, yt - 120, yt - 10, sz * 245 - 11, sz * 245 + 11, 'pinho_x', 2.0))
    p.append(caixa(-180, 180, yt - 108, yt - 22, 256, 262, 'faia_x', 2.0))                                # frente da gavetinha (fixa)
    p.append(_torno([(0, 0), (9, 0), (7, 8), (13, 16), (13, 22), (0, 26)], 'faia_x', 0, yt - 65, 262, n=14, eixo=(0, 0, 1)))
    for sx in (-1, 1):                                                                                    # quadro de linhas
        p.append(caixa(sx * 430 - 16, sx * 430 + 16, H, QUADRO, -292, -270, 'pinho_y', 2.0))
    p.append(caixa(-470, 470, H + 110, QUADRO - 20, -288, -274, 'pinho_x', 1.5))
    p.append(caixa(-490, 490, QUADRO - 6, QUADRO + 14, -300, -262, 'pinho_x', 2.5))
    return p


def _tampo():
    p = []
    for k, d in enumerate((0, 5, -4)):
        z0 = -ZT + k * 201
        p.append(caixa(-XT - d, XT + (4 - d), H - 28, H, z0, z0 + 199, 'tampo_x', 3.5))
    return p


def _maquina():
    """Máquina de costura manual: base de madeira, corpo de ferro esmaltado em C, volante e manivela à direita."""
    y = H + 34
    x0, x1 = MX - 190, MX + 190
    p = [caixa(x0 - 16, x1 + 26, H, y, MZ - 105, MZ + 105, 'faia_x', 5.0)]                                # base de madeira
    corpo = frente([(x0, y), (x1, y), (x1, y + 205), (x1 - 12, y + 232), (x0 + 40, y + 232), (x0 + 8, y + 220), (x0, y + 200),
                    (x0, y + 86), (x0 + 62, y + 86), (x0 + 66, y + 150), (x1 - 82, y + 150), (x1 - 72, y + 26), (x0, y + 26)],
                   MZ - 36, MZ + 36, 'esmalte_preto', 14.0)
    p.append(corpo)
    p.append(caixa(x0 - 6, x1 + 4, y, y + 22, MZ - 86, MZ + 86, 'esmalte_preto', 6.0))                    # mesa da máquina
    p.append(caixa(x0 + 4, x0 + 96, y + 22, y + 23.5, MZ - 40, MZ + 44, 'lata', 0.5))                     # chapa da agulha
    xa = x0 + 32
    p.append(cil((xa, y + 24, MZ), (xa, y + 92, MZ), 2.6, 'lata', n=8))                                   # barra da agulha
    p.append(cil((xa, y + 24, MZ), (xa, y + 40, MZ), 1.0, 'lata', n=6))
    p.append(cil((xa + 16, y + 30, MZ), (xa + 16, y + 92, MZ), 3.0, 'lata', n=8))                         # calcador
    p.append(caixa(xa + 2, xa + 30, y + 24, y + 30, MZ - 9, MZ + 9, 'lata', 1.5))
    p.append(caixa(x0 - 3, x0, y + 100, y + 200, MZ - 28, MZ + 28, 'lata', 1.0))                          # tampa da cabeça
    p.append(_torno([(0, 0), (16, 0), (18, 4), (18, 12), (0, 12)], 'lata', x0 + 34, y + 232, MZ, n=14))   # tensor em cima
    p.append(cil((x1 - 60, y + 232, MZ), (x1 - 60, y + 300, MZ), 2.6, 'lata', n=8))                       # pino do carretel
    p += _carretel(x1 - 60, y + 234, MZ, 'pano_vermelho', eixo=(0, 1, 0))
    for k in range(5):                                                                                    # filete dourado
        p.append(caixa(x0 + 90 + k * 44, x0 + 118 + k * 44, y + 186, y + 196, MZ + 36, MZ + 36.6, 'dourado'))
    xv = x1 + 6                                                                                           # volante
    p.append(_torno([(0, 0), (20, 0), (22, 8), (58, 10), (66, 14), (66, 30), (58, 34), (22, 34), (16, 44), (0, 44)], 'esmalte_preto', xv, y + 178, MZ, n=28, eixo=(1, 0, 0)))
    p.append(_torno([(60, 15), (68, 17), (68, 27), (60, 29)], 'lata', xv, y + 178, MZ, n=28, eixo=(1, 0, 0)))
    yc, zc = y + 178 - 40, MZ + 38                                                                        # manivela
    p.append(caixa(xv + 44, xv + 52, y + 178 - 52, y + 178 + 12, MZ - 10, MZ + 50, 'lata', 2.0))
    p.append(cil((xv + 50, yc, zc), (xv + 60, yc, zc), 4, 'lata', n=8))
    p.append(_torno([(0, 0), (9, 0), (12, 14), (11, 40), (7, 52), (0, 54)], 'faia_x', xv + 58, yc, zc, n=14, eixo=(1, 0, 0)))
    return p


def _carretel(x, y, z, mat, eixo=(0, 0, 1), r=17, h=44):
    return [_torno([(0, 0), (r + 3, 0), (r + 3, 4), (7, 5), (7, h - 5), (r + 3, h - 4), (r + 3, h), (0, h)], 'faia_x', x, y, z, n=10, eixo=eixo),
            _torno([(7, 5), (r, 7), (r + 1, h / 2), (r, h - 7), (7, h - 5)], mat, x, y, z, n=10, eixo=eixo)]


CORES = ('pano_vermelho', 'pano_azul', 'pano_amarelo', 'pano_verde', 'pano_cru', 'pano_cinza')


def _linhas():
    """Carretéis nos pinos do quadro (três fileiras), alguns pinos vazios."""
    p = []
    k = 0
    for j in range(3):
        for i in range(8):
            x, y = -385 + i * 110, H + 150 + j * 82
            p.append(cil((x, y, -274), (x, y + 10, -216), 3.2, 'faia_z', n=8))
            k += 1
            if (i * 7 + j * 5) % 6 == 4:
                continue
            p += _carretel(x, y + 2, -270, CORES[(i * 5 + j * 3) % 6], r=15 + (k % 3) * 2, h=40 + (k % 2) * 6)
    return p


def _dobrado(x0, x1, z0, z1, y, mats, alt=18):
    p = []
    for k, m in enumerate(mats):
        d = k * 7
        p.append(caixa(x0 + d, x1 - d * 0.6, y + k * alt, y + (k + 1) * alt, z0 + d * 0.5, z1 - d, m, 7.0))
    return p


def _tesoura(x, z, a):
    y = H + 3
    c, s = math.cos(a), math.sin(a)
    r = lambda dx, dz: (x + dx * c - dz * s, z + dx * s + dz * c)
    p = []
    for sg in (-1, 1):
        pts = [r(0, sg * 2), r(120, sg * 1), r(124, 0), r(0, -sg * 9)]
        if sg < 0:
            pts.reverse()
        p.append(planta(pts, y, y + 2.2, 'aco_lamina', 0.4))
        cx, cz = r(-52, sg * 24)
        p.append(_fio([(cx + 22 * math.cos(t * math.pi / 8) * (1.3 if sg > 0 else 1.0), y + 3, cz + 17 * math.sin(t * math.pi / 8)) for t in range(16)], 4.0, 'plastico_preto', fechado=True, res=2))
        p.append(cil((*r(-8, 0)[:1], y + 2, r(-8, 0)[1]), (cx + 20, y + 3, cz - sg * 8), 4.0, 'plastico_preto', n=8))
    p.append(cil((x, y, z), (x, y + 5, z), 4.5, 'latao', n=8))
    return p


def _alfineteiro(x, z):
    y = H
    p = [_torno([(0, 0), (34, 0), (42, 14), (40, 30), (26, 44), (0, 48)], 'pano_vermelho', x, y, z, n=18)]
    for k in range(9):
        a = k * 2.4
        rr = 10 + (k * 7) % 22
        bx, bz = x + rr * math.cos(a), z + rr * math.sin(a)
        topo = (bx + 10 * math.cos(a), y + 72 - rr * 0.5, bz + 10 * math.sin(a))
        p.append(cil((bx, y + 38, bz), topo, 0.7, 'lata', n=5))
        p.append(cil(topo, (topo[0], topo[1] + 4, topo[2]), 2.6, ('plastico_amarelo', 'plastico_azul', 'pano_cru')[k % 3], n=6, r1=1.2))
    return p


def _fita_metrica(x, z):
    y = H
    pts = [(x, z), (x + 90, z + 26), (x + 190, z + 6), (x + 270, z + 40), (x + 300, ZT + 4)]
    p = []
    for a, b in zip(pts[:-1], pts[1:]):
        dx, dz = b[0] - a[0], b[1] - a[1]
        m = math.hypot(dx, dz)
        nx, nz = -dz / m * 8, dx / m * 8
        p.append(planta([(a[0] - nx, a[1] - nz), (b[0] - nx, b[1] - nz), (b[0] + nx, b[1] + nz), (a[0] + nx, a[1] + nz)], y, y + 1.2, 'plastico_amarelo'))
    p.append(caixa(x + 292, x + 308, y - 170, y + 1.2, ZT + 3, ZT + 4.2, 'plastico_amarelo'))                 # ponta caindo pela frente
    p.append(caixa(x + 291, x + 309, y - 176, y - 164, ZT + 2.6, ZT + 4.6, 'lata'))
    return p


def _cesto(x, z):
    """Cesto de vime no chão com rolos de pano em pé."""
    c = _torno([(0, 0), (150, 0), (165, 20), (190, 300), (196, 312), (190, 322), (0, 322)], 'vime', x, 0, z, n=24)
    cut(c, _torno([(0, 14), (150, 14), (176, 300), (176, 340), (0, 340)], 'vime', x, 0, z, n=24))
    p = [c]
    for k, (dx, dz, m, alto, rr) in enumerate(((-60, -30, 'pano_azul', 520, 52), (50, -50, 'pano_cru', 600, 46), (20, 60, 'pano_verde', 470, 56), (-70, 70, 'pano_amarelo', 420, 40))):
        ix, iz = (dx * 0.25, dz * 0.25)
        p.append(cil((x + dx, 16, z + dz), (x + dx + ix, alto, z + dz + iz), rr, m, n=14))
        p.append(cil((x + dx + ix, alto - 4, z + dz + iz), (x + dx + ix * 1.01, alto + 6, z + dz + iz * 1.01), 12, 'faia_y', n=8))
    return p


def _miudezas():
    p = _dobrado(-520, -250, -150, 90, H, ('pano_cinza', 'pano_azul', 'pano_cru', 'pano_vermelho'))
    p += _tesoura(-150, 190, 0.5) + _alfineteiro(-330, 200) + _fita_metrica(-60, 150)
    p += _carretel(-200, H, 40, 'pano_verde', eixo=(0, 1, 0)) + _carretel(-120, H + 18, 70, 'pano_cru', eixo=(1, 0, 0.3))
    p.append(caixa(430, 540, H, H + 46, 120, 250, 'lata', 6.0))                                           # lata de botões
    p.append(caixa(427, 543, H + 40, H + 52, 117, 253, 'esmalte_vermelho', 5.0))
    return p


def montar():
    parte('mesa', _mesa(), origem=G(0, 0, 0), grupo='A')
    parte('tampo', _tampo(), origem=G(0, 0, 0), grupo='A')
    parte('maquina', _maquina(), origem=G(0, 0, 0), grupo='B')
    parte('linhas', _linhas(), origem=G(0, 0, 0), grupo='C')
    parte('miudezas', _miudezas(), origem=G(0, 0, 0), grupo='C')
    parte('cesto', _cesto(-300, -60), origem=G(0, 0, 0), grupo='C')
