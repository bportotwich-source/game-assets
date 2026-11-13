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
def _almofada(L, C, A, mat, faixa, zf, solda, e=2.6, n=28):
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
    pintar(o, 'folha_aluminio' if mat != 'saco_branco' else mat, lambda c, nn: abs(c[0]) > hz - solda)
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


FORMAS = {'lata_feijao': lata_feijao, 'lata_milho': lata_milho, 'lata_sardinha': lata_sardinha, 'pacote_arroz': pacote_arroz,
          'caixa_cereal': caixa_cereal, 'caixa_leite': caixa_leite, 'salgadinho': salgadinho, 'barra_chocolate': barra_chocolate, 'arroz_cozido': arroz_cozido}
