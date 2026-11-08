"""Kit 58: hospital de 7 pavimentos em L, em ALTO DETALHE (scripts/detalhe).
Predio de tijolo bege com embasamento de pedra no terreo, faixas e cornija de pedra, janelas de aluminio com peitoril e verga de
pedra, platibanda com capa. Terreo: saguao com recepcao e espera (entrada principal sob marquise de vidro) e pronto-socorro na
ala da frente (entrada de ambulancias sob marquise de concreto, triagem e 6 leitos de cortina). Andares 1 a 6: corredor em L
com corrimao, posto de enfermagem, 15 quartos com banheiro, escada de 2 lances e 2 elevadores. Cobertura com casa de maquinas,
condensadoras, heliponto elevado com rede de protecao e biruta. Lote com acesso, estacionamento, ambulancias e carros genericos.
Arte original e sem texto (so pictogramas; a cruz e branca sobre azul). Y para cima, 1 unidade = 1 m. Padrao: PADRAO_METRICAS.md.
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
CAR_COLS = {'car_r': (150, 56, 52), 'car_b': (60, 92, 140), 'car_g': (90, 116, 92), 'car_y': (200, 172, 92), 'car_w': (226, 224, 216), 'car_s': (168, 172, 176),
            'car_k': (46, 48, 52), 'car_t': (96, 140, 138)}
configurar(cores=dict({'brick': (196, 156, 112), 'stone': (214, 204, 184), 'stone_d': (186, 176, 158), 'coping': (222, 216, 200), 'plaster': (238, 236, 230),
                       'ceil': (244, 244, 240), 'tile_c': (236, 238, 236), 'vinyl_f': (210, 214, 206), 'vinyl_b': (150, 186, 196), 'vinyl_g': (150, 180, 150),
                       'terrazzo': (222, 216, 204), 'concrete': (192, 188, 180), 'conc_s': (178, 174, 166), 'asphalt': (78, 80, 82), 'curb': (200, 198, 192),
                       'grass': (112, 150, 74), 'mulch': (108, 82, 60), 'dirt': (150, 128, 98), 'membrane': (118, 120, 122), 'gravel': (170, 164, 152),
                       'alu': (196, 200, 204), 'alu_d': (90, 96, 102), 'metal': (176, 180, 184), 'chrome': (212, 216, 220), 'steel': (120, 126, 132), 'steel_d': (56, 60, 64),
                       'iron': (40, 42, 44), 'galv': (168, 174, 176), 'glass': (150, 186, 204), 'glass_d': (110, 140, 160), 'mirror': (200, 214, 220), 'lamp_glass': (255, 238, 196),
                       'paint_w': (240, 240, 234), 'paint_y': (236, 196, 50), 'paint_r': (190, 60, 52), 'blue': (40, 92, 160), 'blue_l': (120, 170, 210), 'teal': (70, 150, 150),
                       'wood': (176, 132, 88), 'dkwood': (110, 78, 54), 'laminate': (200, 170, 130), 'counter': (226, 222, 212), 'ctop': (200, 196, 186), 'door': (200, 170, 130),
                       'door_m': (180, 186, 190), 'frame': (232, 230, 222), 'trim': (230, 228, 220), 'dark': (34, 34, 36), 'rubber': (30, 30, 32), 'porcelain': (244, 244, 240),
                       'vinyl': (60, 70, 80), 'vinyl_r': (160, 64, 60), 'vinyl_t': (70, 130, 130), 'fabric2': (90, 110, 130), 'curtain': (150, 190, 200), 'curtain2': (210, 200, 160),
                       'bed_w': (244, 244, 240), 'bed_b': (170, 200, 220), 'screen': (30, 40, 44), 'screen_g': (60, 200, 120), 'paper': (236, 232, 220), 'cream': (240, 232, 214),
                       'leaf': (86, 128, 62), 'leaf2': (108, 150, 70), 'bark': (120, 96, 72), 'plant': (70, 120, 60), 'pot': (230, 226, 214), 'flag_o': (230, 140, 50),
                       'flag_r': (180, 50, 50), 'flag_b': (40, 60, 120), 'food_g': (90, 140, 60), 'food_r': (190, 60, 50), 'food_y': (230, 190, 70), 'basket': (150, 110, 70),
                       'cart_w': (200, 200, 196), 'brass': (196, 164, 90), 'gold': (210, 176, 90), 'line_w': (236, 236, 230), 'line_y': (226, 190, 70), 'player': (90, 140, 220),
                       'bench_g': (60, 100, 70), 'neon_r': (220, 60, 50), 'net': (60, 64, 66), 'pad_y': (226, 180, 50), 'hp_g': (90, 96, 92), 'grille': (60, 62, 64),
                       'glaze': (150, 186, 204), 'ambu_w': (240, 240, 236), 'ambu_r': (200, 60, 50), 'ambu_b': (40, 92, 160), 'lens_r': (220, 50, 40), 'lens_b': (50, 90, 220)}, **CAR_COLS),
           texturas={'brick': 'brick', 'stone': 'stone', 'stone_d': 'stone', 'coping': 'render', 'plaster': 'plaster', 'ceil': 'plaster', 'terrazzo': 'render',
                     'concrete': 'render', 'conc_s': 'render', 'asphalt': 'render', 'curb': 'render', 'grass': 'render', 'mulch': 'render', 'dirt': 'render',
                     'membrane': 'render', 'gravel': 'render', 'wood': 'planks', 'dkwood': 'planks', 'laminate': 'planks', 'bark': 'render', 'vinyl_f': 'render'},
           out=OUT)
D.METAL.update({'metal', 'chrome', 'steel', 'steel_d', 'iron', 'galv', 'alu', 'alu_d'} | set(CAR_COLS)); MATS = D.MATS; TEX = D.TEX
for k in CAR_COLS: MATS[k].roughnessFactor = 0.45; MATS[k].metallicFactor = 0.4
for k in ('screen_g', 'lens_r', 'lens_b'): MATS[k].emissiveFactor = [c / 255 for c in D.COL[k]]

# ============================================================================ medidas
W = 2.0; T = 0.3; TP = 0.12; t_ = 0.1; GY = -0.3
Y0 = 0.15; H = 3.6; ST = 0.3; NL = 7
LV = [Y0 + k * H for k in range(NL + 1)]                         # 0,15 terreo ... 25,35 cobertura
CH = H - ST
AX = (-14.0, 10.0); AZ = (-6.0, 6.0)                              # ala A (ao longo de X)
BXR = (0.0, 10.0); BZR = (6.0, 18.0)                              # ala B (frente, ao longo de Z)
FOOT = Polygon([(-14, -6), (10, -6), (10, 18), (0, 18), (0, 6), (-14, 6)])
CZA = (-1.0, 1.0); CXB = (4.0, 6.0)                               # corredores (ala A em Z, ala B em X)
BAYS_A = [-14.0, -10.0, -6.0, -2.0, 2.0, 6.0, 10.0]
BAYS_B = [6.0, 10.0, 14.0, 18.0]
CORE = (-2.0, 6.0)                                                # nucleo (lado norte): escada -2..2, elevadores 2..6
DW = 1.1; DH = 2.1; DHB = 2.2                                     # portas dos quartos (1,1 m) e altura
SNR = 18; SRR = H / SNR; STRD = 0.28                              # escada: 18 espelhos de 0,2 m, piso 0,28
PAR = 1.0                                                         # platibanda
SX0, SX1, SZ0, SZ1 = -34.0, 30.0, -16.0, 36.0                     # terreno
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
        c = trimesh.creation.cylinder(radius=rr, height=z1 - z0, sections=28); c.apply_translation([0, 0, (z0 + z1) / 2]); p.add(m, c)
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
# ============================================================================ utilitarios (paredes, janelas, portas)
def wall2(p, axis, u0, u1, vo, vi, holes, ya, yb, out='brick', inn='plaster', split=0.5):
    """Parede de 2 camadas com vaos (a, b, y0, y1). axis 'x': corre em X, espessura em Z de vo (face externa) a vi; 'z': corre em Z."""
    vm = vo + (vi - vo) * split
    us = sorted(set([u0, u1] + [h for q in holes for h in q[:2] if u0 < h < u1]))
    ys = sorted(set([ya, yb] + [h for q in holes for h in q[2:4] if ya < h < yb]))
    vs = sorted([vo, vm, vi]); outer_first = vo < vi
    def cell(i, j, k):
        cu = (us[i] + us[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for q in holes:
            if q[0] < cu < q[1] and q[2] < cy < q[3]: return None
        return (out if k == 0 else inn) if outer_first else (inn if k == 0 else out)
    for m, mesh in grid_solid(us, ys, vs, cell).items():
        if axis == 'z':
            v = mesh.vertices.copy(); mesh.vertices = np.stack([v[:, 2], v[:, 1], v[:, 0]], 1); mesh.invert()
        p.add(m, mesh)
def wall_grid(p, axis, u0, u1, v0, v1, holes, ya, yb, mat='plaster'):
    wall2(p, axis, u0, u1, v0, v1, holes, ya, yb, mat, mat)
def polys(g): return [q for q in getattr(g, 'geoms', [g]) if q.geom_type == 'Polygon' and q.area > 1e-5]
def bx(p, mat, axis, u0, u1, y0, y1, v0, v1):
    """Caixa em coordenadas de parede (u ao longo, v na espessura)."""
    if axis == 'x': p.box(mat, u0, u1, y0, y1, *sorted((v0, v1)))
    else: p.box(mat, *sorted((v0, v1)), y0, y1, u0, u1)
def slider(p, a, b, ya, yb, z0=-0.17, f=0.045):
    """Janela de correr de aluminio: 2 folhas, trilhos, fecho e puxador (em coordenadas locais de fachada: x ao longo, z para fora)."""
    zf0, zf1 = z0, z0 + 0.09
    p.box('alu', a, a + f, ya, yb, zf0, zf1); p.box('alu', b - f, b, ya, yb, zf0, zf1)
    p.box('alu', a + f, b - f, yb - f, yb, zf0, zf1); p.box('alu', a + f, b - f, ya, ya + f, zf0, zf1)
    xm = (a + b) / 2; s = 0.035; ia, ib, ja, jb = a + f, b - f, ya + f, yb - f
    for (u, v, za, zb) in ((ia, xm + 0.02, zf1 - 0.035, zf1 - 0.012), (xm - 0.02, ib, zf0 + 0.012, zf0 + 0.035)):
        p.box('alu', u, u + s, ja, jb, za, zb); p.box('alu', v - s, v, ja, jb, za, zb)
        p.box('alu', u + s, v - s, jb - s, jb, za, zb); p.box('alu', u + s, v - s, ja, ja + s, za, zb)
        p.box('glass', u + s - 0.004, v - s + 0.004, ja + s - 0.004, jb - s + 0.004, (za + zb) / 2 - 0.002, (za + zb) / 2 + 0.002)
    ym = (ja + jb) / 2; p.box('chrome', xm - 0.04, xm - 0.016, ym - 0.05, ym + 0.05, zf0 - 0.002, zf0 + 0.012)
def hung(p, a, b, ya, yb, z0=-0.17, f=0.05):
    """Janela de aluminio de 2 folhas de guilhotina com bandeira fixa em cima (coordenadas de fachada)."""
    zf0, zf1 = z0, z0 + 0.1
    p.box('alu', a, a + f, ya, yb, zf0, zf1); p.box('alu', b - f, b, ya, yb, zf0, zf1)
    p.box('alu', a + f, b - f, yb - f, yb, zf0, zf1); p.box('alu', a + f, b - f, ya, ya + f, zf0, zf1)
    yt = ya + (yb - ya) * 0.72; p.box('alu', a + f, b - f, yt - 0.025, yt + 0.025, zf0, zf1)
    p.box('glass', a + f - 0.004, b - f + 0.004, yt + 0.021, yb - f + 0.004, z0 + 0.048, z0 + 0.052)
    ym = (ya + f + yt - 0.025) / 2; s = 0.04
    for (y0, y1, za, zb) in ((ya + f, ym + 0.02, zf0 + 0.06, zf0 + 0.088), (ym - 0.02, yt - 0.025, zf0 + 0.012, zf0 + 0.04)):
        p.box('alu', a + f, a + f + s, y0, y1, za, zb); p.box('alu', b - f - s, b - f, y0, y1, za, zb)
        p.box('alu', a + f + s, b - f - s, y1 - s, y1, za, zb); p.box('alu', a + f + s, b - f - s, y0, y0 + s, za, zb)
        p.box('glass', a + f + s - 0.004, b - f - s + 0.004, y0 + s - 0.004, y1 - s + 0.004, (za + zb) / 2 - 0.002, (za + zb) / 2 + 0.002)
    xm = (a + b) / 2; p.box('chrome', xm - 0.05, xm + 0.05, ym + 0.02, ym + 0.04, zf0 + 0.088, zf0 + 0.1)
    p.box('chrome', xm - 0.06, xm + 0.06, ya + f + 0.05, ya + f + 0.07, zf0 + 0.088, zf0 + 0.104)

# ============================================================================ montagem: lista de posicoes e portas
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(float(x), 3), round(float(y), 3), round(float(z), 3)], 'rotY': round(float(ry), 3), 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': e['rotY'], 'open': round(float(ry + door), 3)}; e['tags'].append('door')
    L.append(e)
def l2w(frame, lx, lz):
    (fx, fz), fr = frame; a = math.radians(fr)
    return fx + math.cos(a) * lx + math.sin(a) * lz, fz - math.sin(a) * lx + math.cos(a) * lz
def put_f(frame, n, lx, ly, lz, lry=0.0, tags=(), door=None):
    x, z = l2w(frame, lx, lz); put(n, x, ly, z, frame[1] + lry, tags, door)
def door_at(n, axis, a, b, c, y, hinge, into, tags, gap=0.01):
    """Folha de porta no vao [a, b] de uma parede (eixo 'x' ou 'z', linha c), dobradica na ponta 'a' ou 'b', abrindo para o lado into (+1/-1)."""
    if axis == 'x':
        if hinge == 'a': put(n, a + gap, y, c, 0, tags, door=-90 * into)
        else: put(n, b - gap, y, c, 180, tags, door=90 * into)
    else:
        if hinge == 'a': put(n, c, y, a + gap, -90, tags, door=90 * into)
        else: put(n, c, y, b - gap, 90, tags, door=-90 * into)

# ============================================================================ quartos (retangulo interno no mundo + lado do corredor)
ROOMS = {'N1': (-13.7, -10.06, -5.7, -1.12, 'z1'), 'N2': (-9.94, -6.06, -5.7, -1.12, 'z1'), 'N3': (-5.94, -2.06, -5.7, -1.12, 'z1'), 'N4': (6.06, 9.7, -5.7, -1.12, 'z1'),
         'S1': (-13.7, -10.06, 1.12, 5.7, 'z0'), 'S2': (-9.94, -6.06, 1.12, 5.7, 'z0'), 'S3': (-5.94, -2.06, 1.12, 5.7, 'z0'), 'S4': (-1.94, 1.94, 1.12, 5.7, 'z0'),
         'W1': (0.3, 3.88, 5.82, 9.94, 'x1'), 'W2': (0.3, 3.88, 10.06, 13.94, 'x1'), 'W3': (0.3, 3.88, 14.06, 17.7, 'x1'),
         'E0': (6.12, 9.7, 1.12, 5.94, 'x0'), 'E1': (6.12, 9.7, 6.06, 9.94, 'x0'), 'E2': (6.12, 9.7, 10.06, 13.94, 'x0'), 'E3': (6.12, 9.7, 14.06, 17.7, 'x0')}
ROOMS_G = ['N1', 'N2', 'N3', 'N4', 'E0']                         # no terreo viram consultorios
def room_frame(k):
    """Moldura local do quarto: origem no meio da face do corredor, local +z para dentro do quarto. Devolve (moldura, largura, fundo)."""
    x0, x1, z0, z1, s = ROOMS[k]
    if s == 'z1': return ((((x0 + x1) / 2, z1), 180.0), x1 - x0, z1 - z0)
    if s == 'z0': return ((((x0 + x1) / 2, z0), 0.0), x1 - x0, z1 - z0)
    if s == 'x1': return (((x1, (z0 + z1) / 2), -90.0), z1 - z0, x1 - x0)
    return (((x0, (z0 + z1) / 2), 90.0), z1 - z0, x1 - x0)
def room_door(k):
    """Vao da porta do quarto na parede do corredor: (eixo, a, b, linha do eixo da parede, dobradica, lado para dentro)."""
    x0, x1, z0, z1, s = ROOMS[k]
    if s == 'z1': return ('x', x0 + 0.25, x0 + 0.25 + DW, z1 + TP / 2, 'a', -1)
    if s == 'z0': return ('x', x1 - 0.25 - DW, x1 - 0.25, z0 - TP / 2, 'b', 1)
    if s == 'x1': return ('z', z1 - 0.25 - DW, z1 - 0.25, x1 + TP / 2, 'b', -1)
    return ('z', z0 + 0.25, z0 + 0.25 + DW, x0 - TP / 2, 'a', 1)
BATH_W = 1.75; BATH_D = 2.0; BATH_DOOR = (0.95, 1.85)              # banheiro no canto do lado lx0, junto do corredor

# ============================================================================ terreno
ROAD = sbox(SX0, 31.0, SX1, SZ1)
WALK = sbox(SX0, 28.6, SX1, 30.85)
CURB = sbox(SX0, 30.85, SX1, 31.0).difference(sbox(-31.0, 30.0, -23.0, 32.0)).difference(sbox(0.5, 30.0, 10.0, 32.0))
AMB = unary_union([sbox(-1.5, 19.6, 11.5, 28.6), sbox(0.5, 28.6, 10.0, 31.0)])
AMB_APRON = sbox(-1.5, 18.0, 11.5, 19.6)
PARK = unary_union([sbox(-33.0, -12.0, -17.0, 28.6), sbox(-31.0, 28.6, -23.0, 31.0)])
BEDS = [sbox(-14.0, 6.0, -10.0, 7.3), sbox(-5.8, 6.0, -0.0, 7.3), sbox(-1.3, 7.3, 0.0, 18.0), sbox(-14.0, -7.3, 10.0, -6.0), sbox(-15.3, -6.0, -14.0, -1.6), sbox(-15.3, 1.6, -14.0, 6.0)]
PLAZA = unary_union([sbox(-15.0, 6.0, 0.0, 13.0), sbox(-10.0, 13.0, -6.0, 28.6), sbox(-17.0, -1.6, -14.0, 1.6), sbox(10.0, -1.6, 13.0, 18.0),
                     sbox(-17.0, 13.0, -10.0, 15.0)]).difference(unary_union(BEDS))
OUTER = sbox(SX0, SZ0, SX1, SZ1).difference(FOOT).difference(ROAD).difference(WALK).difference(CURB).difference(AMB).difference(AMB_APRON) \
    .difference(PARK).difference(PLAZA).difference(unary_union(BEDS))
STALLS_W = [(-33.0, z) for z in np.arange(-10.6, 26.0, 2.6)]     # vagas: x da guia do fundo, z do meio
STALLS_E = [(-17.0, z) for z in np.arange(-10.6, 26.0, 2.6)]
def paving(poly, y1, joints=1.5, mat='concrete', gap=0.006, y0=GY):
    p = Piece(); b = poly.bounds
    for x in np.arange(b[0], b[2], joints):
        for z in np.arange(b[1], b[3], joints):
            q = sbox(x + gap, z + gap, x + joints - gap, z + joints - gap).intersection(poly); ext_y(p, mat, q, y0, y1)
    ext_y(p, 'dark', poly.buffer(-0.002, join_style=2), y0, y1 - 0.008)
    return p
def site():
    """Lote: gramado, canteiros de casca, calcada e praca de concreto com juntas, guias, estacionamento e acesso de ambulancias de
    asfalto com faixas pintadas, rua com faixa amarela tracejada."""
    p = Piece()
    ext_y(p, 'grass', OUTER, GY, 0.0)
    for b in BEDS: ext_y(p, 'mulch', b, GY, 0.02)
    p.merge(paving(PLAZA, 0.0, 1.5, 'concrete')); p.merge(paving(WALK, 0.0, 1.6, 'conc_s')); p.merge(paving(AMB_APRON, 0.0, 1.6, 'conc_s'))
    ext_y(p, 'curb', CURB, GY, 0.12)
    ext_y(p, 'asphalt', unary_union([ROAD, AMB, PARK]), GY, -0.03)
    for x in np.arange(SX0 + 1.0, SX1 - 2.0, 4.0): ext_y(p, 'line_y', sbox(x, 33.4, x + 2.0, 33.52), -0.03, -0.027)
    for (xb, zc) in STALLS_W + STALLS_E:
        for dz in (-1.3, 1.3):
            sg = 1 if xb < -25 else -1; a, b_ = sorted((xb, xb + sg * 5.2)); ext_y(p, 'line_w', sbox(a, zc + dz - 0.05, b_, zc + dz + 0.05), -0.03, -0.027)
    # faixa de ambulancias: caixa amarela de parada e linhas laterais
    for (a, b_) in ((-1.0, -0.88), (10.88, 11.0)): ext_y(p, 'line_y', sbox(a, 19.8, b_, 28.0), -0.03, -0.027)
    box_ = sbox(1.0, 20.0, 9.0, 27.0); ext_y(p, 'line_y', box_.difference(box_.buffer(-0.12, join_style=2)), -0.03, -0.027)
    for k in range(6): z = 20.6 + k * 1.1; ext_y(p, 'line_y', Polygon([(1.1, z), (1.3, z), (8.9, z + 0.6), (8.7, z + 0.6)]).intersection(box_), -0.03, -0.027)
    return p
# ============================================================================ fachadas (envoltoria de um pavimento)
# (nome, eixo, coordenada da face, sentido para fora, u0, u1, centros das janelas em u)
FACS = [('N', 'x', -6.0, -1, -14.0, 10.0, [-13, -11, -9, -7, -5, -3, 7, 9]),
        ('E', 'z', 10.0, 1, -5.7, 17.7, [-5, -3, 0, 3, 5, 7, 9, 11, 13, 15, 17]),
        ('SB', 'x', 18.0, 1, 0.0, 10.0, [1, 3, 5, 7, 9]),
        ('WB', 'z', 0.0, -1, 6.0, 17.7, [7, 9, 11, 13, 15, 17]),
        ('SA', 'x', 6.0, 1, -13.7, 0.3, [-13, -11, -9, -7, -5, -3, -1]),
        ('WA', 'z', -14.0, -1, -5.7, 6.0, [-5, -3, 0, 3, 5])]
WWIN = 1.1                                                         # largura das janelas
WIN_T = (0.9, 2.4); WIN_G = (0.75, 2.75)                           # peitoril e verga (andares e terreo)
STAIR_WIN = (-0.8, 0.8, 2.0, 2.95)                                # janela alta da escada (acima do patamar)
ENTR = (-9.6, -6.4, 0.0, 3.0); ER_DOOR = (3.9, 6.1, 0.0, 3.0)      # vitrines das entradas (u em x)
SIDE_DOOR = (-0.55, 0.55, 0.0, 2.4)                                # portas das pontas do corredor (oeste e leste, u em z)
def fac_frame(f):
    """Moldura local da fachada (x ao longo, +z para fora, face em z = 0): (matriz, sinal de u -> x local)."""
    n, ax, c, s = f[:4]
    if ax == 'x': return (rot_y(0, (0, 0, c)), 1) if s > 0 else (rot_y(180, (0, 0, c)), -1)
    return (rot_y(90, (c, 0, 0)), -1) if s > 0 else (rot_y(-90, (c, 0, 0)), 1)
def fac_openings(f, kind):
    """Vaos da fachada em u: janelas [(a, b, ya, yb, tipo)] e portas."""
    n = f[0]; ya, yb = WIN_G if kind == 'g' else WIN_T; out = []
    for u in f[6]:
        if kind == 'g' and n == 'SA' and u in (-9, -7): continue
        if kind == 'g' and ((n in ('WA', 'E') and u == 0) or (n == 'SB' and u == 5)): continue
        out.append((u - WWIN / 2, u + WWIN / 2, ya, yb, 'win'))
    if n == 'N': out.append(STAIR_WIN + ('stair',))
    if kind == 'g':
        if n == 'SA': out.append(ENTR + ('entr',))
        if n == 'SB': out.append(ER_DOOR + ('entr',))
        if n in ('WA', 'E'): out.append(SIDE_DOOR + ('door',))
    return out
def storefront(q, a, b, ya, yb, doors):
    """Vitrine de aluminio escuro: montantes, travessa da bandeira, vidros fixos laterais e bandeira (as folhas sao pecas)."""
    z0, z1 = -0.2, -0.1; f = 0.05; yt = 2.4
    q.box('alu_d', a, a + f, ya, yb, z0, z1); q.box('alu_d', b - f, b, ya, yb, z0, z1)
    for (u, v) in doors:
        if u - f > a + f: q.box('alu_d', u - f, u, ya, yt, z0, z1)
        if v + f < b - f: q.box('alu_d', v, v + f, ya, yt, z0, z1)
    q.box('alu_d', a + f, b - f, yt, yt + 0.06, z0, z1); q.box('alu_d', a + f, b - f, yb - f, yb, z0, z1)
    q.box('glass', a + f, b - f, yt + 0.06, yb - f, -0.152, -0.148)
    for (u, v) in segs_excl([(du - f, dv + f) for (du, dv) in doors], a + f, b - f):
        q.box('alu_d', u, v, ya, ya + 0.12, z0, z1); q.box('glass', u, v, ya + 0.12, yt, -0.152, -0.148)
def facade(f, kind):
    """Uma fachada de um pavimento na moldura local: parede de 2 camadas (tijolo ou pedra por fora, reboco por dentro), janelas
    de guilhotina com bandeira, peitoril e verga de pedra com fecho, peitoril interno, vitrines e soleiras."""
    M, us = fac_frame(f); q = Piece()
    y0 = GY - Y0 if kind == 'g' else 0.0; out = 'stone' if kind == 'g' else 'brick'
    l0, l1 = sorted((us * f[4], us * f[5]))
    ops = [(*sorted((us * a, us * b)), ya, yb, k) for (a, b, ya, yb, k) in fac_openings(f, kind)]
    wall2(q, 'x', l0, l1, 0.0, -T, [o[:4] for o in ops], y0, H, out, 'plaster')
    for (a, b, ya, yb, k) in ops:
        xm = (a + b) / 2
        if k in ('win', 'stair'):
            hung(q, a, b, ya, yb, -0.2)
            q.box('stone', a - 0.08, b + 0.08, ya - 0.07, ya + 0.02, 0.0, 0.05); q.box('stone', a, b, ya, ya + 0.02, -0.1, 0.0)
            if kind == 't':
                q.box('stone', a - 0.12, b + 0.12, yb, yb + 0.3, 0.0, 0.025); q.box('stone_d', xm - 0.1, xm + 0.1, yb - 0.03, yb + 0.34, 0.0, 0.045)
            else:
                q.box('stone_d', a - 0.1, b + 0.1, yb, yb + 0.22, 0.0, 0.03)
            q.box('counter', a - 0.06, b + 0.06, ya - 0.025, ya, -T - 0.035, -T)
        elif k == 'entr':
            dd = [(-9.0, -7.0)] if f[0] == 'SA' else [(4.0, 6.0)]
            dd = [tuple(sorted((us * u, us * v))) for (u, v) in dd]
            storefront(q, a, b, ya, yb, dd)
            q.box('alu', a + 0.002, b - 0.002, ya, ya + 0.012, -T, 0.0); q.box('stone_d', a - 0.3, b + 0.3, -Y0, -0.0005, 0.0, 1.2)
            q.box('stone_d', a - 0.12, b + 0.12, yb, yb + 0.25, 0.0, 0.04)
        elif k == 'door':
            q.box('alu_d', a, a + 0.05, 0.0, yb, -0.2, -0.1); q.box('alu_d', b - 0.05, b, 0.0, yb, -0.2, -0.1); q.box('alu_d', a + 0.05, b - 0.05, yb - 0.05, yb, -0.2, -0.1)
            q.box('alu', a + 0.002, b - 0.002, ya, ya + 0.012, -T, 0.0); q.box('stone_d', a - 0.3, b + 0.3, -Y0, -0.0005, 0.0, 0.9)
            q.box('stone_d', a - 0.12, b + 0.12, yb, yb + 0.25, 0.0, 0.04)
            q.box('metal', xm - 0.08, xm + 0.08, yb + 0.35, yb + 0.5, 0.0, 0.05); q.hull('lamp_glass', [(xm + dx, yb + dy, z) for dx in (-0.07, 0.07) for dy in (0.36, 0.49) for z in (0.05, 0.14)])
    return q, M
CORNERS = [(-14.0, -6.0, -1, -1), (10.0, -6.0, 1, -1), (10.0, 18.0, 1, 1), (0.0, 18.0, -1, 1), (-14.0, 6.0, -1, 1)]
def quoins(p, y0, y1, mat='stone', d=0.02, h=0.3):
    """Cunhais de pedra nas quinas externas, alternando perna longa e curta nas duas faces."""
    for (x, z, sx, sz) in CORNERS:
        for k, y in enumerate(np.arange(y0, y1 - 1e-6, h)):
            lx, lz = (0.45, 0.25) if k % 2 == 0 else (0.25, 0.45)
            a, b = sorted((x - sx * lx, x + sx * d)); c, e = sorted((z, z + sz * d)); p.box(mat, a, b, y + 0.006, y + h - 0.006, c, e)
            a, b = sorted((x, x + sx * d)); c, e = sorted((z - sz * lz, z)); p.box(mat, a, b, y + 0.006, y + h - 0.006, c, e)
INNER = off(FOOT, -T)
def shell(kind):
    """Envoltoria de um pavimento (pivo: piso do pavimento): 6 fachadas, cunhais, faixa de pedra na laje, embasamento e cornija
    do terreo, rodape de vinil por dentro (para nas portas)."""
    p = Piece()
    for f in FACS:
        q, M = facade(f, kind); p.merge(q, M)
    ring = lambda d0, d1: off(FOOT, d1).difference(off(FOOT, d0))
    gaps = []
    if kind == 'g':
        gaps = [sbox(ENTR[0], 5.0, ENTR[1], 7.0), sbox(ER_DOOR[0], 17.0, ER_DOOR[1], 19.0), sbox(-15.0, SIDE_DOOR[0], -13.0, SIDE_DOOR[1]), sbox(9.0, SIDE_DOOR[0], 11.0, SIDE_DOOR[1])]
        gp = [g.buffer(0.09, join_style=2) for g in gaps]
        ext_y(p, 'stone_d', ring(0.0, 0.05).difference(unary_union(gp)), GY - Y0, 0.55)
        ext_y(p, 'stone_d', ring(0.0, 0.05), H - 0.38, H - 0.26); ext_y(p, 'stone', ring(0.0, 0.1), H - 0.26, H)
    else:
        ext_y(p, 'stone', ring(0.0, 0.04), H - 0.3, H)
        quoins(p, 0.0, H - 0.3)
    bb = off(FOOT, -T).difference(off(FOOT, -T - 0.012))
    bb = bb.difference(unary_union([g.buffer(0.1, join_style=2) for g in gaps])) if gaps else bb.difference(STAIR_HOLE.buffer(0.012, join_style=2))
    ext_y(p, 'vinyl', bb, 0.0, 0.1)
    return p
# ============================================================================ paredes internas, lajes, escada e elevadores
STAIR_DOOR = (-0.55, 0.55); ELEV_X = (3.0, 5.0)                    # porta da escada (x) e centro das portas dos elevadores
STAIR_HOLE = sbox(-1.94, -5.7, 1.94, -2.3)
NURSE_A = (2.3, 3.7); NURSE_B = (1.6, 3.4); NURSE_PASS = (4.35, 5.35)
ER_DD = (4.05, 5.95)                                               # porta dupla saguao -> pronto-socorro (terreo)
LOBBY_COLS = [(-10.0, 1.06), (-6.0, 1.06), (-2.0, 1.06), (2.0, 1.06)]
def rdoor(k):
    ax, a, b, c, hg, into = room_door(k); return (a, b, 0.0, DHB, 'door')
def walls_spec(kind):
    """Paredes internas como (eixo, u0, u1, v0, v1, vaos)."""
    zN, zS = (-1.0 - TP, -1.0), (1.0, 1.0 + TP)
    N = ['N1', 'N2', 'N3', 'N4']
    north = [rdoor(k) for k in N] + [(STAIR_DOOR[0], STAIR_DOOR[1], 0.0, DHB, 'door')]
    W = [('x', -13.7, 9.7, *zN, north)]
    for x in (-10.0, -6.0, -2.0, 2.0, 4.0, 6.0): W.append(('z', -5.7, -1.0 - TP, x - TP / 2, x + TP / 2, []))
    W.append(('x', 6.0 + TP, 9.7, *zS, []))                                                 # parede norte do quarto da juncao
    if kind == 't':
        W.append(('x', -13.7, 4.0, *zS, [rdoor(k) for k in ('S1', 'S2', 'S3', 'S4')] + [(NURSE_A[0], NURSE_A[1], 0.95, 2.1, 'counter')]))
        for x in (-10.0, -6.0, -2.0, 2.0): W.append(('z', 1.0 + TP, 5.7, x - TP / 2, x + TP / 2, []))
        W.append(('x', 0.3, 4.0 - TP, 5.7, 5.7 + TP, []))
        W.append(('z', 1.0 + TP, 17.7, 4.0 - TP, 4.0, [rdoor(k) for k in ('W1', 'W2', 'W3')] + [(NURSE_B[0], NURSE_B[1], 0.95, 2.1, 'counter'), (NURSE_PASS[0], NURSE_PASS[1], 0.0, DHB, 'pass')]))
        W.append(('z', 1.0, 17.7, 6.0, 6.0 + TP, [rdoor(k) for k in ('E0', 'E1', 'E2', 'E3')]))
        for z in (10.0, 14.0): W.append(('x', 0.3, 4.0 - TP, z - TP / 2, z + TP / 2, []))
        for z in (6.0, 10.0, 14.0): W.append(('x', 6.0 + TP, 9.7, z - TP / 2, z + TP / 2, []))
    else:
        W.append(('z', 1.0, 5.94, 6.0, 6.0 + TP, [rdoor('E0')]))
        W.append(('x', 6.0 + TP, 9.7, 5.94, 6.06, []))
        W.append(('x', 0.3, 6.0, 5.7, 5.7 + TP, [(ER_DD[0], ER_DD[1], 0.0, DHB, 'door')]))
    return W
def door_zones(kind):
    out = []
    for (ax, u0, u1, v0, v1, holes) in walls_spec(kind):
        for (a, b, y0, y1, k) in holes:
            if y0 > 0.01: continue
            out.append(sbox(a - 0.1, v0 - 0.2, b + 0.1, v1 + 0.2) if ax == 'x' else sbox(v0 - 0.2, a - 0.1, v1 + 0.2, b + 0.1))
    return out
def rail_runs(kind):
    """Faces do corredor com corrimao: (eixo, u0, u1, v da face, sentido para o corredor)."""
    R = [('x', -13.7, 9.7, -1.0, 1)]
    if kind == 't': R += [('x', -13.7, 3.88, 1.0, -1), ('z', 1.12, 17.7, 4.0, 1)]
    R += [('x', 6.12, 9.7, 1.0, -1), ('z', 1.0 if kind == 't' else 1.12, 17.7 if kind == 't' else 5.94, 6.0, -1)]
    return R
def walls(kind):
    """Paredes internas de um pavimento (pivo: piso): divisorias de reboco com batentes, balcoes do posto de enfermagem, rodape de
    vinil (para nas portas), corrimao de madeira nos corredores, portas dos elevadores com botoeira e sinalizacao sem texto."""
    p = Piece(); spec = walls_spec(kind)
    for (ax, u0, u1, v0, v1, holes) in spec:
        wall_grid(p, ax, u0, u1, v0, v1, [h[:4] for h in holes], 0.0, CH, 'plaster')
        vc = (v0 + v1) / 2
        for (a, b, y0, y1, k) in holes:
            uc = (a + b) / 2
            if k in ('door', 'pass'):
                q = Piece(); door_casing(q, b - a, TP, y1)
                p.merge(q, rot_y(0, (uc, 0, vc)) if ax == 'x' else rot_y(90, (vc, 0, uc)))
            if k == 'counter':
                bx(p, 'counter', ax, a - 0.05, b + 0.05, y0 - 0.04, y0 + 0.02, vc - TP / 2 - 0.28, vc + TP / 2 + 0.28)
                for (vv0, vv1) in ((vc - TP / 2 - 0.02, vc - TP / 2), (vc + TP / 2, vc + TP / 2 + 0.02)):
                    bx(p, 'frame', ax, a - 0.06, a, y0, y1 + 0.06, vv0, vv1); bx(p, 'frame', ax, b, b + 0.06, y0, y1 + 0.06, vv0, vv1); bx(p, 'frame', ax, a, b, y1, y1 + 0.06, vv0, vv1)
                bx(p, 'glass', ax, a, b, y0 + 0.5, y1, vc - 0.004, vc + 0.004); bx(p, 'frame', ax, a, b, y0 + 0.47, y0 + 0.5, vc - 0.02, vc + 0.02)
    # rodape: contorno das paredes (fica escondido onde as paredes se encontram), aberto nas portas
    fp = unary_union([sbox(u0, v0, u1, v1) if ax == 'x' else sbox(v0, u0, v1, u1) for (ax, u0, u1, v0, v1, h) in spec])
    if kind == 'g': fp = unary_union([fp] + [sbox(x - 0.2, z - 0.2, x + 0.2, z + 0.2) for (x, z) in LOBBY_COLS])
    bb = off(fp, 0.012).difference(fp).difference(unary_union(door_zones(kind))).intersection(INNER)
    if kind == 't': bb = bb.difference(STAIR_HOLE)
    ext_y(p, 'vinyl', bb, 0.0, 0.1)
    if kind == 'g':
        for (x, z) in LOBBY_COLS:
            p.cham('plaster', x - 0.2, x + 0.2, 0.0, CH, z - 0.2, z + 0.2, 0.02)
            for (a, b) in ((0.1, 0.13), (1.0, 1.04)): p.cham('steel', x - 0.212, x + 0.212, a, b, z - 0.212, z + 0.212, 0.004)
    # corrimao de madeira nas faces do corredor (para nas portas e balcoes)
    gaps = {}
    for (ax, u0, u1, v0, v1, holes) in spec:
        for (a, b, y0, y1, k) in holes: gaps.setdefault(ax, []).append((a - 0.15, b + 0.15, v0, v1))
    for (ax, u0, u1, vf, sg) in rail_runs(kind):
        gs = [(a, b) for (a, b, v0, v1) in gaps.get(ax, []) if v0 - 0.01 <= vf <= v1 + 0.01]
        if ax == 'x' and vf < 0: gs += [(x - 0.75, x + 0.75) for x in ELEV_X]
        for (a, b) in segs_excl(gs, u0 + 0.12, u1 - 0.12):
            if b - a < 0.4: continue
            bx(p, 'wood', ax, a, b, 0.86, 0.94, vf + sg * 0.045, vf + sg * 0.1)
            for uu in np.arange(a + 0.15, b - 0.1, 1.2): bx(p, 'steel', ax, uu - 0.02, uu + 0.02, 0.88, 0.92, vf, vf + sg * 0.05)
            bx(p, 'vinyl_b', ax, a, b, 0.22, 0.32, vf, vf + sg * 0.012)
    # portas dos elevadores (lado do corredor, face z = -1,0), botoeira e indicador
    zf = -1.0
    for xc in ELEV_X:
        p.box('steel', xc - 0.62, xc + 0.62, 0.0, 2.32, zf, zf + 0.03)
        p.box('chrome', xc - 0.5, xc - 0.004, 0.0, 2.2, zf + 0.03, zf + 0.04); p.box('chrome', xc + 0.004, xc + 0.5, 0.0, 2.2, zf + 0.03, zf + 0.04)
        p.box('dark', xc - 0.5, xc + 0.5, 2.2, 2.204, zf + 0.03, zf + 0.04)
        p.box('dark', xc - 0.3, xc + 0.3, 2.42, 2.6, zf, zf + 0.02)
        for dx, up in ((-0.12, True), (0.12, False)):
            pts = [(xc + dx - 0.05, 2.47), (xc + dx + 0.05, 2.47), (xc + dx, 2.56)] if up else [(xc + dx - 0.05, 2.55), (xc + dx + 0.05, 2.55), (xc + dx, 2.46)]
            ext(p, 'screen_g', Polygon(pts), zf + 0.02, zf + 0.024)
        xb = xc + 0.8; p.cham('steel', xb - 0.07, xb + 0.07, 0.95, 1.3, zf, zf + 0.02, 0.004)
        for yy in (1.06, 1.19): disc_z(p, 'chrome', 0.025, zf + 0.02, zf + 0.03, xb, yy, 14)
    # sinal de saida (pictograma de pessoa correndo e seta) sobre a porta da escada
    p.box('dark', -0.3, 0.3, DHB + 0.15, DHB + 0.4, zf, zf + 0.05)
    sx = Piece(); ext(sx, 'screen_g', sbox(-0.28, DHB + 0.17, 0.28, DHB + 0.38), 0.0, 0.004); p.merge(sx, tr(0, 0, zf + 0.05))
    run = unary_union([Point(-0.12, DHB + 0.335).buffer(0.025, 12), LineString([(-0.13, DHB + 0.31), (-0.1, DHB + 0.24), (-0.16, DHB + 0.19)]).buffer(0.012),
                       LineString([(-0.1, DHB + 0.24), (-0.04, DHB + 0.2)]).buffer(0.012), LineString([(-0.2, DHB + 0.28), (-0.13, DHB + 0.3), (-0.07, DHB + 0.27)]).buffer(0.01),
                       Polygon([(0.04, DHB + 0.27), (0.17, DHB + 0.27), (0.17, DHB + 0.3), (0.22, DHB + 0.275), (0.17, DHB + 0.25), (0.17, DHB + 0.28)]).buffer(0.0),
                       sbox(0.04, DHB + 0.268, 0.18, DHB + 0.282), Polygon([(0.17, DHB + 0.24), (0.24, DHB + 0.275), (0.17, DHB + 0.31)])])
    ext(p, 'paint_w', run, zf + 0.054, zf + 0.057)
    return p

def slab(kind):
    """Laje de um pavimento (pivo: piso de cima): forro liso com luminarias de embutir, laje de concreto e piso de vinil;
    'g' e o contrapiso do terreo (granilite). O vao da escada fica aberto (menos no terreo)."""
    p = Piece()
    if kind == 'g':
        ext_y(p, 'concrete', INNER, GY - Y0, -0.012); ext_y(p, 'terrazzo', INNER, -0.012, 0.0)
        for x in np.arange(-13.5, 9.6, 2.0): ext_y(p, 'brass', sbox(x - 0.004, -5.7, x + 0.004, 17.7).intersection(INNER), 0.0, 0.002)
        return p
    area = INNER.difference(STAIR_HOLE)
    ext_y(p, 'ceil', area, -ST, -ST + 0.012); ext_y(p, 'conc_s', area, -ST + 0.012, -0.006); ext_y(p, 'vinyl_f', area, -0.006, 0.0)
    yl = -ST
    def panel(x, z, rot=False, w=1.2, d=0.6):
        hw, hd = (d / 2, w / 2) if rot else (w / 2, d / 2)
        p.box('metal', x - hw, x + hw, yl - 0.04, yl, z - hd, z + hd); p.box('lamp_glass', x - hw + 0.04, x + hw - 0.04, yl - 0.045, yl - 0.035, z - hd + 0.04, z + hd - 0.04)
    def down(x, z):
        p.cyl('metal', 0.1, yl - 0.02, yl, x, z, 16); p.cyl('lamp_glass', 0.08, yl - 0.025, yl - 0.015, x, z, 16)
    def sprink(x, z):
        p.cyl('chrome', 0.03, yl - 0.012, yl, x, z, 8); p.cyl('chrome', 0.008, yl - 0.05, yl - 0.012, x, z, 6); p.cyl('chrome', 0.02, yl - 0.056, yl - 0.05, x, z, 8)
    def grille(x, z, s=0.6):
        p.box('metal', x - s / 2, x + s / 2, yl - 0.02, yl, z - s / 2, z + s / 2)
        for k in range(1, 6): d_ = -s / 2 + k * s / 6; p.box('dark', x - s / 2 + 0.05, x + s / 2 - 0.05, yl - 0.021, yl - 0.02, z + d_ - 0.01, z + d_ + 0.01)
    # corredores
    for x in np.arange(-12.0, 9.0, 3.0): panel(x, 0.0)
    if kind == 't':
        for z in np.arange(3.0, 17.0, 3.0): panel(5.0, z, True)
    else:
        for z in (3.0,): panel(5.0, z, True)
    for x in (-10.5, -4.5, 1.5, 7.5): grille(x, 0.0, 0.45); sprink(x + 0.9, 0.0)
    # quartos (ou consultorios) do pavimento de baixo
    rooms = list(ROOMS) if kind == 't' else ROOMS_G
    for k in rooms:
        fr, w, dd = room_frame(k); lx0 = -w / 2
        x, z = l2w(fr, 0.4, dd * 0.6); panel(x, z, fr[1] in (90.0, -90.0))
        x, z = l2w(fr, lx0 + BATH_W / 2, BATH_D / 2); down(x, z)
        x, z = l2w(fr, 0.6, dd * 0.25); sprink(x, z)
        x, z = l2w(fr, -w / 2 + 0.5, dd - 0.6); grille(x, z, 0.45)
    if kind == 't':
        panel(2.97, 3.4, True); down(2.97, 2.0)
    if kind == '1':
        for x in np.arange(-12.0, 3.0, 3.0):
            for z in (2.4, 4.6): panel(x, z)
        for x in (1.6, 8.4):
            for z in np.arange(7.5, 17.0, 2.5): panel(x, z, True)
        for z in np.arange(7.5, 17.0, 2.5): panel(5.0, z)
        for (x, z) in ((-9.0, 3.5), (-3.0, 3.5), (5.0, 9.0), (5.0, 14.0)): grille(x, z, 0.6); sprink(x + 1.2, z)
    return p

# ============================================================================ escada de 2 lances (pivo: piso do pavimento de baixo)
ST_Z0 = -2.3; ST_ZL = ST_Z0 - (SNR // 2 - 1) * STRD               # inicio do lance 1 e borda do patamar (-4,54)
def stair():
    """Escada de 2 lances de granilite entre 2 pavimentos: degraus com focinho antiderrapante, patamar, corrimaos de madeira nas
    paredes com suportes e guarda-corpo de aco com balaustres na borda de dentro de cada lance."""
    p = Piece(); n2 = SNR // 2; yL = n2 * SRR
    y1 = lambda z: SRR + (ST_Z0 - z) / STRD * SRR                    # linha dos focinhos do lance 1
    y2 = lambda z: yL + SRR + (z - ST_ZL) / STRD * SRR               # e do lance 2
    # lance 1 (x > 0, sobe para -z ate o patamar)
    pr = [(ST_Z0, 0.0)]
    for i in range(1, n2):
        zf = ST_Z0 - (i - 1) * STRD; pr += [(zf, i * SRR), (zf - STRD, i * SRR)]
    pr += [(ST_ZL, yL - 0.4), (ST_Z0 - (0.18 / SRR) * STRD, 0.0)]
    prof_x(p, 'terrazzo', 0.06, 1.94, pr)
    # lance 2 (x < 0, sobe para +z ate o piso de cima; o ultimo espelho e a borda da laje)
    pr = [(ST_ZL, yL - 0.4)]
    for j in range(n2 + 1, SNR):
        zb = ST_ZL + (j - n2 - 1) * STRD; pr += [(zb, j * SRR), (zb + STRD, j * SRR)]
    pr += [(ST_Z0, y2(ST_Z0) - 0.38)]
    prof_x(p, 'terrazzo', -1.94, -0.06, pr)
    p.box('terrazzo', -1.94, 1.94, yL - 0.4, yL, -5.7, ST_ZL)
    # focinhos
    for i in range(1, n2):
        zf = ST_Z0 - (i - 1) * STRD; p.box('dark', 0.08, 1.92, i * SRR - 0.03, i * SRR + 0.003, zf - 0.05, zf + 0.003)
    for j in range(n2 + 1, SNR):
        zb = ST_ZL + (j - n2 - 1) * STRD; p.box('dark', -1.92, -0.08, j * SRR - 0.03, j * SRR + 0.003, zb - 0.003, zb + 0.05)
    p.box('dark', 0.08, 1.92, yL - 0.03, yL + 0.003, ST_ZL - 0.003, ST_ZL + 0.05)
    # corrimaos de parede
    for (xw, za, zb, fy) in ((1.94, ST_Z0, ST_ZL, y1), (-1.94, ST_ZL, ST_Z0, y2)):
        xr = xw - math.copysign(0.075, xw); dz = math.copysign(0.3, zb - za); ya, yb = fy(za) + 0.9, fy(zb) + 0.9
        seg_cyl(p, 'wood', (xr, ya, za - dz), (xr, ya, za), 0.024, 10); seg_cyl(p, 'wood', (xr, ya, za), (xr, yb, zb), 0.024, 10)
        seg_cyl(p, 'wood', (xr, yb, zb), (xr, yb, zb + dz), 0.024, 10)
        for t_ in (0.1, 0.5, 0.9):
            zz = za + (zb - za) * t_; yy = ya + (yb - ya) * t_; xa, xb_ = sorted((xw, xw - math.copysign(0.012, xw)))
            seg_cyl(p, 'steel', (xr, yy - 0.024, zz), (xr, yy - 0.07, zz), 0.008, 6); seg_cyl(p, 'steel', (xr, yy - 0.07, zz), (xw, yy - 0.07, zz), 0.008, 6)
            p.box('steel', xa, xb_, yy - 0.1, yy - 0.04, zz - 0.035, zz + 0.035)
    # guarda-corpo de dentro (balaustres sobre os degraus)
    for (xg, fy, treads) in ((0.1, y1, [(ST_Z0 - i * STRD, ST_Z0 - (i - 1) * STRD, i * SRR) for i in range(1, n2)]),
                             (-0.1, y2, [(ST_ZL + j * STRD, ST_ZL + (j + 1) * STRD, yL + (j + 1) * SRR) for j in range(n2 - 1)])):
        for (za, zb, yt) in treads:
            for zz in (za + STRD * 0.25, za + STRD * 0.75): seg_cyl(p, 'steel', (xg, yt, zz), (xg, fy(zz) + 0.95, zz), 0.008 if abs(zz - (za + zb) / 2) > 0.01 else 0.012, 6)
        z0_, z1_ = treads[0][0] + (STRD if fy is y1 else 0.0), treads[-1][0] + (0.0 if fy is y1 else STRD)
        seg_cyl(p, 'steel_d', (xg, fy(z0_) + 0.95, z0_), (xg, fy(z1_) + 0.95, z1_), 0.028, 10)
        seg_cyl(p, 'steel_d', (xg, fy(z0_) + 0.45, z0_), (xg, fy(z1_) + 0.45, z1_), 0.012, 6)
    # pilar do guarda-corpo no patamar e travessa ligando os 2 lances
    for xg in (0.1, -0.1): seg_cyl(p, 'steel_d', (xg, yL, ST_ZL - 0.06), (xg, yL + 0.95 + 0.2 * (xg < 0), ST_ZL - 0.06), 0.03, 10)
    seg_cyl(p, 'steel_d', (0.1, yL + 0.95, ST_ZL - 0.06), (-0.1, yL + 0.95, ST_ZL - 0.06), 0.028, 10)
    return p
# ============================================================================ portas
def door_room(w=1.08, h=2.188, t=0.045, mat='laminate', glass=True):
    """Porta de quarto de hospital (pivo: dobradica, embaixo): folha de laminado com bordas, visor estreito, chapa de chute de aco,
    macanetas de alavanca dos 2 lados e 3 dobradicas."""
    p = Piece(); p.cham(mat, 0.0, w, 0.0, h, -t / 2, t / 2, 0.004)
    for z in (1, -1):
        zz = sorted((z * t / 2, z * (t / 2 + 0.003)))
        p.box('steel', 0.03, w - 0.03, 0.03, 0.28, *zz)
        if glass:
            p.box('frame', w - 0.36, w - 0.14, 1.05, 1.85, *sorted((z * t / 2, z * (t / 2 + 0.008))))
        seg_cyl(p, 'chrome', (w - 0.08, 1.02, z * t / 2), (w - 0.08, 1.02, z * (t / 2 + 0.05)), 0.012, 6)
        seg_cyl(p, 'chrome', (w - 0.08, 1.02, z * (t / 2 + 0.05)), (w - 0.22, 1.02, z * (t / 2 + 0.05)), 0.011, 6)
        p.box('chrome', w - 0.11, w - 0.05, 0.92, 1.1, *sorted((z * t / 2, z * (t / 2 + 0.006))))
    if glass: p.box('glass', w - 0.34, w - 0.16, 1.07, 1.83, -t / 2 - 0.005, t / 2 + 0.005)
    for yy in (0.25, h / 2, h - 0.25): p.cyl('chrome', 0.008, yy - 0.06, yy + 0.06, -0.004, t / 2 + 0.002, 8)
    return p
def door_double(w=0.93, h=2.188, t=0.05):
    """Folha de porta dupla de vai-e-vem com visor grande e placa de empurrar (pivo: dobradica, embaixo)."""
    p = Piece(); p.cham('laminate', 0.0, w, 0.0, h, -t / 2, t / 2, 0.004)
    for z in (1, -1):
        zz = sorted((z * t / 2, z * (t / 2 + 0.003)))
        p.box('steel', 0.03, w - 0.03, 0.03, 0.4, *zz); p.box('chrome', w - 0.32, w - 0.08, 1.0, 1.3, *zz)
        p.box('frame', 0.18, w - 0.18, 1.35, 1.95, *sorted((z * t / 2, z * (t / 2 + 0.008))))
    p.box('glass', 0.2, w - 0.2, 1.37, 1.93, -t / 2 - 0.005, t / 2 + 0.005)
    return p

# ============================================================================ moveis de hospital
def hospital_bed(p, M, back=30.0, rails=True, mat='bed_b'):
    """Cama hospitalar (pivo: meio da cabeceira, chao; o pe fica em +Z): chassi com 4 rodizios, colunas, estrado, colchao com
    cabeceira levantada, lencol, travesseiro, manta dobrada, cabeceira e peseira de laminado, grades laterais, suporte de soro."""
    q = Piece(); ym = 0.56
    q.box('steel_d', -0.36, 0.36, 0.2, 0.3, 0.2, 1.9)
    for z in (0.2, 1.9):
        for x in (-0.36, 0.36):
            q.box('steel_d', x - 0.03, x + 0.03, 0.12, 0.2, z - 0.03, z + 0.03); disc_x(q, 'rubber', 0.06, x - 0.02, x + 0.02, 0.07, z + 0.04, 10)
    for z in (0.55, 1.5): q.box('steel', -0.08, 0.08, 0.3, ym - 0.04, z - 0.08, z + 0.08)
    q.box('steel', -0.45, 0.45, ym - 0.06, ym, 0.08, 2.0)
    # colchao: pe plano e cabeceira inclinada
    zk = 0.78; a = math.radians(back); L1 = zk - 0.1
    q.cham(mat, -0.44, 0.44, ym, ym + 0.15, zk, 1.98, 0.03); q.cham('bed_w', -0.445, 0.445, ym + 0.1, ym + 0.152, zk + 0.02, 1.4, 0.01)
    pts = []
    for (dz, dy) in ((0.0, 0.0), (0.0, 0.15), (L1, 0.0), (L1, 0.15)):
        pts += [(x, ym + dy * math.cos(a) + dz * math.sin(a), zk - dz * math.cos(a) + dy * math.sin(a)) for x in (-0.44, 0.44)]
    q.hull(mat, pts)
    c = np.array([0.0, ym + 0.15 * math.cos(a) + (L1 - 0.25) * math.sin(a), zk - (L1 - 0.25) * math.cos(a) + 0.15 * math.sin(a)])
    q.hull('bed_w', [c + np.array([x, dy, dz]) for x in (-0.3, 0.3) for dy in (0.0, 0.12) for dz in (-0.18, 0.18)])
    q.cham('curtain', -0.44, 0.44, ym + 0.15, ym + 0.24, 1.55, 1.95, 0.03)
    # cabeceira e peseira
    q.cham('laminate', -0.48, 0.48, 0.4, 1.05, 0.0, 0.05, 0.015); q.cham('cart_w', -0.49, 0.49, 1.0, 1.07, -0.005, 0.055, 0.015)
    q.cham('laminate', -0.48, 0.48, 0.42, 0.92, 2.02, 2.07, 0.015); q.cham('cart_w', -0.49, 0.49, 0.88, 0.95, 2.015, 2.075, 0.015)
    if rails:
        for s in (-1, 1):
            xa, xb_ = sorted((s * 0.46, s * 0.48)); q.cham('cart_w', xa, xb_, ym + 0.2, ym + 0.48, 0.18, 0.95, 0.008)
            q.box('dark', xa - 0.002, xb_ + 0.002, ym + 0.34, ym + 0.4, 0.5, 0.75)
            for z in (0.3, 0.85): q.box('steel', xa, xb_, ym, ym + 0.2, z - 0.02, z + 0.02)
    seg_cyl(q, 'chrome', (-0.47, 0.4, 0.04), (-0.47, 2.0, 0.04), 0.012, 8)
    for k in range(4):
        a_ = k * math.pi / 2; seg_cyl(q, 'chrome', (-0.47, 2.0, 0.04), (-0.47 + 0.12 * math.cos(a_), 1.95, 0.04 + 0.12 * math.sin(a_)), 0.006, 6)
    q.cham('glass', -0.52, -0.42, 1.55, 1.82, 0.0, 0.08, 0.02)
    p.merge(q, M)
def headwall(p, M, L1=2.0):
    """Painel de cabeceira (pivo: meio, face da parede; para +Z): calha com tomadas, gases (bocais coloridos sem texto), luz de
    leitura, chamada de enfermagem e monitor no braco."""
    q = Piece(); x = L1 / 2
    q.cham('cart_w', -x, x, 1.35, 1.65, 0.0, 0.07, 0.01); q.box('steel', -x, x, 1.49, 1.51, 0.07, 0.072)
    for i, (xx, m) in enumerate(((-0.75, 'food_g'), (-0.6, 'paint_w'), (-0.45, 'blue'))): disc_z(q, m, 0.035, 0.07, 0.09, xx, 1.43, 12); disc_z(q, 'chrome', 0.014, 0.09, 0.11, xx, 1.43, 8)
    for xx in (0.35, 0.55, 0.75): q.box('paint_w', xx - 0.05, xx + 0.05, 1.39, 1.47, 0.07, 0.076); q.box('dark', xx - 0.02, xx + 0.02, 1.41, 1.45, 0.076, 0.078)
    q.cham('paint_r', -0.08, 0.08, 1.4, 1.46, 0.07, 0.085, 0.005)
    q.cham('cart_w', -0.3, 0.3, 1.58, 1.64, 0.07, 0.14, 0.01); q.box('lamp_glass', -0.28, 0.28, 1.575, 1.58, 0.075, 0.135)
    # monitor de sinais vitais no braco articulado
    q.box('steel', 0.62, 0.72, 1.7, 1.86, 0.0, 0.03); seg_cyl(q, 'steel', (0.67, 1.78, 0.03), (0.67, 1.78, 0.32), 0.02, 8)
    q.cham('dark', 0.45, 0.89, 1.65, 1.98, 0.32, 0.4, 0.015); q.box('screen', 0.47, 0.87, 1.67, 1.96, 0.4, 0.402)
    for k, (yy, m) in enumerate(((1.92, 'screen_g'), (1.86, 'lens_b'), (1.8, 'flag_o'), (1.74, 'screen_g'))):
        pts = [(0.49 + 0.026 * i, yy + 0.014 * math.sin(i * (1.3 + 0.4 * k)) * (1 if i % 5 else 2.0)) for i in range(15)]
        ext(q, m, LineString(pts).buffer(0.003, cap_style=2, join_style=2, mitre_limit=3), 0.402, 0.404)
    p.merge(q, M)
def bedside(p, M):
    """Mesa de cabeceira de laminado com gaveta, porta e tampo (pivo: centro de tras, chao; frente +Z)."""
    q = Piece(); q.cham('laminate', -0.22, 0.22, 0.06, 0.78, 0.0, 0.45, 0.01); q.cham('cart_w', -0.23, 0.23, 0.78, 0.81, -0.0, 0.47, 0.008)
    q.box('dark', -0.2, 0.2, 0.0, 0.06, 0.02, 0.43); q.box('cart_w', -0.2, 0.2, 0.56, 0.75, 0.45, 0.46); q.box('cart_w', -0.2, 0.2, 0.09, 0.53, 0.45, 0.46)
    for yy in (0.66, 0.46): q.box('chrome', -0.07, 0.07, yy, yy + 0.02, 0.46, 0.48)
    q.cyl('glass', 0.035, 0.81, 0.95, 0.1, 0.15, 10); q.cham('paper', -0.15, 0.0, 0.81, 0.83, 0.1, 0.32, 0.004)
    p.merge(q, M)
def overbed_table(p, M):
    """Mesa de refeicao de cama (pivo: centro do pe, chao; tampo para +X sobre a cama)."""
    q = Piece(); q.box('steel', -0.05, 0.05, 0.04, 0.08, -0.25, 0.25)
    for z in (-0.25, 0.25): q.box('steel', -0.05, 0.75, 0.04, 0.08, z - 0.03, z + 0.03); q.box('rubber', 0.66, 0.74, 0.0, 0.04, z - 0.025, z + 0.025); q.box('rubber', -0.04, 0.04, 0.0, 0.04, z - 0.025, z + 0.025)
    q.box('steel', -0.03, 0.03, 0.08, 0.9, -0.03, 0.03); q.cham('laminate', -0.08, 0.78, 0.9, 0.94, -0.22, 0.22, 0.012)
    q.cham('cart_w', 0.1, 0.42, 0.94, 0.96, -0.15, 0.15, 0.01); q.cyl('food_y', 0.04, 0.94, 1.06, 0.6, 0.0, 10)
    p.merge(q, M)
def iv_pole(p, x, z):
    for k in range(5):
        a = k * 2 * math.pi / 5; seg_cyl(p, 'chrome', (x, 0.08, z), (x + 0.28 * math.cos(a), 0.06, z + 0.28 * math.sin(a)), 0.012, 6); p.cyl('rubber', 0.03, 0.0, 0.06, x + 0.28 * math.cos(a), z + 0.28 * math.sin(a), 6)
    seg_cyl(p, 'chrome', (x, 0.06, z), (x, 2.0, z), 0.014, 8)
    for k in range(2): seg_cyl(p, 'chrome', (x, 2.0, z), (x + 0.12 * (1 if k else -1), 1.96, z), 0.006, 6)
    p.cham('glass', x + 0.06, x + 0.16, 1.62, 1.92, z - 0.03, z + 0.03, 0.02); seg_cyl(p, 'glass', (x + 0.11, 1.62, z), (x + 0.02, 1.1, z), 0.004, 4)
    p.cham('cart_w', x - 0.08, x + 0.08, 1.05, 1.25, z + 0.015, z + 0.12, 0.01); p.box('screen', x - 0.06, x + 0.06, 1.15, 1.22, z + 0.12, z + 0.122)
def tv(p, M):
    q = Piece(); q.box('steel', -0.1, 0.1, -0.1, 0.1, 0.0, 0.03); seg_cyl(q, 'steel', (0, 0, 0.03), (0, 0, 0.18), 0.02, 8)
    q.cham('dark', -0.42, 0.42, -0.26, 0.26, 0.18, 0.23, 0.01); q.box('screen', -0.4, 0.4, -0.24, 0.24, 0.23, 0.232); p.merge(q, M)
def wardrobe(p, M, w=0.6):
    """Roupeiro estreito de laminado com 2 portas e puxadores (pivo: centro de tras, chao; frente +Z)."""
    q = Piece(); x = w / 2; q.cham('laminate', -x, x, 0.06, 2.1, 0.0, 0.55, 0.01); q.box('dark', -x + 0.02, x - 0.02, 0.0, 0.06, 0.02, 0.52)
    for (a, b) in ((-x + 0.01, -0.004), (0.004, x - 0.01)) if w > 0.45 else ((-x + 0.01, x - 0.01),):
        q.box('cart_w', a, b, 0.08, 2.08, 0.55, 0.56); xh = b - 0.05 if a < -0.01 else a + 0.05
        q.box('chrome', xh - 0.012, xh + 0.012, 0.9, 1.3, 0.56, 0.58)
    p.merge(q, M)
def dispenser(p, M):
    q = Piece(); q.cham('cart_w', -0.06, 0.06, 1.2, 1.45, 0.0, 0.09, 0.01); q.box('chrome', -0.03, 0.03, 1.24, 1.28, 0.09, 0.1); q.box('blue_l', -0.04, 0.04, 1.32, 1.42, 0.09, 0.093); p.merge(q, M)
def wc_unit(p, M):
    q = wc(); p.merge(q, M)
def basin(p, M):
    """Lavatorio de louca suspenso com torneira de alavanca, espelho, saboneteira e toalheiro de papel (pivo: face da parede, chao; +Z)."""
    q = Piece(); q.hull('porcelain', [(x, y, z) for x in (-0.26, 0.26) for (y, z) in ((0.84, 0.0), (0.84, 0.46), (0.7, 0.0), (0.74, 0.4))])
    q.box('dark', -0.18, 0.18, 0.835, 0.842, 0.1, 0.38); q.cyl('chrome', 0.03, 0.55, 0.72, 0.0, 0.08, 10)
    seg_cyl(q, 'chrome', (0.0, 0.84, 0.06), (0.0, 1.0, 0.06), 0.016, 8); seg_cyl(q, 'chrome', (0.0, 1.0, 0.06), (0.0, 0.98, 0.2), 0.012, 8); seg_cyl(q, 'chrome', (0.0, 1.02, 0.06), (0.12, 1.06, 0.06), 0.008, 6)
    q.cham('chrome', -0.3, 0.3, 1.15, 1.85, 0.0, 0.02, 0.006); q.box('mirror', -0.27, 0.27, 1.18, 1.82, 0.02, 0.026)
    q.cham('cart_w', 0.4, 0.62, 1.2, 1.5, 0.0, 0.1, 0.01); q.box('dark', 0.44, 0.58, 1.195, 1.21, 0.04, 0.09)
    q.cham('cart_w', -0.5, -0.38, 1.0, 1.2, 0.0, 0.09, 0.01); q.box('chrome', -0.46, -0.42, 0.98, 1.0, 0.04, 0.08)
    p.merge(q, M)
def grab_bar(p, M, L1=0.7, y=0.8):
    q = Piece(); seg_cyl(q, 'chrome', (-L1 / 2, y, 0.07), (L1 / 2, y, 0.07), 0.016, 8)
    for x in (-L1 / 2, L1 / 2): seg_cyl(q, 'chrome', (x, y, 0.0), (x, y, 0.07), 0.014, 6); disc_z(q, 'chrome', 0.035, 0.0, 0.008, x, y, 8)
    p.merge(q, M)

# ============================================================================ quarto (pivo: meio da face do corredor; local +z para dentro)
TB = 0.1
def room(w, Dp, kind='ward'):
    """Quarto de internacao (ou consultorio, kind 'exam'), na moldura local do quarto: banheiro com paredes de reboco e azulejo,
    piso de ceramica, vaso, lavatorio, chuveiro com cortina, barras de apoio; cama hospitalar com painel de cabeceira e monitor,
    cortina de privacidade, mesa de cabeceira, mesa de refeicao, poltrona, TV, roupeiro, relogio e alcool em gel."""
    p = Piece(); lx0, lx1 = -w / 2, w / 2; bxw = lx0 + BATH_W
    wall_grid(p, 'x', lx0, bxw + TB, BATH_D, BATH_D + TB, [], 0.0, CH, 'plaster')
    wall_grid(p, 'z', 0.0, BATH_D, bxw, bxw + TB, [(BATH_DOOR[0], BATH_DOOR[1], 0.0, 2.1)], 0.0, CH, 'plaster')
    q = Piece(); door_casing(q, BATH_DOOR[1] - BATH_DOOR[0], TB, 2.1); p.merge(q, rot_y(90, (bxw + TB / 2, 0, sum(BATH_DOOR) / 2)))
    # azulejo e piso do banheiro
    ext_y(p, 'tile_c', sbox(lx0, 0.0, bxw, BATH_D), 0.0, 0.004)
    p.box('tile_c', lx0, bxw, 0.1, 2.1, 0.0, 0.004); p.box('tile_c', lx0, lx0 + 0.004, 0.1, 2.1, 0.004, BATH_D)
    p.box('tile_c', lx0 + 0.004, bxw, 0.004, 2.1, BATH_D - 0.004, BATH_D)
    for (a, b) in segs_excl([(BATH_DOOR[0] - 0.1, BATH_DOOR[1] + 0.1)], 0.004, BATH_D - 0.004): p.box('tile_c', bxw - 0.004, bxw, 0.004, 2.1, a, b)
    for (a, b, c, d) in ((lx0 + 0.004, bxw - 0.004, 0.004, 0.006), (lx0 + 0.004, lx0 + 0.006, 0.006, BATH_D - 0.004), (lx0 + 0.006, bxw - 0.004, BATH_D - 0.006, BATH_D - 0.004)):
        p.box('vinyl_t', a, b, 1.2, 1.3, c, d)
    # rodape do lado do quarto nas paredes do banheiro (para na porta)
    p.box('vinyl', lx0, bxw + TB + 0.012, 0.0, 0.1, BATH_D + TB, BATH_D + TB + 0.012)
    for (a, b) in segs_excl([(BATH_DOOR[0] - 0.1, BATH_DOOR[1] + 0.1)], 0.0, BATH_D + TB): p.box('vinyl', bxw + TB, bxw + TB + 0.012, 0.0, 0.1, a, b)
    # louças e acessorios
    wc_unit(p, rot_y(90, (lx0 + 0.006, 0.004, 0.45)))
    grab_bar(p, rot_y(90, (lx0 + 0.004, 0.0, 0.95)), 0.6, 0.85); grab_bar(p, rot_y(0, (lx0 + 0.45, 0.0, 0.004)), 0.5, 0.85)
    basin(p, rot_y(0, (lx0 + 1.05, 0.0, 0.004)))
    sh0 = BATH_D - 0.95
    ext_y(p, 'tile_c', sbox(lx0 + 0.004, sh0, lx0 + 0.95, BATH_D - 0.004), 0.004, 0.02); p.cyl('chrome', 0.05, 0.02, 0.024, lx0 + 0.48, sh0 + 0.48, 16)
    seg_cyl(p, 'chrome', (lx0 + 0.95, 2.05, sh0), (lx0 + 0.95, 2.05, BATH_D - 0.004), 0.012, 8); seg_cyl(p, 'chrome', (lx0 + 0.004, 2.05, sh0), (lx0 + 0.95, 2.05, sh0), 0.012, 8)
    for k in range(5):
        x = lx0 + 0.05 + k * 0.06; p.seg('curtain2', (x, 1.2, sh0 + (0.03 if k % 2 else -0.03)), (x + 0.06, 1.2, sh0 + (-0.03 if k % 2 else 0.03)), 0.01, 1.66)
    seg_cyl(p, 'chrome', (lx0 + 0.004, 1.1, BATH_D - 0.45), (lx0 + 0.06, 1.1, BATH_D - 0.45), 0.02, 10); seg_cyl(p, 'chrome', (lx0 + 0.03, 1.1, BATH_D - 0.45), (lx0 + 0.03, 2.0, BATH_D - 0.45), 0.012, 8)
    seg_cyl(p, 'chrome', (lx0 + 0.03, 2.0, BATH_D - 0.45), (lx0 + 0.14, 1.98, BATH_D - 0.45), 0.01, 6)
    disc_x(p, 'chrome', 0.05, lx0 + 0.12, lx0 + 0.15, 1.96, BATH_D - 0.45, 14)
    p.cham('cart_w', lx0 + 0.35, lx0 + 0.85, 0.45, 0.5, BATH_D - 0.38, BATH_D - 0.004, 0.01)           # banco de banho rebativel
    p.box('paint_r', lx0 + 0.004, lx0 + 0.03, 0.9, 1.0, 1.2, 1.25)                                     # cordao de chamada
    p.box('cart_w', bxw - 0.1, bxw - 0.004, 1.35, 1.55, 0.2, 0.32)                                      # papeleira
    yb = BATH_D + TB
    if kind == 'ward':
        zb = Dp - 0.83
        hospital_bed(p, rot_y(-90, (lx1 - 0.02, 0.0, zb)))
        headwall(p, rot_y(-90, (lx1, 0.0, zb)))
        bedside(p, rot_y(-90, (lx1, 0.0, zb - 0.95)))
        overbed_table(p, rot_y(90, (lx1 - 1.3, 0.0, zb + 0.62)))
        iv_pole(p, lx1 - 0.75, zb - 0.72)
        # trilho de cortina em U (sobre a cama) com a cortina franzida no canto da janela
        yt = CH - 0.006; zA, zB = max(zb - 0.75, BATH_D + TB + 0.05), min(zb + 0.68, Dp - 0.12); xA = lx1 - 2.4
        for (a, b, c, d) in ((xA, lx1 - 0.01, zA, zA + 0.02), (xA, xA + 0.02, zA, zB), (xA, lx1 - 0.01, zB - 0.02, zB)): p.box('alu', a, b, yt - 0.04, yt, c, d)
        xs = np.linspace(lx1 - 0.9, lx1 - 0.15, 9)
        for i in range(8):
            za = zB - 0.06 + (0.04 if i % 2 else -0.04); zc = zB - 0.06 + (-0.04 if i % 2 else 0.04)
            p.seg('curtain', (xs[i], (0.35 + yt - 0.08) / 2, za), (xs[i + 1], (0.35 + yt - 0.08) / 2, zc), 0.012, yt - 0.08 - 0.35)
        q = Piece(); q.merge(guest_chair('vinyl_t'), rot_y(90)); p.merge(q, tr(lx0 + 0.55, 0.0, Dp - 0.75))
        tv(p, rot_y(90, (lx0, 1.95, zb)))
        if Dp > 4.0:
            q = Piece(); q.merge(sofa(1, 'vinyl_t'), rot_y(0)); p.merge(q, tr(lx0 + 1.2, 0.0, yb + 0.02))
    else:
        # consultorio: maca, mesa com computador, cadeiras, armario com pia, biombo e negatoscopio
        zt = Dp - 0.9
        p.cham('steel', lx1 - 1.95, lx1 - 0.15, 0.0, 0.55, zt - 0.28, zt + 0.28, 0.01); p.cham('vinyl_t', lx1 - 1.95, lx1 - 0.15, 0.55, 0.7, zt - 0.32, zt + 0.32, 0.03)
        p.hull('vinyl_t', [(x, y, z) for x in (lx1 - 0.6, lx1 - 0.15) for (y, z) in ((0.7, zt - 0.32), (0.7, zt + 0.32), (0.95, zt - 0.32), (0.95, zt + 0.32))] + [(lx1 - 0.6, 0.7, zt)])
        p.box('paper', lx1 - 1.9, lx1 - 0.2, 0.7, 0.705, zt - 0.25, zt + 0.25)
        p.cham('steel', lx1 - 2.3, lx1 - 1.95, 0.0, 0.2, zt - 0.2, zt + 0.2, 0.01)
        dx0 = lx0 + 0.15; p.cham('laminate', dx0, dx0 + 1.4, 0.72, 0.76, Dp - 0.75, Dp - 0.05, 0.008)
        for x in (dx0 + 0.03, dx0 + 1.37): p.box('steel', x - 0.02, x + 0.02, 0.0, 0.72, Dp - 0.72, Dp - 0.08)
        p.cham('dark', dx0 + 0.45, dx0 + 0.95, 0.8, 1.12, Dp - 0.3, Dp - 0.26, 0.008); p.box('screen', dx0 + 0.47, dx0 + 0.93, 0.82, 1.1, Dp - 0.302, Dp - 0.3); p.box('steel', dx0 + 0.67, dx0 + 0.73, 0.76, 0.82, Dp - 0.28, Dp - 0.24)
        p.cham('dark', dx0 + 0.5, dx0 + 0.9, 0.76, 0.78, Dp - 0.55, Dp - 0.4, 0.004)
        q = office_chair('vinyl_t'); p.merge(q, rot_y(180, (dx0 + 0.7, 0.0, Dp - 1.15)))
        for xx in (dx0 + 0.3, dx0 + 1.1): q = guest_chair('vinyl_t'); p.merge(q, rot_y(0, (xx, 0.0, yb + 0.55)))
        p.box('lamp_glass', lx0 + 0.004, lx0 + 0.03, 1.4, 1.9, yb + 0.3, yb + 1.0); p.box('steel', lx0 + 0.004, lx0 + 0.035, 1.38, 1.4, yb + 0.28, yb + 1.02)
        q = Piece(); headwall(q, np.eye(4), 1.2); p.merge(q, rot_y(-90, (lx1, -0.2, zt)))
    # roupeiro entre o banheiro e a porta; alcool em gel e relogio
    wd = (lx1 - 0.25 - DW - 0.09) - (bxw + TB) - 0.06
    if wd > 0.38: wardrobe(p, rot_y(0, ((lx1 - 0.25 - DW - 0.09 + bxw + TB) / 2, 0.0, 0.0)), min(wd, 0.8))
    dispenser(p, rot_y(-90, (lx1, 0.0, 0.62)))
    q = wall_clock(0.16); p.merge(q, rot_y(180, (0.0, 2.6, Dp)))
    p.box('paint_w', lx1 - 0.015, lx1, 1.1, 1.2, DW + 0.5, DW + 0.58)
    return p
# ============================================================================ posto de enfermagem, saguao e pronto-socorro (coordenadas do pavimento)
def monitor_kb(p, x, y, z, ry=0.0):
    """Monitor de computador com teclado (pivo: centro da base, sobre a mesa; tela olhando para +Z)."""
    q = Piece(); q.box('steel_d', -0.1, 0.1, 0.0, 0.015, -0.1, 0.06); q.box('steel_d', -0.025, 0.025, 0.015, 0.2, -0.07, -0.03)
    q.cham('dark', -0.27, 0.27, 0.12, 0.48, -0.04, 0.0, 0.006); q.box('screen', -0.25, 0.25, 0.14, 0.46, 0.0, 0.002)
    q.cham('dark', -0.22, 0.22, 0.0, 0.02, 0.12, 0.27, 0.004); q.box('steel', -0.2, 0.2, 0.02, 0.024, 0.13, 0.26)
    p.merge(q, rot_y(ry, (x, y, z)))
def beam_seats(p, M, n=3, mat='vinyl_t'):
    """Longarina de cadeiras de espera (pivo: centro de tras, chao; assentos olhando +Z): viga de aco, 2 pes, assentos e encostos
    moldados e bracos entre as cadeiras."""
    q = Piece(); L1 = 0.56 * n; x = L1 / 2
    q.box('steel_d', -x + 0.05, x - 0.05, 0.36, 0.42, 0.2, 0.26)
    for s in (-1, 1):
        xx = s * (x - 0.15); q.box('steel_d', xx - 0.025, xx + 0.025, 0.0, 0.42, 0.2, 0.26); q.box('steel_d', xx - 0.03, xx + 0.03, 0.0, 0.03, -0.0, 0.5)
    for i in range(n):
        a = -x + i * 0.56 + 0.03; b = a + 0.5
        q.cham(mat, a, b, 0.42, 0.47, 0.03, 0.5, 0.02); q.hull(mat, [(xx, y, z) for xx in (a + 0.02, b - 0.02) for (y, z) in ((0.48, 0.02), (0.48, 0.06), (0.88, -0.05), (0.88, -0.01))])
    for i in range(n + 1):
        xx = -x + i * 0.56; q.box('steel', xx - 0.012, xx + 0.012, 0.42, 0.62, 0.15, 0.45); q.cham('dark', xx - 0.025, xx + 0.025, 0.62, 0.65, 0.12, 0.47, 0.008)
    p.merge(q, M)
def low_table(p, x, z, L1=1.0, D1=0.5):
    p.cham('laminate', x - L1 / 2, x + L1 / 2, 0.4, 0.44, z - D1 / 2, z + D1 / 2, 0.008)
    for sx in (-1, 1):
        for sz in (-1, 1): p.box('steel', x + sx * (L1 / 2 - 0.05) - 0.015, x + sx * (L1 / 2 - 0.05) + 0.015, 0.0, 0.4, z + sz * (D1 / 2 - 0.05) - 0.015, z + sz * (D1 / 2 - 0.05) + 0.015)
    p.cham('paper', x - 0.25, x + 0.05, 0.44, 0.452, z - 0.12, z + 0.1, 0.003); p.cham('food_g', x + 0.1, x + 0.32, 0.44, 0.455, z - 0.1, z + 0.12, 0.003)
def wheelchair(p, M):
    """Cadeira de rodas dobravel (pivo: centro, chao; frente +Z): rodas grandes com aro, rodinhas, assento e encosto de lona, pedais."""
    q = Piece()
    for s in (-1, 1):
        x = s * 0.3
        ring = trimesh.creation.annulus(r_min=0.27, r_max=0.3, height=0.03, sections=28); ring.apply_transform(rot_y(90)); ring.apply_translation([x, 0.3, -0.12]); q.add('rubber', ring)
        ring = trimesh.creation.annulus(r_min=0.25, r_max=0.262, height=0.012, sections=28); ring.apply_transform(rot_y(90)); ring.apply_translation([x + s * 0.03, 0.3, -0.12]); q.add('chrome', ring)
        for k in range(8):
            a = k * math.pi / 8; seg_cyl(q, 'chrome', (x, 0.3 + 0.27 * math.sin(a), -0.12 + 0.27 * math.cos(a)), (x, 0.3 - 0.27 * math.sin(a), -0.12 - 0.27 * math.cos(a)), 0.003, 4)
        disc_x(q, 'steel', 0.04, x - 0.02, x + 0.02, 0.3, -0.12, 10)
        disc_x(q, 'rubber', 0.07, s * 0.24 - 0.015, s * 0.24 + 0.015, 0.07, 0.3, 12)
        xi = s * 0.24
        seg_cyl(q, 'chrome', (xi, 0.07, 0.3), (xi, 0.5, 0.25), 0.012, 6); seg_cyl(q, 'chrome', (xi, 0.5, 0.25), (xi, 0.5, -0.2), 0.012, 6)
        seg_cyl(q, 'chrome', (xi, 0.3, -0.12), (xi, 0.95, -0.24), 0.012, 6); seg_cyl(q, 'chrome', (xi, 0.95, -0.24), (xi, 0.95, -0.38), 0.014, 6)
        seg_cyl(q, 'chrome', (xi, 0.5, 0.25), (xi, 0.15, 0.4), 0.01, 6); q.box('dark', xi - 0.07, xi + 0.07, 0.13, 0.15, 0.36, 0.5)
        q.box('dark', xi - 0.02, xi + 0.02, 0.68, 0.71, -0.15, 0.15)
    q.box('fabric2', -0.24, 0.24, 0.48, 0.5, -0.2, 0.24); q.box('fabric2', -0.24, 0.24, 0.55, 0.92, -0.25, -0.23)
    p.merge(q, M)
def cart(p, M, mat='cart_w', h=1.0, top=None, drawers=4, red=False):
    """Carrinho de hospital de gavetas (pivo: centro, chao): corpo, gavetas com puxador, tampo com borda, rodizios e alca."""
    q = Piece(); m = 'paint_r' if red else mat
    q.cham(m, -0.38, 0.38, 0.12, h, -0.26, 0.26, 0.012); q.cham('cart_w', -0.4, 0.4, h, h + 0.04, -0.28, 0.28, 0.01)
    for k in range(drawers):
        y0 = 0.16 + k * (h - 0.2) / drawers; y1 = y0 + (h - 0.2) / drawers - 0.02
        q.box(m, -0.36, 0.36, y0, y1, 0.26, 0.27); q.box('chrome', -0.12, 0.12, y1 - 0.06, y1 - 0.04, 0.27, 0.29)
    for sx in (-1, 1):
        for sz in (-1, 1): q.box('steel_d', sx * 0.32 - 0.02, sx * 0.32 + 0.02, 0.06, 0.12, sz * 0.2 - 0.02, sz * 0.2 + 0.02); q.sphere('rubber', 0.045, sx * 0.32, 0.045, sz * 0.2, 1)
    seg_cyl(q, 'chrome', (-0.3, h - 0.1, -0.32), (0.3, h - 0.1, -0.32), 0.012, 8)
    for x in (-0.3, 0.3): seg_cyl(q, 'chrome', (x, h - 0.1, -0.26), (x, h - 0.1, -0.32), 0.01, 6)
    if red:
        q.cham('dark', -0.2, 0.2, h + 0.04, h + 0.3, -0.12, 0.12, 0.01); q.box('screen_g', -0.15, 0.15, h + 0.1, h + 0.25, 0.12, 0.122)
        q.cyl('food_y', 0.08, h + 0.04, h + 0.2, 0.26, 0.0, 12)
    p.merge(q, M)
def linen_cart(p, M):
    q = Piece()
    for x in (-0.35, 0.35):
        for z in (-0.25, 0.25): seg_cyl(q, 'chrome', (x, 0.1, z), (x, 1.0, z), 0.012, 6); q.sphere('rubber', 0.04, x, 0.04, z, 1)
    for y in (0.1, 1.0): q.box('chrome', -0.36, 0.36, y - 0.01, y + 0.01, -0.26, 0.26)
    q.cham('curtain', -0.33, 0.33, 0.12, 0.98, -0.23, 0.23, 0.04); q.cham('bed_w', -0.3, 0.3, 0.98, 1.08, -0.2, 0.2, 0.03)
    p.merge(q, M)
def med_cabinet(p, M, L1=1.0, h=2.0):
    """Armario de medicamentos alto com portas de vidro, prateleiras e caixas sem texto (pivo: centro de tras, chao; frente +Z)."""
    q = Piece(); x = L1 / 2; rng = np.random.default_rng(int(L1 * 100))
    q.cham('cart_w', -x, x, 0.0, h, 0.0, 0.42, 0.01)
    for y in (0.9, 1.25, 1.6): q.box('cart_w', -x + 0.03, x - 0.03, y, y + 0.02, 0.03, 0.4)
    for y in (0.9, 1.25, 1.6):
        xx = -x + 0.06
        while xx < x - 0.18:
            ww = rng.uniform(0.08, 0.16); hh = rng.uniform(0.1, 0.28); m = ['paper', 'blue_l', 'food_g', 'paint_w', 'flag_o'][int(rng.integers(5))]
            q.box(m, xx, xx + ww, y + 0.02, y + 0.02 + hh, 0.08, 0.32); xx += ww + 0.02
    q.box('frame', -x + 0.02, x - 0.02, 0.88, h - 0.04, 0.42, 0.425)
    q.box('glass', -x + 0.05, -0.01, 0.9, h - 0.07, 0.425, 0.43); q.box('glass', 0.01, x - 0.05, 0.9, h - 0.07, 0.425, 0.43)
    for (a, b) in ((-x + 0.02, -0.004), (0.004, x - 0.02)): q.box('cart_w', a, b, 0.05, 0.84, 0.42, 0.432); q.box('chrome', (a + b) / 2 - 0.05, (a + b) / 2 + 0.05, 0.78, 0.8, 0.432, 0.45)
    p.merge(q, M)
def desk_unit(p, x0, x1, z0, z1, y=0.76, mat='laminate'):
    p.cham(mat, x0, x1, y - 0.04, y, z0, z1, 0.008)
    if x1 - x0 > 1.2: p.cham('cart_w', x1 - 0.45, x1 - 0.03, 0.0, y - 0.04, z0 + 0.03, z1 - 0.03, 0.008)
def nurse_station():
    """Posto de enfermagem (andares): bancadas em L de laminado, 2 computadores, cadeiras, armario de medicamentos, pia, quadro branco
    sem escrita, prontuarios e telefone."""
    p = Piece()
    p.cham('laminate', 2.08, 3.86, 0.72, 0.76, 1.12, 1.75, 0.008); p.cham('laminate', 3.23, 3.86, 0.72, 0.76, 1.75, 3.6, 0.008)
    p.cham('cart_w', 2.1, 2.6, 0.0, 0.72, 1.15, 1.7, 0.01); p.cham('cart_w', 3.26, 3.84, 0.0, 0.72, 3.0, 3.58, 0.01)
    monitor_kb(p, 3.05, 0.76, 1.38, 0.0); monitor_kb(p, 3.5, 0.76, 2.4, -90.0)
    p.cham('dark', 2.5, 2.72, 0.76, 0.82, 1.3, 1.5, 0.01); p.box('dark', 2.53, 2.69, 0.82, 0.86, 1.33, 1.47)
    for k in range(4): p.cham(['blue', 'paint_r', 'food_g', 'paint_y'][k], 3.4 + k * 0.05, 3.44 + k * 0.05, 0.76, 1.02, 3.2, 3.5, 0.004)
    q = office_chair('vinyl_b'); p.merge(q, rot_y(180, (3.0, 0.0, 2.15)))
    q = office_chair('vinyl_b'); p.merge(q, rot_y(90, (2.75, 0.0, 2.95)))
    med_cabinet(p, rot_y(90, (2.06, 0.0, 4.45)), 1.0)
    p.cham('cart_w', 2.06, 2.62, 0.0, 0.86, 1.95, 2.55, 0.01); p.box('steel', 2.12, 2.56, 0.86, 0.9, 2.0, 2.5); p.box('dark', 2.2, 2.48, 0.86, 0.902, 2.07, 2.43)
    seg_cyl(p, 'chrome', (2.08, 0.9, 2.25), (2.08, 1.15, 2.25), 0.014, 8); seg_cyl(p, 'chrome', (2.08, 1.15, 2.25), (2.25, 1.12, 2.25), 0.012, 8)
    p.cham('alu', 2.3, 3.6, 1.15, 2.05, 5.67, 5.7, 0.006); p.box('paint_w', 2.33, 3.57, 1.18, 2.02, 5.664, 5.67); p.box('alu', 2.4, 3.5, 1.14, 1.16, 5.6, 5.67)
    for k, c in enumerate(('flag_r', 'blue', 'food_g')): p.box(c, 2.6 + k * 0.08, 2.65 + k * 0.08, 1.16, 1.18, 5.61, 5.63)
    for k in range(3):
        y = 1.1 + k * 0.32; p.box('steel', 2.07, 2.1, y, y + 0.28, 3.1, 3.9)
        for i in range(5): p.box(['blue_l', 'paper', 'paint_y'][(i + k) % 3], 2.1, 2.36, y + 0.03, y + 0.27, 3.15 + i * 0.15, 3.27 + i * 0.15)
    q = wall_clock(0.15); p.merge(q, rot_y(180, (3.0, 2.5, 5.7)))
    return p
def corridor_props():
    """Objetos do corredor dos andares: carrinhos de medicacao e de emergencia, roupa de cama, cadeira de rodas e alcool em gel."""
    p = Piece()
    cart(p, rot_y(0, (8.9, 0.0, -0.6)), 'cart_w', 1.0); cart(p, rot_y(90, (4.62, 0.0, 16.8)), red=True)
    linen_cart(p, rot_y(0, (-12.6, 0.0, 0.55))); wheelchair(p, rot_y(90, (-8.0, 0.0, 0.55)))
    for (x, z, ry) in ((-4.0, -1.0, 0.0), (0.0, 1.0, 180.0), (4.0, 8.0, 90.0), (6.0, 12.0, -90.0)): dispenser(p, rot_y(ry, (x + (0.0 if ry in (0.0, 180.0) else 0.0), 0.0, z)))
    return p
def lobby():
    """Saguao do terreo: balcao de recepcao com 2 computadores e cadeiras, longarinas de espera com mesas de centro, plantas,
    maquina de bebidas, bebedouro, totem de senha (tela sem texto), cadeiras de rodas, tapete de entrada e lixeiras."""
    p = Piece()
    # balcao alto de recepcao (frente para -x) e mesa baixa por dentro
    p.cham('laminate', 0.6, 0.95, 0.0, 1.05, 1.4, 3.6, 0.01); p.cham('counter', 0.55, 1.05, 1.05, 1.1, 1.38, 3.62, 0.008)
    p.cham('laminate', 0.95, 1.9, 0.0, 0.72, 1.4, 1.75, 0.01); p.cham('laminate', 0.95, 1.9, 0.0, 0.72, 3.25, 3.6, 0.01)
    p.cham('counter', 0.95, 1.65, 0.72, 0.76, 1.4, 3.6, 0.008)
    for z in (1.6, 2.9): p.box('blue', 0.595, 0.6, 0.15, 0.95, z, z + 0.7)
    monitor_kb(p, 1.25, 0.76, 2.0, -90.0); monitor_kb(p, 1.25, 0.76, 3.0, -90.0)
    for z in (2.0, 3.0): q = office_chair('vinyl_b'); p.merge(q, rot_y(-90, (1.75, 0.0, z)))
    # esperas
    for (x0, x1) in ((-13.2, -10.6), (-5.4, -2.6)):
        xc = (x0 + x1) / 2
        beam_seats(p, rot_y(0, (xc, 0.0, 1.85)), 4); beam_seats(p, rot_y(180, (xc, 0.0, 4.75)), 4); low_table(p, xc, 3.3, 1.2, 0.5)
    beam_seats(p, rot_y(90, (-1.6, 0.0, 3.3)), 3)
    for (x, z) in ((-13.3, 5.3), (-0.3, 5.3), (-13.3, -0.5), (-1.0, 1.6)): q = plant(1.5); p.merge(q, tr(x, 0.0, z))
    # maquina de bebidas e bebedouro na parede norte
    p.cham('dark', -11.6, -10.6, 0.0, 1.9, -1.0, -0.25, 0.01); p.box('glass', -11.5, -10.95, 0.5, 1.8, -0.25, -0.24); p.box('dark', -10.9, -10.7, 0.9, 1.3, -0.25, -0.235)
    for k in range(5):
        for i in range(4): p.cyl(['flag_r', 'food_g', 'food_y', 'blue'][(i + k) % 4], 0.03, 0.55 + k * 0.25, 0.75 + k * 0.25, -11.42 + i * 0.12, -0.4, 10)
    p.box('dark', -11.4, -11.0, 0.15, 0.35, -0.25, -0.22)
    p.cham('cart_w', -8.0, -7.6, 0.0, 1.0, -1.0, -0.65, 0.01); p.box('steel', -7.95, -7.65, 1.0, 1.02, -0.95, -0.7); p.cyl('chrome', 0.015, 1.02, 1.08, -7.8, -0.82, 8)
    p.cyl('blue_l', 0.13, 1.02, 1.42, -7.8, -0.82, 16)
    # totem de senha
    p.cham('cart_w', -6.5, -6.1, 0.0, 1.45, 4.95, 5.25, 0.02); p.box('screen', -6.47, -6.13, 1.0, 1.38, 4.945, 4.95); p.box('screen_g', -6.42, -6.18, 1.1, 1.3, 4.943, 4.945)
    # tapete, cadeiras de rodas e lixeiras
    ext_y(p, 'rubber', sbox(-9.3, 4.3, -6.7, 5.7), 0.0, 0.008)
    for x in (-12.1, -11.4): wheelchair(p, rot_y(180, (x, 0.0, 5.25)))
    for (x, z) in ((-10.3, 5.35), (-5.6, 5.35)): q = trash_can(); p.merge(q, tr(x, 0.0, z))
    return p
ER_BAYS = [(7.0, 9.0), (9.0, 11.0), (11.0, 13.0)]
def er():
    """Pronto-socorro do terreo: 6 leitos com trilhos e cortinas, painel de cabeceira com monitor e suporte de soro, balcao central de
    enfermagem, triagem com mesa e balanca, espera com longarinas, carrinho de emergencia, macas, cadeiras de rodas e estantes."""
    p = Piece(); yt = CH - 0.006
    for (side, xw, xf) in ((1, 0.3, 3.0), (-1, 9.7, 7.0)):
        for (za, zb) in ER_BAYS:
            zc = (za + zb) / 2
            hospital_bed(p, rot_y(90 if side > 0 else -90, (xw + side * 0.02, 0.0, zc)), 20.0, True, 'bed_w')
            headwall(p, rot_y(90 if side > 0 else -90, (xw, 0.0, zc)), 0.9)
            iv_pole(p, xw + side * 0.5, zc + 0.65)
        # trilhos (entre os leitos e na frente) e cortinas
        zs = [ER_BAYS[0][0]] + [b for (a, b) in ER_BAYS]
        x0, x1 = sorted((xw + side * 0.01, xf))
        for z in zs:
            p.box('alu', x0, x1, yt - 0.04, yt, z - 0.01, z + 0.01)
            n = 10; xs = np.linspace(x0 + 0.05, x1 - 0.05, n + 1)
            for i in range(n):
                p.seg('curtain', (xs[i], (0.4 + yt - 0.08) / 2, z + (0.04 if i % 2 else -0.04)), (xs[i + 1], (0.4 + yt - 0.08) / 2, z + (-0.04 if i % 2 else 0.04)), 0.012, yt - 0.08 - 0.4)
        p.box('alu', xf - 0.01, xf + 0.01, yt - 0.04, yt, zs[0], zs[-1])
        for (za, zb) in ER_BAYS:
            zz = np.linspace(za + 0.05, za + 0.55, 6)
            for i in range(5):
                p.seg('curtain', (xf + (0.04 if i % 2 else -0.04), (0.4 + yt - 0.08) / 2, zz[i]), (xf + (-0.04 if i % 2 else 0.04), (0.4 + yt - 0.08) / 2, zz[i + 1]), 0.012, yt - 0.08 - 0.4)
    # balcao central
    p.cham('laminate', 4.3, 5.7, 0.0, 1.05, 9.2, 11.6, 0.012); p.cham('counter', 4.25, 5.75, 1.05, 1.09, 9.15, 11.65, 0.008)
    p.box('blue', 4.295, 4.3, 0.15, 0.9, 9.4, 11.4); p.box('blue', 5.7, 5.705, 0.15, 0.9, 9.4, 11.4)
    monitor_kb(p, 5.0, 1.09, 9.9, 180.0); monitor_kb(p, 5.0, 1.09, 10.9, 0.0)
    cart(p, rot_y(0, (5.0, 0.0, 12.7)), red=True)
    # estantes e pia na parede norte
    shelves_p = shelves(1.8); p.merge(shelves_p, rot_y(0, (1.5, 0.0, 5.82)))
    p.cham('cart_w', 7.2, 9.4, 0.0, 0.88, 6.06, 6.66, 0.01); p.box('counter', 7.18, 9.42, 0.88, 0.92, 6.06, 6.7)
    p.box('steel', 7.9, 8.5, 0.86, 0.922, 6.2, 6.6); p.box('dark', 7.95, 8.45, 0.92, 0.923, 6.24, 6.56); seg_cyl(p, 'chrome', (8.2, 0.92, 6.12), (8.2, 1.2, 6.12), 0.014, 8)
    seg_cyl(p, 'chrome', (8.2, 1.2, 6.12), (8.2, 1.16, 6.3), 0.012, 8)
    # triagem (oeste, junto da entrada) e espera (leste)
    desk_unit(p, 0.5, 1.9, 14.6, 15.3); monitor_kb(p, 1.2, 0.76, 14.8, 0.0)
    q = office_chair('vinyl_b'); p.merge(q, rot_y(180, (1.2, 0.0, 14.45)))
    q = guest_chair('vinyl_t'); p.merge(q, rot_y(180, (1.2, 0.0, 15.9)))
    p.cham('steel', 2.5, 2.9, 0.0, 0.06, 14.6, 15.0, 0.01); seg_cyl(p, 'steel', (2.7, 0.06, 14.65), (2.7, 1.2, 14.65), 0.02, 8); p.cham('dark', 2.55, 2.85, 1.2, 1.4, 14.6, 14.7, 0.01)
    iv_pole(p, 2.2, 16.6)
    for z in (15.2, 16.6): beam_seats(p, rot_y(-90, (9.7, 0.0, z)), 2)
    beam_seats(p, rot_y(180, (8.3, 0.0, 17.7)), 2)
    # macas e cadeiras de rodas na entrada
    hospital_bed(p, rot_y(180, (6.4, 0.0, 15.5)), 10.0, True, 'bed_w')
    wheelchair(p, rot_y(90, (3.3, 0.0, 17.15))); wheelchair(p, rot_y(90, (3.3, 0.0, 16.45)))
    q = trash_can(); p.merge(q, tr(6.6, 0.0, 17.3))
    return p
# ============================================================================ cobertura (pivo: topo da laje de cobertura, y = LV[7])
PH = sbox(-2.24, -6.0, 6.24, -1.0); PHH = 3.3                    # casa de maquinas / saida da escada
PH_DOOR = (-0.55, 0.55)
def roof():
    """Cobertura: manta com rufos, platibanda de tijolo com capa de pedra, cornija de 3 degraus, casa de maquinas de tijolo com
    porta, veneziana, escada de marinheiro, faixa de pedra e laje com manta; ralos, respiros e luminaria."""
    p = Piece(); ring = lambda d0, d1: off(FOOT, d1).difference(off(FOOT, d0))
    ext_y(p, 'membrane', off(FOOT, -0.25).difference(PH), 0.0, 0.012)
    ext_y(p, 'brick', ring(-0.25, 0.0).difference(PH), 0.0, PAR)
    ext_y(p, 'membrane', ring(-0.262, -0.25).difference(PH), 0.012, 0.32)
    ext_y(p, 'coping', ring(-0.3, 0.05).difference(sbox(-2.24, -6.1, 6.24, -1.0)), PAR, PAR + 0.08)
    ext_y(p, 'stone', ring(0.0, 0.06), -0.45, -0.3); ext_y(p, 'stone', ring(0.0, 0.14), -0.3, -0.1); ext_y(p, 'stone', ring(0.0, 0.22), -0.1, 0.1)
    # casa de maquinas
    wall2(p, 'x', -2.24, 6.24, -6.0, -5.7, [], 0.0, PHH, 'brick', 'plaster')
    wall2(p, 'x', -2.24, 6.24, -1.0, -1.3, [(PH_DOOR[0], PH_DOOR[1], 0.0, DHB)], 0.0, PHH, 'brick', 'plaster')
    wall2(p, 'z', -5.7, -1.3, -2.24, -1.94, [], 0.0, PHH, 'brick', 'plaster'); wall2(p, 'z', -5.7, -1.3, 6.24, 5.94, [], 0.0, PHH, 'brick', 'plaster')
    wall_grid(p, 'z', -5.7, -1.3, 1.94, 2.06, [], 0.0, PHH, 'plaster')
    q = Piece(); door_casing(q, PH_DOOR[1] - PH_DOOR[0], 0.3, DHB); p.merge(q, tr(0.0, 0.0, -1.15))
    p.box('alu', PH_DOOR[0], PH_DOOR[1], 0.0, 0.012, -1.3, -1.0)
    ext_y(p, 'stone', sbox(-2.28, -6.04, 6.28, -0.96).difference(PH), PHH - 0.3, PHH)
    ext_y(p, 'conc_s', sbox(-2.34, -6.1, 6.34, -0.9), PHH, PHH + 0.22); ext_y(p, 'membrane', sbox(-2.3, -6.06, 6.3, -0.94), PHH + 0.22, PHH + 0.232)
    ext_y(p, 'ceil', sbox(-1.94, -5.7, 1.94, -1.3), PHH - 0.012, PHH); ext_y(p, 'ceil', sbox(2.06, -5.7, 5.94, -1.3), PHH - 0.012, PHH)
    p.cyl('metal', 0.12, PHH - 0.04, PHH - 0.012, 0.0, -2.0, 16); p.cyl('lamp_glass', 0.1, PHH - 0.05, PHH - 0.04, 0.0, -2.0, 16)
    p.box('vinyl', -1.94, 1.94, 0.0, 0.1, -1.312, -1.3)
    # luminaria sobre a porta, veneziana da casa de maquinas e escada de marinheiro
    p.box('metal', -0.1, 0.1, DHB + 0.3, DHB + 0.48, -1.0, -0.95); p.hull('lamp_glass', [(x, y, z) for x in (-0.09, 0.09) for y in (DHB + 0.31, DHB + 0.47) for z in (-0.95, -0.85)])
    p.box('alu', 6.24, 6.29, 0.9, 2.3, -4.6, -2.4)
    for y in np.arange(1.0, 2.25, 0.12): p.hull('alu_d', [(6.24, y, -4.55), (6.24, y, -2.45), (6.3, y + 0.07, -4.55), (6.3, y + 0.07, -2.45), (6.3, y + 0.09, -4.55), (6.3, y + 0.09, -2.45)])
    for z in (-4.0, -3.5): seg_cyl(p, 'galv', (-2.24, 0.15, z), (-2.44, 0.15, z), 0.02, 6); seg_cyl(p, 'galv', (-2.44, 0.1, z), (-2.44, PHH + 0.9, z), 0.022, 8)
    for y in np.arange(0.3, PHH + 0.3, 0.3): seg_cyl(p, 'galv', (-2.44, y, -4.0), (-2.44, y, -3.5), 0.014, 6)
    for y in (PHH + 0.9,): seg_cyl(p, 'galv', (-2.44, y, -4.0), (-2.2, y, -4.0), 0.022, 8); seg_cyl(p, 'galv', (-2.44, y, -3.5), (-2.2, y, -3.5), 0.022, 8)
    # exaustor e respiros no teto da casa de maquinas e na cobertura
    p.cham('galv', 3.0, 4.2, PHH + 0.232, PHH + 0.5, -4.4, -3.2, 0.01); lathe(p, 'galv', [(0.42, PHH + 0.5), (0.45, PHH + 0.62), (0.3, PHH + 0.8), (0.0, PHH + 0.82)], 3.6, -3.8, 0.0, 16)
    for (x, z) in ((-12.0, 4.5), (-12.0, -4.5), (8.0, 4.0), (2.0, 16.5), (8.5, 12.0), (-4.0, 4.6)):
        p.cyl('steel_d', 0.05, 0.012, 0.55, x, z, 10); p.cyl('steel_d', 0.09, 0.012, 0.05, x, z, 10)
    for (x, z) in ((-13.2, 0.0), (9.2, 0.0), (5.0, 17.2), (0.8, 12.0), (-6.0, 5.2)):
        p.cyl('dark', 0.15, 0.012, 0.03, x, z, 16)
        for k in range(6): a = k * math.pi / 6; seg_cyl(p, 'steel_d', (x - 0.14 * math.cos(a), 0.04, z - 0.14 * math.sin(a)), (x + 0.14 * math.cos(a), 0.04, z + 0.14 * math.sin(a)), 0.008, 4)
    return p
def ac_unit():
    """Condensadora de ar-condicionado (pivo: centro, chao): gabinete com aletas, 2 ventiladores com grade no topo, base e tubos."""
    p = Piece(); x, z = 1.1, 0.5
    for s in (-1, 1): p.box('steel_d', -x, x, 0.0, 0.12, s * (z - 0.08) - 0.05, s * (z - 0.08) + 0.05)
    p.cham('galv', -x, x, 0.12, 1.2, -z, z, 0.012)
    for y in np.arange(0.22, 1.12, 0.06):
        for s in (-1, 1): p.box('steel', -x + 0.06, x - 0.06, y, y + 0.02, *sorted((s * z, s * (z + 0.01))))
    for xc in (-0.52, 0.52):
        p.cyl('dark', 0.42, 1.2, 1.205, xc, 0.0, 24)
        ring_y(p, 'steel', 0.42, 0.45, 1.2, 1.24, xc, 0.0, 24)
        for k in range(7): yy = 1.24; seg_cyl(p, 'steel', (xc - 0.43, yy, -0.42 + k * 0.14), (xc + 0.43, yy, -0.42 + k * 0.14), 0.006, 4)
        p.cyl('steel_d', 0.08, 1.205, 1.23, xc, 0.0, 10)
        for k in range(4):
            a = k * math.pi / 2 + 0.4; p.hull('alu_d', [(xc + r * math.cos(a + da), yy + dy, r * math.sin(a + da)) for (r, da, yy) in ((0.06, 0.0, 1.21), (0.36, 0.3, 1.212), (0.36, -0.2, 1.218)) for dy in (0.0, 0.006)])
    for (y, r) in ((0.4, 0.02), (0.55, 0.012)): seg_cyl(p, 'brass', (x - 0.2, y, z), (x - 0.2, y, z + 0.35), r, 8); seg_cyl(p, 'brass', (x - 0.2, y, z + 0.35), (x - 0.2, 0.15, z + 0.35), r, 8)
    p.box('dark', -x + 0.1, -x + 0.4, 0.41, 0.76, z + 0.012, z + 0.03)
    return p
def ahu():
    """Unidade de tratamento de ar no telhado (pivo: centro, chao): caixa com portas de inspecao, tomada de ar com veneziana e duto."""
    p = Piece(); x, z = 2.0, 0.9
    for s in (-1, 1): p.box('steel_d', -x, x, 0.0, 0.2, s * 0.7 - 0.08, s * 0.7 + 0.08)
    p.cham('galv', -x, x, 0.2, 1.8, -z, z, 0.015); p.cham('galv', -x - 0.03, x + 0.03, 1.8, 1.86, -z - 0.03, z + 0.03, 0.01)
    for xx in (-1.4, -0.4, 0.6):
        p.box('galv', xx, xx + 0.8, 0.4, 1.6, z, z + 0.012)
        for yy in (0.6, 1.4): p.box('steel_d', xx + 0.6, xx + 0.66, yy, yy + 0.1, z + 0.012, z + 0.04)
    p.box('alu', -x - 0.012, -x, 0.4, 1.6, -0.7, 0.7)
    for y in np.arange(0.5, 1.55, 0.1): p.hull('alu_d', [(-x - 0.012, y, -0.65), (-x - 0.012, y, 0.65), (-x - 0.07, y + 0.05, -0.65), (-x - 0.07, y + 0.05, 0.65), (-x - 0.07, y + 0.07, -0.65), (-x - 0.07, y + 0.07, 0.65)])
    p.box('galv', x - 0.9, x - 0.2, 1.86, 2.36, -0.4, 0.4); p.box('galv', x - 0.9, x + 0.6, 2.06, 2.56, -0.35, 0.35)
    return p
def helipad():
    """Heliponto elevado (pivo: centro, sobre a cobertura): pilares e vigas de aco, deck circular de concreto, marcacoes pintadas (anel
    amarelo, circulo de toque e uma cruz branca, sem letra), luzes de borda, rede de protecao com bracos e escada de acesso com patamar."""
    p = Piece(); R = 5.2; yt = 1.8
    for k in range(8):
        a = math.radians(22.5 + k * 45); x, z = 3.8 * math.cos(a), 3.8 * math.sin(a)
        p.box('steel', x - 0.12, x + 0.12, 0.04, yt - 0.45, z - 0.12, z + 0.12); p.box('steel_d', x - 0.25, x + 0.25, 0.012, 0.04, z - 0.25, z + 0.25)
        seg_cyl(p, 'steel', (x, 0.5, z), (0.0, yt - 0.5, 0.0), 0.05, 8)
        a2 = math.radians(22.5 + k * 45); seg_cyl(p, 'steel_d', (0.0, yt - 0.35, 0.0), (R * 0.96 * math.cos(a2), yt - 0.35, R * 0.96 * math.sin(a2)), 0.09, 6)
    p.box('steel', -0.15, 0.15, 0.04, yt - 0.45, -0.15, 0.15); p.box('steel_d', -0.25, 0.25, 0.012, 0.04, -0.25, 0.25)
    ring_y(p, 'steel_d', R - 0.35, R - 0.15, yt - 0.45, yt - 0.25, 0, 0, 48)
    ext_y(p, 'hp_g', poly_ngon(0.0, 0.0, R, 48), yt - 0.25, yt)
    ring_y(p, 'pad_y', 4.6, 4.9, yt, yt + 0.004, 0, 0, 48); ring_y(p, 'paint_w', 2.6, 2.85, yt, yt + 0.004, 0, 0, 48)
    ext_y(p, 'paint_w', unary_union([sbox(-1.6, -0.3, 1.6, 0.3), sbox(-0.3, -1.6, 0.3, 1.6)]), yt, yt + 0.004)
    ring_y(p, 'paint_w', R - 0.14, R - 0.06, yt, yt + 0.004, 0, 0, 48)
    for k in range(16):
        a = math.radians(11.25 + k * 22.5)
        if abs(math.degrees(math.atan2(math.sin(a), math.cos(a)))) < 34: continue
        x, z = (R - 0.25) * math.cos(a), (R - 0.25) * math.sin(a); p.cyl('steel_d', 0.07, yt, yt + 0.04, x, z, 10); p.cyl('screen_g', 0.05, yt + 0.04, yt + 0.12, x, z, 10)
    # rede de protecao (fora do setor da escada)
    angs = [a for a in np.arange(-180.0, 180.0, 11.25) if abs(a) > 30.0]
    def at(a, r, y): return (r * math.cos(math.radians(a)), y, r * math.sin(math.radians(a)))
    for a in angs[::2]: seg_cyl(p, 'steel_d', at(a, R - 0.05, yt - 0.1), at(a, R + 1.0, yt - 0.3), 0.025, 6)
    for (a0, a1) in zip(angs[:-1], angs[1:]):
        if a1 - a0 > 12.0: continue
        seg_cyl(p, 'steel_d', at(a0, R + 1.0, yt - 0.3), at(a1, R + 1.0, yt - 0.3), 0.022, 6)
        p.hull('net', [at(a0, R, yt - 0.12), at(a1, R, yt - 0.12), at(a0, R + 1.0, yt - 0.32), at(a1, R + 1.0, yt - 0.32),
                       at(a0, R, yt - 0.135), at(a1, R, yt - 0.135), at(a0, R + 1.0, yt - 0.335), at(a1, R + 1.0, yt - 0.335)])
    # escada de acesso (sobe para -x) com patamar ate o deck
    xb = 8.3; z0, z1 = 1.5, 2.5
    for i in range(1, 9):
        xa = xb - i * 0.28; y = i * 0.2; p.box('galv', xa, xa + 0.3, y - 0.04, y, z0 + 0.05, z1 - 0.05)
        for xx in np.arange(xa + 0.03, xa + 0.28, 0.05): p.box('steel_d', xx, xx + 0.01, y, y + 0.003, z0 + 0.07, z1 - 0.07)
    p.box('galv', xb - 8 * 0.28 - 1.7, xb - 8 * 0.28, yt - 0.2, yt - 0.01, z0, z1)
    for z in (z0 + 0.02, z1 - 0.02):
        p.hull('steel_d', [(x, y, zz) for zz in (z - 0.02, z + 0.02) for (x, y) in ((xb + 0.1, 0.012), (xb + 0.1, 0.25), (xb - 8 * 0.28, yt - 0.01), (xb - 8 * 0.28, yt - 0.25))])
        seg_cyl(p, 'galv', (xb, 1.0, z), (xb - 8 * 0.28, yt + 1.0, z), 0.024, 8); seg_cyl(p, 'galv', (xb, 0.5, z), (xb - 8 * 0.28, yt + 0.5, z), 0.014, 6)
        seg_cyl(p, 'galv', (xb, 0.012, z), (xb, 1.0, z), 0.024, 8); seg_cyl(p, 'galv', (xb - 8 * 0.28, yt - 0.01, z), (xb - 8 * 0.28, yt + 1.0, z), 0.024, 8)
        seg_cyl(p, 'galv', (xb - 8 * 0.28, yt + 1.0, z), (xb - 8 * 0.28 - 0.9, yt + 1.0, z), 0.024, 8)
        seg_cyl(p, 'galv', (xb - 8 * 0.28 - 0.9, yt - 0.01, z), (xb - 8 * 0.28 - 0.9, yt + 1.0, z), 0.024, 8)
    for xx in (xb - 8 * 0.28 - 0.1, xb - 8 * 0.28 - 1.1):
        for z in (z0 + 0.1, z1 - 0.1): p.box('steel', xx - 0.06, xx + 0.06, 0.012, yt - 0.2, z - 0.06, z + 0.06)
    return p
HP_C = (-8.0, 0.0)
def windsock(h=4.5):
    """Biruta (pivo: base, sobre a cobertura): tripe, mastro, aro giratorio, cone listrado laranja e branco e luz de obstaculo."""
    p = Piece()
    for k in range(3):
        a = k * 2 * math.pi / 3; seg_cyl(p, 'galv', (0.6 * math.cos(a), 0.012, 0.6 * math.sin(a)), (0.0, 1.2, 0.0), 0.03, 6); p.box('steel_d', 0.6 * math.cos(a) - 0.1, 0.6 * math.cos(a) + 0.1, 0.012, 0.03, 0.6 * math.sin(a) - 0.1, 0.6 * math.sin(a) + 0.1)
    p.cyl('galv', 0.045, 0.012, h, 0, 0, 10)
    p.cyl('lens_r', 0.07, h, h + 0.12, 0, 0, 12)
    ring = trimesh.creation.annulus(r_min=0.24, r_max=0.27, height=0.025, sections=24); ring.apply_transform(rot_y(90)); ring.apply_translation([0.3, h - 0.35, 0.0]); p.add('galv', ring)
    seg_cyl(p, 'galv', (0.0, h - 0.35, 0.0), (0.3, h - 0.35, 0.0), 0.02, 6)
    n = 5; Ls = 2.4; r0, r1 = 0.25, 0.1; droop = 0.35
    for k in range(n):
        t0, t1 = k / n, (k + 1) / n
        pts = []
        for t in (t0, t1):
            cx = 0.3 + 0.02 + t * Ls; cy = h - 0.35 - droop * t * t; r = r0 + (r1 - r0) * t
            pts += [(cx, cy + r * math.cos(a), r * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)]
        p.hull('flag_o' if k % 2 == 0 else 'paint_w', pts)
    return p
def cross_sign(s=1.4, d=0.22):
    """Placa luminosa de hospital: caixa azul com cruz branca nas 2 faces, moldura de aluminio e 2 suportes (pivo: meio de baixo; faces em +-Z)."""
    p = Piece(); x = s / 2
    p.cham('blue', -x, x, 0.25, 0.25 + s, -d / 2, d / 2, 0.02); p.box('alu', -x - 0.02, x + 0.02, 0.23, 0.27, -d / 2 - 0.01, d / 2 + 0.01); p.box('alu', -x - 0.02, x + 0.02, 0.23 + s, 0.27 + s, -d / 2 - 0.01, d / 2 + 0.01)
    c = unary_union([sbox(-0.3 * s, 0.25 + 0.4 * s, 0.3 * s, 0.25 + 0.6 * s), sbox(-0.1 * s, 0.25 + 0.2 * s, 0.1 * s, 0.25 + 0.8 * s)])
    ext(p, 'paint_w', c, d / 2, d / 2 + 0.006); ext(p, 'paint_w', c, -d / 2 - 0.006, -d / 2)
    for xx in (-x + 0.2, x - 0.2): p.box('steel_d', xx - 0.04, xx + 0.04, 0.0, 0.25, -0.04, 0.04)
    return p

# ============================================================================ marquises (coordenadas do mundo)
def canopy_entr():
    """Marquise de vidro da entrada principal: 2 pilares redondos, vigas de aco, terças, vidro, tirantes ate a fachada e luminarias."""
    p = Piece(); x0, x1, z0, z1, y = -10.6, -5.4, 6.0, 9.6, 3.3
    for x in (-10.2, -5.8):
        p.cyl('steel_d', 0.12, 0.0, y, x, 9.3, 16); p.cyl('steel_d', 0.2, 0.0, 0.08, x, 9.3, 16); p.cham('steel_d', x - 0.14, x + 0.14, y - 0.1, y, 9.16, 9.44, 0.01)
    p.box('steel_d', x0, x1, y, y + 0.2, z1 - 0.12, z1); p.box('steel_d', x0, x1, y, y + 0.2, z0, z0 + 0.12)
    for x in (x0, x1 - 0.1): p.box('steel_d', x, x + 0.1, y, y + 0.2, z0 + 0.12, z1 - 0.12)
    for x in np.linspace(x0 + 0.1, x1 - 0.1, 7)[1:-1]: p.box('steel', x - 0.03, x + 0.03, y + 0.1, y + 0.2, z0 + 0.12, z1 - 0.12)
    p.box('glass', x0 + 0.1, x1 - 0.1, y + 0.2, y + 0.215, z0 + 0.12, z1 - 0.12)
    for x in (x0 + 0.3, x1 - 0.3):
        seg_cyl(p, 'chrome', (x, y + 0.2, z1 - 0.2), (x, y + 2.0, z0), 0.018, 8); p.box('steel_d', x - 0.1, x + 0.1, y + 1.92, y + 2.12, z0, z0 + 0.02)
    for x in (-9.3, -8.0, -6.7): p.cyl('metal', 0.1, y - 0.03, y, x, 7.8, 14); p.cyl('lamp_glass', 0.08, y - 0.035, y - 0.03, x, 7.8, 14)
    return p
def canopy_amb():
    """Marquise de concreto das ambulancias: laje em balanco com 4 pilares, faixa azul com friso branco, placa da cruz, luminarias,
    tubos de queda e protetores amarelos nos pilares."""
    p = Piece(); x0, x1, z0, z1, y0, y1 = -1.2, 11.2, 18.0, 25.5, 3.85, 4.3
    ext_y(p, 'concrete', sbox(x0, z0, x1, z1), y0, y1)
    for (a, b, c, d) in ((x0 - 0.02, x1 + 0.02, z1, z1 + 0.02), (x0 - 0.02, x0, z0, z1), (x1, x1 + 0.02, z0, z1)): p.box('blue', a, b, y0 + 0.05, y1 + 0.12, c, d)
    for (a, b, c, d) in ((x0 - 0.024, x1 + 0.024, z1 + 0.02, z1 + 0.024), (x0 - 0.024, x0 - 0.02, z0, z1 + 0.02), (x1 + 0.02, x1 + 0.024, z0, z1 + 0.02)): p.box('paint_w', a, b, y0 + 0.13, y0 + 0.17, c, d)
    p.box('coping', x0 - 0.02, x1 + 0.02, y1 + 0.12, y1 + 0.16, z0, z1 + 0.02)
    for (x, z) in ((-0.6, 18.6), (10.6, 18.6), (-0.6, 24.9), (10.6, 24.9)):
        p.cyl('concrete', 0.25, 0.0, y0, x, z, 20)
        ring_y(p, 'paint_y', 0.25, 0.27, 0.2, 0.5, x, z, 20); ring_y(p, 'dark', 0.25, 0.27, 0.5, 0.8, x, z, 20); ring_y(p, 'paint_y', 0.25, 0.27, 0.8, 1.1, x, z, 20)
    for x in (-0.6, 10.6): p.cyl('steel_d', 0.05, 0.0, y0, x + (0.3 if x < 0 else -0.3), 25.2, 8)
    for x in (1.5, 5.0, 8.5):
        for z in (20.5, 23.5): p.box('metal', x - 0.5, x + 0.5, y0 - 0.04, y0, z - 0.15, z + 0.15); p.box('lamp_glass', x - 0.46, x + 0.46, y0 - 0.045, y0 - 0.035, z - 0.11, z + 0.11)
    q = cross_sign(1.2, 0.2); p.merge(q, tr(5.0, y1 + 0.16, z1 - 0.3))
    return p

# ============================================================================ ambulancia generica (pivo: meio entre os eixos, chao; frente +Z)
def ambulance():
    """Ambulancia de bau (sem marca): cabine com capo, para-brisa, portas e retrovisores, bau branco com faixas vermelha e azul,
    cruzes brancas sobre azul, janelas, portas traseiras com macanetas, degrau, barras de luz vermelha e azul, rodas duplas atras."""
    p = Piece(); hw = 1.12; zf = 3.0; zc = 1.05; zr = -3.2
    p.hull('ambu_w', [(x, y, z) for x in (-hw + 0.08, hw - 0.08) for (y, z) in ((0.45, zf), (1.1, zf), (1.2, zf - 0.8), (0.45, zc), (2.35, zc), (2.35, zf - 1.35))])
    p.hull('glass', [(x, y, z) for x in (-hw + 0.12, hw - 0.12) for (y, z) in ((1.25, zf - 0.86), (2.25, zf - 1.32), (1.25, zf - 0.88 - 0.02), (2.25, zf - 1.34 - 0.02))])
    p.box('glass', -hw + 0.07, hw - 0.07, 1.35, 2.15, zc + 0.25, zf - 1.45)
    p.cham('ambu_w', -hw, hw, 0.5, 3.05, zr, zc, 0.04)
    p.box('dark', -hw + 0.1, hw - 0.1, 0.25, 0.5, zr + 0.1, zf - 0.3)
    for s in (-1, 1):
        xa, xb_ = sorted((s * hw, s * (hw + 0.005)))
        p.box('ambu_r', xa, xb_, 1.15, 1.42, zr + 0.05, zc - 0.05); p.box('ambu_b', xa, xb_, 1.48, 1.56, zr + 0.05, zc - 0.05)
        p.box('glass', xa, xb_, 2.0, 2.6, -0.6, 0.2)
        p.box('blue', xa, xb_, 1.75, 2.75, zr + 0.4, zr + 1.4)
        c = unary_union([sbox(-0.35, 2.15, 0.35, 2.35), sbox(-0.1, 1.9, 0.1, 2.6)])
        q = Piece(); ext(q, 'paint_w', c, 0.0, 0.004); p.merge(q, rot_y(90 * s, (s * (hw + 0.005), 0.0, zr + 0.9)))
        xa2, xb2 = sorted((s * (hw - 0.08), s * (hw - 0.075)))
        p.box('dark', xa2, xb2, 0.5, 2.3, zc + 0.15, zc + 0.17)
        p.box('ambu_r', *sorted((s * (hw - 0.08), s * (hw - 0.074))), 0.75, 1.0, zc + 0.2, zf - 0.1)
        p.box('chrome', *sorted((s * (hw - 0.08), s * (hw - 0.07))), 1.3, 1.34, zc + 0.6, zc + 0.8)
        seg_cyl(p, 'steel_d', (s * (hw - 0.1), 1.9, zc + 1.0), (s * (hw + 0.2), 1.95, zc + 1.0), 0.015, 6); p.cham('dark', *sorted((s * (hw + 0.12), s * (hw + 0.28))), 1.7, 2.15, zc + 0.96, zc + 1.04, 0.01)
    # traseira: portas, janelas, macanetas, faixas, lanternas e degrau
    for s in (-1, 1):
        xa, xb_ = sorted((s * 0.01, s * (hw - 0.05)))
        p.box('ambu_w', xa, xb_, 0.55, 2.95, zr - 0.02, zr); p.box('glass', *sorted((s * 0.15, s * 0.8)), 1.9, 2.6, zr - 0.025, zr - 0.02)
        p.box('ambu_r', xa, xb_, 1.15, 1.42, zr - 0.025, zr - 0.02); p.box('chrome', *sorted((s * 0.08, s * 0.14)), 1.5, 1.7, zr - 0.05, zr - 0.02)
        p.box('lens_r', *sorted((s * (hw - 0.2), s * (hw - 0.02))), 0.8, 1.05, zr - 0.03, zr - 0.0)
        p.box('lens_r', *sorted((s * (hw - 0.25), s * (hw - 0.02))), 2.88, 3.02, zr - 0.04, zr + 0.0)
    p.box('steel_d', -0.8, 0.8, 0.35, 0.45, zr - 0.35, zr); p.box('dark', -0.8, 0.8, 0.45, 0.47, zr - 0.35, zr - 0.05)
    # frente: grade, farois, para-choque e barra de luzes
    p.box('chrome', -0.75, 0.75, 0.55, 0.9, zf, zf + 0.02);
    for x in np.linspace(-0.68, 0.68, 9): p.box('dark', x - 0.03, x + 0.03, 0.58, 0.87, zf + 0.02, zf + 0.025)
    for s in (-1, 1): p.box('lamp_glass', *sorted((s * 0.8, s * (hw - 0.12))), 0.68, 0.88, zf, zf + 0.02); p.box('flag_o', *sorted((s * 0.8, s * (hw - 0.12))), 0.6, 0.66, zf, zf + 0.02)
    p.cham('steel_d', -hw + 0.05, hw - 0.05, 0.35, 0.52, zf - 0.05, zf + 0.15, 0.02)
    p.box('dark', -0.9, 0.9, 3.05, 3.1, zc - 0.5, zc - 0.05)
    for k, x in enumerate(np.linspace(-0.8, 0.8, 6)): p.cham('lens_r' if k % 2 == 0 else 'lens_b', x - 0.13, x + 0.13, 3.1, 3.22, zc - 0.45, zc - 0.1, 0.02)
    for s in (-1, 1): p.cham('lens_r' if s < 0 else 'lens_b', *sorted((s * (hw - 0.25), s * (hw - 0.02))), 2.88, 3.02, zc - 0.2, zc - 0.02, 0.01)
    # rodas
    for (z, dual) in ((zf - 0.9, False), (zr + 1.0, True)):
        for s in (-1, 1):
            offs = (0.0, 0.25) if dual else (0.0,)
            for o in offs:
                xa = s * (hw - 0.18 - o); disc_x(p, 'rubber', 0.4, xa - 0.11, xa + 0.11, 0.4, z, 20)
            disc_x(p, 'steel', 0.24, *sorted((s * (hw - 0.07), s * (hw - 0.05))), 0.4, z, 16)
            disc_x(p, 'chrome', 0.08, *sorted((s * (hw - 0.05), s * (hw - 0.03))), 0.4, z, 10)
    return p

# ============================================================================ objetos do lote
def lamp_pole(h=6.0):
    """Poste de iluminacao moderno: base de concreto, poste conico de aco, braco e luminaria de LED (pivo: centro, chao; luz para +Z)."""
    p = Piece(); p.cyl('concrete', 0.25, -0.05, 0.4, 0, 0, 16)
    lathe(p, 'steel_d', [(0.1, 0.4), (0.09, 0.5), (0.06, h)], sec=12)
    seg_cyl(p, 'steel_d', (0.0, h - 0.1, 0.0), (0.0, h - 0.05, 0.9), 0.04, 8)
    p.cham('steel_d', -0.18, 0.18, h - 0.12, h - 0.02, 0.8, 1.4, 0.02); p.box('lamp_glass', -0.15, 0.15, h - 0.125, h - 0.115, 0.85, 1.35)
    return p
def bollard():
    p = Piece(); p.cyl('steel_d', 0.1, 0.0, 0.9, 0, 0, 14); lathe(p, 'steel_d', [(0.1, 0.9), (0.07, 0.96), (0.0, 0.98)], sec=14)
    ring_y(p, 'paint_y', 0.1, 0.105, 0.7, 0.8, 0, 0, 14); return p
def monument_sign():
    """Placa monumento da entrada (sem texto): muro baixo de pedra com capa, painel azul com a cruz branca e canteiro (pivo: centro, chao; frente +Z)."""
    p = Piece(); p.cham('stone', -1.6, 1.6, 0.0, 1.1, -0.3, 0.3, 0.02); p.cham('coping', -1.68, 1.68, 1.1, 1.18, -0.36, 0.36, 0.01)
    for s in (1, -1):
        zz = sorted((s * 0.3, s * 0.32)); p.box('blue', -1.3, 1.3, 0.25, 0.95, *zz)
        c = unary_union([sbox(-0.85, 0.52, -0.45, 0.68), sbox(-0.73, 0.4, -0.57, 0.8)])
        q = Piece(); ext(q, 'paint_w', c, 0.0, 0.004); p.merge(q, rot_y(0 if s > 0 else 180, (0, 0, s * 0.32)))
        for k in range(3): p.box('paint_w', -0.3, 1.0 - k * 0.25, 0.68 - k * 0.12, 0.72 - k * 0.12, *sorted((s * 0.32, s * 0.324)))
    ext_y(p, 'mulch', sbox(-2.0, -0.9, 2.0, 0.9).difference(sbox(-1.6, -0.3, 1.6, 0.3)), 0.0, 0.08)
    for x in (-1.5, -0.5, 0.5, 1.5):
        for z in (-0.6, 0.6): p.sphere('leaf2', 0.22, x, 0.18, z, 1)
    return p
# ============================================================================ pecas
ROOM_P = {}
def room_name(k, kind):
    fr, w, dd = room_frame(k); n = f'room_{kind}_{int(round(w * 100))}x{int(round(dd * 100))}'
    if n not in ROOM_P: ROOM_P[n] = room(w, dd, kind)
    return n
for k in ROOMS: room_name(k, 'ward')
for k in ROOMS_G: room_name(k, 'exam')
pieces = {
    'site': site(), 'shell_g': shell('g'), 'shell_t': shell('t'), 'slab_g': slab('g'), 'slab_1': slab('1'), 'slab_t': slab('t'),
    'walls_g': walls('g'), 'walls_t': walls('t'), 'stair': stair(), 'nurse_station': nurse_station(), 'corridor_props': corridor_props(),
    'lobby': lobby(), 'er': er(), 'roof': roof(), 'helipad': helipad(), 'ac_unit': ac_unit(), 'ahu': ahu(), 'windsock': windsock(),
    'cross_sign': cross_sign(), 'canopy_entr': canopy_entr(), 'canopy_amb': canopy_amb(), 'ambulance': ambulance(),
    'door_room': door_room(DW - 0.02, DHB - 0.012), 'door_bath': door_room(0.88, 2.088, 0.04, 'laminate', False), 'door_stair': door_metal(DW - 0.02, DHB - 0.012, 0.045),
    'door_glass': door_glass(0.98, 2.388, 0.05), 'door_glass_1': door_glass(DW - 0.02, 2.388, 0.05), 'door_service': door_metal(DW - 0.02, 2.388, 0.045),
    'door_double': door_double(0.93, DHB - 0.012),
    'lamp_pole': lamp_pole(6.0), 'bollard': bollard(), 'monument_sign': monument_sign(), 'park_bench': park_bench(1.8), 'trash_can': trash_can(),
    'tree': tree(7.0, 2.3, 'leaf', 2), 'tree_b': tree(5.5, 1.8, 'leaf2', 5), 'bush': bush(0.55, 3), 'wheel_stop': wheel_stop(),
    'car_sedan_r': car('car_r', 'sedan'), 'car_wagon_b': car('car_b', 'wagon'), 'car_hatch_y': car('car_y', 'hatch'), 'car_pickup_s': car('car_s', 'pickup'),
    'car_coupe_g': car('car_g', 'coupe'), 'car_sedan_w': car('car_w', 'sedan'),
    'player_scale_ref': player_ref()}
pieces.update(ROOM_P)

# ============================================================================ montagem
G = ['predio']; J = ['rua']
def fl(k): return G + [f'floor{k}']
put('site', 0, 0, 0, 0, J)
for k in range(NL):
    y = LV[k]; t = fl(k); g = k == 0
    put('shell_g' if g else 'shell_t', 0, y, 0, 0, t + ['ext'])
    put('slab_g' if g else ('slab_1' if k == 1 else 'slab_t'), 0, y, 0, 0, t)
    put('walls_g' if g else 'walls_t', 0, y, 0, 0, t)
    put('stair', 0, y, 0, 0, t)
    door_at('door_stair', 'x', STAIR_DOOR[0], STAIR_DOOR[1], -1.0 - TP / 2, y, 'a', -1, t)
    for r in (ROOMS_G if g else list(ROOMS)):
        fr, w, dd = room_frame(r); put_f(fr, room_name(r, 'exam' if g else 'ward'), 0, y, 0, 0, t)
        ax, a, b, c, hg, into = room_door(r); door_at('door_room', ax, a, b, c, y, hg, into, t)
        put_f(fr, 'door_bath', -w / 2 + BATH_W + TB / 2, y, BATH_DOOR[1] - 0.01, 90, t, door=-90)
    if g:
        put('lobby', 0, y, 0, 0, t); put('er', 0, y, 0, 0, t)
        door_at('door_double', 'x', ER_DD[0], ER_DD[0] + 0.94, 5.7 + TP / 2, y, 'a', 1, t); door_at('door_double', 'x', ER_DD[1] - 0.94, ER_DD[1], 5.7 + TP / 2, y, 'b', 1, t)
        door_at('door_glass', 'x', -9.0, -8.0, 6.0 - 0.15, y, 'a', 1, t); door_at('door_glass', 'x', -8.0, -7.0, 6.0 - 0.15, y, 'b', 1, t)
        door_at('door_glass', 'x', 4.0, 5.0, 18.0 - 0.15, y, 'a', 1, t); door_at('door_glass', 'x', 5.0, 6.0, 18.0 - 0.15, y, 'b', 1, t)
        door_at('door_glass_1', 'z', SIDE_DOOR[0], SIDE_DOOR[1], -14.0 + 0.15, y, 'a', -1, t)
        door_at('door_service', 'z', SIDE_DOOR[0], SIDE_DOOR[1], 10.0 - 0.15, y, 'a', 1, t)
    else:
        put('nurse_station', 0, y, 0, 0, t); put('corridor_props', 0, y, 0, 0, t)
# cobertura
y = LV[NL]
put('slab_t', 0, y, 0, 0, fl(NL)); put('roof', 0, y, 0, 0, G + ['roof'])
door_at('door_stair', 'x', PH_DOOR[0], PH_DOOR[1], -1.15, y, 'a', 1, G + ['roof'])
put('helipad', HP_C[0], y + 0.012, HP_C[1], 0, G + ['roof'])
for (x, z) in ((3.2, 9.0), (6.6, 9.0), (6.6, 3.2)): put('ac_unit', x, y + 0.012, z, 0, G + ['roof'])
put('ahu', 4.6, y + 0.012, 14.0, 90, G + ['roof'])
put('windsock', 9.0, y + 0.012, 16.9, 0, G + ['roof'])
put('cross_sign', 5.0, y + PAR + 0.08, 17.85, 0, G + ['roof']); put('cross_sign', 9.85, y + PAR + 0.08, 11.0, 90, G + ['roof'])
# marquises, ambulancias e lote
put('canopy_entr', 0, 0, 0, 0, G); put('canopy_amb', 0, 0, 0, 0, G)
put('ambulance', 3.0, -0.03, 22.4, 0, J); put('ambulance', 7.2, -0.03, 22.7, 0, J)
put('monument_sign', -12.8, 0, 26.4, 0, J)
cars = [('W', 1, 'car_sedan_r'), ('W', 2, 'car_wagon_b'), ('W', 5, 'car_hatch_y'), ('W', 8, 'car_sedan_w'), ('W', 11, 'car_pickup_s'),
        ('E', 0, 'car_coupe_g'), ('E', 3, 'car_sedan_w'), ('E', 4, 'car_hatch_y'), ('E', 7, 'car_sedan_r'), ('E', 9, 'car_wagon_b'), ('E', 12, 'car_pickup_s')]
for side, k, n in cars:
    xb, zc = (STALLS_W if side == 'W' else STALLS_E)[k]
    put(n, xb + (2.7 if side == 'W' else -2.7), -0.03, zc, 90 if side == 'W' else -90, J)
for (xb, zc) in STALLS_W: put('wheel_stop', xb + 0.6, -0.03, zc, 90, J)
for (xb, zc) in STALLS_E: put('wheel_stop', xb - 0.6, -0.03, zc, 90, J)
for (x, z, ry) in ((-33.4, -6.0, 90), (-33.4, 8.0, 90), (-33.4, 22.0, 90), (-16.6, -6.0, -90), (-16.6, 8.0, -90), (-16.6, 22.0, -90),
                   (-2.0, 27.0, 90), (12.0, 27.0, -90), (-16.0, 27.6, 180), (14.0, 2.0, -90), (-16.0, 12.0, 90)):
    put('lamp_pole', x, 0, z, ry, J)
for x in (-9.5, -8.0, -6.5): put('bollard', x, 0, 28.3, 0, J)
for (x, z, ry) in ((-14.4, 9.5, 90), (-14.4, 11.8, 90), (-1.0, 9.6, -90)): put('park_bench', x, 0, z, ry, J)
for (x, z) in ((-14.3, 12.9), (-0.6, 12.6), (12.6, -1.2), (-6.0, 27.9)): put('trash_can', x, 0, z, 0, J)
for (x, z, n) in ((-14.0, 22.0, 'tree'), (-2.5, 22.5, 'tree_b'), (15.0, 23.0, 'tree'), (20.0, 10.0, 'tree_b'), (21.0, -4.0, 'tree'), (-8.0, -11.5, 'tree'),
                  (4.0, -12.0, 'tree_b'), (16.0, -12.0, 'tree'), (24.0, 26.0, 'tree_b'), (-20.0, -14.5, 'tree_b'), (-14.0, 16.5, 'tree_b')):
    put(n, x, 0, z, 0, J + ['roof'])
bushes = [(x, 6.65) for x in (-13.4, -12.2, -11.0, -5.2, -4.0, -2.8, -1.6, -0.6)] + [(-0.65, z) for z in np.arange(8.0, 17.6, 1.6)] + \
         [(x, -6.65) for x in np.arange(-13.0, 9.6, 2.4)] + [(-14.65, z) for z in (-5.2, -3.8, -2.4, 2.4, 3.8, 5.2)]
for (x, z) in bushes: put('bush', x, 0.02, z, 0, J)
put('player_scale_ref', -8.0, LV[0], 3.0, 0, fl(0)); put('player_scale_ref', -4.0, LV[3], 0.0, 0, fl(3)); put('player_scale_ref', 0.0, LV[NL] + 0.012, 1.0, 0, G + ['roof'])

if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'ground': 0.0, 'floor_height': H, 'floor_levels': LV, 'floors': NL,
                       'footprint': [list(c) for c in FOOT.exterior.coords], 'wall_thickness': T, 'partition_thickness': TP,
                       'stair': {'risers': SNR, 'rise': SRR, 'tread': STRD, 'shaft': [-2.0, 2.0, -6.0, -1.0]}, 'helipad': {'center': list(HP_C), 'radius': 5.2},
                       'site': {'x': [SX0, SX1], 'z': [SZ0, SZ1]}, 'textures': 'PBR (albedo + normal + ORM), 2 m tiles, UV in metres / 2'},
              'placements': L}
    json.dump(layout, open(f'{OUT}/building_layout.json', 'w'), indent=1)
    sc2 = trimesh.Scene(); tot = 0
    for e in L:
        T_ = trimesh.transformations.rotation_matrix(math.radians(e['rotY']), [0, 1, 0]); T_[:3, 3] = e['pos']
        sc = pieces[e['piece']].scene(e['piece'])
        for nm, g_ in sc.geometry.items(): g2 = g_.copy(); g2.apply_transform(T_); sc2.add_geometry(g2); tot += len(g2.faces)
    sc2.export(f'{OUT}/building_assembled.glb', include_normals=True); glb_jpeg(f'{OUT}/building_assembled.glb')
    for n, p in sorted(pieces.items(), key=lambda kv: -kv[1].tris())[:12]: print(f'  {n:30s} {p.tris():6d} tri')
    print(len(pieces), 'pecas', len(L), 'posicoes', sum(1 for e in L if 'door' in e), 'portas', tot, 'triangulos no montado')
