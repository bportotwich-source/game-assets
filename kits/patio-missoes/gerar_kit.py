"""Kit 25: patio em estilo missoes, em ALTO DETALHE (scripts/detalhe/detalhe.py).
Casa principal de 12 x 8 m com arcada de 6 arcos e telhado de telha capa-canal em geometria; 3 casitas e um atelie de 6 x 6 m
com terraco, platibanda arredondada, vigas aparentes e gargulas de madeira; portao em arco com campanario; muros com capa de
telha; patio calcado com chafariz. Reboco texturizado, telhas de barro em fiadas onduladas, portas de tabua com cravos.
Y para cima, 1 unidade = 1 m. Padrao de medidas: PADRAO_METRICAS.md.
Dependencias: trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d bpy
"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'scripts', 'detalhe'))
from detalhe import *
import detalhe as D
from shapely.geometry import Point
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT + '/pieces', exist_ok=True)
configurar(cores={'render': (232, 218, 194), 'plaster': (240, 232, 216), 'tile_clay': (176, 84, 54), 'saltillo': (184, 104, 70), 'pavers': (170, 98, 70),
                  'wood': (110, 74, 48), 'planks': (138, 98, 64), 'plinth': (156, 110, 80), 'roofdeck': (164, 150, 132), 'water': (90, 140, 150),
                  'iron': (34, 32, 32), 'bronze': (150, 110, 60), 'glass': (150, 180, 190)},
           texturas={'render': 'render', 'plaster': 'plaster', 'tile_clay': 'render', 'saltillo': 'stone', 'pavers': 'brick', 'wood': 'planks',
                     'planks': 'planks', 'plinth': 'render', 'roofdeck': 'render'},
           out=OUT)
D.METAL.add('bronze'); MATS = D.MATS; TEX = D.TEX
MATS['water'].roughnessFactor = 0.05; MATS['water'].metallicFactor = 0.3; MATS['bronze'].metallicFactor = 0.8; MATS['bronze'].roughnessFactor = 0.35

W = 2.0; T = 0.3; RAISE = 0.15

# ============================================================================ ferramentas
def layered_wall(p, xa, xb, h, holes=(), y0=-RAISE, inner_top=None, inner='plaster', outer='render', t=T, inner_above='render'):
    """Parede estanque de reboco com buracos [(x0, x1, y0, y1)]. A camada interna (2 cm) e 'inner' ate inner_top e 'inner_above'
    acima (platibanda vista do terraco). Pivo: face externa em z=0, parede para -Z."""
    it = h - 0.005 if inner_top is None else inner_top
    xs = sorted(set([xa, xb] + [v for hh in holes for v in hh[:2]]))
    ys = sorted(set([y0, 0.0, it, h - 0.005, h] + [max(y0, v) for hh in holes for v in hh[2:]]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if k == 0:
            if cy < 0.0: return outer
            if inner_top is None and ys[j] >= h - 0.0051: return None
            return inner if cy < it else inner_above
        return outer
    for m, mesh in grid_solid(xs, ys, [-t, -t + 0.02, 0.0], cell).items(): p.add(m, mesh)
def ext(p, mat, poly, z0, z1):
    for g in getattr(poly, 'geoms', [poly]):
        if g.geom_type == 'Polygon' and g.area > 1e-6:
            m = trimesh.creation.extrude_polygon(g, z1 - z0); m.apply_translation([0, 0, z0]); p.add(mat, D._fix(m))
def arch_shape(cx, w, ys, n=16):
    """Contorno de vao em arco pleno: retangulo ate ys + semicirculo de raio w/2."""
    r = w / 2; return Polygon([(cx - r, -50), (cx + r, -50)] + [(cx + r * math.cos(a), ys + r * math.sin(a)) for a in np.linspace(0, math.pi, n)])
def arch_fill(p, cx, w, ys, t=T, outer='render', inner='plaster'):
    """Tímpanos do arco: preenchem o buraco retangular (ate ys + w/2) fora do semicirculo, nas 2 camadas da parede."""
    r = w / 2; box_ = sbox(cx - r, ys, cx + r, ys + r); fill = box_.difference(arch_shape(cx, w, ys, 24))
    ext(p, outer, fill, -t + 0.02, 0.0); ext(p, inner, fill, -t, -t + 0.02)
def plinth(p, xa, xb, gaps=(), top=0.35):
    """Barrado (zócalo) pintado de 2 cm, que para nos vaos de porta."""
    xs = [xa] + [v for g in gaps for v in g] + [xb]
    for i in range(0, len(xs) - 1, 2):
        if xs[i + 1] - xs[i] > 0.01: prof_x(p, 'plinth', xs[i] + 0.0012, xs[i + 1] - 0.0012, crect(0.0, 0.02, -RAISE, top, 0.006, (0, 1, 1, 0)))
def seg_cyl(p, mat, p0, p1, r, sec=10):
    p0, p1 = np.array(p0, float), np.array(p1, float); v = p1 - p0; L = np.linalg.norm(v)
    c = trimesh.creation.cylinder(radius=r, height=L, sections=sec); z = np.array([0, 0, 1.0]); v = v / L
    ax = np.cross(z, v); ang = math.acos(np.clip(np.dot(z, v), -1, 1))
    if np.linalg.norm(ax) > 1e-6: c.apply_transform(trimesh.transformations.rotation_matrix(ang, ax))
    elif v[2] < 0: c.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
    c.apply_translation((p0 + p1) / 2); return p.add(mat, c)

# ---------- telha capa-canal em geometria ----------
TP = 0.25; TA = 0.06; TC = 0.33; TLIP = 0.035
def tile_course(p, xa, xb, za, zb, f, lip=TLIP):
    """Uma fiada de telha capa-canal entre za (borda de baixo, para o beiral) e zb (borda de cima). Onda de passo TP:
    capas (cristas) e canais; a borda de baixo levanta 'lip' (degrau entre fiadas). f(z) = face de baixo do telhado."""
    xs = sorted(set([xa, xb] + [k * TP / 6 for k in range(int(math.floor(xa / (TP / 6))) + 1, int(math.ceil(xb / (TP / 6))))]))
    wv = lambda x: TA * math.sin(math.pi * x / TP) ** 2
    V = []
    for x in xs:
        w = wv(x); V += [(x, f(za) + 0.02 + w + lip, za), (x, f(zb) + 0.02 + w, zb), (x, f(za) + 0.006, za), (x, f(zb) + 0.006, zb)]
    F = []; n = len(xs)
    for i in range(n - 1):
        a, b = 4 * i, 4 * (i + 1)
        F += [[a, b, b + 1], [a, b + 1, a + 1], [a + 2, a + 3, b + 3], [a + 2, b + 3, b + 2], [a, a + 2, b + 2], [a, b + 2, b], [a + 1, b + 1, b + 3], [a + 1, b + 3, a + 3]]
    e = 4 * (n - 1); F += [[0, 1, 3], [0, 3, 2], [e, e + 2, e + 3], [e, e + 3, e + 1]]
    m = trimesh.Trimesh(np.array(V), np.array(F), process=True); m.fix_normals(); p.add('tile_clay', m)
def tile_field(p, xa, xb, z_eave, z_top, f):
    """Fiadas de z_eave (beiral, z maior) ate z_top (cumeeira, z menor), de TC em TC medidos na horizontal."""
    z = z_eave
    while z > z_top + 1e-6:
        zb = max(z - TC, z_top); tile_course(p, xa, xb, z, zb, f); z = zb
def cover_row(p, a, b, r=0.075, ring=0.4):
    """Fileira de capas (cumeeira ou beirada): meia-cana continua com aneis de emenda a cada 'ring' m."""
    seg_cyl(p, 'tile_clay', a, b, r, 12); a, b = np.array(a, float), np.array(b, float); L = np.linalg.norm(b - a); v = (b - a) / L
    for s in np.arange(ring, L - 0.05, ring): seg_cyl(p, 'tile_clay', a + v * (s - 0.03), a + v * (s + 0.01), r + 0.012, 12)

# ---------- janelas e portas ----------
def arched_window(p, cx=0.0, w=0.8, oy0=1.0, ys=2.0, reja=False, sill=True):
    """Janela em arco pleno: caixilho de madeira recuado, folhas com vidro e travessa na nascente do arco, peitoril de telha.
    O buraco retangular vai de oy0 a ys + w/2; os timpanos fecham o arco."""
    r = w / 2; zf0, zf1 = -0.2, -0.14
    outer = arch_shape(cx, w, ys).intersection(sbox(cx - r - 1, oy0, cx + r + 1, 50)); inner = arch_shape(cx, w - 0.12, ys).intersection(sbox(cx - 1, oy0 + 0.06, cx + 1, 50))
    ext(p, 'wood', outer.difference(inner), zf0, zf1)
    ext(p, 'glass', inner, -0.173, -0.167)
    p.box('wood', cx - 0.02, cx + 0.02, oy0 + 0.06, ys + r - 0.06, -0.185, -0.155); p.box('wood', cx - r + 0.06, cx + r - 0.06, ys - 0.02, ys + 0.02, -0.185, -0.155)
    if sill:
        prof_x(p, 'tile_clay', cx - r - 0.06, cx + r + 0.06, [(-0.21, oy0 - 0.04), (0.06, oy0 - 0.04), (0.075, oy0 - 0.025), (0.06, oy0 + 0.01), (-0.21, oy0 + 0.01)])
    if reja:   # grade de ferro com barras torcidas (simplificadas) e travessas
        n = max(3, int(round(w / 0.14)))
        for i in range(1, n):
            xx = cx - r + i * w / n; top = ys + math.sqrt(max(r * r - (xx - cx) ** 2, 0)) - 0.03
            p.cyl('iron', 0.011, oy0 + 0.02, top, xx, -0.05, 8)
        for yy in (oy0 + 0.25, ys - 0.1): p.box('iron', cx - r + 0.01, cx + r - 0.01, yy - 0.012, yy + 0.012, -0.062, -0.038)
    return (cx - r, cx + r, oy0, ys + r)
def door_opening(p, w, oh, depth=T, lintel=True):
    """Vao de porta com verga de madeira aparente que atravessa a parede e sobra 0,25 m de cada lado."""
    x = w / 2
    p.box('wood', -x, -x + 0.06, 0.0, oh, -0.2, -0.04); p.box('wood', x - 0.06, x, 0.0, oh, -0.2, -0.04)
    if lintel: p.cham('wood', -x - 0.25, x + 0.25, oh - 0.004, oh + 0.22, -depth - 0.005, 0.03, 0.02)
    prof_x(p, 'saltillo', -x + 0.001, x - 0.001, [(-depth - 0.005, 0.012), (0.03, 0.012), (0.05, -0.0), (0.05, -0.04), (-depth - 0.005, -0.04)])
def plank_leaf(w=1.0, h=2.2, t=0.06, studs=True):
    """Folha de tabuas verticais com frestas, 3 travessas por dentro, cravos de ferro, dobradicas em faixa e argola."""
    p = Piece(); n = max(4, int(round(w / 0.17)))
    for i in range(n):
        a = i * w / n + 0.003; b = (i + 1) * w / n - 0.003; p.cham('wood', a, b, 0.0, h, -t / 2 + 0.015, t / 2, 0.005)
    p.box('dark', 0.01, w - 0.01, 0.01, h - 0.01, -t / 2 + 0.02, t / 2 - 0.01)
    for yy in (0.2, h / 2, h - 0.2): p.cham('wood', 0.03, w - 0.03, yy - 0.07, yy + 0.07, -t / 2 - 0.012, -t / 2 + 0.015, 0.008)
    if studs:
        for yy in (0.2, h / 2, h - 0.2):
            for i in range(n): p.sphere('iron', 0.014, (i + 0.5) * w / n, yy, t / 2 + 0.004, 0)
    for yy in (0.32, h - 0.32):
        p.box('iron', 0.0, w * 0.55, yy - 0.03, yy + 0.03, t / 2, t / 2 + 0.008); p.cyl('iron', 0.018, yy - 0.05, yy + 0.05, 0.0, t / 2 + 0.006, 10)
    ring = trimesh.creation.torus(0.055, 0.008, major_sections=16, minor_sections=6); ring.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
    ring.apply_translation([w - 0.15, 1.0, t / 2 + 0.03]); p.add('iron', ring)
    p.cham('iron', w - 0.19, w - 0.11, 1.03, 1.13, t / 2, t / 2 + 0.015, 0.004)
    p.cham('iron', w - 0.19, w - 0.11, 0.97, 1.07, -t / 2 - 0.015, -t / 2, 0.004)
    return p

# ============================================================================ casitas e atelie: terraco com platibanda
HC = 3.0; RS = 0.3; HP = 3.78       # forro, laje do terraco, topo da platibanda
VY = HC - 0.13                     # eixo das vigas
def parapet_cap(p, xa, xb, t=T):
    """Capa arredondada da platibanda (meia elipse de 7 cm, sobra 1,2 cm de cada lado)."""
    arcp = [(-t / 2 + (t / 2 + 0.012) * math.cos(a), HP + 0.07 * math.sin(a)) for a in np.linspace(0, math.pi, 11)][1:-1]
    prof_x(p, 'render', xa, xb, [(-t - 0.012, HP - 0.03), (0.012, HP - 0.03)] + arcp)
def viga_ends(p, xs=(-0.5, 0.5), out=0.42):
    """Pontas das vigas redondas saindo 0,42 m da parede, logo abaixo do terraco."""
    for xx in xs:
        c = Piece(); c.cyl('wood', 0.11, -T - 0.01, out, sec=12)
        for m in c.parts['wood']: m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])); m.apply_translation([xx, VY, 0]); p.add('wood', m)
def canale(p, x=0.0):
    """Gargula de madeira (canal em U) saindo da platibanda no nivel do terraco."""
    y = HC + RS + 0.005
    p.box('wood', x - 0.1, x + 0.1, y - 0.04, y, -T - 0.05, 0.7); p.box('wood', x - 0.1, x - 0.07, y, y + 0.12, -T - 0.05, 0.7); p.box('wood', x + 0.07, x + 0.1, y, y + 0.12, -T - 0.05, 0.7)
def c_wall(kind='plain', vig=True):
    """Modulo de 2 m da casita: reboco ate a platibanda, camada interna de gesso ate o forro, barrado, vigas aparentes.
    kind: plain, window, small, door, canale, back."""
    p = Piece(); holes = []
    if kind == 'window': holes = [(-0.45, 0.45, 0.95, 2.4)]
    if kind == 'small': holes = [(-0.3, 0.3, 1.5, 2.3)]
    if kind == 'door': holes = [(-0.5, 0.5, 0.0, 2.2)]
    layered_wall(p, -W / 2, W / 2, HP - 0.03, holes, inner_top=HC)
    if kind == 'window': arched_window(p, 0, 0.9, 0.95, 1.95, reja=True); arch_fill(p, 0, 0.9, 1.95)
    if kind == 'small': arched_window(p, 0, 0.6, 1.5, 2.0); arch_fill(p, 0, 0.6, 2.0)
    if kind == 'door': door_opening(p, 1.0, 2.2)
    plinth(p, -W / 2, W / 2, [(-0.5, 0.5)] if kind == 'door' else [])
    parapet_cap(p, -W / 2, W / 2)
    if vig: viga_ends(p)
    if kind == 'canale': canale(p)
    return p
def c_corner():
    """Quina com contraforte: bloco 4 cm saliente nas 2 faces, base em talude e capa arredondada."""
    p = Piece(); e = 0.04
    p.box('render', -T - 0.01, e, -RAISE, HP - 0.03, -T - 0.01, e)
    p.hull('render', [(x, y, z) for (x, z) in ((-T - 0.01, -T - 0.01), (e + 0.12, -T - 0.01), (e + 0.12, e + 0.12), (-T - 0.01, e + 0.12)) for y in (-RAISE, 0.1)] +
           [(x, 0.9, z) for (x, z) in ((-T - 0.01, -T - 0.01), (e + 0.001, -T - 0.01), (e + 0.001, e + 0.001), (-T - 0.01, e + 0.001))])
    p.hull('render', [(x, y, z) for x in (-T - 0.035, e + 0.03) for z in (-T - 0.035, e + 0.03) for y in (HP - 0.03, HP + 0.085)] + [(-T / 2 + 0.02, HP + 0.15, -T / 2 + 0.02)])
    return p
def party_wall(end=False, h=HP - 0.03):
    """Parede entre 2 casitas (eixo no meio): gesso dos 2 lados ate o forro, reboco acima, capa arredondada. end: termina 0,3 m antes."""
    p = Piece(); t = T; x1 = W / 2 - (T if end else 0.0)
    xs = [-W / 2, x1]; ys = [0.0, HC, h]; zs = [-t / 2, -t / 2 + 0.02, t / 2 - 0.02, t / 2]
    def cell(i, j, k): return ('plaster' if j == 0 else 'render') if k != 1 else 'render'
    for m, mesh in grid_solid(xs, ys, zs, cell).items(): p.add(m, mesh)
    q = Piece(); parapet_cap(q, -W / 2, x1); p.merge(q, trimesh.transformations.translation_matrix([0, 0, T / 2]))
    return p
def c_roof(wx, wz, chimney=None):
    """Laje do terraco (wx x wz, centrada): manta por cima com caimento para as gargulas, forro de gesso, vigas redondas e latilhas."""
    p = Piece(); x0, x1, z0, z1 = -wx / 2, wx / 2, -wz / 2, wz / 2
    p.box('plaster', x0, x1, HC, HC + RS - 0.02, z0, z1); p.box('roofdeck', x0 + 0.002, x1 - 0.002, HC + RS - 0.02, HC + RS, z0 + 0.002, z1 - 0.002)
    for i in range(int(wz / 0.1)):
        zz = z0 + (i + 0.5) * wz / int(wz / 0.1); p.box('planks', x0, x1, HC - 0.025, HC, zz - 0.045, zz + 0.045)
    return p
def c_vigas(wx, zs):
    p = Piece()
    for zz in zs: seg_cyl(p, 'wood', (-wx / 2, VY, zz), (wx / 2, VY, zz), 0.11, 12)
    return p
def kiva():
    """Lareira de canto (kiva): corpo arredondado com boca em arco, coifa conica, banco de pedra. Pivo: quina interna."""
    p = Piece(); r = 0.95
    pts = [(math.cos(a) * r, math.sin(a) * r) for a in np.linspace(0, math.pi / 2, 9)]
    body = [(x, y, z) for (x, z) in pts + [(0, 0)] for y in (0.0, 1.25)]
    p.hull('render', [(x + 0.02, y, z + 0.02) for x, y, z in body])
    p.hull('render', [(x * 0.75 + 0.02, 1.25, z * 0.75 + 0.02) for (x, z) in pts + [(0, 0)]] + [(0.12, HC - 0.02, 0.12), (0.4, HC - 0.02, 0.12), (0.12, HC - 0.02, 0.4), (0.4, HC - 0.02, 0.4)])
    c = r * 0.70710678; n = np.array([1, 0, 1]) / math.sqrt(2); tdir = np.array([-1, 0, 1]) / math.sqrt(2); base = np.array([c, 0, c]) * 1.005 + np.array([0.02, 0, 0.02])
    hole = arch_shape(0, 0.62, 0.5, 12).intersection(sbox(-1, 0.25, 1, 2))
    g = trimesh.creation.extrude_polygon(hole, 0.02); M = np.eye(4); M[:3, 0] = tdir; M[:3, 1] = [0, 1, 0]; M[:3, 2] = n; M[:3, 3] = base - n * 0.012
    g.apply_transform(M); p.add('dark', D._fix(g))
    p.hull('saltillo', [(x * 1.15, y, z * 1.15) for (x, z) in pts + [(0, 0)] for y in (0.0, 0.18)])
    return p
def chimney_roof():
    """Chamine de reboco no terraco com capa e 2 manilhas. Pivo: base no nivel do terraco."""
    p = Piece(); a = 0.3
    p.box('render', -a, a, -0.02, 1.1, -a, a); p.hull('render', [(x, 1.1, z) for x in (-a - 0.03, a + 0.03) for z in (-a - 0.03, a + 0.03)] + [(x, 1.17, z) for x in (-a, a) for z in (-a, a)])
    for xx in (-0.13, 0.13): p.cyl('tile_clay', 0.07, 1.12, 1.42, xx, 0, 12); p.cyl('dark', 0.052, 1.4, 1.425, xx, 0, 12)
    return p
def door_hood(w=1.7, d=0.75):
    """Alpendre de telhas sobre a porta da casita: 2 maos-francesas de madeira, terça e 3 fiadas de telha. Pivo: face da parede."""
    p = Piece(); y0 = 2.6; k = 0.45
    f = lambda z: y0 - k * z
    for s in (-1, 1):
        x = s * (w / 2 - 0.12); p.cham('wood', x - 0.06, x + 0.06, 2.3, y0 - 0.02, 0.0, 0.1, 0.01)
        p.hull('wood', [(x + dx, y, z) for dx in (-0.06, 0.06) for (y, z) in ((2.42, 0.08), (2.55, 0.08), (f(d - 0.12) - 0.03, d - 0.08), (f(d - 0.12) - 0.15, d - 0.12))])
    prof_x(p, 'wood', -w / 2 + 0.01, w / 2 - 0.01, crect(d - 0.16, d - 0.04, f(d - 0.1) - 0.14, f(d - 0.1) - 0.005, 0.01))
    prof_x(p, 'planks', -w / 2, w / 2, [(0.004, f(0.004)), (d - 0.01, f(d - 0.01)), (d - 0.01, f(d - 0.01) + 0.02), (0.004, f(0.004) + 0.02)])
    z = d
    while z > 0.008 + 1e-6:
        zb = max(z - TC, 0.008); tile_course(p, -w / 2 - 0.05, w / 2 + 0.05, z, zb, f); z = zb
    p.box('render', -w / 2 - 0.04, w / 2 + 0.04, y0, y0 + 0.13, 0.0, 0.035)
    return p

# ============================================================================ casa principal: arcada e telhado de telhas
YEM = 4.47; HM = YEM + 0.015; HCM = 3.9; KRM = math.tan(math.radians(25)); OVM = 0.5; HSM = 4.0; RKM = 0.3
CSM = math.cos(math.radians(25))
def under_m(z): return YEM - KRM * z
def m_wall(kind='plain', front=False):
    """Modulo de 2 m da casa principal (reboco ate 4,5 m, gesso ate o forro de 3,9 m). kind: plain, window, door, side_door, small."""
    p = Piece(); holes = []
    if kind == 'window': holes = [(-0.5, 0.5, 0.85, 2.85)]
    if kind == 'small': holes = [(-0.35, 0.35, 1.5, 2.55)]
    if kind == 'door': holes = [(-0.6, 0.6, 0.0, 2.4)]
    if kind == 'side_door': holes = [(-0.5, 0.5, 0.0, 2.2)]
    layered_wall(p, -W / 2, W / 2, HM, holes, inner_top=HCM)
    if kind == 'window': arched_window(p, 0, 1.0, 0.85, 2.35, reja=not front); arch_fill(p, 0, 1.0, 2.35)
    if kind == 'small': arched_window(p, 0, 0.7, 1.5, 2.2); arch_fill(p, 0, 0.7, 2.2)
    if kind == 'door': door_opening(p, 1.2, 2.4)
    if kind == 'side_door': door_opening(p, 1.0, 2.2)
    plinth(p, -W / 2, W / 2, [(-0.6, 0.6)] if kind == 'door' else [(-0.5, 0.5)] if kind == 'side_door' else [])
    return p
def m_corner():
    p = Piece(); e = 0.04
    p.box('render', -T - 0.01, e, -RAISE, HM - 0.06, -T - 0.01, e)
    p.hull('render', [(x, y, z) for (x, z) in ((-T - 0.01, -T - 0.01), (e + 0.12, -T - 0.01), (e + 0.12, e + 0.12), (-T - 0.01, e + 0.12)) for y in (-RAISE, 0.1)] +
           [(x, 0.9, z) for (x, z) in ((-T - 0.01, -T - 0.01), (e + 0.001, -T - 0.01), (e + 0.001, e + 0.001), (-T - 0.01, e + 0.001))])
    return p
def m_gable():
    """Oitao de reboco acima do beiral, com oculo de ventilacao (anel de telha com grade). Pivo: face da parede, meio da empena."""
    p = Piece(); x = HSM - (HM - YEM - 0.01) / KRM
    tri = Polygon([(-x, HM), (x, HM), (0, under_m(-HSM) + 0.01)])
    vy = HM + 0.95; hole = Point(0, vy).buffer(0.28, 16)
    ext(p, 'render', tri.difference(hole), -T + 0.02, 0.0); ext(p, 'plaster', tri.difference(hole), -T, -T + 0.02)
    ext(p, 'tile_clay', Point(0, vy).buffer(0.36, 16).difference(Point(0, vy).buffer(0.28, 16)), 0.0, 0.04)
    p.box('dark', -0.29, 0.29, vy - 0.29, vy + 0.29, -0.2, -0.18)
    for a in (0, 60, 120):
        q = Piece(); q.box('tile_clay', -0.28, 0.28, -0.02, 0.02, -0.14, -0.1); R = trimesh.transformations.rotation_matrix(math.radians(a), [0, 0, 1]); R[:3, 3] = [0, vy, 0]
        p.merge(q, R)
    return p
def rafters(p, xs, f, z0, z1, w=0.08, d=0.16):
    """Caibros aparentes de 8 x 16 cm sob o forro de tabuas, com a ponta chanfrada."""
    for xx in xs: p.hull('wood', [(xx + dx, f(z) - dy, z) for dx in (-w / 2, w / 2) for z in (z0, z1 - 0.06) for dy in (0.0, d)] + [(xx + dx, f(z1) - dy, z1) for dx in (-w / 2, w / 2) for dy in (0.0, d * 0.45)])
def m_roof(x0=-W / 2, x1=W / 2, rake=0):
    """Faixa de 2 m de uma agua da casa principal (beiral em z=OVM, cumeeira em z=-HSM). Forro de tabuas, telhas, caibros
    aparentes no beiral; rake = -1/+1: beirada na ponta (fileira de capas e tabua de testeira)."""
    p = Piece(); f = under_m
    xa = x0 - (RKM if rake < 0 else 0); xb = x1 + (RKM if rake > 0 else 0)
    prof_x(p, 'planks', xa - 0.002 * (rake >= 0), xb + 0.002 * (rake <= 0), [(OVM - 0.01, f(OVM - 0.01)), (-HSM + 0.004, f(-HSM + 0.004)), (-HSM + 0.004, f(-HSM + 0.004) + 0.02), (OVM - 0.01, f(OVM - 0.01) + 0.02)])
    tile_field(p, xa, xb, OVM, -HSM, f)
    xs = [xx for xx in np.arange(-0.75, 0.76, 0.5) if xa + 0.05 < xx < xb - 0.05]
    rafters(p, xs, lambda z: f(z), 0.0, OVM - 0.02)
    if rake:
        xr = xa if rake < 0 else xb
        cover_row(p, (xr - rake * 0.0, f(OVM) + 0.02 + TA + TLIP, OVM + 0.03), (xr, f(-HSM) + 0.02 + TA, -HSM), 0.075)
        a_, b_ = sorted((xr, xr + rake * 0.05))
        prof_x(p, 'wood', a_, b_, [(OVM + 0.02, f(OVM + 0.02) + 0.02), (-HSM, f(-HSM) + 0.02), (-HSM, f(-HSM) - 0.2), (OVM + 0.02, f(OVM + 0.02) - 0.2)])
    return p
def m_ridge(x0, x1):
    p = Piece(); y = under_m(-HSM) + 0.02 + TA + 0.01
    p.hull('render', [(x, y + dy, z) for x in (x0 + 0.01, x1 - 0.01) for (dy, z) in ((-0.06, -0.14), (-0.06, 0.14), (0.03, 0.0))])
    cover_row(p, (x0, y + 0.02, 0.0), (x1, y + 0.02, 0.0), 0.11, 0.42); return p

# ---------- arcada (portal) ----------
AD = 2.6; AS = 2.1; AR = 0.75; AH = 3.12; AY0 = 3.85; AK = math.tan(math.radians(15)); AOV = 0.3
def a_under(z): return AY0 - AK * z          # z a partir da parede da casa (face externa)
def arcade_arch():
    """Arco de 2 m da arcada: meio pilar de cada lado, arco pleno de 1,5 m, frontal ate 3,12 m e frechal de madeira inclinado.
    Pivo: face da frente da arcada (z=0, recuada 2,6 m da casa), eixo do arco, cota do piso da arcada."""
    p = Piece(); t = 0.5
    poly = sbox(-W / 2, -RAISE, W / 2, AH).difference(arch_shape(0, 2 * AR, AS, 24))
    ext(p, 'render', poly, -t, 0.0)
    for s in (-1, 1):   # impostas (capitel simples) e base dos pilares
        a, b = sorted((s * W / 2, s * (W / 2 - 0.25 - 0.02)))
        p.cham('render', a, b, AS - 0.12, AS, -t - 0.025, 0.025, 0.012)
        a, b = sorted((s * W / 2 - 0.003, s * (W / 2 - 0.25 - 0.02))); p.cham('plinth', a, b, -RAISE, 0.3, -t - 0.02, 0.02, 0.008)
    zb, zf = -t, 0.0; yb, yf = a_under(AD + zb), a_under(AD + zf)
    p.hull('wood', [(x, y, z) for x in (-W / 2 + 0.0005, W / 2 - 0.0005) for (z, y) in ((zb + 0.02, AH), (zf - 0.02, AH), (zf - 0.02, yf + 0.012), (zb + 0.02, yb + 0.012))])
    return p
def arcade_end(s=1):
    """Complemento do pilar da ponta (a outra metade + retorno lateral)."""
    p = Piece(); t = 0.5
    a, b = sorted((s * W / 2, s * (W / 2 + 0.25)))
    p.box('render', a, b, -RAISE, AH, -t, 0.0)
    p.cham('render', min(a, b) - 0.02 * (s < 0), max(a, b) + 0.02 * (s > 0), AS - 0.12, AS, -t - 0.025, 0.025, 0.012)
    p.cham('plinth', min(a, b) - 0.02 * (s < 0) - 0.003 * (s > 0), max(a, b) + 0.02 * (s > 0) - 0.003 * (s < 0), -RAISE, 0.3, -t - 0.02, 0.02, 0.008)
    yb, yf = a_under(AD - t), a_under(AD)
    pa, pb = sorted((s * (W / 2 + 0.0005), s * (W / 2 + 0.248)))
    p.hull('wood', [(x, y, z) for x in (pa, pb) for (z, y) in ((-t + 0.02, AH), (-0.02, AH), (-0.02, yf + 0.012), (-t + 0.02, yb + 0.012))])
    return p
def arcade_floor(end=0):
    """Piso da arcada (2 m x 2,6 m): lajotas, laje e degrau de frente com bocel. Pivo: face da casa, cota do piso."""
    p = Piece(); x0 = -W / 2 - (0.25 if end < 0 else 0); x1 = W / 2 + (0.25 if end > 0 else 0)
    p.box('saltillo', x0, x1, -0.03, 0.0, 0.0, AD + 0.04); p.box('render', x0 + 0.01 * (end < 0), x1 - 0.01 * (end > 0), -RAISE, -0.03, 0.0, AD + 0.026)
    prof_x(p, 'saltillo', x0, x1, [(AD + 0.04, -0.03), (AD + 0.07, -0.025), (AD + 0.08, -0.012), (AD + 0.07, 0.0), (AD + 0.04, 0.0)])
    if end:
        xe = x0 if end < 0 else x1; a, b = sorted((xe, xe + end * 0.03))
        prof_z(p, 'saltillo', 0.0, AD + 0.04, crect(a, b, -0.03, 0.0, 0.008))
    return p
def arcade_roof(end=0):
    """Telhado de 1 agua da arcada (2 m): forro de tabuas, caibros aparentes, telhas, rufo de argamassa na parede.
    Pivo: face da casa, cota do piso; o beiral fica em z = 2,9 m. end = -1/+1: ponta com beirada lateral."""
    p = Piece(); x0 = -W / 2 - (0.5 if end < 0 else 0); x1 = W / 2 + (0.5 if end > 0 else 0); ze = AD + AOV
    prof_x(p, 'planks', x0 - 0.002 * (end >= 0), x1 + 0.002 * (end <= 0), [(0.004, a_under(0.004)), (ze - 0.01, a_under(ze - 0.01)), (ze - 0.01, a_under(ze - 0.01) + 0.02), (0.004, a_under(0.004) + 0.02)])
    tile_field(p, x0, x1, ze, 0.008, a_under)
    xs = [xx for xx in np.arange(-0.75, 0.76, 0.5) if x0 + 0.05 < xx < x1 - 0.05] + ([-1.25] if end < 0 else []) + ([1.25] if end > 0 else [])
    rafters(p, xs, a_under, 0.0, ze - 0.02)
    p.box('render', x0 + 0.0005, x1 - 0.0005, a_under(0.0) + 0.02, a_under(0.0) + 0.17, 0.0, 0.05)   # rufo de argamassa na parede
    if end:
        xr = x0 if end < 0 else x1
        cover_row(p, (xr, a_under(ze) + 0.02 + TA + TLIP, ze + 0.03), (xr, a_under(0.05) + 0.02 + TA, 0.05), 0.075)
        a_, b_ = sorted((xr, xr + end * 0.05))
        prof_x(p, 'wood', a_, b_, [(0.0, a_under(0.0) + 0.02), (ze + 0.02, a_under(ze + 0.02) + 0.02), (ze + 0.02, a_under(ze + 0.02) - 0.2), (0.0, a_under(0.0) - 0.2)])
    return p

# ============================================================================ portao, muros, patio
GH = 1.8
def g_wall(L=W):
    """Muro de 2 m (eixo no meio, 0,3 m): reboco, barrado e capa de telha de 2 aguas com capas na cumeeira."""
    p = Piece(); a, b = -L / 2, L / 2; t = 0.3
    p.box('render', a, b, 0.0, GH - 0.02, -t / 2, t / 2)
    for s in (-1, 1): q = Piece(); plinth(q, a, b, top=0.3); p.merge(q, trimesh.transformations.translation_matrix([0, RAISE, s * t / 2]) @ (np.eye(4) if s > 0 else np.diag([1, 1, -1, 1])))
    prof_x(p, 'tile_clay', a, b, [(-t / 2 - 0.07, GH - 0.02), (t / 2 + 0.07, GH - 0.02), (t / 2 + 0.07, GH + 0.02), (0.0, GH + 0.11), (-t / 2 - 0.07, GH + 0.02)])
    cover_row(p, (a, GH + 0.12, 0.0), (b, GH + 0.12, 0.0), 0.06, 0.4)
    return p
def g_pier():
    p = Piece(); a = 0.25
    p.box('render', -a, a, 0.0, GH + 0.25, -a, a); p.cham('plinth', -a - 0.02, a + 0.02, 0.0, 0.32, -a - 0.02, a + 0.02, 0.006)
    p.hull('tile_clay', [(x, GH + 0.25, z) for x in (-a - 0.05, a + 0.05) for z in (-a - 0.05, a + 0.05)] + [(0, GH + 0.5, 0)])
    p.sphere('tile_clay', 0.06, 0, GH + 0.52, 0, 1); return p
GW = 2.4; GS = 2.5; GTH = 0.6
def gate_arch():
    """Portao de 4 m: arco pleno de 2,4 m, campanario curvo (espadana) ate 6,6 m com nicho e sino de bronze, cornija e pinaculos.
    Pivo: face externa (z=0, para fora +Z), eixo, cota do chao."""
    p = Piece(); t = GTH; L = 2.0
    body = sbox(-L, 0.0, L, 4.3)
    sh_l = [(-1.55 + 0.55 * (1 - math.cos(a)), 4.3 + 0.9 * math.sin(a)) for a in np.linspace(0, math.pi / 2, 7)]          # ombro curvo
    top_arc = [(0.75 * math.cos(a), 6.0 + 0.6 * math.sin(a)) for a in np.linspace(math.pi, 0, 13)]
    sil = [(-L, 4.3)] + sh_l + [(-0.75, 5.2)] + top_arc + [(0.75, 5.2)] + [(-x, y) for (x, y) in sh_l[::-1]] + [(L, 4.3)]
    top = Polygon([(-L, 4.29)] + sil[1:-1] + [(L, 4.29)]).buffer(0)
    niche = arch_shape(0, 0.8, 5.75, 16).intersection(sbox(-1, 4.75, 1, 9))
    shape = body.union(top).difference(arch_shape(0, GW, GS, 24)).difference(niche)
    ext(p, 'render', shape, -t, 0.0)
    prof_x(p, 'render', -L - 0.05, L + 0.05, [(-t - 0.06, 4.22), (0.06, 4.22), (0.08, 4.26), (0.08, 4.32), (-t - 0.08, 4.32), (-t - 0.08, 4.26)])
    edge = LineString_(sil[1:-1]); cap = edge.buffer(0.045, cap_style=2, join_style=2).intersection(sbox(-L, 4.33, L, 9))
    ext(p, 'render', cap, -t - 0.035, 0.035)
    p.box('render', -L - 0.05, -L + 0.4, 0.0, 0.35, -t - 0.05, 0.05); p.box('render', L - 0.4, L + 0.05, 0.0, 0.35, -t - 0.05, 0.05)
    for s in (-1, 1):   # pinaculos nos ombros e impostas do arco
        p.box('render', s * 1.65 - 0.12, s * 1.65 + 0.12, 4.32, 4.62, -t / 2 - 0.12, -t / 2 + 0.12); p.hull('render', [(s * 1.65 + dx, 4.62, -t / 2 + dz) for dx in (-0.14, 0.14) for dz in (-0.14, 0.14)] + [(s * 1.65, 4.95, -t / 2)])
        a, b = sorted((s * GW / 2, s * (GW / 2 + 0.18)))
        p.cham('render', a, b, GS - 0.12, GS, -t - 0.03, 0.03, 0.012)
    p.box('render', -0.12, 0.12, 6.64, 6.68, -t / 2 - 0.12, -t / 2 + 0.12); p.sphere('render', 0.09, 0, 6.76, -t / 2, 1)
    # sino de bronze pendurado numa travessa de madeira dentro do nicho
    p.box('wood', -0.5, 0.5, 6.02, 6.1, -t / 2 - 0.04, -t / 2 + 0.04)
    bell = trimesh.creation.revolve(np.array([[0.0, 0.0], [0.24, 0.0], [0.23, 0.04], [0.17, 0.12], [0.14, 0.32], [0.12, 0.44], [0.06, 0.48], [0.0, 0.48]]), sections=20)
    bell.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); bell.apply_translation([0, 5.3, -t / 2]); p.add('bronze', bell)
    p.cyl('iron', 0.012, 5.76, 6.02, 0, -t / 2, 8); p.sphere('iron', 0.035, 0, 5.33, -t / 2, 1)
    p.box('saltillo', -GW / 2, GW / 2, 0.0, 0.03, -t, 0.0)
    return p
def LineString_(pts):
    from shapely.geometry import LineString; return LineString(pts)
def paver_tile():
    p = Piece(); p.box('pavers', -W / 2, W / 2, 0.0, 0.04, -W / 2, W / 2); return p
def fountain():
    """Chafariz octogonal: bacia de reboco com borda de lajota, agua, coluna e taca. Pivo: centro, chao."""
    p = Piece(); R = 1.25
    oct_ = lambda r: Polygon([(r * math.cos(math.pi / 8 + k * math.pi / 4), r * math.sin(math.pi / 8 + k * math.pi / 4)) for k in range(8)])
    ring = oct_(R).difference(oct_(R - 0.2))
    m = trimesh.creation.extrude_polygon(ring, 0.5); m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); p.add('render', D._fix(m))
    m = trimesh.creation.extrude_polygon(oct_(R + 0.06).difference(oct_(R - 0.24)), 0.06); m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); m.apply_translation([0, 0.5, 0]); p.add('saltillo', D._fix(m))
    m = trimesh.creation.extrude_polygon(oct_(R - 0.199), 0.04); m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); m.apply_translation([0, 0.06, 0]); p.add('render', D._fix(m))
    m = trimesh.creation.extrude_polygon(oct_(R - 0.199), 0.01); m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); m.apply_translation([0, 0.38, 0]); p.add('water', D._fix(m))
    p.cyl('render', 0.12, 0.1, 1.05, sec=16); p.cyl('render', 0.18, 0.1, 0.3, sec=16)
    bowl = trimesh.creation.revolve(np.array([[0.0, 0.0], [0.1, 0.0], [0.45, 0.15], [0.5, 0.2], [0.44, 0.2], [0.0, 0.08]]), sections=24)
    bowl.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); bowl.apply_translation([0, 1.0, 0]); p.add('render', bowl)
    p.cyl('water', 0.43, 1.13, 1.16, sec=24); p.cyl('render', 0.05, 1.08, 1.4, sec=12); p.sphere('render', 0.08, 0, 1.44, 0, 1)
    return p
def floor_tile(wx=W, wz=W):
    p = Piece(); p.box('saltillo', -wx / 2, wx / 2, -0.03, 0, -wz / 2, wz / 2); p.box('render', -wx / 2 + 0.02, wx / 2 - 0.02, -RAISE, -0.03, -wz / 2 + 0.02, wz / 2 - 0.02); return p
def floor_tile_bath():
    p = Piece(); p.box('dark', -W / 2, W / 2, -0.027, -0.004, -W / 2, W / 2); n = 10; s = W / n
    for i in range(n):
        for j in range(n):
            x0 = -W / 2 + i * s + 0.004; z0 = -W / 2 + j * s + 0.004; p.box('tile', x0, x0 + s - 0.008, -0.03, 0.0, z0, z0 + s - 0.008)
    p.box('render', -W / 2 + 0.02, W / 2 - 0.02, -RAISE, -0.03, -W / 2 + 0.02, W / 2 - 0.02); return p
def m_ceiling(trim=(0, 0, 0, 0)):
    """Forro da casa principal (2 x 2 m): gesso, 2 vigas redondas ao longo de Z e latilhas (varas) entre elas.
    trim = (x-, x+, z-, z+): lados encostados numa parede externa terminam 0,3 m antes (na face interna)."""
    p = Piece(); y = HCM
    x0, x1, z0, z1 = -W / 2 + T * trim[0], W / 2 - T * trim[1], -W / 2 + T * trim[2], W / 2 - T * trim[3]
    p.box('plaster', x0, x1, y, y + 0.15, z0, z1)
    n = int(round((x1 - x0) / 0.1))
    for i in range(n):
        xx = x0 + (i + 0.5) * (x1 - x0) / n; seg_cyl(p, 'planks', (xx, y - 0.02, z0 + 0.003), (xx, y - 0.02, z1 - 0.003), 0.035, 6)
    for xx in (-0.5, 0.5):
        if x0 < xx < x1: seg_cyl(p, 'wood', (xx, y - 0.16, z0), (xx, y - 0.16, z1), 0.12, 12)
    return p
def interior_wall(doorway, h=HCM, ow=0.9, end=False):
    """Parede interna de 0,14 m (gesso), vao de porta com verga de madeira. end: termina 0,3 m antes (encontra parede externa)."""
    p = Piece(); t = 0.14; x1 = W / 2 - (T if end else 0.0)
    xs = [-W / 2] + ([-ow / 2, ow / 2] if doorway else []) + [x1]; ys = [0.0, 2.1, h] if doorway else [0.0, h]; zs = [-t / 2, t / 2]
    for m, mesh in grid_solid(xs, ys, zs, lambda i, j, k: None if (doorway and i == 1 and j == 0) else 'plaster').items(): p.add(m, mesh)
    if doorway:
        p.cham('wood', -ow / 2 - 0.15, ow / 2 + 0.15, 2.096, 2.3, -t / 2 - 0.02, t / 2 + 0.02, 0.012)
        p.box('wood', -ow / 2, -ow / 2 + 0.04, 0.0, 2.1, -t / 2 - 0.004, t / 2 + 0.004); p.box('wood', ow / 2 - 0.04, ow / 2, 0.0, 2.1, -t / 2 - 0.004, t / 2 + 0.004)
    return p
def player_ref():
    p = Piece(); c = trimesh.creation.capsule(height=1.8 - 0.6, radius=0.3, count=[8, 8]); c.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); c.apply_translation([0, 0.9, 0]); p.add('player', c)
    p.box('dark', -0.15, 0.15, 1.5, 1.6, 0.22, 0.32); return p
def step_block(w=1.4, d=0.45):
    """Degrau de lajota na porta (do patio ao piso a 0,15 m). Pivo: face da parede, cota do piso; avanca para +Z."""
    p = Piece(); p.box('render', -w / 2, w / 2, -RAISE, -0.075 - 0.025, 0.0, d - 0.02)
    prof_x(p, 'saltillo', -w / 2, w / 2, [(0.0, -0.1), (d, -0.1), (d + 0.02, -0.09), (d + 0.02, -0.078), (d, -0.075), (0.0, -0.075)]); return p

# ============================================================================ pecas
VZ = (-0.5, 0.5)
CEIL_E = sorted({(xx == -3, xx == 7, zz == -8, zz == -2) for xx in (-3, -1, 1, 3, 5, 7) for zz in (-8, -6, -4, -2)})
def ceil_name(f): return 'm_ceiling' + ('' if not any(f) else '_e' + ''.join('1' if b else '0' for b in f))
pieces = {'c_wall_plain': c_wall('plain'), 'c_wall_window': c_wall('window'), 'c_wall_small': c_wall('small'), 'c_wall_door': c_wall('door'),
          'c_wall_canale': c_wall('canale'), 'c_wall_side': c_wall('plain', vig=False), 'c_wall_side_small': c_wall('small', vig=False),
          'c_corner': c_corner(), 'party_wall': party_wall(), 'party_wall_end': party_wall(True),
          'c_roof_end': c_roof(5.4, 5.6), 'c_roof_mid': c_roof(5.4, 5.75), 'c_roof_studio': c_roof(5.4, 5.4),
          'c_vigas': c_vigas(5.4, (-2.5, -1.5, -0.5, 0.5, 1.5, 2.5)), 'kiva': kiva(), 'chimney_roof': chimney_roof(), 'door_hood': door_hood(),
          'm_wall_plain': m_wall('plain'), 'm_wall_window': m_wall('window', front=True), 'm_wall_window_reja': m_wall('window'), 'm_wall_small': m_wall('small'),
          'm_wall_door': m_wall('door'), 'm_wall_side_door': m_wall('side_door'), 'm_corner': m_corner(), 'm_gable': m_gable(),
          'm_roof': m_roof(), 'm_roof_end_l': m_roof(rake=-1), 'm_roof_end_r': m_roof(rake=1), 'm_ridge': m_ridge(-6 - RKM - 0.065, 6 + RKM + 0.065), 
          'arcade_arch': arcade_arch(), 'arcade_end_l': arcade_end(-1), 'arcade_end_r': arcade_end(1),
          'arcade_floor': arcade_floor(), 'arcade_floor_end_l': arcade_floor(-1), 'arcade_floor_end_r': arcade_floor(1),
          'arcade_roof': arcade_roof(), 'arcade_roof_end_l': arcade_roof(-1), 'arcade_roof_end_r': arcade_roof(1), 'porch_lantern': porch_lantern(),
          'gate_arch': gate_arch(), 'g_wall': g_wall(), 'g_pier': g_pier(), 'paver_tile': paver_tile(), 'fountain': fountain(),
          'floor_tile': floor_tile(), 'floor_tile_bath': floor_tile_bath(), 'interior_wall_plain': interior_wall(False), 'interior_wall_doorway': interior_wall(True),
          'interior_wall_end': interior_wall(False, end=True), 'interior_wall_end_doorway': interior_wall(True, end=True), 'step_block': step_block(),
          'door_leaf_main': plank_leaf(1.08, 2.37), 'door_leaf_casita': plank_leaf(0.88, 2.18), 'door_leaf_interior': plank_leaf(0.82, 2.08, 0.045, studs=False),
          'gate_leaf': plank_leaf(1.17, 2.45, 0.07), 'player_scale_ref': player_ref()}
for f in CEIL_E: pieces[ceil_name(f)] = m_ceiling(tuple(int(b) for b in f))

if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)

# ============================================================================ montagem
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(x, 3), round(y, 3), round(z, 3)], 'rotY': ry, 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': ry, 'open': ry + door}; e['tags'].append('door')
    L.append(e)
def hinge(x, z, ry, lx, lz):
    r = math.radians(ry); return x + lx * math.cos(r) + lz * math.sin(r), z - lx * math.sin(r) + lz * math.cos(r)
FACE = {0: (0, 1), 180: (0, -1), 90: (1, 0), -90: (-1, 0)}
def box_building(x0, x1, z0, z1, walls, corner, tag):
    """Coloca os modulos das 4 faces de um predio retangular. walls[face] = {centro: peca}; face em front/back/left/right."""
    for face, ry in (('front', 0), ('back', 180), ('right', 90), ('left', -90)):
        for c, n in walls.get(face, {}).items():
            if face == 'front': put(n, c, RAISE, z1, ry, [tag, face, 'ext'])
            if face == 'back': put(n, c, RAISE, z0, ry, [tag, face, 'ext'])
            if face == 'right': put(n, x1, RAISE, c, ry, [tag, face, 'ext'])
            if face == 'left': put(n, x0, RAISE, c, ry, [tag, face, 'ext'])
    for (x, z, ry) in ((x1, z1, 0), (x1, z0, 90), (x0, z0, 180), (x0, z1, -90)): put(corner, x, RAISE, z, ry, [tag, 'ext'])
def door_at(n, x, z, ry, tag, w, door=85, lz=-0.12):
    hx, hz = hinge(x, z, ry, -w / 2, lz); put(n, hx, RAISE + 0.012, hz, ry, [tag, 'ext'], door=door)
# ---------- casitas (x -12 a -6, 3 unidades ao longo de Z) e atelie ----------
for k, zc in enumerate((-6, 0, 6)):
    tag = f'casita{k + 1}'
    fw = {zc - 2: 'c_wall_window', zc: 'c_wall_door', zc + 2: 'c_wall_window'}
    bw = {zc - 2: 'c_wall_canale', zc: 'c_wall_small', zc + 2: 'c_wall_plain'}
    put_f = [(n, -6.0, zc_, 90) for zc_, n in fw.items()] + [(n, -12.0, zc_, -90) for zc_, n in bw.items()]
    for n, x, z, ry in put_f: put(n, x, RAISE, z, ry, [tag, 'front' if x == -6 else 'back', 'ext'])
    put('door_hood', -6.0, RAISE, zc, 90, [tag, 'front'])
    door_at('door_leaf_casita', -6.0, zc, 90, tag, 0.88, 85)
    put('step_block', -6.0, RAISE, zc, 90, [tag, 'front'])
    wz = 5.75 if k == 1 else 5.6; cz = zc + (0.0 if k == 1 else (0.05 if k == 0 else -0.05))
    put('c_roof_mid' if k == 1 else 'c_roof_end', -9.0, RAISE, cz, 0, [tag, 'roof'])
    put('c_vigas', -9.0, RAISE, zc, 0, [tag, 'ceiling', 'roof'])
    put('kiva', -11.7, RAISE, zc - (2.7 if k == 0 else 2.85), 0, [tag])
    put('chimney_roof', -11.25, RAISE + HC + RS, (zc - (2.7 if k == 0 else 2.85)) + 0.45, 0, [tag, 'roof'])
    for xx in (-11, -9, -7):
        for dz in (-2, 0, 2): put('floor_tile', xx, RAISE, zc + dz, 0, [tag, 'floor0'])
for xx in (-11, -9, -7):    # oitoes laterais: z=-9 (casita 1) e z=+9 (casita 3); paredes-meias em z=-3 e z=3
    put('c_wall_side_small' if xx == -9 else 'c_wall_side', xx, RAISE, -9.0, 180, ['casita1', 'side', 'ext'])
    put('c_wall_side_small' if xx == -9 else 'c_wall_side', xx, RAISE, 9.0, 0, ['casita3', 'side', 'ext', 'front'])
for zz in (-3.0, 3.0):
    put('party_wall_end', -7.0, RAISE, zz, 0, ['casitas']); put('party_wall', -9.0, RAISE, zz, 0, ['casitas']); put('party_wall_end', -11.0, RAISE, zz, 180, ['casitas'])
for (x, z, ry) in ((-6.0, 9.0, 0), (-6.0, -9.0, 90), (-12.0, -9.0, 180), (-12.0, 9.0, -90)): put('c_corner', x, RAISE, z, ry, ['casitas', 'ext'])
# atelie x 6..12, z 3..9 (porta para o patio em x=6)
box_building(6.0, 12.0, 3.0, 9.0, {'left': {4: 'c_wall_window', 6: 'c_wall_door', 8: 'c_wall_window'}, 'right': {4: 'c_wall_canale', 6: 'c_wall_small', 8: 'c_wall_plain'},
                                     'front': {7: 'c_wall_side', 9: 'c_wall_side_small', 11: 'c_wall_side'}, 'back': {7: 'c_wall_side', 9: 'c_wall_side_small', 11: 'c_wall_side'}}, 'c_corner', 'studio')
put('door_hood', 6.0, RAISE, 6.0, -90, ['studio', 'left']); door_at('door_leaf_casita', 6.0, 6.0, -90, 'studio', 0.88, 85); put('step_block', 6.0, RAISE, 6.0, -90, ['studio'])
put('c_roof_studio', 9.0, RAISE, 6.0, 0, ['studio', 'roof']); put('c_vigas', 9.0, RAISE, 6.0, 0, ['studio', 'ceiling', 'roof'])
put('kiva', 11.7, RAISE, 8.7, 180, ['studio']); put('chimney_roof', 11.25, RAISE + HC + RS, 8.25, 0, ['studio', 'roof'])
for xx in (7, 9, 11):
    for zz in (4, 6, 8): put('floor_tile', xx, RAISE, zz, 0, ['studio', 'floor0'])
# ---------- casa principal x -4..8, z -9..-1 ----------
MX0, MX1, MZ0, MZ1 = -4.0, 8.0, -9.0, -1.0
box_building(MX0, MX1, MZ0, MZ1, {'front': {-3: 'm_wall_window', -1: 'm_wall_window', 1: 'm_wall_door', 3: 'm_wall_window', 5: 'm_wall_plain', 7: 'm_wall_window'},
                                    'back': {-3: 'm_wall_window_reja', -1: 'm_wall_small', 1: 'm_wall_small', 3: 'm_wall_plain', 5: 'm_wall_window_reja', 7: 'm_wall_plain'},
                                    'left': {-8: 'm_wall_window_reja', -6: 'm_wall_plain', -4: 'm_wall_plain', -2: 'm_wall_window_reja'},
                                    'right': {-8: 'm_wall_window_reja', -6: 'm_wall_plain', -4: 'm_wall_window_reja', -2: 'm_wall_side_door'}}, 'm_corner', 'house')
put('m_gable', MX0, RAISE, -5.0, -90, ['house', 'left']); put('m_gable', MX1, RAISE, -5.0, 90, ['house', 'right'])
for xx in (-3, -1, 1, 3, 5, 7):
    put('m_roof_end_l' if xx == -3 else 'm_roof_end_r' if xx == 7 else 'm_roof', xx, RAISE, MZ1, 0, ['house', 'roof'])
    put('m_roof_end_r' if xx == -3 else 'm_roof_end_l' if xx == 7 else 'm_roof', xx, RAISE, MZ0, 180, ['house', 'roof'])
    for zz in (-8, -6, -4, -2):
        put('floor_tile_bath' if (xx, zz) in ((1, -8), (1, -6)) else 'floor_tile', xx, RAISE, zz, 0, ['house', 'floor0'])
        put(ceil_name((xx == -3, xx == 7, zz == -8, zz == -2)), xx, RAISE, zz, 0, ['house', 'roof', 'ceiling'])
put('m_ridge', 2.0, RAISE, -5.0, 0, ['house', 'roof'])
door_at('door_leaf_main', 1.0, MZ1, 0, 'house', 1.08, 85); put('step_block', 8.0, RAISE, -2.0, 90, ['house']); door_at('door_leaf_casita', MX1, -2.0, 90, 'house', 0.88, 85)
def wl(x0, z0, x1, z1, doors=()):
    """Paredes internas da casa principal: modulos de 2 m na linha; as pontas encostam nas paredes externas."""
    if z0 == z1:
        cs = list(range(int(min(x0, x1)) + 1, int(max(x0, x1)), 2))
        for c in cs:
            end = c in (cs[0], cs[-1]) and (c - 1 == MX0 or c + 1 == MX1); d = c in doors
            ry = 0 if c + 1 == MX1 or not end else 180
            put('interior_wall_end' + ('_doorway' if d else '') if end else 'interior_wall_' + ('doorway' if d else 'plain'), c, RAISE, z0, ry, ['house', 'floor0'])
            if d: hx, hz = hinge(c, z0, 0, -0.41, 0); put('door_leaf_interior', hx, RAISE + 0.01, hz, 0, ['house', 'floor0'], door=75)
    else:
        cs = list(range(int(min(z0, z1)) + 1, int(max(z0, z1)), 2))
        for c in cs:
            end = (c - 1 == MZ0) or (c + 1 == MZ1); d = c in doors
            ry = (90 if c - 1 == MZ0 else -90) if end else 90
            put('interior_wall_end' + ('_doorway' if d else '') if end else 'interior_wall_' + ('doorway' if d else 'plain'), x0, RAISE, c, ry, ['house', 'floor0'])
            if d: hx, hz = hinge(x0, c, 90, -0.41, 0); put('door_leaf_interior', hx, RAISE + 0.01, hz, 90, ['house', 'floor0'], door=75)
wl(MX0, -5.0, MX1, -5.0, doors=(-1, 1, 5)); wl(0.0, MZ0, 0.0, -5.0); wl(2.0, MZ0, 2.0, -5.0); wl(4.0, -5.0, 4.0, MZ1, doors=(-2,))
# arcada na frente da casa (z -1 a 1,6)
for xx in (-3, -1, 1, 3, 5, 7):
    e = -1 if xx == -3 else 1 if xx == 7 else 0
    put('arcade_floor_end_l' if e < 0 else 'arcade_floor_end_r' if e > 0 else 'arcade_floor', xx, RAISE, MZ1, 0, ['house', 'arcade'])
    put('arcade_arch', xx, RAISE, MZ1 + AD, 0, ['house', 'arcade', 'front'])
    put('arcade_roof_end_l' if e < 0 else 'arcade_roof_end_r' if e > 0 else 'arcade_roof', xx, RAISE, MZ1, 0, ['house', 'arcade', 'roof'])
put('arcade_end_l', -3.0, RAISE, MZ1 + AD, 0, ['house', 'arcade', 'front']); put('arcade_end_r', 7.0, RAISE, MZ1 + AD, 0, ['house', 'arcade', 'front'])
for xx in (1.0,): put('porch_lantern', xx, RAISE + a_under(1.3) - 0.01, MZ1 + 1.3, 0, ['house', 'arcade'])
# ---------- portao, muros, patio, chafariz ----------
put('gate_arch', 0.0, 0.0, 9.0 + GTH / 2, 0, ['court', 'front'])
for s, ry, op in ((-1, 0, 80), (1, 180, -80)):
    put('gate_leaf', s * (GW / 2 - 0.02), 0.045, 9.0 + GTH / 2 - GTH + 0.08, ry, ['court', 'front'], door=op)
for x in (-5, -3, 3, 5): put('g_wall', x, 0.0, 9.0, 0, ['court', 'front'])
for z in (-8, -6, -4, -2, 0, 2): put('g_wall', 12.0, 0.0, z, 90, ['court', 'right'])
for x in (-5, 9, 11): put('g_wall', x, 0.0, -9.0, 0, ['court', 'back'])
put('g_pier', 12.0, 0.0, -9.0, 0, ['court', 'back']); put('g_pier', 12.0, 0.0, 3.0 - 0.24, 0, ['court', 'right'])
for x in range(-5, 12, 2):
    for z in range(-8, 9, 2):
        inside_house = MX0 < x < MX1 and MZ0 < z < MZ1
        inside_studio = 6 < x < 12 and 3 < z < 9
        if inside_house or inside_studio: continue
        put('paver_tile', x, 0.0, z, 0, ['court'])
put('fountain', 1.0, 0.04, 5.0, 0, ['court'])
put('player_scale_ref', 0.0, 0.0, 11.5); put('player_scale_ref', 1.0, 0.04, 2.6, 0, ['court']); put('player_scale_ref', 2.0, RAISE, -3.0, 0, ['house'])

if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    json.dump({'grid': {'module_width': W, 'wall_thickness': T, 'floor_raise': RAISE,
                        'court': {'x': [-12, 12], 'z': [-9, 9]}, 'house': {'x': [MX0, MX1], 'z': [MZ0, MZ1], 'ceiling': HCM, 'eave': HM},
                        'arcade': {'z': [MZ1, MZ1 + AD]}, 'casitas': {'x': [-12, -6], 'z': [-9, 9], 'ceiling': HC, 'parapet': HP}, 'studio': {'x': [6, 12], 'z': [3, 9]},
                        'roof': 'house: gable 25 deg, ridge along X at z=-5, barrel clay tiles in geometry; arcade: shed 15 deg; casitas/studio: flat roof with parapet',
                        'textures': 'PBR (albedo + normal + ORM), 2 m tiles, UV in metres / 2'},
               'placements': L}, open(f'{OUT}/building_layout.json', 'w'), indent=1)
    sc = trimesh.Scene()
    for i, e in enumerate(L):
        if e['piece'] == 'player_scale_ref': continue
        Tm = trimesh.transformations.rotation_matrix(math.radians(e['rotY']), [0, 1, 0]); Tm[:3, 3] = e['pos']
        s = pieces[e['piece']].scene(e['piece'])
        for nm, g in s.geometry.items():
            g = g.copy(); g.apply_transform(Tm); sc.add_geometry(g, node_name=f'{i}_{nm}', geom_name=f'{i}_{nm}')
    bym = {}
    for g in sc.geometry.values(): bym.setdefault(g.visual.material.name, []).append(g)
    sc2 = trimesh.Scene()
    for k, gs in bym.items():
        m = trimesh.util.concatenate(gs); m.visual.material = MATS[k]; sc2.add_geometry(m, node_name=f'building_{k}', geom_name=f'building_{k}')
    sc2.export(f'{OUT}/building_assembled.glb', include_normals=True); glb_jpeg(f'{OUT}/building_assembled.glb')
    tot = sum(len(g.faces) for g in sc2.geometry.values())
    print(len(pieces), 'pecas', len(L), 'posicoes', sum(1 for e in L if 'door' in e), 'portas', tot, 'triangulos no montado')
    for n, p in sorted(pieces.items(), key=lambda kv: -kv[1].tris())[:12]: print(f'  {n:28s} {p.tris():6d} tri')
