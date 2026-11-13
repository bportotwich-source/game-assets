"""Comida embalada no nível realista: latas de feijão, milho e sardinha, pacote de arroz, caixa de flocos de
milho, caixa de leite, pacote de salgadinho e barra de chocolate. Desenho próprio, sem marcas.

Coordenadas do jogo em mm (base.py dos móveis): x = largura, y = para cima, z = frente. Cada item fica na
mesma posição do antigo (latas e caixas em pé, pacotes deitados) e com o mesmo tamanho.
"""
import math, random
from mathutils import Vector
import lib
from lib import cut, bevel, parte, pintar, MM
from base import G, caixa, cil, planta, perfil, frente
import bpy


def letreiro(s, tam, x, y, z, mat='letra_preta'):
    """Texto impresso numa face virada para a frente (+z), centrado em x, linha de base em y (curvas mais finas que o de base.py)."""
    cu = bpy.data.curves.new('t', 'FONT')
    cu.body = s
    cu.size = tam * MM
    cu.align_x = 'CENTER'
    cu.resolution_u = 4 if tam >= 8 else 2
    tmp = bpy.data.objects.new('t', cu)
    bpy.context.scene.collection.objects.link(tmp)
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(tmp)
    for v in me.vertices:
        v.co = lib.P(*G(x + v.co.x / MM, y + v.co.y / MM, z))
    o = bpy.data.objects.new('t', me)
    bpy.context.scene.collection.objects.link(o)
    me.materials.clear()
    me.materials.append(lib.M(mat))
    return o


def _mexer(o, f):
    """Move cada vértice: f(x, y, z) em mm do jogo -> (x, y, z)."""
    for v in o.data.vertices:
        x, y, z = v.co.x / MM, v.co.z / MM, -v.co.y / MM
        x, y, z = f(x, y, z)
        v.co = lib.P(*G(x, y, z))
    return o


def _na_lata(s, tam, y, R, mat, giro=0.0):
    """Texto enrolado num cilindro de raio R em volta do eixo y, centrado na frente (+z)."""
    o = letreiro(s, tam, 0, y, 0, mat=mat)
    g = math.radians(giro)
    return _mexer(o, lambda x, yy, z: (R * math.sin(x / R + g), yy, R * math.cos(x / R + g)))


def _deitado(s, tam, x0, z0, alto, mat, giro=0):
    """Texto deitado numa face de cima: lido por quem olha de +z (giro 0) ou de +x (giro 90). alto(x, z) -> y."""
    o = letreiro(s, tam, 0, 0, 0, mat=mat)

    def f(x, y, z):
        if giro == 90:
            X, Z = x0 - y, z0 - x
        else:
            X, Z = x0 + x, z0 - y
        return (X, alto(X, Z), Z)
    return _mexer(o, f)


def _ret_arred(hx, hz, r, n=5):
    pts = []
    for (cx, cz, a0) in ((hx - r, hz - r, 0), (-hx + r, hz - r, 90), (-hx + r, -hz + r, 180), (hx - r, -hz + r, 270)):
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts[::-1]


def _argola(x, y, z, mat='lata'):
    """Anel de puxar a tampa, deitado, com a lingueta e o rebite."""
    return [lib.lathe([(0, 5.6), (0, 8.6), (0.9, 8.6), (0.9, 5.6)], mat, n=16, c0=G(x + 9, y, z), eixo=G(0, 1, 0), anel=True),
            bevel(caixa(x - 9, x + 2.0, y, y + 1.2, z - 4.2, z + 4.2, mat), 0.3, 1),
            cil((x - 5, y, z), (x - 5, y + 1.5, z), 2.3, mat, n=10)]


