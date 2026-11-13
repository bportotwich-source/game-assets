"""Carregadores avulsos no nível de detalhe da M4A1. Cada um nasce do carregador que já vem na
arma refeita (mesmo encaixe, mesma boca, mesmos lábios), no tamanho do avulso, e os que não têm
par na arma (tambores, o de 60 de quatro fileiras, a caixa de 25 do .22, o carregador rápido do
.38) são peças deste arquivo. Desenho próprio, sem marcas.

Coordenadas em mm (../m4a1/lib.py), as do modelo de cada arma: u = para a frente, v = para cima,
w = direita. A origem de cada acessório (config.py) é o nó "carregador" da arma, onde fica o
encaixe_carregador. No fim, as peças viram uma malha só, "carregador".
"""
import math, os, importlib.util
import bpy
from mathutils import Matrix, Vector
from shapely.geometry import Polygon, LineString, Point
from lib import *
from lib import _obj

def pl(g):
    return [(float(x), float(y)) for x, y in list(g.exterior.coords)[:-1]]


def arred(pts, r, n=6):
    """Polígono com os cantos arredondados (raio r)."""
    g = pts if hasattr(pts, 'exterior') else Polygon(pts)
    return g.buffer(-r, quad_segs=n).buffer(2 * r, quad_segs=n).buffer(-r, quad_segs=n)


def solido(g, a, b, mat, plane='uv'):
    """Extrusão de um polígono shapely (os furos viram cortes)."""
    o = extr(pl(g), a, b, mat, plane)
    if g.interiors:
        m = 1.0 if a < b else -1.0
        cut(o, [extr([(float(x), float(y)) for x, y in list(i.coords)[:-1]], a - m, b + m, mat, plane) for i in g.interiors])
    return o


def lados(s, a, b):
    return sorted((s * a, s * b))


import texturas
# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES['janela_fume'] = ((0.016, 0.017, 0.018), 0.12, 0.0, (0.05, 0.05, 0.05), 0.2, 0.0, 0.2, 0.2, 0.5)   # janela de contagem, plástico fumê

ARMAS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CARREGADOS = {}


def arma(pasta, arq='modelo', variante=''):
    """Módulo de uma arma refeita (com as cores dela), sem esconder o modelo.py da M4A1."""
    chave = (pasta, arq, variante)
    if chave not in _CARREGADOS:
        antes = os.environ.get('VARIANTE', '')
        os.environ['VARIANTE'] = variante
        try:
            mat = os.path.join(ARMAS, pasta, 'materiais.py')
            if os.path.exists(mat):
                spec = importlib.util.spec_from_file_location(f'{pasta}_materiais', mat)
                spec.loader.exec_module(importlib.util.module_from_spec(spec))
            spec = importlib.util.spec_from_file_location(f'{pasta}_{arq}_{variante}', os.path.join(ARMAS, pasta, arq + '.py'))
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
        finally:
            os.environ['VARIANTE'] = antes
        _CARREGADOS[chave] = m
    return _CARREGADOS[chave]


def rotulos(m, troca):
    """Troca os números gravados no carregador da arma ("30" -> "40")."""
    orig = m.texto
    m.texto = lambda s, *a, **k: orig(troca.get(s, s), *a, **k)


def trocar_material(mapa):
    for o in PARTES:
        for i, x in enumerate(o.data.materials):
            if x and x.name in mapa:
                o.data.materials[i] = M(mapa[x.name])


def unir(grupo='A'):
    """Todas as peças numa malha só ("carregador"), no lugar."""
    bpy.context.view_layer.update()
    obs = list(PARTES)
    for o in obs:
        mw = o.matrix_world.copy()
        o.parent = None
        o.matrix_world = mw
    bpy.context.view_layer.update()
    for o in obs:
        o.data.transform(o.matrix_world)
        o.matrix_world = Matrix.Identity(4)
    bpy.ops.object.select_all(action='DESELECT')
    for o in obs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    bpy.ops.object.join()
    u = obs[0]
    u.name = u.data.name = 'carregador'
    u['grupo'] = grupo
    PARTES[:] = [u]
    return u


