"""Móveis de quarto no nível realista: cômoda de 3 gavetas, criado-mudo e guarda-roupa de 2 portas.

O mesmo conjunto de madeira escura envernizada (nogueira), com almofadas nas laterais e nas portas, tampo
moldurado, puxadores de alça de latão com espelho e fechaduras. As gavetas são caixas de verdade, de madeira
clara por dentro. Medidas em mm nas coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente.
As medidas de fora e os nós que abrem (gaveta_1..3; gaveta; porta_esq, porta_dir, gaveta) são os mesmos dos
móveis antigos de props/mobilias, para a ambientação dos prédios e o jogo continuarem valendo."""
import math
import lib
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte
from lib import pintar

N = 'nogueira_'          # + eixo do veio
F = 'forro_'


def _torno(prof, mat, x=0, y=0, z=0, n=20, eixo=(0, 1, 0)):
    """Perfil em (raio, altura ao longo do eixo)."""
    return lib.lathe([(h, r) for r, h in prof], mat, n=n, c0=G(x, y, z), eixo=G(*eixo))


def _fio(pts, r, mat, fechado=False, res=2):
    return lib.fio([G(*p) for p in pts], r, mat, fechado=fechado, res=res)


def _puxador(x, y, z, larg=96):
    """Puxador de alça: espelho de latão recortado, dois pinos e a alça caída. z = face da gaveta."""
    a = larg / 2
    esp = [(-a - 16, 0), (-a - 10, -13), (-a + 8, -17), (-18, -11), (0, -15), (18, -11), (a - 8, -17), (a + 10, -13), (a + 16, 0),
           (a + 10, 13), (a - 8, 17), (18, 11), (0, 19), (-18, 11), (-a + 8, 17), (-a - 10, 13)]
    p = [frente([(x + px, y + py) for px, py in esp], z - 0.5, z + 2.2, 'latao_puxador', 0.7)]
    for s in (-1, 1):
        p.append(_torno([(0, 0), (6.5, 0), (6.5, 3), (4.2, 5), (4.2, 11), (5.6, 12), (5.6, 16), (0, 17)], 'latao_puxador', x + s * a, y, z + 2, n=10, eixo=(0, 0, 1)))
    arco = [(x - a, y, z + 14)] + [(x + a * math.cos(math.radians(t)) * 0.92, y - 30 * math.sin(math.radians(180 - t)) ** 0.7 - 2, z + 15 + 5 * math.sin(math.radians(180 - t)))
                                   for t in range(170, 9, -20)] + [(x + a, y, z + 14)]
    p.append(_fio(arco, 3.0, 'latao_puxador'))
    return p


def _fechadura(x, y, z):
    """Espelho de fechadura de latão com o buraco da chave."""
    e = [(x + 9 * math.cos(math.radians(t)), y + 15 * math.sin(math.radians(t)) - (3 if math.sin(math.radians(t)) < 0 else 0)) for t in range(0, 360, 30)]
    return [frente(e, z - 0.5, z + 1.8, 'latao_puxador', 0.6),
            cil((x, y + 4, z + 1.7), (x, y + 4, z + 2.1), 2.6, 'tinta_preta', n=10),
            caixa(x - 1.3, x + 1.3, y - 7, y + 4, z + 1.7, z + 2.1, 'tinta_preta')]


def _botao(x, y, z):
    """Puxador de botão de latão (portas)."""
    return [_torno([(0, 0), (11, 0), (11, 2.5), (5, 5), (4.5, 12), (9, 17), (12.5, 22), (12, 27), (8, 30.5), (0, 31.5)], 'latao_puxador', x, y, z, n=16, eixo=(0, 0, 1))]


