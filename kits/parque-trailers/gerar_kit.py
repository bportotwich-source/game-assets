"""Kit 53: parque de trailers, em ALTO DETALHE (scripts/detalhe/detalhe.py).
Seis casas-trailer de 12 x 4 m em duas fileiras dos dois lados de uma rua de asfalto, cada uma com revestimento de aluminio
canelado em duas cores, faixa de acabamento, cantoneiras, telhado arqueado com emendas, saia canelada com respiros, engate com
macaco, janelas de correr com toldos, ar-condicionado de janela, botijoes e poste de energia. Dentro: sala com sofa, poltrona,
mesa de centro e TV, cozinha com armarios, pia, fogao, coifa, geladeira e mesinha, banheiro com box, vaso e gabinete, quarto
com cama de casal, criado-mudo e comoda. Lote com varanda de madeira, escada, guarda-corpo e toldo, garagem coberta com carro,
deposito de chapa, mesa de piquenique, churrasqueira, cadeiras de praia e varal. Entrada com placa de pictogramas, caixas de
correio, cacamba, postes, lombada, cerca de ripas e arvores. Arte original e sem texto. Y para cima, 1 unidade = 1 m.
Padrao de medidas: PADRAO_METRICAS.md.
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
TR_COLS = {'tr_w': (236, 230, 212), 'tr_y': (226, 186, 84), 'tr_p': (214, 136, 140), 'tr_b': (128, 160, 196), 'tr_n': (64, 86, 124),
           'tr_o': (206, 116, 66), 'tr_g': (156, 176, 136), 'tr_c': (240, 216, 160)}
configurar(cores=dict({'render': (222, 212, 186), 'plaster': (236, 232, 222), 'ceil': (244, 242, 236), 'concrete': (186, 182, 174),
                       'asphalt': (84, 86, 88), 'gravel': (170, 162, 148), 'grass': (116, 150, 78), 'dirt': (150, 128, 98),
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
                       'propane': (236, 236, 230), 'brass': (190, 160, 90), 'gold': (200, 170, 90), 'cart_w': (240, 236, 226), 'flag_o': (230, 140, 50), 'neon_r': (220, 60, 50), 'vinyl_g': (80, 110, 80), 'vinyl_r': (140, 60, 50), 'dumpster': (60, 104, 76), 'player': (90, 140, 220), 'water': (150, 190, 220)}, **CAR_COLS, **TR_COLS),
           texturas={'render': 'render', 'plaster': 'plaster', 'concrete': 'render', 'asphalt': 'render', 'gravel': 'render', 'grass': 'render',
                     'dirt': 'render', 'wood': 'planks', 'dkwood': 'planks', 'deck': 'planks', 'pallet': 'planks', 'panel': 'planks', 'cab': 'planks',
                     'carpet': 'render', 'carpet_b': 'render', 'bark': 'render', 'brick': 'stone'},
           out=OUT)
D.METAL.update({'metal', 'chrome', 'steel', 'steel_d', 'iron', 'galv', 'alu'} | set(CAR_COLS)); MATS = D.MATS; TEX = D.TEX
for k in list(TR_COLS) + ['skirt', 'skirt_g']: MATS[k].metallicFactor = 0.25; MATS[k].roughnessFactor = 0.5
for k in CAR_COLS: MATS[k].roughnessFactor = 0.45; MATS[k].metallicFactor = 0.4

# ============================================================================ medidas
W = 2.0; T = 0.1; t_ = 0.08
FL = 0.8                                    # piso dos trailers
WH = 2.35                                   # topo das paredes acima do piso
CH = 2.28                                   # forro acima do piso
YL = 0.05; YG = 0.07; YA = 0.09; GY = -0.2  # gramado, cascalho, asfalto
HX, HZ = 6.0, 2.0                           # meio comprimento e meia largura do trailer
SX0, SX1, SZ0, SZ1 = -22.0, 22.0, -16.0, 16.0
LANE = (-2.5, 2.5)
# lotes: (x, z, rotY, revestimento, faixa, saia)
LOTS = [(-10.0, -10.0, 0, 'tr_w', 'tr_y', 'skirt'), (-10.0, -1.0, 0, 'tr_b', 'tr_n', 'skirt_g'), (-10.0, 8.0, 0, 'tr_w', 'tr_p', 'skirt'),
        (10.0, -8.0, 180, 'tr_w', 'tr_o', 'skirt'), (10.0, 1.0, 180, 'tr_g', 'tr_w', 'skirt_g'), (10.0, 10.0, 180, 'tr_c', 'tr_b', 'skirt')]
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

# ============================================================================ trailer: paredes (local: comprimento em X, porta em +Z, engate em -X)
# furos por parede, em coordenadas locais da parede (x ao longo, y absoluto): (a, b, y0, y1, tipo)
HOLES = {
    'front': [(-2.85, -1.95, FL, FL + 2.1, 'door'), (-5.2, -3.8, FL + 0.95, FL + 2.0, 'win'), (-0.6, 0.5, FL + 1.1, FL + 2.0, 'win'),
              (4.2, 5.4, FL + 0.95, FL + 2.0, 'win')],
    'back': [(3.2, 4.6, FL + 0.95, FL + 2.0, 'win'), (-0.6, 0.4, FL + 1.25, FL + 2.0, 'win'), (-2.8, -2.2, FL + 1.55, FL + 2.0, 'win'),
             (-5.4, -4.2, FL + 0.95, FL + 2.0, 'win')],
    'east': [(-1.35, -0.65, FL + 1.3, FL + 1.75, 'ac')],
    'west': [],
}
AWN = {'front': [(-5.2, -3.8), (4.2, 5.4)], 'back': [(-5.4, -4.2)]}
YB = FL - 0.15; YT = FL + WH
def rib_ys():
    return [y for y in (FL - 0.06 + 0.19 * k for k in range(13)) if y + 0.025 < YT - 0.04 and not (FL + 0.84 < y + 0.025 and y < FL + 0.97)]
def t_wall(p, xa, xb, holes, main, band):
    """Parede de trailer (outer z = 0, inner z = -T): painel de madeira por dentro, chapa pintada em 2 cores por fora com cordoes de
    aluminio canelado, faixa de acabamento, molduras de janela e porta."""
    xs = sorted(set([xa, xb] + [v for h in holes for v in h[:2]]))
    ys = sorted(set([YB, FL + 0.9, YT] + [v for h in holes for v in h[2:4]]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d, _) in holes:
            if a < cx < b and c < cy < d: return None
        if k == 0: return 'panel'
        return band if cy < FL + 0.9 else main
    for m, mesh in grid_solid(xs, ys, [-T, -T + 0.012, 0.0], cell).items(): p.add(m, mesh)
    for y in rib_ys():
        gaps = [(a - 0.03, b + 0.03) for (a, b, c, d, _) in holes if y + 0.025 > c - 0.06 and y < d + 0.06]
        for (a, b) in segs_excl(gaps, xa, xb):
            if b - a > 0.02: p.box(band if y < FL + 0.9 else main, a, b, y, y + 0.025, 0.0, 0.012)
    for (a, b) in segs_excl([(a - 0.03, b + 0.03) for (a, b, c, d, _) in holes if c < FL + 0.93 and d > FL + 0.87], xa, xb):
        p.box('alu', a, b, FL + 0.87, FL + 0.93, -0.008, 0.017)
    for (a, b, y0, y1, k) in holes:
        # moldura externa de aluminio (1 cm para dentro do vao)
        tw = 0.06
        for (c, d) in ((a - tw, a + 0.01), (b - 0.01, b + tw)): p.box('alu', c, d, y0 if k == 'door' else y0 - tw, y1 + tw, -0.01, 0.02)
        p.box('alu', a + 0.01, b - 0.01, y1 - 0.01, y1 + tw, -0.01, 0.02)
        if k != 'door': p.box('alu', a + 0.01, b - 0.01, y0 - tw, y0 + 0.01, -0.01, 0.026)
        # guarnicao interna
        for (c, d) in ((a - 0.07, a), (b, b + 0.07)): p.box('trim', c, d, y0 if k == 'door' else y0 - 0.07, y1 + 0.07, -T - 0.015, -T)
        p.box('trim', a, b, y1, y1 + 0.07, -T - 0.015, -T)
        if k == 'win':
            f = 0.04; m = (a + b) / 2
            for (c, d) in ((a, a + f), (b - f, b)): p.box('alu', c, d, y0, y1, -0.07, -0.02)
            for (c, d) in ((y0, y0 + f), (y1 - f, y1)): p.box('alu', a + f, b - f, c, d, -0.07, -0.02)
            p.box('alu', m - 0.018, m + 0.018, y0 + f, y1 - f, -0.06, -0.03)
            p.box('glass', a + f - 0.004, m - 0.018, y0 + f - 0.004, y1 - f + 0.004, -0.056, -0.052)
            p.box('glass', m + 0.018, b - f + 0.004, y0 + f - 0.004, y1 - f + 0.004, -0.04, -0.036)
            p.box('trim', a - 0.09, b + 0.09, y0 - 0.03, y0 + 0.004, -T - 0.035, -T - 0.001)
            p.box('trim', a, b, y0 - 0.07, y0 - 0.03, -T - 0.015, -T)
        if k == 'door':
            p.box('alu', a + 0.01, b - 0.01, FL - 0.012, FL + 0.004, -T - 0.01, 0.03)
        if k == 'ac':
            p.cham('alu', a - 0.02, b + 0.02, y0 - 0.02, y1 + 0.02, -0.16, 0.42, 0.01)
            for x in np.arange(a + 0.05, b - 0.03, 0.04): p.box('steel_d', x - 0.008, x + 0.008, y0 + 0.05, y1 - 0.05, 0.42, 0.426)
            for y in np.arange(y0 + 0.06, y1 - 0.04, 0.05): p.box('steel_d', a + 0.03, b - 0.03, y - 0.006, y + 0.006, -0.172, -0.16)
            for x in (a + 0.04, b - 0.04): p.hull('steel_d', [(x + dx, yy, zz) for dx in (-0.012, 0.012) for (yy, zz) in ((y0 - 0.02, 0.025), (y0 - 0.02, 0.36), (y0 - 0.3, 0.025))])
def awning(p, a, b, y1, mat):
    """Toldo de chapa canelada sobre a janela, com abas laterais e bracos."""
    y0 = y1 + 0.12; d = 0.5; a -= 0.12; b += 0.12
    p.hull(mat, [(x, yy, zz) for x in (a, b) for (yy, zz) in ((y0 + 0.28, 0.03), (y0 + 0.3, 0.03), (y0 + 0.02, d), (y0, d))])
    for x in np.arange(a + 0.08, b - 0.04, 0.12): p.hull(mat, [(x + dx, yy + 0.015, zz) for dx in (-0.02, 0.02) for (yy, zz) in ((y0 + 0.3, 0.035), (y0 + 0.02, d - 0.005))])
    for x in (a, b):
        p.hull(mat, [(x + dx, yy, zz) for dx in (-0.008, 0.008) for (yy, zz) in ((y0 + 0.28, 0.03), (y0 + 0.02, d), (y0 - 0.16, 0.03))])
        seg_cyl(p, 'alu', (x + 0.03 * (1 if x == a else -1), y0 - 0.12, 0.03), (x + 0.03 * (1 if x == a else -1), y0 + 0.01, d - 0.05), 0.008, 6)
def wall_at(p, side, main, band, awn):
    q = Piece()
    xa, xb = (-HX, HX) if side in ('front', 'back') else (-HZ + T, HZ - T)
    t_wall(q, xa, xb, HOLES[side], main, band)
    for (a, b) in AWN.get(side, []):
        if awn: awning(q, a, b, FL + 2.0, band)
    M = {'front': rot_y(0, (0, 0, HZ)), 'back': rot_y(180, (0, 0, -HZ)), 'east': rot_y(90, (HX, 0, 0)), 'west': rot_y(-90, (-HX, 0, 0))}[side]
    p.merge(q, M)

# ============================================================================ trailer: casca (pivo: centro, chao)
def roof_y(z): return YT + 0.06 + 0.16 * (1 - (z / (HZ + 0.06)) ** 2)
def trailer(main='tr_w', band='tr_y', skirt='skirt', awn=True):
    """Casca do trailer: 4 paredes, cantoneiras, telhado arqueado com emendas e calhas de borda, respiros, saia canelada com
    grelhas e portinhola, engate com macaco, luminaria da porta, medidor de luz e portinhola do aquecedor."""
    p = Piece()
    for side in ('front', 'back', 'east', 'west'): wall_at(p, side, main, band, awn)
    for sx in (-1, 1):
        for sz in (-1, 1): p.box('alu', *sorted((sx * (HX - 0.07), sx * (HX + 0.03))), YB + 0.003, YT - 0.003, *sorted((sz * (HZ - 0.13), sz * (HZ + 0.03))))
    # saia
    for (side, M) in (('f', rot_y(0, (0, 0, HZ - 0.04))), ('b', rot_y(180, (0, 0, -HZ + 0.04))), ('e', rot_y(90, (HX - 0.04, 0, 0))), ('w', rot_y(-90, (-HX + 0.04, 0, 0)))):
        q = Piece(); L1 = (HX - 0.04) if side in 'fb' else (HZ - 0.04 - 0.02)
        q.box(skirt, -L1, L1, 0.0, YB - 0.003, -0.02, 0.0)
        for x in np.arange(-L1 + 0.08, L1 - 0.05, 0.16): q.box(skirt, x - 0.025, x + 0.025, 0.0, YB - 0.06, 0.0, 0.014)
        q.box(skirt, -L1, L1, YB - 0.06, YB - 0.003, 0.0, 0.024)
        vents = (-3.5, 0.5, 3.8) if side in 'fb' else (0.0,)
        for x in vents:
            q.box('steel_d', x - 0.22, x + 0.22, 0.18, 0.4, 0.014, 0.022)
            for y in np.arange(0.2, 0.39, 0.035): q.box(skirt, x - 0.2, x + 0.2, y, y + 0.012, 0.022, 0.03)
        if side == 'b':
            q.box('steel_d', 1.6, 2.3, 0.1, 0.52, 0.024, 0.03); q.box('chrome', 2.15, 2.22, 0.3, 0.34, 0.03, 0.045)
        p.merge(q, M)
    # chassi visivel atras da saia e engate
    for s in (-1, 1):
        seg_cyl(p, 'steel_d', (-HX + 0.2, 0.5, s * 0.9), (-HX - 1.3, 0.5, 0.0), 0.05, 6)
    p.cham('steel_d', -HX - 1.55, -HX - 1.2, 0.44, 0.58, -0.1, 0.1, 0.01); p.sphere('steel', 0.05, -HX - 1.45, 0.42, 0.0, 1)
    p.cyl('steel', 0.04, 0.06, 0.7, -HX - 0.9, 0.3, 8); p.cyl('steel_d', 0.12, 0.04, 0.07, -HX - 0.9, 0.3, 12); p.cham('steel_d', -HX - 0.96, -HX - 0.84, 0.7, 0.8, 0.24, 0.36, 0.01)
    seg_cyl(p, 'steel_d', (-HX - 0.9, 0.5, 0.3), (-HX - 0.9, 0.5, 0.5 * 0.9 * 0.33), 0.03, 6)
    # luminaria da porta, medidor e portinhola
    p.cham('steel_d', -1.78, -1.58, FL + 1.85, FL + 2.05, HZ + 0.016, HZ + 0.1, 0.008); p.box('lamp_glass', -1.75, -1.61, FL + 1.88, FL + 2.0, HZ + 0.1, HZ + 0.106)
    q = Piece(); q.cham('galv', -0.18, 0.18, 1.1, 1.55, 0.016, 0.16, 0.01); q.cyl('glass', 0.09, 1.55, 1.63, 0.0, 0.09, 14); q.cyl('galv', 0.1, 1.63, 1.66, 0.0, 0.09, 14)
    seg_cyl(q, 'galv', (0.0, 1.1, 0.08), (0.0, YL - 0.02, 0.08), 0.03, 8); p.merge(q, rot_y(-90, (-HX, 0, -1.1)))
    q = Piece(); q.cham(main, -0.32, 0.32, FL + 0.1, FL + 0.8, 0.012, 0.03, 0.004)
    for y in np.arange(FL + 0.16, FL + 0.32, 0.04): q.box('steel_d', -0.24, 0.24, y, y + 0.012, 0.03, 0.036)
    q.box('chrome', 0.22, 0.28, FL + 0.44, FL + 0.48, 0.03, 0.042); p.merge(q, rot_y(180, (-1.2, 0, -HZ)))
    return p

# ============================================================================ trailer: interior (piso, forro, divisorias, rodape, luminarias)
P1, P2, P3, PT = 1.6, 3.4, 0.2, 0.08
IX, IZ = HX - T, HZ - T
BB_H, BB_T = 0.09, 0.014
def bb_x(p, a, b, z, s):
    """Rodape ao longo de X, encostado na face z, voltado para s (+1 / -1)."""
    if b - a > 0.03: p.cham('dkwood', a, b, FL, FL + BB_H, *sorted((z, z + s * BB_T)), 0.003)
def bb_z(p, a, b, x, s):
    if b - a > 0.03: p.cham('dkwood', *sorted((x, x + s * BB_T)), FL, FL + BB_H, a, b, 0.003)
def trailer_in():
    p = Piece(); gap = BB_T + 0.004
    # piso
    zones = [(sbox(-IX, -IZ, -1.0, IZ), 'carpet'), (sbox(-1.0, -IZ, P1, IZ), 'vinyl_f'), (sbox(P1, P3, P2, IZ), 'vinyl_f'),
             (sbox(P1, -IZ, P2, P3), 'tile_a'), (sbox(P2, -IZ, IX, IZ), 'carpet_b')]
    for (q, m) in zones: ext_y(p, m, q, YB, FL)
    p.box('alu', -1.0 - 0.02, -1.0 + 0.02, FL, FL + 0.006, -IZ, IZ)
    # divisorias
    def wall_x(x, za, zb, gaps, h=CH):
        for (a, b) in segs_excl(gaps, za, zb): p.box('plaster', x - PT / 2, x + PT / 2, FL, FL + h, a, b)
        for (a, b) in gaps: p.box('plaster', x - PT / 2, x + PT / 2, FL + 2.05, FL + h, a, b)
        for (a, b) in gaps:
            for (c, d) in ((a, a + 0.02), (b - 0.02, b)): p.box('trim', x - PT / 2 - 0.012, x + PT / 2 + 0.012, FL, FL + 2.05, c, d)
            p.box('trim', x - PT / 2 - 0.012, x + PT / 2 + 0.012, FL + 2.03, FL + 2.05, a + 0.02, b - 0.02)
    def wall_z(z, xa, xb, gaps, h=CH):
        for (a, b) in segs_excl(gaps, xa, xb): p.box('plaster', a, b, FL, FL + h, z - PT / 2, z + PT / 2)
        for (a, b) in gaps: p.box('plaster', a, b, FL + 2.05, FL + h, z - PT / 2, z + PT / 2)
        for (a, b) in gaps:
            for (c, d) in ((a, a + 0.02), (b - 0.02, b)): p.box('trim', c, d, FL, FL + 2.05, z - PT / 2 - 0.012, z + PT / 2 + 0.012)
            p.box('trim', a + 0.02, b - 0.02, FL + 2.03, FL + 2.05, z - PT / 2 - 0.012, z + PT / 2 + 0.012)
    G1, G2, G3 = (0.65, 1.55), (0.75, 1.6), (2.05, 2.85)
    wall_x(P1, -IZ, IZ, [G1]); wall_x(P2, -IZ, IZ, [G2]); wall_z(P3, P1 + PT / 2, P2 - PT / 2, [G3])
    # rodapes por comodo (corridas em X inteiras, corridas em Z comecam depois delas)
    pa, pb = P1 - PT / 2, P1 + PT / 2; qa, qb = P2 - PT / 2, P2 + PT / 2; ra, rb = P3 - PT / 2, P3 + PT / 2
    for (a, b) in segs_excl([(-2.85 - 0.07, -1.95 + 0.07)], -IX, pa): bb_x(p, a, b, IZ, -1)
    bb_x(p, -IX, pa, -IZ, 1); bb_z(p, -IZ + gap, IZ - gap, -IX, 1)
    for (a, b) in segs_excl([G1], -IZ + gap, IZ - gap): bb_z(p, a, b, pa, -1)
    # corredor
    bb_x(p, pb, qa, IZ, -1)
    for (a, b) in segs_excl([G3], pb, qa): bb_x(p, a, b, rb, 1)
    for (a, b) in segs_excl([G1], rb + gap, IZ - gap): bb_z(p, a, b, pb, 1)
    for (a, b) in segs_excl([G2], rb + gap, IZ - gap): bb_z(p, a, b, qa, -1)
    # banheiro (azulejo ate 1,2 m nas paredes)
    for (a, b) in segs_excl([G3], pb, qa): bb_x(p, a, b, ra, -1)
    bb_x(p, pb, qa, -IZ, 1); bb_z(p, -IZ + gap, ra - gap, pb, 1); bb_z(p, -IZ + gap, ra - gap, qa, -1)
    for (a, b, z, s) in ((pb + gap, qa - gap, -IZ, 1),):
        p.box('tile_a', a, b, FL + BB_H + 0.004, FL + 1.2, *sorted((z, z + s * 0.008)))
    for (x, s) in ((pb, 1), (qa, -1)): p.box('tile_a', *sorted((x, x + s * 0.008)), FL + BB_H + 0.004, FL + 1.2, -IZ + 0.012, ra - 0.012)
    # quarto
    bb_x(p, qb, IX, IZ, -1)
    bb_x(p, qb, IX, -IZ, 1); bb_z(p, -IZ + gap, IZ - gap, IX, -1)
    for (a, b) in segs_excl([G2], -IZ + gap, IZ - gap): bb_z(p, a, b, qb, 1)
    return p

def trailer_roof():
    """Telhado arqueado de aluminio com emendas, calhas de borda, respiros e suspiro, mais o forro com plafons (pivo: centro, chao)."""
    p = Piece()
    # telhado
    zz = np.linspace(-(HZ + 0.06), HZ + 0.06, 25)
    prof = [(-(HZ + 0.06), YT), (HZ + 0.06, YT)] + [(z, roof_y(z)) for z in zz[::-1]]
    prof_x(p, 'alu', -HX - 0.06, HX + 0.06, prof)
    for x in np.arange(-HX + 0.6, HX - 0.3, 0.9):
        prof_x(p, 'galv', x - 0.02, x + 0.02, [(z, roof_y(z)) for z in zz[2:-2]] + [(z, roof_y(z) + 0.018) for z in zz[2:-2][::-1]])
    for s in (-1, 1):
        p.box('galv', -HX - 0.06, HX + 0.06, YT - 0.05, YT + 0.08, *sorted((s * (HZ + 0.06), s * (HZ + 0.085))))
    for s in (-1, 1):
        p.box('galv', *sorted((s * (HX + 0.06), s * (HX + 0.085))), YT - 0.05, YT + 0.08, -HZ - 0.085, HZ + 0.085)
    p.cyl('steel_d', 0.05, roof_y(-0.6) - 0.02, roof_y(-0.6) + 0.35, 2.4, -0.6, 10); p.cyl('steel_d', 0.07, roof_y(-0.6) + 0.35, roof_y(-0.6) + 0.38, 2.4, -0.6, 10)
    for (x, z) in ((-0.3, -0.9), (4.6, 0.3)):
        y = roof_y(z); p.cham('alu', x - 0.22, x + 0.22, y - 0.03, y + 0.1, z - 0.22, z + 0.22, 0.01); p.cham('steel_d', x - 0.16, x + 0.16, y + 0.1, y + 0.16, z - 0.16, z + 0.16, 0.01)
    # forro e luminarias
    ext_y(p, 'ceil', sbox(-IX, -IZ, IX, IZ), FL + CH, YT)
    for (x, z) in ((-3.8, 0.0), (0.3, 0.0), (2.5, 1.05), (2.5, -0.85), (4.7, 0.0)):
        p.cyl('lamp_glass', 0.16, FL + CH - 0.06, FL + CH, x, z, 16); ring_y(p, 'alu', 0.16, 0.18, FL + CH - 0.03, FL + CH, x, z, 16)
    return p

# ============================================================================ moveis do trailer (pivo: centro de tras, piso; frente para +Z)
def door_trailer(w=0.88, h=2.08, t=0.04):
    """Porta de trailer de chapa branca com janelinha alta, macaneta e tranca (pivo: dobradica, embaixo)."""
    p = Piece(); p.cham('paint_w', 0.0, w, 0.0, h, -t / 2, t / 2, 0.004)
    for s in (-1, 1):
        z0, z1 = sorted((s * t / 2, s * (t / 2 + 0.012)))
        p.box('alu', 0.2, w - 0.2, 1.42, 1.46, z0, z1); p.box('alu', 0.2, w - 0.2, 1.84, 1.88, z0, z1)
        p.box('alu', 0.2, 0.24, 1.46, 1.84, z0, z1); p.box('alu', w - 0.24, w - 0.2, 1.46, 1.84, z0, z1)
        for y in (0.3, 0.95): p.box('alu', 0.12, w - 0.12, y, y + 0.012, *sorted((s * t / 2, s * (t / 2 + 0.004))))
        p.sphere('chrome', 0.03, w - 0.08, 0.98, s * (t / 2 + 0.04), 1); p.box('chrome', w - 0.1, w - 0.06, 0.94, 1.02, *sorted((s * t / 2, s * (t / 2 + 0.03))))
        p.cyl('chrome', 0.022, 1.12, 1.16, w - 0.08, s * (t / 2 + 0.01), 12) if False else disc_z(p, 'chrome', 0.022, *sorted((s * t / 2, s * (t / 2 + 0.014))), w - 0.08, 1.14, 12)
    p.box('glass', 0.24, w - 0.24, 1.46, 1.84, -0.004, 0.004)
    for y in (0.25, 1.0, 1.9): p.box('chrome', -0.012, 0.02, y, y + 0.1, -t / 2 - 0.004, t / 2 + 0.004)
    return p
def bed(w=1.4, L1=1.95):
    """Cama de casal: cabeceira de madeira, estrado, colchao, colcha dobrada e 2 travesseiros."""
    p = Piece(); x = w / 2
    p.cham('dkwood', -x - 0.05, x + 0.05, 0.0, 1.05, 0.0, 0.05, 0.008)
    for xx in np.linspace(-x + 0.15, x - 0.15, 5): p.box('wood', xx - 0.04, xx + 0.04, 0.55, 0.95, 0.05, 0.062)
    p.cham('dkwood', -x - 0.02, x + 0.02, 0.12, 0.34, 0.05, L1, 0.01)
    for (a, c) in ((-x + 0.04, L1 - 0.06), (x - 0.04, L1 - 0.06)): p.box('dkwood', a - 0.03, a + 0.03, 0.0, 0.12, c - 0.03, c + 0.03)
    p.cham('bed_w', -x + 0.01, x - 0.01, 0.34, 0.56, 0.06, L1 - 0.02, 0.04)
    p.cham('bed_b', -x - 0.015, x + 0.015, 0.3, 0.585, 0.62, L1 + 0.005, 0.02)
    p.cham('bed_w', -x - 0.016, x + 0.016, 0.52, 0.6, 0.55, 0.72, 0.02)
    for s in (-1, 1): p.cham('bed_w', s * 0.34 - 0.3, s * 0.34 + 0.3, 0.56, 0.7, 0.1, 0.48, 0.05)
    return p
def nightstand():
    p = Piece(); p.cham('dkwood', -0.22, 0.22, 0.0, 0.55, 0.0, 0.4, 0.008); p.box('wood', -0.19, 0.19, 0.32, 0.5, 0.4, 0.412)
    p.sphere('chrome', 0.015, 0.0, 0.41, 0.425, 1)
    lathe(p, 'pot', [(0.07, 0.55), (0.06, 0.62), (0.02, 0.66), (0.02, 0.82)], 0.0, 0.2, 0.0, 12)
    lathe(p, 'cloth_y', [(0.15, 0.8), (0.1, 0.98), (0.0, 0.98)], 0.0, 0.2, 0.0, 14)
    return p
def dresser(w=1.0):
    p = Piece(); x = w / 2; p.cham('wood', -x, x, 0.06, 0.82, 0.0, 0.45, 0.01); p.box('dkwood', -x + 0.04, x - 0.04, 0.0, 0.06, 0.02, 0.4)
    for k in range(3):
        y = 0.1 + k * 0.24
        for s in (-1, 1):
            p.cham('dkwood', *sorted((s * 0.01, s * (x - 0.03))), y, y + 0.2, 0.45, 0.465, 0.004); p.box('chrome', s * x / 2 - 0.05, s * x / 2 + 0.05, y + 0.09, y + 0.11, 0.465, 0.485)
    p.cham('dkwood', -0.3, 0.3, 0.82, 1.5, 0.02, 0.05, 0.008); p.box('mirror', -0.26, 0.26, 0.86, 1.46, 0.05, 0.055)
    p.cyl('pot', 0.05, 0.82, 0.96, 0.38, 0.25, 10); p.sphere('plant', 0.1, 0.38, 1.02, 0.25, 1)
    return p
def kitchen_run(L1=1.85):
    """Cozinha: armarios de madeira com portas e puxadores, tampo, cuba com torneira, fogao esmaltado com 4 bocas e forno,
    coifa, armario aereo e frontao."""
    p = Piece(); x = L1 / 2; sx0, sx1 = -L1 / 2, -L1 / 2 + 0.6     # fogao
    for (a, b) in [ab for ab in segs_excl([(sx0 - 0.002, sx1 + 0.002)], -x, x) if ab[1] - ab[0] > 0.05]:
        p.cham('cab', a, b, 0.1, 0.88, 0.0, 0.58, 0.006); p.box('dark', a + 0.02, b - 0.02, 0.0, 0.1, 0.02, 0.52)
        n = max(1, int(round((b - a) / 0.45)))
        for k in range(n):
            c0 = a + k * (b - a) / n + 0.01; c1 = a + (k + 1) * (b - a) / n - 0.01
            p.cham('cab', c0, c1, 0.13, 0.7, 0.58, 0.6, 0.004); p.box('chrome', c1 - 0.06, c1 - 0.04, 0.55, 0.66, 0.6, 0.62)
            p.cham('cab', c0, c1, 0.72, 0.85, 0.58, 0.6, 0.004); p.box('chrome', (c0 + c1) / 2 - 0.05, (c0 + c1) / 2 + 0.05, 0.78, 0.8, 0.6, 0.62)
        p.cham('ctop', a - 0.002, b + 0.002, 0.88, 0.92, 0.0, 0.62, 0.006)
        p.box('ctop', a, b, 0.92, 1.02, 0.0, 0.02)
    # cuba e torneira (debaixo da janela)
    cx = 0.15; p.box('chrome', cx - 0.25, cx + 0.25, 0.92, 0.926, 0.12, 0.5); p.box('dark', cx - 0.22, cx + 0.22, 0.926, 0.928, 0.15, 0.47)
    seg_cyl(p, 'chrome', (cx, 0.926, 0.07), (cx, 1.18, 0.07), 0.014, 8); seg_cyl(p, 'chrome', (cx, 1.18, 0.07), (cx, 1.16, 0.25), 0.012, 8)
    for s in (-1, 1): p.cyl('chrome', 0.02, 0.926, 0.97, cx + s * 0.08, 0.07, 8)
    # fogao
    p.cham('enamel', sx0, sx1, 0.0, 0.9, 0.0, 0.62, 0.008); p.box('dark', sx0 + 0.02, sx1 - 0.02, 0.0, 0.08, 0.62, 0.625)
    p.cham('enamel', sx0 + 0.03, sx1 - 0.03, 0.14, 0.7, 0.62, 0.64, 0.006); p.box('dark', sx0 + 0.12, sx1 - 0.12, 0.3, 0.58, 0.64, 0.644)
    p.box('chrome', sx0 + 0.08, sx1 - 0.08, 0.64, 0.66, 0.65, 0.68)
    for k in range(4): p.cyl('dark', 0.02, 0.76, 0.8, sx0 + 0.12 + k * 0.12, 0.645, 10) if False else disc_z(p, 'dark', 0.02, 0.62, 0.65, sx0 + 0.12 + k * 0.12, 0.8, 10)
    for (bx, bz) in ((sx0 + 0.16, 0.18), (sx1 - 0.16, 0.18), (sx0 + 0.16, 0.44), (sx1 - 0.16, 0.44)):
        ring_y(p, 'dark', 0.06, 0.09, 0.9, 0.915, bx, bz, 14); p.cyl('steel_d', 0.04, 0.9, 0.92, bx, bz, 12)
    p.cham('enamel', sx0, sx1, 0.9, 1.05, 0.0, 0.06, 0.006)
    # coifa e armario aereo
    p.hull('enamel', [(xx, y, z) for xx in (sx0, sx1) for (y, z) in ((1.58, 0.0), (1.58, 0.48), (1.72, 0.0), (1.72, 0.36))]); p.box('dark', sx0 + 0.05, sx1 - 0.05, 1.574, 1.58, 0.06, 0.42)
    a, b = -x, -0.33
    p.cham('cab', a, b, 1.72, 2.22, 0.0, 0.34, 0.006)
    for (c0, c1) in ((a + 0.01, (a + b) / 2 - 0.005), ((a + b) / 2 + 0.005, b - 0.01)):
        p.cham('cab', c0, c1, 1.74, 2.2, 0.34, 0.36, 0.004); p.box('chrome', c1 - 0.05, c1 - 0.03, 1.76, 1.86, 0.36, 0.38)
    p.box('ctop', -x, sx0 - 0.002, 1.02, 1.03, 0.0, 0.02) if False else None
    return p
def fridge_h():
    """Geladeira de 2 portas esmaltada (congelador em cima), puxadores cromados."""
    p = Piece(); p.cham('enamel', -0.34, 0.34, 0.04, 1.72, 0.0, 0.66, 0.03); p.box('dark', -0.3, 0.3, 0.0, 0.04, 0.04, 0.6)
    p.cham('enamel', -0.33, 0.33, 0.08, 1.18, 0.66, 0.69, 0.012); p.cham('enamel', -0.33, 0.33, 1.21, 1.69, 0.66, 0.69, 0.012)
    for (y0, y1) in ((0.7, 1.08), (1.28, 1.5)): p.cham('chrome', 0.24, 0.27, y0, y1, 0.69, 0.73, 0.008)
    p.box('food_r', -0.1, -0.04, 1.4, 1.46, 0.69, 0.695); p.box('food_y', 0.0, 0.07, 1.33, 1.4, 0.69, 0.695)
    return p
def dinette():
    """Mesinha de cozinha com tampo de formica, borda cromada e pe central."""
    p = Piece(); p.cham('ctop', -0.42, 0.42, 0.72, 0.75, -0.36, 0.36, 0.01); p.box('chrome', -0.425, 0.425, 0.715, 0.735, -0.365, 0.365)
    p.cyl('chrome', 0.04, 0.05, 0.715, 0, 0, 12); p.cyl('chrome', 0.25, 0.0, 0.05, 0, 0, 20)
    p.cyl('pot', 0.06, 0.75, 0.84, 0.1, 0.05, 12); p.sphere('food_y', 0.04, -0.12, 0.79, -0.05, 1); p.sphere('food_r', 0.04, -0.02, 0.79, -0.12, 1)
    return p
def chair_d():
    p = Piece()
    for s in (-1, 1):
        seg_cyl(p, 'chrome', (s * 0.2, 0.0, 0.2), (s * 0.2, 0.45, 0.2), 0.012, 6); seg_cyl(p, 'chrome', (s * 0.2, 0.0, -0.2), (s * 0.2, 0.92, -0.22), 0.012, 6)
    p.cham('vinyl', -0.22, 0.22, 0.45, 0.52, -0.21, 0.22, 0.025); p.cham('vinyl', -0.21, 0.21, 0.62, 0.9, -0.26, -0.2, 0.02)
    return p
def coffee_table():
    p = Piece(); p.cham('dkwood', -0.5, 0.5, 0.36, 0.4, -0.3, 0.3, 0.008)
    for sx in (-1, 1):
        for sz in (-1, 1): p.box('dkwood', sx * 0.44 - 0.025, sx * 0.44 + 0.025, 0.0, 0.36, sz * 0.24 - 0.025, sz * 0.24 + 0.025)
    p.box('dkwood', -0.42, 0.42, 0.1, 0.12, -0.22, 0.22); p.box('paper', -0.2, 0.06, 0.4, 0.41, -0.1, 0.12); p.cyl('pot', 0.04, 0.4, 0.5, 0.25, 0.05, 10)
    return p
def tv_stand():
    """Rack baixo com TV de tubo, antena interna e videocassete."""
    p = Piece(); p.cham('dkwood', -0.6, 0.6, 0.0, 0.5, 0.0, 0.45, 0.008); p.box('dark', -0.56, 0.56, 0.06, 0.44, 0.44, 0.452) if False else None
    for s in (-1, 1): p.cham('wood', *sorted((s * 0.01, s * 0.57)), 0.06, 0.44, 0.45, 0.462, 0.004)
    p.cham('steel_d', -0.32, 0.32, 0.5, 0.96, 0.04, 0.44, 0.03); p.cham('screen', -0.25, 0.2, 0.56, 0.9, 0.44, 0.452, 0.02)
    for y in (0.62, 0.7): p.cyl('steel', 0.015, 0.0, 0.0, 0, 0) if False else disc_z(p, 'steel', 0.016, 0.44, 0.452, 0.26, y, 8)
    p.cyl('dark', 0.04, 0.96, 0.98, 0.0, 0.24, 10)
    for s in (-1, 1): seg_cyl(p, 'chrome', (0.0, 0.98, 0.24), (s * 0.25, 1.4, 0.2), 0.005, 4)
    p.cham('dark', -0.2, 0.2, 0.46, 0.5, 0.06, 0.36, 0.006) if False else None
    return p
def shower(w=0.86):
    """Box: base de louca, painel de fundo e lateral, vidro do lado aberto, cortina, ducha e registro."""
    p = Piece(); x = w / 2
    p.cham('porcelain', -x + 0.016, x, 0.002, 0.08, 0.016, w, 0.01); p.box('dark', -0.04, 0.04, 0.08, 0.082, w / 2 - 0.04, w / 2 + 0.04)
    p.box('porcelain', -x + 0.009, x, 0.08, 2.0, 0.009, 0.02); p.box('porcelain', -x + 0.009, -x + 0.02, 0.08, 2.0, 0.02, w)
    p.box('alu', x - 0.022, x, 0.08, 2.0, w - 0.04, w); p.box('glass', x - 0.016, x - 0.004, 0.1, 1.98, 0.03, w - 0.04)
    seg_cyl(p, 'chrome', (-x + 0.02, 1.95, w - 0.02), (x - 0.02, 1.95, w - 0.02), 0.01, 6)
    for k in range(9):
        xx = -x + 0.06 + k * 0.05; p.box('cloth_b', xx, xx + 0.04, 0.5, 1.92, w - 0.04 + 0.012 * (k % 2), w - 0.03 + 0.012 * (k % 2))
    seg_cyl(p, 'chrome', (0.0, 1.0, 0.02), (0.0, 1.85, 0.02), 0.01, 6); p.cyl('chrome', 0.05, 1.85, 1.87, 0.0, 0.07, 12)
    seg_cyl(p, 'chrome', (0.0, 1.86, 0.02), (0.0, 1.86, 0.07), 0.01, 6); disc_z(p, 'chrome', 0.035, 0.02, 0.05, 0.0, 1.1, 12)
    return p
def vanity():
    p = Piece(); p.cham('cab', -0.3, 0.3, 0.08, 0.82, 0.0, 0.46, 0.006); p.box('dark', -0.27, 0.27, 0.002, 0.08, 0.03, 0.4)
    for s in (-1, 1): p.cham('cab', *sorted((s * 0.01, s * 0.28)), 0.12, 0.78, 0.46, 0.475, 0.004); p.box('chrome', s * 0.05 - 0.01, s * 0.05 + 0.01, 0.6, 0.7, 0.475, 0.49)
    p.cham('porcelain', -0.32, 0.32, 0.82, 0.86, 0.0, 0.5, 0.008); p.cyl('dark', 0.16, 0.855, 0.862, 0.0, 0.26, 18)
    seg_cyl(p, 'chrome', (0.0, 0.86, 0.06), (0.0, 1.0, 0.06), 0.012, 6); seg_cyl(p, 'chrome', (0.0, 1.0, 0.06), (0.0, 0.98, 0.16), 0.01, 6)
    p.cham('chrome', -0.28, 0.28, 1.1, 1.75, 0.0, 0.1, 0.01); p.box('mirror', -0.26, 0.26, 1.12, 1.73, 0.1, 0.104)
    p.cham('lamp_glass', -0.24, 0.24, 1.8, 1.88, 0.02, 0.1, 0.02)
    return p
def towel_bar():
    p = Piece(); seg_cyl(p, 'chrome', (-0.3, 1.2, 0.05), (0.3, 1.2, 0.05), 0.01, 6)
    for s in (-1, 1): seg_cyl(p, 'chrome', (s * 0.3, 1.2, 0.0), (s * 0.3, 1.2, 0.05), 0.01, 6)
    p.box('cloth_r', -0.2, 0.2, 0.72, 1.21, 0.035, 0.045); p.box('cloth_r', -0.2, 0.2, 0.9, 1.21, 0.055, 0.065)
    return p
def rug(w=1.6, d=1.1, mat='cloth_r'):
    p = Piece(); p.cham(mat, -w / 2, w / 2, 0.002, 0.012, -d / 2, d / 2, 0.004); p.box('cloth_y', -w / 2 + 0.08, w / 2 - 0.08, 0.012, 0.014, -d / 2 + 0.08, d / 2 - 0.08)
    p.box(mat, -w / 2 + 0.14, w / 2 - 0.14, 0.014, 0.016, -d / 2 + 0.14, d / 2 - 0.14); return p

# ============================================================================ lote (pivo: centro do trailer, chao; coordenadas do trailer)
DX0, DX1, DZ0, DZ1 = -4.2, -0.6, HZ + 0.03, 4.4
YD = FL - 0.03                               # topo da varanda
def rail_run(p, a, b, z, y0, axis='x'):
    """Guarda-corpo de madeira: corrimao, travessa de baixo e balaustres (eixo x ou z)."""
    def B(u0, u1, y_0, y_1, v0, v1):
        if axis == 'x': p.box('wood', u0, u1, y_0, y_1, v0, v1)
        else: p.box('wood', v0, v1, y_0, y_1, u0, u1)
    B(a, b, y0 + 0.9, y0 + 0.94, z - 0.06, z + 0.06); B(a, b, y0 + 0.84, y0 + 0.9, z - 0.025, z + 0.025); B(a, b, y0 + 0.08, y0 + 0.14, z - 0.025, z + 0.025)
    n = int((b - a) / 0.12)
    for k in range(1, n):
        u = a + k * (b - a) / n; B(u - 0.02, u + 0.02, y0 + 0.14, y0 + 0.84, z - 0.02, z + 0.02)
def deck():
    """Varanda de madeira na porta: tabuas com frestas, testeira, pilares, guarda-corpo com balaustres e escada de 4 degraus
    com longarinas e corrimaos."""
    p = Piece()
    for x in np.arange(DX0 + 0.005, DX1 - 0.1, 0.146): p.box('deck', x, min(x + 0.14, DX1 - 0.005), YD - 0.03, YD, DZ0, DZ1)
    for (a, b, c, d) in ((DX0 - 0.03, DX1 + 0.03, DZ1, DZ1 + 0.03), (DX0 - 0.03, DX0, DZ0, DZ1), (DX1, DX1 + 0.03, DZ0, DZ1)):
        p.box('wood', a, b, YD - 0.2, YD - 0.01, c, d)
    p.box('dkwood', DX0 + 0.05, DX1 - 0.05, YD - 0.2, YD - 0.032, DZ0 + 0.1, DZ1 - 0.1)
    for (x, z) in ((DX0 + 0.05, DZ1 - 0.05), (DX1 - 0.05, DZ1 - 0.05), (DX0 + 0.05, DZ0 + 0.1), (DX1 - 0.05, DZ0 + 0.1), ((DX0 + DX1) / 2, DZ1 - 0.05)):
        p.box('wood', x - 0.045, x + 0.045, 0.0, YD - 0.03, z - 0.045, z + 0.045); p.box('concrete', x - 0.12, x + 0.12, YL - 0.03, YL + 0.04, z - 0.12, z + 0.12)
    # pilares do guarda-corpo
    posts = [(DX0 + 0.045, DZ1 - 0.045), (DX1 - 0.045, DZ1 - 0.045), (DX0 + 0.045, DZ0 + 0.05), ((DX0 + DX1) / 2, DZ1 - 0.045), (DX1 - 0.045, DZ0 + 0.05),
             (DX1 - 0.045, 3.1 - 0.045)]
    for (x, z) in posts:
        p.box('wood', x - 0.045, x + 0.045, YD, YD + 1.0, z - 0.045, z + 0.045); p.hull('wood', [(x + a, YD + 1.0 + h, z + c) for a in (-0.05, 0.05) for c in (-0.05, 0.05) for h in (0.0,)] + [(x, YD + 1.06, z)])
    zz = DZ1 - 0.045
    for (a, b) in ((DX0 + 0.09, (DX0 + DX1) / 2 - 0.045), ((DX0 + DX1) / 2 + 0.045, DX1 - 0.09)): rail_run(p, a, b, zz, YD, 'x')
    rail_run(p, DZ0 + 0.095, DZ1 - 0.09, DX0 + 0.045, YD, 'z'); rail_run(p, DZ0 + 0.095, 3.1 - 0.09, DX1 - 0.045, YD, 'z')
    # escada para +X
    n = 4; rise = (YD - YL) / n; run = 0.27; sz0, sz1 = 3.12, DZ1 - 0.09
    for k in range(1, n):
        y = YD - k * rise; x0 = DX1 + 0.03 + (k - 1) * run
        p.box('deck', x0, x0 + run + 0.02, y - 0.035, y, sz0, sz1)
    for z in (sz0 - 0.04, sz1 + 0.0):
        p.hull('wood', [(DX1 + 0.03, YD - 0.04, z), (DX1 + 0.03, YD - 0.22, z), (DX1 + 0.03 + n * run, YL - 0.01, z), (DX1 + 0.03 + (n - 1) * run + 0.05, YL - 0.01, z),
                        (DX1 + 0.03, YD - 0.04, z + 0.04), (DX1 + 0.03, YD - 0.22, z + 0.04), (DX1 + 0.03 + n * run, YL - 0.01, z + 0.04), (DX1 + 0.03 + (n - 1) * run + 0.05, YL - 0.01, z + 0.04)])
    for z in (sz0 - 0.02, sz1 + 0.02):
        xe = DX1 + 0.03 + (n - 1) * run; p.box('wood', xe - 0.045, xe + 0.045, YL - 0.02, YL + 0.95, z - 0.045, z + 0.045)
        seg_cyl(p, 'wood', (DX1 - 0.045, YD + 0.92, z), (xe, YL + 0.92, z), 0.025, 6)
    return p
def deck_awning():
    """Toldo de aluminio sobre a varanda: chapa canelada com caimento, viga de testa, calha e 2 pilares."""
    p = Piece(); y0, y1 = FL + 2.28, FL + 2.06; a, b = DX0 - 0.1, DX1 + 0.1; z0, z1 = HZ + 0.016, DZ1 + 0.05
    p.box('alu', a, b, y0 - 0.12, y0 + 0.02, z0, z0 + 0.05)
    def yy(z): return y0 + (y1 - y0) * (z - z0) / (z1 - z0)
    p.hull('alu', [(x, yy(z) + d, z) for x in (a, b) for z in (z0 + 0.05, z1) for d in (0.0, 0.02)])
    for x in np.arange(a + 0.1, b - 0.05, 0.15): p.hull('alu', [(x + dx, yy(z) + 0.02 + h, z) for dx in (-0.025, 0.025) for z in (z0 + 0.05, z1 - 0.01) for h in (0.0, 0.025 if abs(dx) < 1 else 0)] + [(x, yy(z) + 0.05, z) for z in (z0 + 0.05, z1 - 0.01)])
    p.box('alu', a, b, yy(z1) - 0.1, yy(z1) + 0.03, z1, z1 + 0.06)
    for x in (DX0 + 0.045, DX1 - 0.045):
        p.box('alu', x - 0.04, x + 0.04, YD + 1.06, yy(z1) - 0.1, DZ1 - 0.085, DZ1 - 0.005)
    seg_cyl(p, 'alu', (b - 0.05, yy(z1) - 0.05, z1 + 0.03), (b - 0.05, YD + 0.02, z1 + 0.03), 0.025, 8)
    return p
CP = (0.8, 6.6, 2.45, 6.2)
def carport():
    """Garagem coberta de aco: 6 pilares com placas de base, vigas, cobertura de chapa canelada com caimento e calha."""
    p = Piece(); x0, x1, z0, z1 = CP; ya, yb = 2.62, 2.48
    def yy(z): return ya + (yb - ya) * (z - z0) / (z1 - z0)
    for x in (x0 + 0.1, (x0 + x1) / 2, x1 - 0.1):
        for z in (z0 + 0.1, z1 - 0.1):
            p.box('galv', x - 0.04, x + 0.04, YG, yy(z) - 0.12, z - 0.04, z + 0.04); p.box('steel_d', x - 0.1, x + 0.1, YG - 0.02, YG + 0.012, z - 0.1, z + 0.1)
        p.hull('galv', [(x + dx, yy(z) - 0.12 + h, z) for dx in (-0.04, 0.04) for z in (z0 + 0.05, z1 - 0.05) for h in (0.0, 0.1)])
    for z in (z0 + 0.1, z1 - 0.1): p.box('galv', x0 + 0.02, x1 - 0.02, yy(z) - 0.12, yy(z) - 0.12 + 0.002, z - 0.05, z + 0.05) if False else None
    p.hull('alu', [(x, yy(z) - 0.02 + d, z) for x in (x0, x1) for z in (z0, z1) for d in (0.0, 0.015)])
    for x in np.arange(x0 + 0.08, x1 - 0.04, 0.2): p.hull('alu', [(x + dx, yy(z) - 0.005 + h, z) for dx in (-0.03, 0.03) for z in (z0 + 0.01, z1 - 0.01) for h in (0.0,)] + [(x, yy(z) + 0.02, z) for z in (z0 + 0.01, z1 - 0.01)])
    p.box('alu', x0, x1, yy(z1) - 0.1, yy(z1) - 0.0, z1, z1 + 0.06)
    seg_cyl(p, 'alu', (x1 - 0.05, yy(z1) - 0.06, z1 + 0.03), (x1 - 0.05, YG, z1 + 0.03), 0.03, 8)
    return p
def shed():
    """Deposito de chapa canelada (1,8 x 1,4 m): telhado de 2 aguas, portas de correr com puxadores, base de madeira."""
    p = Piece(); x, z0, z1, h = 0.9, -0.7, 0.7, 1.75
    p.box('pallet', -x - 0.04, x + 0.04, 0.0, 0.1, z0 - 0.04, z1 + 0.04)
    for (a, b, c, d) in ((-x, x, z0, z0 + 0.02), (-x, -x + 0.02, z0 + 0.02, z1), (x - 0.02, x, z0 + 0.02, z1)): p.box('paint_w', a, b, 0.1, 0.1 + h, c, d)
    for k in np.arange(-x + 0.06, x - 0.03, 0.09): p.box('paint_w', k - 0.02, k + 0.02, 0.1, 0.1 + h, z0 - 0.012, z0)
    for z in np.arange(z0 + 0.08, z1 - 0.03, 0.09):
        for s in (-1, 1): p.box('paint_w', *sorted((s * x, s * (x + 0.012))), 0.1, 0.1 + h, z - 0.02, z + 0.02)
    # frente com 2 portas de correr
    p.box('paint_w', -x, x, 0.1, 0.16, z1 - 0.02, z1); p.box('paint_w', -x, x, h - 0.06 + 0.1, h + 0.1, z1 - 0.02, z1)
    for (a, b, zz) in ((-x + 0.02, 0.02, z1), (-0.02, x - 0.02, z1 + 0.022)):
        p.box('paint_g', a, b, 0.16, h + 0.04, zz, zz + 0.02); p.box('chrome', (a + b) / 2 - 0.02 + (0.3 if a < 0 else -0.3), (a + b) / 2 + 0.02 + (0.3 if a < 0 else -0.3), 0.8, 1.0, zz + 0.02, zz + 0.04)
        for k in np.arange(a + 0.07, b - 0.04, 0.09): p.box('paint_g', k - 0.02, k + 0.02, 0.2, h, zz + 0.02, zz + 0.032)
    p.box('galv', -x, x, h + 0.04, h + 0.08, z1 + 0.042, z1 + 0.06)
    # telhado e oitoes
    yr = 0.1 + h; rh = 0.32
    for s in (-1, 1): p.hull('paint_w', [(xx, yr + 0.0 * s, zz) for xx in (s * x - s * 0.02, s * x) for zz in (z0, z1)] + [(s * 0.0 + xx, yr + rh, zz) for xx in (0.0,) for zz in (z0, z1)] if False else [(xx, yr, zz) for xx in (s * x, s * (x - 0.02)) for zz in (z0, z1)] + [(0.0, yr + rh - 0.02, zz) for zz in (z0, z1)])
    for s in (-1, 1): p.hull('paint_g', [(s * (x + 0.08), yr - 0.04, zz) for zz in (z0 - 0.08, z1 + 0.1)] + [(s * (x + 0.08), yr - 0.0, zz) for zz in (z0 - 0.08, z1 + 0.1)] + [(0.0, yr + rh, zz) for zz in (z0 - 0.08, z1 + 0.1)] + [(0.0, yr + rh + 0.04, zz) for zz in (z0 - 0.08, z1 + 0.1)])
    return p
def picnic_table():
    p = Piece()
    for k in range(5): p.box('wood', -0.9, 0.9, 0.72, 0.76, -0.38 + k * 0.152, -0.24 + k * 0.152)
    for s in (-1, 1):
        for k in range(2): p.box('wood', -0.9, 0.9, 0.42, 0.46, s * (0.56 + k * 0.13) - 0.06, s * (0.56 + k * 0.13) + 0.06)
        x = s * 0.62
        for zs in (-1, 1): p.hull('dkwood', [(x + d, y, z) for d in (-0.03, 0.03) for (y, z) in ((0.0, zs * 0.74), (0.0, zs * 0.62), (0.72, zs * 0.1), (0.72, zs * 0.02))])
        p.box('dkwood', x - 0.03, x + 0.03, 0.36, 0.42, -0.8, 0.8)
    p.cyl('cloth_r', 0.12, 0.76, 0.78, 0.2, 0.0, 14) if False else p.box('cloth_r', -0.5, 0.5, 0.76, 0.765, -0.3, 0.3)
    return p
def grill():
    """Churrasqueira de chaleira com tampa, 3 pes, rodinhas e grelha."""
    p = Piece(); y = 0.75
    lathe(p, 'iron', [(0.06, y - 0.32), (0.24, y - 0.2), (0.29, y - 0.05), (0.3, y)], 0.0, 0.0, 0.0, 18)
    lathe(p, 'iron', [(0.3, y + 0.01), (0.27, y + 0.16), (0.16, y + 0.28), (0.0, y + 0.31)], 0.0, 0.0, 0.0, 18)
    p.cyl('chrome', 0.03, y + 0.31, y + 0.34, 0, 0, 8); seg_cyl(p, 'chrome', (-0.1, y + 0.3, 0), (0.1, y + 0.3, 0), 0.012, 6)
    for k in range(3):
        a = k * 2 * math.pi / 3; seg_cyl(p, 'steel_d', (0.2 * math.cos(a), y - 0.2, 0.2 * math.sin(a)), (0.32 * math.cos(a), 0.0, 0.32 * math.sin(a)), 0.015, 6)
    for k in (0, 1):
        a = k * 2 * math.pi / 3; disc_x(p, 'rubber', 0.07, 0.32 * math.cos(a) - 0.02, 0.32 * math.cos(a) + 0.02, 0.07, 0.32 * math.sin(a), 12) if False else None
    ring_y(p, 'steel_d', 0.25, 0.27, 0.3, 0.32, 0, 0, 18)
    return p
def lawn_chair(mat='cloth_b'):
    """Cadeira de praia dobravel de aluminio com fitas trancadas."""
    p = Piece()
    for s in (-1, 1):
        seg_cyl(p, 'alu', (s * 0.26, 0.0, 0.25), (s * 0.26, 0.38, 0.2), 0.012, 6); seg_cyl(p, 'alu', (s * 0.26, 0.0, -0.25), (s * 0.26, 0.85, -0.35), 0.012, 6)
        seg_cyl(p, 'alu', (s * 0.26, 0.38, 0.22), (s * 0.26, 0.38, -0.27), 0.012, 6); seg_cyl(p, 'alu', (s * 0.26, 0.58, 0.15), (s * 0.26, 0.58, -0.3), 0.012, 6)
    for k in range(5):
        z = 0.15 - k * 0.09; p.box(mat if k % 2 else 'cloth_y', -0.25, 0.25, 0.37, 0.385, z - 0.035, z + 0.035)
    for k in range(5):
        t = k / 4; y = 0.42 + t * 0.4; z = -0.27 - t * 0.08; p.hull(mat if k % 2 else 'cloth_y', [(x, y + d, z - d * 0.2 + e) for x in (-0.25, 0.25) for d in (-0.035, 0.035) for e in (0.0, 0.012)])
    return p
def clothesline():
    """Varal: 2 postes em T de tubo com 4 fios e roupas penduradas."""
    p = Piece(); L1 = 3.0
    for x in (-L1 / 2, L1 / 2):
        p.cyl('galv', 0.03, YL - 0.1, 1.85, x, 0, 8); p.box('galv', x - 0.025, x + 0.025, 1.82, 1.87, -0.5, 0.5)
    for z in (-0.42, -0.14, 0.14, 0.42): seg_cyl(p, 'paint_w', (-L1 / 2, 1.85, z), (L1 / 2, 1.85, z), 0.004, 3)
    rng = np.random.default_rng(5)
    for (x, z, w, h, m) in ((-0.9, -0.42, 0.5, 0.7, 'cloth_r'), (-0.2, -0.42, 0.4, 0.45, 'cloth_y'), (0.5, -0.14, 0.7, 0.5, 'bed_w'), (-0.6, 0.14, 0.35, 0.6, 'cloth_b'), (0.4, 0.42, 0.45, 0.4, 'cloth_r')):
        p.box(m, x - w / 2, x + w / 2, 1.85 - h, 1.85, z - 0.006, z + 0.006)
        for s in (-1, 1): p.box('paint_y', x + s * (w / 2 - 0.04) - 0.01, x + s * (w / 2 - 0.04) + 0.01, 1.82, 1.88, z - 0.012, z + 0.012)
    return p
def propane():
    """Par de botijoes grandes de gas sobre laje, com regulador e tubo ate a parede."""
    p = Piece(); p.box('concrete', -0.55, 0.55, YL - 0.03, YL + 0.05, -0.35, 0.35)
    for x in (-0.27, 0.27):
        lathe(p, 'propane', [(0.0, YL + 0.05), (0.17, YL + 0.05), (0.18, YL + 0.12), (0.18, 1.05), (0.15, 1.15), (0.0, 1.17)], x, 0.0, 0.0, 16)
        ring_y(p, 'propane', 0.1, 0.12, 1.15, 1.3, x, 0.0, 12); p.cyl('chrome', 0.03, 1.17, 1.25, x, 0.0, 8)
        seg_cyl(p, 'chrome', (x, 1.24, 0.0), (0.0, 1.26, -0.12), 0.008, 4)
    p.cham('steel_d', -0.06, 0.06, 1.2, 1.32, -0.16, -0.08, 0.01); seg_cyl(p, 'steel', (0.0, 1.22, -0.16), (0.0, 0.3, -0.34), 0.012, 6)
    return p
def power_post():
    """Poste de energia do lote: poste de madeira tratada, medidor com visor, caixa de disjuntor e tomada."""
    p = Piece(); p.box('dkwood', -0.06, 0.06, YL - 0.2, 1.6, -0.06, 0.06)
    p.cham('galv', -0.15, 0.15, 0.8, 1.2, 0.06, 0.2, 0.01); p.cyl('glass', 0.08, 1.2, 1.28, 0.0, 0.13, 14) if False else disc_z(p, 'glass', 0.08, 0.2, 0.26, 0.0, 1.02, 16)
    p.cham('galv', -0.12, 0.12, 0.45, 0.72, 0.06, 0.16, 0.01); p.box('dark', -0.05, 0.05, 0.55, 0.6, 0.16, 0.17)
    seg_cyl(p, 'dark', (0.0, 1.6, 0.0), (0.0, 1.6, 0.0) if False else (0.0, YL - 0.05, 0.12), 0.02, 6) if False else seg_cyl(p, 'dark', (0.1, 0.45, 0.11), (0.1, YL - 0.05, 0.11), 0.02, 6)
    return p
def planter(L1=1.0):
    p = Piece(); x = L1 / 2; p.cham('wood', -x, x, 0.0, 0.3, -0.15, 0.15, 0.01); p.box('dirt', -x + 0.03, x - 0.03, 0.3, 0.31, -0.12, 0.12)
    rng = np.random.default_rng(int(L1 * 10))
    for k in range(int(L1 * 6)):
        xx = -x + 0.08 + k * (L1 - 0.16) / max(1, int(L1 * 6) - 1); p.sphere('leaf2', 0.07, xx, 0.36, rng.uniform(-0.05, 0.05), 1)
        p.sphere(['food_r', 'food_y', 'paint_w', 'cloth_b'][k % 4], 0.035, xx + 0.02, 0.43, rng.uniform(-0.05, 0.05), 1)
    return p
def wheelie_bin():
    p = Piece(); p.hull('dumpster', [(x, 0.06, z) for x in (-0.28, 0.28) for z in (-0.28, 0.3)] + [(x, 1.0, z) for x in (-0.31, 0.31) for z in (-0.34, 0.36)])
    p.hull('dumpster', [(x, 1.0, z) for x in (-0.33, 0.33) for z in (-0.38, 0.4)] + [(x, 1.05, z) for x in (-0.33, 0.33) for z in (-0.38, 0.4)])
    seg_cyl(p, 'dark', (-0.25, 0.95, -0.4), (0.25, 0.95, -0.4), 0.02, 6)
    for s in (-1, 1): disc_x(p, 'rubber', 0.1, *sorted((s * 0.3, s * 0.34)), 0.1, -0.3, 14)
    return p
def lattice(L1=2.4, h=1.8):
    """Painel de trelica de madeira com moldura e mourões (pivo: centro, chao)."""
    p = Piece(); x = L1 / 2
    for s in (-1, 1): p.box('dkwood', s * x - 0.045, s * x + 0.045, YL - 0.2, h + 0.08, -0.045, 0.045)
    p.box('lattice', -x + 0.045, x - 0.045, h - 0.04, h, -0.03, 0.03); p.box('lattice', -x + 0.045, x - 0.045, 0.1, 0.14, -0.03, 0.03)
    for (k, zz) in ((1, -0.012), (-1, 0.0)):
        for c in np.arange(-x - h, x + h, 0.16):
            pts = []
            seg = LineString([(c, 0.14), (c + k * (h - 0.18), h - 0.04)]).intersection(sbox(-x + 0.045, 0.14, x - 0.045, h - 0.04))
            if seg.is_empty or seg.length < 0.05: continue
            (u0, v0), (u1, v1) = list(seg.coords)[0], list(seg.coords)[-1]
            p.hull('lattice', [(u + du, v, zz + dz) for (u, v) in ((u0, v0), (u1, v1)) for du in (-0.014, 0.014) for dz in (0.0, 0.012)])
    return p
def rail_fence(pts, gap_x=None):
    """Cerca de mourao e 2 travessas ao redor do terreno."""
    p = Piece()
    for (a, b) in zip(pts[:-1], pts[1:]):
        a, b = np.array(a, float), np.array(b, float); Ln = np.linalg.norm(b - a); n = max(1, int(round(Ln / 2.4))); d = (b - a) / Ln
        for k in range(n + 1):
            c = a + d * Ln * k / n; p.box('dkwood', c[0] - 0.06, c[0] + 0.06, YL - 0.2, 1.1, c[1] - 0.06, c[1] + 0.06)
            p.hull('dkwood', [(c[0] + dx, 1.1, c[1] + dz) for dx in (-0.06, 0.06) for dz in (-0.06, 0.06)] + [(c[0], 1.16, c[1])])
        nrm = np.array([-d[1], d[0]])
        for y in (0.45, 0.9):
            for k in range(n):
                c0 = a + d * (Ln * k / n + 0.062); c1 = a + d * (Ln * (k + 1) / n - 0.062)
                o = nrm * 0.07
                p.hull('wood', [(c[0] + oo[0] * s, y + dy, c[1] + oo[1] * s) for c in (c0, c1) for s in (0.4, 1.0) for oo in (o,) for dy in (-0.07, 0.07)])
    return p
def sign_board():
    """Placa de entrada: base de tijolo com canteiro, 2 mourões e painel verde com pictogramas de trailer, arvore e sol."""
    p = Piece()
    p.box('brick', -1.4, 1.4, YL - 0.05, 0.5, -0.35, 0.35); p.box('concrete', -1.45, 1.45, 0.5, 0.56, -0.4, 0.4)
    p.box('dirt', -1.3, 1.3, 0.56, 0.6, -0.3, 0.3)
    for k in range(9): p.sphere('leaf2', 0.12, -1.15 + k * 0.29, 0.66, 0.15 * (k % 2) - 0.08, 1); p.sphere(['food_r', 'food_y', 'paint_w'][k % 3], 0.05, -1.1 + k * 0.29, 0.76, 0.0, 1)
    for x in (-1.15, 1.15): p.box('dkwood', x - 0.07, x + 0.07, 0.56, 2.4, -0.07, 0.07); p.hull('dkwood', [(x + a, 2.4, c) for a in (-0.07, 0.07) for c in (-0.07, 0.07)] + [(x, 2.5, 0)])
    p.cham('paint_g', -1.08, 1.08, 1.1, 2.2, -0.04, 0.04, 0.02)
    for z0, z1, s in ((0.04, 0.052, 1), (-0.052, -0.04, -1)):
        p.box('paint_w', -1.0, 1.0, 1.16, 1.19, z0, z1); p.box('paint_w', -1.0, 1.0, 2.11, 2.14, z0, z1)
        # trailer
        q = Piece(); q.cham('paint_w', -0.62, 0.38, 1.36, 1.72, 0, 0.012, 0.03); q.box('paint_g', -0.5, -0.3, 1.52, 1.64, 0.012, 0.014); q.box('paint_g', -0.1, 0.05, 1.42, 1.64, 0.012, 0.014)
        q.box('paint_g', 0.15, 0.3, 1.52, 1.64, 0.012, 0.014); q.box('paint_w', 0.38, 0.6, 1.4, 1.43, 0, 0.012)
        c = trimesh.creation.cylinder(radius=0.08, height=0.012, sections=16); c.apply_translation([-0.2, 1.34, 0.006]); q.add('paint_w', c)
        c = trimesh.creation.cylinder(radius=0.035, height=0.004, sections=12); c.apply_translation([-0.2, 1.34, 0.014]); q.add('paint_g', c)
        # arvore e sol
        c = trimesh.creation.cylinder(radius=0.16, height=0.012, sections=16); c.apply_translation([0.75, 1.75, 0.006]); q.add('paint_y', c)
        q.box('paint_y', 0.72, 0.78, 1.36, 1.6, 0, 0.012)
        c = trimesh.creation.cylinder(radius=0.09, height=0.012, sections=16); c.apply_translation([-0.75, 1.88, 0.006]); q.add('paint_y', c)
        for k in range(8):
            a = k * math.pi / 4; q.hull('paint_y', [(-0.75 + r * math.cos(a + e), 1.88 + r * math.sin(a + e), zz) for r, e in ((0.12, -0.06), (0.12, 0.06), (0.17, 0.0)) for zz in (0, 0.012)])
        M = tr(0, 0, z0) if s > 0 else rot_y(180, (0, 0, z1))
        p.merge(q, M)
    return p
def mailboxes():
    """Caixas de correio coletivas: pedestal, 12 portinholas com fechadura, 2 caixas de encomenda e telhadinho."""
    p = Piece(); p.box('concrete', -0.7, 0.7, YL - 0.03, YL + 0.06, -0.5, 0.5)
    p.box('steel_d', -0.12, 0.12, YL + 0.06, 0.8, -0.12, 0.12); p.cham('steel', -0.55, 0.55, 0.8, 1.6, -0.22, 0.22, 0.01)
    for i in range(4):
        for j in range(3):
            x = -0.55 + 0.06 + i * 0.25; y = 1.0 + j * 0.19
            p.cham('steel', x, x + 0.22, y, y + 0.16, 0.22, 0.232, 0.004); disc_z(p, 'chrome', 0.012, 0.232, 0.24, x + 0.18, y + 0.08, 8)
    p.cham('steel', -0.49, 0.49, 0.84, 0.98, 0.22, 0.232, 0.004)
    p.hull('steel_d', [(x, 1.6, z) for x in (-0.6, 0.6) for z in (-0.28, 0.28)] + [(x, 1.72, 0) for x in (-0.6, 0.6)])
    return p
def dumpster():
    p = Piece(); p.hull('dumpster', [(x, 0.15, z) for x in (-0.95, 0.95) for z in (-0.55, 0.45)] + [(x, 1.2, z) for x in (-0.98, 0.98) for z in (-0.62, 0.65)])
    for s in (-1, 1): p.hull('dark', [(xx, y, z) for xx in sorted((s * 0.02, s * 0.97)) for (y, z) in ((1.2, -0.66), (1.24, -0.66), (1.2, 0.68), (1.28, 0.68))])
    for x in (-0.8, 0.8):
        for z in (-0.4, 0.3): p.cyl('rubber', 0.07, 0.0, 0.15, x, z, 10)
    for s in (-1, 1): p.box('steel_d', *sorted((s * 0.96, s * 1.04)), 0.6, 0.7, -0.4, 0.4)
    return p
def speed_bump():
    p = Piece(); xs = np.arange(LANE[0], LANE[1] + 1e-6, 0.5)
    for k, (a, b) in enumerate(zip(xs[:-1], xs[1:])):
        prof_x(p, 'paint_y' if k % 2 else 'dark', a, b, [(-0.3, YA), (0.3, YA), (0.12, YA + 0.07), (-0.12, YA + 0.07)])
    return p
def street_light():
    """Poste de madeira com braco e luminaria de rua tipo cobra."""
    p = Piece(); lathe(p, 'dkwood', [(0.13, YL - 0.3), (0.1, 7.0), (0.0, 7.02)], 0.0, 0.0, 0.0, 10)
    seg_cyl(p, 'galv', (0.0, 6.4, 0.0), (1.6, 6.7, 0.0), 0.035, 8); seg_cyl(p, 'galv', (0.0, 6.0, 0.0), (0.8, 6.55, 0.0), 0.02, 6)
    p.hull('galv', [(1.5, 6.62, z) for z in (-0.14, 0.14)] + [(2.1, 6.66, z) for z in (-0.1, 0.1)] + [(1.5, 6.78, 0.0), (2.0, 6.74, 0.0)])
    p.hull('lamp_glass', [(x, 6.6, z) for x in (1.6, 2.0) for z in (-0.09, 0.09)] + [(1.8, 6.56, 0.0)])
    p.box('steel_d', -0.05, 0.05, 6.9, 6.95, -0.6, 0.6)
    for z in (-0.5, 0.5): p.cyl('paint_w', 0.03, 6.95, 7.05, 0.0, z, 8)
    return p

# ============================================================================ terreno (pivo: origem)
def lw(lot, x, z):
    """Ponto local do lote -> mundo."""
    X, Z, R = lot[0], lot[1], math.radians(lot[2])
    return X + x * math.cos(R) + z * math.sin(R), Z - x * math.sin(R) + z * math.cos(R)
def lpoly(lot, q):
    return Polygon([lw(lot, x, z) for (x, z) in q.exterior.coords])
SITE = sbox(SX0, SZ0, SX1, SZ1)
ROAD = unary_union([sbox(LANE[0], SZ0 + 1.0, LANE[1], SZ1), Point(0.0, SZ0 + 3.0).buffer(4.2, 32).intersection(sbox(-4.2, SZ0 + 1.0, 4.2, SZ1))]).buffer(0)
DRIVE = unary_union([lpoly(l, sbox(0.4, 2.3, 7.5, 6.3)) for l in LOTS]).difference(ROAD).buffer(0)
WALKS = unary_union([sbox(LANE[1], 14.0, 6.2, 15.4)]).difference(ROAD).buffer(0)
GRASS = SITE.difference(ROAD).difference(DRIVE).difference(WALKS).buffer(0)
def site():
    """Gramado, rua de asfalto com balao no fundo e faixa central tracejada, entradas de cascalho dos lotes e calcadinhas de concreto."""
    p = Piece()
    ext_y(p, 'grass', GRASS, GY, YL); ext_y(p, 'asphalt', ROAD, GY, YA); ext_y(p, 'gravel', DRIVE, GY, YG); ext_y(p, 'concrete', WALKS, GY, YG + 0.02)
    for z in np.arange(SZ0 + 7.0, SZ1 - 1.0, 3.0): p.box('paint_y', -0.06, 0.06, YA, YA + 0.003, z, z + 1.5)
    return p

# ============================================================================ pecas
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(float(x), 3), round(float(y), 3), round(float(z), 3)], 'rotY': round(float(ry), 3), 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': e['rotY'], 'open': round(float(ry + door), 3)}; e['tags'].append('door')
    L.append(e)
def lput(lot, n, x, y, z, ry=0, tags=(), door=None):
    X, Z = lw(lot, x, z); put(n, X, y, Z, lot[2] + ry, tags, door)
pieces = {}
for i, l in enumerate(LOTS):
    n = f'trailer_{"abcdef"[i]}'
    pieces[n] = trailer(l[3], l[4], l[5], True)
FENCE_PTS = [(-3.6, SZ1 - 0.3), (SX0 + 0.3, SZ1 - 0.3), (SX0 + 0.3, SZ0 + 0.3), (SX1 - 0.3, SZ0 + 0.3), (SX1 - 0.3, SZ1 - 0.3), (3.6, SZ1 - 0.3)]
pieces.update({
    'trailer_in': trailer_in(), 'trailer_roof': trailer_roof(), 'door_trailer': door_trailer(), 'deck': deck(), 'deck_awning': deck_awning(), 'carport': carport(), 'shed': shed(),
    'sofa': sofa(3, 'fabric2'), 'armchair': sofa(1, 'fabric3'), 'coffee_table': coffee_table(), 'tv_stand': tv_stand(), 'rug': rug(),
    'kitchen': kitchen_run(1.85), 'fridge': fridge_h(), 'dinette': dinette(), 'chair_d': chair_d(),
    'shower': shower(), 'wc': wc(), 'vanity': vanity(), 'towel_bar': towel_bar(),
    'bed': bed(), 'nightstand': nightstand(), 'dresser': dresser(), 'plant': plant(1.0), 'trash_can': trash_can(),
    'picnic_table': picnic_table(), 'grill': grill(), 'lawn_chair': lawn_chair('cloth_b'), 'lawn_chair_r': lawn_chair('cloth_r'), 'clothesline': clothesline(),
    'propane': propane(), 'power_post': power_post(), 'planter': planter(1.0), 'wheelie_bin': wheelie_bin(), 'lattice': lattice(),
    'car_sedan_r': car('car_r', 'sedan'), 'car_wagon_b': car('car_b', 'wagon'), 'car_pickup_y': car('car_y', 'pickup'),
    'car_hatch_g': car('car_g', 'hatch'), 'car_coupe_t': car('car_t', 'coupe'), 'car_sedan_w': car('car_w', 'sedan'),
    'fence': rail_fence(FENCE_PTS), 'sign_board': sign_board(), 'mailboxes': mailboxes(), 'dumpster': dumpster(), 'speed_bump': speed_bump(),
    'street_light': street_light(), 'tree': tree(6.5, 2.1), 'tree_b': tree(5.0, 1.6, 'leaf2', 4), 'bush': bush(), 'site': site(),
    'player_scale_ref': player_ref()})

# ============================================================================ montagem
OFF = BB_T + 0.003                               # moveis encostados ficam na frente do rodape
CARS = ['car_sedan_r', 'car_wagon_b', 'car_pickup_y', 'car_hatch_g', 'car_coupe_t', 'car_sedan_w']
for i, l in enumerate(LOTS):
    G = [f'lote{i + 1}']; f = FL
    lput(l, f'trailer_{"abcdef"[i]}', 0, 0, 0, 0, G + ['ext']); lput(l, 'trailer_in', 0, 0, 0, 0, G); lput(l, 'trailer_roof', 0, 0, 0, 0, G + ['roof'])
    lput(l, 'door_trailer', -2.84, f + 0.005, HZ - T / 2, 0, G, door=90)
    # sala
    lput(l, 'sofa', -2.7, f, -0.6, -90, G); lput(l, 'armchair', -4.9, f, -IZ + OFF, 0, G); lput(l, 'coffee_table', -4.3, f, -0.5, 90, G)
    lput(l, 'tv_stand', -IX + OFF, f, -0.4, 90, G); lput(l, 'rug', -4.1, f, -0.5, 90, G)
    if i % 2 == 0: lput(l, 'plant', -5.5, f, 1.45, 0, G)
    # cozinha
    lput(l, 'kitchen', -0.075, f, -IZ + OFF, 0, G); lput(l, 'fridge', 1.19, f, -IZ + OFF, 0, G)
    lput(l, 'dinette', -0.45, f, 1.42, 0, G); lput(l, 'chair_d', -1.02, f, 1.42, 90, G); lput(l, 'chair_d', 0.12, f, 1.42, -90, G)
    lput(l, 'trash_can', -1.3, f, -1.55, 0, G)
    # banheiro
    lput(l, 'shower', P1 + PT / 2 + 0.43, f, -IZ, 0, G); lput(l, 'wc', 3.0, f, -IZ + OFF, 0, G); lput(l, 'vanity', P2 - PT / 2 - OFF, f, -0.6, -90, G)
    # quarto
    lput(l, 'bed', IX - OFF, f, -0.3, -90, G); lput(l, 'nightstand', IX - OFF, f, -1.42, -90, G); lput(l, 'dresser', 4.05, f, -IZ + OFF, 0, G)
    # lote
    lput(l, 'deck', 0, 0, 0, 0, G); lput(l, 'deck_awning', 0, 0, 0, 0, G + ['roof']); lput(l, 'carport', 0, 0, 0, 0, G + ['roof'])
    lput(l, CARS[i], 3.7, YG, 4.35, 90, G)
    lput(l, 'propane', -HX - 0.65, 0, -1.2, -90, G); lput(l, 'power_post', -HX - 0.9, 0, 1.4, 90, G)
    lput(l, 'shed', -5.25, YL, 5.9, 90, G); lput(l, 'wheelie_bin', 7.0, YG, 2.95, 0, G)
    lput(l, 'planter', -2.4, YD, DZ1 - 0.3, 0, G) if i in (0, 3, 5) else None
    if i in (0, 2, 4): lput(l, 'picnic_table', -2.3, YL, 5.8, 0, G); lput(l, 'grill', -0.6, YL, 6.2, 0, G)
    if i in (1, 3, 5): lput(l, 'lawn_chair', -2.9, YD, 3.5, 160, G); lput(l, 'lawn_chair_r', -1.7, YD, 3.6, 200, G); lput(l, 'clothesline', -1.9, YL, 6.0, 0, G)
    if i in (0, 4): lput(l, 'lattice', -HX - 0.3, 0, 4.4, 90, G)
J = ['parque']
put('site', 0, 0, 0, 0, J); put('fence', 0, 0, 0, 0, J)
put('sign_board', -5.0, YL, 15.0, 0, J); put('mailboxes', 4.6, YG + 0.02, 14.7, 180, J); put('dumpster', -17.5, YL, 14.2, 0, J)
for z in (5.5, -6.5): put('speed_bump', 0, 0, z, 0, J)
for (x, z) in ((-3.2, 8.0), (3.2, 3.0), (-3.2, -1.0), (3.2, -8.0)): put('street_light', x, 0, z, 180 if x > 0 else 0, J + ['roof'])
for (x, z) in ((-20.5, -14.5), (-20.5, 3.6), (20.5, -2.8), (20.5, 14.5), (-6.0, -14.6), (6.5, 14.6), (-20.5, 12.5), (13.0, -14.6)): put('tree', x, YL, z, 0, J + ['roof'])
for (x, z) in ((-19.8, -5.5), (19.8, 6.0), (16.5, -14.8), (-14.5, 14.8)): put('tree_b', x, YL, z, 0, J + ['roof'])
for (x, z) in ((-7.4, 15.0), (-8.4, 15.1), (7.0, 14.9), (-21.0, 9.6), (21.0, -9.0), (21.0, 9.4)): put('bush', x, YL, z, 0, J)
put('player_scale_ref', 0.5, YA, 9.0, 0, J); lput(LOTS[1], 'player_scale_ref', -3.6, FL, 0.9, 0, ['lote2'])


if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'trailer_floor': FL, 'yard_level': YL, 'gravel_level': YG, 'road_level': YA,
                       'trailer': {'length': 2 * HX, 'width': 2 * HZ, 'wall_top': FL + WH, 'ceiling': FL + CH, 'front': '+Z local (porta)', 'hitch': '-X local'},
                       'lots': [{'x': l[0], 'z': l[1], 'rotY': l[2]} for l in LOTS], 'lane_x': list(LANE), 'site': {'x': [SX0, SX1], 'z': [SZ0, SZ1]},
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