def aumentar(esc):
    """Aumenta em torno da origem do desenho (o .308 de precisão é a M4A1 com 10 % a mais)."""
    bpy.context.view_layer.update()
    for o in PARTES:
        if o.parent is None:
            o.data.transform(Matrix.Scale(esc, 4))
            o.location = o.location * esc
    for o in PARTES:
        if o.parent is not None:
            o.data.transform(Matrix.Scale(esc, 4))
            o.location = o.location * esc


# ================================================================== 5,56 (peças da M4A1, nas coordenadas dela)
def c556_30():
    import acessorios as m4ac
    m4ac.carregador_polimero()
    unir()


def c556_30_tan():
    import acessorios as m4ac
    m4ac.carregador_polimero()
    trocar_material({'polim': 'tan'})
    unir()


def tambor_556_60():
    import acessorios as m4ac
    m4ac.carregador_tambor()
    unir()


def tambor_556_60_tatico():
    """O tambor com janela de contagem na tampa (as pontas dos cartuchos à vista), duas abas de
    pega dos lados e alavanca de carregar no lugar da borboleta de corda."""
    import acessorios as m4ac
    VC = -140.0
    m4ac.carregador_tambor()
    o = []
    # janela em arco na tampa da frente: fenda funda com as pontas de cobre dentro e moldura
    jan = Polygon([(r * math.sin(a), VC + r * math.cos(a)) for r, aa in ((44, 1), (31, -1)) for a in
                   [math.radians(-50 + 100 * i / 16) for i in (range(17) if aa > 0 else range(16, -1, -1))]])
    tb = next(x for x in PARTES if x.name == 'carregador_tambor')
    cut(tb, [solido(jan, -10.0, 2.0, 'polim', plane='wv')])
    for i in range(9):
        a = math.radians(-44 + 11 * i)
        o.append(lathe([(0, 2.6), (3.0, 2.0), (5.0, 0.9), (5.6, 0)], 'cobre', n=12,
                       c0=(-10.5, VC + 37.5 * math.cos(a), 37.5 * math.sin(a)), eixo=(1, 0, 0)))
    o.append(solido(jan.buffer(2.2, quad_segs=4).difference(jan), -4.4, -3.0, 'fosf', plane='wv'))        # moldura
    for s in (-1, 1):                                                                                     # abas de pega
        a_ = bevel(extr([(s * 50, VC + 12), (s * 60, VC + 8), (s * 60, VC - 8), (s * 50, VC - 12)], -60, -24, 'polim', plane='wv'), 1.6, 2, 40)
        cut(a_, [extr([(s * 52, VC + 5), (s * 58, VC + 3), (s * 58, VC - 3), (s * 52, VC - 5)], -56, -28, 'polim', plane='wv')])
        o.append(a_)
    o.append(bevel(box(-90, -84, VC + 20, VC + 46, -5, 5, 'fosf'), 1.2, 2, 40))                          # alavanca de carregar
    o.append(cyl((-90, VC + 33, 0), (-80, VC + 33, 0), 4.0, 'fosf', n=16))
    parte('extras', o, origem=(-40, VC, 0))
    unir()


def _quadro(R, S0):
    def quadro(s):
        if s <= S0:
            return Vector((-40.0, -22.0 - s)), Vector((1.0, 0.0))
        f = (s - S0) / R
        return Vector((-40.0 + R - R * math.cos(f), -22.0 - S0 - R * math.sin(f))), Vector((math.cos(f), math.sin(f)))
    return quadro