def _almofada_lado(s, X, e, y0, y1, z0, z1, mont=52, trav=58, meio=()):
    """Lateral de montantes e travessas com almofada rebaixada. s = lado (-1/+1); X = face de fora; e = espessura."""
    xa, xb = sorted((s * (X - e), s * X))
    xp0, xp1 = sorted((s * (X - e - 3), s * (X - 5)))
    p = [caixa(xa, xb, y0, y1, z0, z0 + mont, N + 'y', 1.6), caixa(xa, xb, y0, y1, z1 - mont, z1, N + 'y', 1.6),
         caixa(xa, xb, y0, y0 + trav, z0 + mont, z1 - mont, N + 'z', 1.6), caixa(xa, xb, y1 - trav, y1, z0 + mont, z1 - mont, N + 'z', 1.6)]
    for ym in meio:
        p.append(caixa(xa, xb, ym - trav / 2, ym + trav / 2, z0 + mont, z1 - mont, N + 'z', 1.6))
    p.append(caixa(xp0, xp1, y0 + trav - 4, y1 - trav + 4, z0 + mont - 4, z1 - mont + 4, N + 'y'))
    return p


def _tampo(X, y, z0, z1, e=26, mat=None):
    """Tampo com a borda moldurada: filete embaixo e a tábua de cima de quina boleada. X, z1 = beiral de fora."""
    return [caixa(-X + 9, X - 9, y, y + 8, z0, z1 - 9, N + 'x', 2.5),
            caixa(-X, X, y + 8, y + e, z0, z1, mat or N + 'x', 5.0)]


def _gaveta(x0, x1, y0, y1, zt, zf, mat_frente=None, esp=22, aba=7, pux=(), fech=None, fundo_y=10):
    """Gaveta: frente com aba (cobre a folga do vão) e quina chanfrada, e a caixa de madeira clara aberta em cima.
    (x0..x1, y0..y1) = vão; zt = fundo da caixa; zf = face da carcaça (a frente fica de zf a zf + esp)."""
    fr = caixa(x0 - aba, x1 + aba, y0 - aba, y1 + aba, zf, zf + esp, mat_frente or N + 'x', 0)
    bevel(fr, 5.0, seg=3)
    p = [fr]
    # moldura rebaixada na frente
    cut(fr, _anel(x0 + 22, x1 - 22, y0 + 20, y1 - 20, 5, zf + esp - 2.5, zf + esp + 3))
    cx0, cx1, cy0, cy1 = x0 + 4, x1 - 4, y0 + 4, y1 - 14
    p += [caixa(cx0, cx0 + 11, cy0, cy1, zt, zf, F + 'z', 1.0), caixa(cx1 - 11, cx1, cy0, cy1, zt, zf, F + 'z', 1.0),
          caixa(cx0 + 11, cx1 - 11, cy0, cy1 - 12, zt, zt + 11, F + 'x', 1.0),
          caixa(cx0 + 11, cx1 - 11, cy0 + fundo_y, cy0 + fundo_y + 5, zt + 11, zf, F + 'x')]
    for px in pux:
        p += _puxador(px, (y0 + y1) / 2 + 6, zf + esp)
    if fech is not None:
        p += _fechadura(fech, (y0 + y1) / 2 + 4, zf + esp)
    return p


