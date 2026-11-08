"""Kit 50: minigolfe, em ALTO DETALHE (scripts/detalhe/detalhe.py).
Clube de 8 x 6 m de reboco creme sobre embasamento de tijolo, telhado de 4 aguas de telhas verdes com topo plano e uma bola de golfe
gigante sobre o tee, janela de atendimento com toldo listrado, porta da frente com arandela e porta dos fundos; dentro, balcao com caixa,
estante de tacos, caixotes de bolinhas, geladeira de bebidas, estante e banco. Campo de 5 buracos de grama sintetica com bordas de
tijolo, tees, copos e bandeirinhas: buraco 2 passa por dentro do tunel do moinho holandes de 4 pas, buraco 4 contorna o farol listrado
de vermelho e branco sobre as pedras. Lago com ponte de madeira em arco, passeios de concreto, palmeiras, mesas com guarda-sol no patio,
postes de lanterna, bancos, lixeiras, arbustos, mastro com bandeirola e gradil de ferro com entrada. Arte original e sem texto.
Y para cima, 1 unidade = 1 m. Padrao de medidas: PADRAO_METRICAS.md.
Dependencias: trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'scripts', 'detalhe'))
from detalhe import *
import detalhe as D
from shapely.geometry import Point, LineString, Polygon, box as sbox
from shapely.ops import unary_union
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT + '/pieces', exist_ok=True)
configurar(cores={'render': (236, 222, 190), 'plaster': (240, 236, 226), 'ceil': (244, 242, 236), 'concrete': (192, 188, 180), 'stone': (180, 172, 160),
                  'brick': (162, 74, 56), 'coping': (214, 208, 196), 'wood': (176, 128, 80), 'dkwood': (104, 72, 48), 'deck': (150, 108, 70),
                  'metal': (176, 180, 184), 'frame': (60, 62, 66), 'chrome': (216, 220, 224), 'steel': (110, 116, 122), 'steel_d': (52, 56, 60),
                  'iron': (30, 36, 34), 'bench_g': (40, 92, 62), 'trim': (250, 248, 240), 'door': (34, 96, 70), 'door_int': (204, 180, 140),
                  'lamp_glass': (255, 238, 196), 'dark': (34, 34, 36), 'roof_g': (44, 104, 76), 'gutter': (240, 240, 236), 'rubber': (28, 28, 30),
                  'paint_w': (246, 246, 242), 'sash': (250, 248, 240), 'flag_r': (210, 50, 44), 'flag_y': (244, 200, 52), 'flag_b': (52, 104, 180),
                  'flag_g': (60, 150, 84), 'fabric': (150, 60, 70), 'vinyl': (120, 40, 40), 'paper': (238, 234, 222), 'food_r': (200, 60, 50),
                  'food_y': (230, 190, 80), 'food_g': (110, 160, 70), 'basket': (176, 130, 76), 'cart_w': (240, 236, 226), 'ball': (246, 246, 244),
                  'ball_d': (234, 234, 232), 'turf': (64, 150, 70), 'turf2': (54, 128, 62), 'tee_m': (40, 92, 50), 'grass': (112, 160, 76),
                  'grass2': (98, 146, 68), 'sand': (226, 206, 160), 'rock': (132, 128, 120), 'rock2': (112, 108, 102), 'leaf': (70, 136, 64),
                  'leaf2': (92, 150, 70), 'palm': (60, 132, 66), 'palm2': (84, 150, 72), 'bark': (132, 104, 74), 'pond_b': (64, 84, 80),
                  'lh_r': (208, 52, 46), 'lh_w': (246, 244, 238), 'mill_w': (236, 228, 214), 'mill_r': (176, 58, 46), 'sail': (234, 226, 206),
                  'umb_r': (226, 70, 50), 'umb_y': (244, 190, 54), 'umb_o': (236, 128, 44), 'putter': (60, 64, 70), 'grip': (30, 30, 32),
                  'pot': (176, 110, 80), 'plant': (70, 120, 60), 'tile': (226, 230, 230), 'tile_b': (54, 110, 80)},
           texturas={'render': 'render', 'plaster': 'plaster', 'concrete': 'render', 'stone': 'stone', 'brick': 'brick', 'wood': 'planks',
                     'dkwood': 'planks', 'deck': 'deck', 'roof_g': 'shingles', 'turf': 'plaster', 'turf2': 'plaster', 'grass': 'render',
                     'grass2': 'render', 'sand': 'render', 'rock': 'stone2', 'mill_w': 'render', 'bark': 'render'},
           out=OUT)
D.METAL.update({'metal', 'chrome', 'steel', 'steel_d', 'iron', 'gutter', 'putter'}); MATS = D.MATS; TEX = D.TEX
MATS['water'] = PBRMaterial(name='water', baseColorFactor=[0.26, 0.52, 0.62, 0.62], alphaMode='BLEND', metallicFactor=0.1, roughnessFactor=0.05, doubleSided=True)

# ============================================================================ medidas
W = 2.0; T = 0.25; t_ = 0.12
Y0 = 0.15                                   # passeios, patio e piso do clube
YL = 0.05                                   # gramado
GY = -0.2
CX0, CX1, CZ0, CZ1 = 10.0, 18.0, 2.0, 8.0   # clube
CH = 3.2; CCEIL = 2.9                       # topo das paredes e forro (sobre o piso)
GT0, GT1 = 0.2, 0.23                        # laje e grama sintetica dos buracos
GW = 1.0; GB = 0.12; GBT = 0.34             # largura da grama, largura e topo da borda de tijolo
SX0, SX1, SZ0, SZ1 = -20.0, 20.0, -15.0, 15.0  # terreno
FX, FZ = 19.5, 14.5                         # gradil
GATE = (6.0, 8.5)                           # entrada no gradil da frente
HOLES = [[(-17.0, 10.5), (-9.0, 10.5), (-9.0, 7.0)],
         [(-17.0, 2.0), (-7.0, 2.0)],
         [(-17.0, -3.5), (-11.0, -3.5), (-11.0, -10.0), (-5.0, -10.0)],
         [(-2.0, -10.5), (-2.0, -3.5), (3.5, -3.5)],
         [(-3.5, 9.5), (3.5, 9.5), (3.5, 7.0)]]
MILL = (-12.0, 2.0)                         # moinho (o buraco 2 passa no tunel)
LH = (1.4, -7.4)                            # farol
POND = (-2.0, 5.25, 2.2, 1.6)               # lago (centro, raios)
BR0, BR1 = -4.8, 0.8                        # ponte (x)
def ext(p, mat, poly, z0, z1):
    for g in getattr(poly, 'geoms', [poly]):
        if g.geom_type == 'Polygon' and g.area > 1e-6:
            m = trimesh.creation.extrude_polygon(g, z1 - z0); m.apply_translation([0, 0, z0]); p.add(mat, D._fix(m))
def ext_y(p, mat, poly, y0, y1):
    for g in getattr(poly, 'geoms', [poly]):
        if g.geom_type == 'Polygon' and g.area > 1e-6:
            m = trimesh.creation.extrude_polygon(g, y1 - y0); v = m.vertices.copy()
            m.vertices = np.stack([v[:, 0], y0 + v[:, 2], v[:, 1]], 1); m.invert(); p.add(mat, D._fix(m))
def seg_cyl(p, mat, p0, p1, r, sec=8):
    p0, p1 = np.array(p0, float), np.array(p1, float); v = p1 - p0; Ln = np.linalg.norm(v)
    c = trimesh.creation.cylinder(radius=r, height=Ln, sections=sec); z = np.array([0, 0, 1.0]); v = v / Ln
    ax = np.cross(z, v); ang = math.acos(np.clip(np.dot(z, v), -1, 1))
    if np.linalg.norm(ax) > 1e-6: c.apply_transform(trimesh.transformations.rotation_matrix(ang, ax))
    elif v[2] < 0: c.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
    c.apply_translation((p0 + p1) / 2); return p.add(mat, c)
def lathe(p, mat, prof, x=0.0, z=0.0, y0=0.0, sec=14):
    for (r0, ya), (r1, yb) in zip(prof[:-1], prof[1:]):
        if abs(yb - ya) < 1e-6: continue
        pts = [(x + r * math.cos(a), y0 + y, z + r * math.sin(a)) for (r, y) in ((r0, ya), (r1, yb)) for a in np.linspace(0, 2 * math.pi, sec, endpoint=False)]
        p.hull(mat, pts)
def player_ref():
    p = Piece(); c = trimesh.creation.capsule(height=1.8 - 0.6, radius=0.3, count=[8, 8]); c.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); c.apply_translation([0, 0.9, 0]); p.add('player', c)
    p.box('dark', -0.15, 0.15, 1.5, 1.6, 0.22, 0.32); return p
def mitre_pair(p, mat, prof):
    """Canto externo de um perfil (z, y) que corre nas duas fachadas (pivo na quina, paredes em -X e -Z): 2 cunhas em meia-esquadria."""
    D_ = max(z for z, y in prof) + 0.001
    q = Piece(); prof_x(q, mat, 0.0, D_, prof); p.add(mat, slice_keep(q.parts[mat][0], [0, 0, 0], np.array([-1, 0, 1]) / math.sqrt(2)))
    q = Piece(); prof_z(q, mat, 0.0, D_, prof); p.add(mat, slice_keep(q.parts[mat][0], [0, 0, 0], np.array([1, 0, -1]) / math.sqrt(2)))
def rot_y(deg, t=(0, 0, 0)):
    M = trimesh.transformations.rotation_matrix(math.radians(deg), [0, 1, 0]); M[:3, 3] = t; return M
def mirror_x(x0=0.0):
    M = np.eye(4); M[0, 0] = -1; M[0, 3] = 2 * x0; return M
def tr(x=0.0, y=0.0, z=0.0): return trimesh.transformations.translation_matrix([x, y, z])
def along(p, q, x0, z0, x1, z1, y=0.0):
    ang = math.degrees(math.atan2(-(z1 - z0), x1 - x0)); p.merge(q, rot_y(ang, (x0, y, z0)))
def segs_excl(gaps, a0=-1.0, a1=1.0, pad=0.0):
    segs = [(a0, a1)]
    for (a, b) in gaps: segs = [s for (c, d) in segs for s in ((c, min(d, a - pad)), (max(c, b + pad), d)) if s[1] - s[0] > 1e-3]
    return segs
def mirrored(p, M):
    q = Piece(); q.merge(p, M); return q
def clipped(p, planes):
    """Corta todas as malhas pelos planos (origem, normal), mantendo o lado da normal (com tampa)."""
    q = Piece(); q.uv = dict(p.uv)
    for mat, ms in p.parts.items():
        for m in ms:
            mm = m
            for (o, n) in planes:
                n = np.array(n, float); b = mm.bounds; d = np.dot(n, o)
                ds = [np.dot(n, [x, y, z]) for x in b[:, 0] for y in b[:, 1] for z in b[:, 2]]
                if min(ds) >= d - 1e-9: continue
                if max(ds) <= d + 1e-9: mm = None; break
                mm = slice_keep(mm, o, n / np.linalg.norm(n))
                if mm is None or len(mm.faces) == 0: mm = None; break
            if mm is not None: q.add(mat, mm)
    return q
def subtract_prism(p, poly, y0, y1):
    """Tira de cada malha o prisma vertical (poligono no plano x-z, de y0 a y1): usado para o telhado encostar no torreao."""
    cut = trimesh.creation.extrude_polygon(poly, y1 - y0); v = cut.vertices.copy(); cut.vertices = np.stack([v[:, 0], y0 + v[:, 2], v[:, 1]], 1); cut.invert(); cut = D._fix(cut)
    bx = poly.bounds; q = Piece(); q.uv = dict(p.uv)
    for mat, ms in p.parts.items():
        for m in ms:
            b = m.bounds
            if b[1, 0] < bx[0] or b[0, 0] > bx[2] or b[1, 2] < bx[1] or b[0, 2] > bx[3] or b[1, 1] < y0 or b[0, 1] > y1: q.add(mat, m); continue
            try:
                r = trimesh.boolean.difference([m, cut], engine='manifold')
                if r is not None and len(r.faces): q.add(mat, r)
            except Exception:
                c = m.centroid
                if not Point(c[0], c[2]).within(poly): q.add(mat, m)
    return q
def poly_ngon(cx, cz, r, n=12, a0=0.0):
    return Polygon([(cx + r * math.cos(a0 + 2 * math.pi * k / n), cz + r * math.sin(a0 + 2 * math.pi * k / n)) for k in range(n)])
def alu_frame(p, a, b, y0, y1, f=0.05, z0=-0.2, z1=-0.1, mulls=(), trans=()):
    p.box('frame', a, a + f, y0, y1, z0, z1); p.box('frame', b - f, b, y0, y1, z0, z1)
    p.box('frame', a + f, b - f, y1 - f, y1, z0, z1); p.box('frame', a + f, b - f, y0, y0 + f, z0, z1)
    for x in mulls: p.box('frame', x - f / 2, x + f / 2, y0 + f, y1 - f, z0, z1)
    for y in trans: p.box('frame', a + f, b - f, y - f / 2, y + f / 2, z0, z1)
def wall_lamp():
    """Arandela redonda de chapa (pivo: face da parede, centro)."""
    p = Piece(); p.cyl('metal', 0.12, -0.12, 0.0, 0, 0, 16) if False else None
    m = trimesh.creation.cylinder(radius=0.13, height=0.05, sections=20); m.apply_translation([0, 0, 0.025]); p.add('metal', m)
    m = trimesh.creation.cylinder(radius=0.1, height=0.05, sections=20); m.apply_translation([0, 0, 0.074]); p.add('lamp_glass', m)
    p.box('metal', -0.14, 0.14, 0.13, 0.15, 0.0, 0.12)
    return p
def tiles(p, poly, y0, y1, step, mat, gap=0.005, fill='brass', ox=0.0, oz=0.0):
    b = poly.bounds
    for i in range(int(math.floor((b[0] - ox) / step)), int(math.ceil((b[2] - ox) / step))):
        for j in range(int(math.floor((b[1] - oz) / step)), int(math.ceil((b[3] - oz) / step))):
            q = sbox(ox + i * step + gap, oz + j * step + gap, ox + (i + 1) * step - gap, oz + (j + 1) * step - gap).intersection(poly)
            if q.area > 1e-6: ext_y(p, mat, q, y0, y1)
    ext_y(p, fill, poly.buffer(-0.001, join_style=2), y0, y1 - 0.003)
def run_wall(Ln, h, cuts=(), t=t_):
    """Parede interna (pivo: inicio, eixo; vai para +X). cuts = (centro, largura, y0, y1, tipo): door (porta com guarnicao),
    pass (vao livre), counter (balcao com aba), grille (guiche com grade cromada e passa-volumes)."""
    p = Piece(); cs = [(c - w / 2, c + w / 2, y0, y1, k) for (c, w, y0, y1, k) in cuts]
    xs = sorted(set([0.0, Ln] + [v for c in cs for v in c[:2]])); ys = sorted(set([0.0, h] + [v for c in cs for v in c[2:4]]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        return None if any(a < cx < b and y0 < cy < y1 for (a, b, y0, y1, _) in cs) else 'plaster'
    for m, mesh in grid_solid(xs, ys, [-t / 2, t / 2], cell).items(): p.add(m, mesh)
    for (a, b, y0, y1, k) in cs:
        if k == 'door': q = Piece(); door_casing(q, b - a, t, y1); p.merge(q, tr((a + b) / 2, 0, 0))
        if k in ('counter', 'grille'):
            p.cham('wood', a - 0.06, b + 0.06, y0 - 0.04, y0 + 0.004, -t / 2 - 0.3, t / 2 + 0.3, 0.006)
            for s in (-1, 1):
                zz = sorted((s * t / 2, s * (t / 2 + 0.02)))
                p.box('metal', a - 0.06, a - 0.002, y0, y1 + 0.06, *zz); p.box('metal', b + 0.002, b + 0.06, y0, y1 + 0.06, *zz); p.box('metal', a - 0.002, b + 0.002, y1 + 0.002, y1 + 0.06, *zz)
        if k == 'glaze':
            for s_ in (-1, 1): p.box('gold', a + 0.001 if s_ < 0 else b - 0.04, a + 0.04 if s_ < 0 else b - 0.001, y0, y1, -t / 2 - 0.012, t / 2 + 0.012)
            p.box('gold', a + 0.04, b - 0.04, y1 - 0.04, y1 - 0.001, -t / 2 - 0.012, t / 2 + 0.012); p.box('gold', a + 0.04, b - 0.04, y0 + 0.001, y0 + 0.04, -t / 2 - 0.012, t / 2 + 0.012)
            for xm in np.linspace(a, b, max(2, int(round((b - a) / 1.0))) + 1)[1:-1]: p.box('gold', xm - 0.02, xm + 0.02, y0 + 0.04, y1 - 0.04, -0.03, 0.03)
            p.box('glass', a + 0.04, b - 0.04, y0 + 0.04, y1 - 0.04, -0.004, 0.004)
        if k == 'grille':
            for x in np.arange(a + 0.06, b - 0.04, 0.06): p.cyl('chrome', 0.006, y0 + 0.22, y1, x, 0.0, 6)
            p.box('chrome', a, b, y0 + 0.2, y0 + 0.23, -0.01, 0.01); p.box('chrome', a, b, y1 - 0.05, y1 - 0.02, -0.01, 0.01)
            p.box('glass', a + 0.002, b - 0.002, y0 + 0.23, y1 - 0.05, 0.03, 0.036)
    for side in (1, -1):
        gaps = [(a - (0.09 if k == 'door' else 0.0), b + (0.09 if k == 'door' else 0.0)) for (a, b, y0, y1, k) in cs if y0 < 0.01]
        for (a, b) in segs_excl(gaps, 0.0, Ln):
            if b - a > 0.02: prof_x(p, 'dkwood', a, b, D.BASE_PROF(t) if side > 0 else [(-z, y) for (z, y) in D.BASE_PROF(t)][::-1])
    return p
PART = [(-8.2, 0.9, 0.0, 2.1, 'door'), (-4.85, 0.9, 0.0, 2.1, 'door'), (-2.3, 1.6, 0.95, 2.2, 'counter'), (-0.9, 0.9, 0.0, 2.1, 'door'),
        (2.3, 1.0, 1.0, 2.1, 'grille'), (3.8, 1.0, 1.0, 2.1, 'grille'), (5.0, 0.9, 0.0, 2.1, 'door'), (7.6, 3.0, 0.0, 2.4, 'pass')]
ZST = -4.25                                                # frente das cabines dos banheiros
def lockers(L1=1.8, rows=3):
    """Guarda-volumes de aco (pivo: centro de tras, piso): base, portas com veneziana, puxador e fechadura, sem numeros."""
    p = Piece(); x = L1 / 2; h = 1.95; n = int(round(L1 / 0.45))
    p.box('steel', -x, x, 0.1, h, 0.0, 0.48); p.box('dark', -x + 0.02, x - 0.02, 0.0, 0.1, 0.0, 0.44); p.cham('steel', -x - 0.01, x + 0.01, h, h + 0.04, 0.0, 0.5, 0.005)
    for i in range(n):
        for j in range(rows):
            a = -x + i * L1 / n + 0.012; b = -x + (i + 1) * L1 / n - 0.012; y0 = 0.12 + j * (h - 0.14) / rows + 0.01; y1 = 0.12 + (j + 1) * (h - 0.14) / rows - 0.01
            p.box('vinyl_g', a, b, y0, y1, 0.48, 0.49)
            for k in range(4): yy = y1 - 0.08 - k * 0.035; p.box('dark', a + 0.08, b - 0.08, yy, yy + 0.012, 0.49, 0.494)
            p.box('chrome', b - 0.07, b - 0.04, (y0 + y1) / 2 - 0.05, (y0 + y1) / 2 + 0.05, 0.49, 0.51); p.cyl('brass', 0.012, (y0 + y1) / 2 + 0.08, (y0 + y1) / 2 + 0.1, b - 0.055, 0.5, 8) if False else p.box('brass', b - 0.065, b - 0.045, (y0 + y1) / 2 + 0.08, (y0 + y1) / 2 + 0.1, 0.49, 0.5)
    return p
def wall_clock(r=0.4):
    """Relogio de parede sem numeros (pivo: face da parede, centro): aro cromado, mostrador, marcas das horas e ponteiros."""
    p = Piece(); R = trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])
    for (rr, z0, z1, m) in ((r, 0.0, 0.06, 'chrome'), (r - 0.04, 0.06, 0.065, 'cream')):
        c = trimesh.creation.cylinder(radius=rr, height=z1 - z0, sections=40); c.apply_translation([0, 0, (z0 + z1) / 2]); p.add(m, c)
    for k in range(12):
        a = k * math.pi / 6; l = 0.07 if k % 3 == 0 else 0.04
        seg_cyl(p, 'dark', ((r - 0.06) * math.sin(a), (r - 0.06) * math.cos(a), 0.067), ((r - 0.06 - l) * math.sin(a), (r - 0.06 - l) * math.cos(a), 0.067), 0.008, 4)
    for (a, l, w_) in ((math.radians(300), r * 0.55, 0.012), (math.radians(60), r * 0.78, 0.008)): seg_cyl(p, 'dark', (0, 0, 0.072), (l * math.sin(a), l * math.cos(a), 0.072), w_, 4)
    p.sphere('dark', 0.02, 0, 0, 0.075, 0)
    return p
def stool():
    p = Piece(); p.cyl('chrome', 0.2, 0.0, 0.02, 0, 0, 16); seg_cyl(p, 'chrome', (0, 0.02, 0), (0, 0.66, 0), 0.03, 8)
    m = trimesh.creation.annulus(r_min=0.15, r_max=0.17, height=0.015, sections=20); m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])); m.apply_translation([0, 0.3, 0]); p.add('chrome', m) if False else p.cyl('chrome', 0.17, 0.3, 0.315, 0, 0, 20)
    lathe(p, 'vinyl_r', [(0.18, 0.66), (0.19, 0.7), (0.18, 0.76), (0.0, 0.77)], sec=20); return p
def safe_box():
    p = Piece(); p.cham('dark', -0.35, 0.35, 0.0, 0.9, 0.0, 0.6, 0.02); p.box('steel', -0.3, 0.3, 0.1, 0.8, 0.6, 0.61)
    c = trimesh.creation.cylinder(radius=0.08, height=0.03, sections=16); c.apply_translation([0, 0.5, 0.625]); p.add('chrome', c)
    p.box('chrome', 0.15, 0.2, 0.3, 0.55, 0.61, 0.64); return p
def file_cab():
    p = Piece(); p.box('steel', -0.25, 0.25, 0.0, 1.35, 0.0, 0.62)
    for k in range(4): y = 0.05 + k * 0.33; p.box('steel', -0.23, 0.23, y, y + 0.3, 0.62, 0.635); p.box('chrome', -0.06, 0.06, y + 0.2, y + 0.23, 0.635, 0.66)
    return p

# ============================================================================ plataforma coberta (pivo: face da parede oeste, chao; local +Z para fora)
CAN_Y0, CAN_Y1 = 3.75, 4.05
CAN_COLS = [-5.0, -1.7, 1.7, 5.0]; CAN_ZC = 5.6
def paving(poly, y1, joints=1.5, mat='concrete', gap=0.006):
    p = Piece(); b = poly.bounds
    for x in np.arange(b[0], b[2], joints):
        for z in np.arange(b[1], b[3], joints):
            q = sbox(x + gap, z + gap, x + joints - gap, z + joints - gap).intersection(poly); ext_y(p, mat, q, GY, y1)
    ext_y(p, 'dark', poly.buffer(-0.002, join_style=2), GY, y1 - 0.008)
    return p
def wheel_stop():
    p = Piece(); p.cham('concrete', -0.9, 0.9, 0.0, 0.12, -0.1, 0.1, 0.02)
    for x in (-0.6, 0.6): p.box('paint_y', x - 0.15, x + 0.15, 0.12, 0.123, -0.08, 0.08)
    return p
def door_glass(w=0.87, h=2.36, t=0.05):
    """Porta de vidro de quadro de aluminio com barra de empurrar e chute de chapa (pivo: dobradica, embaixo)."""
    p = Piece(); s = 0.06
    p.cham('frame', 0, s, 0, h, -t / 2, t / 2, 0.004); p.cham('frame', w - s, w, 0, h, -t / 2, t / 2, 0.004)
    p.cham('frame', s - 0.002, w - s + 0.002, 0, 0.25, -t / 2, t / 2, 0.004); p.cham('frame', s - 0.002, w - s + 0.002, h - s, h, -t / 2, t / 2, 0.004)
    p.box('glass', s - 0.004, w - s + 0.004, 0.246, h - s + 0.004, -0.004, 0.004)
    for z in (1, -1):
        seg_cyl(p, 'chrome', (s, 1.05, z * (t / 2 + 0.05)), (w - s, 1.05, z * (t / 2 + 0.05)), 0.018, 8)
        for x in (s + 0.04, w - s - 0.04): seg_cyl(p, 'chrome', (x, 1.05, z * t / 2), (x, 1.05, z * (t / 2 + 0.05)), 0.01, 6)
    return p
def door_metal(w=0.88, h=2.13, t=0.045):
    """Porta de servico de chapa com visor redondo, barra antipanico e mola (pivo: dobradica, embaixo)."""
    p = Piece(); p.cham('metal', 0.0, w, 0.0, h, -t / 2, t / 2, 0.004)
    for z in (1, -1):
        c = trimesh.creation.annulus(r_min=0.12, r_max=0.15, height=0.012, sections=24); c.apply_translation([w / 2, 1.55, z * (t / 2 + 0.006)]); p.add('chrome', c)
    p.cyl('glass', 0.0, 0, 0, 0, 0) if False else None
    m = trimesh.creation.cylinder(radius=0.12, height=0.008, sections=24); m.apply_translation([w / 2, 1.55, 0]); p.add('dark', m)
    p.box('chrome', 0.1, w - 0.08, 1.0, 1.06, -t / 2 - 0.06, -t / 2 - 0.02); p.box('chrome', w - 0.12, w - 0.06, 1.0, 1.08, t / 2, t / 2 + 0.05)
    p.box('dark', 0.05, 0.4, h - 0.12, h - 0.06, -t / 2 - 0.06, -t / 2)
    return p

# ============================================================================ pecas
L = []
def wc():
    """Vaso de louca com caixa acoplada e assento (pivo: face da parede, piso)."""
    p = Piece()
    lathe(p, 'porcelain', [(0.13, 0.0), (0.15, 0.1), (0.14, 0.28), (0.2, 0.4), (0.2, 0.42), (0.0, 0.42)], 0.0, 0.42, 0.0, 16)
    p.hull('porcelain', [(x * 0.17, y, z) for x in (-1, 1) for z in (0.15, 0.4) for y in (0.0, 0.42)])
    p.cham('porcelain', -0.2, 0.2, 0.42, 0.8, 0.0, 0.18, 0.03); p.cham('porcelain', -0.21, 0.21, 0.8, 0.83, -0.0, 0.19, 0.01)
    p.cham('dark', -0.19, 0.19, 0.42, 0.45, 0.2, 0.62, 0.03); p.box('chrome', 0.1, 0.16, 0.74, 0.76, 0.18, 0.2)
    return p
def urinal():
    p = Piece(); p.hull('porcelain', [(x, y, z) for x in (-0.2, 0.2) for (y, z) in ((0.45, 0.0), (0.45, 0.3), (1.05, 0.0), (1.05, 0.2))])
    p.box('dark', -0.12, 0.12, 0.6, 0.98, 0.2, 0.25) if False else None
    seg_cyl(p, 'chrome', (0, 1.05, 0.06), (0, 1.4, 0.06), 0.015, 6); p.box('chrome', -0.04, 0.04, 1.3, 1.36, 0.06, 0.1)
    return p
def sink_bank(n=2, L1=1.6):
    """Bancada de pias de louca com torneiras cromadas e espelho com moldura de aco (pivo: face da parede, piso)."""
    p = Piece(); x = L1 / 2
    p.cham('porcelain', -x, x, 0.8, 0.88, 0.0, 0.5, 0.02)
    for s in (-1, 1): p.box('chrome', s * (x - 0.08) - 0.02, s * (x - 0.08) + 0.02, 0.0, 0.8, 0.4, 0.44)
    for i in range(n):
        xc = -x + (i + 0.5) * L1 / n; p.box('dark', xc - 0.2, xc + 0.2, 0.875, 0.882, 0.12, 0.42)
        seg_cyl(p, 'chrome', (xc, 0.88, 0.06), (xc, 1.08, 0.06), 0.014, 6); seg_cyl(p, 'chrome', (xc, 1.08, 0.06), (xc, 1.04, 0.2), 0.012, 6)
        p.cham('chrome', xc - 0.32, xc + 0.32, 1.2, 1.95, 0.0, 0.02, 0.006); p.box('mirror', xc - 0.29, xc + 0.29, 1.23, 1.92, 0.02, 0.026)
    return p

def unit(v): v = np.array(v, float); return v / np.linalg.norm(v)
def ring_y(p, mat, r0, r1, y0, y1, x=0.0, z=0.0, sec=96):
    m = trimesh.creation.annulus(r_min=r0, r_max=r1, height=y1 - y0, sections=sec)
    m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); m.apply_translation([x, (y0 + y1) / 2, z]); return p.add(mat, m)
def disc_z(p, mat, r, z0, z1, x, y, sec=20):
    m = trimesh.creation.cylinder(radius=r, height=z1 - z0, sections=sec); m.apply_translation([x, y, (z0 + z1) / 2]); return p.add(mat, m)
def disc_x(p, mat, r, x0, x1, y, z, sec=20):
    m = trimesh.creation.cylinder(radius=r, height=x1 - x0, sections=sec); m.apply_transform(rot_y(90)); m.apply_translation([(x0 + x1) / 2, y, z]); return p.add(mat, m)
def off(poly, d): return poly.buffer(d, join_style=2, mitre_limit=10)
def grid_map(us, vs, mp, fb, ft):
    """Solido entre y = fb(u, v) e y = ft(u, v) sobre a grade us x vs, com (x, z) = mp(u, v) (estanque)."""
    nu, nv = len(us), len(vs); V = []
    for f in (ft, fb):
        for u in us:
            for v in vs: x, z = mp(u, v); V.append((x, f(u, v), z))
    N = nu * nv; idx = lambda i, j, b=0: b * N + i * nv + j; F = []
    for i in range(nu - 1):
        for j in range(nv - 1):
            a, b_, c, d = idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1); F += [[a, c, b_], [a, d, c]]
            a, b_, c, d = idx(i, j, 1), idx(i + 1, j, 1), idx(i + 1, j + 1, 1), idx(i, j + 1, 1); F += [[a, b_, c], [a, c, d]]
    ring = [(i, 0) for i in range(nu)] + [(nu - 1, j) for j in range(1, nv)] + [(i, nv - 1) for i in range(nu - 2, -1, -1)] + [(0, j) for j in range(nv - 2, 0, -1)]
    for k in range(len(ring)):
        (i0, j0), (i1, j1) = ring[k], ring[(k + 1) % len(ring)]
        a, b_ = idx(i0, j0), idx(i1, j1); c, d = idx(i1, j1, 1), idx(i0, j0, 1); F += [[a, b_, c], [a, c, d]]
    m = trimesh.Trimesh(np.array(V, float), np.array(F), process=True); m.fix_normals(); return D._fix(m)

# ============================================================================ moveis reaproveitados
def office_chair(mat='vinyl'):
    """Cadeira giratoria (pivo: centro, chao; encosto em -Z): base de 5 patas com rodizios, coluna, assento e encosto estofados."""
    p = Piece()
    for k in range(5):
        a = k * 2 * math.pi / 5; ex, ez = 0.3 * math.cos(a), 0.3 * math.sin(a)
        seg_cyl(p, 'steel_d', (0, 0.08, 0), (ex, 0.05, ez), 0.02, 6); p.sphere('dark', 0.03, ex, 0.03, ez, 1)
    p.cyl('chrome', 0.025, 0.08, 0.42, 0, 0, 10)
    p.cham(mat, -0.25, 0.25, 0.42, 0.5, -0.24, 0.24, 0.04)
    p.cham(mat, -0.23, 0.23, 0.58, 1.0, -0.3, -0.24, 0.03); p.box('steel_d', -0.03, 0.03, 0.44, 0.62, -0.26, -0.22)
    for s in (-1, 1): p.box('steel_d', s * 0.25 - 0.015, s * 0.25 + 0.015, 0.5, 0.66, -0.12, 0.12); p.cham('dark', s * 0.25 - 0.03, s * 0.25 + 0.03, 0.66, 0.69, -0.16, 0.12, 0.01)
    return p
def guest_chair(mat='vinyl'):
    """Cadeira de visita de tubo de aco com assento e encosto estofados (pivo: centro, chao; encosto em -Z)."""
    p = Piece()
    for s in (-1, 1):
        seg_cyl(p, 'chrome', (s * 0.22, 0.0, 0.2), (s * 0.22, 0.44, 0.2), 0.012, 6); seg_cyl(p, 'chrome', (s * 0.22, 0.0, 0.2), (s * 0.22, 0.0, -0.2), 0.012, 6)
        seg_cyl(p, 'chrome', (s * 0.22, 0.0, -0.2), (s * 0.22, 0.88, -0.22), 0.012, 6)
    p.cham(mat, -0.23, 0.23, 0.44, 0.5, -0.2, 0.22, 0.02); p.cham(mat, -0.22, 0.22, 0.55, 0.85, -0.25, -0.21, 0.02)
    return p
def sofa(n=3, mat='fabric2'):
    """Sofa de courvin de linhas retas (pivo: centro de tras, chao; assento para +Z) com pes cromados."""
    p = Piece(); L1 = 0.62 * n + 0.3; x = L1 / 2
    p.cham(mat, -x, x, 0.12, 0.42, 0.0, 0.82, 0.03); p.cham(mat, -x, x, 0.42, 0.85, 0.0, 0.2, 0.03)
    for s in (-1, 1): p.cham(mat, *sorted((s * x, s * (x - 0.15))), 0.42, 0.62, 0.0, 0.82, 0.03)
    for i in range(n):
        a = -x + 0.15 + i * 0.62 + 0.01; b = a + 0.6; p.cham(mat, a, b, 0.42, 0.52, 0.2, 0.8, 0.04); p.cham(mat, a, b, 0.52, 0.82, 0.2, 0.32, 0.04)
    for (a, c) in ((-x + 0.08, 0.08), (x - 0.08, 0.08), (-x + 0.08, 0.74), (x - 0.08, 0.74)): p.cyl('chrome', 0.025, 0.0, 0.12, a, c, 8)
    return p
def plant(h=1.4):
    """Vaso de planta (pivo: centro, chao): vaso de ceramica e folhas em leque."""
    p = Piece(); lathe(p, 'pot', [(0.18, 0.0), (0.24, 0.45), (0.25, 0.47), (0.0, 0.47)], sec=16); p.cyl('dark', 0.22, 0.45, 0.46, 0, 0, 16)
    rng = np.random.default_rng(5)
    for k in range(9):
        a = k * 2 * math.pi / 9 + rng.uniform(-0.2, 0.2); r = rng.uniform(0.25, 0.5); yy = rng.uniform(h * 0.6, h)
        seg_cyl(p, 'plant', (0, 0.46, 0), (r * math.cos(a), yy, r * math.sin(a)), 0.012, 4)
        c = np.array([r * math.cos(a), yy, r * math.sin(a)]); u = np.array([math.cos(a), 0.2, math.sin(a)]); u /= np.linalg.norm(u); v = np.array([-math.sin(a), 0, math.cos(a)])
        p.hull('plant', [c - 0.35 * u, c + 0.05 * u + 0.09 * v, c + 0.05 * u - 0.09 * v, c + 0.25 * u, c - 0.1 * u + 0.01 * np.array([0, 1, 0])])
    return p
def trash_can():
    p = Piece(); lathe(p, 'steel_d', [(0.26, 0.0), (0.28, 0.9), (0.0, 0.9)], sec=20)
    for y in (0.15, 0.75): ring_y(p, 'steel', 0.28, 0.29, y, y + 0.04, 0, 0, 20)
    lathe(p, 'steel_d', [(0.3, 0.9), (0.3, 0.96), (0.2, 1.02), (0.0, 1.03)], sec=20); return p
def tree(h=6.0, r=1.9, mat='leaf', seed=1):
    p = Piece(); rng = np.random.default_rng(seed)
    lathe(p, 'bark', [(0.18, -0.2), (0.13, 0.5), (0.09, h * 0.6)], sec=10)
    for (dx, dz, yy) in ((0.6, 0.0, h * 0.62), (-0.5, 0.4, h * 0.66), (0.0, -0.5, h * 0.7)): seg_cyl(p, 'bark', (0.0, h * 0.45, 0.0), (dx * 0.8, yy, dz * 0.8), 0.05, 6)
    p.sphere(mat, r, 0.0, h * 0.78, 0.0, 2)
    for _ in range(8):
        a = rng.uniform(0, 2 * math.pi); rr = r * rng.uniform(0.45, 0.65); p.sphere(mat, rr, math.cos(a) * r * 0.7, h * 0.78 + rng.uniform(-0.4, 0.5) * r, math.sin(a) * r * 0.7, 1)
    return p
def bush(r=0.5, seed=3):
    p = Piece(); rng = np.random.default_rng(seed); p.sphere('leaf', r, 0.0, r * 0.85, 0.0, 2)
    for _ in range(6):
        a = rng.uniform(0, 2 * math.pi); p.sphere('leaf2', r * 0.55, math.cos(a) * r * 0.6, r * rng.uniform(0.7, 1.2), math.sin(a) * r * 0.6, 1)
    return p
# ============================================================================ moveis e postes (do kit 48)
def counter_k(L1=5.5):
    """Balcao de atendimento (pivo: face da parede, piso; balcao para +Z): corpo de madeira, tampo, prateleira e copos."""
    p = Piece(); x = L1 / 2
    p.cham('dkwood', -x, x, 0.0, 0.88, 0.0, 0.55, 0.01); p.cham('wood', -x - 0.02, x + 0.02, 0.88, 0.92, 0.0, 0.6, 0.006)
    p.box('dark', -x + 0.04, x - 0.04, 0.0, 0.1, 0.55, 0.56)
    for xx in np.arange(-x + 0.6, x - 0.3, 0.9): p.box('wood', xx - 0.01, xx + 0.01, 0.12, 0.84, 0.55, 0.565)
    return p
def register():
    p = Piece(); p.hull('dark', [(x, y, z) for x in (-0.2, 0.2) for (y, z) in ((0.0, -0.2), (0.0, 0.22), (0.08, 0.22), (0.16, -0.2))])
    p.cham('steel', -0.16, 0.16, 0.16, 0.2, -0.2, -0.04, 0.005)
    for i in range(4):
        for j in range(3): p.box('paper', -0.12 + i * 0.06, -0.08 + i * 0.06, 0.08 + j * 0.024 + 0.005, 0.088 + j * 0.024 + 0.008, 0.12 - j * 0.07, 0.16 - j * 0.07) if False else p.box('paper', -0.12 + i * 0.06, -0.08 + i * 0.06, 0.1 + (2 - j) * 0.02, 0.112 + (2 - j) * 0.02, 0.02 + j * 0.06, 0.06 + j * 0.06)
    p.hull('dark', [(x, y, z) for x in (-0.1, 0.1) for (y, z) in ((0.15, -0.12), (0.15, -0.18), (0.3, -0.16), (0.3, -0.2))])
    p.box('food_g', -0.08, 0.08, 0.22, 0.28, -0.162, -0.155)
    return p
def fridge():
    """Geladeira de bebidas com porta de vidro e prateleiras de garrafas (pivo: centro de tras, piso; porta +Z)."""
    p = Piece(); p.cham('cart_w', -0.4, 0.4, 0.0, 1.95, 0.0, 0.7, 0.012)
    p.box('frame', -0.38, 0.38, 0.1, 1.75, 0.7, 0.73); p.box('glass', -0.34, 0.34, 0.14, 1.71, 0.73, 0.736)
    p.box('dark', -0.34, 0.34, 0.14, 1.71, 0.69, 0.7)
    for k, y in enumerate((0.25, 0.65, 1.05, 1.45)):
        p.box('steel', -0.33, 0.33, y - 0.01, y, 0.1, 0.68)
        for i, x in enumerate(np.linspace(-0.28, 0.28, 7)): p.cyl(['flag_r', 'food_g', 'food_y', 'flag_b'][(i + k) % 4], 0.03, y, y + 0.24, x, 0.55, 10)
    p.box('flag_b', -0.4, 0.4, 1.78, 1.92, 0.7, 0.715); p.box('chrome', 0.33, 0.36, 0.7, 1.2, 0.736, 0.77)
    return p
def shelves(L1=1.6):
    """Estante de aco com caixas e embalagens sem texto (pivo: centro de tras, piso)."""
    p = Piece(); x = L1 / 2; rng = np.random.default_rng(11)
    for s in (-1, 1):
        for z in (0.02, 0.38): p.box('steel', s * x - 0.02 * (s > 0) * 2 + (0 if s > 0 else 0), s * x + (0.0 if s > 0 else 0.04), 0.0, 1.9, z, z + 0.03) if False else p.box('steel', *sorted((s * x, s * (x - 0.03))), 0.0, 1.9, z, z + 0.03)
    for y in (0.1, 0.55, 1.0, 1.45, 1.88):
        p.box('metal', -x + 0.03, x - 0.03, y, y + 0.02, 0.02, 0.41)
        if y > 1.8: continue
        xx = -x + 0.08
        while xx < x - 0.25:
            w = rng.uniform(0.18, 0.32); h = rng.uniform(0.18, 0.36); m = ['basket', 'paper', 'food_r', 'food_y', 'cart_w'][int(rng.integers(5))]
            p.cham(m, xx, xx + w, y + 0.02, y + 0.02 + h, 0.06, 0.38, 0.006); xx += w + 0.03
    return p

def park_bench(L1=1.8):
    """Banco de praca: 2 pes de ferro fundido em curva, assento e encosto de 6 ripas pintadas (pivo: centro, chao; senta-se de frente para +Z)."""
    p = Piece(); x = L1 / 2 - 0.12
    for s in (-1, 1):
        xx = s * x
        p.hull('iron', [(xx + d, y, z) for d in (-0.025, 0.025) for (y, z) in ((0.0, 0.22), (0.0, 0.28), (0.42, 0.2), (0.42, 0.16))])
        p.hull('iron', [(xx + d, y, z) for d in (-0.025, 0.025) for (y, z) in ((0.0, -0.24), (0.0, -0.3), (0.42, -0.2), (0.42, -0.14))])
        p.hull('iron', [(xx + d, y, z) for d in (-0.025, 0.025) for (y, z) in ((0.4, -0.24), (0.44, -0.24), (0.4, 0.24), (0.44, 0.24))])
        p.hull('iron', [(xx + d, y, z) for d in (-0.025, 0.025) for (y, z) in ((0.42, -0.2), (0.42, -0.26), (0.86, -0.34), (0.86, -0.29))])
        p.hull('iron', [(xx + d, y, z) for d in (-0.025, 0.025) for (y, z) in ((0.62, -0.26), (0.66, -0.26), (0.66, 0.22), (0.62, 0.22))])
        p.sphere('iron', 0.035, xx, 0.66, 0.24, 1)
    for k in range(4):
        z0 = -0.22 + k * 0.115; p.cham('bench_g', -L1 / 2, L1 / 2, 0.44, 0.475, z0, z0 + 0.095, 0.006)
    for k in range(3):
        t0 = 0.48 + k * 0.13; z0 = -0.22 - (t0 - 0.42) * 0.27; y0 = t0
        p.hull('bench_g', [(xx, y0 + dy, z0 - dy * 0.27 + dz) for xx in (-L1 / 2, L1 / 2) for dy in (0.0, 0.1) for dz in (-0.035, 0.0)])
    return p
def lamp_post(h=3.8):
    """Poste de lanterna de ferro: base moldada, fuste canelado, braco com volutas e lanterna de 4 vidros (pivo: centro, chao)."""
    p = Piece()
    lathe(p, 'iron', [(0.18, 0.0), (0.18, 0.12), (0.14, 0.16), (0.14, 0.45), (0.1, 0.55), (0.08, 0.62)], sec=16)
    for k in range(8):
        a = k * math.pi / 4; p.box('iron', 0, 0, 0, 0, 0, 0) if False else seg_cyl(p, 'iron', (0.062 * math.cos(a), 0.62, 0.062 * math.sin(a)), (0.05 * math.cos(a), h - 0.5, 0.05 * math.sin(a)), 0.018, 6)
    p.cyl('iron', 0.05, 0.62, h - 0.5, 0, 0, 12)
    lathe(p, 'iron', [(0.06, h - 0.5), (0.1, h - 0.44), (0.07, h - 0.38), (0.12, h - 0.34)], sec=16)
    yb = h - 0.34
    p.hull('iron', [(x, yb, z) for x in (-0.17, 0.17) for z in (-0.17, 0.17)] + [(x, yb + 0.05, z) for x in (-0.15, 0.15) for z in (-0.15, 0.15)])
    p.box('lamp_glass', -0.13, 0.13, yb + 0.05, yb + 0.48, -0.13, 0.13)
    for sx in (-1, 1):
        for sz in (-1, 1): p.box('iron', sx * 0.14 - 0.015, sx * 0.14 + 0.015, yb + 0.05, yb + 0.5, sz * 0.14 - 0.015, sz * 0.14 + 0.015)
    p.hull('iron', [(x, yb + 0.5, z) for x in (-0.22, 0.22) for z in (-0.22, 0.22)] + [(0, yb + 0.78, 0)]); p.sphere('iron', 0.04, 0, yb + 0.8, 0, 1)
    return p

# ============================================================================ clube: modulos de reboco sobre tijolo (pivo: face externa, cota do piso; dentro em -Z)
BASE_Y = 0.9                                 # topo do embasamento de tijolo
def c_core(p, holes, xa, xb, ea=0.0, eb=0.0):
    xs = sorted(set([xa, xb] + [v for h in holes for v in h[:2] if xa < v < xb]))
    ys = sorted(set([GY - Y0, 0.0, BASE_Y, 1.1, CH] + [v for h in holes for v in h[2:] if v < CH]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if cy < 0: return 'concrete'
        if k == 0: return 'tile' if cy < 1.1 else 'plaster'
        return 'brick' if cy < BASE_Y else 'render'
    for m, mesh in grid_solid(xs, ys, [-T, -0.12, 0.0], cell).items(): p.add(m, mesh)
    gaps = [(a - 0.02, b + 0.02) for (a, b, c, d) in holes if c < BASE_Y + 0.1]
    for (a, b) in segs_excl(gaps, xa - ea, xb + eb):                                                  # capa do embasamento
        prof_x(p, 'coping', a, b, [(0.0, BASE_Y - 0.01), (0.045, BASE_Y - 0.01), (0.045, BASE_Y + 0.03), (0.0, BASE_Y + 0.06)])
    for (a, b) in segs_excl([(a, b) for (a, b, c, d) in holes if d > 2.7], xa - ea, xb + eb):          # friso sob o beiral
        prof_x(p, 'trim', a, b, [(0.0, 2.78), (0.02, 2.78), (0.02, 2.82), (0.035, 2.84), (0.035, 2.92), (0.0, 2.92)])
def c_door(p, lamp=True):
    for s in (-1, 1):
        a, b = sorted((s * 0.5, s * 0.46)); p.box('trim', a, b, 0.0, 2.3, -0.2, -0.04)
    p.box('trim', -0.46, 0.46, 2.26, 2.3, -0.2, -0.04)
    p.cham('steel', -0.5, 0.5, -0.02, 0.006, -T + 0.004, 0.03, 0.003)
    for s in (-1, 1):                                                                                 # guarnicao larga
        a, b = sorted((s * 0.5, s * 0.62)); prof_y(p, 'trim', 0.0, 2.42, crect(a, b, 0.0, 0.035, 0.006, (0, 0, 1, 1)))
    prof_x(p, 'trim', -0.66, 0.66, [(0.0, 2.42), (0.07, 2.42), (0.07, 2.45), (0.05, 2.47), (0.0, 2.48)])
    p.box('trim', -0.62, 0.62, 2.3, 2.42, 0.0, 0.035)
    if lamp: p.merge(wall_lantern(), tr(0.9, 2.2, 0.0))
def awning(p, w=1.9, d=0.85, y0=2.18, y1=2.6, n=9):
    """Toldo listrado de vermelho e branco com bambinela e bracos de ferro (pivo: face da parede, centro)."""
    cols = ['flag_r', 'paint_w']; xs = np.linspace(-w / 2, w / 2, n + 1)
    for i in range(n):
        a, b = xs[i], xs[i + 1]; m = cols[i % 2]
        p.hull(m, [(x, y, z) for x in (a, b) for (y, z) in ((y1, 0.01), (y1 - 0.012, 0.01), (y0, d), (y0 - 0.012, d))])
        for k in range(3):                                                                            # bambinela em ondas
            u0 = a + (b - a) * k / 3; u1 = a + (b - a) * (k + 1) / 3
            p.hull(m, [(x, y, z) for x in (u0, u1) for y in (y0, y0 - 0.15) for z in (d, d + 0.012)] + [((u0 + u1) / 2, y0 - 0.19, z) for z in (d, d + 0.012)])
    for s in (-1, 1):
        x = s * (w / 2 - 0.03)
        seg_cyl(p, 'iron', (x, y0 - 0.45, 0.0), (x, y0 - 0.03, d - 0.02), 0.012, 6); p.box('iron', x - 0.03, x + 0.03, y0 - 0.5, y0 - 0.4, 0.0, 0.015)
    seg_cyl(p, 'iron', (-w / 2, y1 + 0.02, 0.03), (w / 2, y1 + 0.02, 0.03), 0.025, 8)
def pictogram(p, y=1.75, z=0.0):
    """Placa redonda com pictograma de taco e bolinha (sem texto)."""
    disc_z(p, 'trim', 0.42, z, z + 0.04, 0.0, y, 32); disc_z(p, 'door', 0.38, z + 0.04, z + 0.055, 0.0, y, 32)
    p.hull('paint_w', [(x, yy, zz) for (x, yy) in ((-0.17, y + 0.2), (-0.14, y + 0.22), (0.1, y - 0.15), (0.07, y - 0.17)) for zz in (z + 0.055, z + 0.066)])
    p.hull('paint_w', [(x, yy, zz) for (x, yy) in ((0.06, y - 0.15), (0.2, y - 0.15), (0.2, y - 0.2), (0.04, y - 0.2)) for zz in (z + 0.055, z + 0.066)])
    disc_z(p, 'paint_w', 0.06, z + 0.055, z + 0.07, -0.12, y - 0.16, 16)
    disc_z(p, 'flag_y', 0.05, z + 0.055, z + 0.068, 0.16, y + 0.16, 16)
def c_mod(kind='plain', tl=0.0, tr_=0.0, ea=0.0, eb=0.0):
    """plain, win (janela de guilhotina larga), door (porta com guarnicao e arandela), door_b (porta dos fundos),
    svc (janela de atendimento com balcao de fora e toldo listrado), sign (parede com placa de pictograma).
    tl/tr: modulo de quina encurtado; ea/eb: quanto a capa e o friso passam da ponta (para fechar a quina)."""
    p = Piece(); xa, xb = -W / 2 + tl, W / 2 - tr_
    if kind == 'win':
        c_core(p, [(-0.6, 0.6, 1.1, 2.3)], xa, xb, ea, eb); window(p, 1.2, 1.1, 2.3, 2)
    elif kind in ('door', 'door_b'):
        c_core(p, [(-0.5, 0.5, 0.0, 2.3)], xa, xb, ea, eb); c_door(p, True)
    elif kind == 'svc':
        c_core(p, [(-0.75, 0.75, 0.95, 2.05)], xa, xb, ea, eb)
        for s in (-1, 1):
            a, b = sorted((s * 0.75, s * 0.71)); p.box('trim', a, b, 0.99, 2.05, -0.2, -0.04)
        p.box('trim', -0.71, 0.71, 2.01, 2.05, -0.2, -0.04)
        p.cham('wood', -0.86, 0.86, 0.95, 0.99, -T - 0.02, 0.32, 0.006)
        for s in (-1, 1): seg_cyl(p, 'iron', (s * 0.7, 0.62, 0.0), (s * 0.7, 0.948, 0.28), 0.012, 6)
        p.box('coping', -0.88, 0.88, 2.05, 2.15, 0.0, 0.03)
        awning(p)
    else:
        c_core(p, [], xa, xb, ea, eb)
        if kind == 'sign': pictogram(p, 1.85, 0.0)
    return p

# ============================================================================ cobertura, piso e rodapes do clube (pivo: origem, cota do piso)
CB = sbox(CX0, CZ0, CX1, CZ1); CI = off(CB, -T)
RO = 0.45; RPITCH = math.radians(26); RIN = 2.1
RX0, RX1, RZ0, RZ1 = CX0 - RO, CX1 + RO, CZ0 - RO, CZ1 + RO
RYE = CH; RYT = CH + 0.16; RYR = RYT + RIN * math.tan(RPITCH)     # beiral, topo da testeira, topo plano
BALL_R = 1.0; BALL_C = ((CX0 + CX1) / 2, RYR + 0.42 + BALL_R * 0.92, (CZ0 + CZ1) / 2)
def golf_ball(p, r, c, n=150):
    """Bola de golfe gigante com covinhas em espiral de Fibonacci (sem as do fundo, que ficam no tee)."""
    s = trimesh.creation.icosphere(subdivisions=3, radius=r); s.apply_translation(c); p.add('ball', s)
    ga = math.pi * (3 - math.sqrt(5))
    for k in range(n):
        yk = 1 - 2 * (k + 0.5) / n
        if yk < -0.72: continue
        rk = math.sqrt(1 - yk * yk); a = ga * k
        d = np.array([rk * math.cos(a), yk, rk * math.sin(a)])
        q = trimesh.creation.icosphere(subdivisions=0, radius=r * 0.075); q.apply_scale([1.0, 1.0, 1.0])
        q.apply_translation(np.array(c) + d * r * 0.94); p.add('ball_d', q)
def c_roof():
    """Forro com luminarias, telhado de 4 aguas de telhas verdes com topo plano, espigoes, testeira branca, calhas com condutores,
    mureta no topo e a bola de golfe gigante sobre o tee."""
    p = Piece()
    ext_y(p, 'ceil', CI, CCEIL, CCEIL + 0.03)
    for (x, z) in ((12.0, 5.0), (16.0, 5.0)):
        p.box('trim', x - 0.6, x + 0.6, CCEIL - 0.008, CCEIL, z - 0.15, z + 0.15); p.box('lamp_glass', x - 0.56, x + 0.56, CCEIL - 0.03, CCEIL - 0.008, z - 0.12, z + 0.12)
    tx0, tx1, tz0, tz1 = RX0 + RIN, RX1 - RIN, RZ0 + RIN, RZ1 - RIN
    p.hull('roof_g', [(x, y, z) for x in (RX0, RX1) for z in (RZ0, RZ1) for y in (RYE, RYT)] + [(x, RYR, z) for x in (tx0, tx1) for z in (tz0, tz1)])
    for (x, z, xx, zz) in ((RX0, RZ0, tx0, tz0), (RX0, RZ1, tx0, tz1), (RX1, RZ0, tx1, tz0), (RX1, RZ1, tx1, tz1)):
        seg_cyl(p, 'roof_g', (x, RYT + 0.03, z), (xx, RYR + 0.02, zz), 0.055, 8)                   # espigoes
    for (x0, x1, z0, z1) in ((RX0 - 0.025, RX1 + 0.025, RZ1, RZ1 + 0.025), (RX0 - 0.025, RX1 + 0.025, RZ0 - 0.025, RZ0), (RX0 - 0.025, RX0, RZ0, RZ1), (RX1, RX1 + 0.025, RZ0, RZ1)):
        p.box('trim', x0, x1, RYE - 0.06, RYT, z0, z1)
    # mureta do topo plano
    top = sbox(tx0, tz0, tx1, tz1)
    ext_y(p, 'trim', top.difference(off(top, -0.12)), RYR, RYR + 0.18); ext_y(p, 'roof_g', off(top, -0.12), RYR, RYR + 0.02)
    # calhas (frente e fundos) e condutores
    for zz, sg, xs_ in ((RZ1 + 0.025, 1, (CX0 + 0.14, CX1 - 0.14)), (RZ0 - 0.025, -1, (CX0 + 0.14, CX1 - 0.14))):
        prof = [(0.0, RYE + 0.06), (0.0, RYE - 0.06), (0.12, RYE - 0.06), (0.14, RYE + 0.06), (0.12, RYE + 0.06), (0.105, RYE - 0.04), (0.015, RYE - 0.04), (0.015, RYE + 0.06)]
        prof_x(p, 'gutter', RX0 - 0.025, RX1 + 0.025, [(zz + sg * u, y) for (u, y) in prof])
        zw = (CZ1 + 0.06) if sg > 0 else (CZ0 - 0.06); zc_ = zz + sg * 0.065
        for x in xs_:
            seg_cyl(p, 'gutter', (x, RYE - 0.05, zc_), (x, RYE - 0.3, zc_), 0.04, 10); seg_cyl(p, 'gutter', (x, RYE - 0.3, zc_), (x, RYE - 0.55, zw), 0.04, 10)
            seg_cyl(p, 'gutter', (x, RYE - 0.55, zw), (x, -Y0 + 0.12 if sg > 0 else YL - Y0 + 0.06, zw), 0.04, 10)
            for yy in (0.8, 1.9): p.box('gutter', x - 0.05, x + 0.05, yy, yy + 0.03, *sorted((zw, CZ1 if sg > 0 else CZ0)))
    # tee e bola
    bx, by, bz = BALL_C
    lathe(p, 'flag_y', [(0.5, RYR + 0.02), (0.5, RYR + 0.08), (0.14, RYR + 0.14), (0.12, RYR + 0.3), (0.5, RYR + 0.42), (0.56, RYR + 0.47)], bx, bz, 0.0, 24)
    golf_ball(p, BALL_R, BALL_C)
    return p
def c_floor():
    p = Piece(); ext_y(p, 'concrete', CI, GY - Y0 + 0.02, -0.012)
    b = CI.bounds; step = 0.4
    for i in range(int(round((b[2] - b[0]) / step + 0.5))):
        for j in range(int(round((b[3] - b[1]) / step + 0.5))):
            q = sbox(b[0] + i * step, b[1] + j * step, b[0] + (i + 1) * step, b[1] + (j + 1) * step).intersection(CI)
            if q.area > 1e-6: ext_y(p, 'tile' if (i + j) % 2 == 0 else 'tile_b', q, -0.012, 0.0)
    return p
def c_plan():
    """Rodape de azulejo verde nas paredes de dentro, parando nas portas."""
    p = Piece(); band = CI.difference(off(CI, -0.012))
    dr = unary_union([sbox(12.4, CZ1 - T - 0.1, 13.6, CZ1 - T + 0.1), sbox(14.4, CZ0 + T - 0.1, 15.6, CZ0 + T + 0.1)])
    ext_y(p, 'tile_b', band.difference(dr), 0.0, 0.12); return p

# ============================================================================ buracos (pivo: origem, coordenadas absolutas)
def green_poly(path): return LineString(path).buffer(GW / 2, cap_style=2, join_style=2)
def unit2(a, b): v = np.array(b, float) - np.array(a, float); return v / np.linalg.norm(v)
FLAGC = ['flag_r', 'flag_y', 'flag_b', 'umb_o', 'flag_g']
def hole(k):
    """Buraco k (1 a 5): laje de concreto, grama sintetica, borda de tijolo com capa, tapete do tee com bolinha, placa do tee com
    k pontos (sem numeros), copo com aro branco, bandeirinha e obstaculos."""
    path = HOLES[k - 1]; p = Piece(); g = green_poly(path); ob = off(g, GB)
    ext_y(p, 'concrete', g, -0.1, GT0); ext_y(p, 'turf', g, GT0, GT1)
    ext_y(p, 'brick', ob.difference(g), -0.1, 0.32); ext_y(p, 'coping', off(g, GB + 0.015).difference(g), 0.32, 0.35)
    # tee
    d = unit2(path[0], path[1]); c = np.array(path[0]) + d * 0.4; n_ = np.array([-d[1], d[0]])
    q = Polygon([tuple(c + d * a + n_ * b) for (a, b) in ((-0.22, -0.3), (0.22, -0.3), (0.22, 0.3), (-0.22, 0.3))]); ext_y(p, 'tee_m', q, GT1, GT1 + 0.012)
    p.sphere('ball', 0.021, c[0], GT1 + 0.012 + 0.021, c[1], 1)
    for s in (-1, 1): e = c + n_ * s * 0.38 + d * 0.1; p.sphere(FLAGC[k - 1], 0.035, e[0], GT1 + 0.035, e[1], 1)
    e = np.array(path[0]) - d * (GB + 0.3); ang = math.atan2(d[0], d[1])
    sg = Piece(); sg.box('dkwood', -0.04, 0.04, -0.1, 0.62, -0.04, 0.04); sg.cham('dkwood', -0.24, 0.24, 0.62, 0.92, -0.03, 0.03, 0.006)
    sg.box('paint_w', -0.21, 0.21, 0.65, 0.89, 0.03, 0.036)
    for i in range(k): disc_z(sg, FLAGC[k - 1], 0.026, 0.036, 0.046, -0.15 + 0.3 * (i + 0.5) / k, 0.77, 12)
    p.merge(sg, rot_y(math.degrees(ang), (e[0], YL, e[1])))
    # copo e bandeirinha
    d2 = unit2(path[-2], path[-1]); h = np.array(path[-1]) - d2 * 0.45
    p.cyl('dark', 0.054, GT1, GT1 + 0.003, h[0], h[1], 20); ring_y(p, 'paint_w', 0.054, 0.066, GT1, GT1 + 0.004, h[0], h[1], 20)
    p.cyl('paint_w', 0.008, GT1 + 0.003, 1.45, h[0], h[1], 8); p.sphere('paint_w', 0.014, h[0], 1.46, h[1], 1)
    p.hull(FLAGC[k - 1], [(h[0] + a, y, h[1] + zz) for (a, y) in ((0.008, 1.43), (0.008, 1.2), (0.36, 1.32)) for zz in (-0.003, 0.003)])
    # obstaculos
    if k == 1:
        for (x, z, r) in ((-12.6, 10.5, 35.0), (-9.0, 8.6, -30.0)):
            q = Piece(); q.cham('brick', -0.3, 0.3, GT1, GT1 + 0.12, -0.07, 0.07, 0.01); q.box('coping', -0.32, 0.32, GT1 + 0.12, GT1 + 0.15, -0.085, 0.085); p.merge(q, rot_y(r, (x, 0, z)))
    if k == 3:
        q = Piece(); ext_y(q, 'brick', Point(-11.0, -6.8).buffer(0.16, 16), GT1, GT1 + 0.14); ext_y(q, 'coping', Point(-11.0, -6.8).buffer(0.18, 16), GT1 + 0.14, GT1 + 0.17); p.merge(q)
        for z in (-8.2, -5.4): p.cham('brick', -11.5, -11.38, GT1, GT1 + 0.12, z - 0.3, z + 0.3, 0.01)
    if k == 5:   # lombada de grama
        for i in range(8):
            a0, a1 = -1.0 + i * 0.25, -1.0 + (i + 1) * 0.25
            y0, y1 = 0.07 * math.cos(a0 * math.pi / 2), 0.07 * math.cos(a1 * math.pi / 2)
            p.hull('turf2', [(x, GT1 + y, z) for (x, y) in ((0.3 + a0 * 0.5, y0), (0.3 + a1 * 0.5, y1)) for z in (9.0, 10.0)] + [(x, GT1, z) for x in (0.3 + a0 * 0.5, 0.3 + a1 * 0.5) for z in (9.0, 10.0)])
    return p

# ============================================================================ moinho holandes (pivo: origem, coordenadas absolutas)
def oct_solid(p, mat, prof, x, z, n=8, a0=math.pi / 8):
    for (r0, ya), (r1, yb) in zip(prof[:-1], prof[1:]):
        if abs(yb - ya) < 1e-6: continue
        p.hull(mat, [(x + r * math.cos(a0 + 2 * math.pi * k / n), y, z + r * math.sin(a0 + 2 * math.pi * k / n)) for (r, y) in ((r0, ya), (r1, yb)) for k in range(n)])
def sail(p, hub, ang, Ls=2.9, zf=0.0):
    """Pa de trelica: vara, ripas transversais, longarinas e lona (no plano x-y, na frente do cubo)."""
    ca, sa = math.cos(ang), math.sin(ang); u = np.array([ca, sa, 0.0]); v = np.array([-sa, ca, 0.0]); h = np.array(hub, float)
    seg_cyl(p, 'dkwood', h + u * 0.2 + [0, 0, zf], h + u * Ls + [0, 0, zf], 0.045, 6)
    for k in range(9):
        r = 0.75 + k * (Ls - 0.8) / 8; a = h + u * r + [0, 0, zf + 0.05]
        p.seg('wood', a - v * 0.05, a + v * 0.55, 0.035, 0.03)
    for w in (0.18, 0.55):
        p.seg('wood', h + u * 0.75 + v * w + [0, 0, zf + 0.08], h + u * Ls + v * w + [0, 0, zf + 0.08], 0.03, 0.025)
    p.hull('sail', [h + u * r + v * w + [0, 0, zf + dz] for r in (0.95, Ls - 0.15) for w in (0.2, 0.52) for dz in (0.1, 0.11)])
def windmill():
    """Moinho holandes de 8 faces: base de pedra com tunel por onde passa o buraco 2, corpo de reboco claro, galeria de madeira com
    guarda-corpo, porta e janelinhas, capuz vermelho com cumeeira, eixo e 4 pas de trelica com lona."""
    p = Piece(); x, z = MILL; rb = 1.72
    oct_solid(p, 'stone', [(rb, -0.15), (rb, 0.95)], x, z)
    p = subtract_prism(p, sbox(x - 3, z - 0.66, x + 3, z + 0.66), -0.5, 0.82)
    oct_solid(p, 'coping', [(rb + 0.06, 0.95), (rb + 0.06, 1.03)], x, z)
    fx = rb * math.cos(math.pi / 8)
    for s in (-1, 1):   # moldura das bocas do tunel
        a, b = sorted((x + s * (fx + 0.002), x + s * (fx + 0.04)))
        for (z0, z1) in ((z - 0.8, z - 0.66), (z + 0.66, z + 0.8)): p.box('coping', a, b, 0.2, 0.92, z0, z1)
        p.box('coping', a, b, 0.82, 0.94, z - 0.8, z + 0.8)
    p.box('dark', x - fx + 0.01, x + fx - 0.01, 0.8, 0.82, z - 0.66, z + 0.66)                       # forro escuro do tunel
    for s in (-1, 1): p.box('dark', x - fx + 0.01, x + fx - 0.01, 0.36, 0.8, *sorted((z + s * 0.66, z + s * 0.64)))
    # corpo
    oct_solid(p, 'mill_w', [(1.45, 1.03), (1.05, 5.0)], x, z)
    oct_solid(p, 'mill_r', [(1.08, 5.0), (1.08, 5.12)], x, z)
    # cantoneiras de madeira nas arestas do corpo
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 8
        seg_cyl(p, 'dkwood', (x + 1.47 * math.cos(a), 1.03, z + 1.47 * math.sin(a)), (x + 1.07 * math.cos(a), 5.0, z + 1.07 * math.sin(a)), 0.035, 6)
    # galeria a 3,0 m
    yg = 3.0; rg = 1.45 - (yg - 1.03) / (5.0 - 1.03) * 0.4
    oct_solid(p, 'deck', [(rg + 0.55, yg - 0.08), (rg + 0.55, yg)], x, z)
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 8; b_ = 2 * math.pi * (k + 1) / 8 + math.pi / 8; R = rg + 0.5
        pa = np.array([x + R * math.cos(a), yg, z + R * math.sin(a)]); pb = np.array([x + R * math.cos(b_), yg, z + R * math.sin(b_)])
        seg_cyl(p, 'dkwood', pa, pa + [0, 0.85, 0], 0.03, 6)
        seg_cyl(p, 'dkwood', pa + [0, 0.85, 0], pb + [0, 0.85, 0], 0.025, 6); seg_cyl(p, 'dkwood', pa + [0, 0.45, 0], pb + [0, 0.45, 0], 0.015, 6)
        for t in np.linspace(0.2, 0.8, 4): q = pa + (pb - pa) * t; seg_cyl(p, 'dkwood', q, q + [0, 0.45, 0], 0.012, 6)
        m = (pa + pb) / 2; seg_cyl(p, 'dkwood', (x + rg * 0.96 * math.cos((a + b_) / 2), yg - 0.8, z + rg * 0.96 * math.sin((a + b_) / 2)), m - [0, 0.06, 0], 0.03, 6)
    # porta (para +Z, na galeria) e janelinhas
    fz = 1.25
    def face_box(m, y0, y1, w, r_at, depth=0.04, ang=math.pi / 2):
        rr = r_at(y0), r_at(y1); ca, sa = math.cos(ang), math.sin(ang); tg = np.array([-sa, ca])
        pts = []
        for (y, r) in ((y0, rr[0]), (y1, rr[1])):
            ri = r * math.cos(math.pi / 8)
            for e in (-0.03, depth):
                c = np.array([x + (ri + e) * ca, z + (ri + e) * sa])
                for s in (-1, 1): q = c + tg * s * w / 2; pts.append((q[0], y, q[1]))
        p.hull(m, pts)
    rf = lambda y: 1.45 - (y - 1.03) / (5.0 - 1.03) * 0.4
    face_box('door', yg, yg + 1.9, 0.7, rf, 0.03); face_box('trim', yg + 1.9, yg + 2.0, 0.86, rf, 0.04)
    for (y, ang) in ((1.7, math.pi / 2), (4.3, math.pi / 2), (2.0, -math.pi / 2), (4.2, -math.pi / 2), (3.4, 0.0), (3.4, math.pi)):
        face_box('dark', y, y + 0.45, 0.32, rf, 0.02, ang); face_box('trim', y - 0.06, y, 0.42, rf, 0.04, ang)
    # capuz (telhado de 2 aguas arredondado) com cumeeira, virado para +Z
    yc = 5.12
    for i in range(10):
        t0, t1 = math.pi * i / 10, math.pi * (i + 1) / 10
        pts = [(x + 1.2 * math.cos(t), yc + 1.15 * math.sin(t) + e, z + zz) for t in (t0, t1) for zz in (-1.35, 1.45) for e in (0.0, 0.06)]
        p.hull('mill_r', pts)
    q = Polygon([(x + 1.17 * math.cos(t), yc + 1.12 * math.sin(t)) for t in np.linspace(0, math.pi, 21)])
    ext(p, 'mill_r', q, z - 1.36, z - 1.34); ext(p, 'mill_r', q, z + 1.3, z + 1.43)
    seg_cyl(p, 'dkwood', (x, yc + 1.2, z - 1.4), (x, yc + 1.2, z + 1.5), 0.05, 8)
    # eixo, cubo e pas
    hub = (x, yc + 0.55, z + 1.95)
    seg_cyl(p, 'iron', (x, yc + 0.55, z + 1.2), hub, 0.11, 12); p.sphere('iron', 0.2, *hub, 1)
    for k in range(4): sail(p, hub, math.radians(20 + 90 * k), 2.9, 0.05)
    return p

# ============================================================================ farol (pivo: origem, coordenadas absolutas)
def lighthouse():
    """Farol listrado de vermelho e branco sobre pedras: plinto de concreto, torre conica de 7 faixas, porta, janelinhas, galeria com
    guarda-corpo, lanterna de vidro com montantes e lampada, cupula vermelha, para-raios."""
    p = Piece(); x, z = LH; rng = np.random.default_rng(5)
    p.cyl('concrete', 1.05, -0.15, 0.55, x, z, 32); p.cyl('coping', 1.1, 0.55, 0.6, x, z, 32)
    for k in range(16):   # pedras em volta
        a = 2 * math.pi * k / 16 + rng.uniform(-0.12, 0.12); r = rng.uniform(1.1, 1.45); s = rng.uniform(0.28, 0.5)
        cx, cz = x + r * math.cos(a), z + r * math.sin(a)
        pts = [(cx + rng.uniform(-s, s), rng.uniform(-0.1, 0.0) if j < 6 else rng.uniform(0.15, 0.25 + s), cz + rng.uniform(-s, s)) for j in range(12)]
        p.hull('rock' if k % 3 else 'rock2', pts)
    r0, r1, y0, y1 = 0.85, 0.55, 0.6, 6.0; n = 7
    rf = lambda y: r0 + (r1 - r0) * (y - y0) / (y1 - y0)
    for i in range(n):
        ya, yb = y0 + (y1 - y0) * i / n, y0 + (y1 - y0) * (i + 1) / n
        lathe(p, 'lh_w' if i % 2 == 0 else 'lh_r', [(rf(ya), ya), (rf(yb), yb)], x, z, 0.0, 28)
    # porta (+Z) e janelinhas
    def on_face(m, ya, yb, w, ang, dep=0.03):
        ca, sa = math.cos(ang), math.sin(ang); tg = np.array([-sa, ca]); pts = []
        for y in (ya, yb):
            for e in (-0.04, dep):
                c = np.array([x + (rf(y) + e) * ca, z + (rf(y) + e) * sa])
                for s in (-1, 1): q = c + tg * s * w / 2; pts.append((q[0], y, q[1]))
        p.hull(m, pts)
    on_face('door', 0.6, 2.4, 0.72, math.pi / 2, 0.02); on_face('steel_d', 2.4, 2.5, 0.86, math.pi / 2, 0.05)
    for (y, ang) in ((3.3, -math.pi / 2), (4.6, math.pi / 2), (4.0, 0.2), (2.8, math.pi + 0.3)):
        on_face('dark', y, y + 0.45, 0.24, ang, 0.012); on_face('steel_d', y - 0.05, y, 0.32, ang, 0.04)
    # galeria
    p.cyl('steel_d', 0.6, y1, y1 + 0.06, x, z, 28); p.cyl('steel_d', 1.0, y1 + 0.06, y1 + 0.16, x, z, 32)
    for k in range(16):
        a = 2 * math.pi * k / 16; b_ = 2 * math.pi * (k + 1) / 16; R = 0.94
        pa = np.array([x + R * math.cos(a), y1 + 0.16, z + R * math.sin(a)]); pb = np.array([x + R * math.cos(b_), y1 + 0.16, z + R * math.sin(b_)])
        seg_cyl(p, 'iron', pa, pa + [0, 0.8, 0], 0.016, 6); seg_cyl(p, 'iron', pa + [0, 0.8, 0], pb + [0, 0.8, 0], 0.02, 6)
        seg_cyl(p, 'iron', pa + [0, 0.4, 0], pb + [0, 0.4, 0], 0.01, 6)
        q = np.array([x + 0.58 * math.cos(a), y1 - 0.5, z + 0.58 * math.sin(a)]); seg_cyl(p, 'steel_d', q, pa - [0, 0.12, 0] + (q - pa) * 0.0, 0.02, 6) if k % 2 == 0 else None
    # lanterna
    yl0, yl1 = y1 + 0.16, y1 + 1.2
    p.cyl('lh_r', 0.62, yl0, yl0 + 0.3, x, z, 24)
    p.cyl('glass', 0.55, yl0 + 0.3, yl1, x, z, 24)
    for k in range(8):
        a = 2 * math.pi * k / 8; seg_cyl(p, 'iron', (x + 0.56 * math.cos(a), yl0 + 0.305, z + 0.56 * math.sin(a)), (x + 0.56 * math.cos(a), yl1 - 0.005, z + 0.56 * math.sin(a)), 0.02, 6)
    ring_y(p, 'iron', 0.54, 0.6, yl0 + 0.302, yl0 + 0.34, x, z, 24)
    p.sphere('lamp_glass', 0.26, x, (yl0 + yl1) / 2 + 0.12, z, 2); p.cyl('steel_d', 0.08, yl0 + 0.3, (yl0 + yl1) / 2 - 0.1, x, z, 10)
    p.cyl('lh_r', 0.66, yl1, yl1 + 0.06, x, z, 24)
    lathe(p, 'lh_r', [(0.64, yl1 + 0.06), (0.5, yl1 + 0.3), (0.28, yl1 + 0.5), (0.08, yl1 + 0.62)], x, z, 0.0, 24)
    p.sphere('lh_r', 0.1, x, yl1 + 0.68, z, 1); seg_cyl(p, 'iron', (x, yl1 + 0.7, z), (x, yl1 + 1.2, z), 0.012, 6)
    return p

# ============================================================================ lago e ponte (pivo: origem, coordenadas absolutas)
def pond_poly(grow=0.0):
    cx, cz, rx, rz = POND
    return Polygon([(cx + (rx + grow) * math.cos(t), cz + (rz + grow) * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 48, endpoint=False)])
def pond():
    """Lago raso: fundo escuro, parede e beira de pedra, agua transparente, pedras e juncos."""
    p = Piece(); P = pond_poly(); rng = np.random.default_rng(9)
    ext_y(p, 'pond_b', P, -0.42, -0.36); ext_y(p, 'stone', pond_poly(0.1).difference(P), -0.42, YL)
    ext_y(p, 'coping', pond_poly(0.28).difference(P), YL, 0.1)
    ext_y(p, 'water', off(P, -0.004), -0.36, -0.06)
    cx, cz, rx, rz = POND
    for k in range(12):
        t = 2 * math.pi * k / 12 + 0.2
        if abs(math.cos(t)) < 0.55: continue
        x, z_ = cx + (rx - 0.25) * math.cos(t), cz + (rz - 0.2) * math.sin(t)
        for j in range(5):
            a = rng.uniform(0, 2 * math.pi); h = rng.uniform(0.5, 0.9)
            seg_cyl(p, 'palm', (x + 0.05 * math.cos(a), -0.36, z_ + 0.05 * math.sin(a)), (x + 0.2 * math.cos(a), h, z_ + 0.2 * math.sin(a)), 0.012, 4)
    for k in range(4):
        a = rng.uniform(0, 2 * math.pi); x, z_ = cx + 1.0 * math.cos(a) * rx / 1.6, cz + 0.6 * math.sin(a)
        p.hull('rock', [(x + rng.uniform(-0.2, 0.2), rng.uniform(-0.4, -0.3), z_ + rng.uniform(-0.2, 0.2)) for _ in range(5)] +
               [(x + rng.uniform(-0.15, 0.15), rng.uniform(-0.04, 0.04), z_ + rng.uniform(-0.15, 0.15)) for _ in range(5)])
    return p
BRZ0, BRZ1 = 4.5, 6.0; BRH = 0.42
def deck_y(x): return Y0 + BRH * math.sin(math.pi * (x - BR0) / (BR1 - BR0))
def bridge():
    """Ponte de madeira em arco: encontros de pedra, 2 longarinas curvas, tabuas transversais, pilares e guarda-corpos com corrimao curvo."""
    p = Piece()
    for (a, b) in ((BR0, BR0 + 0.28), (BR1 - 0.28, BR1)): p.box('stone', a, b, -0.15, Y0 - 0.06, BRZ0, BRZ1)
    N = 34; xs = np.linspace(BR0, BR1, N + 1)
    for i in range(N):
        a, b = xs[i] + 0.006, xs[i + 1] - 0.006
        p.hull('deck', [(x, deck_y(x) + e, z) for x in (a, b) for e in (-0.05, 0.0) for z in (BRZ0 - 0.04, BRZ1 + 0.04)])
    M = 20; xm = np.linspace(BR0 + 0.2, BR1 - 0.2, M + 1)
    for zz in (BRZ0 + 0.1, BRZ1 - 0.1):
        for i in range(M):
            a, b = xm[i], xm[i + 1]
            p.hull('dkwood', [(x, deck_y(x) - 0.05 - e, z) for x in (a, b) for e in (0.002, 0.24) for z in (zz - 0.05, zz + 0.05)])
    posts = np.linspace(BR0 + 0.1, BR1 - 0.1, 7)
    for zz in (BRZ0 + 0.0, BRZ1 - 0.0):
        tops = []
        for x in posts:
            y = deck_y(x); p.box('dkwood', x - 0.05, x + 0.05, y - 0.3, y + 0.95, zz - 0.05 if zz < 5 else zz - 0.05, zz + 0.05); tops.append((x, y + 0.95))
            p.box('dkwood', x - 0.065, x + 0.065, y + 0.95, y + 0.98, zz - 0.065, zz + 0.065)
        for i in range(len(posts) - 1):
            xa, xb = posts[i], posts[i + 1]
            for k in range(4):
                u0, u1 = xa + (xb - xa) * k / 4, xa + (xb - xa) * (k + 1) / 4
                p.hull('wood', [(u, deck_y(u) + 0.86 + e, zz + s * 0.04) for u in (u0 + 0.051 if k == 0 else u0, u1 - 0.051 if k == 3 else u1) for e in (0.0, 0.07) for s in (-1, 1)])
                p.hull('wood', [(u, deck_y(u) + 0.42 + e, zz + s * 0.025) for u in (u0 + 0.051 if k == 0 else u0, u1 - 0.051 if k == 3 else u1) for e in (0.0, 0.06) for s in (-1, 1)])
    return p

# ============================================================================ clube: equipamentos (pivo: centro de tras, piso; frente +Z)
def putter_rack():
    """Estante de tacos: painel de madeira com 2 trilhos e 10 tacos pendurados de cabeca para baixo, com punho e cabeca."""
    p = Piece(); p.cham('wood', -0.7, 0.7, 0.3, 1.6, 0.0, 0.04, 0.006)
    for y in (1.45, 0.45): p.cham('dkwood', -0.66, 0.66, y - 0.04, y + 0.04, 0.04, 0.12, 0.006)
    for i in range(10):
        x = -0.58 + i * 0.129; c = ['flag_r', 'flag_b', 'flag_y', 'flag_g', 'umb_o'][i % 5]
        seg_cyl(p, 'putter', (x, 0.5, 0.09), (x, 1.5, 0.09), 0.007, 6)
        seg_cyl(p, 'grip', (x, 1.28, 0.09), (x, 1.53, 0.09), 0.013, 8); seg_cyl(p, c, (x, 1.53, 0.09), (x, 1.56, 0.09), 0.015, 8)
        p.cham('chrome', x - 0.016, x + 0.016, 0.36, 0.5, 0.06, 0.16, 0.004)
    return p
def ball_bin():
    """Caixote de madeira com bolinhas coloridas e uma prateleira de baixo (pivo: centro de tras, piso)."""
    p = Piece(); rng = np.random.default_rng(3)
    for (x0, x1, z0, z1) in ((-0.4, 0.4, 0.0, 0.03), (-0.4, 0.4, 0.47, 0.5), (-0.4, -0.37, 0.03, 0.47), (0.37, 0.4, 0.03, 0.47)):
        p.box('wood', x0, x1, 0.0, 0.85, z0, z1)
    p.box('wood', -0.37, 0.37, 0.0, 0.03, 0.03, 0.47); p.box('wood', -0.37, 0.37, 0.4, 0.43, 0.03, 0.47); ext_y(p, 'dkwood', sbox(-0.42, -0.02, 0.42, 0.52).difference(sbox(-0.35, 0.05, 0.35, 0.45)), 0.85, 0.88)
    for k in range(70):
        c = ['ball', 'flag_r', 'flag_y', 'flag_b', 'umb_o', 'flag_g'][k % 6]; p.sphere(c, 0.021, rng.uniform(-0.33, 0.33), 0.454 + rng.uniform(0, 0.36), rng.uniform(0.06, 0.44), 0)
    for k in range(6): p.cham('flag_y' if k % 2 else 'paper', -0.3 + k * 0.1, -0.22 + k * 0.1, 0.03, 0.26, 0.08, 0.38, 0.004)
    return p
def score_stand():
    """Suporte de cartoes de pontuacao e cestinha de lapis sobre o balcao (sem texto)."""
    p = Piece(); p.cham('dkwood', -0.15, 0.15, 0.0, 0.18, -0.08, 0.08, 0.004)
    for k in range(5): p.box('paper', -0.12, 0.12, 0.02 + 0.0, 0.17, -0.06 + k * 0.025, -0.055 + k * 0.025)
    p.cyl('basket', 0.05, 0.0, 0.1, 0.24, 0.0, 12)
    for k in range(6): a = k * math.pi / 3; seg_cyl(p, 'flag_y', (0.24 + 0.02 * math.cos(a), 0.02, 0.02 * math.sin(a)), (0.24 + 0.03 * math.cos(a), 0.17, 0.03 * math.sin(a)), 0.004, 5)
    return p
def bench_in(L1=1.6):
    """Banco de madeira de encosto na parede (pivo: centro de tras, piso)."""
    p = Piece()
    for x in (-L1 / 2 + 0.1, L1 / 2 - 0.1):
        for z in (0.06, 0.34): p.box('dkwood', x - 0.03, x + 0.03, 0.0, 0.42, z - 0.03, z + 0.03)
    for k in range(3): p.cham('wood', -L1 / 2, L1 / 2, 0.42, 0.45, 0.02 + k * 0.13, 0.13 + k * 0.13, 0.005)
    p.box('dkwood', -L1 / 2 + 0.07, L1 / 2 - 0.07, 0.25, 0.3, 0.03, 0.09)
    return p

# ============================================================================ patio e jardim (pivo: centro, chao)
def palm(h=6.0, lean=(0.6, 0.2), seed=1):
    """Palmeira: tronco curvo de aneis com escamas, coroa de 10 folhas arqueadas com foliolos e cachos de cocos."""
    p = Piece(); rng = np.random.default_rng(seed); N = 14
    pts = [np.array([lean[0] * (t ** 2), h * t, lean[1] * (t ** 2)]) for t in np.linspace(0, 1, N + 1)]
    for i in range(N):
        r0 = 0.2 - 0.07 * i / N; r1 = 0.2 - 0.07 * (i + 1) / N
        seg_cyl(p, 'bark', pts[i] - [0, 0.15 if i == 0 else 0, 0], pts[i + 1], (r0 + r1) / 2, 10)
        seg_cyl(p, 'dkwood', pts[i + 1] - [0, 0.03, 0], pts[i + 1] + [0, 0.03, 0], (r1 + 0.018), 10) if i < N - 1 else None
    top = pts[-1]; p.sphere('bark', 0.2, *top, 1)
    for k in range(3): a = 2 * math.pi * k / 3 + 0.4; p.sphere('dkwood', 0.09, top[0] + 0.17 * math.cos(a), top[1] - 0.12, top[2] + 0.17 * math.sin(a), 1)
    for k in range(10):
        a = 2 * math.pi * k / 10 + rng.uniform(-0.15, 0.15); L = rng.uniform(2.0, 2.5); up = rng.uniform(0.35, 0.7) if k % 2 else rng.uniform(0.1, 0.35)
        d = np.array([math.cos(a), 0, math.sin(a)]); side = np.array([-math.sin(a), 0, math.cos(a)])
        prev = top.copy(); M = 7; c = 'palm' if k % 2 else 'palm2'
        for j in range(1, M + 1):
            t = j / M; q = top + d * L * t + np.array([0, (up * 2.2 * t - 2.4 * t * t) * 1.0, 0])
            seg_cyl(p, 'palm2', prev, q, 0.018, 4)
            w = 0.45 * math.sin(math.pi * min(1.0, t * 1.15)) + 0.04
            for s in (-1, 1):
                tip = (prev + q) / 2 + side * s * w + np.array([0, -0.12 - 0.1 * t, 0])
                p.hull(c, [prev, q, tip, prev + [0, 0.012, 0], q + [0, 0.012, 0]])
            prev = q
    return p
def umbrella_table(c1='umb_r', c2='paint_w'):
    """Mesa redonda de patio com guarda-sol de 8 gomos listrados, bambinela, mastro e 4 cadeiras de ferro (pivo: centro, piso)."""
    p = Piece()
    p.cyl('iron', 0.28, 0.0, 0.03, 0, 0, 16); p.cyl('iron', 0.035, 0.03, 0.72, 0, 0, 10)
    p.cyl('paint_w', 0.45, 0.72, 0.75, 0, 0, 28); ring_y(p, 'iron', 0.45, 0.47, 0.715, 0.755, 0, 0, 28)
    p.cyl('chrome', 0.02, 0.75, 2.5, 0, 0, 8)
    R = 1.35; yb = 2.05; yt = 2.42
    for k in range(8):
        a0 = 2 * math.pi * k / 8; a1 = 2 * math.pi * (k + 1) / 8; m = c1 if k % 2 == 0 else c2
        pa = (R * math.cos(a0), yb, R * math.sin(a0)); pb = (R * math.cos(a1), yb, R * math.sin(a1))
        p.hull(m, [pa, pb, (0, yt, 0), (pa[0], yb + 0.015, pa[2]), (pb[0], yb + 0.015, pb[2]), (0, yt + 0.015, 0)])
        p.hull(m, [(x * s, y, z * s) for (x, y, z) in (pa, pb) for s in (0.995, 1.0)] + [(x * s, y - 0.14, z * s) for (x, y, z) in (pa, pb) for s in (0.995, 1.0)])
        seg_cyl(p, 'chrome', (0.0, 1.8, 0.0), (pa[0] * 0.55, yb + (yt - yb) * 0.44 - 0.02, pa[2] * 0.55), 0.008, 5)
    p.sphere('chrome', 0.05, 0, yt + 0.05, 0, 1)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2; c = Piece()
        for (x, z) in ((-0.2, -0.2), (0.2, -0.2), (-0.2, 0.2), (0.2, 0.2)): seg_cyl(c, 'iron', (x, 0.0, z), (x * 1.0, 0.44, z), 0.012, 6)
        c.cham(c1, -0.22, 0.22, 0.44, 0.47, -0.22, 0.22, 0.008)
        for x in (-0.2, 0.2): seg_cyl(c, 'iron', (x, 0.47, -0.2), (x, 0.88, -0.24), 0.012, 6)
        for y in (0.62, 0.84): c.cham('iron', -0.21, 0.21, y, y + 0.04, -0.245 + (y - 0.47) * -0.1, -0.225 + (y - 0.47) * -0.1, 0.004)
        p.merge(c, rot_y(math.degrees(a) + 180, (0.75 * math.sin(a), 0, 0.75 * math.cos(a))))
    return p
def flag_pole(h=7.0):
    """Mastro branco com base de concreto, polia, adricas e bandeirola triangular verde e amarela ao vento (sem simbolos)."""
    p = Piece(); p.cyl('concrete', 0.3, -0.15, 0.12, 0, 0, 20); lathe(p, 'paint_w', [(0.07, 0.12), (0.045, h)], 0, 0, 0.0, 12)
    p.sphere('flag_y', 0.08, 0, h + 0.05, 0, 1)
    seg_cyl(p, 'steel', (0.06, 0.12 + 1.2, 0.0), (0.06, h - 0.1, 0.0), 0.004, 4)
    p.box('steel', 0.045, 0.08, 1.2, 1.35, -0.03, 0.03)
    for i in range(8):
        u0, u1 = 2.2 * i / 8, 2.2 * (i + 1) / 8; w0, w1 = 0.7 * (1 - u0 / 2.2), 0.7 * (1 - u1 / 2.2)
        z0, z1 = 0.12 * math.sin(u0 * 2.4), 0.12 * math.sin(u1 * 2.4)
        for (m, a, b) in (('door', 0.0, 0.5), ('flag_y', 0.5, 1.0)):
            p.hull(m, [(0.05 + u, h - 0.12 - w * a, zz + e) for (u, w, zz) in ((u0, w0, z0), (u1, w1, z1)) for e in (-0.004, 0.004)] +
                   [(0.05 + u, h - 0.12 - w * b, zz + e) for (u, w, zz) in ((u0, w0, z0), (u1, w1, z1)) for e in (-0.004, 0.004)])
    return p
def iron_fence():
    """Gradil de ferro com lancas em volta do terreno, postes quadrados com pinhas a cada 2 m e pilares de tijolo na entrada."""
    p = Piece(); x0, x1, z0, z1 = -FX, FX, -FZ, FZ
    runs = [((x0, z0), (x1, z0)), ((x1, z0), (x1, z1)), ((x0, z1), (x0, z0)), ((x0, z1), (GATE[0] - 0.45, z1)), ((GATE[1] + 0.45, z1), (x1, z1))]
    done = set()
    for (a, b) in runs:
        a, b = np.array(a), np.array(b); Ln = np.linalg.norm(b - a); d = (b - a) / Ln; n_ = int(math.ceil(Ln / 2.0))
        for i in range(n_ + 1):
            c = a + d * Ln * i / n_; key = (round(c[0], 2), round(c[1], 2))
            if key in done: continue
            done.add(key); p.box('iron', c[0] - 0.04, c[0] + 0.04, -0.15, 1.25, c[1] - 0.04, c[1] + 0.04); p.sphere('iron', 0.055, c[0], 1.3, c[1], 1)
        for y in (0.16, 0.98):
            ra, rb_ = a + d * 0.04, b - d * 0.04
            if abs(d[0]) > 0.5: p.box('iron', min(ra[0], rb_[0]), max(ra[0], rb_[0]), y, y + 0.03, a[1] - 0.012, a[1] + 0.012)
            else: p.box('iron', a[0] - 0.012, a[0] + 0.012, y, y + 0.03, min(ra[1], rb_[1]), max(ra[1], rb_[1]))
        u = 0.12
        while u < Ln - 0.06:
            c = a + d * u
            if min(abs(u - Ln * i / n_) for i in range(n_ + 1)) > 0.07:
                p.box('iron', c[0] - 0.009, c[0] + 0.009, YL - 0.02, 1.1, c[1] - 0.009, c[1] + 0.009)
                p.hull('iron', [(c[0] + sx * 0.022, 1.1, c[1] + sz * 0.022) for sx in (-1, 1) for sz in (-1, 1)] + [(c[0], 1.2, c[1])])
            u += 0.12
    for gx in (GATE[0] - 0.3, GATE[1] + 0.3):   # pilares de tijolo com capa e bola
        a, b = (gx - 0.3, gx) if gx < 7 else (gx, gx + 0.3)
        p.box('brick', a, b, -0.15, 1.6, z1 - 0.2, z1 + 0.2); p.box('coping', a - 0.04, b + 0.04, 1.6, 1.68, z1 - 0.24, z1 + 0.24)
        p.hull('coping', [(x, 1.68, z) for x in (a - 0.02, b + 0.02) for z in (z1 - 0.22, z1 + 0.22)] + [((a + b) / 2, 1.85, z1)])
        p.sphere('ball', 0.11, (a + b) / 2, 1.96, z1, 2)
    return p

# ============================================================================ green de treino (pivo: origem)
PRACT = Polygon([(14.0 + 3.2 * math.cos(t) + 0.4 * math.cos(3 * t), -7.0 + 2.2 * math.sin(t) + 0.3 * math.sin(2 * t)) for t in np.linspace(0, 2 * math.pi, 56, endpoint=False)])
def practice():
    """Green de treino de forma livre com borda de tijolo, 3 copos com bandeirinhas e bolinhas espalhadas."""
    p = Piece(); g = PRACT; rng = np.random.default_rng(4)
    ext_y(p, 'concrete', g, -0.1, GT0); ext_y(p, 'turf', g, GT0, GT1)
    ext_y(p, 'brick', off(g, GB).difference(g), -0.1, 0.32); ext_y(p, 'coping', off(g, GB + 0.015).difference(g), 0.32, 0.35)
    for k, (x, z) in enumerate(((12.2, -7.6), (14.6, -5.8), (16.0, -7.9))):
        p.cyl('dark', 0.054, GT1, GT1 + 0.003, x, z, 20); ring_y(p, 'paint_w', 0.054, 0.066, GT1, GT1 + 0.004, x, z, 20)
        p.cyl('paint_w', 0.008, GT1 + 0.003, 1.45, x, z, 8); p.sphere('paint_w', 0.014, x, 1.46, z, 1)
        p.hull(FLAGC[k + 1], [(x + a, y, z + zz) for (a, y) in ((0.008, 1.43), (0.008, 1.2), (0.36, 1.32)) for zz in (-0.003, 0.003)])
    for k in range(9):
        a = rng.uniform(0, 2 * math.pi); r = rng.uniform(0.3, 0.8)
        p.sphere(['ball', 'flag_y', 'flag_r'][k % 3], 0.021, 14.0 + 2.6 * r * math.cos(a), GT1 + 0.021, -7.0 + 1.6 * r * math.sin(a), 1)
    return p

# ============================================================================ terreno (pivo: origem)
SITE = sbox(SX0, SZ0, SX1, SZ1)
WALKS = unary_union([sbox(6.0, -13.4, 8.5, SZ1), sbox(-18.5, 12.0, 6.0, 13.5), sbox(-18.5, 4.5, 6.0, 6.0).difference(sbox(BR0, 4.4, BR1, 6.1)),
                     sbox(-18.5, -13.4, 8.5, -12.4), sbox(8.5, 8.0, 18.5, 13.5), sbox(8.5, 0.0, 15.8, 1.0), sbox(14.2, 1.0, 15.8, 2.0)]).difference(CB).buffer(0)
PCUT = pond_poly(0.28)
SAND = sbox(-18.5, -12.0, 5.0, 11.6).difference(WALKS).difference(PCUT).buffer(0)
GRASS = SITE.difference(WALKS).difference(SAND).difference(PCUT).difference(CB).buffer(0)
def site():
    """Terreno: passeios e patio de placas de concreto, leito de saibro do campo, gramado em volta."""
    p = Piece(); p.merge(paving(WALKS, Y0, 1.5, 'concrete'))
    ext_y(p, 'sand', SAND, GY, YL); ext_y(p, 'grass', GRASS, GY, YL)
    return p

# ============================================================================ pecas
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(float(x), 3), round(float(y), 3), round(float(z), 3)], 'rotY': round(float(ry), 3), 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': e['rotY'], 'open': round(float(ry + door), 3)}; e['tags'].append('door')
    L.append(e)
def hinge(x, z, ry, lx, lz):
    r = math.radians(ry); return x + lx * math.cos(r) + lz * math.sin(r), z - lx * math.sin(r) + lz * math.cos(r)
pieces = {}
def wm(kind, tl=0.0, tr_=0.0, ea=0.0, eb=0.0):
    n = 'c_' + kind + ('_l' if tl else '') + ('_r' if tr_ else '') + ('_ea' if ea else '') + ('_eb' if eb else '')
    if n not in pieces: pieces[n] = c_mod(kind, tl, tr_, ea, eb)
    return n
pieces.update({
    'c_roof': c_roof(), 'c_floor': c_floor(), 'c_plan': c_plan(),
    **{f'hole_{k}': hole(k) for k in range(1, 6)}, 'practice': practice(), 'windmill': windmill(), 'lighthouse': lighthouse(),
    'pond': pond(), 'bridge': bridge(), 'fence': iron_fence(), 'site': site(),
    'counter': counter_k(3.0), 'register': register(), 'score_stand': score_stand(), 'putter_rack': putter_rack(), 'ball_bin': ball_bin(),
    'fridge': fridge(), 'shelves': shelves(1.6), 'bench_in': bench_in(1.6), 'plant': plant(1.3), 'trash_can': trash_can(),
    'bench': park_bench(), 'lamp_post': lamp_post(3.8), 'umbrella_r': umbrella_table('umb_r', 'paint_w'), 'umbrella_y': umbrella_table('umb_y', 'umb_o'),
    'flag_pole': flag_pole(7.0), 'palm': palm(6.2, (0.7, 0.2), 1), 'palm_b': palm(5.0, (-0.3, 0.5), 2), 'bush': bush(),
    'door_front': door_front(0.94, 2.26), 'door_back': door_back(0.94, 2.26), 'player_scale_ref': player_ref()})

# ============================================================================ montagem
y = Y0; C = ['clube']; E_ = 0.045
for x, k in ((11, 'win'), (13, 'door'), (15, 'svc'), (17, 'win')): put(wm(k, ea=E_ if x == 11 else 0.0, eb=E_ if x == 17 else 0.0), x, y, CZ1, 0, C + ['ext', 'front'])
for x, k in ((11, 'sign'), (13, 'win'), (15, 'door_b'), (17, 'plain')): put(wm(k, ea=E_ if x == 17 else 0.0, eb=E_ if x == 11 else 0.0), x, y, CZ0, 180, C + ['ext'])
for z, k in ((3, 'plain'), (5, 'win'), (7, 'plain')):
    put(wm(k, T if z == 3 else 0.0, T if z == 7 else 0.0, T if z == 3 else 0.0, T if z == 7 else 0.0), CX0, y, z, -90, C + ['ext'])
    put(wm(k, T if z == 7 else 0.0, T if z == 3 else 0.0, T if z == 7 else 0.0, T if z == 3 else 0.0), CX1, y, z, 90, C + ['ext'])
put('c_roof', 0, y, 0, 0, C + ['roof']); put('c_floor', 0, y, 0, 0, C); put('c_plan', 0, y, 0, 0, C)
hx, hz = hinge(13.0, CZ1, 0, -0.47, -T / 2); put('door_front', hx, y + 0.005, hz, 0, C, door=90)
hx, hz = hinge(15.0, CZ0, 180, -0.47, -T / 2); put('door_back', hx, y + 0.005, hz, 180, C, door=90)
put('counter', 15.6, y, CZ1 - T, 180, C); put('register', 16.4, y + 0.92, 7.42, 180, C); put('score_stand', 14.7, y + 0.92, 7.45, 180, C)
for z in (3.4, 6.6): put('putter_rack', CX0 + T, y, z, 90, C)
for x in (12.6, 13.5): put('ball_bin', x, y, CZ0 + T, 0, C)
put('shelves', 11.2, y, CZ0 + T, 0, C); put('fridge', 17.3, y, CZ0 + T, 0, C); put('bench_in', CX1 - T, y, 4.6, -90, C)
put('plant', 17.45, y, 6.5, 0, C); put('trash_can', 11.6, y, 7.45, 0, C)
# campo
G = ['campo']
put('site', 0, 0, 0, 0, G); put('fence', 0, 0, 0, 0, G); put('pond', 0, 0, 0, 0, G); put('bridge', 0, 0, 0, 0, G)
for k in range(1, 6): put(f'hole_{k}', 0, 0, 0, 0, G)
put('practice', 0, 0, 0, 0, G); put('windmill', 0, 0, 0, 0, G + ['roof']); put('lighthouse', 0, 0, 0, 0, G + ['roof'])
put('umbrella_r', 10.3, Y0, 10.5, 0, G + ['roof']); put('umbrella_y', 15.6, Y0, 10.5, 20, G + ['roof'])
put('flag_pole', 18.95, YL, 9.0, 0, G + ['roof'])
for (x, z) in ((-18.9, 13.0), (-6.0, 11.7), (2.0, 11.7), (-18.9, 5.9), (-7.0, 6.4), (3.0, 4.1), (8.9, 6.5), (8.9, -6.0), (8.9, -12.0), (-18.9, -12.9), (5.6, -11.8)):
    put('lamp_post', x, YL, z, 0, G + ['roof'])
for (x, z, r) in ((-15.5, 3.9, 0), (4.0, 3.6, 0), (9.2, -3.0, -90), (9.2, -9.0, -90), (11.0, -11.6, 0), (17.0, -3.4, 180)): put('bench', x, YL, z, r, G)
for (x, z) in ((5.6, 6.5), (9.0, 12.2), (8.9, 3.6), (-18.9, 6.6), (9.0, -12.9)): put('trash_can', x, Y0 if WALKS.contains(Point(x, z)) else YL, z, 0, G)
for (x, z) in ((9.2, 7.3), (9.2, 2.7), (18.8, 7.0), (18.8, 3.0), (18.8, 5.0), (16.8, 0.6), (9.4, 1.6)): put('bush', x, YL, z, 0, G)
for k, (x, z) in enumerate(((4.5, 0.8), (-6.2, -1.4), (4.6, -8.6), (-15.0, -7.5), (-19.0, 9.6), (18.9, 1.0), (12.0, -2.6), (17.6, -12.6), (-19.0, -4.0),
                            (-5.8, 11.4), (11.0, -13.6), (18.8, -7.0))):
    put('palm' if k % 2 == 0 else 'palm_b', x, YL, z, 0, G + ['roof'])
put('player_scale_ref', 7.2, Y0, 9.0, 0, G); put('player_scale_ref', 14.0, Y0, 4.5, 0, C)


if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'wall_thickness': T, 'walk_level': Y0, 'lawn_level': YL,
                       'clubhouse': {'x': [CX0, CX1], 'z': [CZ0, CZ1], 'wall_top': CH, 'ceiling': CCEIL},
                       'holes': [{'path': h, 'width': GW} for h in HOLES], 'green_top': GT1,
                       'windmill': list(MILL), 'lighthouse': list(LH), 'pond': list(POND), 'bridge_x': [BR0, BR1],
                       'site': {'x': [SX0, SX1], 'z': [SZ0, SZ1]}, 'fence': {'x': [-FX, FX], 'z': [-FZ, FZ], 'gate_x': list(GATE)},
                       'textures': 'PBR (albedo + normal + ORM), 2 m tiles, UV in metres / 2'},
              'placements': L}
    json.dump(layout, open(f'{OUT}/building_layout.json', 'w'), indent=1)
    sc2 = trimesh.Scene(); tot = 0
    for e in L:
        T_ = trimesh.transformations.rotation_matrix(math.radians(e['rotY']), [0, 1, 0]); T_[:3, 3] = e['pos']
        sc = pieces[e['piece']].scene(e['piece'])
        for nm, g_ in sc.geometry.items(): g2 = g_.copy(); g2.apply_transform(T_); sc2.add_geometry(g2); tot += len(g2.faces)
    sc2.export(f'{OUT}/building_assembled.glb', include_normals=True); glb_jpeg(f'{OUT}/building_assembled.glb')
    for n, p in sorted(pieces.items(), key=lambda kv: -kv[1].tris())[:10]: print(f'  {n:30s} {p.tris():6d} tri')
    print(len(pieces), 'pecas', len(L), 'posicoes', sum(1 for e in L if 'door' in e), 'portas', tot, 'triangulos no montado')