def c556_60():
    """Carregador longo de alumínio de quatro fileiras: a boca é a do de 30 e, abaixo do poço, o
    corpo engorda para 39 mm; nervuras estampadas, janelas de contagem atrás, base de polímero."""
    R, S0, LT = 300.0, 72.0, 258.0
    quadro = _quadro(R, S0)
    meia = [(30.5, 0.0), (30.5, 2.2), (29.9, 3.0), (29.9, 8.6), (27.4, 11.2), (-27.4, 11.2), (-29.9, 8.6), (-29.9, 2.6), (-30.9, 2.0), (-30.9, 0.0)]
    sec = meia + [(x, -y) for (x, y) in reversed(meia[1:-1])]

    def gordo(s):
        return 8.2 * min(1.0, max(0.0, (s - 54) / 26)) ** 2 * (3 - 2 * min(1.0, max(0.0, (s - 54) / 26))) / 1.0 if s > 54 else 0.0

    def anel(s, esc=0.0, e2=0.0):
        c, e = quadro(s)
        g = gordo(s) + e2
        out = []
        for (x, y) in sec:
            q = c + e * (x + math.copysign(esc, x))
            yy = y + (math.copysign(g + esc, y) if abs(y) > 0.01 else 0)
            out.append(P(q.x, q.y, yy))
        return out
    ss = [0, 2, 24, 48, 54, 60, 66, 72, 78, 84] + [84 + (LT - 84) * i / 16 for i in range(1, 17)]
    corpo = loft([anel(s) for s in ss], 'magal')
    cs = [box(-67.5, -12.5, -40, -10, -9.6, 9.6, 'magal'), box(-92, -64, -44.5, -36.5, -12, -9.9, 'magal')]
    for s in (-1, 1):                                                                    # nervuras estampadas (rebaixos)
        for k in range(3):
            c, e = quadro(120 + k * 44)
            t = Vector((-e.y, e.x))
            p = [tuple(c + e * x + t * y) for (x, y) in ((-22, -12), (22, -12), (22, 12), (-22, 12))]
            cs.append(extr(p, s * 18.0, s * 30, 'magal'))
    m4 = __import__('acessorios')
    m4._triangular(corpo)
    cut(corpo, cs)
    o = [bevel(corpo, 0.5, 1, 40)]
    for k in range(5):                                                                   # janelas de contagem (trás, esquerda)
        c, e = quadro(110 + k * 30)
        t = Vector((-e.y, e.x))
        o.append(cyl((c.x - e.x * 24, c.y - e.y * 24, -19.4), (c.x - e.x * 24, c.y - e.y * 24, -19.9), 2.4, 'janela_fume', n=14))
    fundo = loft([anel(LT - 0.2), anel(LT, 1.6), anel(LT + 6, 1.6), anel(LT + 8, 0.4)], 'polim')
    o.append(fundo)
    c, e = quadro(LT - 12)
    o.append(texto('60', 4.6, c.x, c.y, 19.4 + 0.05, lado=1))
    tr = bevel(extr([(-66.5, -40), (-66.5, -27.5), (-40, -26), (-13.5, -28), (-13.5, -40)], -9.4, 9.4, 'polim_claro'), 1.0, 1)
    o.append(tr)
    parte('carregador_60', o, origem=(-40, -22, 0))
    unir()


# ================================================================== .308 de precisão (peças da M4A1 x1,1)
def _ar10(LT, n_pain, janelas):
    import acessorios as m4ac
    meia = [(31, 0.0), (31, 3), (30.2, 4), (30.2, 8.4), (27.2, 11.6), (-27.2, 11.6), (-30.4, 8.4), (-30.4, 3), (-31.6, 2.2), (-31.6, 0.0)]
    R, S0 = 900.0, 70.0
    corpo, anel, quadro = m4ac._corpo_carregador(meia, R, S0, LT, 'polim')
    cortes = [box(-67.5, -12.5, -40, -10, -9.6, 9.6, 'polim')]
    for s in (-1, 1):
        for i in range(n_pain):
            c, e = quadro(80 + i * 17)
            t = Vector((-e.y, e.x))
            p = [tuple(c + e * x + t * y) for (x, y) in ((-24, -6.5), (20, -6.5), (20, 6.5), (-24, 6.5))]
            cortes.append(extr(p, s * 10.8, s * 20, 'polim'))
    o = []
    if janelas:                                                                      # janelinhas de contagem atrás
        for i in range(janelas):
            c, e = quadro(30 + i * 18)
            q = c - e * 24
            cortes.append(extr(pl(Point(q.x, q.y).buffer(2.4, 4).union(Point(q.x, q.y - 6).buffer(2.4, 4)).convex_hull), -20, 20, 'polim'))
            o.append(extr(pl(Point(q.x, q.y).buffer(2.6, 4).union(Point(q.x, q.y - 6).buffer(2.6, 4)).convex_hull), -10.0, 10.0, 'janela_fume'))
    m4ac._triangular(corpo)
    cut(corpo, cortes)
    bevel(corpo, 0.5, 1, 40)
    fundo = loft([anel(LT - 0.2), anel(LT, 1.8), anel(LT + 6, 1.8), anel(LT + 8, 0.4)], 'polim')
    tr = bevel(extr([(-66.5, -40), (-66.5, -27.5), (-40, -26), (-13.5, -28), (-13.5, -40)], -9.4, 9.4, 'polim_claro'), 1.0, 1)
    parte('carregador_308', [corpo, fundo, tr] + o, origem=(-40, -22, 0))
    aumentar(1.10)
    unir()


