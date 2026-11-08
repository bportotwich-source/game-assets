"""Kit 47: concessionaria de carros seminovos (anos 70/80), em ALTO DETALHE (scripts/detalhe/detalhe.py).
Showroom de vidro de 14 x 10 m (montantes de aco escuro, faixa de chapa branca, cobertura em cunha com beiral largo e placa de
pictograma no teto) com 2 carros em exposicao (um no prato giratorio), mesa de vendas, sofa e, nos fundos, banheiro, sala de
fechamento e sala do gerente com frente de vidro e copa com porta para fora. Ao lado, a oficina de bloco pintado (10 x 10 m, 5,6 m)
com 2 portoes de enrolar, 2 elevadores de 2 colunas (um com carro levantado), bancada, armario de ferramentas, prateleira de pneus,
compressor, tambores e escritorio de pecas. Entre os dois, passagem coberta. Patio de asfalto com vagas pintadas, carros genericos
dos anos 70/80 em varias cores e 5 tipos (sedan, perua, cupe, picape, hatch), cartoes de preco sem texto no para-brisa, baloes,
bandeirolas entre os postes, bandeiras de pena, boneco inflavel, totem com pictograma de carro e painel de lampadas, calcada, rua.
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
CAR_COLS = {'car_r': (182, 46, 44), 'car_b': (58, 92, 150), 'car_g': (70, 120, 84), 'car_y': (226, 186, 70), 'car_w': (236, 234, 226),
            'car_k': (44, 46, 52), 'car_s': (176, 180, 184), 'car_o': (214, 112, 52), 'car_p': (104, 64, 110), 'car_t': (104, 170, 168)}
configurar(cores=dict({'render': (236, 234, 226), 'plaster': (240, 238, 232), 'ceil': (246, 246, 242), 'concrete': (186, 184, 178), 'conc_f': (170, 170, 166),
                       'panel_w': (240, 240, 236), 'mull': (58, 60, 64), 'block_d': (64, 66, 70), 'block_l': (214, 214, 208), 'coping': (226, 226, 222),
                       'metal': (186, 190, 194), 'frame': (190, 192, 196), 'gold': (184, 188, 192), 'chrome': (218, 222, 226), 'steel': (120, 126, 132),
                       'steel_d': (60, 64, 68), 'lift_r': (190, 48, 40), 'tool_r': (196, 52, 44), 'tile_a': (220, 220, 216), 'tile_b': (196, 198, 196),
                       'carpet': (112, 118, 132), 'tile': (228, 232, 232), 'porcelain': (244, 244, 240), 'mirror': (200, 214, 220), 'wood': (166, 122, 80),
                       'dkwood': (96, 66, 46), 'trim': (90, 92, 96), 'door_int': (196, 170, 130), 'lamp_glass': (255, 238, 196), 'neon_r': (255, 90, 80),
                       'paint_w': (240, 240, 236), 'paint_y': (232, 190, 50), 'yellowp': (238, 196, 54), 'asphalt': (66, 68, 70), 'curb': (196, 192, 184),
                       'grass': (100, 148, 70), 'leaf': (86, 132, 64), 'leaf2': (112, 150, 72), 'bark': (110, 84, 60), 'rubber': (28, 28, 30),
                       'dark': (34, 34, 36), 'vinyl': (70, 60, 56), 'vinyl_b': (60, 80, 120), 'fabric': (150, 120, 90), 'leather': (92, 58, 40),
                       'flag_r': (214, 54, 48), 'flag_y': (244, 196, 46), 'flag_b': (52, 104, 190), 'flag_g': (60, 156, 84), 'flag_o': (236, 126, 40),
                       'tube_g': (96, 196, 80), 'led': (255, 150, 50), 'sign_w': (246, 246, 240), 'oil': (40, 38, 36), 'drum_b': (40, 84, 150),
                       'paper': (238, 234, 222), 'plant': (70, 120, 60), 'pot': (176, 110, 80), 'roofm': (150, 152, 152)}, **CAR_COLS),
           texturas={'render': 'render', 'plaster': 'plaster', 'concrete': 'render', 'conc_f': 'render', 'asphalt': 'render', 'grass': 'render',
                     'block_d': 'stone', 'block_l': 'stone', 'curb': 'render', 'wood': 'planks', 'dkwood': 'planks', 'carpet': 'render'},
           out=OUT)
D.METAL.update({'metal', 'frame', 'chrome', 'steel', 'steel_d', 'gold', 'mull', 'coping', 'lift_r', 'tool_r'} | set(CAR_COLS)); MATS = D.MATS; TEX = D.TEX
for k in CAR_COLS:
    MATS[k].metallicFactor = 0.35; MATS[k].roughnessFactor = 0.3

# ============================================================================ medidas
W = 2.0; T = 0.25; t_ = 0.12                               # modulo, parede externa, parede interna
Y0 = 0.15                                                  # piso dos predios (patio em 0)
GY = -0.2
SX0_, SX1_, SZ0_, SZ1_ = -16.0, -2.0, -11.0, -1.0          # showroom
GX0, GX1, GZ0, GZ1 = 0.0, 10.0, -11.0, -1.0                # oficina
HB = 4.2; CEIL = 3.6; GL = 3.52                            # showroom: topo da faixa, forro, topo do vidro
HPG = 5.6; GDECK = 5.0                                     # oficina: platibanda e laje
ZOF = -7.8                                                 # frente das salas dos fundos do showroom
BAY_W, BAY_H = 3.4, 3.6                                    # vao dos portoes de enrolar
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

# ============================================================================ pictogramas (sem texto)
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

# ============================================================================ showroom: modulos de 2 m (pivo: face externa, cota do piso; dentro em -Z)
def sr_core(p, holes, xa, xb, solid=False):
    xs = sorted(set([xa, xb] + [v for h in holes for v in h[:2] if xa < v < xb]))
    ys = sorted(set([-Y0, 0.0, 0.2, CEIL, HB] + [v for h in holes for v in h[2:]]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if cy < 0: return 'concrete'
        if cy > CEIL: return 'panel_w' if k == 1 else 'plaster'
        if cy < 0.2: return 'block_d' if k == 1 else 'plaster'
        return ('render' if k == 1 else 'plaster') if solid else None
    for m, mesh in grid_solid(xs, ys, [-T, -0.15, 0.0], cell).items(): p.add(m, mesh)
    # pingadeira sob a faixa de chapa
    p.box('panel_w', xa, xb, CEIL - 0.04, CEIL + 0.02, 0.0, 0.05)
def glazing(p, a, b, y0, y1, trans=2.6, caps=(True, True)):
    """Vidraca de piso a forro: montantes de aco escuro de 5 cm (meio montante nas pontas do modulo), travessa e tampas de pressao."""
    f = 0.05
    for (x0, x1, on) in ((a, a + f, caps[0]), (b - f, b, caps[1])):
        p.box('mull', x0, x1, y0, y1, -0.2, 0.0)
        if on: p.box('mull', x0, x1, y0, min(y1, CEIL - 0.04), 0.0, 0.03)
    p.box('mull', a + f, b - f, y0, y0 + 0.06, -0.2, 0.0); p.box('mull', a + f, b - f, y1 - 0.05, y1, -0.2, 0.0)
    if trans: p.box('mull', a + f, b - f, trans - 0.03, trans + 0.03, -0.2, 0.0); p.box('mull', a + f, b - f, trans - 0.025, trans + 0.025, 0.0, 0.025)
    p.box('glass', a + f - 0.004, b - f + 0.004, y0 + 0.056, y1 - 0.046, -0.106, -0.094)
def sr_mod(kind='win', tl=0.0, tr_=0.0):
    """win (vidro de piso a forro), door2 (porta dupla de vidro com bandeira), door1 (porta de vidro com vidros laterais),
    plain (reboco), win_s (janela de aluminio no reboco), door_s (porta de servico de chapa)."""
    p = Piece(); xa, xb = -W / 2 + tl, W / 2 - tr_
    if kind == 'win':
        sr_core(p, [(xa, xb, 0.2, CEIL)], xa, xb); glazing(p, xa, xb, 0.2, CEIL, caps=(tl == 0, tr_ == 0))
    elif kind == 'door2':
        sr_core(p, [(xa, xb, 0.2, CEIL), (-0.92, 0.92, 0.0, 0.2)], xa, xb)
        f = 0.05
        for (x0, x1) in ((xa, xa + f), (xb - f, xb)): p.box('mull', x0, x1, 0.2, CEIL, -0.2, 0.0); p.box('mull', x0, x1, 0.2, CEIL - 0.04, 0.0, 0.03)
        for (x0, x1) in ((xa + f, -0.92), (0.92, xb - f)):
            if x1 - x0 > 0.01: p.box('mull', x0, x1, 0.2, 0.26, -0.2, 0.0)
        for s in (-1, 1):
            a, b = sorted((s * 0.92, s * 0.97)); p.box('mull', a, b, 0.2, 2.4, -0.2, 0.0)
        p.box('mull', xa + f, xb - f, 2.4, 2.46, -0.2, 0.0); p.box('mull', xa + f, xb - f, CEIL - 0.05, CEIL, -0.2, 0.0)
        p.box('glass', xa + f - 0.004, xb - f + 0.004, 2.456, CEIL - 0.046, -0.106, -0.094)
        p.cham('steel', -0.92, 0.92, -0.02, 0.006, -T + 0.004, 0.03, 0.003)
    elif kind == 'door1':
        sr_core(p, [(xa, xb, 0.2, CEIL), (-0.46, 0.46, 0.0, 0.2)], xa, xb)
        f = 0.05
        for (x0, x1, on) in ((xa, xa + f, tl == 0), (xb - f, xb, tr_ == 0)):
            p.box('mull', x0, x1, 0.2, CEIL, -0.2, 0.0)
            if on: p.box('mull', x0, x1, 0.2, CEIL - 0.04, 0.0, 0.03)
        for s in (-1, 1):
            a, b = sorted((s * 0.46, s * 0.51)); p.box('mull', a, b, 0.2, CEIL - 0.05, -0.2, 0.0)
        for (x0, x1) in ((xa + f, -0.51), (0.51, xb - f)):
            p.box('mull', x0, x1, 0.2, 0.26, -0.2, 0.0); p.box('mull', x0, x1, 2.37, 2.43, -0.2, 0.0)
            p.box('glass', x0 - 0.004, x1 + 0.004, 0.256, 2.374, -0.106, -0.094); p.box('glass', x0 - 0.004, x1 + 0.004, 2.426, CEIL - 0.046, -0.106, -0.094)
        p.box('mull', -0.46, 0.46, 2.4, 2.46, -0.2, 0.0); p.box('mull', xa + f, xb - f, CEIL - 0.05, CEIL, -0.2, 0.0)
        p.box('glass', -0.464, 0.464, 2.456, CEIL - 0.046, -0.106, -0.094)
        p.cham('steel', -0.46, 0.46, -0.02, 0.006, -T + 0.004, 0.03, 0.003)
    else:
        holes = {'win_s': [(-0.6, 0.6, 1.0, 2.2)], 'door_s': [(-0.46, 0.46, 0.0, 2.15)]}.get(kind, [])
        sr_core(p, holes, xa, xb, solid=True)
        if kind == 'win_s':
            alu_frame(p, -0.6, 0.6, 1.0, 2.2, f=0.045, z0=-0.17, z1=-0.08, mulls=(0.0,))
            p.box('glass', -0.556, 0.556, 1.044, 2.156, -0.128, -0.122)
            prof_x(p, 'coping', -0.64, 0.64, [(-0.08, 0.96), (0.05, 0.96), (0.06, 0.975), (0.06, 0.99), (-0.08, 1.004)])
            p.cham('wood', -0.62, 0.62, 0.97, 1.004, -T - 0.04, -0.15, 0.005)
        if kind == 'door_s':
            p.box('steel_d', -0.46, -0.41, 0.0, 2.15, -0.18, -0.06); p.box('steel_d', 0.41, 0.46, 0.0, 2.15, -0.18, -0.06); p.box('steel_d', -0.41, 0.41, 2.1, 2.15, -0.18, -0.06)
            p.cham('concrete', -0.46, 0.46, -0.02, 0.008, -T + 0.004, 0.03, 0.004); p.merge(wall_lamp(), tr(0.0, 2.45, 0.0))
    return p

# ============================================================================ oficina: modulos de bloco pintado (pivo: face externa, cota do piso)
def k_core(p, holes, xa, xb):
    xs = sorted(set([xa, xb] + [v for h in holes for v in h[:2] if xa < v < xb]))
    ys = sorted(set([-Y0, 0.0, 0.3, HPG] + [v for h in holes for v in h[2:]]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if cy < 0: return 'concrete'
        if k == 0: return 'block_l' if cy < GDECK else 'block_d'
        return 'concrete' if cy < 0.3 else 'block_d'
    for m, mesh in grid_solid(xs, ys, [-T, -0.15, 0.0], cell).items(): p.add(m, mesh)
def k_window(p, a, b, y0, y1):
    """Janela de oficina de perfil de aco com 3 x 2 vidros aramados, peitoril de concreto e verga."""
    p.box('steel_d', a, a + 0.05, y0, y1, -0.16, -0.08); p.box('steel_d', b - 0.05, b, y0, y1, -0.16, -0.08)
    p.box('steel_d', a + 0.05, b - 0.05, y0, y0 + 0.05, -0.16, -0.08); p.box('steel_d', a + 0.05, b - 0.05, y1 - 0.05, y1, -0.16, -0.08)
    for k in (1, 2): x = a + k * (b - a) / 3; p.box('steel_d', x - 0.015, x + 0.015, y0 + 0.05, y1 - 0.05, -0.15, -0.09)
    p.box('steel_d', a + 0.05, b - 0.05, (y0 + y1) / 2 - 0.015, (y0 + y1) / 2 + 0.015, -0.15, -0.09)
    p.box('glass', a + 0.046, b - 0.046, y0 + 0.046, y1 - 0.046, -0.123, -0.117)
    prof_x(p, 'concrete', a - 0.06, b + 0.06, [(-0.08, y0 - 0.06), (0.06, y0 - 0.06), (0.06, y0 - 0.02), (-0.08, y0 + 0.002)])
    p.box('concrete', a - 0.06, b + 0.06, y1, y1 + 0.2, 0.0, 0.02)
def k_mod(kind='plain', tl=0.0, tr_=0.0):
    """plain, win (janela de aco), door (porta de chapa com capuz e arandela), bay (modulo de 4 m com portao de enrolar aberto),
    bay_half (portao meio baixado ate 2,5 m)."""
    p = Piece(); hw = 2.0 if kind.startswith('bay') else 1.0; xa, xb = -hw + tl, hw - tr_
    if kind == 'win':
        k_core(p, [(-0.8, 0.8, 1.4, 2.6)], xa, xb); k_window(p, -0.8, 0.8, 1.4, 2.6)
    elif kind == 'win_n':
        k_core(p, [(-0.5, 0.5, 1.4, 2.6)], xa, xb); k_window(p, -0.5, 0.5, 1.4, 2.6)
    elif kind == 'door':
        k_core(p, [(-0.48, 0.48, 0.0, 2.2)], xa, xb)
        p.box('steel_d', -0.48, -0.43, 0.0, 2.2, -0.18, -0.06); p.box('steel_d', 0.43, 0.48, 0.0, 2.2, -0.18, -0.06); p.box('steel_d', -0.43, 0.43, 2.15, 2.2, -0.18, -0.06)
        p.cham('concrete', -0.48, 0.48, -0.02, 0.008, -T + 0.004, 0.03, 0.004)
        p.hull('steel_d', [(x, y, z) for x in (-0.7, 0.7) for (y, z) in ((2.35, 0.0), (2.35, 0.6), (2.42, 0.6), (2.6, 0.0))])
        p.merge(wall_lamp(), tr(0.75, 2.0, 0.0))
    elif kind.startswith('bay'):
        a, b = -BAY_W / 2, BAY_W / 2
        k_core(p, [(a, b, -0.2, BAY_H)], xa, xb)
        p.cham('concrete', a, b, -0.05, 0.0, -T, 0.0, 0.004)
        for s in (-1, 1):
            x0, x1 = sorted((s * BAY_W / 2, s * (BAY_W / 2 + 0.1)))
            p.box('steel_d', x0, x1, 0.0, BAY_H + 0.1, -T - 0.1, -T)                       # trilho do portao
            x0, x1 = sorted((s * BAY_W / 2, s * (BAY_W / 2 - 0.03)))
            p.box('paint_y', x0, x1, 0.0, 1.2, -T, 0.0)                                    # cantoneira pintada no batente
        p.hull('steel_d', [(x, y, z) for x in (a - 0.12, b + 0.12) for (y, z) in ((BAY_H + 0.02, -T), (BAY_H + 0.02, -T - 0.5), (BAY_H + 0.52, -T - 0.5), (BAY_H + 0.52, -T))])
        p.box('steel', b + 0.12, b + 0.3, BAY_H + 0.1, BAY_H + 0.4, -T - 0.4, -T - 0.1)    # motor
        yb = 2.5 if kind == 'bay_half' else BAY_H - 0.02
        if yb < BAY_H - 0.05:
            for y in np.arange(yb, BAY_H - 0.01, 0.1):
                p.hull('paint_w', [(x, yy, z) for x in (a - 0.05, b + 0.05) for (yy, z) in ((y + 0.004, -T - 0.07), (y + 0.096, -T - 0.07), (y + 0.05, -T - 0.035), (y + 0.05, -T - 0.085))])
            p.box('steel', a - 0.05, b + 0.05, yb - 0.04, yb + 0.004, -T - 0.09, -T - 0.03)
            for x in (-0.6, 0.6): p.box('steel', x - 0.08, x + 0.08, yb + 0.1, yb + 0.14, -T - 0.11, -T - 0.07)
    else:
        k_core(p, [], xa, xb)
    return p

# ============================================================================ coberturas (pivo: origem, cota do piso)
SRB = sbox(SX0_, SZ0_, SX1_, SZ1_); SRI = off(SRB, -T)
GB = sbox(GX0, GZ0, GX1, GZ1); GI = off(GB, -T)
RX0, RX1, RZ0, RZ1 = SX0_ - 0.6, SX1_ + 0.6, SZ0_ - 0.6, SZ1_ + 1.6
def roof_y(z): return 4.55 + (z - RZ0) / (RZ1 - RZ0) * 0.45
def sr_roof():
    """Forro com luminarias embutidas, cobertura em cunha de chapa branca com beiral largo (1,6 m na frente), manta, rufo escuro,
    calha nos fundos com 2 condutores, luzes no beiral e placa de pictograma de carro num mastro."""
    p = Piece()
    ext_y(p, 'ceil', SRI, CEIL, CEIL + 0.03)
    for x in np.arange(-15.0, -2.4, 2.0):
        for z in (-6.6, -4.2, -2.0) + ((-9.3,) if True else ()):
            if z < ZOF and min(abs(x - xx) for xx in (-13.0, -9.6, -5.6)) < 0.5: continue
            p.box('frame', x - 0.34, x + 0.34, CEIL - 0.006, CEIL, z - 0.34, z + 0.34); p.box('lamp_glass', x - 0.3, x + 0.3, CEIL - 0.008, CEIL - 0.002, z - 0.3, z + 0.3)
    top = lambda z: roof_y(z)
    p.hull('panel_w', [(x, y, z) for x in (RX0, RX1) for z in (RZ0, RZ1) for y in (HB, top(z))])
    i = 0.16
    p.hull('roofm', [(x, y, z) for x in (RX0 + i, RX1 - i) for z in (RZ0 + i, RZ1 - i) for y in (top(z) - 0.02, top(z) + 0.012)])
    for (x0, x1, z0, z1) in ((RX0 - 0.02, RX1 + 0.02, RZ0 - 0.02, RZ0 + 0.18), (RX0 - 0.02, RX1 + 0.02, RZ1 - 0.18, RZ1 + 0.02),
                             (RX0 - 0.02, RX0 + 0.18, RZ0 + 0.18, RZ1 - 0.18), (RX1 - 0.18, RX1 + 0.02, RZ0 + 0.18, RZ1 - 0.18)):
        p.hull('mull', [(x, y, z) for x in (x0, x1) for z in (z0, z1) for y in (top(z) - 0.06, top(z) + 0.03)])
    p.box('coping', RX0 + 0.1, RX1 - 0.1, 4.22, 4.42, RZ0 - 0.16, RZ0 - 0.02)
    for x in (RX0 + 0.3, RX1 - 0.3):
        seg_cyl(p, 'coping', (x, 4.24, RZ0 - 0.09), (x, 3.9, SZ0_ - 0.07), 0.045, 10); seg_cyl(p, 'coping', (x, 3.9, SZ0_ - 0.07), (x, -0.05, SZ0_ - 0.07), 0.045, 10)
        p.box('coping', x - 0.06, x + 0.06, 3.0, 3.04, SZ0_ - 0.13, SZ0_); p.box('coping', x - 0.06, x + 0.06, 1.2, 1.24, SZ0_ - 0.13, SZ0_)
    for x in np.arange(-15.0, -2.0, 2.0): p.cyl('lamp_glass', 0.08, HB - 0.006, HB, x, 0.0, 16); p.cyl('frame', 0.1, HB - 0.004, HB, x, 0.0, 16) if False else None
    # placa no teto
    x, z = -3.2, -2.4; yb = top(z)
    for s in (-1, 1): p.box('steel', x + s * 0.4 - 0.05, x + s * 0.4 + 0.05, yb - 0.05, yb + 2.0, z - 0.05, z + 0.05)
    p.cham('sign_w', x - 0.75, x + 0.75, yb + 1.0, yb + 2.5, z - 0.2, z + 0.2, 0.03)
    p.box('mull', x - 0.78, x + 0.78, yb + 0.97, yb + 1.03, z - 0.22, z + 0.22); p.box('mull', x - 0.78, x + 0.78, yb + 2.47, yb + 2.53, z - 0.22, z + 0.22)
    for s in (-1, 1): picto_car(p, 'dark', x, yb + 1.78, 1.1, *sorted((z + s * 0.2, z + s * 0.212)))
    return p
def link_roof():
    """Passagem coberta entre o showroom e a oficina: laje fina com testeira branca, rufo e luz embaixo."""
    p = Piece(); p.box('panel_w', SX1_, GX0, 3.0, 3.25, -3.4, -0.6); p.box('mull', SX1_, GX0, 3.25, 3.29, -3.4, -0.6)
    p.cyl('lamp_glass', 0.1, 2.994, 3.0, -1.0, -2.0, 16); return p
def g_roof():
    """Oficina: laje de cobertura sobre vigas treliçadas aparentes, rufo da platibanda, 2 claraboias, ar-condicionado e chamine."""
    p = Piece()
    ext_y(p, 'metal', GI, GDECK - 0.01, GDECK); ext_y(p, 'concrete', GI, GDECK, GDECK + 0.2); ext_y(p, 'roofm', GI, GDECK + 0.2, GDECK + 0.215)
    ext_y(p, 'coping', off(GB, 0.04).difference(off(GB, -T - 0.04)), HPG, HPG + 0.06)
    for x in (2.0, 4.0, 6.0, 8.0):
        z0, z1 = GZ0 + T, GZ1 - T
        p.box('steel_d', x - 0.06, x + 0.06, GDECK - 0.07, GDECK - 0.01, z0, z1); p.box('steel_d', x - 0.06, x + 0.06, GDECK - 0.62, GDECK - 0.56, z0 + 0.3, z1 - 0.3)
        zs = np.linspace(z0 + 0.3, z1 - 0.3, 17)
        for k in range(len(zs) - 1):
            ya, yb_ = (GDECK - 0.56, GDECK - 0.07) if k % 2 == 0 else (GDECK - 0.07, GDECK - 0.56)
            seg_cyl(p, 'steel_d', (x, ya, zs[k]), (x, yb_, zs[k + 1]), 0.015, 6)
        for z in (z0, z1 - 0.3): p.box('steel_d', x - 0.06, x + 0.06, GDECK - 0.62, GDECK - 0.07, z, z + 0.3)
    for (x, z) in ((3.0, -6.0), (7.0, -4.0)):
        p.box('coping', x - 0.7, x + 0.7, GDECK + 0.215, GDECK + 0.45, z - 0.7, z + 0.7)
        p.hull('glass', [(x + a, GDECK + 0.45, z + b) for a in (-0.66, 0.66) for b in (-0.66, 0.66)] + [(x + a, GDECK + 0.75, z + b) for a in (-0.3, 0.3) for b in (-0.3, 0.3)])
    x, z = 6.0, -8.0
    p.box('concrete', x - 1.2, x + 1.2, GDECK + 0.215, GDECK + 0.35, z - 0.9, z + 0.9); p.cham('metal', x - 1.0, x + 1.0, GDECK + 0.35, GDECK + 1.35, z - 0.7, z + 0.7, 0.02)
    for k in range(9): xx = x - 0.9 + k * 0.225; p.box('dark', xx, xx + 0.12, GDECK + 0.45, GDECK + 1.25, z + 0.7, z + 0.712)
    p.cyl('dark', 0.42, GDECK + 1.35, GDECK + 1.36, x, z, 24)
    for k in range(4): ring_y(p, 'steel', 0.42 - k * 0.1 - 0.02, 0.42 - k * 0.1, GDECK + 1.36, GDECK + 1.38, x, z, 24)
    seg_cyl(p, 'metal', (x - 1.0, GDECK + 0.6, z - 0.3), (x - 1.6, GDECK + 0.6, z - 0.3), 0.08, 10)
    p.cyl('metal', 0.12, GDECK + 0.215, GDECK + 1.6, 1.2, -9.6, 14); lathe(p, 'metal', [(0.0, GDECK + 1.85), (0.22, GDECK + 1.68), (0.18, GDECK + 1.64)], 1.2, -9.6, 0.0, 14)
    return p
def svc_sign():
    """Caixa luminosa com pictograma de chave inglesa sobre os portoes (pivo: face da parede da frente, cota do piso)."""
    p = Piece(); p.cham('sign_w', -1.2, 1.2, 4.0, 5.0, 0.0, 0.25, 0.02); p.box('mull', -1.23, 1.23, 3.97, 4.03, 0.002, 0.27); p.box('mull', -1.23, 1.23, 4.97, 5.03, 0.002, 0.27)
    picto_wrench(p, 'dark', -0.55, 4.5, 0.75, 0.25, 0.262); picto_car(p, 'dark', 0.45, 4.48, 1.0, 0.25, 0.262)
    for x in (-0.8, 0.8): seg_cyl(p, 'steel', (x, 5.05, 0.1), (x, 5.25, 0.0), 0.02, 6); p.cham('metal', x - 0.12, x + 0.12, 3.82, 3.9, 0.0, 0.3, 0.01)
    return p

# ============================================================================ pisos e paredes internas (pivo: origem, cota do piso)
HALL_S = SRI.intersection(sbox(-99, ZOF, 99, 99))
WC_R = sbox(SX0_ + T, SZ0_ + T, -13.0, ZOF); CLO_R = sbox(-13.0, SZ0_ + T, -9.6, ZOF); MGR_R = sbox(-9.6, SZ0_ + T, -5.6, ZOF); COPA_R = sbox(-5.6, SZ0_ + T, SX1_ - T, ZOF)
OFF_G = sbox(7.0, GZ0 + T, GX1 - T, -8.0)
def checker(p, poly, y0, y1, step, ma, mb, ox=0.0, oz=0.0):
    b = poly.bounds
    for i in range(int(math.floor((b[0] - ox) / step)), int(math.ceil((b[2] - ox) / step))):
        for j in range(int(math.floor((b[1] - oz) / step)), int(math.ceil((b[3] - oz) / step))):
            q = sbox(ox + i * step, oz + j * step, ox + (i + 1) * step, oz + (j + 1) * step).intersection(poly)
            if q.area > 1e-6: ext_y(p, ma if (i + j) % 2 == 0 else mb, q, y0, y1)
def sr_floor():
    """Showroom: porcelanato de 60 cm em 2 tons, carpete nas salas, ladrilho no banheiro e na copa."""
    p = Piece(); ext_y(p, 'concrete', SRI, -Y0 + 0.02, -0.012)
    checker(p, HALL_S, -0.012, 0.0, 0.6, 'tile_a', 'tile_b', 0.0, 0.0)
    ext_y(p, 'carpet', unary_union([CLO_R, MGR_R]).buffer(0), -0.012, 0.0)
    checker(p, WC_R, -0.012, 0.0, 0.2, 'tile', 'porcelain'); checker(p, COPA_R, -0.012, 0.0, 0.3, 'tile', 'tile_b')
    return p
def g_floor():
    """Oficina: concreto alisado com faixas amarelas das baias, ralos e manchas de oleo."""
    p = Piece(); ext_y(p, 'conc_f', GI, -Y0 + 0.02, 0.0)
    for xc in (2.0, 6.0):
        for s in (-1, 1): p.box('paint_y', xc + s * 1.9 - 0.05, xc + s * 1.9 + 0.05, 0.0, 0.002, -8.4, -1.4)
        p.box('dark', xc - 0.3, xc + 0.3, 0.0, 0.002, -2.0, -1.85)
        for k in range(6): p.box('steel', xc - 0.28, xc + 0.28, 0.0, 0.004, -1.98 + k * 0.022, -1.968 + k * 0.022)
    for (x, z, r) in ((2.3, -6.2, 0.5), (1.6, -4.5, 0.3), (6.4, -3.6, 0.4), (5.2, -9.0, 0.35)): p.cyl('oil', r, 0.0, 0.0015, x, z, 20)
    ext_y(p, 'carpet', OFF_G, 0.0, 0.006)
    return p
def ring_base(rooms, cuts, h=0.1):
    """Rodape ao longo das paredes externas (anel de cada sala), sem as portas e sem os pes das divisorias."""
    p = Piece(); u = unary_union([r.difference(off(r, -0.016)) for r in rooms]).difference(cuts)
    ext_y(p, 'trim', u, 0.0, h); return p
def sr_plan():
    """Divisorias dos fundos do showroom (banheiro, sala de fechamento e sala do gerente com frente de vidro, copa), rodapes e forro
    alto nas salas."""
    p = Piece(); L1 = (SX1_ - T) - (SX0_ + T)
    cuts = [(1.35, 0.9, 0.0, 2.1, 'door'), (4.45, 0.9, 0.0, 2.1, 'door'), (5.55, 1.0, 0.9, 2.4, 'glaze'),
            (7.15, 0.9, 0.0, 2.1, 'door'), (8.85, 2.3, 0.9, 2.4, 'glaze'), (12.75, 0.9, 0.0, 2.1, 'door')]
    p.merge(run_wall(L1, CEIL, cuts), tr(SX0_ + T, 0, ZOF))
    for x in (-13.0, -9.6, -5.6): p.merge(run_wall(ZOF - (SZ0_ + T), CEIL), rot_y(-90, (x, 0, SZ0_ + T)))
    # rodape nas paredes externas (vidro nao tem)
    walls = unary_union([sbox(SX0_ + T, SZ0_ + T, SX1_ - T, SZ0_ + T + 0.03), sbox(SX0_ + T, SZ0_ + T, SX0_ + T + 0.03, ZOF), sbox(SX1_ - T - 0.03, SZ0_ + T, SX1_ - T, ZOF)])
    dr = unary_union([sbox(-3.0 - 0.47, SZ0_ + T - 0.1, -3.0 + 0.47, SZ0_ + T + 0.1)] + [sbox(x - 0.09, SZ0_, x + 0.09, ZOF + 0.1) for x in (-13.0, -9.6, -5.6)] + [sbox(-99, ZOF - 0.09, 99, ZOF + 0.09)])
    ext_y(p, 'trim', walls.intersection(unary_union([r.difference(off(r, -0.016)) for r in (WC_R, CLO_R, MGR_R, COPA_R)])).difference(dr), 0.0, 0.1)
    return p
def g_plan():
    """Escritorio de pecas no canto da oficina: divisoria com porta e visor de vidro, forro baixo."""
    p = Piece(); Lz = -8.0 - (GZ0 + T)
    p.merge(run_wall(Lz, 3.0, [(0.75, 0.9, 0.0, 2.1, 'door')]), rot_y(-90, (7.0, 0, GZ0 + T)))
    p.merge(run_wall(GX1 - T - 7.0, 3.0, [(1.55, 1.6, 1.0, 2.2, 'glaze')]), tr(7.0, 0, -8.0))
    ext_y(p, 'ceil', off(OFF_G, 0.06).intersection(GI), 3.0, 3.06)
    p.box('frame', 8.0, 8.9, 2.996, 3.0, -9.6, -9.2); p.box('lamp_glass', 8.04, 8.86, 2.994, 2.998, -9.56, -9.24)
    return p

# ============================================================================ moveis (pivo: chao; frente em +Z salvo indicado)
def desk(w=1.5, d=0.75):
    """Mesa de escritorio (pivo: centro, chao): tampo de madeira com borda, pes de aco, painel frontal, gaveteiro, telefone,
    papeis e porta-lapis. O lado de quem atende fica em -Z."""
    p = Piece(); x = w / 2; z = d / 2
    p.cham('wood', -x, x, 0.72, 0.75, -z, z, 0.006)
    for s in (-1, 1):
        p.box('steel_d', s * (x - 0.04) - 0.02, s * (x - 0.04) + 0.02, 0.0, 0.72, -z + 0.03, z - 0.03)
    p.box('steel_d', -x + 0.06, x - 0.06, 0.3, 0.7, z - 0.04, z - 0.02)
    p.cham('steel', x - 0.5, x - 0.08, 0.02, 0.7, -z + 0.04, z - 0.08, 0.008)
    for k in range(3): y = 0.06 + k * 0.215; p.box('chrome', x - 0.34, x - 0.24, y + 0.15, y + 0.17, -z + 0.035, -z + 0.04)
    p.cham('dark', -x + 0.15, -x + 0.37, 0.75, 0.8, -0.1, 0.1, 0.01); p.box('dark', -x + 0.16, -x + 0.36, 0.8, 0.83, -0.08, 0.0)
    for k in range(3): p.box('paper', -0.2 + k * 0.01, 0.1 + k * 0.01, 0.75 + k * 0.003, 0.752 + k * 0.003, -0.15 + k * 0.02, 0.15 + k * 0.02)
    p.cyl('dark', 0.035, 0.75, 0.85, x - 0.25, 0.15, 10)
    return p
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
def sofa(n=3, mat='vinyl_b'):
    """Sofa de courvin de linhas retas (pivo: centro de tras, chao; assento para +Z) com pes cromados."""
    p = Piece(); L1 = 0.62 * n + 0.3; x = L1 / 2
    p.cham(mat, -x, x, 0.12, 0.42, 0.0, 0.82, 0.03); p.cham(mat, -x, x, 0.42, 0.85, 0.0, 0.2, 0.03)
    for s in (-1, 1): p.cham(mat, *sorted((s * x, s * (x - 0.15))), 0.42, 0.62, 0.0, 0.82, 0.03)
    for i in range(n):
        a = -x + 0.15 + i * 0.62 + 0.01; b = a + 0.6; p.cham(mat, a, b, 0.42, 0.52, 0.2, 0.8, 0.04); p.cham(mat, a, b, 0.52, 0.82, 0.2, 0.32, 0.04)
    for (a, c) in ((-x + 0.08, 0.08), (x - 0.08, 0.08), (-x + 0.08, 0.74), (x - 0.08, 0.74)): p.cyl('chrome', 0.025, 0.0, 0.12, a, c, 8)
    return p
def side_table():
    p = Piece(); p.cyl('chrome', 0.2, 0.0, 0.02, 0, 0, 20); p.cyl('chrome', 0.025, 0.02, 0.5, 0, 0, 8); p.cyl('glass', 0.3, 0.5, 0.52, 0, 0, 28)
    for k in range(3): p.box('flag_' + 'rybg'[k], -0.14 + k * 0.02, 0.1 + k * 0.02, 0.52 + k * 0.004, 0.524 + k * 0.004, -0.1 - k * 0.02, 0.12 - k * 0.02)
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
def brochure_rack():
    """Expositor de folhetos (pivo: centro de tras, chao; para +Z): 3 prateleiras inclinadas com folhetos coloridos sem texto."""
    p = Piece()
    for s in (-1, 1): p.box('chrome', s * 0.3 - 0.012, s * 0.3 + 0.012, 0.0, 1.5, 0.0, 0.03); seg_cyl(p, 'chrome', (s * 0.3, 0.0, 0.015), (s * 0.3, 0.0, 0.35), 0.012, 6)
    p.box('chrome', -0.3, 0.3, 1.45, 1.48, 0.0, 0.03)
    cols = ['flag_r', 'flag_b', 'flag_y', 'flag_g', 'paint_w', 'flag_o']
    for j, y in enumerate((0.45, 0.85, 1.25)):
        p.hull('chrome', [(x, y, 0.03) for x in (-0.3, 0.3)] + [(x, y - 0.06, 0.14) for x in (-0.3, 0.3)] + [(x, y - 0.075, 0.14) for x in (-0.3, 0.3)] + [(x, y - 0.015, 0.03) for x in (-0.3, 0.3)])
        for i in range(3):
            x = -0.2 + i * 0.2; c = cols[(i + j * 2) % 6]
            p.hull(c, [(x + a, y - 0.04 + b * 0.25, 0.1 - b * 0.05 + e) for a in (-0.085, 0.085) for b in (0.0, 1.0) for e in (0.0, 0.01)])
    return p
def water_cooler():
    p = Piece(); p.cham('paint_w', -0.17, 0.17, 0.0, 1.0, -0.17, 0.17, 0.02); p.box('dark', -0.1, 0.1, 0.78, 0.86, 0.17, 0.2)
    lathe(p, 'glass', [(0.0, 1.0), (0.13, 1.03), (0.14, 1.12), (0.14, 1.36), (0.12, 1.42), (0.0, 1.44)], sec=16)
    for x in (-0.05, 0.05): p.box('flag_' + ('b' if x < 0 else 'r'), x - 0.02, x + 0.02, 0.8, 0.84, 0.2, 0.24)
    return p
def bookcase(L1=1.6, h=2.0, d=0.35):
    """Estante de madeira com fichario colorido e caixas (pivo: centro de tras, chao; para +Z)."""
    p = Piece(); x = L1 / 2; rng = np.random.default_rng(9)
    p.box('dkwood', -x, x, 0.0, h, 0.0, 0.02)
    for s in (-1, 1): p.box('dkwood', *sorted((s * x, s * (x - 0.025))), 0.0, h, 0.02, d)
    for y in np.linspace(0.06, h - 0.025, 5): p.box('dkwood', -x + 0.025, x - 0.025, y - 0.025, y, 0.02, d)
    cols = ['flag_r', 'flag_b', 'flag_g', 'flag_y', 'dark', 'paint_w']
    for y in np.linspace(0.06, h - 0.025, 5)[:-1]:
        xx = -x + 0.04
        while xx < x - 0.12:
            wd = rng.uniform(0.05, 0.08); hh = rng.uniform(0.24, 0.32); p.box(cols[rng.integers(6)], xx, xx + wd - 0.004, y, y + hh, 0.04, d - 0.04); xx += wd
            if rng.random() < 0.12: xx += 0.12
    return p
def kitchenette(L1=2.0):
    """Bancada da copa (pivo: centro de tras, chao; para +Z): armarios com puxadores, tampo, cuba, torneira, cafeteira, micro-ondas
    e armarios altos."""
    p = Piece(); x = L1 / 2
    p.box('dark', -x + 0.02, x - 0.02, 0.0, 0.1, 0.0, 0.52); p.box('paint_w', -x, x, 0.1, 0.86, 0.0, 0.55)
    n = int(round(L1 / 0.5))
    for i in range(n):
        a = -x + i * L1 / n + 0.006; b = -x + (i + 1) * L1 / n - 0.006; p.box('paint_w', a, b, 0.14, 0.84, 0.55, 0.57); p.box('chrome', b - 0.06, b - 0.04, 0.66, 0.8, 0.57, 0.59)
    p.cham('dkwood', -x - 0.01, x + 0.01, 0.86, 0.9, 0.0, 0.6, 0.006)
    p.box('chrome', -0.55, -0.15, 0.82, 0.901, 0.12, 0.45); p.box('dark', -0.52, -0.18, 0.8, 0.902, 0.15, 0.42)
    seg_cyl(p, 'chrome', (-0.35, 0.9, 0.06), (-0.35, 1.15, 0.06), 0.012, 6); seg_cyl(p, 'chrome', (-0.35, 1.15, 0.06), (-0.35, 1.1, 0.24), 0.01, 6)
    p.cham('dark', 0.15, 0.4, 0.9, 1.3, 0.1, 0.38, 0.02); p.cyl('glass', 0.06, 0.92, 1.08, 0.27, 0.3, 12)
    p.cham('paint_w', 0.5, 0.95, 0.9, 1.18, 0.05, 0.42, 0.02); p.box('dark', 0.54, 0.82, 0.94, 1.14, 0.42, 0.425)
    p.box('paint_w', -x, x, 1.45, 2.15, 0.0, 0.35)
    for i in range(n):
        a = -x + i * L1 / n + 0.006; b = -x + (i + 1) * L1 / n - 0.006; p.box('paint_w', a, b, 1.47, 2.13, 0.35, 0.37); p.box('chrome', b - 0.06, b - 0.04, 1.5, 1.62, 0.37, 0.39)
    return p
def fridge():
    p = Piece(); p.cham('paint_w', -0.33, 0.33, 0.0, 1.7, 0.0, 0.66, 0.03)
    p.box('paint_w', -0.32, 0.32, 1.18, 1.68, 0.66, 0.69); p.box('paint_w', -0.32, 0.32, 0.04, 1.16, 0.66, 0.69)
    for (y0, y1) in ((1.25, 1.5), (0.7, 1.05)): p.box('chrome', 0.24, 0.27, y0, y1, 0.69, 0.72)
    return p
def table_set():
    """Mesa redonda com 2 cadeiras (pivo: centro, chao)."""
    p = Piece(); p.cyl('chrome', 0.25, 0.0, 0.02, 0, 0, 20); p.cyl('chrome', 0.03, 0.02, 0.72, 0, 0, 10); p.cyl('paint_w', 0.45, 0.72, 0.75, 0, 0, 28)
    for s in (-1, 1): p.merge(guest_chair('vinyl'), rot_y(90 if s > 0 else -90, (s * 0.65, 0, 0)))
    p.cyl('paint_w', 0.04, 0.75, 0.84, 0.1, 0.1, 12)
    return p
def turntable(r=2.2):
    """Prato giratorio do showroom (pivo: centro, piso): base de aco com aro cromado, tampo de porcelanato escuro e luzes no rodape."""
    p = Piece(); p.cyl('steel_d', r, 0.0, 0.09, 0, 0, 64); p.cyl('dark', r - 0.02, 0.09, 0.12, 0, 0, 64)
    ring_y(p, 'chrome', r, r + 0.03, 0.0, 0.125, 0, 0, 64)
    for k in range(24): a = k * 2 * math.pi / 24; p.box('lamp_glass', r * math.cos(a) - 0.03, r * math.cos(a) + 0.03, 0.03, 0.05, r * math.sin(a) - 0.03, r * math.sin(a) + 0.03) if False else None
    for k in range(24):
        a = k * 2 * math.pi / 24; c = np.array([(r + 0.031) * math.cos(a), 0.04, (r + 0.031) * math.sin(a)])
        p.hull('lamp_glass', [c + np.array([dx * -math.sin(a), dy, dx * math.cos(a)]) + np.array([e * math.cos(a), 0, e * math.sin(a)]) for dx in (-0.04, 0.04) for dy in (-0.012, 0.012) for e in (-0.002, 0.006)])
    return p
def stanchion():
    """Pedestal de corda de veludo (pivo: centro, chao)."""
    p = Piece(); p.cyl('chrome', 0.15, 0.0, 0.03, 0, 0, 20); p.cyl('chrome', 0.025, 0.03, 0.95, 0, 0, 10); p.sphere('chrome', 0.045, 0, 0.98, 0, 1); return p

# ============================================================================ oficina (pivo: chao)
def lift(h=2.05):
    """Elevador automotivo de 2 colunas (pivo: centro entre as colunas, chao; colunas em +-X): colunas vermelhas, viga superior,
    carros nas colunas, 4 bracos telescopicos com sapatas na altura h, unidade hidraulica e mangueira."""
    p = Piece(); cx = 1.45
    for s in (-1, 1):
        x = s * cx; p.box('steel_d', x - 0.3, x + 0.3, 0.0, 0.015, -0.35, 0.35); p.box('lift_r', x - 0.14, x + 0.14, 0.015, 3.75, -0.14, 0.14)
        p.box('steel_d', x - 0.18, x + 0.18, h - 0.32, h - 0.02, -0.18, 0.18)
        for zs in (-1, 1):
            tip = (s * 0.5, h - 0.06, zs * (1.25 if zs > 0 else 1.35))
            seg_cyl(p, 'steel', (x - s * 0.18, h - 0.06, zs * 0.12), tip, 0.04, 8)
            p.cyl('rubber', 0.08, h - 0.03, h, tip[0], tip[2], 14); p.cyl('steel_d', 0.05, h - 0.06, h - 0.03, tip[0], tip[2], 10)
    p.box('lift_r', -cx - 0.14, cx + 0.14, 3.75, 3.92, -0.12, 0.12)
    p.box('steel_d', -cx - 0.42, -cx - 0.14, 1.0, 1.5, -0.12, 0.12); p.cyl('dark', 0.1, 1.5, 1.75, -cx - 0.28, 0.0, 12)
    seg_cyl(p, 'dark', (-cx - 0.2, 1.5, 0.13), (-cx, 3.83, 0.13), 0.012, 6); seg_cyl(p, 'dark', (-cx, 3.83, 0.13), (cx, 3.83, 0.13), 0.012, 6)
    p.box('paint_y', -cx - 0.14, -cx + 0.14, 0.015, 0.4, 0.14, 0.145); p.box('paint_y', cx - 0.14, cx + 0.14, 0.015, 0.4, 0.14, 0.145)
    return p
def workbench(L1=2.0):
    """Bancada de oficina (pivo: centro de tras, chao; para +Z): estrutura de aco, tampo de madeira, prateleira de baixo, morsa, painel
    perfurado com ferramentas, luminaria e tomadas."""
    p = Piece(); x = L1 / 2
    p.cham('wood', -x, x, 0.86, 0.92, 0.0, 0.72, 0.006)
    for (a, c) in ((-x + 0.05, 0.05), (x - 0.05, 0.05), (-x + 0.05, 0.67), (x - 0.05, 0.67)): p.box('steel_d', a - 0.025, a + 0.025, 0.0, 0.86, c - 0.025, c + 0.025)
    p.box('steel_d', -x + 0.03, x - 0.03, 0.2, 0.23, 0.05, 0.69)
    for k in range(3): p.cham('drum_b', -x + 0.1 + k * 0.4, -x + 0.45 + k * 0.4, 0.23, 0.5, 0.15, 0.55, 0.02)
    p.box('dkwood', -x, x, 1.0, 1.9, 0.0, 0.02)
    for i in range(24):
        for j in range(10): p.box('dark', -x + 0.05 + i * 0.08, -x + 0.06 + i * 0.08, 1.04 + j * 0.085, 1.05 + j * 0.085, 0.02, 0.021)
    for k in range(5):
        xx = -x + 0.25 + k * 0.18; p.box('steel', xx - 0.012, xx + 0.012, 1.25, 1.55 + k * 0.03, 0.03, 0.05)
        p.cyl('steel', 0.035, 1.55 + k * 0.03, 1.56 + k * 0.03, xx, 0.04, 10)
    p.box('dkwood', 0.2, 0.24, 1.2, 1.5, 0.03, 0.06); p.box('steel_d', 0.12, 0.32, 1.5, 1.58, 0.03, 0.08)
    for k in range(4): xx = 0.5 + k * 0.1; p.box('tool_r', xx - 0.015, xx + 0.015, 1.25, 1.45, 0.03, 0.06); p.box('steel', xx - 0.005, xx + 0.005, 1.45, 1.6, 0.04, 0.05)
    p.cham('steel_d', x - 0.42, x - 0.12, 0.92, 1.0, 0.45, 0.65, 0.01); p.box('steel_d', x - 0.34, x - 0.2, 1.0, 1.1, 0.48, 0.62)
    p.box('steel', x - 0.36, x - 0.18, 1.1, 1.13, 0.52, 0.58); seg_cyl(p, 'chrome', (x - 0.27, 1.04, 0.62), (x - 0.27, 1.04, 0.8), 0.01, 6)
    p.cham('metal', -x + 0.1, x - 0.1, 2.1, 2.18, 0.1, 0.3, 0.01); p.box('lamp_glass', -x + 0.14, x - 0.14, 2.095, 2.1, 0.14, 0.26)
    for xx in (-x + 0.2, x - 0.2): p.box('metal', xx - 0.01, xx + 0.01, 2.18, 2.4, 0.02, 0.2)
    return p
def tool_chest():
    """Armario de ferramentas com rodizios e gavetas (pivo: centro de tras, chao; para +Z) e caixa de cima com tampa."""
    p = Piece(); p.cham('tool_r', -0.5, 0.5, 0.12, 1.0, 0.0, 0.48, 0.015)
    for k in range(6):
        y0 = 0.16 + k * 0.135; p.box('tool_r', -0.48, 0.48, y0, y0 + 0.12, 0.48, 0.495); p.box('chrome', -0.35, 0.35, y0 + 0.08, y0 + 0.1, 0.495, 0.51)
    for (a, c) in ((-0.42, 0.06), (0.42, 0.06), (-0.42, 0.42), (0.42, 0.42)): p.cyl('dark', 0.05, 0.02, 0.12, a, c, 10)
    p.cham('tool_r', -0.48, 0.48, 1.0, 1.4, 0.02, 0.46, 0.015); p.hull('tool_r', [(x, y, z) for x in (-0.48, 0.48) for (y, z) in ((1.4, 0.02), (1.4, 0.46), (1.5, 0.02), (1.48, 0.46))])
    for k in range(3): p.box('chrome', -0.3, 0.3, 1.06 + k * 0.11, 1.08 + k * 0.11, 0.46, 0.475)
    return p
def tire(r=0.32, w=0.2):
    """Pneu de pe (pivo: centro, eixo em X)."""
    p = Piece(); disc_x(p, 'rubber', r, -w / 2, w / 2, 0.0, 0.0, 28); disc_x(p, 'dark', r - 0.12, -w / 2 - 0.004, w / 2 + 0.004, 0.0, 0.0, 20)
    for k in range(14):
        a = k * 2 * math.pi / 14; p.box('dark', -w / 2 + 0.01, w / 2 - 0.01, r * math.sin(a) - 0.015 + 0.0, r * math.sin(a) + 0.015, r * math.cos(a) - 0.015, r * math.cos(a) + 0.015) if False else None
    return p
def tire_rack(L1=3.0):
    """Prateleira de pneus de 2 andares (pivo: centro de tras, chao; para +Z)."""
    p = Piece(); x = L1 / 2; d = 0.55
    for xx in (-x, 0.0, x):
        for zz in (0.03, d - 0.03): p.box('steel', xx - 0.03, xx + 0.03, 0.0, 2.0, zz - 0.03, zz + 0.03)
    for y in (0.2, 1.1):
        for zz in (0.12, d - 0.12): p.box('paint_y', -x + 0.03, x - 0.03, y - 0.04, y, zz - 0.025, zz + 0.025)
        n = int((L1 - 0.1) / 0.23)
        for i in range(n): p.merge(tire(), tr(-x + 0.12 + i * 0.23, y + 0.32, d / 2))
    for zz in (0.03, d - 0.03): p.box('steel', -x - 0.03, x + 0.03, 1.97, 2.03, zz - 0.03, zz + 0.03)
    return p
def tire_stack(n=4):
    p = Piece()
    for k in range(n):
        y = k * 0.2; m = trimesh.creation.annulus(r_min=0.2, r_max=0.32, height=0.19, sections=28); m.apply_transform(rot_y(0) @ trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); m.apply_translation([0, y + 0.095, 0]); p.add('rubber', m)
    return p
def compressor():
    """Compressor de ar (pivo: centro, chao): tanque horizontal com pes, motor, polia com protecao, manometro e mangueira enrolada."""
    p = Piece(); disc_x(p, 'tool_r', 0.28, -0.6, 0.6, 0.38, 0.0, 24)
    for s in (-1, 1): lathe(p, 'tool_r', [(0.28, 0.0), (0.2, 0.08), (0.0, 0.11)], 0, 0, 0, 20) if False else None
    for s in (-1, 1):
        m = trimesh.creation.icosphere(subdivisions=2, radius=0.28); m.apply_scale([0.35, 1, 1]); m.apply_translation([s * 0.6, 0.38, 0]); p.add('tool_r', m)
        for zz in (-0.15, 0.15): p.box('steel_d', s * 0.4 - 0.03, s * 0.4 + 0.03, 0.0, 0.14, zz - 0.06, zz + 0.06)
    p.box('steel_d', -0.4, 0.4, 0.64, 0.68, -0.2, 0.2); p.cyl('dark', 0.14, 0.68, 0.9, -0.15, 0.0, 16); p.cham('steel', 0.1, 0.42, 0.68, 0.92, -0.15, 0.15, 0.02)
    disc_z(p, 'dark', 0.05, 0.28, 0.3, 0.3, 0.55, 14); disc_z(p, 'paint_w', 0.04, 0.3, 0.305, 0.3, 0.55, 14)
    m = trimesh.creation.torus(major_radius=0.18, minor_radius=0.02, major_sections=24, minor_sections=6); m.apply_translation([0.0, 0.38, 0.3]); p.add('dark', m)
    return p
def drum(mat='drum_b'):
    p = Piece(); p.cyl(mat, 0.29, 0.0, 0.88, 0, 0, 24)
    for y in (0.02, 0.3, 0.58, 0.86): ring_y(p, mat, 0.29, 0.305, y, y + 0.025, 0, 0, 24)
    p.cyl('steel', 0.03, 0.88, 0.9, 0.15, 0.0, 10); return p
def floor_jack():
    """Macaco jacare (pivo: centro, chao; cabo para -Z)."""
    p = Piece(); p.hull('tool_r', [(x, y, z) for x in (-0.15, 0.15) for (y, z) in ((0.05, 0.45), (0.05, -0.4), (0.22, -0.35), (0.16, 0.42))])
    for (x, z) in ((-0.17, 0.35), (0.17, 0.35), (-0.17, -0.3), (0.17, -0.3)): disc_x(p, 'dark', 0.05, *sorted((x, x + (0.04 if x > 0 else -0.04))), 0.05, z, 12)
    p.cyl('dark', 0.07, 0.22, 0.25, 0.0, 0.42, 14); seg_cyl(p, 'steel', (0, 0.2, -0.38), (0, 0.9, -1.1), 0.018, 8)
    return p
def parts_shelf(L1=1.8, h=2.0, d=0.5):
    """Estante de aco com caixas de pecas (pivo: centro de tras, chao; para +Z)."""
    p = Piece(); x = L1 / 2; rng = np.random.default_rng(3)
    for xx in (-x, x):
        for zz in (0.02, d - 0.02): p.box('steel', xx - 0.02, xx + 0.02, 0.0, h, zz - 0.02, zz + 0.02)
    for y in np.linspace(0.1, h - 0.02, 5):
        p.box('steel', -x + 0.02, x - 0.02, y - 0.02, y, 0.0, d)
        if y < h - 0.1:
            xx = -x + 0.05
            while xx < x - 0.3:
                wd = rng.uniform(0.2, 0.38); hh = rng.uniform(0.15, 0.3); c = ['fabric', 'paint_w', 'drum_b', 'tool_r'][rng.integers(4)]
                p.cham(c, xx, xx + wd - 0.02, y, y + hh, 0.05, d - rng.uniform(0.05, 0.12), 0.006); xx += wd
    return p
def hose_reel():
    """Enrolador de mangueira de ar na parede (pivo: face da parede, centro)."""
    p = Piece(); p.box('steel_d', -0.15, 0.15, -0.2, 0.2, 0.0, 0.04); disc_z(p, 'tool_r', 0.22, 0.04, 0.06, 0, 0, 24); disc_z(p, 'tool_r', 0.22, 0.2, 0.22, 0, 0, 24)
    disc_z(p, 'dark', 0.13, 0.06, 0.2, 0, 0, 20); seg_cyl(p, 'dark', (0.0, -0.13, 0.13), (0.1, -1.2, 0.2), 0.012, 6); return p
def fl_light():
    """Luminaria fluorescente pendente (pivo: ponto de fixacao no teto, eixo X): calha de chapa, 2 tubos e correntes."""
    p = Piece(); y0 = -0.9
    p.cham('metal', -0.62, 0.62, y0, y0 + 0.08, -0.12, 0.12, 0.01)
    for z in (-0.05, 0.05): disc_x(p, 'lamp_glass', 0.022, -0.58, 0.58, y0 - 0.005, z, 10)
    for x in (-0.45, 0.45): seg_cyl(p, 'steel', (x, y0 + 0.08, 0), (x, 0.0, 0), 0.006, 4)
    return p

# ============================================================================ carros genericos dos anos 70/80 (pivo: meio entre os eixos, chao; frente +Z)
CAR_SPEC = {
    'sedan':  dict(zf=2.42, zr=-2.42, wf=1.38, wr=-1.38, cab=(0.78, -1.5, 0.05, -1.05), top=1.38),
    'wagon':  dict(zf=2.42, zr=-2.48, wf=1.38, wr=-1.4, cab=(0.78, -2.4, 0.05, -2.3), top=1.4),
    'coupe':  dict(zf=2.35, zr=-2.3, wf=1.3, wr=-1.3, cab=(0.7, -1.7, -0.05, -0.85), top=1.3),
    'hatch':  dict(zf=1.92, zr=-1.86, wf=1.15, wr=-1.15, cab=(0.5, -1.78, -0.15, -1.55), top=1.36),
    'pickup': dict(zf=2.5, zr=-2.5, wf=1.6, wr=-1.5, cab=(0.92, -0.56, 0.3, -0.52), top=1.55, bed=-0.62)}
def car(mat='car_r', kind='sedan', tag=False, bumper='chrome'):
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
    for wz in (wf, wr):
        for s in (-1, 1):
            disc_x(p, 'rubber', 0.32, *sorted((s * (hw - 0.27), s * (hw - 0.04))), 0.32, wz, 28)
            disc_x(p, 'chrome', 0.19, *sorted((s * (hw - 0.05), s * (hw - 0.03))), 0.32, wz, 20)
            disc_x(p, 'steel', 0.07, *sorted((s * (hw - 0.03), s * (hw - 0.02))), 0.32, wz, 12)
            for k in range(6):
                a = k * math.pi / 3; p.box('dark', *sorted((s * (hw - 0.034), s * (hw - 0.026))), 0.32 + 0.13 * math.sin(a) - 0.015, 0.32 + 0.13 * math.sin(a) + 0.015, wz + 0.13 * math.cos(a) - 0.015, wz + 0.13 * math.cos(a) + 0.015)
    return p
def balloons():
    """Cacho de 5 baloes com fitas presos num peso (pivo: base do peso, em cima do teto do carro)."""
    p = Piece(); p.cham('dark', -0.06, 0.06, 0.0, 0.05, -0.06, 0.06, 0.01)
    cols = ['flag_r', 'flag_y', 'flag_b', 'flag_g', 'paint_w']; rng = np.random.default_rng(2)
    for k, c in enumerate(cols):
        a = k * 2 * math.pi / 5; r = 0.22; hh = rng.uniform(1.0, 1.3); cx, cz = r * math.cos(a), r * math.sin(a)
        seg_cyl(p, 'paint_w', (0, 0.05, 0), (cx, hh - 0.16, cz), 0.003, 3)
        m = trimesh.creation.icosphere(subdivisions=2, radius=0.16); m.apply_scale([1, 1.18, 1]); m.apply_translation([cx, hh, cz]); p.add(c, m)
        p.cyl(c, 0.02, hh - 0.2, hh - 0.17, cx, cz, 8)
    return p
def feather_flag(mat='flag_r'):
    """Bandeira de pena (pivo: pe, chao; bandeira para +X): base em cruz, mastro curvo e tecido com faixa branca e estrela."""
    p = Piece()
    p.box('steel_d', -0.35, 0.35, 0.0, 0.04, -0.03, 0.03); p.box('steel_d', -0.03, 0.03, 0.005, 0.045, -0.35, 0.35)
    p.cyl('steel_d', 0.02, 0.0, 0.5, 0, 0, 8)
    pts = [(0.0, 0.6 + 2.6 * t + 0.0, 0.0) for t in np.linspace(0, 1, 7)]
    tip = [(0.06 + 0.5 * (1 - math.cos(a)), 3.2 + 0.4 * math.sin(a)) for a in np.linspace(0, math.pi / 2, 6)]
    for k in range(len(pts) - 1): seg_cyl(p, 'steel', pts[k], pts[k + 1], 0.012, 6)
    for k in range(len(tip) - 1): seg_cyl(p, 'steel', (tip[k][0] - 0.06, tip[k][1], 0), (tip[k + 1][0] - 0.06, tip[k + 1][1], 0), 0.01, 6)
    outline = [(0.02, 0.7), (0.62, 0.8), (0.7, 2.4), (0.66, 3.0)] + [(x + 0.06, y - 0.02) for (x, y) in tip[::-1]] + [(0.02, 3.2)]
    poly = Polygon(outline).buffer(0); ext(p, mat, poly, -0.006, 0.006)
    stripe = poly.intersection(sbox(0.0, 1.0, 0.18, 3.3)); ext(p, 'paint_w', stripe, -0.008, 0.008) if False else None
    for s in (-1, 1):
        ext(p, 'paint_w', poly.intersection(sbox(0.0, 0.7, 0.14, 3.4)), *sorted((s * 0.006, s * 0.008)))
        from shapely import affinity
        star = Polygon([(0.4 + (0.13 if k % 2 == 0 else 0.055) * math.sin(k * math.pi / 5), 2.2 + (0.13 if k % 2 == 0 else 0.055) * math.cos(k * math.pi / 5)) for k in range(10)])
        ext(p, 'paint_w', star, *sorted((s * 0.006, s * 0.008)))
    return p
def tube_man():
    """Boneco inflavel de propaganda (pivo: chao): soprador, corpo de tubo ondulado, bracos agitados, rosto simples e cabelo."""
    p = Piece(); p.cham('steel_d', -0.35, 0.35, 0.0, 0.5, -0.35, 0.35, 0.03); p.cyl('dark', 0.25, 0.5, 0.52, 0, 0, 20)
    pts = [(0.08 * math.sin(k * 1.1), 0.5 + k * 0.4, 0.06 * math.cos(k * 0.9)) for k in range(10)]
    for k in range(len(pts) - 1): seg_cyl(p, 'tube_g', pts[k], pts[k + 1], 0.26 - 0.006 * k, 14); p.sphere('tube_g', 0.26 - 0.006 * k, *pts[k + 1], 1)
    sh = np.array(pts[7])
    for s in (-1, 1):
        q = [sh, sh + np.array([s * 0.5, 0.25, 0.05]), sh + np.array([s * 0.9, 0.7 if s > 0 else 0.0, 0.1]), sh + np.array([s * 1.15, 1.1 if s > 0 else -0.2, 0.0])]
        for k in range(3): seg_cyl(p, 'tube_g', q[k], q[k + 1], 0.09, 10); p.sphere('tube_g', 0.09, *q[k + 1], 1)
    hd = np.array(pts[-1])
    for s in (-1, 1):
        p.sphere('paint_w', 0.07, hd[0] + s * 0.09, hd[1] - 0.1, hd[2] + 0.22, 1); p.sphere('dark', 0.035, hd[0] + s * 0.09, hd[1] - 0.1, hd[2] + 0.285, 1)
    p.hull('dark', [(hd[0] + a, hd[1] - 0.3 + b, hd[2] + 0.235 + c) for a in (-0.08, 0.08) for b in (-0.02, 0.02) for c in (0.0, 0.03)])
    for k in range(7):
        a = k * 2 * math.pi / 7; seg_cyl(p, 'flag_y', (hd[0], hd[1] + 0.1, hd[2]), (hd[0] + 0.3 * math.cos(a), hd[1] + 0.45, hd[2] + 0.3 * math.sin(a)), 0.03, 6)
    return p
def pylon_sign():
    """Totem da loja (pivo: chao; faces para +-Z): 2 colunas de aco, caixa luminosa com pictograma de carro, painel de lampadas sem
    numeros (losangos e seta), estrela no topo e base de concreto."""
    p = Piece(); p.cham('concrete', -1.3, 1.3, 0.0, 0.4, -0.4, 0.4, 0.03)
    for x in (-0.9, 0.9): p.box('steel', x - 0.14, x + 0.14, 0.4, 7.3, -0.14, 0.14)
    p.cham('sign_w', -1.6, 1.6, 5.2, 7.2, -0.3, 0.3, 0.04)
    for y in (5.16, 7.16): p.box('mull', -1.64, 1.64, y, y + 0.08, -0.32, 0.32)
    for s in (-1, 1): picto_car(p, 'dark', 0.0, 6.15, 2.4, *sorted((s * 0.3, s * 0.312)))
    p.cham('dark', -1.45, 1.45, 3.9, 4.95, -0.18, 0.18, 0.02); p.box('mull', -1.5, 1.5, 3.86, 3.92, -0.2, 0.2); p.box('mull', -1.5, 1.5, 4.93, 4.99, -0.2, 0.2)
    pat = [(i, j) for i in range(-9, 10) for j in range(-2, 3) if (abs(i % 6 - 3) + abs(j) == 2 and i < 5) or (i >= 6 and abs(j) <= 8 - i) or (i in (4, 5) and j == 0)]
    for s in (-1, 1):
        for (i, j) in pat:
            x = i * 0.13; y = 4.425 + j * 0.16; p.box('led', x - 0.04, x + 0.04, y - 0.04, y + 0.04, *sorted((s * 0.18, s * 0.19)))
    star = Polygon([((0.5 if k % 2 == 0 else 0.22) * math.sin(k * math.pi / 5), 7.85 + (0.5 if k % 2 == 0 else 0.22) * math.cos(k * math.pi / 5)) for k in range(10)])
    ext(p, 'flag_y', star, -0.06, 0.06); p.box('steel', -0.05, 0.05, 7.24, 7.4, -0.05, 0.05)
    return p
def lot_lamp():
    """Poste do patio (pivo: chao): base de concreto, coluna conica, travessa com 2 refletores e caixa de ligacao."""
    p = Piece(); p.cyl('concrete', 0.28, -0.2, 0.5, 0, 0, 16)
    lathe(p, 'steel', [(0.14, 0.5), (0.12, 0.7), (0.07, 7.0)], sec=14)
    seg_cyl(p, 'steel', (-0.7, 7.0, 0), (0.7, 7.0, 0), 0.045, 8)
    for s in (-1, 1):
        x = s * 0.65; p.cham('metal', x - 0.2, x + 0.2, 6.72, 7.0, -0.16, 0.16, 0.02); p.box('lamp_glass', x - 0.17, x + 0.17, 6.7, 6.72, -0.13, 0.13)
    p.box('metal', -0.09, 0.09, 1.4, 1.75, 0.07, 0.14)
    for y in (5.0, 5.6): p.box('steel', -0.1, 0.1, y, y + 0.03, -0.1, 0.1)
    return p
def bollard():
    p = Piece(); p.cyl('paint_y', 0.1, -0.1, 1.0, 0, 0, 16); p.sphere('paint_y', 0.1, 0, 1.0, 0, 1)
    for y in (0.8, 0.86): ring_y(p, 'dark', 0.1, 0.104, y, y + 0.03, 0, 0, 16)
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

# ============================================================================ terreno (pivo: origem)
SX0, SX1, SZ0, SZ1 = -19.0, 19.0, -14.0, 18.0
ISLAND = sbox(-12.2, 6.4, -9.8, 11.2)
DRV1 = sbox(-9.0, 11.5, -4.0, 13.2); DRV2 = sbox(6.0, 11.5, 11.0, 13.2)
APRON = unary_union([sbox(SX0_, SZ1_, GX1, 0.6), sbox(SX1_, GZ0, GX0, GZ1), sbox(-3.8, -12.3, -2.2, SZ0_)])
LOT = unary_union([sbox(-18.0, 0.6, 18.0, 11.5), sbox(GX1, -13.2, 18.0, 0.6), DRV1, DRV2]).difference(ISLAND)
SIDEWALK = sbox(SX0, 11.5, SX1, 13.2).difference(unary_union([DRV1, DRV2])); STREET = sbox(SX0, 13.2, SX1, SZ1)
RA = [-16.2, -13.6, -2.6, 0.0, 2.6, 13.0, 15.6]; RA_Z = 8.36                 # vagas da frente (carros de frente para a rua)
RB = [-11.8, -9.2, -6.6, -4.0, -1.4]; RB_X = 15.4                           # vagas do lado (carros de frente para a oficina)
def site():
    """Terreno: patio de asfalto com vagas pintadas e setas, calcada de placas na frente dos predios e entre eles, ilha do totem
    com meio-fio e grama, calcada com juntas, entradas rebaixadas, rua com faixa amarela dupla e faixas brancas, gramado."""
    p = Piece(); box_ = sbox(SX0, SZ0, SX1, SZ1)
    ext_y(p, 'asphalt', unary_union([LOT, STREET]), GY, 0.0)
    p.merge(paving(APRON, Y0, 1.5)); p.merge(paving(SIDEWALK, Y0, 1.5))
    ext_y(p, 'curb', ISLAND.difference(off(ISLAND, -0.15)), GY, Y0); ext_y(p, 'grass', off(ISLAND, -0.15), GY, 0.12)
    grass = box_.difference(unary_union([LOT, STREET, APRON, SIDEWALK, ISLAND, SRB, GB])); ext_y(p, 'grass', grass, GY, 0.05)
    for x in (-17.5, -14.9, -12.3, -3.9, -1.3, 1.3, 3.9, 11.7, 14.3, 16.9): p.box('paint_w', x - 0.05, x + 0.05, 0.0, 0.004, 5.9, 11.3)
    for z in (-13.1, -10.5, -7.9, -5.3, -2.7, -0.1): p.box('paint_w', 12.6, 17.9, 0.0, 0.004, z - 0.05, z + 0.05)
    for (x, z, s) in ((-6.5, 9.0, -1), (8.5, 9.0, 1), (-6.5, 3.0, -1), (8.5, 3.0, 1)):
        p.hull('paint_w', [(x + dx, y, z + s * dz) for (dx, dz) in ((-0.1, -1.2), (0.1, -1.2), (-0.1, 0.0), (0.1, 0.0)) for y in (0.0, 0.004)])
        p.hull('paint_w', [(x + dx, y, z + s * dz) for (dx, dz) in ((-0.4, 0.0), (0.4, 0.0), (0.0, 0.7)) for y in (0.0, 0.004)])
    for x in np.arange(SX0 + 0.5, SX1 - 1.0, 3.0):
        for z in (15.52, 15.72): p.box('yellowp', x, x + 1.8, 0.0, 0.004, z - 0.05, z + 0.05)
    p.box('paint_w', SX0, SX1, 0.0, 0.004, 13.45, 13.57); p.box('paint_w', SX0, SX1, 0.0, 0.004, 17.6, 17.72)
    return p
def lamp_top(x, z): return (x, 6.2, z)
LAMPS = [(-16.5, 12.4), (-3.5, 12.4), (4.8, 12.4), (16.5, 12.4), (-15.0, 1.3), (10.6, 0.9), (17.0, -13.6)]
RUNS = [(0, 1), (1, 2), (2, 3), (1, 4), (2, 5), (3, 5), (5, 6)]
def pennants():
    """Bandeirolas coloridas em cordas com barriga entre os postes e da quina do showroom ate um poste (pivo: origem)."""
    p = Piece(); cols = ['flag_r', 'flag_y', 'flag_b', 'flag_g', 'flag_o', 'paint_w']; ci = 0
    runs = [(lamp_top(*LAMPS[a]), lamp_top(*LAMPS[b])) for (a, b) in RUNS] + [((-1.55, 4.5, 0.55), lamp_top(*LAMPS[2]))]
    for (a, b) in runs:
        a = np.array(a, float); b = np.array(b, float); L1 = np.linalg.norm((b - a)[[0, 2]]); sag = 0.035 * L1
        f = lambda t: a + (b - a) * t - np.array([0, 4 * sag * t * (1 - t), 0])
        ts = np.linspace(0, 1, 16)
        for k in range(15): seg_cyl(p, 'dark', f(ts[k]), f(ts[k + 1]), 0.007, 4)
        n = int(L1 / 0.42); u = (b - a); u[1] = 0; u /= np.linalg.norm(u); w = np.cross(u, [0, 1, 0])
        for i in range(1, n):
            t = i / n; c = f(t); d = 0.12 / L1
            p0, p1 = f(t - d), f(t + d); tip = c - np.array([0, 0.34, 0])
            p.hull(cols[ci % 6], [q + e * w for q in (p0, p1, tip) for e in (-0.004, 0.004)]); ci += 1
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
def wm(fn, kind, tl=0.0, tr_=0.0):
    n = f"{'s' if fn is sr_mod else 'k'}_{kind}" + ('_l' if tl else '') + ('_r' if tr_ else '')
    if n not in pieces: pieces[n] = fn(kind, tl, tr_)
    return n
CARS = {'car_sedan_r': ('car_r', 'sedan', 'chrome'), 'car_sedan_s': ('car_s', 'sedan', 'chrome'), 'car_sedan_b': ('car_b', 'sedan', 'chrome'),
        'car_wagon_g': ('car_g', 'wagon', 'chrome'), 'car_wagon_w': ('car_w', 'wagon', 'chrome'), 'car_coupe_y': ('car_y', 'coupe', 'chrome'),
        'car_coupe_r': ('car_r', 'coupe', 'chrome'), 'car_coupe_k': ('car_k', 'coupe', 'chrome'), 'car_hatch_p': ('car_p', 'hatch', 'rubber'),
        'car_hatch_t': ('car_t', 'hatch', 'rubber'), 'car_pickup_b': ('car_b', 'pickup', 'rubber'), 'car_pickup_o': ('car_o', 'pickup', 'rubber')}
for n, (m, k, bm) in CARS.items(): pieces[n] = car(m, k, True, bm)
pieces.update({'car_sedan_k_svc': car('car_k', 'sedan', False, 'chrome'), 'car_pickup_o_svc': car('car_o', 'pickup', False, 'rubber')})
pieces.update({
    'sr_roof': sr_roof(), 'link_roof': link_roof(), 'g_roof': g_roof(), 'svc_sign': svc_sign(), 'sr_floor': sr_floor(), 'g_floor': g_floor(),
    'sr_plan': sr_plan(), 'g_plan': g_plan(), 'turntable': turntable(2.2), 'desk': desk(), 'office_chair': office_chair(), 'guest_chair': guest_chair(),
    'sofa': sofa(3), 'side_table': side_table(), 'plant': plant(), 'brochure_rack': brochure_rack(), 'water_cooler': water_cooler(),
    'bookcase': bookcase(1.6), 'file_cab': file_cab(), 'kitchenette': kitchenette(2.0), 'fridge': fridge(), 'table_set': table_set(),
    'wc': wc(), 'sink_one': sink_bank(1, 0.8),
    'lift_up': lift(2.05), 'lift_down': lift(0.36), 'workbench': workbench(2.0), 'tool_chest': tool_chest(), 'tire_rack': tire_rack(3.0),
    'tire_stack': tire_stack(4), 'compressor': compressor(), 'drum': drum('drum_b'), 'drum_r': drum('tool_r'), 'floor_jack': floor_jack(),
    'parts_shelf': parts_shelf(1.8), 'hose_reel': hose_reel(), 'fl_light': fl_light(),
    'balloons': balloons(), 'flag_r': feather_flag('flag_r'), 'flag_b': feather_flag('flag_b'), 'flag_y': feather_flag('flag_y'), 'flag_g': feather_flag('flag_g'),
    'tube_man': tube_man(), 'pylon_sign': pylon_sign(), 'lot_lamp': lot_lamp(), 'bollard': bollard(), 'trash_can': trash_can(), 'pennants': pennants(),
    'tree': tree(5.8, 1.7), 'tree_b': tree(5.0, 1.45, 'leaf2', 4), 'bush': bush(), 'site': site(),
    'door_glass': door_glass(0.9, 2.38, 0.05), 'door_metal': door_metal(0.86, 2.12), 'door_metal_g': door_metal(0.9, 2.17),
    'door_int': door_interior(0.86, 2.08), 'player_scale_ref': player_ref()})

# ============================================================================ montagem
y = Y0; yf = Y0 + 0.005
S = ['showroom', 'ext']; G = ['oficina', 'ext']
for x, k in zip(range(-15, -1, 2), ['win', 'win', 'win', 'door2', 'win', 'win', 'win']): put(wm(sr_mod, k), x, y, SZ1_, 0, S + ['front'])
for x, k in zip(range(-15, -1, 2), ['plain', 'plain', 'win_s', 'plain', 'win_s', 'plain', 'door_s']): put(wm(sr_mod, k), x, y, SZ0_, 180, S + ['back'])
for z, k in zip((-10, -8, -6, -4, -2), ['plain', 'plain', 'win', 'win', 'win']):
    put(wm(sr_mod, k, T if z == -10 else 0.0, T if z == -2 else 0.0), SX0_, y, z, -90, S + (['front'] if z > -7 else ['back']))
for z, k in zip((-10, -8, -6, -4, -2), ['win_s', 'plain', 'win', 'win', 'door1']):
    put(wm(sr_mod, k, T if z == -2 else 0.0, T if z == -10 else 0.0), SX1_, y, z, 90, S + (['front'] if z > -7 else ['back']))
put('door_glass', -9 - 0.915, yf, SZ1_ - 0.1, 0, S + ['front'], door=90); put('door_glass', -9 + 0.915, yf, SZ1_ - 0.1, 180, S + ['front'], door=-90)
hx, hz = hinge(SX1_, -2.0, 90, -0.455, -0.1); put('door_glass', hx, yf, hz, 90, S, door=90)
hx, hz = hinge(-3.0, SZ0_, 180, -0.44, -0.125); put('door_metal', hx, yf, hz, 180, S + ['back'], door=90)
put('sr_roof', 0, y, 0, 0, ['showroom', 'roof']); put('link_roof', 0, y, 0, 0, ['roof'])
put('sr_floor', 0, y, 0, 0, ['showroom']); put('sr_plan', 0, y, 0, 0, ['showroom'])
for c in (1.35, 4.45, 7.15, 12.75): put('door_int', SX0_ + T + c - 0.43, yf, ZOF, 0, ['showroom'], door=90)
# oficina
put(wm(k_mod, 'bay'), 2.0, y, GZ1, 0, G + ['front']); put(wm(k_mod, 'bay_half'), 6.0, y, GZ1, 0, G + ['front']); put(wm(k_mod, 'door'), 9.0, y, GZ1, 0, G + ['front'])
for x, k in zip((1, 3, 5, 7, 9), ['win', 'plain', 'win', 'plain', 'plain']): put(wm(k_mod, k), x, y, GZ0, 180, G + ['back'])
for z, k in zip((-10, -8, -6, -4, -2), ['plain', 'win', 'win', 'plain', 'door']):
    put(wm(k_mod, k, T if z == -10 else 0.0, T if z == -2 else 0.0), GX0, y, z, -90, G + (['front'] if z > -7 else ['back']))
for z, k in zip((-10, -8, -6, -4, -2), ['win_n', 'plain', 'plain', 'win', 'plain']):
    put(wm(k_mod, k, T if z == -2 else 0.0, T if z == -10 else 0.0), GX1, y, z, 90, G + (['front'] if z > -7 else ['back']))
hx, hz = hinge(GX0, -2.0, -90, -0.455, -0.125); put('door_metal_g', hx, yf, hz, -90, G, door=90)
hx, hz = hinge(9.0, GZ1, 0, -0.455, -0.125); put('door_metal_g', hx, yf, hz, 0, G + ['front'], door=90)
put('g_roof', 0, y, 0, 0, ['oficina', 'roof']); put('svc_sign', 4.0, y, GZ1, 0, G + ['front'])
put('g_floor', 0, y, 0, 0, ['oficina']); put('g_plan', 0, y, 0, 0, ['oficina'])
put('door_int', 7.0, yf, GZ0 + T + 0.75 - 0.43, -90, ['oficina'], door=90)
# showroom por dentro
g = ['showroom']
put('turntable', -12.7, y, -4.6, 0, g); put('car_coupe_r', -12.7, y + 0.12, -4.6, 30, g); put('car_sedan_b', -5.6, y, -4.2, 0, g)
put('sofa', -6.6, y, ZOF + t_ / 2, 0, g); put('side_table', -5.0, y, -7.35, 0, g)
put('desk', -3.5, y, -5.0, 0, g); put('office_chair', -3.5, y, -5.55, 0, g)
for x in (-3.9, -3.1): put('guest_chair', x, y, -4.25, 180, g)
put('brochure_rack', SX0_ + T, y, -7.0, 90, g); put('water_cooler', -15.4, y, -2.0, 0, g)
for (x, z) in ((-7.6, -1.75), (-10.4, -1.75), (-13.0, -1.65), (-6.0, -8.2)): put('plant', x, y, z, 0, g)
put('wc', -15.0, y, SZ0_ + T, 0, g); put('sink_one', SX0_ + T, y, -9.1, 90, g)
put('desk', -11.5, y, -9.9, 0, g); put('office_chair', -11.5, y, -10.4, 0, g)
for x in (-11.9, -11.1): put('guest_chair', x, y, -9.0, 180, g)
put('file_cab', -12.6, y, ZOF - t_ / 2, 180, g)
put('desk', -7.0, y, -9.8, 0, g); put('office_chair', -7.0, y, -10.35, 0, g)
for x in (-7.4, -6.6): put('guest_chair', x, y, -9.0, 180, g)
put('bookcase', -9.6 + t_ / 2, y, -9.6, 90, g)
put('kitchenette', -5.6 + t_ / 2, y, -9.4, 90, g); put('fridge', -4.4, y, SZ0_ + T, 0, g); put('table_set', -4.3, y, -9.0, 90, g)
# oficina por dentro
g = ['oficina']
put('lift_up', 2.0, y, -5.5, 180, g); put('car_sedan_k_svc', 2.0, y + 2.05 - 0.3, -5.5, 0, g)
put('lift_down', 6.0, y, -5.5, 0, g); put('car_pickup_o_svc', 6.0, y, -5.5, 180, g)
put('workbench', GX1 - T, y, -6.0, -90, g); put('tool_chest', GX1 - T, y, -4.0, -90, g); put('trash_can', 9.45, y, -7.5, 0, g)
put('tire_rack', 2.0, y, GZ0 + T, 0, g); put('compressor', 4.6, y, -10.4, 0, g)
put('drum', 0.7, y, -9.6, 0, g); put('drum_r', 0.78, y, -8.92, 0, g); put('tire_stack', 0.65, y, -7.8, 0, g); put('floor_jack', 4.0, y, -3.8, 0, g)
put('hose_reel', GX0 + T, y + 2.0, -4.0, 90, g)
put('desk', 8.6, y, -8.0 - t_ / 2 - 0.375, 0, g); put('office_chair', 8.6, y, -9.25, 0, g); put('file_cab', 7.45, y, -8.0 - t_ / 2, 180, g)
put('parts_shelf', GX1 - T, y, -9.8, -90, g)
for x in (1.0, 3.0, 5.0, 7.0, 9.0):
    for z in (-3.4, -6.6): put('fl_light', x, y + GDECK - 0.01, z, 0, g + ['roof'])
# patio
st = ['site']; put('site', 0, 0, 0, 0, st); put('pennants', 0, 0, 0, 0, st + ['roof'])
ra = ['car_sedan_r', 'car_wagon_g', 'car_coupe_y', 'car_sedan_s', 'car_hatch_p', 'car_pickup_b', 'car_wagon_w']
for x, n in zip(RA, ra): put(n, x, 0, RA_Z, 0, st)
for x, n in ((-16.2, 'car_sedan_r'), (0.0, 'car_sedan_s'), (15.6, 'car_wagon_w')):
    S_ = CAR_SPEC[CARS[n][1]]; put('balloons', x, S_['top'] + 0.04, RA_Z + (S_['cab'][2] + S_['cab'][3]) / 2, 0, st)
for z, n in zip(RB, ['car_sedan_s', 'car_coupe_k', None, 'car_hatch_t', 'car_pickup_o']):
    if n: put(n, RB_X, 0, z, -90, st)
put('pylon_sign', -11.0, 0.12, 8.8, 0, st + ['roof'])
for (x, z) in LAMPS: put('lot_lamp', x, 0, z, 0, st + ['roof'])
for (x, z, ry, n) in ((-9.6, 12.4, 180, 'flag_r'), (-2.6, 12.4, 0, 'flag_b'), (5.8, 12.4, 180, 'flag_y'), (13.6, 12.4, 0, 'flag_g'), (17.4, 5.2, 90, 'flag_r'), (17.4, 1.2, 90, 'flag_b')):
    put(n, x, Y0 if z > 11 else 0, z, ry, st)
put('tube_man', 16.4, 0, 3.2, 0, st)
for x in (0.15, 3.85, 4.15, 7.85): put('bollard', x, Y0, -0.6, 0, st)
put('trash_can', -13.6, Y0, 0.1, 0, st)
for k, (x, z) in enumerate(((-17.6, -3.0), (-17.6, -9.5), (-12.0, -12.9), (-7.0, -12.9), (4.0, -12.7), (18.4, 9.0))): put('tree' if k % 2 == 0 else 'tree_b', x, 0.05, z, 0, st)
for (x, z) in ((-16.9, -5.6), (-16.9, -1.2), (-16.9, -7.0), (-0.9, -11.9), (8.5, -11.9)): put('bush', x, 0.05, z, 0, st)
put('player_scale_ref', -6.0, Y0, 0.2, 0, st); put('player_scale_ref', -8.0, Y0, -3.0, 0, ['showroom'])


if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'wall_thickness': T, 'floor_level': Y0,
                       'showroom': {'x': [SX0_, SX1_], 'z': [SZ0_, SZ1_], 'ceiling': CEIL, 'band_top': HB, 'rooms_front_z': ZOF},
                       'garage': {'x': [GX0, GX1], 'z': [GZ0, GZ1], 'deck': GDECK, 'parapet_top': HPG, 'bay_opening': [BAY_W, BAY_H]},
                       'site': {'x': [SX0, SX1], 'z': [SZ0, SZ1], 'lot_level': 0.0, 'sidewalk_z': [11.5, 13.2]},
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
