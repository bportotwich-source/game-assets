"""Kit 52: ferro-velho, em ALTO DETALHE (scripts/detalhe/detalhe.py).
Patio de terra batida com cascalho e manchas de oleo, cercado por muro de chapa ondulada de 2,4 m (chapas de cores e ferrugem
diferentes, postes de tubo, arame farpado) com portao de correr de tela aberto. Escritorio de 6 x 8 m de reboco com platibanda,
placa no telhado com pictogramas de carro e chave (sem texto), janelas com grade, ar-condicionado, porta da frente e dos fundos;
dentro, balcao com caixa, prateleiras de pecas usadas, mesa, cadeiras, arquivo, bebedouro. Fileiras de carros batidos sem rodas
sobre blocos, carros com capo aberto, carros prensados empilhados, fardos de sucata, guincho com lanca e gancho, alpendre de pecas
com estantes, motores sobre paletes, pilhas de pneus, tambores, monte de sucata, poste de luz. Carros genericos sem marca.
Arte original e sem texto. Y para cima, 1 unidade = 1 m. Padrao de medidas: PADRAO_METRICAS.md.
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
CAR_COLS = {'car_r': (150, 62, 52), 'car_b': (78, 98, 130), 'car_g': (92, 116, 88), 'car_y': (196, 170, 96), 'car_w': (214, 210, 198),
            'car_o': (176, 100, 58), 'car_t': (98, 140, 136), 'car_k': (52, 54, 58), 'tow_w': (236, 234, 226)}
configurar(cores=dict({'render': (222, 212, 186), 'plaster': (238, 234, 224), 'ceil': (242, 242, 238), 'concrete': (184, 180, 172), 'coping': (210, 206, 196),
                       'block': (176, 172, 164), 'metal': (176, 180, 184), 'frame': (60, 62, 66), 'chrome': (210, 214, 218), 'steel': (120, 126, 132),
                       'steel_d': (56, 60, 64), 'iron': (40, 42, 44), 'galv': (164, 170, 170), 'sheet_a': (150, 156, 158), 'sheet_b': (124, 136, 150),
                       'sheet_c': (146, 108, 82), 'rust': (140, 70, 40), 'rust_d': (100, 52, 34), 'wood': (166, 122, 80), 'dkwood': (96, 66, 46),
                       'pallet': (176, 140, 96), 'trim': (88, 96, 92), 'door': (70, 96, 86), 'door_int': (196, 170, 130), 'lamp_glass': (255, 238, 196),
                       'neon_r': (220, 60, 50), 'flag_o': (230, 140, 50), 'flag_r': (200, 50, 44), 'paint_w': (238, 238, 232), 'paint_y': (232, 190, 50),
                       'paint_r': (196, 52, 44), 'paint_b': (50, 100, 170), 'dark': (34, 34, 36), 'rubber': (30, 30, 32), 'tire': (36, 36, 38),
                       'glass': (150, 186, 204), 'mirror': (200, 214, 220), 'vinyl': (70, 60, 56), 'vinyl_b': (60, 80, 120), 'paper': (236, 232, 220),
                       'tile_a': (204, 200, 190), 'tile_b': (150, 146, 136), 'porcelain': (244, 244, 240), 'oil': (40, 38, 34), 'water': (150, 190, 220),
                       'dirt': (150, 128, 98), 'gravel': (164, 156, 142), 'grass': (110, 146, 74), 'leaf': (86, 128, 62), 'leaf2': (108, 144, 70),
                       'bark': (110, 84, 60), 'fabric': (120, 100, 80), 'plant': (70, 120, 60), 'pot': (176, 110, 80), 'engine': (80, 84, 88),
                       'engine_r': (150, 60, 46), 'battery': (40, 40, 44), 'food_g': (110, 160, 70), 'food_r': (200, 60, 50), 'food_y': (230, 190, 80), 'basket': (176, 130, 76), 'cart_w': (240, 236, 226), 'flag_b': (52, 104, 180), 'bench_g': (40, 92, 62), 'tool_r': (196, 52, 44), 'player': (90, 140, 220)}, **CAR_COLS),
           texturas={'render': 'render', 'plaster': 'plaster', 'concrete': 'render', 'block': 'stone', 'wood': 'planks', 'dkwood': 'planks',
                     'pallet': 'planks', 'rust': 'render', 'rust_d': 'render', 'dirt': 'render', 'gravel': 'render', 'grass': 'render', 'bark': 'render',
                     'sheet_c': 'render', 'tile_a': 'plaster'},
           out=OUT)
D.METAL.update({'metal', 'chrome', 'steel', 'steel_d', 'iron', 'galv', 'sheet_a', 'sheet_b', 'engine', 'tow_w'} | set(CAR_COLS)); MATS = D.MATS; TEX = D.TEX
for k in ('rust', 'rust_d', 'sheet_c'): MATS[k].metallicFactor = 0.35; MATS[k].roughnessFactor = 0.85
for k in CAR_COLS: MATS[k].roughnessFactor = 0.7; MATS[k].metallicFactor = 0.3

# ============================================================================ medidas
W = 2.0; T = 0.25; t_ = 0.12
Y0 = 0.15                                   # piso do escritorio e calcadas
YL = 0.05                                   # terra do patio e gramado
GY = -0.2
OX0, OX1, OZ0, OZ1 = 10.0, 16.0, 3.0, 11.0   # escritorio (frente para -X)
OH = 3.6; OCEIL = 2.9; OROOF = 3.2          # platibanda, forro, laje
FX0, FX1, FZ0, FZ1, FH = -18.0, 18.0, -12.0, 12.0, 2.4   # muro de chapa
GATE = (-4.0, 2.0)                          # portao (x) no muro da frente
SX0, SX1, SZ0, SZ1 = -21.0, 21.0, -15.0, 15.0  # terreno
LX0, LX1, LZ0, LZ1 = -6.0, 8.0, -12.0, -8.0  # alpendre de pecas (encostado no muro do fundo)
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
# ============================================================================ carros genericos dos anos 70/80 (do kit 47; pivo: meio entre os eixos, chao; frente +Z)
CAR_SPEC = {
    'sedan':  dict(zf=2.42, zr=-2.42, wf=1.38, wr=-1.38, cab=(0.78, -1.5, 0.05, -1.05), top=1.38),
    'wagon':  dict(zf=2.42, zr=-2.48, wf=1.38, wr=-1.4, cab=(0.78, -2.4, 0.05, -2.3), top=1.4),
    'coupe':  dict(zf=2.35, zr=-2.3, wf=1.3, wr=-1.3, cab=(0.7, -1.7, -0.05, -0.85), top=1.3),
    'hatch':  dict(zf=1.92, zr=-1.86, wf=1.15, wr=-1.15, cab=(0.5, -1.78, -0.15, -1.55), top=1.36),
    'pickup': dict(zf=2.5, zr=-2.5, wf=1.6, wr=-1.5, cab=(0.92, -0.56, 0.3, -0.52), top=1.55, bed=-0.62)}
def car(mat='car_r', kind='sedan', tag=False, bumper='chrome', wheels=True):
    """Carro generico de linhas retas (anos 70/80, sem marca): carroceria em 2 faixas com caixas de roda, cabine de vidro com
    colunas, teto, para-choques, grade, farois retangulares, piscas, lanternas, placas lisas, frisos, macanetas, retrovisores,
    limpadores, bancos e painel por dentro, rodas com calota. tag = cartao de preco sem texto no painel e adesivo no vidro."""
    S = CAR_SPEC[kind]; zf, zr, wf, wr = S['zf'], S['zr'], S['wf'], S['wr']; cf, cr, tf, trr = S['cab']; top = S['top']
    p = Piece(); hw = 0.88; yb = 0.3; ym = 0.7; yh = 0.9; ar = 0.42
    # faixa de baixo (entre as caixas de roda)
    for (z0, z1, front) in ((wf + ar, zf, 1), (wr + ar, wf - ar, 0), (zr, wr - ar, -1)):
        if front == 1: pr = [(yb, z0), (ym, z0), (ym, z1), (0.42, z1), (0.34, z1 - 0.05)]
        elif front == -1: pr = [(yb, z1), (ym, z1), (ym, z0), (0.42, z0), (0.34, z0 + 0.05)]
        else: pr = [(yb, z0), (ym, z0), (ym, z1), (yb, z1)]
        p.hull(mat, [(x, y, z) for x in (-hw, hw) for (y, z) in pr])
    for wz in (wf, wr): p.box('rubber', -hw + 0.3, hw - 0.3, 0.32, ym, wz - ar, wz + ar)
    # faixa de cima
    bed = S.get('bed')
    zre = bed if bed is not None else zr
    up = [(ym, zf), (ym, zre), (yh - (0.0 if bed is not None else 0.16), zre), (yh, zre + (0.0 if bed is not None else 0.15)), (yh, cf), (yh - 0.04, zf - 0.15)]
    p.hull(mat, [(x, y, z) for x in (-hw, hw) for (y, z) in up])
    if bed is not None:
        p.box('dark', -hw + 0.06, hw - 0.06, ym, ym + 0.04, zr + 0.06, bed - 0.06)
        for s in (-1, 1): p.box(mat, *sorted((s * hw, s * (hw - 0.06))), ym, 1.02, zr, bed)
        p.box(mat, -hw + 0.06, hw - 0.06, ym, 1.02, bed - 0.06, bed); p.box(mat, -hw + 0.06, hw - 0.06, ym + 0.04, 1.0, zr, zr + 0.06)
        for s in (-1, 1): p.box('chrome', *sorted((s * (hw - 0.07), s * (hw + 0.005))), 1.02, 1.035, zr + 0.05, bed - 0.03)
        p.box('chrome', -0.12, 0.12, 0.88, 0.92, zr - 0.012, zr)
    # cabine de vidro, teto e colunas
    gw0, gw1 = 0.82, 0.72
    p.hull('glass', [(s * gw0, yh, z) for s in (-1, 1) for z in (cf, cr)] + [(s * gw1, top, z) for s in (-1, 1) for z in (tf, trr)])
    p.hull(mat, [(s * (gw1 + 0.015), y, z) for s in (-1, 1) for y in (top - 0.012, top + 0.04) for z in (tf - 0.03, trr + 0.03)])
    def pil(zb, zt, wb=0.1, wt=0.08):
        pts = []
        for s in (-1, 1):
            for (w, y, z, ww) in ((gw0 + 0.012, yh + 0.005, zb, wb), (gw1 + 0.012, top - 0.005, zt, wt)):
                for dz in (-ww / 2, ww / 2):
                    for dx in (0.0, 0.025): pts.append((s * (w + dx), y, z + dz))
        return pts
    for s in (-1, 1):
        for (zb, zt, wb, wt) in ((cf - 0.05, tf + 0.02, 0.08, 0.06), ((cf + cr) / 2 + 0.1, (tf + trr) / 2 + 0.05, 0.12, 0.1), (cr + 0.08, trr - 0.03, 0.18, 0.12)):
            p.hull(mat, [pt for pt in pil(zb, zt, wb, wt) if np.sign(pt[0]) == s])
    # para-choques, grade, farois e lanternas
    bm = bumper
    p.cham(bm, -hw - 0.02, hw + 0.02, 0.3, 0.46, zf - 0.03, zf + 0.12, 0.025); p.cham(bm, -hw - 0.02, hw + 0.02, 0.3, 0.46, zr - 0.12, zr + 0.03, 0.025)
    for z0 in (zf + 0.12, zr - 0.13): p.box('paint_w', -0.2, 0.2, 0.32, 0.44, z0, z0 + 0.01)
    p.box('chrome', -0.56, 0.56, 0.48, 0.69, zf, zf + 0.008); p.box('dark', -0.53, 0.53, 0.5, 0.67, zf + 0.002, zf + 0.012)
    for k in range(3): p.box('chrome', -0.53, 0.53, 0.535 + k * 0.045, 0.545 + k * 0.045, zf + 0.004, zf + 0.016)
    for s in (-1, 1):
        a, b = sorted((s * 0.58, s * 0.84)); p.box('chrome', a, b, 0.5, 0.68, zf, zf + 0.008); p.box('lamp_glass', a + 0.02 * s * s, b - 0.02, 0.53, 0.65, zf + 0.002, zf + 0.014)
        a, b = sorted((s * 0.6, s * 0.82)); p.box('flag_o', a, b, 0.465, 0.495, zf, zf + 0.01)
        a, b = sorted((s * 0.45, s * 0.84)); p.box('chrome', a, b, 0.5, 0.69, zr - 0.008, zr); p.box('neon_r', a + 0.02, b - 0.02, 0.53, 0.66, zr - 0.014, zr - 0.002)
        a, b = sorted((s * 0.62, s * 0.7)); p.box('paint_w', a, b, 0.54, 0.65, zr - 0.016, zr - 0.012)
    # frisos, emendas de porta, macanetas, retrovisores
    for s in (-1, 1):
        xa, xb = sorted((s * hw, s * (hw + 0.006)))
        for (z0, z1) in ((wr + ar + 0.04, wf - ar - 0.04), (wf + ar + 0.04, zf - 0.1), (zr + 0.1, wr - ar - 0.04)):
            if z1 - z0 > 0.05: p.box('chrome', xa + 0.001 * s * 0 , xb, 0.6, 0.625, z0, z1) if False else p.box('chrome', *sorted((s * (hw + 0.001), s * (hw + 0.007))), 0.6, 0.625, z0, z1)
        seams = [cf - 0.08, (cf + cr) / 2 + 0.1] + ([cr + 0.1] if kind in ('sedan', 'wagon') else [])
        for zz in seams:
            arch = abs(zz - wf) < ar + 0.02 or abs(zz - wr) < ar + 0.02
            if not arch: p.box('dark', *sorted((s * hw, s * (hw + 0.003))), yb + 0.06, 0.575, zz - 0.006, zz + 0.006)
            p.box('dark', *sorted((s * hw, s * (hw + 0.003))), 0.71 if arch else 0.65, yh - 0.02, zz - 0.006, zz + 0.006)
        for zz in seams[1:] + ([cr + 0.1 - 0.0] if False else []):
            p.box('chrome', *sorted((s * hw, s * (hw + 0.02))), 0.76, 0.79, zz - 0.2, zz - 0.06)
        p.cham(mat, *sorted((s * 0.8, s * 1.0)), yh + 0.02, yh + 0.13, cf - 0.18, cf - 0.08, 0.015); p.box('mirror', *sorted((s * 0.86, s * 0.99)), yh + 0.035, yh + 0.115, cf - 0.181, cf - 0.18 + 0.0)
    # limpadores, antena, escapamento
    for x in (-0.35, 0.25): seg_cyl(p, 'dark', (x, yh + 0.012, cf + 0.03), (x + 0.4, yh + 0.07, cf - 0.08), 0.008, 4)
    seg_cyl(p, 'chrome', (0.75, ym + 0.15, wf + 0.6), (0.72, 1.6, wf + 0.4), 0.004, 4)
    disc_z(p, 'steel', 0.035, zr - 0.15, zr + 0.3, 0.45, 0.25, 10)
    # bancos e painel (dentro)
    yi = yh + 0.006
    p.cham('dark', -0.74, 0.74, yi, yi + 0.1, cf - 0.5, cf - 0.22, 0.03)
    m = trimesh.creation.torus(major_radius=0.17, minor_radius=0.018, major_sections=20, minor_sections=6)
    m.apply_transform(trimesh.transformations.rotation_matrix(math.radians(-25), [1, 0, 0])); m.apply_translation([-0.4, yi + 0.18, cf - 0.62]); p.add('dark', m)
    sb = cr + 0.22 if kind == 'pickup' else (cf + cr) / 2 if kind == 'coupe' else cf - 1.1
    for s in (-1, 1): p.cham('vinyl', *sorted((s * 0.12, s * 0.68)), yi, yi + 0.32, sb - 0.12, sb, 0.04); p.cham('vinyl', *sorted((s * 0.25, s * 0.55)), yi + 0.335, top - 0.07, sb - 0.1, sb - 0.02, 0.03)
    if kind in ('sedan', 'wagon', 'hatch'):
        zb_ = cr + (0.55 if kind == 'sedan' else 0.3 if kind == 'hatch' else 0.9)
        p.cham('vinyl', -0.7, 0.7, yi, yi + 0.28, zb_ - 0.12, zb_, 0.04)
    if tag:
        p.box('paper', 0.12, 0.42, yi + 0.11, yi + 0.22, cf - 0.51, cf - 0.5); p.box('flag_r', 0.15, 0.39, yi + 0.18, yi + 0.21, cf - 0.5, cf - 0.497)
        p.box('dark', 0.17, 0.37, yi + 0.13, yi + 0.16, cf - 0.5, cf - 0.497)
    # rodas
    for wz in ((wf, wr) if wheels else ()):
        for s in (-1, 1):
            disc_x(p, 'rubber', 0.32, *sorted((s * (hw - 0.27), s * (hw - 0.04))), 0.32, wz, 28)
            disc_x(p, 'chrome', 0.19, *sorted((s * (hw - 0.05), s * (hw - 0.03))), 0.32, wz, 20)
            disc_x(p, 'steel', 0.07, *sorted((s * (hw - 0.03), s * (hw - 0.02))), 0.32, wz, 12)
            for k in range(6):
                a = k * math.pi / 3; p.box('dark', *sorted((s * (hw - 0.034), s * (hw - 0.026))), 0.32 + 0.13 * math.sin(a) - 0.015, 0.32 + 0.13 * math.sin(a) + 0.015, wz + 0.13 * math.cos(a) - 0.015, wz + 0.13 * math.cos(a) + 0.015)
    return p
def picto_car(p, mat, cx, cy, s, z0, z1):
    """Silhueta de carro de perfil no plano x-y, extrudada de z0 a z1 (s = comprimento)."""
    body = Polygon([(cx - 0.5 * s, cy - 0.12 * s), (cx + 0.5 * s, cy - 0.12 * s), (cx + 0.5 * s, cy + 0.02 * s), (cx + 0.3 * s, cy + 0.06 * s),
                    (cx + 0.16 * s, cy + 0.24 * s), (cx - 0.22 * s, cy + 0.24 * s), (cx - 0.36 * s, cy + 0.06 * s), (cx - 0.5 * s, cy + 0.03 * s)])
    win = unary_union([Polygon([(cx + 0.13 * s, cy + 0.08 * s), (cx + 0.02 * s, cy + 0.08 * s), (cx + 0.02 * s, cy + 0.2 * s), (cx + 0.1 * s, cy + 0.2 * s)]),
                       Polygon([(cx - 0.03 * s, cy + 0.08 * s), (cx - 0.3 * s, cy + 0.08 * s), (cx - 0.19 * s, cy + 0.2 * s), (cx - 0.03 * s, cy + 0.2 * s)])])
    wh = unary_union([Point(cx + x * s, cy - 0.12 * s).buffer(0.11 * s, 16) for x in (-0.3, 0.3)])
    shape = body.difference(win).difference(unary_union([Point(cx + x * s, cy - 0.12 * s).buffer(0.135 * s, 16) for x in (-0.3, 0.3)])).union(wh)
    ext(p, mat, shape.buffer(0), z0, z1)
def picto_wrench(p, mat, cx, cy, s, z0, z1):
    head = Point(cx + 0.3 * s, cy + 0.3 * s).buffer(0.2 * s, 20).difference(sbox(cx + 0.27 * s, cy + 0.27 * s, cx + 0.6 * s, cy + 0.6 * s))
    from shapely import affinity
    handle = affinity.rotate(sbox(cx - 0.06 * s, cy - 0.45 * s, cx + 0.06 * s, cy + 0.2 * s), 45, origin=(cx, cy))
    ext(p, mat, unary_union([head, handle, Point(cx - 0.3 * s, cy - 0.3 * s).buffer(0.1 * s, 16)]).buffer(0), z0, z1)

# ============================================================================ escritorio: modulos de reboco (pivo: face externa, cota do piso; dentro em -Z)
def o_core(p, holes, xa, xb, ea=0.0, eb=0.0):
    xs = sorted(set([xa, xb] + [v for h in holes for v in h[:2] if xa < v < xb]))
    ys = sorted(set([GY - Y0, 0.0, 0.45, 1.2, OH] + [v for h in holes for v in h[2:]]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if cy < 0: return 'concrete'
        if k == 0: return 'tile_a' if cy < 1.2 else 'plaster'
        return 'concrete' if cy < 0.45 else 'render'
    for m, mesh in grid_solid(xs, ys, [-T, -0.12, 0.0], cell).items(): p.add(m, mesh)
    for (a, b) in segs_excl([(a - 0.02, b + 0.02) for (a, b, c, d) in holes if c < 0.5], xa - ea, xb + eb):
        prof_x(p, 'coping', a, b, [(0.0, 0.45), (0.03, 0.45), (0.03, 0.48), (0.0, 0.5)])
def o_window(p, a, b, y0, y1):
    """Janela de correr de aluminio com grade de ferro por fora, peitoril de concreto e verga."""
    f = 0.045
    for (c, d) in ((a, a + f), (b - f, b)): p.box('frame', c, d, y0, y1, -0.16, -0.06)
    for (c, d) in ((y0, y0 + f), (y1 - f, y1)): p.box('frame', a + f, b - f, c, d, -0.16, -0.06)
    m = (a + b) / 2; p.box('frame', m - 0.02, m + 0.02, y0 + f, y1 - f, -0.13, -0.09)
    p.box('glass', a + f - 0.003, m - 0.02, y0 + f - 0.003, y1 - f + 0.003, -0.144, -0.138); p.box('glass', m + 0.02, b - f + 0.003, y0 + f - 0.003, y1 - f + 0.003, -0.084, -0.078)
    prof_x(p, 'coping', a - 0.08, b + 0.08, [(-0.06, y0 - 0.05), (0.07, y0 - 0.06), (0.07, y0 - 0.02), (-0.06, y0 + 0.004)])
    p.box('coping', a - 0.08, b + 0.08, y1, y1 + 0.12, 0.0, 0.025)
    for x in np.arange(a + 0.1, b - 0.05, 0.13): p.box('iron', x - 0.008, x + 0.008, y0 - 0.02, y1 + 0.0, 0.05, 0.066)
    for y in (y0 + 0.05, (y0 + y1) / 2, y1 - 0.05): p.box('iron', a - 0.04, b + 0.04, y - 0.012, y + 0.012, 0.042, 0.074)
    for x in (a - 0.03, b + 0.03):
        for y in (y0 + 0.05, y1 - 0.05): p.box('iron', x - 0.02, x + 0.02, y - 0.02, y + 0.02, 0.0, 0.042)
def o_door(p, lamp=True):
    for s in (-1, 1):
        a, b = sorted((s * 0.5, s * 0.45)); p.box('frame', a, b, 0.0, 2.3, -0.2, -0.04)
    p.box('frame', -0.45, 0.45, 2.25, 2.3, -0.2, -0.04)
    p.cham('steel', -0.5, 0.5, -0.02, 0.006, -T + 0.004, 0.03, 0.003)
    p.box('coping', -0.6, 0.6, 2.3, 2.42, 0.0, 0.025)
    if lamp:
        p.cham('steel_d', 0.72, 0.92, 2.3, 2.42, 0.0, 0.12, 0.006); p.box('lamp_glass', 0.74, 0.9, 2.27, 2.3, 0.02, 0.1)
def o_mod(kind='plain', tl=0.0, tr_=0.0, ea=0.0, eb=0.0):
    """plain, win (janela de correr com grade), door (porta com luminaria), door_b (porta dos fundos), ac (ar-condicionado de parede)."""
    p = Piece(); xa, xb = -W / 2 + tl, W / 2 - tr_
    if kind == 'win':
        o_core(p, [(-0.7, 0.7, 1.0, 2.2)], xa, xb, ea, eb); o_window(p, -0.7, 0.7, 1.0, 2.2)
    elif kind in ('door', 'door_b'):
        o_core(p, [(-0.5, 0.5, 0.0, 2.3)], xa, xb, ea, eb); o_door(p, True)
    else:
        o_core(p, [], xa, xb, ea, eb)
        if kind == 'ac':
            p.cham('metal', -0.4, 0.4, 1.7, 2.25, 0.0, 0.5, 0.012)
            for y in np.arange(1.76, 2.2, 0.05): p.box('steel_d', -0.36, 0.36, y, y + 0.012, 0.5, 0.505)
            for s in (-1, 1): p.hull('steel_d', [(s * 0.38, 1.7, 0.0), (s * 0.38, 1.7, 0.48), (s * 0.38, 1.38, 0.0), (s * 0.4, 1.7, 0.0), (s * 0.4, 1.7, 0.48), (s * 0.4, 1.38, 0.0)])
            p.box('dark', -0.2, 0.2, 1.66, 1.7, 0.4, 0.44); seg_cyl(p, 'dark', (0.2, 1.7, 0.42), (0.3, -Y0 + 0.08, 0.42), 0.01, 6)
    return p

# ============================================================================ escritorio: cobertura, placa, piso e rodape (pivo: origem, cota do piso)
OB = sbox(OX0, OZ0, OX1, OZ1); OI = off(OB, -T)
def o_roof():
    """Forro com luminarias, laje com manta, rufo da platibanda, placa no telhado com pictogramas (carro e chave), unidade de ar,
    buzinotes e condutores."""
    p = Piece()
    ext_y(p, 'ceil', OI, OCEIL, OCEIL + 0.03)
    for z in (5.0, 9.0):
        p.box('trim', 12.4, 13.6, OCEIL - 0.008, OCEIL, z - 0.15, z + 0.15); p.box('lamp_glass', 12.44, 13.56, OCEIL - 0.03, OCEIL - 0.008, z - 0.12, z + 0.12)
    ext_y(p, 'concrete', OI, OROOF, OROOF + 0.2); ext_y(p, 'dark', off(OI, -0.01), OROOF + 0.2, OROOF + 0.215)
    ext_y(p, 'coping', off(OB, 0.04).difference(off(OB, -T - 0.04)), OH, OH + 0.06)
    y = OROOF + 0.215
    p.cham('metal', 13.6, 14.8, y, y + 0.7, 8.0, 9.0, 0.02)
    for k in range(5): p.box('steel_d', 13.64, 14.76, y + 0.12 + k * 0.1, y + 0.13 + k * 0.1, 7.996, 8.0)
    p.cyl('steel_d', 0.32, y + 0.7, y + 0.72, 14.2, 8.5, 20)
    # placa: estrutura de cantoneira no telhado, painel branco, pictogramas
    for z in (4.6, 9.4): p.box('steel_d', 11.15, 11.25, y, OH + 3.0, z - 0.05, z + 0.05); seg_cyl(p, 'steel_d', (11.2, OH + 1.2, z), (12.8, y, z), 0.03, 6)
    p.box('steel_d', 11.25, 11.3, OH + 0.7, OH + 3.0, 4.4, 9.6)
    p.box('paint_w', 11.08, 11.15, OH + 0.75, OH + 2.95, 4.3, 9.7); p.box('paint_r', 11.07, 11.08, OH + 0.75, OH + 0.95, 4.3, 9.7)
    p.box('paint_r', 11.07, 11.08, OH + 2.75, OH + 2.95, 4.3, 9.7)
    a = Piece(); picto_car(a, 'paint_r', 0.0, 0.0, 2.2, 0.0, 0.02); p.merge(a, rot_y(-90, (11.07, OH + 1.85, 5.75)))
    b = Piece(); picto_wrench(b, 'dark', 0.0, 0.0, 1.1, 0.0, 0.02); p.merge(b, rot_y(-90, (11.07, OH + 1.85, 8.4)))
    for z in (4.9, 7.0, 9.1): p.box('steel_d', 10.6, 11.07, OH + 3.0, OH + 3.04, z - 0.03, z + 0.03); p.cham('steel_d', 10.5, 10.7, OH + 2.9, OH + 3.04, z - 0.1, z + 0.1, 0.01)
    for z in (OZ0 + 0.6, OZ1 - 0.6):
        p.box('galv', OX1, OX1 + 0.12, y - 0.04, y + 0.08, z - 0.08, z + 0.08)
        seg_cyl(p, 'galv', (OX1 + 0.08, y, z), (OX1 + 0.08, -Y0 + YL + 0.04, z), 0.05, 10)
    return p
def o_floor():
    p = Piece(); ext_y(p, 'concrete', OI, GY - Y0 + 0.02, -0.012); b = OI.bounds; step = 0.4
    for i in range(int(math.ceil((b[2] - b[0]) / step))):
        for j in range(int(math.ceil((b[3] - b[1]) / step))):
            q = sbox(b[0] + i * step, b[1] + j * step, b[0] + (i + 1) * step, b[1] + (j + 1) * step).intersection(OI)
            if q.area > 1e-6: ext_y(p, 'tile_a' if (i + j) % 2 == 0 else 'tile_b', q, -0.012, 0.0)
    return p
def o_plan():
    p = Piece(); band = OI.difference(off(OI, -0.012))
    dr = unary_union([sbox(OX0 + T - 0.1, 5.4, OX0 + T + 0.1, 6.6), sbox(OX1 - T - 0.1, 5.4, OX1 - T + 0.1, 6.6)])
    ext_y(p, 'dkwood', band.difference(dr), 0.0, 0.1); return p

# ============================================================================ muro de chapa ondulada e portao (pivo: origem, coordenadas absolutas)
SHEETS = ['sheet_a', 'sheet_b', 'sheet_c', 'sheet_a', 'sheet_c', 'sheet_b', 'galv']
def fence():
    """Muro de chapa ondulada de 2,4 m: chapas de cores diferentes e enferrujadas, ondas dos 2 lados, postes de tubo galvanizado,
    2 travessas, bracos inclinados com 3 fios de arame farpado; abertura do portao na frente."""
    p = Piece(); rng = np.random.default_rng(12); th = 0.012
    runs = [((FX0 - th, FZ1), (GATE[0], FZ1), (0, 1)), ((GATE[1], FZ1), (FX1 + th, FZ1), (0, 1)), ((FX0 - th, FZ0), (FX1 + th, FZ0), (0, -1)),
            ((FX0, FZ0), (FX0, FZ1), (-1, 0)), ((FX1, FZ0), (FX1, FZ1), (1, 0))]
    k = 0; posts = set()
    for (a, b, n) in runs:
        a, b, n = np.array(a, float), np.array(b, float), np.array(n, float); Ln = np.linalg.norm(b - a); d = (b - a) / Ln; nb = int(math.ceil(Ln / 2.4))
        def box_at(u0, u1, o0, o1, y0, y1, m):
            c0 = a + d * u0 + n * o0; c1 = a + d * u1 + n * o1
            p.box(m, min(c0[0], c1[0]), max(c0[0], c1[0]), y0, y1, min(c0[1], c1[1]), max(c0[1], c1[1]))
        for i in range(nb):
            u0, u1 = Ln * i / nb, Ln * (i + 1) / nb; m = SHEETS[k % len(SHEETS)]; k += 1
            ytop = FH - (0.06 if k % 3 == 0 else 0.0)
            box_at(u0, u1, 0.0, th, -0.1, ytop, m)
            for u in np.arange(u0 + 0.08, u1 - 0.04, 0.16):
                box_at(u - 0.025, u + 0.025, th, th + 0.016, -0.05, ytop - 0.004, m); box_at(u - 0.025, u + 0.025, -0.016, 0.0, -0.05, ytop - 0.004, m)
            if m != 'sheet_c' and rng.random() < 0.55:   # manchas de ferrugem
                for _ in range(2):
                    uu = rng.uniform(u0 + 0.2, u1 - 0.6); yy = rng.uniform(0.0, 0.6)
                    box_at(uu, uu + rng.uniform(0.25, 0.5), th + 0.016, th + 0.019, yy, yy + rng.uniform(0.2, 0.5), 'rust')
        for i in range(nb + 1):
            c = a + d * Ln * i / nb - n * 0.06; key = (round(c[0], 1), round(c[1], 1))
            if key in posts: continue
            posts.add(key); p.cyl('galv', 0.045, -0.15, FH + 0.05, c[0], c[1], 10)
            q = c + n * 0.34; seg_cyl(p, 'galv', (c[0], FH + 0.02, c[1]), (q[0], FH + 0.42, q[1]), 0.016, 6)
        for y in (0.4, 2.0):
            c0 = a + d * 0.05 - n * 0.06; c1 = b - d * 0.05 - n * 0.06; seg_cyl(p, 'galv', (c0[0], y, c0[1]), (c1[0], y, c1[1]), 0.025, 8)
        for j in range(3):
            t = 0.35 + 0.3 * j; c0 = a + d * 0.05 - n * 0.06 + n * 0.34 * t; c1 = b - d * 0.05 - n * 0.06 + n * 0.34 * t
            seg_cyl(p, 'steel', (c0[0], FH + 0.02 + 0.4 * t, c0[1]), (c1[0], FH + 0.02 + 0.4 * t, c1[1]), 0.004, 4)
    return p
def gate():
    """Portao de correr de tela soldada aberto (pivo: origem): quadro de tubo, tela em grade, travessa, rodizios, arame farpado e
    postes-guia da abertura com cadeado e corrente."""
    p = Piece(); z = FZ1 - 0.3; x0, x1 = -10.2, -4.2; h = 2.1
    for x in (x0, x1): seg_cyl(p, 'galv', (x, 0.18, z), (x, h, z), 0.03, 8)
    for y in (0.18, h / 2 + 0.1, h): seg_cyl(p, 'galv', (x0, y, z), (x1, y, z), 0.03, 8)
    for x in np.arange(x0 + 0.1, x1 - 0.05, 0.1): p.box('steel', x - 0.003, x + 0.003, 0.2, h - 0.02, z - 0.003, z + 0.003)
    for y in np.arange(0.28, h - 0.05, 0.1): p.box('steel', x0 + 0.03, x1 - 0.03, y - 0.003, y + 0.003, z - 0.009, z - 0.003)
    seg_cyl(p, 'galv', (x0 + 0.05, 0.3, z), (x1 - 0.05, h - 0.1, z), 0.018, 6)
    for x in (x0 + 0.3, x1 - 0.3):
        p.box('steel_d', x - 0.05, x + 0.05, 0.1, 0.18, z - 0.04, z + 0.04); disc_z(p, 'rubber', 0.08, z - 0.025, z + 0.025, x, 0.08 + YL, 14)
    for j in range(3): seg_cyl(p, 'steel', (x0, h + 0.1 + 0.12 * j, z), (x1, h + 0.1 + 0.12 * j, z), 0.004, 4)
    for x in (x0, x1): seg_cyl(p, 'galv', (x, h, z), (x, h + 0.36, z), 0.012, 6)
    for x in (GATE[0] - 0.06, GATE[1] + 0.06):
        p.cyl('galv', 0.06, -0.15, FH + 0.2, x, FZ1 - 0.12, 12); p.sphere('galv', 0.07, x, FH + 0.24, FZ1 - 0.12, 1)
    for k in range(7): p.box('steel', GATE[1] + 0.12, GATE[1] + 0.16, 1.0 - k * 0.05, 1.04 - k * 0.05, FZ1 - 0.14, FZ1 - 0.1)
    p.cham('paint_y', GATE[1] + 0.1, GATE[1] + 0.2, 0.62, 0.72, FZ1 - 0.15, FZ1 - 0.09, 0.006)
    return p

# ============================================================================ alpendre de pecas (pivo: origem, coordenadas absolutas)
def lean_to():
    """Alpendre de estrutura de aco encostado no muro do fundo: laje, pilares, vigas, tercas, telhado de chapa ondulada inclinado
    para tras com rufo e calha."""
    p = Piece(); yf, yb = 3.0, 2.65; z0, z1 = LZ0 + 0.15, LZ1
    ext_y(p, 'concrete', sbox(LX0, z0, LX1, z1), GY, Y0)
    xs = np.linspace(LX0 + 0.15, LX1 - 0.15, 5)
    for x in xs:
        for (z, y) in ((z1 - 0.15, yf), (z0 + 0.15, yb)):
            p.box('steel_d', x - 0.06, x + 0.06, Y0, y - 0.14, z - 0.06, z + 0.06); p.box('steel_d', x - 0.12, x + 0.12, Y0, Y0 + 0.012, z - 0.12, z + 0.12)
        p.hull('steel_d', [(x + dx, y + dy, z) for dx in (-0.04, 0.04) for (z, y) in ((z1 - 0.1, yf - 0.14), (z0 + 0.1, yb - 0.14)) for dy in (0.0, 0.12)])
    ry = lambda z: yb + (yf - yb) * (z - (z0 - 0.3)) / (z1 + 0.4 - (z0 - 0.3))
    for z in np.linspace(z0 - 0.0, z1 - 0.1, 4): p.box('steel', LX0 - 0.2, LX1 + 0.2, ry(z) - 0.14, ry(z) - 0.02, z - 0.04, z + 0.04)
    za, zb = z0 - 0.3, z1 + 0.4
    p.hull('sheet_a', [(x, ry(z) + e, z) for x in (LX0 - 0.3, LX1 + 0.3) for z in (za, zb) for e in (-0.02, 0.0)])
    for x in np.arange(LX0 - 0.2, LX1 + 0.25, 0.16): p.seg('sheet_a', (x, ry(za) + 0.008, za), (x, ry(zb) + 0.008, zb), 0.04, 0.022)
    p.box('trim', LX0 - 0.33, LX1 + 0.33, ry(zb) - 0.14, ry(zb) + 0.03, zb, zb + 0.03)
    for s in (-1, 1):
        x = LX0 - 0.3 if s < 0 else LX1 + 0.3; a, b = sorted((x, x + s * 0.03)); p.hull('trim', [(xx, ry(z) + e, z) for xx in (a, b) for z in (za, zb) for e in (-0.14, 0.03)])
    return p
def parts_rack(L1=2.4, seed=1):
    """Estante de aco de pecas usadas: alternadores, farois, rodas, baterias e caixas (pivo: centro de tras, piso; frente +Z)."""
    p = Piece(); x = L1 / 2; rng = np.random.default_rng(seed)
    for s in (-1, 1):
        for z in (0.03, 0.57): p.box('steel_d', *sorted((s * x, s * (x - 0.05))), 0.0, 2.0, z - 0.025, z + 0.025)
    for y in (0.12, 0.62, 1.12, 1.62):
        p.box('steel', -x + 0.05, x - 0.05, y, y + 0.025, 0.0, 0.6)
        xx = -x + 0.12
        while xx < x - 0.3:
            k = int(rng.integers(5)); yy = y + 0.025
            if k == 0:   # alternador
                disc_z(p, 'engine', 0.08, 0.15, 0.33, xx + 0.08, yy + 0.08, 12); disc_z(p, 'steel_d', 0.04, 0.33, 0.37, xx + 0.08, yy + 0.08, 10); xx += 0.22
            elif k == 1: # farol
                p.cham('chrome', xx, xx + 0.28, yy, yy + 0.16, 0.2, 0.32, 0.01); p.box('lamp_glass', xx + 0.02, xx + 0.26, yy + 0.02, yy + 0.14, 0.32, 0.33); xx += 0.33
            elif k == 2: # roda
                disc_z(p, 'chrome', 0.2, 0.25, 0.45, xx + 0.2, yy + 0.2, 18) if y < 1.5 else p.cham('paper', xx, xx + 0.3, yy, yy + 0.2, 0.1, 0.45, 0.006); xx += 0.44
            elif k == 3: # bateria
                p.cham('battery', xx, xx + 0.3, yy, yy + 0.2, 0.15, 0.33, 0.008); p.cyl('paint_r', 0.015, yy + 0.2, yy + 0.23, xx + 0.05, 0.2, 6); p.cyl('dark', 0.015, yy + 0.2, yy + 0.23, xx + 0.25, 0.2, 6); xx += 0.36
            else:
                w = rng.uniform(0.2, 0.35); p.cham(['paper', 'pallet', 'engine_r'][int(rng.integers(3))], xx, xx + w, yy, yy + rng.uniform(0.15, 0.3), 0.08, 0.5, 0.006); xx += w + 0.04
    return p
def tire_rack(L1=2.4):
    """Cavalete de tubo com pneus em pe (pivo: centro, piso)."""
    p = Piece(); x = L1 / 2
    for s in (-1, 1):
        for z in (-0.3, 0.3): seg_cyl(p, 'steel_d', (s * x, 0.0, z), (s * x, 1.0, z), 0.025, 8)
        seg_cyl(p, 'steel_d', (s * x, 0.15, -0.3), (s * x, 0.15, 0.3), 0.02, 6)
    for z in (-0.18, 0.18): seg_cyl(p, 'steel_d', (-x, 0.15, z), (x, 0.15, z), 0.02, 6)
    for z in (-0.3, 0.3): seg_cyl(p, 'steel_d', (-x, 1.0, z), (x, 1.0, z), 0.02, 6)
    for k in range(10):
        m = tire_mesh(); m.apply_transform(rot_y(90)); m.apply_translation([-x + 0.17 + k * 0.23, 0.48, 0.0]); p.add('tire', m)
    return p

# ============================================================================ sucata (pivo: centro, chao)
def tire_mesh(R=0.31, r=0.1):
    m = trimesh.creation.torus(major_radius=R, minor_radius=r, major_sections=18, minor_sections=6)
    return m   # deitado no plano x-y (eixo z); quem usa gira
def tire_stack(n=5):
    p = Piece()
    for k in range(n):
        m = tire_mesh(); m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])); m.apply_translation([0.02 * math.sin(k * 2.3), 0.1 + k * 0.2, 0.02 * math.cos(k * 1.7)]); p.add('tire', m)
    return p
def tire_heap(n=26, seed=3):
    """Monte de pneus jogados, deitados e em pe."""
    p = Piece(); rng = np.random.default_rng(seed); placed = []
    for k in range(n):
        for _ in range(30):
            a = rng.uniform(0, 2 * math.pi); r = rng.uniform(0, 1.6); x, z = r * math.cos(a), r * math.sin(a)
            lvl = sum(1 for (px, pz, pl) in placed if (px - x) ** 2 + (pz - z) ** 2 < 0.36)
            if lvl < 3: break
        m = tire_mesh(); tilt = rng.uniform(0.0, 0.35) if lvl else rng.uniform(0.0, 0.2)
        m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2 + tilt, [1, 0, 0])); m.apply_transform(rot_y(rng.uniform(0, 360)))
        m.apply_translation([x, 0.11 + lvl * 0.21 + 0.31 * math.sin(tilt), z]); p.add('tire', m); placed.append((x, z, lvl))
    return p
def bale(m='car_b', seed=1):
    """Fardo de carro prensado: bloco amassado de chapas coloridas e ferrugem com cintas de aco (1,6 x 0,8 x 1,0 m)."""
    p = Piece(); rng = np.random.default_rng(seed); cols = [m, 'rust', 'rust_d', 'steel', m, 'car_w', 'rust']
    p.hull('rust_d', [(sx * 0.78, y, sz * 0.48) for sx in (-1, 1) for sz in (-1, 1) for y in (0.0, 0.78)])
    cnt = [0, 0, 0, 0, 0]
    for _ in range(26):
        f = int(rng.integers(6)); c = cols[int(rng.integers(len(cols)))]; g = min(f, 4); cnt[g] += 1
        u, v = rng.uniform(-0.6, 0.6), rng.uniform(0.08, 0.7); w = rng.uniform(0.12, 0.35); h = rng.uniform(0.08, 0.22); e = 0.004 + 0.0016 * cnt[g]
        for _k in range(3):
            if min(abs(v + h - 0.78), abs(v - h)) < 0.006: h += 0.013
            if min(abs(abs(u) + w - 0.78), abs(abs(u) + w - 0.48), abs(abs(u) - w - 0.48), abs(abs(u) - w - 0.78)) < 0.006: w += 0.013
            if min(abs(abs(u * 0.6) + w * 0.8 - 0.48), abs(abs(u * 0.6) - w * 0.8 - 0.48), abs(abs(u * 0.6) + h * 0.8 - 0.48)) < 0.006: w += 0.011; h += 0.011
        di = -(0.012 + 0.005 * cnt[g])
        if f in (0, 1): s = 1 if f == 0 else -1; p.hull(c, [(u + a, v + b, s * (0.48 + dd)) for a in (-w, w) for b in (-h, h) for dd in (di, e)])
        elif f in (2, 3):
            s = 1 if f == 2 else -1; uu = u * 0.6; p.hull(c, [(s * (0.78 + dd), v + b, uu + a) for a in (-w * 0.8, w * 0.8) for b in (-h, h) for dd in (di, e)])
        else: uu = u * 0.6; v2 = min(0.7, max(0.08, v)); p.hull(c, [(u + a, 0.78 + dd, uu + b) for a in (-w, w) for b in (-h * 0.8, h * 0.8) for dd in (di, e)])
    for x in (-0.45, 0.45): p.box('steel', x - 0.02, x + 0.02, -0.005, 0.81, -0.51, 0.51)
    return p
def bale_pile():
    """Pilha de 6 fardos em piramide (3, 2, 1)."""
    p = Piece(); cols = ['car_b', 'car_r', 'car_g', 'car_y', 'car_o', 'car_t']; k = 0
    for (lvl, n) in enumerate((3, 2, 1)):
        for i in range(n):
            z = (i - (n - 1) / 2) * 1.04; p.merge(bale(cols[k], k + 1), rot_y([-4, 0, 4.5, 0, -5, 6][k], (0.04 * ((k * 3) % 3 - 1), lvl * 0.82, z) )); k += 1
    return p
def engine_pallet(seed=1):
    """Motor usado sobre palete: bloco, cabecote, carter, polias, coletor e mangueiras."""
    p = Piece()
    for x in (-0.5, 0.0, 0.5): p.box('pallet', x - 0.05, x + 0.05, 0.0, 0.08, -0.55, 0.55)
    for z in np.linspace(-0.5, 0.5, 6): p.box('pallet', -0.6, 0.6, 0.08, 0.1, z - 0.06, z + 0.06)
    c = 'engine' if seed % 2 else 'engine_r'
    p.cham(c, -0.3, 0.3, 0.22, 0.62, -0.4, 0.4, 0.02); p.cham('engine', -0.25, 0.25, 0.1, 0.22, -0.36, 0.36, 0.02)
    p.hull(c, [(sx * 0.3, 0.62, z) for sx in (-1, 1) for z in (-0.4, 0.4)] + [(sx * 0.42, 0.82, z) for sx in (-1, 1) for z in (-0.38, 0.38)])
    p.cham('steel_d', -0.4, 0.4, 0.82, 0.9, -0.36, 0.36, 0.01)
    for s in (-1, 1):
        for z in np.linspace(-0.27, 0.27, 4): disc_x(p, 'rust', 0.035, *sorted((s * 0.42, s * 0.52)), 0.72, z, 8)
        p.box('rust', *sorted((s * 0.5, s * 0.56)), 0.68, 0.76, -0.36, 0.36)
    for (y, r) in ((0.35, 0.12), (0.55, 0.08), (0.45, 0.06)): disc_z(p, 'steel_d', r, 0.4, 0.44, 0.1 * (r > 0.1) - 0.05, y, 16)
    seg_cyl(p, 'rubber', (-0.15, 0.6, 0.4), (-0.1, 0.9, 0.2), 0.025, 6)
    return p
def drum(m='paint_b'):
    p = Piece(); p.cyl(m, 0.29, 0.0, 0.88, 0, 0, 20)
    for y in (0.29, 0.59): ring_y(p, m, 0.29, 0.305, y - 0.012, y + 0.012, 0, 0, 20)
    ring_y(p, 'steel_d', 0.27, 0.295, 0.88, 0.9, 0, 0, 20); p.cyl('steel_d', 0.04, 0.88, 0.9, 0.15, 0.0, 8)
    return p
def scrap_heap(n=60, seed=8):
    """Monte de sucata: chapas, canos, aros, para-choques, portas e pedacos enferrujados."""
    p = Piece(); rng = np.random.default_rng(seed); mats = ['rust', 'rust_d', 'steel', 'sheet_a', 'car_r', 'car_b', 'car_w', 'chrome', 'rust', 'engine']
    for k in range(n):
        a = rng.uniform(0, 2 * math.pi); r = 2.2 * math.sqrt(rng.uniform(0, 1)); x, z = r * math.cos(a), r * math.sin(a) * 0.75
        hmax = 1.5 * (1 - r / 2.3); y = rng.uniform(0, max(0.05, hmax)); m = mats[int(rng.integers(len(mats)))]; t_k = int(rng.integers(4))
        if t_k == 0:
            L_ = rng.uniform(0.6, 1.6); b = rng.uniform(0, math.pi); d = np.array([math.cos(b), rng.uniform(-0.4, 0.4), math.sin(b)])
            seg_cyl(p, m, (x, y, z), (x + d[0] * L_, max(0.02, y + d[1] * L_), z + d[2] * L_), rng.uniform(0.02, 0.06), 6)
        elif t_k == 1:
            w, h = rng.uniform(0.3, 1.0), rng.uniform(0.3, 0.8); tl = rng.uniform(-0.8, 0.8); b = rng.uniform(0, math.pi)
            u = np.array([math.cos(b), 0, math.sin(b)]); v = np.array([-math.sin(b) * math.sin(tl), math.cos(tl), math.cos(b) * math.sin(tl)]); n_ = np.cross(u, v)
            c = np.array([x, y + h / 2 * abs(math.cos(tl)), z]); p.hull(m, [c + u * su * w / 2 + v * sv * h / 2 + n_ * e for su in (-1, 1) for sv in (-1, 1) for e in (0.0, 0.012)])
        elif t_k == 2:
            mm = trimesh.creation.torus(major_radius=0.22, minor_radius=0.03, major_sections=14, minor_sections=5)
            mm.apply_transform(trimesh.transformations.rotation_matrix(rng.uniform(0, math.pi), [1, 0, 0])); mm.apply_translation([x, y + 0.2, z]); p.add('chrome' if k % 2 else 'rust', mm)
        else:
            s = rng.uniform(0.15, 0.45); p.hull(m, [(x + rng.uniform(-s, s), y + rng.uniform(0, s), z + rng.uniform(-s, s)) for _ in range(8)])
    p.hull('rust_d', [(2.3 * math.cos(t), -0.05, 1.7 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 10, endpoint=False)] + [(0, 0.9, 0)])
    return p
def cinder(p, x, z, y=0.0):
    p.box('block', x - 0.2, x + 0.2, y, y + 0.3, z - 0.1, z + 0.1)
    for dx in (-0.1, 0.1):
        for zz in ((z - 0.101, z - 0.1), (z + 0.1, z + 0.101)): p.box('dark', x + dx - 0.06, x + dx + 0.06, y + 0.04, y + 0.26, *zz)
def junk(m='car_r', kind='sedan', seed=1, hood=False, flat=False):
    """Carro batido sem rodas sobre blocos de concreto, com manchas de ferrugem, para-choque torto e (hood) capo aberto mostrando o motor.
    flat = carro prensado (achatado, sem blocos), para empilhar."""
    p = Piece(); rng = np.random.default_rng(seed); S = CAR_SPEC[kind]; q = car(m, kind, False, 'steel', wheels=False)
    if flat:
        p.merge(q, np.diag([1.04, 0.5, 1.0, 1.0]) @ tr(0, -0.3, 0)); return p
    p.merge(q)
    for wz in (S['wf'], S['wr']):
        for s in (-1, 1): cinder(p, s * 0.55, wz)
    top = S['top'] + 0.04
    for _ in range(4):
        x0 = rng.uniform(-0.6, 0.3); z0 = rng.uniform(S['cab'][3] + 0.05, S['cab'][2] - 0.4); p.box('rust', x0, x0 + rng.uniform(0.15, 0.35), top, top + 0.004, z0, z0 + rng.uniform(0.15, 0.35))
    for s in (-1, 1):
        for _ in range(3):
            z0 = rng.uniform(S['zr'] + 0.3, S['zf'] - 0.8); y0 = rng.uniform(0.32, 0.55); a, b = sorted((s * 0.88, s * 0.889))
            p.box('rust', *sorted((s * 0.882, s * 0.886)), y0, y0 + rng.uniform(0.08, 0.15), z0, z0 + rng.uniform(0.2, 0.5))
    if hood:
        cf, zf = S['cab'][0], S['zf']
        hp = trimesh.creation.box(extents=[1.66, 0.025, zf - 0.15 - cf]); hp.apply_translation([0, 0, (zf - 0.15 - cf) / 2])
        hp.apply_transform(trimesh.transformations.rotation_matrix(math.radians(-62), [1, 0, 0])); hp.apply_translation([0, 0.93, cf + 0.02]); p.add(m, hp)
        seg_cyl(p, 'steel', (0.6, 0.91, cf + 0.6), (0.6, 1.5, cf + 0.35), 0.008, 4)
        p.cham('engine', -0.35, 0.35, 0.9, 1.08, cf + 0.25, zf - 0.45, 0.02); p.cyl('steel_d', 0.16, 1.08, 1.16, -0.05, (cf + zf) / 2 - 0.1, 16)
    return p
def car_stack(n=3, seed=2):
    """Pilha de n carros prensados, um pouco tortos."""
    p = Piece(); cols = ['car_g', 'car_y', 'car_r', 'car_b', 'car_t', 'car_o']; kinds = ['sedan', 'coupe', 'wagon', 'sedan']
    for k in range(n):
        q = junk(cols[(seed + k) % len(cols)], kinds[(seed + k) % len(kinds)], seed + k, flat=True)
        p.merge(q, rot_y([-5.0, 4.0, -3.5, 6.0][(seed + k) % 4], (0.05 * ((k % 3) - 1), k * 0.56, 0.08 * ((k % 2) * 2 - 1))))
    return p
def tow_truck():
    """Guincho: picape branca com faixa vermelha, giroflex no teto, lanca em A com pistao, cabo, polia e gancho, asa de reboque
    atras e caixas de ferramentas."""
    p = Piece(); p.merge(car('tow_w', 'pickup', False, 'chrome', wheels=True)); S = CAR_SPEC['pickup']; hw = 0.88
    for s in (-1, 1):
        a, b = sorted((s * (hw + 0.001), s * (hw + 0.007))); p.box('paint_r', a, b, 0.64, 0.7, S['zr'] + 0.1, S['zf'] - 0.15)
    top = S['top'] + 0.04
    p.cham('steel_d', -0.6, 0.6, top, top + 0.05, S['cab'][2] - 0.15, S['cab'][2] - 0.02, 0.01)
    for x in (-0.45, -0.15, 0.15, 0.45): p.cham('flag_o', x - 0.12, x + 0.12, top + 0.05, top + 0.14, S['cab'][2] - 0.14, S['cab'][2] - 0.03, 0.01)
    zb = S['bed']; zr = S['zr']
    for s in (-1, 1): p.cham('steel', *sorted((s * 0.52, s * 0.82)), 1.02, 1.42, zb - 1.0, zb - 0.1, 0.015)
    for s in (-1, 1): seg_cyl(p, 'paint_r', (s * 0.35, 1.05, zb - 0.3), (0.0, 2.35, zr - 0.25), 0.06, 8)
    seg_cyl(p, 'steel', (0.0, 0.78, zb - 0.5), (0.0, 1.9, zr + 0.35), 0.05, 8); seg_cyl(p, 'chrome', (0.0, 1.9, zr + 0.35), (0.0, 2.15, zr + 0.05), 0.03, 8)
    disc_x(p, 'steel_d', 0.12, -0.05, 0.05, 2.32, zr - 0.3, 16); seg_cyl(p, 'steel_d', (0.0, 2.2, zr - 0.35), (0.0, 0.9, zr - 0.4), 0.008, 4)
    p.hull('steel_d', [(x, y, zr - 0.4 + dz) for x in (-0.03, 0.03) for (y, dz) in ((0.92, 0.0), (0.8, 0.0), (0.78, -0.1), (0.85, -0.12))])
    disc_x(p, 'steel', 0.15, -0.3, 0.3, 1.0, zb - 0.55, 14)
    p.box('steel_d', -0.1, 0.1, 0.2, 0.32, zr - 1.1, zr + 0.2); p.box('steel_d', -0.85, 0.85, 0.2, 0.32, zr - 1.25, zr - 1.05)
    for s in (-1, 1): p.box('paint_y', *sorted((s * 0.6, s * 0.85)), 0.32, 0.4, zr - 1.25, zr - 1.05)
    return p
def light_pole(h=7.0):
    """Poste de madeira com 2 luminarias de braco, isoladores e fio."""
    p = Piece(); lathe(p, 'dkwood', [(0.14, -0.3), (0.11, h)], 0, 0, 0.0, 10)
    for s in (-1, 1):
        seg_cyl(p, 'galv', (0, h - 0.6, 0), (s * 1.4, h - 0.35, 0), 0.03, 8)
        p.hull('steel_d', [(s * 1.4 + dx, h - 0.35 + dy, dz) for dx in (-0.06, 0.45 * s) for dy in (-0.06, 0.06) for dz in (-0.14, 0.14)])
        p.box('lamp_glass', *sorted((s * 1.45, s * 1.8)), h - 0.43, h - 0.41, -0.1, 0.1)
    p.box('dkwood', -0.6, 0.6, h - 0.15, h - 0.05, -0.05, 0.05)
    for x in (-0.5, 0.5): p.cyl('porcelain', 0.03, h - 0.05, h + 0.05, x, 0.0, 8)
    p.cham('steel_d', -0.1, 0.1, 2.2, 2.5, 0.12, 0.2, 0.01)
    return p
def desk(w=1.5, d=0.75):
    p = Piece(); p.cham('dkwood', -w / 2, w / 2, 0.72, 0.76, -d / 2, d / 2, 0.006)
    for s in (-1, 1): p.cham('metal', *sorted((s * (w / 2 - 0.02), s * (w / 2 - 0.45))), 0.0, 0.72, -d / 2 + 0.02, d / 2 - 0.02, 0.006)
    for y in (0.08, 0.32, 0.52): p.box('chrome', w / 2 - 0.3, w / 2 - 0.16, y + 0.1, y + 0.12, d / 2 - 0.02, d / 2 - 0.0)
    p.cham('paper', -0.4, -0.1, 0.76, 0.79, -0.1, 0.12, 0.003); p.cham('dark', 0.1, 0.5, 0.76, 0.78, -0.25, 0.02, 0.003)
    p.cham('dark', 0.15, 0.45, 0.78, 1.0, -0.3, -0.25, 0.003)
    return p
def water_cooler():
    p = Piece(); p.cham('paint_w', -0.17, 0.17, 0.0, 0.95, -0.17, 0.17, 0.01)
    lathe(p, 'water', [(0.13, 0.95), (0.15, 1.05), (0.15, 1.3), (0.1, 1.38), (0.03, 1.4)], 0, 0, 0.0, 16)
    for x in (-0.06, 0.06): p.box('paint_r' if x > 0 else 'paint_b', x - 0.02, x + 0.02, 0.8, 0.86, 0.17, 0.2)
    p.box('steel_d', -0.12, 0.12, 0.6, 0.62, 0.0, 0.2)
    return p

# ============================================================================ terreno (pivo: origem)
SITE = sbox(SX0, SZ0, SX1, SZ1); YARD = sbox(FX0, FZ0, FX1, FZ1)
STOOP = sbox(8.9, 5.2, OX0, 6.8); STOOP_B = sbox(OX1, 5.2, 17.0, 6.8)
WALK = unary_union([sbox(SX0, 13.5, SX1, SZ1), sbox(GATE[0], FZ1, GATE[1], 13.5)]).buffer(0)
CUT = unary_union([OB, STOOP, STOOP_B, sbox(LX0, LZ0 + 0.15, LX1, LZ1)])
GRAV = unary_union([sbox(GATE[0], 7.0, GATE[1], FZ1), sbox(GATE[1], 3.0, OX0 - 0.6, 10.5), Point(9.5, -4.0).buffer(3.0, 24)]).intersection(YARD).difference(CUT).buffer(0)
DIRT = YARD.difference(GRAV).difference(CUT).buffer(0)
GRASS = SITE.difference(YARD).difference(WALK).buffer(0)
def site():
    """Patio de terra batida com cascalho na entrada, na frente do escritorio e debaixo do monte de sucata, manchas de oleo, poças,
    degraus de concreto nas portas do escritorio, calcada e entrada de concreto, gramado de fora."""
    p = Piece(); rng = np.random.default_rng(21)
    ext_y(p, 'dirt', DIRT, GY, YL); ext_y(p, 'gravel', GRAV, GY, YL)
    for q in (STOOP, STOOP_B): ext_y(p, 'concrete', q, GY, Y0 - 0.005)
    p.merge(paving(WALK, 0.1, 1.5, 'concrete')); ext_y(p, 'grass', GRASS, GY, YL)
    for (x, z, r) in ((-1.0, 5.0, 1.1), (3.5, 1.0, 0.8), (-8.0, -1.0, 1.3), (5.0, -6.0, 0.9), (-13.7, 4.0, 0.7), (1.5, 9.5, 0.9), (12.0, -1.0, 0.8)):
        q = Polygon([(x + r * (0.7 + 0.3 * math.sin(3 * t + x)) * math.cos(t), z + r * 0.8 * (0.7 + 0.3 * math.cos(2 * t + z)) * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 18, endpoint=False)])
        ext_y(p, 'oil', q.intersection(YARD).difference(CUT), YL, YL + 0.003)
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
    n = 'o_' + kind + ('_l' if tl else '') + ('_r' if tr_ else '') + ('_ea' if ea else '') + ('_eb' if eb else '')
    if n not in pieces: pieces[n] = o_mod(kind, tl, tr_, ea, eb)
    return n
pieces.update({
    'o_roof': o_roof(), 'o_floor': o_floor(), 'o_plan': o_plan(),
    'counter': counter_k(3.0), 'register': register(), 'shelves': shelves(1.6), 'desk': desk(), 'office_chair': office_chair('vinyl'),
    'guest_chair': guest_chair('vinyl_b'), 'file_cab': file_cab(), 'water_cooler': water_cooler(), 'plant': plant(1.2), 'trash_can': trash_can(),
    'fence': fence(), 'gate': gate(), 'lean_to': lean_to(), 'parts_rack': parts_rack(2.4, 1), 'parts_rack_b': parts_rack(2.4, 5), 'tire_rack': tire_rack(),
    'junk_sedan_r': junk('car_r', 'sedan', 1), 'junk_wagon_b': junk('car_b', 'wagon', 2, hood=True), 'junk_coupe_o': junk('car_o', 'coupe', 3),
    'junk_hatch_g': junk('car_g', 'hatch', 4, hood=True), 'junk_pickup_y': junk('car_y', 'pickup', 5), 'junk_sedan_t': junk('car_t', 'sedan', 6, hood=True),
    'car_stack_3': car_stack(3, 1), 'car_stack_2': car_stack(2, 4), 'car_ok': car('car_w', 'sedan', False, 'chrome'), 'tow_truck': tow_truck(),
    'tire_stack': tire_stack(5), 'tire_stack_b': tire_stack(3), 'tire_heap': tire_heap(), 'bale_pile': bale_pile(), 'bale': bale('car_k', 9),
    'engine_pallet': engine_pallet(1), 'engine_pallet_b': engine_pallet(2), 'drum_b': drum('paint_b'), 'drum_r': drum('rust'), 'drum_y': drum('paint_y'),
    'scrap_heap': scrap_heap(), 'light_pole': light_pole(), 'tree': tree(6.0, 2.0), 'bush': bush(), 'site': site(),
    'door_metal': door_metal(0.88, 2.24), 'player_scale_ref': player_ref()})

# ============================================================================ montagem
y = Y0; O = ['escritorio']
for z, k in ((4, 'win'), (6, 'door'), (8, 'win'), (10, 'win')):
    put(wm(k, T if z == 4 else 0.0, T if z == 10 else 0.0, T if z == 4 else 0.0, T if z == 10 else 0.0), OX0, y, z, -90, O + ['ext', 'front'])
for z, k in ((10, 'plain'), (8, 'win'), (6, 'door_b'), (4, 'ac')):
    put(wm(k, T if z == 10 else 0.0, T if z == 4 else 0.0, T if z == 10 else 0.0, T if z == 4 else 0.0), OX1, y, z, 90, O + ['ext'])
for x, k in ((11, 'win'), (13, 'plain'), (15, 'plain')): put(wm(k), x, y, OZ1, 0, O + ['ext'])
for x, k in ((11, 'plain'), (13, 'win'), (15, 'plain')): put(wm(k), x, y, OZ0, 180, O + ['ext'])
put('o_roof', 0, y, 0, 0, O + ['roof']); put('o_floor', 0, y, 0, 0, O); put('o_plan', 0, y, 0, 0, O)
hx, hz = hinge(OX0, 6.0, -90, -0.44, -T / 2); put('door_metal', hx, y + 0.005, hz, -90, O, door=90)
hx, hz = hinge(OX1, 6.0, 90, -0.44, -T / 2); put('door_metal', hx, y + 0.005, hz, 90, O, door=90)
put('counter', 13.2, y, 8.6, -90, O); put('register', 12.95, y + 0.92, 9.5, -90, O)
for z in (7.9, 9.7): put('shelves', OX1 - T, y, z, -90, O)
put('desk', 13.6, y, 3.95, 180, O); put('office_chair', 13.6, y, 4.75, 180, O); put('file_cab', OX1 - T, y, 3.9, -90, O)
put('water_cooler', OX0 + T + 0.25, y, 10.4, 0, O)
for x in (11.0, 11.7): put('guest_chair', x, y, OZ1 - T - 0.3, 180, O)
put('plant', OX0 + T + 0.3, y, 3.6, 0, O); put('trash_can', 12.4, y, 4.0, 0, O)
# patio
J = ['patio']; yl = YL
put('site', 0, 0, 0, 0, J); put('fence', 0, 0, 0, 0, J); put('gate', 0, 0, 0, 0, J); put('lean_to', 0, 0, 0, 0, J + ['roof'])
for x in (-4.6, -1.8): put('parts_rack', x, Y0, LZ0 + 0.35, 0, J)
for x in (1.4,): put('parts_rack_b', x, Y0, LZ0 + 0.35, 0, J)
put('tire_rack', 5.6, Y0, LZ0 + 0.7, 0, J)
for x in (3.4,): put('engine_pallet', x, Y0, -10.9, 0, J)
put('engine_pallet_b', 6.8, yl, -6.6, 25, J); put('engine_pallet', 4.6, yl, -6.4, -10, J)
row1 = (('junk_sedan_r', -9.0, 0), ('car_stack_3', -3.5, 180), ('junk_wagon_b', 2.0, 0), ('car_stack_2', 7.5, 180))
row2 = (('junk_coupe_o', -9.0, 180), ('junk_hatch_g', -3.5, 0), ('junk_sedan_t', 2.0, 180), ('junk_pickup_y', 7.5, 0))
for (n, z, r) in row1: put(n, -15.8, yl, z, r, J)
for (n, z, r) in row2: put(n, -11.6, yl, z, r, J)
put('junk_sedan_r', 13.6, yl, -1.8, 90, J); put('junk_wagon_b', 13.6, yl, -6.0, 75, J)
put('scrap_heap', 9.5, yl, -4.0, 0, J); put('bale_pile', -6.0, yl, -3.0, 0, J); put('bale', -6.4, yl, 0.6, 20, J)
put('tire_heap', -6.5, yl, 7.0, 0, J)
for (x, z, n) in ((-8.6, 10.6, 'tire_stack'), (-7.6, 10.9, 'tire_stack_b'), (-6.6, 10.7, 'tire_stack'), (-3.2, -6.4, 'tire_stack_b')): put(n, x, yl, z, 0, J)
put('tow_truck', 4.6, yl, 1.5, 200, J); put('car_ok', 5.6, yl, 9.2, 90, J)
for (x, z, n) in ((16.9, 9.5, 'drum_b'), (16.9, 10.2, 'drum_r'), (17.3, 1.2, 'drum_y'), (16.6, 1.4, 'drum_r'), (-17.3, -11.55, 'drum_r'), (-17.35, -10.9, 'drum_b')): put(n, x, yl, z, 0, J)
put('light_pole', 1.4, yl, -2.0, 0, J + ['roof'])
for (x, z) in ((-20.0, -13.6), (-20.0, -4.0), (-20.0, 6.0), (20.0, -13.6), (20.0, -4.0), (20.0, 6.0), (-9.0, -13.8), (8.0, -13.8)): put('tree', x, yl, z, 0, J + ['roof'])
for (x, z) in ((-12.0, 12.8), (-8.0, 12.8), (6.0, 12.8), (11.0, 12.8), (16.0, 12.8)): put('bush', x, yl, z, 0, J)
put('player_scale_ref', -1.0, yl, 6.0, 0, J); put('player_scale_ref', 11.2, y, 6.8, 0, O)


if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'wall_thickness': T, 'office_floor': Y0, 'yard_level': YL,
                       'office': {'x': [OX0, OX1], 'z': [OZ0, OZ1], 'parapet': OH, 'ceiling': OCEIL, 'front': '-X'},
                       'fence': {'x': [FX0, FX1], 'z': [FZ0, FZ1], 'height': FH, 'gate_x': list(GATE)},
                       'lean_to': {'x': [LX0, LX1], 'z': [LZ0, LZ1]}, 'site': {'x': [SX0, SX1], 'z': [SZ0, SZ1]},
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