def ar10_20():
    _ar10(132.0, 3, 4)


def ar10_10():
    _ar10(80.0, 0, 2)


# ================================================================== 7,62 (peças do Brasa)
def c762_30():
    arma('brasa').carregador()
    unir()


def c762_30_grade():
    arma('brasa', variante='').carregador(grade=True)
    unir()


def c762_30_grade_gasto():
    arma('brasa', variante='gasto').carregador(grade=True)
    unir()


def c762_40():
    """O de 40: mesmo desenho, de polímero preto e 62 mm mais comprido pela curva."""
    b = arma('brasa', variante='')
    b.carregador(grade=True, arco=262.0)
    unir()


def tambor_762_75():
    """Tambor de 75: a torre do carregador curvo entra no poço e desce até o tambor (eixo ao longo
    do cano), com tampa abaulada de nervuras, chave de corda na frente e janela de contagem."""
    b = arma('brasa')
    b.carregador(grade=True, arco=62.0, base=False, mat='polim')
    U, V = b.CAR_U, b.CAR_V
    VC, R = V - 128.0, 60.0
    UF, UT = U + 52, U - 46                                                             # frente e trás do tambor
    tb = lathe([(UT, 0), (UT, R - 8), (UT + 3, R - 2), (UT + 9, R), (UF - 10, R), (UF - 4, R - 3), (UF, R - 10), (UF + 4, 22), (UF + 4, 0)],
               'polim', n=64, c0=(0, VC, 0))
    cs = []
    for i in range(16):                                                                 # nervuras da volta
        a = 2 * math.pi * i / 16
        cs.append(cyl((UT + 14, VC + (R + 2) * math.cos(a), (R + 2) * math.sin(a)), (UF - 14, VC + (R + 2) * math.cos(a), (R + 2) * math.sin(a)),
                      3.0, 'polim', n=10))
    cut(tb, cs)
    o = [bevel(tb, 0.8, 1, 35)]
    pesc = solido(arred([(U - 30, V - 48), (U + 34, V - 48), (U + 40, VC + R - 4), (U - 36, VC + R - 4)], 3.0, 4), -13.5, 13.5, 'polim')
    o.append(bevel(pesc, 1.2, 2, 35))
    o.append(lathe([(UF + 3, 9), (UF + 9, 9), (UF + 9, 12), (UF + 12, 12), (UF + 12, 0)], 'fosf', n=24, c0=(0, VC, 0)))        # cubo
    o.append(bevel(box(UF + 11, UF + 16, VC - 26, VC + 26, -4.5, 4.5, 'fosf'), 1.4, 2, 40))                                   # chave de corda
    for s in (-1, 1):
        o.append(cyl((UF + 11, VC + s * 22, 0), (UF + 18, VC + s * 22, 0), 6.0, 'fosf', n=18))
    jan = arred([(U - 30, VC - 4), (U + 30, VC - 4), (U + 30, VC + 4), (U - 30, VC + 4)], 2.5, 4)                             # janela do lado esquerdo
    o.append(extr(pl(jan), -R - 0.3, -R + 1.0, 'janela_fume'))
    for k in range(6):
        o.append(lathe([(0, 3.4), (4, 2.6), (7, 1.0), (7.6, 0)], 'cobre', n=12, c0=(U - 24 + k * 10, VC, -R + 8.5), eixo=(0, 0, -1)))
    parte('tambor', o, origem=(U, VC, 0))
    unir()


# ================================================================== carabina .308 de ferrolho
def c308(n):
    m = arma('carabina')
    m.CACA = n == 5
    m.carregador()
    unir()


# ================================================================== submetralhadoras
def smg(n, ml):
    m = arma('smg')
    m.ML = ml
    rotulos(m, {'30': str(n)})
    m.carregador()
    unir()


def ciclone(n, ml):
    m = arma('ciclone')
    m.ML = ml
    rotulos(m, {'30': str(n)})
    m.carregador()
    unir()