def _anel(x0, x1, y0, y1, l, z0, z1):
    """Friso retangular de largura l (para rebaixar com cut)."""
    o = frente([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, N + 'x')
    cut(o, frente([(x0 + l, y0 + l), (x1 - l, y0 + l), (x1 - l, y1 - l), (x0 + l, y1 - l)], z0 - 1, z1 + 1, N + 'x'))
    return o


def _saia(X, y0, y1, z0, z1, pe=70):
    """Saia recortada da base com pés de mísula: frente e as duas laterais."""
    def rec(a, b):
        m, d = (a + b) / 2, (b - a) / 2
        pts = [(a, y0), (a + pe, y0), (a + pe + 14, y0 + 30), (a + pe + 46, y1 - 34)]
        pts += [(m + (d - pe - 70) * math.cos(math.radians(t)), y1 - 34 + 12 * math.sin(math.radians(t))) for t in range(180, -1, -30)][1:-1]
        pts += [(b - pe - 46, y1 - 34), (b - pe - 14, y0 + 30), (b - pe, y0), (b, y0), (b, y1), (a, y1)]
        return pts
    p = [frente(rec(-X, X), z1 - 20, z1, N + 'x', 1.6)]
    for s in (-1, 1):
        xa, xb = sorted((s * (X - 20), s * X))
        p.append(lib.extr([(-z, y) for z, y in rec(z0, z1 - 20)], xa, xb, N + 'z', plane='uv'))
        bevel(p[-1], 1.6)
        p.append(caixa(min(s * (X - 20), s * (X - 62)), max(s * (X - 20), s * (X - 62)), y0 + 4, y1, z1 - 62, z1 - 20, N + 'y', 1.5))   # calço do canto
    return p


# ------------------------------------------------------------------ cômoda
def comoda():
    X, Z0, Z1, H = 450, -220, 200, 850
    VAOS = ((136, 340), (366, 570), (596, 800))
    c = caixa(-X + 8, X - 8, 118, H - 26, Z0, Z1, N + 'y')
    cut(c, caixa(-X + 24, X - 24, 124, H - 44, Z0 + 8, Z1 + 5, N + 'y'))
    pintar(c, F + 'y', lambda q, n: abs(q[2]) < X - 23 and 123 < q[1] < H - 43 and q[0] < -Z0 - 7)
    p = [c]
    for y in (340, 570):                                                  # travessas entre as gavetas
        p.append(caixa(-X + 24, X - 24, y, y + 26, Z1 - 60, Z1, N + 'x', 1.0))
        p.append(caixa(-X + 24, X - 24, y + 4, y + 22, Z0 + 8, Z1 - 60, F + 'x'))
    for s in (-1, 1):
        p += _almofada_lado(s, X, 9, 118, H - 26, Z0, Z1)
    p += _tampo(X + 15, H - 26, Z0 - 5, Z1 + 40)
    p += _saia(X + 6, 0, 118, Z0, Z1 + 22)
    p.append(caixa(-X + 6, X - 6, 60, 118, Z0, Z0 + 12, N + 'x'))            # fecho de trás da base
    parte('corpo', p, origem=G(0, 0, 0), grupo='A')
    for i, (y0, y1) in enumerate(VAOS):
        g = _gaveta(-X + 26, X - 26, y0, y1, Z0 + 20, Z1, pux=(-225, 225), fech=0)
        parte(f'gaveta_{i + 1}', g, origem=G(0, 0, 0), grupo='B')


# ------------------------------------------------------------------ criado-mudo
def criado_mudo():
    X, Z0, Z1, H = 225, -190, 180, 555
    yb = 125                                                              # onde acabam os pés
    c = caixa(-X + 8, X - 8, yb, H - 24, Z0, Z1, N + 'y')
    cut(c, caixa(-X + 22, X - 22, yb + 18, H - 40, Z0 + 8, Z1 + 5, N + 'y'))
    pintar(c, F + 'y', lambda q, n: abs(q[2]) < X - 21 and 349 < q[1] < H - 39 and q[0] < -Z0 - 7)
    p = [c, caixa(-X + 22, X - 22, 326, 348, Z0 + 8, Z1, N + 'x', 1.0)]     # prateleira entre o nicho e a gaveta
    for s in (-1, 1):
        p += _almofada_lado(s, X, 9, yb, H - 24, Z0, Z1, mont=44, trav=46)
        for z in (Z0 + 24, Z1 - 4):                                       # pés torneados
            p.append(_torno([(0, 0), (13, 0), (15, 6), (15, 14), (12, 20), (17, 60), (21, 88), (21, 98), (17, 104), (22, 110), (22, yb), (0, yb)],
                            N + 'y', s * (X - 24), 0, z, n=16))
    p += _tampo(X + 12, H - 24, Z0 - 4, Z1 + 30, e=24)
    p.append(perfil([(Z1, yb), (Z1 + 20, yb), (Z1 + 20, yb + 12), (Z1 + 12, yb + 24), (Z1, yb + 24)], -X + 2, X - 2, N + 'x', 1.5))   # friso da frente embaixo
    parte('corpo', p, origem=G(0, 0, 0), grupo='A')
    g = _gaveta(-X + 24, X - 24, 356, 512, Z0 + 20, Z1, esp=20, pux=(0,))
    parte('gaveta', g, origem=G(0, 0, 0), grupo='A')


# ------------------------------------------------------------------ guarda-roupa
def _porta_gr(lado, X, y0, y1, z0, esp=22):
    """Porta almofadada (2 almofadas). lado = -1 esquerda, +1 direita; dobradiça na quina de fora."""
    xa, xb = sorted((lado * (X - 1.5), lado * 1.5))
    mont, trav = 72, 80
    ym = y0 + (y1 - y0) * 0.40
    p = [caixa(xa, xa + mont, y0, y1, z0, z0 + esp, N + 'y', 2.0), caixa(xb - mont, xb, y0, y1, z0, z0 + esp, N + 'y', 2.0)]
    for ya, yb in ((y0, y0 + trav), (ym - trav / 2, ym + trav / 2), (y1 - trav, y1)):
        p.append(caixa(xa + mont, xb - mont, ya, yb, z0, z0 + esp, N + 'x', 2.0))
    for ya, yb in ((y0 + trav, ym - trav / 2), (ym + trav / 2, y1 - trav)):   # almofadas: fundo e miolo levantado de quina chanfrada
        p.append(caixa(xa + mont - 4, xb - mont + 4, ya - 4, yb + 4, z0 + 3, z0 + 11, N + 'y'))
        a = caixa(xa + mont + 14, xb - mont - 14, ya + 14, yb - 14, z0 + 10, z0 + esp - 2, N + 'y')
        bevel(a, 9.0, seg=1, ang=60)
        p.append(a)
        p.append(caixa(xa + mont - 4, xb - mont + 4, ya - 4, yb + 4, z0 + 1.5, z0 + 3, F + 'y'))           # verso claro
    for y in (y0 + 160, (y0 + y1) / 2, y1 - 160):                                                          # dobradiças de latão
        p.append(cil((lado * X, y - 34, z0 + esp), (lado * X, y + 34, z0 + esp), 5.5, 'latao_puxador', n=12))
        for d in (-36, 36):
            p.append(cil((lado * X, y + d - 2, z0 + esp), (lado * X, y + d + 2, z0 + esp), 7.0, 'latao_puxador', n=12))
    xm = lado * 38                                                                                         # montante do meio
    p += _botao(xm, ym + 40, z0 + esp)
    if lado > 0:
        p += _fechadura(xm, ym - 40, z0 + esp)
        p.append(caixa(-10, 3, y0, y1, z0 + esp - 1, z0 + esp + 5, N + 'y', 2.0))                          # batente que cobre a fresta
    return p


def _cabide(x, y, z, giro=0.0):
    """Cabide de madeira com gancho de arame, pendurado no varão (y = eixo do varão)."""
    c, s = math.cos(giro), math.sin(giro)
    def q(a, b, d=0):
        return (x + a * s + d * c, y + b, z + a * c - d * s)
    gancho = [q(0, -62), q(0, -22), q(-9, -12), q(-14, 0), (x, y + 14, z)[0:0] or q(-9, 15), q(4, 17), q(13, 8), q(12, -2)]
    p = [_fio(gancho, 1.6, 'cabide_arame')]
    pts = [(-205, -128), (-150, -100), (-70, -70), (0, -58), (70, -70), (150, -100), (205, -128), (198, -140), (150, -116), (70, -88), (0, -78), (-70, -88), (-150, -116), (-198, -140)]
    o = lib.extr([(-(z + a * c), y + b) for a, b in pts], x - 5, x + 5, 'faia_x', plane='uv') if abs(s) < 1e-6 else None
    if o is None:
        import bmesh, bpy
        o = lib.extr([(a, b) for a, b in pts], -5, 5, 'faia_x', plane='uv')
        for v in o.data.vertices:                                         # extr 'uv': u = a (para trás em -z do jogo), v = b, w = espessura
            a, b, d = v.co.y / lib.MM, v.co.z / lib.MM, v.co.x / lib.MM
            v.co = lib.P(*G(*q(a, b, d)))
    bevel(o, 2.5)
    p.append(o)
    return p


def guarda_roupa():
    X, Z0, Z1, H = 500, -290, 270, 2000
    YB, YG, YP, YC = 80, 400, 425, 1915          # topo do rodapé, topo do vão da gaveta, pé das portas, pé da cornija
    c = caixa(-X + 8, X - 8, YB, YC, Z0, Z1, N + 'y')
    cut(c, caixa(-X + 26, X - 26, YB + 20, YC - 18, Z0 + 8, Z1 + 5, N + 'y'))
    pintar(c, F + 'y', lambda q, n: abs(q[2]) < X - 25 and YB + 19 < q[1] < YC - 17 and q[0] < -Z0 - 7)
    p = [c, caixa(-X + 26, X - 26, YG, YG + 24, Z0 + 8, Z1, N + 'x', 1.0)]                                 # piso do roupeiro, sobre a gaveta
    for s in (-1, 1):
        p += _almofada_lado(s, X, 9, YB, YC, Z0, Z1, mont=70, trav=80, meio=(YP + (YC - YP) * 0.40,))
    # rodapé com pés de mísula
    p += _saia(X + 4, 0, YB + 4, Z0, Z1 + 26, pe=90)
    p.append(caixa(-X + 6, X - 6, 30, YB, Z0, Z0 + 12, N + 'x'))
    # cornija em três degraus
    for dx, ya, yb, ch in ((8, YC, YC + 22, 2.0), (17, YC + 22, YC + 60, 9.0), (25, YC + 60, H, 3.0)):
        p.append(caixa(-X - dx, X + dx, ya, yb, Z0, Z1 + 22 + dx - 1, N + 'x', ch))
    parte('corpo', p, origem=G(0, 0, 0), grupo='A')
    # dentro: maleiro, varão com as flanges e os cabides
    d = [caixa(-X + 26, X - 26, 1700, 1718, Z0 + 8, Z1 - 22, F + 'x', 1.0),
         cil((-X + 26, 1640, -10), (X - 26, 1640, -10), 12.5, 'zincado', n=16)]
    for s in (-1, 1):
        d.append(_torno([(0, 0), (30, 0), (30, 3), (16, 5), (16, 16), (0, 16)], 'zincado', s * (X - 26), 1640, -10, n=16, eixo=(-s, 0, 0)))
    for x, g in ((-310, 0.0), (-250, 0.10), (120, -0.14), (340, 0.0)):
        d += _cabide(x, 1640, -10, g)
    parte('dentro', d, origem=G(0, 0, 0), grupo='B')
    for nome, lado in (('porta_esq', -1), ('porta_dir', 1)):
        parte(nome, _porta_gr(lado, X, YP, YC - 3, Z1), origem=G(lado * X, 0, Z1 + 22), grupo='C')
    g = _gaveta(-X + 28, X - 28, YB + 26, YG - 6, Z0 + 30, Z1, pux=(-250, 250), fech=0)
    parte('gaveta', g, origem=G(0, 0, 0), grupo='C')


FORMAS = {'comoda': comoda, 'criado_mudo': criado_mudo, 'guarda_roupa': guarda_roupa}
