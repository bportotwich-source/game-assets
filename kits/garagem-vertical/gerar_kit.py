"""Kit 54: garagem vertical de concreto, em ALTO DETALHE (scripts/detalhe/detalhe.py).
Edificio-garagem de 32 x 20 m com terreo e 3 lajes (a ultima descoberta), estrutura de pilares e vigas aparentes, peitoris de
concreto pre-moldado com juntas, rampas retas sobrepostas de 11 % com guarda-corpos, faixas de vagas, setas, batentes de roda,
luminarias e tubulacao de sprinkler sob as lajes, cores por pavimento nos pilares. Torre de escada e elevador com escada em U,
fachada de vidro, portas corta-fogo, portas do elevador e casa de maquinas. Entrada com cabine, cancelas, totem de ticket,
barra de altura, placa vertical com pictogramas, caixa de pagamento, carros genericos sem marca, postes no terraco, calcada,
rua e canteiros. Arte original e sem texto. Y para cima, 1 unidade = 1 m. Padrao de medidas: PADRAO_METRICAS.md.
Dependencias: trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'scripts', 'detalhe'))
from detalhe import *
import detalhe as D
from shapely.geometry import Point, LineString, Polygon, box as sbox
from shapely.ops import unary_union
from shapely import affinity
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT + '/pieces', exist_ok=True)
CAR_COLS = {'car_r': (176, 70, 58), 'car_b': (70, 96, 140), 'car_g': (88, 120, 86), 'car_y': (206, 176, 90), 'car_w': (222, 218, 206),
            'car_o': (186, 104, 56), 'car_t': (92, 146, 142), 'car_k': (48, 50, 54)}
configurar(cores=dict({'render': (222, 212, 186), 'plaster': (236, 232, 222), 'ceil': (244, 242, 236), 'concrete': (186, 182, 174),
                       'asphalt': (84, 86, 88), 'conc_s': (178, 176, 170), 'conc_d': (150, 148, 142), 'coping': (206, 202, 192), 'glass_t': (120, 160, 180), 'gravel': (170, 162, 148), 'grass': (116, 150, 78), 'dirt': (150, 128, 98),
                       'skirt': (214, 204, 182), 'skirt_g': (170, 172, 168), 'panel': (186, 150, 108), 'carpet': (150, 128, 110), 'carpet_b': (110, 124, 140),
                       'vinyl_f': (214, 206, 186), 'tile_a': (222, 224, 220), 'cab': (176, 132, 86), 'ctop': (226, 218, 196), 'enamel': (240, 238, 232),
                       'alu': (196, 200, 204), 'metal': (176, 180, 184), 'frame': (60, 62, 66), 'chrome': (210, 214, 218), 'steel': (120, 126, 132),
                       'steel_d': (56, 60, 64), 'iron': (40, 42, 44), 'galv': (164, 170, 170), 'rust': (140, 70, 40), 'trim': (110, 80, 56),
                       'wood': (176, 132, 88), 'dkwood': (110, 78, 54), 'deck': (164, 124, 84), 'pallet': (176, 140, 96), 'lattice': (232, 228, 216),
                       'lamp_glass': (255, 238, 196), 'dark': (34, 34, 36), 'rubber': (30, 30, 32), 'glass': (150, 186, 204), 'mirror': (200, 214, 220),
                       'fabric': (120, 100, 80), 'fabric2': (110, 120, 90), 'fabric3': (150, 90, 70), 'bed_w': (236, 232, 222), 'bed_b': (90, 120, 160),
                       'porcelain': (244, 244, 240), 'paper': (236, 232, 220), 'vinyl': (70, 60, 56), 'vinyl_b': (60, 80, 120), 'screen': (30, 40, 48),
                       'leaf': (86, 128, 62), 'leaf2': (108, 144, 70), 'bark': (110, 84, 60), 'plant': (70, 120, 60), 'pot': (176, 110, 80),
                       'paint_w': (238, 238, 232), 'paint_y': (232, 190, 50), 'paint_r': (196, 52, 44), 'paint_g': (52, 110, 70), 'paint_b': (50, 100, 170),
                       'food_g': (110, 160, 70), 'food_r': (200, 60, 50), 'food_y': (230, 190, 80), 'flag_r': (200, 50, 44), 'flag_b': (52, 104, 180),
                       'cloth_r': (196, 80, 70), 'cloth_y': (230, 200, 110), 'cloth_b': (100, 140, 190), 'bench_g': (40, 92, 62), 'brick': (156, 86, 64),
                       'propane': (236, 236, 230), 'brass': (190, 160, 90), 'gold': (200, 170, 90), 'cart_w': (240, 236, 226), 'flag_o': (230, 140, 50), 'neon_r': (220, 60, 50), 'vinyl_g': (80, 110, 80), 'vinyl_r': (140, 60, 50), 'dumpster': (60, 104, 76), 'player': (90, 140, 220), 'water': (150, 190, 220)}, **CAR_COLS),
           texturas={'conc_s': 'render', 'conc_d': 'render', 'coping': 'render', 'render': 'render', 'plaster': 'plaster', 'concrete': 'render', 'asphalt': 'render', 'gravel': 'render', 'grass': 'render',
                     'dirt': 'render', 'wood': 'planks', 'dkwood': 'planks', 'deck': 'planks', 'pallet': 'planks', 'panel': 'planks', 'cab': 'planks',
                     'carpet': 'render', 'carpet_b': 'render', 'bark': 'render', 'brick': 'stone'},
           out=OUT)
D.METAL.update({'metal', 'chrome', 'steel', 'steel_d', 'iron', 'galv', 'alu'} | set(CAR_COLS)); MATS = D.MATS; TEX = D.TEX
for k in CAR_COLS: MATS[k].roughnessFactor = 0.45; MATS[k].metallicFactor = 0.4

# ============================================================================ medidas
W = 2.0; T = 0.2; t_ = 0.12
Y0 = 0.15; LH = 2.85; ST = 0.25; BD = 0.4          # terreo, pe-direito, laje, viga
LV = [Y0 + k * LH for k in range(4)]               # 0,15  3,0  5,85  8,7
YL = 0.05; GY = -0.3
BX0, BX1, BZ0, BZ1 = -16.0, 16.0, -10.0, 10.0      # bloco da garagem
RX0, RX1, RZ0, RZ1 = -12.0, 12.0, -10.0, -4.0      # faixa das rampas (sobem para +X)
SPH, SPD = 1.05, 0.65                              # peitoril acima e abaixo do topo da laje
TDZ = (6.0, 6.9)                                   # porta da torre
TX0, TX1, TZ0, TZ1 = 16.2, 20.6, 3.5, 10.0         # torre de escada e elevador (externo)
TPZ = 7.4                                          # divisoria escada / elevador
TROOF = LV[3] + 3.0
SX0, SX1, SZ0, SZ1 = -25.0, 24.0, -14.0, 14.0
COLX = (BX0 + 0.27, -7.2, 0.0, 7.2, BX1 - 0.27); COLZ = (BZ0 + 0.27, -4.0, 1.0, BZ1 - 0.27)
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

# ============================================================================ laje tipo (pivo: x = z = 0, y = topo da laje)
DECK = sbox(BX0, BZ0, BX1, BZ1).difference(sbox(RX0, RZ0, RX1, RZ1))
STALL_X = [-14.4 + 2.4 * i for i in range(13)]
def spandrel_x(p, a, b, z, s, gaps=()):
    """Peitoril pre-moldado ao longo de X na borda z (s = lado de fora): painel, capa e juntas verticais."""
    for (c, d) in segs_excl(gaps, a, b):
        if d - c < 0.05: continue
        p.box('concrete', c, d, -SPD, SPH, *sorted((z, z + s * T)))
        p.box('coping', c - (0.02 if c <= BX0 - T + 1e-6 else 0.0), d + (0.02 if d >= BX1 + T - 1e-6 else 0.0), SPH, SPH + 0.06, *sorted((z - s * 0.02, z + s * (T + 0.02))))
        for x in np.arange(c + 4.0, d - 0.5, 4.0): p.box('conc_d', x - 0.012, x + 0.012, -SPD + 0.05, SPH, *sorted((z + s * T, z + s * (T + 0.004))))
        p.box('conc_d', c, d, -SPD, -SPD + 0.05, *sorted((z + s * T, z + s * (T + 0.006))))
def spandrel_z(p, a, b, x, s, gaps=(), skin=()):
    for (c, d) in segs_excl(gaps, a, b):
        if d - c < 0.05: continue
        p.box('concrete', *sorted((x, x + s * T)), -SPD, SPH, c, d)
        p.box('coping', *sorted((x - s * 0.02, x + s * (T + 0.02))), SPH, SPH + 0.06, c + (0.02 if c <= BZ0 + 1e-6 else 0.0), d - (0.02 if d >= BZ1 - 1e-6 else 0.0))
        for z in np.arange(c + 4.0, d - 0.5, 4.0):
            if not any(u - 0.05 < z < v + 0.05 for (u, v) in skin): p.box('conc_d', *sorted((x + s * T, x + s * (T + 0.004))), -SPD + 0.05, SPH, z - 0.012, z + 0.012)
        for (e, f) in segs_excl(list(skin), c, d):
            if f - e > 0.05: p.box('conc_d', *sorted((x + s * T, x + s * (T + 0.006))), -SPD, -SPD + 0.05, e, f)
def stalls(p, x0, x1, z0, z1, y=0.0):
    for x in STALL_X:
        if x0 - 0.01 <= x <= x1 + 0.01: p.box('paint_w', x - 0.05, x + 0.05, y, y + 0.003, z0, z1)
def arrow(p, x, z, d=-1, y=0.0, mat='paint_w'):
    """Seta pintada no piso apontando para d (+1 / -1 em X)."""
    p.box(mat, *sorted((x, x + d * 1.4)), y, y + 0.003, z - 0.12, z + 0.12)
    p.hull(mat, [(x + d * 1.4 + d * dd, y + h, z + zz) for (dd, zz) in ((0.0, -0.4), (0.0, 0.4), (0.7, 0.0)) for h in (0.0, 0.003)])
def deck():
    """Laje de pavimento: laje com buraco da rampa, vigas aparentes, viga de borda, mureta da rampa, peitoris com capa e juntas,
    vao da porta da torre, faixas de vagas, setas, luminarias e tubo de sprinkler por baixo."""
    p = Piece(); ext_y(p, 'conc_s', DECK, -ST, 0.0)
    for x in COLX[1:-1]: p.box('concrete', x - 0.2, x + 0.2, -ST - BD, -ST, RZ1 + 0.4, BZ1)
    for x in (BX0 + 0.27, BX1 - 0.27): p.box('concrete', x - 0.2, x + 0.2, -ST - BD, -ST, BZ0, BZ1)
    p.box('concrete', RX0, RX1, -ST - BD, -ST, RZ1, RZ1 + 0.4)
    p.box('concrete', RX0, RX1, 0.0, 1.0, RZ1, RZ1 + 0.2); p.box('coping', RX0, RX1, 1.0, 1.05, RZ1, RZ1 + 0.22)
    for (a, b) in ((BX0 - T, RX0), (RX1, BX1 + T)): spandrel_x(p, a, b, BZ0, -1)
    spandrel_x(p, BX0 - T, BX1 + T, BZ1, 1)
    spandrel_z(p, BZ0, BZ1, BX0, -1); spandrel_z(p, BZ0, BZ1, BX1, 1, [(TDZ[0] - 0.1, TDZ[1] + 0.1)], [(TZ0, TZ1)])
    # pintura
    stalls(p, -14.4, 14.4, 5.06, BZ1 - 0.1); stalls(p, -14.4, 14.4, RZ1 + 0.2, 1.28)
    p.box('paint_w', -14.45, 14.45, 0.0, 0.003, 4.95, 5.05); p.box('paint_w', -14.45, 14.45, 0.0, 0.003, 1.3, 1.4)
    for x in (-6.0, 6.0): arrow(p, x, 2.85, -1)
    # luminarias e sprinkler
    for x in np.arange(-13.2, 13.5, 3.6):
        for z in (2.85, 7.4, -1.6):
            if abs(x - 0.0) < 0.5 or abs(abs(x) - 7.2) < 0.5: continue
            p.box('alu', x - 0.65, x + 0.65, -ST - 0.06, -ST, z - 0.1, z + 0.1); p.box('lamp_glass', x - 0.6, x + 0.6, -ST - 0.075, -ST - 0.06, z - 0.07, z + 0.07)
    seg_cyl(p, 'paint_r', (BX0 + 0.4, -ST - 0.25, 3.6), (BX1 - 0.4, -ST - 0.25, 3.6), 0.04, 8)
    for x in np.arange(-14.0, 14.5, 3.0):
        p.box('galv', x - 0.01, x + 0.01, -ST - 0.25, -ST, 3.59, 3.61); seg_cyl(p, 'chrome', (x + 0.6, -ST - 0.25, 3.6), (x + 0.6, -ST - 0.36, 3.6), 0.012, 6)
    return p
def ramp():
    """Rampa reta de 24 m e 11 %: laje inclinada, mureta interna e peitoril externo inclinados, faixa central e faixas de borda
    (pivo: x = z = 0, y = topo do pavimento de baixo)."""
    p = Piece()
    def yy(x): return LH * (x - RX0) / (RX1 - RX0)
    p.hull('conc_s', [(x, yy(x) + d, z) for x in (RX0, RX1) for z in (RZ0, RZ1) for d in (0.0, -ST)])
    p.hull('concrete', [(x, yy(x) + d, z) for x in (RX0, RX1) for z in (RZ1 - 0.2, RZ1) for d in (0.0, 1.0)])
    p.hull('coping', [(x, yy(x) + d, z) for x in (RX0, RX1) for z in (RZ1 - 0.22, RZ1) for d in (1.0, 1.05)])
    p.hull('concrete', [(x, yy(x) + d, z) for x in (RX0, RX1) for z in (RZ0 - T, RZ0) for d in (-SPD, SPH)])
    p.hull('coping', [(x, yy(x) + d, z) for x in (RX0, RX1) for z in (RZ0 - T - 0.02, RZ0 + 0.02) for d in (SPH, SPH + 0.06)])
    for x in np.arange(RX0 + 4.0, RX1 - 0.5, 4.0): p.hull('conc_d', [(xx, yy(xx) + d, z) for xx in (x - 0.012, x + 0.012) for z in (RZ0 - T - 0.004, RZ0 - T) for d in (-SPD, SPH)])
    zc = (RZ0 + RZ1) / 2
    for x in np.arange(RX0 + 0.5, RX1 - 1.0, 2.0): p.hull('paint_y', [(xx, yy(xx) + d, z) for xx in (x, x + 1.0) for z in (zc - 0.06, zc + 0.06) for d in (0.0, 0.003)])
    for z in (RZ0 + 0.3, RZ1 - 0.5): p.hull('paint_w', [(xx, yy(xx) + d, zz) for xx in (RX0 + 0.1, RX1 - 0.1) for zz in (z - 0.05, z + 0.05) for d in (0.0, 0.003)])
    return p
def column():
    """Pilar de 50 x 50 cm do terreo ate a laje de cobertura, com chanfro e faixa colorida de cada pavimento."""
    p = Piece(); p.cham('concrete', -0.25, 0.25, Y0 - 0.05, LV[3] - 0.005, -0.25, 0.25, 0.02)
    for k, m in enumerate(('paint_b', 'paint_g', 'paint_y')):
        y = LV[k] + 1.3; p.box(m, -0.256, 0.256, y, y + 0.35, -0.256, 0.256)
        p.box('paint_w', -0.258, 0.258, y + 0.12, y + 0.23, -0.258, 0.258)
    return p

# ============================================================================ terreno e terreo (pivo: origem)
STREET = sbox(SX0, SZ0, -20.0, SZ1)
CURB = sbox(-20.0, SZ0, -19.8, SZ1)
APRON = sbox(-19.8, -3.2, BX0, 7.0)
PLANT = unary_union([sbox(-12.0, -13.2, -4.0, -11.4), sbox(-2.0, -13.2, 6.0, -11.4), sbox(BX0 + 0.5, 11.4, -2.0, 13.2), sbox(4.0, 11.4, 14.0, 13.2)])
WALK = sbox(-19.8, SZ0, SX1, SZ1).difference(sbox(BX0, BZ0, BX1, BZ1)).difference(sbox(BX1, TZ0, TX1, TZ1)).difference(APRON).difference(PLANT).buffer(0)
def site():
    """Laje do terreo com faixas e setas, calcada de placas, guia, rua de asfalto com faixa, rebaixo de entrada e canteiros com grama."""
    p = Piece(); ext_y(p, 'conc_s', sbox(BX0, BZ0, BX1, BZ1), GY, Y0)
    stalls(p, -14.4, 14.4, 5.06, BZ1 - 0.1, Y0); p.box('paint_w', -14.45, 14.45, Y0, Y0 + 0.003, 4.95, 5.05)
    stalls(p, RX1 + 0.1, 14.4, RZ0 + 0.3, RZ1, Y0)
    for (x, z, d) in ((-13.5, 5.6 - 2.2, 1), (6.0, 2.85, 1), (-6.0, 2.85, 1)): arrow(p, x, z, d, Y0)
    arrow(p, -13.8, 1.2, -1, Y0, 'paint_y')
    p.merge(paving(WALK, Y0, 1.5, 'concrete')); ext_y(p, 'concrete', APRON, GY, Y0)
    for q in (sbox(BX1, TZ0, TX0, TDZ[0] - 0.1), sbox(BX1, TDZ[1] + 0.1, TX0, TZ1)): ext_y(p, 'concrete', q, GY, Y0)
    ext_y(p, 'asphalt', STREET, GY, 0.0); ext_y(p, 'concrete', CURB, GY, Y0)
    for z in np.arange(SZ0 + 1.0, SZ1 - 1.0, 3.0): p.box('paint_w', -22.56, -22.44, 0.0, 0.003, z, z + 1.5)
    for q in getattr(PLANT, 'geoms', [PLANT]):
        ext_y(p, 'grass', off(q, -0.1), GY, Y0 - 0.04)
        ext_y(p, 'concrete', q.difference(off(q, -0.1)), GY, Y0 + 0.12)
    return p

# ============================================================================ torre de escada e elevador (pivo: origem)
IX0, IX1, IZ0, IZ1 = TX0 + T, TX1 - T, TZ0 + T, TZ1 - T     # miolo: 16,4..20,4 x 3,7..9,8
GLZ = (3.95, 7.15)                                           # pano de vidro da escada (face leste)
def wall_grid(p, axis, u0, u1, v0, v1, holes, ya, yb, mat='concrete', inner='plaster'):
    """Parede da torre com vaos: axis = 'x' (corre em X, espessura em Z de v0 a v1) ou 'z'. holes = (a, b, y0, y1)."""
    us = sorted(set([u0, u1] + [h for q in holes for h in q[:2]])); ys = sorted(set([ya, yb] + [h for q in holes for h in q[2:]]))
    def cell(i, j, k):
        cu = (us[i] + us[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cu < b and c < cy < d: return None
        return mat
    for m, mesh in grid_solid(us, ys, [v0, v1], cell).items():
        if axis == 'z':
            v = mesh.vertices.copy(); mesh.vertices = np.stack([v[:, 2], v[:, 1], v[:, 0]], 1); mesh.invert()
        p.add(m, mesh)
def tower():
    """Torre de concreto: paredes com vaos das portas em cada pavimento, porta da rua, janelas, pano de vidro com montantes e
    travessas, divisoria do elevador com vaos das portas, laje de cobertura, platibanda com rufo, casa de maquinas e piso do terreo."""
    p = Piece(); ytop = TROOF + 0.9
    doors = [(TDZ[0], TDZ[1], LV[k] - ST + 0.05, LV[k] + 2.1) for k in range(4)]
    wall_grid(p, 'z', TZ0, TZ1, TX0, TX0 + T, doors, Y0 - 0.05, ytop)
    wins = [(18.3, 19.9, LV[k] + 1.0, LV[k] + 2.2) for k in range(4)]
    wall_grid(p, 'x', TX0 + T, TX1, TZ0, TZ0 + T, [(16.6, 17.5, Y0, Y0 + 2.1)] + wins, Y0 - 0.05, ytop)
    wall_grid(p, 'x', TX0 + T, TX1, TZ1 - T, TZ1, [], Y0 - 0.05, ytop)
    wall_grid(p, 'z', TZ0 + T, TZ1 - T, TX1 - T, TX1, [(GLZ[0], GLZ[1], Y0 + 0.4, TROOF - 0.1)], Y0 - 0.05, ytop)
    wall_grid(p, 'x', IX0, IX1, TPZ, TPZ + 0.2, [(16.6, 17.5, LV[k], LV[k] + 2.1) for k in range(4)], Y0, TROOF - ST, 'plaster')
    # pano de vidro
    x0 = TX1 - T + 0.04; x1 = TX1 - 0.04
    p.box('glass', x0 + 0.06, x0 + 0.07, Y0 + 0.42, TROOF - 0.12, GLZ[0], GLZ[1])
    for z in np.linspace(GLZ[0], GLZ[1], 5):
        a, b = max(GLZ[0], z - 0.04), min(GLZ[1], z + 0.04); p.box('alu', x0, x1, Y0 + 0.4, TROOF - 0.1, a, b)
    for k in range(4):
        for y in (LV[k] - 0.25, LV[k] + 1.2):
            if Y0 + 0.4 < y < TROOF - 0.2: p.box('alu', x0 + 0.01, x1 - 0.01, y, y + 0.22, GLZ[0] + 0.04, GLZ[1] - 0.04)
    for k in range(4):
        x0w, x1w = 18.3, 19.9
        p.box('alu', x0w, x1w, LV[k] + 1.0, LV[k] + 1.04, TZ0 + 0.06, TZ0 + 0.14); p.box('alu', x0w, x1w, LV[k] + 2.16, LV[k] + 2.2, TZ0 + 0.06, TZ0 + 0.14)
        for x in (x0w, (x0w + x1w) / 2 - 0.02, x1w - 0.04): p.box('alu', x + (0.0 if x == x0w else 0.0), x + 0.04, LV[k] + 1.04, LV[k] + 2.16, TZ0 + 0.06, TZ0 + 0.14)
        p.box('glass', x0w + 0.04, x1w - 0.04, LV[k] + 1.04, LV[k] + 2.16, TZ0 + 0.095, TZ0 + 0.105)
        p.box('coping', x0w - 0.05, x1w + 0.05, LV[k] + 0.96, LV[k] + 1.0, TZ0 - 0.05, TZ0)
    # porta da rua: verga
    p.box('coping', 16.5, 17.6, Y0 + 2.1, Y0 + 2.22, TZ0 - 0.04, TZ0)
    # piso do terreo, cobertura, platibanda e casa de maquinas
    ext_y(p, 'conc_s', sbox(IX0, IZ0, IX1, IZ1).difference(sbox(IX0, IZ0, SA, TPZ)), GY, Y0); ext_y(p, 'conc_s', sbox(IX0, IZ0, SA, TPZ), GY, Y0 - 0.2)
    ext_y(p, 'concrete', sbox(IX0, IZ0, IX1, IZ1), TROOF - ST, TROOF)
    ext_y(p, 'dark', sbox(IX0 + 0.01, IZ0 + 0.01, IX1 - 0.01, IZ1 - 0.01), TROOF, TROOF + 0.012)
    ext_y(p, 'coping', off(sbox(TX0, TZ0, TX1, TZ1), 0.03).difference(off(sbox(TX0, TZ0, TX1, TZ1), -T - 0.03)), ytop, ytop + 0.06)
    p.cham('concrete', IX0 + 0.3, IX1 - 0.3, TROOF + 0.012, TROOF + 1.8, TPZ + 0.25, IZ1 - 0.25, 0.02)
    p.box('coping', IX0 + 0.26, IX1 - 0.26, TROOF + 1.8, TROOF + 1.86, TPZ + 0.21, IZ1 - 0.21)
    p.cham('metal', IX1 - 1.6, IX1 - 0.6, TROOF + 0.4, TROOF + 1.5, TPZ + 0.21, TPZ + 0.26, 0.01)
    for y in np.arange(TROOF + 0.5, TROOF + 1.45, 0.08): p.box('steel_d', IX1 - 1.55, IX1 - 0.65, y, y + 0.02, TPZ + 0.19, TPZ + 0.21)
    return p
NR = 9; RR = LH / 2 / NR; RUN = 0.25; FA = (IZ0, 5.45); FB = (5.65, TPZ)
SA, SB = 17.6, 19.6                                          # inicio e fim dos lances em X
def flight(p, x0, d, y0, z0, z1):
    """Lance reto de NR espelhos subindo para d (+1/-1 em X) a partir de x0, y0; degraus macicos, laje inclinada por baixo, bocel."""
    for i in range(1, NR):
        a, b = sorted((x0 + d * (i - 1) * RUN, x0 + d * i * RUN)); y = y0 + i * RR
        p.box('conc_s', a, b, y - 0.5, y, z0 + 0.003, z1 - 0.003); p.box('paint_y', *sorted((x0 + d * ((i - 1) * RUN - 0.003), x0 + d * ((i - 1) * RUN + 0.04))), y - 0.004, y + 0.002, z0 + 0.02, z1 - 0.02)
    xe = x0 + d * (NR - 1) * RUN
    p.hull('concrete', [(x, y0 + (x - x0) * d / RUN * RR + dd, z) for x in (x0 + d * 0.003, xe - d * 0.003) for z in (z0 + 0.006, z1 - 0.006) for dd in (-0.32, -0.47)])
def rail(p, x0, d, y0, z):
    xe = x0 + d * (NR - 1) * RUN
    for i in range(1, NR):
        x = x0 + d * (i - 0.5) * RUN; y = y0 + i * RR; p.box('steel_d', x - 0.012, x + 0.012, y, y + 0.92, z - 0.012, z + 0.012)
    seg_cyl(p, 'steel_d', (x0, y0 + 0.92 + RR * 0.5, z), (xe, y0 + (NR - 1) * RR + 0.92 + RR * 0.5, z), 0.022, 8)
def landing(p, y, mid=False):
    if mid: p.box('conc_s', SB, IX1 - 0.07, y - 0.2, y, IZ0, TPZ)
    else:
        p.box('conc_s', IX0, SA, y - 0.2, y, IZ0, TPZ)
        p.box('conc_s', BX1, TX0, y - 0.2, y, TDZ[0] - 0.1, TDZ[1] + 0.1); p.box('conc_s', TX0, IX0, y - 0.2, y, TDZ[0], TDZ[1])
        p.box('alu', TX0 - 0.03, IX0 + 0.03, y, y + 0.006, TDZ[0] + 0.01, TDZ[1] - 0.01)
def stair_storey():
    """Um pavimento da escada em U: patamar do piso com soleira ate a laje, lance 1, patamar intermediario, lance 2 e guarda-corpos
    (pivo: origem, y = topo do pavimento)."""
    p = Piece(); landing(p, 0.0); landing(p, LH / 2, True)
    flight(p, SA, 1, 0.0, FA[0], FA[1]); flight(p, SB, -1, LH / 2, FB[0], FB[1])
    rail(p, SA, 1, 0.0, FA[1] - 0.03); rail(p, SB, -1, LH / 2, FB[0] + 0.03)
    for z in (FA[1] - 0.03, FB[0] + 0.03): p.box('steel_d', SB + 0.02, SB + 0.05, LH / 2, LH / 2 + 1.0, z - 0.015, z + 0.015)
    p.box('steel_d', SB + 0.02, SB + 0.05, LH / 2 + 0.96, LH / 2 + 1.0, FA[1] - 0.03, FB[0] + 0.03)
    # extintor e luminaria
    p.cham('alu', IX0 + 0.3, IX0 + 1.0, LH - 0.26, LH - 0.2, 4.6, 4.8, 0.005); p.box('lamp_glass', IX0 + 0.34, IX0 + 0.96, LH - 0.275, LH - 0.26, 4.63, 4.77)
    return p
def stair_top():
    p = Piece(); landing(p, 0.0)
    p.cham('alu', IX0 + 0.3, IX0 + 1.0, TROOF - LV[3] - ST - 0.06, TROOF - LV[3] - ST, 4.6, 4.8, 0.005)
    return p
def elev_door():
    """Portas de elevador de aco escovado, 2 folhas, com batente, soleira, botoeira e indicador (pivo: centro embaixo, frente +Z)."""
    p = Piece(); w = 0.9
    for s in (-1, 1):
        a, b = sorted((0.0, s * w / 2)); p.box('steel', a + s * 0.003, b, 0.0, 2.1, -0.06, -0.03)
    for s in (-1, 1): p.box('chrome', *sorted((s * w / 2, s * (w / 2 + 0.06))), 0.0, 2.16, 0.0, 0.02)
    p.box('chrome', -w / 2 - 0.06, w / 2 + 0.06, 2.1, 2.16, 0.0, 0.02); p.box('chrome', -w / 2, w / 2, 0.0, 0.006, -0.1, 0.02)
    p.cham('chrome', -w / 2 - 0.32, -w / 2 - 0.2, 1.0, 1.3, 0.0, 0.02, 0.005)
    for y in (1.1, 1.2): disc_z(p, 'lamp_glass', 0.02, 0.02, 0.03, -w / 2 - 0.26, y, 12)
    p.box('dark', -0.15, 0.15, 2.22, 2.32, 0.0, 0.02); p.box('neon_r', -0.06, 0.06, 2.25, 2.29, 0.02, 0.024)
    return p
def blade_sign():
    """Placa vertical da garagem: caixa vermelha com 3 pictogramas de carro e seta, molduras, bracos e refletores (pivo: base)."""
    p = Piece(); y0, y1 = 3.2, 10.2
    p.cham('paint_r', -0.12, 0.12, y0, y1, 0.0, 1.2, 0.02)
    for s in (-1, 1):
        x = s * 0.12; x2 = s * 0.13
        p.box('paint_w', *sorted((x, x2)), y0 + 0.08, y0 + 0.12, 0.08, 1.12); p.box('paint_w', *sorted((x, x2)), y1 - 0.12, y1 - 0.08, 0.08, 1.12)
        for k, yc in enumerate((y1 - 1.2, y1 - 3.0, y1 - 4.8)):
            q = Piece(); picto_car(q, 'paint_w', 0.0, 0.0, 0.9, 0.0, 0.012); p.merge(q, rot_y(90 * s, (x, yc, 0.6)))
        p.hull('paint_y', [(xx, yy, zz) for xx in sorted((x, x2)) for (yy, zz) in ((y0 + 1.0, 0.45), (y0 + 1.0, 0.75), (y0 + 0.5, 0.6))])
        p.box('paint_y', *sorted((x, x2)), y0 + 1.0, y0 + 1.5, 0.54, 0.66)
    for y in (y0 + 0.6, y1 - 0.6): p.box('steel_d', -0.05, 0.05, y - 0.05, y + 0.05, -0.15, 0.0)
    for y in (y0 - 0.2,): p.cham('steel_d', -0.08, 0.08, y, y + 0.12, 0.2, 1.0, 0.01)
    return p
def booth():
    """Cabine de cobranca de 1,6 x 1,6 m: base, chapa ate o peitoril, janelas em volta com montantes, telhado com beiral e ar."""
    p = Piece(); x = 0.8; h = 2.5
    p.cham('concrete', -x - 0.1, x + 0.1, 0.0, 0.15, -x - 0.1, x + 0.1, 0.01)
    p.box('metal', -x, x, 0.15, 1.05, -x, x)
    for sx in (-1, 1):
        for sz in (-1, 1): p.box('alu', *sorted((sx * x, sx * (x - 0.06))), 1.05, h, *sorted((sz * x, sz * (x - 0.06))))
    for (a, b, c, d) in ((-x + 0.06, x - 0.06, -x + 0.025, -x + 0.035), (-x + 0.06, x - 0.06, x - 0.035, x - 0.025),
                         (-x + 0.025, -x + 0.035, -x + 0.06, x - 0.06), (x - 0.035, x - 0.025, -x + 0.06, x - 0.06)):
        p.box('glass', a, b, 1.05, h - 0.02, c, d)
    p.cham('alu', -x - 0.02, x + 0.02, 1.0, 1.06, -x - 0.12, x + 0.12, 0.004)
    p.cham('coping', -x - 0.25, x + 0.25, h, h + 0.15, -x - 0.25, x + 0.25, 0.01)
    p.cham('metal', -0.3, 0.3, h + 0.15, h + 0.5, -0.3, 0.3, 0.01)
    p.box('dark', -0.5, 0.5, 1.05, 1.08, -x + 0.04, -x + 0.3)
    return p
def barrier():
    """Cancela automatica: gabinete amarelo, braco listrado e apoio na ponta."""
    p = Piece(); p.cham('paint_y', -0.18, 0.18, 0.0, 1.05, -0.18, 0.18, 0.01); p.cham('steel_d', -0.2, 0.2, 1.05, 1.1, -0.2, 0.2, 0.01)
    L1 = 3.4
    for k in range(int(L1 / 0.4)):
        p.box('paint_r' if k % 2 else 'paint_w', -0.05, 0.05, 0.92, 1.0, 0.18 + k * 0.4, 0.18 + (k + 1) * 0.4)
    p.box('steel_d', -0.04, 0.04, 0.0, 0.88, L1 + 0.1, L1 + 0.18); p.box('steel_d', -0.06, 0.06, 0.88, 0.92, L1 + 0.05, L1 + 0.22)
    return p
def ticket_kiosk():
    """Totem de ticket / pagamento com tela, fenda, botao e cobertura (pivo: centro embaixo, frente +Z)."""
    p = Piece(); p.cham('concrete', -0.35, 0.35, 0.0, 0.12, -0.3, 0.3, 0.01)
    p.cham('steel', -0.25, 0.25, 0.12, 1.55, -0.2, 0.2, 0.02); p.cham('steel_d', -0.28, 0.28, 1.55, 1.62, -0.24, 0.26, 0.01)
    p.box('screen', -0.15, 0.15, 1.2, 1.42, 0.2, 0.206); p.box('dark', -0.08, 0.08, 1.0, 1.03, 0.2, 0.21)
    disc_z(p, 'lamp_glass', 0.035, 0.2, 0.215, 0.12, 0.92, 12); p.box('dark', -0.1, 0.1, 0.55, 0.62, 0.2, 0.21)
    return p
def height_bar(L1=4.2, h=2.2):
    """Barra de limite de altura: 2 postes e barra listrada pendurada em correntes."""
    p = Piece()
    for s in (-1, 1): p.cham('paint_y', s * L1 / 2 - 0.08, s * L1 / 2 + 0.08, Y0 - 0.05, h + 0.5, -0.08, 0.08, 0.01); p.box('steel_d', s * L1 / 2 - 0.15, s * L1 / 2 + 0.15, Y0 - 0.04, Y0 + 0.012, -0.15, 0.15)
    p.box('steel_d', -L1 / 2 - 0.08, L1 / 2 + 0.08, h + 0.5, h + 0.58, -0.08, 0.08)
    for k in range(int(L1 / 0.35)):
        x = -L1 / 2 + 0.3 + k * 0.35
        if x + 0.35 > L1 / 2 - 0.3: break
        p.box('paint_y' if k % 2 else 'dark', x, x + 0.35, h, h + 0.12, -0.05, 0.05)
    for x in (-L1 / 2 + 0.5, L1 / 2 - 0.5): seg_cyl(p, 'chrome', (x, h + 0.12, 0.0), (x, h + 0.5, 0.0), 0.008, 4)
    return p
def bollard():
    p = Piece(); p.cyl('paint_y', 0.1, Y0 - 0.1, Y0 + 0.9, 0, 0, 14); lathe(p, 'paint_y', [(0.1, Y0 + 0.9), (0.06, Y0 + 0.98), (0.0, Y0 + 1.0)], 0, 0, 0, 14)
    ring_y(p, 'dark', 0.1, 0.104, Y0 + 0.7, Y0 + 0.78, 0, 0, 14); return p
def roof_light(h=6.0):
    """Poste do terraco com base de concreto e 2 luminarias."""
    p = Piece(); p.cham('concrete', -0.3, 0.3, 0.0, 0.6, -0.3, 0.3, 0.03); p.cyl('galv', 0.07, 0.6, h, 0, 0, 12)
    for s in (-1, 1):
        seg_cyl(p, 'galv', (0.0, h - 0.2, 0.0), (s * 0.8, h - 0.1, 0.0), 0.03, 6)
        p.hull('galv', [(s * 0.7 + a, h - 0.12, b) for a in (-0.25, 0.25) for b in (-0.15, 0.15)] + [(s * 0.7 + a, h, b) for a in (-0.2, 0.2) for b in (-0.12, 0.12)])
        p.box('lamp_glass', s * 0.7 - 0.22, s * 0.7 + 0.22, h - 0.14, h - 0.12, -0.13, 0.13)
    return p
def mirror_convex():
    p = Piece(); p.box('steel_d', -0.03, 0.03, 0.0, 0.3, -0.03, 0.03); p.sphere('mirror', 0.3, 0.0, -0.1, 0.12, 2)
    return p
def ext_cabinet():
    """Abrigo de extintor e hidrante vermelho com visor (pivo: face da parede/pilar, frente +Z)."""
    p = Piece(); p.cham('paint_r', -0.35, 0.35, 0.9, 1.7, 0.0, 0.2, 0.01); p.box('glass', -0.27, 0.27, 1.0, 1.6, 0.2, 0.204)
    p.cyl('paint_r', 0.08, 1.05, 1.5, 0.0, 0.1, 12); p.box('chrome', 0.24, 0.27, 1.25, 1.35, 0.204, 0.22)
    return p
def pay_station():
    p = Piece(); p.cham('steel_d', -0.4, 0.4, 0.0, 1.9, 0.0, 0.45, 0.02); p.cham('paint_b', -0.38, 0.38, 1.6, 1.88, 0.45, 0.47, 0.01)
    q = Piece(); picto_car(q, 'paint_w', 0.0, 0.0, 0.5, 0.0, 0.01); p.merge(q, tr(0, 1.74, 0.47))
    p.box('screen', -0.2, 0.2, 1.2, 1.45, 0.45, 0.456); p.box('dark', -0.25, 0.25, 0.7, 0.75, 0.45, 0.46); p.box('chrome', -0.12, 0.12, 1.0, 1.06, 0.45, 0.47)
    return p

# ============================================================================ pecas
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(float(x), 3), round(float(y), 3), round(float(z), 3)], 'rotY': round(float(ry), 3), 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': e['rotY'], 'open': round(float(ry + door), 3)}; e['tags'].append('door')
    L.append(e)
def hinge(x, z, ry, lx, lz):
    r = math.radians(ry); return x + lx * math.cos(r) + lz * math.sin(r), z - lx * math.sin(r) + lz * math.cos(r)
CARS = {'car_sedan_r': ('car_r', 'sedan'), 'car_wagon_b': ('car_b', 'wagon'), 'car_pickup_y': ('car_y', 'pickup'), 'car_hatch_g': ('car_g', 'hatch'),
        'car_coupe_t': ('car_t', 'coupe'), 'car_sedan_w': ('car_w', 'sedan'), 'car_sedan_k': ('car_k', 'sedan'), 'car_hatch_o': ('car_o', 'hatch')}
pieces = {n: car(m, k) for n, (m, k) in CARS.items()}
pieces.update({
    'site': site(), 'deck': deck(), 'ramp': ramp(), 'column': column(), 'tower': tower(), 'stair_storey': stair_storey(), 'stair_top': stair_top(),
    'elev_door': elev_door(), 'door_metal': door_metal(0.88, 2.08), 'blade_sign': blade_sign(), 'booth': booth(), 'barrier': barrier(),
    'ticket_kiosk': ticket_kiosk(), 'height_bar': height_bar(7.9, 2.2), 'bollard': bollard(), 'roof_light': roof_light(6.0), 'street_lamp': roof_light(5.0),
    'mirror_convex': mirror_convex(), 'ext_cabinet': ext_cabinet(), 'pay_station': pay_station(), 'wheel_stop': wheel_stop(),
    'tree': tree(5.5, 1.7, 'leaf', 2), 'bush': bush(), 'trash_can': trash_can(), 'player_scale_ref': player_ref()})

# ============================================================================ montagem
G = ['garagem']; S = ['torre']; J = ['rua']
put('site', 0, 0, 0, 0, J)
for k in range(3): put('ramp', 0, LV[k], 0, 0, G + [f'floor{k}'] + (['roof'] if k == 3 else []))
for k in (1, 2, 3): put('deck', 0, LV[k], 0, 0, G + [f'floor{k}'] + (['roof'] if k == 3 else []) + (['roof'] if k == 3 else []))
for x in COLX:
    for z in COLZ: put('column', x, 0, z, 0, G)
put('tower', 0, 0, 0, 0, S + ['ext'])
for k in range(3): put('stair_storey', 0, LV[k], 0, 0, S + [f'floor{k}'])
put('stair_top', 0, LV[3], 0, 0, S + ['floor3'])
for k in range(4):
    put('elev_door', 17.05, LV[k], TPZ, 180, S)
    hx, hz = hinge(TX0, (TDZ[0] + TDZ[1]) / 2, -90, -0.44, -T / 2); put('door_metal', hx, LV[k] + 0.005, hz, -90, S, door=90)
hx, hz = hinge(17.05, TZ0, 180, -0.44, -T / 2); put('door_metal', hx, Y0 + 0.005, hz, 180, S, door=90)
put('blade_sign', BX0 - T, 0, 8.4, -90, G + ['ext'])
# carros nas vagas (centro da vaga x, fileira)
XC = [-13.2 + 2.4 * i for i in range(12)]
names = list(CARS)
park = {0: [(1, 'n'), (2, 'n'), (5, 'n'), (8, 'n'), (10, 'n')],
        1: [(0, 'n'), (3, 'n'), (4, 'n'), (7, 'n'), (11, 'n'), (1, 's'), (6, 's'), (9, 's')],
        2: [(2, 'n'), (5, 'n'), (6, 'n'), (9, 'n'), (0, 's'), (4, 's'), (10, 's')],
        3: [(1, 'n'), (4, 'n'), (8, 's'), (3, 's')]}
c = 0
for k, lst in park.items():
    for (i, row) in lst:
        if k == 0 and row == 's': continue
        z = 7.45 if row == 'n' else -1.26
        put(names[c % len(names)], XC[i], LV[k], z, 0 if row == 'n' else 180, G + [f'floor{k}'] + (['roof'] if k == 3 else [])); c += 1
    for i in range(12): put('wheel_stop', XC[i], LV[k], 9.35, 0, G + [f'floor{k}'] + (['roof'] if k == 3 else []))
    if k > 0:
        for i in range(12): put('wheel_stop', XC[i], LV[k], -3.35, 0, G + [f'floor{k}'] + (['roof'] if k == 3 else []))
put('car_sedan_w', -20.2, Y0, 3.0, 90, J)
for (x, z) in ((-3.6, 1.0), (3.6, 1.0), (-14.2, -7.2), (14.2, -7.2)): put('roof_light', x, LV[3], z, 0, G + ['floor3', 'roof'])
for (x, z, r) in ((15.48, 1.0, -90), (-15.48, 1.0, 90)):
    for k in range(4): put('ext_cabinet', x, LV[k], z, r, G + [f'floor{k}'] + (['roof'] if k == 3 else []))
for k in range(2): put('mirror_convex', RX1 + 0.3, LV[k + 1] + 2.3, RZ1 + 0.02, 0, G + [f'floor{k + 1}'])
# entrada
put('booth', -18.2, Y0, 5.95, 0, J); put('barrier', -17.6, Y0, 1.35, 0, J); put('barrier', -17.6, Y0, 0.65, 180, J)
put('ticket_kiosk', -16.9, Y0, 5.0, 180, J); put('pay_station', -16.9, Y0, -3.6, 0, J)
put('height_bar', -19.5, 0, 0.9, 90, J)
for (x, z) in ((-19.6, -3.6), (-19.6, 7.3), (-17.0, 1.0)): put('bollard', x, 0, z, 0, J)
for (x, z) in ((-8.0, -12.3), (2.0, -12.3), (-10.0, 12.3), (9.0, 12.3)): put('tree', x, Y0 - 0.04, z, 0, J + ['roof'])
for (x, z) in ((-11.0, -12.3), (-5.0, -12.3), (-1.0, -12.3), (5.0, -12.3), (-14.5, 12.3), (-5.0, 12.3), (5.5, 12.3), (12.5, 12.3)): put('bush', x, Y0 - 0.04, z, 0, J)
for (x, z) in ((-19.2, -11.0), (-19.2, 11.0), (21.5, -11.0), (21.5, 12.0)): put('street_lamp', x, Y0, z, 0, J + ['roof'])
put('trash_can', 21.2, Y0, 3.0, 0, J); put('trash_can', -19.2, Y0, -6.0, 0, J)
put('player_scale_ref', -14.0, Y0, -1.0, 0, J); put('player_scale_ref', 15.0, LV[1], 2.6, 0, G + ['floor1'])


if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'ground_floor': Y0, 'storey_height': LH, 'levels': LV, 'slab': ST, 'beam_depth': BD,
                       'garage': {'x': [BX0, BX1], 'z': [BZ0, BZ1]}, 'ramp_band': {'x': [RX0, RX1], 'z': [RZ0, RZ1], 'rises_to': '+X'},
                       'tower': {'x': [TX0, TX1], 'z': [TZ0, TZ1], 'roof': TROOF}, 'site': {'x': [SX0, SX1], 'z': [SZ0, SZ1]},
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