def tambor_ciclone_50():
    """Tambor de 50: torre curta no poço e o tambor com o eixo ao longo do cano, botão de corda do
    lado esquerdo e janelinha de contagem do lado direito."""
    m = arma('ciclone')
    m.ML = 88.0
    rotulos(m, {'30': '50'})
    m.carregador()
    c = m.ax(m.ML + 36, 0)
    VC, R, UC = c[1], 45.0, c[0]
    tb = lathe([(-34, 0), (-34, R - 7), (-31, R - 2), (-26, R), (26, R), (31, R - 2), (34, R - 7), (37, 14), (37, 0)], 'polim', n=56, c0=(UC, VC, 0))
    cs = []
    for i in range(12):
        a = 2 * math.pi * (i + 0.5) / 12
        cs.append(cyl((UC - 20, VC + (R + 1.6) * math.cos(a), (R + 1.6) * math.sin(a)), (UC + 20, VC + (R + 1.6) * math.cos(a), (R + 1.6) * math.sin(a)),
                      2.6, 'polim', n=10))
    cut(tb, cs)
    o = [bevel(tb, 0.7, 1, 35)]
    o.append(cyl((UC + 37, VC, 0), (UC + 41, VC, 0), 9, 'fosf', n=24, lobes=0.1))      # cubo da frente
    o.append(lathe([(0, 0), (0, 10), (2, 11), (9, 11), (10, 9), (10, 0)], 'fosf', n=24, c0=(UC, VC, -R + 1), eixo=(0, 0, -1), lobes=0.12, lobe_min=10))  # botão de corda
    jan = arred([(UC - 18, VC - 3.5), (UC + 18, VC - 3.5), (UC + 18, VC + 3.5), (UC - 18, VC + 3.5)], 2.5, 4)
    o.append(extr(pl(jan), R - 1.0, R + 0.3, 'janela_fume'))
    for k in range(4):
        o.append(lathe([(0, 2.8), (3, 2.1), (5, 0.9), (5.5, 0)], 'cobre', n=12, c0=(UC - 13 + k * 8.5, VC, R - 7.4), eixo=(0, 0, 1)))
    t0, t1 = m.ax(m.ML - 4, -m.MW + 2), m.ax(m.ML + 4, m.MW - 2)                       # pescoço que liga a torre ao tambor
    pesc = solido(arred([m.ax(m.ML - 6, -m.MW - 1), m.ax(m.ML - 6, m.MW + 1), (UC + 24, VC + R - 22), (UC - 24, VC + R - 22)], 3.0, 4),
                  -m.MZ - 1.4, m.MZ + 1.4, 'polim')
    o.append(bevel(pesc, 1.0, 2, 35))
    parte('tambor', o, origem=(UC, VC, 0))
    unir()


# ================================================================== .22
def c22_10():
    arma('pardal').carregador()
    unir()


def c22_25():
    """Caixa comprida de 25: corpo reto de polímero que desce do poço, mola de aço à vista pela
    fenda de contagem, lábios de aço e base com pega estriada."""
    m = arma('pardal')
    U, V = m.CAR_U, m.CAR_V
    baixo = V - 107.0
    c = solido(arred([(U - 17, baixo), (U + 15, baixo), (U + 19, V - 30), (U + 19, V), (U - 19, V), (U - 19, V - 30)], 2.5, 5), -11.2, 11.2, 'polim')
    cs = [box(U - 17, U + 14, V - 8, V + 5, -4.2, 4.2, 'polim')]
    fen = arred([(U - 3, V - 30), (U + 3, V - 30), (U + 3, baixo + 14), (U - 3, baixo + 14)], 2.5, 4)
    cs.append(solido(fen, -20, -9.4, 'polim'))
    for s in (-1, 1):
        a, b = lados(s, 10.2, 14)
        cs.append(solido(arred([(U - 13, V - 36), (U + 11, V - 36), (U + 11, baixo + 16), (U - 11, baixo + 16)], 3, 4), a, b, 'polim'))
    cut(c, cs)
    o = [bevel(c, 0.6, 2, 40)]
    o.append(extr(pl(fen.buffer(-0.2)), -9.6, -9.0, 'janela_fume'))
    for k in range(12):                                                                  # marcas de 5 em 5
        if k % 2 == 0:
            v = V - 34 - k * 5.5
            o.append(box(U + 4.5, U + 7.5, v - 0.5, v + 0.5, -11.35, -11.1, 'tinta'))
    o.append(texto('25', 3.2, U + 9, baixo + 8, -11.22))
    base = solido(arred([(U - 18.5, baixo - 4.5), (U + 16.5, baixo - 4.5), (U + 16.5, baixo + 1.5), (U - 18.5, baixo + 1.5)], 1.8, 4), -12.9, 12.9, 'polim')
    rs = []
    for s in (-1, 1):
        a, b = lados(s, 12.1, 14)
        rs += [box(U - 14 + i * 4.0, U - 12.2 + i * 4.0, baixo - 6, baixo + 3, a, b, 'polim') for i in range(7)]
    cut(base, rs)
    o.append(bevel(base, 0.6, 1, 40))
    for s in (-1, 1):                                                                    # lábios de aço
        a, b = lados(s, 2.8, 6.2)
        o.append(box(U - 16, U + 12, V - 3.0, V + 0.8, a, b, 'fosf'))
    o += m.cartucho((U - 15.5, V - 3.0, 0.0))
    parte('carregador', o, origem=(U, V, 0))
    unir()