# ------------------------------------------------------------------ latas redondas
def _lata(R, H, cor, faixa, y0, y1, titulo, sub, letra, letra_sub):
    r = R - 1.4
    corpo = lib.lathe([(0, 0), (0, r - 0.6), (0.6, R), (3.4, R), (4.2, r), (H - 4.2, r), (H - 3.4, R), (H - 0.6, R), (H, r - 0.6), (H, r - 2.2),
                       (H - 3.0, r - 2.6), (H - 3.0, r - 7), (H - 2.4, r - 9), (H - 3.0, r - 11), (H - 3.0, 0)], 'lata', n=32, c0=G(0, 0, 0), eixo=G(0, 1, 0))
    rot = lib.lathe([(6.5, r), (6.5, r + 0.3), (y0, r + 0.3), (y1, r + 0.3), (H - 6.5, r + 0.3), (H - 6.5, r)], cor, n=32, c0=G(0, 0, 0), eixo=G(0, 1, 0))
    pintar(rot, faixa, lambda c, n: y0 < c[1] < y1)
    ym = (y0 + y1) / 2
    txt = [_na_lata(titulo, (y1 - y0) * 0.50, ym - (y1 - y0) * 0.14, r + 0.55, letra),
           _na_lata(sub, 4.6, y0 - 9.5, r + 0.55, letra_sub),
           _na_lata('ingredientes: grãos, água e sal', 3.0, ym + 3, r + 0.55, 'letra_preta', giro=180),
           _na_lata('conservar em lugar fresco', 3.0, ym - 4, r + 0.55, 'letra_preta', giro=180)]
    raiz = parte('lata', [corpo], origem=G(0, 0, 0), grupo='A', suave=40)
    parte('rotulo', [rot], origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    parte('letras', txt, origem=G(0, 0, 0), pai=raiz, grupo='A')
    parte('argola', _argola(-4, H - 3.0, 0), origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


def lata_feijao():
    return _lata(38.0, 110.0, 'rot_marrom', 'rot_creme', 44.0, 76.0, 'FEIJÃO', 'carioca cozido  ·  400 g', 'letra_vermelha', 'letra_amarela')


def lata_milho():
    return _lata(37.5, 75.0, 'rot_verde', 'rot_amarelo', 30.0, 54.0, 'MILHO', 'verde em conserva  ·  200 g', 'letra_vermelha', 'letra_amarela')


# ------------------------------------------------------------------ lata de sardinha
def lata_sardinha():
    HX, HZ, RC = 52.0, 36.0, 15.0
    fora = _ret_arred(HX, HZ, RC)
    dentro = _ret_arred(HX - 0.9, HZ - 0.9, RC - 0.9)
    p = [planta(fora, 0, 2.6, 'lata'), planta(dentro, 2.6, 20.6, 'rot_azul'), planta(fora, 20.6, 23.0, 'lata'),
         planta(_ret_arred(HX - 3.2, HZ - 3.2, RC - 3.2), 23.0, 23.5, 'lata')]
    est = [planta(_ret_arred(HX - 6.5, HZ - 6.5, RC - 6.0), 23.5, 23.75, 'letra_azul')]
    alto = lambda x, z: 24.0
    txt = [_deitado('SARDINHA', 9.0, -8, 4, alto, 'letra_amarela'), _deitado('em óleo  ·  125 g', 4.2, -8, 14, alto, 'letra_branca'),
           planta([(-44, -16.5), (28, -16.5), (28, -15.3), (-44, -15.3)][::-1], 23.75, 23.95, 'letra_amarela')]
    raiz = parte('lata', p, origem=G(0, 0, 0), grupo='A', suave=40)
    parte('estampa', est, origem=G(0, 0, 0), pai=raiz, grupo='A')
    parte('letras', txt, origem=G(0, 0, 0), pai=raiz, grupo='A')
    parte('argola', _argola(31, 23.75, 0), origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


# ------------------------------------------------------------------ pacotes em almofada (arroz, salgadinho)
def _almofada(L, C, A, mat, faixa, zf, solda, e=2.6, n=28, mat_solda='folha_aluminio'):
    """Pacote deitado, comprido em z: cheio no meio e achatado nas duas soldas. Devolve (malha, alto(x, z))."""
    hx, hz, ry = L / 2, C / 2, A / 2

    def meio(z):
        t = min(1.0, (hz - abs(z)) / (hz * 0.34))                  # 0 na solda, 1 no corpo
        t = max(0.0, (hz - solda - abs(z)) / (hz * 0.34)) if abs(z) < hz - solda else 0.0
        t = min(1.0, t)
        s = math.sin(t * math.pi / 2) ** 0.8
        return hx * (1.0 - 0.045 * s), 0.7 + (ry - 0.7) * s

    def alto(x, z):
        rx, r = meio(z)
        return ry + r * max(0.0, 1.0 - min(1.0, abs(x) / rx) ** e) ** (1.0 / e)
    zs = [-hz, -hz + solda * 0.5, -hz + solda] + [-hz + solda + (2 * (hz - solda)) * k / 22 for k in range(1, 22)] + [hz - solda, hz - solda * 0.5, hz]
    aneis = []
    for z in zs:
        rx, r = meio(z)
        pts = []
        for k in range(n):
            a = 2 * math.pi * k / n
            c, s = math.cos(a), math.sin(a)
            pts.append(lib.P(*G(rx * math.copysign(abs(c) ** (2 / e), c), ry + r * math.copysign(abs(s) ** (2 / e), s), z)))
        aneis.append(pts)
    o = lib.loft(aneis, mat)
    pintar(o, faixa, lambda c, nn: zf[0] < c[2] * 0 - c[0] < zf[1])
    pintar(o, mat_solda if mat != 'saco_branco' else mat, lambda c, nn: abs(c[0]) > hz - solda)
    return o, alto


def pacote_arroz():
    o, alto = _almofada(170.0, 270.0, 64.0, 'saco_branco', 'saco_azul', (-62.0, 2.0), 9.0)
    sobe = lambda x, z: alto(x, z) + 0.35
    txt = [_deitado('ARROZ', 24.0, 0, -18, sobe, 'letra_branca'), _deitado('branco  ·  tipo 1', 7.0, 0, -6, sobe, 'letra_amarela'),
           _deitado('1 kg', 12.0, 0, 34, sobe, 'letra_azul'), _deitado('agulhinha polido', 6.0, 0, 46, sobe, 'letra_azul')]
    raiz = parte('pacote', [o], origem=G(0, 0, 0), grupo='A', suave=50)
    parte('letras', txt, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=50)
    return raiz


def salgadinho():
    o, alto = _almofada(170.0, 264.0, 44.0, 'saco_laranja', 'saco_vermelho', (-40.0, 30.0), 11.0, e=2.2)
    sobe = lambda x, z: alto(x, z) + 0.35
    txt = [_deitado('SALGADINHO', 17.0, 0, 2, sobe, 'letra_amarela'), _deitado('de milho  ·  sabor queijo', 6.5, 0, 14, sobe, 'letra_branca'),
           _deitado('80 g', 9.0, 0, 62, sobe, 'letra_branca'), _deitado('crocante', 9.0, 0, -62, sobe, 'letra_branca')]
    raiz = parte('pacote', [o], origem=G(0, 0, 0), grupo='A', suave=50)
    parte('letras', txt, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=50)
    return raiz


# ------------------------------------------------------------------ caixa de flocos de milho
def caixa_cereal():
    HX, H, HZ = 95.0, 282.0, 35.0
    cx = bevel(caixa(-HX, HX, 0, H, -HZ, HZ, 'rot_amarelo'), 0.9, 2)
    F = HZ + 0.3
    est = [caixa(-HX + 0.6, HX - 0.6, 196, 258, HZ, F, 'letra_vermelha'),
           cil((0, 104, HZ), (0, 104, F), 62, 'rot_branco', n=40), cil((0, 104, F), (0, 104, F + 0.3), 50, 'flocos', n=40),
           caixa(-HX + 0.6, HX - 0.6, 0.6, 20, HZ, F, 'letra_vermelha'),
           caixa(-HX + 0.6, HX - 0.6, 196, 258, -F, -HZ, 'letra_vermelha'), caixa(-70, 70, 40, 170, -F, -HZ, 'rot_branco'),
           caixa(HX, HX + 0.3, 60, 230, -24, 24, 'rot_branco'), caixa(-HX - 0.3, -HX, 0.6, H - 0.6, -HZ + 0.6, HZ - 0.6, 'letra_vermelha'),
           caixa(-HX + 4, HX - 4, H, H + 0.3, -1.0, 1.0, 'rot_creme')]                             # aba de fechar em cima
    rnd = random.Random(4)
    for k in range(26):                                                                          # flocos na tigela
        a, r = rnd.uniform(0, 6.283), 44 * rnd.random() ** 0.5
        est.append(cil((r * math.cos(a), 104 + r * math.sin(a), F + 0.3), (r * math.cos(a), 104 + r * math.sin(a), F + 0.6 + 0.04 * k), rnd.uniform(4, 7), 'rot_amarelo', n=7))
    Z = F + 0.3
    txt = [letreiro('FLOCOS', 30.0, 0, 226, Z, mat='letra_amarela'), letreiro('DE MILHO', 17.0, 0, 203, Z, mat='letra_branca'),
           letreiro('500 g', 9.0, 0, 6, Z, mat='letra_branca'), letreiro('crocantes  ·  sem recheio', 8.0, 0, 176, HZ + 0.3, mat='letra_vermelha')]
    for k in range(9):                                                                           # tabela do verso e da lateral
        txt.append(caixa(-60, 60 - 14 * (k % 3), 150 - 12 * k, 152 - 12 * k, -Z - 0.0, -F, 'letra_preta'))
        txt.append(caixa(HX + 0.3, HX + 0.6, 210 - 16 * k, 212 - 16 * k, -18, 18 - 6 * (k % 2), 'letra_preta'))
    raiz = parte('caixa', [cx], origem=G(0, 0, 0), grupo='A')
    parte('estampa', est, origem=G(0, 0, 0), pai=raiz, grupo='A')
    parte('letras', txt, origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


# ------------------------------------------------------------------ caixa de leite longa vida
def caixa_leite():
    HX, H, HZ = 48.0, 206.0, 31.0
    aneis = []
    for y in (0.0, 1.0, 66.0, 72.0, 78.0, H - 1.0, H):
        d = 1.0 if y in (0.0, H) else 0.0
        aneis.append([lib.P(*G(x, y, z)) for (x, z) in _ret_arred(HX - d, HZ - d, 2.2, n=2)])
    cx = lib.loft(aneis, 'rot_branco')
    pintar(cx, 'rot_azul', lambda c, n: c[1] < 66.0)
    pintar(cx, 'rot_amarelo', lambda c, n: 72.0 < c[1] < 78.0)
    dob = [caixa(-HX + 2, HX - 2, H, H + 3.2, -0.7, 0.7, 'rot_branco')]                           # solda de cima, deitada
    for s in (-1, 1):                                                                            # orelhas dobradas nas laterais
        dob.append(perfil([(-HZ + 2, H - 0.5), (HZ - 2, H - 0.5), (0, H - 30)][::s], s * HX, s * (HX + 0.8), 'rot_branco'))
    tampa = [lib.lathe([(0, 0), (0, 14.5), (1.6, 14.5), (1.6, 12.2), (9, 12.2), (10, 11.2), (10, 0)], 'rot_azul', n=20, c0=G(20, H, 10), eixo=G(0, 1, 0))]
    Z = HZ + 0.3
    txt = [letreiro('LEITE', 20.0, 0, 136, Z, mat='letra_azul'), letreiro('integral', 8.5, 0, 122, Z, mat='letra_azul'),
           letreiro('longa vida', 7.0, 0, 96, Z, mat='letra_vermelha'), letreiro('1 L', 15.0, 0, 30, Z, mat='letra_branca')]
    for k in range(7):
        txt.append(caixa(-30, 30 - 9 * (k % 3), 170 - 11 * k, 171.6 - 11 * k, -Z, -HZ - 0.0, 'letra_azul'))
    raiz = parte('caixa', [cx] + dob, origem=G(0, 0, 0), grupo='A')
    parte('tampa', tampa, origem=G(0, 0, 0), pai=raiz, grupo='A')
    parte('letras', txt, origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


# ------------------------------------------------------------------ barra de chocolate
def barra_chocolate():
    HX, HZ = 37.0, 95.0
    choc = [caixa(-HX, HX, 0.9, 5.2, 30, HZ, 'chocolate')]
    for i in range(4):                                                                           # tabletes à mostra
        for k in range(3):
            x0, z0 = -HX + 0.9 + i * 18.3, 39.5 + k * 18.6
            choc.append(bevel(caixa(x0, x0 + 17.3, 5.2, 9.4, z0, z0 + 17.4, 'chocolate'), 1.8, 2))
    capa = bevel(caixa(-HX - 3, HX + 3, 0, 11.0, -HZ - 2, 34, 'rot_vermelho'), 1.0, 2)             # luva de papel
    faixa = [caixa(-HX - 3.3, HX + 3.3, 0.0, 11.3, -90, -80, 'folha_aluminio')]
    rnd = random.Random(9)
    borda = [(-HX - 2, 30)] + [(-HX - 2 + (2 * HX + 4) * k / 14, HZ + 2 + rnd.uniform(-3, 5) + (5 if k % 2 else 0)) for k in range(15)] + [(HX + 2, 30)]
    folha = [planta(borda[::-1], 0.2, 0.75, 'folha_aluminio')]
    for s in (-1, 1):                                                                            # papel alumínio rasgado, em pé nos lados
        pts, z = [], 30.0
        while z < HZ:
            pts += [(z, 9.5 + rnd.uniform(-3, 4)), (z + 4, 5.5 + rnd.uniform(-2, 2))]
            z += 8.0
        folha.append(perfil(([(30, 0.75)] + pts + [(HZ, 0.75)])[::s], s * (HX + 1.4), s * (HX + 1.9), 'folha_aluminio'))
    alto = lambda x, z: 11.3
    txt = [_deitado('CHOCOLATE', 12.0, 6, -24, alto, 'letra_amarela', giro=90), _deitado('ao leite  ·  90 g', 5.0, -9, -24, alto, 'letra_branca', giro=90)]
    raiz = parte('capa', [capa] + faixa, origem=G(0, 0, 0), grupo='A')
    parte('chocolate', choc, origem=G(0, 0, 0), pai=raiz, grupo='A')
    parte('folha', folha, origem=G(0, 0, 0), pai=raiz, grupo='A')
    parte('letras', txt, origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


# ------------------------------------------------------------------ tigela de arroz cozido
def arroz_cozido():
    tig = lib.lathe([(0, 0), (0, 38), (2, 42), (30, 66), (52, 74), (55, 75.5), (56.5, 74.5), (54, 72.3), (32, 63.5), (5, 40), (4, 0)], 'esmalte_branco', n=32,
                    c0=G(0, 0, 0), eixo=G(0, 1, 0))
    pintar(tig, 'rot_azul', lambda c, n: c[1] > 52.5)                                            # friso azul da borda
    monte = lib.lathe([(0, 0), (2.5, 24), (8, 44), (16, 59), (23, 66)], 'arroz', n=28, c0=G(0, 63, 0), eixo=G(0, -1, 0))
    rnd = random.Random(2)
    graos = []
    for k in range(70):                                                                          # grãos soltos por cima
        a, r = rnd.uniform(0, 6.283), 60 * rnd.random() ** 0.6
        y = 63.6 - 23 * (r / 66) ** 1.9
        b, c = rnd.uniform(0, 6.283), rnd.uniform(2.6, 3.6)
        x, z = r * math.cos(a), r * math.sin(a)
        graos.append(cil((x - c * math.cos(b), y, z - c * math.sin(b)), (x + c * math.cos(b), y + rnd.uniform(-0.6, 0.8), z + c * math.sin(b)), 1.15, 'arroz', n=5))
    raiz = parte('tigela', [tig], origem=G(0, 0, 0), grupo='A', suave=40)
    parte('arroz', [monte] + graos, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=50)
    return raiz


# ================================================================== comida fresca
def _sup(f, nt, na, mat, cap=True):
    """Superfície f(t, a) -> (x, y, z) em mm do jogo, t de 0 a 1 e a em volta; anéis fechados em a."""
    return lib.loft([[lib.P(*G(*f(i / (nt - 1), 2 * math.pi * k / na))) for k in range(na)] for i in range(nt)], mat, cap=cap)


def saco_farinha():
    o, alto = _almofada(296.0, 506.0, 118.0, 'saco_papel', 'rot_azul', (-150.0, -40.0), 16.0, e=3.0, mat_solda='saco_papel')
    sobe = lambda x, z: alto(x, z) + 0.4
    txt = [_deitado('FARINHA', 44.0, 0, -76, sobe, 'letra_branca'), _deitado('de trigo  ·  tipo 1', 13.0, 0, -52, sobe, 'letra_amarela'),
           _deitado('5 kg', 30.0, 0, 60, sobe, 'letra_azul'), _deitado('especial para pães', 12.0, 0, 90, sobe, 'letra_azul'),
           _deitado('enriquecida com ferro', 9.0, 0, 110, sobe, 'letra_azul')]
    cost = []
    for s in (-1, 1):                                                                            # costura das duas bocas
        for k in range(24):
            x = -138 + k * 12
            cost.append(caixa(x, x + 8, 59.6, 61.2, s * 246 - 0.8, s * 246 + 0.8, 'sisal'))
            cost.append(caixa(x, x + 8, 56.8, 58.4, s * 246 - 0.8, s * 246 + 0.8, 'sisal'))
    raiz = parte('saco', [o], origem=G(0, 0, 0), grupo='A', suave=50)
    parte('letras', txt, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=50)
    parte('costura', cost, origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


def _pao_frances(cx, cy, cz, L=132.0, rx=34.0, ry=27.0, giro=0.0):
    """Pão francês comprido em z, com o corte claro em cima."""
    g = math.radians(giro)

    def f(t, a):
        t = 0.015 + 0.97 * t
        s = math.sin(math.pi * t) ** 0.5
        c, sn = math.cos(a), math.sin(a)
        x, y = rx * s * c, ry * s * (sn if sn > 0 else 0.8 * sn)
        z = L * (t - 0.5)
        if sn > 0.55 and abs(z) < L * 0.31:                                                      # lábios do corte
            d = abs(x)
            y += 2.4 if 4.5 < d < 11 else (-1.2 if d <= 4.5 else 0)
        return (cx + x * math.cos(g) + z * math.sin(g), cy + y, cz - x * math.sin(g) + z * math.cos(g))
    o = _sup(f, 26, 24, 'pao_crosta')

    def corte(c, n):
        x, z = c[2] - cx, -c[0] - cz
        xl, zl = x * math.cos(g) - z * math.sin(g), x * math.sin(g) + z * math.cos(g)
        return n[1] > 0.5 and abs(xl) < 4.6 and abs(zl) < L * 0.30
    return pintar(o, 'pao_miolo', corte)


def pao_velho():
    RX, RY, Z0, Z1 = 118.0, 57.0, -244.0, 64.0

    def f(t, a):
        c, sn = math.cos(a), math.sin(a)
        sup = lambda r, v: math.copysign(abs(v) ** (2 / 3.2), v) * r
        if t < 0.8:                                                                              # por fora, do fundo dobrado até a boca
            u = t / 0.8
            z = Z0 + (Z1 - Z0) * u
            k = min(1.0, u / 0.16)
            ry = 1.2 + (RY - 1.2) * math.sin(k * math.pi / 2) ** 0.8
            boca = 1.0 + 0.05 * max(0.0, (u - 0.85) / 0.15) * math.sin(5 * a)                    # boca amassada
            return (sup(RX * (0.93 + 0.07 * k), c) * boca, RY + sup(ry, sn) * boca, z)
        u = (t - 0.8) / 0.2                                                                      # volta por dentro
        return (sup(RX - 1.5, c) * (1 - 0.3 * u), RY + sup(RY - 1.5, sn) * (1 - 0.3 * u), Z1 - 90 * u)
    saco = _sup(f, 40, 36, 'papel_pardo')
    paes = [_pao_frances(-72, 29, 62, giro=4), _pao_frances(0, 29, 76, giro=-3), _pao_frances(72, 29, 58, giro=-6),
            _pao_frances(-36, 79, 48, giro=-5), _pao_frances(38, 78, 66, giro=7)]
    alto = lambda x, z: 2 * RY + 0.5 - RY * (1 - (1 - min(1.0, abs(x) / RX) ** 3.2) ** (1 / 3.2))
    txt = [_deitado('PADARIA', 26.0, 0, -96, alto, 'letra_vermelha'), _deitado('pão fresquinho todo dia', 9.0, 0, -80, alto, 'letra_vermelha')]
    raiz = parte('saco', [saco], origem=G(0, 0, 0), grupo='A', suave=50)
    parte('paes', paes, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=50)
    parte('letras', txt, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=50)
    return raiz


def pao_caseiro():
    L, RX, H = 180.0, 54.5, 80.0

    def talho(x, z):
        return (z + 67.5 + 450) % 45.0 - 22.5 if abs(z) < 88 else 99.0, (5.5 if abs(x) < 37 else 0.0)

    def f(t, a):
        t = 0.012 + 0.976 * t
        s = math.sin(math.pi * t) ** 0.5
        c, sn = math.cos(a), math.sin(a)
        x, z = RX * s * math.copysign(abs(c) ** 0.85, c), L * (t - 0.5)
        y = 9 * s ** 0.4 + ((H - 9) * s * sn ** 0.85 if sn > 0 else 9 * s ** 0.4 * sn)
        d, larg = talho(x, z)
        if sn > 0.3 and larg > 0.5:
            y += -2.6 * (1 - abs(d) / larg) if abs(d) < larg else (1.8 if abs(d) < larg + 4 else 0)
        return (x, y, z)
    o = _sup(f, 82, 36, 'pao_crosta')

    def corte(c, n):
        d, larg = talho(c[2], -c[0])
        return n[1] > 0.2 and abs(d) < larg
    pintar(o, 'pao_miolo', corte)
    return parte('pao', [o], origem=G(0, 0, 0), grupo='A', suave=60)


def carne_crua():
    HX, HZ = 130.0, 100.0

    def papel(t, a_):
        return None
    aneis, M_ = [], 28
    for i in range(25):
        z = -HZ + 2 * HZ * i / 24
        fz = max(0.0, abs(z) / HZ - 0.7) / 0.3
        cima, baixo = [], []
        for k in range(M_ + 1):
            u = k / M_
            x = (-HX + 2 * HX * u) * (1 - 0.04 * fz * fz)
            fx = max(0.0, abs(x) / HX - 0.62) / 0.38
            y = 1.4 + 34 * fx ** 2.2 + 16 * fz ** 2 + 1.6 * math.sin(x / 15 + z / 21) * math.sin(z / 13 - x / 31) + 4 * fx * math.sin(z / 9 + x / 40)
            y = max(1.2, y)
            baixo.append(lib.P(*G(x, y - 1.2, z)))
            cima.append(lib.P(*G(x, y, z)))
        aneis.append(baixo + cima[::-1])
    folha = lib.loft(aneis, 'papel_acougue')

    def f(t, a):
        prof = [(4, 0.55), (5, 0.80), (8, 0.94), (13, 1.0), (30, 1.0), (36, 0.97), (39.5, 0.91)] + [(40.5 + 2.5 * (1 - e) ** 0.5 * 0 + 2.2 * (1 - e ** 2) ** 0.5, e) for e in (0.86, 0.80, 0.74, 0.68, 0.62, 0.56, 0.50, 0.44, 0.38, 0.32, 0.26, 0.20, 0.14, 0.08, 0.02)]
        y, e = prof[min(len(prof) - 1, int(round(t * (len(prof) - 1))))]
        r = 1 + 0.10 * math.sin(2 * a + 1.0) + 0.07 * math.sin(3 * a + 0.4) + 0.025 * math.sin(7 * a)
        return (4 + 86 * r * e * math.sin(a), y, 56 * r * e * math.cos(a))
    bife = _sup(f, 22, 72, 'carne')
    borda = lambda a: 1 + 0.10 * math.sin(2 * a + 1.0) + 0.07 * math.sin(3 * a + 0.4) + 0.025 * math.sin(7 * a)

    def capa(c, n):                                                                              # capa de gordura num lado
        x, z = c[2] - 4, -c[0]
        a = math.atan2(x / 86, z / 56) % (2 * math.pi)
        return 0.25 < a < 2.5 and math.hypot(x / 86, z / 56) / borda(a) > 0.80
    pintar(bife, 'gordura', capa)
    veios = []
    rnd = random.Random(5)
    for k, (z0, x0, x1) in enumerate(((-34, -44, 30), (-25, -58, 44), (-15, -64, 20), (-12, 26, 52), (-3, -68, 54), (8, -66, 6), (10, 14, 52), (21, -60, 48), (31, -46, 36), (38, -30, 20))):   # marmoreio
        m = max(4, int((x1 - x0) / 5))
        pts = []
        for i in range(m + 1):
            x, z = x0 + (x1 - x0) * i / m, z0 + 3.5 * math.sin(i / 2.1 + k * 1.9) + 1.5 * math.sin(i * 1.3 + k)
            rho = min(0.95, math.hypot((x - 4) / 86, z / 56))
            pts.append(G(x, 40.5 + 2.2 * (1 - rho * rho) ** 0.5 - 0.22, z))
        veios.append(lib.fio(pts, rnd.uniform(0.4, 0.6), 'gordura', fechado=False, res=1))
    raiz = parte('papel', [folha], origem=G(0, 0, 0), grupo='A', suave=50)
    parte('carne', [bife] + veios, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=50)
    return raiz


def carne_defumada():
    prof0 = [(0, 0), (0, 21), (3, 27), (14, 32), (45, 36), (85, 37), (125, 34), (150, 27), (163, 18), (169, 9), (170, 0)]
    prof = prof0[:3] + [(x, 0) for x in range(8, 150, 6)] + prof0[-3:]

    def raio(x):
        for (a, ra), (b, rb) in zip(prof0, prof0[1:]):
            if a <= x <= b and b > a:
                return ra + (rb - ra) * (x - a) / (b - a)
        return 0.0
    prof = [(x, r if r or x in (0, 170) else raio(x)) for (x, r) in prof]
    prof[0] = (0, 0)
    X0 = -91.0
    peca = lib.lathe(prof, 'defumada', n=28, c0=G(X0, 37, 0), eixo=G(1, 0, 0))
    pintar(peca, 'carne_cozida', lambda c, n: c[2] < X0 + 0.5 and (c[1] - 37) ** 2 + c[0] ** 2 < 18.5 ** 2)
    cord = []
    for x in (22, 58, 94, 130):
        r = raio(x) - 0.4
        cord.append(lib.lathe([(x - 1.3, r), (x - 1.3, r + 1.7), (x + 1.3, r + 1.7), (x + 1.3, r)], 'sisal', n=28, c0=G(X0, 37, 0), eixo=G(1, 0, 0), anel=True))
    amass = lambda x, y, z: (x, 37 + (y - 37) * (1.0 if y > 37 else 0.97) + 1.5 * math.sin(x / 19.0) * (1 if y > 37 else 0), z * 1.40 * (1 + 0.05 * math.sin(x / 23.0 + 1)))
    amass0 = amass
    gomo = lambda x: 1 + 0.045 * abs(math.sin(math.pi * (x + 91 - 22) / 36.0)) ** 0.6 if -75 < x < 45 else 1.0
    amass = lambda x, y, z: (lambda q: (q[0], 37 + (q[1] - 37) * gomo(x), q[2] * gomo(x)))(amass0(x, y, z))
    for o in [peca] + cord:
        _mexer(o, amass)
    laco = lib.fio([G(78 + 9 * math.cos(a), 37 + 0.0, 9 * math.sin(a)) for a in [2 * math.pi * k / 14 for k in range(14)]], 1.2, 'sisal', fechado=True)
    cord.append(lib.fio([G(-88, 60, 0), G(-80, 37 + raio(11) + 1.2 + 1.5 * math.sin(-80 / 19.0), 0), G(-69, 37 + raio(22) + 1.2 + 1.5 * math.sin(-69 / 19.0), 0)] + [G(x, 37 + raio(x + 91) + 1.2 + 1.5 * math.sin(x / 19.0), 0) for x in (-33, 3, 39, 58, 70, 76)], 1.2, 'sisal', fechado=False))
    raiz = parte('carne', [peca], origem=G(0, 0, 0), grupo='A', suave=50)
    parte('barbante', cord + [laco], origem=G(0, 0, 0), pai=raiz, grupo='A', suave=50)
    return raiz


def _tomate(x, y, z, R=33.0):
    prof = [(R * 0.84 * (1 - math.cos(math.radians(p))), R * math.sin(math.radians(p)) ** 0.9) for p in range(0, 171, 17)] + [(R * 1.55, 3.0), (R * 1.50, 0)]
    t = lib.lathe(prof, 'tomate', n=14, c0=G(x, y - R * 0.8, z), eixo=G(0, 1, 0))
    top = y - R * 0.8 + R * 1.53
    cal = [cil((x, top, z), (x + 13 * math.cos(a), top + 2.2, z + 13 * math.sin(a)), 3.2, 'talo', n=4, r1=0.4) for a in [k * 1.2566 + x for k in range(5)]]
    cal.append(cil((x, top - 1, z), (x + 1, top + 9, z + 1), 2.0, 'talo', n=6))
    return [t], cal


def _cenoura(tip, head, R=15.0):
    v = Vector(head) - Vector(tip)
    m1, m2 = Vector(tip) + v * 0.45, Vector(tip) + v * 0.97
    p = [cil(tip, tuple(m1), 3.0, 'cenoura', n=8, r1=R * 0.72), cil(tuple(m1), tuple(m2), R * 0.72, 'cenoura', n=8, r1=R),
         cil(tuple(m2), head, R, 'cenoura', n=8, r1=R * 0.55)]
    d = v.normalized()
    rnd = random.Random(int(abs(head[0] * 7 + head[2])))
    fol = []
    for k in range(4):
        e = Vector(head) + d * rnd.uniform(26, 44) + Vector((rnd.uniform(-14, 14), rnd.uniform(4, 20), rnd.uniform(-14, 14)))
        fol.append(cil(head, tuple(e), 2.6, 'talo', n=4, r1=4.5))
        fol.append(cil(tuple(e), tuple(e + d * 9 + Vector((0, 4, 0))), 4.5, 'alface', n=4, r1=0.6))
    return p, fol


def cesto_legumes():
    H = 172.0
    raio = lambda y: 132.0 + 45.0 * (y / H) ** 0.8
    prof = [(0, 0), (0, raio(0) - 3)]
    y = 3.0
    while y < H - 12:                                                                            # fiadas de vime
        prof += [(y, raio(y) + 2.6), (y + 7, raio(y + 7) + 2.6), (y + 9, raio(y + 9) - 0.4)]
        y += 12.0
    prof += [(H - 9, raio(H) + 1), (H - 7, raio(H) + 6.3), (H - 1, raio(H) + 6.3), (H, raio(H) + 3), (H, raio(H) - 7), (H - 8, raio(H) - 9)]
    prof += [(8, raio(8) - 8), (8, 0)]
    cesto = lib.lathe(prof, 'vime', n=32, c0=G(0, 0, 0), eixo=G(0, 1, 0))
    varas = []
    for k in range(20):                                                                          # varas em pé por fora
        a = 2 * math.pi * (k + 0.5) / 20
        varas.append(cil((raio(4) * math.cos(a), 4, raio(4) * math.sin(a)), ((raio(H - 10) + 2.2) * math.cos(a), H - 10, (raio(H - 10) + 2.2) * math.sin(a)), 3.4, 'vime', n=6))
    RA, HA = raio(H) + 1.0, 340.0 - H - 6
    alca = []
    for dz, fase in ((-5.0, 0.0), (5.0, math.pi)):                                               # alça de duas varas trançadas
        pts = []
        for k in range(25):
            a = math.pi * k / 24
            pts.append(G(RA * math.cos(a), H - 6 + HA * math.sin(a) ** 0.85, dz * math.cos(9 * a + fase)))
        alca.append(lib.fio(pts, 5.2, 'vime', fechado=False, res=2))
    forro = [lib.lathe([(0, 0), (0, raio(104) - 9), (6, raio(110) - 9), (30, raio(110) - 50), (40, 0)], 'pano_cru', n=32, c0=G(0, 100, 0), eixo=G(0, 1, 0))]

    def folha(j, X, Y, Z, R, Hh):
        def f(t, a):
            if t < 0.75:
                u = t / 0.75
                r = R * math.sin(math.pi * (0.10 + 0.46 * u)) ** 0.7 * (1 + (0.03 + 0.07 * u) * math.sin(9 * a + j * 1.7) + 0.03 * u * math.sin(23 * a + j))
                return (X + r * math.sin(a), Y + Hh * u + 5 * u * math.sin(6 * a + j), Z + r * math.cos(a))
            u = (t - 0.75) / 0.25
            r = R * (1 + 0.07 * math.sin(9 * a + j * 1.7)) * (0.97 - 0.9 * u)
            return (X + r * math.sin(a), Y + Hh * (1 - 0.45 * u), Z + r * math.cos(a))
        return _sup(f, 14, 32, 'alface' if j < 2 else 'alface_claro')
    AX, AY, AZ = -58.0, 104.0, -40.0
    alf = [folha(0, AX, AY, AZ, 80, 84), folha(1, AX + 3, AY + 6, AZ - 2, 68, 92), folha(2, AX - 2, AY + 12, AZ + 3, 54, 96),
           lib.lathe([(0, 0), (6, 26), (24, 41), (46, 41), (64, 26), (70, 0)], 'alface_claro', n=18, c0=G(AX, AY + 36, AZ), eixo=G(0, 1, 0))]
    tom, cal = [], []
    for (x, yv, z, R) in ((84, 146, 48, 35), (104, 144, -40, 33), (22, 146, 104, 33), (46, 172, 14, 31), (34, 146, -118, 32), (-52, 144, 112, 30), (-128, 142, 44, 30), (68, 150, -84, 30), (-40, 170, 66, 30)):
        a, b = _tomate(x, yv, z, R)
        tom += a
        cal += b
    cen, fol = [], []
    for tip, head in (((136, 150, 80), (20, 192, 150)), ((122, 168, 56), (-2, 208, 132)), ((-140, 150, 30), (-84, 196, 124)), ((112, 150, -116), (150, 190, -14)), ((130, 172, -60), (120, 200, 76)), ((-20, 150, -150), (-120, 196, -100))):
        a, b = _cenoura(tip, head)
        cen += a
        fol += b
    raiz = parte('cesto', [cesto] + varas, origem=G(0, 0, 0), grupo='A', suave=50)
    parte('alca', alca, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=60)
    parte('forro', forro, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=50)
    parte('alface', alf, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=60)
    parte('tomates', tom + cal, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=50)
    parte('cenouras', cen + fol, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=50)
    return raiz


FORMAS = {'lata_feijao': lata_feijao, 'lata_milho': lata_milho, 'lata_sardinha': lata_sardinha, 'pacote_arroz': pacote_arroz,
          'caixa_cereal': caixa_cereal, 'caixa_leite': caixa_leite, 'salgadinho': salgadinho, 'barra_chocolate': barra_chocolate, 'arroz_cozido': arroz_cozido,
          'saco_farinha': saco_farinha, 'pao_velho': pao_velho, 'pao_caseiro': pao_caseiro, 'carne_crua': carne_crua,
          'carne_defumada': carne_defumada, 'cesto_legumes': cesto_legumes}