# ================================================================== pistolas
def guardia(n):
    m = arma('guardia')
    if n == 20:
        m.ML = 112.0 + 14.0
    m.carregador()
    if n == 20:                                                                          # luva de polímero que continua o cabo
        f = lambda t, k: m.ax(m.ML + t, k)
        luva = solido(arred([f(-24, -m.MW - 3.6), f(-24, m.MW + 3.0), f(5, m.MW + 5.6), f(9, m.MW + 4.2), f(9, -m.MW - 3.6)], 3.0, 5),
                      -m.MZ - 3.6, m.MZ + 3.6, 'polim_areia')
        cs = []
        for s in (-1, 1):                                                                # estrias como as do cabo
            a, b = lados(s, m.MZ + 2.6, m.MZ + 6)
            cs += [solido(Polygon([f(-20 + i * 4.2, -m.MW - 5), f(-18.6 + i * 4.2, -m.MW - 5), f(-18.6 + i * 4.2, m.MW + 6), f(-20 + i * 4.2, m.MW + 6)]),
                          a, b, 'polim_areia') for i in range(6)]
        cut(luva, cs)
        parte('luva', [bevel(luva, 1.4, 2, 40)], origem=(m.T[0], m.T[1], 0))
    unir()


def sentinela(n):
    m = arma('sentinela')
    if n == 24:
        m.ML = 106.0 + 38.0
    m.carregador()
    unir()


# ================================================================== revólver .38: carregador rápido
def rapido_38():
    """Carregador rápido: corpo de alumínio que segura os 6 cartuchos no círculo das câmaras (os aros
    para trás, encostados no corpo) e o botão estriado que solta todos de uma vez."""
    m = arma('revolver')
    RC = m.RC
    corpo = lathe([(-14, 0), (-14, 15.5), (-12.6, 17.6), (-2.6, 17.6), (-1.4, 16.2), (-1.4, 0)], 'anod', n=48)
    cs = []
    for i in range(6):
        a = i * math.pi / 3
        v, w = RC * math.cos(a), RC * math.sin(a)
        cs.append(cyl((-3.2, v, w), (1, v, w), 5.9, 'anod', n=20))                       # alojamento do aro
        cs.append(cyl((-20, v, w), (1, v, w), 2.0, 'anod', n=10))                        # furo da espoleta
        b = a + math.pi / 6
        cs.append(cyl((-16, 18.6 * math.cos(b), 18.6 * math.sin(b)), (0, 18.6 * math.cos(b), 18.6 * math.sin(b)), 3.4, 'anod', n=14))   # recortes entre os cartuchos
    cut(corpo, cs)
    o = [bevel(corpo, 0.5, 1, 40)]
    o.append(lathe([(-14, 0), (-14, 5.0), (-20, 5.0), (-20, 7.8), (-22.5, 8.6), (-23.2, 7.8), (-23.2, 0)], 'fosf', n=32, lobes=0.12, lobe_min=8.0))   # botão
    o.append(cyl((-1.2, 0, 0), (2.0, 0, 0), 3.4, 'inox', n=16))                         # pino do centro
    for i in range(6):
        a = i * math.pi / 3
        o += m.cartucho((-1.2, RC * math.cos(a), RC * math.sin(a)))
    parte('carregador', o, origem=(0, 0, 0))
    unir()
